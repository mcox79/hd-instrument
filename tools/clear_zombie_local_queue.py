"""One-shot: clear zombie runner claim on local_cpu_queue, restore seed_7 to pending.

Author: orchestrator agent 2026-06-29 ~02:25Z
Context: PID 5776 wedged at substrate_lock_in_amp_phase_diagram_v2_seed_7 since 2026-06-28T18:17:45.
Heartbeat last self-updated 19:18:18Z (no content updates in ~3h); mtime touched but JSON stale.
Process cannot be killed without admin (S4U/admin lineage from Task Scheduler).

Action: atomic rewrite queue.json setting that one 'running' entry -> 'pending'
        (clears claimed_by + started_at fields so a fresh runner can re-claim).
"""
import json
import os
import shutil
import tempfile
from pathlib import Path

QUEUE = Path("d:/AI/hd-instrument/data/local_cpu_queue/queue.json")
HEARTBEAT = Path("d:/AI/hd-instrument/data/local_cpu_queue/heartbeat.cpu_runner_local.json")
HEARTBEAT2 = Path("d:/AI/hd-instrument/data/local_cpu_queue/heartbeat.json")
SINGLETON_PID = Path("d:/AI/hd-instrument/data/logs/cpu_runner_local.pid")

TARGET_NAME = "substrate_lock_in_amp_phase_diagram_v2_seed_7"


def main():
    # Backup queue.json first
    backup = QUEUE.with_suffix(".json.bak_zombie_clear_2026-06-29")
    shutil.copy2(QUEUE, backup)
    print(f"[backup] {QUEUE} -> {backup}")

    with QUEUE.open("r", encoding="utf-8") as f:
        q = json.load(f)

    exps = q["experiments"]
    print(f"[load] {len(exps)} experiments in queue.json")

    # Find target
    matched = 0
    for e in exps:
        if e.get("name") == TARGET_NAME and e.get("status") == "running":
            print(f"[found] {TARGET_NAME}: status={e.get('status')} claimed_by={e.get('claimed_by')} started={e.get('started_at')}")
            # Reset to pending; preserve script/prereg/timeout etc; clear claim fields
            e["status"] = "pending"
            for k in ("claimed_by", "started_at"):
                if k in e:
                    e.pop(k, None)
            # Annotate why
            e["zombie_cleared_at"] = "2026-06-29T02:25:00Z"
            e["zombie_cleared_note"] = "PID 5776 wedged 4h+ no heartbeat content updates; admin-blocked kill; re-issued to pending for fresh runner pickup (orchestrator agent)"
            matched += 1

    if matched != 1:
        print(f"[ERROR] expected exactly 1 running entry to flip, got {matched}")
        return 1

    # Status breakdown after
    from collections import Counter
    sc = Counter(e.get("status", "<none>") for e in exps)
    print(f"[post] status counts: {dict(sc)}")

    # Atomic write
    fd, tmp = tempfile.mkstemp(prefix="queue.json.", dir=str(QUEUE.parent))
    os.close(fd)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(q, f, indent=2)
        # On Windows os.replace is atomic
        os.replace(tmp, QUEUE)
        print(f"[write] atomic-replaced {QUEUE}")
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

    # Clear stale heartbeat files (so runner_status doesn't think old runner is alive)
    for hb in (HEARTBEAT, HEARTBEAT2):
        if hb.exists():
            hb.unlink()
            print(f"[clear] {hb}")

    # Clear singleton PID file (PID 5776 is wedged; new runner needs to start)
    if SINGLETON_PID.exists():
        SINGLETON_PID.unlink()
        print(f"[clear] {SINGLETON_PID}")

    print("[done]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
