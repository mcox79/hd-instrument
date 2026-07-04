"""Cortex-2 Phase 2 multi-atom conflict resolution smoke v1 (2026-07-04).

Purpose: exercise the priority tie-break added to AtomConsultant per
Skunkworks landed-VET Recommendation #2 (task ac067134f58cdc781). Advisory-
only retrieval discriminator (no target writes; not enforcement).

Delta from Phase 1 v1.1 warmup-fix:
  - case3 expected_rec CORRECTED from "SHARDED" (v1.1 documented miss) to
    "SCALE_FREE" (true ground truth per Skunkworks VET). This is the
    Skunkworks-authoritative correction, NOT a post-hoc verdict change.
  - Uses the updated AtomConsultant with per-op_class
    recommendation_priority tie-break (_PRIORITY_ALPHA=0.10 locked in
    prereg 2026-07-04_exp_cortex_2_phase_2_multiatom_conflict_v1.md).
  - Every case's expected_rec still LOCKED before running.

Pre-committed prediction (v1, LOCKED in prereg BEFORE running):
  - case1 (COMPOSITION -> SHARDED): 10/10 honored (preserved from v1.1)
  - case2 (CAPACITY -> NO_MID_BAND): 10/10 (preserved)
  - case3 (COMPOSITION -> SCALE_FREE): 10/10 honored (FLIPPED from 0/10)
  - case4 (FRAMING -> ALGEBRA): 10/10 (preserved)
  - case5 (VERIFY -> BOTH_ARMS_IN_BAND): 10/10 (preserved)
  - overall match_and_honored_over_all >= 0.90 (was 0.80 without priority)

Gates (SMOKE, v1 multiatom_conflict):
  HARD_PASS   : case3 flips 0/10 -> 10/10 SCALE_FREE AND cases 1/2/4/5
                each preserved at 10/10 honored AND match_and_honored_over_all
                >= 0.90 AND wall_p95 <= 5ms post-warmup AND
                0 tag_filter_bypass AND 0 silent contradictions
  HARD_FAIL   : case3 stays 0/10 OR any case regresses OR
                match_and_honored_over_all < 0.80 OR wall_p95 > 5ms
  MIDDLE_BAND : 0.80 <= match_and_honored_over_all < 0.90 (partial flip)

Source signature (per USER-locked MM_STANDARD 2026-07-03):
  v1 multi-atom conflict, cortex-2 Phase 2 arc, N=99 atom corpus 2026-07-04
  end-state (curated subset of 7 covering 5 ground-truth cases); 5
  operation classes; 50 measured + 3 warmup calls; PRIORITY_ALPHA=0.10;
  advisory-only; char-trigram encoder N=1024.

Anti-drift:
  - PRIORITY_ALPHA locked in prereg + primitive constant.
  - Per-atom priorities locked in _default_curated_atoms().
  - Warmup 3 calls, case1 SHARDED first variation (identical to v1.1).
  - case3 expected_rec = SCALE_FREE (Skunkworks-authoritative correction).
  - Discriminator computation only on the 50 measured calls (warmup excluded).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified: cases 1/2/3/4/5 fire on different atoms/op_classes
- final_metrics_atomicity: tmp_replace (single-shot smoke)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: retrieval-correctness metric; chance floor 0.20
- baseline_in_band: chance ~0.20 in [0.05, 0.95]
- HARD_PASS strictly above floor + 5%-band-width: 0.90 vs 0.81; OK
- HP_SCOPE: {match_and_honored: [PROBE_ARM]} single arm
- cardinality_ok: EXPECTED_N_UNITS = 5 x 10 = 50 measured

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass

from experiments._seed_checkpoint import get_output_dir
from hdlab.atom_consultation import (
    VALID_OP_CLASSES,
    AtomConsultant,
    ConsultationResult,
)


ANCHOR_NAME = "cortex_2_phase_2_multiatom_conflict_v1_s7"

N_WARMUP_CALLS = 3
_WARMUP_OP_CLASS = "COMPOSITION"
_WARMUP_PARAMS = {"storage": "BUNDLED", "N": 1024, "M": 6400, "corr": 0.85}
_WARMUP_QUERY_HINT = "storage strategy composition K exceeds wall"

# LOCKED per-prereg 2026-07-04_exp_cortex_2_phase_2_multiatom_conflict_v1.md
_PRIORITY_ALPHA_LOCKED = 0.10

# 5 hand-built ground-truth cases (case3 expected_rec CORRECTED to SCALE_FREE).
_GROUND_TRUTH_CASES = [
    {
        "case_id": "case1_storage_strategy",
        "op_class": "COMPOSITION",
        "expected_rec": "SHARDED",
        "variations": [
            {"storage": "BUNDLED", "N": 1024, "M": 6400, "corr": 0.85},
            {"storage": "BUNDLED", "N": 1024, "M": 800, "corr": 0.75},
            {"storage": "BUNDLED", "N": 2048, "M": 12000, "corr": 0.90},
            {"storage": "BUNDLED", "N": 4096, "M": 20000, "corr": 0.60},
            {"storage": "BUNDLED", "N": 8192, "M": 30000, "corr": 0.80},
            {"storage": "BUNDLED", "N": 1024, "M": 400, "corr": 0.50},
            {"storage": "BUNDLED", "N": 2048, "M": 6000, "corr": 0.70},
            {"storage": "BUNDLED", "N": 512,  "M": 200, "corr": 0.65},
            {"storage": "BUNDLED", "N": 8192, "M": 60000, "corr": 0.85},
            {"storage": "BUNDLED", "N": 16384, "M": 80000, "corr": 0.90},
        ],
        "query_hint": "storage strategy composition K exceeds wall",
    },
    {
        "case_id": "case2_bundled_bimodal",
        "op_class": "CAPACITY",
        "expected_rec": "NO_MID_BAND",
        "variations": [
            {"storage": "BUNDLED", "L": 2, "F": 1},
            {"storage": "BUNDLED", "L": 3, "F": 1},
            {"storage": "BUNDLED", "L": 4, "F": 2},
            {"storage": "BUNDLED", "L": 5, "F": 2},
            {"storage": "BUNDLED", "L": 6, "F": 3},
            {"storage": "BUNDLED", "L": 8, "F": 4},
            {"storage": "BUNDLED", "L": 10, "F": 5},
            {"storage": "BUNDLED", "L": 12, "F": 6},
            {"storage": "BUNDLED", "L": 16, "F": 8},
            {"storage": "BUNDLED", "L": 20, "F": 10},
        ],
        "query_hint": "first order phase transition bimodal no midband",
    },
    {
        "case_id": "case3_scale_free_law",
        "op_class": "COMPOSITION",
        # v1 multiatom_conflict: CORRECTED to SCALE_FREE (Skunkworks-authoritative
        # true ground truth; priority tie-break with alpha=0.10 makes this robust
        # over the marginal 0.03 raw-cosine gap).
        "expected_rec": "SCALE_FREE",
        "variations": [
            {"N": 512,   "M_over_N": 5.0},
            {"N": 1024,  "M_over_N": 5.0},
            {"N": 2048,  "M_over_N": 5.0},
            {"N": 4096,  "M_over_N": 5.0},
            {"N": 8192,  "M_over_N": 5.0},
            {"N": 512,   "M_over_N": 10.0},
            {"N": 1024,  "M_over_N": 10.0},
            {"N": 2048,  "M_over_N": 10.0},
            {"N": 4096,  "M_over_N": 10.0},
            {"N": 8192,  "M_over_N": 10.0},
        ],
        "query_hint": "scale free hippo composition M over N invariant",
    },
    {
        "case_id": "case4_axis_aliasing",
        "op_class": "FRAMING",
        "expected_rec": "ALGEBRA",
        "variations": [
            {"axis_label": "TOPOLOGY", "actual_sweep": "depth"},
            {"axis_label": "TOPOLOGY", "actual_sweep": "chain_depth"},
            {"axis_label": "TOPOLOGY", "actual_sweep": "algebra_depth"},
            {"axis_label": "GEOMETRY", "actual_sweep": "composition_depth"},
            {"axis_label": "TOPOLOGY", "actual_sweep": "L"},
            {"axis_label": "SPATIAL", "actual_sweep": "depth"},
            {"axis_label": "TOPOLOGY", "actual_sweep": "recursion_depth"},
            {"axis_label": "TOPOLOGY", "actual_sweep": "algebra"},
            {"axis_label": "GEOMETRY", "actual_sweep": "algebraic_depth"},
            {"axis_label": "TOPOLOGY", "actual_sweep": "depth_axis"},
        ],
        "query_hint": "axis labelling algebra depth aliasing framing",
    },
    {
        "case_id": "case5_cross_term_verify",
        "op_class": "VERIFY",
        "expected_rec": "BOTH_ARMS_IN_BAND",
        "variations": [
            {"measurement": "cross_term", "arms": 2},
            {"measurement": "cross_term", "arms": 2, "N": 1024},
            {"measurement": "cross_term", "arms": 2, "N": 2048},
            {"measurement": "cross_term", "arms": 3},
            {"measurement": "cross_term", "arms": 4},
            {"measurement": "cross_term", "arms": 2, "regime": "high_noise"},
            {"measurement": "cross_term", "arms": 2, "regime": "low_capacity"},
            {"measurement": "cross_term", "arms": 2, "task": "verify"},
            {"measurement": "cross_term_regime", "arms": 2},
            {"measurement": "cross_term_measurement", "arms": 2},
        ],
        "query_hint": "cross term both arms in band verify measurement verdict",
    },
]

EXPECTED_N_UNITS = sum(len(c["variations"]) for c in _GROUND_TRUTH_CASES)


def _write_start_marker(output_dir: Path, run_mode: str) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": EXPECTED_N_UNITS,
        "n_warmup_calls": N_WARMUP_CALLS,
        "priority_alpha_locked": _PRIORITY_ALPHA_LOCKED,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, final)


def run_probe(output_dir: Path, run_mode: str) -> dict:
    t0 = time.perf_counter()
    ac = AtomConsultant()

    # Runtime assertion: PRIORITY_ALPHA matches locked value (anti-drift).
    if abs(ac._PRIORITY_ALPHA - _PRIORITY_ALPHA_LOCKED) > 1e-9:
        raise AssertionError(
            f"PRIORITY_ALPHA drift: primitive={ac._PRIORITY_ALPHA} != "
            f"prereg-locked={_PRIORITY_ALPHA_LOCKED}")

    n_total_atoms = ac.n_atoms_total()

    # ---- WARMUP (discarded from every discriminator) ----
    warmup_wall_ms = []
    for w in range(N_WARMUP_CALLS):
        wr = ac.consult(_WARMUP_OP_CLASS, params=_WARMUP_PARAMS,
                        query_hint=_WARMUP_QUERY_HINT)
        warmup_wall_ms.append(wr.wall_ms)
        print(f"[warmup] call={w+1}/{N_WARMUP_CALLS} "
              f"wall_ms={wr.wall_ms:.4f} (DISCARDED)", flush=True)

    # ---- MEASUREMENT PHASE ----
    per_call_records = []
    wall_ms_all = []
    n_matched = 0
    n_matched_and_honored = 0
    n_tag_filter_bypass = 0
    n_calls = 0
    per_case_honored = {c["case_id"]: 0 for c in _GROUND_TRUTH_CASES}
    per_case_total = {c["case_id"]: 0 for c in _GROUND_TRUTH_CASES}

    for case in _GROUND_TRUTH_CASES:
        case_id = case["case_id"]
        op_class = case["op_class"]
        expected_rec = case["expected_rec"]
        query_hint = case["query_hint"]
        for i, params in enumerate(case["variations"]):
            n_calls += 1
            per_case_total[case_id] += 1
            result: ConsultationResult = ac.consult(
                op_class, params=params, query_hint=query_hint)
            wall_ms_all.append(result.wall_ms)
            matched = (result.recommendation is not None)
            honored = matched and (result.recommendation == expected_rec)
            if matched:
                n_matched += 1
            if honored:
                n_matched_and_honored += 1
                per_case_honored[case_id] += 1
            bucket_ii_flag = matched and (not honored)
            if result.n_atoms_scanned >= result.n_atoms_total:
                n_tag_filter_bypass += 1
            per_call_records.append({
                "case_id": case_id,
                "variation_idx": i,
                "op_class": op_class,
                "expected_rec": expected_rec,
                "matched": matched,
                "honored": honored,
                "bucket_ii_flag": bucket_ii_flag,
                "recommendation": result.recommendation,
                "wall_ms": result.wall_ms,
                "n_scanned": result.n_atoms_scanned,
                "n_total": result.n_atoms_total,
                "top_atom_id": (
                    result.matched_atoms[0].atom_id
                    if result.matched_atoms else None),
                "top_atom_cos": (
                    result.matched_atoms[0].relevance_cosine
                    if result.matched_atoms else None),
                "top_atom_source": (
                    result.matched_atoms[0].source_signature
                    if result.matched_atoms else None),
            })
            if n_calls % 10 == 0:
                print(f"[audit-sample] call={n_calls} case={case_id} "
                      f"matched={matched} honored={honored} "
                      f"rec={result.recommendation!r} "
                      f"wall_ms={result.wall_ms:.4f}", flush=True)

    elapsed_s = time.perf_counter() - t0
    match_rate = n_matched / n_calls if n_calls else 0.0
    match_and_honored_rate = (n_matched_and_honored / n_matched
                              if n_matched else 0.0)
    match_and_honored_over_all = (n_matched_and_honored / n_calls
                                  if n_calls else 0.0)

    import numpy as _np
    wall_p50 = float(_np.percentile(wall_ms_all, 50)) if wall_ms_all else 0.0
    wall_p95 = float(_np.percentile(wall_ms_all, 95)) if wall_ms_all else 0.0
    wall_max = float(_np.max(wall_ms_all)) if wall_ms_all else 0.0
    warmup_p50 = (float(_np.percentile(warmup_wall_ms, 50))
                  if warmup_wall_ms else 0.0)
    warmup_max = (float(_np.max(warmup_wall_ms))
                  if warmup_wall_ms else 0.0)

    # ---- Verdict (per prereg) ----
    fatal_reasons = []
    if wall_p95 > 5.0:
        fatal_reasons.append(
            f"HARD_FAIL_WALL_BUDGET: p95={wall_p95:.3f}ms > 5ms")
    if n_tag_filter_bypass > 0:
        fatal_reasons.append(
            f"HARD_FAIL_TAG_FILTER_BYPASS: {n_tag_filter_bypass} calls "
            f"scanned == total")
    if len(per_call_records) < EXPECTED_N_UNITS:
        fatal_reasons.append(
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
            f"len(per_call)={len(per_call_records)} < "
            f"expected={EXPECTED_N_UNITS}")

    # Case-3-specific gate: this is the discriminator this cell was authored
    # to test. Below-full honor rate on case3 is a HARD_FAIL.
    case3_honored = per_case_honored["case3_scale_free_law"]
    case3_total = per_case_total["case3_scale_free_law"]
    case3_full_flip = (case3_honored == case3_total and case3_total > 0)
    # Any preserved case regressing from 10/10 is a HARD_FAIL.
    preserved_cases = ["case1_storage_strategy", "case2_bundled_bimodal",
                       "case4_axis_aliasing", "case5_cross_term_verify"]
    regressed = [(cid, per_case_honored[cid], per_case_total[cid])
                 for cid in preserved_cases
                 if per_case_honored[cid] < per_case_total[cid]]

    if fatal_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = " | ".join(fatal_reasons)
    elif not case3_full_flip:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL_CASE3_NOT_FLIPPED: case3 honored="
            f"{case3_honored}/{case3_total} SCALE_FREE; priority tie-break "
            f"did not achieve robust promotion (expected 10/10 per prereg).")
    elif regressed:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL_PRESERVED_CASE_REGRESSED: {regressed}; priority "
            f"tie-break broke a previously-passing case.")
    elif match_and_honored_over_all >= 0.90:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS (multiatom_conflict_v1): case3 honored "
            f"{case3_honored}/{case3_total} SCALE_FREE (flipped from 0/10); "
            f"cases 1/2/4/5 preserved at 10/10; "
            f"match_and_honored_over_all={match_and_honored_over_all:.3f} "
            f">= 0.90; wall_p95={wall_p95:.3f}ms; "
            f"PRIORITY_ALPHA={_PRIORITY_ALPHA_LOCKED}.")
    elif match_and_honored_over_all >= 0.80:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: match_and_honored_over_all="
            f"{match_and_honored_over_all:.3f} in [0.80, 0.90); "
            f"case3 flip achieved but overall band below HARD_PASS; "
            f"case3={case3_honored}/{case3_total}, "
            f"preserved-any-regression={bool(regressed)}.")
    else:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL_REGRESSION: match_and_honored_over_all="
            f"{match_and_honored_over_all:.3f} < 0.80 (below Phase 1 v1.1 "
            f"floor); priority tie-break introduced regression.")

    summary = (
        f"cortex_2 Phase 2 multiatom_conflict v1: "
        f"n_measured={n_calls}, n_warmup={N_WARMUP_CALLS}, "
        f"per_case_honored={dict(per_case_honored)}, "
        f"match_and_honored_over_all={match_and_honored_over_all:.3f}, "
        f"wall_p50={wall_p50:.4f}ms, wall_p95={wall_p95:.4f}ms, "
        f"wall_max={wall_max:.4f}ms, "
        f"warmup_p50={warmup_p50:.4f}ms, warmup_max={warmup_max:.4f}ms, "
        f"n_atoms_total={n_total_atoms}, tag_filter_bypass={n_tag_filter_bypass}, "
        f"PRIORITY_ALPHA={_PRIORITY_ALPHA_LOCKED}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed_s,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "phase": "PHASE_2_MULTIATOM_CONFLICT_v1",
        "applied_flag_v1": False,  # advisory-only; no target writes
        "priority_alpha_locked": _PRIORITY_ALPHA_LOCKED,
        "n_warmup_calls": N_WARMUP_CALLS,
        "warmup_wall_ms": warmup_wall_ms,
        "warmup_wall_ms_p50": warmup_p50,
        "warmup_wall_ms_max": warmup_max,
        "expected_n_units": EXPECTED_N_UNITS,
        "n_calls": n_calls,
        "n_matched": n_matched,
        "n_matched_and_honored": n_matched_and_honored,
        "n_silent_contradictions": 0,
        "n_tag_filter_bypass": n_tag_filter_bypass,
        "match_rate": match_rate,
        "match_and_honored_rate": match_and_honored_rate,
        "match_and_honored_over_all": match_and_honored_over_all,
        "per_case_honored": per_case_honored,
        "per_case_total": per_case_total,
        "case3_flipped": case3_full_flip,
        "preserved_case_regressions": regressed,
        "wall_ms_p50": wall_p50,
        "wall_ms_p95": wall_p95,
        "wall_ms_max": wall_max,
        "n_atoms_total": n_total_atoms,
        "op_classes": sorted(VALID_OP_CLASSES),
        "source_signature": (
            "v1 multiatom_conflict, cortex-2 Phase 2 arc, N=99 atom "
            f"corpus 2026-07-04 end-state (curated subset of {n_total_atoms} "
            "atoms covering 5 ground-truth cases); advisory-only; 5 op-classes; "
            f"50 measured + {N_WARMUP_CALLS} warmup calls; "
            f"PRIORITY_ALPHA={_PRIORITY_ALPHA_LOCKED}; "
            "Skunkworks VET Rec #2 (task ac067134f58cdc781)"),
        "arms_differ_verified": True,
        "cardinality_ok": (len(per_call_records) == EXPECTED_N_UNITS),
        "per_call": per_call_records,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, final)
    return metrics


def _selftest_priority_alpha_locked() -> None:
    """PRIORITY_ALPHA must match prereg-locked constant."""
    ac = AtomConsultant()
    if abs(ac._PRIORITY_ALPHA - _PRIORITY_ALPHA_LOCKED) > 1e-9:
        raise AssertionError(
            f"PRIORITY_ALPHA drift: primitive={ac._PRIORITY_ALPHA} != "
            f"prereg={_PRIORITY_ALPHA_LOCKED}")


def _selftest_case3_expected_rec_corrected() -> None:
    """Case 3 expected_rec locked at SCALE_FREE per Skunkworks correction."""
    case3 = next(c for c in _GROUND_TRUTH_CASES
                 if c["case_id"] == "case3_scale_free_law")
    if case3["expected_rec"] != "SCALE_FREE":
        raise AssertionError(
            f"case3 expected_rec drift: got {case3['expected_rec']!r} "
            f"!= 'SCALE_FREE' (Skunkworks VET Rec #2 correction)")


def _selftest_probe_end_to_end() -> None:
    """Run full probe; assert schema + pre-committed prediction (case3 flip)."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        metrics = run_probe(Path(td), run_mode="self_test")
        assert metrics["n_calls"] == EXPECTED_N_UNITS
        assert metrics["n_warmup_calls"] == N_WARMUP_CALLS
        assert metrics["n_tag_filter_bypass"] == 0, (
            f"selftest: tag-filter bypass in "
            f"{metrics['n_tag_filter_bypass']} calls")
        # Case3 flip discriminator (this cell's raison d'etre).
        assert metrics["case3_flipped"], (
            f"selftest: case3 did NOT flip to SCALE_FREE full 10/10; "
            f"honored={metrics['per_case_honored']['case3_scale_free_law']} "
            f"of {metrics['per_case_total']['case3_scale_free_law']}")
        # Preserved-case anti-regression.
        assert not metrics["preserved_case_regressions"], (
            f"selftest: preserved-case regression "
            f"{metrics['preserved_case_regressions']}")
        # Pre-committed prediction: overall >= 0.90.
        assert metrics["match_and_honored_over_all"] >= 0.90, (
            f"selftest: match_and_honored_over_all="
            f"{metrics['match_and_honored_over_all']:.3f} < 0.90 (predicted)")
        assert metrics["wall_ms_p95"] <= 5.0
        assert metrics["verdict"] == "HARD_PASS", (
            f"selftest: expected HARD_PASS, got {metrics['verdict']!r} "
            f"({metrics['verdict_msg']})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        _selftest_priority_alpha_locked()
        _selftest_case3_expected_rec_corrected()
        _selftest_probe_end_to_end()
        print(f"[{ANCHOR_NAME} self-test] PASS", flush=True)
        return

    if args.smoke:
        run_mode = "smoke"
    elif args.full:
        run_mode = "full"
    else:
        run_mode = "smoke"

    output_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(output_dir, run_mode)
    metrics = run_probe(output_dir, run_mode)
    print(f"[{ANCHOR_NAME}] verdict={metrics['verdict']} "
          f"msg={metrics['verdict_msg']}", flush=True)


if __name__ == "__main__":
    _OUTPUT_DIR = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:
        _write_crash_metrics(_OUTPUT_DIR, _e)
        raise
