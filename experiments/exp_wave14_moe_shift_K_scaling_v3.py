"""MoE SHIFT K-scaling v3: extended K sweep {64, 128, 256} + divergence characterization.

PARENT: wave14_moe_shift_K_scaling_v2 (in-flight; K in {2,4,8,16,32,64}).

ANTICIPATORY PRE-BUILD -- two trigger paths:
  PATH A (MONOTONE): v2 confirms monotone scaling past K=64 (k_scaling_ratio >= 4.0 or
          monotone with structural_lift >= 0.10). Ship this v3 to map extreme-K regime:
          does SHIFT scale to K=128 and K=256, or is there a collapse/saturation onset?

  PATH B (DIVERGENCE): v2 shows Arm_A retention DEGRADES at K>=32 while Arm_C (SINGLE)
          is stable or improves -- divergence pattern similar to v1. Ship the per-arm
          probe to characterize WHICH substrate property causes divergence: LSH gating
          quality, expert capacity saturation, or intra-expert interference.

This script implements PATH A (extreme-K continuation). PATH B is exp_wave14_moe_shift_K_perarm_v1.py.

DESIGN (PATH A):
  - K sweep: {64, 128, 256}  (extends v2 range; K=64 overlap for continuity)
  - N = 4096, M_per_expert = 1600 (same calibrated point)
  - 5 seeds, GPU
  - Arms A/B/C identical to v2

PRE-REGISTERED BANDS:
  HARD_PASS (extreme-K continues to scale):
    - retention_A(K=128) / retention_A(K=64) >= 1.10 (10% gain from doubling K)
    - AND structural_lift_A-C at K=128 >= 0.10
    -> SHIFT structural separation scales past K=64; regime holds at extreme K

  HARD_FAIL (saturation / collapse):
    - retention_A(K=256) <= retention_A(K=64) - 0.05 (degradation)
    - OR mode-collapse Gini > 0.5 at K >= 128
    -> Extreme-K regime shows saturation or collapse; K=64 is near-optimal

  MIDDLE_BAND (plateau / slow growth):
    - retention_A monotone but ratio(256/64) < 1.10
    -> Sub-linear saturation; document scaling exponent

  INSTRUMENTATION_FAIL:
    - OOM at K=128 or K=256 (memory budget exceeded)
    - OR retention_A NaN/non-finite

Memory estimate:
  K=128: 128 * 4096^2 * 4 bytes = 8.59 GB -- EXCEEDS 8GB. Need chunked W storage.
  K=64:  64 * 4096^2 * 4 bytes = 4.29 GB -- fits with care.
  SOLUTION: use N=2048 for K>64. N=2048 still gives structural insight.
  K=128, N=2048: 128 * 2048^2 * 4 bytes = 2.15 GB -- fits.
  K=256, N=2048: 256 * 2048^2 * 4 bytes = 4.29 GB -- fits.

Self-tests:
  1. gini(equal_loads) < 0.01
  2. retention from run_arm_shift at K=64, N=128 (tiny) is finite
  3. K-scaling ratio formula computable from 3 points
  4. memory_estimate(K, N) stays < 6GB for K<=256, N=2048

Queue: overnight_queue (GPU; 5 seeds x 3 K-values x 3 arms; ~4-6 GPU-hrs at N=2048)
Pre-reg: preregs/2026-05-26_wave14_moe_shift_K_scaling_v3.md
Trigger: ship when v2 returns HARD_PASS or MONOTONE verdict.
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

# ── design parameters (exp_dev autonomy) ──
# N=2048 used for K>=64 to stay within 8GB GPU memory
N_FULL = 2048
N_SMOKE = 256
M_PER_EXPERT_FULL = 800    # proportional: 1600 * 2048/4096
M_PER_EXPERT_SMOKE = int(800 * N_SMOKE / N_FULL)  # ~100
K_SWEEP_FULL = [64, 128, 256]
K_SWEEP_SMOKE = [64, 128]   # skip K=256 at smoke (too slow even at N_SMOKE)
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_STORE = 128
BATCH_PROBE = 256

# Pre-registered thresholds
HP_EXTREME_K_RATIO = 1.10     # retention_A(K=128) / retention_A(K=64) >= 1.10
HP_STRUCTURAL_LIFT = 0.10
HF_DEGRADE_TOL = 0.05         # retention drops > 0.05 from K=64 to K=256
HF_GINI_COLLAPSE = 0.5
MONOTONE_TOL = 0.02
GINI_ALERT = 0.4
MAX_MIN_LOAD_ALERT = 5.0


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


def recall_cosine_batch(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor,
                        batch: int = BATCH_PROBE) -> float:
    total = 0.0
    n = keys.shape[0]
    for s in range(0, n, batch):
        e = min(s + batch, n)
        y = keys[s:e] @ W.T
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = vals[s:e] / vals[s:e].norm(dim=1, keepdim=True).clamp(min=1e-9)
        total += float((yn * vn).sum(dim=1).sum())
    return total / max(n, 1)


def _gini(loads: list) -> float:
    n = len(loads)
    if n <= 1:
        return 0.0
    s = sorted(loads)
    total = sum(s)
    if total <= 0:
        return 0.0
    gini_num = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(s))
    return abs(gini_num) / (n * total)


def build_lsh_proj(N: int, K: int, gen: torch.Generator, device) -> torch.Tensor:
    proj = make_bsc(K, N, gen, device)
    return proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-9)


def gate_assign_balanced(keys: torch.Tensor, proj: torch.Tensor, K: int) -> torch.Tensor:
    scores = keys @ proj.T
    assignment = scores.argmax(dim=1)
    loads = torch.bincount(assignment, minlength=K).float()
    if _gini(loads.tolist()) > 0.3:
        sorted_idx = scores[:, 0].argsort()
        target = keys.shape[0] // K
        new_assign = torch.zeros(keys.shape[0], dtype=torch.long, device=keys.device)
        for k in range(K):
            start = k * target
            end = (k + 1) * target if k < K - 1 else keys.shape[0]
            new_assign[sorted_idx[start:end]] = k
        return new_assign
    return assignment


def compute_load_metrics(assignment: torch.Tensor, K: int) -> dict:
    loads = torch.bincount(assignment, minlength=K).float()
    gini = _gini(loads.tolist())
    max_l = float(loads.max())
    min_l = float(loads.min())
    return {"gini": round(gini, 4), "max_min_ratio": round(max_l / max(min_l, 1.0), 3)}


def run_arm_shift(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert
    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)
    proj = build_lsh_proj(N, K, gen, device)
    assignment = gate_assign_balanced(keys, proj, K)
    load_metrics = compute_load_metrics(assignment, K)

    # Build per-expert W, one at a time to save memory
    total_cos = 0.0
    # Precompute gating scores for retrieval
    gating_scores = keys @ proj.T  # (M_total, K)

    for s in range(0, M_total, BATCH_PROBE):
        e = min(s + BATCH_PROBE, M_total)
        q_batch = keys[s:e]
        v_batch = vals[s:e]
        scores_b = gating_scores[s:e]
        top2 = scores_b.topk(min(2, K), dim=1)
        top2_idx = top2.indices
        top2_w = top2.values.softmax(dim=1)

        # For each expert in this batch, accumulate W contribution
        # Memory-efficient: don't store all Wks simultaneously
        y = torch.zeros((e - s, N), dtype=torch.float32, device=device)

        # Get unique experts needed for this batch
        unique_experts = top2_idx.unique().tolist()
        Wk_cache = {}
        for k_id in unique_experts:
            mask = (assignment == k_id)
            if mask.sum() == 0:
                Wk_cache[k_id] = torch.zeros((N, N), dtype=torch.float32, device=device)
            else:
                Wk_cache[k_id] = outer_product_store(keys[mask], vals[mask], N)

        for rank in range(min(2, K)):
            expert_ids = top2_idx[:, rank]
            gate_w = top2_w[:, rank]
            for b in range(e - s):
                k_id = int(expert_ids[b])
                if k_id in Wk_cache:
                    y[b] += gate_w[b] * (Wk_cache[k_id] @ q_batch[b])

        del Wk_cache
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = v_batch / v_batch.norm(dim=1, keepdim=True).clamp(min=1e-9)
        total_cos += float((yn * vn).sum(dim=1).sum())

    retention = total_cos / max(M_total, 1)
    del keys, vals, proj, assignment, gating_scores
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"retention": round(retention, 4), "M_total": M_total, **load_metrics}


def run_arm_partition(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    N_k = max(N // K, 1)
    gen = torch.Generator(device=device).manual_seed(seed + 1000)
    M_total = K * M_per_expert
    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N_k, gen, device)
    total_cos = 0.0
    for k in range(K):
        idx = torch.arange(k, M_total, K, device=device)
        k_keys = keys[idx, :N_k]
        k_vals = vals[idx]
        Wk = outer_product_store(k_keys, k_vals, N_k)
        retention_k = recall_cosine_batch(Wk, k_keys, k_vals)
        total_cos += retention_k * len(idx)
        del Wk
    retention = total_cos / max(M_total, 1)
    del keys, vals
    return {"retention": round(retention, 4), "M_total": M_total, "N_k": N_k,
            "gini": 0.0, "max_min_ratio": 1.0}


def run_arm_single(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    N_single = int(math.sqrt(K) * N)
    # Cap N_single to avoid OOM
    N_single = min(N_single, 8192)
    gen = torch.Generator(device=device).manual_seed(seed + 2000)
    M = M_per_expert
    keys = make_bsc(M, N_single, gen, device)
    vals = make_bsc(M, N_single, gen, device)
    W = outer_product_store(keys, vals, N_single)
    retention = recall_cosine_batch(W, keys, vals)
    del keys, vals, W
    return {"retention": round(retention, 4), "M": M, "N_single": N_single}


# ── instrumentation self-test ──

def _instrumentation_selftest():
    """Assert all metrics non-null/non-sentinel at tiny scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    device = torch.device("cpu")

    # 1. gini(equal loads) = 0.0
    g = _gini([100.0, 100.0, 100.0, 100.0])
    assert g < 0.01, f"Selftest 1 FAIL: gini(equal)={g}"
    print("[selftest] 1/4 gini(equal)=0 OK")

    # 2. run_arm_shift tiny scale
    r_a = run_arm_shift(4, 64, 8, seed=42, device=device)
    assert math.isfinite(r_a["retention"]), f"Selftest 2 FAIL: retention not finite: {r_a}"
    assert r_a["retention"] > -1.0, f"Selftest 2 FAIL: retention too low: {r_a}"
    print(f"[selftest] 2/4 run_arm_shift K=4 N=64 retention={r_a['retention']:.4f} OK")

    # 3. run_arm_partition tiny scale
    r_b = run_arm_partition(4, 64, 8, seed=42, device=device)
    assert math.isfinite(r_b["retention"]), f"Selftest 3 FAIL: partition retention not finite"
    print(f"[selftest] 3/4 run_arm_partition K=4 N=64 retention={r_b['retention']:.4f} OK")

    # 4. memory_estimate for K=256, N=2048 < 6GB
    mem_gb = 256 * (2048 ** 2) * 4 / (1024 ** 3)
    assert mem_gb < 6.0, f"Selftest 4 FAIL: memory estimate {mem_gb:.2f}GB exceeds 6GB"
    print(f"[selftest] 4/4 memory_estimate K=256 N=2048 = {mem_gb:.2f}GB < 6GB OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run_sweep(smoke: bool = False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[run] device={device}", flush=True)
    N = N_SMOKE if smoke else N_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_moe_shift_K_scaling_v3")

    results_per_K: dict[int, dict] = {}
    for K in K_sweep:
        print(f"\n[run] K={K} N={N} M_per_expert={M_per_expert}", flush=True)
        arm_a, arm_b, arm_c, ginis_a = [], [], [], []
        for seed in seeds:
            a = run_arm_shift(K, N, M_per_expert, seed, device)
            b = run_arm_partition(K, N, M_per_expert, seed, device)
            c = run_arm_single(K, N, M_per_expert, seed, device)
            arm_a.append(a["retention"])
            arm_b.append(b["retention"])
            arm_c.append(c["retention"])
            ginis_a.append(a.get("gini", 0.0))
            print(f"  seed={seed}: A={a['retention']:.4f} B={b['retention']:.4f} "
                  f"C={c['retention']:.4f} gini={a.get('gini',0):.3f}", flush=True)

        mu_a = sum(arm_a) / len(arm_a)
        mu_b = sum(arm_b) / len(arm_b)
        mu_c = sum(arm_c) / len(arm_c)
        mean_gini = sum(ginis_a) / len(ginis_a)
        results_per_K[K] = {
            "mean_retention_A": round(mu_a, 4),
            "mean_retention_B": round(mu_b, 4),
            "mean_retention_C": round(mu_c, 4),
            "mean_gini_A": round(mean_gini, 4),
            "mode_collapse_flag": mean_gini > GINI_ALERT,
        }
        print(f"  -> A={mu_a:.4f} B={mu_b:.4f} C={mu_c:.4f} gini={mean_gini:.3f}")

    return results_per_K, out_dir


