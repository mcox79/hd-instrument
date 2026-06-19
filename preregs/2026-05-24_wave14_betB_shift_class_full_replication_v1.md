# Pre-registration: wave14_betB_shift_class_full_replication_v1

**Filed:** 2026-05-24 by exp_dev sub-agent
**Queue:** remote_cpu_queue
**ETA:** ~45-90 min (15 seeds x 2 classes x FULL-scale Bet B training on remote CPU)
**Trigger:** Cap_map v201 pre-registered gate — row-state promotion for Bet B retention
predictability requires n>=15 for ALL 6 shift classes; v1 smoke had n=5 for
SAME_CORPUS_PRISTINE (class 0) and NO_REPLAY_SAME_CORPUS (class 3).

## Hypothesis

The v201 SHIFT_CLASS_HARD_PASS result (6/6 non-overlapping CIs, K-W p=2.9e-14) was a
re-analysis of EXISTING experiment artifacts. Two classes had n=5 (small sample). This
experiment runs 15 fresh seeds for those two classes and re-evaluates the predictor at
n>=15 across ALL 6 classes.

If the 6/6 CI separation holds at n=15 per small-n class AND K-W p<0.01, the row-state
promotion gate is cleared: Bet B retention predictability claim gets OPERATIONAL status.

## Class definitions (same as v1)

| Class | Name | What is tested |
|---|---|---|
| 0 | SAME_CORPUS_PRISTINE | 2-task same corpus, 50% replay, EMA=0.7 (base Kovacs setup) |
| 1 | COMPOUND_SAME_CORPUS | per-task sub-substrate + replay (existing data, n=15 already OK) |
| 2 | REPLAY_SAME_CORPUS | replay-enabled ablation frac>=0.05 (existing data, n=49 already OK) |
| 3 | NO_REPLAY_SAME_CORPUS | ablation boundary frac=0.0 (needs 10 more seeds) |
| 4 | STAGE_4_COMPOUND | 4-stage A->B->C->D (existing data, n=20 already OK) |
| 5 | DIFF_CORPUS_2TASK | English x code corpus (existing data, n=13 already OK) |

## New runs required

- **Class 0 (SAME_CORPUS_PRISTINE)**: 15 fresh seeds using base Kovacs setup
  (N=4096, K=4, BETA=8.0, EMA=0.7, REPLAY_FRAC=0.50, PHASE_A_EPOCHS=8, EPOCHS=5,
  BYTES_PER_CORPUS=200000, BATCH_SIZE=64).
  Seeds chosen: [53, 61, 67, 71, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131].
  (Distinct from existing seeds 7,17,23,31,41 used in v9/v11/v12 cap_map history.)

- **Class 3 (NO_REPLAY_SAME_CORPUS)**: 15 fresh seeds with ablation_B frac=0.0 setup
  (N=4096, K=4, BETA=8.0, EMA_ALPHA=0.7, REPLAY_FRAC=0.0, PHASE_A_EPOCHS=8, EPOCHS=5,
  BYTES_PER_CORPUS=200000, BATCH_SIZE=64).
  Seeds chosen: [53, 61, 67, 71, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131].
  (Distinct from existing seeds 7,17,23,31,41 in ablation_B data.)

After running, the script re-evaluates the shift-class predictor using:
  - Class 0: the 15 fresh seeds (discarding hardcoded cap_map values since we now have
    real runs; or merging -- the script chooses fresh-only for class 0/3 to test clean)
  - Classes 1,2,4,5: existing data loaded from tmp_betb_analysis/ (unchanged)

## Pre-registered thresholds (from v201 cap_map + user contract)

**HARD-PASS** (row-state promotion gate cleared):
  - All 6 class CIs are STILL non-overlapping at n>=15 for the two small-n classes
  - K-W p < 0.01 across all 6 classes
  Interpretation: the SHIFT_CLASS_HARD_PASS is confirmed at higher replication;
  row-state move R-PRIME-3 HARD-FAIL row -> Alt 1 PASS row is cleared.

**HARD-FAIL** (replication caveat becomes a genuine failure):
  - Any PREVIOUSLY non-overlapping CI (class 0 or 3) now OVERLAPS with an adjacent class
    at the larger sample size
  - OR K-W p >= 0.05
  Interpretation: the v1 result was a sampling artifact from small n=5 classes;
  predictability claim does NOT hold at replication scale.

**MIDDLE-BAND**:
  - CIs nominally non-overlapping but margins narrowed significantly (CI half-width >50%
    reduction compared to v1 and classes are borderline non-overlapping)
  - K-W p in [0.01, 0.05)
  Interpretation: signal is real but predictability boundary is softer than v1 suggested.

## Self-test cells (8 cells)

1. Class 0 fresh run: single seed produces retention_A > 0.80 (sanity: SAME_CORPUS_PRISTINE
   should be near 0.94 per v1 result)
2. Class 3 fresh run: single seed produces retention_A in [0.60, 0.75] (NO_REPLAY plateau)
3. CI computation: mean_std_ci([0.94]*15) has half-width < 0.01 (tight CI at n=15)
4. CI non-overlap: CIs [0.93,0.95] and [0.67,0.69] are non-overlapping (True)
5. CI overlap: CIs [0.93,0.97] and [0.91,0.95] are overlapping (True)
6. KW p-value: groups [[0.94]*15, [0.68]*15] produces p << 0.001 (True)
7. HARD-PASS verdict fires when n_nonoverlap==6 AND kw_p<0.01
8. HARD-FAIL verdict fires when any previously-non-overlapping CI now overlaps

## Data architecture

Fresh runs saved to:
  data/exp_wave14_betB_shift_class_full_replication_v1/class0_seeds.json
  data/exp_wave14_betB_shift_class_full_replication_v1/class3_seeds.json
Final predictor analysis saved to:
  data/exp_wave14_betB_shift_class_full_replication_v1/metrics.json

## Key constants

- N_FULL = 4096
- BATCH_SIZE = 64
- PHASE_A_EPOCHS = 8
- EPOCHS = 5
- BYTES_PER_CORPUS = 200000
- EMA_ALPHA = 0.7
- REPLAY_FRAC_CLASS0 = 0.50
- REPLAY_FRAC_CLASS3 = 0.0
- CI_Z = 1.96
- SEEDS_PER_CLASS = 15
- PASS_KW_P = 0.01
- FAIL_KW_P = 0.05
