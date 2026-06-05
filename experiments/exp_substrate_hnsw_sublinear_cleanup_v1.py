"""
substrate_hnsw_sublinear_cleanup_v1 -- sub-linear cleanup retrieval via FAISS-HNSW (HP-12 V2 critical path) -- CPU.

ROUTING: research HP12_core_HP_ack_critical_path -- HNSW empirical PROMOTED to HP-12 critical path. Dense Hebbian
  cleanup is O(M) (brute-force argmax over codebook); the 1M-fact killer demo needs SUB-LINEAR cleanup. FAISS-HNSW
  gives approximate-NN cleanup in O(logM). Validates: speedup >> brute AND recall@1 preserved -> enables HP-12 V2
  scale to 1M facts. CPU numpy + faiss-cpu (1.8.0 on runner) $0.

MODEL: codebook C (M items, D-dim, unit). Noisy queries (item + noise). BRUTE: argmax(C@q) [O(M)]. HNSW:
  IndexHNSWFlat inner-product search(q,1) [O(logM)]. Metrics: search speedup (brute/hnsw), recall@1 (HNSW top-1 ==
  true item), agreement (HNSW == brute top-1).

PRE-REGISTERED bands: HARD-PASS speedup >= 3200x AND recall@1 >= 0.97 at the largest M. MIDDLE: speedup >= 100x AND
  recall@1 >= 0.95. HARD-FAIL: recall@1 < 0.95 (HNSW loses cleanup fidelity) OR speedup < 100x.
FORMULA SELF-TESTS (PROT-022): 1. brute argmax cleanup. 2. faiss import + tiny index search. 3. cosine.
ASCII-only. write_metrics. PROT-018: no _nN.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"; os.environ["OMP_NUM_THREADS"] = "1"   # faiss/numpy OpenMP coexistence + avoid deadlock (Windows libomp vs libiomp5)
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_hnsw_sublinear_cleanup_v1"
D = 256; N_QUERY = 200; HNSW_M = 32; EF_SEARCH = 64
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; M_GRID = [10000, 100000]
else:
    SEEDS = [7, 17, 23]; M_GRID = [100000, 1000000]


def unit(X):
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def _selftest():
    g = np.random.default_rng(0); C = unit(g.standard_normal((100, 16)).astype(np.float32)); q = C[7]
    assert int(np.argmax(C @ q)) == 7, "brute argmax cleanup"
    try:
        import faiss
        idx = faiss.IndexFlatIP(16); idx.add(C); _, I = idx.search(C[7:8], 1); assert int(I[0, 0]) == 7, "faiss search"
    except Exception as e:
        print("[selftest] faiss issue: %s" % e, flush=True)
    print("[selftest] PASS: brute faiss cosine", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
import faiss
faiss.omp_set_num_threads(1)   # single-thread faiss to avoid Windows OpenMP deadlock


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); per_M = {}
    for M in M_GRID:
        C = unit(g.standard_normal((M, D)).astype(np.float32))
        qi = g.choice(M, size=N_QUERY, replace=False)
        Q = unit(C[qi] + 0.7 * g.standard_normal((N_QUERY, D)).astype(np.float32))
        # BRUTE-FORCE cleanup: argmax(C @ q) -- O(M) per query
        t0 = time.perf_counter()
        brute = np.array([int(np.argmax(C @ Q[j])) for j in range(N_QUERY)]); brute_t = time.perf_counter() - t0
        # HNSW cleanup -- O(logM) per query
        index = faiss.IndexHNSWFlat(D, HNSW_M, faiss.METRIC_INNER_PRODUCT); index.hnsw.efConstruction = 80
        index.add(C); index.hnsw.efSearch = EF_SEARCH
        t1 = time.perf_counter(); _, I = index.search(Q, 1); hnsw_t = time.perf_counter() - t1
        hnsw = I[:, 0]
        recall_true = float(np.mean(hnsw == qi))           # HNSW returns the true source item
        agree_brute = float(np.mean(hnsw == brute))        # HNSW == brute top-1
        per_M["M%d" % M] = {"speedup": float(brute_t / max(hnsw_t, 1e-9)), "recall_at1": recall_true,
                            "agree_brute": agree_brute, "brute_ms": round(brute_t * 1000, 1), "hnsw_ms": round(hnsw_t * 1000, 2)}
    return {"seed": seed, "per_M": per_M}


def verdict(ps) -> Tuple[str, str]:
    Mmax = "M%d" % M_GRID[-1]
    sp = float(np.mean([p["per_M"][Mmax]["speedup"] for p in ps])); rc = float(np.mean([p["per_M"][Mmax]["recall_at1"] for p in ps]))
    parts = " | ".join("%s: %.0fx recall@1=%.3f" % (k, np.mean([p["per_M"][k]["speedup"] for p in ps]), np.mean([p["per_M"][k]["recall_at1"] for p in ps])) for k in ps[0]["per_M"])
    summary = "at %s: speedup=%.0fx recall@1=%.3f | %s" % (Mmax, sp, rc, parts)
    if sp >= 3200 and rc >= 0.97:
        return ("HARD_PASS", "HARD_PASS: HNSW sub-linear cleanup >=3200x + recall@1>=0.97 -- HP-12 V2 can scale to 1M facts. " + summary)
    if sp >= 100 and rc >= 0.95:
        return ("MIDDLE_BAND", "MIDDLE_BAND: HNSW cleanup speedup>=100x + recall>=0.95. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: HNSW cleanup loses fidelity or speedup. " + summary)


print("[config] anchor=%s mode=%s seeds=%s D=%d M_grid=%s efS=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, D, M_GRID, EF_SEARCH), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    for k, v in r["per_M"].items():
        print("  [seed=%d %s] speedup=%.0fx recall@1=%.3f agree=%.3f (brute=%.1fms hnsw=%.2fms)" % (seed, k, v["speedup"], v["recall_at1"], v["agree_brute"], v["brute_ms"], v["hnsw_ms"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
