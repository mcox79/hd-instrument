---
problem: situation_model_has_no_mutable_world_state_register
status: PARTIAL
bar: "PASS = the mutable world-state register, driven by the reader's OWN extraction, answers STATE queries (is obj X open / does agent have Y / where is Z, at story-time t) CI-SEPARATED over the strongest no-state-tracking floor actually run -- (a) LAST-MENTION / static and (b) a no-model surface baseline -- on a population with state-CHANGING events, with the info-free TWIN (shuffle which event's effect updates which predicate, or a random-effect twin) LOSING CI-separated, AND a positive control that the register's answer CHANGES at the updating event (not a constant). A rigorous NEGATIVE is a full PASS if located: name precisely whether the wall is the register MECHANISM or extraction RECALL of implicit preconditions/effects (and the coref coverage)."
result: "MECHANISM (construction gold, isolates tracking; n=960 possession-transfer + open/close re-toggle queries): register 1.000 [1.000,1.000] vs strongest no-state-tracking floor last_obj_mention 0.750 [0.722,0.778], +0.250 [0.224,0.277], null p95 0.026. PRECONDITION-READ (n=1200 balanced): register detects violations 1.000 vs strongest trivial ever-had 0.512, +0.488 [0.461,0.518]. OPERATORS FROM WHAT WE HAVE: 105 transfer verbs across 13 FrameNet frames WITH recipient/source roles (replaces the hand lexicon; fixes the recipient slot at the resource level). LEARN-AND-ADAPT: operators INDUCED from observed possession transitions recover FrameNet gold 1.000 [1.000,1.000] (n=24 held-out verbs) vs shuffle-twin 0.417 (+0.583 CI-sep), abstains on non-transfer verbs, register driven by LEARNED operators is downstream-usable 1.000. OPEN TEXT via the substrate's OWN parser (MCScript2, 1500 real sentences): 1467 transfer instances fire (GET 926 / LOSE 313 / GIVE 228); role recovery theme 0.78 / agent 0.51 / recipient-on-GIVE 0.33 (was 0 with stock extract_args) / source-on-GET 0.11; end-to-end who-has-what is LOCATED as coref-bound (81% of real agents are pronouns) + recipient-PP + verb-sense precision -- NOT the mechanism or the operator lexicon."
floor: "MECHANISM: strongest of four no-state-tracking floors on n=960: last_obj_mention 0.750 [0.722,0.778] (hi 0.778); recency_subject 0.250; ever_entity 0.250; first_holder 0.125 -- register lower CI 1.000 > floor upper CI 0.778, and last_obj_mention (the strongest) fails on TWO distinct structures (lose 0.00, mention-after-transfer 0.00). PRECONDITION: strongest trivial ever-had 0.512 (constant baselines pinned at 0.500 by the balanced base rate). LEARNING: shuffle-transition twin 0.417 (chance-level recovery)."
controls: "MECHANISM: two info-free twins -- order-shuffle 0.546 and bind-shuffle 0.659 -- both LOSE CI-sep; empty register 0.250 = chance LOSES; change-point positive control 100%% flip / 0%% constant. PRECONDITION-READ: register 1.000 vs ever-had 0.512 CI-sep, ever-had fails every unmet-after-transfer case (give 0.00 / lose 0.00 / double-close 0.20); order-shuffle twin loses. LEARNING: shuffle-transition twin at chance (+0.583 CI-sep), abstains on a non-transfer verb (no false learning), learning curve 0.0@2 -> 1.0@>=3 exposures (commit threshold explicit). OPEN TEXT: coverage/precision localization on real text via the substrate's own parser (no gold 'who has X' on MCScript2), residual attributed to coref (81%% pronoun agents) + recipient-PP + verb-sense."
files_changed: "experiments/world_state_register.py (spaCy-free mutable-register CORE + STRIPS operators + precondition-read; operator class now supplied per-rep so it runs off a FrameNet-derived OR learned lexicon); experiments/possession_operators.py (FrameNet-derived operator+role lexicon, 'from what we have'); experiments/exp_world_state_query_v1.py (mechanism); experiments/exp_world_state_precondition_v1.py (precondition-read); experiments/exp_world_state_learn_operators_v1.py (learn-and-adapt tier); experiments/exp_world_state_realtext_mcscript_v1.py (open-text via the substrate's own parser); experiments/exp_world_state_serves_order_mcscript_v1.py (downstream: does it break the aligner's before/after wall -- NO, confirms order is conventional); experiments/exp_world_state_extraction_v1.py (synthetic explicit-vs-implicit decomposition, superseded by the real-text arm but kept); verification/test_world_state_register.py (34/34 witness); data/possession_operators_v1/lexicon.json (offline FrameNet asset); SOLVED.md. NO hdlab/ written (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_world_state_register.py   # 34/34 -- recomputes CORE + mechanism + precondition + FrameNet operators + learning + real-text FROM SOURCE"
---

