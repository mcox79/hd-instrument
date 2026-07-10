"""
A5-gated atom-write: density-payoff relational-reasoning FULL landed-VET (2026-07-09).

Anchor: grounding_density_payoff_relational_reasoning_v1
Cell verdict: HARD_FAIL_DENSITY_ALONE_NOT_THE_ENABLER (correctly scored per pre-reg bands).
Skunkworks disposition: HONEST-NEGATIVE for the NARROW claim ('k-core densify the same
graph = the reasoning lever'), but BRANCHINESS-CONFOUNDED for any strong reading
('density does not help the substrate reason'). Independent off-disk recompute reproduces
every headline exactly; the KNOWN_T oracle ceiling reach@2 on the held-out chains ITSELF
collapses 0.462->0.043 (10.7x) on the dense k-core, so the absolute rel_gain metric was
doomed to shrink regardless of any learning benefit. Ceiling-normalized, the substrate's
relational signal is actually STRONGER on dense (learned/oracle 0.80 vs 0.25).

Writes: 1 math atom (HARD_FAIL honest-negative + branchiness scope) + 1 meta atom
(methodology: normalize by oracle dynamic-range / match branchiness when comparing across
density-varying regimes) + 2 cert_ledger rows.

A5 protocol: read -> build -> tmp write + fsync -> os.replace -> re-read + verify count
delta + tail round-trip ID match. Abort on any mismatch (originals untouched pre-replace).
"""

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
METRICS_PATH = "data/exp_grounding_density_payoff_relational_reasoning_v1/metrics.json"
ANCHOR = "grounding_density_payoff_relational_reasoning_v1"
CELL_COMMIT = "65d2e908c7b01f15b04874d4af0ec3e956036e21"
ATOMIZED_BY = "skunkworks_landed_vet_density_payoff_HF_branchiness_confound_2026-07-09"
ATOMIZED_DATE = "2026-07-09"

# ---------------------------------------------------------------------------
# Independently-recomputed off-disk numbers (all verified via .venv recompute).
# ---------------------------------------------------------------------------
M = dict(
    seeds=[7, 13, 17], n_nodes=4440, n_edges=14767, kcore_k=7,
    sparse_nodes=4440, sparse_edges=14767, sparse_deg=6.652,
    dense_nodes=469, dense_edges=2788, dense_deg=11.889,
    # rel_gain = LEARNED_HELDOUT@2 - DEGREE_ONLY@2
    rel_gain_sparse=0.0837, rel_gain_dense=0.0220, rel_gain_rise=-0.0617,
    rel_gain_rise_per_seed=[-0.0552, -0.0620, -0.0680], rel_gain_rise_std=0.0052, all_seeds_neg=True,
    codes_margin_sparse=0.0107, codes_margin_dense=0.0033, codes_margin_rise=-0.0074,
    # KEY: KNOWN_T full-map ORACLE ceiling reach@2 on the SAME held-out chains
    oracle_knownT2_sparse=0.4618, oracle_knownT2_dense=0.0433, oracle_drop_x=10.7,
    oracle_knownT2_sparse_per_seed=[0.451, 0.452, 0.482],
    oracle_knownT2_dense_per_seed=[0.033, 0.051, 0.046],
    # memoryless floor on held-out chains
    ho_mem2_sparse=0.0172, ho_mem2_dense=0.0082,
    # dynamic range = oracle - memoryless floor
    dynrange_sparse=0.445, dynrange_dense=0.035, dynrange_compress_x=12.7,
    # ceiling-normalized relational signal (STRONGER on dense)
    learned_frac_oracle_sparse=0.248, learned_frac_oracle_dense=0.802,
    relgain_over_dynrange_sparse=0.188, relgain_over_dynrange_dense=0.627,
    # arm decomposition (SPARSE)
    learned2_sparse=0.1148, memctrl2_sparse=0.0424, codealias2_sparse=0.1040, degree2_sparse=0.0310,
    hole_fill_learned_minus_memctrl_sparse=0.0723,
    # Gate-D positive-control reproduction (certified learned-SR anchors)
    repro_mem1=0.4628, repro_mem1_exp=0.453, repro_sup1=0.7442, repro_sup1_exp=0.756,
    repro_sup2=0.4938, repro_sup2_exp=0.500, repro_knownT2=0.4381, repro_knownT2_exp=0.434, repro_tol=0.10,
    # anti-sat controls
    baseline_collapses=True, supplied_fires=True, hop1_present=True, enough_heldout=True,
    n_heldout_sparse=1021, n_heldout_dense=893,
    # mechanism self-test
    st_rel_gain_rel=0.7923, st_rel_gain_deg=-0.7308, st_gap=1.5231,
)

