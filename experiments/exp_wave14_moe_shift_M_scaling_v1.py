"""MoE SHIFT M-scaling sweep: retention vs M_per_expert at fixed K=4.

CONTEXT:
wave14_moe_shift_K_scaling_v1 returned MIDDLE_BAND: sub-linear K-scaling (exponent p=-0.01
near-flat; ratio=0.97). Structural separation IS present (SHIFT > SINGLE throughout) but
diminishing returns in K suggest intra-expert load is the dominant lever, not expert count.

HYPOTHESIS: Retention in SHIFT MoE is primarily governed by how loaded each expert is
relative to its capacity (M_per_expert / alpha_c * N). Sweeping M_per_expert at fixed K=4
maps the operating curve and identifies the optimal operating point.

This is the "Within-SHIFT class refinement" branch named in Part B refill:
  - Map retention(M_per_expert) at K=4 (confirmed SHIFT regime)
  - Primary: does retention degrade gracefully as M_per_expert increases toward capacity?
  - Secondary: what is the optimal M_per_expert for maximum K=4 aggregate retention?
  - Framing: product claim "each MoE-SHIFT expert operates at 70% capacity for best lift"

DESIGN (exp_dev autonomy):
  - K = 4 (FIXED; SHIFT confirmed at K=4 with lift=0.205 per v3)
  - M_per_expert sweep: proportions of alpha_c*N = 0.5625*4096 = 2304 items
    Fractions: [0.25, 0.40, 0.55, 0.70, 0.85, 1.00] x alpha_c*N
    Absolute M: [576, 921, 1267, 1613, 1958, 2304] at N=4096
    Rationale: maps from well-below-capacity to at-capacity; expected knee at ~0.70
  - N = 4096 (FULL only; K=4 SHIFT validated at this N)
  - Seeds: 5 seeds [7,17,23,31,41]
  - ARM A (SHIFT K=4): 4 full-N experts, M_total = 4 * M_per_expert
  - ARM C (SINGLE): 1 expert at N, M = M_per_expert (no structural separation)
  - METRIC: structural_lift(M) = retention_A(M) - retention_C(M)
    Secondary: lift_vs_capacity_fraction(M) curve shape

PRE-REGISTERED BANDS:
  HARD_PASS (capacity-operating-curve CONFIRMED):
    - Peak structural_lift >= 0.15 at some M_per_expert in sweep AND
    - Lift degrades at M_per_expert = alpha_c*N (at-capacity) by >= 0.05 vs peak
    - (i.e., there is a clear optimal operating point below full capacity)
  HARD_FAIL (no operating curve):
    - Peak structural_lift < 0.05 at all M values
    - (structural separation negligible across all load levels)
  MIDDLE_BAND: peak_lift in [0.05, 0.15)
  INSTRUMENTATION_FAIL: mode-collapse (gini > 0.4) at majority of cells OR
    retention NaN at any cell

Self-tests (per [[feedback-strategy-spec-formula-selftests]]):
  1. alpha_c * N = 0.5625 * 4096 = 2304.0 (exact). Input: alpha_c=0.5625, N=4096.
  2. M fractions [0.25, 0.40, 0.55, 0.70, 0.85, 1.00] -> abs M at N=4096:
     [576, 921, 1267, 1613, 1958, 2304].
  3. run_arm_shift(K=4, N=512, M_per_expert=100) returns finite retention at smoke.
  4. structural_lift = retention_A - retention_C: if both ~0.70, lift=0.

Queue: overnight_queue (GPU; 5 seeds x 6 M-values x 2 arms; ~3-4 GPU-hrs)
Pre-reg: prereqs/2026-05-26_wave14_moe_shift_M_scaling_v1.md
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

import torch

REPO = Path(__file__).resolve().parent.parent

# ─── design parameters ───
K_FIXED = 4                        # confirmed SHIFT regime
ALPHA_C = 0.5625                   # from wave14_moe_alpha_c_prestep_v3 HARD_PASS
N_FULL = 4096
N_SMOKE = 512
# M_per_expert as fraction of alpha_c*N
M_FRACTIONS = [0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
M_FRACTIONS_SMOKE = [0.25, 0.55, 1.00]  # 3 points for smoke
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_STORE = 256
BATCH_PROBE = 512

# Pre-registered thresholds
HP_PEAK_LIFT = 0.15       # structural lift at best M >= this
HP_CAPACITY_DEGRADE = 0.05  # lift drops by >= this from peak to M=alpha_c*N
HF_MAX_LIFT = 0.05        # peak lift < this -> HARD_FAIL
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


def run_arm_shift(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    """Arm A: K full-N experts, M_total = K * M_per_expert."""
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert

    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)
    proj = build_lsh_proj(N, K, gen, device)
    assignment = gate_assign_balanced(keys, proj, K)
    loads = torch.bincount(assignment, minlength=K).float()
    gini = _gini(loads.tolist())

    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N, N), dtype=torch.float32, device=device))
        else:
            Wks.append(outer_product_store(keys[mask], vals[mask], N))

    total_cos = 0.0
    for s in range(0, M_total, BATCH_PROBE):
        e = min(s + BATCH_PROBE, M_total)
        q_batch = keys[s:e]
        v_batch = vals[s:e]
        scores = q_batch @ proj.T
        top2 = scores.topk(min(2, K), dim=1)
        top2_idx = top2.indices
        top2_w = top2.values.softmax(dim=1)

        y = torch.zeros((e - s, N), dtype=torch.float32, device=device)
        for rank in range(min(2, K)):
            expert_ids = top2_idx[:, rank]
            gate_w = top2_w[:, rank]
            for b in range(e - s):
                y[b] += gate_w[b] * (Wks[expert_ids[b]] @ q_batch[b])
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = v_batch / v_batch.norm(dim=1, keepdim=True).clamp(min=1e-9)
        total_cos += float((yn * vn).sum(dim=1).sum())

    retention = total_cos / max(M_total, 1)
    return {"retention": round(retention, 4), "M_total": M_total, "gini": round(gini, 4)}


def run_arm_single(N: int, M_per_expert: int, seed: int, device) -> dict:
    """Arm C (SINGLE): 1 expert at N, M = M_per_expert."""
    gen = torch.Generator(device=device).manual_seed(seed + 2000)
    keys = make_bsc(M_per_expert, N, gen, device)
    vals = make_bsc(M_per_expert, N, gen, device)
    W = outer_product_store(keys, vals, N)
    retention = recall_cosine_batch(W, keys, vals)
    return {"retention": round(retention, 4), "M": M_per_expert}


def _instrumentation_selftest():
    """Assert all claimed metrics non-null at smoke scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    device = torch.device("cpu")

    # 1. alpha_c*N arithmetic: 0.5625 * 4096 = 2304
    cap = ALPHA_C * N_FULL
    assert abs(cap - 2304.0) < 0.1, f"Selftest 1 FAIL: alpha_c*N={cap} expected 2304"
    print(f"[selftest] 1/4 alpha_c * N = {cap:.1f} (expected 2304) OK")

    # 2. M fractions at N_SMOKE: 0.25 * alpha_c * 512 = 72
    m_list = [max(int(f * ALPHA_C * N_SMOKE), 1) for f in M_FRACTIONS_SMOKE]
    assert all(m > 0 for m in m_list), f"Selftest 2 FAIL: M list has zeros: {m_list}"
    print(f"[selftest] 2/4 M fractions at N_SMOKE={N_SMOKE}: {m_list} OK")

    # 3. run_arm_shift returns finite retention at tiny scale
    M_test = max(int(0.55 * ALPHA_C * N_SMOKE), 1)
    r = run_arm_shift(K_FIXED, N_SMOKE, M_test, seed=42, device=device)
    assert math.isfinite(r["retention"]), f"Selftest 3 FAIL: retention={r['retention']}"
    print(f"[selftest] 3/4 run_arm_shift K=4 N={N_SMOKE} M={M_test} retention={r['retention']:.4f} OK")

    # 4. structural_lift computable: lift = retention_A - retention_C
    r_c = run_arm_single(N_SMOKE, M_test, seed=42, device=device)
    lift = r["retention"] - r_c["retention"]
    assert math.isfinite(lift), f"Selftest 4 FAIL: lift={lift}"
    print(f"[selftest] 4/4 structural_lift = {lift:.4f} (retention_A={r['retention']:.4f} "
          f"retention_C={r_c['retention']:.4f}) OK")
    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_moe_shift_M_scaling_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[run] device={device}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    fracs = M_FRACTIONS_SMOKE if smoke else M_FRACTIONS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_moe_shift_M_scaling_v1")

    # Pre-compute M_per_expert values
    m_per_expert_list = [max(int(f * ALPHA_C * N), 1) for f in fracs]
    print(f"[run] K={K_FIXED} N={N} M_per_expert={m_per_expert_list} fractions={fracs}",
          flush=True)

    results_per_M: dict = {}
    for frac, M_per_expert in zip(fracs, m_per_expert_list):
        print(f"\n[run] M_per_expert={M_per_expert} (frac={frac:.2f} x alpha_c*N={N*ALPHA_C:.0f})",
              flush=True)
        arm_a_rets, arm_c_rets, ginis = [], [], []

        for seed in seeds:
            a = run_arm_shift(K_FIXED, N, M_per_expert, seed, device)
            c = run_arm_single(N, M_per_expert, seed, device)
            arm_a_rets.append(a["retention"])
            arm_c_rets.append(c["retention"])
            ginis.append(a["gini"])
            print(f"  seed={seed}: A={a['retention']:.4f} C={c['retention']:.4f} "
                  f"lift={a['retention']-c['retention']:.4f} gini_A={a['gini']:.3f}", flush=True)

        mu_a = sum(arm_a_rets) / len(arm_a_rets)
        mu_c = sum(arm_c_rets) / len(arm_c_rets)
        struct_lift = mu_a - mu_c
        mean_gini = sum(ginis) / len(ginis)

        results_per_M[frac] = {
            "frac": frac,
            "M_per_expert": M_per_expert,
            "M_total_K4": K_FIXED * M_per_expert,
            "retention_A_mean": round(mu_a, 4),
            "retention_C_mean": round(mu_c, 4),
            "structural_lift": round(struct_lift, 4),
            "mean_gini": round(mean_gini, 4),
            "mode_collapse_alert": mean_gini > GINI_ALERT,
        }
        print(f"  M_SUMMARY: lift={struct_lift:.4f} A_mean={mu_a:.4f} C_mean={mu_c:.4f}",
              flush=True)

    # Verdict computation
    lifts = [r["structural_lift"] for r in results_per_M.values()]
    ginis = [r["mean_gini"] for r in results_per_M.values()]
    mode_collapses = sum(1 for r in results_per_M.values() if r["mode_collapse_alert"])

    if mode_collapses > len(fracs) // 2:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (
            f"INSTRUMENTATION_FAIL: mode-collapse (gini > {GINI_ALERT}) at "
            f"{mode_collapses}/{len(fracs)} M cells. LSH gating breakdown."
        )
    elif any(not math.isfinite(l) for l in lifts):
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: non-finite retention in some cells."
    else:
        peak_lift = max(lifts)
        peak_frac = list(results_per_M.keys())[lifts.index(peak_lift)]
        # Lift at full capacity
        lift_at_capacity = results_per_M.get(1.00, {}).get("structural_lift", lifts[-1])

        capacity_degrade = peak_lift - lift_at_capacity

        if peak_lift >= HP_PEAK_LIFT and capacity_degrade >= HP_CAPACITY_DEGRADE:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: MoE-SHIFT M-scaling curve CONFIRMED. "
                f"Peak structural_lift={peak_lift:.4f} >= {HP_PEAK_LIFT} at frac={peak_frac:.2f} "
                f"AND capacity_degrade={capacity_degrade:.4f} >= {HP_CAPACITY_DEGRADE}. "
                f"Clear optimal operating point below full capacity."
            )
        elif peak_lift < HF_MAX_LIFT:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL: No structural lift. Peak={peak_lift:.4f} < {HF_MAX_LIFT}. "
                f"MoE-SHIFT structural separation absent at all load levels."
            )
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND: Partial M-scaling curve. "
                f"peak_lift={peak_lift:.4f} at frac={peak_frac:.2f}, "
                f"capacity_degrade={capacity_degrade:.4f}. "
                f"Lift present but curve shape inconclusive. "
                f"| M-sweep: " + " | ".join(
                    f"frac={r['frac']:.2f}:lift={r['structural_lift']:.4f}"
                    for r in results_per_M.values()
                )
            )

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": {
            "M_sweep": {
                str(frac): r for frac, r in results_per_M.items()
            },
            "peak_structural_lift": round(max(lifts), 4),
            "peak_frac": float(list(results_per_M.keys())[lifts.index(max(lifts))]),
        },
        "config": {
            "K_fixed": K_FIXED,
            "N": N,
            "alpha_c": ALPHA_C,
            "M_fractions": fracs,
            "M_per_expert_values": m_per_expert_list,
            "seeds": seeds,
            "smoke": smoke,
        },
    }
    validate_metrics(metrics)
    metrics_file = out_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
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
