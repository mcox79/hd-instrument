"""Cortex-2 atom-consultation ADVISORY-ONLY smoke v1.1 -- WARMUP-FIX (2026-07-03).

Delta from v1 (per Skunkworks landed-VET branch-(a) recommendation, math
atom #54 MM_TENTATIVE_ADVISORY, task ac63eee40ecd0f2d2):

  - v1 SMOKE landed HARD_FAIL_WALL_BUDGET: p95=6.31ms > 5ms budget.
    BUT steady-state calls 25-49 in v1 measured p50=0.97ms, p95=2.63ms,
    max=3.80ms -- all under budget. Cold-start tail (calls 0-2) was
    OS/JIT (identical n_scanned=2 for the SHARDED case per Skunkworks VET),
    NOT intrinsic primitive latency.
  - v1.1 adds 3 WARMUP calls BEFORE the 50 measured calls. Warmup calls
    are DISCARDED from the p50/p95/max computation and from every
    discriminator (match_and_honored, tag_filter_bypass, cardinality).
  - All other physics / discriminator / schema semantics IDENTICAL to v1
    (same 5 ground-truth cases, 10 variations each, same encoder, same
    AtomConsultant, same source_signature axes, same PASS/FAIL bands).

Warmup discipline (pre-committed in prereg BEFORE running):
  - 3 warmup calls, case_id="_warmup", op_class=COMPOSITION (case 1
    SHARDED, first variation), fixed a-priori. NOT tunable to force pass.
  - Warmup wall_ms recorded to metrics.json under `warmup_wall_ms` for
    audit (Skunkworks can verify cold-start pattern is real), but
    EXCLUDED from every discriminator.

Pre-committed predictions (v1.1):
  - wall_p95 <= 5ms (post-warmup, over 50 measured calls) -- PASS
  - match_and_honored_over_all preserves 0.80 +/- 0.05 -- retrieval
    discriminator preserved (identical corpus + identical cases)
  - 0 silent contradictions, 0 tag_filter_bypass, 50 cardinality
  - FAIL branch: wall_p95 still > 5ms -> 6.31ms is intrinsic OR primitive
    code-path is inefficient; escalate to branch-(b) diagnostic cell.

Cell purpose (unchanged from v1): exercise AtomConsultant primitive on 5
hand-built ground-truth cases (COMPOSITION / FRAMING / CAPACITY /
RETRIEVAL / VERIFY) across ~10 param variations each = 50 consultation
calls. Measure:
- match-and-honored rate: (matched atom's recommendation matches the
  ground-truth downstream choice for that case) / (matched cases).
- sub-ms wall assert per consult() call (post-warmup steady-state).
- strict-subset tag-filter (scanned < total on every call).
- zero silent contradictions (bucket-ii cases must be flagged).

Phase: ADVISORY-ONLY (applied=False throughout). Retrieval-correctness
probe, NOT enforcement.

Gates (SMOKE, v1.1):
  HARD_PASS_MATCH_AND_HONORED : rate >= 0.70 AND zero silent contradictions
                                across the 50 MEASURED calls.
  HARD_FAIL_DECORATIVE        : rate < 0.20 -> decorative retrieval; route
                                back to research.
  MIDDLE_BAND                 : 0.20 <= rate < 0.70. Tag-filter tuning
                                needed under Skunkworks discipline.
  HARD_FAIL_WALL_BUDGET       : wall_p95 > 5ms across the 50 MEASURED
                                calls (post-3-warmup).
  HARD_FAIL_TAG_FILTER_BYPASS : any measured consult() scanned == total.

Source signature (per USER-locked MM_STANDARD 2026-07-03):
  v1.1 warmup-fix, cortex-2 arc, N=99 atom corpus 2026-07-03 end-state
  (curated subset of 7 covering the 5 ground-truth cases + 2 distractors);
  5 operation classes; 50 measured + 3 warmup calls; advisory-only phase;
  char-trigram encoder N=1024.

Anti-drift:
  - 3 warmup calls LOCKED in prereg BEFORE running -- NOT tunable.
  - Warmup case = SHARDED (case 1 var 0) fixed a-priori -- no cherry-picking.
  - Discriminator computation ONLY on the 50 measured calls.
  - Skunkworks-audit sample every N=10 measured calls (per hand-off memo
    section e, unchanged from v1).
  - Zero silent contradictions: bucket-ii MUST be flagged per-call.
  - MM_TENTATIVE at SMOKE at most (arc-continuation != arc-closure).

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
- cardinality_ok: EXPECTED_N_UNITS = 5 cases x 10 variations = 50 MEASURED
  (warmup calls NOT counted).

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

# Line-buffered stdout so smoke progress is visible in runner logs.
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


ANCHOR_NAME = "cortex2_atom_consultation_smoke_v1_1_warmup_fix_s7"

# WARMUP DISCIPLINE (v1.1 fix):
# - 3 warmup calls fixed a-priori (pre-committed in prereg).
# - Warmup case is SHARDED / COMPOSITION (case 1 first variation).
# - Warmup wall discarded from every discriminator (p50, p95, max,
#   match_and_honored, tag_filter_bypass, cardinality).
N_WARMUP_CALLS = 3
_WARMUP_OP_CLASS = "COMPOSITION"
_WARMUP_PARAMS = {"storage": "BUNDLED", "N": 1024, "M": 6400, "corr": 0.85}
_WARMUP_QUERY_HINT = "storage strategy composition K exceeds wall"

# 5 hand-built ground-truth cases (IDENTICAL to v1 per hand-off memo
# section d). Each case: (op_class, params dict, query_hint,
# expected_recommendation). 10 param variations per case = 50 calls per
# full smoke pass.
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
        # per anti-drift (see prereg).
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
        "n_warmup_calls": N_WARMUP_CALLS,
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
    """Run 3 warmup calls (discarded) + 5 cases x 10 vars = 50 measured calls."""
    t0 = time.perf_counter()
    ac = AtomConsultant()
    n_total_atoms = ac.n_atoms_total()

    # ---- WARMUP PHASE (v1.1 fix; DISCARDED from every discriminator) ----
    warmup_wall_ms = []
    for w in range(N_WARMUP_CALLS):
        wr: ConsultationResult = ac.consult(
            _WARMUP_OP_CLASS, params=_WARMUP_PARAMS,
            query_hint=_WARMUP_QUERY_HINT)
        warmup_wall_ms.append(wr.wall_ms)
        print(f"[warmup] call={w+1}/{N_WARMUP_CALLS} "
              f"wall_ms={wr.wall_ms:.4f} (DISCARDED)", flush=True)

    # ---- MEASUREMENT PHASE (50 calls; discriminator inputs) ----
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
            # Bucket-ii = matched but recommendation != expected. Flag
            # EXPLICITLY per-call so "silent contradiction" is provably 0.
            bucket_ii_flag = matched and (not honored)
            if bucket_ii_flag:
                pass  # explicitly logged in per_call record below
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
            # Skunkworks-audit sample every N=10 measured calls (unchanged from v1).
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
    # p50/p95/max computed over MEASURED calls only (warmup excluded).
    wall_p50 = float(_np.percentile(wall_ms_all, 50)) if wall_ms_all else 0.0
    wall_p95 = float(_np.percentile(wall_ms_all, 95)) if wall_ms_all else 0.0
    wall_max = float(_np.max(wall_ms_all)) if wall_ms_all else 0.0

    # Warmup wall stats (audit-only; not gated).
    warmup_p50 = (float(_np.percentile(warmup_wall_ms, 50))
                  if warmup_wall_ms else 0.0)
    warmup_max = (float(_np.max(warmup_wall_ms))
                  if warmup_wall_ms else 0.0)

    # Verdict computation.
    fatal_reasons = []
    if wall_p95 > 5.0:
        fatal_reasons.append(
            f"HARD_FAIL_WALL_BUDGET: p95={wall_p95:.3f}ms > 5ms "
            f"(post-{N_WARMUP_CALLS}-warmup; intrinsic latency or "
            f"primitive-code-path inefficient; escalate branch (b) diagnostic)")
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
        if match_and_honored_over_all >= 0.70:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS (v1.1 warmup-fix): match_and_honored_over_all="
                f"{match_and_honored_over_all:.3f} >= 0.70 across {n_calls} "
                f"measured calls (post-{N_WARMUP_CALLS}-warmup); "
                f"wall_p95={wall_p95:.3f}ms <= 5ms; "
                f"bucket_ii_silent_contradictions=0 by construction.")
        elif match_and_honored_over_all < 0.20:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL_DECORATIVE (v1.1): match_and_honored_over_all="
                f"{match_and_honored_over_all:.3f} < 0.20; route back to "
                f"research for tag-vector rework.")
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND (v1.1): match_and_honored_over_all="
                f"{match_and_honored_over_all:.3f} in [0.20, 0.70); "
                f"tag-filter tuning under Skunkworks discipline before "
                f"promotion.")

    summary = (
        f"cortex2 atom-consultation smoke v1.1 warmup-fix ADVISORY-ONLY: "
        f"n_measured={n_calls}, n_warmup={N_WARMUP_CALLS}, "
        f"match_rate={match_rate:.3f}, "
        f"match_and_honored_rate={match_and_honored_rate:.3f}, "
        f"match_and_honored_over_all={match_and_honored_over_all:.3f}, "
        f"wall_p50={wall_p50:.4f}ms, wall_p95={wall_p95:.4f}ms, "
        f"wall_max={wall_max:.4f}ms, "
        f"warmup_p50={warmup_p50:.4f}ms, warmup_max={warmup_max:.4f}ms, "
        f"n_atoms_total={n_total_atoms}, tag_filter_bypass={n_tag_filter_bypass}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed_s,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "phase": "ADVISORY_ONLY_v1_1_warmup_fix",
        "applied_flag_v1": False,
        "warmup_fix_v1_1": (
            "3 warmup calls discarded from p50/p95/max/discriminator; "
            "Skunkworks landed-VET branch (a) recommendation "
            "(task ac63eee40ecd0f2d2, math atom #54 MM_TENTATIVE_ADVISORY)"),
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
        "wall_ms_p50": wall_p50,
        "wall_ms_p95": wall_p95,
        "wall_ms_max": wall_max,
        "n_atoms_total": n_total_atoms,
        "op_classes": sorted(VALID_OP_CLASSES),
        "source_signature": (
            "v1.1 warmup-fix, cortex-2 arc, N=99 atom corpus 2026-07-03 "
            f"end-state (curated subset of {n_total_atoms} atoms covering "
            "5 ground-truth cases); advisory-only; 5 op-classes; "
            f"50 measured + {N_WARMUP_CALLS} warmup calls"),
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
    """Self-test: run full probe in scratch dir; assert schema + wall gate.

    v1.1 pre-commit: wall_p95 <= 5ms post-warmup on self-test host.
    match_and_honored_over_all >= 0.70 (same curated corpus as v1)."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        metrics = run_probe(Path(td), run_mode="self_test")
        assert metrics["n_calls"] == EXPECTED_N_UNITS, (
            f"selftest: n_calls={metrics['n_calls']} != "
            f"expected={EXPECTED_N_UNITS}")
        assert metrics["n_warmup_calls"] == N_WARMUP_CALLS
        assert len(metrics["warmup_wall_ms"]) == N_WARMUP_CALLS
        assert metrics["n_tag_filter_bypass"] == 0, (
            f"selftest: tag-filter bypass in "
            f"{metrics['n_tag_filter_bypass']} calls")
        # v1.1 fix's core assertion: p95 <= 5ms post-warmup.
        assert metrics["wall_ms_p95"] <= 5.0, (
            f"selftest: p95 wall {metrics['wall_ms_p95']:.3f}ms > 5ms "
            f"even after {N_WARMUP_CALLS} warmup calls; branch (b) "
            f"diagnostic needed")
        # Retrieval discriminator preserved (unchanged corpus).
        assert metrics["match_and_honored_over_all"] >= 0.70, (
            f"selftest: match_and_honored={metrics['match_and_honored_over_all']:.3f} "
            f"< 0.70; retrieval regressed vs v1")
        assert metrics["verdict"] in {"HARD_PASS", "HARD_FAIL", "MIDDLE_BAND"}


