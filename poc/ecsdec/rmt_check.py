"""Why the first-order held-out slope works: a signal-plus-noise reading of a module's gradient, checked on
GPT-2 (docs/prescreen-theory.md).

  /usr/bin/python3 -m poc.ecsdec.rmt_check            -> poc/results/ed4/rmt_check.json and a table on stdout

For each module the training gradient is G = g + E: the population gradient plus sampling noise. The noise of the
mean over n contexts has the same law as the half-difference (G_A - G_B) / 2 of two disjoint halves, so that
matrix is an empirical null: its top singular value is the noise edge, its Frobenius norm the noise level.
The adapter direction is the rank-r truncation R of G. Its training slope is sqrt(sum s_k^2); its held-out
slope is <G_ho, R> / ||R||; the theory predicts the held-out slope from the training gradient alone as
sum s_k eta(s_k) / sqrt(sum s_k^2), eta the optimal singular-value shrinker for the noise level.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, jax, jax.numpy as jnp
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.ecsdec import gpt2 as GM
from poc.ecsdec import prescreen as PS

OUT = PS.OUT; log = PS.log


def shrink(s, tau, a, b):
    """The Frobenius-optimal shrinker (Gavish and Donoho) for an a x b matrix with noise entries of standard
    deviation tau: the expected inner product of the true rank-one component with its empirical estimate."""
    big, small = max(a, b), min(a, b); c = small / big; y = s / (tau * np.sqrt(big))
    return float(tau * np.sqrt(big) * np.sqrt(max((y * y - c - 1) ** 2 - 4 * c, 0.0)) / y) if y > 1 + np.sqrt(c) else 0.0


def main(r=2):
    P = GM.load_params(); tok = GM.tokenizer(); lib = PS.LIBRARY; zeros = {m: jnp.zeros(GM.shape_of(m), jnp.float32) for m in lib}
    loss = lambda P, x, y, D: PS._ce(GM.forward(P, x, D), y); grad = jax.jit(lambda P, x, y: jax.grad(lambda D: loss(P, x, y, D))(zeros)); rows = []
    for transform in ("altcaps", "none"):
        for n in (8, 24, 96):
            t = time.time(); tr, ho = PS.corpus(0, n, tok, transform); X = lambda a: (jnp.asarray(a[:, :PS.CTX]), jnp.asarray(a[:, 1:PS.CTX + 1]))
            G = {k: grad(P, *X(v)) for k, v in dict(tr=tr, A=tr[:n // 2], B=tr[n // 2:], ho=ho).items()}
            for m in lib:
                a, b = GM.shape_of(m); Gt = np.asarray(G["tr"][m], np.float64); E = (np.asarray(G["A"][m], np.float64) - np.asarray(G["B"][m], np.float64)) / 2
                U, S, Vt = np.linalg.svd(Gt, full_matrices=False); R = (U[:, :r] * S[:r]) @ Vt[:r]; nR = np.linalg.norm(R); e = np.linalg.svd(E, compute_uv=False)
                tau_F = np.linalg.norm(E) / np.sqrt(a * b); tau_edge = e[0] / (np.sqrt(a) + np.sqrt(b))
                pred = lambda tau: float(sum(S[k] * shrink(S[k], tau, a, b) for k in range(r)) / nR)
                rows.append(dict(transform=transform, n=n, module=m, s1=float(S[0]), s2=float(S[1]), edge=float(e[0]), ratio=float(S[0] / e[0]), train_slope=float(nR),
                                 held_slope=float(np.vdot(np.asarray(G["ho"][m], np.float64), R) / nR), pred_F=pred(tau_F), pred_edge=pred(tau_edge),
                                 noise_rank=float(np.linalg.norm(E) ** 2 / e[0] ** 2), tau_F=float(tau_F), tau_edge=float(tau_edge)))
            sub = [x for x in rows if x["transform"] == transform and x["n"] == n]; h = np.array([x["held_slope"] for x in sub])
            c = lambda k: float(np.corrcoef(h, np.array([x[k] for x in sub]))[0, 1]) if np.std([x[k] for x in sub]) > 0 else float("nan")
            log(f"{transform} n={n}: held/train slope median {np.median([x['held_slope'] / x['train_slope'] for x in sub]):.3f}; s1/edge median {np.median([x['ratio'] for x in sub]):.2f}; "
                f"corr(held, train slope) {c('train_slope'):+.2f}, corr(held, shrink at edge) {c('pred_edge'):+.2f}, corr(held, shrink at Frobenius level) {c('pred_F'):+.2f} ({time.time() - t:.0f}s)")
            for x in sub: log(f"   {x['module']:<8} s1/edge {x['ratio']:5.2f} train {x['train_slope']:.4f} held {x['held_slope']:+.4f} ratio {x['held_slope'] / x['train_slope']:+.3f} pred(edge) {x['pred_edge']:.4f} pred(F) {x['pred_F']:.4f} noise eff. rank {x['noise_rank']:.1f}")
            json.dump(rows, open(OUT / "rmt_check.json", "w"), indent=1)
    log("rmt check done")


def main2(r=2, n_held=192):
    """The fair test: training sets of several sizes against one large held-out set, so the held-out slope is
    a precise estimate of the population slope. Does shrinkage at the empirical edge predict it from the
    training gradient alone, and better than the raw training slope?"""
    P = GM.load_params(); tok = GM.tokenizer(); lib = PS.LIBRARY; zeros = {m: jnp.zeros(GM.shape_of(m), jnp.float32) for m in lib}
    loss = lambda P, x, y, D: PS._ce(GM.forward(P, x, D), y); grad = jax.jit(lambda P, x, y: jax.grad(lambda D: loss(P, x, y, D))(zeros)); rows = []
    X = lambda a: (jnp.asarray(a[:, :PS.CTX]), jnp.asarray(a[:, 1:PS.CTX + 1]))
    for transform in ("none", "altcaps", "leet"):
        _, ho = PS.corpus(100, n_held, tok, transform); Gh = grad(P, *X(ho)); Gh = {m: np.asarray(Gh[m], np.float64) for m in lib}
        for n in (8, 16, 32, 64, 128):
            t = time.time(); tr, _ = PS.corpus(7, n, tok, transform); G = {k: grad(P, *X(v)) for k, v in dict(tr=tr, A=tr[:n // 2], B=tr[n // 2:]).items()}; sub = []
            for m in lib:
                a, b = GM.shape_of(m); Gt = np.asarray(G["tr"][m], np.float64); E = (np.asarray(G["A"][m], np.float64) - np.asarray(G["B"][m], np.float64)) / 2
                U, S, Vt = np.linalg.svd(Gt, full_matrices=False); R = (U[:, :r] * S[:r]) @ Vt[:r]; nR = np.linalg.norm(R); e = np.linalg.svd(E, compute_uv=False); tau = e[0] / (np.sqrt(a) + np.sqrt(b))
                sub.append(dict(transform=transform, n=n, module=m, ratio=float(S[0] / e[0]), train_slope=float(nR), held_slope=float(np.vdot(Gh[m], R) / nR),
                                pred=float(sum(S[k] * shrink(S[k], tau, a, b) for k in range(r)) / nR), bound=float(nR - np.sqrt(np.sum(e[:r] ** 2))), above=int(np.sum(S[:8] > e[0]))))
            rows += sub; h = np.array([x["held_slope"] for x in sub]); tr_ = np.array([x["train_slope"] for x in sub]); pr = np.array([x["pred"] for x in sub]); ok = (pr > 0) & (h > 0)
            err = lambda v: float(np.mean(np.abs(np.log(v[ok] / h[ok])))) if ok.any() else float("nan")
            log(f"{transform} n={n:3d}: s1/edge median {np.median([x['ratio'] for x in sub]):.2f}; held/train {np.median(h / tr_):.3f}; held/pred {np.median(h[ok] / pr[ok]) if ok.any() else float('nan'):.3f}; "
                f"mean |log error| train {err(tr_):.3f} shrink {err(pr):.3f}; corr with held: train {np.corrcoef(h, tr_)[0, 1]:+.2f} shrink {np.corrcoef(h, pr)[0, 1]:+.2f}; "
                f"lower bound holds on {sum(x['bound'] <= x['held_slope'] for x in sub)}/16; singular values above the edge (of 8), median {np.median([x['above'] for x in sub]):.0f} ({time.time() - t:.0f}s)")
            json.dump(rows, open(OUT / "rmt_check2.json", "w"), indent=1)
    log("rmt check 2 done")


if __name__ == "__main__":
    main2() if len(sys.argv) > 1 and sys.argv[1] == "v2" else main()
