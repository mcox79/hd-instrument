"""Probe HF for MuSiQue / 2WikiMultiHop / MetaQA availability. Run on the runner."""
from datasets import load_dataset
CANDS = [
    "dgslibisey/MuSiQue", "Salesforce/musique", "musique",
    "voidful/2WikiMultihopQA", "scholarly-shadows-syndicate/2WikiMultihopQA_with_q_gpt35", "2wikimultihopqa",
    "rmanluo/RoG-metaqa", "metaqa", "yulsu/MetaQA",
]
for name in CANDS:
    try:
        d = load_dataset(name, split="train", streaming=True)
        row = next(iter(d))
        print("OK", name, "keys=", list(row.keys())[:8], flush=True)
    except Exception as e:
        print("FAIL", name, str(e)[:70], flush=True)
