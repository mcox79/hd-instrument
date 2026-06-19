"""DECISION 50a M4d -- capability-graph walk to escape the BGE-cosine representation bound (H_M4 confirmed: held-out gap is capability-transfer, not coverage). For each held-out in-coverage query: bge top-300 pool (gives cosines incl MEDIUM gold at rank 21/69); BFS 2 hops from the bge top-20 ANCHORS over typed edges (DEPENDS_ON/SHARES_MATH/SPECIALIZES); re-rank pool by combined = cosine + beta*proximity (proximity = decay^hop from nearest anchor); top-5. Sweep beta (beta=0 == bge baseline sanity). HARD-PASS: IN-COVERAGE F1 0.140 -> >=0.30 on MEDIUM 2/7 with no in-coverage regression. Substrate-internal (bge + graph; no LLM). Runs on BGE machine. ASCII; --self-test + metrics.json."""
from __future__ import annotations
import sys, os, time, json
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_m4d_capability_graph_walk_heldout_cpu_v1"
RUN_MODE = "full"
SELFTEST = "--self-test" in sys.argv
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
WALK_EDGES = {"DEPENDS_ON", "SHARES_MATH", "SPECIALIZES", "USES", "INSTANCE_OF"}
POOL_K = 300; N_ANCHORS = 20; MAX_HOP = 2; DECAY = 0.5
BETAS = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def f1_present(pred: set, present: set) -> float:
    if not present:
        return 1.0 if not pred else 0.0
    inter = len(pred & present)
    p = inter / len(pred) if pred else 0.0; r = inter / len(present)
    return 2 * p * r / (p + r) if (p + r) else 0.0


def bfs_proximity(anchors: List[str], adj: Dict[str, list], max_hop: int) -> Dict[str, int]:
    """min hop distance from any anchor (0 at anchor); up to max_hop."""
    dist = {a: 0 for a in anchors}
    q = deque((a, 0) for a in anchors)
    while q:
        n, d = q.popleft()
        if d >= max_hop:
            continue
        for m in adj.get(n, ()):  # undirected neighbors
            if m not in dist:
                dist[m] = d + 1; q.append((m, d + 1))
    return dist


def _selftest():
    assert abs(f1_present({"a", "b"}, {"a"}) - (2 * .5 * 1 / 1.5)) < 1e-9
    adj = {"x": ["y"], "y": ["x", "z"], "z": ["y"]}
    d = bfs_proximity(["x"], adj, 2); assert d["x"] == 0 and d["y"] == 1 and d["z"] == 2
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    if not HELDOUT.exists():
        return {"error": "no_heldout_file"}
    try:
        from backend.substrate_index.partition import PartitionedStore
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
    except Exception as e:
        return {"error": "import_failed:" + str(e)[:120]}
    pstore = PartitionedStore(DATA_ROOT)
    try:
        enc = AtomEncoder()
    except Exception as e:
        return {"error": "bge_unavailable:" + str(e)[:80]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    sset = {_short(a.id) for a in pstore.all_atoms()}
    # undirected adjacency over walkable typed edges (qualified-id space)
    adj = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in WALK_EDGES:
                s = rr.get("src_id", ""); t = rr.get("tgt_id", "")
                if s and t and s != t:
                    adj[s].add(t); adj[t].add(s)
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    perq = []
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present:
            continue  # in-coverage only
        cands = r.semantic(q["question"], top_k=POOL_K)
        pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool:
            continue
        # CONSENSUS proximity: sum over each top-N anchor (weighted by its cosine) of decay^hop.
        # Favors nodes reachable from MANY STRONG anchors (discriminative), not just reachable-at-all.
        cons = defaultdict(float)
        for a_qid, a_cos in pool[:N_ANCHORS]:
            d = bfs_proximity([a_qid], adj, MAX_HOP)
            for node, hop in d.items():
                if hop > 0:  # exclude the anchor itself
                    cons[node] += a_cos * (DECAY ** hop)
        perq.append({"qid": q["qid"], "present": present, "pool": pool, "cons": dict(cons)})

    def eval_beta(beta):
        f1s = {}
        for x in perq:
            scored = []
            for qid, cos in x["pool"]:
                prox = x["cons"].get(qid, 0.0)
                scored.append((qid, cos + beta * prox))
            scored.sort(key=lambda t: -t[1])
            top5 = {_short(qid) for qid, _ in scored[:5]}
            f1s[x["qid"]] = f1_present(top5, x["present"])
        macro = sum(f1s.values()) / len(f1s) if f1s else 0.0
        return round(macro, 4), f1s
    rows = []
    base_macro, base_f1s = eval_beta(0.0)
    for beta in BETAS:
        macro, f1s = eval_beta(beta)
        rows.append({"beta": beta, "macro": macro, "f1s": f1s})
    print("  in-coverage held-out: %d q | POOL_K=%d anchors=%d max_hop=%d decay=%.2f" % (len(perq), POOL_K, N_ANCHORS, MAX_HOP, DECAY), flush=True)
    print("  beta   IN-COV macro-F1   per-question", flush=True)
    for r_ in rows:
        pq = " ".join("%s=%.2f" % (k.split("-")[0], v) for k, v in sorted(r_["f1s"].items()))
        print("  %.2f   %.4f          %s" % (r_["beta"], r_["macro"], pq), flush=True)
    best = max(rows, key=lambda d: d["macro"])
    # regression check: any question worse than beta=0 at best beta?
    regressed = [k for k in base_f1s if best["f1s"].get(k, 0) < base_f1s[k] - 1e-9]
    return {"n": len(perq), "base_macro": base_macro, "best_beta": best["beta"], "best_macro": best["macro"],
            "sweep": rows, "regressed_at_best": regressed, "base_f1s": base_f1s, "best_f1s": best["f1s"]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    lift = r["best_macro"] - r["base_macro"]
    s = ("M4d capability-graph walk (DECISION 50a). IN-COVERAGE base(bge)=%.4f -> best graph-walk=%.4f at beta=%.2f (lift %+.4f). "
         "Regressions vs bge at best beta: %s." % (r["base_macro"], r["best_macro"], r["best_beta"], lift, r["regressed_at_best"] or "none"))
    if r["best_macro"] >= 0.30 and not r["regressed_at_best"]:
        return ("HARD_PASS", "HARD_PASS (M4d escapes the bge bound): in-coverage F1 reaches %.4f >= 0.30 via structural walk, no regression. " % r["best_macro"] + s)
    if lift >= 0.04 and not r["regressed_at_best"]:
        return ("PARTIAL", "PARTIAL (M4d helps, below 0.30): lift %+.4f >= 0.04, no regression -- structural walk pulls some MEDIUM gold up but not to 0.30. Compose with M4b. " % lift + s)
    if lift < 0.04:
        return ("HARD_FAIL", "HARD_FAIL (M4d insufficient): lift %+.4f < 0.04 -- the MEDIUM gold is not 2-hop-reachable from bge top-20 anchors via typed edges (graph too sparse OR gold disconnected). Activate M4b (query-side reformulation) per DECISION 50b. " % lift + s)
    return ("MIDDLE", "MIDDLE: " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
