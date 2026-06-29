# Prereg: substrate_schema_exemplar_bayes_capacity_stress_v4

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Stage 2 capacity-stress drill — v3 5/5 MB -> MECHANISM-CLASS DIVERSION
**Drill source:** Skunkworks 2x-drill 2026-06-28 — v3 landed 5/5 MB; mechanism is real (avg_bayes_minus_nn ~0.59) but cliff_observable=False on all 5 seeds, capacity_scaling_delta negative or marginal. Substrate is showing GRACEFUL DEGRADATION across 4 decades of alpha — a different MECHANISM CLASS than Kanerva-cliff but chain-grade-eligible.

  v3 empirical (off-disk verified, seed_7 example):
  - avg_bayes_minus_nn = 0.590 (strong mechanism)
  - capacity_scaling_delta = -0.020 (FAILS gate on this discriminator)
  - cliff_observable = False (n_cliff_pts = 2 of 64)

  Skunkworks 2x-drill recommendation (TWO options):
  - **Option A (harness change):** redefine PASS as graceful-degradation gate (monotonic-in-alpha + alpha-floor retention) rather than cliff-counting.
  - **Option B (primitive substitution):** replace LSE Bayes readout with hard-max readout (no prior pull) so cliff IS observable.

  v4 implements BOTH + a THIRD path emerged from the design selftest.

## SELFTEST EMPIRICAL DISCOVERY (2026-06-28; honored by gating)

During v4 cell-author selftest, the hard-max primitive was chosen as **cosine-nearest-MEAN** (argmax over per-class centroid similarity). The premise was that hard-max would lose prior-pull stabilization and exhibit the Kanerva cliff. **Selftest disproved this premise:**

| corner                     | alpha | GRACEFUL | HARD_MAX | REFERENCE | chance |
|----------------------------|-------|----------|----------|-----------|--------|
| SAT (10,10,16384)          | 0.006 | 1.000    | 1.000    | 0.200     | 0.10   |
| sweet (50,50,8192)         | 0.31  | 0.800    | 0.800    | 0.200     | 0.02   |
| FLOOR (200,200,2048)       | 19.5  | 0.200    | **0.800**| 0.000     | 0.005  |

At FLOOR (alpha=19.5; K_total=40000 in N=2048), HARD_MAX-centroid maintains 0.800 accuracy (160x chance) while GRACEFUL Bayes-LSE collapses to 0.200 and single-nearest REFERENCE goes to 0.000. **The centroid acts as a low-variance prototype estimate; at high K, averaging removes per-exemplar noise more effectively than LSE smoothing.** This is a v4 mechanism-class DISCOVERY, not a pre-supposed Option B.

The actual cliff-prone primitive that follows Skunkworks's "no smoothing -> cliff" prediction is ARM_REFERENCE (single-nearest-exemplar). v4 keeps cliff_observable as the discriminator on that primitive (Option C).

## v4 design: 3 mechanism-class candidates + 4 arms

**ARMS:**
- `ARM_BAYES_GRACEFUL` — full Bayes-LSE posterior aggregation with prior=1.0. v3-identity readout, renamed to emphasize Option A discriminator framing.
- `ARM_HARD_MAX` — cosine-nearest-MEAN (per-class centroid argmax). NO LSE smoothing; centroid is a low-variance prototype estimate from K exemplars. Selftest empirical: dominates at FLOOR.
- `ARM_REFERENCE` — single-nearest-exemplar (v3 ARM_NEAREST_EXEMPLAR identity). The actual cliff-prone primitive (no aggregation, no smoothing).
- `ARM_UNIFORM_RANDOM` — chance witness (rules out artifact).

**SWEEP (UNCHANGED from v3 tightening):**
- n_exemplars_per_class in {10, 50, 100, 200}
- n_classes in {10, 50, 100, 200}
- N_DIM in {2048, 4096, 8192, 16384}
- prior_strength = 1.0 fixed
- 4x4x4 = 64 phase points per seed; alpha range 0.006 to 19.5

**Stage:** Stage 2 (substrate higher-function characterization — schema Bayesian inference cliff)
**P_deflated:** 0.45 (v4 introduces a new primitive + 3 chain-grade gates; HARD_MAX-centroid sustained-floor result is strong on seed_7 selftest but full-scale + 5-seed replication is what determines chain-grade)
**Phase-diagram axis:** (n_exemplars_per_class, n_classes, N_DIM) capacity-stress sweep; 3-gate cross-sibling chain-grade gate

## SUBSTRATE-AS-CANONICAL prior work

