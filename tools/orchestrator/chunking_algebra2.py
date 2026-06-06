
# Revised algebra - key insight: the "tokens per article" is the binding cost driver
# 968 tokens/article is ~15x more than a short abstract (which was the 10K benchmark)
# Need to recalibrate: the 5.7min/10K was for ABSTRACTS not full articles
# Full articles average 717 words = ~968 tokens
# Abstracts average ~150-200 words = ~200-270 tokens
# So full-article extraction is ~4-5x more expensive than abstract extraction

# Let us recalibrate with two regimes:
# (a) Abstract-only extraction: ~200 tokens/doc (like the 5.7min/10K benchmark)
# (b) Full-article extraction: ~968 tokens/doc

print("=== CALIBRATION CHECK ===")
# If 1B model on H100 does 10K abstracts in 5.7 min:
# That's 0.034 s/doc. At ~200 tokens/doc = 200/0.034 = ~5882 tok/s for 1B on H100
# Which is very reasonable for H100 batch inference of 1B model
toks_per_sec_1b_h100 = 200 / 0.034
print(f"Implied 1B H100 throughput (abstract mode): {toks_per_sec_1b_h100:.0f} tok/s")

# For 70B on H100x8: throughput is roughly proportional to tok/s
# H100 peak: ~3350 GB/s bandwidth; 70B in bf16 = 140GB, so tokens/s = bandwidth/model_size
# Per token = 2*70B flops forward pass; memory-bound at decode
# Single H100 at 70B bf16 (decode-limited): ~3350/(140) = ~24 tok/s
# With 8 H100s tensor parallel: ~24*8 = 192 tok/s (memory bandwidth scales with TP)
# At batch prefill (doc processing), prefill throughput is compute-bound not memory-bound
# Prefill at 8xH100: can process ~1000-2000 tok/s for 70B in batch mode
toks_per_sec_70b_h100x8_prefill = 1500  # batch prefill estimate
s_per_doc_abstract_70b = 200 / toks_per_sec_70b_h100x8_prefill
s_per_doc_full_70b = 968 / toks_per_sec_70b_h100x8_prefill
print(f"\n70B H100x8 prefill mode:")
print(f"  s/doc (abstract ~200 tok): {s_per_doc_abstract_70b:.4f}")
print(f"  s/doc (full article ~968 tok): {s_per_doc_full_70b:.4f}")

N_articles = 7_200_000
h100_70b_total_hr_prefill = (N_articles * s_per_doc_full_70b) / 3600
h100_cost_per_hr = 2.5
h100_70b_cost_prefill = h100_70b_total_hr_prefill * h100_cost_per_hr * 8
print(f"  Full Wikipedia wall: {h100_70b_total_hr_prefill:.1f} hr")
print(f"  Full Wikipedia cost (8x H100): ${h100_70b_cost_prefill:.0f}")

# Now for CPU with llama.cpp:
# llama.cpp at q4 7B on ARM CPU (4-core t4g.xlarge):
# Prefill throughput: ~2000-5000 tok/s (prefill is compute-bound, cheaper)
# Decode: 60 tok/s is decode; for extraction (single forward pass prefill) it's much faster
toks_per_sec_cpu_7b_prefill = 3000  # prefill only, no decode needed
s_per_doc_cpu_prefill = 968 / toks_per_sec_cpu_7b_prefill
print(f"\n7B CPU (t4g.xlarge) prefill-only:")
print(f"  s/doc: {s_per_doc_cpu_prefill:.4f}")

n_cpu_workers = 100
docs_per_worker = N_articles / n_cpu_workers
wall_cpu_hr = (docs_per_worker * s_per_doc_cpu_prefill) / 3600
total_cost_cpu = wall_cpu_hr * 0.04 * n_cpu_workers
print(f"  Wall (100 workers): {wall_cpu_hr:.1f} hr")
print(f"  Cost (100 CPU x $0.04/hr): ${total_cost_cpu:.2f}")

