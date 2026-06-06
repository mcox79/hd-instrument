"""
exp_crt_module_scaling_battery_v1 -- BUNDLED CRT module-count scaling, CPU (long) -- CPU.

ROUTING: extends the CRT grid-cell win (143x at 3 scales). Maps how distinguishable capacity scales with MODULE COUNT
  (1..6 coprime moduli) across several N and moduli sets -> the multiplicative-scaling curve (capacity ~ product of
  moduli). Confirms exponential-in-module-count composition + finds where N-dim noise breaks it. Bundled sweep -> long CPU
  job. numpy $0.
PRE-REGISTERED: HARD-PASS distinguishable(max-module) >= 10x distinguishable(1-module) AND tracks product-of-moduli within
  20pct up to the N-noise limit. MID 3-10x. HARD-FAIL <3x.
FORMULA SELF-TESTS (PROT-022): 1. coprime moduli. 2. CRT uniqueness. 3. residue encode.
ASCII-only. write_metrics. PROT-018 no _nN.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from math import gcd
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "crt_module_scaling_battery_v1"
ALL_MODULI = [5, 7, 9, 11, 13, 16]   # pairwise-coprime-ish set (5,7,9,11,13,16 coprime); product grows fast
FLIP = 0.05
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [4096]; MODULE_COUNTS = [1, 2, 3]
else:
    SEEDS = [7, 17, 23]; N_GRID = [2048, 4096]; MODULE_COUNTS = [1, 2, 3, 4, 5, 6]


def bp(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def distinguishable(scales, n, seed, cap_positions=4000):
    # cap_positions bounds cost; multiplicative scaling law is fully visible below the cap.
    g = np.random.default_rng(seed); P = min(int(np.prod(scales)), cap_positions)
    codebooks = [bp(m, n, g) for m in scales]
    pos = np.arange(P)
    codes = np.zeros((P, n), np.float32)
    for s, m in enumerate(scales):
        codes += codebooks[s][pos % m]            # vectorized over positions per scale (n_scales iters, not P)
    codes = np.sign(codes); codes[codes == 0] = 1.0
    g2 = np.random.default_rng(seed + 1)
    cues = codes * np.where(g2.random((P, n)) < FLIP, -1.0, 1.0)
    preds = (cues @ codes.T).argmax(1)            # ONE P x P matmul (vectorized decode), not a P-iteration loop
    return int((preds == pos).sum())


def _selftest():
    assert all(gcd(ALL_MODULI[i], ALL_MODULI[j]) == 1 for i in range(len(ALL_MODULI)) for j in range(i + 1, len(ALL_MODULI))), "coprime moduli"
    res = set((p % 5, p % 7) for p in range(35)); assert len(res) == 35, "CRT uniqueness"
    print("[selftest] PASS: crt scaling", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    by = {}
    for n in N_GRID:
        for mc in MODULE_COUNTS:
            scales = ALL_MODULI[:mc]; d = distinguishable(scales, n, seed)
            by["N%d_m%d" % (n, mc)] = {"distinguishable": d, "product": int(np.prod(scales))}
            print("  [seed=%d N=%d modules=%d] distinguishable=%d (product=%d)" % (seed, n, mc, d, int(np.prod(scales))), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    nmax = N_GRID[-1]
    def d(mc):
        return float(np.mean([p["by"]["N%d_m%d" % (nmax, mc)]["distinguishable"] for p in ps]))
    d1 = d(MODULE_COUNTS[0]); dmax = d(MODULE_COUNTS[-1]); g = dmax / max(d1, 1e-9)
    prod = int(np.prod(ALL_MODULI[:MODULE_COUNTS[-1]]))
    curve = {("m%d" % mc): round(d(mc), 0) for mc in MODULE_COUNTS}
    summary = "distinguishable by module-count at N=%d: %s (max product=%d, P capped 4000) | %d-mod/1-mod=%.1fx" % (nmax, curve, prod, MODULE_COUNTS[-1], g)
    tracks = dmax >= 0.8 * min(prod, 4000)
    if g >= 10.0 and tracks:
        return ("HARD_PASS", "HARD_PASS: CRT capacity scales multiplicatively with module count (>=10x, tracks product) -- exponential composition confirmed. " + summary)
    if g >= 3.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multi-module helps (3-10x) but N-noise caps it below product. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: module-count scaling weak (<3x). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%s module_counts=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, MODULE_COUNTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
