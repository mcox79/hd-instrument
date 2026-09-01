---
problem: situation_model_has_no_mutable_world_state_register
status: SOLVED
bar: "PASS = the mutable world-state register, driven by the reader's OWN extraction, answers STATE queries (is obj X open / does agent have Y / where is Z, at story-time t) CI-SEPARATED over the strongest no-state-tracking floor actually run -- (a) LAST-MENTION / static and (b) a no-model surface baseline -- on a population with state-CHANGING events, with the info-free TWIN (shuffle which event's effect updates which predicate, or a random-effect twin) LOSING CI-separated, AND a positive control that the register's answer CHANGES at the updating event (not a constant). A rigorous NEGATIVE is a full PASS if located: name precisely whether the wall is the register MECHANISM or extraction RECALL of implicit preconditions/effects."
result: "MECHANISM (construction gold, isolates tracking; n=960 state queries over possession-transfer + open/close re-toggle, current holder/state DECORRELATED from every stateless cue): world-state register 1.000 [1.000,1.000] vs the strongest no-state-tracking floor last_obj_mention 0.750 [0.722,0.778] -- CI-separated, delta +0.250 [0.224,0.277], null p95 0.029. PRECONDITION-READ (n=1200, balanced 50/50): register detects precondition VIOLATIONS 1.000 vs the strongest trivial baseline (ever-had) 0.512 [0.484,0.539], +0.488 [0.461,0.518] (F1 on unmet 1.000 vs 0.117). EXTRACTION end-to-end (n=300 modern prose, glass-box spaCy transfer adapter): gold-effects ceiling 1.000; EXPLICIT lexicalized transfers recover near-ceiling 0.989 (component recall verb 1.00 / agent 1.00 / object 1.00 / RECIPIENT 0.987); IMPLICIT stative transfers 0.000 -- the LOCATED residual."
floor: "Strongest of four no-state-tracking floors recomputed on the SAME n=960 population: last_obj_mention 0.750 [0.722,0.778] (hi 0.778); recency_subject 0.250; ever_entity 0.250; first_holder 0.125. Register lower CI 1.000 > floor upper CI 0.778. No single stateless floor handles all query types: last_obj_mention (the strongest) FAILS on TWO distinct structures -- possession-lose (0.00) and mention-after-transfer (0.00) -- so the win is broad, not one-structure. Precondition floor: strongest trivial ever_had 0.512 (constant baselines pinned at 0.500 by the balanced base rate)."
controls: "(1) INFO-FREE TWIN order-shuffle 0.546 LOSES CI-sep (delta +0.454; destroys the transfer SEQUENCE). (2) INFO-FREE TWIN bind-shuffle 0.659 LOSES CI-sep (delta +0.341; destroys who-gets-what). (3) EMPTY register 0.250 = chance-level LOSES CI-sep (delta +0.750; not gameable by emptiness). (4) CHANGE-POINT positive control: 100%% of has-items FLIP across the updating event, 0%% constant -> tracks STATE, not recency. (5) PRECONDITION-VIOLATION READ control: register detects unmet preconditions 1.000 vs ever-had 0.512 CI-sep; ever-had FAILS every unmet-after-transfer case (give 0.00, lose 0.00, double-close 0.20) -> the register is READ, not just written. (6) EXTRACTION decomposition: gold ceiling 1.000 ISOLATES the mechanism from extraction; explicit-vs-implicit condition split + per-component recall LOCATE the residual as implicit-effect extraction (coref cost ~0, recipient 0.987 -- neither is the wall)."
files_changed: "experiments/world_state_register.py (spaCy-free mutable-register CORE + STRIPS operators + precondition-read); experiments/exp_world_state_query_v1.py (mechanism); experiments/exp_world_state_precondition_v1.py (precondition-read control); experiments/exp_world_state_extraction_v1.py (extraction residual, lazy-spaCy transfer adapter); verification/test_world_state_register.py (22/22 witness); notes/problems/situation_model_has_no_mutable_world_state_register/SOLVED.md. NO hdlab/ written (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_world_state_register.py   # 22/22 -- recomputes every headline FROM SOURCE (core self-test + mechanism CI-sep + precondition-read + extraction residual)"
---

# The situation model gets its mutable WORLD-STATE dimension: possession + a precondition-read, as STRIPS operators

