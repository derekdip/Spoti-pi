"""Wind: can a sparse set of travelling gust tokens replace a turbulent wind field?

Teacher: a frozen 2-D turbulent velocity field with a von Karman-like
spectrum, advected downwind at U (Taylor's hypothesis), driving each stalk
as a damped oscillator. This is synthetic; it stands in for field video
until real footage is available.

Two cheap representations of the same frozen field, each with K terms:
  * Fourier: the K highest-energy plane-wave modes (global: every vertex
    evaluates all K).
  * Gusts:   K travelling Gaussian blobs found by greedy matching pursuit
             (local: a vertex evaluates only the blobs whose footprint covers it).

Both are scored on the wind field and on the stalk bend they produce through
the same oscillator, so the comparison isolates the representation.

Usage: python poc/wind_experiment.py [--out poc/results]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reactive.metrics import rel_rmse  # noqa: E402

LX, LY, DX = 128.0, 32.0, 0.25  # domain (m) and grid spacing
L_OUTER = 8.0  # outer scale of turbulence (m)
U_MEAN = 4.0  # mean wind (m/s), along +x
SIGMA_U = 1.2  # turbulence intensity (m/s)
FIELD = 32.0  # stalk field is [0, FIELD)^2
N_SIDE = 64  # stalks per side (0.5 m spacing)
F0, ZETA, ALPHA = 1.0, 0.15, 5.0  # stalk natural frequency (Hz), damping ratio, drag gain
T_TOTAL, FPS, SUBSTEPS = 20.0, 60.0, 4
SCALES = (1.0, 2.0, 4.0, 8.0)  # candidate gust radii (m)


def frozen_turbulence(rng: np.random.Generator) -> np.ndarray:
    nx, ny = int(LX / DX), int(LY / DX)
    kx = 2 * np.pi * np.fft.fftfreq(nx, DX)
    ky = 2 * np.pi * np.fft.fftfreq(ny, DX)
    k = np.sqrt(kx[:, None] ** 2 + ky[None, :] ** 2)
    amp = (1.0 + (k * L_OUTER) ** 2) ** (-2.0 / 3.0)  # ~k^-8/3 PSD per mode -> k^-5/3 energy spectrum in 2-D
    amp[0, 0] = 0.0
    out = []
    for _ in range(2):
        spec = amp * (rng.standard_normal((nx, ny)) + 1j * rng.standard_normal((nx, ny)))
        f = np.fft.ifft2(spec).real
        out.append(f / f.std() * SIGMA_U)
    return np.stack(out, axis=-1)  # (nx, ny, 2)


def sample_field(field: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Periodic bilinear sample of (nx, ny, C) at world coords x, y (arrays of same shape)."""
    nx, ny = field.shape[:2]
    u, v = x / DX, y / DX
    i0, j0 = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = (u - i0)[..., None], (v - j0)[..., None]
    i0 %= nx
    j0 %= ny
    i1, j1 = (i0 + 1) % nx, (j0 + 1) % ny
    return (field[i0, j0] * (1 - fu) * (1 - fv) + field[i1, j0] * fu * (1 - fv)
            + field[i0, j1] * (1 - fu) * fv + field[i1, j1] * fu * fv)


def stalk_bend(field: np.ndarray, pos: np.ndarray) -> np.ndarray:
    """Integrate damped oscillators driven by the advected field. Returns (F, N, 2)."""
    k = (2 * np.pi * F0) ** 2
    c = 2 * ZETA * np.sqrt(k)
    dt = 1.0 / (FPS * SUBSTEPS)
    n_frames = int(T_TOTAL * FPS) + 1
    b = np.zeros_like(pos)
    v = np.zeros_like(pos)
    out = np.zeros((n_frames, pos.shape[0], 2))
    t = 0.0
    for f in range(n_frames):
        out[f] = b
        for _ in range(SUBSTEPS):
            w = sample_field(field, pos[:, 0] - U_MEAN * t, pos[:, 1])
            v += dt * (ALPHA * w - k * b - c * v)
            b += dt * v
            t += dt
    return out


def bend_field(field: np.ndarray) -> np.ndarray:
    """Steady-state stalk bend for a frozen field advected at U, as a frozen field itself.

    A wind mode exp(i kx (x - U t)) has temporal frequency -kx U at a fixed stalk, so the
    oscillator's transfer function H(w) = k / (k - w^2 + i c w) applied at w = -kx U turns the
    wind field into the bend field, with no time integration.
    """
    k = (2 * np.pi * F0) ** 2
    c = 2 * ZETA * np.sqrt(k)
    nx = field.shape[0]
    kx = 2 * np.pi * np.fft.fftfreq(nx, DX)
    w = -kx * U_MEAN
    H = k / (k - w ** 2 + 1j * c * w)
    spec = np.fft.fft(field, axis=0)
    return ALPHA / k * np.fft.ifft(spec * H[:, None, None], axis=0).real


