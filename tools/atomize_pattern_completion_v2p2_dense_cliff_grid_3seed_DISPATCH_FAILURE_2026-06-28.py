"""
A5-gated atomize: pattern_completion_corruption_cliff_v2p2_dense_cliff_grid
3 seeds x HARD_FAIL -- but ROOT CAUSE = DISPATCH INFRASTRUCTURE FAILURE,
NOT substrate-mechanism failure.

DIAGNOSIS (off-disk read of all 3 metrics.json):
  Each seed's verdict = HARD_FAIL with verdict_msg:
    "HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden by Fix #24
     unless HDLAB_QUEUE=local_cpu_queue (USER explicit route). Got HDLAB_QUEUE=''. Refusing."
  Each seed's elapsed_s = 0.01 (cell refused at gpu_mandate_check phase BEFORE
  executing any substrate sweep).
  _phase = "gpu_mandate_check" (cell exited at line 192-203 of seed_7.py).

  The cell was DESIGNED to refuse FULL CPU runs unless HDLAB_QUEUE=local_cpu_queue
  is set by the runner. The pre-reg explicitly noted this dispensation (lines
  129-137 of preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid.md).

  The actual full-run dispatch did NOT set HDLAB_QUEUE=local_cpu_queue.
  Result: 3 seeds x cell-refusal sentinel WITHOUT any substrate sweep evidence.

  This is a TEST-DESIGN-INFRA-FAILURE classification per the test-design-failure
  rule (USER 2026-06-28): cell is well-formed; substrate state is UNKNOWN
  (sweep never ran); root cause = dispatch runner config gap.

NOT a substrate hypothesis HARD_FAIL. NOT a discriminator-threshold mismatch.
NOT a by-construction saturation/floor. NOT a code bug.

ROOT-CAUSE CATEGORY: dispatch_infrastructure_runner_env_var_unset
  Adjacent to: "effective != nominal parameter" (effective backend = cpu but
  effective queue env var = '' instead of 'local_cpu_queue')

RECOMMENDATION: dispatch v2.3 with HDLAB_QUEUE=local_cpu_queue set in the runner,
OR alternatively allow the cell's local_cpu_queue dispensation to default ON
when a torch.cpu backend is detected AND smoke gates pass AND user has not
opted into GPU-mandate-strict (an alternative would be to make the
gpu_mandate_check refusal more lenient OR provide a clearer error pointing
to the runner-side env-var fix).

Atoms created (4):
  1. seed_7  per-cell record (math, T3, dispatch_infrastructure_failure)
  2. seed_13 per-cell record (math, T3, dispatch_infrastructure_failure)
  3. seed_19 per-cell record (math, T3, dispatch_infrastructure_failure)
  4. CROSS-SEED AGG (math, T3, test_design_failure_dispatch_infra; no CERT delta;
     RECOMMENDS v2.3 with HDLAB_QUEUE=local_cpu_queue)

This is NOT a substrate hypothesis test outcome -- substrate hypothesis remains
OPEN. v2.1 MEASURED_MECHANISM (6 MB / 72; commit 2daf9b55) stands as the latest
substrate-grade evidence; v2.2 was MEANT to promote to chain-grade with dense
grid but the dispatch never ran. No supersession of v2.1.

A5 protocol: pre-read line counts; tmp -> os.replace atomic; verify-load.
"""
import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATH_7 = "data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7/metrics.json"
METRICS_PATH_13 = "data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_13/metrics.json"
METRICS_PATH_19 = "data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_19/metrics.json"
PREREG_PATH = "preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid.md"
CELL_CORE = "experiments/_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_core.py"
CELL_PATH_7 = "experiments/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7.py"
CELL_PATH_13 = "experiments/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_13.py"
CELL_PATH_19 = "experiments/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_19.py"

