# exp_dev hand-off -- research: uniform-criterion SHARES_MATH AAA-3-definitive

Filed-by: research
Filed: 2026-06-13
Trigger: 2x DEEP drill on AAA-3 confounded 0.94x + provisional 1.33x; clean uniform-criterion test designed
Source: d:/AI/hd-instrument/notes/research_DRILL_uniform_criterion_SHARES_MATH_design_AAA3_definitive_load_bearing_axis_test_2026-06-13.md
Pause state: check d:/AI/hd-instrument/data/orchestrator_paused.flag before ship

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides anchor pointers + substrate-product reading + tier hints + why-now signals only. Exp_dev owns the actual experiment design (envelope-fail-bands, smoke gate, queue_add, REMOTE VERIFY).

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY): CELL-AAA-3-definitive uniform-criterion test
  - **Anchor pointer:** AAA-3-definitive cell, criterion C3 (USES-rule shared-capability) + DC-SBM null + bootstrap CI + permutation test
  - **Substrate-product reading:** if HARD-PASS, substrate gains empirically validated two-axis architecture (epistemic tier x structural-role); composes with 9d spectral pillar -> 11d structural-cognition observability claim; LLM categorical gap WIDENS
  - **Tier hint:** Tier 5 substrate metacognition (architectural-claim validation)
  - **Why-now:** unblocks 13th methodology rule 2nd-empirical-appearance; closes the canonical AAA-3 0.94x confound; cheap (~30 min CPU, 0 authoring)
  - **Pre-reg numeric thresholds:**
    - HARD-PASS: excess_ratio >= 1.25, 95% CI lower > 1.0, permutation p < 0.01, naive ratio >= 1.30
    - HARD-FAIL: excess_ratio <= 1.05 OR 95% CI crosses 1.0 OR permutation p >= 0.10
    - MIDDLE_BAND: 1.05 < excess_ratio < 1.25 -> rerun C2 cross-check before verdict

### Anchor 2 (CROSS-CHECK, only if MIDDLE_BAND): CELL-AAA-3-FCA-crosscheck
  - **Anchor pointer:** same null model + FCA-intent criterion C2, tau=0.40 pre-registered
  - **Substrate-product reading:** triangulates C3 result; if both criteria converge on HARD-PASS or both on HARD-FAIL, architectural claim is robust to criterion choice
  - **Tier hint:** Tier 5
  - **Why-now:** only fire if Anchor 1 lands MIDDLE_BAND; otherwise defer
  - **Cost:** ~1 day attribute-set construction + ~30 min CPU

### Anchor 3 (SENSITIVITY, optional): CELL-AAA-3-4block-DCSBM
  - **Anchor pointer:** same C3 criterion but DC-SBM with 4 blocks (T0/T1/T2/T3) x (TOOLS/MATERIALS) = 8 blocks
  - **Substrate-product reading:** confirms structural-role axis is orthogonal to epistemic tier (the actual 13th-rule claim)
  - **Tier hint:** Tier 5
  - **Why-now:** sensitivity check; run only if Anchor 1 HARD-PASS to strengthen orthogonality claim
  - **Cost:** ~30 min CPU additional

## Context pointers (file paths, not summaries)

  - Research source note: d:/AI/hd-instrument/notes/research_DRILL_uniform_criterion_SHARES_MATH_design_AAA3_definitive_load_bearing_axis_test_2026-06-13.md
  - 13th methodology rule (1st USER appearance): C:/Users/marsh/.claude/projects/d--AI/memory/substrate_architecture_two_orthogonal_axes_epistemic_foundationality_vs_substrate_load_bearing_capability_primitive_USER_craftsman_distinction_13th_methodology_rule_candidate_2026-06-13.md
  - 13th methodology rule (2nd empirical appearance): C:/Users/marsh/.claude/projects/d--AI/memory/substrate_architecture_3_axis_EMPIRICALLY_ORTHOGONAL_Cell_3_KP_P6_HARD_PASS_USER_craftsman_VERBATIM_corroborated_13th_rule_2nd_appearance_2026-06-13.md
  - 12th methodology rule context: C:/Users/marsh/.claude/projects/d--AI/memory/substrate_methodology_rule_12th_universal_operators_field_specific_signal_extractors_first_class_field_partition_routing_H3_HYBRID_first_appearance_2026-06-13.md
  - 11th methodology rule (held-out test): C:/Users/marsh/.claude/projects/d--AI/memory/feedback_held_out_test_methodology_required_for_macro_F1_claims_USER_LOCKED_11th_methodology_rule_2026-06-13.md
  - 7th rule (never-lock-in-frameworks): C:/Users/marsh/.claude/projects/d--AI/memory/feedback_always_reconsider_frameworks_dont_lock_in_prematurely_USER_LOCKED_2026-06-13.md
  - 10th rule (verify-before-asserting cluster): C:/Users/marsh/.claude/projects/d--AI/memory/substrate_methodology_rule_verify_before_asserting_5_class_cluster_cycle_51_F4_CH_P6_P4_smoke_GHRR_all_caught_before_report_2026-06-13.md
  - 9d spectral pillar: C:/Users/marsh/.claude/projects/d--AI/memory/substrate_9d_spectral_observability_pillar_clustered_codebook_BBP_spike_extension_8d_SURVIVES_revision_substrate_product_STRENGTHENS_2026-06-13.md
  - cap_map (current state): d:/AI/hd-instrument/notes/substrate_capability_map.md

## Contract

  - Exp_dev owns: envelope-fail-band registration, smoke gate, queue_add.sh ship, REMOTE VERIFY, self-test per formula-selftests
  - Research provides: criterion + null-model + threshold pre-reg (this note) and methodology citations
  - Strategy owns: cap_map row creation/bump on verdict
  - Verdict_handler owns: post-verdict synthesis (this is a load-bearing-axis claim, importance=CRITICAL on HARD-PASS or HARD-FAIL)
  - Pause-gated: yes; check data/orchestrator_paused.flag before ship

## Autonomy declaration

Exp_dev decides:
  - Implementation language (Python expected) and library choices (networkx, graph-tool, igraph)
  - DC-SBM sampler choice (Karrer-Newman MCMC vs fast spectral approximation)
  - Random seed protocol and replicate count (suggested N=200; exp_dev may scale per CPU budget)
  - Smoke-gate canary (suggested: run on 100-atom subset first, verify ratio computation correct before full sweep)
  - Exact pre-reg file location and format

Research does NOT decide:
  - Code structure
  - Cell file naming beyond CELL-AAA-3-definitive convention
  - Queue priority

Verdict mapping (suggested, exp_dev may revise):
  - HARD-PASS bands per Anchor 1 numeric thresholds above
  - HARD-FAIL bands per Anchor 1 numeric thresholds above
  - Auto-trigger Anchor 2 ONLY if MIDDLE_BAND
  - Auto-trigger Anchor 3 ONLY if Anchor 1 HARD-PASS
