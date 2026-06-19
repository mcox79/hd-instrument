# Research (Director) -> USER: ADDENDUM to T3 deeper-ingest proposal (filed 15:10; commit 49490c89) -- honest framing correction per literature drill findings. My naive proportional prediction (1.4-1.5x recall lift) was TOO CLEAN. Lit shows density-recall functional form is UNFIT (no clean scaling law). Revised honest framing: target +15 absolute points at 3-hop with 20% coverage (PullNet 18-point delta anchor across 2x density change); HARD-FAIL if <+5 absolute (= NOT pure-coverage hypothesis). + 1 correction on targeting strategy (HYBRID per Wei TKDD 2024 beats pure-targeted). Substance + 3-option scope ask unchanged.

**From:** Research (Director); USER-routed
**To:** USER
**Date:** 2026-06-18 ~16:10 PDT
**Re:** T3 proposal addendum -- honest framing correction. fname_v2.

## TL;DR

My T3 proposal earlier (15:10) used a naive proportional model predicting 1.4-1.5x recall lift at 3-4 hops from doubling coverage. The Director-side literature drill just returned (Item 4 of the 5 joint initiatives) and showed the actual empirical curve is more nuanced than my naive math implied. **Honest framing correction below; the substance + the 3-option scope-decision ask are unchanged.**

## What the literature actually says (24 URLs verified; ASCII; factual-retrieval)

```
EMPIRICAL ANCHORS for coverage-vs-recall in multi-hop KG QA:
  PullNet on WebQuestionsSP   68.1% -> 50.3% Hits@1 at 50% retention
  MetaQA-3hop                  91.4% -> 85.2% (domain-dependent cliff sharpness)
  EmbedKGQA "Half-KG"          degradation pattern documented
  Per-hop error compound       ~1 - (1 - epsilon)^L per KGC review

WHAT'S WELL-ATTESTED:
  - Density-up -> recall-up at coarse anchor points (10-25 absolute Hits@1 across
    50% retention deltas)
  - The MECHANISM (sparse KG -> per-hop failure rate compounds geometrically)

WHAT'S NOT IN THE LITERATURE:
  - A clean scaling law for recall vs density
  - A clean scaling law for recall vs depth
  - Closed-form extrapolation -- speculative
```

## Honest framing correction

```
OLD (my 15:10 framing):
  "Naive proportional model: recall(3-hop) baseline 0.368 -> new 1.4x baseline
   = ~0.515 at 10k coverage"

REVISED HONEST (lit-anchored):
  HARD-PASS prediction at 20% WordNet coverage (vs current 4.2%):
    Lift 3-hop recall by +15 absolute points or more (0.368 -> >=0.518)
    Anchor: PullNet 18-point delta across ~2x density change in published curve
  
  HARD-FAIL prediction:
    If lift <+5 absolute at 20% coverage (0.368 -> <0.418), the depth-cliff
    is NOT pure-coverage hypothesis -> deeper finding (algorithmic/walker-policy/
    refusal-threshold cause); valuable honest negative

  HONEST SCOPE:
    Density-up-recall-up is empirically robust at coarse points; the precise
    functional form is UNFIT in literature -- treat any quantitative extrapolation
    as speculative within the wider lit-attested band
```

## Targeting-strategy correction (also per lit-drill)

```
OLD (my 15:10 framing):
  "by SEMANTIC FREQUENCY + 1-hop HYPERNYM gap-closure"

REVISED (HYBRID per Wei TKDD 2024 finding -- pure-targeted is NOT Pareto-dominant):
  60% Galarraga/Razniewski completeness-prediction
     (low-in-degree HYPERNYM targets where existing 5k synsets have unverified
      parent links; AMIE-style rule mining)
  30% Corpus-frequency (W3C OntoLex-FrAC pattern; most-referenced synsets)
  10% Dalton EQFE frontier
     (expand at BROAD's HYPERNYM-failing nodes specifically; query-driven)
  
  AVOID pure-uniform-random (worst per literature)
  AVOID pure-centrality (sub-Pareto per Wei TKDD 2024)
  AVOID RL-learned-policy (11th-rule-adverse per GPA 2020)
```

## Substantively unchanged

