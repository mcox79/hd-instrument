"""
A5-gated atomization: VET'd operator-arc + cross-module-interface batch (2026-07-15).

USER-AUTHORIZED. All 6 dispositions independently VET'd off-disk (.venv, Fix #28: recompute
from metrics.json per_seed / verdict gates, NOT verdict_msg alone). Cross-arc overlap check
(USER-locked): substrate_query top hits are lexical wordnet only (CN_operative 0.3418,
noncombinative 0.3291 char-trigram) -- NO prior CERTIFIED experiment atom at cosine>0.30; grep of
math/atoms.jsonl for every anchor slug = 0. Genuinely novel arc.

6 atoms (all math corpus; experiment landed-vet):
 1. crossmodule_interface  -> CHAIN_GRADE, bound UPGRADED to HELDOUT_PREDICTIVE (v2 heldout landed).
 2. TRANSITION_OP          -> CHAIN_GRADE, dominance SPECIALIST, synthetic construction.
 3. joint_operator_capstone-> CHAIN_GRADE, ONE shared code + 2 readouts, ZERO interference.
 4. bilinear_wall          -> HF_STRUCTURAL_BOUND, single product/bilinear op = parity specialist only.
 5. nonadditive_discovery  -> CHAIN_GRADE scoped, reasoning-core construction (reads nonadd+noncomm).
 6. interference_avoidance -> CHAIN_GRADE construction-proof (conjunctive/orth beats additive+freq).

consolidation-MM: NOT atomized -- no named anchor in the task, ambiguous among ~20 consolidation
cells, no in-context VET report. FLAGGED BACK to Director instead of guessing.

A5: read -> build -> tmp write + fsync -> os.replace -> re-read + verify count delta + tail-id match.
Sequential single process (save_atoms NOT concurrency-safe): 6 atoms appended atomically to
math/atoms.jsonl, then 6 rows atomically to meta/cert_ledger.jsonl.
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
ATOMIZED_BY = "skunkworks_landed_vet_operator_arc_crossmodule_batch_2026-07-15"
ATOMIZED_DATE = "2026-07-15"

# --- atom ids (ASCII, no whitespace, no newline) ---
ID_XMOD = ("math::CHAIN_GRADE_crossmodule_interface_identity_anchored_hub_composes_real_BioGRID_physical_x_Costanzo_"
           "genetic_HUB_0p830_vs_single_ceiling_0p254_identity_anchor_load_bearing_remove_collapses_to_0p088_JOIN_"
           "precision_0p989_edge_jaccard_0p022_distinct_AND_HELDOUT_PREDICTIVE_v2_novel_HUB_0p831_vs_ceiling_0p250_"
           "400_conjunctions_never_stored_no_direct_edge_margin_0p397_5seed_construction_plus_heldout_not_biology_"
           "prediction_synthetic_free_real_2module_data_v1_2026-07-15")
ID_TRANS = ("math::CHAIN_GRADE_TRANSITION_OP_asymmetric_matrix_chain_TEM_successor_reads_antisymmetric_DOMINANCE_1p000_"
            "5of5_sd0_clears_FREQ_0p778_by_0p222_order_attributed_TRANS_minus_SHUF_0p578_while_SYM_0p477_and_BILINEAR_"
            "0p485_provably_cannot_dominance_SPECIALIST_not_parity_par_0p685_synthetic_construction_learned_M_i_"
            "v1_2026-07-15")
ID_JOINT = ("math::CHAIN_GRADE_joint_operator_capstone_ONE_shared_code_two_selective_readouts_solves_BOTH_parity_0p998_"
            "and_dominance_1p000_with_ZERO_measured_interference_rel_drop_par_neg0p006_dom_0p000_beats_prior_joint_dual_"
            "MIDDLE_0p816_0p164_all_9_gates_pass_M_equals_I_identity_exact_MATCHES_specialists_win_is_zero_interference_"
            "rank_R_count_saturated_R1_synthetic_construction_v1_2026-07-15")
ID_BILIN = ("math::HF_STRUCTURAL_BOUND_single_learned_bilinear_product_op_is_ANOTHER_PARITY_SPECIALIST_ONLY_hero_parity_"
            "0p978_matches_SYM_but_dominance_0p485_below_role_specialist_1p000_and_freq_0p778_rank1_to_4_capacity_ruled_"
            "out_R4_dom_0p503_native_product_bind_bounded_to_COMMUTATIVE_asymmetric_requires_role_keying_two_channel_"
            "synthetic_v1_2026-07-15")
ID_NONADD = ("math::CHAIN_GRADE_interaction_nonadditive_discovery_reasoning_core_INT_operator_reads_BOTH_symmetric_"
             "nonadditive_parity_1p000_vs_MONO_0p477_and_antisymmetric_noncommutative_dominance_1p000_vs_FREQ_0p778_"
             "that_no_additive_monadic_frequency_baseline_can_MI_margins_genuine_parity_joint_0p999_vs_single_0p003_"
             "controls_fire_ceiling_synthetic_construction_5seed_v1_2026-07-15")
ID_INTERF = ("math::CHAIN_GRADE_interference_avoidance_conjunctive_orthogonal_storage_beats_additive_AND_frequency_for_"
             "single_driver_attribute_at_M_HI_256_orth_1p000_add_0p273_freq_0p654_gap_orth_add_0p727_crossover_M48_"
             "disjoint_control_gap_0p000_clean_3of3_seeds_pattern_separation_hedge_holds_construction_proof_synthetic_"
             "v1_2026-07-15")

# ==================================================================================================
atoms = []
ledgers = []

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()


def mk(atom, ledger):
    atom["ts_iso"] = _iso
    atom["ts"] = _ts
    ledger["ts_iso"] = _iso
    ledger["ts"] = _ts
    ledger["atom_id"] = atom["id"]
    atoms.append(atom)
    ledgers.append(ledger)


# --------------------------------------------------------------------------------------------------
# 1. CROSS-MODULE INTERFACE  (CHAIN_GRADE; bound upgraded to HELDOUT_PREDICTIVE)
# --------------------------------------------------------------------------------------------------
mk(
    {
        "id": ID_XMOD,
        "name": ("MATH CHAIN_GRADE (foundation-architecture, bound UPGRADED to HELDOUT-PREDICTIVE): identity-anchored "
                 "hub-and-spoke interface composes TWO REAL biology modules (BioGRID physical-interaction x Costanzo "
                 "genetic-interaction) -- HUB conjunctive recall 0.830 vs single-module ceiling 0.254 (GEN_ONLY), the "
                 "identity-anchor is load-bearing (remove it -> NO_HUB 0.088, ~SCRAMBLE 0.088 / RANDOM 0.019), JOIN "
                 "precision 0.989 with edge_jaccard 0.022 (modules genuinely distinct, fuzzy_gain 0.0). HELDOUT-"
                 "PREDICTIVE upgrade (v2): on 400 NOVEL conjunctions never stored with no direct edge, novel HUB 0.831 "
                 "vs single-ceiling 0.250 (margin 0.397), seen HUB 0.827 -- held-out compositional recovery, not just "
                 "storage. 5 seeds [7,13,17,23,29]. SCOPE: this is a CONSTRUCTION + HELD-OUT-COMPOSITIONAL-RECOVERY "
                 "proof on real 2-module data (the reasoning-architecture recovering cross-module conjunctions), NOT a "
                 "biological-discovery/prediction claim."),
        "corpus": "math",
        "tier": "CHAIN_GRADE",
        "kind": "experiment_landed_vet",
        "cert_status": ("confirmed_chain_grade_identity_anchored_hub_and_spoke_composes_real_biogrid_costanzo_and_"
                        "predicts_heldout_novel_conjunctions_identity_anchor_load_bearing_join_clean_modules_distinct"),
        "cert_class": ("cross_module_interface_identity_anchored_hub_and_spoke_compositional_recovery_heldout_"
                       "predictive_real_two_module_biology_data_construction_plus_generalization"),
        "description": (
            "Independent off-disk landed-VET (.venv; recompute from per_seed + verdict gates, Fix #28). TWO cells.\n\n"
            "CELL v1 (crossmodule_interface_hub_identity_bind_costanzo_biogrid_v1, commit 224666483, VET a7e1d82e): "
            "per-seed HUB {0.8122,0.82932,0.81663,0.85538,0.83646} -> mean 0.830; MERGED 0.437; NO_HUB 0.088 "
            "(identity-anchor removed); SCRAMBLE 0.088; RANDOM 0.019; PHYS_ONLY 0.219; GEN_ONLY 0.254 (=single_ceiling); "
            "margin_abs 0.393; hub>=1.5x merged True; must-fails (scramble, no-hub <= ceil+0.05 AND hub-arm>=0.15) fire. "
            "JOIN precision 0.9892 (>=0.90), n_shared 5356, fuzzy_gain 0.0, edge_jaccard 0.0219 (<=0.50 -> modules "
            "distinct). arms_differ True, deterministic. 598 queries, 400 vertices, 3176 phys + 2843 gen edges.\n\n"
            "CELL v2 HELDOUT (crossmodule_interface_hub_identity_bind_heldout_v2): 794 queries (seen 394, novel 400, "
            "novel_no_direct_edge True, conj_never_stored True). NOVEL stratum: HUB 0.8315 (per-seed "
            "{0.85042,0.84223,0.81538,0.82971,0.81987}), MERGED 0.435, NO_HUB 0.093, SCRAMBLE 0.098, RANDOM 0.019, "
            "single_ceiling 0.2496, margin_abs 0.3967, beats_single True, mustfails_ok True. SEEN stratum HUB 0.827, "
            "ceiling 0.265. ALL HUB 0.829, all_pass True. verdict HARD_PASS_INTERFACE_HUB_HELDOUT_PREDICTIVE.\n\n"
            "TIER: CHAIN_GRADE. The base construction (store + compose + recover on real 2-module data) is confirmed, "
            "AND the held-out predictive upgrade criterion (module-2b) landed and reproduces: the identity-anchored hub "
            "recovers 400 novel cross-module conjunctions that were never stored and have no direct edge, at 0.83 vs a "
            "0.25 single-module ceiling. This is held-out COMPOSITIONAL generalization of the reasoning architecture on "
            "REAL biology data. HONEST SCOPE: it is a compositional-recovery proof, not a claim to predict new biology; "
            "the 'prediction' is of held-out conjunctive structure implied by the two stored single-module graphs, not "
            "of unseen experimental measurements. cert_increment_delta=1."
        ),
        "aliases": [
            "identity-anchored hub-and-spoke composes real BioGRID x Costanzo HUB 0.83 vs single-ceiling 0.254",
            "identity anchor load-bearing removing it collapses hub to 0.088 near scramble",
            "cross-module interface heldout predictive novel HUB 0.831 vs 0.250 on 400 conjunctions never stored no direct edge",
            "JOIN precision 0.989 edge jaccard 0.022 modules distinct fuzzy gain zero",
        ],
        "metadata": {
            "provenance_quality": "CHAIN_GRADE_construction_plus_heldout_predictive_recompute_off_per_seed_controls_fire",
            "anchor": "crossmodule_interface_hub_identity_bind_costanzo_biogrid_v1 (+ heldout_v2)",
            "cell_commit": "224666483 (v1); heldout_v2 local run 2026-07-15T23:17Z",
            "vet_id": "a7e1d82e (v1) + off-disk heldout recompute this session",
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": ["data/exp_crossmodule_interface_hub_identity_bind_costanzo_biogrid_v1/metrics.json",
                             "data/exp_crossmodule_interface_hub_identity_bind_heldout_v2/metrics.json"],
            "verified_off_data": ("Recomputed HUB per-seed mean 0.830 (v1) / novel 0.8315 (v2) from per_seed maps; NO_HUB "
                                  "0.088 confirms identity-anchor load-bearing; JOIN precision 0.9892, edge_jaccard "
                                  "0.0219; heldout novel_no_direct_edge=True conj_never_stored=True margin 0.397. Cross-"
                                  "arc overlap: substrate_query lexical-only (no prior cert atom >0.30); grep anchor=0."),
            "honest_scope": ("Construction + HELD-OUT compositional recovery on REAL 2-module biology data (BioGRID "
                             "physical x Costanzo genetic). NOT a biological-prediction/discovery claim -- recovers "
                             "held-out conjunctive structure implied by the two stored single-module graphs. Synthetic-"
                             "free (real edges) but the target is compositional recall, not novel measurement."),
            "n_seeds": 5, "seeds": [7, 13, 17, 23, 29],
            "metrics": {"hub_mean_v1": 0.830, "single_ceiling_v1": 0.2543, "no_hub_v1": 0.0876,
                        "scramble_v1": 0.0877, "merged_v1": 0.4372, "join_precision": 0.9892, "edge_jaccard": 0.0219,
                        "heldout_novel_hub": 0.8315, "heldout_novel_ceiling": 0.2496, "heldout_novel_margin": 0.3967,
                        "heldout_seen_hub": 0.8270, "n_novel_conjunctions_never_stored": 400},
            "bound": "CHAIN_GRADE_construction_plus_HELDOUT_PREDICTIVE_upgrade_landed",
            "composes_with": [
                "reasoning architecture = additive_map shared-code compositional-readout (real-data lineage)",
                "project_reasoning_theory_constraints_brought_to_bear (identity-anchor = a brought-to-bear constraint)",
            ],
            "cites": ["Fix_28_verify_off_data_not_verdict_msg", "symmetric_anti_negativity_verify_both_directions_USER",
                      "feedback_construction_proof_is_not_a_capability_win_ask_could_it_fail_informatively",
                      "feedback_never_narrate_synthetic_HD_bundles_as_english_language_capability_USER"],
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE, "needs_orchestrator_store_sync": True,
        },
    },
    {
        "op": "cert_ruling", "corpus": "math", "tier": "CHAIN_GRADE",
        "cert_status": "confirmed_chain_grade_crossmodule_interface_heldout_predictive",
        "anchor": "crossmodule_interface_hub_identity_bind_costanzo_biogrid_v1+heldout_v2",
        "cell_commit": "224666483", "store_head_at_write": "unsynced_needs_orchestrator",
        "verified_off_data": True, "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "verdict": "HARD_PASS_construction_confirmed_AND_heldout_predictive_upgrade_landed_HUB_0p830_v1_novel_0p831_v2",
        "cert_increment_delta": 1,
        "decision": ("CHAIN_GRADE. Base construction (compose+recover real BioGRID x Costanzo, HUB 0.830 vs ceiling "
                     "0.254, identity-anchor load-bearing NO_HUB 0.088, JOIN 0.989) confirmed off-disk; the held-out "
                     "upgrade criterion (module-2b) LANDED and reproduces (novel HUB 0.831 vs 0.250 on 400 conjunctions "
                     "never stored, no direct edge, margin 0.397). Bound UPGRADED construction -> heldout-predictive."),
        "framing_correction_vs_director": ("Director framed the base cell as construction with held-out as the upgrade "
                                           "criterion. The upgrade LANDED before write, so I atomize at the higher bound "
                                           "(HELDOUT_PREDICTIVE) -- but I TIGHTEN the scope: this is held-out "
                                           "COMPOSITIONAL RECOVERY on real 2-module data, NOT a biology-prediction claim; "
                                           "the recovered conjunctions are implied by the two stored single-module graphs."),
        "cross_arc_overlap_check": "substrate_query lexical-only (CN_operative 0.34, noncombinative 0.33); no prior cert experiment atom >0.30; grep anchor=0. Novel.",
        "net_cert_delta": "+1 CHAIN_GRADE (foundation-architecture: identity-anchored hub composes + predicts heldout cross-module conjunctions on real data).",
        "needs_orchestrator_store_sync": True,
    },
)

# --------------------------------------------------------------------------------------------------
# 2. TRANSITION_OP  (CHAIN_GRADE; dominance specialist, synthetic construction)
# --------------------------------------------------------------------------------------------------
mk(
    {
        "id": ID_TRANS,
        "name": ("MATH CHAIN_GRADE: a non-commutative matrix-chain (TEM-successor) TRANSITION_OP reads antisymmetric "
                 "DOMINANCE at 1.000 (5/5 seeds, sd=0), clearing the FREQ baseline 0.778 by +0.222; the win is "
                 "ORDER-attributed (TRANS - order-SHUFFLE = 0.578) and a symmetric operator (SYM 0.477) and a single "
                 "bilinear reference (BILINEAR_REF 0.485, ~chance 0.62) provably CANNOT read it. SCOPE: a DOMINANCE "
                 "SPECIALIST (parity only 0.685, not solved), SYNTHETIC, construction-proof (learned per-family M_i). "
                 "State-vs-FREQ, not vs chance."),
        "corpus": "math", "tier": "CHAIN_GRADE", "kind": "experiment_landed_vet",
        "cert_status": ("confirmed_chain_grade_transition_op_asymmetric_matrix_chain_reads_antisymmetric_dominance_"
                        "1p000_5of5_order_attributed_dominance_specialist_symmetric_and_bilinear_cannot"),
        "cert_class": "asymmetric_noncommutative_matrix_chain_transition_operator_dominance_specialist_synthetic_construction",
        "description": (
            "Independent off-disk landed-VET (.venv; gates + per-candidate, Fix #28). Anchor "
            "interaction_asymmetric_directed_operators_v1, commit 290400320, VET a61d3a0e. DOMINANCE (chance 0.62, "
            "antisymmetric): role_dom=1.0000, freq_dom=0.77778, sym_dom=0.47677. per_candidate TRANSITION_OP dom=1.0 "
            "(dominance_ok True, mustfail_ok True), parity 0.68485 (parity_ok False -> NOT a parity solver). "
            "HETEROASSOC_OP dom 0.774 (dom_ok False), PHASE_ORDER_OP dom 0.471 (dom_ok False). ATTRIBUTION: "
            "trans_order_confirmed True (trans_minus_shuf_dom 0.57778 -> the win comes from OPERATOR ORDER, not a "
            "lookup); phase_attribution_to_role_tag False (-0.022); hetero_lookup_confirmed False (seen-novel 0.026). "
            "clean_passers = ['TRANSITION_OP'] (unique). BILINEAR_REF 0.4849 (a single bilinear cannot). ceiling True, "
            "cardinality True. INT_MATCH par 1.0 dom 1.0 (refute False). 5 seeds [7,13,17,23,29], emb_d 48, 500 epochs.\n\n"
            "TIER: CHAIN_GRADE. A non-commutative matrix-chain operator provably reads antisymmetric dominance that "
            "symmetric and bilinear operators cannot, order-attributed and unique among the candidate operator set. "
            "SCOPE (honest): dominance SPECIALIST (parity 0.685 not solved), SYNTHETIC arena, construction-proof (the "
            "M_i are learned per family); the comparison of merit is vs FREQ (0.778), which it clears by +0.222, not vs "
            "chance. cert_increment_delta=1."
        ),
        "aliases": [
            "non-commutative matrix chain TEM-successor transition operator reads antisymmetric dominance 1.000 5 of 5",
            "transition op clears freq 0.778 by 0.222 order-attributed trans minus shuffle 0.578",
            "symmetric op 0.477 and bilinear 0.485 provably cannot read dominance dominance specialist not parity",
        ],
        "metadata": {
            "provenance_quality": "CHAIN_GRADE_recompute_off_gates_per_candidate_attribution_clean_unique_passer",
            "anchor": "interaction_asymmetric_directed_operators_v1", "cell_commit": "290400320", "vet_id": "a61d3a0e",
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_interaction_asymmetric_directed_operators_v1/metrics.json",
            "verified_off_data": ("gates: role_dom 1.0, freq_dom 0.77778, sym_dom 0.47677, TRANSITION_OP dom 1.0 "
                                  "parity 0.68485, trans_minus_shuf_dom 0.57778, clean_passers=['TRANSITION_OP'], "
                                  "BILINEAR_REF 0.4849. INT_MATCH refute=False. Cross-arc overlap lexical-only."),
            "honest_scope": ("Dominance SPECIALIST (not parity), SYNTHETIC, construction (learned M_i); merit vs FREQ "
                             "0.778 (+0.222), not vs chance. Never narrate as a real-language/biology capability."),
            "n_seeds": 5, "seeds": [7, 13, 17, 23, 29],
            "metrics": {"trans_dom": 1.0, "freq_dom": 0.77778, "sym_dom": 0.47677, "bilinear_ref_dom": 0.4849,
                        "trans_parity": 0.68485, "trans_minus_shuf_dom": 0.57778, "chance_dom": 0.62273},
            "composes_with": [ID_NONADD + " (parent: reasoning-core discovery)",
                              ID_BILIN + " (the negative TRANSITION_OP breaks: bilinear=parity-only)"],
            "cites": ["Fix_28_verify_off_data_not_verdict_msg",
                      "project_reasoning_mechanism_improve_additive_map_encoding_lever_break_bind_commutativity",
                      "feedback_construction_proof_is_not_a_capability_win"],
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE, "needs_orchestrator_store_sync": True,
        },
    },
    {
        "op": "cert_ruling", "corpus": "math", "tier": "CHAIN_GRADE",
        "cert_status": "confirmed_chain_grade_transition_op_dominance_specialist",
        "anchor": "interaction_asymmetric_directed_operators_v1", "cell_commit": "290400320",
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True, "auditor": "hdi_skunkworks",
        "atomized_by": ATOMIZED_BY,
        "verdict": "HARD_PASS_transition_op_reads_dominance_1p000_order_attributed_symmetric_and_bilinear_cannot",
        "cert_increment_delta": 1,
        "decision": ("CHAIN_GRADE. Non-commutative matrix-chain reads antisymmetric dominance 1.000 (5/5), clears FREQ "
                     "0.778 by +0.222, order-attributed (TRANS-SHUF 0.578), unique clean passer; SYM 0.477 + BILINEAR "
                     "0.485 provably cannot. Dominance specialist, synthetic, construction (learned M_i)."),
        "framing_correction_vs_director": ("Confirms Director's framing exactly; I only sharpen that merit is vs FREQ "
                                           "(0.778), NOT vs chance, and it is a SPECIALIST (parity 0.685 unsolved) -- "
                                           "the joint-capstone (this batch) is what fuses it with the parity specialist."),
        "cross_arc_overlap_check": "lexical-only; no prior cert atom >0.30; grep anchor=0.",
        "net_cert_delta": "+1 CHAIN_GRADE (asymmetric operator reads dominance; construction, synthetic).",
        "needs_orchestrator_store_sync": True,
    },
)

# --------------------------------------------------------------------------------------------------
# 3. JOINT OPERATOR CAPSTONE  (CHAIN_GRADE; zero-interference shared code)
# --------------------------------------------------------------------------------------------------
mk(
    {
        "id": ID_JOINT,
        "name": ("MATH CHAIN_GRADE (capstone): ONE shared code + TWO selective readouts solves BOTH parity (0.998) and "
                 "dominance (1.000) with ZERO measured interference (parity rel_drop vs specialist -0.006, dominance "
                 "rel_drop 0.000), beating the prior joint-dual MIDDLE (0.816/0.164); all 9 gates pass; M=I identity "
                 "EXACT. SCOPE: the win is ZERO-INTERFERENCE co-existence (it MATCHES, not beats, each specialist), "
                 "SYNTHETIC, construction; rank-R count discriminator SATURATED at R1 (untested here)."),
        "corpus": "math", "tier": "CHAIN_GRADE", "kind": "experiment_landed_vet",
        "cert_status": ("confirmed_chain_grade_joint_operator_capstone_one_shared_code_two_readouts_solves_parity_and_"
                        "dominance_zero_interference_all_9_gates_pass_matches_specialists"),
        "cert_class": "joint_shared_code_two_selective_readouts_zero_interference_parity_and_dominance_synthetic_construction",
        "description": (
            "Independent off-disk landed-VET (.venv; headline gates + per_seed regimes, Fix #28). Anchor "
            "joint_operator_capstone_selective_readouts_v1, commit e5ff86ca4, VET a23cfd71. PARITY (chance 0.518): "
            "JOINT_CONFIG 0.9980, SYM_SPEC 0.9919 (rel_drop -0.0061 -> no interference, joint is NOT worse than the "
            "specialist), HEADDISC_order_on_parity 0.4707 (the wrong readout is at chance -> selectivity). DOMINANCE "
            "(chance 0.623, freq 0.778): JOINT_ORDER 1.0000, TRANS_SPEC 1.0000 (rel_drop 0.0000), SHUF 0.4222 "
            "(attr_gap 0.5778), HEADDISC_config_on_dom 0.5152. Gates G1-G9 all True (par, dom, parity-interference, "
            "dom-interference, cfg-headdisc, ord-headdisc, attribution, must-fail, ceiling). RANK sweep: count R1=1.0 "
            "R8=1.0 (recover False -> the count task SATURATES at rank 1, so rank-recovery is untested/vacuous here); "
            "parity R1=0.9758 R8=0.9980. per_seed sigs: JOINT_CONFIG hash == SYM_RANKR_SPEC hash and JOINT_ORDER == "
            "TRANSITION_SPEC in-seed -> the shared code IS the identity M=I on the readout path. cardinality True. "
            "5 seeds [7,13,17,23,29].\n\n"
            "TIER: CHAIN_GRADE. A single shared code with two selective readouts co-solves a symmetric-nonadditive task "
            "(parity) and an antisymmetric task (dominance) with ZERO measured cross-task interference, improving on "
            "the prior joint-dual MIDDLE (0.816/0.164). HONEST SCOPE: the capability win is the ZERO-INTERFERENCE "
            "co-existence -- it MATCHES each specialist (parity 0.998~=SYM 0.992, dominance 1.0==TRANS 1.0), it does NOT "
            "beat them; M=I is exact (identity readout); SYNTHETIC; construction. The rank-R count discriminator is "
            "saturated at R1 and therefore not informative here. cert_increment_delta=1."
        ),
        "aliases": [
            "one shared code two selective readouts solves parity 0.998 and dominance 1.0 zero interference",
            "joint operator capstone beats prior joint-dual middle 0.816 0.164 all 9 gates pass",
            "M equals I identity exact shared code hash matches specialist readouts in seed",
            "win is zero interference matches specialists not beats rank-R count saturated at R1",
        ],
        "metadata": {
            "provenance_quality": "CHAIN_GRADE_recompute_off_headline_gates_per_seed_regimes_9_gates_pass",
            "anchor": "joint_operator_capstone_selective_readouts_v1", "cell_commit": "e5ff86ca4", "vet_id": "a23cfd71",
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_joint_operator_capstone_selective_readouts_v1/metrics.json",
            "verified_off_data": ("JOINT_CONFIG par 0.9980 vs SYM 0.9919 (rel_drop -0.0061), JOINT_ORDER dom 1.0 vs "
                                  "TRANS 1.0 (rel_drop 0.0), HEADDISC cross-readout ~chance (0.471/0.515), 9 gates True, "
                                  "rank count R1=R8=1.0 (recover False=saturated), in-seed sig hashes match (M=I)."),
            "honest_scope": ("Win = ZERO-INTERFERENCE co-existence (MATCHES specialists, does not beat). SYNTHETIC, "
                             "construction, M=I exact. rank-R count discriminator saturated at R1 -> untested."),
            "n_seeds": 5, "seeds": [7, 13, 17, 23, 29],
            "metrics": {"joint_config_parity": 0.9980, "sym_spec_parity": 0.9919, "parity_rel_drop": -0.0061,
                        "joint_order_dom": 1.0, "trans_spec_dom": 1.0, "dom_rel_drop": 0.0,
                        "headdisc_order_on_parity": 0.4707, "headdisc_config_on_dom": 0.5152,
                        "prior_joint_dual_middle": [0.816, 0.164], "rank_count_R1": 1.0, "rank_count_R8": 1.0},
            "composes_with": [
                ID_BILIN + " (parity-specialist wall)", ID_TRANS + " (dominance specialist)",
                ID_NONADD + " (reasoning-core parent)",
                "joint_dual_channel_readout_v1 (prior MIDDLE 0.816/0.164, superseded-in-capability by zero-interference; not a Store atom)",
            ],
            "cites": ["Fix_28_verify_off_data_not_verdict_msg", "feedback_construction_proof_is_not_a_capability_win",
                      "project_reasoning_mechanism_improve_additive_map_construction_proof"],
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE, "needs_orchestrator_store_sync": True,
        },
    },
    {
        "op": "cert_ruling", "corpus": "math", "tier": "CHAIN_GRADE",
        "cert_status": "confirmed_chain_grade_joint_capstone_zero_interference",
        "anchor": "joint_operator_capstone_selective_readouts_v1", "cell_commit": "e5ff86ca4",
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True, "auditor": "hdi_skunkworks",
        "atomized_by": ATOMIZED_BY,
        "verdict": "HARD_PASS_joint_capstone_solves_parity_0p998_and_dominance_1p000_zero_interference_9_gates",
        "cert_increment_delta": 1,
        "decision": ("CHAIN_GRADE. One shared code + two selective readouts co-solves parity 0.998 + dominance 1.0 with "
                     "zero measured interference (rel_drop -0.006 / 0.000), all 9 gates pass, M=I exact, beats prior "
                     "joint-dual MIDDLE 0.816/0.164."),
        "framing_correction_vs_director": ("Confirms Director's framing; I sharpen that the win is ZERO-INTERFERENCE "
                                           "co-existence (MATCHES each specialist, does not beat), and the rank-R count "
                                           "discriminator is SATURATED at R1 (recover False) so rank capacity is "
                                           "untested here -- do not read a rank-recovery claim into this cell."),
        "cross_arc_overlap_check": "lexical-only; no prior cert atom >0.30; grep anchor=0.",
        "net_cert_delta": "+1 CHAIN_GRADE (shared-code zero-interference dual operator; construction, synthetic).",
        "needs_orchestrator_store_sync": True,
    },
)

# --------------------------------------------------------------------------------------------------
# 4. BILINEAR WALL  (HF_STRUCTURAL_BOUND)
# --------------------------------------------------------------------------------------------------
mk(
    {
        "id": ID_BILIN,
        "name": ("MATH HF_STRUCTURAL_BOUND (the negative TRANSITION_OP breaks): a single learned product/bilinear "
                 "operator (rank 1-4, capacity ruled out) is ANOTHER PARITY SPECIALIST -- it matches SYM on parity "
                 "(hero R1 0.978) but CANNOT read dominance (hero R1 0.485 vs role-specialist 1.000 and FREQ 0.778); "
                 "more rank does not help (R4 dom 0.503). PROVEN BOUND: native product/bilinear bind is bounded to "
                 "COMMUTATIVE structure; asymmetric/dominance requires role-keying or a two-channel operator. SYNTHETIC."),
        "corpus": "math", "tier": "HF_STRUCTURAL_BOUND", "kind": "experiment_landed_vet",
        "cert_status": ("confirmed_hard_fail_structural_bound_single_bilinear_product_op_is_parity_specialist_only_"
                        "cannot_read_dominance_capacity_ruled_out_native_bind_bounded_commutative"),
        "cert_class": "single_learned_bilinear_product_operator_commutative_bound_cannot_read_antisymmetric_dominance_synthetic",
        "description": (
            "Independent off-disk landed-VET (.venv; gates + per-family, Fix #28). Anchor "
            "interaction_bilinear_wall_break_v1, commit 29b53e63b, VET adjacent-to a61d3a0e. PARITY (chance 0.518, "
            "symmetric): HERO_R1 0.9778, SYM 0.9919 (specialist), LADD 0.4040, FREQ 0.4788 (R1-SYM -0.0141, R1-LADD "
            "+0.5737) -> parity_ok True (bilinear DOES parity). DOMINANCE (chance 0.623, freq 0.778, antisymmetric): "
            "HERO_R1 0.4849, roleSpec 1.0000, SYM 0.4768 (R1-role -0.5151, R1-FREQ -0.2929) -> dom_ok False (bilinear "
            "CANNOT do dominance; ~chance). n_solved 1 (parity only). CAPACITY RULED OUT: rank4 par 0.9798 dom 0.5030 "
            "(R4-R1 dom +0.0182) -> adding rank does not recover dominance. AND2 int-add 0.0000, MULT int-add -0.0061 "
            "(genuine nonadditivity present, so the failure is not a lack of interaction signal). hero_mustfail_ok "
            "True, ceiling True, cardinality True. ADDleak arb_gap_BR1 -0.008, shuf_gap -0.105. verdict "
            "HARD_FAIL_BILINEAR_IS_ANOTHER_SPECIALIST_PARITY_ONLY. 5 seeds [7,13,17,23,29].\n\n"
            "TIER: HF_STRUCTURAL_BOUND (genuine, substantive negative -- NOT a test-design failure: the parity arm "
            "passes at ceiling so the operator and harness work; the failure is specifically on antisymmetric "
            "dominance, and capacity is ruled out by the rank sweep). PROVEN BOUND: a single native product/bilinear "
            "bind operator is bounded to COMMUTATIVE (symmetric) interaction structure; reading antisymmetric dominance "
            "requires role-keying or a two-channel/matrix-chain operator (which TRANSITION_OP supplies, and the "
            "joint-capstone fuses). REVIVAL: none needed -- this is the characterized wall the arc was built to map; "
            "any claim that a symmetric bind reads asymmetric relations is refuted here. cert_increment_delta=1 "
            "(proven boundary / honest negative)."
        ),
        "aliases": [
            "single learned bilinear product op is another parity specialist cannot read dominance",
            "bilinear hero R1 parity 0.978 dominance 0.485 vs role 1.0 capacity ruled out rank4 dom 0.503",
            "native product bind bounded to commutative asymmetric requires role-keying two-channel",
        ],
        "metadata": {
            "provenance_quality": "HF_STRUCTURAL_BOUND_recompute_off_gates_capacity_ruled_out_by_rank_sweep_parity_arm_passes",
            "anchor": "interaction_bilinear_wall_break_v1", "cell_commit": "29b53e63b",
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_interaction_bilinear_wall_break_v1/metrics.json",
            "hf_attribution": "HF_STRUCTURAL_BOUND (parity arm passes at ceiling -> harness/operator work; failure is specific to antisymmetric dominance; capacity ruled out by rank sweep)",
            "verified_off_data": ("PARITY HERO_R1 0.9778 (parity_ok True), DOMINANCE HERO_R1 0.4849 vs roleSpec 1.0 "
                                  "(dom_ok False), rank4 dom 0.5030 (R4-R1 +0.018 -> capacity ruled out), nonadditivity "
                                  "present (MULT int-add -0.006). n_solved=1. Cross-arc overlap lexical-only."),
            "honest_scope": "SYNTHETIC. The bound is on a single native product/bilinear bind; not a claim about all learnable operators (the arc's own role-keyed/matrix-chain operators break it).",
            "n_seeds": 5, "seeds": [7, 13, 17, 23, 29],
            "metrics": {"hero_r1_parity": 0.9778, "sym_parity": 0.9919, "hero_r1_dom": 0.4849, "role_spec_dom": 1.0,
                        "sym_dom": 0.4768, "freq_dom": 0.7778, "rank4_dom": 0.5030, "n_solved": 1, "chance_dom": 0.62},
            "revival_criteria": ["none_needed_characterized_wall; any_claim_symmetric_bind_reads_asymmetric_relations_refuted_here"],
            "composes_with": [ID_NONADD + " (parent: reasoning-core discovery)",
                              ID_TRANS + " (the fix: role-keyed matrix-chain breaks this wall)",
                              ID_JOINT + " (fuses the parity + dominance specialists)"],
            "cites": ["Fix_28_verify_off_data_not_verdict_msg", "symmetric_anti_negativity_verify_both_directions_USER",
                      "project_reasoning_mechanism_encoding_lever_break_bind_commutativity",
                      "auditor_HF_positive_control_must_clear_its_own_floor_first_2026-07-01"],
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE, "needs_orchestrator_store_sync": True,
        },
    },
    {
        "op": "cert_ruling", "corpus": "math", "tier": "HF_STRUCTURAL_BOUND",
        "cert_status": "confirmed_hf_structural_bound_bilinear_parity_specialist_only",
        "anchor": "interaction_bilinear_wall_break_v1", "cell_commit": "29b53e63b",
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True, "auditor": "hdi_skunkworks",
        "atomized_by": ATOMIZED_BY,
        "verdict": "HARD_FAIL_bilinear_is_another_parity_specialist_cannot_read_dominance_capacity_ruled_out",
        "cert_increment_delta": 1,
        "hf_attribution": "HF_STRUCTURAL_BOUND (not test-design: parity arm clears ceiling; dominance-specific failure; capacity ruled out by rank sweep)",
        "decision": ("HF_STRUCTURAL_BOUND. Single learned bilinear/product op does parity (R1 0.978, matches SYM) but "
                     "NOT dominance (R1 0.485 vs role 1.0, ~chance); rank1->4 does not help (dom 0.503). Native product "
                     "bind bounded to commutative; asymmetric requires role-keying/two-channel."),
        "framing_correction_vs_director": ("Confirms Director's framing; I verify HF is a SUBSTANTIVE structural "
                                           "negative (positive/parity control clears its own ceiling first per auditor "
                                           "discipline, capacity ruled out) -- NOT a test-design failure."),
        "cross_arc_overlap_check": "lexical-only; no prior cert atom >0.30; grep anchor=0.",
        "net_cert_delta": "+1 (proven BOUND / honest negative: bilinear bind is commutative-bounded, cannot read dominance).",
        "needs_orchestrator_store_sync": True,
    },
)

# --------------------------------------------------------------------------------------------------
# 5. NONADDITIVE DISCOVERY (reasoning-core; CHAIN_GRADE scoped)
# --------------------------------------------------------------------------------------------------
mk(
    {
        "id": ID_NONADD,
        "name": ("MATH CHAIN_GRADE (reasoning-core, scoped): a learned INTeraction operator reads BOTH symmetric-"
                 "nonadditive parity (INT 1.000 vs MONO 0.477, INT-MONO 0.523) AND antisymmetric-noncommutative "
                 "dominance (INT 1.000, roleBest 1.000, vs FREQ 0.778) -- structure that no additive/monadic/frequency "
                 "baseline can read (LADD 0.404, MONO 0.477). Genuine nonadditivity confirmed by MI margins (parity "
                 "joint MI 0.999 vs best-single 0.003; dominance 0.956 vs 0.338). Discriminators fire (symNONADD True, "
                 "NONCOMM True), controls clean, ceiling True. SYNTHETIC construction, 5 seeds. This is the ARC PARENT "
                 "the bilinear-wall / transition-op / joint-capstone decompose."),
        "corpus": "math", "tier": "CHAIN_GRADE", "kind": "experiment_landed_vet",
        "cert_status": ("confirmed_chain_grade_scoped_interaction_operator_reads_symmetric_nonadditive_parity_and_"
                        "antisymmetric_noncommutative_dominance_no_additive_baseline_can_mi_margins_genuine_controls_fire"),
        "cert_class": "interaction_operator_reads_nonadditive_and_noncommutative_structure_reasoning_core_synthetic_construction",
        "description": (
            "Independent off-disk landed-VET (.venv; gates + nonadditivity MI + per-family, Fix #28). Anchor "
            "interaction_nonadditive_discovery_v1 (full, 5 seeds [7,13,17,23,29], ts 2026-07-15T01:59Z). verdict "
            "A=HARD_PASS_A_INTERACTION_CONSTRUCTION_PROVEN, B=HARD_PASS_B_SYMMETRY_MATCHED_DISCOVERY_NONADDITIVE_AND_"
            "NONCOMMUTATIVE. PARITY (chance 0.518, symmetric): INT 1.0000, MONO 0.4768 (INT-MONO 0.5232), LSYM 0.9919, "
            "LADD 0.4040 (LSYM-LADD 0.5879), LINT 0.4081, MEMO 0.4768, FREQ 0.4788, ORACLE 1.0000. DOMINANCE (chance "
            "0.623, antisymmetric): INT 1.0000, roleBest 1.0000, FREQ 0.7778 (role-FREQ 0.2222), LSYM 0.4768 (sym_fails, "
            "role-LSYM 0.5232). NONADDITIVITY (MI margins, off-disk): PARITY joint 0.999 vs best_single 0.0031 (margin "
            "0.9959); DOMINANCE joint 0.9561 vs 0.338 (0.6181); MULT 1.7152 vs 0.5725; AND2 0.8322 vs 0.3241. gates: "
            "hard_pass_A True, a_parity/a_dom/a_mustfail/a_ceiling True, disc_symmetric_nonadditive True, "
            "disc_noncommutative True, symmetry_tension False, b_leak_ok True. AND2 int-add 0.0, MULT int-add 0.0 "
            "(interaction not additively decomposable). ADD control: MONO 0.9758 LADD 0.9192 INT 0.9939 (additive task "
            "solvable by additive baselines -> discriminator is telemetry-sensitive, not analytically pinned). "
            "add_control_leak small (arb_gap_INT -0.028).\n\n"
            "TIER: CHAIN_GRADE (scoped). Construction-proof that a single learned interaction operator reads both "
            "symmetric-nonadditive (parity) and antisymmetric-noncommutative (dominance) structure that additive/"
            "monadic/frequency baselines provably cannot, with genuine (MI-verified) nonadditivity and clean controls. "
            "HONEST SCOPE: SYNTHETIC arena; this is the reasoning-CORE construction proof, and the SAME operator here "
            "solving both is the general/expressive INT -- the sibling cells in this batch (bilinear-wall, "
            "transition-op) drill WHICH MINIMAL operator class each half needs (a single bilinear = parity only; a "
            "matrix-chain = dominance), and the joint-capstone shows one shared code can do both with zero "
            "interference. cert_increment_delta=1."
        ),
        "aliases": [
            "interaction operator reads nonadditive parity 1.0 and noncommutative dominance 1.0 no additive baseline can",
            "symmetry matched discovery nonadditive and noncommutative MI margin parity 0.996 dominance 0.618",
            "reasoning-core construction proof arc parent bilinear-wall transition-op joint-capstone decompose it",
        ],
        "metadata": {
            "provenance_quality": "CHAIN_GRADE_scoped_recompute_off_gates_and_MI_margins_controls_fire_telemetry_sensitive",
            "anchor": "interaction_nonadditive_discovery_v1", "cell_commit": "UNKNOWN_local_capture_needed",
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_interaction_nonadditive_discovery_v1/metrics.json",
            "verified_off_data": ("PARITY INT 1.0 vs MONO 0.477, DOMINANCE INT 1.0 vs FREQ 0.778; MI margins parity "
                                  "0.9959 dominance 0.6181; disc_symmetric_nonadditive + disc_noncommutative True; ADD "
                                  "control solvable by additive baseline (discriminator telemetry-sensitive). Cross-arc "
                                  "overlap: substrate_query lexical-only (CN_operative 0.342, noncombinative 0.329)."),
            "honest_scope": "SYNTHETIC. Reasoning-core CONSTRUCTION proof; the general INT solves both, siblings drill the minimal operator class. Never narrate as language/biology capability.",
            "n_seeds": 5, "seeds": [7, 13, 17, 23, 29],
            "metrics": {"parity_int": 1.0, "parity_mono": 0.4768, "parity_lsym": 0.9919, "parity_ladd": 0.4040,
                        "dom_int": 1.0, "dom_rolebest": 1.0, "dom_freq": 0.7778, "dom_lsym": 0.4768,
                        "mi_margin_parity": 0.9959, "mi_margin_dominance": 0.6181, "mult_int_add_gap": 0.0},
            "composes_with": [ID_BILIN + " (child: parity-only bilinear wall)",
                              ID_TRANS + " (child: dominance matrix-chain specialist)",
                              ID_JOINT + " (child: zero-interference fusion)"],
            "cites": ["Fix_28_verify_off_data_not_verdict_msg",
                      "feedback_discriminator_must_be_telemetry_sensitive_not_analytically_pinned",
                      "project_realworld_conjunctions_are_minority_regime (nonadditive structure is the prize)",
                      "project_reasoning_mechanism_improve_additive_map_construction_proof"],
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE, "needs_orchestrator_store_sync": True,
        },
    },
    {
        "op": "cert_ruling", "corpus": "math", "tier": "CHAIN_GRADE",
        "cert_status": "confirmed_chain_grade_scoped_nonadditive_discovery_reasoning_core",
        "anchor": "interaction_nonadditive_discovery_v1", "cell_commit": "UNKNOWN_local_capture_needed",
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True, "auditor": "hdi_skunkworks",
        "atomized_by": ATOMIZED_BY,
        "verdict": "HARD_PASS_A_construction_proven_HARD_PASS_B_symmetry_matched_discovery_nonadditive_and_noncommutative",
        "cert_increment_delta": 1,
        "decision": ("CHAIN_GRADE scoped. Learned INT operator reads symmetric-nonadditive parity (1.0 vs MONO 0.477) "
                     "AND antisymmetric-noncommutative dominance (1.0 vs FREQ 0.778) that additive baselines cannot; "
                     "MI margins genuine (0.996/0.618); controls fire; ADD-control telemetry-sensitive. Reasoning-core "
                     "construction proof, synthetic."),
        "framing_correction_vs_director": ("Confirms Director's 'CHAIN_GRADE scoped'; I add that the SAME expressive INT "
                                           "solves both here -- the MINIMAL-operator decomposition (bilinear=parity, "
                                           "matrix-chain=dominance) is the sibling cells' contribution, not this one's."),
        "cross_arc_overlap_check": "substrate_query lexical-only (CN_operative 0.342); no prior cert atom >0.30; grep anchor=0.",
        "net_cert_delta": "+1 CHAIN_GRADE (reasoning-core: interaction operator reads nonadditive + noncommutative structure; construction, synthetic).",
        "needs_orchestrator_store_sync": True,
    },
)

# --------------------------------------------------------------------------------------------------
# 6. INTERFERENCE AVOIDANCE (CHAIN_GRADE construction-proof / hedge)
# --------------------------------------------------------------------------------------------------
mk(
    {
        "id": ID_INTERF,
        "name": ("MATH CHAIN_GRADE (construction-proof / hedge): conjunctive/orthogonal storage beats BOTH additive "
                 "storage AND a frequency oracle for a single-driver-dominated attribute -- at M_HI=256 orth 1.000 vs "
                 "add 0.273 vs freq 0.654 (gap_orth_add 0.727, gap_orth_freq 0.346), add<freq True, crossover at M=48, "
                 "disjoint-control gap 0.000 (clean must-fail), 3/3 seeds. Establishes the pattern-separation hedge: "
                 "conjunctive coding is justified even for single-driver attributes (interference avoidance), not only "
                 "for genuine conjunctions. SYNTHETIC (N=4096)."),
        "corpus": "math", "tier": "CHAIN_GRADE", "kind": "experiment_landed_vet",
        "cert_status": ("confirmed_chain_grade_construction_conjunctive_orthogonal_storage_beats_additive_and_frequency_"
                        "single_driver_attribute_crossover_M48_disjoint_control_clean_pattern_separation_hedge_holds"),
        "cert_class": "conjunctive_orthogonal_vs_additive_storage_interference_avoidance_single_driver_pattern_separation_synthetic",
        "description": (
            "Independent off-disk landed-VET (.venv; recompute from per_seed units, Fix #28). Anchor "
            "interference_avoidance_conjunctive_vs_additive_v1 (full, N=4096, P=48, k=8, V=8, p_drv=0.6, seeds "
            "[7,13,19], n_units 48, cardinality_ok True). At shared M=256: orth_acc {1.0,1.0,1.0} -> 1.000; add_acc "
            "{0.26953,0.265625,0.28516} -> 0.273; freq_oracle {0.65234,0.69141,0.61719} -> 0.654. gap_orth_add 0.727, "
            "gap_orth_freq 0.346, add<freq True. CROSSOVER at M=48 (add drops to ~0.625 while orth stays 1.0, and "
            "keeps falling as M grows: add 0.49/0.35/0.27/0.24 at M=128/192/256/768 while orth stays 1.0). "
            "DISJOINT-CONTROL must-fail: at M=64/256/768 orth=add=1.0 -> gap_control 0.000 (when patterns are "
            "disjoint/uncorrelated there is NO advantage -> the advantage is specifically an interference/correlation "
            "effect, rho_add ~0.16 in shared vs ~0 in control). discriminator_survives_scale True, "
            "discriminator_reachability True. prior_work_check: substrate-KB top-1 cosine 0.3057 'proactive "
            "interference' (wordnet, not arc); prior arc cells (cortex_hippo 0.277, correlation-hurts 0.270) all <0.30 "
            "-> genuine new operationalization. 3/3 seeds pass.\n\n"
            "TIER: CHAIN_GRADE (construction-proof). Conjunctive/orthogonal storage provably beats additive storage AND "
            "a frequency oracle for a single-driver-dominated attribute, with a clean disjoint-control must-fail "
            "isolating the effect to correlation/interference. This is the pattern-separation HEDGE from the program: "
            "conjunctive coding is independently justified by interference avoidance, holding even for single-driver "
            "attributes (not only for genuine no-dominant-driver conjunctions). HONEST SCOPE: SYNTHETIC (N=4096, "
            "V=8 codewords, argmax decode); a construction proof on designed data, not a real-data capability win; the "
            "additive arm's collapse is the expected correlated-pattern capacity wall (Loewe 1998). cert_increment_"
            "delta=1."
        ),
        "aliases": [
            "conjunctive orthogonal storage beats additive and frequency for single-driver attribute interference avoidance",
            "at M 256 orth 1.000 add 0.273 freq 0.654 gap 0.727 crossover M48 disjoint control clean",
            "pattern separation hedge conjunctive coding justified even for single-driver attributes",
        ],
        "metadata": {
            "provenance_quality": "CHAIN_GRADE_construction_recompute_off_per_seed_units_disjoint_control_clean_isolates_correlation",
            "anchor": "interference_avoidance_conjunctive_vs_additive_v1", "cell_commit": "UNKNOWN_local_capture_needed",
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_interference_avoidance_conjunctive_vs_additive_v1/metrics.json",
            "verified_off_data": ("M=256 shared: orth mean 1.000, add mean 0.273, freq mean 0.654 (recomputed from "
                                  "per_seed units); disjoint-control M=64/256/768 orth=add=1.0 -> gap 0.000; rho_add "
                                  "~0.16 shared vs ~0 control; crossover M=48. 3/3 seeds. Cross-arc overlap: cell "
                                  "prior_work_check cosine 0.3057 wordnet (not arc), arc cells <0.30."),
            "honest_scope": "SYNTHETIC (N=4096, V=8 argmax). Construction-proof / hedge, not a real-data win. Additive collapse = expected correlated-pattern capacity wall.",
            "n_seeds": 3, "seeds": [7, 13, 19],
            "metrics": {"orth_M256": 1.000, "add_M256": 0.273, "freq_oracle_M256": 0.654, "gap_orth_add": 0.727,
                        "gap_orth_freq": 0.346, "crossover_M": 48, "disjoint_control_gap": 0.000,
                        "hp_gap_orth_add_bar": 0.30, "hp_control_max_bar": 0.10},
            "composes_with": [
                "reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval (operationalized here)",
                "project_realworld_conjunctions_are_minority_regime (the hedge: conjunctive coding holds even single-driver)",
                "hippocampal DG/CA3 pattern separation (Leutgeb 2007; conjunctive coding) -- brain reference",
            ],
            "cites": ["Fix_28_verify_off_data_not_verdict_msg",
                      "feedback_saturation_vacuous_smoke_discriminator_must_fire_at_scale",
                      "reference_correlation_hurts_associative_store_capacity",
                      "feedback_construction_proof_is_not_a_capability_win"],
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE, "needs_orchestrator_store_sync": True,
        },
    },
    {
        "op": "cert_ruling", "corpus": "math", "tier": "CHAIN_GRADE",
        "cert_status": "confirmed_chain_grade_construction_interference_avoidance_hedge_holds",
        "anchor": "interference_avoidance_conjunctive_vs_additive_v1", "cell_commit": "UNKNOWN_local_capture_needed",
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True, "auditor": "hdi_skunkworks",
        "atomized_by": ATOMIZED_BY,
        "verdict": "HARD_PASS_conjunctive_orthogonal_beats_additive_and_frequency_single_driver_disjoint_control_clean",
        "cert_increment_delta": 1,
        "decision": ("CHAIN_GRADE construction-proof. Conjunctive/orthogonal storage beats additive AND frequency for a "
                     "single-driver attribute (M=256 orth 1.0 / add 0.273 / freq 0.654), crossover M=48, disjoint "
                     "control gap 0.000 (isolates correlation), 3/3 seeds. Pattern-separation hedge holds."),
        "framing_correction_vs_director": ("Confirms Director's 'CHAIN_GRADE construction-proof'; I keep the scope "
                                           "SYNTHETIC and note the additive collapse is the expected correlated-pattern "
                                           "capacity wall -- the novel, load-bearing part is the disjoint-control "
                                           "isolating the effect to interference (gap 0.000)."),
        "cross_arc_overlap_check": "cell prior_work_check cosine 0.3057 wordnet (not arc); arc cells <0.30; grep anchor=0.",
        "net_cert_delta": "+1 CHAIN_GRADE (construction: conjunctive coding justified by interference avoidance even for single-driver attrs).",
        "needs_orchestrator_store_sync": True,
    },
)


# ==================================================================================================
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
    print("=== A5 atom-write: operator-arc + cross-module batch (2026-07-15) ===")
    print("ts_iso =", _iso)
    print("atoms to write:", len(atoms), " ledger rows:", len(ledgers))
    assert len(atoms) == 6 and len(ledgers) == 6, "expected 6+6"
    # id uniqueness within batch
    ids = [a["id"] for a in atoms]
    assert len(set(ids)) == 6, "duplicate ids in batch"
    # id uniqueness vs existing store
    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    dup = [i for i in ids if i in existing]
    if dup:
        print("ABORT: id already in store:", dup); sys.exit(1)
    print("id-uniqueness OK (6 new, none pre-existing)")

    print("Writing 6 atoms to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, atoms)
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 6:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 6 rows to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, ledgers)
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 6:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    print()
    print("=== A5 WRITE COMPLETE ===")
    for p in (MATH_ATOMS, CERT_LEDGER):
        with open(p, "rb") as f:
            n = f.read().count(b"\n")
        print("  %s: %d lines" % (p.name, n))
    print()
    print("CERT N delta: +5 CHAIN_GRADE + 1 HF_STRUCTURAL_BOUND (proven bound). No new META.")
    print("needs_orchestrator_store_sync = True")
    for a in atoms:
        print("  ", a["tier"], "::", a["id"][:80], "...")


if __name__ == "__main__":
    main()
