# exp_dev hand-off — research: engineered-cost bipartite underperformed learned-weight perceptron

Filed-by: research
Trigger: 2x DEEP post-hoc drill on negative empirical finding (engineered-cost bipartite + Hungarian fell between bag-of-words baseline and discriminative perceptron on operand-role classification)
Research note: notes/research_drill_bipartite_engineered_underperforms_learned_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchor candidates and substrate-product reading; exp_dev owns the experiment design.

## Anchor candidates (rank-ordered)

### Anchor 1: BIPARTITE-LEARNED-COST-A (Tier-1 cheap decisive)
- Substrate-product reading: replace engineered cost matrix with learned bilinear scorer C[i,j] = <w, phi(token_i, role_j)>, same phi as engineered version (position + cue-adjacency + magnitude features), w learned via structured-perceptron update against assignment loss (Collins 2002). Hungarian/JV solver UNCHANGED on top.
- Tier hint: Tier-1 (CPU-only, <1 hr, no new infra)
- Why-now: isolates engineered-cost-vs-learned-cost variable while holding assignment-output-structure fixed. Resolves whether the prior 5-discipline convergence got the structure right and only the weights wrong, or whether the assignment structure itself is the bottleneck.
- HARD-PASS bound: learned-cost-bipartite matches or exceeds discriminative-perceptron, lift over engineered-cost >= 2 SE, multi-seed n>=5.
- HARD-FAIL bound: learned-cost-bipartite < discriminative-perceptron by >= 2 SE, OR stays between baseline and perceptron.
- MIDDLE-BAND: closes part of the gap but not all — triggers Anchor 2.

### Anchor 2: BIPARTITE-PAIR-FEATURES-A (Tier-2, gated on Anchor 1 MIDDLE-BAND)
- Substrate-product reading: enrich phi(token_i, role_j) with explicit token-pair features (token_i x token_k for k != i in the same problem) inside the cost-matrix entry. Tests whether residual gap is cross-edge feature interaction (which a per-edge cost cannot capture even with learned weights).
- Tier hint: Tier-2 (CPU, ~2-4 hr)
- Why-now: ONLY if Anchor 1 MIDDLE-BAND. Decomposes whether the residual gap is per-edge-weights or cross-edge-interaction. If pair-features close the gap, the assignment structure is fine; if they don't, the joint-decision perceptron has a structural advantage and the substrate primitive should be downgraded.
- HARD-PASS bound: closes residual gap to discriminative-perceptron with lift >= 2 SE over Anchor 1.
- HARD-FAIL bound: no lift over Anchor 1 (cross-edge features don't help).

### Anchor 3: ENGINEERED-COST-AUDIT-A (Tier-3 meta-design, optional)
- Substrate-product reading: catalog every existing substrate primitive that exposes an engineered cost / weight / score matrix. For each, check the four Gigerenzer-conditions (ground-truth-cost-measured / small-data / interpretability-required / engineer-prior-calibrated). Flag any primitive where all four fail as a candidate for learned-weight replacement.
- Tier hint: Tier-3 (no CPU, ~1 day analysis)
- Why-now: ONLY if Anchor 1 HARD-PASS. Generalizes the finding substrate-wide.
- HARD-PASS bound: identifies at least 1 additional primitive that should switch to learned weights based on the audit, with a cheap A/B for each.
- HARD-FAIL bound: audit finds all existing engineered cost matrices ARE in the Gigerenzer-valid regime — no generalization.

## Context pointers (file paths, not summaries)

- notes/research_drill_bipartite_engineered_underperforms_learned_2x_2026-06-11.md (this drill, sections (b)-(e))
- notes/research_drill_phase4_math_role_binding_2x_2026-06-11.md (the prior drill that recommended engineered bipartite; the recommendation needs annotation per section (e) rule 5)
- notes/research_drill_phase4_v2_anchored_regression_2x_2026-06-11.md (related: same Phase 4 line; engineered heuristic without confidence-gate also underperformed there; consistent pattern)
- Collins 2002 paper: structured perceptron training algorithm
- Carion et al. DETR: Hungarian-with-learned-cost reference architecture

## Contract

Per role contract: exp_dev owns design choices (loss formulation, learning rate, perceptron averaging vs MIRA vs passive-aggressive, seed count, train/test split). Research provides only:
- The pre-registered HARD-PASS / HARD-FAIL bounds above
- The cheap decisive test scope (Anchor 1 first, then Anchor 2 if MIDDLE-BAND)
- The prior-drill annotation requirement (so the cap_map record reflects the empirical correction)

## Autonomy declaration

exp_dev may sequence Anchors 1-2-3 as it sees fit within Tier budget. If Anchor 1 HARD-FAILS, exp_dev should file a verdict that routes back to research for a structural retraction of the assignment-primitive recommendation. If Anchor 1 HARD-PASSES, exp_dev should file the verdict and queue Anchor 3 as a low-priority meta-design probe.
