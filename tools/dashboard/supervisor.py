"""Dashboard supervisor: restart uvicorn if it dies.

Launches `python -m uvicorn server:app ...` as a child process. When the child
exits for any reason, sleep briefly + relaunch. Pure-Python parent that doesn't
do SSH itself, so OS resource exhaustion from the SSH poller can't kill the
supervisor. Only uvicorn (the child) is affected, and the supervisor brings it
back up.

Usage:
    python supervisor.py [--host 0.0.0.0] [--port 8765]

Log files:
    dashboard.out.log   - uvicorn stdout (access logs)
    dashboard.err.log   - uvicorn stderr (paramiko noise + exceptions)
    supervisor.log      - this script's restart events
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent


def log(msg: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}\n"
    sys.stdout.write(line)
    sys.stdout.flush()
    try:
        with open(HERE / "supervisor.log", "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", default="8765")
    p.add_argument("--log-level", default="info")
    p.add_argument("--restart-delay-s", type=float, default=2.0)
    p.add_argument("--restart-cooldown-s", type=float, default=10.0,
                   help="if child died within this many seconds of start, "
                        "wait longer before next restart to avoid tight loops")
    p.add_argument("--cooldown-multiplier", type=float, default=5.0)
    args = p.parse_args()

    # Use pythonw.exe (windowless variant) to spawn uvicorn — python.exe is a
    # wrapper that re-execs the real interpreter and silently drops the parent's
    # DETACHED_PROCESS flag, so a console gets created anyway. pythonw.exe never
    # creates a console under any circumstance.
    venv_python = HERE / ".venv" / "Scripts" / "pythonw.exe"
    if not venv_python.is_file():
        venv_python = HERE / ".venv" / "Scripts" / "python.exe"
    if not venv_python.is_file():
        log(f"ERROR: venv python not found at {venv_python}")
        return 1

    out_log = HERE / "dashboard.out.log"
    err_log = HERE / "dashboard.err.log"

    log(f"supervisor pid={os.getpid()} starting; "
        f"python={venv_python} host={args.host} port={args.port}")

    restart_count = 0
    while True:
        cmd = [
            str(venv_python),
            "-m", "uvicorn",
            "server:app",
            "--app-dir", str(HERE),
            "--host", args.host,
            "--port", args.port,
            "--log-level", args.log_level,
        ]
        log(f"launching child: {' '.join(cmd)}")
        child_start = time.time()
        # DETACHED_PROCESS: child gets NO console. Survives parent console close
        # (CTRL_CLOSE_EVENT) which is suspected to be killing uvicorn after the
        # spawning PowerShell session ends. CREATE_NEW_PROCESS_GROUP is NOT enough
        # — the process still inherits the parent's console handle.
        DETACHED_PROCESS = 0x00000008
        flags = DETACHED_PROCESS | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        try:
            with open(out_log, "ab") as out_f, open(err_log, "ab") as err_f:
                proc = subprocess.Popen(
                    cmd, cwd=str(HERE),
                    stdout=out_f, stderr=err_f, stdin=subprocess.DEVNULL,
                    creationflags=flags,
                )
            rc = proc.wait()
            uptime_s = time.time() - child_start
            log(f"child pid={proc.pid} exited rc={rc} after {uptime_s:.1f}s")
        except Exception as e:
            log(f"failed to spawn child: {type(e).__name__}: {e}")
            uptime_s = 0.0

        restart_count += 1
        if uptime_s < args.restart_cooldown_s:
            delay = args.restart_delay_s * args.cooldown_multiplier
            log(f"child died fast (< {args.restart_cooldown_s}s); "
                f"cooldown {delay:.1f}s before restart #{restart_count + 1}")
        else:
            delay = args.restart_delay_s
            log(f"normal restart #{restart_count + 1} after {delay:.1f}s")
        time.sleep(delay)


if __name__ == "__main__":
    sys.exit(main())
