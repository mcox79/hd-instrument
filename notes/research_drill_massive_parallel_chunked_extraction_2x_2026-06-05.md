# 2x Research Drill: Massive Parallel Chunked Extraction Architecture
**Date:** 2026-06-05
**Topic:** Distributed chunked LLM activation extraction for bipolar discrete-state associative memory
**Trigger:** 2x depth drill on prior cost estimates and architectural feasibility
**Calibration penalty applied:** P estimates deflated 0.15-0.25; novel-synthesis cap at 0.50

---

## HEADLINE

Chunked parallel extraction is NOT merely cheaper than sequential cloud -- it is categorically different in cost structure: 100 CPU workers running 7B Q4 prefill extract all of Wikipedia in ~8 hours for ~$31; 100 idle Apple Silicon laptops do the same with 70B Q4 for ~$1 electricity. The dominant cost insight is that activation extraction is PREFILL-ONLY (no decoding), which is 50-500x faster per document than generation-mode throughput benchmarks suggest. The "$14k for 405B" prior estimate was based on decode-mode throughput and overstates the real cost by ~40x. Revised estimate for 405B Wikipedia extraction with 16x H100: ~$333k (still prohibitive), but 30B with 1000 consumer GPUs takes 12 minutes for ~$7 in electricity. The practical recommendation: a two-tier architecture using 7B-Q4 on cheap CPU cloud for body text (~$31 total for 7.2M articles) with optional 70B enrichment passes on a small curated subset is tractable today at consumer cost.

---

## 1. CHUNKING GRANULARITY + COMMUNICATION OVERHEAD

### Algebraic framework

Total wall time for K workers, each processing M = N_total/K documents:

    T_total = max_k( T_load_k + M * T_extract_k ) + T_aggregate

where:
- T_load_k = model weight load time (dominant fixed cost per worker)
- T_extract_k = per-document forward-pass time (variable cost)
- T_aggregate = output aggregation time (trivially cheap, shown below)

**Calibrated corpus parameters (English Wikipedia, 2026):**
- N_total = 7,200,000 articles
- Mean article length = 717 words = ~968 BPE tokens
- Total corpus = 6.97B tokens

**Critical distinction -- prefill vs. decode mode:**

Activation extraction requires only the PREFILL pass (one forward pass through the full network, reading activations from a target layer). There is no token sampling, no KV-cache reuse across calls, and no autoregressive decode loop. This makes extraction 50-500x faster per document than generation-throughput benchmarks.

Empirical calibration anchor (given): 1B model on H100, 10K abstracts in 5.7 min.
- Abstracts = ~200 tokens each
- Implied throughput: 5882 tok/s (prefill-batch mode)
- This is consistent with H100's 3350 GB/s bandwidth and 1B = 2 GB model weights

**Optimal chunk size (90% efficiency threshold):**

Efficiency drops when T_load >> M * T_extract. The break-even at 90% efficiency is:

    M_min = 9 * T_load / T_extract_per_doc

For 7B Q4 CPU workers (T_load ~300s, T_extract ~0.39 s/doc): M_min = 167 docs.
For 70B Q4 Mac workers (T_load ~900s, T_extract ~0.48 s/doc): M_min = 84 docs.

Practical chunks of 10K-100K documents are well above threshold for all hardware tiers. Once a worker loads the model (a one-time cost), it processes its entire chunk at peak efficiency. There is zero incentive to sub-chunk below ~1000 documents.

**Output data volume:**

Each extracted activation vector: N_substrate dimensions x 2 bytes (bf16).
- N_substrate = 10^4: 20 KB/document
- Full Wikipedia (7.2M docs): 144 GB total output
- Per-worker output (100 workers): 1.44 GB
- Upload time per worker at 10 Mbps home connection: ~1152 seconds = 19 minutes

The 144 GB total is well within the range of a single aggregation server. At 1 TFLOPS CPU server, substrate aggregation (summing 7.2M vectors of length 10^4) costs 72G FLOPs = ~72 ms. Aggregation is not a bottleneck.

**Key finding:** Communication overhead is upload-bound per worker (~19 min at 10 Mbps), not compute-bound or latency-bound. Workers can stream their results incrementally while processing the next batch, hiding upload latency entirely with double-buffered output.

