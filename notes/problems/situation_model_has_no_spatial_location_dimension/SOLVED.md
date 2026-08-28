---
problem: situation_model_has_no_spatial_location_dimension
status: SOLVED
bar: "A per-entity LOCATION REGISTER organ (presence intervals updated by motion events off the PATH satellite, deixis dominating, maintained over the full running model); 'where is entity X at T?' CI-separated over the STRONGEST floor with the info-free twin LOSING CI-separated; a POSITIVE control the register gets and a stateless last-mention baseline cannot; and it SERVES a downstream capability (reproduces the ToM observation-cue win in place of the inline stopgap). A rigorous NEGATIVE is a full pass."
result: "'Where is X at T?' node-exact accuracy: REGISTER 1.000 [1.000,1.000] vs strongest stateless floor last-mention-location 0.417 [0.354,0.479], n=240 (construction gold: real English motion verbs, by-construction node labels, 4 discriminating structures x 60). Info-free shuffled-order twin 0.422 (null p95 0.468) LOSES CI-separated. Real-PROSE: SERVES the ToM cue 0.972 [0.947,0.992] vs lexical floor 0.500 on real mined LitBank presence clauses (n=246); motion-extraction gate 0.909 Goal precision on 186 real LitBank 'to X' tokens."
floor: "STRONGEST of four stateless floors recomputed on the same population: last-mention-location 0.417 [0.354,0.479] (hi 0.479); most-recent-scene 0.250; first-location 0.000; most-frequent-location 0.000. Register lower CI 1.000 > floor upper CI 0.479. Serve floor: lexical keyword extractor 0.500 (CI-separated, register-served 0.972)."
controls: "(1) INFO-FREE TWIN: register on shuffled-order text -> 0.422, LOSES CI-separated and lands AT floor level (0.417), so the win is 100% correctly-ordered tracking not a lexical prior. (2) POSITIVE CONTROLS per-type: REENTRY 1.000 vs last-mention 0.000, PERSIST 1.000 vs 0.000, STALE 1.000 vs 0.667 -- excludes 'metric cannot move'. (3) DISTANCE-ROBUSTNESS: register flat 0.967 at K=0..20 while WINDOWED (0.967->0.000 at K>=2) and last-mention (1.000->0.000 at K>=5) COLLAPSE -- excludes 'local read'. (4) ABLATION real prose: place-typing + motion-frame gates raise Goal precision 0.219->0.909, communication-verb false-goals 0.573->0.000 (n=96) -- excludes 'gates do nothing'. (5) SERVE presence agreement with the stopgap 0.967 overall, 0.985 on presence-decisive classes."
files_changed: "experiments/location_register.py; experiments/exp_location_register_where_is_x_v1.py; experiments/exp_location_register_distance_v1.py; experiments/exp_location_register_serves_tom_v1.py; experiments/exp_location_register_verbclass_gate_v1.py; verification/test_location_register.py; notes/problems/situation_model_has_no_spatial_location_dimension/{SOLVED.md, research_motion_goal_vs_addressee_and_spatial_situation_model_2026-08-28.md}"
reverify: ".venv/Scripts/python.exe verification/test_location_register.py   # 12/12 ; then .venv/Scripts/python.exe experiments/exp_location_register_where_is_x_v1.py   # HARD_PASS, REGISTER 1.000 vs floor 0.417"
---

# The situation model now has a per-entity SPACE dimension: a first-class LOCATION REGISTER

## What was built
`experiments/location_register.py` -- `LocationRegister`, the missing Zwaan & Radvansky **event-indexing SPACE
dimension**. Per entity it maintains a list of **presence intervals** `(location_node, t_open, t_close)`:
an arrival opens an interval, a departure closes it (Allen interval containment). `where_is(entity, t)` returns
the node active at clause `t`; `present_in_scene(entity, t)` is the co-presence bit the ToM cue consumes. It
COMPOSES with the existing `(entity, role, event)` binding rather than replacing it: `to_fhrr_readout` binds
the current node through the substrate's own FHRR `RelationRegister.bind_filler` and decodes it back at cos
1.000 (witness), so the location dimension lives in the same binding algebra (representation sweep).

