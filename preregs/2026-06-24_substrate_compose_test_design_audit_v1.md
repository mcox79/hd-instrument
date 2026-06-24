# Pre-reg: substrate_compose_test_design_audit_v1

**Date:** 2026-06-24
**Author:** exp_dev (cell-author)
**Anchor:** `substrate_compose_test_design_audit_v1`
**Routing:** local_cpu_queue (CPU-bound matmul; ~45-60min wall)
**Trigger:** A1 3rd-angle drill (`notes/research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md`)

---

## Question

Is A1's catastrophic FULL_JOINT BPC=7.89 a TEST-DESIGN ARTIFACT (60-75% per drill)
or a STRUCTURAL collapse?

The drill identified 5 design biases that each independently pre-bias toward
sub-additivity. The smoking-gun precedent
(`exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512`) HARD_PASSed
super-additive with IDENTICAL plasticity primitives. This cell tests whether the
SAME primitive mechanism stack composes DIFFERENTLY when the 5 design biases are
varied.

## Five design biases (per A1 drill)

1. **MH-certified-at-wrong-regime** (ST9 self-test validates pattern-completion;
   cell uses MH for LM-readout)
2. **TEMP_GRID pegs at T=1.0** (best_T_for_bpc=1.0 across all lambdas in A1
   FULL_JOINT; grid maxes at top -> true optimum outside grid)
3. **N_STEPS=1000 under-asymptotic** (cf-RPE asymptotes at N=5000 per
   n_steps_curve; A1 trains at N=1000)
