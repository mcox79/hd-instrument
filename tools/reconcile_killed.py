import json, sys, datetime
KILL = {"wikipedia_ingest_1m_gpu_v1", "e3_cyclic_khop_1m_cpu_v1"}
for qp in [r"C:\dev\hd-instrument\data\overnight_queue\queue.json", r"C:\dev\hd-instrument\data\remote_cpu_queue\queue.json"]:
    with open(qp, "r", encoding="utf-8") as f:
        j = json.load(f)
    ch = 0
    for e in j.get("experiments", []):
        if e.get("name") in KILL and e.get("status") in ("running", "claimed"):
            e["status"] = "killed"; e["ended_at"] = datetime.datetime.now().isoformat(timespec="seconds"); ch += 1
    if ch:
        with open(qp, "w", encoding="utf-8") as f:
            json.dump(j, f, indent=2)
        print("%s marked %d killed" % (qp.split("\\")[-2], ch))
print("done")
