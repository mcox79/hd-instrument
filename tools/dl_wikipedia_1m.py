"""Download a 1m-article Wikipedia subset via HF datasets streaming. Run on the runner."""
import json
from datasets import load_dataset

OUT = "C:/dev/hd-instrument/data/datasets/wikipedia_1m.jsonl"
ds = load_dataset("wikimedia/wikipedia", "20231101.en", split="train", streaming=True)
n = 0
with open(OUT, "w", encoding="utf-8") as f:
    for r in ds:
        f.write(json.dumps({"title": r["title"], "text": r["text"][:2000]}) + "\n")
        n += 1
        if n >= 1000000:
            break
print("wrote", n, "wiki articles to", OUT, flush=True)
