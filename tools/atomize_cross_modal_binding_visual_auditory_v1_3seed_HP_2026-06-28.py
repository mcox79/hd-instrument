"""
A5-gated atomize: cross-modal binding visual-auditory v1 (3 seeds x HARD_PASS)

Stage 3 cross-modal binding (TPJ-analog) characterization.
3 sibling cells (seeds 7, 13, 19) x HARD_PASS via:
  - disc_pts (BIND_CROSS - NO_BIND >= 0.40 lift): 18/45 each seed (>=10 required)
  - cw_match_pts (|BIND_CROSS - WITHIN| <= 0.20):  35/34/35 (>=10 required)
  - pos_ctrl (K=10, N=8192, HRR): 1.0 / 1.0 / 1.0 (>=0.95 required)
  - cardinality_ok: True (2700 == 2700) each seed
  - all_saturated: False each seed (passes by-construction-saturation gate)

Mechanism-class breakdown (independent off-disk recompute by skunkworks):
  - HRR_bind:           10-11 / 15 disc-points (mechanism works; K-cliff present)
  - position_key_bind:   7-8  / 15 disc-points (partial; K-cliff present)
  - sum_then_query:      0    / 15 disc-points (BROKEN as predicted - mechanism not load-bearing)

K-cliff observed (HRR_bind, averaged over N):
  - seed_7:  K=10 BIND_CROSS=1.000  K=1000 BIND_CROSS=0.200
  - seed_13: K=10 BIND_CROSS=1.000  K=1000 BIND_CROSS=0.117
  - seed_19: K=10 BIND_CROSS=1.000  K=1000 BIND_CROSS=0.133

TIER DECISION (per Skunkworks-2026-06-22 default-MM-let-cert-owner-tier-up):
  Cross-modal HRR_bind = SAME PRIMITIVE as sequence_binding chain-grade
  (HRR FFT bind is commutative + codebooks are i.i.d. random bipolar).
  Pre-reg authors explicitly state: "HARD_PASS = trivial (substrate supports
  cross-modal HRR-bind by codebook symmetry)". This is NOT a new chain-grade
  primitive break -- it's a SUBSTRATE-PROPERTY characterization (Stage 3
  capability-table fill: UNTESTED -> CHARACTERIZED).

  Per-seed atoms = mechanism_characterization (cert_status=middle_band, no CERT delta).
  Cross-seed AGG = substrate_property_characterization (cert_status=chain_grade
    at the Stage-3-capability-table-fill granularity; CERT +1 for STAGE 3
    cell filling UNTESTED slot, consistent with seqbind/g1b precedent of
    +1 per cross-seed AGG only).

  Rationale for CERT +1: this is a Stage 3 characteristics-table UNTESTED slot
  FILLED with 3-seed verified HARD_PASS. The hidden information is which
  mechanism class works (HRR_bind clean; pos_key partial; sum broken) -- that's
  the new substrate-property characterization. Same tier precedent as g1b
  capacity sweep CHAIN_GRADE entry: aggregation atom carries +1.

OFF-DATA RECOMPUTE (skunkworks, .venv python):
  Verified discriminator counts independently:
    seed=7:  disc=18>=10  cw_match=35>=10  pos_ctrl=1.0  all_sat=False  HARD_PASS
    seed=13: disc=18>=10  cw_match=34>=10  pos_ctrl=1.0  all_sat=False  HARD_PASS
    seed=19: disc=18>=10  cw_match=35>=10  pos_ctrl=1.0  all_sat=False  HARD_PASS
  Cardinality_ok recomputed: 3/3 seeds (observed_n=2700 == expected_n=2700)

Atoms created (4):
  1. seed_7  per-cell record (math, T3, mechanism_characterization)
  2. seed_13 per-cell record (math, T3, mechanism_characterization)
  3. seed_19 per-cell record (math, T3, mechanism_characterization)
  4. CROSS-SEED AGG (math, T3, substrate_property_characterization, CERT +1
     for Stage 3 capability-table-fill: cross-modal binding UNTESTED -> CHARACTERIZED)

A5 protocol:
  1. Pre-read line counts; build atoms + ledger rows
  2. tmp -> os.replace atomic append
  3. Verify-load: count delta = +1 each; tail-line round-trip; integrity-check all lines

Anchors:
  - metrics paths: data/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_{7,13,19}/metrics.json
  - prereg:        preregs/2026-06-28_substrate_cross_modal_binding_visual_auditory_v1.md
  - cell core:     experiments/_substrate_cross_modal_binding_visual_auditory_v1_core.py
  - cell siblings: experiments/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_{7,13,19}.py
  - commit:        a2d56443
"""
import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATH_7 = "data/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_7/metrics.json"
METRICS_PATH_13 = "data/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_13/metrics.json"
METRICS_PATH_19 = "data/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_19/metrics.json"
PREREG_PATH = "preregs/2026-06-28_substrate_cross_modal_binding_visual_auditory_v1.md"
CELL_CORE = "experiments/_substrate_cross_modal_binding_visual_auditory_v1_core.py"
CELL_PATH_7 = "experiments/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_7.py"
CELL_PATH_13 = "experiments/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_13.py"
CELL_PATH_19 = "experiments/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_19.py"