V2P1_AGG_ATOM = "math::T3/EXP_pattern_completion_corruption_cliff_v2p1_narrow_regime_CROSS_SEED_AGG_3_of_3_MM_2026-06-28"

ATOMIZED_BY = "skunkworks_atomize_pattern_completion_v2p2_dense_cliff_grid_3seed_DISPATCH_FAILURE_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "ac706494"

SEED7_ATOM_ID = "T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7_DISPATCH_INFRA_FAILURE_HDLAB_QUEUE_env_var_unset_gpu_mandate_refusal_no_substrate_sweep_executed_elapsed_0p01s_2026-06-28"
SEED13_ATOM_ID = "T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_13_DISPATCH_INFRA_FAILURE_HDLAB_QUEUE_env_var_unset_gpu_mandate_refusal_no_substrate_sweep_executed_elapsed_0p01s_2026-06-28"
SEED19_ATOM_ID = "T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_19_DISPATCH_INFRA_FAILURE_HDLAB_QUEUE_env_var_unset_gpu_mandate_refusal_no_substrate_sweep_executed_elapsed_0p01s_2026-06-28"
AGG_ATOM_ID = "T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_CROSS_SEED_AGG_3_of_3_DISPATCH_INFRA_FAILURE_NOT_substrate_hypothesis_test_outcome_v2p1_MM_stands_v2p3_recommended_with_HDLAB_QUEUE_set_2026-06-28"

