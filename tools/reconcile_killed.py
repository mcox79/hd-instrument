"""Reconcile killed worker tasks: mark named queue entries status='killed' so the runner stops waiting for metrics.json.

Usage: python tools/reconcile_killed.py <anchor_name> [<anchor_name> ...]
Sets status='killed' + ended_at=now for matching running/claimed entries in BOTH queues. Per orchestrator suggestion 2026-06-08.
"""
import json, sys, datetime

QUEUES = [r"C:\dev\hd-instrument\data\overnight_queue\queue.json",
          r"C:\dev\hd-instrument\data\remote_cpu_queue\queue.json"]


def main(names):
    if not names:
        print("usage: reconcile_killed.py <anchor_name> [<anchor_name> ...]"); return
    kill = set(names); total = 0
    for qp in QUEUES:
        try:
            with open(qp, "r", encoding="utf-8") as f:
                j = json.load(f)
        except Exception as e:
            print("skip %s (%s)" % (qp, e)); continue
        ch = 0
        for e in j.get("experiments", []):
            if e.get("name") in kill and e.get("status") in ("running", "claimed"):
                e["status"] = "killed"; e["ended_at"] = datetime.datetime.now().isoformat(timespec="seconds"); ch += 1
        if ch:
            with open(qp, "w", encoding="utf-8") as f:
                json.dump(j, f, indent=2)
            print("%s: marked %d killed" % (qp.split("\\")[-2], ch)); total += ch
    print("done (%d entries reconciled)" % total)


if __name__ == "__main__":
    main(sys.argv[1:])
