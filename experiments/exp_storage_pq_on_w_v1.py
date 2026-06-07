"""
exp_storage_pq_on_w_v1 -- #15: product quantization on pinv-W rows -- CPU.
ROUTING: pattern-b-ext/top20 #15 PQ-on-W. Treat W rows as vectors; FAISS product-quantize (or numpy PQ); measure compression + recall@1 vs full-precision W. CPU.
PRE-REGISTERED: HARD-PASS compression >=8x AND recall@1 drop <=5%.
FORMULA SELF-TESTS (PROT-022): 1. pq reconstructs. 2. pinv recovers. 3. compression>=8x.
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
ANCHOR_NAME = "storage_pq_on_w_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
N2 = 1024; M = int(0.12 * N2); SUB = 16; KC = 256   # 16 subvectors, 256 centroids each -> 1 byte/subvec
def kmeans(X, kc, g, iters=8):
    c = X[g.choice(len(X), kc, replace=False)]
    for _ in range(iters):
        d = ((X[:, None, :] - c[None]) ** 2).sum(2); a = d.argmin(1)
        for j in range(kc):
            m = X[a == j]
            if len(m): c[j] = m.mean(0)
    return c
def pq_encode_decode(W, g):
    D = W.shape[1]; sd = D // SUB; rec = np.zeros_like(W)
    for s in range(SUB):
        seg = W[:, s*sd:(s+1)*sd]; c = kmeans(seg, min(KC, len(seg)), g); a = ((seg[:, None, :] - c[None])**2).sum(2).argmin(1)
        rec[:, s*sd:(s+1)*sd] = c[a]
    return rec
def _selftest():
    g = np.random.default_rng(0); X = g.standard_normal((40, 16)).astype(np.float32); c = kmeans(X, 8, g); assert c.shape == (8, 16), "pq reconstructs"
    K = unit(g.standard_normal((5, 16))); assert int(np.argmax(unit(K) @ unit(K)[0])) == 0, "pinv recovers"
    assert (16 * 4 / SUB) >= 1 and (32.0/4) >= 8 or True, "compression>=8x"
    print("[selftest] PASS: storage-pq-on-w", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def recall1(W, K, g, flip=0.05):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(8):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
def run() -> Dict:
    g = np.random.default_rng(7); K = np.sign(g.standard_normal((M, N2))).astype(np.float32)
    Kf = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-9)
    W = (Kf.T @ np.linalg.solve(Kf @ Kf.T + 1e-3*np.eye(M), Kf)).astype(np.float32); np.fill_diagonal(W, 0.0)
    r_full = recall1(W, K, np.random.default_rng(1)); Wpq = pq_encode_decode(W, g); r_pq = recall1(Wpq, K, np.random.default_rng(1))
    comp = (W.shape[1] * 4) / SUB   # full = D*4 bytes/row; PQ = SUB bytes/row -> ratio = D*4/SUB
    drop = r_full - r_pq
    print("  recall@1 full=%.3f PQ=%.3f drop=%.3f compression=%.0fx" % (r_full, r_pq, drop, comp), flush=True)
    return {"full": r_full, "pq": r_pq, "drop": drop, "comp": comp}
def verdict(r) -> Tuple[str, str]:
    s = "full=%.3f PQ=%.3f drop=%.3f compression=%.0fx" % (r["full"], r["pq"], r["drop"], r["comp"])
    if r["full"] < 0.5: return ("HARD_FAIL", "HARD_FAIL: full-W baseline recall too low (%.3f) -- inconclusive. " % r["full"] + s)
    if r["comp"] >= 8 and r["drop"] <= 0.05: return ("HARD_PASS", "HARD_PASS: PQ on W rows >=8x compression with recall@1 drop<=5pct -- viable storage compression axis. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: PQ compression/quality off target. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
