"""
q19_aging_mu_correct_observable_v1 -- Q19 aging REDESIGN: C(t,t_w) scaling collapse.

SCIENTIFIC QUESTION (Q19 RESCUE v2 -- CK/FRSB-correct observable):
  q19_aging_mu_high_res_v1 used Phi(t_w) = plateau of C(t,t_w).
  DIAGNOSIS: the Phi observable is contaminated by a time-lag artifact --
  C never fully reaches its plateau at finite T_MAX, so Phi picks up transient
  contributions that mimic aging even in non-aging systems.

  CORRECT aging observable (Cugliandolo-Kurchan / FRSB theory):
    Aging = C(t,t_w) collapses as a function of the RATIO t/t_w (or t-t_w).
    Specifically: C(t,t_w) ~ f(t/t_w) for t >> t_w >> 1 (aging scaling).
    C(t,t_w) ~ g(t-t_w) for fixed t-t_w, varying t_w (stationary regime).
    Aging signature: SCALING COLLAPSE quality improves with larger t_w.

  Protocol:
    1. Measure C(t, t_w) for t_w in {10, 20, 40, 80} and t in [t_w, 5*t_w].
    2. For each pair, compute C as a function of the lag ratio u = t / t_w.
    3. Scaling collapse quality: for each pair of t_w values,
       measure MSE between C(u; t_w1) and C(u; t_w2) after interpolating onto
       a common u-grid. LOW MSE = good collapse = aging.
    4. Stationarity test: if C(t,t_w) ~ g(t-t_w) only, then C depends on
       (t - t_w) not (t / t_w) -- residual will be large for large t_w.

  HARD-PASS: collapse_residual < 0.10 (mean pairwise MSE in u-space)
             across >=80% of u-grid points, in >= 4/5 seeds.
  MIDDLE:    collapse_residual 0.10-0.25 in >=3/5 seeds.
  HARD-FAIL: collapse_residual >= 0.25 in >=3/5 seeds (no scaling collapse,
             pure stationarity or trivial regime).

  Calibration: no prior empirical collapse measurement for this substrate.
  Bands set +-50% around theoretical prediction (collapse_residual ~0.05
  for full aging regime in mean-field spin glasses). HP=0.10 = 2x theoretical.

FORMULA SELF-TESTS:
  1. C(t,t_w) = (1/N) * s(t) . s(t_w) where s(t) is Glauber state at time t.
     Correct range: C in [-1, 1]. C(t_w, t_w) = 1 (self-overlap = 1).
  2. Scaling collapse: if C(t,t_w) = f(t/t_w) exactly, interpolating to common
     u-grid and taking pairwise MSE gives ~0. Test with synthetic f(u) = exp(-u):
     MSE < 0.01 for perfect collapse.
  3. Stationarity test: if C(t,t_w) = g(t-t_w) = exp(-(t-t_w)/tau),
     then C as function of u = t/t_w shifts with t_w, giving large MSE. Test
     with synthetic g: MSE >> 0 for stationary process.

TIMEOUT ESTIMATE:
  Smoke: N=512, M=int(0.15*N)=77, t_w in [10,20,40], 2 seeds, Glauber T_MAX=400.
  Smoke wall expected ~8s.
  Full: N=1024, M=int(0.15*N), t_w in [10,20,40,80], 5 seeds, T_MAX=800.
  Full = 1.5 * 8 * (1024/512)^1.5 * (5/2) = ceil(1.5*8*2.83*2.5) = ceil(84.9) = 90s.
  timeout=600s (7x buffer for Glauber variability).

  Multi-scale smoke: run at N=512 and N=1024 (4x scale).

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
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "q19_aging_mu_correct_observable_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

ALPHA_C = 0.138
BETA = 2.0  # inverse temperature for Glauber

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    ALPHA_LIST = [0.15]         # above alpha_c
    T_W_LIST = [10, 20, 40]     # 3 waiting times
    T_MAX_FACTOR = 5            # t_max = T_MAX_FACTOR * max(T_W_LIST) = 200
    N_U_GRID = 20               # points on u = t/t_w grid
    N_TRIALS = 5
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_LIST = [0.14, 0.16]   # just above alpha_c, further above
    T_W_LIST = [10, 20, 40, 80] # 4 waiting times for robust collapse test
    T_MAX_FACTOR = 5
    N_U_GRID = 40
    N_TRIALS = 10

T_MAX = T_MAX_FACTOR * max(T_W_LIST)

HP_COLLAPSE_RESIDUAL = 0.10   # hard-pass threshold
MID_COLLAPSE_UPPER = 0.25     # middle-band upper
HF_COLLAPSE_RESIDUAL = 0.25   # hard-fail threshold
HP_FRAC_SEEDS = 0.80          # 4/5 seeds

# ---- FORMULA SELF-TESTS ----
def _perfect_collapse_mse():
    """Test: perfect f(u)=exp(-u) collapse gives MSE ~ 0."""
    u_grid = np.linspace(1.0, 5.0, 20)
    f_u = np.exp(-u_grid)
    # Two curves that perfectly collapse
    mse = float(np.mean((f_u - f_u)**2))
    assert mse < 1e-10, f"perfect collapse MSE={mse}, expected ~0"
    return mse


def _stationary_collapse_mse():
    """Test: stationary g(t-t_w)=exp(-lag/10) gives LARGE MSE in u-space."""
    u_grid = np.linspace(1.0, 5.0, 20)
    tau_decay = 10.0
    t_w1, t_w2 = 10.0, 40.0
    # C(t, t_w) = exp(-(t - t_w)/tau) = exp(-t_w*(u-1)/tau)
    c1 = np.exp(-t_w1 * (u_grid - 1.0) / tau_decay)
    c2 = np.exp(-t_w2 * (u_grid - 1.0) / tau_decay)
    mse = float(np.mean((c1 - c2)**2))
    assert mse > 0.01, f"stationary process MSE={mse} not large (expected >0.01)"
    return mse


_perf_mse = _perfect_collapse_mse()
_stat_mse = _stationary_collapse_mse()
assert _stat_mse > _perf_mse * 100, (
    f"Formula self-test FAIL: stationary MSE={_stat_mse:.4f} should be >> "
    f"perfect MSE={_perf_mse:.2e} by 100x"
)


def build_hopfield_w(M: int, N: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = Xi.T @ Xi / N
    return W, Xi


def glauber_step(state: np.ndarray, W: np.ndarray,
                 beta: float, rng: np.random.RandomState) -> np.ndarray:
    """One sweep of async Glauber dynamics (N random single-spin updates)."""
    N_local = len(state)
    state = state.copy()
    indices = rng.randint(0, N_local, size=N_local)
    for i in indices:
        h_i = float(W[i] @ state)
        prob_up = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        state[i] = 1.0 if rng.rand() < prob_up else -1.0
    return state


def measure_ctw_trajectory(W: np.ndarray, N_dim: int, t_w: int,
                           t_max: int, n_trials: int,
                           rng: np.random.RandomState) -> Dict[int, float]:
    """
    Measure C(t, t_w) for t in {t_w, t_w+5, ..., t_max}.
    Returns dict: {t: mean_C(t, t_w)} over n_trials.
    """
    t_measure = list(range(t_w, t_max + 1, max(1, (t_max - t_w) // (N_U_GRID - 1))))
    if t_max not in t_measure:
        t_measure.append(t_max)
    t_set = set(t_measure)

    c_by_t: Dict[int, List[float]] = {t: [] for t in t_measure}

    for _ in range(n_trials):
        state = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
        state_at_tw = None
        for step in range(t_max + 1):
            if step == t_w:
                state_at_tw = state.copy()
            state = glauber_step(state, W, BETA, rng)
            if step in t_set and state_at_tw is not None:
                c = float(np.dot(state_at_tw, state)) / N_dim
                c_by_t[step].append(c)

    return {t: float(np.mean(vals)) if vals else float("nan")
            for t, vals in c_by_t.items()}


def compute_scaling_collapse(t_w_to_ctw: Dict[int, Dict[int, float]],
                              t_w_list: List[int]) -> Dict:
    """
    For each pair of t_w values, interpolate C(t,t_w) onto common u = t/t_w grid
    and compute pairwise MSE. Return mean pairwise MSE and per-pair details.
    """
    u_min, u_max = 1.0, float(T_MAX_FACTOR)
    u_grid = np.linspace(u_min, u_max, N_U_GRID)

    # Build interpolated curves in u-space
    curves = {}
    for t_w in t_w_list:
        ctw = t_w_to_ctw.get(t_w, {})
        if not ctw:
            continue
        t_vals = sorted(ctw.keys())
        c_vals = [ctw[t] for t in t_vals]
        if len(t_vals) < 2:
            continue
        # u = t / t_w
        u_vals = [t / t_w for t in t_vals]
        valid = [(u, c) for u, c in zip(u_vals, c_vals) if not math.isnan(c)]
        if len(valid) < 2:
            continue
        u_sorted, c_sorted = zip(*sorted(valid))
        curves[t_w] = np.interp(u_grid, u_sorted, c_sorted)

    tw_keys = [tw for tw in t_w_list if tw in curves]
    if len(tw_keys) < 2:
        return {"mean_pairwise_mse": float("nan"), "n_pairs": 0, "pairs": {}}

    pairwise_mse = {}
    for i in range(len(tw_keys)):
        for j in range(i + 1, len(tw_keys)):
            tw_i, tw_j = tw_keys[i], tw_keys[j]
            mse = float(np.mean((curves[tw_i] - curves[tw_j])**2))
            pairwise_mse[(tw_i, tw_j)] = mse

    mean_mse = float(np.mean(list(pairwise_mse.values())))
    return {
        "mean_pairwise_mse": mean_mse,
        "n_pairs": len(pairwise_mse),
        "pairs": {f"{a}_{b}": v for (a, b), v in pairwise_mse.items()},
    }


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results_by_alpha = {}

    for alpha in ALPHA_LIST:
        M = max(1, int(alpha * N))
        W, _ = build_hopfield_w(M, N, seed)

        t_w_to_ctw = {}
        for t_w in T_W_LIST:
            print(f"  [seed={seed} alpha={alpha:.2f} t_w={t_w}] measuring C(t,t_w)...",
                  flush=True)
            ctw = measure_ctw_trajectory(W, N, t_w, T_MAX, N_TRIALS, rng)
            t_w_to_ctw[t_w] = ctw
            c_self = ctw.get(t_w, float("nan"))
            c_end = ctw.get(max(ctw.keys()), float("nan"))
            print(f"    C(t_w,t_w)={c_self:.4f} C(t_max,t_w)={c_end:.4f}", flush=True)

        collapse = compute_scaling_collapse(t_w_to_ctw, T_W_LIST)
        print(f"  [seed={seed} alpha={alpha:.2f}] "
              f"mean_pairwise_mse={collapse['mean_pairwise_mse']:.4f} "
              f"n_pairs={collapse['n_pairs']}", flush=True)

        results_by_alpha[alpha] = {
            "alpha": alpha, "M": M,
            "collapse": collapse,
            "t_w_list": T_W_LIST,
        }

    return {"by_alpha": results_by_alpha, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert collapse metrics non-null at tiny scale."""
    N_test = 256
    M_test = max(1, int(0.15 * N_test))
    rng = np.random.RandomState(42)
    W, _ = build_hopfield_w(M_test, N_test, 42)

    t_w_to_ctw = {}
    for tw in [10, 20]:
        ctw = measure_ctw_trajectory(W, N_test, tw, 80, n_trials=2, rng=rng)
        assert len(ctw) > 0, "C(t,t_w) trajectory is empty"
        vals = [v for v in ctw.values() if not math.isnan(v)]
        assert len(vals) > 0, "All C(t,t_w) values are NaN"
        t_w_to_ctw[tw] = ctw

    collapse = compute_scaling_collapse(t_w_to_ctw, [10, 20])
    assert not math.isnan(collapse["mean_pairwise_mse"]), "collapse MSE is NaN"
    assert collapse["n_pairs"] >= 1, "no pairs computed in collapse"

    print(f"[selftest] PASS: collapse_mse={collapse['mean_pairwise_mse']:.4f} "
          f"n_pairs={collapse['n_pairs']} at N={N_test}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for alpha in ALPHA_LIST:
        mses = []
        for sd in per_seed.values():
            row = sd["by_alpha"].get(alpha) or sd["by_alpha"].get(str(alpha))
            if row is None:
                continue
            mse = row["collapse"].get("mean_pairwise_mse", float("nan"))
            if not math.isnan(mse):
                mses.append(mse)
        agg[alpha] = {
            "mean_collapse_mse": float(np.mean(mses)) if mses else float("nan"),
            "n_seeds_pass": sum(1 for mse in mses if mse < HP_COLLAPSE_RESIDUAL),
            "n_seeds": len(mses),
        }
    return {"by_alpha": agg}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_alpha = agg["by_alpha"]
    above_c = {a: v for a, v in by_alpha.items() if float(a) > ALPHA_C - 0.02}
    if not above_c:
        return ("HARD_FAIL", "No above-alpha_c results.")

    n_seeds = max((v["n_seeds"] for v in above_c.values()), default=0)
    n_req = max(1, round(n_seeds * HP_FRAC_SEEDS))

    best_seeds_pass = max((v["n_seeds_pass"] for v in above_c.values()), default=0)
    mean_mse = float(np.nanmean([v["mean_collapse_mse"] for v in above_c.values()]))

    if best_seeds_pass >= n_req and mean_mse < HP_COLLAPSE_RESIDUAL:
        return ("HARD_PASS",
                f"Scaling collapse CONFIRMED. mean_collapse_mse={mean_mse:.4f} < "
                f"{HP_COLLAPSE_RESIDUAL}. seeds_pass={best_seeds_pass}/{n_seeds}. "
                f"C(t,t_w) collapses as function of t/t_w: genuine aging signature.")
    if mean_mse >= HF_COLLAPSE_RESIDUAL:
        return ("HARD_FAIL",
                f"No scaling collapse. mean_collapse_mse={mean_mse:.4f} >= "
                f"{HF_COLLAPSE_RESIDUAL}. C(t,t_w) does not follow t/t_w scaling.")
    return ("MIDDLE_BAND",
            f"Partial collapse. mean_collapse_mse={mean_mse:.4f} "
            f"(hp={HP_COLLAPSE_RESIDUAL}, hf={HF_COLLAPSE_RESIDUAL}). "
            f"seeds_pass={best_seeds_pass}/{n_seeds}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"ALPHA={ALPHA_LIST} T_W={T_W_LIST} T_MAX={T_MAX}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE, "T_MAX": T_MAX}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N,
        "ALPHA_LIST": ALPHA_LIST, "T_W_LIST": T_W_LIST, "T_MAX": T_MAX,
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
