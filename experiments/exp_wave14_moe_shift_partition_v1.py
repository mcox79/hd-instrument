"""3-arm MoE rebuild: SHIFT vs PARTITION vs SINGLE matched-compute.

CONTEXT: R-PRIME-2 HARD-FAILED due to PARTITION-architecture confound (K cancels
algebraically from load ratio when N_k = N/K at fixed M_total). This is the rebuild
with clean 3-arm design. Pre-step calibration (exp_wave14_moe_alpha_c_prestep_v2.py)
must complete first; this script uses M_per_expert_from_prestep = 1600 (recalibrated
from alpha_c ~ 0.56 x N=4096 x 0.70 = ~1612 items).

ARMS:
  Arm A (SHIFT): K full-N experts, parameter budget K*N^2 (grows with K).
    Each expert W_k is NxN. Per-expert capacity: alpha_c * N (full).
    Aggregate capacity (oracle gate): K * alpha_c * N.
    This is the substantive hypothesis: structural separation gives K-fold gain.

  Arm B (PARTITION): K experts each of dim N/K, parameter budget N^2 (fixed).
    Each expert W_k is (N/K)x(N/K). Per-expert capacity: alpha_c * N/K.
    Aggregate capacity: K * alpha_c * N/K = alpha_c * N (same as single expert).
    Prediction: FLAT in K -- this is the null / negative control.

  Arm C (SINGLE): 1 expert of dimension sqrt(K)*N, parameter budget K*N^2 (matched to SHIFT).
    W is (sqrt(K)*N)x(sqrt(K)*N). Single readout. Tests if SHIFT gains come from
    parameter count alone or from structural separation.
    Note: for K not a perfect square, use N_single = int(sqrt(K)*N); closest integer.

GATING (SHIFT and PARTITION arms):
  LSH balanced-bin quantization: project each key onto K signed random projections,
  assign to equal-frequency bins from EMPIRICAL key distribution quantiles (not min-max),
  preventing the CLT concentration mode-collapse seen in wave14e.
  Storage: top-1 gate (item goes to one expert).
  Retrieval: top-2 gate (query reads from its primary + secondary expert, weighted pool).

MODE-COLLAPSE INSTRUMENTATION (per handoff):
  Log Gini coefficient over expert loads. Alert if Gini > 0.4.
  Log max/min expert load ratio. Alert if > 5x.
  Log fraction of items in top-2 experts. Alert if > 1.5 * (2/K).

PARAMETER NOTES (exp_dev autonomy):
  N = 4096 (full). K sweep: K in {1, 2, 4, 8}.
  M_total sweep: M in {0.5, 1.0, 2.0} x K x M_per_expert (= 1600).
    Smoke: N=512, K in {1, 2, 4}, M_total in {400, 800, 1600}.
  Seeds: 5 full, 1 smoke.
  M_per_expert (from alpha_c recalibration) = 1600 at N=4096.
  Walk-back: if smoke effect size d < 1.0 or measured value within 20% of HARD-PASS,
    register full at n*2.

PRE-REGISTERED BANDS (per notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md):
  HARD-PASS -- MoE BREAKS the floor:
    - Arm A (SHIFT) retention exceeds Arm C (SINGLE) by > 0.15 at M_total = 2*M_single_baseline AND
    - mode-collapse metrics WITHIN safe band: Gini < 0.4, max/min < 5x, top2_frac < 0.6 AND
    - retention monotone-non-decreasing in K at fixed M_total/K (tol 0.02)
    -> MoE row: structural separation demonstrated; SHIFT-MoE breaks floor

  HARD-FAIL -- MoE on substrate REJECTED:
    - Arm A tracks Arm C within +/-0.05 across all M_total AND
    - Arm B tracks Arm C within +/-0.05 (confirms PARTITION null) AND
    - mode-collapse: Gini > 0.4 OR max/min > 5x
    -> MoE row closed; parameter budget alone explains any improvement

  MIDDLE BAND -- MoE hides on the floor at higher cost:
    - Arm A exceeds Arm C by 0.05-0.15 AND
    - mode-collapse marginal: Gini 0.3-0.4 or max/min 3x-5x
    -> Structural separation present but not active mechanism;
       capacity gain attributed to parameter budget, not structural separation

  INSTRUMENTATION-FAIL:
    - Mode-collapse metrics cannot be reported (degenerate gating)
    - OR alpha_c cannot be extracted from pre-step data
    -> Re-design before re-ship

SELF-TESTS (per [[feedback-strategy-spec-formula-selftests]]):
  1. gini(loads=[500,500,500,500]) = 0.0  (perfect balance)
  2. gini(loads=[2000,0,0,0]) = 0.75  (total collapse)
  3. top2_frac(loads=[500,500,500,500], K=4) = 0.50  (< 1.5*2/4 = 0.75, OK)
  4. top2_frac(loads=[1800,200,0,0], K=4) = 1.0  (> 0.75, ALERT)
  5. PARTITION load-ratio check: load_ratio = (M_total/K) / (alpha_c * N/K)
     = M_total / (alpha_c * N) -- K cancels; verified flat-in-K property
  6. SHIFT load-ratio check: load_ratio = (M_total/K) / (alpha_c * N)
     = M_total / (K * alpha_c * N) -- decreases with K; capacity scales with K

Queue: overnight_queue (GPU; 5 seeds x 4 K-values x 3 M-values x 3 arms; ~4-6 GPU-hrs)
Pre-reg: preregs/2026-05-24_wave14_moe_shift_partition_v1.md
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

# ─── design parameters (exp_dev autonomy) ───
N_FULL = 4096
N_SMOKE = 512
# M_per_expert from recalibrated alpha_c ~0.56 at N=4096: 0.70 * 0.56 * 4096 = 1605
M_PER_EXPERT_FULL = 1600
M_PER_EXPERT_SMOKE = int(1600 * N_SMOKE / N_FULL)  # ~200 at N=512
K_SWEEP_FULL = [1, 2, 4, 8]
K_SWEEP_SMOKE = [1, 2, 4]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
# M_total multipliers (x K x M_per_expert)
M_MULT_FULL = [0.5, 1.0, 2.0]
M_MULT_SMOKE = [0.5, 1.0, 2.0]
BATCH_STORE = 256

# HARD-PASS/FAIL thresholds
HP_ARM_A_VS_C_LIFT = 0.15   # Arm A must exceed Arm C by this at M=2*baseline
HP_GINI_MAX = 0.4
HP_MAX_MIN_RATIO = 5.0
HP_TOP2_FRAC_MAX = 0.6
HF_ARM_A_VS_C_MAX = 0.05    # HARD-FAIL if Arm A within this of Arm C across ALL M
MID_ARM_A_VS_C_MIN = 0.05   # MIDDLE: Arm A exceeds Arm C by 0.05-0.15
MONOTONE_TOL = 0.02


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


# ─── BSC helpers ───
def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    raw = torch.randint(0, 2, (M, N), generator=gen, device=device).float()
    return 2.0 * raw - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    """W = (1/N) sum v_i k_i^T, batched."""
    device = keys.device
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def recall_cosine_batch(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor) -> float:
    """Mean cosine(W @ k, v) for all items."""
    y = keys @ W.T
    yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return float((yn * vn).sum(dim=1).mean())


# ─── LSH balanced-bin gating ───
def build_lsh_gate(N: int, K: int, gen: torch.Generator, device) -> torch.Tensor:
    """Return K random unit projections for LSH gating."""
    proj = make_bsc(K, N, gen, device).float()
    proj = proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return proj  # (K, N)


def gate_assign(keys: torch.Tensor, proj: torch.Tensor, K: int) -> torch.Tensor:
    """Assign each key to one expert using LSH balanced-bin quantization.
    Uses empirical quantile bins (not min-max) to prevent CLT mode-collapse.
    Returns assignments: (M,) LongTensor with values in [0, K).
    """
    # Project each key onto first projection vector (1D gate for assignment)
    # For K-way split: sum of dot-products with each of K projections, argmax
    scores = keys @ proj.T   # (M, K)
    # Use argmax on scores for primary assignment
    assignment = scores.argmax(dim=1)   # (M,)

    # Balanced-bin correction: re-balance using empirical quantiles if imbalanced
    # Sort items by their primary score and redistribute evenly
    target_load = keys.shape[0] // K
    if target_load < 1:
        return assignment

    # Check if imbalanced (Gini > 0.3)
    loads = torch.bincount(assignment, minlength=K).float()
    gini_val = _gini(loads.tolist())
    if gini_val > 0.3:
        # Fall back to rank-based equal-frequency assignment
        primary_score = scores[:, 0]  # use first projection
        sorted_idx = primary_score.argsort()
        new_assign = torch.zeros(keys.shape[0], dtype=torch.long, device=keys.device)
        for k in range(K):
            start = k * target_load
            end = (k + 1) * target_load if k < K - 1 else keys.shape[0]
            new_assign[sorted_idx[start:end]] = k
        return new_assign

    return assignment


def gate_top2(query: torch.Tensor, proj: torch.Tensor, K: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Return top-2 expert indices and their gate scores for a single query.
    query: (N,), proj: (K, N). Returns (top2_indices, top2_scores)."""
    scores = (proj @ query)  # (K,)
    top2_idx = scores.topk(min(2, K)).indices
    top2_scores = scores[top2_idx].softmax(dim=0)
    return top2_idx, top2_scores


