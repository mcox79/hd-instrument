"""Score held-out benchmark Q54-Q65 against substrate (CPU-only).

Reuses the canonical qa_self_knowledge scoring + axis routes from
experiments/exp_qa_self_knowledge_cpu_v1.py via in-process import. Operates on
my held-out benchmark file `gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl` (commit
99ea2b08) instead of the canonical Q01-Q53.

Output:
  - stdout summary (per-Q F1 + per-axis F1 + macro F1)
  - data/substrate_index/bench_reports/held_out_benchmark_score.json
  - optionally appends a held-out=True entry to scorecard.json
    (via --update-scorecard flag)

DEGRADED MODE: this scorer does NOT load bge encoder (local laptop has no
torch per ALL-CPU-on-remote rule). Routes E/G that depend on semantic similarity
will use META/METHODOLOGY keyword match only (per canonical script's CPU fallback).
Routes A/B/C/D/F are full-fidelity.

Per pre-reg HARD-PASS criteria from held-out ship note:
  HARD-PASS:    macro F1 >= 0.50
  MIDDLE-BAND:  0.30 < macro F1 < 0.50
  HARD-FAIL:    macro F1 < 0.30

Usage:
  python tools/substrate_score_held_out_benchmark_v1.py
      [--bench-path experiments/data/gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl]
      [--update-scorecard]
"""
from __future__ import annotations
import sys
import os
import json
import time
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index import self_knowledge as sk

# Reuse the canonical bench's route + scoring functions
from exp_qa_self_knowledge_cpu_v1 import (
    _norm, _f1, route_A, route_B, route_C, route_D, route_E, route_F, route_G,
    _load_relations, _extract_args,
)


