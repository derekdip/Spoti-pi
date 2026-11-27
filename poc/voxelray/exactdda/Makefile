CC ?= cc
CFLAGS ?= -O2 -std=c99 -Wall -Wextra -Iinclude
all: test example
test: tests/test_exactdda.c include/exactdda.h
	$(CC) $(CFLAGS) -o test_exactdda tests/test_exactdda.c -lm && ./test_exactdda
example: examples/raycast_grid.c include/exactdda.h
	$(CC) $(CFLAGS) -fopenmp -o raycast_grid examples/raycast_grid.c -lm && ./raycast_grid
cxx: include/exactdda.h
	printf '#include "exactdda.h"\nint main(){edda_ray r; long long o[3]={0,0,0}, d[3]={1,2,3}; edda_init(&r,(int64_t*)o,1,(int64_t*)d); edda_step(&r); return 0;}\n' > cxx_check.cpp && c++ -std=c++11 -Wall -Iinclude cxx_check.cpp -o cxx_check && ./cxx_check && echo "C++ build ok"
clean:
	rm -f test_exactdda raycast_grid cxx_check cxx_check.cpp bench
