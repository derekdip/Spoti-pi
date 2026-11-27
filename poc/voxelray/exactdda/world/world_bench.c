/* CPU voxel-world benchmark: exact (exactdda EDDA_WALK) vs float32/float64 Amanatides-Woo on a 1024 x 1024 x 256
   procedural terrain (32 MB bitset). Workloads: block picking (short rays, first hit) and line of sight (long rays).
   Input regimes: (a) exactly representable rays (exact = true path; mismatches are float errors),
                  (b) generic float rays (exact traverses the 20-bit-quantised direction). */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <omp.h>
#include "exactdda.h"
#define WX 1024
#define WY 1024
#define WZ 256
static uint64_t *W;
static inline int solid(int64_t x, int64_t y, int64_t z) {
    if ((uint64_t)x >= WX || (uint64_t)y >= WY || (uint64_t)z >= WZ) return -1;      /* outside */
    uint64_t i = ((uint64_t)x * WY + (uint64_t)y) * WZ + (uint64_t)z; return (int)((W[i >> 6] >> (i & 63)) & 1); }
static inline uint32_t hsh(int x, int y, int z) { uint32_t h = (uint32_t)x * 374761393u + (uint32_t)y * 668265263u + (uint32_t)z * 2147483647u; h = (h ^ (h >> 13)) * 1274126177u; return h ^ (h >> 16); }
static float vnoise2(float x, float y, int sc) { int xi = (int)floorf(x / sc), yi = (int)floorf(y / sc); float fx = x / sc - xi, fy = y / sc - yi;
    float a = hsh(xi, yi, 7) / 4294967296.0f, b = hsh(xi + 1, yi, 7) / 4294967296.0f, c = hsh(xi, yi + 1, 7) / 4294967296.0f, d = hsh(xi + 1, yi + 1, 7) / 4294967296.0f;
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy); return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy; }
static float vnoise3(int x, int y, int z, int sc) { int xi = x / sc, yi = y / sc, zi = z / sc; float fx = (float)(x % sc) / sc, fy = (float)(y % sc) / sc, fz = (float)(z % sc) / sc; float r = 0;
    for (int c = 0; c < 8; c++) { int dx = c & 1, dy = (c >> 1) & 1, dz = c >> 2; float w = (dx ? fx : 1 - fx) * (dy ? fy : 1 - fy) * (dz ? fz : 1 - fz); r += w * (hsh(xi + dx, yi + dy, zi + dz) / 4294967296.0f); } return r; }
static int H[WX][WY];
static void build(void) {
    W = calloc((size_t)WX * WY * WZ / 64, 8);
    for (int x = 0; x < WX; x++) for (int y = 0; y < WY; y++)
        H[x][y] = 60 + (int)(90 * vnoise2(x, y, 128) + 30 * vnoise2(x, y, 32) + 8 * vnoise2(x, y, 8));
    #pragma omp parallel for schedule(dynamic, 8)
    for (int x = 0; x < WX; x++) for (int y = 0; y < WY; y++) for (int z = 0; z < H[x][y] && z < WZ; z++) {
        if (z > 4 && vnoise3(x, y, z, 24) > 0.68f) continue;                               /* caves */
        uint64_t i = ((uint64_t)x * WY + y) * WZ + z;
        __atomic_fetch_or(&W[i >> 6], 1ULL << (i & 63), __ATOMIC_RELAXED); } }
typedef struct { double o[3], d[3]; int64_t on[3], dn[3]; int maxs; } q_t;
typedef struct { int64_t v[3]; int hit; int steps; } res_t;
static res_t run_exact(const q_t *q, int regime) {
    edda_ray r; res_t s = { { 0 }, 0, 0 };
    if (regime == 0) edda_init(&r, q->on, 65536, q->dn); else edda_init_f(&r, q->o, q->d, 16, 20);
    int st = 0, hit = 0;
    EDDA_WALK(&r, q->maxs, x, y, z, { st++; int sv = solid(x, y, z); if (sv) { hit = sv; break; } });
    s.v[0] = r.v[0]; s.v[1] = r.v[1]; s.v[2] = r.v[2]; s.hit = hit; s.steps = st; return s; }
