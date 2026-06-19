"""
exp_substrate_decision41_cross_encoder_rerank_cpu_v1.py -- DECISION 41 TRUE cross-encoder rerank: rerank the bge top-100 pool with a bge-reranker (joint query-candidate cross-attention, NOT bi-encoder cosine) and check whether MEDIUM in-coverage gold (rank 21/69) recovers into top-5 + whether COVERAGE-GAP precision improves. -- runs on BGE machine.

ROUTING: DECISION 41 escalation. Bi-encoder rerank (name/desc/fusion) HARD_FAILED to recover MEDIUM (representation bottleneck). A cross-encoder
  scores (query, candidate-description) JOINTLY via cross-attention -- a fundamentally different, stronger signal. R1 (substrate-on-its-own): a
  bge-reranker is a LOCAL model (sentence_transformers CrossEncoder), NOT an LLM API -- 11th-rule compliant. Downloads BAAI/bge-reranker-base (~1.1GB)
  on first run. Measures, on held-out: IN-COVERAGE top-5 macro-F1 (name-baseline vs cross-encoder rerank) + per-question recovery/regression, and
  COVERAGE-GAP top-1 cross-encoder score distribution (does the reranker SCORE gap candidates low -> a refuse signal?). HARD-PASS: in-coverage lifts
  toward 0.3 with no per-question regression. ASCII; --self-test + metrics.json.
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
ANCHOR_NAME = "substrate_decision41_cross_encoder_rerank_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
POOL_K = 100
RERANKER = "BAAI/bge-reranker-base"


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def f1_present(pred: set, present: set) -> float:
    if not present:
        return 1.0 if not pred else 0.0
    inter = len(pred & present)
    p = inter / len(pred) if pred else 0.0; r = inter / len(present)
    return 2 * p * r / (p + r) if (p + r) else 0.0


def _selftest():
    assert abs(f1_present({"a", "b"}, {"a"}) - (2 * 0.5 * 1 / 1.5)) < 1e-9
    assert _short("MATH::T2/Cosine_Cleanup") == "cosine_cleanup"
    print("[selftest] PASS: substrate_decision41_cross_encoder_rerank_cpu_v1", flush=True)


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
        from sentence_transformers import CrossEncoder
    except Exception as e:
        return {"error": "import_failed:" + str(e)[:120]}
    pstore = PartitionedStore(DATA_ROOT)
    try:
        enc = AtomEncoder()
    except Exception as e:
        return {"error": "bge_unavailable:" + str(e)[:80]}
    try:
        ce = CrossEncoder(RERANKER)
    except Exception as e:
        return {"error": "reranker_load_failed:" + str(e)[:100]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    desc = {a.qualified_id: (a.description or a.name or "") for a in pstore.all_atoms()}
    sset = {_short(a.id) for a in pstore.all_atoms()}
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    rows = []
    name_f1s, ce_f1s = [], []
    gap_ce_top1 = []  # cross-encoder top1 score on coverage-gap questions (refuse signal probe)
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        cands = r.semantic(q["question"], top_k=POOL_K)
        pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool:
            continue
        base_short = [_short(qid) for qid, _ in pool]
        pairs = [[q["question"], desc.get(qid, "")] for qid, _ in pool]
        ce_scores = np.asarray(ce.predict(pairs, show_progress_bar=False), dtype=np.float32)
        order = np.argsort(-ce_scores)
        ce_top5 = {base_short[i] for i in order[:5]}
        ce_top1_score = float(ce_scores[order[0]]) if len(order) else 0.0
        if not present:  # coverage-gap
            gap_ce_top1.append((q["qid"], round(ce_top1_score, 3)))
            continue
        name_top5 = set(base_short[:5])
        nf = f1_present(name_top5, present); cf = f1_present(ce_top5, present)
        name_f1s.append(nf); ce_f1s.append(cf)
        ce_gold_rank = min([list(order).index(base_short.index(g)) + 1 for g in present if g in base_short] or [9999]) if present else 9999
        rows.append({"qid": q["qid"], "present_n": len(present), "name_top5_f1": round(nf, 3), "ce_top5_f1": round(cf, 3), "ce_top1_score": round(ce_top1_score, 3)})
    name_macro = round(sum(name_f1s) / len(name_f1s), 4) if name_f1s else 0.0
    ce_macro = round(sum(ce_f1s) / len(ce_f1s), 4) if ce_f1s else 0.0
    print("  reranker=%s | in-coverage q=%d | POOL_K=%d" % (RERANKER, len(rows), POOL_K), flush=True)
    print("  qid        present  name_top5_F1  ce_top5_F1  ce_top1_score", flush=True)
    for x in rows:
        print("  %-9s  %d        %.3f         %.3f       %.3f" % (x["qid"], x["present_n"], x["name_top5_f1"], x["ce_top5_f1"], x["ce_top1_score"]), flush=True)
    print("  IN-COVERAGE top5 macro-F1: name-baseline=%.4f -> cross-encoder=%.4f" % (name_macro, ce_macro), flush=True)
    print("  COVERAGE-GAP cross-encoder top1 scores (refuse-signal probe): %s" % gap_ce_top1, flush=True)
    in_gold = [x["ce_top1_score"] for x in rows]
    print("  IN-COVERAGE cross-encoder top1 scores: %s" % [round(s, 3) for s in in_gold], flush=True)
    return {"reranker": RERANKER, "n_in": len(rows), "name_macro": name_macro, "ce_macro": ce_macro, "rows": rows,
            "gap_ce_top1": gap_ce_top1, "in_ce_top1": [round(s, 3) for s in in_gold], "pool_k": POOL_K}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    delta = r["ce_macro"] - r["name_macro"]
    regressed = [x["qid"] for x in r["rows"] if x["ce_top5_f1"] < x["name_top5_f1"] - 1e-9]
    recovered = [x["qid"] for x in r["rows"] if x["name_top5_f1"] == 0.0 and x["ce_top5_f1"] > 0.0]
    # refuse-signal: is there separation between in-coverage and gap cross-encoder top1?
    gapscores = [s for _, s in r["gap_ce_top1"]]
    in_med = float(np.median(r["in_ce_top1"])) if r["in_ce_top1"] else 0.0
    gap_med = float(np.median(gapscores)) if gapscores else 0.0
    base = ("DECISION 41 cross-encoder (%s). IN-COVERAGE top5 macro-F1 name=%.4f -> CE=%.4f (delta %+.4f). Recovered:%s Regressed:%s. "
            "Refuse-signal: CE top1 median in-coverage=%.3f vs gap=%.3f." % (
                r["reranker"], r["name_macro"], r["ce_macro"], delta, recovered or "none", regressed or "none", in_med, gap_med))
    if delta >= 0.05 and not regressed:
        return ("HARD_PASS", "HARD_PASS (cross-encoder recovers in-coverage cleanly): " + base + " INTEGRATE cross-encoder rerank into scorer; validate tuned regression next.")
    if delta >= 0.03:
        return ("PARTIAL", "PARTIAL (cross-encoder helps but with regressions or modest lift): " + base + " Integrate with care; check tuned regression.")
    if in_med > gap_med + 0.5:
        return ("PARTIAL", "PARTIAL (no in-coverage recovery BUT a usable refuse-signal emerged): CE separates in-coverage from gap by top1 score -- "
                "may fix Cause-2 refuse-robustness even though it does not recover MEDIUM. " + base)
    return ("HARD_FAIL", "HARD_FAIL (cross-encoder does not recover MEDIUM and gives no clean refuse-signal): " + base + " MEDIUM is genuinely M4/representation-bound; accept it behind the ingest+M4 track.")


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
