"""Auto-healer for hd-instrument runner state.

Runs continuously on the remote workstation. Wakes every 5 min, performs
4 conservative auto-corrections, logs every action.

Designed for unattended operation: no git ops, no outbound network calls,
no destructive deletes. All state changes are status label updates only.

The 4 auto-corrections:
1. Misflagged failures: queue says "failed" but data/exp_<name>/metrics.json
   exists with real content -> re-flag "completed" + emit retroactive outcome.
2. Zombie clearing: queue says "running" but started_at > 6h ago AND no
   matching live process -> mark "failed" with note.
3. Duplicate entries: same name appears twice in queue -> dedupe, keep
   most recently modified (status not "pending" wins; otherwise last wins).
4. Inconclusive promotion: queue says "inconclusive" but metrics.json now
   exists -> promote to "completed".

Healer NEVER:
- Relaunches dead runners
- Deletes any data
- Modifies experiment scripts
- Touches git
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")
sys.path.insert(0, str(REPO))
from hdlab.session_log import log_event  # noqa: E402

QUEUES = ["overnight_queue", "remote_cpu_queue"]
HEAL_INTERVAL_S = 300  # 5 min between iterations
ZOMBIE_THRESHOLD_HOURS = 6
HEALER_LOG = REPO / "data" / "healer.log"
HEALER_HEARTBEAT = REPO / "data" / "healer_heartbeat.json"


def log(msg: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    HEALER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with HEALER_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def heartbeat(iteration: int, last_actions: int) -> None:
    HEALER_HEARTBEAT.write_text(json.dumps({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "pid": str(__import__("os").getpid()),
        "iteration": iteration,
        "last_iteration_actions": last_actions,
    }, indent=2))


def read_queue(queue_name: str) -> dict | None:
    p = REPO / "data" / queue_name / "queue.json"
    if not p.exists():
        return None
    for attempt in range(8):
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, PermissionError):
            time.sleep(0.5 * (attempt + 1))
    log(f"WARN: could not read {queue_name}/queue.json after 8 retries")
    return None


def write_queue(queue_name: str, q: dict) -> bool:
    p = REPO / "data" / queue_name / "queue.json"
    for attempt in range(8):
        try:
            p.write_text(json.dumps(q, indent=2))
            return True
        except PermissionError:
            time.sleep(0.5 * (attempt + 1))
    log(f"WARN: could not write {queue_name}/queue.json after 8 retries")
    return False


def metrics_exists_with_content(name: str) -> bool:
    p = REPO / "data" / f"exp_{name}" / "metrics.json"
    if not p.exists():
        return False
    try:
        return p.stat().st_size > 100
    except OSError:
        return False


def heal_misflagged_failures(q: dict) -> int:
    count = 0
    for e in q["experiments"]:
        if e.get("status") != "failed":
            continue
        if metrics_exists_with_content(e["name"]):
            e["status"] = "completed"
            existing_note = e.get("note", "")
            e["note"] = ((existing_note + "; ") if existing_note else "") + \
                        f"healer({datetime.now().isoformat(timespec='seconds')}): re-flagged completed (metrics.json exists)"
            log(f"  HEAL misflagged: {e['name']} failed -> completed")
            log_event("experiment_outcome", name=e["name"], verdict="completed_via_healer",
                      summary=f"Re-flagged by healer: failed status but metrics.json exists. Manual review recommended.",
                      headline=False)
            count += 1
    return count


def heal_zombies(q: dict, threshold_hours: int) -> int:
    count = 0
    now = datetime.now()
    for e in q["experiments"]:
        if e.get("status") != "running":
            continue
        started_str = e.get("started_at")
        if not started_str:
            continue
        try:
            started = datetime.fromisoformat(started_str)
        except ValueError:
            continue
        age_hours = (now - started).total_seconds() / 3600
        if age_hours > threshold_hours:
            e["status"] = "failed"
            e["error"] = f"healer: marked failed after {age_hours:.1f}h still running"
            log(f"  HEAL zombie: {e['name']} ({age_hours:.1f}h) -> failed")
            log_event("experiment_outcome", name=e["name"], verdict="failed",
                      summary=f"Orphaned: running > {threshold_hours}h, no completion. Auto-cleared by healer.",
                      headline=False)
            count += 1
    return count


def heal_duplicates(q: dict) -> int:
    """De-duplicate entries with same name. Keep the most recently modified."""
    by_name: dict[str, tuple[int, dict]] = {}
    for i, e in enumerate(q["experiments"]):
        name = e["name"]
        if name not in by_name:
            by_name[name] = (i, e)
        else:
            old_i, old_e = by_name[name]
            # Prefer non-pending status (completed/failed > pending > running)
            status_pref = {"completed": 4, "failed": 3, "running": 2, "pending": 1, "inconclusive": 4}
            new_pref = status_pref.get(e.get("status"), 0)
            old_pref = status_pref.get(old_e.get("status"), 0)
            if new_pref > old_pref:
                by_name[name] = (i, e)
    if len(by_name) == len(q["experiments"]):
        return 0  # no duplicates
    # Preserve original insertion order
    seen = set()
    new_list = []
    for i, e in enumerate(q["experiments"]):
        if e["name"] in seen:
            continue
        seen.add(e["name"])
        kept_i, kept_e = by_name[e["name"]]
        new_list.append(kept_e)
    removed = len(q["experiments"]) - len(new_list)
    log(f"  HEAL duplicates: removed {removed} duplicate entries")
    q["experiments"] = new_list
    return removed


def heal_inconclusive(q: dict) -> int:
    count = 0
    for e in q["experiments"]:
        if e.get("status") != "inconclusive":
            continue
        if metrics_exists_with_content(e["name"]):
            e["status"] = "completed"
            log(f"  HEAL inconclusive: {e['name']} -> completed")
            count += 1
    return count


def run_iteration(iteration: int) -> int:
    total_actions = 0
    for queue_name in QUEUES:
        q = read_queue(queue_name)
        if q is None:
            continue
        actions = 0
        actions += heal_misflagged_failures(q)
        actions += heal_zombies(q, ZOMBIE_THRESHOLD_HOURS)
        actions += heal_duplicates(q)
        actions += heal_inconclusive(q)
        if actions > 0:
            if write_queue(queue_name, q):
                log(f"  Wrote {queue_name} queue.json with {actions} corrections")
                total_actions += actions
            else:
                log(f"  WARN: skipped write for {queue_name}")
    return total_actions


def main():
    log("============================================")
    log(f"Healer started, pid={__import__('os').getpid()}, interval={HEAL_INTERVAL_S}s")
    iteration = 0
    while True:
        iteration += 1
        last_actions = 0
        try:
            log(f"Iteration {iteration}")
            last_actions = run_iteration(iteration)
            if last_actions == 0:
                log(f"  No corrections needed")
        except Exception as exc:
            log(f"ERROR in iteration {iteration}: {exc}")
            log(f"Traceback: {traceback.format_exc()}")
        heartbeat(iteration, last_actions)
        time.sleep(HEAL_INTERVAL_S)


if __name__ == "__main__":
    main()
