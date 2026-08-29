# Candidate follow-on briefs (from the verb-sense-disambiguator solve, 2026-08-28)

Two adjacent problems this solve repeatedly bottlenecked on. Written in the PROBLEM.md shape so the strategy
session can promote either to `notes/problems/<slug>/PROBLEM.md`. Both are HIGHER leverage than any remaining
tweak to the disambiguator itself (which is converged: all four bars clear).

---

## BRIEF A -- `coreference_for_anaphoric_arguments`  [the #1 real-narrative cap, named across problems]

**THE PROBLEM (plain).** A reader can't tell what "it/him/them" refers to without resolving the antecedent, and
that blocks several front-ends: the verb-sense disambiguator can't TYPE a pronoun object ("she saw **it**" -- a
bird? a point?), the location register can't track the destination of a thrown/sent object ("he threw **it** to
her"), and entity tracking / the ToM cue mis-handle re-entry and occlusion. Coreference (~0.65 on real narrative)
is the dominant cap this project keeps hitting.

**WHY THIS ONE.** MEASURED on disk: (1) the verb-sense solve DEFERRED pronoun-object typing (`dobj_types = {}` for
PRON) because typing "it/him" without the referent is a guess -- correct, but it leaves the disambiguator blind on
anaphoric objects; (2) the location_register solve explicitly mapped the ambiguous caused-motion "to X" head
(throw/send it to X) to coref as the residual; (3) `the_live_front_end_mislabels_who_did_what_to_whom` and the ToM
observation-cue residual both name coref. One glass-box coref unblocks all of these.

**HOW THE BRAIN DOES IT.** Reference resolution binds a pronoun to a discourse-active entity via the situation
model + attentional focus (Centering theory; Ariel's Accessibility; the ACT-R salience binder already in the
substrate: `hdlab/bundle_focus_coref`). Copy the salience/recency + agreement + selectional-fit computation; sweep
the weights.

**THE BAR (draft).** A glass-box coref that resolves pronoun/anaphoric ARGUMENTS in running narrative beats a
nearest-noun / string-match floor CI-separated on a real gold (LitBank/OntoNotes coref, or the project's mined
narrative), the info-free twin (shuffled antecedents) loses, AND it LIFTS a downstream CI-separated -- either the
verb-sense anaphoric-object typing (feed the resolved head into `frame_sense_disambiguator`) or entity tracking.

**ENTRY POINTS.** `hdlab/bundle_focus_coref.py`; experiments/frame_sense_disambiguator.py (the `dobj_coref` field
already extracted in exp_frame_sense_semcor_v1's cache is a starting signal); LitBank coref layer.

---

## BRIEF B -- `wire_the_event_frame_as_a_shared_primitive`  [shared primitive, not island]

**THE PROBLEM (plain).** The verb-sense disambiguator produces a coarse EVENT FRAME (motion / deposit / perception
/ communication / change / ...) that SEVERAL front-ends each need but currently re-implement or ignore: the
situation model's EVENT slot, the location register's MOTION gate ("is this a motion event?"), and the ToM ledger's
DEPARTURE/observation cue. Each pays the verb-polysemy tax separately. Wire ONE event-type read feeding all of them.

**WHY THIS ONE.** MEASURED: the disambiguator's gate measurably improves the un-disambiguated motion decision the
ledger makes (bar 3 of the verb-sense solve: 0.611 -> 0.685 on a real gold, CI-separated, McNemar p=8e-06). That
lift currently lives in an experiments/ cell; propagating the single event-type read into `situation_model_accumulate`
+ `location_register` + `perceptual_access_ledger` would carry the improvement into the live reader and delete three
copies of "which event is this?".

**HOW THE BRAIN DOES IT.** A single event-schema representation (event semantics, ATL/pSTS) feeds multiple
consumers (the location update, the belief update, the situation model) -- not three private re-derivations. The
coarse event-frame IS that schema at the grain the consumers use.

**THE BAR (draft).** The shared event-type read (promote `frame_sense_disambiguator` -> hdlab, gated context ON),
wired into >=2 consumers, measurably improves EACH vs its current (un-disambiguated / re-implemented) behaviour on
the LIVE reader, CI-separated; no consumer regresses. Keep the no-LLM invariant; keep the reliability gate
(precision-weighting) so it defers where context is unreliable.

**ENTRY POINTS.** experiments/frame_sense_disambiguator.py + experiments/context_prior.py + data/{idiom_foundation_v1,
context_prior_v1} (the proposed hdlab promotion); hdlab/{situation_reader,location_register?,perceptual_access_ledger}.
Strategy owns the hdlab landing (Q111).

---

**NOTE.** Both are the owner's to prioritise. Brief A (coref) is the higher-leverage capability gap; Brief B is a
wiring/integration that banks an already-measured win. The verb-sense disambiguator itself needs no further work
beyond the optional cue-calibration finding (documented: hand weights near-optimal; posterior approximately, not
exactly, calibrated -- ECE ~0.21).
