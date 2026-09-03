---
problem: wire_the_copular_state_qa_consumer_and_turn_on_bind_entity_states
status: SOLVED
bar: "PASS = a live `qa_state` per-dimension row on the baseline board (Instrument A) that scores CI-separated over the copular problem's validated most-recent-noun floor (0.503) with a shuffle twin LOSING (reuse the copular SOLVED's floor/twin so the row carries a CI -- do NOT invent a degenerate gold), AND a non-negative move on `qa_aggregate` (today 0.36), AND `bind_entity_states` turned ON (default-on) since it is now net-positive on a consumed metric. Report CI half-width + null p95. Expected `qa_state` ~= 0.67 within-clause vs floor 0.50. A rigorous located NEGATIVE -- the register read-out does NOT beat the floor live -- is a FULL PASS with the named cause. Also run the reader-QA before/after to confirm no other-dimension regression."
result: "The wired STATE-QA consumer (route 'what/who is X' -> state dim -> sm.state_register.state_at readout) scores qa_state MODEL = 0.7116 on 378 predicational copular clauses (UD-EWT copular gold, NON-CIRCULAR = gold from GOLD deprels), CI-separated +0.1402 [+0.0868,+0.1958] hw=0.0545 nullp95=0.0544 over the recomputed most-recent-noun floor (0.5714 on the predicational subset; 0.503 on all-gold in the copular SOLVED), with the info-free SHUFFLE-HOLDER twin (0.49-0.50) LOSING +0.2090 [+0.164,+0.255] CI-sep. Live can-fail: the base reader (bind_entity_states OFF) scores 0/378 (no state register). Router 'what is X' -> state hit 1.000 (cue-table AND wh-ontology); ablating the frame collapses the answer to 0. yes/no 'Is X a Y?' 0.7143. UPSTREAM-FIX ladder through the SAME consumer (both REQUIRED): label path 0.7116 -> +robust_cop 0.8333 (+0.1217 [+0.091,+0.155] CI-sep) -> +arc-eager tree 0.8651 (+0.0317 [+0.016,+0.051] CI-sep), concentrated on is-a (pred_nom 0.621 -> 0.806 -> 0.903)."
floor: "Strongest floor actually run, recomputed on the SAME predicational population = most-recent-noun / parse-free positional binding (COP.positional_floor / extract_entity_states_positional): 0.5714. (The copular SOLVED's validated all-gold value is 0.5033; on the predicational subset it recomputes to 0.5714.) The MODEL beats it CI-separated +0.1402."
controls: "(1) SHUFFLE-HOLDER twin (copular-validated info-free: keep the property, bind a random preceding nominal) -> excludes 'the holder binding is noise' (loses CI-sep +0.209). (2) ROUTER ABLATION (disable the copular frame -> the question falls through to events) -> collapses to 0 -> excludes 'the router wire is not load-bearing'. (3) BASE READER OFF (bind_entity_states=False) -> 0/378 (no state register) = the live can-fail zero the wire beats. (4) NO-REGRESSION: the 4 scored LitBank dims (events/coref/timeline/causal) are BYTE-IDENTICAL on the capable reader with the flag OFF vs ON -> excludes 'turning it on regresses the other dims' (the flag is additive). (5) WATERFALL: read-back GIVEN the binding = 0.9963, routing = 1.000 -> excludes 'the consumer loses signal' (the residual is UPSTREAM detection). (6) per-Higgins-type split (pred_adj 0.746 vs pred_nom 0.621) -> the loss is concentrated in is-a, and the upstream fix recovers it most (+0.184). Each control excludes a specific alternative."
files_changed: "experiments/exp_situation_model_state_qa_v1.py (NEW -- the powered NON-CIRCULAR state-QA consumer over the copular UD-EWT gold: model vs floor vs shuffle-twin + router-ablation + base-off zero + waterfall + upstream-fix arm + LitBank live-fires + board_state_dimension). experiments/exp_situation_model_qa_v1.py (the WIRE: DIMENSIONS+='state'; the brain-faithful copular-FRAME router _is_state_frame + route/wh_ontology_route state_frame short-circuit; SituationQA._answer_state + readout dispatch; build_state_questions; build_reader flips bind_entity_states=True; run() injects per_dimension['state'] + aggregate_including_state via a lazy import of the state cell; _selftest asserts the state dim + router guards). verification/test_state_qa_consumer_organ.py (NEW -- scaffold-free 8/8 witness). REUSES verbatim (unmodified): experiments.exp_copular_is_a_binding_readout_v1 (typed_gold / positional_floor / shuffle_twin / robust_cop / predicted_type), hdlab.state_register.StateRegister, hdlab.copular_binding, hdlab.situation_reader (bind_entity_states). NO hdlab/ file changed -- proposed default-on diff below (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_state_qa_consumer_organ.py   (9/9, all recomputed from source)"
---

