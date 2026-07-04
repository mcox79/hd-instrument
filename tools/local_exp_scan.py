"""Local substrate-experiment subprocess scanner (popup-free, stdlib-only).

WHY THIS EXISTS (testbed 2026-07-04): the dashboard + inflight_monitor were
QUEUE/RUNNER-centric and blind to direct agent-launched python subprocesses that
bypass the queue. The priority work (R1 encoder validation
`experiments/exp_encoder_migration_step1b_v3_..._core.py`, and Part B sweeps in
the session scratchpad) runs as LOCAL direct subprocesses on this laptop, so the
dashboard read "all idle" while training was actively burning CPU. The remote
emitter's logical_processes only covers the REMOTE box; local direct runs never
appeared anywhere. This module closes that structural blindness.

It is imported by BOTH tools/dashboard/poller.py (surfaces in /api/system
logical_processes) and tools/inflight_monitor.py (surfaces in the pane), so the
in-flight priority experiment shows as RUNNING with its cell name, elapsed time,
memory, and device -- in both surfaces, and independently of whether the remote
feed or dashboard is alive.

Design notes:
  * WMIC with CREATE_NO_WINDOW -- popup-free (USER 2026-06-28 windowless mandate).
    Same discipline as remote_state_emitter._classify_python_procs.
  * Right-anchored CSV parse -- CommandLine can contain commas; the trailing
    numeric columns (CreationDate/ParentProcessId/ProcessId/WorkingSetSize) are
    comma-free, so we read them from the end and rejoin CommandLine. Robust to
    commas the emitter's fixed-index parser would mis-column.
  * venv shim+interp grouping -- on Windows a venv launch is TWO pids (the
    `.venv\\Scripts\\python.exe` shim + the real interpreter child). We collapse
    the pair to one logical entry so an experiment isn't double-counted.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
_REPO = Path(__file__).resolve().parent.parent
_DATA = _REPO / "data"

# A direct-launched substrate experiment cell: experiments/exp_*.py
_EXP_CELL_RE = re.compile(r"experiments[\\/](exp_[\w.\-]+\.py)", re.IGNORECASE)
# A scratchpad training/diagnostic script (agent-launched, queue-bypassing).
_SCRATCH_PY_RE = re.compile(r"[\\/]scratchpad[\\/]([\w.\-]+\.py)", re.IGNORECASE)
# Scratchpad basenames that look like real experiment/training/eval work (vs a
# throwaway helper) -- keeps the signal high and avoids flagging transient tools.
_SCRATCH_KEEP_RE = re.compile(
    r"(diag_|train|sweep|_core|exp_|part[ab]|encoder|probe|eval|validat|fit|distil|bench)",
    re.IGNORECASE,
)
# Infra / tooling python we must NEVER classify as an experiment.
_INFRA_MARKERS = (
    "runner_v2_prod.py", "remote_state_emitter.py", "heartbeat_watchdog.py",
    "landing_notifier.py", "inflight_monitor.py", "supervisor.py", "uvicorn",
    "server:app", "director_kb", "substrate_capabilit", "session_watchdog",
    "notes_monitor.py", "monitor_arm.py", "testbed_red_watcher.py",
    "local_exp_scan.py", "substrate_durability", "substrate_snapshot",
    "emit_cadence_signal.py", "hd_session_watchdog.py",
)


def _is_venv_shim(cmd: str) -> bool:
    c = cmd.lower()
    return (
        r".venv\scripts\python" in c
        or "scripts\\python.exe" in c
        or "scripts\\pythonw.exe" in c
        or (len(cmd) < 80 and c.endswith(("python.exe", "pythonw.exe")))
    )


def _elapsed_s(creation_date: str) -> float | None:
    """WMIC CreationDate (YYYYMMDDHHMMSS.ffffff+ZZZ) -> seconds since start."""
    if not creation_date or len(creation_date) < 14:
        return None
    try:
        dt = datetime.strptime(creation_date[:14], "%Y%m%d%H%M%S")
        return max(0.0, (datetime.now() - dt).total_seconds())
    except (ValueError, TypeError):
        return None


def _cell_name(cmd: str) -> tuple[str, str] | None:
    """(name, source) if cmd is a substrate experiment; else None."""
    low = cmd.lower()
    if any(m in low for m in _INFRA_MARKERS):
        return None
    m = _EXP_CELL_RE.search(cmd)
    if m:
        return m.group(1), "experiments"
    m = _SCRATCH_PY_RE.search(cmd)
    if m and _SCRATCH_KEEP_RE.search(m.group(1)):
        return m.group(1), "scratchpad"
    return None


def _args_summary(cmd: str) -> dict:
    out: dict = {}
    md = re.search(r"--device\s+(\w+)", cmd)
    if md:
        out["device"] = md.group(1)
    ms = re.search(r"--seed\s+(\d+)", cmd)
    if ms:
        out["seed"] = int(ms.group(1))
    for tier in ("--smoke", "--mid", "--full"):
        if tier in cmd:
            out["tier"] = tier.lstrip("-")
            break
    return out


def _wmic_python_procs() -> list[dict]:
    """[{cmd, ppid, pid, mem_kb, creation}] for all local python/pythonw procs."""
    try:
        # timeout kept below the caller's wall-clock budget so a wedged WMI service
        # self-cleans within the tick (the caller also caps this via _bounded).
        out = subprocess.check_output(
            ["wmic", "process", "where",
             "name='python.exe' or name='pythonw.exe'",
             "get", "CommandLine,CreationDate,ParentProcessId,ProcessId,WorkingSetSize",
             "/format:csv"],
            stderr=subprocess.DEVNULL, timeout=4, text=True,
            encoding="utf-8", errors="replace", creationflags=_NO_WINDOW,
        )
    except Exception:
        return []
    rows = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if len(rows) < 2:
        return []
    header = [h.strip().lower() for h in rows[0].split(",")]
    # CommandLine is the only comma-bearing field; everything after it is fixed.
    try:
        cmd_i = header.index("commandline")
    except ValueError:
        return []
    n_trail = len(header) - (cmd_i + 1)  # columns after CommandLine (all comma-free)
    trail_names = header[cmd_i + 1:]
    procs: list[dict] = []
    for row in rows[1:]:
        parts = row.split(",")
        if len(parts) < cmd_i + 1 + n_trail:
            continue
        trailing = parts[-n_trail:] if n_trail else []
        cmd = ",".join(parts[cmd_i:len(parts) - n_trail]).strip()
        field = dict(zip(trail_names, [t.strip() for t in trailing]))
        try:
            pid = int(field.get("processid", ""))
            ppid = int(field.get("parentprocessid", ""))
        except (ValueError, TypeError):
            continue
        try:
            mem_kb = int(field.get("workingsetsize", "0") or 0) // 1024
        except ValueError:
            mem_kb = 0
        procs.append({"cmd": cmd, "pid": pid, "ppid": ppid,
                      "mem_kb": mem_kb, "creation": field.get("creationdate", "")})
    return procs


def _last_jsonl_obj(path: Path) -> dict | None:
    """Last complete JSON object in a .jsonl file (tail-read, no full load)."""
    try:
        with path.open("rb") as f:
            f.seek(0, 2)
            size = f.tell()
            chunk = min(size, 8192)
            f.seek(size - chunk)
            data = f.read().decode("utf-8", errors="replace")
    except OSError:
        return None
    # Iterate newest-first; the last full line is complete even if the leading
    # line in the tail chunk was cut mid-record.
    for line in reversed(data.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _heartbeat_progress(name: str, args: dict) -> dict:
    """{progress_pct, unit_idx, total_units, phase, eta_s} from the experiment's
    data/<anchor>_<tier>/_heartbeat.jsonl last line. Empty dict if none/unparseable.

    Anchor dir maps from the cell name the same way the runner names its dir:
    name minus the `_core.py` (or `.py`) suffix, `exp_` prefix retained, plus the
    tier suffix (_mid / _smoke / '' for full). We also try the exp_-stripped and
    other-tier variants so a mislabeled tier still resolves.
    """
    stem = name[:-3] if name.lower().endswith(".py") else name
    if stem.endswith("_core"):
        stem = stem[:-5]
    tier = (args or {}).get("tier")
    tier_suffix = {"mid": "_mid", "smoke": "_smoke"}.get(tier, "")
    bases = [stem]
    if stem.startswith("exp_"):
        bases.append(stem[4:])
    cands: list[str] = []
    for b in bases:
        if tier_suffix:
            cands.append(b + tier_suffix)
        cands += [b, b + "_smoke", b + "_mid"]
    seen: set[str] = set()
    hb: dict | None = None
    for c in cands:
        if c in seen:
            continue
        seen.add(c)
        p = _DATA / c / "_heartbeat.jsonl"
        if p.is_file():
            hb = _last_jsonl_obj(p)
            if hb is not None:
                break
    if not isinstance(hb, dict):
        return {}
    ui = hb.get("unit_idx")
    tu = hb.get("total_units")
    extra = hb.get("extra") if isinstance(hb.get("extra"), dict) else {}
    phase = extra.get("phase")
    hb_elapsed = hb.get("elapsed_s")
    out: dict = {}
    if isinstance(ui, (int, float)):
        out["unit_idx"] = int(ui)
    if isinstance(tu, (int, float)):
        out["total_units"] = int(tu)
    if isinstance(ui, (int, float)) and isinstance(tu, (int, float)) and tu:
        out["progress_pct"] = round(max(0.0, min(100.0, 100.0 * ui / tu)), 1)
    if phase:
        out["phase"] = str(phase)
    if (isinstance(hb_elapsed, (int, float)) and isinstance(ui, (int, float))
            and isinstance(tu, (int, float)) and ui > 0 and tu > ui):
        out["eta_s"] = round(hb_elapsed * (tu - ui) / ui, 1)
    return out


def scan_local_experiments() -> list[dict]:
    """Logical local substrate-experiment subprocesses (queue-bypassing direct runs).

    Returns entries: {type:"experiment", source, name, pid, shim_pid, parent_pid,
                      cmdline_short, mem_kb, elapsed_s, args, local:True}
    Empty list on any error (never raises -- callers merge into a live snapshot).
    """
    procs = _wmic_python_procs()
    if not procs:
        return []
    by_pid = {p["pid"]: p for p in procs}
    pyset = set(by_pid)
    # parent -> python children
    kids: dict[int, list[int]] = {}
    for p in procs:
        if p["ppid"] in pyset:
            kids.setdefault(p["ppid"], []).append(p["pid"])
    # shim -> real interpreter (shim = venv-shim cmd with exactly one python child)
    shim_to_interp: dict[int, int] = {}
    for p in procs:
        kk = kids.get(p["pid"], [])
        if len(kk) == 1 and _is_venv_shim(p["cmd"]):
            shim_to_interp[p["pid"]] = kk[0]
    interp_pids = set(shim_to_interp.values())

    out: list[dict] = []
    for p in sorted(procs, key=lambda x: x["pid"]):
        if p["pid"] in interp_pids:
            continue  # counted via its shim
        interp = shim_to_interp.get(p["pid"])
        real = by_pid.get(interp, p) if interp else p
        combined = p["cmd"] + " " + (real["cmd"] if interp else "")
        hit = _cell_name(combined)
        if not hit:
            continue
        name, source = hit
        el = _elapsed_s(real.get("creation", ""))
        args = _args_summary(combined)
        entry = {
            "type": "experiment",
            "source": source,
            "name": name,
            "pid": real["pid"],
            "shim_pid": p["pid"] if interp else None,
            "parent_pid": p["ppid"],
            "cmdline_short": name,
            "mem_kb": real["mem_kb"],
            "elapsed_s": round(el, 1) if el is not None else None,
            "args": args,
            "local": True,
        }
        # Progress/phase from the run's heartbeat (blank if no heartbeat file).
        try:
            entry.update(_heartbeat_progress(name, args))
        except Exception:
            pass
        out.append(entry)
    return out


if __name__ == "__main__":
    import json
    exps = scan_local_experiments()
    print(f"detected {len(exps)} local experiment subprocess(es):")
    print(json.dumps(exps, indent=2, default=str))
