"""R-PRIME-2 MoE M_c falsifier — K-sweep at FIXED M_total.

Hypothesis (per research_R_PRIME_directions_2026-05-24.md R-PRIME-2):
If substrate retention is governed by per-expert capacity M_c (not global M),
then K-sweep at fixed M_total should show retention(K) = f(M_total / K).
Mixture-of-Experts framing: K disjoint expert sub-substrates each store
M_total/K items.

This is DIFFERENT from `exp_wave14e_moe_xtalk_smoke_v1.py` (which sweeps M at
fixed K). Here K varies, M_total fixed.

Mechanism: at K experts, partition the BSC substrate into K disjoint blocks
W_k of N/K rows each, gate by hash(key) % K, and store M_total/K outer-product
pairs per block. Retention probe: bind M_total key-value pairs, then measure
mean cosine(recall, target) over all M_total items.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered below.
Per [[feedback-rehabilitation-after-rejection]]: this is the lead R-PRIME falsifier
returning to TOP priority post-R-PRIME-3 closure v193.

Pre-reg:
    HARD-PASS: retention(K) tracks 1 - (M_total/K) / M_capacity prediction within +/-10%
               across >=4 K values (K in {2,4,8,16}). Specifically: retention(K=16) - retention(K=2)
               >= 0.20 (20 pp), monotone-non-decreasing in K with tolerance 0.02.
               -> MoE row promoted 🔬 -> 🟢 (implicit-expert allocation supported).
    HARD-FAIL: retention flat in K — abs(retention(K=16) - retention(K=2)) < 0.05 (5 pp)
               AND max_dev_from_mean across all K < 0.03 (3 pp).
               -> MoE-on-substrate REJECTED.
    MIDDLE: any intermediate; report bands.

Pre-reg: preregs/2026-05-24_wave14_rprime2_moe_K_sweep_v1.md
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

# ───── design parameters (exp_dev autonomy) ─────
N_FULL = 4096           # substrate width N (per-expert N_k = N/K)
N_SMOKE = 1024
M_TOTAL_FULL = 4096     # fixed total items stored across K experts
M_TOTAL_SMOKE = 256
K_SWEEP_FULL = [2, 4, 8, 16]     # exp_dev autonomy: 4-point K-sweep (≥4 per R-PRIME-2 falsifier spec)
K_SWEEP_SMOKE = [2, 4]
SEEDS_FULL = [7, 17, 23, 31, 41]   # 5 seeds per [[project-research-playbook]]
SEEDS_SMOKE = [17]
BATCH_PROBE_FULL = 1024
BATCH_PROBE_SMOKE = 256

# Falsifier thresholds (pre-registered).
PASS_LIFT = 0.20           # retention(K=16) - retention(K=2) lift in pp
PASS_TRACK_TOL = 0.10      # prediction tracks 1 - M/K/M_cap within +/-10 pp
MONOTONE_TOL = 0.02        # monotonicity tolerance
FAIL_FLAT_LIFT = 0.05      # max - min across K must exceed to escape HARD_FAIL
FAIL_MAX_DEV = 0.03        # max deviation from mean across K


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


def is_monotone_nondecreasing(values, tol=0.01):
    for i in range(len(values) - 1):
        if values[i + 1] < values[i] - tol:
            return False
    return True


def bsc_atoms(num: int, dim: int, gen: torch.Generator, device) -> torch.Tensor:
    """Return num x dim {-1,+1} BSC code vectors."""
    return (torch.randint(0, 2, (num, dim), generator=gen, device=device).float() * 2 - 1)


def run_one_seed_K(seed: int, K: int, N: int, M_total: int, device, batch_probe: int):
    """Build K expert sub-substrates each of dim N/K, store M_total/K key-value pairs per expert
    (M_total total). Measure mean cosine(recall, target) across all M_total items.
    """
    assert N % K == 0, f"N={N} not divisible by K={K}"
    N_k = N // K
    M_per_expert = M_total // K
    gen = torch.Generator(device=device).manual_seed(seed)

    keys = bsc_atoms(M_total, N, gen, device)
    vals = bsc_atoms(M_total, N, gen, device)
    # Gate: hash key to expert via sign-pattern parity over a fixed random projection.
    proj = bsc_atoms(K, N, gen, device)  # K random sign vectors
    # gate score: dot(keys, proj_k) — argmax gives expert assignment
    scores = keys @ proj.t()  # M_total x K
    gates = scores.argmax(dim=1)  # length M_total

    # Re-balance: trim each expert's items to exactly M_per_expert (drop overflow, pad UNUSED).
    by_expert: list = [[] for _ in range(K)]
    for i, g in enumerate(gates.tolist()):
        if len(by_expert[g]) < M_per_expert:
            by_expert[g].append(i)
    # Items not assigned (overflow) are NOT stored.
    stored_idx = [i for sublist in by_expert for i in sublist]
    M_actually_stored = len(stored_idx)

    # Build expert sub-substrate matrices W_k of shape (N_k, N_k) using Hebbian outer-product.
    Ws = [torch.zeros((N_k, N_k), dtype=torch.float32, device=device) for _ in range(K)]
    # Each expert sees per-expert-dimensional projections of keys and values.
    # Simplest mapping: take the first N_k slice of the global key/val (after permutation seeded per K).
    # We use a stable per-K random permutation so K=2 vs K=16 see different slices but the same global keys.
    perm = torch.randperm(N, generator=gen, device=device)
    keys_perm = keys[:, perm]
    vals_perm = vals[:, perm]
    for k in range(K):
        slice_lo = k * N_k
        slice_hi = (k + 1) * N_k
        for i in by_expert[k]:
            v = vals_perm[i, slice_lo:slice_hi].unsqueeze(0)  # 1 x N_k
            kk = keys_perm[i, slice_lo:slice_hi].unsqueeze(0)  # 1 x N_k
            Ws[k] = Ws[k] + kk.t() @ v  # rank-1 outer-product
        # Sign-normalize column-wise to mimic standard BSC readout.
        Ws[k] = Ws[k] / max(M_per_expert, 1)

    # Recall: for each stored item, route to its expert, read out, measure cosine.
    cos_vals = []
    for k in range(K):
        if not by_expert[k]:
            continue
        idxs = torch.tensor(by_expert[k], device=device)
        K_keys = keys_perm[idxs, k * N_k:(k + 1) * N_k]
        K_vals_target = vals_perm[idxs, k * N_k:(k + 1) * N_k]
        recalled = K_keys @ Ws[k]  # |idxs| x N_k
        # cosine
        num = (recalled * K_vals_target).sum(dim=1)
        den = recalled.norm(dim=1) * K_vals_target.norm(dim=1) + 1e-9
        cos_vals.append((num / den).detach().cpu())
    if cos_vals:
        all_cos = torch.cat(cos_vals)
        mean_cos = float(all_cos.mean().item())
    else:
        mean_cos = 0.0

    # MoE prediction: retention proxy = 1 - (M_per_expert) / N_k_capacity, where
    # N_k_capacity ≈ N_k / 4 (BSC capacity rule-of-thumb).
    M_cap_per_expert = N_k / 4.0
    moe_predicted_retention = max(0.0, 1.0 - M_per_expert / max(M_cap_per_expert, 1.0))

    return {
        "retention": mean_cos,
        "moe_predicted_retention": moe_predicted_retention,
        "M_actually_stored": M_actually_stored,
        "M_per_expert": M_per_expert,
        "N_per_expert": N_k,
    }


def compute_verdict(summary):
    per_K = summary.get("per_K")
    if not per_K:
        return ("MOE_KSWEEP_INCONCLUSIVE", "Missing per_K data.")
    Ks = sorted([int(k) for k in per_K.keys()])
    rets = []
    pred = []
    for k in Ks:
        seeds = per_K[str(k)]
        ret_mean = sum(s["retention"] for s in seeds.values()) / len(seeds)
        pr_mean = sum(s["moe_predicted_retention"] for s in seeds.values()) / len(seeds)
        rets.append(ret_mean)
        pred.append(pr_mean)
    if len(rets) < 2:
        return ("MOE_KSWEEP_INCONCLUSIVE", f"Need >= 2 K-points; got {len(rets)}.")
    monotone = is_monotone_nondecreasing(rets, MONOTONE_TOL)
    lift = rets[-1] - rets[0]
    mean_ret = sum(rets) / len(rets)
    max_dev = max(abs(r - mean_ret) for r in rets)
    # MoE prediction tracking: per-K residual <= PASS_TRACK_TOL
    abs_residuals = [abs(r - p) for r, p in zip(rets, pred)]
    max_residual = max(abs_residuals) if abs_residuals else 1.0

    pts = ", ".join(f"K={k}: ret={r:.3f}, pred={p:.3f}" for k, r, p in zip(Ks, rets, pred))

    if (monotone and lift >= PASS_LIFT and max_residual <= PASS_TRACK_TOL):
        return ("MOE_KSWEEP_HARD_PASS_IMPLICIT_EXPERT",
                f"Implicit-expert allocation SUPPORTED: monotone-non-decreasing in K, lift={lift:.3f} "
                f">= {PASS_LIFT}, max_residual_vs_MoE_pred={max_residual:.3f} <= {PASS_TRACK_TOL}. {pts}.")
    if lift < FAIL_FLAT_LIFT and max_dev <= FAIL_MAX_DEV:
        return ("MOE_KSWEEP_HARD_FAIL_REJECTED",
                f"MoE-on-substrate REJECTED: retention flat in K — lift={lift:.3f} < {FAIL_FLAT_LIFT}, "
                f"max_dev={max_dev:.3f} <= {FAIL_MAX_DEV}. {pts}.")
    return ("MOE_KSWEEP_MIDDLE_BAND",
            f"Intermediate: monotone={monotone}, lift={lift:.3f}, max_dev={max_dev:.3f}, "
            f"max_residual_vs_MoE_pred={max_residual:.3f}. {pts}.")


def self_test_verdict():
    def mk(k_to_ret, k_to_pred):
        return {"per_K": {str(k): {"17": {"retention": r, "moe_predicted_retention": k_to_pred[k]}}
                          for k, r in k_to_ret.items()}}
    s_pass = mk({2: 0.55, 4: 0.65, 8: 0.74, 16: 0.80}, {2: 0.50, 4: 0.62, 8: 0.75, 16: 0.85})
    s_fail = mk({2: 0.72, 4: 0.73, 8: 0.72, 16: 0.71}, {2: 0.50, 4: 0.62, 8: 0.75, 16: 0.85})
    s_mid = mk({2: 0.50, 4: 0.55, 8: 0.62, 16: 0.66}, {2: 0.50, 4: 0.62, 8: 0.75, 16: 0.85})
    s_inconc = {}
    cases = [
        (s_pass, "MOE_KSWEEP_HARD_PASS_IMPLICIT_EXPERT"),
        (s_fail, "MOE_KSWEEP_HARD_FAIL_REJECTED"),
        (s_mid, "MOE_KSWEEP_MIDDLE_BAND"),
        (s_inconc, "MOE_KSWEEP_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp} for case; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    Ks = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    N = N_SMOKE if smoke else N_FULL
    M_total = M_TOTAL_SMOKE if smoke else M_TOTAL_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_probe = BATCH_PROBE_SMOKE if smoke else BATCH_PROBE_FULL
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N,
        "M_total": M_total,
        "K_sweep": Ks,
        "seeds": seeds,
        "batch_probe": batch_probe,
        "device": str(device),
        "pass_lift": PASS_LIFT,
        "pass_track_tol": PASS_TRACK_TOL,
        "monotone_tol": MONOTONE_TOL,
        "fail_flat_lift": FAIL_FLAT_LIFT,
        "fail_max_dev": FAIL_MAX_DEV,
    }
    print(f"[config] {config}", flush=True)
    per_K = {}
    for K in Ks:
        print(f"[K={K}] ...", flush=True)
        per_seed = {}
        for seed in seeds:
            r = run_one_seed_K(seed, K, N, M_total, device, batch_probe)
            per_seed[str(seed)] = r
            print(f"  K={K} seed={seed}: retention={r['retention']:.3f} pred={r['moe_predicted_retention']:.3f}", flush=True)
        per_K[str(K)] = per_seed
    summary = {"per_K": per_K}
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
    out_dir = get_output_dir("wave14_rprime2_moe_K_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_rprime2_moe_K_sweep_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