## INTEGRATED_BY_STRATEGY (2026-09-03) — EXCELLENT
Reverified first-hand: `verification/test_state_qa_consumer_organ.py` **9/9** PRE-landing (base OFF=0; qa_state 0.7011 CI-sep +0.140 over floor; shuffle twin loses; router 1.000/ablation 0; no-regression 4 dims byte-identical; waterfall read-back|binding 0.992; LitBank 295/296; label 0.701→robust_cop 0.826→arc-eager 0.848 each CI-sep). Bar met the brain-foundational way (content-addressable retrieval → mental-model read-out). **BOTH REQUIRED CHANGES LANDED (Q111):**
- **CHANGE 1 — consumer wire + turn ON:** the state-QA consumer lives in `experiments/exp_situation_model_qa_v1.py` (already on disk); flipped `bind_entity_states` **DEFAULT-ON** in `hdlab/situation_reader.py` (no-default-off: net-positive on a CONSUMED metric, PURELY ADDITIVE — 4 scored dims byte-identical off vs on, qa_aggregate 0.2811→0.4657, +~5ms/read).
- **CHANGE 2 — upstream detection fix:** promoted `robust_cop` (label-ROBUST closed-class copula detector) VERBATIM → `hdlab/copular_binding.py`; unioned it into `_read_entity_states` (`bind | robust_cop`). Measured FIRST-HAND through the LIVE reader: **qa_state 0.7011 → 0.826 CI-sep** (concentrated on is-a pred_nom +0.184).
- **Witnesses:** `test_copular_is_a_binding_landing_organ.py` 6/6 (default-ON [0] + union [3] byte-exact + read-back + factory-off); `test_state_qa_consumer_organ.py` 9/9 (W9 made landing-aware — robust_cop is now the reader default, arc-eager +0.032 on top). Registered `copular_state_qa_consumer_and_robust_cop_wire_v1`. §2b AUDIT UPDATE folded.
- **OPTIMIZATION NOT LANDED (modern-only): arc-eager tree** stacks +0.032 (→0.848) but is 19c-negative → needs PER-REGISTER parser routing; deferred as a measured follow-on. Two brain-differences remain filed follow-ons (cross-sentence canonical-entity binding; identity→coref-merge).

# SOLVED -- the copular is-a/attribute capability now has a LIVE QA CONSUMER, proven net-positive on a consumed metric (qa_state CI-separated over the validated floor, twin losing), no other-dimension regression, and the flag is ready to turn ON

**Status: SOLVED (WIP until `owner_verdict: DONE`).** Glass-box, NO external LLM at inference (the invariant). NO
`hdlab/` file changed -- the producer already landed; this is the EXPERIMENTS-side consumer wire, and the one-line
hdlab default-on flip is the proposed diff for strategy (Q111). Witnessed scaffold-free **9/9** (both required
changes verified from source).

## The opening move -- how the BRAIN does this, replicated exactly
A copular predication ("Ahab is the captain", "the room is cold") binds the complement PROPERTY/CATEGORY to the
subject's ENTITY NODE (Higgins 1979 predicational vs identificational; Maienborn 2005 Kimian states; Bemis &
Pylkkanen 2011 LATL property attribution ~200-250ms), filed on the ENTITIES dimension of the situation model
(Zwaan & Radvansky 1998 = the queryable discourse memory, hippocampal/DMN). Later "what was he?" is answered by
CONSULTING that stored record -- a mental-model READ-OUT (Glenberg 1987; Kintsch 1988) -- NOT by re-scanning the
text. The question SELECTS the store by content-addressable retrieval (Lewis & Vasishth 2005): "what/who is X" is
a cue whose answer-type (a property of X) matches the entity-state store and wins the retrieval race.
**I copy that computation exactly:** route "what/who is X" (the cue) -> the entity-state store
(content-addressable) -> read `state_at(holder)` (query the model, never re-read). PINNED: the routing = cue-based
retrieval; the readout = the mental-model read-out. OUR-INVENTION-UNDER-TEST (labelled + swept): the surface
copular-FRAME detector, the templates, the abstain policy. The discrete register (holder -> {values}) is the
producer's OUR-INVENTION primitive, which I only CONSUME.

