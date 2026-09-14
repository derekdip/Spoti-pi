import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reactive.causes import bank_path, emit_stride_events, s_curve_walk  # noqa: E402
from reactive.geometry import build_geometry  # noqa: E402
from reactive.model import CheapModel, make_term  # noqa: E402
from reactive.primitives import LIVE_EPS, RingWave, Wake, spring_response  # noqa: E402
from reactive.teacher import TeacherParams, stalk_grid  # noqa: E402


def _rk4_spring(lam, k, zeta, tau_max=6.0, n=6000):
    """Numerically integrate x'' + c x' + k x = k e^{-lam t} from rest."""
    c = 2 * zeta * np.sqrt(k)
    dt = tau_max / n
    x, v = 0.0, 0.0
    ts, xs = [0.0], [0.0]

    def acc(t, x, v):
        return k * np.exp(-lam * t) - c * v - k * x

    t = 0.0
    for _ in range(n):
        k1x, k1v = v, acc(t, x, v)
        k2x, k2v = v + 0.5 * dt * k1v, acc(t + 0.5 * dt, x + 0.5 * dt * k1x, v + 0.5 * dt * k1v)
        k3x, k3v = v + 0.5 * dt * k2v, acc(t + 0.5 * dt, x + 0.5 * dt * k2x, v + 0.5 * dt * k2v)
        k4x, k4v = v + dt * k3v, acc(t + dt, x + dt * k3x, v + dt * k3v)
        x += dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
        v += dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        t += dt
        ts.append(t)
        xs.append(x)
    return np.array(ts), np.array(xs)


def test_spring_closed_form_matches_numeric_integration():
    for lam, k, zeta in [(2.0, 40.0, 0.3), (0.5, 10.0, 0.1), (8.0, 120.0, 0.7)]:
        ts, xs = _rk4_spring(lam, k, zeta)
        closed = spring_response(ts, lam, k, zeta)
        # both normalised to unit peak
        xs = xs / np.max(np.abs(xs))
        assert np.max(np.abs(closed - xs)) < 2e-3, (lam, k, zeta)


def test_spring_is_causal_and_starts_at_rest():
    tau = np.array([-1.0, -1e-6, 0.0])
    assert np.all(spring_response(tau, 2.0, 40.0, 0.3) == 0.0)


def _small_scene():
    p = TeacherParams(nx=12, ny=12)
    pos = stalk_grid(p)
    path = s_curve_walk()
    return pos, path, emit_stride_events(path), bank_path(path)


def test_ring_wave_is_causal():
    pos, path, ev, tok = _small_scene()
    g = build_geometry(pos, ev, tok, path)
    rw = RingWave()
    prm = {"A": 0.1, "lam": 1.0, "v": 1.0, "w": 0.2, "kappa": 5.0}
    times = np.array([0.5])
    b, _ = rw.evaluate(g, times, prm)
    # only events already emitted can contribute, and only near their fronts
    tau = times[0] - g.ev_t0
    r_front = np.where(tau >= 0, 1.0 * tau, -np.inf)
    far = np.all(g.ev_d > r_front[None, :] + 6 * prm["w"], axis=1)
    assert np.all(np.linalg.norm(b[0][far], axis=-1) < 1e-6)


def test_wake_is_one_sided_in_time():
    pos, path, ev, tok = _small_scene()
    g = build_geometry(pos, ev, tok, path)
    b, _ = Wake().evaluate(g, np.array([0.0]), {"B": 0.3, "w": 0.3, "t_lead": 0.0, "lam": 3.0, "k": 60.0, "zeta": 0.3, "mix": 0.3})
    # at t=0 nobody has been passed yet (t_pass > 0 for all stalks off the start point)
    assert np.all(np.linalg.norm(b[0][g.path_tpass > 0], axis=-1) == 0.0)


def test_dead_tokens_do_not_change_output():
    pos, path, ev, tok = _small_scene()
    g = build_geometry(pos, ev, tok, path)
    t = make_term("radial_impulse")
    t.params.update(lam=5.0)
    times = np.array([9.5])  # long after every event
    b, live = t.prim.evaluate(g, times, t.params)
    assert live == 0.0
    assert np.all(b == 0.0)
    assert LIVE_EPS < 1e-2


def test_model_param_roundtrip():
    m = CheapModel([make_term("wake"), make_term("crush")], {"b_max": 0.6})
    z = m.get_vector()
    before = m.describe()
    m.set_vector(z)
    assert m.describe() == before
