# Exp-Dev -> Research: CHTV-1 substrate-as-VERIFIER HARD_PASS -- CH-P1 well-typed-accept 8/8, CH-P2 ill-typed-reject 8/8 (ZERO false-accepts; type-checker precision = 1.0). No-heat local cell. Honest framing + corpus depth finding inside.

**From:** Exp-Dev -> Research  **Date:** 2026-06-12. Hand-off anchor #1 (Curry-Howard CHTV-1). NO LLM. Local file-IO (no torch/GPU; no heat -- done while experiments paused for laptop-cooling).
**Cell:** exp_substrate_curry_howard_type_checker_cpu_v1.py.

## Result -- HARD_PASS
- CH-P1 (REAL derivation witness -> ACCEPT): 8/8 = 1.0 (>=0.75 HP).
- CH-P2 (witness with a FABRICATED edge -> REJECT): 8/8 = 1.0, **0 false-accepts** -- classical type-checker precision (non-negotiable bar met).
- Goals spanned real atoms: T2/fhrr_bind, T1/probability_distribution, T2/cleanup, T3/dijkstra, T3/astar, T1/field_axioms,
  T2/hamming_distance, T1/inner_product. Each fabricated edge (e.g. a research_drill note "DEPENDS_ON T1/topological_space") rejected.

## Honest framing (substrate-product claim, not an inflated ML result)
- The verifier is SOUND BY CONSTRUCTION: it type-checks each claimed typed edge against the substrate's real edge set, so it
  trivially accepts real chains and rejects any chain containing a non-existent edge. The non-triviality -- and the LLM
  CATEGORICAL GAP -- is that the substrate HAS an explicit, checkable typed-derivation ground-truth graph to verify against.
  An LLM has no such ground truth, so it cannot guarantee CH-P2 (hallucination-inevitability). The product claim is the
  CHECKABLE GROUND TRUTH, not a hard learning result. CH-P2 = 1.0 is the right, honest demonstration of that gap.

## Corpus depth finding (verify-before-build)
- DEPENDS_ON alone is authored only ONE layer deep: 2220 DEPENDS_ON edges but **0 depth-2 chains** (a->b->c). So multi-step
  proof verification over DEPENDS_ON-only is NOT yet feasible. I generalized the TYPING CONTEXT to the full structural-derivation
  graph {DEPENDS_ON, USES, INSTANCE_OF, SPECIALIZES, DEFINED_OVER, SHARES_MATH} -- 2491 edges, 2595 real depth-2 chains -- which
  is arguably a MORE faithful Curry-Howard framing (each edge type = a distinct typed inference rule). If you want DEPENDS_ON-only
  multi-step proofs, the lever is deeper DEPENDS_ON authoring (the dependency targets need their OWN dependencies authored).

## Routing
- **Research:** CHTV-1 HARD_PASS (substrate-as-verifier surface works). Anchor 4 (LLM-baseline CH-P6 categorical-gap) is now
  unblocked but is REMOTE-GPU (LLM inference) + would reheat the laptop -- DEFERRED pending USER go-ahead on resuming heavy runs.
  Anchor 2 (alpha-equivalence / SHARES_MATH univalence) gated on SHARES_MATH edges being populated (check Strategy commit).
  Anchor 3 (NbE cleanup-gap) is cleanup-dense -> REMOTE, also deferred for heat.
- **Exp-Dev:** CHTV-1 done as the no-heat pick from the queued hand-offs. The CPU-heavy / GPU ones (L6-PROOF needs BATCH-02
  authoring; F4 kappa_n; smoke-v2; C-axis C4; LLM baseline) remain HELD for USER go-ahead per the laptop-cooling priority.
