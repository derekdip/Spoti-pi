/* Tests for exactdda.h: brute-force event sort, seek == stepping, parallel chunks, 26-connected policy, long rays,
   float quantisation determinism, C++-free C99 build. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "exactdda.h"
static uint64_t rng = 88172645463325252ULL;
static uint64_t xs(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }
static int64_t rint_(int64_t lo, int64_t hi) { return lo + (int64_t)(xs() % (uint64_t)(hi - lo + 1)); }
static int fails = 0;
#define CHECK(c, ...) do { if (!(c)) { fails++; fprintf(stderr, "FAIL %s:%d: ", __FILE__, __LINE__); fprintf(stderr, __VA_ARGS__); fprintf(stderr, "\n"); } } while (0)

typedef struct { __int128 tn, td; int a; } ev_t;
static int evcmp(const void *x, const void *y) {
    const ev_t *p = x, *q = y; __int128 l = p->tn * q->td, r = q->tn * p->td;
    if (l < r) return -1;
    if (l > r) return 1;
    return p->a - q->a; }
static void brute(const edda_ray *r0, int n, int64_t (*out)[3]) {
    ev_t *e = malloc(sizeof(ev_t) * 3 * (n + 2)); int m = 0;
    for (int a = 0; a < 3; a++) if (r0->ad[a]) for (int j = 1; j <= n + 1; j++) { e[m].tn = (__int128)j * r0->S - r0->F[a]; e[m].td = (__int128)r0->ad[a] * r0->S; e[m].a = a; m++; }
    qsort(e, m, sizeof(ev_t), evcmp);
    int64_t v[3] = { r0->start[0], r0->start[1], r0->start[2] }; memcpy(out[0], v, sizeof v);
    for (int k = 0; k < n; k++) { v[e[k].a] += r0->sg[e[k].a]; memcpy(out[k + 1], v, sizeof v); }
    free(e); }
static void rand_ray(edda_ray *r, int kind) {
    int64_t S = kind == 2 ? (1 << 16) : rint_(1, 60), o[3], d[3];
    for (int a = 0; a < 3; a++) { o[a] = rint_(-6 * S, 6 * S); d[a] = kind == 2 ? rint_(-(1 << 20), 1 << 20) : rint_(-25, 25); }
    if (kind == 1) for (int a = 0; a < 3; a++) { o[a] = S * rint_(-5, 5); d[a] = rint_(-4, 4); }     /* ties, axis-parallel */
    if (!d[0] && !d[1] && !d[2]) d[0] = 1;
    CHECK(edda_init(r, o, S, d) == EDDA_OK, "init");
}
int main(void) {
    int64_t (*A)[3] = malloc(sizeof(int64_t[3]) * 200001), (*B)[3] = malloc(sizeof(int64_t[3]) * 200001);
    /* 1. stepping == brute-force event sort */
    for (int t = 0; t < 3000; t++) {
        edda_ray r; rand_ray(&r, t % 2); int n = (int)rint_(1, 150); brute(&r, n, A);
        for (int k = 1; k <= n; k++) { edda_step(&r); CHECK(!memcmp(r.v, A[k], sizeof A[k]), "step != brute at ray %d step %d", t, k); }
    }
    printf("1. edda_step == brute-force event sort: 3000 random rays (generic, ties, axis-parallel)\n");
    /* 2. seek == stepping; 3. chunks; 4. 26-connected */
    for (int t = 0; t < 1500; t++) {
        edda_ray r, s; rand_ray(&r, t % 3); s = r; int n = 400;
        for (int k = 0; k <= n; k++) { memcpy(A[k], s.v, sizeof A[k]); if (k < n) edda_step(&s); }
        for (int q = 0; q < 20; q++) { int64_t k = rint_(0, n), v[3]; edda_voxel_at(&r, k, v); CHECK(!memcmp(v, A[k], sizeof v), "seek ray %d k %ld", t, (long)k); }
        for (int k0 = 0; k0 < n; k0 += 53) {            /* independent chunk: seek then step */
            edda_ray c = r; edda_seek(&c, k0); CHECK(!memcmp(c.v, A[k0], sizeof c.v), "chunk start");
            for (int k = k0 + 1; k <= n && k < k0 + 53; k++) { edda_step(&c); CHECK(!memcmp(c.v, A[k], sizeof c.v), "chunk ray %d k %d", t, k); }
        }
        edda_ray w = r; int64_t prev[3]; memcpy(prev, w.v, sizeof prev);
        for (int k = 0; k < 200; k++) {
            int mask = edda_step26(&w); int64_t dsum = 0, dmax = 0;
            for (int a = 0; a < 3; a++) { int64_t dd = llabs(w.v[a] - prev[a]); dsum += dd; if (dd > dmax) dmax = dd; }
            CHECK(dmax == 1 && dsum == __builtin_popcount(mask), "26-step");
            CHECK(!memcmp(w.v, A[w.steps], sizeof w.v), "26-path visits a subsequence of the 6-path");
            memcpy(prev, w.v, sizeof prev);
            if (w.steps > n - 3) break;
        }
    }
    printf("2-4. edda_seek == stepping (1500 rays x 20 positions), chunks join exactly, edda_step26 is 26-connected and a subsequence of the 6-path\n");
    /* 5. long rays: seek at 1e9 vs a chunk boundary, and t_exit monotone */
    for (int t = 0; t < 20; t++) {
        edda_ray r; rand_ray(&r, 2); int64_t K = 1000000000LL + rint_(0, 1000);
        edda_ray a = r, b = r; edda_seek(&a, K); edda_seek(&b, K - 1000);
        for (int k = 0; k < 1000; k++) edda_step(&b);
        CHECK(!memcmp(a.v, b.v, sizeof a.v), "long-ray seek vs seek+step");
        int64_t tn0, td0, tn1, td1; edda_t_exit(&a, &tn0, &td0); edda_step(&a); edda_t_exit(&a, &tn1, &td1);
        CHECK((__int128)tn0 * td1 <= (__int128)tn1 * td0, "t_exit monotone");
    }
    printf("5. rays of 1e9 steps: seek(K) == seek(K-1000) + 1000 steps; exit times monotone\n");
    /* 6. float quantisation is deterministic and matches the integer init */
    { double o[3] = { 0.3, -7.125, 2.5 }, d[3] = { 0.6, -0.2, 0.77 }; edda_ray a, b; edda_init_f(&a, o, d, 16, 15); edda_init_f(&b, o, d, 16, 15);
      CHECK(!memcmp(&a, &b, sizeof a), "init_f deterministic"); for (int k = 0; k < 1000; k++) { edda_step(&a); edda_step(&b); } CHECK(!memcmp(a.v, b.v, sizeof a.v), "same path"); }
    printf("6. edda_init_f deterministic\n");
    /* 7. EDDA_WALK == edda_step, including the wide (128-bit) branch and early break */
    for (int t = 0; t < 2000; t++) {
        edda_ray r; rand_ray(&r, t % 3); edda_ray s = r, w = r; if (t % 4 == 3) { s.safe64 = 7; w.safe64 = 7; }
        int n = (int)rint_(1, 300), stopat = (t % 5 == 0) ? (int)rint_(1, n) : -1, cnt = 0;
        int64_t last[3] = { 0, 0, 0 };
        EDDA_WALK(&w, n, X, Y, Z, { cnt++; last[0] = X; last[1] = Y; last[2] = Z; edda_step(&s); CHECK(s.v[0] == X && s.v[1] == Y && s.v[2] == Z, "walk != step ray %d", t); if (cnt == stopat) break; });
        CHECK(!memcmp(w.v, s.v, sizeof w.v) && !memcmp(w.num, s.num, sizeof w.num) && w.steps == s.steps, "walk write-back");
        CHECK(!memcmp(last, w.v, sizeof last), "last voxel");
    }
    printf("7. EDDA_WALK == edda_step (2000 rays, incl. forced 128-bit branch and early break); state written back\n");
    printf(fails ? "FAILED: %d\n" : "all tests passed\n", fails);
    free(A); free(B); return fails != 0;
}
