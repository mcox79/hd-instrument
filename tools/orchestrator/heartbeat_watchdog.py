"""Heartbeat watchdog for the hd-instrument orchestrator.

Runs in parallel to dispatch.py as a second Monitor. Emits a `silent_idle`
event when the orchestrator pipeline has been demonstrably idle (both GPU
and CPU queues at depth 0, no in-flight orchestrator dispatches, no recently
running runner) for longer than IDLE_THRESHOLD_S.

This is the structural fix for the failure mode described in
`feedback_no_silent_idle.md` (2026-05-23): the orchestrator can otherwise
sit silently waiting for a Monitor event that never fires when an experiment
crashes mid-run or completes without writing a verdict.

Event line format (same convention as dispatch.py)::

    EVENT silent_idle <payload-json>

Payload fields:
- gpu_pending: int          gpu.queue_pending_count
- cpu_pending: int          cpu.queue_pending_count
- gpu_status:  str          gpu.heartbeat.status (idle/running/...)
- cpu_status:  str          cpu.heartbeat.status
- in_flight:   int          len(orchestrator_in_flight.json["dispatches"])
- idle_seconds: float       how long the silent-idle condition has held
- paused: bool              whether the pause flag is set (orchestrator may
                            still want to know, but should NOT refill while paused)

Behavior:
- Polls every POLL_INTERVAL_S (60s).
- Tracks the timestamp at which the silent-idle condition first became true.
- Once the condition has held continuously for >= IDLE_THRESHOLD_S (120s),
  emits ONE silent_idle event and arms a cooldown so we do not spam the
  orchestrator while it is dispatching a recovery. The cooldown is reset
  the moment the condition becomes false (e.g. a refill landed in the queue).

The orchestrator's handling of silent_idle is documented in
`tools/orchestrator/orchestrator_prompt.md` — dispatch exp_dev with an
"emergency refill" prompt unless the pause flag is set.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Suppress console-window pop-ups when this script is launched by Task Scheduler
# or pythonw.exe (no attached console).  Applies to all subprocess.run/Popen calls
# that set this flag — harmless on non-Windows platforms.
_CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

REPO = Path(__file__).resolve().parents[2]
DASHBOARD = REPO / "data" / "local_dashboard_snapshot.json"
IN_FLIGHT = REPO / "data" / "orchestrator_in_flight.json"
PAUSE_FLAG = REPO / "data" / "orchestrator_paused.flag"
ROUTING_RATIO_PATH = REPO / "data" / "orchestrator_routing_ratio.json"
ROUTING_RATIO_SCRIPT = REPO / "tools" / "orchestrator" / "routing_ratio.py"
# Ship-attempt sentinel (Condition 2). queue_add.sh appends one JSONL entry per
# successful local-side exit; watchdog cross-references against the queue
# dashboard to detect SSH/SCP/queue-write silent failures.
SHIP_ATTEMPTS_PATH = REPO / "data" / "recent_ship_attempts.jsonl"
STATUS_LOG_PATH = REPO / "data" / "orchestrator_status_log.jsonl"
LOCAL_CPU_QUEUE_JSON = REPO / "data" / "local_cpu_queue" / "queue.json"
RESEARCH_FIELD_ADVISOR_SCRIPT = REPO / "tools" / "orchestrator" / "research_field_advisor.py"

# ---- Remote-bridge cache pull ----
# heartbeat_watchdog pulls remote_state_cache.json from marsh@home every
# REMOTE_CACHE_PULL_INTERVAL_S seconds.  This feeds the remote_state.py
# consumer API so sub-agents can read queue/runner state without SSH.
REMOTE_STATE_CACHE_PATH = REPO / "data" / "remote_state_cache.json"
REMOTE_CACHE_PULL_INTERVAL_S = 30.0  # how often to SCP the cache file
REMOTE_CACHE_SOURCE = "marsh@home:C:/dev/hd-instrument/data/remote_state_cache.json"

# ---- Remote SSH queue polling (Option A fix for cache-staleness false-idle) ----
# The local_dashboard_snapshot.json can be minutes out of date relative to the
# REAL queue state on marsh@home. heartbeat_watchdog now SSH-polls
# overnight_queue and remote_cpu_queue directly, caching results for
# REMOTE_QUEUE_CACHE_TTL_S to avoid hammering SSH.
SSH_TARGET = "marsh@home"
REPO_REMOTE = "C:/dev/hd-instrument"
REMOTE_OVERNIGHT_QUEUE = f"{REPO_REMOTE}/data/overnight_queue/queue.json"
REMOTE_CPU_QUEUE = f"{REPO_REMOTE}/data/remote_cpu_queue/queue.json"
QUEUE_PENDING_COUNT_SCRIPT = f"{REPO_REMOTE}/tools/orchestrator/_queue_pending_count.py"
REMOTE_PYTHON = f"{REPO_REMOTE}/.venv/Scripts/python.exe"
REMOTE_QUEUE_CACHE_TTL_S = 30.0  # cache SSH results for this many seconds
SSH_CONNECT_TIMEOUT = 8  # seconds; fast fail so we fall back to snapshot

POLL_INTERVAL_S = 60.0
IDLE_THRESHOLD_S = 120.0
# After firing silent_idle, suppress further fires for this long to give the
# orchestrator time to dispatch an emergency refill. If the refill lands, the
# idle condition resets naturally; if it does not, we re-fire after cooldown.
COOLDOWN_S = 600.0

# ---- Per-queue idle events (gpu_idle / cpu_idle) ----
# Fire INDEPENDENTLY of the other queue's state, so the orchestrator can refill
# the GPU lane even when CPU is still busy (and vice-versa).
# Threshold and cooldown are the same as silent_idle (120s / 600s).
PER_QUEUE_IDLE_THRESHOLD_S = 120.0   # same as IDLE_THRESHOLD_S
PER_QUEUE_IDLE_COOLDOWN_S = 600.0    # same as COOLDOWN_S

# ---- Proactive low-queue events (gpu_queue_low / cpu_queue_low) ----
# Fire WHILE the runner is still actively processing an anchor (pending <=
# QUEUE_LOW_THRESHOLD AND has_running == True).  Intent: alert the orchestrator
# while there is still ~30-60 min of in-flight work, leaving time to dispatch
# an exp_dev refill BEFORE the lane goes idle.
#
# Two sub-levels:
#   LOW  (pending <= QUEUE_LOW_THRESHOLD)  — primary signal; cooldown 600s
#   SEVERELY_LOW (pending == 0 but running)  — separate event kind with its
#                                             own cooldown 300s so it doesn't
#                                             dilute the LOW signal
QUEUE_LOW_THRESHOLD = 1          # fire when pending <= this value AND running
QUEUE_LOW_COOLDOWN_S = 600.0     # between LOW fires per lane
QUEUE_SEVERELY_LOW_COOLDOWN_S = 300.0  # between SEVERELY_LOW fires per lane

# ---- Condition 2 (audit recommendation #2): ship_unconfirmed ----
# An attempt is unconfirmed when queue_add.sh returned success locally but the
# named experiment never appears in the remote (or local) queue.json within this
# window. The window must be long enough to absorb the dashboard's own poll lag
# (~5s) plus SSH round-trip jitter, but short enough that a real silent failure
# (scp/ssh dropped the file) gets caught while it can still be re-shipped.
SHIP_UNCONFIRMED_THRESHOLD_S = 60.0
SHIP_CONFIRMED_RETENTION_S = 600.0  # drop entries older than this; they're either confirmed long ago or surfaced already
SHIP_UNCONFIRMED_COOLDOWN_S = 300.0  # don't re-fire on the same name within this window

# ---- Event C: for_you_stale ----
# Fires when no status_log entry has been written in FOR_YOU_STALE_MINUTES.
# Cooldown FOR_YOU_STALE_COOLDOWN_S between fires.
FOR_YOU_STALE_MINUTES = 30.0
FOR_YOU_STALE_COOLDOWN_S = 1800.0

# ---- Event D: research_overdue ----
# Fires when no research_drill_closure / research_delivered event in past
# RESEARCH_OVERDUE_HOURS. Cooldown RESEARCH_OVERDUE_COOLDOWN_S between fires.
RESEARCH_OVERDUE_HOURS = 24.0
RESEARCH_OVERDUE_COOLDOWN_S = 3600.0
RESEARCH_EVENT_KINDS = frozenset({"research_drill_closure", "research_delivered"})

# Routing-ratio enforcement (audit recommendation #3,
# notes/orchestrator_process_audit_2026-05-24.md).
ROUTING_RATIO_THRESHOLD = 0.75
ROUTING_RATIO_WINDOW = 20  # measure over last N turns
# Don't fire on the first few turns of a fresh session (noise).
ROUTING_RATIO_MIN_TURNS = 8
# Recompute every N seconds (parsing the JSONL is cheap but not free).
ROUTING_RATIO_RECOMPUTE_S = 180.0
# Suppress repeat fires for this long after a routing_ratio_low event so the
# orchestrator has time to self-correct before we nag again.
ROUTING_RATIO_COOLDOWN_S = 900.0

# ---- Event E: verdict_landed ----
# Fires once per NEW verdict that appears in the remote_state_cache since the
# last poll.  No cooldown — each distinct verdict fires exactly one event.
# On first poll: initialise last_seen_ts to the newest ended_at in the cache
# (skip-history behaviour) so old verdicts are never replayed after a restart.
HEARTBEAT_WATCHDOG_STATE_PATH = REPO / "data" / "heartbeat_watchdog_state.json"
HEARTBEAT_WATCHDOG_LOG_PATH = REPO / "data" / "heartbeat_watchdog.log"

# ---- Event F: bridge_cache_stale ----
# Fires when remote_state.is_stale() returns True (cache file older than
# WARN_AGE_S=120s), indicating the SCP pull from marsh@home has broken.
# Orchestrator should re-establish the bridge before relying on remote state.
# Cooldown BRIDGE_CACHE_STALE_COOLDOWN_S between fires to avoid spam during
# prolonged SSH outage.
BRIDGE_CACHE_STALE_COOLDOWN_S = 300.0  # suppress repeat fires for 5 min

# ---- Event G: duplicate_runner_detected ----
# Fires when >1 instance of a named runner kind (cpu_runner_0, gpu_runner_0,
# remote_state_emitter) is found running on marsh@home via SSH wmic query.
# The PID-file singleton lock prevents NEW duplicates from launching, but
# pre-lock instances or manual start /BELOWNORMAL launches can still survive.
# Payload: {"runner_kind": str, "instance_count": int, "pids": [...],
#           "creation_times": [...]}
# Cooldown: 900s per runner-kind so we don't spam alerts every poll cycle.
DUPLICATE_RUNNER_COOLDOWN_S = 900.0
# Runner kind → commandline fragment(s) that identify it in wmic output.
# Each entry is (kind_name, must_contain_fragment).
RUNNER_KIND_PATTERNS: list[tuple[str, str]] = [
    ("gpu_runner_0", "gpu_runner_0"),
    ("cpu_runner_0", "cpu_runner_0"),
    ("remote_state_emitter", "remote_state_emitter"),
]
# Minimum real-interpreter memory size in MB to distinguish the real Python
# interpreter from the ~4 MB venv shim launcher.  Any process whose wmic
# WorkingSetSize is < SHIM_MEMORY_THRESHOLD_BYTES is treated as a shim and
# excluded from the runner-instance count.
SHIM_MEMORY_THRESHOLD_BYTES = 10 * 1024 * 1024  # 10 MB

# ---- Event H: duplicate_watchdog_detected ----
# Fires when >1 instance of heartbeat_watchdog.py is found running LOCALLY
# (on this machine, not the remote).  Earlier today PID 8744 + 8340 were both
# alive; the extra instance leads to duplicate events and split state.
# Payload: {"instance_count": int, "pids": [...]}
# Cooldown: 900s between fires.
DUPLICATE_WATCHDOG_COOLDOWN_S = 900.0


# ---------------------------------------------------------------------------
# Remote-bridge cache pull
# ---------------------------------------------------------------------------

_last_cache_pull_ts: float = 0.0


def pull_remote_state_cache(now: float) -> None:
    """SCP remote_state_cache.json from marsh@home to the local data dir.

    Called once per REMOTE_CACHE_PULL_INTERVAL_S inside the main watchdog
    loop.  Failures are silent — the consumer API (remote_state.py) handles
    staleness gracefully.  We use SCP with a short connect timeout to avoid
    blocking the watchdog poll loop for more than ~10s on SSH outage.
    """
    global _last_cache_pull_ts
    if (now - _last_cache_pull_ts) < REMOTE_CACHE_PULL_INTERVAL_S:
        return
    _last_cache_pull_ts = now
    try:
        REMOTE_STATE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = REMOTE_STATE_CACHE_PATH.with_suffix(".pull.tmp")
        result = subprocess.run(
            [
                "scp",
                "-o", f"ConnectTimeout={SSH_CONNECT_TIMEOUT}",
                "-o", "BatchMode=yes",
                "-o", "StrictHostKeyChecking=no",
                REMOTE_CACHE_SOURCE,
                str(tmp),
            ],
            capture_output=True,
            text=True,
            timeout=SSH_CONNECT_TIMEOUT + 10,
            creationflags=_CREATE_NO_WINDOW,
        )
        if result.returncode == 0 and tmp.exists():
            import os as _os
            _os.replace(tmp, REMOTE_STATE_CACHE_PATH)
        else:
            try:
                tmp.unlink(missing_ok=True)
            except Exception:
                pass
    except Exception:
        pass  # SCP failure is non-fatal; consumers fall back to direct SSH


def emit(kind: str, payload: dict[str, Any]) -> None:
    line = f"EVENT {kind} {json.dumps(payload, separators=(',', ':'), default=str)}"
    print(line, flush=True)
    # Also write directly to the log file so events persist when running standalone
    # (e.g. via schtask pythonw.exe without a Monitor capturing stdout).
    try:
        with HEARTBEAT_WATCHDOG_LOG_PATH.open("a", encoding="utf-8") as _fh:
            _fh.write(line + "\n")
    except Exception:
        pass


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Remote queue polling — Option A cache-staleness fix
# ---------------------------------------------------------------------------

# Module-level cache: (result_tuple, fetched_at_monotonic)
# result_tuple = (gpu_pending: int | None, cpu_pending: int | None,
#                 gpu_running: bool, cpu_running: bool)
_remote_queue_cache: tuple[tuple[int | None, int | None, bool, bool], float] | None = None


def _ssh_count_queue(queue_json_path: str) -> int | None:
    """Return pending+running count for a single remote queue.json via SSH.

    Uses a one-liner PowerShell command rather than the helper script so we
    need only one SSH round-trip for both queues.  Returns None on any error
    (SSH timeout, parse failure) so caller falls back to snapshot.
    """
    # PowerShell one-liner: read queue.json, count entries with pending/running status.
    ps = (
        f"(Get-Content '{queue_json_path}' -Raw | ConvertFrom-Json).experiments"
        f" | Where-Object {{ $_.status -in @('pending','running') }}"
        f" | Measure-Object | Select-Object -ExpandProperty Count"
    )
    try:
        result = subprocess.run(
            ["ssh", "-o", f"ConnectTimeout={SSH_CONNECT_TIMEOUT}",
             "-o", "BatchMode=yes",
             SSH_TARGET, f"powershell -Command \"{ps}\""],
            capture_output=True,
            text=True,
            timeout=SSH_CONNECT_TIMEOUT + 5,
            creationflags=_CREATE_NO_WINDOW,
        )
        if result.returncode != 0:
            return None
        raw = result.stdout.strip()
        if raw == "":
            return 0
        return int(raw)
    except Exception:
        return None


def _fetch_remote_queue_counts() -> tuple[int | None, int | None, bool, bool]:
    """SSH-poll both remote queues in a single multiplexed SSH batch.

    Returns (gpu_pending, cpu_pending, gpu_has_running, cpu_has_running).
    Any value can be None if the SSH call failed (caller uses snapshot fallback).

    Batches both queue queries into ONE ssh call via a compound PS command to
    minimise round-trip cost (typical SSH + PS startup ~0.5-1.5 s).
    """
    # Compound PowerShell: emit four lines for pure-pending and running counts.
    # NOTE: GPU:/CPU: must count ONLY 'pending' items (NOT 'pending+running').
    # evaluate_per_queue_low uses gpu_pending <= QUEUE_LOW_THRESHOLD to fire
    # the proactive queue-low alert while the runner is still busy; if we
    # include the in-flight 'running' item in the count the threshold is off
    # by one and the alert never fires at depth=1 (bug: 2026-05-27).
    ps = (
        f"$g=(Get-Content '{REMOTE_OVERNIGHT_QUEUE}' -Raw | ConvertFrom-Json).experiments;"
        f"$c=(Get-Content '{REMOTE_CPU_QUEUE}' -Raw | ConvertFrom-Json).experiments;"
        f"'GPU:' + (($g | Where-Object {{ $_.status -eq 'pending' }} | Measure-Object).Count);"
        f"'CPU:' + (($c | Where-Object {{ $_.status -eq 'pending' }} | Measure-Object).Count);"
        f"'GPU_RUN:' + (($g | Where-Object {{ $_.status -eq 'running' }} | Measure-Object).Count);"
        f"'CPU_RUN:' + (($c | Where-Object {{ $_.status -eq 'running' }} | Measure-Object).Count)"
    )
    try:
        result = subprocess.run(
            ["ssh", "-o", f"ConnectTimeout={SSH_CONNECT_TIMEOUT}",
             "-o", "BatchMode=yes",
             SSH_TARGET, f"powershell -Command \"{ps}\""],
            capture_output=True,
            text=True,
            timeout=SSH_CONNECT_TIMEOUT + 10,
            creationflags=_CREATE_NO_WINDOW,
        )
        if result.returncode != 0:
            return (None, None, False, False)
        lines = {
            line.split(":", 1)[0]: line.split(":", 1)[1]
            for line in result.stdout.strip().splitlines()
            if ":" in line
        }
        gpu_pending = int(lines["GPU"]) if "GPU" in lines else None
        cpu_pending = int(lines["CPU"]) if "CPU" in lines else None
        gpu_running = int(lines.get("GPU_RUN", "0")) > 0
        cpu_running = int(lines.get("CPU_RUN", "0")) > 0
        return (gpu_pending, cpu_pending, gpu_running, cpu_running)
    except Exception:
        return (None, None, False, False)


def get_remote_queue_counts(now: float) -> tuple[int | None, int | None, bool, bool]:
    """Return cached remote queue counts, refreshing if TTL has expired.

    Returns (gpu_pending, cpu_pending, gpu_has_running, cpu_has_running).
    Returns (None, None, False, False) if SSH is unavailable; caller falls
    back to the local dashboard snapshot.
    """
    global _remote_queue_cache
    if _remote_queue_cache is not None:
        counts, fetched_at = _remote_queue_cache
        if (now - fetched_at) < REMOTE_QUEUE_CACHE_TTL_S:
            return counts
    counts = _fetch_remote_queue_counts()
    _remote_queue_cache = (counts, now)
    return counts


def in_flight_count() -> int:
    """Count orchestrator dispatches currently registered as running.

    Empty / missing file => 0.
    """
    if not IN_FLIGHT.exists():
        return 0
    d = load_json(IN_FLIGHT)
    if not isinstance(d, dict):
        return 0
    dispatches = d.get("dispatches")
    if not isinstance(dispatches, list):
        return 0
    return len(dispatches)


def pause_is_set() -> bool:
    return PAUSE_FLAG.exists()


def _get_queue_state(now: float) -> dict[str, Any] | None:
    """Fetch current GPU and CPU queue state from SSH (or snapshot fallback).

    Returns a dict with keys:
      gpu_pending: int
      cpu_pending: int
      gpu_has_running: bool
      cpu_has_running: bool
      gpu_status: str   (from snapshot, human-context only)
      cpu_status: str   (from snapshot, human-context only)
      source: str       ("remote_ssh" | "snapshot_fallback")

    Returns None if data is completely unavailable.
    """
    remote_gpu_pending, remote_cpu_pending, remote_gpu_running, remote_cpu_running = (
        get_remote_queue_counts(now)
    )

    remote_available = remote_gpu_pending is not None and remote_cpu_pending is not None

    if remote_available:
        gpu_pending = remote_gpu_pending
        cpu_pending = remote_cpu_pending
        gpu_has_running = remote_gpu_running
        cpu_has_running = remote_cpu_running
        source = "remote_ssh"
    else:
        if not DASHBOARD.exists():
            return None
        d = load_json(DASHBOARD)
        if not isinstance(d, dict):
            return None
        gpu = d.get("gpu") or {}
        cpu = d.get("cpu") or {}
        gpu_pending = gpu.get("queue_pending_count")
        cpu_pending = cpu.get("queue_pending_count")
        if gpu_pending is None or cpu_pending is None:
            return None
        gpu_status_str = ((gpu.get("heartbeat") or {}).get("status") or "").lower()
        cpu_status_str = ((cpu.get("heartbeat") or {}).get("status") or "").lower()
        gpu_has_running = gpu_status_str == "running"
        cpu_has_running = cpu_status_str == "running"
        source = "snapshot_fallback"

    # Derive status strings for the payload (best-effort from snapshot)
    snap = load_json(DASHBOARD) if DASHBOARD.exists() else {}
    snap = snap or {}
    gpu_status = ((snap.get("gpu") or {}).get("heartbeat") or {}).get("status") or "unknown"
    cpu_status = ((snap.get("cpu") or {}).get("heartbeat") or {}).get("status") or "unknown"

    return {
        "gpu_pending": gpu_pending,
        "cpu_pending": cpu_pending,
        "gpu_has_running": gpu_has_running,
        "cpu_has_running": cpu_has_running,
        "gpu_status": gpu_status.lower(),
        "cpu_status": cpu_status.lower(),
        "source": source,
    }


def evaluate_idle() -> dict[str, Any] | None:
    """Return a payload dict iff the silent-idle condition currently holds.

    Condition:
      - gpu queue pending+running count == 0 AND cpu queue pending+running count == 0
      - gpu.heartbeat.status != 'running' AND cpu.heartbeat.status != 'running'
      - in_flight_count() == 0

    Queue counts are obtained by SSH-polling the remote queue.json files
    directly (Option A fix for cache-staleness false-alarms). If the SSH call
    fails we fall back to the local_dashboard_snapshot.json, which may be
    stale — in that case we treat the result as "not idle" to avoid a false
    positive (safe-side: only fire when we have fresh evidence of real idleness).

    Returns None if any of those is false or data is unavailable.
    """
    now = time.time()
    qs = _get_queue_state(now)
    if qs is None:
        return None

    # ---- Apply idle gate (BOTH queues must be idle) ----
    if qs["gpu_pending"] != 0 or qs["cpu_pending"] != 0:
        return None
    if qs["gpu_has_running"] or qs["cpu_has_running"]:
        return None
    if in_flight_count() != 0:
        return None

    return {
        "gpu_pending": qs["gpu_pending"],
        "cpu_pending": qs["cpu_pending"],
        "gpu_status": qs["gpu_status"],
        "cpu_status": qs["cpu_status"],
        "in_flight": 0,
        "queue_source": qs["source"],
    }


def evaluate_per_queue_idle(now: float) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Return (gpu_idle_payload, cpu_idle_payload) for per-lane idle detection.

    Each payload is non-None iff:
      - That lane's queue pending+running count == 0
      - That lane's runner is NOT currently marked 'running'
      - (No in_flight gate — the per-queue events fire regardless of the OTHER
        queue's state, which is the whole point of this split.)

    If queue state data is unavailable, returns (None, None).
    """
    qs = _get_queue_state(now)
    if qs is None:
        return (None, None)

    gpu_payload: dict[str, Any] | None = None
    cpu_payload: dict[str, Any] | None = None

    if qs["gpu_pending"] == 0 and not qs["gpu_has_running"]:
        gpu_payload = {
            "gpu_pending": qs["gpu_pending"],
            "gpu_status": qs["gpu_status"],
            "cpu_pending": qs["cpu_pending"],  # context — may be non-zero
            "cpu_status": qs["cpu_status"],
            "queue_source": qs["source"],
        }

    if qs["cpu_pending"] == 0 and not qs["cpu_has_running"]:
        cpu_payload = {
            "cpu_pending": qs["cpu_pending"],
            "cpu_status": qs["cpu_status"],
            "gpu_pending": qs["gpu_pending"],  # context — may be non-zero
            "gpu_status": qs["gpu_status"],
            "queue_source": qs["source"],
        }

    return (gpu_payload, cpu_payload)