# The situation model's mutable WORLD-STATE dimension: possession + precondition-read, operators FROM WHAT WE HAVE, LEARNED from reading

## Status in one line
The register MECHANISM and the LEARN-AND-ADAPT tier are **SOLVED with the full control battery**; end-to-end
on **open text** is a **located residual** (coref + recipient-PP + verb-sense precision -- all NAMED existing
organs, not the mechanism). Hence PARTIAL, honestly: everything the register itself must do is proven; what
is not yet demonstrated is unrestricted-natural-prose accuracy, and I show exactly why and what closes it.

## THE DISK OUTRANKS THE BRIEF -- what already existed, and what genuinely did not
- `at(obj,loc)` -> **`hdlab/location_register.py`** and `open/broken` -> **`hdlab/state_register.py`** are
  ALREADY mutable, effect-updated, time-queryable registers (SPACE + ENTITIES(state) dimensions, promoted).
  I did NOT rebuild them.
- The aligner (`exp_operator_partial_order_mcscript_v1`) already prototyped `avail/at/open` STRIPS operators
  -- but ONLY as a static enable-DAG for ORDER, and PROVED that a mutable register is "structurally IDLE"
  for ordering everyday scripts (~99% of before/after pairs are causally independent; order is conventional,
  not causal). **That is why I reframed off ORDER and onto STATE QUERIES / POSSESSION, where mutability IS
  required** -- a transfer A->B->C flips `have()`, so both a static "ever-held" bag and a last-mention floor
  are fooled. The genuinely-missing pieces this problem builds:
  1. **POSSESSION `have(holder,obj)`** -- the one predicate in the brief's list with no register (the
     maximally-mutable one; the predicate Glenberg-Meyer-Lindem 1987 is about).
  2. **A mutable forward-application** (`has(e,obj,t)` = state after events <= t) -- the thing the aligner's
     static DAG omitted.
  3. **A precondition-READ / violation layer** -- every existing register is WRITE+query; none reads state as
     an event precondition to flag a bridging inference.

## THE OWNER'S REDIRECTION, and what changed because of it
The first version hand-coded the transfer-verb lists and drove extraction with a bespoke spaCy parser. On the
owner's instruction -- **use what we have, be brain-foundational and optimized, use the learning module** --
the operator + extraction + learning layers were rebuilt:
- **OPERATORS FROM WHAT WE HAVE (FrameNet).** `experiments/possession_operators.py` derives the verb->operator
  map from FrameNet transfer frames (Giving, Getting, Receiving, Taking, Sending, Delivery, Commerce_*,
  Lending, Supply, Transfer, Removing): **105 verbs across 13 frames**, each carrying its **recipient / donor
  / source ROLE from the frame elements**. This replaces the hand list AND fixes the recipient slot at the
  resource level (the stock `hdlab/mcscript_extraction.extract_args` returns only subject/object -- no
  recipient; FrameNet says a GIVE HAS a Recipient, so the extractor knows to look for it).
