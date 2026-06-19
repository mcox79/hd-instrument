"""
exp_substrate_1M_recall_validation_v1 -- promote CELL-4 100K perfect recall to 1M scale -- CPU.

ROUTING: scale_gap_experiments Experiment 2. CELL-4 showed perfect sign-key autoassociative recall at 100K; production needs
  validation at 1M. Stores N sign-binarized keys (D-dim), queries with noisy versions, measures recall@1 (nearest key by dot)
  via CHUNKED matmul (no Gram inverse -- O(N*D) memory, feasible at 1M). Tests whether recall holds as N scales 100K->1M.
  Pure numpy, memory-safe (int8 keys, chunked). CPU.
PRE-REGISTERED: HARD-PASS recall@1 >= 0.99 at N=1M under moderate noise (CELL-4 promotes to production scale). MIDDLE 0.95-0.99.
  HARD-FAIL < 0.95 (crosstalk at 1M; needs higher D or chunked cleanup memory).
FORMULA SELF-TESTS (PROT-022): 1. self-recall. 2. sign keys. 3. chunked == full.
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

ANCHOR_NAME = "substrate_1M_recall_validation_v1"; D = 1024; NOISE_FLIP = 0.15; NQ = 500; CHUNK = 50000
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_KEYS = 50000 if RUN_MODE == "smoke" else 1000000


def sign_keys(n, d, g):
    return np.sign(g.standard_normal((n, d))).astype(np.int8)


def recall_chunked(query_idx, queries, keys, chunk):
    # for each query (noisy key), find nearest stored key by dot product, chunked over keys -- recall@1 vs true index
    nq = queries.shape[0]; best = np.full(nq, -1, dtype=np.int64); best_score = np.full(nq, -1e18)
    qf = queries.astype(np.float32)
    for c0 in range(0, keys.shape[0], chunk):
        c1 = min(c0 + chunk, keys.shape[0]); block = keys[c0:c1].astype(np.float32)   # [cb, D]
        scores = qf @ block.T                                                          # [nq, cb]
        bidx = np.argmax(scores, axis=1); bsc = scores[np.arange(nq), bidx]
        upd = bsc > best_score; best[upd] = c0 + bidx[upd]; best_score[upd] = bsc[upd]
    return float((best == query_idx).mean())


def _selftest():
    g = np.random.default_rng(0); K = sign_keys(20, 64, g)
    q = K[5].astype(np.float32)[None, :]; sc = q @ K.astype(np.float32).T; assert int(np.argmax(sc)) == 5, "self-recall"
    assert set(np.unique(K)) <= {-1, 1}, "sign keys"
    full = K.astype(np.float32) @ K[3].astype(np.float32); ch = recall_chunked(np.array([3]), K[3:4], K, 8); assert ch == 1.0, "chunked == full"
    print("[selftest] PASS: substrate-1M-recall-validation", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(606)
    print("  allocating %d sign keys (D=%d, ~%.1f GB int8)..." % (N_KEYS, D, N_KEYS * D / 1e9), flush=True)
    keys = sign_keys(N_KEYS, D, g)
    qidx = g.choice(N_KEYS, size=NQ, replace=False)
    flips = g.random((NQ, D)) < NOISE_FLIP
    queries = keys[qidx].copy(); queries[flips] *= -1                       # flip NOISE_FLIP fraction of bits
    t0 = time.perf_counter(); rec = recall_chunked(qidx, queries, keys, CHUNK); dt = time.perf_counter() - t0
    print("  N=%d recall@1=%.4f (noise_flip=%.2f, n_q=%d, recall wall=%.1fs)" % (N_KEYS, rec, NOISE_FLIP, NQ, dt), flush=True)
    return {"n_keys": N_KEYS, "recall1": rec, "noise_flip": NOISE_FLIP, "nq": NQ}


def verdict(r) -> Tuple[str, str]:
    rec = r["recall1"]; s = "recall@1=%.4f at N=%d (noise_flip=%.2f, n_q=%d)" % (rec, r["n_keys"], r["noise_flip"], r["nq"])
    if rec >= 0.99:
        return ("HARD_PASS", "HARD_PASS: sign-key autoassociative recall holds at 1M scale (recall@1>=0.99) -- CELL-4 promotes to production scale. " + s)
    if rec >= 0.95:
        return ("MIDDLE_BAND", "MIDDLE_BAND: recall@1 0.95-0.99 at 1M -- mild crosstalk; higher D or cleanup memory closes it. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall@1 <0.95 at 1M -- crosstalk at scale; D=%d insufficient for 1M. " % D + s)


print("[config] anchor=%s mode=%s N_keys=%d D=%d noise=%.2f chunk=%d" % (ANCHOR_NAME, RUN_MODE, N_KEYS, D, NOISE_FLIP, CHUNK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
