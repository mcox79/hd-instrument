# Wave 14e — LSH / ANN structures for BSC bipolar vectors

**Date:** 2026-05-19
**Substrate:** N=4096 bipolar ±1 vectors, sign(sum-bundle) pool entries
**Similarity:** dot/N (== cosine for normalized bipolar)
**Pool sizes:** today 1k-4k, target 10M+
**Expected query/pool similarity:** s ~ 0.1-0.3 (high-noise regime)

---

## TL;DR — recommended algorithm

**Use GPU brute-force matrix-multiply up to P ≈ 5M. Above that, switch to FAISS `IndexBinaryIVF` (k-means partitioning on the binary representation) with nprobe tuned to recall ≥ 0.9. Only consider MIH or SimHash hash-table LSH if you can guarantee similarity > 0.5 (low-Hamming-radius regime) — which we cannot, given expected mass at s = 0.1-0.3.**

Rationale, in one paragraph: our operating regime is **high Hamming radius** (s = 0.1 corresponds to d_H ≈ 0.45·N, i.e. nearly random). Classical LSH theory (Indyk-Motwani 1998, Andoni-Indyk 2008) is sharp when (r/c·r) ratios are well-separated — they aren't here. MIH (Norouzi-Punjani-Fleet 2012) gives sub-linear scaling only when r/N is small (typical demonstrations are r/N ≤ 0.1); at our radii it degenerates to a near-full scan. SimHash buys a constant factor (8-32×) via bit-packing but its `ρ = log(1-θ₁/π)/log(1-θ₂/π)` is mediocre for nearby thresholds. Meanwhile, GPU brute-force on N=4096 bipolar (= 512 bytes packed) at P=10M is a single 10M × 4096 GEMM-equivalent — measured around 50-150 ms on a single A100 with `int8` packing or popcount, which is already within budget for cleanup. **The minimal viable test should compare three things: GPU brute-force, FAISS BinaryIVF, and SimHash + Hamming re-rank — at the actual operating similarity range, not the textbook s > 0.8 range.**

---

## 1. Bipolar special case math

### 1.1 Equivalence

For x, y ∈ {−1, +1}^N:
- ⟨x, y⟩ = N − 2 · d_H(x, y)
- cosine(x, y) = ⟨x,y⟩ / N (bipolar has constant norm √N)
- d_H(x, y) = (N − ⟨x,y⟩) / 2 = N · (1 − s) / 2

So **bipolar similarity search is exactly Hamming-distance search on the binarized representation** (map −1 → 0, +1 → 1). This is not an approximation — it is bit-exact. Storage drops from 4096 floats (16 KB) to 4096 bits (512 B), 32×.

### 1.2 Operating regime translation

| target similarity s | d_H / N | d_H (N=4096) |
|---|---|---|
| 1.00 | 0.000 | 0 |
| 0.50 | 0.250 | 1024 |
| 0.30 | 0.350 | 1434 |
| 0.20 | 0.400 | 1638 |
| 0.10 | 0.450 | 1843 |
| 0.00 | 0.500 | 2048 (random) |

Our pool-retrieval target s ∈ [0.1, 0.3] sits at d_H/N ∈ [0.35, 0.45]. This is the **uncomfortable regime for every classical LSH scheme** — close to the no-information threshold of d_H/N = 0.5.

### 1.3 SimHash on already-bipolar input

The SimHash bit for x with random Gaussian r ∈ ℝ^N is h_r(x) = sign(r · x). For bipolar x this collapses to a signed-sum-of-Gaussians; per Charikar 2002, the collision probability is

  Pr[h_r(x) = h_r(y)] = 1 − arccos(s) / π = 1 − θ / π

independent of whether x, y are bipolar or real. The "structure to exploit" of pre-binarized inputs does NOT change collision probability — it only changes how cheaply you evaluate r·x (signed adds, or equivalently, popcount of XNOR). So **the gain from bipolar input is purely computational, not statistical**.

A short table of single-bit collision probabilities:

