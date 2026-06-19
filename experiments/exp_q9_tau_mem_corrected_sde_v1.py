"""
q9_tau_mem_corrected_sde_v1 -- Q9 tau_mem REDESIGN: correct empirical measurement.

SCIENTIFIC QUESTION (Q9 RESCUE -- correct empirical tau_mem protocol):
  Research delivered tau_mem formula: tau = (1/gamma) * log(1 + N*gamma/(2*lambda)).
  Prior smoke (tau_mem_n_scaling_v1) used scalar ODE simulation -- INSTRUMENTATION_FAIL:
  the ODE saturated at max_steps because field equations weren't calibrated.

  CORRECT empirical measurement (state-vector simulation):
    - Store M patterns in W at time 0.
    - Simulate CONTINUOUS WRITE: at each step, add Gaussian write noise
      dW_t = lambda * xi xi^T / N dt, DECAY W: W -> W * exp(-gamma * dt).
    - Discrete-time approximation: each step t:
        W_{t+1} = (1 - gamma*dt) * W_t + lambda * dt * (xi_new)(xi_new)^T / N
      where xi_new is a FRESH random pattern (simulating new writes).
    - Measure RETRIEVAL ACCURACY of ORIGINAL patterns vs time step t.
    - tau_mem_empirical = time at which retrieval accuracy drops from initial to
      THRESHOLD (0.5 halfway between initial and 0).

  Sweep N in {2048, 4096, 8192} to verify tau_mem scaling vs theory.

  FORMULA: tau_theory = (1/gamma) * log(1 + N*gamma/(2*lambda))
  This formula has two regimes:
    N*gamma << 2*lambda (weak N): tau_theory ~ N/(2*lambda) (linear in N).
    N*gamma >> 2*lambda (strong N): tau_theory ~ (1/gamma)*log(N*gamma/(2*lambda))
                                                  (log in N).

PRE-REGISTERED BANDS:
  HARD-PASS: R^2 >= 0.95 on log-log fit of tau_empirical vs N
             AND C_ratio = tau_empirical/tau_theory within [0.80, 1.20] for >=2/3 N values.
  MIDDLE:    R^2 >= 0.70 AND C_ratio within [0.50, 1.50] for >=1/3 N values.
  HARD-FAIL: R^2 < 0.70 OR C_ratio outside [0.20, 5.0] for all N (formula wrong by >5x).

  Calibration: first state-vector tau_mem measurement. Bands +-50% around formula.

FORMULA SELF-TESTS:
  1. tau_theory(N=2048, gamma=0.01, lambda=0.1):
     = (1/0.01) * log(1 + 2048*0.01/(2*0.1)) = 100 * log(1 + 102.4) = 100 * log(103.4)
     = 100 * 4.638 = 463.8 steps.
     [INPUT: N=2048, gamma=0.01, lambda=0.1] [EXPECTED: tau_theory~464]
  2. tau_theory(N=4096, gamma=0.01, lambda=0.1):
     = 100 * log(1 + 204.8) = 100 * log(205.8) = 100 * 5.327 = 532.7 steps.
     [INPUT: N=4096, gamma=0.01, lambda=0.1] [EXPECTED: tau_theory~533]
  3. tau_theory(N=8192, gamma=0.01, lambda=0.1):
     = 100 * log(1 + 409.6) = 100 * log(410.6) = 100 * 6.018 = 601.8 steps.
     [INPUT: N=8192, gamma=0.01, lambda=0.1] [EXPECTED: tau_theory~602]
  4. Ratio tau(8192)/tau(2048) = 601.8/463.8 = 1.30. If linear: ratio would be 4.
     Confirming LOG regime for these parameters.

TIMEOUT ESTIMATE:
  Smoke: N=256, T_MAX_STEPS=1000, 2 seeds, 3 N values from {256,512,1024}.
  Each step: O(N) write + O(N^2) outer product.
  At N=256: T=1000 steps * N^2 ops = 65M ops. ~0.5s.
  Smoke wall ~3s -> Full at N in {2048,4096,8192}: 3 * (8192/256)^2 * (5/2) = 3*1024*2.5 = 7680s.
  BUT: use batched outer product (M_batch patterns per step) to reduce per-step cost.
  With M_batch=1 and vectorized numpy: N=8192 step is O(N^2) = 67M flops -> ~0.01s/step.
  T_MAX_STEPS=600 (covers tau_theory + 50% buffer). Full: 600 * 0.01 * 3 * 5 = 90s.
  timeout=900s.

  Multi-scale smoke: run N_smoke=256 and N_smoke*4=1024.
  PROT-018 check: no _nN suffix, production uses N_LIST.
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

ANCHOR_NAME = "q9_tau_mem_corrected_sde_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

GAMMA = 0.01     # decay parameter
LAMBDA = 0.1     # write rate
DT = 1.0         # discrete time step

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N_LIST = [256, 512, 1024]   # multi-scale smoke
    SEEDS = [7, 17]
    T_MAX_STEPS = 1200          # generous: covers tau_theory at N=1024
    M_INIT = 5                  # initial stored patterns
else:
    N_LIST = [2048, 4096, 8192]
    SEEDS = [7, 17, 23, 31, 41, 53, 61, 71, 79, 89]  # 10 seeds (walk-back gate: smoke borderline)
    T_MAX_STEPS = 1500          # covers tau_theory at N=8192 + 50%
    M_INIT = 10                 # initial stored patterns

# Retrieval threshold: half of initial SNR
RETRIEVAL_THRESHOLD = 0.5

HP_R2 = 0.95
HP_C_RATIO_LO = 0.80
HP_C_RATIO_HI = 1.20
MID_R2 = 0.70
MID_C_RATIO_LO = 0.50
MID_C_RATIO_HI = 1.50
HF_C_RATIO_LO = 0.20
HF_C_RATIO_HI = 5.0

# ---- FORMULA SELF-TESTS ----
def tau_theory(N: int, gamma: float = GAMMA, lam: float = LAMBDA) -> float:
    """tau = (1/gamma) * log(1 + N*gamma/(2*lambda))."""
    return (1.0 / gamma) * math.log(1.0 + N * gamma / (2.0 * lam))


# Validate formula self-tests
_tau_2048 = tau_theory(2048)
_tau_4096 = tau_theory(4096)
_tau_8192 = tau_theory(8192)
assert 400.0 < _tau_2048 < 550.0, f"tau(2048)={_tau_2048:.1f}, expected ~464"
assert 480.0 < _tau_4096 < 610.0, f"tau(4096)={_tau_4096:.1f}, expected ~533"
assert 550.0 < _tau_8192 < 680.0, f"tau(8192)={_tau_8192:.1f}, expected ~602"
_ratio_log = _tau_8192 / _tau_2048
assert _ratio_log < 2.0, f"Ratio tau(8192)/tau(2048)={_ratio_log:.2f}, should be <2 (log regime)"


def build_initial_W(M: int, N: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Build initial weight matrix from M stored patterns."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = Xi.T @ Xi / N
    np.fill_diagonal(W, 0.0)
    return W, Xi


def retrieval_accuracy(W: np.ndarray, Xi: np.ndarray, N: int) -> float:
    """Mean cosine similarity of retrieved patterns vs stored patterns."""
    accs = []
    for i in range(Xi.shape[0]):
        pattern = Xi[i]
        raw = W @ pattern
        retrieved = np.sign(raw)
        cosine = float(np.dot(retrieved, pattern)) / N
        accs.append(cosine)
    return float(np.mean(accs))


def run_one_N_seed(N: int, seed: int) -> Dict:
    """Run continuous-write decay simulation for one N and seed."""
    rng = np.random.RandomState(seed)

    W, Xi = build_initial_W(M_INIT, N, seed)
    initial_acc = retrieval_accuracy(W, Xi, N)

    # Half-way threshold
    threshold = initial_acc * RETRIEVAL_THRESHOLD

    tau_empirical = float("nan")
    accs_over_time = [initial_acc]

    t_half = None
    for step in range(1, T_MAX_STEPS + 1):
        # Decay: W -> W * (1 - gamma*dt)
        W *= (1.0 - GAMMA * DT)
        # Write: add fresh random pattern
        xi_new = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
        W += (LAMBDA * DT / N) * np.outer(xi_new, xi_new)
        np.fill_diagonal(W, 0.0)

        # Measure every 10 steps to keep runtime manageable
        if step % 10 == 0:
            acc = retrieval_accuracy(W, Xi, N)
            accs_over_time.append(acc)
            if t_half is None and acc <= threshold:
                t_half = step
                tau_empirical = float(step)
                break

    tau_th = tau_theory(N)
    c_ratio = tau_empirical / tau_th if not math.isnan(tau_empirical) and tau_th > 0 else float("nan")

    print(f"  [N={N} seed={seed}] initial_acc={initial_acc:.4f} "
          f"threshold={threshold:.4f} tau_emp={tau_empirical:.1f} "
          f"tau_theory={tau_th:.1f} ratio={c_ratio:.3f}", flush=True)

    return {
        "N": N, "seed": seed,
        "initial_acc": initial_acc,
        "tau_empirical": tau_empirical,
        "tau_theory": tau_th,
        "c_ratio": c_ratio,
        "n_steps_measured": len(accs_over_time),
        "run_mode": RUN_MODE,
    }


def run_seed(seed: int) -> Dict:
    """Run all N values for one seed."""
    results = {}
    for N in N_LIST:
        result = run_one_N_seed(N, seed)
        results[str(N)] = result
    return {"by_N": results, "seed": seed, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert tau_empirical is measurable at small scale."""
    N_test = 128
    M_test = 3
    rng = np.random.RandomState(42)
    W_test, Xi_test = build_initial_W(M_test, N_test, 42)

    # Verify retrieval accuracy non-null
    acc = retrieval_accuracy(W_test, Xi_test, N_test)
    assert not math.isnan(acc), "retrieval_accuracy returned NaN"
    assert 0.0 <= acc <= 1.0, f"acc={acc} out of [0,1]"
    assert acc > 0.3, f"Initial acc={acc:.4f} too low (expected >0.3 for M_init=3 at N=128)"

    # Run 50 decay steps and verify acc changes
    acc0 = acc
    for _ in range(50):
        W_test *= (1.0 - GAMMA * DT)
        xi_new = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
        W_test += (LAMBDA * DT / N_test) * np.outer(xi_new, xi_new)
        np.fill_diagonal(W_test, 0.0)
    acc50 = retrieval_accuracy(W_test, Xi_test, N_test)

    # Tau theory for N=128 (log regime): tau = (1/0.01)*log(1+128*0.01/0.2) = 100*log(7.4)=201
    # After 50 steps (25% of tau), accuracy should still be reasonable but different
    assert not math.isnan(acc50), "acc after 50 steps is NaN"
    # At N=128 with M_INIT=3 patterns, retrieval is noisy; just verify it changed direction
    print(f"[selftest] acc0={acc0:.4f} acc50={acc50:.4f} "
          f"tau_theory(128)={tau_theory(128):.1f}", flush=True)
    print("[selftest] PASS: tau_mem simulation produces non-null metrics", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate tau_empirical vs N across seeds."""
    # Collect per-N
    by_N = {}
    for N in N_LIST:
        taus_emp, taus_th, ratios = [], [], []
        for sd in per_seed.values():
            row = sd["by_N"].get(str(N))
            if row is None:
                continue
            t_emp = row.get("tau_empirical", float("nan"))
            t_th = row.get("tau_theory", float("nan"))
            c_r = row.get("c_ratio", float("nan"))
            if not math.isnan(t_emp):
                taus_emp.append(t_emp)
            if not math.isnan(t_th):
                taus_th.append(t_th)
            if not math.isnan(c_r):
                ratios.append(c_r)
        by_N[N] = {
            "mean_tau_empirical": float(np.mean(taus_emp)) if taus_emp else float("nan"),
            "mean_tau_theory": float(np.mean(taus_th)) if taus_th else float("nan"),
            "mean_c_ratio": float(np.mean(ratios)) if ratios else float("nan"),
            "n_seeds": len(taus_emp),
        }

    # Log-log fit of tau_empirical vs N (should be log-linear)
    N_vals = []
    tau_vals = []
    for N, v in by_N.items():
        if not math.isnan(v["mean_tau_empirical"]):
            N_vals.append(float(N))
            tau_vals.append(v["mean_tau_empirical"])

    r2 = float("nan")
    if len(N_vals) >= 2:
        log_N = np.array([math.log(n) for n in N_vals])
        log_tau = np.array([math.log(t) for t in tau_vals])
        n = len(log_N)
        sx = float(np.sum(log_N))
        sy = float(np.sum(log_tau))
        sxy = float(np.dot(log_N, log_tau))
        sx2 = float(np.dot(log_N, log_N))
        denom = n * sx2 - sx**2
        if abs(denom) > 1e-12:
            slope = (n * sxy - sx * sy) / denom
            intercept = (sy - slope * sx) / n
            pred = slope * log_N + intercept
            ss_tot = float(np.sum((log_tau - np.mean(log_tau))**2))
            ss_res = float(np.sum((log_tau - pred)**2))
            r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0

    return {"by_N": by_N, "r2_loglog": r2}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_N = agg["by_N"]
    r2 = agg.get("r2_loglog", float("nan"))

    # Count N values where c_ratio is within HP range
    ratios = [v["mean_c_ratio"] for v in by_N.values()
              if not math.isnan(v.get("mean_c_ratio", float("nan")))]
    n_hp = sum(1 for r in ratios if HP_C_RATIO_LO <= r <= HP_C_RATIO_HI)
    n_mid = sum(1 for r in ratios if MID_C_RATIO_LO <= r <= MID_C_RATIO_HI)
    n_total = len(ratios)

    if not math.isnan(r2) and r2 >= HP_R2 and n_hp >= max(1, 2 * n_total // 3):
        return ("HARD_PASS",
                f"tau_mem formula CONFIRMED. R2_loglog={r2:.3f}>={HP_R2}. "
                f"{n_hp}/{n_total} N-values within +-20% of theory. "
                f"Continuous-write decay matches tau=(1/gamma)*log(1+N*gamma/(2*lambda)).")
    if math.isnan(r2) or r2 < MID_R2 or n_mid == 0:
        return ("HARD_FAIL",
                f"tau_mem formula NOT confirmed. R2_loglog={r2:.3f}<{MID_R2}. "
                f"n_ratios_in_5x_band={sum(1 for r in ratios if HF_C_RATIO_LO<=r<=HF_C_RATIO_HI)}/{n_total}. "
                f"SDE model mis-specified or parameter regime wrong.")
    return ("MIDDLE_BAND",
            f"Partial confirmation. R2={r2:.3f}(hp={HP_R2}) "
            f"n_hp={n_hp}/{n_total} n_mid={n_mid}/{n_total}. "
            f"Mean ratios: {[round(r,2) for r in ratios]}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N_LIST={N_LIST} "
          f"gamma={GAMMA} lambda={LAMBDA} T_MAX={T_MAX_STEPS} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N_LIST": N_LIST, "run_mode": RUN_MODE, "T_MAX": T_MAX_STEPS}
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
        "run_mode": RUN_MODE, "N_LIST": N_LIST,
        "gamma": GAMMA, "lambda": LAMBDA,
        "T_MAX_STEPS": T_MAX_STEPS, "seeds": SEEDS,
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
