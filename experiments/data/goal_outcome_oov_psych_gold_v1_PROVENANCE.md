# goal_outcome_oov_psych_gold_v1.jsonl -- provenance

## Purpose
Goal-owner eval items whose GOAL VERB is OUT-OF-VOCABULARY to the production frame table
(`hdlab.frame_induction.is_oov`, checked against `hdlab.thematic_role_labeler.VERB_FRAMES`), so
they can exercise the OOV-psych frame-INDUCTION wire (`hdlab/frame_induction.py`, wired into
`hdlab/situation_reader.py` `_assign_frame_primary_roles`, commit 22b9b6f8e). The existing bank
(`experiments/data/goal_outcome_c3mined_v1.jsonl`, 38 items) was mined WITH `PSYCH_VERBS` as the
goal-verb prefilter, so every item in it is in-vocab by construction and cannot test the induction
path.

## OOV target verb inventory (step 1)
16 psych/experiencer/desiderative verbs, hand-assembled from a broader
admiration/aversion/desire lexicon, explicitly checked to have ZERO overlap with
`hdlab.thematic_role_labeler.PSYCH_VERBS` (the 47-verb production in-vocab set) and confirmed
`is_oov(lemma)==True` for both the dictionary base form and every inflected surface form's
`lemma_verb()` output (the SAME lemmatizer the mining and induction code paths both call, so OOV
status is internally consistent end to end):

- aversive: loathe, despise, abhor, detest, resent, scorn, disdain
- positive/desiderative: crave, covet, cherish, treasure, relish, idolize, worship, dote, esteem

Verified via `hdlab.frame_induction.is_oov` + `hdlab.thematic_role_labeler.lemma_verb` (see session
transcript): all 16 base forms and all tested inflections (loathed/loathing, despised/despising,
abhorred/abhorring, detested/detesting, resented/resenting, scorned/scorning,
disdained/disdaining, craved/craving, coveted/coveting, cherished/cherishing,
treasured/treasuring, relished/relishing, idolized/idolizing, worshipped/worshiped/worshipping,
doted/doting, esteemed/esteeming) -> `is_oov == True`.

## Mining (step 2) -- `experiments/mine_goal_outcome_oov_psych_v1.py`
Reuses `mine_goal_outcome_litbank_c3syntax_v1.py`'s owner resolver bit-identical
(`build_roster_c3`, `c3_syntax_owner` -- POS-verb gate, passive gate, animacy gate, parser-licensed
subject candidates via `hdlab/candidate_generator.py`) and `mine_goal_outcome_litbank_v1.py`'s
sentence loader / outcome-cue lexicon / diversity selector. New logic is ONLY the OOV-verb
prefilter and two mining-time fixes added mid-task per Director direction (a parallel finding on
the C-F quotative-wiring cell showed the OLD bank's dominant failure mode was narrow text windows
where the resolved owner's name never appears in the item's own text):

1. **Wide, self-contained window**: track (sentence_idx, name) for every named roster mention.
   When the owner is resolved via pronoun, the item's text window is extended BACKWARD to the
   sentence where that name was last mentioned, so the owner is NAMED and resolvable from the
   item's own text (not from off-window global state). Bounded at `MAX_BACKWARD_SENT=6`. In this
   run every selected item resolved with `window_backward_sentences=0` (owner named directly in
   the goal sentence, or a same-sentence pronoun resolving to a same-sentence name) except one raw
   item resolved via pronoun to a same-sentence roster match (later DROPPED at gold review as a
   roster-corruption false positive -- see below).
2. **Non-quoted outcome**: items whose outcome sentence contains a `"` are dropped (dialogue lines
   are exactly the quote-fracture pathology -- speaker outside window -- the Director flagged on
   the parallel cell). NOTE (honest gap found during gold review): this filter only checks
   double-quote characters; several litbank novels render dialogue with single quotes, so some
   quote-fracture-prone items still slipped through the automated filter and had to be caught by
   hand at gold review (see DROPPED below).

Scan: 100 novels, per-novel prefilter budget 60 OOV-psych-verb-prefiltered sentences.
Raw yield: **21 owner-resolved, window-clean, non-double-quoted items**
(`experiments/data/goal_outcome_oov_psych_v1.jsonl`, RAW/unreviewed). Prefilter funnel (raw token
hits of the 16 target lemmas = 3398 across 100 novels; after OOV-psych-verb prefilter budget =
2324 sentences scanned):
`owner_unresolved_VERB_NOT_POS_VERB_OR_NOT_LOCATED=986`,
`owner_unresolved_SUBJ_TOKEN_NOT_ROSTER_NAME_OR_PRONOUN=745`,
`owner_unresolved_PRONOUN_NO_GENDER_COMPATIBLE_ANTECEDENT=305`,
`owner_unresolved_NO_PARSER_LICENSED_SUBJ_CANDIDATE=151`,
`owner_unresolved_PASSIVE_PSYCH_SUBJECT_IS_PATIENT_NOT_EXPERIENCER=65`,
`no_outcome_in_window=25`, `skip_outcome_has_quote=18`, `skip_antecedent_too_far=6`,
`owner_unresolved_SUBJECT_INANIMATE_NOT_GOAL_HOLDER=2`.

