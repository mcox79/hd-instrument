"""Continuous Director-KB ingest (ANCHOR 3; v1).

Watches the configured source classes for file-mtime changes; when ANY watched
file changes (new note dropped, metrics landed, fleet_state updated, etc.) it
triggers a FULL re-ingest of the KB.

DESIGN CHOICE (load-bearing for no-lock-in):
  We do FULL RE-INGEST on every change, not incremental atom-merge. Reasons:
    - Preserves Principle 2 (wipe-and-rebuild safety) byte-equal guarantee
    - Preserves Principle 1 (filesystem is source-of-truth; the KB is a pure
      function of the filesystem)
    - Full ingest is ~15s on local_cpu at the current ~17k file corpus
      (ARM_INGEST_FULL elapsed_s=14.3 on the 2026-06-26 full run); well under
      the 60s latency budget
    - Incremental atom-merge would require atom-merge code that hand-rolls W
      matrix updates per-file (more lock-in, more bug surface, would break
      determinism guarantees of ANCHOR 1.5 ARM_REINGEST_DETERMINISTIC)

Discipline:
  - Single-writer: file lock prevents concurrent re-ingests
  - Backpressure: rapid changes coalesce (next ingest after current finishes
    picks up ALL changes since last scan tick)
  - Heartbeat: writes mtime + last-rebuild-ts to data/director_kb_continuous_state.json

Usage:
  python tools/director_kb_continuous_ingest.py            # default poll loop
  python tools/director_kb_continuous_ingest.py --once     # one scan + maybe-ingest
  python tools/director_kb_continuous_ingest.py --self-test
  python tools/director_kb_continuous_ingest.py --poll-sec 30 --quiet

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb import (  # noqa: E402
    SCHEMA_PATH_DEFAULT,
    build_ingest_plan,
    load_schema,
    run_ingest,
)


STATE_PATH = REPO / "data" / "director_kb_continuous_state.json"
LOCK_PATH = REPO / "data" / "director_kb_continuous.lock"
LOG_PATH = REPO / "data" / "director_kb_continuous.log"

# Reduced from 600s to 90s: a hung ingest blocks the loop entirely; after one full
# ingest cycle (~7min) + buffer (~1.5min headroom for slow disk) we consider any
# lock holder dead. Combined with PID-liveness check, this clears orphaned locks
# from crashed mid-ingest processes promptly (caught 2026-06-26: PID 25308 died
# mid-ingest 20:53, lock held until 21:03 = 10min KB-dark window).
STALE_LOCK_SEC = 90.0


def _scan_max_mtime(plan: dict) -> tuple[float, int]:
    """Return (max_mtime_ns, n_files_scanned) over all files in the plan."""
    max_mtime = 0.0
    n = 0
    for cname, cinfo in plan.items():
        for f in cinfo["files"]:
            try:
                st = f.stat()
                n += 1
                if st.st_mtime > max_mtime:
                    max_mtime = st.st_mtime
            except OSError:
                pass
    return max_mtime, n


def _pid_alive(pid: int) -> bool:
    """Cross-platform best-effort: is the process with this PID still running?

    On Windows, OpenProcess via ctypes; on POSIX, signal 0 to check. Returns True
    on uncertainty (fail-closed: don't steal a lock we're not sure is dead).
    """
    if pid <= 0:
        return False
    try:
        if sys.platform == "win32":
            import ctypes  # noqa: PLC0415
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            h = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if not h:
                # ERROR_INVALID_PARAMETER (87) typically means PID gone; treat as dead
                return False
            # Check if process has exited
            exit_code = ctypes.c_ulong(0)
            ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(exit_code))
            ctypes.windll.kernel32.CloseHandle(h)
            if not ok:
                return True  # uncertain -> fail-closed
            STILL_ACTIVE = 259
            return exit_code.value == STILL_ACTIVE
        else:
            os.kill(pid, 0)
            return True
    except (OSError, PermissionError, ProcessLookupError):
        # On POSIX: PermissionError means proc exists but we can't signal it
        # On Windows: handled above
        return False
    except Exception:  # noqa: BLE001
        return True  # uncertain -> fail-closed


def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {
        "last_scan_max_mtime": 0.0,
        "last_ingest_ts": 0.0,
        "last_ingest_n_triples": 0,
        "last_ingest_elapsed_s": 0.0,
        "n_ingests": 0,
        "last_ingest_trigger": None,
    }


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def _acquire_lock(timeout_s: float = 60.0) -> bool:
    """Best-effort cross-process lock via O_EXCL file create. Returns False if
    another process holds the lock. Caller MUST release.

    Stale-lock policy: a lock is stale if EITHER (a) the holder PID is no longer
    running, OR (b) age > STALE_LOCK_SEC. PID-liveness is the primary check; the
    age fallback handles crashes that left no PID trace (raw-process-kill, OOM-
    reaper). Fixed 2026-06-26 after PID 25308 crashed mid-ingest leaving a 10-
    minute KB-dark window with the old 600s pure-age policy.
    """
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    while True:
        try:
            fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii"))
            os.close(fd)
            return True
        except FileExistsError:
            # Check if lock is stale (PID dead OR age > STALE_LOCK_SEC)
            try:
                content = LOCK_PATH.read_text(encoding="ascii", errors="replace").strip()
                holder_pid = int(content) if content.isdigit() else -1
                age = time.time() - LOCK_PATH.stat().st_mtime
                stale_reason = None
                if holder_pid > 0 and not _pid_alive(holder_pid):
                    stale_reason = f"holder_pid_{holder_pid}_dead"
                elif age > STALE_LOCK_SEC:
                    stale_reason = f"age_{age:.0f}s_exceeds_{STALE_LOCK_SEC}s"
                if stale_reason:
                    print(f"[continuous-ingest] clearing stale lock: {stale_reason}",
                          flush=True, file=sys.stderr)
                    LOCK_PATH.unlink(missing_ok=True)
                    continue
            except (OSError, ValueError):
                pass
            if time.time() - t0 > timeout_s:
                return False
            time.sleep(0.5)


def _release_lock() -> None:
    try:
        LOCK_PATH.unlink(missing_ok=True)
    except OSError:
        pass


def _atomic_swap_kb(staging: Path, final: Path) -> None:
    """Replace `final` with `staging` atomically (best-effort on Windows).

    Strategy:
      1. If `final` exists, rename it to `final.old.<pid>` (atomic on same-FS)
      2. Rename `staging` -> `final` (atomic)
      3. Delete the `.old` backup
    On step-2 failure, restore from step-1 backup.
    """
    final = Path(final)
    staging = Path(staging)
    backup = final.with_suffix(final.suffix + f".old.{os.getpid()}")
    if final.exists():
        if backup.exists():
            # Clean up any leftover backup from a prior crash
            import shutil as _sh
            _sh.rmtree(backup, ignore_errors=True)
        os.rename(str(final), str(backup))
    try:
        os.rename(str(staging), str(final))
    except OSError:
        # Roll back the backup
        if backup.exists() and not final.exists():
            os.rename(str(backup), str(final))
        raise
    # Success: clean up backup
    if backup.exists():
        import shutil as _sh
        _sh.rmtree(backup, ignore_errors=True)


def _do_ingest(schema: dict, trigger: str, quiet: bool = False) -> dict:
    kb_ver = schema.get("kb_version", "v1")
    kb_path = schema.get("kb_path", f"data/substrate_director_kb_{kb_ver}")
    out_dir = REPO / kb_path
    # Atomic swap: write to .staging.<pid> dir, then rename. Prevents the prior
    # bug (caught 2026-06-26 with PID 25308 mid-ingest crash) where wipe-then-
    # rebuild on the live KB dir destroyed it irrecoverably on crash, leaving
    # ALL queries failing for the full duration of next-ingest-success.
    staging_dir = out_dir.parent / f"{out_dir.name}.staging.{os.getpid()}"
    # If a prior crashed run left a staging dir, clean it
    if staging_dir.exists():
        import shutil
        shutil.rmtree(staging_dir, ignore_errors=True)

    plan = build_ingest_plan(schema=schema, repo_root=REPO, max_files_per_class=None,
                              only_classes=None)
    if not quiet:
        print(f"[continuous-ingest] running FULL re-ingest trigger={trigger} "
              f"out={out_dir} staging={staging_dir.name}", flush=True)
    t0 = time.perf_counter()
    # Ingest into staging dir (wipe=True is now safe: staging is fresh)
    manifest = run_ingest(
        plan=plan, out_dir=staging_dir, schema=schema,
        n_dim=2048, seed=17, wipe=True, redact_timestamps_in_atoms=False,
    )
    # Atomic swap into place: if we crash AFTER ingest but BEFORE this, the
    # current KB on disk remains intact and queryable.
    _atomic_swap_kb(staging_dir, out_dir)
    elapsed = time.perf_counter() - t0
    if not quiet:
        print(f"[continuous-ingest] DONE elapsed={elapsed:.2f}s n_triples={manifest['n_triples']} "
              f"n_ent={manifest['n_entities']}", flush=True)
    return {
        "elapsed_s": elapsed, "manifest": manifest,
        "trigger": trigger, "ingest_ts": time.time(),
    }


def _verify_kb_coverage(schema: dict, manifest: dict, plan: dict) -> dict:
    """Regression guard: assert per-class discovered file count in KB equals
    file count on disk. Catches future scanner-resolution regressions where the
    external memory dir (or any other source class) silently drops files.

    Returns {"ok": bool, "violations": [{"class": ..., "on_disk": N, "in_manifest": M}]}.
    """
    violations = []
    manifest_per_class = manifest.get("per_class", {})
    for cname, cinfo in plan.items():
        on_disk = len(cinfo["files"])
        m_entry = manifest_per_class.get(cname, {})
        in_manifest = int(m_entry.get("n_discovered", -1))
        if in_manifest != on_disk:
            violations.append({
                "class": cname,
                "on_disk": on_disk,
                "in_manifest": in_manifest,
            })
    return {"ok": len(violations) == 0, "violations": violations}


def scan_once(schema: dict, force: bool = False, quiet: bool = False) -> dict:
    """One pass: check if anything changed since last ingest; if so, re-ingest.

    Returns event dict: {"changed": bool, "ingested": bool, "elapsed_s": ...}
    """
    plan = build_ingest_plan(schema=schema, repo_root=REPO, max_files_per_class=None,
                              only_classes=None)
    cur_max_mtime, n_files = _scan_max_mtime(plan)
    state = _load_state()
    prev = float(state.get("last_scan_max_mtime", 0.0))
    changed = cur_max_mtime > prev or force
    event = {"changed": changed, "ingested": False,
             "cur_max_mtime": cur_max_mtime, "prev_max_mtime": prev,
             "n_files_scanned": n_files}
    if not changed:
        return event

    # Acquire lock; if another ingest is in flight, skip (it will pick up our changes)
    if not _acquire_lock(timeout_s=2.0):
        event["skipped_locked"] = True
        return event
    try:
        try:
            result = _do_ingest(schema, trigger="mtime_changed", quiet=quiet)
        except Exception as e:  # noqa: BLE001
            # Record the failure in state so we don't blindly skip on next scan
            # (last_scan_max_mtime stays at prev value -> next scan retries).
            state["last_failed_ingest_ts"] = time.time()
            state["last_failed_ingest_error"] = f"{type(e).__name__}: {str(e)[:500]}"
            state["n_failed_ingests"] = int(state.get("n_failed_ingests", 0)) + 1
            _save_state(state)
            event["ingest_failed"] = True
            event["ingest_error"] = f"{type(e).__name__}: {str(e)[:300]}"
            return event
        # Regression guard: verify per-class file counts match
        coverage_check = _verify_kb_coverage(schema, result["manifest"], plan)
        if not coverage_check["ok"]:
            msg = f"coverage_violation: {coverage_check['violations']}"
            print(f"[continuous-ingest] WARN {msg}", flush=True, file=sys.stderr)
            event["coverage_violations"] = coverage_check["violations"]
        state["last_scan_max_mtime"] = cur_max_mtime
        state["last_ingest_ts"] = result["ingest_ts"]
        state["last_ingest_n_triples"] = result["manifest"]["n_triples"]
        state["last_ingest_elapsed_s"] = result["elapsed_s"]
        state["n_ingests"] = int(state.get("n_ingests", 0)) + 1
        state["last_ingest_trigger"] = result["trigger"]
        state["last_ingest_per_class_n_discovered"] = {
            c: int(result["manifest"].get("per_class", {}).get(c, {}).get("n_discovered", 0))
            for c in plan.keys()
        }
        state["last_coverage_check_ok"] = coverage_check["ok"]
        _save_state(state)
        event["ingested"] = True
        event["elapsed_s"] = result["elapsed_s"]
        event["n_triples"] = result["manifest"]["n_triples"]
        event["coverage_ok"] = coverage_check["ok"]
    finally:
        _release_lock()
    return event


def loop(schema: dict, poll_sec: float, quiet: bool) -> None:
    if not quiet:
        print(f"[continuous-ingest] starting poll loop poll_sec={poll_sec}", flush=True)
    while True:
        try:
            evt = scan_once(schema, force=False, quiet=quiet)
            if evt["ingested"]:
                print(f"[continuous-ingest] reingested n_triples={evt.get('n_triples')} "
                      f"elapsed={evt.get('elapsed_s', 0):.2f}s",
                      flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[continuous-ingest] scan error: {type(e).__name__}: {e}",
                  flush=True, file=sys.stderr)
        time.sleep(poll_sec)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--schema", default=SCHEMA_PATH_DEFAULT)
    ap.add_argument("--poll-sec", type=float, default=20.0,
                    help="Seconds between scans in loop mode (default 20)")
    ap.add_argument("--once", action="store_true",
                    help="Do one scan + maybe-ingest, then exit")
    ap.add_argument("--force", action="store_true",
                    help="Force re-ingest regardless of mtime check")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args()

    if args.self_test:
        # Verify schema + lock acquire/release
        schema = load_schema(REPO, args.schema)
        assert "source_classes" in schema
        plan = build_ingest_plan(schema=schema, repo_root=REPO,
                                  max_files_per_class=1, only_classes=["note"])
        assert "note" in plan
        ok = _acquire_lock(timeout_s=1.0)
        assert ok, "lock acquire failed"
        _release_lock()
        # Verify state load/save round-trip
        st = _load_state()
        _save_state(st)
        print("[selftest] director_kb_continuous_ingest PASS", flush=True)
        return 0

    schema = load_schema(REPO, args.schema)
    if args.once or args.force:
        evt = scan_once(schema, force=args.force, quiet=args.quiet)
        print(json.dumps(evt, indent=2, sort_keys=True, default=str))
        return 0

    loop(schema, poll_sec=args.poll_sec, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
