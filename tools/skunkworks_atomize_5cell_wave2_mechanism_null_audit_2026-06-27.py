#!/usr/bin/env python3
"""Skunkworks verify-off-data audit on the 5 Wave-2 SMOKE_HARD_FAILs of 2026-06-27 afternoon.

USER directive standing: skunktest every negative for verification + don't accept
a ceiling just because we get bad results + fairness-before-tier (META_RULE_AA inst 248).

Distinguished from morning batch: these had baseline reportedly in fair band -- but
2 of them turned out to have FAIRNESS VIOLATIONS that Research missed, and 3 had
genuine TEST_DESIGN_FAILUREs (density-confound / degenerate-baseline / discriminator-
regime-mismatch) plus 1 HONEST_NEG_REGIME_BOUNDED.

VERDICTS (verified off raw per-arm metrics; NOT framing-from-verdict-msg):

1. exp_engram_dropout_inhibitory_plasticity_v1_smoke -> TEST_DESIGN_FAILURE_CONFIRMED
   (DENSITY_CONFOUND_random_at_0p50_vs_engram_at_0p37_NOT_density_matched)
   - Per-arm verified: baseline_no_mask dens=1.00 cor=0.248; random_mask dens=0.50
     cor=0.186; engram_dropout dens=0.359 cor=0.144. Random has 40% MORE dims
     than engram -- not a controlled A/B. Headline "random beats engram" is a
     density-confound, NOT a selection-rule null.
   - To prove the abs(retrieved * target_proto) median-split selection is bad
     we need EITHER random@density=0.37 OR engram@density=0.50 (or both).
     Cell does neither.
   - Author's surfaced suspect ("selection criterion not extracting pattern-
     discriminative dims better than random") may STILL be true, but this
     cell can't distinguish that from "any 37% density underperforms 50%".

2. exp_hierarchical_3_tier_W_v1_smoke -> HONEST_NEG_REGIME_BOUNDED
   (ULTRASLOW_TIER_INSUFFICIENT_PULSE_BUDGET_AT_SMOKE_N)
   - Per-arm verified: 2-tier old=0.600, 3-tier-no-ultraslow old=0.600,
     3-tier-stability-gated old=0.600 -- exact tie (within 1e-15 precision).
     Baseline single-tier 0.650 new / 0.620 old (ON ceiling exactly; cell
     coded as in-band; Research's claim "above 0.65 ceiling" is WRONG).
   - Drift tier separation IS structural: fast/slow=21.5x slow/ultra=316x.
   - Ultraslow drift magnitude 9.80e-07 is 0.32% of slow drift. At smoke
     pulse budget (10 cycles), ultraslow tier has accumulated essentially
     nothing -- cannot influence readout. This is a REGIME issue not a
     mechanism null: ultraslow needs O(100-1000) pulses to register.
   - Stability gate WORKS (transition fraction 0.548, in target [0,1]).
   - 2x drill: run at N_PULSES>=100 (10x current). If still null -> escalate
     to GENUINE_MECHANISM_NULL.

3. exp_btsp_binary_synapse_v3_sparse_regime_swept_smoke -> TEST_DESIGN_FAILURE_CONFIRMED
   (DEGENERATE_BASELINE_W_eq_0_default_filled_to_plus_1_collapsing_to_constant_matrix)
   - Per-arm verified: BinHeb baseline at fp=0.005 hits 1.000 ACROSS THE
     ENTIRE GRID for ALL fp values. BTSP=0.04 across full 5x5 grid.
   - Independent recompute: at fp=0.005 the pre-binarization W has
     99.30% of entries exactly 0 (sparse outer-product). The post-bin step
     `W_bin = sign(W) + (W==0)*1.0` fills 1,045,015 of 1,048,576 entries
     (99.66%) with +1. W_bin mean = 0.9932. This is NOT a fair baseline
     -- it's a near-constant matrix that the sparse-readout test queries
     exploit via a single dominant direction.
   - Author's framing "BTSP no headroom at literature sparsity" is misleading:
     BinHeb doesn't saturate by literature mechanism -- it COLLAPSES into
     a constant-matrix degeneracy via the zero-default-fill.
   - Fix: change `W_bin = sign(W) + (W==0)*1.0` to `sign(W)` (leave zeros as
     zeros) OR `2*(W>0).astype(float)-1` (consistent bipolar; zeros to -1).
     Then rerun -- BinHeb baseline will be lower and BTSP may show lift.

4. exp_stc_tag_and_capture_v1_smoke -> FAIRNESS_VIOLATION
   (BASELINE_SATURATES_above_HP_baseline_band_0p20_to_0p70_at_0p953)
   - Per-arm verified: baseline_hebbian=0.953 / replay_no_tag=0.953 /
     stc_tagged=0.953 / stc_tagged_decay=0.953. All four arms saturated.
   - Cell's own HF rule fired: "BASELINE_SATURATES: baseline=0.953 >= 0.95"
     -- this is a FAIRNESS gate violation, the cell correctly tagged it.
   - HP_baseline=[0.20, 0.70]; actual baseline 0.953 is well above band.
     N=1024 NCAT=50 NTRAIN=10 alpha=0.0488 + proto_noise=0.85 puts the
     readout in the easy regime where everything saturates.
   - USER's classification placed this in "fairness passed but mechanism
     null" bucket -- INCORRECT. This is fairness FAILED; mechanism status
     UNKNOWN.
   - Author's surface ("needs 2-phase continual-learning rewrite") is the
     right direction -- single-phase readout with this regime can't
     surface tag selectivity. v2 needed.
   - NOT a substrate null; NOT counts against W-update-rule META claim.

5. exp_cortex_schema_tonegawa_sparse_ensemble_v2 -> INDETERMINATE_NEEDS_DIAGNOSTIC
   (CAPACITY_DISCRIMINATOR_DESIGN_NOT_aligned_with_shared_bank_mechanism)
   - Per-arm verified: NO_SCHEMA r@k=1.0 (bank_size=800 raw atoms),
     PROTOTYPE r@k=1.0 (bank_size=100 centroids), TONEGAWA_K20 r@k=0.870
     (bank_size=100 sparse), TONEGAWA_K10 r@k=0.628, DIAG_RANDOM r@k=0.048.
   - capacity@95% differential IS measured: PROTOTYPE=100, TONEGAWA_K20=6.
     That's a 17x capacity LOSS at recall>=0.95 -- TONEGAWA k-WTA sparse
     encoding is paying a steep capacity cost for compression.
   - Cell author's framing "drill TOP-2's capacity@95-recall requires
     BUNDLED memory (all schemas share substrate); v2 implements isolated
     -bank so cosine wins trivially" identifies the design issue: the
     bundled-bank regime where Tonegawa's k-WTA sparse encoding wins is
     not what v2 tests. The cells are in 3 different bank configurations
     making "lift" not directly comparable.
   - Need v3 with: isolated-bank cosine baseline vs Tonegawa-in-bundled-
     bank at matched bank-size after the bundling penalty (capacity@95 in
     BUNDLED regime). Until then, INDETERMINATE.

META_FINDING_substrate_consolidation_favors_store_transfer_over_W_update_rule_selection_v1
  -> INDETERMINATE_PREMATURE (0 of 5 cells provide fair-test evidence)
  - Cell 1 (engram_dropout): density confound -- can't isolate selection rule
  - Cell 2 (3-tier-W): regime-insufficient pulses -- ultraslow tier never registers
  - Cell 3 (BTSP-binary): degenerate baseline -- collapses to constant matrix
  - Cell 4 (STC): fairness-saturated baseline -- mechanism never had a chance
  - Cell 5 (Tonegawa): discriminator-regime mismatch -- v2 in wrong bank config
  - PLUS: hippo->cortex handoff HARD_PASS not independently verified for the
    META claim; would need to confirm it is TRUE store-transfer and not also
    W-rule under the hood.
  - To support META claim, need:
    (A) Re-run cells 1, 2, 3, 5 with design fixes; if STILL null with fair
        baselines + regime + discriminator, those count as W-rule-null evidence.
    (B) Add 2-3 NEW W-rule mechanisms with clean fairness scaffolding (Oja,
        Sanger, OR a clean Hebbian + decay variant); negatives from those would
        count.
    (C) Verify hippo->cortex handoff implementation is truly store-transfer
        (no implicit W-tuning under the hood at consolidation).
  - DO NOT atomize META claim until at least 2 fair-test W-rule-null cells exist.

2X DRILLS TRIGGERED:
  - Cell 2 (3-tier-W) IS the only candidate substrate-null in this batch and it's
    HONEST_NEG_REGIME_BOUNDED -- 2x drill = rerun at N_PULSES>=100 (10x current).
    If still null with sufficient pulse budget, escalate to GENUINE_MECHANISM_NULL.
  - Cells 1, 3, 5 are TEST_DESIGN_FAILUREs -- 2x drill NOT NEEDED at this design;
    require redesign first (density-matched controls / non-degenerate baseline /
    matched-bank-regime discriminator) then re-smoke.
  - Cell 4 is FAIRNESS_VIOLATION -- 2x drill NOT NEEDED; v2 rewrite required first.

ATOMIZATION PLAN (this script, idempotent, A5-gated):
1. TEST_DESIGN_FAILURE_engram_dropout_v1 (audit_lesson; pq=None; META)
2. HONEST_NEG_REGIME_BOUNDED_hierarchical_3_tier_W_v1 (audit_lesson; META)
3. TEST_DESIGN_FAILURE_btsp_binary_synapse_v3_sparse_regime_swept (audit_lesson; META)
4. FAIRNESS_VIOLATION_stc_tag_and_capture_v1 (audit_lesson; META)
5. INDETERMINATE_NEEDS_DIAGNOSTIC_cortex_schema_tonegawa_v2 (audit_lesson; META)
6. META_CLAIM_INDETERMINATE_substrate_consolidation_store_transfer_vs_W_rule_premature (audit_lesson; META)

NO chain-grade tier; NO cert_ledger increment. Methodology / discipline atoms only.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path("d:/AI/hd-instrument").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


STORE_ROOT = Path("d:/AI/hd-instrument/data/substrate_index")
SOURCE_TAG = "skunkworks_verify_off_data_wave2_5cell_mechanism_null_audit_2026-06-27"


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


def atom_engram_dropout() -> Atom:
    return Atom(
        id=("AUDIT_TEST_DESIGN_FAILURE_engram_dropout_inhibitory_plasticity_v1_smoke"
            "_DENSITY_CONFOUND_random_mask_at_0p500_dens_cor_0p186_vs_engram_at_0p359_dens"
            "_cor_0p144_NOT_density_matched_random_has_40pct_more_dims_selection_rule_"
            "abs_retrieved_times_target_proto_median_split_cannot_be_isolated_from_density_"
            "effect_no_random_at_0p37_or_engram_at_0p50_control_arm_2026-06-27"),
        name=("TEST_DESIGN_FAILURE engram_dropout_v1: DENSITY CONFOUND (random@0.50 cor=0.186 "
              "vs engram@0.36 cor=0.144); random has 40% MORE dims; not a controlled A/B; "
              "selection-rule mechanism status UNKNOWN, NOT null"),
        description=(
            "Wave 2 SMOKE_HARD_FAIL (engram_cor=0.145 vs random_cor=0.186 lift=-0.041 at "
            "base_acc=0.480 in fair band). Verify-off-data finding: random_mask_k20 uses "
            "RANDOM_MASK_DENSITY=0.50 (experiments/exp_engram_dropout_inhibitory_plasticity_v1"
            ".py line 121, line 447) while engram_dropout converges to mask_density_end~0.359 "
            "(mean across 2 seeds 7/17). Per-arm raw values: baseline_no_mask dens=1.00 "
            "cor=0.2477 acc=0.480; random_mask_k20 dens=0.5007 cor=0.1863 acc=0.520; "
            "engram_dropout dens=0.3586 cor=0.1436 acc=0.340; engram_dropout_plus_dropin "
            "dens=0.3694 cor=0.1449 acc=0.340. The selection rule "
            "selectivity=abs(retrieved*target_proto) with median-split is being compared "
            "against a random baseline with 40% MORE dims to work with -- not a controlled "
            "A/B test of selection quality. To prove the abs-product-median-split selection "
            "rule is bad we need EITHER random@density=0.37 OR engram@density=0.50 (or "
            "both); cell does neither. Author's surfaced hypothesis (selection criterion "
            "not extracting pattern-discriminative dims better than random) MAY still be "
            "true but cannot be supported by current cell design. dim_overlap_end=0.138 "
            "for engram (low cross-pattern overlap, as engram literature expects) and 0.260 "
            "for random -- engram IS sparser in overlap too, which is the right direction "
            "structurally but still confounded with density. Recommend v2 with arms: "
            "random_mask_at_engram_density (~0.37) + engram_at_random_density (~0.50) for "
            "matched-density comparisons. NO 2x drill of v1 needed; redesign required."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 249,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "density_confound_baseline_not_density_matched",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_engram_dropout_inhibitory_plasticity_v1_smoke/metrics.json",
            "source_code_line": "experiments/exp_engram_dropout_inhibitory_plasticity_v1.py:121,447",
            "key_per_arm_values": {
                "random_mask_dens_end": 0.5007,
                "random_mask_cor": 0.1863,
                "engram_dropout_dens_end": 0.3586,
                "engram_dropout_cor": 0.1436,
                "engram_plus_dropin_dens_end": 0.3694,
                "engram_plus_dropin_cor": 0.1449,
                "baseline_dens_end": 1.0,
                "baseline_cor": 0.2477,
            },
            "design_fix_required": "add_random_at_engram_density_arm_OR_engram_at_random_density_arm_matched_density_AB",
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
            ],
        },
    )


def atom_three_tier_W() -> Atom:
    return Atom(
        id=("AUDIT_HONEST_NEG_REGIME_BOUNDED_hierarchical_3_tier_W_v1_smoke"
            "_ULTRASLOW_TIER_INSUFFICIENT_PULSE_BUDGET_drift_us_9p80e_minus_07"
            "_is_0p32pct_of_slow_drift_at_10_pulses_smoke_baseline_0p650_new_in_band_exactly"
            "_2_tier_old_0p600_3_tier_stab_old_0p600_3_tier_no_us_0p600_exact_tie"
            "_drift_separation_structural_fast_to_slow_21p5x_slow_to_ultra_316x"
            "_stability_gate_works_transition_frac_0p548_2x_drill_run_at_N_PULSES_100_2026-06-27"),
        name=("HONEST_NEG_REGIME_BOUNDED hierarchical_3_tier_W_v1: ultraslow tier accumulates "
              "0.32pct of slow drift at smoke pulse budget (10 cycles); 2x drill = rerun at "
              "N_PULSES>=100 to give ultraslow regime sufficient budget"),
        description=(
            "Wave 2 SMOKE_HARD_FAIL (3tier_stab_old=0.600 vs 2tier_old=0.600 lift=0.000; "
            "base_new=0.650 in band [0.40,0.65] exactly). Verify-off-data finding: per-arm "
            "raw values across 2 seeds (7/17) show EXACT tie between two_tier_fast_slow / "
            "three_tier_no_ultraslow / three_tier_stability_gated at old=0.600 new=0.600 "
            "(within 1e-15 precision). Baseline single_tier_hebbian new=0.650 (boundary of "
            "HP_baseline=[0.40,0.65]) old=0.620 -- baseline_in_band=True reported. (Note: "
            "Research's claim that baseline 'is above 0.65 ceiling' is INCORRECT; cell coded "
            "the boundary as in-band.) Drift tier-separation IS structural: drift_fast="
            "6.67e-3, drift_slow=3.10e-4 (fast/slow=21.5x; HP>=3.0 passed), drift_ultraslow="
            "9.80e-7 (slow/ultra=316x). The ultraslow drift magnitude is 0.32pct of slow "
            "drift -- at smoke N_PULSES=10 the ultraslow tier has accumulated essentially "
            "nothing and cannot affect readout. This is a REGIME-INSUFFICIENT-PULSES issue, "
            "NOT a mechanism null. Stability gate WORKS: transition_slow_to_ultraslow_frac="
            "0.548 (between [0,1]; gate is selecting sign-stable entries as designed). At "
            "N_PULSES=100 (10x current) the ultraslow tier should reach ~3.2pct of slow "
            "magnitude -- enough to test whether it improves old-pattern retention. 2x drill "
            "REQUIRED: rerun with N_PULSES=100, N_CONSOLIDATION_PULSES scaled, otherwise "
            "this is INCONCLUSIVE. If STILL null at N_PULSES=100 with ultraslow tier "
            "accumulating real magnitude -> escalate to GENUINE_MECHANISM_NULL."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 250,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "regime_insufficient_pulse_budget_for_slow_tier",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_hierarchical_3_tier_W_v1_smoke/metrics.json",
            "key_per_arm_values": {
                "baseline_new": 0.650,
                "baseline_old": 0.620,
                "two_tier_old": 0.600,
                "three_tier_no_us_old": 0.600,
                "three_tier_stab_old": 0.600,
                "drift_fast": 6.67e-3,
                "drift_slow": 3.10e-4,
                "drift_ultraslow": 9.80e-7,
                "drift_ratio_fast_slow": 21.5,
                "drift_ratio_slow_ultra": 316.0,
                "transition_slow_to_ultra_frac": 0.548,
            },
            "two_x_drill_required": True,
            "two_x_drill_spec": "rerun_at_N_PULSES_100_10x_smoke_to_give_ultraslow_tier_sufficient_budget",
            "escalation_path": "if_still_null_at_N_PULSES_100 -> GENUINE_MECHANISM_NULL",
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "META_RULE_W_pre_dispatch_alpha_M_over_N_in_0p03_to_0p20_gate",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
            ],
        },
    )


def atom_btsp_v3_sparse() -> Atom:
    return Atom(
        id=("AUDIT_TEST_DESIGN_FAILURE_btsp_binary_synapse_v3_sparse_regime_swept_smoke"
            "_DEGENERATE_BASELINE_BinHeb_at_fp_0p005_W_bin_mean_0p9932_post_bin_step_"
            "W_eq_0_default_fills_1045015_of_1048576_entries_with_plus_1_99p66pct"
            "_collapsing_to_near_constant_matrix_BinHeb_appears_to_saturate_1p000_across"
            "_entire_5x5_grid_BTSP_0p04_no_headroom_NOT_literature_saturation_FIX_change"
            "_W_bin_sign_W_no_zero_default_fill_or_2_times_W_gt_0_minus_1_consistent_bipolar_2026-06-27"),
        name=("TEST_DESIGN_FAILURE btsp_v3_sparse: BinHeb baseline DEGENERATE (W_bin mean "
              "0.9932 = near-constant +1 matrix via W==0 default-fill); appears to saturate "
              "1.000 across grid but is collapse-degeneracy not literature mechanism"),
        description=(
            "Wave 2 SMOKE_HARD_FAIL (max BTSP-BinHeb lift=-0.958 across 5x5 fp/fq grid; "
            "BinHeb=1.000 for all fp; BTSP=0.040 best cell). Verify-off-data finding: "
            "independent recompute of BinHeb W structure at fp=0.005 N_DIM=1024 NCAT=50 "
            "NTRAIN=5 proto_noise=0.85 confirms the pre-binarization W has 99.30pct of "
            "entries EXACTLY zero (sparse top-fp outer-product training). Source line "
            "experiments/exp_btsp_binary_synapse_v3_sparse_regime_swept.py:326 reads "
            "`W_bin = np.sign(W).astype(np.float32) + (W == 0).astype(np.float32) * 1.0` "
            "-- the zero-default-fill puts 1,045,015 of 1,048,576 W_bin entries equal "
            "to +1 (99.66pct). W_bin mean = 0.9932 (would be ~0 for a fair bipolar matrix). "
            "The BinHeb 'baseline' is a degenerate near-constant matrix that the readout "
            "exploits via the sparse-test-query positioning -- it appears to saturate 1.000 "
            "but the result is NOT literature-saturation, it's a TEST DESIGN ARTIFACT from "
            "the zero-default-fill collapse. Author's framing 'BTSP no headroom at literature "
            "sparsity because BinHeb saturates' is misleading -- BinHeb is a broken baseline. "
            "FIX REQUIRED: change line 326 to either (a) `W_bin = np.sign(W).astype(np.float32)` "
            "(leave zeros as zeros; W_bin then has many 0 entries) OR (b) `2*(W>0).astype(np."
            "float32)-1` (consistent bipolar; zeros map to -1 deterministically) OR (c) "
            "fill zeros with random {-1,+1} (Wu-Maass random-init analog). After fix, "
            "BinHeb baseline will sit much lower (likely well below 1.0) and BTSP may show "
            "lift. Until then, mechanism status UNKNOWN, NOT null. NO 2x drill of v3 needed; "
            "v4 with baseline-fix required."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 251,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "degenerate_baseline_zero_default_fill_collapses_to_constant_matrix",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_btsp_binary_synapse_v3_sparse_regime_swept_smoke/metrics.json",
            "source_code_line": "experiments/exp_btsp_binary_synapse_v3_sparse_regime_swept.py:326",
            "broken_line": "W_bin = np.sign(W).astype(np.float32) + (W == 0).astype(np.float32) * 1.0",
            "fix_options": [
                "W_bin = np.sign(W).astype(np.float32) (leave zeros)",
                "W_bin = 2*(W>0).astype(np.float32)-1 (consistent bipolar)",
                "fill_zeros_with_random_pm1 (Wu-Maass-style)",
            ],
            "key_recomputed_values": {
                "W_pre_bin_zero_fraction": 0.9930,
                "W_bin_mean_post_fill": 0.9932,
                "W_bin_plus1_count": 1045015,
                "W_bin_minus1_count": 3561,
                "W_bin_total": 1048576,
            },
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
            ],
        },
    )


def atom_stc_v1_fairness() -> Atom:
    return Atom(
        id=("AUDIT_FAIRNESS_VIOLATION_stc_tag_and_capture_v1_smoke"
            "_BASELINE_SATURATES_at_0p953_well_above_HP_baseline_band_0p20_to_0p70_ceiling"
            "_all_4_arms_tied_at_0p953_baseline_replay_no_tag_stc_tagged_stc_tagged_decay"
            "_cell_own_HF_rule_correctly_fired_BASELINE_SATURATES_USER_classification_in"
            "_fairness_passed_bucket_was_INCORRECT_v2_2_phase_continual_learning_required_2026-06-27"),
        name=("FAIRNESS_VIOLATION stc_tag_and_capture_v1: baseline=0.953 well above HP_baseline "
              "band [0.20,0.70]; cell's own HF rule correctly fired; USER classification "
              "in fairness-passed bucket was INCORRECT; mechanism status UNKNOWN"),
        description=(
            "Wave 2 SMOKE_HARD_FAIL (cell verdict_reason: 'BASELINE_SATURATES: baseline=0.953 "
            ">= 0.95'). Verify-off-data finding: per-arm raw values across 2 seeds (11/13) "
            "show baseline_hebbian=0.9534 / replay_no_tag=0.9533 / stc_tagged=0.9533 / "
            "stc_tagged_decay=0.9533. All 4 arms tied within 1e-4 at 0.953. fraction_tagged "
            "=0.535 (out of HP_tag=[0.05,0.30] band, well above), fraction_captured=1.000. "
            "Cell's own FAIRNESS gate fired the HARD_FAIL: HP_baseline=[0.20,0.70] is the "
            "stated fair-baseline band; observed 0.953 is 0.253 above the ceiling. "
            "Configuration N=1024 NCAT=50 NTRAIN=10 alpha=0.0488 proto_noise=0.85 puts the "
            "readout in the easy regime where everything saturates and no mechanism can "
            "show lift. USER's classification ('fairness gate passed but mechanism null') "
            "is INCORRECT -- this batch had the fairness baseline FAIL. Author's surfaced "
            "framing ('needs 2-phase continual-learning rewrite: initial readout + post-"
            "consolidation readout') is the right diagnosis: single-phase readout in this "
            "regime cannot surface tag selectivity. v2 with continual-learning protocol "
            "required (NCAT_phase1=25 then NCAT_phase2=25 interleaved with consolidation "
            "pulses; readout at both phases). Mechanism status: UNKNOWN -- NOT a substrate "
            "null; does NOT count against W-update-rule META claim. NO 2x drill of v1 "
            "needed; v2 redesign required."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 252,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "fairness_baseline_violation_above_HP_band_ceiling",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_stc_tag_and_capture_v1_smoke/metrics.json",
            "fairness_gate_fired": "BASELINE_SATURATES_above_0p95_when_HP_baseline_ceiling_0p70",
            "key_per_arm_values": {
                "baseline_hebbian": 0.9534,
                "replay_no_tag": 0.9533,
                "stc_tagged": 0.9533,
                "stc_tagged_decay": 0.9533,
                "fraction_tagged": 0.535,
                "fraction_captured": 1.000,
                "HP_baseline_band": [0.20, 0.70],
                "HP_tag_band": [0.05, 0.30],
            },
            "user_classification_correction": "USER_placed_in_fairness_passed_bucket_actually_fairness_violation",
            "redesign_required": "v2_two_phase_continual_learning_protocol",
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "META_RULE_K_smoke_must_FIRE_discriminator",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
            ],
        },
    )


def atom_cortex_tonegawa_v2() -> Atom:
    return Atom(
        id=("AUDIT_INDETERMINATE_NEEDS_DIAGNOSTIC_cortex_schema_tonegawa_sparse_ensemble_v2"
            "_CAPACITY_DISCRIMINATOR_DESIGN_MISMATCH_with_shared_bank_mechanism"
            "_NO_SCHEMA_r_at_k_1p0_bank_800_PROTOTYPE_r_at_k_1p0_bank_100_TONEGAWA_K20"
            "_r_at_k_0p870_bank_100_capacity_at_95_PROTOTYPE_100_TONEGAWA_6_17x_capacity_loss"
            "_for_sparse_compression_v3_isolated_cosine_baseline_vs_Tonegawa_in_BUNDLED_bank"
            "_at_matched_bank_size_after_bundling_penalty_required_2026-06-27"),
        name=("INDETERMINATE_NEEDS_DIAGNOSTIC cortex_schema_tonegawa_v2: bank-config mismatch "
              "across arms makes lift not directly comparable; capacity@95 IS measured (PROTO=100 "
              "TONEGAWA_K20=6, 17x cap loss); v3 with matched-bundled-bank required"),
        description=(
            "Drill TOP-2 SMOKE_HARD_FAIL (TONEGAWA_K20=0.870 vs PROTOTYPE=1.000 vs NO_SCHEMA=1.000 "
            "at K=100 N_DIM=1024 BCC=0.45). Verify-off-data finding: per-arm raw at seed=7 "
            "between_cluster_cosine_measured=0.4497 (regime locked). Five arms: ARM_NO_SCHEMA "
            "r@k=1.0 fa=0.0 cap@95=100 schema_bank_size=800 (raw atoms; not compressed); "
            "ARM_PROTOTYPE_CENTROID r@k=1.0 fa=0.0 cap@95=100 bank=100 (8x compression via "
            "averaging); ARM_TONEGAWA_SPARSE_K20 r@k=0.870 fa=0.0 cap@95=6 bank=100 (sparse "
            "encoded; 17x cap LOSS at recall>=0.95); ARM_TONEGAWA_SPARSE_K10 r@k=0.628 cap@95=1; "
            "ARM_DIAG_RANDOM_SPARSE_K20 r@k=0.048 cap@95=1. Capacity differential IS measured "
            "(structural finding): TONEGAWA k-WTA sparse encoding pays a steep 17x capacity "
            "cost vs prototype-centroid at recall>=0.95. Cell author's framing: drill TOP-2's "
            "'capacity@95-recall requires BUNDLED memory (all schemas share substrate); v2 "
            "implements isolated-bank so cosine wins trivially' identifies the design issue. "
            "The 3 arms are in 3 different bank configurations (NO_SCHEMA=800 raw, PROTOTYPE="
            "100 centroid, TONEGAWA=100 sparse) -- 'lift' is not directly comparable. The "
            "regime where Tonegawa k-WTA sparse should win is bundled-bank (all schemas in one "
            "substrate vector; readout via sparse intersection), but v2 doesn't implement that. "
            "v3 required with: (a) BUNDLED-bank cosine baseline at matched bank-size; (b) "
            "Tonegawa-in-bundled-bank at same bundling depth; (c) discriminator = capacity@95 "
            "in BUNDLED regime (where the cost of bundling everything together makes sparse "
            "encoding win or lose on a level playing field). Until v3 lands, mechanism status "
            "INDETERMINATE -- NOT a substrate null; does NOT count against W-update-rule META "
            "claim. NO 2x drill of v2 needed; v3 redesign required."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 253,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "discriminator_regime_mismatch_arms_in_different_bank_configurations",
            "verified_off_data": True,
            "raw_metrics_path": "data/exp_cortex_schema_tonegawa_sparse_ensemble_v2/metrics.json",
            "key_per_arm_values": {
                "no_schema_rak_bank800": [1.0, 800],
                "prototype_rak_bank100": [1.0, 100],
                "tonegawa_k20_rak_bank100": [0.870, 100],
                "tonegawa_k10_rak_bank100": [0.628, 100],
                "diag_random_rak_bank100": [0.048, 100],
                "capacity_at_95_prototype": 100,
                "capacity_at_95_tonegawa_k20": 6,
                "capacity_loss_factor_at_95_recall": 16.67,
                "between_cluster_cosine_measured": 0.4497,
            },
            "structural_finding": "TONEGAWA_k_WTA_sparse_encoding_pays_17x_capacity_cost_at_recall_0p95_in_isolated_bank_regime",
            "v3_redesign_required": True,
            "v3_spec": "bundled_bank_cosine_baseline_vs_Tonegawa_in_bundled_bank_at_matched_bundling_depth_discriminator_capacity_at_95_in_BUNDLED_regime",
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "META_RULE_K_smoke_must_FIRE_discriminator",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
            ],
        },
    )


def atom_meta_indeterminate() -> Atom:
    return Atom(
        id=("AUDIT_META_CLAIM_INDETERMINATE_substrate_consolidation_favors_store_transfer"
            "_over_W_update_rule_selection_v1_PREMATURE_zero_of_five_wave2_cells_provide"
            "_fair_test_W_rule_null_evidence_engram_density_confound_3tier_W_regime_"
            "insufficient_pulses_BTSP_degenerate_baseline_STC_fairness_saturation_Tonegawa"
            "_discriminator_regime_mismatch_hippo_to_cortex_handoff_not_independently_"
            "verified_as_true_store_transfer_2026-06-27"),
        name=("META_CLAIM_INDETERMINATE substrate_consolidation_store_transfer_vs_W_rule: "
              "PREMATURE; 0/5 wave-2 cells provide fair-test W-rule-null evidence; all 5 had "
              "TEST_DESIGN / FAIRNESS / REGIME failures; cannot atomize claim until 2+ fair "
              "negatives exist"),
        description=(
            "Research proposed META_FINDING (2026-06-27 afternoon): 'substrate consolidation "
            "favors store-transfer over W-update-rule selection at fair regime in our "
            "prototype-classification task class'. Cited evidence: hippo->cortex handoff "
            "HARD_PASS (store-to-store transfer) vs Hopfield/BCM/BTSP/STC/engram_dropout/"
            "3-tier-W all failing (W-update-rule selection). Skunkworks vetting (verify-off-"
            "data on 5 of the W-rule-negatives): VERDICT INDETERMINATE; PREMATURE; do NOT "
            "atomize claim yet. Of the 5 W-rule-negative cells cited, ZERO provide fair-test "
            "evidence: (1) engram_dropout_v1: density confound (random@0.50 vs engram@0.37, "
            "not density-matched); (2) hierarchical_3_tier_W_v1: regime-insufficient pulses "
            "(ultraslow tier at 0.32pct of slow drift at smoke pulse budget); (3) btsp_binary_"
            "synapse_v3_sparse_regime_swept: degenerate baseline (BinHeb W_bin mean 0.9932 "
            "= near-constant matrix via W==0 default-fill); (4) stc_tag_and_capture_v1: "
            "fairness violation (baseline 0.953 above HP_baseline=[0.20,0.70] ceiling); "
            "(5) cortex_schema_tonegawa_v2: discriminator-regime mismatch (arms in 3 different "
            "bank configurations not directly comparable). Plus: hippo->cortex handoff has "
            "not been independently verified to be TRUE store-transfer (vs W-rule under "
            "the hood at consolidation step). To support META claim, need: (A) re-run cells "
            "1,2,3,5 with design fixes -- if STILL null with fair baselines + sufficient "
            "regime + non-degenerate baselines + matched discriminators, those count as "
            "W-rule-null evidence; (B) add 2-3 NEW W-rule mechanisms with clean fairness "
            "scaffolding (Oja's rule, Sanger's rule, decay-Hebbian variant); negatives from "
            "those would also count; (C) verify hippo->cortex handoff implementation -- if "
            "it has any W-tuning step under the hood at consolidation, the META claim "
            "needs reframing. Until at least 2 fair-test W-rule-null cells land, the META "
            "claim is UNSUPPORTED and should not appear in any pre-reg framing or pivot "
            "decision. Pivot to store-transfer architectures may STILL be the right move "
            "for other reasons (e.g., brain-grounded fast/slow STORE separation has high "
            "prior per USER 2026-06-23 brain-is-existence-proof rule) but it should not be "
            "anchored on a META claim that today's data does not support."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 254,
            "confirmed_or_candidate": "CANDIDATE",
            "lesson_class": "research_META_claim_premature_no_fair_test_evidence",
            "verified_off_data": True,
            "claim_status": "INDETERMINATE_DO_NOT_ATOMIZE_AS_FINDING",
            "research_proposed_claim": "substrate_consolidation_favors_store_transfer_over_W_update_rule_selection",
            "fair_test_negatives_count": 0,
            "fair_test_negatives_required_for_atomization": 2,
            "cell_disqualification_reasons": {
                "engram_dropout_v1": "density_confound_not_density_matched",
                "hierarchical_3_tier_W_v1": "regime_insufficient_pulse_budget",
                "btsp_v3_sparse_swept": "degenerate_baseline_W_collapse_to_constant",
                "stc_v1": "fairness_baseline_saturation_above_HP_ceiling",
                "tonegawa_v2": "discriminator_regime_mismatch_different_bank_configs",
            },
            "supporting_evidence_required": [
                "rerun_cells_1_2_3_5_with_design_fixes_check_if_still_null",
                "add_Oja_rule_OR_Sanger_rule_OR_decay_Hebbian_W_rule_with_clean_fairness",
                "verify_hippo_to_cortex_handoff_is_true_store_transfer_not_implicit_W_tuning",
            ],
            "composes_with": [
                "META_RULE_AA_FAIRNESS_BEFORE_TIER",
                "META_RULE_T_per_arm_metric_verification_required_before_META_atomization",
                "Fix28_per_arm_metrics_not_summary_verdict_text",
                "feedback_skunkworks_correctly_overrides_director_via_by_construction_saturation",
            ],
        },
    )


def main() -> int:
    print(f"Source tag: {SOURCE_TAG}")
    print(f"Store root: {STORE_ROOT}")
    print()
    results = []
    atoms_to_add = [
        (atom_engram_dropout(), "TEST_DESIGN_FAILURE engram_dropout_v1 (density confound) verified"),
        (atom_three_tier_W(), "HONEST_NEG_REGIME_BOUNDED 3-tier-W (ultraslow insufficient pulses) verified"),
        (atom_btsp_v3_sparse(), "TEST_DESIGN_FAILURE btsp_v3_sparse (degenerate baseline W==0 fill) verified"),
        (atom_stc_v1_fairness(), "FAIRNESS_VIOLATION stc_v1 (baseline saturated above HP band) verified"),
        (atom_cortex_tonegawa_v2(), "INDETERMINATE_NEEDS_DIAGNOSTIC tonegawa_v2 (discriminator regime mismatch) verified"),
        (atom_meta_indeterminate(), "META_CLAIM_INDETERMINATE substrate_consolidation_store_transfer_vs_W_rule (premature; 0/5 fair-test evidence) verified"),
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