- **DRIVEN BY THE SUBSTRATE'S OWN PARSER.** The open-text arm uses `hdlab.candidate_generator`
  (pos_tagger + arc_parser -- the reader's front-end), not spaCy, and fills the FrameNet roles from the real
  dependency parse (recipient = the to/unto-PP head; source = the from-PP head).
- **A LEARNING TIER (learn and adapt).** `experiments/exp_world_state_learn_operators_v1.py`: a transfer verb
  NOT in the FrameNet seed has its operator INDUCED from observed possession transitions -- the register grows
  its own operator knowledge from reading (usage-based construction acquisition; the `consequence_learning_
  loop` template). The supervision is the world state itself: the post-state of the unknown event is revealed
  by the PRECONDITION-READ of a known downstream event ("Ben gave it to Cara" presupposes Ben had it) -- so
  the learning tier reuses this problem's own precondition-read capability.

## THE BRAIN FRAME (which structure; replicate or substitute?)
- **PINNED (copy the COMPUTATION):** the situation model maintains a mutable current state updated by event
  EFFECTS and read by PRECONDITIONS (Zwaan & Radvansky 1998; the STRIPS operator form, Fikes & Nilsson 1971);
  object availability tracks the current relation to the protagonist (Glenberg, Meyer & Lindem 1987 =
  possession); an unmet precondition triggers a bridging inference (Haviland & Clark 1974); possession-transfer
  is a caused-change-of-possession CONSTRUCTION whose semantics is a FrameNet FRAME with Donor/Recipient/Theme
  roles (Fillmore frame semantics; Goldberg 1995; Pinker 1989); verb->event-structure mappings are ACQUIRED
  from experience (usage-based learning, Goldberg 2006 / Tomasello 2003; syntactic bootstrapping, Gleitman).
- **FROM-RESOURCE (the PARAMETER we GET, not invent):** which verbs evoke which transfer frame + each frame's
  role inventory -- read from FrameNet (a static offline asset we already have; admissible foundation).
- **LEARNED (the growth):** operators for OOV verbs, induced from observed transitions (prediction-error /
  consequence learning).
- **OUR-INVENTION-SWEPT:** the FRAME->op mapping table (frame semantics -> STRIPS possession effect), the
  single-holder possession assumption, the discrete-interval representation.

## WHAT WAS MEASURED
1. **MECHANISM (`exp_world_state_query_v1`, n=960).** Register 1.000 vs strongest floor 0.750, +0.250 CI-sep
   [0.224,0.277], null p95 0.026; both info-free twins lose (order 0.546, bind 0.659); empty 0.250; change-
   point 100% flip / 0% constant; the strongest floor fails on two distinct structures (not one-off).
2. **PRECONDITION-READ (`exp_world_state_precondition_v1`, n=1200 balanced).** 1.000 vs ever-had 0.512,
   +0.488 CI-sep; ever-had collapses on every unmet-after-transfer case.
3. **OPERATORS FROM FRAMENET (`possession_operators`).** 105 verbs / 13 frames, recipient role recovered;
   the mechanism holds when driven by these resource-derived operators (the core consumes them via a supplied
   OP class -- witnessed).
4. **LEARN-AND-ADAPT (`exp_world_state_learn_operators_v1`, n=24 held-out verbs).** Recovery of FrameNet gold
   1.000 vs shuffle-twin 0.417 (+0.583 CI-sep); committed 100%; abstains on a non-transfer verb; learning
   curve 0.0@2 -> 1.0@>=3 exposures; register driven by LEARNED operators answers who-has-it as well as the
   FrameNet-seeded one (1.000, delta 0).
5. **OPEN TEXT (`exp_world_state_realtext_mcscript_v1`, 1500 real MCScript2 sentences, substrate's own parser).**
   1467 transfer instances fire (GET 926 / LOSE 313 / GIVE 228) -- possession is DENSE on real narrative, so
   the register is not "idle" for STATE. Role recovery: theme 0.78, agent 0.51, recipient-on-GIVE 0.33 (was 0
   with the stock front-end), source-on-GET 0.11. The dominant end-to-end bottleneck is COREF: 81% of real
   agents are pronouns ("I grabbed...", "the nurse takes me...").
6. **DOWNSTREAM SERVE TEST -- does the register break the aligner's ~0.59 BEFORE/AFTER wall?** (owner-requested;
   `exp_world_state_serves_order_mcscript_v1`, the previous solver's EXACT MCScript2 before/after harness,
   one-variable swap: operator set += FrameNet possession). **NO -- and that is the rigorous result.** Baseline
   vs +possession on n=301 held-out: SIM 0.525, COOCCUR 0.591 (the wall reproduced exactly); possession adds
   enable-edges (54.2 -> 62.0) but decides the SAME ~0.7% of questioned pairs (coverage 0.007, delta 0.0) and
   E2E is unchanged (0.588, delta 0.0, not CI-sep). VERDICT: possession is IDLE FOR ORDER -- it CONFIRMS the
   aligner's deepest finding, now with the ACTUAL register + FrameNet operators (not just the avail/at/open
   prototype): MCScript2 before/after order is CONVENTIONAL (script schema), NOT derivable from possession/
   causal state. The register's value is STATE QUERIES (who-has-what, proven), NOT ordering. This closes the
   "maybe the register unblocks ordering" hypothesis with evidence.

