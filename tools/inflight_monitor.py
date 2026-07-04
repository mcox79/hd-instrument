"""Proactive in-flight experiment monitor for the hd-instrument fleet.

USER 2026-07-04: "you also need a more proactive way to monitor the experiments in
flight." The prior posture was reactive -- per-dispatch landing monitors +
20-min Director polls -- so an OOM crash / stalled runner / silently-dead feed
was only discovered on the next manual poll. This tool gives the Director an
always-current, one-command view of what is ACTUALLY in flight, and pushes a
Director-visible pane + alert stream on state-change (no manual ssh each time).

Design (reuses existing pieces; no reinvention):
  * Live GPU + feed freshness   <- dashboard localhost HTTP (/api/runs, /api/system,
                                   /api/health). The dashboard already does the SSH;
                                   we read localhost so the monitor is popup-free and
                                   needs no SSH of its own. Dashboard-unreachable is
                                   itself a CRITICAL alert (the recurring silent
                                   supervisor-death case).
  * Queues + runners + procs    <- data/remote_state_cache.json (emitter->SCP, no SSH)
                                   plus local_cpu_queue/queue.json (local read).
  * Notify-on-change surface    <- data/inflight_status.md pane (turn-start Read) +
                                   data/inflight_alerts.jsonl transitions, mirroring
                                   tools/landing_notifier.py's pane+jsonl pattern.

Crash / stall detection (alerts, never silent):
  DASHBOARD_DOWN      dashboard HTTP unreachable (supervisor/uvicorn dead)
  FEED_STALE          dashboard SSH poll last-ok > 90s (remote feed dead)
  CACHE_STALE         remote_state_cache file mtime > 300s (emitter/SCP dead)
  RUNNER_HB_STALE     a runner heartbeat_ts older than 300s while marked running
  GPU_EXP_UNTRACKED   a substrate experiment is on the GPU but no queue tracks it
  GPU_RUNNER_STALL    runner says running but GPU util ~0 for the sustained window
  ZOMBIE              pid dead while queue still marks the entry running
  QUEUE_FAILED        a queue entry newly flipped to failed/killed (the OOM case)

Invocation:
  python tools/inflight_monitor.py               # one-shot human report
  python tools/inflight_monitor.py --json        # machine-readable
  python tools/inflight_monitor.py --alerts-only # print only current alerts
  python tools/inflight_monitor.py --watch [--interval 60]   # loop + push on change

The --watch mode is the proactive engine: register it as a scheduled task
(companion to landing_notifier) or run it in a background terminal. On every
state transition it appends to inflight_alerts.jsonl and rewrites
inflight_status.md so the Director sees the change at the next turn-start.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Direct-launched local experiment scanner (queue-bypassing agent runs). Imported
# so this monitor sees the priority experiment even when the dashboard is DOWN --
# the exact case (supervisor death) where you most need to know what's training.
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)
try:
    from local_exp_scan import scan_local_experiments
except Exception:  # pragma: no cover - fail-open
    def scan_local_experiments() -> list[dict]:
        return []
DATA = REPO / "data"
CACHE = DATA / "remote_state_cache.json"
LOCAL_CPU_QUEUE = DATA / "local_cpu_queue" / "queue.json"
STATUS_PANE = DATA / "inflight_status.md"
ALERTS_LOG = DATA / "inflight_alerts.jsonl"
STATE_FILE = DATA / ".inflight_monitor_state.json"

DASHBOARD = "http://127.0.0.1:8765"

# Thresholds (seconds)
FEED_STALE_S = 90.0        # dashboard SSH poll age
CACHE_STALE_S = 300.0      # remote_state_cache file mtime age
RUNNER_HB_STALE_S = 300.0  # runner heartbeat age while running
GPU_STALL_UTIL = 5         # util at/below this + runner-running for the window = stall

# Direct-SSH GPU fallback (testbed 2026-07-04). The dashboard's localhost HTTP
# poll is the ONLY GPU source, so when the web supervisor/poller dies the GPU
# reading goes dark -- and "is the GPU idle?" is exactly the reading that most
# matters and that historically misfired via the broken poller. When the feed is
# DOWN/STALE we fall back to a short one-shot `ssh <alias> nvidia-smi` with a hard
# subprocess timeout so it can never hang a refresh. This is a SHORT probe (not a
# long-lived remote child), so raw SSH is fine -- the disconnect-death concern is
# only about long-running processes.
#
# SSH_ALIAS matches tools/dashboard/ssh_client.py ReadOnlySSH's default alias
# ("home"); `ssh <alias>` and paramiko's SSHConfig.lookup(alias) both resolve the
# SAME ~/.ssh/config, so this reuses the existing host resolution rather than
# hardcoding a fresh hostname/IP.
SSH_ALIAS = "home"
GPU_SSH_TIMEOUT_S = 4.0     # subprocess-internal cap on the probe
GPU_SSH_CONNECT_TIMEOUT_S = 3  # ssh -o ConnectTimeout; fail fast, never prompt
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)  # popup-free (windowless mandate)

# ---------------------------------------------------------------------------
# HARD WALL-CLOCK BUDGETS (regression fix 2026-07-04: build_state() hung >2min).
# build_state() is the Director's primary status tool AND the GUI's 7s refresh
# source, so it must NEVER block. Each external/blocking data source (dashboard
# HTTP, WMIC local scan, SSH nvidia-smi) has its OWN subprocess/socket timeout,
# but those can be defeated by pathologies the internal timeout doesn't cover
# (DNS getaddrinfo stalls, a half-dead server that accepts but never replies, the
# subprocess double-communicate-after-kill hang when a grandchild inherits the
# pipe). So every source ALSO runs under a wall-clock thread-join cap here that
# CANNOT be defeated by any subprocess/socket internal: if a source exceeds its
# budget the worker thread is abandoned (daemon; leaks harmlessly, reclaimed at
# process exit) and that section returns unavailable + an explicit alert. The 3
# always-run sources run CONCURRENTLY under one shared budget, so worst-case total
# build_state() wall time is PRIMARY_BUDGET_S + (SSH only when feed is down).
PRIMARY_BUDGET_S = 5.0     # shared cap for the concurrent {health, runs, local scan} gather
GPU_SSH_BUDGET_S = 5.0     # wall cap on the SSH fallback (fires only when feed is DOWN/STALE)
# => worst case ~10s (feed down + ssh pathological); feed-up worst ~5s; clean <1s.


# ---------------------------------------------------------------------------
# Source reads (all popup-free; dashboard = localhost HTTP, rest = local files)
# ---------------------------------------------------------------------------

def _bounded(fn, timeout_s: float, default=None):
    """Run fn() in a daemon thread; return (result, completed). On timeout returns
    (default, False) and ABANDONS the thread so the caller is never blocked longer
    than timeout_s -- the wall-clock guarantee that no subprocess/socket internal
    pathology can defeat. The abandoned daemon thread is reclaimed at process exit."""
    box = {"v": default, "done": False}

    def _run():
        try:
            box["v"] = fn()
        except Exception:
            box["v"] = default
        finally:
            box["done"] = True

    th = threading.Thread(target=_run, daemon=True)
    th.start()
    th.join(timeout_s)
    return box["v"], box["done"]


def _gather(jobs: dict, timeout_s: float) -> dict:
    """Run several callables CONCURRENTLY under one shared wall-clock deadline.
    jobs: name -> callable. Returns name -> (result, completed). Total wall time is
    bounded by timeout_s regardless of how many jobs wedge (each runs in its own
    daemon thread; wedged ones are abandoned)."""
    boxes = {n: {"v": None, "done": False} for n in jobs}
    threads = []
    for n, fn in jobs.items():
        def _mk(name, f):
            def _run():
                try:
                    boxes[name]["v"] = f()
                except Exception:
                    pass
                finally:
                    boxes[name]["done"] = True
            return _run
        t = threading.Thread(target=_mk(n, fn), daemon=True)
        t.start()
        threads.append(t)
    deadline = time.time() + timeout_s
    for t in threads:
        t.join(max(0.0, deadline - time.time()))
    return {n: (b["v"], b["done"]) for n, b in boxes.items()}


def _http_json(path: str, timeout: float = 3.0) -> dict | None:
    try:
        with urllib.request.urlopen(DASHBOARD + path, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError):
        return None


def _load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _naive_or_utc_age_s(ts: str | None) -> float | None:
    """Age of an ISO timestamp. tz-aware honored; naive treated as UTC (best-effort)."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except (ValueError, TypeError):
        return None


