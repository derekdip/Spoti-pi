/* Cross-check exactdda.h against the validated dda.c kernels (same rays, same path hash) and benchmark. */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "exactdda.h"
static inline uint64_t mix(uint64_t h, int64_t x, int64_t y, int64_t z) {
    h ^= (uint64_t)x * 0x9E3779B97F4A7C15ULL; h = (h << 13) | (h >> 51);
    h ^= (uint64_t)y * 0xC2B2AE3D27D4EB4FULL; h = (h << 17) | (h >> 47);
    h ^= (uint64_t)z * 0x165667B19E3779F9ULL; h *= 0xFF51AFD7ED558CCDULL; return h; }
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int n; if (fscanf(f, "%d", &n) != 1) return 1;
    int64_t (*o)[3] = malloc(sizeof(int64_t[3]) * n), (*d)[3] = malloc(sizeof(int64_t[3]) * n);
    for (int i = 0; i < n; i++) if (fscanf(f, "%ld %ld %ld %ld %ld %ld", &o[i][0], &o[i][1], &o[i][2], &d[i][0], &d[i][1], &d[i][2]) != 6) return 1;
    int steps = atoi(argv[2]); uint64_t *H = malloc(8 * n); int hash = atoi(argv[4]), walk = argc > 5 ? atoi(argv[5]) : 0;
    struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < n; i++) {
        edda_ray r; edda_init(&r, o[i], 65536, d[i]); uint64_t h = hash ? mix(0, r.v[0], r.v[1], r.v[2]) : 0;
        if (walk) { if (hash) { EDDA_WALK(&r, steps, X, Y, Z, { h = mix(h, X, Y, Z); }); } else { EDDA_WALK(&r, steps, X, Y, Z, { h += (uint64_t)X; }); } }
        else for (int k = 0; k < steps; k++) { edda_step(&r); if (hash) h = mix(h, r.v[0], r.v[1], r.v[2]); else h += (uint64_t)r.v[0]; }
        H[i] = h; }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double s = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    printf("exactdda.h %s (%s): %.3f s, %.2f ns per ray-step\n", walk ? "EDDA_WALK" : "edda_step", hash ? "with path hash" : "no hash", s, 1e9 * s / ((double)n * steps));
    if (hash) { FILE *g = fopen(argv[3], "w"); for (int i = 0; i < n; i++) fprintf(g, "%016llx\n", (unsigned long long)H[i]); fclose(g); }
    return 0; }
