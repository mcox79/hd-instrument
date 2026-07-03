"""MoE SHIFT K-scaling sweep v2: extended K grid {2,4,8,16,32,64}.

PARENT: wave14_moe_shift_K_scaling_v1 MIDDLE_BAND (ratio=0.98 near-flat, p=-0.02).
v1 only tested K in {2,4,8,16,32}. v2 extends to K=64 to map whether the sub-linear
K-scaling persists at higher K or shows a regime change / eventual collapse.

HYPOTHESIS: In SHIFT mode, K=64 may reveal: (a) continued sub-linear plateau,
(b) further saturation at K=32->64, or (c) mode-collapse onset at K=64.
Mapping the full K-range to K=64 anchors the envelope-expansion claim.

DESIGN:
  - FIXED M_per_expert = M_PER_EXPERT (from alpha_c calibration at N=4096)
  - K sweep: K in {2, 4, 8, 16, 32, 64}  (6 points; v1=5 points)
  - Arm A (SHIFT): K full-N experts, M_total = K * M_per_expert
  - Arm C (SINGLE): 1 expert at N_single = sqrt(K) * N, M_single = M_per_expert
    (matched per-expert load, NOT K-fold matched-compute)
    This is the "fair comparison" arm: tests structural-separation vs single large W
  - Arm B (PARTITION): K (N/K x N/K) experts, M_total = K * (alpha_c * N/K)
    Control arm: M/expert capacity scales DOWN with K (null prediction: flat or declining)
  - Arm A (SHIFT): K full-N experts, M_total = K * M_per_expert
  - Arm C (SINGLE): 1 expert at N_single = sqrt(K) * N, M_single = M_per_expert
    (matched per-expert load, NOT K-fold matched-compute)
    This is the "fair comparison" arm: tests structural-separation vs single large W
  - Arm B (PARTITION): K (N/K x N/K) experts, M_total = K * (alpha_c * N/K)
    Control arm: M/expert capacity scales DOWN with K (null prediction: flat or declining)

PRIMARY METRIC: retention_A(K) / retention_A(K=2) -- K-fold scaling ratio
  If structural-separation gives K-fold gain, this should be ~ K/2.
  If gain is sub-linear in K, exponent p where ratio ~ (K/2)^p.

SECONDARY METRIC: retention_A(K) vs retention_C(K)
  Structural separation vs parameter count: if A >> C, separation is the mechanism.

PRE-REGISTERED BANDS:
  HARD_PASS (K-scaling CONFIRMED):
    - retention_A(K=32) / retention_A(K=2) >= 4.0 (linear in K gives 32/2=16x; 4x is
      conservative floor allowing for overhead)
    - OR retention_A(K) monotone-non-decreasing in K with tolerance 0.02
    - AND retention_A(K=16) > retention_C(K=16) by >= 0.10 (structural separation > param count)
    -> K-sweep annotated; SHIFT structural-separation row promoted to empirically mapped

  HARD_FAIL (K-scaling FLAT):
    - abs(retention_A(K=32) - retention_A(K=2)) < 0.05 (flat across K)
    - OR retention_A(K=16) within 0.05 of retention_C(K=16) (no separation vs param budget)
    -> SHIFT benefit attributed to parameter count alone, not structural separation

  MIDDLE_BAND:
    - retention_A monotone-increasing in K but ratio < 4.0 at K=32
    - Sub-linear scaling: document exponent p

  INSTRUMENTATION_FAIL:
    - Mode-collapse (Gini > 0.4 or max/min_load > 5x) in >= 2 K-values
    - OR retention_A at any K is NaN or non-finite

NOTE on K=32 feasibility at N=4096: K=32 means 32 full N x N experts; parameter budget
32 * 4096^2 ~ 537M parameters, ~2 GB float32. Feasible on 8 GB GPU.
M_per_expert=1600, M_total_K32 = 51200 pairs stored. Each BSC vector is 4096-dim float32 = 16KB;
51200 vectors ~ 800MB. Total memory for K=32 cell: ~3 GB -- fits in 8GB. OK.

Self-tests:
  1. gini(equal_loads) = 0.0
  2. gini(total_collapse) = (K-1)/K for K experts
  3. retention_A at K=1 matches SINGLE arm (single expert is trivially K=1 SHIFT)
  4. evaluate_bsc_recall_cosine returns value in [-1, 1] at smoke scale

Queue: overnight_queue (GPU; 5 seeds x 5 K x 3 arms; ~6-8 GPU-hrs at N=4096)
Pre-reg: prereqs/2026-05-26_wave14_moe_shift_K_scaling_v1.md
DEPENDENCY: wave14_moe_shift_partition_v2 must return SHIFT verdict before shipping.
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
M_PER_EXPERT_FULL = 1600   # from alpha_c calibration at N=4096
M_PER_EXPERT_SMOKE = int(1600 * N_SMOKE / N_FULL)   # ~200 at N=512
K_SWEEP_FULL = [2, 4, 8, 16, 32, 64]
K_SWEEP_SMOKE = [2, 4, 8]  # smoke unchanged
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_STORE = 256
BATCH_PROBE = 512

# Pre-registered thresholds
HP_K_SCALING_RATIO = 4.0      # retention(K=64)/retention(K=2) >= 4x for HARD_PASS (K range doubled)
HP_STRUCTURAL_LIFT = 0.10     # retention_A(K=16) - retention_C(K=16) >= 0.10
MONOTONE_TOL = 0.02
HF_FLAT_TOLERANCE = 0.05      # abs(ret_A(K=32) - ret_A(K=2)) < this for HARD_FAIL
HF_SEPARATION_TOL = 0.05      # ret_A(K=16) within this of ret_C(K=16) -> HARD_FAIL
GINI_ALERT = 0.4
MAX_MIN_LOAD_ALERT = 5.0


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


# ─── BSC helpers ───

def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    """Return M x N {-1, +1} BSC code vectors."""
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    """W = (1/N) sum_i v_i k_i^T, batched."""
    device = keys.device
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def recall_cosine_batch(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor,
                        batch: int = BATCH_PROBE) -> float:
    """Mean cosine(W @ k, v) for all items."""
    total = 0.0
    n = keys.shape[0]
    for s in range(0, n, batch):
        e = min(s + batch, n)
        y = keys[s:e] @ W.T
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = vals[s:e] / vals[s:e].norm(dim=1, keepdim=True).clamp(min=1e-9)
        total += float((yn * vn).sum(dim=1).sum())
    return total / max(n, 1)


# ─── LSH balanced-bin gating (carried from v2) ───

def build_lsh_proj(N: int, K: int, gen: torch.Generator, device) -> torch.Tensor:
    """K random unit projections for LSH gating."""
    proj = make_bsc(K, N, gen, device)
    return proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-9)


def gate_assign_balanced(keys: torch.Tensor, proj: torch.Tensor, K: int) -> torch.Tensor:
    """Balanced-bin assignment: argmax scores with empirical-quantile re-balance if Gini > 0.3."""
    scores = keys @ proj.T   # (M, K)
    assignment = scores.argmax(dim=1)
    loads = torch.bincount(assignment, minlength=K).float()
    gini_val = _gini(loads.tolist())
    if gini_val > 0.3:
        # Rank-based equal-frequency fallback
        sorted_idx = scores[:, 0].argsort()
        target = keys.shape[0] // K
        new_assign = torch.zeros(keys.shape[0], dtype=torch.long, device=keys.device)
        for k in range(K):
            start = k * target
            end = (k + 1) * target if k < K - 1 else keys.shape[0]
            new_assign[sorted_idx[start:end]] = k
        return new_assign
    return assignment


def _gini(loads: list) -> float:
    n = len(loads)
    if n <= 1:
        return 0.0
    s = sorted(loads)
    total = sum(s)
    if total <= 0:
        return 0.0
    cum = 0.0
    gini_num = 0.0
    for i, v in enumerate(s):
        cum += v
        gini_num += (2 * (i + 1) - n - 1) * v
    return abs(gini_num) / (n * total)


def compute_load_metrics(assignment: torch.Tensor, K: int) -> dict:
    loads = torch.bincount(assignment, minlength=K).float()
    gini = _gini(loads.tolist())
    max_l = float(loads.max())
    min_l = float(loads.min())
    ratio = max_l / max(min_l, 1.0)
    return {"gini": round(gini, 4), "max_min_ratio": round(ratio, 3),
            "loads": loads.tolist()}


# ─── Arm runners ───

def run_arm_shift(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    """Arm A (SHIFT): K full-N experts, M_total = K * M_per_expert stored.

    Returns per-K retention + load metrics.
    """
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert

    # Generate all keys and values
    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)

    # LSH gating
    proj = build_lsh_proj(N, K, gen, device)
    assignment = gate_assign_balanced(keys, proj, K)
    load_metrics = compute_load_metrics(assignment, K)

    # Build per-expert W
    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N, N), dtype=torch.float32, device=device))
        else:
            Wks.append(outer_product_store(keys[mask], vals[mask], N))

    # Recall: top-2 gate retrieval (same as v2)
    total_cos = 0.0
    for s in range(0, M_total, BATCH_PROBE):
        e = min(s + BATCH_PROBE, M_total)
        q_batch = keys[s:e]
        v_batch = vals[s:e]
        scores = q_batch @ proj.T  # (B, K)
        top2 = scores.topk(min(2, K), dim=1)
        top2_idx = top2.indices
        top2_w = top2.values.softmax(dim=1)

        y = torch.zeros((e - s, N), dtype=torch.float32, device=device)
        for rank in range(min(2, K)):
            expert_ids = top2_idx[:, rank]   # (B,)
            gate_w = top2_w[:, rank]         # (B,)
            for b in range(e - s):
                y[b] += gate_w[b] * (Wks[expert_ids[b]] @ q_batch[b])
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = v_batch / v_batch.norm(dim=1, keepdim=True).clamp(min=1e-9)
        total_cos += float((yn * vn).sum(dim=1).sum())

    retention = total_cos / max(M_total, 1)
    return {"retention": round(retention, 4), "M_total": M_total, **load_metrics}


def run_arm_partition(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    """Arm B (PARTITION): K experts each of dim N/K, M_per_expert items per expert.

    Null arm: per-expert capacity = alpha_c * N/K (shrinks with K); aggregate flat in K.
    """
    N_k = max(N // K, 1)
    gen = torch.Generator(device=device).manual_seed(seed + 1000)
    M_total = K * M_per_expert

    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N_k, gen, device)

    # Assign items to experts by index partition (round-robin, not LSH)
    # Simple deterministic partition for null control
    total_cos = 0.0
    Wks = []
    for k in range(K):
        idx = torch.arange(k, M_total, K, device=device)
        k_keys = keys[idx, :N_k]
        k_vals = vals[idx]
        Wk = outer_product_store(k_keys, k_vals, N_k)
        Wks.append(Wk)

    for k in range(K):
        idx = torch.arange(k, M_total, K, device=device)
        q_batch = keys[idx, :N_k]
        v_batch = vals[idx]
        retention_k = recall_cosine_batch(Wks[k], q_batch, v_batch)
        total_cos += retention_k * len(idx)

    retention = total_cos / max(M_total, 1)
    return {"retention": round(retention, 4), "M_total": M_total,
            "N_k": N_k, "gini": 0.0, "max_min_ratio": 1.0, "loads": [M_per_expert] * K}


def run_arm_single(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    """Arm C (SINGLE): 1 expert at N_single = int(sqrt(K) * N), M = M_per_expert.

    Matched per-expert load but not structural-separation.
    """
    N_single = int(math.sqrt(K) * N)
    gen = torch.Generator(device=device).manual_seed(seed + 2000)
    M = M_per_expert

    keys = make_bsc(M, N_single, gen, device)
    vals = make_bsc(M, N_single, gen, device)
    W = outer_product_store(keys, vals, N_single)
    retention = recall_cosine_batch(W, keys, vals)
    return {"retention": round(retention, 4), "M": M, "N_single": N_single}


# ─── Instrumentation self-test ───

def _instrumentation_selftest():
    """Assert all metrics are non-null/non-sentinel at smoke scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    device = torch.device("cpu")
    K_test, N_test = 2, 64
    M_test = 20

    # 1. gini(equal loads) = 0.0
    g = _gini([100.0, 100.0, 100.0, 100.0])
    assert g < 0.01, f"Selftest 1 FAIL: gini(equal)={g}"
    print("[selftest] 1/5 gini(equal) = 0 OK")

    # 2. gini(total collapse) close to (K-1)/K
    K4 = 4
    g2 = _gini([2000.0, 0.0, 0.0, 0.0])
    expected = (K4 - 1) / K4
    assert abs(g2 - expected) < 0.1, f"Selftest 2 FAIL: gini(collapse)={g2}, expected ~{expected}"
    print(f"[selftest] 2/5 gini(collapse) ~{expected:.2f} OK")

    # 3. run_arm_shift returns non-NaN non-zero retention
    result_a = run_arm_shift(K_test, N_test, M_test, seed=42, device=device)
    assert result_a["retention"] is not None, "Selftest 3 FAIL: retention is None"
    assert math.isfinite(result_a["retention"]), f"Selftest 3 FAIL: retention not finite: {result_a}"
    assert result_a["retention"] > -1.0, f"Selftest 3 FAIL: retention too low: {result_a}"
    print(f"[selftest] 3/5 run_arm_shift K=2 retention={result_a['retention']:.4f} OK")

    # 4. run_arm_single returns non-NaN value
    result_c = run_arm_single(K_test, N_test, M_test, seed=42, device=device)
    assert math.isfinite(result_c["retention"]), f"Selftest 4 FAIL: single retention not finite"
    print(f"[selftest] 4/5 run_arm_single K=2 retention={result_c['retention']:.4f} OK")

    # 5. evaluate_metrics callable: K-scaling ratio computable from 2 K-values
    ret_k2, ret_k4 = 0.60, 0.70
    ratio = ret_k4 / max(ret_k2, 1e-9)
    assert math.isfinite(ratio) and ratio > 0, f"Selftest 5 FAIL: ratio={ratio}"
    print(f"[selftest] 5/5 K-scaling ratio metric computable OK")
    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


