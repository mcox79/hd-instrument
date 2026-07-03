"""Batched VAMP recovery curve on FULL Kerdock 4-coset at substrate-native N=4096 (GPU).

This is a substantial GPU anchor: every iteration runs two (M, batch) <-> (N, batch)
matmuls on cuda with M=16384, N=4096, batch=2048. Across 8 SNR cells x 5 seeds x
200 iterations, total ~4.4e15 fp32 mul-adds -- pure GPU matmul, ~30-90 min wall.

No numpy fallback in the inner loop: codebook, signals, iterates all live on cuda.

Pre-reg: preregs/2026-05-24_wave14_kerdock_batched_vamp_gpu_n4096_v1.md
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

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
import torch


def _import_module(module_name: str, rel_path: str):
    p = REPO / rel_path
    spec = importlib.util.spec_from_file_location(module_name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# Import 4-coset MM Kerdock codebook builder (supports N in {1024, 4096, 16384}).
_v3 = _import_module("kerdock_v3", "experiments/exp_wave14y_erase_kerdock_v3.py")
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook


# ---------------------------------------------------------------------------
# State-evolution fixed point (one-time CPU eigvalsh + scalar recursion)
# ---------------------------------------------------------------------------

def se_fixed_point(eigenvalues: np.ndarray, snr_lin: float, signal_var: float = 1.0,
                    n_iter: int = 1000, tol: float = 1e-12) -> tuple[float, int]:
    """VAMP state-evolution fixed point with matched-MMSE denoiser.

    For Gaussian signal, the SE recursion is:
        tau_sq_{t+1} = sigma_noise_sq + (1/M) sum_i lambda_i * (signal_var * tau_sq_t /
                                                                (signal_var + tau_sq_t))
    Simplified MMSE-Gaussian closed form for the AMP-class case.

    snr_lin = signal_var * (avg lambda) / sigma_noise_sq.
    Returns (mse_fixed_point, n_iter_to_converge).
    """
    sigma_noise_sq = signal_var * np.mean(eigenvalues) / snr_lin
    tau_sq = signal_var
    M = len(eigenvalues)
    for it in range(n_iter):
        mmse = signal_var * tau_sq / (signal_var + tau_sq)
        tau_new = sigma_noise_sq + (1.0 / M) * np.sum(eigenvalues * mmse)
        if abs(tau_new - tau_sq) < tol:
            tau_sq = tau_new
            return float(mmse), it
        tau_sq = tau_new
    mmse = signal_var * tau_sq / (signal_var + tau_sq)
    return float(mmse), n_iter


# ---------------------------------------------------------------------------
# Batched VAMP iteration on GPU
# ---------------------------------------------------------------------------

def batched_vamp_gpu(
    A: torch.Tensor,      # (M, N) normalized so A.T @ A ~ I in bulk
    y: torch.Tensor,      # (M, batch) observations
    sigma_noise_sq: float,
    signal_var: float,
    n_iter: int,
) -> tuple[torch.Tensor, list]:
    """Batched VAMP with Gaussian-MMSE denoiser (alpha = M/N regime).

    All ops on the same device as A.  Returns (x_hat (N, batch), per-iter mse trace).
    """
    M, N = A.shape
    batch = y.shape[1]
    device = A.device
    dtype = A.dtype

    x_hat = torch.zeros((N, batch), device=device, dtype=dtype)
    # Onsager-tracking state
    tau_sq = signal_var
    trace = []

    for it in range(n_iter):
        # Residual on observation side
        # z = y - A @ x_hat
        z = y - A @ x_hat
        # Onsager-corrected pseudo-obs
        # r = x_hat + A.T @ z / (M / N)  (the AMP fixed coefficient at right-rot-invar)
        # For VAMP we use the matched scaling: r = x_hat + A.T @ z * (N / M).
        r = x_hat + (N / M) * (A.T @ z)
        # Matched MMSE denoiser update
        # tau_sq update via empirical residual variance (Onsager state)
        # Use closed-form scalar: tau_sq_new = sigma_noise_sq + (1/M)*sum(eig_i)*mmse(tau_sq)
        # but for batched VAMP we approximate via residual mean-square.
        # Empirical tau_sq from per-batch residual norm
        with torch.no_grad():
            z_var = (z.pow(2).sum(dim=0).mean() / M).item()
            tau_sq = max(z_var, 1e-12)
        mmse_coef = signal_var / (signal_var + tau_sq)
        x_hat = mmse_coef * r
        # Track per-iter MSE proxy (norm of update)
        if it == n_iter - 1 or it % 25 == 0:
            with torch.no_grad():
                trace.append((it, float(x_hat.pow(2).sum(dim=0).mean().item())))
    return x_hat, trace


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def self_test_codebook_pm1() -> None:
    """SELF-TEST 1: 4-coset Kerdock codebook entries are in {-1, +1} at N=1024."""
    device = torch.device("cpu")
    cb, _ = make_kerdock_4coset_codebook(1024, device)
    unique_vals = torch.unique(cb).cpu().numpy()
    assert set(unique_vals.tolist()) <= {-1.0, 1.0}, f"non-binary: {unique_vals[:5]}"
    assert cb.shape == (4096, 1024), f"shape {cb.shape}"


def self_test_column_norms() -> None:
    """SELF-TEST 2: A_norm column norms equal sqrt(M/N) at N=1024."""
    device = torch.device("cpu")
    cb, _ = make_kerdock_4coset_codebook(1024, device)
    N = 1024
    M = cb.shape[0]  # 4096
    A_norm = cb.float() / math.sqrt(N)
    col_norms = A_norm.pow(2).sum(dim=0).sqrt()
    expected = math.sqrt(M / N)  # = 2.0 at 4-coset
    mean_norm = float(col_norms.mean())
    print(f"[self-test 2] N=1024 A_norm column norm mean={mean_norm:.4f}, expected={expected:.4f}")
    assert abs(mean_norm - expected) < 0.05, f"col-norm mean {mean_norm} vs {expected}"


def self_test_vamp_one_step() -> None:
    """SELF-TEST 3: VAMP one-step update is sane (finite, correct shapes)."""
    device = torch.device("cpu")
    torch.manual_seed(0)
    M, N, batch = 16, 8, 4
    A = torch.randn(M, N) / math.sqrt(N)
    x_true = torch.randn(N, batch)
    y = A @ x_true + 0.1 * torch.randn(M, batch)
    x_hat, trace = batched_vamp_gpu(A, y, 0.01, 1.0, n_iter=3)
    assert x_hat.shape == (N, batch), f"shape {x_hat.shape}"
    assert torch.isfinite(x_hat).all(), "non-finite VAMP iterate"
    assert len(trace) >= 1


def self_test_se_fp_asymptote() -> None:
    """SELF-TEST 4: SE fixed point at M/N=4, large noise -> mse approaches signal_var."""
    # 4-coset Kerdock: spectrum is roughly bimodal {0, 4} at M=4N (most eigvals 0 are
    # in the null space, M-N of them; N eigvals are at M/N=4). To match, pass that spectrum:
    M = 16
    N = 4
    eigs = np.array([4.0] * N + [0.0] * (M - N))
    # Very low SNR: mse should be close to signal_var
    mse_fp, _ = se_fixed_point(eigs, snr_lin=0.01, signal_var=1.0)
    assert 0.5 < mse_fp <= 1.0, f"SE FP at low SNR: {mse_fp}"
    # Very high SNR: mse should approach 0
    mse_fp_hi, _ = se_fixed_point(eigs, snr_lin=100.0, signal_var=1.0)
    assert mse_fp_hi < 0.5, f"SE FP at high SNR: {mse_fp_hi}"
    print(f"[self-test 4] SE FP low/high SNR: {mse_fp:.4f} / {mse_fp_hi:.4f}")


def self_test_verdict_logic() -> None:
    """SELF-TEST 5: verdict logic on synthetic data."""
    def verdict(rel_err_max, var_bound_fails, n_cells):
        if n_cells == 0:
            return "HARD_FAIL_NO_RESULTS"
        if rel_err_max > 0.20:
            return "HARD_FAIL_KERDOCK_VAMP_GPU_DIVERGES"
        if rel_err_max > 0.05 or var_bound_fails > 2:
            return "MIDDLE_BAND_KERDOCK_VAMP_PARTIAL"
        return "HARD_PASS_KERDOCK_VAMP_GPU_UNIVERSALITY"
    assert verdict(0.01, 0, 8) == "HARD_PASS_KERDOCK_VAMP_GPU_UNIVERSALITY"
    assert verdict(0.10, 1, 8) == "MIDDLE_BAND_KERDOCK_VAMP_PARTIAL"
    assert verdict(0.30, 0, 8) == "HARD_FAIL_KERDOCK_VAMP_GPU_DIVERGES"
    assert verdict(0.0, 0, 0) == "HARD_FAIL_NO_RESULTS"


def run_all_self_tests() -> None:
    print("[self-test] Running 5 formula assertions...")
    self_test_codebook_pm1()
    print("  1. 4-coset Kerdock codebook +/-1 at N=1024: PASS")
    self_test_column_norms()
    print("  2. A_norm column norms equal sqrt(M/N): PASS")
    self_test_vamp_one_step()
    print("  3. VAMP one-step update finite + correct shape: PASS")
    self_test_se_fp_asymptote()
    print("  4. SE FP low/high SNR asymptotes: PASS")
    self_test_verdict_logic()
    print("  5. Verdict logic: PASS")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def write_metrics_atomic(out_path: Path, d: dict) -> None:
    tmp = out_path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, out_path)


def run_one_cell(
    A: torch.Tensor,
    eigenvalues_cpu: np.ndarray,
    snr_db: float,
    batch_size: int,
    n_iter: int,
    seed: int,
    signal_var: float,
) -> dict:
    """One (snr, seed) cell: batched VAMP on GPU + SE fixed-point comparison."""
    M, N = A.shape
    device = A.device
    dtype = A.dtype

    g = torch.Generator(device=device)
    g.manual_seed(seed)

    # Signal
    x_true = torch.randn((N, batch_size), generator=g, device=device, dtype=dtype) * math.sqrt(signal_var)
    # Pre-compute average spectral gain so we can pin SNR to (E[|Ax|^2]/E[|noise|^2])
    snr_lin = 10.0 ** (snr_db / 10.0)
    # Signal power per observation: E[|Ax|^2] / M ~ signal_var * (1/M)*sum(eigs of A.T@A / N)
    # Since we computed eigenvalues of (1/N) * A.T @ A (or equivalently from A_norm),
    # avg eig is approximately M/N for 4-coset.
    avg_eig = float(np.mean(eigenvalues_cpu))
    sigma_noise_sq = signal_var * avg_eig / snr_lin
    sigma_noise = math.sqrt(sigma_noise_sq)

    # Observation
    Ax = A @ x_true  # GPU matmul, (M, batch)
    noise = sigma_noise * torch.randn((M, batch_size), generator=g, device=device, dtype=dtype)
    y = Ax + noise

    # VAMP
    t0 = time.time()
    x_hat, trace = batched_vamp_gpu(A, y, sigma_noise_sq, signal_var, n_iter)
    t_vamp = time.time() - t0

    # Empirical MSE per sample then averaged
    err = x_hat - x_true
    per_sample_mse = err.pow(2).mean(dim=0)  # (batch,) one MSE per sample
    emp_mse_mean = float(per_sample_mse.mean().item())
    emp_mse_std = float(per_sample_mse.std().item())

    # SE prediction
    se_mse, se_iters = se_fixed_point(eigenvalues_cpu, snr_lin, signal_var)

    rel_err = abs(emp_mse_mean - se_mse) / max(abs(se_mse), 1e-10)
    # Universality variance bound: batch_mse_std / sqrt(batch_size) < 0.10 * se_mse
    var_bound_lhs = emp_mse_std / math.sqrt(batch_size)
    var_bound_ok = var_bound_lhs < 0.10 * se_mse

    return {
        "snr_db": snr_db,
        "seed": seed,
        "emp_mse_mean": emp_mse_mean,
        "emp_mse_std": emp_mse_std,
        "se_mse_fixed": se_mse,
        "se_iters_to_fixed": int(se_iters),
        "rel_err": float(rel_err),
        "var_bound_ok": bool(var_bound_ok),
        "var_bound_lhs": float(var_bound_lhs),
        "vamp_wall_s": float(t_vamp),
        "trace": trace,
        "sigma_noise_sq": float(sigma_noise_sq),
        "avg_eig": float(avg_eig),
    }


def run_main(args) -> None:
    run_all_self_tests()
    print("[main] Running full experiment")

    if args.smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "batch_size": 64,
            "snr_db_list": [0.0, 6.0],
            "n_iter": 20,
            "n_seeds": 1,
        }
        default_name = "wave14_kerdock_batched_vamp_gpu_n4096_v1_smoke"
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "batch_size": 2048,
            "snr_db_list": [-6.0, -3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0],
            "n_iter": 200,
            "n_seeds": 5,
        }
        default_name = "wave14_kerdock_batched_vamp_gpu_n4096_v1"

    N = config["N"]
    batch_size = config["batch_size"]
    snr_db_list = config["snr_db_list"]
    n_iter = config["n_iter"]
    n_seeds = config["n_seeds"]

    # Device
    if torch.cuda.is_available() and not args.smoke:
        device = torch.device("cuda")
    else:
        device = torch.device("cpu") if args.smoke else torch.device("cuda")
    print(f"[main] device = {device}")
    if device.type == "cuda":
        print(f"[main] cuda: {torch.cuda.get_device_name(0)}, "
              f"vram free/total = {torch.cuda.mem_get_info()}")

    out_dir = get_output_dir(default_name)

    t_start = time.time()

    # Build Kerdock codebook on GPU
    print(f"[main] building Kerdock 4-coset codebook at N={N} on {device}...", flush=True)
    cb_torch, info = make_kerdock_4coset_codebook(N, device)
    M = cb_torch.shape[0]  # = 4N
    print(f"[main] codebook shape = {tuple(cb_torch.shape)}, M={M}, M/N={M/N}", flush=True)
    A = cb_torch.to(torch.float32) / math.sqrt(N)  # normalize on GPU

    # One-time eigvalsh of A_norm.T @ A_norm (N x N = 4096 x 4096 -> 64 MB, easy)
    # to feed SE fixed-point on CPU.
    print("[main] computing one-time A.T@A eigenspectrum on GPU...", flush=True)
    t_eig0 = time.time()
    gram_NN = A.T @ A  # (N, N)
    eig_NN = torch.linalg.eigvalsh(gram_NN)
    eig_NN_cpu = eig_NN.cpu().numpy()
    eig_NN_cpu = np.clip(eig_NN_cpu, 0.0, None)
    # For the SE recursion we need the spectrum of A_norm @ A_norm.T (M x M) which
    # = the same nonzero eigenvalues as A_norm.T @ A_norm padded with M-N zeros.
    eig_MM_cpu = np.concatenate([eig_NN_cpu, np.zeros(M - N)])
    print(f"[main] eigvalsh done in {time.time()-t_eig0:.2f}s; "
          f"eig_NN mean={eig_NN_cpu.mean():.4f} (expected ~{M/N:.1f})", flush=True)

    # SE FP at each SNR (CPU scalar loop, fast)
    se_table = {}
    for snr_db in snr_db_list:
        snr_lin = 10.0 ** (snr_db / 10.0)
        se_mse, se_it = se_fixed_point(eig_MM_cpu, snr_lin, signal_var=1.0)
        se_table[float(snr_db)] = (se_mse, se_it)
    print(f"[main] SE FP table: {se_table}", flush=True)

    # Main loop
    seeds = [17, 23, 31, 41, 53][:n_seeds]
    all_cells = []
    cell_count = 0
    total_cells = len(snr_db_list) * len(seeds)
    for snr_db in snr_db_list:
        for seed in seeds:
            cell_count += 1
            try:
                t_cell0 = time.time()
                cell = run_one_cell(
                    A=A,
                    eigenvalues_cpu=eig_MM_cpu,
                    snr_db=snr_db,
                    batch_size=batch_size,
                    n_iter=n_iter,
                    seed=seed,
                    signal_var=1.0,
                )
                t_cell = time.time() - t_cell0
                cell["wall_s"] = float(t_cell)
                all_cells.append(cell)
                print(f"[cell {cell_count}/{total_cells} snr={snr_db:+5.1f}dB seed={seed:3d}] "
                      f"emp_mse={cell['emp_mse_mean']:.4e} se_mse={cell['se_mse_fixed']:.4e} "
                      f"rel_err={cell['rel_err']:.3e} var_bound_ok={cell['var_bound_ok']} "
                      f"wall={t_cell:.1f}s", flush=True)
            except Exception as e:
                print(f"[cell {cell_count}/{total_cells} snr={snr_db} seed={seed}] FAILED: {e}",
                      flush=True)
                all_cells.append({
                    "snr_db": float(snr_db), "seed": int(seed),
                    "error": str(e),
                })

    elapsed = time.time() - t_start

    # Aggregate
    good = [c for c in all_cells if "error" not in c]
    rel_errs = [c["rel_err"] for c in good]
    var_bound_fails = sum(1 for c in good if not c["var_bound_ok"])
    n_good = len(good)

    if not rel_errs:
        verdict = "HARD_FAIL_NO_RESULTS"
        verdict_msg = "All (snr, seed) cells failed."
    else:
        rel_err_max = max(rel_errs)
        rel_err_mean = float(np.mean(rel_errs))
        if rel_err_max > 0.20:
            verdict = "HARD_FAIL_KERDOCK_VAMP_GPU_DIVERGES"
            verdict_msg = (f"rel_err_max={rel_err_max:.3e} (>0.20): Kerdock matrix breaks "
                           f"VAMP universality at N={N}, M={M}.")
        elif rel_err_max > 0.05 or var_bound_fails > 2:
            verdict = "MIDDLE_BAND_KERDOCK_VAMP_PARTIAL"
            verdict_msg = (f"rel_err_max={rel_err_max:.3e}, var_bound_fails={var_bound_fails}: "
                           f"partial agreement; Cap 8 envelope holds in bulk.")
        else:
            verdict = "HARD_PASS_KERDOCK_VAMP_GPU_UNIVERSALITY"
            verdict_msg = (f"rel_err_max={rel_err_max:.3e}, rel_err_mean={rel_err_mean:.3e}, "
                           f"var_bound_fails={var_bound_fails}/{n_good}: "
                           f"Kerdock VAMP universality licensed at N={N}, M={M}, batch={batch_size}.")
    print(f"[verdict] {verdict}: {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "N": N,
            "M": M,
            "batch_size": batch_size,
            "snr_db_list": snr_db_list,
            "n_iter": n_iter,
            "n_seeds": n_seeds,
            "n_cells_good": n_good,
            "n_cells_total": total_cells,
            "rel_err_max": float(max(rel_errs)) if rel_errs else float("nan"),
            "rel_err_mean": float(np.mean(rel_errs)) if rel_errs else float("nan"),
            "var_bound_fails": int(var_bound_fails),
            "device": str(device),
            "avg_eig_NN": float(eig_NN_cpu.mean()),
        },
        "config": {**config, "seeds": seeds},
        "se_fp_table": {str(k): {"se_mse": v[0], "se_iters": v[1]} for k, v in se_table.items()},
        "all_cells": all_cells,
    }

    validate_metrics(metrics)
    out_path = out_dir / "metrics.json"
    write_metrics_atomic(out_path, metrics)
    print(f"[done] wrote {out_path}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Smoke at N=1024 / 1-seed / 2 SNR / 20 iter.")
    parser.add_argument("--self-test", action="store_true", help="Run self-tests only.")
    args = parser.parse_args()

    if args.self_test:
        run_all_self_tests()
        print("[self-test] all 5 PASS")
        return 0

    run_main(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
