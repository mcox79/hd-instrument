# The GROUNDING BRIDGE -- design for the next problem (handoff-ready)

**Why this is the biggest-impact next step.** This solve proved (a) the text-mined causal store is capped at ~0.61 on
DIRECTION and inert on the WIQA necessity axis, and (b) the route past the wall -- grounded interventional learning --
works: direction 0.99 (+0.38 over text), few-shot 0.90 in ~5 active interventions, composed into `causal_reasoner` for
cause selection (0.03->0.98), hardened into `GroundedCausalLearner`. **But the learner has NO live consumer without the
bridge** -- the "landed != live" trap. The bridge is where LIVE reader impact is unlocked.

## What the bridge IS (brain-foundational)
The brain does not physically intervene while reading -- it runs SIMULATED interventions on an internal generative model
(Gerstenberg-Tenenbaum counterfactual simulation model; Battaglia intuitive-physics engine; Hegarty mental simulation;
Craik "small-scale model in the head"). Grounding comes from PRIOR grounded knowledge (physics, magnitudes, embodied
schemas), NOT from the text. So the bridge = two halves:
1. **STRUCTURE from text** -- extract the narrative's entities/quantities/candidate relations (the reader's parse + the
   sparse causal skeleton `sm.causal_links`).
2. **DYNAMICS from grounded priors** -- instantiate those entities in a SIMULABLE dynamical model (qualitative physics +
   magnitude grounding via `hdlab/sensorimotor_spoke` + `hdlab/grounded_similarity`), then run FEW-SHOT simulated do()
   interventions -> feed `GroundedCausalLearner` -> a directed+signed graph the do-sim reasoner traverses.
   Active selection (built here) is what makes the few-shot simulation viable (you get ~a handful of imagined
   interventions per narrative, not thousands).

## Sequence (bounded risk first)
1. **SCIENCE-SLICE bridge prototype FIRST (tractable grounding).** On quantitative/physical processes (WIQA science
   slice; chemistry/physics), grounding already partly exists: `hdlab/causal_sign_channel.py` computes edge SIGN from
   formal-model structure (stoichiometry/physics/thermo, ~14% coverage, beats the falsifier +0.157). Reuse those formal
   couplings as the grounded DYNAMICS; run simulated interventions to recover DIRECTION (not just sign) and answer the
   more/less/no_effect. BAR: beat the text store + the shuffled twin CI-sep on the science slice, where text provably
   caps (direction ~0.61, sign text-exhausted). This proves the bridge CONCEPT where grounding is easiest.
2. **GENERAL bridge (the main event, likely owner-run, large).** Extend beyond the formal-model slice to everyday/social
   causation -- this needs the MEANING/GROUNDING channel (the fleet's biggest open cluster: map arbitrary narrative
   concepts -> grounded magnitudes/schemas). Overlaps `reader_meaning_channel` + the generative world-model program.
   Do NOT attempt inside a store-wiring solve.
3. **LAND `GroundedCausalLearner`** as `hdlab/grounded_causal_learner.py` (Q111) once the bridge feeds it real
   grounded/simulated experience + the audit verifies -> raise BF_SPIRIT to BF.

## The hard dependency, named honestly
The bridge's success hinges on GROUNDING -- mapping narrative concepts to grounded magnitudes + correct dynamical
priors. If the grounding is wrong, the simulation reproduces garbage (garbage in). That is why the science slice (where
grounding = formal physical models) is the right first target, and why the general bridge is gated on the meaning
channel. This is the same wall 5+ solvers named as the generative world-model MAIN EVENT.

## Controls the bridge problem must run
Shuffled-dynamics twin (grounded model with scrambled couplings -> loses); text-store baseline (the ~0.61 direction /
sign-exhausted ceiling to beat); a NO-intervention observational baseline (confounded -> chance, per this solve);
density-matched + direction-scramble nulls (per this solve's control battery, to avoid the density/topicality artifacts
that inflated the store's +0.139). Grade on MODERN gold (WIQA science slice; 19c banned).

## Reuse (do not rebuild)
`GroundedCausalLearner` (`exp_grounded_causal_learner_organ_v1.py`), `hdlab/causal_reasoner` (rung-2/3 do-sim),
`hdlab/causal_sign_channel` (formal-model sign = the science-slice grounded dynamics), `hdlab/sensorimotor_spoke` +
`hdlab/grounded_similarity` (magnitude grounding), the active-selection + MI-readout + control-battery machinery here.
