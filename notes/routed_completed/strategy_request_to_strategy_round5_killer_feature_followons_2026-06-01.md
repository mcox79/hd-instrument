# Strategy request: Round 5 killer-feature follow-ons (3-drill consolidated routing)

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Source**: `notes/research_round5_7_drills_synthesis_2026-06-01.md`
**Trigger**: user "do all" greenlight; design drills for 3 of 4 newly-promoted PP rows in v316 (PP-31 + PP-28 + PP-30)

## TL;DR

3 design drills landed for newly-promoted v316 rows. **Sub-property additions + conditional LIFTs proposed**; combined Tier 1 cheap-smoke cost ~40 CPU-min + cert-chain integration test. Each drill produces 4-8 mechanism candidates with explicit pre-reg bands.

## PP-31 calibrated-confidence Sub-caps 2+4 (8 mechanisms)

**Tier 1 dispatch order**:

| # | Mechanism | Cost | Strategic value |
|---|---|---|---|
| **2-D** | **Refusal audit certificate** | **3 CPU-min** | **STRONGEST compliance** (P=0.48) — distinguishes confidence-refusal from system-failure; satisfies FDA SaMD + EU AI Act Art 14 + SR 11-7 |
| 2-A | Hard threshold precision-coverage sweep | 8 CPU-min | Foundational τ ∈ [0.3, 0.8] sweep (P=0.42) |
| 4-A | Independence test for per-hop error correlation | 15 CPU-min | **GATES** product-rule chain confidence (P=0.38) |

**Tier 2 (conditional on Tier 1 outcomes)**: 2-C (ANY-HOP vs FINAL-HOP, P=0.38), 4-B (weakest-hop identification, P=0.43), 4-D (PRODUCT vs MIN, P=0.40), 4-C (per-hop ECE composition, P=0.36), 2-B (bootstrap CI width, P=0.32). Total ~85 CPU-min if all dispatched.

**Sub-property addition**: PP-31 sub-property "refusal audit certificate" per 2-D (compliance differentiator).

## PP-28 edit-impact Algebraic Perturbation (4 refinements)

**Critical sequencing insight**: O(k·h) ≈ sub-10ms at k=10K compositions. DAG back-pointer walk (Mechanism 1, ALREADY PROMOTED v316) is the bottleneck, NOT perturbation scoring (Mechanism 2). Sequencing: Mechanism 1 first → Mechanism 2 as second pass; no additional registry reads needed.

**Tier 1 dispatch**:

| # | Refinement | Cost | P | Status |
|---|---|---|---|---|
| **R1** | **Scale accuracy MAE+rank at k=5000** | **30s CPU** | **0.72 per-comp / 0.48 top-50 ranking** | **MANDATORY GATE** |
| R2 | Linearization breakdown for correlated edits | 60s CPU | 0.45 (with 2nd-order correction) | Conditional on R1 baseline |
| R3 | Joint distribution rank-1 Gaussian cluster model | 2 min CPU | 0.55 (NOVEL abstraction) | Depends on R1 |
| R4 | Cert-chain integration (PP-30 multi-edit) | Integration test | 0.70 multi-edit correctness | Integration, not new mechanism |

**Sub-property addition**: PP-28 sub-property "rank-1 Gaussian cluster impact model" per R3 (novel abstraction for GDPR Art 17 audit reports — "Deleting entity X affects these 7 composition clusters, impact ~N(μ,σ²)").

## PP-30 DR cert-chain replay protocol (4 candidates)

**Tier 1 dispatch**:

| # | Candidate | Eng-days | P | Specialty |
|---|---|---|---|---|
| **A** | **Full Replay + Seeded Codebook (FP32)** | **3-5** | **0.42** | Baseline; 160× backup compression via seeded codebook |
| **D** | **INT32 Deterministic Replay** | **7-10** | **0.40** | Bit-exact cross-machine; STRONGEST HIPAA "exact-copy" claim |

**A+D parallelized: 8-12 days combined**

**Tier 2** (post A+D PASS):

| # | Candidate | Eng-days | P | Specialty |
|---|---|---|---|---|
| **B** | Snapshot + Delta Replay | 5-8 | 0.38 | Makes N=65536 viable (snapshot 17GB→4GB INT8 compressed) |
| **C** | Streaming Auditor Protocol | 6-9 | 0.35 | **SOC 2 + HIPAA AUDITOR DIFFERENTIATOR** — auditor verifies any cert window WITHOUT trusting replaying party |

**Total sequential 11-17 days** for all 4 candidates.

**Sub-property addition**: PP-30 sub-property "streaming auditor protocol" per Candidate C (SOC 2 + HIPAA auditor-trust differentiator).

**MANDATED design decision**: seeded codebook required (8-byte seed regenerates entire codebook via `sign(hash(atom_id, seed))`); cert chain 400KB + seed = ~160× backup compression vs 64MB W matrix.

## CONSOLIDATED CONDITIONAL LIFTS (post Tier 1 PASS)

| Row | Current | Post-Tier 1 |
|---|---|---|
| PP-31 calibrated-confidence | promoted in v316 | → ✅ if 2-D + 2-A + 4-A all PASS |
| PP-28 edit-impact | promoted in v316 | → further LIFT if R1 PASS |
| PP-30 DR-Merkle-randproj | promoted in v316 | → further LIFT if A + D PASS |

## CONTRACT FOR STRATEGY

1. **Dispatch Tier 1 across all 3 drills** (~40 CPU-min combined + cert-chain integration test)?
2. **Authorize 3 sub-property additions** (refusal audit cert / rank-1 Gaussian cluster / streaming auditor protocol)?
3. **Authorize PP-30 seeded-codebook design mandate** (160× backup compression)?
4. **Sequence Tier 2 / Tier 3** per Tier 1 outcomes?
5. **PP-30 A+D parallelized engineering** (8-12 days) — testbed handoff after research closure?

## METHOD NOTES

- 3 parallel Sonnet drills + synthesis; per [[feedback-no-preframe-batch-all-pass]] explicit HP/MID/HF bands per design
- Per [[feedback-no-experiment-design-in-prompts]]: deliverables hand TASK + WHY + CONTRACT + AUTONOMY; sweep grids and exact thresholds remain exp_dev's call

## CLOSING

Move to `routed_completed/` when strategy authorizes Tier 1 dispatch + sub-property additions + PP-30 design mandates.


**Acted-on 2026-06-01:** PP-31 Tier 1 (2-D + 2-A + 4-A) + PP-28 R1 mandatory gate AUTHORIZED via exp_dev dispatch; 3 sub-properties added (PP-31a / PP-28a / PP-30a); PP-30 seeded-codebook design mandate added; PP-30 A+D parallel engineering routed to testbed via testbed_handoff_pp30_replay_protocol_a_d_parallel_engineering_2026-06-01.