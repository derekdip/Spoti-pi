"""A one-parameter slice of quasi-Fuchsian space of the punctured torus, and the dual area on it.

Cusped characters (mu = 0) with tr e0 = 3 fixed and b = tr e1 complex; c = tr(e0 - e1) the smaller root of
z^2 - 3b z + 9 + b^2 = 0. At each grid point the trace tree is grown to depth DEPTH in the two cones (e0, e1) and
(e0, -e1). Bowditch's conditions (traces off [-2, 2], finitely many with |t| <= 2) are tested as: every node of depth
>= 3 has |t| > 2 and the deepest level has min log|t| >= GROW. The set passing is the slice of the Bowditch set
(conjecturally = quasi-Fuchsian space). Inside, the dual area A* = sum g N (principal branches: accurate near the
real locus, where short curves have small twist) is accumulated over the same tree.
  python3 poc/farey/qf_slice.py            # picture -> docs/figures/qf_slice.png
"""
import sys, math
import numpy as np

DEPTH, GROW = 11, 4.0


def slice_grid(re, im, chunk=1500):
    ins, A = slice_points((re[None, :] + 1j * im[:, None]).ravel(), chunk)
    return ins.reshape(len(im), len(re)), A.reshape(len(im), len(re))


def slice_points(B, chunk=1500):
    B = np.asarray(B, complex); inside = np.zeros(B.size, bool); As = np.full(B.size, np.nan + 0j)
    for s in range(0, B.size, chunk):
        b = B[s:s + chunk]; a = np.full_like(b, 3.0)
        disc = np.sqrt((3 * b)**2 - 4 * (9 + b * b)); r1, r2 = (3 * b - disc) / 2, (3 * b + disc) / 2
        c = np.where(np.abs(r1) <= np.abs(r2), r1, r2); w = 3 * b - c
        term = lambda t: np.log(1 + 4 / (t * t - 4)) * np.arccosh(t / 2)
        with np.errstate(all="ignore"):
            A = term(a) + term(b); ok = np.ones(b.size, bool)
            for (L0, R0, O0) in ((a, b, c), (a, b, w)):          # cone (e0, e1) opp e0-e1; cone (e0, -e1) opp e0+e1
                L, R, O = L0[None], R0[None], O0[None]
                for d in range(1, DEPTH + 1):
                    M = L * R - O; A = A + np.nansum(term(M), axis=0)
                    if d >= 3: ok &= np.all(np.abs(M) > 2, axis=0)
                    if d == DEPTH: ok &= np.min(np.log(np.abs(M) + 1e-300), axis=0) >= GROW
                    L, R, O = np.concatenate([L, M]), np.concatenate([M, R]), np.concatenate([R, L])
        inside[s:s + chunk] = ok; As[s:s + chunk] = np.where(ok, A, np.nan)
    return inside, As


def rays():
    """From the modular torus b = 3 along rays: the boundary distance, and A*, M (holomorphic continuation along the ray)."""
    import cmath
    sys.path.insert(0, __file__.rsplit("/", 1)[0]); import complex_limits as CL
    for th in (90, 45, 135, 170):
        u = cmath.exp(1j * math.radians(th)); ts = np.linspace(0, 7, 2801); ins, _ = slice_points(3 + ts * u)
        tb = ts[np.argmax(~ins)] if (~ins).any() else None
        print(f"ray at {th} deg from b = 3: leaves the Bowditch set at distance {tb:.4f} (b = {3 + tb * u:.4f})")
        for f in (0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 0.99):
            def path(s_, f=f): b = 3 + s_ * f * tb * u; return 3.0 + 0j, b, 0j
            AB, As, M, n, gs, Ns = CL.continued_invariants(path, steps=60)
            shortest = min(Ns.values(), key=lambda z: abs(z.real))
            print(f"   {f:.2f} of the way: {n:>7} curves;  A* = {As.real:+.5f}{As.imag:+.5f}i;  M = {M.real:+.5f}{M.imag:+.5f}i;  shortest Re N = {shortest.real:.4f}")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "rays":
    rays(); sys.exit()
