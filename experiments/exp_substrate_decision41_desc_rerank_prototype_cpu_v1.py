"""
exp_substrate_decision41_desc_rerank_prototype_cpu_v1.py -- DECISION 41 rerank FEASIBILITY prototype (standalone, pre-integration): does reranking the bge top-50 by each candidate's FULL DESCRIPTION (richer signal than the name+aliases index) move MEDIUM in-coverage gold (rank 21/69) into the top-5? -- runs on BGE machine.

ROUTING: DECISION 41. bge-large is a BI-encoder; a bi-encoder rerank on the SAME (name) text reproduces the cosine order (no gain). No
  cross-encoder model is cached (would need ~2GB download). R1 (substrate-on-its-own, use existing bge): rerank instead by re-encoding each top-50
  candidate's DESCRIPTION (the index encodes only name+id+aliases; descriptions carry more signal and CAN reorder). Standalone feasibility check
  BEFORE touching the scorer: for each in-coverage held-out question, compare present-gold rank + top-5 F1 under (a) name-index cosine vs (b)
  description-rerank. DECISIVE: if MEDIUM gold (Q54 rank69, Q55 rank21) moves into top-5 -> integrate into scorer (DECISION 41 proper). If not ->
  escalate to true cross-encoder (bge-reranker download). Substrate-internal (existing bge; no new model, no LLM). ASCII; --self-test + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_decision41_desc_rerank_prototype_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
POOL_K = 100


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def f1_present(pred: set, present: set) -> float:
    if not present:
        return 1.0 if not pred else 0.0
    inter = len(pred & present)
    p = inter / len(pred) if pred else 0.0; r = inter / len(present)
    return 2 * p * r / (p + r) if (p + r) else 0.0


def _norm(M):
    M = np.asarray(M, dtype=np.float32)
    n = np.linalg.norm(M, axis=-1, keepdims=True); n[n == 0] = 1.0
    return M / n


def _selftest():
    assert abs(f1_present({"a"}, {"a"}) - 1.0) < 1e-9 and f1_present({"x"}, set()) == 0.0
    v = _norm([[3.0, 4.0]]); assert abs(np.linalg.norm(v[0]) - 1.0) < 1e-6
    print("[selftest] PASS: substrate_decision41_desc_rerank_prototype_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    if not HELDOUT.exists():
        return {"error": "no_heldout_file"}
    try:
        from backend.substrate_index.partition import PartitionedStore
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
    except Exception as e:
        return {"error": "import_failed:" + str(e)[:100]}
    pstore = PartitionedStore(DATA_ROOT)
    try:
        enc = AtomEncoder()
    except Exception as e:
        return {"error": "bge_unavailable:" + str(e)[:80]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    desc = {a.qualified_id: (a.description or a.name or "") for a in pstore.all_atoms()}
    sset = {_short(a.id) for a in pstore.all_atoms()}

    def bge_encode(texts):
        return _norm(enc.bge.encode(texts))

    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    rows = []
    # strategy accumulators: name (baseline), desc, max-fusion, mean-fusion
    STRATS = ["name", "desc", "maxfuse", "meanfuse"]
    acc = {s: [] for s in STRATS}
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present:
            continue  # in-coverage only
        cands = r.semantic(q["question"], top_k=POOL_K)
        pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool:
            continue
        base_short = [_short(qid) for qid, _ in pool]
        name_score = _norm(np.array([[s] for _, s in pool]).repeat(2, 1))[:, 0]  # already cosines; keep as-is
        name_score = np.array([s for _, s in pool], dtype=np.float32)
        qv = bge_encode([q["question"]])[0]
        dvecs = bge_encode([desc.get(qid, "") for qid, _ in pool])
        desc_score = dvecs @ qv
        scores = {"name": name_score, "desc": desc_score,
                  "maxfuse": np.maximum(name_score, desc_score),
                  "meanfuse": 0.5 * name_score + 0.5 * desc_score}
        row = {"qid": q["qid"], "present_n": len(present)}
        for s in STRATS:
            order = np.argsort(-scores[s])
            top5 = {base_short[i] for i in order[:5]}
            f = f1_present(top5, present); acc[s].append(f); row[s] = round(f, 3)
        rows.append(row)
    macro = {s: round(sum(acc[s]) / len(acc[s]), 4) if acc[s] else 0.0 for s in STRATS}
    print("  in-coverage held-out: %d q | POOL_K=%d" % (len(rows), POOL_K), flush=True)
    print("  qid        " + "  ".join("%-8s" % s for s in STRATS), flush=True)
    for x in rows:
        print("  %-9s  " % x["qid"] + "  ".join("%-8.3f" % x[s] for s in STRATS), flush=True)
    print("  IN-COVERAGE top5 macro-F1: " + " | ".join("%s=%.4f" % (s, macro[s]) for s in STRATS), flush=True)
    return {"n": len(rows), "base_macro": macro["name"], "rerank_macro": max(macro["maxfuse"], macro["meanfuse"]),
            "macro_by_strategy": macro, "rows": rows, "pool_k": POOL_K, "best_strategy": max(macro, key=macro.get)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    m = r["macro_by_strategy"]; best = r["best_strategy"]; base = m["name"]
    delta = m[best] - base
    # per-question regression check of the best fusion vs name baseline
    regressed = [x["qid"] for x in r["rows"] if x[best] < x["name"] - 1e-9]
    txt = ("DECISION 41 rerank prototype (in-coverage held-out, POOL_K=%d). Macro-F1 by strategy: %s. Best=%s (%.4f vs name-baseline %.4f, delta %+.4f). "
           "Best-strategy per-question regressions vs name: %s." % (
               r["pool_k"], ", ".join("%s=%.4f" % (k, v) for k, v in m.items()), best, m[best], base, delta, regressed or "none"))
    if best != "name" and delta >= 0.05 and not regressed:
        return ("HARD_PASS", "HARD_PASS (fusion rerank recovers MEDIUM cleanly, no per-question regression): " + txt + " INTEGRATE '%s' fusion into scorer." % best)
    if best != "name" and delta >= 0.03:
        return ("PARTIAL", "PARTIAL (fusion helps overall but has per-question regressions or modest lift): " + txt + " Consider integrating '%s' with care, or escalate to true cross-encoder." % best)
    return ("HARD_FAIL", "HARD_FAIL (no rerank strategy beats name-baseline cleanly): " + txt + " Description/fusion signals do not reliably recover MEDIUM; escalate to true cross-encoder (bge-reranker ~2GB) or accept MEDIUM needs M4.")


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