# ===========================================================================
# ATOM 1 - math, HARD_FAIL honest-negative + branchiness-confound scope
# ===========================================================================
atom_math = {
    "id": ("math::HARD_FAIL_density_alone_via_kcore_densification_does_NOT_raise_held_out_relational_reasoning_reach"
           "_rel_gain_sparse_0p084_dense_0p022_rise_neg0p062_3seed_std0p005_all_neg_BUT_this_is_a_BRANCHINESS_CONFOUND"
           "_the_KNOWN_T_ORACLE_ceiling_reach_at_2_ALSO_collapses_0p462_sparse_to_0p043_dense_10p7x_dynamic_range_"
           "oracle_minus_memoryless_compresses_12p7x_0p445_to_0p035_dense_kcore_k7_deg_11p89_469nodes_2788edges_is_"
           "a_SUBSET_of_sparse_4440nodes_14767edges_deg_6p65_MORE_same_relation_siblings_per_hop_lowers_routing_"
           "ceiling_so_absolute_rel_gain_DOOMED_to_shrink_regardless_ceiling_normalized_substrate_relational_signal"
           "_is_STRONGER_on_dense_learned_over_oracle_0p80_vs_0p25_relgain_over_dynrange_0p63_vs_0p19_SCOPE_refutes"
           "_ONLY_kcore_densify_a_node_subset_NOT_richer_knowledge_entirely_UNTESTED_more_relation_types_more_"
           "entities_cleaner_edges_hard_limit_is_INDUCTIVE_INFERENCE_ITSELF_KNOWN_T_traversal_works_MM_0p46_infer_"
           "beyond_withheld_barely_beats_random_codes_margin_0p011_3seed_n4440_2026-07-09"),
    "name": ("MATH HARD_FAIL (honest-negative, BRANCHINESS-CONFOUNDED for the strong reading): density-alone via "
             "k-core densification does NOT raise held-out relational-reasoning reach (rel_gain sparse 0.084 -> dense "
             "0.022, rise -0.062, 3-seed std 0.005, all seeds negative). The verdict is CORRECTLY SCORED per pre-reg "
             "bands, BUT the mechanism is BRANCHINESS: the KNOWN_T ORACLE ceiling reach@2 on the same held-out chains "
             "ALSO collapses 0.462 -> 0.043 (10.7x) on the dense k-core, and the oracle-minus-memoryless dynamic range "
             "compresses 12.7x (0.445 -> 0.035). The dense 'graph' is a 469-node k-core SUBSET (2788 edges, deg 11.89) "
             "of the 4440-node/14767-edge sparse graph (deg 6.65) - FEWER nodes/edges, higher local branchiness. More "
             "same-relation siblings per hop lowers the routing ceiling, so the ABSOLUTE rel_gain was doomed to shrink "
             "regardless of any learning benefit. Ceiling-NORMALIZED, the substrate's relational signal is actually "
             "STRONGER on dense (learned/oracle 0.80 vs 0.25; rel_gain/dynrange 0.63 vs 0.19). SCOPE: refutes only "
             "'k-core-densify a node subset = the reasoning lever', NOT 'richer knowledge enables reasoning' - the "
             "other richness axes (more relation-TYPES, more distinct ENTITIES, cleaner/less-noisy edges) were NOT "
             "varied. The hard limit is INDUCTIVE INFERENCE ITSELF: goal-conditioned traversal over KNOWN structure "
             "works (KNOWN_T reach@2 0.46, reproduces certified MM 0.434); inferring reachability of withheld nodes "
             "barely beats random codes (codes_margin 0.011). 3 seeds [7,13,17], n=4440, k-core k=7."),
    "corpus": "math",
    "tier": "HARD_FAIL",
    "kind": "experiment_landed_vet",
    "cert_status": ("hard_fail_honest_negative_density_alone_kcore_not_the_reasoning_lever_but_branchiness_confounded"
                    "_for_the_strong_reading_oracle_ceiling_also_collapses"),
    "cert_class": ("held_out_relational_reach_at_2_learned_minus_degree_gain_rise_across_kcore_density_ladder_vs_"
                   "known_T_oracle_ceiling_dynamic_range_normalization"),
    "description": (
        "Independent off-disk recompute (3 seeds [7,13,17], n=4440, E=14767, k-core k=7) reproduces EVERY headline "
        "gate exactly from per_seed.arms[*].reach (NOT verdict_msg; Fix #28). SCP-recovered metrics.json (remote "
        "sync-lag). Disposition: the pre-registered HARD_FAIL_DENSITY_ALONE_NOT_THE_ENABLER is CORRECTLY SCORED "
        "(rel_gain_rise -0.062 <= 0.03 flat AND codes_margin_rise -0.007 <= 0.02 flat; density_no_help=True). It is an "
        "HONEST NEGATIVE for the NARROW roadmap claim. But it is BRANCHINESS-CONFOUNDED for the strong reading, and "
        "must NOT be over-read as 'the substrate cannot benefit from richer knowledge'.\n\n"
        "HEADLINE (independently recomputed):\n"
        "  rel_gain (LEARNED_HELDOUT@2 - DEGREE_ONLY@2): SPARSE 0.0837 -> DENSE 0.0220, rise -0.0617.\n"
        "  Per-seed rise [-0.0552, -0.0620, -0.0680], mean -0.0617, std 0.0052, ALL 3 seeds negative (robust).\n"
        "  codes_margin (LEARNED - CODEALIAS): SPARSE 0.0107 -> DENSE 0.0033, rise -0.0074.\n\n"
        "THE KEY MECHANISM = BRANCHINESS (oracle ceiling ALSO collapses on dense):\n"
        "  KNOWN_T full-map ORACLE ceiling reach@2 on the SAME held-out chains: SPARSE 0.4618 -> DENSE 0.0433 (10.7x "
        "drop). Per-seed sparse [0.451,0.452,0.482] -> dense [0.033,0.051,0.046].\n"
        "  Held-out memoryless floor: SPARSE 0.0172 -> DENSE 0.0082.\n"
        "  Dynamic range (oracle - memoryless floor): SPARSE 0.445 -> DENSE 0.035 = 12.7x COMPRESSION.\n"
        "  => Even with PERFECT knowledge of reachability (full transition matrix), reach@2 on the dense k-core is "
        "near the floor. The dense graph is INTRINSICALLY MUCH HARDER TO ROUTE, not 'easier because richer'. The "
        "dense k-core (deg 11.89, ~1.8x the sparse 6.65) has more same-relation siblings per hop, so the 1-of-many "
        "reach@2 routing task has a far lower ceiling. The absolute rel_gain metric (a DIFFERENCE of two reach@2 "
        "values) was doomed to shrink as that ceiling collapsed - independent of whether density helps learning.\n\n"
        "CEILING-NORMALIZED, the substrate's relational signal is STRONGER on dense (the opposite of the naive read):\n"
        "  learned2 / oracle_ceiling: SPARSE 0.248 -> DENSE 0.802.\n"
        "  rel_gain / dynamic_range: SPARSE 0.188 -> DENSE 0.627.\n"
        "  So the substrate captures a LARGER fraction of the (much smaller) available headroom on dense. The "
        "absolute-scale HARD_FAIL is a dynamic-range artifact of branchiness, not a relational-signal failure.\n\n"
        "SCOPE (what this DOES and does NOT refute):\n"
        "  DENSE here = a 469-node k-core SUBSET (2788 edges) of the 4440-node/14767-edge sparse graph. It has FEWER "
        "nodes AND FEWER edges - just higher LOCAL degree. 'Density' = degree-density on a subset, NOT added "
        "knowledge. So the cell cannot even in principle test 'more knowledge'; it tests 'route on a denser subset'.\n"
        "  REFUTES: 'k-core-densify the same graph = the reasoning lever' (narrow, robust negative).\n"
        "  DOES NOT REFUTE: 'richer knowledge enables reasoning'. The other richness axes were NOT varied: more "
        "relation-TYPES, more distinct ENTITIES/nodes, higher-quality/less-noisy edges, longer-range structure.\n\n"
        "RECONCILE with graph_inductive_ceiling_v1 (test #4, MEASURED_MECHANISM, same k-core ladder n4440/E14767/k7): "
        "#4's density-raises-edge-prediction-AUC is about PREDICTING-AN-EDGE-EXISTS (local binary classification, and "
        "that +0.062 was itself already flagged a PA/degree artifact: PA AUC 0.755 sparse collapses to 0.622 dense). "
        "THIS cell's reach@2 is ROUTING-TO-THE-RIGHT-SUCCESSOR-AMONG-MORE-SIBLINGS (1-of-many selection whose ceiling "
        "drops with branchiness). Predicting-edge-exists != routing-among-siblings = the ceiling-vs-reach gap. Fully "
        "consistent: k-core densification adds local popularity signal (marginal AUC) but raises branchiness (routing "
        "ceiling collapse).\n\n"
        "WHAT ENABLES INDUCTIVE REASONING (the settled nuance):\n"
        "  Goal-conditioned traversal over KNOWN structure WORKS: KNOWN_T reach@2 = 0.462 (sparse), reproducing the "
        "certified learned-SR MM anchor (0.438 vs 0.434, within tol).\n"
        "  The hard wall is INFERRING BEYOND the known: LEARNED_HELDOUT reach@2 = 0.115 clears the hole-leaving "
        "MEMCTRL 0.042 (+0.072 hole-fill = real) but BARELY beats random-code CODEALIAS 0.104 (codes_margin 0.011). "
        "The limit is INDUCTIVE INFERENCE ITSELF (generalizing reachability to unseen/withheld nodes), not knowledge "
        "density. Density (k-core) is the WRONG lever because it raises branchiness.\n\n"
        "POSITIVE CONTROLS + VALIDITY (not saturation-vacuous):\n"
        "  Gate-D repro all pass (within tol 0.10): mem1 0.463 (exp 0.453), sup1 0.744 (0.756), sup2 0.494 (0.500), "
        "knownT2 0.438 (0.434). Anti-sat: baseline_collapses=True, supplied_fires=True, hop1_present=True, "
        "enough_heldout=True (1021 sparse / 893 dense held-out chains). Mechanism self-test FIRES: rel_gain(REL)=0.792 "
        ">= 0.20, rel_gain(DEG)=-0.731 <= 0.05, gap=1.523 >= 0.15 (the rel_gain metric proven degree-independent). No "
        "seed failures. So the TEST is valid; the confound is that the k-core density ladder conflates 'more "
        "knowledge' with 'harder routing regime', and the absolute rel_gain discriminator cannot separate them.\n\n"
        "TIER: HARD_FAIL (honest-negative for the narrow claim; proven roadmap-scoping negative). cert_increment_delta"
        "=0 (a negative closes a direction; does not increment chain-grade N). The MEASURED_MECHANISM branchiness "
        "characterization (oracle ceiling collapse + dynamic-range compression) is the load-bearing scope guard.\n\n"
        "REVIVAL / roadmap criterion: to test 'richer knowledge helps reasoning' HONESTLY, vary a richness axis that "
        "does NOT co-vary branchiness (more relation-TYPES, more distinct ENTITIES, cleaner edges) AND/OR normalize "
        "the reach-gain by the KNOWN_T oracle dynamic range (or match branchiness/out-degree across the compared "
        "regimes) so the discriminator is not confounded by routing-difficulty shifts. Attacking the inductive-"
        "inference mechanism directly (better code-space smoothing / generalization to withheld nodes) is the more "
        "promising lever than ingesting denser graphs on the same nodes."
    ),
    "aliases": [],
    "metadata": {
        "provenance_quality": "HARD_FAIL_HONEST_NEGATIVE_BRANCHINESS_CONFOUNDED_STRONG_READING",
        "cert_status": "hard_fail_honest_negative",
        "cert_class": "density_alone_kcore_not_reasoning_lever_branchiness_confound",
        "verdict_cell": "HARD_FAIL_DENSITY_ALONE_NOT_THE_ENABLER",
        "verdict_scored_correctly": True,
        "anchor": ANCHOR,
        "cell_commit": CELL_COMMIT,
        "metrics_path": METRICS_PATH,
        "verified_off_data": (
            "Cert-owner SCP-recovered metrics.json (remote sync-lag) and recomputed off per_seed.arms[*].reach + "
            "heldout_refs directly via .venv Python (independent of verdict_msg; Fix #28). Reproduced: rel_gain sparse "
            "0.0837 / dense 0.0220 / rise -0.0617 (per-seed [-0.0552,-0.0620,-0.0680], std 0.0052, all neg). "
            "KNOWN_T oracle reach@2 held-out sparse 0.4618 / dense 0.0433 (per-seed sparse [0.451,0.452,0.482] dense "
            "[0.033,0.051,0.046]). Dynamic range (oracle-memoryless) sparse 0.445 / dense 0.035 (12.7x). learned/oracle "
            "sparse 0.248 / dense 0.802. Gate-D repro mem1 0.463 sup1 0.744 sup2 0.494 knownT2 0.438 all within 0.10. "
            "Anti-sat controls fire; self-test rel_gain(REL) 0.792 / (DEG) -0.731 / gap 1.523. DENSE=469 nodes/2788 "
            "edges subset of SPARSE 4440/14767. Cross-arc overlap check: top hits REASONING_ROUTING_PASS (0.379) / "
            "inductive_reasoning (0.357) - general routing concepts, NONE is this branchiness-confound finding; novel."
        ),
        "honest_scope": (
            "REFUTES 'k-core-densify a node subset = the reasoning lever' (robust 3-seed negative, correctly scored). "
            "DOES NOT refute 'richer knowledge enables reasoning' - the k-core ladder SUBSETS to a denser core (fewer "
            "nodes/edges, higher branchiness) and does not add knowledge; other richness axes (relation-types, "
            "entities, edge-quality) untested. The absolute-rel_gain HARD_FAIL is confounded by the oracle-ceiling "
            "collapse (branchiness); ceiling-normalized, the relational signal is stronger on dense. The proven "
            "positive is that goal-conditioned traversal over KNOWN structure works (MM 0.46); the proven wall is "
            "inferring reachability of withheld nodes (barely beats random codes, margin 0.011)."
        ),
        "n_seeds": 3, "seeds": M["seeds"], "n_nodes": M["n_nodes"], "n_edges": M["n_edges"], "kcore_k": M["kcore_k"],
        "metrics": {
            "rel_gain_sparse": M["rel_gain_sparse"], "rel_gain_dense": M["rel_gain_dense"],
            "rel_gain_rise": M["rel_gain_rise"], "rel_gain_rise_per_seed": M["rel_gain_rise_per_seed"],
            "rel_gain_rise_std": M["rel_gain_rise_std"], "all_seeds_neg": M["all_seeds_neg"],
            "codes_margin_sparse": M["codes_margin_sparse"], "codes_margin_dense": M["codes_margin_dense"],
            "codes_margin_rise": M["codes_margin_rise"],
            "oracle_knownT2_sparse": M["oracle_knownT2_sparse"], "oracle_knownT2_dense": M["oracle_knownT2_dense"],
            "oracle_drop_x": M["oracle_drop_x"],
            "oracle_knownT2_sparse_per_seed": M["oracle_knownT2_sparse_per_seed"],
            "oracle_knownT2_dense_per_seed": M["oracle_knownT2_dense_per_seed"],
            "dynrange_sparse": M["dynrange_sparse"], "dynrange_dense": M["dynrange_dense"],
            "dynrange_compress_x": M["dynrange_compress_x"],
            "learned_frac_oracle_sparse": M["learned_frac_oracle_sparse"],
            "learned_frac_oracle_dense": M["learned_frac_oracle_dense"],
            "relgain_over_dynrange_sparse": M["relgain_over_dynrange_sparse"],
            "relgain_over_dynrange_dense": M["relgain_over_dynrange_dense"],
            "sparse_nodes": M["sparse_nodes"], "sparse_edges": M["sparse_edges"], "sparse_deg": M["sparse_deg"],
            "dense_nodes": M["dense_nodes"], "dense_edges": M["dense_edges"], "dense_deg": M["dense_deg"],
            "learned2_sparse": M["learned2_sparse"], "memctrl2_sparse": M["memctrl2_sparse"],
            "codealias2_sparse": M["codealias2_sparse"], "degree2_sparse": M["degree2_sparse"],
            "hole_fill_learned_minus_memctrl_sparse": M["hole_fill_learned_minus_memctrl_sparse"],
            "repro_mem1": M["repro_mem1"], "repro_sup1": M["repro_sup1"], "repro_sup2": M["repro_sup2"],
            "repro_knownT2": M["repro_knownT2"], "repro_tol": M["repro_tol"],
            "st_rel_gain_rel": M["st_rel_gain_rel"], "st_rel_gain_deg": M["st_rel_gain_deg"], "st_gap": M["st_gap"],
        },
        "branchiness_confound": True,
        "oracle_ceiling_also_falls_on_dense": True,
        "ceiling_normalized_signal_stronger_on_dense": True,
        "dense_is_node_subset_not_added_knowledge": True,
        "hard_limit_is_inductive_inference_itself": True,
        "known_traversal_works_MM": True,
        "revival_criteria": [
            "vary_a_richness_axis_that_does_not_covary_branchiness_relation_types_entities_edge_quality",
            "normalize_reach_gain_by_KNOWN_T_oracle_dynamic_range_or_match_out_degree_across_compared_regimes",
            "attack_inductive_inference_mechanism_directly_better_codespace_smoothing_generalization_to_withheld_nodes",
        ],
        "composes_with": [
            ("math::MEASURED_MECHANISM_graph_inductive_predictability_ceiling_of_real_conceptnet_subgraph_is_AUC_0p76"
             " (test #4, same k-core ladder n4440/E14767/k7; ceiling-vs-reach reconcile: predict-edge-exists != "
             "route-among-siblings; both consistent with branchiness rising on dense)"),
            "certified_learned_sr_heldout_reasoning_v1 (KNOWN_T MM 0.434 anchor reproduced at 0.438)",
        ],
        "cites": [
            "Fix_28_verify_per_arm_metrics_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "SH-9_scp_recover_before_citing_remote_numbers",
            "substrate_kb_concept_overlap_check_on_schema_vet_USER_locked_2026-07-01",
            "grounding_needs_active_intervention_exogenous_referent_3source_synthesis_2026-07-09",
        ],
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
    },
}

