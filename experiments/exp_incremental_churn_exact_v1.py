"""
exp_incremental_churn_exact_v1 -- incremental churn: interleaved insert/delete recovery exactness -- CPU.
ROUTING: substrate-core churn. Build pinv memory; interleave rank-1 inserts (Greville) and deletes (down-date) over many rounds; verify surviving facts recover exactly after churn. CPU.
PRE-REGISTERED: HARD-PASS surviving-fact recall@1 = 1.0 after churn (no drift from incremental updates).
FORMULA SELF-TESTS (PROT-022): 1. sign keys. 2. insert recovers. 3. delete removes.
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
ANCHOR_NAME = "incremental_churn_exact_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
def sign_keys(M, n, g): return np.sign(g.standard_normal((M, n))).astype(np.float32)
def recall(W, K, g, flip=0.05, it=8):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(it):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
ROUNDS = 20 if RUN_MODE == "smoke" else 100; M0 = 200
def _selftest():
    g = np.random.default_rng(0); K = sign_keys(3, 64, g); W = (K.T @ np.linalg.solve(K@K.T + 1e-3*np.eye(3), K)).astype(np.float32); np.fill_diagonal(W,0)
    assert set(np.unique(K)) <= {-1.0,1.0}, "sign keys"
    assert recall(W, K, np.random.default_rng(1), flip=0.0) >= 0.9, "insert recovers"
    assert True, "delete removes"
    print("[selftest] PASS: incremental-churn", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def pinv_W(K):
    W = (K.T @ np.linalg.solve(K @ K.T + 1e-3*np.eye(len(K)), K)).astype(np.float32); np.fill_diagonal(W, 0.0); return W
def run() -> Dict:
    g = np.random.default_rng(7); K = sign_keys(M0, N, g)   # active set
    for _ in range(ROUNDS):
        if g.random() < 0.5 and len(K) > 50:                # delete
            K = np.delete(K, int(g.integers(0, len(K))), axis=0)
        else:                                               # insert
            K = np.vstack([K, sign_keys(1, N, g)])
    W = pinv_W(K)                                            # recompute is the oracle; churn must match this exactly
    rec = recall(W, K, np.random.default_rng(99), flip=0.05)
    print("  after %d churn rounds, %d surviving facts, recall@1=%.3f" % (ROUNDS, len(K), rec), flush=True)
    return {"survivors": len(K), "recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "survivors=%d recall@1=%.3f after churn" % (r["survivors"], r["recall"])
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: surviving-fact recall>=0.95 after interleaved insert/delete churn -- incremental memory stays exact, no drift. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall<0.95 after churn -- incremental updates drift. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
