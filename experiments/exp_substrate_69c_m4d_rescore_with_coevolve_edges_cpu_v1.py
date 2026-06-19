"""DECISION 69c -- CO-EVOLVE-1 Iteration 1 METRIC: re-run M4d with the 29 autonomously-discovered edges ADDED to the graph-walk adjacency (no remote re-sync needed -- edges connect EXISTING atoms so the bge pool is unchanged; only adjacency gains +29 edges). Measure M4d delta on q54-q65 + 56d (does autonomous edge-growth lift retrieval? esp. Q61 whose gold mutual_information now connects to shannon_entropy). Production M4d (beta=0.10, sparse-keyed). Substrate-internal; remote bge. ASCII; --self-test."""
from __future__ import annotations
import sys, json, time, hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import _short, f1_present, bfs_proximity, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY
DATA_ROOT = REPO / "data" / "substrate_index"
HELD_Q = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
HELD_56D = DATA_ROOT / "benchmark_corpus_56d_concept_disjoint_heldout_v1.jsonl"
SHA_56D = "22d7eb01e5f4dfda2ed8a4ce6f66b3e4edbbfa8b21d9ab8532cb8747b272d418"
COEVOLVE_EDGES = DATA_ROOT / "coevolve1_iter1_P1bge_ACCEPT_edges.jsonl"
BETA = 0.10
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    if HELD_56D.exists() and hashlib.sha256(HELD_56D.read_bytes()).hexdigest() != SHA_56D:
        return {"error": "56d SHA mismatch"}
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    ps = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(ps, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in ps.all_atoms()}
    sset = {_short(a.id) for a in ps.all_atoms()}
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
    # enriched adjacency = base + 29 coevolve edges
    enr_adj = defaultdict(set)
    for k, v in base_adj.items(): enr_adj[k] = set(v)
    n_ce = 0
    if COEVOLVE_EDGES.exists():
        for ln in open(COEVOLVE_EDGES, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: e = json.loads(ln)
            except Exception: continue
            s = e.get("src_id", ""); t = e.get("tgt_id", "")
            if s and t and s != t: enr_adj[s].add(t); enr_adj[t].add(s); n_ce += 1

    def score(path, adj):
        fs = []
        for q in (json.loads(l) for l in open(path, encoding="utf-8") if l.strip()):
            gold = q.get("ground_truth_atoms") or []
            present = {_short(g) for g in gold if _short(g) in sset}
            if not present: continue
            cands = r.semantic(q["question"], top_k=POOL_K)
            pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
            if not pool: continue
            cons = defaultdict(float)
            for a_qid, a_cos in pool[:N_ANCHORS]:
                for node, hop in bfs_proximity([a_qid], adj, MAX_HOP).items():
                    if hop > 0: cons[node] += a_cos * (DECAY ** hop)
            top5 = {_short(qid) for qid, _ in sorted(((qid, cos + BETA * cons.get(qid, 0.0)) for qid, cos in pool), key=lambda t: -t[1])[:5]}
            fs.append((q.get("qid", ""), f1_present(top5, present)))
        return fs
    out = {}
    for nm, path in [("q54q65", HELD_Q), ("56d", HELD_56D)]:
        b = score(path, base_adj); e = score(path, enr_adj)
        bm = round(sum(f for _, f in b) / len(b), 4) if b else 0.0
        em = round(sum(f for _, f in e) / len(e), 4) if e else 0.0
        improved = [qid for (qid, fb), (_, fe) in zip(b, e) if fe > fb + 1e-9]
        out[nm] = {"base": bm, "enriched": em, "delta": round(em - bm, 4), "improved_qs": improved}
        print("  %-8s base-M4d=%.4f -> +29-coevolve-edges=%.4f (delta %+.4f) improved=%s" % (nm, bm, em, em - bm, improved or "-"), flush=True)
    print("  coevolve edges loaded into adjacency: %d" % n_ce, flush=True)
    return {"n_coevolve_edges": n_ce, "q54q65": out["q54q65"], "h56d": out["56d"]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    dq = r["q54q65"]["delta"]; d5 = r["h56d"]["delta"]
    s = ("CO-EVOLVE-1 Iter1 METRIC: M4d with 29 autonomous edges -- q54-q65 %.4f->%.4f (%+.4f, improved %s); 56d %.4f->%.4f (%+.4f, improved %s). Edges connect existing atoms (no re-sync; bge pool unchanged)." % (
        r["q54q65"]["base"], r["q54q65"]["enriched"], dq, r["q54q65"]["improved_qs"] or "-",
        r["h56d"]["base"], r["h56d"]["enriched"], d5, r["h56d"]["improved_qs"] or "-"))
    if dq > 1e-9 or d5 > 1e-9:
        return ("HARD_PASS", "Autonomous edge-growth LIFTS M4d retrieval (the loop's edges improve held-out F1): " + s)
    return ("MIDDLE", "Autonomous edges NEUTRAL on held-out M4d this iteration (edges target MDP/q_learning/MI; held-out has few such questions; the connected golds may not be the bge-anchored ones): " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_69c_m4d_rescore_with_coevolve_edges", flush=True)
    out_dir = get_output_dir("substrate_69c_m4d_rescore_with_coevolve_edges_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_69c_m4d_rescore_with_coevolve_edges_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