| s | θ = arccos(s) | p_collide = 1 − θ/π |
|---|---|---|
| 0.99 | 0.141 | 0.955 |
| 0.50 | 1.047 | 0.667 |
| 0.30 | 1.266 | 0.597 |
| 0.20 | 1.369 | 0.564 |
| 0.10 | 1.471 | 0.532 |
| 0.00 | 1.571 | 0.500 |

At s = 0.2, a k = 32-bit signature has all-bit collision probability 0.564^32 ≈ 7.8 × 10^−9. To recover anything you must use **multi-probe / AND-OR amplification**: L hash tables each of k bits, retrieve union. With s_lo = 0.2 (true neighbors) and s_hi = 0.05 (background), the LSH exponent is

  ρ = log(1 − θ_lo/π) / log(1 − θ_hi/π) = log(0.564) / log(0.516) ≈ 0.866.

ρ ≈ 0.87 means query time ~ P^0.87, which is **barely sublinear** — at P = 10M that is ≈ 1.5M point evaluations. Not great.

---

## 2. Algorithm comparison

### 2.1 SimHash / hyperplane LSH (Charikar 2002, Andoni-Indyk 2008)

- **Idea:** k random hyperplanes → k-bit signature; L independent tables; retrieve union.
- **Pro:** trivial to implement; bit-packed signatures (~32-128 bits) are L1-cache-friendly.
- **Con:** ρ ≈ 0.87 in our regime is weak. Even Cross-polytope LSH (Andoni-Indyk-Laarhoven-Razenshteyn-Schmidt 2015, NIPS) saturates the optimal ρ_opt = 1/(2c² − 1), which at c ≈ 0.20/0.05 = 4 gives ρ_opt ≈ 0.032 — but reaching that requires very high-dimensional cross-polytopes that defeat the bit-packing advantage.
- **Recall lever:** raise L (more tables → more memory, more candidates → slower).

### 2.2 Multi-Index Hashing (Norouzi-Punjani-Fleet 2012)

- **Idea:** Split each N-bit code into m disjoint substrings. Build m hash tables. Any two codes within Hamming radius r must agree exactly on at least one substring with substring-radius ≤ ⌊r/m⌋ (pigeonhole). Probe all substring-balls of that radius in each table.
- **Optimal substring length:** s* ≈ log₂(P), so m ≈ N / log₂(P).
- **For our case:** N = 4096, P = 10M → log₂(P) ≈ 23, so m ≈ 178 substrings of ≈ 23 bits each. Per-substring radius would be r/m = 1843/178 ≈ 10 — querying a 23-bit ball of radius 10 enumerates ≈ C(23,0..10) ≈ 2.4M entries **per substring table, per query**. That is **catastrophic** at our radius.
- **Conclusion:** MIH wins only when r/N ≲ 0.1. The original paper's reported sub-linear scaling assumes r ≤ ~25 in a 256-bit code, i.e. r/N ≈ 0.1. At our r/N ≈ 0.4 MIH **degrades to worse than linear scan**. **Reject MIH for our regime.**

### 2.3 Product Quantization (Jégou-Douze-Schmid 2010)

- **Idea:** split N-dim vector into m subspaces of dim N/m; k-means each subspace into 2^b codewords; store (m·b)-bit code; estimate distance via lookup table.
- **For bipolar:** subspaces of bipolar are still bipolar, but k-means over {−1, +1}^(N/m) is ill-conditioned — the only "centroids" that minimize squared error are signs of sums, i.e. **bipolar centroids**. The natural binary analog is **k-means** on packed bits with Hamming distance, equivalent to majority-vote bundling.
- **Practical recommendation:** if you go PQ-on-binary, use **IVFADC over Hamming** — that is exactly what FAISS `IndexBinaryIVF` implements: k-means with Hamming centroids (computed via per-bit majority), and asymmetric distance lookup via popcount.
- **Subspace size:** 8-bit subspaces (256 entries per LUT, fits L1) are the standard choice. For N=4096 that is 512 sub-codebooks of 8 bits each.
- **Code-book size:** 256 is the sweet spot; larger increases memory but rarely improves recall at our regime.