#define AWW(TYPE, NAME, FL, CE) \
static res_t NAME(const q_t *q) { \
    TYPE o[3], d[3], tmax[3], tdel[3]; int64_t v[3], sgn[3]; res_t s; \
    for (int a = 0; a < 3; a++) { o[a] = (TYPE)q->o[a]; d[a] = (TYPE)q->d[a]; v[a] = d[a] >= 0 ? (int64_t)FL(o[a]) : (int64_t)CE(o[a]) - 1; sgn[a] = d[a] > 0 ? 1 : -1; \
        if (d[a] > 0) { tmax[a] = ((TYPE)(v[a] + 1) - o[a]) / d[a]; tdel[a] = (TYPE)1 / d[a]; } \
        else if (d[a] < 0) { tmax[a] = ((TYPE)v[a] - o[a]) / d[a]; tdel[a] = -(TYPE)1 / d[a]; } else { tmax[a] = (TYPE)1e30; tdel[a] = 0; } } \
    int st = 0, hit = 0; \
    for (int k = 0; k < q->maxs; k++) { int b = (tmax[1] < tmax[0]) ? 1 : 0; if (tmax[2] < tmax[b]) b = 2; \
        v[b] += sgn[b]; tmax[b] += tdel[b]; st++; int sv = solid(v[0], v[1], v[2]); if (sv) { hit = sv; break; } } \
    s.v[0] = v[0]; s.v[1] = v[1]; s.v[2] = v[2]; s.hit = hit; s.steps = st; return s; }
AWW(float, run_f32, floorf, ceilf)
AWW(double, run_f64, floor, ceil)

/* register-resident float Amanatides-Woo (fair baseline: same structure as EDDA_WALK) */
#define AWF(TYPE, NAME, FL, CE) \
static res_t NAME(const q_t *q) { \
    TYPE o[3], d[3]; int64_t v[3], sgn[3]; TYPE tm[3], td[3]; res_t s; \
    for (int a = 0; a < 3; a++) { o[a] = (TYPE)q->o[a]; d[a] = (TYPE)q->d[a]; v[a] = d[a] >= 0 ? (int64_t)FL(o[a]) : (int64_t)CE(o[a]) - 1; sgn[a] = d[a] > 0 ? 1 : -1; \
        if (d[a] > 0) { tm[a] = ((TYPE)(v[a] + 1) - o[a]) / d[a]; td[a] = (TYPE)1 / d[a]; } \
        else if (d[a] < 0) { tm[a] = ((TYPE)v[a] - o[a]) / d[a]; td[a] = -(TYPE)1 / d[a]; } else { tm[a] = (TYPE)1e30; td[a] = 0; } } \
    TYPE tx = tm[0], ty = tm[1], tz = tm[2]; const TYPE dx = td[0], dy = td[1], dz = td[2]; \
    int64_t x = v[0], y = v[1], z = v[2]; const int64_t sx = sgn[0], sy = sgn[1], sz = sgn[2]; \
    int st = 0, hit = 0; \
    for (int k = 0; k < q->maxs; k++) { \
        if (tx <= ty && tx <= tz) { if (ty < tx || tz < tx) {} x += sx; tx += dx; } \
        else if (ty <= tz) { y += sy; ty += dy; } else { z += sz; tz += dz; } \
        st++; int sv = solid(x, y, z); if (sv) { hit = sv; break; } } \
    s.v[0] = x; s.v[1] = y; s.v[2] = z; s.hit = hit; s.steps = st; return s; }
AWF(float, run_f32r, floorf, ceilf)
AWF(double, run_f64r, floor, ceil)