## Organ match -- I reused, I did not reinvent
`hdlab.state_register.StateRegister` is the EXACT sibling of `hdlab.location_register.LocationRegister` (where)
and `hdlab.world_state_register.WorldState` (who-has-what) -- the per-entity attribute-register family (the
Zwaan-Radvansky situation-model dimensions). So the state-QA consumer I built is the ENTITY-STATE sibling of the
EXISTING situation-model QA dimensions (coref / events / temporal / causal / location / belief) in
`exp_situation_model_qa_v1`. There is no better-matching organ; the wire is the same cue->store->read-out pattern.

## What I built (the CONSUMER, experiments-only)
1. **`_is_state_frame` + the router short-circuit** (in `exp_situation_model_qa_v1`): a brain-faithful copular
   FRAME detector -- "what/who is X" / "is X a Y" routes to the entity-STATE dim in BOTH routers (cue-table
   `route` and `wh_ontology_route`). Structural (not a cue word) -> paraphrase-invariant, generalizes to unseen
   holders/properties. Gated to NOT steal the existing dims: not where/when/why (own dims), not a salience
   question ("who is the MAIN character"), not a pronoun-holder "who is he" (= coref/identity), not a question
   with another main/mental/causal/temporal verb.
2. **`SituationQA._answer_state`**: reads the is-a/attribute OFF `sm.state_register.state_at(holder)` -- never
   re-reads the text (the same discipline as the temporal/causal readouts).
3. **`build_state_questions` + `bind_entity_states=True` in `build_reader`**: the consumer's reader now populates
   `sm.entity_states` + `sm.state_register` (additive; +~5ms/read).
4. **`run()` injects `per_dimension['state']`** (auto-visible on the baseline board's Instrument A, which iterates
   `res["per_dimension"]`) + `aggregate_including_state` -- via a lazy import of the powered state cell.
5. **`exp_situation_model_state_qa_v1`**: the powered, NON-CIRCULAR measurement + all controls + the waterfall +
   the upstream-fix prototype + the LitBank live-fires demo.

## The result (the bar, met with power) -- `exp_situation_model_state_qa_v1`, UD-EWT copular gold, n=378 predicational
| arm | qa_state | vs floor / vs twin |
|---|---|---|
| most-recent-noun FLOOR (recomputed on predicational) | 0.5714 | -- |
| info-free SHUFFLE-HOLDER twin | 0.49-0.50 | -- |
| **MODEL (route + state_register read-out)** | **0.7116** | **+0.1402 [+0.087,+0.196] hw=0.055 nullp95=0.054 CI-sep over floor; +0.209 over twin CI-sep** |
| base reader OFF (bind_entity_states off) | **0.0000** | the live can-fail zero the wire beats |
| **+ UPSTREAM FIX (label-robust detection)** | **0.8333** | **+0.1217 [+0.091,+0.155] CI-sep over the label path** |

- Router "what is X" -> state: **1.000** (cue-table AND wh-ontology). Ablating the frame -> **0** (load-bearing).
- yes/no "Is X a Y?" (via `is_in_state(semantic=True)`): 0.7143.
- Per Higgins type: pred_adj 0.7455, pred_nom (is-a) 0.6214 -> the loss is concentrated in is-a.

## Non-circularity -- the decisive design choice (DISK OUTRANKS THE BRIEF, stated openly)
The brief's step 1 suggests gold from `sm.entity_states` (the reader's own extraction). **That would be a
degenerate/circular gold** (model == gold source -> ~1.0), which the brief itself forbids. On LitBank there is NO
independent copular gold (no gold deprels), so ANY transparent LitBank gold collides with the positional floor
(circular). So the powered, honest instrument is the copular problem's **UD-EWT typed gold** (from GOLD deprels --
`COP.typed_gold`): gold is INDEPENDENT of the reader's parse, the model can MISS a clause (detection recall), and
model_acc = 0.7116 < 1. This is exactly what "reuse the copular SOLVED's floor/twin so the row carries a real CI"
points at. **Consequence for the board:** the `qa_state` row is population-tagged `UD-EWT copular gold
(predicational)`, NOT LitBank -- a deliberate deviation from the brief's implicit "LitBank like the other dims,"
made because the LitBank alternative is circular. The on-corpus (19c) demonstration is the LIVE-FIRES section below.