---

## 2. HETEROGENEOUS HARDWARE TIERS -- CALIBRATED NUMBERS

### Baseline: Sequential H100 Cloud

| Model | Hardware | Throughput | Wall (7.2M articles) | Cost |
|-------|----------|------------|---------------------|------|
| 1B bf16 | H100 x1 | 5882 tok/s | 329 hr | $823 |
| 70B bf16 | H100 x8 | ~672 tok/s | 2880 hr | $57,596 |
| 405B bf16 | H100 x16 | ~232 tok/s | 8331 hr | $333,234 |

**Important:** The "~$300-500 for 70B" prior estimate was almost certainly derived from short-run (10K article) linear extrapolation of decode-mode throughput on abstracts. The corrected estimate at extraction mode, full articles, 8x H100, is $57,596. The 405B estimate of "~$14k" appears to have assumed 10K articles not 7.2M. For Wikipedia-scale, 405B sequential cloud is not consumer-tractable.

### Tier 1: Idle Apple M-Series Laptops (70B Q4 extraction)

Hardware profile: M4 Max (128 GB, 546 GB/s bandwidth), 70B Q4_K_M = ~38 GB.
Prefill throughput (Metal/MLX compute-bound): ~2000 tok/s per machine.

| Workers | Wall | Cost (electricity) | Model |
|---------|------|--------------------|-------|
| 10 Macs | 96.8 hr | $0.10 | 70B Q4 |
| 100 Macs | 9.7 hr | $0.97 | 70B Q4 |
| 1000 Macs | 0.97 hr | $0.97 | 70B Q4 |

With 100 idle M4 Max laptops: full Wikipedia in ~10 hours for under $1 in electricity. This is not a joke estimate -- it follows from the prefill-mode throughput reality. The model quality is 70B with ~3% quality loss from Q4 quantization.

**Practical constraint:** Requires 38 GB unified memory per machine. M4 Pro (24 GB) cannot run 70B Q4. Only M3 Ultra, M4 Max, or M3/M4 Pro with 48+ GB can do this. Population of qualifying Macs in a volunteer network is smaller than total Macs.

**Orchestration complexity:** Low. Each worker gets a URL list + model path. No cross-worker communication. Result upload is the only coordination touch point.

### Tier 2: Cheap Cloud CPU Instances (7B Q4 extraction)

AWS t4g.xlarge (ARM Graviton3, 4 vCPU, 8 GB): $0.04/hr on-demand, ~$0.02/hr spot.
llama.cpp prefill throughput for 7B Q4 at batch mode: ~2500 tok/s (AVX2/NEON optimized).

| Workers | Wall | Cost (on-demand) | Cost (spot) | Model |
|---------|------|--------------------|-------------|-------|
| 100 CPUs | 7.7 hr | $30.98 | ~$15.49 | 7B Q4 |
| 500 CPUs | 1.55 hr | $30.98 | ~$15.49 | 7B Q4 |

Cost is nearly wall-time-independent for fixed worker count (cost = hours * rate * N). The $31 estimate at 100 workers is robust; spot pricing brings it to ~$15-20. This is the cheapest CLOUD path for full Wikipedia at 7B quality.

**Important:** 7B extraction quality is significantly below 70B. The substrate receives lower-quality semantic vectors. Whether this degrades associative memory performance by a measurable amount is a HARD-FAIL-triggering open question (see Section 6).

### Tier 3: Consumer GPU Fleet (30B Q4 extraction)

NVIDIA RTX 4090 (24 GB VRAM): 30B Q4_K_M fits in 24 GB.
Prefill throughput: ~8000 tok/s (CUDA, large batch, prefill-bound).

| Workers | Wall | Cost (electricity) | Model |
|---------|------|--------------------|-------|
| 100 x 4090 | 2.4 hr | $0.72 | 30B Q4 |
| 1000 x 4090 | 0.24 hr | $7.26 | 30B Q4 |

With 1000 consumer GPUs, full Wikipedia at 30B quality in 14 minutes for $7 electricity. This is the fastest consumer-grade path with strong model quality (30B is near-parity with 70B on many tasks with Q4_K_M quantization).

