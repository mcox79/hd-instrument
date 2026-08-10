"""Modern-neural coref extraction for the extraction-quality gate re-run (coordinator directive,
2026-08-10): run fastcoref (biu-nlp/f-coref, a modern 2022-23 neural coref model) and dump its
predicted clusters as CHAR SPANS over a reconstructed passage text, so the .venv gate cell can
align them to the gold mention stream (real neural coref does its OWN mention detection; alignment
to gold mentions is by char-span overlap, done cell-side).

RUNS IN SYSTEM PYTHON (transformers 4.57.3, torch 2.8.0) -- NOT the project .venv (transformers
5.10.1, where fastcoref crashes at model-load on the 5.x all_tied_weights_keys refactor).
transformers 4.57.3 does NOT have that code path (verified), so fastcoref loads. System python is
a separate interpreter, isolated from the project .venv per the coordinator's isolate directive.
Model already fully cached (~/.cache/huggingface/hub/models--biu-nlp--f-coref, 694M) so no
download hang.

Invoke:  python data/eval_gold_extraction_quality_gate_v1/run_fastcoref_predict_v1.py
Output:  data/eval_gold_extraction_quality_gate_v1/fastcoref_predictions_v1.json

Text reconstruction rule (MUST match the .venv gate cell exactly):
  text = " ".join(clauses)          for McGuffey passages (key "clauses")
  text = " ".join(sentences)        for gold_coref_modern passages (key "sentences")
Single spaces; global char offset of unit i = sum(len(units[j]) for j<i) + i.
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_extraction_quality_gate_v1")
COREF_GOLD_PATH = os.path.join(GOLD_DIR, "gold_coref_modern_v1.jsonl")
MCGUFFEY_POWERED_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_combined_pronoun_powered_v1.jsonl"
)
OUT_PATH = os.path.join(GOLD_DIR, "fastcoref_predictions_v1.json")


def load_jsonl(path):
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def reconstruct(units):
    """Return (text, [unit_global_start_offset, ...]) for a list of clause/sentence strings joined
    by single spaces."""
    text = " ".join(units)
    offsets = []
    cur = 0
    for u in units:
        offsets.append(cur)
        cur += len(u) + 1  # +1 for the joining space
    return text, offsets


def main():
    from fastcoref import FCoref
    model = FCoref(device="cpu")

    predictions = {"coref_gold": {}, "mcguffey_powered": {},
                   "_meta": {"model": "biu-nlp/f-coref", "lib": "fastcoref",
                             "env": "system_python_transformers_4.57.3"}}

    # ---- gold_coref_modern (sentences) ----
    coref_passages = load_jsonl(COREF_GOLD_PATH)
    coref_texts = [" ".join(p["sentences"]) for p in coref_passages]
    coref_preds = model.predict(texts=coref_texts)
    for p, pred in zip(coref_passages, coref_preds):
        clusters = pred.get_clusters(as_strings=False)  # list of list of (start,end) char spans
        predictions["coref_gold"][p["passage_id"]] = {
            "text": " ".join(p["sentences"]),
            "clusters": [[list(span) for span in cl] for cl in clusters],
        }

    # ---- McGuffey powered eval (clauses) ----
    mc_passages = sorted(load_jsonl(MCGUFFEY_POWERED_PATH), key=lambda p: p["passage_id"])
    mc_texts = [" ".join(p["clauses"]) for p in mc_passages]
    mc_preds = model.predict(texts=mc_texts)
    for p, pred in zip(mc_passages, mc_preds):
        clusters = pred.get_clusters(as_strings=False)
        predictions["mcguffey_powered"][p["passage_id"]] = {
            "text": " ".join(p["clauses"]),
            "clusters": [[list(span) for span in cl] for cl in clusters],
        }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)
    n_coref = len(predictions["coref_gold"])
    n_mc = len(predictions["mcguffey_powered"])
    n_mc_clusters = sum(len(v["clusters"]) for v in predictions["mcguffey_powered"].values())
    print(f"wrote {n_coref} coref_gold + {n_mc} mcguffey_powered passages "
          f"({n_mc_clusters} total fastcoref clusters on McGuffey) -> {OUT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
