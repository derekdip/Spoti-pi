"""ECS-Decision with sketched geometry for models too large for exact Jacobians (ED2,
docs/math-track-ed2-prereg.md). Everything is a function of G: theta -> state vector, evaluated through
forward-mode (JVP), reverse-mode (VJP) and Hessian-vector products only.

  stationarity   s = ||J^T r|| / (sigma_max(J) ||r||), J^T r by one VJP, sigma_max by power iteration
  curvature      lambda_min(H_F) and ||H_F|| by Lanczos on Hessian-vector products
  tangent        a sketch of the current family's tangent space (m_T random directions, orthonormalised)
  candidates     a sketch of each candidate module's dense first-order block at its neutral state (m random
                 direction matrices), projected off the tangent sketch; eta on the sketch, principal
                 directions at matched p, containment between sketched spans, winning atoms
  fit            Adam for a frozen number of steps on F = 0.5 ||x - G(theta)||^2, best iterate kept

A sketch sees an m-dimensional random subspace of a span, so every eta here is a lower bound on the
full-span value, the same m for every candidate; the prereg says so and ranks on it.
"""
from __future__ import annotations
import numpy as np, jax, jax.numpy as jnp

TH = dict(eps_g=None, D_max=None, eps_H_rel=1e-6, p_set=(1, 3, 12), beam=3, contain_min=0.95, d_max=0.2, mu_min=0.95,
          multistarts=2, better_frac=0.10, lam_s=None, spent=0.01, m_T=16, m_c=8, subspace_iters=1, power_iters=6, lanczos=12, cand_rank=2,
          lin_steps=30, lin_lr=3e-3, rank_by="held_gain", objective="D")      # objective: "D" (held-out distortion) or "nll" (held-out cross-entropy)


# ---- adapters on a model with named modules
def family_size(fam, shape_of):
    return sum(r * (shape_of(k)[0] + shape_of(k)[1]) for k, r in fam)


def deltas_of(fam, theta, shape_of):
    out = {}; i = 0
    for k, r in fam:
        a, b = shape_of(k); A = theta[i:i + r * b].reshape(r, b); i += r * b; Bm = theta[i:i + a * r].reshape(a, r); i += a * r
        out[k] = out.get(k, 0) + Bm @ A
    return out


def init_theta(fam, key, shape_of, a_scale=0.02, b_scale=0.0):
    parts = []; ks = jax.random.split(key, 2 * len(fam) + 1)
    for j, (k, r) in enumerate(fam):
        a, b = shape_of(k); parts += [jax.random.normal(ks[2 * j], (r * b,)) * a_scale, jax.random.normal(ks[2 * j + 1], (a * r,)) * b_scale]
    return jnp.concatenate(parts).astype(jnp.float32)


def fit(G, x, theta0, steps, lr, consts):
    """Adam on F for `steps` steps as a jitted scan; returns the best iterate and its F. G(theta, consts):
    the model's constants (its weights) are a runtime argument of every jitted program here, never a
    closure, so XLA does not fold half a gigabyte of weights into each compiled executable."""
    def run_(th0, x, consts):
        F = lambda th: 0.5 * jnp.sum((x - G(th, consts)) ** 2); vg = jax.value_and_grad(F)
        def body(c, i):
            th, m, v, bF, bth = c; L, g = vg(th); m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g ** 2
            better = L < bF; bF = jnp.where(better, L, bF); bth = jnp.where(better, th, bth)
            th = th - lr * (m / (1 - 0.9 ** i)) / (jnp.sqrt(v / (1 - 0.999 ** i)) + 1e-8); return (th, m, v, bF, bth), L
        (th, m, v, bF, bth), _ = jax.lax.scan(body, (th0, 0 * th0, 0 * th0, jnp.inf, th0), jnp.arange(1, steps + 1).astype(jnp.float32))
        Lf = F(th); return jnp.where(Lf <= bF, th, bth), jnp.minimum(Lf, bF)
    th, Lf = jax.jit(run_)(theta0, x, consts); return th, float(Lf)