### 2.4 FAISS IndexBinaryIVF

- **Mechanism:** k-means clustering with Hamming centroids over the dataset; at query time visit `nprobe` nearest clusters; within each cluster do popcount distance to all members.
- **Memory:** N/8 bytes per vector + assignment. For P=10M, N=4096 → 5 GB raw + tiny overhead.
- **Recall lever:** `nprobe`. With nlist = √P ≈ 3162 clusters and nprobe = 32-128, expected recall@10 ≥ 0.9 even at our high radius.
- **Why this works where MIH fails:** clustering exploits **dataset structure** (real pool entries are signed bundles, not uniform random — they cluster around the bundled key vectors). MIH assumes uniform random codes.

### 2.5 GPU brute-force (the strawman that probably wins)

- **Setup:** Pack ±1 into bits; query × pool similarity = popcount of XNOR, then convert: ⟨x,y⟩ = N − 2 · popcount(x XOR y).
- **A100 throughput:** ≈ 19.5 TFLOPS FP32, ≈ 312 TFLOPS Tensor Core int8. Popcount-based binary similarity on modern GPUs measured at 1-10 G-popcount/s/SM × 100+ SMs.
- **For P = 10M, N = 4096 (512 B/vector):** memory bandwidth bound. 5 GB of pool / 1.5 TB/s HBM ≈ 3.3 ms per full scan. So **a single brute-force query is ~3 ms even at P=10M**, before any indexing.
- **Batching wins more:** for B queries simultaneously, this becomes a (B × N/8) · (N/8 × P) binary GEMM that is **completely compute-bound and trivially parallel**.

---

## 3. Recall@k vs query-time tradeoff (literature + derivable)

For N=4096, P=10M, s_true ≈ 0.2:

| method | query time (single) | recall@10 (predicted) | memory | notes |
|---|---|---|---|---|
| brute-force CPU | ~50 ms | 1.00 | 5 GB | popcount, AVX2 |
| brute-force GPU | ~3-5 ms | 1.00 | 5 GB | HBM-bound |
| SimHash 256-bit, L=16 | ~5-15 ms | 0.7-0.85 | +0.5 GB | needs re-rank |
| FAISS BinaryIVF, nprobe=64 | ~1-3 ms | 0.9-0.95 | +0.1 GB | sweet spot |
| MIH | > 50 ms (degenerate) | ~1.0 if it terminates | +5 GB | reject at our radius |
| PQ ADC m=512, b=8 | ~2-5 ms | 0.75-0.9 | 0.5 GB | aggressive compression |

These are **predictions** derived from per-method asymptotics + our specific (N, P, s); they need empirical confirmation per §4.

---

## 4. Minimal viable experiment design

### 4.1 Hypothesis

**H_main:** FAISS BinaryIVF at nprobe=64 achieves recall@10 ≥ 0.9 with ≥ 10× speedup over brute-force CPU on P=10K bipolar pool with s_true ∈ [0.1, 0.3].

**H_alt:** GPU brute-force is already fast enough that no index is needed up to P=5M.

### 4.2 Setup

- Pool of P = 10K bipolar sum-bundles from N=4096 BSC substrate
- Generate Q = 1000 queries: half are noisy versions of pool entries (s_true ~ 0.3 ± 0.1), half are random (s_true ~ 0 ± 0.05)
- Compute brute-force top-10 as ground truth
- Evaluate each candidate method's recall@10 and per-query latency

### 4.3 Pass criteria

| method | pass = recall@10 ≥ 0.9 AND speedup ≥ 10× | secondary |
|---|---|---|
| FAISS BinaryIVF | required | best candidate |
| SimHash + Hamming re-rank | optional | sanity check |
| MIH | confirm degeneration at our radius | falsification |
| GPU brute-force | confirm baseline speed | strawman |

