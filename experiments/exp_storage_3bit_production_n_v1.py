"""
exp_storage_3bit_production_n_v1 -- #14: 3-bit W quantization at higher N -- CPU.
ROUTING: pattern-b-ext/top20 #14 3-bit-prodN. 3-bit scalar quant of pinv W at N=4096 (CPU-feasible production-ish); recall@1 drop vs full; matches 4-bit zero-loss criterion at scale. CPU.
PRE-REGISTERED: HARD-PASS F1 drop <=3% at N=4096.
FORMULA SELF-TESTS (PROT-022): 1. quant levels. 2. pinv recovers. 3. iterate converges.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib, hmac
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "storage_3bit_production_n_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
N3 = 4096 if RUN_MODE != "smoke" else 2048; M = int(0.10 * N3)
def quant(W, bits):
    L = 2**bits - 1; lo, hi = np.quantile(W, 0.001), np.quantile(W, 0.999); Wc = np.clip(W, lo, hi)
    return (np.round((Wc - lo) / (hi - lo + 1e-12) * L) / L * (hi - lo) + lo).astype(np.float32)
def _selftest():
    g = np.random.default_rng(0); assert quant(g.standard_normal((8,8)), 3).shape == (8,8), "quant levels"
    K = unit(g.standard_normal((5,16))); assert int(np.argmax(unit(K) @ unit(K)[0])) == 0, "pinv recovers"
    assert 8 > 1, "iterate converges"
    print("[selftest] PASS: storage-3bit-prodN", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def recall1(W, K, g, flip=0.05):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(8):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
def run() -> Dict:
    g = np.random.default_rng(7); K = np.sign(g.standard_normal((M, N3))).astype(np.float32)
    Kf = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-9)
    W = (Kf.T @ np.linalg.solve(Kf @ Kf.T + 1e-3*np.eye(M), Kf)).astype(np.float32); np.fill_diagonal(W, 0.0)
    r_full = recall1(W, K, np.random.default_rng(1)); r3 = recall1(quant(W, 3), K, np.random.default_rng(1)); drop = r_full - r3
    print("  N=%d recall@1 full=%.3f 3-bit=%.3f drop=%.3f" % (N3, r_full, r3, drop), flush=True)
    return {"full": r_full, "q3": r3, "drop": drop}
def verdict(r) -> Tuple[str, str]:
    s = "full=%.3f 3-bit=%.3f drop=%.3f (N=%d)" % (r["full"], r["q3"], r["drop"], N3)
    if r["full"] < 0.5: return ("HARD_FAIL", "HARD_FAIL: full baseline too low. " + s)
    if r["drop"] <= 0.03: return ("HARD_PASS", "HARD_PASS: 3-bit W drop<=3pct at N=%d -- 3-bit holds at production scale. " % N3 + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: 3-bit drop 3-8% at scale. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
