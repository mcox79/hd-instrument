"""Mark stale 'running' entries as 'failed' so dashboard stops flagging them."""
import json
from pathlib import Path
import sys
sys.path.insert(0, r"C:\dev\hd-instrument")
from hdlab.session_log import log_event

REPO = Path(r"C:\dev\hd-instrument")
LIVE_RUNNERS = {"wave14d_icl_via_pool_v2", "wave14e2_parisi_ultrametricity"}

for queue_name in ["overnight_queue", "remote_cpu_queue"]:
    p = REPO / "data" / queue_name / "queue.json"
    q = json.loads(p.read_text())
    fixed = 0
    for e in q["experiments"]:
        if e["status"] == "running" and e["name"] not in LIVE_RUNNERS:
            e["status"] = "failed"
            e["error"] = "orphaned (runner died before completion); zombie cleared 2026-05-20"
            fixed += 1
            print(f"  {queue_name}: marked {e['name']} as failed")
            log_event("experiment_outcome", name=e["name"], verdict="failed",
                      summary="Orphaned during runner crash (CPU collapse 01:30 or GPU foreground-tied SSH death). Queue.json zombie cleared.",
                      headline=False)
    p.write_text(json.dumps(q, indent=2))
    print(f"  {queue_name}: cleaned {fixed} zombies")