PER_SEED = {
    7:  {"verdict_msg": "HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden by Fix #24 unless HDLAB_QUEUE=local_cpu_queue (USER explicit route). Got HDLAB_QUEUE=''. Refusing.",
         "elapsed_s": 0.01, "phase": "gpu_mandate_check", "backend": "torch.cpu", "routed_queue": ""},
    13: {"verdict_msg": "HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden by Fix #24 unless HDLAB_QUEUE=local_cpu_queue (USER explicit route). Got HDLAB_QUEUE=''. Refusing.",
         "elapsed_s": 0.01, "phase": "gpu_mandate_check", "backend": "torch.cpu", "routed_queue": ""},
    19: {"verdict_msg": "HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden by Fix #24 unless HDLAB_QUEUE=local_cpu_queue (USER explicit route). Got HDLAB_QUEUE=''. Refusing.",
         "elapsed_s": 0.01, "phase": "gpu_mandate_check", "backend": "torch.cpu", "routed_queue": ""},
}


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
            f"Pattern completion v2.2 dense cliff grid seed_{seed} -- "
            f"DISPATCH INFRA FAILURE (HDLAB_QUEUE unset; cell refused at gpu_mandate_check; "
            f"elapsed=0.01s; NO substrate sweep executed)"
        ),
        "corpus": "math",
        "tier": "T3",
        "kind": "dispatch_infrastructure_failure",
        "description": (
            f"Pattern completion corruption-cliff v2.2 dense-cliff-grid seed_{seed} of 3. "
            f"Cell verdict = HARD_FAIL but ROOT CAUSE is DISPATCH INFRASTRUCTURE failure, "
            f"NOT a substrate hypothesis test outcome. "
            f"DIAGNOSIS (off-disk read of metrics.json): "
            f"verdict_msg='{p['verdict_msg']}'; elapsed_s={p['elapsed_s']} "
            f"(cell exited at phase={p['phase']} BEFORE executing any substrate sweep); "
            f"backend={p['backend']}; routed_queue='{p['routed_queue']}' (empty -- runner did not set "
            f"HDLAB_QUEUE=local_cpu_queue). "
            f"The cell's gpu_mandate_check gate at line 192-203 of {cell_path} explicitly refuses "
            f"FULL runs on CPU backend unless HDLAB_QUEUE=local_cpu_queue is set, per Fix #24 GPU mandate. "
            f"The pre-reg ({PREREG_PATH}) explicitly noted this dispensation at lines 129-137 ('CPU fallback "
            f"ALLOWED for this cell when HDLAB_QUEUE=local_cpu_queue is set'). "
            f"The dispatch runner did not export this env var, so the gate refused -- exactly the cell-author's "
            f"intended behavior in absence of the explicit local_cpu_queue route. "
            f"OUTCOME: substrate sweep NEVER ran; no data on whether dense grid populates the cliff with >=22 MB / 180; "
            f"v2.1 MEASURED_MECHANISM (math::T3/EXP_pattern_completion_corruption_cliff_v2p1_narrow_regime_CROSS_SEED_AGG_3_of_3_MM_2026-06-28; "
            f"6 MB / 72) REMAINS the latest substrate-grade evidence on this anchor. "
            f"This is NOT a substrate negative result. The hypothesis (dense grid populates cliff with sufficient "
            f"MB to clear chain-grade promotion threshold) is UNTESTED. "
            f"REMEDIATION: re-dispatch v2.3 with runner setting HDLAB_QUEUE=local_cpu_queue, OR amend the cell "
            f"to default-ON local_cpu_queue dispensation when backend == torch.cpu AND smoke gates pass."
        ),
        "aliases": [
            f"pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_{seed}_DISPATCH_INFRA_FAILURE_2026-06-28",
            f"pattern_completion_v2p2_seed_{seed}_gpu_mandate_refusal_HDLAB_QUEUE_unset_2026-06-28",
            f"v2p2_dense_cliff_grid_seed_{seed}_test_design_infra_failure_no_substrate_sweep_executed",
        ],
        "metadata": {
            "provenance_quality": "MEASURED",
            "cert_status": "test_design_infra_failure",
            "cert_class": "dispatch_infrastructure_failure",
            "verdict": "DISPATCH_INFRA_FAILURE_NO_SUBSTRATE_SWEEP_EXECUTED",
            "verdict_subtype": "GPU_MANDATE_REFUSAL_RUNNER_HDLAB_QUEUE_ENV_VAR_UNSET",
            "cell_commit": CELL_COMMIT,
            "cell_path": cell_path,
            "cell_core_path": CELL_CORE,
            "prereg_path": PREREG_PATH,
            "metrics_path": metrics_path,
            "atomized_by": ATOMIZED_BY,
            "atomized_date": ATOMIZED_DATE,
            "verified_off_data": True,
            "verified_off_data_evidence": (
                f"OFF-DATA read of metrics.json: verdict=HARD_FAIL; verdict_msg matches GPU_MANDATE_BREACH "
                f"sentinel from cell line 192-203; elapsed_s=0.01 (cell exited before any phase point ran); "
                f"_phase=gpu_mandate_check; backend=torch.cpu; routed_queue=''. No phase-map records. "
                f"No cardinality_ok / observed_n_units / expected_n_units fields (cell exited pre-sweep)."
            ),
            "seed": seed,
            "raw_verdict_msg": p["verdict_msg"],
            "raw_phase_at_exit": p["phase"],
            "raw_backend": p["backend"],
            "raw_routed_queue": p["routed_queue"],
            "raw_elapsed_s": p["elapsed_s"],
            "substrate_sweep_executed": False,
            "n_phase_points_recorded": 0,
            "is_substrate_hypothesis_test_outcome": False,
            "is_dispatch_infra_failure": True,
            "cert_increment_delta": 0,
            "discipline_tags": [
                "Fix_24_GPU_mandate_dispatch_must_actually_use_GPU_OR_set_HDLAB_QUEUE",
                "test_design_failure_diagnosis_and_hardening_USER_2026-06-28",
                "Fix_28_per_arm_metrics_not_verdict_msg_VERIFY_VERDICT_MSG_for_INFRA_vs_HYPOTHESIS_distinction",
                "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
                "verify_OFF_DATA_not_reports_USER_LOCKED_skunkworks_discipline",
            ],
            "supersedes": None,
            "ts_iso_atomized": ATOMIZED_DATE,
        },
    }


