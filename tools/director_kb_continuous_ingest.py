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

# Age fallback ONLY applies when the lock file has no parseable holder PID (a
# crash that left no PID trace). When a PID is present, _pid_alive is
# authoritative and a LIVE holder is NEVER stolen from -- see _acquire_lock.
# Bumped 90s -> 1800s (testbed 2026-07-08): the post-UNIFIED-KB full ingest now
# takes ~21min (state last_ingest_elapsed_s=1268), so the old 90s age threshold
# stole the lock from a LIVE 21-min ingest, spawning a concurrent second ingest.
# Two ~9GB E-codebook builds = ~18GB peak on a 32GB box -> OOM kill -> empty
# staging dir + dead PID leftovers with no logged exception: the exact
# stuck-since-2026-07-02 signature. 1800s is a safe belt for the no-PID case.
STALE_LOCK_SEC = 1800.0


# Windows transient resource-exhaustion error codes. Under heavy multi-agent
# I/O contention a scandir of a cluttered dir (data/ holds 842 gate_log_*.txt
# scratch files as of 2026-07-26) can raise these; they are TRANSIENT -- a
# gc + backoff + retry on a calmer pass succeeds. This is what turned a
# recoverable blip into 4 recorded permanent ingest failures + an 18-day-stale
# index.
#   1450 = ERROR_NO_SYSTEM_RESOURCES ("Insufficient system resources ...")
#   1455 = ERROR_COMMITMENT_LIMIT ("The paging file is too small ...")
#      8 = ERROR_NOT_ENOUGH_MEMORY
_TRANSIENT_WINERRORS = frozenset({8, 1450, 1455})
_INGEST_RETRY_BACKOFFS_SEC = (30.0, 60.0)  # 1 initial try + len() retries


def _is_transient_resource_error(exc: BaseException) -> bool:
    """True if `exc` is a transient Windows resource-exhaustion error worth a
    backoff + retry rather than recording a permanent ingest failure."""
    winerr = getattr(exc, "winerror", None)
    if winerr in _TRANSIENT_WINERRORS:
        return True
    msg = str(exc).lower()
    return (
        "insufficient system resources" in msg
        or "not enough memory" in msg
        or "winerror 1450" in msg
        or "winerror 1455" in msg
        or "paging file is too small" in msg
    )


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
                # CRITICAL (testbed 2026-07-08): OpenProcess returning NULL does
                # NOT always mean the PID is gone. ERROR_ACCESS_DENIED (5) means
                # the process EXISTS but is owned by another security context
                # (e.g. a Task-Scheduler pythonw cannot open a handle to a
                # bash-launched python in a different session/token). The old
                # `return False` here conflated access-denied with dead-PID, so a
                # scheduled --once tick declared a LIVE 21-min ingest dead, STOLE
                # its lock, and launched a concurrent ingest -> ~28GB combined ->
                # OOM/thrash. Distinguish via GetLastError: only ERROR_INVALID_
                # PARAMETER (87) / ERROR_NOT_FOUND means gone.
                err = ctypes.windll.kernel32.GetLastError()
                ERROR_ACCESS_DENIED = 5
                if err == ERROR_ACCESS_DENIED:
                    return True  # exists but cross-context -> alive
                # 87 (invalid param) / other -> treat as gone
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
                if holder_pid > 0:
                    # PID-liveness is authoritative. A LIVE holder is NEVER
                    # stale, no matter how long its ingest runs (~21min full
                    # ingest). Only a DEAD holder frees the lock. The age
                    # fallback is deliberately NOT applied here -- applying it
                    # stole the lock from live long ingests and caused
                    # concurrent-ingest OOM (testbed 2026-07-08).
                    if not _pid_alive(holder_pid):
                        stale_reason = f"holder_pid_{holder_pid}_dead"
                elif age > STALE_LOCK_SEC:
                    # No parseable holder PID (crash left no trace): age fallback.
                    stale_reason = f"unknown_pid_age_{age:.0f}s_exceeds_{STALE_LOCK_SEC}s"
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


