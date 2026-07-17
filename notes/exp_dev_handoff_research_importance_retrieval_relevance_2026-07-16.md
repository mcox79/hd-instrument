# exp_dev hand-off — research: importance/downstream-reach correct-function cell (retrieval-relevance, not acquisition-order)

**Filed-by:** research (Sonnet lit-scan x3 + synthesis), 2026-07-16.
**Trigger:** `notes/research_importance_correct_function_retrieval_vs_active_learning_2026-07-16.md` — full findings,
falsifiable predictions, and cited mechanism recipe live there. This file is the pointer-only hand-off; do not
re-derive the reasoning here, read the cited note.
**Pause state:** `data/orchestrator_paused.flag` — check at pickup time before shipping anything to remote/GPU
queues. This cell is expected to be CHEAP (near-zero new compute, mostly re-analysis) and may be runnable inline/
local per the local-compute re-authorization, but re-verify pause state regardless.

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below beyond the
already-pre-registered HARD-PASS/HARD-FAIL bars in the cited research note's section (c) — cell-author owns
translating those into concrete pre-reg + code.

---

## Anchor candidates (rank-ordered)

1. **[Primary] Retrieval-relevance re-target of the already-run HARD_FAIL cell — reuses 100% existing machinery,
   new ground truth only.**
   - Anchor pointer: research note section (c) "Recommended cell."
   - Substrate-product reading: the HARD_FAIL cell (`exp_importance_downstream_reach_ingest_prioritization_real_
     codex_v1`) tested whether downstream-reach should order ACQUISITION of new facts — it lost to random and
     frequency order. This anchor tests a mechanistically different question on the SAME already-fitted graph and
     SAME already-computed importance scores: does downstream-reach predict which entities are actually needed at
     RETRIEVAL time (test-query relevance), degree-orthogonalized. If it HARD-PASSes, downstream-reach becomes a
     usable retrieval/beam-allocation ranking signal — a genuinely different, additive product claim from anything
     currently built.
   - Concrete spec (per research note section (c)): reuse `experiments/exp_importance_downstream_reach_ingest_
     prioritization_real_codex_v1.py`'s `load_dataset`/`read_triples` (same CoDEx split, `n_ent=2034`,
     `n_test=3656`), `importance_btwn_orth` (the already-validated degree-orthogonalized primary metric,
     `SEPARABLE` tier per `part1_separability`), and `separability_analysis`'s exact OLS-residual/unique-variance
     method (already built, already validated on this dataset for a different target). New ground truth:
     `test_query_count` per entity = count of appearances as head or tail across the held-out test triples — zero
     new labeling, a groupby-count on data already on disk.
   - **HARD-PASS:** unique/incremental variance of `importance_btwn_orth` on `test_query_count`, controlling for
     `[degree, rel_freq]`, is >= 0.15 (partial R², same method as `part1_separability`'s `unique_variance`) AND
     top-tertile-by-importance entities show >= 15 percentage points higher test-appearance rate than bottom-tertile
     at MATCHED degree bins (reuse `degree_matched_order`, already built).
   - **HARD-FAIL:** degree/rel_freq-residualized correlation < 0.05, OR degree-matched arms show no separation —
     meaning retrieval relevance is popularity in disguise here too; correct move is raw degree/frequency as the
     retrieval-priority signal, no separate machinery needed for this purpose. This is a legitimate, valuable
     negative — see research note's pre-registered HARD-FAIL localization guidance (do NOT conclude importance is
     dead outright; the separability finding still stands, only "importance predicts retrieval-priority beyond
     popularity" would be closed).
   - **MIDDLE (plausible modal outcome):** partial correlation 0.05-0.15 — route to Anchor 2 below.
   - Tier hint: near-zero-cost re-analysis of already-fitted artifacts (no new training, no new data acquisition);
     the risk is entirely in whether the correlation clears the threshold, not in implementation difficulty.
   - Why now: cheapest possible test of the one hypothesis this drill confirms is genuinely untested and better-
     precedented (classical IR: PageRank/HITS/personalized-PageRank as retrieval-relevance signals) than the
     already-failed acquisition-order hypothesis.

2. **[Secondary, only if Anchor 1 lands MIDDLE] Bounded-width retrieval-ranking accuracy test.**
   - Anchor pointer: research note section (c), MIDDLE-band routing.
   - Substrate-product reading: the heavier but more directly product-relevant test — does surfacing high-
     downstream-reach facts FIRST within a bounded multi-hop retrieval width (reusing `sr_foundation`'s
     resolvent-AUROC machinery under a fixed retrieval budget, analogous to the HARD_FAIL cell's `budget_grid` but
     applied to per-query retrieval width rather than global ingestion order) improve downstream answer accuracy
     vs. popularity-first or random-first ranking.
   - Tier hint: more expensive (requires a new budget-grid sweep over retrieval width, not just a correlation);
     defer until Anchor 1's result is in — do not build this speculatively.
   - Why now: not yet — sequenced explicitly behind Anchor 1's outcome.

3. **[Deprioritized fallback, only if Anchor 1 ALSO HARD-FAILs] Diversity-corrected re-attempt at acquisition-order
   (hypothesis (b), fixed for the documented redundancy anti-pattern).**
   - Anchor pointer: research note section (b) — BatchBALD/coreset/submodular-coverage literature; section on
     substrate-product implications point 3.
   - Substrate-product reading: the original HARD_FAIL cell used naive top-k-by-centrality acquisition order, a
     documented active-learning anti-pattern (clusters selection on a redundant subset — well-precedented per
     BatchBALD/coreset literature). A facility-location or degree-decorrelated marginal-coverage score, instead of
     raw top-k centrality, is the literature's own named fix.
   - Tier hint: novel-synthesis, capped low; NOT the next dispatch — only relevant if BOTH retrieval-relevance
     (Anchor 1) and the ranking test (Anchor 2) also fail, at which point this is the honest next thing to try
     before concluding value-of-information has no role on this substrate at all.
   - Why now: not now — explicitly deprioritized behind Anchors 1 and 2 per the research note's verdict.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_importance_correct_function_retrieval_vs_active_learning_2026-07-16.md` — this drill's full
  findings, decisive test, falsifiable predictions, citations, calibration reasoning.
- `data/exp_importance_downstream_reach_ingest_prioritization_real_codex_v1/metrics.json` — the already-run
  HARD_FAIL cell's full metrics; `part1_separability` for the already-validated separability/orthogonalization
  method to reuse; `part2_foundation_growth`/`part3_popularity_neutrality` for the acquisition-order result being
  re-targeted, not redone.
- `experiments/exp_importance_downstream_reach_ingest_prioritization_real_codex_v1.py` — reuse `load_dataset`,
  `read_triples`, `separability_analysis`, `degree_matched_order`, `sr_foundation`/`_sr_M` (for Anchor 2), `auroc`.
  Do not rebuild any of these from scratch.
- `notes/research_surprise_decomposition_unexpectedness_vs_importance_2026-07-16.md` — the note that first
  proposed downstream-reach as a candidate 4th ingest signal (P=0.40, flagged untested); this hand-off's Anchor 1
  is the direct empirical follow-through on that note's "cheap decisive test" recommendation, narrowed to the
  retrieval-relevance framing this drill's synthesis confirmed as correct.
- `notes/research_consolidation_function_inventory_schema_reorg_2026-07-16.md` — the keep-gate/prune framing this
  drill's (c) section builds on (write-time gating not-needed for an unbounded store; retrieval-time competition
  IS still finite and is the correct analog to import).

---

## Contract section

- Cell-author owns: exact partial-R² computation details (matching `separability_analysis`'s existing method),
  exact degree-bin construction for the matched-tertile comparison (reuse `degree_matched_order`), and whether to
  compute `test_query_count` from `test.txt` alone or `test.txt + valid.txt` combined (either is defensible; note
  the choice in the pre-reg).
- Must reuse the primary `importance_btwn_orth` metric (not `importance_reach`, which correlates more with degree
  per `part1_separability`'s `importance_reach__degree=0.596` — using the noisier variant would bias toward a false
  HARD-FAIL).
- HARD-PASS/HARD-FAIL bars are pre-registered in the research note section (c) — do not loosen them at pre-reg
  time without flagging the deviation explicitly in the pre-reg file.
- Must NOT re-run `part2_foundation_growth`'s acquisition-order simulation — that question is already answered
  (HARD_FAIL) and is not being re-litigated by this hand-off.

## Autonomy declaration

Research does not prescribe exact partial-R² implementation, exact degree-bin count, or exact test-set-vs-valid-set
scope beyond what is specified above. Cell-author has full autonomy over these implementation details, subject to
reusing the named existing functions and the falsifiable predictions/HARD-PASS/HARD-FAIL bars pre-registered in the
cited research note.
