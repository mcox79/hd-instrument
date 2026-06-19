"""DECISION 61a (DECISIVE Phase-3 trigger): score PRODUCTION M4d (sparse-keyed adjacency, beta=0.10, MAX_HOP=2, N_ANCHORS=20 -- the exact 0.272 config) ONCE on the 56d concept-disjoint blind held-out (SHA-256 locked). Tests whether M4d generalizes to NEW CONCEPTS (vs q54-q65 in-distribution concepts, 9/14 gold in dev). One-shot, NO tuning. Report macro-F1 + bge baseline (paired delta) + per-question. Pre-reg: F1>=0.20 TRIGGER-1 (Phase 3); <0.10 TRIGGER-2 (walk-external pivot); 0.10-0.20 TRIGGER-3. Substrate-internal; remote bge. ASCII; --self-test."""
from __future__ import annotations
import sys, time, json, hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import (
    _short, f1_present, bfs_proximity, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY)
ANCHOR_NAME = "substrate_61a_m4d_on_56d_concept_disjoint_heldout_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT_56D = DATA_ROOT / "benchmark_corpus_56d_concept_disjoint_heldout_v1.jsonl"
EXPECTED_SHA = "22d7eb01e5f4dfda2ed8a4ce6f66b3e4edbbfa8b21d9ab8532cb8747b272d418"
BETA = 0.10
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    if not HELDOUT_56D.exists():
        return {"error": "no_56d_file"}
    sha = hashlib.sha256(HELDOUT_56D.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA:
        return {"error": "SHA256_MISMATCH abort: %s != %s" % (sha, EXPECTED_SHA)}
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
    # PRODUCTION M4d adjacency: raw src_id/tgt_id (sparse-keyed; the 0.272 config; DECISION 59 sparse load-bearing)
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
    qs = [json.loads(l) for l in open(HELDOUT_56D, encoding="utf-8") if l.strip()]
    m4d_f1, bge_f1 = [], []; rows = []; n_gap = 0
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present:
            n_gap += 1; continue   # gap question (skip per 61a; 61b handles refuse)
        cands = r.semantic(q["question"], top_k=POOL_K)
        pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool:
            m4d_f1.append(0.0); bge_f1.append(0.0); continue
        bge_top5 = {_short(qid) for qid, _ in pool[:5]}
        cons = defaultdict(float)
        for a_qid, a_cos in pool[:N_ANCHORS]:
            for node, hop in bfs_proximity([a_qid], adj, MAX_HOP).items():
                if hop > 0: cons[node] += a_cos * (DECAY ** hop)
        m4d_top5 = {_short(qid) for qid, _ in sorted(((qid, cos + BETA * cons.get(qid, 0.0)) for qid, cos in pool), key=lambda t: -t[1])[:5]}
        bf = f1_present(bge_top5, present); mf = f1_present(m4d_top5, present)
        bge_f1.append(bf); m4d_f1.append(mf)
        rows.append({"qid": q["qid"], "chapter": q.get("chapter", ""), "bge": round(bf, 3), "m4d": round(mf, 3)})
    mac = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0
    bm, mm = mac(bge_f1), mac(m4d_f1)
    print("  SHA-256 VERIFIED. 56d: in-coverage scored=%d, gap-skipped=%d | beta=%.2f production-M4d" % (len(m4d_f1), n_gap, BETA), flush=True)
    print("  56d concept-disjoint: bge baseline=%.4f | M4d=%.4f (paired delta %+.4f)" % (bm, mm, mm - bm), flush=True)
    print("  (reference: q54-q65 in-distribution M4d=0.272)", flush=True)
    # per-chapter breakdown
    bychap = defaultdict(list)
    for x in rows: bychap[x["chapter"]].append(x["m4d"])
    for ch, vs in sorted(bychap.items()):
        print("    %-22s n=%d M4d-F1=%.3f" % (ch, len(vs), sum(vs) / len(vs)), flush=True)
    n_nonzero = sum(1 for x in rows if x["m4d"] > 0)
    print("  questions with M4d F1>0: %d/%d" % (n_nonzero, len(rows)), flush=True)
    return {"n_in_cov": len(m4d_f1), "n_gap": n_gap, "bge_baseline": bm, "m4d_f1": mm,
            "paired_delta": round(mm - bm, 4), "n_nonzero": n_nonzero, "rows": rows}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    f = r["m4d_f1"]
    s = ("DECISIVE 56d concept-disjoint blind held-out (n=%d in-cov; SHA-256 locked; one-shot beta=0.10): M4d F1=%.4f vs bge %.4f (paired delta %+.4f); "
         "%d/%d questions F1>0. Reference: q54-q65 in-distribution M4d=0.272." % (r["n_in_cov"], f, r["bge_baseline"], r["paired_delta"], r["n_nonzero"], r["n_in_cov"]))
    if f >= 0.20:
        return ("HARD_PASS", "TRIGGER-1 (substrate GENERALIZES to NEW CONCEPTS): F1_56d=%.4f >= 0.20. Phase 3 CO-EVOLVE-1 dispatch authorized. " % f + s)
    if f < 0.10:
        return ("HARD_FAIL", "TRIGGER-2 (substrate does NOT generalize to new concepts): F1_56d=%.4f < 0.10. M4d is in-distribution-concept only; Phase 3 needs walk-EXTERNAL mechanism / architectural redesign. " % f + s)
    return ("MIDDLE", "TRIGGER-3 (partial generalization): 0.10 <= F1_56d=%.4f < 0.20. Phase 3 scoped to what lifted; M7 + new-class both relevant. " % f + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
