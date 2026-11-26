"""Compare blind flat tori and blind hyperbolic tori in shape coordinates of the three shortest curves:
flat z in F (x >= 0): lengths (1, |z|, |z-1|) -> (|z|, |z-1|); hyperbolic sink (x <= y <= z traces) -> (b/a, c/a)."""
import re, math, numpy as np
L = lambda t: 2 * math.acosh(t / 2)
flat = {}; k = None
for line in open("poc/farey/flat_blind.log"):
    m = re.match(r"k = (\d+)", line)
    if m: k = int(m.group(1)); flat[k] = []
    m = re.match(r"\s+z = ([\d.]+) \+ ([\d.]+) i", line)
    if m: z = complex(float(m.group(1)), float(m.group(2))); flat[k].append((abs(z), abs(z - 1)))
hyp = {}
for fn in ("poc/farey/zb_count_fine_a.log", "poc/farey/zb_count_fine_b.log", "poc/farey/hyp_census2_a.log", "poc/farey/hyp_census2_b.log"):
    try: lines = open(fn).read().splitlines()
    except FileNotFoundError: continue
    for line in lines:
        m = re.match(r"k = (\d+)", line)
        if m: k = int(m.group(1)); hyp.setdefault(k, [])
        m = re.match(r"\s+traces \(([\d.]+), ([\d.]+), ([\d.]+)\)", line)
        if m:
            a, b, c = sorted(L(float(g)) for g in m.groups()); pt = (b / a, c / a)
            if not any(abs(pt[0] - q[0]) < 1e-5 and abs(pt[1] - q[1]) < 1e-5 for q in hyp[k]): hyp[k].append(pt)
for k in sorted(set(flat) & set(hyp)):
    F = sorted(flat[k]); H = sorted(hyp[k])
    print("k = %d: flat %d, hyperbolic %d" % (k, len(F), len(H)))
    print("   flat (|z|, |z-1|):  " + "  ".join("(%.3f, %.3f)" % p for p in F))
    print("   hyp  (b/a, c/a):    " + "  ".join("(%.3f, %.3f)" % p for p in H))
