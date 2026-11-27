/* Same source, different builds: does the voxel path change? Rays from an integer RNG (exactly representable as floats),
   traversed by exactdda (EDDA_WALK), float32 and float64 Amanatides-Woo. Writes one path hash per ray and method. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "exactdda.h"
static uint64_t st = 0x9E3779B97F4A7C15ULL;
static uint64_t xr(void) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return st; }
static inline uint64_t mix(uint64_t h, int64_t x, int64_t y, int64_t z) {
    h ^= (uint64_t)x * 0x9E3779B97F4A7C15ULL; h = (h << 13) | (h >> 51);
    h ^= (uint64_t)y * 0xC2B2AE3D27D4EB4FULL; h = (h << 17) | (h >> 47);
    h ^= (uint64_t)z * 0x165667B19E3779F9ULL; h *= 0xFF51AFD7ED558CCDULL; return h; }
#define AW(TYPE, NAME) \
static uint64_t NAME(const TYPE o[3], const TYPE d[3], int steps) { \
    TYPE tmax[3], tdel[3]; int64_t v[3], s[3]; \
    for (int a = 0; a < 3; a++) { v[a] = d[a] >= 0 ? (int64_t)floor(o[a]) : (int64_t)ceil(o[a]) - 1; s[a] = d[a] > 0 ? 1 : -1; \
        if (d[a] > 0) { tmax[a] = ((TYPE)(v[a] + 1) - o[a]) / d[a]; tdel[a] = (TYPE)1 / d[a]; } \
        else if (d[a] < 0) { tmax[a] = ((TYPE)v[a] - o[a]) / d[a]; tdel[a] = -(TYPE)1 / d[a]; } \
        else { tmax[a] = (TYPE)INFINITY; tdel[a] = 0; } } \
    uint64_t h = mix(0, v[0], v[1], v[2]); \
    for (int k = 0; k < steps; k++) { int b = (tmax[1] < tmax[0]) ? 1 : 0; if (tmax[2] < tmax[b]) b = 2; \
        v[b] += s[b]; tmax[b] += tdel[b]; h = mix(h, v[0], v[1], v[2]); } \
    return h; }
AW(float, aw32)
AW(double, aw64)
/* common no-accumulation variant: next crossing recomputed from the plane, t = (plane - o) * invd */
#define AWR(TYPE, NAME) \
static uint64_t NAME(const TYPE o[3], const TYPE d[3], int steps) { \
    TYPE inv[3]; int64_t v[3], s[3]; \
    for (int a = 0; a < 3; a++) { v[a] = d[a] >= 0 ? (int64_t)floor(o[a]) : (int64_t)ceil(o[a]) - 1; s[a] = d[a] > 0 ? 1 : -1; inv[a] = d[a] != 0 ? (TYPE)1 / d[a] : (TYPE)0; } \
    uint64_t h = mix(0, v[0], v[1], v[2]); \
    for (int k = 0; k < steps; k++) { TYPE t[3]; \
        for (int a = 0; a < 3; a++) t[a] = d[a] != 0 ? ((TYPE)(d[a] > 0 ? v[a] + 1 : v[a]) - o[a]) * inv[a] : (TYPE)1e30; \
        int b = (t[1] < t[0]) ? 1 : 0; if (t[2] < t[b]) b = 2; \
        v[b] += s[b]; h = mix(h, v[0], v[1], v[2]); } \
    return h; }
AWR(float, awr32)
AWR(double, awr64)
int main(int argc, char **argv) {
    int n = atoi(argv[1]), steps = atoi(argv[2]); FILE *g = fopen(argv[3], "w");
    for (int i = 0; i < n; i++) {
        int64_t on[3], dn[3];
        for (int a = 0; a < 3; a++) { on[a] = (int64_t)(xr() % (1 << 24)) - (1 << 23); dn[a] = (int64_t)(xr() % 2047) - 1023; }
        if (i % 8 == 7) for (int a = 0; a < 3; a++) { on[a] = 65536 * ((int64_t)(xr() % 200) - 100); dn[a] = (int64_t)(xr() % 13) - 6; }  /* tie-heavy */
        if (!dn[0] && !dn[1] && !dn[2]) dn[0] = 1;
        edda_ray r; edda_init(&r, on, 65536, dn); uint64_t he = mix(0, r.v[0], r.v[1], r.v[2]);
        EDDA_WALK(&r, steps, x, y, z, { he = mix(he, x, y, z); });
        float of[3], df[3]; double od[3], dd[3];
        for (int a = 0; a < 3; a++) { od[a] = (double)on[a] / 65536.0; dd[a] = (double)dn[a]; of[a] = (float)od[a]; df[a] = (float)dd[a]; }
        fprintf(g, "%016llx %016llx %016llx %016llx %016llx\n", (unsigned long long)he, (unsigned long long)aw32(of, df, steps), (unsigned long long)aw64(od, dd, steps), (unsigned long long)awr32(of, df, steps), (unsigned long long)awr64(od, dd, steps));
    }
    fclose(g); return 0; }
