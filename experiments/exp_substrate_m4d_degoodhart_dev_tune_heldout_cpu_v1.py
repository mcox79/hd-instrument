"""DECISION 50a M4d de-Goodhart: tune beta on a DEV set (v3_60q in-coverage, q01-q53) then measure HELD-OUT ONCE with that fixed beta -> unbiased M4d number (the M4d sweep picked best-beta ON held-out = Goodhart). Reuses M4d machinery. Substrate-internal; remote bge cache. ASCII; --self-test + metrics.json."""
from __future__ import annotations
import sys, time, json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import (
    _short, f1_present, bfs_proximity, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY, BETAS)
ANCHOR_NAME = "substrate_m4d_degoodhart_dev_tune_heldout_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
DEV = DATA_ROOT / "benchmark_corpus_v3_60q.jsonl"
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("A::B/c") == "c" and abs(f1_present({"a"}, {"a"}) - 1.0) < 1e-9
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def _build(pstore, r, qual, sset, adj, path):
    perq = []
    for q in (json.loads(l) for l in open(path, encoding="utf-8") if l.strip()):
        gold = q.get("ground_truth_atoms") or q.get("gold") or []
        if isinstance(gold, str): gold = [gold]
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present: continue
        cands = r.semantic(q["question"], top_k=POOL_K)
        pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool: continue
        cons = defaultdict(float)
        for a_qid, a_cos in pool[:N_ANCHORS]:
            for node, hop in bfs_proximity([a_qid], adj, MAX_HOP).items():
                if hop > 0: cons[node] += a_cos * (DECAY ** hop)
        perq.append({"present": present, "pool": pool, "cons": dict(cons)})
    return perq


def _macro(perq, beta):
    fs = []
    for x in perq:
        scored = sorted(((qid, cos + beta * x["cons"].get(qid, 0.0)) for qid, cos in x["pool"]), key=lambda t: -t[1])
        fs.append(f1_present({_short(qid) for qid, _ in scored[:5]}, x["present"]))
    return sum(fs) / len(fs) if fs else 0.0


def run() -> Dict:
    if not HELDOUT.exists() or not DEV.exists():
        return {"error": "missing_files"}
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    pstore = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    sset = {_short(a.id) for a in pstore.all_atoms()}
    adj = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in WALK_EDGES:
                s = rr.get("src_id", ""); t = rr.get("tgt_id", "")
                if s and t and s != t: adj[s].add(t); adj[t].add(s)
    dev = _build(pstore, r, qual, sset, adj, DEV)
    held = _build(pstore, r, qual, sset, adj, HELDOUT)
    # tune beta on DEV (exclude beta=0 from being chosen unless it wins)
    dev_scores = {b: round(_macro(dev, b), 4) for b in BETAS}
    best_beta = max(BETAS, key=lambda b: dev_scores[b])
    held_base = round(_macro(held, 0.0), 4)
    held_at_best = round(_macro(held, best_beta), 4)
    print("  DEV in-cov n=%d | HELD-OUT in-cov n=%d" % (len(dev), len(held)), flush=True)
    print("  DEV beta-sweep: %s" % dev_scores, flush=True)
    print("  -> DEV-best beta = %.2f" % best_beta, flush=True)
    print("  HELD-OUT: bge baseline=%.4f | M4d @ DEV-tuned beta=%.2f -> %.4f (lift %+.4f)" % (
        held_base, best_beta, held_at_best, held_at_best - held_base), flush=True)
    return {"dev_n": len(dev), "held_n": len(held), "dev_scores": dev_scores, "dev_best_beta": best_beta,
            "held_baseline": held_base, "held_m4d_unbiased": held_at_best, "lift": round(held_at_best - held_base, 4)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("M4d UNBIASED (beta=%.2f tuned on DEV q01-q53, measured once on held-out): held-out IN-COVERAGE bge=%.4f -> M4d=%.4f (lift %+.4f). "
         "No Goodhart: beta NOT tuned on held-out." % (r["dev_best_beta"], r["held_baseline"], r["held_m4d_unbiased"], r["lift"]))
    if r["held_m4d_unbiased"] >= 0.30:
        return ("HARD_PASS", "HARD_PASS (M4d unbiased >= 0.30): " + s)
    if r["lift"] >= 0.04:
        return ("PARTIAL", "PARTIAL (M4d unbiased lift >= 0.04, below 0.30): real substrate-internal gain, compose with M4b for 0.30. " + s)
    return ("HARD_FAIL", "HARD_FAIL (M4d unbiased lift < 0.04): DEV-tuned beta does not transfer to held-out. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
