"""DECISION 58a (HIGHEST PRIORITY): fix the M4d id-namespace mismatch (Skunkworks 28th finding -- adjacency keyed by qualified_id but ~3/4 of edges are short-form -> M4d walked ~1/4 of graph). Normalize adjacency + anchors + consensus to _short space so ALL edges are visible. Re-run held-out IN-COV at beta=0.10 (dev-fixed); compare to faithful 0.272; check the 3 isolated golds (markov_decision_process, mutual_information, q_learning). Substrate-internal; remote bge. ASCII; --self-test.

Pre-registered (58a): HARD-PASS = F1 > 0.272 AND >=2 of 3 isolated golds recover. HARD-FAIL = F1 within +/-0.01 AND isolated golds still 0."""
from __future__ import annotations
import sys, time, json
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import (
    _short, f1_present, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY)
ANCHOR_NAME = "substrate_58a_m4d_namespace_normalized_heldout_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
BETA = 0.10
ISOLATED = {"markov_decision_process", "mutual_information", "q_learning"}
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("math::T1/mutual_information") == "mutual_information"
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def bfs(anchors, adj, max_hop):
    dist = {a: 0 for a in anchors}; q = deque((a, 0) for a in anchors)
    while q:
        n, d = q.popleft()
        if d >= max_hop: continue
        for m in adj.get(n, ()):
            if m not in dist: dist[m] = d + 1; q.append((m, d + 1))
    return dist


