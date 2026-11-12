"""RGRE-1b fresh benchmark: 30 cases, none of them run before the freeze.

Composition per docs/math-track-rgre1b-prereg.md: 10 isolated tangent defects, 6 isolated
support/localisation defects, 8 mixtures (four of them fresh versions of the regimes where
RGRE-1's coherence penalty flipped a correct raw diagnosis), 6 out-of-vocabulary cases.
Corn trajectories come from a fresh seed; water teachers use fresh parameters except one
declared replication anchor.
"""
from __future__ import annotations

import numpy as np

from w1_experiment import CENTRE

from . import corn, water

SEED = 20260916


def build(model0, theta0, grid, floor_full, seed=SEED, log=print):
    rng = np.random.default_rng(seed)
    base = water.mk_state(theta0)
    iso, mix, unk, gap = [], [], [], []

    # ---------------- isolated tangent defects (10) ----------------
    # corn tail: two reduced persistence (RGRE-1's flipped regime) and one increased
    for k, lo_hi in enumerate(((0.3, 0.6), (0.3, 0.6), (1.6, 3.0))):
        m = float(rng.uniform(*lo_hi))
        iso.append(corn.CornCase(f"corn_tail_{k}", corn.gentle_path(rng, f"ct{k}"), model0, ("tail",),
                                 corn.State(lam_mult=m)))
    for k in range(2):
        tau = float(rng.uniform(0.05, 0.15)) * (1 if rng.random() < 0.5 else -1)
        iso.append(corn.CornCase(f"corn_coordinate_{k}", corn.gentle_path(rng, f"cc{k}"), model0, ("coordinate",),
                                 corn.State(tau0=tau)))
    m = float(rng.uniform(0.5, 0.75))
    iso.append(corn.CornCase("corn_unary_0", corn.gentle_path(rng, "cu0"), model0, ("unary",), corn.State(w_mult=m)))
    log(f"  corn isolated tangent built ({len(iso)})")
    for k, df in enumerate((2, 5)):  # 2 fresh; 5 is the declared replication anchor from RGRE-1
        eta, _ = water.eta_linear_single(1.0, delay_frames=df)
        iso.append(water.WaterCase(f"water_coordinate_{k}", ("coordinate",), eta, [CENTRE], grid, base, theta0, floor_full))
        log(f"  water_coordinate_{k} (delay {df})")
    eta, _ = water.eta_linear_single(1.0, sigma=0.022)
    iso.append(water.WaterCase("water_unary_0", ("unary",), eta, [CENTRE], grid, base, theta0, floor_full))
    eta, _ = water.eta_linear_single(1.0, gamma0=0.6)
    iso.append(water.WaterCase("water_tail_0", ("tail",), eta, [CENTRE], grid, base, theta0, floor_full))
    log(f"  isolated tangent done ({len(iso)})")

    # ---------------- isolated support / localisation defects (6) ----------------
    for k in range(2):
        iso.append(corn.CornCase(f"corn_stop_{k}", corn.stop_path(rng, f"cs{k}"), model0, ("stop",),
                                 corn.State(interior_events=False, edge_events=False)))
    for k in range(2):
        iso.append(corn.CornCase(f"corn_corner_{k}", corn.corner_path(rng, f"ck{k}"), model0, ("corner",), corn.State()))
    for k, (A, D) in enumerate(((5.5, 0.234375), (7.0, 0.328125))):
        single, _ = water.eta_nonlinear_single(A)
        dt, gain = water.fit_single(theta0, single, grid, A, with_shift=True)
        eta, _ = water.eta_nonlinear_pair(A, D)
        cen = [(CENTRE[0] - D / 2, CENTRE[1]), (CENTRE[0] + D / 2, CENTRE[1])]
        iso.append(water.WaterCase(f"water_interaction_{k}", ("interaction",), eta, cen, grid,
                                   water.mk_state(theta0, gain=gain, dt=dt), theta0, floor_full))
        log(f"  water_interaction_{k} A={A} D={D:.4f} (single fit gain {gain:.2f} dt {dt*1e3:+.0f} ms)")
    log(f"  isolated done ({len(iso)})")

    # ---------------- mixtures (8) ----------------
    # flipped regime 1: water pair with a gain-only single fit, so the onset shift is also missing
    for k, (A, D) in enumerate(((6.5, 0.234375), (7.5, 0.28125))):
        single, _ = water.eta_nonlinear_single(A)
        _, gain = water.fit_single(theta0, single, grid, A, with_shift=False)
        eta, _ = water.eta_nonlinear_pair(A, D)
        cen = [(CENTRE[0] - D / 2, CENTRE[1]), (CENTRE[0] + D / 2, CENTRE[1])]
        mix.append(water.WaterCase(f"mix_interaction_coordinate_{k}", ("interaction", "coordinate"), eta, cen, grid,
                                   water.mk_state(theta0, gain=gain), theta0, floor_full))
        log(f"  mix_interaction_coordinate_{k} A={A} D={D:.4f}")
    # flipped regime 2: corn stop with a wrong kernel width
    for k in range(2):
        m = float(rng.uniform(0.5, 0.7))
        mix.append(corn.CornCase(f"mix_unary_stop_{k}", corn.stop_path(rng, f"mus{k}"), model0, ("unary", "stop"),
                                 corn.State(interior_events=False, edge_events=False, w_mult=m)))
    tau = float(rng.uniform(0.06, 0.14)) * (1 if rng.random() < 0.5 else -1)
    mix.append(corn.CornCase("mix_coordinate_corner_0", corn.corner_path(rng, "mcc0"), model0, ("coordinate", "corner"),
                             corn.State(tau0=tau)))
    mix.append(corn.CornCase("mix_tail_smooth_0", corn.smooth_path(rng, "mts0"), model0, ("tail", "smooth"),
                             corn.State(lam_mult=float(rng.uniform(1.8, 2.8)))))
    mix.append(corn.CornCase("mix_corner_stop_0", corn.corner_path(rng, "mks0", with_stop=True), model0, ("corner", "stop"),
                             corn.State(interior_events=False, edge_events=False)))
    A = 4.5
    eta, _ = water.eta_nonlinear_single(A)
    mix.append(water.WaterCase("mix_coordinate_unary_0", ("coordinate", "unary"), eta, [CENTRE], grid,
                               water.mk_state(theta0, gain=A), theta0, floor_full))
    log(f"  mixtures done ({len(mix)})")

    # ---------------- out of vocabulary (6) ----------------
    for k in range(2):
        unk.append(corn.CornCase(f"unknown_wind_{k}", corn.gentle_path(rng, f"uw{k}"), model0, ("unknown",),
                                 corn.State(), extra_field=corn.gust_field(rng)))
    wh = corn.gentle_path(rng, "uh0")
    unk.append(corn.CornCase("unknown_hidden_walker_0", wh, model0, ("unknown",), corn.State(),
                             hidden=corn.hidden_walker(rng, wh)))
    for k, off in enumerate(((1.1, 0.6), (-0.9, -1.2))):
        eta, _ = water.eta_hidden(0.6, off)
        unk.append(water.WaterCase(f"unknown_hidden_splash_{k}", ("unknown",), eta, [CENTRE], grid, base, theta0, floor_full))
    log(f"  unknown done ({len(unk)})")

    # ---------------- reported, unscored: a vocabulary gap ----------------
    # The vocabulary has a time coordinate and no space coordinate, so a mislocated cause is outside
    # it. The pre-freeze oracle check showed this is not a clean out-of-vocabulary case: a gain repair
    # removes about a fifth of the error by turning the wrong-placed token down, above the 10 percent
    # construct-validity limit. It is kept as one reported case and excluded from every bar.
    eta, _ = water.eta_linear_single(1.0, centre=(CENTRE[0] + 0.6, CENTRE[1] + 0.4))
    gap.append(water.WaterCase("gap_offcentre_0", ("space_coordinate",), eta, [CENTRE], grid, base, theta0, floor_full))
    log("  gap case done (1, unscored)")
    return iso, mix, unk, gap
