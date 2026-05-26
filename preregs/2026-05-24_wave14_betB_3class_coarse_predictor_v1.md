# Prereg: wave14_betB_3class_coarse_predictor_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Alt1 walk-back rescue -- 3-class coarse taxonomy for Bet B retention
**Trigger**: wave14_betB_shift_class_full_replication_v1 SHIFT_CLASS_REPLICATION_HARD_FAIL
             (4/6 non-overlapping CIs vs required 5/6 at n>=15). Walk-back asks whether
             a COARSER taxonomy (3 classes matching observed plateau structure) cleanly
             separates at replication scale.
**Compute**: zero new training -- pure re-analysis of existing full-replication data.

## Hypothesis

The 6-class taxonomy was too fine-grained. The per-class means from the full replication
reveal 3 natural plateau clusters:
  HIGH: SAME_CORPUS_PRISTINE (0.941) + COMPOUND_SAME_CORPUS (0.885)
  MID:  REPLAY_SAME_CORPUS (0.845) + NO_REPLAY_SAME_CORPUS (0.682) + STAGE_4_COMPOUND (0.734)
  LOW:  DIFF_CORPUS_2TASK (0.633)

These 3 coarse classes have much larger between-class gaps (~0.25 HIGH-MID gap at means)
than the within-class variance, so CI separation should hold even at current seed counts.

## Design

- Re-analysis of data/exp_wave14_betB_shift_class_full_replication_v1/metrics.json
- Aggregate per-class values into 3 coarse classes per SIX_TO_THREE mapping above
- Compute 95% CI for each coarse class via normal approximation (CI_Z=1.96)
- Count non-overlapping CI pairs (all 3 must be pairwise non-overlapping for HARD-PASS)
- Compute Kruskal-Wallis p-value across 3 coarse groups

## Pre-registered bands

HARD-PASS: all 3 coarse-class CIs non-overlapping (3/3) AND K-W p < 0.01.
  -> 3-class taxonomy is the defensible product claim.
  -> Cap_map Bet B retention predictability at 3-class granularity (v203 annotation bump).
  -> Product claim: "substrate has 3 distinct retention regimes predictable from task-shift class."

HARD-FAIL: any 2 coarse-class CIs overlap (< 3/3 non-overlapping).
  -> Even coarsest taxonomy lacks CI separation at current seed counts.
  -> Walk back to omnibus group-level claim only (K-W p survives, class boundaries do not).
  -> Next rescue: n=30+ per boundary class or alternative continuous predictor.

MIDDLE: 3/3 non-overlapping but K-W p in [0.01, 0.05).
  -> Structural separation confirmed but statistical power weaker than expected.
  -> Consider more seeds for MID class boundaries.

## Self-test verification (5 cells)

1. mean_std_ci([0.5]) -> CI=[0.5, 0.5]
2. mean_std_ci([0.8, 0.9, 1.0]) -> mu=0.9 with CI symmetric around mean
3. SIX_TO_THREE covers all 6 expected class labels
4. All SIX_TO_THREE values in {HIGH, MID, LOW}
5. kruskal_wallis_p on clearly separated groups -> p < 0.01

## Dependency

Requires data/exp_wave14_betB_shift_class_full_replication_v1/metrics.json to exist
and contain "per_class" dict with "values" lists. If missing, returns 3CLASS_DATA_MISSING.
The full-replication ran remotely; if the JSON isn't synced locally, sync before ship.
