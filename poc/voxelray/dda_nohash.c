/* Exact vs floating-point 3D voxel traversal: benchmark and correctness.
   Rays: origin o/S (int64 numerators, S = 2^16), integer direction d. Policy 'face': one axis per step, ties -> x, y, z.
   Methods: 0 exact cross-multiplication (|d| < 2^15), 1 exact integer tMax (common denominator L = |dx dy dz|, |d| < 2^10),
            2 float32 Amanatides-Woo, 3 float64 Amanatides-Woo.
   Input file: n, then n lines "ox oy oz dx dy dz". Output: per-ray path hash and final voxel for each method, timings. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#ifdef _OPENMP
#include <omp.h>
#endif
#define S 65536LL
static inline uint64_t mix(uint64_t h, int64_t x, int64_t y, int64_t z) {
    h ^= (uint64_t)x * 0x9E3779B97F4A7C15ULL; h = (h << 13) | (h >> 51);
    h ^= (uint64_t)y * 0xC2B2AE3D27D4EB4FULL; h = (h << 17) | (h >> 47);
    h ^= (uint64_t)z * 0x165667B19E3779F9ULL; h *= 0xFF51AFD7ED558CCDULL; return h; }
typedef struct { int64_t o[3], d[3]; } ray_t;
static void init_exact(const ray_t *r, int64_t v[3], int64_t F[3], int64_t ad[3], int64_t sg[3]) {
    for (int a = 0; a < 3; a++) {
        int64_t o = r->o[a], d = r->d[a];
        if (d >= 0) { v[a] = (o >= 0) ? o / S : -((-o + S - 1) / S); F[a] = o - v[a] * S; }
        else { int64_t c = (o >= 0) ? (o + S - 1) / S : -((-o) / S); v[a] = c - 1; F[a] = c * S - o; }
        ad[a] = d < 0 ? -d : d; sg[a] = d > 0 ? 1 : (d < 0 ? -1 : 0); } }
static uint64_t exact_xmul(const ray_t *r, int steps, int64_t fin[3]) {
    int64_t v[3], F[3], ad[3], sg[3], num[3]; init_exact(r, v, F, ad, sg);
    for (int a = 0; a < 3; a++) num[a] = S - F[a];              /* j = 1 */
    uint64_t h = mix(0, v[0], v[1], v[2]);
    for (int k = 0; k < steps; k++) {
        int b = -1;
        for (int a = 0; a < 3; a++) if (ad[a]) { if (b < 0 || num[a] * ad[b] < num[b] * ad[a]) b = a; }
        v[b] += sg[b]; num[b] += S; h += (uint64_t)v[0]; }
    fin[0] = v[0]; fin[1] = v[1]; fin[2] = v[2]; return h; }
static uint64_t exact_tmax(const ray_t *r, int steps, int64_t fin[3]) {
    int64_t v[3], F[3], ad[3], sg[3], T[3], D[3]; init_exact(r, v, F, ad, sg);
    int64_t L = 1; for (int a = 0; a < 3; a++) if (ad[a]) L *= ad[a];
    for (int a = 0; a < 3; a++) {
        if (ad[a]) { int64_t m = L / ad[a]; T[a] = (S - F[a]) * m; D[a] = S * m; }
        else { T[a] = INT64_MAX; D[a] = 0; } }
    uint64_t h = mix(0, v[0], v[1], v[2]);
    for (int k = 0; k < steps; k++) {
        int b = (T[1] < T[0]) ? 1 : 0; if (T[2] < T[b]) b = 2;
        v[b] += sg[b]; T[b] += D[b]; h += (uint64_t)v[0]; }
    fin[0] = v[0]; fin[1] = v[1]; fin[2] = v[2]; return h; }
#define AW(TYPE, NAME, FLOOR, CEIL, INF) \
static uint64_t NAME(const ray_t *r, int steps, int64_t fin[3]) { \
    TYPE o[3], d[3], tmax[3], tdel[3]; int64_t v[3], st[3]; \
    for (int a = 0; a < 3; a++) { o[a] = (TYPE)r->o[a] / (TYPE)S; d[a] = (TYPE)r->d[a]; \
        v[a] = d[a] >= 0 ? (int64_t)FLOOR(o[a]) : (int64_t)CEIL(o[a]) - 1; st[a] = d[a] > 0 ? 1 : -1; \
        if (d[a] > 0) { tmax[a] = ((TYPE)(v[a] + 1) - o[a]) / d[a]; tdel[a] = (TYPE)1 / d[a]; } \
        else if (d[a] < 0) { tmax[a] = ((TYPE)v[a] - o[a]) / d[a]; tdel[a] = -(TYPE)1 / d[a]; } \
        else { tmax[a] = INF; tdel[a] = 0; } } \
    uint64_t h = mix(0, v[0], v[1], v[2]); \
    for (int k = 0; k < steps; k++) { int b = (tmax[1] < tmax[0]) ? 1 : 0; if (tmax[2] < tmax[b]) b = 2; \
        v[b] += st[b]; tmax[b] += tdel[b]; h += (uint64_t)v[0]; } \
    fin[0] = v[0]; fin[1] = v[1]; fin[2] = v[2]; return h; }
AW(float, aw32, floorf, ceilf, INFINITY)
AW(double, aw64, floor, ceil, INFINITY)
typedef uint64_t (*meth_t)(const ray_t *, int, int64_t *);
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: dda rays.txt steps out.txt\n"); return 1; }
    FILE *f = fopen(argv[1], "r"); int n; if (fscanf(f, "%d", &n) != 1) return 1;
    ray_t *R = malloc(sizeof(ray_t) * n);
    for (int i = 0; i < n; i++) if (fscanf(f, "%ld %ld %ld %ld %ld %ld", &R[i].o[0], &R[i].o[1], &R[i].o[2], &R[i].d[0], &R[i].d[1], &R[i].d[2]) != 6) return 1;
    fclose(f); int steps = atoi(argv[2]);
    meth_t M[4] = { exact_xmul, exact_tmax, aw32, aw64 }; const char *names[4] = { "exact_xmul", "exact_tmax", "float32_AW", "float64_AW" };
    uint64_t *H = malloc(8 * (size_t)n * 4); int64_t *FIN = malloc(8 * (size_t)n * 12);
    for (int m = 0; m < 4; m++) {
        struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < n; i++) H[(size_t)m * n + i] = M[m](&R[i], steps, &FIN[((size_t)m * n + i) * 3]);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        double s = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
        printf("%-11s %8.3f s   %6.2f ns per ray-step\n", names[m], s, 1e9 * s / ((double)n * steps)); }
    FILE *g = fopen(argv[3], "w");
    for (int i = 0; i < n; i++) { fprintf(g, "%d", i);
        for (int m = 0; m < 4; m++) fprintf(g, " %016llx %ld %ld %ld", (unsigned long long)H[(size_t)m * n + i], FIN[((size_t)m*n+i)*3], FIN[((size_t)m*n+i)*3+1], FIN[((size_t)m*n+i)*3+2]);
        fprintf(g, "\n"); }
    fclose(g); return 0; }
