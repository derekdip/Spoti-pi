"""The real share without a noise model: cross-fitting, checked on GPT-2 (docs/prescreen-theory.md, section 9).

  /usr/bin/python3 -m poc.ecsdec.crossfit_check      -> poc/results/ed4/crossfit_check.json and a table

Split the n training contexts into halves A and B. Directions taken from A are independent of B, so
<G_B, R_A> / ||R_A||^2 is an unbiased estimate of the real share of a rank-r direction fitted on n / 2
contexts; average it with the same from B to A. Per component, the same with u_k v_k^T from one half and the
other half's gradient. The share rises with n, so this estimates a lower sample size than the one in hand.
To first order in the noise the optimism <E, R> / ||R|| is quadratic in E, hence proportional to 1 / n, so
1 - rho(n) is about half of 1 - rho(n / 2): the corrected estimate is (1 + rho_cf) / 2.

Targets, as in rank_check: the full-sample direction's share against 192 held-out contexts.

Written before the run:
  C1. Uncorrected, the cross-fitted rank-2 share reads low: its median over the 16 modules is below the
      measured share's median in at least 12 of the 15 (condition, n) rows.
  C2. Corrected, train slope x (1 + rho_cf) / 2 predicts the held-out slope with a mean absolute log error
      below the raw training slope's over the 15 rows (0.247 in section 4). Whether it also beats the shrunk
      slope (0.105) is not predicted; both are reported.
  C3. As a rank estimate, the number of the first eight components with an uncorrected cross-fitted share
      above 1/2 is closer to the number worth fitting (rho_k > 1/2) than the number above 1.155 x edge is:
      smaller mean absolute error per module in at least 12 of the 15 rows.
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


def main(r=2, n_held=192):
    P = GM.load_params(); tok = GM.tokenizer(); lib = PS.LIBRARY; zeros = {m: jnp.zeros(GM.shape_of(m), jnp.float32) for m in lib}
    loss = lambda P, x, y, D: PS._ce(GM.forward(P, x, D), y); grad = jax.jit(lambda P, x, y: jax.grad(lambda D: loss(P, x, y, D))(zeros)); rows = []; summary = []
    X = lambda a: (jnp.asarray(a[:, :PS.CTX]), jnp.asarray(a[:, 1:PS.CTX + 1])); svd = lambda M: np.linalg.svd(M, full_matrices=False)
    for transform in ("none", "altcaps", "leet"):
        _, ho = PS.corpus(100, n_held, tok, transform); Gh = grad(P, *X(ho)); Gh = {m: np.asarray(Gh[m], np.float64) for m in lib}
        for n in (8, 16, 32, 64, 128):
            t = time.time(); tr, _ = PS.corpus(7, n, tok, transform); G = {k: grad(P, *X(v)) for k, v in dict(tr=tr, A=tr[:n // 2], B=tr[n // 2:]).items()}; sub = []
            for m in lib:
                a, b = GM.shape_of(m); Gt, GA, GB = (np.asarray(G[k][m], np.float64) for k in ("tr", "A", "B")); edge = float(np.linalg.svd((GA - GB) / 2, compute_uv=False)[0]); tau = edge / (np.sqrt(a) + np.sqrt(b))
                U, S, Vt = svd(Gt); R = (U[:, :r] * S[:r]) @ Vt[:r]; nR = np.linalg.norm(R); held = float(np.vdot(Gh[m], R) / nR)
                rho_k = [float(U[:, k] @ Gh[m] @ Vt[k] / S[k]) for k in range(K)]; cf_k = np.zeros(K); cf = 0.0
                for Gfit, Gval in ((GA, GB), (GB, GA)):
                    u, s, vt = svd(Gfit); Rh = (u[:, :r] * s[:r]) @ vt[:r]; cf += 0.5 * float(np.vdot(Gval, Rh) / np.sum(Rh * Rh))
                    cf_k += 0.5 * np.array([u[:, k] @ Gval @ vt[k] / s[k] for k in range(K)])
                sub.append(dict(transform=transform, n=n, module=m, train_slope=float(nR), held_slope=held, rho=held / float(nR), rho_cf=cf, shrunk=float(sum(S[k] * shrink(S[k], tau, a, b) for k in range(r)) / nR),
                                rho_k=rho_k, cf_k=[float(v) for v in cf_k], ratio_k=[float(S[k] / edge) for k in range(K)]))
            rows += sub; h = np.array([x["held_slope"] for x in sub]); s_ = np.array([x["train_slope"] for x in sub]); cfv = np.array([x["rho_cf"] for x in sub])
            pred = dict(raw=s_, shrunk=np.array([x["shrunk"] for x in sub]), cf=s_ * cfv, cf_corrected=s_ * (1 + cfv) / 2)
            err = {k: (float(np.mean(np.abs(np.log(v[(v > 0) & (h > 0)] / h[(v > 0) & (h > 0)])))) if ((v > 0) & (h > 0)).any() else float("nan")) for k, v in pred.items()}
            worth = np.array([sum(v > 0.5 for v in x["rho_k"]) for x in sub]); r_cf = np.array([sum(v > 0.5 for v in x["cf_k"]) for x in sub]); r_edge = np.array([sum(v > THR for v in x["ratio_k"]) for x in sub])
            row = dict(transform=transform, n=n, rho_med=float(np.median(h / s_)), cf_med=float(np.median(cfv)), cf_corr_med=float(np.median((1 + cfv) / 2)), err=err, worth=float(worth.mean()), r_cf=float(r_cf.mean()), r_edge=float(r_edge.mean()),
                       mae_cf=float(np.abs(r_cf - worth).mean()), mae_edge=float(np.abs(r_edge - worth).mean())); summary.append(row)
            log(f"{transform} n={n:3d}: share measured {row['rho_med']:.3f}, cross-fitted {row['cf_med']:.3f}, corrected {row['cf_corr_med']:.3f}; |log error| raw {err['raw']:.3f} shrunk {err['shrunk']:.3f} cross-fit {err['cf']:.3f} corrected {err['cf_corrected']:.3f}; "
                f"rank per module: worth fitting {row['worth']:.1f}, cross-fit {row['r_cf']:.1f} (abs. error {row['mae_cf']:.2f}), above 1.155 x edge {row['r_edge']:.1f} (abs. error {row['mae_edge']:.2f}) ({time.time() - t:.0f}s)")
            json.dump(dict(rows=rows, summary=summary), open(OUT / "crossfit_check.json", "w"), indent=1)
    m_ = lambda k: float(np.nanmean([x["err"][k] for x in summary]))
    log(f"C1: cross-fitted median below the measured median in {sum(x['cf_med'] < x['rho_med'] for x in summary)}/15 rows")
    log(f"C2: mean |log error| over the 15 rows: raw {m_('raw'):.3f}, shrunk {m_('shrunk'):.3f}, cross-fit {m_('cf'):.3f}, corrected cross-fit {m_('cf_corrected'):.3f}")
    log(f"C3: rank error smaller for cross-fit than for the edge count in {sum(x['mae_cf'] < x['mae_edge'] for x in summary)}/15 rows; mean abs. error cross-fit {np.mean([x['mae_cf'] for x in summary]):.2f}, edge count {np.mean([x['mae_edge'] for x in summary]):.2f}; "
        f"cross-fit rank at or below the number worth fitting on average in {sum(x['r_cf'] <= x['worth'] for x in summary)}/15 rows")
    log("crossfit check done")


if __name__ == "__main__":
    main()
