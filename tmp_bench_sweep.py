import sys, time, statistics
sys.path.insert(0, r'C:\dev\hd-instrument\tools\hp12')
import rsa_accumulator as ra

print(f"Sweeping rsa_bits to find where add/delete <1ms")
for rb in [128, 192, 256, 384, 512, 768, 1024]:
    acc = ra.RSAAccumulator(rsa_bits=rb)
    for i in range(10):
        acc.add(f"setup_{i}")
    for _ in range(3):
        acc.add("warm"); acc.delete("warm")
    add_t = []
    del_t = []
    for i in range(50):
        e = f"e_{i}"
        t0 = time.perf_counter(); acc.add(e); add_t.append((time.perf_counter()-t0)*1000)
        t0 = time.perf_counter(); acc.delete(e); del_t.append((time.perf_counter()-t0)*1000)
    a = statistics.median(add_t); d = statistics.median(del_t)
    print(f"  rsa_bits={rb:4d}  N~{rb*2:4d}-bit  add_p50={a:7.3f}ms  delete_p50={d:7.3f}ms")