def advect_sample(field: np.ndarray, pos: np.ndarray, times: np.ndarray) -> np.ndarray:
    """Sample a frozen field at the stalks as it advects: (F, N, C)."""
    return np.stack([sample_field(field, pos[:, 0] - U_MEAN * t, pos[:, 1]) for t in times])


def top_k_fourier(field: np.ndarray, k_terms: int) -> np.ndarray:
    spec = np.fft.fft2(field, axes=(0, 1))
    energy = (np.abs(spec) ** 2).sum(-1)
    nx, ny = energy.shape
    # count each conjugate pair once: keep modes with (i, j) <= its conjugate index
    ii, jj = np.meshgrid(np.arange(nx), np.arange(ny), indexing="ij")
    ci, cj = (-ii) % nx, (-jj) % ny
    canonical = (ii < ci) | ((ii == ci) & (jj <= cj))
    order = np.argsort(np.where(canonical, energy, -1.0).ravel())[::-1][:k_terms]
    mask = np.zeros(nx * ny, dtype=bool)
    mask[order] = True
    mask = mask.reshape(nx, ny)
    mask |= mask[ci, cj]  # include conjugates so the result is real
    return np.fft.ifft2(spec * mask[..., None], axes=(0, 1)).real


def _periodic_offsets(x0: float, y0: float):
    nx, ny = int(LX / DX), int(LY / DX)
    xs = (np.arange(nx) * DX)[:, None]
    ys = (np.arange(ny) * DX)[None, :]
    dxx = xs - x0
    dxx = (dxx + LX / 2) % LX - LX / 2
    dyy = ys - y0
    dyy = (dyy + LY / 2) % LY - LY / 2
    return dxx, dyy


def _atoms(wave: bool) -> list[dict]:
    """Dictionary: isotropic Gaussian gusts, plus (optionally) travelling wave packets.

    A wave packet is an across-wind-elongated Gaussian envelope carrying cos/sin at the
    resonant wavelength U / f0: the stripes a resonant canopy shows under a passing gust.
    """
    atoms = [{"kind": "gust", "sx": s, "sy": s, "k0": 0.0} for s in SCALES]
    if wave:
        k0 = 2 * np.pi * F0 / U_MEAN
        atoms += [{"kind": "wave", "sx": sx, "sy": sy, "k0": k0} for sx, sy in ((1.0, 2.0), (2.0, 4.0), (2.0, 8.0), (4.0, 8.0))]
    return atoms


def gust_pursuit(field: np.ndarray, k_max: int, wave: bool = False) -> tuple[list[dict], list[np.ndarray]]:
    """Greedy matching pursuit over the atom dictionary.

    Returns the token list and the reconstruction after each step. Wave atoms come as a
    cos/sin quadrature pair fitted together (treated as orthogonal, which holds well once
    sx * k0 > ~2), so one wave token carries an amplitude and a phase.
    """
    dxx0, dyy0 = _periodic_offsets(0.0, 0.0)
    kernels = []
    for a in _atoms(wave):
        env = np.exp(-(dxx0 ** 2 / (2 * a["sx"] ** 2) + dyy0 ** 2 / (2 * a["sy"] ** 2)))
        parts = [env] if a["kind"] == "gust" else [env * np.cos(a["k0"] * dxx0), env * np.sin(a["k0"] * dxx0)]
        kernels.append((a, [(np.fft.fft2(g), float((g * g).sum())) for g in parts]))
    residual = field.copy()
    tokens, recons = [], []
    recon = np.zeros_like(field)
    for _ in range(k_max):
        best = None
        r_hat = np.fft.fft2(residual, axes=(0, 1))
        for a, parts in kernels:
            projs = [np.fft.ifft2(r_hat * np.conj(g_hat)[..., None], axes=(0, 1)).real for g_hat, _ in parts]  # correlation
            gain = sum((pr ** 2).sum(-1) / gg for pr, (_, gg) in zip(projs, parts))
            idx = np.unravel_index(np.argmax(gain), gain.shape)
            if best is None or gain[idx] > best[0]:
                best = (gain[idx], a, idx, [pr[idx] / gg for pr, (_, gg) in zip(projs, parts)])
        _, a, (i, j), amps = best
        dxx, dyy = _periodic_offsets(i * DX, j * DX)
        env = np.exp(-(dxx ** 2 / (2 * a["sx"] ** 2) + dyy ** 2 / (2 * a["sy"] ** 2)))
        parts = [env] if a["kind"] == "gust" else [env * np.cos(a["k0"] * dxx), env * np.sin(a["k0"] * dxx)]
        blob = sum(g[..., None] * amp[None, None, :] for g, amp in zip(parts, amps))
        residual -= blob
        recon = recon + blob
        tokens.append({"kind": a["kind"], "x": i * DX, "y": j * DX, "sx": a["sx"], "sy": a["sy"], "k0": a["k0"],
                       "amp": [amp.tolist() for amp in amps]})
        recons.append(recon.copy())
    return tokens, recons


