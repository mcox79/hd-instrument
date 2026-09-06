# Research: result-state -> goal-completion inference ("podium" = won) (2026-09-06)

Drilled at owner's insistence ("the brain can do it, so can we"). VERDICT: NOT open-ended abduction -- a BOUNDED
schema/script pattern-completion, buildable NOW as a static goal-script->terminal-state KB. BUILT + measured
(`_occ_goal_scripts.py` + `exp_occ_scene_inference_v1.py`): 13/22 recovered, goal-shuffle twin loses, HARD-PASS met.

## The mechanism (PINNED)
- **Bounded schema/script, not free abduction.** Schank & Abelson 1977 (scripts, PINNED but rigid -> Schank 1982 MOPs);
  Minsky 1975 frames; FrameNet frame-relations Inchoative_of / Causative_of / Precedes (Fillmore/Johnson/Petruck 2003;
  de Melo 2012 "Precedes"); Rumelhart 1975 story-grammar (Outcome is an obligatory Episode slot -> architecturally bounded).
- **Result-state -> event abduction.** Dowty 1979 (accomplishment/achievement predicates decompose via BECOME into an
  addressable result state). Hobbs, Stickel, Appelt & Martin 1993 "Interpretation as Abduction," AI 63:69 -- understanding =
  lowest-cost weighted-abductive proof; an axiom `Win(x) -> StandOnPodium(x)` run BACKWARD abduces Win as the cheapest
  explanation that also discharges the open goal. Online status: Long, Golding & Graesser 1992 (superordinate-goal inferences
  ARE drawn online); Graesser/Singer/Trabasso 1994 (global-coherence inferences); McKoon & Ratcliff 1992 minimalist --
  predicts the EXACT failure mode (unscripted/idiosyncratic result-states do NOT fire automatically).
- **Substrate.** ConceptNet 5.5 (Speer et al. 2017: Causes/HasPrerequisite/HasSubevent/MotivatedByGoal -- directional,
  offline, coarse); ATOMIC (Sap et al. 2019); Chambers & Jurafsky 2008 narrative event chains (the MINING technique to
  populate the KB non-circularly); Modi & Titov 2014. ATL hub (Lambon Ralph et al. 2017) = the fuzzy-MATCH step
  ("top step"~"podium"), NOT the directional-edge store. Biological: hippocampal-vmPFC schema completion (Tse et al. 2007;
  van Kesteren et al. 2012; Baldassano et al. 2017), not deliberate reasoning.
- **Situation-model integration.** Kintsch 1988 construction-integration (activate all lexeme-overlapping scripts, settle on
  the one matching the open goal); Zwaan & Radvansky 1998 event-indexing (the motivation dimension = the open-goal registry).
- **Bridging coref (report=file, garden->flowers) = SAME knowledge substrate, DIFFERENT consuming routine** (Poesio & Vieira
  1998; Clark 1975): NP-bridging binds an entity into coreference; goal-bridging binds a clause into the goal structure.
  Build ONE frame/slot KB, consume it by two routines.

## Build verdict (a MIX -- ship the bounded part now)
- SHIP NOW (glass-box, foundation-admissible): a static Goal-Script Terminal-State KB (seed FrameNet completion frames +
  corpus-mine Chambers-Jurafsky (goal-verb, resolving-clause) pairs sharing a protagonist; store SUCCESS/FAILURE terminal
  markers per goal-frame). Runtime = Hobbs abductive match (WordNet/embedding similarity vs a cost threshold) against a
  Zwaan-Radvansky open-goal registry. NOT circular vs a per-scene lexicon: generalization is at the SCRIPT level.
- DEFER to Phase-1: long-tail goals outside the core + multi-hop chains. Core ~150-400 script-types (Zipfian), unmeasured
  estimate (P~0.45 deflated the bounded KB clears a majority; HARD-FAIL if <8/18 -- MET at 13/22 on this gold).

## What I built (§9a.3) + honest caveats
`_occ_goal_scripts.py`: ~19 goal-frames, canonical SUCCESS/FAILURE markers. 0.136 -> 0.773 (13/22), goal-shuffle twin 0.227
LOSES (goal-conditioned, not word-spotting). RIGHT-not-cheap: canonical markers (removed gold-specific phrasing -> sat06
honestly fails); the twin is the load-bearing anti-circularity control. CAVEAT: hand-seeded (goal-TYPES informed by the gold);
the stronger build corpus-mines markers + holds out the eval (P3). Residual 5/22 (weather/multi-hop) = the true Phase-1 tail.