# ===========================================================================
# ATOM 2 - meta, CERT-neutral methodology rule
# ===========================================================================
atom_meta = {
    "id": ("meta::META_density_or_richness_ladder_that_shifts_the_reach_at_K_oracle_ceiling_CONFOUNDS_an_absolute_"
           "reach_gain_discriminator_with_ROUTING_BRANCHINESS_kcore_densification_raises_out_degree_lowers_1_of_many"
           "_routing_ceiling_so_a_learned_minus_degree_gain_DIFFERENCE_shrinks_on_the_denser_regime_regardless_of_"
           "learning_check_KNOWN_T_oracle_ceiling_across_the_ladder_FIRST_if_it_also_falls_normalize_by_oracle_"
           "dynamic_range_or_match_branchiness_before_reading_a_flat_gain_as_density_does_not_help_2026-07-09"),
    "name": ("META (cert-neutral): a density/richness ladder that SHIFTS the reach@K oracle ceiling CONFOUNDS an "
             "absolute reach-gain discriminator with routing BRANCHINESS. k-core densification raises out-degree, "
             "which lowers the 1-of-many routing ceiling, so a learned-minus-baseline reach DIFFERENCE shrinks on the "
             "denser regime REGARDLESS of any learning benefit. Before reading a flat/falling gain as 'density does "
             "not help', check the KNOWN_T (oracle / perfect-knowledge) reach@K ceiling ACROSS the ladder FIRST; if "
             "it also falls, normalize the gain by the oracle dynamic range (or match out-degree/branchiness across "
             "the compared regimes)."),
    "corpus": "meta",
    "tier": "META_RULE_CERT_NEUTRAL",
    "kind": "methodology_rule",
    "cert_status": "meta_rule",
    "cert_class": "discipline_confound_elimination_regime_comparison",
    "description": (
        "RULE (cert-discipline, CERT-neutral): when a cell compares a mechanism arm's HELD-OUT reach@K gain across a "
        "ladder of graph DENSITY or RICHNESS regimes (e.g. sparse full graph vs dense k-core), an ABSOLUTE reach-gain "
        "difference (learned_reach - baseline_reach) is CONFOUNDED with routing BRANCHINESS. Denser regimes have "
        "higher out-degree = more same-relation siblings per hop = a lower ceiling for any 1-of-many routing task at "
        "depth >= 2. So the absolute gain DIFFERENCE can shrink on the denser regime purely because the whole reach "
        "dynamic range compresses - NOT because the mechanism benefits less from density.\n\n"
        "DIAGNOSTIC (mandatory before reading a flat/falling absolute gain as 'density does not help'):\n"
        "  1. Compute the KNOWN_T / ORACLE (perfect-knowledge full transition matrix) reach@K ceiling on the SAME "
        "held-out chains at EACH density level.\n"
        "  2. Compute the memoryless (or chance) floor at each level.\n"
        "  3. If the oracle ceiling - floor DYNAMIC RANGE shrinks materially across the ladder, the absolute-gain "
        "discriminator is CONFOUNDED. Report the CEILING-NORMALIZED gain (gain / dynamic_range, or mechanism_reach / "
        "oracle_reach) instead; and/or design the ladder to MATCH out-degree/branchiness across regimes so the "
        "confound is removed by construction.\n\n"
        "OBSERVED INSTANCE (2026-07-09, grounding_density_payoff_relational_reasoning_v1): the pre-reg gated on "
        "absolute rel_gain_rise (LEARNED@2 - DEGREE@2, dense minus sparse) and landed HARD_FAIL_DENSITY_ALONE_NOT_"
        "THE_ENABLER (rise -0.062). CORRECTLY SCORED, but the KNOWN_T oracle ceiling reach@2 on the same held-out "
        "chains ALSO collapsed 0.462 -> 0.043 (10.7x) and the oracle-minus-memoryless dynamic range compressed 12.7x "
        "(0.445 -> 0.035). The dense 'graph' was a 469-node k-core (deg 11.89) subset of the 4440-node sparse graph "
        "(deg 6.65). Ceiling-normalized, the relational signal was STRONGER on dense (learned/oracle 0.80 vs 0.25). "
        "So the flat/falling absolute gain was a branchiness/dynamic-range artifact; the strong reading 'density does "
        "not help the substrate reason' was NOT supported by the absolute-gain discriminator alone. The included "
        "DEGREE_ONLY confound control catches PURE-POPULARITY gains but does NOT control the routing-difficulty shift "
        "in the reach@K ceiling between regimes.\n\n"
        "SCOPE: applies to any across-regime comparison of a HELD-OUT reach@K (or any depth>=2 1-of-many routing/"
        "selection metric) where the regime axis co-varies out-degree/branchiness (density ladders, k-core subsets, "
        "hub-richness sweeps). Does NOT apply to depth-1 or binary edge-existence metrics whose ceiling is regime-"
        "invariant, nor to comparisons where branchiness is held fixed by construction. Complements (does not replace) "
        "the DEGREE_ONLY / preferential-attachment confound control: that isolates popularity WITHIN a regime; THIS "
        "isolates routing-difficulty ACROSS regimes."
    ),
    "aliases": [],
    "metadata": {
        "provenance_quality": "META_RULE_CERT_NEUTRAL",
        "cert_status": "meta_rule",
        "cert_class": "discipline",
        "rule_id": "M_REACH_GAIN_ACROSS_DENSITY_LADDER_CONFOUNDED_BY_BRANCHINESS_CHECK_ORACLE_CEILING_FIRST",
        "rule_category": "cross_regime_discriminator_confound_elimination",
        "rule_name": "normalize_reach_gain_by_oracle_dynamic_range_or_match_branchiness_across_density_ladder",
        "rule_text": (
            "When comparing a held-out reach@K (depth>=2 1-of-many routing) gain across graph density/richness "
            "regimes, first check the KNOWN_T oracle reach@K ceiling at each level. If the oracle ceiling (minus "
            "floor = dynamic range) shifts across the ladder, an ABSOLUTE reach-gain difference is confounded with "
            "routing branchiness (denser = higher out-degree = lower 1-of-many ceiling). Report ceiling-normalized "
            "gain (gain/dynamic_range or mechanism/oracle) and/or match out-degree across regimes before reading a "
            "flat/falling absolute gain as 'density/richness does not help'."
        ),
        "rebuttal_check_for_skunkworks_landed_VET": (
            "(a) Does the metric compare a HELD-OUT reach@K (K>=2, 1-of-many) ACROSS a density/richness ladder? "
            "(b) Does the regime axis co-vary out-degree/branchiness (k-core, hub-richness)? "
            "(c) Is the KNOWN_T oracle ceiling reach@K reported at EACH level, and does it move? "
            "If (a)+(b)+(c-moves): the absolute-gain discriminator is CONFOUNDED; demand ceiling-normalized gain or a "
            "branchiness-matched ladder before accepting a 'does-not-help' negative as a substantive finding."
        ),
        "observed_instances": [
            ("grounding_density_payoff_relational_reasoning_v1 (2026-07-09): HARD_FAIL_DENSITY_ALONE_NOT_THE_ENABLER "
             "correctly scored on absolute rel_gain_rise -0.062, but KNOWN_T oracle ceiling reach@2 collapsed 0.462->"
             "0.043 (10.7x) and dynamic range compressed 12.7x; ceiling-normalized relational signal STRONGER on "
             "dense (learned/oracle 0.80 vs 0.25). Strong reading 'density does not help the substrate reason' NOT "
             "supported by the absolute-gain discriminator; narrow reading 'k-core-densify-a-subset is not the lever' "
             "is the correct honest scope."),
        ],
        "composes_with": [
            "math::HARD_FAIL_density_alone_via_kcore_densification (the instance that motivated this rule)",
            "reference_crt_residue_helps_clean_encoding_hurts_noisy_readout_classify_regime_first",
            "feedback_discriminator_must_be_telemetry_sensitive_not_analytically_pinned",
        ],
        "honest_scope": (
            "Applies to across-regime comparisons of held-out reach@K / depth>=2 1-of-many routing metrics where the "
            "regime axis co-varies branchiness. Does NOT apply to depth-1 or binary edge-existence metrics (regime-"
            "invariant ceiling), nor to branchiness-matched ladders. Complements the DEGREE_ONLY/PA confound control "
            "(within-regime popularity) with an ACROSS-regime routing-difficulty control."
        ),
        "cites": [
            "grounding_density_payoff_relational_reasoning_v1_2026-07-09",
            "graph_inductive_ceiling_v1_ceiling_vs_reach_gap_predict_edge_exists_vs_route_among_siblings",
            "Fix_28_verify_per_arm_metrics_not_verdict_msg",
            "symmetric_anti_negativity_USER",
        ],
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
    },
}

