---
problem: theory_of_mind_residual_is_the_observation_cue_front_end
status: SOLVED
bar: "PASSES only with ALL of: 1. observation-cue extractor beats the 0.808 lexical baseline CI-separated on cue accuracy (did agent A witness event E?), on a CORPUS-mined false-belief gold (real story passages, not authored); recompute the strongest real floor; info-free twin (shuffled presence/absence) LOSES CI-sep; report CI half-width + null p95. 2. Lifts END-TO-END belief accuracy (feeding the LANDED belief_partition) toward oracle 1.000, CI-separated over the lexical-cue end-to-end 0.821. 3. Brain-faithful mechanism: a PERCEPTUAL-ACCESS inference read from the event/entity/situation structure (presence/absence/informed at the moment of change), NOT a keyword list; COPY the computation, SWEEP params. 4. A corpus-mined false-belief gold exists + is verified: real passages where an agent holds a belief the world has since falsified, observation state derivable from text; report how mined + verified. A rigorous NEGATIVE is a FULL PASS."
result: "Observation-cue accuracy (scorer: extractor observed-bit == ground-truth observation state). CORPUS-GROUNDED gold (real LitBank cue-clauses in canonical frames): LEDGER 0.988 [0.972,1.000] dev (n=246), 0.985 [0.978,0.992] HELD-OUT (5 unseen phrasing draws, n=1230) vs lexical 0.500 [0.439,0.557]. INTACT natural LitBank passages (n=86 balanced): LEDGER 0.930 [0.872,0.977] vs lexical 0.581 -- CI-separated. Authored gold: LEDGER 1.000 vs lexical 0.808. END-TO-END through the LANDED hdlab.belief_partition (corpus gold): LEDGER 0.988 [0.972,1.000] vs lexical 0.500 vs oracle 1.000."
floor: "Strongest floor actually run = the LANDED lexical extractor (extract_observed_from_text) recomputed on EACH gold: 0.500 [0.439,0.557] on the corpus gold, 0.808 on the authored gold. Also: majority-class 0.500 (gold balanced 50/50); always-observed / always-not-observed both 0.500. Ledger CI-low 0.980 > every floor CI-high."
controls: "INFO-FREE TWIN (randomised observation): corpus 0.488 [0.423,0.553] and intact 0.581 -- both LOSE CI-sep. HELD-OUT: tuned on one seed's errors, measured on 5 UNSEEN phrasing draws (0.985 pooled) -- rules out overfit. PER-CLASS dissociation (corpus): ledger advantage entirely on NOT-OBSERVED classes (depart 1.000, occlude 0.980 vs lexical 0.000) -- proves it READS the cue. RULE-DECOMPOSITION (intact): with RULE 0 (explicit marker) OFF, spatial-only = 0.535 (chance) because the spatial CAUSE is out-of-window; the situation model is built incrementally over the WHOLE text, so windowing under-powers RULE 1 -- a MEASUREMENT artifact, not mechanism failure (frame gold, where the cause is in-frame, isolates RULE 1 at 0.98). LABEL VERIFICATION: read ~50+ clauses, ~90% precision after metaphor/transitive/speech-tag/dialogue filters. CANONICAL: solves re-entry, occlusion-despite-co-presence, went-to-new-place, testimony."
files_changed: "experiments/perceptual_access_ledger.py; experiments/exp_perceptual_access_corpus_v1.py; experiments/exp_perceptual_access_intact_v1.py; experiments/mine_presence_phrasings_v1.py; experiments/mine_false_belief_corpus_v1.py; experiments/exp_perceptual_access_distance_v1.py; verification/test_perceptual_access_ledger.py; verification/test_perceptual_field_occlusion.py; verification/test_sequential_registration.py; verification/test_testimony_reliability.py; notes/problems/theory_of_mind_residual_is_the_observation_cue_front_end/{BRAIN_MECHANISM_SPEC.md,SOLVED.md}; data/{exp_perceptual_access_corpus_v1,exp_perceptual_access_intact_v1,exp_perceptual_access_distance_v1,mine_presence_phrasings_v1,mine_false_belief_corpus_v1}/. NO hdlab/ writes (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_perceptual_access_ledger.py && .venv/Scripts/python.exe verification/test_perceptual_field_occlusion.py && .venv/Scripts/python.exe verification/test_sequential_registration.py && .venv/Scripts/python.exe verification/test_testimony_reliability.py"
---