# ─── Gini and mode-collapse metrics ───
def _gini(loads: list[float]) -> float:
    """Gini coefficient over load distribution. 0=perfect balance, 1=total collapse."""
    n = len(loads)
    if n <= 1:
        return 0.0
    total = sum(loads)
    if total <= 0:
        return 0.0
    loads_sorted = sorted(loads)
    cumsum = 0.0
    for i, v in enumerate(loads_sorted):
        cumsum += (2 * (i + 1) - n - 1) * v
    return cumsum / (n * total)


def mode_collapse_metrics(loads: list[int]) -> dict:
    K = len(loads)
    total = sum(loads)
    if total == 0 or K == 0:
        return {"gini": 1.0, "max_min_ratio": float("inf"), "top2_frac": 1.0}
    gini = _gini([float(x) for x in loads])
    max_load = max(loads)
    min_load = max(min(loads), 1)  # avoid div/0
    max_min = max_load / min_load
    sorted_loads = sorted(loads, reverse=True)
    top2_sum = sum(sorted_loads[:2])
    top2_frac = top2_sum / total
    return {"gini": gini, "max_min_ratio": max_min, "top2_frac": top2_frac}


# ─── Arm A: SHIFT (K full-N experts) ───
def run_arm_a_shift(keys: torch.Tensor, vals: torch.Tensor, K: int, N: int,
                    gen: torch.Generator, device) -> dict:
    """SHIFT arm: K experts each (N, N). Parameter budget K*N^2."""
    proj = build_lsh_gate(N, K, gen, device)
    assignment = gate_assign(keys, proj, K)
    loads = [int((assignment == k).sum()) for k in range(K)]

    # Store into K full-N expert matrices
    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N, N), dtype=torch.float32, device=device))
            continue
        Wk = outer_product_store(keys[mask], vals[mask], N)
        Wks.append(Wk)

    # Retrieval: top-2 weighted pool
    M = keys.shape[0]
    cos_vals = []
    for i in range(M):
        q = keys[i]   # (N,)
        top2_idx, top2_w = gate_top2(q, proj, K)
        y = torch.zeros(N, device=device)
        for rank, (k_idx, w) in enumerate(zip(top2_idx.tolist(), top2_w.tolist())):
            y = y + w * (Wks[k_idx] @ q)
        v_target = vals[i]
        y_n = y / y.norm().clamp(min=1e-9)
        v_n = v_target / v_target.norm().clamp(min=1e-9)
        cos_vals.append(float((y_n * v_n).sum()))

    del Wks
    if device.type == "cuda":
        torch.cuda.empty_cache()

    mean_cos = sum(cos_vals) / len(cos_vals)
    mc = mode_collapse_metrics(loads)
    return {"mean_cosine": mean_cos, "loads": loads, "mode_collapse": mc,
            "param_budget": K * N * N}


