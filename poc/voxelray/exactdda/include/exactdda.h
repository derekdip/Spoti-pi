/*
 * exactdda.h - exact, deterministic 3D voxel ray traversal (header-only, C99 / C++)
 *
 * A ray P(t) = O + t D with fixed-point origin O = o_num / S (integers) and integer direction D is walked through the
 * unit voxel grid with integer arithmetic only. The result never drifts and never depends on the platform, compiler
 * or float mode. Per axis, the plane crossings are the arithmetic progression t_j = (j S - F) / (|d| S), j = 1, 2, ...
 * (F in [0, S) is the start offset). The traversal merges the three progressions exactly; that is Amanatides-Woo with
 * the crossing times over a common denominator.
 *
 * Voxel convention: at parameter t the ray is in the voxel containing P(t + 0). Per axis the index is floor(x) when
 * d >= 0 and ceil(x) - 1 when d < 0, so a ray starting exactly on a plane is already in the voxel it is heading into.
 *
 * Tie policy (ray through an edge or corner):
 *   edda_step   - 6-connected: tied axes are stepped one per call, in the order x, y, z.
 *   edda_step26 - 26-connected: all tied axes are stepped together.
 *
 * Random access: edda_seek(r, k) puts the ray in the exact state after k edda_step calls, in O(log k) operations.
 * Long rays can therefore be split into independent chunks (parallel threads, GPU lanes, streaming).
 *
 * Range: with __int128 (GCC, Clang) comparisons are exact for |d| < 2^31 and up to edda_max_steps(r) steps
 * (about 2^62 / S per axis). Without __int128, comparisons use 64-bit products and require
 * steps_on_any_axis * S * max|d| < 2^62 (edda_max_steps reports the limit), and edda_seek is unavailable.
 *
 * Usage:   #include "exactdda.h"   (all functions are static inline; no implementation macro needed)
 * License: see the repository.
 */
#ifndef EXACTDDA_H
#define EXACTDDA_H
#include <stdint.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(__SIZEOF_INT128__)
#define EDDA_HAVE_INT128 1
__extension__ typedef __int128 edda_wide;
#else
#define EDDA_HAVE_INT128 0
typedef int64_t edda_wide;
#endif

typedef struct {
    int64_t v[3];      /* current voxel */
    int64_t num[3];    /* exit-time numerator per axis: next crossing at num / (ad S) */
    int64_t ad[3];     /* |d| */
    int64_t F[3];      /* start offset per axis, in [0, S) */
    int64_t start[3];  /* start voxel */
    int64_t S;         /* fixed-point denominator of the origin */
    int64_t steps;     /* edda_step calls taken since the start */
    int64_t sg[3];     /* sign of d */
    int64_t safe64;    /* while steps < safe64, 64-bit products are exact (fast path) */
} edda_ray;

enum { EDDA_OK = 0, EDDA_EBADS = -1, EDDA_EZERODIR = -2, EDDA_ERANGE = -3 };

static inline int64_t edda__floordiv(int64_t a, int64_t b) { int64_t q = a / b; return (a % b != 0 && ((a < 0) != (b < 0))) ? q - 1 : q; }
static inline int64_t edda__ceildiv(int64_t a, int64_t b) { return -edda__floordiv(-a, b); }

/* Initialise from fixed-point data: origin o_num[a] / S, direction d[a] (not all zero). */
static inline int edda_init(edda_ray *r, const int64_t o_num[3], int64_t S, const int64_t d[3]) {
    if (S <= 0) return EDDA_EBADS;
    if (!d[0] && !d[1] && !d[2]) return EDDA_EZERODIR;
    r->S = S; r->steps = 0;
    for (int a = 0; a < 3; a++) {
        int64_t o = o_num[a], da = d[a];
        if (da > INT32_MAX || da < -(int64_t)INT32_MAX) return EDDA_ERANGE;
        if (da >= 0) { r->v[a] = edda__floordiv(o, S); r->F[a] = o - r->v[a] * S; }
        else { int64_t c = edda__ceildiv(o, S); r->v[a] = c - 1; r->F[a] = c * S - o; }
        r->ad[a] = da < 0 ? -da : da; r->sg[a] = da > 0 ? 1 : (da < 0 ? -1 : 0);
        r->num[a] = S - r->F[a]; r->start[a] = r->v[a];
    }
    {   /* num_a <= (steps + 1) S on every axis, so num_a ad_b <= (steps + 1) S max|d| < 2^62 is safe */
        int64_t m = r->ad[0]; if (r->ad[1] > m) m = r->ad[1]; if (r->ad[2] > m) m = r->ad[2];
        int64_t lim = (((int64_t)1 << 62) / S) / m; r->safe64 = lim > 1 ? lim - 1 : 0;
    }
    return EDDA_OK;
}

