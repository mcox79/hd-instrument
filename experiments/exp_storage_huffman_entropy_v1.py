"""
exp_storage_huffman_entropy_v1 -- storage compression Anchor 1: entropy of 4-bit pinv-W codewords -- CPU.
ROUTING: handoff storage_compression_v3 Anchor 1 (CPU, not pause-gated). If the 4-bit quantized pseudoinverse W matrix has
  low Shannon entropy on its codeword histogram (H<3.0 bits of 4), Huffman/entropy coding gives a free 1.33x+ storage gain
  on top of 4-bit. CPU.
PRE-REGISTERED: HARD-PASS H < 3.0 bits (1.33x+ gain). MIDDLE 3.0-3.5. HARD-FAIL >= 3.5 (near-uniform; no coding gain).
FORMULA SELF-TESTS (PROT-022): 1. uniform entropy=4. 2. degenerate entropy=0. 3. 16 levels.
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
ANCHOR_NAME = "storage_huffman_entropy_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N = 512 if RUN_MODE == "smoke" else 2048; M = int(0.5 * N); SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
def entropy(hist):
    p = hist[hist > 0] / hist.sum(); return float(-(p * np.log2(p)).sum())
def quant4(W):
    lo, hi = np.quantile(W, 0.001), np.quantile(W, 0.999); Wc = np.clip(W, lo, hi)
    return np.clip(((Wc - lo) / (hi - lo + 1e-12) * 15).round(), 0, 15).astype(np.int64)
def _selftest():
    assert abs(entropy(np.ones(16)) - 4.0) < 1e-6, "uniform entropy=4"
    h = np.zeros(16); h[3] = 100; assert entropy(h) == 0.0, "degenerate entropy=0"
    g = np.random.default_rng(0); assert quant4(g.standard_normal((8, 8))).max() <= 15, "16 levels"
    print("[selftest] PASS: storage-huffman", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run_seed(seed):
    g = np.random.default_rng(seed); K = g.standard_normal((M, N)).astype(np.float64)
    K /= (np.linalg.norm(K, axis=1, keepdims=True) + 1e-9)
    W = (K.T @ np.linalg.solve(K @ K.T + 1e-3 * np.eye(M), K)).astype(np.float64)   # pinv associative W (NxN)
    q = quant4(W); hist = np.bincount(q.ravel(), minlength=16).astype(np.float64); return entropy(hist)
def run() -> Dict:
    H = float(np.mean([run_seed(s) for s in SEEDS])); gain = 4.0 / max(H, 1e-6)
    print("  4-bit W codeword entropy H=%.3f bits -> entropy-coding gain %.2fx (on top of 4-bit)" % (H, gain), flush=True)
    return {"entropy_bits": H, "gain": gain}
def verdict(r) -> Tuple[str, str]:
    H = r["entropy_bits"]; summary = "H=%.3f bits (of 4); entropy-coding gain=%.2fx" % (H, r["gain"])
    if H < 3.0: return ("HARD_PASS", "HARD_PASS: 4-bit W codeword entropy <3.0 bits -- Huffman/entropy coding gives 1.33x+ free storage gain on top of 4-bit. " + summary)
    if H < 3.5: return ("MIDDLE_BAND", "MIDDLE_BAND: entropy 3.0-3.5 bits (modest coding gain). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: entropy >=3.5 bits -- codewords near-uniform; no entropy-coding gain. " + summary)
print("[config] anchor=%s mode=%s N=%d M=%d seeds=%s" % (ANCHOR_NAME, RUN_MODE, N, M, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
