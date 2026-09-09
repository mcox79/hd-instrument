# PATH TO SOLVED — research SPECs for Phases A-D (2026-09-09, solver_opus48_causaltestimony)

The PARTIAL -> SOLVED plan, grounded in research. "Solved" = a full-population causal-antecedent SELECTION win on a
TRAP-PROOF instrument, CI-sep over the strongest floor, twin losing. Four barriers / signal-loss points:
(A) eval position-confound; (B) concept grain too coarse; (C) Gricean coverage gap; (D) end-to-end wiring.

## PHASE B SPEC — the brain-faithful UNIT of a cause->effect edge (research: causal_edge_grain, 6 converged literatures)
**VERDICT: predicate-argument frame `(verb, AGENT, PATIENT)` is the mandatory FLOOR; participant-attribute-value
STATE-change `(entity, attribute, value)` is the TARGET. Bare content words are INDEFENSIBLE (information-losing).**
- Schank-Abelson CD: the RESULT of an ACT is a bound STATE on a scale (health/physical/mental) with a VALUE, tied to a
  specific object -- never a free word. Dowty CAUSE(x,BECOME(state(y))); Jackendoff CAUSE/GO/BECOME over Thing args.
- Wolff force dynamics: the effect is the PATIENT reaching (or not) an END-STATE computed from the patient's own force
  vector; binding to the affected entity is STRUCTURAL, not optional.
- Zwaan-Radvansky event-indexing: causal nodes are events already bundled with protagonist; Kintsch CI: relata are
  PROPOSITIONS (head + argument slots) e.g. BAKE[agent:MARY, object:CAKE], not words. The correct relatum:
  WATER[agent:X, patient:PLANT] -> LIVE[patient:PLANT].
- Forbus QP / Mueller Event Calculus / STRIPS: effects are changes to FLUENTS bound to a participant; no formalism has
  an unbound effect -- the object argument is mandatory in the predicate signature.
- Neuroscience: Frankland-Greene 2015 (PNAS) localize agent/patient role-binding to left mid-superior temporal cortex
  (lmSTC), a dedicated computation distinct from ATL concept storage; Baldassano 2017 event-schema = state-schema
  coding, not word co-occurrence (matches our on-disk SEM/TEM: forward transition needs a bound role-filler vector).
- ADVERSARIAL (Michotte fast/automatic causal perception): still participant-bound ("A launches B"); word-level
  association is a fast QUALIFYING prior, not a defeater -> state-grain is not over-engineering. Word-level as a
  TERMINAL representation reproduces our own measured promiscuity failure.
- **BUILD (glass-box, no LLM): two-tier store.** Tier 0 = bare-word association (cheap recall prefilter, NEVER
  terminal). Tier 1 = frame-grain `(verb, AGENT, PATIENT)` via `hdlab.graded_role_assigner` (already extracts this) --
  the hard floor. Upgrade to state-change `(entity, attribute, value)` when a change-of-state verb-class lexicon fires
  (BECOME(state(patient)) as a lookup; existence/health/location/possession axes). The one untested engineering bridge
  = the change-of-state verb-class lexicon (VerbNet resultative coverage).

## PHASE A SPEC — position-balanced causal-selection instrument (instrument-validity research: appended when it lands)
(pending synthesis -- COPA / Balanced-COPA / e-CARE ids, floors, CausalNet ceiling, trap-check.)

## PHASE C — cover the Gricean gap with ACTION-CONDITIONED online goal inference
Research (assoc-vs-causation): forward models are causal PRECISELY where action-conditioned (Wolpert motor forward
model = P(sensation|do(command)); Rezende 2020: passively-fit transitions are causally incorrect for planning). This
is why the parents' ONE win was the GOAL slice. The obvious everyday links testimony omits (Gricean) are exactly the
GOAL-driven ones -> infer them ONLINE from the story's goal/means-end structure (chain_multi_step's shelved MeansEnd
ATL hub), not from corpus retrieval. Full architecture = corpus testimony (non-obvious/mechanism links) + online
goal-inference (obvious/everyday links).

## PHASE D — wire + measure end-to-end
Feed the store through the full per-story counterfactual-necessity read with SOFT participant binding (NOT hard-gating
-- parents proved hard coref-gating flat; online-comprehension research: coref is a soft graded cue). Confirm no live
reasoner regresses; build a `board_causal_direction` instrument-arm so the proven signal is scorable live.
