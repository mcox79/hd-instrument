"""Smoke test for tools/verify_landing.py.

Constructs synthetic metrics.json files under a tmp exp_ dir and asserts that
verify_landing correctly discriminates:
    - selftest_ok (never ran FULL) -> FAIL
    - smoke HP -> FAIL when expect=full, OK when expect=smoke/any
    - full HP -> OK
    - RUNNING mid-flight -> FAIL
    - STARTED never advanced -> FAIL
    - IMPORT_CRASH -> FAIL
    - full HP with elapsed_s=0 -> OK non-strict, FAIL strict
    - missing metrics.json -> FAIL

Run:
    python tools/test_verify_landing.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Import verify_landing as a module (both files live in tools/)
THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
import verify_landing  # noqa: E402


def _write_metrics(data_dir: Path, anchor: str, payload: dict) -> Path:
    exp_dir = data_dir / f"exp_{anchor}"
    exp_dir.mkdir(parents=True, exist_ok=True)
    p = exp_dir / "metrics.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def _assert(cond: bool, msg: str):
    if not cond:
        raise AssertionError(msg)


def run_tests(tmp_root: Path):
    # Redirect verify_landing to look under tmp_root
    verify_landing.DATA = tmp_root

    tests = 0
    passed = 0

    # 1. FULL HP -> OK
    _write_metrics(tmp_root, "anchor_full_hp", {
        "run_mode": "full", "verdict": "HARD_PASS",
        "elapsed_s": 42.1, "cardinality_ok": True,
    })
    r = verify_landing.verify_one("anchor_full_hp", expected_mode="full")
    _assert(r["ok"], f"expected OK on full HP, got {r}")
    passed += 1; tests += 1

    # 2. SELFTEST_OK -> FAIL
    _write_metrics(tmp_root, "anchor_selftest", {
        "run_mode": "selftest", "verdict": "SELFTEST_OK",
        "elapsed_s": 1.2, "cardinality_ok": True,
    })
    r = verify_landing.verify_one("anchor_selftest", expected_mode="full")
    _assert(not r["ok"], f"expected FAIL on selftest, got {r}")
    _assert("run_mode" in r["reason"], f"expected run_mode reason, got {r['reason']}")
    passed += 1; tests += 1

    # 3. SMOKE HP -> FAIL when expect=full, OK when expect=smoke or any
    _write_metrics(tmp_root, "anchor_smoke_hp", {
        "run_mode": "smoke", "verdict": "HARD_PASS",
        "elapsed_s": 8.3, "cardinality_ok": True,
    })
    r = verify_landing.verify_one("anchor_smoke_hp", expected_mode="full")
    _assert(not r["ok"], f"expected FAIL on smoke when expect=full, got {r}")
    passed += 1; tests += 1

    r = verify_landing.verify_one("anchor_smoke_hp", expected_mode="smoke")
    _assert(r["ok"], f"expected OK on smoke when expect=smoke, got {r}")
    passed += 1; tests += 1

    r = verify_landing.verify_one("anchor_smoke_hp", expected_mode="any")
    _assert(r["ok"], f"expected OK on smoke when expect=any, got {r}")
    passed += 1; tests += 1

    # 4. RUNNING (mid-flight or crash-partial) -> FAIL
    _write_metrics(tmp_root, "anchor_running", {
        "run_mode": "full", "verdict": "RUNNING",
        "elapsed_s": 0, "cardinality_ok": None,
    })
    r = verify_landing.verify_one("anchor_running", expected_mode="full")
    _assert(not r["ok"], f"expected FAIL on RUNNING, got {r}")
    _assert("RUNNING" in r["reason"], f"expected RUNNING in reason, got {r['reason']}")
    passed += 1; tests += 1

    # 5. STARTED -> FAIL
    _write_metrics(tmp_root, "anchor_started", {
        "run_mode": "full", "verdict": "STARTED",
        "elapsed_s": 0, "cardinality_ok": None,
    })
    r = verify_landing.verify_one("anchor_started", expected_mode="full")
    _assert(not r["ok"], f"expected FAIL on STARTED, got {r}")
    passed += 1; tests += 1

    # 6. IMPORT_CRASH -> FAIL
    _write_metrics(tmp_root, "anchor_crash", {
        "run_mode": "full", "verdict": "IMPORT_CRASH",
        "elapsed_s": 0, "cardinality_ok": None,
    })
    r = verify_landing.verify_one("anchor_crash", expected_mode="full")
    _assert(not r["ok"], f"expected FAIL on IMPORT_CRASH, got {r}")
    passed += 1; tests += 1

    # 7. FULL HP with elapsed_s=0 -> OK non-strict, FAIL strict
    _write_metrics(tmp_root, "anchor_zero_elapsed", {
        "run_mode": "full", "verdict": "HARD_PASS",
        "elapsed_s": 0, "cardinality_ok": True,
    })
    r = verify_landing.verify_one("anchor_zero_elapsed", expected_mode="full")
    _assert(r["ok"], f"expected OK non-strict, got {r}")
    passed += 1; tests += 1

    r = verify_landing.verify_one("anchor_zero_elapsed", expected_mode="full", strict=True)
    _assert(not r["ok"], f"expected FAIL strict on elapsed=0, got {r}")
    _assert("elapsed_s" in r["reason"], f"expected elapsed_s in reason, got {r['reason']}")
    passed += 1; tests += 1

    # 8. FULL HP with cardinality_ok=False -> FAIL strict
    _write_metrics(tmp_root, "anchor_bad_card", {
        "run_mode": "full", "verdict": "HARD_PASS",
        "elapsed_s": 10.0, "cardinality_ok": False,
    })
    r = verify_landing.verify_one("anchor_bad_card", expected_mode="full", strict=True)
    _assert(not r["ok"], f"expected FAIL strict on bad cardinality, got {r}")
    _assert("cardinality_ok" in r["reason"], f"expected cardinality_ok in reason, got {r['reason']}")
    passed += 1; tests += 1

    # 9. Missing metrics.json -> FAIL
    r = verify_landing.verify_one("anchor_no_such_thing", expected_mode="full")
    _assert(not r["ok"], f"expected FAIL on missing, got {r}")
    _assert("metrics_path_missing" in r["reason"], f"expected missing reason, got {r['reason']}")
    passed += 1; tests += 1

    # 10. SH-4 double-prefix: exp_exp_<anchor> variant
    dbl_anchor = "anchor_double_prefix"
    dbl_dir = tmp_root / f"exp_exp_{dbl_anchor}"
    dbl_dir.mkdir(parents=True, exist_ok=True)
    (dbl_dir / "metrics.json").write_text(json.dumps({
        "run_mode": "full", "verdict": "HARD_PASS",
        "elapsed_s": 5.0, "cardinality_ok": True,
    }), encoding="utf-8")
    r = verify_landing.verify_one(dbl_anchor, expected_mode="full")
    _assert(r["ok"], f"expected OK on double-prefix variant, got {r}")
    passed += 1; tests += 1

    # 11. FAIL verdict (HARD_FAIL) -> still "OK" because it's a terminal verdict
    # (verify_landing is verify-CELL-RAN gate, NOT verify-CELL-PASSED gate)
    _write_metrics(tmp_root, "anchor_hard_fail", {
        "run_mode": "full", "verdict": "HARD_FAIL",
        "elapsed_s": 20.0, "cardinality_ok": True,
    })
    r = verify_landing.verify_one("anchor_hard_fail", expected_mode="full")
    _assert(r["ok"], f"expected OK on HARD_FAIL (terminal, run completed), got {r}")
    passed += 1; tests += 1

    # 12. Batch main() with mixed inputs: 1 OK + 1 FAIL -> exit 1
    rc = verify_landing.main(["anchor_full_hp", "anchor_selftest"])
    _assert(rc == 1, f"expected exit 1 on mixed, got {rc}")
    passed += 1; tests += 1

    # 13. Batch main() with all OK -> exit 0
    rc = verify_landing.main(["anchor_full_hp", "anchor_hard_fail"])
    _assert(rc == 0, f"expected exit 0 on all OK, got {rc}")
    passed += 1; tests += 1

    # 14. main() with no anchors -> exit 2
    rc = verify_landing.main([])
    _assert(rc == 2, f"expected exit 2 on no anchors, got {rc}")
    passed += 1; tests += 1

    print(f"\n[test_verify_landing] {passed}/{tests} tests passed")
    return passed == tests


def main() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="verify_landing_test_"))
    try:
        ok = run_tests(tmp_root)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
