# Full parser-replacement: consumer-by-consumer analysis (owner's expanded scope, 2026-09-04)

Owner: "prototype a full replacement for the parser so that it maximizes results for all consumers. Some
consumers might not be brain foundational, and where that is true, we can prototype an optimized consumer too"
+ "there is a default off parser that is way better, but it's default off because one of the consumers gets
killed by it."

Two exhaustive audits enumerated every consumer of the dependency parse on the LIVE reading path
(`hdlab/situation_reader.py read()`). This is the reconciled map + the design conclusion.

## THE FINDING THAT REFRAMES "REPLACE THE PARSER"

**The parse's value to its consumers is in LABELS + VOICE + VALENCY + per-arc CONFIDENCE -- not head accuracy.**
- Head accuracy is head-INDEPENDENT for who-did-what: live arc_parser (UAS 0.79) vs arceager (UAS 0.842) gives
  the same patient readout gain (+0.077); the deployed AGENT is taken off a Competition-Model readout that reads
  NO arc heads (0.317 -> 0.690).
- The parse already computes TWO brain signals the live consumers throw away: (a) dependency LABELS -- only 1 of
  ~5 head-consumers reads them; (b) per-arc CONFIDENCE -- produced by both parsers, consumed by ZERO live
  consumers, yet the arc_parser margin discriminates a correct object attachment at AUC 0.81.
- Register-general HEAD parsing has three prior located-negatives on disk (delexicalization flat OOD;
  register-native training REFUTED; EM self-training flat). Building a fancier head parser is the documented
  low-value move.

**So the brain-faithful "full replacement" is a register-general READOUT LAYER over the best available parse**
-- labeled grammatical relations + voice remapping + valency-slot binding + confidence precision-weighting --
which maximizes the head-driven consumers AND makes the better parser register-SAFE (the answer to the hint:
the default-off arceager "kills" the 19c consumer only because that consumer TRUSTS the parse unconditionally;
under the labeled/valency/voice readout arceager is +0.0045 on 19c clean-DO, not -0.0017).

## THE CONSUMER MAP (live path)

Head-driven = the parse `heads` change its output. Legend: BF = brain-foundational; OI = OUR-INVENTION placeholder.

| # | consumer (fn) | extracts | reads parse via | head-driven? | brain-fidelity | needs from an ideal parse |
|---|---|---|---|---|---|---|
| A1 | router `route_predicate_arguments` | who-did-what PATIENT + PP/spatial roles | heads + POSITION + VOICE; patient=`structural_patient_pick` | YES (patient 0.75->0.91 gold; PP obl-heavy) | PATIENT BF-basis (this fix); the router AGENT is OI (positional) but overridden live | LABELED obj/nsubj:pass (this fix); correct voice (this fix); obl attach |
| A2 | SPACE `_read_space` | per-entity location/goal/path/source | heads head-chain walks + prep | YES (obl/PP-heavy) | PINNED (noisy-channel parse-as-evidence) | **obl attach (0.69->1.0 gold)**; per-arc confidence to weight evidence vs prior |
| A3 | copular `_read_entity_states` | "what is X" (holder/property) | arc LABELS (`ArcLabeler`) + `robust_cop` | YES (label-driven) | PINNED (Kimian state); the ONLY live label consumer | labeled cop/nsubj; but detection-recall matters more (solved by robust_cop) |
| A4 | world-state `_read_world_state` | has/holder/is_open | router recipient/source (indirect) | weak (ARG2 only) | PINNED; dominant residual is COREF | recipient/source PP attach; else coref |
| A5 | belief `_read_belief` | ToM channels | via A2 (indirect) | weak | PINNED | inherits A2 |
| B1 | AGENT `cm_agent` | who-did-what AGENT | toks/POS/animacy/coref (NO heads) | NO (0.317->0.690 head-independent) | **PINNED** (Competition Model) -- the BF replacement for the OI router agent | a labeled `nsubj` cue INTO the competition (sibling problem) |
| B2 | predict_revise `resolve_patient` | dropped patients | UPOS + relativizers + VOICE (NO heads) | NO | BF (filler-gap) | -- (voice already precise here) |
| B3 | verb_subcat_gate | patient PRESENCE | verb lemma (NO parse) | NO | PINNED-basis; wired gate is the SIMPLE lexical threshold | the GRADED Competition-Model gate is built + UNWIRED (WIRING DEBT 2) |
| B4 | surprisal `_read_surprisal` | N400 confidence | POS candidates (NO heads) | NO | PINNED | -- |
| B5 | goals/affect | goal + emotion | POS + coref + subcat frames (NO heads) | NO | PINNED-dissociated | -- |
| C | coref / events-detection / time / causation | entities, predicates, order, cause | NO parse (POS/coref/connectives) | NO | mixed | -- |

