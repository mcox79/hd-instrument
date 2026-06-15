"""DECISION 51 (M4d optimization): jointly dev-tune M4d (MAX_HOP in {2,3}, beta in sweep) on DEV q01-q53, measure held-out ONCE at dev-best (hop,beta). Cheap shot at the 0.30 bar via deeper graph reach, no held-out Goodhart. Reuses M4d primitives. Substrate-internal; remote bge. ASCII; --self-test."""
from __future__ import annotations
import sys, time, json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import (
    _short, f1_present, bfs_proximity, WALK_EDGES, POOL_K, N_ANCHORS, DECAY, BETAS)
ANCHOR_NAME = "substrate_m4d_hop_beta_jointtune_heldout_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
DEV = DATA_ROOT / "benchmark_corpus_v3_60q.jsonl"
HOPS = [2, 3]
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def _build(r, qual, sset, adj, path, hop):
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
            for node, h in bfs_proximity([a_qid], adj, hop).items():
                if h > 0: cons[node] += a_cos * (DECAY ** h)
        perq.append({"present": present, "pool": pool, "cons": dict(cons)})
    return perq


def _macro(perq, beta):
    fs = []
    for x in perq:
        sc = sorted(((qid, cos + beta * x["cons"].get(qid, 0.0)) for qid, cos in x["pool"]), key=lambda t: -t[1])
        fs.append(f1_present({_short(qid) for qid, _ in sc[:5]}, x["present"]))
    return sum(fs) / len(fs) if fs else 0.0


def run() -> Dict:
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
    grid = {}
    best = None
    for hop in HOPS:
        dev = _build(r, qual, sset, adj, DEV, hop)
        for beta in BETAS:
            dm = round(_macro(dev, beta), 4)
            grid[(hop, beta)] = dm
            if best is None or dm > best[2]:
                best = (hop, beta, dm)
    bh, bb, bdev = best
    held = _build(r, qual, sset, adj, HELDOUT, bh)
    held_base = round(_macro(held, 0.0), 4)
    held_best = round(_macro(held, bb), 4)
    print("  DEV grid (hop,beta)->F1:", flush=True)
    for hop in HOPS:
        print("   hop=%d: %s" % (hop, {b: grid[(hop, b)] for b in BETAS}), flush=True)
    print("  DEV-best: hop=%d beta=%.2f (dev F1=%.4f)" % (bh, bb, bdev), flush=True)
    print("  HELD-OUT: bge=%.4f | M4d@dev-best(hop=%d,beta=%.2f)=%.4f (lift %+.4f)" % (held_base, bh, bb, held_best, held_best - held_base), flush=True)
    return {"dev_best_hop": bh, "dev_best_beta": bb, "dev_best_f1": bdev, "held_base": held_base,
            "held_m4d": held_best, "lift": round(held_best - held_base, 4), "grid": {str(k): v for k, v in grid.items()}}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = "M4d joint hop/beta dev-tuned (hop=%d beta=%.2f): held-out %.4f (bge %.4f, lift %+.4f). No held-out Goodhart." % (
        r["dev_best_hop"], r["dev_best_beta"], r["held_m4d"], r["held_base"], r["lift"])
    if r["held_m4d"] >= 0.30:
        return ("HARD_PASS", "HARD_PASS (M4d alone clears 0.30 with deeper reach): " + s)
    if r["lift"] >= 0.04:
        return ("PARTIAL", "PARTIAL: " + s)
    return ("HARD_FAIL", "HARD_FAIL (no transfer): " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
