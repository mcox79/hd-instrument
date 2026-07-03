"""Smoke test: SH-4 double-prefix fallback in verify tools.

Testbed 2026-07-03 fleet audit. Recurring Fix#28 pattern: verify tools miss
landings when runner writes to `data/exp_exp_<anchor>/` instead of
`data/exp_<anchor>/`. This test drives each patched read-path through a synthetic
double-prefix fixture and asserts the fallback fires.

Covers:
    - tools/verify_landing.py (already tested in test_verify_landing.py; smoke
      here for parity)
    - tools/runner_status.read_cell_heartbeat
    - tools/healer.metrics_exists_with_content
    - tools/orchestrator/purge_pending_reruns (dry-run through subprocess)
    - tools/orchestrator/remote_state.get_local_metrics

Does NOT drive the SSH-based tools (poller.fetch_exp_metrics, scp_recover,
remote_state remote path) because those require a live remote; the SH-4 code
paths there are simple sequential-fallback and code-reviewable.

Run:
    python tools/test_sh4_double_prefix_fallback.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO = THIS_DIR.parent
sys.path.insert(0, str(THIS_DIR))
sys.path.insert(0, str(REPO))


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _write_metrics(root: Path, dir_name: str, payload: dict) -> Path:
    d = root / dir_name
    d.mkdir(parents=True, exist_ok=True)
    p = d / "metrics.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def _write_heartbeat(root: Path, dir_name: str, payload: dict) -> Path:
    d = root / dir_name
    d.mkdir(parents=True, exist_ok=True)
    p = d / "_heartbeat.jsonl"
    p.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return p


def test_verify_landing_double_prefix(tmp_root: Path) -> tuple[int, int]:
    import verify_landing
    verify_landing.DATA = tmp_root
    # Fixture: metrics under data/exp_exp_<anchor>/
    _write_metrics(tmp_root, "exp_exp_sh4_probe_v1", {
        "run_mode": "full", "verdict": "HARD_PASS",
        "elapsed_s": 5.0, "cardinality_ok": True,
    })
    r = verify_landing.verify_one("sh4_probe_v1", expected_mode="full")
    _assert(r["ok"], f"verify_landing SH-4 fallback FAIL: {r}")
    return 1, 1


def test_runner_status_cell_heartbeat_double_prefix(tmp_root: Path) -> tuple[int, int]:
    import runner_status
    runner_status.REPO = tmp_root.parent  # monkey-patch base
    # runner_status uses REPO / "data" / ... — build that layout
    data = tmp_root  # tmp_root IS the "data" dir for this test
    runner_status.REPO = data.parent
    # actually simpler: create data/exp_exp_<anchor>/_heartbeat.jsonl under a
    # fake REPO structure
    fake_repo = Path(tempfile.mkdtemp(prefix="rs_sh4_"))
    try:
        (fake_repo / "data").mkdir()
        _write_heartbeat(fake_repo / "data", "exp_exp_sh4_hb_probe_v1", {
            "ts_iso": "2026-07-03T20:00:00Z", "unit_idx": 3, "total_units": 5,
        })
        runner_status.REPO = fake_repo
        row = runner_status.read_cell_heartbeat("sh4_hb_probe_v1")
        _assert(row is not None, "read_cell_heartbeat SH-4 fallback returned None")
        _assert(row.get("unit_idx") == 3, f"payload mismatch: {row}")
    finally:
        shutil.rmtree(fake_repo, ignore_errors=True)
    return 1, 1


def test_healer_metrics_exists_double_prefix() -> tuple[int, int]:
    import healer
    fake_repo = Path(tempfile.mkdtemp(prefix="healer_sh4_"))
    try:
        (fake_repo / "data").mkdir()
        _write_metrics(fake_repo / "data", "exp_exp_sh4_healer_probe_v1", {
            "run_mode": "full", "verdict": "HARD_PASS",
            "elapsed_s": 5.0, "cardinality_ok": True,
            # padding to exceed 100-byte threshold
            "padding": "x" * 200,
        })
        healer.REPO = fake_repo
        ok = healer.metrics_exists_with_content("sh4_healer_probe_v1")
        _assert(ok, "healer.metrics_exists_with_content SH-4 fallback returned False")
        ok2 = healer.metrics_exists_with_content("no_such_anchor_zzz")
        _assert(not ok2, "healer.metrics_exists_with_content false-positive on missing")
    finally:
        shutil.rmtree(fake_repo, ignore_errors=True)
    return 1, 1


def test_purge_pending_reruns_double_prefix() -> tuple[int, int]:
    """Drive purge_pending_reruns via subprocess; assert double-prefix dir
    triggers a DROP for a pending re-run."""
    fake_repo = Path(tempfile.mkdtemp(prefix="purge_sh4_"))
    try:
        data = fake_repo / "data"
        (data / "sh4_queue").mkdir(parents=True)
        _write_metrics(data, "exp_exp_sh4_purge_probe_v1", {
            "run_mode": "full", "verdict": "HARD_PASS",
            "elapsed_s": 5.0, "cardinality_ok": True,
        })
        queue = {"experiments": [
            {"name": "sh4_purge_probe_v1", "status": "pending"},
            {"name": "genuinely_new_zzz_v1", "status": "pending"},
        ]}
        qpath = data / "sh4_queue" / "queue.json"
        qpath.write_text(json.dumps(queue, indent=2), encoding="utf-8")
        script = REPO / "tools" / "orchestrator" / "purge_pending_reruns.py"
        proc = subprocess.run(
            [sys.executable, str(script), str(qpath)],
            capture_output=True, text=True, timeout=30,
        )
        _assert("sh4_purge_probe_v1" in proc.stdout,
                f"purge dry-run did NOT flag SH-4 double-prefix: {proc.stdout}")
        _assert("genuinely_new_zzz_v1" not in proc.stdout,
                f"purge dry-run flagged a genuine-new entry: {proc.stdout}")
    finally:
        shutil.rmtree(fake_repo, ignore_errors=True)
    return 1, 1


def test_remote_state_local_double_prefix() -> tuple[int, int]:
    from orchestrator import remote_state
    fake_repo = Path(tempfile.mkdtemp(prefix="remote_state_sh4_"))
    try:
        (fake_repo / "data").mkdir()
        _write_metrics(fake_repo / "data", "exp_exp_sh4_rs_probe_v1", {
            "run_mode": "full", "verdict": "HARD_PASS",
            "elapsed_s": 5.0, "cardinality_ok": True,
        })
        remote_state._REPO = fake_repo
        doc = remote_state.get_local_metrics("sh4_rs_probe_v1")
        _assert(doc is not None, "remote_state.get_local_metrics SH-4 fallback returned None")
        _assert(doc.get("verdict") == "HARD_PASS", f"payload mismatch: {doc}")
    finally:
        shutil.rmtree(fake_repo, ignore_errors=True)
    return 1, 1


def main() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="sh4_fallback_"))
    total_pass = 0
    total_tests = 0
    cases = [
        ("verify_landing", lambda: test_verify_landing_double_prefix(tmp_root)),
        ("runner_status", lambda: test_runner_status_cell_heartbeat_double_prefix(tmp_root)),
        ("healer", test_healer_metrics_exists_double_prefix),
        ("purge_pending_reruns", test_purge_pending_reruns_double_prefix),
        ("remote_state", test_remote_state_local_double_prefix),
    ]
    try:
        for name, fn in cases:
            try:
                p, t = fn()
                total_pass += p
                total_tests += t
                print(f"  [OK]   {name}: {p}/{t}")
            except AssertionError as e:
                total_tests += 1
                print(f"  [FAIL] {name}: {e}")
            except Exception as e:
                total_tests += 1
                print(f"  [FAIL] {name}: unexpected exception {type(e).__name__}: {e}")
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    print(f"\n[test_sh4_double_prefix_fallback] {total_pass}/{total_tests} tests passed")
    return 0 if total_pass == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