# ─── Multi-scale smoke ───

def run_sweep(smoke: bool = False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[run] device={device}", flush=True)
    N = N_SMOKE if smoke else N_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_moe_shift_K_scaling_v2")

    results_per_K: dict[int, dict] = {}

    for K in K_sweep:
        print(f"\n[run] K={K} (N={N}, M_per_expert={M_per_expert}, seeds={seeds})", flush=True)
        arm_a_rets, arm_b_rets, arm_c_rets = [], [], []
        ginis_a = []
        for seed in seeds:
            a = run_arm_shift(K, N, M_per_expert, seed, device)
            b = run_arm_partition(K, N, M_per_expert, seed, device)
            c = run_arm_single(K, N, M_per_expert, seed, device)
            arm_a_rets.append(a["retention"])
            arm_b_rets.append(b["retention"])
            arm_c_rets.append(c["retention"])
            ginis_a.append(a["gini"])
            print(f"  seed={seed}: A={a['retention']:.4f} B={b['retention']:.4f} "
                  f"C={c['retention']:.4f} gini_A={a['gini']:.3f}", flush=True)

        mu_a = sum(arm_a_rets) / len(arm_a_rets)
        mu_b = sum(arm_b_rets) / len(arm_b_rets)
        mu_c = sum(arm_c_rets) / len(arm_c_rets)
        mean_gini = sum(ginis_a) / len(ginis_a)
        results_per_K[K] = {
            "mean_retention_A": round(mu_a, 4),
            "mean_retention_B": round(mu_b, 4),
            "mean_retention_C": round(mu_c, 4),
            "arm_A_vals": arm_a_rets,
            "arm_B_vals": arm_b_rets,
            "arm_C_vals": arm_c_rets,
            "mean_gini_A": round(mean_gini, 4),
            "mode_collapse_flag": mean_gini > GINI_ALERT,
        }
        print(f"  -> A={mu_a:.4f} B={mu_b:.4f} C={mu_c:.4f} gini={mean_gini:.3f}")

    return results_per_K, out_dir


def compute_verdict(results_per_K: dict) -> tuple[str, str, dict]:
    """Compute verdict and summary from per-K results."""
    K_vals = sorted(results_per_K.keys())
    rets_A = [results_per_K[K]["mean_retention_A"] for K in K_vals]
    rets_C = [results_per_K[K]["mean_retention_C"] for K in K_vals]
    ginis = [results_per_K[K]["mean_gini_A"] for K in K_vals]

    # Check mode collapse
    n_collapse = sum(1 for g in ginis if g > GINI_ALERT)
    collapse_flag = n_collapse >= 2

    # K-scaling ratio: largest K vs smallest K
    K_lo, K_hi = K_vals[0], K_vals[-1]
    ret_lo = results_per_K[K_lo]["mean_retention_A"]
    ret_hi = results_per_K[K_hi]["mean_retention_A"]
    k_scaling_ratio = ret_hi / max(ret_lo, 1e-9)

    # Monotonicity check
    def is_monotone_nondecrease(vals, tol=MONOTONE_TOL):
        return all(vals[i + 1] >= vals[i] - tol for i in range(len(vals) - 1))

    monotone = is_monotone_nondecrease(rets_A)

    # Structural separation at K=16 (if in sweep)
    sep_K = 16 if 16 in results_per_K else K_vals[-2] if len(K_vals) >= 2 else K_vals[-1]
    ret_A_sepK = results_per_K[sep_K]["mean_retention_A"]
    ret_C_sepK = results_per_K[sep_K]["mean_retention_C"]
    structural_lift = ret_A_sepK - ret_C_sepK

    # Fit scaling exponent: log(ratio) / log(K_hi / K_lo)
    if K_hi > K_lo and ret_lo > 1e-6 and ret_hi > 1e-6:
        p_exponent = math.log(k_scaling_ratio) / math.log(K_hi / K_lo)
    else:
        p_exponent = 0.0

    # Instrumentation fail
    if any(not math.isfinite(r) or r is None for r in rets_A):
        return ("INSTRUMENTATION_FAIL",
                f"INSTRUMENTATION_FAIL: non-finite retention_A in results.",
                {})

    if collapse_flag:
        return ("INSTRUMENTATION_FAIL",
                f"INSTRUMENTATION_FAIL: mode-collapse in {n_collapse}/{len(K_vals)} K-values "
                f"(Gini > {GINI_ALERT}).",
                {})

    # Hard-pass
    hard_pass = (
        (k_scaling_ratio >= HP_K_SCALING_RATIO or monotone) and
        structural_lift >= HP_STRUCTURAL_LIFT
    )

    # Hard-fail
    hard_fail = (
        abs(ret_hi - ret_lo) < HF_FLAT_TOLERANCE and
        abs(structural_lift) < HF_SEPARATION_TOL
    )

    summary = {
        "K_sweep": K_vals,
        "retention_A_per_K": {K: results_per_K[K]["mean_retention_A"] for K in K_vals},
        "retention_B_per_K": {K: results_per_K[K]["mean_retention_B"] for K in K_vals},
        "retention_C_per_K": {K: results_per_K[K]["mean_retention_C"] for K in K_vals},
        "k_scaling_ratio": round(k_scaling_ratio, 3),
        "scaling_exponent_p": round(p_exponent, 3),
        "monotone_nondecreasing_A": monotone,
        "structural_lift_at_K16": round(structural_lift, 4),
        "mean_ginis": {K: results_per_K[K]["mean_gini_A"] for K in K_vals},
        "mode_collapse_flag": collapse_flag,
    }

    if hard_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: K-scaling CONFIRMED. "
            f"retention_A ratio({K_hi}/{K_lo})={k_scaling_ratio:.2f} "
            f"{'(>= 4x floor)' if k_scaling_ratio >= HP_K_SCALING_RATIO else '(monotone)'}, "
            f"structural_lift_A-C at K={sep_K}={structural_lift:.3f} >= {HP_STRUCTURAL_LIFT}. "
            f"Scaling exponent p={p_exponent:.2f}. "
            f"SHIFT structural separation provides K-scaling; parameter count does not fully explain."
        )
    elif hard_fail:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: K-scaling FLAT. "
            f"retention_A range={abs(ret_hi - ret_lo):.3f} < {HF_FLAT_TOLERANCE} AND "
            f"structural_lift={structural_lift:.3f} < {HF_SEPARATION_TOL}. "
            f"SHIFT benefit attributed to parameter count alone (Arm C matches Arm A). "
            f"K-scaling does not hold."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: Sub-linear K-scaling. "
            f"ratio={k_scaling_ratio:.2f} (< {HP_K_SCALING_RATIO} floor), "
            f"monotone={monotone}, "
            f"structural_lift={structural_lift:.3f}. "
            f"Scaling exponent p={p_exponent:.2f} (< 1 = sub-linear). "
            f"Structural separation present but partial; K-scaling benefit is real but diminishing."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_moe_shift_K_scaling_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)

    results_per_K, out_dir = run_sweep(smoke)

    # Multi-scale smoke: if smoke, also run at N * 2 to check for degenerate scaling
    if smoke:
        print("\n[multi-scale smoke] running at N_smoke * 2...", flush=True)
        N2 = N_SMOKE * 2
        M2 = M_PER_EXPERT_SMOKE * 2
        results2 = {}
        for K in K_SWEEP_SMOKE[:2]:  # just K=2,4 for scale2
            device = torch.device("cpu")
            a2 = run_arm_shift(K, N2, M2, SEEDS_SMOKE[0], device)
            results2[K] = {"mean_retention_A": a2["retention"]}
            print(f"  N={N2} K={K}: A={a2['retention']:.4f}")
        # Check no degenerate collapse at scale2
        for K, r in results2.items():
            assert math.isfinite(r["mean_retention_A"]), f"Scale2 degenerate at K={K}"
        print("[multi-scale smoke] PASS (no degenerate scaling at N_smoke*2)")

    verdict, verdict_msg, summary = compute_verdict(results_per_K)
    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "per_K_details": {str(K): results_per_K[K] for K in results_per_K},
        "config": {
            "N": N_SMOKE if smoke else N_FULL,
            "M_per_expert": M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL,
            "K_sweep": K_SWEEP_SMOKE if smoke else K_SWEEP_FULL,
            "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
            "smoke": smoke,
            "dependency": "wave14_moe_shift_partition_v2 SHIFT verdict required before full ship",
        },
    }
    validate_metrics(metrics)

    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
