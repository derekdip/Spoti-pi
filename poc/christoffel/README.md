# Christoffel words: digital lines from the Farey / Markoff tree

The simple closed curves on the torus, the Farey/Stern-Brocot tree behind the Markoff-number work, and digital straight
lines are the same combinatorial object. The lower Christoffel word of slope p/q is the step sequence of the
rasterised segment (0,0)-(q,p), and it is built by mediant concatenation, w(p/q) = w(left parent) w(right parent).

`christoffel.py` provides:

| Piece | What it does | Verified |
|---|---|---|
| `christoffel(p, q)`, `christoffel_closed` | Mediant construction and closed form | Identical for all p, q < 40 |
| `SLP(p, q)` | The word as a straight-line program built along the continued fraction with repeated squaring: O(log(p+q)) nodes, O(depth) random access (`letter`, `height`) | A 1.62e12-step line in 64 nodes (0.1 ms); 20 000 random height queries at 7 us each, all exact |
| `digital_line` | All-octant rasterisation, nearest pixel with ties rounded down | 3000 random segments within 1/2 pixel of the true line; equal to Bresenham except at exact half-pixel ties (all 1628 differing segments of 5000; `ties.log`) |
| `spans` | Run lengths of a digital line, which take two adjacent values (balance property) | |
| `floor_sum(n, m, a, b)` | sum floor((a i + b)/m) in O(log) | 3000 random cases |
| `lattice_points_in_convex_polygon` | Exact integer-point count of a rational convex polygon, from floor sums on the hull edges | 400 random polygons against brute force |
| `cohn_trace(p, q)` | Substitutes x -> [[2,1],[1,1]], y -> [[5,2],[2,1]] into the word: the trace is 3 m(p/q), m the Markoff number (m(2/5) = 1325) | Markoff equation on Farey triples |

The last row is the bridge to the hyperbolic work. A digital line of slope p/q *is* the simple geodesic of that slope on
the modular torus, with hyperbolic length 2 arccosh(3m/2).

**Sampling test** (`explore.py`). Rank-1 point sets {(i/N, frac(i alpha))}, N = 610, with alpha from the Markoff/Lagrange
spectrum (golden ratio, 1 + sqrt 2, (9 + sqrt 221)/10, (23 + sqrt 1517)/26) all have N D* = 3.2-3.4, against 3.8-43 for
random slopes. The order within the spectrum does not follow the Lagrange constant at this N.

Honest limits:
- y_k = floor(k p/n) already gives O(1) random access for a single line. The value of the SLP is structural: hierarchical
  spans, range aggregates (floor sums), shared sub-words for tile caching, comparing and intersecting lines without
  expanding them.
- floor_sum is a known algorithm (e.g. the AtCoder library).
