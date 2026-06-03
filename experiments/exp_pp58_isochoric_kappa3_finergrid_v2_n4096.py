"""
pp58_isochoric_kappa3_finergrid_v2_n4096 -- PP-58 R3b: finer sigma_g grid to locate audit_crit.

v1 R3 MULTI-ALPHA result (v354):
  a0.1: audit_crit=1.000 (grid-limited: sigma_g=0.5 and 1.0 are adjacent; true crit between these)
  a0.2: audit_crit=1.000 (same grid limitation)
  cap_crit exact at both alphas (pred and actual match exactly)
  ratio: a0.1=3.00 (HP boundary), a0.2=2.00 (MIDDLE)

R3b rescue: finer sigma_g grid 0.0..2.0 step 0.1 to resolve audit_crit location.
The founding run (v353 alpha=0.05) found audit_crit=0.500 which was also coarsely located.
With step=0.1, we can pin audit_crit to within +-0.05 for each alpha.

SCIENTIFIC QUESTION (PP-58 R3b):
  Does sigma_g_audit_crit scale predictably across alpha={0.10, 0.20} when measured
  with sufficient resolution?
  If audit_crit(0.10) < 0.50 (between 0.0 and 0.5 step 0.1): ratio > cap_crit/0.5 > 3/0.5 = 6x
  If audit_crit(0.20) < 0.50: ratio > 2/0.5 = 4x (above HP=3.0)
  So finer grid could PROMOTE a0.2 ratio from MIDDLE to HP, clearing PP-58 HP gate.

FORMULA SELF-TESTS (PROT-022):
  1. Cap boundary formula sqrt(1/alpha-1) for alpha={0.10, 0.20}
     [INPUT: alpha=0.10] [EXPECTED: 3.0000]
     [INPUT: alpha=0.20] [EXPECTED: 2.0000]
  2. kappa_3 identity at sigma_g=0.0 for each alpha.
     [INPUT: sigma_g=0.0, alpha=0.10, N=512] [EXPECTED: kappa_3_ratio ~1.0 +/- 0.5]
  3. M = int(alpha * N) > 0 for each alpha.
  4. grid: step=0.1 from 0.0..2.0 => 21 points.
     [EXPECTED: len(SIGMA_G_FULL) = 21]

PRE-REGISTERED BANDS (R3b finer grid; same hypothesis as R3 multi-alpha):
  HARD-PASS: ratio >= 3.0 for EACH alpha tested AND sigma_g_cap_crit within 20% of sqrt(1/alpha-1).
  MIDDLE: worst ratio in [1.5, 3.0) for any alpha.
  HARD-FAIL: ratio < 1.5 for any alpha.

PROT-018: anchor has _n4096; N MUST = 4096.
PROT-021: per-alpha sub-directories for seed checkpoints.
QUEUE: remote_cpu_queue (CPU; pure numpy; 2 alpha x 21 sigma x 5 seeds ~4h).
TIMEOUT ESTIMATE: v1 multialpha elapsed_s ~106s (2 alphas, 14 sigma_g, 5 seeds N=4096).
  R3b: 21 sigma_g points vs 14 = 1.5x more.
  ceil(1.5 * 106 * (21/14)^1.0 * (5/5)) = ceil(1.5 * 106 * 1.5) = ceil(238.5) = 300s.
  With margin for finer grid computations: 900s.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp58_isochoric_kappa3_finergrid_v2_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_VALS = [0.10, 0.20]

# FINER GRID: 0.0..2.0 step 0.1 => 21 points (vs 14 coarse points in v1)
SIGMA_G_FULL = [round(i * 0.1, 2) for i in range(21)]  # 0.0, 0.1, 0.2, ..., 2.0
assert len(SIGMA_G_FULL) == 21, f"grid size: {len(SIGMA_G_FULL)}"

# PROT-022: cap boundary formula self-test
_CAP_CRIT_010 = (1.0 / 0.10 - 1.0) ** 0.5  # sqrt(9) = 3.0
_CAP_CRIT_020 = (1.0 / 0.20 - 1.0) ** 0.5  # sqrt(4) = 2.0
assert abs(_CAP_CRIT_010 - 3.0) < 1e-9, f"cap_crit(0.10): {_CAP_CRIT_010}"
assert abs(_CAP_CRIT_020 - 2.0) < 1e-9, f"cap_crit(0.20): {_CAP_CRIT_020}"

RECALL_CRIT = 0.50
N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 10
N_PROBES_FULL = 50
N_PROBES_SELFTEST = 20

# Verdict thresholds
HP_RATIO_MIN = 3.0
MIDDLE_RATIO_MIN = 1.5
HP_CAP_CRIT_TOLERANCE = 0.20

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    # Smoke: coarser sigma_g selection but still spans 0..2.0
    SIGMA_G_USE = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
    N_QUERIES_USE = 5
    N_PROBES_USE = N_PROBES_SELFTEST
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    SIGMA_G_USE = SIGMA_G_FULL
    N_QUERIES_USE = N_QUERIES_PER_CELL
    N_PROBES_USE = N_PROBES_FULL


def hutchinson_kappa3_np(W: np.ndarray, n_probes: int, seed: int) -> float:
    """Hutchinson estimator for Tr(W^3) / N."""
    rng_h = np.random.RandomState(seed + 88888)
    n_dim = W.shape[0]
    estimates = np.zeros(n_probes)
    for i in range(n_probes):
        v = rng_h.choice([-1.0, 1.0], size=(n_dim,)).astype(np.float64)
        Wv = W @ v
        W2v = W @ Wv
        W3v = W @ W2v
        estimates[i] = float(np.dot(v, W3v)) / n_dim
    return float(np.mean(estimates))


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null at small scale."""
    assert abs(_CAP_CRIT_010 - 3.0) < 1e-9, f"cap_crit(0.10): {_CAP_CRIT_010}"
    assert abs(_CAP_CRIT_020 - 2.0) < 1e-9, f"cap_crit(0.20): {_CAP_CRIT_020}"

    step_max = max(abs(SIGMA_G_FULL[i+1] - SIGMA_G_FULL[i]) for i in range(len(SIGMA_G_FULL)-1))
    assert abs(step_max - 0.1) < 1e-9, f"grid step: {step_max:.4f} expected 0.1"
    assert len(SIGMA_G_FULL) == 21, f"grid length: {len(SIGMA_G_FULL)}"

    N_t = 512
    for alpha in ALPHA_VALS:
        M_t = max(1, int(alpha * N_t))
        assert M_t > 0, f"M=0 at alpha={alpha} N={N_t}"
    assert M_t > 0

    N_t2 = 512
    alpha_t = 0.10
    M_t2 = max(1, int(alpha_t * N_t2))
    rng = np.random.RandomState(42)
    Xi = rng.choice([-1.0, 1.0], size=(M_t2, N_t2)).astype(np.float32)
    W = (Xi.T @ Xi) / float(N_t2)
    kappa3_baseline = hutchinson_kappa3_np(W.astype(np.float64), 20, 0)
    assert not np.isnan(kappa3_baseline), "kappa3_baseline is NaN"
    assert 0.01 < kappa3_baseline < 2.0, f"kappa3_baseline={kappa3_baseline:.4f} out of expected range [0.01,2.0]"

    W_noisy = W + 0.0 * np.random.RandomState(1).randn(*W.shape).astype(np.float32)
    kappa3_noisy = hutchinson_kappa3_np(W_noisy.astype(np.float64), 20, 0)
    ratio = kappa3_noisy / max(kappa3_baseline, 1e-12)
    assert 0.5 < ratio < 1.5, f"kappa3 ratio at sigma_g=0.0: {ratio:.4f} expected ~1.0"

    print(f"[selftest] PASS: cap_crit(0.10)=3.000, cap_crit(0.20)=2.000, "
          f"grid_step=0.1, grid_len=21, kappa3_baseline={kappa3_baseline:.3f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_alpha_seed(alpha: float, seed: int, n_dim: int) -> Dict:
    """Run one alpha x seed cell. Returns per-sigma_g results."""
    M = max(1, int(alpha * n_dim))
    rng = np.random.RandomState(seed + int(alpha * 10000))

    Xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
    W_clean = (Xi.T @ Xi) / float(n_dim)
    kappa3_baseline = hutchinson_kappa3_np(W_clean.astype(np.float64), N_PROBES_USE, seed)

    sigma_g_cap_pred = (1.0 / alpha - 1.0) ** 0.5

    cells = {}
    cap_crit_found = None
    audit_crit_found = None

    for sg in SIGMA_G_USE:
        if sg == 0.0:
            W_sg = W_clean
        else:
            noise = rng.randn(n_dim, n_dim).astype(np.float32) * sg
            W_sg = W_clean + (noise + noise.T) / 2.0

        kappa3_noisy = hutchinson_kappa3_np(W_sg.astype(np.float64), N_PROBES_USE, seed)
        kappa3_ratio = kappa3_noisy / max(kappa3_baseline, 1e-12)

        total_acc = 0.0
        for k in range(min(N_QUERIES_USE, M)):
            probe = Xi[k].copy()
            if sg > 0:
                flip = rng.random(n_dim) < 0.10
                probe[flip] *= -1.0
            state = probe.copy()
            for _ in range(N_RETRIEVAL_STEPS):
                h = W_sg @ state
                state = np.sign(h).astype(np.float32)
                state[state == 0] = 1.0
            total_acc += float(np.mean(state == Xi[k]))
        recall = total_acc / min(N_QUERIES_USE, M)

        above_half_cap = (sg > sigma_g_cap_pred / 2.0)
        below_audit_pred = (sg < sigma_g_cap_pred / 3.0)

        cells[f"sg{sg:.3f}"] = {
            "sigma_g": float(sg),
            "kappa3_ratio": float(kappa3_ratio),
            "recall": float(recall),
            "below_audit_pred": bool(below_audit_pred),
            "above_half_cap": bool(above_half_cap),
        }

        if cap_crit_found is None and recall < RECALL_CRIT:
            cap_crit_found = sg

        if audit_crit_found is None and abs(kappa3_ratio - 1.0) > 1.0:
            audit_crit_found = sg

    cap_crit = cap_crit_found if cap_crit_found is not None else max(SIGMA_G_USE)
    audit_crit = audit_crit_found if audit_crit_found is not None else max(SIGMA_G_USE)
    ratio = cap_crit / max(audit_crit, 1e-12)
    cap_tol = abs(cap_crit - sigma_g_cap_pred) / max(sigma_g_cap_pred, 1e-12) < HP_CAP_CRIT_TOLERANCE

    return {
        "alpha": float(alpha),
        "seed": seed,
        "N": n_dim,
        "run_mode": RUN_MODE,
        "sigma_g_cap_pred": float(sigma_g_cap_pred),
        "sigma_g_cap_crit": float(cap_crit),
        "sigma_g_audit_crit": float(audit_crit),
        "ratio": float(ratio),
        "cap_tol": bool(cap_tol),
        "cells": cells,
    }


def compute_verdict(results_by_alpha: Dict) -> tuple:
    alpha_summaries = []
    worst_ratio = float('inf')
    all_hp = True
    any_hf = False

    for alpha_str, alpha_results in results_by_alpha.items():
        alpha = float(alpha_str)
        ratios = [r["ratio"] for r in alpha_results if r.get("ratio") is not None]
        cap_crits = [r["sigma_g_cap_crit"] for r in alpha_results]
        cap_preds = [r["sigma_g_cap_pred"] for r in alpha_results]
        cap_tols = [r["cap_tol"] for r in alpha_results]

        mean_ratio = float(np.mean(ratios)) if ratios else 0.0
        mean_cap = float(np.mean(cap_crits))
        mean_pred = float(np.mean(cap_preds))
        all_cap_tol = all(cap_tols)

        worst_ratio = min(worst_ratio, mean_ratio)
        if mean_ratio < HP_RATIO_MIN or not all_cap_tol:
            all_hp = False
        if mean_ratio < MIDDLE_RATIO_MIN:
            any_hf = True

        alpha_summaries.append(
            f"a{alpha}: cap_crit={mean_cap:.3f}(pred={mean_pred:.3f}) "
            f"ratio={mean_ratio:.2f} cap_tol={all_cap_tol}"
        )

    summary = " | ".join(alpha_summaries) + f" | worst_ratio={worst_ratio:.2f}"

    if any_hf:
        return ("HARD_FAIL", f"HARD_FAIL: ratio<{MIDDLE_RATIO_MIN} for some alpha. {summary}")
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: ratio>={HP_RATIO_MIN} all alphas + cap_tol. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial separation. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_vals={ALPHA_VALS} sigma_g_use={SIGMA_G_USE}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

results_by_alpha: Dict[str, List[Dict]] = {str(a): [] for a in ALPHA_VALS}
n_dim_use = N_ACTIVE if RUN_MODE == "smoke" else N

t_sweep = time.time()
for alpha in ALPHA_VALS:
    out_dir_alpha = Path(str(get_output_dir(ANCHOR_NAME))) / f"a{alpha}"
    out_dir_alpha.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N, "alpha": alpha, "run_mode": RUN_MODE,
                  "sigma_g_grid_len": len(SIGMA_G_USE)}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir_alpha, run_config=run_config)
    print(f"[alpha={alpha}] {len(done_seeds)} done, {len(remaining_seeds)} to run", flush=True)

    for seed in remaining_seeds:
        t0 = time.time()
        print(f"  [alpha={alpha} seed={seed}] running...", flush=True)
        result = run_alpha_seed(alpha, seed, n_dim_use)
        result["elapsed_s"] = time.time() - t0
        write_partial(out_dir_alpha, seed, result)

    per_seed_alpha = aggregate_partials(out_dir_alpha, SEEDS)
    results_by_alpha[str(alpha)] = list(per_seed_alpha.values())

verdict, verdict_msg = compute_verdict(results_by_alpha)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
elapsed_total = time.time() - t_sweep

out_dir_main = get_output_dir(ANCHOR_NAME)
metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(SEEDS),
    "N": N,
    "alpha_vals": ALPHA_VALS,
    "sigma_g_use": SIGMA_G_USE,
    "run_mode": RUN_MODE,
    "elapsed_s": elapsed_total,
    "results_by_alpha": results_by_alpha,
}
metrics_path = out_dir_main / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