## WHAT I DID NOT ESTABLISH (withdraw-first)
- **End-to-end who-has-what accuracy on unrestricted open text is NOT demonstrated.** There is no gold
  "who has X at time t" annotation for MCScript2, so the open-text arm is an honest COVERAGE/PRECISION
  localization, not an accuracy claim. **First thing I would withdraw:** any implication that the register
  answers unrestricted-natural-prose possession queries at construction-gold accuracy.
- **The open-text residual is LOCATED, not closed:** (a) COREF -- 81% pronoun agents need
  `hdlab/coreference_resolver` (the entity backbone; a standing shared cap); (b) RECIPIENT-PP recovery 0.33
  (many gives lack an explicit to-PP, or it attaches non-locally); (c) VERB-SENSE precision -- "take me to the
  room" mis-fires as a GET (a non-possession sense of "take"); frame-sense disambiguation is the meaning
  channel's job. None is the register mechanism.
- **The learning curve's clean step (0->1 at 3 exposures) reflects NOISELESS synthetic supervision;** on real
  noisy transitions it would be more graded (a bound, not a claim).
- **The FRAME->op mapping table is OUR-INVENTION-swept**, and the FrameNet lexicon, while resource-scale
  (105 verbs), is not exhaustive; the learning tier is exactly what covers the tail.

## KEY REALIZATIONS (the enabling moves)
1. **The aligner's "mutable register is idle for ORDER on everyday scripts" is why the problem is a STATE-
   QUERY problem, not an order one.** Mutability earns its keep only where predicates FLIP; possession-transfer
   is the maximally-mutable predicate, so it is where the mechanism is provable -- and it is dense on real text.
2. **"From what we have" fixed the recipient at the SOURCE, not with a bespoke rule.** FrameNet frames carry
   the Recipient/Donor/Theme roles; once the frame says a GIVE has a recipient, the substrate's OWN parse
   already exposes it (the to-PP head) -- the stock `extract_args` gap was simply that it never looked. Recipient
   recovery went 0 -> 0.33 on real text with no new parser, just the frame role + the existing parse.
3. **The precondition-read IS the learning signal.** The learner induces an unknown verb's operator from the
   possession transition, and the post-state is revealed by a KNOWN downstream event's precondition -- so the
   "read" capability bootstraps the "learn" capability. One mechanism, two payoffs.
4. **Two info-free twins + change-point are the mechanism claim, not the 1.000** -- a recency echo would also
   score high on a weak gold; the proof is that the answer FLIPS at the update and both scrambles collapse.
5. **The real-text arm relocated the wall from "the mechanism / the lexicon" to COREF (81% pronoun agents).**
   Measuring on text I did not write, through the reader's own organs, is what turned a synthetic win into a
   named, buildable open-text residual.

## ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization -> next problems)
- **`coreference_resolver` is THE open-text lever (81% pronoun agents).** Brain-fidelity: coref IS entity
  tracking (bridging). The register's `have()` keys on entities; on real first-person narrative most agents are
  pronouns, so who-has-what is coref-bound. HIGH leverage, existing organ. **Wire the register's entity keys
  through coref** -- the shared cap the SPACE/ENTITIES registers also hit.