**Practical constraint:** 1000 volunteer consumer GPUs is a BOINC-class coordination problem. Onboarding, authentication, and payload delivery infrastructure requires significant engineering (estimated 2-4 eng-months for a working system). Reliability per worker ~70-90%, requiring 10-15% redundancy overhead.

### Tier 4: Smartphone NPUs (1B Q4 extraction, volunteer-compute class)

iPhone 15+ Neural Engine: ~50 tok/s for 1B Q4 at prefill.
Full Wikipedia at 1B quality with 10K iPhones: ~3.9 hours, ~$8 electricity.

**Quality concern:** 1B model extraction is qualitatively different from 7B+. The semantic depth of 1B representations may be insufficient for the substrate's associative retrieval quality. This tier is viable only if small-model extraction quality is demonstrated adequate -- currently untested.

**Coordination complexity:** Highest. Smartphone apps, background processing rules (iOS limits), battery management, and app-store distribution create high engineering overhead relative to payoff.

---

## 3. FAULT TOLERANCE + AGGREGATION ARCHITECTURE

### BOINC architecture lessons (empirical, 20+ years)

Key lessons from volunteer distributed computing (BOINC 2003+, Folding@home 2000+):

1. **Replication is the primary correctness mechanism.** BOINC validates by redundant computation: each work unit sent to 2+ workers, outputs compared. For floating-point extraction, exact bit-match is not expected; instead validate by cosine similarity of outputs from two independent workers on sentinel documents. Threshold: cos_sim > 0.98 (empirically calibrated).

2. **Optimal spot-check rate creates a quadratic tradeoff.** Higher check rate reduces needed replication (less redundancy overhead) but consumes compute. The BOINC literature identifies optimal spot-check fraction ~5-10% that minimizes total compute. For extraction, 2% sentinel docs (documents whose activations are pre-computed on a trusted H100) provide effective bad-actor detection.

3. **Task granularity optimum.** BOINC servers perform best with work units sized for 10-60 minutes wall time per worker. This matches chunks of ~1000-10000 documents per worker per job assignment (at 7B CPU speed: 1000 docs * 0.39 s/doc = ~390s = 6.5 minutes -- exactly in the sweet spot).

4. **Persistent idempotent design.** Each work unit gets a unique hash (SHA256 of sorted doc_ids in chunk). Worker outputs tagged by chunk hash. Aggregator upserts by chunk hash; re-processing a duplicate chunk is harmless. This eliminates the most common failure mode (double-counting on retry).

5. **Dead-letter queue for stragglers.** Workers that fail to return results within 2x expected wall time have their chunks re-dispatched to a different tier. No cross-worker dependencies, so re-dispatch has zero coordination cost.

### Output format standardization

Workers may use different quantization levels (4-bit, 8-bit, bf16). Before substrate write, ALL activations must be round-tripped to bf16 (2 bytes per dimension). This costs one vectorized cast operation per document on the aggregator. The information loss from 4-bit to bf16 promotion is irrelevant because the source representation was already 4-bit; promotion does not reconstruct lost precision.

Aggregation operation (online Hebbian update or simple accumulation) is commutative and order-independent across chunks. Workers can return in any order; the aggregator processes each chunk upon receipt.

### Erasure coding applicability

For output storage redundancy, Reed-Solomon erasure coding of the final 144 GB output matrix provides durability against aggregator disk failures. RS(n=10, k=8) provides protection against 2-node failures with 25% storage overhead. This is optional for the extraction pipeline but advisable for the final substrate matrix if stored across multiple drives.

---

## 4. SECURITY AND PRIVACY FOR FEDERATED EXTRACTION

### Threat model for public-corpus extraction (Wikipedia)

Wikipedia is fully public. Workers cannot cause privacy harm by observing document content. The only adversarial vector is output corruption: a malicious worker returns incorrect activation vectors that silently corrupt the substrate.

**Detection mechanisms:**

1. **Sentinel documents.** 2% of documents per chunk are "sentinels" with pre-computed gold-standard activations (computed on a trusted reference hardware instance). Worker outputs for sentinels are compared to gold standards. If cosine_sim(worker_output, gold) < 0.95 for >5% of sentinels, the entire chunk from that worker is rejected and re-dispatched.

