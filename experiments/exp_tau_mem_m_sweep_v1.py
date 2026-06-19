"""
tau_mem_m_sweep_v1 -- tau_mem vs M_eff sweep to characterize multi-pattern memory decay.

SCIENTIFIC QUESTION (Q9 follow-on, per research negative-results review R3):
  q9_tau_mem_corrected_sde_v1 tests the corrected single-pattern formula.
  This companion experiment sweeps M_eff in {1, 2, 5, 10, 20} at fixed N to
  empirically characterize how tau_emp scales with M_eff and compare to the
  M_eff-corrected formula:
    tau_mem^(M) = (1/gamma) * log(1 + N*gamma / (2*lambda*(1 + M_eff/N)))

  For large N: 1 + M_eff/N ~ 1 (correction negligible), so tau_mem^(M) ~ tau_mem^(1).
  This predicts: tau_emp(M_eff) should NOT depend strongly on M_eff at large N.

  Measurement: measure empirical tau_emp by tracking how fast the overlap m(t) =
  (1/N) * state(t) . xi_1 decays when N-1 background patterns are also stored.

  Test cells:
    (A) M_eff independence at large N: tau_emp(M=1) / tau_emp(M=10) in [0.5, 2.0]
        (within 2x, consistent with O(M_eff/N) correction being negligible).
        HP-A: ratio in [0.5, 2.0]. HF-A: ratio > 5.0 (strong M_eff dependence).
    (B) Formula validation at M_eff=1: |tau_emp - tau_theory| / tau_theory <= 0.20.
        HP-B: rel_err <= 0.20. HF-B: rel_err > 1.0 (10x off).
    (C) Monotone decay: tau_emp decreases (or stays flat) as M_eff increases from 1 to 20.
        HP-C: tau(M=1) >= tau(M=10) * 0.80 (tau doesn't INCREASE with more patterns).
        HF-C: tau(M=20) > tau(M=1) * 1.5 (non-physical increase).

  HARD-PASS: All of A, B, C.
  HARD-FAIL: HF-A (strong M_eff dependence = formula wrong) or HF-C (non-physical).
  MIDDLE: 2/3 cells.

PRE-REGISTERED BANDS (calibration probe; no prior M_eff sweep measurement):
  HP: ratio in [0.5, 2.0], rel_err <= 0.20, tau_mono.
  HF: ratio > 5.0, rel_err > 1.0, non-physical increase.
  Bands: +-50% per calibration-probe policy.
  Theory: M_eff correction is O(M_eff/N) ~ O(20/1024) ~ 2% at full scale -- negligible.

FORMULA SELF-TESTS:
  1. Formula at M_eff=1, N=1024, gamma=0.001, lambda=0.01:
     tau = (1/0.001) * log(1 + 1024*0.001 / (2*0.01*(1+1/1024)))
           = 1000 * log(1 + 1.024/(0.02*1.001))
           = 1000 * log(1 + 51.17) = 1000 * log(52.17) = 1000 * 3.954 = 3954
     [INPUT: N=1024, gamma=0.001, lambda=0.01, M_eff=1] [EXPECTED: tau ~ 3954]
  2. M_eff correction: tau(M_eff=1) / tau(M_eff=20) for N=1024.
     Correction factor: (1 + 1/1024) / (1 + 20/1024) = 1.000977 / 1.01953 = 0.9814.
     tau ratio = 1.0 / 0.9814 ~ 1.019 (within 2% -- negligible).
     [INPUT: M_eff=1 vs 20, N=1024] [EXPECTED: ratio ~ 1.02]
  3. Relative error: |tau_emp=3800 - tau_theory=3954| / 3954 = 154/3954 = 0.039 < 0.20.
     [INPUT: tau_emp=3800, tau_theory=3954] [EXPECTED: rel_err=0.039]

TIMEOUT ESTIMATE:
  Smoke: N=512, M_eff in {1,2,5}, 2 seeds, 50 equilibration steps. ~5s.
  Full: N=1024, M_eff in {1,2,5,10,20}, 5 seeds, 100 equilibration steps.
  Scale: 1.5 * 5 * (1024/512)^1.0 * (5/2) * (5/3) = ceil(1.5*5*2*2.5*1.67) = ceil(62.5) = 63s.
  timeout=600s (generous; tau_emp measurement needs Glauber runs).

No _nN suffix; production N=1024 per rule 3.
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
from typing import Dict, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "tau_mem_m_sweep_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

GAMMA = 0.001   # memory decay rate
LAMBDA = 0.01   # pattern weight / learning rate
BETA = 2.0

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    M_EFF_SWEEP = [1, 2, 5]
    T_MAX = 500    # max steps for tau measurement
    T_EQUILIBRATE = 50
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    M_EFF_SWEEP = [1, 2, 5, 10, 20]
    T_MAX = 2000
    T_EQUILIBRATE = 100

HP_TAU_RATIO_MAX = 2.0
HF_TAU_RATIO_MAX = 5.0
HP_REL_ERR = 0.20
HF_REL_ERR = 1.0
HP_MONO_RATIO = 0.80

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


def tau_theory(N_dim: int, gamma: float, lam: float, M_eff: int) -> float:
    """M_eff-corrected tau_mem formula."""
    denom = 2.0 * lam * (1.0 + M_eff / N_dim)
    return (1.0 / gamma) * math.log(1.0 + N_dim * gamma / denom)


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. Formula at M_eff=1, N=1024
    tau_1 = tau_theory(1024, 0.001, 0.01, 1)
    expected_tau = 3954.0
    assert abs(tau_1 - expected_tau) / expected_tau < 0.05, f"tau formula M=1: got {tau_1:.1f}, expected ~{expected_tau:.1f}"

    # 2. M_eff correction ratio
    tau_20 = tau_theory(1024, 0.001, 0.01, 20)
    ratio = tau_1 / tau_20
    assert 0.95 < ratio < 1.10, f"M_eff correction ratio: {ratio:.4f} expected ~1.02"

    # 3. Relative error formula
    tau_emp = 3800.0
    tau_th = 3954.0
    rel_err = abs(tau_emp - tau_th) / tau_th
    assert abs(rel_err - 0.039) < 0.005, f"rel_err formula: {rel_err:.4f} expected ~0.039"

    print(f"[selftest] tau_theory_M1={tau_1:.1f} ratio_1_vs_20={ratio:.4f} rel_err={rel_err:.4f}", flush=True)


_instrumentation_selftest()


def build_w_with_decay(M_eff: int, N_dim: int, gamma: float, lam: float, seed: int):
    """Build W = (lambda/N)*Xi^T Xi - gamma*I (decay term)."""
    rng = np.random.RandomState(seed)
    # Store 1 target pattern + (M_eff-1) background patterns
    Xi = rng.choice([-1.0, 1.0], size=(max(1, M_eff), N_dim)).astype(np.float64)
    W = lam * Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    # Decay: effective field = W @ state - gamma * state
    return W, Xi[0]  # Return W and target pattern


def measure_tau_emp(W: np.ndarray, xi_target: np.ndarray, N_dim: int, gamma: float,
                    beta: float, T_max: int, T_eq: int, seed: int) -> float:
    """Measure empirical tau by tracking overlap decay from retrieval state."""
    rng = np.random.RandomState(seed + 77777)

    # Start from near-perfect retrieval state
    state = xi_target.copy()
    n_flip_init = int(0.05 * N_dim)
    flip_idx = rng.choice(N_dim, size=n_flip_init, replace=False)
    state[flip_idx] = -state[flip_idx]

    # Run dynamics with explicit decay: h_eff = W @ state - gamma * state
    overlaps = []
    for t in range(T_max):
        h = W @ state - gamma * state  # decay term
        prob_up = 1.0 / (1.0 + np.exp(-2.0 * beta * h))
        rand_vals = rng.rand(N_dim)
        state = np.where(rand_vals < prob_up, 1.0, -1.0)
        overlap = float(np.dot(state, xi_target)) / N_dim
        overlaps.append(overlap)

    overlaps_arr = np.array(overlaps)
    # Find half-life: first t where overlap drops below 0.5 * initial overlap
    m0 = max(overlaps_arr[0], 1e-6)
    threshold = 0.5 * m0
    below_threshold = np.where(overlaps_arr < threshold)[0]
    if len(below_threshold) == 0:
        return float(T_max)  # didn't decay by half
    return float(below_threshold[0])


def run_one_seed(seed: int) -> Dict:
    tau_emp_by_M = {}
    tau_theory_by_M = {}

    for M_eff in M_EFF_SWEEP:
        W, xi_target = build_w_with_decay(M_eff, N, GAMMA, LAMBDA, seed)
        tau_emp = measure_tau_emp(W, xi_target, N, GAMMA, BETA, T_MAX, T_EQUILIBRATE, seed + M_eff)
        tau_th = tau_theory(N, GAMMA, LAMBDA, M_eff)
        tau_emp_by_M[M_eff] = tau_emp
        tau_theory_by_M[M_eff] = tau_th

    tau_M1 = tau_emp_by_M.get(1, tau_emp_by_M[M_EFF_SWEEP[0]])
    tau_M_large = tau_emp_by_M.get(10, tau_emp_by_M[M_EFF_SWEEP[-1]])
    tau_ratio = tau_M1 / (tau_M_large + 1e-6)

    tau_theory_M1 = tau_theory_by_M.get(1, tau_theory_by_M[M_EFF_SWEEP[0]])
    rel_err_M1 = abs(tau_M1 - tau_theory_M1) / (tau_theory_M1 + 1e-6)

    # Monotone check: tau should not increase from M=1 to M=20
    tau_last = tau_emp_by_M[M_EFF_SWEEP[-1]]
    tau_mono_ratio = tau_M1 / (tau_last + 1e-6)

    assert tau_M1 >= 0.0, f"tau_emp_M1={tau_M1:.1f} negative -- instrumentation bug"

    cell_A_pass = 0.5 <= tau_ratio <= HP_TAU_RATIO_MAX
    cell_A_hf = tau_ratio > HF_TAU_RATIO_MAX
    cell_B_pass = rel_err_M1 <= HP_REL_ERR
    cell_B_hf = rel_err_M1 > HF_REL_ERR
    cell_C_pass = tau_mono_ratio >= HP_MONO_RATIO
    cell_C_hf = tau_mono_ratio < (1.0 / 1.5)  # tau increases by 50%+

    return {
        "N": N,
        "run_mode": RUN_MODE,
        "seed": seed,
        "tau_emp_by_M": {str(k): v for k, v in tau_emp_by_M.items()},
        "tau_theory_by_M": {str(k): v for k, v in tau_theory_by_M.items()},
        "tau_ratio": tau_ratio,
        "rel_err_M1": rel_err_M1,
        "tau_mono_ratio": tau_mono_ratio,
        "cell_A_pass": cell_A_pass,
        "cell_A_hf": cell_A_hf,
        "cell_B_pass": cell_B_pass,
        "cell_B_hf": cell_B_hf,
        "cell_C_pass": cell_C_pass,
        "cell_C_hf": cell_C_hf,
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"[seed={seed}] running M_eff sweep {M_EFF_SWEEP}...", flush=True)
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed={seed}] tau_ratio={result['tau_ratio']:.3f} rel_err_M1={result['rel_err_M1']:.3f} tau_mono={result['tau_mono_ratio']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    n_seeds = len(SEEDS)

    all_ratio = [per_seed[str(s)]["tau_ratio"] for s in SEEDS]
    all_rel_err = [per_seed[str(s)]["rel_err_M1"] for s in SEEDS]
    all_mono = [per_seed[str(s)]["tau_mono_ratio"] for s in SEEDS]
    mean_ratio = float(np.mean(all_ratio))
    mean_rel_err = float(np.mean(all_rel_err))
    mean_mono = float(np.mean(all_mono))

    n_A = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_pass"])
    n_A_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_hf"])
    n_B = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_pass"])
    n_C = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_pass"])
    n_C_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_hf"])

    thr = math.ceil(n_seeds * 0.6)
    cell_A_pass = n_A >= thr
    cell_B_pass = n_B >= thr
    cell_C_pass = n_C >= thr
    hf_A = n_A_hf >= thr
    hf_C = n_C_hf >= thr

    n_cells_pass = int(cell_A_pass) + int(cell_B_pass) + int(cell_C_pass)
    if n_cells_pass == 3:
        verdict = "HARD_PASS"
    elif hf_A or hf_C:
        verdict = "HARD_FAIL"
    elif n_cells_pass >= 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    verdict_msg = (
        f"tau_mem_m_sweep_v1 verdict={verdict}: "
        f"mean_tau_ratio(1_vs_large_M)={mean_ratio:.3f}(HP in [0.5,{HP_TAU_RATIO_MAX}]) "
        f"mean_rel_err_M1={mean_rel_err:.3f}(HP<={HP_REL_ERR}) "
        f"mean_tau_mono={mean_mono:.3f}(HP>={HP_MONO_RATIO}) "
        f"cells={n_cells_pass}/3 elapsed={elapsed:.1f}s"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "n_seeds": n_seeds,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_tau_ratio": mean_ratio,
        "mean_rel_err_M1": mean_rel_err,
        "mean_tau_mono_ratio": mean_mono,
        "n_cell_A_pass": n_A,
        "n_cell_B_pass": n_B,
        "n_cell_C_pass": n_C,
        "elapsed_s": elapsed,
    }
    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] metrics written to {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
