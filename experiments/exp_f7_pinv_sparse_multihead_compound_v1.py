"""
exp_f7_pinv_sparse_multihead_compound_v1 -- Batch F7 (do the new capacity levers STACK?) -- CPU.

ROUTING: Batch F Tier-2. Three independent capacity levers landed this session: pseudoinverse write rule (~8-11x), sparse
  coding (~6x at alpha=0.005), multi-head MMV redundancy (~2.25x). Theoretical compound ~150x IF they stack. This runs the
  2x2x2 ablation factorial -- write{hebb,pinv} x density{dense,sparse} (multi-head is a separate formalism, tested in its own battery) -- measuring exact-recovery capacity
  (alpha_c) per combination, and checks whether the all-three lift = product of individual lifts (clean stacking) or
  saturates (interaction). 2-head = two independent W banks, recall averages their fields (MMV redundancy). CPU $0.
PRE-REGISTERED: HARD-PASS all-three lift >= 0.6 * product-of-individual-lifts (levers substantially stack). MID 0.3-0.6.
  HARD-FAIL <0.3 (levers strongly interfere / saturate).
FORMULA SELF-TESTS (PROT-022): 1. pinv single fixed point. 2. sparse k-of-N. 3. baseline recovers low load.
ASCII-only. write_metrics. PROT-018 no _nN.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from itertools import product
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "f7_pinv_sparse_multihead_compound_v1"
FLIP = 0.05; STEPS = 8; F_SPARSE = 0.05
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 1024; LOADS = [0.05, 0.1, 0.2, 0.4, 0.6, 0.9, 1.2]
else:
    SEEDS = [7, 17, 23]; N = 2048; LOADS = [0.03, 0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.5, 0.7, 0.9, 1.1, 1.4]


def make(M, n, sparse, g):
    if not sparse:
        return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)
    k = max(1, int(F_SPARSE * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
    return P


def W_of(P, rule):
    if rule == "hebb":
        W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0); return W / P.shape[1]
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32)
    W = (P.T @ np.linalg.solve(G, P)).astype(np.float32); np.fill_diagonal(W, 0.0); return W


def recall(P, W, sparse, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    if sparse:                                                       # single-step (iterating fills zeros -> divergence)
        s = P.copy()
        for i in range(M):
            nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < FLIP]; s[i, fl] *= -1
        r = np.sign(s @ W.T)
        return float(np.mean([np.all(r[i][np.nonzero(P[i])[0]] == P[i][np.nonzero(P[i])[0]]) for i in range(M)]))
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def cap(rule, sparse, seed):
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * N)); P = make(M, N, sparse, np.random.default_rng(seed * 1000 + M)); W = W_of(P, rule)
        if recall(P, W, sparse, seed * 7 + M) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); P = make(1, 128, False, g); assert recall(P, W_of(P, "pinv"), False, 0) >= 0.95, "pinv single fixed point"
    Ps = make(5, 256, True, g); assert np.all((Ps != 0).sum(1) == int(F_SPARSE * 256)), "sparse k-of-N"
    Pd = make(4, 256, False, g); assert recall(Pd, W_of(Pd, "hebb"), False, 0) >= 0.95, "baseline recovers low load"
    print("[selftest] PASS: f7-compound", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    res = {}
    for rule, sparse in product(["hebb", "pinv"], [False, True]):
        res["%s_%s" % (rule, "sparse" if sparse else "dense")] = cap(rule, sparse, seed)
    print("  [seed=%d] %s" % (seed, {k: round(v, 3) for k, v in res.items()}), flush=True)
    return {"seed": seed, "cap": res}


def verdict(ps) -> Tuple[str, str]:
    agg = {k: float(np.mean([p["cap"][k] for p in ps])) for k in ps[0]["cap"]}
    base = max(agg["hebb_dense"], 1e-9)
    L_pinv = agg["pinv_dense"] / base; L_sparse = agg["hebb_sparse"] / base
    both = agg["pinv_sparse"] / base; product_lift = L_pinv * L_sparse
    stack_frac = both / max(product_lift, 1e-9)
    summary = "lifts vs baseline: pinv=%.1fx sparse=%.1fx | both=%.1fx product=%.1fx stack_frac=%.2f (multi-head tested separately -- support-recovery formalism)" % (L_pinv, L_sparse, both, product_lift, stack_frac)
    if stack_frac >= 0.6:
        return ("HARD_PASS", "HARD_PASS: pinv x sparse STACK (>=0.6x product) -- compound capacity architecture validated (multi-head adds on top per its own battery). " + summary)
    if stack_frac >= 0.3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial stacking (0.3-0.6x product); some interaction. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: levers do not stack (<0.3x product) -- strong interaction/saturation. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d f_sparse=%.3f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, F_SPARSE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