# Mac: prefill throughput for 70B Q4_K_M on Apple Silicon
# M4 Max: 546 GB/s bandwidth; 70B Q4_K_M = ~38 GB
# Prefill is compute-bound on the GPU tiles of M4 Max
# Apple ANE + Metal can do ~1000-3000 tok/s prefill for 70B
toks_per_sec_mac_prefill = 1200  # conservative prefill
s_per_doc_mac_prefill = 968 / toks_per_sec_mac_prefill
docs_per_mac = N_articles / 100
wall_mac_hr = (docs_per_mac * s_per_doc_mac_prefill) / 3600
total_cost_mac = wall_mac_hr * 0.001 * 100
print(f"\n70B Mac M4 Max prefill-only:")
print(f"  s/doc: {s_per_doc_mac_prefill:.4f}")
print(f"  Wall (100 Macs): {wall_mac_hr:.1f} hr")
print(f"  Cost (electricity only): ${total_cost_mac:.2f}")

# KEY INSIGHT: For activation EXTRACTION (not generation), we only need the PREFILL pass
# We do NOT generate tokens - we just run the forward pass and extract hidden states
# This is ~10-50x faster than generation-speed benchmarks
# The 5.7min/10K abstract benchmark WAS extraction-mode, not generation
# So the 1B H100 benchmark already captures this

# Recalibrate based on extraction mode rationale:
# 1B H100: 10K abstracts (200 tok each) in 5.7 min = 200/0.034 = 5882 tok/s
# Scaling to full articles (968 tok each) at same throughput:
# s/doc_full = 968/5882 = 0.1645 s/doc
s_per_doc_full_1b_h100 = 968 / toks_per_sec_1b_h100
total_1b_h100_hr = N_articles * s_per_doc_full_1b_h100 / 3600
total_1b_cost = total_1b_h100_hr * 2.5
print(f"\n=== REVISED BASELINES (extraction mode, full articles) ===")
print(f"1B H100 full-article extraction:")
print(f"  s/doc: {s_per_doc_full_1b_h100:.4f}")
print(f"  Wall: {total_1b_h100_hr:.1f} hr")
print(f"  Cost: ${total_1b_cost:.2f}")

# 70B (7B-scaled): extraction throughput scales ~proportional to model_size / bandwidth
# H100 memory bandwidth: 3350 GB/s
# 70B bf16 = 140 GB; 1B bf16 = 2 GB
# Per-token bandwidth at prefill: much less (only need activations not KV for prefill)
# Actually for extraction batch (large batch, prefill-dominated):
# 70B H100x8 throughput relative to 1B H100x1:
# = (1 GPU bandwidth / (70B params / 8 GPUs)) * (8 GPUs)
# = bandwidth / (70B/8) params = same bandwidth as 1B on 1GPU * (140GB / (140/8 GB)) = 8x
# Actually at large batch prefill, compute-bound:
# TFLOPS ratio H100x8 to H100x1 = 8x
# Model size ratio = 70:1
# Net factor = 8/70 = 0.114
toks_per_sec_70b_h100x8 = toks_per_sec_1b_h100 * 8 / 70  # ~672 tok/s
s_per_doc_70b_h100x8 = 968 / toks_per_sec_70b_h100x8
total_70b_h100x8_hr = N_articles * s_per_doc_70b_h100x8 / 3600
total_70b_cost = total_70b_h100x8_hr * 2.5 * 8
print(f"\n70B H100x8 full-article extraction (compute-scaled):")
print(f"  Implied throughput: {toks_per_sec_70b_h100x8:.0f} tok/s")
print(f"  s/doc: {s_per_doc_70b_h100x8:.4f}")
print(f"  Wall: {total_70b_h100x8_hr:.1f} hr")
print(f"  Cost: ${total_70b_cost:.0f}")

