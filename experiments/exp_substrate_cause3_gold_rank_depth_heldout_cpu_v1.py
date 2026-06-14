"""
exp_substrate_cause3_gold_rank_depth_heldout_cpu_v1.py -- scope the M4 decision: on IN-COVERAGE held-out questions (gold IS in index but retrieval fails), HOW DEEP does the present gold atom rank in the full bge ranking? -- runs on BGE machine.

ROUTING: Cause 3 characterization (capability-transfer gap; in-coverage F1=0.029 even when gold present). M4 (paraphrase-invariant retrieval) is the
  proposed fix but DEFERRED to USER scope decision (DECISION 35b). This DIAGNOSTIC (not the M4 build) quantifies how hard M4 must be. For each
  in-coverage held-out question, rank ALL atoms by bge cosine to the query and find where the PRESENT gold atom(s) sit:
   - gold ranks SHALLOW (best-gold-rank <= 20): a cheap top-K increase or light rerank recovers it -> M4 scope SMALL (the gold IS near the top, just
     outside the top-5 cutoff). Capability-transfer gap is a CUTOFF artifact, not a representation failure.
   - gold ranks DEEP (best-gold-rank >> 100): bge representation places the held-out paraphrase far from its gold -> paraphrase-invariance genuinely
     needed -> M4 scope LARGE (representation-level work).
  Reports per-question best-gold-rank + percentile + cosine(gold) vs cosine(top1), and the aggregate distribution. Substrate-internal (bge; no LLM).
  ASCII; --self-test + metrics.json.
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
ANCHOR_NAME = "substrate_cause3_gold_rank_depth_heldout_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def bucketize(ranks: List[int]) -> Dict[str, int]:
    b = {"top5": 0, "top20": 0, "top100": 0, "deeper": 0}
    for r in ranks:
        if r <= 5:
            b["top5"] += 1
        elif r <= 20:
            b["top20"] += 1
        elif r <= 100:
            b["top100"] += 1
        else:
            b["deeper"] += 1
    return b


def _selftest():
    b = bucketize([1, 4, 10, 50, 500])
    assert b == {"top5": 2, "top20": 1, "top100": 1, "deeper": 1}, b
    assert _short("foo::bar/baz") == "baz"
    print("[selftest] PASS: substrate_cause3_gold_rank_depth_heldout_cpu_v1", flush=True)


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
    sset = {_short(a.id) for a in pstore.all_atoms()}
    n_atoms = len(sset)
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    per = []
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present:
            continue  # in-coverage only
        # full ranking
        try:
            cands = r.semantic(q["question"], top_k=n_atoms)
        except Exception as e:
            per.append({"qid": q["qid"], "error": str(e)[:60]}); continue
        ranked_short = [_short(getattr(c, "atom_id", "")) for c in cands]
        scores = [float(getattr(c, "score", 0.0)) for c in cands]
        top1_score = scores[0] if scores else 0.0
        gold_ranks = []
        for gs in present:
            if gs in ranked_short:
                idx = ranked_short.index(gs)
                gold_ranks.append((idx + 1, scores[idx]))
        if not gold_ranks:
            per.append({"qid": q["qid"], "n_present": len(present), "best_rank": None, "note": "gold present in index but absent from bge ranking"})
            continue
        best = min(gold_ranks, key=lambda t: t[0])
        per.append({"qid": q["qid"], "n_present": len(present), "best_rank": best[0], "best_gold_score": round(best[1], 4),
                    "top1_score": round(top1_score, 4), "pctile": round(100.0 * (1 - best[0] / n_atoms), 2)})
    ranked_ok = [p for p in per if p.get("best_rank")]
    ranks = [p["best_rank"] for p in ranked_ok]
    buckets = bucketize(ranks) if ranks else {}
    med = int(np.median(ranks)) if ranks else None
    print("  n_atoms=%d | in-coverage questions with rankable gold: %d" % (n_atoms, len(ranked_ok)), flush=True)
    print("  qid        n_present  best_gold_rank  pctile   gold_score  top1_score", flush=True)
    for p in per:
        if p.get("best_rank"):
            print("  %-9s  %d          %-6d          %.2f    %.4f      %.4f" % (
                p["qid"], p["n_present"], p["best_rank"], p["pctile"], p["best_gold_score"], p["top1_score"]), flush=True)
        else:
            print("  %-9s  %s  -> %s" % (p["qid"], p.get("n_present", "?"), p.get("note") or p.get("error")), flush=True)
    print("  median best-gold-rank=%s | buckets: %s" % (med, buckets), flush=True)
    return {"n_atoms": n_atoms, "n_questions": len(ranked_ok), "median_best_rank": med, "buckets": buckets, "per_q": per}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    med = r["median_best_rank"]; b = r["buckets"]
    if med is None:
        return ("UNKNOWN", "no rankable gold")
    base = ("Cause-3 gold-rank depth on in-coverage held-out (n=%d q, %d atoms). Median best-gold-rank=%d. Buckets %s. Scopes M4: shallow=cheap "
            "top-K/rerank; deep=representation-level paraphrase-invariance." % (r["n_questions"], r["n_atoms"], med, b))
    shallow = b.get("top5", 0) + b.get("top20", 0)
    if med <= 20:
        return ("HARD_PASS", "M4 SCOPE SMALL (cheap fix likely): median present-gold ranks at %d (<=20) -- the gold IS near the top, just outside the "
                "top-5 answer cutoff. Capability-transfer gap is largely a CUTOFF artifact; a top-K increase or light rerank should recover much of "
                "it WITHOUT representation-level paraphrase-invariance. Test top-K=20 before committing to heavy M4. " % med + base)
    if med > 100:
        return ("HARD_FAIL", "M4 SCOPE LARGE (representation-level work needed): median present-gold ranks at %d (>100) -- bge places held-out "
                "paraphrases FAR from their gold. No cutoff tweak recovers this; paraphrase-invariant retrieval (M4a-d) is genuinely required. "
                "Confirms M4 is substantive, not a one-cycle tweak. " % med + base)
    return ("PARTIAL", "M4 SCOPE MEDIUM: median present-gold rank=%d (20-100). Mixed -- a top-K increase recovers the shallow tail; the deep tail "
            "needs M4. Recommend top-K=50 + measure the residual before sizing M4. (%d of %d in top-20). " % (med, shallow, r["n_questions"]) + base)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
