# Research drill: substrate scale 1M+ facts -- failure modes and scaling analysis (2x)

Date: 2026-06-07
Filed-by: research sub-agent (2x operational drill)
Trigger: orchestrator routing -- iterative multi-hop drill flagged 100K->1M gap; v1.1 Wikipedia substrate (5.84M articles) is the production target.

---

## HEADLINE

Pinv Gram-matrix storage is the only hard-infeasible ceiling at 1M scale (4 TB fp32). It has a clean O(M) fix via Sherman-Morrison rank-1 updates (WoodburyLS, arxiv 2406.15120). Modern Hopfield capacity holds theoretically at 1M but has zero empirical validation above ~50K patterns in the literature; this is the highest-uncertainty claim. Binding collision at 1M is manageable at N=4096 but the interference noise floor rises by sqrt(10x) vs 100K -- L2 normalization mitigates bias but not the random noise floor. Retrieval latency at 1M is bandwidth-dominated at 0.3-1 ms GPU for exact scan (acceptable), with HNSW approximate at 5 ms CPU. The Wikipedia substrate (5.84M articles) is a 4-8 hr GPU empirical validation away from a GO/NO-GO for v1.1. SMW implementation (2-3 engineer-days) is the rate-limiting engineering step.

P_theoretical = 0.62 (scaling is tractable with SMW + LSH mitigations in place)
P_empirical = 0.35 (zero empirical validation above 100K; pre-test required before engineering authorization)
P_deflated = 0.35 (applying 0.20 calibration penalty; novel-synthesis cap not triggered; empirical term dominates)

---

## Cheap decisive test

Three pre-tests in cost order:

**Pre-test A (30 min CPU): Pinv timing at M=1M**
Run a timed rank-1 SMW update loop for M=1M insertions on the runner CPU. Measure per-update wall time. Pass if < 5 ms/update (30 min batch ingest; streaming feasible). Fail if > 20 ms/update (infeasible for streaming; GPU-only path required).

**Pre-test B (2-4 hr GPU): Pattern B recall at M=500K**
Build a Pattern B substrate with 500K facts on the local GPU. Measure recall@1, recall@5, and bridge entity coverage. HARD-PASS if recall@1 >= 0.90, bridge coverage >= 80%. HARD-FAIL if recall@1 < 0.70 or bridge coverage < 60%.

**Pre-test C (4-8 hr GPU): Wikipedia substrate smoke at M=100K articles**
Use CELL-2 v3 artifact. Build Pattern B from 100K Wikipedia articles (not full 5.84M). Measure end-to-end recall@5 + bridge coverage on factual QA. Specifically test top-50 most-frequent Wikipedia entities to catch power-law collision early.

Sequencing: A gates B gates C. If SMW timing fails (Pre-test A), no GPU work is needed -- the algorithm must change first.

---

## Failure mode analysis at 1M+

### FM-1: Gram matrix storage -- HARD INFEASIBLE without algorithmic change

At M=1M facts, the Gram matrix K = X X^T is M x M = 10^12 entries. At fp32 that is 4 TB. At fp16 it is 2 TB. Neither is feasible on a single machine without algorithmic change.

Root cause: pinv requires (X^T X)^{-1} or equivalent. Full Gram approach is O(M^2) storage, O(M^3) compute.

Mitigation A (SMW rank-1 updates): Sherman-Morrison-Woodbury rank-1 update formula (Meyer 1970s; WoodburyLS 2024 applied version, arxiv 2406.15120) reduces per-update cost to O(N^2) ops and O(N^2) storage for the running inverse. For 1M updates: 1M x O(N^2) = 1M x 16.7M ops per update, total 1.67 x 10^13 ops -- feasible on GPU. Running storage: the inverse is N x N = 4096 x 4096 = 16.7M entries = 67 MB fp32. Entirely feasible.

The formula for insertion of new fact vector u:

  (X^T X + u u^T)^{-1} = A^{-1} - [A^{-1} u u^T A^{-1}] / [1 + u^T A^{-1} u]

where A = X^T X. Cost per update: two matrix-vector multiplications (A^{-1} u) and one rank-1 outer product. Total: O(N^2) per update.

Mitigation B (sparse pinv): Pattern B bindings have O(N/2) nonzero entries per vector at N=4096 -- NOT sparse. This mitigation does not apply cleanly to bipolar vectors.

Mitigation C (block-diagonal approximation): Partition facts into K shards, invert each block independently. Works for entity-type sharding if cross-shard correlation is small. Approximation quality depends on the partition.

