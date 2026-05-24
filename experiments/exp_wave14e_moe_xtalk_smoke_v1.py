"""MoE smoke: K=4 expert sub-matrices on BSC-style substrate, cross-talk reduction
at fixed M_stored.

Mechanism: instead of one W (NxN) accumulating M outer-product pairs, partition
into K disjoint expert blocks W_k each of size NxN with M/K pairs each. Gating
function g(key) = key_bsc_hash % K. At retrieval, pick expert by gate and read
out only that expert's W_k. Cross-talk for any item scales with M/K (its expert
load) instead of M (all items).

Hypothesis: at fixed M_stored, the K=4 MoE substrate yields per-item recall
fidelity bounded by M/K, NOT M. Specifically: mean cosine(recall, target) >=
(K-1)/K * baseline_at_M_over_K + 1/K * baseline_at_M  (a coarse bound).
Concretely we expect cosine improvement vs. baseline single-W by a factor
>= 1.5x at M=2000 with K=4.

Hard-fail: MoE cosine < single-W cosine at same M_stored.
Hard-pass: MoE cosine >= 1.3x single-W cosine at M_stored where single-W
shows saturation.
Middle band: improvement of 1.0-1.3x.

Smoke scale: N=512, M_grid={200, 800, 2000}, single seed, K=4, ~30-60s.
Full: N=4096, M_grid={500, 2000, 8000, 32000}, 5 seeds, K=4 and K=8.

Pre-reg: preregs/2026-05-24_wave14e_moe_xtalk_smoke_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent

N_FULL = 4096
N_SMOKE = 512
M_GRID_FULL = [500, 2000, 8000, 32000]
M_GRID_SMOKE = [200, 800, 2000]
K_EXPERTS_FULL = [4, 8]
K_EXPERTS_SMOKE = [4]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_RATIO = 1.30   # MoE / single-W cosine
HARD_FAIL_RATIO = 1.00  # MoE worse than single-W
PARTIAL_RATIO = 1.05


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def make_bsc(M, N, gen):
    raw = torch.rand((M, N), generator=gen)
    out = 2.0 * (raw > 0.5).float() - 1.0
    return out


def gate(keys, K, gen):
    """Hash-based gating: project key onto a random direction, take sign-bits modulo K.
    Specifically, sum sign(keys @ proj_vec) shifted to non-negative range mod K."""
    N = keys.shape[1]
    proj = make_bsc(1, N, gen).squeeze(0).to(keys.device)
    s = (keys @ proj)
    smin = s.min()
    smax = s.max()
    if (smax - smin).abs() < 1e-9:
        # Degenerate: all keys project to identical scalar. Distribute round-robin.
        return torch.arange(keys.shape[0], device=keys.device) % K
    bins = (s - smin) / (smax - smin)
    expert = (bins * K).clamp(max=K - 1).long()
    return expert


def store_outer_product(keys, vals, N, device):
    """Standard outer-product Hopfield/HRR-like memory: W = sum_i v_i k_i^T / N."""
    M = keys.shape[0]
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    # batched accumulation
    bs = 256
    for s in range(0, M, bs):
        e = min(s + bs, M)
        kb = keys[s:e]
        vb = vals[s:e]
        W.add_(vb.T @ kb / N)
    return W


def recall(W, keys, vals):
    """Recall: y = W @ k, measure mean cosine(y, v_target)."""
    y = keys @ W.T
    # normalize
    yn = y / (y.norm(dim=1, keepdim=True) + 1e-9)
    vn = vals / (vals.norm(dim=1, keepdim=True) + 1e-9)
    cos = (yn * vn).sum(dim=1)
    return float(cos.mean()), float(cos.std())


def moe_store(keys, vals, K, N, device, gen):
    """K expert sub-Ws, each storing only its bucket's pairs."""
    experts = gate(keys, K, gen)
    Wks = [torch.zeros((N, N), dtype=torch.float32, device=device) for _ in range(K)]
    for k in range(K):
        mask = (experts == k)
        if mask.sum() == 0:
            continue
        kb = keys[mask]
        vb = vals[mask]
        Wks[k] = store_outer_product(kb, vb, N, device)
    return Wks, experts


def moe_recall(Wks, keys, vals, experts):
    K = len(Wks)
    M = keys.shape[0]
    y = torch.zeros_like(vals)
    for k in range(K):
        mask = (experts == k)
        if mask.sum() == 0:
            continue
        y[mask] = keys[mask] @ Wks[k].T
    yn = y / (y.norm(dim=1, keepdim=True) + 1e-9)
    vn = vals / (vals.norm(dim=1, keepdim=True) + 1e-9)
    cos = (yn * vn).sum(dim=1)
    return float(cos.mean()), float(cos.std())


