"""Which properties of the Markoff/Farey tree survive for the generalised Markoff equation
x^2 + y^2 + z^2 - xyz = mu  (mu = 0: the punctured torus; mu = 2 - 2 cosh(L/2) < 0: a one-holed torus whose
boundary geodesic has length L). Exploratory probe; predictions were derived by hand before the run.

Tested at each mu, on the Farey tree from the root pair of traces (4, 4):
 P1  the cell recursion Phi(a,b) = Phi(a,c) + Phi(c,b) + h(c) - mu/(2abc), with
     Phi(a,b) = (s(a) + s(b) - 1 - d(a,b))/4, s(x) = sqrt(1 - 4/x^2), d(a,b) = sqrt(1 - 4/a^2 - 4/b^2 + 4 mu/(a^2 b^2))
     (d is (c - c')/(ab), the gap between the two roots for the third trace), h(x) = (1 - s(x))/2;
 P2  the atoms are positive and form a max-heap down the tree;
 P3  their sum over the tree equals Phi at the root (the frontier's Phi goes to zero);
 P4  the gap of the stable norm's one-sided slopes at a rational direction, g = log((c^2 - mu)/(c^2 - 4)),
     derived from the fans k m +- x;
 P5  the series law with one extra resistor: 1/(c c') = 1/a^2 + 1/b^2 - mu/4 in reciprocal half-traces;
 P6  the Farey-Schauder ratio D/Phi tends to 4 deep in the tree, D = F(a) + F(b) - F(c), F = arccosh(t/2).
"""
import mpmath as mp
mp.mp.dps = 120
s = lambda x: mp.sqrt(1 - 4 / x**2)
h = lambda x: (1 - s(x)) / 2
F = lambda t: mp.acosh(t / 2)


def run(mu, depth=13, cap=mp.mpf(10)**25):
    d = lambda a, b: mp.sqrt(1 - 4 / a**2 - 4 / b**2 + 4 * mu / (a**2 * b**2))
    Phi = lambda a, b: (s(a) + s(b) - 1 - d(a, b)) / 4
    child = lambda a, b: (a * b + mp.sqrt(a**2 * b**2 - 4 * (a**2 + b**2 - mu))) / 2
    a0 = b0 = mp.mpf(4); root = Phi(a0, b0)
    P1 = P2 = True; atoms = mp.mpf(0); frontier = mp.mpf(0); gap_err = mp.mpf(0); ser_err = mp.mpf(0); ratios = []
    st = [(a0, b0, 0, None)]
    while st:
        a, b, k, parent_atom = st.pop(); c = child(a, b); atom = h(c) - mu / (2 * a * b * c)
        P1 &= abs(Phi(a, b) - Phi(a, c) - Phi(c, b) - atom) < mp.mpf(10)**-80
        P2 &= atom > 0 and (parent_atom is None or atom < parent_atom)
        atoms += atom
        cp = a * b - c; ser_err = max(ser_err, abs(1 / ((2 / c) * (2 / cp)) - (a**2 / 4 + b**2 / 4 - mu / 4)) / (a**2 / 4))
        if k < 6:   # gap law from the fans
            lam = c / 2 + mp.sqrt(c**2 / 4 - 1); tp = [a, a * c - b]; sp = [a, b]
            for _ in range(80): tp.append(c * tp[-1] - tp[-2]); sp.append(c * sp[-1] - sp[-2])
            gap = F(tp[80]) + F(sp[80]) - 2 * 80 * F(c); gap_err = max(gap_err, abs(gap - mp.log((c**2 - mu) / (c**2 - 4))))
        if k >= 6 and a < mp.mpf(10)**8 and b < mp.mpf(10)**8: ratios.append((F(a) + F(b) - F(c)) / Phi(a, b))
        if k < depth and c < cap: st += [(a, c, k + 1, atom), (c, b, k + 1, atom)]
        else: frontier += Phi(a, c) + Phi(c, b)
    P3 = abs(atoms + frontier - root) < mp.mpf(10)**-60
    return dict(mu=mu, P1=P1, P2=P2, P3=P3, root=root, atoms=atoms, frontier=frontier, gap_err=gap_err, ser_err=ser_err,
                ratio_min=min(ratios), ratio_max=max(ratios))


if __name__ == "__main__":
    for mu in (0, -0.5, -2, -8, -20):
        r = run(mp.mpf(mu))
        L = 2 * mp.acosh(1 - mp.mpf(mu) / 2) if mu < 0 else 0
        print(f"mu = {mu:>5} (boundary length {mp.nstr(L, 4)}):")
        print(f"   P1 exact cell recursion with atom h(c) - mu/(2abc): {'PASS' if r['P1'] else 'FAIL'}")
        print(f"   P2 atoms positive and a max-heap: {'PASS' if r['P2'] else 'FAIL'}")
        print(f"   P3 atoms + frontier = Phi(root): {'PASS' if r['P3'] else 'FAIL'}; atoms so far {mp.nstr(r['atoms'], 10)}, frontier {mp.nstr(r['frontier'], 3)}, Phi(root) {mp.nstr(r['root'], 10)}")
        print(f"   P4 gap law log((c^2-mu)/(c^2-4)): max error {mp.nstr(r['gap_err'], 3)} {'PASS' if r['gap_err'] < 1e-30 else 'FAIL'}")
        print(f"   P5 series law with extra resistor -mu/4: max relative error {mp.nstr(r['ser_err'], 3)} {'PASS' if r['ser_err'] < 1e-60 else 'FAIL'}")
        print(f"   P6 D/Phi on deep cells: {mp.nstr(r['ratio_min'], 8)} to {mp.nstr(r['ratio_max'], 8)}")
