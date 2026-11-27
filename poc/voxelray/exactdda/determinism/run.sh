#!/bin/bash
# Build determinism.c in several configurations and record per-ray path hashes.
set -e
N=20000; STEPS=2000
declare -a B=(
 "gcc_O0|gcc -O0"
 "gcc_O2|gcc -O2"
 "gcc_O3_native|gcc -O3 -march=native"
 "gcc_O3_native_fpcontract_off|gcc -O3 -march=native -ffp-contract=off"
 "gcc_O2_fastmath|gcc -O2 -ffast-math"
 "gcc_O3_native_fastmath|gcc -O3 -march=native -ffast-math"
 "gcc_O2_x87|gcc -O2 -mfpmath=387"
 "clang_O2|clang -O2"
 "clang_O3_native_fastmath|clang -O3 -march=native -ffast-math"
 "gcc_O3_native_fastmath_recip|gcc -O3 -march=native -ffast-math -mrecip=all"
 "clang_O3_native_fastmath_recip|clang -O3 -march=native -ffast-math -mrecip"
)
for b in "${B[@]}"; do name="${b%%|*}"; cmd="${b#*|}"
  $cmd -std=c99 -I../include -o det_$name determinism.c -lm
  ./det_$name $N $STEPS out_$name.txt; echo "built and ran $name: $cmd"
done