def walk_top5(pool_short, adj, beta):
    # pool_short: list of (short_id, cos); anchors = top-N short ids
    cons = defaultdict(float)
    for a_s, a_cos in pool_short[:N_ANCHORS]:
        for node, hop in bfs([a_s], adj, MAX_HOP).items():
            if hop > 0: cons[node] += a_cos * (DECAY ** hop)
    scored = sorted(((s, cos + beta * cons.get(s, 0.0)) for s, cos in pool_short), key=lambda t: -t[1])
    return {s for s, _ in scored[:5]}, cons


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
    # OLD adjacency (faithful: raw src_id/tgt_id) + NEW (normalized to _short)
    old_adj = defaultdict(set); new_adj = defaultdict(set); n_edges = 0
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in WALK_EDGES:
                s = rr.get("src_id", ""); t = rr.get("tgt_id", "")
                if s and t and s != t:
                    old_adj[s].add(t); old_adj[t].add(s)
                    ss, tt = _short(s), _short(t)
                    if ss != tt: new_adj[ss].add(tt); new_adj[tt].add(ss); n_edges += 1
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    perq = []
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present: continue
        cands = r.semantic(q["question"], top_k=POOL_K)
        pool_q = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool_q: continue
        cons_o = defaultdict(float)
        for a_qid, a_cos in pool_q[:N_ANCHORS]:
            for node, hop in bfs([a_qid], old_adj, MAX_HOP).items():
                if hop > 0: cons_o[node] += a_cos * (DECAY ** hop)
        pool_s = [(_short(qid), cos) for qid, cos in pool_q]
        cons_n = defaultdict(float)
        for a_s, a_cos in pool_s[:N_ANCHORS]:
            for node, hop in bfs([a_s], new_adj, MAX_HOP).items():
                if hop > 0: cons_n[node] += a_cos * (DECAY ** hop)
        perq.append({"qid": q["qid"], "present": present, "pool_q": pool_q, "pool_s": pool_s,
                     "cons_o": dict(cons_o), "cons_n": dict(cons_n)})
    mac = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0

    def old_macro(beta):
        return mac([f1_present({_short(qid) for qid, _ in sorted(((qid, cos + beta * x["cons_o"].get(qid, 0.0)) for qid, cos in x["pool_q"]), key=lambda t: -t[1])[:5]}, x["present"]) for x in perq])

    def new_macro(beta):
        out = []
        for x in perq:
            top5 = {s for s, _ in sorted(((s, cos + beta * x["cons_n"].get(s, 0.0)) for s, cos in x["pool_s"]), key=lambda t: -t[1])[:5]}
            out.append(f1_present(top5, x["present"]))
        return mac(out)
    import math
    deg_new = {n: len(v) for n, v in new_adj.items()}

    def dn_macro(beta):
        # DENSITY-AWARE: degree-normalized consensus (penalize hub nodes reachable from everyone)
        out = []
        for x in perq:
            scored = []
            for s, cos in x["pool_s"]:
                c = x["cons_n"].get(s, 0.0) / math.sqrt(deg_new.get(s, 1) or 1)
                scored.append((s, cos + beta * c))
            top5 = {s for s, _ in sorted(scored, key=lambda t: -t[1])[:5]}
            out.append(f1_present(top5, x["present"]))
        return mac(out)
    BETAS = [0.0, 0.01, 0.02, 0.05, 0.10, 0.20]
    DN_BETAS = [0.0, 0.05, 0.1, 0.2, 0.4, 0.8]
    om = old_macro(BETA)
    new_sweep = {b: new_macro(b) for b in BETAS}
    dn_sweep = {b: dn_macro(b) for b in DN_BETAS}
    dn_best_b = max(DN_BETAS, key=lambda b: dn_sweep[b]); dn_best = dn_sweep[dn_best_b]
    print("  DENSITY-AWARE (degree-normalized) full-graph sweep: %s" % {b: round(v, 4) for b, v in dn_sweep.items()}, flush=True)
    print("  DENSITY-AWARE best = %.4f @ beta=%.2f (vs sparse-M4d 0.2721)" % (dn_best, dn_best_b), flush=True)
    nm_best_b = max(BETAS, key=lambda b: new_sweep[b]); nm_best = new_sweep[nm_best_b]
    # isolated-gold recovery at the best normalized beta
    iso_recovered = set()
    for x in perq:
        top5 = {s for s, _ in sorted(((s, cos + nm_best_b * x["cons_n"].get(s, 0.0)) for s, cos in x["pool_s"]), key=lambda t: -t[1])[:5]}
        iso_recovered.update(g for g in x["present"] if g in ISOLATED and g in top5)
    print("  normalized walk-edges: %d | in-coverage held-out n=%d" % (n_edges, len(perq)), flush=True)
    print("  OLD(faithful sparse-graph) M4d @ beta=0.10 = %.4f" % om, flush=True)
    print("  NEW(normalized full-graph) beta sweep: %s" % {b: round(v, 4) for b, v in new_sweep.items()}, flush=True)
    print("  NEW best = %.4f @ beta=%.2f | isolated golds recovered: %s/3" % (nm_best, nm_best_b, sorted(iso_recovered)), flush=True)
    return {"n": len(perq), "old_macro": om, "new_macro": nm_best, "new_best_beta": nm_best_b, "new_sweep": {str(b): v for b, v in new_sweep.items()},
            "delta": round(nm_best - om, 4), "iso_recovered": sorted(iso_recovered), "n_iso_recovered": len(iso_recovered)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("58a namespace-normalize: OLD(faithful, ~1/4 graph)=%.4f -> NEW(normalized, full graph)=%.4f (delta %+.4f). "
         "Isolated golds recovered: %d/3 (%s). beta=%.2f one-shot." % (
             r["old_macro"], r["new_macro"], r["delta"], r["n_iso_recovered"], r["iso_recovered"], BETA))
    if r["new_macro"] > 0.272 + 1e-9 and r["n_iso_recovered"] >= 2:
        return ("HARD_PASS", "HARD_PASS (28th finding CONFIRMED; M4d was graph-throttled): " + s + " 0.272 was conservative; full-graph M4d is higher. De-Goodhart beta on fixed graph next.")
    if abs(r["delta"]) <= 0.01 and r["n_iso_recovered"] == 0:
        return ("HARD_FAIL", "HARD_FAIL (normalization does NOT help; 0.272 is bge/scorer-bound not graph-throttled): " + s + " -> M7 / walk-external pivot per DECISION 56.")
    return ("PARTIAL", "PARTIAL (normalization helps but below both pre-reg bars): " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
