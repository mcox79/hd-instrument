"""
exp_substrate_es1_es2_bge_primitive_proxy_cached_core_cpu_v1.py -- E-S1/E-S2 PROXY on the cached BGE structured core: is the BGE retrieval primitive healthy, and does type/domain routing lift recall? -- CPU/local (no heat), READ-ONLY.

ROUTING: Research F1 AMENDMENT tests E-S1 (self-recognition recall@10) + E-S2 (routed vs flat). Both LITERAL forms need BGE to encode the
  QUERY (atom description / query text), and sentence_transformers is NOT installed locally (this is exactly why the scorer ran
  cpu_only_no_bge_degraded -> 0.0067). So the full E-S1/E-S2 over canonical 20820 must run where BGE is installed (queued separately). This
  cell runs a LEGITIMATE LOCAL PROXY using the CACHED BGE index (data/substrate_index/cached_indices/bge_large_v2_name_1782_*.npz, 1782 atoms,
  precomputed BGE `semantic` vectors): for each duplicate/equivalence pair present in the cache, use one member's cached BGE vector as the query
  and ask whether the equivalent member is in top-10 (flat) vs within-domain-partition (routed). This tests the BGE RETRIEVAL PRIMITIVE health
  (the H1 question) without encoding new queries. NOT the literal description-query E-S1; an honest BGE-layer analog of E-S3.

PRE-REGISTERED: report flat top-10 recall + routed top-10 recall of the equivalent over the cached pairs.
  E-S1-proxy HEALTHY iff flat recall >= 0.60 (BGE primitive retrieves equivalents -> 0.0067 is a scorer-shard artifact, not a primitive defect);
    <0.30 = BGE primitive itself degraded on the core (more serious, R3).
  E-S2-proxy ROUTING-LIFT iff routed recall >= flat recall (+epsilon) -> domain/type routing helps (CELL SC transfers); routed << flat = routing
    not honored. Combined HARD_PASS iff E-S1-proxy HEALTHY (>=0.60) AND routed >= flat - 0.05. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_es1_es2_bge_primitive_proxy_cached_core_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
TOPK = 10
CACHE_GLOB = "cached_indices/bge_large_v2_name_*.npz"


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def recall_topk(qvec: np.ndarray, mat: np.ndarray, ids: List[str], self_i: int, targets: set, k: int, allowed: set = None) -> bool:
    sims = mat @ qvec
    sims[self_i] = -1e9
    if allowed is not None:
        mask = np.ones(len(ids), dtype=bool)
        for j in range(len(ids)):
            if ids[j] not in allowed:
                mask[j] = False
        sims = np.where(mask, sims, -1e9)
    order = np.argsort(-sims)[:k]
    return any(ids[j] in targets for j in order)


def _selftest():
    m = np.eye(5, dtype=np.float64); ids = ["T3/x", "T2/x", "T1/y", "T2/z", "T3/w"]
    m[1] = 0.9 * m[0] + 0.1 * m[2]; m[1] /= np.linalg.norm(m[1])    # T2/x near T3/x
    assert recall_topk(m[0].copy(), m, ids, 0, {"T2/x"}, 3)         # equivalent retrievable
    assert not recall_topk(m[4].copy(), m, ids, 4, {"T1/y"}, 1)     # T3/w's top-1 is not T1/y (orthogonal)
    print("[selftest] PASS: substrate_es1_es2_bge_primitive_proxy_cached_core_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    caches = sorted(root.glob(CACHE_GLOB))
    if not caches:
        return {"error": "no_bge_cache"}
    cache = caches[-1]
    d = np.load(cache, allow_pickle=True)
    ids = json.loads(str(d["id_order_json"]))
    mat = np.asarray(d["semantic"], dtype=np.float64)
    mat = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12)
    n = len(ids)
    # domain per cached id (join with live atoms) for routing
    dom_of = {}
    try:
        from backend.substrate_index.partition import PartitionedStore
        live = {str(a.id): (getattr(a, "algebra", None) or {}).get("domain") for a in PartitionedStore(root).all_atoms()}
        for i in ids:
            dom_of[i] = live.get(i) or "unknown"
    except Exception:
        for i in ids:
            dom_of[i] = "unknown"
    # equivalence pairs: same short-name appearing >=2x in cache
    by = defaultdict(list)
    for i, aid in enumerate(ids):
        by[_short(aid)].append(i)
    groups = {k: v for k, v in by.items() if len(v) >= 2}
    if not groups:
        return {"error": "no_pairs_in_cache", "cache": cache.name}
    # domain partitions for routing
    dom_members = defaultdict(set)
    for aid in ids:
        dom_members[dom_of[aid]].add(aid)
    flat_hits = 0; routed_hits = 0; nq = 0; rows = []
    for sname, idxs in groups.items():
        idset = set(ids[i] for i in idxs)
        for i in idxs:
            targets = idset - {ids[i]}
            allowed = dom_members.get(dom_of[ids[i]])
            fh = recall_topk(mat[i].copy(), mat, ids, i, targets, TOPK, None)
            rh = recall_topk(mat[i].copy(), mat, ids, i, targets, TOPK, allowed)
            flat_hits += int(fh); routed_hits += int(rh); nq += 1
            rows.append({"name": sname, "src": ids[i], "flat": fh, "routed": rh, "domain": dom_of[ids[i]]})
    flat_recall = round(flat_hits / nq, 4); routed_recall = round(routed_hits / nq, 4)
    print("  cache=%s | %d atoms | equivalence pairs=%d (queries=%d)" % (cache.name, n, len(groups), nq), flush=True)
    print("  E-S1-proxy (BGE primitive): flat top-10 recall of equivalent = %.4f" % flat_recall, flush=True)
    print("  E-S2-proxy (domain routing): routed top-10 recall = %.4f (lift vs flat = %+.4f)" % (routed_recall, routed_recall - flat_recall), flush=True)
    misses = [r for r in rows if not r["flat"]][:6]
    for m in misses:
        print("    flat-MISS %-26s src=%s dom=%s" % (m["name"], m["src"], m["domain"]), flush=True)
    return {"cache": cache.name, "n_cached": n, "n_pairs": len(groups), "n_queries": nq,
            "flat_recall": flat_recall, "routed_recall": routed_recall, "routing_lift": round(routed_recall - flat_recall, 4),
            "sample_flat_misses": misses}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("cache", "")))
    fr = r["flat_recall"]; rr = r["routed_recall"]
    s = ("E-S1/E-S2 PROXY on cached BGE structured core (%s, %d atoms, %d equivalence pairs, %d queries). E-S1-proxy flat top-10 recall of "
         "equivalent=%.4f (BGE primitive health). E-S2-proxy routed (domain-partition) top-10 recall=%.4f (lift %+.4f). NOTE: this is the "
         "BGE-layer analog of E-S3 using PRECOMPUTED cached vectors (no query encoding); the LITERAL description-query E-S1 + full-corpus E-S2 "
         "need sentence_transformers installed (NOT local) and are queued for a BGE-enabled machine. Pre-reg: flat>=0.60 healthy (0.0067 is a "
         "scorer-shard artifact), <0.30 serious; routed>=flat means routing helps.") % (
        r["cache"], r["n_cached"], r["n_pairs"], r["n_queries"], fr, rr, r["routing_lift"])
    healthy = fr >= 0.60; routing_ok = rr >= fr - 0.05
    if fr < 0.30:
        return ("HARD_FAIL", "HARD_FAIL (R3, more serious than 0.0067): BGE primitive flat recall=%.4f<0.30 -- even the cached BGE vectors do not "
                "retrieve known equivalents; the embedding/retrieval primitive itself is degraded on the structured core. " % fr + s)
    if healthy and routing_ok:
        return ("HARD_PASS", "HARD_PASS (BGE retrieval primitive HEALTHY on the core; H1 supported at the BGE layer): flat top-10 recall=%.4f>=0.60 "
                "-- the BGE primitive DOES retrieve equivalents, so 0.0067 is a scorer-shard/bge-off artifact (1746/20820 + bge off), not a primitive "
                "defect. Routing recall=%.4f (lift %+.4f). Confirms E-S3 (algebra layer) at the BGE layer: both retrieval primitives are healthy. " % (
                    fr, rr, r["routing_lift"]) + s)
    if healthy:
        return ("MIDDLE_BAND", "MIDDLE_BAND: BGE primitive healthy (flat recall=%.4f>=0.60) but domain-routing did NOT help (routed=%.4f < flat-0.05) "
                "-- routing not a lever at this scale/partitioning, or domain partitions too coarse. " % (fr, rr) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: BGE flat recall=%.4f in [0.30,0.60) -- partial primitive health on the core; not clearly a pure scorer "
            "artifact. " % fr + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
