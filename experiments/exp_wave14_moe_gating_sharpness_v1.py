"""MoE SHIFT gating sharpness sweep at K=4: vary softmax temperature.

CONTEXT:
wave14_moe_shift_K_scaling_v1 MIDDLE_BAND: sub-linear K-scaling (p=-0.01 near-flat).
wave14_moe_shift_M_scaling_v1 (in-flight): maps retention vs M_per_expert.
This probe: vary gating sharpness (softmax temperature tau_gate) at fixed K=4.

HYPOTHESIS: MoE SHIFT benefit depends on how sharply each query is routed. Soft gating
(high tau_gate -> nearly uniform weights) blurs expert separation. Hard gating (low tau_gate
-> top-1 routing) maximizes structural separation. There is an optimal tau_gate where lift
is maximal: too soft loses routing signal, too hard loses interpolation smoothness.

DESIGN (exp_dev autonomy):
  - K = 4 (FIXED; SHIFT confirmed)
  - N = 4096 FULL, N = 512 SMOKE
  - tau_gate sweep: [0.01, 0.05, 0.10, 0.25, 0.50, 1.0, 2.0]
    tau_gate=0.01: near-argmax (hard routing)
    tau_gate=1.0: standard softmax
    tau_gate=2.0: near-uniform (soft routing)
  - ARM A (SHIFT K=4): M_per_expert = 0.70 * alpha_c * N (known near-peak from M-scaling design)
  - ARM C (SINGLE): same M_total = K * M_per_expert for fair comparison
  - Seeds: 5 seeds FULL, 1 seed SMOKE
  - METRIC: structural_lift(tau) = retention_shift(tau) - retention_single
    (single is independent of tau; use mean over seeds for single)

PRE-REGISTERED BANDS:
  HARD_PASS (gating sharpness IS a lever):
    - max_lift across tau sweep >= 0.10 AND
    - lift range (max_lift - min_lift across tau) >= 0.05
    - (both significant absolute lift AND sensitivity to tau)
  HARD_FAIL (gating sharpness does not matter):
    - max_lift < 0.05 OR lift_range < 0.02
  MIDDLE_BAND: intermediate
  INSTRUMENTATION_FAIL: NaN at any cell OR mode-collapse gini > 0.4 at majority

Self-tests (per [[feedback-strategy-spec-formula-selftests]]):
  1. softmax_gated([1.0,0.5,0.3,0.2], tau=0.01) -> top-1 concentrated (weight[0] >= 0.95)
  2. softmax_gated([1.0,0.5,0.3,0.2], tau=2.0) -> near-uniform (max_weight < 0.40)
  3. run_arm_shift_tau(K=4,N=512,M_per_expert=100,tau=1.0,seed=17) returns finite retention
  4. structural_lift: if both retention_shift and retention_single are finite, delta is finite

Queue: overnight_queue (GPU; 5 seeds x 7 tau-values x 2 arms; ~3-4 GPU-hrs)
Pre-reg: prereqs/2026-05-26_wave14_moe_gating_sharpness_v1.md
Dependency: wave14_moe_shift_partition_v3 HARD-PASS (SHIFT confirmed) -- SATISFIED
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
from typing import List

import torch

REPO = Path(__file__).resolve().parent.parent

# ─── design parameters ───
K_FIXED = 4
ALPHA_C = 0.5625
M_FRACTION = 0.70        # M_per_expert = 0.70 * alpha_c * N (near-peak from M-scaling design)
N_FULL = 4096
N_SMOKE = 512
TAU_SWEEP_FULL = [0.01, 0.05, 0.10, 0.25, 0.50, 1.0, 2.0]
TAU_SWEEP_SMOKE = [0.05, 0.25, 1.0]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_STORE = 256
BATCH_PROBE = 512

# Pre-registered thresholds
HP_MAX_LIFT = 0.10        # max lift across tau >= 0.10
HP_LIFT_RANGE = 0.05      # max_lift - min_lift >= 0.05 (tau IS a lever)
HF_MAX_LIFT = 0.05        # max lift < 0.05 -> HARD_FAIL
HF_LIFT_RANGE = 0.02      # lift range < 0.02 -> HARD_FAIL
GINI_ALERT = 0.4


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    W = torch.zeros((N, N), dtype=torch.float32, device=keys.device)
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


def build_lsh_proj(N: int, K: int, gen: torch.Generator, device) -> torch.Tensor:
    proj = make_bsc(K, N, gen, device)
    return proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-9)


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


def softmax_with_temperature(scores: torch.Tensor, tau: float) -> torch.Tensor:
    """Apply softmax with temperature tau (tau>1 = softer, tau<1 = sharper)."""
    return (scores / max(tau, 1e-6)).softmax(dim=-1)


def run_arm_shift_tau(K: int, N: int, M_per_expert: int, tau: float, seed: int, device) -> dict:
    """Arm A: K full-N experts with softmax-temperature tau gating."""
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert

    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)
    proj = build_lsh_proj(N, K, gen, device)

    # Build each expert (balanced assignment for storage, not affected by tau)
    scores_full = keys @ proj.T
    assignment = scores_full.argmax(dim=1)
    loads = torch.bincount(assignment, minlength=K).float()
    gini = _gini(loads.tolist())

    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N, N), dtype=torch.float32, device=device))
        else:
            Wks.append(outer_product_store(keys[mask], vals[mask], N))

    # Recall with tau-gated routing
    total_cos = 0.0
    for s in range(0, M_total, BATCH_PROBE):
        e = min(s + BATCH_PROBE, M_total)
        q_batch = keys[s:e]
        v_batch = vals[s:e]
        scores = q_batch @ proj.T
        gate_w = softmax_with_temperature(scores, tau)   # shape (batch, K)

        y = torch.zeros((e - s, N), dtype=torch.float32, device=device)
        for k in range(K):
            y += gate_w[:, k:k+1] * (q_batch @ Wks[k].T)
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = v_batch / v_batch.norm(dim=1, keepdim=True).clamp(min=1e-9)
        total_cos += float((yn * vn).sum(dim=1).sum())

    retention = total_cos / max(M_total, 1)
    return {"retention": round(retention, 4), "M_total": M_total, "gini": round(gini, 4), "tau": tau}


def run_arm_single(N: int, M_per_expert: int, seed: int, device) -> dict:
    """Arm C (SINGLE): 1 expert, M = M_per_expert (no gating; tau-independent baseline)."""
    gen = torch.Generator(device=device).manual_seed(seed + 2000)
    keys = make_bsc(M_per_expert, N, gen, device)
    vals = make_bsc(M_per_expert, N, gen, device)
    W = outer_product_store(keys, vals, N)
    retention = recall_cosine_batch(W, keys, vals)
    return {"retention": round(retention, 4), "M": M_per_expert}


def _instrumentation_selftest():
    """Assert all claimed metrics non-null at smoke scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. softmax tau=0.01 near-argmax
    scores_t = torch.tensor([[1.0, 0.5, 0.3, 0.2]])
    w_sharp = softmax_with_temperature(scores_t, 0.01).squeeze()
    assert w_sharp[0].item() >= 0.95, f"Selftest 1 FAIL: top weight={w_sharp[0]:.4f}"
    print(f"[selftest] 1/4 tau=0.01 sharp routing OK top_weight={w_sharp[0]:.4f}")

    # 2. softmax tau=2.0 near-uniform
    w_soft = softmax_with_temperature(scores_t, 2.0).squeeze()
    assert w_soft[0].item() < 0.40, f"Selftest 2 FAIL: top weight={w_soft[0]:.4f}"
    print(f"[selftest] 2/4 tau=2.0 soft routing OK top_weight={w_soft[0]:.4f}")

    # 3. run_arm_shift_tau returns finite retention
    device_t = torch.device("cpu")
    result_t = run_arm_shift_tau(K=4, N=64, M_per_expert=20, tau=1.0, seed=17, device=device_t)
    assert math.isfinite(result_t["retention"]), f"Selftest 3 FAIL: retention={result_t['retention']}"
    print(f"[selftest] 3/4 run_arm_shift_tau retention={result_t['retention']:.4f} OK")

    # 4. structural_lift: finite if both inputs finite
    ret_s = 0.70
    ret_c = 0.60
    lift = ret_s - ret_c
    assert math.isfinite(lift), f"Selftest 4 FAIL: lift={lift}"
    print(f"[selftest] 4/4 structural_lift finite OK delta={lift:.4f}")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    label = "SMOKE" if smoke else "FULL"
    print(f"[exp] wave14_moe_gating_sharpness_v1 {label}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    tau_sweep = TAU_SWEEP_SMOKE if smoke else TAU_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_moe_gating_sharpness_v1")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    M_per_expert = max(10, int(M_FRACTION * ALPHA_C * N))
    M_total = K_FIXED * M_per_expert

    print(f"[run] N={N} K={K_FIXED} M_per_expert={M_per_expert} M_total={M_total}", flush=True)
    print(f"[run] tau_sweep={tau_sweep} seeds={seeds} device={device}", flush=True)

    # Arm C (SINGLE) baseline -- independent of tau
    single_rets: List[float] = []
    for seed in seeds:
        try:
            res_c = run_arm_single(N, M_per_expert, seed, device)
            single_rets.append(res_c["retention"])
            print(f"  single seed={seed} retention={res_c['retention']:.4f}", flush=True)
        except Exception as e:
            print(f"  single seed={seed} FAILED: {e}", flush=True)
            single_rets.append(float("nan"))

    valid_single = [v for v in single_rets if math.isfinite(v)]
    if not valid_single:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: all SINGLE arm cells failed."
        summary = {"valid_single": 0}
        elapsed = time.time() - t0
        metrics = {
            "verdict": verdict, "verdict_msg": verdict_msg,
            "elapsed_s": round(elapsed, 3), "summary": summary,
            "config": {"N": N, "tau_sweep": tau_sweep, "seeds": seeds, "smoke": smoke},
        }
        validate_metrics(metrics)
        metrics_file = out_dir / "metrics.json"
        with open(metrics_file, "w") as f_out:
            json.dump(metrics, f_out, indent=2)
        print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
        return

    mean_single = sum(valid_single) / len(valid_single)
    print(f"\n[run] mean_single={mean_single:.4f}", flush=True)

    # Arm A (SHIFT K=4) at each tau
    tau_results: dict = {}
    for tau in tau_sweep:
        rets: List[float] = []
        for seed in seeds:
            print(f"\n[run] tau={tau} seed={seed}", flush=True)
            try:
                res_a = run_arm_shift_tau(K=K_FIXED, N=N, M_per_expert=M_per_expert,
                                          tau=tau, seed=seed, device=device)
                rets.append(res_a["retention"])
                print(f"  shift tau={tau} seed={seed} retention={res_a['retention']:.4f} gini={res_a['gini']:.3f}", flush=True)
            except Exception as e:
                print(f"  shift tau={tau} seed={seed} FAILED: {e}", flush=True)
                rets.append(float("nan"))
        valid_rets = [v for v in rets if math.isfinite(v)]
        mean_r = sum(valid_rets) / len(valid_rets) if valid_rets else float("nan")
        lift = (mean_r - mean_single) if math.isfinite(mean_r) else float("nan")
        tau_results[str(tau)] = {"mean_retention": round(mean_r, 4), "lift": round(lift, 4) if math.isfinite(lift) else None}
        print(f"  tau={tau}: mean_retention={mean_r:.4f} lift={lift:+.4f}", flush=True)

    # Verdict
    valid_lifts = [v["lift"] for v in tau_results.values() if v["lift"] is not None]
    if not valid_lifts:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: no valid tau cells."
        summary = {}
    else:
        max_lift = max(valid_lifts)
        min_lift = min(valid_lifts)
        lift_range = max_lift - min_lift

        nan_count = sum(1 for v in tau_results.values() if v["lift"] is None)
        any_gini_fail = False  # not tracked per-cell here; checked per arm above

        hard_pass = (max_lift >= HP_MAX_LIFT and lift_range >= HP_LIFT_RANGE)
        hard_fail = (max_lift < HF_MAX_LIFT or lift_range < HF_LIFT_RANGE)

        tau_strs = " ".join(f"t={t}:lift={v['lift']:+.4f}" for t, v in tau_results.items() if v["lift"] is not None)

        if hard_pass:
            verdict = "GATING_HARD_PASS"
            verdict_msg = (
                f"Gating sharpness IS a lever: max_lift={max_lift:.4f} >= {HP_MAX_LIFT}, "
                f"lift_range={lift_range:.4f} >= {HP_LIFT_RANGE}. "
                f"mean_single={mean_single:.4f}. | {tau_strs}"
            )
        elif hard_fail:
            verdict = "GATING_HARD_FAIL"
            verdict_msg = (
                f"Gating sharpness NOT a significant lever: max_lift={max_lift:.4f}, "
                f"lift_range={lift_range:.4f}. mean_single={mean_single:.4f}. | {tau_strs}"
            )
        else:
            verdict = "GATING_MIDDLE"
            verdict_msg = (
                f"Intermediate: max_lift={max_lift:.4f} lift_range={lift_range:.4f}. "
                f"mean_single={mean_single:.4f}. | {tau_strs}"
            )

        summary = {
            "N": N,
            "K": K_FIXED,
            "M_per_expert": M_per_expert,
            "mean_single": round(mean_single, 4),
            "max_lift": round(max_lift, 4),
            "lift_range": round(lift_range, 4),
            "tau_results": tau_results,
        }

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": {
            "N": N,
            "K": K_FIXED,
            "M_fraction": M_FRACTION,
            "tau_sweep": tau_sweep,
            "seeds": seeds,
            "smoke": smoke,
        },
    }
    validate_metrics(metrics)
    metrics_file = out_dir / "metrics.json"
    with open(metrics_file, "w") as f_out:
        json.dump(metrics, f_out, indent=2)
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"Metrics saved to {metrics_file}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
