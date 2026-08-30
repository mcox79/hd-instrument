---
problem: the_situation_model_tracks_no_entity_state_history
status: SOLVED
bar: "Answers entity-STATE queries on real prose CI-separated over a no-state-history floor -- a real-narrative population of state-decisive queries ('what state had X been in?' / 'is X in state S here?'); the floor = the reader WITHOUT the register (nearest-mention / most-recent-adjective guess) recomputed on the same population. The info-free twin (shuffled state->entity or state->interval bindings) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. A POSITIVE control the metric can move (a state-decisive case the register gets and the floor cannot). ... A rigorous NEGATIVE is a FULL PASS (e.g. 'a faithful state register recovers X% of state-decisive queries where the state IS extracted, but real-prose extraction coverage is Y%, so the population lift is Z -- a measured coverage bound, with the positive control confirming the mechanism')."
result: "Construction gold (isolates TRACKING; real English state constructions, 4 discriminating structures, n=420 queries over 180 items): STATE REGISTER 1.000 [1.000,1.000] vs the strongest stateless floor nearest-entity-recency 0.719 [0.676,0.762] -- CI-separated. Empty register 0.429 (chance). Real-PROSE (25 LitBank docs, gold-coref entity key held fixed): extraction coverage 0.374 (489/1309 spaCy-reference predications bound to a gold cluster); the previously-DROPPED 'had been X' prior-state channel now extracted+bound (n=33, hand precision ~0.65); entity-state queries are unsolvable by an entity-blind floor (0.492) or the entity-shuffle twin (0.456), both at chance -> the task needs entity-bound state history."
floor: "STRONGEST of 4 stateless floors recomputed on the same construction population: nearest-entity-recency 0.719 [0.676,0.762] (hi 0.762); ever-entity 0.753; recency 0.503; ever-any 0.503. Register lower CI 1.000 > floor upper CI 0.762. No single stateless floor handles all three mechanisms (BIND/RESULT/SUPERSEDE): ever-entity uses the gold entity key yet fails SUPERSEDE (0.258) and RESULT (0.000); recency fails BIND. Real-prose floor: entity-blind recency 0.492."
controls: "(1) INFO-FREE ENTITY-SHUFFLE TWIN 0.762 [0.719,0.802] LOSES CI-sep (null p95 0.048) -- destroys state->entity binding. (2) INFO-FREE ORDER-SHUFFLE TWIN 0.843 [0.807,0.879] LOSES CI-sep (null p95 0.038) -- destroys the interval order (supersession/persistence). (3) EMPTY register 0.429 = chance, NOT perfect -> the rank/decision metric is not gameable by emptiness. (4) DISTANCE-ROBUSTNESS: register flat 1.000 at K=0,2,5,10,20 filler clauses while a windowed floor collapses 1.000->0.000 at K>=2 -> state is a MAINTAINED property, not a local read. (5) PER-STRUCTURE positive controls: each floor fails >=1 structure the register gets (RESULT 1.000 vs all floors 0.000; SUPERSEDE 1.000 vs ever-entity 0.258). (6) COREF HELD FIXED (gold clusters, bar #3) in the real-prose eval + a gold-coref stateless floor -> the isolated lift is the state-history logic, not coref. (7) Real-prose ENTITY-SHUFFLE TWIN 0.456 LOSES. (8) SUPERSEDE incidence in the bound real-prose population = 0 (honest bound: the closure channel, proven on construction gold, has ~0 natural incidence here)."
files_changed: "experiments/state_register.py (tracking core + extraction adapter); experiments/exp_state_register_query_v1.py (construction-gold CI-sep eval); experiments/exp_state_register_real_prose_v1.py (real-LitBank coverage + query + incidence); verification/test_state_register.py (35/35 witness); notes/problems/the_situation_model_tracks_no_entity_state_history/SOLVED.md. NO hdlab/ written (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_state_register.py   # 35/35 ; then .venv/Scripts/python.exe experiments/exp_state_register_query_v1.py   # HARD_PASS, register 1.000 vs floor 0.719, twins lose, empty 0.429"
---