- 3-option scope-decision ask stays: (a) GO / (b) HOLD-post-FrameNet / (c) REFRAME
- Cost estimate stays: ~3-4h total (Bucket B ingest + B-α SCALE-UP variant)
- Cert-conditions stay (deterministic-BFS + 5th gate + per-benchmark independent gold + min-cert-along-path)
- Director lean stays: (a) GO with the honest revised bands (or (b) for cleaner timing post-FrameNet)
- Composes-with stays: FrameNet (independent; orthogonal); BROAD baseline; multi-hop-provenance gate

## Why this matters for honest scope

The original naive proportional framing implied a SPECIFIC quantitative prediction (1.4-1.5x). That over-stated my confidence in the curve shape. The lit-honest framing presents HARD-PASS and HARD-FAIL as wider bands tied to empirical anchors + acknowledges curve-shape uncertainty. **This is the negativity-bias-symmetric discipline cutting toward PRECISION** -- same pattern as the morning's 432-map "61 distinct claims NOT 432 capabilities" correction.

Per the ratified honest-scope policy (ASK 3 today): the substrate answers what it has PROVEN/MEASURED, with measured-bounds-not-fundamental qualifiers. This addendum is the same discipline applied to my own prediction-making.

## Standing

- ME: addendum filed; the substance + 3-option ask stand; standing reactive on your scope-decision (T3 GO/HOLD/REFRAME) + your separate FrameNet ARC-3 sign-off.
- SUBSTRATE state unchanged: atoms 41330 / CERT 569 honest / engine 6 LIVE.
- Items 2 + 3 cell-design scaffolds filed to Skunkworks + Exp-Dev for finalization on the respective USER GOs.

Tag: user_t3_proposal_addendum_honest_framing_correction_lit_drill_naive_proportional_too_clean_curve_unfit_revised_hard_pass_15_absolute_3_hop_20_coverage_pullnet_18_point_2x_density_hard_fail_5_absolute_not_pure_coverage_targeting_hybrid_wei_tkdd_2024_substance_3_option_unchanged_lit_24_urls_verified_factual_pullnet_webquestionssp_68_1_50_3_50_retention_metaqa_3hop_91_4_85_2_embedkgqa_half_kg_per_hop_compound_kgc_review_density_recall_coarse_anchor_attested_mechanism_sparse_compound_not_literature_clean_scaling_law_density_depth_closed_form_speculative_honest_correction_old_naive_proportional_0_368_1_4x_0_515_10k_revised_hard_pass_20_coverage_15_absolute_3_hop_0_368_0_518_anchor_pullnet_18_point_2x_density_hard_fail_5_absolute_0_368_0_418_not_pure_coverage_algorithmic_walker_refusal_honest_negative_honest_scope_density_recall_robust_coarse_functional_unfit_speculative_quantitative_extrapolation_attested_band_targeting_strategy_old_semantic_frequency_1_hop_gap_revised_hybrid_wei_tkdd_2024_60_galarraga_razniewski_completeness_low_in_degree_hypernym_unverified_parent_amie_30_corpus_frequency_w3c_ontolex_frac_most_referenced_10_dalton_eqfe_frontier_query_avoid_uniform_random_centrality_sub_pareto_rl_11th_rule_adverse_gpa_2020_substantively_unchanged_3_option_scope_ask_a_go_b_hold_post_framenet_c_reframe_cost_3_4h_bucket_b_alpha_scale_up_cert_conditions_deterministic_bfs_5th_per_benchmark_independent_min_cert_along_path_director_lean_a_go_honest_revised_b_cleaner_timing_post_framenet_composes_framenet_independent_orthogonal_broad_baseline_multi_hop_provenance_why_matters_honest_scope_original_naive_implied_quantitative_prediction_over_stated_confidence_curve_lit_honest_hard_pass_fail_wider_bands_anchors_acknowledges_uncertainty_negativity_bias_symmetric_precision_morning_432_map_61_distinct_not_432_capabilities_ratified_honest_scope_ask_3_substrate_proven_measured_measured_bounds_not_fundamental_discipline_own_prediction_making_standing_addendum_filed_substance_3_option_stand_reactive_scope_t3_go_hold_reframe_separate_framenet_arc_3_substrate_unchanged_41330_cert_569_engine_6_items_2_3_scaffolds_skunkworks_exp_dev_finalization_respective_user_gos_fname_v2_50

-- Research (Director); USER-routed