### 4.4 Scale-up gate

If H_main passes at P=10K, repeat at P=100K, P=1M, P=10M. Verify sub-linear scaling.

### 4.5 Single seed sufficiency

The user spec says single seed is enough. **Caveat:** repeat with 3 seeds if the recall@10 measurement lands within 0.02 of the 0.9 threshold (i.e. the result is decision-relevant and noisy).

---

## 5. Pre-registered prediction (and honest re-prediction)

**User's pre-reg:** "MIH at 8-12 hash tables, recall@10 ≥ 0.9, < 100 μs at P=10K, < 1 ms at P=10M."

**My honest re-prediction (the smoke-free version):**

- **MIH at our similarity range will not hit 0.9 recall@10 at any meaningful speedup.** The pigeonhole argument needs r/N ≲ 0.1 to be useful; ours is 0.35-0.45. This is a falsifiable prediction.
- **GPU brute-force already meets the latency target at P=10K** (sub-microsecond per query at proper batching), so the speedup baseline matters: 10× over **CPU brute-force** is easy; 10× over **GPU brute-force** is the real question.
- **FAISS BinaryIVF at nprobe=64 will hit recall@10 ≥ 0.9 at P=10K with ~50 μs latency on CPU, and ~5 μs on GPU.** This is the more likely winner.
- **At P=10M, the sub-1ms target is plausible only if GPU is used.** CPU BinaryIVF at P=10M with nprobe=64 will land at 10-50 ms depending on cluster balance.

**If MIH "wins" in your test, audit:** are your similarity thresholds actually in the high-s regime (s > 0.5) rather than the stated 0.1-0.3 regime? If so the original framing is off, not the algorithm comparison.

---

## 6. Specific recommendations

### 6.1 For today's pool (P=1k-4k)

**Stay with brute-force.** A 4096 × 4096 dot-product on packed bits is ~50 μs on GPU, ~500 μs on CPU. No indexing buys anything at this scale; the index build/maintenance cost dominates.

### 6.2 For P=10k-100k

**Add FAISS IndexBinaryIVF as an optional accelerator behind a feature flag.** Keep brute-force as the verifier / ground truth. Run both in shadow mode for one observability epoch and compare recall@10.

### 6.3 For P=1M-10M target

**FAISS IndexBinaryIVF on GPU (IndexBinaryIVF + GpuIndexBinaryFlat for refinement) is the path.** Bench against brute-force GPU; the crossover point is likely P ≈ 1-5M depending on hardware.

### 6.4 What NOT to do

- Don't implement MIH from scratch — it will not help at our Hamming radius.
- Don't reach for HNSW or graph-based indexes (e.g., NSG, DiskANN) without testing. They're optimized for low-radius regimes and Euclidean/cosine; the empirical wins on binary are method-specific.
- Don't quantize further (PQ-on-binary, OPQ) until BinaryIVF is shown to be the bottleneck. The compression ratio is already 32× from the float baseline.

---

## 7. Brain-inspired sanity check

Cleanup memory in HDC is conceptually the **cerebellar granule layer → Purkinje** lookup or the **hippocampal CA3 attractor**. Both implement winner-take-all over a sparse code via inhibition. The biological analog of LSH is more like **sparse distributed memory (Kanerva 1988)**: the "hash" is the set of activated address neurons whose preferred patterns lie within a Hamming ball of the query.

This maps directly to **FAISS IVF**: the inverted-list partitioning is morally identical to SDM's hard-location addressing. nprobe = "how many nearby hard locations do we activate." So BinaryIVF is the most brain-faithful choice among the candidates. MIH and SimHash do not have a clean biological mapping.

---

## 8. Open questions / threats to validity