# The situation model now has a per-entity STATE-HISTORY dimension (Zwaan-Radvansky ENTITIES)

## What was built
A first-class **per-entity state-history register**, sibling of the SPACE `location_register`: the same
per-entity interval bookkeeping, a different attribute (what an entity IS / has-been, not where it is).

- **`experiments/state_register.py`** -- two layers, cleanly separated (as the SPACE organ split
  hdlab-core from experiments-adapter):
  - **`StateRegister`** (spaCy-FREE tracking CORE): per entity a list of `StateSpan(value, polarity,
    aspect, t_open, t_close)` plus a permanent `OccurrenceFact` log. `is_in_state(e, v, t)` /
    `state_at(e, t)` / `had_been(e, t)` / `occurrences_of(e, t)`. Folds abstract state events; reuses the
    `location_register` interval shape, generalised to MULTIPLE concurrent spans per entity (states are
    not mutually exclusive) + the telic two-field split.
  - **`StateReader`** (extraction ADAPTER, lazy spaCy -- the OUR-INVENTION front-end): prose -> abstract
    state events via a dependency parse. Copular / perfect / archaic BE-perfect / resultant-of-telic, with
    glass-box wall-guards.

## The brain frame (PINNED vs OUR-INVENTION), and the research that corrected the design
Opening move was a literature drill (`research` dispatch, 2026-08-29) on how the brain files a state to an
entity via aspect. **Its detailed note did NOT persist to disk (I searched notes/ + scratch/ by name and by
distinctive content -- absent; disk-outranks-claim), so I re-grounded the citations from the returned
headline + my own knowledge.** The headline changed the design in one load-bearing way:

- **PINNED (copied exactly):**
  - Perfect/stative ASPECT binds a STATE to an ENTITY over an interval and routes to the ENTITY/state layer,
    distinct from the event-ORDER layer (**Ferretti, Kutas & McRae 2007** -- perfect "had shattered" primes
    the resultant/entity state; imperfective keeps the ongoing event). Zwaan & Radvansky 1998 ENTITIES.
  - States **DEFAULT-PERSIST** until contradicted (temporal inertia -- Dowty 1986).
  - **The perfect's currency is a CANCELLABLE pragmatic default, NOT an entailment** (Iatridou et al. on the
    perfect; Moens & Steedman 1988 "consequent state"). "He had been a soldier" does NOT entail he is no
    longer one. **My initial instinct -- file a pluperfect as a PRIOR/CLOSED interval -- would OVERCLAIM.**
    The register instead files "had been X" as PRIOR and **default-open-through-the-reference-time**,
    closable only by an explicit cancellation cue. This is the single most important correction.
  - A telic change-of-state event carries **TWO fields** (neo-Davidsonian; Parsons 1990; Kratzer 2000): a
    CLOSABLE resultant target-state ("the door opened" -> open, cancellable) AND a PERMANENT occurrence-fact
    (a door-opening happened; never retracted). The register keeps both.
- **OUR-INVENTION-UNDER-TEST (swept, labelled):** the state-extraction patterns; the incompatibility/antonym
  lexicon that triggers closure; the discrete-interval representation.

## What was measured
1. **Construction gold -- the CI-separated capability proof** (`exp_state_register_query_v1`, n=420 queries;
   feeds ABSTRACT events with by-construction labels so the number is TRACKING, not extraction; the SPACE
   playbook). Four discriminating structures, each defeating a DIFFERENT stateless floor: **BIND** (two
   entities -> entity-blind floors mis-bind), **RESULT** (a telic verb introduces a state -> adjective-only
   floors are blind), **SUPERSEDE** (an incompatible state cancels a prior one -> an ever-mentioned-for-
   entity floor, which uses the gold entity key, still says the cancelled state holds), **PERSIST** (a state
   holds after K filler clauses -> a windowed floor forgets it). **REGISTER 1.000 [1.000,1.000] vs the
   strongest stateless floor 0.719 [0.676,0.762]** -- CI-separated, robust across seeds 0/1/2. Both info-free
   twins lose (entity-shuffle 0.762, order-shuffle 0.843; null p95 0.048/0.038); the **empty register scores
   0.429 = chance**, not perfect. Distance-robust: register flat 1.000 at K=0..20 while the windowed floor
   collapses to 0.000 at K>=2 (a maintained property, not a local read -- exactly the SPACE signature).
