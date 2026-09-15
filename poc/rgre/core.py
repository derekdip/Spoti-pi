"""RGRE-1 core: residual diagnosis by projection, localisation and coherence; selection; baselines.

Mechanistic by design (docs/math-track-rgre1-prereg.md): no fitted classifier anywhere.

Residual r (F, N). Two kinds of class diagnostics:
  signed    {class: [tangent fields (F, N)]}  -> orthogonal projection of r onto the class subspace
  templates {class: energy template (N,) >= 0} -> nonnegative least squares of the per-point residual
                                                  energy left after the joint signed fit
Support-type templates (corner, stop) own their support's energy when the residual is concentrated there
(enrichment >= 2); shape-type templates (smooth, interaction) are fitted by nonnegative least squares.
Ownership q_j, coherence mu_j (largest canonical correlation between signed subspaces; cosine between
energy profiles otherwise), score S_j = q_j (1 - mu_j), and the unexplained energy fraction q_perp.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import nnls


def orth(vectors, tol=1e-12):
    M = np.stack([np.asarray(v, float).ravel() for v in vectors], 1)
    norms = np.linalg.norm(M, axis=0)
    keep = norms > tol
    if not keep.any():
        return np.zeros((M.shape[0], 0))
    M = M[:, keep] / norms[keep]
    Q, R = np.linalg.qr(M)
    keep2 = np.abs(np.diag(R)) > 1e-8
    return Q[:, keep2]


def canon(Qa, Qb):
    if Qa.shape[1] == 0 or Qb.shape[1] == 0:
        return 0.0
    s = np.linalg.svd(Qa.T @ Qb, compute_uv=False)
    return float(min(1.0, s.max()))


def cosine(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else 0.0


ENRICH = 2.0
SUPPORT = ("corner", "stop")


def diagnose(r, signed, templates, support=SUPPORT):
    """Return ownership q, raw shares, coherence mu, score S, q_perp, and per-item fractions."""
    F, N = r.shape
    rv = r.ravel().astype(float)
    E = float(rv @ rv)
    if E <= 0:
        return None
    bases = {c: orth(v) for c, v in signed.items() if len(v)}
    bases = {c: Q for c, Q in bases.items() if Q.shape[1] > 0}
    q, raw, items = {}, {}, []
    for c, Q in bases.items():
        p = Q @ (Q.T @ rv)
        q[c] = float(p @ p / E)
        raw[c] = q[c]
    for c, vs in signed.items():
        for k, v in enumerate(vs):
            vv = np.asarray(v, float).ravel()
            n2 = vv @ vv
            items.append((c, f"{c}[{k}]", float((rv @ vv) ** 2 / (n2 * E)) if n2 > 0 else 0.0))
    if bases:
        Qj = orth([Q[:, i] for Q in bases.values() for i in range(Q.shape[1])])
        fit = Qj @ (Qj.T @ rv)
        joint = float(fit @ fit / E)
        rem = rv - fit
    else:
        joint, rem = 0.0, rv
    e = (rem.reshape(F, N) ** 2).sum(0)
    tn = [c for c, T in templates.items() if T is not None and np.asarray(T, float).sum() > 0]
    # support-type templates (corner, stop): the class owns its support's energy when the residual is
    # concentrated there (enrichment >= ENRICH); that energy is then removed before the shape stage
    for c in [c for c in tn if c in support]:
        m = np.asarray(templates[c], float) > 0
        share = float(e[m].sum() / E)
        frac = float(m.mean())
        raw[c] = share
        items.append((c, c, share))
        if frac > 0 and share / frac >= ENRICH:
            q[c] = share
            e = np.where(m, 0.0, e)
        else:
            q[c] = 0.0
    sn = [c for c in tn if c not in support]
    if sn:
        T = np.stack([np.asarray(templates[c], float) / np.asarray(templates[c], float).sum() for c in sn], 1)
        a, _ = nnls(T, e)
        ehat = T @ a
        for c, ac in zip(sn, a):
            q[c] = float(ac / E)
            raw[c] = float(e[np.asarray(templates[c]) > 0].sum() / E)
            items.append((c, c, raw[c]))
        unexpl = float(np.maximum(e - ehat, 0).sum() / E)
    else:
        unexpl = float(e.sum() / E)
    prof = {c: (Q.reshape(F, N, -1) ** 2).sum((0, 2)) for c, Q in bases.items()}
    for c in tn:
        prof[c] = np.asarray(templates[c], float)
    classes = list(q)
    mu = {}
    for c in classes:
        best = 0.0
        for k in classes:
            if k == c:
                continue
            v = canon(bases[c], bases[k]) if (c in bases and k in bases) else cosine(prof[c], prof[k])
            best = max(best, v)
        mu[c] = best
    S = {c: q[c] * (1.0 - mu[c]) for c in classes}
    return {"E": E, "q": q, "raw": raw, "mu": mu, "S": S, "q_perp": unexpl, "q_signed_joint": joint,
            "items": items, "n_signed": {c: int(Q.shape[1]) for c, Q in bases.items()}}


def select(diag, tau_perp, unrepairable=("floor",)):
    """RGRE-1 choice: abstain on unexplained residual or on an unrepairable top class, else the top score."""
    if diag is None:
        return None, "no residual"
    if diag["q_perp"] > tau_perp:
        return None, "unknown"
    order = sorted(diag["S"], key=lambda c: -diag["S"][c])
    if not order:
        return None, "no class"
    if order[0] in unrepairable:
        return None, "atom"
    return order[0], "ok"


def ranked_classes(diag, key):
    return sorted(diag[key], key=lambda c: -diag[key][c])


def baseline_rankings(diag, repairs, costs, class_order):
    """Three frozen baselines, each an ordered list of repair names to evaluate.

    cheapest-first: by cost, ties by the frozen class order and listed order.
    largest generic opportunity: classes by raw share (no coherence, no abstention), repairs of each in order.
    class-free best local projection: individual diagnostics by their own fraction; the class of the top item first.
    """
    by_class = {}
    for name, cls in repairs:
        by_class.setdefault(cls, []).append(name)
    pos = {name: i for i, (name, _) in enumerate(repairs)}
    cheapest = sorted([n for n, _ in repairs], key=lambda n: (costs[n], class_order.index(dict(repairs)[n]) if dict(repairs)[n] in class_order else 99, pos[n]))
    opp = []
    for c in ranked_classes(diag, "raw"):
        opp += by_class.get(c, [])
    opp += [n for n in cheapest if n not in opp]
    items = sorted(diag["items"], key=lambda t: -t[2])
    proj = []
    for c, _, _ in items:
        for n in by_class.get(c, []):
            if n not in proj:
                proj.append(n)
    proj += [n for n in cheapest if n not in proj]
    return {"cheapest_first": cheapest, "largest_opportunity": opp, "best_local_projection": proj}
