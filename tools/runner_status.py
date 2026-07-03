#!/usr/bin/env python
"""runner_status.py — canonical "what's actually running?" command.

Testbed observability deliverable 3 (2026-06-28). Replaces the multi-step SSH +
ps + queue.json + log-tail dance that caused Director to misdiagnose runner
state 4+ times on 2026-06-28.

Usage:
    python d:/AI/hd-instrument/tools/runner_status.py             # local-only
    python d:/AI/hd-instrument/tools/runner_status.py --remote    # + SSH check
    python d:/AI/hd-instrument/tools/runner_status.py --verbose   # + per-cell heartbeats
    python d:/AI/hd-instrument/tools/runner_status.py --json      # machine-readable

Exit codes:
    0 = all healthy
    1 = at least one zombie detected
    2 = at least one expected runner not running

Combines:
    * data/logs/<runner_id>_heartbeat.json files (canonical runner liveness)
    * Local python process list (psutil if available, else tasklist parse)
    * queue.json files (local + SSH-remote)
    * data/exp_<anchor>/_heartbeat.jsonl (per-cell progress)
    * data/recent_landings.jsonl (last 30 min)

Safe to run as a scheduled task every 5min (creates no popup; subprocess.run
of any child uses CREATE_NO_WINDOW on Windows per USER 2026-06-21 audit).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# --- Constants ---------------------------------------------------------------
HEARTBEAT_STALE_S = 60          # runner heartbeat > 60s old -> zombie
CELL_HEARTBEAT_STALE_S = 300    # cell heartbeat > 5min old -> hung-cell flag
RECENT_LANDINGS_WINDOW_S = 1800 # 30 min
DEFAULT_TIMEOUT_S = 14400       # 4h; mirrors runner_v2_prod.py

# remote_state_cache.json staleness threshold. Testbed 2026-07-02: the cache
# went 3 days stale (2026-06-29T10:06 -> 2026-07-02T14:45) when the remote
# emitter died without restart. Detector prints WARNING to alert operators
# reading queue/runner state from a stale file.
REMOTE_CACHE_PATH = REPO / "data" / "remote_state_cache.json"
REMOTE_CACHE_WARN_S = 900       # 15 min; warn threshold Director asked for

LOCAL_QUEUE_DIRS = [
    ("local_cpu_queue", REPO / "data" / "local_cpu_queue"),
]
REMOTE_QUEUE_DIRS = [
    ("remote_cpu_queue", "C:/dev/hd-instrument/data/remote_cpu_queue"),
    ("overnight_queue", "C:/dev/hd-instrument/data/overnight_queue"),
]

# Expected runner_ids that should be alive when --remote is set. If a runner
# in this list is missing entirely, exit 2. Tunable: empty if user wants
# "report whatever is there" mode.
EXPECTED_REMOTE_RUNNERS = ["cpu_runner_0", "gpu_runner_0"]
EXPECTED_LOCAL_RUNNERS = ["cpu_runner_local"]

NO_WINDOW = 0x08000000 if os.name == "nt" else 0


# --- Time helpers ------------------------------------------------------------

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso_utc(s: str | None) -> datetime | None:
    """Tolerant ISO8601 parser: accepts Z suffix, +00:00 suffix, or naive."""
    if not s or not isinstance(s, str):
        return None
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s[:-1]).replace(tzinfo=timezone.utc)
        if "+" in s[10:] or "-" in s[11:]:
            return datetime.fromisoformat(s)
        # naive -> assume UTC (best-effort for legacy heartbeats)
        return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _age_s(iso: str | None) -> float | None:
    dt = _parse_iso_utc(iso)
    if dt is None:
        return None
    return (_now_utc() - dt).total_seconds()


def _fmt_dur(sec: float | None) -> str:
    if sec is None:
        return "?"
    sec = max(0.0, float(sec))
    if sec < 60:
        return f"{sec:.0f}s"
    if sec < 3600:
        m, s = divmod(int(sec), 60)
        return f"{m}m{s}s"
    h, rem = divmod(int(sec), 3600)
    m, _ = divmod(rem, 60)
    return f"{h}h{m}m"


# --- Heartbeat reading -------------------------------------------------------

def _read_json(path: Path) -> dict | None:
    try:
        # errors="replace" guards against the rare partial-write race on the
        # readers' side; atomic-write on the writer side makes that rare but
        # not impossible across SMB/networked FS.
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return None


def discover_local_heartbeats() -> dict[str, dict]:
    """Returns {runner_id: heartbeat_dict_with_age_s_added}.

    Priority: canonical data/logs/<id>_heartbeat.json (post-patch); falls back
    to legacy <queue_dir>/heartbeat.<id>.json so pre-patch runners are still
    visible during the rollout window.
    """
    out: dict[str, dict] = {}
    # Canonical (post-2026-06-28 patch)
    logs_dir = REPO / "data" / "logs"
    if logs_dir.exists():
        for hb_path in logs_dir.glob("*_heartbeat.json"):
            runner_id = hb_path.name[: -len("_heartbeat.json")]
            data = _read_json(hb_path)
            if data is None:
                continue
            data["_source"] = "local"
            data["_path"] = str(hb_path)
            data["_age_s"] = _age_s(data.get("ts_iso") or data.get("ts"))
            out[runner_id] = data
    # Legacy fallback (pre-patch runners): scan known local queue dirs.
    for _, qd in LOCAL_QUEUE_DIRS:
        if not qd.exists():
            continue
        for hb_path in qd.glob("heartbeat.*.json"):
            runner_id = hb_path.name[len("heartbeat."): -len(".json")]
            if runner_id in out:  # canonical already present; skip legacy
                continue
            data = _read_json(hb_path)
            if data is None:
                continue
            data["_source"] = "local"
            data["_path"] = str(hb_path)
            data["_age_s"] = _age_s(data.get("ts_iso") or data.get("ts"))
            data["_legacy_format"] = True
            out[runner_id] = data
    return out


def _ssh_cat(remote_path: str, timeout: int = 15) -> str | None:
    """Best-effort cat-via-SSH; returns None on any failure.

    Uses powershell.exe Get-Content -Raw to avoid Windows-side cat aliases that
    might add trailing newlines / BOM stripping inconsistencies.
    """
    # ssh -T disables pseudo-tty (popup-fix per testbed 2026-06-28: prevents
    # remote conhost.exe allocation on each heartbeat poll).
    cmd = [
        "ssh", "-T", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
        "marsh@home",
        f'powershell -NoProfile -Command "Get-Content -Raw -LiteralPath \\"{remote_path}\\""',
    ]
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, creationflags=NO_WINDOW,
        )
        if out.returncode != 0:
            return None
        return out.stdout
    except (subprocess.TimeoutExpired, OSError):
        return None


def discover_remote_heartbeats() -> dict[str, dict]:
    """SSH-fetch data/logs/<runner_id>_heartbeat.json for known remote runners.

    Falls back to legacy <remote_queue_dir>/heartbeat.<runner_id>.json so
    pre-patch runners are still visible during the rollout window. Per-runner
    queue affinity (cpu_runner_0 -> remote_cpu_queue; gpu_runner_0 ->
    overnight_queue) is hard-coded here; if the convention changes update both.
    """
    out: dict[str, dict] = {}
    legacy_paths = {
        "cpu_runner_0": "C:/dev/hd-instrument/data/remote_cpu_queue/heartbeat.cpu_runner_0.json",
        "gpu_runner_0": "C:/dev/hd-instrument/data/overnight_queue/heartbeat.gpu_runner_0.json",
    }
    for runner_id in EXPECTED_REMOTE_RUNNERS:
        # Try canonical first.
        remote_path = f"C:/dev/hd-instrument/data/logs/{runner_id}_heartbeat.json"
        raw = _ssh_cat(remote_path)
        legacy = False
        if raw is None:
            # Fall back to legacy queue-dir heartbeat (pre-patch runners).
            lp = legacy_paths.get(runner_id)
            if lp:
                raw = _ssh_cat(lp)
                legacy = True
                remote_path = lp
        if raw is None:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        data["_source"] = "remote"
        data["_path"] = f"remote:{remote_path}"
        data["_age_s"] = _age_s(data.get("ts_iso") or data.get("ts"))
        if legacy:
            data["_legacy_format"] = True
        out[runner_id] = data
    return out


# --- Queue reading -----------------------------------------------------------

def _normalize_entries(data) -> list:
    if isinstance(data, dict):
        return data.get("experiments") or data.get("entries") or []
    if isinstance(data, list):
        return data
    return []


def read_local_queue(queue_dir: Path) -> list:
    qf = queue_dir / "queue.json"
    if not qf.exists():
        return []
    data = _read_json(qf)
    return _normalize_entries(data) if data else []


def read_remote_queue(remote_dir: str) -> list:
    raw = _ssh_cat(f"{remote_dir}/queue.json")
    if raw is None:
        return []
    try:
        return _normalize_entries(json.loads(raw))
    except json.JSONDecodeError:
        return []


def queue_stats(entries: list) -> dict:
    pending = [e for e in entries if e.get("status") == "pending"]
    running = [e for e in entries if e.get("status") == "running"]
    serial_eta_s = sum(int(e.get("timeout_s") or DEFAULT_TIMEOUT_S)
                       for e in pending + running)
    return {
        "pending": len(pending),
        "running": len(running),
        "running_entries": running,
        "serial_eta_s": serial_eta_s,
    }


# --- Per-cell heartbeat (from _heartbeat.jsonl) ------------------------------

def read_cell_heartbeat(anchor: str) -> dict | None:
    """Returns the LAST _heartbeat.jsonl row for a given anchor, with age.

    SH-4 fallback: also try `data/exp_exp_<anchor>/_heartbeat.jsonl` when the
    canonical single-prefix dir is empty; runner sometimes writes double-prefix
    when the queue entry name already begins with 'exp_' (root cause in
    experiments/_seed_checkpoint.get_output_dir). Testbed 2026-07-03 fleet audit.
    """
    p = REPO / "data" / f"exp_{anchor}" / "_heartbeat.jsonl"
    if not p.exists():
        # SH-4 double-prefix fallback
        p_dbl = REPO / "data" / f"exp_exp_{anchor}" / "_heartbeat.jsonl"
        if p_dbl.exists():
            p = p_dbl
        else:
            return None
    try:
        # Tail-only read so we don't load megabytes of history.
        with p.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 4096), os.SEEK_SET)
            tail = f.read().decode("utf-8", errors="replace")
    except OSError:
        return None
    last = None
    for line in tail.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            last = json.loads(line)
        except json.JSONDecodeError:
            continue
    if last is None:
        return None
    last["_age_s"] = _age_s(last.get("ts_iso"))
    return last


# --- Process liveness fallback ----------------------------------------------

def pid_alive(pid: int) -> bool:
    """Best-effort: ctypes OpenProcess on Windows; os.kill(pid,0) elsewhere."""
    if pid <= 0:
        return False
    try:
        if os.name == "nt":
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            h = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if h:
                ctypes.windll.kernel32.CloseHandle(h)
                return True
            return False
        else:
            os.kill(pid, 0)
            return True
    except (OSError, AttributeError, ValueError):
        return False


# --- Recent landings ---------------------------------------------------------

def read_recent_landings(window_s: float = RECENT_LANDINGS_WINDOW_S) -> list:
    p = REPO / "data" / "recent_landings.jsonl"
    if not p.exists():
        return []
    try:
        with p.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return []
    out = []
    for line in lines[-200:]:  # cap tail-read
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        age = _age_s(row.get("ts_iso") or row.get("ts"))
        if age is None or age <= window_s:
            row["_age_s"] = age
            out.append(row)
    return out


# --- Aggregation -------------------------------------------------------------

def classify_runner(hb: dict) -> str:
    """Returns one of: ALIVE | STALE | ZOMBIE.

    ALIVE   = heartbeat < HEARTBEAT_STALE_S old AND (if local) pid alive
    STALE   = heartbeat 60s..5min old (transient; check again in 1min)
    ZOMBIE  = heartbeat > 5min old OR pid recorded but dead (local only)
    """
    age = hb.get("_age_s")
    if age is None:
        return "ZOMBIE"  # unparseable ts = treat as dead
    # Local: cross-check PID. Remote: trust the heartbeat (we can't query PID).
    if hb.get("_source") == "local":
        try:
            pid = int(hb.get("pid") or 0)
        except (TypeError, ValueError):
            pid = 0
        if pid > 0 and not pid_alive(pid):
            return "ZOMBIE"
    if age <= HEARTBEAT_STALE_S:
        return "ALIVE"
    if age <= 5 * HEARTBEAT_STALE_S:
        return "STALE"
    return "ZOMBIE"


def assemble_report(include_remote: bool, verbose: bool) -> dict:
    runners: dict[str, dict] = {}
    runners.update(discover_local_heartbeats())
    if include_remote:
        runners.update(discover_remote_heartbeats())

    # Expected runners that have NO heartbeat at all
    expected = list(EXPECTED_LOCAL_RUNNERS)
    if include_remote:
        expected.extend(EXPECTED_REMOTE_RUNNERS)
    missing = [r for r in expected if r not in runners]

    # Per-runner classification
    rows = []
    for runner_id, hb in sorted(runners.items()):
        verdict = classify_runner(hb)
        cell = hb.get("current_cell") or hb.get("current")
        cell_hb = read_cell_heartbeat(cell) if (verbose and cell) else None
        rows.append({
            "runner_id": runner_id,
            "verdict": verdict,
            "hb": hb,
            "cell_hb": cell_hb,
        })

    # Queues
    local_q = []
    for label, qd in LOCAL_QUEUE_DIRS:
        entries = read_local_queue(qd)
        local_q.append((label, queue_stats(entries)))
    remote_q = []
    if include_remote:
        for label, rd in REMOTE_QUEUE_DIRS:
            entries = read_remote_queue(rd)
            remote_q.append((label, queue_stats(entries)))

    # Zombies = queue entries `running` whose owning runner is ZOMBIE OR not
    # represented in heartbeats at all.
    alive_runner_ids = {
        r["runner_id"] for r in rows
        if r["verdict"] in ("ALIVE", "STALE")
    }
    zombies = []
    for label, stats in local_q + remote_q:
        for ent in stats["running_entries"]:
            owner = ent.get("claimed_by")
            if owner and owner not in alive_runner_ids:
                zombies.append({
                    "queue": label,
                    "anchor": ent.get("name"),
                    "claimed_by": owner,
                    "started_at": ent.get("started_at"),
                })

    landings = read_recent_landings()

    return {
        "ts_iso": _now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runners": rows,
        "missing_runners": missing,
        "local_queues": local_q,
        "remote_queues": remote_q,
        "zombies": zombies,
        "recent_landings": landings,
        "remote_cache_staleness": check_remote_cache_staleness(),
    }


def check_remote_cache_staleness() -> dict:
    """Check remote_state_cache.json snapshot_ts age.

    Returns dict with keys:
        snapshot_ts: str | None      the ISO ts in the file (naive local time
                                      from remote_state_emitter.py; may be
                                      Eastern/UTC depending on remote clock)
        age_s: float | None          seconds since snapshot_ts (naive-compared
                                      to datetime.now(); accurate when local
                                      and remote clocks share tz, else biased
                                      by tz offset; 15min warn floor is well
                                      above any single-tz offset so safe)
        stale: bool                  True iff age_s > REMOTE_CACHE_WARN_S
                                      or snapshot_ts unparseable
        exists: bool
    """
    if not REMOTE_CACHE_PATH.is_file():
        return {"snapshot_ts": None, "age_s": None, "stale": True, "exists": False}
    try:
        d = json.loads(REMOTE_CACHE_PATH.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return {"snapshot_ts": None, "age_s": None, "stale": True, "exists": True}
    snap = d.get("snapshot_ts")
    if not isinstance(snap, str):
        return {"snapshot_ts": None, "age_s": None, "stale": True, "exists": True}
    try:
        # Emitter writes naive isoformat (see remote_state_emitter.build_snapshot).
        # Strip Z if present, compare with datetime.now() (also naive local).
        ts_str = snap[:-1] if snap.endswith("Z") else snap
        ts = datetime.fromisoformat(ts_str)
        if ts.tzinfo is not None:
            ts = ts.replace(tzinfo=None)
        age_s = (datetime.now() - ts).total_seconds()
    except (ValueError, TypeError):
        return {"snapshot_ts": snap, "age_s": None, "stale": True, "exists": True}
    return {
        "snapshot_ts": snap,
        "age_s": age_s,
        "stale": age_s > REMOTE_CACHE_WARN_S,
        "exists": True,
    }


# --- Rendering ---------------------------------------------------------------

def render_report(report: dict, verbose: bool) -> str:
    L = []
    # Bridge-cache staleness banner: fires above the runner section so callers
    # who read queue/runner state from data/remote_state_cache.json see the
    # WARNING before trusting downstream numbers. Testbed 2026-07-02 detector.
    rcs = report.get("remote_cache_staleness") or {}
    if rcs.get("stale"):
        age = rcs.get("age_s")
        if not rcs.get("exists"):
            L.append("!!! WARNING: data/remote_state_cache.json is MISSING - queue/runner data UNAVAILABLE (remote emitter dead or SCP broken)")
        elif age is None:
            L.append("!!! WARNING: data/remote_state_cache.json has unparseable snapshot_ts; treat as STALE")
        else:
            mins = age / 60.0
            L.append(f"!!! WARNING: data/remote_state_cache.json is STALE ({mins:.1f}m old; snapshot_ts={rcs.get('snapshot_ts')}); remote emitter may be dead; queue/runner numbers below are pre-stale-file and should NOT be trusted")
        L.append("")
    L.append(f"=== RUNNER LIVENESS (as of {report['ts_iso']}) ===")
    if not report["runners"] and not report["missing_runners"]:
        L.append("(no runners discovered; expected ones may not be configured yet)")
    for row in report["runners"]:
        hb = row["hb"]
        verdict = row["verdict"]
        age = hb.get("_age_s")
        age_str = f"{age:.0f}s" if age is not None else "?"
        try:
            pid = int(hb.get("pid") or 0)
        except (TypeError, ValueError):
            pid = 0
        uptime = hb.get("runner_uptime_s")
        uptime_str = _fmt_dur(uptime) if uptime is not None else "?"
        legacy_tag = " [legacy-hb-format; needs runner patch]" if hb.get("_legacy_format") else ""
        L.append(f"{row['runner_id']:<20} {verdict:<8} (pid {pid}; heartbeat {age_str} old; up {uptime_str}){legacy_tag}")
    for runner_id in report["missing_runners"]:
        L.append(f"{runner_id:<20} NOT_RUNNING (no heartbeat file found)")

    L.append("")
    L.append("=== CURRENTLY EXECUTING ===")
    any_running = False
    for row in report["runners"]:
        hb = row["hb"]
        cell = hb.get("current_cell") or hb.get("current")
        if not cell or hb.get("status") not in ("running", "running_cell"):
            continue
        any_running = True
        cell_elapsed = hb.get("current_cell_elapsed_s")
        cell_elapsed_str = _fmt_dur(cell_elapsed)
        L.append(f"{row['runner_id']}: {cell} (started {cell_elapsed_str} ago)")
        cell_hb = row.get("cell_hb")
        if cell_hb is not None:
            cell_hb_age = cell_hb.get("_age_s")
            unit_idx = cell_hb.get("unit_idx")
            total = cell_hb.get("total_units")
            unit_str = f"unit_idx={unit_idx}/{total}" if total else f"unit_idx={unit_idx}"
            L.append(f"  - cell-heartbeat: {cell_hb_age:.0f}s old ({unit_str})"
                     if cell_hb_age is not None else
                     f"  - cell-heartbeat: present (ts unparseable) ({unit_str})")
        elif verbose:
            L.append("  - cell-heartbeat: NONE (cell pre-§13 or not yet emitting)")
    if not any_running:
        L.append("(none)")

    L.append("")
    L.append("=== QUEUE STATE ===")
    for label, stats in report["local_queues"] + report["remote_queues"]:
        eta = _fmt_dur(stats["serial_eta_s"])
        L.append(f"{label}: {stats['running']} running + {stats['pending']} pending ({eta} serial worst-case)")

    L.append("")
    L.append("=== ZOMBIES DETECTED ===")
    if report["zombies"]:
        for z in report["zombies"]:
            L.append(f"  [{z['queue']}] {z['anchor']} (claimed_by={z['claimed_by']}; started_at={z['started_at']})")
        L.append("  -> recommend: see orchestrator.md RUNNER-ZOMBIE DETECTION + RECOVERY section to clear")
    else:
        L.append("[none]")

    L.append("")
    L.append("=== RECENT LANDINGS (last 30 min) ===")
    if report["recent_landings"]:
        for r in report["recent_landings"][-12:]:
            anchor = r.get("anchor") or r.get("name") or "?"
            verdict = r.get("verdict") or r.get("verdict_tag") or "?"
            ts = r.get("ts_iso") or r.get("ts") or "?"
            L.append(f"  {anchor}: {verdict} [{ts}]")
    else:
        L.append("(none in window)")

    return "\n".join(L)


# --- Exit-code computation --------------------------------------------------

def compute_exit_code(report: dict) -> int:
    if report["zombies"]:
        return 1
    if report["missing_runners"]:
        return 2
    for row in report["runners"]:
        if row["verdict"] == "ZOMBIE":
            return 1
    return 0


# --- CLI --------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--remote", action="store_true",
                    help="Also probe SSH-remote runners + queues (marsh@home)")
    ap.add_argument("--verbose", action="store_true",
                    help="Include per-cell _heartbeat.jsonl tail under each executing cell")
    ap.add_argument("--json", action="store_true",
                    help="Emit machine-readable JSON instead of one-page summary")
    args = ap.parse_args()

    report = assemble_report(include_remote=args.remote, verbose=args.verbose)

    if args.json:
        # Strip non-serializable internal fields for cleaner JSON consumers
        def _clean(o):
            if isinstance(o, dict):
                return {k: _clean(v) for k, v in o.items()
                        if not (isinstance(k, str) and k.startswith("_path"))}
            if isinstance(o, list):
                return [_clean(x) for x in o]
            return o
        print(json.dumps(_clean(report), indent=2, default=str))
    else:
        print(render_report(report, verbose=args.verbose))

    return compute_exit_code(report)


if __name__ == "__main__":
    sys.exit(main())
