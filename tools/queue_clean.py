"""Queue management utility.

Subcommands
-----------
--list [queue_name]         Show current queue.json entries (all statuses).
--list-failed [queue_name]  Show only failed/killed entries.
--reset <name>              Flip a terminal entry back to pending (re-run it).
--remove <name>             Delete an entry from the queue entirely.

Queue name defaults to 'overnight_queue' if not specified.

Examples
--------
    python tools/queue_clean.py --list local_cpu_queue
    python tools/queue_clean.py --list-failed overnight_queue
    python tools/queue_clean.py --reset pq_high_resolution_v1 local_cpu_queue
    python tools/queue_clean.py --remove old_exp_name local_cpu_queue
    python tools/queue_clean.py --dry-run local_cpu_queue

For remote queues (overnight_queue / remote_cpu_queue), reads are done
via SCP from marsh@home using the same pattern as queue_add_remote.sh.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from safe_queue import QueueLock  # noqa: E402

SSH_TARGET = "marsh@home"
REPO_REMOTE = "C:/dev/hd-instrument"

# Statuses that --reset accepts; statuses that --remove accepts freely.
_TERMINAL = {"done", "failed", "completed", "canceled", "killed"}
_ALL_STATUSES = _TERMINAL | {"pending", "running"}

# Status -> display colour prefix (plain ANSI; fine for Windows Terminal / bash).
_STATUS_COLOUR = {
    "pending":   "\033[33m",   # yellow
    "running":   "\033[34m",   # blue
    "done":      "\033[32m",   # green
    "completed": "\033[32m",
    "failed":    "\033[31m",   # red
    "killed":    "\033[31m",
    "canceled":  "\033[90m",   # grey
}
_RESET = "\033[0m"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _queue_path(queue_name: str) -> Path:
    return REPO / "data" / queue_name / "queue.json"


def _is_remote(queue_name: str) -> bool:
    return queue_name in ("overnight_queue", "remote_cpu_queue")


def _read_remote(queue_name: str) -> dict:
    """SCP the queue.json from marsh@home into a tmp file and parse it."""
    remote_path = f"{SSH_TARGET}:{REPO_REMOTE}/data/{queue_name}/queue.json"
    tmp = REPO / "data" / f"_remote_queue_tmp_{queue_name}.json"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["scp", "-o", "ConnectTimeout=10", remote_path, str(tmp)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[queue-clean] ERROR: SCP failed: {e.stderr.decode().strip()}", file=sys.stderr)
        sys.exit(1)
    with open(tmp, "r", encoding="utf-8") as f:
        data = json.load(f)
    tmp.unlink(missing_ok=True)
    return data


def _write_remote(queue_name: str, queue: dict) -> None:
    """Write updated queue.json to a local tmp, SCP it back, then SSH-replace atomically."""
    tmp = REPO / "data" / f"_remote_queue_tmp_{queue_name}.json"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    remote_tmp = f"{REPO_REMOTE}/data/{queue_name}/queue.json.tmp"
    remote_final = f"{REPO_REMOTE}/data/{queue_name}/queue.json"
    try:
        subprocess.run(
            ["scp", "-o", "ConnectTimeout=10", str(tmp),
             f"{SSH_TARGET}:{remote_tmp}"],
            check=True,
            capture_output=True,
        )
        # Atomic replace on remote via SSH + PowerShell Move-Item.
        ps_cmd = f"Move-Item -Force '{remote_tmp}' '{remote_final}'"
        subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", SSH_TARGET,
             f"powershell -Command \"{ps_cmd}\""],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[queue-clean] ERROR: remote write failed: {e.stderr.decode().strip()}",
              file=sys.stderr)
        tmp.unlink(missing_ok=True)
        sys.exit(1)
    tmp.unlink(missing_ok=True)


def _colour_status(status: str) -> str:
    colour = _STATUS_COLOUR.get(status, "")
    return f"{colour}{status}{_RESET}" if colour else status


def _print_entries(entries: list[dict], queue_name: str, header: str) -> None:
    print(f"\n{header} [{queue_name}] — {len(entries)} entries")
    print("-" * 60)
    if not entries:
        print("  (empty)")
        return
    for e in entries:
        name = e.get("name", "?")
        status = e.get("status", "?")
        run_idx = e.get("run_index", 1)
        gated = e.get("gated_at", "")
        started = e.get("started_at") or ""
        ri_tag = f" [run #{run_idx}]" if run_idx and run_idx > 1 else ""
        print(
            f"  {_colour_status(status):30s}  {name}{ri_tag}"
            + (f"\n    gated={gated}" if gated else "")
            + (f"  started={started}" if started else "")
        )
    print()


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------

def cmd_list(queue_name: str, failed_only: bool) -> int:
    if _is_remote(queue_name):
        q = _read_remote(queue_name)
    else:
        qp = _queue_path(queue_name)
        if not qp.exists():
            print(f"[queue-clean] queue not found: {qp}")
            return 1
        with open(qp, "r", encoding="utf-8") as f:
            q = json.load(f)

    entries = q.get("experiments", [])
    if failed_only:
        entries = [e for e in entries if e.get("status") in ("failed", "killed")]
        _print_entries(entries, queue_name, "Failed/killed entries")
    else:
        _print_entries(entries, queue_name, "Queue")

    # Summary counts
    counts: dict[str, int] = {}
    for e in q.get("experiments", []):
        s = e.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
    if counts:
        summary = "  Summary: " + "  ".join(
            f"{_colour_status(s)}={n}" for s, n in sorted(counts.items())
        )
        print(summary)
    return 0


def cmd_reset(name: str, queue_name: str, dry_run: bool) -> int:
    """Flip a terminal entry back to pending."""
    if _is_remote(queue_name):
        q = _read_remote(queue_name)
        is_remote = True
    else:
        qp = _queue_path(queue_name)
        if not qp.exists():
            print(f"[queue-clean] queue not found: {qp}")
            return 1
        with open(qp, "r", encoding="utf-8") as f:
            q = json.load(f)
        is_remote = False

    for entry in q.get("experiments", []):
        if entry.get("name") == name:
            cur = entry.get("status", "")
            if cur == "pending":
                print(f"[queue-clean] {name} is already pending; nothing to do")
                return 0
            if cur == "running":
                print(
                    f"[queue-clean] ERROR: {name} is currently running. "
                    f"Cannot reset a running entry.",
                    file=sys.stderr,
                )
                return 1
            if cur not in _TERMINAL:
                print(
                    f"[queue-clean] ERROR: {name} has unexpected status '{cur}'. "
                    f"Inspect queue.json manually.",
                    file=sys.stderr,
                )
                return 1
            run_index = entry.get("run_index", 1) + 1
            if dry_run:
                print(
                    f"[queue-clean] DRY-RUN: would reset '{name}' "
                    f"({cur} -> pending, run_index={run_index})"
                )
                return 0
            entry.update({
                "status": "pending",
                "gated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "run_index": run_index,
                "started_at": None,
                "finished_at": None,
                "claimed_by": None,
            })
            if is_remote:
                _write_remote(queue_name, q)
            else:
                qp = _queue_path(queue_name)
                with QueueLock(qp, max_wait_s=10.0) as lock:
                    lock.write(q)
            print(f"[queue-clean] OK: reset '{name}' to pending (run_index={run_index})")
            return 0

    print(f"[queue-clean] ERROR: entry '{name}' not found in {queue_name}", file=sys.stderr)
    return 1


def cmd_remove(name: str, queue_name: str, dry_run: bool) -> int:
    """Delete an entry from the queue."""
    if _is_remote(queue_name):
        q = _read_remote(queue_name)
        is_remote = True
    else:
        qp = _queue_path(queue_name)
        if not qp.exists():
            print(f"[queue-clean] queue not found: {qp}")
            return 1
        with open(qp, "r", encoding="utf-8") as f:
            q = json.load(f)
        is_remote = False

    before = q.get("experiments", [])
    target = next((e for e in before if e.get("name") == name), None)
    if target is None:
        print(f"[queue-clean] ERROR: entry '{name}' not found in {queue_name}", file=sys.stderr)
        return 1

    cur = target.get("status", "")
    if cur == "running":
        print(
            f"[queue-clean] ERROR: '{name}' is currently running. Stop it before removing.",
            file=sys.stderr,
        )
        return 1

    if dry_run:
        print(f"[queue-clean] DRY-RUN: would remove '{name}' (status={cur})")
        return 0

    after = [e for e in before if e.get("name") != name]
    q["experiments"] = after

    if is_remote:
        _write_remote(queue_name, q)
    else:
        qp = _queue_path(queue_name)
        with QueueLock(qp, max_wait_s=10.0) as lock:
            lock.write(q)
    print(f"[queue-clean] OK: removed '{name}' from {queue_name}")
    return 0


def cmd_dry_run(queue_name: str) -> int:
    """Report which entries are older than 24h with terminal status (would prune)."""
    if _is_remote(queue_name):
        q = _read_remote(queue_name)
    else:
        qp = _queue_path(queue_name)
        if not qp.exists():
            print(f"[queue-clean] queue not found: {qp}")
            return 1
        with open(qp, "r", encoding="utf-8") as f:
            q = json.load(f)

    now = time.time()
    prune_candidates = []
    for e in q.get("experiments", []):
        if e.get("status") not in _TERMINAL:
            continue
        gated = e.get("gated_at", "")
        try:
            t = time.mktime(time.strptime(gated, "%Y-%m-%dT%H:%M:%S"))
            age_h = (now - t) / 3600
        except (ValueError, TypeError):
            age_h = 0
        if age_h >= 24:
            prune_candidates.append((e["name"], e.get("status"), age_h))

    if not prune_candidates:
        print(f"[queue-clean] DRY-RUN [{queue_name}]: no entries older than 24h with terminal status")
        return 0

    print(f"\n[queue-clean] DRY-RUN [{queue_name}]: {len(prune_candidates)} entries would be pruned:")
    for name, status, age_h in sorted(prune_candidates, key=lambda x: -x[2]):
        print(f"  {_colour_status(status):30s}  {name}  (age={age_h:.1f}h)")
    print()
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--list",
        nargs="?",
        const="overnight_queue",
        metavar="QUEUE_NAME",
        help="Show all entries in QUEUE_NAME (default: overnight_queue)",
    )
    ap.add_argument(
        "--list-failed",
        nargs="?",
        const="overnight_queue",
        metavar="QUEUE_NAME",
        help="Show only failed/killed entries in QUEUE_NAME",
    )
    ap.add_argument(
        "--reset",
        metavar="NAME",
        help="Flip a terminal entry back to pending",
    )
    ap.add_argument(
        "--remove",
        metavar="NAME",
        help="Delete an entry from the queue",
    )
    ap.add_argument(
        "--dry-run",
        nargs="?",
        const="overnight_queue",
        metavar="QUEUE_NAME",
        help=(
            "Report which terminal entries are older than 24h and would be pruned. "
            "Does NOT modify the queue. Cron-safe."
        ),
    )
    ap.add_argument(
        "queue_name",
        nargs="?",
        default=None,
        help=(
            "Queue to target for --reset / --remove "
            "(e.g. local_cpu_queue, overnight_queue, remote_cpu_queue). "
            "Defaults to overnight_queue."
        ),
    )
    args = ap.parse_args()

    # Resolve effective queue name for --reset / --remove.
    effective_queue = args.queue_name or "overnight_queue"

    # Exactly one action required.
    actions = [args.list, args.list_failed, args.reset, args.remove, args.dry_run]
    active = [a for a in actions if a is not None]
    if len(active) == 0:
        ap.print_help()
        return 2
    if len(active) > 1:
        print("[queue-clean] ERROR: specify only one action at a time", file=sys.stderr)
        return 2

    if args.list is not None:
        return cmd_list(args.list, failed_only=False)

    if args.list_failed is not None:
        return cmd_list(args.list_failed, failed_only=True)

    if args.dry_run is not None:
        return cmd_dry_run(args.dry_run)

    if args.reset is not None:
        return cmd_reset(args.reset, effective_queue, dry_run=False)

    if args.remove is not None:
        return cmd_remove(args.remove, effective_queue, dry_run=False)

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
