#!/usr/bin/env python3
"""Skunkworks verify-off-data audit on 2 Wave 2H drill cells of 2026-06-27 evening.

USER directive 2026-06-27 ~17:35 PDT:
  "skunktest tonegawa v3 obviously drill 3x; skunktest stc v2 and v2 drill 3x"

Both cells are FOLLOW-UPs to morning Wave 2 audit (5cell_wave2_mechanism_null_audit):
  - tonegawa_v3_BUNDLED follows from tonegawa_v2 INDETERMINATE (v3 = bundled-regime fix)
  - stc_v2_two_phase follows from stc_v1 FAIRNESS_VIOLATION (v2 = 2-phase continual-learning fix)

VERDICTS (verified off raw per-arm metrics; NOT framing-from-verdict-msg):

1. exp_cortex_schema_tonegawa_sparse_ensemble_v3_BUNDLED -> INDETERMINATE_NEEDS_DIAGNOSTIC
   (XOR_BUNDLE_INCOMPATIBLE_WITH_SPARSE_K_WTA_codes_only_one_bundle_op_tested)
   - Per-arm verified: ARM_PROTOTYPE_CENTROID_BUNDLED recall@1_K25=0.836
     ARM_TONEGAWA_SPARSE_K20_BUNDLED=0.040 ARM_DIAG_RANDOM_SPARSE_BUNDLED=0.044
   - TONE/PROTO ratio = 0.048 (TONE 20.9x worse); DIAG/TONE = 1.10 (random
     ~= structured) -> structure NOT load-bearing AT THIS BUNDLE_OP
   - All 3 arms collapse to cap@95=0.0 at K=100; cell-author's claim "both
     collapse at K=100" verified -- bundling capacity exhausted in regime
   - CRITICAL UNTESTED: cell only tested XOR-bind (`S = sum_k XOR(schema_id_k,
     sparse_code_k)`). XOR-bind designed for dense bipolar; sparse k-WTA codes
     are ~98% zero so XOR-of-two-sparse is ~96% zero -> unbind near-degenerate.
     ADDITIVE-bind variant NOT TESTED. This rules out XOR-bundled-Tonegawa
     as a substrate-native mechanism, but doesn't rule out:
       (a) additive-bind variant (sum + cleanup instead of XOR-unbind)
       (b) sparse-aware bundle op (Plate's compress-then-bundle)
       (c) coarse-grained position binding (smaller K-WTA support)
   - Author framing "HRR-bundled sparse encoding genuinely uncompetitive" too
     strong -- only ONE bundle op tested. The right framing: "XOR-bundling
     specifically is incompatible with sparse k-WTA at K=25 bundling depth;
     additive-bind variant required to fully characterize Tonegawa-vs-Prototype
     in shared-bank regime."
   - K_SWEEP=[25, 100] does verify cell-author's "K=25 too small to favor sparse"
     concern is NOT the issue at K=100 -- both regimes collapse equivalently
   - Single-seed smoke; spec valid for design-failure ruling but needs n_seeds>=3
     before any tier promotion
   - 3X DRILL spec: (a) re-author with ADDITIVE bundle: `S = sum_k (schema_id_k +
     sparse_code_k)`, recall via top-K cleanup against schema-id codebook;
     (b) repeat at K=[10, 25, 50] sparse-load depth; (c) n_seeds=5 minimum

2. exp_stc_tag_and_capture_v2_two_phase_continual_learning -> TEST_DESIGN_FAILURE
   (INTERFERENCE_REGIME_NEVER_MANIFESTS_baseline_A_after_0p999_substrate_holds_both_A_and_B)
   - Per-arm verified at 2 seeds (11/13): baseline_A_after=0.999 (mean over 2 seeds
     0.9991); stc_A_after=0.996; random_tag_A_after=0.996; decay_A_after=0.993
   - A_lift_over_baseline = -0.003 (STC SLIGHTLY WORSE than baseline) ;
     A_lift_over_random_tag = +0.0003 (essentially zero)
   - recall_B_after across all 4 arms in [0.987, 0.998] -- phase-B writes
     succeed completely without disturbing phase-A. The substrate at this
     configuration (N=1024 NCAT=10 NVAR=5 alpha=0.0098) is far below capacity
     and B-writes coexist additively with A-writes without overwrite
   - tag_fraction=0.080 IS in HP_tag=[0.05,0.15] band -- the v1->v2 tag fix
     worked structurally; cell-author's framing on this point verified
   - DEEPER ISSUE (cell-author identified, Skunkworks confirms): there's NO
     INTERFERENCE TO SELECTIVELY RESCUE from. STC's mechanism is "selectively
     preserve some weights during catastrophic-forgetting overwrite" -- if
     overwrite doesn't happen, mechanism has no headroom
   - cell-author's surfaced fix "ETA_CAPTURE=0.20 lets A and B coexist
     additively; needs ETA_CAPTURE=1.0 or W_slow normalization" is ONE option
     but doesn't address root cause: substrate write-mode + capacity-headroom
     combination means single B-pattern doesn't displace A-patterns
   - 3X DRILL spec: (a) NCAT_phase1 + NCAT_phase2 >= 200 (push to substrate
     capacity ~N/proto_noise^2 ~ 1024/0.72 ~ 1400 patterns; current 50 patterns
     is 4pct of capacity); (b) add W_slow normalization between phases (||W||_F
     held constant); (c) ETA_CAPTURE=1.0 with consolidation pulses interleaved
   - Mechanism status: UNKNOWN -- NOT a substrate null; baseline-no-interference
     means cell never tested what it intended to test

META CLAIM VETTING:

Research-surfaced META claim (Wave 2H wrap-up):
  "Wave 2 mechanism tests in our substrate's prototype-classification task are
   subject to deeper saturation issues that 4 separate cell-author fixes can't
   resolve at the cell level. Pattern recommendation: pivot to non-classification
   readouts (capacity@retrieval, interference-fraction-measured, signal-to-
   crosstalk ratio)."

Skunkworks verdict: PARTIALLY_SUPPORTED_BUT_OVERGENERALIZED. Atomize with the
nuance, NOT the over-generalized version.

Supporting evidence (5 cells with saturation-related failure of today's 9):
  - tonegawa_v2: NO_SCHEMA r@k=1.000 (saturated baseline)
  - stc_v1: all 4 arms tied at 0.953 (saturated baseline)
  - stc_v2: baseline_A_after=0.999 (saturation prevents interference regime)
  - cortex_E_tensor_v1: rec_old=1.000 across E_GATED and RANDOM (saturated)
  - tonegawa_v3 PROTOTYPE: 0.836 (just-below saturation but TONE 0.040 catastrophic)

Counter-evidence (claim too strong):
  - tonegawa_v3 DID move past v2's design issue (bundled-bank regime); just hit
    a NEW design issue (XOR-bind incompatible with sparse codes). v3 IS a
    cell-level fix that resolved the v2 issue, just exposed a different one.
  - stc_v2 DID move past v1's fairness-violation; just exposed the deeper "no
    interference regime to test in" problem.
  - mh_revival_feature: classification readout HIT lift +0.127, just under +0.15
    threshold -- proves classification readout CAN work if regime is right
  - soft_topK_cleanup HARD_FAIL: BASELINE_top1@hop5=0.001, not saturated -- FLOOR
    collapse (different failure mode)

Three distinct root-cause families conflated in Research's META framing:
  (A) BASELINE-SATURATION: regime too easy; everything wins; no readout headroom
      (tonegawa_v2 NO_SCHEMA, stc_v1, cortex_E_tensor_v1, stc_v2 baseline_A)
  (B) INTERFERENCE-REGIME-ABSENT: substrate writes additively, B doesn't displace
      A, mechanism has no scenario to demonstrate value (stc_v2 specifically)
  (C) BUNDLE-OP-INCOMPATIBLE: chosen superposition op (XOR for sparse codes)
      breaks the mechanism's algebraic premise (tonegawa_v3 specifically)

Non-classification readout recommendation:
  - Would HELP (A): capacity@95 instead of recall@K can break saturation ties
    (tonegawa_v2 capacity@95 showed 17x loss that recall@K hid)
  - Would NOT HELP (B): no readout cures absent-interference-regime; need to
    push regime to substrate capacity OR add explicit normalization
  - Would NOT HELP (C): no readout cures algebraic-incompatibility of bundle op
    with code structure; need additive-bind or sparse-aware bundle op

Honest framing: cell-author fixes RESOLVED Wave 2 design issues sequentially
but each fix uncovered the NEXT lower layer of design issue (saturation -> bundle-
regime-mismatch -> XOR-bind-incompatible). The "deeper saturation" framing is
half-right; the actual pattern is "sequential design-issue layers". The non-
classification-readout pivot is a GOOD partial fix for family (A) but doesn't
address (B) or (C).

3X DRILL on META: verify against any future Wave 2 cells (e.g., when stc_v3 or
tonegawa_v4 lands) whether the next layer is still saturation OR is a different
root cause family. If 3+ consecutive Wave 2 cells fail with family (A) (saturation
specifically) AND cell-author fixes can't move past saturation, the strong form
of the META claim becomes supportable. Until then, atomize the NUANCED version.

ATOMIZATION PLAN (this script, idempotent, A5-gated):
1. INDETERMINATE_NEEDS_DIAGNOSTIC tonegawa_v3_BUNDLED (XOR-bundle incompatible
   with sparse k-WTA; only one bundle op tested; additive variant required)
2. TEST_DESIGN_FAILURE stc_v2 (interference regime absent; baseline_A_after=0.999;
   substrate writes additively without displacement at NCAT=10)
3. META_NUANCED_PARTIALLY_SUPPORTED_three_root_cause_families wave2_failure_pattern
   (saturation + interference-absent + bundle-op-incompatible; non-classification-
   readout pivot helps family A only)

NO chain-grade tier; NO cert_ledger increment. Methodology / discipline atoms only.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path("d:/AI/hd-instrument").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


STORE_ROOT = Path("d:/AI/hd-instrument/data/substrate_index")
SOURCE_TAG = "skunkworks_verify_off_data_tonegawa_v3_stc_v2_plus_META_2026-06-27_evening"


def _add_safely(atom: Atom, note: str) -> bool:
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"SKIP (idempotent): {atom.id[:90]}")
        return True
    print(f"ADDING: {atom.id[:90]}")
    ps.add_atom(atom, source=SOURCE_TAG, note=note)
    ps2 = PartitionedStore(STORE_ROOT)
    atoms = list(ps2.all_atoms())
    found = next((a for a in atoms if a.id == atom.id), None)
    if found is None:
        print(f"  FAIL: not present post-add")
        return False
    if found.tier != atom.tier or found.kind != atom.kind:
        print(f"  FAIL: tier/kind drift on round-trip")
        return False
    print(f"  PASS: round-trip clean")
    return True


def atom_tonegawa_v3() -> Atom:
    return Atom(
        id=("AUDIT_INDETERMINATE_NEEDS_DIAGNOSTIC_cortex_schema_tonegawa_sparse_ensemble_v3_BUNDLED"
            "_XOR_BUNDLE_OP_INCOMPATIBLE_WITH_SPARSE_K_WTA_codes_PROTOTYPE_BUNDLED_recall_at_1_K25"
            "_0p836_TONEGAWA_K20_BUNDLED_0p040_DIAG_RANDOM_SPARSE_BUNDLED_0p044_TONE_OVER_PROTO_0p048"
            "_DIAG_OVER_TONE_1p10_random_essentially_matches_structured_capacity_at_95_all_zero_at_K100"
            "_only_ONE_bundle_op_XOR_tested_additive_bind_variant_required_3x_drill_2026-06-27"),
        name=("INDETERMINATE_NEEDS_DIAGNOSTIC tonegawa_v3_BUNDLED: XOR-bundle incompatible with sparse "
              "k-WTA codes (98pct zeros -> XOR-unbind near-degenerate); PROTO=0.836 TONE=0.040 "
              "DIAG=0.044 ratio_DIAG_over_TONE=1.10; only ONE bundle op tested; additive-bind variant required"),
        description=(
            "Wave 2H DRILL on tonegawa_v2 INDETERMINATE (morning audit). v3 implements bundled-bank "
            "regime as v2 audit specified. Verify-off-data finding: per-arm recall@1_K25 (single "
            "seed=7, N_DIM=1024, K_SCHEMAS=1024, K_SPARSE=20, BCC=0.30, WCN=0.60, K_SWEEP=[25,100]) "
            "shows ARM_PROTOTYPE_CENTROID_BUNDLED=0.836, ARM_TONEGAWA_SPARSE_K20_BUNDLED=0.040, "
            "ARM_DIAG_RANDOM_SPARSE_BUNDLED=0.044. Ratios: TONE/PROTO=0.048 (TONE 20.9x worse); "
            "DIAG/TONE=1.10 (random essentially matches structured sparse) -> structure NOT "
            "load-bearing AT THIS BUNDLE_OP. Capacity@95 all arms = 0.0 across K_SWEEP=[25,100] "
            "(no arm reaches 0.95 recall after bundling -- bundling capacity exhausted in this "
            "regime). Cell-author's claim 'both collapse at K=100' is verified, but the framing "
            "'HRR-bundled sparse encoding genuinely uncompetitive vs dense centroid' is TOO STRONG "
            "because only XOR-bundle was tested. Architecture issue: cell defines S = sum_k "
            "XOR(schema_id_k, sparse_code_k); XOR-bind is HRR-designed for DENSE bipolar codes "
            "(roughly equal +1/-1 mass). Sparse k-WTA codes with K_SPARSE=20 out of N=1024 are "
            "~98pct zero. XOR of two ~98pct-zero vectors is ~96pct zero (since 0 XOR 0 = 0) -> "
            "the bundled superposition S becomes ~96pct zero too -> unbinding via XOR(query, S) "
            "is near-degenerate. The mechanism's algebraic premise (XOR-unbinding distinguishes "
            "schema-bound from noise) breaks when input vectors don't have HRR's required statistics. "
            "v3 result IS a clean diagnostic: it rules out XOR-bundled-Tonegawa as a substrate-"
            "native mechanism in this regime, but does NOT rule out: (a) additive-bind variant "
            "`S = sum_k (schema_id_k + sparse_code_k)` with cleanup; (b) Plate's compress-then-"
            "bundle for sparse codes; (c) coarse-grained-position binding at smaller K_WTA "
            "support. K_SWEEP=[25,100] verifies cell-author's 'K=25 too small to favor sparse' "
            "concern is NOT the issue at K=100 -- both regimes collapse equivalently. n_seeds=1 "
            "smoke; mechanism status: UNKNOWN, NOT proven-null. 3X DRILL spec: (a) re-author "
            "with additive bundle op; (b) sweep K=[10,25,50] sparse-load depth; (c) n_seeds=5 "
            "minimum; (d) recall via top-K cleanup against schema-id codebook (no XOR-unbinding). "
            "Mechanism remains a candidate for substrate-native sparse-schema-ensemble class until "
            "additive-bind variant is tested and characterized."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 254,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "bundle_op_algebraic_incompatibility_XOR_with_sparse_k_WTA_codes",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_cortex_schema_tonegawa_sparse_ensemble_v3_BUNDLED/metrics.json",
            "key_per_arm_values": {
                "prototype_centroid_bundled_recall_at_1_K25": 0.836,
                "tonegawa_sparse_K20_bundled_recall_at_1_K25": 0.040,
                "diag_random_sparse_bundled_recall_at_1_K25": 0.044,
                "tone_over_proto_ratio": 0.048,
                "diag_over_tone_ratio": 1.10,
                "capacity_at_95_prototype": 0.0,
                "capacity_at_95_tonegawa": 0.0,
                "capacity_at_95_diag": 0.0,
                "K_sparse": 20,
                "K_sweep": [25, 100],
                "N_dim": 1024,
                "n_seeds_smoke": 1,
            },
            "untested_variants_blocking_definitive_null": [
                "additive_bind_sum_k_schema_id_plus_sparse_code_with_cleanup",
                "Plate_compress_then_bundle_for_sparse_codes",
                "coarse_grained_position_binding_smaller_K_WTA_support",
            ],
            "structural_reason_xor_incompatible": (
                "sparse_k_WTA_98pct_zero_then_XOR_of_two_sparse_is_96pct_zero"
                "_unbind_near_degenerate_HRR_requires_dense_bipolar_statistics"
            ),
            "three_x_drill_required": True,
            "three_x_drill_spec": (
                "additive_bundle_op_plus_K_sweep_10_25_50_plus_n_seeds_5"
                "_plus_top_K_cleanup_recall_against_schema_id_codebook"
            ),
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "META_RULE_K_smoke_must_FIRE_discriminator",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
                "AUDIT_INDETERMINATE_NEEDS_DIAGNOSTIC_cortex_schema_tonegawa_v2_morning_audit_2026-06-27",
            ],
        },
    )


def atom_stc_v2() -> Atom:
    return Atom(
        id=("AUDIT_TEST_DESIGN_FAILURE_stc_tag_and_capture_v2_two_phase_continual_learning"
            "_INTERFERENCE_REGIME_NEVER_MANIFESTS_baseline_A_after_0p999_substrate_writes_additively"
            "_NCAT_10_NVAR_5_alpha_0p0098_is_4pct_of_substrate_capacity_B_does_not_displace_A_no_"
            "mechanism_headroom_to_demonstrate_selective_rescue_tag_fraction_0p080_in_band_v1_v2_tag"
            "_fix_worked_structurally_but_exposed_deeper_regime_issue_3x_drill_NCAT_200_or_W_slow_norm_2026-06-27"),
        name=("TEST_DESIGN_FAILURE stc_v2_two_phase: interference regime never manifests; "
              "baseline_A_after=0.999 (B doesn't displace A at 4pct-of-capacity regime); STC has "
              "no scenario to demonstrate selective rescue; mechanism UNKNOWN not null; v3 3x drill required"),
        description=(
            "Wave 2H DRILL on stc_v1 FAIRNESS_VIOLATION (morning audit). v2 implements 2-phase "
            "continual-learning protocol as v1 audit specified. Verify-off-data finding: per-arm "
            "raw values across 2 seeds (11/13) at N=1024 NCAT=10 NVAR=5 proto_noise=0.85 alpha=0.0098 "
            "J_capture=5 K_decay=3 theta_pct=92.0 eta_fast=1.00 eta_cap=0.20. Phase-A retention "
            "across arms: baseline_no_stc_A_after=0.9991 (mean over 2 seeds); stc_tagged_A_after"
            "=0.9960; random_tag_matched_A_after=0.9956; diag_stc_decay_A_after=0.9930. Phase-B "
            "acquisition: all 4 arms reach recall_B_after in [0.987, 0.998] (B-writes succeed "
            "completely). A_lift_over_baseline = -0.0032 (STC slightly WORSE than baseline for A "
            "retention -- direction of lift wrong); A_lift_over_random_tag = +0.0003 (essentially "
            "zero -- STC vs random-tag indistinguishable). Tag fraction = 0.0800 in HP_tag=[0.05,"
            "0.15] band (the v1->v2 tag-fraction-fix worked structurally; cell-author framing on "
            "this point verified). CORE DESIGN FAILURE (cell-author identified, Skunkworks "
            "confirms via raw-data audit): there is NO INTERFERENCE TO SELECTIVELY RESCUE FROM. "
            "STC's mechanism is 'selectively preserve some weights during catastrophic-forgetting "
            "overwrite by tagging strong synapses during phase A so phase-B writes spare them'. "
            "If catastrophic forgetting doesn't happen (because substrate writes additively and "
            "is at 4pct of capacity), then the mechanism has no scenario to demonstrate value. "
            "Substrate write capacity estimate: M_max ~ N / proto_noise^2 ~ 1024/0.72 ~ 1400 "
            "patterns; current 50 patterns (NCAT=10 x NVAR=5) is 4pct of capacity. At 4pct of "
            "capacity, B-writes coexist additively with A-writes without overwrite -- cell's "
            "verdict_msg 'INTERFERENCE_REGIME_BROKEN: baseline_A_after=0.999 > 0.30' correctly "
            "diagnoses this. Cell-author's surfaced fix ('ETA_CAPTURE=0.20 lets A and B coexist "
            "additively; needs ETA_CAPTURE=1.0 or W_slow normalization') is one option but doesn't "
            "address the root cause: at this capacity regime + write mode, single B-pattern "
            "doesn't displace A-patterns regardless of ETA_CAPTURE. Mechanism status: UNKNOWN; "
            "NOT a substrate null; does NOT count against any META claim about W-update-rule. "
            "3X DRILL spec: (a) push NCAT_phase1 + NCAT_phase2 >= 200 (force regime to substrate "
            "capacity); (b) add W_slow normalization between phases (||W||_F held constant after "
            "B-writes); (c) ETA_CAPTURE=1.0 with consolidation-pulses interleaved; (d) explicit "
            "baseline_no_stc_A_after_target=[0.40, 0.70] in HP gate (HARD_FAIL if baseline_A_after"
            ">0.70, telling cell-author the regime didn't bite)."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 255,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "interference_regime_never_manifests_substrate_at_4pct_capacity_additive_write_mode",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_stc_tag_and_capture_v2_two_phase_continual_learning/metrics.json",
            "key_per_arm_values": {
                "baseline_no_stc_A_after": 0.9991,
                "stc_tagged_A_after": 0.9960,
                "random_tag_matched_A_after": 0.9956,
                "diag_stc_decay_A_after": 0.9930,
                "baseline_no_stc_B_after": 0.9983,
                "stc_tagged_B_after": 0.9878,
                "A_lift_over_baseline": -0.0032,
                "A_lift_over_random_tag": +0.0003,
                "tag_fraction": 0.0800,
                "HP_tag_band": [0.05, 0.15],
                "HP_baseline_A_after_ceiling": 0.30,
                "n_seeds": 2,
                "N_dim": 1024,
                "NCAT": 10,
                "NVAR": 5,
                "patterns_total": 50,
                "estimated_substrate_capacity": 1400,
                "patterns_pct_of_capacity": 0.036,
            },
            "v1_to_v2_fix_landed_structurally": "tag_fraction_in_HP_band_0p05_to_0p15_at_0p080",
            "v2_exposed_deeper_layer": "interference_regime_never_manifests_substrate_at_4pct_capacity",
            "three_x_drill_required": True,
            "three_x_drill_spec": (
                "NCAT_phase1_plus_NCAT_phase2_at_least_200_force_substrate_to_capacity"
                "_AND_W_slow_normalization_between_phases_AND_ETA_CAPTURE_1p0_with_consolidation_pulses"
                "_AND_explicit_HP_baseline_A_after_ceiling_0p70_hard_fail_if_regime_didnt_bite"
            ),
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "META_RULE_K_smoke_must_FIRE_discriminator",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
                "AUDIT_FAIRNESS_VIOLATION_stc_tag_and_capture_v1_smoke_morning_audit_2026-06-27",
            ],
        },
    )


def atom_meta_nuanced() -> Atom:
    return Atom(
        id=("AUDIT_META_NUANCED_PARTIALLY_SUPPORTED_wave2_failure_pattern_three_root_cause_families"
            "_NOT_one_deeper_saturation_family_A_BASELINE_SATURATION_family_B_INTERFERENCE_REGIME"
            "_ABSENT_family_C_BUNDLE_OP_ALGEBRAIC_INCOMPATIBILITY_non_classification_readout_pivot"
            "_helps_family_A_only_does_not_help_B_or_C_cell_author_fixes_DO_resolve_layers_each_fix"
            "_uncovers_next_design_issue_strong_form_of_META_overgeneralized_3x_drill_3_consecutive_"
            "wave2_family_A_failures_unfixable_required_before_strong_form_atomizable_2026-06-27"),
        name=("META_NUANCED_PARTIALLY_SUPPORTED wave2 failure pattern: THREE distinct root-cause "
              "families (saturation / interference-absent / bundle-op-incompatible) NOT one; "
              "non-classification-readout pivot helps family A only; strong form of META overgeneralized"),
        description=(
            "Research-surfaced META claim (Wave 2H wrap-up): 'Wave 2 mechanism tests in our "
            "substrate's prototype-classification task are subject to deeper saturation issues "
            "that 4 separate cell-author fixes can't resolve at the cell level. Pattern "
            "recommendation: pivot to non-classification readouts (capacity@retrieval, interference-"
            "fraction-measured, signal-to-crosstalk ratio).' Skunkworks vetting (verify-off-data "
            "across 9 today's Wave 2 cells): PARTIALLY_SUPPORTED_BUT_OVERGENERALIZED. The "
            "saturation pattern IS real (5 cells: tonegawa_v2 NO_SCHEMA r@k=1.000, stc_v1 all-4-"
            "arms-tied-0.953, stc_v2 baseline_A_after=0.999, cortex_E_tensor_v1 rec_old=1.000, "
            "tonegawa_v3 PROTOTYPE=0.836 just-below); the 'cell-author fixes can't resolve' claim "
            "is TOO STRONG (tonegawa_v3 DID resolve v2's bank-config mismatch by moving to "
            "bundled-bank, just exposed a NEW layer issue with XOR-bundle-incompatible-with-sparse; "
            "stc_v2 DID resolve v1's fairness-violation, just exposed deeper interference-regime-"
            "absent issue). Counter-evidence: mh_revival_feature got LIFT +0.127 just under +0.15 "
            "threshold, proving classification readout CAN work; soft_topK_cleanup HARD_FAIL was "
            "FLOOR collapse (BASELINE_top1@hop5=0.001) NOT saturation -- different failure mode. "
            "Three distinct root-cause families CONFLATED in Research's META framing: (A) "
            "BASELINE-SATURATION (regime too easy, no readout headroom): tonegawa_v2 NO_SCHEMA, "
            "stc_v1, cortex_E_tensor_v1, stc_v2 baseline_A; (B) INTERFERENCE-REGIME-ABSENT "
            "(substrate writes additively, B doesn't displace A): stc_v2 specifically; (C) "
            "BUNDLE-OP-INCOMPATIBLE (chosen superposition op breaks algebraic premise): tonegawa_v3 "
            "specifically. Non-classification-readout recommendation: HELPS family (A) (capacity@95 "
            "instead of recall@K broke saturation ties in tonegawa_v2 to reveal 17x cap loss); "
            "does NOT help family (B) (no readout cures absent-interference-regime; need regime "
            "push to capacity or explicit W normalization); does NOT help family (C) (no readout "
            "cures algebraic-incompatibility; need additive-bind or sparse-aware bundle op). "
            "Honest framing: cell-author fixes RESOLVE Wave 2 design issues sequentially but each "
            "fix uncovers the next lower layer (fairness -> bundle-regime -> interference-regime "
            "-> bundle-op-compatibility). The 'deeper saturation' framing is half-right; actual "
            "pattern is 'sequential design-issue layers'. Non-classification-readout pivot is GOOD "
            "partial fix for family (A) but isn't a panacea. 3X DRILL META spec: verify against "
            "next 3 Wave 2 cells (stc_v3, tonegawa_v4, plus one new mechanism). If 3 consecutive "
            "fail with family (A) SPECIFICALLY AND cell-author fixes can't move past saturation, "
            "the STRONG form of META becomes supportable. Until then, atomize NUANCED version "
            "only. DO NOT atomize the over-generalized 'deeper saturation issues that fixes can't "
            "resolve' framing -- it's a CONFLATION error."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 256,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "meta_claim_overgeneralized_three_root_cause_families_conflated",
            "verified_off_data": True,
            "evidence_cells_audited_today": 9,
            "evidence_cells_supporting_saturation_family_A": [
                "exp_cortex_schema_tonegawa_sparse_ensemble_v2",
                "exp_stc_tag_and_capture_v1_smoke",
                "exp_stc_tag_and_capture_v2_two_phase_continual_learning",
                "exp_cortex_E_tensor_separate_importance_v1",
                "exp_cortex_schema_tonegawa_sparse_ensemble_v3_BUNDLED",
            ],
            "evidence_cells_supporting_interference_absent_family_B": [
                "exp_stc_tag_and_capture_v2_two_phase_continual_learning",
            ],
            "evidence_cells_supporting_bundle_op_incompatible_family_C": [
                "exp_cortex_schema_tonegawa_sparse_ensemble_v3_BUNDLED",
            ],
            "counter_evidence_classification_readout_can_work": [
                "exp_mh_revival_feature_regime_diagnostic_v1_lift_plus_0p127_just_under_threshold",
            ],
            "counter_evidence_different_failure_mode_not_saturation": [
                "exp_soft_topK_cleanup_distribution_preserving_v1_FLOOR_collapse_baseline_0p001",
            ],
            "non_classification_readout_pivot_applicability": {
                "family_A_saturation": "HELPS (capacity@95 broke tonegawa_v2 ties to reveal 17x loss)",
                "family_B_interference_absent": "DOES_NOT_HELP (no readout cures regime issue; need NCAT push)",
                "family_C_bundle_op_incompatible": "DOES_NOT_HELP (no readout cures algebraic incompatibility)",
            },
            "strong_form_of_META_requires_evidence": (
                "3_consecutive_wave2_cells_failing_with_family_A_SPECIFICALLY_AND_cell_author"
                "_fixes_unable_to_move_past_saturation"
            ),
            "three_x_drill_required": True,
            "three_x_drill_spec": (
                "verify_against_next_3_wave2_cells_stc_v3_tonegawa_v4_one_new_mechanism"
                "_if_3_consecutive_family_A_unfixable_strong_form_atomizable"
            ),
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "META_RULE_T_per_arm_metric_verification_required_before_META_atomization",
                "META_RULE_K_smoke_must_FIRE_discriminator",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
                "AUDIT_META_CLAIM_INDETERMINATE_substrate_consolidation_favors_store_transfer_over_W_update_rule_morning_audit_2026-06-27",
            ],
        },
    )


def main() -> int:
    print(f"Source tag: {SOURCE_TAG}")
    print(f"Store root: {STORE_ROOT}")
    print()
    results = []
    atoms_to_add = [
        (atom_tonegawa_v3(), "INDETERMINATE_NEEDS_DIAGNOSTIC tonegawa_v3_BUNDLED (XOR-bundle incompatible with sparse k-WTA; additive variant required) verified"),
        (atom_stc_v2(), "TEST_DESIGN_FAILURE stc_v2 (interference regime never manifests at 4pct of capacity; baseline_A_after=0.999) verified"),
        (atom_meta_nuanced(), "META_NUANCED_PARTIALLY_SUPPORTED wave2 failure pattern: 3 root-cause families not 1; non-classification-readout pivot helps family A only) verified"),
    ]
    for atom, note in atoms_to_add:
        ok = _add_safely(atom, note)
        results.append((atom.id[:80], ok))
    print()
    print("=" * 80)
    print("Summary:")
    n_pass = sum(1 for _, ok in results if ok)
    n_total = len(results)
    print(f"  {n_pass}/{n_total} atoms added/verified")
    for aid, ok in results:
        flag = "OK" if ok else "FAIL"
        print(f"  [{flag}] {aid}")
    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    sys.exit(main())