ATOMIZED_BY = "skunkworks_atomize_cross_modal_binding_visual_auditory_v1_3seed_HP_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "a2d56443"

# Independent off-data recompute by skunkworks (verified above)
PER_SEED = {
    7:  {"disc": 18, "cw_match": 35, "pos_ctrl": 1.0, "all_sat": False, "avg_lift": 0.400, "avg_cw_diff": 0.136, "observed_n": 2700, "elapsed_s": 31.35,
         "hrr_disc": 11, "pos_key_disc": 7,  "sum_disc": 0, "k10_hrr_avg": 1.000, "k1000_hrr_avg": 0.200},
    13: {"disc": 18, "cw_match": 34, "pos_ctrl": 1.0, "all_sat": False, "avg_lift": 0.392, "avg_cw_diff": 0.128, "observed_n": 2700, "elapsed_s": 31.63,
         "hrr_disc": 10, "pos_key_disc": 8, "sum_disc": 0, "k10_hrr_avg": 1.000, "k1000_hrr_avg": 0.117},
    19: {"disc": 18, "cw_match": 35, "pos_ctrl": 1.0, "all_sat": False, "avg_lift": 0.400, "avg_cw_diff": 0.123, "observed_n": 2700, "elapsed_s": 62.72,
         "hrr_disc": 10, "pos_key_disc": 8, "sum_disc": 0, "k10_hrr_avg": 1.000, "k1000_hrr_avg": 0.133},
}

# Sibling atom IDs (built first then cross-linked into AGG)
SEED7_ATOM_ID = "T3/EXP_substrate_cross_modal_binding_visual_auditory_v1_seed_7_HARD_PASS_TPJ_analog_HRR_bind_cross_modal_codebook_symmetry_disc_18_45_cw_match_35_45_pos_ctrl_1p0_2026-06-28"
SEED13_ATOM_ID = "T3/EXP_substrate_cross_modal_binding_visual_auditory_v1_seed_13_HARD_PASS_TPJ_analog_HRR_bind_cross_modal_codebook_symmetry_disc_18_45_cw_match_34_45_pos_ctrl_1p0_2026-06-28"
SEED19_ATOM_ID = "T3/EXP_substrate_cross_modal_binding_visual_auditory_v1_seed_19_HARD_PASS_TPJ_analog_HRR_bind_cross_modal_codebook_symmetry_disc_18_45_cw_match_35_45_pos_ctrl_1p0_2026-06-28"
AGG_ATOM_ID = "T3/EXP_substrate_cross_modal_binding_visual_auditory_v1_CROSS_SEED_AGG_3_of_3_HARD_PASS_Stage_3_TPJ_analog_capability_table_fill_HRR_bind_works_pos_key_partial_sum_then_query_broken_substrate_property_characterization_2026-06-28"


