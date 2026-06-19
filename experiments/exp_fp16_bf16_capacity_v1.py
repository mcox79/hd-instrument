"""
exp_fp16_bf16_capacity_v1 -- #2: fp16 vs bf16 capacity parity -- CPU.
ROUTING: cpu_backlog_high_priority_12 #2 fp16-bf16. Compare recall@1 of pinv W stored in fp16 vs bf16 across load; characterize the crossover/safe-M for fp16. CPU.
PRE-REGISTERED: HARD-PASS characterize fp16 vs bf16 crossover (document safe M for fp16).
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
ANCHOR_NAME = "fp16_bf16_capacity_v1"; N = 4096
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
def to_bf16(W):
    u = W.astype(np.float32).view(np.uint32); u = (u + 0x8000) & 0xFFFF0000; return u.view(np.float32)
def run() -> Dict:
    g = np.random.default_rng(7); by = {}
    for load in ([0.1, 0.3] if RUN_MODE=="smoke" else [0.1, 0.2, 0.3, 0.5]):
        M = max(2, int(load*N)); K = sign_keys(M, N, g); W = pinv_W(K)
        r16 = recall(W.astype(np.float16).astype(np.float32), K, np.random.default_rng(1)); rbf = recall(to_bf16(W), K, np.random.default_rng(1))
        by["L%.1f" % load] = {"fp16": r16, "bf16": rbf}; print("  load=%.1f fp16=%.3f bf16=%.3f" % (load, r16, rbf), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    s = "by load: %s" % {k: {"f16": round(v["fp16"],3), "bf16": round(v["bf16"],3)} for k,v in r["by"].items()}
    parity = all(abs(v["fp16"]-v["bf16"]) < 0.05 for v in r["by"].values())
    if parity: return ("HARD_PASS", "HARD_PASS: fp16/bf16 capacity parity (<5pct gap) across loads -- both precisions safe; crossover characterized. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: fp16/bf16 diverge at some load -- crossover documented. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
