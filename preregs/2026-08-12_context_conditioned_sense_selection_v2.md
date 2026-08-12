# PRE-REGISTRATION -- exp_context_conditioned_sense_selection_v2

Filed 2026-08-12 BEFORE any accuracy number exists on the v5 material. Basis:
`notes/context_conditioned_sense_selection_2026-08-12.md` (v1 note),
`preregs/2026-08-12_context_conditioned_sense_selection_v1.md` (v1 prereg, superseded by this
file for the v5 re-run only -- v1's own metrics.json is untouched and still the record of the
v3-material run),
`notes/definitional_term_boundary_v5_2026-08-12.md` (v5 fact set, commits e01db310b..458bfac75).

## WHY A RE-RUN, NOT A PATCH
v1's main arm (sense = bare stored object word) was a decisive floor-level HARD_FAIL. v1's one
suggestive signal (sense = its own other source sentences, 0.6914) could not be separated from
topic/segment matching at adequate power: the same-segment control had n=45, CI lower bound
0.4330, on the floor. The blocking constraint was DATA SCARCITY: 621/723 v3 multi-sense facts
(85.9%) had exactly one source sentence, so the topic-controlled slice was starved.
The v5 term-boundary fix (independently reproduced below) raises multi-sentence-sense yield.
This re-run exists to answer the ONE question v1 could not: does the sense-from-own-sentences
effect survive topic control at adequate power. Nothing else about the design changes.

## V5 YIELD -- INDEPENDENTLY VERIFIED OFF DISK (not inherited from the v5 note)
Recomputed directly from
`data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl` (2092 rows),
by grouping on each of the two candidate subject keys and counting `source_sentences` per
stored row (no merge across rows):

| index | n_multi_sense_words | senses_with_gt1_source_sentence | words_all_senses_gt1 |
|---|---|---|---|
| `subject` (full term) | 288 | 96 | 3 |
| `subject_head_lemma` | 379 | 167 | 6 |

`subject` matches the v5 note's own reported triple (288/96/3) exactly. `subject_head_lemma`
recomputes to 379/167/6, not the note's quoted 379/145/4; the note itself flags this exact kind
of discrepancy for v4 (333/88/2 recomputed vs 333/135/7 quoted) and attributes it to whether
sentence counts are pooled across distinct literal-subject rows that share a head lemma
(measured here: 62 such (head_lemma, object) pairs are fed by >1 distinct literal subject).
This cell counts PER STORED ROW, un-pooled, which is the more conservative (lower) convention
for "how many senses have real multi-sentence support" and is the number the C3 arm's power
actually depends on. Both directions agree: yield is UP on both indexes vs v3/v4, materially
easing (not fully removing) the v1 data-scarcity blocker. Full recompute in this prereg's
companion cell self-test.

## EVAL SET -- BOTH INDEXES, DECLARED PRIMARY BEFORE RUNNING
v1 used `subject_head_lemma`... no: v1 used the full-term `subject` field
(`exp_context_conditioned_sense_selection_v1.py:78`, `by_subj[r["subject"]]`). The v5 note flags
that `subject_head_lemma` reproduces the OVER-GENERALITY the term-key fix (F8) corrects, and is
defensible only as an EVAL index, never as a stored fact. Per that, and per v1's own precedent:

**PRIMARY = `subject` (full term) index.** `subject_head_lemma` is run and reported in full as a
SECONDARY / power-comparison arm, explicitly labelled non-primary in every output table. This is
declared now, before either number exists, so a later preference for whichever index scores
better cannot masquerade as the pre-registered choice.

## FLOOR -- RECOMPUTED FOR V5 (k changes from v3's k)
Independently recomputed off the v5 fact set (both indexes; the run asserts these against the
census it computes at runtime -- a mismatch blocks the run):

| index | mean k | k-dist | analytic floor (subject-weighted, mean 1/k) | micro floor (n_multi / n_facts_multisense) |
|---|---|---|---|---|
| `subject` | 2.2431 | {2:230,3:49,4:7,5:1,6:1} | **0.4634** | 0.4458 |
| `subject_head_lemma` | 2.4538 | {2:264,3:83,4:22,5:4,6:3,8:2,11:1} | **0.4401** | 0.3919 |

Both floors are additionally checked by an empirical random-pick simulation (1000 seeds); a
mismatch >0.02 from the analytic value is a harness bug and blocks the run. NEITHER floor is
0.4316 -- that number belonged to v3's k distribution and does not apply here. Every accuracy
number in this cell is reported against ITS OWN index's floor, never the other's and never v1's.

## SELECTORS, LEAKAGE MECHANISMS, CONTROLS -- UNCHANGED FROM V1, RE-ASSERTED NOT WEAKENED
Reused verbatim from `exp_context_conditioned_sense_selection_v1.py`:
- S1 DIST (`hdlab/random_indexing.RandomIndexingEncoder`, same hyperparameters: N=8192,
  sparsity=10, window=5, min_count=3, seed=0), S2 PERC (raw Lancaster+Brysbaert), S3 COMBO.
