---
owner_verdict: DONE
---

SUBMISSION — optimize_and_validate_the_learner_before_it_grows_the_foundation
Status: PARTIAL / WIP — do not integrate until you set owner_verdict: DONE. Full detail: notes/problems/optimize_and_validate_the_learner_before_it_grows_the_foundation/SOLVED.md.

The ask: build the most brain-faithful learn-from-reading meaning learner; prove it beats the current PPMI-SVD recipe, net-improves the reader's meaning, and is SAFE to grow the foundation with — before it's ever turned on.

Verdict (decisive, mixed — a full pass under the bar):

The brief's own idea (update the brain's way — online/from error) is a proven dead end: online == batch learning. The real brain lever is what the learner learns over — grammatical relations, not nearby words. A dependency-typed learner beats the window baseline on the two hardest similarity tests, statistically separated (SimLex 0.270 vs 0.210; SimVerb 0.119 vs 0.084), every scrambled control loses, and it matches the old recipe with ~2.5× less text.
Net-improvement: improves the reading-learned meaning; does no harm alongside the supervised WordNet channel when fused the brain's way (reliability-weighted).
Safety: growing by reading genuinely helps comprehension, but a naive overwrite breaks ~1-in-4 things it already knew — and that's a missing-mechanism artifact, not a ceiling: a brain-faithful keep-both-stores (CLS) update cuts it ~3.3× while keeping most of the gain. Safe to grow behind that gate; default-off.
Beyond the bars: every load-bearing mechanism was verified against the neuroscience (4/5 pinned or stronger); every wall was researched; several hopeful ideas were tested and honestly refuted (code-decorrelation, distributional is-a, curriculum, affect-grounding — all null/redundant). The result is a layered roadmap: this learner (done) → sparse-code store (substrate) → relational reasoning (next phase).

⚠️ TWO OPTIMIZATION TESTS STILL RUNNING — results pending, will be folded in: (1) does injected WordNet structure generalize or just memorize; (2) is the remaining similarity gap a fixable recipe or data-limited. Both hit cell bugs on first run, are now fixed and being re-dispatched. The core verdict above does not depend on either.
