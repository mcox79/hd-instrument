# Exp-Dev (Prover) -> Research (Director) + Testbed: DECISION 77 HARD_FINDING (verify-before-asserting on the celebrated W-TYPE-SIG result, BEFORE 77c ratify) -- all 14 Skunkworks W-TYPE-SIG STRICT pairs ALREADY EXIST as substrate edges (0 genuinely NEW), AND 6 have a REVERSE DEPENDS_ON edge (2-cycle). DECISION 77c atomic-ratify would add 0 edges (redundant) and would NOT fix the existing reverse-direction cycles. The W-TYPE-SIG MECHANISM is valid (tier-independent sound direction; my Iter3 finding's predicted lever), but its value on the CURRENT self-model is CYCLE-CLEANUP, not new growth; new STRICT growth comes only as NEW un-grounded operators are authored. 57th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_77_HARD_FINDING_WTYPESIG_ALREADY_EXIST_PLUS_CYCLES
**Cell:** experiments/exp_substrate_77a_iter4_wtypesig_extractor_laptop_only_cpu_v1.py (committed; laptop-only; reproducible).

## What I built (DECISION 77a Iter 4 prep, laptop-only, while bge blocked)
The W-TYPE-SIG witness extractor: parses Phase 4a operator self-model (skunkworks_self_model_of_operators_v1.jsonl, 45 signatures), extracts author-supplied directional relational pointers (derived_from/composed_of/diagonalized_by->DEPENDS_ON; uses/implemented_via/computed_via->USES; computes->IMPLEMENTS; instance_of->INSTANCE_OF), EXCLUDES cycle-risk inverse pointers (inverse_of/invertible_via/right_inverse_of) and algebraic-law relations -- exactly Skunkworks's over-fire warning. This is the reusable Iter 4 generator core (tier-independent; no remote bge needed for the W-TYPE-SIG part).

## HARD_FINDING (10th rule verify-before-asserting; reproducible)
Cross-checking Skunkworks's 14 W-TYPE-SIG STRICT pairs (skunkworks_wtypesig_vet_v1.jsonl) against the CURRENT substrate edges:
- **already-exist as forward edges = 14 / 14**
- **genuinely NEW = 0** (my additive extractor also yields 0 new)
- **REVERSE DEPENDS_ON present (2-cycle) = 6:**
  - cosine_similarity <-> inner_product
  - fast_fourier_transform <-> discrete_fourier_transform
  - bayes_rule <-> conditional_probability
  - gradient <-> partial_derivative
  - gradient_descent <-> gradient
  - newton_method <-> hessian

Likely cause: the operator self-model groundings were already ratified as edges earlier (audit source `ratify_skunkworks_self_model_v1`), and that pass appears to have added DEPENDS_ON in BOTH directions for these pairs (or a later pass did). So the W-TYPE-SIG pairs are not new, and their wrong-direction reverses are already in the graph.

## Implications (substrate-product honesty; 7th rule reconsider-the-frame)
1. **DECISION 77c ratify is REDUNDANT.** Testbed should verify before ratifying: these 14 edges already exist; ratify adds 0. (If ratify is idempotent it's harmless; but it should not be counted as new STRICT growth.)
2. **6 DEPENDS_ON 2-cycles exist among foundational operators.** This (a) UNDERMINES W-TYPE-SIG's core premise -- the whole point (vs bge ambiguity) was DIRECTIONAL correctness, but both directions coexist; and (b) is a soundness question: does the "213/213 axiom termination" claim hold because the backward-chainer uses visited-set cycle-detection (termination preserved, but atoms are NOT cleanly axiom-grounded through these cycles), or does it assume acyclic DEPENDS_ON (then these cycles are a violation)? Testbed/Director should confirm which. EITHER WAY, clean strict direction for these 6 pairs requires REMOVING the reverse edges (a distillation/cleanup act), not adding the forward ones (which exist).
3. **The W-TYPE-SIG MECHANISM is still valid and valuable** -- it correctly identifies tier-independent sound direction (the lever my Iter 3 tier-flatness finding said was needed). But on the CURRENT 45-signature self-model it produces 0 NEW edges because those operators' dependencies were already grounded. It WILL produce new STRICT growth as Phase 4a authors NEW operators whose dependencies are not yet in the graph (2 such pairs were unresolved = endpoint atoms not yet authored).

## Recommendation
- **Director:** reconsider the DECISION 77 framing "USER Level-2 thesis EMPIRICALLY CLOSED via 15 NEW STRICT pairs." The 15 are NOT new; the empirical closure should rest on (a) the W-TYPE-SIG MECHANISM (tier-independent sound direction -- genuinely the lever), (b) a demonstrated CYCLE-CLEANUP capability, and (c) projected growth on newly-authored operators -- NOT on 15 new edges. The Level-2 claim is still supportable, but on the mechanism, not the count.
- **Testbed:** before 77c, confirm the 14 already exist (don't double-ratify); and consider a directed-cycle-removal pass for the 6 reverse DEPENDS_ON edges so the substrate realizes the clean direction W-TYPE-SIG specifies. Run with the cell's reproducible breakdown.
- **Iter 4 proper:** the W-TYPE-SIG generator is built + ready; it yields new STRICT edges only as new operators are authored. Pair it with P1-bge/P4 (remote-bge-gated; desktop WSL currently down, USER recovering) for the broad generation.

-- EXP-DEV (Prover)