def per_vertex_count(tokens: list[dict], radius_sigmas: float = 3.0) -> float:
    """Mean number of tokens whose footprint (3 sigma ellipse) covers a point of the domain."""
    count = np.zeros((int(LX / DX), int(LY / DX)))
    for t in tokens:
        dxx, dyy = _periodic_offsets(t["x"], t["y"])
        count += (dxx ** 2 / t["sx"] ** 2 + dyy ** 2 / t["sy"] ** 2) < radius_sigmas ** 2
    return float(count.mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "results"))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    field = frozen_turbulence(rng)
    xs = (np.arange(N_SIDE) + 0.5) * (FIELD / N_SIDE)
    gx, gy = np.meshgrid(xs, xs, indexing="xy")
    pos = np.stack([gx.ravel(), gy.ravel()], axis=-1)
    print(f"teacher: frozen turbulence {field.shape[0]}x{field.shape[1]} at {DX} m, U={U_MEAN} m/s, "
          f"sigma_u={SIGMA_U} m/s, {pos.shape[0]} stalks at f0={F0} Hz")
    bend_ref = stalk_bend(field, pos)
    print(f"  teacher bend rms {np.sqrt((bend_ref ** 2).mean()):.3f} m, peak {np.linalg.norm(bend_ref, axis=-1).max():.3f} m")

    # steady-state check: the frozen bend field must reproduce the integrated teacher once the
    # start-up transient has died (t >= 3 s)
    times = np.arange(bend_ref.shape[0]) / FPS
    steady = times >= 3.0
    bf = bend_field(field)
    check = rel_rmse(advect_sample(bf, pos, times[steady]), bend_ref[steady])
    print(f"  frozen bend field vs integrated teacher (t >= 3 s): {check:.3f} relative error")

    ks = (4, 8, 16, 32, 64, 128)
    tokens, recons = gust_pursuit(field, max(ks))
    tokens_b, recons_b = gust_pursuit(bf, max(ks))
    tokens_w, recons_w = gust_pursuit(bf, max(ks), wave=True)
    rows = []
    for k in ks:
        fk = top_k_fourier(field, k)
        gk = recons[k - 1]
        fbk = top_k_fourier(bf, k)
        gbk = recons_b[k - 1]
        row = {"K": k,
               "fourier_wind": rel_rmse(fk, field), "gust_wind": rel_rmse(gk, field),
               "fourier_bend": rel_rmse(stalk_bend(fk, pos)[steady], bend_ref[steady]),
               "gust_bend": rel_rmse(stalk_bend(gk, pos)[steady], bend_ref[steady]),
               "fourier_bendspace": rel_rmse(advect_sample(fbk, pos, times[steady]), bend_ref[steady]),
               "gust_bendspace": rel_rmse(advect_sample(gbk, pos, times[steady]), bend_ref[steady]),
               "wave_bendspace": rel_rmse(advect_sample(recons_w[k - 1], pos, times[steady]), bend_ref[steady]),
               "fourier_per_vertex": float(k), "gust_per_vertex": per_vertex_count(tokens[:k]),
               "gust_bendspace_per_vertex": per_vertex_count(tokens_b[:k]),
               "wave_bendspace_per_vertex": per_vertex_count(tokens_w[:k]),
               "wave_fraction": sum(1 for t in tokens_w[:k] if t["kind"] == "wave") / k}
        rows.append(row)
        print(f"K={k:4d}  wind: fourier {row['fourier_wind']:.3f} gust {row['gust_wind']:.3f}   "
              f"bend (fit to wind): fourier {row['fourier_bend']:.3f} gust {row['gust_bend']:.3f}   "
              f"bend (fit to bend): fourier {row['fourier_bendspace']:.3f} gust {row['gust_bendspace']:.3f} "
              f"wave {row['wave_bendspace']:.3f} ({100 * row['wave_fraction']:.0f}% wave atoms)   "
              f"evals/vertex: fourier {k} gust {row['gust_per_vertex']:.1f} / {row['gust_bendspace_per_vertex']:.1f} wave {row['wave_bendspace_per_vertex']:.1f}")
    scales = {s: sum(1 for t in tokens if t["sx"] == s) for s in SCALES}
    scales_b = {s: sum(1 for t in tokens_b if t["sx"] == s) for s in SCALES}
    report = {"rows": rows, "gust_scale_histogram_128": scales, "gust_bendspace_scale_histogram_128": scales_b,
              "steady_state_check": check,
              "setup": {"LX": LX, "LY": LY, "DX": DX, "L_outer": L_OUTER, "U": U_MEAN, "sigma_u": SIGMA_U,
                        "stalks": int(pos.shape[0]), "f0": F0, "zeta": ZETA}}
    (out / "wind.json").write_text(json.dumps(report, indent=2))
    lines = ["# Wind: gust tokens versus Fourier modes", "",
             f"Synthetic frozen turbulence ({LX:.0f} m x {LY:.0f} m at {DX} m, outer scale {L_OUTER} m, "
             f"U = {U_MEAN} m/s, sigma_u = {SIGMA_U} m/s) advected over {pos.shape[0]} stalks at {F0} Hz, zeta {ZETA}.",
             "Errors are relative RMS. 'wind' scores the wind field itself; 'bend' scores the stalk bend on frames after the",
             "start-up transient (t >= 3 s). 'fit to wind' representations were chosen to match the wind field; 'fit to bend'",
             "representations were chosen to match the steady-state bend field (the wind field passed through the stalk's",
             f"transfer function, which reproduces the integrated teacher to {check:.3f}).",
             "Evals per vertex: terms a vertex must evaluate. Fourier modes are global; a gust only touches vertices within 3 sigma.", "",
             "Wave packets: the dictionary also holds across-wind-elongated envelopes carrying cos/sin at the resonant",
             f"wavelength U/f0 = {U_MEAN / F0:.1f} m (a travelling wave packet); the pursuit picks gusts or packets freely.", "",
             "| K | wind: Fourier | wind: gusts | bend, fit to wind: Fourier | bend, fit to wind: gusts | bend, fit to bend: Fourier | bend, fit to bend: gusts | bend, fit to bend: gusts + wave packets | evals/vertex: Fourier | evals/vertex: gusts | evals/vertex: packets |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['K']} | {r['fourier_wind']:.3f} | {r['gust_wind']:.3f} | {r['fourier_bend']:.3f} | {r['gust_bend']:.3f} | "
                     f"{r['fourier_bendspace']:.3f} | {r['gust_bendspace']:.3f} | {r['wave_bendspace']:.3f} ({100 * r['wave_fraction']:.0f}% packets) | "
                     f"{r['K']} | {r['gust_bendspace_per_vertex']:.1f} | {r['wave_bendspace_per_vertex']:.1f} |")
    lines += ["", "Gust radii chosen by the pursuit (first 128 tokens), fit to wind: " + ", ".join(f"{s} m: {n}" for s, n in scales.items()),
              "", "Fit to bend: " + ", ".join(f"{s} m: {n}" for s, n in scales_b.items()), ""]
    (out / "wind.md").write_text("\n".join(lines) + "\n")
    try:
        make_figure(field, bf, recons_b[31], recons_w[31], out / "wind.png")
    except Exception as exc:
        print(f"(figure skipped: {exc})")
    print(f"wrote {out}")


def make_figure(field, f16, g16, g64, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    panels = [("frozen turbulence u' (wind teacher)", field), ("steady-state bend field (what stalks show)", f16),
              ("32 gust tokens fit to bend", g16), ("32 tokens from gusts + travelling wave packets", g64)]
    fig, axes = plt.subplots(len(panels), 1, figsize=(12, 9))
    for ax, (name, f) in zip(axes, panels):
        vmax = np.abs(f[..., 0]).max() if name.startswith("frozen") else np.abs(panels[1][1][..., 0]).max()
        ax.imshow(f[..., 0].T, origin="lower", extent=(0, LX, 0, LY), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_title(name)
        ax.set_yticks([])
    axes[-1].set_xlabel("x (m); the pattern advects at U = 4 m/s over the 32 m stalk field")
    fig.tight_layout()
    fig.savefig(path, dpi=100)


if __name__ == "__main__":
    main()
