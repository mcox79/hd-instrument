# Prereg: wave14_rprime3_r2_subcorpus_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: R-PRIME-3 R2 -- sub-corpus geometry as retention mediator
**Trigger**: v193 R-PRIME-3 between-corpus geometry HARD_FAIL (r^2=0.103). R2 rescue
tests within-corpus chunk-pair geometry, which is geometrically distinct from v193.

## Hypothesis

Between-corpus distance fails to predict retention. Within-corpus (sub-corpus) chunk
pairs may show stronger geometry-retention correlation because they span a finer and
more geometrically diverse set of task pairs. If Pearson r(chunk_pair_distance, retention)
>= 0.50, geometry hypothesis survives at sub-corpus scale.

## Design (exp_dev autonomy)

- Corpus A split into 8 chunks -> 56 directional pairs (i,j), (i != j)
- N = 2048 (FULL), 512 (smoke)
- M per chunk = 80 (FULL), 20 (smoke)
- Geometry metric: cosine distance between chunk centroids (mean key direction)
- Retention: ratio of within-W retention after 2-phase (i then j) training
- Seeds = {7, 17, 23, 31, 41} (FULL)
- Queue: remote_cpu_queue (pure numpy; ~5-10 min CPU)

## Pre-registered falsifier bands

- **HARD-PASS**: mean Pearson r >= 0.50 AND mean p < 0.05 across seeds.
  -> R-PRIME-3 R2 sub-corpus geometry PASSES; geometry hypothesis survives
  at sub-corpus scale; further probing warranted.
- **HARD-FAIL**: mean |r| < 0.15 AND n_non_monotone >= 4 of 6 distance bins.
  -> R2 REJECTED; R-PRIME-3 geometry framing CLOSED at both between-corpus
  and within-corpus scales.
- **MIDDLE**: any intermediate.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

- (r=0.60, pval=0.02, n_non_mono=1) -> R2_SUBCORPUS_HARD_PASS
- (r=0.10, pval=0.80, n_non_mono=5) -> R2_SUBCORPUS_HARD_FAIL
- (r=0.35, pval=0.10, n_non_mono=2) -> R2_SUBCORPUS_MIDDLE_BAND
All 7/7 self-test cases pass.

## Smoke outcome (N=512, m_per=20, 1 seed, 56 pairs)

R2_SUBCORPUS_MIDDLE_BAND: r=0.187, pval=0.161, n_non_monotone=4.
Weak correlation at smoke scale -- FULL at N=2048 + 5 seeds will resolve.
Smoke DOES NOT fail: not HARD_FAIL. Ship FULL.

## Queue entry

`queue=remote_cpu_queue name=wave14_rprime3_r2_subcorpus_v1 script=experiments/exp_wave14_rprime3_r2_subcorpus_v1.py prereg=preregs/2026-05-24_wave14_rprime3_r2_subcorpus_v1.md timeout=1800`
