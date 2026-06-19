"""
exp_storage_blockwise_quant_v1 -- #8: block-wise quant with shared scales -- CPU.
ROUTING: cpu_backlog_high_priority_12 #8 blockwise. Quantize W in blocks with per-block shared scale (3-bit codes + fp16 per-block scale); compression + F1 vs 4-bit. CPU.
PRE-REGISTERED: HARD-PASS 2-3x compression beyond 4-bit at F1 drop <=3pct.
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
ANCHOR_NAME = "storage_blockwise_quant_v1"; N = 4096
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
    g = np.random.default_rng(7); M = int(0.1*N); K = sign_keys(M, N, g); W = pinv_W(K); r4 = recall(quant(W,4), K, np.random.default_rng(1))
    BS = 64; Wb = W.copy().reshape(-1)
    for i in range(0, len(Wb), BS):
        blk = Wb[i:i+BS]; sc = np.abs(blk).max() + 1e-9; q = np.round(blk/sc*3); Wb[i:i+BS] = q/3*sc   # 3-bit (-3..3) per block
    Wb = Wb.reshape(W.shape); rb = recall(Wb.astype(np.float32), K, np.random.default_rng(1))
    comp = 4.0 / (3 + 16.0/BS); print("  4bit F1=%.3f blockwise F1=%.3f compression-vs-4bit=%.2fx" % (r4, rb, comp), flush=True)
    return {"r4": r4, "rb": rb, "drop": r4-rb, "comp": comp}
def verdict(r) -> Tuple[str, str]:
    s = "4bit=%.3f block=%.3f drop=%.3f comp-vs-4bit=%.2fx" % (r["r4"], r["rb"], r["drop"], r["comp"])
    if r["comp"] >= 2.0 and r["drop"] <= 0.03: return ("HARD_PASS", "HARD_PASS: block-wise quant 2-3x beyond 4-bit at <=3pct drop. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: block-wise off target. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