def _per_seed_atom(seed: int) -> dict:
    p = PER_SEED[seed]
    if seed == 7:
        atom_id = SEED7_ATOM_ID; metrics_path = METRICS_PATH_7; cell_path = CELL_PATH_7
    elif seed == 13:
        atom_id = SEED13_ATOM_ID; metrics_path = METRICS_PATH_13; cell_path = CELL_PATH_13
    elif seed == 19:
        atom_id = SEED19_ATOM_ID; metrics_path = METRICS_PATH_19; cell_path = CELL_PATH_19
    else:
        raise ValueError(seed)

    return {
        "id": atom_id,
        "name": (
            f"Cross-modal binding visual-auditory v1 seed_{seed} HARD_PASS "
            f"(Stage 3 TPJ-analog; HRR_bind cross-modal codebook symmetry; "
            f"disc={p['disc']}/45 cw_match={p['cw_match']}/45 pos_ctrl=1.0)"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "experiment_record",
        "description": (
            f"Stage 3 cross-modal binding (TPJ-analog) cell seed_{seed} of 3. "
            f"Tests cross-modal HRR_bind / sum_then_query / position_key_bind across "
            f"K in {{10,50,100,500,1000}} x N in {{2048,4096,8192}} (45 phase points) with "
            f"3 discriminator arms (BIND_CROSS_MODAL / NO_BIND_BASELINE / WITHIN_MODAL_BIND_CONTROL). "
            f"OFF-DATA recompute: disc_pts={p['disc']}/45 (>=10 PASS); "
            f"cw_match_pts={p['cw_match']}/45 (>=10 PASS); pos_ctrl K=10 N=8192 HRR={p['pos_ctrl']} (>=0.95 PASS); "
            f"avg_lift={p['avg_lift']}; avg_cw_diff={p['avg_cw_diff']}; saturated=False (passes by-construction-saturation "
            f"gate). Cardinality observed_n={p['observed_n']} == expected_n=2700 PASS. "
            f"Mechanism-class breakdown: HRR_bind {p['hrr_disc']}/15 disc (mechanism works); "
            f"position_key_bind {p['pos_key_disc']}/15 (partial); sum_then_query {p['sum_disc']}/15 (BROKEN as predicted). "
            f"HRR K-cliff: K=10 BIND_CROSS avg={p['k10_hrr_avg']} (codebook-symmetric ceiling); "
            f"K=1000 BIND_CROSS avg={p['k1000_hrr_avg']} (cliff observed; consistent with sequence_binding K-cliff "
            f"capacity scaling sqrt(N/4)). Rolls up via 3-seed aggregation to Stage 3 capability-table fill "
            f"(substrate_property_characterization at cross-seed AGG tier; this per-cell atom is "
            f"mechanism_characterization at single-cell tier per chunked-architecture precedent). "
            f"Elapsed: {p['elapsed_s']}s on torch.cpu. Substrate-only inference (zero LLM calls)."
        ),
        "aliases": [
            f"substrate_cross_modal_binding_visual_auditory_v1_seed_{seed}_HARD_PASS_2026-06-28",
            f"cross_modal_binding_v1_seed_{seed}_TPJ_analog_HRR_bind_codebook_symmetry_2026-06-28",
            f"stage_3_cross_modal_TPJ_analog_seed_{seed}_disc_18_45_cw_match_3X_pos_ctrl_1p0",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "middle_band",
            "cert_class": "mechanism_characterization",
            "verdict": "HARD_PASS",
            "verdict_subtype": "STAGE_3_CROSS_MODAL_BINDING_HRR_BIND_PER_CELL_HP_PROMOTES_AT_CROSS_SEED_TO_SUBSTRATE_PROPERTY_CHARACTERIZATION",
            "cell_commit": CELL_COMMIT,
            "cell_path": cell_path,
            "cell_core_path": CELL_CORE,
            "prereg_path": PREREG_PATH,
            "metrics_path": metrics_path,
            "atomized_by": ATOMIZED_BY,
            "atomized_date": ATOMIZED_DATE,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                f"OFF-DATA recompute via .venv python on summary_per_phase_point: "
                f"disc_pts (BIND_CROSS-NO_BIND >= 0.40) = {p['disc']} of 45 >= 10 PASS; "
                f"cw_match_pts (|BIND_CROSS-WITHIN| <= 0.20) = {p['cw_match']} of 45 >= 10 PASS; "
                f"pos_ctrl K=10 N=8192 HRR_bind = {p['pos_ctrl']} >= 0.95 PASS; "
                f"all_saturated = False (passes by-construction gate); "
                f"cardinality_ok = True ({p['observed_n']} == 2700); "
                f"mechanism-class disc: HRR={p['hrr_disc']}/15 pos_key={p['pos_key_disc']}/15 sum=0/15 "
                f"(HRR works; pos_key partial; sum broken as predicted)."
            ),
            "n_seeds_run": 1,
            "n_seeds_planned_total": 3,
            "seed": seed,
            "regime": {
                "K_VALUES": [10, 50, 100, 500, 1000],
                "N_VALUES": [2048, 4096, 8192],
                "BIND_MECHANISMS": ["HRR_bind", "sum_then_query", "position_key_bind"],
                "DISCRIMINATOR_ARMS": ["BIND_CROSS_MODAL", "NO_BIND_BASELINE", "WITHIN_MODAL_BIND_CONTROL"],
                "V_MOD_A": 2048,
                "V_MOD_B": 2048,
                "V_POS": 2048,
                "N_QUERIES_FULL": 20,
                "n_phase_points": 45,
                "backend": "torch.cpu",
                "n_records_per_seed": 2700,
            },
            "per_seed_headlines": {
                "disc_pts_of_45_ge_0p40_lift": p["disc"],
                "cw_match_pts_of_45_le_0p20_diff": p["cw_match"],
                "pos_ctrl_recall": p["pos_ctrl"],
                "avg_bind_minus_nobind_lift": p["avg_lift"],
                "avg_cross_vs_within_abs_diff": p["avg_cw_diff"],
                "all_saturated_HP_block": p["all_sat"],
                "hrr_bind_disc_pts_of_15": p["hrr_disc"],
                "position_key_bind_disc_pts_of_15": p["pos_key_disc"],
                "sum_then_query_disc_pts_of_15": p["sum_disc"],
                "hrr_k10_BIND_CROSS_avg_over_N": p["k10_hrr_avg"],
                "hrr_k1000_BIND_CROSS_avg_over_N": p["k1000_hrr_avg"],
                "elapsed_s": p["elapsed_s"],
            },
            "gates_evaluated": {
                "disc_ge_10": True,
                "cw_match_ge_10": True,
                "pos_ctrl_ge_0p95": True,
                "not_all_saturated": True,
                "cardinality_ok": True,
                "arms_distinct_3_arms_BIND_NOBIND_WITHIN": True,
                "no_silent_except_no_phantom_zero_filled_units": True,
            },
            "cert_increment_delta": 0,
            "stage_3_table_fill_status": "FILL_PROMOTED_AT_CROSS_SEED_AGG_TIER_to_substrate_property_characterization",
            "discipline_tags": [
                "META_RULE_AC", "META_RULE_AE", "META_RULE_AF",
                "META_RULE_H", "META_RULE_J", "META_RULE_L",
                "BIAS-Q_pos_ctrl_K10_N8192_1p0_in_pre_reg_expected_not_leakage",
                "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
                "Fix_28_per_arm_metrics_not_verdict_msg",
                "stage_3_compositional_understanding_USER_2026-06-26",
                "chunked_per_seed_architecture_USER_2026-06-28",
                "substrate_as_canonical_query_first_USER_2026-06-27",
                "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
            ],
            "supersedes": None,
            "ts_iso_atomized": ATOMIZED_DATE,
        },
    }


