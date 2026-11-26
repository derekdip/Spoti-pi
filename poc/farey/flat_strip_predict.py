"""Two-term prediction on the strip vs measured (flat_strip logs), hexagonal z:
   diff(A) = (A/12) s zeta(s) E(z, s/2+1) - 2^{-s} s zeta(s-1) E(z, 3/2) M(s) A^{(s+1)/2},  M(s) = pi^{-s} zeta(s+1)/cos(pi s/2)."""
import re, math, mpmath as mp
exec(open("poc/farey/flat_first_order.py").read().split("pts = {")[0])
z = mp.mpc(0.5, math.sqrt(3) / 2)
M = lambda s: mp.pi ** (-s) * mp.zeta(s + 1) / mp.cos(mp.pi * s / 2)
# check M against direct quadrature
for s in (0.5, 1.5, 2.5):
    Psi = lambda y: (mp.coth(y) - 1 / y - y / 3) if y > 1e-3 else -y ** 3 / 45
    if 1 < s < 3: print("M(%.1f): closed form %.8f, quadrature %.8f" % (s, float(M(s)), float(mp.quad(lambda y: y ** (-s - 1) * Psi(y), [0, 1, 10, mp.inf]))))
data = {}
for fn in ("poc/farey/flat_strip_a.log", "poc/farey/flat_strip_b.log", "poc/farey/flat_strip_c.log"):
    s = None
    for line in open(fn):
        m = re.match(r"s = ([\d.]+)", line)
        if m: s = float(m.group(1)); data[s] = []
        m = re.search(r"A=([\d.]+): diff/A ([-\d.]+)", line)
        if m: data[s].append((float(m.group(1)), float(m.group(2))))
for s in sorted(data):
    c1 = float(s * mp.zeta(s) * E(s / 2 + 1, z) / 12); c2 = float(-mp.mpf(2) ** (-s) * s * mp.zeta(s - 1) * E(1.5, z) * M(s))
    print("s = %.2f: first-order coeff %.4f, staircase coeff %.4f (power %.2f)" % (s, c1, c2, (s + 1) / 2))
    for A, dA in data[s]:
        pred = c1 + c2 * A ** ((s - 1) / 2)
        print("    A = %.3f: measured diff/A %.4f   two-term prediction %.4f   gap %.4f" % (A, dA, pred, dA - pred))
