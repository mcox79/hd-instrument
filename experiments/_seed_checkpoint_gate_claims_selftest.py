"""Self-tests for the OPT-IN structured gate_claims extension of write_metrics.

Added 2026-07-05 (Testbed) alongside the record_gate / write_metrics(gate_claims)
change in _seed_checkpoint.py. Kept in a SEPARATE file (not the module's import-time
selftest) so the shared library imported by thousands of cells gains ZERO extra
import-time cost. Run directly:

    python experiments/_seed_checkpoint_gate_claims_selftest.py

Exits 0 on success, non-zero on any failure. ASCII-only per
feedback_ascii_only_in_scripts.

Covers:
  A. BACKWARD-COMPAT byte-identical proof -- the golden is a FROZEN verbatim copy
     of the pre-2026-07-05 write_metrics body (_legacy_write_metrics below).
     write_metrics(..., gate_claims=None) must produce byte-for-byte identical
     metrics.json across many metric shapes.
  B. ROUND-TRIP -- write gate_claims -> read metrics.json back -> exact match.
  C. record_gate verdict correctness across all 5 ops (pass + fail).
  D. Fail-fast schema validation (malformed claims raise BEFORE any write).
  E. Non-interference -- supplying gate_claims leaves every other key identical
     to the legacy output for the same base metrics.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

# Make the sibling module importable regardless of CWD.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _seed_checkpoint import (  # noqa: E402
    record_gate,
    write_metrics,
    _validate_gate_claims,
)


# ---------------------------------------------------------------------------
# FROZEN reference: verbatim copy of write_metrics' body as it was BEFORE the
# 2026-07-05 gate_claims change (commit 4feca27e3). This is the "golden" the
# backward-compat test diffs against. DO NOT edit to track future changes -- it
# exists precisely to detect any drift from the historical output.
# ---------------------------------------------------------------------------
def _legacy_write_metrics(out_dir: Path, metrics: Dict[str, Any],
                          results: Optional[Sequence[Dict[str, Any]]] = None
                          ) -> Dict[str, Any]:
    if metrics.get("elapsed_s") is None:
        tot = 0.0
        for r in (results or []):
            try:
                tot += float(r.get("elapsed_s") or 0.0)
            except (TypeError, ValueError, AttributeError):
                pass
        metrics["elapsed_s"] = tot
    if not metrics.get("summary"):
        metrics["summary"] = metrics.get("verdict_msg") or metrics.get("verdict") or ""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


# Representative metric shapes exercising every branch of the injection logic.
_SHAPES = {
    "A_all_fields_present": (
        {"verdict": "HARD_PASS", "verdict_msg": "ok", "summary": "done",
         "elapsed_s": 12.5, "op_agreement": 1.0, "nested": {"k": [1, 2, 3]}},
        None,
    ),
    "B_missing_elapsed_and_summary_with_results": (
        {"verdict": "PASS", "verdict_msg": "clean run"},
        [{"elapsed_s": 2.0}, {"elapsed_s": 3.5}, {"elapsed_s": None}],
    ),
    "C_missing_elapsed_no_results_empty_summary": (
        {"verdict": "FAIL", "verdict_msg": "band miss", "summary": ""},
        None,
    ),
    "D_elapsed_present_summary_missing": (
        {"verdict": "PARTIAL", "verdict_msg": "mixed", "elapsed_s": 0.0},
        [],
    ),
    "E_unicode_and_falsy_verdict_msg": (
        {"verdict": "", "verdict_msg": "", "elapsed_s": 1.0,
         "note": "band <= 0.9 -> ok; ratio >= 1.0"},
        None,
    ),
    "F_results_with_bad_elapsed_entries": (
        {"verdict": "PASS", "verdict_msg": "x"},
        [{"elapsed_s": "notnum"}, {"nope": 1}, {"elapsed_s": 4}],
    ),
}


def _t(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"[selftest] PASS: {label}")


def test_backward_compat_byte_identical() -> None:
    """A: gate_claims=None -> byte-identical metrics.json vs frozen legacy."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        for name, (metrics, results) in _SHAPES.items():
            leg_dir = base / f"leg_{name}"
            new_dir = base / f"new_{name}"
            leg_ret = _legacy_write_metrics(leg_dir, copy.deepcopy(metrics),
                                            copy.deepcopy(results))
            new_ret = write_metrics(new_dir, copy.deepcopy(metrics),
                                    copy.deepcopy(results))  # gate_claims omitted
            leg_bytes = (leg_dir / "metrics.json").read_bytes()
            new_bytes = (new_dir / "metrics.json").read_bytes()
            _t(leg_bytes == new_bytes,
               f"A[{name}] metrics.json byte-identical "
               f"({len(leg_bytes)} bytes)")
            _t(leg_ret == new_ret, f"A[{name}] returned dict identical")
            _t("structured_gate_claims" not in new_ret,
               f"A[{name}] no structured_gate_claims key on None path")

        # Explicit gate_claims=None keyword must also be a no-op.
        m = {"verdict": "PASS", "verdict_msg": "kw", "elapsed_s": 1.0}
        d1 = base / "kw_none"
        d2 = base / "kw_absent"
        write_metrics(d1, copy.deepcopy(m), gate_claims=None)
        write_metrics(d2, copy.deepcopy(m))
        _t((d1 / "metrics.json").read_bytes() == (d2 / "metrics.json").read_bytes(),
           "A[kw] gate_claims=None identical to omitting the kwarg")