static uint64_t rs = 0x2545F4914F6CDD1DULL;
static uint64_t xr(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static double ur(void) { return (xr() >> 11) * (1.0 / 9007199254740992.0); }
static void make(q_t *Q, int n, int kind, int regime) {
    for (int i = 0; i < n; i++) {
        q_t *q = &Q[i]; int x = 16 + (int)(xr() % (WX - 32)), y = 16 + (int)(xr() % (WY - 32)), z = H[x][y] + 2; if (z > WZ - 3) z = WZ - 3;
        double dx, dy, dz;
        if (kind == 0) { double th = 2 * M_PI * ur(), c = -0.95 + 1.3 * ur(); double sn = sqrt(1 - c * c); dx = sn * cos(th); dy = sn * sin(th); dz = c; q->maxs = 256; }   /* picking */
        else { int x2 = 16 + (int)(xr() % (WX - 32)), y2 = 16 + (int)(xr() % (WY - 32)); while (abs(x2 - x) + abs(y2 - y) > 1100) { x2 = (x + x2) / 2; y2 = (y + y2) / 2; }
               int z2 = H[x2][y2] + 2; if (z2 > WZ - 3) z2 = WZ - 3; dx = x2 - x; dy = y2 - y; dz = z2 - z; q->maxs = (int)(fabs(dx) + fabs(dy) + fabs(dz)); if (q->maxs < 1) q->maxs = 1; }
        if (regime == 0) {          /* exactly representable: origin on a 2^-16 grid, integer direction < 2^20 */
            double m = fmax(fabs(dx), fmax(fabs(dy), fabs(dz))), sc = ((1 << 20) - 1) / m;
            for (int a = 0; a < 3; a++) q->dn[a] = llround((a == 0 ? dx : a == 1 ? dy : dz) * sc);
            int64_t base[3] = { x, y, z }; for (int a = 0; a < 3; a++) { q->on[a] = base[a] * 65536 + (int64_t)(xr() % 65536); q->o[a] = q->on[a] / 65536.0; q->d[a] = (double)q->dn[a]; }
        } else {
            double base[3] = { x + ur(), y + ur(), z + ur() }, dd[3] = { dx, dy, dz };
            for (int a = 0; a < 3; a++) { q->o[a] = base[a]; q->d[a] = dd[a]; } } } }
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
int main(void) {
    double t0 = now(); build(); uint64_t cnt = 0; for (size_t i = 0; i < (size_t)WX * WY * WZ / 64; i++) cnt += __builtin_popcountll(W[i]);
    printf("world %dx%dx%d, %.1f%% solid, built in %.1f s, %d threads\n", WX, WY, WZ, 100.0 * cnt / ((double)WX * WY * WZ), now() - t0, omp_get_max_threads());
    const char *kn[2] = { "block picking (<= 256 steps)", "line of sight (long)" }, *rn[2] = { "(a) exact inputs", "(b) float inputs" };
    int ns[2] = { 1000000, 200000 };
    for (int kind = 0; kind < 2; kind++) for (int regime = 0; regime < 2; regime++) {
        int n = ns[kind]; q_t *Q = malloc(sizeof(q_t) * n); make(Q, n, kind, regime);
        res_t *R[5]; for (int m = 0; m < 5; m++) R[m] = malloc(sizeof(res_t) * n);
        double tt[5]; long long steps[5];
        for (int m = 0; m < 5; m++) { long long sum = 0; double a = now();
            #pragma omp parallel for schedule(dynamic, 256) reduction(+:sum)
            for (int i = 0; i < n; i++) { R[m][i] = m == 0 ? run_exact(&Q[i], regime) : m == 1 ? run_f32(&Q[i]) : m == 2 ? run_f64(&Q[i]) : m == 3 ? run_f32r(&Q[i]) : run_f64r(&Q[i]); sum += R[m][i].steps; }
            tt[m] = now() - a; steps[m] = sum; }
        int d01 = 0, d02 = 0, d12 = 0, hits = 0;
        for (int i = 0; i < n; i++) { hits += R[0][i].hit == 1;
            d01 += memcmp(R[0][i].v, R[1][i].v, 24) != 0 || R[0][i].hit != R[1][i].hit;
            d02 += memcmp(R[0][i].v, R[2][i].v, 24) != 0 || R[0][i].hit != R[2][i].hit;
            d12 += memcmp(R[1][i].v, R[2][i].v, 24) != 0 || R[1][i].hit != R[2][i].hit; }
        printf("\n%s, %s: %d rays, %.1f%% hit, mean %.0f steps\n", kn[kind], rn[regime], n, 100.0 * hits / n, (double)steps[0] / n);
        const char *mn[5] = { "exact EDDA_WALK", "float32 A&W arrays", "float64 A&W arrays", "float32 A&W regs", "float64 A&W regs" };
        for (int m = 0; m < 5; m++) printf("   %-16s %6.1f M rays/s   %5.2f ns per step (incl. lookup)\n", mn[m], n / tt[m] / 1e6, 1e9 * tt[m] / steps[m]);
        printf("   result (hit voxel or end voxel) differs: exact vs f32 %d (%.2f%%), exact vs f64 %d (%.3f%%), f32 vs f64 %d (%.2f%%)\n", d01, 100.0 * d01 / n, d02, 100.0 * d02 / n, d12, 100.0 * d12 / n);
        int d34 = 0, d13 = 0; for (int i = 0; i < n; i++) { d13 += memcmp(R[1][i].v, R[3][i].v, 24) != 0; d34 += memcmp(R[0][i].v, R[4][i].v, 24) != 0 || R[0][i].hit != R[4][i].hit; }
        printf("   register f32 vs array f32 differ: %d;  exact vs register f64: %d\n", d13, d34);
        free(Q); for (int m = 0; m < 5; m++) free(R[m]); }
    return 0; }
