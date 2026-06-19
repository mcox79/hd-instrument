# exp_dev hand-off -- research: L6-PROOF FINDER 62pct authoring-gap leaf prioritization strategy (BATCH 18-25 + cheap simulation cell)

**Filed-by:** research (this drill cycle).
**Trigger:** notes/research_drill_L6_PROOF_FINDER_62pct_authoring_gap_leaf_prioritization_strategy_depth_corpus_expansion_2x_2026-06-13.md
**Pause state:** check data/orchestrator_paused.flag before ship. If paused, file
as pre-reg only; the cheap simulation cell (Anchor 1) is laptop-CPU + file-IO only and may proceed under pause if user permits; BATCH 18-25 ingest is gated.

Per [[feedback-no-experiment-design-in-prompts]]: this file points at the
research note; exp_dev autonomously designs the experiment cells. Anchor pointers
below are SUGGESTIONS for ranking + decision.

## Anchor candidates (rank-ordered)

### Anchor #1 -- L6_PROOF_DEPTH_LIFT_BATCH18_SMOKE (cheap simulation cell)

- Anchor pointer: substrate cells/exp_L6_proof_depth_lift_batch18_smoke_cpu_v1.py (to be authored by exp_dev). 1-2 hour CPU laptop, file-IO + graph BFS only, NO authoring required.
- Substrate-product reading: validates the prioritization recipe `(downstream_fanin x cross_capability_breadth x is_leaf) / authoring_cost` BEFORE committing 6-8 hours of BATCH 18-25 authoring. If smoke HARD-PASS, BATCH 18-25 is empirically grounded. If smoke HARD-FAIL, re-derive heuristic via PageRank eigenvector centrality (Kaliszyk-Urban lemma-mining) before authoring.
- Tier hint: Tier 1 (de-risk authoring commit; substrate-distinctive prioritization).
- Why now: BATCH 17 just shipped; depth re-measurement is pending; before authoring 80 more atoms, validate that the priority queue is correctly ranked. Cheap (1-2 hr CPU), reversible, decisive.
- Pre-reg thresholds: HARD-PASS top-50 simulation lifts avg depth >= 2.5 AND % T1-terminating >= 60pct (vs. baseline 1.30 / 38pct). HARD-FAIL avg depth <= 1.8 OR % T1-terminating <= 45pct. MIDDLE depth in [1.8, 2.5).

### Anchor #2 -- L6_PROOF_DEPTH_LIFT_BATCH18_INGEST (real authoring + re-measure)

- Anchor pointer: substrate cells/exp_L6_proof_depth_lift_batch18_ingest_cpu_v1.py + BATCH 18 hand-off file with 10 TIER-1 foundational primitives (discrete_fourier_transform, complex_field, inner_product_space, matrix_norm, vector_norm, pointwise_multiplication, elementwise_operation, linear_map, vector_subspace, orthonormal_basis). Authoring via Phase-2-light substrate-guided proposal tool.
- Substrate-product reading: empirically validates HARD-PASS predictions PASS-1 through PASS-5 in the research note; closes the 62pct authoring-gap leaf for ~10 specific T1 primitives; measures the empirical compounding factor per T1 atom authored.
- Tier hint: Tier 1 (engine 4 self-deducing capability scaling KPI).
- Why now: BATCH 17 just shipped; the prioritization recipe is delivered; the next natural extension is BATCH 18 to test the compounding factor.
- Pre-reg thresholds: HARD-PASS avg depth >= 2.5 AND T1-terminating >= 60pct AND leaf-dead-end <= 30pct after BATCH 18 ingest. HARD-FAIL avg depth < 1.6 OR T1-terminating < 45pct.

### Anchor #3 -- SHARES_MATH_EQUIVCLASS_TRANSITIVE_CLOSURE (Paige-Tarjan pre-filter)

- Anchor pointer: substrate cells/exp_shares_math_equivclass_transitive_closure_cpu_v1.py. Computes bisimulation quotient via Paige-Tarjan O(m log n) on ~1742-atom graph; identifies SHARES_MATH equivalence classes with Jaccard >= 0.90; tests transitive proof closure on 3 representative classes.
- Substrate-product reading: confirms whether authoring 1 SHARES_MATH representative transfers to all class members (the compounding factor multiplier). Pre-filter for BATCH 18-25 -- avoid wasting priority budget on redundant equivalence-class members.
- Tier hint: Tier 1.5 (compounding amplifier for Anchors 1 + 2).
- Why now: BATCH 18-25 efficiency depends on whether SHARES_MATH transitive closure works as predicted. Validating here gives 3-5x effective authoring coverage.
- Pre-reg thresholds: HARD-PASS 3/3 equivalence classes show transitive proof closure (1 authored representative gives proof access to all N members). HARD-FAIL < 1/3 transitive closure (signal: SHARES_MATH false-merge audit needs stricter threshold).

### Anchor #4 (DEFERRED) -- 6-EDGE-UNION PRIORITIZATION VARIANT

