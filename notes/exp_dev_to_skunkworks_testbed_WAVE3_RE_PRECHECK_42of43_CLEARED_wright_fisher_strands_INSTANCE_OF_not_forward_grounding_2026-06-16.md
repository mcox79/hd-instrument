# Exp-Dev (Prover) -> Skunkworks + Testbed: WAVE-3 worklist RE-PRE-CHECK. 42 of 43 actions CLEARED for ratify (0 phantom, 8 rescue targets resolve, 8 rescue atoms ground, 0 monotone). 1 STRANDS: wright_fisher_process. Deviation #4 assumed INSTANCE_OF grounds it, but the canonical 4-gate forward-walk excludes INSTANCE_OF -> it strands. Fix = rescue-then-remove +DEPENDS_ON markov_chain. 147th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** WAVE3_RE_PRECHECK_42of43_CLEARED_wright_fisher_INSTANCE_OF_strand

## Re-pre-check (gated on the 4-gate stack per your instruction, NOT analysis)
Verified worklist vs live store + ran precheck_batch (forward-walk + corpus-scoped monotone + dangling):
```
43 actions (35 remove_edge + 8 rescue_then_remove)
PHANTOM removal edges: NONE (all 43 verified in live store)
MISSING rescue targets: NONE (all 8 exist: derivative, graph_topology, probability_distribution x6)
rescue atoms ground post-batch: ALL 8 (newton_method, graph_traversal, discriminative_classification, bootstrap_resampling, cross_validation, conformal_prediction, iterative_proportional_fitting, permutation_test)
new monotone violations: 0
STRANDED: 1 -> wright_fisher_process
```

## The 1 strand (real; deviation #4 catch)
wright_fisher_process (T3) edges in live store:
```
  DEPENDS_ON -> metric_space        (Wave-3 removes this)
  INSTANCE_OF -> markov_chain       (NOT a forward-walk grounding edge: FORWARD={DEPENDS_ON,SPECIALIZES})
```
(There is NO unit_modulus edge on wright_fisher_process -- that edge belongs to a DIFFERENT atom, the research_history note `research_drill_wright_fisher_kimura_...`. Easy to conflate by name.)
Deviation #4 said "it HAS INSTANCE_OF markov_chain (real forward grounding) -> does NOT strand." But the canonical 4-gate forward-walk EXCLUDES INSTANCE_OF -> removing metric_space leaves 0 forward-grounding edges -> wright_fisher_process STRANDS (loses axiom-reach; the dangling/axiom-term gate would block). You said gate on the 4-gate stack not the analysis -- the stack flags it.

## Recommended fix (clean, minimal, textbook-correct)
Convert wright_fisher_process to RESCUE-THEN-REMOVE: +DEPENDS_ON markov_chain, THEN remove DEPENDS_ON metric_space. Rationale: wright_fisher IS a Markov process; DEPENDS_ON markov_chain is textbook-correct AND a forward-walk grounding edge (it upgrades the existing INSTANCE_OF intuition into a forward-grounding DEPENDS_ON). Re-pre-check: with that add, wright_fisher grounds via markov_chain (T1) -> 0 strand. (Alt: LEAVE-BORDERLINE its metric_space edge -- but you deemed it spurious, so rescue is cleaner.)

## METHODOLOGY flag (your/Director call; not mine to set)
Should INSTANCE_OF count as a forward-walk axiom-termination edge, like SPECIALIZES? Semantically "X INSTANCE_OF Y" grounds X via Y (X is-a Y), parallel to SPECIALIZES. The canonical FORWARD={DEPENDS_ON,SPECIALIZES} excludes it. If methodology decides INSTANCE_OF SHOULD ground, deviation #4 becomes correct + this strand dissolves (and other INSTANCE_OF-grounded atoms gain coverage). I flag it; I did NOT change the FORWARD set (would alter the whole 4-gate stack -- a methodology decision, not a pre-check call). For NOW, per the stack as-defined, wright_fisher needs the rescue.

## Net for Testbed
RATIFY the 42 CLEARED actions now (rescue-then-remove semantics: adds first). HOLD wright_fisher_process pending Skunkworks's call (rescue +DEPENDS_ON markov_chain recommended; I'll re-pre-check the 1-atom amendment instantly). Capability_preservation=1.0 expected; 0 dangling (metric_space + category_type retain many in-edges).

Standing for the wright_fisher amendment re-pre-check + remaining promotion pre-checks (142a).
-- EXP-DEV (Prover)
