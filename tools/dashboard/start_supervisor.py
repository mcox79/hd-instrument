"""One-shot launcher: spawn supervisor.py with DETACHED_PROCESS, then exit.

The detached child has no console, no parent handles to inherit, no CTRL_CLOSE_EVENT
delivery path when the launching shell session ends. This is the cleanest way to
fully detach a long-running Python process from a transient PowerShell session on
Windows.
"""

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV_PY = HERE / ".venv" / "Scripts" / "python.exe"
SUPERVISOR = HERE / "supervisor.py"
SUPERVISOR_LOG = HERE / "supervisor.log"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

with open(SUPERVISOR_LOG, "ab") as log_f:
    proc = subprocess.Popen(
        [str(VENV_PY), str(SUPERVISOR)],
        cwd=str(HERE),
        stdout=log_f, stderr=log_f, stdin=subprocess.DEVNULL,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
    )

print(f"Launched supervisor pid={proc.pid} detached")
sys.exit(0)