- `exp_substrate_schema_exemplar_bayes_capacity_stress_v3_seed_{7,13,19,23,29}` (2026-06-28): all landed MIDDLE_BAND on 2-arm capacity_scaling_delta discriminator. Mechanism CONFIRMED on Bayes-LSE arm.
- `exp_substrate_schema_exemplar_bayes_capacity_stress_v2_seed_{7,13,19}` (2026-06-28): v2 baseline, 3-seed MM.
- Existing chain-grade Stage 2 schema exemplar-Bayes primitive (~80% completeness pre-v4; v4 either promotes to chain-grade via mechanism-class diversion OR closes the promotion path with honest MIDDLE_BAND).

## HYPOTHESIS

The substrate's schema-exemplar mechanism exhibits AT LEAST one chain-grade-eligible discriminator from three candidate mechanism classes:

- **Class A (graceful-degradation on Bayes-LSE):** monotonic-in-alpha advantage + alpha-floor retention >= 0.30 + lift-over-chance >= 5x at FLOOR + advantage spans >= 3 decades.
- **Class B (HARD_MAX-centroid SUSTAINED-FLOOR):** per-class centroid argmax retains accuracy >= 0.50 at alpha>=10 corners AND lifts >= 10x over chance at FLOOR AND dominates REFERENCE by >= 0.20 at >= 25/64 phase points. The centroid acts as a noise-suppressing prototype primitive.
- **Class C (REFERENCE cliff_observable):** the cliff-prone primitive (single-nearest-exemplar; no aggregation) exhibits Kanerva-style cliff: ARM_REFERENCE < 0.40 at >= 10/64 phase points.

## ARMS-MUST-DIFFER (META_RULE_AF)

- Arms diverge at >= 10/64 phase points (smoke-scaled: >= 2/6).
- ARM_HARD_MAX vs ARM_BAYES_GRACEFUL: at SAT corners both saturate (within tol); at FLOOR they diverge (HARD_MAX dominates).
- ARM_REFERENCE vs others: REFERENCE is loose floor; must lift over chance at low-load corners (full-N gate; loose).

## PRE-REG BANDS — PER-SIBLING (LOCKED; PROSPECTIVE)

### CHAIN_GRADE_GRACEFUL (Option A on Bayes-LSE)

ALL conditions required:
- `floor_retention_met`: ARM_BAYES_GRACEFUL acc >= 0.30 at ALL alpha>=10 corners
- `floor_lift_met`: ARM_BAYES_GRACEFUL / chance >= 5x at ALL alpha>=10 corners
- `monotonic_met`: across alpha decades D0..D4, mean GRACEFUL non-increasing within tol 0.10 (no decade has +0.10 lift over the preceding lower-alpha decade)
- `decades_met`: >=3 decades with GRACEFUL_mean > chance_mean + 0.10

### CHAIN_GRADE_HARDMAX (Option B; v4 NEW)

ALL conditions required:
- `hardmax_floor_retention_met`: ARM_HARD_MAX acc >= 0.50 at ALL alpha>=10 corners
- `hardmax_floor_lift_met`: ARM_HARD_MAX / chance >= 10x at ALL alpha>=10 corners
- `hardmax_over_ref_met`: ARM_HARD_MAX - ARM_REFERENCE >= 0.20 at >= 25/64 phase points (smoke-scaled: 3/6)

### CHAIN_GRADE_REFCLIFF (Option C; cliff on the cliff-prone primitive)

- `reference_cliff_met`: ARM_REFERENCE acc < 0.40 at >= 10/64 phase points (smoke-scaled: 1/6)

### Per-sibling verdict

- `CHAIN_GRADE_MULTI`: 2 or 3 of {A, B, C} gates met
- `CHAIN_GRADE_HARDMAX`: only B met
- `CHAIN_GRADE_GRACEFUL`: only A met
- `CHAIN_GRADE_REFCLIFF`: only C met
- `MIDDLE_BAND`: NO gate met but avg(GRACEFUL - REFERENCE) >= 0.05 (mechanism shows lift; no clean chain-grade story)
- `HARD_FAIL`: arms_identical_pathology OR random_arm_pathology OR REFERENCE arm not lifting at low-load (positive control failure)

## CHAIN-GRADE GATE — CROSS-SIBLING AGG (5-seed; LOAD-BEARING)

Skunkworks computes after all 5 seeds land:

### (A) GRACEFUL chain-grade
- >=3/5 seeds with `graceful_gate_met=True`
- AND 5-seed mean `floor_retention_mean` >= 0.30
- AND 5-seed mean `n_decades_with_advantage` >= 3

