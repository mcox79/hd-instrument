#!/usr/bin/env python3
"""monitor_arm.py -- self-healing wrapper around notes_monitor.py.

Direct Python equivalent of monitor_arm.sh (without the kill-priors leak guard;
since Python launches Python via subprocess in-process, there's no second bash
shell to leak). Restarts the inner monitor on any non-zero exit, with a 5s delay.

INVOCATION (canonical, supersedes the bash wrapper for popup-free operation):
  Monitor({
    command: "python D:\\\\AI\\\\hd-instrument\\\\tools\\\\monitor_arm.py <role>",
    persistent: true,
    timeout_ms: 3600000,
    description: "notes_monitor <role> (Python; no subprocess spawns)"
  })

WHY THIS REPLACES THE BASH WRAPPER: bash spawned `find | grep | grep | sort`
every 20s in notes_monitor.sh. Each child .exe under Claude Code's hidden-console
parent allocated a fresh visible console = popup flash. Python port runs the
set-diff in-process. Inner script restarts (if it ever crashes) reuse the same
python.exe console — no flash.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time

if len(sys.argv) < 2:
    sys.stderr.write("usage: python tools/monitor_arm.py <role>\n")
    sys.exit(2)

ROLE = sys.argv[1].strip()
ROOT = r"D:\AI\hd-instrument"
INNER = os.path.join(ROOT, "tools", "notes_monitor.py")
PYTHON = sys.executable

try:
    os.chdir(ROOT)
except OSError as e:
    sys.stderr.write(f"MONITOR-ARM-FATAL: cannot cd {ROOT}: {e}\n")
    sys.exit(1)

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

child: subprocess.Popen | None = None


def cleanup(*_args: object) -> None:
    if child is not None and child.poll() is None:
        try:
            child.terminate()
        except OSError:
            pass
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

print(
    f"MONITOR-ARMED: notes_monitor for {ROLE} "
    f"(monitor_arm.py wrapper; Python inner; no subprocess spawns; popup-free)",
    flush=True,
)

restart_count = 0
while True:
    child = subprocess.Popen(
        [PYTHON, INNER, ROLE],
        cwd=ROOT,
        creationflags=CREATE_NO_WINDOW,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    rc = child.wait()
    restart_count += 1
    print(
        f"MONITOR-CRASH: notes_monitor {ROLE} exited rc={rc} "
        f"(restart #{restart_count}); reloading in 5s",
        flush=True,
    )
    time.sleep(5)
