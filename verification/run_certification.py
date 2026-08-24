"""Run the full verification suite and produce a markdown certification report.

Usage: python verification/run_certification.py [--output data/certification.md]
                                                 [--target verification]
                                                 [--timeout-s N] [--heartbeat-s N]

BOUNDED + LOUD + OBSERVABLE (2026-08-24, problem `certification_gate_hangs`).
------------------------------------------------------------------------------
This gate used to shell `pytest verification/` with NO timeout and NO live progress:

    result = subprocess.run([... "pytest", "verification/", ...])   # blocks forever

When the suite grew (527 tests; ~112s just to COLLECT) and a SECOND session ran heavy
disk-bound work at the same time (the 2026-08-22 stall happened "during a cell re-land"),
pytest's own startup -- importing the pytest package and enumerating every installed
distribution's entry-point metadata to decide what to assertion-rewrite -- became
disk-I/O-starved. faulthandler stacks taken during the stall show it BLOCKED IN FILE READS
(`importlib._bootstrap_external.get_data`, `importlib.metadata.entry_points -> read_text`)
and ADVANCING between dumps: slow, not deadlocked. But the parent's CPU stays flat while it
waits on I/O -- this repo's documented "parent CPU is flat" false alarm -- so a healthy-slow
run is indistinguishable from a hang and gets killed by hand. A gate that can be quietly
killed is a gate that can be quietly skipped.

THE FIX does not narrow what runs. It bounds and instruments it:
  * a wall-clock BUDGET (env CERT_TIMEOUT_S, default 2700s; --timeout-s overrides);
  * on expiry the whole pytest PROCESS TREE is killed (pytest spawns witness subprocesses;
    killing only the direct child leaves them resident on Windows);
  * a FOURTH verdict, "DID NOT RUN -- TIMED OUT", that NAMES what it was waiting on: whether
    collection had finished, which test was in flight, and the top of the last faulthandler
    stack (import / test / lock);
  * a live progress sidecar + periodic stack dumps under data/certification_run/, so an
    operator watching a slow run sees it is alive rather than assuming a hang.

Tune the budget from a measured clean wall-clock. Under heavy concurrent disk load the gate
will TIME OUT loudly (with the blocking stack) rather than hang -- which is the correct
outcome: "cannot certify right now, here is exactly where it was stuck."
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The child wrapper. Runs pytest via pytest.main(plugins=[...]) -- an in-process plugin
# instance, so there is NO plugin-by-name import and NO PYTHONPATH juggling. faulthandler is
# armed BEFORE pytest.main so a stall anywhere (startup, collection, a test, a lock) dumps every
# thread's stack to the stacks file on a repeating timer. The progress plugin writes one fsync'd
# json line per test start/end plus a collection-finished marker, so the parent can tell
# "stuck in startup" from "stuck in test X" even when pytest's own stdout is buffered.
_CHILD_SRC = r'''
import faulthandler, json, os, sys, time

_TARGET, _PROG, _STACKS, _HB = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
_sf = open(_STACKS, "w", encoding="utf-8", buffering=1)
faulthandler.enable(_sf)
faulthandler.dump_traceback_later(_HB, repeat=True, file=_sf)
_T0 = time.time()

def _emit(rec):
    rec["wall"] = round(time.time() - _T0, 3)
    with open(_PROG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass

class _Progress:
    def pytest_collection_finish(self, session):
        _emit({"phase": "collected", "n": len(session.items)})
    def pytest_runtest_logstart(self, nodeid, location):
        _emit({"phase": "start", "nodeid": nodeid})
    def pytest_runtest_logreport(self, report):
        if report.when == "call" or (report.when in ("setup", "teardown") and report.outcome == "failed"):
            _emit({"phase": "end", "nodeid": report.nodeid, "when": report.when,
                   "outcome": report.outcome, "duration": round(report.duration, 3)})
    def pytest_sessionfinish(self, session, exitstatus):
        _emit({"phase": "session_finish", "exitstatus": int(exitstatus)})

import pytest
_rc = pytest.main([_TARGET, "-v", "--tb=short"], plugins=[_Progress()])
_emit({"phase": "main_return", "rc": int(_rc)})
raise SystemExit(int(_rc))
'''


def _kill_tree(pid: int) -> None:
    """Kill the process and every descendant (witness subprocesses included)."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, text=True)
    else:  # pragma: no cover - repo is Windows
        import signal
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except OSError:
            pass


