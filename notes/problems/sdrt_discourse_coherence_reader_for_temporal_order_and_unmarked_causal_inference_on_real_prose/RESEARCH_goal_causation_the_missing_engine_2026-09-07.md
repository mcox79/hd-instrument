# Research: GOAL/intentional causation is the missing brain-faithful engine (the drill of the located negative)

Two independent literature drills (2026-09-07), triggered by the owner's push to drill the located negative
aggressively ("where are we losing signal, how does the brain do it exactly?"). Saved here so the SOLVED.md
citation is not dangling. Both converge on the same decomposition.

## 1. GOAL causation is the organizing spine of narrative (not one category among equals)
- **Trabasso & van den Broek 1985 (JML 24); Trabasso, van den Broek & Suh 1989 (Discourse Processes 12):** every
  story clause codes into Setting/Event/Internal-Response/GOAL/Attempt/Outcome; the backbone causal chain is
  GOAL -> Attempt -> Outcome (a desire MOTIVATES an attempt that PRODUCES an outcome). Physical Event->Event
  causation exists but is comparatively sparse in character-centered narrative.
- **Graesser, Singer & Trabasso 1994 (Psych Review 101):** the "why"-question-answering procedure works by TRACING
  an action back through a GOAL HIERARCHY (subgoal -> superordinate -> motive) as the DEFAULT explanatory move;
  causal-antecedent + superordinate-goal inferences are generated ON-LINE / routinely (required for coherence).
- **Lehnert 1981 (Cognitive Science 4/5):** Plot Units have NO physical-causation primitive at all -- only
  goal/affect links (Motivation / Actualization / Termination / Equivalence). A near-definitional claim that
  character-centric short narrative (the TellMeWhy/ROCStories genre) is goal-structured.
- **Schank & Abelson 1977:** an action is "understood" iff connected to a goal via a plan.
- **TellMeWhy (Lal et al. 2021):** 28.82% of why-answers are IMPLICIT (>=2/3 annotators say not stated); every
  quoted implicit example in the paper is a goal/desire/motivation inference; human agreement kappa=0.88 (implicit
  answers are convergent, not idiosyncratic). No published motivation-vs-physical percentage exists ("dominant" is
  a well-supported qualitative claim). MEASURED HERE: goal-typed = 35.9% of non-adjacent causes (the largest single
  category); the base physics+psych engine scored 0.293 on it (blind).

## 2. The exact no-LLM mechanism, and is it a separate engine?
- **Malle 1999 (PSPR) / 2004:** intentional action -> a REASON explanation (desire + belief -> intention -> action),
  categorically distinct from a CAUSE explanation (physical/unintentional). The reason engine gives d=0.4-0.7 where
  generic cause/effect categories give NULL on the same data; the 'in order to / so that' construction is
  reason-specific. => a decisively separate engine at the explanation level.
- **Baker, Saxe & Tenenbaum 2009 (Cognition 113); Baker et al. 2017 (Nat Hum Behav):** inverse planning -- model the
  agent as an approximately-rational planner, invert via Bayes to recover the goal. **Csibra & Gergely 1997/2003:**
  cheaper teleological stance -- infer the goal such that the action is the MOST EFFICIENT available means (a
  means-end plausibility check, no full utility model).
- **Minimal no-LLM features:** (a) desire/goal predicate detector; (b) goal-object extraction; (c) MEANS-END
  satisfaction match (does THIS action serve THAT goal); (d) agent coreference.
- **Talmy 1988 / 2000:** desire is an internal psychological FORCE/tendency toward a goal-state -- so the
  "tendency-toward-goal" half is a force-dynamics extension; the GENUINELY-DISTINCT computation is the
  satisfaction-MATCHING step (symbolic/relational, not a force-sum).

## 3. Principled cue integration vs the heuristic product
- **Kintsch 1988 construction-integration:** a CONSTRUCTION phase (loose, overinclusive candidates) then an
  INTEGRATION phase = a connectionist constraint-satisfaction network that SETTLES (signed excitatory/inhibitory
  edges, iterative relaxation), suppressing inconsistent nodes. The gap in `content*(1+Sum cues)` is NOT
  additive-vs-multiplicative (it is a first-order product-of-experts, defensible if cues are calibrated) -- it is
  the ABSENCE of a settling/INHIBITION step (nothing lets a locally-plausible cue be VETOED by the emerging global
  causal chain). **Myers & O'Brien 1998 resonance ("proposes") + Trabasso/Graesser necessity ("disposes")** is the
  right two-stage frame; Rehder 2003 causal-model theory (noisy-OR Bayes net) a still-more-principled option.

## 4. Decomposition estimate (two independent drills converge)
- Drill A: ~55-65% missing goal engine (buildable, no-LLM) / ~35-45% irreducible world-knowledge coverage.
- Drill B: ~60-75% missing goal engine / ~25-40% idiosyncratic world-knowledge (GLUCOSE dim-5/10-style facts).
- **MEASURED HERE (the falsifiable test):** the goal ENGINE lifts the GOAL-typed subset 0.293 -> 0.533 (+0.239,
  CI-sep over base/topical/twin, twin LOSES) -- the fidelity gap is REAL and crossed on the dominant category. But
  it does NOT win the FULL population (trades off: +0.239 goal / -0.108 OTHER), and the MEANS-END gate does NOT fix
  the over-firing (OTHER stays 0.139) -- because SELECTING which of several stated goals motivates THIS action is
  Tier-2 inverse planning (Baker-Saxe-Tenenbaum), the world-knowledge wall the goal_register itself flagged
  ("Tier-2 'why THIS action over the alternatives' REQUIRES the world-knowledge/meaning channel"). So the residual
  is precisely: Tier-1 goal DETECTION = buildable (done); Tier-2 goal SELECTION + idiosyncratic coverage = the wall.

Research confidence: P_deflated ~0.7 (goal-causation dominance + the missing-engine decomposition, corroborated by
two independent drills + a direct on-disk measurement) / ~0.75 (the mechanism-is-PINNED sub-claim).
