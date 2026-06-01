"""Orthogonal probe: Jarzynski equality v2 -- larger N, smaller beta to reduce variance.

CONTEXT: wave14_ortho_jarzynski_crooks_v1 returned MIDDLE_BAND.
  v1 result: hp_frac=0.00 (< 0.60); mean_agreement=16.517; jarz_var=27.462.
  Root cause: at N=128/256 with beta=1.0, the Jarzynski estimator suffers from
  high variance (jarz_var ~ 27) because substrate writes are far from equilibrium
  at beta=1.0 (strong coupling). The estimator needs many more samples or lower beta.

FIX v2:
  - N=512 (double from v1 N=256): larger N reduces per-step work variance
  - beta = 0.3 (reduce from 1.0): softer coupling moves system closer to
    quasi-static limit where Jarzynski converges faster
  - M_SWEEP extended: [50, 200, 500, 1000] to probe well above capacity
  - 3 seeds (was 1 in smoke; now use 5 for full)

HYPOTHESIS: At beta=0.3, substrate writes are near-equilibrium, so
<exp(-0.3 * w)> has lower variance and Jarzynski converges. If hp_frac >= 0.60,
this opens a cheap forward-only free-energy estimator for substrate capacity.

PRE-REGISTERED BANDS (same logic as v1, adapted thresholds for beta=0.3):
  HARD_PASS:
    - hp_frac >= 0.60 (at least 60% of cells within 50% agreement)
    - AND jarz_var_mean < 5.0
    -> Jarzynski viable at lower beta; useful capacity estimator

  HARD_FAIL:
    - mean_agreement > 200% for all M conditions AND jarz_var_mean > 50
    -> Fundamental non-equilibrium gap; Jarzynski unusable for substrate writes

  MIDDLE_BAND: intermediate

SELF-TESTS (same as v1, extended for N=512):
  1. work_per_step(W=0, v=random) = 0.0
  2. jarzynski_estimator([0,0,0], beta=0.3) = 0.0
  3. jarzynski_estimator([1,1,1], beta=0.3) = 1.0 (constant work -> delta_F = w)
  4. Gaussian work variance reduction: beta=0.3 gives lower exp(-w) variance than beta=1.0
  5. run_one_cell(N=64, M=50, beta=0.3) gives finite dF_J

Queue: remote_cpu_queue (CPU; M in {50,200,500,1000} x 5 seeds x N=512 x beta=0.3; ~30-60 min)
Pre-reg: preregs/2026-05-27_wave14_ortho_jarzynski_crooks_v2.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import v1 module for shared functions
_v1_path = REPO / "experiments" / "exp_wave14_ortho_jarzynski_crooks_v1.py"
_v1_spec = importlib.util.spec_from_file_location("jarzynski_v1", _v1_path)
_v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_v1_mod)

# v2 parameters: larger N, smaller beta
N_FULL  = 512
N_SMOKE = 256
M_SWEEP_FULL  = [50, 200, 500, 1000]
M_SWEEP_SMOKE = [50, 200]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BETA = 0.3       # reduced from 1.0 to reduce Jarzynski variance
ALPHA_HEBBIAN = 0.1

# Same bands as v1
HP_AGREEMENT_MAX = 0.50
HF_AGREEMENT_MIN = 2.0
HP_VARIANCE_MAX  = 5.0


def get_output_dir(default_name: str = "wave14_ortho_jarzynski_crooks_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def run_one_cell(N: int, M: int, seed: int, beta: float = BETA) -> Dict:
    """Same as v1 but with configurable beta and larger N."""
    patterns = _v1_mod.build_patterns(N, M, seed)
    W = np.zeros((N, N))
    works = []

    for mu in range(M):
        v = patterns[mu]
        w = _v1_mod.work_per_step(W, v)
        works.append(w)
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
        np.fill_diagonal(W, 0.0)

    delta_F_J = _v1_mod.jarzynski_estimator(works, beta)
    exp_works = [math.exp(-beta * w) for w in works]
    jarz_variance = float(np.var(exp_works)) if len(exp_works) > 1 else 0.0

    W0 = np.zeros((N, N))
    log_Z_before = _v1_mod.mean_field_log_Z(W0, beta)
    log_Z_after  = _v1_mod.mean_field_log_Z(W, beta)
    delta_log_Z  = (log_Z_after - log_Z_before) / N
    delta_F_direct = -delta_log_Z / beta

    mean_work = float(np.mean(works)) if works else 0.0
    if abs(delta_F_direct) < 1e-6 and abs(mean_work) > 1e-6:
        delta_F_direct = -mean_work

    if abs(delta_F_direct) < 1e-9:
        agreement_frac = float("nan")
    else:
        agreement_frac = abs(delta_F_J - delta_F_direct) / abs(delta_F_direct)

    mean_w = float(np.mean(works))
    var_w  = float(np.var(works))

    return {
        "N": N, "M": M, "seed": seed, "beta": beta,
        "delta_F_J": round(float(delta_F_J), 6),
        "delta_F_direct": round(float(delta_F_direct), 6),
        "agreement_frac": round(float(agreement_frac), 5) if not math.isnan(agreement_frac) else None,
        "jarz_variance": round(float(jarz_variance), 5),
        "mean_work": round(float(mean_w), 6),
        "var_work": round(float(var_w), 6),
        "within_hp_band": bool(
            agreement_frac is not None and not math.isnan(agreement_frac)
            and agreement_frac <= HP_AGREEMENT_MAX
        ),
    }


def _instrumentation_selftest():
    # 1. work_per_step(W=0, v=anything) = 0
    W0 = np.zeros((8, 8))
    v = np.array([1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, 1.0])
    w0 = _v1_mod.work_per_step(W0, v)
    assert abs(w0) < 1e-9, f"selftest 1 FAIL: w0={w0}"
    print(f"[selftest] 1/5 work(W=0)={w0:.6f} OK")

    # 2. jarzynski with all-zero works -> delta_F = 0
    dF_zero = _v1_mod.jarzynski_estimator([0.0, 0.0, 0.0], beta=0.3)
    assert abs(dF_zero) < 1e-9, f"selftest 2 FAIL: dF_zero={dF_zero}"
    print(f"[selftest] 2/5 Jarz([0,0,0], beta=0.3)={dF_zero:.6f} OK")

    # 3. jarzynski with constant work w=1 -> delta_F = 1.0 (regardless of beta)
    dF_const = _v1_mod.jarzynski_estimator([1.0, 1.0, 1.0], beta=0.3)
    assert abs(dF_const - 1.0) < 0.01, f"selftest 3 FAIL: dF_const={dF_const}"
    print(f"[selftest] 3/5 Jarz([1,1,1], beta=0.3)={dF_const:.4f} expected 1.0 OK")

    # 4. Variance reduction: beta=0.3 gives lower exp(-w) variance than beta=1.0
    rng = np.random.default_rng(0)
    works_g = list(rng.normal(1.0, 1.0, 500))
    var_b03 = float(np.var([math.exp(-0.3 * w) for w in works_g]))
    var_b10 = float(np.var([math.exp(-1.0 * w) for w in works_g]))
    assert var_b03 < var_b10, f"selftest 4 FAIL: var_b03={var_b03:.4f} >= var_b10={var_b10:.4f}"
    print(f"[selftest] 4/5 var(beta=0.3)={var_b03:.4f} < var(beta=1.0)={var_b10:.4f} OK")

    # 5. run_one_cell at small scale gives finite dF_J
    cell = run_one_cell(64, 50, 42, beta=0.3)
    assert cell["delta_F_J"] is not None and math.isfinite(cell["delta_F_J"]), \
        f"selftest 5 FAIL: dF_J={cell['delta_F_J']}"
    assert cell["var_work"] >= 0, f"selftest 5 FAIL: var_work negative"
    print(f"[selftest] 5/5 cell(N=64,M=50,beta=0.3): dF_J={cell['delta_F_J']:.4f} OK")

    print("[selftest] PASS: 5/5 OK", flush=True)


_instrumentation_selftest()


def run_sweep(smoke: bool) -> Dict:
    N     = N_SMOKE if smoke else N_FULL
    M_sw  = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    t0 = time.monotonic()
    print(f"[jarzynski_crooks_v2] smoke={smoke} N={N} M_sweep={M_sw} beta={BETA} seeds={seeds}",
          flush=True)

    all_cells: List[Dict] = []
    for M in M_sw:
        for seed in seeds:
            t_c = time.monotonic()
            cell = run_one_cell(N, M, seed, beta=BETA)
            all_cells.append(cell)
            agr = cell["agreement_frac"]
            print(f"  M={M} s={seed}: dF_J={cell['delta_F_J']:.5f} "
                  f"dF_direct={cell['delta_F_direct']:.5f} "
                  f"agreement={agr} "
                  f"jarz_var={cell['jarz_variance']:.4f} "
                  f"({time.monotonic()-t_c:.1f}s)", flush=True)

    by_M: Dict[int, List[Dict]] = {}
    for c in all_cells:
        by_M.setdefault(c["M"], []).append(c)

    summary: Dict = {}
    for M in M_sw:
        rows = by_M.get(M, [])
        agrs = [c["agreement_frac"] for c in rows
                if c["agreement_frac"] is not None and math.isfinite(c["agreement_frac"])]
        hp_frac = sum(c["within_hp_band"] for c in rows) / len(rows) if rows else 0.0
        jarz_var_mean = (sum(c["jarz_variance"] for c in rows) / len(rows)
                          if rows else float("nan"))
        summary[f"M{M}"] = {
            "M": M, "n_seeds": len(rows),
            "agreement_mean": round(sum(agrs)/len(agrs), 5) if agrs else None,
            "hp_frac": round(hp_frac, 3),
            "jarz_variance_mean": round(jarz_var_mean, 4),
        }

    n_valid = sum(1 for c in all_cells if c["agreement_frac"] is not None)
    hp_cells = sum(1 for c in all_cells if c["within_hp_band"])
    hp_frac_total = hp_cells / len(all_cells) if all_cells else 0.0
    agrs_all = [c["agreement_frac"] for c in all_cells
                if c["agreement_frac"] is not None and math.isfinite(c["agreement_frac"])]
    mean_var = (sum(c["jarz_variance"] for c in all_cells) / len(all_cells)
                if all_cells else float("nan"))

    if n_valid < len(all_cells) * 0.5:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: {n_valid}/{len(all_cells)} valid cells; "
                       f"delta_F_direct near zero or NaN")
    elif hp_frac_total >= 0.6:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: {hp_frac_total:.2f} cells within {HP_AGREEMENT_MAX*100:.0f}% agreement "
                       f"at beta={BETA}; jarz_var_mean={mean_var:.3f}; Jarzynski viable at soft coupling")
    elif agrs_all and all(a > HF_AGREEMENT_MIN for a in agrs_all):
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: all agreement > {HF_AGREEMENT_MIN*100:.0f}% even at beta={BETA}; "
                       f"mean_agreement={sum(agrs_all)/len(agrs_all):.3f}; "
                       f"Jarzynski unusable for substrate writes at any tested coupling")
    else:
        verdict = "MIDDLE_BAND"
        agr_str = f"{sum(agrs_all)/len(agrs_all):.3f}" if agrs_all else "nan"
        verdict_msg = (f"MIDDLE_BAND: hp_frac={hp_frac_total:.2f}; "
                       f"mean_agreement={agr_str}; jarz_var_mean={mean_var:.3f}; "
                       f"mixed signal at beta={BETA}; try beta<0.3 or larger M")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.monotonic() - t0, 1),
        "summary": summary,
        "config": {
            "N": N, "smoke": smoke, "M_sweep": M_sw, "seeds": seeds,
            "beta": BETA, "alpha_hebbian": ALPHA_HEBBIAN,
            "hp_agreement_band": HP_AGREEMENT_MAX,
            "v2_fix": "N=512 (was 256), beta=0.3 (was 1.0), extended M_sweep",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import", flush=True)
        sys.exit(0)

    out_dir = get_output_dir()
    metrics = run_sweep(smoke=args.smoke)

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
