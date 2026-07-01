"""Smoke test for runner_v2_prod.py wall-clock timeout enforcement (Bug 1 fix 2026-07-01).

Validates that:
  1. A hanging cell (sleeps for 60s) with timeout_s=10 is killed within
     10 + TIMEOUT_GRACE_S (60) + a few polls (~15s) — total ceiling ~90s.
  2. A fast-exit cell with timeout_s=30 completes normally (no premature kill).
  3. The runner emits a TIMEOUT-KILL log line + marks queue entry as 'failed'
     with error='timeout_killed_by_runner'.

Run:
    python tools/test_runner_timeout_enforcement.py

Exit codes: 0 = all passed; 1 = at least one failure.

Isolated: uses a temp queue dir, does NOT touch remote_cpu_queue or overnight_queue.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNNER = REPO / "experiments" / "runner_v2_prod.py"


HANG_CELL_SRC = '''
"""Test cell that hangs for 60s. Runner timeout=10 should kill within ~15s."""
import time, os, sys, json
name = os.environ.get("HDLAB_EXP_NAME", "hang_cell_test")
outdir = os.path.join("data", f"exp_{name}")
os.makedirs(outdir, exist_ok=True)
print(f"HANG_CELL START name={name}", flush=True)
sys.stdout.flush()
time.sleep(60)  # SHOULD BE KILLED before this returns
# If we get here the runner did NOT enforce the timeout — test fails
print("HANG_CELL SURVIVED THE FULL SLEEP (BAD)", flush=True)
open(os.path.join(outdir, "metrics.json"), "w").write(json.dumps({
    "verdict": "PASS", "verdict_msg": "should not reach here", "elapsed_s": 60,
}))
'''


FAST_CELL_SRC = '''
"""Test cell that exits quickly with valid metrics. Runner should mark completed.

