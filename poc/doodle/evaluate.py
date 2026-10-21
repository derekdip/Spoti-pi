"""Does the bank with edits give coherent, non-repeating drawings, and what does chaos cost? (docs/doodle-bots.md)

Two consumers, in this project's habit of scoring what a reader reads rather than the pixels:
  coherence   a nearest-neighbour classifier over the six words, trained on human doodles, applied to
              held-out human doodles (the ceiling), to bank variations, to hand-executed variations, and
              to whole collaborative canvases at three chaos levels. "Recognisable as the word" is what the
              VR player needs from the drawing.
  novelty     the distance from a drawing to its nearest neighbour in the bank, for held-out humans (a
              fresh person's doodle) and for generated drawings (excluding their own source); and the
              spread of variations of one source against the spread of independent human doodles.

  python3 -m poc.doodle.evaluate   -> poc/results/doodle_eval.md
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.doodle.bank import WORDS, load_word, BOX, bbox
from poc.doodle.edits import variation
from poc.doodle.hand import PERSONAS, execute
from poc.doodle.bots import make_bots, run_round, Frame, CANVAS

OUT = Path(__file__).resolve().parents[2] / "poc/results/doodle_eval.md"
G = 32


def raster(strokes, size=None):
    """A GxG bitmap of the strokes, fitted to the box with a margin (what a glance sees)."""
    img = np.zeros((G, G)); pts_all = np.concatenate(strokes, 0)
    lo, hi = pts_all.min(0), pts_all.max(0); span = max(float((hi - lo).max()), 1.0); c = (lo + hi) / 2
    for s in strokes:
        p = (s - c) / span * (G - 4) + G / 2
        for a, b in zip(p[:-1], p[1:]):
            n = int(np.linalg.norm(b - a)) + 2
            for u in np.linspace(0, 1, n):
                x, y = a + u * (b - a); xi, yi = int(round(x)), int(round(y))
                if 0 <= xi < G and 0 <= yi < G: img[yi, xi] = 1.0
        if len(s) == 1:
            x, y = (s[0] - c) / span * (G - 4) + G / 2; xi, yi = int(round(x)), int(round(y))
            if 0 <= xi < G and 0 <= yi < G: img[yi, xi] = 1.0
    # a little blur so near misses count
    k = np.array([[0.25, 0.5, 0.25]]); img = np.clip(np.apply_along_axis(lambda r: np.convolve(r, k[0], "same"), 0, img) + img, 0, 1)
    img = np.clip(np.apply_along_axis(lambda r: np.convolve(r, k[0], "same"), 1, img) + img, 0, 1)
    v = img.ravel(); return v / max(np.linalg.norm(v), 1e-9)


class KNN:
    def __init__(self, X, y, k=7):
        self.X, self.y, self.k = X, np.asarray(y), k

    def predict(self, Q):
        sims = Q @ self.X.T; idx = np.argsort(-sims, axis=1)[:, :self.k]
        votes = self.y[idx]; return np.array([np.bincount(v, minlength=len(WORDS)).argmax() for v in votes])

    def nn_dist(self, Q, exclude=None):
        sims = Q @ self.X.T
        if exclude is not None:
            for i, ex in enumerate(exclude):
                for j in ex: sims[i, j] = -1
        return np.sqrt(np.clip(2 - 2 * sims.max(1), 0, 4))


def main(seed=0):
    rng = np.random.default_rng(seed)
    train = {w: load_word(w, 1500) for w in WORDS}; test = {w: load_word(w, 400, skip=1500) for w in WORDS}
    X = np.stack([raster(d) for w in WORDS for d in train[w]]); y = [i for i, w in enumerate(WORDS) for _ in train[w]]; knn = KNN(X, y)
    L = ["# Doodle bots: coherence and novelty", "", f"Nearest-neighbour classifier (k = 7, cosine on {G}x{G} bitmaps) over six words, trained on 1500 human doodles per word; test sets of 400 held-out human doodles per word.", ""]
    acc = lambda Q, w: float(np.mean(knn.predict(Q) == WORDS.index(w)))
    L += ["## Coherence: fraction classified as the word", "", "The canvas columns score everything on the canvas; the team columns score the team's figure alone (its plan, details, fixes and copies), which is what the VR player builds, leaving out a solo bot's corner figure, a misheard bot's other word and the scribbles.", "",
          "| word | held-out humans | bank variations | variations drawn by a hand | canvas, chaos 0.15 | chaos 0.5 | chaos 0.85 | team figure, chaos 0.15 | chaos 0.5 | chaos 0.85 |", "|---|---|---|---|---|---|---|---|---|---|"]
    tot = {k: [] for k in ("h", "v", "e", "c15", "c50", "c85", "t15", "t50", "t85")}
    for w in WORDS:
        H = np.stack([raster(d) for d in test[w]]); a_h = acc(H, w)
        V = [variation(train[w][:400], rng) for _ in range(300)]; a_v = acc(np.stack([raster(d) for d in V]), w)
        E = []
        for d in V[:200]:
            ex = execute(d, PERSONAS[str(rng.choice(list(PERSONAS)))], rng); E.append([pts for _, pts in ex])
        a_e = acc(np.stack([raster(d) for d in E]), w)
        a_c, a_t = {}, {}
        for chaos in (0.15, 0.5, 0.85):
            C, T = [], []
            for _ in range(60):
                bots = make_bots(int(rng.integers(3, 6)), chaos, rng); canvas, frame, plan = run_round(w, train, bots, chaos, rng, duration=45.0)
                if canvas: C.append([s.xy for s in canvas])
                team = [s.xy for s in canvas if s.kind in ("plan", "extra", "fix", "copy")]
                if team: T.append(team)
            a_c[chaos] = acc(np.stack([raster(d) for d in C]), w); a_t[chaos] = acc(np.stack([raster(d) for d in T]), w)
        L.append(f"| {w} | {a_h:.2f} | {a_v:.2f} | {a_e:.2f} | {a_c[0.15]:.2f} | {a_c[0.5]:.2f} | {a_c[0.85]:.2f} | {a_t[0.15]:.2f} | {a_t[0.5]:.2f} | {a_t[0.85]:.2f} |")
        for k, v in zip(tot, (a_h, a_v, a_e, a_c[0.15], a_c[0.5], a_c[0.85], a_t[0.15], a_t[0.5], a_t[0.85])): tot[k].append(v)
    L.append("| **mean** | " + " | ".join(f"{np.mean(tot[k]):.2f}" for k in tot) + " |"); L.append("")
    # novelty
    L += ["## Novelty: distance to the nearest bank doodle, and spread", "", "| word | held-out human to bank | variation to bank (own source excluded) | hand-drawn variation to bank | spread of 20 variations of one source | spread of 20 human doodles |", "|---|---|---|---|---|---|"]
    for w in WORDS:
        wi = WORDS.index(w); offset = sum(len(train[v]) for v in WORDS[:wi])
        H = np.stack([raster(d) for d in test[w][:200]]); d_h = knn.nn_dist(H).mean()
        src_idx = rng.integers(0, 400, 200); V = []; excl = []
        for si in src_idx:
            oj = [int(j) for j in rng.integers(0, 400, 3)]; A = train[w][si]; others = [train[w][j] for j in oj]
            V.append(variation([A] + others, rng, p_recombine=0.5)); excl.append([offset + int(si)] + [offset + j for j in oj])
        Vr = np.stack([raster(d) for d in V]); d_v = knn.nn_dist(Vr, excl).mean()
        E = [[pts for _, pts in execute(d, PERSONAS[str(rng.choice(list(PERSONAS)))], rng)] for d in V[:100]]; d_e = knn.nn_dist(np.stack([raster(d) for d in E]), excl[:100]).mean()
        def spread(R):
            S = R @ R.T; n = len(R); return float(np.sqrt(np.clip(2 - 2 * S[np.triu_indices(n, 1)], 0, 4)).mean())
        sp_v = np.mean([spread(np.stack([raster(variation([train[w][i]] + [train[w][j] for j in rng.integers(0, 400, 3)], rng)) for _ in range(20)])) for i in rng.integers(0, 400, 10)])
        sp_h = spread(np.stack([raster(d) for d in test[w][:20]]))
        L.append(f"| {w} | {d_h:.3f} | {d_v:.3f} | {d_e:.3f} | {sp_v:.3f} | {sp_h:.3f} |")
    L += ["", "Reading: a variation is as far from its nearest bank doodle as a fresh human doodle is (the two 'to bank' columns against the first), so it is not a copy of anything in the bank. The spread columns are on the same coarse bitmap distance, which saturates near 1 for any two doodles that are not near-identical; they say that twenty variations of one source are not near-identical to each other, and no more than that.", ""]
    OUT.write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