# 405B H100x16:
toks_per_sec_405b = toks_per_sec_1b_h100 * 16 / 405  # ~232 tok/s
s_per_doc_405b = 968 / toks_per_sec_405b
total_405b_h100x16_hr = N_articles * s_per_doc_405b / 3600
total_405b_cost = total_405b_h100x16_hr * 2.5 * 16
print(f"\n405B H100x16 full-article extraction:")
print(f"  Implied throughput: {toks_per_sec_405b:.0f} tok/s")
print(f"  s/doc: {s_per_doc_405b:.4f}")
print(f"  Wall: {total_405b_h100x16_hr:.1f} hr")
print(f"  Cost: ${total_405b_cost:.0f}")

# CPU WORKERS (extraction mode):
# llama.cpp prefill on ARM4 CPU: ~2000-5000 tok/s for 7B Q4
# Use 2500 tok/s (conservative; prefill is compute-not-memory-bound)
toks_cpu_prefill = 2500
s_per_doc_cpu = 968 / toks_cpu_prefill
docs_per_100workers = N_articles / 100
wall_cpu_prefill = docs_per_100workers * s_per_doc_cpu / 3600
cost_cpu = wall_cpu_prefill * 0.04 * 100
print(f"\n100 CPU workers (t4g.xlarge), 7B Q4 prefill:")
print(f"  tok/s per worker: {toks_cpu_prefill}")
print(f"  s/doc: {s_per_doc_cpu:.4f}")
print(f"  Wall: {wall_cpu_prefill:.1f} hr")
print(f"  Cost: ${cost_cpu:.2f}")

# Mac workers (extraction mode):
# Apple Silicon prefill for 70B Q4: ~2000-4000 tok/s (Metal/MLX compute-bound)
# Use 2000 tok/s
toks_mac_prefill = 2000
s_per_doc_mac = 968 / toks_mac_prefill
docs_per_100macs = N_articles / 100
wall_mac_prefill = docs_per_100macs * s_per_doc_mac / 3600
cost_mac = wall_mac_prefill * 0.001 * 100
print(f"\n100 Macs (M4 Max), 70B Q4 prefill:")
print(f"  tok/s per worker: {toks_mac_prefill}")
print(f"  s/doc: {s_per_doc_mac:.4f}")
print(f"  Wall: {wall_mac_prefill:.1f} hr")
print(f"  Cost (electricity): ${cost_mac:.2f}")

# 4090 GPU (30B Q4 prefill):
toks_4090_prefill = 8000  # 4090 at 30B prefill
s_per_doc_4090 = 968 / toks_4090_prefill
docs_per_1000gpus = N_articles / 1000
wall_4090 = docs_per_1000gpus * s_per_doc_4090 / 3600
cost_4090 = wall_4090 * 0.03 * 1000  # electricity $0.03/hr
print(f"\n1000 consumer GPUs (4090), 30B Q4 prefill:")
print(f"  tok/s per worker: {toks_4090_prefill}")
print(f"  s/doc: {s_per_doc_4090:.4f}")
print(f"  Wall: {wall_4090:.1f} hr")
print(f"  Cost (electricity): ${cost_4090:.2f}")

print("\n=== SUMMARY TABLE ===")
print(f"{'Scenario':<35} {'Wall(hr)':>10} {'Cost($)':>12} {'Model':>8}")
print("-"*70)
print(f"{'H100x1, 1B bf16 (baseline)':<35} {total_1b_h100_hr:>10.1f} {total_1b_cost:>12.0f} {'1B':>8}")
print(f"{'H100x8, 70B bf16':<35} {total_70b_h100x8_hr:>10.1f} {total_70b_cost:>12.0f} {'70B':>8}")
print(f"{'H100x16, 405B bf16':<35} {total_405b_h100x16_hr:>10.1f} {total_405b_cost:>12.0f} {'405B':>8}")
print(f"{'100 CPU, 7B Q4 (prefill)':<35} {wall_cpu_prefill:>10.1f} {cost_cpu:>12.0f} {'7B-Q4':>8}")
print(f"{'100 Mac, 70B Q4 (prefill)':<35} {wall_mac_prefill:>10.1f} {cost_mac:>12.2f} {'70B-Q4':>8}")
print(f"{'1000 4090 GPU, 30B Q4':<35} {wall_4090:>10.1f} {cost_4090:>12.0f} {'30B-Q4':>8}")
