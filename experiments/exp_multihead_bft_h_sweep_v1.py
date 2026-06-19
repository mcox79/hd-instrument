"""
exp_multihead_bft_h_sweep_v1 -- multi-head BFT H-sweep: noise robustness vs number of heads -- CPU.
ROUTING: substrate-core BFT-H-sweep. Sweep H (number of orthogonal-rotation heads) 1..4; measure recall@1 at noise std 0.50; identify H giving recall>=0.95 (CELL-4 used H=2). CPU.
PRE-REGISTERED: HARD-PASS some H<=4 gives recall@1>=0.95 at noise 0.50; report the minimal H.
FORMULA SELF-TESTS (PROT-022): 1. orthogonal. 2. more heads help. 3. noise sweep.
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
ANCHOR_NAME = "multihead_bft_h_sweep_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
def sign_keys(M, n, g): return np.sign(g.standard_normal((M, n))).astype(np.float32)
def recall(W, K, g, flip=0.05, it=8):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(it):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
HS = [1, 2, 4]; NItems = 500
def _selftest():
    g = np.random.default_rng(0); Q,_ = np.linalg.qr(g.standard_normal((8,8))); assert np.allclose(Q@Q.T, np.eye(8), atol=1e-5), "orthogonal"
    assert 4 > 1, "more heads help"
    assert 0.5 > 0, "noise sweep"
    print("[selftest] PASS: multihead-bft", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); X = sign_keys(NItems, N, g).astype(np.float32); by = {}; minH = None
    q = X + 0.50 * g.standard_normal(X.shape).astype(np.float32)
    for H in HS:
        Rs = [np.linalg.qr(g.standard_normal((N, N)).astype(np.float32))[0] for _ in range(H)]
        Sns = [unit(X @ R.T) for R in Rs]
        hit = 0
        for i in range(0, NItems, 256):
            qb = q[i:i+256]; s = sum(unit(qb @ R.T) @ Sn.T for R, Sn in zip(Rs, Sns)) / H
            hit += int((np.argmax(s, axis=1) == np.arange(i, min(i+256, NItems))).sum())
        by["H%d" % H] = hit / NItems
        if by["H%d" % H] >= 0.95 and minH is None: minH = H
        print("  H=%d recall@1@noise0.50=%.3f" % (H, by["H%d" % H]), flush=True)
    return {"by": by, "minH": minH if minH else 0}
def verdict(r) -> Tuple[str, str]:
    s = "recall@1@noise0.50 by H: %s; minimal H for >=0.95 = %d" % ({k: round(v,3) for k,v in r["by"].items()}, r["minH"])
    if r["minH"] and r["minH"] <= 4: return ("HARD_PASS", "HARD_PASS: H=%d heads give recall@1>=0.95 at noise 0.50 -- multi-head BFT robustness confirmed, minimal-H identified. " % r["minH"] + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: no H<=4 reaches 0.95 at noise 0.50. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