# ===========================================================================
# CERT_LEDGER rows
# ===========================================================================
ts = time.time()

ledger_math = {
    "op": "cert_ruling",
    "atom_id": "math::" + atom_math["id"].split("::", 1)[1],
    "corpus": "math",
    "tier": "HARD_FAIL",
    "cert_status": "hard_fail_honest_negative",
    "cert_class": "density_alone_kcore_not_reasoning_lever_branchiness_confound",
    "anchor": ANCHOR,
    "cell_commit": CELL_COMMIT,
    "verified_off_data": True,
    "auditor": "skunkworks",
    "atomized_by": ATOMIZED_BY,
    "verdict": "HARD_FAIL_DENSITY_ALONE_NOT_THE_ENABLER_correctly_scored_but_BRANCHINESS_CONFOUNDED_strong_reading",
    "cert_increment_delta": 0,
    "cv": 0.0052,
    "decision": (
        "HARD_FAIL honest-negative: k-core densification does NOT raise held-out relational reach (rel_gain rise "
        "-0.062, 3-seed std 0.005, all neg). Correctly scored per pre-reg. BUT branchiness-confounded: KNOWN_T oracle "
        "ceiling reach@2 ALSO collapses 0.462->0.043 (10.7x), dynamic range compresses 12.7x; ceiling-normalized the "
        "relational signal is STRONGER on dense (learned/oracle 0.80 vs 0.25). DENSE = 469-node k-core subset of the "
        "4440-node sparse graph (fewer nodes/edges, higher branchiness) - 'density' is degree-density on a subset, "
        "not added knowledge."
    ),
    "scope_correction_vs_director": (
        "Director HELD interpretation (no over-read) - CONFIRMED correct. The verdict NAME "
        "'DENSITY_ALONE_NOT_THE_ENABLER / the wall is deeper' could be over-read as 'the substrate cannot benefit "
        "from richer knowledge'; the AUDIT scopes it to 'k-core-densify a NODE SUBSET is not the reasoning lever'. "
        "Does NOT refute 'richer knowledge enables reasoning' (relation-types / entities / edge-quality axes "
        "untested). The proven wall is inductive-inference-itself (inferring reachability of withheld nodes barely "
        "beats random codes, margin 0.011), not knowledge density."
    ),
    "net_cert_delta": (
        "+0 to chain-grade CERT N (honest negative; closes the 'densify-same-graph' roadmap direction, does not add a "
        "chain-grade capability). Records a proven roadmap-scoping negative + a MEASURED_MECHANISM branchiness "
        "characterization (oracle-ceiling collapse + dynamic-range compression) as the scope guard against over-read."
    ),
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "atom_qualified_id": "math::" + atom_math["id"].split("::", 1)[1],
    },
    "ts_iso": None,
    "ts": ts,
}

