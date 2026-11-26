"""Local degrees of the flat blind tori (zeros of E*(z, rho/2)) in the chart (x, y), and the boundary winding of E*
around the truncated half fundamental domain 0 <= x <= 1/2, |z| >= 1, y <= YMAX (signed count)."""
import re, math, numpy as np, mpmath as mp
src = open("poc/farey/flat_blind.py").read().split("res = []")[0]; exec(src)
zs = {}; k = None
for line in open("poc/farey/flat_blind.log"):
    m = re.match(r"k = (\d+)", line)
    if m: k = int(m.group(1)); zs[k] = []
    m = re.match(r"\s+z = ([\d.]+) \+ ([\d.]+) i", line)
    if m: zs[k].append((float(m.group(1)), float(m.group(2))))
for k in sorted(zs):
    rho = mp.zetazero(k); s = rho / 2; cf = coefs(s); c2 = xi(2 - 2 * s)
    f = lambda x, y: Estar(s, x, y, cf, c2); h = 1e-6; degs = []
    for x, y in zs[k]:
        fx = (f(x + h, y) - f(x - h, y)) / (2 * h); fy = (f(x, y + h) - f(x, y - h)) / (2 * h)
        degs.append(int(np.sign(fx.real * fy.imag - fx.imag * fy.real)))
    # boundary winding: x = 0 (y from YMAX down to 1), arc |z| = 1 from i to e^{i pi/3}, x = 1/2 up to YMAX, top back
    YMAX = 2.5 + float(rho.imag) / 12
    path = [(0, y) for y in np.linspace(YMAX, 1, 600)] + [(math.cos(t), math.sin(t)) for t in np.linspace(math.pi / 2, math.pi / 3, 300)] + \
           [(0.5, y) for y in np.linspace(math.sqrt(3) / 2, YMAX, 600)] + [(x, YMAX) for x in np.linspace(0.5, 0, 300)]
    vals = np.array([f(x, y) for x, y in path]); w = np.sum(np.angle(vals[1:] / vals[:-1])) / (2 * math.pi)
    print("k = %d: %d flat zeros, degrees %s, signed sum %+d, boundary winding %.3f" % (k, len(degs), degs, sum(degs), w), flush=True)