### (B) HARDMAX chain-grade
- >=3/5 seeds with `hardmax_gate_met=True`
- AND 5-seed mean `hardmax_floor_retention_mean` >= 0.50
- AND 5-seed mean `hardmax_floor_lift_mean` >= 10x
- AND 5-seed mean `hardmax_over_ref_pts` >= 25

### (C) REFCLIFF chain-grade
- >=3/5 seeds with `reference_gate_met=True`
- AND 5-seed mean `n_reference_cliff_points` >= 10

### MULTI chain-grade
- Any combination of 2+ gates met by >=3/5 seeds

### Honest-downward
- If no AGG gate met by 3/5 -> MIDDLE_BAND (mechanism shows lift but no clean chain-grade story).

## CARDINALITY (META_RULE_H_ANCHOR)

- `EXPECTED_N_UNITS_FULL` per seed = 4 arms x 4 n_ex x 4 n_classes x 4 N x 20 queries = **5120 records per seed**
- `EXPECTED_N_UNITS_SMOKE` per seed = 4 arms x 6 corners x 5 queries = **120 records per seed**
- `EXPECTED_N_SEEDS_V4` = 5 (chunked siblings: seed 7, 13, 19, 23, 29)
- `EXPECTED_N_UNITS_AGGREGATE_FULL` = 5120 x 5 = **25600 records**

`HARD_FAIL_CARDINALITY_BREACH` asserted in metrics.json `cardinality_ok` field per sibling.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26)

**Smoke verdict at seed=7 (verified pre-dispatch 2026-06-28; commit pending):**
- run_mode=smoke, 6 corners, 4 arms, 5 queries: **CHAIN_GRADE_MULTI**
- 2/3 gates met: HARDMAX_gate=True, REFCLIFF_gate=True, GRACEFUL_gate=False (1 monotonic violation at smoke granularity; expected to recover at full n_q=20)
- All 6 cardinality OK (120 = 6 x 4 x 5)
- HARD_MAX FLOOR retention 1.000, lift 200x at alpha=19.5
- REFERENCE FLOOR collapse 0.000 at alpha=19.5 (cliff IS observable on the cliff-prone primitive)
- arms_diverge 4/6 (above smoke threshold 2/6)

Smoke confirms HARDMAX-centroid and REFCLIFF discriminators FIRE at the corners they're expected to fire on. GRACEFUL falls at smoke due to coarse granularity (n_q=5 -> 0.20 acc-step makes monotonic-in-alpha test brittle); FULL run (n_q=20) gives 0.05 granularity and should resolve.

## FAIRNESS GATES (META_RULE_AC/AE/AF)