- **Verb-SENSE disambiguation (frame selection).** "take a picture / take the leap / take me to the room" are
  non-possession senses of a possession verb. The FrameNet lexicon is sense-blind; the fix is the meaning
  channel selecting the frame in context (the grounded-semantic-graph organ's job). OUR-INVENTION today
  (surface lemma -> frame). **Candidate follow-on: frame-sense selection before operator application.**
- **The LEARNING tier should compose the landed learner organs.** I built a focused consequence-learning-style
  inducer; `hdlab/consequence_learning_loop` (result-valence from the episode's own consequence) and
  `hdlab/result_type_induction` (glass-box episode->class induction) are the landed organs to route this
  through at wiring time. Fidelity: PINNED (usage-based acquisition). **Candidate consolidation.**
- **Stative-possession channel ("X is Y's" / "belongs to" / "had").** Possession stated as a RESULT STATE, not
  a transfer event -- the analogue of what `state_register` does for attributes. Complements the transfer
  operators. **Candidate follow-on.**

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b -- strategy folds in)
New 2b entry: **the situation model gains a mutable WORLD-STATE / cross-event CAUSATION dimension as STRIPS
operators (possession + precondition-read), with operators DERIVED FROM FrameNet and LEARNABLE from exposure.**
Brain structure: Zwaan-Radvansky current-model + Glenberg-Meyer-Lindem object-availability + Fikes-Nilsson
STRIPS + Fillmore frame semantics + usage-based construction acquisition (all PINNED at the computational
level). Fidelity: the mutable forward-apply + effect-write + precondition-read COMPUTATION copied; verb->frame
membership + role inventory FROM FrameNet (resource); OOV operators LEARNED from observed transitions.
Deviations: (a) CI-separated headline on construction gold (isolates tracking); (b) open text via the
substrate's own parser fires densely (1467 transfer instances / 1500 sentences) but end-to-end who-has-what is
COREF-bound (81% pronoun agents) + recipient-PP-bound (0.33) + verb-sense-bound -- a located residual on NAMED
organs, not a mechanism failure. **Reconciles the brief's premise:** `at`/`open` already ARE mutable registers;
the new dimension is POSSESSION + the PRECONDITION-READ, and it is now resource-grounded and learnable.
**Corrects/confirms the aligner's world-state note WITH EVIDENCE:** running the previous solver's exact
before/after harness with the ACTUAL register + FrameNet possession operators, the ~0.59 wall HOLDS (E2E 0.588,
delta 0.0 vs baseline; possession decides the same ~0.7% of pairs) -- so a mutable register is IDLE FOR ORDER
(MCScript2 order is conventional/script-schema), but it is REQUIRED and DENSE for STATE QUERIES (1467 possession
transitions in 1500 real sentences). The register is a STATE organ, not an ORDER organ -- measured, not asserted.

## FOR STRATEGY (you land hdlab; Q111 -- I do not write hdlab/)
1. Promote the spaCy-free CORE `experiments/world_state_register.py` -> `hdlab/world_state_register.py`
   (sibling of location/state register): `has`/`holder_of`/`is_open`/`unmet_preconditions`, consuming abstract
   events with an OP class. Keep the FrameNet operator lexicon (`possession_operators`) as an offline asset and
   the parser-role extraction experiment-side (the SPACE/ENTITIES split).
2. Wire a default-off `track_world_state` reader flag binding `sm.has(entity,obj,t)` / `sm.holder_of(obj,t)`,
   driven by the substrate's own parser + FrameNet roles, **routed through `coreference_resolver`** for the
   entity key (the located open-text lever). Byte-identical when off.
3. The LEARNING tier and the stative-possession channel are the two follow-ons; verb-sense/frame selection is
   the meaning-channel dependency.

## GAINS TO BE MADE AND HOW (post-investigation, owner-directed; deflated, with the parser caveat made explicit)
This problem's register is done; the owner then directed a brain-mechanism-method sweep of the adjacent
compounding levers. Every mechanism candidate was BUILT and MEASURED. The honest map of what gain is available
and exactly how to realize it (all files + reproduce commands are in
`notes/problems/situation_model_has_no_mutable_world_state_register/DISSECTION_before_after_order_wall.md`):

| lever | status (measured) | gain (deflated) | HOW (brain-faithful) | risk / caveat |
|---|---|---|---|---|
| **World-state/possession register** | BUILT, proven, witnessed 36/36 | a NEW capability the reader lacked: answers who-has-what at story-time + flags impossible (precondition-violated) actions | promote the spaCy-free core; wire a default-off `track_world_state` flag ROUTED THROUGH `coreference_resolver` | on real prose it is **coref-bound** -- 81% of agents are pronouns; the register itself is not the gap |
| **Spreading-activation MEANING channel** | mechanism VALIDATED: PPR walk beats the info-free shuffled-graph twin +0.099 CI-sep on per-context WiC | per-context sense selection the live reader lacks (its meaning read-out is flat/co-occurrence) | land the grounded-semantic-graph organ; wire as a live meaning read-out (paradigmatic WordNet+ConceptNet graph) | **the +0.099 is CLEAN-INPUT (gold lemma/POS, no parser). The LIVE gain is PARSER-BOUNDED** -- the reader must supply the target lemma+POS from its own parser/POS-tagger. Measure the wiring gain THROUGH the live extractor, never on gold WiC. |
| **Syntagmatic axis (SyntagNet 88k)** | TESTED, REJECTED: naive +0.000 WiC; up-weighted x8 = -0.011 WiC (drowns the paradigmatic signal) | ~0 / negative | -- | do NOT invest; the paradigmatic graph is already the walk's optimum. Located negative. |
| **Before/after ORDERING** | CLOSED by diagnosis: all 3 brain mechanisms replicated (DG/CA3 identity, partial-order abstain, SLIMM script/episode precedence) | ~0 aggregate (task/data-capped: ~half the pairs are genuinely order-free); **~0.67 on the answerable ~1/4** via the partial-order abstain readout | ship the partial-order + ABSTAIN readout (answer the reliably-ordered pairs, decline the rest) | none -- diagnosed shut; do NOT chase (a domain-matched everyday-script corpus was the only remaining lever, and it is a resource decision, not mechanism) |
| **Parser / extraction front-end** | known cap; surfaced by the parser question | **highest-COMPOUNDING** -- it gates the *live* payoff of BOTH validated mechanisms above (roles for the register; lemma/POS for the meaning channel) | the existing parse-fidelity / extraction-front-end work | this is *why* both live gains are bounded; it is the shared upstream lever |

**The through-line (the single most important sentence for the reader of this submission):** both validated
mechanisms (register + spreading-activation meaning) prove out on clean/gold input and each realizes its LIVE
gain only as far as the parser supplies correct roles / lemma+POS -- so the most compounding investment for
more *effective live comprehension* is the extraction front-end; everything else here is validated and waiting
on it. Ordering is closed; the syntagmatic axis is a located negative; do not spend effort on either.

## TLDR
As you read, you track who currently has what and update it every time something changes hands. Our reader
already did this for WHERE things are and whether they're open, but not for WHO HAS WHAT, and it had no way to
notice an action that shouldn't be possible. I built that: a running possession record that moves an object
from giver to receiver, answers "who has the cup now?" at any point, and flags impossible actions -- right 100%
of the time versus 75% for the best shortcut, with scrambled and empty versions failing and the answer flipping
exactly when the object changes hands. Then, on your steer, I rebuilt it to use what we already have instead of
a hand-made list: the rules for which verbs move possession now come from FrameNet (105 verbs, and it tells us
which word is the receiver -- the piece the reader's front-end was missing), and I added a learning step so the
reader can figure out a NEW handover verb just by watching what happens to the object (it recovers the correct
rule 100% of the time, a scrambled version fails, and it refuses to over-learn a verb that moves nothing).
Finally I ran it on 1,500 sentences of REAL everyday stories through the reader's OWN grammar engine: handovers
are everywhere (1,467 of them), the receiver is now recoverable, and the one real bottleneck is that in real
stories 4 out of 5 doers are pronouns ("I", "he") -- so finishing the job on open text needs the reader's
existing pronoun-resolver wired in, not any change to the tracker itself. So: the tracker and the learning work
and are built from what we have; the remaining open-text gap is a specific, named, existing organ.

## QUESTIONS
None.

## NEXT STEPS
1. Strategy: promote the core + wire a default-off `track_world_state` flag routed through `coreference_resolver`.
2. Wire the register's entity key through coref (the located 81%-pronoun open-text lever) and re-measure who-has-what on real text.
3. Frame-SENSE selection before operator application (kills the "take me to the room" false positive) -- the meaning-channel dependency.
4. Consolidate the learning tier onto `consequence_learning_loop` / `result_type_induction`; add a stative-possession channel ("belongs to" / "had").

## INTEGRATED_BY_STRATEGY — 2026-09-01 (grade: EXCELLENT; SOLVED owner-DONE)
Reverified **36/36 first-hand** (`verification/test_world_state_register.py` -- recomputes CORE + mechanism +
precondition + FrameNet operators + learning + open-text FROM SOURCE). A rigorous, brain-foundational positive
with an honestly-located open-text residual (PARTIAL, but a full PASS as a located result). Register 1.000 vs the
strongest stateless floor last_obj_mention 0.750 (+0.250 CI-sep); all three info-free twins LOSE; change-point
100%/0%; precondition-read 1.000 vs ever-had 0.512; FrameNet 105-verb operator lexicon WITH the recipient role;
learn-and-adapt recovers gold 1.000 vs shuffle 0.417 + abstains on non-transfer; open text 1467 transfers with the
residual precisely located to coref (81% pronoun agents) -- a NAMED existing organ, not the mechanism; the
downstream serve-test honestly confirms the register does NOT break the ~0.59 order wall (order is conventional --
the register is correctly a STATE organ, not an order organ). Reuses the existing location/state registers.

**WIRE LANDED (Q111, WIRING_MAP):** promoted `experiments/world_state_register.py` -> **`hdlab/world_state_register.py`**
and `experiments/possession_operators.py` -> **`hdlab/possession_operators.py`** VERBATIM (byte-for-byte behavior;
the FrameNet lexicon loads from the cached `data/possession_operators_v1/lexicon.json` -- no nltk at inference). Added
a **default-off `track_world_state` flag** on `SituationReader`: when on, `read()` (running LAST over the FINAL event
set) folds the reader's OWN extracted events into `sm.world_state` = a `hdlab.world_state_register.WorldState`
(PRED/AGENT/PATIENT from the reader's extraction, ARG2 recipient/source from `wired_extra_roles`, operator class from
the FrameNet lexicon) exposing `has(entity,obj,t)` / `holder_of(obj,t)` / `is_open(obj,t)` / `unmet_preconditions()`.
Default OFF = byte-identical (`sm.world_state` None; nothing imported). **Witness `test_world_state_register_landing_organ.py`**:
[1] default-off byte-identical (219 events / 136 entities on 1023_bleak_house), [2] flag-on register == an independent
recompute through BOTH the hdlab core AND the experiments core BYTE-EXACT (proves the promotion is faithful + the wire
builds the register from the right reps), [3] the promoted core's transfer/toggle/precondition mechanism, [4] the wire
builds the correct mutable possession on a known transfer (anna GETs then GIVEs to ben; recipient consumed). Registered
`world_state_dimension_live_reader_v1`. **HONEST BOUND:** the wire lands the CAPABILITY (mechanism-proven, byte-faithful);
LIVE who-has-what on real prose is COREF/parser-recall-bound (the register faithfully folds whatever the reader extracts,
so 19c extraction noise flows through -- the located residual, the register-through-coref re-measure is the follow-on).
`priority:` cleared; review (EXCELLENT) + this block written into PROBLEM.md; AUDIT §2b folded.
