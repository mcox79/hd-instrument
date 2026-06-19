"""AMP-on-Kerdock with 5x more iterations: explosion vs fixed-point question.

Motivation
----------
Verdict AMP_SE_DIVERGES (v163, 2026-05-23) ran 200 AMP iterations on Kerdock
codebook at N=4096 and concluded the scalar AMP-SE prediction (~0.09 MSE) does
not match empirical AMP MSE (~0.65-0.95). But 200 iterations may have terminated
mid-trajectory if the empirical AMP has unusual long-tail behavior.

This experiment extends iteration count by 5x (1000 iterations) and tracks
the FULL MSE trajectory to discriminate:

  (a) DIVERGENCE EXPLODES: MSE keeps growing past 200 iters -> truly unstable
      iteration; the "0.65 MSE" v163 found was just a snapshot of a runaway.
  (b) FIXED POINT MISSED: MSE plateaus at a non-zero level by iter 500-1000;
      v163's "diverges" verdict was correct in spirit but the actual fixed
      point lies at a different MSE than scalar AMP-SE predicts (still
      universality-class-failure but with a well-defined limit).
  (c) STABILIZES: MSE oscillates with no monotone trend; this is the
      mathematical signature of AMP cycling between extrinsic-estimate basins
      without converging -- a known failure mode for non-RI matrices.

Empirically distinguishing these matters for the substrate-product story:
  - (a) means "AMP iterates explode on this codebook" (most dramatic)
  - (b) means "AMP has a fixed point but at the wrong MSE" (mechanism for v163)
  - (c) means "AMP doesn't converge at all" (oscillation, dynamical)

Method
------
N=4096 Kerdock codebook, alpha in {1.0, 2.0, 4.0} (substrate's working regime).
5 seeds. AMP iteration count = 1000. Track full MSE history; compute:
  - mse_at_1000 (final value)
  - mse_at_200 (the v163-equivalent snapshot)
  - mse_trajectory_max
  - mse_trajectory_oscillation (max deviation from running mean over last 100 iters)
  - growth_rate (linear fit of log MSE over last 500 iters)

Verdict from these metrics.

Vertex: AMP_LONGITER_EXPLODES / AMP_LONGITER_FIXED_POINT / AMP_LONGITER_OSCILLATES /
        AMP_LONGITER_CONVERGES_TO_SE (would override v163; very low prior probability) /
        AMP_LONGITER_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_amp_se_kerdock_longiter_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False


# ---------------------------------------------------------------------------
# Kerdock matrix builder
# ---------------------------------------------------------------------------

def get_kerdock_matrix(N: int, M: int, seed: int) -> np.ndarray:
    """Return A_norm = A / sqrt(N) shape (M, N)."""
    if not _TORCH_OK:
        raise RuntimeError("torch required")
    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    A_t = cb[idx].float() / math.sqrt(N)
    return A_t.numpy()


# ---------------------------------------------------------------------------
# Long-iteration AMP with full trajectory
# ---------------------------------------------------------------------------

def amp_se_scalar_fixed_point(alpha: float, sigma_sq: float, signal_var: float,
                              n_iter: int = 2000, tol: float = 1e-14) -> float:
    """Standard Bayati-Montanari scalar AMP-SE fixed point (no early stop tightness)."""
    tau_sq = sigma_sq + signal_var
    for _ in range(n_iter):
        mse_t = signal_var * tau_sq / (signal_var + tau_sq)
        tau_new = sigma_sq + mse_t / alpha
        if abs(tau_new - tau_sq) < tol * max(abs(tau_sq), 1.0):
            tau_sq = tau_new
            break
        tau_sq = tau_new
    return float(signal_var * tau_sq / (signal_var + tau_sq))


def run_amp_long(A: np.ndarray, y: np.ndarray, x_true: np.ndarray,
                 signal_var: float, sigma_sq: float, n_iter: int) -> dict:
    """Run AMP iteration with FULL trajectory recording (no convergence early-exit)."""
    M, N = A.shape
    alpha = M / N
    x_hat = np.zeros(N)
    z = y.copy()
    mses = []
    tau_eff_history = []
    diverged_flag = False

    for it in range(n_iter):
        r = A.T @ z + x_hat
        tau_eff = max(float(np.mean(z ** 2)) / alpha, 1e-10)
        tau_eff_history.append(tau_eff)
        gain = signal_var / (signal_var + tau_eff)
        x_hat_new = gain * r
        b = gain
        z = y - A @ x_hat_new + (b / alpha) * z
        x_hat = x_hat_new
        mse = float(np.mean((x_hat - x_true) ** 2))
        mses.append(mse)
        # Sentinel: if MSE blows up beyond 1000 * signal_var, stop early to avoid NaN
        if mse > 1000.0 * signal_var or not math.isfinite(mse):
            diverged_flag = True
            break

    return {
        "mse_history": mses,
        "tau_eff_history": tau_eff_history,
        "diverged_flag": diverged_flag,
        "n_iter_completed": len(mses),
    }


def trajectory_metrics(mses: list[float]) -> dict:
    """Compute summary metrics from full MSE trajectory."""
    n = len(mses)
    if n == 0:
        return {}
    mse_arr = np.array(mses)
    out = {
        "mse_final": float(mse_arr[-1]),
        "mse_max": float(mse_arr.max()),
        "mse_min": float(mse_arr.min()),
        "n_iters": n,
    }
    # Snapshot at iter 200 (or last if shorter)
    if n >= 200:
        out["mse_at_200"] = float(mse_arr[199])
    else:
        out["mse_at_200"] = float(mse_arr[-1])
    # Snapshot at iter 1000
    if n >= 1000:
        out["mse_at_1000"] = float(mse_arr[999])
    else:
        out["mse_at_1000"] = float(mse_arr[-1])

    # Oscillation metric: max deviation from running mean over last 100 iters
    if n >= 100:
        last = mse_arr[-100:]
        mean_last = float(last.mean())
        oscillation = float(np.max(np.abs(last - mean_last)))
        out["mse_running_mean_last100"] = mean_last
        out["mse_oscillation_last100"] = oscillation
        out["mse_oscillation_relative"] = oscillation / max(abs(mean_last), 1e-12)
    else:
        out["mse_running_mean_last100"] = float(mse_arr.mean())
        out["mse_oscillation_last100"] = float(mse_arr.std())
        out["mse_oscillation_relative"] = float(mse_arr.std() / max(abs(mse_arr.mean()), 1e-12))

    # Growth rate over last 500 iters: linear fit of log(mse) vs iteration
    if n >= 500:
        last500 = mse_arr[-500:]
        # Guard non-positive values
        pos = np.where(last500 > 0, last500, 1e-12)
        log_mse = np.log(pos)
        xs = np.arange(len(log_mse))
        # slope of log mse per iter
        slope = float(np.polyfit(xs, log_mse, 1)[0])
        out["log_mse_slope_last500"] = slope
    else:
        out["log_mse_slope_last500"] = 0.0

    return out


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """Classify the trajectory shape across cells.

    Per cell:
      EXPLODES: mse_at_1000 > 2 * mse_at_200 AND log_mse_slope_last500 > 0.001
                OR diverged_flag set.
      OSCILLATES: oscillation_relative > 0.20 AND |log_mse_slope_last500| < 0.0005
      FIXED_POINT: oscillation_relative < 0.10 AND mse_at_1000 substantially > se_mse_scalar
                   (>1.5x) -- i.e. plateau at wrong level
      CONVERGES_TO_SE: mse_at_1000 within 20% of se_mse_scalar (overrides v163)
      UNCLEAR: else

    Global verdict picks dominant class.
    """
    if not summary.get("cells"):
        return ("AMP_LONGITER_INCONCLUSIVE", "No cells.")

    classes = {"EXPLODES": 0, "OSCILLATES": 0, "FIXED_POINT": 0,
               "CONVERGES_TO_SE": 0, "UNCLEAR": 0}
    for cell in summary["cells"]:
        m200 = cell.get("mse_at_200_mean")
        m1000 = cell.get("mse_at_1000_mean")
        se = cell.get("se_mse_scalar")
        osc_rel = cell.get("oscillation_relative_mean", 0.0)
        slope = cell.get("log_mse_slope_last500_mean", 0.0)
        div = cell.get("any_diverged", False)
        if m200 is None or m1000 is None or se is None:
            classes["UNCLEAR"] += 1
            cell["traj_class"] = "UNCLEAR"
            continue

        if div or (m1000 > 2.0 * m200 and slope > 0.001):
            cls = "EXPLODES"
        elif osc_rel > 0.20 and abs(slope) < 0.0005:
            cls = "OSCILLATES"
        elif osc_rel < 0.10 and m1000 > 1.5 * se:
            cls = "FIXED_POINT"
        elif se > 0 and abs(m1000 - se) / max(m1000, se, 1e-12) < 0.20:
            cls = "CONVERGES_TO_SE"
        else:
            cls = "UNCLEAR"
        classes[cls] += 1
        cell["traj_class"] = cls

    n = sum(classes.values())
    dom_count = max(classes.values())
    if classes["EXPLODES"] == dom_count and classes["EXPLODES"] >= max(1, n // 2):
        return (
            "AMP_LONGITER_EXPLODES",
            f"AMP-on-Kerdock trajectory EXPLODES at 5x iteration budget. "
            f"{classes['EXPLODES']}/{n} cells show mse_at_1000 >> mse_at_200 with positive "
            f"log-slope. v163's 'AMP_SE_DIVERGES' is a snapshot of runaway dynamics. "
            f"Per-cell: {classes}",
        )
    if classes["OSCILLATES"] == dom_count and classes["OSCILLATES"] >= max(1, n // 2):
        return (
            "AMP_LONGITER_OSCILLATES",
            f"AMP-on-Kerdock trajectory does NOT converge: oscillates with relative amplitude > 20% "
            f"and ~zero net slope. {classes['OSCILLATES']}/{n} cells. Substrate-novel: AMP cycles "
            f"between extrinsic basins; standard scalar-SE fixed point inaccessible. Per-cell: {classes}",
        )
    if classes["FIXED_POINT"] == dom_count and classes["FIXED_POINT"] >= max(1, n // 2):
        return (
            "AMP_LONGITER_FIXED_POINT",
            f"AMP-on-Kerdock converges to a non-SE fixed point. {classes['FIXED_POINT']}/{n} cells "
            f"show <10% oscillation but mse plateau is >1.5x the scalar-SE prediction. v163 "
            f"AMP_SE_DIVERGES is confirmed: a fixed point exists but at a different MSE than "
            f"the universality-class theory says. Per-cell: {classes}",
        )
    if classes["CONVERGES_TO_SE"] == dom_count and classes["CONVERGES_TO_SE"] >= max(1, n // 2):
        return (
            "AMP_LONGITER_CONVERGES_TO_SE",
            f"AMP-on-Kerdock at 5x iters converges WITHIN 20% of scalar-SE prediction. "
            f"{classes['CONVERGES_TO_SE']}/{n} cells. This REVERSES v163: the perceived "
            f"divergence was an under-iteration artefact. Substrate IS in AMP universality. "
            f"Per-cell: {classes}",
        )
    return (
        "AMP_LONGITER_INCONCLUSIVE",
        f"No dominant trajectory class. Per-cell: {classes}",
    )


def self_test() -> None:
    """Verify trajectory_metrics + verdict on synthetic trajectories."""

    # Test 1: trajectory_metrics on a flat plateau
    mses = [0.5] * 1000
    m = trajectory_metrics(mses)
    assert abs(m["mse_at_1000"] - 0.5) < 1e-9
    assert abs(m["mse_at_200"] - 0.5) < 1e-9
    assert m["mse_oscillation_relative"] < 1e-9
    assert abs(m["log_mse_slope_last500"]) < 1e-9

    # Test 2: trajectory_metrics on exponential growth
    mses = [math.exp(0.01 * i) for i in range(1000)]
    m = trajectory_metrics(mses)
    assert m["log_mse_slope_last500"] > 0.005, f"slope={m['log_mse_slope_last500']}"

    # Test 3: trajectory_metrics on oscillation
    mses = [0.5 + 0.3 * math.sin(i * 0.1) for i in range(1000)]
    m = trajectory_metrics(mses)
    assert m["mse_oscillation_relative"] > 0.2, f"osc_rel={m['mse_oscillation_relative']}"
    assert abs(m["log_mse_slope_last500"]) < 0.001

    # Test 4: verdict EXPLODES
    summary = {"cells": [
        {"mse_at_200_mean": 0.5, "mse_at_1000_mean": 5.0, "se_mse_scalar": 0.1,
         "oscillation_relative_mean": 0.1, "log_mse_slope_last500_mean": 0.005,
         "any_diverged": False},
        {"mse_at_200_mean": 0.5, "mse_at_1000_mean": 8.0, "se_mse_scalar": 0.1,
         "oscillation_relative_mean": 0.1, "log_mse_slope_last500_mean": 0.005,
         "any_diverged": False},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "AMP_LONGITER_EXPLODES", f"expected EXPLODES got {v}"

    # Test 5: verdict OSCILLATES
    summary = {"cells": [
        {"mse_at_200_mean": 0.5, "mse_at_1000_mean": 0.5, "se_mse_scalar": 0.1,
         "oscillation_relative_mean": 0.4, "log_mse_slope_last500_mean": 0.0,
         "any_diverged": False},
        {"mse_at_200_mean": 0.5, "mse_at_1000_mean": 0.5, "se_mse_scalar": 0.1,
         "oscillation_relative_mean": 0.4, "log_mse_slope_last500_mean": 0.0,
         "any_diverged": False},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "AMP_LONGITER_OSCILLATES", f"expected OSCILLATES got {v}"

    # Test 6: verdict FIXED_POINT
    summary = {"cells": [
        {"mse_at_200_mean": 0.5, "mse_at_1000_mean": 0.5, "se_mse_scalar": 0.1,
         "oscillation_relative_mean": 0.05, "log_mse_slope_last500_mean": 0.0,
         "any_diverged": False},
        {"mse_at_200_mean": 0.5, "mse_at_1000_mean": 0.5, "se_mse_scalar": 0.1,
         "oscillation_relative_mean": 0.05, "log_mse_slope_last500_mean": 0.0,
         "any_diverged": False},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "AMP_LONGITER_FIXED_POINT", f"expected FIXED_POINT got {v}"

    # Test 7: verdict CONVERGES_TO_SE
    summary = {"cells": [
        {"mse_at_200_mean": 0.10, "mse_at_1000_mean": 0.10, "se_mse_scalar": 0.10,
         "oscillation_relative_mean": 0.05, "log_mse_slope_last500_mean": 0.0,
         "any_diverged": False},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "AMP_LONGITER_CONVERGES_TO_SE", f"expected CONVERGES_TO_SE got {v}"

    # Test 8: empty
    v, _ = compute_verdict({"cells": []})
    assert v == "AMP_LONGITER_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    print("AMP-longiter self-test passed (8/8 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "M_over_N_list": [1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 2,
            "n_iter": 200,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N_list": [1.0, 2.0, 4.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 5,
            "n_iter": 1000,
        }

    N = config["N"]
    sigma_sq = config["sigma_noise"] ** 2
    signal_var = config["signal_var"]

    cells = []
    for alpha in config["M_over_N_list"]:
        M = max(1, int(alpha * N))
        if M > 4 * N:
            print(f"[skip] alpha={alpha:.2f}: M={M} > 4N", flush=True)
            continue
        print(f"\n[alpha={alpha:.2f}] N={N} M={M}", flush=True)

        # Scalar SE fixed point (no spectrum required)
        se_mse = amp_se_scalar_fixed_point(alpha, sigma_sq, signal_var)

        per_seed = []
        any_div = False
        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + int(alpha * 100)
            A = get_kerdock_matrix(N, M, seed=seed_val)
            rng = np.random.default_rng(seed_val + 77)
            x_true = rng.standard_normal(N) * math.sqrt(signal_var)
            noise = rng.standard_normal(M) * config["sigma_noise"]
            y = A @ x_true + noise
            result = run_amp_long(A, y, x_true, signal_var, sigma_sq, n_iter=config["n_iter"])
            metrics = trajectory_metrics(result["mse_history"])
            metrics["diverged_flag"] = result["diverged_flag"]
            per_seed.append(metrics)
            any_div = any_div or result["diverged_flag"]
            print(
                f"  seed={seed} mse@200={metrics.get('mse_at_200', float('nan')):.4f} "
                f"mse@1000={metrics.get('mse_at_1000', float('nan')):.4f} "
                f"osc_rel={metrics.get('mse_oscillation_relative', 0):.3f} "
                f"slope={metrics.get('log_mse_slope_last500', 0):.5f} "
                f"div={result['diverged_flag']}",
                flush=True,
            )

        # Aggregate
        def mean_of(key):
            vals = [m[key] for m in per_seed if key in m and math.isfinite(m[key])]
            return float(np.mean(vals)) if vals else 0.0

        cell = {
            "alpha": float(alpha),
            "N": N, "M": M,
            "se_mse_scalar": float(se_mse),
            "mse_at_200_mean": mean_of("mse_at_200"),
            "mse_at_1000_mean": mean_of("mse_at_1000"),
            "mse_final_mean": mean_of("mse_final"),
            "mse_max_mean": mean_of("mse_max"),
            "oscillation_relative_mean": mean_of("mse_oscillation_relative"),
            "log_mse_slope_last500_mean": mean_of("log_mse_slope_last500"),
            "any_diverged": any_div,
            "n_seeds": config["n_seeds"],
        }
        cells.append(cell)
        print(
            f"  AGGREGATE alpha={alpha:.2f}: SE={se_mse:.4f} mse@200={cell['mse_at_200_mean']:.4f} "
            f"mse@1000={cell['mse_at_1000_mean']:.4f} osc={cell['oscillation_relative_mean']:.3f} "
            f"slope={cell['log_mse_slope_last500_mean']:.5f}",
            flush=True,
        )

    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    env_name = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{env_name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_amp_se_kerdock_longiter_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_amp_se_kerdock_longiter_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
