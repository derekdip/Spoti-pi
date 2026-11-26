"""Asymptotic V-profile of l_{r,q}(tau): l = q|tau - tau0| + h + O(e^-|tau|) on both sides; is h independent of r?"""
import math, numpy as np, mpmath as mp
mp.mp.dps = 40
a = 2 * mp.log((3 + mp.sqrt(5)) / 2); lam = mp.exp(a / 2); K = 1 / mp.tanh(a / 2)
def tr(r, q, tau):
    y = 2 * K * mp.cosh(tau / 2); z = 2 * K * mp.cosh((tau + a) / 2)
    p = (z - y / lam) / (lam - 1 / lam); s = y - p
    A = mp.matrix([[lam, 0], [0, 1 / lam]]); B = mp.matrix([[p, 1], [p * s - 1, s]])
    M = mp.eye(2)
    for i in range(1, q + 1):
        M = M * B; k = (i * r) // q - ((i - 1) * r) // q
        if k: M = M * A ** k
    return abs(M[0, 0] + M[1, 1])
L = lambda t: 2 * mp.acosh(t / 2)
T = mp.mpf(60)
print(" q   r    slope+      slope-       c+ = l(T) - qT    c- = l(-T) - qT    tau0 = (c- - c+)/(2q)    h = (c+ + c-)/2    h/q")
rows = {}
for q in (1, 2, 3, 5, 7, 8, 13):
    for r in range(q):
        if math.gcd(r, q) != 1: continue
        lp, lm_ = L(tr(r, q, T)), L(tr(r, q, -T))
        sp = (lp - L(tr(r, q, T - 1))); sm = (lm_ - L(tr(r, q, -T + 1)))
        cp, cm = lp - q * T, lm_ - q * T
        h = (cp + cm) / 2; rows[(r, q)] = h
        print("%2d %3d  %9.6f  %9.6f   %16.12f   %16.12f   %14.10f   %16.12f  %.10f" % (q, r, sp, sm, cp, cm, (cm - cp) / (2 * q), h, h / q))
