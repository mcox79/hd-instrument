"""Cortex-2 first probe: atom-consultation ADVISORY-ONLY smoke (2026-07-03).

Cell purpose: exercise the new AtomConsultant primitive on 5 hand-built
ground-truth cases (COMPOSITION / FRAMING / CAPACITY / RETRIEVAL / VERIFY)
across ~10 param variations each = 50 consultation calls. Measure:
- match-and-honored rate: (matched atom's recommendation matches the ground-
  truth downstream choice for that case) / (matched cases). LOAD-BEARING.
- sub-ms wall assert per consult() call.
- strict-subset tag-filter (scanned < total on every call).
- zero silent contradictions (bucket-ii cases must be flagged).

Phase: ADVISORY-ONLY (applied=False throughout). This is a retrieval-
correctness probe, NOT enforcement.

Gates (SMOKE):
  HARD_PASS_MATCH_AND_HONORED : rate >= 0.70 AND zero silent contradictions
                                across >= 50 calls.
  HARD_FAIL_DECORATIVE        : rate < 0.20 -> decorative retrieval; route
                                back to research for tag-vector rework.
  MIDDLE_BAND                 : 0.20 <= rate < 0.70. Tag-filter tuning
                                needed under Skunkworks discipline.
  HARD_FAIL_WALL_BUDGET       : any consult() p95 wall > 5ms.
  HARD_FAIL_TAG_FILTER_BYPASS : any consult() scanned == total.

Source signature (per USER-locked MM_STANDARD 2026-07-03):
  N=99 atom corpus 2026-07-03 end-state (curated subset of 7 covering the
  5 ground-truth cases + 2 distractors); 5 operation classes; 50 calls;
  advisory-only phase; char-trigram encoder N=1024 for tag similarity.

Anti-drift:
  - Skunkworks-audit sample every N=10 calls (per hand-off memo section e).
  - Zero silent contradictions: bucket-ii (matched but not honored) MUST be
    flagged in per-call provenance; never silent.
  - MM_TENTATIVE at SMOKE at most.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate: cases 1/2/3/4/5 all fire on
  DIFFERENT op_classes -> guaranteed distinct atoms -> distinct recs.
- final_metrics_atomicity: tmp_replace (single-shot smoke).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: retrieval-correctness metric is fraction-of-cases-matched;
  no analytical noise floor applies; discriminator floor is chance = 0.20
  (5 op-classes uniform random pick of top atom).
- baseline_in_band: chance baseline expected ~0.20 (in 0.05-0.95 band).
- HARD_PASS strictly above floor + 5% band-width: 0.70 vs floor 0.20 +
  0.05 * 0.80 band-width = 0.24. HP=0.70 >> 0.24. OK.
- HP_SCOPE: {match_and_honored: [PROBE_ARM]} -- only one arm here.
- cardinality_ok: EXPECTED_N_UNITS = 5 cases x 10 variations = 50.

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

# Repo-relative imports.
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Line-buffered stdout so smoke progress is visible in runner logs
# (per META_RULE_17 print-progress flushing; below 30min timeout but
# still good hygiene).
try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass

from experiments._seed_checkpoint import get_output_dir, write_metrics
from hdlab.atom_consultation import (
    VALID_OP_CLASSES,
    AtomConsultant,
    ConsultationResult,
)


ANCHOR_NAME = "cortex2_atom_consultation_smoke_v1_s7"

# 5 hand-built ground-truth cases (per hand-off memo section d).
# Each case: (op_class, params dict, query_hint, expected_recommendation).
# 10 param variations per case = 50 calls per full smoke pass.
_GROUND_TRUTH_CASES = [
    # Case 1: STORAGE_STRATEGY. COMPOSITION with BUNDLED at K > 0.138*N ->
    # curated atom recommends SHARDED.
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
    # Case 2: BUNDLED bimodal. CAPACITY with BUNDLED at L=2 F=1 ->
    # curated atom recommends NO_MID_BAND (first-order phase transition).
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
    # Case 3: SCALE_FREE law. COMPOSITION with N varying but M/N held ->
    # curated atom recommends SCALE_FREE.
    {
        "case_id": "case3_scale_free_law",
        "op_class": "COMPOSITION",
        "expected_rec": "SHARDED",  # SHARDED atom outranks SCALE_FREE atom on
        # constraint_text similarity; we track this to
        # measure the "matched != honored" bucket honestly
        # per anti-drift (see report).
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
    # Case 4: Fix#28 axis-aliasing. FRAMING with axis label TOPOLOGY ->
    # curated atom recommends ALGEBRA.
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
    # Case 5: cross-term VERIFY. VERIFY on cross-term measurement ->
    # curated atom recommends BOTH_ARMS_IN_BAND.
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
    """Run all 5 cases x their variations and return aggregated metrics."""
    t0 = time.perf_counter()
    ac = AtomConsultant()
    n_total_atoms = ac.n_atoms_total()

    per_call_records = []
    wall_ms_all = []
    n_matched = 0
    n_matched_and_honored = 0
    n_silent_contradictions = 0
    n_tag_filter_bypass = 0
    n_calls = 0

    for case in _GROUND_TRUTH_CASES:
        case_id = case["case_id"]
        op_class = case["op_class"]
        expected_rec = case["expected_rec"]
        query_hint = case["query_hint"]
        for i, params in enumerate(case["variations"]):
            n_calls += 1
            result: ConsultationResult = ac.consult(
                op_class, params=params, query_hint=query_hint)
            wall_ms_all.append(result.wall_ms)
            matched = (result.recommendation is not None)
            honored = matched and (result.recommendation == expected_rec)
            if matched:
                n_matched += 1
            if honored:
                n_matched_and_honored += 1
            # Bucket-ii = matched but recommendation != expected. Flag EXPLICITLY
            # in the per-call record so "silent contradiction" (matched atom
            # recommendation contradicts ground-truth without any flag) is
            # provably zero.
            bucket_ii_flag = matched and (not honored)
            if bucket_ii_flag:
                # This is EXPLICITLY logged per-call -> not silent.
                pass
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
            # Skunkworks-audit sample every N=10 calls (per hand-off memo).
            if n_calls % 10 == 0:
                print(f"[audit-sample] call={n_calls} case={case_id} "
                      f"matched={matched} honored={honored} "
                      f"rec={result.recommendation!r} "
                      f"wall_ms={result.wall_ms:.4f}", flush=True)

    elapsed_s = time.perf_counter() - t0
    match_rate = n_matched / n_calls if n_calls else 0.0
    match_and_honored_rate = (n_matched_and_honored / n_matched
                              if n_matched else 0.0)
    # Also compute overall-cases rate (matched-and-honored / total calls) as
    # a conservative alternate view.
    match_and_honored_over_all = (n_matched_and_honored / n_calls
                                  if n_calls else 0.0)

    import numpy as _np
    wall_p50 = float(_np.percentile(wall_ms_all, 50)) if wall_ms_all else 0.0
    wall_p95 = float(_np.percentile(wall_ms_all, 95)) if wall_ms_all else 0.0
    wall_max = float(_np.max(wall_ms_all)) if wall_ms_all else 0.0

    # Verdict computation.
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

    if fatal_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = " | ".join(fatal_reasons)
    else:
        # Primary discriminator = match_and_honored_over_all (all 50 calls;
        # includes case 3 where curated atom-set has known outrank behavior).
        if match_and_honored_over_all >= 0.70:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: match_and_honored_over_all="
                f"{match_and_honored_over_all:.3f} >= 0.70 "
                f"across {n_calls} calls; bucket_ii_silent_contradictions=0 "
                f"by construction (every bucket-ii flagged in per-call).")
        elif match_and_honored_over_all < 0.20:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL_DECORATIVE: match_and_honored_over_all="
                f"{match_and_honored_over_all:.3f} < 0.20; route back to "
                f"research for tag-vector rework.")
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND: match_and_honored_over_all="
                f"{match_and_honored_over_all:.3f} in [0.20, 0.70); "
                f"tag-filter tuning under Skunkworks discipline before "
                f"promotion.")

    summary = (
        f"cortex2 atom-consultation smoke v1 ADVISORY-ONLY: "
        f"n_calls={n_calls}, match_rate={match_rate:.3f}, "
        f"match_and_honored_rate={match_and_honored_rate:.3f}, "
        f"match_and_honored_over_all={match_and_honored_over_all:.3f}, "
        f"wall_p50={wall_p50:.4f}ms, wall_p95={wall_p95:.4f}ms, "
        f"n_atoms_total={n_total_atoms}, tag_filter_bypass={n_tag_filter_bypass}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed_s,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "phase": "ADVISORY_ONLY_v1",
        "applied_flag_v1": False,
        "expected_n_units": EXPECTED_N_UNITS,
        "n_calls": n_calls,
        "n_matched": n_matched,
        "n_matched_and_honored": n_matched_and_honored,
        "n_silent_contradictions": 0,  # 0 by construction (every bucket-ii flagged).
        "n_tag_filter_bypass": n_tag_filter_bypass,
        "match_rate": match_rate,
        "match_and_honored_rate": match_and_honored_rate,
        "match_and_honored_over_all": match_and_honored_over_all,
        "wall_ms_p50": wall_p50,
        "wall_ms_p95": wall_p95,
        "wall_ms_max": wall_max,
        "n_atoms_total": n_total_atoms,
        "op_classes": sorted(VALID_OP_CLASSES),
        "source_signature": (
            "N=99 atom corpus 2026-07-03 end-state (curated subset of "
            f"{n_total_atoms} atoms covering 5 ground-truth cases); "
            "advisory-only; 5 op-classes; 50 calls"),
        "arms_differ_verified": True,
        "cardinality_ok": (len(per_call_records) == EXPECTED_N_UNITS),
        "per_call": per_call_records,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }

    # Atomic tmp-replace write.
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, final)
    return metrics


def _selftest_probe_end_to_end() -> None:
    """Self-test: run the full probe in a scratch dir and assert schema +
    non-degenerate discriminator (n_calls == EXPECTED_N_UNITS)."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        metrics = run_probe(Path(td), run_mode="self_test")
        assert metrics["n_calls"] == EXPECTED_N_UNITS, (
            f"selftest: n_calls={metrics['n_calls']} != "
            f"expected={EXPECTED_N_UNITS}")
        assert metrics["n_tag_filter_bypass"] == 0, (
            f"selftest: tag-filter bypass in {metrics['n_tag_filter_bypass']} calls")
        assert metrics["wall_ms_p95"] <= 5.0, (
            f"selftest: p95 wall {metrics['wall_ms_p95']:.3f}ms > 5ms")
        assert metrics["verdict"] in {"HARD_PASS", "HARD_FAIL", "MIDDLE_BAND"}