def test_round_trip() -> None:
    """B: write gate_claims -> read metrics.json -> exact field match."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "rt"
        claims = [
            record_gate("op_agreement", 1.0, 1.0, "=="),
            record_gate("flag_recall", 0.97, 0.90, ">="),
            record_gate("false_parse_rate", 0.02, 0.05, "<=",
                        note="16/915 residual free-text misparses"),
            record_gate("retrieval_hit_rate", 0.108, 0.10, ">"),
        ]
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "loop closes",
                   "summary": "s", "elapsed_s": 3.0}
        write_metrics(out, metrics, gate_claims=claims)

        loaded = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
        _t("structured_gate_claims" in loaded, "B key present after opt-in")
        got = loaded["structured_gate_claims"]
        _t(got == claims, "B round-trip exact match (read == record_gate output)")
        # Field-level integrity on one claim carrying an optional note.
        c2 = got[2]
        _t(c2["gate_name"] == "false_parse_rate", "B gate_name preserved")
        _t(c2["measured"] == 0.02 and c2["threshold"] == 0.05, "B operands preserved")
        _t(c2["op"] == "<=" and c2["gate_verdict"] is True, "B op+verdict preserved")
        _t(c2["note"] == "16/915 residual free-text misparses", "B note preserved")
        # Canonical key order per claim (deterministic for the audit consumer).
        _t(list(got[0].keys()) == ["gate_name", "measured", "threshold", "op",
                                   "gate_verdict"],
           "B canonical key order (no note)")
        _t(list(got[2].keys()) == ["gate_name", "measured", "threshold", "op",
                                   "gate_verdict", "note"],
           "B canonical key order (with note)")

        # Empty list is a deliberate opt-in: stores [] (distinct from None path).
        out2 = Path(td) / "rt_empty"
        write_metrics(out2, {"verdict": "PASS", "verdict_msg": "x", "elapsed_s": 0.0},
                      gate_claims=[])
        loaded2 = json.loads((out2 / "metrics.json").read_text(encoding="utf-8"))
        _t(loaded2.get("structured_gate_claims") == [],
           "B empty gate_claims list stored as []")


def test_record_gate_verdicts() -> None:
    """C: verdict computed correctly for every op, both directions."""
    cases = [
        (">=", 1.0, 1.0, True), (">=", 0.9, 1.0, False),
        ("<=", 0.9, 1.0, True), ("<=", 1.1, 1.0, False),
        ("==", 5, 5, True), ("==", 5, 6, False),
        (">", 2.0, 1.0, True), (">", 1.0, 1.0, False),
        ("<", 0.5, 1.0, True), ("<", 1.0, 1.0, False),
    ]
    for op, m, t, expect in cases:
        c = record_gate(f"g_{op}", m, t, op)
        _t(c["gate_verdict"] is expect,
           f"C record_gate({m} {op} {t}) verdict == {expect}")
    # int-ness preserved for a count; float stays float.
    ci = record_gate("count", 5, 3, ">")
    _t(ci["measured"] == 5 and isinstance(ci["measured"], int),
       "C int measured preserved (5, not 5.0)")
    cf = record_gate("ratio", 0.5, 0.25, ">")
    _t(isinstance(cf["measured"], float), "C float measured preserved")
    # numeric string coerces to float.
    cs = record_gate("coerced", "0.5", "0.25", ">")
    _t(cs["measured"] == 0.5 and cs["gate_verdict"] is True,
       "C numeric-string operand coerced + compared")


def _raises(fn, exc) -> bool:
    try:
        fn()
    except exc:
        return True
    except Exception as other:  # noqa: BLE001
        print(f"[selftest]   (raised {type(other).__name__}, expected {exc.__name__})")
        return False
    return False


def test_fail_fast_validation() -> None:
    """D: malformed claims raise, and raise BEFORE any file is written."""
    # record_gate rejects bad op / non-numeric / empty name.
    _t(_raises(lambda: record_gate("g", 1.0, 1.0, "!="), ValueError),
       "D record_gate rejects unknown op")
    _t(_raises(lambda: record_gate("", 1.0, 1.0, ">="), ValueError),
       "D record_gate rejects empty gate_name")
    _t(_raises(lambda: record_gate("g", True, 1.0, ">="), ValueError),
       "D record_gate rejects bool measured")
    _t(_raises(lambda: record_gate("g", "abc", 1.0, ">="), ValueError),
       "D record_gate rejects non-numeric measured")

    # _validate_gate_claims (the write_metrics gate) rejects bad shapes.
    good = record_gate("g", 1.0, 1.0, ">=")
    _t(_raises(lambda: _validate_gate_claims(good), TypeError),
       "D validate rejects a single dict (must be a list)")
    _t(_raises(lambda: _validate_gate_claims([{"gate_name": "g"}]), ValueError),
       "D validate rejects claim missing required keys")
    bad_op = {**good, "op": "!="}
    _t(_raises(lambda: _validate_gate_claims([bad_op]), ValueError),
       "D validate rejects bad op in claim")
    bad_num = {**good, "measured": "x"}
    _t(_raises(lambda: _validate_gate_claims([bad_num]), ValueError),
       "D validate rejects non-numeric measured in claim")
    bad_bool = {**good, "measured": True}
    _t(_raises(lambda: _validate_gate_claims([bad_bool]), ValueError),
       "D validate rejects bool measured in claim")
    bad_verdict = {**good, "gate_verdict": "PASS"}
    _t(_raises(lambda: _validate_gate_claims([bad_verdict]), ValueError),
       "D validate rejects non-bool gate_verdict")

    # Fail-fast: a malformed claim must raise WITHOUT writing metrics.json.
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "ff"
        raised = _raises(
            lambda: write_metrics(out, {"verdict": "PASS", "verdict_msg": "m"},
                                  gate_claims=[bad_op]),
            ValueError)
        _t(raised, "D write_metrics raises on malformed gate_claims")
        _t(not (out / "metrics.json").exists(),
           "D fail-fast: NO metrics.json written when validation fails")


def test_non_interference() -> None:
    """E: gate_claims only ADDS its key; every other key matches legacy."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        metrics = {"verdict": "PASS", "verdict_msg": "m", "acc": 0.9}
        leg_dir = base / "leg"
        new_dir = base / "new"
        _legacy_write_metrics(leg_dir, copy.deepcopy(metrics), None)
        write_metrics(new_dir, copy.deepcopy(metrics),
                      gate_claims=[record_gate("acc", 0.9, 0.8, ">=")])
        leg = json.loads((leg_dir / "metrics.json").read_text(encoding="utf-8"))
        new = json.loads((new_dir / "metrics.json").read_text(encoding="utf-8"))
        # Every legacy key is present and identical in the new output.
        for k, v in leg.items():
            _t(new.get(k) == v, f"E key {k!r} unchanged when gate_claims supplied")
        # The ONLY delta is the added key.
        _t(set(new.keys()) - set(leg.keys()) == {"structured_gate_claims"},
           "E only added key is structured_gate_claims")


def main() -> int:
    tests = [
        ("A backward-compat byte-identical", test_backward_compat_byte_identical),
        ("B round-trip", test_round_trip),
        ("C record_gate verdicts", test_record_gate_verdicts),
        ("D fail-fast validation", test_fail_fast_validation),
        ("E non-interference", test_non_interference),
    ]
    for label, fn in tests:
        print(f"\n=== {label} ===")
        fn()
    print("\n[selftest] ALL gate_claims TESTS PASS -- "
          "backward-compatible, round-trip exact, fail-fast validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
