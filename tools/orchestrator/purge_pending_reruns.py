"""purge_pending_reruns.py -- remove PENDING entries whose anchor already has a COMPLETED entry (re-run padding).
Keeps: running, completed, failed, and pending entries that are genuinely NEW (no prior completed). Atomic write, UTF-8 no BOM.
Usage: python purge_pending_reruns.py <queue.json> [--apply]   (dry-run unless --apply)
"""
import json, os, sys, io

path = sys.argv[1]
apply = "--apply" in sys.argv
with io.open(path, "r", encoding="utf-8-sig") as f:
    data = json.load(f)
exps = data.get("experiments", [])
completed_names = {e["name"] for e in exps if e.get("status") == "completed"}
keep, dropped = [], []
for e in exps:
    if e.get("status") == "pending" and e["name"] in completed_names:
        dropped.append(e["name"])
    else:
        keep.append(e)
print("queue=%s total=%d pending_reruns_dropped=%d kept=%d" % (os.path.basename(path), len(exps), len(dropped), len(keep)))
for n in dropped:
    print("  DROP pending re-run: %s" % n)
if apply and dropped:
    data["experiments"] = keep
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:   # utf-8 no BOM
        json.dump(data, f, ensure_ascii=True, indent=2)
    os.replace(tmp, path)
    print("APPLIED: queue rewritten (%d entries)" % len(keep))
elif apply:
    print("APPLIED: nothing to drop")
else:
    print("DRY-RUN (pass --apply to write)")
