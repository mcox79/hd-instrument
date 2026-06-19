"""
substrate_sq7_two_substrate_transfer_v1_n2048 -- two-substrate knowledge transfer (distributed intelligence) -- remote CPU.

ROUTING: SQ7 (P_drill=0.70). Can substrate B acquire substrate A's learned associations via direct weight
  transfer (W_merged = W_A + W_B), and does merging keep BOTH knowledge bases without catastrophic interference?
  CPU numpy, $0. remote_cpu_queue.

CELLS (3 seeds): A learns M ctx->val assoc; B learns M different assoc; arms = A_alone recall(A), B_alone recall(B),
  merged recall(A), merged recall(B). M = FRAC*alpha_c*N each (merged ~2*FRAC*alpha_c).
PRE-REG: HARD-PASS merged recall(A) AND recall(B) both >= 0.90 (lossless transfer below joint capacity).
  MIDDLE both >= 0.75. HARD-FAIL either < 0.75 (interference).
SELF-TESTS (PROT-022): 1. heteroassoc recall. 2. N=2048.
ASCII-only. write_metrics. PROT-018 _n2048 -> N=2048.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sq7_two_substrate_transfer_v1_n2048"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
FRAC = 0.40
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def learn(n, M, g):
    ctx = bipolar((M, n), g); val = bipolar((M, n), g); W = (val.T @ ctx).astype(np.float32)
    return W, ctx, val


def recall(W, ctx, val, n):
    R = np.sign(ctx @ W.T); R[R == 0] = 1.0
    return float(np.mean((R * val).sum(axis=1) / n > 0.90))


def _selftest():
    g = np.random.default_rng(0); W, ctx, val = learn(256, 5, g)
    assert recall(W, ctx, val, 256) > 0.9, "heteroassoc recall"
    assert N == 2048
    print("[selftest] PASS: heteroassoc_recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed):
    M = max(2, int(round(FRAC * ALPHA_C * N_DIM)))
    Wa, ca, va = learn(N_DIM, M, np.random.default_rng(seed * 10 + 1))
    Wb, cb, vb = learn(N_DIM, M, np.random.default_rng(seed * 10 + 2))
    Wm = Wa + Wb
    return {"seed": seed, "M_each": M,
            "A_alone": recall(Wa, ca, va, N_DIM), "B_alone": recall(Wb, cb, vb, N_DIM),
            "merged_A": recall(Wm, ca, va, N_DIM), "merged_B": recall(Wm, cb, vb, N_DIM)}


def verdict(ps) -> Tuple[str, str]:
    mA = float(np.mean([p["merged_A"] for p in ps])); mB = float(np.mean([p["merged_B"] for p in ps]))
    aA = float(np.mean([p["A_alone"] for p in ps])); aB = float(np.mean([p["B_alone"] for p in ps]))
    summary = "A_alone=%.2f B_alone=%.2f merged_A=%.2f merged_B=%.2f (M_each=%d)" % (aA, aB, mA, mB, ps[0]["M_each"])
    if mA >= 0.90 and mB >= 0.90:
        return ("HARD_PASS", "HARD_PASS: two substrates merge losslessly (both knowledge bases preserved). " + summary)
    if mA >= 0.75 and mB >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: merge mostly preserves both. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: merge causes interference. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d frac=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, FRAC), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] A=%.2f B=%.2f mA=%.2f mB=%.2f" % (seed, r["A_alone"], r["B_alone"], r["merged_A"], r["merged_B"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
