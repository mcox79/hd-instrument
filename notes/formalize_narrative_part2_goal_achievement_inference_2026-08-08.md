# FORMALIZE: Narrative PART-2 = GOAL-ACHIEVEMENT INFERENCE (the deep half of the narrative frontier)

**Filed:** 2026-08-08 by Director, formalize-first (build-ready spec; part-1 = learnable goal-recognition
is HARD_PASS/tractable, bd9b76e28). This scopes part-2 so the USER's go/no-go on the deep build is
informed. Companion: the narrative-frontier diagnostic + generality test in the backup doc.

## 0. WHAT + the honest problem
Part-2 = infer whether the story's OUTCOME actually ACHIEVES the character's GOAL-state (met/unmet).
The generality test showed SURFACE achievement/affect cues PLATEAU ~0.60 even with learned weighting
-- so part-2 is NOT missing-learning-over-surface-cues; it needs a RELATIONAL comparison: does the
outcome-STATE satisfy the goal-STATE. That is the session's deepest comprehension wall, localized.

## 1. BRAIN-FIDELITY (which structure, does it reuse an owned process)
Goal-achievement monitoring = ACC (anterior cingulate) EXPECTANCY-VIOLATION / conflict-monitoring
(established earlier this session as the "did-it-happen" analog): the brain holds the goal-state as an
expectation and fires on MATCH (goal met) vs MISMATCH (goal thwarted) with the achieved state. Value
sign (good/bad for the agent) rides OFC/vmPFC. So part-2 = an ACC-analog goal-state<->outcome-state
COMPARISON, with the value/polarity from the owned valuation. SHARE-a-process: YES -- the owned
did-it-happen (occurrence-gate + _verb_negated_before) IS the ACC-analog; reuse it, don't rebuild.

## 2. REUSE MAP (part-2 is reuse-heavy -- NOT a from-scratch engine)
- FRONT-END: part-1 LEARNABLE goal-recognition (bd9b76e28, recall 0.871) -> extracts the goal-state
  (verb + referent + desired class) on modern narrative. DONE + tractable; wire it in.
- SUBSTRATE: hdlab/situation_model_accumulate GoalOutcomeRegister (bind GOAL-state + OUTCOME-state;
  directed goal->outcome coherence score) -- owned, 1.0 on fair banks (exp_component5_wired_endtoend).
- COMPARISON (the ACC-analog achievement check): hdlab/goal_typing._class_relation (same/opposed
  between desired-class and actual-class) + did-it-happen occurrence-gate + negation-scope. Owned.
- VALUE/POLARITY: the owned goal-congruence outcome-valence (goal_typing) + (for social/felt) the
  grounded valuation. Owned.
So the PIPELINE is mostly owned: part-1-goal-recognition -> bind goal+outcome in the register ->
_class_relation/did-it-happen achievement check -> met/unmet + value. The ORGANS exist.

## 3. THE DEEP GAP (the one real build) -- same missing-LEARNING/grounding pattern part-1 solved
The achievement COMPARISON (_class_relation) resolves via a HAND CLASS_REGISTRY (achievement verbs
win/reach/..., failure verbs, opposed-pairs). On modern narrative's DIVERSE goal/outcome expressions
this does NOT generalize (the diagnostic: owned typer abstained 96%). => part-2's CORE build =
a LEARNABLE / GROUNDED achievement-comparison: "does outcome-X achieve goal-Y" generalizing past the
hand CLASS_REGISTRY, via EITHER (a) learned class-relations (reuse hdlab/learner, same route that just
worked for goal-recognition), OR (b) the owned lexical_similarity (ATL-hub shared-feature) / grounded
valuation to judge goal-outcome satisfaction by MEANING not a hand list. This is the exact missing-
LEARNING/grounding lever the session keeps landing on -- now for the goal<->outcome RELATION.

## 4. BUILD ORDER + CAN-FAIL (test-first, each strict-ADD, anti-premature-HARD_FAIL governs)
- INC-1: wire part-1 goal-recognition -> GoalOutcomeRegister -> owned _class_relation/did-it-happen on
  modern narrative. CAN-FAIL: does fixing the front-end (part-1) alone lift modern-narrative met/unmet
  coverage above the 96%-abstain (does the owned comparison then FIRE)? Measures how much is front-end
  vs comparison.
- INC-2 (the core): LEARNABLE/GROUNDED achievement-comparison (learned class-relation via hdlab/learner
  OR lexical_similarity/grounded judgement) replacing the hand CLASS_REGISTRY. CAN-FAIL: modern
  narrative met/unmet > the 0.60 SURFACE PLATEAU (the bar every surface-cue method hit) AND >
  majority, non-episodic, scramble-collapses. Beating 0.60 = the relational comparison adds real
  signal past surface cues = part-2 tractable.
- HARD-FAIL triage (NOT a ceiling): if it stays ~0.60, diagnose -- is the comparison still surface
  (needs deeper semantic/grounded judgement)? is the goal/outcome extraction the bottleneck? is n too
  small? Brain=existence-proof: goal-achievement monitoring is an ACC function -> achievable.

## 5. HONEST RISK
The deepest residual: some achievement inferences need genuine SEMANTIC/pragmatic reasoning (irony:
"flavored the cake with liniment" = goal-thwarted with no failure verb; indirect achievement via a
third party) that neither class-relation NOR shared-feature similarity captures -- those are the
irreducible discourse/world-knowledge tail (the session's L-bucket, out-of-scope for a finite curric).
Part-2's realistic target is the RELATIONAL-but-not-deeply-inferential majority; the irony/world-
knowledge tail is a later frontier. Also: modern narrative goal-achievement data must be authored
(the ROCStories relabel gives ~50; more needed for a robust n).

## 6. BOTTOM LINE
Part-2 is NOT a from-scratch inference engine -- it REUSES the owned goal->outcome register + did-it-
happen (ACC-analog) + part-1's learnable goal-recognition; the ONE real build is a LEARNABLE/GROUNDED
achievement-comparison (does outcome achieve goal) generalizing past the hand CLASS_REGISTRY -- the
same missing-LEARNING/grounding lever that just worked for goal-recognition. Can-fail = beat the 0.60
surface plateau on modern narrative. This is the concrete, de-risked, reuse-heavy shape of the deep
narrative frontier -- recommended as the next major build, pending USER go.
