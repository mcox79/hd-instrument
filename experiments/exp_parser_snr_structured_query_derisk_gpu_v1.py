"""
exp_parser_snr_structured_query_derisk_gpu_v1.py -- de-risk Cycle-52 Technique 1 (structured Tier-A query parse) for parser-SNR -- GPU/bge.

ROUTING: Research's Cycle 52 priority is nl_to_hrr_parser SNR improvement; Technique 1 = pipe the query through substrate Tier-A
  NL primitives (POS/chunk/NER) to a STRUCTURED representation before mapping to atoms, expected +0.04-0.06. Before Testbed
  commits the ~11-day build, this Exp-Dev cell DE-RISKS the premise cheaply: does a structured-term query (lightweight Tier-A
  proxy -- content words / candidate entities, drop question-words + stopwords) improve query->atom retrieval SNR over RAW-text
  bge on the benchmark? Metric per free-text question (A content + E methodology + G): gold bge cosine, gold RANK, recall@3/@10.
  My A/E cue-alignment finding shows raw bge already ranks gold ~0 -- so this is decisive either way: if structured beats raw,
  Technique 1's retrieval premise is validated; if not, the retrieval-SNR benefit is limited and the parser payoff is elsewhere
  (compose/decode, not benchmark retrieval) -- valuable signal for scoping the Cycle 52 build. NO generative LLM (bge embedding).

PRE-REGISTERED: HARD-PASS structured query improves mean gold-rank (lower) AND recall@3 by a clear margin (recall@3 +0.05 or
  median-rank improvement >=1 position). MIDDLE small improvement. HARD-FAIL structured does not beat raw (raw bge already
  saturates retrieval SNR -> Technique 1's lift is NOT in benchmark retrieval; informs Testbed scoping). UNKNOWN if bge/bench absent.
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
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "parser_snr_structured_query_derisk_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
# question-words + generic stopwords to strip for the structured-term query (lightweight Tier-A proxy)
QWORDS = {"what", "which", "how", "when", "where", "who", "do", "does", "did", "i", "have", "are", "is", "the", "a", "an",
          "of", "to", "and", "in", "on", "for", "about", "atoms", "atom", "my", "me", "can", "should", "would", "with", "that",
          "this", "it", "as", "by", "or", "be", "apply", "exist", "serve", "serves", "relations", "relation"}


def _norm(x):
    return str(x).split("::")[-1].strip().lower()


def _structured_terms(q):
    """lightweight Tier-A proxy: keep content tokens (>=3 chars, not question/stopword), preserve CamelCase/ID-ish tokens."""
    toks = re.findall(r"[A-Za-z0-9_\-]+", q)
    keep = [t for t in toks if len(t) >= 3 and t.lower() not in QWORDS]
    return " ".join(keep) if keep else q


def _selftest():
    s = _structured_terms("What atoms do I have about FHRR binding?")
    assert "FHRR" in s and "binding" in s and "atoms" not in s.lower().split(), s
    print("[selftest] PASS: parser_snr_structured_query_derisk_gpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch  # PROT-020
    _ = torch.cuda.is_available()
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)


def _stats(ranks, coss, K=3):
    ranks = np.array(ranks); coss = np.array(coss)
    return {"median_rank": float(np.median(ranks)), "mean_rank": round(float(ranks.mean()), 2),
            "recall_at_3": round(float((ranks < 3).mean()), 4), "recall_at_10": round(float((ranks < 10).mean()), 4),
            "median_cos": round(float(np.median(coss)), 4)}


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    bench_fp = REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl"
    if not bench_fp.exists():
        return {"error": "benchmark_missing"}
    raw = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    qs = []
    for r in raw:
        ax = r.get("type", "A").split("_")[0].upper()
        if ax not in ("A", "E", "G"):   # free-text-cue axes
            continue
        gold = [_norm(g) for g in (r.get("ground_truth_atoms") or r.get("gold") or [])]
        if not gold:
            continue
        args = r.get("args") or {}
        raw_q = args.get("topic") or args.get("scenario") or r.get("question", "")
        qs.append({"id": r.get("qid") or r.get("id"), "ax": ax, "raw": raw_q,
                   "struct": _structured_terms(r.get("question", "") or raw_q), "gold": gold})
    if SMOKE: qs = qs[:5]
    idx_dir = REPO / "data" / "substrate_index"
    if not idx_dir.exists():
        return {"error": "no_substrate_index"}
    pstore = PartitionedStore(idx_dir); atoms = pstore.all_atoms()
    try:
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        enc = AtomEncoder(); retr = Retriever(getattr(pstore, "store", pstore), enc); retr.rebuild_index()
    except Exception as e:
        return {"error": "bge_unavailable", "note": str(e)[:160]}
    id_order = retr._id_order; sem = retr._semantic_matrix; norm_ids = [_norm(i) for i in id_order]
    nid_row = {nid: i for i, nid in enumerate(norm_ids)}
    N = sem.shape[0]
    def eval_query(text, gold_present):
        qv = enc.bge.encode([text])[0].astype(np.float32); qv /= (np.linalg.norm(qv) + 1e-9)
        sims = sem @ qv; order = np.argsort(-sims)
        rank_of = {id_order[order[r]]: r for r in range(N)}
        best_cos = max(float(sims[nid_row[g]]) for g in gold_present)
        best_rank = min(rank_of[id_order[nid_row[g]]] for g in gold_present)
        return best_rank, best_cos
    raw_ranks = []; raw_cos = []; str_ranks = []; str_cos = []; rows = []
    for q in qs:
        gp = [g for g in q["gold"] if g in nid_row]
        if not gp:
            continue
        rr, rc = eval_query(q["raw"], gp); sr, sc = eval_query(q["struct"], gp)
        raw_ranks.append(rr); raw_cos.append(rc); str_ranks.append(sr); str_cos.append(sc)
        rows.append({"id": q["id"], "ax": q["ax"], "raw_rank": rr, "struct_rank": sr, "raw_cos": round(rc, 3), "struct_cos": round(sc, 3)})
    raw_s = _stats(raw_ranks, raw_cos); str_s = _stats(str_ranks, str_cos)
    print("  n=%d free-text questions (A+E+G)" % len(rows), flush=True)
    print("  RAW-text query:        %s" % raw_s, flush=True)
    print("  STRUCTURED-term query: %s" % str_s, flush=True)
    d_r3 = round(str_s["recall_at_3"] - raw_s["recall_at_3"], 4); d_mr = round(raw_s["median_rank"] - str_s["median_rank"], 2)
    print("  delta: recall@3 %+.4f | median-rank improvement %+.1f (positive = structured better)" % (d_r3, d_mr), flush=True)
    return {"n": len(rows), "raw": raw_s, "structured": str_s, "delta_recall_at_3": d_r3, "delta_median_rank": d_mr, "rows": rows}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("note", "")))
    dr = r["delta_recall_at_3"]; dm = r["delta_median_rank"]
    s = "n=%d; RAW=%s; STRUCTURED=%s; delta recall@3=%+.4f median-rank-improvement=%+.1f" % (
        r["n"], r["raw"], r["structured"], dr, dm)
    if dr >= 0.05 or dm >= 1.0:
        return ("HARD_PASS", "HARD_PASS: a structured-term query IMPROVES query->atom retrieval SNR over raw text -- Cycle-52 Technique 1's retrieval premise is validated; structured Tier-A parse is worth Testbed's build. " + s)
    if dr >= 0.02 or dm >= 0.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: structured query gives a small retrieval-SNR improvement -- Technique 1 helps marginally on benchmark retrieval. " + s)
    return ("HARD_FAIL", "HARD_FAIL: structured query does NOT beat raw bge on benchmark retrieval -- raw bge already saturates query->atom retrieval SNR (gold ~rank 0). Technique 1's lift is NOT in benchmark retrieval; the parser-SNR payoff is in compose/decode (NL->algebra-HRR for reasoning), not retrieval. Scopes the Cycle 52 build away from the retrieval path. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
