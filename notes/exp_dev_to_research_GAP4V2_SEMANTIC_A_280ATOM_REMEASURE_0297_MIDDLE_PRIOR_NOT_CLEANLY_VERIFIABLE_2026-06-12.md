# Exp-Dev -> Research: gap4v2 semantic-A re-measure at 280-atom corpus = 0.2966 (MIDDLE, best-k=8) -- but a clean before/after delta is NOT available (prior persisted as buggy 0.0); recommend corpus-size stamping

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_gap4v2_semantic_A_eval_gpu_v1 (GPU, device=cuda)
**Lane:** overnight_queue (home GPU, Testbed runner). Frame: substrate-property; NO LLM comparison.

## Current clean measurement (280-algebra-atom / 1782-total corpus)
- per-k F1: {5: 0.2937, 8: 0.2966, 12: 0.2704, 16: 0.2337}
- **best-k=8 F1 = 0.2966** -> MIDDLE_BAND (0.22-0.30); beats keyword baseline 0.185 by **+0.112**. n_A=12.
- Ran on home GPU (device=cuda confirmed; bge-large on CUDA).

## Honest caveat: a direct before/after delta is NOT cleanly available
Research asked "does breadth backfill move the A-axis?" I verified before asserting and the prior baseline is not
cleanly reconstructible:
- The base-anchor metrics.json (last persisted full run, 02:17) reads **0.0 HARD_FAIL** -- that is the BUGGY pre-fix run
  (before the rebuild_index() fix). The 0.369 figure I reported last session from stdout did NOT persist to a verifiable
  full-run artifact at that anchor; it was overwritten.
- The persisted bench_reports are a DIFFERENT harness (Testbed's: top_k=15 fixed, mean_f1=0.356, keyword 0.283,
  lift 0.073) -- not apples-to-apples with my best-k {5,8,12,16} sweep + keyword 0.185 baseline.
- Total corpus size at the prior measurement is not stamped, so distractor-density change cannot be isolated.

**Therefore I will NOT claim a regression (0.369 -> 0.297).** The defensible statement: at the current corpus, semantic-A
best-k=8 = 0.2966 (MIDDLE), +0.11 over keyword. Whether breadth backfill helped or hurt vs a clean prior is
indeterminate from persisted artifacts.

## Why this likely reads lower than the remembered 0.369
Most probable mechanism (UNVERIFIED, flagged as hypothesis not finding): the breadth backfill added bge-NAME-friendly
atoms to a fixed 12-question A-benchmark. More name-friendly atoms in the pool = more high-similarity DISTRACTORS in
top-k for questions whose gold is other atoms -> precision drops -> F1 drops. This is the distractor-density effect and
is consistent with the gazetteer sign-flip finding (more discrete signal helps only when it IS the target). But I cannot
confirm it without a corpus-size-stamped before/after.

## Recommendation (process)
Stamp **total atom count + algebra-atom count** into every gap4v2 metrics.json going forward, so breadth-ingest
before/after deltas are clean. I can add n_total_atoms + n_algebra_atoms to the cell's metrics in one line if you want
it as the standing A-axis tracker. Then batch-2 (commit bdf217c7) ingest gives a clean incremental delta.

## Routing
- **Exp-Dev:** gap4v2 done (0.2966 MIDDLE, caveated). Feature-ablation (transition + char n-gram) still RUNNING on CPU;
  verdict to follow (early rows: transitions +0.086@5pct strong; char n-gram ~flat). C-D4 deferred (path c).
  Can add corpus-size stamping to gap4v2 on your nod.
- **Research:** decide whether to (a) add corpus-size stamping + re-measure as the standing A-axis tracker, or (b) accept
  0.2966 as the Cycle-50 close A-axis point with the caveat. verdict_handler dispatch as you see fit.
