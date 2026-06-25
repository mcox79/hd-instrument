# exp_dev hand-off - research: Resonator integration HARD_FAIL revival (disparate-fields drill)

filed: 2026-06-24
trigger: research drill `notes/research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md` identified that the Resonator-integration HARD_FAIL (NAIVE 2HOP 0.65 ~= RESONATOR 2HOP 0.63) is NOT a per-hop-cleanup-capacity problem (Modern-Hopfield top-K cleanup is fine per-hop). It is an INTER-HOP hard-decision error-propagation problem structurally identical to error-propagation in Decision Feedback Equalization (DFE) in communications theory. The substrate-native rescue is to replace hop-1 hard argmax with soft-confidence chaining; brain analog is CA3 graded reactivation. 5-field cross-domain drill ranked three implementation paths.

pause state: check `d:/AI/hd-instrument/data/orchestrator_paused.flag` before shipping any anchor. If paused, this hand-off is read-only structural context for the orchestrator to pick up post-resume; do NOT ship to queue until the flag is cleared and the orchestrator/USER confirms.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors and substrate-product readings; it does NOT prescribe cell-level experiment parameters. exp_dev owns the design call. The role of this file is to surface pre-registered HARD-PASS/HARD-FAIL bands so exp_dev can ship with confidence.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (RANK 1, cross-field lit-anchored, highest P, lowest substrate-primitive distance)

ANCHOR: SOFT-CHAIN multi-hop (substrate-native analog of Soft-DFE / turbo equalization).

