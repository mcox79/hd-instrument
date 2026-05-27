# Pre-registration: wave14_betB_2tier_coarse_analysis_v1

**Filed:** 2026-05-26  
**Trigger:** triage instruction — Bet B Alt 1 follow-up at COARSER 2-tier taxonomy comparison  
**Context:** alt_taxonomy_sweep_v1 found MIDDLE (silhouette=0.584 at K=4). Group-level CONFIRMED  
  (v206) but within-cell level Yellow-PARTIAL. 2-tier is the coarsest meaningful test.  
**Queue:** remote_cpu_queue (pure re-analysis, < 5s)

## Taxonomy design

**2-tier:**
- HIGH: SAME_CORPUS_PRISTINE + COMPOUND_SAME_CORPUS + REPLAY_SAME_CORPUS + NO_REPLAY_SAME_CORPUS
       (empirical means: 0.925, 0.885, 0.845, 0.838; all >= 0.83)
- LOW: STAGE_4_COMPOUND + DIFF_CORPUS_2TASK
      (empirical means: 0.734, 0.633; all <= 0.74)

Expected separation: large gap (~0.83 vs ~0.70), should be HARD-PASS.

**3-tier (secondary analysis):**
- HIGH: SAME + COMPOUND (mean ~0.90)
- MID:  REPLAY + NO_REPLAY + STAGE4 (mean ~0.73-0.845)
- LOW:  DIFF (mean ~0.63)

## Pre-registered bands

**HARD-PASS** (2-tier separable):
- 2-tier silhouette >= 0.70 AND all CIs non-overlapping AND KW p < 0.001

**HARD-FAIL** (even 2-tier overlaps):
- HIGH CI high <= LOW CI low (overlap)

**MIDDLE**:
- CI separation exists but silhouette in [0.40, 0.70)

## Strategic implications

HARD-PASS: Bet B retention is BINARY-classifiable at a minimum. Confirms group-level
  finding (v206) at per-cell CI level. Cap_map annotation: 2-tier binary taxonomy
  CONFIRMED at cell level; within-cell Yellow-PARTIAL at K=4 persists but binary
  separation is locked.

HARD-FAIL: Even binary separation fails at cell level. Omnibus KW signal is real
  but no taxonomy survives CI scrutiny at production scale. Bet B retention story
  limited to "significant group effect" without predictive taxonomy.

Per [[feedback-envelope-expansion-fail-bands]]: bands pre-registered.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only.
