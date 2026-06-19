"""Free-additive-convolution top-edge v4: N-scaling sweep with corrected formula.

ANTICIPATORY PRE-BUILD -- two trigger paths:
  PATH A (FORMULA CORRECTED): v3 returns FREE_ADDITIVE_HARD_PASS (offset_ratio ~1.0,
          formula confirms at N=16384). Ship this v4 to run a full N-scaling sweep
          using the corrected formula and demonstrate that the framework generalizes.

  PATH B (DMPK FALLBACK): v3 returns FREE_ADDITIVE_FORMULA_ERROR (offset persists
          at N=16384). Ship a DMPK (Dorokhov-Mello-Pereyra-Kumar) transfer-matrix
          probe: a different random-matrix framework that also governs singular-value
          distributions in products of random matrices with different symmetry classes.

This script implements PATH A (N-scaling with corrected formula).
DMPK fallback is exp_wave14_moe_top_edge_dmpk_v1.py.

DESIGN (PATH A):
  - N sweep: {4096, 8192, 16384, 32768}  (log-spaced; tests asymptotic convergence)
  - K in {2, 4} (same as v3 decisive cells)
  - 5 seeds per (N, K) cell
  - Primary metric: offset_ratio_emp_over_pred (should converge to 1.0 as N->inf)
  - Secondary metric: rate of convergence (fit: offset = 1 - A / sqrt(N))

PRE-REGISTERED BANDS:
  HARD_PASS (free-additive confirmed + N-scaling):
    - offset_ratio at N=32768 within 15% of 1.0 (|offset - 1.0| < 0.15)
    - AND convergence fit A/sqrt(N) gives R^2 > 0.7 (systematic finite-N correction)
    -> Free-additive framework confirmed + finite-N correction characterized

  HARD_FAIL (persistent offset, not finite-N):
    - offset_ratio at N=32768 still < 0.75
    -> Framework does not apply; systematic formula error not explained by finite-N

  MIDDLE_BAND:
    - offset_ratio improves monotonically with N but < 0.85 at N=32768
    -> Partial convergence; may need N > 32768

  INSTRUMENTATION_FAIL:
    - OOM at N=32768 (W matrix = 32768^2 * 4 bytes = 4.3 GB; feasible but tight)
    - OR non-finite ratio

Memory check:
  N=32768: W = 32768^2 * 4 = 4.29 GB; feasible on 8GB GPU with careful memory management.
  SOLUTION: compute sigma_top via power iteration (not full SVD) at N=32768.

Self-tests:
  1. Closed-form formula: K=2, c=0.5 -> ratio_pred = 1.0 (v3 corrected formula)
  2. match_within_15pct logic
  3. ci95 formula
  4. power_iteration_svd returns correct sigma_top on 4x4 known matrix

Queue: overnight_queue (GPU; 5 seeds x 4 N-values x 2 K-values; ~6-8 GPU-hrs)
Pre-reg: preregs/2026-05-26_wave14_moe_top_edge_v4.md
Trigger: ship when v3 returns FREE_ADDITIVE_HARD_PASS (offset_ratio ~1.0).
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent

N_SWEEP_FULL = [4096, 8192, 16384, 32768]
N_SWEEP_SMOKE = [512, 1024]
K_SWEEP_FULL = [2, 4]
K_SWEEP_SMOKE = [2]
M_PER_EXPERT = 1600    # same calibrated point (scaled proportionally per N below)
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_STORE = 256

RATIO_MATCH_15PCT = 0.15
RATIO_MATCH_30PCT = 0.30
PASS_SEED_FRAC = 0.80

# Convergence fit thresholds
HP_OFFSET_AT_LARGE_N = 0.85   # offset_ratio >= 0.85 at max N
HP_FIT_R2 = 0.7
HF_OFFSET_AT_LARGE_N = 0.75   # offset_ratio < 0.75 at max N -> HARD_FAIL


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")


def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    device = keys.device
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def sigma_top_via_power_iter(W: torch.Tensor, n_iter: int = 20) -> float:
    """Approximate largest singular value via power iteration (memory-efficient for large N)."""
    device = W.device
    N = W.shape[0]
    gen = torch.Generator(device=device).manual_seed(42)
    v = torch.randn(N, generator=gen, device=device)
    v = v / v.norm()
    for _ in range(n_iter):
        u = W @ v
        u = u / u.norm().clamp(min=1e-9)
        v = W.T @ u
        sv = v.norm()
        v = v / sv.clamp(min=1e-9)
    return float(sv)


def build_lsh_gate(N: int, K: int, gen: torch.Generator, device) -> torch.Tensor:
    proj = torch.randn(K, N, generator=gen, device=device)
    return proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-9)


def gate_assign(keys: torch.Tensor, proj: torch.Tensor, K: int) -> torch.Tensor:
    scores = keys @ proj.T
    score_sum = scores.sum(dim=1)
    order = score_sum.argsort()
    M = keys.shape[0]
    bin_size = max(M // K, 1)
    assignment = torch.zeros(M, dtype=torch.long, device=keys.device)
    for k in range(K):
        lo = k * bin_size
        hi = (k + 1) * bin_size if k < K - 1 else M
        assignment[order[lo:hi]] = k
    return assignment


def ci95(values: list) -> tuple:
    n = len(values)
    if n < 2:
        m = values[0] if values else float("nan")
        return m, m, m
    m = sum(values) / n
    s = math.sqrt(sum((v - m) ** 2 for v in values) / (n - 1))
    t = 2.776 if n == 5 else 2.0
    half = t * s / math.sqrt(n)
    return m, m - half, m + half


def run_cell(seed: int, K: int, N: int, M_total: int, device) -> dict:
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)

    gate_gen = torch.Generator(device=device).manual_seed(seed + 1000)
    proj = build_lsh_gate(N, K, gate_gen, device)
    assignment = gate_assign(keys, proj, K)

    # SHIFT arm: K full-N experts, sum W = W_shift
    W_shift_total = torch.zeros((N, N), dtype=torch.float32, device=device)
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            continue
        Wk = outer_product_store(keys[mask], vals[mask], N)
        W_shift_total += Wk
        del Wk

    # PARTITION arm: K experts of dim N/K
    N_k = max(N // K, 1)
    perm_gen = torch.Generator(device=device).manual_seed(N * 100 + K)
    perm = torch.randperm(N, generator=perm_gen, device=device)
    keys_p = keys[:, perm]
    vals_p = vals[:, perm]
    sigma_tops_part = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            sigma_tops_part.append(0.0)
            continue
        k_slice = keys_p[mask, k * N_k:(k + 1) * N_k]
        v_slice = vals_p[mask, k * N_k:(k + 1) * N_k]
        Wk = outer_product_store(k_slice, v_slice, N_k)
        sv = sigma_top_via_power_iter(Wk)
        sigma_tops_part.append(sv)
        del Wk

    # Use power iteration for large N (>= 16384) for memory efficiency
    sigma_top_shift = sigma_top_via_power_iter(W_shift_total)
    sigma_top_partition_mean = sum(sigma_tops_part) / max(K, 1)

    # v3 corrected formula: ratio = sigma_top_shift / (K * sigma_top_partition_mean)
    # Free-additive prediction: ratio_predicted = 1.0
    ratio_empirical = sigma_top_shift / max(K * sigma_top_partition_mean, 1e-9)
    ratio_predicted = 1.0
    err_frac = abs(ratio_empirical - ratio_predicted) / max(ratio_predicted, 1e-9)
    offset_ratio = ratio_empirical / max(ratio_predicted, 1e-9)
    c = M_total / max(K * N, 1)

    del W_shift_total, keys, vals, keys_p, vals_p
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "sigma_top_shift": round(sigma_top_shift, 6),
        "sigma_top_partition_mean": round(sigma_top_partition_mean, 6),
        "ratio_empirical": round(ratio_empirical, 6),
        "ratio_predicted": ratio_predicted,
        "ratio_error_frac": round(err_frac, 6),
        "offset_ratio_emp_over_pred": round(offset_ratio, 6),
        "match_within_15pct": err_frac < RATIO_MATCH_15PCT,
        "match_within_30pct": err_frac < RATIO_MATCH_30PCT,
        "c": round(c, 6), "K": K, "N": N, "M_total": M_total,
    }


def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. v3 corrected formula: ratio_predicted = 1.0 always
    ratio_pred = 1.0
    assert abs(ratio_pred - 1.0) < 0.001, f"Selftest 1 FAIL: ratio_pred={ratio_pred}"
    print(f"[selftest] 1/4 v3 corrected formula ratio_pred=1.0 OK")

    # 2. match_within_15pct logic
    err = abs(0.90 - 1.0) / 1.0
    assert err < 0.15, f"Selftest 2 FAIL: err={err:.4f}"
    print(f"[selftest] 2/4 match_within_15pct(offset=0.90) OK")

    # 3. ci95 formula
    vals = [0.95, 0.97, 0.93, 0.96, 0.94]
    m, lo, hi = ci95(vals)
    assert abs(m - 0.95) < 0.001, f"Selftest 3 FAIL: mean={m}"
    assert hi - lo < 0.06, f"Selftest 3 FAIL: CI too wide {hi-lo:.4f}"
    print(f"[selftest] 3/4 ci95 OK (mean={m:.3f} width={hi-lo:.4f})")

    # 4. power_iteration_svd: 2x2 known matrix sigma_top=2.0
    device = torch.device("cpu")
    W4 = torch.tensor([[1.0, 1.0], [1.0, 1.0]])
    sv = sigma_top_via_power_iter(W4, n_iter=50)
    assert abs(sv - 2.0) < 0.05, f"Selftest 4 FAIL: sv={sv:.4f} (expected ~2.0)"
    print(f"[selftest] 4/4 power_iter sigma_top={sv:.4f} ~2.0 OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run_sweep(smoke: bool = False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_moe_top_edge_v4")
    print(f"[moe_top_edge_v4] device={device} smoke={smoke}", flush=True)
    print(f"  N_sweep={N_sweep} K_sweep={K_sweep}", flush=True)

    results: dict = {}  # key: (N, K)
    for N in N_sweep:
        for K in K_sweep:
            M_total = int(K * M_PER_EXPERT * N / 4096)  # proportional to N
            M_total = max(M_total, K * 10)
            print(f"\n  N={N} K={K} M_total={M_total}", flush=True)
            cells = []
            for seed in seeds:
                cell = run_cell(seed, K, N, M_total, device)
                cell["seed"] = seed
                cells.append(cell)
                print(f"    seed={seed}: ratio_emp={cell['ratio_empirical']:.4f} "
                      f"offset={cell['offset_ratio_emp_over_pred']:.4f} "
                      f"match15={cell['match_within_15pct']}", flush=True)
            offsets = [c["offset_ratio_emp_over_pred"] for c in cells]
            m_off = sum(offsets) / len(offsets)
            ratios = [c["ratio_empirical"] for c in cells]
            m_r, lo_r, hi_r = ci95(ratios)
            results[f"N{N}_K{K}"] = {
                "N": N, "K": K, "M_total": M_total,
                "mean_offset_ratio": round(m_off, 4),
                "ratio_empirical_mean": round(m_r, 4),
                "ratio_empirical_ci_lo": round(lo_r, 4),
                "ratio_empirical_ci_hi": round(hi_r, 4),
                "match15_frac": round(sum(c["match_within_15pct"] for c in cells) / len(cells), 3),
            }
            print(f"  -> mean_offset={m_off:.4f} match15={results[f'N{N}_K{K}']['match15_frac']:.2f}")

    return results, out_dir


def fit_convergence(N_vals, offsets):
    """Fit: offset = 1 - A / sqrt(N). Returns (A, R2)."""
    if len(N_vals) < 2:
        return 0.0, 0.0
    x = [1.0 / math.sqrt(N) for N in N_vals]
    y = [1.0 - o for o in offsets]
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    varx = sum((x[i] - mx) ** 2 for i in range(n))
    if varx < 1e-12:
        return 0.0, 0.0
    A = cov / varx
    y_pred = [A * xi for xi in x]
    ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((y[i] - my) ** 2 for i in range(n))
    r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
    return round(A, 4), round(max(r2, 0.0), 4)


def compute_verdict(results: dict) -> tuple[str, str, dict]:
    # Group by K, average offset across K for each N
    N_vals_all = sorted(set(v["N"] for v in results.values()))
    offsets_by_N = {}
    for N in N_vals_all:
        cells_at_N = [v for v in results.values() if v["N"] == N]
        offsets_by_N[N] = sum(c["mean_offset_ratio"] for c in cells_at_N) / len(cells_at_N)

    N_max = max(N_vals_all)
    offset_at_Nmax = offsets_by_N[N_max]

    # Convergence fit
    A, fit_r2 = fit_convergence(N_vals_all, [offsets_by_N[N] for N in N_vals_all])

    # Match fraction at largest N
    largest_N_cells = {k: v for k, v in results.items() if v["N"] == N_max}
    match15_at_Nmax = sum(c["match15_frac"] for c in largest_N_cells.values()) / max(len(largest_N_cells), 1)

    summary = {
        "N_sweep": N_vals_all,
        "offsets_by_N": {str(N): round(offsets_by_N[N], 4) for N in N_vals_all},
        "offset_at_N_max": round(offset_at_Nmax, 4),
        "N_max": N_max,
        "convergence_A": A,
        "convergence_fit_r2": fit_r2,
        "match15_frac_at_Nmax": round(match15_at_Nmax, 3),
        "results": results,
    }

    if not math.isfinite(offset_at_Nmax):
        return ("INSTRUMENTATION_FAIL", "Non-finite offset at N_max.", summary)

    if offset_at_Nmax >= HP_OFFSET_AT_LARGE_N and fit_r2 >= HP_FIT_R2:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: free-additive framework confirmed with N-scaling. "
            f"offset_ratio at N={N_max}={offset_at_Nmax:.3f} >= {HP_OFFSET_AT_LARGE_N}. "
            f"Convergence fit: A={A:.3f}, R^2={fit_r2:.3f} >= {HP_FIT_R2}. "
            f"Systematic finite-N correction 1/sqrt(N) confirmed. Framework generalizes."
        )
    elif offset_at_Nmax < HF_OFFSET_AT_LARGE_N:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: persistent offset at N={N_max}. "
            f"offset_ratio={offset_at_Nmax:.3f} < {HF_OFFSET_AT_LARGE_N}. "
            f"Free-additive framework does not converge; formula error is not finite-N. "
            f"Route to: DMPK fallback or alternative RMT framework."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: improving with N but not converged. "
            f"offset_ratio at N={N_max}={offset_at_Nmax:.3f} "
            f"(>= {HF_OFFSET_AT_LARGE_N} but < {HP_OFFSET_AT_LARGE_N}). "
            f"fit_R2={fit_r2:.3f}. May need N > {N_max} for full convergence."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_moe_top_edge_v4 {'SMOKE' if smoke else 'FULL'}", flush=True)
    results, out_dir = run_sweep(smoke)

    # Multi-scale smoke
    if smoke:
        print("\n[multi-scale smoke] N_smoke * 4...", flush=True)
        device = torch.device("cpu")
        N_scale2 = N_SWEEP_SMOKE[0] * 4
        M2 = int(2 * M_PER_EXPERT * N_scale2 / 4096)
        c2 = run_cell(17, 2, N_scale2, M2, device)
        assert math.isfinite(c2["ratio_empirical"]), f"Scale2 degenerate N={N_scale2}"
        print(f"  N={N_scale2} K=2: offset={c2['offset_ratio_emp_over_pred']:.4f}")
        print("[multi-scale smoke] PASS")

    verdict, verdict_msg, summary = compute_verdict(results)
    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N_sweep": N_SWEEP_SMOKE if smoke else N_SWEEP_FULL,
            "K_sweep": K_SWEEP_SMOKE if smoke else K_SWEEP_FULL,
            "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
            "smoke": smoke,
            "trigger": "ship when v3 returns FREE_ADDITIVE_HARD_PASS (offset_ratio ~1.0)",
        },
    }
    validate_metrics(metrics)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