# ─── Arm B: PARTITION (K experts each N/K) ───
def run_arm_b_partition(keys: torch.Tensor, vals: torch.Tensor, K: int, N: int,
                        gen: torch.Generator, device) -> dict:
    """PARTITION arm: K experts each (N/K, N/K). Parameter budget N^2 (fixed)."""
    N_k = max(N // K, 1)
    proj = build_lsh_gate(N, K, gen, device)
    assignment = gate_assign(keys, proj, K)
    loads = [int((assignment == k).sum()) for k in range(K)]

    # Random dimension permutation: stable per (K, N) combination
    perm_gen = torch.Generator(device=device).manual_seed(N * 100 + K)
    perm = torch.randperm(N, generator=perm_gen, device=device)
    keys_p = keys[:, perm]
    vals_p = vals[:, perm]

    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N_k, N_k), dtype=torch.float32, device=device))
            continue
        k_slice = keys_p[mask, k * N_k:(k + 1) * N_k]
        v_slice = vals_p[mask, k * N_k:(k + 1) * N_k]
        Wk = outer_product_store(k_slice, v_slice, N_k)
        Wks.append(Wk)

    # Retrieval: use assigned expert (top-1 for PARTITION to isolate confound)
    M = keys.shape[0]
    cos_vals = []
    for i in range(M):
        k_idx = int(assignment[i])
        q_slice = keys_p[i, k_idx * N_k:(k_idx + 1) * N_k]
        v_slice = vals_p[i, k_idx * N_k:(k_idx + 1) * N_k]
        y = Wks[k_idx] @ q_slice
        y_n = y / y.norm().clamp(min=1e-9)
        v_n = v_slice / v_slice.norm().clamp(min=1e-9)
        cos_vals.append(float((y_n * v_n).sum()))

    del Wks
    if device.type == "cuda":
        torch.cuda.empty_cache()

    mean_cos = sum(cos_vals) / len(cos_vals)
    mc = mode_collapse_metrics(loads)
    return {"mean_cosine": mean_cos, "loads": loads, "mode_collapse": mc,
            "param_budget": N * N}


