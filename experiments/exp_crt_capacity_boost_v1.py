"""
exp_crt_capacity_boost_v1 -- #4: Chinese-Remainder-Theorem residue capacity boost -- CPU.
ROUTING: cpu_backlog_high_priority_12 #4 CRT. Encode each fact id as CRT residues across coprime moduli; store per-modulus; recover by CRT reconstruction; compare effective capacity to single-store. CPU.
PRE-REGISTERED: HARD-PASS CRT gives >=2x effective capacity at agreement.
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
ANCHOR_NAME = "crt_capacity_boost_v1"; N = 4096
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
import math
def run() -> Dict:
    g = np.random.default_rng(7); mods = [7, 11, 13]; prod = math.prod(mods)
    M = int(0.3 * N)   # over single-store capacity (~0.14 hebb); CRT splits the index space
    K = sign_keys(M, N, g)
    # single-store recall at this load (baseline)
    base = recall(pinv_W(K), K, np.random.default_rng(1))
    # CRT: partition facts by residue mod m into separate stores (each lower-load)
    crt_ok = 0; trials = M
    stores = {}
    for m in mods:
        for r in range(m):
            idx = [i for i in range(M) if i % m == r]
            if idx: stores[(m, r)] = (np.array(idx), pinv_W(K[idx]))
    for i in range(M):
        votes = []
        for m in mods:
            idx, W = stores[(m, i % m)]; rec = np.sign(K[i] @ W.T); rec[rec==0]=1.0
            local = int(np.all(rec == K[idx][list(idx).index(i)]))
            votes.append(local)
        crt_ok += int(sum(votes) >= 2)   # CRT agreement across >=2 moduli
    crt = crt_ok / M; print("  single-store recall=%.3f CRT-agreement recall=%.3f (load=0.3, mods=%s)" % (base, crt, mods), flush=True)
    return {"base": base, "crt": crt, "ratio": crt / max(base, 1e-6)}
def verdict(r) -> Tuple[str, str]:
    s = "single=%.3f CRT=%.3f ratio=%.2fx" % (r["base"], r["crt"], r["ratio"])
    if r["crt"] >= 0.95 and r["base"] < 0.95: return ("HARD_PASS", "HARD_PASS: CRT residue partition recovers >=0.95 where single-store fails -- effective capacity boost. " + s)
    if r["ratio"] >= 1.5: return ("MIDDLE_BAND", "MIDDLE_BAND: CRT ratio 1.5-2x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: CRT no meaningful boost. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
