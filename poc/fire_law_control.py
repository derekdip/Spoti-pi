"""The decisive controlled comparison: old law vs new law, both fitted on the bedless pilot.

On a scene with a fuel bed the coarse-glow centroid moves when the bed lights, so a sway measured
there is not necessarily the plume's. `gusty` has no bed, no shelf and no shutoff, so nothing but
the plume can move. Both laws are fitted by identical code with identical settings.
"""
import sys, json, subprocess, importlib.util
sys.path.insert(0, "/home/user/Spoti-pi")
import numpy as np
from scipy.optimize import differential_evolution, minimize
from poc.fire import scenes, rgre_puffs as RP, teacher as TT
from poc.f5_experiment import sway
SC = "/tmp/claude-0/-home-user-Spoti-pi/1b1f644f-a664-570f-99b3-f54d941ef46d/scratchpad"
src = subprocess.run(["git", "show", "22bd9f7:poc/fire/puffs.py"], cwd="/home/user/Spoti-pi",
                     capture_output=True, text=True).stdout
open(f"{SC}/puffs_f4.py", "w").write(src.replace("from .teacher import", "from poc.fire.teacher import"))
spec = importlib.util.spec_from_file_location("puffs_f4", f"{SC}/puffs_f4.py")
old = importlib.util.module_from_spec(spec); sys.modules["puffs_f4"] = old; spec.loader.exec_module(old)

case = RP.PuffCase("gusty", scenes.gusty())
t_sway = sway(case, None)
print(f"teacher sway {100*t_sway[0]:.1f} cm", flush=True)
names = [n for n in RP.active_params(case) if n in old.PuffState.__dataclass_fields__]
lo = np.array([RP.RANGES[n][0] for n in names]); hi = np.array([RP.RANGES[n][1] for n in names])

def measure(st):
    rec = old.as_record(st, case.p, case.times, case.burners, case.patches, case.obstacles)
    g = np.asarray(TT.g_visual(rec), float).reshape(case.F, -1)
    nx = case.p.nx // 4
    G = g.reshape(case.F, -1, nx); xs = (np.arange(nx) + 0.5) * 4 * case.p.dx
    m = G.sum((1, 2)); xc = (G.sum(1) * xs[None]).sum(1) / np.maximum(m, 1e-9)
    w = 2 * np.pi * case.p.gust_hz; t = case.times; late = t >= 1.0
    M = np.stack([np.ones(int(late.sum())), np.sin(w * t[late]), np.cos(w * t[late])], 1)
    c, *_ = np.linalg.lstsq(M, xc[late], rcond=None)
    A = float(np.hypot(c[1], c[2])); ph = float(np.arctan2(-c[2], c[1]))
    return A, float(np.degrees(np.abs(np.angle(np.exp(1j * (ph - t_sway[1]))))))

def err(x):
    st = old.PuffState(**{n: float(np.clip(v, *RP.RANGES[n])) for n, v in zip(names, x)})
    rec = old.as_record(st, case.p, case.times, case.burners, case.patches, case.obstacles)
    tot = 0.0
    for c in case.names:
        v = (TT.g_visual(rec) if c == "visual" else TT.g_heat(rec, case.probes) if c == "heat" else TT.g_ai(rec))
        v = np.asarray(v, float).reshape(case.F, -1)
        n = case.target[c].shape[1]
        r = (case.target[c] - v) / (case.scale[c] * np.sqrt(n))
        tot += float((r ** 2).sum())
    e = float(np.sqrt(tot / (case.F * len(case.names))))
    live = int(np.ceil(min(st.burn + 3.0 * max(st.cool, 1e-3), 4.0) * st.rate))
    return e * (1.0 + 0.02 * max(live - 16, 0))

r = differential_evolution(err, list(zip(lo, hi)), maxiter=22, popsize=12, seed=0, tol=1e-6,
                           polish=False, init="latinhypercube")
r2 = minimize(err, r.x, method="Powell", bounds=list(zip(lo, hi)),
              options={"maxfev": 40 * len(names), "xtol": 1e-3, "ftol": 1e-4})
x = r2.x if r2.fun <= r.fun else r.x
st = old.PuffState(**{n: float(np.clip(v, *RP.RANGES[n])) for n, v in zip(names, x)})
A, dphi = measure(st)
live = int(np.ceil(min(st.burn + 3.0 * max(st.cool, 1e-3), 4.0) * st.rate))
print(f"OLD law on gusty: budgeted E {min(r.fun, r2.fun):.4f}  sway {100*A:.1f} cm ({A/t_sway[0]:.0%}) phase err {dphi:.0f} deg  "
      f"v_rise {st.v_rise:.2f} gust {st.gust:.2f} live {live}", flush=True)
f5 = json.load(open("/home/user/Spoti-pi/poc/results/f5.json"))["pilot"]
b = f5["fits"][f5["best"]]
print(f"NEW law on gusty: E {b['error']:.4f}  sway {100*b['sway_amp']:.1f} cm ({b['sway_ratio']:.0%}) phase err {b['sway_phase_err']:.0f} deg  "
      f"v_rise {b['state']['v_rise']:.2f} gust {b['state']['gust']:.2f} live {b['live']}", flush=True)
