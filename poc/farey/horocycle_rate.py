"""Horocycle equidistribution on the modular surface and the Riemann zeros.

Test function: incomplete Eisenstein series f(z) = sum_{Gamma_inf \\ Gamma} psi(Im gamma z), psi(t) = exp(-1/t).
Unfolding the closed horocycle {x + iy : 0 <= x <= 1} through the Farey/Ford structure gives exactly
    a(y) = int_0^1 f(x+iy) dx = psi(y) + sqrt(pi y) * sum_{c>=1} phi(c)/c * exp(-c^2 y)
(each denominator c contributes phi(c) Farey fractions d/c). Mean of f = 3/pi.
Mellin transform: zeta(2s-1)/zeta(2s) * sqrt(pi) Gamma(s-1/2), so
    a(y) - 3/pi = sum_rho R_rho y^(1 - rho/2) + sum_k T_k y^(1+k),
    R_rho = sqrt(pi) zeta(rho-1) Gamma((rho-1)/2) / (2 zeta'(rho)),
    T_k   = sqrt(pi) zeta(-2k-1) Gamma(-k-1/2) / (2 zeta'(-2k)).
|y^(1-rho/2)| = y^(1-beta/2): RH  <=>  error = O(y^(3/4 - eps))  (Zagier 1981).
"""
import numpy as np, mpmath as mp
mp.mp.dps = 30
NMAX = 4_000_000
phi = np.arange(NMAX + 1, dtype=np.int64)
for p in range(2, NMAX + 1):
    if phi[p] == p:
        phi[p::p] -= phi[p::p] // p
c = np.arange(1, NMAX + 1, dtype=np.longdouble)
w = phi[1:].astype(np.longdouble) / c

def a_minus_mean(y):
    y = np.longdouble(y)
    n = int(min(NMAX, np.sqrt(80 / float(y))))
    s = np.sum(w[:n] * np.exp(-c[:n] ** 2 * y))      # longdouble, terms positive
    return float(np.sqrt(np.longdouble(np.pi) * y) * s + np.exp(-1 / y) - np.longdouble(3) / np.longdouble(np.pi))

zeros = [mp.zetazero(k) for k in range(1, 31)]
R = [mp.sqrt(mp.pi) * mp.zeta(r - 1) * mp.gamma((r - 1) / 2) / (2 * mp.zeta(r, derivative=1)) for r in zeros]
T = [mp.sqrt(mp.pi) * mp.zeta(-2 * k - 1) * mp.gamma(-k - mp.mpf(1) / 2) / (2 * mp.zeta(-2 * k, derivative=1)) for k in range(1, 6)]
print("first zero gamma_1 = %.6f;  |R_1| = %.3e, |R_2| = %.3e, |R_5| = %.3e" % (zeros[0].imag, abs(R[0]), abs(R[1]), abs(R[4])))

def predicted(y, nz=30):
    y = mp.mpf(y)
    e = sum(2 * (Rr * y ** (1 - r / 2)).real for Rr, r in zip(R[:nz], zeros[:nz]))   # rho and conj(rho)
    return float(e + sum(Tk * y ** (2 + k) for k, Tk in enumerate(T)))

print("\n      y        E(y) measured      zeros prediction    E/y^(3/4)     E/y^(1/2)")
ys = np.logspace(-1, -11, 41)
rows = []
for y in ys:
    E = a_minus_mean(y); P = predicted(y)
    rows.append((y, E, P))
    print("  %.2e   % .10e   % .10e   % .4e   % .3e" % (y, E, P, E / y ** 0.75, E / y ** 0.5))

big = [(y, E, P) for y, E, P in rows if abs(P) > 1e-14]
print("\nmax |measured - predicted| over y <= 0.03: %.2e (float64 rounding of the mean ~ 1e-16)" % max(abs(E - P) for y, E, P in rows if y < 0.03))
print("first zero only, y <= 1e-4: max |E - pred_1| / y^(3/4) = %.2e  (vs |E|/y^(3/4) up to %.2e)" % (max(abs(E - predicted(y, 1)) / y ** 0.75 for y, E, P in rows if y < 1e-4), max(abs(E) / y ** 0.75 for y, E, P in rows if y < 1e-4)))
logy = np.log(ys); E = np.array([r[1] for r in rows])
for alpha in (0.5, 0.75, 1.0):
    r = np.abs(E) / ys ** alpha
    print("alpha = %.2f: E/y^alpha envelope at y~1e-3: %.2e, at y~1e-11: %.2e" % (alpha, r[np.abs(logy - np.log(1e-3)).argmin()-2:np.abs(logy - np.log(1e-3)).argmin()+3].max(), r[-5:].max()))
# frequency in log y of E/y^(3/4): fit A cos(w log y + p)
from scipy.optimize import curve_fit
yy = np.logspace(-3, -11, 400); EE = np.array([a_minus_mean(y) for y in yy]) / yy ** 0.75
f = lambda L, A, wv, p: A * np.cos(wv * L + p)
popt, _ = curve_fit(f, np.log(yy), EE, p0=[2 * float(abs(R[0])), 7.07, 0.0])
print("fit E/y^(3/4) = A cos(w log y + p): A = %.4e (2|R_1| = %.4e), w = %.6f (gamma_1/2 = %.6f)" % (abs(popt[0]), 2 * abs(R[0]), abs(popt[1]), zeros[0].imag / 2))
np.save("poc/farey/horocycle_rate.npy", np.array([yy, EE]))
E1 = EE * yy ** 0.75
env = [np.abs(E1[(yy <= 10.0 ** -k) & (yy > 10.0 ** -(k + 1))]).max() for k in range(5, 11)]
print("decades 1e-5..1e-11: max|E|/y^(3/4) =", " ".join("%.3e" % np.abs(EE[(yy <= 10.0 ** -k) & (yy > 10.0 ** -(k + 1))]).max() for k in range(5, 11)), " (2|R_1| = %.3e)" % (2 * float(abs(R[0]))))
print("fitted envelope exponent (decades 1e-5..1e-11): %.4f" % np.polyfit([-k - 0.5 for k in range(5, 11)], np.log10(env), 1)[0])
