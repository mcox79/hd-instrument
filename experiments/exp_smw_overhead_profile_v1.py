"""
exp_smw_overhead_profile_v1 -- #1: SMW rank-1 update phase timing -- CPU.
ROUTING: cpu_backlog_high_priority_12 #1 SMW-profile. Time the phases of a rank-1 Sherman-Morrison-Woodbury pinv update at production N; identify the dominant phase. CPU.
PRE-REGISTERED: HARD-PASS identify a phase consuming >50pct of update time.
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
ANCHOR_NAME = "smw_overhead_profile_v1"; N = 4096
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
    g = np.random.default_rng(7); M = int(0.1 * N); K = sign_keys(M, N, g); G = K @ K.T + 1e-3*np.eye(M); Ginv = np.linalg.inv(G)
    k = sign_keys(1, N, g)[0]; ph = {}
    t = time.perf_counter(); u = K @ k; ph["gram_update"] = time.perf_counter() - t
    t = time.perf_counter(); v = Ginv @ u; ph["inv_apply"] = time.perf_counter() - t
    t = time.perf_counter(); denom = 1.0 + k @ k - u @ v; ph["denom"] = time.perf_counter() - t
    t = time.perf_counter(); Ginv2 = Ginv + np.outer(v, v) / denom; ph["rank1_update"] = time.perf_counter() - t
    tot = sum(ph.values()); dom = max(ph, key=ph.get); frac = ph[dom] / tot
    print("  phase fractions: %s; dominant=%s (%.1f pct)" % ({k2: round(v2/tot,3) for k2,v2 in ph.items()}, dom, frac*100), flush=True)
    return {"dom": dom, "frac": frac}
def verdict(r) -> Tuple[str, str]:
    s = "dominant phase=%s frac=%.2f" % (r["dom"], r["frac"])
    if r["frac"] > 0.50: return ("HARD_PASS", "HARD_PASS: SMW update dominated by '%s' (>50pct) -- the optimization target is identified. " % r["dom"] + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: no single phase >50pct. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