def _read_progress(path: Path):
    """(collected_n_or_None, in_flight_nodeids, session_exitstatus, main_rc)."""
    collected = None
    started, ended = [], set()
    session_exit = main_rc = None
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rec = __import__("json").loads(line)
            except ValueError:
                continue
            ph = rec.get("phase")
            if ph == "collected":
                collected = rec.get("n")
            elif ph == "start":
                started.append(rec["nodeid"])
            elif ph == "end":
                ended.add(rec["nodeid"])
            elif ph == "session_finish":
                session_exit = rec.get("exitstatus")
            elif ph == "main_return":
                main_rc = rec.get("rc")
    in_flight = [n for n in started if n not in ended]
    return collected, in_flight, session_exit, main_rc


def _last_stack(stacks_path: Path, max_lines: int = 16) -> str:
    """The most recent faulthandler thread dump -- 'what it was waiting on', verbatim."""
    if not stacks_path.exists():
        return "(no stack captured)"
    text = stacks_path.read_text(encoding="utf-8", errors="replace")
    blocks = [b for b in text.split("Timeout (") if "Thread 0x" in b]
    if not blocks:
        return "(no stack captured)"
    lines = ("Timeout (" + blocks[-1]).splitlines()
    return "\n".join(lines[:max_lines])


def _verdict(out: str, returncode: int) -> tuple[str, str]:
    """(verdict, detail) from pytest's own summary -- never from a test's printed text.

      PASS          tests ran and all passed
      FAIL          tests ran and some failed
      DID_NOT_RUN   the session aborted (collection error / INTERNALERROR) -- the failure mode
                    that hid for two days, because a report saying "0 failed" reads like success
    """
    def n(pat: str) -> int:
        m = re.search(pat, out)
        return int(m.group(1)) if m else 0

    passed, failed, errors = n(r"(\d+) passed"), n(r"(\d+) failed"), n(r"(\d+) error")
    collected = n(r"(\d+) tests? collected")
    aborted = ("INTERNALERROR" in out) or ("Interrupted:" in out)

    if aborted or (collected and passed == 0 and failed == 0):
        return ("DID NOT RUN -- THE SESSION ABORTED",
                f"**{collected} tests were collected and {passed + failed} ran.** "
                f"{'An INTERNALERROR or collection error aborted the session. ' if aborted else ''}"
                f"**This is NOT a pass.** Nothing below may be read as evidence, including any "
                f"`RESULT: PASS` line printed by a test at import time.")
    if failed or errors or returncode != 0:
        return ("FAIL", f"**{passed} passed, {failed} failed, {errors} errors** (exit {returncode}).")
    return ("PASS", f"**{passed} passed, 0 failed** (exit {returncode}), {collected} collected.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/certification.md"))
    parser.add_argument("--target", default="verification",
                        help="pytest target (default: the whole verification suite)")
    parser.add_argument("--timeout-s", type=int,
                        default=int(os.environ.get("CERT_TIMEOUT_S", "2700")),
                        help="wall-clock budget; on expiry the gate FAILS LOUD, it does not wait")
    parser.add_argument("--heartbeat-s", type=int, default=30,
                        help="faulthandler stack-dump interval while running")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    run_dir = args.output.parent / "certification_run"
    run_dir.mkdir(parents=True, exist_ok=True)
    child_path = run_dir / "_cert_child.py"
    progress_path = run_dir / "progress.jsonl"
    stacks_path = run_dir / "stacks.txt"
    log_path = run_dir / "pytest_output.log"
    child_path.write_text(_CHILD_SRC, encoding="utf-8")
    progress_path.write_text("", encoding="utf-8")
    stacks_path.write_text("", encoding="utf-8")

    cmd = [sys.executable, "-u", str(child_path), args.target,
           str(progress_path), str(stacks_path), str(args.heartbeat_s)]
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0

    t0 = time.time()
    log_fh = open(log_path, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(cmd, cwd=str(ROOT), stdout=log_fh, stderr=subprocess.STDOUT,
                            creationflags=creationflags,
                            start_new_session=(os.name != "nt"))
    timed_out = False
    while True:
        if proc.poll() is not None:
            break
        if time.time() - t0 > args.timeout_s:
            timed_out = True
            _kill_tree(proc.pid)
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                pass
            break
        time.sleep(1.0)
    log_fh.close()
    elapsed = time.time() - t0

    out = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    collected, in_flight, _session_exit, main_rc = _read_progress(progress_path)

    if timed_out:
        verdict = "DID NOT RUN -- TIMED OUT"
        if collected is None:
            where = ("It never finished STARTUP/COLLECTION -- no test had started. Under a "
                     "second disk-heavy session this is pytest itself blocked on file reads "
                     "(import + entry-point metadata), not a test.")
        elif in_flight:
            where = (f"Collection finished ({collected} tests). IN FLIGHT when the budget "
                     f"expired: {', '.join(in_flight[:5])}.")
        else:
            where = (f"Collection finished ({collected} tests) but no test was recorded in "
                     f"flight -- likely between tests or in teardown.")
        detail = (f"**The gate exceeded its {args.timeout_s}s budget after {elapsed:.0f}s and was "
                  f"killed.** {where} **This is NOT a pass and NOT a hang -- it is a bounded, loud "
                  f"stop with the blocking stack below.** Raise --timeout-s (or CERT_TIMEOUT_S) if "
                  f"the suite is legitimately this slow, or run it when no other session is "
                  f"saturating the disk.")
        returncode = 124
    else:
        returncode = proc.returncode if proc.returncode is not None else 1
        verdict, detail = _verdict(out, returncode)

    # The blocking stack is meaningful only when the run was killed mid-flight. On a clean
    # PASS/FAIL the periodic faulthandler dump just shows whatever test happened to be running
    # at the last heartbeat, which reads as alarming noise -- so show it only on a timeout.
    if timed_out:
        stack_section = (
            "## last faulthandler stack (what it was waiting on)\n\n"
            "(A `Windows fatal exception: access violation` line below is a known faulthandler "
            "stack-walk artifact when a dump races a `stat`/`open` under heavy load -- not a "
            "crash; the run kept going until the budget killed it.)\n\n"
            "```\n" + _last_stack(stacks_path) + "\n```\n\n"
        )
    else:
        stack_section = ""

    timestamp = datetime.now().isoformat(timespec="seconds")

    # THE VERDICT BLOCK GOES FIRST, AND IT IS NOT OPTIONAL (2026-08-22). A report whose first
    # line can be produced by a test's stray print is not a report. The wall-clock and budget sit
    # in the verdict block too, so "it is merely slow" can never again be mistaken for "it hangs".
    body = (
        "# hd-instrument certification report\n\n"
        f"## VERDICT: {verdict}\n\n"
        f"{detail}\n\n"
        f"Wall-clock: {elapsed:.1f}s (budget {args.timeout_s}s). "
        f"Collected: {collected if collected is not None else 'n/a'}.\n\n"
        f"Generated: {timestamp}\n"
        f"Exit code: {returncode}\n\n"
        f"{stack_section}"
        "## pytest output\n\n"
        "```\n"
        f"{out}\n"
        "```\n"
    )
    args.output.write_text(body, encoding="utf-8")

    print(f"VERDICT: {verdict}")
    print(re.sub(r"\*\*", "", detail))
    print(f"Wall-clock: {elapsed:.1f}s (budget {args.timeout_s}s); collected "
          f"{collected if collected is not None else 'n/a'}")
    print(f"Wrote {args.output}")
    return returncode


if __name__ == "__main__":
    sys.exit(main())
