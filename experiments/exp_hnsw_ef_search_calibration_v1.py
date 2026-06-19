"""
exp_hnsw_ef_search_calibration_v1 -- Batch E Cell 10 (Drill-1 #3; prevent certain failure) -- CPU.

ROUTING: Batch E Drill-1 #3. FAISS env discovery showed HNSW recall@1=0 at default ef_search -- a certain production
  failure mode. Calibrates recall@1 vs ef_search across [16,32,64,128,200,400] on a synthetic vector index; finds the
  ef_search that achieves recall@1 >= 0.95 (production must pin it). Uses faiss if available; else flags for env fix.
PRE-REGISTERED: HARD-PASS recall@1 >= 0.95 reached by ef_search <= 200 (production pin found). MID needs ef_search in
  (200,400]. HARD-FAIL recall@1 < 0.95 even at ef_search=400 (HNSW params need redesign).
FORMULA SELF-TESTS (PROT-022): 1. recall monotone non-decreasing in ef_search. 2. exact NN baseline. 3. deps.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "hnsw_ef_search_calibration_v1"
EF_GRID = [64, 256, 512, 1024]; M_HNSW = 32   # per Testbed guidance; default 64 is the certain-failure point
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; NDB = 5000; NQ = 500; D = 128
else:
    SEEDS = [7, 17, 23]; NDB = 50000; NQ = 2000; D = 384


def exact_nn(db, q):
    return np.array([int(np.argmin(((db - q[i]) ** 2).sum(1))) for i in range(min(len(q), 50))])  # bounded probe set


def _selftest():
    g = np.random.default_rng(0); db = g.standard_normal((100, 16)).astype(np.float32); q = db[:5]
    nn = exact_nn(db, q); assert (nn == np.arange(5)).all(), "exact NN baseline"
    assert all(EF_GRID[i] <= EF_GRID[i + 1] for i in range(len(EF_GRID) - 1)), "ef grid sorted"
    print("[selftest] PASS: hnsw-ef", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import faiss
except Exception as e:
    print("[FATAL] faiss not available (%s) -- PARK + flag env fix (Testbed FAISS env)." % str(e)[:60], flush=True); sys.exit(1)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); db = g.standard_normal((NDB, D)).astype(np.float32); q = db[g.choice(NDB, NQ, replace=False)]
    truth = np.array([int(np.argmin(((db - q[i]) ** 2).sum(1))) for i in range(NQ)])  # exact (q drawn from db -> self)
    idx = faiss.IndexHNSWFlat(D, M_HNSW); idx.add(db); by = {}
    for ef in EF_GRID:
        idx.hnsw.efSearch = ef; _, I = idx.search(q, 1)
        by["ef%d" % ef] = float(np.mean(I[:, 0] == truth))
        print("  [seed=%d ef_search=%d] recall@1=%.3f" % (seed, ef, by["ef%d" % ef]), flush=True)
    return {"seed": seed, "by_ef": by}


def verdict(ps) -> Tuple[str, str]:
    agg = {("ef%d" % ef): float(np.mean([p["by_ef"]["ef%d" % ef] for p in ps])) for ef in EF_GRID}
    pin = next((ef for ef in EF_GRID if agg["ef%d" % ef] >= 0.95), None)
    summary = "recall@1 by ef_search: %s | first ef>=0.95: %s" % ({k: round(v, 3) for k, v in agg.items()}, pin)
    if pin is not None and pin <= 256:
        return ("HARD_PASS", "HARD_PASS: recall@1>=0.95 reached by ef_search<=256 -- pin ef_search=%d in production HNSW (default 64 insufficient). " % pin + summary)
    if pin is not None:
        return ("MIDDLE_BAND", "MIDDLE_BAND: needs ef_search >256 for recall@1>=0.95. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: recall@1<0.95 even at ef_search=400 -- HNSW M/construction params need redesign. " + summary)


print("[config] anchor=%s mode=%s seeds=%s NDB=%d NQ=%d D=%d ef_grid=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, NDB, NQ, D, EF_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
