"""
A5-gated atomize: M1.9 SemanticParser FULL — main CG atom + META MM_TENTATIVE atom.

CELL: experiments/exp_substrate_semantic_parser_intent_slot_extraction_v1.py (ab4a06f56)
ANCHOR: substrate_semantic_parser_intent_slot_extraction_v1
METRICS: data/exp_substrate_semantic_parser_intent_slot_extraction_v1/metrics.json

OFF-DATA VERIFICATION (independent recompute via .venv-equivalent numeric check):
  ARM_SUBSTRATE_FULL intent = mean(0.915, 0.865, 0.915) = 0.898 (matches verdict)
  ARM_SUBSTRATE_FULL slot   = mean(1.000, 1.000, 1.000) = 1.000 (matches verdict)
  ARM_INTENT_ONLY intent    = mean(0.035, 0.015, 0.020) = 0.023 (Hebbian collapses)
  ARM_M16_ROUTER slot       = mean(0.030, 0.014, 0.019) = 0.021 (unbind LOAD-BEARING)
  ARM_SHUFFLED_ROLE_KEYS slot = mean(0.020, 0.013, 0.018) = 0.017 (role-key LOAD-BEARING)
  ARM_BASELINE_SYMBOLIC     = 1.000/1.000 (scoring rig OK; positive control PASS)

  cross-seed cv on ARM_SUBSTRATE_FULL intent: mean 0.898, std ~0.024, cv ~0.026 << 0.15 CG
  cross-seed cv on slot: 0.0 (all 1.000)
  cardinality_ok: n_observed = 15 = 5 arms x 3 seeds (expected)
  arms_differ_verified: true; per-seed digests distinct across all 5 arms per seed
  storage_strategy: sharded

RULING:
  Main atom: chain-grade. Cortex primitive M1.9 SemanticParser validated. Cross-seed
    tight (cv 0.026 intent, 0.0 slot); 3 independent ablations collapse to <0.03
    slot floor and <0.03 intent floor for Hebbian arm; positive control clears
    ceiling. Load-bearing mechanism confirmed: (a) unbind is required for slot
    (M16 router without unbind = 0.021); (b) role-key binding is required
    (shuffled cyclic-derangement role keys = 0.017); (c) intent leg cannot be
    Hebbian on compositional-bundle inputs (0.023 chance).

  META atom: MEASURED_MECHANISM_TENTATIVE. IntentClassifier (Hebbian CG on CharTrigram
    text at n=50 acc~0.75) DOES NOT TRANSFER to compositional-bundle inputs (intent_hd
    + K=5 role-slot bind noise). Diagnostic sweep across INTENT_WEIGHT {1,3,5,10}
    (seed 11): Hebbian flatlined chance 0.02 all weights; direct k_NN_lookup on
    codebook recovered 0.00 -> 0.16 -> 0.56 -> 1.00. Cell swapped intent leg to
    direct-cleanup on codebook (mechanism-symmetric to slot cleanup). Regime-
    mismatch caught during smoke iteration; documented in pre-reg AMENDMENT +
    cell docstring. Load-bearing regime characterization.

    NOT SUPERSEDING the prior IntentClassifier CG (which remains valid on
    CharTrigram-encoded text inputs at n=50). AMENDS with input-regime bound:
    Hebbian read-out is a linear-superposition summarizer over training examples;
    it assumes the input is a de-facto template that lands near a training-set
    centroid. Compositional-bundle inputs violate that assumption because the
    intent signal is buried under K=5 bound role-slot pairs (SNR ~ 1/sqrt(K+1)
    at fixed alpha). Direct k_NN_lookup is the mechanism-symmetric readout.

TIER RATIONALE FOR META (MM_TENTATIVE not CG):
  - single classifier (Hebbian); not tested across classifier family
  - single input regime pair (CharTrigram-text vs K=5 compositional-bundle)
  - transfer surface is under-sampled; the general claim
    "Hebbian classifiers are regime-narrow for compositional-bundle inputs"
    needs at least one more classifier-mechanism confirmation
  Expansion criteria:
    (a) confirm on Perceptron / softmax-linear on compositional-bundle inputs
    (b) confirm across K (K=3, K=8) that the collapse tracks SNR ~ 1/sqrt(K+1)
    (c) test compositional-bundle input on 2+ tasks (slot-fill, hierarchical)

CROSS-ARC OVERLAP CHECK (substrate-KB v2 query 2026-07-02):
  Query 1 "Hebbian classifier regime narrow compositional bundle input"
    top-1 cosine=0.281 -> Composition classification (prior K-ratio drills)
    NOT the same finding (input-regime mismatch vs K-ratio scaling)
  Query 2 "IntentClassifier Hebbian mechanism-symmetric cleanup codebook"
    top-1 cosine=0.301 -> Mechanism class (generic mech-class chunks)
    top-3 cosine=0.253 -> benchmark TASK-SHAPE must match mechanism OUTPUT-SHAPE
    RELATED but orthogonal: OUTPUT-SHAPE matching is the 2026-06-11 methodology
    rule; this atom is INPUT-REGIME matching (mechanism assumes input geometry).
  RULING: genuinely orthogonal; not a rediscovery. Adds INPUT-REGIME matching
    as a complementary methodology rule alongside the existing OUTPUT-SHAPE one.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_M1p9_semantic_parser_CG_and_META_MM_hebbian_regime_narrow_2026-07-02"
ATOMIZED_DATE = "2026-07-02"
CELL_COMMIT = "ab4a06f56"

# ============================================================================
# MAIN CG ATOM (math corpus) — M1.9 SemanticParser mechanism
# ============================================================================
atom_M1p9_CG = {
    "id": (
        "T3/EXP_substrate_semantic_parser_intent_slot_extraction_v1_3seed_CG_"
        "cortex_M1p9_intent_0p898_slot_1p000_ablation_M16_router_slot_0p021_"
        "shuffled_role_keys_slot_0p017_intent_only_hebbian_0p023_baseline_symbolic_"
        "1p000_positive_control_PASS_sharded_storage_arms_differ_verified_"
        "cross_seed_cv_intent_0p026_slot_0p0_direct_kNN_codebook_readout_"
        "on_both_intent_and_slot_K5_role_slot_compositional_bundle_2026-07-02"
    ),
    "name": (
        "M1.9 SemanticParser (cortex primitive) chain-grade: intent 0.898 (cv 0.026) + "
        "slot 1.000 (cv 0.0) on 3-seed FULL. Mechanism: K=5 role-slot compositional bind "
        "over sharded FHRR substrate with direct k_NN codebook cleanup on both intent and "
        "slot readouts. Three ablations collapse: M16 router (no unbind) slot 0.021; "
        "shuffled cyclic-derangement role keys slot 0.017; Hebbian intent-only 0.023. "
        "Positive control ARM_BASELINE_SYMBOLIC 1.000/1.000 clears ceiling; storage "
        "sharded; arms_differ_verified true; cardinality_ok 15/15 seed-arm combos."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "cortex_primitive_validated",
    "description": (
        "M1.9 SemanticParser Option-A cortex primitive validated on 3-seed FULL.\n"
        "\n"
        "REGIME: 50 intents; 5 roles (SUBJECT/OBJECT/ATTRIBUTE/TIME/LOCATION); 100 slot "
        "dict entries per role; N=8192 FHRR; n_train=500 n_test=200; seeds=[11,17,23].\n"
        "\n"
        "MECHANISM (ARM_SUBSTRATE_FULL):\n"
        "  1. encode utterance -> intent_hd via intent codebook\n"
        "  2. K=5 role-slot compositional bind: bundle over sum_i bind(role_i, slot_i)\n"
        "  3. direct k_NN cleanup on intent codebook (post-swap from Hebbian - see META)\n"
        "  4. per-role unbind + k_NN cleanup on slot codebook (mechanism-symmetric)\n"
        "\n"
        "OFF-DATA RESULTS (mean over seeds 11/17/23):\n"
        "  ARM_BASELINE_SYMBOLIC       intent=1.000 slot=1.000  (scoring rig OK; ceiling PC)\n"
        "  ARM_SUBSTRATE_FULL          intent=0.898 slot=1.000  (main claim; cv 0.026 / 0.0)\n"
        "  ARM_INTENT_ONLY (Hebbian)   intent=0.023 slot=0.009  (chance; regime-narrow -> META)\n"
        "  ARM_M16_ROUTER (no unbind)  intent=0.898 slot=0.021  (unbind LOAD-BEARING)\n"
        "  ARM_SHUFFLED_ROLE_KEYS      intent=0.898 slot=0.017  (role-key LOAD-BEARING)\n"
        "\n"
        "PER-SEED (ARM_SUBSTRATE_FULL):\n"
        "  seed 11: intent 0.915 slot 1.000\n"
        "  seed 17: intent 0.865 slot 1.000\n"
        "  seed 23: intent 0.915 slot 1.000\n"
        "  cv intent = 0.024/0.898 = 0.026 << 0.15 CG threshold\n"
        "  cv slot   = 0.0\n"
        "\n"
        "ABLATION DISCRIMINATION (all p<0.001 by binomial floor):\n"
        "  M16 router (no unbind) collapse: slot 1.000 -> 0.021  (Delta = 0.979)\n"
        "  shuffled cyclic-derangement role keys: slot 1.000 -> 0.017 (Delta = 0.983)\n"
        "  Hebbian IntentClassifier collapse: intent 0.898 -> 0.023 (Delta = 0.875)\n"
        "\n"
        "STORAGE: sharded (per-role slot codebook + intent codebook + role-key bank).\n"
        "ARMS_DIFFER_VERIFIED: true; per-seed mechanism-hash distinct across all 5 arms.\n"
        "CARDINALITY_OK: 15/15 (5 arms x 3 seeds).\n"
        "\n"
        "COMPOSITION: builds on Option-A cortex primitives; extends M1.6-M1.8 substrate "
        "primitives (codebook, bundling, sharded storage). See META atom for the "
        "regime-narrowness bound on IntentClassifier that motivated the swap to direct k_NN."
    ),
    "metadata": {
        "provenance_quality": "CHAIN_GRADE_3SEED_FULL",
        "verdict": "HARD_PASS",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute of metrics.json per-arm-per-seed: "
            "ARM_SUBSTRATE_FULL intent mean(0.915,0.865,0.915)=0.898 slot mean=1.000; "
            "ARM_INTENT_ONLY intent mean(0.035,0.015,0.020)=0.023; "
            "ARM_M16_ROUTER slot mean(0.030,0.014,0.019)=0.021; "
            "ARM_SHUFFLED_ROLE_KEYS slot mean(0.020,0.013,0.018)=0.017; "
            "ARM_BASELINE_SYMBOLIC 1.000/1.000; cardinality_ok=true; "
            "arms_differ_verified=true; per-seed digests all distinct across 5 arms; "
            "cross-seed cv intent=0.026 slot=0.0"
        ),
        "cell_commit": CELL_COMMIT,
        "cell_path": "experiments/exp_substrate_semantic_parser_intent_slot_extraction_v1.py",
        "prereg_path": "preregs/2026-07-02_substrate_semantic_parser_intent_slot_extraction_v1.md",
        "metrics_path": "data/exp_substrate_semantic_parser_intent_slot_extraction_v1/metrics.json",
        "anchor_name": "substrate_semantic_parser_intent_slot_extraction_v1",
        "run_mode": "full",
        "seeds": [11, 17, 23],
        "N_DIM": 8192,
        "N_INTENTS": 50,
        "N_ROLES": 5,
        "SLOT_DICT_SIZE_PER_ROLE": 100,
        "arms": {
            "ARM_BASELINE_SYMBOLIC":  {"intent_cross_seed_mean": 1.000, "slot_cross_seed_mean": 1.000},
            "ARM_SUBSTRATE_FULL":     {"intent_cross_seed_mean": 0.898, "slot_cross_seed_mean": 1.000},
            "ARM_INTENT_ONLY":        {"intent_cross_seed_mean": 0.023, "slot_cross_seed_mean": 0.009},
            "ARM_M16_ROUTER":         {"intent_cross_seed_mean": 0.898, "slot_cross_seed_mean": 0.021},
            "ARM_SHUFFLED_ROLE_KEYS": {"intent_cross_seed_mean": 0.898, "slot_cross_seed_mean": 0.017},
        },
        "cross_seed_cv": {"intent_ARM_SUBSTRATE_FULL": 0.026, "slot_ARM_SUBSTRATE_FULL": 0.0},
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "storage_strategy": "sharded",
        "load_bearing_mechanism_components": [
            "K5_role_slot_compositional_bind_over_bundle",
            "per_role_unbind_M16_router_ablation_collapses_slot_to_0p021",
            "role_key_binding_shuffled_role_keys_ablation_collapses_slot_to_0p017",
            "intent_leg_direct_kNN_codebook_readout_hebbian_ablation_collapses_to_0p023",
            "positive_control_symbolic_baseline_clears_1p000_1p000_ceiling",
        ],
        "cortex_M_slot": "M1.9",
        "cortex_option": "A_primitive",
        "cert_increment_delta": 1,
        "discipline_tags": [
            "chain_grade_3seed_FULL_cortex_primitive",
            "three_orthogonal_ablations_all_collapse",
            "positive_control_PASS_scoring_rig_OK",
            "cross_seed_cv_intent_0p026_slot_0p0_tight",
            "sharded_storage_strategy",
            "arms_differ_verified_all_15_digests_distinct",
            "cardinality_ok_15_of_15",
            "regime_narrow_hebbian_swap_documented_in_cell_and_prereg",
            "Fix_28_per_arm_metrics_verified",
            "stage_3_compositional_understanding_USER_2026-06-26",
            "M3_cortex_above_substrate_USER_2026-06-28",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

ledger_M1p9_CG = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{atom_M1p9_CG['id']}",
    "cert_status": "chain_grade",
    "cert_class": "cortex_primitive_M1p9_semantic_parser_intent_slot_extraction",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "CG_M1p9_semantic_parser_3seed_FULL_intent_0p898_cv_0p026_slot_1p000_cv_0p0_"
        "three_orthogonal_ablations_collapse_M16_router_no_unbind_slot_0p021_"
        "shuffled_cyclic_derangement_role_keys_slot_0p017_hebbian_intent_only_0p023_"
        "positive_control_symbolic_baseline_1p000_1p000_PASS_sharded_storage_"
        "arms_differ_verified_cardinality_ok_15_of_15"
    ),
    "cert_increment_delta": 1,
    "cv": {"intent": 0.026, "slot": 0.0},
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_semantic_parser_intent_slot_extraction_v1/metrics.json",
        "cell_path": "experiments/exp_substrate_semantic_parser_intent_slot_extraction_v1.py",
        "prereg_path": "preregs/2026-07-02_substrate_semantic_parser_intent_slot_extraction_v1.md",
        "atom_qualified_id": f"math::{atom_M1p9_CG['id']}",
    },
    "supersedes": None,
    "note": (
        "M1p9_cortex_primitive_SemanticParser_CG_3seed_FULL_intent_slot_extraction_"
        "K5_role_slot_compositional_bind_direct_kNN_codebook_readout_"
        "three_ablations_all_collapse_cross_seed_cv_tight_"
        "META_hebbian_regime_narrow_atom_paired_MM_TENTATIVE_landed_same_batch"
    ),
}

# ============================================================================
# META ATOM (meta corpus) — MM_TENTATIVE Hebbian regime-narrowness on
# compositional-bundle inputs
# ============================================================================
atom_META_hebbian_regime_narrow = {
    "id": (
        "META_hebbian_classifier_regime_narrow_for_compositional_bundle_inputs_"
        "MM_TENTATIVE_input_regime_mismatch_load_bearing_"
        "IntentClassifier_CG_on_chartrigram_text_n50_acc_0p754_does_NOT_transfer_"
        "to_K5_role_slot_bind_bundle_inputs_diagnostic_sweep_INTENT_WEIGHT_1_3_5_10_"
        "hebbian_flatlined_0p02_all_weights_direct_kNN_recovered_0p00_0p16_0p56_1p00_"
        "cell_swapped_intent_leg_to_direct_kNN_cleanup_mechanism_symmetric_to_slot_"
        "expansion_criteria_perceptron_softmax_across_K_multi_task_2026-07-02"
    ),
    "name": (
        "MM_TENTATIVE META rule: Hebbian classifiers are input-regime-narrow. A Hebbian "
        "IntentClassifier that hits chain-grade on CharTrigram-encoded text (n=50 acc "
        "~0.75) DOES NOT transfer to compositional-bundle inputs (K=5 role-slot bind "
        "over bundle) - flatlines at chance 0.02 across INTENT_WEIGHT sweep {1,3,5,10}. "
        "Direct k_NN codebook lookup (mechanism-symmetric to slot cleanup) recovers "
        "0.00 -> 0.16 -> 0.56 -> 1.00 across the same sweep. Rule: match READOUT to "
        "INPUT REGIME, not just OUTPUT SHAPE. Complements the 2026-06-11 "
        "'benchmark TASK-SHAPE must match mechanism OUTPUT-SHAPE' rule with an "
        "input-side variant. TENTATIVE per single-classifier single-task test surface."
    ),
    "corpus": "meta",
    "tier": "T3",
    "kind": "methodology_rule_input_regime_matching",
    "description": (
        "MECHANISM-LEVEL DIAGNOSIS:\n"
        "\n"
        "A Hebbian classifier computes a weight matrix W = sum_i y_i x_i^T from training\n"
        "pairs (x_i, y_i), then predicts via argmax(W x_test). This is a linear\n"
        "superposition summarizer over training examples. It assumes x_test lands near a\n"
        "training-set centroid; equivalently, class centroids in x-space are far apart\n"
        "relative to intra-class variance.\n"
        "\n"
        "On CharTrigram-encoded text (fixed vocabulary, small n=50 intents), utterances\n"
        "within an intent share strong lexical structure so intent-conditional centroids\n"
        "in x-space are well-separated. Hebbian read-out works (prior CG at acc ~0.75).\n"
        "\n"
        "On compositional-bundle inputs (utterance encoded as intent_hd + sum_k bind(role_k,\n"
        "slot_k)) the intent-bearing signal is submerged under K=5 bound role-slot pairs.\n"
        "The intent signal has SNR ~ 1 / sqrt(K + 1) at unit-norm alpha, so the Hebbian\n"
        "linear-superposition read-out collects near-zero signal above the K-slot noise\n"
        "floor.\n"
        "\n"
        "EVIDENCE (diagnostic sweep, seed 11, INTENT_WEIGHT amplification):\n"
        "  INTENT_WEIGHT=1:  Hebbian 0.02  direct k_NN 0.00\n"
        "  INTENT_WEIGHT=3:  Hebbian 0.02  direct k_NN 0.16\n"
        "  INTENT_WEIGHT=5:  Hebbian 0.02  direct k_NN 0.56\n"
        "  INTENT_WEIGHT=10: Hebbian 0.02  direct k_NN 1.00\n"
        "  Hebbian FLATLINES; direct k_NN monotonic in amplification.\n"
        "\n"
        "FULL-RUN CONFIRMATION (3-seed, ARM_INTENT_ONLY Hebbian):\n"
        "  seed 11: intent 0.035; seed 17: intent 0.015; seed 23: intent 0.020; mean 0.023\n"
        "  (chance 0.02 for 50-way classification confirms flatline)\n"
        "\n"
        "SWAP: cell swapped intent leg from Hebbian IntentClassifier to direct k_NN\n"
        "codebook cleanup (mechanism-symmetric to slot cleanup: unbind or read out\n"
        "intent_hd component, then k_NN against intent codebook). Result: ARM_SUBSTRATE_FULL\n"
        "intent 0.898 across 3 seeds.\n"
        "\n"
        "META RULE (this atom): the readout mechanism must match INPUT REGIME (input\n"
        "geometry), not merely OUTPUT SHAPE (task family). A Hebbian classifier is\n"
        "appropriate when the input geometry places class centroids far apart in the\n"
        "input space; it fails when the input is a compositional bundle where the\n"
        "class-carrying signal is submerged under a K-way superposition. Prefer direct\n"
        "codebook k_NN (or mechanism-symmetric unbind-and-clean) when the input is\n"
        "compositional-bundle-shaped.\n"
        "\n"
        "COMPLEMENTS the 2026-06-11 methodology rule 'benchmark TASK-SHAPE must match\n"
        "mechanism OUTPUT-SHAPE' - that rule constrains what you TEST the mechanism on;\n"
        "this rule constrains what INPUT REGIME the mechanism is EXPECTED to handle.\n"
        "\n"
        "TIER: MM_TENTATIVE. Single classifier (Hebbian), single input-regime pair\n"
        "(CharTrigram-text vs K=5 compositional-bundle). Load-bearing regime-mismatch\n"
        "characterization is REAL and REPRODUCED (3-seed FULL confirms diagnostic\n"
        "sweep) but the general claim needs more classifier-mechanism confirmations.\n"
        "\n"
        "EXPANSION CRITERIA (elevates MM_TENTATIVE toward MM_STANDARD then CG-eligible):\n"
        "  (a) confirm same failure on Perceptron / softmax-linear on compositional\n"
        "      bundle inputs\n"
        "  (b) confirm scaling: collapse tracks K-value across K in {2, 3, 5, 8}\n"
        "      predicted by SNR ~ 1/sqrt(K+1)\n"
        "  (c) confirm on 2+ tasks beyond intent classification\n"
        "\n"
        "DOES NOT SUPERSEDE prior IntentClassifier CG atom. That atom remains valid\n"
        "on CharTrigram-encoded text at n=50. This atom AMENDS with input-regime bound."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM_TENTATIVE",
        "verdict": "MEASURED_MECHANISM_TENTATIVE",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "ARM_INTENT_ONLY (Hebbian on compositional-bundle input) 3-seed FULL: "
            "intent mean(0.035,0.015,0.020)=0.023 (chance 0.02 for 50-way); slot mean=0.009. "
            "Diagnostic sweep seed 11 INTENT_WEIGHT {1,3,5,10}: Hebbian flatline 0.02 all; "
            "direct k_NN monotonic 0.00,0.16,0.56,1.00. ARM_SUBSTRATE_FULL post-swap to "
            "direct k_NN intent = 0.898 3-seed."
        ),
        "cell_commit": CELL_COMMIT,
        "cell_path": "experiments/exp_substrate_semantic_parser_intent_slot_extraction_v1.py",
        "prereg_amendment_path": "preregs/2026-07-02_substrate_semantic_parser_intent_slot_extraction_v1.md",
        "diagnostic_sweep": {
            "seed": 11,
            "INTENT_WEIGHT_values": [1, 3, 5, 10],
            "Hebbian_acc": [0.02, 0.02, 0.02, 0.02],
            "direct_kNN_acc": [0.00, 0.16, 0.56, 1.00],
            "conclusion": "Hebbian flatline; direct k_NN monotonic - mechanism-swap indicated",
        },
        "composes_atoms": [
            {
                "atom_id_prefix": "T3/EXP_substrate_semantic_parser_intent_slot_extraction_v1_3seed_CG",
                "commit": CELL_COMMIT,
                "role": "evidence_source_ARM_INTENT_ONLY_and_ARM_SUBSTRATE_FULL",
            },
        ],
        "complements_prior_meta_rule": {
            "rule_id": "methodology_benchmark_must_break_symmetry_OUTPUT_SHAPE_2026-06-11",
            "relationship": "input_regime_matching_side_of_the_same_general_principle",
        },
        "does_not_supersede": [
            "IntentClassifier_CG_on_CharTrigram_text_n50_acc_0p754",
        ],
        "expansion_criteria_for_MM_STANDARD_and_CG_eligibility": {
            "(a)_confirm_on_perceptron_or_softmax_linear": {
                "elevates_to": "MM_STANDARD_when_met",
            },
            "(b)_confirm_K_scaling_SNR_1_over_sqrt_K_plus_1": {
                "K_values_to_test": [2, 3, 5, 8],
                "elevates_to": "MM_STANDARD_when_met",
            },
            "(c)_confirm_on_2plus_tasks_beyond_intent": {
                "elevates_to": "CG_eligibility_with_pre_reg_when_met",
            },
        },
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_input_regime_matching_readout_to_input_geometry",
            "complements_2026-06-11_OUTPUT_SHAPE_rule",
            "MM_TENTATIVE_single_classifier_single_input_regime_pair_narrow_surface",
            "load_bearing_regime_mismatch_caught_in_smoke_iteration",
            "documented_in_cell_docstring_and_prereg_amendment",
            "mechanism_symmetric_readout_intent_and_slot_both_direct_kNN_codebook",
            "cortex_M1p9_evidence_source_ARM_INTENT_ONLY_and_ARM_SUBSTRATE_FULL",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

ledger_META_hebbian = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"meta::{atom_META_hebbian_regime_narrow['id']}",
    "cert_status": "measured_mechanism_tentative",
    "cert_class": "methodology_rule_input_regime_matching",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "MM_TENTATIVE_META_hebbian_classifier_regime_narrow_for_compositional_bundle_inputs_"
        "IntentClassifier_CG_on_chartrigram_text_n50_does_NOT_transfer_to_K5_role_slot_bind_"
        "hebbian_flatlines_0p02_diagnostic_sweep_intent_weight_1_3_5_10_direct_kNN_recovers_"
        "0p00_0p16_0p56_1p00_cell_swapped_intent_leg_to_direct_kNN_codebook_cleanup_"
        "mechanism_symmetric_to_slot_cleanup_complements_2026-06-11_OUTPUT_SHAPE_rule_"
        "with_INPUT_REGIME_side_expansion_perceptron_K_scaling_multi_task_needed"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_semantic_parser_intent_slot_extraction_v1/metrics.json",
        "cell_path": "experiments/exp_substrate_semantic_parser_intent_slot_extraction_v1.py",
        "prereg_path": "preregs/2026-07-02_substrate_semantic_parser_intent_slot_extraction_v1.md",
        "atom_qualified_id": f"meta::{atom_META_hebbian_regime_narrow['id']}",
        "composes_atoms_referents": [
            f"math::{atom_M1p9_CG['id']} (same-batch landed CG cortex primitive)",
        ],
    },
    "supersedes": None,
    "note": (
        "META_input_regime_matching_rule_MM_TENTATIVE_load_bearing_regime_mismatch_"
        "caught_in_M1p9_smoke_iteration_paired_with_same_batch_M1p9_CG_atom_"
        "complements_2026-06-11_OUTPUT_SHAPE_rule_with_INPUT_REGIME_side"
    ),
}

# ============================================================================
# A5 write protocol
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists()

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row: assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row: assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text); f.flush(); os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try: os.replace(str(tmp_path), str(path)); break
        except PermissionError:
            if _attempt == 9: raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row: assert tail["id"] == new_row["id"]
    if "atom_id" in new_row: assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_M1p9_CG,                        "math/atoms (M1.9 SemanticParser CG cortex primitive)")
    append_jsonl_a5(META_ATOMS, atom_META_hebbian_regime_narrow,     "meta/atoms (META hebbian regime-narrow MM_TENTATIVE)")
    append_jsonl_a5(CERT_LEDGER, ledger_M1p9_CG,                     "cert_ledger (M1.9 CG)")
    append_jsonl_a5(CERT_LEDGER, ledger_META_hebbian,                "cert_ledger (META MM_TENTATIVE)")
    print(f"[A5] DONE OK")
    print(f"[A5] M1.9 SemanticParser CG (+1 CG); META hebbian regime-narrow MM_TENTATIVE (+0)")
    print(f"[A5] Cell commit: {CELL_COMMIT}")


if __name__ == "__main__":
    main()
