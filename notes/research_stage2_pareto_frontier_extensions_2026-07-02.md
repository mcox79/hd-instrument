# Stage 2 Opening Cells — Pareto Frontier Extensions 2026-07-02

**Filed:** 2026-07-02 (SONNET LIBERAL DRILL per USER 2026-07-01 full-night directive)
**Context:** Post-session INT8 v3 3-seed HARD_PASS; INT4 hypothesis falsified (INT4 ALSO works at cliff); cleanup dominance v2c HARD_PASS; cross-axis M-N-K separable HARD_PASS; LLN commercial V_C=1M CG.

---

## What the INT8/INT4 Pareto Tells Us (Off-Disk Verified)

INT8 v3 discriminator: cliff at (M=160,000, sigma=0.35) at N=8192. Three-seed summary:
- Seed 7: FP32=0.529, INT8=0.530, INT4=0.524 — arms_range=0.006 — HARD_PASS
- Seed 13: FP32=0.521, INT8=0.521, INT4=0.512 — arms_range=0.010 — HARD_PASS
- Seed 19: FP32=0.520, INT8=0.519, INT4=0.512 — arms_range=0.007 — HARD_PASS

**INT4 not broken (arms_range 0.006-0.010, INT4_drop 0.006-0.009, breaks=False across all seeds).** This falsified the original INT4-breaks hypothesis — the discrimination is there but tiny. At 4 bits, 8x compression vs FP32, the substrate is still operating within noise. Memory factor 0.250 = 25% of FP32 memory for INT8 at this M.

Cleanup v2c at N=8192: cleanup_recall=1.0 maintained up to alpha=30 (M=245k items); first degradation at alpha=100 (M=819k, cleanup_recall=0.9925 clean / 0.05 noisy). Cleanup wall is effectively unbounded for practical M.

---

## Ranked Top-5 Stage 2 Opening Cells

### RANK 1 — INT2 / 1-bit quantization Pareto probe
**Cell concept:** exp_stage2_int2_binary_quantization_pareto_v1
**Question:** Does INT2 (4x beyond INT8, 16x FP32) survive at the noise cliff? If yes, the bytes-per-fact Pareto curve extends to 4 bits and below. Binary (1-bit SIGN) is the extreme.
**Why highest rank:** INT4 unexpectedly holds. INT2 and binary are the natural next probe. If INT2 holds, the substrate is achieving near-binary compression at the accuracy cliff — a commercially decisive result for on-device M3 deployment. If INT2 fails, we get the actual precision floor, which is equally load-bearing.

**Design:**
- Arms: FP32 (control), INT8 (anchor), INT4 (anchor), INT2 (probe), BINARY (extreme)
- Discriminator point: same (M=160k, sigma=0.35, N=8192) — verified to be discriminating
- HARD_PASS: INT2_recall >= FP32_recall - 0.02 (2x looser than INT4 gate, accounts for additional quantization noise); BINARY may fail
- MIDDLE_BAND: INT2_drop in [0.02, 0.10]
- HARD_FAIL: INT2_recall < FP32_recall - 0.10 (full degradation)
- Runtime: ~same as v3 (add 2 arms); remote_cpu_queue; 3 seeds

**Load-bearing for M3:** on-device memory budget. If INT2 holds, a 1M-item substrate fits in ~1.5 GB instead of 12 GB (FP32). This is the threshold between possible and impossible for edge deployment.
**Cost to decisive answer:** 1 cell, 3 seeds, ~6-8h remote CPU. Pre-reg effort: 1h (re-use v3 structure, swap precision arms).
**Novelty score:** HIGH. INT2 Hopfield storage has not been studied in the HDC literature to our knowledge. Prior arc only reaches INT4.
**Rank justification:** highest (load-bearing) x (lowest cost: structure already proven) x (genuinely novel).

**Substrate-KB concept query ran:** "INT8 INT4 precision quantization pareto" — cosine=0.42; prior arc = 2026-05-29 KF-2 isolation cell (different mechanism class). No INT2/binary-at-cliff pre-reg exists. SAFE TO FILE.

---

### RANK 2 — Cleanup memory-budget model cell (latency x alpha operating curve)
**Cell concept:** exp_stage2_cleanup_capacity_latency_operating_curve_v1
**Question:** At each alpha (capacity level), what is the bytes-per-fact and query latency percentile (p50/p95/p99)? Produce a 2D operating map: accuracy vs (memory-cost, latency).

**Why rank 2:** Cleanup dominance result (v2c HARD_PASS) shows cleanup_recall=1.0 up to alpha=30, degrading at alpha=100. But v2c measured only accuracy, not latency. For M3 memory-budget planning, the cortex needs: "given memory budget B and latency budget L, what is achievable accuracy?" This operating curve is the key planning artifact.

