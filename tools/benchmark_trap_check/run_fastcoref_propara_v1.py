"""Modern-neural coref extraction over ProPara paragraphs for ARM-2 (extracted structure).

RUNS IN SYSTEM PYTHON (transformers 4.57.3, torch 2.8.0) -- NOT the project .venv (transformers
5.10.1, where fastcoref crashes at the 5.x all_tied_weights_keys model-load refactor). Same
cross-interpreter pattern as data/eval_gold_extraction_quality_gate_v1/run_fastcoref_predict_v1.py
(commit 3f23f2fb2): fastcoref (biu-nlp/f-coref, 90.5M) does its OWN mention detection and dumps
predicted clusters as CHAR SPANS over the reconstructed passage text; the .venv ARM-2 cell aligns
them to participants + sentences by char-span overlap.

Invoke (system python):
  python tools/benchmark_trap_check/run_fastcoref_propara_v1.py
Output:
  data/benchmark_trap_check/propara_fastcoref_predictions_v1.json

Text reconstruction rule (MUST match the .venv cell exactly):
  text = " ".join(sentence_texts); single spaces; sentence i global char offset =
  sum(len(sentence_texts[j]) + 1 for j < i). The output records sentence_offsets so the cell can
  map each coref char-span back to a sentence index by offset containment.
"""
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara")
OUT_PATH = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara_fastcoref_predictions_v1.json")
SPLITS = ["dev", "test"]  # baselines fit on train (text classifiers, no coref needed); reasoning
                          # arm runs on dev (smoke) + test (full)


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8").read().strip().split("\n")]


def sentence_offsets(sentences):
    offs = []
    cur = 0
    for s in sentences:
        offs.append(cur)
        cur += len(s) + 1
    return offs


def main():
    from fastcoref import FCoref
    model = FCoref(device="cpu")

    out = {"_meta": {"model": "biu-nlp/f-coref", "lib": "fastcoref",
                     "env": "system_python_transformers_4.57.3",
                     "text_join": "single_space"}}
    for split in SPLITS:
        paras = load_jsonl(os.path.join(DATA_DIR, f"grids.v1.{split}.json"))
        texts = [" ".join(p["sentence_texts"]) for p in paras]
        preds = model.predict(texts=texts)
        split_out = {}
        for p, pred in zip(paras, preds):
            clusters = pred.get_clusters(as_strings=False)  # list of list of (start,end) char spans
            split_out[str(p["para_id"])] = {
                "text": " ".join(p["sentence_texts"]),
                "sentence_offsets": sentence_offsets(p["sentence_texts"]),
                "n_sentences": len(p["sentence_texts"]),
                "clusters": [[list(span) for span in cl] for cl in clusters],
            }
        out[split] = split_out
        n_cl = sum(len(v["clusters"]) for v in split_out.values())
        print(f"[{split}] {len(split_out)} paragraphs, {n_cl} total fastcoref clusters", flush=True)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"wrote -> {OUT_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