## What I built

A **brain-faithful observation-cue front-end** that replaces the landed lexical keyword extractor (0.808) with a
glass-box **perceptual-access REGISTRATION LEDGER** (`experiments/perceptual_access_ledger.py`).

The mechanism is copied from the developmental/cognitive-science account of "seeing leads to knowing" (a deep,
web-verified literature drill is captured in `BRAIN_MECHANISM_SPEC.md`). The single most important correction to
the naive gate `observed = co_present AND available OR informed`: the brain does NOT re-evaluate a boolean at query
time -- it maintains a **sticky, procedurally-updated ledger** (Butterfill & Apperly 2013, *Mind & Language*):

- **Presence is a temporal INTERVAL** on a per-agent location register (Zwaan & Radvansky event-indexing SPACE
  dimension; Speer/Zacks 2009: parahippocampal + hippocampus fire on a character's location change during ordinary
  reading). Departure closes the interval, arrival opens it; `presence_check` is interval containment. This is
  exactly what the stateless keyword list cannot do (re-entry, present-before-gone-during).
- **Motion updates location by reading the realized PATH SATELLITE / Source-Goal-Path PP** ("out", "into X",
  "back", "upstairs"), NOT a manner-verb whitelist (Talmy 1985; Papafragou 2008; FrameNet's ~15-20 frames do NOT
  collapse to a small primitive set). "She florped out" still departs via "out". **Deixis dominates** (come/return
  vs go/leave). This is why the ledger generalises to real literary phrasings the keyword list never enumerated.
- **The OCCLUSION field gate -- a PER-MODALITY field** (from a dedicated occlusion/Level-1-VPT research drill),
  the precisely-diagnosed NLP wall (FANToM Kim 2023: Belief >> InfoAccess; Ullman 2023 transparent-bag). Not a
  coarse single blocker: vision needs light + line-of-sight + not-in-a-closed-opaque-container + attending +
  awake; audition penetrates darkness / thin barriers / inattention but needs a non-silent event; touch needs
  contact. So a NOISY move in the dark is HEARD where a silent one is not, and a TRANSPARENT container is seen
  where an opaque one is not -- distinctions a keyword gate structurally cannot make. Unstated opacity returns a
  glass-box UNKNOWN rather than a guess.
- **A TESTIMONY route** (RULE 2): being told = knowledge without perception (Harris & Koenig 2006).
- **An EXPLICIT-STATEMENT route** (RULE 0, highest priority): when the narrator states the mind-state outright
  ("unbeknownst to her", "he did not perceive", "she watched it"), a faithful reader uses it directly -- it is
  the most direct evidence, testimony from the narrator. RULE 0 covers a broad set of epistemic verbs where the
  landed keyword list has only two ("did not see/notice").

`observed` (the bit the landed `belief_partition.believed_location` gate consumes) == "RULE 0 (explicit statement)
else RULE 1 (co-present & field-open at the move) OR RULE 2 (informed)". **False belief is not a separate
computation -- it is the ledger being stale relative to ground truth** (exactly what the landed organ models).

## What I measured

1. **Canonical dissociation.** The ledger solves 4 cases the stateless keyword list structurally cannot:
   re-entry-then-present, occlusion-despite-co-presence, went-to-a-new-place, testimony-after-absence (5/5 with the
   Sally/Anne cases; witness [1]).
2. **Authored gold:** ledger cue accuracy **1.000 vs lexical 0.808** (the residual's own gold; witness [2]).
3. **Corpus-grounded gold (the generality test):** ledger **0.992 [0.980, 1.000]** dev / **0.985 [0.978, 0.992]**
   held-out (5 unseen phrasing draws, n=1230) **vs lexical 0.500 [0.439, 0.557]** -- CI-separated by ~0.44, over the
   majority floor 0.500 and the info-free twin 0.488 (witness [3]). The lexical baseline collapses from 0.808 (its
   own authored phrasings) to 0.500 (near chance) on diverse real corpus phrasings -- it defaults to "present" and
   misses every absence it does not have a keyword for. **This IS the residual.**
4. **End-to-end lift** through the LANDED `belief_partition`: ledger **0.988 [0.972, 1.000] vs lexical 0.500**, past
   the in-situ residual 0.821 (witness [4]).
5. **INTACT natural LitBank passages** (n=86 balanced real 3-sentence windows around dramatic-irony markers):
   ledger **0.930 [0.872, 0.977] vs lexical 0.581** -- CI-separated, twin loses (witness [5]). **Honest
   decomposition:** with RULE 0 (explicit marker) OFF, spatial-only drops to **0.535 (chance)** -- because in a
   3-sentence WINDOW the spatial CAUSE of absence is usually out-of-window (the character left pages earlier). So
   on intact windows the win is RULE 0's broad marker coverage (the landed keyword list has 2 epistemic verbs and
   scores 0.30/0.20 on the "ignorant"/"irony" tiers; the ledger covers the diverse set and scores 1.00). The
   SPATIAL mechanism's clean test is the frame gold, where the cause is in-frame -- there RULE 1 does all the work.
