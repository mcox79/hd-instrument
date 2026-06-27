# Prereg: multihop_kbeam_pathsum_v1

Date: 2026-06-27
Author: exp_dev (spawn) per M4 belief-propagation drill recommendation
Cell: `experiments/exp_multihop_kbeam_pathsum_v1.py`
Routing: `remote_cpu_queue` (USER 2026-06-27 NO LOCAL directive)
Drill source: `notes/research_drill_brain_multihop_M4_belief_propagation_soft_message_passing_3x_2026-06-27.md`

## Strategic rationale

The 2026-06-27 M4 drill REJECTED a direct soft-message-passing re-try because the
2026-06-24 beta-sweep cell already fairly tested moderate-temperature soft
superposition (ARM_BETA_2 with entropy ~ 2.84 nats = log(16) effective candidates)
and HARD_FAILED:

- ARM_BETA_2 top1 = 0.6483 (3-seed mean)
- ARM_BASELINE_HARD top1 = 0.6500 (3-seed mean)
- delta = -0.0017 (within noise; soft mechanism does NOT help at 2-hop)

The drill diagnosed the failure mode as **correlated-error amplification on
rank-1 cleanup against a shared codebook** (not temperature mis-calibration).
Cross-domain anchors:
- Particle-filter weight degeneracy under correlated resampling
- LDPC EXIT-chart no-swath when no extrinsic-info separation between hops
- Loopy-BP overconfidence via correlated cleanup re-circulation
- Rank-1 superposition collapse in HRR family at high K

The drill RECOMMENDED K-beam path-sum as a substrate-native alternative that
addresses the actual failure mode: maintain K diverse beam members per hop;
at terminal, sum scores across all surviving paths to favor candidates reached
via MULTIPLE chains (consensus across paths breaks correlated-error rank-1
collapse).

Brain analog: DDM (drift-diffusion model) sequential evidence accumulation
uses DIFFERENT POPULATIONS of neurons for sequential samples (Gold-Shadlen
2007) -- explicitly avoiding the substrate's "same W, same E codebook, same
cleanup" anti-pattern. K-beam's per-path separate state is structurally
analogous to DDM-with-different-populations.

## Configuration (FULL run)

- N_DIM = 8192 (substrate canonical dim; matches 2026-06-24 beta-sweep for
  direct delta comparability with prior cell)
- V_CONCEPTS = 200
- V_PREDICATES = 2 (p1=0/p2=1 fixed-pair; beta-sweep regime for sanity rail
  reproducibility)
- K_SET_CLEANUP = 20 (candidates per hop available for argpartition)
- K_BEAM_C = 10 (primary mechanism arm)
- K_BEAM_D = 10 (argmax-control arm; isolates path-sum vs just K candidates)
- K_BEAM_E = 30 (wider-beam saturation/scale probe)
- BETA_2_VALUE = 2.0 (anchors discriminator arm to 2026-06-24 BETA_2)
- N_CHAINS = 200 per seed
- SEEDS = [7, 17, 23] (3 seeds for CV)
- HOP_DEPTHS = [3, 5, 7] (primary measurement depths)
- SANITY_DEPTH = 2 (rails for 2026-06-24 reproduction)

## Cardinality (META_RULE_H mandatory)

- 5 arms x 3 seeds x [d3, d5, d7] = **EXPECTED_N_UNITS = 45**
- Sanity rails (BASELINE_TOP1 d2 + BETA_2_REPLICATE d2) computed separately
  per seed (NOT counted in EXPECTED_N_UNITS).
- **HARD_FAIL_CARDINALITY_BREACH** if observed total < 45.
- Cell asserts cardinality in verdict; metrics.json includes `cardinality_ok`
  field.

## Arms (5 total)

| Arm | Mechanism | Role |
|---|---|---|
| A: ARM_BASELINE_TOP1 | per-hop argmax cleanup | baseline; reproduces substrate per-hop-cleanup ceiling |
| B: ARM_BETA_2_SANITY_REPLICATE | soft-superposition beta=2 over top-K=20 | sanity rail; reproduces 2026-06-24 BETA_2 |
| C: ARM_KBEAM_K10_PATHSUM | K=10 beam + path-sum aggregation at terminal | the mechanism |
| D: ARM_KBEAM_K10_ARGMAX | K=10 beam but argmax-per-hop (NO path-sum) | control; isolates path-sum as load-bearing |
| E: ARM_KBEAM_K30_PATHSUM | K=30 beam + path-sum | wider-beam saturation probe |

Per-arm HP scope (SCHEMA-VET 5b):
- Arms **C and D ONLY** can fire HARD_PASS (the mechanism + its control).
- Arms A and B are SANITY/RAIL (sanity-only; cannot fire HP).
- Arm E is a SCALE PROBE (HARD_PASS not gated on it; informative for the
  K=10 vs K=30 saturation question).