# ---- geometry by products
def stationarity(G, x, theta, key, consts):
    jv = jax.jit(lambda th, v, c: jax.jvp(lambda t: G(t, c), (th,), (v,))[1]); vj = jax.jit(lambda th, y, c: jax.vjp(lambda t: G(t, c), th)[1](y)[0])
    r = x - G(theta, consts); g = vj(theta, r, consts)
    v = jax.random.normal(key, theta.shape); v = v / jnp.linalg.norm(v); sig2 = 0.0
    for _ in range(TH["power_iters"]):
        u = jv(theta, v, consts); w = vj(theta, u, consts); sig2 = float(jnp.linalg.norm(w)); v = w / (sig2 + 1e-30)
    smax = float(np.sqrt(sig2)); rn = float(jnp.linalg.norm(r))
    return dict(r=np.asarray(r), grad_norm=float(jnp.linalg.norm(g)), smax=smax, rnorm=rn, stat=float(jnp.linalg.norm(g)) / (smax * rn + 1e-30))


def curvature(G, x, theta, key, consts):
    """Lanczos with full reorthogonalisation on H_F v = d/dt grad F(theta + t v)."""
    def hvp_(th, v, x, c):
        gradF = jax.grad(lambda t: 0.5 * jnp.sum((x - G(t, c)) ** 2)); return jax.jvp(gradF, (th,), (v,))[1]
    hvp_j = jax.jit(hvp_); hvp = lambda v: hvp_j(theta, v, x, consts)
    k = TH["lanczos"]; n = theta.shape[0]; Q = np.zeros((k + 1, n), np.float64); alpha = np.zeros(k); beta = np.zeros(k)
    q = np.asarray(jax.random.normal(key, (n,)), np.float64); q /= np.linalg.norm(q); Q[0] = q
    for j in range(k):
        w = np.asarray(hvp(jnp.asarray(Q[j], jnp.float32)), np.float64); alpha[j] = w @ Q[j]
        w = w - alpha[j] * Q[j] - (beta[j - 1] * Q[j - 1] if j > 0 else 0); w = w - Q[:j + 1].T @ (Q[:j + 1] @ w)
        beta[j] = np.linalg.norm(w)
        if beta[j] < 1e-10 or j == k - 1: k = j + 1; break
        Q[j + 1] = w / beta[j]
    Tm = np.diag(alpha[:k]) + np.diag(beta[:k - 1], 1) + np.diag(beta[:k - 1], -1); lam = np.linalg.eigvalsh(Tm)
    return dict(lam_min=float(lam[0]), hnorm=float(np.abs(lam).max()), lanczos_steps=int(k))


def tangent_sketch(G, theta, key, consts):
    """Orthonormal basis of a random m_T-dimensional subspace of the current tangent space."""
    V = jax.random.normal(key, (TH["m_T"], theta.shape[0])); jv = jax.jit(lambda th, v, c: jax.jvp(lambda t: G(t, c), (th,), (v,))[1])
    S = np.stack([np.asarray(jv(theta, v, consts)) for v in V], 1).astype(np.float64); Q, _ = np.linalg.qr(S); return Q