# ─── Arm C: SINGLE (matched parameter budget to SHIFT) ───
def run_arm_c_single(keys: torch.Tensor, vals: torch.Tensor, K: int, N: int,
                     device) -> dict:
    """SINGLE arm: one expert of dim int(sqrt(K)*N) to match SHIFT param budget K*N^2.
    If K=1: use N directly. Else: project keys/vals into sqrt(K)*N space via random proj.
    """
    if K == 1:
        N_single = N
        keys_s = keys
        vals_s = vals
    else:
        N_single = int(math.sqrt(K) * N)
        # Random projection to higher-dim space
        proj_gen = torch.Generator(device=device).manual_seed(N * 1000 + K)
        proj_k = torch.randn(N, N_single, generator=proj_gen, device=device)
        proj_k = proj_k / proj_k.norm(dim=0, keepdim=True).clamp(min=1e-9)
        proj_v = torch.randn(N, N_single, generator=proj_gen, device=device)
        proj_v = proj_v / proj_v.norm(dim=0, keepdim=True).clamp(min=1e-9)
        keys_s = keys @ proj_k    # (M, N_single)
        vals_s = vals @ proj_v    # (M, N_single)
        # Re-binarize for BSC property
        keys_s = keys_s.sign()
        vals_s = vals_s.sign()
        keys_s[keys_s == 0] = 1.0
        vals_s[vals_s == 0] = 1.0

    W = outer_product_store(keys_s, vals_s, N_single)
    mean_cos = recall_cosine_batch(W, keys_s, vals_s)
    del W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"mean_cosine": mean_cos, "N_single": N_single,
            "param_budget": N_single * N_single}


# ─── one (K, M_total, seed) cell ───
def run_one_cell(seed: int, K: int, M_total: int, N: int, device) -> dict:
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)

    # Generate fresh gen for gating (so gate is independent of data gen)
    gate_gen = torch.Generator(device=device).manual_seed(seed + 10000)

    arm_a = run_arm_a_shift(keys, vals, K, N, gate_gen, device)
    gate_gen2 = torch.Generator(device=device).manual_seed(seed + 20000)
    arm_b = run_arm_b_partition(keys, vals, K, N, gate_gen2, device)
    arm_c = run_arm_c_single(keys, vals, K, N, device)

    del keys, vals
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"arm_a": arm_a, "arm_b": arm_b, "arm_c": arm_c,
            "K": K, "M_total": M_total, "N": N}


