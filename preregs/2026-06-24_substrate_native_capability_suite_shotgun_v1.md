# Pre-registration: substrate_native_capability_suite_shotgun_v1

**Date:** 2026-06-24
**Anchor:** substrate_native_capability_suite_shotgun_v1
**Queue:** remote_cpu_queue
**N_DIM:** 8192, **Sparse f:** 0.05, **Seeds:** [7, 17, 23]
**Arms:** 6 (PATTERN_COMPLETION / COMPOSITIONAL_GEN / WORKING_MEMORY /
RETRIEVAL_PRECISION / SEQUENCE_BINDING / SPARSITY_F)
**Lane:** 1 (substrate-native capability; apples-to-apples synthetic)
**Corpus provenance:** SYNTHETIC (sparse-bipolar from rng; NO text / NO encoder / NO transformer)

## Scientific question

USER master bias checklist Lane 1: substrate has CHAIN-GRADE individual capabilities
confirmed in separate cells (ANCHOR 1 capacity-respecting M=20 / ANCHOR 2 K10-K20
compositional / brain-aligned shotgun ARM 1 pattern-completion top1=1.000 / ARM 3 WM
capacity=15 / ARM 4 bidirectional top1=0.884). No UNIFIED substrate-native benchmark
suite exists at production scale. This cell ships the first such suite: comprehensive,
apples-to-apples, synthetic, 6-arm, 3-seed.

If suite-alive at production scale, the substrate-product story has a rigorous unified
foundation. If suite-partial, identifies specific gaps. If suite-dead, the per-cell wins
don't scale together (interaction effects).

## Arms (6 total; all share substrate primitives -- only TASK varies)

1. **ARM_PATTERN_COMPLETION_AT_CORRUPTION** -- M=200 sparse-bipolar patterns; corrupt
   50% of bits; cleanup via cosine over codebook. PRIMARY metric: top1_recovery_rate.
2. **ARM_COMPOSITIONAL_GENERALIZATION_HOLDOUT** -- 20 subj x 20 obj = 400 pairs;
   bind 200 (coverage=0.5); recover heldout 200 obj given subj. PRIMARY: heldout_top1.
3. **ARM_WORKING_MEMORY_CAPACITY_SCALING** -- k in {1,4,7,10,15,20,30}; trials_per_k=40;
   capacity = largest k with accuracy >= 0.90. PRIMARY: k_capacity_at_90pct.
4. **ARM_RETRIEVAL_PRECISION_AT_LOAD** -- M in {100,500,1000,2000} at fixed N_DIM=8192;
   recall@1 per M. PRIMARY: recall_at_1_at_M_target (M=1000).
5. **ARM_SEQUENCE_BINDING_LOSSLESS** -- K in {5,10,20,50}; trials_per_K=20; vocab=60;
   sequence bind/unbind exact-recovery. PRIMARY: exact_recovery_at_K_target (K=20).
6. **ARM_SPARSITY_F_SWEEP** -- f in {0.005,0.01,0.02,0.05,0.10} at fixed M=500;
   per-f recall@1. PRIMARY: capacity_ratio_f002_over_f005.

## Apples-to-apples discipline (Lane 1)

- Lane 1 declared: substrate-native capability.
- INTRA_LANE_DELTA: all arms use IDENTICAL substrate primitives (HRR bind/unbind via
  FFT circular convolution + sparse-bipolar codebook at f=0.05; cosine cleanup).
  Only the TASK varies between arms.
