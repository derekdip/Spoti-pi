"""Uniform random rooted planar hypermaps by mobiles, with the exact moments as test statistics.

The bijection used in the proof is also a linear-time sampler. A pointed rooted planar bipartite map
with k edges is a mobile with k edges and a marked corner; a mobile is a plane tree whose black nodes
of half-degree i carry one of C(2i-1, i-1) label patterns.  Reading R = 1 + sum C(2i-1,i) t^i R^i as
a simply generated tree (a node of out-degree i is a black node of half-degree i whose first i-1
children are new white vertices and whose last child continues the parent white vertex), a uniform
mobile is drawn by the cycle lemma: i.i.d. out-degrees with weights C(2i-1,i) y^i at the critical
y = 3/16, conditioned on the total, rotated once.

Colours need no map closure: in a bipartite map the colour of a vertex is the parity of its distance
to the pointed vertex, and the distance is the mobile label minus the minimum label plus one.

Reported per size k (Monte Carlo against the exact values):
  E_pointed[1/v]        = 3 / (2 (k+2))        checks the sampler's normalisation (no theorem)
  E_rooted[c3]          = (k+2)/3              faces = black nodes, checks the tree (no labels)
  E_rooted[c3^2]        = (D_k + Q_k) / (2 N_k) second moment of one colour (the proof's D and Q)
  E_rooted[(c1-c2)^2]   = 2 Q_k / N_k          the theorem, through the labels
where rooted expectations are ratio estimates with weight 1/v (a rooted map is pointed v ways).
"""
import json, os, sys, time
from math import comb, log, lgamma
import numpy as np

def exact_moments(k):
    K = k
    M = [0] * (K + 1)
    for n in range(1, K + 1): M[n] = 2 ** (n - 1) * comb(2 * n, n) // (n + 1)
    M2 = [sum(M[i] * M[n - i] for i in range(n + 1)) for n in range(K + 1)]
    Q = [0] * (K + 1)
    for n in range(K + 1): Q[n] = M2[n] - sum(Q[i] * M[n - i] for i in range(n))
    N = 3 * M[k] // (k + 2)
    D = (Q[k] + 2 * (k + 2) * M[k]) // 3
    return dict(N=N, L=M[k], Q=Q[k], D=D)

def degree_distribution(n, y=3/16):
    logw = np.array([0.0] + [lgamma(2*d) - lgamma(d+1) - lgamma(d) + d*log(y) for d in range(1, n+1)])
    p = np.exp(logw - logw.max()); return p / p.sum()

def sample_sequences(n, want, rng, p, batch=4096):
    """i.i.d. out-degree sequences of length n+1 conditioned on sum n, rotated to Lukasiewicz words."""
    out, tried = [], 0
    while len(out) < want:
        seqs = rng.choice(len(p), size=(batch, n + 1), p=p)
        tried += batch
        good = seqs[seqs.sum(axis=1) == n]
        for s in good:
            pref = np.cumsum(s - 1)
            r = int(np.argmin(pref)) + 1            # rotate so the word becomes a valid tree
            out.append(np.concatenate([s[r:], s[:r]]))
    return out[:want], tried

def mobile_statistics(word, rng):
    """returns (v, c3, (c1-c2)^2) for the pointed rooted map of one Lukasiewicz word."""
    n = len(word) - 1
    labels = [0]                                     # relative labels of white vertices, root first
    stack = [0]                                      # pending nodes: the label of their white vertex
    c3 = 0
    for d in word:
        ell = stack.pop()
        if d == 0: continue
        c3 += 1                                      # a black node = a face of degree 2d
        i = d
        if i > 1:
            downs = np.sort(rng.choice(2 * i - 1, size=i - 1, replace=False) + 1)
            steps = np.ones(2 * i, dtype=np.int64); steps[0] = -1; steps[downs] = -1
            cum = np.cumsum(steps)                   # cum[p-1] = label offset at position p
            child_labels = [ell + int(cum[q - 1]) for q in downs]
        else:
            child_labels = []
        labels.extend(child_labels)
        # children are visited in order: the new white vertices, then the continuation of ell
        for lab in reversed([*child_labels, ell]): stack.append(lab)
    lab = np.array(labels)
    true = lab - lab.min() + 1                       # distances to the pointed vertex (label 0)
    even = int(np.sum(true % 2 == 0)); odd = len(true) - even
    v = 1 + len(labels)
    return v, c3, (1 + even - odd) ** 2

def run(k, samples, seed):
    rng = np.random.default_rng(seed)
    p = degree_distribution(k)
    t0 = time.time()
    words, tried = sample_sequences(k, samples, rng, p)
    stats = np.array([mobile_statistics(w, rng) for w in words], dtype=float)
    v, c3, dd = stats[:, 0], stats[:, 1], stats[:, 2]
    ex = exact_moments(k)
    inv = 1 / v
    def rooted(f):
        return float(np.mean(f * inv) / np.mean(inv))
    def boot(f, B=400):
        idx = rng.integers(0, len(v), size=(B, len(v)))
        vals = [np.mean(f[i] * inv[i]) / np.mean(inv[i]) for i in idx]
        return float(np.std(vals))
    res = dict(k=k, samples=samples, tried=tried, seconds=round(time.time() - t0, 1),
               pointed_inv_v=dict(mc=float(np.mean(inv)), se=float(np.std(inv) / np.sqrt(len(v))), exact=3 / (2 * (k + 2))),
               rooted_c3=dict(mc=rooted(c3), se=boot(c3), exact=(k + 2) / 3),
               rooted_c3_sq=dict(mc=rooted(c3 ** 2), se=boot(c3 ** 2), exact=(ex["D"] + ex["Q"]) / (2 * ex["N"])),
               rooted_diff_sq=dict(mc=rooted(dd), se=boot(dd), exact=2 * ex["Q"] / ex["N"]))
    return res

if __name__ == "__main__":
    sizes = [int(a) for a in sys.argv[1:]] or [20, 50, 100, 200]
    samples = 60000
    results = []
    for k in sizes:
        r = run(k, samples if k <= 100 else samples // 2, seed=20260918 + k)
        results.append(r)
        print(f"k={k} samples={r['samples']} (tried {r['tried']}) {r['seconds']}s")
        for name in ("pointed_inv_v", "rooted_c3", "rooted_c3_sq", "rooted_diff_sq"):
            d = r[name]; z = (d["mc"] - d["exact"]) / d["se"] if d["se"] > 0 else float("nan")
            print(f"   {name:15s} mc={d['mc']:.5f} +- {d['se']:.5f}   exact={d['exact']:.5f}   z={z:+.2f}")
    out = os.path.join(os.path.dirname(__file__), "..", "results", "hyper_sampler.json")
    json.dump(results, open(out, "w"), indent=1)
    print("wrote", os.path.normpath(out))