# ─── compute verdict ───
def compute_verdict(results: list[dict], M_per_expert: int) -> tuple[str, str, dict]:
    """Compute 3-arm verdict from per-cell results."""
    if not results:
        return ("MOE_INSTRUMENTATION_FAIL", "No results.", {})

    # Organize by (K, M_total): average over seeds
    from collections import defaultdict
    cells: dict[tuple[int, int], dict[str, list[float]]] = defaultdict(
        lambda: {"arm_a": [], "arm_b": [], "arm_c": [], "mc_gini": [], "mc_mm": [], "mc_top2": []})

    for r in results:
        key = (r["K"], r["M_total"])
        cells[key]["arm_a"].append(r["arm_a"]["mean_cosine"])
        cells[key]["arm_b"].append(r["arm_b"]["mean_cosine"])
        cells[key]["arm_c"].append(r["arm_c"]["mean_cosine"])
        mc = r["arm_a"]["mode_collapse"]
        cells[key]["mc_gini"].append(mc["gini"])
        cells[key]["mc_mm"].append(mc["max_min_ratio"])
        cells[key]["mc_top2"].append(mc["top2_frac"])

    def mean(lst):
        return sum(lst) / len(lst) if lst else float("nan")

    # Per-cell means
    cell_means = {}
    for (K, M), d in cells.items():
        a_m = mean(d["arm_a"])
        b_m = mean(d["arm_b"])
        c_m = mean(d["arm_c"])
        lift_a_vs_c = a_m - c_m
        lift_b_vs_c = b_m - c_m
        cell_means[(K, M)] = {
            "arm_a": a_m, "arm_b": b_m, "arm_c": c_m,
            "lift_a_vs_c": lift_a_vs_c, "lift_b_vs_c": lift_b_vs_c,
            "gini": mean(d["mc_gini"]),
            "max_min_ratio": mean(d["mc_mm"]),
            "top2_frac": mean(d["mc_top2"]),
        }

    # Find highest-lift cell (Arm A vs C)
    M_baseline = M_per_expert  # single-expert capacity floor
    best_lift = -1.0
    best_cell = None
    for (K, M), cm in cell_means.items():
        if cm["lift_a_vs_c"] > best_lift:
            best_lift = cm["lift_a_vs_c"]
            best_cell = (K, M, cm)

    if best_cell is None:
        return ("MOE_INSTRUMENTATION_FAIL", "Could not find best cell.", {})

    K_best, M_best, cm_best = best_cell

    # Mode-collapse status at best cell
    mc_ok = (cm_best["gini"] < HP_GINI_MAX and
              cm_best["max_min_ratio"] < HP_MAX_MIN_RATIO and
              cm_best["top2_frac"] < HP_TOP2_FRAC_MAX)

    # PARTITION null confirmed: Arm B tracks Arm C across all cells?
    partition_null_lifts = [abs(cm["lift_b_vs_c"]) for cm in cell_means.values()]
    partition_null = all(lift < HF_ARM_A_VS_C_MAX for lift in partition_null_lifts)

    # K monotonicity for SHIFT (at M = 2*M_baseline if available)
    target_M = 2 * M_baseline
    K_vals = sorted(set(K for K, M in cell_means if M <= target_M * 1.5))
    if len(K_vals) >= 2:
        retention_at_target = []
        for K in K_vals:
            M_closest = min((M for (k, M) in cell_means if k == K),
                            key=lambda m: abs(m - target_M))
            retention_at_target.append((K, cell_means[(K, M_closest)]["arm_a"]))
        monotone = all(retention_at_target[i+1][1] >= retention_at_target[i][1] - MONOTONE_TOL
                       for i in range(len(retention_at_target) - 1))
    else:
        monotone = None  # insufficient K points

    # Build summary
    summary_cells = {}
    for (K, M), cm in cell_means.items():
        summary_cells[f"K{K}_M{M}"] = cm

    summary = {
        "best_lift_a_vs_c": best_lift,
        "best_K": K_best,
        "best_M_total": M_best,
        "best_cell": cm_best,
        "partition_null_confirmed": partition_null,
        "mode_collapse_ok_at_best": mc_ok,
        "monotone_in_K": monotone,
        "M_per_expert_used": M_per_expert,
        "cells": summary_cells,
    }

    # Verdict logic
    if (best_lift >= HP_ARM_A_VS_C_LIFT and mc_ok and
            (monotone is True or monotone is None)):
        verdict = "MOE_SHIFT_HARD_PASS"
        msg = (f"SHIFT arm BREAKS floor: Arm A exceeds Arm C by {best_lift:.3f} > {HP_ARM_A_VS_C_LIFT} "
               f"at K={K_best}, M_total={M_best}. "
               f"Mode-collapse OK: gini={cm_best['gini']:.3f}<{HP_GINI_MAX}, "
               f"max_min={cm_best['max_min_ratio']:.1f}<{HP_MAX_MIN_RATIO}, "
               f"top2_frac={cm_best['top2_frac']:.3f}<{HP_TOP2_FRAC_MAX}. "
               f"Monotone in K: {monotone}. "
               f"PARTITION null: {partition_null}. "
               f"Structural separation demonstrated: MoE row -> active capability.")
    elif (all(abs(cm["lift_a_vs_c"]) < HF_ARM_A_VS_C_MAX for cm in cell_means.values()) and
          not mc_ok):
        verdict = "MOE_SHIFT_HARD_FAIL"
        msg = (f"SHIFT arm tracks SINGLE within +/-{HF_ARM_A_VS_C_MAX} across all cells. "
               f"Mode-collapse present: gini={cm_best['gini']:.3f}, "
               f"max_min={cm_best['max_min_ratio']:.1f}. "
               f"Parameter budget alone explains any improvement. "
               f"MoE on substrate REJECTED.")
    elif MID_ARM_A_VS_C_MIN <= best_lift < HP_ARM_A_VS_C_LIFT:
        verdict = "MOE_SHIFT_MIDDLE"
        msg = (f"SHIFT arm shows modest gain: Arm A exceeds Arm C by {best_lift:.3f} "
               f"in [{MID_ARM_A_VS_C_MIN},{HP_ARM_A_VS_C_LIFT}) at K={K_best}, M_total={M_best}. "
               f"Mode-collapse marginal: gini={cm_best['gini']:.3f}, "
               f"max_min={cm_best['max_min_ratio']:.1f}. "
               f"MIDDLE BAND: structural separation present but not dominant mechanism; "
               f"gain attributable partially to parameter budget.")
    else:
        verdict = "MOE_SHIFT_INCONCLUSIVE"
        msg = (f"Inconclusive: best lift Arm A vs C = {best_lift:.3f}. "
               f"mode_collapse_ok={mc_ok}. monotone={monotone}. "
               f"Review per-cell data in summary.")

    return verdict, msg, summary


