"""
exp_modern_hopfield_n_sweep_v1 -- storage-unconventional anchor 1 (modern Hopfield exponential energy) -- CPU.

ROUTING: handoff storage_unconventional_mechanisms #1. Modern Hopfield (exponential energy / softmax retrieval, Ramsauer
  2020) stores ~exp(N) patterns -- can N drop from 65536 to 4096-8192 at high load? Measures retrieval accuracy at M/N up to
  0.30 with the exponential-energy update. CPU.
PRE-REGISTERED: HARD-PASS accuracy>0.90 at N=4096 M/N=0.30. HARD-FAIL accuracy<0.70 at M/N=0.20.
FORMULA SELF-TESTS (PROT-022): 1. exact retrieval clean. 2. softmax sharpens. 3. load ordered.
ASCII-only. write_metrics. PROT-018 no _nN.
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

ANCHOR_NAME = "modern_hopfield_n_sweep_v1"
BETA = 8.0; FLIP = 0.05
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
N_GRID = [2048, 4096] if RUN_MODE == "smoke" else [4096, 8192]
LOADS = [0.2, 0.3]


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def softmax(x):
    x = x - x.max(1, keepdims=True); e = np.exp(x); return e / e.sum(1, keepdims=True)


def mh_recall(P, beta, seed):
    g = np.random.default_rng(seed); M, n = P.shape; s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(3):
        s = np.sign(softmax(beta * (s @ P.T)) @ P); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def _selftest():
    g = np.random.default_rng(0); P = patterns(4, 128, g); assert mh_recall(P, 8.0, 0) >= 0.95, "exact retrieval clean"
    a = softmax(np.array([[0.0, 10.0]])); assert a[0, 1] > 0.99, "softmax sharpens"
    assert LOADS[1] > LOADS[0], "load ordered"
    print("[selftest] PASS: modern-hopfield", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    by = {}
    for n in N_GRID:
        for load in LOADS:
            M = max(4, int(load * n)); accs = [mh_recall(patterns(M, n, np.random.default_rng(s)), BETA, s * 7 + M) for s in SEEDS]
            a = float(np.mean(accs)); by["N%d_L%.2f" % (n, load)] = a; print("  [N=%d M/N=%.2f] accuracy=%.3f" % (n, load, a), flush=True)
    return {"by": by}


def verdict(r) -> Tuple[str, str]:
    acc030 = r["by"].get("N%d_L0.30" % N_GRID[0], 0.0); acc020 = r["by"].get("N%d_L0.20" % N_GRID[0], 0.0)
    summary = "accuracy: %s (N=%d M/N=0.30 -> %.3f)" % ({k: round(v, 3) for k, v in r["by"].items()}, N_GRID[0], acc030)
    if acc030 > 0.90:
        return ("HARD_PASS", "HARD_PASS: modern Hopfield >0.90 at N=4096 M/N=0.30 -- exponential energy lets N drop from 65536; major storage win. " + summary)
    if acc020 >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: holds at M/N=0.20 but not 0.30. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: modern Hopfield <0.70 at M/N=0.20 -- no N-reduction benefit. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s beta=%.1f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, BETA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
