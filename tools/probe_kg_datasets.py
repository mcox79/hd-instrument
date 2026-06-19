"""Probe HF for NELL / WebQSP / ComplexWebQuestions availability. Run on the runner."""
from datasets import load_dataset

CANDS = [
    "nell", "VLyb/NELL-995", "KGraph/NELL995",
    "web_questions", "Stanford/web_questions",
    "rmanluo/RoG-webqsp", "rmanluo/RoG-cwq", "drt/complex_web_questions",
]
for name in CANDS:
    try:
        d = load_dataset(name, split="train", streaming=True)
        row = next(iter(d))
        print("OK", name, "keys=", list(row.keys())[:6], flush=True)
    except Exception as e:
        print("FAIL", name, str(e)[:70], flush=True)