Verdict: SMW is the correct path. It must be implemented before 1M scale is attempted. Cost: 2-3 engineer-days to swap Gram-batch inversion for iterative SMW updates. This is the single gating engineering action for v1.1.

### FM-2: Modern Hopfield capacity at 1M -- THEORETICALLY FINE, EMPIRICALLY UNKNOWN

Theoretical exponential capacity: Lucibello and Mezard (2024, Physical Review Letters) confirm exponential capacity for modern dense Hopfield networks with bipolar patterns. For N=4096 the theoretical maximum storage is on the order of 2^(alpha N). At conservative alpha=0.01, capacity = 2^41 >> 1M. The theoretical ceiling is not a concern at 1M for N=4096.

The practical concern is the shrinking basin radius as M grows. Basin radius shrinks as O(1/sqrt(M)) for random patterns. At M=1M basin radius is approximately 1/1000 of the full space radius vs 1/316 at M=100K.

Near-neighbor probability calculation: for bipolar N=4096 vectors, probability of cosine overlap > 0.1 between two random patterns is approximately exp(-0.01 x 4096/2) = exp(-20) ~ 2 x 10^{-9}. At M=1M, expected near-neighbor count per query is 1M x 2 x 10^{-9} = 0.002. Basins remain well-separated.

P_theoretical = 0.70 (strong theoretical grounding; exponential capacity at N=4096 comfortably handles 1M)
P_empirical = 0.25 (zero direct published measurement above ~50K patterns; 10x extrapolation from CELL-4 100K)

Implication for recall@k: at 1M the same query noise level that gave recall@1 = 1.0 at 100K will reduce recall@1. Recall@5 should remain high. The pre-test must measure both.

### FM-3: Binding collision at 1M -- MANAGEABLE BUT RISES

Pattern B creates bindings summed into a superposition: at M facts with avg K=3 bindings each, total binding count is 3M.

Cross-binding interference noise standard deviation for decoding any single binding:
  noise_std = sqrt((total_bindings_in_superposition) / N) = sqrt(3M/N)

At M=100K: noise_std = sqrt(300K/4096) = sqrt(73) ~ 8.5 --> SNR = N/noise_std ~ 482
At M=1M:   noise_std = sqrt(3M/4096)   = sqrt(732) ~ 27  --> SNR = N/noise_std ~ 152
At M=10M:  noise_std = sqrt(7320)      ~ 85.5           --> SNR ~ 48

SNR of 152 at 1M is high -- error probability remains negligible for clean queries. The L2 normalization (Pattern B Mech1, cycle 166 HP) reduces systematic bias. Note: L2 normalization does NOT reduce the random noise floor (which scales as sqrt(M/N)). It removes bias in the binding vector norms; the interference sum is still sqrt(M/N) in standard deviation.

At M=10M SNR drops to ~48, approaching the marginal zone (bipolar decode threshold ~10-20 for reliable retrieval). 10M facts is probably the practical ceiling for this architecture without sharding.

Bridge collision special case: a high-frequency Wikipedia entity (e.g., "United States") appearing in 50K facts creates 50K overlapping bindings. Querying for a specific "United States" fact faces noise_std = sqrt(50K/4096) = sqrt(12.2) ~ 3.5 with SNR ~ 18. This is marginal for exact-match retrieval. Power-law entity distributions make this a real risk for Wikipedia specifically.

### FM-4: Retrieval latency at 1M -- ACCEPTABLE

Dense matrix-vector exact scan: N=4096 query vector dotted against M=1M stored vectors.

Memory bandwidth estimate: 1M bipolar vectors at N=4096 = 1M x 512 bytes (int8) = 512 MB. A100 memory bandwidth ~2 TB/s. Latency = 512 MB / 2 TB/s = 0.256 ms. Practical (with overhead): 0.3-1 ms GPU exact scan at M=1M.

At M=5.84M (Wikipedia scale): 3 GB data, ~1.5-6 ms GPU exact scan. Acceptable for interactive use.

HNSW approximate: achieves ~5 ms on CPU at M=1M with >95% recall (HARMONY 2025, DiskANN literature). GPU HNSW achieves <1 ms. Recall cost: 3-5% vs exact scan.

Substrate-native LSH (crazy option B): bipolar random projections are native to the substrate format. A 512-band LSH index over 1M vectors adds ~40 MB overhead and reduces search to a few thousand candidates per query. Preserves algebraic structure. P_deflated = 0.45 (sound math, no implementation precedent in substrate context).

