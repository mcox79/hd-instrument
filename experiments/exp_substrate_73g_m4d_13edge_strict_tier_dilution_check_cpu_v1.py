"""DECISION 73g (Exp-Dev pre-vet, on critical path) -- does the STRICT-confidence retrieval tier stay DILUTION-SAFE when it grows from 6 (Iter 1) to 13 edges (6 Iter1-STRICT + 7 Iter2 full-P2 ACCEPT)? Claim 12 R1 confirmed dilution-neutral at 6 edges (70c/72b); this checks the SAME tier at 13. Upper-bound (assumes all 7 Iter2 ratify; Skunkworks vet pending). M4d production beta=0.10, sparse-keyed, on q54-q65 + 56d under base / base+6 / base+13. In-memory adjacency (edges connect existing atoms; no re-sync, no substrate mutation, no held-out touch). Remote bge. ASCII; --self-test."""
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
ITER2 = DATA_ROOT / "coevolve1_iter2_fullP2_ACCEPT_edges.jsonl"
STRICT6 = [("mutual_information", "shannon_entropy"), ("markov_decision_process", "markov_chain_property_lemma"),
           ("markov_decision_process", "probability_space"), ("markov_decision_process", "markov_chain"),
           ("q_learning", "bellman_equation"), ("q_learning", "markov_decision_process")]
BETA = 0.10
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"; print("[selftest] PASS", flush=True)


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
    short2q = {}
    for a in ps.all_atoms(): short2q.setdefault(_short(a.id), a.qualified_id)
    base = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in WALK_EDGES:
                s = rr.get("src_id", ""); t = rr.get("tgt_id", "")
                if s and t and s != t: base[s].add(t); base[t].add(s)

    def plus(edges_qual):
        a = defaultdict(set)
        for k, v in base.items(): a[k] = set(v)
        n = 0
        for s, t in edges_qual:
            if s and t and s != t: a[s].add(t); a[t].add(s); n += 1
        return a, n
    strict_q = [(short2q.get(s, s), short2q.get(t, t)) for s, t in STRICT6]
    iter2_q = []
    if ITER2.exists():
        for ln in open(ITER2, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: e = json.loads(ln)
            except Exception: continue
            iter2_q.append((short2q.get(_short(e.get("src_id", "")), e.get("src_id", "")),
                            short2q.get(_short(e.get("tgt_id", "")), e.get("tgt_id", ""))))
    adj_s6, n6 = plus(strict_q); adj_s13, n13 = plus(strict_q + iter2_q)

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
            fs.append(f1_present(top5, present))
        return round(sum(fs) / len(fs), 4) if fs else 0.0
    out = {}
    for nm, path in [("q54q65", HELD_Q), ("56d", HELD_56D)]:
        b = score(path, base); s6 = score(path, adj_s6); s13 = score(path, adj_s13)
        out[nm] = {"base": b, "strict6": s6, "strict13": s13, "d6": round(s6 - b, 4), "d13": round(s13 - b, 4), "d13_vs_6": round(s13 - s6, 4)}
        print("  %-8s base=%.4f | +6-STRICT=%.4f (%+.4f) | +13-STRICT-tier=%.4f (%+.4f) | 13-vs-6 %+.4f" % (
            nm, b, s6, s6 - b, s13, s13 - b, s13 - s6), flush=True)
    print("  edges added: 6-STRICT=%d  13-tier=%d (6 Iter1-STRICT + 7 Iter2 full-P2 ACCEPT)" % (n6, n13), flush=True)
    return {"strict6_edges": n6, "strict13_edges": n13, "q54q65": out["q54q65"], "h56d": out["56d"]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    d13 = r["q54q65"]["d13"]; d13v6 = r["q54q65"]["d13_vs_6"]
    s = ("73g 13-edge STRICT-tier dilution pre-check (upper-bound; Skunkworks vet pending): q54-q65 base %.4f -> +6 %.4f (%+.4f) -> +13 %.4f (%+.4f; 13-vs-6 %+.4f); 56d +6 %+.4f -> +13 %+.4f. In-memory adjacency, no substrate mutation, no held-out touch." % (
        r["q54q65"]["base"], r["q54q65"]["strict6"], r["q54q65"]["d6"], r["q54q65"]["strict13"], d13, d13v6,
        r["h56d"]["d6"], r["h56d"]["d13"]))
    if d13 >= -0.01 and d13v6 >= -0.01:
        return ("HARD_PASS", "STRICT-tier stays DILUTION-SAFE at 13 edges (>=-0.01 vs base AND vs 6): " + s + " Claim 12 R1 holds as the tier grows -> ratifying the 7 Iter2 edges into the STRICT tier is dilution-safe.")
    if d13 >= -0.01:
        return ("PARTIAL", "13-tier dilution-safe vs base but 7 Iter2 edges add slight dilution vs 6: " + s)
    return ("MIDDLE", "13-tier dilutes vs base -- adding the 7 Iter2 edges to the retrieval tier hurts; recommend GROWTH-tier-only for some Iter2 edges: " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_73g_m4d_13edge_strict_tier_dilution_check", flush=True)
    out_dir = get_output_dir("substrate_73g_m4d_13edge_strict_tier_dilution_check_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_73g_m4d_13edge_strict_tier_dilution_check_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
