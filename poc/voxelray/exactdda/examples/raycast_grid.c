/* Example: first occupied voxel along a ray in a 128^3 occupancy grid, exact and deterministic, with the exact hit
   distance; plus parallel chunked traversal of one long ray. */
#include <stdio.h>
#include "exactdda.h"
#define N 128
static unsigned char grid[N][N][N];
int main(void) {
    for (int x = 0; x < N; x++) for (int y = 0; y < N; y++) for (int z = 0; z < N; z++)
        grid[x][y][z] = ((x - 64) * (x - 64) + (y - 64) * (y - 64) + (z - 64) * (z - 64) < 30 * 30);   /* a ball */
    double o[3] = { 3.25, 10.5, 7.75 }, d[3] = { 1.0, 0.9, 1.1 };
    edda_ray r; edda_init_f(&r, o, d, 16, 15);
    int hit = 0;
    EDDA_WALK(&r, 3 * N, x, y, z, {
        if (x < 0 || y < 0 || z < 0 || x >= N || y >= N || z >= N) break;
        if (grid[x][y][z]) { hit = 1; break; }
    });
    if (hit) {   /* entry parameter of the hit voxel = exit parameter of the previous one */
        edda_ray p = r; edda_seek(&p, r.steps - 1); int64_t tn, td; edda_t_exit(&p, &tn, &td);
        printf("hit voxel (%ld, %ld, %ld) after %ld steps, entry parameter t = %ld/%ld = %.9f\n", (long)r.v[0], (long)r.v[1], (long)r.v[2], (long)r.steps, (long)tn, (long)td, (double)tn / (double)td);
    } else printf("no hit\n");
    /* parallel: 8 chunks of a 10^6-step ray, each starts exactly via edda_seek */
    edda_ray L; edda_init_f(&L, o, d, 16, 15); int64_t end[8][3];
    #pragma omp parallel for
    for (int c = 0; c < 8; c++) { edda_ray q = L; edda_seek(&q, (int64_t)c * 125000); EDDA_WALK(&q, 125000, x, y, z, { (void)x; (void)y; (void)z; }); for (int a = 0; a < 3; a++) end[c][a] = q.v[a]; }
    edda_ray s = L; for (int k = 0; k < 1000000; k++) edda_step(&s);
    printf("chunked end (%ld, %ld, %ld) vs sequential end (%ld, %ld, %ld)\n", (long)end[7][0], (long)end[7][1], (long)end[7][2], (long)s.v[0], (long)s.v[1], (long)s.v[2]);
    return 0;
}
