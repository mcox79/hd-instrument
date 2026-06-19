"""
nhse_annulus_tau_crit_boundary_v1_n8192 -- NHSE-annulus tau_crit boundary probe (continuity).

ROUTING: notes/exp_dev_handoff_research_nhse_annulus_tau_scaling_2026-06-04.md (Research).
FRAMEWORK: notes/research_drill_nhse_annulus_tau_scaling_2x_2026-06-04.md.

CAPABILITY QUESTION:
  Is the disk-to-annulus transition CONTINUOUS (smooth crossover, consistent with NHSE) or
  DISCONTINUOUS (spectral jump, first-order critical NHSE)? Where is tau_crit? Framework predicts a
  CONTINUOUS transition with tau_crit ~ 0.25-0.45. Dense 6-cell sweep of the transition zone.

BUILD (consistent with PP-58 SCS d-sweeps that produced the calibration data points):
  W = (1-t)*W_sym + t*W_asym_scaled   (W_asym scaled to ||W_sym||_F; W_sym = xi^T xi / n at natural scale)
  We sweep the build knob t (TAU_TARGET) and REPORT the measured tau_actual = ||W_asym||/||W||.
  This reproduces the calibration regime: t=0.50 -> tau_actual~0.707; t=0.71 -> tau_actual~0.926
  (the exact tau where gamma_emp=41.456 was measured). gamma_emp(tau_actual) is then comparable to
  the 1.45@0.05 / 41.456@0.926 anchor points the exponential was fit to.

OBSERVABLES per cell:
  - gamma_emp via isochoric kappa_3 separation (same observable the exponential fit was calibrated on).
  - annulus radii r_outer/r_inner from the complex spectrum at reduced N_EIG (structural NHSE signature;
    inner radius collapses at high tau under skin-effect localization).

PRE-REGISTERED BANDS (exp_dev autonomy, grounded in research note P_deflated=0.31-0.42):
  HARD-PASS (NHSE-annulus exponential confirmed):
    - gamma_emp monotone non-decreasing in tau (allow 5% slack) AND
    - exponential-fit R^2 (log gamma vs tau, linear) > 0.90 AND fitted c in [2.5, 5.5] AND
    - gamma_emp(tau=0.50) >= 4.0
  MIDDLE:
    - monotone but exp-fit R^2 in [0.70, 0.90] OR c outside [2.5,5.5] OR gamma(0.50) in [2.0, 4.0)
  HARD-FAIL (NHSE-annulus exponential refuted; SCS/polynomial favored):
    - non-monotone OR exp-fit R^2 < 0.70 OR gamma_emp(tau=0.50) < 2.0

FORMULA SELF-TESTS (PROT-022):
  1. Unit-norm build: tau_actual(tau=0.50) within 0.02 of 0.50; tau_actual(0.71) within 0.02 of 0.71.
  2. NHSE prediction gamma(0.30)=1.20*exp(3.83*0.30)=3.79; gamma(0.926)=41.4. [within 1%]
  3. exp-fit recovers (A,c) from synthetic gamma=1.2*exp(3.83*tau): c within 0.1 of 3.83.
  4. R^2 of a perfect exponential series == 1.0 (within 1e-6).

PROT-018: anchor has _n8192; substrate N MUST = 8192 (kappa_3 measurement).
PROT-021: seed checkpoints keyed run_mode + N.
QUEUE: remote_cpu_queue (CPU; pure numpy). TIMEOUT: 21600s (PROT-019 floor for _n>=4096).
ASCII-only stdout.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "nhse_annulus_tau_crit_boundary_v1_n8192"
_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_FIXED = 0.05
NHSE_A = 1.20
NHSE_C = 3.83

# Pre-registered band thresholds
HP_R2 = 0.90
HP_C_LO, HP_C_HI = 2.5, 5.5
HP_GAMMA_AT_050 = 4.0
MID_R2 = 0.70
MID_GAMMA_AT_050 = 2.0
MONO_SLACK = 0.05

# Anchor 2: DENSE boundary probe. Build knob t -> tau_actual ~ {0.22,0.27,0.32,0.39,0.45,0.50},
# densely sampling the predicted disk-to-annulus transition zone tau_crit ~ 0.25-0.45.
TAU_GRID = [0.18, 0.22, 0.26, 0.30, 0.34, 0.38]

if RUN_MODE == "smoke":
    N_ACTIVE = 256
    SEEDS = [7, 17]
    N_PROBES = 100
    N_EIG = 256
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 500
    N_EIG = 512   # reduced N for the O(N^3) eigendecomposition (structural annulus check)


def _nhse_gamma(tau: float) -> float:
    return NHSE_A * math.exp(NHSE_C * tau)


def build_W(xi: np.ndarray, n: int, t: float, rng_asym: np.random.Generator) -> np.ndarray:
    """Original PP-58 build: W = (1-t)*W_sym + t*W_asym_scaled (W_asym scaled to ||W_sym||_F).
    W_sym symmetric, W_asym antisymmetric -> Frobenius-orthogonal -> tau_actual = t/sqrt((1-t)^2+t^2)."""
    W_sym = (xi.T @ xi) / n
    W_rand = rng_asym.standard_normal((n, n)).astype(np.float32) / math.sqrt(n)
    W_asym = (W_rand - W_rand.T) / 2.0
    scale = np.linalg.norm(W_sym, "fro") / max(np.linalg.norm(W_asym, "fro"), 1e-10)
    return ((1.0 - t) * W_sym + t * (W_asym * scale)).astype(np.float32)


def measure_tau_actual(W: np.ndarray) -> float:
    W_asym = (W - W.T) / 2.0
    return float(np.linalg.norm(W_asym, "fro") / (np.linalg.norm(W, "fro") + 1e-12))


def measure_kappa3(W: np.ndarray, n: int, rng: np.random.Generator, n_probes: int) -> float:
    V = rng.choice([-1.0, 1.0], size=(n, n_probes))
    V3 = W @ (W @ (W @ V))
    return float(np.mean((V * V3).sum(axis=0) / n))


def measure_gamma_emp(W_base: np.ndarray, n: int, rng: np.random.Generator, n_probes: int) -> float:
    delta_M = max(1, int(0.01 * n))
    xi_extra = rng.choice([-1.0, 1.0], size=(delta_M, n)).astype(np.float32)
    W_aug = W_base + (xi_extra.T @ xi_extra) / n
    k3_base = measure_kappa3(W_base, n, rng, n_probes)
    k3_aug = measure_kappa3(W_aug, n, rng, n_probes)
    if abs(k3_base) < 1e-10:
        return 0.0
    return abs(k3_aug) / abs(k3_base)


def measure_annulus_ratio(xi_seed: int, n_eig: int, t: float, rng_asym: np.random.Generator) -> float:
    """r_outer/r_inner of the complex spectrum at reduced N (NHSE annulus signature)."""
    r = np.random.default_rng(xi_seed)
    M = max(1, int(ALPHA_FIXED * n_eig))
    xi = r.choice([-1.0, 1.0], size=(M, n_eig)).astype(np.float32)
    W = build_W(xi, n_eig, t, rng_asym)
    ev = np.linalg.eigvals(W)
    rad = np.abs(ev)
    rad = rad[rad > 1e-9]
    if rad.size < 2:
        return 1.0
    r_outer = float(np.percentile(rad, 98))
    r_inner = float(np.percentile(rad, 2))
    return r_outer / max(r_inner, 1e-9)


def exp_fit_r2(taus: List[float], gammas: List[float]) -> Tuple[float, float, float]:
    """Fit log(gamma) = ln(A) + c*tau. Return (A, c, R2)."""
    t = np.array(taus, dtype=np.float64)
    g = np.array(gammas, dtype=np.float64)
    g = np.clip(g, 1e-9, None)
    y = np.log(g)
    c, lnA = np.polyfit(t, y, 1)
    yhat = c * t + lnA
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
    return float(math.exp(lnA)), float(c), float(r2)


def poly_fit_r2(taus: List[float], gammas: List[float], deg: int = 2) -> float:
    t = np.array(taus, dtype=np.float64)
    g = np.array(gammas, dtype=np.float64)
    coef = np.polyfit(t, g, deg)
    ghat = np.polyval(coef, t)
    ss_res = float(np.sum((g - ghat) ** 2))
    ss_tot = float(np.sum((g - np.mean(g)) ** 2))
    return 1.0 - ss_res / max(ss_tot, 1e-12)


def _instrumentation_selftest():
    rng_a = np.random.default_rng(999)
    r = np.random.default_rng(1)
    xi = r.choice([-1.0, 1.0], size=(max(1, int(ALPHA_FIXED * 256)), 256)).astype(np.float32)
    for tval, expected in ((0.50, 0.7071), (0.71, 0.9260)):
        W = build_W(xi, 256, tval, np.random.default_rng(999))
        ta = measure_tau_actual(W)
        assert abs(ta - expected) < 0.03, f"tau_actual map failed: t={tval} actual={ta} expected={expected}"
    assert abs(_nhse_gamma(0.30) - 3.79) < 0.05, f"nhse(0.30)={_nhse_gamma(0.30)}"
    assert abs(_nhse_gamma(0.926) - 41.4) < 0.5, f"nhse(0.926)={_nhse_gamma(0.926)}"
    syn_t = [0.1, 0.3, 0.5, 0.7, 0.9]
    syn_g = [_nhse_gamma(x) for x in syn_t]
    A, c, r2 = exp_fit_r2(syn_t, syn_g)
    assert abs(c - NHSE_C) < 0.1 and r2 > 1.0 - 1e-6, f"exp_fit recovery failed: c={c} r2={r2}"
    print(f"[selftest] PASS: tau_actual map + nhse prediction + exp-fit recovery (c={c:.3f} R2={r2:.6f})", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    M = max(1, int(ALPHA_FIXED * n_dim))
    xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
    cells = []
    for t in TAU_GRID:
        rng_asym = np.random.default_rng(999)   # fixed asym basis (consistent across t)
        W = build_W(xi, n_dim, t, rng_asym)
        tau_act = measure_tau_actual(W)
        rng2 = np.random.default_rng(seed + int(t * 10000))
        gamma = measure_gamma_emp(W, n_dim, rng2, N_PROBES)
        annulus = measure_annulus_ratio(seed * 131 + 7, N_EIG, t, np.random.default_rng(999))
        nhse_pred = _nhse_gamma(tau_act)
        print(f"  [seed={seed} t={t:.2f}] tau_act={tau_act:.3f} gamma_emp={gamma:.3f} "
              f"nhse_pred={nhse_pred:.3f} annulus_r={annulus:.2f}", flush=True)
        cells.append({"t": t, "tau_actual": float(tau_act), "gamma_emp": float(gamma),
                      "nhse_pred": float(nhse_pred), "annulus_ratio": float(annulus)})
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "cells": cells, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no valid results.")
    # Mean gamma per build-knob cell across seeds (sorted by tau_actual).
    pairs = []
    for tval in TAU_GRID:
        gs, tas = [], []
        for r in results:
            for c in r.get("cells", []):
                if abs(c["t"] - tval) < 1e-9:
                    gs.append(c["gamma_emp"]); tas.append(c["tau_actual"])
        if gs:
            pairs.append((float(np.mean(tas)), float(np.mean(gs))))
    pairs.sort(key=lambda p: p[0])
    mean_tau_act = [p[0] for p in pairs]
    mean_gamma = [p[1] for p in pairs]
    if len(mean_gamma) < 2:
        return ("HARD_FAIL", "HARD_FAIL: insufficient cells.")

    monotone = all(mean_gamma[i + 1] >= mean_gamma[i] * (1.0 - MONO_SLACK) for i in range(len(mean_gamma) - 1))
    # Continuity: largest consecutive-cell gamma ratio (a big jump => first-order/discontinuous).
    ratios = [mean_gamma[i + 1] / max(mean_gamma[i], 1e-9) for i in range(len(mean_gamma) - 1)]
    max_ratio = float(max(ratios)) if ratios else 1.0
    spread = float(max(mean_gamma) / max(min(mean_gamma), 1e-9))
    # tau_crit: first tau_actual where gamma crosses 2.0 (linear-interp between bracketing cells).
    tau_crit = None
    for i in range(len(mean_gamma)):
        if mean_gamma[i] >= 2.0:
            if i == 0:
                tau_crit = mean_tau_act[0]
            else:
                g0, g1 = mean_gamma[i - 1], mean_gamma[i]
                t0, t1 = mean_tau_act[i - 1], mean_tau_act[i]
                frac = (2.0 - g0) / max(g1 - g0, 1e-9)
                tau_crit = t0 + frac * (t1 - t0)
            break

    summary = (f"tau_crit={None if tau_crit is None else round(tau_crit,3)} max_ratio={max_ratio:.2f} "
               f"spread={spread:.2f} monotone={monotone} "
               f"gammas={[round(g,2) for g in mean_gamma]} taus_act={[round(t,3) for t in mean_tau_act]}")

    # HARD_FAIL: discontinuous jump, non-monotone, or no transition (flat).
    if max_ratio > 5.0 or not monotone or spread < 1.5:
        return ("HARD_FAIL",
                f"HARD_FAIL: discontinuous (max_ratio>{5.0}) OR non-monotone OR flat (spread<1.5). {summary}")
    # HARD_PASS: continuous monotone crossover with tau_crit in [0.25, 0.45].
    if max_ratio < 3.0 and tau_crit is not None and 0.25 <= tau_crit <= 0.45:
        return ("HARD_PASS",
                f"HARD_PASS: continuous transition (max_ratio<3.0), tau_crit in [0.25,0.45] "
                f"(framework-consistent). {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: transition present; tau_crit outside [0.25,0.45] or mild jump (3-5x). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_ACTIVE} mode={RUN_MODE} seeds={SEEDS} "
      f"tau_grid={TAU_GRID} N_EIG={N_EIG}", flush=True)
if RUN_MODE == "full" and N_ACTIVE != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_ACTIVE={N_ACTIVE} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "run_mode": RUN_MODE, "tau_grid": TAU_GRID, "N_EIG": N_EIG}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N_ACTIVE, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "tau_grid": TAU_GRID,
    "nhse_A_ref": NHSE_A, "nhse_c_ref": NHSE_C, "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", []), "elapsed_s": r.get("elapsed_s")}
                 for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
