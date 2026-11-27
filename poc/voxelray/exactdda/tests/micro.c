#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "exactdda.h"
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+1e-9*t.tv_nsec; }
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int n; if (fscanf(f, "%d", &n) != 1) return 1;
    int64_t (*o)[3] = malloc(sizeof(int64_t[3]) * n), (*d)[3] = malloc(sizeof(int64_t[3]) * n);
    for (int i = 0; i < n; i++) if (fscanf(f, "%ld %ld %ld %ld %ld %ld", &o[i][0], &o[i][1], &o[i][2], &d[i][0], &d[i][1], &d[i][2]) != 6) return 1;
    int steps = 4096; uint64_t acc = 0; double t0;
    /* A: header as is */
    t0 = now(); for (int i = 0; i < n; i++) { edda_ray r; edda_init(&r, o[i], 65536, d[i]); for (int k = 0; k < steps; k++) { edda_step(&r); acc += (uint64_t)r.v[0]; } }
    printf("A header edda_step          %.2f ns/step (%llu)\n", 1e9*(now()-t0)/((double)n*steps), (unsigned long long)(acc&1));
    /* B: locals, same branch-free selection, no counter */
    t0 = now(); for (int i = 0; i < n; i++) { edda_ray r; edda_init(&r, o[i], 65536, d[i]);
        int64_t v0=r.v[0],v1=r.v[1],v2=r.v[2], n0=r.num[0],n1=r.num[1],n2=r.num[2], a0=r.ad[0],a1=r.ad[1],a2=r.ad[2], s0=r.sg[0],s1=r.sg[1],s2=r.sg[2], S=r.S;
        for (int k = 0; k < steps; k++) {
            int b = 0; int64_t nb = n0, ab = a0;
            if (n1 * ab < nb * a1) { b = 1; nb = n1; ab = a1; }
            if (n2 * ab < nb * a2) { b = 2; }
            if (b == 0) { v0 += s0; n0 += S; } else if (b == 1) { v1 += s1; n1 += S; } else { v2 += s2; n2 += S; }
            acc += (uint64_t)v0; }
        (void)v1; (void)v2; }
    printf("B locals, branch-free       %.2f ns/step (%llu)\n", 1e9*(now()-t0)/((double)n*steps), (unsigned long long)(acc&1));
    /* C: struct, no steps counter / safe64 check */
    t0 = now(); for (int i = 0; i < n; i++) { edda_ray r; edda_init(&r, o[i], 65536, d[i]);
        for (int k = 0; k < steps; k++) { int b = 0; if (r.num[1]*r.ad[b] < r.num[b]*r.ad[1]) b = 1; if (r.num[2]*r.ad[b] < r.num[b]*r.ad[2]) b = 2; r.v[b] += r.sg[b]; r.num[b] += r.S; acc += (uint64_t)r.v[0]; } }
    printf("C struct, no counter        %.2f ns/step (%llu)\n", 1e9*(now()-t0)/((double)n*steps), (unsigned long long)(acc&1));
    t0 = now(); for (int i = 0; i < n; i++) { edda_ray r; edda_init(&r, o[i], 65536, d[i]); EDDA_WALK(&r, steps, X, Y, Z, { acc += (uint64_t)X; }); }
    printf("D EDDA_WALK                 %.2f ns/step (%llu)\n", 1e9*(now()-t0)/((double)n*steps), (unsigned long long)(acc&1));
    /* E/F: register-resident float Amanatides-Woo (fair baseline) */
    for (int prec = 0; prec < 2; prec++) {
        t0 = now(); for (int i = 0; i < n; i++) {
            double o_[3], d_[3]; for (int a = 0; a < 3; a++) { o_[a] = (double)o[i][a] / 65536.0; d_[a] = (double)d[i][a]; }
            if (prec == 0) {
                float tm[3], td[3]; int64_t v[3], sg[3];
                for (int a = 0; a < 3; a++) { float oo = (float)o_[a], dd = (float)d_[a]; v[a] = dd >= 0 ? (int64_t)floorf(oo) : (int64_t)ceilf(oo) - 1; sg[a] = dd > 0 ? 1 : -1;
                    if (dd > 0) { tm[a] = ((float)(v[a] + 1) - oo) / dd; td[a] = 1.0f / dd; } else if (dd < 0) { tm[a] = ((float)v[a] - oo) / dd; td[a] = -1.0f / dd; } else { tm[a] = 1e30f; td[a] = 0; } }
                float tx = tm[0], ty = tm[1], tz = tm[2]; int64_t x = v[0], y = v[1], z = v[2];
                for (int k = 0; k < steps; k++) { if (tx <= ty && tx <= tz) { x += sg[0]; tx += td[0]; } else if (ty <= tz) { y += sg[1]; ty += td[1]; } else { z += sg[2]; tz += td[2]; } acc += (uint64_t)x; }
                (void)y; (void)z;
            } else {
                double tm[3], td[3]; int64_t v[3], sg[3];
                for (int a = 0; a < 3; a++) { double oo = o_[a], dd = d_[a]; v[a] = dd >= 0 ? (int64_t)floor(oo) : (int64_t)ceil(oo) - 1; sg[a] = dd > 0 ? 1 : -1;
                    if (dd > 0) { tm[a] = ((double)(v[a] + 1) - oo) / dd; td[a] = 1.0 / dd; } else if (dd < 0) { tm[a] = ((double)v[a] - oo) / dd; td[a] = -1.0 / dd; } else { tm[a] = 1e300; td[a] = 0; } }
                double tx = tm[0], ty = tm[1], tz = tm[2]; int64_t x = v[0], y = v[1], z = v[2];
                for (int k = 0; k < steps; k++) { if (tx <= ty && tx <= tz) { x += sg[0]; tx += td[0]; } else if (ty <= tz) { y += sg[1]; ty += td[1]; } else { z += sg[2]; tz += td[2]; } acc += (uint64_t)x; }
                (void)y; (void)z;
            } }
        printf("%s float%d A&W, registers   %.2f ns/step (%llu)\n", prec ? "F" : "E", prec ? 64 : 32, 1e9*(now()-t0)/((double)n*steps), (unsigned long long)(acc&1)); }
    return 0; }