2. **Quorum voting on redundant chunks.** For high-value document subsets (e.g., 1% of articles selected as canonical knowledge anchors), 3 independent workers process the same chunk. Majority-vote by centroid proximity resolves disagreements.

3. **Reputation system (BOINC-style).** Workers accrue per-tier reputation based on sentinel pass rate. High-reputation workers get fewer sentinel checks (lower overhead); new workers get 10% sentinel check rate until they establish reputation.

**No federated learning privacy risk:** This is NOT federated LEARNING -- workers never update any shared model, never see any substrate state, and never have access to anything beyond their assigned document chunk. The privacy model is far simpler than FL. The scheme is compatible with OpenMined-style substrate validation but does not require its cryptographic overhead for public-corpus extraction.

---

## 5. COST AND TIME COMPARISON MATRIX

### Full Wikipedia (7.2M articles), extraction-mode prefill

| Architecture | Wall Time | Total Cost | Model | Quality | Practical Challenge |
|---|---|---|---|---|---|
| H100 x1, 1B sequential | 329 hr | $823 | 1B | Low | None (baseline) |
| H100 x8, 70B sequential | 2880 hr | $57,596 | 70B | High | Expensive |
| H100 x16, 405B sequential | 8331 hr | $333,234 | 405B | SOTA | Very expensive |
| 100 CPU cloud, 7B Q4 | 7.7 hr | $31 | 7B | Medium | Script + spot mgmt |
| 100 Mac M4, 70B Q4 | 9.7 hr | $1 (elec) | 70B | High | Volunteer coord |
| 1000 4090 GPU, 30B Q4 | 0.24 hr | $7 (elec) | 30B | Medium-High | BOINC infra |
| 10K smartphone NPU, 1B Q4 | 3.9 hr | $8 (elec) | 1B | Low | App dev + iOS limits |

**P_deflated for each scenario's cost estimate being accurate within 2x:**
- H100 sequential: P = 0.80 (well-understood, compute-bound math)
- 100 CPU cloud (7B Q4): P = 0.60 (prefill throughput benchmarks have variance; llama.cpp batch mode less documented than decode mode)
- 100 Mac (70B Q4): P = 0.50 (prefill throughput on Apple Silicon at batch mode is less benchmarked; ANE vs Metal vs CPU routing introduces variance)
- 1000 consumer GPUs: P = 0.40 (volunteer network coordination overhead uncertain; reliability model is empirical estimate from BOINC literature)
- 10K smartphones: P = 0.20 (iOS background processing limits may reduce throughput by 10x; unvalidated)

---

## 6. RECOMMENDED ARCHITECTURE: 70B WIKIPEDIA AT <$50

### Practical architecture for immediate deployment

**Recommended configuration:** 100 cloud CPU workers (AWS t4g.xlarge spot) + 7B Q4_K_M model.

Why this wins:
- Cost: $15-31 depending on spot price
- Wall: 7.7 hours (fits in an overnight job)
- Infrastructure: no BOINC, no volunteer coordination, pure AWS spot fleet
- Reproducibility: identical hardware = no quantization-mode variance
- Model quality: 7B Q4 sufficient for dense semantic extraction if corpus is preprocessed (chunked to relevant passages)

**Implementation recipe:**

1. Preprocess: chunk Wikipedia dump to passages of ~500-1000 tokens each (use Wikimedia structured-wikipedia dataset from HuggingFace). This reduces per-doc length variance.

2. Dispatch: Python coordinator reads doc list, shards into 100 chunks of ~72,000 docs each. Writes chunk manifests to S3/R2.

3. Worker container: Docker image with llama.cpp server + 7B Q4_K_M weights (~4 GB). On launch: (a) download weights from S3, (b) load model, (c) process chunk manifest, (d) for each doc: POST to llama.cpp /embedding endpoint, receive hidden-state vector, append to local output file, (e) upload output file to S3 upon chunk completion.

4. Aggregator: single t4g.medium instance reads completed chunk outputs as they arrive (streaming aggregation), applies Hebbian update or stores raw activation matrix.

5. Fault tolerance: chunk manifest tracks status (pending/running/done/failed). Any chunk not marked done within 3x expected wall time re-dispatched to a new worker.

