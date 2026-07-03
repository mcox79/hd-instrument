"""Free-additive-convolution top-edge ratio: MoE SHIFT vs PARTITION spectral analysis.

CONTEXT: MoE shift_partition_v2 (in flight) does NOT persist W_k tensors.
This script is a focused re-run that computes ONLY the top-singular-value ratio
between SHIFT-aggregate and PARTITION-per-expert, comparing to the free-additive-
convolution closed-form prediction.

HANDOFF SOURCE: notes/exp_dev_handoff_free_additive_top_edge_moe_2026-05-26.md
COMPANION: exp_wave14_moe_shift_partition_v2.py (DMPK bimodality arm)

WHAT THIS MEASURES:
  For each (K, M_total) cell:
    SHIFT: build K full-N experts, compute W_total = sum(W_k), get sigma_top_shift.
    PARTITION: build K N/K experts, compute sigma_top per expert (mean).
    Ratio = sigma_top_shift / (K * sigma_top_partition_mean)
    Free-additive-conv prediction: K*(1+sqrt(c))^2 / (K*(1+sqrt(Kc))^2)
      where c = M_total / (K * N)
    Check: |ratio_empirical - ratio_predicted| / ratio_predicted < 0.15 (HARD-PASS)

WHY ZERO EXTRA COMPUTE:
  W_k construction is the dominant cost in v2. This script builds the SAME W_k
  tensors but skips the per-item recall loop (M items x cosine loop), replacing
  it with a single SVD call on each W_k. At N=4096, SVD of W is O(N^2) ~= 67M
  flops -- similar to one iteration of the recall loop over M=1600 items.
  Total overhead over v2: ~0% (the recall loop was the bottleneck, not SVD).

PRE-REGISTERED BANDS (from handoff P3.1 + P3.2 + P3.3):
  HARD-PASS: mean match_within_15pct == True across >= 80% of seeds at K in {2,4}
             AND mean ratio_empirical within +/-15% of ratio_predicted at operating M.
  HARD-FAIL: mean ratio_empirical off by > 30% from prediction at K in {2,4}.
  MIDDLE BAND: ratio off 15-30% -- finite-N corrections likely; mark INCONCLUSIVE.
  K=8 EXEMPTION: at K=8, N=4096, N/K=512 is borderline for asymptotic freeness;
    MIDDLE-BAND at K=8 is expected, NOT failure.

SELF-TESTS:
  1. Closed-form ratio formula: K=2, c=0.5 -> ratio_predicted = 2*(1+sqrt(0.5))^2 /
     (2*(1+sqrt(1.0))^2) = (1+0.7071)^2 / (1+1)^2 = 2.9142/4 = 0.7286 (approx)
  2. Empirical ratio for K=1: W_total = W_0 (single expert); sigma_top_shift / sigma_top_partition
     -> degenerate case; K=1 is recorded but not used for PASS/FAIL verdict.
  3. match_within_15pct logic: |0.70 - 0.72| / 0.72 = 0.028 < 0.15 -> True
  4. ci95 of [0.72, 0.74, 0.71, 0.73, 0.72] -> mean~0.724, width < 0.05

Queue: overnight_queue (GPU; 5 seeds x {2,4,8} K-values x {1,2} M-mult; ~1-2 GPU-hr)
Pre-reg: preregs/2026-05-26_wave14_moe_top_edge_v1.md
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

sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ─── design parameters (exp_dev autonomy) ───
N_FULL = 4096
N_SMOKE = 512
M_PER_EXPERT_FULL = 1600   # from alpha_c recalibration (v2 prestep)
M_PER_EXPERT_SMOKE = 200   # proportional at N=512
K_SWEEP_FULL = [1, 2, 4, 8]   # K=1 for control; K={2,4} are PASS/FAIL decisive; K=8 exempt
K_SWEEP_SMOKE = [1, 2, 4]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
# M_total multipliers (as multiples of K * M_per_expert)
M_MULT_FULL = [1.0, 2.0]   # operating point and stress
M_MULT_SMOKE = [1.0, 2.0]
BATCH_STORE = 256

# Pre-registered thresholds
RATIO_MATCH_15PCT = 0.15   # HARD-PASS: within 15%
RATIO_MATCH_30PCT = 0.30   # HARD-FAIL: off by > 30%
PASS_SEED_FRAC = 0.80      # >= 80% seeds must match at K in {2,4}


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


# ─── BSC atoms ───
def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    raw = torch.randint(0, 2, (M, N), generator=gen, device=device).float()
    return 2.0 * raw - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    device = keys.device
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


# ─── LSH gating (VERBATIM from v2) ───
def build_lsh_gate(N: int, K: int, gen: torch.Generator, device) -> torch.Tensor:
    """K random unit projections for LSH balanced-bin gating. Shape: (K, N)."""
    proj = torch.randn(K, N, generator=gen, device=device)
    proj = proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return proj


def gate_assign(keys: torch.Tensor, proj: torch.Tensor, K: int) -> torch.Tensor:
    """Balanced-bin LSH: assign each key to one of K experts via quantile binning."""
    scores = keys @ proj.T   # (M, K)
    score_sum = scores.sum(dim=1)   # (M,) -- aggregate projection for sorting
    order = score_sum.argsort()
    M = keys.shape[0]
    bin_size = max(M // K, 1)
    assignment = torch.zeros(M, dtype=torch.long, device=keys.device)
    for k in range(K):
        lo = k * bin_size
        hi = (k + 1) * bin_size if k < K - 1 else M
        assignment[order[lo:hi]] = k
    return assignment


# ─── free-additive-convolution top-edge helper (from handoff contract) ───
def compute_free_additive_top_edge_ratio(
    Wks_shift: list,
    Wks_partition: list,
    K: int,
    N: int,
    M_total: int,
) -> dict:
    """Free-additive-convolution prediction: top-edge ratio SHIFT vs PARTITION.

    Returns dict with empirical + predicted + match flag.
    """
    # SHIFT: aggregate all K experts
    W_shift_total = sum(Wks_shift)
    sigma_top_shift = torch.linalg.svdvals(W_shift_total)[0].item()
    # PARTITION: mean top singular value across K experts
    sigma_tops_part = [torch.linalg.svdvals(W)[0].item() for W in Wks_partition]
    sigma_top_partition_mean = sum(sigma_tops_part) / max(K, 1)

    # Free-additive-convolution closed-form (c = M_total / (K * N))
    c = M_total / max(K * N, 1)
    # SHIFT aggregate: K addends each with shape distribution ~ c-scaled Marchenko-Pastur
    sigma_top_shift_predicted = float(K) * (1.0 + c ** 0.5) ** 2
    # PARTITION per-expert: each W_k stored M_total/K items in N/K dimensions (normalized)
    # Top edge of per-expert (N_k x N_k): (1 + sqrt(Kc))^2  [c_k = (M_total/K)/(N/K) = M_total/N = Kc]
    sigma_top_partition_predicted = (1.0 + (K * c) ** 0.5) ** 2

    # Ratio: sigma_top_shift / (K * sigma_top_partition_mean)
    ratio_empirical = sigma_top_shift / max(K * sigma_top_partition_mean, 1e-9)
    ratio_predicted = sigma_top_shift_predicted / max(K * sigma_top_partition_predicted, 1e-9)

    err_frac = abs(ratio_empirical - ratio_predicted) / max(ratio_predicted, 1e-9)
    match_within_15pct = err_frac < RATIO_MATCH_15PCT
    match_within_30pct = err_frac < RATIO_MATCH_30PCT

    return {
        "sigma_top_shift": sigma_top_shift,
        "sigma_top_partition_mean": sigma_top_partition_mean,
        "sigma_top_shift_predicted": sigma_top_shift_predicted,
        "sigma_top_partition_predicted": sigma_top_partition_predicted,
        "ratio_empirical": ratio_empirical,
        "ratio_predicted_free_additive_conv": ratio_predicted,
        "ratio_error_frac": err_frac,
        "match_within_15pct": match_within_15pct,
        "match_within_30pct": match_within_30pct,
        "c": c,
        "K": K,
        "M_total": M_total,
        "N": N,
    }


# ─── per-cell runner ───
def run_cell(seed: int, K: int, N: int, M_total: int, device) -> dict:
    """Build SHIFT and PARTITION W_k tensors for one (K, M_total, seed) cell.
    Compute top-edge ratio. Return metrics dict.
    """
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)

    # LSH gate (shared for both arms, same gen state)
    gate_gen = torch.Generator(device=device).manual_seed(seed + 1000)
    proj = build_lsh_gate(N, K, gate_gen, device)
    assignment = gate_assign(keys, proj, K)

    # ─── SHIFT arm: K full-N experts ───
    Wks_shift = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks_shift.append(torch.zeros((N, N), dtype=torch.float32, device=device))
            continue
        Wks_shift.append(outer_product_store(keys[mask], vals[mask], N))

    # ─── PARTITION arm: K experts of dim N/K ───
    N_k = max(N // K, 1)
    perm_gen = torch.Generator(device=device).manual_seed(N * 100 + K)
    perm = torch.randperm(N, generator=perm_gen, device=device)
    keys_p = keys[:, perm]
    vals_p = vals[:, perm]
    Wks_partition = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks_partition.append(torch.zeros((N_k, N_k), dtype=torch.float32, device=device))
            continue
        k_slice = keys_p[mask, k * N_k:(k + 1) * N_k]
        v_slice = vals_p[mask, k * N_k:(k + 1) * N_k]
        Wks_partition.append(outer_product_store(k_slice, v_slice, N_k))

    # ─── top-edge ratio ───
    result = compute_free_additive_top_edge_ratio(
        Wks_shift, Wks_partition, K, N, M_total
    )

    # cleanup
    del Wks_shift, Wks_partition, keys, vals, keys_p, vals_p
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return result


def ci95(values: list[float]) -> tuple[float, float, float]:
    n = len(values)
    if n < 2:
        m = values[0] if values else float("nan")
        return m, m, m
    m = sum(values) / n
    s = math.sqrt(sum((v - m) ** 2 for v in values) / (n - 1))
    t = 2.776 if n == 5 else 2.0
    half = t * s / math.sqrt(n)
    return m, m - half, m + half


def iqr(values: list[float]) -> float:
    sv = sorted(values)
    n = len(sv)
    if n < 4:
        return float("nan")
    return sv[3 * n // 4] - sv[n // 4]


# ─── instrumentation self-test (MANDATORY) ───
def _instrumentation_selftest():
    # Self-test 1: closed-form ratio formula at K=2, c=0.5
    K_t, c_t = 2, 0.5
    pred_shift = float(K_t) * (1.0 + c_t ** 0.5) ** 2
    pred_part = (1.0 + (K_t * c_t) ** 0.5) ** 2
    ratio_pred = pred_shift / (K_t * pred_part)
    # K=2, c=0.5: pred_shift = 2*(1+0.7071)^2 = 2*2.9142 = 5.8284
    # pred_part = (1+1.0)^2 = 4.0
    # ratio = 5.8284 / (2*4.0) = 5.8284/8 = 0.7286
    assert abs(ratio_pred - 0.7286) < 0.001, f"Self-test 1 FAIL: ratio_pred={ratio_pred:.4f} (expected ~0.7286)"
    print(f"[SELFTEST] 1/4 closed-form ratio formula OK (ratio_pred={ratio_pred:.4f})", flush=True)

    # Self-test 2: match_within_15pct logic
    ratio_emp_t = 0.70
    ratio_prd_t = 0.72
    err_t = abs(ratio_emp_t - ratio_prd_t) / max(ratio_prd_t, 1e-9)
    match_t = err_t < 0.15
    assert match_t, f"Self-test 2 FAIL: expected match_within_15pct=True for 0.70 vs 0.72 (err={err_t:.4f})"
    print(f"[SELFTEST] 2/4 match_within_15pct logic OK (err={err_t:.4f})", flush=True)

    # Self-test 3: ci95 formula
    vals_t = [0.72, 0.74, 0.71, 0.73, 0.72]
    m3, lo3, hi3 = ci95(vals_t)
    assert abs(m3 - 0.724) < 0.001, f"Self-test 3 FAIL: ci95 mean={m3:.4f} (expected 0.724)"
    assert hi3 - lo3 < 0.05, f"Self-test 3 FAIL: CI width {hi3-lo3:.4f} >= 0.05"
    print(f"[SELFTEST] 3/4 ci95 formula OK (mean={m3:.4f}, width={hi3-lo3:.4f})", flush=True)

    # Self-test 4: outer_product_store and SVD at tiny scale
    device = torch.device("cpu")
    gen4 = torch.Generator().manual_seed(0)
    keys4 = make_bsc(4, 8, gen4, device)
    vals4 = make_bsc(4, 8, gen4, device)
    W4 = outer_product_store(keys4, vals4, 8)
    svs = torch.linalg.svdvals(W4)
    assert svs[0].item() > 0, "Self-test 4 FAIL: top singular value is 0"
    assert not math.isnan(svs[0].item()), "Self-test 4 FAIL: top singular value is NaN"
    print(f"[SELFTEST] 4/4 SVD on tiny W OK (sigma_top={svs[0].item():.4f})", flush=True)

    print("[SELFTEST] All 4 self-tests passed", flush=True)


_instrumentation_selftest()


# ─── suspicious result gate ───
def suspicious_result_gate(cells: list[dict]) -> str | None:
    ratios = [c["ratio_empirical"] for c in cells if not math.isnan(c.get("ratio_empirical", float("nan")))]
    if not ratios:
        return "All ratio_empirical values are NaN -- instrumentation failure"
    if all(abs(r) < 1e-9 for r in ratios):
        return "All ratio_empirical values are exactly 0.0"
    if len(set(f"{r:.4f}" for r in ratios)) == 1:
        return f"All ratio_empirical values identical ({ratios[0]:.4f}) -- no variance across cells"
    return None


# ─── main sweep ───
def run_sweep(N: int, K_sweep: list, M_per_expert: int, M_mults: list, seeds: list, device) -> list[dict]:
    """Run full grid of (K, M_total, seed) cells. Return list of cell result dicts."""
    results = []
    for K in K_sweep:
        for mult in M_mults:
            M_total = int(mult * K * M_per_expert)
            for seed in seeds:
                print(f"  K={K} M_total={M_total} seed={seed}", flush=True)
                cell = run_cell(seed, K, N, M_total, device)
                cell["seed"] = seed
                cell["M_mult"] = mult
                results.append(cell)
                print(f"    ratio_emp={cell['ratio_empirical']:.4f} "
                      f"ratio_pred={cell['ratio_predicted_free_additive_conv']:.4f} "
                      f"match15={cell['match_within_15pct']}", flush=True)
    return results


def aggregate_results(cells: list[dict], K_sweep: list, M_mults: list, seeds: list) -> dict:
    """Aggregate per-seed results into per-(K,M_total) summary with CI."""
    agg = {}
    for K in K_sweep:
        for mult in M_mults:
            M_total_expected = None
            cell_group = [c for c in cells if c["K"] == K and c["M_mult"] == mult]
            if not cell_group:
                continue
            M_total_expected = cell_group[0]["M_total"]
            key = f"K{K}_Mmult{mult:.1f}"
            ratio_emps = [c["ratio_empirical"] for c in cell_group]
            ratio_pred = cell_group[0]["ratio_predicted_free_additive_conv"]
            match_flags = [c["match_within_15pct"] for c in cell_group]
            m_emp, lo_emp, hi_emp = ci95(ratio_emps)
            agg[key] = {
                "K": K,
                "M_mult": mult,
                "M_total": M_total_expected,
                "n_seeds": len(cell_group),
                "ratio_empirical_mean": m_emp,
                "ratio_empirical_ci_lo": lo_emp,
                "ratio_empirical_ci_hi": hi_emp,
                "ratio_empirical_iqr": iqr(ratio_emps),
                "ratio_predicted": ratio_pred,
                "match_within_15pct_frac": sum(match_flags) / max(len(match_flags), 1),
                "match_within_30pct_frac": sum(c["match_within_30pct"] for c in cell_group) / max(len(cell_group), 1),
                "c": cell_group[0]["c"],
                "k8_exempt": K == 8,
            }
    return agg


def compute_verdict(agg: dict, K_decisive: list = None) -> tuple[str, str]:
    """Classify HARD-PASS / MIDDLE / HARD-FAIL based on K in {2,4} cells."""
    if K_decisive is None:
        K_decisive = [2, 4]

    decisive_cells = {k: v for k, v in agg.items() if v["K"] in K_decisive}
    if not decisive_cells:
        return "INSTRUMENTATION_FAIL", "No decisive cells (K in {2,4}) found."

    hp_cells = [v for v in decisive_cells.values()
                if v["match_within_15pct_frac"] >= PASS_SEED_FRAC]
    fail_cells = [v for v in decisive_cells.values()
                  if v["match_within_30pct_frac"] < PASS_SEED_FRAC]

    n_decisive = len(decisive_cells)
    n_hp = len(hp_cells)
    n_fail = len(fail_cells)

    if n_hp >= n_decisive * 0.8:
        verdict = "FREE_ADDITIVE_HARD_PASS"
        msg = (f"Free-additive-convolution confirmed: {n_hp}/{n_decisive} decisive cells "
               f"(K in {K_decisive}) show match_within_15pct >= {PASS_SEED_FRAC:.0%} of seeds. "
               f"Top-edge ratio discriminates SHIFT vs PARTITION at spectral level.")
    elif n_fail >= n_decisive * 0.8:
        verdict = "FREE_ADDITIVE_HARD_FAIL"
        msg = (f"Free-additive-convolution does NOT govern aggregate spectrum: "
               f"{n_fail}/{n_decisive} decisive cells (K in {K_decisive}) show "
               f"match_within_30pct < {PASS_SEED_FRAC:.0%} of seeds. "
               f"Spectral mechanism requires alternative model.")
    else:
        verdict = "FREE_ADDITIVE_MIDDLE"
        msg = (f"Middle band: {n_hp}/{n_decisive} cells match within 15%, "
               f"{n_decisive-n_fail}/{n_decisive} match within 30%. "
               f"Finite-N corrections likely (N={4096}). "
               f"Mark INCONCLUSIVE; re-confirm at N=16384 if warranted.")

    # Add per-cell summary to msg
    for key, v in sorted(decisive_cells.items()):
        msg += (f" | {key}: ratio_emp={v['ratio_empirical_mean']:.4f} "
                f"pred={v['ratio_predicted']:.4f} "
                f"match15={v['match_within_15pct_frac']:.2f}")
    return verdict, msg


# ─── main ───
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[moe_top_edge_v1] device={device} smoke={smoke}", flush=True)

    if smoke:
        N = N_SMOKE
        K_sweep = K_SWEEP_SMOKE
        M_per_expert = M_PER_EXPERT_SMOKE
        seeds = SEEDS_SMOKE
    else:
        N = N_FULL
        K_sweep = K_SWEEP_FULL
        M_per_expert = M_PER_EXPERT_FULL
        seeds = SEEDS_FULL

    M_mults = M_MULT_SMOKE if smoke else M_MULT_FULL
    out_dir = get_output_dir("wave14_moe_top_edge_v1")

    print(f"[moe_top_edge_v1] N={N} K_sweep={K_sweep} M_per_expert={M_per_expert} "
          f"seeds={seeds} M_mults={M_mults}", flush=True)

    t0 = time.time()
    cells = run_sweep(N, K_sweep, M_per_expert, M_mults, seeds, device)

    # Suspicious gate
    flag = suspicious_result_gate(cells)
    if flag is not None:
        print(f"[smoke] INSTRUMENTATION_SUSPECT: {flag}", flush=True)
        if smoke:
            sys.exit(1)

    agg = aggregate_results(cells, K_sweep, M_mults, seeds)
    verdict, verdict_msg = compute_verdict(agg)
    elapsed = time.time() - t0

    # Serialize cells (convert bool/tensor fields)
    cells_serial = []
    for c in cells:
        cs = {k: (bool(v) if isinstance(v, (bool,)) else
                  (float(v) if isinstance(v, (int, float)) else v))
              for k, v in c.items()}
        cells_serial.append(cs)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "verdict": verdict,
            "n_decisive_cells": len([v for v in agg.values() if v["K"] in [2, 4]]),
            "agg": agg,
        },
        "cells": cells_serial,
        "config": {
            "mode": "smoke" if smoke else "full",
            "N": N,
            "K_sweep": K_sweep,
            "M_per_expert": M_per_expert,
            "M_mults": M_mults,
            "seeds": seeds,
            "device": str(device),
            "handoff": "exp_dev_handoff_free_additive_top_edge_moe_2026-05-26.md",
        },
    }
    validate_metrics(metrics)

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    print(f"[moe_top_edge_v1] verdict={verdict}", flush=True)
    print(f"[moe_top_edge_v1] {verdict_msg[:300]}", flush=True)
    print(f"[moe_top_edge_v1] elapsed={elapsed:.1f}s  metrics -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