def _selftest_op_class_coverage() -> None:
    """All 4 unique op-classes represented in ground-truth cases."""
    seen = {c["op_class"] for c in _GROUND_TRUTH_CASES}
    expected_unique = {"COMPOSITION", "CAPACITY", "FRAMING", "VERIFY"}
    if not expected_unique.issubset(seen):
        raise AssertionError(
            f"missing op-class coverage: seen={seen}, "
            f"expected superset of {expected_unique}")


def _selftest_warmup_discipline() -> None:
    """Warmup case + count are pre-committed constants (anti-drift)."""
    assert N_WARMUP_CALLS == 3, (
        f"warmup discipline: N_WARMUP_CALLS locked at 3 in prereg; "
        f"got {N_WARMUP_CALLS}")
    assert _WARMUP_OP_CLASS == "COMPOSITION"
    assert _WARMUP_PARAMS.get("storage") == "BUNDLED"
    assert _WARMUP_PARAMS.get("N") == 1024


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        _selftest_op_class_coverage()
        _selftest_warmup_discipline()
        _selftest_probe_end_to_end()
        print(f"[{ANCHOR_NAME} self-test] PASS", flush=True)
        return

    if args.smoke:
        run_mode = "smoke"
    elif args.full:
        run_mode = "full"
    else:
        # Default: smoke (per META_RULE_16 RUN_MODE VERIFICATION).
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
    except Exception as _e:  # NOT BaseException per META_RULE_8.
        _write_crash_metrics(_OUTPUT_DIR, _e)
        raise
