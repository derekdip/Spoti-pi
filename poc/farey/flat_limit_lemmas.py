"""Checks for the flat-limit proof.
(1) Parallelogram defect: for every Farey cell (u, w; mediant m = u+w, d = u-w),
    D = N_m^2 + N_d^2 - 2 N_u^2 - 2 N_w^2 = A^2/6 + O(A^3)     (expansion of t_m + t_d = t_u t_w, unit-area det = 1).
(2) Uniform length comparison: fit the unimodular form Q from three root curves using N^2 + A^2/12 = A Q (first-order
    conformal correction -A/(24 n^2)), then the relative error of sqrt(A Q(v) - A^2/12) against N(v), for all simple v up
    to hyperbolic length 30, must be O(A^2) uniformly (no growth with length)."""
import math, numpy as np, mpmath as mp
mp.mp.dps = 60
def run(kap, x, y):
    th = 2 * math.acos(1 - kap / 2); A = 2 * math.pi - th
    X, Y = mp.mpf(x), mp.mpf(y); Zt = (X * Y - mp.sqrt((X * Y) ** 2 - 4 * (X * X + Y * Y - kap))) / 2
    L = lambda t: 2 * mp.acosh(t / 2)
    # homology bookkeeping: roots e0 (x), e1 (y), e0+e1 (z) ... cells (u, w) with vectors
    cells = []; st = [((X, (1, 0)), (Zt, (1, 1)), (Y, (0, 1))), ((Zt, (1, 1)), (Y, (0, 1)), (X, (-1, 0))), ((Y, (0, 1)), (X, (-1, 0)), (Zt, (1, 1)))]
    allv = {(1, 0): L(X), (0, 1): L(Y), (1, 1): L(Zt)}
    while st:
        (tu, vu), (tw, vw), (td, vd) = st.pop(); tm = tu * tw - td; vm = (vu[0] + vw[0], vu[1] + vw[1]); lm = L(tm)
        if lm > 30: continue
        allv[vm] = lm
        Du = L(tu) ** 2; Dw = L(tw) ** 2; Dd = L(td) ** 2; Dm = lm ** 2
        cells.append((float(L(tu) + L(tw)), float(Dm + Dd - 2 * Du - 2 * Dw)))
        st += [((tu, vu), (tm, vm), (tw, vw)), ((tm, vm), (tw, vw), (tu, vu))]
    c = np.array(cells); r = c[:, 1] / (A * A / 6)
    print("kappa %.3f  area A = %.4f:  %d cells;  D/(A^2/6): all in [%.6f, %.6f];  short cells (N_u+N_w < 1) mean %.6f, long (> 10) mean %.6f" % (
        kap, A, len(c), r.min(), r.max(), r[c[:, 0] < 1].mean() if (c[:, 0] < 1).any() else float('nan'), r[c[:, 0] > 10].mean()))
    # (2) fit Q(p, q) = a p^2 + 2 b p q + c q^2 from v = (1,0), (0,1), (1,1)
    q = {v: (float(allv[v]) ** 2 + A * A / 12) / A for v in [(1, 0), (0, 1), (1, 1)]}
    a, cc = q[(1, 0)], q[(0, 1)]; b = (q[(1, 1)] - a - cc) / 2
    det = a * cc - b * b
    q0 = {v: float(allv[v]) ** 2 / A for v in [(1, 0), (0, 1), (1, 1)]}
    a0, c0 = q0[(1, 0)], q0[(0, 1)]; b0 = (q0[(1, 1)] - a0 - c0) / 2
    errs = []
    for (p, qq), l in allv.items():
        Q = a * p * p + 2 * b * p * qq + cc * qq * qq; pred = math.sqrt(max(A * Q - A * A / 12, 1e-300))
        Q0 = a0 * p * p + 2 * b0 * p * qq + c0 * qq * qq; pred0 = math.sqrt(A * Q0)
        errs.append((float(l), abs(pred - float(l)) / float(l), abs(pred0 - float(l)) / float(l)))
    e = np.array(errs)
    bands = [(0, 2), (2, 5), (5, 10), (10, 20), (20, 30)]
    print("     fitted form det %.6f (unimodular -> 1 + O(A));  relative error of the predicted lengths by hyperbolic-length band: " % det +
          "  ".join("[%g,%g): %.1e (uncorrected %.1e)" % (lo, hi, e[(e[:, 0] >= lo) & (e[:, 0] < hi), 1].max(), e[(e[:, 0] >= lo) & (e[:, 0] < hi), 2].max()) for lo, hi in bands if ((e[:, 0] >= lo) & (e[:, 0] < hi)).any()))
for kap in (3.9, 3.96, 3.99, 3.999):
    # a generic shape: sink lengths roughly in ratio 1 : 1.2 : 1.4 at unit area
    th = 2 * math.acos(1 - kap / 2); A = 2 * math.pi - th; s = math.sqrt(A)
    run(kap, 2 * math.cosh(s * 1.0 / 2), 2 * math.cosh(s * 1.2 / 2))

print("\nsigned deviation (N/(sqrt(A) n) - 1)/A for the corrected fit, by length band (mean, min, max):")
def signed(kap):
    th = 2 * math.acos(1 - kap / 2); A = 2 * math.pi - th; s = math.sqrt(A)
    X, Y = mp.mpf(2 * math.cosh(s / 2)), mp.mpf(2 * math.cosh(1.2 * s / 2)); Zt = (X * Y - mp.sqrt((X * Y) ** 2 - 4 * (X * X + Y * Y - kap))) / 2
    L = lambda t: 2 * mp.acosh(t / 2)
    allv = {(1, 0): L(X), (0, 1): L(Y), (1, 1): L(Zt)}
    st = [((X, (1, 0)), (Zt, (1, 1)), (Y, (0, 1))), ((Zt, (1, 1)), (Y, (0, 1)), (X, (-1, 0))), ((Y, (0, 1)), (X, (-1, 0)), (Zt, (1, 1)))]
    while st:
        (tu, vu), (tw, vw), (td, vd) = st.pop(); tm = tu * tw - td; vm = (vu[0] + vw[0], vu[1] + vw[1]); lm = L(tm)
        if lm > 30: continue
        allv[vm] = lm; st += [((tu, vu), (tm, vm), (tw, vw)), ((tm, vm), (tw, vw), (tu, vu))]
    q = {v: (float(allv[v]) ** 2 + A * A / 12) / A for v in [(1, 0), (0, 1), (1, 1)]}
    a, cc = q[(1, 0)], q[(0, 1)]; b = (q[(1, 1)] - a - cc) / 2; det = a * cc - b * b
    a, b, cc = a / math.sqrt(det), b / math.sqrt(det), cc / math.sqrt(det)      # force exactly unimodular
    rows = []
    for (p, qq), l in allv.items():
        n = math.sqrt(a * p * p + 2 * b * p * qq + cc * qq * qq); rows.append((float(l), (float(l) / (s * n) - 1) / A, n))
    r = np.array(rows)
    out = []
    for lo, hi in ((0, 2), (2, 5), (5, 10), (10, 20), (20, 30)):
        m = (r[:, 0] >= lo) & (r[:, 0] < hi)
        out.append("[%g,%g): %+.4f %+.4f %+.4f" % (lo, hi, r[m, 1].mean(), r[m, 1].min(), r[m, 1].max()))
    # first-order prediction -1/(24 n^2) for the shortest
    print("  A = %.4f: " % A + "   ".join(out))
for kap in (3.96, 3.99, 3.999): signed(kap)
