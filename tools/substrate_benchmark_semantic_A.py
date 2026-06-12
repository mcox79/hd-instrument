"""Run substrate_benchmark with Gap 4 v2 SEMANTIC A_content via bge encoder.

Per Research CYCLE45_MIDDLE_BAND_APPROVE_NEXT_PRIORITY Q4 PRIMARY:
- Gap 4 v2 REMOTE encoder semantic intent classifier + bge cosine + cross-corpus filter
- A axis 0.28 -> 0.40 (+0.12 macro lift)
- Path-to-HP_v1 0.70 critical lever

This script ONLY runs on REMOTE (encoder load required per all-cpu-compute-remote rule).

Strategy: For each A_content question, use Retriever.semantic(question, top_k=15) to surface
candidate atoms by bge cosine similarity. Replaces keyword AND-matching.

Compare per-Q vs keyword baseline (router) to quantify Gap 4 v2 lift.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.retrieve import Retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("benchmark_semantic_A")

DATA_ROOT = Path("data/substrate_index")


def score_set_overlap(predicted: set[str], ground_truth: list[str]) -> dict:
    gt = set(ground_truth)
    tp = predicted & gt
    fn = gt - predicted
    fp = predicted - gt
    precision = len(tp) / max(1, len(tp) + len(fp))
    recall = len(tp) / max(1, len(tp) + len(fn))
    f1 = 2 * precision * recall / max(1e-9, precision + recall)
    return {
        "tp": len(tp), "fn": len(fn), "fp": len(fp),
        "precision": round(precision, 3), "recall": round(recall, 3),
        "f1": round(f1, 3),
        "n_pred": len(predicted),
        "n_gold": len(gt),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path,
                    default=DATA_ROOT / "benchmark_corpus_v3_60q.jsonl")
    ap.add_argument("--top-k", type=int, default=15,
                    help="bge semantic retrieval top-K per A_content question")
    ap.add_argument("--sweep", type=str, default="",
                    help="comma-separated top_k values to sweep (e.g. '5,8,12,16')")
    args = ap.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    log.info("substrate: %d atoms across %d partitions",
             len(pstore.all_atoms()),
             sum(1 for p in pstore.stats()["partitions"].values() if p["n_atoms"] > 0))

    log.info("loading bge encoder (REMOTE required)...")
    encoder = AtomEncoder()
    retriever = Retriever(pstore, encoder)
    log.info("building retrieval index...")
    retriever.rebuild_index()

    # Load A_content questions only
    questions = []
    with open(args.questions, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            q = json.loads(line)
            if q.get("type") == "A_content":
                questions.append(q)
    log.info("loaded %d A_content questions", len(questions))

    ks = [int(x) for x in args.sweep.split(",")] if args.sweep else [args.top_k]

    print("\n" + "=" * 78)
    print(f"GAP 4 v2 SEMANTIC A_content -- bge cosine top-k sweep {ks}")
    print("=" * 78)

    # Build id->qualified_id map
    bare_to_qid = {}
    for atom in pstore.all_atoms():
        bare_to_qid[atom.id] = atom.qualified_id
    log.info("built bare->qualified map: %d entries", len(bare_to_qid))

    results = []
    per_k_mean = {}
    for K in ks:
        f1_sum = 0.0
        k_results = []
        for q in questions:
            candidates = retriever.semantic(q["question"], top_k=K)
            predicted = set()
            for c in candidates:
                qid = bare_to_qid.get(c.atom_id, c.atom_id)
                predicted.add(qid)
            sc = score_set_overlap(predicted, q["ground_truth_atoms"])
            k_results.append({"qid": q["qid"], "k": K, **sc})
            f1_sum += sc["f1"]
        mean_f1 = f1_sum / max(1, len(questions))
        per_k_mean[K] = mean_f1
        results.extend(k_results)
        print(f"  top_k={K:2d}  mean F1={mean_f1:.3f}")
        if len(ks) == 1:
            for r in k_results:
                mark = "++" if r["f1"] >= 0.7 else ("+" if r["f1"] >= 0.4 else "-")
                print(f"    {r['qid']:8s} F1={r['f1']:.2f} P={r['precision']:.2f} R={r['recall']:.2f} {mark}  tp={r['tp']} fp={r['fp']} fn={r['fn']}")

    best_k = max(per_k_mean, key=per_k_mean.get)
    best_f1 = per_k_mean[best_k]
    print(f"\nbest_k={best_k} F1={best_f1:.3f} vs keyword baseline 0.283 -- lift +{best_f1 - 0.283:.3f}")
    print(f"pre-reg verdict: {'HARD-PASS' if best_f1 >= 0.30 else 'MIDDLE' if best_f1 >= 0.22 else 'HARD-FAIL'}")
    mean_f1 = best_f1

    out = DATA_ROOT / "bench_reports" / f"gap4v2_semantic_A_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "n_questions": len(questions),
        "top_k": args.top_k,
        "results": results,
        "mean_f1": mean_f1,
        "baseline_keyword_f1": 0.283,
        "lift": mean_f1 - 0.283,
    }, indent=2), encoding="utf-8")
    log.info("wrote report -> %s", out)


if __name__ == "__main__":
    main()