/* Quantise a floating-point ray deterministically: origin to 2^-frac_bits voxels, direction to integers of at most
   dir_bits bits (largest component scaled to 2^dir_bits - 1). The direction is changed by at most one part in
   2^dir_bits; the traversal of the quantised ray is then exact. */
static inline int edda_init_f(edda_ray *r, const double o[3], const double d[3], int frac_bits, int dir_bits) {
    int64_t S = (int64_t)1 << frac_bits, on[3], dn[3];
    double m = fmax(fabs(d[0]), fmax(fabs(d[1]), fabs(d[2])));
    if (!(m > 0)) return EDDA_EZERODIR;
    double sc = (double)(((int64_t)1 << dir_bits) - 1) / m;
    for (int a = 0; a < 3; a++) { on[a] = (int64_t)llround(o[a] * (double)S); dn[a] = (int64_t)llround(d[a] * sc); }
    return edda_init(r, on, S, dn);
}

/* exit-time comparison: num_a / ad_a < num_b / ad_b */
static inline int edda__lt(const edda_ray *r, int a, int b) {
    return (edda_wide)r->num[a] * r->ad[b] < (edda_wide)r->num[b] * r->ad[a];
}
static inline int edda__eq(const edda_ray *r, int a, int b) {
    return (edda_wide)r->num[a] * r->ad[b] == (edda_wide)r->num[b] * r->ad[a];
}
/* Branch-free selection: an inactive axis (ad = 0) never wins a strict comparison against an active one, and an active
   axis always beats an inactive incumbent, so no special cases are needed. Ties keep the lower index. */
static inline int edda__next_axis(const edda_ray *r) {
    int b = 0;
    if (r->steps < r->safe64) {
        if (r->num[1] * r->ad[b] < r->num[b] * r->ad[1]) b = 1;
        if (r->num[2] * r->ad[b] < r->num[b] * r->ad[2]) b = 2;
    } else {
        if (edda__lt(r, 1, b)) b = 1;
        if (edda__lt(r, 2, b)) b = 2;
    }
    return b;
}

/* One 6-connected step. Returns the axis stepped (0, 1, 2). */
static inline int edda_step(edda_ray *r) {
    int b = edda__next_axis(r);
    r->v[b] += r->sg[b]; r->num[b] += r->S; r->steps++;
    return b;
}

/* One 26-connected step: all axes whose next crossing is simultaneous move together. Returns a bit mask of the axes
   moved. (steps counts the equivalent number of 6-connected steps, so edda_seek stays consistent.) */
static inline int edda_step26(edda_ray *r) {
    int b = edda__next_axis(r), mask = 0;
    int tied[3] = { 0, 0, 0 };
    (void)edda__eq;
    for (int a = 0; a < 3; a++) if (r->ad[a] && (a == b || edda__eq(r, a, b))) tied[a] = 1;
    for (int a = 0; a < 3; a++) if (tied[a]) { r->v[a] += r->sg[a]; r->num[a] += r->S; r->steps++; mask |= 1 << a; }
    return mask;
}


/* EDDA_WALK(r, maxsteps, x, y, z, { body }): fast traversal loop. Keeps the state in registers (several times faster
   than calling edda_step in a loop, which goes through memory on every step), performs up to maxsteps 6-connected steps,
   and runs body after each step with the new voxel in the int64_t variables x, y, z. "break" inside body stops early.
   On exit the ray state is written back to *r (v, num, steps), so EDDA_WALK, edda_step and edda_seek compose freely.
   Results are identical to edda_step, including ties (x, y, z order) and the exact wide fallback past safe64. */