## Pre-reg HARD bands (sacrosanct, both directions)

**PRIMARY metric:** ARM_KBEAM_K10_PATHSUM at depth-5 top1 (mean across 3 seeds)

- **HARD_PASS** (all three required):
  - K10_PATHSUM d5 top1 >= **0.45** (deflated from naive 0.65; substrate's
    actual 5-hop baseline is ~0.17 per 2026-06-26 pointer-chain ceiling work)
  - (K10_PATHSUM d5 - K10_ARGMAX d5) >= **0.10** (path-sum load-bearing,
    NOT just having K candidates)
  - cv across seeds <= **0.10**

- **MIDDLE_BAND**:
  - K10_PATHSUM d5 in [0.25, 0.45) **OR**
  - path-sum-over-argmax lift in [0.05, 0.10)
  - (partial-mechanism band; path-sum measurably helps but below
     chain-grade ceiling)

- **HARD_FAIL**:
  - K10_PATHSUM d5 < 0.25 **OR**
  - (K10_PATHSUM - K10_ARGMAX) < 0.05
  - (path-sum cannot escape correlated-error rank-1 collapse; pivot to
     encoder/W-capacity track)

- **SANITY_BREACH** (cell un-interpretable):
  - ARM_BASELINE_TOP1 depth-2 outside [0.60, 0.70] **OR**
  - ARM_BETA_2_SANITY_REPLICATE depth-2 outside [0.60, 0.70]
  - (setup drifted from 2026-06-24 beta-sweep regime; do NOT interpret
     main arms)

- **HARD_FAIL_CARDINALITY_BREACH**: observed n_units < 45

## Why HARD_PASS bar is 0.45 not 0.65 (band-calibration regime check, USER S)

- 2026-06-24 beta-sweep cell: baseline at 2-hop ~ 0.65
- 2026-06-26 pointer-chain hybrid v2: baseline at 5-hop ~ 0.17 (per-hop
  cleanup; same V_C=200, N=8192, K_SET=20 regime)
- A 5-hop HARD_PASS of 0.65 would be 4x the actual baseline -- closer to
  random than achievable for soft-mechanism family
- 0.45 = 2.6x lift over 0.17 baseline; lit-defensible per particle-filter
  diversity-preserving resampling outperformance regime
- USER M-S BIAS_15 (band-calibration regime checks; capacity-feasible)

## By-construction-saturation rule

If K10_PATHSUM d5 == 1.000 (exact) AND cv < 0.001 across seeds:
- Tier as **DIAGNOSTIC_PASS** (not chain-grade)
- Reason: at V_C=200, N=8192, N_CHAINS=200, only 200 unique 5-hop paths
  in W -- if path-sum perfectly recovers all 200, may be by-construction
  saturated. Skunkworks tiers; cell-author reports honest metrics.
- USER Q (suspect 1.000 results) + Fix #28 (cert-classification from
  cert-owner not cell-author framing)

## Self-test gate (formula-selftests)

At D=512, V=30, P=2, 8 chains, max_depth=3:
- (a) primitives run; outputs in [0, V).
- (b) K=1 path-sum matches baseline_top1 on >=3 of 4 queries (wiring check;
  single chain = no beam).
- (c) K=3 path-sum diverges from K=1 path-sum on at least 1 of 4 queries
  (proves beam mechanism is exercised, not no-op).
- (d) K=10 pathsum diverges from K=10 argmax on at least 1 of 4 queries
  (proves path-sum aggregation differs from argmax-per-hop).

Cell must `--self-test` exit 0 with selftest measurements matching expected.

## Smoke gate (META_RULE_K + META_RULE_M)

At N=2048, 1 seed, 50 chains, all 3 depths:
- Smoke runs full arm grid at smaller N (5 arms x 1 seed x 3 depths = 15 units).
- **META_RULE_M FULL-N PREVIEW**: at smoke time, ALSO runs single full-N
  preview point (K=10 pathsum + K=10 argmax + baseline at N=8192, depth=5,
  40 chains) to verify the discriminator survives full-N BEFORE dispatching
  the full run.
- Smoke MUST show K=10 pathsum diverges measurably from K=10 argmax at full-N
  preview (lift >= 0.05) OR full dispatch is at risk of HARD_FAIL.
- Smoke metrics.json includes `smoke_preview_fullN` field with the preview
  baseline/pathsum/argmax/lift values.

## Cell-level verdict mapping