HELD_OUT_BENCH = Path("experiments/data/gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl")
SUBSTRATE_DIR = Path("data/substrate_index")
OUT_PATH = Path("data/substrate_index/bench_reports/held_out_benchmark_score.json")
SCORECARD_PATH = Path("data/substrate_index/bench_reports/scorecard.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--bench-path", default=str(HELD_OUT_BENCH))
    ap.add_argument("--substrate-dir", default=str(SUBSTRATE_DIR))
    ap.add_argument("--update-scorecard", action="store_true",
                    help="Append a held-out=True entry to scorecard.json (incremental cycle phase)")
    ap.add_argument("--cycle-phase-label", default="cycle_51_held_out_local",
                    help="Cycle phase label for scorecard entry")
    args = ap.parse_args()

    bench_fp = Path(args.bench_path)
    if not bench_fp.exists():
        print(f"ERROR: held-out bench not found at {bench_fp}")
        sys.exit(2)

    print(f"=== Held-Out Benchmark Scorer v1 ===")
    print(f"bench: {bench_fp}")
    print(f"substrate: {args.substrate_dir}")

    raw = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    bench = []
    for r in raw:
        qid = r.get("qid") or r.get("id")
        qtype = r.get("type", "A")
        tnorm = qtype.split("_")[0].upper()
        if tnorm in ("NEGATIVE", "N", "NEG"):
            tnorm = "A"  # route negatives as content (should refuse via empty retrieval)
        q = r.get("question", "")
        gold = list(r.get("ground_truth_atoms") or r.get("gold") or [])
        ans = r.get("answerable", bool(gold))
        if tnorm == "D" and ans and not gold:
            gold = ["PATH_EXISTS"]
        q_args = r.get("args") or _extract_args(q, tnorm)
        bench.append({"id": qid, "type": tnorm, "question": q, "args": q_args,
                      "answerable": ans, "gold": gold})

    pstore = PartitionedStore(Path(args.substrate_dir))
    atoms = pstore.all_atoms()
    relations = _load_relations(Path(args.substrate_dir))
    all_ids = set(_norm(a.id) for a in atoms)
    id2corpus = {_norm(a.id): str(getattr(a.corpus, "value", a.corpus)).lower() for a in atoms}
    id2qid = {_norm(a.id): "%s::%s" % (str(getattr(a.corpus, "value", a.corpus)).lower(), a.id) for a in atoms}

    print(f"\n[snapshot] atoms={len(atoms)} relations={len(relations)} benchmark_qs={len(bench)}")
    per_q = []
    by_type = {}
    for q in bench:
        t = q["type"]
        ans = q.get("answerable", True)
        gold = set(_norm(g) for g in q.get("gold", []))
        gold_present = set(g for g in gold if (g in all_ids or g == "path_exists"))
        attrition = len(gold) - len(gold_present)
        try:
            if t == "A":
                retrieved = route_A(atoms, q["args"])
            elif t == "B":
                retrieved = route_B(relations, q["args"], id2corpus)
            elif t == "C":
                retrieved = route_C(pstore, sk, q["args"])
            elif t == "D":
                retrieved = route_D(pstore, sk, q["args"], id2qid)
            elif t == "E":
                retrieved = route_E(atoms, q["args"])
            elif t == "F":
                retrieved = route_F(pstore, atoms, q["args"])
            elif t == "G":
                retrieved = route_G(atoms, relations, q["args"])
            else:
                retrieved = set()
        except Exception as e:
            print(f"  {q['id']} route_{t} failed: {str(e)[:100]}; retrieved empty")
            retrieved = set()
        f1, tp, fp, fn = _f1(retrieved, gold_present, ans)
        per_q.append({
            "id": q["id"], "type": t, "f1": round(f1, 4),
            "tp": tp, "fp": fp, "fn": fn,
            "gold_present": len(gold_present), "gold_attrition": attrition,
            "answerable": ans,
            "retrieved_sample": list(retrieved)[:5],
        })
        by_type.setdefault(t, []).append(f1)
        print(f"  {q['id']:8s} [{t}] F1={f1:.3f} (tp={tp} fp={fp} fn={fn} gold_present={len(gold_present)} attrition={attrition})")

    macro = sum(p["f1"] for p in per_q) / max(len(per_q), 1)
    type_f1 = {t: round(sum(v) / len(v), 4) for t, v in by_type.items()}
    worst = sorted(per_q, key=lambda p: p["f1"])[:3]

    print(f"\n=== HELD-OUT MACRO F1 = {macro:.4f} (n={len(per_q)} Qs) ===")
    print(f"per-type F1: {type_f1}")
    print(f"worst-3: {[(p['id'], p['f1']) for p in worst]}")
    print(f"total gold attrition: {sum(p['gold_attrition'] for p in per_q)}")

    if macro >= 0.50:
        verdict = "HARD_PASS"
        verdict_msg = f"substrate generalizes to held-out; macro F1 {macro:.4f} >= 0.50"
    elif macro >= 0.30:
        verdict = "MIDDLE_BAND"
        verdict_msg = f"substrate partially generalizes; macro F1 {macro:.4f} in [0.30, 0.50)"
    else:
        verdict = "HARD_FAIL"
        verdict_msg = f"substrate Goodhart'd; held-out macro F1 {macro:.4f} < 0.30"
    print(f"\nVERDICT: {verdict} -- {verdict_msg}")

    # Honesty check on Q_neg_2
    neg_q = next((p for p in per_q if p["id"] == "Q_neg_2"), None)
    if neg_q:
        honesty = "PASS" if neg_q["f1"] == 1.0 else "FAIL"
        print(f"HONESTY (Q_neg_2 refuse): {honesty} (F1={neg_q['f1']}; expected 1.0 for correct refusal)")

    out = {
        "bench_path": str(bench_fp),
        "substrate_dir": str(args.substrate_dir),
        "atoms": len(atoms),
        "relations": len(relations),
        "n_qs": len(per_q),
        "macro_f1": round(macro, 4),
        "per_type_f1": type_f1,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "per_q": per_q,
        "scorer_mode": "cpu_only_no_bge_degraded",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nfull JSON: {OUT_PATH}")

    if args.update_scorecard and SCORECARD_PATH.exists():
        scorecard = json.loads(SCORECARD_PATH.read_text(encoding="utf-8"))
        new_entry = {
            "cycle_id": scorecard.get("current_cycle_id", 51),
            "cycle_phase": args.cycle_phase_label,
            "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "macro_f1": round(macro, 4),
            "per_axis_f1": type_f1,
            "mechanism_classes_shipped": ["held-out benchmark Q54-Q65 score (CPU degraded; no bge)"],
            "commit_hash": "held_out_local_score",
            "held_out_companion_macro_f1": round(macro, 4),
            "held_out": True,
            "notes": (
                f"Held-out CPU-only score on degraded {args.substrate_dir} (local laptop 1746 atoms; "
                f"canonical remote 20820 expected to be higher). Per USER Goodhart directive."
            ),
        }
        scorecard.setdefault("history", []).append(new_entry)
        with SCORECARD_PATH.open("w", encoding="utf-8") as f:
            json.dump(scorecard, f, indent=2)
        print(f"appended held-out entry to scorecard: {SCORECARD_PATH}")


if __name__ == "__main__":
    main()
