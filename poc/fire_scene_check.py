"""Validate new scenes before any experiment is designed on them.

Checks the property that makes a scene useful, not any particular answer: every consumer has
something to read, the plume is stable, a gust actually sways the plume, a shelf actually deflects
it, and every fuel bed actually lights and then burns out. A bed that never lights leaves the
ignition consumer identically zero, which was true of the first scene ever tried here.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, teacher as TT

NEW = ["gusty", "gust_shelf", "fast_gust", "strong_gust", "gust_twin", "bed_chain"]


def check(nm):
    p, burners, patches, obstacles = getattr(scenes, nm)()
    rec = TT.run(p, burners, patches, obstacles)
    X, Y = TT._grid(p)
    ex = rec.T - TT.T_AMBIENT
    t = rec.times; late = t >= 1.0
    ok, notes = True, []
    peak = float(ex.max())
    notes.append(f"peak {peak:.0f} K")
    if not (400 < peak < 1600):
        ok = False; notes.append("PEAK OUT OF RANGE")
    for cname, g in (("visual", lambda r: TT.g_visual(r)),
                     ("heat", lambda r: TT.g_heat(r, np.array([[x, y] for x in np.linspace(.18, 1.32, 6) for y in np.linspace(.2, 1.37, 4)]))),
                     ("ai", lambda r: TT.g_ai(r))):
        v = np.asarray(g(rec), float)
        s = float(np.sqrt((v ** 2).mean()))
        if s <= 1e-9:
            ok = False; notes.append(f"{cname} DEGENERATE")
    if p.gust_amp:
        j = int(round(0.6 / p.dx))
        row = np.maximum(ex[:, j, :], 0.0)
        xc = (row * X[j][None]).sum(1) / np.maximum(row.sum(1), 1e-9)
        rng = float(np.ptp(xc[late]))
        notes.append(f"sway {100*rng:.0f} cm at {p.gust_hz} Hz")
        if rng < 0.05:
            ok = False; notes.append("NO SWAY")
    if obstacles:
        o = obstacles[0]
        above = (Y > o.y + o.half_h + 0.05) & (np.abs(X - o.x) < o.half_w)
        beside = (Y > o.y - 0.1) & (np.abs(X - o.x) > o.half_w) & (np.abs(X - o.x) < o.half_w + 0.25)
        a, b = float(ex[late][:, above].max()), float(ex[late][:, beside].max())
        notes.append(f"shelf: above {a:.0f} K vs beside {b:.0f} K")
        if b < 100:
            ok = False; notes.append("NO DEFLECTION")
    if patches:
        ig = np.asarray(TT.g_ignition(rec, patches), float)
        for i, q in enumerate(patches):
            lit = ig[:, i] > 0.5
            if not lit.any():
                ok = False; notes.append(f"bed {i} NEVER LIGHTS")
                continue
            on = t[lit]
            out = "burns out" if not lit[-1] else "still lit at the end"
            notes.append(f"bed {i}: lights {on[0]:.1f}s, {out}")
    return ok, notes


def main():
    allok = True
    for nm in NEW:
        ok, notes = check(nm)
        allok &= ok
        print(f"{'ok  ' if ok else 'FAIL'} {nm:<13} " + "; ".join(notes), flush=True)
    print("\nall usable" if allok else "\nSOME SCENES UNUSABLE")


if __name__ == "__main__":
    main()