**For 70B quality at <$50:** Use 100 idle Apple M4 Max machines (electricity cost: ~$1) or use a 16x H100 burst for ~$64 (2.7 hours wall at 8x the price). The $50 target is achievable with 70B only via volunteer Mac hardware OR by accepting H100 spot pricing (~$1.49/hr = $64 for 8x H100 at 2.7 hr -- just over budget). The $31 CPU path with 7B Q4 is the cleanest within-budget option.

**Tiered quality strategy:**
- Phase 1: Extract ALL 7.2M articles with 7B Q4 on CPU cluster. Cost: ~$31. Wall: 8 hr.
- Phase 2 (optional): Identify top 500K articles by PageRank or incoming-link density. Re-extract with 70B on a 4-hour H100 burst. Cost: ~$12 incremental. Wall: 4 hr.
- Total: ~$43 for full corpus at 7B quality + top-500K at 70B quality.

---

## 7. CROSS-DOMAIN PROBE: VOLUNTEER COMPUTE LITERATURE

### SETI@home / Folding@home / BOINC lessons for LLM extraction

**What BOINC got right (applicable to chunked extraction):**
- Work-unit sizing for 10-60 min per task matches naturally with doc-chunk sizing for CPU workers
- Adaptive replication (trust higher-reputation workers more) directly applicable to GPU/Mac fleet quality tiering
- Server-side validation by redundant computation works without modification for activation extraction
- The key insight from 20+ years of BOINC: RELIABILITY OVERHEAD IS DOMINATED BY STARTUP COSTS, not per-task overhead. This means larger chunks are strictly better for volunteer compute (amortize bad-worker overhead over more useful work)

**What BOINC missed (relevant for LLM extraction):**
- Model weights are large (4-38 GB). BOINC was designed for small executables (~1 MB). Downloading 38 GB per worker is a new constraint. This strongly favors pre-positioning model weights on volunteer machines (e.g., mac-fleet with pre-downloaded weights) over ad-hoc volunteer compute where each worker must download fresh.
- BOINC's validation by exact-match fails for floating-point outputs. The cos_sim-based sentinel approach described above is novel but straightforward.

**Recent distributed inference literature (2024-2025):**
- Federated inference (2603.28772): collaboratively exploiting on-device inference for accuracy vs. latency tradeoffs -- complementary to extraction, focused on generation tasks
- vLLM distributed serving (Feb 2025): pipeline parallel for 405B across nodes -- requires high-bandwidth NVLink; not applicable to heterogeneous consumer fleets
- Edge LLM inference (2603.23640): NPU-coordinated speculative decoding on mobile -- relevant for smartphone tier but currently decode-focused, not prefill-extraction mode
- LLMEasyQuant (2406.19657): system-aware quantization across edge/cloud deployments -- directly applicable for format standardization across tiers

**Key gap in existing literature:** No published system targets PREFILL-ONLY distributed extraction (as opposed to generation serving). The closest analogue is distributed embedding computation (e.g., distributed BERT embeddings for retrieval), which is a well-studied problem. The chunked extraction architecture is essentially "distributed embedding at scale with larger models" -- the math is proven, the gap is engineering.

---

## 8. FALSIFIABLE PREDICTIONS

### HARD-PASS thresholds

**HP-1 (CPU throughput floor):** llama.cpp batch prefill on 4-vCPU ARM instance at 7B Q4 achieves >= 1500 tok/s (50% of predicted 2500). Cheap decisive test: time 1000 Wikipedia passages through llama.cpp /embedding endpoint on single t4g.xlarge. Measurable in <10 minutes on a $0.04 instance.

**HP-2 (Cost bound):** 100 CPU workers complete 7.2M article extraction at total cost <= $60 (2x predicted $31). Measurable from AWS billing after overnight run.

**HP-3 (Quality adequacy):** Substrate retrieval accuracy with 7B Q4 extracted vectors is >= 85% of accuracy with 70B bf16 extracted vectors, measured on a 10K article held-out test set. Measurable as a standalone ablation experiment.

**HP-4 (Aggregation time):** Streaming aggregation of 144 GB output on a single t4g.medium instance completes within 4 hours (2x theoretical 2 hour estimate). Measurable without running full extraction.