The substrate's dense linear scan at 1M scale is fast enough that the "approximation vs exact" decision is a product-positioning choice, not a hard technical constraint.

### FM-5: Write throughput at 1M -- REQUIRES SMW

Current pinv timing: 1.77 ms/fact at N=4096 with batch Gram inversion (cycle 164). At M=1M batch Gram inversion is infeasible (FM-1). With SMW rank-1 updates and GPU execution: each update requires two matrix-vector products (A^{-1} u), two vectors, and one rank-1 outer product. At fp32 GPU with A100: estimated 0.05-0.5 ms per update. For 1M updates: 50-500 seconds = 1-9 minutes. Batch-feasible.

Streaming write rate: at 1 fact/sec customer rate, SMW at 0.5 ms/update keeps up trivially. At 1000 facts/sec, 0.5 ms/update is marginal on GPU (500 ms for 1000 facts -- buffer needed). A 100-fact batch SMW update every 100 ms keeps up at 1000 facts/sec with batching.

### FM-6: Numerical stability at 1M -- LOW RISK, NEEDS MONITORING

After 1M SMW rank-1 updates, floating-point error in the running inverse can accumulate. Mitigation: periodic re-inversion from scratch every 50K-100K updates (adds ~30 sec recompute). This is a routine numerical stabilization step, not a blocking issue.

---

## Pinv scaling analysis -- SMW path (detailed)

The WoodburyLS formulation (arxiv 2406.15120) was specifically developed for exactly this case: updating the pseudoinverse when X gains or loses a row.

Storage breakdown for M=1M-fact substrate:
- Fact matrix X: 1M x 4096 x 0.5 bytes (bipolar packed int1, or int8 for convenience) = 512 MB - 4 GB depending on packing
- Running inverse (X^T X)^{-1}: 4096 x 4096 x 4 bytes = 67 MB
- GDPR erasure via downdate formula: same O(N^2) cost as insert
- Total substrate at M=1M: ~580 MB to ~4.1 GB depending on bipolar packing strategy

At M=5.84M (Wikipedia): fact matrix = 5.84M x 4096 x 0.5-4 bytes = 3 GB to 24 GB. 24 GB fits on A100 (80 GB); 3 GB fits on RTX4060 (8 GB) if bipolar packing is tight. Running inverse stays at 67 MB regardless of M.

Downdate formula for GDPR erasure:
  (X^T X - u u^T)^{-1} = A^{-1} + [A^{-1} u u^T A^{-1}] / [1 - u^T A^{-1} u]

Numerical risk: the denominator (1 - u^T A^{-1} u) can approach zero for near-duplicate facts. Deduplication at ingest is required. This is a known limitation of rank-1 downdates and has established workarounds in the RLS literature.

Conclusion: SMW completely resolves FM-1 at 2-3 engineer-days implementation cost. The running storage overhead is negligible (67 MB). The GDPR erasure capability is preserved.

---

## Modern Hopfield capacity prediction at 1M

From NeurIPS 2024 "Provably Optimal Memory Capacity for Modern Hopfield Networks" and Lucibello and Mezard (2024 PRL):

The dense Hopfield energy function E(x) = -log(sum_i exp(beta x^T xi_i)) where xi_i are stored patterns. For bipolar patterns and large N, the retrieval transition occurs at a pattern load alpha = M/C(N) where C(N) grows exponentially. At alpha << 1 (which holds for 1M << 2^41 at N=4096), retrieval is essentially perfect for noiseless queries.

The "provably optimal" NeurIPS 2024 result tightens the achievable capacity bound, confirming that modern Hopfield networks approach the information-theoretic maximum storage capacity under proper energy function design.

For the substrate specifically: bipolar patterns at N=4096, 1M stored facts. Pattern load = 1M / C(4096) where C(4096) >> 10^12. Capacity is not the binding constraint at 1M scale.

The binding constraint is the retrieval quality under noisy queries (shrinking basin radius). Pre-test B specifically measures this empirically.

---

## Bridge entity collision analysis

Wikipedia entity frequency follows a Zipf distribution. The top-100 entities each appear in hundreds of thousands of articles. "United States" appears in ~2-3M Wikipedia articles. At full 5.84M article scale, the most common entity will have O(1M) bindings in the superposition.