def candidate_sketch(jvp_d, vjp_d, module, shape, key, Q_T, r_perp, quotient=True):
    """jvp_d(module, D) and vjp_d(module, y): the products of the dense delta's first-order block K on the
    module at its neutral state. Returns the candidate's sketched novel block: its orthonormal basis U
    (ordered by singular value), eta at matched p and on the sketch, the winning atom. The sketch is a
    block of m_c random directions pushed through K, then `subspace_iters` rounds of K K^T (a VJP and a
    JVP per direction), so its span approaches the block's top principal directions rather than a random
    slice of its range."""
    a, b = shape; keys = jax.random.split(key, TH["m_c"])
    S = np.stack([np.asarray(jvp_d(module, jax.random.normal(k, (a, b)) / np.sqrt(a * b))) for k in keys], 1).astype(np.float64)
    for _ in range(TH["subspace_iters"]):
        if quotient: S = S - Q_T @ (Q_T.T @ S)
        Q, _ = np.linalg.qr(S); S = np.stack([np.asarray(jvp_d(module, vjp_d(module, jnp.asarray(Q[:, i], jnp.float32)))) for i in range(Q.shape[1])], 1).astype(np.float64)
    if quotient: S = S - Q_T @ (Q_T.T @ S)
    U, s, _ = np.linalg.svd(S, full_matrices=False); keep = s > 1e-6 * s[0]; U = U[:, keep]
    den = max(float(r_perp @ r_perp), 1e-30); atom = U @ (U.T @ r_perp); an = float(np.linalg.norm(atom))
    return dict(U=U, dim=int(U.shape[1]), eta_sketch=an * an / den, eta={p: float(np.sum((U[:, :p].T @ r_perp) ** 2) / den) for p in TH["p_set"]},
                atom=atom / an if an > 0 else atom, sv=s[keep])


def linearised_gain(jvp_tr, vjp_tr, jvp_ho, module, shape, rank, r_perp, r_held, key):
    """The complexity-adjusted proposal score: a rank-`rank` adapter on the module fitted to the training
    residual in the linearised model (lin_steps of Adam, one JVP and one VJP per step, through the dense
    block's products), then the fraction of the held-out residual the same delta removes at first order
    (one held-out JVP). Returns the training and held-out gains and the delta's norm."""
    a, b = shape; k1, k2 = jax.random.split(key); A = jax.random.normal(k1, (rank, b)) * 0.02; Bm = jnp.zeros((a, rank)); r = jnp.asarray(r_perp, jnp.float32)
    mA = 0 * A; vA = 0 * A; mB = 0 * Bm; vB = 0 * Bm; lr = TH["lin_lr"]; den = float(r @ r) + 1e-30; best = (den, A, Bm)
    for i in range(1, TH["lin_steps"] + 1):
        D = Bm @ A; y = jvp_tr(module, D); e = y - r; L = float(e @ e)
        if L < best[0]: best = (L, A, Bm)
        gD = vjp_tr(module, e); gB = gD @ A.T; gA = Bm.T @ gD
        mA = 0.9 * mA + 0.1 * gA; vA = 0.999 * vA + 0.001 * gA ** 2; A = A - lr * (mA / (1 - 0.9 ** i)) / (jnp.sqrt(vA / (1 - 0.999 ** i)) + 1e-8)
        mB = 0.9 * mB + 0.1 * gB; vB = 0.999 * vB + 0.001 * gB ** 2; Bm = Bm - lr * (mB / (1 - 0.9 ** i)) / (jnp.sqrt(vB / (1 - 0.999 ** i)) + 1e-8)
    D = Bm @ A; y = jvp_tr(module, D); e = y - r; L = float(e @ e)
    if L < best[0]: best = (L, A, Bm)
    L, A, Bm = best; D = Bm @ A; rh = jnp.asarray(r_held, jnp.float32); yh = jvp_ho(module, D); eh = yh - rh
    return dict(gain_train=float(1 - L / den), gain_held=float(1 - float(eh @ eh) / (float(rh @ rh) + 1e-30)), delta_norm=float(jnp.linalg.norm(D)))


def rgn_score(vjp_ho, module, W_module, r_held):
    """Auto-RGN (Lee et al. 2023) on a module: the norm of the held-out loss's gradient with respect to the
    module's weights (one VJP of the held-out state against the held-out residual) over the weights' norm."""
    g = vjp_ho(module, -jnp.asarray(r_held, jnp.float32)); return float(jnp.linalg.norm(g) / (jnp.linalg.norm(W_module) + 1e-30))