- K10_PATHSUM d5 >= 0.45 AND lift >= 0.10 AND cv <= 0.10 -> HARD_PASS
- K10_PATHSUM d5 == 1.000 AND cv < 0.001 -> DIAGNOSTIC_PASS (by-construction)
- K10_PATHSUM d5 in [0.25, 0.45) OR lift in [0.05, 0.10) -> MIDDLE_BAND
- K10_PATHSUM d5 < 0.25 OR lift < 0.05 -> HARD_FAIL
- sanity breach -> SANITY_BREACH
- cardinality breach -> HARD_FAIL_CARDINALITY_BREACH

## Confound audit (per master bias checklist 2026-06-24 + M-S 2026-06-25)

- **A1 lit-scan calibration**: drill applied 0.15-0.20 deflation throughout;
  P_deflated(HARD_PASS) = 0.40.
- **F1 Fix #28**: per-arm metrics read from drill; ARM_BETA_2 was fair
  test not wiring bug; this cell uses ARM_BETA_2_REPLICATE as anchored
  sanity rail.
- **H2 saturated discriminator**: this cell does NOT re-do beta sweep;
  K-beam-path-sum is a distinct mechanism addressing the diagnosed
  rank-1 collapse failure mode.
- **H6 single-knob**: K is the swept knob (1 via K_beam wiring in self-test,
  10 in arms C/D, 30 in arm E); aggregation (pathsum vs argmax) is the
  control isolation.
- **M production-scale**: smoke includes full-N (N=8192) preview point on
  the primary discriminator to verify scale-survival pre-dispatch.
- **N verify-referent**: 2026-06-24 beta-sweep ARM_BETA_2 mean 0.6483 +/-
  per-seed verification done; baseline anchor 0.6500 verified.
- **Q suspect 1.000**: by-construction-saturation rule above.
- **R BIAS-13 contamination**: each chain uses fresh draws within a seed;
  used_s set prevents cross-chain s-collision; nodes within chain unique.
- **S band-calibration regime**: HARD_PASS 0.45 deflated from naive 0.65
  per substrate's actual 5-hop baseline ~0.17; 2.6x lift is achievable.
- **DISCRIMINATOR-MUST-SURVIVE-SCALE**: META_RULE_M full-N preview arm
  in smoke catches the discriminator-collapse-at-scale failure mode that
  burned ~10+ CPU-hr on 2026-06-26.

## What this does NOT show

- Whether K-beam beats POINTER-PIN (pointer-chain hybrid v2 already broke
  5-hop ceiling to 0.78 via a DIFFERENT mechanism; this cell tests the
  soft-message-passing-replacement question, not pointer-pin-dominance).
- Whether path-sum generalizes beyond fixed-pair predicates (V_P=2 here;
  V_P=10 follow-up if HARD_PASS).
- Whether path-sum holds at depth 10+ (drill capped at depth 7 for compute).
- Whether path-sum helps OUT-OF-DISTRIBUTION chains (holdout follow-up cell
  if HARD_PASS).
- Encoder questions (this cell uses dense-bipolar HRR for direct
  comparability with 2026-06-24 beta-sweep; encoder swaps are separate work).

## Compute estimate (per-seed runtime)

- Per chain: 5 arms x 3 depths = 15 mechanism invocations.
- Per invocation: roughly K_BEAM x depth matmul ops of size (V_C x N) for
  cleanup score.
- Estimate per seed: ~ 15min at N=8192, V_C=200, 200 chains, K_BEAM=30 cap.
- 3 seeds: ~ 45-60min wall, with overhead. Timeout = 5400s (1.5h) gives
  margin for slow first-seed cold-cache + W-build.

## Cites

- `notes/research_drill_brain_multihop_M4_belief_propagation_soft_message_passing_3x_2026-06-27.md` (drill spec; load-bearing)
- `experiments/exp_substrate_resonator_softchain_beta_sweep_v1.py` (2026-06-24 beta-sweep; BETA_2 anchor)
- `experiments/exp_substrate_multihop_pointer_chain_hybrid_v2_BASELINE_RAIL_FIXED.py` (2026-06-26 pointer-chain ceiling)
- USER 2026-06-27 NO LOCAL directive (routing to remote_cpu_queue)
- USER 2026-06-26 DISCRIMINATOR-MUST-SURVIVE-SCALE (META_RULE_M full-N preview)
- USER 2026-06-26 CARDINALITY_OK mandatory (META_RULE_H)
- USER 2026-06-24 EXPERIMENT BIAS MASTER CHECKLIST (M/N/O/Q/R/S sections)
- USER 2026-06-22 Fix #28 (per-arm metrics; cert-classification from cert-owner)
- Doucet-Johansen particle-filter tutorial (weight degeneracy; diversity-preserving resampling)
- Gold-Shadlen 2007 (DDM with different neural populations for sequential evidence)