## How we compare to the brain, and EXACTLY where we differ (the waterfall)
| stage | brain | us | loss |
|---|---|---|---|
| reference | ~1.0 (a fluent reader always answers a clear copular clause, cross-sentence) | -- | -- |
| 1 BINDING (upstream producer) | holistic/incremental | **0.7116** | **-0.29 -- the arc-labeler `cop`-recall on hard equatives/clefts** |
| 2 ROUTING (the consumer) | cue-based race | **1.000** | 0 |
| 3 READ-BACK given binding (the consumer) | mental-model read-out | **0.9963** | ~0 |

**The consumer adds ~zero loss** (routing 1.0, read-back 0.996) -- it is at the brain's ceiling GIVEN the binding.
The entire residual to the brain is (a) UPSTREAM detection (the producer's mapped `cop`-recall gap), (b)
within-clause SURFACE-TOKEN keying vs the brain's cross-sentence CANONICAL-ENTITY binding (hippocampal concept
cells reactivating across coref; Dijksterhuis 2024 -- a filed follow-on), and (c) identity copulas routed to
coref-merge (symmetric/CA3), not the property store (a filed follow-on).

## The wall I hit, understood deeply, and the brain-faithful fix
First full pass, the model barely beat the floor. Diagnosed EXACTLY: the router dropped 19% of questions -- the
PRONOUN-holder ones ("what is *it*?"), because a non-pronoun gate (meant to keep "who is he" = coref out) wrongly
excluded them. **The brain-faithful discriminator is the wh-word's answer-type** (Higgins; Cysouw language
universal): "WHAT is X" asks a PROPERTY of X -> the state store, for ANY holder (the register keys the surface
token 'it'; the brain would resolve 'it' to its referent first, which our within-clause keying handles because
the register keyed 'it'); "WHO is X" with a pronoun asks IDENTITY -> coref. Splitting the gate by wh-word lifted
routing 0.81 -> 1.000 and the model 0.45 -> 0.712 (CI-sep). The wall was a router fidelity gap (conflating a
property query with an identity query), closed by the brain's own distinction -- NOT a ceiling.

## The upstream fix, prototyped AND optimized (the residual is upstream, so I closed most of it)
Because the consumer is lossless, ANY upstream binding gain flows straight through. I prototyped the producer's
PINNED brain-faithful fix, then OPTIMIZED it with a better parse tree -- an upstream ladder, all CI-separated,
all measured at the consumer:

| upstream config (brain-faithful) | qa_state | pred_nom (is-a) | step |
|---|---|---|---|
| label `cop` path (the landed default) | 0.7116 | 0.6214 | -- |
| **+ `robust_cop`** (copula is closed-class -> don't gate on the fragile label; read off the tree) | **0.8333** | 0.8058 | **+0.1217 [+0.091,+0.155] CI-sep** |
| **+ arc-eager TREE** (rely on an accurate tree, not a label workaround) | **0.8651** | **0.9029** | **+0.0317 [+0.016,+0.051] CI-sep** |

- **`robust_cop`** reproduces the producer's validated +0.10 adjectival / +0.18 is-a EXACTLY, now at the consumer;
  its own shuffle twin loses (+0.283 CI-sep).
- **arc-eager** adds a FURTHER +0.032 CI-sep ON TOP of `robust_cop`, concentrated on the NOMINAL is-a
  (pred_nom 0.806 -> 0.903; pred_adj flat). NEW finding vs the producer (who found arc-eager ~ns on top of the
  fix on ALL gold): on the PREDICATIONAL subset the better tree specifically fixes the nominal is-a attachment.
  ⚠️ arc-eager is a MODERN lever (measured on UD-EWT); the substrate note flags it 19c-NEGATIVE, so it is
  modern-only -- do NOT default it on the 19c reader (route it per-register).
- Net: the upstream ladder takes the LIVE consumer 0.712 -> **0.865** (of a brain ceiling ~1.0), closing 53% of
  the gap that remained after the consumer, entirely via better UPSTREAM detection (the consumer never changed).

## No-regression + qa_aggregate + turning the flag ON
- **NO-REGRESSION (witnessed):** the 4 scored LitBank dims (events/coref/timeline/causal) are BYTE-IDENTICAL on
  the capable reader with `bind_entity_states` OFF vs ON -- the flag is purely additive (it only writes
  `entity_states`/`state_register`).
- **qa_aggregate:** the 4-dim LitBank aggregate stays **0.3598** (unchanged = non-negative, no regression; I did
  NOT dilute it with the cross-population state row). The UNION aggregate over {4 LitBank dims + the state dim}
  moves **0.3147 (flag off, state scores 0) -> 0.4039 (flag on)** = +0.089 -- turning the flag on lifts the
  consumed aggregate because a whole 0/N dimension becomes 0.71.
- **TURN IT ON:** the flag is now net-positive on a consumed metric (`qa_state` CI-sep, twin losing, no
  regression), so per the no-default-off rule it should be default-ON. The one-line hdlab flip is the proposed
  diff below (Q111 -- strategy lands hdlab).

## LIVE-FIRES on real 19c prose (the reading corpus)
On 25 real LitBank docs the wired consumer answers **527/530** "what is X" state questions the base reader could
not (0 answerable with the flag off). HONEST CAVEAT: the LitBank gold is READER-DERIVED (no independent copular
gold on LitBank), so this is a COVERAGE / round-trip demonstration that the consumer fires on 19c narrative, NOT a
floor-beating capability claim -- the powered, non-circular capability number is the UD-EWT qa_state above.

## BOTH CHANGES ARE REQUIRED (not one-or-the-other) -- explicit for the integrator
This submission delivers, and REQUIRES landing, **TWO** coupled changes. The first CLEARS the bar (makes the
capability answerable + turns the flag on); the second is REQUIRED to make it ACCURATE (it closes the mapped
upstream residual the waterfall isolated). Landing only the first leaves 0.833-0.712 = **+0.12 of proven,
CI-separated capability on the table**, concentrated exactly on the is-a sentences the label parser misses.

1. **CHANGE 1 -- the CONSUMER wire + turn the flag ON (clears the bar).** The router frame + `_answer_state` +
   `build_state_questions` live in `experiments/exp_situation_model_qa_v1.py` (ready). The hdlab action: flip the
   `bind_entity_states` DEFAULT to True in `hdlab/situation_reader.py` (add it to the 2026-09-03 default-ON set,
   or `bind_entity_states: bool = True` in `__init__`). Justification: net-positive on a CONSUMED metric
   (`qa_state` 0.712 CI-sep over the floor, twin losing), additive (4 scored dims byte-identical off vs on),
   +~5ms/read -> satisfies the no-default-off rule.
2. **CHANGE 2 -- the UPSTREAM detection fix (REQUIRED to make it accurate).** Adopt the producer's PINNED
   label-robust `robust_cop` on the entity-state detection route in `hdlab/situation_reader._read_entity_states`
   (fire on the closed-class copula token + read holder/property off the tree, union with the label path).
   Justification: because the consumer is LOSSLESS (read-back|binding 0.996), this flows straight through:
   `qa_state` 0.712 -> **0.833 CI-sep**, concentrated on is-a (pred_nom +0.184). The producer's operating-point
   split holds (the high-precision label path stays the default; expose `robust_cop` as the recall-max detection
   for the entity-state route). This is NOT optional polish -- it is the mapped residual, and it is proven.
   **OPTIMIZATION (modern-only):** stack the arc-eager TREE on top of `robust_cop` for a further `qa_state`
   0.833 -> **0.865 CI-sep** on the nominal is-a (pred_nom 0.806 -> 0.903). Route it PER-REGISTER (arc-eager is
   19c-negative per the substrate note), so: 19c reader = `robust_cop` on the July tree; modern reader =
   `robust_cop` on the arc-eager tree.
3. The state-QA CONSUMER itself lives in `experiments/`; if a first-class `SituationReader.answer_state(holder)`
   API is wanted in hdlab later, the reference impl is `SituationQA._answer_state` + `_is_state_frame`.

## What I did NOT establish / what I would withdraw first
- **The `qa_state` row is on UD-EWT (modern), not 19c LitBank** -- because a LitBank copular gold would be
  circular. The 19c evidence is the live-fires COVERAGE (527/530), not a floor-separated 19c capability number.
  **Withdraw first:** any claim that `qa_state` is a 19c number -- it is modern (UD-EWT); 19c is coverage-only.
- **CROSS-SENTENCE "what is Ahab (later 'he')" does NOT round-trip** -- the register keys on the SURFACE holder
  token (within-clause). Cross-sentence canonical-entity binding is a SEPARATE filed follow-on (the producer's
  decisive limitation, confirmed here).
- **Identity copulas ("she is his wife") are excluded** -- only predicational (pred_adj/pred_nom) states are
  applied to the register; identity -> coref-merge is a separate filed follow-on.
- **The floor recomputes to 0.5714 on the predicational subset** (vs 0.5033 on all-gold in the copular SOLVED) --
  I gate on the recomputed 0.5714; the +0.140 margin is CI-separated on the item's own population.

## KEY REALIZATIONS (the enabling moves)
1. **The consumer is lossless; the residual is upstream.** The waterfall (read-back|binding = 0.996, routing =
   1.0) LOCATED the entire gap to the brain in the producer's binding -- so "optimize the consumer" is the wrong
   move; closing the UPSTREAM detection (the label-robust fix) is what lifts `qa_state` (0.712 -> 0.833).
2. **The wh-word sets the answer-type -- that is the router.** The pronoun-holder wall dissolved once I routed by
   Higgins answer-type: WHAT-is-X = property (state, any holder), WHO-is-pronoun = identity (coref). A structural
   frame, not a keyword -- so it generalizes to unseen wordings.
3. **On LitBank the honest gold does not exist, so the non-circular instrument is UD-EWT.** Recognising that any
   LitBank state gold collides with the positional floor (circular) is what kept the row honest -- the brief's
   "reuse the copular floor/twin" was pointing at the UD-EWT gold all along.
4. **Reuse beat reinvention.** `StateRegister` is the sibling of the location/world-state registers, and the
   consumer is the sibling of the existing QA dimensions -- so the whole wire is ~120 lines of consumer, zero new
   organ.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec.2b)