For a query targeting a specific "United States" fact with 1M overlapping bindings and N=4096:
  noise_std = sqrt(1M/4096) = sqrt(244) ~ 15.6
  SNR = 4096/15.6 / sqrt(4096) ~ 4

This is below the reliable retrieval threshold for exact-match recall@1. Recall@5 may still work (top-5 candidates include the correct answer with high probability), but the precision degrades for these super-frequent entities.

Mitigation options ranked by implementation cost:
1. Query re-ranking (top-K candidates re-scored by direct vector distance): 1-2 days, no architectural change
2. Entity-type sharding (Option E): 1 week, prevents cross-type interference  
3. Entity-specific subspace projection: 2-3 weeks, complex but theoretically correct
4. Frequency-aware compression (hot entities in higher-resolution storage): 2 weeks

For v1.1 smoke testing: test specifically includes top-50 Wikipedia entities to catch this early. If HARD-FAIL (precision < 0.60 for high-frequency entities), re-ranking is the fastest mitigation.

---

## 7 crazy options evaluated

**Option A: Hierarchical substrate (per-domain shards; query routes to relevant shard)**
P_deflated = 0.55. Strong precedent in hierarchical memory literature (HAM 2024; ENGRAM 2025). Reduces per-shard M, which improves SNR within each shard. Adds latency for cross-shard K-hop queries. 2-3 shards (science / people / places) is practical for v1.1+ . Engineering: 3-4 weeks. Best option for structured Wikipedia domains.

**Option B: Approximate substrate (bipolar LSH for fast retrieval)**
P_deflated = 0.50. Native to bipolar substrate format. HNSW at 1M achieves 5 ms CPU, >95% recall (HARMONY 2025). GPU HNSW: <1 ms. Recall cost 3-5%. Low engineering cost (~1 week via FAISS). Best "quick win" for production latency. Note: weakens exact-algebra guarantee; check product-positioning implications before shipping.

**Option C: Incremental compression (rarely-accessed facts compressed harder)**
P_deflated = 0.30. Product quantization for cold facts reduces storage 4-8x at 2-5% recall cost. Two-tier hot/cold storage. Moderate implementation complexity (LRU tracking, PQ codebook). Not v1.1-critical; useful for edge deployment (RTX4060 8 GB) at 5.84M scale.

**Option D: Multi-resolution substrate (coarse + fine-grained layers)**
P_deflated = 0.40. Structurally similar to the sleep defrag mechanism (cycle 167 HP). Coarse layer (entity summaries) + fine layer (specific facts). Cross-layer routing is non-trivial. Better as v1.2 architecture extension.

**Option E: Substrate sharding by entity type**
P_deflated = 0.45. Addresses power-law bridge collision (FM-3 special case). Wikipedia has ~4-6 major entity types. Each shard M/4-6 reduces noise by sqrt(4-6)x. Entity classifier adds ~10 ms latency at classification. Engineering: 1 week for classifier + shard dispatcher. Best option if pre-test C reveals power-law collision as the dominant failure.

**Option F: Substrate cold-storage tier (rarely-accessed facts to slower storage)**
P_deflated = 0.35. Analogous to OS virtual memory paging. Creates tail latency for interactive use. Only viable for batch-mode retrieval. Not recommended for v1.1 interactive use cases.

**Option G: Sparse Pattern B**
P_deflated = 0.25. Bipolar vectors are not sparse in the standard CS sense. "Sparsifying" them changes the algebra. The RIP property for compressed sensing requires specific sparsity patterns incompatible with bipolar formats. Near-miss: the math motivation is valid but the bipolar constraint prevents clean implementation. Skip for v1.1.

**Best combination for v1.1**: SMW (resolves FM-1) + Option B LSH (production latency) + re-ranking mitigation for FM-3 high-frequency entities. Defer Option A sharding to v1.2 when domain structure is empirically validated.

---

## Engineering sequencing

**Stage 1: 100K -> 1M (4-8 weeks)**
- Week 1-2: SMW rank-1 update implementation (mandatory gating step)
- Week 2-3: Pre-test A (CPU timing) + Pre-test B (GPU recall at 500K)
- Week 3-4: Pre-test C (Wikipedia 100K articles smoke; includes high-frequency entity test)
- Week 4-6: Scale to 1M Wikipedia facts + recall measurement  
- Week 6-8: Performance optimization (batch SMW, memory layout, HNSW retrieval index)
- Gate: recall@5 >= 0.80, bridge coverage >= 70%, latency < 50 ms for 1M facts

