# STAGE-2 first learned component -- buildable design (brain-faithful, flexible/improving)

**Filed:** Director, 2026-07-18 (prep-to-fire while the 4-slice prior-art scour runs; refine with scour findings before firing). Governed by: keep-brain-faithful + flexible/improving-not-static ([[feedback_keep_as_close_to_brain_as_possible_flexible_improving_capability_not_static_USER_2026-07-18]]); sentences=reasoning-maps; learning=ingestion-efficiency.

## Goal of the first component
Replace ONE hand-rule in the reader with a LEARNED, coherence-scored component that emits into the FHRR HD reasoning-map (the Stage-1-validated target) -- and that KEEPS IMPROVING as it reads (grows/refines its construction inventory), NOT a trained-once-frozen parser. Fair can-fail vs the hand-rule baseline (D2 Stage-B: >=60% from a declared 0%).

## Brain-faithful shape (what to build ON -- confirm/adjust from the scour)
- COMPREHENSION LOOP backbone = Kintsch Construction-Integration (build candidate propositions -> integrate by coherence/spreading-activation -> keep the coherent ones). Our version: build candidate role-filler bindings for a sentence -> integrate against the situation-model-so-far -> keep the coherent map.
- LEARNED PARSE = usage-based CONSTRUCTION INDUCTION (Tomasello/construction grammar): induce form->meaning pairings (constructions) from grounded examples; the construction inventory GROWS + reweights with exposure (the flexible/improving property). NOT a supervised treebank parse.
- LEARNING SIGNAL = COHERENCE + GROUNDING + PREDICT-ERROR (brain-faithful, NOT next-token, NOT treebank labels): a parse is good iff (a) fillers are GROUNDED (known concepts), (b) the resulting map COHERES with the situation-model + known relations (schema-fit gate -- also the taxonomic-coherence gate for expository later), (c) it supports PREDICTION (predict the next piece of meaning; error corrects the construction). = the predictive/error loop the k-parity test justified for SELECTION.
- REPRESENTATION = FHRR role-filler binding (Stage-1 confirmed zero-training target).

## The one-variable can-fail cell (first step)
- REAL baseline = one current hand-rule component (candidate: the role-assigner OR a specific construction, e.g. the transitive SVO or the ditransitive give-X-to-Y).
- LEARNED arm = induce that construction from grounded examples + coherence-score; emit HD binding. Improves as more examples seen (report the LEARNING CURVE, not a single number -- the flexible/improving evidence).
- DIFFICULTY-ON = real grade-2/3 narrative (clean slice, fair bar); ONE VARIABLE = learned-vs-hand-rule for that construction, hold everything else.
- HARD-PASS = learned beats hand-rule (>=60% from 0%) AND improves with exposure (rising learning curve); HARD-FAIL = can't learn the construction from grounded signal alone (-> the grounded/coherence signal is insufficient, a real localization; may need more supervision or a different signal).
- MEASURE the flexible/improving property explicitly: capture-per-exposure rising as the construction inventory grows (ties to learning=ingestion-efficiency + the rational external-review metric).

## Extensibility (do NOT bake in narrative-only assumptions -- expository drill)
Keep the construction-inducer + coherence-gate + grounding EXTENSIBLE to the 4 later expository components: technical-term grounding-from-definitions, nominal/bridging coref, definition-as-construction + taxonomy-coherence gate, de-nominalization. (Narrative-first per the 4th-grade-shift, but the machinery must not wall these off.)

## Open (resolve from the scour before firing)
- WHICH existing system's construction-induction / semantic-parse-learning to BUILD-ON + CREDIT (scour slice 2 + 3): usage-based induction models? grounded semantic parsing from denotations? DIORA-style unsupervised? -- adopt the brain-faithful, self-improving one, adapt the engineering.
- WHICH VSA reading precedent to credit (scour slice 1): Semantic Pointer Architecture/Spaun binding+reasoning? HRR sentence encoding? -- for the representation + reasoning readout.
- WHETHER a system already does substantially this (scour slice 4) -- if so, adopt; if not, this is the genuine build.
NEXT: fold the 4 scours -> pick the brain-faithful/flexible prior art to build on -> refine this spec -> fire the can-fail cell.
