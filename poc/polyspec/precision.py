"""Per-coefficient relative error of the float64 monoid evaluation vs the 60-digit run of the same algorithm."""
import random, math
from bench import heptagon, run_mp
from polyspec import polygon_dft
rng = random.Random(5)
for e in (3, 4, 5, 6, 7, 9, 12):
    N = 10 ** e; V = heptagon(N)
    low = [(rng.randrange(1, 20), rng.randrange(1, 20)) for _ in range(4)]
    high = [(rng.randrange(N), rng.randrange(N)) for _ in range(4)]
    def rel(ks): return [abs(complex(polygon_dft(V, kx, ky, N)) - complex(run_mp(V, kx, ky, N))) / abs(complex(run_mp(V, kx, ky, N))) for kx, ky in ks]
    rl, rh = rel(low), rel(high)
    print("N = 1e%-2d  low k: max rel error %.1e | random k: max rel error %.1e (median %.1e)" % (e, max(rl), max(rh), sorted(rh)[2]), flush=True)
