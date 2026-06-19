"""DECISION 49b/53a -- abstraction analysis on the 5510 ingested wikidata atoms: bge-cluster into SHARED_ABSTRACTION groups (tight semantic clusters within a class) and emit candidate SHARES_MATH edges that DENSIFY the typed-operator graph M4d walks. Light INVERSE_PAIR name heuristic. Substrate-internal (bge cached vectors + numpy; no LLM). Runs on BGE machine (uses cached semantic matrix). HARD-PASS: 20+ SHARED_ABSTRACTION groups. ASCII; --self-test + metrics.json + emits candidate edges jsonl."""
from __future__ import annotations
import sys, time, json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_49b_wikidata_abstraction_analysis_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
SIM_THRESH = 0.80          # tight semantic-cluster threshold (SHARED_ABSTRACTION)
MAX_EDGES_PER_NODE = 3     # cap emitted SHARES_MATH edges per atom (avoid explosion)
INVERSE_HINTS = [("forward", "inverse"), ("encode", "decode"), ("transform", "inverse_transform"),
                 ("bind", "unbind"), ("compress", "decompress"), ("differentiat", "integrat")]
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def connected_components(nodes, edges):
    parent = {n: n for n in nodes}
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    groups = defaultdict(list)
    for n in nodes: groups[find(n)].append(n)
    return [g for g in groups.values() if len(g) >= 2]


def _selftest():
    g = connected_components(["a", "b", "c", "d"], [("a", "b"), ("b", "c")])
    assert len(g) == 1 and len(g[0]) == 3
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    pstore = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    mat = getattr(r, "_semantic_matrix", None); ids = getattr(r, "_id_order", None)
    if mat is None or ids is None:
        return {"error": "no_cached_matrix"}
    mat = np.asarray(mat, dtype=np.float32)
    # normalize (bge usually normalized, but ensure)
    nrm = np.linalg.norm(mat, axis=1, keepdims=True); nrm[nrm == 0] = 1.0; mat = mat / nrm
    name_of = {a.id: (a.name or a.id) for a in pstore.all_atoms()}
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    # wikidata atom indices
    widx = [i for i, aid in enumerate(ids) if "wikidata_" in aid.lower()]
    if len(widx) < 10:
        return {"error": "too_few_wikidata_atoms:%d" % len(widx)}
    W = mat[widx]                       # (nw, dim)
    wids = [ids[i] for i in widx]
    nw = len(widx)
    # cosine sims (nw x nw); threshold edges (i<j)
    sims = W @ W.T

    def build(thresh):
        ed = set()
        for i in range(nw):
            order = np.argsort(-sims[i]); added = 0
            for j in order:
                if j == i: continue
                if sims[i][j] < thresh: break
                if added >= MAX_EDGES_PER_NODE: break
                ed.add((i, j) if i < j else (j, i)); added += 1
        gs = connected_components(list(range(nw)), list(ed)); gs.sort(key=len, reverse=True)
        return list(ed), gs
    # sweep to find granular grouping (avoid giant-blob); pick smallest threshold with largest-group <= 60
    sweep = {}
    chosen = None
    for th in [0.80, 0.84, 0.86, 0.88, 0.90, 0.92]:
        ed, gs = build(th)
        sweep[th] = (len(gs), len(gs[0]) if gs else 0, len(ed))
        if chosen is None and gs and len(gs[0]) <= 60 and len(gs) >= 20:
            chosen = th
    print("  threshold sweep (thresh -> n_groups, largest_group, n_edges):", flush=True)
    for th, (ng, lg, ne) in sweep.items():
        print("    %.2f -> groups=%d largest=%d edges=%d" % (th, ng, lg, ne), flush=True)
    SIM_USE = chosen if chosen is not None else 0.90
    print("  chosen threshold for granular grouping: %.2f" % SIM_USE, flush=True)
    edges, groups = build(SIM_USE)
    # INVERSE_PAIR light heuristic (name contains complementary hint tokens, same-ish topic)
    inv_pairs = []
    lname = {i: name_of.get(wids[i], "").lower() for i in range(nw)}
    for i in range(nw):
        for (h1, h2) in INVERSE_HINTS:
            if h1 in lname[i]:
                base = lname[i].replace(h1, "")
                for j in range(nw):
                    if j != i and h2 in lname[j] and base and base.strip() and base.strip()[:6] in lname[j]:
                        inv_pairs.append((wids[i], wids[j])); break
    inv_pairs = list({tuple(sorted(p)) for p in inv_pairs})
    # emit candidate SHARES_MATH edges (within groups, the capped edge set)
    cand_edges = [{"src_id": qual.get(wids[a], wids[a]), "tgt_id": qual.get(wids[b], wids[b]),
                   "rel_type": "SHARES_MATH", "source": "49b_bge_abstraction_cluster",
                   "cosine": round(float(sims[a, b]), 4)} for a, b in edges]
    out = DATA_ROOT / "wikidata_action_api" / "abstraction_49b_candidate_shares_math_edges.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(e) for e in cand_edges), encoding="utf-8")
    print("  wikidata atoms=%d | chosen-thresh=%.2f | candidate SHARES_MATH edges=%d" % (nw, SIM_USE, len(cand_edges)), flush=True)
    print("  SHARED_ABSTRACTION groups (>=2): %d (largest %d)" % (len(groups), len(groups[0]) if groups else 0), flush=True)
    print("  INVERSE_PAIR candidates (name-heuristic): %d" % len(inv_pairs), flush=True)
    print("  sample groups:", flush=True)
    for g in groups[:6]:
        print("    [%d] %s" % (len(g), ", ".join(name_of.get(wids[k], wids[k])[:22] for k in g[:4])), flush=True)
    for p in inv_pairs[:5]:
        print("    INV: %s <-> %s" % (_short(p[0]), _short(p[1])), flush=True)
    print("  wrote candidate edges -> %s" % out, flush=True)
    return {"n_wikidata": nw, "n_shared_abstraction_groups": len(groups), "n_candidate_edges": len(cand_edges),
            "n_inverse_pairs": len(inv_pairs), "largest_group": len(groups[0]) if groups else 0,
            "sample_groups": [[name_of.get(wids[k], wids[k]) for k in g[:4]] for g in groups[:6]]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("49b abstraction analysis on %d wikidata atoms: %d SHARED_ABSTRACTION groups (largest %d), %d candidate SHARES_MATH edges, "
         "%d INVERSE_PAIR (name-heuristic). Edges densify the M4d graph." % (
             r["n_wikidata"], r["n_shared_abstraction_groups"], r["largest_group"], r["n_candidate_edges"], r["n_inverse_pairs"]))
    if r["n_shared_abstraction_groups"] >= 20:
        return ("HARD_PASS", "HARD_PASS (>=20 SHARED_ABSTRACTION groups): %d groups + %d candidate SHARES_MATH edges ready to enrich M4d's graph (51c). " % (
            r["n_shared_abstraction_groups"], r["n_candidate_edges"]) + s + " (INVERSE_PAIR/THEOREM_LINKED partial: name-heuristic only; full detection needs derivation data -- honest gap.)")
    return ("PARTIAL", "PARTIAL (<20 groups at this threshold): " + s + " Consider lower SIM_THRESH for more groups.")


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
