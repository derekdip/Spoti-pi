"""Post-hoc W4 attribution (exploratory, unregistered): at A = 8 and 10, is the winning law's error gap due to the delay miss or to the gain-law miss? Output: poc/results/w4_attribution.json."""
import json, sys, numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from w1_experiment import CENTRE, NL
from w4_experiment import K_field, CAL
from water.teacher import WaterParams, run_splash
from reactive.metrics import rel_rmse
r = json.load(open("poc/results/w4.json")); th = r["theta0"]; c = {float(k): v for k, v in r["cells"].items()}
s1 = r["laws"]["s1"]; c_lin = r["laws"]["c_lin_ms_per_unitA"] / 1e3
p = WaterParams(n=256, size=6.0, duration=4.0, record_stride=1, **NL)
xs = np.arange(p.n) * p.dx; X, Y = np.meshgrid(xs, xs, indexing="ij")
times_all = np.arange(int(p.duration * p.fps) + 1) / p.fps; ok = times_all >= 0.15
rad = np.sqrt((X - 3) ** 2 + (Y - 3) ** 2); ev = rad < 2.0
pts = np.stack([X[ev], Y[ev]], -1); t_eval = times_all[ok]
out = {}
for A in (8.0, 10.0):
    tgt = run_splash(p, *CENTRE, v0=A, sigma=0.03).eta.astype(float)[ok][:, ev]
    dt_fit, s_fit = c[A]["dt_hat"], c[A]["s_phase"]
    dt_law, s_law = c_lin * (A - 1), A ** (1 + s1)
    rows = {}
    for lab, dt, s in (("direct dt, direct gain", dt_fit, s_fit), ("law dt, direct gain", dt_law, s_fit), ("direct dt, law gain", dt_fit, s_law), ("law dt, law gain", dt_law, s_law),
                       ("law dt, LS gain given law dt", dt_law, None)):
        K = K_field(th, pts, t_eval, dt)
        if s is None:
            s = float((tgt * K).sum() / (K * K).sum())
        rows[lab] = {"E": rel_rmse(s * K, tgt), "dt_ms": dt * 1e3, "gain": s}
        print(f"A={A:g} {lab:32s} E {rows[lab]['E']:.3f}  dt {dt*1e3:+.1f} ms  gain {s:.2f}")
    out[str(A)] = rows
json.dump(out, open("poc/results/w4_attribution.json", "w"), indent=2)
print("done")