## THE DISK OUTRANKS THE BRIEF -- what was already built, and what genuinely was not
The brief frames this as building "a mutable world-state register" as if the situation model had none. **Two
of the brief's own three example predicates already exist as mutable, effect-updated, time-queryable
registers, and I did NOT rebuild them:**
- `at(obj,loc)` -> **`hdlab/location_register.py`** (SPACE dimension, promoted+wired): `apply_motion(effect)`
  -> `where_is(entity, t)` (query) IS a mutable STRIPS-style register for location.
- `open/broken` -> **`hdlab/state_register.py`** (ENTITIES(state) dimension, promoted+wired, owner-DONE
  `the_situation_model_tracks_no_entity_state_history`): its `RESULT` aspect files the resultant state of a
  telic event ("the door opened" -> open), read at time t.
- The aligner (`exp_operator_partial_order_mcscript_v1`) ALREADY prototyped `avail/at/open` STRIPS operators
  -- but ONLY as a static enable-DAG for ORDER, with an explicit note: *"NO forward simulation of a mutable
  state ... on short scripts re-toggles/consumed-resources are RARE."*

So the brief's premise is PARTLY already met. The genuinely-missing pieces -- and what this problem builds --
are exactly the three the disk did NOT have:
1. **POSSESSION `have(holder,obj)`** -- the ONE predicate in the brief's list (have/at/open) with no register,
   and the MAXIMALLY-MUTABLE one (a transfer A->B->C flips `have()` true<->false), where both a static
   "ever-held" bag and a last-mention floor are fooled. This is the predicate the brief's pinned Glenberg,
   Meyer & Lindem (1987) citation is literally about (object availability = current relation to the
   protagonist).
2. **A MUTABLE FORWARD-APPLICATION over story-time** -- `has(e,obj,t)` = the state AFTER events <= t -- the
   thing the aligner's static DAG deliberately omitted. This is what makes the register TRACK state, not
   echo recency.
3. **A PRECONDITION-READ / violation layer** -- every existing register is WRITE + query; NONE reads the
   current state as an event's PRECONDITION. An event whose precondition is unmet flags a bridging-inference
   demand. This is what makes it a world MODEL, not a log.

## THE BRAIN FRAME (the opening move: which structure, replicate or substitute?)
**PINNED -- copied operation-for-operation:**
- The situation model maintains a MUTABLE CURRENT STATE, updated incrementally by event EFFECTS and read by
  event PRECONDITIONS (Zwaan & Radvansky 1998 event-indexing; van Dijk & Kintsch 1983 situation model).
- An object's representational availability tracks its CURRENT relation to the protagonist, NOT its last
  mention (Glenberg, Meyer & Lindem 1987 -- "put on / took off the sweatshirt" changes the object's
  accessibility): this IS the possession/association relation.
- An event has PRECONDITIONS (state required) and EFFECTS (state changed); the STRIPS/operator form (Fikes &
  Nilsson 1971) is the computational-level description of the forward model; an unmet precondition triggers a
  bridging inference (Haviland & Clark 1974).

**OUR-INVENTION-UNDER-TEST (swept, labelled, NOT adopted):** the verb->operator lexicon (GIVE/GET/LOSE/TOGGLE
classes -- seeded conceptually from VerbNet caused-possession classes give-13.1 / get-13.5.1 / send-11.1 /
obtain-13.5.2; a full VerbNet-derived asset is the foundation upgrade), the single-holder possession
assumption, the discrete-interval representation (reuses the `location_register` interval shape).

## WHAT WAS BUILT
- **`experiments/world_state_register.py`** -- a spaCy-FREE tracking CORE (consumes abstract events, exactly
  as the location/state register cores do, so the mechanism is isolable from extraction). `WorldState` holds
  per-object single-valued interval tracks for `have(holder)` and `state(open/closed)`; `apply_event(rep,t)`
  applies STRIPS effects (GIVE: giver loses + recipient gains; GET: agent gains; LOSE: holder cleared;
  TOGGLE_ON/OFF: state set); `_read_preconditions` reads the current state as the event's precondition
  (USE needs `have`; close needs `open`; give needs `have`). Queries: `has(e,obj,t)`, `holder_of(obj,t)`,
  `is_open(obj,t)`, `unmet_preconditions()`.
- **Three experiments + a 22/22 scaffold-free witness**, mirroring the entity-state register's playbook
  (construction gold isolates TRACKING; a lazy-spaCy adapter bounds EXTRACTION).

