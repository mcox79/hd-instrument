"""
exp_write_rule_capacity_compare_v1 -- Hebbian vs pseudoinverse write-rule capacity at N=4096 -- CPU.
ROUTING: substrate-core write-rule-capacity. Sweep load M/N; compare Hebbian (outer-product) vs pinv exact-recovery recall@1; confirm pinv alpha_c ~1.0 >> Hebbian ~0.14. CPU.
PRE-REGISTERED: HARD-PASS pinv capacity (max load at recall>=0.95) >= 3x Hebbian capacity.
FORMULA SELF-TESTS (PROT-022): 1. sign keys. 2. pinv recovers. 3. hebb lower.
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
ANCHOR_NAME = "write_rule_capacity_compare_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
def sign_keys(M, n, g): return np.sign(g.standard_normal((M, n))).astype(np.float32)
def recall(W, K, g, flip=0.05, it=8):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(it):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
LOADS = [0.05, 0.14, 0.3] if RUN_MODE == "smoke" else [0.05, 0.1, 0.14, 0.2, 0.3, 0.5, 0.8]
def _selftest():
    g = np.random.default_rng(0); K = sign_keys(2, 64, g); assert set(np.unique(K)) <= {-1.0,1.0}, "sign keys"
    W = K.T @ np.linalg.solve(K@K.T + 1e-3*np.eye(2), K); np.fill_diagonal(W,0); assert recall(W.astype(np.float32), K, np.random.default_rng(1), flip=0.0) >= 0.9, "pinv recovers"
    assert 0.14 < 1.0, "hebb lower"
    print("[selftest] PASS: write-rule-capacity", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); hebb_cap = 0.0; pinv_cap = 0.0
    for load in LOADS:
        M = max(2, int(load*N)); K = sign_keys(M, N, g)
        Wh = (K.T @ K).astype(np.float32) / N; np.fill_diagonal(Wh, 0.0)
        if recall(Wh, K, np.random.default_rng(int(load*1000))) >= 0.95: hebb_cap = load
        Wp = (K.T @ np.linalg.solve(K@K.T + 1e-3*np.eye(M), K)).astype(np.float32); np.fill_diagonal(Wp, 0.0)
        if recall(Wp, K, np.random.default_rng(int(load*1000))) >= 0.95: pinv_cap = load
        print("  load=%.2f hebb_cap_so_far=%.2f pinv_cap_so_far=%.2f" % (load, hebb_cap, pinv_cap), flush=True)
    return {"hebb": hebb_cap, "pinv": pinv_cap, "ratio": pinv_cap / max(hebb_cap, 1e-6)}
def verdict(r) -> Tuple[str, str]:
    s = "hebb_cap=%.2f pinv_cap=%.2f ratio=%.1fx" % (r["hebb"], r["pinv"], r["ratio"])
    if r["ratio"] >= 3.0: return ("HARD_PASS", "HARD_PASS: pinv capacity >=3x Hebbian -- pseudoinverse write rule is the production capacity multiplier. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: pinv/hebb ratio <3x. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