def pair_geometry(ci, cj):
    res = {"p": {}}
    for p in TH["p_set"]:
        if p > ci["dim"] or p > cj["dim"]: continue
        sv = np.linalg.svd(ci["U"][:, :p].T @ cj["U"][:, :p], compute_uv=False); res["p"][p] = dict(mu=float(sv[0]), d=float(np.sqrt(max(0.0, 1 - sv[-1] ** 2))))
    Ui, Uj = ci["U"], cj["U"]; res["c_ij"] = float(np.linalg.norm(Uj.T @ Ui) ** 2 / Ui.shape[1]); res["c_ji"] = float(np.linalg.norm(Ui.T @ Uj) ** 2 / Uj.shape[1])
    res["align"] = float(abs(ci["atom"] @ cj["atom"])); return res


def equivalent(pg): return pg["c_ij"] >= TH["contain_min"] and pg["c_ji"] >= TH["contain_min"]
def equivalent_matched(pg): return bool(pg["p"]) and all(v["d"] <= TH["d_max"] and v["mu"] >= TH["mu_min"] for v in pg["p"].values())
def deployment(D_held, n): return float(D_held + TH["lam_s"] * n)
def normD(x, y): x = np.asarray(x, np.float64); y = np.asarray(y, np.float64); return float(np.linalg.norm(x - y) / np.linalg.norm(x))


