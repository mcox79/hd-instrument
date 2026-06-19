"""DECISION 82 follow-up (Exp-Dev, GPU) -- did the DECISION 79/81 cycle-cleanup (10 wrong-direction DEPENDS_ON edges removed; 2 fhrr re-typed DUAL) change the HEADLINE M4d held-out F1? Validates Claim 14 (substrate self-corrects own graph) at the RETRIEVAL-F1 level, complementing the axiom-termination capability_preservation already shown (78d/79a). Non-destructive: the substrate still has the pre-cleanup edges; we remove the 10 cleanup edges IN-MEMORY to simulate post-cleanup, and score M4d on held-out under base (pre-cleanup) vs base-minus-10 (post-cleanup). M4d beta=0.10. bge (remote GPU). ASCII; --self-test.
HARD-PASS: |post - pre| <= 0.01 on q54-q65 AND 56d -> cleanup preserved headline retrieval capability (capability_preservation=1.0 extends to M4d F1). Larger drop -> a removed edge was retrieval-load-bearing (would warrant review)."""
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
# the 10 DEPENDS_ON edges removed by DECISION 79/81 cycle-cleanup (8 cycle backsides + 2 fhrr re-typed DUAL)
CLEANUP_REMOVED = [("graph_topology", "bipartite_graph"), ("partial_derivative", "gradient"),
                   ("metric_space", "euclidean_distance"), ("derivative", "gradient"),
                   ("conditional_probability", "bayes_rule"), ("measure_space", "probability_space"),
                   ("gradient", "gradient_descent"), ("inner_product", "cosine_similarity"),
                   ("fhrr_bind", "fhrr_unbind"), ("fhrr_unbind", "fhrr_bind")]
BETA = 0.10
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c" and len(CLEANUP_REMOVED) == 10
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
    # post-cleanup adjacency = base minus the 10 removed edges. Match by SHORT-name pair (both dirs) --
    # robust to tier-prefix + DUPLICATE atoms (cosine_similarity exists at T1 AND T3) which broke a qualified-id resolver.
    removed_short = set()
    for s, t in CLEANUP_REMOVED:
        removed_short.add(frozenset((s, t)))
    post = defaultdict(set)
    n_removed = 0
    for k, vs in base.items():
        for v in vs:
            if frozenset((_short(k), _short(v))) in removed_short: n_removed += 1; continue
            post[k].add(v)

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
        pre = score(path, base); pos = score(path, post)
        out[nm] = {"pre": pre, "post": pos, "delta": round(pos - pre, 4)}
        print("  %-8s M4d PRE-cleanup=%.4f | POST-cleanup=%.4f | delta %+.4f" % (nm, pre, pos, pos - pre), flush=True)
    print("  walk-edge endpoints removed in-memory (both dirs counted): %d" % n_removed, flush=True)
    return {"removed_edges": len(CLEANUP_REMOVED), "walk_endpoints_removed": n_removed,
            "q54q65": out["q54q65"], "h56d": out["56d"]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    dq = r["q54q65"]["delta"]; d56 = r["h56d"]["delta"]
    s = ("M4d post-cleanup F1 effect: q54-q65 %.4f->%.4f (%+.4f); 56d %.4f->%.4f (%+.4f). Removed the 10 DECISION 79/81 cleanup edges in-memory." % (
        r["q54q65"]["pre"], r["q54q65"]["post"], dq, r["h56d"]["pre"], r["h56d"]["post"], d56))
    if abs(dq) <= 0.01 and abs(d56) <= 0.01:
        return ("HARD_PASS", "Cycle-cleanup PRESERVES headline M4d retrieval F1 (|delta|<=0.01 on both held-out sets) -> Claim 14 (substrate self-corrects own graph) capability_preservation now confirmed at the RETRIEVAL-F1 level, not just axiom-termination. The 10 removed wrong-direction edges were NOT retrieval-load-bearing. " + s)
    return ("REVIEW", "Cycle-cleanup CHANGED M4d F1 by >0.01 on a held-out set -> a removed edge was retrieval-relevant; review which. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_82g_m4d_post_cleanup_f1_effect", flush=True)
    out_dir = get_output_dir("substrate_82g_m4d_post_cleanup_f1_effect_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_82g_m4d_post_cleanup_f1_effect_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