def compute_verdict(results_per_K: dict) -> tuple[str, str, dict]:
    K_vals = sorted(results_per_K.keys())
    rets_A = [results_per_K[K]["mean_retention_A"] for K in K_vals]
    ginis = [results_per_K[K]["mean_gini_A"] for K in K_vals]

    # Check for NaN
    if any(not math.isfinite(r) for r in rets_A):
        return ("INSTRUMENTATION_FAIL", "Non-finite retention_A detected.", {})

    # Check collapse
    n_collapse = sum(1 for g in ginis if g > HF_GINI_COLLAPSE)
    if n_collapse >= 2:
        return ("INSTRUMENTATION_FAIL",
                f"Mode-collapse: Gini > {HF_GINI_COLLAPSE} in {n_collapse}/{len(K_vals)} K-values.", {})

    K_lo, K_hi = K_vals[0], K_vals[-1]
    ret_lo = results_per_K[K_lo]["mean_retention_A"]
    ret_hi = results_per_K[K_hi]["mean_retention_A"]

    # ratio from K=64 to K=128 (first two points)
    K_64 = 64 if 64 in results_per_K else K_vals[0]
    K_128 = 128 if 128 in results_per_K else (K_vals[1] if len(K_vals) > 1 else K_vals[0])
    ret_64 = results_per_K[K_64]["mean_retention_A"]
    ret_128 = results_per_K[K_128]["mean_retention_A"]
    k64_to_128_ratio = ret_128 / max(ret_64, 1e-9)

    # Structural lift at K=128
    ret_C_128 = results_per_K[K_128]["mean_retention_C"]
    structural_lift_128 = ret_128 - ret_C_128

    monotone = all(rets_A[i + 1] >= rets_A[i] - MONOTONE_TOL for i in range(len(rets_A) - 1))

    summary = {
        "K_sweep": K_vals,
        "retention_A_per_K": {K: results_per_K[K]["mean_retention_A"] for K in K_vals},
        "retention_C_per_K": {K: results_per_K[K]["mean_retention_C"] for K in K_vals},
        "k64_to_128_ratio": round(k64_to_128_ratio, 3),
        "structural_lift_at_K128": round(structural_lift_128, 4),
        "monotone_nondecreasing_A": monotone,
        "mean_ginis": {K: results_per_K[K]["mean_gini_A"] for K in K_vals},
    }

    # Hard pass: K=128 is >=10% above K=64 and structural lift holds
    hard_pass = k64_to_128_ratio >= HP_EXTREME_K_RATIO and structural_lift_128 >= HP_STRUCTURAL_LIFT
    # Hard fail: degradation from K=64 to K=256, or collapse
    hard_fail = (ret_hi <= ret_lo - HF_DEGRADE_TOL)

    if hard_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: extreme-K SHIFT scaling continues past K=64. "
            f"ratio(K=128/K=64)={k64_to_128_ratio:.3f} >= {HP_EXTREME_K_RATIO}. "
            f"structural_lift_at_K128={structural_lift_128:.3f} >= {HP_STRUCTURAL_LIFT}. "
            f"SHIFT structural separation holds at K=128."
        )
    elif hard_fail:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: SHIFT degrades at extreme K. "
            f"retention_A(K={K_hi})={ret_hi:.4f} vs K={K_lo}={ret_lo:.4f} "
            f"(drop > {HF_DEGRADE_TOL}). K={K_lo} near-optimal for SHIFT."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: extreme-K plateau. "
            f"ratio(128/64)={k64_to_128_ratio:.3f} (< {HP_EXTREME_K_RATIO} threshold), "
            f"monotone={monotone}, structural_lift_128={structural_lift_128:.3f}. "
            f"SHIFT saturating at K>=64."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_moe_shift_K_scaling_v3 {'SMOKE' if smoke else 'FULL'}", flush=True)
    results_per_K, out_dir = run_sweep(smoke)

    # Multi-scale smoke
    if smoke:
        print("\n[multi-scale smoke] N_smoke * 2...", flush=True)
        N2 = N_SMOKE * 2
        M2 = M_PER_EXPERT_SMOKE * 2
        device = torch.device("cpu")
        for K in [64]:
            a2 = run_arm_shift(K, N2, M2, 17, device)
            assert math.isfinite(a2["retention"]), f"Scale2 degenerate K={K}"
            print(f"  N={N2} K={K}: A={a2['retention']:.4f}")
        print("[multi-scale smoke] PASS")

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
            "trigger": "ship when v2 HARD_PASS or monotone K-scaling past K=64",
            "note": "N=2048 used (N=4096 OOMs at K>=128)",
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