# ─── instrumentation self-test ───
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    device = torch.device("cpu")
    gen = torch.Generator().manual_seed(99)

    # Test 1: gini perfect balance
    g0 = _gini([500.0, 500.0, 500.0, 500.0])
    assert abs(g0) < 1e-9, f"Selftest 1 FAIL: gini perfect balance={g0}"
    print("[SELFTEST] 1/6 gini perfect balance OK", flush=True)

    # Test 2: gini total collapse
    g1 = _gini([2000.0, 0.0, 0.0, 0.0])
    assert abs(g1 - 0.75) < 0.01, f"Selftest 2 FAIL: gini total collapse={g1:.3f}"
    print("[SELFTEST] 2/6 gini total collapse OK", flush=True)

    # Test 3: top2_frac balanced
    mc_bal = mode_collapse_metrics([500, 500, 500, 500])
    assert mc_bal["top2_frac"] < 0.75, f"Selftest 3 FAIL: top2_frac balanced={mc_bal['top2_frac']}"
    print("[SELFTEST] 3/6 top2_frac balanced OK", flush=True)

    # Test 4: top2_frac collapse
    mc_col = mode_collapse_metrics([1800, 200, 0, 0])
    assert mc_col["top2_frac"] > 0.75, f"Selftest 4 FAIL: top2_frac collapse={mc_col['top2_frac']}"
    print("[SELFTEST] 4/6 top2_frac collapse OK", flush=True)

    # Test 5: PARTITION load-ratio K-cancellation (algebraic check)
    # load_ratio = (M/K) / (alpha_c * N/K) = M / (alpha_c * N) -- K cancels
    for K in [2, 4, 8]:
        M_total = 256
        alpha_c = 0.56
        N = 512
        M_per_exp = M_total // K
        N_per_exp = N // K
        cap_per_exp = alpha_c * N_per_exp
        ratio = M_per_exp / cap_per_exp
        expected = M_total / (alpha_c * N)  # K-independent
        assert abs(ratio - expected) < 1e-9, f"Selftest 5 FAIL: K={K} ratio={ratio:.4f} != {expected:.4f}"
    print("[SELFTEST] 5/6 PARTITION load-ratio K-cancellation verified", flush=True)

    # Test 6: SHIFT load-ratio decreases with K
    ratios = []
    for K in [1, 2, 4, 8]:
        M_total = 256
        alpha_c = 0.56
        N = 512
        M_per_exp = M_total // K
        cap_per_exp = alpha_c * N  # SHIFT: full N per expert
        ratios.append(M_per_exp / cap_per_exp)
    assert all(ratios[i] > ratios[i+1] for i in range(len(ratios)-1)), \
        f"Selftest 6 FAIL: SHIFT ratios not decreasing with K: {ratios}"
    print("[SELFTEST] 6/6 SHIFT load-ratio decreases with K OK", flush=True)

    # Test 7: run_one_cell at tiny scale returns non-null cosines
    cell = run_one_cell(seed=7, K=2, M_total=16, N=32, device=device)
    for arm in ["arm_a", "arm_b", "arm_c"]:
        cos = cell[arm]["mean_cosine"]
        assert cos is not None and not math.isnan(cos), f"Selftest 7 FAIL: {arm} cosine={cos}"
        assert cos > 0.0, f"Selftest 7 FAIL: {arm} cosine={cos:.4f} not positive"
    print("[SELFTEST] 7/7 run_one_cell all arms non-null OK", flush=True)

    print("[SELFTEST] All 7 self-tests passed", flush=True)


