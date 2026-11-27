"""(3) Amortised updates and (4) tick-rate choice for Quest display rates."""
import numpy as np
from math import gcd
from fractions import Fraction
from schedule import TickSchedule, continued_fraction, convergents, amortize
print("(3) amortised updates: N objects, each updated once per M frames")
for N, M in ((1000, 72), (37, 10), (5, 72)):
    loads = [len(amortize(N, M, f)) for f in range(4 * M)]
    last = {}; gaps = []
    for f in range(4 * M):
        for i in amortize(N, M, f):
            if i in last: gaps.append(f - last[i])
            last[i] = f
    naive = [min(-(-N // M), N - f * (-(-N // M))) if N - f * (-(-N // M)) > 0 else 0 for f in range(M)]   # ceil(N/M) per frame until done
    print("   N = %4d, M = %3d: Christoffel load per frame %s..%s, staleness exactly %s frames; naive ceil-chunks load %d..%d" % (
        N, M, min(loads), max(loads), sorted(set(gaps)), min(naive), max(naive)))
print("\n(4) per-frame tick patterns for Quest display rates (no interpolation: displacement per frame = ticks/T)")
print("%5s %5s %8s %22s %14s %16s" % ("disp", "tick", "period", "ticks/frame pattern", "judder (cv)", "max state age"))
for F in (72, 80, 90, 120):
    for T in (30, 45, 50, 60, 72, 90, 100, 120, 144, 360, 720):
        sch = TickSchedule(T, F); p, _ = sch.period()
        tk = [sch.ticks_in_frame(s, s + 1) for s in range(p)]
        cv = np.std(tk) / np.mean(tk)                       # relative variation of per-frame motion = visible judder
        age = max(((s * sch.T) % sch.F) / sch.F for s in range(p)) / T * 1000   # ms since the newest state, worst case
        pat = "".join(str(x) for x in tk[:12]) + ("..." if p > 12 else "")
        if T in (50, 60, 72, 90, 120, 720) or cv == 0:
            print("%5d %5d %8d %22s %14.3f %13.2f ms" % (F, T, p, pat, cv, age))
from functools import reduce
lcm = reduce(lambda a, b: a * b // gcd(a, b), (72, 80, 90, 120))
print("\n   tick rates giving an integer number of ticks per frame on all of 72/80/90/120 Hz: multiples of lcm = %d" % lcm)
print("\n(4b) near-rational ratios: continued fractions give the 'hiccup' structure")
for T, F, label in ((Fraction(60000, 1001), 60, "59.94 Hz content on a 60 Hz display"), (60, Fraction(72, 1), "60 Hz physics on 72 Hz"), (50, 72, "50 Hz physics on 72 Hz"), (Fraction(2997, 50), 72, "59.94 Hz video on 72 Hz")):
    r = Fraction(T) / Fraction(F); cf = continued_fraction(r.numerator, r.denominator); cv = convergents(cf)
    sch = TickSchedule(r.numerator, r.denominator); p = r.denominator
    tk = [sch.ticks_in_frame(s, s + 1) for s in range(min(p, 4000))]
    runs = []; c = 1
    for a, b in zip(tk, tk[1:]):
        if a == b: c += 1
        else: runs.append((a, c)); c = 1
    runs.append((tk[-1], c))
    common = sorted(set(runs), key=lambda x: -runs.count(x))[:3]
    print("   %-38s ratio %s = [%s], convergents %s; period %d frames (%.2f s); commonest runs (ticks, length): %s" % (
        label, r, ";".join(map(str, cf[:6])) + ("..." if len(cf) > 6 else ""), ", ".join("%d/%d" % c_ for c_ in cv[:5]), p, p / float(F), common))