## WHAT WAS MEASURED
1. **MECHANISM (`exp_world_state_query_v1`, n=960).** Construction gold decorrelates the current holder/state
   from last-mention, ever-association and first-mention; each query type defeats a DIFFERENT stateless floor
   (transfer-away / current-holder-after-chain / recency-trap / lose / mention-after-transfer / has-positive /
   open-close re-toggle / stay-open). **Register 1.000 vs the strongest floor last_obj_mention 0.750,
   +0.250 CI-sep [0.224,0.277], null p95 0.029.** No single floor handles all types (last_obj_mention, the
   strongest, fails on lose AND mention-after-transfer). Both info-free twins LOSE (order-shuffle 0.546,
   bind-shuffle 0.659); the empty register is at chance (0.250); the CHANGE-POINT control fires (100% of
   has-items flip at the updating event, 0% constant).
2. **PRECONDITION-READ (`exp_world_state_precondition_v1`, n=1200, balanced 50/50).** The register detects
   precondition VIOLATIONS 1.000 vs the strongest trivial baseline (ever-had) 0.512, +0.488 CI-sep
   (F1-unmet 1.000 vs 0.117). Ever-had gets the MET cases but collapses on every unmet-after-transfer case
   (give 0.00, lose 0.00, double-close 0.20) -- it cannot tell that possession/openness MOVED AWAY since the
   object was introduced. The order-shuffle twin loses (0.643).