atom_seed7 = _per_seed_atom(7)
atom_seed13 = _per_seed_atom(13)
atom_seed19 = _per_seed_atom(19)


# Cross-seed AGG -- documents the dispatch-infra failure pattern + recommendation
atom_agg = {
    "id": AGG_ATOM_ID,
    "name": (
        "Pattern completion v2.2 dense cliff grid CROSS-SEED 3-of-3 DISPATCH INFRA FAILURE "
        "(HDLAB_QUEUE env var unset across all 3 dispatches; cell refused at gpu_mandate_check; "
        "NO substrate sweep executed; v2.1 MM stands; v2.3 recommended with HDLAB_QUEUE=local_cpu_queue "
        "set OR cell-level default-ON dispensation)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "test_design_failure_dispatch_infra",
    "description": (
        "Pattern completion corruption-cliff v2.2 dense-cliff-grid CROSS-SEED 3-of-3 outcome: "
        "all 3 seeds (7, 13, 19) refused FULL run at the gpu_mandate_check gate (cell line 192-203) "
        "because the runner did not set HDLAB_QUEUE=local_cpu_queue. Each seed's metrics.json shows "
        "elapsed_s=0.01, _phase=gpu_mandate_check, backend=torch.cpu, routed_queue=''. "
        "ROOT CAUSE: dispatch infrastructure runner did not export HDLAB_QUEUE=local_cpu_queue env var "
        "before invoking the FULL run, despite the pre-reg's explicit dispensation note (lines 129-137 of "
        "the prereg). The cell-author honored the user's Fix #24 GPU mandate by refusing CPU FULL runs by "
        "default; the runner's env-var-set was the missing piece. "
        "DIAGNOSIS PER USER 2026-06-28 test-design-failure-and-hardening rule: this is NOT a substrate "
        "hypothesis test outcome -- substrate sweep never executed; substrate state remains UNKNOWN with "
        "respect to v2.2's hypothesis (dense grid in [0.46, 0.50] @ 0.005 step populates >=22 MB / 180). "
        "The PROMOTION PATH to chain-grade for pattern_completion_corruption_cliff is BLOCKED pending v2.3 "
        "re-dispatch with correct env var, OR a cell-level amendment to default-ON local_cpu_queue when "
        "backend == torch.cpu AND smoke gates pass. "
        "v2.1 CROSS_SEED_AGG MEASURED_MECHANISM (math::T3/"
        "EXP_pattern_completion_corruption_cliff_v2p1_narrow_regime_CROSS_SEED_AGG_3_of_3_MM_2026-06-28; "
        "6 MB / 72) STANDS as the latest substrate-grade evidence on this anchor and is NOT SUPERSEDED by "
        "this dispatch-infra-failure atom. "
        "NEW DIAGNOSIS CATEGORY for test-design-failure rule: dispatch_infrastructure_failure (runner config gap). "
        "Pattern: cell ships with environment-gated dispensation; runner does not set required env var; cell "
        "refuses with clear sentinel verdict_msg (cell-author intent honored). Distinguishable from: "
        "(a) by-construction saturation (substrate sweep RAN and saturated), (b) discriminator threshold "
        "mismatch (substrate sweep RAN and produced data that mismatched pre-reg thresholds), (c) code bug "
        "(substrate sweep RAN and produced incorrect numbers), (d) effective != nominal parameter "
        "(substrate sweep RAN with wrong parameters). In this case, elapsed_s=0.01 and _phase=gpu_mandate_check "
        "are the load-bearing distinguishers -- the cell NEVER reached substrate sweep code. "
        "RECOMMENDATION: v2.3 sibling cells with one of: "
        "(1) runner-side amendment: dispatch script exports HDLAB_QUEUE=local_cpu_queue before invoking python; "
        "(2) cell-side amendment: default-ON local_cpu_queue dispensation when backend == torch.cpu AND "
        "len(sys.argv) suggests non-smoke explicit-route invocation; "
        "(3) runner-side amendment: route to remote GPU queue (per Fix #24 GPU mandate) instead of local CPU. "
        "Skunkworks RECOMMENDS option (1) for v2.3 as the smallest intervention -- the cell-author's gate is "
        "intentional safety; the runner's env-var-set is the correct extension point. "
        "EXP_DEV HARDENING (proposed): exp_dev/CLAUDE.md hardening rule -- 'cells with environment-gated "
        "dispensation MUST include a HEADER COMMENT block specifying the exact env-var contract; runners "
        "MUST source that header before dispatch (e.g. greppable PRESERVE_ENV_VARS: HDLAB_QUEUE marker).' "
        "Skunkworks SCHEMA-VET gate proposed (META_RULE: env-var-contract-must-survive-runner-dispatch): on "
        "any cell pre-reg dispatch, verify the runner exports any env-var contracts specified in the cell "
        "(gpu mandate dispensation, custom routing, etc.); if env-var-contract mismatch detected, SCHEMA-VET "
        "auto-fails the dispatch."
    ),
    "aliases": [
        "pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_CROSS_SEED_AGG_3_of_3_DISPATCH_INFRA_FAILURE_2026-06-28",
        "pattern_completion_v2p2_dispatch_infra_failure_HDLAB_QUEUE_unset_2026-06-28",
        "test_design_failure_dispatch_infrastructure_new_diagnosis_category_2026-06-28",
        "v2p2_dense_cliff_grid_no_substrate_sweep_executed_v2p1_MM_stands",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "test_design_infra_failure",
        "cert_class": "test_design_failure_dispatch_infra",
        "verdict": "CROSS_SEED_3_OF_3_DISPATCH_INFRA_FAILURE_NO_SUBSTRATE_SWEEP_EXECUTED_RECOMMEND_V2P3_WITH_RUNNER_HDLAB_QUEUE_SET",
        "verdict_subtype": "RUNNER_DID_NOT_EXPORT_HDLAB_QUEUE_local_cpu_queue_PER_PREREG_DISPENSATION_CELL_AUTHOR_GATE_HONORED_AS_DESIGNED",
        "cell_commit": CELL_COMMIT,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA read of all 3 sibling metrics.json: each verdict=HARD_FAIL with identical verdict_msg "
            "matching GPU_MANDATE_BREACH sentinel from cell line 192-203; elapsed_s=0.01 each (cell never "
            "executed sweep); _phase=gpu_mandate_check each; backend=torch.cpu each; routed_queue='' each. "
            "No phase-map / cardinality fields populated (cell exited pre-sweep). "
            "Cell ac706494 line 191-203 code path confirms: routed_queue = os.environ.get('HDLAB_QUEUE', '').lower(); "
            "if not SMOKE_MODE and backend == 'torch.cpu' and routed_queue != 'local_cpu_queue': REFUSE. "
            "Prereg lines 129-137 confirm cell-author intent: dispensation requires HDLAB_QUEUE=local_cpu_queue "
            "to be set BY THE RUNNER. Runner did not set."
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
        "substrate_sweep_executed": False,
        "n_phase_points_recorded_across_all_3_seeds": 0,
        "is_substrate_hypothesis_test_outcome": False,
        "is_dispatch_infra_failure": True,
        "supersedes_v2p1_MM_atom": False,
        "v2p1_MM_atom_still_authoritative": V2P1_AGG_ATOM,
        "diagnosis_category": "dispatch_infrastructure_runner_env_var_unset",
        "diagnosis_category_is_new": True,
        "diagnosis_category_added_to_test_design_failure_catalog": True,
        "remediation_recommendation": {
            "preferred": (
                "v2.3 sibling cells with RUNNER-SIDE amendment: dispatch script exports "
                "HDLAB_QUEUE=local_cpu_queue before invoking python (smallest intervention; preserves "
                "cell-author's intentional safety gate)"
            ),
            "alternatives": [
                "v2.3 with CELL-SIDE amendment: default-ON local_cpu_queue dispensation when backend == "
                "torch.cpu (weakens safety gate slightly)",
                "v2.3 routed to remote GPU queue per Fix #24 GPU mandate (matches USER intent more closely but "
                "requires remote GPU access)",
            ],
        },
        "exp_dev_hardening_proposed": {
            "rule": "META_RULE: env-var-contract-must-survive-runner-dispatch",
            "schema_vet_gate": (
                "On any cell pre-reg SCHEMA-VET: if cell source contains env-var dispensation gates "
                "(e.g. HDLAB_QUEUE check), verify the dispatch runner exports those env vars before invocation. "
                "If env-var-contract mismatch detected, SCHEMA-VET auto-fails the dispatch and routes to "
                "exp_dev for runner amendment."
            ),
            "header_contract_format": (
                "Cells with env-var-gated dispensation MUST include a HEADER COMMENT block: "
                "PRESERVE_ENV_VARS: HDLAB_QUEUE=<expected_value>, HDLAB_RUN_MODE=<expected>, etc. "
                "Greppable marker for both pre-dispatch verify AND post-hoc audit."
            ),
        },
        "pattern_completion_anchor_substrate_status": (
            "v2.1 MEASURED_MECHANISM stands as authoritative (6 MB / 72; cliff razor-sharp at corruption=0.48-0.50). "
            "v2.2 dense-grid hypothesis UNTESTED -- promotion path BLOCKED pending v2.3 re-dispatch. "
            "Pattern_completion_corruption_cliff capability remains at MEASURED_MECHANISM tier (not chain-grade) "
            "as of 2026-06-28. The cliff is real; the substrate has the primitive; just need to populate the "
            "dense MB band to clear >=22 MB / 180 promotion threshold."
        ),
        "follow_up_drills": [
            "v2.3 sibling cells with runner-side HDLAB_QUEUE=local_cpu_queue export (PREFERRED -- smallest intervention)",
            "exp_dev CLAUDE.md amendment: env-var-contract header rule",
            "skunkworks SCHEMA-VET gate amendment: env-var-contract-must-survive-runner-dispatch check",
            "consider routing v2.3 to remote GPU queue instead (Fix #24 alignment; requires GPU access)",
        ],
        "cert_increment_delta": 0,
        "discipline_tags": [
            "Fix_24_GPU_mandate_HDLAB_QUEUE_env_var_contract",
            "test_design_failure_diagnosis_and_hardening_USER_2026-06-28",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "verify_OFF_DATA_not_reports_USER_LOCKED_skunkworks_discipline",
            "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
            "META_RULE_env_var_contract_must_survive_runner_dispatch_NEW_2026-06-28",
            "stage_3_compositional_understanding_USER_2026-06-26",
            "M3_milestone_glass_box_conversational",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


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
    0, atom_seed7, "cert_ruling_dispatch_infra_failure", "test_design_infra_failure",
    "dispatch_infrastructure_failure",
    "DISPATCH_INFRA_FAILURE_seed_7_HDLAB_QUEUE_unset_cell_refused_at_gpu_mandate_check_phase_no_substrate_sweep_executed_NOT_a_substrate_hypothesis_test_outcome",
    0,
    "v2p2_seed_7_dispatch_infra_failure_runner_env_var_unset_substrate_state_UNKNOWN_re_dispatch_v2p3_recommended",
    metrics_path=METRICS_PATH_7,
)
ledger_seed13 = _ledger_row(
    1, atom_seed13, "cert_ruling_dispatch_infra_failure", "test_design_infra_failure",
    "dispatch_infrastructure_failure",
    "DISPATCH_INFRA_FAILURE_seed_13_HDLAB_QUEUE_unset_cell_refused_at_gpu_mandate_check_phase_no_substrate_sweep_executed_NOT_a_substrate_hypothesis_test_outcome",
    0,
    "v2p2_seed_13_dispatch_infra_failure_runner_env_var_unset_substrate_state_UNKNOWN_re_dispatch_v2p3_recommended",
    metrics_path=METRICS_PATH_13,
)
ledger_seed19 = _ledger_row(
    2, atom_seed19, "cert_ruling_dispatch_infra_failure", "test_design_infra_failure",
    "dispatch_infrastructure_failure",
    "DISPATCH_INFRA_FAILURE_seed_19_HDLAB_QUEUE_unset_cell_refused_at_gpu_mandate_check_phase_no_substrate_sweep_executed_NOT_a_substrate_hypothesis_test_outcome",
    0,
    "v2p2_seed_19_dispatch_infra_failure_runner_env_var_unset_substrate_state_UNKNOWN_re_dispatch_v2p3_recommended",
    metrics_path=METRICS_PATH_19,
)
ledger_agg = _ledger_row(
    3, atom_agg, "cert_ruling_test_design_failure_aggregation", "test_design_infra_failure",
    "test_design_failure_dispatch_infra",
    "CROSS_SEED_3_OF_3_DISPATCH_INFRA_FAILURE_NEW_DIAGNOSIS_CATEGORY_dispatch_infrastructure_runner_env_var_unset_v2p1_MM_stands_v2p3_recommended_with_HDLAB_QUEUE_set_exp_dev_hardening_proposed_env_var_contract_rule",
    0,
    "v2p2_CROSS_SEED_AGG_3_of_3_dispatch_infra_failure_new_diagnosis_category_added_v2p1_MM_stands_v2p3_recommended_exp_dev_hardening_env_var_contract_rule_skunkworks_schema_vet_gate_proposed",
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
    print(f"[A5] PC v2.2 root-cause = DISPATCH INFRA FAILURE (runner HDLAB_QUEUE unset)")
    print(f"[A5] NOT substrate hypothesis HF; substrate sweep never executed")
    print(f"[A5] v2.1 MEASURED_MECHANISM atom stands; v2.3 re-dispatch recommended")
    print(f"[A5] CERT delta = 0 (no substrate evidence; dispatch infra failure)")

    append_jsonl_a5(MATH_ATOMS, atom_seed7, "math/atoms.jsonl (seed_7 INFRA-FAIL)")
    append_jsonl_a5(MATH_ATOMS, atom_seed13, "math/atoms.jsonl (seed_13 INFRA-FAIL)")
    append_jsonl_a5(MATH_ATOMS, atom_seed19, "math/atoms.jsonl (seed_19 INFRA-FAIL)")
    append_jsonl_a5(MATH_ATOMS, atom_agg, "math/atoms.jsonl (CROSS-SEED AGG INFRA-FAIL)")
    append_jsonl_a5(CERT_LEDGER, ledger_seed7, "meta/cert_ledger.jsonl (seed_7 INFRA-FAIL)")
    append_jsonl_a5(CERT_LEDGER, ledger_seed13, "meta/cert_ledger.jsonl (seed_13 INFRA-FAIL)")
    append_jsonl_a5(CERT_LEDGER, ledger_seed19, "meta/cert_ledger.jsonl (seed_19 INFRA-FAIL)")
    append_jsonl_a5(CERT_LEDGER, ledger_agg, "meta/cert_ledger.jsonl (AGG INFRA-FAIL)")

    print(f"[A5] DONE OK; CERT delta = 0")
    print(f"[A5] RECOMMENDATION: v2.3 sibling cells with runner HDLAB_QUEUE=local_cpu_queue env var set")
    print(f"[A5] exp_dev hardening proposed: env-var-contract-must-survive-runner-dispatch META_RULE")


if __name__ == "__main__":
    main()
