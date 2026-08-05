# Pre-reg: BRIDGE-1 original-failure payoff test (C-C)

Anchor: `bridge1_original_failure_payoff_v1`. Author: exp_dev. Date 2026-08-05.

## Question
Does the CERTIFIED two-stage grounding (governor sense-select stage-1, from
`experiments/exp_bridge1_governor_grounding_v1.py`, cert `notes/landed_vet_bridge1_foundation.md`
commit f06c06535) actually CLEAR the ORIGINAL affect-reader failures that motivated this whole
build, on its CERTIFIED scope -- replacing `resolve_valence_blind`
(`experiments/exp_grounded_structure_phase0_probe_v1.py:133`) where it is wrong, on real data?

## Reused, unmodified (do NOT rebuild)
- `resolve_valence_blind` -- the reader being replaced (imported directly, never reimplemented).
- `exp_bridge1_governor_grounding_v1`: `GOVERNOR_VERB_CLASS`, `ADJ_MODIFIER_CLASS`,
  `extract_governor_feats`, `gold_type_from_classes`, `nearest_verb_idx`, `adjmod_idx`, `mk_item`,
  `COLLISION_PAIRS`, `TRAIN_ITEMS`, `_scrambled_class_dict` -- the CERTIFIED governor stage
  (differential grounding 0.967, 5-seed cert 96e8e8404). Perceptron is RE-FIT here (3 seeds:
  0,1,2 -- not the full 5-seed cert sweep; this cell tests TRANSFER to new items, not
  re-certification of the mechanism itself, which already stands on disk).
- `hdlab.thematic_role_labeler.train_perceptron` -- the earned perceptron engine.

## Eval set assembly + scope labeling (assembled from the pointers in the spawn task)

### A) Word-sense collision core (task-named, IN-SCOPE, governor axis)
The `hard` and `trick` collision pairs already built into
`exp_bridge1_governor_grounding_v1.COLLISION_PAIRS` (4 items: hard_A_nonharm/hard_B_harm,
trick_A_nonharm/trick_B_harm). These are the literal "studied hard vs hit hard" / "a card trick
vs a cruel trick" pairs named in the spawn task. IN_SCOPE: governor sense-select is exactly the
certified mechanism for this axis (TEST-pool governor verbs `practice`/`attack`/`know`, TEST-pool
adjective `vicious`).

### B) Real-corpus word-sense false positives (IN-SCOPE, governor axis)
Two items pulled from `data/exp_maintained_affect_narrative_irony_probe_v1/metrics.json` (run
2026-08-05, `grapp_sincere_003`/`grapp_sincere_005` false-positive rows), traced back to source
text via `paragraphs_for()`:
- `missed_a_trick_real`: Tom Sawyer line 570, "...and missed a trick." `resolve_valence_blind`
  fires HARM on the token `trick` (in `HARM_WORDS`). Gold sense: NON-HARM (idiom, "missed an
  opportunity"). Local governor context hand-tagged (declared simplification, same convention as
  `mk_item`'s hand-tagged POS lists used throughout this cell family): governor = "missed" ->
  lemma "mis" (lemmatizer double-consonant artifact, harmless here) -> UNK class (not in
  GOVERNOR_VERB_CLASS either way) -> NEUTRAL by the UNK-default rule.
- `studied_hard_real`: Anne of Green Gables line 8778, "We've studied hard and...".
  `resolve_valence_blind` fires HARM on the token `hard`. Gold sense: NON-HARM (adverbial
  intensifier). Governor = "studied" -> lemma "study" -> literally in `TRAIN_NEUTRAL_VERBS` ->
  NEUTRAL class.
Both IN_SCOPE: force-capable-governor identification is exactly the certified stage-1 axis;
both governors resolve to non-force classes (one by explicit list membership, one by UNK-default),
which is the correct behavior either way.

### C) Confused-4 (relinf_unstated_007/010/011/012) -- scope audited per item, NOT assumed in-scope
Traced via `ci.load_gold()['unstated_goal']`:
- `relinf_unstated_007` ("...let her take care of herself") -- OUT_OF_SCOPE. Irony/discourse:
  gold=REVENGE_PUNISH (spiteful abandonment) but surface reads HELP-toned ("take care"). No
  force-verb+patient collision exists here at all; this is the STAGE-2b discourse port, proven
  NOT open-vocab-tested per the cert (`notes/landed_vet_bridge1_foundation.md` Axis 5).
- `relinf_unstated_010` ("carefully skating... sounding the ice") -- OUT_OF_SCOPE. No force verb,
  no HARM/HELP-class governor or adjective present (governor="skate"/"sound", both UNK to
  GOVERNOR_VERB_CLASS); the item's only valence-bearing cue is the adverb "carefully" (HELP_WORDS
  token, not a governor/adjective-modifier structure bridge1 operates on). Not a collision the
  two-stage mechanism can even see.
