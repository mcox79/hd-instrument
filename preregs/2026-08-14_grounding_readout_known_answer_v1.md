# PRE-REG -- exp_grounding_readout_known_answer_v1

**Filed 2026-08-14, BEFORE any arm of this cell was run.** Bands, arms, floors and gates below are
frozen. STEP 1 of `notes/SUBSTRATE_STRATEGY.md` (scoreboard number C3).

## 1. The question, and why this cell exists rather than a fourth hand-score

C3 (reading-grounding MEANINGFUL rate) is quoted at **1-3% with NO RECORDED FLOOR**. Two prior
attempts gated on a HAND-SCORED MEANINGFUL DELTA and were arithmetically undecidable at that base
rate: `exp_grounding_quality_readout_v1` produced 3 MEANINGFUL rows in a 100-row blind sample (its
own pre-registered minimum resolvable delta was 0.20); `exp_structured_comparator_v1` returned 1
row, 5.5x below its own declared MDE.

**This cell does NOT gate on a hand-scored delta.** It uses KNOWN-ANSWER RECALL against WordNet 3.0
gold meaning sets, with an explicit measured floor, plus a 2AFC arm whose chance level is **0.50 by
construction**.

`exp_grounding_quality_readout_v1` is NOT re-authored: its FULL run completed
(`data/exp_grounding_quality_readout_v1/metrics.json`, 2026-08-12 22:44, STRUCTURAL_PASS_PENDING_B3,
384 + 369 banked facts). STAGE A of this cell RE-SCORES that run's banked output with a floored
discriminator. STAGE B is new because a known-answer test requires querying the read-out with gold
candidates, which no existing artifact contains.

## 2. Organs under test (imported from hdlab, NOT modified)

`hdlab.reading_grounding_loop`: `ConceptSpace` (+`observe`/`bundle`/`anchor_matrix`),
`context_vector_masked`, `canonicalize_fast` (the read-out), `content_lemmas`, `normalize_lemma`.
Corpus: `experiments.exp_definitional_grounding_v5.load_corpus_v5(limit, lineaware=True)` -- the
SAME corpus the 1-3% and 8% numbers were measured on.

## 3. Gold standard (frozen; deliberately GENEROUS, which favours the treatment)

`gold_meaning_set(L)` = lowercased lemma names of, over ALL WordNet 3.0 synsets of L (any POS):
synonyms; direct hypernyms; hypernyms-of-hypernyms (2 up); sister terms (hyponyms of a direct
hypernym); direct hyponyms. Minus L itself and its morphological variants.
A generous gold makes a hit EASIER. A null under a generous gold is conservative.

## 4. STAGE A -- banked-fact known-answer audit (no re-run)

Input: `data/exp_grounding_quality_readout_v1/arm_PBV_{BASE,F1F3}_provenance.json`.
Metric **GOLD_HIT** = fraction of WordNet-evaluable facts (L,O) with `O in gold_meaning_set(L)`.

Arms, all scored on the SAME evaluable fact set (paired):
- `A1_REAL` -- the read-out's actual (L,O) pairing.
- `A2_SCRAMBLE` -- **THE FLOOR.** Deterministic derangement of the object column across subjects
  (same object multiset, destroyed pairing).
- `A3_POPULARITY` -- **THE FLOOR.** Each L assigned an object drawn from the arm's own object
  frequency distribution (seeded).

Bands on `d_A = GOLD_HIT(A1) - GOLD_HIT(A2)`, 5000-replicate paired bootstrap:
- **HARD_PASS_A**: `GOLD_HIT(A1) >= 0.10` AND `d_A >= 0.05` AND `CI(d_A)` excludes 0 AND
  `GOLD_HIT(A1) > GOLD_HIT(A3)`. This is the recorded revival criterion (>=10% against a floor).
- **SIGNAL_ABOVE_FLOOR**: `CI(d_A)` excludes 0 and `d_A > 0` but `GOLD_HIT(A1) < 0.10`.
- **AT_FLOOR**: `CI(d_A)` includes 0 -- the banked meanings are indistinguishable from a random
  re-pairing of the same words. **This outcome is LIVE and expected.**
- **HARD_FAIL_BELOW_FLOOR**: `d_A < 0` and `CI(d_A)` excludes 0.

