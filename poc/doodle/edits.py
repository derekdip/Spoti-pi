"""Edits of a doodle (docs/doodle-bots.md): the other half of "never repeats".

A variation of a word is a source doodle from the bank with, in turn: one stroke borrowed from another
doodle of the same word (matched by where it sits and how big it is, in the normalised box), a minor
stroke dropped, the strokes after the first reordered, and an affine change of scale, aspect and tilt.
Every step keeps the drawing a drawing of that word because every source was one.
"""
from __future__ import annotations
import numpy as np
from .bank import bbox, stroke_length, BOX


def affine(strokes, scale=1.0, aspect=1.0, rot=0.0, shift=(0.0, 0.0), about=None):
    about = np.array([BOX / 2, BOX / 2]) if about is None else np.asarray(about, float)
    c, s = np.cos(rot), np.sin(rot); R = np.array([[c, -s], [s, c]])
    S = np.diag([scale * aspect, scale / aspect])
    return [((st - about) @ (R @ S).T) + about + np.asarray(shift, float) for st in strokes]


def _descriptor(stroke, lo, size):
    """Where a stroke sits and how big it is, in a doodle's own box: centroid, extent, length, all in [0, 1]."""
    s = (stroke - lo) / size
    return np.concatenate([s.mean(0), s.max(0) - s.min(0), [stroke_length(stroke) / size.max()]])


def recombine(A, B, rng):
    """A with one stroke (not its first) replaced by B's best-matching stroke, mapped into A's box."""
    if len(A) < 2 or len(B) < 1:
        return [s.copy() for s in A]
    loA, hiA = bbox(A); loB, hiB = bbox(B); sA = np.maximum(hiA - loA, 1.0); sB = np.maximum(hiB - loB, 1.0)
    k = int(rng.integers(1, len(A))); dA = _descriptor(A[k], loA, sA)
    dB = [_descriptor(s, loB, sB) for s in B]; j = int(np.argmin([np.linalg.norm(d - dA) for d in dB]))
    mapped = (B[j] - loB) / sB * sA + loA
    out = [s.copy() for s in A]; out[k] = mapped
    return out


def drop_minor(strokes, rng):
    """Drop one stroke that is not the first and not among the longest third."""
    if len(strokes) < 3:
        return strokes
    L = np.array([stroke_length(s) for s in strokes]); thr = np.quantile(L, 0.67)
    cands = [i for i in range(1, len(strokes)) if L[i] < thr]
    if not cands:
        return strokes
    k = cands[int(rng.integers(len(cands)))]
    return [s for i, s in enumerate(strokes) if i != k]


def reorder(strokes, rng):
    """Keep the first stroke first (it is usually the outline) and shuffle a little after it."""
    if len(strokes) < 3:
        return strokes
    idx = np.arange(1, len(strokes))
    for _ in range(2):
        i = int(rng.integers(len(idx) - 1)); idx[i], idx[i + 1] = idx[i + 1], idx[i]
    return [strokes[0]] + [strokes[i] for i in idx]


def variation(sources, rng, p_recombine=0.5, p_drop=0.3, p_reorder=0.5, scale=(0.85, 1.15), aspect=(0.88, 1.12), tilt=0.12):
    """A fresh drawing of the word from the bank's sources, in the 256 box."""
    A = sources[int(rng.integers(len(sources)))]
    if rng.random() < p_recombine and len(sources) > 1:
        A = recombine(A, sources[int(rng.integers(len(sources)))], rng)
    if rng.random() < p_drop:
        A = drop_minor(A, rng)
    if rng.random() < p_reorder:
        A = reorder(A, rng)
    return affine(A, scale=rng.uniform(*scale), aspect=rng.uniform(*aspect), rot=rng.uniform(-tilt, tilt))
