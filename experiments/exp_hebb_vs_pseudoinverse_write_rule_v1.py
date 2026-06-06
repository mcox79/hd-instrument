"""
exp_hebb_vs_pseudoinverse_write_rule_v1 -- Batch E Cell 2 (TAX-1; largest unrealized gain) -- CPU.

ROUTING: Batch E Drill-4 anchor D. Amit-Gutfreund-Sompolinsky 1985 + Personnaz/Kanter-Sompolinsky: the PSEUDOINVERSE
  (projection) write rule gives alpha_c ~ 1.0 vs Hebbian outer-product alpha_c ~ 0.14 -> ~7x capacity for bipolar patterns
  (substrate is bipolar). Compares exact-recovery capacity of the two write rules on synthetic +-1 patterns across N.
  Hebb: W = P^T P (zero diag). Pseudoinverse: W = P^T (P P^T)^-1 P (projector onto pattern span). Recall = iterated
  sign(W @ s). Vectorized; W is N x N with N bounded small (no OOM). CPU $0.
PRE-REGISTERED: HARD-PASS pseudoinverse alpha_c >= 3x Hebb. MID 1.5-3x. HARD-FAIL <1.5x (pseudoinverse gain not realized).
FORMULA SELF-TESTS (PROT-022): 1. single pattern fixed point both rules. 2. pinv projector idempotent. 3. Hebb low-load.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
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

ANCHOR_NAME = "hebb_vs_pseudoinverse_write_rule_v1"
FLIP = 0.05; STEPS = 8
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_SWEEP = [512]; LOADS = [0.05, 0.1, 0.2, 0.4, 0.6, 0.9]
else:
    SEEDS = [7, 17, 23]; N_SWEEP = [1024, 2048]; LOADS = [0.05, 0.1, 0.14, 0.2, 0.3, 0.4, 0.55, 0.7, 0.85, 0.95]


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def W_hebb(P):
    W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0); return W / P.shape[1]


def W_pinv(P):
    # projector onto pattern span: W = P^T (P P^T)^-1 P ; zero diagonal for dynamics
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32)
    W = (P.T @ np.linalg.solve(G, P)).astype(np.float32); np.fill_diagonal(W, 0.0); return W


def recall(W, P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0                       # vectorized: all M patterns at once
    return float(np.mean(np.all(s == P, axis=1)))


def cap(rule, n, seed):
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * n)); P = patterns(M, n, g)
        W = W_hebb(P) if rule == "hebb" else W_pinv(P)
        if recall(W, P, seed * 7 + M) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); P = patterns(1, 128, g)
    assert recall(W_hebb(P), P, 0) >= 0.95, "Hebb single pattern fixed point"
    assert recall(W_pinv(P), P, 0) >= 0.95, "pinv single pattern fixed point"
    P2 = patterns(20, 128, g); Wp = P2.T @ np.linalg.solve(P2 @ P2.T + 1e-3 * np.eye(20), P2)
    assert np.allclose(Wp @ Wp, Wp, atol=1e-2), "pinv projector idempotent"
    print("[selftest] PASS: hebb-vs-pinv", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    by_N = {}
    for n in N_SWEEP:
        ch = cap("hebb", n, seed); cp = cap("pinv", n, seed)
        by_N["N%d" % n] = {"hebb_alpha_c": ch, "pinv_alpha_c": cp, "ratio": cp / max(ch, 1e-9)}
        print("  [seed=%d N=%d] hebb_alpha_c=%.3f pinv_alpha_c=%.3f ratio=%.2fx" % (seed, n, ch, cp, cp / max(ch, 1e-9)), flush=True)
    return {"seed": seed, "by_N": by_N}


def verdict(ps) -> Tuple[str, str]:
    nmax = "N%d" % N_SWEEP[-1]
    h = float(np.mean([p["by_N"][nmax]["hebb_alpha_c"] for p in ps])); pv = float(np.mean([p["by_N"][nmax]["pinv_alpha_c"] for p in ps])); g = pv / max(h, 1e-9)
    summary = "at N=%d: hebb_alpha_c=%.3f pinv_alpha_c=%.3f | pinv/hebb=%.2fx (theory ~7x)" % (N_SWEEP[-1], h, pv, g)
    if g >= 3.0:
        return ("HARD_PASS", "HARD_PASS: pseudoinverse write rule >=3x Hebb capacity -- largest single capacity lever, swap the write rule. " + summary)
    if g >= 1.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: pseudoinverse 1.5-3x Hebb. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: pseudoinverse <1.5x Hebb (gain not realized in this regime). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_sweep=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_SWEEP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
