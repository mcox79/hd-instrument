#!/usr/bin/env python3
"""Skunkworks atomize -- Wave 1 (3 fulls) + Wave 1.6 (1 smoke STOP) + 1 META rule -- 2026-06-26.

Lands 5 atoms per the ruling note
d:/AI/hd-instrument/notes/skunkworks_landed_vet_wave1_4cell_plus_w16_smoke_2026-06-26.md.

Atom inventory:
  1. math::T3 EXP_cortex_E_tensor_separate_importance_v1 -> honest_negative (delta=+1)
       null-op-by-threshold (E_min=0.5 >= e_threshold=0.3 -> n_downscaled=0) at smoke-
       saturation regime; precursor to RETEST_fairness_v2 structural refutation
  2. math::T3 EXP_topk_composition_refuse_gate_v1 -> measured_mechanism (delta=0)
       BY-CONSTRUCTION: amb_frac=0.000 in regime; DISJ + REFUSE arms degenerate to
       top1_commit identity; HARD_PASS verdict is by-construction
  3. math::T3 EXP_pc_cleanup_attractor_v1 -> measured_mechanism (delta=0)
       BY-CONSTRUCTION: all 18 arm-instances (3 seeds x 3 arms x 2 depths) produce
       BIT-IDENTICAL fe_per_hop; PC blend mixes attractor with itself at saturation
  4. math::T3 EXP_cortex_E_tensor_RETEST_fairness_v2_smoke -> honest_negative (delta=+1)
       SMOKE-STOP per pre-reg: cor(E,|W|)=0.984 vs <0.30 fairness gate; STRUCTURAL
       refutation of Fix B mechanism (constant-bump + linear decay reduces E to bimodal
       set-membership tag = retrieved-set is by-construction high-|W| subset)
  5. meta::T_methodology META_RULE_F_retrieval_success_driven_importance_signals_are_
       magnitude_coupled_by_construction -> discipline_meta (delta=0)
       CROSS-CELL rule: any importance signal gated on retrieval success (any bump
       shape) inherits structural correlation with |W @ key| because cleanup-argmax-
       correct condition selects high-readback-magnitude atoms by construction

Discipline (mirrors prior batch tools):
- A5 PRE/POST verify via PartitionedStore + cert_ledger_writer
- Pre-cert N = 612 -> Post-cert N = 614 (delta = +2 from atoms 1 + 4)
- Axiom 206 invariant
- Cap_pres 6/6
- Atomic Store add_atom (PartitionedStore handles tmp + os.replace)
- Idempotent ledger append (modulo ts)
- Foreground execution; ASCII only

Independent off-data per-arm recompute COMPLETED:
- Atom 1 (separate_importance_v1): all 9 arm-instances rec_old=1.000 + n_downscaled=0
  for ARM_E_GATED (E_min=0.5 above threshold=0.3); RANDOM downscales 200 with no loss
- Atom 2 (refuse_gate_v1): all 9 arm-instances correctness=1.000 + amb_frac=0.000 +
  n_refused=0 + n_disjuncted=0 (mechanism never triggered)
- Atom 3 (pc_cleanup_attractor_v1): all 18 arm-instances recall=1.000 + bit-identical
  fe_per_hop across the 3 arms within each (seed, depth) tuple
- Atom 4 (RETEST_fairness_v2 smoke): cor(E,|W|)=0.984 vs gate<0.30; E_retrieved=499.5
  E_unretrieved=0.0 perfectly bimodal; structural mechanism-grounded refutation
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row

STORE_ROOT = REPO_ROOT / "data" / "substrate_index"
NOTES_PATH = "notes/skunkworks_landed_vet_wave1_4cell_plus_w16_smoke_2026-06-26.md"
DIAGNOSIS_NOTE = (
    "notes/exp_dev_to_research_cortex_E_tensor_v2_SMOKE_HARD_FAIL_Fix_B_wrong_shaped_2026-06-26.md"
)
CELL_COMMIT_PLACEHOLDER = "wave1_w16_2026-06-26"  # actual short-hash unknown; placeholder per ledger convention


# ============================================================================
# Atom 1: cortex_E_tensor_separate_importance_v1 -> honest_negative (+1)
# ============================================================================

def atom_1_cortex_E_tensor_separate_importance_v1_honest_negative() -> Atom:
    return Atom(
        id=(
            "T3/EXP_cortex_E_tensor_separate_importance_v1_HONEST_NEGATIVE_"
            "null_op_by_threshold_E_min_0p5_above_e_threshold_0p3_n_downscaled_0_"
            "smoke_saturation_regime_M_OLD_300_M_RECENT_200_N_2048_alpha_0p244_"
            "all_9_arm_instances_rec_old_1p000_RANDOM_downscales_200_with_no_loss_"
            "precursor_to_RETEST_fairness_v2_structural_refutation"
        ),
        name=(
            "Cortex E-tensor separate-importance v1: HONEST_NEGATIVE (null-op-by-threshold; "
            "E_min=0.5 >= e_threshold=0.3 so ARM_E_GATED_DOWNSCALE n_downscaled=0 across "
            "all 3 seeds; smoke-saturation regime: all 9 arm-instances rec_old=1.000 "
            "rec_recent=1.000; RANDOM correctly downscales 200 atoms with no recall loss)"
        ),
        description=(
            "HONEST_NEGATIVE: cortex E-tensor mechanism produces NO measurable signal in "
            "this regime because (a) E-gate is a null-op (E_min=0.5 above threshold 0.3 = "
            "zero atoms gated), (b) regime is smoke-saturated (M_OLD+M_RECENT=500 << "
            "capacity at N=2048 alpha=0.244), (c) RANDOM_GATED downscales 200 atoms with "
            "no recall loss = headroom exists but mechanism cannot exercise it.\n\n"
            "VERBATIM PER-ARM (3 seeds, 600 queries total):\n"
            "  seed=7:  ARM_NO_E_BASELINE     rec_old=1.000 rec_recent=1.000 n_down=820 cor=0.013\n"
            "           ARM_E_GATED_DOWNSCALE rec_old=1.000 rec_recent=1.000 n_down=0   cor=0.010\n"
            "           ARM_RANDOM_GATED      rec_old=1.000 rec_recent=1.000 n_down=200 cor=0.001\n"
            "  seed=17: ARM_NO_E_BASELINE     rec_old=1.000 rec_recent=1.000 n_down=819 cor=0.059\n"
            "           ARM_E_GATED_DOWNSCALE rec_old=1.000 rec_recent=1.000 n_down=0   cor=0.073\n"
            "           ARM_RANDOM_GATED      rec_old=1.000 rec_recent=1.000 n_down=200 cor=-0.010\n"
            "  seed=23: ARM_NO_E_BASELINE     rec_old=1.000 rec_recent=1.000 n_down=820 cor=-0.002\n"
            "           ARM_E_GATED_DOWNSCALE rec_old=1.000 rec_recent=1.000 n_down=0   cor=-0.017\n"
            "           ARM_RANDOM_GATED      rec_old=1.000 rec_recent=1.000 n_down=200 cor=0.042\n\n"
            "DIAGNOSIS: E_min=0.5 means the lowest E across all 500 atoms is at the floor "
            "of the EWMA bump range; e_threshold=0.3 is BELOW the floor; so the E < threshold "
            "selector never fires. Wave 1.5 HARDER_REGIME smoke (n_seeds=1, baseline_old=0.8) "
            "exposes the mechanism is wrong-direction; Wave 1.6 RETEST_fairness_v2 smoke "
            "(cor(E,|W|)=0.984) supplies the structural refutation.\n\n"
            "TIER: honest_negative. Mechanism at this regime is a measured null. Counts as "
            "proven-negative at smoke-saturation regime. Future cells with different "
            "e_threshold or capacity-stress regime can re-test, but the v1 cell's claim is "
            "structurally null.\n\n"
            "VET: skunkworks landed-VET 2026-06-26 (verified off per-arm metrics.json; not "
            "from verdict_msg). REFERENT: data/exp_cortex_E_tensor_separate_importance_v1/metrics.json\n"
            f"RULING_NOTE: {NOTES_PATH}\n"
        ),
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.METHODOLOGY,
        aliases=(
            "cortex_E_tensor_v1_HARD_FAIL_smoke_saturation",
            "exp_cortex_E_tensor_separate_importance_v1_null_op_by_threshold",
        ),
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",  # honest_negative counts toward CERT N
            "cert_status": "honest_negative",
            "cert_class": "pre_reg_pass",  # pre-reg HARD_FAIL gate triggered as expected
            "verdict": "HARD_FAIL",
            "verdict_subclass": "HONEST_NEGATIVE_null_op_by_threshold_smoke_saturation",
            "atomized_by": "skunkworks_landed_vet_wave1_4cell_plus_w16_smoke_2026-06-26",
            "verified_off_data": True,
            "n_seeds": 3,
            "regime": {"N": 2048, "M_OLD": 300, "M_RECENT": 200, "alpha": 0.244},
            "referent_metrics_path": "data/exp_cortex_E_tensor_separate_importance_v1/metrics.json",
            "referent_notes_path": NOTES_PATH,
            "cell_commit": CELL_COMMIT_PLACEHOLDER,
        },
    )


# ============================================================================
# Atom 2: topk_composition_refuse_gate_v1 -> measured_mechanism (+0)
# ============================================================================

def atom_2_topk_composition_refuse_gate_v1_measured_mechanism() -> Atom:
    return Atom(
        id=(
            "T3/EXP_topk_composition_refuse_gate_v1_MEASURED_MECHANISM_"
            "by_construction_amb_frac_0p000_DISJ_REFUSE_arms_degenerate_to_top1_commit_"
            "identity_n_refused_0_n_disjuncted_0_across_all_9_arm_instances_HARD_PASS_"
            "verdict_is_by_construction_not_chain_grade_per_Fix_28_verify_per_arm"
        ),
        name=(
            "Top-K composition refuse-gate v1: MEASURED_MECHANISM (by-construction; "
            "amb_frac=0.000 in regime so DISJ + REFUSE arms degenerate to TOP1_COMMIT "
            "identity; HARD_PASS verdict is by-construction, NOT chain-grade per "
            "by-construction-saturation rule)"
        ),
        description=(
            "MEASURED_MECHANISM (by-construction-saturation): top-K disjunctive + "
            "refuse-on-small-gap mechanisms are plumbed end-to-end (verified by self-test) "
            "but NEVER TRIGGERED in this regime because input ambiguity is zero.\n\n"
            "VERBATIM PER-ARM (3 seeds, 1800 queries total at p_flip=0.18 M=400 alpha=0.195):\n"
            "  seed=7:  T1=1.000 REFUSE=1.000 DISJ=1.000 amb_frac=0.000 n_refused=0 n_disj=0\n"
            "  seed=17: T1=1.000 REFUSE=1.000 DISJ=1.000 amb_frac=0.000 n_refused=0 n_disj=0\n"
            "  seed=23: T1=1.000 REFUSE=1.000 DISJ=1.000 amb_frac=0.000 n_refused=0 n_disj=0\n\n"
            "DIAGNOSIS: at p_flip=0.18 + M=400 + alpha=0.195, the gap statistic that "
            "triggers REFUSE (gap < gap_tau=0.1) and DISJUNCTIVE (top-K window) never "
            "fires -- every query has a single dominant retrieval. All three arms reduce "
            "to TOP1_COMMIT_BASELINE identity. HARD_PASS verdict (correctness=1.000 "
            "everywhere) is by-construction; mechanism is NOT chain-grade.\n\n"
            "COMPANION cell: exp_topk_composition_engineered_ambiguity_v1_smoke "
            "(amb_frac=0.345 in regime; DISJ +2.0pp over T1; amb_rec@K=2=0.290 fails 0.85 "
            "gate; MIDDLE_BAND at smoke) is the discriminating regime. If research dispatches "
            "the engineered_ambiguity FULL and it passes the discriminator gate at "
            "amb_rec@K=2 >= 0.85, this v1 atom could be SUPERSEDED by a chain_grade ruling.\n\n"
            "TIER: measured_mechanism. delta=0. Mechanism plumbed; not differentially "
            "discriminating at this regime.\n\n"
            "VET: skunkworks landed-VET 2026-06-26. REFERENT: data/exp_topk_composition_"
            "refuse_gate_v1/metrics.json\n"
            f"RULING_NOTE: {NOTES_PATH}\n"
        ),
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.METHODOLOGY,
        aliases=(
            "topk_composition_refuse_gate_v1_MM_by_construction",
            "exp_topk_composition_refuse_gate_v1_amb_frac_zero_mechanism_never_triggered",
        ),
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verdict": "HARD_PASS_by_construction",
            "verdict_subclass": "MEASURED_MECHANISM_by_construction_amb_frac_zero",
            "atomized_by": "skunkworks_landed_vet_wave1_4cell_plus_w16_smoke_2026-06-26",
            "verified_off_data": True,
            "n_seeds": 3,
            "regime": {"N": 2048, "M": 400, "alpha": 0.195, "p_flip": 0.18},
            "referent_metrics_path": "data/exp_topk_composition_refuse_gate_v1/metrics.json",
            "referent_notes_path": NOTES_PATH,
            "cell_commit": CELL_COMMIT_PLACEHOLDER,
        },
    )


# ============================================================================
# Atom 3: pc_cleanup_attractor_v1 -> measured_mechanism (+0)
# ============================================================================

def atom_3_pc_cleanup_attractor_v1_measured_mechanism() -> Atom:
    return Atom(
        id=(
            "T3/EXP_pc_cleanup_attractor_v1_MEASURED_MECHANISM_by_construction_"
            "all_18_arm_instances_recall_1p000_bit_identical_fe_per_hop_across_VAN_"
            "PC_each_hop_PC_final_within_each_seed_depth_tuple_pc_blend_mixes_"
            "attractor_with_itself_at_saturation_HARD_PASS_verdict_is_by_construction"
        ),
        name=(
            "PC cleanup attractor v1: MEASURED_MECHANISM (by-construction; all 18 arm-"
            "instances produce BIT-IDENTICAL fe_per_hop within each (seed, depth) tuple; "
            "PC blend pc_blend=0.3 mixes attractor with itself at saturation regime)"
        ),
        description=(
            "MEASURED_MECHANISM (by-construction-saturation): predictive-coding cleanup "
            "is plumbed (VAN_BASELINE, PC_AT_EACH_HOP, PC_FINAL_ONLY arms all implemented "
            "and self-test PASS) but produces BIT-IDENTICAL outputs at this regime.\n\n"
            "VERBATIM PER-ARM (3 seeds x 2 depths x 3 arms = 18 instances; 80 queries each):\n"
            "  All 18 instances: recall=1.000\n"
            "  Within each (seed, depth) tuple: VAN.fe_per_hop == PC_EACH.fe_per_hop == "
            "PC_FINAL.fe_per_hop (bit-identical list comparison verified off-data)\n\n"
            "DIAGNOSIS: at N=2048 V=1024 M_CHAINS=80 depths=(5,10), sign-cleanup already "
            "maps each hop to the noise-free attractor (recall=1.000 at depth 10). PC "
            "blend pc_blend=0.3 = 0.3 * attractor + 0.7 * raw_readback; but raw_readback "
            "AT SATURATION is already the attractor; so 0.3*att + 0.7*att = att. PC "
            "mechanism cannot differentially help where vanilla already perfect.\n\n"
            "COMPANION cell: exp_pc_cleanup_deeper_chains_v1_smoke (depths=(5,10) only, "
            "n_queries=4; same bit-identical-arm artifact at smoke) -- the FULL with "
            "depths=(15,20,30) HAS NOT LANDED despite caller framing. If research "
            "dispatches the deeper-chains FULL with noisy attractors (hop_noise_sigma > 0 "
            "+ depth >= 15) and PC differentially helps, this v1 atom could be SUPERSEDED "
            "by a chain_grade ruling.\n\n"
            "TIER: measured_mechanism. delta=0. Mechanism plumbed; non-discriminating at "
            "this regime.\n\n"
            "VET: skunkworks landed-VET 2026-06-26. REFERENT: data/exp_pc_cleanup_"
            "attractor_v1/metrics.json\n"
            f"RULING_NOTE: {NOTES_PATH}\n"
        ),
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.METHODOLOGY,
        aliases=(
            "pc_cleanup_attractor_v1_MM_by_construction",
            "exp_pc_cleanup_attractor_v1_bit_identical_arms_at_saturation",
        ),
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verdict": "HARD_PASS_by_construction",
            "verdict_subclass": "MEASURED_MECHANISM_by_construction_pc_blend_self_mix",
            "atomized_by": "skunkworks_landed_vet_wave1_4cell_plus_w16_smoke_2026-06-26",
            "verified_off_data": True,
            "n_seeds": 3,
            "regime": {"N": 2048, "V": 1024, "M_CHAINS": 80, "depths": [5, 10], "pc_blend": 0.3},
            "referent_metrics_path": "data/exp_pc_cleanup_attractor_v1/metrics.json",
            "referent_notes_path": NOTES_PATH,
            "cell_commit": CELL_COMMIT_PLACEHOLDER,
        },
    )


# ============================================================================
# Atom 4: cortex_E_tensor_RETEST_fairness_v2_smoke -> honest_negative (+1)
# ============================================================================

def atom_4_cortex_E_tensor_RETEST_fairness_v2_smoke_honest_negative() -> Atom:
    return Atom(
        id=(
            "T3/EXP_cortex_E_tensor_RETEST_fairness_v2_smoke_HONEST_NEGATIVE_"
            "Fix_B_refuted_at_smoke_cor_E_W_0p984_vs_USER_fairness_gate_0p30_"
            "E_perfectly_bimodal_499p5_retrieved_0p0_unretrieved_structural_set_"
            "membership_correlation_STOP_at_smoke_per_pre_reg_correct_discipline"
        ),
        name=(
            "Cortex E-tensor RETEST fairness v2 (Fix B): HONEST_NEGATIVE smoke-STOP "
            "(cor(E,|W|)=0.984 vs USER load-bearing fairness gate <0.30; E perfectly "
            "bimodal {0.0, 499.5}; mechanism CLASS structurally refuted; STOP at smoke "
            "per pre-reg is correct exp_dev discipline)"
        ),
        description=(
            "HONEST_NEGATIVE (smoke-grade, mechanism-class refutation, STOP-at-smoke "
            "per USER pre-reg gate): Fix B's constant-bump + linear-decay attempt to "
            "decouple E from magnitude FAILED structurally, not by tuning.\n\n"
            "VERBATIM PER-ARM (1 seed, N=256, M_OLD=150, M_RECENT=100, J=500, N_USE=45):\n"
            "  BASELINE_NO_DOWNSCALE  rec_RETR=1.000 rec_UNRETR=1.000 rec_recent=1.000 cor=-0.033 n_down=0\n"
            "  ARM_E_GATED_RETEST     rec_RETR=1.000 rec_UNRETR=0.880 rec_recent=0.820 cor=0.984  n_down=205\n"
            "  ARM_RANDOM_GATED       rec_RETR=0.844 rec_UNRETR=0.840 rec_recent=0.900 cor=-0.027 n_down=205\n"
            "  ARM_BASELINE_MAG_GATED rec_RETR=0.778 rec_UNRETR=0.780 rec_recent=0.900 cor=0.030  n_down=205\n\n"
            "E IS PERFECTLY BIMODAL: E_retrieved_mean=499.5 (45 atoms; every retrieved hit "
            "every cycle in 500 passes; uniform constant-bump - 500*0.001 decay = 499.5); "
            "E_unretrieved_mean=0.0 (105 atoms; no bumps; decayed to floor). cor(E,|W|)=0.984 "
            "is a structural set-membership correlation: the RETRIEVED-set IS the high-|W| "
            "subset BY CONSTRUCTION because cleanup-argmax-correct requires key_i to "
            "dominate W's response.\n\n"
            "PRE-REG STOP GATE: USER specified 'if fairness checks still fail at smoke, "
            "STOP and route back to research'. cor=0.984 >> 0.5 (HARD_FAIL gate) >> 0.30 "
            "(fairness gate). exp_dev correctly STOPPED at smoke without dispatching full. "
            "FULL run NOT EXECUTED.\n\n"
            "MECHANISM-CLASS REFUTATION (load-bearing): the failure is invariant to "
            "bump-shape. Constant-additive (Fix B) and EWMA (v1) BOTH inherit the structural "
            "coupling because the HIT condition itself is magnitude-correlated. Any "
            "retrieval-success-driven importance signal in the bump-shape family will "
            "structurally fail the fairness gate. (META_RULE_F atomized alongside this "
            "atom captures the cross-cell rule.)\n\n"
            "WHAT FIX B DID ACCOMPLISH (under-claimed per Fix #28):\n"
            "  - E_GATED beats RANDOM on RETRIEVED by +0.156 (1.000 vs 0.844)\n"
            "  - E_GATED beats MAG_GATED on RETRIEVED by +0.222 (1.000 vs 0.778)\n"
            "  - Fix A (RETRIEVED/UNRETRIEVED partition) correctly instrumented\n"
            "  - E carries 'was-this-atom-recently-queried' tag info -- but this is NOT "
            "    independent from |W|, so the importance frame is wrong.\n\n"
            "TIER: honest_negative. delta = +1. Smoke-grade evidence is sufficient because: "
            "(a) USER load-bearing pre-reg STOP-at-smoke gate fired correctly, (b) "
            "refutation is structural (mechanism-grounded, not statistical noise), (c) "
            "full-run cost would be wasted on a structurally-refuted mechanism class.\n\n"
            "VET: skunkworks landed-VET 2026-06-26 (verified off per-arm metrics.json + "
            "diagnosis note). REFERENT: data/exp_cortex_E_tensor_RETEST_fairness_v2_smoke/"
            f"metrics.json\nDIAGNOSIS_NOTE: {DIAGNOSIS_NOTE}\nRULING_NOTE: {NOTES_PATH}\n"
        ),
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.METHODOLOGY,
        aliases=(
            "cortex_E_tensor_RETEST_fairness_v2_Fix_B_refuted_smoke",
            "cortex_E_tensor_v2_smoke_STOP_per_pre_reg_structural_refutation",
        ),
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",  # honest_negative counts toward CERT N
            "cert_status": "honest_negative",
            "cert_class": "pre_reg_pass",
            "verdict": "HARD_FAIL_smoke_STOP_per_pre_reg",
            "verdict_subclass": "HONEST_NEGATIVE_smoke_grade_mechanism_class_refutation",
            "atomized_by": "skunkworks_landed_vet_wave1_4cell_plus_w16_smoke_2026-06-26",
            "verified_off_data": True,
            "n_seeds": 1,
            "smoke_only": True,
            "stop_at_smoke_per_pre_reg": True,
            "regime": {"N": 256, "M_OLD": 150, "M_RECENT": 100, "J": 500, "N_USE": 45},
            "key_stat": {
                "cor_E_W": 0.984,
                "pre_reg_gate_lt": 0.30,
                "hard_fail_gate_ge": 0.5,
                "E_retrieved_mean": 499.5,
                "E_unretrieved_mean": 0.0,
            },
            "referent_metrics_path": "data/exp_cortex_E_tensor_RETEST_fairness_v2_smoke/metrics.json",
            "referent_diagnosis_note": DIAGNOSIS_NOTE,
            "referent_notes_path": NOTES_PATH,
            "cell_commit": CELL_COMMIT_PLACEHOLDER,
        },
    )


# ============================================================================
# Atom 5: META_RULE_F retrieval-success-driven importance = magnitude-coupled
# ============================================================================

def atom_5_meta_rule_F_retrieval_success_importance_magnitude_coupled() -> Atom:
    return Atom(
        id=(
            "T_methodology/META_RULE_F_retrieval_success_driven_importance_signals_"
            "are_magnitude_coupled_by_construction_constant_bump_EWMA_multiplicative_"
            "all_inherit_structural_set_membership_correlation_cleanup_argmax_correct_"
            "selects_high_readback_magnitude_atoms_by_construction"
        ),
        name=(
            "META_RULE_F: retrieval-success-driven importance signals are magnitude-"
            "coupled by construction (any bump shape -- constant-additive, EWMA, "
            "multiplicative -- inherits structural correlation with |W @ key|)"
        ),
        description=(
            "META RULE (CERT-neutral; discipline_meta cert_class):\n\n"
            "ANY substrate importance signal E_i whose update rule is gated on retrieval "
            "success (E_i bumped iff key_i is argmax-correct under sign-cleanup against W, "
            "regardless of bump shape -- constant-additive, EWMA, multiplicative) inherits "
            "a structural correlation with |W @ key_i|.\n\n"
            "MECHANISM (why this is structural, not implementation): cleanup-argmax-correct "
            "condition requires key_i to dominate W's response to its own probe. This is "
            "exactly the condition that defines high |W @ key_i|. So 'atoms that get "
            "bumped' is by-construction a high-readback-magnitude subset. Any importance "
            "score derived from bump-history will inherit this coupling, regardless of "
            "bump-shape engineering.\n\n"
            "OBSERVED INSTANCES (2026-06-26):\n"
            "  - exp_cortex_E_tensor_separate_importance_v1 (EWMA bump): null-op-by-threshold; "
            "    E_min=0.5 above gate=0.3 means gate never fires.\n"
            "  - exp_cortex_E_tensor_RETEST_fairness_v2_smoke (constant-additive bump + "
            "    linear decay = Fix B): cor(E,|W|)=0.984 (vs USER pre-reg <0.30 gate); "
            "    E perfectly bimodal {0.0 unretrieved, 499.5 retrieved}. Structural "
            "    refutation that bump-shape engineering CANNOT decouple this.\n\n"
            "IMPLICATION FOR SUBSTRATE RESEARCH: importance signals that aim to be "
            "magnitude-independent CANNOT be derived from retrieval-success gating in the "
            "bumped-shape family. Need:\n"
            "  - Counterfactual-utility (ablation: does removing atom degrade recall? Yes -> "
            "    important. Independent of |W| because measured by ablation not readback).\n"
            "  - Surprisal-weighted bump (E bumped by (1 - p(obs|substrate)) not by hit; "
            "    requires substrate-native generative score, which substrate has via "
            "    cleanup-attractor convergence rate).\n"
            "  - Random-projection witness (E as JL-orthogonal random sketch; cor with |W| "
            "    -> 0 by Johnson-Lindenstrauss).\n"
            "  - Per-edge importance (not per-atom: edge-level signal can be magnitude-"
            "    decoupled even if atom-level cannot).\n"
            "  - Distribution-shape importance (not pointwise: e.g. entropy of activation "
            "    pattern vs simple readback magnitude).\n\n"
            "REFRAMING OPTION (cheap): accept E as a 'was-this-atom-recently-queried' TAG "
            "(not as importance), which preserves the cor(E,|W|)~1.0 observation as "
            "expected-not-failed; PASS bands change accordingly. This is a research "
            "scope-change, not a mechanism win.\n\n"
            "ATOMIZED BY: skunkworks landed-VET batch 2026-06-26 (atoms 1 + 4 are the "
            "observed instances).\n"
            f"RULING_NOTE: {NOTES_PATH}\nDIAGNOSIS_NOTE: {DIAGNOSIS_NOTE}\n"
        ),
        corpus=Corpus.META,
        tier=Tier.TIER_NA,
        kind=AtomKind.METHODOLOGY_RULE,
        aliases=(
            "META_RULE_F_retrieval_success_importance_magnitude_coupled",
            "importance_signal_design_constraint_no_bump_shape_decoupling",
        ),
        metadata={
            "provenance_quality": "DISCIPLINE_META",
            "cert_status": "custom",
            "cert_class": "discipline_meta",
            "verdict": "META_RULE_CERT_NEUTRAL_F_skunkworks",
            "atomized_by": "skunkworks_landed_vet_wave1_4cell_plus_w16_smoke_2026-06-26",
            "verified_off_data": True,
            "observed_instances": [
                "math::T3/EXP_cortex_E_tensor_separate_importance_v1_HONEST_NEGATIVE",
                "math::T3/EXP_cortex_E_tensor_RETEST_fairness_v2_smoke_HONEST_NEGATIVE",
            ],
            "rule_scope": (
                "any importance signal gated on retrieval-success in the bump-shape family"
            ),
            "referent_notes_path": NOTES_PATH,
            "referent_diagnosis_note": DIAGNOSIS_NOTE,
        },
    )


# ============================================================================
# Driver
# ============================================================================

def main():
    print("Skunkworks atomize -- Wave 1 (3 fulls) + Wave 1.6 (1 smoke STOP) + 1 META 2026-06-26")
    print("=" * 80)

    # A5 PRE: snapshot
    print("\n[A5 PRE] Loading PartitionedStore...")
    ps = PartitionedStore(STORE_ROOT)
    pre_cert = sum(
        1 for a in ps.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    pre_total = sum(1 for _ in ps.all_atoms())
    print(f"  CERT N (pre)   = {pre_cert}")
    print(f"  Atom total     = {pre_total}")

    # PRE-cert accommodates re-run idempotency: original snapshot was 612; if rerun
    # finds 613 or 614 it means a prior partial run landed atoms 1 (and/or 4).
    BASE_PRE_CERT = 612
    assert pre_cert in (612, 613, 614), (
        f"A5 PRE: expected CERT N in [612, 613, 614], got {pre_cert}"
    )
    # The cumulative delta accounting will use BASE_PRE_CERT; idempotent Store
    # adds skip via existing_ids check, idempotent ledger writes skip via
    # _ts_stripped match in cert_ledger_writer.
    pre_cert_base = BASE_PRE_CERT

    # Atom inventory
    atoms = [
        ("Atom 1 (cortex_E_tensor_separate_importance_v1 -> honest_negative +1)",
         atom_1_cortex_E_tensor_separate_importance_v1_honest_negative(), 1),
        ("Atom 2 (topk_composition_refuse_gate_v1 -> measured_mechanism +0)",
         atom_2_topk_composition_refuse_gate_v1_measured_mechanism(), 0),
        ("Atom 3 (pc_cleanup_attractor_v1 -> measured_mechanism +0)",
         atom_3_pc_cleanup_attractor_v1_measured_mechanism(), 0),
        ("Atom 4 (cortex_E_tensor_RETEST_fairness_v2_smoke -> honest_negative +1)",
         atom_4_cortex_E_tensor_RETEST_fairness_v2_smoke_honest_negative(), 1),
        ("Atom 5 (META_RULE_F retrieval-success importance magnitude-coupled +0)",
         atom_5_meta_rule_F_retrieval_success_importance_magnitude_coupled(), 0),
    ]

    cumulative_delta = 0
    for label, atom, delta in atoms:
        print(f"\n--- {label} ---")
        print(f"  qualified_id = {atom.corpus.value}::{atom.id[:80]}...")
        print(f"  kind         = {atom.kind.name}")
        print(f"  delta        = {delta}")

        # Idempotency check via fresh-load
        ps_check = PartitionedStore(STORE_ROOT)
        existing_ids = {a.id for a in ps_check.all_atoms()}
        if atom.id in existing_ids:
            print(f"  IDEMPOTENT-SKIP: atom id already in Store; skipping add_atom")
        else:
            print(f"  Adding atom to Store...")
            ps.add_atom(atom)
            # Verify load
            ps_verify = PartitionedStore(STORE_ROOT)
            verify_ids = {a.id for a in ps_verify.all_atoms()}
            assert atom.id in verify_ids, f"FAIL: atom {atom.id} not in Store after add"
            print(f"  Store verify: atom present")

        # Compute expected CERT N after this atom (use base pre-cert from first run)
        expected_post_cert = pre_cert_base + cumulative_delta + delta

        # Ledger row
        ledger_row = {
            "ts": float(time.time()),
            "op": "cert_ruling",
            "atom_id": f"{atom.corpus.value}::{atom.id}",
            "cert_status": atom.metadata.get("cert_status", "custom"),
            "cert_class": atom.metadata.get("cert_class", "discipline_meta"),
            "verified_off_data": True,
            "atomized_by": atom.metadata.get(
                "atomized_by",
                "skunkworks_landed_vet_wave1_4cell_plus_w16_smoke_2026-06-26",
            ),
            "cell_commit": atom.metadata.get("cell_commit", "n/a"),
            "verdict": atom.metadata.get("verdict", "unspecified"),
            "cert_increment_delta": delta,
            "cv": None,
            "referent_pointer": {
                "notes_path": atom.metadata.get("referent_notes_path", NOTES_PATH),
                "metrics_path": atom.metadata.get("referent_metrics_path"),
                "atom_qualified_id": f"{atom.corpus.value}::{atom.id}",
            },
            "supersedes": None,
            "note": f"skunkworks_landed_vet_wave1_4cell_plus_w16_smoke_{atom.metadata.get('verdict_subclass', 'meta_rule_F')}",
        }
        # The ledger writer's PRE snapshot reads the live Store, which already
        # reflects this atom's add. So expected_cert_n_pre == expected_post_cert.
        rh = append_cert_ledger_row(
            ledger_row,
            expected_cert_n_pre=expected_post_cert,
            expected_cert_n_post=expected_post_cert,
        )
        print(f"  Ledger row appended: hash={rh}")

        cumulative_delta += delta

    # A5 POST: final verify
    print("\n[A5 POST] Final verify...")
    ps_post = PartitionedStore(STORE_ROOT)
    post_cert = sum(
        1 for a in ps_post.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    post_total = sum(1 for _ in ps_post.all_atoms())
    print(f"  CERT N (post)  = {post_cert}  (delta from base {pre_cert_base} = +{post_cert - pre_cert_base})")
    print(f"  Atom total     = {post_total}  (delta from this-run pre {pre_total} = +{post_total - pre_total})")
    print(f"  Expected delta = +{cumulative_delta} CERT, +5 atoms (cumulative across re-runs)")

    assert post_cert == pre_cert_base + cumulative_delta, (
        f"A5 POST: CERT N drift: base_pre={pre_cert_base} post={post_cert} expected_delta={cumulative_delta}"
    )

    print("\n" + "=" * 80)
    print("SKUNKWORKS ATOMIZE COMPLETE")
    print(f"  Pre  CERT N: {pre_cert}")
    print(f"  Post CERT N: {post_cert}")
    print(f"  Atoms added: 5 (4 experiment + 1 META rule)")
    print(f"  Ledger rows: 5 cert_ruling appended")
    print(f"  Verdicts: 2 honest_negative (+1 each), 2 measured_mechanism (+0), 1 meta_rule (+0)")


if __name__ == "__main__":
    main()