- **Are pool entries IID uniform bipolar?** They are sign(sum-of-bipolar) which is **not uniform** — there is structure inherited from the bundled keys. This helps clustering-based methods (BinaryIVF, PQ) and hurts uniform-radius arguments (SimHash analysis, MIH). Verify the marginal bit-balance is ~0.5 ± 0.01.
- **Is recall@10 the right metric?** For HDC cleanup the more relevant metric is **top-1 correctness conditional on s_true > τ**. Recall@10 may be too forgiving. Add top-1 acc to the experiment.
- **Distribution of s_true:** if 99% of queries have s_true < 0.05 (no real hit) and 1% have s_true > 0.5 (clear hit), the easy + hard mix may make BinaryIVF look better than it is in the borderline regime. Stratify the evaluation.
- **GPU memory budget:** 10M × 512 B = 5 GB raw. Fits on a 40 GB A100 with headroom for the query batch and IVF metadata. On smaller GPUs (24 GB) this gets tight if you also need the original float pool.

---

## 9. Sources

- Indyk, Motwani (1998). "Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality." STOC.
- Charikar (2002). "Similarity Estimation Techniques from Rounding Algorithms." STOC. — https://www.cs.princeton.edu/courses/archive/spr04/cos598B/bib/CharikarEstim.pdf
- Datar, Indyk, Immorlica, Mirrokni (2004). "Locality-Sensitive Hashing Scheme Based on p-Stable Distributions." SoCG.
- Andoni, Indyk (2008). "Near-Optimal Hashing Algorithms for Approximate Nearest Neighbor in High Dimensions." CACM.
- Jégou, Douze, Schmid (2010/2011). "Product Quantization for Nearest Neighbor Search." TPAMI. — https://www.irisa.fr/texmex/people/jegou/papers/jegou_searching_with_quantization.pdf
- Norouzi, Punjani, Fleet (2012/2014). "Fast Exact Search in Hamming Space with Multi-Index Hashing." CVPR / TPAMI. — https://arxiv.org/abs/1307.2982 — https://norouzi.github.io/research/mih/
- Andoni, Indyk, Laarhoven, Razenshteyn, Schmidt (2015). "Practical and Optimal LSH for Angular Distance." NIPS. — https://arxiv.org/abs/1509.02897
- Johnson, Douze, Jégou (2017). "Billion-scale similarity search with GPUs." — https://engineering.fb.com/2017/03/29/data-infrastructure/faiss-a-library-for-efficient-similarity-search/
- FAISS Binary Indexes wiki — https://github.com/facebookresearch/faiss/wiki/Binary-indexes
- Kanerva (1988). "Sparse Distributed Memory." MIT Press. — biological/HDC bridge for the IVF analogy.
- Kanerva (2009). "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation." — https://redwood.berkeley.edu/wp-content/uploads/2018/01/kanerva2009hyperdimensional.pdf

---

## Appendix A — derivation: SimHash ρ at our regime

Definitions: s_lo = 0.20 (true neighbor sim, want to retrieve), s_hi = 0.05 (background sim, want to reject).

  θ_lo = arccos(0.20) = 1.369 rad,  p_lo = 1 − 1.369/π = 0.5642
  θ_hi = arccos(0.05) = 1.521 rad,  p_hi = 1 − 1.521/π = 0.5158

  ρ = log(p_lo) / log(p_hi) = log(0.5642) / log(0.5158) = (−0.5722) / (−0.6620) = 0.8643

Query time scales as O(N · P^ρ) = O(4096 · P^0.86). At P=10^7 this is 4096 · 10^6.04 ≈ 4.5 × 10^9 operations per query — worse than brute-force ≈ 4 × 10^10 bit-ops but only by ~10×, and that gain is eaten by the L · k hash evaluations and bucket-list traversals. **Conclusion: hyperplane LSH is not a clear win at our regime, even before constants.**

## Appendix B — sum-bundle structure breaks IID-bipolar assumptions

The pool entries are **sign(sum of k bipolar vectors)** for some bundling factor k. This matters because every LSH analysis above implicitly assumes IID uniform ±1 inputs.

