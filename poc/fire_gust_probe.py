"""What the teacher's gusted plume actually does, and whether the puff drift law can follow it.

The gust is a known deterministic cause, `gust_amp * sin(2*pi*0.7*t)` forcing the whole velocity
field, so a stateless model should be able to phase-lock to it. F4 could not: on every gusted
scene the fit slowed its parcels to a crawl and filled the swept envelope instead. This measures
the sway the teacher produces, height by height, and compares it with what the drift law predicts.

Scene: `gusty`, declared seen. No F4 scene is touched.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, teacher as TT

W = 2 * np.pi * 0.7


def harmonic(t, y):
    """Amplitude and phase of the 0.7 Hz component of y(t): y ~ mean + A sin(wt - phi)."""
    M = np.stack([np.ones_like(t), np.sin(W * t), np.cos(W * t)], 1)
    c, *_ = np.linalg.lstsq(M, y, rcond=None)
    A = float(np.hypot(c[1], c[2]))
    phi = float(np.arctan2(-c[2], c[1]))          # y = mean + A sin(wt - phi)
    resid = y - M @ c
    frac = 1.0 - float((resid ** 2).sum() / max(((y - y.mean()) ** 2).sum(), 1e-12))
    return c[0], A, phi, frac


def main():
    p, burners, patches, obstacles = scenes.gusty()
    rec = TT.run(p, burners, patches, obstacles)
    X, Y = TT._grid(p)
    ex = rec.T - TT.T_AMBIENT
    t = rec.times
    late = t >= 1.0
    b = burners[0]
    print(f"gust amplitude {p.gust_amp} m/s, 0.7 Hz; burner at x={b.x:.2f}")
    print("\nheight   mean x   sway A   phase (rad)  phase lag vs forcing   explained   peak excess")
    heights = [0.15, 0.3, 0.45, 0.6, 0.8, 1.0, 1.25, 1.5]
    rows = []
    for h in heights:
        j = int(round(h / p.dx))
        row = np.maximum(ex[:, j, :], 0.0)
        m = row.sum(1)
        if m.max() < 5:
            continue
        xc = (row * X[j][None]).sum(1) / np.maximum(m, 1e-9)
        mean, A, phi, frac = harmonic(t[late], xc[late])
        rows.append((h, mean, A, phi, frac, row[late].max()))
        print(f"{h:5.2f}  {mean:7.3f}  {A:7.3f}  {phi:+8.3f}   {np.degrees(phi):+8.1f} deg  {frac:8.2f}   {row[late].max():7.0f} K")
    # what the current law predicts: a parcel born at t_k is displaced by (gust/w)(cos(w t_k) - cos(w t))
    print("\nIf parcels rise at v and the law is x = x0 + (g/w)(cos(w t_k) - cos(w t)), then at height h")
    print("the parcel's age is h/v, its birth phase is w(t - h/v), and the sway seen at that height is")
    print("A(h) = g/w (constant in h), with phase advancing by w*h/v. Measured against that:")
    if len(rows) >= 2:
        hs = np.array([r[0] for r in rows]); As = np.array([r[2] for r in rows]); ps = np.unwrap([r[3] for r in rows])
        print(f"  measured A grows {As[0]:.3f} -> {As[-1]:.3f} m over {hs[0]:.2f} -> {hs[-1]:.2f} m: ratio {As[-1]/max(As[0],1e-9):.1f}x, NOT constant")
        sl = np.polyfit(hs, ps, 1)[0]
        print(f"  measured phase slope {sl:+.2f} rad/m -> implied travel speed {W/abs(sl):.2f} m/s" if abs(sl) > 1e-6 else "  phase flat")
        print(f"  g/w for the teacher's own gust amplitude = {p.gust_amp/W:.3f} m")
    # the base: does the flame root move at all?
    j0 = int(round(0.12 / p.dx))
    row0 = np.maximum(ex[:, j0, :], 0.0)
    xc0 = (row0 * X[j0][None]).sum(1) / np.maximum(row0.sum(1), 1e-9)
    print(f"\nbase (y=0.12) sway: {xc0[late].std()*100:.1f} cm rms, range {np.ptp(xc0[late])*100:.1f} cm -- the root is {'pinned' if np.ptp(xc0[late]) < 0.05 else 'moving'}")
    # tip height over time: does the plume also breathe?
    vis = (ex > 407).astype(float)
    tips = np.array([Y[:, 0][vis[f].any(1)].max() if vis[f].any() else 0.0 for f in range(len(t))])
    mean, A, phi, frac = harmonic(t[late], tips[late])
    print(f"tip height: mean {mean:.2f} m, 0.7 Hz amplitude {A:.3f} m ({frac:.2f} explained) -- the plume {'breathes' if A > 0.05 else 'does not breathe'} with the gust")


if __name__ == "__main__":
    main()
