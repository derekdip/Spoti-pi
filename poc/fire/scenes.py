"""Validated fire scenes: teacher configurations where every consumer has something to read.

Each scene was checked once, before any experiment was designed, for the property that makes it
useful rather than for any particular answer: the plume is stable and narrow, the obstacle deflects
it, and the fuel patches actually ignite and burn out. A patch that never lights leaves the ignition
consumer identically zero, which was true of the first scene tried.
"""
from __future__ import annotations

from .teacher import Burner, FireParams, FuelPatch, Obstacle

BURNER = dict(x=0.45, y=0.10, radius=0.10)


def plume():
    """Bare buoyant flame: visual and heat consumers only."""
    return FireParams(), [Burner(**BURNER)], [], []


def obstacle():
    """The plume strikes a shelf and rolls into a vortex: the interaction case."""
    return FireParams(), [Burner(**BURNER)], [], [Obstacle(x=0.62, y=0.95, half_w=0.22, half_h=0.035)]


def ignition():
    """A gust carries the flame onto a fuel bed, which lights at about 0.4 s and burns out."""
    return (FireParams(gust_amp=1.6), [Burner(**BURNER)],
            [FuelPatch(x=0.78, y=0.30, radius=0.07, amount=1.6)], [])


def delayed_ignition():
    """A stronger gust reaches a further bed only at about 2.0 s: a late, isolated event."""
    return (FireParams(gust_amp=2.4), [Burner(**BURNER)],
            [FuelPatch(x=0.95, y=0.45, radius=0.07, amount=1.6)], [])


def full():
    """Everything at once: gusted plume, a shelf, a near bed and a far bed."""
    return (FireParams(gust_amp=1.6), [Burner(**BURNER)],
            [FuelPatch(x=0.78, y=0.30, radius=0.07, amount=1.6),
             FuelPatch(x=1.10, y=0.55, radius=0.06, amount=1.2)],
            [Obstacle(x=0.62, y=0.95, half_w=0.22, half_h=0.035)])


def windy():
    """A steady crosswind leans the column: the tilt case."""
    return FireParams(wind=0.35), [Burner(**BURNER)], [], []


def twin():
    """Two burners half a metre apart, so the cheap model has to superpose two columns."""
    return (FireParams(), [Burner(x=0.42, y=0.10, radius=0.09),
                           Burner(x=0.95, y=0.10, radius=0.09, t_on=0.5)], [], [])


def shelf_bed():
    """A shelf and a bed beyond it: deflection and a delayed secondary source at once."""
    return (FireParams(gust_amp=1.8), [Burner(**BURNER)],
            [FuelPatch(x=1.02, y=0.38, radius=0.07, amount=1.5)],
            [Obstacle(x=0.58, y=0.80, half_w=0.20, half_h=0.035)])


def shutoff():
    """The burner stops at 1.5 s and the hot gas detaches and keeps rising.

    No token in the vocabulary is a detached buoyant puff: every source is anchored to its cause's
    position. This is the out-of-vocabulary case.
    """
    return FireParams(), [Burner(x=0.45, y=0.10, radius=0.10, t_off=1.5, pilot_for=1.5)], [], []


def split():
    """A wide shelf directly over the burner: the plume splits and goes around both sides.

    Every source in the cheap vocabulary is a single Gaussian column with one centre. Deflection
    can move that centre but cannot make two of it, so a split plume has no representation at all.
    This is the out-of-vocabulary case.
    """
    return (FireParams(), [Burner(**BURNER)], [],
            [Obstacle(x=0.45, y=0.62, half_w=0.30, half_h=0.04)])


def gusty():
    """A gusted plume with nothing else: no bed, no shelf, no shutoff.

    Added for F5 as a pilot scene, declared seen. The gust is the one cause F4 could not follow,
    and every F4 scene that has one also has a bed or a shelf, so none of them can be used to
    diagnose it without spending a scored scene.
    """
    return FireParams(gust_amp=1.6), [Burner(**BURNER)], [], []


def gust_shelf():
    """A gust drives the plume under a shelf set downwind: sway and deflection at once, no bed."""
    return (FireParams(gust_amp=1.8), [Burner(**BURNER)], [],
            [Obstacle(x=0.72, y=0.70, half_w=0.22, half_h=0.035)])


def fast_gust():
    """The same gust at twice the frequency. The frequency is a property of the cause, so a model
    that reads it rather than fitting it should transfer here with nothing refitted."""
    return FireParams(gust_amp=1.6, gust_hz=1.4), [Burner(**BURNER)], [], []


def strong_gust():
    """A much stronger gust: does the sway law hold at an amplitude well outside the fitted range."""
    return FireParams(gust_amp=2.6), [Burner(**BURNER)], [], []


def gust_twin():
    """Two burners in a gust: superposition and sway together."""
    return (FireParams(gust_amp=1.5), [Burner(x=0.42, y=0.10, radius=0.09),
                                       Burner(x=0.92, y=0.10, radius=0.09, t_on=0.4)], [], [])


def bed_chain():
    """Three beds in a line at increasing distance: the delay law has to hold over three events."""
    return (FireParams(gust_amp=2.0), [Burner(**BURNER)],
            [FuelPatch(x=0.70, y=0.24, radius=0.07, amount=1.5),
             FuelPatch(x=0.88, y=0.36, radius=0.07, amount=1.4),
             FuelPatch(x=1.00, y=0.38, radius=0.07, amount=1.4)], [])


SCENES = {"plume": plume, "gusty": gusty, "gust_shelf": gust_shelf, "fast_gust": fast_gust,
          "strong_gust": strong_gust, "gust_twin": gust_twin, "bed_chain": bed_chain, "obstacle": obstacle, "ignition": ignition,
          "delayed_ignition": delayed_ignition, "full": full,
          "windy": windy, "twin": twin, "shelf_bed": shelf_bed, "shutoff": shutoff, "split": split}
