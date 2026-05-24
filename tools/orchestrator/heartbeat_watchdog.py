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
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

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

POLL_INTERVAL_S = 60.0
IDLE_THRESHOLD_S = 120.0
# After firing silent_idle, suppress further fires for this long to give the
# orchestrator time to dispatch an emergency refill. If the refill lands, the
# idle condition resets naturally; if it does not, we re-fire after cooldown.
COOLDOWN_S = 600.0

# ---- Condition 2 (audit recommendation #2): ship_unconfirmed ----
# An attempt is unconfirmed when queue_add.sh returned success locally but the
# named experiment never appears in the remote (or local) queue.json within this
# window. The window must be long enough to absorb the dashboard's own poll lag
# (~5s) plus SSH round-trip jitter, but short enough that a real silent failure
# (scp/ssh dropped the file) gets caught while it can still be re-shipped.
SHIP_UNCONFIRMED_THRESHOLD_S = 60.0
SHIP_CONFIRMED_RETENTION_S = 600.0  # drop entries older than this; they're either confirmed long ago or surfaced already
SHIP_UNCONFIRMED_COOLDOWN_S = 300.0  # don't re-fire on the same name within this window

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


def emit(kind: str, payload: dict[str, Any]) -> None:
    print(
        f"EVENT {kind} {json.dumps(payload, separators=(',', ':'), default=str)}",
        flush=True,
    )


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


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


def evaluate_idle() -> dict[str, Any] | None:
    """Return a payload dict iff the silent-idle condition currently holds.

    Condition:
      - dashboard snapshot loadable
      - gpu.queue_pending_count == 0 AND cpu.queue_pending_count == 0
      - gpu.heartbeat.status != 'running' AND cpu.heartbeat.status != 'running'
      - in_flight_count() == 0

    Returns None if any of those is false (or the snapshot is unreadable).
    """
    if not DASHBOARD.exists():
        return None
    d = load_json(DASHBOARD)
    if not isinstance(d, dict):
        return None

    gpu = d.get("gpu") or {}
    cpu = d.get("cpu") or {}
    gpu_pending = gpu.get("queue_pending_count")
    cpu_pending = cpu.get("queue_pending_count")
    gpu_status = ((gpu.get("heartbeat") or {}).get("status") or "").lower()
    cpu_status = ((cpu.get("heartbeat") or {}).get("status") or "").lower()

    # Treat unknown / None pending as "not idle" — we only fire on clear evidence.
    if gpu_pending is None or cpu_pending is None:
        return None
    if gpu_pending != 0 or cpu_pending != 0:
        return None
    if gpu_status == "running" or cpu_status == "running":
        return None
    if in_flight_count() != 0:
        return None

    return {
        "gpu_pending": gpu_pending,
        "cpu_pending": cpu_pending,
        "gpu_status": gpu_status or "unknown",
        "cpu_status": cpu_status or "unknown",
        "in_flight": 0,
    }


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


def _name_in_dashboard_queue(snapshot: dict[str, Any], queue: str, name: str) -> bool:
    """Return True iff `name` appears in any queue.json reflected by the dashboard
    snapshot for the matching `queue` label.

    Queue label mapping:
      overnight_queue  -> snapshot["gpu"]
      remote_cpu_queue -> snapshot["cpu"]
      local_cpu_queue  -> snapshot["local_cpu"] (if present)

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
    if not isinstance(section, dict):
        return False
    for field in ("queue_pending", "queue_running"):
        v = section.get(field) or []
        if isinstance(v, list) and name in v:
            return True
    # Currently-running heartbeat catches the short window where queue.json may
    # be re-written without the entry but the runner is mid-execution.
    cur = section.get("current")
    if cur and cur == name:
        return True
    hb = section.get("heartbeat") or {}
    if isinstance(hb, dict) and hb.get("current") == name:
        return True
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
    if _name_in_dashboard_queue(snapshot, queue, name):
        return True
    if _name_in_recent_verdicts(snapshot, name):
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


def main() -> None:
    emit(
        "ready",
        {
            "component": "heartbeat_watchdog",
            "poll_s": POLL_INTERVAL_S,
            "idle_threshold_s": IDLE_THRESHOLD_S,
            "cooldown_s": COOLDOWN_S,
            "routing_ratio_threshold": ROUTING_RATIO_THRESHOLD,
            "routing_ratio_window": ROUTING_RATIO_WINDOW,
            "ship_unconfirmed_threshold_s": SHIP_UNCONFIRMED_THRESHOLD_S,
            "ship_unconfirmed_cooldown_s": SHIP_UNCONFIRMED_COOLDOWN_S,
        },
    )

    idle_since: float | None = None
    last_fire_ts: float | None = None
    last_routing_recompute_ts: float = 0.0
    last_routing_fire_ts: float | None = None
    # Per-(queue,name) cooldown timestamps for ship_unconfirmed events.
    ship_unconfirmed_last_fire: dict[str, float] = {}

    while True:
        try:
            now = time.time()
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

            time.sleep(POLL_INTERVAL_S)
        except KeyboardInterrupt:
            emit("stopped", {"component": "heartbeat_watchdog"})
            return
        except Exception as e:
            emit("error", {"component": "heartbeat_watchdog", "message": str(e)})
            time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    main()