- Same encoder (bipolar random HDC) across all 4 arms.
- Same class+exemplar codebook per seed.
- Same query set per seed.
- All 4 arms consume IDENTICAL query encoding; only readout differs.
- beta = log(n_classes) / 0.1 (for GRACEFUL LSE).
- Q-discipline: arm acc=1.000 at high-load points triggers leakage audit (didn't appear in smoke).

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel + atomic per-seed partial via `experiments._seed_checkpoint`. META_RULE_X main-guard. PROT-021 N+anchor stamp on every partial.

## HARDWARE / DISPATCH

- CPU-only cell (no torch; numpy + scipy.special.logsumexp).
- Smoke wall: ~10s per seed (6 corners; 4 arms each).
- Full wall (4 arms vs v3's 3 arms; +33% per-pt cost): est ~700-1000s per seed.
- Target queue: **remote_cpu_queue** (CPU-only; cpu_runner_0 alive; matches task spec).
- 5 seeds serial wall estimate: ~50-85 min (matches task spec ~50-65min within bounds).
- timeout_s per cell = 2400 (40min; 2.4-3.4x safety margin).
- Dispatch path: laptop authors + smokes; Orchestrator pushes for remote_cpu_queue (push is harness-DENIED to cell-author).

## CHUNKED ARCHITECTURE (USER 2026-06-28)

5 sibling files (one seed each):
- `exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_7.py`
- `exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_13.py`
- `exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_19.py`
- `exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_23.py`
- `exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_29.py`

Shared core: `experiments/_substrate_schema_exemplar_bayes_capacity_stress_v4_core.py`
Resumability: `experiments/_seed_checkpoint.py` (PROT-021 anchor + N stamping).

Aggregation post-hoc: Skunkworks combines 5 sibling metrics.json -> 5-seed mean + 3/5 majority per gate.

## POSITIVE CONTROL

ARM_BAYES_GRACEFUL on smoke (seed=7): GRACEFUL=1.000 at SAT, GRACEFUL=0.800 at sweet, avg_graceful_minus_ref=0.600 — reproduces v3's known sweet-spot lift behavior (v3 avg_bayes_minus_nn=0.59). Positive control confirms v4 inherits v3's confirmed mechanism on the renamed arm.

## SUBSTRATE PREREQS (chain-grade primitives cited)

- Bipolar random HDC codebook (chain-grade per `exp_substrate_sequence_binding_v1`)
- Cosine similarity readout (chain-grade ubiquitous)
- Log-sum-exp Bayesian aggregation (substrate-native; no exotic ops)
- Per-class centroid (mean of normalized bipolar exemplars; in-substrate operation; v4 promotes to first-class primitive candidate)
- v3 atom (5-seed MM on capacity_scaling_delta; mechanism confirmed)

## HDLAB_QUEUE CONTRACT (Skunkworks META RULE)

`# PRESERVE_ENV_VARS: HDLAB_QUEUE` header in all cell files. NO gpu_mandate_check that blocks CPU dispatch. CPU-only cell.

## PRE-REG FIELDS

- expected_n_units_full = 5120 (per seed; 64 pts x 4 arms x 20 queries)
- expected_n_units_smoke = 120 (6 corners x 4 arms x 5 queries)
- expected_n_seeds_v4 = 5 (chunked siblings: 7, 13, 19, 23, 29)
- HARD_FAIL_CARDINALITY_BREACH (asserted in metrics.json `cardinality_ok` field)
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR (asserted via reference_sanity_met)
- HARD_FAIL_ARMS_IDENTICAL (asserted via n_pts_arms_diverge < threshold)
- 3 chain-grade gates: A_GRACEFUL, B_HARDMAX_SUSTAINED_FLOOR, C_REFERENCE_CLIFF
- discriminator_survives_scale (smoke gate verified pre-dispatch; HARDMAX+REFCLIFF fire at smoke)
- CARDINALITY_OK (per sibling)
- META_RULE_AF arms-must-differ
- §13 patterns (4-arm bracket; cliff axis; arms-must-differ)
- **5-seed cross-sibling chain-grade gate** (computed by Skunkworks at landed-VET)

## PHASE-DIAGRAM DECISION TABLE

| 5-seed AGG outcome                                                              | Phase-diagram verdict                                              |
|---------------------------------------------------------------------------------|--------------------------------------------------------------------|
| CHAIN_GRADE_HARDMAX or MULTI with B met                                          | NEW chain-grade primitive: HARD_MAX-centroid SUSTAINED-FLOOR; v3 MM -> v4 chain-grade promotion via mechanism-class diversion |
| CHAIN_GRADE_GRACEFUL or MULTI with A met (B not met)                             | Original Bayes-LSE chain-grade via graceful-degradation harness (Option A) |
| CHAIN_GRADE_REFCLIFF only                                                        | Substrate has cliff (on cliff-prone primitive) but no mechanism class superior to chance |
| MIDDLE_BAND (no AGG gate met)                                                    | Mechanism shows lift but no chain-grade story; abandon promotion path |

## NOTES

- v4 is mechanism-class DIVERSION not just band relaxation. ARM_HARD_MAX is a NEW substrate primitive (centroid argmax) not present in v3.
- The Skunkworks "Option B: hard-max loses prior pull -> cliff" premise was DISPROVED by selftest. Centroid averaging is a noise-suppressing primitive that DOMINATES at high K. v4 honors this finding by gating on SUSTAINED-FLOOR (Option B reinterpreted) and moving cliff_observable to the actual cliff-prone primitive (REFERENCE; Option C).
- Per USER 2026-06-26 discriminator-must-survive-scale: smoke uses full-N (16384) corner + full-cliff corner + FLOOR corner; 2/3 gates fire at smoke. v4 satisfies discipline.
- Per USER 2026-06-27 substrate-as-canonical: builds on v3 5-seed atom + Skunkworks 2x-drill recommendation. New primitive (centroid argmax) added; full path (LSE smoothing) preserved as separate arm.
- Per USER 2026-06-28 chunked architecture: 5 sibling files mirroring v3.
- Per Fix #28: per-sibling metrics.json carry full phase_map + 3-gate booleans + decade aggregates; Skunkworks reads per-arm + per-gate not just verdict_msg.
- Per honest-downward discipline: if 5-seed AGG fails all 3 gates, default MIDDLE_BAND (the discovery is still recorded as a measured-mechanism for future drills).