- **The copular is-a/attribute capability now has a LIVE QA CONSUMER** (route "what/who is X" -> entity-state
  store -> `state_at` read-out), proven net-positive on a consumed metric: `qa_state` 0.7116 CI-sep +0.140 over
  the most-recent-noun floor (0.5714 predicational), shuffle-holder twin losing, base reader OFF = 0. PINNED: the
  routing is content-addressable cue retrieval (Lewis & Vasishth 2005), the readout is the situation-model
  read-out (Zwaan & Radvansky 1998; Glenberg 1987). `bind_entity_states` is additive (4 scored dims byte-identical
  off vs on) and should turn DEFAULT-ON.
- **The consumer is LOSSLESS; the residual to the brain is UPSTREAM detection** (read-back|binding = 0.996,
  routing = 1.0). The label-robust `robust_cop` fix flows through the consumer: `qa_state` 0.712 -> 0.833 CI-sep,
  concentrated on is-a (pred_nom +0.184). Refines the copular entry: the entity-state READ-OUT is at ceiling given
  the binding; the lever is the producer's detection recall, not the consumer.
- **Two remaining brain-differences are filed follow-ons:** within-clause SURFACE-TOKEN keying vs cross-sentence
  CANONICAL-ENTITY binding (hippocampal concept cells), and identity->coref-merge (symmetric/CA3).

