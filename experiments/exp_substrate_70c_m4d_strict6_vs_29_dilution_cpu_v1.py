"""DECISION 70c -- does the CURATED 6-STRICT edge subset dilute M4d LESS than the broad 29? Tests the 'confidence-tiered subset preserves selectivity' hypothesis (Exp-Dev dilution recommendation + Claim 6 high-quality-subgraph). M4d (production beta=0.10, sparse-keyed) on q54-q65 + 56d under 3 adjacencies: base / base+6-STRICT / base+29. Edges connect existing atoms (no re-sync; bge pool unchanged). Remote bge. ASCII; --self-test."""
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
ALL29 = DATA_ROOT / "coevolve1_iter1_P1bge_ACCEPT_edges.jsonl"
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
    all29_q = []
    if ALL29.exists():
        for ln in open(ALL29, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: e = json.loads(ln)
            except Exception: continue
            all29_q.append((e.get("src_id", ""), e.get("tgt_id", "")))
    adj_s6, n6 = plus(strict_q); adj_29, n29 = plus(all29_q)

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
        b = score(path, base); s6 = score(path, adj_s6); a29 = score(path, adj_29)
        out[nm] = {"base": b, "strict6": s6, "all29": a29, "delta_strict6": round(s6 - b, 4), "delta_all29": round(a29 - b, 4)}
        print("  %-8s base=%.4f | +6-STRICT=%.4f (%+.4f) | +29-all=%.4f (%+.4f)" % (nm, b, s6, s6 - b, a29, a29 - b), flush=True)
    print("  edges added: strict=%d all=%d" % (n6, n29), flush=True)
    return {"strict6_edges": n6, "all29_edges": n29, "q54q65": out["q54q65"], "h56d": out["56d"]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    dq6 = r["q54q65"]["delta_strict6"]; dq29 = r["q54q65"]["delta_all29"]
    s = ("70c curated-subset dilution test: q54-q65 base %.4f -> +6-STRICT %.4f (%+.4f) vs +29-all %.4f (%+.4f); 56d +6-STRICT %+.4f vs +29 %+.4f. Edges connect existing atoms (no re-sync)." % (
        r["q54q65"]["base"], r["q54q65"]["strict6"], dq6, r["q54q65"]["all29"], dq29, r["h56d"]["delta_strict6"], r["h56d"]["delta_all29"]))
    if dq6 >= -0.01 and dq6 > dq29 + 1e-9:
        return ("HARD_PASS", "CURATED 6-STRICT preserves selectivity (dilutes LESS than 29; near-neutral): " + s + " Supports confidence-tiered-subset path (Claim 6 high-quality-subgraph) -- sound growth into broad substrate + M4d on STRICT subset.")
    if dq6 > dq29 + 1e-9:
        return ("PARTIAL", "6-STRICT dilutes LESS than 29 but still negative -- fewer edges = less dilution, but the tension persists even for strict edges: " + s)
    return ("MIDDLE", "6-STRICT does not clearly beat 29 -- dilution tension is fundamental even at 6 edges: " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_70c_m4d_strict6_vs_29_dilution", flush=True)
    out_dir = get_output_dir("substrate_70c_m4d_strict6_vs_29_dilution_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_70c_m4d_strict6_vs_29_dilution_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
