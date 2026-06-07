import sys, time, statistics
sys.path.insert(0, r'C:\dev\hd-instrument\tools\hp12')
import rsa_accumulator as ra

print("RSAAccumulator methods:", [m for m in dir(ra.RSAAccumulator) if not m.startswith('_')])

acc = None
for kw in [{'bits': 512}, {'modulus_bits': 512}, {'key_bits': 512}, {}]:
    try:
        acc = ra.RSAAccumulator(**kw)
        print(f"created with kwargs {kw}")
        break
    except TypeError as e:
        print(f"  kwargs {kw} failed: {e}")
if acc is None:
    print("FAIL: could not create RSAAccumulator")
    sys.exit(1)

for i in range(10):
    acc.add(f"fact_{i}".encode())
print("pre-loaded 10 facts")

issue_method = None
for name in ['gen_witness', 'witness', 'witness_gen', 'cert', 'gen_cert', 'membership_witness']:
    if hasattr(acc, name):
        issue_method = name
        break
print(f"witness method: {issue_method}")

if issue_method:
    fn = getattr(acc, issue_method)
    for _ in range(3):
        fn(b'fact_5')
    times = []
    for _ in range(100):
        t0 = time.perf_counter()
        fn(b'fact_5')
        times.append((time.perf_counter() - t0) * 1000.0)
    p50 = statistics.median(times)
    p95 = sorted(times)[int(len(times)*0.95)]
    print(f"witness latency: p50={p50:.3f}ms  p95={p95:.3f}ms  (N=100)")
    print(f"result: {'HP PASS (<1ms)' if p50 < 1.0 else 'still MIDDLE'}")