#define EDDA_WALK(r, maxsteps, x, y, z, body) do {                                                                \
    edda_ray *edda_w_ = (r);                                                                                        \
    int64_t x = edda_w_->v[0], y = edda_w_->v[1], z = edda_w_->v[2];                                                \
    int64_t edda_n0_ = edda_w_->num[0], edda_n1_ = edda_w_->num[1], edda_n2_ = edda_w_->num[2];                     \
    const int64_t edda_a0_ = edda_w_->ad[0], edda_a1_ = edda_w_->ad[1], edda_a2_ = edda_w_->ad[2];                  \
    const int64_t edda_s0_ = edda_w_->sg[0], edda_s1_ = edda_w_->sg[1], edda_s2_ = edda_w_->sg[2], edda_S_ = edda_w_->S; \
    int64_t edda_st_ = edda_w_->steps; const int64_t edda_lim_ = edda_w_->safe64, edda_max_ = (maxsteps);          \
    for (int64_t edda_k_ = 0; edda_k_ < edda_max_; edda_k_++) {                                                     \
        int edda_b_ = 0; int64_t edda_nb_ = edda_n0_, edda_ab_ = edda_a0_;                                          \
        if (edda_st_ < edda_lim_) {                                                                                 \
            if (edda_n1_ * edda_ab_ < edda_nb_ * edda_a1_) { edda_b_ = 1; edda_nb_ = edda_n1_; edda_ab_ = edda_a1_; } \
            if (edda_n2_ * edda_ab_ < edda_nb_ * edda_a2_) edda_b_ = 2;                                             \
        } else {                                                                                                    \
            if ((edda_wide)edda_n1_ * edda_ab_ < (edda_wide)edda_nb_ * edda_a1_) { edda_b_ = 1; edda_nb_ = edda_n1_; edda_ab_ = edda_a1_; } \
            if ((edda_wide)edda_n2_ * edda_ab_ < (edda_wide)edda_nb_ * edda_a2_) edda_b_ = 2;                       \
        }                                                                                                           \
        if (edda_b_ == 0) { x += edda_s0_; edda_n0_ += edda_S_; }                                                   \
        else if (edda_b_ == 1) { y += edda_s1_; edda_n1_ += edda_S_; }                                              \
        else { z += edda_s2_; edda_n2_ += edda_S_; }                                                                \
        edda_st_++;                                                                                                 \
        { body }                                                                                                    \
    }                                                                                                               \
    edda_w_->v[0] = x; edda_w_->v[1] = y; edda_w_->v[2] = z;                                                        \
    edda_w_->num[0] = edda_n0_; edda_w_->num[1] = edda_n1_; edda_w_->num[2] = edda_n2_; edda_w_->steps = edda_st_;  \
} while (0)

/* Exact exit parameter of the current voxel: t = *tn / *td. */
static inline void edda_t_exit(const edda_ray *r, int64_t *tn, int64_t *td) {
    int b = edda__next_axis(r); *tn = r->num[b]; *td = r->ad[b] * r->S;
}

/* Largest number of steps on one axis for which the comparisons are guaranteed exact. */
static inline int64_t edda_max_steps(const edda_ray *r) {
    int64_t m = 1; for (int a = 0; a < 3; a++) if (r->ad[a] > m) m = r->ad[a];
#if EDDA_HAVE_INT128
    (void)m; return (INT64_MAX - r->S) / r->S;              /* num must fit in int64 */
#else
    return ((int64_t)1 << 62) / r->S / m;
#endif
}

#if EDDA_HAVE_INT128
/* number of crossings of axis b with time <= t (strict = 0) or < t (strict = 1), t = tn / td > 0 */
static inline int64_t edda__count(const edda_ray *r, int b, edda_wide tn, edda_wide td, int strict) {
    if (!r->ad[b]) return 0;
    /* floor(ad_b t + F_b / S) = floor((ad_b tn S + F_b td) / (td S)) */
    edda_wide N = (edda_wide)r->ad[b] * tn * r->S + (edda_wide)r->F[b] * td, D = td * r->S;
    edda_wide q = N / D; if (strict && q * D == N) q -= 1;
    return q < 0 ? 0 : (int64_t)q;
}
/* rank of event (axis a, crossing jj >= 1) in the merged (time, axis) order, 1-based */
static inline int64_t edda__rank(const edda_ray *r, int a, int64_t jj) {
    edda_wide tn = (edda_wide)jj * r->S - r->F[a], td = (edda_wide)r->ad[a] * r->S;
    int64_t k = 0;
    for (int b = 0; b < 3; b++) {
        if (!r->ad[b]) continue;
        int64_t lt = edda__count(r, b, tn, td, 1);
        k += (b <= a) ? edda__count(r, b, tn, td, 0) : lt;
    }
    return k;
}
/* Put the ray in the exact state after k edda_step calls from its start (k >= 0), in O(log k). */
static inline void edda_seek(edda_ray *r, int64_t k) {
    int64_t n[3] = { 0, 0, 0 };
    for (int a = 0; a < 3; a++) {
        if (!r->ad[a] || k == 0) continue;
        int64_t lo = 0, hi = k;                             /* largest jj with rank(a, jj) <= k */
        while (lo < hi) { int64_t mid = lo + (hi - lo + 1) / 2; if (edda__rank(r, a, mid) <= k) lo = mid; else hi = mid - 1; }
        n[a] = lo;
    }
    for (int a = 0; a < 3; a++) { r->v[a] = r->start[a] + r->sg[a] * n[a]; r->num[a] = (n[a] + 1) * r->S - r->F[a]; }
    r->steps = k;
}
/* Voxel after k steps, without changing r. */
static inline void edda_voxel_at(const edda_ray *r, int64_t k, int64_t out[3]) {
    edda_ray c = *r; edda_seek(&c, k); out[0] = c.v[0]; out[1] = c.v[1]; out[2] = c.v[2];
}
#endif

#ifdef __cplusplus
}
#endif
#endif /* EXACTDDA_H */
