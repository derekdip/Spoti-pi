"""ECS-Decision v1 as frozen in docs/ecs-decision-v1-handoff.md, sections 4 to 16, with the thresholds of
docs/math-track-ed1-prereg.md (loaded into TH from poc/results/ed1/config.json by the suite).

Given x (the target's probe distribution), the current family with its fitted theta, the candidate
syntaxes (each a dict with its `geom` family for the first-order block and its `fit` family for the full
fit and the cost) and a fallback, return the action and every diagnostic the handoff asks to preserve. The
ablation flags remove one layer each so the same code scores every arm.
"""
from __future__ import annotations
import jax, jax.numpy as jnp, numpy as np
from .model import deltas_of, init_theta, fit, family_size, jacobian

TH = dict(eps_g=None, D_max=0.05, gamma_rel=1e-8, kappa_max=None, eps_H_rel=1e-8, p_set=(1, 3, 12), beam=3,
          d_max=0.2, mu_min=0.95, contain_min=0.95, multistarts=8, better_frac=0.10, lam_s=None, spent=0.01)


def geometry(G, x, theta):
    """Residual, Jacobian, normalised distortion, stationarity, conditioning on the numerical rank, tangent
    split, Hessian extremes."""
    x = np.asarray(x); r = x - np.asarray(G(theta)); J = jacobian(G, theta, 32); n = len(r)
    U, s, _ = np.linalg.svd(J, full_matrices=False); smax = float(s[0]) if len(s) else 0.0
    keep = s > TH["gamma_rel"] * smax; rank = int(keep.sum()); Uk = U[:, keep]
    r_par = Uk @ (Uk.T @ r); r_perp = r - r_par
    stat = float(np.linalg.norm(J.T @ r) / (smax * np.linalg.norm(r) + 1e-300))
    gamma = float(s[keep].min()) if rank else 0.0; kappa = float(smax / gamma) if gamma > 0 else float("inf")
    F = lambda th: 0.5 * jnp.sum((jnp.asarray(x) - G(th)) ** 2)
    H = jacobian(jax.grad(F), theta, 32); lam = np.linalg.eigvalsh((H + H.T) / 2); lam_min = float(lam[0]); hnorm = float(np.abs(lam).max())
    return dict(r=r, Uk=Uk, rank=rank, n=n, n_theta=int(theta.shape[0]), D=float(np.linalg.norm(r) / np.linalg.norm(x)), stat=stat, gamma=gamma, kappa=kappa,
                smax=smax, tau=float(np.sum(r_par ** 2) / max(np.sum(r ** 2), 1e-300)), r_perp=r_perp, lam_min=lam_min, hnorm=hnorm)


def first_stage(g, abl):
    """Sections 4 to 6: STOP, REFINE, REPARAMETERIZE, GLOBALIZE or LOCALLY EXHAUSTED. Ablation A keeps only
    the adequacy test; B keeps adequacy and stationarity; C drops the conditioning test."""
    if g["D"] <= TH["D_max"]: return "STOP"
    if abl == "A": return "EXHAUSTED"
    if g["stat"] > TH["eps_g"]:
        if abl in ("B", "C"): return "REFINE"
        return "REFINE" if (g["gamma"] > 0 and g["kappa"] <= TH["kappa_max"]) else "REPARAMETERIZE"
    if abl == "B": return "EXHAUSTED"
    if g["lam_min"] < -TH["eps_H_rel"] * g["hnorm"]: return "GLOBALIZE"
    return "EXHAUSTED"


def globalize(G, fam, x, theta, key, steps, lr):
    """Section 7, the frozen budget: multistarts of the same family from random factors; substantially better
    means F falls by better_frac of F(theta)."""
    F0 = float(0.5 * jnp.sum((x - G(theta)) ** 2)); best = (F0, theta)
    for k in jax.random.split(key, TH["multistarts"]):
        th, Fv = fit(G, x, init_theta(fam, k, scale=0.2, b_scale=0.2), steps, lr)
        if Fv < best[0]: best = (Fv, th)
    return dict(F0=F0, F_best=best[0], theta=best[1], improved=bool(best[0] < (1 - TH["better_frac"]) * F0))


def candidate_geometry(G_of, fam, theta, cands, g, abl):
    """Sections 8 to 10: each candidate family's first-order block at its neutral state with the current
    adapter folded in, its novel part (projected off the current tangent; ablation D skips the quotient),
    principal novel subspaces, eta at the matched p and on the full span, and the winning atom."""
    r_perp = g["r"] if abl == "D" else g["r_perp"]; Uk = g["Uk"]; out = {}; extra = deltas_of(fam, theta)
    for name, cfam in cands.items():
        cfam = cfam["geom"] if isinstance(cfam, dict) else cfam
        K = jacobian(G_of(cfam, extra), jnp.zeros(family_size(cfam)), 128)
        Kp = K if abl == "D" else K - Uk @ (Uk.T @ K)
        U, s, _ = np.linalg.svd(Kp, full_matrices=False); U = U[:, s > TH["gamma_rel"] * (s[0] if len(s) else 1.0)]
        atom = U @ (U.T @ r_perp); a = float(np.linalg.norm(atom)); den = max(float(np.sum(r_perp ** 2)), 1e-300)
        out[name] = dict(U=U, dim=int(U.shape[1]), eta_full=a * a / den, eta={p: float(np.sum((U[:, :p].T @ r_perp) ** 2) / den) for p in TH["p_set"]},
                         atom=atom / a if a > 0 else atom, params=int(family_size(cands[name]["fit"] if isinstance(cands[name], dict) else cfam)))
    return out


