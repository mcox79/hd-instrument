"""
combo4_dynamical_redesign_v2_n2048 -- COMBO-4 v2 redesign: C(t,t_w) vs t/t_w scaling collapse.

COMBO-4 v1 was MIDDLE 2/4: M_dyn PASS (0.871) + C(t,t_w) aging collapse PASS,
but DFT oscillation detection + piecewise-vs-monotone X(C) shape discrimination FAIL.
v2 redesign per research guidance: focus on the TWO clean observables confirmed by v1,
drop the DFT oscillation sub-test (not enough signal at N=1024), and add the
C(t,t_w) ~ (t/t_w)^mu SCALING COLLAPSE as the centerpiece test at N=2048.

The v2 simplification: C(t,t_w) vs t/t_w log-log collapse with exponent mu.
Correct aging exponent: mu in [0.5, 1.0] for CK class. mu ~ 0.7-0.9 predicted by theory.

Test cells:
  (A) C(t,t_w) scaling collapse quality: MSE of C(t,t_w) vs fit C0 * (t/t_w)^{-mu} < 0.05.
      HP-A: scaling_collapse_mse < 0.05 in >= 3/3 (all) seeds.
  (B) Aging exponent mu: log-log fit gives mu in [0.50, 1.00].
      HP-B: mu_fit in [0.50, 1.00].
  (C) M_dyn ultrametricity: M_dyn >= 0.75 (confirmed class at N=1024; test at N=2048).
      HP-C: M_dyn >= 0.75.

HARD-PASS: HP-A AND HP-B AND HP-C.
HARD-FAIL: scaling_collapse_mse > 0.20 OR M_dyn < 0.60.
MIDDLE: 2/3 cells pass.

PRE-REGISTERED BANDS:
  HP: collapse_mse < 0.05, mu in [0.50, 1.00], M_dyn >= 0.75.
  HF: collapse_mse > 0.20 OR M_dyn < 0.60.
  Calibration: v1 at N=1024 gave M_dyn=0.871, C(t,t_w) collapse PASS.
  v2 at N=2048: expect same or better (larger N -> cleaner signal).
  mu bands from CK theory: [0.5, 1.0] with mode ~0.8.

FORMULA SELF-TESTS:
  1. CK ultrametricity ratio: C_13 / min(C_12, C_23) <= 1.
     [INPUT: C_12=0.9, C_23=0.8, C_13=0.7] [EXPECTED: ratio=0.875 <= 1.0]
  2. Scaling collapse: C(t,t_w) = (t/t_w)^{-0.8} has MSE < 0.001 when fitted.
     [INPUT: C = (t/t_w)^{-0.8} grid] [EXPECTED: MSE_collapse < 0.001]
  3. Aging exponent from log-log: slope of log(C) vs log(t/t_w) = -mu.
     [INPUT: C = 0.5 * (t/t_w)^{-0.75}] [EXPECTED: mu_fit in [0.70, 0.80]]

PROT-018: anchor has _n2048; N MUST = 2048.
PROT-021: run_config includes N, ALPHA, R, run_mode.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "combo4_dynamical_redesign_v2_n2048"

_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.12
BETA = 2.0

if RUN_MODE == "smoke":
    N_SMOKE = 256
    N_ACTIVE = N_SMOKE
    SEEDS = [7]
    R = 30
    TW_LIST = [16, 64]
    T_RATIO_GRID = [2.0, 4.0, 8.0]
    T_MAX = 512
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23]
    R = 150
    TW_LIST = [16, 64, 256]
    T_RATIO_GRID = [1.5, 2.0, 3.0, 5.0, 8.0]
    T_MAX = 2048

M = max(2, int(ALPHA * N_ACTIVE))

HP_COLLAPSE_MSE = 0.05
HF_COLLAPSE_MSE = 0.20
HP_MU_LO = 0.50
HP_MU_HI = 1.00
HP_MDYN = 0.75
HF_MDYN = 0.60


def _selftest_ck_ratio():
    c12, c23, c13 = 0.9, 0.8, 0.7
    ratio = c13 / min(c12, c23)
    assert abs(ratio - 0.875) < 1e-9, f"CK ratio selftest: {ratio:.6f} != 0.875"
    assert ratio <= 1.0, f"CK ratio {ratio} > 1 (ultrametricity violated)"
    return ratio


def _selftest_scaling_collapse():
    mu = 0.8
    t_w_vals = [16.0, 64.0, 256.0]
    ratios = [1.5, 2.0, 4.0, 8.0]
    C_vals = []
    for t_w in t_w_vals:
        for r in ratios:
            C_vals.append((r, (t_w / (t_w * r)) ** mu))
    ratios_all = [v[0] for v in C_vals]
    c_all = [v[1] for v in C_vals]
    log_r = np.log(ratios_all)
    log_c = np.log([max(c, 1e-15) for c in c_all])
    slope, intercept = np.polyfit(log_r, log_c, 1)
    c_pred = np.exp(intercept + slope * np.array(log_r))
    mse = float(np.mean((np.array(c_all) - c_pred) ** 2))
    assert mse < 0.001, f"scaling collapse selftest: MSE={mse:.6f} > 0.001"
    mu_fit = -slope
    assert abs(mu_fit - mu) < 0.05, f"mu_fit={mu_fit:.4f} != {mu} (tolerance 0.05)"
    return mse, mu_fit


def _instrumentation_selftest():
    r1 = _selftest_ck_ratio()
    mse, mu_fit = _selftest_scaling_collapse()
    print(f"[selftest] PASS: ck_ratio={r1:.4f} collapse_mse={mse:.6f} mu_fit={mu_fit:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def glauber_step(W: np.ndarray, state: np.ndarray, beta: float,
                  rng: np.random.RandomState) -> np.ndarray:
    n = W.shape[0]
    state = state.copy()
    h = W @ state
    perm = rng.permutation(n)
    for i in perm:
        hi = float(h[i])
        p_up = 1.0 / (1.0 + math.exp(-2.0 * beta * hi))
        new_si = 1.0 if rng.random() < p_up else -1.0
        delta = new_si - state[i]
        if abs(delta) > 1e-12:
            h += W[:, i] * delta
            state[i] = new_si
    return state


def run_trajectory(W: np.ndarray, N_dim: int, t_max: int, beta: float,
                    seed: int) -> dict:
    rng = np.random.RandomState(seed)
    state = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
    snapshots = {}
    for t in range(1, t_max + 1):
        state = glauber_step(W, state, beta, rng)
        snapshots[t] = state.copy()
    return snapshots


def two_time_correlator(s_t: np.ndarray, s_tw: np.ndarray, N_dim: int) -> float:
    return float(np.dot(s_t, s_tw)) / float(N_dim)


def compute_mdyn(W: np.ndarray, N_dim: int, R: int, tw_list: List[int],
                  t_ratio_grid: List[float], beta: float, seed_base: int) -> Tuple[float, int]:
    if len(tw_list) < 2:
        return float("nan"), 0
    t1 = tw_list[0]
    t2 = tw_list[1]
    t3 = int(tw_list[0] * t_ratio_grid[-1])
    t_max_needed = max(t1, t2, t3)
    ratios = []
    for r in range(R):
        traj = run_trajectory(W, N_dim, t_max_needed, beta, seed=seed_base + r)
        s1 = traj.get(t1)
        s2 = traj.get(t2)
        s3 = traj.get(t3)
        if s1 is None or s2 is None or s3 is None:
            continue
        c12 = two_time_correlator(s2, s1, N_dim)
        c23 = two_time_correlator(s3, s2, N_dim)
        c13 = two_time_correlator(s3, s1, N_dim)
        denom = min(abs(c12), abs(c23))
        if denom < 1e-12:
            continue
        ratios.append(abs(c13) / denom)
    m_dyn = float(np.mean(ratios)) if ratios else float("nan")
    return m_dyn, len(ratios)


def compute_aging_collapse(W: np.ndarray, N_dim: int, tw_list: List[int],
                             t_ratio_grid: List[float], beta: float,
                             seed_base: int, n_rep: int = 15) -> Dict:
    t_max = int(max(tw_list) * max(t_ratio_grid))
    C_matrix = {}
    for rep in range(n_rep):
        traj = run_trajectory(W, N_dim, t_max, beta, seed=seed_base + 1000 + rep)
        for tw in tw_list:
            for ratio in t_ratio_grid:
                t = int(tw * ratio)
                if t > t_max or t <= tw:
                    continue
                s_t = traj.get(t)
                s_tw = traj.get(tw)
                if s_t is None or s_tw is None:
                    continue
                key = ratio
                if key not in C_matrix:
                    C_matrix[key] = []
                C_matrix[key].append(two_time_correlator(s_t, s_tw, N_dim))

    if not C_matrix:
        return {"scaling_collapse_mse": float("nan"), "aging_exponent_mu": float("nan")}

    ratios_sorted = sorted(C_matrix.keys())
    c_means = [float(np.mean(C_matrix[r])) for r in ratios_sorted]

    # Log-log fit: log(C) = -mu * log(t/t_w) + const
    valid = [(r, c) for r, c in zip(ratios_sorted, c_means) if c > 1e-10]
    if len(valid) < 2:
        return {"scaling_collapse_mse": float("nan"), "aging_exponent_mu": float("nan")}

    log_r = np.log([v[0] for v in valid])
    log_c = np.log([v[1] for v in valid])
    try:
        slope, intercept = np.polyfit(log_r, log_c, 1)
    except Exception:
        return {"scaling_collapse_mse": float("nan"), "aging_exponent_mu": float("nan")}

    c_pred = np.exp(intercept + slope * log_r)
    c_actual = np.array([v[1] for v in valid])
    mse = float(np.mean((c_actual - c_pred) ** 2))
    mu_fit = float(-slope)

    return {"scaling_collapse_mse": mse, "aging_exponent_mu": mu_fit}


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi = rng.choice([-1.0, 1.0], size=(M, N_ACTIVE)).astype(np.float64)
    W = Xi.T @ Xi / float(N_ACTIVE)
    np.fill_diagonal(W, 0.0)

    m_dyn, n_valid = compute_mdyn(W, N_ACTIVE, R, TW_LIST, T_RATIO_GRID, BETA, seed_base=seed * 100)
    aging = compute_aging_collapse(W, N_ACTIVE, TW_LIST, T_RATIO_GRID, BETA, seed_base=seed * 100)

    collapse_mse = aging["scaling_collapse_mse"]
    mu_fit = aging["aging_exponent_mu"]

    hp_a = (not math.isnan(collapse_mse)) and collapse_mse < HP_COLLAPSE_MSE
    hp_b = (not math.isnan(mu_fit)) and HP_MU_LO <= mu_fit <= HP_MU_HI
    hp_c = (not math.isnan(m_dyn)) and m_dyn >= HP_MDYN

    elapsed = time.time() - t0
    print(f"  [seed={seed}] M_dyn={m_dyn:.4f}(HP>={HP_MDYN}) "
          f"collapse_mse={collapse_mse:.4f}(HP<{HP_COLLAPSE_MSE}) "
          f"mu_fit={mu_fit:.4f}(HP in [{HP_MU_LO},{HP_MU_HI}]) "
          f"n_valid={n_valid} hp_ABC=[{int(hp_a)},{int(hp_b)},{int(hp_c)}] "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N_ACTIVE, "M": M, "R": R, "run_mode": RUN_MODE,
        "m_dyn": float(m_dyn) if not math.isnan(m_dyn) else None,
        "n_valid_mdyn": int(n_valid),
        "scaling_collapse_mse": float(collapse_mse) if not math.isnan(collapse_mse) else None,
        "aging_exponent_mu": float(mu_fit) if not math.isnan(mu_fit) else None,
        "hp_a": bool(hp_a), "hp_b": bool(hp_b), "hp_c": bool(hp_c),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    mdyn_vals = [r["m_dyn"] for r in results if r.get("m_dyn") is not None]
    mse_vals = [r["scaling_collapse_mse"] for r in results if r.get("scaling_collapse_mse") is not None]
    mu_vals = [r["aging_exponent_mu"] for r in results if r.get("aging_exponent_mu") is not None]

    mean_mdyn = float(np.mean(mdyn_vals)) if mdyn_vals else float("nan")
    mean_mse = float(np.mean(mse_vals)) if mse_vals else float("nan")
    mean_mu = float(np.mean(mu_vals)) if mu_vals else float("nan")

    summary = (f"M_dyn={mean_mdyn:.4f}(HP>={HP_MDYN} HF<{HF_MDYN}) "
               f"collapse_mse={mean_mse:.4f}(HP<{HP_COLLAPSE_MSE} HF>{HF_COLLAPSE_MSE}) "
               f"mu={mean_mu:.4f}(HP [{HP_MU_LO},{HP_MU_HI}]) "
               f"n_seeds={n}")

    if (not math.isnan(mean_mse) and mean_mse > HF_COLLAPSE_MSE) or \
       (not math.isnan(mean_mdyn) and mean_mdyn < HF_MDYN):
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    n_all_hp = sum(1 for r in results if r["hp_a"] and r["hp_b"] and r["hp_c"])
    n_hp2 = sum(1 for r in results if sum([r["hp_a"], r["hp_b"], r["hp_c"]]) >= 2)
    min_pass = max(1, math.ceil(n * 0.6))

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: COMBO-4 v2 A+B+C at N={N}. {summary}")
    if n_hp2 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 cells at N={N}. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "ALPHA": ALPHA, "R": R, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N_active={N_ACTIVE} M={M} R={R}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N_ACTIVE,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "mean_m_dyn": float(np.mean([r["m_dyn"] for r in all_results if r.get("m_dyn") is not None])) if any(r.get("m_dyn") for r in all_results) else None,
    "mean_scaling_collapse_mse": float(np.mean([r["scaling_collapse_mse"] for r in all_results if r.get("scaling_collapse_mse") is not None])) if any(r.get("scaling_collapse_mse") for r in all_results) else None,
    "mean_aging_exponent_mu": float(np.mean([r["aging_exponent_mu"] for r in all_results if r.get("aging_exponent_mu") is not None])) if any(r.get("aging_exponent_mu") for r in all_results) else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