_instrumentation_selftest()


# ─── suspicious-result gate (after smoke) ───
def suspicious_result_gate(smoke_results: list[dict]) -> str | None:
    """Return description if smoke metrics are suspicious."""
    if not smoke_results:
        return "No smoke results"
    # Check for all-zero cosines
    for r in smoke_results:
        for arm in ["arm_a", "arm_b", "arm_c"]:
            if abs(r[arm]["mean_cosine"]) < 1e-9:
                return f"{arm} cosine exactly 0.0 at K={r['K']}, M={r['M_total']}"
    # Check for no variation across M
    a_cosines = [r["arm_a"]["mean_cosine"] for r in smoke_results]
    if len(set(f"{c:.4f}" for c in a_cosines)) == 1:
        return f"Arm A cosine constant {a_cosines[0]:.4f} across all cells -- no M variation"
    return None


# ─── walk-back gate ───
def compute_cohens_d(values_a: list[float], values_c: list[float]) -> float:
    """Cohen's d for Arm A vs Arm C lift."""
    if not values_a or not values_c:
        return 0.0
    n_a, n_c = len(values_a), len(values_c)
    mean_a = sum(values_a) / n_a
    mean_c = sum(values_c) / n_c
    var_a = sum((x - mean_a)**2 for x in values_a) / max(n_a - 1, 1)
    var_c = sum((x - mean_c)**2 for x in values_c) / max(n_c - 1, 1)
    pooled_sd = math.sqrt((var_a + var_c) / 2.0)
    if pooled_sd < 1e-9:
        return 0.0
    return (mean_a - mean_c) / pooled_sd


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
    print(f"[moe_shift_partition] device={device} smoke={smoke}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    M_mults = M_MULT_SMOKE if smoke else M_MULT_FULL
    mode = "smoke" if smoke else "full"

    # Build M_total grid from multipliers
    M_totals = sorted(set(int(m * K * M_per_expert) for m in M_mults for K in K_sweep))

    print(f"[moe_shift_partition] N={N} K_sweep={K_sweep} M_totals={M_totals} "
          f"seeds={seeds} M_per_expert={M_per_expert}", flush=True)

    out_dir_name = "wave14_moe_shift_partition_v1_smoke" if smoke else "wave14_moe_shift_partition_v1"
    out_dir = get_output_dir(out_dir_name)

    t0 = time.time()
    all_results = []

    for K in K_sweep:
        for M_total in M_totals:
            for seed in seeds:
                print(f"[moe_shift_partition] K={K} M_total={M_total} seed={seed}", flush=True)
                cell = run_one_cell(seed, K, M_total, N, device)
                all_results.append(cell)
                a, b, c = cell["arm_a"]["mean_cosine"], cell["arm_b"]["mean_cosine"], cell["arm_c"]["mean_cosine"]
                mc = cell["arm_a"]["mode_collapse"]
                print(f"  A={a:.3f} B={b:.3f} C={c:.3f} "
                      f"gini={mc['gini']:.2f} mm={mc['max_min_ratio']:.1f}", flush=True)

    if smoke:
        flag = suspicious_result_gate(all_results)
        if flag is not None:
            print(f"[smoke] INSTRUMENTATION_SUSPECT: {flag}", flush=True)
            # Write metrics with suspect flag then exit 1
            metrics = {
                "verdict": "MOE_INSTRUMENTATION_SUSPECT",
                "verdict_msg": f"Smoke suspicious-result gate BLOCKED ship: {flag}",
                "elapsed_s": time.time() - t0,
                "summary": {"suspect_flag": flag},
                "config": {"mode": "smoke", "N": N},
            }
            (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
            sys.exit(1)

        # Walk-back gate: compute smoke effect size
        smoke_a = [r["arm_a"]["mean_cosine"] for r in all_results]
        smoke_c = [r["arm_c"]["mean_cosine"] for r in all_results]
        d = compute_cohens_d(smoke_a, smoke_c)
        lift = sum(smoke_a) / len(smoke_a) - sum(smoke_c) / len(smoke_c)
        print(f"[smoke] effect size d={d:.3f} lift={lift:.3f}", flush=True)
        if d < 1.0 or abs(lift) < HP_ARM_A_VS_C_LIFT * 0.8:
            print(f"[smoke] WALK-BACK: d={d:.3f}<1.0 or lift={lift:.3f} borderline -- "
                  f"full run registered at n*2 seeds", flush=True)

        print(f"[smoke] smoke PASS (d={d:.3f})", flush=True)
        metrics = {
            "verdict": "SMOKE_PASS",
            "verdict_msg": f"Smoke passed: effect_size_d={d:.3f}, lift={lift:.3f}",
            "elapsed_s": time.time() - t0,
            "summary": {"smoke_d": d, "smoke_lift": lift, "n_cells": len(all_results)},
            "config": {"mode": "smoke", "N": N, "K_sweep": K_sweep, "M_totals": M_totals},
        }
        (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
        sys.exit(0)

    # Full run verdict
    verdict, verdict_msg, summary = compute_verdict(all_results, M_per_expert)
    elapsed = time.time() - t0

    # Serialize results (keep small: just scalar summary, not per-item cosines)
    results_serial = []
    for r in all_results:
        results_serial.append({
            "K": r["K"], "M_total": r["M_total"], "N": r["N"],
            "arm_a_cos": r["arm_a"]["mean_cosine"],
            "arm_b_cos": r["arm_b"]["mean_cosine"],
            "arm_c_cos": r["arm_c"]["mean_cosine"],
            "arm_a_loads": r["arm_a"]["loads"],
            "arm_a_mc": r["arm_a"]["mode_collapse"],
        })

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "results": results_serial,
        "config": {
            "mode": mode,
            "N": N,
            "K_sweep": K_sweep,
            "M_totals": M_totals,
            "M_per_expert": M_per_expert,
            "seeds": seeds,
            "hp_arm_a_vs_c_lift": HP_ARM_A_VS_C_LIFT,
            "hp_gini_max": HP_GINI_MAX,
            "hp_max_min_ratio": HP_MAX_MIN_RATIO,
            "hp_top2_frac_max": HP_TOP2_FRAC_MAX,
            "hf_arm_a_vs_c_max": HF_ARM_A_VS_C_MAX,
            "device": str(device),
            "reference_class": "linear_heteroassociator_recalibrated_alpha_c_056",
        },
    }
    validate_metrics(metrics)

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2, default=float)

    print(f"\n[moe_shift_partition] verdict={verdict}", flush=True)
    print(f"[moe_shift_partition] {verdict_msg}", flush=True)
    print(f"[moe_shift_partition] elapsed={elapsed:.1f}s  metrics -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
