"""Is per-frame glow correlation a fair measure of 'looks like fire'? Tested with no model in it.

F4 froze its glow bar on the correlation between the cheap coarse glow and the teacher's, pooled
over the second half of the run. The F5 pilot found a state that tracks the teacher's sway at 87
percent of its amplitude scoring WORSE on that correlation than a state with no sway at all. If
that is a property of the measure rather than of the model, the measure cannot be used to ask
whether a fire looks right.

This asks the question without fitting anything. The competitors are built from the teacher's own
output: its time-average (a perfect static blob, no motion at all) and delayed copies of the
teacher itself (a perfect model that is slightly late). If the static average beats a delayed
copy of the truth, the measure prefers the average and is disqualified.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poc.fire import scenes, teacher as TT


def corr(a, b):
    a, b = np.asarray(a, float).ravel(), np.asarray(b, float).ravel()
    if a.std() <= 0 or b.std() <= 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def main():
    for nm in ("gusty", "ignition", "full"):
        p, burners, patches, obstacles = getattr(scenes, nm)()
        rec = TT.run(p, burners, patches, obstacles)
        g = TT.g_visual(rec)[::4]                       # the frames a case scores
        F = g.shape[0]
        late = slice(F // 2, None)
        tgt = g[late]
        static = np.broadcast_to(g[late].mean(0)[None], tgt.shape)   # a perfect static blob
        print(f"\n{nm} (gust {p.gust_amp} m/s at {p.gust_hz} Hz)")
        print(f"  teacher's own time-average, no motion at all : corr {corr(tgt, static):.3f}")
        dt = (rec.times[::4][1] - rec.times[::4][0])
        for lag in (1, 2, 3, 4):
            shifted = g[F // 2 - lag: F - lag]           # the teacher itself, delayed
            print(f"  the teacher itself, delayed {lag*dt:.2f} s ({np.degrees(2*np.pi*p.gust_hz*lag*dt):3.0f} deg of gust) : corr {corr(tgt, shifted):.3f}")
        # and the teacher delayed by half a gust period: the worst case a swaying model can hit
        half = max(int(round(0.5 / p.gust_hz / dt)), 1)
        if F // 2 - half >= 0:
            print(f"  the teacher itself, delayed half a gust period : corr {corr(tgt, g[F // 2 - half: F - half]):.3f}")


if __name__ == "__main__":
    main()
