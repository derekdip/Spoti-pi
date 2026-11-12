"""Post-hoc W3 check (exploratory, unregistered): does an actual onset delay dt0 of the token beat, or add to, the g_eff slope? Fits gain+dt0, gain+g_eff, gain+g_eff+dt0 directly at A = 4 and 8 on W1's fit subset; scores on the evaluation set. Output: poc/results/w3_shift_check.json."""
import json, sys, numpy as np
from pathlib import Path
from scipy.optimize import minimize
sys.path.insert(0, str(Path(__file__).resolve().parent))
from w1_experiment import CENTRE, NL
from w3_experiment import token_field
from water.teacher import WaterParams, run_splash
from reactive.metrics import rel_rmse
w3 = json.load(open("poc/results/w3.json")); th = w3["theta0"]
p = WaterParams(n=256, size=6.0, duration=4.0, record_stride=1, **NL)
xs = np.arange(p.n) * p.dx; X, Y = np.meshgrid(xs, xs, indexing="ij")
times_all = np.arange(int(p.duration * p.fps) + 1) / p.fps; ok = times_all >= 0.15
r = np.sqrt((X - 3) ** 2 + (Y - 3) ** 2)
sub = (r < 1.6) & (np.arange(p.n)[:, None] % 3 == 0) & (np.arange(p.n)[None, :] % 3 == 0); ev = r < 2.0
fit_pts, eval_pts = np.stack([X[sub], Y[sub]], -1), np.stack([X[ev], Y[ev]], -1)
fit_frames = np.flatnonzero(ok)[::2]; t_fit, t_eval = times_all[fit_frames], times_all[ok]
out = {}
for A in (4.0, 8.0):
    eta = run_splash(p, *CENTRE, v0=A, sigma=0.03).eta.astype(float)
    ref, tgt = eta[fit_frames][:, sub], eta[ok][:, ev]
    la = np.log(A)
    def model(z, keys, pts, times):
        # z = [s1, dt0, slopes for keys...]; slopes are per-unit-log-A so that the numbers compare with W3's table
        slopes = {k: z[2 + i] for i, k in enumerate(keys)}
        return token_field(th, slopes, z[0], A, pts, times - z[1], [CENTRE])
    for label, keys in (("gain+dt0", []), ("gain+g_eff", ["g_eff"]), ("gain+g_eff+dt0", ["g_eff"])):
        free_dt = "dt0" in label
        def loss(z):
            zz = np.array([z[0], z[1] if free_dt else 0.0] + list(z[2:]))
            return rel_rmse(model(zz, keys, fit_pts, t_fit), ref)
        z0 = np.zeros(2 + len(keys))
        res = minimize(loss, z0, method="Powell", options={"maxfev": 800, "xtol": 1e-3, "ftol": 1e-5})
        zz = np.array([res.x[0], res.x[1] if free_dt else 0.0] + list(res.x[2:]))
        e = rel_rmse(model(zz, keys, eval_pts, t_eval), tgt)
        out[f"{label}_A{A:g}"] = {"fit": float(res.fun), "eval": float(e), "gain_s1": float(zz[0]), "dt0_s": float(zz[1]), "slopes": {k: float(zz[2 + i]) for i, k in enumerate(keys)}}
        print(f"A={A:g} {label:15s} fit {res.fun:.3f} eval {e:.3f} gain {zz[0]:+.3f} dt0 {zz[1]*1000:+.1f} ms slopes {out[f'{label}_A{A:g}']['slopes']}")
json.dump(out, open("poc/results/w3_shift_check.json", "w"), indent=2)
