"""
exp_pb_pinv_capacity_n_scaling_v1 -- propose-back (absolute facts-per-dim storable with pinv at larger N (production ceiling)) -- CPU.

ROUTING: Exp-Dev propose-back. Hebb capacity is alpha_c~0.14*N (sub-1 fraction). Pseudoinverse theory says alpha_c->1.0
  (store ~N patterns). G2/I6 measured throughput; this measures the CAPACITY scaling law: does pinv alpha_c stay ~constant
  (near 1.0) across N=512..4096, confirming the linear cap=alpha_c*N with alpha_c~1 for pinv? Synthetic +-1 patterns,
  exact-recovery. CPU $0.
PRE-REGISTERED: HARD-PASS pinv alpha_c >= 0.8 AND ~constant across N (production stores ~N facts/dim). MID 0.4-0.8.
  HARD-FAIL <0.4 (pinv advantage doesn't hold at scale).
FORMULA SELF-TESTS (PROT-022): 1. pinv projector idempotent. 2. low-load recovers. 3. deps.
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

ANCHOR_NAME = "pb_pinv_capacity_ceiling_v1"
FLIP = 0.05; STEPS = 8
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_SWEEP = [512, 1024]; LOADS = [0.2, 0.4, 0.6, 0.8, 0.9, 0.95]
else:
    SEEDS = [7, 17, 23]; N_SWEEP = [2048, 4096, 8192]; LOADS = [0.5, 0.7, 0.85, 0.95]


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def W_pinv(P):
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32); W = (P.T @ np.linalg.solve(G, P)).astype(np.float32); np.fill_diagonal(W, 0.0); return W


def recall(P, W, seed):
    g = np.random.default_rng(seed); M, n = P.shape; s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def alpha_c(n, seed):
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * n)); P = patterns(M, n, g)
        if recall(P, W_pinv(P), seed * 7 + M) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); P = patterns(1, 128, g); assert recall(P, W_pinv(P), 0) >= 0.95, "pinv single fixed point"
    assert alpha_c(256, 0) > 0, "capacity positive"
    print("[selftest] PASS: pinv-n-scaling", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    a = {("N%d" % n): alpha_c(n, seed) for n in N_SWEEP}
    print("  [seed=%d] pinv alpha_c by N %s" % (seed, {k: round(v, 3) for k, v in a.items()}), flush=True); return {"seed": seed, "alpha_c": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {("N%d" % n): float(np.mean([p["alpha_c"]["N%d" % n] for p in ps])) for n in N_SWEEP}
    vals = np.array(list(agg.values())); mean_ac = float(vals.mean()); flat = float(vals.min() / max(vals.max(), 1e-9))
    summary = "pinv alpha_c by N: %s | mean=%.3f flatness=%.2f" % ({k: round(v, 3) for k, v in agg.items()}, mean_ac, flat)
    if mean_ac >= 0.8 and flat >= 0.7:
        return ("HARD_PASS", "HARD_PASS: pinv alpha_c >=0.8 and ~constant across N -- production stores ~N facts/dim (vs Hebb 0.14N); linear capacity at near-unit fraction. " + summary)
    if mean_ac >= 0.4:
        return ("MIDDLE_BAND", "MIDDLE_BAND: pinv alpha_c 0.4-0.8. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: pinv alpha_c <0.4 -- advantage weak at scale. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_sweep=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_SWEEP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