def _file_age_s(path: Path) -> float | None:
    try:
        return max(0.0, time.time() - path.stat().st_mtime)
    except OSError:
        return None


def _same_basis_delta_s(later: str | None, earlier: str | None) -> float | None:
    """(later - earlier) in seconds. Both timestamps are compared on the SAME basis
    (tz stripped) so a naive remote-local snapshot_ts vs naive remote-local
    heartbeat_ts yields a correct delta regardless of the remote's timezone --
    avoids the 4h skew from treating naive-local as UTC."""
    try:
        a = datetime.fromisoformat(str(later).replace("Z", "+00:00")).replace(tzinfo=None)
        b = datetime.fromisoformat(str(earlier).replace("Z", "+00:00")).replace(tzinfo=None)
        return (a - b).total_seconds()
    except (ValueError, TypeError, AttributeError):
        return None


def _queue_running_pending(entries: list[dict]) -> tuple[list[str], list[str], list[dict]]:
    """(running_names, pending_names, terminal_entries) from a queue entry list."""
    running, pending, terminal = [], [], []
    for e in entries or []:
        if not isinstance(e, dict):
            continue
        st = (e.get("status") or "").lower()
        nm = e.get("name") or "?"
        if st == "running":
            running.append(nm)
        elif st in ("pending", "queued", "claimed"):
            pending.append(nm)
        elif st in ("failed", "killed", "error", "oom"):
            terminal.append({"name": nm, "status": st})
    return running, pending, terminal


