"""Isolate beat packets: terms with |A| > AMIN, clustered with frequency gap < 2e-6. Rank packets by growth of their
mean square from window w=100 to w=3200, and test whether the packets alone reproduce the measured growth."""
import math, numpy as np
exec(open("poc/farey/beat_model.py").read().split("for F in (3.0, 6.0):")[0])
f, A = terms(6.0)
GAP = float(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else 1e-3
for AMIN in (0.05, 0.01):
    keep = np.abs(A) > AMIN; fk, Ak = f[keep], A[keep]
    cut = np.where(np.diff(fk) > GAP)[0] + 1
    groups = np.split(np.arange(len(fk)), cut)
    multi = [g for g in groups if len(g) > 1]
    print("terms |A| > %.2f: %d; packets: %d (multi-term %d)" % (AMIN, len(fk), len(groups), len(multi)))
    def ms(g, w):
        Rs = np.linspace(w, 2 * w, 64); P = np.exp(2j * math.pi * np.outer(Rs, fk[g])) @ Ak[g]; return 0.5 * np.mean(np.abs(P) ** 2)
    rows = []
    for g in groups:
        rows.append((ms(g, 3200) - ms(g, 100), g))
    rows.sort(key=lambda r: -r[0])
    tot = {w: sum(ms(g, w) for g in groups) for w in (100, 200, 400, 800, 1600, 3200)}
    print("sum over packets (orthogonal-packet model): " + "  ".join("w=%d: %.1f" % (w, math.sqrt(v)) for w, v in tot.items()))
    for dm, g in rows[:8]:
        ls = sorted(set(round(float(fk[j] and 0) + 0, 1) for j in g))
        print("   freq %.7f: %2d terms, amps %s, net %+.3f, spread %.1e, rms(w=100) %.2f -> rms(w=3200) %.2f" % (
            fk[g].mean(), len(g), " ".join("%+.1f" % a for a in sorted(set(np.round(Ak[g], 1)))), Ak[g].sum(), fk[g].max() - fk[g].min(), math.sqrt(ms(g, 100)), math.sqrt(ms(g, 3200))))
