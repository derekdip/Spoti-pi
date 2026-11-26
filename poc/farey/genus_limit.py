"""Conjecture: lim_{g -> inf} <F_ij>(L) = 2 phi(L_i) phi(L_j),  phi(L) = (L/2) coth(L/2)   (cusps: exactly 2 = 0.20264 pi^2).

Derivation: Mirzakhani-Zograf Thm 3.2 gives [tau_{k+1}]_{g,1}/[tau_k]_{g,1} = 1 - (2k - 1/2)/(pi^2 g) + O(1/g^2), hence the
profile [tau_k]/V -> exp(-k^2/(pi^2 g)); with V_{g,2} ~ 8 pi^2 g V_{g,1} the per-pair sum tends to 2. With boundaries the
pants factor is ~ 2 cosh(Li/2) cosh(Lj/2) e^{-x/2} for large x and volumes carry sinh(L/2)/(L/2).
Test: R_g(L) = [F_{g,2}(L)/V_{g,2}(L)] / [2 phi(L1) phi(L2)] for g = 1..G at several L; if the conjecture holds, all
columns approach 1 together (with the same slow ~1/sqrt(g) convergence seen at L = 0).
"""
import sys
import sympy as sp, mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from higher_volumes import V, P, pants_corner_sum

if __name__ == "__main__":
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    phi = lambda l: 1.0 if l == 0 else (l / 2) / mp.tanh(l / 2)
    Ls = [(0, 0), (1, 1), (2, 0.5), (3, 3)]
    print("g   " + "   ".join(f"R_g at L = {L}" for L in Ls))
    for g in range(1, G + 1):
        Fs, Lsym = pants_corner_sum(g, 2); Vg = sp.expand(V(g, 2)); row = []
        for (a, b) in Ls:
            sub = {Lsym[0]: sp.Float(a, 30), Lsym[1]: sp.Float(b, 30), P: sp.pi}
            val = sp.N(Fs.subs(sub), 25) / sp.N(Vg.subs(sub), 25)
            row.append(float(val) / float(2 * phi(a) * phi(b)))
        print(f"{g}   " + "   ".join(f"{r:.5f}" for r in row), flush=True)