## Gold review (step 3, triple-check discipline) -- HONEST, load-bearing finding
All 21 raw items were read in context by hand. **13 of 21 were dropped** at gold review for one of
three failure classes, all pre-existing weaknesses of the reused mining infrastructure (not
specific to the OOV-verb prefilter):
- **Owner extraction wrong** (6 items): a common noun or role-word got into the proper-noun roster
  and was picked as "owner" (`"Frenchman"`, `"Christian"`, `"Girls"` from "Camp Fire Girls" --
  gender-only pronoun antecedent search matched the wrong nearest name); a multi-word name split
  across a first-token/foil pair (`"Mary Ann"` mined as owner=Mary, foil=Ann, one person not two);
  a subject/object confusion inside a coordinated gerund clause (Fagin "cherished" Oliver, mined
  with owner=Oliver); a past-participle used adjectivally, not as a finite predicate with a real
  subject (`"most cherished personal treasures"`).
- **Outcome topically unrelated to the goal** (6 items): the reused ACHIEVE_CUES/BLOCK_CUES
  forward-window scan is topic-blind -- it fires on the first sentence within 7 sentences that
  contains an achieve/block-lexicon word, with NO check that the sentence is actually about the
  same character/goal. Several "dispersed" items picked up an unrelated plot beat (a tombstone
  inscription, an unrelated character's arrival, an unrelated topic shift).
- **Single-quote dialogue slipped the double-quote-only filter** (1 item): confirms the filter gap
  noted above.

This is a genuine, reportable finding: the topic-blind outcome-cue window and the roster's
proper-noun admission are the SAME weak links that degraded the original in-vocab bank, and they
dominate yield loss here too (mining infra issue, not an OOV-specific issue).

**6 items survive gold review** (`experiments/data/goal_outcome_oov_psych_gold_v1.jsonl`) with an
explicit per-item `gold_confidence` (`high`/`medium`/`low_medium`/`low`) and `gold_notes` caveat
where applicable (negated-verb polarity inversion, object-dependent polarity, sentence-fragment
truncation, weak outcome-topic relevance). `gold_outcome_polarity` was hand-corrected where the
auto-mined `outcome_polarity` read backwards on manual re-read (2 of 6 items).

**This falls short of the >=15 target.** Per the task's own honesty clause ("if the corpus yields
few clean items, report the true N + why -- routes to SUPPLY as a finding, do NOT pad with noisy
items"): the true bottleneck is NOT verb rarity (2324 sentences were prefiltered on the 16 target
lemmas, comparable in scale to the in-vocab miner's budget) but the mining infrastructure's
topic-blind outcome-window and roster-admission false-positive rate, which this task was not
scoped to fix. A follow-up cell that hardens `mine_goal_outcome_litbank_v1`'s roster gates and adds
a topical-relevance check to the outcome-cue window (e.g. require the outcome sentence to mention
the owner or a roster member, which most dropped items in fact violate) would likely raise clean
yield on BOTH banks; that is the honest next step, not something papered over here.

## Sanity eval (step 4) -- production `frame_primary_role` via `SituationReader`
For each of the 6 gold items, the `goal_sentence` was fed through `hdlab.situation_reader
.SituationReader.read()` (the actual production code path `_selftest_frame_primary_wiring` in
`hdlab/situation_reader.py` exercises), with the mined `goal_owner` token tagged as a coref mention
so `_pick_role_mentions` can find a subject candidate. Result:
- 3/6 items: **no event was extracted for the goal verb at all** -- a pre-existing gap in the
  production event extractor (participial/non-finite clauses e.g. "Mary, resenting that...", and
  coordinated-VP constructions e.g. "had long owned and cherished", are not modeled as events by
  `_read_events`/`_pick_role_mentions`; one item's full sentence produced zero events). Honest:
  these are NOT OOV-wire failures, they are upstream event-extraction gaps this bank surfaces.
- 3/6 items resolved an event for the goal verb: **1/3 typed EXPERIENCER** (Dave/"resented", the
  induction fired correctly), **2/3 typed AGENT** (Ernest/"worshipped", Ahab/"cherished" -- the
  induced hypothesis abstained on these constructions and honestly fell back to the positional
  AGENT default, per the wire's own documented abstain-not-overclaim design).
- This is consistent with the wire's own measured held-out accuracy (subj-axis acc=0.833,
  MIDDLE_BAND per `data/exp_frame_induction_oov_psych_real_v1/metrics.json`, cited in
  `hdlab/situation_reader.py`'s own self-test docstring) at this tiny n=3-resolved sample: the
  induction is a real, measurable, non-1.0 improvement over always-AGENT, not a saturated win.

## Files
- `experiments/mine_goal_outcome_oov_psych_v1.py` -- the miner (has `--self-test`).
- `experiments/data/goal_outcome_oov_psych_v1.jsonl` -- RAW 21-item mined output (pre-gold-review).
- `experiments/data/goal_outcome_oov_psych_gold_v1.jsonl` -- the 6-item GOLD-reviewed bank (the
  deliverable), with `gold_outcome_polarity`, `gold_confidence`, `gold_notes`,
  `sanity_frame_primary_subj_role` fields added on top of the raw mined schema.
