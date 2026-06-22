#!/usr/bin/env python
"""
queue_status.py — aggregate queue-depth + ETA visibility per Fix #11 TODO #11.

Reads local + remote queue.json files; reports pending/running counts + estimated
wall-time-to-clear per queue. Pipeline-agent spawns use this PRE-DISPATCH to make
informed routing decisions (route to less-contended queue OR defer dispatch).

Usage:
    python tools/queue_status.py                    # local + remote, default-format
    python tools/queue_status.py --queue local_cpu  # specific queue
    python tools/queue_status.py --json             # machine-readable
    python tools/queue_status.py --eta-only         # just ETA-to-start estimates

Reads (best-effort; missing files skipped):
    data/local_cpu_queue/queue.json
    marsh@home:C:/dev/hd-instrument/data/remote_cpu_queue/queue.json
    marsh@home:C:/dev/hd-instrument/data/overnight_queue/queue.json

Per-entry expected fields: name / status / estimated_wall_s (optional; default 1800)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_WALL_S = 1800  # 30min default if estimated_wall_s missing
QUEUES_LOCAL = [
    ("local_cpu", "data/local_cpu_queue/queue.json"),
]
QUEUES_REMOTE = [
    ("remote_cpu", "data/remote_cpu_queue/queue.json"),
    ("overnight", "data/overnight_queue/queue.json"),
]


def read_local_queue(path: Path) -> list:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def read_remote_queue(remote_path: str) -> list:
    """Read remote queue.json via SSH; returns [] on any error (best-effort)."""
    cmd = [
        "ssh", "-o", "ConnectTimeout=10", "marsh@home",
        f'.venv\\Scripts\\python.exe -c "import json; print(open(r\'C:/dev/hd-instrument/{remote_path}\').read())"',
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if out.returncode != 0:
            return []
        # strip noise (quantum warnings; OpenSSH banners)
        lines = [ln for ln in out.stdout.splitlines() if ln.strip() and not any(
            n in ln.lower() for n in ("quantum", "openssh", "vulnerable", "store now", "warning")
        )]
        if not lines:
            return []
        return json.loads("\n".join(lines))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return []


def aggregate(entries: list) -> dict:
    """Compute queue-depth + ETA aggregate."""
    pending = [e for e in entries if e.get("status") == "pending"]
    running = [e for e in entries if e.get("status") == "running"]
    completed = [e for e in entries if e.get("status") in ("completed", "failed")]
    # ETA-to-clear = sum(estimated_wall_s) over running + pending
    eta_s = sum(e.get("estimated_wall_s", DEFAULT_WALL_S) for e in (running + pending))
    return {
        "pending_count": len(pending),
        "running_count": len(running),
        "completed_count": len(completed),
        "total_count": len(entries),
        "eta_to_clear_s": eta_s,
        "eta_to_clear_min": round(eta_s / 60, 1),
        "pending_names": [e.get("name", "?") for e in pending[:10]],
        "running_names": [e.get("name", "?") for e in running[:5]],
    }


def main():
    parser = argparse.ArgumentParser(description="Queue-depth + ETA aggregate visibility")
    parser.add_argument("--queue", default=None, help="Specific queue name (local_cpu / remote_cpu / overnight)")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    parser.add_argument("--eta-only", action="store_true", help="Just ETA-to-clear per queue")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    results = {}

    # Local queues
    for name, rel_path in QUEUES_LOCAL:
        if args.queue and args.queue != name:
            continue
        entries = read_local_queue(repo_root / rel_path)
        results[name] = aggregate(entries)

    # Remote queues (one SSH round-trip per; could batch but kept simple)
    for name, rel_path in QUEUES_REMOTE:
        if args.queue and args.queue != name:
            continue
        entries = read_remote_queue(rel_path)
        results[name] = aggregate(entries)
        results[name]["_remote"] = True

    if args.json:
        print(json.dumps(results, indent=2))
        return

    if args.eta_only:
        for name, agg in results.items():
            tag = " (remote)" if agg.get("_remote") else ""
            print(f"{name}{tag}: ETA-to-clear={agg['eta_to_clear_min']}min ({agg['pending_count']} pending / {agg['running_count']} running)")
        return

    # Default human-readable format
    for name, agg in results.items():
        tag = " (remote; SSH)" if agg.get("_remote") else ""
        print(f"=== {name}{tag} ===")
        print(f"  pending: {agg['pending_count']} | running: {agg['running_count']} | completed: {agg['completed_count']} | total: {agg['total_count']}")
        print(f"  ETA-to-clear: {agg['eta_to_clear_min']}min (assumes {DEFAULT_WALL_S}s default per-entry; override via entry.estimated_wall_s)")
        if agg["running_names"]:
            print(f"  running: {', '.join(agg['running_names'])}")
        if agg["pending_names"]:
            shown = agg["pending_names"][:3]
            ell = f" + {agg['pending_count']-3} more" if agg["pending_count"] > 3 else ""
            print(f"  next pending: {', '.join(shown)}{ell}")
        print()


if __name__ == "__main__":
    main()