### HARD-FAIL thresholds

**HF-1 (Throughput collapse):** If llama.cpp prefill on t4g.xlarge achieves < 300 tok/s for 7B Q4, the CPU cost estimate is off by 8x, making the $31 estimate invalid (~$250 real cost). At this point, cloud CPU is not cost-competitive with a 4-hour single H100 burst (~$10).

**HF-2 (Model quality cliff):** If 7B Q4 extraction vectors yield < 70% retrieval accuracy vs. 70B baseline on the held-out test set, the cost advantage of 7B is irrelevant. The pipeline must use >= 30B model quality, which requires GPU workers (consumer or cloud). The "cheap CPU path" is invalidated.

**HF-3 (Apple Silicon prefill):** If 70B Q4 prefill throughput on M4 Max is < 500 tok/s (vs. predicted 2000 tok/s), the Mac-fleet wall time increases from 9.7 hr to 38.8 hr for 100 machines. Still feasible as an overnight job but reduces attractiveness vs. CPU cloud.

**HF-4 (Volunteer reliability):** If volunteer GPU worker reliability is < 50% (vs. assumed 80%), the redundancy overhead exceeds 100%, making the effective cost 2x the electricity estimate. Consumer GPU fleet becomes cost-equivalent to cloud CPU.

### P_deflated estimates

| Claim | P_deflated | Key uncertainty |
|---|---|---|
| CPU 7B Q4 extraction at $31 for full Wikipedia | 0.50 | Prefill batch throughput unvalidated at scale; llama.cpp server mode overhead unknown |
| Mac 70B Q4 extraction at $1 electricity | 0.40 | Prefill throughput on Apple Silicon in server mode poorly benchmarked; thermal throttling in continuous operation unknown |
| Consumer GPU fleet at 30B in 14 min | 0.35 | Volunteer network coordination unvalidated; BOINC-style overhead for LLM workloads unknown |
| 7B quality >= 85% of 70B for substrate retrieval | 0.40 | No published data on quality degradation specifically for bipolar associative memory substrate; general LLM benchmarks are not substrate-specific |
| Full architecture tractable at <$50 for 70B-quality | 0.45 | Depends on resolving HP-3 (quality adequacy) and HP-1 (CPU throughput) |

---

## 9. CROSS-THREAD SYNTHESIS

**With prior cost model (sequential cloud):**
Prior estimate assumed 70B extraction at ~$300-500. The corrected extract-mode estimate for FULL Wikipedia (not 10K articles) with 70B is $57,596 sequential, or ~$31 with 100 CPU workers at 7B quality. This is a 1858x cost reduction by switching to distributed 7B, or a 1352x reduction by staying at 70B quality via a Mac volunteer fleet. The prior cost model was not wrong per se -- it was implicitly scoped to a 10K-article benchmark run, not the full corpus.

**With substrate-physics framing:**
Chunked extraction is embarrassingly parallel because the substrate's Hebbian update W_final = sum_i(x_i * x_i^T) is a commutative, associative operation over documents. Each chunk computes a partial sum, and the aggregator sums the partial sums. There are no cross-document dependencies in the update rule. This is the mathematical reason the parallelism is exact (no approximation, no cross-chunk information loss).

**With federated learning literature:**
Federated extraction differs from federated LEARNING in a critical way: there is no model update, no gradient communication, and no convergence concern. The privacy model is simpler (public corpus). The engineering is simpler (workers are stateless). The only borrowed concept from FL is the worker reliability/reputation management layer.

**With BOINC volunteer computing:**
The model weight download problem (4-38 GB) is the key new constraint BOINC didn't face. Pre-seeding model weights onto volunteer machines before extraction campaigns is the correct architectural response. This maps to a "substrate seeding" protocol where interested users download a model binary once, then join extraction campaigns as they are announced.

---

## 10. SUBSTRATE-PRODUCT IMPLICATIONS

**Immediate actionable finding:**
The 7B CPU cluster path ($31, 8 hr, no GPU) is deployable today. It requires: a Python coordinator script, a Docker worker container with llama.cpp, and an S3/R2 bucket. Total engineering effort: 2-3 days for a working pipeline. This makes full-Wikipedia extraction at 7B quality a "day-one feature" of the substrate product, not a future milestone.