def evaluate_per_queue_low(now: float) -> tuple[
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
]:
    """Return (gpu_low_payload, cpu_low_payload, gpu_severely_low_payload, cpu_severely_low_payload).

    Each payload is non-None when the corresponding condition holds:

    gpu_low_payload:
      - overnight_queue pending <= QUEUE_LOW_THRESHOLD (default 1) AND gpu runner IS running.
      - Fires while work is still in flight so the orchestrator has lead time to dispatch
        an exp_dev refill before the lane goes idle.

    cpu_low_payload: same for remote_cpu_queue.

    gpu_severely_low_payload:
      - overnight_queue pending == 0 AND gpu runner IS running (one item in flight, nothing
        queued behind it).  Separate cooldown (300s) so it doesn't dilute the LOW signal.

    cpu_severely_low_payload: same for remote_cpu_queue.

    If queue state data is unavailable, returns (None, None, None, None).
    """
    qs = _get_queue_state(now)
    if qs is None:
        return (None, None, None, None)

    gpu_low: dict[str, Any] | None = None
    cpu_low: dict[str, Any] | None = None
    gpu_severely_low: dict[str, Any] | None = None
    cpu_severely_low: dict[str, Any] | None = None

    # GPU lane
    if qs["gpu_has_running"]:
        # pending count does NOT include the currently-running item (which is in
        # gpu_has_running, not pending). So pending <= QUEUE_LOW_THRESHOLD means
        # the queue will go empty <= QUEUE_LOW_THRESHOLD + 1 anchors from now.
        if qs["gpu_pending"] <= QUEUE_LOW_THRESHOLD:
            base = {
                "gpu_pending": qs["gpu_pending"],
                "gpu_status": qs["gpu_status"],
                "cpu_pending": qs["cpu_pending"],
                "cpu_status": qs["cpu_status"],
                "threshold": QUEUE_LOW_THRESHOLD,
                "queue_source": qs["source"],
            }
            if qs["gpu_pending"] == 0:
                gpu_severely_low = dict(base)
            else:
                gpu_low = dict(base)

    # CPU lane
    if qs["cpu_has_running"]:
        if qs["cpu_pending"] <= QUEUE_LOW_THRESHOLD:
            base = {
                "cpu_pending": qs["cpu_pending"],
                "cpu_status": qs["cpu_status"],
                "gpu_pending": qs["gpu_pending"],
                "gpu_status": qs["gpu_status"],
                "threshold": QUEUE_LOW_THRESHOLD,
                "queue_source": qs["source"],
            }
            if qs["cpu_pending"] == 0:
                cpu_severely_low = dict(base)
            else:
                cpu_low = dict(base)

    return (gpu_low, cpu_low, gpu_severely_low, cpu_severely_low)