def decide(world, fam, theta, x, x_held, cands, key, steps, lr, log=print, sweep=False):
    """The rule on a world: world.G(fam, extra) builds (theta, P) -> training state, world.Gh the held-out
    state, world.delta_products(extra, library) gives the dense-delta JVP and VJP per module, world.shape_of,
    world.P the weights passed to every jitted program as a runtime argument. `cands` is a list of
    module keys; the fallback of the decision is the base model (no adapter); the all-modules adapter is
    fitted and reported. With sweep=True every candidate
    is fitted in full as well (the comparison the real-data case needs) and recorded under 'sweep'."""
    ks = jax.random.split(key, 8); G = world.G(fam); C = world.P; rec = dict(n_theta=int(theta.shape[0]), fits_run=0)
    st = stationarity(G, x, theta, ks[0], C); r = st["r"]; rec.update(D=normD(x, x - r), stat=st["stat"], smax=st["smax"], grad_norm=st["grad_norm"])
    rec["D_held"] = normD(x_held, world.Gh(fam)(theta, C)); log(f"  D {rec['D']:.4f} D_held {rec['D_held']:.4f} s {rec['stat']:.2e}")
    if rec["D"] <= TH["D_max"]: rec.update(first_stage="STOP", action="STOP"); return rec
    if rec["stat"] > TH["eps_g"]: rec.update(first_stage="REFINE", action="REFINE"); return rec
    cv = curvature(G, x, theta, ks[1], C); rec.update(lam_min=cv["lam_min"], hnorm=cv["hnorm"]); log(f"  lam_min {cv['lam_min']:.2e} |H| {cv['hnorm']:.2e} ({cv['lanczos_steps']} Lanczos steps)")
    rec["first_stage"] = "GLOBALIZE" if cv["lam_min"] < -TH["eps_H_rel"] * cv["hnorm"] else "EXHAUSTED"
    F0 = 0.5 * float(r @ r); best = (F0, theta)
    for k in jax.random.split(ks[2], TH["multistarts"]):
        th, Fv = fit(G, x, init_theta(fam, k, world.shape_of, 0.02, 0.02), steps, lr, C); rec["fits_run"] += 1
        if Fv < best[0]: best = (Fv, th)
    rec["glob_improvement"] = float(1 - best[0] / max(F0, 1e-30)); log(f"  budget: F {F0:.4e} -> {best[0]:.4e} ({100 * rec['glob_improvement']:.1f} percent)")
    if best[0] < (1 - TH["better_frac"]) * F0: rec["action"] = "GLOBALIZE"; return rec
    Q_T = tangent_sketch(G, theta, ks[3], C); r_perp = r.astype(np.float64) - Q_T @ (Q_T.T @ r); rec["tau_sketch"] = float(1 - (r_perp @ r_perp) / max(float(r @ r), 1e-30))
    extra = deltas_of(fam, theta, world.shape_of); cg = {}; jvp_d, vjp_d = world.delta_products(extra, cands); jvp_h, vjp_h = world.delta_products(extra, cands, "ho")
    r_held = np.asarray(x_held) - np.asarray(world.Gh(fam)(theta, C))
    for i, m in enumerate(cands):
        cg[m] = candidate_sketch(jvp_d, vjp_d, m, world.shape_of(m), jax.random.fold_in(ks[4], i), Q_T, r_perp)
        cg[m].update(linearised_gain(jvp_d, vjp_d, jvp_h, m, world.shape_of(m), TH["cand_rank"], r_perp, r_held, jax.random.fold_in(ks[4], 100 + i)))
        cg[m]["rgn"] = rgn_score(vjp_h, m, world.P[m], r_held)
    rec["cands"] = {m: dict(eta=c["eta"], eta_sketch=c["eta_sketch"], dim=c["dim"], gain_train=c["gain_train"], gain_held=c["gain_held"], delta_norm=c["delta_norm"], rgn=c["rgn"]) for m, c in cg.items()}
    log("  eta p12 / linearised gain train / held: " + ", ".join(f"{m} {c['eta'][12]:.3f}/{c['gain_train']:.3f}/{c['gain_held']:.3f}" for m, c in cg.items()))
    pairs = {}; dropped = set()
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            a, b = cands[i], cands[j]; pg = pair_geometry(cg[a], cg[b]); pg["collapse"] = equivalent(pg); pg["collapse_matched"] = equivalent_matched(pg); pairs[f"{a}|{b}"] = pg
            if pg["collapse"]: dropped.add(b if family_size([(b, TH["cand_rank"])], world.shape_of) >= family_size([(a, TH["cand_rank"])], world.shape_of) else a)
    rec["pairs"] = pairs; rec["collapsed"] = sorted(dropped)
    score = (lambda m: cg[m]["gain_held"]) if TH["rank_by"] == "held_gain" else (lambda m: cg[m]["eta"][max(TH["p_set"])])
    beam = [m for m in sorted(cands, key=lambda m: -score(m)) if m not in dropped][:TH["beam"]]; rec["beam"] = beam
    rec["beam_matched_p"] = [m for m in sorted(cands, key=lambda m: -cg[m]["eta"][max(TH["p_set"])]) if m not in dropped][:TH["beam"]]
    rec["beam_rgn"] = [m for m in sorted(cands, key=lambda m: -cg[m]["rgn"]) if m not in dropped][:TH["beam"]]
    log(f"  beam {beam} (matched-p would give {rec['beam_matched_p']}, Auto-RGN {rec['beam_rgn']})")
    n_cur = int(theta.shape[0]); use_nll = TH["objective"] == "nll"
    rec["nll_held_current"] = float(world.nll("ho", fam, theta)) if use_nll else None
    J_cur = deployment(rec["nll_held_current"] if use_nll else rec["D_held"], n_cur); fits = {}
    def joint(name, cfam, k):
        jf = list(fam) + list(cfam); th0 = jnp.concatenate([theta, init_theta(cfam, k, world.shape_of)])
        th, Fv = fit(world.G(jf), x, th0, steps, lr, C); Dh = normD(x_held, world.Gh(jf)(th, C)); rec["fits_run"] += 1
        nh = float(world.nll("ho", jf, th)) if use_nll else None
        fits[name] = dict(D_train=float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(x))), D_held=Dh, nll_held=nh, J=deployment(nh if use_nll else Dh, n_cur + family_size(cfam, world.shape_of)), params=int(family_size(cfam, world.shape_of)))
        log(f"  fit {name}: D_train {fits[name]['D_train']:.4f} D_held {Dh:.4f}" + (f" nll_held {nh:.4f}" if use_nll else "") + f" J {fits[name]['J']:.4f}")
    rk = TH["cand_rank"]
    for i, m in enumerate(beam): joint(m, [(m, rk)], jax.random.fold_in(ks[5], i))
    joint("all_modules", [(m, rk) for m in cands], ks[6])
    nb = float(world.nll("ho", [], jnp.zeros(0))) if use_nll else None
    fits["base"] = dict(D_train=normD(x, world.base_state("tr")), D_held=normD(x_held, world.base_state("ho")), nll_held=nb, J=deployment(nb if use_nll else normD(x_held, world.base_state("ho")), 0), params=0)
    rec["fits"] = fits; rec["J_cur"] = J_cur; J_fb = fits["base"]["J"]                           # the fallback is the base model: no adapter
    best_m = min(beam, key=lambda m: fits[m]["J"]) if beam else None
    if best_m is not None and fits[best_m]["J"] < (1 - TH["spent"]) * J_cur and fits[best_m]["J"] <= J_fb: rec.update(action="EXPAND", chosen=best_m)
    else: rec.update(action="FALLBACK", chosen="base" if J_fb < (1 - TH["spent"]) * J_cur else "current")
    if sweep:
        rec["sweep"] = {}
        for i, m in enumerate(cands):
            if m in fits: rec["sweep"][m] = fits[m]; continue
            joint(m, [(m, rk)], jax.random.fold_in(ks[7], i)); rec["sweep"][m] = fits.pop(m)
        rec["sweep_best"] = min(rec["sweep"], key=lambda m: rec["sweep"][m]["J"])
        # every selector's outcome, read off the sweep: the best J among the modules it would have fitted
        sw = rec["sweep"]; rng = np.random.default_rng(int(jax.random.randint(ks[7], (), 0, 2 ** 31 - 1)))
        rec["selectors"] = {"held_gain": beam, "matched_p": rec["beam_matched_p"], "rgn": rec["beam_rgn"],
                            "random": [str(m) for m in rng.choice(cands, size=min(TH["beam"], len(cands)), replace=False)]}
        rec["selector_J"] = {k: min(sw[m]["J"] for m in v) for k, v in rec["selectors"].items()}; rec["selector_J"]["sweep"] = sw[rec["sweep_best"]]["J"]
        rec["selector_J"]["expected_random"] = float(np.mean([min(sw[m]["J"] for m in rng.choice(cands, size=min(TH["beam"], len(cands)), replace=False)) for _ in range(2000)]))
        # the predictor's accuracy: first-order held-out gain against the fitted held-out gain, per module
        fitted = {m: 1 - sw[m]["D_held"] / rec["D_held"] for m in cands}; pred = {m: cg[m]["gain_held"] for m in cands}
        corr = lambda a, b: (float(np.corrcoef(a, b)[0, 1]), float(np.corrcoef(np.argsort(np.argsort(a)), np.argsort(np.argsort(b)))[0, 1])) if a.std() > 0 and b.std() > 0 else (float("nan"), float("nan"))
        a = np.array([pred[m] for m in cands]); pe, sp = corr(a, np.array([fitted[m] for m in cands]))
        rec["predictor"] = dict(fitted_gain=fitted, pearson=pe, spearman=sp)
        if use_nll:
            fitted_nll = {m: rec["nll_held_current"] - sw[m]["nll_held"] for m in cands}; pe2, sp2 = corr(a, np.array([fitted_nll[m] for m in cands]))
            rec["predictor"].update(fitted_nll_gain=fitted_nll, pearson_nll=pe2, spearman_nll=sp2)
        log(f"  selectors' best J: " + ", ".join(f"{k} {v:.4f}" for k, v in rec["selector_J"].items()) + f"; predictor Pearson {pe:.2f} Spearman {sp:.2f}" + (f" (against NLL gain: {rec['predictor']['pearson_nll']:.2f} / {rec['predictor']['spearman_nll']:.2f})" if use_nll else ""))
    return rec