- `relinf_unstated_011` ("...slapped the Lion upon his nose as hard as she could...") --
  MECHANICALLY IN-SCOPE (governor="slap", literally in TEST_HARM_VERBS; patient="Lion", animate)
  but gold_valence=HELP (PROTECT_OTHERS, `sgv.CATEGORY_TARGET_VALENCE`) because the actual harmed
  entity (Lion) is the ADVERSARY, not the beneficiary (Toto) -- a PATIENT-vs-BENEFICIARY
  distinction the cert explicitly names as PROVEN GAP #2 (social-relational, needs a
  relational/social-appraisal signal, not animacy/force). Both `resolve_valence_blind` (token
  "slapped" in HARM_WORDS) AND the two-stage grounding (governor="slap"->HARM class) predict HARM
  here -- BOTH WRONG, for the SAME architectural reason (neither has beneficiary-tracking).
  Reported as a TIED-FAILURE on a DIFFERENT proven gap, not counted toward HARD_PASS/FAIL.
- `relinf_unstated_012` ("...box her own ears for having cheated herself...") -- OUT_OF_SCOPE.
  Target patient "ears" is a body-part noun (PROVEN GAP #1, body-part -> WordNet inanimate ->
  no lift either way).

**Honest finding, pre-registered before running:** zero of the 4 confused-4 items are cleanly
IN-SCOPE for the governor/animacy axis with room for the two-stage grounding to "beat"
`resolve_valence_blind` -- 3 are out-of-scope (discourse, no-collision-structure, body-part) and
the 4th is a same-cause tie on a DIFFERENT proven gap (beneficiary tracking). This is reported as
a labeled diagnostic section, not forced into the HARD_PASS gate, per the spawn task's own
instruction ("if it clears fewer original failures than expected, drill WHY per-item -- that's
the deliverable").

## Bands (pre-registered, scoped to what is actually IN-SCOPE)
- **HARD_PASS**: two-stage grounding correctly resolves the NAMED collision core (hard_A, hard_B,
  trick_A, trick_B: 4/4 correct-sign) AND clears BOTH real-corpus FPs (studied_hard_real,
  missed_a_trick_real: both predicted non-harm) AND `resolve_valence_blind` itself is WRONG on a
  strict majority of these 6 items (>=4/6) -- i.e. the replacement's win is real, not a no-op
  because the baseline was already fine.
- **MIDDLE_BAND**: two-stage grounding clears >=4/6 of the above but not all 6, or
  `resolve_valence_blind`'s own failure rate on these 6 is <4/6 (baseline not clearly the thing
  being fixed).
- **HARD_FAIL**: two-stage grounding clears <4/6.
- Confused-4 (item 011 tied-failure + 3 out-of-scope) reported separately, always, regardless of
  the above verdict -- never silently folded into the gate.

## Controls
- Scramble control on item 011's governor class (per `_scrambled_class_dict`, same construction
  as the cert's SCRAMBLED-GOVERNOR arm) -- demonstrates the two-stage signal is NOT inert (changes
  under scramble) even where it agrees with `resolve_valence_blind`'s wrong answer, in contrast to
  `resolve_valence_blind`'s own measured inertness on confused_4 in the phase0 probe
  (`data/exp_grounded_structure_phase0_probe_v1/metrics.json`:
  GROUNDED_ORACLE_SCRAMBLED_VALENCE_accuracy == GROUNDED_ORACLE_NARRATIVE_accuracy == 0.75, i.e.
  scrambling the OLD valence table left the OLD pipeline's confused_4 accuracy unchanged --
  MEASURED, cited not recomputed here).
- No leakage: real-corpus items' hand-tagged local governor windows never read the gold
  category/valence label to construct the tokens/POS -- only the surrounding SURFACE TEXT.

## Compute architecture
Sequential-CPU, single-shot, <5s total (12 collision items + 2 real-FP items + 4 confused-4 items
x 3 seeds for the perceptron fit == trivial). `cell_chunked: false`. `crlb_n/a`: fixed small
discriminator set, no capacity sweep. `final_metrics_atomicity: tmp_replace`.