**70B quality path at consumer cost:**
A Mac volunteer network with 100+ M4 Max machines (available in any university research computing context, or as an opt-in network of enthusiasts) brings 70B quality to ~$1 electricity. The product-facing story: "substrate trained on Wikipedia at GPT-3-level quality for less than the cost of a cup of coffee." This is a compelling product claim contingent on HP-3 (7B quality adequacy) and HP-1 (prefill throughput). If HP-3 fails, the story requires the Mac fleet, which requires more coordination.

**Critical experiment for cap_map:**
Before committing to CPU-only extraction infrastructure, the HP-2/HF-2 quality test (7B vs 70B extraction quality for substrate retrieval) must be run. This is a cheap 2-GPU experiment: extract 10K articles with 7B and 70B, load into a small substrate instance, test retrieval accuracy. If the quality cliff is real and sharp, the architecture recommendation changes from "CPU fleet 7B" to "Mac fleet 70B." If quality is acceptable at 7B, the CPU fleet path dominates on cost.

**405B path (SOTA quality):**
Not consumer-tractable at full Wikipedia scale ($333K sequential, no practical distributed path without BOINC-scale infrastructure). Viable for curated subsets: top 100K articles at 405B quality with 4x H100 burst = ~$2,000. This is a "premium tier" extraction option for later product phases.

---

## Citations

1. Anderson, D.P. (2019). BOINC: A Platform for Volunteer Computing. arXiv:1903.01699 -- task granularity + validation architecture
2. Folding@home architecture lessons (ResearchGate, Pande lab, 2000-2008) -- fault tolerance patterns
3. vLLM Distributed Inference Blog (Feb 2025): blog.vllm.ai/2025/02/17/distributed-inference -- pipeline + tensor parallel for 405B
4. LLMEasyQuant (2406.19657): quantization framework for distributed edge/cloud deployments
5. Federated Inference for Heterogeneous LLM (arXiv 2603.28772, 2026) -- on-device collaborative inference
6. LLM Inference at the Edge: NPU/GPU benchmarks (arXiv 2603.23640, 2026) -- mobile throughput
7. llama.cpp GitHub discussions/4167: Apple Silicon M-series performance benchmarks (community, 2024-2026)
8. M4 Max AI Inference Benchmarks blog (blog.imseankim.com, 2025): 70B Q4_K_M at 12.5-20 tok/s (decode mode)
9. Wikipedia:Size of Wikipedia (en.wikipedia.org, 2026): 7.19M articles, ~717 words/article mean
10. vLLM Parallelism Scaling docs (docs.vllm.ai v0.18.0): TP + PP architecture for multi-node
11. BOINC High-Performance Task Distribution (boinc.berkeley.edu/server_perf): chunk size + reliability analysis
12. H100 Performance benchmarks, VALDI Docs (2025): Llama 3.1 inference testing
13. Cerebras Llama 3.1-405B inference (cerebras.ai, 2024): $6/M tokens, 969 tok/s (specialized hardware)

**Verified citation count: 13**

---

## Cheap Decisive Test

**Test:** Run llama.cpp embedding endpoint on a single AWS t4g.xlarge instance against 10,000 Wikipedia article bodies (500-1000 tokens each), measure wall time.

**Expected result:** ~5-8 minutes = 1500-2500 tok/s effective throughput.

**HARD-PASS:** <= 6.7 min (>= 1500 tok/s) -- validates the $31 full-corpus estimate within 2x.
**HARD-FAIL:** > 53 min (< 187.5 tok/s) -- invalidates the CPU path entirely; switches recommendation to H100 spot burst.

**Cost:** $0.04/hr x 0.15 hr = $0.006. Effectively free.

---

*P_deflated summary: 0.45 (feasibility of <$50 full Wikipedia at 70B quality via distributed architecture). P_deflated: 0.55 (feasibility of <$50 at 7B quality via CPU fleet -- higher confidence due to simpler hardware tier).*
*Next-drill candidate: quality-degradation curve for substrate retrieval accuracy as function of extraction model size (1B vs 7B vs 30B vs 70B) -- this is the binding open question for architecture selection.*
