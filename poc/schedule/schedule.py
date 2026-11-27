"""Exact fixed-timestep scheduling from Christoffel words.

Display at F Hz (vsync counter s), simulation at T Hz. Ticks completed by vsync s: n(s) = floor(s T / F). Ticks in the
frame from vsync s0 to s1: n(s1) - n(s0). The per-frame counts form the Christoffel/Sturmian word of slope T/F, so any
window of frames contains floor or ceil of (window x T/F) ticks (balance). Interpolation factor between the last two
states: alpha = (s T mod F) / F, exact. Everything depends only on the integer vsync counter, so it cannot drift, does
not depend on timing noise, and any frame can be evaluated directly (replay seek, rollback).
"""
from fractions import Fraction
from math import gcd, floor

class TickSchedule:
    def __init__(self, tick_hz, display_hz):
        g = gcd(tick_hz, display_hz); self.T, self.F = tick_hz // g, display_hz // g    # reduced ratio p/q = T/F
    def ticks_by(self, s):                  # ticks completed by vsync s
        return (s * self.T) // self.F
    def ticks_in_frame(self, s0, s1):       # ticks to run when presenting at vsync s1 after vsync s0 (handles drops)
        return self.ticks_by(s1) - self.ticks_by(s0)
    def alpha(self, s):                     # interpolation factor in [0, 1): exact numerator over F
        return (s * self.T) % self.F, self.F
    def period(self):                       # pattern repeats every F (reduced) vsyncs, with T ticks per period
        return self.F, self.T
    def ticks_in_range(self, s0, s1):       # O(1) range query
        return self.ticks_by(s1) - self.ticks_by(s0)

def continued_fraction(num, den, nmax=40):
    out = []
    while den and len(out) < nmax: a = num // den; out.append(a); num, den = den, num - a * den
    return out

def convergents(cf):
    h0, h1, k0, k1 = 0, 1, 1, 0; res = []
    for a in cf: h0, h1 = h1, a * h1 + h0; k0, k1 = k1, a * k1 + k0; res.append((h1, k1))
    return res

def amortize(n_objects, m_frames, frame):
    """Christoffel spreading: objects updated in frame f are the contiguous round-robin range
    [floor(f N / M), floor((f+1) N / M)) mod N. Load per frame is floor or ceil of N/M; every object is updated once per
    M frames, at evenly spaced frames."""
    a = (frame * n_objects) // m_frames; b = ((frame + 1) * n_objects) // m_frames
    return [i % n_objects for i in range(a, b)]
