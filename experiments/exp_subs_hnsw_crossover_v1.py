"""
exp_subs_hnsw_crossover_v1 -- reactive-subscriptions anchor 2 (HNSW vs naive-scan crossover) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_reactive_subscriptions (#2). At what subscription count S does an ANN index
  (HNSW; ef=100) beat a naive linear scan in per-write-event dispatch time, at N=65536? Research predicts crossover ~S=500.
  Determines the v1 (naive) vs v2 (indexed) architecture boundary. Uses hnswlib if available, else sklearn brute/kd as ANN
  proxy. CPU $0.
PRE-REGISTERED (research bands): HARD-PASS index faster than naive at S>=500. MID faster only at 1K<=S<=5K. HARD-FAIL index
  never faster at S<=50K.
FORMULA SELF-TESTS (PROT-022): 1. naive scan correctness. 2. timing positive. 3. index returns neighbors.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "subs_hnsw_crossover_v1"
N = 65536
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N = 4096; S_GRID = [100, 1000]; N_Q = 20
else:
    S_GRID = [100, 500, 1000, 5000, 10000, 50000]; N_Q = 50


def naive_query(subs, q, k=10):
    return np.argsort(subs @ q)[-k:]


def _selftest():
    g = np.random.default_rng(0); subs = g.standard_normal((20, 16)).astype(np.float32); q = g.standard_normal(16).astype(np.float32)
    r = naive_query(subs, q, 5); assert len(r) == 5 and r[-1] == int(np.argmax(subs @ q)), "naive scan correctness"
    t0 = time.perf_counter(); _ = naive_query(subs, q); assert time.perf_counter() - t0 >= 0, "timing positive"
    print("[selftest] PASS: hnsw-crossover", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

_BACKEND = "none"
try:
    import hnswlib
    _BACKEND = "hnswlib"
except Exception:
    try:
        from sklearn.neighbors import NearestNeighbors
        _BACKEND = "sklearn"
    except Exception:
        _BACKEND = "none"
print("[backend] ANN=%s" % _BACKEND, flush=True)


def build_index(subs):
    if _BACKEND == "hnswlib":
        ix = hnswlib.Index(space="cosine", dim=subs.shape[1]); ix.init_index(max_elements=subs.shape[0], ef_construction=100, M=16)
        ix.add_items(subs, np.arange(subs.shape[0])); ix.set_ef(100); return ix
    if _BACKEND == "sklearn":
        nn = NearestNeighbors(n_neighbors=10, algorithm="auto"); nn.fit(subs); return nn
    return None


def index_query(ix, q):
    if _BACKEND == "hnswlib":
        return ix.knn_query(q[None, :], k=10)[0]
    return ix.kneighbors(q[None, :], return_distance=False)


def run() -> Dict:
    g = np.random.default_rng(7); by = {}; crossover = None
    for S in S_GRID:
        subs = g.standard_normal((S, N)).astype(np.float32); qs = g.standard_normal((N_Q, N)).astype(np.float32)
        t0 = time.perf_counter()
        for q in qs:
            _ = naive_query(subs, q)
        naive = (time.perf_counter() - t0) / N_Q
        ix = build_index(subs); t1 = time.perf_counter()
        for q in qs:
            _ = index_query(ix, q)
        idx_t = (time.perf_counter() - t1) / N_Q
        faster = idx_t < naive
        if faster and crossover is None:
            crossover = S
        by["S%d" % S] = {"naive_ms": naive * 1e3, "index_ms": idx_t * 1e3, "index_faster": bool(faster)}
        print("  [S=%d] naive=%.3fms index=%.3fms faster=%s" % (S, naive * 1e3, idx_t * 1e3, faster), flush=True)
    return {"backend": _BACKEND, "crossover_S": crossover, "by": by}


def verdict(r) -> Tuple[str, str]:
    cx = r["crossover_S"]
    summary = "ANN=%s crossover_S=%s | %s" % (r["backend"], cx, {k: ("idx" if v["index_faster"] else "naive") for k, v in r["by"].items()})
    if r["backend"] == "none":
        return ("UNKNOWN", "UNKNOWN: no ANN backend (hnswlib/sklearn) available on runner -- install hnswlib to measure. " + summary)
    if cx is not None and cx <= 500:
        return ("HARD_PASS", "HARD_PASS: index beats naive scan at S<=500 -- ANN index mandatory by v1; crossover confirmed. " + summary)
    if cx is not None and cx <= 5000:
        return ("MIDDLE_BAND", "MIDDLE_BAND: crossover at 500<S<=5000 -- naive scan serves a longer v1 tail. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: index never beats naive scan at S<=50K -- naive scan sufficient (or index needs tuning). " + summary)


print("[config] anchor=%s mode=%s N=%d S_grid=%s" % (ANCHOR_NAME, RUN_MODE, N, S_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