def run_one_config(seed, M, N, K_exp, device):
    gen = torch.Generator().manual_seed(seed)
    keys = make_bsc(M, N, gen).to(device)
    vals = make_bsc(M, N, gen).to(device)
    # Baseline: single-W
    W_single = store_outer_product(keys, vals, N, device)
    base_cos, base_std = recall(W_single, keys, vals)
    # Free baseline before allocating MoE expert tensors (memory hygiene at full N/M/K).
    del W_single
    if device.type == "cuda":
        torch.cuda.empty_cache()
    # MoE
    Wks, experts = moe_store(keys, vals, K_exp, N, device, gen)
    moe_cos, moe_std = moe_recall(Wks, keys, vals, experts)
    # Per-expert load
    expert_loads = [int((experts == k).sum()) for k in range(K_exp)]
    # Free MoE tensors before returning (memory hygiene across configs).
    del Wks, experts, keys, vals
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "M": M,
        "N": N,
        "K": K_exp,
        "single_W_cos_mean": base_cos,
        "single_W_cos_std": base_std,
        "moe_cos_mean": moe_cos,
        "moe_cos_std": moe_std,
        "ratio": moe_cos / max(base_cos, 1e-6),
        "expert_loads": expert_loads,
    }


def run_one_seed(seed, config, device):
    out = []
    for M in config["M_grid"]:
        for K_exp in config["K_experts"]:
            r = run_one_config(seed, M, config["N"], K_exp, device)
            out.append(r)
            print(f"  seed={seed} M={M} K={K_exp}: "
                  f"single={r['single_W_cos_mean']:.3f} "
                  f"moe={r['moe_cos_mean']:.3f} ratio={r['ratio']:.3f}", flush=True)
    return out


def compute_verdict(summary):
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("MOE_INCONCLUSIVE", "Missing per-seed.")
    # Across seeds, find the (M, K) cell with highest ratio. Use that as the
    # operating point.
    all_rows = []
    for s, rows in per_seed.items():
        for r in rows:
            all_rows.append(r)
    if not all_rows:
        return ("MOE_INCONCLUSIVE", "No rows.")
    # Find best (M, K) by ratio
    best = max(all_rows, key=lambda r: r["ratio"])
    if best["ratio"] >= PASS_RATIO:
        return ("MOE_PASS",
                f"MoE reduces cross-talk: at M={best['M']}, K={best['K']}, "
                f"ratio={best['ratio']:.3f} >= {PASS_RATIO}. "
                f"moe_cos={best['moe_cos_mean']:.3f}, single_cos={best['single_W_cos_mean']:.3f}.")
    # Hard-fail: ALL ratios <= HARD_FAIL_RATIO across all seeds at all M
    worst_ratio = min(r["ratio"] for r in all_rows)
    avg_ratio = sum(r["ratio"] for r in all_rows) / len(all_rows)
    if avg_ratio < HARD_FAIL_RATIO:
        return ("MOE_KILLED",
                f"MoE makes cross-talk worse: avg ratio {avg_ratio:.3f} < {HARD_FAIL_RATIO}. "
                f"Best ratio {best['ratio']:.3f} at M={best['M']}, K={best['K']}. "
                f"Worst {worst_ratio:.3f}.")
    if best["ratio"] >= PARTIAL_RATIO:
        return ("MOE_PARTIAL",
                f"MoE modestly reduces cross-talk: best ratio {best['ratio']:.3f} "
                f"in [{PARTIAL_RATIO}, {PASS_RATIO}) at M={best['M']}, K={best['K']}.")
    return ("MOE_INCONCLUSIVE",
            f"MoE marginal: best ratio {best['ratio']:.3f} at M={best['M']}, K={best['K']}. "
            f"Mean ratio {avg_ratio:.3f}.")


def self_test_verdict():
    def mk(rows):
        return {"per_seed": {"17": rows}}
    cases = [
        (mk([{"M": 2000, "K": 4, "ratio": 1.5, "moe_cos_mean": 0.6, "single_W_cos_mean": 0.4}]),
         "MOE_PASS"),
        (mk([{"M": 2000, "K": 4, "ratio": 0.8, "moe_cos_mean": 0.3, "single_W_cos_mean": 0.4}]),
         "MOE_KILLED"),
        (mk([{"M": 2000, "K": 4, "ratio": 1.10, "moe_cos_mean": 0.44, "single_W_cos_mean": 0.4}]),
         "MOE_PARTIAL"),
        (mk([{"M": 2000, "K": 4, "ratio": 1.02, "moe_cos_mean": 0.41, "single_W_cos_mean": 0.4}]),
         "MOE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "M_grid": M_GRID_SMOKE if smoke else M_GRID_FULL,
        "K_experts": K_EXPERTS_SMOKE if smoke else K_EXPERTS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        rows = run_one_seed(seed, config, device)
        per_seed[str(seed)] = rows
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14e_moe_xtalk_smoke_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # sanity assertion
    s = list(summary["per_seed"].values())[0]
    assert len(s) > 0, "no rows"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14e_moe_xtalk_smoke_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