**The COMPUTATION copied exactly** (PINNED): per-entity location STATE, updated only by MOTION events,
PERSISTING between updates; motion read off the realized **PATH satellite / Source-Goal-Path** with **deixis
dominating** (`come/return` toward the scene, `go/leave` away -- Talmy 1985; Papafragou 2008), **Goal-over-
Source** (a realized Goal names the destination even under an away-deixis: "went out *to the garden*" -> garden;
Lakusta & Landau 2005), and an explicit **RETURN satellite** ("back"/"again") overriding deixis. NOT a
manner-verb whitelist -- "she florped out" still departs via the satellite (witness).

**The REPRESENTATION swept** (OUR-INVENTION-UNDER-TEST, labelled): symbolic **topological scene nodes** (not
metric coordinates -- confirmed brain-faithful: Rinck, Hahnel, Bower & Glowalla 1997 rule out Euclidean
distance in narrative spatial models), plus the FHRR-bound alternative giving the same answer.

## What was measured
1. **"Where is X at T?"** (`exp_location_register_where_is_x_v1`, n=240 construction gold: real motion verbs,
   by-construction node labels, four discriminating structures). REGISTER **1.000 [1.000,1.000]** vs the
   strongest stateless floor last-mention-location **0.417 [0.354,0.479]** -- CI-separated. Info-free
   shuffled-order twin **0.422** (null p95 0.468) LOSES and sits exactly at floor. Robust across seeds 0/1/2
   (0.946-1.000, all HARD_PASS). Per-type positive controls: REENTRY/PERSIST/STALE/MULTIHOP register 1.000 vs
   last-mention 0.000/0.000/0.667/1.000.
2. **Distance-robustness** (`exp_location_register_distance_v1`) -- the sharpest mechanism control. REGISTER
   stays **0.967 flat at K=0,2,5,10,20** filler sentences; a 3-sentence WINDOWED register **collapses 0.967 ->
   0.000 at K>=2** and last-mention-location **1.000 -> 0.000 at K>=5**. Location is a maintained STATE, not a
   local read (parallels the ToM distance result).
3. **Serves the ToM observation cue** (`exp_location_register_serves_tom_v1`, real mined LitBank presence
   clauses, n=246). Feeding the register's presence bit in place of the inline stopgap: cue accuracy
   **0.972 [0.947,0.992]** vs lexical floor 0.500 (CI-separated) and e2e belief accuracy 0.972 through the
   landed `hdlab.belief_partition`. Presence-bit agreement with the stopgap 0.967 overall, **0.985 on the
   presence-decisive classes** (depart 1.000, present 0.988, occlude 0.961).
4. **Real-prose extraction gate** (`exp_location_register_verbclass_gate_v1`, 186 real LitBank "to X" tokens).
   The ATL place-typing + VerbNet motion-frame gates raise Goal-extraction precision **0.219 -> 0.909** and
   drive communication-verb false-goals **0.573 -> 0.000** (n=96 -- the dominant real-prose false-positive
   source, "said/told/gave *to X*"). Ambiguous caused-motion stays 0.167 (the mapped residual).