- **L1** -- fit corpus is the v5 CANONICAL corpus (`exp_definitional_grounding_v5.load_corpus_v5`
  with `lineaware=True`, i.e. the same F9 line-aware bio loader the facts themselves were
  extracted from -- using the v3/v4 joined-line loader here would be a corpus/fact mismatch, not
  a leakage issue but a validity one), with every eval sentence for BOTH indexes' trial sets
  removed before fitting. ASSERT: empty intersection; removed count reported.
- **L2** -- identical masking (`build_mask_terms` / `masked_context_tokens`), rebuilt per index
  (candidate lists differ between the two indexes). ASSERT: no candidate token survives masking,
  checked per trial, per index.
- **L3** -- identical: scorer signature is `(tokens, candidates)` only.
- **C1** cross-item context swap (5 seeds) -- unchanged, must drop >=0.05 to avoid the fail band.
- **C2** context lesion (empty context, same code path) -- unchanged, must stay >=0.03 below
  primary to avoid the fail band.
- **C3** strict leave-one-sentence-out, PLUS its own decisive controls (query-swap,
  count-matched, same-segment-only, same-segment query-swap) -- unchanged mechanics, run on
  BOTH indexes this time (v1 ran it on `subject` only).
- **Removed control re-verified, not assumed.** v1's self-test #5 proved word-order scramble is
  score-invariant for a bag-of-words selector (max float delta <1e-9 from summation-order only,
  incapable of changing an argmax). That proof is a property of the SELECTOR code
  (`DistSelector.scores` / `PercSelector.scores`), which is imported unchanged from v1's module,
  not reimplemented -- so the proof still applies verbatim. This cell RE-RUNS that exact
  self-test (not a citation of v1's result) so it is asserted fresh against this run's code, not
  merely inherited.

## MAIN QUESTION FOR THIS RE-RUN (the reason it exists)
Does C3's same-segment-only accuracy clear its OWN index's floor with the 95% CI lower bound
above that floor? Report acc, n, and CI for both indexes. If the CI lower bound still sits at or
below the floor, the answer is: the sense-from-own-sentences effect CANNOT be separated from
topic/segment matching at this scale, even with the eased data constraint -- and that is to be
reported as a real, informative negative, not softened or buried under a different slice that
happens to clear.

## PRE-REGISTERED BANDS -- for the PRIMARY (`subject`) index's main arm, floor F=0.4634
- **HARD_FAIL** if ANY of: (i) both S1 and S2 <= F+0.03=0.4934; OR (ii) best selector's C1 drop
  < 0.05; OR (iii) C2 lesion >= primary - 0.03.
- **MIDDLE_BAND**: 0.4934 < acc <= 0.60 with C1 drop >= 0.05.
- **PASS**: acc > 0.60 AND C1 drop >= 0.08 AND C2 <= 0.4934.
- **HARD_PASS**: acc >= 0.70 AND all controls clean AND C3-same-segment (not just raw C3)
  >= 0.60 with CI lower bound above F. (HARD_PASS is deliberately gated on the SAME-SEGMENT
  number this time, not raw C3 -- raw C3 already passed that bar in v1 and is not the open
  question; topic-controlled C3 is.)
Same band structure applies to the `subject_head_lemma` secondary arm against ITS floor
(0.4401), reported but not determinative of the cell's headline verdict.

## WHAT RESULT MEANS IT DOES NOT WORK -- stated plainly, before running
If the main arm (sense = bare object word) again sits at or within 0.03 of its index's floor,
that reproduces v1: the collapse/retrieval mechanism is not what is missing, storage of the bare
object word is. If C3-same-segment's CI lower bound is still at or below the floor despite the
eased data constraint, the honest conclusion is that THIS corpus, at this size, cannot separate
context-conditioned sense selection from topic matching -- not that no such effect exists, and
not that it does. Both are real, reportable findings. Do not hunt for a slice that clears if the
pre-registered main slices do not.

## HONEST SCOPE CAPS (carried from v1, unchanged)
Fit corpus ~623K tokens (v5 corpus is the same segments, size not expected to move materially --
measured at runtime and reported). Small for distributional semantics. The "true sense" label is
the v5 extractor's own output; the v5 note's own out-of-scope fault classes (inverted hypernymy,
adjectival/list heads, role-not-meaning) still cap achievable accuracy by an unknown amount, and
that cap did not close between v3/v4 and v5 (the v5 note reports it unchanged at 1.2%/0%/present
respectively) -- multi-sense-word overlap with those fault classes is not separately audited here.

## RUNTIME
Local, single process, CPU. Two index arms roughly double v1's ~15 min runtime; expect < 35 min.
Not a queue cell.
