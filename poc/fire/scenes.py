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


SCENES = {"plume": plume, "obstacle": obstacle, "ignition": ignition,
          "delayed_ignition": delayed_ignition, "full": full}
