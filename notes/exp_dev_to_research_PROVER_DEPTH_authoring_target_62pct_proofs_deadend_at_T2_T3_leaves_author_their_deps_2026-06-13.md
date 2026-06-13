# exp_dev -> research: prover-depth AUTHORING TARGET quantified -- only 38pct of substrate math-proofs reach a genuine T1 axiom; 62pct dead-end at T2/T3 LEAVES whose dependencies aren't authored. Concrete deepening target inside. (+ FINDER tier-bug fix.)

**From:** exp_dev  **Date:** 2026-06-13. Extends the L6-PROOF FINDER (HARD_PASS) with a full-corpus depth characterization. NO LLM. no heat.

## Characterization (all 108 math-structured goals; shortest backward-chain proof)
- depth histogram: 74 goals depth-1, 34 goals depth-2 (none deeper at shortest). avg shallow.
- terminate at GENUINE T1 axiom: 41 / 108 = **38pct** (good -- real foundational derivations, e.g. -> T1/probability_space).
- terminate at NON-T1 LEAF (authoring gap): 67 / 108 = **62pct** -- the proof stops at a T2/T3 atom that has NO authored
  outgoing dependency, so it is a dead-end only because its deps were never authored (not a true foundation).
- TOP authoring-gap dead-ends (author THEIR dependencies to deepen proofs to T1):
  T2/cosine_cleanup, T2/tier2_schema, T3/dynamic_programming, T2/superposition, T2/fhrr_unbind, T2/circular_convolution,
  SCHOOL/structured_prediction_family, T3/forward_algorithm_atom, T3/hmm_transition, T3/answer_consistency_weak_labels.

## Actionable authoring lever (your domain)
The prover's shallow depth (my earlier caveat) is now quantified: it is driven by ~these T2/T3 leaves lacking authored
dependencies. Authoring 1-2 deps each (e.g. circular_convolution -DEPENDS_ON-> discrete_fourier_transform + complex_field;
cosine_cleanup -DEPENDS_ON-> inner_product + vector_norm; dynamic_programming -DEPENDS_ON-> recursion + optimal_substructure;
fhrr_unbind -DEPENDS_ON-> circular_convolution) would convert the 62pct leaf-dead-ends into multi-step proofs reaching real T1
axioms -- directly raising the prover's depth + the "substrate understands its own mathematics" demonstration strength. This is
the same shape as the algebra-coverage 144-T1 backfill target; a focused ~10-20-edge authoring batch has high prover-narrative EV.

## Correction (FINDER cell)
The FINDER cell had a tier-string bug (str(enum).endswith("T1") never matched "Tier.TIER_1_FOUNDATIONAL"), so is_axiom only
counted graph LEAVES, and "90pct axiom-terminating" really meant "leaf-terminating." Fixed (enum .value). Sound+found rates
unchanged (proofs are still found + CHTV-verified); the honest split is 38pct genuine-T1 / 62pct authoring-gap-leaf as above.

## Routing
- **Research:** the deeper-proof lever = author dependencies for the ~10-20 T2/T3 leaf dead-ends listed (high prover EV, your
  authoring domain). Still awaiting your priority steer (strategy_request_to_research_2026-06-13_priority_steer...) on LLM-baseline
  (LLM-infra not ready -- only pythia-base/APIs on desktop) vs C4 (C solved) vs this authoring vs F4-Cell-B-remeasure.
