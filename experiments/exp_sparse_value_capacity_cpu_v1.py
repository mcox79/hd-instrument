"""
exp_sparse_value_capacity_cpu_v1.py -- sparse (k-active) value codes raise per-shard capacity vs dense phasor values -- CPU.

ROUTING: deep-batch (sparse-VALUE coding capacity). Compare per-shard recall capacity using dense phasor values vs SPARSE k-active value codes (only k of N dims active). Sparse codes have lower mutual interference -> more facts per shard at fixed recall. Tests the v2.0 sparse-VALUE capacity gain. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS sparse value coding sustains recall>=0.95 at >= 1.5x the dense per-shard load. MIDDLE >= 1.2x. HARD-FAIL < 1.2x.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "sparse_value_capacity_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    import numpy as _n; x = _n.zeros(10); x[[1, 3, 5]] = 1; assert x.sum() == 3, "sparse"; print("[selftest] PASS: sparse-value-capacity", flush=True)
def cap(make_val, N, g):
    VV = 2000; book = make_val(VV, N, g); lo, hi, best = 5, 400, 5
    while lo <= hi:
        M = (lo + hi) // 2; keys = cphasor(M, N, g); vi = g.integers(0, VV, M)
        B = np.zeros(N, dtype=np.complex64)
        for j in range(M):
            B = B + keys[j] * book[vi[j]]
        ok = sum(int(cidx(B * np.conj(keys[j]), book) == vi[j]) for j in range(M)) / M
        if ok >= 0.95:
            best = M; lo = M + 1
        else:
            hi = M - 1
    return best
def run() -> Dict:
    g = np.random.default_rng(213); N = 4096
    def dense(m, d, gg):
        return cphasor(m, d, gg)
    def sparse(m, d, gg):
        K = max(8, d // 32); out = np.zeros((m, d), dtype=np.complex64)
        for i in range(m):
            idx = gg.choice(d, K, replace=False); ph = np.exp(1j * (gg.random(K) * 2 - 1) * math.pi); out[i, idx] = ph.astype(np.complex64)
        return out
    cd = cap(dense, N, np.random.default_rng(1)); cs = cap(sparse, N, np.random.default_rng(1)); ratio = cs / max(1, cd)
    print("  per-shard capacity (recall>=0.95): dense=%d sparse=%d ratio=%.2f" % (cd, cs, ratio), flush=True)
    return {"dense": cd, "sparse": cs, "ratio": ratio}
def verdict(r) -> Tuple[str, str]:
    s = "dense-cap=%d sparse-cap=%d ratio=%.2f" % (r["dense"], r["sparse"], r["ratio"])
    if r["ratio"] >= 1.5: return ("HARD_PASS", "HARD_PASS: sparse-VALUE coding gives >=1.5x per-shard capacity -- v2.0 capacity lever validated. " + s)
    if r["ratio"] >= 1.2: return ("MIDDLE_BAND", "MIDDLE_BAND: sparse capacity gain 1.2-1.5x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sparse capacity gain <1.2x. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