3. **EXTRACTION end-to-end (`exp_world_state_extraction_v1`, n=300 modern prose).** Gold-effects ceiling
   1.000 (mechanism, re-confirmed). EXPLICIT lexicalized transfers recover near-ceiling **0.989**, with
   per-component recall verb 1.00 / agent 1.00 / object 1.00 / **RECIPIENT 0.987** -- the a-priori-hardest
   piece (the dative / to-PP recipient, which the live reader has no clean field for) is recovered by the
   glass-box adapter on clean modern prose, and coref cost is ~0. **IMPLICIT stative transfers ("the book was
   Cara's" / "belonged to" / "had") = 0.000** -- a transfer-operator extractor structurally cannot fire when
   the effect is not a transfer EVENT. This LOCATES the residual precisely: the wall is extraction RECALL of
   IMPLICIT (stative, non-event) effects, NOT the register mechanism and NOT the recipient or coref.

## WHAT I DID NOT ESTABLISH (withdraw-first if wrong)
- **The CI-separated headline is on CONSTRUCTION gold** (real English possession/toggle constructions, but
  by-construction labels), NOT fully-natural raw-prose queries -- for the same reason the location/state
  registers used construction gold (on unrestricted prose the extraction wall would dominate the tracking
  signal, and an auto-mined natural gold would be as noisy as the mechanism). The real-prose burden is carried
  by the extraction arm's decomposition. **First thing I would withdraw:** any implied claim that the register
  answers UNRESTRICTED natural-narrative possession queries at construction-gold accuracy -- it tracks at that
  accuracy given clean transfer events; raw-prose is bounded by implicit-effect extraction.
- **A stricter reading of the bar ("driven by the reader's OWN extraction ... CI-separated") is met on the
  EXPLICIT slice (0.989) but NOT the IMPLICIT slice (0.000).** I mark SOLVED because (a) the register MECHANISM
  -- the thing the problem asks to build -- is proven with the full control battery, (b) the novel
  precondition-read works, (c) extraction-driven state tracking holds where transfers are lexicalized, and
  (d) the residual is precisely LOCATED as implicit-effect extraction (which the bar explicitly blesses as a
  full PASS) and is an adjacent-component cap, not a mechanism failure. A reader who weights the implicit slice
  more heavily could fairly call this PARTIAL; the disagreement is about labelling, not about any number.
- **The verb->operator lexicon is OUR-INVENTION-swept, not a validated VerbNet asset.** Recall on explicit
  prose is near-ceiling on my population but the lexicon is not exhaustive; a full VerbNet caused-possession
  asset is the foundation upgrade (below).
- **The BONUS (order-from-cause) is deliberately NOT claimed.** The aligner already LOCATED that as a negative
  (in-text enablement 0.568 <= 0.591 co-occurrence; ~99% of MCScript pairs are causally independent -> order
  is a canonical-script-schema problem, its own filed problem `learn_canonical_script_order_from_a_causal_
  enablement_foundation`), and temporal-order comprehension is separately CLAIMED by `solver_opus48_temporal`.
  I did not compete on it. The precondition->effect join is available as a mechanism that problem could consume.

## KEY REALIZATIONS (the enabling moves)
1. **The disk already had a mutable register for `at` and `open` -- so the real gap was POSSESSION + the
   PRECONDITION-READ, not "a world-state register" writ large.** Reading `location_register`/`state_register`
   and the aligner's operator prototype BEFORE building turned a vague "build the whole thing" into a bounded,
   genuinely-missing three-piece contribution. (The brief's MEASURED section undersells this; the disk
   outranks the brief.)
2. **Mutability only earns its keep where predicates FLIP -- so possession is the RIGHT headline.** The
   aligner's own note ("re-toggles/transfers are rare on short scripts, so a static DAG is not measurably
   improved by a mutable rollout") is the key: a mutable register beats a static/last-mention floor exactly in
   proportion to transfer/re-toggle density. Possession-transfer is the maximally-mutable predicate, so it is
   where the mechanism's value is provable. I built the population to MAXIMIZE flips, which is why the twins
   and the empty register collapse.
3. **The change-point control is the mechanism claim, not the 1.000.** A register that echoed recency could
   also score high on a badly-built gold; the proof that it TRACKS is that `has(A,obj)` flips true->false at
   the exact give event (100% flip, 0% constant), and that both info-free twins (which preserve per-event
   bookkeeping but scramble the sequence / the bindings) lose.
4. **The precondition-READ is the layer that turns a log into a model, and ever-had is the floor that proves
   it.** An "ever-had" baseline detects a violation only if the agent NEVER had the object -- so it is blind to
   the interesting case (possession moved away since). Building that specific floor is what makes the READ a
   measurable capability rather than a decoration.
5. **Isolating the mechanism (gold effects) from extraction (prose) is what let me LOCATE the residual
   honestly.** The same gold ceiling (1.000) under both arms proves the drop is extraction; the explicit-vs-
   implicit split proves the extraction wall is IMPLICIT STATIVE transfers, not the recipient (0.987) and not
   coref (~0). A single end-to-end number would have hidden all of this.

## ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization -> candidate follow-ons)
- **A STATIVE-POSSESSION channel is the located residual and the clear next build.** "The book was Cara's" /
  "belonged to" / "X had Y" convey possession as a RESULT STATE, not a transfer EVENT -- the exact analogue of
  what the entity-state register does for attributes (copular/perfect). Fidelity: this is a real linguistic
  channel the transfer-operator reader is blind to. Optimization: a copular/possessive-`have` extraction
  channel feeding `have()` would close most of the implicit residual. **Candidate follow-on.**
- **The verb->operator lexicon (GIVE/GET/LOSE/TOGGLE, OUR-INVENTION) should become a VerbNet caused-possession
  asset.** `data/verbnet_cache` is on disk; give-13.1 / get-13.5.1 / obtain-13.5.2 / send-11.1 supply the
  transfer classes + their argument structure (the recipient/source slot) as a static offline FOUNDATION
  (admissible; glass-box at inference). Fidelity: PARTIAL (curated). **Candidate follow-on / foundation
  upgrade.**
- **Coref supplies the entity/object key.** I resolved pronouns with a lightweight recency+gender heuristic
  (cost ~0 on my population) and held the object key fixed at query time; on real multi-entity same-gender
  prose the live `coreference_resolver` (~0.65) would cap possession binding, exactly as it caps the SPACE and
  ENTITIES registers. Already a standing cap -- not a new problem.
- **The precondition->effect join is the mechanism the ORDER problem needs, but order is NOT this problem.**
  The aligner located order-from-cause as a negative (~99% causally-independent pairs) and it is separately
  filed/claimed. The register exposes `unmet_preconditions()` and the effect/precondition literals that
  `learn_canonical_script_order_from_a_causal_enablement_foundation` / `solver_opus48_temporal` could consume.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b -- strategy folds in)
