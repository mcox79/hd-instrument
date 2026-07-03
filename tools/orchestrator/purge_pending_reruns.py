"""purge_pending_reruns.py -- remove PENDING entries that are RE-RUNS (a metrics.json already exists for that anchor).
Keeps: running, completed, failed, and pending entries that are genuinely NEW (no prior metrics.json = never run).
Atomic write, UTF-8 no BOM. Run while runners are stopped to avoid concurrent-write races.
Usage: python purge_pending_reruns.py <queue.json> <data_root> [--apply]   (dry-run unless --apply)
"""
import json, os, sys, io

path = sys.argv[1]
# derive data_root from queue path (data/<queue>/queue.json -> data/) to avoid shell backslash-mangling
data_root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
apply = "--apply" in sys.argv
with io.open(path, "r", encoding="utf-8-sig") as f:
    data = json.load(f)
exps = data.get("experiments", [])
keep, dropped = [], []
for e in exps:
    if e.get("status") == "pending":
        # SH-4 fallback: check canonical exp_<name>/ then double-prefix
        # exp_exp_<name>/ (Testbed 2026-07-03 fleet audit; root cause in
        # experiments/_seed_checkpoint.get_output_dir).
        mpath = os.path.join(data_root, "exp_" + e["name"], "metrics.json")
        mpath_dbl = os.path.join(data_root, "exp_exp_" + e["name"], "metrics.json")
        if os.path.exists(mpath) or os.path.exists(mpath_dbl):
            dropped.append(e["name"]); continue
    keep.append(e)
print("queue=%s total=%d pending_reruns_dropped=%d kept=%d" % (os.path.basename(path), len(exps), len(dropped), len(keep)))
for n in dropped:
    print("  DROP pending re-run (metrics exist): %s" % n)
if apply and dropped:
    tmp = path + ".tmp"
    data["experiments"] = keep
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True, indent=2)
    os.replace(tmp, path)
    print("APPLIED: queue rewritten (%d entries)" % len(keep))
elif apply:
    print("APPLIED: nothing to drop")
else:
    print("DRY-RUN (pass --apply to write)")
