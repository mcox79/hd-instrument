"""DECISION 51b M4b -- query-side reformulation via PSEUDO-RELEVANCE FEEDBACK (PRF), composed with M4d consensus graph walk. Principled + leakage-free (uses the substrate's OWN atom names as expansion terms; NO LLM; NO per-question hand-tuned templates -> no held-out leakage). For each held-out query: bge top-5 -> expansion terms = their atom names; expanded query = original + terms; bge top-300 on expanded UNION original top-300 (max cosine); then M4d consensus walk (beta=0.10 dev-fixed). Compare to bge-only (0.148) + M4d-only (0.272). HARD-PASS composite >= 0.30. Substrate-internal; remote bge. ASCII; --self-test + metrics.json."""
from __future__ import annotations
import sys, time, json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import (
    _short, f1_present, bfs_proximity, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY)
ANCHOR_NAME = "substrate_m4b_prf_plus_m4d_composite_heldout_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
BETA = 0.10        # dev-fixed (DECISION 51a de-Goodhart)
PRF_K = 5          # standard PRF depth (fixed; not tuned on held-out)
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("X::Y/z") == "z" and abs(f1_present({"a"}, {"a"}) - 1.0) < 1e-9
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def _consensus_walk(pool, adj, beta):
    cons = defaultdict(float)
    for a_qid, a_cos in pool[:N_ANCHORS]:
        for node, hop in bfs_proximity([a_qid], adj, MAX_HOP).items():
            if hop > 0: cons[node] += a_cos * (DECAY ** hop)
    scored = sorted(((qid, cos + beta * cons.get(qid, 0.0)) for qid, cos in pool), key=lambda t: -t[1])
    return {_short(qid) for qid, _ in scored[:5]}


def run() -> Dict:
    if not HELDOUT.exists():
        return {"error": "no_heldout"}
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    pstore = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    name_of = {a.id: (a.name or a.id) for a in pstore.all_atoms()}
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

    def pool_of(query):
        cands = r.semantic(query, top_k=POOL_K)
        return [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands], cands

    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    bge_f1, m4d_f1, comp_f1 = [], [], []
    rows = []
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present: continue
        base_pool, base_cands = pool_of(q["question"])
        if not base_pool: continue
        # PRF: expansion terms from top-5 atom names
        exp_terms = " ".join(name_of.get(c.atom_id, "") for c in base_cands[:PRF_K])
        exp_pool, _ = pool_of(q["question"] + " " + exp_terms)
        # union (max cosine per qid)
        merged = {}
        for qid, cos in base_pool + exp_pool:
            merged[qid] = max(merged.get(qid, 0.0), cos)
        union_pool = sorted(merged.items(), key=lambda t: -t[1])
        # metrics
        bge_top5 = {_short(qid) for qid, _ in base_pool[:5]}
        bf = f1_present(bge_top5, present)
        mf = f1_present(_consensus_walk(base_pool, adj, BETA), present)          # M4d only
        cf = f1_present(_consensus_walk(union_pool, adj, BETA), present)         # M4b+M4d composite
        bge_f1.append(bf); m4d_f1.append(mf); comp_f1.append(cf)
        rows.append({"qid": q["qid"], "bge": round(bf, 3), "m4d": round(mf, 3), "composite": round(cf, 3)})
    mac = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0
    bge_m, m4d_m, comp_m = mac(bge_f1), mac(m4d_f1), mac(comp_f1)
    print("  IN-COVERAGE held-out n=%d | beta=%.2f (dev-fixed) | PRF_K=%d" % (len(rows), BETA, PRF_K), flush=True)
    print("  qid        bge     M4d     M4b+M4d", flush=True)
    for x in rows:
        print("  %-9s  %.3f   %.3f   %.3f" % (x["qid"], x["bge"], x["m4d"], x["composite"]), flush=True)
    print("  MACRO:     %.4f  %.4f  %.4f" % (bge_m, m4d_m, comp_m), flush=True)
    return {"n": len(rows), "bge": bge_m, "m4d": m4d_m, "composite": comp_m,
            "comp_vs_m4d": round(comp_m - m4d_m, 4), "rows": rows}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("M4b(PRF)+M4d composite (DECISION 51b). IN-COVERAGE: bge=%.4f, M4d=%.4f, composite=%.4f (composite vs M4d %+.4f). beta=%.2f dev-fixed, PRF_K=%d." % (
        r["bge"], r["m4d"], r["composite"], r["comp_vs_m4d"], BETA, PRF_K))
    if r["composite"] >= 0.30 and r["comp_vs_m4d"] >= 0:
        return ("HARD_PASS", "HARD_PASS (composite >= 0.30): M4b query expansion + M4d graph walk clears the bar. " + s)
    if r["comp_vs_m4d"] >= 0.02:
        return ("PARTIAL", "PARTIAL (M4b adds to M4d, below 0.30): PRF expansion helps the graph walk; compose with graph densification (49a/49c). " + s)
    if r["comp_vs_m4d"] < 0:
        return ("HARD_FAIL", "HARD_FAIL (M4b HURTS M4d): PRF expansion adds noise / drifts; drop PRF, keep M4d-only (0.272). " + s)
    return ("MIDDLE", "MIDDLE (M4b neutral on top of M4d): PRF does not add; M4d-only 0.272 stands. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