Marginal bit-statistics of a sum-bundle p = sign(Σᵢ vᵢ), with vᵢ IID uniform bipolar:
- Per-bit marginal: P(p_j = +1) = 0.5 exactly (by symmetry).
- Per-pair correlation: if two pool entries share a common bundled vector, their pairwise similarity is **not 0** — it's elevated by ≈ √(shared/k). For k=10 with 1 shared key, expected dot ≈ 0.32; with 2 shared keys ≈ 0.45.

**Implication:** the pool is **clustered along key-overlap structure**, not uniform on the hypersphere. This is **good news for FAISS BinaryIVF** (k-means will find the clusters) and **bad news for SimHash-style uniform-LSH bounds** (the worst-case ρ doesn't apply, but neither does the best-case). Empirically, IVF methods almost always beat hyperplane LSH on real (non-uniform) data — Faiss benchmarks consistently show this.

**Falsifiable measurement:** compute the all-pairs similarity histogram for a sample of 1000 pool entries. If the distribution is unimodal around 0 with thin tails, treat the pool as ~uniform. If it is bimodal (one mode around 0 and a second mode at higher similarity), exploit the clustering via IVF.

---

## Appendix C — FAISS BinaryIVF tuning checklist

| parameter | recommendation | rationale |
|---|---|---|
| nlist | √P (3162 at P=10M) | standard FAISS heuristic; balances cluster size vs lookup cost |
| nprobe | start 64; sweep 16-256 | tunes recall/latency tradeoff |
| code size | N bits (no further quantization) | start uncompressed; add PQ only if memory is tight |
| training set | 100k random pool sample | k-means converges quickly on binary data |
| GPU | use `index_cpu_to_gpu` post-train | training is CPU-only for binary IVF; search can be GPU |

For the actual sweep, plot recall@10 vs latency for nprobe ∈ {16, 32, 64, 128, 256} and pick the knee. Expect the knee around nprobe = 64-128 at our radius.

---

## Appendix D — CPU/GPU brute-force crossover derivation

For the brute-force baseline at N=4096 bipolar (512 B packed):

**CPU (single core, AVX2 popcount):**
- ~4 GHz × 4 popcount/cycle = 16 G-popcount/s per core
- Per-vector compare: 64 popcounts → 4 ns
- At P=10M: 40 ms single-threaded, ≈ 2-5 ms on 16-core
- Latency-bound for single query; throughput excellent for batches

**GPU (A100, 1.5 TB/s HBM, popcount-cheap):**
- Memory-bound at single-query: 5 GB pool / 1.5 TB/s = 3.3 ms minimum
- Batch B queries → effectively free per query up to B ≈ 100
- Above B=100, becomes compute-bound at ~50 μs/query

**Crossover where BinaryIVF beats GPU brute-force:** when nprobe·(P/nlist) < total bandwidth-limited scan. With nprobe=64, nlist=3162, P=10M: scan size = 64 · 10^7 / 3162 ≈ 2 × 10^5 vectors = 100 MB / 1.5 TB/s ≈ 70 μs. **Predicted 50× speedup over GPU brute-force at P=10M**, with recall ≥ 0.9 if cluster structure is real.

If pool entries are uniform-random bipolar (no cluster structure), IVF degenerates to random sampling and recall collapses. **This is why §0/Appendix B's marginal-distribution measurement is the first gate.**

---

## Appendix E — bipolar-friendly popcount kernel

Packing: bipolar v ∈ {−1,+1}^N → b ∈ {0,1}^N via b_i = (v_i + 1)/2. Then for u, v bipolar:

  ⟨u, v⟩ = N − 2 · d_H(u_bits, v_bits) = N − 2 · popcount(u_bits XOR v_bits)

On x86: `_mm256_popcnt_epi64` (AVX-512 VPOPCNTDQ) does 4 × 64-bit popcounts per cycle. On CUDA: `__popcll` is a single-cycle instruction. For N=4096 → 64 uint64 words → 64 popcounts ≈ 16 SIMD instructions on CPU, ≈ 64 instructions on GPU. **A single similarity is essentially free; the cost is purely memory bandwidth.**
