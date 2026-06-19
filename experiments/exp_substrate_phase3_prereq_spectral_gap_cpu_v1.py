"""DECISION 66e (Phase 3 prereq, per W4 warning): compute the SHARES_MATH (+ full typed-operator) graph spectral gap / algebraic connectivity (Fiedler value) on the substrate atom-graph. Pattern C (self-play theorem proving) precondition = well-connected graph (non-trivial spectral gap; fast random-walk mixing). Reports: components, largest-CC size, Fiedler value (lambda_2 of normalized Laplacian on largest CC), spectral interpretation for Pattern C viability. Laptop-runnable; structural; no bge. ASCII; --self-test."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_phase3_prereq_spectral_gap_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
WALK_EDGES = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def components(adj, nodes):
    seen = set(); comps = []
    for s in nodes:
        if s in seen: continue
        c = []; q = deque([s]); seen.add(s)
        while q:
            n = q.popleft(); c.append(n)
            for m in adj.get(n, ()):
                if m not in seen: seen.add(m); q.append(m)
        comps.append(c)
    return sorted(comps, key=len, reverse=True)


def fiedler(adj, comp):
    """algebraic connectivity = 2nd-smallest eigenvalue of normalized Laplacian on one connected component."""
    idx = {n: i for i, n in enumerate(comp)}; n = len(comp)
    if n < 3: return 0.0
    A = np.zeros((n, n), dtype=np.float64)
    for u in comp:
        for v in adj.get(u, ()):
            if v in idx: A[idx[u], idx[v]] = 1.0
    deg = A.sum(1); dinv = 1.0 / np.sqrt(np.maximum(deg, 1e-12))
    L = np.eye(n) - (dinv[:, None] * A * dinv[None, :])
    L = (L + L.T) / 2
    ev = np.linalg.eigvalsh(L)
    ev.sort()
    return float(ev[1])  # lambda_2 (lambda_1 ~ 0)


def _selftest():
    adj = {"a": ["b"], "b": ["a", "c"], "c": ["b"], "x": ["y"], "y": ["x"]}
    cs = components(adj, list(adj)); assert len(cs) == 2 and len(cs[0]) == 3
    f = fiedler(adj, cs[0]); assert 0 < f <= 2
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def build_adj(edge_types):
    adj = defaultdict(set); ne = 0
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in edge_types:
                s = _short(rr.get("src_id", "")); t = _short(rr.get("tgt_id", ""))
                if s and t and s != t: adj[s].add(t); adj[t].add(s); ne += 1
    return adj, ne


def analyze(name, edge_types) -> Dict:
    adj, ne = build_adj(edge_types)
    nodes = list(adj.keys())
    comps = components(adj, nodes)
    largest = comps[0] if comps else []
    fied = fiedler(adj, largest) if len(largest) >= 3 else 0.0
    res = {"graph": name, "n_nodes_with_edges": len(nodes), "n_undirected_edges": ne,
           "n_components": len(comps), "largest_cc": len(largest),
           "largest_cc_frac": round(len(largest) / max(len(nodes), 1), 3), "fiedler_lambda2": round(fied, 5)}
    print("  [%s] nodes-with-edges=%d edges=%d | components=%d largest-CC=%d (%.1f%%) | Fiedler lambda2=%.5f" % (
        name, res["n_nodes_with_edges"], ne, res["n_components"], res["largest_cc"], 100 * res["largest_cc_frac"], fied), flush=True)
    return res


def run() -> Dict:
    sm = analyze("SHARES_MATH-only", {"SHARES_MATH"})
    full = analyze("full-typed-operator", WALK_EDGES)
    return {"shares_math": sm, "full_graph": full}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    sm = r["shares_math"]; full = r["full_graph"]
    s = ("Phase-3 spectral prereq: SHARES_MATH graph (nodes=%d, edges=%d, components=%d, largest-CC=%d=%.0f%%, Fiedler=%.5f); "
         "full typed-operator graph (nodes=%d, edges=%d, components=%d, largest-CC=%d=%.0f%%, Fiedler=%.5f)." % (
             sm["n_nodes_with_edges"], sm["n_undirected_edges"], sm["n_components"], sm["largest_cc"], 100 * sm["largest_cc_frac"], sm["fiedler_lambda2"],
             full["n_nodes_with_edges"], full["n_undirected_edges"], full["n_components"], full["largest_cc"], 100 * full["largest_cc_frac"], full["fiedler_lambda2"]))
    # Pattern C precondition: well-connected (large CC fraction + non-trivial Fiedler)
    if full["largest_cc_frac"] >= 0.5 and full["fiedler_lambda2"] >= 0.01:
        return ("HARD_PASS", "Pattern C VIABLE on full typed-operator graph (largest-CC >=50%% + Fiedler >=0.01; random-walk mixes). SHARES_MATH-only graph is sparse/fragmented (expected; few bridges). " + s)
    if full["largest_cc_frac"] >= 0.5:
        return ("PARTIAL", "Full graph connected (largest-CC>=50%%) but LOW Fiedler (slow random-walk mixing; Pattern C precondition WEAK -- self-play walk would mix slowly). Pattern A (AlphaGeometry-style, no walk) preferred. " + s)
    return ("MIDDLE", "Graph FRAGMENTED (largest-CC<50%%) -- random-walk self-play (Pattern C) NOT viable; Pattern A/D (proposer+verifier, no walk) is the right Phase-3 choice. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