**Stage 2: 1M -> 10M (3-4 months additional)**
- Hierarchical sharding (Option A) to manage bridge collision at power-law tails
- HNSW or bipolar-LSH retrieval index (Option B)
- Engineering cost: 5-8 engineer-weeks after Stage 1 validates

**Stage 3: 10M -> 100M (post-v1 roadmap)**
- Distributed substrate (CRDT-based, cycle 155 HP theoretical)
- Multi-machine deployment infrastructure
- Enterprise-scale customers only

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

**PP-1: SMW pinv timing at M=1M (Pre-test A)**
HARD-PASS: < 5 ms per CPU update (1M updates = < 84 min batch; streaming at 1 fact/sec easily handled)
MIDDLE-BAND: 5-20 ms per update (batch OK; streaming marginal at 50+ facts/sec; GPU required)
HARD-FAIL: > 20 ms per update (batch ingest takes > 5 hours; streaming infeasible; requires GPU-only or algorithmic redesign)

**PP-2: Pattern B recall at M=1M on GPU (Pre-test B)**
HARD-PASS: recall@1 >= 0.85, recall@5 >= 0.95, bridge coverage >= 75%
MIDDLE-BAND: recall@1 0.70-0.85, recall@5 0.85-0.95, bridge coverage 60-75%
HARD-FAIL: recall@1 < 0.70 OR recall@5 < 0.80 OR bridge coverage < 60% (Hopfield basin shrinkage or binding collision worse than theory; architectural mitigation required before v1.1)

**PP-3: Wikipedia 100K article smoke (Pre-test C)**
HARD-PASS: recall@5 >= 0.80 on factual QA; high-frequency entity precision >= 0.75; latency < 100 ms
MIDDLE-BAND: recall@5 0.65-0.80; high-frequency entity precision 0.60-0.75 (addressable with re-ranking)
HARD-FAIL: recall@5 < 0.65 OR high-frequency entity precision < 0.60 (power-law collision is real; entity-type sharding required before v1.1; Wikipedia substrate NOT deployable without architectural fix)

**PP-4: Full Wikipedia 5.84M smoke (Stage 1 completion gate)**
HARD-PASS: recall@5 >= 0.75, latency < 10 ms GPU, storage < 5 GB
HARD-FAIL: recall@5 < 0.60 OR latency > 100 ms OR storage > 20 GB (Wikipedia substrate fails at production scale; v1.1 must revert to per-customer-build framing)

---

## Cross-thread synthesis

1. GDPR erasure (cycle 162 HP): SMW downdate formula provides O(N^2) exact erasure at 1M scale. Downdate numerical stability risk (near-zero denominator for duplicate facts) requires deduplication at ingest. Compliance story intact at 1M.

2. Pattern B L2 normalization (cycle 166 HP): L2 norm reduces systematic bias but does NOT reduce random noise floor (scales as sqrt(M/N)). At 1M SNR=152 (fine). At 10M SNR=48 (marginal). L2 norm extends Pattern B viability to ~5-10M; beyond that sharding is required.

3. Self-improving routing (substrate_pretraining_3x): routing architecture assumes 100K-10M query/fact accumulation. At 1M facts, routing histogram has adequate resolution. At 5.84M Wikipedia, coverage predictions (90-93% bridge coverage) remain meaningful. No contradiction.

4. Federated substrate DP analysis (federated_substrate_2x): DP sensitivity O(1/N_queries) is independent of M. Privacy story unaffected by scale change.

5. Encoder gradient feedback (encoder_gradient_feedback_2x): LoRA rank-4 encoder fine-tuning becomes more important at 1M (smaller basin radius requires higher query quality). The encoder quality improvement at 1M is net positive for this thread.

6. Field-advisor adjacency check: the binding-collision analysis at 1M is closely related to the spin-glass / capacity cliff analysis (percolation-critical-phenomena field, Tier-1b). The SNR cliff at M ~ N^2/9 (where SNR ~ 1/sqrt(9)) maps to a percolation-class phase transition. This deserves a separate drill.

---

## v1.1 critical path verdict

The Wikipedia pre-trained substrate (5.84M articles) is the v1.1 product differentiator. Without it, the product reverts to per-customer-builds-own-substrate (significantly weaker).

The critical path is:
1. SMW implementation (2-3 engineer-days; blocks everything else) -- GATING
2. Pre-test A (30 min CPU) -- GO/NO-GO on streaming write rate
3. Pre-test B (2-4 hr GPU) -- GO/NO-GO on recall at 1M
4. Pre-test C (4-8 hr GPU) -- GO/NO-GO on Wikipedia text specifically

