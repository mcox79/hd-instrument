"""51c PREVIEW (pre-ratify): re-run M4d with the 12 Skunkworks 49a SHARES_MATH bridges ADDED to the graph (bridges connect existing real-named math atoms -> no re-encode needed). Tests whether graph densification from 49a lifts M4d above 0.272 BEFORE Testbed ratifies. beta=0.10 (dev-fixed). Substrate-internal; remote bge. ASCII; --self-test."""
from __future__ import annotations
import sys, time, json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import (
    _short, f1_present, bfs_proximity, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY)
ANCHOR_NAME = "substrate_m4d_preview_with_49a_bridges_heldout_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
BRIDGES = DATA_ROOT / "skunkworks_shares_math_bridges_v1.jsonl"
BETA = 0.10
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def _walk_top5(pool, adj, beta):
    cons = defaultdict(float)
    for a_qid, a_cos in pool[:N_ANCHORS]:
        for node, hop in bfs_proximity([a_qid], adj, MAX_HOP).items():
            if hop > 0: cons[node] += a_cos * (DECAY ** hop)
    scored = sorted(((qid, cos + beta * cons.get(qid, 0.0)) for qid, cos in pool), key=lambda t: -t[1])
    return {_short(qid) for qid, _ in scored[:5]}


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
    # resolver: short-name -> qualified id (for bridge endpoint resolution)
    short_to_q = {}
    for a in pstore.all_atoms():
        short_to_q.setdefault(_short(a.id), a.qualified_id)
    base_adj = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in WALK_EDGES:
                s = rr.get("src_id", ""); t = rr.get("tgt_id", "")
                if s and t and s != t: base_adj[s].add(t); base_adj[t].add(s)
    # bridge edges (resolve src/dst short -> qualified)
    bridge_edges = []
    if BRIDGES.exists():
        for ln in open(BRIDGES, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: b = json.loads(ln)
            except Exception: continue
            s = short_to_q.get(_short(b.get("src", "")), None)
            t = short_to_q.get(_short(b.get("dst", "")), None)
            if s and t and s != t: bridge_edges.append((s, t))
    enr_adj = defaultdict(set)
    for k, v in base_adj.items(): enr_adj[k] = set(v)
    for s, t in bridge_edges: enr_adj[s].add(t); enr_adj[t].add(s)
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    base_f1, enr_f1 = [], []
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present: continue
        cands = r.semantic(q["question"], top_k=POOL_K)
        pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool: continue
        base_f1.append(f1_present(_walk_top5(pool, base_adj, BETA), present))
        enr_f1.append(f1_present(_walk_top5(pool, enr_adj, BETA), present))
    mac = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0
    bm, em = mac(base_f1), mac(enr_f1)
    print("  bridges resolved: %d / 12 | in-coverage held-out n=%d | beta=%.2f" % (len(bridge_edges), len(base_f1), BETA), flush=True)
    print("  M4d base (current graph): %.4f | M4d + 49a bridges: %.4f (delta %+.4f)" % (bm, em, em - bm), flush=True)
    return {"n_bridges_resolved": len(bridge_edges), "m4d_base": bm, "m4d_with_bridges": em, "delta": round(em - bm, 4)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = "M4d 51c-preview: base=%.4f -> +49a bridges (%d resolved)=%.4f (delta %+.4f), beta=%.2f." % (
        r["m4d_base"], r["n_bridges_resolved"], r["m4d_with_bridges"], r["delta"], BETA)
    if r["delta"] >= 0.02:
        return ("PARTIAL", "49a bridges LIFT M4d (densification helps): " + s + " Full 51c (all enrichments ratified) likely lifts more.")
    if r["delta"] <= -0.01:
        return ("HARD_FAIL", "49a bridges HURT M4d: " + s)
    return ("MIDDLE", "49a bridges NEUTRAL on held-out M4d (12 bridges among foundations not on held-out anchor-paths): " + s + " Full densification (relabel + qclass + more edges) needed; 12 bridges alone insufficient.")


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
