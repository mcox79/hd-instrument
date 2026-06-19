"""Download MuSiQue + 2WikiMultiHop dev subsets + inspect formats. Run on the runner."""
import json
from datasets import load_dataset

# 2WikiMultiHop (HotpotQA-like: context + supporting_facts)
ds = load_dataset("voidful/2WikiMultihopQA", split="train", streaming=True)
n = 0
with open("C:/dev/hd-instrument/data/datasets/twowiki_1k.jsonl", "w", encoding="utf-8") as f:
    for r in ds:
        f.write(json.dumps({"question": r.get("question"), "context": r.get("context"),
                            "supporting_facts": r.get("supporting_facts"), "answer": r.get("answer")}) + "\n")
        n += 1
        if n >= 1000:
            break
print("wrote", n, "2wiki", flush=True)
first = json.loads(open("C:/dev/hd-instrument/data/datasets/twowiki_1k.jsonl", encoding="utf-8").readline())
print("2wiki context type:", type(first["context"]).__name__, "| sample:", str(first["context"])[:200], flush=True)
print("2wiki sf:", str(first["supporting_facts"])[:150], flush=True)

# MuSiQue (paragraphs + question_decomposition)
ds2 = load_dataset("dgslibisey/MuSiQue", split="train", streaming=True)
n = 0
with open("C:/dev/hd-instrument/data/datasets/musique_1k.jsonl", "w", encoding="utf-8") as f:
    for r in ds2:
        f.write(json.dumps({"question": r.get("question"), "paragraphs": r.get("paragraphs"),
                            "answer": r.get("answer")}) + "\n")
        n += 1
        if n >= 1000:
            break
print("wrote", n, "musique", flush=True)
firstm = json.loads(open("C:/dev/hd-instrument/data/datasets/musique_1k.jsonl", encoding="utf-8").readline())
ps = firstm["paragraphs"]
print("musique paragraphs type:", type(ps).__name__, "| n:", len(ps) if hasattr(ps, "__len__") else "?", flush=True)
print("musique para[0] keys:", list(ps[0].keys()) if ps and isinstance(ps[0], dict) else type(ps[0]).__name__, flush=True)