- NO corpus (no Pythia, no word2vec, no transformer baseline, no text8, no shakespeare).
- NO encoder learning, no plasticity, no cf-RPE, no gradient updates.
- SYNTHETIC data only (sparse-bipolar vectors drawn from rng).
- PRIMARY metric per arm declared (single metric, NOT OR-gated per top-5 bias #1).
- CONFOUND_AUDIT documented per arm in the cell docstring.

## Pre-registered HARD bands per arm (sacrosanct both directions)

| Arm | HARD_PASS | HARD_FAIL | MIDDLE_BAND |
|-----|-----------|-----------|-------------|
| PATTERN_COMPLETION (top1) | >= 0.85 | < 0.50 | [0.50, 0.85) |
| COMPOSITIONAL_GEN (heldout_top1) | >= 0.50 | < 0.20 | [0.20, 0.50) |
| WORKING_MEMORY (capacity_min) | >= 7 (Miller) | < 4 | [4, 7) |
| RETRIEVAL_PRECISION (recall@M=1000) | >= 0.95 | < 0.70 | [0.70, 0.95) |
| SEQUENCE_BINDING (exact@K=20) | >= 0.99 | < 0.90 | [0.90, 0.99) |
| SPARSITY_F (ratio f0.02/f0.05) | >= 1.5 | <= 1.0 | (1.0, 1.5) |

## Cell-level verdict

- **ARM_SUITE_NATIVE_ALIVE**: ALL 6 arms HARD_PASS -> substrate-native uniformly
  chain-grade. The substrate has a comprehensive native capability suite that
  passes at production scale.
- **ARM_SUITE_NATIVE_PARTIAL**: 4-5 of 6 arms HARD_PASS -> substrate has strong native
  suite with 1-2 specific gaps to characterize/fix.
- **ARM_SUITE_NATIVE_DEAD**: <= 3 of 6 arms HARD_PASS -> substrate-native suite has
  fundamental gaps; the per-cell wins do not compose into a unified production-scale
  suite without interaction-effect mitigation.

## Calibration rationale (per band)

- **PATTERN_COMPLETION 0.85**: matches brain-aligned shotgun ARM 1 reference
  (top1=1.000 reported; 0.85 = ample margin below). Cleanup is the most fundamental
  substrate operation; substrate-product story REQUIRES this arm.
- **COMPOSITIONAL_GEN 0.50**: CORRECTED protocol (not pair-collision-bound; chance is
  1/n_obj=0.05). Brain-aligned ARM 2 reported holdout 0.50-0.70 region in prior runs;
  0.50 is conservative substrate-product floor; 0.20 = 4x chance HARD_FAIL line.
- **WORKING_MEMORY >= 7**: Miller 7+/-2 (1956). Brain-aligned ARM 3 reported capacity=15
  at smoke; production should sustain >= 7 (lower bound of Miller). < 4 = sub-Miller
  HARD_FAIL.
- **RETRIEVAL_PRECISION 0.95 at M=1000**: substrate-mining drill at sparse-bipolar
  N_DIM=8192 f=0.05 reports near-perfect recall through M~1500; 0.95 at M=1000 is
  the substrate-mining-confirmed band. < 0.70 at M=1000 = decisive capacity-cliff
  HARD_FAIL.
- **SEQUENCE_BINDING 0.99 at K=20**: HRR with position-codebook is by-design near-
  lossless at K=20 below capacity ceiling; 0.99 is the "lossless target" floor.
  < 0.90 at K=20 = sequence-binding broken HARD_FAIL.
- **SPARSITY_F ratio >= 1.5**: substrate-mining drill finds lower f (more spread)
  raises capacity at fixed M (because crosstalk scales M*f^2/D). The 1.5x ratio of
  f=0.02 recall over f=0.05 recall at M=500 is the substrate-mining-confirmed
  separation. <= 1.0 = f=0.02 NOT better than f=0.05 = HARD_FAIL.

## Critical disciplines

- **Fix #28 per-arm metrics**: each arm's PRIMARY metric is recorded in per_seed;
  verdict reads per-arm numbers, NEVER trusts verdict_msg summary string.
- **Fix #26 predispatch_check**: ran clean (0 matching landings; 0 matching atoms;
  RECOMMENDATION: PROCEED).
- **Fix #14 ONE cell**: 6 arms in one cell is acceptable for a shotgun signal-
  detection sweep; not 6 separate cells (would saturate spawn budget).
- **A5 path-scoped commit**: cell + prereg only; never git add -A.
- **ASCII-only**: all code, comments, output.
- **Pure numpy CPU**: no torch / no CUDA; remote_cpu_queue dispatch.
- **Synthetic data only**: sparse-bipolar from rng; no substrate atoms; no labels;
  no encoder leakage (per USER 2026-06-23 clean-encoder-tests directive).
- **Self-test BEFORE smoke**: asserts HRR involutive + 6 arms mechanism operational
  at tiny dim (~1s wall). Selftest PASSED locally 2026-06-24.
- **Smoke BEFORE full dispatch**: 11.5s wall on local CPU; smoke verdict
  ARM_SUITE_NATIVE_PARTIAL (4 of 6 HARD_PASS; CG and SP "fail" at smoke are smoke-
  scale artifacts -- 6x6 grid too small for CG, 2 f-values + M=50 too small for SP
  ratio differentiation -- full grids will discriminate).
