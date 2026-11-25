"""Weil-Petersson average of the dual area over the moduli space of one-holed tori (boundary L; L = 0 cusped).

Prediction (Mirzakhani unfolding + the gap law g = log((cosh l + cosh(L/2))/(cosh l - 1)), N = l/2):
    int over M_{1,1}(L) of A* = (L^2 + 4 pi^2)^2 / 384,   Vol = (L^2 + 4 pi^2)/24  (both in the unfolded normalisation,
    twice Mirzakhani's orbifold V_{1,1}(L) = (L^2 + 4 pi^2)/48),  so  average A* = (L^2 + 4 pi^2)/16 = 3 V_{1,1}(L).
Independent check: integrate directly over a fundamental domain in Fenchel-Nielsen coordinates (l, tau) of a curve
alpha, with omega_WP = dl ^ dtau (Wolpert):  D = { alpha is the systole, |tau| <= l/2 }.  Traces: a = 2 cosh(l/2),
tr of the transverse curve b = C cosh(tau/2), C = 2 sqrt((a^2 - mu)/(a^2 - 4)), mu = 2 - 2 cosh(L/2) (this solves the
trace relation for every tau, and tau -> tau + l is the Dehn twist). alpha is the systole iff 2 cosh(l/2) <= C cosh(tau/2).
"""
import math, sys
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from limits import curves, g as gap, N as Nf


def Astar(a, b, mu):
    cv, _ = curves(a, b, mu, tol=1e-12)
    return sum(gap(t, mu) * Nf(t) for t in cv.values())


def domain(L):
    mu = 2 - 2 * math.cosh(L / 2)
    C = lambda l: 2 * math.sqrt((4 * math.cosh(l / 2)**2 - mu) / (4 * math.cosh(l / 2)**2 - 4))
    # tau range at given l: |tau| <= min(l/2, tau_sys(l)), where 2 cosh(l/2) >= C cosh(tau/2) fails beyond tau_sys
    def tau_max(l):
        r = 2 * math.cosh(l / 2) / C(l)
        return l / 2 if r <= 1 else min(l / 2, 2 * math.acosh(r)) if False else (l / 2 if r <= 1 else None)
    # systole condition at |tau| = t: 2cosh(l/2) <= C cosh(t/2)  <=>  t >= 2 acosh(2cosh(l/2)/C) when that ratio > 1
    def tau_interval(l):
        r = 2 * math.cosh(l / 2) / C(l)
        lo = 0.0 if r <= 1 else 2 * math.acosh(r)
        return (lo, l / 2) if lo < l / 2 else None
    # l_max: where the interval closes
    lo, hi = 1e-6, 40.0
    for _ in range(200):
        m = (lo + hi) / 2
        if tau_interval(m) is None: hi = m
        else: lo = m
    return mu, C, tau_interval, lo


def integrate(L, nl=48, nt=20):
    mu, C, tau_interval, lmax = domain(L)
    xl, wl = np.polynomial.legendre.leggauss(nl); xt, wt = np.polynomial.legendre.leggauss(nt)
    vol = 0.0; I = 0.0
    # l substitution l = lmax * s^2 (clusters nodes near the cusp l -> 0)
    for x, w in zip(xl, wl):
        s = (x + 1) / 2; l = lmax * s * s; dl = lmax * 2 * s * w / 2
        iv = tau_interval(l)
        if iv is None: continue
        t0, t1 = iv
        for y, v in zip(xt, wt):
            tau = t0 + (t1 - t0) * (y + 1) / 2; dt = (t1 - t0) * v / 2
            a = 2 * math.cosh(l / 2); b = C(l) * math.cosh(tau / 2)
            vol += 2 * dl * dt; I += 2 * dl * dt * Astar(a, b, mu)      # factor 2: tau and -tau
    return vol, I, lmax


if __name__ == "__main__":
    for L in (0.0, 2.0, 5.0):
        vol, I, lmax = integrate(L)
        pv, pI = (L * L + 4 * math.pi**2) / 24, (L * L + 4 * math.pi**2)**2 / 384
        print(f"L = {L}: domain l in (0, {lmax:.4f}];  Vol = {vol:.6f} (predicted {pv:.6f});  int A* = {I:.6f} (predicted {pI:.6f});  "
              f"average A* = {I / vol:.6f} (predicted (L^2 + 4 pi^2)/16 = {(L * L + 4 * math.pi**2) / 16:.6f})")
