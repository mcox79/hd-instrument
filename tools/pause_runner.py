"""Pause / resume GPU + CPU runners by writing a PAUSED flag file.

Runs ON THE WORKSTATION (where the queues + runners live).

The runner_v2_prod.py main loop checks for `<queue_dir>/PAUSED` before
claiming the next experiment. While the flag exists, the runner sits idle
(heartbeat status = "paused") and does NOT advance the idle-exit timer.

CLI:
  --gpu          target the GPU queue (overnight_queue)
  --cpu          target the CPU queue (remote_cpu_queue)
  --both         target both queues
  --resume       remove the PAUSED flag instead of creating it
  --hard         also kill the currently-running experiment, requeue it,
                 and restart the runner so it picks up the flag immediately
                 (without --hard, the current experiment runs to completion
                 and only the NEXT claim is blocked)
  --status       print current pause + runner status and exit

Examples:
  python pause_runner.py --status
  python pause_runner.py --gpu                  # soft pause GPU queue
  python pause_runner.py --both --hard          # kill + pause everything
  python pause_runner.py --gpu --resume         # let GPU resume claiming
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PYTHON = str(REPO / ".venv" / "Scripts" / "python.exe")

QUEUES = {
    "gpu": "overnight_queue",
    "cpu": "remote_cpu_queue",
}


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def pause_path(queue_kind: str) -> Path:
    return REPO / "data" / QUEUES[queue_kind] / "PAUSED"


def heartbeat_path(queue_kind: str) -> Path:
    return REPO / "data" / QUEUES[queue_kind] / "heartbeat.json"


def read_heartbeat(queue_kind: str) -> dict | None:
    hb = heartbeat_path(queue_kind)
    if not hb.exists():
        return None
    try:
        return json.loads(hb.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def touch_paused(queue_kind: str, reason: str) -> None:
    """Atomic write: .tmp then rename."""
    p = pause_path(queue_kind)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    payload = json.dumps({
        "ts": _now_iso(),
        "queue": QUEUES[queue_kind],
        "reason": reason,
    }, indent=2)
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(p)
    print(f"  PAUSED: {p}")


def remove_paused(queue_kind: str) -> bool:
    p = pause_path(queue_kind)
    if p.exists():
        p.unlink()
        print(f"  RESUMED: removed {p}")
        return True
    print(f"  (no PAUSED flag at {p})")
    return False


def call_cutover(queue_kind: str) -> int:
    """Run cutover.py to kill running experiment, requeue, and relaunch runner.

    The runner sees the PAUSED flag we already wrote and immediately idles.
    """
    flag = "--gpu-only" if queue_kind == "gpu" else "--cpu-only"
    cmd = [PYTHON, str(REPO / "tools" / "cutover.py"), flag]
    print(f"  Running cutover: {' '.join(cmd)}")
    return subprocess.call(cmd)


def print_status(targets: list[str]) -> None:
    print(f"[{_now_iso()}] pause / runner status:")
    for kind in targets:
        flag = pause_path(kind)
        hb = read_heartbeat(kind)
        flag_state = "PAUSED" if flag.exists() else "active"
        if hb is None:
            run_state = "no heartbeat"
        else:
            run_state = f"{hb.get('status')} (runner_id={hb.get('runner_id')}, current={hb.get('current')}, ts={hb.get('ts')})"
        print(f"  {kind.upper():4s} flag={flag_state:6s}  runner={run_state}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--both", action="store_true")
    ap.add_argument("--resume", action="store_true",
                    help="Remove PAUSED flag instead of creating it")
    ap.add_argument("--hard", action="store_true",
                    help="Kill running experiment + requeue + restart runner")
    ap.add_argument("--status", action="store_true",
                    help="Print current pause + runner state and exit")
    ap.add_argument("--reason", default="manual",
                    help="Reason string written into the PAUSED file")
    args = ap.parse_args()

    if args.both:
        targets = ["gpu", "cpu"]
    else:
        targets = [k for k, on in [("gpu", args.gpu), ("cpu", args.cpu)] if on]

    if args.status:
        print_status(targets or ["gpu", "cpu"])
        return 0

    if not targets:
        ap.error("specify --gpu, --cpu, --both, or --status")

    if args.resume and args.hard:
        ap.error("--resume and --hard are mutually exclusive")

    if args.resume:
        for kind in targets:
            remove_paused(kind)
        print_status(targets)
        return 0

    for kind in targets:
        touch_paused(kind, args.reason)

    if args.hard:
        for kind in targets:
            hb = read_heartbeat(kind)
            if hb and hb.get("status") == "running":
                print(f"  {kind.upper()}: running experiment '{hb.get('current')}'; cutover to kill + requeue")
                rc = call_cutover(kind)
                if rc != 0:
                    print(f"  WARN: cutover for {kind} returned exit {rc}")
            else:
                status = hb.get("status") if hb else "unknown"
                print(f"  {kind.upper()}: runner {status}; no kill needed (flag set, next claim blocked)")

    print_status(targets)
    return 0


if __name__ == "__main__":
    sys.exit(main())