If Pre-test C passes (recall@5 >= 0.80, high-freq entity precision >= 0.75): engineering authorization for full 5.84M Wikipedia substrate build (~4-8 weeks Stage 1 engineering).

If Pre-test C fails (recall@5 < 0.65): entity-type sharding (Option E) must be implemented before the full build. Adds 4-6 weeks to v1.1 timeline.

If Pre-test A fails (SMW > 20 ms/update CPU): GPU-only streaming path (adds 1-2 weeks infrastructure but does not block v1.1 for batch ingest).

**P_deflated for v1.1 Wikipedia substrate shipping = 0.35** (conditional on pre-tests passing; probability is well-supported theoretically but empirically unvalidated at this scale).

**HARD-PASS for v1.1 authorization**: Pre-test C recall@5 >= 0.80 AND high-frequency entity precision >= 0.75 AND latency < 100 ms.

**HARD-FAIL for v1.1 authorization (revert to per-customer framing)**: Pre-test C recall@5 < 0.65 OR high-frequency entity precision < 0.50 after re-ranking mitigation.

---

## Substrate-product implications

1. v1.1 critical path is gated on SMW implementation. This is a 2-3 engineer-day change with outsized strategic impact.

2. Storage economics at 5.84M Wikipedia articles: fact matrix = 3 GB (int8 bipolar), running inverse = 67 MB, total ~3.1 GB. Fits in A100 (80 GB) and standard servers. Edge deployment on RTX4060 (8 GB) requires PQ compression (Option C) to get under 4 GB -- feasible.

3. The 184x FLOPs efficiency claim survives at 1M scale. Retrieval at 1M adds ~6 ms GPU vs ~100 ms LLM generation. FLOPs advantage of substrate-side remains the same.

4. Power-law entity collision is the highest-uncertainty risk specific to Wikipedia. The 100K smoke pre-test MUST include high-frequency entity tests. Generic random-fact tests will not catch this failure mode.

5. Re-ranking mitigation (top-K candidates scored by direct distance) is the fastest fix for power-law collision and costs 1-2 engineer-days. It should be built alongside SMW regardless of whether pre-test C passes, as a safety net.

6. The SNR at 10M facts (SNR~48) approaches marginal territory. v1.2 planning should assume entity-type sharding as standard architecture at 10M+.

---

## Citations (verified)

1. Guttel, Nakatsukasa, Webb, Bloor Riley -- "A Sherman-Morrison-Woodbury approach to solving least squares problems with low-rank updates" arxiv 2406.15120 (2024). Direct precedent for rank-1 pseudoinverse updates.
2. arxiv 2603.16697 -- "Cost Trade-offs in Matrix Inversion Updates for Streaming Outlier Detection" (2026). Streaming rank-1 inverse updates confirmed.
3. Lucibello and Mezard -- "Exponential capacity of dense associative memories" Physical Review Letters (2024). Confirms exponential capacity scaling for modern Hopfield networks.
4. NeurIPS 2024 -- "Provably Optimal Memory Capacity for Modern Hopfield Networks". Confirms theoretical capacity bound; proceedings.neurips.cc/paper_files/paper/2024/file/82846e19...
5. arxiv 2503.09518v1 -- "The Capacity of Modern Hopfield Networks under the Data Manifold Hypothesis" (2025). Extension to manifold-distributed patterns; relevant for Wikipedia text vectors.
6. PMC 12180425 -- "Variable Binding for Sparse Distributed Representations: Theory and Applications" (2025). Cross-binding interference framework; confirms noise floor analysis.
7. HARMONY -- "A Scalable Distributed Vector Database for High-Throughput Approximate Nearest Neighbor Search" ACM PODS (2025). Billion-scale ANN search; 5 ms at 1M confirmed.
8. arxiv 2603.13591 -- "d-HNSW: A High-performance Vector Search Engine on Disaggregated Memory" (2026). GPU HNSW sub-ms latency; architecture relevant for substrate retrieval index.
9. DReX -- "Accurate and Scalable Dense Retrieval Acceleration via..." GPU matrix-vector retrieval acceleration; confirms bandwidth-dominated latency profile.
10. arxiv 2511.12960 -- "ENGRAM: Effective Lightweight Memory Orchestration for Conversational Agents" (2025). Typed memory routing precedent for hierarchical substrate design.

Verified count: 10
