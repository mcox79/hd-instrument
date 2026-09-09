# Counterfactual necessity -- the causal-selection GATE, built to spec + tested. LOCATED NEGATIVE (10th triangulation)

**problem:** chain_multi_step_plans_and_scripts_for_the_generative_world_model | **date:** 2026-09-08
**cell:** experiments/exp_multistep_necessity_v1.py | **gold:** TellMeWhy non-adjacent (Lal 2021), n=256
**research:** notes/research_recurrent_generative_loop_counterfactual_necessity_2026-09-08.md

## WHY (the decisive reframe)
The forward-SUFFICIENCY organ tied because sufficiency is FORMALLY unable to discriminate a true cause from a
merely-predictive confound (Lewis 1973; Mackie 1974 INUS; Halpern-Pearl 2005 AC2a) -- not a power problem. Every
serious formal + cognitive account makes counterfactual NECESSITY the causal-selection GATE (CSM Gerstenberg 2021;
NSM Icard-Kominsky-Knobe 2017; Henne 2021). So the categorically-different fix is NECESSITY, not a stronger
sufficiency model. I built it to the pre-registered spec.

## WHAT I BUILT (glass-box; reuses the LANDED FHRR event-bundle substrate)
- Each sentence -> a role-slot-bound FHRR event vector over {PRED,AGENT,PATIENT} (hdlab.event_bundle.EventBundleCodec,
  the substrate's validated bound-event representation; SEM scene binding, Franklin 2020).
- SITUATION register S = FHRR-bundle of the candidate events. DECODE-CONFIDENCE(S,q) = mean cleanup-readback of q's
  own (role,filler) pairs from S (situation_model_accumulate.cleanup_argmax algebra).
- NECESSITY(C_i) = decode_conf(S_FULL,q) - decode_conf(S_FULL MINUS C_i, q) -- the counterfactual leave-one-out
  (does REMOVING C_i drop q's support? Halpern-Pearl but-for). SUFFICIENCY(C_i) = decode_conf({C_i},q) kept as an
  arm for the dissociation test.
- Pre-registered controls: info-free TWIN (permute necessity across candidates); BINDING-SHUFFLE
  (encode_scrambled_event -- fillers bound to PERMUTED role keys; does necessity survive role-scrambling?);
  shared-participant-CONFOUND subset (n=192, where sufficiency lost to its twin); GOAL/OTHER; single-gold + credit@2.

## THE MEASURED RESULT (n=256; base_mult 0.2773, topical 0.2500) -- verdict NECESSITY_LOCATED_NEGATIVE
- FULL: nec_solo 0.281, nec_add 0.297, suf_solo 0.324, conj 0.297 -- ALL TIE (none CI-sep, none beats twin).
- CONFOUND (n=192): base 0.052, nec_solo 0.229 (+0.177 CI[0.115,0.245] over base) BUT LOSES to its own info-free
  twin (obs 0.229 < null p95 0.307) -- a TWIN-FAILING ARTIFACT, exactly as sufficiency was. P1 HARD-FAIL.
- BINDING-SHUFFLE (the killer diagnostic): nec-vs-shuffled-roles +0.0625, NOT CI-separated -> "SET-MEMBERSHIP-ONLY":
  scrambling the role bindings barely changes necessity, so the computation is using LEXICAL OVERLAP (which candidate
  shares q's content words), NOT who-did-what structure. This is why it is promiscuous.
- P2 dissociation: on 64 items where necessity and sufficiency disagree, necessity agrees with gold 0.203 vs
  sufficiency 0.375 -- necessity is WORSE, adds no favorable independent signal. HARD-FAIL.
- P3 eval-ceiling: credit@2 base 0.543 -> nec 0.570 (+0.027), not materially larger than single-gold (+0.004) -- a
  lenient scorecard does NOT rescue it on this data.

## CONCLUSION -- the ceiling, named (the research's own HARD-FAIL clause, realized)
Counterfactual NECESSITY -- the categorically-correct causal-selection computation per four independent literatures
-- built faithfully over the substrate's LANDED FHRR event representation, ALSO ties and loses to its info-free twin,
AND the binding-shuffle proves it reduces to LEXICAL SET-MEMBERSHIP. Per the pre-registered Prediction-1 HARD-FAIL
clause: the Lewis/Mackie/Halpern-Pearl necessity asymmetry, while real in the philosophy/CSM literature, DOES NOT
TRANSFER to this substrate's representation at this task's granularity. The ceiling is REPRESENTATIONAL, not the
necessity-vs-sufficiency distinction: the substrate's per-event bundle + leave-one-out reinstatement does NOT encode
the STORY-SPECIFIC CAUSAL STRUCTURE (which state C establishes, whether q depends on that state) that true
counterfactual necessity requires. Computing genuine necessity needs a per-story CAUSAL GRAPH one can intervene on
(Bramley 2017 minimal-edit structure learning; CSM's simulate-with-C-removed) -- a fundamentally larger build than
any leave-one-out scoring, and the edge-scoring it needs inherits the same causal-edge-correctness wall. This is the
10th independent triangulation point (after the parent's ~8 + the forward-sufficiency tie): determining the true
causal edge from narrative text is the fundamental wall, now bracketed on BOTH formal halves (sufficiency AND
necessity), and additionally capped by a documented single-gold EVAL ceiling (TellMeWhy: 26% annotator overlap;
credit@2 does not rescue).

## WHAT IS BRAIN-FOUNDATIONAL NOW / WHAT THIS ADVANCES
- Both formal halves of causal selection (sufficiency, necessity) are now BUILT to brain-foundational spec and
  MEASURED -- the causal-selection component is characterized to the formal-theory level, not left as a hope.
- The binding-shuffle diagnostic is a reusable "is this signal using structure or set-membership" control.
- Coref quality confirmed NOT the lever for single-protagonist narratives (Kehler 2008/2013 + our measurement); the
  brain-foundational binding lever is COHERENCE-RELATION / implicit-causality driven resolution, not generic coref.

## PROPOSED hdlab LANDING (Q111 -- I do not write hdlab/)
Do NOT wire necessity (or sufficiency) as a TellMeWhy cause-selection cue: measured tie + confound twin-artifact +
set-membership. The organs remain valid for their own home benefits (forward_expect_fn closing the N400 loop). The
only route that could cross the causal core is a per-story causal-STRUCTURE learner (Bramley/CSM), which is a
multi-cell program AND is capped by the eval; recommend it be scoped as such, not as a quick cue.

## REVERIFY
.venv/Scripts/python.exe experiments/exp_multistep_necessity_v1.py --run --n 1500   # ~90s
Witness: verification/test_multistep_meansend_chain.py W24-W26 (necessity located negative + binding-shuffle
set-membership + dissociation-fail).

## TLDR (plain English)
The outside science said: to pick the true cause you must ask "if this had NOT happened, would the outcome still
have happened?" (necessity), not just "did this make the outcome likely?" (sufficiency, which we already built and
which tied). So I built the necessity test, reusing parts we already had, exactly as prescribed. It also tied -- and
a built-in check revealed WHY: on our current way of representing an event, the necessity test collapses into "which
earlier sentence shares the most words with the outcome," which is the same promiscuous signal we keep hitting. The
honest, important conclusion: we have now tested BOTH halves of the textbook definition of a cause, done right, and
both are capped by the same deeper thing -- our reader does not build a little story-specific cause-and-effect MAP
as it reads (it scores sentence pairs), and without that map neither test can tell a real cause from a look-alike.
Building that map (a per-story causal graph you can poke at) is the one remaining brain-faithful route, and it is a
big build -- and separately, the answer key we grade on is itself so inconsistent (different people agree only about
a quarter of the time) that even a real win would look small. This is a real, formally-grounded result about WHERE
the wall is, not a wasted cycle.

## QUESTIONS
One genuine strategic fork for the owner (stated as prose per discipline, in NEXT STEPS).

## NEXT STEPS
- THE ONE UNREFUTED CORE ROUTE: a per-story causal-STRUCTURE learner (Bramley 2017 minimal-edit local search over a
  small causal graph; CSM intervene-and-re-simulate). Brain-foundational, glass-box, but a multi-cell build whose
  edge-scoring inherits the causal-edge wall and whose payoff is capped by the eval ceiling -- honest P is low.
- FIDELITY (audit-completeness, not task-signal per measurement): the chain-top components (predictive/graded parse
  I5, decision ECHO+DDM, the recurrent architecture) can be made brain-foundational for the AUDIT, but the
  measurement says they will not cross THIS task's ceiling.
- MEASUREMENT: a genuinely graded causal-network eval (Trabasso-Sperry connectivity) would need annotation; credit@2
  did not rescue, so the eval fix is lower-value than hoped on this data.
- DO NOT REDO: sufficiency-as-cue (tie), necessity-as-cue (tie, set-membership), the confound subset as a "win"
  (twin-failing), coref-quality as the lever (not the lever, single-protagonist).