def pair_geometry(ci, cj):
    """Section 11: coherence and projector distance at each matched p, directed containment on the full
    novel spans, and the winning atoms' alignment."""
    res = {"p": {}}
    for p in TH["p_set"]:
        if p > ci["dim"] or p > cj["dim"]: continue
        sv = np.linalg.svd(ci["U"][:, :p].T @ cj["U"][:, :p], compute_uv=False)        # cosines of the principal angles
        res["p"][p] = dict(mu=float(sv[0]), d=float(np.sqrt(max(0.0, 1 - sv[-1] ** 2))))   # ||P_i - P_j||_2 = sin of the largest angle (equal dims)
    Ui, Uj = ci["U"], cj["U"]
    res["c_ij"] = float(np.linalg.norm(Uj.T @ Ui) ** 2 / max(Ui.shape[1], 1)); res["c_ji"] = float(np.linalg.norm(Ui.T @ Uj) ** 2 / max(Uj.shape[1], 1))
    res["align"] = float(abs(ci["atom"] @ cj["atom"]))
    return res


def equivalent(pg):
    """Section 12, the frozen rule: COLLAPSE when the full novel spans contain each other (section 11's
    directed containment, both ways, at contain_min)."""
    return pg["c_ij"] >= TH["contain_min"] and pg["c_ji"] >= TH["contain_min"]


def equivalent_matched(pg):
    """The editorial's proposal, reported beside it: d <= d_max and mu >= mu_min at every matched p."""
    return bool(pg["p"]) and all(v["d"] <= TH["d_max"] and v["mu"] >= TH["mu_min"] for v in pg["p"].values())


def deployment(D_held, n_params):
    """Section 14 with the surrogate costs the prereg records: distortion plus a per-parameter state cost."""
    return float(D_held + TH["lam_s"] * n_params)


def held_D(Gh, theta, x_held):
    x_held = np.asarray(x_held); return float(np.linalg.norm(x_held - np.asarray(Gh(theta))) / np.linalg.norm(x_held))


def joint_fit(G_of, Gh_of, fam, theta, cfam, x, x_held, key, steps, lr):
    """Section 13's full fit of the augmented model: the current family and the extension fitted together,
    started from the current state and the extension's usual initialisation."""
    joint = list(fam) + list(cfam); th0 = jnp.concatenate([theta, init_theta(cfam, key)])
    th, Fv = fit(G_of(joint), x, th0, steps, lr)
    return th, Fv, held_D(Gh_of(joint), th, x_held)


def decide(G_of, Gh_of, fam, theta, x, x_held, cands, fallback, key, steps, lr, abl=None):
    """Sections 4 to 16 in order. G_of and Gh_of build G on the training and the held-out probes."""
    G = G_of(fam); g = geometry(G, x, theta)
    rec = {k: g[k] for k in ("D", "stat", "tau", "gamma", "kappa", "lam_min", "hnorm", "rank", "n_theta")}
    rec["D_held"] = held_D(Gh_of(fam), theta, x_held); rec["first_stage"] = first_stage(g, abl); rec["fits_run"] = 0
    if rec["first_stage"] in ("STOP", "REFINE", "REPARAMETERIZE"):
        rec["action"] = rec["first_stage"]; return rec
    if abl not in ("A", "B"):                                                    # section 7 before any expansion
        gl = globalize(G, fam, x, theta, key, steps, lr); rec["glob_F0"] = gl["F0"]; rec["glob_F"] = gl["F_best"]; rec["fits_run"] += TH["multistarts"]
        rec["glob_improvement"] = float(1 - gl["F_best"] / max(gl["F0"], 1e-300))
        if gl["improved"]: rec["action"] = "GLOBALIZE"; return rec
    cg = candidate_geometry(G_of, fam, theta, cands, g, abl)
    rec["cands"] = {n: dict(eta=c["eta"], eta_full=c["eta_full"], dim=c["dim"], params=c["params"]) for n, c in cg.items()}
    names = list(cands); pairs = {}; dropped = set()
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]; pg = pair_geometry(cg[a], cg[b]); pg["collapse"] = equivalent(pg); pg["collapse_matched"] = equivalent_matched(pg); pairs[f"{a}|{b}"] = pg
            if abl != "E" and pg["collapse"]:
                dropped.add(b if cg[b]["params"] >= cg[a]["params"] else a)       # section 12: keep the cheaper syntax
    rec["pairs"] = pairs; rec["collapsed"] = sorted(dropped)
    score = (lambda n: cg[n]["eta_full"]) if abl == "A" else (lambda n: cg[n]["eta"][max(TH["p_set"])])
    beam = [n for n in sorted(names, key=lambda n: -score(n)) if n not in dropped][:TH["beam"]]; rec["beam"] = beam
    n_cur = int(theta.shape[0]); J_cur = deployment(rec["D_held"], n_cur); fits = {}
    for n in beam + ["fallback"]:
        cfam = fallback if n == "fallback" else (cands[n]["fit"] if isinstance(cands[n], dict) else cands[n])
        th, Fv, Dh = joint_fit(G_of, Gh_of, fam, theta, cfam, x, x_held, jax.random.fold_in(key, len(fits) + 1), steps, lr); rec["fits_run"] += 1
        fits[n] = dict(D_train=float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(x))), D_held=Dh, J=deployment(Dh, n_cur + family_size(cfam)), params=int(family_size(cfam)))
    rec["fits"] = fits; rec["J_cur"] = J_cur
    best = min(beam, key=lambda n: fits[n]["J"]) if beam else None
    if best is not None and fits[best]["J"] < (1 - TH["spent"]) * J_cur and fits[best]["J"] <= fits["fallback"]["J"]:
        rec["action"] = "EXPAND"; rec["chosen"] = best
    else:
        rec["action"] = "FALLBACK"; rec["chosen"] = "fallback" if fits["fallback"]["J"] < (1 - TH["spent"]) * J_cur else "current"
    return rec
