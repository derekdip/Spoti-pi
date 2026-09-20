"""The puff grammar's stated properties: causal, stateless, intensive, bounded in cost."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.fire import puffs, scenes, teacher as TT


def _eval(st, scene, times):
    p, b, q, o = scene
    return puffs.evaluate(st, p, np.asarray(times, float), b, q, o)


def test_nothing_before_the_cause():
    scene = scenes.twin()                      # the second burner switches on at 0.5 s
    b2 = scene[1][1]
    st = puffs.PuffState(base_amp=800.0, jitter=0.05)
    T, _ = _eval(st, scene, [0.3])
    X, Y = TT._grid(scene[0])
    near = ((X - b2.x) ** 2 + (Y - b2.y) ** 2) <= 0.2 ** 2
    assert np.all(T[0][near] <= TT.T_AMBIENT + 1e-6)


def test_detaches_after_switch_off():
    scene = scenes.shutoff()
    st = puffs.PuffState()
    T, _ = _eval(st, scene, [1.4, 2.5])
    b = scene[1][0]
    X, Y = TT._grid(scene[0])
    disc = ((X - b.x) ** 2 + (Y - b.y) ** 2) <= (b.radius * 1.5) ** 2
    assert T[0][disc].max() > TT.T_AMBIENT + 300      # burning: hot at the source
    assert T[1][disc].max() < TT.T_AMBIENT + 50       # a second after shut-off: the source is cold
    assert (T[1] > TT.T_AMBIENT + 50).any()           # but the detached parcels are still hot somewhere


def test_frames_are_independent():
    scene = scenes.windy()
    st = puffs.PuffState(wind=0.3, jitter=0.03)
    a, _ = _eval(st, scene, [0.5, 1.7, 3.1])
    b, _ = _eval(st, scene, [1.7])
    assert np.array_equal(a[1], b[0])


def test_intensive_never_exceeds_the_parcel_temperature():
    scene = scenes.twin()
    st = puffs.PuffState(amp=700.0, rate=10.0, accel=0.5, base_amp=650.0)
    T, _ = _eval(st, scene, [1.0, 2.0, 3.5])
    assert T.max() <= TT.T_AMBIENT + 700.0 + 1e-6


def test_live_count_bounds_the_cost():
    st = puffs.PuffState(rate=10.0, burn=1.5, cool=2.0)
    assert st.live_count() <= puffs.MAX_LIVE
    assert puffs.PuffState().live_count() >= 1


def test_deflection_keeps_parcels_out_of_the_shelf_shadow():
    scene = scenes.split()
    o = scene[3][0]
    on = puffs.PuffState(deflect=1.0, reach=0.6)
    off = puffs.PuffState()
    T_on, _ = _eval(on, scene, [2.5])
    T_off, _ = _eval(off, scene, [2.5])
    X, Y = TT._grid(scene[0])
    above = (Y > o.y + o.half_h + 0.05) & (Y < o.y + 0.5) & (np.abs(X - o.x) < 0.10)
    assert T_off[0][above].max() > T_on[0][above].max()   # undeflected parcels pass straight through


def test_bed_lights_on_its_own_clock_and_burns_out():
    scene = scenes.ignition()
    q = scene[2][0]
    st = puffs.PuffState(bed_amp=600.0, bed_delay=0.4, bed_speed=0.0, bed_dur=1.0, bed_fall=0.3, sharp=3.0)
    T, _ = _eval(st, scene, [0.2, 1.0, 3.5])
    X, Y = TT._grid(scene[0])
    near = ((X - q.x) ** 2 + (Y - q.y) ** 2) <= (q.radius + 0.05) ** 2
    assert T[0][near].max() < TT.T_AMBIENT + 100     # not lit yet
    assert T[1][near].max() > TT.T_AMBIENT + 300     # alight
    assert T[2][near].max() < T[1][near].max() - 100  # dying after the fuel runs out
    rec = puffs.as_record(st, scene[0], np.array([0.2, 1.0, 3.5]), *scene[1:])
    assert rec.fuel[0][near].max() > rec.fuel[2][near].max()   # the bed depletes its fuel
