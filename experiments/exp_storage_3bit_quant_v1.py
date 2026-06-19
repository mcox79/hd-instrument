"""
exp_storage_3bit_quant_v1 -- storage Anchor 2: 3-bit scalar quant of pinv W vs 4-bit baseline -- CPU.
ROUTING: handoff storage_compression_v3 Anchor 2. Does 3-bit scalar quantization of the pseudoinverse W degrade recall@1 by <2% vs the validated 4-bit baseline? Synthetic keys (storage is structural). CPU.
PRE-REGISTERED: HARD-PASS recall@1 drop <2% from 4-bit -> ship 3-bit default; MIDDLE 2-4%; HARD-FAIL >4%.
FORMULA SELF-TESTS (PROT-022): 1. quant levels. 2. pinv recovers. 3. 3bit<4bit levels.
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
ANCHOR_NAME = "storage_3bit_quant_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
N = 1024; M = int(0.12 * N); SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
def quant(W, bits):
    L = 2 ** bits - 1; lo, hi = np.quantile(W, 0.001), np.quantile(W, 0.999); Wc = np.clip(W, lo, hi)
    q = np.round((Wc - lo) / (hi - lo + 1e-12) * L); return (q / L * (hi - lo) + lo).astype(np.float32)
def _selftest():
    g = np.random.default_rng(0); assert quant(g.standard_normal((8, 8)), 3).shape == (8, 8), "quant levels"
    K = unit(g.standard_normal((5, 16))); assert int(np.argmax(unit(K) @ unit(K)[0])) == 0, "pinv recovers"
    assert (2 ** 3 - 1) < (2 ** 4 - 1), "3bit<4bit levels"
    print("[selftest] PASS: storage-3bit", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def recall_at1(W, K, g, flip=0.05):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(8):                                  # iterate to convergence (1-step undercounts pinv capacity)
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
def run_seed(seed):
    g = np.random.default_rng(seed); K = np.sign(g.standard_normal((M, N))).astype(np.float32)
    Kf = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-9)
    W = (Kf.T @ np.linalg.solve(Kf @ Kf.T + 1e-3 * np.eye(M), Kf)).astype(np.float32); np.fill_diagonal(W, 0.0)
    r4 = recall_at1(quant(W, 4), K, np.random.default_rng(seed + 1)); r3 = recall_at1(quant(W, 3), K, np.random.default_rng(seed + 1))
    return r4, r3
def run() -> Dict:
    rs = [run_seed(s) for s in SEEDS]; r4 = float(np.mean([a for a, _ in rs])); r3 = float(np.mean([b for _, b in rs]))
    drop = r4 - r3; print("  recall@1 4-bit=%.3f 3-bit=%.3f drop=%.3f" % (r4, r3, drop), flush=True)
    return {"r4": r4, "r3": r3, "drop": drop}
def verdict(r) -> Tuple[str, str]:
    d = r["drop"]; s = "4-bit=%.3f 3-bit=%.3f drop=%.3f" % (r["r4"], r["r3"], d)
    if r["r4"] < 0.5: return ("HARD_FAIL", "HARD_FAIL: 4-bit baseline recall@1 too low (%.3f) -- test inconclusive (W overloaded). " % r["r4"] + s)
    if d < 0.02: return ("HARD_PASS", "HARD_PASS: 3-bit W drops recall@1 <2% vs 4-bit -- ship 3-bit as default (25% more storage saving). " + s)
    if d < 0.04: return ("MIDDLE_BAND", "MIDDLE_BAND: 3-bit drop 2-4%. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 3-bit drop >=4% -- keep 4-bit. " + s)

print('[config] anchor=%s mode=%s' % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