## TLDR (plain language)
A lot of what a story tells you is not an action but a fact about someone or something -- "Ahab was a captain",
"the room was cold". The reader had recently learned to record such facts, but nothing in the reading test ever
ASKED about them, so the ability sat switched off (it would cost a little effort for no measured benefit, and the
rules here forbid switching something on with no measured benefit). I built the missing question: the reading test
now asks "what is X?" and grades the answer by looking it up in the reader's memory of the story -- never
re-reading the text, which is how a person answers. It gets the right answer 71 times in 100, well above the best
simple guess (nearest noun, 57), while a scrambled version does much worse -- so the signal is real. Switching the
ability off makes the score drop to zero (nothing to look up), which is the proof it is doing the work. Turning it
on does not harm anything else the reader already does (identical results on the other four question types). I also
checked exactly where we still fall short of a human: it is NOT in the looking-up (that is essentially perfect) --
it is one step earlier, in spotting the "is a" sentence in the first place. So I prototyped the fix to THAT step
(don't rely on a fragile grammar label; find the linking word directly), and the score jumped from 71 to 83, with
the biggest gain exactly on the "is-a-kind-of" sentences that were failing worst. On old-fashioned prose the
ability answers 527 of 530 questions the old reader could not.

## QUESTIONS
None blocking. One transparency call, flagged: the headline `qa_state` number is measured on MODERN
grammar-annotated text (the only place an honest, non-circular "is-a" gold exists), not on the 19th-century novels
the rest of the reading board uses; on the novels I can only show that the ability now fires (527/530), not a
clean above-a-baseline score, because those texts have no independent "is-a" answer key. If you want a
floor-separated 19c number, it needs a small hand-annotated 19c copular gold (a modest, separable task).

## WHERE THE SIGNAL IS LOST, RANKED -- and the exact further-optimization step for each
The CONSUMER is lossless (routing 1.0, read-back|binding 0.996), so every remaining loss is UPSTREAM or a
capability the register does not yet cover. Ranked by how much real-reading signal it costs:

| # | where the signal is lost | measured | brain does it by | the FURTHER-OPTIMIZATION STEP | owner |
|---|---|---|---|---|---|
| 1 | **CROSS-SENTENCE** -- the register keys the SURFACE token, so "what is Ahab" fails once he is "he"/"the captain" | within-clause only (cross-sentence = 0 by construction); the producer measured **0.43 of predications become cross-sentence answerable** once bound to the coref entity | binds the attribute to the CANONICAL discourse referent (hippocampal concept cells reactivate across coref; Dijksterhuis 2024) | **key `state_register` on the coref entity, not the surface token** -- compose `_read_entity_states` with `run_match_or_allocate`; the producer's end-to-end binding already proved 0.43 answerable | filed follow-on (biggest real-reading lever) |
| 2 | **DETECTION of the hardest constructions** -- equatives / clefts / specificational-inversions the copula-anchored path still misses | after the ladder, `qa_state` 0.865; residual is these hard clauses + is-a attachment (pred_adj 0.851, pred_nom 0.903) | holistic/incremental detection from the closed-class copula, no full parse | **REGISTER-NATIVE parse/POS data** -- arc-eager already banked on modern (+0.032); the 19c hard residual needs 19c-native training data (arc-eager is 19c-negative) | the register-parse-data problem |
| 3 | **IDENTITY copulas excluded** -- "she is his wife" is typed `ident` and routed NOWHERE (not applied to the register) | 0% of identity clauses answerable via the state store (a whole excluded population, ~16% of copular clauses) | equative identity is a SYMMETRIC relational link (CA3 auto-association; Bunsey & Eichenbaum lesion) fed to coreference | **route identity copulas into coref-merge** (symmetric X==Y) -- the producer already emits the identity edge; wire it to the coref system | filed follow-on |
| 4 | **19c capability number does not exist** -- the powered `qa_state` is modern (UD-EWT); on 19c there is only coverage (527/530) | no floor-separated 19c number (a LitBank copular gold would be circular) | -- (a measurement gap, not a mechanism gap) | **a small hand-annotated 19c copular gold** (~200 clauses) converts the LitBank coverage into a floor-separated 19c `qa_state` | separable, modest |

## NEXT STEPS (the two REQUIRED landings first, then the ranked further-optimization above)
1. **REQUIRED -- CHANGE 1: turn the flag ON** (the one-line `bind_entity_states` default flip, Q111 -- strategy).
   Net-positive on a consumed metric, additive, +~5ms/read.
2. **REQUIRED -- CHANGE 2: adopt the label-robust upstream detection** (`robust_cop`) on the entity-state route:
   `qa_state` 0.712 -> 0.833 CI-sep, concentrated on is-a. Route the arc-eager optimization PER-REGISTER (modern
   +0.032 -> 0.865; 19c stays on the July tree). Both changes are proven and coupled -- land them together.
3. **FURTHER OPTIMIZATION (ranked in the table above):** (1) cross-sentence canonical-entity binding [biggest
   real-reading lever, 0.43 answerable]; (2) register-native parse data for the hardest-construction detection;
   (3) identity->coref-merge; (4) a small 19c copular gold to get a floor-separated 19c number.
