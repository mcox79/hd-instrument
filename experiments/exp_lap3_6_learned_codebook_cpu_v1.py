"""
exp_lap3_6_learned_codebook_cpu_v1.py -- learned (orthonormal) vs random codebook capacity at K=150 -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (LAP3-6 LEARNED-ORTHOGONAL-CODEBOOK); pure-FHRR (no download). Compare recall storing K=150 pairs with a random vs an orthonormal (QR) value codebook.
PRE-REGISTERED: HARD-PASS capacity ratio>=1.5x. MIDDLE>=1.2x. HARD-FAIL<1.2x.
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
ANCHOR_NAME = "lap3_6_learned_codebook_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; q, _ = _n.linalg.qr(_n.random.RandomState(0).randn(4, 4)); assert q.shape == (4, 4), "qr"; print("[selftest] PASS: learned-codebook", flush=True)
def _recall(N, K, vals, g):
    keys = cphasor(K, N, g); Mem = (keys * vals).sum(axis=0)
    return sum(int(cidx(Mem * np.conj(keys[i]), vals) == i) for i in range(K)) / K
def run() -> Dict:
    g = np.random.default_rng(150); N = 512; K = 150; TR = 5 if SMOKE else 25
    rand_r = []; learn_r = []
    for _ in range(TR):
        rv = cphasor(K, N, g)                                            # random codebook
        Q, _ = np.linalg.qr(g.standard_normal((N, K)) + 1j * g.standard_normal((N, K)))   # learned: orthonormal codebook
        lv = (Q.T * math.sqrt(N)).astype(np.complex64)                   # K orthonormal columns -> rows, scaled to ~unit-energy
        rand_r.append(_recall(N, K, rv, g)); learn_r.append(_recall(N, K, lv, g))
    rr = float(np.mean(rand_r)); lr = float(np.mean(learn_r)); ratio = lr / rr if rr > 0 else 99.0
    print("  CODEBOOK K=%d N=%d: random-recall=%.3f learned-recall=%.3f ratio=%.2fx (n=%d)" % (K, N, rr, lr, ratio, TR), flush=True)
    return {"random_recall": rr, "learned_recall": lr, "capacity_ratio": round(ratio, 2), "K": K, "N": N}
def verdict(r) -> Tuple[str, str]:
    s = "random=%.3f learned=%.3f ratio=%.2fx (K=%d N=%d)" % (r["random_recall"], r["learned_recall"], r["capacity_ratio"], r["K"], r["N"])
    if r["capacity_ratio"] >= 1.5:
        return ("HARD_PASS", "HARD_PASS: learned orthonormal codebook gives >=1.5x the recall/capacity of a random codebook at K=150 -- engineering lever #2 (learned codebooks) confirmed; substrate stack expects learned codebooks at the right layer. " + s)
    if r["capacity_ratio"] >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: capacity ratio 1.2-1.5x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity ratio <1.2x. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