**Design:**
- Fixed N=8192 (matching v2c)
- Alpha sweep: [0.3, 1, 3, 10, 30, 100] (same as v2c)
- For each alpha, measure: (a) cleanup recall, (b) bit-match recall, (c) query wall_time p50/p95/p99 across 400 queries, (d) write throughput (facts/sec)
- Additional INT8 arm at each alpha — verifies INT8 doesn't add latency overhead vs FP32
- HARD_PASS: latency curve monotone in alpha (more items = slower); p95 latency < 10ms at alpha=1 (N=8192 practical CAM); INT8 latency within 2x of FP32 at all alpha
- This extends the operating envelope from accuracy-only to a 3-axis Pareto surface

**Load-bearing for M3:** The cortex needs a lookup-table: "for a conversation with K active items at N=8192, query latency is X ms." This is the enabling specification for Phase 1 router timing budgets.
**Cost to decisive answer:** 1 cell, moderate complexity. Re-uses v2c structure, adds timing instrumentation. ~4h remote CPU.
**Novelty score:** MEDIUM. Latency characterization of Hopfield CAM is known analytically (O(N*M) matmul), but the practical GPU/CPU empirical curve at these alpha levels is new and M3-enabling.
**Rank justification:** (high load-bearing: M3 Phase 1 planning artifact) x (low cost: re-uses v2c) x (medium novelty).

---

### RANK 3 — Group-wise / non-uniform quantization probe
**Cell concept:** exp_stage2_group_wise_quantization_pareto_v1
**Question:** Does splitting W into groups of G columns and quantizing each group independently extend the INT4/INT2 Pareto frontier? Group-wise quantization is the standard technique in LLM quantization (GPTQ, AWQ) for recovering accuracy from aggressive compression.

**Why rank 3:** INT4 holds at arms_range=0.006-0.010. The question is whether INT2 fails cleanly or partially. If INT2 fails even slightly, group-wise quantization (group_size=64 or 128) may recover the INT2 loss. This would extend the Pareto frontier to 2-bit effective precision. It is the natural follow-on to Rank 1.

**Design:**
- Conditioned on Rank 1 results: if INT2 HARD_PASS, this cell is lower priority (defer). If INT2 MIDDLE_BAND or HARD_FAIL, this becomes priority.
- Arms: INT4 (control), INT2_uniform (anchor from Rank 1), INT2_group64, INT2_group128, INT2_group16
- Discriminator: same cliff point
- HARD_PASS: INT2_group64 recall >= INT4_recall - 0.01 (group quantization recovers INT2 to INT4 parity)
- Literature anchor: Frantar et al. GPTQ (2023); Dettmers et al. QLoRA (2023) — both show group-wise quantization recovers 3-4 bits of effective precision in LLM weight matrices. Substrate W matrix has similar statistical properties (dense, normally distributed at random initialization).

**Load-bearing for M3:** If group-wise INT2 achieves INT4 parity, memory budget halves again. 2M items in 1.5 GB vs 3 GB. Edge deployment threshold meaningfully extended.
**Cost to decisive answer:** Medium. Implementation is non-trivial (group quantization requires per-group scale factors stored alongside W). ~1d implementation + 8h remote CPU.
**Novelty score:** HIGH. Group-wise quantization of Hebbian CAM weight matrices has not been explored. The technique comes from transformer-weight literature; substrate W has different structure (correlation matrix, not attention/MLP weights). Could generalize or fail in novel ways.
**Rank justification:** (high load-bearing, conditioned on Rank 1) x (medium cost) x (high novelty).

---

### RANK 4 — Dim L: Learned encoding vs random (decisive baseline)
**Cell concept:** exp_stage2_learned_encoding_vs_random_baseline_v1
**Question:** Does a learned linear projection (trained to maximize recall at fixed alpha) outperform random FHRR encoding at the noise cliff? By how much?