if __name__ == "__main__":
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    re = np.linspace(0.5, 8.5, 481); im = np.linspace(-5, 5, 601)
    inside, As = slice_grid(re, im)
    frac = inside.mean(); print(f"grid {inside.shape}, inside fraction {frac:.3f}")
    j3 = np.argmin(abs(re - 3)); i0 = np.argmin(abs(im)); print(f"A* at b = 3: {As[i0, j3]:.6f} (exact 2.697090)")
    # boundary along rays from b = 3
    for th in (90, 60, 30, 120, 150):
        u = np.exp(1j * math.radians(th)); ts = np.linspace(0, 8, 1601); pts = 3 + ts * u
        ins, Ar = slice_grid(pts.real.copy(), np.array([0.0])) if False else (None, None)
    blues = ["#cce3fd", "#9dc8f7", "#6aabf1", "#338ced", "#2370cd", "#1757ac", "#0e3d7e"]
    cmap = LinearSegmentedColormap.from_list("seqblue", blues); cmap.set_bad("#efefef")
    fig, ax = plt.subplots(figsize=(8.4, 6.6), dpi=150)
    im_ = ax.imshow(np.where(inside, As.real, np.nan), extent=[re[0], re[-1], im[0], im[-1]], origin="lower", cmap=cmap, aspect="equal", interpolation="nearest")
    ax.plot([6 / math.sqrt(5), re[-1]], [0, 0], color="#ffffff", lw=1.2, alpha=0.9); ax.annotate("Fuchsian (real) locus", (7.2, 0), (6.4, 0.6), fontsize=8.5, color="#fff")
    ax.plot([3], [0], marker="o", ms=6, mfc="white", mec="#0e3d7e", mew=2)
    ax.annotate("modular torus  b = 3", (3, 0), (3.6, -1.2), fontsize=9, color="#222", arrowprops=dict(arrowstyle="-", color="#555", lw=0.8))
    for (x, y, lab, dx, dy) in ((3, 2, "cusp: e0 - e1 parabolic (b = 3 + 2i)", 0.35, 0.35), (3, -2, "b = 3 - 2i", 0.35, -0.45), (2, 0, "cusp: e1\nparabolic\n(b = 2)", -1.35, 0.9)):
        ax.plot([x], [y], marker="o", ms=5, mfc="#ffffff", mec="#222222", mew=1.2)
        ax.annotate(lab, (x, y), (x + dx, y + dy), fontsize=8, color="#222", arrowprops=dict(arrowstyle="-", color="#555", lw=0.7))
    ax.text(0.6, 3.2, "Shaded: depth-11\nBowditch test\n(conservative; the true\nboundary lies slightly\noutside and reaches\nthe cusp points)", fontsize=7.2, color="#444", va="bottom")
    for side in ("top", "right"): ax.spines[side].set_visible(False)
    ax.set_xlabel("Re b  (trace of e1; trace of e0 fixed at 3)", fontsize=9, color="#333"); ax.set_ylabel("Im b", fontsize=9, color="#333")
    ax.tick_params(labelsize=8, colors="#555")
    ax.set_title("Dual area A* = Σ g·N on a slice of quasi-Fuchsian space (punctured torus)", fontsize=10.5, color="#111", loc="left")
    cb = fig.colorbar(im_, ax=ax, shrink=0.8, pad=0.02); cb.set_label("Re A*, dual area (gray: outside the Bowditch set; b -> -b is a mirror copy)", fontsize=8.5, color="#333"); cb.ax.tick_params(labelsize=7.5, colors="#555")
    import os; os.makedirs("docs/figures", exist_ok=True); fig.tight_layout(); fig.savefig("docs/figures/qf_slice.png"); print("saved docs/figures/qf_slice.png")

