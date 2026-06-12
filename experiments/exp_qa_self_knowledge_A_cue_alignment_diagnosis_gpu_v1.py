"""
exp_qa_self_knowledge_A_cue_alignment_diagnosis_gpu_v1.py -- is the A-axis residual a bge CUE-ALIGNMENT problem? (GPU/bge) -- GPU.

ROUTING: the two-vector trilogy concluded every retrieval path is ultimately QUERY-SNR-bound (cue-to-target alignment), and
  that the FREE-TEXT A-axis (which routes through the bge semantic index, NOT the atom-keyed composite) should be limited by
  bge cue quality. The trilogy ROUTED this to Testbed but never MEASURED it. This cell measures it directly: for each A-axis
  answerable question with gold, encode the query topic with bge, and compute the cosine to the GOLD atom's bge semantic vector
  + the gold atom's RANK in the semantic ordering + whether gold is inside the production top-k (k=3). If A-gold cosines are
  high and recall@k is high, the A-axis residual is NOT cue-alignment (it is elsewhere -- e.g. keyword-UNION precision); if
  cosines are low / gold falls outside top-k, cue-alignment IS the bottleneck and the lever is bge query encoding (expansion /
  reformulation), confirming the trilogy's free-text-path prediction. Either way the diagnosis is decisive. NO LLM (bge is an
  embedding model, not a generative LLM); substrate-physics of the A-route. Runs on the remote desktop (bge on CUDA).

PRE-REGISTERED (descriptive diagnosis, decisive either way):
  - "CUE-BOUND" if median best-gold bge cosine < 0.40 OR recall@3 < 0.60 -> A-axis is query-encoding-limited; fix is bge cue
    quality, not the route/index. (HARD_PASS: clean actionable diagnosis -> query encoding is the lever.)
  - "CUE-ALIGNED" if median best-gold cosine >= 0.50 AND recall@3 >= 0.75 -> gold IS reachable by bge; the A-axis residual is a
    RANKING/UNION-precision problem downstream of the cue, not cue alignment. (HARD_PASS: also a clean diagnosis -> different lever.)
  - MIDDLE_BAND if mixed (one threshold each side). UNKNOWN if bge/benchmark unavailable.
ASCII-only. write_metrics. PROT-020 (import torch). GPU. Route via overnight_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json, re
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "qa_self_knowledge_A_cue_alignment_diagnosis_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
STOP = {"the", "a", "an", "of", "to", "and", "in", "is", "it", "for", "on", "what", "which", "how", "does", "do", "are"}
_IDPAT = re.compile(r"[A-Za-z0-9_]+(?:[-/][A-Za-z0-9_]+)+")


def _norm(qid):
    return str(qid).split("::")[-1].strip()


def _extract_topic(q, args):
    if isinstance(args, dict) and args.get("topic"):
        return args["topic"]
    return q  # fall back to the raw question text as the cue


def _selftest():
    assert _norm("concept::T1/x") == "T1/x"
    v = np.array([3.0, 4.0]); assert abs(float(np.linalg.norm(v)) - 5.0) < 1e-6
    print("[selftest] PASS: qa_self_knowledge_A_cue_alignment_diagnosis_gpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch  # PROT-020
    _ = torch.cuda.is_available()
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)


def _snapshot_index():
    d = REPO / "data" / "substrate_index"
    return d if d.exists() else None


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    bench_fp = REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl"
    if not bench_fp.exists():
        return {"error": "benchmark_missing", "note": str(bench_fp)}
    raw = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    # A-axis answerable questions with gold
    aqs = []
    for r in raw:
        qtype = r.get("type", "A"); tnorm = qtype.split("_")[0].upper()
        if tnorm not in ("A",):
            continue
        gold = list(r.get("ground_truth_atoms") or r.get("gold") or [])
        if not gold:
            continue
        aqs.append({"id": r.get("qid") or r.get("id"), "q": r.get("question", ""),
                    "args": r.get("args") or {}, "gold": [_norm(g) for g in gold]})
    if SMOKE: aqs = aqs[:5]
    if not aqs:
        return {"error": "no_A_gold_questions"}
    idx_dir = _snapshot_index()
    if idx_dir is None:
        return {"error": "no_substrate_index"}
    pstore = PartitionedStore(idx_dir)
    try:
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        enc = AtomEncoder(); retr = Retriever(getattr(pstore, "store", pstore), enc); retr.rebuild_index()
    except Exception as e:
        return {"error": "bge_unavailable", "note": str(e)[:160]}
    vecs = retr._vectors; id_order = retr._id_order
    # normalized id -> stored id (semantic vectors keyed by stored id)
    norm2id = {_norm(i): i for i in id_order}
    sem = retr._semantic_matrix  # [N, D], L2-normalized rows
    N = sem.shape[0]
    K = int(os.environ.get("HDLAB_A_K", "3"))
    rows = []
    for q in aqs:
        topic = _extract_topic(q["q"], q["args"])
        qv = enc.bge.encode([topic])[0].astype(np.float32)
        qv = qv / (np.linalg.norm(qv) + 1e-9)
        gold_present = [g for g in q["gold"] if g in norm2id]
        if not gold_present:
            rows.append({"id": q["id"], "gold_in_index": False, "best_cos": None, "best_rank": None, "in_topk": None})
            continue
        sims = sem @ qv                                  # cosine to every atom (rows L2-normed, qv normed)
        order = np.argsort(-sims)
        rank_of = {id_order[order[r]]: r for r in range(N)}
        best_cos = max(float(sims[id_order.index(norm2id[g])]) for g in gold_present)
        best_rank = min(rank_of[norm2id[g]] for g in gold_present)
        rows.append({"id": q["id"], "gold_in_index": True, "best_cos": round(best_cos, 4),
                     "best_rank": int(best_rank), "in_topk": bool(best_rank < K)})
    scored = [r for r in rows if r.get("best_cos") is not None]
    if not scored:
        return {"error": "no_gold_in_index", "n_A": len(aqs)}
    cosv = np.array([r["best_cos"] for r in scored]); rankv = np.array([r["best_rank"] for r in scored])
    med_cos = float(np.median(cosv)); mean_cos = float(cosv.mean())
    recall_k = float(np.mean([r["in_topk"] for r in scored])); recall10 = float(np.mean(rankv < 10))
    med_rank = float(np.median(rankv))
    print("  A-axis answerable-with-gold: %d (gold-in-index: %d)" % (len(aqs), len(scored)), flush=True)
    print("  best-gold bge cosine: median=%.4f mean=%.4f" % (med_cos, mean_cos), flush=True)
    print("  recall@%d=%.4f recall@10=%.4f | median gold rank=%.1f (of %d atoms)" % (K, recall_k, recall10, med_rank, N), flush=True)
    print("  per-q: %s" % [(r["id"], r["best_cos"], r["best_rank"], r["in_topk"]) for r in scored], flush=True)
    return {"n_A": len(aqs), "n_scored": len(scored), "median_best_cos": round(med_cos, 4), "mean_best_cos": round(mean_cos, 4),
            "recall_at_k": round(recall_k, 4), "recall_at_10": round(recall10, 4), "median_gold_rank": med_rank,
            "K": K, "N_atoms": N, "rows": scored}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        msg = r["error"] + " " + str(r.get("note", r.get("n_A", "")))
        return ("UNKNOWN", "UNKNOWN: " + msg)
    mc = r["median_best_cos"]; rk = r["recall_at_k"]
    s = "median best-gold bge cos=%.4f (mean %.4f); recall@%d=%.4f recall@10=%.4f; median gold rank=%.1f/%d; n_scored=%d/%d; per-q=%s" % (
        mc, r["mean_best_cos"], r["K"], rk, r["recall_at_10"], r["median_gold_rank"], r["N_atoms"], r["n_scored"], r["n_A"],
        [(x["id"], x["best_cos"], x["best_rank"]) for x in r["rows"]])
    cue_bound = (mc < 0.40) or (rk < 0.60)
    cue_aligned = (mc >= 0.50) and (rk >= 0.75)
    if cue_bound:
        return ("HARD_PASS", "HARD_PASS (CUE-BOUND diagnosis): the A-axis IS query-encoding-limited -- A-gold atoms have low bge cue alignment (median cos %.2f) and/or fall outside top-%d (recall@%d %.2f). The lever is bge CUE QUALITY (query expansion/reformulation), NOT the route or index. Confirms the two-vector trilogy's free-text-path prediction. " % (mc, r["K"], r["K"], rk) + s)
    if cue_aligned:
        return ("HARD_PASS", "HARD_PASS (CUE-ALIGNED diagnosis): A-gold IS reachable by bge (median cos %.2f, recall@%d %.2f) -- the A-axis residual is NOT cue alignment but a downstream RANKING / keyword-UNION-precision problem. Lever is the route's selection/fusion, not the cue. " % (mc, r["K"], rk) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: mixed signal -- A-gold is partially bge-reachable; both cue quality and downstream ranking contribute. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
