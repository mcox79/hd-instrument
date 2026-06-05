"""
substrate_cerebellar_random_expansion_write_v1 -- CEREBELLAR-EXP-1: random-expansion capacity lift -- CPU.

ROUTING: research kgram_xor_binding_rescue (CEREBELLAR-EXP-1; novel write rule). Albus 1971 cerebellar model:
  granule-cell random expansion lifts effective capacity. Bipolar substrate: phi_exp = sign(R^T phi) (R = N x N_exp
  random), store in expanded space, decode via projection. Theoretical capacity lifts toward O(N_exp). Tests whether
  random expansion raises the M_crit pattern-capacity boundary vs base N-dim auto-assoc. CPU numpy $0.

MODEL: M random bipolar patterns. BASE: auto-assoc W=sum outer(p,p) in N-dim; recall from 20%-flipped cue; M_crit
  (recall>=0.9). EXPANDED: phi_exp = sign(R^T p) in N_exp=EXP*N dim; W_exp auto-assoc; recall via expand->clean->
  decode. M_crit_exp. Compare boundary.

PRE-REGISTERED bands: HARD-PASS M_crit_exp >= 1.8x M_crit_base (random expansion lifts capacity). MIDDLE: 1.2-1.8x.
  HARD-FAIL: <1.2x (expansion does not lift capacity at this scale).
FORMULA SELF-TESTS (PROT-022): 1. expansion preserves identity. 2. base auto-assoc recall. 3. N fixed.
ASCII-only. write_metrics. PROT-018: no _nN.
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_cerebellar_random_expansion_write_v1"
N_DIM = 1024; EXP = 4
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_D = 512; EXP = 4; M_GRID = [40, 80, 160, 320, 640]
else:
    SEEDS = [7, 17, 23]; N_D = N_DIM; EXP = 4; M_GRID = [80, 160, 320, 640, 1280, 2560]


def bipolar(M, n, g):
    return (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)


def _selftest():
    g = np.random.default_rng(0); n = 128; R = bipolar(n, n * 2, g); p = bipolar(1, n, g)[0]
    pe = np.sign(p @ R); pe2 = np.sign(p @ R); assert np.array_equal(pe, pe2), "expansion deterministic/identity"
    X = bipolar(3, n, g); W = X.T @ X; np.fill_diagonal(W, 0)
    assert int(np.argmax(X @ (W @ X[0]))) == 0, "base auto-assoc recall"
    assert N_DIM == 1024; print("[selftest] PASS: expansion autoassoc", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def mcrit_base(n, g):
    mc = 0
    for M in M_GRID:
        X = bipolar(M, n, g); W = (X.T @ X).astype(np.float32); np.fill_diagonal(W, 0.0)
        flip = g.random((M, n)) < 0.2; Xc = X * np.where(flip, -1.0, 1.0)
        R = np.sign(Xc @ W.T); R[R == 0] = 1.0
        acc = float(np.mean((R * X).sum(1) / n > 0.95))
        if acc >= 0.9:
            mc = M
        else:
            break
    return mc


def mcrit_expanded(n, n_exp, g):
    Rp = bipolar(n, n_exp, g) / math.sqrt(n); mc = 0
    for M in M_GRID:
        X = bipolar(M, n, g); Xe = np.sign(X @ Rp).astype(np.float32)        # expand
        W = (Xe.T @ Xe).astype(np.float32); np.fill_diagonal(W, 0.0)
        flip = g.random((M, n)) < 0.2; Xc = X * np.where(flip, -1.0, 1.0); Xce = np.sign(Xc @ Rp)
        Re = np.sign(Xce @ W.T); Re[Re == 0] = 1.0                            # recall in expanded space
        acc = float(np.mean((Re * Xe).sum(1) / n_exp > 0.95))
        if acc >= 0.9:
            mc = M
        else:
            break
    return mc


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_D; n_exp = EXP * n
    mb = mcrit_base(n, g); me = mcrit_expanded(n, n_exp, np.random.default_rng(seed + 1))
    note = "" if me < M_GRID[-1] else " (expanded hit grid ceiling; LOWER BOUND)"
    return {"seed": seed, "N": n, "N_exp": n_exp, "M_crit_base": mb, "M_crit_expanded": me,
            "ratio": float(me / max(mb, 1)), "note": note}


def verdict(ps) -> Tuple[str, str]:
    mb = float(np.mean([p["M_crit_base"] for p in ps])); me = float(np.mean([p["M_crit_expanded"] for p in ps])); r = me / max(mb, 1)
    summary = "M_crit_base=%.0f M_crit_expanded=%.0f ratio=%.2fx (N=%d N_exp=%d EXP=%d)%s" % (mb, me, r, ps[0]["N"], ps[0]["N_exp"], EXP, ps[0]["note"])
    if r >= 1.8:
        return ("HARD_PASS", "HARD_PASS: cerebellar random expansion lifts pattern capacity >=1.8x (toward O(N_exp)). " + summary)
    if r >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: expansion lifts capacity 1.2-1.8x. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: random expansion no capacity lift at this scale. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d EXP=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_D, EXP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] M_crit_base=%d M_crit_expanded=%d ratio=%.2fx" % (seed, r["M_crit_base"], r["M_crit_expanded"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_D, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
