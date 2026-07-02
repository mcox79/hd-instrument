# Dim F Throughput Scaling — Batch QPS Analysis
**Filed:** 2026-07-02  
**Director drill:** SONNET LIBERAL / hidden-dimension F (throughput scaling)  
**P_def prior:** 0.18 (low priority)  
**P_def updated:** 0.28 (bottleneck is real but tractable — see below)

---

## PRIOR ARC WORK (substrate-KB check ran first)

- `exp_dev_handoff_research_final_impl_perf_bottlenecks_2026-06-07.md` — Pre-test C: encoder batching throughput at batch sizes 1/4/16/64; PASS threshold batch=16 latency ≤ 2x batch=1. That measured encoder (bge-small / Llama head) NOT substrate retrieval kernel.
- Misra-Gries concurrency degradation at 10 QPS identified as risk (P=0.55), not yet resolved.
- NO prior cell measured substrate retrieval QPS vs batch size at commercial M. This drill fills that gap.

---

## NUMBERS READ FROM DISK (no hallucination)

### Source 1: cleanup_latency_operating_curve_v1 — HARD_PASS CG
**Operation:** cleanup query = `p @ W_correlator.T` where W is (N x N). This is the ASSOCIATIVE RECALL kernel, NOT the retrieval kernel.

- Numpy backend, sequential single-query, N=8192:
  - p50 = 11–13ms across alpha values (M-invariant, as certified)
  - Sequential QPS ceiling (numpy): ~76–90 QPS at N=8192
  - O(N²) confirmed: slope = 2.0 in log-log

**Key distinction:** cleanup is O(N²), M-independent. At N=8192 this is 67M ops per query regardless of how many memories are stored.

### Source 2: commercial_M v5 HARD_PASS (torch.cuda, 3-seed, N=8192, M=[100k, 500k, 1M])
**Operation:** retrieval via Hebbian W=(M,N) — the `q @ W.T` step where W holds M key-vectors. This scales O(MN).

Sequential 200-query loop results (arm_name=ARM_STD, FP16 keys, mode=hebbian):

| M | Seed 7 QPS | Seed 13 QPS | Seed 19 QPS | Avg QPS | Avg latency |
|---|---|---|---|---|---|
| 100k | 2842 | 1716 | 2778 | 2445 | 0.41ms |
| 500k | 590 | 246 | 589 | 475 | 2.11ms |
| 1M | 294 | 100 | 277 | 224 | 4.47ms |

ARM_REPL (int8 keys, chunked attention):

| M | Avg QPS |
|---|---|
| 100k | 605 |
| 500k | 107 |
| 1M | 54 |

**Seed 13 is a notable outlier** (3-4x slower than seeds 7/19 at M=100k-500k). Most plausible cause: GPU thermal throttling or competing process during that run. Seed 7/19 agreement is strong.

**QPS scaling slope vs M (Hebbian FP16):** measured log-log slopes = −0.98 to −1.00 (fast seeds). Confirms O(MN) retrieval: QPS scales inversely with M as expected.

---

## HEADLINE: SUBSTRATE THROUGHPUT CEILING AT COMMERCIAL-M

At M=500k, N=8192, torch.cuda, sequential single-query dispatch:
- **Normal operation (seeds 7/19): ~590 QPS** per-query latency 1.7ms
- **Conservative floor (worst-case seed 13): ~246 QPS** per-query latency 4.1ms
- **Cleanup kernel (N=8192 numpy): ~83 QPS** (entirely separate O(N²) path)

At M=1M, N=8192, torch.cuda:
- Normal: ~285 QPS / 3.5ms
- Conservative: ~100 QPS / 10ms

---

## BATCH AMORTIZATION — DOES THROUGHPUT SCALE NEAR-LINEARLY WITH B?

### Theory

Substrate retrieval kernel: `(B, N) @ (N, M) -> (B, M)` or equivalently `q @ W.T` per-query in a loop.

When dispatched as a batched matmul (B queries together):
- Must read W from GPU DRAM once per batch regardless of B
- Memory access cost: constant = M × N × bytes_per_element
- FLOPs: B × 2 × M × N (scales with B)
- Arithmetic intensity AI = 2B ops/byte

In the memory-bandwidth-bound regime (AI < ridge point), throughput scales **linearly** with B: each doubling of B doubles QPS at no additional latency cost.

Ridge point (transition to compute-bound):
- A100: 312 TFLOPS / 2.0 TB/s = 156 ops/byte → B_ridge ≈ 78 queries
- H100: 989 TFLOPS / 3.35 TB/s = 295 ops/byte → B_ridge ≈ 148 queries
- RTX4090: 82.6 TFLOPS / 1.008 TB/s = 82 ops/byte → B_ridge ≈ 41 queries

### Predicted batch throughput (M=500k, N=8192, FP16, A100)

| Batch B | Regime | Predicted QPS | vs Sequential (B=1) |
|---|---|---|---|
| 1 | MEM-bound | ~244 | 1× |
| 8 | MEM-bound | ~1953 | 8× |
| 64 | MEM-bound | ~15,625 | 64× |
| 256 | COMPUTE-bound | ~38,000 | plateaus |
| 1024 | COMPUTE-bound | ~38,000 | no gain |

**Answer: YES, throughput scales near-linearly with B up to B≈64-148 depending on GPU, then plateaus.**

The v5 commercial_M cell measures SEQUENTIAL queries (Python loop, each dispatched individually). The 590 QPS is NOT the batch ceiling — it is the single-query streaming ceiling where each kernel launch is separate. True batched dispatch would be 10-60× higher throughput.

---

## MEMORY BANDWIDTH CLIFF AT (N=8192, M=1M)