## THE OPTIMIZED (brain-faithful) CONSUMERS -- named per the owner's ask

- **PATIENT readout (A1) -- BUILT + measured (this problem):** position -> labeled obj-slot + precise voice +
  valency binding. +0.086 CI-sep clean UD, +0.097 19c clean-DO, head-independent, zero-param. The optimized,
  brain-faithful consumer that replaces the positional patient read.
- **AGENT (router, A1) is OI (positional "nearest pre-verbal nominal" + quotative inversion)** -- but ALREADY
  replaced live by the BF Competition-Model agent (B1). The next brain-faithful step is a labeled `nsubj` cue
  INTO that competition = the sibling `the_agent_tie_wall...` problem. Not duplicated here.
- **verb_subcat gate (B3) is OI-simple (lexical threshold)** -- the BF GRADED Competition-Model presence gate
  (`verb_subcat.patient_present`, AUC 0.777, who-did-what 0.30->0.49) is built but UNWIRED (needs POS + patient
  index at role-assignment time; WIRING DEBT 2). A ready optimized consumer.
- **SPACE/PP (A2) is the one genuine remaining HEAD lever:** obl attach 0.69 (live) / 0.72 (arceager) / 1.0
  (gold). Its QA is saturated (location = 1.0 on the 16-doc gold), so an obl improvement is not measurable on the
  current instrument -- a candidate follow-on that needs an obl-sensitive instrument first.
- **Curated-list / fixed-window placeholders (OI):** `SPEECH_VERBS` / `ANIMATE_NOUNS` / `_CURATED_PLACES` /
  `i//LOCAL_WINDOW` scene segmentation -- flagged OI; out of this problem's patient scope.

## THE DISCARDED BRAIN SIGNAL: per-arc CONFIDENCE (precision-weighting)

Both parsers emit per-arc confidence; ZERO live consumers read it. Measured: the arc_parser margin discriminates
a correct object attachment at AUC 0.81 (arceager conf is miscalibrated at 0.54; its margin 0.72). This is the
Friston precision signal the register-safe consumption needs: trust the labeled arc where confident, fall back to
the register-general readout where not. It is what lets the better (arceager) parser be turned on without killing
the OOD consumer -- and it is already computed, just thrown away.

## RECOMMENDED FULL-REPLACEMENT LANDING (Q111, strategy owns)

1. Land the PATIENT readout (precise voice one-liner; then labeled+valency `structural_patient_pick`).
2. Wire the GRADED `verb_subcat.patient_present` presence gate mid-role-path (WIRING DEBT 2).
3. Expose per-arc CONFIDENCE to the router + SPACE consumer and precision-weight; then re-enable `parser_arceager`
   (now register-safe) and re-measure end-to-end.
4. File the obl/PP instrument + the labeled-nsubj-into-CM-agent (sibling) as follow-ons.

The "full replacement" is therefore NOT a new head parser -- it is the labeled/valency/voice/confidence READOUT
layer + the two unwired BF consumers, which is register-general and unblocks the better parser.
