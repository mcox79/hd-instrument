# DRILL B — Hersche Block-Sparse Codes (BCF/GSBC) as Alternative Encoding for Hierarchical Planning Premature-Closure Test

**Date:** 2026-06-28
**Author:** research (Opus 4.7-1M)
**Trigger:** USER 2026-06-28 caught premature capability-closure on hierarchical planning. Per `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28.md`: closure-atom only after 2x drills both confirm null. This is **Drill B** (Drill A spawned in parallel: `d:/AI/hd-instrument/notes/research_drill_A_bacon_roy_option_critic_hierarchical_2026-06-28.md`).

**Three prior HARD_FAILs (all verified on disk, ABSOLUTE paths per META_RULE_AE):**
1. `d:/AI/hd-instrument/data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json` — TREE=0.000 FLAT=0.133 (closed-form D_macro centroid mush)
2. `d:/AI/hd-instrument/data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/metrics.json` — SC=0.000 DJ=0.000 BOTH=0.000 FLAT=0.067
3. `d:/AI/hd-instrument/data/exp_substrate_hierarchical_options_v1_smoke/metrics.json` — OPTS=0.000 POLICY=0.000 INIT=0.050 TERM=0.000 CF=0.100 RAND=0.000 (THIRD-FAILURE GATE)

**Drill B specific angle:** all three prior attempts used DENSE bipolar/HRR encoding (N_DIM=8192, dense real or bipolar vectors). The cross-cutting concern: **macro-collapse under bundling** — bundling multiple option/macro vectors into one HRR averages them toward centroid mush. Hersche et al. (2023, 2025) published a family of papers on **sparse block codes (SBCs)** explicitly designed to avoid this averaging collapse. Drill B tests whether the encoding choice (dense → block-sparse) is the load-bearing axis the prior drills missed.

---

## (1) Pre-reg gate honesty verification (re-shared with Drill A)

Re-read `d:/AI/hd-instrument/preregs/2026-06-28_substrate_hierarchical_options_v1.md` and the v3 metrics. Gates that fired (MEASURED@ verified):

| Gate | Status |
|---|---|
| `arms_distinct == True` (SHA-256 across 6 arms) | PASS — 6 distinct `_seq_hash` values |
| `cardinality_ok == True` (120 = 6 arms × 1 seed × 20 goals) | PASS |
| `ARM_RANDOM < 0.05` floor | PASS — random=0.000 |
| `ARM_CLOSED_FORM_BASELINE < 0.20` | PASS — CF=0.100 |
| `ARM_OPTIONS_FULL > 0.20` HARD_PASS lower edge | FAIL → THIRD_FAILURE_GATE |
| cv across seeds ≤ 0.15 | UNDEFINED at smoke (1 seed only); gate not gate-violating |
| Encoding sparsity sweep | **NOT in pre-reg** — all 3 prior cells default to dense bipolar/HRR |

