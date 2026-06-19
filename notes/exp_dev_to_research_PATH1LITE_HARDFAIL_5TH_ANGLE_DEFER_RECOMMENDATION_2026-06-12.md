# Exp-Dev -> Research: Path-1-lite HARD_FAIL 0.34 = 5th triangulation angle -> RECOMMEND defer full Path-1 SRL to Phase-6

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** your pending Path-1 SRL decision

To inform your Path-1 decision (build full SRL w/ CoNLL-2005, or defer), I built a Path-1-LITE probe: heuristic entity-quantity
binding (the SRL linguistic angle, no CoNLL-2005 needed). Result:

- ASDiv-1op acc = **0.3402** (HARD_FAIL, lift -0.05 vs 0.39)
- **Distractor-subset (>2 numbers, where entity-binding should matter MOST): 0.1354** -- WORST performance exactly where the
  linguistic angle is supposed to help.

## 5th independent triangulation angle

| # | mechanism class | ASDiv-1op |
|---|---|---|
| 1 | discriminative perceptron | 0.39 |
| 2 | world-model schema-simulation (E4) | 0.34 |
| 3 | BMA ensemble | gain=0 |
| 4 | hippocampal schema-retrieval (Path 5) | 0.36 |
| 5 | **heuristic entity-binding (Path-1-lite)** | **0.34** |

FIVE distinct mechanism classes (statistical / simulation / ensemble / structural-memory / LINGUISTIC) all plateau 0.34-0.39.

## Recommendation: DEFER full Path-1 SRL to Phase-6

The linguistic angle (Path 1's premise) FAILS heuristically, and worst on distractors (0.135) -- the "which number goes with which
agent" problem the drill said SRL addresses is exactly where the heuristic collapses. A TRAINED SRL (CoNLL-2005) would label roles
better, BUT the bottleneck the distractor failure reveals is SEMANTIC (which quantity does the question target) -- corpus/comprehension-
bound, not role-labeling-bound. So full Path-1 SRL (3-5d + CoNLL-2005 bundling) would likely face the same comprehension ceiling.

RECOMMEND: defer full Path-1 SRL to post-Phase-6. The 5-deep triangulation strongly supports corpus-deficiency as the operand-selection
root cause; math+science ingestion (USER strategic priority) is the empirically-supported lever. Re-run ALL operand-selection paths
(discriminative + world-model + schema-retrieval + entity-binding + SRL) post-ingest against the clean pre-ingest baselines I've now established.

CAVEAT (honest): the heuristic's failure doesn't DEFINITIVELY prove trained-SRL fails -- if you want the definitive test, bundle
CoNLL-2005 and I'll build full Path 1. But the 5-deep triangulation makes defer-to-Phase-6 the higher-EV call. Your decision. Path-1-lite queued.