def _rename_with_retry(src: str, dst: str, tries: int = 7,
                        base_delay: float = 0.5) -> None:
    """os.rename with exponential-backoff retry on Windows PermissionError.

    Root cause 2026-07-02: Windows Search Indexer / Defender realtime scan opens
    transient handles on newly-created dirs; rename fails with WinError 5. A
    live director_kb_query.py process can also hold an mmap handle on
    E.pt / E_unit_fp16.npy inside the live dir, blocking the dir rename. Retry
    with jitter clears in almost all cases. tries=7 gives a ~30s cumulative
    backoff window (0.5,1,2,4,8,16s) vs the prior ~8s, which was too short for a
    reader holding a handle across a query (testbed 2026-07-08).
    """
    import random  # noqa: PLC0415
    last_exc = None
    for attempt in range(tries):
        try:
            os.rename(src, dst)
            return
        except PermissionError as e:  # noqa: PERF203
            last_exc = e
            if attempt == tries - 1:
                break
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.25)
            print(f"[continuous-ingest] rename retry {attempt+1}/{tries} "
                  f"after {delay:.2f}s (WinError likely): {e}",
                  flush=True, file=sys.stderr)
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def _sweep_stale_staging_dirs(out_dir: Path) -> int:
    """Clean up `<name>.staging.<pid>` dirs where PID is not alive AND `<name>.old.<pid>`.
    Runs at daemon startup + before every ingest to prevent 380-dir accumulation
    (observed 2026-07-02: silent accumulation over ~150 successful ingests + N
    failed swaps left an empty dir per PID that never got cleaned).
    """
    import re, shutil  # noqa: PLC0415
    parent = out_dir.parent
    base = out_dir.name
    n_cleaned = 0
    for p in parent.iterdir():
        if not p.is_dir():
            continue
        m = re.match(rf"^{re.escape(base)}\.(?:staging|old)\.(\d+)$", p.name)
        if not m:
            continue
        pid = int(m.group(1))
        if pid == os.getpid():
            continue  # our own; other logic handles it
        if _pid_alive(pid):
            continue  # some other live process; leave alone
        try:
            shutil.rmtree(p, ignore_errors=True)
            n_cleaned += 1
        except OSError:
            pass
    return n_cleaned


def _atomic_swap_kb(staging: Path, final: Path) -> None:
    """Replace `final` with `staging` atomically (best-effort on Windows).

    Strategy:
      1. If `final` exists, rename it to `final.old.<pid>` (atomic on same-FS)
      2. Rename `staging` -> `final` (atomic; retry on WinError 5)
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
        _rename_with_retry(str(final), str(backup))
    try:
        _rename_with_retry(str(staging), str(final))
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
    # Sweep other-PID stale staging + old dirs (accumulate silently over months
    # otherwise; 2026-07-02 found 380 empty stale .staging.<pid> dirs).
    n_swept = _sweep_stale_staging_dirs(out_dir)
    if n_swept > 0 and not quiet:
        print(f"[continuous-ingest] swept {n_swept} stale staging/old dirs",
              flush=True)

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
        # Resilience (testbed 2026-07-26): retry transient Windows resource-
        # exhaustion (WinError 1450/1455/8) with gc + backoff before recording a
        # permanent failure. Root cause of the 4 recorded failures + 18-day-stale
        # index: a scandir over a cluttered data/ dir hit WinError 1450 under
        # multi-agent I/O contention and aborted the whole run. A calmer retry
        # pass succeeds. Non-transient errors fail fast (no wasted backoff).
        import gc  # noqa: PLC0415
        result = None
        n_attempts = 1 + len(_INGEST_RETRY_BACKOFFS_SEC)
        for attempt in range(n_attempts):
            try:
                result = _do_ingest(schema, trigger="mtime_changed", quiet=quiet)
                break
            except Exception as e:  # noqa: BLE001
                is_last = attempt >= n_attempts - 1
                if _is_transient_resource_error(e) and not is_last:
                    backoff = _INGEST_RETRY_BACKOFFS_SEC[attempt]
                    gc.collect()
                    print(f"[continuous-ingest] transient resource error "
                          f"(attempt {attempt+1}/{n_attempts}); gc + backoff "
                          f"{backoff:.0f}s then retry: {type(e).__name__}: {str(e)[:200]}",
                          flush=True, file=sys.stderr)
                    time.sleep(backoff)
                    continue
                # Non-transient OR retries exhausted: record the failure so the
                # next scan retries (last_scan_max_mtime stays at prev value).
                state["last_failed_ingest_ts"] = time.time()
                state["last_failed_ingest_error"] = f"{type(e).__name__}: {str(e)[:500]}"
                state["n_failed_ingests"] = int(state.get("n_failed_ingests", 0)) + 1
                state["last_failed_ingest_attempts"] = attempt + 1
                _save_state(state)
                event["ingest_failed"] = True
                event["ingest_error"] = f"{type(e).__name__}: {str(e)[:300]}"
                event["ingest_attempts"] = attempt + 1
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
