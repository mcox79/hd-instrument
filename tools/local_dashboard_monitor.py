"""Local dashboard monitor: snapshot remote experiment state to a local JSON file.

Polls marsh@home every POLL_INTERVAL_S via the read-only SSH client in
tools/dashboard, then atomically writes a JSON snapshot to
data/local_dashboard_snapshot.json so other sessions can read remote state
cheaply (no SSH on their side).

Usage:
    python tools/local_dashboard_monitor.py            # run forever
    python tools/local_dashboard_monitor.py --once     # single snapshot then exit
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "dashboard"))
from ssh_client import ReadOnlySSH  # noqa: E402

SNAPSHOT_PATH = ROOT / "data" / "local_dashboard_snapshot.json"
POLL_INTERVAL_S = 5.0  # 2026-05-23 U1 upgrade: was 30.0; orchestrator dispatch needs lower verdict-detection latency. Each poll is one small SSH read; 5s gives ~7s end-to-end vs ~32s before.
HEARTBEAT_ALIVE_WINDOW_S = 90.0
LOG_TAIL_LINES = 100
SESSION_EVENTS_TAIL_LINES = 30
RECENT_VERDICTS_LIMIT = 50

QUEUES: dict[str, dict[str, str]] = {
    "gpu": {
        "dir": r"C:\dev\hd-instrument\data\overnight_queue",
        "runner_id": "gpu_runner_0",
    },
    "cpu": {
        "dir": r"C:\dev\hd-instrument\data\remote_cpu_queue",
        "runner_id": "cpu_runner_0",
    },
}

DATA_DIR_FWD = "C:/dev/hd-instrument/data"


def _parse_json(text: str | None) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError, TypeError):
        return None


def _heartbeat_alive(hb: Any, now: datetime) -> bool:
    if not isinstance(hb, dict):
        return False
    ts = hb.get("ts")
    if not isinstance(ts, str):
        return False
    try:
        hb_dt = datetime.fromisoformat(ts)
    except ValueError:
        return False
    if hb_dt.tzinfo is not None:
        hb_dt = hb_dt.replace(tzinfo=None)
    age_s = (now - hb_dt).total_seconds()
    return -5.0 < age_s < HEARTBEAT_ALIVE_WINDOW_S


def _recent_log_lines(log_text: str | None, n: int = 5) -> list[str]:
    if not log_text:
        return []
    matched = [
        ln.rstrip()
        for ln in log_text.splitlines()
        if " START " in ln or " DONE " in ln or " FAIL " in ln
    ]
    return matched[-n:]


def _queue_names_by_status(queue_doc: Any) -> tuple[list[str], list[str], int]:
    if not isinstance(queue_doc, dict):
        return [], [], 0
    exps = queue_doc.get("experiments") or []
    pending = [e.get("name") for e in exps if isinstance(e, dict) and e.get("status") == "pending"]
    running = [e.get("name") for e in exps if isinstance(e, dict) and e.get("status") == "running"]
    pending = [p for p in pending if isinstance(p, str)]
    running = [r for r in running if isinstance(r, str)]
    return pending, running, len(pending)


def _atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, path)


def _build_cmds() -> list[tuple[str, str]]:
    cmds: list[tuple[str, str]] = []
    for label, info in QUEUES.items():
        qdir = info["dir"]
        rid = info["runner_id"]
        cmds.append((f"{label}_heartbeat", f"type {qdir}\\heartbeat.{rid}.json"))
        cmds.append((f"{label}_queue", f"type {qdir}\\queue.json"))
        cmds.append((
            f"{label}_log_tail",
            f'powershell -Command "Get-Content {qdir}\\queue.{rid}.log -Tail {LOG_TAIL_LINES}"',
        ))
        cmds.append((
            f"{label}_paused",
            f'powershell -Command "Get-ChildItem {qdir}\\PAUSED -ErrorAction SilentlyContinue"',
        ))
    cmds.append((
        "session_events_tail",
        f'powershell -Command "Get-Content C:\\dev\\hd-instrument\\data\\session_events.jsonl -Tail {SESSION_EVENTS_TAIL_LINES}"',
    ))
    return cmds


# Parses one file row from `Get-ChildItem -Recurse -Filter metrics.json` default
# output. Example: "-a----         5/18/2026  11:18 AM           7477 metrics.json"
# Capture groups: mode, M/D/YYYY, H:MM, AM/PM, size, name.
_PS_FILE_ROW = re.compile(
    r"^\s*-[arhsl-]+\s+"
    r"(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})\s+(AM|PM)\s+"
    r"\d+\s+metrics\.json\s*$"
)


def _parse_pwsh_recurse_listing(text: str, root_norm: str) -> list[tuple[float, str, str]]:
    """Parse `Get-ChildItem -Recurse -Filter metrics.json` output into
    (mtime, exp_name_without_prefix, full_path) tuples.

    Format (US locale):
        Directory: C:\\dev\\hd-instrument\\data\\exp_NAME
        <blank>
        Mode                 LastWriteTime         Length Name
        ----                 -------------         ------ ----
        -a----         5/18/2026  11:18 AM           7477 metrics.json

    The cap_map / runner code uses US date format on the workstation; if the
    machine ever switches locale this parser would need updating.
    """
    out: list[tuple[float, str, str]] = []
    current_dir: str | None = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("Directory:"):
            current_dir = s[len("Directory:"):].strip()
            continue
        if current_dir is None:
            continue
        m = _PS_FILE_ROW.match(line)
        if not m:
            continue
        date_str, time_str, ampm = m.group(1), m.group(2), m.group(3)
        try:
            dt = datetime.strptime(f"{date_str} {time_str} {ampm}", "%m/%d/%Y %I:%M %p")
        except ValueError:
            continue
        # current_dir on remote uses Windows backslashes, e.g.
        #   C:\dev\hd-instrument\data\exp_NAME
        # We need the exp_NAME for the verdict label.
        last = current_dir.rsplit("\\", 1)[-1]
        if not last.startswith("exp_"):
            continue
        full_path = f"{root_norm}/{last}/metrics.json"
        out.append((dt.timestamp(), last[len("exp_"):], full_path))
    return out


def _fetch_recent_verdicts(ssh: ReadOnlySSH, limit: int) -> list[dict]:
    """Find the N most recently modified exp_*/metrics.json files and extract
    verdict-relevant fields. Returns [] on any toplevel failure.

    Mechanism: a single PowerShell `Get-ChildItem -Recurse` call returns all
    paths + mtimes in one round-trip; we parse client-side, sort, and SFTP-read
    only the top-N contents. Costs roughly 1-2 s for the PS call + ~5 s for N
    sequential reads — well inside the 30 s polling budget.

    History:
      v1 (2026-05-21): stat every metrics.json via SFTP — ~8 s at 210 dirs.
      v2 (2026-05-21): dir-mtime optimization to top-30 candidates — ~2 s,
        but lost recent verdicts when their parent dir's mtime didn't bump
        on an in-place overwrite (audit 2026-05-23 caught the leak at 752
        dirs).
      v3 attempt (2026-05-23): parallel SFTP stat via multiple SFTPClients
        on shared transport — hung (paramiko serializes message dispatch
        at the transport layer; opening N SFTPClients does not actually
        parallelize SSH I/O).
      v4 (this code): PowerShell Get-ChildItem -Recurse + parse — single
        round-trip, locale-dependent parser. Robust at current scale.
    """
    cmd = (
        f'powershell -Command "Get-ChildItem C:\\dev\\hd-instrument\\data '
        f'-Recurse -Filter metrics.json -Force"'
    )
    try:
        results = ssh.run_parallel([cmd], tolerate_errors=True)
    except Exception:
        return []
    text = results[0] if results else None
    if not text:
        return []

    candidates = _parse_pwsh_recurse_listing(text, DATA_DIR_FWD)

    candidates.sort(key=lambda x: x[0], reverse=True)
    out: list[dict] = []
    for mtime, name, mpath in candidates[:limit]:
        try:
            text = ssh.sftp_read_text(mpath)
        except Exception:
            continue
        parsed = _parse_json(text)
        if not isinstance(parsed, dict):
            continue
        out.append({
            "name": name,
            "verdict": parsed.get("verdict"),
            "verdict_msg": parsed.get("verdict_msg"),
            "elapsed_s": parsed.get("elapsed_s"),
            "mtime": mtime,
            "mtime_iso": datetime.fromtimestamp(mtime).isoformat(timespec="seconds"),
        })
    return out


def _build_data(ssh: ReadOnlySSH) -> dict[str, Any]:
    """Pull all remote state and return a dict with the data-bearing fields.

    Raises on SSH/connectivity failure (caller decides what to write).
    """
    keyed = _build_cmds()
    results = ssh.run_parallel([c for _, c in keyed], tolerate_errors=True)
    by_key = {k: r for (k, _), r in zip(keyed, results)}

    now = datetime.now()
    data: dict[str, Any] = {"data_ts": now.isoformat(timespec="seconds")}

    for label in QUEUES:
        hb = _parse_json(by_key.get(f"{label}_heartbeat"))
        qd = _parse_json(by_key.get(f"{label}_queue"))
        log_text = by_key.get(f"{label}_log_tail")
        paused_out = by_key.get(f"{label}_paused")
        pending, running, pending_count = _queue_names_by_status(qd)
        data[label] = {
            "heartbeat": hb,
            "alive": _heartbeat_alive(hb, now),
            "paused": bool(paused_out and paused_out.strip()),
            "current": (hb.get("current") if isinstance(hb, dict) else None),
            "recent_log_lines": _recent_log_lines(log_text, n=5),
            "queue_pending": pending,
            "queue_running": running,
            "queue_pending_count": pending_count,
        }

    data["recent_verdicts"] = _fetch_recent_verdicts(ssh, RECENT_VERDICTS_LIMIT)

    events_text = by_key.get("session_events_tail") or ""
    data["recent_session_events"] = [
        ln for ln in events_text.splitlines() if ln.strip()
    ][-SESSION_EVENTS_TAIL_LINES:]

    return data


def _empty_data() -> dict[str, Any]:
    """Shape-stable placeholder for the case where no successful poll has happened yet."""
    empty_queue = {
        "heartbeat": None,
        "alive": False,
        "paused": False,
        "current": None,
        "recent_log_lines": [],
        "queue_pending": [],
        "queue_running": [],
        "queue_pending_count": 0,
    }
    return {
        "data_ts": None,
        "gpu": dict(empty_queue),
        "cpu": dict(empty_queue),
        "recent_verdicts": [],
        "recent_session_events": [],
    }


def _log_stderr(msg: str) -> None:
    sys.stderr.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")
    sys.stderr.flush()


class _MonitorState:
    """Holds the last good data + rolling health so we can keep serving useful
    data through transient SSH failures rather than overwriting with a sentinel.
    """

    def __init__(self) -> None:
        self.last_good_data: dict[str, Any] = _empty_data()
        self.last_poll_ok_ts: datetime | None = None
        self.last_poll_attempted_ts: datetime | None = None
        self.consecutive_failures: int = 0
        self.total_failures: int = 0
        self.poll_count: int = 0
        self.last_error: dict[str, Any] | None = None

    def record_success(self, data: dict[str, Any], now: datetime) -> None:
        self.last_good_data = data
        self.last_poll_ok_ts = now
        self.last_poll_attempted_ts = now
        self.consecutive_failures = 0
        self.poll_count += 1
        self.last_error = None

    def record_failure(self, exc: BaseException, now: datetime) -> None:
        self.last_poll_attempted_ts = now
        self.consecutive_failures += 1
        self.total_failures += 1
        self.poll_count += 1
        self.last_error = {
            "type": type(exc).__name__,
            "msg": str(exc)[:300],
            "ts": now.isoformat(timespec="seconds"),
        }

    def render_snapshot(self, now: datetime) -> dict[str, Any]:
        """Merge last-good data with current monitor_health and a fresh top-level ts.

        Schema:
          ts             - when this snapshot file was written (always current).
                           Indicates the monitor *process* is alive.
          data_ts        - when the data was last successfully fetched. None if no
                           successful poll yet. Use this for "is the data fresh".
          gpu/cpu/...    - last good data; carries over through failure cycles.
          monitor_health - explicit status of the polling loop (see fields below).
        """
        last_ok = self.last_poll_ok_ts
        stale_s = (now - last_ok).total_seconds() if last_ok else None
        last_attempt = self.last_poll_attempted_ts
        attempt_iso = last_attempt.isoformat(timespec="seconds") if last_attempt else None
        ok_iso = last_ok.isoformat(timespec="seconds") if last_ok else None
        health = {
            "last_poll_ok": ok_iso,
            "last_poll_attempted": attempt_iso,
            "stale_for_s": round(stale_s, 1) if stale_s is not None else None,
            "consecutive_failures": self.consecutive_failures,
            "total_failures": self.total_failures,
            "poll_count": self.poll_count,
            "poll_interval_s": POLL_INTERVAL_S,
            "last_error": self.last_error,
            "status": (
                "ok" if self.consecutive_failures == 0
                else "degraded" if last_ok is not None
                else "no_data"
            ),
        }
        snap = {"ts": now.isoformat(timespec="seconds")}
        snap.update(self.last_good_data)
        snap["monitor_health"] = health
        return snap


def _run_forever() -> int:
    state = _MonitorState()
    ssh = ReadOnlySSH()
    try:
        while True:
            cycle_start = time.perf_counter()
            now = datetime.now()
            try:
                data = _build_data(ssh)
                state.record_success(data, now)
            except Exception as e:
                state.record_failure(e, now)
                _log_stderr(f"cycle error: {type(e).__name__}: {e}")
                sys.stderr.write(traceback.format_exc())
                sys.stderr.flush()
                try:
                    ssh.reset()
                except Exception:
                    pass

            try:
                _atomic_write_json(SNAPSHOT_PATH, state.render_snapshot(datetime.now()))
            except Exception as e:
                _log_stderr(f"write error: {type(e).__name__}: {e}")

            elapsed = time.perf_counter() - cycle_start
            sleep_s = max(1.0, POLL_INTERVAL_S - elapsed)
            time.sleep(sleep_s)
    finally:
        ssh.close()


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        state = _MonitorState()
        now = datetime.now()
        with ReadOnlySSH() as ssh:
            try:
                data = _build_data(ssh)
                state.record_success(data, now)
            except Exception as e:
                state.record_failure(e, now)
        snap = state.render_snapshot(datetime.now())
        _atomic_write_json(SNAPSHOT_PATH, snap)
        print(f"snapshot written: {SNAPSHOT_PATH}")
        print(json.dumps(snap, indent=2, default=str)[:2000])
        return 0
    return _run_forever()


if __name__ == "__main__":
    sys.exit(main())
