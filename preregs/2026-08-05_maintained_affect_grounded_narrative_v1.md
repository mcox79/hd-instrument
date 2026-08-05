# Pre-reg: maintained_affect_grounded_narrative_v1 (C-D part 1: situation-model AFFECT dimension)

Cell: experiments/exp_maintained_affect_grounded_narrative_v1.py
Anchor: maintained_affect_grounded_narrative_v1  | LOCAL-only, glass-box, no origin push.

## Question
Does a per-entity MAINTAINED affect trajectory, populated by the VALIDATED two-stage grounding
(governor class + WordNet-animacy event-assembly; certified notes/landed_vet_bridge1_foundation.md)
instead of resolve_valence_blind, recover the narrative-only irony items the v1 blind-lexicon probe
(exp_maintained_affect_narrative_irony_probe_v1, NULL_FALSE_POSITIVES: narrative 1/3, sincere_fp 2/5)
MISSED -- while clearing v1's 2 sincere false-positives? This is the affect DIMENSION only; the
forward-projection PREDICTION step is C-D PART 2 (NOT attempted here).

## Mechanism (what it extends)
Keeps v1's coref-lite maintenance mechanism (wide 400-line strictly-prior entity-name-variant window +
majority-vote maintained state + asymmetric HARM incongruity override) UNCHANGED; swaps ONLY the
per-event scorer: spaCy (verb, direct-object) extraction -> ea.event_type_for_item_real +
FORCE_CLASS_HARM_REAL + real_animacy_lookup (open-vocab WordNet animacy) with bridge1
GOVERNOR_VERB_CLASS stage-1 fallback. Coref = declared lite proxy (SituationModel.read needs a CoNLL
mention stream unavailable for raw novel text at this scope) -- flagged, not silently substituted.

## Arms
(a) arm_c_local (no maintenance); (b) old_blind_maintained = v1's NULL (recomputed live via v1 fns,
must reproduce v1 disk = narrative 1/3, fp 2/5); (c) new_grounded_maintained (the fix);
(d) per-token pooling (entity-BLIND blind-vote over the window; integration must beat it).

## Bands (pre-registered BEFORE running)
- HARD_PASS: grounded recovers >=2/3 narrative-missed AND grounded_sincere_fp==0 AND beats pooling.
- PARTIAL_NEEDS_PREDICTION: FPs cleared / present-state improved but narrative recovery short ->
  forward-dread routes to C-D part 2 (prediction).
- MIDDLE_BAND: strictly better than NULL on narrative and/or FP and beats pooling, but neither the
  clean 0-FP HARD_PASS nor the FP-fully-cleared PARTIAL.
- HARD_FAIL_NO_BETTER_THAN_NULL: grounded narrative <= old-blind AND grounded_fp >= old-blind_fp.

## Controls / no-leakage
Trajectory scanner never reads any gold answer field (true_intent_valence / supporting_span /
surface_valence); window strictly prior, excludes arm_c's own +-2 local lines. Pooling arm =
entity-blind must-be-beaten control. arms_must_differ (META_RULE_AF): grounded vector MUST differ
from old-blind (that IS the grounding-fix discriminator) -- asserted, cell raises otherwise.

## Result (MEASURED@data/exp_maintained_affect_grounded_narrative_v1/metrics.json)
MIDDLE_BAND: grounded narrative 2/3 [irony_002, irony_003] vs old_blind NULL 1/3 [irony_002] vs
pooling 0/3; grounded_fp 1/5 vs old_blind_fp 2/5 (one cleared); beats_pooling=True.
- irony_005 MISS: dread = FORWARD expectation (fake-deathbed manipulation), no present harm event ->
  correctly routes to C-D part 2 (prediction).
- residual sincere_005 FP: governor word-sense leak on "beat" (benign senses: heartbeat / "beat to
  the Island") where the C-C event-stage sense-resolution can't engage (dobj None / proper-noun
  animacy lookup None) -> stage-1 governor HARM leaks. Routes to C-AB/C-C sense-resolution scope,
  NOT a maintenance/coref failure.
