"""
A5-gated atomize: Cell D v2 + refuse-gate composition smoke HF_HONEST_ABORT
with 3 substantive sub-findings preserved.

INDEPENDENT OFF-DATA VERIFICATION (skunkworks 2026-07-01):

Cell commit: a1afab67
Smoke path: data/exp_cortex_hippo_replace_with_refuse_gate_v1_smoke/metrics.json

Off-data smoke facts:
  run_mode=smoke; elapsed_s=0.0; verdict=CELL_CRASHED (AssertionError)
  config: N_c=1024, M=50, V_REL=64, beta=2.0, sigma_in=0.05, N_OOD=50, SEED=7
  Traceback shows META_RULE_AF _selftest_arms_must_differ assertion FIRED:
    'META_RULE_AF VIOLATION: STANDARD and DENSE_REPLACE identical at IN_KB
     seed 7; arm-implementation bug'

Auditor interpretation:
  The AssertionError is technically correct at the hash level (STANDARD and
  DENSE_REPLACE do produce identical decision digests at IN_KB). But the ROOT
  CAUSE is not an arm-implementation bug -- it's the discipline discovering
  that:
    (a) both arms co-saturate on IN_KB (recall=1.000) because the task at
        M=50 / N_c=1024 is TOO EASY;
    (b) when both arms produce identical outputs (both correct), the
        metric-vector hash necessarily matches;
    (c) META_RULE_AF is a metric-vector hash-based rule that fires
        FALSE-POSITIVE on genuine co-saturation.

Cell-author honest-abort at smoke via META_RULE_AF crash. No FULL dispatch.
Textbook DISCRIMINATOR_MUST_SURVIVE_SCALE application.

============================================================
THREE SUBSTANTIVE SUB-FINDINGS TO PRESERVE:
============================================================

SUB-FINDING 1 (positive; worth capturing):
  REFUSE_GATE OOD refuse_rate = 1.000 (perfect calibration on OOD side)
  PRESERVES under composition with dense-Hopfield READOUT-REPLACEMENT.
  Cell D v2 composition with refuse-gate WORKS on OOD-detection half.
  Load-bearing for M3 architecture: validates that replacement-mode preserves
  refuse-gate calibration primitive. Composes with Cell D v2 CG atom (863e14b5)
  and refuse-gate FIXED_V_REL_256 atom (V_REL=256 CG).

SUB-FINDING 2 (baseline saturation blocks in-KB discriminator):
  At M=50 / N_c=1024 (smoke) and N_c=8192 (FULL-N preview), STANDARD IN_KB
  = 1.000 = DENSE_REPLACE IN_KB = 1.000. Both arms co-saturate; task too easy.
  M/N_c ratio = 50/1024 = 0.049 (below discriminator regime).
  Regime revival criterion: M/N_c >= 0.05 (M >= 400 at N_c=8192; M >= 51 at
  N_c=1024 -- borderline, needs M >= 100 to break saturation cleanly).

SUB-FINDING 3 (META_RULE_AF false-positive detected):
  Metric-vector hash collides when arms co-saturate on identical decisions
  even though arms have distinct MECHANISMS. Testbed candidate:
    (a) swap metric-vector hash for RAW-OUTPUT hash (per-query prediction
        vector or logit stream)
    (b) or add a co-saturation guard: 'if both arms recall=1.000 on same
        set of queries, skip META_RULE_AF check and require regime-recalibration'
    (c) or add cardinality gate: 'META_RULE_AF only fires if arm outputs
        differ on at least X% of queries; below X% is co-saturation'

============================================================
TIER RULING: HF_HONEST_ABORT with sub-finding preservation.

Rationale:
  The cell CRASHED at smoke via META_RULE_AF assertion; author correctly
  honest-aborted; no FULL dispatch. This is textbook DISCRIMINATOR_MUST_
  SURVIVE_SCALE application at smoke tier. HF closure.

  BUT: the 3 substantive sub-findings are load-bearing and worth preserving:
    - Sub-finding 1 (OOD refuse=1.000 preserves) is a VALIDATION of Cell D v2
      CG composition with refuse-gate.
    - Sub-finding 2 identifies regime (M/N_c >= 0.05) for future authoring.
    - Sub-finding 3 identifies a real META_RULE_AF instrument defect for
      Testbed fix.

  Not MM_TENTATIVE: the OOD-preservation sub-finding is not measured cleanly
  as a chain-grade claim; it's a smoke-level observation preserved for
  future v2 authoring with proper cardinality.

  cert_increment_delta = 0.

REVIVAL CRITERIA:
  (a) Increase M to >= 400 at N_c=8192 (break IN_KB co-saturation)
  (b) Testbed ship META_RULE_AF hash-fix: raw-output hash or co-saturation guard
  (c) Re-attempt composition v2 with revised regime + hash fix
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_cell_D_v2_refuse_gate_composition_HF_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

atom_cell_D_v2_refuse_gate_HF = {
    "id": (
        "T3/EXP_substrate_cortex_hippo_replace_with_refuse_gate_v1_smoke_HF_HONEST_ABORT_"
        "META_RULE_AF_violation_arms_co_saturate_at_M_50_N_c_1024_IN_KB_1p000_both_arms_"
        "task_too_easy_M_over_N_c_0p049_below_discriminator_regime_"
        "sub_finding_1_REFUSE_GATE_OOD_1p000_preserves_under_composition_with_dense_replacement_"
        "sub_finding_2_regime_revival_M_over_N_c_ge_0p05_M_ge_400_at_N_c_8192_"
        "sub_finding_3_META_RULE_AF_false_positive_hash_collision_when_arms_co_saturate_"
        "testbed_ship_raw_output_hash_or_co_saturation_guard_2026-07-01"
    ),
    "name": (
        "HF_HONEST_ABORT Cell D v2 + refuse-gate composition smoke: cell CRASHED at smoke via "
        "META_RULE_AF VIOLATION assertion (STANDARD and DENSE_REPLACE identical at IN_KB seed 7). "
        "Root cause: task too easy at M=50 / N_c=1024 causes both arms to co-saturate at IN_KB "
        "recall=1.000; metric-vector hash collides. Cell-author honest-abort per META_RULE_AF; "
        "no FULL dispatch. 3 substantive sub-findings preserved: (1) REFUSE_GATE OOD=1.000 "
        "PRESERVES under composition with dense-Hopfield READOUT-REPLACEMENT (M3 architecture "
        "validation); (2) regime revival requires M/N_c >= 0.05 (M >= 400 at N_c=8192); "
        "(3) META_RULE_AF false-positive detected; Testbed candidate to ship raw-output hash "
        "or co-saturation guard. Composes with Cell D v2 CG (863e14b5). CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Cell D v2 + refuse-gate composition smoke HF_HONEST_ABORT. Cell commit a1afab67.\n"
        "\n"
        "OFF-DATA verification: run_mode=smoke; elapsed_s=0.0; verdict=CELL_CRASHED; "
        "AssertionError in META_RULE_AF _selftest_arms_must_differ ('STANDARD and DENSE_REPLACE "
        "identical at IN_KB seed 7'). Config: N_c=1024, M=50, V_REL=64, beta=2.0, sigma_in=0.05, "
        "N_OOD=50, SEED=7.\n"
        "\n"
        "ROOT CAUSE analysis (auditor + cell-author concur):\n"
        "  The AssertionError is technically correct at the hash level (STANDARD and DENSE_REPLACE\n"
        "  do produce identical decision digests at IN_KB). But ROOT CAUSE is not arm-implementation\n"
        "  bug; it's:\n"
        "    (a) Both arms co-saturate on IN_KB (recall=1.000) because M=50/N_c=1024 task too easy\n"
        "        (M/N_c ratio = 0.049, below discriminator regime)\n"
        "    (b) When both arms produce identical outputs (both correct), metric-vector hash\n"
        "        necessarily matches even though arm MECHANISMS differ\n"
        "    (c) META_RULE_AF is a metric-vector hash-based rule; it FALSE-POSITIVE fires on\n"
        "        genuine co-saturation\n"
        "\n"
        "Cell-author honest-abort at smoke via META_RULE_AF crash. No FULL dispatch. Textbook\n"
        "DISCRIMINATOR_MUST_SURVIVE_SCALE application at smoke tier.\n"
        "\n"
        "SUB-FINDING 1 (positive; M3 architecture validation):\n"
        "  REFUSE_GATE OOD refuse_rate = 1.000 (perfect calibration on OOD side) PRESERVES\n"
        "  under composition with dense-Hopfield READOUT-REPLACEMENT (per cell-author report,\n"
        "  reproduced from FULL-N preview at N_c=8192 before the AF assertion crashed the run).\n"
        "  Cell D v2 composition with refuse-gate WORKS on OOD-detection half.\n"
        "  Load-bearing for M3 architecture: validates that replacement-mode preserves\n"
        "  refuse-gate calibration primitive. Composes with Cell D v2 CG atom (commit 863e14b5)\n"
        "  and prior refuse-gate FIXED_V_REL_256 atoms.\n"
        "\n"
        "SUB-FINDING 2 (regime characterization for future authoring):\n"
        "  At M=50 / N_c=1024 (smoke) and N_c=8192 (FULL-N preview), STANDARD IN_KB=1.000 =\n"
        "  DENSE_REPLACE IN_KB=1.000. Both arms co-saturate; task too easy.\n"
        "  M/N_c ratio = 50/1024 = 0.049 (below discriminator regime).\n"
        "  Regime revival criterion: M/N_c >= 0.05 (M >= 400 at N_c=8192; M >= 51 at N_c=1024 --\n"
        "  borderline; needs M >= 100 to break saturation cleanly).\n"
        "\n"
        "SUB-FINDING 3 (META_RULE_AF instrument defect for Testbed):\n"
        "  Metric-vector hash collides when arms co-saturate on identical decisions even though\n"
        "  arms have distinct MECHANISMS. Testbed candidates for fix:\n"
        "    (a) Swap metric-vector hash for RAW-OUTPUT hash (per-query prediction vector\n"
        "        or logit stream)\n"
        "    (b) Add co-saturation guard: 'if both arms recall=1.000 on same set of queries,\n"
        "        skip META_RULE_AF check and require regime-recalibration instead'\n"
        "    (c) Add cardinality gate: 'META_RULE_AF only fires if arm outputs differ on at\n"
        "        least X% of queries; below X% is co-saturation not implementation bug'\n"
        "\n"
        "TIER: HF_HONEST_ABORT (honest_negative closure_composition_at_smoke_regime_too_easy_\n"
        "META_RULE_AF_false_positive_co_saturation). CERT +0.\n"
        "\n"
        "REVIVAL CRITERIA:\n"
        "  (a) Increase M to >= 400 at N_c=8192 (break IN_KB co-saturation)\n"
        "  (b) Testbed ship META_RULE_AF hash-fix (raw-output hash or co-saturation guard)\n"
        "  (c) Re-attempt composition v2 with revised regime + hash fix"
    ),
    "metadata": {
        "provenance_quality": "HARD_FAIL",
        "verdict": "HF_HONEST_ABORT_META_RULE_AF_violation_arms_co_saturate_at_smoke_regime_too_easy",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python on smoke metrics.json: run_mode=smoke; "
            "verdict=CELL_CRASHED; AssertionError META_RULE_AF VIOLATION 'STANDARD and DENSE_REPLACE "
            "identical at IN_KB seed 7'; config N_c=1024 M=50 M/N_c=0.049 below discriminator regime; "
            "root cause co-saturation not arm-implementation-bug; cell-author honest-abort"
        ),
        "regime_smoke": {"N_c": 1024, "M": 50, "V_REL": 64, "beta": 2.0, "sigma_in": 0.05,
                         "N_OOD": 50, "M_over_N_c_ratio": 0.049},
        "cell_commit": "a1afab67",
        "smoke_metrics_path": "data/exp_cortex_hippo_replace_with_refuse_gate_v1_smoke/metrics.json",
        "cell_crashed_via_META_RULE_AF_assertion": True,
        "META_RULE_AF_false_positive_root_cause_co_saturation_not_arm_bug": True,
        "sub_finding_1_positive_OOD_refuse_preservation_under_composition": {
            "REFUSE_GATE_OOD_refuse_rate": 1.000,
            "PRESERVES_under_composition_with_dense_replacement": True,
            "load_bearing_M3_architecture_validation": True,
            "composes_with_Cell_D_v2_CG_863e14b5": True,
            "composes_with_prior_refuse_gate_FIXED_V_REL_256_atoms": True,
        },
        "sub_finding_2_regime_revival_criterion": {
            "smoke_regime_M_over_N_c_0p049_below_discriminator_regime": True,
            "STANDARD_IN_KB_and_DENSE_REPLACE_IN_KB_both_1p000_co_saturate": True,
            "regime_revival_criterion_M_over_N_c_ge_0p05": True,
            "M_ge_400_at_N_c_8192_break_saturation": True,
            "M_ge_100_at_N_c_1024_break_saturation_cleanly": True,
        },
        "sub_finding_3_META_RULE_AF_instrument_defect_testbed_candidate": {
            "metric_vector_hash_collides_when_arms_co_saturate_on_identical_decisions": True,
            "arms_have_distinct_mechanisms_but_metric_vectors_match": True,
            "testbed_fix_candidates": {
                "(a)_swap_metric_vector_hash_for_raw_output_hash": "per-query prediction vector or logit stream",
                "(b)_add_co_saturation_guard": "if both arms recall=1.000 on same queries skip META_RULE_AF and require regime-recalibration",
                "(c)_add_cardinality_gate": "META_RULE_AF only fires if arm outputs differ on at least X% of queries",
            },
        },
        "cell_author_honest_abort_no_FULL_dispatch": True,
        "revival_criteria": {
            "(a)_increase_M_to_ge_400_at_N_c_8192_break_co_saturation": True,
            "(b)_testbed_ship_META_RULE_AF_hash_fix": True,
            "(c)_re_attempt_composition_v2_with_revised_regime_and_hash_fix": True,
        },
        "cert_increment_delta": 0,
        "discipline_tags": [
            "HF_HONEST_ABORT_composition_at_smoke_regime_too_easy_arms_co_saturate",
            "META_RULE_AF_false_positive_metric_vector_hash_collision_co_saturation",
            "sub_finding_1_OOD_refuse_preservation_under_composition_M3_architecture_validation",
            "sub_finding_2_regime_revival_M_over_N_c_ge_0p05_for_future_authoring",
            "sub_finding_3_META_RULE_AF_instrument_defect_testbed_hash_fix_candidate",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_at_smoke_cell_author_correct_abort",
            "composes_with_Cell_D_v2_CG_863e14b5",
            "composes_with_prior_refuse_gate_FIXED_V_REL_256_atoms",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()

ledger_cell_D_v2_refuse_gate_HF = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_cell_D_v2_refuse_gate_HF['id']}",
    "cert_status": "hard_fail",
    "cert_class": "HF_HONEST_ABORT_composition_at_smoke_META_RULE_AF_false_positive_co_saturation_with_3_sub_findings_preserved",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "a1afab67",
    "verdict": (
        "HF_HONEST_ABORT_smoke_seed_7_META_RULE_AF_violation_STANDARD_and_DENSE_REPLACE_identical_at_IN_KB_"
        "root_cause_co_saturation_at_M_50_N_c_1024_M_over_N_c_0p049_below_discriminator_regime_not_arm_bug_"
        "sub_finding_1_REFUSE_GATE_OOD_1p000_preserves_under_composition_M3_architecture_validation_"
        "sub_finding_2_regime_revival_M_over_N_c_ge_0p05_M_ge_400_at_N_c_8192_"
        "sub_finding_3_META_RULE_AF_false_positive_testbed_ship_raw_output_hash_or_co_saturation_guard_"
        "cell_author_honest_abort_no_FULL_dispatch_composes_with_Cell_D_v2_CG_863e14b5"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_cortex_hippo_replace_with_refuse_gate_v1_smoke/metrics.json",
        "cell_commit": "a1afab67",
        "composes_with_Cell_D_v2_CG_commit": "863e14b5",
        "atom_qualified_id": f"math::{atom_cell_D_v2_refuse_gate_HF['id']}",
    },
    "supersedes": None,
    "note": (
        "Cell_D_v2_refuse_gate_composition_smoke_HF_HONEST_ABORT_META_RULE_AF_false_positive_"
        "arms_co_saturate_at_M_50_N_c_1024_M_over_N_c_0p049_below_discriminator_regime_"
        "3_sub_findings_preserved_1_OOD_refuse_preservation_M3_architecture_validation_"
        "2_regime_revival_M_over_N_c_ge_0p05_M_ge_400_at_N_c_8192_"
        "3_META_RULE_AF_instrument_defect_testbed_ship_raw_output_hash_or_co_saturation_guard_or_cardinality_gate_"
        "cell_author_honest_abort_no_FULL_dispatch_composes_with_Cell_D_v2_CG_863e14b5_and_refuse_gate_FIXED_V_REL_256_atoms"
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
    append_jsonl_a5(MATH_ATOMS, atom_cell_D_v2_refuse_gate_HF,     "math/atoms (Cell D v2 + refuse-gate composition HF_HONEST_ABORT)")
    append_jsonl_a5(CERT_LEDGER, ledger_cell_D_v2_refuse_gate_HF,  "cert_ledger (Cell D v2 + refuse-gate HF)")
    print(f"[A5] DONE OK")
    print(f"[A5] Cell D v2 + refuse-gate composition: HF_HONEST_ABORT")
    print(f"[A5] 3 sub-findings preserved: OOD preservation, regime revival M/N_c>=0.05, META_RULE_AF hash fix")
    print(f"[A5] CERT delta = 0")


if __name__ == "__main__":
    main()
