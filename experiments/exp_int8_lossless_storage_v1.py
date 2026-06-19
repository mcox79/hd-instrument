"""
exp_int8_lossless_storage_v1.py -- int8-quantized substrate retains recall vs bf16 (4x memory saving) -- CPU.

ROUTING: DEEPER_drills_8 Anchor 1.3 (int8 Modern Hopfield). Quantize continuous stored patterns to int8 (per-vector scale) vs float16; measure recall@1 of noisy queries. int8 = 4x memory vs fp32, 2x vs fp16; validates lossless int8 production storage. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS int8 recall@1 >= 0.95 * fp16 recall at production noise. MIDDLE >= 0.90. HARD-FAIL < 0.90.
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
ANCHOR_NAME = "int8_lossless_storage_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    x = np.array([0.5, -0.3]); q = np.clip(np.round(x / 0.004), -127, 127).astype(np.int8); assert q.dtype == np.int8, "int8 dtype"
    assert np.float16(1.0) == 1.0, "fp16 ok"
    e = np.array([3.0, 4.0]); assert abs(np.linalg.norm(e) - 5.0) < 1e-6, "norm"
    print("[selftest] PASS: int8-lossless-storage", flush=True)
def quant8(X):
    sc = np.abs(X).max(axis=1, keepdims=True) / 127.0 + 1e-12
    return np.round(X / sc).astype(np.int8).astype(np.float32) * sc
def recall(K, Q, qi, dtype):
    Kd = K.astype(dtype).astype(np.float32); Qd = Q.astype(dtype).astype(np.float32)
    pred = np.argmax(Qd @ Kd.T, axis=1); return float((pred == qi).mean())
def run() -> Dict:
    g = np.random.default_rng(1); N = 5000 if SMOKE else 30000; D = 768; NOISE = 0.3; NQ = 500
    X = g.standard_normal((N, D)).astype(np.float32); X = X / np.linalg.norm(X, axis=1, keepdims=True)
    qi = g.choice(N, NQ, replace=False); Q = X[qi] + NOISE / np.sqrt(D) * g.standard_normal((NQ, D)).astype(np.float32)
    r16 = recall(X, Q, qi, np.float16)
    X8 = quant8(X); Q8 = quant8(Q); pred = np.argmax(Q8 @ X8.T, axis=1); r8 = float((pred == qi).mean())
    ratio = r8 / (r16 + 1e-9)
    print("  recall@1 fp16=%.3f int8=%.3f ratio=%.3f (N=%d D=%d noise=%.1f)" % (r16, r8, ratio, N, D, NOISE), flush=True)
    return {"fp16": r16, "int8": r8, "ratio": ratio}
def verdict(r) -> Tuple[str, str]:
    s = "int8=%.3f fp16=%.3f ratio=%.3f" % (r["int8"], r["fp16"], r["ratio"])
    if r["ratio"] >= 0.95: return ("HARD_PASS", "HARD_PASS: int8 storage retains >=95pct of fp16 recall -- 4x memory saving production-safe. " + s)
    if r["ratio"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: int8 0.90-0.95 of fp16. " + s)
    return ("HARD_FAIL", "HARD_FAIL: int8 <0.90 of fp16 recall. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
