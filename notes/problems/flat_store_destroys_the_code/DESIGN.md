# DESIGN -- flat_store_destroys_the_code (solver session, 2026-08-22)

Written BEFORE the decisive run, frozen here so the bar cannot move to fit the result.

## The question, stated so it can FAIL
The brief: the live reading loop "adds each word's pattern into one running total per concept"
(`hdlab.reading_grounding_loop.ConceptSpace._sums[lemma] += ctx_vec` -- a flat prototype). The
paint analogy is IDENTITY DESTRUCTION: mix red+blue+yellow, you cannot pull the red back out. The
proposed fix is a store that keeps a label on every item (addressed / episodic -- the "pull it back
out cleanly" store). The bar (PROBLEM.md sec 6): a read-out on the LIVE reading path that uses
addressed storage instead of the flat sum and BEATS THE STRONGEST COUNTING FLOOR, CI-separated, on
HELD-OUT text.

## What the disk already says (verified this session, not assumed)
- The three isolation proofs (1.000 vs 0.003; 1.000 vs 0.273; 1.0 vs 0.06) are SYNTHETIC
  mechanism-proofs; their own notes say "not chain-grade capability, real-text build still required."
- The ONE cell that connected structure to a real read-out is `exp_structured_code_vs_flat_bag_c3_v1`
  -> `STRUCTURE_HURTS` (-0.0113, CI [-0.0195,-0.0030]).
- `exp_substrate_end_to_end_readout_v1`: exact-key 0.9333 vs held-out 0.0044 (the collapse).
- The `6.93 of 7 bits` figure is NOT ON DISK; the real bundling-retention numbers (validated ruler
  `exp_encoding_quality_instrument_v2`): incumbent SimHash retains 0.8744/7 through the sum, sparse
  graded C1_KCAP retains 3.5264/7. So the survivable-superposition lever is CODE FORMAT (a Phase-1
  change), not addressing (Phase-3).
- LONG_TERM_PLAN Phase 3 is "BLOCKED UNTIL PHASE 1 CLEARS"; supply-before-architecture.

## The experiment -- open-vocabulary IDENTITY RECOVERY on the live reading path
Reuse the proven live-path harness (`exp_grounding_readout_known_answer_v1`: corpus, 80/20
profile/held-out split via `_n_profile`, `context_vector_masked` cues, `paired_bootstrap`,
self-retrieval >=0.70 positive control). Candidate/label set = the harness's anchor lemmas. For a
query cue, each arm scores EVERY lemma; hit@1 iff argmax lemma == the true lemma L.

Arms (same candidates, same gold=L, same n):
- **A_FLAT** (incumbent): score(lemma) = cos(query_dense, prototype(lemma)), prototype = raw sum of
  its profile `context_vector_masked` vectors (accumulated RAW -- mean norm ~44.5, per the sec-7
  warning; normalise only at compare time).
- **A_ADDRESSED** (the brief's fix): keep EVERY profile encounter as a labelled episode; score(lemma)
  = max over that lemma's episodes of cos(query_dense, episode). Exemplar / CA3-completion read-out
  -- the fair "keep a label on every item, pull it back out" store, with NO discrete-codebook
  collision (the handicap the plan flagged on the prior completer test).
- **F_COUNT1 / F_COUNT2** (the floor): explicit co-occurrence counting, first- and second-order PPMI
  profiles (the `prof()` math from `measure_counting_floors_through_the_harness`). The STRONGEST
  floor actually run; gate on its per-arm CI UPPER bound.

Two cue regimes, same items:
- **EXACT-KEY**: query = an in-store PROFILE sentence of L (leave-one-out for A_ADDRESSED so the
  self-episode cannot trivially self-match). Expected ~high for all -> the instrument works.
- **HELD-OUT**: query = L's held-out sentence (never stored). THE column the bar is decided on.

Controls (none optional; each reports how many items it removed):
- **SCRAMBLE-CONTENT twin**: query = a DIFFERENT lemma's held-out sentence, gold stays L (destroys
  the cue's CONTENT, not word order). Must collapse to chance.
- **INFO-FREE A_ADDRESSED**: episodes replaced by random +/-1 codes (same count, same grouping).
  Must LOSE at both exact-key and held-out.
- **ABLATION**: A_ADDRESSED -> A_FLAT is the addressed-off delta; report it.
- **Positive control**: 2AFC self-retrieval on held-out cues must clear 0.70 or the comparison is
  VOID_PLUMBING.
- **Tie report**: assert tie density on every argmax and report both tie conventions
  (`tools/rank_with_ties.py`) if ties are material (sparse counting arms can tie at 0.0).

## The gate (frozen)
A_ADDRESSED beats `max(F_COUNT1, F_COUNT2, SCRAMBLE)` UPPER bound, CI-separated, ON HELD-OUT.
- FAIL (a): no margin over the floor's upper bound -> real negative.
- FAIL (c): a margin only at exact-key and not held-out -> the ALREADY-KNOWN result, NOT progress.
- FAIL (d): the isolation win does not reproduce once wired -> the most informative outcome; write up.
- WIN: A_ADDRESSED clears the floor's upper bound on HELD-OUT, CI-separated, with the info-free arm
  losing and the ablation moving the score.

## Predicted (hypothesis, not a result)
Exact-key: all arms high (A_ADDRESSED ~1.0). Held-out: A_ADDRESSED COLLAPSES (best single episode
match to a novel cue is noise-dominated across a large episode pool -- the 0.0044 signature), FLAT
and COUNT degrade gracefully; A_ADDRESSED does NOT beat the counting floor. If so -> REFUTED as
stated: the flat sum's pooling is ABSTRACTION that transfers, not destruction; keeping every item
wins only at exact-key. Let the disk decide.
