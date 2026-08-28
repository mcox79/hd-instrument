#!/usr/bin/env python
"""tools/remote_run_request_watcher.py -- STANDING watcher that gives solvers SELF-SERVICE remote dispatch.

Solvers are scope-barred from preregs + remote ops, so they cannot queue their own runs -- they drop a
`notes/problems/<slug>/REMOTE_RUN_REQUEST_<cell>.md`. This watcher (run on a Windows Scheduled Task every few
minutes; see tools/orchestrator/install_remote_run_watcher_task.ps1) scans for those files and AUTO-RUNS
`tools/fulfill_remote_run_request.py` on any NEW or CHANGED one -- so a solver dropping a request gets it
queued to the right CPU or GPU queue with NO strategy session in the loop. The fulfiller's guardrails
(self-test, no-spaCy, KB_REFERENT, hdlab-closure ship, CPU/GPU route, smoke-default warning) are the gate.

SEMANTICS
  - First run (no state file): SEED -- record every current request as processed WITHOUT dispatching (start
    watching "from now"; avoids re-firing already-handled / known-blocked requests). Use --seed to re-seed.
  - Subsequent runs: dispatch a request that is NEW (unseen path) or CHANGED (edited -> new content hash;
    dispatched with --rerun so a terminal remote entry is reset). Unchanged -> skip.
  - A failed dispatch is retried up to MAX_ATTEMPTS (handles a transient remote outage); after that the hash
    is parked until the solver edits the request (a persistently-broken cell does not spam the queue).
  - CPU vs GPU is decided by the request's `queue:` / the cell's torch usage inside the fulfiller.

State: data/remote_run_request_watcher_state.json  ({path: {hash, status, attempts, ts}}).
Log:   data/remote_run_request_watcher_log.jsonl.
Lock:  data/remote_run_request_watcher.lock (skips if another watcher run is in flight).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULFILLER = os.path.join(REPO, "tools", "fulfill_remote_run_request.py")
STATE = os.path.join(REPO, "data", "remote_run_request_watcher_state.json")
LOG = os.path.join(REPO, "data", "remote_run_request_watcher_log.jsonl")
LOCK = os.path.join(REPO, "data", "remote_run_request_watcher.lock")
REQ_GLOB = os.path.join(REPO, "notes", "problems", "*", "REMOTE_RUN_REQUEST_*.md")
MAX_ATTEMPTS = 3
LOCK_STALE_S = 3600


def _now():
    return datetime.now(timezone.utc).isoformat()


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _load(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return default


def _save_state(state):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE)


def _log(rec):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8", newline="") as f:
        f.write(json.dumps(rec) + "\n")


def _lock_ok(mtime_now):
    """Best-effort single-flight. Returns True if we acquired the lock."""
    if os.path.exists(LOCK):
        try:
            age = mtime_now - os.path.getmtime(LOCK)
            if age < LOCK_STALE_S:
                return False  # another run in flight
        except OSError:
            pass
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w", encoding="utf-8") as f:
        f.write(_now())
    return True


def dispatch(req, rerun, dry_run):
    cmd = [sys.executable, FULFILLER, "--request", req]
    if rerun:
        cmd.append("--rerun")
    if dry_run:
        cmd.append("--dry-run")
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    return p.returncode, (p.stdout[-800:] + p.stderr[-400:])


def main():
    ap = argparse.ArgumentParser(description="Watch for solver REMOTE_RUN_REQUESTs and auto-dispatch new/changed ones.")
    ap.add_argument("--seed", action="store_true", help="record all current requests as processed WITHOUT dispatching")
    ap.add_argument("--dry-run", action="store_true", help="show what would dispatch; fulfiller runs in --dry-run too")
    ap.add_argument("--force", action="store_true", help="ignore the lock")
    a = ap.parse_args()

    # a monotonic-ish clock for the lock; time.time() is unavailable-free here (normal tool, not a workflow)
    import time
    if not a.force and not _lock_ok(time.time()):
        print("[watcher] another run is in flight (lock fresh); exiting.")
        return 0

    try:
        state = _load(STATE, None)
        requests = sorted(glob.glob(REQ_GLOB))
        seeding = state is None or a.seed
        if state is None:
            state = {}

        if seeding:
            for req in requests:
                rel = os.path.relpath(req, REPO).replace("\\", "/")
                state[rel] = {"hash": _sha(req), "status": "seeded", "attempts": 0, "ts": _now()}
            _save_state(state)
            _log({"ts": _now(), "action": "seed", "count": len(requests)})
            print(f"[watcher] SEEDED {len(requests)} existing request(s) (no dispatch). Future new/changed ones will fire.")
            return 0

        dispatched, skipped, failed = 0, 0, 0
        for req in requests:
            rel = os.path.relpath(req, REPO).replace("\\", "/")
            h = _sha(req)
            prev = state.get(rel)
            if prev and prev.get("hash") == h:
                if prev.get("status") in ("dispatched", "seeded"):
                    skipped += 1
                    continue
                if prev.get("attempts", 0) >= MAX_ATTEMPTS:
                    skipped += 1
                    continue
            rerun = bool(prev)  # a re-request (edited) resets the terminal remote entry
            print(f"[watcher] {'RE-' if rerun else ''}DISPATCH {rel}{' (dry-run)' if a.dry_run else ''}")
            rc, tail = dispatch(req, rerun=rerun, dry_run=a.dry_run)
            if rc == 0:
                state[rel] = {"hash": h, "status": "dispatched", "attempts": (prev or {}).get("attempts", 0) + 1, "ts": _now()}
                dispatched += 1
                print(f"[watcher]   OK -> queued")
            else:
                state[rel] = {"hash": h, "status": "failed", "attempts": (prev or {}).get("attempts", 0) + 1, "ts": _now()}
                failed += 1
                print(f"[watcher]   FAIL rc={rc} (attempt {state[rel]['attempts']}/{MAX_ATTEMPTS})")
            _log({"ts": _now(), "action": "dispatch", "request": rel, "rerun": rerun, "rc": rc,
                  "dry_run": a.dry_run, "tail": tail})
            _save_state(state)

        print(f"[watcher] done: dispatched={dispatched} skipped={skipped} failed={failed} (total requests {len(requests)})")
        return 0
    finally:
        try:
            os.remove(LOCK)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