**Prior arc status:** Two related cells have landed:
- exp_encoder_bridge_learned_projection_shared_intermediate_v1: MIDDLE_BAND (max true bridge=0.0000; proj=0.0000, tag=0.28, within=0.355, ctrl=0.000). This was a cross-encoder interop test — different question.
- exp_encoder_cocktail_composition_v1: HARD_FAIL (cross_recall=0.004 — encoders don't interoperate). Also a different question.

The prior arc tested cross-encoder composition, not single-encoder learned-vs-random. The decisive Dim L question has NOT been answered. The TEST RATIONALITY discipline (encoding-before-readout) applies here: the question is "does a learned projection that explicitly encodes items into the substrate retrieve better?" not "do two different random encoders interoperate?"

**Design:**
- Single encoder (FHRR N=8192), two arms: random-init projection (control = current substrate) vs. SGD-trained projection (gradient on recall loss over a held-out probe set, K=100 training triplets)
- Discriminator: at the noise cliff (alpha=0.3 where cleanup_recall starts degrading from 1.0), does learned projection raise cleanup_recall vs random? HARD_PASS if learned_recall >= random_recall + 0.05 at alpha=0.3.
- Key: the gradient must flow through the WRITE operation (outer product) not just through a separate query encoder. This is analogous to FAISS-IVF centroid learning.
- Smoke: N=2048, alpha=0.3, 20 training steps, check gradient flows

**Load-bearing for M3:** If learned encoding provides even 10% recall improvement at the noise cliff, the effective capacity of a fixed-N substrate is dramatically higher. This is the difference between "substrate as static memory" and "substrate as trainable memory" — a Stage 2/Stage 3 boundary-defining result.
**Cost to decisive answer:** Medium-high. Implementation requires a differentiable outer-product write (doable via torch autograd, outer product is just einsum). ~2d implementation + 6h smoke iteration + remote CPU full.
**Novelty score:** VERY HIGH. Learned Hebbian encoding with gradient-through-write is novel to the HDC literature. Closest work: Frady et al. (2021) resonator networks learn to factor VSA representations, but not via direct write-gradient.
**Rank justification:** (very high load-bearing: Stage 2/3 boundary) x (medium-high cost) x (very high novelty). Ranked below throughput model because that's immediately needed for M3 Phase 1 planning; this is 2-3 cycles out.

---

### RANK 5 — Retrieval latency percentile sweep at commercial M (Dim C)
**Cell concept:** exp_stage2_retrieval_latency_percentiles_commercial_M_v1
**Question:** What is p50/p95/p99 retrieval latency as M scales from 10k to 1M items, at N=8192, on CPU vs GPU? Does latency grow linearly (O(N*M) matmul dominates) or sub-linearly (BLAS blocking effects)?

**Context:** cortex_hippo_commercial v5 (HARD_PASS) verified recall at M=100k/500k/1M. But that cell was a RECALL cell. The latency regime at commercial scale is uncharacterized. For M3 Phase 1, the cortex router must decide: "can I afford a substrate lookup in the critical path of a conversational response?" This requires knowing p95 latency at production load.

**Design:**
- N=8192, M sweep: [10k, 50k, 100k, 500k, 1M]
- Measure: ingest throughput (facts/sec), query latency (p50/p95/p99 across 1000 queries)
- Arms: CPU (numpy), GPU (torch.cuda), INT8-CPU (using int8_dense.py primitive)
- Discriminator: at M=100k, GPU p95 < 10ms AND CPU p95 < 100ms (reasonable conversational latency)
- Secondary: does INT8 halve query latency vs FP32 at the same M? (Memory bandwidth bound at large M)

**Load-bearing for M3:** The Phase 1 cortex router makes substrate lookups inline. A 100ms p95 latency at M=100k items kills interactive latency budgets. A 10ms GPU p95 is usable. This characterization gates whether substrate-as-conversational-memory is viable without pre-computation / approximate methods.
**Cost to decisive answer:** LOW. No new mechanism — pure instrumentation of existing code paths. 1d implementation, 4h remote CPU + GPU.
**Novelty score:** LOW (latency characterization). But the result is immediately commercially actionable.
**Rank justification:** (high load-bearing for M3 Phase 1 planning) x (lowest cost of all 5 cells) x (low novelty). Ranked 5 because it's confirmatory/measurement rather than discovery, and the Rank 2 cleanup operating curve partially covers this.

---

## Literature Review Candidates Per Cell

**Rank 1 (INT2/binary at cliff):**
- Nagel et al. "A White Paper on Neural Network Quantization." arXiv 2106.08295 (2021) — quantization theory, noise floor models
- Courbariaux et al. "BinaryConnect: Training Deep Neural Networks with Binary Weights." NeurIPS 2015 — binary weight matrices in neural networks; W_binary = SIGN(W_full)
- Hubara et al. "Quantized Neural Networks: Training Neural Networks with Low Precision Weights and Activations." JMLR (2018)
- The specific question (Hopfield network with binary weight matrix) maps to the classical Amit-Gutfreund-Sompolinsky 1985 analysis which shows binary Hopfield has ~0.138N capacity vs 0.14N for analog — very close. This suggests INT2 should also survive with minimal loss.

**Rank 2 (cleanup latency operating curve):**
- Ramsauer et al. "Hopfield Networks is All You Need." ICLR 2021 — modern Hopfield energy, update rule complexity
- McAuley & Caetano "Faster Algorithms for Max-Product Message-Passing." JMLR (2011) — BLAS-bound quadratic CAM
- RAGO: Systematic Performance Optimization for RAG Serving. ISCA 2025 — RAG latency decomposition (in substrate-KB at cosine=0.27); substrate lookup would be ~encoding portion

**Rank 3 (group-wise quantization):**
- Frantar et al. "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers." ICLR 2023
- Dettmers et al. "QLoRA: Efficient Finetuning of Quantized LLMs." NeurIPS 2023
- Dettmers & Zettlemoyer "The Case for 4-bit Precision." ICML 2023 — empirical evidence that 4-bit is the quantization floor for weight matrices; 2-bit needs group-wise

**Rank 4 (learned encoding):**
- Johnson et al. "Billion-scale Similarity Search with GPUs." IEEE TKDE 2021 (FAISS-IVF — learned centroids for ANN)
- Frady et al. "Resonator Networks, 1: An Efficient Solution for Factoring High-Dimensional, Distributed Representations." Neural Computation 2020
- Yang et al. "Scalable and Accurate Self-Supervised Contrastive Graph Representation Learning." ICLR 2022 — contrastive objectives for embedding spaces; applicable if learned encoding uses contrastive loss

**Rank 5 (latency percentiles):**
- RAGO ISCA 2025 (in substrate-KB) — RAG latency breakdown; substrate lookup equivalent to vector search step
- Johnson et al. FAISS-IVF — BLAS matmul at scale (same O(N*M) complexity)

---

## Recommended Immediate Cell-Author Dispatches

**Dispatch order (gated by substrate-KB query result + discriminator-must-survive-scale):**

1. **Rank 1 (INT2/binary pareto probe)** — dispatch immediately via hdi_exp_dev. Structure is 100% re-usable from v3. Pre-reg authoring cost ~1h. Route to remote_cpu_queue (3 seeds). This is the decisive next step in the quantization Pareto arc.

2. **Rank 2 (cleanup latency operating curve)** — dispatch in parallel with Rank 1 if spawn budget allows. Re-uses v2c code, adds timing instrumentation only. Route to remote_cpu_queue. Useful for M3 Phase 1 planning immediately.

3. **Rank 5 (commercial latency percentiles)** — can be authored as part of the same Rank 2 dispatch (latency-at-scale is the natural extension of the cleanup latency curve). Bundle with Rank 2 in a single hdi_exp_dev spawn.

4. **Rank 3 (group-wise quantization)** — defer until Rank 1 results land. If INT2 HARD_PASS, deprioritize. If INT2 MIDDLE_BAND or HARD_FAIL, promote to top priority.

5. **Rank 4 (learned encoding)** — Stage 2 later. Requires new implementation work (differentiable outer-product write). File pre-reg now, dispatch after Ranks 1-3 resolve. The encoder_bridge MIDDLE_BAND and cocktail_composition HARD_FAIL both suggest the encoding question is hard; TEST RATIONALITY discipline means the new cell must explicitly encode via gradient, not test interoperability.

---

## Stage 2 Gap Map (Beyond These 5)

The July 2026 pre-reg list shows these Stage 2 cells already filed but not in the top-5 because they're either running or pre-regged:
- `2026-07-01_substrate_bytes_per_fact_pareto_v2_extended_precisions.md` — covers BFLOAT16+INT4+M sweep at N=4096 (KG-ingest angle; different from noise-cliff angle)
- `2026-07-01_substrate_bytes_per_fact_pareto_v5_int8_specialization.md` — covers INT8 at M=40k-80k with BINARY anchor

These are complementary. The INT2 Rank-1 cell fills the gap between INT4 and binary at the NOISE CLIFF specifically.

Additional Stage 2 gaps NOT yet addressed:
- Write-rule comparison: `2026-07_write_rule_capacity_compare_v1.md` exists — check if landed
- ZCA prewhitening: `2026-07_zca_prewhiten_online_cpu_v1.md` — online whitening as encoding optimization
- Dim S (metric-dependence top-K vs top-1) — partial via metric_dependence v3 3-seed (check verdict); if HARD_PASS, extend to semantic similarity (cosine not top-K)

---

## Cross-references

- `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` — parent dim catalog (Dim L = random vs learned encoding; Dim C = latency percentiles)
- `notes/research_dim_a_temporal_dynamics_forgetting_2026-07-02.md` — companion Dim A drill (Dim A = CLOSED structural constraint, not open question)
- `data/exp_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack_seed_{7,13,19}/metrics.json` — INT8 v3 baseline (all HARD_PASS)
- `data/exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_7/metrics.json` — cleanup dominance v2c
- `data/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7/metrics.json` — M-N-K separability HARD_PASS
- `preregs/2026-07-01_stage2_int8_dense_hopfield_end_to_end_recall_v3_noise_sweep_at_crack.md` — INT8 v3 pre-reg (template for INT2 cell)
- Amit-Gutfreund-Sompolinsky 1985 — classical binary Hopfield capacity 0.138N (predicts INT2/binary should survive)
- Nagel et al. 2021 "White Paper on Neural Network Quantization" — quantization noise floor models