Recommended new 2b entry: **The situation model now has a mutable WORLD-STATE / CAUSATION dimension as STRIPS
operators (possession + precondition-read).** Brain structure: Zwaan & Radvansky event-indexing "current
model" + Glenberg-Meyer-Lindem 1987 object-availability-tracks-current-relation + Fikes & Nilsson STRIPS
operator form + Haviland & Clark bridging on an unmet precondition (all PINNED at the computational level).
Our fidelity: the mutable-forward-application + effect-write + precondition-read COMPUTATION copied (PINNED);
the verb->operator lexicon + single-holder possession + discrete intervals are OUR-INVENTION-swept.
Deviations to record: (a) the CI-separated headline is on construction gold (isolates tracking); (b) extraction
is near-ceiling on EXPLICIT lexicalized transfers (incl. recipient 0.987) but ~0 on IMPLICIT STATIVE transfers
-- the located residual, a stative-possession-channel gap, NOT a mechanism failure; (c) order-from-cause is
deliberately excluded (aligner-located negative; separate problem). **Reconciles the brief's premise: `at`
(location_register) and `open` (state_register RESULT) already ARE mutable registers -- the new dimension is
POSSESSION + the PRECONDITION-READ layer, which nothing on the live path had.**

## FOR STRATEGY (you land hdlab; Q111 -- I do not write hdlab/)
1. **Promote the spaCy-free CORE `experiments/world_state_register.py` -> `hdlab/world_state_register.py`** as a
   first-class organ, sibling of `location_register`/`state_register`: `WorldState` with `has`/`holder_of`/
   `is_open`/`unmet_preconditions`, consuming abstract events. Keep the lazy-spaCy transfer extraction adapter
   (`exp_world_state_extraction_v1.extract`) on the experiments side (it needs the parser), exactly as the
   SPACE/ENTITIES splits kept their readers experiment-side.
2. **Wire a default-off `track_world_state` flag on `SituationReader`** binding `sm.world_state` +
   `sm.has(entity,obj,t)` / `sm.holder_of(obj,t)` query callables driven by the reader's own transfer
   extraction. Byte-identical when off (the belief/space wiring pattern).
3. **Do the stative-possession channel FIRST if you want the flag to earn its keep on real prose** -- the
   located residual says the transfer-operator extractor alone is 0 on stative possession.
4. Do NOT chase order-from-cause here (aligner-located negative; separate problem). Do NOT rebuild
   location_register / state_register / coref.

## TLDR
As you read a story you keep a running picture of who currently has what and what is open or shut, and you
update it with every action. Our reader already keeps such a picture for WHERE things are and for whether a
thing is open or broken -- but it had nothing for WHO HAS WHAT, and nothing that CHECKS the picture before
letting an action happen. I built that missing piece: a running record of possession that moves the object
from giver to receiver on every "gave"/"handed"/"took"/"dropped", can be asked "who has the cup now?" or "does
Anna still have the key?" at any point, and flags an action that shouldn't be possible ("she unlocked it with
the key" after she gave the key away). On a controlled test it is right 100% of the time versus 75% for the
best guess that ignores transfers; two scrambled versions and an empty version both fail (so the skill is the
tracking, not the test); and its answer flips at exactly the moment the object changes hands (so it tracks
state, not who was mentioned last). The violation-checker is right 100% versus a coin flip for a method that
only remembers whether someone ever held the thing. When I drove the whole thing from the actual sentences,
it worked almost perfectly when the handover is stated as an action -- including correctly picking up who the
object went TO -- and failed completely when the handover is only implied ("the book was now Cara's"), which
is the one honest gap and points straight at the next build: teach it to read possession stated as a fact, not
just as an action. Two of the brief's three example facts (where things are, whether they're open) already had
running records on disk, so I did not rebuild them and said so.

## QUESTIONS
None.

## NEXT STEPS
1. Strategy: re-verify (`verification/test_world_state_register.py`, 22/22) and, if landing, promote the
   spaCy-free CORE to `hdlab/world_state_register.py` + a default-off `track_world_state` reader flag.
2. Follow-on problem: a **stative-possession channel** ("X is Y's" / "belongs to" / "X had Y") feeding the
   possession register -- the located residual; closes most of the implicit-transfer gap.
3. Follow-on / foundation upgrade: a **VerbNet caused-possession asset** (give-13.1 / get-13.5.1 / obtain /
   send) replacing the OUR-INVENTION verb->operator lexicon (`data/verbnet_cache` is on disk).
4. Hand the effect/precondition literals + `unmet_preconditions()` to the ORDER line
   (`learn_canonical_script_order_from_a_causal_enablement_foundation` / `solver_opus48_temporal`) -- a
   mechanism they can consume; NOT re-derived here (aligner-located negative).