- **Apples-to-apples Lane 1 declared in metrics**: `lane="Lane 1 substrate-native
  capability"`, `corpus_provenance="synthetic"` recorded in metrics.json.

## Timeout estimate

Per-seed wall (full config):
- ARM_PC: M=200 patterns; M-vs-M cosine matrix probe per pattern -> ~M*M*N_DIM ops.
  200 * 200 * 8192 / 3 GFLOPS = ~110s. With numpy BLAS more like ~30s.
- ARM_CG: 400 pair bindings (FFT) + 400 unbind probes vs 20-obj codebook.
  ~400*2 FFTs (8192) + 400 cosine probes vs 20 = ~10-15s.
- ARM_WM: 7 k-values * 40 trials * up-to-30 items bind + retrieve per trial.
  Mostly k=20,30 dominate. ~30 * 40 * 2 FFTs * 7 levels avg = ~20s.
- ARM_RP: sum M_i = 100+500+1000+2000 = 3600 bind operations + same unbind probes.
  ~3600 * 2 FFTs + 2000 * 2000 cosine = ~30-50s.
- ARM_SB: 4 K values * 20 trials * up-to-50 items * 2 (bind+unbind) FFTs.
  ~50 * 20 * 2 * 4 = ~8000 FFTs at 8192 = ~30s.
- ARM_SP: 5 f-values * 500 M = 2500 bind + 500*500 cosine each = ~30s per f = ~150s.

Per-seed total: ~250-330s. 3 seeds total: ~750-1000s = 13-17 min wall.
Plus selftest (~1s) + overhead. Total ~15-20 min wall estimate.

Formula per queue_add.py rule:
  timeout_s = ceil(1.5 * smoke_wall * (full_N/smoke_N) * (full_seeds/smoke_seeds))
  smoke_wall = 11.5s; scaling factor ~80 (vs smoke); 3 seeds vs 1 seed.
  timeout_s = ceil(1.5 * 11.5 * 80) = 1380s + safety -> 3600s (1h) for ample margin.

**timeout_s = 3600** (1h). Anchor has no `_n<N>` suffix -> PROT-019 not triggered.
Below PROT-021 4h threshold -> _seed_checkpoint required but NOT mandated by gate; we
import it anyway for crash recovery.

## Why this is load-bearing strategically

USER's standing emphasis (master bias checklist 2026-06-24): substrate competes on
its native strengths (composition, retrieval, working memory, capacity), NOT on
transformer-corpus benchmarks. The substrate-product story requires that these
native capabilities form a UNIFIED suite at production scale, not a sequence of
isolated wins. This cell is the FIRST comprehensive substrate-native capability
snapshot at production-scale on apples-to-apples synthetic data.

- If ARM_SUITE_NATIVE_ALIVE: substrate-product story has rigorous unified foundation;
  next step is to compose this suite into substrate-as-LM with confidence.
- If ARM_SUITE_NATIVE_PARTIAL: identifies SPECIFIC gaps (which arm(s) fail at
  production scale) for targeted follow-up; clarifies what's solid vs what needs
  development.
- If ARM_SUITE_NATIVE_DEAD: the per-cell chain-grade wins do not compose; interaction
  effects dominate; substrate program needs to rethink unified-suite framing.

## References

- `notes/feedback_experiment_bias_master_checklist_USER_2026-06-24.md` (master
  bias checklist; Lane 1 substrate-native capability declaration).
- `experiments/exp_substrate_brain_aligned_aliveness_shotgun_v1.py` (closest
  precedent; 4-arm brain-aligned cell at N_DIM=8192).
- `experiments/exp_substrate_arm2_capacity_respecting_pair_storage_v1.py` (ANCHOR 1
  capacity-respecting M=20 DIAGNOSTIC_PASS).
- `experiments/exp_substrate_compositional_K10_K20_reconfirm_n8192_v1.py` (ANCHOR 2
  K10-K20 compositional HARD_PASS).
- `experiments/exp_substrate_compositional_generalization_CORRECTED_v1.py` (CORRECTED
  protocol; not pair-collision-bound).
- Miller 1956 "The magical number seven plus or minus two".
- `reference_operational_findings_2026-06-23_late_session.md` (sparse-bipolar
  20-300x bundle lift; HRR involutive intuition).
- `feedback_smoke_clean_synthetic_data_not_substrate_state_USER_2026-06-23.md`
  (clean synthetic data; no substrate state contamination).