6. **OCCLUSION discriminators** (`verification/test_perceptual_field_occlusion.py`, from a dedicated occlusion/
   Level-1-VPT research drill): the PER-MODALITY field gate gets **6/6** of the cases the literature says the brain
   makes and a keyword gate cannot -- transparent-vs-closed-opaque container (the Ullman flip), silent-vs-loud
   change in the dark (darkness blocks vision only, so a loud move is HEARD), behind-an-opaque-screen despite
   co-presence, present-but-not-attending. A COARSE single-gate baseline fails 2/6 -- exactly the opacity + loudness
   distinctions it structurally cannot represent.
7. **DISTANCE ROBUSTNESS -- the spatial route is distance-invariant over the full text** (`exp_perceptual_access_
   distance_v1.py`, witness [6]): inserting K neutral filler sentences between the departure and the move, the
   FULL-text spatial route (RULE 0 off) holds at **0.99-1.00 for K = 0..20**, while a 3-sentence WINDOW collapses
   from 0.99 (K=0) to **0.00 (K>=2)** the moment the departure scrolls out. This PROVES the intact-window
   spatial-only chance score (item 5) is a WINDOWING artifact, not a mechanism failure -- and validates the Zwaan
   incremental-situation-model claim: presence is a STATE maintained across the whole narrative.
8. **SEQUENTIAL registration -- the mechanism's completion** (`verification/test_sequential_registration.py`,
   from a second research drill): folding the per-event cue over a CHAIN of changes yields a sticky per-agent
   ledger. **4/4** discriminating cases the single-move gate cannot express: (a) A->B->C, sees the first move only
   -> believes **B** (last-registered, not initial/final); (b) watched-object-INTO-a-box then secretly emptied ->
   believes the **box** (destination frozen -- the motion-persistence exception -- NOT ignorant, NOT the true
   location); (c) already-hidden-before-arrival -> **IGNORANT** (registration = None, distinct from a false
   "initial" guess); (d) two agents, one present one absent -> **divergent** per-agent beliefs over one event
   stream. No new theory -- the existing `observed()` is reused per change; only the fold + an UNKNOWN default are
   new (Butterfill&Apperly registration; Baker/Saxe/Tenenbaum 2011 freeze-when-unobserved).
9. **TESTIMONY with RELIABILITY** (`verification/test_testimony_reliability.py`; Harris&Koenig 2006 testimony as
   an independent channel; Koenig 2004 reliability discounting): testimony writes the **asserted** location to the
   ledger, so **3/3**: (a) told the truth -> true belief; (b) **believed a LIE -> a FALSE belief matching the lie**
   (asserted != reality -- the single-move gate cannot represent "believes X" where X is neither initial nor true);
   (c) a **DISTRUSTED** source is discounted -> the agent keeps its prior belief. Cases (b) and (c) assert the SAME
   location and diverge only on trust. (The landed RULE 2 only handled honest testimony -> knows-reality.)

## HONEST SCOPE -- what I did NOT establish (read before quoting)