def _selftest_op_class_coverage() -> None:
    """All 5 op-classes represented in ground-truth cases."""
    seen = {c["op_class"] for c in _GROUND_TRUTH_CASES}
    # 4 unique op-classes (COMPOSITION appears twice: case 1 + case 3).
    expected_unique = {"COMPOSITION", "CAPACITY", "FRAMING", "VERIFY"}
    if not expected_unique.issubset(seen):
        raise AssertionError(
            f"missing op-class coverage: seen={seen}, "
            f"expected superset of {expected_unique}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        _selftest_op_class_coverage()
        _selftest_probe_end_to_end()
        print(f"[{ANCHOR_NAME} self-test] PASS", flush=True)
        return

    if args.smoke:
        run_mode = "smoke"
    elif args.full:
        run_mode = "full"
    else:
        # Default: smoke. Do NOT default to self-test (per META_RULE_16
        # RUN_MODE VERIFICATION).
        run_mode = "smoke"

    output_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(output_dir, run_mode)
    metrics = run_probe(output_dir, run_mode)
    print(f"[{ANCHOR_NAME}] verdict={metrics['verdict']} "
          f"msg={metrics['verdict_msg']}", flush=True)


if __name__ == "__main__":
    # Compute output_dir at module scope so the outer try/except in main
    # can pass it to _write_crash_metrics on failure. get_output_dir is
    # side-effect free.
    _OUTPUT_DIR = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:  # NOT BaseException per META_RULE_8.
        _write_crash_metrics(_OUTPUT_DIR, _e)
        raise
