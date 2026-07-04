"""autorefill_watcher.py -- dispatch-on-idle auto-refill for overnight_queue (GPU,
gpu_runner_0) and remote_cpu_queue (CPU, cpu_runner_0).

PROBLEM THIS FIXES: dispatch has been one-cell-at-a-time with no backlog, so any
smoke/design latency between cells leaves a remote runner idle (USER-flagged 7+
times; standing directive is "multiple experiments in flight at all times"). This
watcher runs on a short cadence (recommended every 5 min), checks whether a remote
runner is idle AND its queue has nothing pending/running, and if so pops the next
entry off a Director/agent-curated ready-pool and ships it via the SAME
tools/orchestrator/queue_add.sh path exp_dev already uses (routing-sanity gate,
sibling auto-SCP, post-ship remote verify -- all inherited for free). It COMPLEMENTS
agent-driven dispatch; it never competes for the same decision (it only acts when a
runner has been sitting idle with an empty queue).

DEFAULT STATE: DISABLED. This is a new, consequential (auto-dispatches real remote
GPU/CPU jobs) mechanism; it must be explicitly opted into.

ENABLE:
    (git-bash / Bash tool)
        touch d:/AI/hd-instrument/data/autorefill_enabled.flag
    (PowerShell)
        New-Item -ItemType File -Force d:\\AI\\hd-instrument\\data\\autorefill_enabled.flag

DISABLE (trivial, no task-scheduler surgery needed -- the watcher no-ops if the
flag is absent):
    rm d:/AI/hd-instrument/data/autorefill_enabled.flag

PAUSE-GATED: also refuses to dispatch while data/orchestrator_paused.flag exists
(same flag exp_dev/orchestrator honor). Presence of either flag => no-op, logged
once per cycle, zero side effects.

CADENCE / REGISTRATION: this script does ONE check-and-maybe-dispatch pass per
invocation (no internal loop) -- Windows Task Scheduler owns the interval, exactly
like tools/substrate_snapshot_cron.bat + tools/register_substrate_snapshot_task_
elevated.ps1. See tools/autorefill_cron.bat (launcher) and
tools/register_autorefill_task_elevated.ps1 (one-time registration, needs an
elevated PowerShell -- S4U logon registration requires admin, same precedent as
the substrate-snapshot task).

READY-POOL (data/autorefill_pool.json) -- Director/agent-curated manifest of
validated, ready-to-dispatch cells. Append an entry any time a cell has cleared
smoke and is just waiting for a runner slot:
    {
      "schema_version": 1,
      "pool": [
        {
          "id": "encoder_r12_seed_4",              # unique; used for dedup + removal
          "queue": "overnight_queue",               # overnight_queue | remote_cpu_queue
          "name": "encoder_r12_seed_4",              # queue entry name (HDLAB_EXP_NAME)
          "script": "experiments/exp_encoder_r12_seed_4.py",
          "prereg": "preregs/2026-07-04_encoder_r12.md",
          "timeout_s": 3600,
          "seeds": 1,
          "added_by": "hdi_exp_dev",
          "added_ts": "2026-07-04T20:00:00Z",
          "note": "why this is ready (smoke passed, cleared discriminator, etc.)"
        }
      ]
    }
The watcher pops the FIRST entry (FIFO) whose "queue" matches the idle runner's
queue and whose "name" is not already pending/running there, dispatches it, and
removes it from the pool (successful dispatch OR stale-duplicate alike).

FALLBACK (data/autorefill_fallback_cell.json) -- used ONLY when the pool has
nothing for that queue. Deliberately Director/agent-curated (not
auto-derived-by-heuristic from verdict logs): picking "the most recent HARD_PASS
validated encoder cell" is a judgment call and this fleet has a known failure mode
of scripts mis-identifying/hallucinating the wrong artifact -- so a human/agent
states it explicitly instead of the watcher guessing. Schema (per queue key):
    {
      "overnight_queue": {
        "active": true,
        "cell_id": "encoder_v3e_dense_recovery",
        "prereg": "preregs/2026-07-04_encoder_v3e.md",
        "timeout_s": 5400,
        "candidate_seeds": [
          {"name": "encoder_v3e_seed_9",  "script": "experiments/exp_encoder_v3e_seed_9.py",  "dispatched": false},
          {"name": "encoder_v3e_seed_10", "script": "experiments/exp_encoder_v3e_seed_10.py", "dispatched": false}
        ],
        "verdict_ref": "HARD_PASS <landing note or verdict_msg pointer>",
        "updated_by": "hdi_research",
        "updated_ts": "2026-07-04T20:00:00Z"
      },
      "remote_cpu_queue": { ... same shape ... }
    }
Candidate seed WRAPPER FILES must already exist on disk (this watcher never
generates new seed scripts -- that is exp_dev's job). It dispatches candidates in
list order, marks each "dispatched": true once shipped, and caps at
FALLBACK_CAP (2) CONSECUTIVE fallback dispatches per runner before going quiet and
writing a loud one-time alert log line (no silent infinite seed-spam). The cap
resets the moment a pool entry is available again for that runner.

STATE (data/autorefill_state.json): per-runner consecutive_fallback counter +
alerted flag, maintained by this script. Safe to delete to reset the cap.

Dispatch audit trail: data/autorefill_dispatch_log.jsonl (append-only, one line
per attempted dispatch, pool or fallback, success or fail).

Reuses tools/runner_status.py's canonical SSH/heartbeat/queue readers -- no
duplicate SSH logic. Reuses tools/orchestrator/queue_add.sh for the actual ship
(routing-sanity gate + sibling auto-SCP Patterns 1-6 + post-ship verify all
inherited).

CLI:
    python tools/autorefill_watcher.py                  # real pass (SSH + maybe dispatch)
    python tools/autorefill_watcher.py --dry-run         # real state read, print instead of dispatch
    python tools/autorefill_watcher.py --test-state F.json --dry-run
                                                          # fully offline smoke (no SSH, no dispatch)
See tools/_autorefill_watcher_smoke.py for the smoke harness.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from runner_status import (  # noqa: E402  -- reuse canonical remote-state readers
    discover_remote_heartbeats,
    read_remote_queue,
    queue_stats,
    classify_runner,
    REMOTE_QUEUE_DIRS,
)

ENABLED_FLAG = REPO / "data" / "autorefill_enabled.flag"
PAUSED_FLAG = REPO / "data" / "orchestrator_paused.flag"
POOL_PATH = REPO / "data" / "autorefill_pool.json"
FALLBACK_PATH = REPO / "data" / "autorefill_fallback_cell.json"
STATE_PATH = REPO / "data" / "autorefill_state.json"
LOG_PATH = REPO / "data" / "logs" / "autorefill_watcher.log"
DISPATCH_LOG_PATH = REPO / "data" / "autorefill_dispatch_log.jsonl"
QUEUE_ADD_SH = REPO / "tools" / "orchestrator" / "queue_add.sh"

FALLBACK_CAP = 2  # consecutive fallback dispatches (per runner) before going quiet + alerting
DISPATCH_TIMEOUT_S = 300  # wall clock cap on the queue_add.sh subprocess itself (SCP+SSH+verify)

# queue_name -> runner_id (mirrors runner_status.py's remote-runner/queue affinity)
QUEUE_RUNNER = {
    "overnight_queue": "gpu_runner_0",
    "remote_cpu_queue": "cpu_runner_0",
}

# Known-good bash.exe locations, checked before falling back to PATH lookup.
BASH_CANDIDATES = [
    r"C:\Program Files\Git\bin\bash.exe",
    r"C:\Program Files\Git\usr\bin\bash.exe",
]

NO_WINDOW = 0x08000000  # CREATE_NO_WINDOW; Windows-only, matches repo-wide popup-free convention


# --- small IO helpers ---------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return default


def _write_json_atomic(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _log(line: str) -> None:
    stamped = f"[{_now_iso()}] {line}"
    print(stamped, flush=True)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(stamped + "\n")
    except OSError:
        pass


def _append_dispatch_log(row: dict) -> None:
    try:
        DISPATCH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with DISPATCH_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


# --- world assembly (real SSH path, or offline fixture for smoke tests) -------

def build_world(test_state_path: str | None) -> dict:
    """Returns {queue_name: {runner_verdict, idle, status, pending, running,
    queue_entries}} for overnight_queue + remote_cpu_queue.

    If test_state_path is given, that JSON file IS the world dict verbatim (no
    SSH at all) -- this is how smoke tests exercise the decision logic without
    touching any real runner or queue.
    """
    if test_state_path:
        return _load_json(Path(test_state_path), {})

    remote_dirs = dict(REMOTE_QUEUE_DIRS)
    heartbeats = discover_remote_heartbeats()
    world: dict = {}
    for queue_name, runner_id in QUEUE_RUNNER.items():
        entries = read_remote_queue(remote_dirs[queue_name])
        stats = queue_stats(entries)
        hb = heartbeats.get(runner_id)
        if hb is None:
            world[queue_name] = {
                "runner_verdict": "MISSING", "idle": False, "status": None,
                "pending": stats["pending"], "running": stats["running"],
                "queue_entries": entries,
            }
            continue
        verdict = classify_runner(hb)
        status = hb.get("status")
        idle = (
            verdict in ("ALIVE", "STALE")
            and status == "idle"
            and stats["pending"] == 0
            and stats["running"] == 0
        )
        world[queue_name] = {
            "runner_verdict": verdict, "idle": idle, "status": status,
            "pending": stats["pending"], "running": stats["running"],
            "queue_entries": entries,
        }
    return world


# --- pure decision logic (unit-testable, no IO) -------------------------------

def decide(world: dict, pool: dict, fallback: dict, state: dict):
    """Pure function: given current world/pool/fallback/state, decide what (if
    anything) to dispatch per queue.

    Returns (actions, new_state, log_lines, pool_ids_to_remove).
      actions: list of dicts, each either
        {"kind": "pool", "queue":.., "runner_id":.., "entry": <pool entry dict>}
        {"kind": "fallback", "queue":.., "runner_id":.., "cell_id":.., "candidate": <seed dict>,
         "prereg":.., "timeout_s":..}
      new_state: deep-copied + updated `state` (consecutive_fallback / alerted per runner_id)
      log_lines: list[str], already tagged for _log()
      pool_ids_to_remove: set of pool entry "id" values to strip from the pool file
        (both the one we dispatched AND any stale duplicates we skipped over)
    """
    actions: list[dict] = []
    new_state = copy.deepcopy(state)
    logs: list[str] = []
    pool_ids_to_remove: set[str] = set()

    entries_by_queue: dict[str, list[dict]] = {}
    for e in pool.get("pool", []):
        entries_by_queue.setdefault(e.get("queue"), []).append(e)

    for queue_name, runner_id in QUEUE_RUNNER.items():
        q = world.get(queue_name, {})
        rs = new_state.setdefault(runner_id, {"consecutive_fallback": 0, "alerted": False})

        verdict = q.get("runner_verdict")
        if verdict == "ZOMBIE":
            logs.append(
                f"[AUTOREFILL][ZOMBIE-SKIP] {runner_id}: heartbeat classifies ZOMBIE; "
                f"NOT autofilling a dead runner (needs manual revival; see runner_status.py --remote)"
            )
            continue
        if verdict == "MISSING" or verdict is None:
            logs.append(f"[AUTOREFILL][NO-HEARTBEAT] {runner_id}: no reachable heartbeat this cycle; skipping")
            continue
        if not q.get("idle"):
            logs.append(
                f"[AUTOREFILL][NOT-IDLE] {runner_id}: status={q.get('status')} "
                f"pending={q.get('pending')} running={q.get('running')}; nothing to do"
            )
            continue

        logs.append(f"[AUTOREFILL][IDLE-DETECTED] {runner_id}/{queue_name}: idle + queue empty -- checking ready-pool")

        existing_names = {
            e.get("name") for e in q.get("queue_entries", [])
            if e.get("status") in ("pending", "running")
        }

        picked = None
        for e in entries_by_queue.get(queue_name, []):
            if e.get("name") in existing_names:
                logs.append(
                    f"[AUTOREFILL][SKIP-DUP] pool entry '{e.get('name')}' (id={e.get('id')}) already "
                    f"pending/running in {queue_name}; dropping stale pool entry, not re-dispatching"
                )
                pool_ids_to_remove.add(e.get("id"))
                continue
            picked = e
            break

        if picked is not None:
            actions.append({"kind": "pool", "queue": queue_name, "runner_id": runner_id, "entry": picked})
            pool_ids_to_remove.add(picked.get("id"))
            rs["consecutive_fallback"] = 0
            rs["alerted"] = False
            logs.append(
                f"[AUTOREFILL][POOL-FILL] {runner_id}/{queue_name}: dispatching ready-pool entry "
                f"'{picked.get('name')}' (id={picked.get('id')})"
            )
            continue

        logs.append(f"[AUTOREFILL][POOL-EMPTY] {runner_id}/{queue_name}: no matching ready-pool entry")

        fb = (fallback or {}).get(queue_name)
        if not fb or not fb.get("active", False):
            logs.append(
                f"[AUTOREFILL][FALLBACK-NOT-CONFIGURED] {runner_id}/{queue_name}: no active fallback "
                f"manifest for this queue in data/autorefill_fallback_cell.json; staying idle"
            )
            continue

        if rs.get("consecutive_fallback", 0) >= FALLBACK_CAP:
            if not rs.get("alerted"):
                logs.append(
                    f"[AUTOREFILL][FALLBACK-CAP-ALERT] {runner_id}/{queue_name}: reached {FALLBACK_CAP} "
                    f"consecutive fallback dispatches; going QUIET (no more auto-seeding) until the "
                    f"ready-pool gets a real entry for this queue, or data/autorefill_state.json is reset."
                )
                rs["alerted"] = True
            else:
                logs.append(
                    f"[AUTOREFILL][FALLBACK-CAP-QUIET] {runner_id}/{queue_name}: cap reached, already alerted"
                )
            continue

        candidates = fb.get("candidate_seeds", [])
        cand = next((c for c in candidates if not c.get("dispatched")), None)
        if cand is None:
            if not rs.get("alerted"):
                logs.append(
                    f"[AUTOREFILL][FALLBACK-EXHAUSTED-ALERT] {runner_id}/{queue_name}: fallback cell "
                    f"'{fb.get('cell_id')}' has no undispatched candidate_seeds left; staying idle. "
                    f"Add more candidates to data/autorefill_fallback_cell.json."
                )
                rs["alerted"] = True
            else:
                logs.append(
                    f"[AUTOREFILL][FALLBACK-EXHAUSTED-QUIET] {runner_id}/{queue_name}: still no undispatched "
                    f"candidates, already alerted"
                )
            continue
        if cand.get("name") in existing_names:
            # Harmless no-op: it's already in flight (someone shipped it another way).
            # Re-fires every cycle until it leaves pending/running, but never
            # double-dispatches and never counts against the fallback cap.
            logs.append(
                f"[AUTOREFILL][SKIP-DUP] fallback candidate '{cand.get('name')}' already "
                f"pending/running in {queue_name}; not touching"
            )
            continue

        actions.append({
            "kind": "fallback", "queue": queue_name, "runner_id": runner_id,
            "cell_id": fb.get("cell_id"), "candidate": cand,
            "prereg": fb.get("prereg"), "timeout_s": fb.get("timeout_s"),
        })
        rs["consecutive_fallback"] = rs.get("consecutive_fallback", 0) + 1
        rs["alerted"] = False
        logs.append(
            f"[AUTOREFILL][FALLBACK-FILL] {runner_id}/{queue_name}: dispatching FALLBACK seed "
            f"'{cand.get('name')}' from cell '{fb.get('cell_id')}' "
            f"(consecutive={rs['consecutive_fallback']}/{FALLBACK_CAP}) -- pool was empty"
        )

    return actions, new_state, logs, pool_ids_to_remove


# --- dispatch (IO; shells out to the SAME queue_add.sh exp_dev uses) ----------

def _bash_path() -> str:
    for c in BASH_CANDIDATES:
        if Path(c).exists():
            return c
    which = shutil.which("bash")
    if which:
        return which
    raise RuntimeError("no bash.exe found (checked known Git-bash paths + PATH); cannot invoke queue_add.sh")


def dispatch_action(action: dict, dry_run: bool) -> bool:
    if action["kind"] == "pool":
        e = action["entry"]
        name, script, prereg, timeout_s = e["name"], e["script"], e["prereg"], e["timeout_s"]
    else:
        cand = action["candidate"]
        name, script = cand["name"], cand["script"]
        prereg, timeout_s = action["prereg"], action["timeout_s"]

    qa_posix = str(QUEUE_ADD_SH).replace("\\", "/")
    cmd = [_bash_path(), qa_posix, action["queue"], name, script, prereg, str(timeout_s)]

    if dry_run:
        _log(f"[AUTOREFILL][DRY-RUN] would run: {' '.join(cmd)}")
        return True

    log_path = REPO / "data" / "logs" / f"autorefill_dispatch_{name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("w", encoding="utf-8") as lf:
            result = subprocess.run(
                cmd, cwd=str(REPO), stdout=lf, stderr=subprocess.STDOUT,
                timeout=DISPATCH_TIMEOUT_S, creationflags=NO_WINDOW,
            )
        ok = result.returncode == 0
    except (subprocess.TimeoutExpired, OSError) as exc:
        _log(f"[AUTOREFILL][DISPATCH-FAIL] {name} -> {action['queue']}: {exc!r}")
        return False

    tag = "DISPATCH-OK" if ok else "DISPATCH-FAIL"
    _log(f"[AUTOREFILL][{tag}] {name} -> {action['queue']} (queue_add.sh log: {log_path})")
    return ok


# --- persistence of pool/fallback mutations -----------------------------------

def _strip_pool_ids(pool_path: Path, ids_to_remove: set) -> None:
    if not ids_to_remove:
        return
    doc = _load_json(pool_path, {"schema_version": 1, "pool": []})
    before = len(doc.get("pool", []))
    doc["pool"] = [e for e in doc.get("pool", []) if e.get("id") not in ids_to_remove]
    if len(doc["pool"]) != before:
        _write_json_atomic(pool_path, doc)


def _mark_fallback_dispatched(fallback_path: Path, queue_name: str, cand_name: str) -> None:
    doc = _load_json(fallback_path, {})
    fb = doc.get(queue_name)
    if not fb:
        return
    changed = False
    for c in fb.get("candidate_seeds", []):
        if c.get("name") == cand_name and not c.get("dispatched"):
            c["dispatched"] = True
            c["dispatched_ts"] = _now_iso()
            changed = True
    if changed:
        _write_json_atomic(fallback_path, doc)


# --- main ----------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="compute + print actions, never actually dispatch")
    ap.add_argument("--test-state", default=None, help="path to a fixture JSON = the world dict verbatim; bypasses SSH")
    ap.add_argument("--pool", default=str(POOL_PATH))
    ap.add_argument("--fallback", default=str(FALLBACK_PATH))
    ap.add_argument("--state", default=str(STATE_PATH))
    ap.add_argument("--enabled-flag", default=str(ENABLED_FLAG))
    ap.add_argument("--paused-flag", default=str(PAUSED_FLAG))
    args = ap.parse_args()

    enabled_flag = Path(args.enabled_flag)
    paused_flag = Path(args.paused_flag)

    if not enabled_flag.exists():
        _log(f"[AUTOREFILL][DISABLED] {enabled_flag} absent; no-op. Enable by creating that file.")
        return 0
    if paused_flag.exists():
        _log(f"[AUTOREFILL][PAUSED] {paused_flag} present; skipping this cycle (pause-gated, same as exp_dev).")
        return 0

    world = build_world(args.test_state)
    pool = _load_json(Path(args.pool), {"schema_version": 1, "pool": []})
    fallback = _load_json(Path(args.fallback), {})
    state = _load_json(Path(args.state), {})

    actions, new_state, logs, pool_ids_to_remove = decide(world, pool, fallback, state)
    for line in logs:
        _log(line)

    dispatched_pool_ids: set = set()
    dispatched_fallback: list[tuple[str, str]] = []  # (queue_name, cand_name)

    for action in actions:
        ok = dispatch_action(action, dry_run=args.dry_run)
        _append_dispatch_log({
            "ts": _now_iso(), "kind": action["kind"], "queue": action["queue"],
            "runner_id": action["runner_id"],
            "name": (action["entry"]["name"] if action["kind"] == "pool" else action["candidate"]["name"]),
            "ok": ok, "dry_run": args.dry_run,
        })
        if ok and not args.dry_run:
            if action["kind"] == "pool":
                dispatched_pool_ids.add(action["entry"].get("id"))
            else:
                dispatched_fallback.append((action["queue"], action["candidate"]["name"]))

    if not args.dry_run:
        all_remove_ids = pool_ids_to_remove | dispatched_pool_ids
        _strip_pool_ids(Path(args.pool), all_remove_ids)
        for queue_name, cand_name in dispatched_fallback:
            _mark_fallback_dispatched(Path(args.fallback), queue_name, cand_name)
        if not args.test_state:
            _write_json_atomic(Path(args.state), new_state)

    return 0


if __name__ == "__main__":
    sys.exit(main())