- Anchor pointer: same as Anchor 1 but with 6-edge-union (DEPENDS_ON + INSTANCE_OF + IS_KIND_OF + USES + SHARES_MATH + INHIBITS) for fan-in computation, per CHTV-1 generalized 6-edge-type typing context.
- Substrate-product reading: tests whether the typing-context generalization (per CHTV-1 finding) gives BETTER prioritization than DEPENDS_ON-only.
- Tier hint: Tier 2 (refinement, run after Anchor 1 baseline).
- Why now: defer until Anchor 1 baseline measured; comparison gives clean delta.

### Anchor #5 (DEFERRED) -- KNOWLEDGE PROMOTION OPERATOR PRE-PASS

- Anchor pointer: per knowledge-promotion 3x drill (research_drill_optimal_external_corpus_to_VSA_HRR_*); run KP operator BEFORE BATCH 18 to promote high-frequency low-tier atoms to T1 via promotion (cheaper than de-novo authoring).
- Substrate-product reading: tests whether promotion-vs-authoring decision step is empirically beneficial. Could reduce BATCH 18-25 authoring cost by 20-40pct.
- Tier hint: Tier 2 (cost reduction, not capability lift).
- Why now: defer until KP operator HARD-PASS confirmed in separate cell.

### Anchor #6 (DEFERRED) -- LLM-baseline soundness comparison at depth 5+

- Anchor pointer: per substrate-as-differentiable-theorem-prover drill (Anchor 4 there).
- Substrate-product reading: substrate-LLM categorical gap WIDENS at depth 5+; validate empirically.
- Tier hint: Tier 2 (product positioning; LLM-infra availability gated).
- Why now: LLM-infra not ready (only pythia-base/APIs on desktop); defer until GPU runner has LLM-baseline harness up.

## Context pointers (file paths only, not summaries)

- d:\AI\hd-instrument\notes\research_drill_L6_PROOF_FINDER_62pct_authoring_gap_leaf_prioritization_strategy_depth_corpus_expansion_2x_2026-06-13.md
- d:\AI\hd-instrument\notes\exp_dev_to_research_PROVER_DEPTH_authoring_target_62pct_proofs_deadend_at_T2_T3_leaves_author_their_deps_2026-06-13.md
- d:\AI\hd-instrument\notes\exp_dev_to_research_L6_PROOF_substrate_FINDER_HARD_PASS_sound_find_verify_prover_shallow_depth_corpus_limited_2026-06-13.md
- d:\AI\hd-instrument\notes\research_to_testbed_T1_ALGEBRA_BATCH_17_DEEPER_DEPENDS_ON_targeted_62pct_authoring_gap_leaves_TESTBED_FLAGGED_T2_T3_atoms_L6_PROOF_depth_jump_2026-06-13.md
- d:\AI\hd-instrument\notes\research_to_testbed_exp_dev_L6_PROOF_PHASE_2_SPEC_UPDATE_generalized_6_edge_type_typing_context_per_CHTV1_finding_supersedes_DEPENDS_ON_only_2026-06-13.md
- d:\AI\hd-instrument\notes\research_drill_curry_howard_atoms_as_types_substrate_dependent_types_proof_verification_2x_2026-06-12.md
- d:\AI\hd-instrument\notes\research_drill_coalgebraic_semantics_substrate_observation_state_transition_Cycle_53_extension_DisCoCat_2x_2026-06-12.md
- d:\AI\hd-instrument\notes\research_drill_shares_math_subgraph_equivalence_class_compression_connected_components_substrate_compressed_lever_set_discovery_1x_2026-06-12.md
- d:\AI\hd-instrument\notes\research_drill_optimal_external_corpus_to_VSA_HRR_substrate_ingest_methodology_knowledge_promotion_mechanism_3x_2026-06-13.md

## Contract

- exp_dev autonomously designs each cell (substrate cells/exp_*.py).
- Pre-reg thresholds (above) MUST be met for HARD-PASS verdict.
- substrate-quality-first: all cells avoid LLM-as-judge; verification is substrate-graph-internal.
- Honest negative results valued (any HARD-FAIL refines the prioritization recipe).
- No GPU required for Anchors 1, 2, 3; Anchor 6 GPU-gated.
- Run on remote desktop CPU per [[feedback-all-cpu-compute-on-remote-desktop]]; NEVER local laptop CPU for heavy compute.

## Autonomy declaration

exp_dev decides:
- Which anchor to schedule first (recommended: Anchor 1 cheap-smoke before Anchor 2 ingest).
- Whether to run anchors sequentially or in parallel (independent cells).
- Cell-level design (BFS depth limit, edge-type weighting, simulation strategy).
- Whether to use Phase-2-light substrate-guided proposal tool for BATCH 18 authoring or hand-author (proposal tool 5 min/atom strongly preferred).
- Whether to invoke SHARES_MATH false-merge audit before Anchor 3 (Jaccard >= 0.90 threshold).