def recompute_routing_ratio() -> dict[str, Any] | None:
    """Run tools/orchestrator/routing_ratio.py to refresh the snapshot.

    Returns the parsed primary summary, or None on failure. The script
    writes data/orchestrator_routing_ratio.json itself; this function
    just kicks it and reads back.
    """
    if not ROUTING_RATIO_SCRIPT.is_file():
        return None
    try:
        subprocess.run(
            [
                sys.executable,
                str(ROUTING_RATIO_SCRIPT),
                "--window",
                str(ROUTING_RATIO_WINDOW),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=False,
            creationflags=_CREATE_NO_WINDOW,
        )
    except Exception:
        return None
    if not ROUTING_RATIO_PATH.is_file():
        return None
    try:
        doc = json.loads(ROUTING_RATIO_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    return doc.get("primary") if isinstance(doc, dict) else None


def load_ship_attempts() -> list[dict[str, Any]]:
    """Read the recent_ship_attempts.jsonl sentinel.

    Each line is one JSON object written by queue_add.sh on local-side success:
      {"ts": ISO, "queue": "overnight_queue|remote_cpu_queue|local_cpu_queue",
       "name": "<exp_name>", "attempted_at": ISO}

    Tolerates torn writes (skips malformed lines). Returns chronological list.
    """
    if not SHIP_ATTEMPTS_PATH.is_file():
        return []
    out: list[dict[str, Any]] = []
    try:
        text = SHIP_ATTEMPTS_PATH.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            d = json.loads(s)
        except Exception:
            continue
        if isinstance(d, dict) and d.get("name") and d.get("queue"):
            out.append(d)
    return out


def _name_in_local_cpu_queue_direct(name: str) -> bool:
    """Fallback for local_cpu_queue: read data/local_cpu_queue/queue.json directly.

    The dashboard snapshot has no `local_cpu` section, so
    `_name_in_dashboard_queue` would always return False for local_cpu_queue
    ships. This causes `landed_at` to never be stamped and triggers repeated
    ship_unconfirmed fires on completed local_cpu anchors.

    Confirmation paths:
      1. Any experiment entry whose name matches and status is NOT pending
         (completed / failed / killed / running) → anchor landed and ran.
      2. Any experiment with status "pending" or "queued" and the name matches
         → anchor is in the queue, actively waiting.
      3. The experiment is absent from queue.json entirely → cannot confirm
         presence, but caller may still confirm via recent_verdicts or runner logs.
    """
    if not LOCAL_CPU_QUEUE_JSON.is_file():
        return False
    try:
        doc = json.loads(LOCAL_CPU_QUEUE_JSON.read_text(encoding="utf-8"))
    except Exception:
        return False
    if not isinstance(doc, dict):
        return False
    exps = doc.get("experiments")
    if not isinstance(exps, list):
        return False
    for exp in exps:
        if not isinstance(exp, dict):
            continue
        exp_name = exp.get("name")
        if exp_name == name:
            # Entry found in queue.json — regardless of status (pending, running,
            # completed, failed, killed) its presence proves the ship landed.
            return True
    return False


def _name_in_dashboard_queue(snapshot: dict[str, Any], queue: str, name: str) -> bool:
    """Return True iff `name` appears in any queue.json reflected by the dashboard
    snapshot for the matching `queue` label.

    Queue label mapping:
      overnight_queue  -> snapshot["gpu"]
      remote_cpu_queue -> snapshot["cpu"]
      local_cpu_queue  -> snapshot["local_cpu"] (if present); falls back to
                          reading data/local_cpu_queue/queue.json directly
                          because the dashboard snapshot has no local_cpu section.

    Membership check looks at both queue_pending and queue_running lists. If the
    experiment already completed and was reaped from the queue, we treat that as
    "confirmed" too (it landed, the runner ran it) -- but the dashboard snapshot
    drops completed names, so we additionally consult any current/heartbeat
    fields to avoid false positives on fast-completing entries.
    """
    label_map = {
        "overnight_queue": "gpu",
        "remote_cpu_queue": "cpu",
        "local_cpu_queue": "local_cpu",
    }
    key = label_map.get(queue)
    if key is None:
        return False

    section = snapshot.get(key) or {}
    if isinstance(section, dict) and section:
        # Dashboard has the section — use it normally.
        for field in ("queue_pending", "queue_running"):
            v = section.get(field) or []
            if isinstance(v, list) and name in v:
                return True
        # Currently-running heartbeat catches the short window where queue.json
        # may be re-written without the entry but the runner is mid-execution.
        cur = section.get("current")
        if cur and cur == name:
            return True
        hb = section.get("heartbeat") or {}
        if isinstance(hb, dict) and hb.get("current") == name:
            return True
        return False

    # Dashboard section is absent or empty. For local_cpu_queue this is the
    # structural blind-spot: the snapshot writer never includes a `local_cpu`
    # key. Fall back to reading the local queue file directly.
    if queue == "local_cpu_queue":
        return _name_in_local_cpu_queue_direct(name)

    return False


def _name_in_recent_verdicts(snapshot: dict[str, Any], name: str) -> bool:
    """Return True iff `name` (exact or prefix match) appears in recent_verdicts.

    Background: dashboard surfaces the last ~50 verdicts. After an experiment
    completes and is reaped from queue.json, this is the canonical evidence
    that the ship "landed and ran." Without this check the watchdog
    false-positives on fast-completing experiments — entry hit queue.json,
    runner picked it up, finished, queue.json was rewritten without it, and
    the watchdog interprets "not in queue.json now" as "never landed."

    Match rules:
      * Exact name match: verdict.name == name
      * Prefix match: verdict.name == f"{name}_rerun" or startswith(f"{name}_")
        (queue_add.py supports --rerun-as which appends suffixes; the original
         ship-attempt name should still be considered "landed" if any of its
         derivatives produced a verdict).
    """
    rv = snapshot.get("recent_verdicts")
    if not isinstance(rv, list):
        return False
    name_underscore = name + "_"
    for v in rv:
        if not isinstance(v, dict):
            continue
        vn = v.get("name")
        if not isinstance(vn, str):
            continue
        if vn == name or vn.startswith(name_underscore):
            return True
    return False


def _name_in_runner_logs(snapshot: dict[str, Any], queue: str, name: str) -> bool:
    """Return True iff `recent_log_lines` for the relevant runner shows a
    START/DONE record for `name`.

    Catches the third confirmation window: experiment landed, runner logged
    START/DONE, completed, dropped from queue.json, also rolled off the 50-
    entry recent_verdicts tail. As long as the runner's recent_log_lines tail
    still shows the name, it confirms "ran and completed."
    """
    label_map = {
        "overnight_queue": "gpu",
        "remote_cpu_queue": "cpu",
        "local_cpu_queue": "local_cpu",
    }
    key = label_map.get(queue)
    if key is None:
        return False
    section = snapshot.get(key) or {}
    if not isinstance(section, dict):
        return False
    lines = section.get("recent_log_lines") or []
    if not isinstance(lines, list):
        return False
    for ln in lines:
        if isinstance(ln, str) and (f" {name} " in ln or ln.endswith(f" {name}") or f" {name}_" in ln):
            return True
    return False


def _is_confirmed(
    snapshot: dict[str, Any],
    queue: str,
    name: str,
    attempt_landed: bool,
) -> bool:
    """Composite ship-landing check. Returns True if ANY confirmation path holds.

    The four confirmation paths together cover the full lifecycle:
      1. attempt_landed: a prior poll already observed this name in the queue
         (sticky bit; once landed, always confirmed for the rest of retention)
      2. queue.json membership (queue_pending / queue_running / current /
         heartbeat.current) — entry is in flight RIGHT NOW
      3. recent_verdicts — entry completed and produced a verdict, even if
         it has since been reaped from queue.json
      4. runner recent_log_lines — entry has a START/DONE line in the
         50-line tail, even if it rolled off recent_verdicts

    This is the structural fix for the v193-era false-positive class where
    the watchdog re-fired ship_unconfirmed on names that completed cleanly
    minutes earlier (e.g. moe_xtalk_smoke, hatano_sasa_cap3_long_traj_v2,
    mingo_speicher_1st_order_mn8_v1 at the 2026-05-24 16:44-16:47 window).
    """
    if attempt_landed:
        return True
    # recent_verdicts check first: covers completed/failed/killed entries that
    # already ran and were reaped from queue.json. Any verdict status counts as
    # "landed" — the runner picked up the entry and ran it to completion.
    if _name_in_recent_verdicts(snapshot, name):
        return True
    if _name_in_dashboard_queue(snapshot, queue, name):
        return True
    if _name_in_runner_logs(snapshot, queue, name):
        return True
    return False


def evaluate_ship_unconfirmed(
    snapshot: dict[str, Any],
    last_fire_ts_by_name: dict[str, float],
    now: float,
) -> list[dict[str, Any]]:
    """Return one ship_unconfirmed payload per attempt that is overdue and missing.

    State machine per attempt:
      * UNLANDED: no `landed_at` field; not yet observed in any confirmation
        path. If past threshold, fire ship_unconfirmed.
      * LANDED:   has `landed_at`; confirmed in a prior poll via queue.json,
        recent_verdicts, or runner logs. Sticky — never re-evaluate as
        unconfirmed; just retain until SHIP_CONFIRMED_RETENTION_S elapses.

    Side effects:
      * Stamps `landed_at` on entries that confirm this cycle.
      * Drops entries older than SHIP_CONFIRMED_RETENTION_S (whether landed
        or not — the latter case means we already fired ship_unconfirmed and
        the orchestrator either re-shipped or accepted the loss).
      * Rewrites the sentinel JSONL with the surviving entries (atomic).
    """
    attempts = load_ship_attempts()
    if not attempts:
        return []

    payloads: list[dict[str, Any]] = []
    keepers: list[dict[str, Any]] = []
    rewrite_needed = False

    for att in attempts:
        attempted_iso = att.get("attempted_at") or att.get("ts")
        try:
            attempted_dt = datetime.fromisoformat(attempted_iso)
            # Legacy entries (pre-Z-suffix) are naive UTC; stamp tzinfo so
            # .timestamp() does not silently apply the local-machine offset
            # and produce a spurious 4-8h age inflation that re-fires
            # ship_unconfirmed forever.
            if attempted_dt.tzinfo is None:
                attempted_dt = attempted_dt.replace(tzinfo=timezone.utc)
            attempted_ts = attempted_dt.timestamp()
        except Exception:
            # Malformed timestamp: keep it but skip evaluation.
            keepers.append(att)
            continue

        age_s = now - attempted_ts
        name = att["name"]
        queue = att["queue"]
        already_landed = bool(att.get("landed_at"))

        # Drop very old entries so the file does not grow unbounded. This
        # applies regardless of landed state — confirmed entries don't need
        # to live forever, and unconfirmed entries past retention either got
        # surfaced + handled or are permanent ghosts.
        if age_s > SHIP_CONFIRMED_RETENTION_S:
            rewrite_needed = True
            continue

        confirmed = _is_confirmed(snapshot, queue, name, already_landed)

        if confirmed:
            # Stamp landed_at on first confirmation so subsequent polls treat
            # this as sticky-landed even if the entry rolls off recent_verdicts
            # and recent_log_lines before retention expires.
            if not already_landed:
                att = dict(att)
                att["landed_at"] = datetime.now().isoformat(timespec="seconds")
                rewrite_needed = True
            keepers.append(att)
            continue

        # Not yet confirmed. Keep in sentinel; only emit if past the threshold.
        keepers.append(att)
        if age_s < SHIP_UNCONFIRMED_THRESHOLD_S:
            continue

        # Cooldown per (queue,name) to avoid spamming on the same missing entry.
        key = f"{queue}|{name}"
        last_fire = last_fire_ts_by_name.get(key)
        if last_fire is not None and (now - last_fire) < SHIP_UNCONFIRMED_COOLDOWN_S:
            continue
        last_fire_ts_by_name[key] = now

        payloads.append({
            "name": name,
            "queue": queue,
            "attempted_at": attempted_iso,
            "seconds_since": round(age_s, 1),
        })

    # Best-effort prune of confirmed/old entries by rewriting the file. We
    # rewrite when the keepers list differs in length OR when any entry was
    # mutated (landed_at stamping).
    if rewrite_needed or len(keepers) != len(attempts):
        try:
            tmp = SHIP_ATTEMPTS_PATH.with_suffix(SHIP_ATTEMPTS_PATH.suffix + ".tmp")
            with tmp.open("w", encoding="utf-8") as fh:
                for k in keepers:
                    fh.write(json.dumps(k, separators=(",", ":")) + "\n")
            tmp.replace(SHIP_ATTEMPTS_PATH)
        except Exception:
            pass

    return payloads


def _tail_status_log(n: int = 200) -> list[dict[str, Any]]:
    """Return the last *n* parsed entries from data/orchestrator_status_log.jsonl.

    Skips malformed lines. Returns [] if the file is missing or unreadable.
    """
    if not STATUS_LOG_PATH.is_file():
        return []
    try:
        text = STATUS_LOG_PATH.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except Exception:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out[-n:]


def _parse_ts(ts_str: str | None) -> float | None:
    """Parse an ISO-8601 timestamp string to a Unix float. Returns None on failure."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str).timestamp()
    except Exception:
        return None


def _load_watchdog_state() -> dict[str, Any]:
    """Load persistent watchdog state from disk. Returns {} on failure."""
    try:
        return json.loads(
            HEARTBEAT_WATCHDOG_STATE_PATH.read_text(encoding="utf-8")
        )
    except Exception:
        return {}


# Routing-file inbox patterns: keyed by recipient session. Matches the poller's
# inbox_globs (kept in sync; if poller adds patterns, mirror here so the
# auto-ping watchdog fires on the same set the dashboard surfaces).
# Cross-session-coordination Part C layer 1 per
# notes/testbed_handoff_dashboard_session_coordination_v1_2026-06-01.md
_INBOX_PATTERNS_BY_RECIPIENT = {
    "orchestrator": [
        "strategy_request_to_strategy_*.md",
        "strategy_request_to_exp_dev_*.md",
        "exp_dev_handoff_*.md",
    ],
    "research": [
        "strategy_request_to_research_*.md",
        "strategy_response_to_research_*.md",
    ],
    "testbed": [
        "testbed_handoff_*.md",
        "strategy_response_to_testbed_*.md",
    ],
    "cloud": [
        "cloud_handoff_*.md",
    ],
}


def evaluate_new_routings(
    seen_filenames: set[str],
) -> tuple[list[dict[str, Any]], set[str]]:
    """Scan notes/ for routing files; return (new payloads, current seen set).

    Each new routing file (one not in seen_filenames) emits a payload with
    the recipient session and the filename, so consumers (For-You feed,
    orchestrator, etc.) can surface "new message for testbed!" within ~30s
    (one watchdog tick).

    Excludes notes/routed_completed/ subdirectory (routed files already
    processed are not "new" by any meaningful definition).
    """
    notes_dir = REPO / "notes"
    current: set[str] = set()
    new_payloads: list[dict[str, Any]] = []
    if not notes_dir.is_dir():
        return new_payloads, current

    for recipient, patterns in _INBOX_PATTERNS_BY_RECIPIENT.items():
        for pat in patterns:
            for p in notes_dir.glob(pat):
                if not p.is_file():
                    continue
                # Skip files in routed_completed/ subdirectory
                if "routed_completed" in p.parts:
                    continue
                fname = p.name
                current.add(fname)
                if fname not in seen_filenames:
                    new_payloads.append({
                        "recipient": recipient,
                        "filename": fname,
                        "mtime_iso": datetime.fromtimestamp(
                            p.stat().st_mtime, tz=timezone.utc
                        ).isoformat(timespec="seconds"),
                    })
    return new_payloads, current


def _save_watchdog_state(state: dict[str, Any]) -> None:
    """Persist watchdog state atomically."""
    try:
        HEARTBEAT_WATCHDOG_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = HEARTBEAT_WATCHDOG_STATE_PATH.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(state, indent=2, default=str), encoding="utf-8"
        )
        tmp.replace(HEARTBEAT_WATCHDOG_STATE_PATH)
    except Exception:
        pass


def evaluate_verdict_landed(
    last_seen_ts: float,
) -> tuple[list[dict[str, Any]], float]:
    """Return (new_verdict_payloads, updated_last_seen_ts).

    Reads recent_verdicts from the remote_state bridge cache.  For each
    verdict whose ended_at is strictly greater than last_seen_ts, one
    verdict_landed payload is emitted.  Returns the updated last_seen_ts
    (max ended_at seen so far, or unchanged if nothing new).

    Verdicts with missing / unparseable ended_at are skipped.
    """
    # Import here to avoid circular-import issues at module level.
    try:
        from tools.orchestrator.remote_state import get_recent_verdicts
    except Exception:
        return ([], last_seen_ts)

    verdicts = get_recent_verdicts(n=50)
    if not verdicts:
        return ([], last_seen_ts)

    new_payloads: list[dict[str, Any]] = []
    new_last_seen = last_seen_ts

    for v in verdicts:
        ended_at_str = v.get("ended_at")
        ts = _parse_ts(ended_at_str)
        if ts is None:
            continue
        if ts <= last_seen_ts:
            continue
        # New verdict
        new_payloads.append({
            "name": v.get("name", ""),
            "verdict": v.get("verdict", ""),
            "ended_at": ended_at_str,
            "queue": v.get("queue", ""),
        })
        if ts > new_last_seen:
            new_last_seen = ts

    return (new_payloads, new_last_seen)


def evaluate_for_you_stale(now: float) -> dict[str, Any] | None:
    """Return a payload iff the for_you_stale condition holds.

    Condition: the most-recent entry in data/orchestrator_status_log.jsonl
    has a 'ts' field older than FOR_YOU_STALE_MINUTES minutes ago (or the file
    has no parseable entries at all).

    Payload fields:
      minutes_since_last_event  float  how many minutes since the last log entry
      most_recent_event_kind    str    event_kind of the most-recent entry, or "(none)"
    """
    entries = _tail_status_log(50)
    if not entries:
        return {
            "minutes_since_last_event": round(FOR_YOU_STALE_MINUTES, 1),
            "most_recent_event_kind": "(none)",
        }
    # Walk backwards to find the most-recent valid ts
    for entry in reversed(entries):
        ts_val = _parse_ts(entry.get("ts"))
        if ts_val is not None:
            age_minutes = (now - ts_val) / 60.0
            if age_minutes > FOR_YOU_STALE_MINUTES:
                return {
                    "minutes_since_last_event": round(age_minutes, 1),
                    "most_recent_event_kind": entry.get("event_kind", "(unknown)"),
                }
            return None  # recent enough — no event needed
    # No parseable timestamps at all → treat as stale
    return {
        "minutes_since_last_event": round(FOR_YOU_STALE_MINUTES, 1),
        "most_recent_event_kind": "(none)",
    }


def _get_top_research_field() -> str:
    """Run research_field_advisor.py --json and return the top scope-expansion field name.

    Returns an empty string on any failure (advisor is optional enrichment only).
    """
    if not RESEARCH_FIELD_ADVISOR_SCRIPT.is_file():
        return ""
    try:
        result = subprocess.run(
            [sys.executable, str(RESEARCH_FIELD_ADVISOR_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            creationflags=_CREATE_NO_WINDOW,
        )
        if result.returncode not in (0, 1):
            return ""
        doc = json.loads(result.stdout)
        scope = doc.get("scope_expansion")
        if isinstance(scope, list) and scope:
            return scope[0].get("field", "")
    except Exception:
        pass
    return ""


def evaluate_research_overdue(now: float) -> dict[str, Any] | None:
    """Return a payload iff the research_overdue condition holds.

    Condition: the most-recent entry with event_kind in RESEARCH_EVENT_KINDS
    is older than RESEARCH_OVERDUE_HOURS hours (or no such entry exists).

    Payload fields:
      hours_since_last_research  float   hours since most-recent research event
      suggested_field            str     top scope-expansion field from advisor, or ""
    """
    entries = _tail_status_log(200)
    threshold_s = RESEARCH_OVERDUE_HOURS * 3600.0

    most_recent_research_ts: float | None = None
    for entry in reversed(entries):
        if entry.get("event_kind") in RESEARCH_EVENT_KINDS:
            ts_val = _parse_ts(entry.get("ts"))
            if ts_val is not None:
                most_recent_research_ts = ts_val
                break

    if most_recent_research_ts is None:
        # No research event in the tail at all; check age as if from epoch 0
        # but cap the reported hours at a sane ceiling (1 week).
        hours_ago = min(RESEARCH_OVERDUE_HOURS * 2, 168.0)
    else:
        age_s = now - most_recent_research_ts
        if age_s <= threshold_s:
            return None  # recent enough — no event needed
        hours_ago = age_s / 3600.0

    return {
        "hours_since_last_research": round(hours_ago, 1),
        "suggested_field": _get_top_research_field(),
    }


def evaluate_routing_ratio(primary: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return payload iff routing_ratio_low condition holds, else None."""
    if not isinstance(primary, dict):
        return None
    n = primary.get("n_turns") or 0
    if n < ROUTING_RATIO_MIN_TURNS:
        return None
    ratio = primary.get("routing_ratio")
    if ratio is None:
        return None
    if ratio >= ROUTING_RATIO_THRESHOLD:
        return None
    return {
        "routing_ratio": ratio,
        "target_ratio": ROUTING_RATIO_THRESHOLD,
        "window_turns": n,
        "total_dispatches": primary.get("total_dispatches"),
        "total_main_thread": primary.get("total_main_thread"),
        "chat_overhead": primary.get("chat_overhead"),
        "status": primary.get("status"),
    }


def evaluate_duplicate_runner(now: float) -> list[dict[str, Any]]:
    """SSH to marsh@home, query running Python processes, and detect runner duplicates.

    For each runner kind defined in RUNNER_KIND_PATTERNS, count the number of
    running Python interpreter instances whose command-line contains the kind's
    fragment.  Shim launchers (~4 MB venv shims) are excluded by checking wmic
    WorkingSetSize.  Parent-child shim pairs are thereby collapsed to ONE instance.

    Returns a list of payloads (one per offending runner kind).  Empty list means
    no duplicates detected (or SSH unavailable).
    """
    # Query: ProcessId, CommandLine, and WorkingSetSize for all python.exe / pythonw.exe
    ps = (
        "wmic process where \\\"name='python.exe' or name='pythonw.exe'\\\""
        " get ProcessId,CommandLine,WorkingSetSize /format:list"
    )
    try:
        result = subprocess.run(
            [
                "ssh",
                "-o", f"ConnectTimeout={SSH_CONNECT_TIMEOUT}",
                "-o", "BatchMode=yes",
                "-o", "StrictHostKeyChecking=no",
                SSH_TARGET,
                f"powershell -Command \"{ps}\"",
            ],
            capture_output=True,
            text=True,
            timeout=SSH_CONNECT_TIMEOUT + 15,
            creationflags=_CREATE_NO_WINDOW,
        )
        if result.returncode != 0:
            return []
        raw_output = result.stdout
    except Exception:
        return []

    # Parse wmic /format:list output into a list of dicts.
    # Each process block is separated by a blank line; within a block each
    # line is "Key=Value".
    processes: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            if current:
                processes.append(current)
                current = {}
        elif "=" in line:
            k, _, v = line.partition("=")
            current[k.strip()] = v.strip()
    if current:
        processes.append(current)

    # Filter out shim launchers by WorkingSetSize < SHIM_MEMORY_THRESHOLD_BYTES.
    real_interpreters: list[dict[str, str]] = []
    for proc in processes:
        wss_str = proc.get("WorkingSetSize", "0")
        try:
            wss = int(wss_str)
        except ValueError:
            wss = 0
        if wss >= SHIM_MEMORY_THRESHOLD_BYTES:
            real_interpreters.append(proc)

    payloads: list[dict[str, Any]] = []
    for kind_name, fragment in RUNNER_KIND_PATTERNS:
        matching = [
            p for p in real_interpreters
            if fragment in (p.get("CommandLine") or "")
        ]
        if len(matching) > 1:
            pids = [p.get("ProcessId", "?") for p in matching]
            # CreationDate is not in the query above; include PIDs only.
            payloads.append({
                "runner_kind": kind_name,
                "instance_count": len(matching),
                "pids": pids,
                "detected_at": datetime.now().isoformat(timespec="seconds"),
            })

    return payloads


def evaluate_duplicate_watchdog() -> dict[str, Any] | None:
    """Detect multiple local heartbeat_watchdog.py instances.

    Uses tasklist (Windows) or ps (POSIX) to enumerate Python processes on
    THIS machine whose command-line contains 'heartbeat_watchdog'.

    Returns a payload dict if >1 instance found, else None.
    """
    own_pid = os.getpid() if hasattr(os, "getpid") else -1

    if sys.platform == "win32":
        # WMIC on local machine (no SSH needed).
        try:
            result = subprocess.run(
                [
                    "wmic", "process",
                    "where", "name='python.exe' or name='pythonw.exe'",
                    "get", "ProcessId,CommandLine,WorkingSetSize",
                    "/format:list",
                ],
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=_CREATE_NO_WINDOW,
            )
            raw = result.stdout
        except Exception:
            return None

        processes: list[dict[str, str]] = []
        current: dict[str, str] = {}
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                if current:
                    processes.append(current)
                    current = {}
            elif "=" in line:
                k, _, v = line.partition("=")
                current[k.strip()] = v.strip()
        if current:
            processes.append(current)

        watchdog_pids: list[str] = []
        for proc in processes:
            cmdline = proc.get("CommandLine") or ""
            if "heartbeat_watchdog" not in cmdline:
                continue
            # Exclude shims
            wss_str = proc.get("WorkingSetSize", "0")
            try:
                wss = int(wss_str)
            except ValueError:
                wss = 0
            if wss < SHIM_MEMORY_THRESHOLD_BYTES:
                continue
            watchdog_pids.append(proc.get("ProcessId", "?"))

        if len(watchdog_pids) > 1:
            return {
                "instance_count": len(watchdog_pids),
                "pids": watchdog_pids,
                "own_pid": str(own_pid),
                "detected_at": datetime.now().isoformat(timespec="seconds"),
            }
        return None
    else:
        # POSIX fallback — not the primary platform but include for completeness.
        try:
            result = subprocess.run(
                ["pgrep", "-a", "-f", "heartbeat_watchdog"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
            if len(lines) > 1:
                pids = [ln.split()[0] for ln in lines]
                return {
                    "instance_count": len(pids),
                    "pids": pids,
                    "own_pid": str(own_pid),
                    "detected_at": datetime.now().isoformat(timespec="seconds"),
                }
        except Exception:
            pass
        return None


def main() -> None:
    emit(
        "ready",
        {
            "component": "heartbeat_watchdog",
            "poll_s": POLL_INTERVAL_S,
            "idle_threshold_s": IDLE_THRESHOLD_S,
            "cooldown_s": COOLDOWN_S,
            "per_queue_idle_threshold_s": PER_QUEUE_IDLE_THRESHOLD_S,
            "per_queue_idle_cooldown_s": PER_QUEUE_IDLE_COOLDOWN_S,
            "queue_low_threshold": QUEUE_LOW_THRESHOLD,
            "queue_low_cooldown_s": QUEUE_LOW_COOLDOWN_S,
            "queue_severely_low_cooldown_s": QUEUE_SEVERELY_LOW_COOLDOWN_S,
            "routing_ratio_threshold": ROUTING_RATIO_THRESHOLD,
            "routing_ratio_window": ROUTING_RATIO_WINDOW,
            "ship_unconfirmed_threshold_s": SHIP_UNCONFIRMED_THRESHOLD_S,
            "ship_unconfirmed_cooldown_s": SHIP_UNCONFIRMED_COOLDOWN_S,
            "for_you_stale_minutes": FOR_YOU_STALE_MINUTES,
            "for_you_stale_cooldown_s": FOR_YOU_STALE_COOLDOWN_S,
            "research_overdue_hours": RESEARCH_OVERDUE_HOURS,
            "research_overdue_cooldown_s": RESEARCH_OVERDUE_COOLDOWN_S,
            "remote_bridge_cache_pull_interval_s": REMOTE_CACHE_PULL_INTERVAL_S,
            "remote_bridge_cache_source": REMOTE_CACHE_SOURCE,
            "bridge_cache_stale_cooldown_s": BRIDGE_CACHE_STALE_COOLDOWN_S,
            "duplicate_runner_cooldown_s": DUPLICATE_RUNNER_COOLDOWN_S,
            "duplicate_watchdog_cooldown_s": DUPLICATE_WATCHDOG_COOLDOWN_S,
            "event_kinds": [
                "silent_idle",
                "gpu_idle",
                "cpu_idle",
                "gpu_queue_low",
                "cpu_queue_low",
                "ship_unconfirmed",
                "for_you_stale",
                "research_overdue",
                "verdict_landed",
                "bridge_cache_stale",
                "routing_ratio_low",
                "duplicate_runner_detected",
                "duplicate_watchdog_detected",
            ],
        },
    )

    idle_since: float | None = None
    last_fire_ts: float | None = None
    # Per-queue idle clocks and cooldowns (gpu_idle / cpu_idle)
    gpu_idle_since: float | None = None
    cpu_idle_since: float | None = None
    last_gpu_idle_fire_ts: float | None = None
    last_cpu_idle_fire_ts: float | None = None
    # Per-queue low-level clocks and cooldowns (gpu_queue_low / cpu_queue_low)
    last_gpu_low_fire_ts: float | None = None
    last_cpu_low_fire_ts: float | None = None
    last_gpu_severely_low_fire_ts: float | None = None
    last_cpu_severely_low_fire_ts: float | None = None
    last_routing_recompute_ts: float = 0.0
    last_routing_fire_ts: float | None = None
    last_for_you_fire_ts: float | None = None
    last_research_overdue_fire_ts: float | None = None
    last_bridge_stale_fire_ts: float | None = None
    # Per-(queue,name) cooldown timestamps for ship_unconfirmed events.
    # Populated below after _wdog_state is loaded (see ship_unconfirmed_last_fire init).
    ship_unconfirmed_last_fire: dict[str, float] = {}
    # Per-runner-kind cooldown timestamps for duplicate_runner_detected events.
    duplicate_runner_last_fire: dict[str, float] = {}
    last_duplicate_watchdog_fire_ts: float | None = None
    # Periodic state save: persist verdict_last_seen_ts + ship_unconfirmed_last_fire
    # every 5 minutes even when no new verdicts fire, so restarts resume correctly.
    _STATE_SAVE_INTERVAL_S = 300.0
    last_state_save_ts: float = 0.0

    # ---- Event E: verdict_landed — initialise last_seen_ts ----
    # Load from persisted state if available, otherwise bootstrap from the
    # current cache snapshot so old verdicts are never replayed on restart.
    _wdog_state = _load_watchdog_state()

    # ---- Restore ship_unconfirmed cooldown state from persisted snapshot ----
    # PERSISTED in heartbeat_watchdog_state.json so restarts don't reset the
    # cooldown and cause immediate re-fires on entries already surfaced.
    # Values stored as ISO strings — convert to floats here.
    _persisted_su_cooldowns = _wdog_state.get("ship_unconfirmed_last_fire") or {}
    for _k, _v in _persisted_su_cooldowns.items():
        _ts = _parse_ts(_v) if isinstance(_v, str) else None
        if _ts is not None:
            ship_unconfirmed_last_fire[_k] = _ts
    _persisted_ts = _parse_ts(_wdog_state.get("verdict_last_seen_ts"))
    if _persisted_ts is not None:
        verdict_last_seen_ts: float = _persisted_ts
        emit(
            "verdict_landed_init",
            {
                "component": "heartbeat_watchdog",
                "resumed_from": _wdog_state.get("verdict_last_seen_ts"),
            },
        )
    else:
        # First start — snapshot current max ended_at so we don't replay history.
        # Subtract 1 second from max so the newest verdict at bootstrap time
        # still satisfies ts > last_seen_ts and fires on the next poll.
        # This prevents the off-by-one where bootstrap stamps exactly the
        # max verdict timestamp and that verdict is never emitted (since the
        # loop condition is strictly greater-than).
        try:
            from tools.orchestrator.remote_state import get_recent_verdicts as _grv
            _boot_verdicts = _grv(n=50)
            _max_ts: float = 0.0
            for _v in _boot_verdicts:
                _ts = _parse_ts(_v.get("ended_at"))
                if _ts is not None and _ts > _max_ts:
                    _max_ts = _ts
            verdict_last_seen_ts = max(0.0, _max_ts - 1.0)
        except Exception:
            verdict_last_seen_ts = 0.0
        _wdog_state["verdict_last_seen_ts"] = datetime.fromtimestamp(
            verdict_last_seen_ts
        ).isoformat(timespec="seconds") if verdict_last_seen_ts > 0 else None
        _save_watchdog_state(_wdog_state)
        emit(
            "verdict_landed_init",
            {
                "component": "heartbeat_watchdog",
                "bootstrapped_last_seen_ts": _wdog_state.get("verdict_last_seen_ts"),
                "skip_history": True,
            },
        )

    while True:
        try:
            now = time.time()

            # ---- Remote-bridge cache pull (every REMOTE_CACHE_PULL_INTERVAL_S) ----
            pull_remote_state_cache(now)

            payload = evaluate_idle()

            if payload is None:
                # Condition broken — reset the idle clock.
                idle_since = None
            else:
                if idle_since is None:
                    idle_since = now
                idle_seconds = now - idle_since

                # Suppress firing while we are in the post-emit cooldown,
                # UNLESS the condition has just freshly re-armed after recovery.
                in_cooldown = (
                    last_fire_ts is not None and (now - last_fire_ts) < COOLDOWN_S
                )

                if idle_seconds >= IDLE_THRESHOLD_S and not in_cooldown:
                    payload["idle_seconds"] = round(idle_seconds, 1)
                    payload["paused"] = pause_is_set()
                    payload["detected_at"] = datetime.now().isoformat(
                        timespec="seconds"
                    )
                    emit("silent_idle", payload)
                    last_fire_ts = now

            # ---- Per-queue idle events: gpu_idle / cpu_idle ----
            # Fire INDEPENDENTLY so the orchestrator gets an early-warning per
            # lane (e.g. GPU empty while CPU is still busy with 2 pending).
            gpu_q_payload, cpu_q_payload = evaluate_per_queue_idle(now)

            if gpu_q_payload is None:
                gpu_idle_since = None  # GPU lane active — reset clock
            else:
                if gpu_idle_since is None:
                    gpu_idle_since = now
                gpu_idle_seconds = now - gpu_idle_since
                in_gpu_cooldown = (
                    last_gpu_idle_fire_ts is not None
                    and (now - last_gpu_idle_fire_ts) < PER_QUEUE_IDLE_COOLDOWN_S
                )
                if gpu_idle_seconds >= PER_QUEUE_IDLE_THRESHOLD_S and not in_gpu_cooldown:
                    gpu_q_payload["idle_seconds"] = round(gpu_idle_seconds, 1)
                    gpu_q_payload["paused"] = pause_is_set()
                    gpu_q_payload["detected_at"] = datetime.now().isoformat(
                        timespec="seconds"
                    )
                    emit("gpu_idle", gpu_q_payload)
                    last_gpu_idle_fire_ts = now

            if cpu_q_payload is None:
                cpu_idle_since = None  # CPU lane active — reset clock
            else:
                if cpu_idle_since is None:
                    cpu_idle_since = now
                cpu_idle_seconds = now - cpu_idle_since
                in_cpu_cooldown = (
                    last_cpu_idle_fire_ts is not None
                    and (now - last_cpu_idle_fire_ts) < PER_QUEUE_IDLE_COOLDOWN_S
                )
                if cpu_idle_seconds >= PER_QUEUE_IDLE_THRESHOLD_S and not in_cpu_cooldown:
                    cpu_q_payload["idle_seconds"] = round(cpu_idle_seconds, 1)
                    cpu_q_payload["paused"] = pause_is_set()
                    cpu_q_payload["detected_at"] = datetime.now().isoformat(
                        timespec="seconds"
                    )
                    emit("cpu_idle", cpu_q_payload)
                    last_cpu_idle_fire_ts = now

            # ---- Proactive queue-low events: gpu_queue_low / cpu_queue_low ----
            # Fire WHILE the runner is still busy so the orchestrator gets lead
            # time to dispatch an exp_dev refill before the lane goes idle.
            (
                gpu_low_payload,
                cpu_low_payload,
                gpu_severely_low_payload,
                cpu_severely_low_payload,
            ) = evaluate_per_queue_low(now)

            if gpu_low_payload is not None:
                in_gpu_low_cd = (
                    last_gpu_low_fire_ts is not None
                    and (now - last_gpu_low_fire_ts) < QUEUE_LOW_COOLDOWN_S
                )
                if not in_gpu_low_cd:
                    gpu_low_payload["paused"] = pause_is_set()
                    gpu_low_payload["detected_at"] = datetime.now().isoformat(timespec="seconds")
                    emit("gpu_queue_low", gpu_low_payload)
                    last_gpu_low_fire_ts = now

            if cpu_low_payload is not None:
                in_cpu_low_cd = (
                    last_cpu_low_fire_ts is not None
                    and (now - last_cpu_low_fire_ts) < QUEUE_LOW_COOLDOWN_S
                )
                if not in_cpu_low_cd:
                    cpu_low_payload["paused"] = pause_is_set()
                    cpu_low_payload["detected_at"] = datetime.now().isoformat(timespec="seconds")
                    emit("cpu_queue_low", cpu_low_payload)
                    last_cpu_low_fire_ts = now

            if gpu_severely_low_payload is not None:
                in_gpu_sl_cd = (
                    last_gpu_severely_low_fire_ts is not None
                    and (now - last_gpu_severely_low_fire_ts) < QUEUE_SEVERELY_LOW_COOLDOWN_S
                )
                if not in_gpu_sl_cd:
                    gpu_severely_low_payload["paused"] = pause_is_set()
                    gpu_severely_low_payload["detected_at"] = datetime.now().isoformat(timespec="seconds")
                    emit("gpu_queue_low", gpu_severely_low_payload)
                    last_gpu_severely_low_fire_ts = now

            if cpu_severely_low_payload is not None:
                in_cpu_sl_cd = (
                    last_cpu_severely_low_fire_ts is not None
                    and (now - last_cpu_severely_low_fire_ts) < QUEUE_SEVERELY_LOW_COOLDOWN_S
                )
                if not in_cpu_sl_cd:
                    cpu_severely_low_payload["paused"] = pause_is_set()
                    cpu_severely_low_payload["detected_at"] = datetime.now().isoformat(timespec="seconds")
                    emit("cpu_queue_low", cpu_severely_low_payload)
                    last_cpu_severely_low_fire_ts = now

            # ---- Condition 2: ship_unconfirmed (audit rec #2) ----
            # Read sentinel + dashboard snapshot, fire one event per overdue
            # attempt that has not appeared in the queue dashboard within
            # SHIP_UNCONFIRMED_THRESHOLD_S. Cooldown is per (queue,name).
            snap_doc = load_json(DASHBOARD) or {}
            ship_payloads = evaluate_ship_unconfirmed(
                snap_doc, ship_unconfirmed_last_fire, now
            )
            for sp in ship_payloads:
                sp["paused"] = pause_is_set()
                sp["detected_at"] = datetime.now().isoformat(timespec="seconds")
                emit("ship_unconfirmed", sp)

            # ---- Routing-ratio enforcement (audit rec #3) ----
            # Recompute periodically; fire routing_ratio_low if below target.
            if now - last_routing_recompute_ts >= ROUTING_RATIO_RECOMPUTE_S:
                last_routing_recompute_ts = now
                primary = recompute_routing_ratio()
                rr_payload = evaluate_routing_ratio(primary)
                if rr_payload is not None:
                    in_rr_cooldown = (
                        last_routing_fire_ts is not None
                        and (now - last_routing_fire_ts) < ROUTING_RATIO_COOLDOWN_S
                    )
                    if not in_rr_cooldown:
                        rr_payload["detected_at"] = datetime.now().isoformat(
                            timespec="seconds"
                        )
                        rr_payload["paused"] = pause_is_set()
                        emit("routing_ratio_low", rr_payload)
                        last_routing_fire_ts = now

            # ---- Event C: for_you_stale ----
            # Fires when status_log has not been written in FOR_YOU_STALE_MINUTES.
            fy_payload = evaluate_for_you_stale(now)
            if fy_payload is not None:
                in_fy_cooldown = (
                    last_for_you_fire_ts is not None
                    and (now - last_for_you_fire_ts) < FOR_YOU_STALE_COOLDOWN_S
                )
                if not in_fy_cooldown:
                    fy_payload["detected_at"] = datetime.now().isoformat(timespec="seconds")
                    emit("for_you_stale", fy_payload)
                    last_for_you_fire_ts = now

            # ---- Event D: research_overdue ----
            # Fires when no research event written in RESEARCH_OVERDUE_HOURS.
            ro_payload = evaluate_research_overdue(now)
            if ro_payload is not None:
                in_ro_cooldown = (
                    last_research_overdue_fire_ts is not None
                    and (now - last_research_overdue_fire_ts) < RESEARCH_OVERDUE_COOLDOWN_S
                )
                if not in_ro_cooldown:
                    ro_payload["detected_at"] = datetime.now().isoformat(timespec="seconds")
                    emit("research_overdue", ro_payload)
                    last_research_overdue_fire_ts = now

            # ---- Event E: verdict_landed ----
            # One event per new verdict in the bridge cache since last poll.
            # No cooldown — each distinct verdict fires exactly once.
            vl_payloads, verdict_last_seen_ts = evaluate_verdict_landed(
                verdict_last_seen_ts
            )
            if vl_payloads:
                for vl in vl_payloads:
                    vl["detected_at"] = datetime.now().isoformat(timespec="seconds")
                    emit("verdict_landed", vl)
                # Persist updated last_seen_ts + ship_unconfirmed cooldowns so
                # restarts don't replay verdicts or re-fire cooled-down names.
                _wdog_state["verdict_last_seen_ts"] = datetime.fromtimestamp(
                    verdict_last_seen_ts
                ).isoformat(timespec="seconds")
                _wdog_state["ship_unconfirmed_last_fire"] = {
                    k: datetime.fromtimestamp(v).isoformat(timespec="seconds")
                    for k, v in ship_unconfirmed_last_fire.items()
                }
                _save_watchdog_state(_wdog_state)
                last_state_save_ts = now
            elif now - last_state_save_ts >= _STATE_SAVE_INTERVAL_S:
                # Periodic heartbeat save: persist current last_seen_ts AND
                # ship_unconfirmed cooldowns so a crash/restart resumes correctly
                # rather than re-bootstrapping from cache max or re-firing names.
                _wdog_state["verdict_last_seen_ts"] = (
                    datetime.fromtimestamp(verdict_last_seen_ts).isoformat(timespec="seconds")
                    if verdict_last_seen_ts > 0 else None
                )
                _wdog_state["ship_unconfirmed_last_fire"] = {
                    k: datetime.fromtimestamp(v).isoformat(timespec="seconds")
                    for k, v in ship_unconfirmed_last_fire.items()
                }
                _save_watchdog_state(_wdog_state)
                last_state_save_ts = now

            # ---- Event F: bridge_cache_stale ----
            # Fires when the remote_state_cache.json is older than WARN_AGE_S
            # (120s), meaning the SCP pull from marsh@home has broken.
            # Cooldown BRIDGE_CACHE_STALE_COOLDOWN_S between fires.
            try:
                from tools.orchestrator.remote_state import is_stale as _cache_is_stale, _cache_age_s as _cache_age
                if _cache_is_stale():
                    in_bridge_cooldown = (
                        last_bridge_stale_fire_ts is not None
                        and (now - last_bridge_stale_fire_ts) < BRIDGE_CACHE_STALE_COOLDOWN_S
                    )
                    if not in_bridge_cooldown:
                        age_s = _cache_age()
                        bridge_payload = {
                            "cache_age_s": round(age_s, 1) if age_s is not None else None,
                            "warn_threshold_s": 120.0,
                            "paused": pause_is_set(),
                            "detected_at": datetime.now().isoformat(timespec="seconds"),
                            "action": "re-establish bridge before relying on remote state",
                        }
                        emit("bridge_cache_stale", bridge_payload)
                        last_bridge_stale_fire_ts = now
            except Exception:
                pass  # bridge_cache_stale check is non-fatal

            # ---- Event G: duplicate_runner_detected ----
            # SSH to marsh@home; enumerate Python processes; detect >1 real
            # interpreter per runner kind.  Cooldown 900s per runner kind.
            try:
                dr_payloads = evaluate_duplicate_runner(now)
                for dr_payload in dr_payloads:
                    kind = dr_payload["runner_kind"]
                    last_dr = duplicate_runner_last_fire.get(kind)
                    in_dr_cooldown = (
                        last_dr is not None
                        and (now - last_dr) < DUPLICATE_RUNNER_COOLDOWN_S
                    )
                    if not in_dr_cooldown:
                        emit("duplicate_runner_detected", dr_payload)
                        duplicate_runner_last_fire[kind] = now
            except Exception:
                pass  # duplicate_runner check is non-fatal

            # ---- Event H: duplicate_watchdog_detected ----
            # Check THIS machine for multiple heartbeat_watchdog.py instances.
            # Cooldown 900s between fires.
            try:
                dw_payload = evaluate_duplicate_watchdog()
                if dw_payload is not None:
                    in_dw_cooldown = (
                        last_duplicate_watchdog_fire_ts is not None
                        and (now - last_duplicate_watchdog_fire_ts) < DUPLICATE_WATCHDOG_COOLDOWN_S
                    )
                    if not in_dw_cooldown:
                        emit("duplicate_watchdog_detected", dw_payload)
                        last_duplicate_watchdog_fire_ts = now
            except Exception:
                pass  # duplicate_watchdog check is non-fatal

            # ---- New-routing auto-ping (Part C layer 1) ----
            # Detect routing files that landed in any session's inbox since
            # the last tick. Fires one `new_routing` event per new file.
            # Persists the seen-set in heartbeat_watchdog_state.json so a
            # restart doesn't re-fire everything that was already surfaced.
            # First-boot bootstrap: snapshot CURRENT files as seen so we don't
            # spam the For-You feed with the entire historical inbox.
            try:
                _seen_routings_list = _wdog_state.get("seen_routings") or []
                _is_bootstrap = "seen_routings" not in _wdog_state
                _seen_routings: set[str] = set(_seen_routings_list)
                _new_payloads, _current_set = evaluate_new_routings(_seen_routings)
                if _is_bootstrap:
                    # On first boot, snapshot current state as seen; suppress
                    # the firehose. Only files appearing AFTER bootstrap emit.
                    emit("new_routing_init", {
                        "component": "heartbeat_watchdog",
                        "bootstrapped_seen_count": len(_current_set),
                        "skip_history": True,
                    })
                else:
                    for _np in _new_payloads:
                        emit("new_routing", _np)
                _wdog_state["seen_routings"] = sorted(_current_set)
                _save_watchdog_state(_wdog_state)
            except Exception:
                pass  # new-routing detection is non-fatal

            time.sleep(POLL_INTERVAL_S)
        except KeyboardInterrupt:
            emit("stopped", {"component": "heartbeat_watchdog"})
            return
        except Exception as e:
            emit("error", {"component": "heartbeat_watchdog", "message": str(e)})
            time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    main()
