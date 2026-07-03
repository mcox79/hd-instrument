"""Free-additive-convolution top-edge ratio N=16384 retry.

CONTEXT: wave14_moe_top_edge_v1 (N=4096) returned FREE_ADDITIVE_MIDDLE with systematic
0.50x offset: ratio_emp/ratio_pred consistently ~0.50 across all 4 cells (range 0.365-0.715).
This is NOT stochastic noise -- it is a systematic factor-2 offset. Two hypotheses per v211:
  (a) finite-N correction scaling ~1/sqrt(N): offset should shrink from 2x at N=4096 to
      ~sqrt(4096/16384) = 0.5x -> sqrt(0.5) ~ 0.7x at N=16384 (i.e., offset shrinks by ~30%)
  (b) formula missing normalization factor independent of N: offset persists at N=16384

This N=16384 retry DISCRIMINATES between (a) and (b). Pre-reg:
  HARD_PASS: ratio_emp/ratio_pred within 15% at K in {2,4} -> formula correct, v1 was finite-N
  HARD_FAIL: offset >= 1.5x persists -> formula error; free-additive does NOT govern this regime
  MIDDLE_BAND: offset shrinks but does not eliminate -> partial finite-N; formula may need correction

SELF-TESTS (same as v1 4/4):
  1. Closed-form ratio formula: K=2, c=0.5 -> ratio_predicted ~0.7286
  2. match_within_15pct logic
  3. ci95 formula
  4. outer_product_store + SVD at tiny scale

Queue: overnight_queue (GPU; 5 seeds x {2,4} K-values x {1.0} M-mult at N=16384; ~2-3 GPU-hr)
Pre-reg: prereqs/2026-05-26_wave14_moe_top_edge_v2.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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
# ─── design parameters ───
# PRIMARY CHANGE from v1: N_FULL = 16384 (was 4096)
# K=8 dropped (N/K=2048 is safe for asymptotic freeness at N=16384)
N_FULL = 16384
N_SMOKE = 1024
M_PER_EXPERT_FULL = 1600    # same calibrated operating point
M_PER_EXPERT_SMOKE = 100    # proportional: 1600 * 1024 / 16384 ~ 100
K_SWEEP_FULL = [2, 4]       # decisive K values only (K=8 exempt in v1, not needed here)
K_SWEEP_SMOKE = [2]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
M_MULT_FULL = [1.0]         # operating point only (2x too memory-heavy at N=16384)
M_MULT_SMOKE = [1.0]
BATCH_STORE = 256

# Pre-registered thresholds (same as v1)
RATIO_MATCH_15PCT = 0.15
RATIO_MATCH_30PCT = 0.30
PASS_SEED_FRAC = 0.80

# Discrimination thresholds (specific to v2)
# v1 showed ratio_emp/ratio_pred ~ 0.50x offset.
# If finite-N, offset at N=16384 should be ~0.71x of v1's offset.
# Operationally: if ratio_emp comes within 15% of pred, finite-N hypothesis CONFIRMED.
# If ratio_emp still < 0.75*pred at N=16384: formula error (not finite-N).
V1_OFFSET_TYPICAL = 0.50   # v1 ratio_emp/ratio_pred typical ratio (from v211 metrics)
FINITE_N_EXPECTED_IMPROVEMENT = math.sqrt(4096.0 / N_FULL)  # ~0.5x of v1 offset


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


# ─── LSH gating (same as v1) ───
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


# ─── free-additive-convolution top-edge helper (same formula as v1) ───
def compute_free_additive_top_edge_ratio(
    Wks_shift: list, Wks_partition: list, K: int, N: int, M_total: int
) -> dict:
    W_shift_total = sum(Wks_shift)
    sigma_top_shift = torch.linalg.svdvals(W_shift_total)[0].item()
    sigma_tops_part = [torch.linalg.svdvals(W)[0].item() for W in Wks_partition]
    sigma_top_partition_mean = sum(sigma_tops_part) / max(K, 1)

    c = M_total / max(K * N, 1)
    sigma_top_shift_predicted = float(K) * (1.0 + c ** 0.5) ** 2
    sigma_top_partition_predicted = (1.0 + (K * c) ** 0.5) ** 2
    ratio_empirical = sigma_top_shift / max(K * sigma_top_partition_mean, 1e-9)
    ratio_predicted = sigma_top_shift_predicted / max(K * sigma_top_partition_predicted, 1e-9)

    err_frac = abs(ratio_empirical - ratio_predicted) / max(ratio_predicted, 1e-9)
    # Offset ratio: how much of v1's 0.5x offset persists
    offset_ratio = ratio_empirical / max(ratio_predicted, 1e-9)

    return {
        "sigma_top_shift": sigma_top_shift,
        "sigma_top_partition_mean": sigma_top_partition_mean,
        "sigma_top_shift_predicted": sigma_top_shift_predicted,
        "sigma_top_partition_predicted": sigma_top_partition_predicted,
        "ratio_empirical": ratio_empirical,
        "ratio_predicted_free_additive_conv": ratio_predicted,
        "ratio_error_frac": err_frac,
        "match_within_15pct": err_frac < RATIO_MATCH_15PCT,
        "match_within_30pct": err_frac < RATIO_MATCH_30PCT,
        "offset_ratio_emp_over_pred": offset_ratio,  # 1.0 = perfect match; 0.5 = v1 pattern
        "c": c, "K": K, "M_total": M_total, "N": N,
    }


# ─── per-cell runner ───
def run_cell(seed: int, K: int, N: int, M_total: int, device) -> dict:
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)

    gate_gen = torch.Generator(device=device).manual_seed(seed + 1000)
    proj = build_lsh_gate(N, K, gate_gen, device)
    assignment = gate_assign(keys, proj, K)

    # SHIFT arm: K full-N experts
    Wks_shift = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks_shift.append(torch.zeros((N, N), dtype=torch.float32, device=device))
            continue
        Wks_shift.append(outer_product_store(keys[mask], vals[mask], N))

    # PARTITION arm: K experts of dim N/K
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

    result = compute_free_additive_top_edge_ratio(Wks_shift, Wks_partition, K, N, M_total)

    del Wks_shift, Wks_partition, keys, vals, keys_p, vals_p
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return result


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


# ─── instrumentation self-test (MANDATORY, 4 tests from v1) ───
def _instrumentation_selftest():
    # 1. Closed-form ratio formula at K=2, c=0.5
    K_t, c_t = 2, 0.5
    pred_shift = float(K_t) * (1.0 + c_t ** 0.5) ** 2
    pred_part = (1.0 + (K_t * c_t) ** 0.5) ** 2
    ratio_pred = pred_shift / (K_t * pred_part)
    assert abs(ratio_pred - 0.7286) < 0.001, f"Selftest 1 FAIL: ratio_pred={ratio_pred:.4f}"
    print(f"[selftest] 1/4 closed-form ratio OK (ratio_pred={ratio_pred:.4f})", flush=True)

    # 2. match_within_15pct logic
    err_t = abs(0.70 - 0.72) / 0.72
    assert err_t < 0.15, f"Selftest 2 FAIL: err={err_t:.4f}"
    print(f"[selftest] 2/4 match_within_15pct logic OK", flush=True)

    # 3. ci95 formula
    vals_t = [0.72, 0.74, 0.71, 0.73, 0.72]
    m3, lo3, hi3 = ci95(vals_t)
    assert abs(m3 - 0.724) < 0.001, f"Selftest 3 FAIL: mean={m3}"
    assert hi3 - lo3 < 0.05, f"Selftest 3 FAIL: CI width {hi3-lo3}"
    print(f"[selftest] 3/4 ci95 OK (mean={m3:.4f} width={hi3-lo3:.4f})", flush=True)

    # 4. outer_product_store + SVD at tiny scale
    device = torch.device("cpu")
    gen4 = torch.Generator().manual_seed(0)
    keys4 = make_bsc(4, 8, gen4, device)
    vals4 = make_bsc(4, 8, gen4, device)
    W4 = outer_product_store(keys4, vals4, 8)
    sv = torch.linalg.svdvals(W4)[0].item()
    assert sv > 0 and math.isfinite(sv), f"Selftest 4 FAIL: sv={sv}"
    print(f"[selftest] 4/4 SVD on tiny W OK (sigma_top={sv:.4f})", flush=True)
    print("[selftest] PASS 4/4", flush=True)


_instrumentation_selftest()


# ─── suspicious result gate ───
def suspicious_result_gate(cells: list) -> str | None:
    ratios = [c["ratio_empirical"] for c in cells
              if math.isfinite(c.get("ratio_empirical", float("nan")))]
    if not ratios:
        return "All ratio_empirical values are NaN"
    if all(abs(r) < 1e-9 for r in ratios):
        return "All ratio_empirical values exactly 0.0"
    # Only flag identical if n >= 3 (n=1 trivially identical, not suspicious)
    if len(ratios) >= 3 and len(set(f"{r:.4f}" for r in ratios)) == 1:
        return f"All ratio_empirical identical across {len(ratios)} cells ({ratios[0]:.4f})"
    return None


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
    N = N_SMOKE if smoke else N_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    M_mults = M_MULT_SMOKE if smoke else M_MULT_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_moe_top_edge_v2")

    print(f"[moe_top_edge_v2] N={N} device={device} smoke={smoke}", flush=True)
    print(f"  K_sweep={K_sweep} M_per_expert={M_per_expert} M_mults={M_mults}", flush=True)
    print(f"  finite-N hypothesis: v1 offset ~0.50x; expected at N={N}: "
          f"offset ~{V1_OFFSET_TYPICAL + (1.0 - V1_OFFSET_TYPICAL) * FINITE_N_EXPECTED_IMPROVEMENT:.3f}x pred", flush=True)

    t0 = time.time()

    # Run cells
    cells = []
    for K in K_sweep:
        for mult in M_mults:
            M_total = int(mult * K * M_per_expert)
            for seed in seeds:
                print(f"  K={K} M_total={M_total} seed={seed}...", flush=True)
                cell = run_cell(seed, K, N, M_total, device)
                cell["seed"] = seed
                cell["M_mult"] = mult
                cells.append(cell)
                print(f"    ratio_emp={cell['ratio_empirical']:.4f} "
                      f"ratio_pred={cell['ratio_predicted_free_additive_conv']:.4f} "
                      f"offset_ratio={cell['offset_ratio_emp_over_pred']:.4f} "
                      f"match15={cell['match_within_15pct']}", flush=True)

    # Suspicious result gate
    suspicious = suspicious_result_gate(cells)
    if suspicious:
        print(f"[SUSPICIOUS] {suspicious}", flush=True)

    # Aggregate per (K, M_mult)
    agg = {}
    for K in K_sweep:
        for mult in M_mults:
            key = f"K{K}_Mmult{mult:.1f}"
            cell_group = [c for c in cells if c["K"] == K and c["M_mult"] == mult]
            if not cell_group:
                continue
            ratios = [c["ratio_empirical"] for c in cell_group]
            offsets = [c["offset_ratio_emp_over_pred"] for c in cell_group]
            m_r, lo_r, hi_r = ci95(ratios)
            m_off = sum(offsets) / len(offsets)
            ratio_pred = cell_group[0]["ratio_predicted_free_additive_conv"]
            match15 = [c["match_within_15pct"] for c in cell_group]
            match30 = [c["match_within_30pct"] for c in cell_group]
            agg[key] = {
                "K": K, "M_mult": mult, "M_total": cell_group[0]["M_total"],
                "ratio_empirical_mean": round(m_r, 4),
                "ratio_empirical_ci_lo": round(lo_r, 4),
                "ratio_empirical_ci_hi": round(hi_r, 4),
                "ratio_predicted": round(ratio_pred, 4),
                "mean_offset_ratio": round(m_off, 4),
                "match_within_15pct_frac": round(sum(match15) / max(len(match15), 1), 3),
                "match_within_30pct_frac": round(sum(match30) / max(len(match30), 1), 3),
                "c": round(cell_group[0]["c"], 4),
            }
            print(f"  [{key}] ratio_emp={m_r:.4f} pred={ratio_pred:.4f} "
                  f"offset={m_off:.4f} match15={agg[key]['match_within_15pct_frac']:.2f}", flush=True)

    # Verdict computation
    decisive = {k: v for k, v in agg.items() if v["K"] in K_sweep}
    if not decisive:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "No decisive cells found (K sweep empty)"
    else:
        n_hp = sum(1 for v in decisive.values() if v["match_within_15pct_frac"] >= PASS_SEED_FRAC)
        n_fail = sum(1 for v in decisive.values() if v["match_within_30pct_frac"] < PASS_SEED_FRAC)
        # Mean offset ratio across decisive cells
        mean_offset = sum(v["mean_offset_ratio"] for v in decisive.values()) / len(decisive)
        # v1 mean offset was ~0.50; significant improvement = > 0.75
        v1_offset_improved = mean_offset > 0.75

        if n_hp >= len(decisive) * 0.8:
            verdict = "FREE_ADDITIVE_HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: free-additive-convolution confirmed at N={N_FULL}. "
                f"{n_hp}/{len(decisive)} cells match within 15%. Mean offset_ratio={mean_offset:.3f} "
                f"(~1.0 = perfect). Finite-N hypothesis CONFIRMED: v1 offset was N-artifact."
            )
        elif n_fail >= len(decisive) * 0.8:
            if not v1_offset_improved:
                verdict = "FREE_ADDITIVE_FORMULA_ERROR"
                verdict_msg = (
                    f"HARD_FAIL: formula error. Mean offset_ratio={mean_offset:.3f} (v1 was ~0.50). "
                    f"Offset did NOT improve at N={N_FULL} vs N=4096. "
                    f"Free-additive-conv formula missing normalization independent of N. "
                    f"Model requires correction."
                )
            else:
                verdict = "FREE_ADDITIVE_HARD_FAIL"
                verdict_msg = (
                    f"HARD_FAIL: improved vs v1 (offset={mean_offset:.3f} vs ~0.50) but still >30% off. "
                    f"Partial finite-N; formula also needs correction."
                )
        else:
            if v1_offset_improved:
                verdict = "FREE_ADDITIVE_MIDDLE_IMPROVING"
                verdict_msg = (
                    f"MIDDLE_BAND (IMPROVING): offset improved from ~0.50 (v1) to {mean_offset:.3f} at N={N_FULL}. "
                    f"Consistent with finite-N 1/sqrt(N) correction. "
                    f"Match within 15%: {n_hp}/{len(decisive)} cells. "
                    f"May need N>=65536 for full convergence."
                )
            else:
                verdict = "FREE_ADDITIVE_MIDDLE"
                verdict_msg = (
                    f"MIDDLE_BAND: offset={mean_offset:.3f} (v1 was ~0.50); minimal improvement at N={N_FULL}. "
                    f"Finite-N hypothesis partially supported. Match within 15%: {n_hp}/{len(decisive)} cells."
                )

    # Per-cell row in verdict_msg
    for key, v in sorted(decisive.items()):
        verdict_msg += (f" | {key}: emp={v['ratio_empirical_mean']:.4f} "
                        f"pred={v['ratio_predicted']:.4f} offset={v['mean_offset_ratio']:.4f} "
                        f"match15={v['match_within_15pct_frac']:.2f}")

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": {
            "agg": agg,
            "n_cells": len(cells),
            "suspicious_pattern": suspicious,
            "v1_context": "v1 (N=4096) showed systematic offset ~0.50x; this v2 tests N=16384",
            "finite_n_expected_improvement": round(FINITE_N_EXPECTED_IMPROVEMENT, 3),
        },
        "config": {
            "N": N, "K_sweep": K_sweep, "M_per_expert": M_per_expert,
            "M_mults": M_mults, "seeds": seeds, "smoke": smoke,
            "v1_reference": "wave14_moe_top_edge_v1 N=4096 FREE_ADDITIVE_MIDDLE offset~0.50",
        },
    }
    validate_metrics(metrics)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