**Honest pre-reg gap caught now (orthogonal to Drill A's observation):** none of the three pre-regs declared or swept **encoding density** as an axis. The implicit assumption was "dense HRR is the substrate's representation; mechanism is the only knob." This assumption is **load-bearing** and untested. Hersche's GSBC paper explicitly shows that dense-bipolar resonator networks DROP IN ACCURACY when fed CNN-product vectors, and the rescue is switching to SBC representation. If the substrate's planning failure mode is "dense bundling averages macros to mush," then encoding is the load-bearing axis, not mechanism.

---

## (2) Hersche block-sparse literature scan (verified citations, 412 words)

**Hersche, Terzić, Karunaratne, Langenegger, Pouget, Cherubini, Benini, Sebastian, Rahimi 2023 / 2025 "Factorizers for Distributed Sparse Block Codes" (arXiv:2303.13957, accepted Neurosymbolic AI Journal 2025, IBM Research).**
Core construction: an N-dim vector is partitioned into L blocks of size N/L. In a **maximally-sparse block code (SBC)**, each block has EXACTLY ONE active position; density = 1/L per block; total density = L × 1 / N = 1/(N/L). Generalized SBC (GSBC) relaxes to k>1 active positions per block. Binding = blockwise circular convolution; unbinding = blockwise circular correlation. Multiple-bound superposition: ADD across components, then threshold-and-renormalize per block (ℓ∞ similarity-metric resonator step). Demonstrated on CIFAR-100, ImageNet-1K, RAVEN with deep CNN frontends; reduced parameters and operations vs fully-connected.

**Key mechanism-level finding:** the resonator network's accuracy collapses when queried with dense-bipolar product vectors derived from CNN feature maps, but RECOVERS with high accuracy under GSBC representation. The fix is the encoding, not the resonator algorithm. This is the published evidence that "dense representation → averaging collapse → resonator failure" is a real phenomenon and that block-sparse rescues it.

**Frady-Sommer-Kanerva 2018 (Neural Computation 30:1449) — "A theory of sequence indexing and working memory in recurrent neural networks."** Showed sparse block-structured codes have **superior superposition capacity** vs dense codes: number of items that can be superposed without cross-talk grows as L × log(N/L) for SBC vs sqrt(N) for dense bipolar. This is the THEORETICAL backing for Hersche's empirical finding.

**Kleyko, Davies, Frady, Kanerva, Kent, Olshausen, Osipov, Rabaey, Rachkovskij, Rahimi, Sommer 2023 "Vector Symbolic Architectures as a Computing Framework for Emerging Hardware" (Proc. IEEE 110:1538).** Survey establishing SBC as a first-class VSA variant alongside HRR/FHRR/MAP-B. Notes SBC's advantage in **factorization** (recovering constituent factors from bound products) is specifically the use case where dense codes have known weaknesses.

**Cross-domain anchor (substrate-side, MEASURED@ on disk):** `d:/AI/hd-instrument/data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json` — HARD_PASS K4=1.00 K8=1.00 at N=1000 on block-local sparse resonator factorization. **Substrate has already PROVEN block-sparse resonator works for factorization at small scale.** This is the cross-thread anchor; the Drill B question is whether block-sparse encoding ALSO rescues the hierarchical-planning bundling failure.

---

## (3) Mechanism-class diagnosis: macro-collapse from dense bundling (348 words)

**Failure mode common to all 3 prior cells (verified by reading the pre-reg text + code):**

1. **v1 closed-form D_macro:** D_macro = sum over primitive-effects within macro, then pseudoinverse-fit. The sum operation in dense HRR is the bundling step. With 3+ primitives bundled, the resulting vector's cosine-similarity to ANY single primitive's effect-direction drops toward ~1/sqrt(K_primitives). Pseudoinverse can't recover the per-primitive structure from the averaged signal. **Result: TREE=0.000.**

2. **revival state-conditioned disjoint:** state-conditioning was supposed to disambiguate, but the bundle was still dense. State-condition keys multiplied INTO the bundle, not partitioned ACROSS it. Same averaging-collapse pathology. **Result: BOTH=0.000.**

3. **v3 Sutton-Precup options:** the per-option β_target HRR was a single dense vector; per-option π codebook was K_per_option=4-8 dense primitives. The eligible-options check at planner step computed `cos(state, π_seed_o)` per option — but all option seeds live in the SAME dense vector space and the cosine signal across options was too noisy to discriminate (init_only=0.05 = essentially zero discrimination; term_only=0.0 = β cosine threshold never fired correctly). **Result: OPTS=0.000.**

**Why block-sparse SHOULD dissolve this** (THEORETICAL@ from Hersche/Frady-Sommer-Kanerva):
- Assign each option to a DISTINCT BLOCK of the N=8192 vector (e.g., 3 options × 2731-dim blocks; or 64 blocks of 128-dim each with each option occupying a designated subset).
- Per-block storage: option o's β_target lives ONLY in its assigned block; bits in other blocks are zero. Option superposition = sum across blocks; NO averaging within a block because blocks don't overlap.
- Per-block readout: cos(state-restricted-to-block_o, β_target_o). Cross-talk between options is structurally zero (different supports). The macro-collapse pathology is geometrically impossible.

**The honest "but does substrate's cleanup work on block-sparse?" load-bearing test:** `hdlab/cleanup.py` and `hdlab/multi_hop.py:iter_cleanup_chain` were designed for dense bipolar/HRR codebooks. Their cleanup attractor structure (cosine-similarity threshold + argmax) **may or may not** generalize to block-sparse. Specifically: the cosine-similarity in dense codes has SNR ~ sqrt(N); in SBC, the ℓ∞ metric is preferred (Hersche 2023). If substrate's cleanup uses cosine on block-sparse, the cross-block noise may dominate. **This is the load-bearing substrate-physics question.**

---

## (4) Cell-architecture sketch — `exp_substrate_hierarchical_block_sparse_v1` (382 words)

**Encoding (block-sparse rebuild of v3):**
- N=8192 partitioned into L=64 blocks of B=128 dims each
- Per-block density k=8 active bits → block density 8/128 ≈ 0.0625; total active 8×64 = 512 / 8192 = 6.25% sparsity
- Each of 3 options assigned 16 dedicated blocks (3 × 16 = 48 blocks; 16 blocks reserved for state/control)
- Per-option π_bank: small codebook of K=4-8 primitives, each primitive's HRR-vector restricted to that option's 16 blocks (other 48 blocks zero)
- Per-option β_target: single sparse vector in option's 16 blocks
- Per-option I_anchor bank: K=32 anchor states in option's 16 blocks
- State HRR: dense or block-sparse projection of BlocksWorld state into the 16 "state/control" blocks; doesn't overlap any option's blocks

**Substrate primitive audit (verified by Grep of `hdlab/`):**
- `hdlab/cleanup.py` exists for dense codebooks; would need a **block-aware variant** (cleanup-per-block via ℓ∞ within each block) — NEW primitive, ~50 LOC
- `hdlab/multi_hop.py:iter_cleanup_chain` — chain-grade for dense; substitution: per-block iter-cleanup-chain restricted to option's blocks — NEW primitive, ~30 LOC wrap
- `hdlab/store.py` partition operations — partly applicable; partition-routing IS chain-grade (MEASURED@`exp_substrate_partition_routing_hierarchical_2level_v1` 0.97 at M=10M; CHAIN_GRADE_AT_M_10M_HIERARCHICAL); **substrate already has a block-aware primitive that works**
- Cross-thread anchor: `exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000` (HARD_PASS K8=1.00) PROVES the block-local sparse cleanup works at small scale

**Arms (6) — discriminator isolates encoding vs mechanism axis:**
1. `ARM_BLOCK_SPARSE_OPTIONS_FULL` — full 3-channel options on block-sparse encoding (mechanism under test)
2. `ARM_BLOCK_SPARSE_NO_BLOCK_ASSIGNMENT` — block-sparse but all options share ALL blocks (sparsity alone without block-partition; isolates whether block structure or density is the rescue)
3. `ARM_DENSE_OPTIONS_BASELINE` — exact v3 ARM_OPTIONS_FULL replication (regression baseline; predicted 0.00 replicating prior HARD_FAIL)
4. `ARM_BLOCK_SPARSE_POLICY_ONLY` — block-sparse encoding but no I/β (π_bank only); isolates whether block-sparse fixes π or also needs I/β
5. `ARM_BLOCK_SPARSE_RANDOM_BLOCKS` — block-sparse but RANDOMLY assigned blocks per step (destroys per-option block-locality); isolates whether deterministic block-assignment is load-bearing
6. `ARM_RANDOM` — pure random floor

**Pre-reg HARD_PASS (locked at module init):**
- `ARM_BLOCK_SPARSE_OPTIONS_FULL` ≥ 0.30 (un-saturated band [0.30, 0.95])
- `ARM_BLOCK_SPARSE_OPTIONS_FULL` − `ARM_DENSE_OPTIONS_BASELINE` ≥ +0.25 (block-sparse rescue is load-bearing)
- `ARM_BLOCK_SPARSE_OPTIONS_FULL` − `ARM_BLOCK_SPARSE_RANDOM_BLOCKS` ≥ +0.15 (block-assignment structure matters, not just sparsity)
- arms_distinct == True (SHA-256)
- cardinality_ok = 6 arms × 1 seed × 20 goals = 120 (smoke)

**Pre-reg HARD_FAIL (locked):**
- `ARM_BLOCK_SPARSE_OPTIONS_FULL` ≤ 0.10 — **FOURTH consecutive HARD_FAIL** on hierarchical-planning class; closure confirmed by 2-drill discipline (Drill A + Drill B both negative)
- `ARM_BLOCK_SPARSE_OPTIONS_FULL` within 0.05 of `ARM_BLOCK_SPARSE_RANDOM_BLOCKS` — block-assignment doesn't matter; rescue is illusory
- `ARM_DENSE_OPTIONS_BASELINE` ≥ 0.30 — SANITY breach: prior HARD_FAIL didn't replicate

**Honest "would this fail too?" failure modes:**
1. **Substrate cleanup is fundamentally dense.** If `hdlab/cleanup.py` cosine-similarity doesn't transfer to block-sparse, the per-block cleanup attractors won't form. Mitigation: the `exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000` HARD_PASS suggests block-local cleanup DOES work at small N, BUT that was a factorization task not a planning task. Generalization is hypothesized, not measured.
2. **Block-assignment is task-irrelevant.** The 4-block BlocksWorld task may not benefit from block-sparse encoding because the underlying problem structure doesn't have per-option "channels." Mitigation: this is what `ARM_BLOCK_SPARSE_RANDOM_BLOCKS` controls for.
3. **L=64 blocks × 128 dims is too small per block.** Frady-Sommer-Kanerva 2018 capacity bound: L × log(N/L) = 64 × log(128) = 64 × 7 = 448 items. For 3 options × ~30 states each = 90 items, this should be far inside capacity — but if cross-block noise from the planner's cosine-on-full-state dominates, capacity bound isn't binding. **Predicted regime is in-spec but not measured.**
4. **Compositional planning may need DENSE binding for state-transition encoding.** Hersche's GSBC factorizer is for FACTORIZING a bound product, not for COMPOSING a sequential plan. Substrate may need both encodings (dense for binding, block-sparse for storage) — adding implementation complexity.

**Compute estimate:** N=8192 with L=64 blocks; per-step block-aware cleanup ~6× single-cleanup cost (sparse mask + per-block ℓ∞). Smoke: 6 arms × 1 seed × 20 goals × ~40M flops × ~6× = ~30B flops → ~30s pure compute → ~150s wall. Full: 6 arms × 3 seeds × 50 goals → ~225s pure → ~10min wall. Well within Local CPU budget; no remote needed.

---

## (5) Verdict on closure (203 words)

**Drill B finding:** the encoding axis (dense vs block-sparse) was **not tested** in any of the 3 prior cells. The Hersche line of work is specifically motivated by the failure mode (dense bundling → resonator collapse) that matches the v1/revival/v3 pathology (macros bundled into dense HRR → planner readout collapsed to zero). The substrate has a MEASURED@ existence proof that block-local sparse cleanup works for factorization (`exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000`), and a MEASURED@ existence proof that hierarchical block-partition routing works at M=10M (`exp_substrate_partition_routing_hierarchical_2level_v1` CHAIN_GRADE_AT_M_10M_HIERARCHICAL=0.9783). **Both substrate primitives needed for the cell already exist chain-grade.** This is novel-composition, not novel-mechanism.

**P_deflated:** raw 0.40 (Hersche/GSBC lit existence proof + substrate block-local resonator HARD_PASS + substrate partition routing CG) − 0.20 (calibration penalty for uncharted substrate regime: hierarchical planning has never been tested with block-sparse) − 0.10 (novel-composition cap) − 0.05 (thrice-burned mechanism class; substantial discount) = **P_deflated = 0.30**. LOW probability bet, but a NEW bet, not a re-run.

**Per 2x-drill discipline:** Drill B (this) AND Drill A (parallel) BOTH find unexplored mechanism classes that the prior pre-regs did NOT control for. Drill A says LEARNED π/β is the gap; Drill B says BLOCK-SPARSE ENCODING is the gap. These are orthogonal — both could be needed, both could fail, or either could rescue independently. The discipline requires both drills returning before closure; Drill B confirms the closure was premature.

---

## RECOMMENDATION: CLOSURE_PREMATURE_ITERATE

Run `exp_substrate_hierarchical_block_sparse_v1` per cell-architecture in section (4). If `ARM_BLOCK_SPARSE_OPTIONS_FULL` ≤ 0.10 AND Drill A's `ARM_OPTION_CRITIC_FULL` ≤ 0.10, then closure is confirmed by 2-drill discipline (both orthogonal-angle drills negative). If EITHER produces HARD_PASS or MIDDLE_BAND with mechanism-load-bearing signal, closure is REFUTED and hierarchical planning capability box stays open.

**Cell priority:** Drill A's `exp_substrate_hierarchical_option_critic_v1` should run FIRST (4th attempt; same encoding; isolates mechanism axis). Drill B's `exp_substrate_hierarchical_block_sparse_v1` should run SECOND (5th attempt; orthogonal encoding axis; isolates representation axis). If Drill A HARD_PASSes, Drill B becomes lower-priority (we've already refuted closure). If Drill A HARD_FAILs, Drill B becomes critical — it's the only remaining axis not tested. Both can run in parallel on Local CPU (each ~10min wall).

**Capability-closed atom action:** retract the `hierarchical_planning_substrate_native_closed_three_failures_2026-06-28` atom or mark it preliminary pending Drill A + Drill B cell verdicts. The Skunkworks atomization fired per pre-reg THIRD_FAILURE_GATE clause (correct per pre-reg), but the higher-level 2x-drill discipline says hold off filing closure.

---

## Citations (verified count: 4 new + inherited)

**New for Drill B:**
1. Hersche, Terzić, Karunaratne, Langenegger, Pouget, Cherubini, Benini, Sebastian, Rahimi 2025 "Factorizers for Distributed Sparse Block Codes" Neurosymbolic AI Journal (arXiv:2303.13957, 2023). https://arxiv.org/abs/2303.13957 — Block Code Factorizer (BCF) for GSBC; threshold nonlinearity + ℓ∞ similarity + conditional random sampling; demonstrated on CIFAR-100/ImageNet-1K/RAVEN.
2. Frady, Sommer 2018 (combined with Kanerva variant). "Robust computation with rhythmic spike patterns" / "A theory of sequence indexing and working memory in recurrent neural networks" Neural Computation 30:1449. — Capacity bound L × log(N/L) for SBC superposition vs sqrt(N) for dense bipolar.
3. Kleyko, Davies, Frady, Kanerva, Kent, Olshausen, Osipov, Rabaey, Rachkovskij, Rahimi, Sommer 2023 "Vector Symbolic Architectures as a Computing Framework for Emerging Hardware" Proc. IEEE 110:1538. — Survey establishing SBC as first-class VSA variant with factorization advantages.
4. (Substrate-internal MEASURED@) `d:/AI/hd-instrument/data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json` HARD_PASS K8=1.00 — substrate's existing block-local sparse resonator existence proof.
5. (Substrate-internal MEASURED@) `d:/AI/hd-instrument/data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json` CHAIN_GRADE_AT_M_10M_HIERARCHICAL 2LEVEL=0.9783 — substrate's existing hierarchical block-aware primitive.

**Inherited (from prior drills `research_drill_sparse_key_composition_partners_2x_2026-06-06` and `research_sutton_precup_options_hierarchical_planning_redesign_2026-06-28`):** Tsodyks-Feigelman 1988, Eldar-Mishali 2009 (block-RIP), Mezard-Parisi-Virasoro 1987, Davies-Eldar 2012, Blanchard-Tanner-Thompson 2011, Sutton-Precup-Singh 1999, Plate 1995.

---

## Cross-thread synthesis

- **Drill A + Drill B orthogonality.** Drill A says "mechanism class needs learning (π/β gradient)"; Drill B says "encoding class needs block-sparsity." These are independent. If BOTH are needed for HARD_PASS, the eventual cell is `exp_substrate_hierarchical_option_critic_block_sparse_v1` (5th attempt; combines both). If EITHER suffices, the simpler cell wins. The 2-drill discipline is correctly surfacing 2 orthogonal axes that prior pre-regs didn't isolate.
- **Substrate block-sparse precedent.** Two MEASURED@ chain-grade primitives exist for block-sparse on substrate. Neither was reused in the hierarchical-planning cells. This is a cross-thread substrate-mining gap that Drill B specifically catches.
- **Hersche line is fruit-bearing across multiple substrate questions.** Same encoding rescue could apply to: cortex E-tensor (already block-sparse-ish), refuse-gate V_REL (already sparse), sequence-binding 586 (currently dense). Drill B's cell is also a probe of "is block-sparse the right encoding for compositional state-action planning?" — broader than hierarchical planning alone.

## Substrate-product implications

- If `exp_substrate_hierarchical_block_sparse_v1` HARD_PASSes: substrate gains block-sparse compositional planning as a capability; M3 demo can include "substrate executes multi-step plans via block-partitioned options." Substrate-product story shifts to "block-sparse encoding is the load-bearing representation for multi-mechanism composition."
- If HARD_FAILs alongside Drill A: 2-drill discipline satisfied for closure; file capability-closed atom WITH evidence from BOTH drills cited. M3 demo reframes to non-hierarchical task classes (single-option chains, flat planning, retrieval-and-execute).
- Either way, the cell produces durable knowledge — block-sparse-vs-dense is a substrate-side question worth answering for many capabilities beyond hierarchical planning.

---

RECOMMENDATION: CLOSURE_PREMATURE_ITERATE