- substrate-product reading: at hop-1, replace argmax/top-K cleanup with a softmax distribution `q1[i] = softmax(similarity_i / T)` over top-K=20 candidates (T calibrated so median-entropy ~= log(3) on the well-resolved synthetic case). Hop-2 key is built as a SUPERPOSITION: `k_hop2 = sum_i q1[i] * bind(atom_i, p2)`. Hop-2 cleanup runs on this superposed key; final readout is argmax over hop-2 codebook. ZERO new primitives required — just defer the hop-1 argmax and weight-sum the hop-2 keys.
- tier hint: TIER-2 (wiring change on existing Modern-Hopfield + bind + W stack; no new operator).
- why-now: highest-P rescue across 5 disparate fields. Communications-theory existence proof (50-year-mature soft-DFE / turbo decoding); brain existence proof (CA3 graded reactivation). Cell author can implement in ~30 LOC.
- pre-registered HARD-PASS: ARM_SOFT_CHAIN mean accuracy >= 0.78 over 5 seeds at M=1000, K_SET=20, N_DIM=4096 (apples-to-apples regime that produced the HARD_FAIL); sd <= 0.04; ARM_SOFT_CHAIN > ARM_BASELINE_HARD + 0.10 at p<0.05 paired-seed.
- pre-registered HARD-FAIL: ARM_SOFT_CHAIN mean <= 0.68 (no detectable lift over baseline + 0.03 ceiling).
- pre-registered MIDDLE_BAND (most-likely outcome under 0.25 calibration deflation): 0.70 <= ARM_SOFT_CHAIN < 0.78 (small-but-real lift); follow-up at larger M and/or turbo iteration.
- cost: ~1 hr CPU pre-flight + ~1-2 hr cell-author smoke (Fix #17). Single cell, 3 arms (BASELINE_HARD + SOFT_CHAIN + KBEAM_PATHSUM combined).
- risk class: structural-additive. LOW.
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples
- corpus_provenance: synthetic_random_atoms_M1000_V10_K20_N4096_seeds_0_to_4

### ANCHOR 2 (RANK 2, complementary to ANCHOR 1, run in same cell)

ANCHOR: K-BEAM PATH-SUM (substrate-native analog of Feynman sum-over-paths).

- substrate-product reading: at hop-1, retain top-K=10 candidate intermediates with similarity scores s1[i] (do NOT superpose into hop-2 key). For each candidate i, run hop-2 separately to get endpoint distribution and per-endpoint similarity s2[i, j]. Final endpoint score: `score[j] = sum_i s1[i] * s2[i, j]` (real-amplitude path sum); argmax over j. For FHRR substrate, can be extended to complex amplitude sum for true interference.
- tier hint: TIER-2 (K-fold per-hop cleanup repetition + readout aggregator; no new primitive).
- why-now: complementary to ANCHOR 1 — soft-chain mixes hop-1 candidates INSIDE W via superposition; K-beam keeps them SEPARATE and aggregates only at readout. Different failure modes. If BOTH HARD_PASS, the soft-confidence-chaining principle is cross-confirmed by two implementations.
- pre-registered HARD-PASS: ARM_KBEAM_PATHSUM mean accuracy >= 0.78 over 5 seeds at same regime; sd <= 0.04; > baseline + 0.10.
- pre-registered HARD-FAIL: ARM_KBEAM_PATHSUM mean <= 0.68.
- cost: ~1-2 hr CPU (K-fold per hop is heavier than soft-chain); combine with ANCHOR 1 in single 3-arm cell to amortize.
- risk class: structural-additive. LOW.
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples
- corpus_provenance: synthetic_random_atoms_M1000_V10_K20_N4096_seeds_0_to_4

### ANCHOR 3 (RANK 3, contingent on ANCHOR 1+2 outcomes)

ANCHOR: SUBSTRATE-PAGERANK readout (random-walk stationary distribution; graph-theory field).

- substrate-product reading: treat W as encoding a relation-graph; multi-hop query is personalized PageRank from start-entity. `pi_(t+1) = alpha * W_relation @ pi_t + (1-alpha) * e_s0`; iterate 20-50 steps to convergence; top-K endpoints from pi are the answer. Substrate-native form is power-iteration directly in vector space (no graph materialization).
- tier hint: TIER-2/TIER-3 boundary (no new operator but a new readout pattern with iteration convergence to manage).
- why-now: ONLY dispatch if ANCHOR 1 AND ANCHOR 2 both HARD_FAIL or both MIDDLE_BAND. If either delivers HARD_PASS, skip — the soft-confidence-chaining principle is established and PageRank does not add an independent angle.
- pre-registered HARD-PASS: ARM_PAGERANK mean accuracy >= 0.78 over 5 seeds at same regime; sd <= 0.04; convergence within 50 iter; > baseline + 0.10.
- pre-registered HARD-FAIL: ARM_PAGERANK mean <= 0.68 OR fails to converge in 50 iter on >10% of seeds.
- pre-registered MIDDLE_BAND: 0.70-0.78 — likely outcome given substrate W is high-dim dense, not sparse graph.
- cost: ~3-5 hr (iteration convergence tuning + readout from continuous pi distribution).
- risk class: structural-additive. MEDIUM (iteration convergence on substrate W is unvalidated).
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples
- corpus_provenance: synthetic_random_atoms_M1000_V10_K20_N4096_seeds_0_to_4

### ANCHOR 4 (RANK 4, contingent on RANK 3 outcome; bonus cross-of-2+4)

ANCHOR: TURBO BELIEF PROPAGATION on substrate factor graph (unifies soft-DFE + PageRank).

- substrate-product reading: treat each hop as a factor node; pass soft messages (entity distributions) between factor nodes; 2-3 iterations to convergence. Generalizes both ANCHOR 1 (soft-DFE = BP on a chain) and ANCHOR 3 (PageRank = BP with teleportation).
- tier hint: TIER-3 (new message-passing scheduler primitive; substrate has no existing BP machinery).
- why-now: dispatch ONLY if RANK 1 + RANK 2 both deliver MIDDLE_BAND (suggesting iteration / refinement could push to HARD_PASS) AND RANK 3 also MIDDLE_BAND (suggesting graph-style readout has merit but needs unification). If RANK 1 HARD_PASSes alone, this anchor is structurally unnecessary.
- pre-registered HARD-PASS: ARM_TURBO_BP mean accuracy >= 0.85 over 5 seeds (higher bar because of new-primitive cost); convergence within 3 iter on >90% of seeds.
- pre-registered HARD-FAIL: ARM_TURBO_BP mean <= 0.75 OR fails to converge in 5 iter.
- cost: ~3-5 person-days impl (new BP scheduler primitive) + ~2 hr CPU validation.
- risk class: new primitive. MEDIUM-HIGH.

### ANCHOR 5 (DEFERRED, do NOT ship from this hand-off)

ANCHOR: Resonator-Network 3-factor SIMULTANEOUS factorization (re-frame 2HOP as `bind(start, p1, p2)` composite with intermediate as unknown factor).

- why deferred: substrate-native variant of Frady-Kent that has never been tested on our substrate because we have always done sequential cleanup. P_deflated = 0.25; below ANCHOR 1-3. Cost of implementation higher than wiring-change anchors. Surface as "open option for after ANCHOR 1+2+3 outcomes."

---

## Context pointers (file paths, not summaries)

- research note (primary): `d:/AI/hd-instrument/notes/research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md`
- cross-thread prior 1: `d:/AI/hd-instrument/notes/research_2x_revival_comparator_resonator_HF_2026-06-23.md` (smoke-regime-too-easy diagnosis for the comparator)
- cross-thread prior 2: `d:/AI/hd-instrument/notes/research_negative_N6_resonator_dense_V100_HF_2x_2026-06-20.md` (dense V100 resonator multi-hop HARD_FAIL — soft-chain not tested)
- cross-thread prior 3: `d:/AI/hd-instrument/notes/research_resonator_capacity_extensions_2026-06-16.md`
- cap_map: `d:/AI/hd-instrument/notes/substrate_capability_map.md` (PP-multi-hop-reasoning currently INCONCLUSIVE; PP-resonator-decomposition-ACF VALIDATED — clarifies that resonator-network per-se is NOT what failed; chaining wrapper is)
- pause flag check: `d:/AI/hd-instrument/data/orchestrator_paused.flag`
- exp_dev companion exists for prior comparator HF: `d:/AI/hd-instrument/notes/exp_dev_handoff_research_2x_revival_comparator_resonator_HF_2026-06-23.md` (the comparator's v3 Arm 3 wants soft-chain too; SHARE the substrate primitive between cells)

---

## Contract

This file is auto-discovered by exp_dev on emergency-refill cycles (it scans `notes/exp_dev_handoff_*.md` sorted by mtime). It surfaces cross-domain-anchored anchors with pre-registered failure bands - exp_dev decides the cell parameters, smoke-gate, and ship order.

The pre-registered HARD-PASS/HARD-FAIL bands above are AUTHORITATIVE - they were derived during the cross-domain research drill against published literature (communications theory + brain neuroscience + 3 other fields) and substrate-product positioning constraints. exp_dev should not soften them at design time; if cell parameters force a softer threshold, that itself is a finding worth surfacing back to research before shipping.

The ordering RANK 1+2 (parallel-in-one-cell) -> RANK 3 -> RANK 4 is a sequential gate: ship the 3-arm cell with ANCHOR 1 + ANCHOR 2 + BASELINE_HARD; read verdict; only ship RANK 3 if both 1 and 2 fail or middle-band; only ship RANK 4 if 1+2+3 all middle-band; never ship ANCHOR 5 from this hand-off without strategy/USER approval.

Pre-dispatch verify-the-referent (Fix #26) discipline: cell-author should `tools/predispatch_check.py multihop_softchain_kbeam_3arm_v1` BEFORE spawning to catch any prior partial implementation.

Per-arm metrics discipline (Fix #28): record per-seed per-arm accuracy SEPARATELY in metrics.json; do NOT propagate cross-arm convergence claims from verdict_msg without per-arm verification.

---

## Autonomy declaration

This hand-off names anchors + reads + bands. exp_dev owns:
- Cell parameter choices (single-cell-3-arm vs three-separate-cells; smoke regime selection within the apples-to-apples band; T-calibration sweep for soft-chain; K-beam width search for K-beam path-sum)
- Smoke-gate design (target ~30 min runtime per arm; 5 seeds; deterministic seed list)
- Queue routing (local_cpu_queue likely sufficient given M=1000, N_DIM=4096; overnight_queue if exp_dev expands to multi-K-sweep)
- Ship order across the rank-gate
- Post-verdict atomization into Store (results-to-application-cadence per [[feedback-results-to-application-cadence]])

research deliverable ends at this hand-off + the research note. exp_dev decides next steps from here.