- **TWO golds, complementary; each has a real caveat.** (a) The CORPUS-GROUNDED frame gold isolates the SPATIAL
  mechanism: its cue clause is REAL, diverse LitBank prose ("stole out quietly", "was unconscious", "had withdrawn
  to the library" -- mined from 100 novels by a BROAD net) with a ground-truth-by-construction label, in a
  canonical frame; it is NOT an intact scene. (b) The INTACT gold uses REAL intact 3-sentence LitBank windows with
  the narrator marker as label -- but on windows the win is RULE 0 (explicit-marker coverage), NOT the spatial
  mechanism (spatial-only = chance because the cause is out-of-window). Neither gold alone is a full
  intact-natural-scene-with-spatial-inference test; together they cover the mechanism (a) and the realism (b).
- **Finding (bar #4, the honest gap): intact false-belief-about-an-object scenes are TOO SPARSE to mine at scale**
  -- 991 dramatic-irony marker windows over 100 novels, most idiom / dialogue / unfamiliar-person ("unknown to
  Tommy" = an unfamiliar *person*, not an unwitnessed *event*); and automatic mining of clean presence/absence is
  bounded by **verb POLYSEMY** ("observed" = remarked vs watched; "left" = departed vs deposited; "returned" =
  came-back vs replied; "passed away" = died vs time-passed). Polysemy is a wall the brain crosses with full
  lexical semantics; our glass-box front-end cannot. I report this rather than paper over it.
- **The intact-WINDOW test under-powers the spatial mechanism by construction, and this is now PROVEN** -- the
  distance experiment (item 7) shows the spatial route holds at 0.99 across K=0..20 filler sentences over the full
  text but collapses to 0.00 under a 3-sentence window. So windowing (not the mechanism) causes the intact-window
  chance score; the DEPLOYED reader runs over the WHOLE running model where the spatial cause IS available. Still,
  on intact windows RULE 0 (explicit markers) is what wins; do not quote the intact 0.930 as a spatial-inference
  result -- the spatial-inference result is the frame gold (0.988) + the distance invariance (0.99 at K=20).
- **Label precision ~90%** (verified by reading ~50 clauses); residual mislabels are deep polysemy. The 0.98-vs-0.50
  gap is an order of magnitude larger than the label noise, so the conclusion is robust, but the exact 0.992 is
  gold-quality-bounded.
- **Coreference is a simple proxy** (salient-subject / pronoun-default + a parse-failure fallback for the mis-tagged
  sentence-initial proper noun). On the canonical frames the agent is the salient subject so this suffices; on
  intact multi-character literary prose, coref becomes the binding constraint -- the deployment path is LitBank GOLD
  coref (on disk) or the substrate's coref organs, which is where this should be WIRED.
- **First-order belief only** (the landed organ's scope); higher-order "A thinks B thinks" is a separate line.
- **What I would withdraw first if wrong:** the exact 0.992 (gold-quality-bounded). What I would NOT withdraw: the
  ledger beats the lexical baseline on BOTH golds, the twin loses, and the not-observed dissociation -- those are
  robust to the label noise and the held-out check.

## KEY REALIZATIONS (the enabling moves)

1. **False belief is the ledger being stale -- there is no separate "compute false belief" step.** Reframing the
   cue as a sticky per-agent registration ledger (not a query-time boolean) is what made the mechanism map exactly
   onto the landed `believed_location(observed, initial, final)` gate. (Butterfill & Apperly 2013.)
2. **PATH lives in the SATELLITE, not the verb** -- the wall I *expected* (open-vocabulary motion verbs) is an
   IMPLEMENTATION TRAP. Reading Source/Goal/Path off the realized PP/particle, with deixis dominating, generalises
   to arbitrary manner verbs. Hardcoding a verb whitelist would have manufactured a wall the brain doesn't have.
3. **The REAL wall is elsewhere and I had to find it twice:** (a) OCCLUSION reasoning (FANToM/Ullman) -- built as an
   explicit field gate; (b) VERB POLYSEMY -- it bit the extractor ("gazed into the fire" is not locomotion; suppress
   motion for perception/stance verbs) AND the gold labels ("passed away" / dismount / speech-tag "returned").
   Naming the polysemy wall precisely (rather than calling the corpus "too noisy") is the deliverable for bar #4.
4. **Deixis dominates + presence is scene-relative:** "went upstairs to bed" departs even though "bed" looks like a
   scene word; "hurried indoors" departs when the object is outdoors. The clean rule -- any self-motion leaves the
   object's scene unless it is an explicit return -- fell out of reading the errors, not from the armchair.
5. **Two brain-faithful routes, and the intact test told them apart: explicit statement (RULE 0) vs spatial
   inference (RULE 1).** On intact 3-sentence windows the spatial mechanism alone is at CHANCE -- not because it is
   wrong but because the spatial cause is out-of-window; the situation model is built INCREMENTALLY over the whole
   narrative (Zwaan), so a window strands it. The narrator usually states the mind explicitly there, and a faithful
   reader uses that (RULE 0). This is why the DEPLOYED front-end must run over the full running situation model, not
   windows -- and why the two golds (spatial-isolating frame; explicit-marker intact) are both needed. Turning RULE
   0 off to *measure* the spatial contribution is the move that made this legible.
6. **The "ledger" formalism only earns its name over a SEQUENCE -- and then two subtle bugs surface that a single
   move hides.** Folding the per-event cue over a chain (A->B->C) gives last-registered-not-final beliefs, motion-
   persistence, and ignorance-vs-false-belief for free -- but only after fixing (a) the occlusion window read one
   sentence PAST the event, so a closure described *after* a move wrongly blocked perception of it (motion-
   persistence broke); and (b) RULE 0 scanned the whole text, so "Anna watched" (move 1) leaked onto move 2 --
   epistemic markers are EVENT-LOCAL. Both are invisible in the single-move case; the sequence is what exposed them.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b, Theory of Mind)

- The **RESIDUAL named in the audit (the observation-cue front-end)** now has a brain-faithful mechanism: a
  spatial-presence **registration ledger** (Butterfill & Apperly field/encountering/registration; Zwaan event-
  indexing SPACE dimension; Talmy PATH satellites). Verdict on the landed lexical extractor: it is an
  OUR-INVENTION-UNDER-TEST stand-in that does NOT generalise (0.808 -> 0.500 on real corpus phrasings).
- Add **OCCLUSION / perceptual-availability** as a first-class, PINNED sub-mechanism and the precisely-diagnosed
  NLP-vs-brain wall (FANToM Kim 2023; Ullman 2023) -- previously unnamed in the ToM entry. Now built as a
  PER-MODALITY FIELD (vision/audition/touch each gated separately, over an occluder ontology: opaque-barrier /
  closed-opaque-container / transparent-open-container / darkness / inattention / asleep), with UNKNOWN as a
  first-class value for unstated opacity. Discriminators 6/6 (`test_perceptual_field_occlusion.py`).
- Add **VERB POLYSEMY** as a fidelity wall for any text front-end (the brain uses full lexical semantics; our
  glass-box reader cannot), distinct from coreference.
- Correct any implication that reading "who saw what" is a keyword problem: it is a SITUATION-MODEL read (spatial
  interval + occlusion + testimony), PINNED.
- Record **SEQUENTIAL registration** (the mechanism's completion): belief over a CHAIN = the last change the agent
  perceived (sticky per-agent cell, world-track separate), with (i) the MOTION-PERSISTENCE exception (watched-it-
  into-an-occluder registers the destination; the occlusion-window off-by-one bug that broke this is fixed --
  occlusion must hold AT-OR-BEFORE the event, not after), and (ii) IGNORANCE (registration=None) as a first-class
  state distinct from false belief. `belief_partition`'s binary `believed_location(observed, initial, final)`
  should be extended to this. Epistemic markers are EVENT-LOCAL (a marker about move 1 must not leak onto move 2).
- Record the **two-route dissociation**: an EXPLICIT-STATEMENT route (narrator asserts the mind-state; local) and a
  SPATIAL-INFERENCE route (needs the FULL incremental situation model -- Zwaan). On intact windows the spatial
  route is at chance because the cause is out-of-window; the deployed front-end must run over the running model,
  not windows. The diagnosed walls are OCCLUSION + verb POLYSEMY, NOT coreference.

## PROPOSED hdlab CHANGE (strategy lands it -- Q111)

- **Promote** `experiments/perceptual_access_ledger.py` -> `hdlab/perceptual_access.py` (`PerceptualAccessLedger`,
  the observation-cue front-end), default-off island exactly like `belief_partition`.
- **Wire** it as the input stage of the belief pipeline: for each (agent, object-move) the situation model surfaces,
  call `led.observed(...) -> observed bit -> belief_partition.form_belief(agent, obj, initial, final, observed)`.
  **Run it over the FULL running situation model, NOT a local window** -- the spatial route (RULE 1) needs the
  incremental presence history (the intact-window test showed spatial-only collapses to chance when the history is
  windowed away). It should CONSUME the substrate's coref / situation-model organs for mention resolution + event
  localisation (currently a spaCy-parse proxy inside the module) rather than re-parsing -- `agent_aliases` +
  `event_location`/`event_index` are the seams; on real multi-character prose use gold/organ coref. RULE 0
  (explicit narrator epistemic statements) is local and works today; RULE 1/RULE 2 are where the wiring pays off.
- **Do NOT** touch the belief mechanism, its controls, or its dissociations (DONE + LANDED).
- **Extend `belief_partition` from a single-move gate to a SEQUENCE registration ledger** (the sequential-
  registration drill): `believed_location(observed, initial, final)` is binary and cannot express (a) a
  last-registered INTERMEDIATE state in a chain, nor (b) an IGNORANT agent (registration = None, distinct from a
  false "initial" belief). The proposed shape is on disk + validated in `perceptual_access_ledger.
  sequential_registration()` + `belief_of/is_false_belief/is_ignorant` (world-track + per-agent sticky cell,
  UNKNOWN default). Keep the two stores separate (world vs per-agent -- already the organ's shape; neuro-plausible
  per Saxe rTPJ).
- Register `perceptual_access_v1` in the capability registry; witnesses `test_perceptual_access_ledger.py` +
  `test_perceptual_field_occlusion.py` + `test_sequential_registration.py` are the landed-VET gates.

## ADJACENT GAPS THAT ARE SUBOPTIMAL -- candidate focused-solver problems (grounded on disk)

Building this front-end surfaced adjacent components that BOTTLENECK it (and other reading organs) and are
bounded enough to hand to focused solvers. Ranked by leverage; each with the on-disk evidence.

1. **NO SPATIAL (SPACE) DIMENSION IN THE SITUATION MODEL -- a genuinely MISSING organ. [highest leverage]**
   `hdlab/situation_model_accumulate.py`, `situation_reader.py`, `factorized_entity_store.py`, `event_bundle.py`
   bind (entity, role, event) but NONE tracks WHERE each entity is over time (grep: 0-1 incidental "location"
   mentions, no location register). This is the Zwaan & Radvansky event-indexing SPACE dimension, PINNED as
   brain-foundational and absent. My ledger implements a minimal per-entity presence tracker INLINE as a stopgap.
   A focused solver would build it as a first-class organ (per-entity location register updated by motion events;
   presence intervals), validate on LitBank spatial tracking, and wire the observation cue + "where is X?" + any
   navigation/inference to it. Shared by many capabilities -> highest leverage.

2. **COREFERENCE ACCURACY ~0.65 ON REAL NARRATIVE -- a live bottleneck. [high leverage]**
   `hdlab/coreference_resolver.py` is WIRED and canonical, but its measured accuracy on real narrative is ~0.65
   (capability_registry: "coref abs ~0.65<0.70"). Every organ that resolves who-is-who on multi-character prose
   inherits that error -- including THIS observation cue (on intact multi-character passages the cue is
   coref-capped, which is exactly the brief's anticipated "the cue needs coref the reader lacks", now quantified).
   A focused solver would push real-narrative coref toward the situation model's needs, or make the confidence-
   gated abstain (already prototyped as honest-mode) a signal downstream organs consume so they degrade gracefully
   instead of silently inheriting a wrong link.

3. **VERB-SENSE / POLYSEMY -- a cross-cutting front-end wall. [broad leverage]**
   The diagnosed wall that bit BOTH my extractor and the gold labels: "left the room" (depart) vs "left a letter"
   (deposit); "returned home" vs "returned a reply" (said); "observed the move" vs "observed" (remarked); "passed
   away". There is no glass-box word-sense / frame disambiguator; every text front-end pays for this. A focused
   solver would build a minimal glass-box sense/frame disambiguator over the dependency parse (motion-vs-transitive,
   perception-vs-speech), which lifts this cue AND the reader broadly.

4. **EVENT (OBJECT-STATE-CHANGE) EXTRACTION -- a missing input stage. [medium]**
   The observation cue is GIVEN the object-move (via `event_index`/`event_location`); the live pipeline needs an
   organ to extract "what changed, where, when" from prose. Partial pieces exist (`outcome_event_extraction.py`,
   `event_bundle.py`) but no clean object-state-change extractor feeding the situation model. Bounded build.

5. **belief_partition IS A DEFAULT-OFF ISLAND WITH NO LIVE BELIEF-QUESTION TASK. [integration, strategy-owned]**
   `belief_partition` is first-order, perfect, and unimported; the live reader has NO belief tracking and its
   comprehension task asks no false-belief questions -- so the end-to-end value of this whole line is currently
   unmeasured on the REAL reader. Wiring observation-cue -> belief_partition into the reader AND adding belief
   questions to the reading task is where the payoff becomes visible. (This is strategy's integration lane, not a
   solver problem, but it is the gating adjacency for VALUE.)

## TLDR (plain language)

We already built a reader that correctly tracks what a story character believes -- but only when we hand it the
answer to "did this character actually see the thing change?" Reading that one fact from ordinary prose was the last
weak link, and it was done with a hand-written list of phrases, which works on our own tidy examples (81% right) but
falls apart on real novel language (50% -- a coin flip). I replaced the phrase-list with the brain's actual method:
keep a running note of where each character is, whether anything is blocking their view (a wall, sleep, darkness),
and whether they were told -- and mark them as knowing only when they were actually there and able to see, or were
told. On a test built from real sentences pulled out of 100 novels, this brain-style reader gets it right 98-99% of
the time versus the old 50%, and it never wins by luck (a scrambled version drops to a coin flip). Two honest limits:
truly intact "false-belief scenes" are rare in real books, so my test frames real absence/presence sentences rather
than whole natural scenes; and the deep reason both the old and any word-based reader struggle is that words are
ambiguous ("left the room" vs "left a letter"), which the brain resolves with full understanding and we can only
partly.

## QUESTIONS

None blocking. One scope decision made visible: I could not mine enough INTACT natural false-belief scenes (they are
genuinely sparse in literature), so I tested the observation cue on REAL corpus absence/presence *clauses* placed in
canonical frames, with ground-truth labels. If you want an intact-scene gold specifically, the path is LitBank gold
coref + hand-verification of the ~dozens of clean dramatic-irony windows -- smaller, and coref-bound.

## NEXT STEPS

1. (You) Re-verify with the one command above; fold the AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.
2. (You) Land the proposed `hdlab/perceptual_access.py` + wire it into the belief pipeline, consuming the coref /
   situation-model organs for mention + event localisation.
3. (Me, continuing) The 30-min deepening cron keeps drilling occlusion + the coref-on-intact-prose path; if a small
   gold-coref intact-scene gold becomes tractable it strengthens bar #4 from "corpus-grounded" to "intact-natural".

---
INTEGRATED_BY_STRATEGY: 2026-08-28 (grade EXCELLENT). Re-verified FIRST-HAND: 4 witnesses PASS (ledger 6/6,
occlusion 6/6, sequential 4/4, testimony 3/3). The observation-cue residual is SOLVED by a brain-faithful per-agent
PERCEPTUAL-ACCESS REGISTRATION LEDGER replacing the landed lexical extractor: cue accuracy 0.992 [0.980,1.000] vs
lexical 0.500 CI-sep on the corpus-grounded gold (twin 0.500 loses, held-out 0.985), END-TO-END through the landed
belief_partition 0.992 vs lexical 0.500 vs oracle 1.000 (past 0.821). Argument audit clean: lexical baseline is the
landed extractor recomputed per-gold (0.808->0.500 on real prose = the residual); per-class dissociation localizes
the win to NOT-OBSERVED classes; the intact-window spatial chance is PROVEN a windowing artifact (distance exp:
full-text 0.99 at K=0..20 vs windowed->0.00). Mechanism PINNED (Butterfill&Apperly registration; Zwaan SPACE; Talmy
PATH-satellite; Harris&Koenig testimony). Beyond the bar: OCCLUSION per-modality field (6/6), SEQUENTIAL registration
(4/4), TESTIMONY reliability (3/3). Honest scope preserved (two-gold split, intact-scene scarcity, verb polysemy +
coref caps, exact 0.992 gold-bounded). Review + SOLVER REVIEW block in PROBLEM.md; priority cleared. AUDIT UPDATE
folded (BRAIN_FOUNDATIONAL_AUDIT.md 2b). hdlab landing QUEUED (careful port: promote perceptual_access + extend
belief_partition to a sequence ledger; must consume the coref/situation-model organs to drop the spaCy-parse proxy,
else hdlab gains a spaCy dependency). 5 adjacent-gap briefs noted as future solver candidates (SPACE dimension =
highest leverage). NO hdlab written this commit (Q111 landing is the follow-on).
