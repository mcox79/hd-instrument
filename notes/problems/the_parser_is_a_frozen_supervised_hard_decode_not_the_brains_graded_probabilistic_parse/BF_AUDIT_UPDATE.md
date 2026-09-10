# AUDIT UPDATE -- parser cluster (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)

Solver session 2026-09-10. Strategy re-verifies + folds into the living audit at integration.

## The reconciled parser-cluster verdict (with a NUMBER for the hard-decode vs scorer split)
The parser front-end's non-brain-faithfulness is TWO separable defects, and this solution measured their
relative size on UD-EWT test (n=24,120 tokens):

1. **HARD-DECODE (the BLOCKING defect, now FIXABLE via a landed organ).** Greedy argmax + heuristic
   cycle-break discards the globally-normalized posterior. The exact graded decode (`hdlab.graded_parser`,
   brute-force-verified) fixes it -- but it changes only **1.9%** of head errors (95/5048); the exact MAP +
   Matrix-Tree marginals are the BF replacement for the decode. **Recommend: the DECODE half of
   `arc_parser`/`arceager_parser` becomes BF once `decode="exact"` is on the read path; `graded_parser`
   moves DORMANT -> LIVE.**
2. **FROZEN SUPERVISED SCORER (the deep, residual NOT_BF, ~99% of the head error).** The arc-factored
   surface-feature averaged-perceptron trained on the gold treebank. The exact normalization cannot touch
   its errors. This is the genuine remaining NOT_BF and the acquisition follow-on.

## Specific entries to update
- **`parse_confidence` (currently NOT_BF, fitted logistic, decision-dead).** Confirmed replaceable by the
  raw graded marginal: reliability AUC **0.8546** (marginal of the picked head) vs the logistic's 0.736 ->
  a fitted NOT_BF component the reader can DROP. The registry note's "UPGRADE (gated on a live defer
  consumer)" is unblocked by consuming the marginal directly.
- **`graded_parser` (BF, DORMANT PASS).** Verified live-usable: exact CLE MAP + single-root marginals
  brute-force-exact (`self_test`), marginal is a strong reliability signal (AUC 0.855) AND a strong
  downstream reach (patient recall 0.951->0.991 via top-2). Recommend LIVE.
- **`arc_parser` / `arceager_parser` (NOT_BF).** The NOT_BF note "greedy hard-decode discards Matrix-Tree
  marginals" is HALF-addressable now (decode -> exact); the residual NOT_BF is precisely the SUPERVISED
  SCORER acquisition, which the audit should now name as the deep gap (not the decode).

## NEW deviation logged
- **The graded posterior's downstream value is as a DISTRIBUTION TO READ, not a better point decode.** A
  measured deviation from the naive expectation: a better single decode is board-invisible (too few heads
  change); the top-2 marginal reach is the CI-sep lever. Downstream consumers should read the top-2
  reliability-ranked, not just the argmax head.

## Acquisition-admissibility ruling (proposed for the audit's PINNED/INVENTED column)
A frozen glass-box arc SCORER is an ADMISSIBLE offline FOUNDATION (supplies adult syntactic competence,
frozen, no external tool/LLM at inference) -- **the blocking NOT_BF is the hard-decode, not the offline
fit.** The reading-learned scorer (Prong 2: viable, grows with reading, first-step gap 0.57) is the deeper
BF upgrade, filed as a follow-on -- not a reason to call the treebank scorer inadmissible today.
