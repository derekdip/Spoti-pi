"""How many directions are worth fitting: the half rule one singular component at a time, on GPT-2
(docs/prescreen-theory.md, sections 6 and 8).

  /usr/bin/python3 -m poc.ecsdec.rank_check      -> poc/results/ed4/rank_check.json and a table

For each module the training gradient has singular components s_k u_k v_k^T. Component k's real share is
rho_k = u_k^T G_pop v_k / s_k, G_pop estimated on 192 held-out contexts; by the half rule it is worth fitting
to the training optimum when rho_k > 1/2. The isotropic model puts that boundary at s_k = 4 / sqrt(3) noise
units, which is 2 / sqrt(3) = 1.155 times the noise edge, the edge being the top singular value of the
split-half null (G_A - G_B) / 2.

Defect, kept on record: the run of 01:10 UTC 2026-11-11 had THR = 4 / sqrt(3) = 2.309 times the edge (the
threshold in noise units used as if it were in units of the edge), so the P1 and P2 lines of rank_check.log are
at 2.31 x edge, not at the 1.155 x the predictions name. Every component's ratio and rho are in
rank_check.json; `rescore` recomputes the three predictions at 1.155 from those rows, with no new data.

  /usr/bin/python3 -m poc.ecsdec.rank_check rescore   -> the predictions at 1.155 x edge, from rank_check.json

Written before the run (the noise here is known not to be isotropic, effective rank 1.2 to 4.6):
  P1. Components above 1.155 x edge have rho_k > 1/2 in at least 90% of cases.
  P2. The threshold is cautious: more than a quarter of the components below it (k <= 8) have rho_k > 1/2,
      so the count above it understates the number worth fitting.
  P3. Among components above the edge, the shrinker's share eta(s_k) / s_k correlates with the measured
      rho_k at more than 0.5.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, jax, jax.numpy as jnp
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.ecsdec import gpt2 as GM
from poc.ecsdec import prescreen as PS
from poc.ecsdec.rmt_check import shrink

OUT = PS.OUT; log = PS.log; K = 8; THR = 2 / np.sqrt(3)


def main(n_held=192):
    P = GM.load_params(); tok = GM.tokenizer(); lib = PS.LIBRARY; zeros = {m: jnp.zeros(GM.shape_of(m), jnp.float32) for m in lib}
    loss = lambda P, x, y, D: PS._ce(GM.forward(P, x, D), y); grad = jax.jit(lambda P, x, y: jax.grad(lambda D: loss(P, x, y, D))(zeros)); rows = []
    X = lambda a: (jnp.asarray(a[:, :PS.CTX]), jnp.asarray(a[:, 1:PS.CTX + 1]))
    for transform in ("none", "altcaps", "leet"):
        _, ho = PS.corpus(100, n_held, tok, transform); Gh = grad(P, *X(ho)); Gh = {m: np.asarray(Gh[m], np.float64) for m in lib}
        for n in (8, 16, 32, 64, 128):
            t = time.time(); tr, _ = PS.corpus(7, n, tok, transform); G = {k: grad(P, *X(v)) for k, v in dict(tr=tr, A=tr[:n // 2], B=tr[n // 2:]).items()}; sub = []
            for m in lib:
                a, b = GM.shape_of(m); Gt = np.asarray(G["tr"][m], np.float64); E = (np.asarray(G["A"][m], np.float64) - np.asarray(G["B"][m], np.float64)) / 2
                U, S, Vt = np.linalg.svd(Gt, full_matrices=False); edge = float(np.linalg.svd(E, compute_uv=False)[0]); tau = edge / (np.sqrt(a) + np.sqrt(b))
                for k in range(K):
                    sub.append(dict(transform=transform, n=n, module=m, k=k + 1, ratio=float(S[k] / edge), rho=float(U[:, k] @ Gh[m] @ Vt[k] / S[k]), shrunk=float(shrink(S[k], tau, a, b) / S[k])))
            rows += sub; ab = [x for x in sub if x["ratio"] > THR]; be = [x for x in sub if x["ratio"] <= THR]; f = lambda v: f"{sum(x['rho'] > 0.5 for x in v)}/{len(v)}"
            oracle = np.mean([sum(x["rho"] > 0.5 for x in sub if x["module"] == m) for m in lib]); count = np.mean([sum(x["ratio"] > THR for x in sub if x["module"] == m) for m in lib])
            log(f"{transform} n={n:3d}: rho > 1/2 among components above the threshold {f(ab)}, below it {f(be)}; per module, components worth fitting (of {K}) {oracle:.1f}, above the threshold {count:.1f} ({time.time() - t:.0f}s)")
            json.dump(rows, open(OUT / "rank_check.json", "w"), indent=1)
    ab = [x for x in rows if x["ratio"] > THR]; be = [x for x in rows if x["ratio"] <= THR]; ed = [x for x in rows if x["ratio"] > 1]
    log(f"P1: above 1.155 x edge, rho > 1/2 in {sum(x['rho'] > 0.5 for x in ab)}/{len(ab)} = {np.mean([x['rho'] > 0.5 for x in ab]):.3f}")
    log(f"P2: below it, rho > 1/2 in {sum(x['rho'] > 0.5 for x in be)}/{len(be)} = {np.mean([x['rho'] > 0.5 for x in be]):.3f}")
    log(f"P3: above the edge ({len(ed)} components), corr(shrunk share, rho) {np.corrcoef([x['shrunk'] for x in ed], [x['rho'] for x in ed])[0, 1]:+.3f}")
    for lo, hi in ((0, 0.5), (0.5, 0.8), (0.8, 1.0), (1.0, THR), (THR, 1.5), (1.5, 2.0), (2.0, 3.0), (3.0, 1e9)):
        v = [x["rho"] for x in rows if lo < x["ratio"] <= hi]
        if v: log(f"   s_k / edge in ({lo:.2f}, {hi:.2f}]: {len(v):4d} components, rho median {np.median(v):+.3f}, quartiles {np.percentile(v, 25):+.3f} to {np.percentile(v, 75):+.3f}, share above 1/2 {np.mean(np.array(v) > 0.5):.2f}")
    log("rank check done")


def rescore():
    rows = json.load(open(OUT / "rank_check.json")); lib = sorted({x["module"] for x in rows}); half = lambda v: f"{sum(x['rho'] > 0.5 for x in v)}/{len(v)} = {np.mean([x['rho'] > 0.5 for x in v]):.3f}"
    for tr in ("none", "altcaps", "leet"):
        for n in (8, 16, 32, 64, 128):
            sub = [x for x in rows if x["transform"] == tr and x["n"] == n]; per = lambda f: np.mean([sum(f(x) for x in sub if x["module"] == m) for m in lib])
            log(f"{tr} n={n:3d}: per module (of {K}), components worth fitting {per(lambda x: x['rho'] > 0.5):.1f}, above 1.155 x edge {per(lambda x: x['ratio'] > THR):.1f}, above the edge {per(lambda x: x['ratio'] > 1):.1f}")
    ab = [x for x in rows if x["ratio"] > THR]; be = [x for x in rows if x["ratio"] <= THR]; ed = [x for x in rows if x["ratio"] > 1]
    log(f"P1: above 1.155 x edge, rho > 1/2 in {half(ab)}")
    log(f"P2: below it, rho > 1/2 in {half(be)}")
    log(f"P3: above the edge ({len(ed)} components), corr(shrunk share, rho) {np.corrcoef([x['shrunk'] for x in ed], [x['rho'] for x in ed])[0, 1]:+.3f}")
    for lo, hi in ((0, 0.5), (0.5, 0.8), (0.8, 1.0), (1.0, THR), (THR, 1.5), (1.5, 2.0), (2.0, 3.0), (3.0, 1e9)):
        v = [x["rho"] for x in rows if lo < x["ratio"] <= hi]
        if v: log(f"   s_k / edge in ({lo:.2f}, {hi:.2f}]: {len(v):4d} components, rho median {np.median(v):+.3f}, quartiles {np.percentile(v, 25):+.3f} to {np.percentile(v, 75):+.3f}, share above 1/2 {np.mean(np.array(v) > 0.5):.2f}")
    for k in range(1, K + 1):
        v = [x for x in rows if x["k"] == k]; log(f"   component {k}: rho median {np.median([x['rho'] for x in v]):+.3f}, share above 1/2 {np.mean([x['rho'] > 0.5 for x in v]):.2f}, s_k / edge median {np.median([x['ratio'] for x in v]):.2f}")
    log("rank check rescored")


if __name__ == "__main__":
    rescore() if len(sys.argv) > 1 and sys.argv[1] == "rescore" else main()
