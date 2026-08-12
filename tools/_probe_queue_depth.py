"""One-shot remote queue depth probe; run via ssh marsh@home + powershell."""
import json
import sys
from pathlib import Path

queue = sys.argv[1] if len(sys.argv) > 1 else "remote_cpu_queue"
p = Path("data") / queue / "queue.json"
if not p.exists():
    print("MISSING:", p)
    raise SystemExit(0)
q = json.load(open(p, encoding="utf-8"))
exps = q.get("experiments", [])
pend = [e for e in exps if e.get("status") in ("pending", "running")]
print("queue:", queue, "total:", len(exps), "pending_or_running:", len(pend))
for e in pend[:20]:
    print(" ", e.get("status"), "|", str(e.get("name", "?"))[:60], "queued:",
          str(e.get("queued_at", "?"))[:19], "started:",
          str(e.get("started_at", "?"))[:19] if e.get("started_at") else "-")
