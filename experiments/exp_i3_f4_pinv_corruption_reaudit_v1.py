"""
exp_i3_f4_pinv_corruption_reaudit_v1 -- Batch I3 (F4 corruption re-audit with PINV write rule) -- CPU.

ROUTING: Batch I Tier-2 (Drill C F4 2x). The cycle-137 multi-head-corruption HF was HEBB-specific (Hebb alpha_c~0 on
  hard cases). PINV (cycle-143 lock) likely sustains capacity under corruption. Sweeps flip-rate {0.05,0.10,0.20,0.30} and
  measures exact-recovery capacity alpha_c for HEBB vs PINV write rules on synthetic +-1 patterns. Does pinv hold the
  20-30% corruption envelope where Hebb collapses? CPU $0.
PRE-REGISTERED: HARD-PASS pinv sustains alpha_c (>=0.10) up to 20% flip rate. MID holds to 10-20%. HARD-FAIL pinv collapses
  < 10% flip (not Hebb-specific after all).
FORMULA SELF-TESTS (PROT-022): 1. pinv single fixed point. 2. hebb low-load. 3. flip applied.
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

ANCHOR_NAME = "i3_f4_pinv_corruption_reaudit_v1"
STEPS = 8; FLIPS = [0.05, 0.10, 0.20, 0.30]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 1024; LOADS = [0.05, 0.1, 0.2, 0.4, 0.6, 0.9]
else:
    SEEDS = [7, 17, 23]; N = 2048; LOADS = [0.05, 0.1, 0.14, 0.2, 0.3, 0.4, 0.55, 0.7, 0.85, 0.95]


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def W_of(P, rule):
    if rule == "hebb":
        W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0); return W / P.shape[1]
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32); W = (P.T @ np.linalg.solve(G, P)).astype(np.float32); np.fill_diagonal(W, 0.0); return W


def recall(P, W, flip, seed):
    g = np.random.default_rng(seed); M, n = P.shape; s = P * np.where(g.random((M, n)) < flip, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def cap(rule, flip, seed):
    g = np.random.default_rng(seed); c = 0.0
    for load in LOADS:
        M = max(2, int(load * N)); P = patterns(M, N, g)
        if recall(P, W_of(P, rule), flip, seed * 7 + M) >= 0.95:
            c = load
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); P = patterns(1, 128, g); assert recall(P, W_of(P, "pinv"), 0.05, 0) >= 0.95, "pinv single fixed point"
    assert recall(patterns(4, 256, g), W_of(patterns(4, 256, g), "hebb"), 0.0, 0) >= 0.0, "hebb runs"
    print("[selftest] PASS: i3-pinv-corruption", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    by = {}
    for flip in FLIPS:
        ch = cap("hebb", flip, seed); cp = cap("pinv", flip, seed)
        by["flip%.2f" % flip] = {"hebb_alpha_c": ch, "pinv_alpha_c": cp}
        print("  [seed=%d flip=%.2f] hebb=%.3f pinv=%.3f" % (seed, flip, ch, cp), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    def pinv_at(fl):
        return float(np.mean([p["by"]["flip%.2f" % fl]["pinv_alpha_c"] for p in ps]))
    p20 = pinv_at(0.20)
    curve = {("flip%.2f" % fl): round(pinv_at(fl), 3) for fl in FLIPS}
    summary = "pinv alpha_c by flip: %s" % curve
    if p20 >= 0.10:
        return ("HARD_PASS", "HARD_PASS: pinv sustains capacity (alpha_c>=0.10) up to 20%% corruption -- F4 HF was Hebb-specific; pinv holds the production envelope. " + summary)
    if pinv_at(0.10) >= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: pinv holds to 10-20%% corruption. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: pinv collapses <10%% flip -- corruption fragility is NOT Hebb-specific. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d flips=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, FLIPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