**TAUTOLOGY RATE** is reported as a first-class number beside GOLD_HIT for every store and arm
(`normalize_lemma(L) == normalize_lemma(O)`), against the recorded <10% criterion.

## 5. STAGE B -- 2AFC known-answer forced choice (chance 0.50 BY CONSTRUCTION)

Items: lemma L (in the space, WordNet-covered, corpus count >= MIN_LEMMA_COUNT) paired with
G = the highest-count anchor in `gold_meaning_set(L)`, and foil F = the anchor whose corpus count is
nearest G's (ratio band [0.5, 2.0]) that is NOT in `gold_meaning_set(L)`, not a variant of L or G,
and whose own gold set excludes L.

Read-out call is hdlab's own: `canonicalize_fast(slot, query, space, thresh=-1.0,
eligible_mask={G,F})` -- pure argmax over exactly two candidates, so **chance is 0.50 and cannot be
floor-pinned by vocabulary size, by saturation, or by a degenerate always-one-answer policy.**

Arms (same items, paired):
- `B1_ACCUM_REAL` -- **PRIMARY.** query = `space.bundle(L)`, L's accumulated context: the actual
  input the reading loop's read-out consumes.
- `B2_ACCUM_SCRAMBLE` -- **THE FLOOR.** query = a donor lemma's bundle (derangement, candidates
  disjoint).
- `B3_FREQUENCY` -- **THE FLOOR.** pick whichever of G/F has the higher corpus count.
- `B4_SENTENCE_REAL` -- secondary: query = a held-out sentence containing L, masked on {L,G,F}.

- `B5_OPEN_REAL` / `B6_OPEN_SCRAMBLE` -- **OPEN-VOCABULARY** read-out: the same query, but ALL
  anchors eligible (`eligible_mask=None`), i.e. the argmax the reading loop actually performs.
  Reported as hit@1 against the gold set with `B6` (donor bundle) as its floor, together with the
  **tautology rate** (`pick == L`). B5 is the closest automated analogue of the open-vocabulary
  MEANINGFUL rate; it carries no HARD_PASS gate of its own and is read against the same
  `>=0.10` revival criterion as STAGE A.

Positive control **SELF_RETRIEVAL** (query = bundle(L), candidates {L, random other anchor}) must be
`>= 0.70`. Below that, STAGE B is reported **VOID_PLUMBING** and makes no quality claim -- a null
would then be about broken machinery, not about meaning.

Bands on `B1`:
- **HARD_PASS_B**: `acc(B1) >= 0.60` AND `CI(acc(B1) - 0.50)` excludes 0 AND `CI(B1 - B2)` excludes
  0 AND `B1 > B3`.
- **MIDDLE_BAND_B**: `CI(B1 - B2)` excludes 0 but `acc(B1) < 0.60`.
- **AT_CHANCE**: `CI(acc(B1) - 0.50)` includes 0. **LIVE and expected.**
- **HARD_FAIL_B**: `acc(B1) < 0.50` and the CI excludes 0.

Power: at n >= 400 items, `se ~ 0.025`, MDE_95 ~ 0.049 < the 0.10 band width. A run with
n < MIN_ITEMS (200) is reported `INSUFFICIENT_ITEMS_NO_READ` rather than read underpowered.

## 6. Declared leak, left IN on purpose

L's accumulated bundle may include sentences in which G co-occurs. Co-occurrence IS the read-out's
mechanism, so removing it would test a different organ. The leak biases **towards** the treatment;
a null under it is conservative. Both floor arms are computed on the same leaked space.

## 7. Comparator setting

`HD_GRADED_COMPARATOR` is ON at HEAD (`38f7a0d5c`, 2026-08-14). STAGE B is run under **both** 1 and
0 and both are reported. STAGE A re-scores facts banked on 2026-08-12, i.e. **before** the flip;
that provenance is stated with the number and no cross-setting comparison is drawn.

## 8. What this cell may NOT claim

- GOLD_HIT is not identical to a human MEANINGFUL judgement. It is a KNOWN-ANSWER PROXY chosen
  because it has a floor; the hand-score does not. Convergence with the prior hand-score is reported
  as evidence about the proxy, never as a substitute for it.
- STAGE B accuracy is a 2-candidate forced choice; it does NOT license any statement about the
  open-vocabulary argmax rate. Only STAGE A speaks to that.
- Nothing here licenses resuming knowledge-base growth unless HARD_PASS_A holds.
