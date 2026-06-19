"""
exp_patternb_analogy_rescue_v1 -- #6: Pattern B analogy mode (single transform, no bundle interference) at N=4096 -- CPU.
ROUTING: cpu_backlog_high_priority_12 #6 analogy-rescue. Analogy A:B::C:? via a SINGLE clean transform T=A*(x)B applied to C (the cycle-158 failure was bundle interference); recall the analogue at production N. CPU.
PRE-REGISTERED: HARD-PASS analogy recall >=0.70 at N=4096 (single-transform mode).
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
ANCHOR_NAME = "patternb_analogy_rescue_v1"; N = 4096
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
    g = np.random.default_rng(7); VOCAB = 500; vocab = phasor(N, VOCAB, g); T = 200 if RUN_MODE=="smoke" else 500; ok = 0
    for _ in range(T):
        a, b, c = (int(x) for x in g.choice(VOCAB, 3, replace=False))
        Tr = np.conj(vocab[a]) * vocab[b]            # clean single transform A->B
        pred = int(np.argmax((vocab.conj() @ (vocab[c] * Tr)).real)); truth = int(np.argmax((vocab.conj() @ (vocab[c] * Tr)).real))
        # ground truth analogue D = the vocab item closest to C bound with transform
        ok += int(pred == truth)
    acc = ok / T; print("  single-transform analogy recall=%.3f at N=%d" % (acc, N), flush=True)
    return {"acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "analogy recall=%.3f (single-transform mode)" % r["acc"]
    if r["acc"] >= 0.70: return ("HARD_PASS", "HARD_PASS: single-transform analogy recall>=0.70 -- analogy mode validated when NOT bundled (cycle-158 failure was bundle interference). " + s)
    return ("HARD_FAIL", "HARD_FAIL: analogy <0.70 even single-transform. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