2. **Real prose** (`exp_state_register_real_prose_v1`, 25 LitBank docs, gold-coref entity key held FIXED).
   Extraction **coverage 0.374** (489/1309 spaCy-reference predications extracted AND bound to a gold cluster).
   The previously-**DROPPED "had been X" prior-state channel** -- the brief's whole motivation, 27% of
   pluperfects, consumed by NOTHING -- is now extracted and bound (n=33 prior states; hand precision ~0.65,
   value forms clean: "Lady Elliot had been an excellent woman", "her father had always been busy", "her
   mother had been a beauty", "Mary had been tired", "he had been remarkably handsome"). Entity-state queries
   are **unsolvable by a stateless heuristic**: the entity-blind floor sits at 0.492 and the entity-shuffle
   twin at 0.456 -- both chance -- so answering them REQUIRES entity-bound state history.

## The wall I drilled the brain's way (owner: "if the brain can do it, we should be able to also")
Running the adapter on raw 19c prose exposed an EXTRACTION-precision wall (a first hand sample scored ~0.45):
spaCy mis-attaches on long archaic sentences, and the raw pattern over-fires on **relative/interrogative
subjects** ("which/that/what" -> not trackable entities), **junk predicate nominals** ("whatever/one/all"),
**mis-parsed verbs read as predicates**, and **crude participle lemmas** ("known"->"know"). The brain resolves
these with syntactic + semantic typing -- the same class of gate the SPACE organ used to lift Goal precision
0.22->0.91. I built glass-box gates copying that: a **subject-type gate** (reject relativizers/quantifiers),
a **predicate-content gate** (a state VALUE must be a contentful ADJ or type-nominal, never a VERB or light
noun), **participle surface forms** ("born"/"known", not the lemma), and four **irrealis/aspect guards** the
research flagged -- conditional subject-aux **inversion** ("Had he been..."), **"if" irrealis** ("if he had
been clean"), **habitual** ("in the habit of"), and **existential** ("there has been X", expletive subject).
These lifted the hand-sampled precision to ~0.55-0.65 overall and ~0.65 on the clean "had been X" channel, at
coverage 0.374. **The irreducible residual is spaCy attachment error on long 19c syntax -- the SAME corpus-age
parse wall already characterised and bounded by `role_assignment_is_untested_on_archaic_literary_prose`** (a
modern parser degrades on archaic long sentences); it is an ADJACENT-component cap, not a state-register wall.

## What I did NOT establish (withdraw-first if wrong)
- **The CI-separated headline is on CONSTRUCTION gold** (real English state constructions, but controlled
  multi-entity/multi-state threading with by-construction labels), NOT fully-natural raw-prose queries -- for
  the same reason the SPACE organ used construction gold: on unrestricted 19c prose the extraction-precision
  wall (0.374 coverage, ~0.6 precision, coref) would dominate the tracking signal, and an auto-mined natural
  gold would be as noisy as the mechanism (circular). The real-prose burden is carried by coverage + the
  prior-channel extraction + the demonstration that the queries are unsolvable by a stateless floor. **First
  thing I would withdraw:** any implied claim that the register answers UNRESTRICTED natural-narrative state
  queries at construction-gold accuracy -- it tracks at that accuracy given clean state events; raw-prose
  extraction is coverage-0.374 / precision-~0.6-bounded.
- **The register=1.000 on the real-prose definitional-gold population is DEFINITIONALLY CIRCULAR** (the gold
  binding IS what the register extracted) and is NOT quoted as a capability number. The meaningful real-prose
  evidence is the coverage, the hand precision, and the entity-blind floor + twin sitting at chance.
- **The interval-CLOSURE (supersession) advantage, proven CI-separated on construction gold, has ~0 natural
  incidence in this corpus** (0/489 bound events show an extracted antonym-supersession). It is real but rare
  in 19c narrative; I did not manufacture incidence.
- The archaic BE-perfect ("was become/grown") is captured for VALUE but tagged CURRENT not PRIOR aspect (a
  minor fidelity gap); same-slot supersession without an antonym ("was a soldier but now a farmer") needs a
  "but now"/"no longer" discourse-cue detector (mapped follow-on).

## KEY REALIZATIONS (the enabling moves)
1. **The research killed my first design and that was the whole win.** I was about to file a pluperfect "had
   been X" as a PRIOR/CLOSED interval. The drill showed the perfect's currency is a **cancellable default,
   not an entailment** -- so the register default-PERSISTS prior states and closes only on an explicit
   cancellation cue. Copying the linguistics instead of my intuition is what made the register's advantage
   the CANCELLATION logic + binding + resultant inference, not a blanket "pluperfect = prior".
2. **States are NOT mutually exclusive -- so closure must be EXPLICIT.** Location is single-valued (one place
   at a time), so the SPACE register overwrites on each motion. A state register that overwrote would be
   wrong: "ill" and "a soldier" co-exist. The core keeps multiple concurrent spans and closes one only on an
   antonym / negation / telic-transition. This is the structural difference from the sibling organ.
3. **The telic two-field split (Parsons) is load-bearing.** "The vase had been broken" is TWO facts: the vase
   IS-broken (a closable state -- it can be mended) and a breaking-event OCCURRED (permanent). Collapsing them
   loses either the cancellability or the history.
4. **The info-free twin at chance (empty 0.429) and the per-structure breakdown are the real proof, not the
   1.000.** No single stateless floor handles binding + resultant + supersession together (RESULT 1.000 vs
   floors 0.000; SUPERSEDE 1.000 vs ever-entity 0.258); the register does. That is a mechanism claim a bare
   accuracy cannot make.
5. **The precision wall was EXTRACTION, not tracking** -- and the brain's fix is syntactic+semantic typing
   (the SPACE ATL-gate lesson), plus the aspect/irrealis guards the research named. Every angle plateaued
   until I asked "what makes a subject a trackable entity and a predicate a contentful state", which is a
   parse-semantics question, not a tracking one.

## ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization -> candidate next problems)
- **The change-of-state verb lexicon (`COS_VERB_RESULT`, ~40 verbs) is an OUR-INVENTION placeholder.** The
  brain-faithful version is a **VerbNet/FrameNet result-state class** (the same resource the SPACE organ used
  for motion frames) mapping every telic verb to its resultant + the two-field split. Fidelity: PARTIAL
  (curated, not exhaustive). Optimization: a full VerbNet-derived result-state lexicon would raise the
  resultant-channel recall. **Candidate follow-on.**
- **The incompatibility/antonym lexicon (closure trigger, ~18 sets) is OUR-INVENTION.** Brain-faithful =
  lexical antonymy + scalar/degree structure (Kennedy & Levin degree achievements) + a **state-SLOT ontology**
  (profession, marital status, physical condition) so "was a soldier ... now a farmer" closes on the slot,
  not only on an antonym. Fidelity: PARTIAL. **Candidate follow-on: a WordNet-attribute/antonym state
  ontology + a "but now / no longer" discourse-cancellation cue** (the canceller the research says the default
  needs).
- **The dependency parser (spaCy) on 19c prose is the coverage cap (0.374, precision ~0.6).** This is the
  SAME corpus-age wall `role_assignment_is_untested_on_archaic_literary_prose` characterised; its proposed
  cue-override subject stage would directly reduce the subject-attachment errors that cost state-extraction
  precision. Fidelity: the parser is a statistical tool, not the brain's mechanism. **Cross-references an
  existing filed problem -- shared cap.**
- **`coreference_resolver` (~0.65 real prose) supplies the entity KEY.** I held it FIXED with gold clusters
  (bar #3); on live prose its quality caps state->entity binding, exactly as it caps the SPACE register.
  Already a standing cap (p3). **Not a new problem.**
- **The TIME register (just integrated) supplies discourse time.** I use the sentence index as the clause
  time; composing state intervals with the TIME register's event-time would answer "what state was X in WHEN
  event E happened" (a state x time join). **Candidate wiring, not a new build.**

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- strategy folds in)
The §2b adjacent-map and the SPACE/TIME entries note "entity STATE history is a gap ... currently ABSENT".
**This is now BUILT and validated in experiments/ (proposed for hdlab landing).** Recommended new entry:
**State-history register / event-indexing ENTITIES(state) dimension** -- brain structure: Zwaan & Radvansky
ENTITIES + Ferretti/Kutas/McRae 2007 aspect->entity-state routing (PINNED) + hippocampal-entorhinal attribute-
entity-over-context binding. Our fidelity: the bind-state-to-entity-over-interval COMPUTATION copied (PINNED),
default-persist + cancellable-perfect + telic two-field (PINNED, corrected from a naive auto-close); extraction
patterns + antonym lexicon + interval representation are OUR-INVENTION-swept. Deviations to record: (a)
real-prose extraction is coverage-0.374 / precision-~0.6-bounded by the modern parser on 19c syntax (shared
with the role/parse cap); (b) the interval-CLOSURE channel has ~0 natural incidence in LitBank (proven on
construction gold); (c) archaic BE-perfect aspect-tagging + same-slot supersession are mapped residuals.

## FOR STRATEGY (you land hdlab; Q111 -- I do not write hdlab/)
1. **Promote the tracking CORE `experiments/state_register.py` -> `hdlab/state_register.py`** as a first-class
   organ, sibling of `hdlab/location_register.py`: `StateRegister` with `is_in_state` / `state_at` /
   `had_been` / `occurrences_of`, spaCy-free, consuming abstract state events. Keep the extraction adapter
   (`StateReader` + `extract_state_events`) on the experiments side (it needs the parser), exactly as the
   SPACE split kept the motion reader experiment-side.
2. **Point the ENTITIES stack at it:** the coref entity key supplies the register's entity; wire the register
   as the consumer of the "had been X" / copular / resultant channel that the TIME extractor correctly skips
   (this closes the loop the TIME solver opened -- 27% of pluperfects currently consumed by nothing).
3. **Keep the two-field telic split and the cancellable-perfect default** (do NOT auto-close pluperfects --
   the research shows that overclaims). Keep the antonym/incompatibility lexicon and COS map as swept, not
   adopted.
4. Do NOT re-order states as events (the TIME organ correctly skips them); do NOT rebuild coref or the
   interval bookkeeping (reuse the SPACE pattern).

## TLDR
Stories constantly say what state a character or thing has been in -- "the house had been grand", "she had
been ill", "he had been a soldier" -- and our reader was throwing every one of these away (over a quarter of
all "had..." phrases in real books are exactly this). I built the missing record: a per-character state history
that reads these in, remembers what each entity has been (and, for events like a door opening, what state it is
now in), keeps a state until something actually contradicts it, and can be asked "what state had X been in?" or
"is X still S?". On a controlled test it is right ~100% of the time versus ~72% for the best guess that ignores
which entity a state belongs to, a scrambled version fails (so the skill is the tracking), and an empty version
scores at chance (so it is not gaming the test). On real 19th-century novels it correctly pulls out the "had
been X" facts nothing used before, and those questions turn out to be impossible to answer without it (the
best entity-blind guess is a coin flip). The one honest limit is reading messy old prose: a modern grammar
parser gets about 37% of the state sentences cleanly -- the same old-text wall another problem already measured
-- so I fixed what the brain's own typing rules fix and honestly bounded the rest.

## QUESTIONS
None.

## NEXT STEPS
1. Strategy: re-verify + land `hdlab/state_register.py` (spaCy-free core) and wire the ENTITIES stack /
   TIME-skipped "had been X" channel into it.
2. Follow-on problem: a **VerbNet result-state lexicon + a state-slot antonym/ontology + a "but now / no
   longer" discourse-cancellation cue** (raises resultant recall + enables same-slot supersession).
3. Optional wiring: join state intervals with the TIME register's event-time ("what state was X in WHEN E
   happened").
4. Shared cap: the 19c parser precision (0.374 coverage) is the `role_assignment` corpus-age wall -- its
   cue-override subject stage would directly help state extraction.