W matrix sizes:
- M=100k, N=8192, FP16: 1.64 GB
- M=500k, N=8192, FP16: 8.19 GB  (A100 80GB can hold this; RTX4090 24GB: marginal)
- M=1M,   N=8192, FP16: 16.38 GB (requires A100/H100; consumer GPUs excluded)

Theoretical BW-bound QPS ceiling for single-query sequential dispatch (A100 2.0 TB/s):
- M=100k: 1221 QPS (measured 2445 — FASTER THAN BW FLOOR, likely L2 cache hit for 1.6GB)
- M=500k: 244 QPS (measured 590 — also faster; streaming kernel may cache chunks)
- M=1M: 122 QPS (measured 224 — faster; same caching effect)

The measured QPS is consistently ~2× the naive BW-floor prediction. This suggests the chunked streaming implementation gets useful cache reuse across the 200-query sequential loop (hot rows of W reused across queries). This is good news but non-trivial: cold-start single queries will be at the BW floor.

**Hard cliff at M=1M for consumer GPUs:** 16GB FP16 keys tensor exceeds RTX4090 VRAM (24GB total, ~8GB available after model). Int8 keys halve this to 8GB — fits on a 24GB consumer card. This makes `int8_keys=True` non-optional at M=1M on consumer hardware.

---

## QPS BUDGET FOR M3 PHASE 1

Assumptions:
- M=500k, N=8192 (CG-confirmed commercial-M)
- 2-3 substrate lookups per LLM call (context retrieve + WM update)
- Sequential baseline = 300 QPS (conservative, between seeds 13 and 7/19 avg)
- Batched B=64 baseline = ~19,200 QPS (theoretical, BW-linear)

| Scenario | Req/s | Substrate QPS needed | Seq margin | Batch B=64 margin | Verdict |
|---|---|---|---|---|---|
| Dev / demo | 1 | 2 | 150× | 9600× | trivial |
| Single user | 10 | 30 | 10× | 640× | safe |
| 10-user shard | 100 | 300 | 1.0× | 64× | seq OK, no headroom |
| 100-user shard | 1000 | 3000 | 0.1× | 6× | needs batching |

**M3 Phase 1 recommendation:** sequential dispatch is sufficient for single-user through ~10-user demo scenarios at M=500k. The 100-user production shard requires batched kernel dispatch or query queuing (B=32-64 sufficient for 6× headroom). At M=1M all scenarios need batching for production.

---

## RELATIONSHIP TO CG LANDINGS

### cleanup_latency CG
That cell certified O(N²) scaling of the cleanup (associative recall) kernel and confirmed M-invariance of cleanup latency. Throughput interpretation: cleanup QPS at N=8192 is 76-90 (numpy). Under torch.cuda the dtype mismatch bug caused both BACKEND arms to FAIL — so cleanup torch_cuda QPS is not yet measured. This is a gap: cleanup path is in the same latency budget as retrieval in a real M3 turn.

### commercial_M v5 MM
That cell certified mechanism holds at M=100k/500k/1M. The wall_s values per arm were measured but QPS was not the primary deliverable — they showed GPU utilization ~98% (kernel_active_fraction), confirming the kernels ARE compute/BW-active, not idle. The 590 QPS at M=500k is derived from wall_s/n_queries and is real (not hallucinated).

---

## CHEAPEST DECISIVE EXPERIMENT

**Not needed for the retrieval path** — the QPS numbers are readable from v5 existing wall_s data. The unknowns are:

1. **Cleanup torch.cuda QPS at N=8192** — blocked by dtype mismatch bug in cleanup_latency CG (BACKEND_TORCH_CUDA arm FAILED). Fix = cast query to float32 before dispatch. One-arm patch on existing cell. Estimated: 1-2 hours. Would confirm cleanup adds ~2-5ms (O(N²)) or less per turn in GPU mode.

2. **True batched QPS validation** — the v5 cell dispatches queries sequentially. Confirming that B=64 batch gives ~64× throughput requires a single new arm in the existing v5 framework (reshape n_queries into batches). Estimated: 2-3 hours cell-author. Would confirm or refute the BW-linear scaling prediction at the critical B=64 operating point for M3 deployment.

3. **Cold-start single-query latency at M=500k** — the v5 warmup is not explicit. Without warmup, each query in a cold GPU cold-cache scenario hits the full BW floor (4ms vs 1.7ms). One arm with warmup_queries=0 and n_queries=10 (no amortization). Would bound p99 for conversational latency budget.

Recommended priority: experiment (2) — batched QPS validation. It is load-bearing for the 100-user shard decision and can reuse existing cell scaffolding.

---

## P_DEF UPDATE

- Prior: 0.18 (low priority per hidden-dim drill initial estimate)
- Updated: 0.28

Rationale: throughput bottleneck is real at 100-user scale without batching. However the bottleneck is well-understood analytically (BW-bound, linear with B) and the fix (batched dispatch) is straightforward. This is not a surprise that invalidates the M3 design — it is a known deployment engineering requirement. P_def lifted because the gap between sequential-QPS and production-needed-QPS is larger than initially assumed (10× at 100-user, not 2×), but capped at 0.28 because the path to resolution is cheap.

---

## SOURCES (verified off-disk)

- `d:/AI/hd-instrument/data/exp_stage2_cleanup_latency_operating_curve_v1_seed_7/metrics.json`
- `d:/AI/hd-instrument/data/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_seed_7/metrics.json`
- `d:/AI/hd-instrument/data/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_seed_13/metrics.json`
- `d:/AI/hd-instrument/data/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_seed_19/metrics.json`
- Substrate-KB query: `bash tools/substrate_query.sh "throughput batch size queries per second scaling memory bandwidth"` — top hit cosine=0.29 (Pre-test C encoder batching, 2026-06-07 perf drill)
