"""
exp_rank_k_woodbury_v1 -- #3: rank-k Woodbury low-rank inverse-update accuracy/throughput -- CPU.
ROUTING: cpu_backlog_high_priority_12 #3 rank-k-Woodbury. Approximate pinv via rank-k Woodbury update; sweep k; measure recall vs throughput vs full pinv. CPU.
PRE-REGISTERED: HARD-PASS a k giving acceptable accuracy AND >=2x throughput vs full pinv.
FORMULA SELF-TESTS (PROT-022): 1. pinv recovers. 2. quant ok. 3. sign keys.
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
ANCHOR_NAME = "rank_k_woodbury_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def sign_keys(M, n, g): return np.sign(g.standard_normal((M, n))).astype(np.float32)
def pinv_W(K, ridge=1e-3):
    W = (K.T @ np.linalg.solve(K @ K.T + ridge * np.eye(len(K)), K)).astype(np.float32); np.fill_diagonal(W, 0.0); return W
def recall(W, K, g, flip=0.05, it=8):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(it):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
def quant(W, bits):
    L = 2 ** bits - 1; lo, hi = np.quantile(W, 0.001), np.quantile(W, 0.999); Wc = np.clip(W, lo, hi)
    return (np.round((Wc - lo) / (hi - lo + 1e-12) * L) / L * (hi - lo) + lo).astype(np.float32)
def _selftest():
    g = np.random.default_rng(0); K = sign_keys(3, 64, g); W = pinv_W(K); assert recall(W, K, np.random.default_rng(1), flip=0.0) >= 0.9, "pinv recovers"
    assert quant(W, 4).shape == W.shape, "quant ok"
    assert set(np.unique(K)) <= {-1.0, 1.0}, "sign keys"
    print("[selftest] PASS: %s" % ANCHOR_NAME, flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); M = int(0.2 * N); K = sign_keys(M, N, g)
    t = time.perf_counter(); Wf = pinv_W(K); tf = time.perf_counter() - t; rf = recall(Wf, K, np.random.default_rng(1))
    by = {}
    for k in ([8, 32] if RUN_MODE=="smoke" else [8, 16, 32, 64]):
        t = time.perf_counter(); U, S, Vt = np.linalg.svd(K, full_matrices=False); Kk = (U[:, :k]*S[:k]) @ Vt[:k]; Wk = pinv_W(Kk.astype(np.float32)); tk = time.perf_counter() - t
        rk = recall(Wk, K, np.random.default_rng(1)); by["k%d" % k] = {"rec": rk, "speedup": tf/max(tk,1e-6)}
        print("  k=%d recall=%.3f speedup=%.2fx (full recall=%.3f)" % (k, rk, tf/max(tk,1e-6), rf), flush=True)
    return {"by": by, "full": rf}
def verdict(r) -> Tuple[str, str]:
    s = "full=%.3f by k: %s" % (r["full"], {k: {"r": round(v["rec"],3), "x": round(v["speedup"],2)} for k,v in r["by"].items()})
    ok = any(v["rec"] >= r["full"] - 0.05 and v["speedup"] >= 2.0 for v in r["by"].values())
    if ok: return ("HARD_PASS", "HARD_PASS: a rank-k Woodbury gives accuracy within 5pct of full pinv at >=2x throughput. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: no k hits both accuracy + 2x speedup. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
