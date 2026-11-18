"""Synthetic VR tracking: head and both hands, positions in metres at 90 Hz, one style per player.

A player's style is drawn from a population (sample_style); a session is drawn from a style (session). The
motion is built from events with minimum-jerk profiles, as people's reaches and head turns roughly are:

- body: walking drift, an Ornstein-Uhlenbeck velocity in the floor plane, and a slow sway of the head;
- head: turns in yaw between targets at Poisson times (look-around rate and range per player), the head
  position carried on a short neck so a turn also moves it;
- hands: rest pose in the body frame, reaches at Poisson times to targets around a player-specific mean
  (direction, distance, speed, handedness), held and brought back, and intermittent small gestures at a
  player's own frequency;
- tracking noise per player.

Everything a player does is drawn again per session from their style, so a fresh session is new motion of
the same person, not a replay.
"""
from __future__ import annotations
import numpy as np

HZ = 90


def mj(t):  # minimum-jerk position profile on [0, 1]
    t = np.clip(t, 0, 1); return 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5


def sample_style(rng):
    hand = rng.uniform(0.3, 0.9)   # share of reaches made by the right hand
    return dict(
        height=rng.uniform(1.5, 1.85), sway_f=rng.uniform(0.15, 0.7), sway_a=rng.uniform(0.003, 0.025),
        walk_sd=rng.uniform(0.02, 0.25), walk_theta=rng.uniform(0.3, 1.5),
        turn_rate=rng.uniform(0.15, 1.2), turn_range=rng.uniform(0.2, 1.2), turn_dur=rng.uniform(0.18, 0.5),
        reach_rate=rng.uniform(0.2, 1.2), right_share=hand,
        reach_mean=[np.array([rng.uniform(0.2, 0.5), rng.uniform(-0.2, 0.2), rng.uniform(-0.1, 0.35)]) for _ in range(2)],   # forward, outward, up
        reach_sd=rng.uniform(0.04, 0.15), reach_dur=rng.uniform(0.3, 0.9), hold=rng.uniform(0.1, 1.0),
        gest_f=rng.uniform(1.0, 3.5), gest_a=rng.uniform(0.0, 0.03), gest_share=rng.uniform(0.0, 0.5),
        noise=rng.uniform(0.0005, 0.002))


def _events(rng, T, rate, make):
    """Sequential events: a gap drawn at `rate`, then an event of the length `make` returns, and so on."""
    out = []; t = rng.exponential(1 / rate)
    while t < T:
        e = make(); out.append((t, e)); t += e["len"] + rng.exponential(1 / rate)
    return out


def session(style, seconds, seed):
    rng = np.random.default_rng(seed); s = style; n = int(seconds * HZ); t = np.arange(n) / HZ
    # body drift (floor plane) and sway
    v = np.zeros((n, 2)); p = np.zeros((n, 2)); dt = 1 / HZ
    for i in range(1, n):
        v[i] = v[i - 1] - s["walk_theta"] * v[i - 1] * dt + s["walk_sd"] * np.sqrt(2 * s["walk_theta"] * dt) * rng.normal(size=2)
        p[i] = p[i - 1] + v[i] * dt
    ph = rng.uniform(0, 2 * np.pi, 3)
    sway = s["sway_a"] * np.stack([np.sin(2 * np.pi * s["sway_f"] * t + ph[0]), 0.5 * np.sin(2 * np.pi * s["sway_f"] * 0.7 * t + ph[1]), 0.3 * np.sin(2 * np.pi * s["sway_f"] * 1.3 * t + ph[2])], 1)
    # head yaw: min-jerk turns between targets
    yaw = np.zeros(n); cur = 0.0
    for t0, e in _events(rng, seconds, s["turn_rate"], lambda: dict(len=s["turn_dur"] * rng.uniform(0.7, 1.4), to=np.clip(rng.normal(0, s["turn_range"]), -2.5, 2.5))):
        i0 = int(t0 * HZ); i1 = min(n, i0 + max(2, int(e["len"] * HZ)))
        yaw[i0:i1] = cur + (e["to"] - cur) * mj((np.arange(i0, i1) - i0) / max(1, i1 - i0 - 1)); yaw[i1:] = e["to"]; cur = e["to"]
    byaw = np.convolve(np.pad(yaw, (45, 45), mode="edge"), np.ones(91) / 91, mode="valid")[:n]   # the body follows the head slowly
    neck = 0.09
    head = np.stack([p[:, 0] + neck * np.cos(yaw), p[:, 1] + neck * np.sin(yaw), np.full(n, s["height"])], 1) + sway
    # hands in the body frame (x forward, y left, z up), then rotated by the body's yaw
    rest = [np.array([0.1, 0.22, -0.55]), np.array([0.1, -0.22, -0.55])]
    hands = []
    for h in (0, 1):   # 0 left, 1 right
        off = np.tile(rest[h], (n, 1)); rate = s["reach_rate"] * (s["right_share"] if h else 1 - s["right_share"]) + 1e-3
        for t0, e in _events(rng, seconds, rate, lambda: dict(len=2 * s["reach_dur"] + s["hold"] * rng.uniform(0.5, 1.5), tgt=s["reach_mean"][h] + rng.normal(0, s["reach_sd"], 3))):
            i0 = int(t0 * HZ); d = max(2, int(s["reach_dur"] * HZ)); L = int(e["len"] * HZ)
            side = 1 if h == 0 else -1   # outward is +y for the left hand, -y for the right
            tgt = np.array([0.1 + e["tgt"][0], rest[h][1] + side * e["tgt"][1], -0.3 + e["tgt"][2]])
            for i in range(i0, min(n, i0 + L)):
                k = i - i0; w = mj(k / d) if k < d else (1.0 if k < L - d else mj((L - k) / d))
                off[i] = rest[h] + w * (tgt - rest[h])
        if s["gest_a"] > 0:
            on = (np.convolve((rng.random(n) < s["gest_share"] / HZ * 2).astype(float), np.ones(HZ), mode="same") > 0)
            g = s["gest_a"] * np.stack([np.sin(2 * np.pi * s["gest_f"] * t), np.cos(2 * np.pi * s["gest_f"] * t), 0.5 * np.sin(4 * np.pi * s["gest_f"] * t)], 1)
            off = off + g * on[:, None]
        c, sn = np.cos(byaw), np.sin(byaw)
        world = np.stack([p[:, 0] + c * off[:, 0] - sn * off[:, 1], p[:, 1] + sn * off[:, 0] + c * off[:, 1], s["height"] + off[:, 2]], 1)
        hands.append(world)
    X = np.concatenate([head, hands[0], hands[1]], 1)
    return X + rng.normal(0, s["noise"], X.shape)


# windows: K past frames relative to the current one -> displacement H frames ahead, in centimetres
K, H = 24, 9   # 267 ms of history, 100 ms ahead


def windows(X, stride=2):
    idx = np.arange(K - 1, len(X) - H, stride)
    past = np.stack([X[i - K + 1:i + 1] - X[i] for i in idx])      # (n, K, 9), current frame at zero
    fut = np.stack([X[i + H] - X[i] for i in idx])
    return (100 * past.reshape(len(idx), -1)).astype(np.float32), (100 * fut).astype(np.float32)


def const_velocity(xp):
    """Dead reckoning: the last frame's velocity carried H frames ahead (xp in the windows' layout)."""
    last = xp.reshape(len(xp), K, 9); return (last[:, -1] - last[:, -2]) * H