4. **Cumulative-build loses interaction info** (no factorial decomposition;
   can't localize which interaction destroys compose)
5. **Shared-frozen HPs** (CFRPE_LR / STDP_WEIGHT / MH_BETA / GATE_TEMP frozen
   across arms; composes need different HPs than isolation)

## Arms (six; same primitives as A1; design varies)

1. **ARM_A1_BASELINE** -- reproduces A1's FULL_JOINT at A1 settings; provenance
   rail (target ~7.89)
2. **ARM_FIX_TEMP_GRID** -- A1 FULL_JOINT + extended TEMP_GRID
   `[0.01, 0.05, 0.2, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]`; addresses bias #2
3. **ARM_FIX_N_STEPS** -- A1 FULL_JOINT + N_STEPS=5000 to reach asymptote;
   addresses bias #3
4. **ARM_FIX_NON_CUMULATIVE_BUILD** -- K=2 + cf-RPE+STDP WITHOUT MH cleanup;
   isolates the K=2 hetplast pair from MH degradation; addresses bias #4
5. **ARM_FIX_PER_ARM_HP_TUNED** -- A1 FULL_JOINT but MH_BETA in {1.0, 2.0, 4.0}
   inner-sweep (pick best dev BPC); addresses bias #5
6. **ARM_FIX_ALL_5_TOGETHER** -- combined fixes (extended T-grid + N_STEPS=5000
   + per-arm MH_BETA sweep + MH cleanup OFF for one variant); the test-design-
   corrected A1; PRIMARY arm

## Pre-registered HARD bands (both directions; bias #5 audit / single primary)

**Primary arm:** `ARM_FIX_ALL_5_TOGETHER` BPC (lower = better)

**Sanity rail (provenance):**
- `ARM_A1_BASELINE` BPC within +/-0.10 of 7.89 reference  
  (looser than 0.05 tolerance; this arm SHOULD reproduce A1 catastrophic failure)
- If sanity rail fails -> HARD_FAIL_PROVENANCE (cell didn't reproduce A1
  failure mode; comparison invalid)

**HARD_PASS_TEST_DESIGN_ARTIFACT:** `ARM_FIX_ALL_5_TOGETHER` BPC <= 7.30
- Interpretation: design fixes recover compose to A1 baseline level
  (fair_harness 7.3065); 60-75% of A1 failure was test-design artifact
- "Composition isn't catastrophically broken; A1's test wasn't sensitive
  enough to detect working compose"

**HARD_PASS_SUPER_ADDITIVE:** `ARM_FIX_ALL_5_TOGETHER` BPC <= 7.00
- Interpretation: composition is SUPER-additive once design biases removed
- "Substrate compose is alive AND beats the best single primitive on the
  task-design-corrected harness"

**MIDDLE_BAND:** `ARM_FIX_ALL_5_TOGETHER` BPC in (7.30, 7.50]
- Interpretation: partial recovery; ~40-50% of A1 was test-design, remainder
  structural; both A1 angle-2 (near-decomposability) and angle-3 (test-design)
  load-bearing

**HARD_FAIL_STRUCTURAL_CONFIRMED:** `ARM_FIX_ALL_5_TOGETHER` BPC >= 7.70
- Interpretation: ALL 5 design fixes don't help meaningfully; A1's structural
  Angle 2 diagnosis (near-decomposability with violated weak-coupling) dominates
- "Substrate compose IS structurally broken; methodology cleanup doesn't
  save it"

**Per-arm CONTRIBUTION (each FIX_X arm vs ARM_A1_BASELINE):**
- Each `ARM_FIX_X` reports lift over `ARM_A1_BASELINE` -> attributes share of
  A1's 7.89 - X.XX collapse to that single bias
- No HARD band on individual FIX arms (they're diagnostic; the verdict comes
  from ARM_FIX_ALL_5_TOGETHER)

## Apples-to-apples (master bias checklist)

- **Lane 1 declared:** substrate-native composition mechanism comparison
  (primitives constant; test-design varies)
- **CONFOUND_AUDIT:** ARM_FIX_PER_ARM_HP_TUNED could overfit (inner MH_BETA
  sweep -> 3x more configs scored on dev). Mitigated by reporting test BPC
  at dev-best HP (standard double-split discipline).
- **INTRA_LANE_DELTA:** each ARM_FIX_X varies ONE design choice from
  ARM_A1_BASELINE; ARM_FIX_ALL_5_TOGETHER combines them
- **PRIMARY metric:** BPC (lower = better)
- **SECONDARY metric:** top1 accuracy
- **PRE-REGISTERED PRIMARY ARM:** `ARM_FIX_ALL_5_TOGETHER`

## Config

```
N_DIM=8192, V=4000, N_TRAIN=100_000, N_HELD=20_000 (text8)
Encoder: word2vec_sparse_bipolar f=0.05 (matches A1 / fair_harness chain-grade)
Seeds: [7, 17, 23] (matches A1)
Primitives: ALL five mechanisms held constant as A1; only test design varies
Local CPU: timeout=5400s (90min wall; A1 was ~30min CPU + ARM_FIX_N_STEPS 5x
  steps -> ~60min; ARM_FIX_PER_ARM_HP_TUNED 3x configs on FULL_JOINT only)
```

## Self-test gates (formula-selftests; mandatory)

- ST1-ST14: inherited from A1 cell (primitive equivalence)
- ST_DESIGN_FIX_1: ARM_FIX_TEMP_GRID extended grid range OK (T_max == 50.0)
- ST_DESIGN_FIX_2: ARM_FIX_N_STEPS reads N_STEPS=5000 in full mode
- ST_DESIGN_FIX_3: ARM_FIX_NON_CUMULATIVE_BUILD has mh_cleanup=False
- ST_DESIGN_FIX_4: ARM_FIX_PER_ARM_HP_TUNED MH_BETA_SWEEP = [1.0, 2.0, 4.0]
- ST_DESIGN_FIX_5: ARM_FIX_ALL_5_TOGETHER applies ALL of the above

## Verify-the-referent

- A1 metrics file (target reproducibility): `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json`
  - A1 FULL_JOINT bpc=7.8919 (verified)
- Smoking-gun precedent: `data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json`
  - HARD_PASS super-additive gap=3.744 nats
- A1 3rd-angle drill: `notes/research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md`

## Cites

- A1 source: `experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py`
- A1 metrics: `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json`
- A1 3rd-angle drill: `notes/research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md`
- Smoking gun: `data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json`
- N_STEPS asymptote: `data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json`

## What this does NOT show

- K>2 not tested (held at K=2 per A1 for primitive-constant audit)
- Gate not end-to-end trained (held at GATE_TEMP=0.5 per A1; ARM_FIX_PER_ARM_HP
  sweeps MH_BETA only)
- factorial 2^4=16 decomposition NOT run (that's escape-path B in the drill;
  separate cell if this primary returns HARD_FAIL or MIDDLE)
- TEMP_GRID extension MAY introduce numerical overflow at T=50 (softmax very
  cold); cell asserts logits finite at every T

## Honest scope

"Tests whether A1's FULL_JOINT HARD_FAIL is dominantly test-design artifact
(P_deflated=0.75 per drill) by holding the 5 substrate primitives constant and
varying each of the 5 identified test-design biases independently + combined.
The verdict on ARM_FIX_ALL_5_TOGETHER falsifies one of {test-design dominant,
structural dominant, mixed} at 0.20 BPC discrimination."