ledger_meta = {
    "op": "cert_ruling",
    "atom_id": "meta::" + atom_meta["id"].split("::", 1)[1],
    "corpus": "meta",
    "tier": "META_RULE_CERT_NEUTRAL",
    "cert_status": "meta_rule",
    "cert_class": "discipline",
    "anchor": ANCHOR,
    "cell_commit": CELL_COMMIT,
    "verified_off_data": True,
    "auditor": "skunkworks",
    "atomized_by": ATOMIZED_BY,
    "verdict": "META_reach_gain_across_density_ladder_confounded_by_branchiness_check_KNOWN_T_oracle_ceiling_first_normalize_by_dynamic_range_or_match_out_degree",
    "cert_increment_delta": 0,
    "cv": None,
    "decision": (
        "CERT-neutral methodology rule: a density/richness ladder that shifts the reach@K oracle ceiling confounds an "
        "absolute reach-gain discriminator with routing branchiness; check the KNOWN_T oracle ceiling across the "
        "ladder first, normalize by dynamic range or match out-degree before reading a flat gain as 'density does "
        "not help'. Complements the within-regime DEGREE_ONLY/PA control with an across-regime routing-difficulty "
        "control."
    ),
    "scope_correction_vs_director": "N/A (methodology rule; CERT-neutral).",
    "net_cert_delta": "+0 (CERT-neutral META rule).",
    "referent_pointer": {
        "metrics_path": "META_RULE_no_metrics_path",
        "atom_qualified_id": "meta::" + atom_meta["id"].split("::", 1)[1],
    },
    "ts_iso": None,
    "ts": ts,
}

from datetime import datetime, timezone
_iso = datetime.now(timezone.utc).isoformat()
atom_math["ts_iso"] = _iso; atom_math["ts"] = ts
atom_meta["ts_iso"] = _iso; atom_meta["ts"] = ts
ledger_math["ts_iso"] = _iso
ledger_meta["ts_iso"] = _iso


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
    print("=== A5 atom-write: density-payoff HF branchiness-confound (2026-07-09) ===")
    print("ts_iso =", _iso)
    print()
    print("Writing 1 atom to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom_math])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 1 atom to meta/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(META_ATOMS, [atom_meta])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: meta atoms write failed"); sys.exit(1)

    print("Writing 2 rows to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger_math, ledger_meta])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 2:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    print()
    print("=== A5 WRITE COMPLETE ===")
    for p in (MATH_ATOMS, META_ATOMS, CERT_LEDGER):
        with open(p, "rb") as f:
            n = f.read().count(b"\n")
        print("  %s: %d lines" % (p.name, n))
    print()
    print("CERT N delta: +0 (math HARD_FAIL honest-negative) ; +0 (meta CERT-neutral rule)")


if __name__ == "__main__":
    main()
