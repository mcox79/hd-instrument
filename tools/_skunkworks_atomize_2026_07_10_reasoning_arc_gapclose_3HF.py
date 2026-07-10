"""
A5-gated atom-write: reasoning-arc ledger gap-close (2026-07-10).

Three landed FULLs READ + used in tonight's resolved 5-hypothesis conclusion but not yet
formally VET'd/atomized. Independent off-disk recompute (.venv) reproduces every headline
from per-arm data (NOT verdict_msg; Fix #28). All three are HONEST NEGATIVES that CLOSE
roadmap directions and COMPOSE with the graph_inductive_ceiling_v1 (#4) knowledge-limit MM.

  CELL 1  relation_type_richness_ladder_v1          -> HARD_FAIL honest-negative (confound-free)
          Relation-type richness ALONE does not raise inductive inference. best_inductive
          k=[2,5,10,16]=[0.673,0.667,0.666,0.675], slope 0.002 (flat). type_entropy genuinely
          rose 0.62->1.40 (n_types 2->15) yet AUC flat. Degree HELD (mean_deg range_rel 0.090
          <=0.10) AND -- unlike the density cell -- the ORACLE_PA ceiling is FLAT (range_rel
          0.004), so NO branchiness/dynamic-range confound. Self-test discriminator WOULD rise
          (pos_slope 0.096, degree_probe moves 0.35->0.82). Clean, telemetry-sensitive negative.

  CELL 2  exp_encoder_structure_aware_sharpness_v1  -> HARD_FAIL honest-negative (all 3 seeds)
          Structure-aware encoder training does NOT lift held-out M5. Canonical n=4440:
          deltaM5(best-struct C_hybrid - baseline A) = [-0.012,-0.017,-0.024], mean -0.0175,
          all <= HF bar +0.03 (HP +0.10). node2vec (B) is transductive by construction
          (seen_auc 0.94, heldout 0.57); the FAIR inductive arm (hybrid C) is also flat/neg,
          and the walk component HURTS 1-hop AUC (0.76 vs baseline 0.88). Worse at n=9000
          (-0.032..-0.038) -> not a small-N artifact. Baseline reaches heldout M5 0.68 (~#4
          ceiling / phase-0 0.6945) so the test CAN see held-out signal; structure just doesn't add.

  CELL 3  grounding_learned_sr_heldout_reasoning_v1 -> HARD_FAIL structural (memorized search)
          codes_necessary=False at FULL: LEARNED_HELDOUT reach@2 0.115 barely beats random-code
          CODEALIAS 0.104 (delta 0.011 < NEC_MARGIN 0.05); learned/knownT ratio 0.248. It DOES
          fill holes over memoryless (vs 0.017, +0.072 = real retrieval) = memorized traversal,
          NOT inductive inference. GENUINE structural bound (not test-design): positive control
          repro_ok=True and the PLANTED self-test has codes_necessary=True (learned 1.0 vs ctrls
          ~0.22) so the machinery CAN distinguish learned from random when structure is learnable
          -- on real held-out it cannot. This is the central held-out-inductive negative the arc
          rests on; distinct from additive_geometric (TransE codes_necessary=True, reach@1
          completion) which is the promising lever, not a duplicate.

Writes: 3 math atoms (HARD_FAIL) + 3 cert_ledger rows. No new META (Cell 1 is an APPLICATION
of the already-banked branchiness META rule, here SATISFIED = confound-free; Cell 3 is an
APPLICATION of the positive-control-clears-floor discipline). CERT N delta: +0 CG, +3 proven
negatives.

A5 protocol: read -> build -> tmp write + fsync -> os.replace -> re-read + verify count delta +
tail round-trip ID match. Abort on any mismatch (originals untouched pre-replace).
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = "skunkworks_landed_vet_reasoning_arc_gapclose_3HF_2026-07-10"
ATOMIZED_DATE = "2026-07-10"

# ===========================================================================
# CELL 1 - relation-type richness ladder : HARD_FAIL honest-negative (confound-free)
# ===========================================================================
C1_ANCHOR = "relation_type_richness_ladder_v1"
C1_METRICS = "data/exp_relation_type_richness_ladder_v1/metrics.json"
C1_COMMIT = "d74c4bca26be373f9efdd8bf438fd0c9866492b2"

atom_c1 = {
    "id": ("math::HARD_FAIL_relation_type_richness_ALONE_does_NOT_raise_held_out_inductive_inference_CONFOUND_FREE_"
           "best_inductive_per_rung_k_2_5_10_16_eq_0p673_0p667_0p666_0p675_slope_0p002_flat_lt_0p05_richness_rises_"
           "False_3seed_cv_0p004_to_0p018_type_entropy_GENUINELY_ROSE_0p62_to_1p40_n_types_used_2_to_15_yet_AUC_FLAT_"
           "and_UNLIKE_the_kcore_density_cell_the_ORACLE_PA_ceiling_is_FLAT_range_rel_0p004_so_NO_branchiness_dynamic"
           "_range_confound_degree_HELD_mean_deg_3p79_to_3p47_range_rel_0p090_le_0p10_selftest_discriminator_WOULD_"
           "rise_pos_slope_0p096_null_flat_pos_oracle_flat_degree_probe_MOVES_0p35_to_0p82_so_telemetry_sensitive_not"
           "_analytically_pinned_absolute_inductive_signal_sits_at_the_arc_0p67_to_0p76_ceiling_band_consistent_with_"
           "graph_inductive_ceiling_v1_number4_richness_is_another_SAME_GRAPH_KNOB_that_does_NOT_move_inductive_"
           "alongside_kcore_density_HF_the_lever_remains_INGEST_KNOWLEDGE_not_relation_type_diversity_n4440_E14767_"
           "3seed_7_13_17_FULL_2026-07-10"),
    "name": ("MATH HARD_FAIL (honest-negative, CONFOUND-FREE): relation-type RICHNESS ALONE does NOT raise held-out "
             "inductive inference. best_inductive per rung k=[2,5,10,16] = [0.673,0.667,0.666,0.675], slope 0.002 "
             "(flat, < 0.05 rise bar; richness_rises=False), 3-seed cv 0.004-0.018. The richness axis GENUINELY moved: "
             "type_entropy 0.62 -> 1.40, n_types_used 2 -> 15 -- yet inductive AUC stayed flat. CONFOUND-FREE (the key "
             "distinction from the k-core density HF): degree HELD (mean_deg 3.79 -> 3.47, range_rel 0.090 <= 0.10) "
             "AND the ORACLE_PA routing ceiling is FLAT (range_rel 0.004), so there is NO branchiness / dynamic-range "
             "confound -- the flat learned-AUC is a genuine richness-null (satisfies the branchiness META rule: check "
             "the oracle ceiling first; here it does not move). Discriminator is telemetry-sensitive, not analytically "
             "pinned: the mechanism self-test on planted richness-dependent data DOES rise (pos_slope 0.096) with "
             "degree held (pos_oracle_flat=True), null_flat=True, and the degree probe MOVES 0.35 -> 0.82 -- so the "
             "discriminator WOULD have risen had richness mattered. The absolute inductive signal (~0.67) sits in the "
             "arc's 0.67-0.76 ceiling band (consistent with graph_inductive_ceiling_v1 #4). CONCLUSION: relation-type "
             "diversity is another SAME-GRAPH knob that does not move inductive inference, alongside k-core density; "
             "the lever remains INGEST/knowledge, not relation-type richness. n=4440, E=14767, 3 seeds [7,13,17]."),
    "corpus": "math",
    "tier": "HARD_FAIL",
    "kind": "experiment_landed_vet",
    "cert_status": "hard_fail_honest_negative_relation_type_richness_alone_not_the_inductive_lever_confound_free",
    "cert_class": ("held_out_best_inductive_AUC_across_relation_type_richness_ladder_degree_and_oracle_ceiling_both_"
                   "held_flat_confound_free_richness_null"),
    "description": (
        "Independent off-disk recompute (3 seeds [7,13,17], n=4440, E=14767) from per_seed.rungs[*].best_inductive "
        "(NOT verdict_msg; Fix #28) reproduces every headline. Cell verdict label MIDDLE_BAND_RICHNESS_LADDER; "
        "SKUNKWORKS ADJUDICATION: for the HYPOTHESIS under test ('relation-type richness is the inductive lever') this "
        "is a CLEAN HONEST-NEGATIVE (richness_rises=False). The MIDDLE_BAND label reflects only that the ABSOLUTE "
        "inductive AUC ~0.67 sits mid-band (there IS inductive signal, in the arc's 0.67-0.76 ceiling); it does not "
        "make the richness result partial.\n\n"
        "HEADLINE (recomputed):\n"
        "  best_inductive per rung k=[2,5,10,16] mean = [0.6729, 0.6674, 0.6662, 0.6751]; range_rel 0.013; "
        "gate richness_slope 0.00227 (< 0.05 flat bar); richness_monotonic reported True but magnitude negligible.\n"
        "  Per-rung cross-seed cv: [0.012, 0.010, 0.018, 0.004] (tight).\n"
        "  Richness axis DID move: type_entropy 0.624 -> 1.177 -> 1.365 -> 1.396; n_types_used 2 -> 5 -> 10 -> 15.\n\n"
        "CONFOUND-FREE (the load-bearing distinction from grounding_density_payoff HF):\n"
        "  DEGREE control HELD: mean_deg 3.792 -> 3.501 -> 3.474 -> 3.470, range_rel 0.090 <= 0.10 (degree_flat=True; "
        "not tight <0.05, but within band; degree slightly FALLS with richness, so richness had a slight degree "
        "headwind, not tailwind).\n"
        "  ORACLE_PA routing ceiling FLAT: [0.6357,0.6381,0.6362,0.6383], range_rel 0.004 (oracle_flat=True). This is "
        "the key check the density cell FAILED (there the KNOWN_T oracle collapsed 10.7x = branchiness confound). "
        "Here the oracle ceiling does NOT move across the ladder, so the flat learned-AUC is a genuine richness-null, "
        "NOT a routing-difficulty / dynamic-range artifact. This cell SATISFIES the branchiness META rule.\n\n"
        "DISCRIMINATOR IS TELEMETRY-SENSITIVE (not saturation-vacuous, not analytically pinned):\n"
        "  mechanism_selftest on PLANTED richness-dependent data: pos_rises=True (pos_slope 0.096 >> 0.05 bar), "
        "pos_oracle_flat=True (0.092 rel, degree held in planted), null_slope 0.003 null_flat=True, degree_probe "
        "MOVES 0.346 -> 0.823 (range 0.477). So the discriminator WOULD have risen had relation-type richness "
        "carried inductive signal, and it responds to degree -- it simply did not fire on the real ladder because "
        "richness alone carries no inductive lift.\n\n"
        "SCOPE (honest): REFUTES 'add more relation TYPES on the same node set = the inductive-inference lever' "
        "(robust 3-seed, confound-free negative). DOES NOT test more distinct ENTITIES, cleaner/less-noisy edges, "
        "longer-range structure, or an ACTIVE exogenous referent. The inductive ceiling itself (~0.67-0.76 AUC) is "
        "unchanged. Composes with graph_inductive_ceiling_v1 (#4, knowledge-thin ingest = primary lever) and the "
        "density-payoff HF: richness and density are two SAME-GRAPH knobs that both fail to move inductive inference; "
        "the settled reading is that the lever is INGEST/knowledge and the hard wall is inductive inference itself.\n\n"
        "TIER: HARD_FAIL (honest-negative; proven roadmap-scoping negative). cert_increment_delta=0 (a clean negative "
        "closes the relation-type-diversity direction; does not increment chain-grade N). REVIVAL: vary a richness "
        "axis orthogonal to the same-node-set graph (more entities, cleaner edges, an actively-sampled exogenous "
        "referent) rather than relation-type count; or attack the inductive-inference mechanism directly."
    ),
    "aliases": [
        "relation-type richness alone does not raise held-out inductive inference confound-free",
        "richness ladder flat slope degree and oracle ceiling both held same-graph knob",
        "relation-type diversity is not the inductive lever ingest knowledge is",
    ],
    "metadata": {
        "provenance_quality": "HARD_FAIL_HONEST_NEGATIVE_CONFOUND_FREE",
        "cert_status": "hard_fail_honest_negative",
        "cert_class": "relation_type_richness_alone_not_inductive_lever_confound_free",
        "verdict_cell": "MIDDLE_BAND_RICHNESS_LADDER",
        "verdict_scored_correctly": True,
        "skunkworks_adjudication": "honest_negative_for_the_richness_lever_hypothesis_MIDDLE_BAND_label_is_absolute_AUC_mid_band_only",
        "anchor": C1_ANCHOR,
        "cell_commit": C1_COMMIT,
        "metrics_path": C1_METRICS,
        "verified_off_data": (
            "Recomputed off per_seed.rungs[*].best_inductive/type_entropy/mean_degree/oracle_pa via .venv Python "
            "(independent of verdict_msg; Fix #28). best_inductive k=[2,5,10,16]=[0.6729,0.6674,0.6662,0.6751] range_rel "
            "0.013 slope 0.00227; per-rung cv [0.012,0.010,0.018,0.004]; type_entropy 0.624->1.396 n_types 2->15; "
            "mean_deg 3.792->3.470 range_rel 0.090; oracle_pa range_rel 0.004; selftest pos_slope 0.096 null_flat True "
            "pos_oracle_flat True degree_probe 0.346->0.823. Cross-arc overlap: substrate_query top hit cosine 0.329 "
            "(stale cross-domain-analogy note); grep anchor in Store = 0 prior atoms; NOVEL, not subsumed."
        ),
        "honest_scope": (
            "REFUTES 'more relation TYPES on the same node set = the inductive lever' (confound-free 3-seed negative; "
            "degree AND oracle ceiling both held flat). DOES NOT test entities/edge-quality/active-referent axes, and "
            "does not change the ~0.67-0.76 inductive ceiling. The lever remains ingest/knowledge; the wall is "
            "inductive inference itself."
        ),
        "n_seeds": 3, "seeds": [7, 13, 17], "n_nodes": 4440, "n_edges": 14767,
        "metrics": {
            "best_inductive_per_rung": [0.6729, 0.6674, 0.6662, 0.6751],
            "rung_ks": [2, 5, 10, 16], "richness_slope": 0.00227, "range_rel_best_inductive": 0.013,
            "per_rung_cv": [0.012, 0.010, 0.018, 0.004],
            "type_entropy_per_rung": [0.624, 1.177, 1.365, 1.396], "n_types_used_per_rung": [2, 5, 10, 15],
            "mean_deg_per_rung": [3.792, 3.501, 3.474, 3.470], "degree_range_rel": 0.090,
            "oracle_pa_per_rung": [0.6357, 0.6381, 0.6362, 0.6383], "oracle_range_rel": 0.004,
            "selftest_pos_slope": 0.096, "selftest_null_flat": True, "selftest_pos_oracle_flat": True,
            "selftest_degree_probe_range": 0.477, "richness_rises": False,
        },
        "confound_free": True,
        "oracle_ceiling_held_flat_no_branchiness_confound": True,
        "degree_control_held": True,
        "discriminator_telemetry_sensitive": True,
        "revival_criteria": [
            "vary_entities_or_edge_quality_or_active_exogenous_referent_not_relation_type_count",
            "attack_inductive_inference_mechanism_directly_generalization_to_withheld_nodes",
        ],
        "composes_with": [
            "math::MEASURED_MECHANISM_graph_inductive_predictability_ceiling_of_real_conceptnet_subgraph_is_AUC_0p76 (#4 knowledge-limit)",
            "math::HARD_FAIL_density_alone_via_kcore_densification (sibling same-graph-knob negative)",
            "meta::META_density_or_richness_ladder_that_shifts_the_reach_at_K_oracle_ceiling (branchiness rule -- here SATISFIED/passed)",
        ],
        "cites": [
            "Fix_28_verify_per_arm_metrics_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "feedback_discriminator_must_be_telemetry_sensitive_not_analytically_pinned",
            "substrate_kb_concept_overlap_check_on_schema_vet_USER_locked_2026-07-01",
        ],
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
    },
}

# ===========================================================================
# CELL 2 - structure-aware encoder sharpening : HARD_FAIL honest-negative (all 3 seeds)
# ===========================================================================
C2_ANCHOR = "exp_encoder_structure_aware_sharpness_v1"
C2_METRICS = "data/exp_encoder_structure_aware_sharpness_v1_seed_{7,13,19}/metrics.json"
C2_COMMIT = "3833b761fd17e8ecfd4735b5b874a04e75becd78"

atom_c2 = {
    "id": ("math::HARD_FAIL_structure_aware_encoder_training_does_NOT_lift_held_out_inductive_generalization_M5_"
           "canonical_n4440_deltaM5_best_struct_C_hybrid_minus_baseline_A_eq_neg0p012_neg0p017_neg0p024_3seed_mean_"
           "neg0p0175_ALL_le_HF_bar_plus0p03_HP_plus0p10_node2vec_arm_B_is_TRANSDUCTIVE_by_construction_seen_auc_"
           "0p94_heldout_0p57_cannot_generalize_the_FAIR_inductive_arm_hybrid_C_is_ALSO_flat_negative_and_the_walk_"
           "component_HURTS_1hop_AUC_0p76_vs_baseline_0p88_worse_at_n9000_neg0p032_to_neg0p038_so_NOT_a_smallN_"
           "artifact_baseline_A_reaches_heldout_M5_0p68_matching_graph_inductive_ceiling_v1_and_phase0_0p6945_so_the_"
           "TEST_CAN_see_held_out_signal_structure_just_does_NOT_ADD_cardinality_ok_arms_differ_verified_composes_"
           "with_knowledge_limit_the_encoder_TRAINING_STRUCTURE_is_NOT_the_lever_ingest_is_n4440_and_n7895_3seed_7_"
           "13_19_FULL_2026-07-10"),
    "name": ("MATH HARD_FAIL (honest-negative, all 3 seeds): a structure-aware encoder (node2vec / hybrid walk+"
             "semantic) does NOT lift held-out inductive generalization (M5). Canonical n=4440: deltaM5 (best-struct "
             "arm C_hybrid_walk_semantic - baseline A_semantic) = [-0.012, -0.017, -0.024], mean -0.0175, ALL <= HF "
             "bar +0.03 (HP bar +0.10). The pure-structural node2vec arm (B) is TRANSDUCTIVE by construction -- it "
             "memorizes seen structure (seen_auc 0.94) but collapses on held-out nodes (M5 0.57) because it has no "
             "walk-derived embedding for unseen nodes; the FAIR inductive comparison is the hybrid arm (C), which is "
             "ALSO flat/negative, and its walk component actively HURTS 1-hop discrimination (M3 1hop AUC 0.76 vs "
             "baseline 0.88, from walk-mixing over-smoothing: M1 cosine stays high-flat 0.32->0.19 instead of "
             "decaying). Worse at n=9000 (deltaM5 -0.032..-0.038), so NOT a small-N artifact. The baseline itself "
             "reaches held-out M5 0.68 (matching graph_inductive_ceiling_v1 and phase-0 M5 0.6945), so the TEST CAN "
             "detect held-out inductive signal -- structure-aware training simply does not ADD any. cardinality_ok="
             "True, arms_differ_verified=True (distinct code hashes all arms/seeds). COMPOSES with the knowledge-limit "
             "conclusion: the encoder TRAINING-STRUCTURE is not the lever; ingest/knowledge is. Seeds [7,13,19]."),
    "corpus": "math",
    "tier": "HARD_FAIL",
    "kind": "experiment_landed_vet",
    "cert_status": "hard_fail_honest_negative_structure_aware_encoder_does_not_lift_held_out_inductive_generalization",
    "cert_class": ("held_out_M5_AUC_structure_aware_vs_semantic_baseline_encoder_transductive_node2vec_and_inductive_"
                   "hybrid_both_flat_or_negative"),
    "description": (
        "Independent off-disk recompute (3 seeds [7,13,19], 3 arms x 2 sizes = 6 units/seed) from per_size[*].m5_A/"
        "m5_B/m5_C (NOT verdict_msg; Fix #28) reproduces every headline. All 3 seeds land HARD_FAIL; genuine "
        "substantive negative, NOT a test-design failure.\n\n"
        "HEADLINE canonical n=4440 (recomputed):\n"
        "  seed7:  A=0.6842 B(n2v)=0.5841 C(hybrid)=0.6724  deltaM5(C-A)=-0.0118  deltaReach=+0.0010\n"
        "  seed13: A=0.6919 B(n2v)=0.5685 C(hybrid)=0.6749  deltaM5(C-A)=-0.0170  deltaReach=-0.0030\n"
        "  seed19: A=0.6954 B(n2v)=0.5767 C(hybrid)=0.6716  deltaM5(C-A)=-0.0238  deltaReach=+0.0030\n"
        "  mean deltaM5 -0.0175; ALL three seeds <= HF bar +0.03 (HP bar +0.10). best_struct_arm = C_hybrid all seeds.\n"
        "  At n=9000: deltaM5 [-0.0323, -0.0324, -0.0378] (MORE negative) -> degrades with scale, not a small-N fluke.\n\n"
        "WHY node2vec (B) is not the fair arm (Director's note CONFIRMED): node2vec is a TRANSDUCTIVE structural "
        "embedding -- it has no representation for nodes unseen at train time, so on held-out edges it degrades to "
        "M5 ~0.57 (near chance) while its SEEN-node AUC is 0.94. It CANNOT generalize inductively by construction. "
        "The fair inductive arm is the hybrid C (walk features + semantic, inductive at inference), which is also "
        "flat/negative. So the negative is not an artifact of an unfair transductive arm.\n\n"
        "MECHANISM of the negative: the walk/structure component HURTS the clean semantic signal. Hybrid C's 1-hop "
        "AUC (M3) is 0.76 vs baseline 0.88; its per-hop cosine stays high and flat (0.32,0.22,0.19,... instead of "
        "decaying), i.e. walk-mixing OVER-SMOOTHS and blurs the 1-hop neighbor distinction that drives held-out edge "
        "prediction. Adding structure trades away 1-hop sharpness for nothing on held-out.\n\n"
        "VALIDITY (not saturation-vacuous / not test-design failure): cardinality_ok=True (6/6 units), "
        "arms_differ_verified=True (all 18 arm code-hashes distinct). The baseline A reaches held-out M5 0.68-0.695, "
        "reproducing the certified inductive ceiling (graph_inductive_ceiling_v1 ~0.76 SIGNAL / phase-0 M5 0.6945) -- "
        "so the M5 metric DOES capture held-out inductive signal when it exists; the structure arms simply fail to "
        "improve it. No seed failures.\n\n"
        "TIER: HARD_FAIL (honest-negative; proven roadmap-scoping negative). cert_increment_delta=0. COMPOSES with "
        "graph_inductive_ceiling_v1 (#4): #4 established the ~0.76 inductive ceiling is knowledge-thin (ingest = "
        "primary lever, GNN/encoder machinery = small bounded secondary); THIS cell independently confirms the "
        "ENCODER TRAINING-STRUCTURE (node2vec/hybrid walk objectives) is NOT the lever -- structure-aware training "
        "does not lift held-out generalization. REVIVAL: the lever is knowledge/ingest and inductive-inference "
        "mechanism (e.g. additive-geometric TransE codes, per grounding_additive_geometric_inductive_v1), not "
        "structure-aware encoder objectives on the existing graph."
    ),
    "aliases": [
        "structure-aware encoder training does not lift held-out inductive generalization",
        "node2vec transductive cannot generalize hybrid walk semantic also flat negative",
        "encoder training-structure is not the inductive lever ingest knowledge is",
    ],
    "metadata": {
        "provenance_quality": "HARD_FAIL_HONEST_NEGATIVE_ALL_3_SEEDS",
        "cert_status": "hard_fail_honest_negative",
        "cert_class": "structure_aware_encoder_does_not_lift_held_out_inductive_generalization",
        "verdict_cell": "HARD_FAIL",
        "verdict_scored_correctly": True,
        "anchor": C2_ANCHOR,
        "cell_commit": C2_COMMIT,
        "metrics_path": C2_METRICS,
        "verified_off_data": (
            "Recomputed off per_size[0].m5_A/m5_B/m5_C (canonical n=4440) for all 3 seed files via .venv Python "
            "(independent of verdict_msg; Fix #28). deltaM5(C-A) [-0.0118,-0.0170,-0.0238] mean -0.0175 all <= +0.03 "
            "HF bar; n=9000 deltaM5 [-0.0323,-0.0324,-0.0378]. node2vec B heldout M5 [0.584,0.569,0.577] vs seen_auc "
            "~0.94 (transductive). Hybrid C M3 1hop AUC ~0.76 vs baseline ~0.88. cardinality_ok=True arms_differ="
            "True all seeds. Baseline A M5 0.684-0.695 reproduces the inductive ceiling. Cross-arc overlap: "
            "substrate_query top hit cosine 0.288 (stale prereg); grep anchor in Store = 0 prior atoms; NOVEL."
        ),
        "honest_scope": (
            "REFUTES 'structure-aware encoder training (node2vec / hybrid walk objectives) lifts held-out inductive "
            "generalization on the existing graph'. Does NOT refute knowledge/ingest as the lever, nor the promising "
            "additive-geometric code direction. The transductive node2vec arm cannot generalize by construction; the "
            "fair inductive hybrid arm is also flat/negative and the walk component hurts 1-hop sharpness."
        ),
        "n_seeds": 3, "seeds": [7, 13, 19], "n_nodes": 4440, "n_edges": 14767, "sizes": [5000, 9000],
        "metrics": {
            "deltaM5_C_minus_A_n4440": [-0.0118, -0.0170, -0.0238], "deltaM5_mean_n4440": -0.0175,
            "deltaM5_C_minus_A_n9000": [-0.0323, -0.0324, -0.0378],
            "m5_A_n4440": [0.6842, 0.6919, 0.6954], "m5_B_node2vec_n4440": [0.5841, 0.5685, 0.5767],
            "m5_C_hybrid_n4440": [0.6724, 0.6749, 0.6716],
            "node2vec_seen_auc": 0.94, "hybrid_1hop_auc": 0.76, "baseline_1hop_auc": 0.88,
            "HF_bar": 0.03, "HP_bar": 0.10, "cardinality_ok": True, "arms_differ_verified": True,
        },
        "node2vec_is_transductive_cannot_generalize": True,
        "fair_inductive_hybrid_arm_also_flat_negative": True,
        "walk_component_hurts_1hop_sharpness": True,
        "worse_at_larger_scale_not_smallN_artifact": True,
        "baseline_reproduces_inductive_ceiling_test_is_valid": True,
        "revival_criteria": [
            "knowledge_ingest_lever_not_structure_aware_encoder_objectives",
            "additive_geometric_transe_codes_inductive_inference_mechanism",
        ],
        "composes_with": [
            "math::MEASURED_MECHANISM_graph_inductive_predictability_ceiling_of_real_conceptnet_subgraph_is_AUC_0p76 (#4: encoder machinery = small bounded secondary; this confirms encoder training-structure not the lever)",
            "math::MEASURED_MECHANISM_additive_geometric_TransE_relation_code_roughly_DOUBLES (the promising code-side lever, contrast)",
        ],
        "cites": [
            "Fix_28_verify_per_arm_metrics_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "feedback_held_out_test_methodology_required_for_macro_F1_claims_USER_LOCKED",
        ],
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
    },
}

# ===========================================================================
# CELL 3 - learned-SR held-out reasoning : HARD_FAIL structural (memorized search)
# ===========================================================================
C3_ANCHOR = "grounding_learned_sr_heldout_reasoning_v1"
C3_METRICS = "data/exp_grounding_learned_sr_heldout_reasoning_v1/metrics.json"
C3_COMMIT = "5ab793d1cd2163c7d20d95afdd95a3471d9c247b"

atom_c3 = {
    "id": ("math::HARD_FAIL_CG_the_substrate_learned_SR_codes_route_NO_BETTER_than_random_codes_on_held_out_"
           "MEMORIZED_SEARCH_not_reasoning_codes_necessary_False_at_FULL_dim2048_LEARNED_HELDOUT_reach_at_2_0p115_"
           "barely_beats_random_code_CODEALIAS_0p104_delta_0p011_lt_NEC_MARGIN_0p05_perseed_delta_0p019_0p008_0p005_"
           "SHRINKING_learned2_perseed_0p114_0p110_0p120_cv_0p037_ratio_learned_over_knownT_heldout_0p248_it_DOES_"
           "fill_holes_over_memoryless_0p017_delta_plus0p072_eq_REAL_memorized_traversal_over_KNOWN_but_NOT_inductive"
           "_inference_GENUINE_structural_bound_NOT_test_design_positive_control_repro_ok_True_mem1_0p463_sup1_0p744_"
           "sup2_0p494_knownT2_0p438_all_within_tol_0p10_and_the_PLANTED_selftest_has_codes_necessary_True_learned_"
           "1p0_vs_memctrl_0p229_codealias_0p221_arms_differ_True_so_machinery_CAN_distinguish_learned_from_random_"
           "when_structure_learnable_on_real_heldout_it_CANNOT_this_is_the_CENTRAL_held_out_inductive_negative_the_5"
           "_hypothesis_arc_rests_on_distinct_from_additive_geometric_TransE_codes_necessary_True_reach1_completion_"
           "which_is_the_PROMISING_lever_not_a_duplicate_n4440_E14767_3seed_7_13_17_FULL_CUDA_2026-07-10"),
    "name": ("MATH HARD_FAIL (structural bound): the substrate's LEARNED successor-representation codes route NO "
             "BETTER than random codes on held-out chains = MEMORIZED SEARCH, not reasoning. codes_necessary=False at "
             "FULL (dim=2048): LEARNED_HELDOUT reach@2 = 0.115 barely beats random-code CODEALIAS 0.104 (delta 0.011 "
             "< NEC_MARGIN 0.05; per-seed delta 0.019/0.008/0.005, SHRINKING). learned2 per-seed [0.114,0.110,0.120] "
             "cv 0.037; ratio learned / KNOWN_T-heldout ceiling 0.248. The learned codes DO fill holes over the "
             "memoryless floor (0.017, +0.072) = REAL memorized traversal over KNOWN structure, but that is NOT "
             "inductive inference over withheld nodes. GENUINE structural bound, NOT a test-design failure: the "
             "positive control reproduces all certified anchors (mem1 0.463, sup1 0.744, sup2 0.494, knownT2 0.438, "
             "all within tol 0.10) AND the PLANTED self-test has codes_necessary=True (learned reach 1.0 vs memctrl "
             "0.229 / codealias 0.221, arms_differ=True) -- so the machinery CAN distinguish learned from random codes "
             "when there is real learnable structure; on the real held-out graph it CANNOT. This is the central "
             "held-out-inductive negative the 5-hypothesis arc rests on. Distinct from additive_geometric_inductive "
             "(TransE codes_necessary=True on reach@1 completion, the PROMISING lever) -- different mechanism (learned "
             "multiplicative SR vs additive TransE) and metric regime; NOT a duplicate. n=4440, seeds [7,13,17]."),
    "corpus": "math",
    "tier": "HARD_FAIL",
    "kind": "experiment_landed_vet",
    "cert_status": "hard_fail_structural_bound_learned_codes_memorized_search_not_reasoning_codes_necessary_false_heldout",
    "cert_class": ("held_out_multi_hop_reach_at_2_learned_SR_codes_vs_random_code_alias_control_delta_below_necessity_"
                   "margin_memorized_traversal_not_inductive_inference"),
    "description": (
        "Independent off-disk recompute (3 seeds [7,13,17], n=4440, E=14767, dim=2048, CUDA) from per_seed.arms[*]."
        "reach (NOT verdict_msg; Fix #28) reproduces every headline. This is the CENTRAL held-out-inductive negative "
        "of the reasoning arc, and it is a GENUINE structural bound.\n\n"
        "HEADLINE (recomputed):\n"
        "  LEARNED_HELDOUT reach@1 = 0.362, reach@2 = 0.115.\n"
        "  Random-code control CODEALIAS reach@2 = 0.104; delta(learned - codealias) = 0.011 < NEC_MARGIN 0.05 => "
        "codes_necessary = FALSE. Per-seed delta [0.019, 0.008, 0.005] (shrinking to noise).\n"
        "  learned2 per-seed [0.114, 0.110, 0.120], cv 0.037 (tight); ratio learned2 / KNOWN_T-heldout ceiling 0.462 "
        "= 0.248.\n"
        "  cg_hard_fail=True (learned2 0.115 <= 0.20 OR codes-do-nothing OR learned<=memctrl fires); cg_hard_pass=False.\n\n"
        "WHAT THE LEARNED CODES DO (the honest nuance): they DO clear the hole-leaving MEMCTRL floor -- learned2 0.115 "
        "vs heldout_memctrl 0.042 (delta_vs_memctrl 0.072) and vs heldout memoryless 0.017 -- so there IS real memory "
        "retrieval / traversal over KNOWN structure. But routing over known structure is MEMORIZED SEARCH; the "
        "held-out test asks the codes to INFER reachability of WITHHELD nodes, and there they collapse to the "
        "random-code baseline (delta 0.011). Memorized traversal != inductive inference.\n\n"
        "GENUINE STRUCTURAL BOUND, NOT a test-design failure (positive control clears its own floor -- auditor "
        "discipline):\n"
        "  positive_control repro_ok=True: mem1 0.463 (anchor 0.453), sup1 0.744 (0.756), sup2 0.494 (0.500), knownT2 "
        "0.438 (0.434), ALL within tol 0.10 -- the certified learned-SR mechanism anchors reproduce.\n"
        "  mechanism_selftest on PLANTED synthetic: learned_recovers=True (reach 1.0), codes_necessary(planted)=True "
        "(learned 1.0 vs memctrl 0.229 vs codealias 0.221), arms_differ=True. So when the held-out structure is "
        "genuinely learnable, the SAME machinery DOES show codes_necessary=True. On the real ConceptNet held-out it "
        "does not -> the failure is in the DATA/inductive-inference regime, not the test. Anti-sat: hop1_present, "
        "baseline_in_band, baseline_collapses, supplied_fires, enough_heldout (1021 held-out chains) all True.\n\n"
        "CROSS-ARC (not a duplicate): grounding_additive_geometric_inductive_v1 found TransE additive codes "
        "codes_necessary=TRUE on completable held-out reach@1 (0.187 vs 0.089 discrete, the PROMISING lever). THIS "
        "cell tests the substrate's own LEARNED multiplicative SR codes on multi-hop reach@2 and finds "
        "codes_necessary=FALSE. Different code mechanism + different metric regime; complementary, not a rediscovery. "
        "It is also distinct from graph_inductive_ceiling_v1 (edge-existence AUC ceiling) and the density HF "
        "(density knob). grep of the Store confirms this anchor had 0 prior atoms -> NOVEL, banked here.\n\n"
        "TIER: HARD_FAIL (structural bound; proven negative). cert_increment_delta=0. This is the load-bearing "
        "negative that grounds the arc conclusion: the substrate's learned codes memorize/traverse KNOWN structure "
        "but do not INFER over withheld nodes; the wall is inductive inference itself, and the lever is knowledge/"
        "ingest + a genuinely inductive code geometry (additive-geometric), not the learned SR code as-is. REVIVAL: "
        "the additive-geometric TransE direction (already MM); better code-space generalization to withheld nodes; "
        "an actively-sampled exogenous referent (grounding needs active intervention)."
    ),
    "aliases": [
        "learned SR codes route no better than random on held-out memorized search not reasoning",
        "codes_necessary False at full held-out multi-hop reach@2 structural bound",
        "substrate learned codes memorize known structure do not infer over withheld nodes",
    ],
    "metadata": {
        "provenance_quality": "HARD_FAIL_STRUCTURAL_BOUND_POSITIVE_CONTROL_CLEARS_FLOOR",
        "cert_status": "hard_fail_structural_bound",
        "cert_class": "learned_codes_memorized_search_not_inductive_reasoning_codes_necessary_false_heldout",
        "verdict_cell": "HARD_FAIL_CG_MEMORIZED_SEARCH",
        "verdict_scored_correctly": True,
        "hf_attribution": "HF_STRUCTURAL_BOUND_not_HF_TEST_DESIGN_FAILURE",
        "anchor": C3_ANCHOR,
        "cell_commit": C3_COMMIT,
        "metrics_path": C3_METRICS,
        "verified_off_data": (
            "Recomputed off gates.cg + gates.reach + per_seed.arms[*].reach via .venv Python (independent of "
            "verdict_msg; Fix #28). LEARNED_HELDOUT reach1 0.362 reach2 0.115; CODEALIAS reach2 0.104; "
            "delta 0.011 < NEC_MARGIN 0.05 -> codes_necessary False; per-seed delta [0.019,0.008,0.005]; learned2 "
            "per-seed [0.114,0.110,0.120] cv 0.037; ratio/knownT 0.248; memctrl2 0.042 delta_vs_memctrl 0.072; "
            "positive_control repro_ok True (mem1 0.463/sup1 0.744/sup2 0.494/knownT2 0.438 within 0.10); planted "
            "selftest codes_necessary True (learned 1.0 vs memctrl 0.229 codealias 0.221) arms_differ True. Cross-arc "
            "overlap: substrate_query top hit cosine 0.325 (stale multi-hop note); grep anchor in Store = 0 prior "
            "atoms; distinct from additive_geometric (codes_necessary True, reach@1); NOVEL/not subsumed."
        ),
        "honest_scope": (
            "PROVES the substrate's LEARNED SR codes are memorized-search (traverse KNOWN structure: +0.072 over "
            "memctrl) but do NOT do inductive inference over WITHHELD nodes (tie random codes, delta 0.011). Does NOT "
            "refute the additive-geometric TransE lever (codes_necessary True on reach@1 completion), which remains "
            "the promising direction. The wall is inductive inference itself, consistent with the whole arc."
        ),
        "n_seeds": 3, "seeds": [7, 13, 17], "n_nodes": 4440, "n_edges": 14767, "code_dim": 2048,
        "metrics": {
            "learned_heldout_reach1": 0.362, "learned_heldout_reach2": 0.115,
            "codealias_reach2": 0.104, "delta_vs_codealias": 0.011, "nec_margin": 0.05, "codes_necessary": False,
            "delta_vs_codealias_per_seed": [0.019, 0.008, 0.005],
            "learned2_per_seed": [0.114, 0.110, 0.120], "learned2_cv": 0.037,
            "memctrl_reach2": 0.042, "delta_vs_memctrl": 0.072, "heldout_memoryless_reach2": 0.017,
            "knownT_heldout_reach2": 0.462, "ratio_vs_knownT_heldout": 0.248,
            "cg_hard_fail": True, "cg_hard_pass": False, "n_heldout_chains": 1021,
            "posctrl_repro_ok": True, "posctrl_mem1": 0.463, "posctrl_sup1": 0.744, "posctrl_sup2": 0.494,
            "posctrl_knownT2": 0.438, "posctrl_tol": 0.10,
            "selftest_learned_recovers": True, "selftest_codes_necessary_planted": True,
            "selftest_learned_reach": 1.0, "selftest_memctrl": 0.229, "selftest_codealias": 0.221,
        },
        "memorized_search_over_known_not_inductive_inference": True,
        "positive_control_clears_own_floor_genuine_not_test_design": True,
        "planted_selftest_codes_necessary_true_machinery_valid": True,
        "distinct_from_additive_geometric_not_a_duplicate": True,
        "central_heldout_inductive_negative_the_arc_rests_on": True,
        "revival_criteria": [
            "additive_geometric_transe_codes_inductive_inference_lever_already_MM",
            "better_codespace_generalization_to_withheld_nodes",
            "actively_sampled_exogenous_referent_grounding_needs_active_intervention",
        ],
        "composes_with": [
            "math::MEASURED_MECHANISM_additive_geometric_TransE_relation_code_roughly_DOUBLES (contrast: codes_necessary True reach@1)",
            "math::MEASURED_MECHANISM_graph_inductive_predictability_ceiling_of_real_conceptnet_subgraph_is_AUC_0p76 (#4)",
            "math::HARD_FAIL_density_alone_via_kcore_densification (KNOWN_T MM 0.434 traversal anchor reproduced here at 0.438)",
        ],
        "cites": [
            "Fix_28_verify_per_arm_metrics_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "auditor_discipline_positive_control_clears_own_expected_floor_before_reading_HF_2026-07-01",
            "project_grounding_needs_active_intervention_exogenous_referent_3source_synthesis_2026-07-09",
        ],
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
    },
}

# ===========================================================================
# CERT_LEDGER rows
# ===========================================================================
ts = time.time()
_iso = datetime.now(timezone.utc).isoformat()
for a in (atom_c1, atom_c2, atom_c3):
    a["ts_iso"] = _iso
    a["ts"] = ts


def ledger_row(atom, anchor, commit, cv, verdict, decision, scope, netdelta):
    return {
        "op": "cert_ruling",
        "ts_iso": _iso,
        "ts": ts,
        "atom_id": atom["id"],
        "corpus": "math",
        "tier": "HARD_FAIL",
        "cert_status": atom["cert_status"],
        "cert_class": atom["cert_class"],
        "anchor": anchor,
        "cell_commit": commit,
        "verified_off_data": True,
        "auditor": "hdi_skunkworks",
        "atomized_by": ATOMIZED_BY,
        "verdict": verdict,
        "cert_increment_delta": 0,
        "cv": cv,
        "decision": decision,
        "scope_correction_vs_director": scope,
        "net_cert_delta": netdelta,
        "referent_pointer": {"metrics_path": atom["metadata"]["metrics_path"], "atom_qualified_id": atom["id"]},
    }


ledger_c1 = ledger_row(
    atom_c1, C1_ANCHOR, C1_COMMIT, 0.012,
    "HARD_FAIL_honest_negative_relation_type_richness_alone_not_the_inductive_lever_confound_free",
    ("HARD_FAIL honest-negative: relation-type richness ALONE does not raise held-out inductive inference "
     "(best_inductive k=[2,5,10,16]=[0.673,0.667,0.666,0.675], slope 0.002, richness_rises=False, 3-seed). "
     "CONFOUND-FREE: type_entropy genuinely rose 0.62->1.40 (n_types 2->15) with degree HELD (range_rel 0.090) AND "
     "the ORACLE_PA ceiling FLAT (range_rel 0.004) -- so, unlike the density HF, no branchiness/dynamic-range "
     "confound; satisfies the branchiness META rule. Self-test discriminator WOULD rise (pos_slope 0.096, degree "
     "probe moves 0.35->0.82) = telemetry-sensitive."),
    ("Cell gate-label was MIDDLE_BAND_RICHNESS_LADDER; ADJUDICATION: for the richness-lever HYPOTHESIS this is a "
     "clean HONEST-NEGATIVE (richness_rises=False). The MIDDLE_BAND label only reflects the absolute inductive AUC "
     "~0.67 sitting mid-band (the ~0.67-0.76 arc ceiling). Does not overturn the arc conclusion -- confirms "
     "relation-type diversity is another same-graph knob that does not move inductive inference; lever remains "
     "ingest/knowledge."),
    "+0 CG (honest negative; closes the relation-type-diversity roadmap direction). +1 proven confound-free negative.")

ledger_c2 = ledger_row(
    atom_c2, C2_ANCHOR, C2_COMMIT, 0.30,
    "HARD_FAIL_honest_negative_structure_aware_encoder_does_not_lift_held_out_inductive_generalization_all_3_seeds",
    ("HARD_FAIL (all 3 seeds): structure-aware encoder training does NOT lift held-out M5. Canonical n=4440 "
     "deltaM5(best-struct C_hybrid - baseline A) = [-0.012,-0.017,-0.024] mean -0.0175, all <= HF bar +0.03. "
     "node2vec (B) transductive by construction (seen_auc 0.94, heldout 0.57 -- unfair arm, correctly excluded); "
     "fair inductive hybrid C also flat/negative and its walk component HURTS 1-hop AUC (0.76 vs 0.88). Worse at "
     "n=9000 (-0.032..-0.038). Baseline A M5 0.68 reproduces the inductive ceiling so the TEST is valid; structure "
     "just does not add."),
    ("Director used this as a knowledge-limit-confirming negative -- CONFIRMED correct. Scope: refutes 'structure-"
     "aware encoder objectives on the existing graph lift held-out inductive generalization'; does NOT refute the "
     "knowledge/ingest lever nor the additive-geometric code direction. cv is high (0.30) only because it is a cv "
     "of tiny near-zero deltas; the SIGN is robust (all 6 seed-size deltas negative)."),
    "+0 CG (honest negative; closes the structure-aware-encoder-training roadmap direction). +1 proven negative; composes with #4 knowledge-limit.")

ledger_c3 = ledger_row(
    atom_c3, C3_ANCHOR, C3_COMMIT, 0.037,
    "HARD_FAIL_structural_bound_learned_SR_codes_memorized_search_not_reasoning_codes_necessary_false_at_FULL",
    ("HARD_FAIL structural bound: the substrate's learned SR codes route NO BETTER than random codes on held-out "
     "(codes_necessary=False at FULL dim=2048): LEARNED_HELDOUT reach@2 0.115 vs random-code CODEALIAS 0.104, delta "
     "0.011 < NEC_MARGIN 0.05 (per-seed 0.019/0.008/0.005, shrinking; learned2 cv 0.037). Codes DO fill holes over "
     "memoryless (+0.072 vs memctrl) = memorized traversal over KNOWN structure, NOT inductive inference over "
     "withheld nodes. GENUINE (not test-design): positive control repro_ok=True (mem1/sup1/sup2/knownT2 all within "
     "tol 0.10) AND planted self-test has codes_necessary=True (learned 1.0 vs ctrls ~0.22) -- machinery CAN "
     "distinguish learned from random when structure is learnable; on real held-out it cannot."),
    ("This is the CENTRAL held-out-inductive finding the 5-hypothesis arc rests on; VET CONFIRMS the arc conclusion "
     "off-data. Cross-arc: DISTINCT from grounding_additive_geometric_inductive_v1 (TransE codes_necessary=TRUE on "
     "reach@1 completion, the promising lever) -- different code mechanism (learned multiplicative SR vs additive "
     "TransE) and metric regime (multi-hop reach@2 vs completion reach@1); NOT a duplicate. grep confirms anchor had "
     "0 prior atoms; banked here to close the ledger gap."),
    "+0 CG (proven structural negative; the substrate's learned codes = memorized-search not reasoning on held-out). +1 proven negative; grounds the arc conclusion; revival = additive-geometric / active referent.")

# ===========================================================================
# A5-gated atomic write
# ===========================================================================
def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    print("=== A5 atom-write: reasoning-arc ledger gap-close 3 HF (2026-07-10) ===")
    print("ts_iso =", _iso)
    print()
    print("Writing 3 atoms to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom_c1, atom_c2, atom_c3])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 3:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 3 rows to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger_c1, ledger_c2, ledger_c3])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 3:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    print()
    print("=== A5 WRITE COMPLETE ===")
    for p in (MATH_ATOMS, CERT_LEDGER):
        with open(p, "rb") as f:
            n = f.read().count(b"\n")
        print("  %s: %d lines" % (p.name, n))
    print()
    print("CERT N delta: +0 CG ; +3 HARD_FAIL proven negatives (all math). No new META.")


if __name__ == "__main__":
    main()
