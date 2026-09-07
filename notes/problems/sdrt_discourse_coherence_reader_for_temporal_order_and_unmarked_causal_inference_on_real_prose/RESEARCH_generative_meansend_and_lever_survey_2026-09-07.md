# Research + measurement: the generative means-end, and a complete survey of tractable no-LLM levers

Owner push (2026-09-07): "with more knowledge, any other upgrades/efficiencies? do it all." A 4-part literature
drill + built + measured each candidate lever. Saved here so the SOLVED.md citation is not dangling.

## The means-end axis: object-as-patient is PARTLY referential coherence; result-state is the general signal
- **Object-as-patient ("wanted milk"->"bought milk") is MOSTLY generic referential coherence, NOT means-end**
  (Grosz-Joshi-Weinstein 1995 Centering; Givon 1983 topic continuity; Kintsch-van Dijk argument overlap; Keenan-
  Baillet-Brown 1984: referential coherence "establishes the NEED for a causal inference but otherwise contributes
  minimally"; Zwaan-Radvansky 1998: protagonist- and goal-continuity are SEPARATE dimensions; Csibra-Gergely 2007
  efficiency is goal-CENTRIC not object-centric). It is high-precision only for OBJECT-DESIRE goals (get/obtain NP)
  and UNAVAILABLE for STATE-DESIRE goals (lose weight, feel safe -> no shared object; GLUCOSE's canonical motivation
  example "wants safety -> turned bike" is a DIFFERENT-object case). No corpus reports its precision/recall (open).
- **MEASURED (the decisive control):** the goal-GATED object-match (overall 0.293) BEATS the UNGATED referential-
  coherence control (0.254) CI-sep (+0.0391 [0.004,0.074]); the ungated version OVER-FIRES (407 fires) and HURTS
  (-0.023 vs base). So the goal-gating carries a REAL (weak) means-end signal beyond Centering -- for object-desire
  goals -- but pure referential coherence over-fires. The research's "it's all coherence" is PARTIALLY refuted.
- **RESULT-STATE matching is the VALID, general means-end** (Schank-Abelson PLANBOX RESULT links; Long-Golding-
  Graesser 1992: superordinate goal inferences like jog->fitness are generated on-line WITHOUT argument overlap).
  Object-match is its special case for possession/consumption goals. It needs a per-verb-class effect schema
  (buy->possess, jog->fitness-state) -- the coverage wall for state-desire goals.

## The built stack (measured, TellMeWhy non-adj n=256): generative union is best-yet, beats twin, ties base
| arm | overall | notes |
|---|---|---|
| base (physics+psych, no goal) | 0.277 | blind to goal causation (36% of non-adj) |
| typed (CSKG retrieval means-end) | 0.277 | coverage-bound 34%; cuts over-fire; beats twin |
| objmatch (goal-object-as-patient, generative) | 0.293 | beats ungated refcoh CI-sep -> real weak means-end |
| refcoh (UNGATED object overlap) | 0.254 | pure referential coherence -- OVER-FIRES, HURTS |
| **generative (typed OR objmatch)** | **0.309** | **best; fires 150 (vs 102 retrieval); beats twin +0.113 CI-sep** |
| gen vs base | +0.031 [-0.012,+0.074] | borderline, NOT CI-sep (state-desire goals still uncovered) |

## The other levers, ranked (4th drill) -- none crosses the cause-ID wall in scope
1. **Aspect/telicity** (cheapest, parse-only; Moens-Steedman 1988; Vendler): a GOAL-COMPLETION cue (telic->achieved;
   progressive->culmination stripped). On-target for Result/Background typing, but TANGENTIAL to the cause-ID metric.
2. **Two-stage generate/verify scaffold** (Myers-O'Brien resonance + Trabasso necessity): near-zero new-signal cost,
   but only pays off with a real EXPENSIVE verifier = the generative rollout (the wall).
3. **Surprise / prediction-error gate** (Graesser-Singer-Trabasso online causal-antecedent search): real, but needs a
   corpus event-expectedness table (script-slot PMI) and the discourse-surprisal proxy is unvalidated.
4. **Selectional-preference gate:** weakest evidence, redundant with participant-overlap -- DROP.

## Trabasso multi-hop goal-chain selection -- real but will NOT beat nearest-antecedent full-population
Importance/recall is driven by CONNECTIVITY (degree) + causal-chain membership, NOT goal-CATEGORY (Fletcher-Bloom
1988, primary: causal-connections R2=.22, chain-status R2=.24, referential .02). QUEST (Graesser-Gordon-Brainerd
1992, primary) DOES multi-hop backward-chain to root goals -- but with EXPONENTIAL DISTANCE DECAY (score = t^d,
t=.67), so a distant goal is a WEAKER explanation, not equal. CRUCIAL COUNTER (Fletcher-Bloom 1988, primary): a
"current-state+goal" strategy fit recall WORSE (R2=.27) than plain NEAREST-ANTECEDENT (R2=.31) -- goal dominance
shows in importance/inference-direction, not continuous WM occupancy. => a multi-hop chain selector will NOT beat
the adjacency/nearest baseline full-population (only on the non-adjacent subset, exactly what the causal reasoner
already showed). So it is not a new full-population lever.

## Verdict (from ~6-8 angles now): the residual is the GENERATIVE WORLD-MODEL
Every tractable no-LLM lever either (i) measures referential coherence/topicality (relatedness, ungated object-match)
-- real generic cues that over-fire, not the intentional means-end; or (ii) is the correct means-end axis (typed-edge
retrieval, result-state) but COVERAGE-BOUND (CSKG cause-pairs 17.3%; goal->action 34%; state-desire result-states
need a broad verb->effect model); or (iii) helps only the non-adjacent subset / is tangential (multi-hop chains,
aspect). The full-population CI-sep win requires a GENERATIVE means-end: SIMULATE the action forward and check the
goal-STATE (result-state matching over a broad experiential verb->effect model) -- the causal reasoner's own
content-sensitive rollout P1, needing the meaning channel. The best shippable stack now: goal engine + typed-edge +
generative object-as-patient (union -> best overall 0.309, beats twin CI-sep).

P_deflated ~0.7 (the axis/coverage conclusions, corroborated by 4 sub-agents + direct measurement from many angles).
