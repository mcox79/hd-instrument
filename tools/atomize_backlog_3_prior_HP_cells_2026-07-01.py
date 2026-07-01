"""
A5-gated atomize: backlog 3 prior HP cells with NO cert-ledger atoms
(USER-directed backlog scour 2026-07-01).

Cell 1: lap3_7_n100_ensemble_cpu_v1 (2026-06-19; single-seed FULL HP)
Cell 2: lap9_population_substrate_cpu_v1 (2026-06-19; single-seed FULL HP)
Cell 3: phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1 (2026-06-26; 3-seed FULL SANITY_BREACH)

Substrate-KB concept-overlap check (per new 2026-07-01 discipline rule):
  - lap3_7 lap9 phase_diagram_capacity_sweep queries returned prior chunk-note
    references (PP-249, PP-274, prereg chunks) but NO cert-ledger atoms.
    Cert-gap CONFIRMED. Prior arc context preserved via note-chunks.

INDEPENDENT OFF-DATA VERIFICATION (skunkworks 2026-07-01):

Cell 1: lap3_7_n100_ensemble_cpu_v1
  run_mode=full; verdict=HARD_PASS; elapsed_s=75.4; n_seeds=1
  per_seed = [{'single': 0.7, 'ens10': 1.0, 'ens100': 1.0, 'gain100_pp': 30.0}]
  summary: N=100 substrate ensemble lifts noisy-recall by >=20pp over single;
    sqrt-N population-coding improvement holds to N=100.
  ENS10 = ENS100 = 1.000 (ceiling reached at N=10; N=100 saturates ceiling not extends)

  Off-data tier: MM_SINGLE_SEED. Substantive finding: sqrt-N population coding
  lifts single 0.700 -> ensemble 1.000 by N=10 (SATURATED); N=100 confirms
  saturation not extension. Single-seed prevents CG; cross-seed replication
  would enable CG if the gain is preserved.

Cell 2: lap9_population_substrate_cpu_v1
  run_mode=full; verdict=HARD_PASS; elapsed_s=17.9; n_seeds=1
  per_seed = [{'single_acc': 0.88, 'ensemble_acc': 1.0, 'gain_pp': 12.0, 'P': 10}]
  summary: N=10 substrate population (majority vote) beats single by >=5pp on
    noisy queries; biological population coding analog.

  Off-data tier: MM_SINGLE_SEED. Substantive: N=10 majority-vote ensemble +12pp.
  Baseline for lap3_7 N=100 saturation finding.

Cell 3: phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1
  run_mode=full; verdict=SANITY_BREACH; elapsed_s=39.4; n_seeds=3
  config: N=16384 VC_SWEEP=[2000, 4000, 8000] M_FACTS=[1500, 3000, 6000] V_REL=8
    seeds=[11, 13, 19] encoder=SUBSTRATE_NATIVE
  summary: SANITY_BREACH_KNN_SENTINEL_BELOW_0.90 KNN=0.3273 (knn_breach=3/3)
    VC_2000=1.0000 cv=0.000 VC_4000=1.0000 cv=0.000 VC_8000=1.0000 cv=0.000

  MECHANISM by itself would be CG-quality (3 VC values all recall=1.000, cv=0.000)
  BUT KNN control sentinel BREACH at 0.3273 (well below 0.90 required per Fix #28)
  disqualifies clean interpretation. Cannot distinguish 'substrate genuinely at
  ceiling at VC=8000' from 'KNN-baseline pathology masking true bound'.

  Off-data tier: MM_MEASURED_MECHANISM_WITH_CONTROL_BREACH (proven bound with
  caveat). Cannot lift to CG until KNN sentinel is either fixed to >=0.90 OR
  the KNN-breach is proven not-to-cause-VC-ceiling-artifact.

Tier counts today: 3 single/split MM; CERT delta=0 for all 3.
Cert-gap FILL rationale: substantive findings preserved via atomization even
without CG lift; useful for phase-diagram coverage documentation.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_backlog_VET_3_prior_HP_cells_USER_directed_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

# ============================================================================
# ATOM 1: lap3_7_n100_ensemble single-seed MM (backlog fill)
# ============================================================================
atom_lap3_7_n100 = {
    "id": (
        "T3/EXP_lap3_7_n100_ensemble_cpu_v1_single_seed_FULL_MM_"
        "population_coding_N_100_saturates_ens10_ens100_1p000_ceiling_"
        "gain_30pp_over_single_0p700_sqrt_N_lift_holds_to_ceiling_"
        "BACKLOG_ATOMIZE_USER_directed_2026-07-01_landed_2026-06-19"
    ),
    "name": (
        "MM_SINGLE_SEED backlog atomize lap3_7_n100_ensemble_cpu_v1: N=100 substrate "
        "ensemble lifts noisy-recall single 0.700 -> ensemble 1.000 (30pp gain; exceeds "
        "20pp HP threshold). Ceiling REACHED at N=10 (ens10=1.000=ens100); N=100 confirms "
        "saturation not extension. sqrt-N population-coding lift holds to ceiling. "
        "Single-seed FULL prevents CG per canonical rules. Extends PP-249 (N=10 baseline; "
        "companion atom this commit). Backlog fill; substantive finding preserved. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Backlog atomize of lap3_7_n100_ensemble_cpu_v1 (landed 2026-06-19; HP verdict never "
        "atomized). Substrate-KB query confirmed no prior Store atom exists (only note-chunk "
        "references in strategy_decisions_2026-06-09.md PP-274). Cert-gap FILL.\n"
        "\n"
        "OFF-DATA verification: run_mode=full; verdict=HARD_PASS; elapsed_s=75.4; n_seeds=1.\n"
        "per_seed = [{'single': 0.7, 'ens10': 1.0, 'ens100': 1.0, 'gain100_pp': 30.0}]\n"
        "\n"
        "SUBSTANTIVE FINDING: sqrt-N population coding lift saturates at N=10:\n"
        "  single = 0.700 (baseline noisy-recall)\n"
        "  ens10  = 1.000 (ceiling reached at N=10)\n"
        "  ens100 = 1.000 (N=100 confirms saturation; does not extend)\n"
        "  gain100_pp = 30 (exceeds pre-reg HP threshold >=20pp)\n"
        "\n"
        "TIER: MM_SINGLE_SEED. Substantive HP verdict at per-cell tier; but single-seed FULL "
        "prevents CG per canonical rules (CG requires cross-seed HP with cv<0.15 or equivalent). "
        "Cross-seed replication would enable CG if gain and saturation both preserved.\n"
        "\n"
        "PRIOR ARC CONTEXT (from substrate-KB):\n"
        "  PP-249 (companion atom this commit): lap9_population_substrate N=10 baseline\n"
        "  PP-274 (this): extends N=10 to N=100; saturation confirmed\n"
        "  Product implication (from note-chunks): substrate as population-coding primitive\n"
        "\n"
        "cert_increment_delta = 0. Backlog fill; substantive finding preserved."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM_SINGLE_SEED",
        "verdict": "HARD_PASS_single_seed_MM_per_canonical_rules",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python on metrics.json (local, landed 2026-06-19): "
            "run_mode=full; verdict=HARD_PASS; single=0.700 ens10=1.000 ens100=1.000 "
            "gain100_pp=30.0 exceeds 20pp threshold; ens10==ens100==1.000 confirms saturation "
            "at N=10; n_seeds=1 (single-seed FULL); substrate-KB query confirms no prior Store "
            "atom (only note-chunk references)"
        ),
        "regime": {"N_substrate_ensemble_sizes": [1, 10, 100], "task": "noisy_recall"},
        "metrics_path": "data/exp_lap3_7_n100_ensemble_cpu_v1/metrics.json",
        "landed_date": "2026-06-19",
        "per_seed_single_full_run": [{"single": 0.7, "ens10": 1.0, "ens100": 1.0, "gain100_pp": 30.0}],
        "saturation_at_N_10_ceiling_confirmed": True,
        "sqrt_N_population_coding_lift_saturates": True,
        "single_seed_prevents_CG_needs_cross_seed_replication": True,
        "backlog_fill_no_prior_Store_atom_per_substrate_KB_query": True,
        "extends_PP_249_baseline_companion_atom_this_commit": True,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "backlog_atomize_USER_directed_2026_07_01_cert_gap_fill",
            "MM_single_seed_per_canonical_rules_HP_verdict_only_at_per_cell_tier",
            "substrate_KB_query_first_confirms_no_prior_atom",
            "extends_PP_249_N_10_baseline",
            "sqrt_N_population_coding_saturates_at_N_10",
            "META_RULE_H_cardinality_ok_single_seed_ensemble_size_sweep_3",
            "stage_1_population_coding_capability_USER_LOCKED",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# ATOM 2: lap9_population_substrate single-seed MM (backlog fill)
# ============================================================================
atom_lap9_population = {
    "id": (
        "T3/EXP_lap9_population_substrate_cpu_v1_single_seed_FULL_MM_"
        "N_10_majority_vote_beats_single_by_12pp_gain_biological_population_coding_analog_"
        "single_0p880_ensemble_1p000_gain_12pp_exceeds_5pp_threshold_2p4x_"
        "BACKLOG_ATOMIZE_USER_directed_2026-07-01_landed_2026-06-19"
    ),
    "name": (
        "MM_SINGLE_SEED backlog atomize lap9_population_substrate_cpu_v1: N=10 majority-vote "
        "ensemble beats single by 12pp (single 0.880 -> ensemble 1.000; exceeds 5pp HP threshold "
        "by 2.4x). Biological population coding analog: independent encoding noise averages "
        "across ensemble. Baseline for lap3_7 N=100 saturation finding (companion atom). "
        "Single-seed FULL prevents CG. Backlog fill. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Backlog atomize of lap9_population_substrate_cpu_v1 (landed 2026-06-19; HP verdict "
        "never atomized). Substrate-KB query confirmed no prior Store atom (only note-chunk "
        "reference in strategy_decisions_2026-06-09.md PP-249). Cert-gap FILL.\n"
        "\n"
        "OFF-DATA verification: run_mode=full; verdict=HARD_PASS; elapsed_s=17.9; n_seeds=1.\n"
        "per_seed = [{'single_acc': 0.88, 'ensemble_acc': 1.0, 'gain_pp': 12.0, 'P': 10}]\n"
        "\n"
        "SUBSTANTIVE FINDING: N=10 majority-vote ensemble lifts single-substrate by 12pp:\n"
        "  single_acc   = 0.880 (baseline noisy-query accuracy)\n"
        "  ensemble_acc = 1.000 (N=10 majority vote reaches ceiling)\n"
        "  gain_pp      = 12 (exceeds pre-reg HP threshold >=5pp by 2.4x)\n"
        "  P            = 10 (ensemble size)\n"
        "\n"
        "TIER: MM_SINGLE_SEED. HP per-cell; single-seed prevents CG.\n"
        "\n"
        "BASELINE FOR: lap3_7_n100_ensemble (companion atom this commit) which extends N=10 "
        "to N=100 and confirms saturation. This atom + lap3_7 together characterize the sqrt-N "
        "population-coding curve at chain-grade-quality-per-cell but single-seed each.\n"
        "\n"
        "cert_increment_delta = 0."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM_SINGLE_SEED",
        "verdict": "HARD_PASS_single_seed_MM_per_canonical_rules",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python on metrics.json (local, landed 2026-06-19): "
            "run_mode=full; verdict=HARD_PASS; single_acc=0.880 ensemble_acc=1.000 gain_pp=12.0 "
            "P=10 exceeds 5pp threshold 2.4x; n_seeds=1 (single-seed FULL); substrate-KB query "
            "confirms no prior Store atom"
        ),
        "regime": {"P_ensemble_size": 10, "task": "noisy_query_accuracy",
                   "ensemble_method": "majority_vote"},
        "metrics_path": "data/exp_lap9_population_substrate_cpu_v1/metrics.json",
        "landed_date": "2026-06-19",
        "per_seed_single_full_run": [{"single_acc": 0.88, "ensemble_acc": 1.0, "gain_pp": 12.0, "P": 10}],
        "biological_population_coding_analog": True,
        "baseline_for_lap3_7_N_100_companion_atom_this_commit": True,
        "single_seed_prevents_CG_needs_cross_seed_replication": True,
        "backlog_fill_no_prior_Store_atom_per_substrate_KB_query": True,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "backlog_atomize_USER_directed_2026_07_01_cert_gap_fill",
            "MM_single_seed_per_canonical_rules",
            "substrate_KB_query_first_confirms_no_prior_atom",
            "baseline_for_lap3_7_N_100_extension_companion_atom",
            "biological_population_coding_analog_majority_vote_ensemble",
            "META_RULE_H_cardinality_ok",
            "stage_1_population_coding_capability_USER_LOCKED",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# ATOM 3: phase_diagram_capacity_sweep_n16384 MM_MEASURED_MECHANISM_WITH_CONTROL_BREACH
# ============================================================================
atom_phase_capacity_sweep = {
    "id": (
        "T3/EXP_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1_3seed_MM_"
        "MEASURED_MECHANISM_WITH_CONTROL_BREACH_KNN_SENTINEL_BELOW_0p90_"
        "KNN_0p3273_breach_3_of_3_VC_2000_recall_1p000_cv_0p000_VC_4000_recall_1p000_cv_0p000_"
        "VC_8000_recall_1p000_cv_0p000_mechanism_CG_quality_by_itself_KNN_control_disqualifies_clean_interpretation_"
        "cannot_distinguish_ceiling_from_KNN_artifact_BACKLOG_ATOMIZE_landed_2026-06-26_2026-07-01"
    ),
    "name": (
        "MM_MEASURED_MECHANISM_WITH_CONTROL_BREACH phase_diagram_capacity_sweep_n16384 3-seed "
        "FULL: mechanism CG-quality by itself (VC in {2000, 4000, 8000} all recall=1.000 "
        "cv=0.000 cross-seed) BUT KNN control sentinel BREACH at 0.3273 (well below 0.90 "
        "required per Fix #28) prevents clean CG interpretation. Cannot distinguish "
        "'substrate genuinely at ceiling at VC=8000' from 'KNN-baseline pathology masking "
        "true bound'. Backlog fill. Path to CG: fix KNN sentinel to >=0.90 OR prove KNN-breach "
        "does not cause VC-ceiling-artifact. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Backlog atomize of phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1 (landed "
        "2026-06-26; SANITY_BREACH verdict never atomized). Substrate-KB query confirmed no "
        "prior Store atom (only prereg-chunk references). Cert-gap FILL.\n"
        "\n"
        "OFF-DATA verification: run_mode=full; verdict=SANITY_BREACH; elapsed_s=39.4; n_seeds=3 "
        "(seeds=[11, 13, 19]); GPU torch.cuda NVIDIA RTX 4060 Ti.\n"
        "Config: N=16384 VC_SWEEP=[2000, 4000, 8000] M_FACTS=[1500, 3000, 6000] V_REL=8 "
        "M_FACTS/V_C ratio held at 0.75 (production-baseline); encoder=SUBSTRATE_NATIVE.\n"
        "\n"
        "SUBSTANTIVE FINDING (mechanism by itself CG-quality):\n"
        "  VC_2000: recall=1.000, cv=0.000 (all 3 seeds identical)\n"
        "  VC_4000: recall=1.000, cv=0.000 (all 3 seeds identical)\n"
        "  VC_8000: recall=1.000, cv=0.000 (all 3 seeds identical)\n"
        "  All 3 VC values at ceiling across all 3 seeds; capacity ceiling reached at\n"
        "  VC=8000 (top of tested range).\n"
        "\n"
        "CONTROL BREACH prevents CG lift:\n"
        "  KNN sentinel = 0.3273 (well below 0.90 required per Fix #28 discipline)\n"
        "  knn_breach = 3/3 (all 3 seeds show KNN below 0.90 sentinel)\n"
        "  Cell auto-emits SANITY_BREACH per pre-reg gate.\n"
        "\n"
        "INTERPRETATION: Cannot distinguish 'substrate genuinely at ceiling at VC=8000' from "
        "'KNN-baseline pathology (e.g., wrong distance metric, degenerate KNN structure) "
        "masking true VC bound'. The mechanism recall=1.000 might be:\n"
        "  (a) Genuine substrate at CG-quality ceiling (substrate truly retrieves all facts\n"
        "      at VC=8000 with substrate-native encoding)\n"
        "  (b) KNN-artifact: the recall metric fires as 1.000 because KNN comparison baseline\n"
        "      is broken; substrate might not actually be discriminating.\n"
        "\n"
        "TIER: MM_MEASURED_MECHANISM_WITH_CONTROL_BREACH. Substantive mechanism finding "
        "preserved but not CG-eligible until KNN sentinel is fixed.\n"
        "\n"
        "PATH TO CG:\n"
        "  (a) Fix KNN sentinel to >= 0.90 (investigate why KNN degenerate: wrong distance "
        "metric? degenerate KNN with only 8 relations V_REL=8? insufficient KNN warmup?)\n"
        "  (b) Prove KNN-breach does not cause VC-ceiling-artifact (e.g., swap in a different "
        "sanity control that fires clean at 0.90+)\n"
        "  (c) Test intermediate VC values (e.g., VC=6000, 10000) to see where ceiling breaks\n"
        "\n"
        "cert_increment_delta = 0."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM_WITH_CONTROL_BREACH",
        "verdict": "SANITY_BREACH_mechanism_CG_quality_by_itself_but_KNN_control_disqualifies",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python on metrics.json (local, landed 2026-06-26): "
            "run_mode=full; verdict=SANITY_BREACH; VC_2000 VC_4000 VC_8000 all recall=1.000 "
            "cv=0.000 cross-seed [11,13,19]; KNN sentinel=0.3273 well below 0.90 required; "
            "knn_breach=3/3; GPU torch.cuda; substrate-KB query confirms no prior Store atom"
        ),
        "regime": {"N": 16384, "VC_sweep": [2000, 4000, 8000], "M_FACTS": [1500, 3000, 6000],
                   "V_REL": 8, "seeds": [11, 13, 19], "encoder": "SUBSTRATE_NATIVE",
                   "M_FACTS_over_VC_ratio": 0.75, "backend": "torch.cuda"},
        "metrics_path": "data/exp_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1/metrics.json",
        "landed_date": "2026-06-26",
        "mechanism_CG_quality_by_itself": {
            "VC_2000": {"recall": 1.000, "cv": 0.000},
            "VC_4000": {"recall": 1.000, "cv": 0.000},
            "VC_8000": {"recall": 1.000, "cv": 0.000},
        },
        "KNN_control_breach": {
            "KNN_sentinel_observed": 0.3273,
            "KNN_sentinel_required": 0.90,
            "breach_ratio": "3/3 seeds",
            "Fix_28_discipline_reference": True,
        },
        "interpretation_ambiguity": {
            "option_a_genuine_ceiling": "substrate truly at CG-quality ceiling at VC=8000",
            "option_b_KNN_artifact": "recall=1.000 fires because KNN comparison baseline broken",
            "cannot_distinguish_without_KNN_fix": True,
        },
        "path_to_CG": {
            "(a)_fix_KNN_sentinel_to_ge_0p90": "investigate degenerate KNN causes",
            "(b)_prove_KNN_breach_not_cause_VC_artifact": "swap sanity control",
            "(c)_test_intermediate_VC_values": "e.g., VC=6000, 10000 to find ceiling break",
        },
        "backlog_fill_no_prior_Store_atom_per_substrate_KB_query": True,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "backlog_atomize_USER_directed_2026_07_01_cert_gap_fill",
            "MM_measured_mechanism_with_control_breach",
            "mechanism_CG_quality_by_itself_but_KNN_sentinel_disqualifies_clean_interpretation",
            "substrate_KB_query_first_confirms_no_prior_atom",
            "Fix_28_KNN_sentinel_discipline_reference",
            "META_RULE_AH_positive_control_at_KNN_below_0p90_breach_3_of_3_seeds",
            "META_RULE_H_cardinality_ok_3_seed_full_run",
            "phase_diagram_action_data_survives_phase_transformations_USER_2026-06-22",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================================
# CERT LEDGER ROWS
# ============================================================================
_t0 = time.time()

ledger_lap3_7_n100 = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_lap3_7_n100['id']}",
    "cert_status": "measured_mechanism_single_seed",
    "cert_class": "backlog_atomize_MM_single_seed_HP_verdict_per_cell_only",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_single_seed_HP_lap3_7_n100_ensemble_N_100_saturates_at_ens10_1p000_ens100_1p000_"
        "gain_30pp_over_single_0p700_exceeds_20pp_threshold_sqrt_N_lift_saturates_at_N_10_"
        "single_seed_prevents_CG_backlog_fill_extends_PP_249_baseline_landed_2026-06-19"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": "notes/strategy_decisions_2026-06-09.md (PP-274 row)",
        "metrics_path": "data/exp_lap3_7_n100_ensemble_cpu_v1/metrics.json",
        "atom_qualified_id": f"math::{atom_lap3_7_n100['id']}",
        "extends_baseline_atom": f"math::{atom_lap9_population['id']}",
    },
    "supersedes": None,
    "note": (
        "backlog_atomize_lap3_7_n100_ensemble_USER_directed_2026_07_01_cert_gap_fill_"
        "single_seed_MM_HP_verdict_per_cell_ens10_ens100_1p000_saturation_at_N_10_confirmed_"
        "gain_30pp_over_single_0p700_exceeds_20pp_threshold_"
        "extends_PP_249_N_10_baseline_lap9_population_companion_atom_same_commit_"
        "substrate_KB_query_first_confirms_no_prior_Store_atom_only_note_chunk_references"
    ),
}

ledger_lap9_population = {
    "ts": _t0 + 0.001,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_lap9_population['id']}",
    "cert_status": "measured_mechanism_single_seed",
    "cert_class": "backlog_atomize_MM_single_seed_HP_verdict_per_cell_only",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_single_seed_HP_lap9_population_N_10_majority_vote_gain_12pp_over_single_"
        "single_0p880_ensemble_1p000_exceeds_5pp_threshold_2p4x_biological_population_coding_analog_"
        "single_seed_prevents_CG_backlog_fill_baseline_for_lap3_7_N_100_landed_2026-06-19"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": "notes/strategy_decisions_2026-06-09.md (PP-249 row)",
        "metrics_path": "data/exp_lap9_population_substrate_cpu_v1/metrics.json",
        "atom_qualified_id": f"math::{atom_lap9_population['id']}",
        "baseline_for_extension_atom": f"math::{atom_lap3_7_n100['id']}",
    },
    "supersedes": None,
    "note": (
        "backlog_atomize_lap9_population_substrate_USER_directed_2026_07_01_cert_gap_fill_"
        "single_seed_MM_HP_verdict_per_cell_N_10_majority_vote_ensemble_1p000_vs_single_0p880_"
        "gain_12pp_exceeds_5pp_threshold_2p4x_biological_population_coding_analog_"
        "baseline_for_lap3_7_N_100_extension_companion_atom_same_commit_"
        "substrate_KB_query_first_confirms_no_prior_Store_atom"
    ),
}

ledger_phase_capacity_sweep = {
    "ts": _t0 + 0.002,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_phase_capacity_sweep['id']}",
    "cert_status": "measured_mechanism_with_control_breach",
    "cert_class": "backlog_atomize_MM_mechanism_CG_quality_by_itself_but_KNN_sentinel_disqualifies_clean_interpretation",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_MEASURED_MECHANISM_WITH_CONTROL_BREACH_phase_diagram_capacity_sweep_n16384_3seed_"
        "VC_2000_1p000_cv_0p000_VC_4000_1p000_cv_0p000_VC_8000_1p000_cv_0p000_mechanism_CG_quality_"
        "KNN_sentinel_0p3273_below_0p90_required_breach_3_of_3_disqualifies_clean_interpretation_"
        "cannot_distinguish_ceiling_from_KNN_artifact_path_to_CG_fix_KNN_or_swap_sanity_control_landed_2026-06-26"
    ),
    "cert_increment_delta": 0,
    "cv": 0.000,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1/metrics.json",
        "prereg_path": "preregs/2026-06-26_phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1.md",
        "atom_qualified_id": f"math::{atom_phase_capacity_sweep['id']}",
    },
    "supersedes": None,
    "note": (
        "backlog_atomize_phase_diagram_capacity_sweep_n16384_USER_directed_2026_07_01_cert_gap_fill_"
        "3_seed_full_mechanism_VC_2000_4000_8000_all_recall_1p000_cv_0p000_cross_seed_CG_quality_by_itself_"
        "KNN_sentinel_0p3273_below_0p90_required_Fix_28_discipline_breach_3_of_3_seeds_"
        "cannot_distinguish_substrate_genuine_ceiling_from_KNN_baseline_pathology_"
        "path_to_CG_fix_KNN_sentinel_or_swap_sanity_control_or_test_intermediate_VC_values_"
        "substrate_KB_query_first_confirms_no_prior_Store_atom_only_prereg_chunk_references"
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
    append_jsonl_a5(MATH_ATOMS, atom_lap9_population,         "math/atoms (lap9_population single-seed MM)")
    append_jsonl_a5(MATH_ATOMS, atom_lap3_7_n100,             "math/atoms (lap3_7_n100 single-seed MM)")
    append_jsonl_a5(MATH_ATOMS, atom_phase_capacity_sweep,    "math/atoms (phase_diagram_capacity_sweep 3-seed MM w/ KNN breach)")
    append_jsonl_a5(CERT_LEDGER, ledger_lap9_population,      "cert_ledger (lap9_population MM)")
    append_jsonl_a5(CERT_LEDGER, ledger_lap3_7_n100,          "cert_ledger (lap3_7_n100 MM)")
    append_jsonl_a5(CERT_LEDGER, ledger_phase_capacity_sweep, "cert_ledger (phase_capacity_sweep MM w/ breach)")
    print(f"[A5] DONE OK")
    print(f"[A5] 3 backlog atoms filed: 2 single-seed MM + 1 MM w/ KNN control breach")
    print(f"[A5] Substrate-KB query first confirmed all 3 had no prior Store atoms")
    print(f"[A5] CERT delta = 0 for all 3 (no CG-eligible per canonical rules)")


if __name__ == "__main__":
    main()
