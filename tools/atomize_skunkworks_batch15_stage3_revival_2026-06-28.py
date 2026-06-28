"""Atomize: Skunkworks batch 15 Stage 3 revival morning wave (2026-06-28).

Source request:
  Director batch 15 dispatch covering 3 candidates from Stage 3 morning revival wave:
    1) multihop partition-oracle v5-regime-revival c1 N=2048 (SMOKE_HARD_PASS saturated)
    2) multihop partition-oracle v5-regime-revival c1 N=8192 (MIDDLE_BAND_SATURATED_AUTO_DEMOTE)
    3) hierarchical-planner state-conditioned-disjoint v1 (HARD_FAIL clean negative)
  + META_RULE_AN cone-collapse-formula-N2048-calibrated (extends META_RULE_AL/AM)

VERIFY-OFF-DATA basis (.venv Python; each metrics.json Read end-to-end on disk; per-arm
cross-checked against Director's framings):

  Cell 1  Partition-oracle revival c1 N=2048 SMOKE  -> MEASURED_MECHANISM (saturation
                                                       auto-demote per BIAS-Q; mechanism
                                                       class confirmed via 5-arm distinct
                                                       lift_B_A=+0.81)
  Cell 2  Partition-oracle revival c1 N=8192 SMOKE  -> MEASURED_MECHANISM (saturated arms
                                                       B/C/D all at ceiling; BASELINE=0.59
                                                       breaches RAIL [0.110,0.250] upward;
                                                       lift_B_A=+0.41 mechanism load-bearing;
                                                       cone-collapse formula MISCALIBRATED
                                                       at N=8192 by 3.7x)
  Cell 3  Hierarchical state-cond-disjoint v1 SMOKE -> HONEST_NEGATIVE_SMOKE (both=0.000
                                                       <= flat=0.067; SC=DJ=0.000;
                                                       arms_distinct=True; 2nd hierarchical-
                                                       planning attempt failed; macro
                                                       vocabulary non-compositional at d=8)
  Cell 4  META_RULE_AN cone-collapse-formula-calibration -> META atom (concrete evidence
                                                            from Cell 2's BASELINE rail-
                                                            breach +0.43 above predicted)

NET CERT delta: 0 chain-grade (all saturated)
  + 2 MM (Cell 1 + Cell 2 mechanism characterization)
  + 1 HONEST_NEG (Cell 3 hierarchical revival fail)
  + 1 META (META_RULE_AN cone-collapse-formula-N2048-calibrated)

PRE CERT N (verified live): 628
POST CERT N (predicted; A5-gated): 628 (no chain_grade increment; MM/honest_neg/meta = +0)

LEDGER ROWS: 4 (2 measured_mechanism + 1 honest_negative + 1 discipline_meta)

A5 GATING: PRE/POST cert_n assertions on every window; round-trip pq check on every atom.

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_batch15_stage3_revival_2026-06-28.py            # DRY
  .venv/Scripts/python.exe tools/atomize_skunkworks_batch15_stage3_revival_2026-06-28.py --apply    # WRITE
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row

STORE_ROOT = Path("data/substrate_index")
RULING_NOTE = "notes/skunkworks_landed_vet_batch15_stage3_revival_2026-06-28.md"
CELL_COMMIT = "n/a-2026-06-28-batch15-stage3-revival"
ATOMIZED_BY = "skunkworks_atomize_batch15_stage3_revival_2026-06-28"

METRICS_PO_N2048 = "data/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_smoke/metrics.json"
METRICS_PO_N8192 = "data/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_n8192/metrics.json"
METRICS_HIER_SCDJ = "data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/metrics.json"


# ============================================================================
# ATOM 1 -- Partition-Oracle v5-revival c1 N=2048 MEASURED_MECHANISM (saturation)
# ============================================================================

def build_atom1_po_n2048_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_N2048_MEASURED_MECHANISM_smoke_"
            "BASELINE_A_0p190_in_rail_target_0p160_ORACLE_B_1p000_saturated_psz10_xtalk_0p066_"
            "ORACLE_C_0p970_psz20_xtalk_0p096_ORACLE_D_0p840_psz100_xtalk_0p220_RANDOM_E_0p000_"
            "lift_B_A_0p810_lift_B_E_1p000_arms_distinct_5_cardinality_ok_cv_nan_saturation_True_"
            "BIAS_Q_AUTO_DEMOTE_n_seeds_1_seed_11_N2048_V_C1000_depth10_n_chains_train200_test100"
        ),
        name=(
            "substrate_multihop_partition_oracle_at_v5_regime_revival_c1 N=2048 MEASURED_MECHANISM at smoke: "
            "BASELINE_A=0.190 (rail OK, target=0.160) ORACLE_B=1.000 (saturated psz=10) "
            "ORACLE_C=0.970 ORACLE_D=0.840 RANDOM_E=0.000 lift_B_A=+0.81 lift_B_E=+1.00 "
            "arms_distinct=5; BIAS-Q auto-demote on ORACLE_B saturation; mechanism class confirmed"
        ),
        description=(
            "MEASURED_MECHANISM substrate multi-hop partition-oracle at v5 harder regime, revival c1\n"
            "N=2048 (delta=0). Cell verdict SMOKE_HARD_PASS but BIAS-Q saturation guard auto-demotes\n"
            "to MM (ORACLE_B=1.000 at ceiling; cv=nan because n_seeds=1; saturation=True per config).\n"
            "The MECHANISM CLASS is confirmed: goal-conditioned partition lookup recovers chain-grade\n"
            "depth-10 multi-hop accuracy that baseline-full-V_C cleanup CANNOT recover.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 1 seed: 11; 5 arms = baseline_\n"
            "full_V_C / oracle_part_100_psz10 / oracle_part_50_psz20 / oracle_part_10_psz100 /\n"
            "no_oracle_random_part_100; per-arm verified):\n"
            "  Cardinality: 5/5 OK (5 arms, expected=observed=5, cardinality_ok=True).\n"
            "  Per-arm top1 (single seed; per-step accuracy over depth 10):\n"
            "    arm_a_baseline (full V_C=1000)        top1=0.19  per-step [0.88,0.77,...,0.19]\n"
            "    arm_b_oracle_part_100_psz10           top1=1.00  per-step [1.0]*10 *SATURATED*\n"
            "    arm_c_oracle_part_50_psz20            top1=0.97  per-step [0.99,...,0.97]\n"
            "    arm_d_oracle_part_10_psz100           top1=0.84  per-step [0.98,...,0.84]\n"
            "    arm_e_no_oracle_random_part_100       top1=0.00  per-step [~0.0]*10\n"
            "  Crosstalk:\n"
            "    baseline_xtalk=0.6984 (V_C=1000)\n"
            "    crosstalk_B=0.0663   (psz=10)  -- predicted decoder margin tight\n"
            "    crosstalk_C=0.0963   (psz=20)\n"
            "    crosstalk_D=0.2199   (psz=100)\n"
            "  Lifts:\n"
            "    lift_B_over_A = 1.00 - 0.19 = +0.81  (vs HP_lift_base=0.15 -- cleared 5.4x)\n"
            "    lift_B_over_E = 1.00 - 0.00 = +1.00  (vs HP_lift_rand=0.10 -- cleared 10x)\n"
            "    lift_C_over_A = +0.78\n"
            "    lift_D_over_A = +0.65\n"
            "  BASELINE rail: target=0.160; RAIL=[0.110,0.210]; observed=0.190 -> rail_breach=0/1 PASS.\n"
            "  Discriminator E (no_oracle_random partition same bucket-size) at 0.000 vs ORACLE_B 1.000:\n"
            "    goal-info IS load-bearing; routing through correct partition is mechanism.\n"
            "\n"
            "WHY MEASURED_MECHANISM NOT CHAIN_GRADE (Skunkworks-cert-owner BIAS-Q):\n"
            "  ORACLE_B=1.000 hits saturation ceiling; cv cannot be computed (n_seeds=1); the cell's\n"
            "  smoke verdict acknowledges saturation=True. Chain-grade requires an UN-saturated win\n"
            "  band so that lift_B_A is bounded by mechanism strength not by the metric cap. The\n"
            "  REVIVAL design recognized this and dispatched the N=8192 c1 variant (Atom 2 below)\n"
            "  precisely to find the un-saturated regime; that variant also saturates -> formula\n"
            "  recalibration MM (META_RULE_AN, Atom 4 below).\n"
            "  Recommendation for chain-grade promotion: psz scaling beyond N=8192 (e.g. psz=80+\n"
            "  AND part_count=128 at N=8192 keeping crosstalk_B~0.069 fixed) so ORACLE_B lands\n"
            "  in [0.45, 0.80] with HEADROOM and cv<0.15 over >=3 seeds.\n"
            "\n"
            "WHY NOT HARD_FAIL: 4 distinct arms cleanly separate (5/5 distinct); mechanism direction\n"
            "  matches all theoretical predictions (B>C>D as part_size grows -> xtalk grows;\n"
            "  random-routed E at chance). Mechanism is REAL; the only deficit is metric-cap.\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Mante 2013 PFC goal-conditioned-attention: PFC suppresses irrelevant feature\n"
            "  dimensions during context-conditional decisions. Partition-oracle is the substrate\n"
            "  analog: pre-supplied attention mask shrinks effective decode vocabulary from V_C=1000\n"
            "  to psz=10. This validates Barrier-1 (goal-conditioning) mechanism CLASS; brain analog\n"
            "  exists; substrate-side implementation requires a learnable upstream partition\n"
            "  classifier (not oracle-supplied) for product-grade chain.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 5/5 OK\n"
            "  META_RULE_AF arms-must-differ: 5 distinct arms (A=0.19, B=1.00, C=0.97, D=0.84, E=0.00)\n"
            "  META_RULE_AH atomic metrics: per-arm per-step + lifts + crosstalks all recorded\n"
            "  META_RULE_K discriminator: ARM_E random-routed = 0.000 (clean discriminator-fires)\n"
            "  META_RULE_L band: BASELINE in rail [0.110,0.210]; ORACLE_B saturated (BIAS-Q auto-\n"
            "    demote triggered correctly per cell verdict_msg)\n"
            "  BIAS-Q saturation guard: triggered (HP_sat_ceil=0.99; ORACLE_B=1.000)\n"
            "  Fix #28 per-arm reads: per-step accuracy lists verified for all 5 arms\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero_llm_calls_at_inference=True per metrics).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "substrate_multihop_partition_oracle_at_v5_regime_revival_c1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_PO_N2048,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "smoke",
            "n_seeds": 1,
            "seeds": [11],
            "N": 2048,
            "V_C": 1000,
            "V_P": 10,
            "depth": 10,
            "n_chains_train": 200,
            "n_chains_test": 100,
            "n_partitions_B": 100,
            "part_size_B": 10,
            "n_partitions_C": 50,
            "part_size_C": 20,
            "n_partitions_D": 10,
            "part_size_D": 100,
            "crosstalk_baseline_MEASURED": 0.6984,
            "crosstalk_B_MEASURED": 0.0663,
            "crosstalk_C_MEASURED": 0.0963,
            "crosstalk_D_MEASURED": 0.2199,
            "ARM_A_baseline_top1_MEASURED": 0.190,
            "ARM_B_oracle_p100_psz10_top1_MEASURED": 1.000,
            "ARM_C_oracle_p50_psz20_top1_MEASURED": 0.970,
            "ARM_D_oracle_p10_psz100_top1_MEASURED": 0.840,
            "ARM_E_random_part_top1_MEASURED": 0.000,
            "lift_B_over_A_MEASURED": 0.810,
            "lift_B_over_E_MEASURED": 1.000,
            "lift_C_over_A_MEASURED": 0.780,
            "lift_D_over_A_MEASURED": 0.650,
            "baseline_rail_ok": True,
            "saturation_triggered": True,
            "BIAS_Q_auto_demote": True,
            "arms_distinct": True,
            "encoder_provenance": "SUBSTRATE_NATIVE_BIPOLAR",
            "verdict_raw": "SMOKE_HARD_PASS",
            "demote_reason": "ORACLE_B_saturated_at_1p000_cv_nan_n_seeds_1_BIAS_Q_chain_grade_requires_unsaturated_band",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AF_arms_must_differ_5of5_distinct": True,
            "META_RULE_AH_atomic_metrics": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_baseline_in_rail": True,
            "BIAS_Q_saturation_guard": "triggered_correctly",
            "load_bearing_finding": "barrier_1_goal_conditioning_partition_oracle_mechanism_class_validated_at_5x_HP_lift",
            "feeds_META_RULE_AN": True,
            "scope_observed": "smoke_1_seed_N2048_V_C1000_depth10_5_arms_psz_in_10_20_100",
            "scope_not_claimed": "chain_grade_OR_un_saturated_OR_multi_seed_cv",
            "brain_analog": "Mante_2013_PFC_goal_conditioned_attention_partition_as_substrate_analog",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 2 -- Partition-Oracle v5-revival c1 N=8192 MEASURED_MECHANISM (rail_breach upward + saturation)
# ============================================================================

def build_atom2_po_n8192_mm() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_N8192_MEASURED_MECHANISM_smoke_"
            "BASELINE_A_0p590_rail_breach_1of1_upward_RAIL_0p110_0p250_target_0p160_substrate_exceeds_formula_"
            "ORACLE_B_1p000_saturated_psz40_xtalk_0p069_ORACLE_C_1p000_psz100_xtalk_0p110_ORACLE_D_0p990_"
            "psz200_xtalk_0p156_RANDOM_E_0p000_lift_B_A_0p410_lift_B_E_1p000_arms_distinct_5_cardinality_ok_"
            "cv_nan_saturation_True_BIAS_Q_AUTO_DEMOTE_n_seeds_1_seed_11_N8192_V_C4000_depth10"
        ),
        name=(
            "substrate_multihop_partition_oracle_at_v5_regime_revival_c1 N=8192 MEASURED_MECHANISM at smoke: "
            "BASELINE_A=0.590 (rail_breach UPWARD; expected ~0.160 by cone-collapse formula -> 3.7x off) "
            "ORACLE_B/C/D=1.00/1.00/0.99 saturated; lift_B_A=+0.41 mechanism load-bearing; "
            "cone-collapse formula calibration broken at N=8192 -> feeds META_RULE_AN"
        ),
        description=(
            "MEASURED_MECHANISM substrate multi-hop partition-oracle at v5-revival c1 N=8192 (delta=0).\n"
            "Cell verdict MIDDLE_BAND_SATURATED_AUTO_DEMOTE; mechanism characterization preserved.\n"
            "TWO load-bearing findings:\n"
            "  (1) Mechanism CLASS confirmed at scaled-up N=8192: ORACLE_B/C/D all retain >=0.99\n"
            "      top1 at depth-10 with substantially larger psz (40/100/200 vs prior 10/20/100);\n"
            "      lift_B_A=+0.41 (HP_lift_base=0.20 cleared 2.0x).\n"
            "  (2) Cone-collapse formula MISCALIBRATED at N=8192: BASELINE_A=0.59 vs formula\n"
            "      prediction ~0.16 -> off by 3.7x. Substrate has ~3.7x MORE headroom at N=8192\n"
            "      than the per-hop crosstalk-margin model predicts. Feeds META_RULE_AN (Atom 4).\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 1 seed: 11; 5 arms; per-arm\n"
            "per-step verified):\n"
            "  Cardinality: 5/5 OK; expected=observed=5.\n"
            "  Per-arm top1:\n"
            "    arm_a_baseline (full V_C=4000)        top1=0.590  per-step [0.96,0.92,...,0.59]\n"
            "    arm_b_oracle_part_100_psz40           top1=1.000  per-step [1.0]*10 *SATURATED*\n"
            "    arm_c_oracle_part_40_psz100           top1=1.000  per-step [1.0]*10 *SATURATED*\n"
            "    arm_d_oracle_part_20_psz200           top1=0.990  per-step [1.0]*9,0.99 *NEAR-SAT*\n"
            "    arm_e_no_oracle_random_part_100       top1=0.000  per-step [0.0]*10\n"
            "  Crosstalk:\n"
            "    baseline_xtalk=0.6987 (V_C=4000)\n"
            "    crosstalk_B=0.0690 (psz=40)\n"
            "    crosstalk_C=0.1099 (psz=100)\n"
            "    crosstalk_D=0.1559 (psz=200)\n"
            "  Lifts:\n"
            "    lift_B_over_A = 1.000 - 0.590 = +0.410 (vs HP_lift_base=0.20 -- cleared 2.05x)\n"
            "    lift_B_over_E = 1.000 - 0.000 = +1.000 (vs HP_lift_rand=0.10 -- cleared 10x)\n"
            "    lift_C_over_A = +0.41; lift_D_over_A = +0.40\n"
            "  BASELINE rail: target=0.160; RAIL=[0.110,0.250]; observed=0.590 -> rail_breach=1/1\n"
            "    UPWARD. Substrate exceeds formula by ~3.7x.\n"
            "  Discriminator E (random-routed psz=40 same as B): 0.000 vs B=1.000 = +1.000 lift.\n"
            "    Goal-routed partition oracle is mechanism (NOT just psz-narrowing); pure psz=40\n"
            "    cleanup with random partition assignment gets nothing.\n"
            "\n"
            "WHY MEASURED_MECHANISM NOT CHAIN_GRADE (Skunkworks-cert-owner BIAS-Q):\n"
            "  ORACLE_B/C saturate at 1.000; ORACLE_D at 0.990; cv=nan (n_seeds=1). The CELL DESIGN\n"
            "  pre-specified HP_B_band=[0.40, 0.80] expecting psz=40 expansion would un-saturate\n"
            "  -- it did NOT, because substrate baseline crosstalk margin at N=8192 V_C=4000 psz=40\n"
            "  is much smaller than the formula predicted. The cell's verdict_msg ('NEED_HARDER_\n"
            "  REGIME') correctly identifies this. Chain-grade requires:\n"
            "    (a) psz>=80 OR depth>=12 OR V_C>=8000 to land ORACLE_B in [0.45, 0.80]\n"
            "    (b) >=3 seeds with cv<0.15\n"
            "    (c) BASELINE_A back in rail (i.e. baseline -50% per-hop attrition restored)\n"
            "  c1 chain: N=2048 saturated -> N=8192 c1 still saturated -> next attempt should be\n"
            "  psz=80 at N=8192 V_C=4000 depth=12, OR depth=15 at psz=40 to push BASELINE_A back\n"
            "  to ~0.16 target.\n"
            "\n"
            "WHY NOT HARD_FAIL: 5 distinct arms cleanly separate; mechanism direction matches\n"
            "  prediction (B>=C>D as psz/xtalk grow); discriminator E at 0.000 cleanly fires;\n"
            "  lift_B_A at +0.41 is HP-passing on lift but saturation prevents chain-grade.\n"
            "\n"
            "FALSIFIED PREDICTION (Mechanism still real; formula needs recalibration):\n"
            "  v1 calibration: crosstalk_std=sqrt((V_C_per_hop-1)/N) -> at N=2048 V_C=1000 the\n"
            "  formula was empirically tight (BASELINE=0.19 matches predicted ~0.16). At N=8192\n"
            "  V_C=4000 the SAME formula predicts BASELINE~0.16; observed 0.59 (off by 3.7x).\n"
            "  Either the per-hop attrition has SUB-linear scaling in V_C / N (not 1:1), OR\n"
            "  the substrate decoder has implicit cleanup margin beyond the simple cone model.\n"
            "  This is the META_RULE_AN finding (Atom 4): cone-collapse formula calibrated at\n"
            "  N=2048 cannot be naively extrapolated to N=8192 without recalibration.\n"
            "\n"
            "BRAIN-GROUNDED FRAMING (same as Atom 1; PFC goal-conditioning class):\n"
            "  Larger N + V_C = closer to cortical capacity scale; mechanism CLASS survives the\n"
            "  4x scale-up. Open: is the mechanism FREE (i.e. comes from N alone) or REQUIRES\n"
            "  oracle-supplied partition? Random-routed E at 0.000 confirms partition INFO is\n"
            "  load-bearing; substrate-grown partition-classifier remains the chain-grade path.\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 5/5 OK\n"
            "  META_RULE_AF arms-must-differ: 5 distinct\n"
            "  META_RULE_AH atomic metrics: per-arm per-step + lifts + xtalks recorded\n"
            "  META_RULE_K discriminator: random-routed E=0.000 (clean fires)\n"
            "  META_RULE_L band: BASELINE_A=0.59 breached RAIL [0.110,0.250] upward;\n"
            "    ORACLE_B in_band=False (above HP_B_band=[0.40,0.80])\n"
            "  BIAS-Q saturation guard: triggered (HP_sat_ceil=0.99; B/C=1.000)\n"
            "  Fix #28 per-arm reads: verified all 5 arms\n"
            "  PROT-018 _n8192 suffix binding: cell anchor correctly differentiated\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (zero_llm_calls_at_inference=True per metrics).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "cell_anchor": "substrate_multihop_partition_oracle_at_v5_regime_revival_c1_n8192",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_PO_N8192,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "smoke",
            "n_seeds": 1,
            "seeds": [11],
            "N": 8192,
            "V_C": 4000,
            "V_P": 10,
            "depth": 10,
            "n_chains_train": 200,
            "n_chains_test": 100,
            "n_partitions_B": 100,
            "part_size_B": 40,
            "n_partitions_C": 40,
            "part_size_C": 100,
            "n_partitions_D": 20,
            "part_size_D": 200,
            "crosstalk_baseline_MEASURED": 0.6987,
            "crosstalk_B_MEASURED": 0.0690,
            "crosstalk_C_MEASURED": 0.1099,
            "crosstalk_D_MEASURED": 0.1559,
            "ARM_A_baseline_top1_MEASURED": 0.590,
            "ARM_B_oracle_p100_psz40_top1_MEASURED": 1.000,
            "ARM_C_oracle_p40_psz100_top1_MEASURED": 1.000,
            "ARM_D_oracle_p20_psz200_top1_MEASURED": 0.990,
            "ARM_E_random_part_top1_MEASURED": 0.000,
            "lift_B_over_A_MEASURED": 0.410,
            "lift_B_over_E_MEASURED": 1.000,
            "lift_C_over_A_MEASURED": 0.410,
            "lift_D_over_A_MEASURED": 0.400,
            "baseline_rail_ok": False,
            "baseline_rail_breach_direction": "UPWARD_substrate_more_capable_than_formula_predicted",
            "rail_predicted": [0.110, 0.250],
            "rail_target": 0.160,
            "rail_observed": 0.590,
            "rail_breach_ratio_vs_target": 3.7,
            "saturation_triggered": True,
            "BIAS_Q_auto_demote": True,
            "arms_distinct": True,
            "encoder_provenance": "SUBSTRATE_NATIVE_BIPOLAR",
            "verdict_raw": "MIDDLE_BAND_SATURATED_AUTO_DEMOTE",
            "demote_reason": "ORACLE_B_C_saturated_at_1p000_AND_BASELINE_rail_breach_upward_3p7x_formula_misclibrated",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AF_arms_must_differ_5of5_distinct": True,
            "META_RULE_AH_atomic_metrics": True,
            "META_RULE_K_discriminator_fires": True,
            "META_RULE_L_band_check": "BASELINE_breach_upward_ORACLE_B_above_band_saturated",
            "BIAS_Q_saturation_guard": "triggered_correctly",
            "load_bearing_finding_1": "barrier_1_partition_oracle_mechanism_class_survives_4x_scale_up_N2048_to_N8192",
            "load_bearing_finding_2": "cone_collapse_formula_predicted_baseline_0p16_observed_0p59_off_by_3p7x_substrate_exceeds_formula",
            "feeds_META_RULE_AN": True,
            "scope_observed": "smoke_1_seed_N8192_V_C4000_depth10_5_arms_psz_in_40_100_200",
            "scope_not_claimed": "chain_grade_OR_un_saturated_OR_multi_seed_cv_OR_recalibrated_formula",
            "brain_analog": "Mante_2013_PFC_goal_conditioned_attention_partition_at_cortex_scale_N",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 3 -- Hierarchical state-conditioned-disjoint v1 HONEST_NEGATIVE_SMOKE
# ============================================================================

def build_atom3_hier_scdj_honest_neg() -> Atom:
    return Atom(
        id=(
            "T3/EXP_substrate_hierarchical_planner_state_conditioned_disjoint_v1_HONEST_NEGATIVE_SMOKE_"
            "RAIL_1p000_sanity_OK_RAND_0p017_chance_FLAT_PREPLAY_K64_D8_0p067_baseline_"
            "TREE_3LVL_STATE_COND_0p000_TREE_3LVL_DISJOINT_BLOCK_0p000_TREE_3LVL_BOTH_0p000_"
            "both_minus_flat_neg_0p067_both_minus_state_cond_0p000_both_minus_disjoint_0p000_"
            "arms_distinct_True_cardinality_ok_360of360_n_seeds_2_seeds_7_17_N8160_blocks8_actions6_"
            "macros5_K_class8_goals30_depth8_K_flat64_K_tree16_2nd_hierarchical_planning_attempt_failed"
        ),
        name=(
            "substrate_hierarchical_planner_state_conditioned_disjoint v1 HONEST_NEGATIVE at smoke: "
            "RAIL=1.000 sanity OK; RAND=0.017 chance; FLAT_BASELINE=0.067; "
            "SC=DJ=BOTH=0.000 (HURTS baseline by -0.067); macro-vocabulary non-compositional at depth=8; "
            "2nd hierarchical-planning attempt failed -- Sutton-Precup options redesign needed"
        ),
        description=(
            "HONEST_NEGATIVE substrate hierarchical planner with state-conditioned + disjoint-block\n"
            "tree macros at v1 smoke (delta=0). 2nd attempted hierarchical-planning revival fails:\n"
            "the macro-vocabulary approach (tree-3-level abstractions) NOT only fails to outperform\n"
            "flat preplay, it HURTS the baseline (both_minus_flat=-0.067; both=0.000 vs flat=0.067).\n"
            "Cleanly atomizable as proven negative; HARD_FAIL not infra-bug.\n"
            "\n"
            "OFF-DATA RECOMPUTE (Skunkworks 2026-06-28, .venv Python, 2 seeds: 7, 17; 6 arms =\n"
            "reproduce_rail / random_plan / flat_preplay_k64_d8 / tree_3lvl_state_cond /\n"
            "tree_3lvl_disjoint_block / tree_3lvl_both; per-arm per-seed verified):\n"
            "  Cardinality: 360/360 OK (cardinality_ok=True).\n"
            "  n_seeds_complete=2.\n"
            "  Per-arm solve_rate (seed7, seed17; mean):\n"
            "    reproduce_rail            (1.000, 1.000) mean=1.000  *SANITY OK*\n"
            "    random_plan               (0.000, 0.033) mean=0.017  *CHANCE FLOOR*\n"
            "    flat_preplay_k64_d8       (0.067, 0.067) mean=0.067  *BASELINE*\n"
            "    tree_3lvl_state_cond      (0.000, 0.000) mean=0.000\n"
            "    tree_3lvl_disjoint_block  (0.000, 0.000) mean=0.000\n"
            "    tree_3lvl_both            (0.000, 0.000) mean=0.000  *PRIMARY*\n"
            "  Discriminator + lift:\n"
            "    both_minus_flat        = 0.000 - 0.067 = -0.067  (HURTS baseline; HP_lift_flat>=0.25 FAILED)\n"
            "    both_minus_state_cond  = 0.000 - 0.000 = 0.000   (HP_lift_sc>=0.10 FAILED)\n"
            "    both_minus_disjoint    = 0.000 - 0.000 = 0.000   (HP_lift_dj>=0.10 FAILED)\n"
            "    chance_random_floor    = 5.95e-07 (effectively zero)\n"
            "    chance_random_rerank_ub= 0.050 (above-chance threshold; FLAT 0.067 only just above)\n"
            "  arms_distinct=True (rail/rand/flat are distinct; the three TREE arms tie at 0.000\n"
            "    which is the LOAD-BEARING null finding -- macros add zero/negative value).\n"
            "  cv on tree arms = inf (zero variance because zero solves); cv on flat = 0.0 (tied\n"
            "    seeds at 0.067).\n"
            "\n"
            "WHY HONEST_NEGATIVE (Skunkworks-cert-owner) NOT MEASURED_MECHANISM:\n"
            "  Mechanism direction CONTRADICTS prediction (macros HURT baseline). MM requires a\n"
            "  validated mechanism CLASS even if magnitude is partial; here the mechanism CLASS\n"
            "  itself is falsified at this regime. This is the 2nd hierarchical-planning attempt\n"
            "  (v1 + state-cond-disjoint revival) and both fail. Macro-vocabulary at depth-8 with\n"
            "  K_class=8 macro-classes shows no compositional gain.\n"
            "\n"
            "WHY HONEST_NEG_SMOKE not chain-grade HONEST_NEG:\n"
            "  n_seeds=2 (smoke regime). Promotion to full-N honest-negative needs >=3 seeds + the\n"
            "  Sutton-Precup options reformulation to falsify the MECHANISM CLASS rather than just\n"
            "  this implementation. Drill ANCHOR 2 (Sutton-Precup options framework) carries the\n"
            "  revival path; current atom files this implementation as failed.\n"
            "\n"
            "BRAIN-GROUNDED FRAMING:\n"
            "  Brain hierarchical control (Botvinick/Niv option framework / BG-frontal hierarchy)\n"
            "  uses LEARNED OPTION TERMINATIONS not pre-specified macro classes. The v1 + revival\n"
            "  both use ALL-AT-ONCE macro instantiation without termination learning; this is the\n"
            "  candidate root-cause and points to Sutton-Precup options as the redesign frame.\n"
            "\n"
            "RECOMMENDATION (research-owned redesign; cert-owner does NOT direct strategy):\n"
            "  Atomize this implementation as failed; do NOT re-attempt the macro-vocabulary\n"
            "  approach without a fundamentally different formulation (Sutton-Precup termination\n"
            "  functions + intra-option learning + bottleneck states).\n"
            "\n"
            "META_RULE COMPLIANCE:\n"
            "  META_RULE_H cardinality: 360/360 OK\n"
            "  META_RULE_AF arms-must-differ: rail/rand/flat distinct; 3 tree arms tie at 0.000\n"
            "    (load-bearing null -- not a violation, this IS the finding)\n"
            "  META_RULE_AH atomic metrics: per-arm per-seed recorded\n"
            "  META_RULE_K discriminator: rail/rand fire cleanly (1.000 vs 0.017); macros don't fire\n"
            "  META_RULE_L band: rail in 'oracle' band; rand at chance floor; flat just above chance\n"
            "    upper bound (0.067 vs 0.050) -- FLAT itself MIDDLE_BAND-adjacent; macros below FLAT\n"
            "  META_RULE_AM substrate-already-does-X: 9th occurrence today (flat preplay at K=64\n"
            "    captures everything macros could; macros add nothing or negative)\n"
            "  hardening L1early+L2perarm+L3outertry+L4importsentinel: present\n"
            "  Fix #28 per-arm reads: verified all 6 arms across 2 seeds\n"
            "\n"
            "_llm_forward_calls_at_inference = 0.\n"
            "substrate_only_decode_gate: PASS (no LLM in inference path).\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "SMOKE_ONLY",
            "cert_status": "honest_negative",
            "cert_class": "proven_negative_smoke",
            "cell_anchor": "substrate_hierarchical_planner_state_conditioned_disjoint_v1",
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_HIER_SCDJ,
            "ruling_note": RULING_NOTE,
            "verified_off_data": True,
            "run_mode": "smoke",
            "n_seeds": 2,
            "seeds": [7, 17],
            "N": 8160,
            "blocks": 8,
            "actions": 6,
            "macros": 5,
            "K_class": 8,
            "goals": 30,
            "depth": 8,
            "K_flat": 64,
            "K_tree": 16,
            "ARM_reproduce_rail_solve_rate_MEASURED": 1.000,
            "ARM_random_plan_solve_rate_MEASURED": 0.017,
            "ARM_flat_preplay_K64_D8_solve_rate_MEASURED": 0.067,
            "ARM_tree_3lvl_state_cond_solve_rate_MEASURED": 0.000,
            "ARM_tree_3lvl_disjoint_block_solve_rate_MEASURED": 0.000,
            "ARM_tree_3lvl_both_solve_rate_MEASURED": 0.000,
            "both_minus_flat_MEASURED": -0.067,
            "both_minus_state_cond_MEASURED": 0.000,
            "both_minus_disjoint_MEASURED": 0.000,
            "chance_random_floor_MEASURED": 5.95e-07,
            "chance_random_rerank_ub_MEASURED": 0.050,
            "arms_distinct": True,
            "cardinality_ok": True,
            "verdict_raw": "HARD_FAIL",
            "honest_negative_reason": "macro_vocabulary_state_conditioned_AND_disjoint_block_at_depth_8_HURTS_flat_baseline_by_0p067_2nd_hierarchical_attempt_failed",
            "META_RULE_H_cardinality_ok": True,
            "META_RULE_AF_arms_must_differ_load_bearing_null_at_tree_arms": True,
            "META_RULE_AH_atomic_metrics": True,
            "META_RULE_K_discriminator_fires_on_rail_rand_flat_not_on_tree": True,
            "META_RULE_L_band_check": "rail_oracle_rand_chance_flat_just_above_rerank_ub_tree_below_flat",
            "META_RULE_AM_substrate_already_does_X_occurrence_today": 9,
            "Fix_28_per_arm_reads": "verified_6_arms_2_seeds",
            "hardening": "L1early+L2perarm+L3outertry+L4importsentinel+META_AF+META_AH+META_AL+CARDINALITY",
            "load_bearing_finding": "tree_macros_NOT_compositional_at_depth_8_K_class_8_2nd_hierarchical_attempt_fails_Sutton_Precup_redesign_needed",
            "scope_observed": "smoke_2_seeds_N8160_blocks8_actions6_macros5_K_class8_goals30_depth8",
            "scope_not_claimed": "full_N_OR_3_plus_seeds_OR_mechanism_class_falsified_universally",
            "brain_analog": "Botvinick_Niv_option_framework_requires_learned_terminations_not_prespecified_macro_classes",
            "research_owned_redesign_pointer": "Sutton_Precup_options_framework_drill_ANCHOR_2",
            "zero_llm_calls_at_inference": True,
            "_llm_forward_calls_at_inference": 0,
            "substrate_only_decode_gate": "PASS",
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# ATOM 4 -- META_RULE_AN cone-collapse-formula-N2048-calibrated discipline meta
# ============================================================================

def build_atom4_meta_rule_an() -> Atom:
    return Atom(
        id=(
            "META_RULE_AN_cone_collapse_formula_crosstalk_std_sqrt_V_C_per_hop_minus_1_over_N_"
            "calibrated_at_N2048_does_NOT_naively_extrapolate_to_N8192_observed_BASELINE_0p590_"
            "predicted_0p160_off_by_3p7x_UPWARD_substrate_has_MORE_headroom_at_larger_N_than_"
            "linear_cone_model_predicts_recalibration_required_BEFORE_using_formula_to_design_"
            "harder_regime_cells_at_N_gt_2048_evidence_partition_oracle_revival_c1_N2048_baseline_"
            "0p190_in_rail_AND_revival_c1_N8192_baseline_0p590_rail_breach_UPWARD_extends_META_"
            "RULE_AL_substrate_already_does_X_at_capacity_layer_meta_discipline_first_atomized_2026-06-28"
        ),
        name=(
            "META_RULE_AN cone-collapse-formula-N2048-calibrated: crosstalk_std=sqrt((V_C_per_hop-1)/N) "
            "calibrated at N=2048 does NOT naively extrapolate to N=8192; substrate has ~3.7x MORE "
            "headroom at larger N than linear cone model predicts; recalibration required before "
            "using formula to design cells at N>2048; extends META_RULE_AL at capacity layer"
        ),
        description=(
            "META_RULE_AN: META discipline atom (delta=0). Substrate-product process rule landed\n"
            "after Skunkworks batch 15 verify-off-data on Stage 3 morning revival wave (Atom 2\n"
            "above provides the concrete evidence).\n"
            "\n"
            "RULE STATEMENT:\n"
            "  The cone-collapse formula crosstalk_std = sqrt((V_C_per_hop - 1) / N) is calibrated\n"
            "  EMPIRICALLY at N=2048 and CANNOT be naively extrapolated to N>=8192 to predict\n"
            "  baseline top1 at depth-d multi-hop cleanup. Substrate has substantially more\n"
            "  effective headroom at larger N than the linear-in-(V_C/N) cone model implies;\n"
            "  any cell designed using the formula at N>=8192 to set BASELINE rails must include\n"
            "  an EMPIRICAL recalibration arm (e.g. a baseline-only smoke at the target N before\n"
            "  the mechanism arms are dispatched) so the rails are tight.\n"
            "\n"
            "EVIDENCE (off-disk; from batch 15 Atoms 1 and 2):\n"
            "  At N=2048 V_C=1000 depth=10 (Atom 1):\n"
            "    Formula predicted BASELINE top1 ~ 0.160; observed 0.190 (in rail [0.110, 0.210]).\n"
            "    Formula tight.\n"
            "  At N=8192 V_C=4000 depth=10 (Atom 2):\n"
            "    Formula predicted BASELINE top1 ~ 0.160 (RAIL set to [0.110, 0.250] explicitly\n"
            "    using the v1 calibration); observed 0.590.\n"
            "    Rail breached UPWARD by factor 0.590/0.160 ~ 3.7x.\n"
            "  Mechanism arms (ORACLE_B/C/D) all saturated at 1.000/1.000/0.990 -- the saturation\n"
            "  itself prevents chain-grade promotion in the c1 N=8192 attempt; without the formula\n"
            "  miscalibration the RAIL would have been set in [0.40, 0.80] (matching observed) and\n"
            "  the un-saturated mechanism band would have been pushed to [0.85, 0.99].\n"
            "\n"
            "CANDIDATE ROOT CAUSE (research-owned to investigate; cert-owner does NOT prescribe):\n"
            "  Per-hop attrition is not linear in (V_C/N) ratio at the scale tested. Either:\n"
            "  (a) Effective decoder margin has sub-linear N dependence due to angular density\n"
            "      of substrate basis at higher N (cone vertex isn't the binding constraint).\n"
            "  (b) The cleanup operator has a fixed-point absorption term not modeled by per-hop\n"
            "      crosstalk_std.\n"
            "  (c) V_C scaling (1000 -> 4000) compensates the N scaling (2048 -> 8192) less than\n"
            "      1:1, but the cleanup tail is sub-Gaussian in the regime tested.\n"
            "\n"
            "DISCIPLINE IMPLICATION:\n"
            "  Before dispatching a v5-revival OR any cell using cone-collapse to set RAILS at\n"
            "  N >= 4096:\n"
            "    REQUIRED: run a baseline-only single-arm smoke (e.g. arm_a equivalent) at the\n"
            "    target N first to empirically determine BASELINE top1 + set RAIL [BASELINE +/-\n"
            "    band] EMPIRICALLY rather than from formula.\n"
            "    OR: include the baseline arm as part of the smoke and treat RAIL pre-check as\n"
            "    a guard not as a HP/HF gate when formula confidence is unverified at the N scale.\n"
            "\n"
            "RELATION TO OTHER META RULES:\n"
            "  Extends META_RULE_AL (substrate cosine kernel pre-encodes schema prior) at the\n"
            "  capacity layer: just as cosine geometry already-aligns schemas, substrate per-hop\n"
            "  cleanup already-resolves more multi-hop crosstalk at scale than the simple cone\n"
            "  model captures.\n"
            "  Extends META_RULE_AM (substrate-already-does-X test discipline) at the formula\n"
            "  layer: substrate-already-does-X applies not just to mechanism cells but to the\n"
            "  formulas we use to size them.\n"
            "  Companion to META_RULE_AH (atomic metrics): in this case the atomic per-hop top1\n"
            "  per-step accuracy lists (e.g. [0.96, 0.92, 0.86, ..., 0.59] at N=8192 baseline)\n"
            "  immediately show the substrate retains substantially more per-hop accuracy at\n"
            "  larger N than the formula assumes.\n"
            "\n"
            "VERIFIED-OFF-DATA EVIDENCE POINTERS:\n"
            "  Atom 1 (N=2048 calibration tight): data/exp_substrate_multihop_partition_oracle_\n"
            "    at_v5_regime_revival_c1_smoke/metrics.json arm_a_baseline.top1=0.190\n"
            "  Atom 2 (N=8192 formula miscalibration): data/exp_substrate_multihop_partition_\n"
            "    oracle_at_v5_regime_revival_c1_n8192/metrics.json arm_a_baseline.top1=0.590\n"
            "    rail_observed=0.590 vs rail_predicted=[0.110, 0.250]\n"
            "\n"
            "FIRST ATOMIZED 2026-06-28 by Skunkworks batch 15 landed-VET (.venv off-data recompute).\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE",
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "rule_id": "META_RULE_AN",
            "rule_topic": "cone_collapse_formula_calibrated_at_N2048_no_naive_extrapolation_to_larger_N",
            "rule_layer": "capacity_formula_calibration",
            "evidence_atoms": [
                "T3/EXP_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_N2048_MEASURED_MECHANISM_smoke",
                "T3/EXP_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_N8192_MEASURED_MECHANISM_smoke",
            ],
            "calibration_tight_at_N_MEASURED": 2048,
            "calibration_broken_at_N_MEASURED": 8192,
            "predicted_baseline_at_broken_N_MEASURED": 0.160,
            "observed_baseline_at_broken_N_MEASURED": 0.590,
            "calibration_breach_ratio_MEASURED": 3.7,
            "extends_META_RULE_AL_capacity_layer": True,
            "extends_META_RULE_AM_formula_layer": True,
            "companion_META_RULE_AH_atomic_per_hop_evidence": True,
            "verified_off_data": True,
            "first_atomized_ts": "2026-06-28",
            "ruling_note": RULING_NOTE,
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# A5 invariants
# ============================================================================

def _cert_count(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )


def main(argv):
    apply = "--apply" in argv
    mode = "APPLY" if apply else "DRY"
    print(f"[batch15] mode={mode}")

    store = PartitionedStore(STORE_ROOT)

    pre_cert_n = _cert_count(store)
    print(f"[batch15] PRE cert_n={pre_cert_n}")
    assert pre_cert_n == 628, f"PRE cert_n {pre_cert_n} != 628 expected"

    atoms = [
        build_atom1_po_n2048_mm(),
        build_atom2_po_n8192_mm(),
        build_atom3_hier_scdj_honest_neg(),
        build_atom4_meta_rule_an(),
    ]

    for i, a in enumerate(atoms, 1):
        print(f"[batch15] Atom {i}: id_head={str(a.id)[:80]}... corpus={a.corpus.name} tier={a.tier.name} kind={a.kind.name}")

    if not apply:
        print("[batch15] DRY mode -- no Store / ledger writes. Re-run with --apply.")
        return 0

    # ============================================================
    # APPLY: Atom adds + ledger rows (A5 PRE/POST window per write)
    # ============================================================
    expected_n = pre_cert_n  # delta=0 (all MM/honest_neg/meta)

    print("[batch15] Writing Atom 1 (PO N=2048 MM)...")
    store.add_atom(atoms[0])
    post_n_1 = _cert_count(store)
    assert post_n_1 == expected_n, f"After Atom 1: cert_n={post_n_1} != {expected_n}"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{atoms[0].id}",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "SMOKE_HARD_PASS_BIAS_Q_AUTO_DEMOTE",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_PO_N2048,
                "atom_qualified_id": f"math::{atoms[0].id}",
            },
            "supersedes": None,
            "note": "batch15_partition_oracle_revival_c1_N2048_MM_saturation_auto_demote_barrier1_mechanism_class_validated_lift_B_A_0p81",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )

    print("[batch15] Writing Atom 2 (PO N=8192 MM)...")
    store.add_atom(atoms[1])
    post_n_2 = _cert_count(store)
    assert post_n_2 == expected_n, f"After Atom 2: cert_n={post_n_2} != {expected_n}"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{atoms[1].id}",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "MIDDLE_BAND_SATURATED_AUTO_DEMOTE",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_PO_N8192,
                "atom_qualified_id": f"math::{atoms[1].id}",
            },
            "supersedes": None,
            "note": "batch15_partition_oracle_revival_c1_N8192_MM_baseline_rail_breach_UPWARD_3p7x_formula_misclibrated_feeds_META_RULE_AN",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )

    print("[batch15] Writing Atom 3 (Hierarchical SC-DJ HONEST_NEG)...")
    store.add_atom(atoms[2])
    post_n_3 = _cert_count(store)
    assert post_n_3 == expected_n, f"After Atom 3: cert_n={post_n_3} != {expected_n}"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{atoms[2].id}",
            "cert_status": "honest_negative",
            "cert_class": "proven_negative_smoke",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "HARD_FAIL",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_HIER_SCDJ,
                "atom_qualified_id": f"math::{atoms[2].id}",
            },
            "supersedes": None,
            "note": "batch15_hierarchical_planner_state_cond_disjoint_HONEST_NEG_2nd_attempt_macros_hurt_flat_baseline_neg_0p067_Sutton_Precup_options_drill_ANCHOR_2_redesign_needed",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )

    print("[batch15] Writing Atom 4 (META_RULE_AN cone-collapse-formula-calibration)...")
    store.add_atom(atoms[3])
    post_n_4 = _cert_count(store)
    assert post_n_4 == expected_n, f"After Atom 4: cert_n={post_n_4} != {expected_n}"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"meta::{atoms[3].id}",
            "cert_status": "discipline_meta",
            "cert_class": "discipline_meta",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "META_RULE_NEUTRAL",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": "n/a-meta-rule-derived-from-Atom1-and-Atom2",
                "atom_qualified_id": f"meta::{atoms[3].id}",
            },
            "supersedes": None,
            "note": "batch15_META_RULE_AN_cone_collapse_formula_N2048_calibrated_no_extrapolate_to_N8192_3p7x_off_extends_AL_AM_at_capacity_layer",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )

    final_cert_n = _cert_count(store)
    print(f"[batch15] FINAL cert_n={final_cert_n} (pre={pre_cert_n}, delta=0; 2 MM + 1 HONEST_NEG + 1 META)")
    assert final_cert_n == expected_n

    # Round-trip verify: each atom should reload
    store_verify = PartitionedStore(STORE_ROOT)
    for a in atoms:
        match = [x for x in store_verify.all_atoms() if x.id == a.id]
        assert len(match) == 1, f"Round-trip FAIL for atom id={a.id} (found {len(match)})"
        assert (match[0].metadata or {}).get("atomized_by") == ATOMIZED_BY
        print(f"[batch15] Round-trip OK: {a.id[:60]}...")

    print("[batch15] APPLY OK -- 4 atoms landed; ledger 4 rows appended; cert_n unchanged at 628.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
