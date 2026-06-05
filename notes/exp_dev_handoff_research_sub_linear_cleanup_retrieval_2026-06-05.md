# exp_dev hand-off -- research: sub-linear cleanup retrieval production scale

Filed-by: research sub-agent (Sonnet), 2026-06-05
Trigger: notes/research_drill_sub_linear_cleanup_retrieval_production_scale_2x_2026-06-05.md
Pause state: check data/orchestrator_paused.flag before dispatching; experiments below are PENDING user go-ahead

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs anchor mechanics autonomously; this file supplies TASK + WHY + CONTRACT + AUTONOMY pointers only. No sweep grids, no threshold formulas, no anchor names, no queue assignments.

---

## Anchor Candidates (rank-ordered)

### 1. HNSW cleanup vs naive scan -- cheap decisive test (Tier: CPU laptop smoke)
Anchor pointer: Research note Section "Cheap Decisive Test" + Architecture 2 (HNSW) analysis
Substrate-product reading: Validates 1000-3000x query speedup; unlocks production V_c = 1M with CPU-only inference; removes GPU dependency for cleanup step
Tier hint: laptop CPU; <2h wall; V_c=10K to 100K range; N=1024 to 4096
Why now: This is the direct experimental gate for the Phase 3 production architecture decision. The algebraic analysis is done; empirical recall@1 vs speedup curve needs one smoke run to confirm.

### 2. IVF-PQ + RaBitQ bipolar cleanup (Tier: remote CPU or GPU)
Anchor pointer: Research note Architecture 4 (PQ/RaBitQ) + Synthesis Table
Substrate-product reading: RaBitQ's O(1/sqrt(N)) error bound applies directly to bipolar +-1 codebook atoms; SIMD bitwise ops give 128x over float32 per distance; combined with IVF nprobe=10 gives expected 6000x total speedup
Tier hint: remote CPU; V_c = 100K to 1M; N = 65536 for full-scale validation
Why now: RaBitQ SIGMOD 2024 has published theoretical guarantees; bipolar fit is direct; no community validation at V_c > 100K in bipolar context

### 3. Hierarchical VQ (k=4 levels) cleanup (Tier: CPU laptop)
Anchor pointer: Research note Architecture 1, k-level generalization formula; 4 levels at V_c=1M -> 126 evaluations -> 7937x speedup
Substrate-product reading: Simplest to implement (partition tree on atom indices); deterministic; zero accuracy loss if SNR > recall threshold derived in note
Tier hint: laptop CPU; V_c = 10K to 1M sweep; N = 1024 to 65536
Why now: Does NOT require FAISS; can be implemented in pure numpy; lowest barrier to entry; validates the algebraic speedup claim

### 4. Random projection sketch + IVF + RaBitQ hybrid (Tier: remote CPU)
Anchor pointer: Research note Cross-Domain Probe section, "Sketch+IVF+RaBitQ" row in Synthesis Table
Substrate-product reading: Novel cross-domain synthesis; sketch_dim = N/100 = 655 for N=65536; compressed-sensing JL lemma gives 100x additional speedup on top of IVF; community has not applied this to bipolar cleanup; P_deflated = 0.50 (novel synthesis cap)
Tier hint: remote CPU; V_c = 1M, N = 65536 for production-scale proof of concept
Why now: If validated, this is the highest-speedup architecture available (~5200x total, CPU-deployable)

---

## Context Pointers

- Research note (full analysis, formulas, citations): d:/AI/hd-instrument/notes/research_drill_sub_linear_cleanup_retrieval_production_scale_2x_2026-06-05.md
- FAISS documentation: https://github.com/facebookresearch/faiss/wiki
- RaBitQ paper: https://arxiv.org/abs/2405.12497 (SIGMOD 2024)
- Kronecker VSA paper: https://arxiv.org/abs/2506.15793 (June 2025)
- HNSW paper: Malkov & Yashunin 2018, IEEE TPAMI 42(4):824-836
- hnswlib (Python): https://github.com/nmslib/hnswlib
- Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md (check for cleanup-cost rows)

---

## Contract

exp_dev is responsible for:
1. Reading the research note in full before designing any anchor
2. Identifying which existing substrate infrastructure (hdlab/ modules) handles bipolar vector generation + W-matrix retrieval output
3. Designing smoke checkpoints per [[feedback-metrics-required-fields-write_metrics]]
4. Pre-registering HARD-PASS / HARD-FAIL bands per [[feedback-envelope-expansion-fail-bands]] before queueing
5. Verifying timeout formula [[feedback-per-experiment-timeout-required]] for each anchor
6. NOT including mechanism-specific configs or threshold numbers in queue prompts [[feedback-no-experiment-design-in-prompts]]

## Autonomy Declaration

exp_dev has full autonomy to:
- Choose which anchor to ship first based on current queue depth + runner state
- Define sweep grids, seed counts, and timeout multipliers
- Select queue (laptop CPU / remote CPU / remote GPU) per [[feedback-route-gpu-vs-cpu-by-torch-not-N]]
- Reject anchors that fail the smoke gate without escalating
- Propose a different architecture not in this list if research note suggests it
