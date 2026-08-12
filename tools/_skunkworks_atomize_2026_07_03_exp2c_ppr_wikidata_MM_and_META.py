"""
Skunkworks A5-gated atomization for Exp 2C landed VET.

Cell: exp_substrate_stage1_apply_exp2c_ppr_walk_synthesized_wikidata_bridges_smoke_2026_07_03
Verdict-off-disk: MEASURED_MECHANISM (scope-narrowed to hub-concept 2-hop bridges).
Cell-author's own recommendation was MEASURED_MECHANISM; audit confirms tier.

OFF-DISK RECOMPUTE (Fix#28):
  per-arm means (3 seeds x 50 queries = 150 units):
    baseline_char_trigram_hop1_alone = 0.3467 (seeds 0.34/0.30/0.40)
    main_ppr_recovered              = 0.9933 (seeds 1.00/1.00/0.98)
    pos_ctl_ppr_from_true_bridge    = 1.0000 (seeds 1.00/1.00/1.00)
    neg_ctl_ppr_from_random         = 0.1333 (seeds 0.14/0.12/0.14)
  margin main-neg = 0.860 (well above discriminator gate 0.50)
  combined recovery on missed-by-hop1 = 97/98 = 0.9898
  ppr_mass_max_deviation = ~4.6e-14 across all seeds (mass conservation ok)
  kg_signal_local_ok all 3 seeds; cardinality_ok True; arms_differ True

MID-SMOKE ADJUSTMENT AUDIT:
  (1) SYNTHESIZER REDESIGN (bridge_deg cap 3-50 -> 5-100000): LEGITIMATE + SCOPE-NARROWS.
      KG topology discovered off-disk (5230 leaves, 126 d=2, 15 hubs d>5); at deg 3-50
      only 3 candidate bridges existed. Widening to deg>=5 is honest re-scoping to what
      the KG actually contains. HOWEVER: the actual B pool collapsed to 3 hub concepts
      (Q11348=function deg 295, Q11563=number deg 44, Q246672=mathematical object deg 41)
      because the top-3 mega-hubs (Q65943 deg 1515, Q24034552 deg 1501, Q8366 deg 796)
      are UNLABELED in the shard aliases[0] source (verified off-disk) and were filtered
      out by the "B has label" requirement. Result: the claim scope is "PPR recovers
      hub-concept bridges (B in labeled hubs with deg 41-295)", NOT "PPR recovers 2-hop
      bridges in general". This is a genuine scope narrowing but the discovery was honest.
  (2) NEG_CTL 0.10 -> 0.20 + margin gate (MAIN - NEG >= 0.50): LEGITIMATE STRUCTURAL.
      Bipartite-forest topology genuinely creates residual mass diffusion paths through
      multi-hub leaves. NEG_CTL landed 0.12-0.14 consistently; margin observed 0.860 vs
      gate 0.50 = HUGE buffer. Not Goodhart: the discriminator gate held on a much
      stronger criterion (margin) than the loosened absolute threshold. META_RULE_M
      adaptive-with-discriminator-gate is real, not ad-hoc: the gate is defensible
      because the KG topology is measurable and the margin is far from the gate.
  (3) LABEL SOURCE atoms.jsonl name -> shard aliases[0]: LEGITIMATE + FLAGS BUG.
      Verified off-disk: atoms.jsonl `name` field is trivial "wikidata Qxxx" placeholder
      for all 5,360 Wikidata entities (SUBSTRATE INFRASTRUCTURE BUG - name field never
      populated with real semantic label). shard aliases[0] gives 5,360/5,371 real labels
      (function, number, mathematical object, etc). PPR uses graph structure only (no
      labels); label source affects ALL arms uniformly through query_text encoding
      (baseline and main both use same labels). No PPR-favoring exploit. HOWEVER: the
      atoms.jsonl bug is a real substrate infrastructure issue that hides label
      information from downstream substrate-KB queries and should be routed to Testbed.

CROSS-ARC OVERLAP CHECK:
  Substrate-KB query for "PPR walk 2-hop bridge Wikidata KG typed relations dense
  semantic" returned unrelated WordNet/FrameNet atoms at cosine<0.32; no prior cell
  operationalizes PPR on Wikidata-adapted KG. Genuinely novel; immediate parents Exp 2
  (numeric PPR proof, 20-entity synthetic KG POS_CTL=1.000) and Exp 2B
  (HALT_KG_DATA_AVAILABILITY_FLOOR_BREACH on HotpotQA distractor mini-KGs, revival
  criterion mean_edges_per_node >= 1.5).

TIER RATIONALE (MEASURED_MECHANISM):
  Not full CG because:
    (a) Mid-smoke scope narrowing (deg cap 3-50 -> 5-100000) crosses the boundary of
        pre-registered claim. Pre-reg said "2-hop bridges"; landing proves "hub-concept
        2-hop bridges" only.
    (b) BY-CONSTRUCTION-adjacent regime: hub-concept bridges are STRUCTURALLY favored
        for PPR recovery because in bipartite hub-and-spoke KGs, PPR mass from any leaf
        neighbor concentrates on the hub. This mirrors Exp 2's 20-entity synthetic
        near-saturation but in a real KG. The mechanism proof is real; the difficulty
        level of the test is unclear.
    (c) NEG_CTL threshold adjustment used up a discriminator freedom (rescued cleanly by
        margin gate but consumed one).
  Is MM (not HF): mechanism DOES work; recovery 0.99 at 5,371-entity real KG scale is
  a genuine measurement; the proven bound is "PPR-walk recovers hub-concept 2-hop
  bridges at r@5 = 0.99 on Wikidata-adapted KG in this scale/topology regime".

DECISION-POINT CLOSURE:
  Retrieval-architecture decision-point (PPR-walk viable at real-semantic-KG scale vs
  encoder-swap required) is CLOSED WITH SCOPE-ANNOTATION. PPR-walk IS viable for the
  hub-concept-bridge class in the Wikidata substrate. Encoder-swap DEFERRED. Full
  extrapolation to non-hub bridges would require KG that has non-hub bridges, which the
  current Wikidata partition structurally lacks - this is a data-availability bound on
  the substrate, not a mechanism bound on PPR.

Two atoms filed:
  (a) math MEASURED_MECHANISM: PPR recovers hub-concept 2-hop bridges on Wikidata KG
  (b) meta MM_TENTATIVE_METHODOLOGY: three-adjustments-with-discriminator-margin-gate
     protocol validates when structural rationale is defensible + margin buffer >= 1.5x
     original threshold
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META_ATOMS = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))
COMMIT = "3bea99513"

# ============= ATOM (a): math MEASURED_MECHANISM PPR hub-bridge recovery Wikidata =============
atom_mm = {
    "id": ("math::T3/EXP_substrate_stage1_apply_exp2c_ppr_walk_synthesized_wikidata_bridges_smoke_"
           "MEASURED_MECHANISM_hub_concept_bridge_recovery_r5_0p9933_across_3_seeds_150_queries_"
           "combined_missed_by_hop1_recovery_97of98_0p9898_pos_ctl_1p000_neg_ctl_0p1333_margin_"
           "0p860_baseline_char_trigram_hop1_alone_0p3467_wikidata_kg_5371_entities_5489_undirected_"
           "edges_bipartite_forest_5230_leaves_126_d2_15_hubs_deg_gt_5_actual_bridge_pool_collapsed_"
           "to_3_labeled_hubs_Q11348_function_deg295_Q11563_number_deg44_Q246672_mathematical_"
           "object_deg41_because_top3_megahubs_Q65943_1515_Q24034552_1501_Q8366_796_are_unlabeled_"
           "in_shard_aliases0_source_scope_narrowed_from_prereg_2hop_bridges_general_to_hub_concept_"
           "bridges_only_ppr_mass_conservation_max_dev_4p6e14_all_seeds_kg_signal_local_ok_all_"
           "seeds_cardinality_ok_arms_differ_ok_1_legit_exemption_seed11_seed17_main_pos_both_all_"
           "ones_saturated_regime_alpha_0p15_iters_5_topk_5_ndim_trigram_1024_wall_4p4s_2026-07-03"),
    "name": ("EXP substrate_stage1_apply_exp2c_ppr_walk_synthesized_wikidata_bridges_smoke "
             "MEASURED_MECHANISM_HUB_CONCEPT_BRIDGE_RECOVERY (r@5=0.993 main, 0.99 recovery on "
             "missed-by-hop1, POS 1.000, NEG 0.133, margin 0.860; scope narrowed mid-smoke from "
             "2-hop bridges to hub-concept bridges)"),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Experiment record: Exp 2C landed 2026-07-03 (local SMOKE, 4.4s wall). PPR-walk on a real "
        "5,371-entity Wikidata-adapted KG (5,510 typed triples, 5,489 undirected edges, mean "
        "edges/node 2.19-2.20 measured) recovers 2-hop bridge entities at recall@5 = 0.9933 "
        "(seeds 11/17/23: 1.00/1.00/0.98) vs char-trigram-hop1-alone baseline 0.3467. On the "
        "missed-by-hop1 subset the recovery rate is 97/98 = 0.9898 (POS_CTL from true bridge = "
        "1.000, NEG_CTL from random unrelated entity = 0.1333, margin main-neg = 0.860). "
        "SCOPE (audited): the claim is proven for the HUB-CONCEPT 2-hop bridge class only. The "
        "actual bridge pool collapsed to 3 labeled hubs (Q11348 'function' deg 295, Q11563 "
        "'number' deg 44, Q246672 'mathematical object' deg 41) because (i) the Wikidata KG has "
        "bipartite-forest topology (5,230 leaves + 126 deg-2 + 15 hubs with deg>5 as verified "
        "off-disk from the relations file); (ii) the top-3 mega-hubs (Q65943 in-degree 1515, "
        "Q24034552 in-degree 1501, Q8366 in-degree 796) are UNLABELED in the shard aliases[0] "
        "label source and were filtered out by the 'B has label' requirement; (iii) the "
        "synthesizer's original prereg deg cap 3-50 found only 3 candidate bridges so was widened "
        "to 5-100000 mid-smoke. THREE MID-SMOKE ADJUSTMENTS: (1) synthesizer redesign (deg cap "
        "3-50 -> 5-100000): LEGITIMATE + SCOPE-NARROWS (honest KG topology discovery, but claim "
        "scope shifts from '2-hop bridges' to 'hub-concept bridges'); (2) NEG_CTL threshold "
        "0.10 -> 0.20 with margin gate MAIN-NEG >= 0.50: LEGITIMATE STRUCTURAL (bipartite-forest "
        "topology creates real residual mass diffusion; observed margin 0.860 is 1.72x the gate "
        "so the discriminator held on a much stronger criterion than the loosened absolute); "
        "(3) label source atoms.jsonl name -> shard aliases[0]: LEGITIMATE data-quality workaround "
        "that FLAGS a substrate infrastructure bug (atoms.jsonl `name` field is trivial 'wikidata "
        "Qxxx' placeholder for all 5,360 Wikidata entities; real labels only available via shard "
        "aliases[0]; PPR itself uses graph structure only so label source does not favor any arm). "
        "The mechanism claim IS real; scale delta 268x over Exp 2's 20-entity synthetic KG is "
        "genuine; POS_CTL 1.000 replicates Exp 2 mechanism proof at real KG scale; margin 0.860 "
        "on a real bipartite-forest KG is a strong discriminator. Not full CG because the "
        "scope-narrowing and NEG_CTL threshold adjustment consumed pre-registered freedoms. "
        "Not HF because the mechanism does work as advertised for the scope where the KG has "
        "labeled hubs. TIER: MEASURED_MECHANISM with proven bound: 'PPR-alpha=0.15-5-iters "
        "recovers hub-concept 2-hop bridges at r@5=0.99 on Wikidata-adapted KG in bipartite-"
        "forest topology when B is a labeled hub with degree 41-295'. Substrate-KB overlap "
        "check: top hits WordNet/FrameNet at cosine<0.32, no prior PPR-on-Wikidata operationalization; "
        "genuinely novel. Decision-point closure: retrieval-architecture decision CLOSED WITH "
        "SCOPE-ANNOTATION; PPR-walk viable for hub-concept-bridge class; encoder-swap DEFERRED; "
        "full extrapolation to non-hub bridges gated by data availability (Wikidata partition "
        "structurally lacks non-hub bridges), not by mechanism."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_record",
        "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
        "metric_type": "recall_at_5_hub_concept_2hop_bridge_recovery_ppr_walk",
        "experiment_path": "experiments/exp_substrate_stage1_apply_exp2c_ppr_walk_synthesized_wikidata_bridges_smoke_2026_07_03.py",
        "prereg_path": "preregs/2026-07-03_exp2c_ppr_walk_synthesized_wikidata_bridge_queries.md",
        "metrics_paths": ["data/exp_exp2c_smoke_local/metrics.json"],
        "cell_sha": COMMIT,
        "verdict": "MEASURED_MECHANISM_HUB_CONCEPT_BRIDGE_RECOVERY_scope_narrowed_from_prereg",
        "run_mode": "smoke",
        "provenance_quality": "MEASURED_MECHANISM_verified_off_disk_3_seeds_150_queries_local_cpu_4p4s_wall",
        "relevance_tier": "HIGH",
        "era": "STAGE_1_APPLY_2026-07-03_retrieval_architecture_decision_point",
        "cert_status": "measured_mechanism_proven_bound_hub_concept_bridge_recovery",
        "cert_class": "ppr_walk_recovers_hub_concept_2hop_bridges_at_r5_0p99_on_5371_entity_wikidata_kg_bipartite_forest_topology_scope_narrowed_from_general_2hop_bridges_mid_smoke",
        "verified_off_data": True,
        "verification_method": "independent .venv python recompute off metrics.json + KG topology verification via wikidata_action_api_v2_relabeled_adapted_relations.jsonl scan + label source verification via wikidata_action_api_v2_relabeled.shard_0000.jsonl aliases[0] scan",
        "atomized_by": "skunkworks_landed_VET_2026-07-03_exp2c_ppr_wikidata_MM_scope_narrow",
        "cert_ts": TS_ISO,
        "n_seeds": 3,
        "n_queries_per_seed": 50,
        "seeds": [11, 17, 23],
        "per_arm_mean_recall_at_k": {
            "ARM_HOP1_TRIGRAM_ALONE_BASELINE": 0.3467,
            "ARM_MAIN_PPR_RECOVERED": 0.9933,
            "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": 1.0000,
            "ARM_NEG_CTL_PPR_FROM_RANDOM": 0.1333
        },
        "margin_main_minus_neg": 0.860,
        "discriminator_gate_threshold": 0.50,
        "discriminator_margin_over_gate_ratio": 1.72,
        "combined_recovery_on_missed_by_hop1": {"recovered": 97, "missed": 98, "rate": 0.9898},
        "per_seed_recovery_rate": [1.0, 1.0, 0.9667],
        "ppr_mass_max_deviation_from_1_worst_seed": 4.64e-14,
        "kg_signal_local_ok_all_seeds": True,
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "arms_differ_exempted_all_ones_saturated": [
            "seed_11 MAIN==POS both all-ones",
            "seed_17 MAIN==POS both all-ones"
        ],
        "kg_topology_measured": {
            "n_entities": 5371,
            "n_undirected_edges": 5489,
            "n_typed_triples": 5510,
            "leaves_deg_1": 5230,
            "deg_2": 126,
            "deg_3_to_4": 1,
            "hubs_deg_5_to_20": 0,
            "hubs_deg_gt_20": 14,
            "top_3_megahubs_unlabeled_in_shard_aliases0": ["Q65943 deg 1515", "Q24034552 deg 1501", "Q8366 deg 796"],
            "actual_bridge_pool_labeled_hubs": ["Q11348 function deg 295", "Q11563 number deg 44", "Q246672 mathematical object deg 41"],
            "topology_class": "bipartite_forest_hub_and_spoke"
        },
        "mid_smoke_adjustments_audited": {
            "adj_1_synthesizer_redesign": {
                "before": "bridge_deg cap 3-50",
                "after": "bridge_deg cap 5-100000",
                "verdict": "LEGITIMATE_AND_SCOPE_NARROWS",
                "rationale": "KG topology honestly discovered; only 3 candidate bridges at deg 3-50; widening admits hub-concept bridges; scope shifts from '2-hop bridges' to 'hub-concept 2-hop bridges'"
            },
            "adj_2_neg_ctl_threshold_plus_margin_gate": {
                "before": "NEG_CTL <= 0.10",
                "after": "NEG_CTL <= 0.20 AND MAIN-NEG >= 0.50",
                "verdict": "LEGITIMATE_STRUCTURAL_margin_gate_defensible",
                "rationale": "bipartite-forest topology creates real residual mass diffusion; margin observed 0.860 = 1.72x gate; META_RULE_M adaptive-with-discriminator-gate applies"
            },
            "adj_3_label_source_correction": {
                "before": "atoms.jsonl name field",
                "after": "shard aliases[0] via wikidata_action_api_v2_relabeled.shard_0000.jsonl",
                "verdict": "LEGITIMATE_data_quality_workaround_FLAGS_substrate_infrastructure_bug",
                "rationale": "atoms.jsonl name field is 'wikidata Qxxx' placeholder for all 5360 Wikidata entities; shard aliases[0] gives real labels; PPR uses graph structure only so label source affects arms uniformly through query_text encoding; no PPR-favoring exploit"
            }
        },
        "substrate_infrastructure_bug_flagged": {
            "bug": "atoms.jsonl name field is trivial 'wikidata Qxxx' placeholder for all 5360 Wikidata entities; real labels only available via shard aliases[0]",
            "impact": "downstream substrate-KB queries cannot retrieve Wikidata concepts by real semantic label without shard-side workaround",
            "recommended_owner": "hdi_testbed",
            "recommended_fix": "backfill atoms.jsonl name field from shard aliases[0] for all wikidata_Qxxx entities in the math corpus; verify integrity check + verify-load"
        },
        "decision_point_closure": {
            "decision_point": "retrieval_architecture: PPR-walk viable at real-semantic-KG scale vs encoder-swap required",
            "status": "CLOSED_WITH_SCOPE_ANNOTATION",
            "resolution": "PPR-walk viable for hub-concept-bridge class in Wikidata substrate; encoder-swap DEFERRED",
            "extrapolation_gate": "full extrapolation to non-hub bridges requires KG with non-hub bridges; current Wikidata partition structurally lacks them (data-availability bound not mechanism bound)"
        },
        "cross_arc_overlap_check": {
            "query": "PPR walk 2-hop bridge Wikidata KG typed relations dense semantic",
            "top_hits_cosine": [
                ["semantic_relation wordnet", 0.3145],
                ["semantic_relation.n.01 wordnet", 0.2803],
                ["relation wordnet", 0.2686]
            ],
            "verdict": "no_prior_operationalization_of_PPR_on_Wikidata_adapted_KG_genuinely_novel"
        },
        "supersedes": None,
        "amends": None,
        "composes_with": [
            "math::T3/exp_2_ppr_walk_bridge_recovery_smoke_20_entity_synthetic_POS_CTL_1p000 (parent: PPR primitive numeric proof)",
            "math::T3/exp_2b_ppr_walk_wikipedia_semantic_kb_smoke_HALT_KG_DATA_AVAILABILITY_FLOOR_BREACH (parent: infrastructure/scope diagnosis + revival criterion mean_edges_per_node>=1.5)"
        ],
        "cites": [
            "Haveliwala_2003_personalized_pagerank_alpha_0p15",
            "HippoRAG_arXiv_2405p14831_PPR_on_Wikipedia_semantic_KG_precedent",
            "Fix_28_verify_per_arm_off_disk_not_verdict_msg",
            "META_RULE_M_adaptive_with_discriminator_gate",
            "USER_locked_scope_narrowing_documented_not_hidden"
        ],
        "revival_criterion": (
            "To promote MM -> CG: run Exp 2C on a KG partition that contains non-hub bridges "
            "(e.g., Wikidata subset filtered to only entities with 3 <= deg <= 20) AND has "
            ">= 30 candidate non-hub bridge triples. If PPR still recovers r@5 >= 0.90 on that "
            "restricted pool, the mechanism generalizes beyond hub-concept bridges and the "
            "scope-annotation can drop. Alternatively, dispatch on a denser semantic KG (e.g., "
            "ConceptNet, DBpedia truthy) where the bipartite-forest degeneracy does not hold."
        ),
        "cert_increment_delta": 1
    }
}

# ============= ATOM (b): meta MM_TENTATIVE_METHODOLOGY three-adjustments-with-margin-gate =============
atom_meta = {
    "id": ("meta::T2/META_MID_SMOKE_ADJUSTMENTS_LEGITIMATE_WHEN_STRUCTURAL_RATIONALE_MEASURABLE_"
           "AND_DISCRIMINATOR_MARGIN_GATE_HELD_AT_1p5X_ORIGINAL_THRESHOLD_MM_TENTATIVE_METHODOLOGY_"
           "witness_exp2c_ppr_wikidata_2026-07-03_three_adjustments_synthesizer_scope_narrow_"
           "neg_ctl_threshold_plus_margin_gate_label_source_correction_all_three_survived_audit_"
           "because_a_KG_topology_off_disk_verified_bipartite_forest_hub_and_spoke_b_margin_"
           "0p860_vs_gate_0p50_ratio_1p72x_c_label_source_bug_verified_off_disk_and_affects_all_"
           "arms_uniformly_meta_rule_form_when_mid_smoke_adjustment_requires_structural_rationale_"
           "measured_off_disk_plus_discriminator_margin_gate_at_least_1p5x_original_threshold_"
           "then_LEGITIMATE_annotate_scope_narrowing_in_atom_do_not_downgrade_to_HF_expansion_"
           "gate_two_more_independent_witnesses_where_the_pattern_holds_would_promote_MM_to_CG"),
    "name": ("META MID_SMOKE_ADJUSTMENTS_LEGITIMATE_WHEN_STRUCTURAL_RATIONALE_MEASURABLE_AND_"
             "DISCRIMINATOR_MARGIN_GATE_HELD_AT_1p5X (MM_TENTATIVE_METHODOLOGY, 1 witness Exp 2C)"),
    "corpus": "meta",
    "tier": "T2",
    "kind": "methodology_rule",
    "description": (
        "META methodology rule (MM_TENTATIVE, 1 witness Exp 2C 2026-07-03): mid-smoke calibration "
        "adjustments are LEGITIMATE (do not warrant HF closure or full downgrade below MM) when "
        "ALL THREE of the following hold: (a) the structural rationale for the adjustment is "
        "measurable off-disk (e.g., KG topology, corpus statistics, encoder codebook properties) "
        "and the measurement is documented in metrics.json or the pre-reg; (b) any discriminator "
        "threshold that was loosened is REPLACED by a margin gate at >= 1.5x the loosened "
        "absolute threshold, and the observed margin is >= 1.5x the margin gate itself "
        "(compound safety factor); (c) any data-source workaround is verified off-disk to "
        "affect all arms uniformly (no arm-favoring exploit). Exp 2C witness: (adj 1) "
        "synthesizer bridge_deg cap 3-50 -> 5-100000 justified by measured bipartite-forest KG "
        "topology (5230 leaves, 126 deg-2, 15 hubs deg>5); scope narrows from '2-hop bridges' "
        "to 'hub-concept 2-hop bridges' and is annotated in atom. (adj 2) NEG_CTL 0.10 -> 0.20 "
        "with margin gate MAIN-NEG >= 0.50; observed margin 0.860 = 1.72x gate = ~4.3x original "
        "NEG_CTL absolute threshold; compound safety factor holds. (adj 3) label source "
        "atoms.jsonl name -> shard aliases[0] verified off-disk to affect all arms uniformly "
        "(PPR uses graph structure only). Corollary: when any of (a)/(b)/(c) FAILS, the "
        "adjustment is Goodhart-loosening and warrants downgrade to MB or HF depending on "
        "severity. Rule applies to smoke landings ONLY; FULL landings with mid-smoke adjustments "
        "should re-dispatch pre-registered variant for formal audit trail (higher bar because "
        "FULL consumes real compute budget). SCOPE: methodology-rule level, catches the "
        "'three-adjustments-with-margin-gate' pattern before it becomes p-hacking cover. "
        "EXPANSION CRITERION: two more independent witnesses where the (a)+(b)+(c) rubric "
        "correctly separates legitimate scope-narrowing from p-hacking would promote MM -> CG_META. "
        "Composes with USER-locked never-hallucinate + scope-narrowing-must-be-documented."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "methodology_rule",
        "term_class": "MID_SMOKE_ADJUSTMENT_AUDIT_DISCIPLINE",
        "cert_status": "mm_tentative_methodology_1_witness",
        "cert_class": "MM_TENTATIVE_META_mid_smoke_adjustment_legitimate_when_three_conditions_hold",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_exp2c_MID_SMOKE_ADJUSTMENT_META",
        "witness_cells": [
            {
                "cell": "exp_substrate_stage1_apply_exp2c_ppr_walk_synthesized_wikidata_bridges_smoke_2026_07_03",
                "cell_sha": COMMIT,
                "verified_conditions": {
                    "a_structural_rationale_measured_off_disk": True,
                    "b_margin_gate_at_1p5x_or_higher": {"gate_ratio": 1.72, "observed_margin_ratio_to_original": 4.3},
                    "c_data_source_workaround_affects_arms_uniformly": True
                },
                "outcome_tier": "MEASURED_MECHANISM (not full CG; not HF)"
            }
        ],
        "rule_form": (
            "IF mid_smoke_adjustment AND "
            "measurable_structural_rationale_off_disk AND "
            "discriminator_margin_gate >= 1.5x_loosened_threshold AND "
            "observed_margin >= 1.5x_margin_gate AND "
            "data_source_workaround_uniform_across_arms "
            "THEN LEGITIMATE (annotate scope narrowing; do not HF-close) "
            "ELSE Goodhart-loosening (downgrade to MB or HF depending on severity)"
        ),
        "composes_with_disciplines": [
            "USER_locked_scope_narrowing_documented_not_hidden",
            "META_RULE_M_adaptive_with_discriminator_gate",
            "META_RULE_AF_arms_differ_exempted_all_ones_saturated_regime",
            "Fix_28_verify_per_arm_off_disk_not_verdict_msg"
        ],
        "cites": [
            "witness_atom_exp2c_ppr_wikidata_MM_hub_concept_bridge_recovery_2026-07-03"
        ],
        "expansion_criterion": "two more independent witnesses (different cell class, different adjustment class) where the (a)+(b)+(c) rubric correctly separates legitimate scope-narrowing from p-hacking would promote MM -> CG_META",
        "supersedes": None,
        "amends": None,
        "cert_increment_delta": 1
    }
}


def a5_append(path, atom):
    """Atomic append: tmp write + fsync + os.replace + verify-load."""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atomize_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    n_lines = 0
    found = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            if atom["id"] in line:
                found = True
    if not found:
        raise RuntimeError(f"verify-load failed: atom id not found in {path}")
    return n_lines


def ledger_append(atom, session_tag, ledger_path=CERT_LEDGER):
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "cert_status": atom["metadata"].get("cert_status"),
        "cert_class": atom["metadata"].get("cert_class"),
        "cert_increment_delta": atom["metadata"].get("cert_increment_delta", 0),
        "verified_off_data": atom["metadata"].get("verified_off_data", False),
        "cell_sha": atom["metadata"].get("cell_sha"),
        "atomized_by": atom["metadata"].get("atomized_by"),
        "landed_VET_session": session_tag,
    }
    d = os.path.dirname(ledger_path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_ledger_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ledger_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    print(f"[atomize] ts_iso={TS_ISO} commit={COMMIT}")
    session_tag = "2026-07-03_exp2c_ppr_wikidata_MM_and_mid_smoke_adjustment_META"

    n_math = a5_append(MATH_ATOMS, atom_mm)
    print(f"[atomize] MATH atom (a) MM appended; total math lines={n_math}")
    ledger_append(atom_mm, session_tag)

    n_meta = a5_append(META_ATOMS, atom_meta)
    print(f"[atomize] META atom (b) MM_TENTATIVE_METHODOLOGY appended; total meta lines={n_meta}")
    ledger_append(atom_meta, session_tag)

    print("[atomize] done. Both atoms A5-gated + verify-loaded + ledger'd.")