def probe_gpu_via_ssh() -> dict | None:
    """One-shot `ssh <SSH_ALIAS> nvidia-smi` GPU probe. None on any failure/timeout.

    Fallback for when the dashboard feed is DOWN/STALE. Returns
    {util_pct, mem_used_mb, temp_c, source:"ssh", queried_at} on success. Hardened
    against hangs: ConnectTimeout (connect stall) + ServerAlive (post-connect
    handshake/read stall) + BatchMode (never prompt) + ControlMaster=no/
    ControlPath=none (never spawn or reuse a persistent master whose surviving pipe
    would defeat the subprocess timeout) + stdin=DEVNULL + subprocess timeout.
    Popup-free via CREATE_NO_WINDOW. Never raises. The caller ALSO runs this under
    a wall-clock cap (_bounded) as the final backstop, so even a pathology that
    slips every option above cannot block build_state().
    """
    cmd = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", f"ConnectTimeout={GPU_SSH_CONNECT_TIMEOUT_S}",
        "-o", "ServerAliveInterval=2",
        "-o", "ServerAliveCountMax=2",
        "-o", "ControlMaster=no",
        "-o", "ControlPath=none",
        SSH_ALIAS,
        "nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu "
        "--format=csv,noheader,nounits",
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=GPU_SSH_TIMEOUT_S, creationflags=_NO_WINDOW,
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if proc.returncode != 0:
        return None
    # First non-empty stdout line = the (first) GPU's "util, mem, temp" (nounits).
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            return None
        try:
            return {
                "util_pct": int(float(parts[0])),
                "mem_used_mb": int(float(parts[1])),
                "temp_c": int(float(parts[2])),
                "source": "ssh",
                "queried_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        except (ValueError, TypeError):
            return None
    return None


# ---------------------------------------------------------------------------
# Snapshot assembly + alert derivation
# ---------------------------------------------------------------------------

def build_state() -> dict:
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    alerts: list[dict] = []

    # --- Primary sources gathered CONCURRENTLY under one shared wall-clock cap ---
    # dashboard /api/health + /api/runs (localhost HTTP) and the local WMIC
    # experiment scan are independent and each can block (half-dead server / wedged
    # WMI). Running them concurrently under PRIMARY_BUDGET_S bounds total wall time
    # to the budget (not the sum) and guarantees build_state() returns even if any
    # of them wedges. A wedged source returns unavailable + an explicit alert.
    gathered = _gather({
        "health": lambda: _http_json("/api/health"),
        "runs": lambda: _http_json("/api/runs"),
        "local": scan_local_experiments,
    }, PRIMARY_BUDGET_S)
    health, health_done = gathered["health"]
    runs, runs_done = gathered["runs"]
    local_experiments, local_done = gathered["local"]
    if not isinstance(local_experiments, list):
        local_experiments = []
    if not local_done:
        alerts.append({"level": "WARN", "code": "LOCAL_SCAN_TIMEOUT",
                       "msg": f"local experiment scan (WMIC) exceeded {PRIMARY_BUDGET_S:.0f}s "
                              f"and was abandoned; off-queue local runs may be hidden this tick"})
    if not (health_done and runs_done):
        alerts.append({"level": "WARN", "code": "FEED_TIMEOUT",
                       "msg": f"dashboard HTTP did not respond within {PRIMARY_BUDGET_S:.0f}s "
                              f"(half-dead server?); treating GPU feed as unavailable"})

    # --- Dashboard live view (GPU truth + feed freshness) ---
    dashboard_up = health is not None and runs is not None
    if not dashboard_up:
        alerts.append({"level": "CRITICAL", "code": "DASHBOARD_DOWN",
                       "msg": "dashboard localhost:8765 unreachable (supervisor/uvicorn dead?)"})

    feed = (runs or {}).get("_feed", {}) if isinstance(runs, dict) else {}
    feed_age = feed.get("age_s")
    if dashboard_up and feed.get("stale"):
        alerts.append({"level": "CRITICAL", "code": "FEED_STALE",
                       "msg": f"remote SSH poll stale ({feed_age}s > {FEED_STALE_S}s); "
                              f"GPU/runner status is FROZEN, last_error={feed.get('last_error')}"})

    gpu = (runs or {}).get("gpu", {}) if isinstance(runs, dict) else {}
    gpu_util = gpu.get("gpu_util_ema")
    if gpu_util is None:
        gpu_util = gpu.get("gpu_util_pct")

    # --- Direct-SSH GPU fallback when the feed can't be trusted ---
    # The feed-up path is UNCHANGED (gpu_source="feed"). Only when the dashboard
    # is DOWN or the SSH poll is STALE do we run the short one-shot ssh nvidia-smi
    # probe, so "is the GPU idle?" survives the web supervisor dying. The probe has
    # its own subprocess timeout AND runs here under a wall-clock cap (_bounded) so
    # a pathological SSH (DNS stall, handshake hang, grandchild pipe) can never
    # block build_state(). On probe failure/timeout gpu_source stays "stale" and
    # the graceful stale rendering is preserved.
    feed_trustworthy = dashboard_up and not feed.get("stale")
    gpu_source = "feed" if feed_trustworthy else "stale"
    ssh_gpu = None
    if not feed_trustworthy:
        ssh_gpu, ssh_done = _bounded(probe_gpu_via_ssh, GPU_SSH_BUDGET_S, None)
        if not ssh_done:
            alerts.append({"level": "WARN", "code": "GPU_SSH_TIMEOUT",
                           "msg": f"direct SSH nvidia-smi probe exceeded {GPU_SSH_BUDGET_S:.0f}s "
                                  f"and was abandoned; GPU reading unavailable this tick"})
            ssh_gpu = None
        if ssh_gpu is not None:
            gpu_source = "ssh"
            gpu_util = ssh_gpu["util_pct"]

    # --- Cache view (queues, runners, logical procs) ---
    cache = _load_json(CACHE) if CACHE.is_file() else None
    cache_age = _file_age_s(CACHE)
    if cache_age is not None and cache_age > CACHE_STALE_S:
        alerts.append({"level": "WARN", "code": "CACHE_STALE",
                       "msg": f"remote_state_cache {int(cache_age)}s old "
                              f"(> {int(CACHE_STALE_S)}s); emitter/SCP-back may be dead"})

    queues: dict[str, dict] = {}
    runners: dict[str, dict] = {}
    if isinstance(cache, dict):
        # Prefer the naive-local snapshot_ts as the delta baseline (same tz basis as
        # heartbeat_ts). Effective runner-hb age = (snapshot - heartbeat) + cache file age.
        snap_ts = cache.get("snapshot_ts")
        cq = cache.get("queues", {})
        for qname in ("overnight_queue", "remote_cpu_queue"):
            run, pend, term = _queue_running_pending(cq.get(qname, []))
            queues[qname] = {"running": run, "pending": pend, "terminal_recent": term}
        # runners
        for rid, r in (cache.get("runners") or {}).items():
            if not isinstance(r, dict):
                continue
            hb_lag = _same_basis_delta_s(snap_ts, r.get("heartbeat_ts"))
            eff_age = None
            if hb_lag is not None:
                eff_age = max(0.0, hb_lag) + (cache_age or 0.0)
            runners[rid] = {
                "status": r.get("status"), "current": r.get("current"),
                "pid": r.get("pid"), "heartbeat_age_s": round(eff_age, 1) if eff_age is not None else None,
                "alive": r.get("alive"),
            }
            if (r.get("status") == "running" and eff_age is not None
                    and eff_age > RUNNER_HB_STALE_S):
                alerts.append({"level": "CRITICAL", "code": "RUNNER_HB_STALE",
                               "msg": f"{rid} marked running but heartbeat ~{int(eff_age)}s old "
                                      f"(current={r.get('current')}); runner stalled/crashed?"})

    # --- Local CPU queue (local read) ---
    lcq = _load_json(LOCAL_CPU_QUEUE) if LOCAL_CPU_QUEUE.is_file() else None
    if isinstance(lcq, dict):
        run, pend, term = _queue_running_pending(lcq.get("experiments", []))
        queues["local_cpu_queue"] = {"running": run, "pending": pend, "terminal_recent": term}

    # --- GPU reconciliation alerts (from the dashboard's enriched runs.gpu) ---
    if dashboard_up and isinstance(gpu, dict):
        if gpu.get("gpu_queue_mismatch"):
            who = gpu.get("gpu_exp_name") or (gpu.get("gpu_top_proc") or {}).get("pid")
            alerts.append({"level": "WARN", "code": "GPU_EXP_UNTRACKED",
                           "msg": f"substrate experiment on GPU ({who}) but no queue tracks it "
                                  f"(util {gpu_util}%); direct dispatch or queue lag"})
        # runner says running but GPU idle for the sustained (EMA) window = stall
        if (gpu.get("status") == "running" and isinstance(gpu_util, (int, float))
                and gpu_util <= GPU_STALL_UTIL):
            alerts.append({"level": "WARN", "code": "GPU_RUNNER_STALL",
                           "msg": f"gpu runner marks '{gpu.get('current')}' running but "
                                  f"GPU util {gpu_util}% (EMA) -- possible stall/hang"})
        cache_note = gpu.get("gpu_logical_age_s")
        # zombie: pid dead while queue marks running (dashboard computes pid_alive)
        for qk in ("gpu", "cpu", "local_cpu"):
            rr = (runs or {}).get(qk, {})
            if isinstance(rr, dict) and rr.get("pid_alive") is False and rr.get("queue_marks_running"):
                alerts.append({"level": "CRITICAL", "code": "ZOMBIE",
                               "msg": f"{qk} queue marks '{rr.get('current')}' running but pid "
                                      f"{rr.get('pid')} is dead (zombie/crashed)"})
    else:
        cache_note = None

    # GPU display values: prefer the SSH-probe numbers when the feed was untrusted
    # and the probe succeeded (source="ssh"); otherwise the feed's own values. The
    # SSH probe carries no EMA, so util_ema is None and downstream util-selection
    # (util_ema or util_pct) picks the raw util_pct.
    if gpu_source == "ssh" and ssh_gpu is not None:
        disp_util_pct, disp_util_ema = ssh_gpu["util_pct"], None
        disp_mem, disp_temp = ssh_gpu["mem_used_mb"], ssh_gpu["temp_c"]
    else:
        disp_util_pct, disp_util_ema = gpu.get("gpu_util_pct"), gpu.get("gpu_util_ema")
        disp_mem, disp_temp = gpu.get("gpu_mem_used_mb"), gpu.get("gpu_temp_c")

    state = {
        "ts": now_iso,
        "dashboard_up": dashboard_up,
        "feed": {"stale": bool(feed.get("stale")), "age_s": feed_age,
                 "last_poll_ok": feed.get("last_poll_ok")},
        "cache_age_s": round(cache_age, 1) if cache_age is not None else None,
        "gpu": {
            "util_pct": disp_util_pct, "util_ema": disp_util_ema,
            "mem_used_mb": disp_mem, "temp_c": disp_temp,
            "source": gpu_source,  # "feed" | "ssh" | "stale"
            "source_ts": ssh_gpu["queried_at"] if ssh_gpu else None,
            "queue_status": gpu.get("status"), "current": gpu.get("current"),
            "experiment_on_card": gpu.get("gpu_experiment_on_card"),
            "exp_name": gpu.get("gpu_exp_name"),
            "elapsed_s": gpu.get("elapsed_s"), "progress_pct": gpu.get("progress_pct"),
            "eta_sec": gpu.get("eta_sec"),
            "last_line": (gpu.get("stdout_tail") or [""])[-1] if gpu.get("stdout_tail") else "",
            "cache_logical_age_s": cache_note,
        },
        "queues": queues,
        "runners": runners,
        "local_experiments": local_experiments,
        "alerts": alerts,
        "alert_codes": sorted({a["code"] for a in alerts}),
    }
    return state


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _fmt_dur(s) -> str:
    if not isinstance(s, (int, float)):
        return "?"
    s = int(s)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m{s % 60:02d}s"
    return f"{s // 3600}h{(s % 3600) // 60:02d}m"


def render_human(st: dict) -> str:
    L: list[str] = []
    L.append(f"IN-FLIGHT MONITOR  {st['ts']}")
    L.append("=" * 60)
    # Alerts first (loudest)
    if st["alerts"]:
        L.append("ALERTS:")
        for a in st["alerts"]:
            L.append(f"  [{a['level']}] {a['code']}: {a['msg']}")
    else:
        L.append("ALERTS: none")
    L.append("")
    # GPU line
    g = st["gpu"]
    dash = "up" if st["dashboard_up"] else "DOWN"
    feed = st["feed"]
    feed_txt = f"feed {'STALE' if feed['stale'] else 'live'}"
    if feed.get("age_s") is not None:
        feed_txt += f" ({feed['age_s']}s)"
    util = g["util_ema"] if g["util_ema"] is not None else g["util_pct"]
    L.append(f"DASHBOARD: {dash} | {feed_txt} | cache {_fmt_dur(st['cache_age_s'])} old")
    src = g.get("source")
    src_txt = {"feed": "via feed", "ssh": "via SSH (feed DOWN)", "stale": "STALE"}.get(src, "?")
    gpu_line = (f"GPU: util {util}% | mem {g['mem_used_mb']}MB | {g['temp_c']}C | "
                f"queue={g['queue_status']} | src={src_txt}")
    L.append(gpu_line)
    # Ownership call-out: distinguish OUR work from external/BOINC on a high util.
    if src == "feed" and isinstance(util, (int, float)) and util >= 25:
        if g.get("queue_status") == "running" or g.get("experiment_on_card"):
            L.append("  -> OUR WORK on GPU")
        else:
            L.append("  -> external load (BOINC/other); our queue idle")
    if g["experiment_on_card"] and g["exp_name"]:
        prog = f" {g['progress_pct']}%" if g.get("progress_pct") is not None else ""
        eta = f" eta {_fmt_dur(g['eta_sec'])}" if g.get("eta_sec") else ""
        L.append(f"  on card: {g['exp_name']}{prog}{eta} (elapsed {_fmt_dur(g.get('elapsed_s'))})")
        if g.get("last_line"):
            L.append(f"    -> {g['last_line'][:110]}")
    elif g["current"]:
        L.append(f"  running (queue): {g['current']}")
    L.append("")
    # Local direct-launched experiments (queue-bypassing agent subprocesses)
    lx = st.get("local_experiments") or []
    if lx:
        L.append("LOCAL EXPERIMENTS (direct subprocess, off-queue):")
        for e in lx:
            args = e.get("args") or {}
            atxt = " ".join(f"{k}={v}" for k, v in args.items())
            prog = ""
            if e.get("progress_pct") is not None:
                prog = (f" [{e.get('unit_idx')}/{e.get('total_units')} "
                        f"{int(e['progress_pct'])}%"
                        + (f" eta {_fmt_dur(e['eta_s'])}" if e.get("eta_s") else "")
                        + (f" {e['phase']}" if e.get("phase") else "") + "]")
            L.append(f"  {e.get('name')}  pid={e.get('pid')} "
                     f"elapsed={_fmt_dur(e.get('elapsed_s'))} "
                     f"mem={int((e.get('mem_kb') or 0) / 1024)}MB {atxt}{prog}".rstrip())
        L.append("")
    # Queues
    L.append("QUEUES:")
    for qname, q in st["queues"].items():
        run = ",".join(q["running"]) or "-"
        L.append(f"  {qname}: running=[{run}] pending={len(q['pending'])}")
        for t in q.get("terminal_recent", [])[:3]:
            L.append(f"      recent terminal: {t['name']} = {t['status']}")
    # Runners
    if st["runners"]:
        L.append("RUNNERS:")
        for rid, r in st["runners"].items():
            L.append(f"  {rid}: {r['status']} pid={r['pid']} "
                     f"hb_age={_fmt_dur(r['heartbeat_age_s'])} current={r['current']}")
    return "\n".join(L)


def render_pane(st: dict) -> str:
    """Director turn-start surface -- overwrite each tick (like latest_landings.md)."""
    agg = "RED" if any(a["level"] == "CRITICAL" for a in st["alerts"]) else (
        "WARN" if st["alerts"] else "OK")
    g = st["gpu"]
    util = g["util_ema"] if g["util_ema"] is not None else g["util_pct"]
    lines = [
        "# In-flight monitor (auto-refreshed by tools/inflight_monitor.py --watch)",
        "",
        f"**Refreshed:** {st['ts']}  |  **Status:** {agg}  |  "
        f"**Dashboard:** {'up' if st['dashboard_up'] else 'DOWN'}  |  "
        f"**Feed:** {'STALE' if st['feed']['stale'] else 'live'}  |  "
        f"**Cache:** {_fmt_dur(st['cache_age_s'])} old",
        "",
    ]
    if st["alerts"]:
        lines.append("## Alerts")
        for a in st["alerts"]:
            lines.append(f"- **[{a['level']}] {a['code']}** — {a['msg']}")
        lines.append("")
    lines.append("## GPU")
    src = g.get("source")
    src_txt = {"feed": "via feed", "ssh": "via SSH (feed DOWN)", "stale": "STALE"}.get(src, "?")
    lines.append(f"- util **{util}%** · mem {g['mem_used_mb']}MB · {g['temp_c']}C · "
                 f"queue={g['queue_status']} · src={src_txt}")
    if src == "feed" and isinstance(util, (int, float)) and util >= 25:
        if g.get("queue_status") == "running" or g.get("experiment_on_card"):
            lines.append("- **OUR WORK on GPU**")
        else:
            lines.append("- external load (BOINC/other); our queue idle")
    if g["experiment_on_card"] and g["exp_name"]:
        prog = f" · {g['progress_pct']}%" if g.get("progress_pct") is not None else ""
        lines.append(f"- on card: `{g['exp_name']}`{prog} (elapsed {_fmt_dur(g.get('elapsed_s'))})")
    lines.append("")
    lx = st.get("local_experiments") or []
    if lx:
        lines.append("## Local experiments (direct subprocess, off-queue)")
        lines.append("| cell | progress | pid | elapsed | mem | args |")
        lines.append("|---|---|---|---|---|---|")
        for e in lx:
            args = e.get("args") or {}
            atxt = " ".join(f"{k}={v}" for k, v in args.items()) or "-"
            prog = "-"
            if e.get("progress_pct") is not None:
                prog = (f"{e.get('unit_idx')}/{e.get('total_units')} {int(e['progress_pct'])}%"
                        + (f" eta {_fmt_dur(e['eta_s'])}" if e.get("eta_s") else "")
                        + (f" {e['phase']}" if e.get("phase") else ""))
            lines.append(f"| `{e.get('name')}` | {prog} | {e.get('pid')} | "
                         f"{_fmt_dur(e.get('elapsed_s'))} | "
                         f"{int((e.get('mem_kb') or 0) / 1024)}MB | {atxt} |")
        lines.append("")
    lines.append("## Queues")
    lines.append("| queue | running | pending |")
    lines.append("|---|---|---|")
    for qname, q in st["queues"].items():
        lines.append(f"| {qname} | {','.join(q['running']) or '-'} | {len(q['pending'])} |")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# State-change detection + push
# ---------------------------------------------------------------------------

def _load_prev_state() -> dict:
    d = _load_json(STATE_FILE)
    return d if isinstance(d, dict) else {}


def _save_prev_state(codes: list[str], sig: str, running_by_queue: dict) -> None:
    try:
        STATE_FILE.write_text(json.dumps(
            {"alert_codes": codes, "sig": sig, "running_by_queue": running_by_queue}),
            encoding="utf-8")
    except OSError:
        pass


def _detect_crashes(st: dict, prev: dict) -> list[dict]:
    """A job that was RUNNING last tick and is now in a terminal (failed/killed) state
    is a fresh crash -- the OOM case the Director must be pinged about proactively.
    Requires continuity (only meaningful in --watch); seeded silently on first run."""
    out: list[dict] = []
    prev_running = prev.get("running_by_queue") or {}
    if not prev_running:  # first observation -- seed baseline, don't alert on history
        return out
    for qname, q in st["queues"].items():
        was = set(prev_running.get(qname, []))
        term_names = {t["name"]: t["status"] for t in q.get("terminal_recent", [])}
        for nm in was:
            if nm in term_names and nm not in q["running"]:
                out.append({"level": "CRITICAL", "code": "QUEUE_FAILED",
                            "msg": f"{qname}: '{nm}' was running and is now "
                                   f"{term_names[nm]} (crash/OOM?)"})
    return out


def _state_signature(st: dict) -> str:
    """A compact fingerprint of the fields whose CHANGE is worth pushing."""
    q = {k: (tuple(v["running"]), len(v["pending"])) for k, v in st["queues"].items()}
    return json.dumps({"alerts": st["alert_codes"], "queues": q,
                       "gpu_current": st["gpu"]["current"],
                       "dash": st["dashboard_up"]}, sort_keys=True, default=str)


def push_on_change(st: dict) -> list[dict]:
    """Rewrite the pane always; append transitions to alerts.jsonl; return NEW alerts."""
    prev = _load_prev_state()
    prev_codes = set(prev.get("alert_codes", []))

    # Fresh running->terminal crash transitions (needs prev running set).
    crashes = _detect_crashes(st, prev)
    for c in crashes:
        st["alerts"].append(c)
    st["alert_codes"] = sorted({a["code"] for a in st["alerts"]})

    cur_codes = set(st["alert_codes"])
    new_codes = cur_codes - prev_codes
    cleared = prev_codes - cur_codes

    # Always refresh the pane (cheap; keeps the Director surface current).
    try:
        STATUS_PANE.write_text(render_pane(st), encoding="utf-8")
    except OSError:
        pass

    running_by_queue = {q: v["running"] for q, v in st["queues"].items()}
    changed = _state_signature(st) != prev.get("sig")
    # QUEUE_FAILED is a per-event transition (not a level-code) -- always emit each one.
    new_alerts = [a for a in st["alerts"]
                  if a["code"] in new_codes or a["code"] == "QUEUE_FAILED"]
    if new_alerts or cleared:
        try:
            with ALERTS_LOG.open("a", encoding="utf-8") as f:
                for a in new_alerts:
                    f.write(json.dumps({"ts": st["ts"], "event": "RAISED", **a}) + "\n")
                for c in sorted(cleared):
                    f.write(json.dumps({"ts": st["ts"], "event": "CLEARED", "code": c}) + "\n")
        except OSError:
            pass

    if changed or new_alerts or cleared or not prev:
        _save_prev_state(st["alert_codes"], _state_signature(st), running_by_queue)
    return new_alerts


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Proactive in-flight experiment monitor")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--alerts-only", action="store_true", help="print only current alerts")
    ap.add_argument("--watch", action="store_true", help="loop + push on state-change")
    ap.add_argument("--interval", type=float, default=60.0, help="watch poll interval (s)")
    args = ap.parse_args()

    def one() -> dict:
        st = build_state()
        if args.json:
            print(json.dumps(st, indent=2, default=str))
        elif args.alerts_only:
            if st["alerts"]:
                for a in st["alerts"]:
                    print(f"[{a['level']}] {a['code']}: {a['msg']}")
            else:
                print("no alerts")
        else:
            print(render_human(st))
        return st

    if not args.watch:
        st = one()
        # single-shot still refreshes the pane so the surface is never stale-by-omission
        push_on_change(st)
        return 2 if any(a["level"] == "CRITICAL" for a in st["alerts"]) else 0

    print(f"[inflight_monitor] watching every {args.interval:.0f}s; "
          f"pane={STATUS_PANE.name} alerts={ALERTS_LOG.name}", flush=True)
    while True:
        try:
            st = build_state()
            new = push_on_change(st)
            for a in new:
                print(f"[{st['ts']}] NEW {a['level']} {a['code']}: {a['msg']}", flush=True)
        except Exception as e:  # never crash the watch loop
            print(f"[inflight_monitor] ERROR: {type(e).__name__}: {e}", flush=True)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
