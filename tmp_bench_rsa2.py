import sys, time, statistics
sys.path.insert(0, r'C:\dev\hd-instrument\tools\hp12')
import rsa_accumulator as ra

acc = ra.RSAAccumulator()
# Pre-load
for i in range(20):
    acc.add(f"fact_{i}")
print("pre-loaded 20 facts")

# Benchmark add (issuance) and delete (the cert-producing op for HP-12 demo)
for _ in range(3):
    acc.add("warmup_add")
    acc.delete("warmup_add")

# add benchmark
add_times = []
for i in range(100):
    t0 = time.perf_counter()
    acc.add(f"bench_add_{i}")
    add_times.append((time.perf_counter() - t0) * 1000.0)
# delete benchmark
del_times = []
for i in range(100):
    t0 = time.perf_counter()
    acc.delete(f"bench_add_{i}")
    del_times.append((time.perf_counter() - t0) * 1000.0)

print(f"add latency:    p50={statistics.median(add_times):.3f}ms  p95={sorted(add_times)[94]:.3f}ms")
print(f"delete latency: p50={statistics.median(del_times):.3f}ms  p95={sorted(del_times)[94]:.3f}ms")
print(f"HP gate <1ms: add p50 {'PASS' if statistics.median(add_times) < 1.0 else 'MID'} ; delete p50 {'PASS' if statistics.median(del_times) < 1.0 else 'MID'}")
