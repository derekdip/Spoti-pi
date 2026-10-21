"""The doodle bank: real human doodles as the teacher for a drawing bot (docs/doodle-bots.md).

Source: the Quick, Draw! dataset (Google, CC BY 4.0), the "simplified" stroke format: each doodle is a
list of strokes, each stroke a polyline, drawn in about twenty seconds by a person asked for one word,
aligned to the top-left and scaled to a 256 box, with a flag for whether the game's classifier
recognised it. poc/results/doodle_bank/<word>.ndjson holds the first 4000 records of six words.

In this project's terms (docs/ecs-theory-snapshot.md, docs/gait3d-runtime.md): a drawing is a clip, the
bank is the teacher's own motion, and variation comes from edits of the clip and from the hand that
executes it, not from a fitted grammar.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "poc/results/doodle_bank"
WORDS = ("house", "cat", "bicycle", "tree", "sun", "fish")
BOX = 256.0


def load_word(word, n=None, recognized_only=True, skip=0):
    """Doodles of a word: a list of drawings, each a list of (K, 2) float arrays in the 256 box."""
    out, seen = [], 0
    with open(DATA / f"{word}.ndjson") as f:
        for line in f:
            r = json.loads(line)
            if recognized_only and not r["recognized"]:
                continue
            seen += 1
            if seen <= skip:
                continue
            strokes = [np.stack([np.asarray(s[0], float), np.asarray(s[1], float)], 1) for s in r["drawing"]]
            strokes = [s for s in strokes if len(s) >= 1]
            if not strokes:
                continue
            out.append(centre(strokes))
            if n and len(out) >= n:
                break
    return out


def bbox(strokes):
    pts = np.concatenate(strokes, 0)
    return pts.min(0), pts.max(0)


def centre(strokes, box=BOX):
    """The doodle centred in the box (the source aligns it to the top-left)."""
    lo, hi = bbox(strokes); c = (lo + hi) / 2
    return [s - c + box / 2 for s in strokes]


def stroke_length(s):
    return float(np.linalg.norm(np.diff(s, axis=0), axis=1).sum()) if len(s) > 1 else 0.0


def load_bank(words=WORDS, n=400, skip=0):
    return {w: load_word(w, n, skip=skip) for w in words}