## The wall I drilled (owner: "if the brain can do it, we should be able to also")
Running the register on RAW literary prose exposed a precision wall: a bare "to X" PP was read as a spatial
Goal regardless of the verb, so "said **to** Alice", "gave it **to** her", "pointed **to** the door" (X =
ADDRESSEE/RECIPIENT) were mis-read as relocations, and abstract grounds ("broke into a **laugh**", "in high
**feather**") were mis-typed as places. **The brain resolves this with the verb's EVENT FRAME plus semantic
type of the ground** -- VerbNet encodes exactly this as two thematic roles, **Destination** (+concrete
location, self-motion verbs) vs **Recipient** (+animate, communication/transfer verbs); the anterior temporal
lobe supplies "kitchen is a place, laugh is not". I built three glass-box gates that copy this:
- **ATL place-typing** (`is_place_ground`): WordNet location-hypernym + a curated scene lexicon.
- **VerbNet motion-frame gate**: a bare goal PP is a destination only if the verb evokes self-motion and is
  not a communication/transfer verb; **PATH satellites bypass it** (florped out -- no manner-verb whitelist).
- **Argument-structure gate**: a goal PP with a competing moved-theme direct object is the OBJECT's path, not
  the agent's ("struck **them** to the ground" -> them moves, agent stays).
Result: raw-prose false motion-reads fell **51 -> 6**, precision **0.22 -> 0.91**. A literature drill
(`research_motion_goal_vs_addressee_...md`) confirmed this is the standard account (Rappaport Hovav & Levin
2008; Levin 1993) and that the one irreducible residual -- **ambiguous caused-motion verbs** (throw/send/pass),
where verb class carries zero signal -- needs the **coreference/entity-status** of the "to X" head (character
-> Recipient, location -> Goal), a mapped follow-on, not WordNet animacy typing.

## What I did NOT establish (withdraw-first if wrong)
- **The CI-separated "where is X" headline is on a CONSTRUCTION gold** (real English motion verbs + real place
  nouns, but synthetic multi-location threads with by-construction labels), NOT fully-natural LitBank prose.
  It isolates and proves the TRACKING mechanism (intervals, PATH/deixis/Goal-over-Source, persistence). I did
  NOT run a fully-natural raw-prose "where is X" CI-eval because on unrestricted prose the **extraction-precision
  wall** (Goal-vs-Addressee, argument structure, coref ~0.65) would dominate the tracking signal, and an
  auto-mined natural gold would be as noisy as the mechanism (circular). Real-PROSE evidence is instead the
  serve (0.972 on real mined clauses) + the gate precision (0.909 on 186 real tokens) + hand-verified real
  tracking (the register correctly reads "Alice ... swam **to the shore**" -> shore; "Alice went ... **to the
  door**" -> door; "Holmes dashed **into the crowd**" -> present-elsewhere). **First thing I would withdraw if
  wrong:** any implied claim that the register handles UNRESTRICTED natural narrative at construction-gold
  accuracy -- it handles the TRACKING at that accuracy given clean motion events; raw-prose EXTRACTION is
  0.909-precision with a mapped residual.
- The FHRR representation is a demonstration that the register composes with the binding algebra (round-trips
  at cos 1.000 on a small codebook), NOT a claim that a dense FHRR store scales to many entities x locations.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
The §2b ToM entry names "NO SPACE dimension in the situation model ... a genuinely MISSING organ (highest-
leverage adjacency)". **This is now BUILT and validated in experiments/ (proposed for hdlab landing).** New
entry recommended: **Location register / event-indexing SPACE dimension** -- brain structure: Zwaan &
Radvansky event-indexing SPACE (PINNED) + hippocampal place / entorhinal grid allocentric map + parahippocampal
(Speer & Zacks 2009). Our fidelity: presence-interval + PATH-satellite/deixis/Goal-over-Source computation
COPIED (PINNED); representation = topological scene nodes (categorical, NOT metric -- Rinck 1997), FHRR-
compatible. Deviations to record: (a) SPACE is the WEAKEST/most-effortful event-indexing dimension (Zwaan,
Langston & Graesser 1995) -> the register should be **lazy/on-demand**, which our design already is (updates
only on motion, queries on demand); (b) raw-prose motion EXTRACTION is gated at 0.909 Goal precision, residual
= ambiguous caused-motion needing coref/entity-status.

## Adjacent-component bottlenecks (mapped, not silent gaps)
- **coreference_resolver (~0.65 on real narrative)** -- binds a mention to the tracked entity whose location
  updates. On real prose this caps recall and is half of the "who moved" signal. Evidence: the register uses
  gold aliases in the controlled eval and the ToM gold-coref surfaces in the serve; unrestricted prose needs
  honest coref. **Leverage: the ambiguous-caused-motion Goal-vs-Recipient residual is resolved by the entity-
  STATUS of the "to X" head (character vs location) -- a direct coref consumer.** Candidate follow-on.
- **A predicate-argument / thematic-role front-end (SRL)** -- the residual raw-prose extraction errors are
  argument-structure ("eased *them* to the ground" = the theme falls; participial "went *on*" = continue).
  A shallow SRL that marks the agent as the moving theme would close most of the residual. Candidate follow-on.
- **situation_model_accumulate event-slot advance** -- a spatial shift IS an event boundary (Zwaan); the
  register's departures/arrivals are a free boundary signal that could advance the event slot. Candidate wiring.

## Proposed hdlab landing (strategy lands; Q111 -- I do not write hdlab/)
1. **Promote `experiments/location_register.py` -> `hdlab/location_register.py`** as a first-class organ:
   `LocationRegister.read(text, entities)` / `where_is` / `present_in_scene` / `intervals_of`, with the three
   glass-box gates (place-typing, motion-frame, argument-structure) ON by default.
2. **Have the queued `perceptual_access` landing CONSUME it** instead of re-implementing the inline
   `PresenceState` stopgap (`experiments/perceptual_access_ledger.py`): the register supplies the presence/co-
   location bit (serve shows 0.985 decisive-class agreement, 0.972 composed cue). Removes the inline
   re-implementation the ToM solver flagged.
3. **Keep it FHRR-compatible** (bind current node via `RelationRegister`) so the SPACE dimension composes with
   the `(entity, role, event)` binding rather than replacing the register.
4. **Do NOT** adopt a metric-coordinate representation (Rinck 1997: narrative space is categorical) or an
   eager per-entity-per-event maintenance (Zwaan 1995: SPACE is the most effortful dimension -> lazy).

## KEY REALIZATIONS (the enabling moves)
1. **The ToM stopgap had the OPERATION but the wrong GRANULARITY.** Its binary present/absent `PresenceState`
   collapsed every room to "the scene"; a register that answers *where* had to distinguish named nodes ("his
   room" upstairs != the parlour) AND extract the **Goal** ground under an away-deixis ("went out *to the
   garden*" -> garden). Generalising, not copying, the stopgap was the whole build.
2. **The info-free twin landing exactly AT the floor (0.42 ~ 0.42), not below it, is the cleanest proof:**
   destroying temporal order collapses the register precisely to the stateless heuristic, so 100% of its
   advantage is correctly-ordered tracking. A twin that lost by a *little* would have been weaker evidence.
3. **The real wall was not tracking, it was EXTRACTION.** On raw prose the register works when the motion is
   read correctly; the failure was reading "said **to** Alice" as motion. The fix is the brain's actual
   mechanism -- VerbNet Destination-vs-Recipient verb frames + ATL place-typing -- not a bigger lexicon. This
   is the "shared wall = go deeper" lesson: every angle plateaued until I asked how the brain tells a Goal from
   an Addressee, which is a *verb-semantics* question, not a *tracking* one.
4. **A construction gold with real verbs + a real-prose SERVE + a real-prose gate ablation triangulate what a
   single natural-prose eval could not** -- the construction gold isolates tracking (power), the serve proves
   real-prose usefulness (presence), the ablation proves the gates and quantifies the residual wall. Refusing
   to fabricate a noisy auto-mined natural "where is X" gold (which would be as noisy as the mechanism) was the
   honest call.

## TLDR
The reader could bind *who did what* but had no track of *where each character is*. I built that missing track:
a per-character location register that updates when someone moves (reading direction words like "out", "back",
"upstairs" and verbs like come/go the way the brain does), and remembers where they are across the whole story.
Asked "where is X now?", it is right ~100% of the time on a controlled test versus ~42% for the best guess that
just looks at the last place mentioned, a scrambled-order version fails (so the skill is really the tracking),
and it stays right no matter how many sentences pass since the move (the best guess collapses to 0%). Feeding
it into the mind-reading module reproduces that module's win (97% vs a 50% keyword floor) and lets us delete a
temporary stand-in. Running it on real novel text, I hit a wall the brain also has to solve: telling "went **to**
the door" (a move) from "said **to** Alice" (talking to someone). I fixed it the brain's way -- using the verb's
meaning (motion verbs vs speaking verbs) and knowing a "laugh" isn't a place -- raising accuracy on that
distinction from 22% to 91%, with the last hard case (throw/send/give) needing the character-tracking module to
finish it off.

## QUESTIONS
None.

## NEXT STEPS
1. Strategy: re-verify + land `hdlab/location_register.py` (default-on gates) and point the queued
   `perceptual_access` landing at it instead of the inline stopgap.
2. Follow-on problem: **resolve the ambiguous caused-motion Goal-vs-Recipient residual via coref/entity-status**
   (character vs location) -- a direct `coreference_resolver` consumer; and a shallow SRL for the remaining
   argument-structure extraction errors.
3. Optional wiring: use the register's spatial shifts as an event-boundary signal to advance
   `situation_model_accumulate`'s event slot (a spatial shift IS an event boundary, Zwaan).