Metrics must be > 100B to pass _validate_metrics_schema METRICS_MIN_BYTES gate.
"""
import os, json, time
name = os.environ.get("HDLAB_EXP_NAME", "fast_cell_test")
outdir = os.path.join("data", f"exp_{name}")
os.makedirs(outdir, exist_ok=True)
print(f"FAST_CELL START name={name}", flush=True)
time.sleep(2)
payload = {
    "verdict": "PASS",
    "verdict_msg": "fast cell exit ok - smoke test for runner_timeout_enforcement fix 2026-07-01",
    "elapsed_s": 2,
    "summary": {"N": 1024, "note": "test metrics padded to exceed 100-byte schema gate"},
}
open(os.path.join(outdir, "metrics.json"), "w").write(json.dumps(payload, indent=2))
print("FAST_CELL DONE", flush=True)
'''


def _write_cell_script(path: Path, src: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(src, encoding="utf-8")


def _write_queue_entry(queue_json: Path, name: str, script_rel: str, timeout_s: int) -> None:
    q = {"experiments": [{
        "name": name,
        "script": script_rel,
        "status": "pending",
        "purpose": "runner-timeout-enforcement smoke test",
        "timeout_s": timeout_s,
    }]}
    queue_json.write_text(json.dumps(q, indent=2), encoding="utf-8")


def _read_queue(queue_json: Path) -> dict:
    return json.loads(queue_json.read_text(encoding="utf-8"))


def _run_runner_until_done(queue_dir: Path, runner_id: str, timeout_wait_s: float) -> tuple[int, str]:
    """Spawn runner, wait until queue drained (all entries terminal) or timeout_wait_s.

    Returns (runner_exit_code, log_tail).
    """
    log_path = queue_dir / f"queue.{runner_id}.log"
    # idle-exit-minutes=0.1 = 6s so runner exits shortly after queue drained.
    # But 0.1 gets converted to int(0)=0 in the CLI — use 1 minute for safety;
    # we kill the runner ourselves after entry becomes terminal.
    cmd = [
        sys.executable, "-u", str(RUNNER),
        "--queue-dir", str(queue_dir),
        "--id", runner_id,
        "--idle-exit-minutes", "1",
    ]
    proc = subprocess.Popen(cmd, cwd=str(REPO), stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    t0 = time.time()
    try:
        while True:
            if proc.poll() is not None:
                out, _ = proc.communicate()
                return proc.returncode, (out or "")
            elapsed = time.time() - t0
            if elapsed > timeout_wait_s:
                # Test framework timeout; kill runner
                proc.kill()
                out, _ = proc.communicate()
                return -1, (out or "") + f"\n[TEST-FRAMEWORK-TIMEOUT after {elapsed:.1f}s]\n"
            # Check queue state
            try:
                q = _read_queue(queue_dir / "queue.json")
                all_terminal = all(
                    e.get("status") in ("completed", "failed", "skipped")
                    for e in q.get("experiments", [])
                )
                if all_terminal:
                    # Queue drained; give runner a beat then kill it (idle-exit is 60s)
                    time.sleep(2)
                    proc.terminate()
                    try:
                        out, _ = proc.communicate(timeout=10)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        out, _ = proc.communicate()
                    return proc.returncode, (out or "")
            except (OSError, json.JSONDecodeError):
                pass
            time.sleep(1)
    finally:
        if proc.poll() is None:
            proc.kill()


def test_hang_cell_killed_within_ceiling() -> bool:
    """A cell that sleeps 60s with timeout=10 should be killed by the runner."""
    print("\n=== TEST 1: hang cell with timeout=10 ===")
    with tempfile.TemporaryDirectory(prefix="runner_timeout_test_") as td:
        td_path = Path(td)
        queue_dir = td_path / "test_queue"
        queue_dir.mkdir()

        # Write cell script under experiments/ so the runner (REPO-anchored) finds it
        script_rel = "experiments/_test_hang_cell_delete_me.py"
        script_abs = REPO / script_rel
        _write_cell_script(script_abs, HANG_CELL_SRC)
        try:
            queue_json = queue_dir / "queue.json"
            _write_queue_entry(queue_json, "test_hang_cell", script_rel, timeout_s=10)

            # Ceiling: timeout(10) + grace(60) + poll_slack(15) + startup(5) = ~90s.
            # Framework waits 150s (2.5min) to give slack for a slow start.
            t0 = time.time()
            rc, out = _run_runner_until_done(queue_dir, "test_runner", timeout_wait_s=150)
            elapsed = time.time() - t0

            q = _read_queue(queue_json)
            entry = q["experiments"][0]
            status = entry.get("status")
            error = entry.get("error", "")
            wall_s = entry.get("wall_s", 0)

            print(f"  runner rc={rc}, elapsed={elapsed:.1f}s")
            print(f"  entry status={status!r}, error={error!r}, wall_s={wall_s}")
            # Check log for TIMEOUT-KILL line
            log_txt = out
            has_kill = "TIMEOUT-KILL" in log_txt
            has_timeout_msg = "SURVIVED THE FULL SLEEP" not in log_txt

            passed = (
                status == "failed"
                and "timeout" in error.lower()
                and wall_s < 90
                and has_kill
                and has_timeout_msg
            )
            if passed:
                print(f"  PASS: killed at wall_s={wall_s:.1f}s (< 90s ceiling)")
            else:
                print(f"  FAIL: status={status}, error={error}, wall_s={wall_s}, "
                      f"has_kill={has_kill}, cell_didnt_survive={has_timeout_msg}")
                print(f"  --- Runner log tail (last 2000 chars) ---")
                print(log_txt[-2000:])
            return passed
        finally:
            # Clean up test cell script
            try:
                script_abs.unlink()
            except OSError:
                pass
            # Clean up test cell output
            outdir = REPO / "data" / "exp_test_hang_cell"
            if outdir.exists():
                for f in outdir.iterdir():
                    try:
                        f.unlink()
                    except OSError:
                        pass
                try:
                    outdir.rmdir()
                except OSError:
                    pass


def test_fast_cell_completes_normally() -> bool:
    """A cell that exits in 2s should complete normally when timeout=30."""
    print("\n=== TEST 2: fast cell with timeout=30 ===")
    with tempfile.TemporaryDirectory(prefix="runner_timeout_test_") as td:
        td_path = Path(td)
        queue_dir = td_path / "test_queue"
        queue_dir.mkdir()

        script_rel = "experiments/_test_fast_cell_delete_me.py"
        script_abs = REPO / script_rel
        _write_cell_script(script_abs, FAST_CELL_SRC)
        try:
            queue_json = queue_dir / "queue.json"
            _write_queue_entry(queue_json, "test_fast_cell", script_rel, timeout_s=30)

            t0 = time.time()
            rc, out = _run_runner_until_done(queue_dir, "test_runner_2", timeout_wait_s=60)
            elapsed = time.time() - t0

            q = _read_queue(queue_json)
            entry = q["experiments"][0]
            status = entry.get("status")
            wall_s = entry.get("wall_s", 0)

            print(f"  runner rc={rc}, elapsed={elapsed:.1f}s")
            print(f"  entry status={status!r}, wall_s={wall_s}")

            passed = (status == "completed" and wall_s < 30)
            if passed:
                print(f"  PASS: cell completed at wall_s={wall_s:.1f}s (no premature kill)")
            else:
                print(f"  FAIL: expected status=completed, wall_s<30; got status={status}, wall_s={wall_s}")
                print(f"  --- Runner log tail (last 2000 chars) ---")
                print(out[-2000:])
            return passed
        finally:
            try:
                script_abs.unlink()
            except OSError:
                pass
            outdir = REPO / "data" / "exp_test_fast_cell"
            if outdir.exists():
                for f in outdir.iterdir():
                    try:
                        f.unlink()
                    except OSError:
                        pass
                try:
                    outdir.rmdir()
                except OSError:
                    pass


def main() -> int:
    print(f"Runner: {RUNNER}")
    print(f"Repo:   {REPO}")
    print(f"Python: {sys.executable}")

    if not RUNNER.exists():
        print(f"FATAL: runner not found at {RUNNER}")
        return 1

    results = []
    results.append(("hang_cell_killed", test_hang_cell_killed_within_ceiling()))
    results.append(("fast_cell_completes", test_fast_cell_completes_normally()))

    print("\n=== RESULTS ===")
    for name, ok in results:
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")

    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
