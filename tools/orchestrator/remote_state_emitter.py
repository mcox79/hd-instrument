"""Remote-side state emitter for the hd-instrument remote bridge.

Runs on marsh@home (Windows, cmd.exe environment). Snapshots queue state,
runner heartbeats, and recent verdicts into a single JSON file every 30s.

Designed to be launched once by Windows Task Scheduler (or a schtasks entry)
and run as a while-True loop. It writes:
    C:/dev/hd-instrument/data/remote_state_cache.json

The local orchestrator (heartbeat_watchdog.py patched) SCPs this file back to
D:/AI/hd-instrument/data/remote_state_cache.json every 30s, so sub-agents can
read it locally without any SSH overhead.

Usage (on remote):
    C:/dev/hd-instrument/.venv/Scripts/python.exe ^
        C:/dev/hd-instrument/tools/orchestrator/remote_state_emitter.py

Or via schtasks (see install_remote_emitter_schtask.ps1 in the same directory).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO = Path(r"C:/dev/hd-instrument")
OUTPUT = REPO / "data" / "remote_state_cache.json"
OVERNIGHT_QUEUE = REPO / "data" / "overnight_queue" / "queue.json"
CPU_QUEUE = REPO / "data" / "remote_cpu_queue" / "queue.json"

RUNNER_HEARTBEAT_PATHS = {
    "gpu_runner_0": REPO / "data" / "overnight_queue" / "heartbeat.gpu_runner_0.json",
    "cpu_runner_0": REPO / "data" / "remote_cpu_queue" / "heartbeat.cpu_runner_0.json",
}
# Also check generic heartbeat.json fallbacks
RUNNER_HEARTBEAT_FALLBACKS = {
    "gpu_runner_0": REPO / "data" / "overnight_queue" / "heartbeat.json",
    "cpu_runner_0": REPO / "data" / "remote_cpu_queue" / "heartbeat.json",
}
EVENT_OUTCOMES_DIR = REPO / "data" / "event_outcomes"
RUNNER_LOGS_DIR = REPO / "data"

POLL_INTERVAL_S = 30


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _queue_entries(queue_path: Path) -> list[dict]:
    """Load a queue.json and return the experiments list."""
    doc = _load_json(queue_path)
    if not isinstance(doc, dict):
        return []
    exps = doc.get("experiments")
    if not isinstance(exps, list):
        return []
    out = []
    for e in exps:
        if not isinstance(e, dict):
            continue
        out.append({
            "name": e.get("name"),
            "status": e.get("status"),
            "queued_at": e.get("queued_at") or e.get("created_at"),
            "started_at": e.get("started_at"),
        })
    return out


def _runner_state_from_heartbeat(runner_id: str) -> dict:
    """Read runner heartbeat from the queue-local heartbeat JSON file."""
    path = RUNNER_HEARTBEAT_PATHS.get(runner_id)
    fallback = RUNNER_HEARTBEAT_FALLBACKS.get(runner_id)

    doc: dict | None = None
    for p in [path, fallback]:
        if p is not None:
            result = _load_json(p)
            if isinstance(result, dict):
                doc = result
                break

    if not isinstance(doc, dict):
        return {"alive": False, "error": "heartbeat_missing"}

    return {
        "pid": doc.get("pid"),
        "heartbeat_ts": doc.get("ts"),
        "status": doc.get("status"),
        "current": doc.get("current"),
        "alive": True,
        "runner_id": doc.get("runner_id"),
    }


def _classify_python_procs() -> list[dict]:
    """Return a list of LOGICAL Python processes, grouping venv-shim+interpreter pairs.

    On Windows each runner/emitter/experiment is actually TWO PIDs:
      - the venv activation shim  (parent = cmd or schtasks)
      - the python.exe interpreter (parent = shim PID)

    We use WMIC to get (PID, ParentPID, CommandLine) for all python.exe procs,
    then:
      1. Build a pid->info map and parent->children map.
      2. Group shim+interpreter pairs: if proc B's parent is proc A (both python.exe),
         they form one logical process; B is the "real" interpreter.
      3. Classify each logical proc by its commandline:
         - "runner"           if cmdline contains "runner_v2_prod.py"
         - "emitter"          if cmdline contains "remote_state_emitter.py"
         - "experiment_child" if parent (logical) is a runner
         - "unknown"          otherwise

    Returns list of dicts:
      {type, name, pid, shim_pid, parent_pid, cmdline_short, mem_kb}
    """
    try:
        out = subprocess.check_output(
            [
                "wmic", "process", "where", "name='python.exe'",
                "get", "ProcessId,ParentProcessId,CommandLine,WorkingSetSize",
                "/format:csv",
            ],
            stderr=subprocess.DEVNULL,
            timeout=10,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return []

    # WMIC CSV: first non-empty line is header, rest are data rows.
    # Header: Node,CommandLine,ParentProcessId,ProcessId,WorkingSetSize
    rows = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if len(rows) < 2:
        return []

    header = [h.strip() for h in rows[0].split(",")]
    # Find column indices (case-insensitive)
    col = {h.lower(): i for i, h in enumerate(header)}
    idx_pid  = col.get("processid")
    idx_ppid = col.get("parentprocessid")
    idx_cmd  = col.get("commandline")
    idx_ws   = col.get("workingsetsize")
    if idx_pid is None or idx_ppid is None:
        return []

    procs: dict[int, dict] = {}
    for row in rows[1:]:
        parts = row.split(",")
        # Parts length check is done inside the loop after computing required.
        # Need at least enough parts to read pid and ppid columns.
        required = max(x for x in [idx_pid, idx_ppid, idx_cmd] if x is not None)
        if len(parts) < required + 1:
            continue
        try:
            pid  = int(parts[idx_pid])
            ppid = int(parts[idx_ppid])
        except (ValueError, IndexError):
            continue
        cmd = parts[idx_cmd].strip() if idx_cmd is not None and idx_cmd < len(parts) else ""
        ws_bytes = 0
        if idx_ws is not None and idx_ws < len(parts):
            try:
                ws_bytes = int(parts[idx_ws])
            except ValueError:
                pass
        procs[pid] = {
            "pid": pid,
            "ppid": ppid,
            "cmd": cmd,
            "mem_kb": ws_bytes // 1024,
        }

    if not procs:
        return []

    python_pids = set(procs.keys())

    # ---- Step 1: Identify venv-shim + interpreter pairs. ----
    # A "shim" is a python.exe whose cmd contains the venv Scripts path (or is very short)
    # AND has exactly one python.exe child. The child is the "real" interpreter.
    #
    # Key insight: the venv shim path is `.venv\Scripts\python.exe` while the real
    # interpreter is a system Python path (e.g. AppData\Local\Programs\Python\...).
    # We detect shims by looking for the venv Scripts marker in the cmdline.
    #
    # Parent->children map (python.exe only).
    py_children: dict[int, list[int]] = {}
    for pid, info in procs.items():
        ppid = info["ppid"]
        if ppid in python_pids:
            py_children.setdefault(ppid, []).append(pid)

    def _is_venv_shim(cmd: str) -> bool:
        """True if the cmdline looks like a venv activation shim."""
        c = cmd.lower()
        return (
            r".venv\scripts\python" in c
            or "scripts\\python.exe" in c
            or (len(cmd) < 80 and cmd.lower().endswith("python.exe"))
        )

    shim_to_interp: dict[int, int] = {}  # shim_pid -> real_interpreter_pid
    for pid, info in procs.items():
        kids = py_children.get(pid, [])
        # A shim has exactly one python.exe child AND looks like a shim cmdline.
        if len(kids) == 1 and _is_venv_shim(info["cmd"]):
            shim_to_interp[pid] = kids[0]

    # Interpreter pids: the real half of a shim+interp pair.
    interp_pids = set(shim_to_interp.values())
    # Build reverse map: real interpreter -> its shim
    interp_to_shim: dict[int, int] = {v: k for k, v in shim_to_interp.items()}

    # ---- Step 2: Collect runner interpreter PIDs (needed to classify children). ----
    # A runner interpreter has "runner_v2_prod.py" in its cmd.
    runner_interp_pids: set[int] = set()
    for pid, info in procs.items():
        if "runner_v2_prod.py" in info["cmd"]:
            runner_interp_pids.add(pid)

    # ---- Step 3: Build one logical entry per "root" process. ----
    # Root = not an interpreter child of a known shim.
    logical: list[dict] = []
    for pid, info in sorted(procs.items()):
        # Skip if this pid is the interpreter half of a shim+interp pair
        if pid in interp_pids:
            continue

        # Is this a shim that pairs with an interpreter?
        interp_pid = shim_to_interp.get(pid)
        real_pid   = interp_pid if interp_pid else pid
        real_info  = procs.get(real_pid, info)
        cmd        = real_info["cmd"]
        # Also check both the shim and interp cmds for the classifiers
        cmd_combined = info["cmd"] + " " + (procs.get(real_pid, {}).get("cmd", ""))

        # Classify by command line
        if "runner_v2_prod.py" in cmd_combined:
            proc_type = "runner"
            m = re.search(r"--id\s+(gpu_runner_\w+|cpu_runner_\w+)", cmd_combined, re.IGNORECASE)
            if not m:
                m = re.search(r"(gpu_runner_\w+|cpu_runner_\w+)", cmd_combined, re.IGNORECASE)
            name = m.group(1) if m else "runner"
        elif "remote_state_emitter.py" in cmd_combined:
            proc_type = "emitter"
            name = "remote_state_emitter"
        else:
            # Check if this process's shim parent is a runner interpreter.
            # Experiment shim: parent is runner interpreter pid.
            # Experiment interpreter: parent is experiment shim pid.
            parent_pid = info["ppid"]
            parent_is_runner = parent_pid in runner_interp_pids
            proc_type = "experiment_child" if parent_is_runner else "unknown"
            # Extract experiment script name from combined cmd
            m = re.search(r"(exp_wave\d+_[\w.]+\.py|exp_[\w]+\.py)", cmd_combined)
            if m:
                name = m.group(1).replace("\\", "/").split("/")[-1]
            else:
                name = _short_cmd(cmd)

        cmd_short = _short_cmd(cmd)

        logical.append({
            "type": proc_type,
            "name": name,
            "pid": real_pid,
            "shim_pid": pid if interp_pid else None,
            "parent_pid": info["ppid"],
            "cmdline_short": cmd_short,
            "mem_kb": real_info["mem_kb"],
        })

    return logical


def _short_cmd(cmd: str) -> str:
    """Return the last path component of the first script argument in a cmdline."""
    if not cmd:
        return "(empty)"
    # Strip leading python executable path
    cmd = cmd.strip().strip('"')
    # Find the last *.py token
    m = re.search(r'(\S+\.py)', cmd)
    if m:
        p = m.group(1).replace("\\", "/")
        return p.split("/")[-1]
    return cmd[:60]


def _recent_verdicts(n: int = 10) -> list[dict]:
    """Pull the most recent n verdicts from queue.json completed entries.

    Looks at both overnight_queue and remote_cpu_queue for entries with
    status in (completed, failed, killed) and an ended_at timestamp.
    Returns the n most recently-ended entries sorted newest-last.
    """
    all_entries: list[dict] = []
    for queue_name, queue_path in [
        ("overnight_queue", OVERNIGHT_QUEUE),
        ("remote_cpu_queue", CPU_QUEUE),
    ]:
        doc = _load_json(queue_path)
        if not isinstance(doc, dict):
            continue
        exps = doc.get("experiments") or []
        for e in exps:
            if not isinstance(e, dict):
                continue
            status = e.get("status")
            if status not in ("completed", "failed", "killed", "inconclusive"):
                continue
            ended_at = e.get("ended_at") or e.get("completed_at")
            all_entries.append({
                "name": e.get("name"),
                "verdict": status,
                "queue": queue_name,
                "ended_at": ended_at,
                "elapsed_s": e.get("elapsed_s"),
                "verdict_msg": e.get("verdict_msg") or e.get("notes"),
            })

    # Sort by ended_at, newest last; take last n
    def _sort_key(e: dict) -> str:
        return e.get("ended_at") or ""

    all_entries.sort(key=_sort_key)
    return all_entries[-n:]



# ---------------------------------------------------------------------------
# Core snapshot
# ---------------------------------------------------------------------------

def build_snapshot() -> dict:
    now_iso = datetime.now().isoformat(timespec="seconds")

    snapshot = {
        "snapshot_ts": now_iso,
        "queues": {
            "overnight_queue": _queue_entries(OVERNIGHT_QUEUE),
            "remote_cpu_queue": _queue_entries(CPU_QUEUE),
        },
        "runners": {
            "gpu_runner_0": _runner_state_from_heartbeat("gpu_runner_0"),
            "cpu_runner_0": _runner_state_from_heartbeat("cpu_runner_0"),
        },
        "recent_verdicts": _recent_verdicts(10),
        "recent_runner_log_tail": "",
        "logical_processes": _classify_python_procs(),
    }

    return snapshot


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    print(
        f"[remote_state_emitter] starting; writing to {OUTPUT}; poll={POLL_INTERVAL_S}s",
        flush=True,
    )
    while True:
        try:
            snap = build_snapshot()
            write_atomic(OUTPUT, snap)
        except Exception as e:
            # Never crash — just log and keep going
            print(f"[remote_state_emitter] ERROR: {e}", flush=True)
        time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    main()
