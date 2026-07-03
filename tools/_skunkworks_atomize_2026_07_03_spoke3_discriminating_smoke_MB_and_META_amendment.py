"""
A5-gated atomization for landed VET of
exp_substrate_spoke3_hippocampal_encoder_episodic_binding_discriminating_smoke_2026_07_03.

Skunkworks landed-VET off-disk per Fix#28.

VERIFIED-OFF-DISK numbers (data/exp_substrate_spoke3_hippocampal_encoder_episodic_binding_discriminating_smoke_2026_07_03/metrics.json):
  ARM_HIPPOCAMPAL_N500_ADV_90CORRUPT:  per-seed [0.720, 0.720, 0.718]  mean 0.7193  std 0.00094  cv 0.13%
  ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_90: per-seed [0.742, 0.736, 0.726]  mean 0.7347  std 0.00660  cv 0.90%
  ARM_COSINE_BASELINE_N500_ADV_90:     per-seed [1.000, 1.000, 1.000]  mean 1.0000  std 0.0000
  ARM_HIPPOCAMPAL_N500_ADV_75CORRUPT:  per-seed [0.974, 0.986, 0.974]  mean 0.9780  std 0.0057
  ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_75: per-seed [0.982, 0.994, 0.988]  mean 0.9880  std 0.0049
  ARM_HIPPOCAMPAL_N800_ADV_75CORRUPT:  per-seed [0.9675, 0.98125, 0.9775]  mean 0.9754  std 0.0058
  ARM_COSINE_BASELINE_N500_ADV_75:     1.0000 all seeds
  ARM_COSINE_BASELINE_N800_ADV_75:     1.0000 all seeds
  ARM_REGRESSION_HIPPOCAMPAL_N50_RANDOM_50: 1.0000 all seeds (bit-identical to predecessor commit 96d9055e5)
  ARM_REGRESSION_HIPPOCAMPAL_DG_ONLY_N50:   1.0000 all seeds
  ARM_REGRESSION_COSINE_BASELINE_N50:       1.0000 all seeds
  ARM_RANDOM_BASELINE_N500: per-seed [0.006, 0.000, 0.002] mean 0.00267 (chance 0.002; band 0.01 -- IN-BAND)
  cardinality_ok=true; arms_differ_verified=true; positive_control (regression) PASSES.

SNR MATH CROSS-CHECK (cell-author-derived, verified off-disk):
  For cosine baseline at 90% cue-zeroing at n_dim=2048:
    target signal cos(query, correct) = sqrt(0.10) = 0.31623
    metrics.json ARM_COSINE_BASELINE_N500_ADV_90 intra_pair_cos_mean = 0.31638 (matches within 0.0005)
    adversarial cluster cos = 0.64
    distractor bound cos(query, wrong-cluster-neighbor) = 0.64 * 0.316 = 0.2025
    signal 0.316 > distractor 0.2025 by 0.114 -> cosine argmax always wins deterministically
  CONFIRMS: regime is INSUFFICIENT to force baseline degradation. Discriminator did NOT FIRE.

HP JUDGMENTS (verified):
  HP1 (mechanism holds under load, threshold r1 >= 0.70): 0.7193 >= 0.70 --> CLEARED
  HP2 (mechanism > baseline separation, threshold sep >= 0.20): -0.2807 < 0.20 --> FAILED

CELL-AUTHOR SELF-CORRECTION (verified in cell interpretation section):
  verdict_msg emitted "HARD_FAIL_NO_MECHANISM_SEPARATION" + "task-class-mismatch hypothesis REFUTED".
  Cell-author's in-cell interpretation section explicitly refuses the REFUTED framing, showing
  post-hoc SNR math proving baseline saturation was baked in by parameter choice.
  This is a LEGITIMATE self-correction adjacent to META_RULE_AG (substrate-too-robust-for-default-
  regime); the discriminator did not fire, so mechanism-loses claim is regime-conditional not
  fundamental.

CA3 CONTRIBUTION SYMMETRIC-VERIFY (cell-author framed as "adds NEARLY ZERO"; auditor sharpens):
  At 90% cue-zero: DG_ONLY 0.7347 vs HIPPO (DG+CA3) 0.7193 --> CA3 contribution = -0.0154 (SLIGHTLY NEGATIVE)
  At 75% cue-zero: DG_ONLY 0.9880 vs HIPPO (DG+CA3) 0.9780 --> CA3 contribution = -0.0100 (SLIGHTLY NEGATIVE)
  Cell-author frame "CA3 adds ~zero" is directionally right but slightly softening: CA3 in fact
  MILDLY HURTS in both adversarial regimes tested. Not a zero-contribution finding; a mild-anti-
  contribution finding. Architecturally: DG expansion at 40x (2048->8192) with 2%-sparsity already
  saturates the separability lever; CA3 pattern-completion overshoots because DG output is already
  near-fully-sparse before CA3 gets to fill in.

CROSS-ARC PRECEDENT CHECK (grep meta atoms.jsonl):
  META_RULE_AG (2026-06-27; substrate-too-robust-for-default-regime, witness Cycle 1 v3+v4):
    same class as this landing -- baseline saturates leaving no headroom.
  META_RULE_AI (2026-06-27; RAIL_SANITY_BREACH means substrate-exceeds-prediction).
  This Spoke 3 landing is the 3rd witness for the "discriminator-didn't-fire regime" class.
  Note: the *substrate* is not too-robust here; the *baseline* is. But the enforcement lesson
  is identical: cosine baseline saturates the discriminating band [0.30, 0.70], mechanism
  comparison is uninformative in this regime.

TIER DISPOSITION:
  Overall: MIDDLE_BAND (MEASURED_MECHANISM) for the OVERALL cell. HP1 CLEARED clean; HP2
    FAILED but only because baseline saturated (regime-insufficient). Cell-author correctly
    refuses the verdict_msg's REFUTED framing.
  ATOMS FILED:
    (a) MATH CG_MEASURED_BOUND: episodic binding at 48% TF-capacity + adversarial cluster cos=0.64
        + 90% cue-zeroing holds r1=0.7193 (cv 0.13%). Mechanism performs its designed task under
        load. Distinct from prior 4.8% TF-capacity existence proof.
    (b) MATH CG_HONEST_NEGATIVE architectural: DG expansion is anti-signal at extreme sparse cue;
        CA3 contribution MILDLY NEGATIVE (not zero) in both 75% and 90% adversarial regimes.
    (c) META DISCIPLINE promotion: 2nd witness of cell-author-self-corrects-own-verdict-msg-
        overclaim (composes with prior TF-formula-in-code witness). Promotes to MM_STANDARD 2
        witnesses (cell-author-quality discipline propagation).
    (d) META AMENDMENT: parent MM_TENTATIVE_SYNTHESIS_4_witnesses substrate-native-loses-to-
        char-trigram promotion_criterion refined to TWO-GATE structure with deterministic
        promotion rules at Gate 1 landing.

DIRECTOR OVER-CLAIM MITIGATION:
  Director framed as "HP1 CLEARED and NOTABLE substantive new finding". Auditor cross-check:
  HP1 CLEARED at cv 0.13% is genuine CG for MEASURED BOUND (mechanism holds under load), NOT
  CG for "mechanism beats baseline" -- that's the demarcation. Cell-author already respects
  this. Symmetric-verify on Director's "CA3 contribution ~zero" catches slight sharpening
  needed: CA3 mildly HURTS, not zero.

Four atoms filed with matching TS_ISO on ledger.
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
COMMIT = "1d8b0ec44"
CELL_ANCHOR = "substrate_spoke3_hippocampal_encoder_episodic_binding_discriminating_smoke_2026_07_03"
METRICS_PATH = f"data/exp_{CELL_ANCHOR}/metrics.json"
CELL_PATH = f"experiments/exp_{CELL_ANCHOR}.py"


# ============= ATOM (a): MATH CG_MEASURED_BOUND on hippocampal episodic binding under load =============
atom_a_cg_bound = {
    "id": "math::T1/MATH_SPOKE3_HIPPOCAMPAL_EPISODIC_BINDING_CG_MEASURED_BOUND_at_48pct_TF_CAPACITY_N500_adversarial_cluster_cos_0p64_90pct_cue_zero_r1_0p7193_std_0p00094_cv_0p13pct_3_seeds_11_17_23_HP1_threshold_0p70_CLEARED_at_load_10x_prior_existence_proof_4p8pct_N50_1p000_this_landing_extends_capacity_load_curve_from_4p8pct_to_48pct_via_adversarial_correlated_fillers_cluster_size_5_stress_test_of_pattern_separation_lever_baseline_saturates_at_1p000_so_this_is_NOT_a_mechanism_beats_baseline_claim_but_a_mechanism_holds_at_load_claim_at_extreme_corruption_75pct_regime_r1_0p9780_cv_0p006_N800_75pct_r1_0p9754_cv_0p006_all_three_load_bearing_arms_land_above_HP1_0p70_floor_regression_arms_bit_identical_to_predecessor_96d9055e5_code_integrity_verified_composes_prior_MATH_SPOKE3_HIPPOCAMPAL_EPISODIC_BINDING_SMOKE_EXISTENCE_PROOF_r1_1p000_N50_TFload_4p8pct_2026_07_03",
    "name": "MATH Spoke3 hippocampal EPISODIC BINDING CG_MEASURED_BOUND at 48% TF-capacity + 90% cue-zero + adversarial (r1=0.7193 cv 0.13%; HP1 cleared)",
    "corpus": "math",
    "tier": "T1",
    "kind": "experiment_record",
    "description": (
        "CG_MEASURED_BOUND on hippocampal-encoder episodic binding under stress. "
        "Independent recompute off-disk (metrics.json commit 1d8b0ec44): "
        "ARM_HIPPOCAMPAL_N500_ADVERSARIAL_90CORRUPT r@1 per-seed [0.720, 0.720, 0.718] "
        "mean 0.7193 std 0.00094 cv 0.13% (extremely tight); ARM_HIPPOCAMPAL_N500_ADVERSARIAL_75CORRUPT "
        "r@1 mean 0.9780 cv 0.006; ARM_HIPPOCAMPAL_N800_ADVERSARIAL_75CORRUPT r@1 mean 0.9754 cv 0.006. "
        "Regime: n_dim=2048, dg_dim=8192, dg_sparsity_target=0.02, TF capacity theoretical=1047 patterns, "
        "N=500 gives load_fraction=0.4775 (48% of TF capacity), cluster_size=5, adversarial_flip_frac=0.10 "
        "(cluster cosine ~0.64), partial_cue_fraction_zeroed=0.90. HP1 threshold r1>=0.70 CLEARED. "
        "Regression arms (N=50 random codebook 50% cue-zero) bit-identical to predecessor commit "
        "96d9055e5 (query digests match across regressions), so code integrity is verified. "
        "CARDINALITY: expected_n_units=actual_n_units=36 (12 arms x 3 seeds), cardinality_ok=true, "
        "arms_differ_verified=true, positive_control (regression arms) PASSES with r1=1.000 std 0.0 "
        "across seeds. Baseline-in-band check: ARM_RANDOM_BASELINE_N500 mean r1=0.00267 (chance 0.002, "
        "band 0.01) IN-BAND. "
        "IMPORTANT SCOPE: this is a MEASURED_BOUND on 'mechanism performs episodic binding under "
        "capacity+adversarial+extreme-corruption stress', NOT a 'mechanism beats cosine baseline' claim. "
        "Cosine baseline saturates at r1=1.000 in all three adversarial regimes because at "
        "n_dim=2048 with adversarial cluster cos=0.64 and 90% cue-zeroing, cosine argmax has margin: "
        "target signal cos = sqrt(0.10) = 0.3162 (matches metrics.json cosine intra_pair_cos_mean "
        "0.3164 within 0.0005); distractor bound = 0.64 * 0.3162 = 0.2025; deterministic 0.114 "
        "margin means cosine argmax wins. This DOES NOT refute mechanism value; it means regime is "
        "insufficient to force baseline degradation (META_RULE_AG-adjacent; discriminator did NOT "
        "fire). SEE COMPOSED ATOM META_TASK_CLASS_MISMATCH_HIPPOCAMPAL_MECHANISM_MM_STANDARD_2_WITNESS "
        "for the scope-refinement diagnostic. "
        "COMPOSES WITH: prior MATH_SPOKE3_HIPPOCAMPAL_EPISODIC_BINDING_SMOKE_EXISTENCE_PROOF_r1_1p000_"
        "N50_TFload_4p8pct_2026_07_03 (existence proof at 4.8% load); this atom extends the capacity "
        "curve to 48% load with adversarial stress. EXPANSION CRITERION: a future regime where "
        "baseline drops out of ceiling (>=95% cue-zero OR reduced n_dim OR cluster cos >=0.90) that "
        "still holds mechanism r1 >= 0.60 would upgrade this atom to CG_MECHANISM_BEATS_BASELINE."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment",
        "term_class": "SPOKE3_HIPPOCAMPAL_EPISODIC_BINDING_CAPACITY_STRESS_MEASURED_BOUND",
        "cert_status": "chain_grade_measured_bound",
        "cert_class": "CG_MEASURED_BOUND_mechanism_holds_under_load_not_beats_baseline",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_spoke3_discriminating_smoke",
        "raw_metrics_path": METRICS_PATH,
        "cell_source_path": CELL_PATH,
        "commit_hash": COMMIT,
        "cell_sha": None,
        "cell_anchor": CELL_ANCHOR,
        "n_seeds": 3,
        "seeds": [11, 17, 23],
        "n_dim": 2048,
        "dg_dim": 8192,
        "dg_sparsity_target": 0.02,
        "tf_capacity_theoretical": 1047.0286,
        "load_fraction_N500": 0.4775,
        "cluster_size": 5,
        "adversarial_flip_frac": 0.10,
        "adversarial_cluster_cos_approx": 0.64,
        "hp1_threshold_r1": 0.70,
        "hp1_verdict": "CLEARED_0p7193_gte_0p70",
        "hp2_threshold_sep": 0.20,
        "hp2_verdict": "FAILED_sep_neg_0p2807_because_baseline_saturates_at_1p000_regime_insufficient",
        "key_per_arm_r1_means": {
            "ARM_HIPPOCAMPAL_N500_ADV_90CORRUPT": 0.7193,
            "ARM_HIPPOCAMPAL_N500_ADV_75CORRUPT": 0.9780,
            "ARM_HIPPOCAMPAL_N800_ADV_75CORRUPT": 0.9754,
            "ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_90CORRUPT": 0.7347,
            "ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_75CORRUPT": 0.9880,
            "ARM_COSINE_BASELINE_N500_ADV_90CORRUPT": 1.0000,
            "ARM_COSINE_BASELINE_N500_ADV_75CORRUPT": 1.0000,
            "ARM_COSINE_BASELINE_N800_ADV_75CORRUPT": 1.0000,
            "ARM_RANDOM_BASELINE_N500": 0.00267,
            "ARM_REGRESSION_HIPPO_N50_50CORRUPT": 1.0000,
            "ARM_REGRESSION_HIPPO_DG_ONLY_N50_50CORRUPT": 1.0000,
            "ARM_REGRESSION_COSINE_N50_50CORRUPT": 1.0000
        },
        "key_per_arm_r1_stds": {
            "ARM_HIPPOCAMPAL_N500_ADV_90CORRUPT": 0.00094,
            "ARM_HIPPOCAMPAL_N500_ADV_75CORRUPT": 0.00566,
            "ARM_HIPPOCAMPAL_N800_ADV_75CORRUPT": 0.00580,
            "ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_90CORRUPT": 0.00660,
            "ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_75CORRUPT": 0.00490
        },
        "positive_control_regression_bit_identical_to_predecessor_commit_96d9055e5": True,
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "baseline_in_band_ok": True,
        "regime_discriminator_fired": False,
        "regime_discriminator_did_not_fire_reason": "cosine baseline saturates at 1.000 across all three adversarial regimes because n_dim=2048 with cluster cos=0.64 leaves a deterministic 0.114 argmax margin under 90% cue-zeroing (SNR math verified: signal sqrt(0.10)=0.316 vs distractor 0.64*0.316=0.202)",
        "composes_with_atoms": [
            "MATH_SPOKE3_HIPPOCAMPAL_EPISODIC_BINDING_SMOKE_EXISTENCE_PROOF_r1_1p000_N50_TFload_4p8pct_2026_07_03",
            "META_TASK_CLASS_MISMATCH_HIPPOCAMPAL_MECHANISM_MM_STANDARD_2_WITNESS_2026_07_03",
            "T_methodology/META_RULE_AG_substrate_too_robust_for_mechanism_at_default_regime"
        ],
        "expansion_criterion_to_CG_MECHANISM_BEATS_BASELINE": "future regime where baseline drops out of ceiling (>=95% cue-zero, or reduced n_dim to 512 or 1024, or cluster cos>=0.90 with adversarial_flip_frac>=0.05) that still holds mechanism r1>=0.60 would upgrade this to CG_MECHANISM_BEATS_BASELINE",
        "supersedes_none": True,
        "amends_smoke_existence_proof_by_extending_load_curve_to_48pct_with_adversarial": True,
        "cert_increment_delta": 1
    }
}


# ============= ATOM (b): MATH CG_HONEST_NEGATIVE architectural on DG expansion at extreme sparse cue =============
atom_b_arch_hn = {
    "id": "math::T2/MATH_META_DG_EXPANSION_AMPLIFIES_NOISE_MORE_THAN_SEPARATES_SIGNAL_AT_EXTREME_SPARSE_CUE_CA3_CONTRIBUTION_MILDLY_NEGATIVE_not_zero_CG_HONEST_NEGATIVE_architectural_finding_at_90pct_cue_zero_N500_adversarial_DG_ONLY_r1_0p7347_vs_full_HIPPO_DG_plus_CA3_r1_0p7193_CA3_delta_neg_0p0154_at_75pct_cue_zero_DG_ONLY_r1_0p9880_vs_HIPPO_r1_0p9780_CA3_delta_neg_0p0100_MECHANISM_LEVEL_DG_expansion_40x_2048_to_8192_with_2pct_sparsity_target_already_saturates_separability_lever_before_CA3_gets_to_fill_in_pattern_completion_at_high_sparsity_regime_this_is_NOT_the_Wikipedia_retrieval_finding_but_an_INTRINSIC_architecture_finding_at_capacity_regime_composes_with_prior_wikipedia_HF_but_distinct_root_cause_2026_07_03",
    "name": "MATH-META architectural CG_HONEST_NEGATIVE: DG expansion is anti-signal at extreme sparse cue; CA3 contribution MILDLY NEGATIVE (not zero) in both 75% and 90% adversarial regimes",
    "corpus": "math",
    "tier": "T2",
    "kind": "experiment_record_architectural_finding",
    "description": (
        "CG_HONEST_NEGATIVE architectural finding: adding CA3 pattern-completion on top of DG "
        "expansion+sparsify MILDLY HURTS retrieval in BOTH adversarial cue-corruption regimes tested. "
        "This is a distinct finding from the prior Wikipedia retrieval HF (which was task-class-mismatch); "
        "here the root cause is architectural at the CA3-on-top-of-DG stage in the load-bearing regime. "
        "Independent recompute off-disk: "
        "At 90% cue-zero + adversarial (N=500, cluster cos ~0.64): "
        "  ARM_HIPPOCAMPAL_DG_ONLY (no CA3) r1 mean 0.7347 std 0.00660 [0.742, 0.736, 0.726] "
        "  ARM_HIPPOCAMPAL       (DG+CA3) r1 mean 0.7193 std 0.00094 [0.720, 0.720, 0.718] "
        "  CA3 contribution delta = -0.0154 (SLIGHTLY NEGATIVE) "
        "At 75% cue-zero + adversarial (N=500): "
        "  ARM_HIPPOCAMPAL_DG_ONLY r1 mean 0.9880 std 0.00490 [0.982, 0.994, 0.988] "
        "  ARM_HIPPOCAMPAL       r1 mean 0.9780 std 0.00566 [0.974, 0.986, 0.974] "
        "  CA3 contribution delta = -0.0100 (SLIGHTLY NEGATIVE) "
        "SYMMETRIC-VERIFY CORRECTION (auditor sharpens cell-author framing): cell-author interpretation "
        "text called CA3 contribution 'nearly zero (+0.0000)'; verified off-disk the value is not zero "
        "but MILDLY NEGATIVE in both regimes. Directionally identical (CA3 does not add value) but "
        "sharper: at these regimes, CA3 pattern-completion actively removes ~1-2% recall. "
        "MECHANISM-LEVEL HYPOTHESIS: DG expansion at 40x (2048->8192) with 2%-sparsity target already "
        "saturates the separability lever at extreme corruption (input entropy is already destroyed by "
        "90% cue-zeroing, and DG amplifies whatever remains including noise); CA3 pattern-completion "
        "then makes wrong-attractor decisions on the corrupted DG output. Cell-author noted 'DG "
        "projection amplifies noise more than separates signal' -- verified: intra_pair_cos_mean at "
        "DG_ONLY 90CORRUPT is 0.061 (very low signal), CA3 pattern-completion can't recover it. "
        "SCOPE: this finding is limited to CA3-on-top-of-DG in the EXTREME sparse cue + high capacity "
        "load regime (N>=500 -> 48%+ TF capacity; cue-zero >=75%). At the 4.8% TF-load easy regime, "
        "CA3 works fine (existence proof holds r1=1.000). So this is a NARROW architectural bound: "
        "CA3 becomes counterproductive at capacity+extreme-corruption edge. "
        "COMPOSES WITH: prior atom MATH_SPOKE3_HIPPOCAMPAL_DG_CA3_WIKIPEDIA_SMOKE_HF (which is task-"
        "class mismatch), but this finding is INDEPENDENT: at the intended episodic-binding task class "
        "with capacity+corruption load, CA3 also fails to add value. Two different failure modes for "
        "the same architecture. "
        "REVIVAL/EXPANSION: (1) Try adaptive CA3 gating (only apply CA3 when DG output is above sparsity "
        "band, indicating recoverable signal). (2) Try lower DG expansion factor (2048->4096 rather than "
        "8192) so CA3 has denser input to complete. (3) Try higher DG sparsity target (5% not 2%) so "
        "DG output is less over-sparsified."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_architectural_finding",
        "term_class": "SPOKE3_DG_EXPANSION_ANTI_SIGNAL_AT_EXTREME_SPARSE_CUE_CA3_MILD_NEG_CONTRIB",
        "cert_status": "chain_grade_honest_negative",
        "cert_class": "CG_HONEST_NEGATIVE_architectural_finding_ablation_shows_CA3_mildly_hurts_at_capacity_edge",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_spoke3_discriminating_smoke",
        "raw_metrics_path": METRICS_PATH,
        "cell_source_path": CELL_PATH,
        "commit_hash": COMMIT,
        "cell_anchor": CELL_ANCHOR,
        "ablation_pair_at_90pct_cue_zero": {
            "DG_ONLY_r1_mean": 0.7347,
            "HIPPO_DG_plus_CA3_r1_mean": 0.7193,
            "CA3_contribution_delta": -0.0154
        },
        "ablation_pair_at_75pct_cue_zero": {
            "DG_ONLY_r1_mean": 0.9880,
            "HIPPO_DG_plus_CA3_r1_mean": 0.9780,
            "CA3_contribution_delta": -0.0100
        },
        "auditor_sharpening_correction_vs_cell_author": "cell-author frame 'CA3 adds nearly zero (+0.0000)' softens the finding; off-disk verified CA3 contribution is MILDLY NEGATIVE in BOTH regimes (-0.0154 at 90%, -0.0100 at 75%). Directionally identical, but the correct framing is CA3 mildly hurts at capacity+corruption edge.",
        "mechanism_level_hypothesis": "DG 40x expansion + 2% sparsity target already saturates separability lever at extreme cue corruption; DG output intra_pair_cos_mean at 90CORRUPT is only 0.061; CA3 pattern-completion makes wrong-attractor decisions on this near-noise DG output",
        "scope_narrow": "capacity_edge_N_gte_500_and_cue_zero_gte_75pct_only; does NOT contradict prior existence proof at 4.8% TF load",
        "revival_criteria": [
            "adaptive_CA3_gating_only_when_DG_output_sparsity_within_target_band",
            "lower_DG_expansion_factor_4x_not_16x_more_dense_CA3_input",
            "higher_DG_sparsity_target_5pct_not_2pct_less_over_sparsified"
        ],
        "composes_with_atoms": [
            "MATH_SPOKE3_HIPPOCAMPAL_EPISODIC_BINDING_SMOKE_EXISTENCE_PROOF_r1_1p000_N50_TFload_4p8pct_2026_07_03",
            "MATH_SPOKE3_HIPPOCAMPAL_DG_CA3_WIKIPEDIA_SMOKE_HF_r5_0p145_vs_charTri_0p854_N500_2026_07_03"
        ],
        "distinct_from_wikipedia_HF_root_cause": "Wikipedia HF was task-class-mismatch (open-domain retrieval task, mechanism designed for episodic one-shot); THIS finding is at the mechanism's INTENDED task class (episodic binding) at capacity+corruption edge, hence architectural rather than task-class mismatch",
        "cert_increment_delta": 1
    }
}


# ============= ATOM (c): META DISCIPLINE_META witness promotion 1->2 (cell-author self-corrects verdict_msg) =============
atom_c_discipline = {
    "id": "META_METHODOLOGY_WITNESS_CELL_AUTHOR_SELF_CORRECTS_VERDICT_MSG_OVERCLAIM_IN_SAME_CELL_INTERPRETATION_SECTION_SECOND_WITNESS_promotes_prior_1_witness_TF_formula_in_code_to_MM_STANDARD_2_witnesses_discipline_propagation_across_cell_authoring_boundaries_2026_07_03",
    "name": "METHODOLOGY_WITNESS #2: cell-author refuses own verdict_msg REFUTED framing in same-cell interpretation section; provides post-hoc SNR math showing regime-insufficient. Promotes to MM_STANDARD 2 witnesses.",
    "corpus": "meta",
    "tier": "T_measured_mechanism_standard",
    "kind": "discipline_meta_methodology_witness",
    "description": (
        "Second-witness promotion of discipline-propagation-witness class. First witness "
        "(META_METHODOLOGY_WITNESS_SKUNKWORKS_CORRECTED_TF_FORMULA_IN_CODE_2026_07_03, filed "
        "2026-07-03 04:15Z): cell-author encoded Skunkworks-corrected TF-capacity formula directly "
        "at line 137 of the SMOKE cell without prompting. Second witness (THIS ATOMIZATION): cell-"
        "author of the DISCRIMINATING SMOKE cell (same anchor family) emits verdict_msg calling "
        "task-class-mismatch hypothesis 'REFUTED' and calling result 'HARD_FAIL_NO_MECHANISM_"
        "SEPARATION', THEN in the same-cell interpretation section EXPLICITLY REFUSES those framings "
        "with post-hoc SNR math: target signal cos = sqrt(0.10) = 0.316 vs distractor bound "
        "0.64*0.316 = 0.202, deterministic 0.114 margin means cosine argmax always wins at "
        "n_dim=2048 with cluster cos=0.64. Cell-author concludes 'discriminator did not fire; "
        "regime is insufficient to force baseline degradation; verdict_msg REFUTED framing is "
        "over-strong'. AUDITOR CONFIRMS off-disk: baseline saturates at 1.0000 across all three "
        "adversarial cosine baseline arms; discriminator did not fire; META_RULE_AG-adjacent class. "
        "This is DISTINCT discipline from witness 1 (which was TF-formula-in-code): witness 2 is "
        "verdict-msg-honest-reread + regime-realism-post-hoc-verification, both USER-locked "
        "disciplines from feedback catalog. Discipline propagation is now witnessed at 2 independent "
        "sub-disciplines: pre-arg-parse formula correction (witness 1) AND post-hoc verdict reframing "
        "(witness 2). Promotion 1->2 witnesses supports MM_STANDARD; promotion to CG_META would "
        "require witness 3 on a third independent discipline (e.g., pre-reg regime-realism check, "
        "positive-control-clears-floor-before-negative-attribution, or discriminator-must-survive-scale)."
    ),
    "aliases": ["methodology_witness_verdict_msg_honest_reread_2026_07_03"],
    "metadata": {
        "verified_off_data": True,
        "verified_ts": TS_ISO,
        "verifier": "hdi_skunkworks",
        "commit_hash": COMMIT,
        "cell_file": CELL_PATH,
        "cert_status": "measured_mechanism_standard",
        "cert_class": "MM_STANDARD_2_witnesses_discipline_propagation_across_independent_disciplines",
        "supersedes_atom": "META_METHODOLOGY_WITNESS_SKUNKWORKS_CORRECTED_TF_FORMULA_IN_CODE_2026_07_03",
        "witnesses_count": 2,
        "witness_atoms": [
            "META_METHODOLOGY_WITNESS_SKUNKWORKS_CORRECTED_TF_FORMULA_IN_CODE_2026_07_03",
            "this_atom_cell_author_self_corrects_verdict_msg_overclaim_2026_07_03"
        ],
        "witness_1_discipline": "encoded_Skunkworks_corrected_TF_formula_in_cell_source_line_137",
        "witness_2_discipline": "refused_own_verdict_msg_REFUTED_framing_in_same_cell_interpretation_with_post_hoc_SNR_math",
        "composes_memory_rules": [
            "feedback_verdict_msg_honest_reread.md",
            "feedback_test_rationality_encoding_before_readout_2026-06-27",
            "feedback_fix28_verify_per_arm_metrics_not_summary_verdict_text_2026-06-22",
            "META_RULE_AG_substrate_too_robust_for_mechanism_at_default_regime"
        ],
        "promotion_criterion_to_CG_META": "third independent discipline witnessed in cell-author code or same-cell interpretation without Skunkworks prompting (e.g., positive-control-clears-floor-before-negative-attribution, or discriminator-must-survive-scale check)",
        "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
        "cert_increment_delta": 0
    }
}


# ============= ATOM (d): META AMENDMENT parent MM_TENTATIVE_SYNTHESIS_4 -> two-gate promotion criterion =============
atom_d_amendment = {
    "id": "META_AMENDMENT_TO_PARENT_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_MM_TENTATIVE_SYNTHESIS_4_witnesses_promotion_criterion_refined_to_TWO_GATE_deterministic_at_Gate_1_landing_Gate_1_PPMI_FULL_10K_formal_3_seed_landing_within_plus_minus_0p02_of_preliminary_delta_neg_0p024_Gate_2_Spoke3_discriminating_regime_witness_with_UNAMBIGUOUS_mechanism_vs_baseline_separation_current_Spoke3_landing_does_NOT_satisfy_Gate_2_because_baseline_saturates_at_1p000_regime_insufficient_Gate_2_requires_future_regime_ge_95pct_cue_zero_OR_n_dim_reduced_to_512_or_1024_OR_cluster_cos_ge_0p90_2026_07_03",
    "name": "META AMENDMENT: parent MM_TENTATIVE_SYNTHESIS_4_witnesses promotion criterion refined to TWO-GATE (Gate 1 PPMI FULL 3-seed within +/-0.02; Gate 2 Spoke 3 discriminator-fires with future tighter regime). Current Spoke 3 landing does NOT satisfy Gate 2.",
    "corpus": "meta",
    "tier": "T2",
    "kind": "metadata_amendment_to_parent_atom",
    "description": (
        "AMENDS parent atom (Store atoms are immutable-append; this is an amendment atom that "
        "supersedes the parent's promotion_criterion_to_CG_META metadata field via cross-reference). "
        "Parent atom id: meta::T2/META_SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_"
        "BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE_MM_TENTATIVE_SYNTHESIS_4_witnesses_... "
        "Parent stated promotion criterion 'witness at 2 more independent mechanism classes (e.g., "
        "Spoke 3 hippocampal pattern-separation OR neuroscience A-B-C composition) at FULL scale "
        "with same result would promote to CG_META'. THIS AMENDMENT refines to TWO DETERMINISTIC "
        "GATES so promotion decision at Gate 1 landing is by-construction. "
        "GATE 1: PPMI/SVD FULL Wikipedia N=10K formal 3-seed metrics.json landing must confirm the "
        "preliminary 2-seed heartbeat r@5 delta (-0.024 PPMI below char-trigram) within +/-0.02 "
        "(i.e., PPMI-minus-char-trigram delta in [-0.044, -0.004]). Currently PPMI FULL re-run in "
        "flight; this gate is the audit-trail-formalization gate, not an epistemic gate (direction "
        "already established). "
        "GATE 2: A Spoke 3 hippocampal discriminating-regime witness with UNAMBIGUOUS mechanism-vs-"
        "baseline separation, i.e., a regime where cosine baseline drops OUT OF CEILING (baseline "
        "r@1 <= 0.90) AND mechanism arms lift or lose by at least +/-0.10. "
        "ASSESSMENT of current Spoke 3 discriminating-regime landing (2026-07-03, commit 1d8b0ec44): "
        "does NOT satisfy Gate 2. Reason: cosine baseline saturates at r@1=1.000 in all three "
        "adversarial regimes (75%, 90%, 90% at N=800), so discriminator DID NOT FIRE. SNR math "
        "verified off-disk: at n_dim=2048 with cluster cos=0.64 and 90% cue-zeroing, target signal "
        "cos = sqrt(0.10) = 0.316 vs distractor bound 0.64*0.316 = 0.202 yields deterministic 0.114 "
        "argmax margin. Cell-author correctly refused own verdict_msg's REFUTED framing on this "
        "basis. "
        "GATE 2 REQUIRES FUTURE REGIME (cell-author-suggested + auditor-confirmed): "
        "  (i) cue-zero fraction >= 0.95 (reduces target signal cos to sqrt(0.05)=0.224 while "
        "      distractor stays 0.64*0.224=0.143; margin 0.081 -- baseline may drop below ceiling); "
        "  OR (ii) n_dim reduced to 512 or 1024 (increases noise floor from random cross-cosine "
        "      sqrt(2/pi/n) so 0.202 distractor bound gets closer to noise); "
        "  OR (iii) cluster cos raised to >= 0.90 with adversarial_flip_frac >= 0.05 (distractor "
        "      bound rises to 0.90*0.316=0.284, closer to target 0.316, baseline drops). "
        "Cell-author recommended (i) as first attempt. Auditor concurs and additionally recommends "
        "combining (i) + n_dim=1024 for robustness. "
        "PROMOTION DECISION AT GATE 1 LANDING (deterministic): "
        "  IF Gate 1 confirms PPMI delta in [-0.044, -0.004] AND Gate 2 satisfied (either by future "
        "     Spoke 3 tighter-regime landing showing mechanism beats OR ties baseline) "
        "  THEN promote parent MM_TENTATIVE -> CG_META with scope-refinement annotation citing "
        "     META_TASK_CLASS_MISMATCH_HIPPOCAMPAL_MECHANISM_MM_STANDARD_2_WITNESS. "
        "  IF Gate 1 confirms but Gate 2 not yet satisfied (Spoke 3 tighter regime not yet run) "
        "  THEN parent remains MM_TENTATIVE; treat as CG_META_PENDING_GATE_2. "
        "  IF Gate 1 fails (PPMI delta swings positive or by more than +/-0.02) "
        "  THEN parent demotes toward MM_TENTATIVE and re-examine PPMI witness at scale. "
        "COMPOSES WITH: parent atom, current landing atoms (a) and (b), META_TASK_CLASS_MISMATCH "
        "MM_STANDARD_2 (2026-07-03), META_RULE_AG (substrate-too-robust-for-default-regime)."
    ),
    "aliases": ["parent_META_two_gate_amendment_2026_07_03"],
    "metadata": {
        "verified_off_data": True,
        "verified_ts": TS_ISO,
        "verifier": "hdi_skunkworks",
        "commit_hash": COMMIT,
        "cert_status": "meta_metadata_amendment_no_cert_delta",
        "cert_class": "META_AMENDMENT_two_gate_promotion_criterion_refinement",
        "amends_parent_atom_id": "meta::T2/META_SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE_MM_TENTATIVE_SYNTHESIS_4_witnesses_across_heterogeneous_mechanism_classes_witness1_substrate_content_v1_concept_encoder_WordNet_N100_r5_0p160_below_char_trigram_r5_0p280_witness2_component_C_modern_hopfield_readout_WordNet_N100_r5_0p05_below_cosine_0p16_below_char_trigram_0p280_witness3_VWFA_HRR_position_binding_wikipedia_smoke_N500_r5_0p776_below_char_trigram_r5_0p854_witness4_PPMI_SVD_wikipedia_FULL_N10K_r5_0p6791_below_char_trigram_r5_0p7030_scale_reversal_from_smoke_which_had_plus_0p052_lift_pattern_all_four_substrate_native_structural_mechanisms_concept_encoder_readout_position_binding_co_occurrence_matrix_factorization_fail_to_beat_surface_char_trigram_bag_on_real_content_retrieval_tasks_only_synthetic_supervised_clustering_regime_Spoke1_v3D_Spoke2_Foldiak_saw_them_win_mechanism_analog_is_not_task_analog_USER_LOCKED_holds_scope_witnesses_at_N100_N500_N10K_real_wordnet_and_real_wikipedia_common_failure_mode_char_trigram_bag_gets_free_high_lexical_overlap_signal_that_structural_encoders_do_not_add_to_or_actively_dilute_expansion_criterion_two_more_independent_mechanism_classes_e_g_hippocampal_pattern_separation_Spoke3_or_neuroscience_ABC_composition_at_FULL_scale_with_same_result_would_promote_to_CG_META_2026-07-03",
        "amendment_type": "promotion_criterion_refinement_to_two_deterministic_gates",
        "gate_1_definition": "PPMI/SVD FULL Wikipedia N=10K formal 3-seed metrics.json landing confirms preliminary delta PPMI-minus-char-trigram in [-0.044, -0.004]",
        "gate_1_status": "IN_FLIGHT_PPMI_FULL_10K_re_run_orchestrator_a610548e",
        "gate_2_definition": "Spoke 3 hippocampal discriminating-regime witness with baseline r@1 <= 0.90 (out of ceiling) AND mechanism arm lift or loss magnitude >= 0.10",
        "gate_2_status_current_landing": "NOT_SATISFIED_baseline_saturates_at_1p000_discriminator_did_not_fire_regime_insufficient",
        "gate_2_future_regime_recommendations": [
            "cue_zero_fraction_ge_0p95_target_signal_sqrt_0p05_0p224_distractor_bound_0p143_margin_0p081_baseline_may_drop",
            "n_dim_reduced_to_512_or_1024_raises_random_cross_cosine_floor_toward_distractor_bound",
            "cluster_cos_ge_0p90_with_adversarial_flip_frac_ge_0p05_distractor_bound_0p284_closer_to_target_0p316"
        ],
        "cell_author_recommended_next_regime": "cue_zero_ge_0p95",
        "auditor_additionally_recommends": "combine_cue_zero_0p95_plus_n_dim_1024_for_robustness",
        "promotion_decision_at_gate_1_landing_deterministic_rules": {
            "gate1_pass_gate2_pass_via_future_spoke3_tighter": "promote_MM_TENTATIVE_to_CG_META_with_scope_refinement_annotation",
            "gate1_pass_gate2_pending": "remain_MM_TENTATIVE_labeled_CG_META_PENDING_GATE_2",
            "gate1_fail": "demote_toward_MM_TENTATIVE_reexamine_PPMI_witness_at_scale"
        },
        "composes_with_atoms": [
            "META_TASK_CLASS_MISMATCH_HIPPOCAMPAL_MECHANISM_MM_STANDARD_2_WITNESS_2026_07_03",
            "T_methodology/META_RULE_AG_substrate_too_robust_for_mechanism_at_default_regime",
            "math::T1/MATH_SPOKE3_HIPPOCAMPAL_EPISODIC_BINDING_CG_MEASURED_BOUND_at_48pct_TF_CAPACITY (this batch atom a)",
            "math::T2/MATH_META_DG_EXPANSION_AMPLIFIES_NOISE (this batch atom b)"
        ],
        "cert_increment_delta": 0
    }
}


# ================================================================================
# A5-GATED APPENDS (atomic tmp+os.replace+verify-load) with matching TS_ISO ledger
# ================================================================================
def a5_append(path, atom):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atoms_", suffix=".jsonl")
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
        "atomized_by": atom["metadata"].get("atomized_by") or atom["metadata"].get("verifier"),
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
    session_tag = "2026-07-03_spoke3_discriminating_smoke_MB_and_META_two_gate_amendment"

    n_math1 = a5_append(MATH_ATOMS, atom_a_cg_bound)
    print(f"[atomize] MATH atom (a) CG_MEASURED_BOUND appended; total math lines={n_math1}")
    ledger_append(atom_a_cg_bound, session_tag)

    n_math2 = a5_append(MATH_ATOMS, atom_b_arch_hn)
    print(f"[atomize] MATH atom (b) CG_HONEST_NEGATIVE architectural appended; total math lines={n_math2}")
    ledger_append(atom_b_arch_hn, session_tag)

    n_meta1 = a5_append(META_ATOMS, atom_c_discipline)
    print(f"[atomize] META atom (c) DISCIPLINE_META MM_STANDARD_2 appended; total meta lines={n_meta1}")
    ledger_append(atom_c_discipline, session_tag)

    n_meta2 = a5_append(META_ATOMS, atom_d_amendment)
    print(f"[atomize] META atom (d) two-gate AMENDMENT appended; total meta lines={n_meta2}")
    ledger_append(atom_d_amendment, session_tag)

    print("[atomize] DONE 4 atoms + 4 ledger entries; A5-gated (tmp+os.replace+verify-load); matching TS_ISO")
