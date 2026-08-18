"""
population_coding_3seed_CG_lift_v1.py -- 3-seed cross-witness of N=100 substrate ensemble noise robustness -- CPU.

ROUTING: Research Stage-1 MM->CG lift for lap3_7_n100_ensemble_cpu_v1. Same regime as parent
(N_DIM=512, M=90, VV=100, NOISE=2.6, TR=120 full / 20 smoke, P=100 substrates), sweep seeds [7,13,19]
and verify ensemble lift >= 20pp across ALL seeds with cv < 10%.
PRE-REGISTERED:
  HARD_PASS: min gain100_pp>=20 AND cv(gain100_pp)<0.10 across seeds [7,13,19]
  MIDDLE_BAND: min gain>=10 OR (min>=20 AND cv 0.10-0.20)
  HARD_FAIL: min gain<10 OR cv>=0.20
CARDINALITY_OK: EXPECTED_N_SEEDS=3 (SEEDS=[7,13,19]); HARD_FAIL_CARDINALITY_BREACH if observed<3.
DISCRIMINATOR-AT-SCALE: parent HP at same regime (single-seed 249); mechanism is variance-averaging
so cross-seed stability is intrinsic; smoke at full-grid (TR=20) verifies lift direction survives.
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
ANCHOR_NAME = "population_coding_3seed_CG_lift_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SEEDS = [7, 13, 19]
EXPECTED_N_SEEDS = 3

def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    # Vote sanity
    import numpy as _n
    assert _n.bincount([2, 2, 1]).argmax() == 2, "vote"
    # CV formula sanity: cv = std/mean; on [20,22,24] -> mean=22, std_pop=sqrt(8/3)~1.633, cv~0.0742
    vals = _n.array([20.0, 22.0, 24.0])
    cv_measured = float(vals.std() / vals.mean())
    cv_expected = 1.632993161855452 / 22.0
    assert abs(cv_measured - cv_expected) < 1e-6, "cv=%.6f expected=%.6f" % (cv_measured, cv_expected)
    print("[selftest] PASS: 3seed-pop-coding cv=%.4f" % cv_measured, flush=True)

def run_one_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); N = 512; M = 90; VV = 100; NOISE = 2.6
    TR = 20 if SMOKE else 120; single = 0; ens10 = 0; ens100 = 0; n = 0
    for _ in range(TR):
        truth = g.integers(0, VV, size=M); P = 100
        subs = []
        for p in range(P):
            keys = cphasor(M, N, g); vals = cphasor(VV, N, g); Mem = (keys * vals[truth]).sum(axis=0); subs.append((keys, vals, Mem))
        qi = int(g.integers(0, M)); votes = []
        for (keys, vals, Mem) in subs:
            noisy = Mem * np.conj(keys[qi]) + NOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            votes.append(cidx(noisy, vals))
        single += int(votes[0] == truth[qi])
        ens10 += int(np.bincount(votes[:10]).argmax() == truth[qi])
        ens100 += int(np.bincount(votes).argmax() == truth[qi]); n += 1
    sa = single / n; e10 = ens10 / n; e100 = ens100 / n
    gain = round((e100 - sa) * 100, 1)
    print("  [seed=%d] single=%.3f ens10=%.3f ens100=%.3f gain100=%.1fpp n=%d" % (seed, sa, e10, e100, gain, n), flush=True)
    return {"seed": seed, "single": sa, "ens10": e10, "ens100": e100, "gain100_pp": gain}

def run() -> Dict:
    per_seed_rows = [run_one_seed(s) for s in SEEDS]
    gains = np.array([r["gain100_pp"] for r in per_seed_rows], dtype=np.float64)
    mean_gain = float(gains.mean()); std_gain = float(gains.std()); min_gain = float(gains.min()); max_gain = float(gains.max())
    cv = float(std_gain / mean_gain) if mean_gain > 0 else float("inf")
    print("  [cross-seed] min=%.1fpp max=%.1fpp mean=%.1fpp std=%.2fpp cv=%.4f n_seeds=%d" % (min_gain, max_gain, mean_gain, std_gain, cv, len(per_seed_rows)), flush=True)
    return {"per_seed_rows": per_seed_rows, "min_gain_pp": min_gain, "max_gain_pp": max_gain, "mean_gain_pp": mean_gain, "std_gain_pp": std_gain, "cv_gain": cv, "n_seeds_observed": len(per_seed_rows)}

def verdict(r) -> Tuple[str, str]:
    n_obs = r["n_seeds_observed"]
    if n_obs < EXPECTED_N_SEEDS:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH: observed=%d expected=%d seeds" % (n_obs, EXPECTED_N_SEEDS))
    s = "min=%.1fpp max=%.1fpp mean=%.1fpp cv=%.3f seeds=%s" % (r["min_gain_pp"], r["max_gain_pp"], r["mean_gain_pp"], r["cv_gain"], SEEDS)
    if r["min_gain_pp"] >= 20.0 and r["cv_gain"] < 0.10:
        return ("HARD_PASS", "HARD_PASS: N=100 substrate ensemble lifts noisy-recall by >=20pp across ALL 3 seeds [7,13,19] with cv<10% -- sqrt-N population-coding is cross-seed stable; lifts MM->CG for lap3_7_n100_ensemble. " + s)
    if r["min_gain_pp"] >= 10.0 or (r["min_gain_pp"] >= 20.0 and r["cv_gain"] < 0.20):
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial 3-seed lift. " + s)
    return ("HARD_FAIL", "HARD_FAIL: min gain<10pp or cv>=0.20. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r["n_seeds_observed"], "expected_n_seeds": EXPECTED_N_SEEDS, "per_seed": r["per_seed_rows"], "cross_seed": {"min_gain_pp": r["min_gain_pp"], "max_gain_pp": r["max_gain_pp"], "mean_gain_pp": r["mean_gain_pp"], "std_gain_pp": r["std_gain_pp"], "cv_gain": r["cv_gain"]}, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, r["per_seed_rows"]); print("[metrics] written", flush=True)