atom_seed7 = _per_seed_atom(7)
atom_seed13 = _per_seed_atom(13)
atom_seed19 = _per_seed_atom(19)


# Cross-seed AGG atom -- substrate_property_characterization with CERT +1
atom_agg = {
    "id": AGG_ATOM_ID,
    "name": (
        "Cross-modal binding visual-auditory v1 CROSS-SEED 3-of-3 HARD_PASS -- "
        "Stage 3 TPJ-analog capability-table fill (UNTESTED -> CHARACTERIZED); "
        "HRR_bind cross-modal works (codebook-symmetric); pos_key partial; sum broken; "
        "substrate_property_characterization; CERT +1"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "substrate_property_characterization",
    "description": (
        "Stage 3 cross-modal binding (TPJ-analog) CHARACTERIZATION via 3-seed cross-validation "
        "(seeds 7, 13, 19). Each seed independently lands HARD_PASS on the same phase-diagram sweep: "
        "K in {10,50,100,500,1000} x N in {2048,4096,8192} x mech in {HRR_bind, sum_then_query, position_key_bind} "
        "(45 phase points x 3 arms x 20 queries = 2700 records per seed; cardinality_ok=True all 3 seeds). "
        "Per-seed discriminator: disc_pts=18/45 each seed (>=10 required); "
        "cw_match_pts=35/34/35 (>=10 required); pos_ctrl K=10 N=8192 HRR=1.0 each seed (>=0.95). "
        "Mechanism-class summary (independent off-data recompute by skunkworks): "
        "HRR_bind disc 10-11/15 (codebook-symmetric; cross-modal HRR_bind == within-modal HRR_bind "
        "at low K; K-cliff observed at K~500-1000 consistent with sequence_binding chain-grade primitive); "
        "position_key_bind disc 7-8/15 (partial mechanism; K-cliff present); "
        "sum_then_query disc 0/15 (BROKEN as predicted in pre-reg -- naive superposition has no cross-modal "
        "addressing). HRR K-cliff (averaged over N): K=10 BIND_CROSS=1.000 across all 3 seeds (codebook-symmetric "
        "ceiling); K=1000 BIND_CROSS=0.117-0.200 across 3 seeds (cliff = HRR capacity bound sqrt(N/4)). "
        "INTERPRETATION: cross-modal binding is a SUBSTRATE-PROPERTY CHARACTERIZATION rather than a new "
        "primitive break -- HRR FFT bind is commutative + independent codebooks are i.i.d. random bipolar, "
        "so cross-modal HRR_bind is the SAME PRIMITIVE as sequence_binding chain-grade (math::T3/"
        "EXP_substrate_sequence_binding...) applied to TWO codebooks instead of one. The pre-reg explicitly "
        "states the expected outcome ('HARD_PASS = trivial; substrate supports cross-modal HRR-bind by codebook "
        "symmetry'). What's NEW here is the mechanism-class characterization: HRR works; pos_key partial; sum "
        "broken. This fills the BACKUP UPDATE #25 characteristics-table Stage 3 'Cross-modal binding' entry "
        "(was UNTESTED) with 3-seed verified evidence. "
        "CERT +1 at the Stage 3 capability-table-fill granularity (per g1b/seqbind precedent of +1 per cross-seed "
        "AGG only). Brain analog: TPJ multisensory integration; substrate primitive demonstrates the algebraic "
        "structure that supports this capability at compositional-understanding (Stage 3) level. "
        "M3 IMPLICATION: cross-modal entity binding is a free substrate property (no new mechanism needed; "
        "downstream multimodal cells can rely on HRR_bind cross-modal at K<=O(sqrt(N/4)). Capacity-bounded "
        "(K=1000 cliff at all 3 N tested)."
    ),
    "aliases": [
        "cross_modal_binding_visual_auditory_v1_CROSS_SEED_AGG_3_of_3_HARD_PASS_2026-06-28",
        "stage_3_TPJ_analog_capability_table_fill_2026-06-28",
        "cross_modal_HRR_bind_substrate_property_characterization_codebook_symmetric_2026-06-28",
        "BACKUP_UPDATE_25_cross_modal_binding_UNTESTED_to_CHARACTERIZED_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "chain_grade",
        "cert_class": "substrate_property_characterization",
        "verdict": "CROSS_SEED_3_OF_3_HARD_PASS_STAGE_3_CROSS_MODAL_BINDING_TPJ_ANALOG_CHARACTERIZED",
        "verdict_subtype": "SUBSTRATE_PROPERTY_CHARACTERIZATION_HRR_BIND_CODEBOOK_SYMMETRIC_NOT_NEW_PRIMITIVE_TRIVIAL_EXTENSION_OF_SEQUENCE_BINDING_CHAIN_GRADE_PRIMITIVE_TO_TWO_INDEPENDENT_CODEBOOKS_PER_PREREG_EXPECTED_OUTCOME",
        "cell_commit": CELL_COMMIT,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on all 3 sibling metrics.json: "
            "seed_7  disc=18/45 cw_match=35/45 pos_ctrl=1.0 all_sat=False cardinality_ok=True; "
            "seed_13 disc=18/45 cw_match=34/45 pos_ctrl=1.0 all_sat=False cardinality_ok=True; "
            "seed_19 disc=18/45 cw_match=35/45 pos_ctrl=1.0 all_sat=False cardinality_ok=True; "
            "Mechanism-class: HRR=11/10/10 of 15; pos_key=7/8/8 of 15; sum=0/0/0 of 15 (broken as predicted). "
            "HRR K-cliff confirmed all 3 seeds (K=10 BIND_CROSS=1.0; K=1000 BIND_CROSS=0.117-0.200). "
            "All 3 per-seed verdicts independently confirmed HARD_PASS by skunkworks."
        ),
        "n_seeds_run": 3,
        "n_seeds_planned_total": 3,
        "seeds_landed": [7, 13, 19],
        "per_seed_atom_ids": {
            "seed_7": f"math::{SEED7_ATOM_ID}",
            "seed_13": f"math::{SEED13_ATOM_ID}",
            "seed_19": f"math::{SEED19_ATOM_ID}",
        },
        "per_seed_metrics_paths": {
            "seed_7": METRICS_PATH_7,
            "seed_13": METRICS_PATH_13,
            "seed_19": METRICS_PATH_19,
        },
        "regime": {
            "K_VALUES": [10, 50, 100, 500, 1000],
            "N_VALUES": [2048, 4096, 8192],
            "BIND_MECHANISMS": ["HRR_bind", "sum_then_query", "position_key_bind"],
            "DISCRIMINATOR_ARMS": ["BIND_CROSS_MODAL", "NO_BIND_BASELINE", "WITHIN_MODAL_BIND_CONTROL"],
            "V_MOD_A": 2048,
            "V_MOD_B": 2048,
            "V_POS": 2048,
            "n_phase_points_per_seed": 45,
            "n_records_per_seed": 2700,
            "n_records_aggregate": 8100,
            "backend": "torch.cpu",
            "elapsed_s_total": 125.7,
        },
        "cross_seed_stats": {
            "disc_pts_of_45_ge_0p40_lift": [18, 18, 18],
            "cw_match_pts_of_45_le_0p20_diff": [35, 34, 35],
            "pos_ctrl_K10_N8192_HRR": [1.0, 1.0, 1.0],
            "avg_bind_minus_nobind_lift": [0.400, 0.392, 0.400],
            "avg_cross_vs_within_abs_diff": [0.136, 0.128, 0.123],
            "hrr_disc_pts_of_15": [11, 10, 10],
            "pos_key_disc_pts_of_15": [7, 8, 8],
            "sum_disc_pts_of_15": [0, 0, 0],
            "hrr_k10_BIND_CROSS_avg_over_N": [1.000, 1.000, 1.000],
            "hrr_k1000_BIND_CROSS_avg_over_N": [0.200, 0.117, 0.133],
            "all_3_seeds_HARD_PASS": True,
            "all_3_seeds_cardinality_ok": True,
        },
        "promotion_gate_evaluation": {
            "gate_text": (
                "3-of-3 seeds HARD_PASS via pre-registered discriminators (disc>=10, cw_match>=10, "
                "pos_ctrl>=0.95, not_all_saturated, cardinality_ok); mechanism-class structure (HRR works; "
                "pos_key partial; sum broken) coherent across all 3 seeds. Cross-modal HRR_bind is "
                "SAME PRIMITIVE as sequence_binding chain-grade applied to 2 codebooks (HRR FFT bind "
                "commutative + codebooks i.i.d.); pre-reg authors explicitly mark this as expected "
                "TRIVIAL HP outcome -- a SUBSTRATE-PROPERTY characterization, NOT a new chain-grade "
                "primitive break."
            ),
            "criteria_met": {
                "all_3_seeds_HARD_PASS": True,
                "all_3_seeds_cardinality_ok": True,
                "mechanism_class_structure_coherent": True,
                "K_cliff_observed_consistent_with_HRR_capacity_bound": True,
                "by_construction_saturation_gate_passed": True,
                "discriminator_survives_scale": True,
            },
            "tier_decision": "substrate_property_characterization_with_CERT_plus_1_at_capability_table_fill_granularity",
            "tier_rationale": (
                "Cross-modal HRR_bind = sequence_binding chain-grade primitive applied to two codebooks. "
                "Not a NEW primitive break (chain_grade_capability_break tier reserved for novel mechanism "
                "characterization e.g. Barrier 1 break). Tier = substrate_property_characterization; "
                "CERT +1 at Stage 3 capability-table-fill granularity matches g1b/seqbind precedent."
            ),
        },
        "stage_3_table_fill_status": "FILLED_UNTESTED_to_CHARACTERIZED_substrate_property_characterization",
        "stage_3_capability_table_entry": "cross_modal_binding_TPJ_analog",
        "brain_analog": "TPJ_multisensory_integration",
        "M3_implication": (
            "Cross-modal entity binding is a free substrate property under HRR_bind primitive. "
            "Downstream multimodal cells can rely on cross-modal HRR_bind at K <= O(sqrt(N/4)) cleanly "
            "without further chain-grade work. Capacity-bounded: K=1000 cliff at all 3 N tested. "
            "M3 architecture: TPJ-analog binding is substrate-resident (no new cortex layer needed for "
            "the binding op itself; cortex layer needed for SEMANTIC encoder feeding the codebooks)."
        ),
        "supersedes_legacy_atoms": [
            "math::T3/EXP_wave14_k4_cross_modal_binding_v1",
            "math::T3/EXP_wave14_k4_cross_modal_binding_v1_smoke",
        ],
        "supersedes_legacy_evidence_link": (
            "PRE_SUBSTRATE_BUILD era HF atoms wave14_k4_cross_modal_binding_v1 (K=4 killer regime; "
            "LEGACY_EXCERPT provenance) are SUPERSEDED by this substrate-era 3-seed HARD_PASS at K=10-1000 "
            "with 3 mechanism arms swept. The K=4 inverted-result killer was a different regime / framing; "
            "this atom records the modern characterization."
        ),
        "follow_up_drills": [
            "Higher N sweep (N=16384+) to push K-cliff out -- chain-grade-eligible regime for the HRR primitive (already characterized at 4096 in seqbind chain-grade)",
            "3-modality bind (V x A x somatosensory) -- tests whether codebook independence holds at higher arity",
            "Encoder integration: real semantic codebooks (BPE / SBERT) at the modality-A/B layer -- couples to M3 encoder track",
        ],
        "cert_increment_delta": 1,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF",
            "META_RULE_H", "META_RULE_J", "META_RULE_L",
            "BIAS-Q_pos_ctrl_1p0_in_pre_reg_expected_not_leakage",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "stage_3_compositional_understanding_USER_2026-06-26",
            "chunked_per_seed_architecture_USER_2026-06-28",
            "substrate_as_canonical_query_first_USER_2026-06-27",
            "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
            "feedback_capability_dev_is_goal_cert_grade_is_instrument_USER_2026-06-19",
            "M3_milestone_glass_box_conversational",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# Cert ledger rows -- ledger only CERT-counts on the AGG atom
_t0 = time.time()


def _ledger_row(idx: int, atom: dict, op: str, cert_status: str, cert_class: str, verdict: str, delta: int, note: str, metrics_path: str = None) -> dict:
    referent = {
        "atom_qualified_id": f"math::{atom['id']}",
        "prereg_path": PREREG_PATH,
        "cell_commit": CELL_COMMIT,
    }
    if metrics_path:
        referent["metrics_path"] = metrics_path
    return {
        "ts": _t0 + 0.001 * idx,
        "op": op,
        "atom_id": f"math::{atom['id']}",
        "cert_status": cert_status,
        "cert_class": cert_class,
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "cell_commit": CELL_COMMIT,
        "verdict": verdict,
        "cert_increment_delta": delta,
        "cv": None,
        "referent_pointer": referent,
        "supersedes": None,
        "note": note,
    }


ledger_seed7 = _ledger_row(
    0, atom_seed7, "cert_ruling", "middle_band", "mechanism_characterization",
    "HARD_PASS_per_cell_disc_18_45_cw_match_35_45_pos_ctrl_1p0_cardinality_ok_HRR_works_pos_key_partial_sum_broken_PROMOTES_at_cross_seed_AGG_to_substrate_property_characterization",
    0,
    "cross_modal_binding_visual_auditory_v1_seed_7_per_cell_HARD_PASS_promotes_at_cross_seed_AGG_to_substrate_property_characterization",
    metrics_path=METRICS_PATH_7,
)
ledger_seed13 = _ledger_row(
    1, atom_seed13, "cert_ruling", "middle_band", "mechanism_characterization",
    "HARD_PASS_per_cell_disc_18_45_cw_match_34_45_pos_ctrl_1p0_cardinality_ok_HRR_works_pos_key_partial_sum_broken_PROMOTES_at_cross_seed_AGG_to_substrate_property_characterization",
    0,
    "cross_modal_binding_visual_auditory_v1_seed_13_per_cell_HARD_PASS_promotes_at_cross_seed_AGG_to_substrate_property_characterization",
    metrics_path=METRICS_PATH_13,
)
ledger_seed19 = _ledger_row(
    2, atom_seed19, "cert_ruling", "middle_band", "mechanism_characterization",
    "HARD_PASS_per_cell_disc_18_45_cw_match_35_45_pos_ctrl_1p0_cardinality_ok_HRR_works_pos_key_partial_sum_broken_PROMOTES_at_cross_seed_AGG_to_substrate_property_characterization",
    0,
    "cross_modal_binding_visual_auditory_v1_seed_19_per_cell_HARD_PASS_promotes_at_cross_seed_AGG_to_substrate_property_characterization",
    metrics_path=METRICS_PATH_19,
)
ledger_agg = _ledger_row(
    3, atom_agg, "cert_ruling_promotion_substrate_property_characterization", "chain_grade",
    "substrate_property_characterization",
    "CROSS_SEED_3_OF_3_HARD_PASS_STAGE_3_CROSS_MODAL_BINDING_TPJ_ANALOG_CHARACTERIZED_substrate_property_characterization_CERT_plus_1_HRR_works_pos_key_partial_sum_broken_capability_table_UNTESTED_to_CHARACTERIZED",
    1,
    "cross_modal_binding_visual_auditory_v1_CROSS_SEED_3_of_3_HARD_PASS_substrate_property_characterization_CERT_plus_1_Stage_3_TPJ_analog_capability_table_fill",
)


def append_jsonl_a5(path: Path, new_row: dict, label: str):
    """Atomic append with verify-load + integrity-check."""
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"
    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")
    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id"), "round-trip id mismatch"
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id"), "round-trip atom_id mismatch"
    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp_path), str(path))
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1, f"count delta mismatch: {pre_count} -> {post_count}"
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], "tail id mismatch"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], "tail atom_id mismatch"
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")
    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    print(f"[A5] atom_seed7  = math::{atom_seed7['id'][:80]}...")
    print(f"[A5] atom_seed13 = math::{atom_seed13['id'][:80]}...")
    print(f"[A5] atom_seed19 = math::{atom_seed19['id'][:80]}...")
    print(f"[A5] atom_agg    = math::{atom_agg['id'][:80]}...")
    print(f"[A5] CERT delta = +1 (substrate_property_characterization at AGG; per-seed delta=0)")

    append_jsonl_a5(MATH_ATOMS, atom_seed7, "math/atoms.jsonl (seed_7)")
    append_jsonl_a5(MATH_ATOMS, atom_seed13, "math/atoms.jsonl (seed_13)")
    append_jsonl_a5(MATH_ATOMS, atom_seed19, "math/atoms.jsonl (seed_19)")
    append_jsonl_a5(MATH_ATOMS, atom_agg, "math/atoms.jsonl (CROSS-SEED AGG +1)")
    append_jsonl_a5(CERT_LEDGER, ledger_seed7, "meta/cert_ledger.jsonl (seed_7)")
    append_jsonl_a5(CERT_LEDGER, ledger_seed13, "meta/cert_ledger.jsonl (seed_13)")
    append_jsonl_a5(CERT_LEDGER, ledger_seed19, "meta/cert_ledger.jsonl (seed_19)")
    append_jsonl_a5(CERT_LEDGER, ledger_agg, "meta/cert_ledger.jsonl (AGG +1)")

    print(f"[A5] DONE OK; CERT delta = +1")
    print(f"[A5] Stage 3 capability-table 'cross_modal_binding' UNTESTED -> CHARACTERIZED (TPJ-analog)")


if __name__ == "__main__":
    main()
