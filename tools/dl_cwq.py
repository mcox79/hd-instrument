"""Download RoG-CWQ (real KG-QA with per-question subgraphs). Run on the runner."""
import json
from datasets import load_dataset

OUT = "C:/dev/hd-instrument/data/datasets/cwq_rog.jsonl"
ds = load_dataset("rmanluo/RoG-cwq", split="train", streaming=True)
n = 0
with open(OUT, "w", encoding="utf-8") as f:
    for r in ds:
        rec = {"question": r.get("question"), "answer": r.get("answer"), "q_entity": r.get("q_entity"),
               "a_entity": r.get("a_entity"), "graph": r.get("graph")}
        f.write(json.dumps(rec) + "\n"); n += 1
        if n >= 2000:
            break
print("wrote", n, "cwq questions to", OUT, flush=True)
# inspect one graph
import json as _j
first = _j.loads(open(OUT, encoding="utf-8").readline())
g = first.get("graph")
print("graph type:", type(g).__name__, "| len:", len(g) if hasattr(g, "__len__") else "?", flush=True)
print("graph[0]:", g[0] if g else None, flush=True)
print("q_entity:", first.get("q_entity"), "| a_entity:", first.get("a_entity"), flush=True)
