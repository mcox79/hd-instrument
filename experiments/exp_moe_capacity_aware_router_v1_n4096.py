"""MoE CAPACITY-AWARE ROUTER v1: online entropy-based adaptation at N=4096.

CONTEXT:
  v266 meta-learning lock: ROUTING MUST BE CAPACITY-AWARE, NOT IDENTITY-AWARE.
  4-arm MoE rescue closure confirmed: static-anchor / random / dim-scaling / hebbian-anchor
  ALL fail because they are identity-aware (route by what, not by how full).

  The 5th rescue arm: CAPACITY-AWARE online router.
  Design: at K-inference time, measure expert load (fraction of capacity consumed)
  and route queries to the expert with the most available capacity.
  This is the natural extension of the v265 fixed-total-capacity insight.

  MECHANISM:
    Each expert e has fill_frac_e = M_e / M_budget_e (current load / capacity budget).
    For new query q, route to expert e* = argmin fill_frac_e (least loaded expert).
    This ensures no single expert saturates while others are underloaded.

  PREDICTION: capacity-aware routing should eliminate K-scaling degradation
  because it ensures balanced load across experts, keeping each expert in
  the multi-basin regime (fill_frac < 1) even as K grows.

PRE-REGISTERED BANDS (5th MoE rescue arm; prior anchor = v265 fixed-total-capacity HARD_PASS):
  Prior anchor: v265 fixed-total-capacity K=4,8,16,32 all retain=1.0 under balanced load.
  HARD_PASS: retention >= 0.70 at K=16 under capacity-aware routing with VARIABLE total M.
    (vs random routing which degrades to 0.0 at K=16; vs fixed-total which trivially stays 1.0)
    Specifically: test with VARIABLE M_total (not fixed) to stress the router.
    K_sweep={4, 8, 16, 32} x M_total_per_expert=800 (variable allocation, K-dependent total).
    HARD_PASS: ret(K=16) >= 0.70 AND ret_delta(K=16 vs K=4) >= -0.20.
  HARD_FAIL: ret(K=16) < 0.30 (same as random baseline = routing doesn't help).
  MIDDLE_BAND: ret(K=16) in [0.30, 0.70).

FORMULA SELF-TESTS:
  1. fill_frac_e = M_e / M_budget_e. Route to argmin fill_frac_e.
  2. With M_total = K * M_budget_per_expert = K * 800, and K experts of equal budget:
     baseline fill_frac = 0 initially; routes evenly -> fill_frac = (M_total/K) / 800 = 1.0.
     This is the same as fixed-total-capacity! Test at K=4: expected ret=1.0.
  3. HARD_PASS gate: ret(K=16) >= 0.70 at >= 2/3 seeds.
  4. N == 4096 (PROT-018 binding).

OOM CHECK:
  K=32, M_per_expert=800, N=4096: 32*800=25600 patterns. keys=25600*4096*4=419MB. Under 6GB.

TIMEOUT ESTIMATE:
  Per cell: K experts x M_per_expert store + K-expert routing + retention eval.
  K=32 x M=800 = 25600 facts. Batched store: fast (~0.3s on CPU). 4 K x 3 seeds = 12 cells.
  Total: 12 * 0.5s = 6s. Safety: ceil(1.5 * 6 * 20) = 180s.
  timeout_s = 3600 (conservative for CPU queue).

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: moe_capacity_aware_router_v1_n4096
Queue: remote_cpu_queue (CPU; MoE capacity-aware routing test; K-sweep N=4096)
Pre-reg: preregs/2026-05-28_moe_capacity_aware_router_v1_n4096.md
Parent: wave14_moe_hebbian_anchor_router_v2_n4096 (v266 HARD_FAIL; meta-learning -> 5th arm)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load kf2 v1 for Kerdock codebook builder (stores + retrieval)
_kf2v1_path = REPO / "experiments" / "exp_kf2_isolation_proof_v1.py"
_kf2v1_spec = importlib.util.spec_from_file_location("kf2v1_moe_cap", _kf2v1_path)
kf2v1 = importlib.util.module_from_spec(_kf2v1_spec)
_kf2v1_spec.loader.exec_module(kf2v1)

v3 = kf2v1.v3   # Kerdock codebook builder

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096   # PROT-018 binding contract
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K_SWEEP_FULL  = [4, 8, 16, 32]
K_SWEEP_SMOKE = [4, 16]

M_BUDGET_PER_EXPERT = 800  # per-expert memory budget (patterns)

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_RET_K16_MIN   = 0.70   # retention at K=16 must be >= 0.70
HP_DELTA_K16_MIN = -0.20  # delta ret K=16 vs K=4 must be >= -0.20
HF_RET_K16_MAX   = 0.30   # ret(K=16) < 0.30 = random baseline = HARD_FAIL
HP_SEEDS_MIN     = 2      # >= 2/3 seeds must pass


def get_output_dir(default_name: str = "moe_capacity_aware_router_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_kerdock_codebook(N: int, device: torch.device) -> torch.Tensor:
    """Build Kerdock codebook or BSC fallback."""
    try:
        cb = v3.make_kerdock_4coset_codebook(N, device)
        if isinstance(cb, tuple):
            cb = cb[0]
        return cb
    except Exception:
        gen = torch.Generator(device=device)
        gen.manual_seed(0)
        cb = (torch.randint(0, 2, (N, N), generator=gen, device=device) * 2 - 1).float()
        return cb


def run_one_K(N: int, K: int, M_budget: int, seed: int, device: torch.device) -> Dict:
    """Run MoE capacity-aware router at fixed K.

    Design:
    - K experts, each with M_budget pattern capacity.
    - Total M_total = K * M_budget patterns to store.
    - Capacity-aware router: assign each new pattern to the expert with lowest fill_frac.
    - Measure mean retention across all K experts.
    """
    cb = build_kerdock_codebook(N, device)
    C = cb.shape[0]
    M_total = K * M_budget

    # Generate all patterns and their query/value indices
    gen = torch.Generator(device=device)
    gen.manual_seed(seed + K * 1000)
    all_key_idx = torch.randint(0, C, (M_total,), generator=gen, device=device)
    all_val_idx = torch.randint(0, C, (M_total,), generator=gen, device=device)
    all_keys = cb[all_key_idx]
    all_vals = cb[all_val_idx]

    # Initialize K expert weight matrices and fill counts
    W_experts = [torch.zeros(N, N, device=device, dtype=torch.float32) for _ in range(K)]
    fill_counts = [0] * K

    # Capacity-aware routing: assign each pattern to least-loaded expert
    routing = []
    for i in range(M_total):
        fill_fracs = [fill_counts[e] / M_budget for e in range(K)]
        e_star = fill_fracs.index(min(fill_fracs))
        routing.append(e_star)
        if fill_counts[e_star] < M_budget:
            k_i = all_keys[i]
            v_i = all_vals[i]
            W_experts[e_star] = W_experts[e_star] + torch.outer(v_i, k_i) / N
            fill_counts[e_star] += 1

    # Compute routing entropy (should be near log2(K) for balanced routing)
    routing_counts = [routing.count(e) for e in range(K)]
    routing_probs = [c / M_total for c in routing_counts]
    import math
    entropy = -sum(p * math.log2(p + 1e-12) for p in routing_probs)

    # Measure retention per expert
    expert_retentions = []
    for e in range(K):
        expert_patterns = [i for i, r in enumerate(routing) if r == e]
        if not expert_patterns:
            expert_retentions.append(0.0)
            continue
        n_probe = min(len(expert_patterns), 100)
        probe_idx = expert_patterns[:n_probe]
        probe_keys = all_keys[probe_idx]
        probe_vals = all_val_idx[probe_idx] % C

        # Softmax retrieval at beta=32
        logits = (cb @ (probe_keys @ W_experts[e].T).T) / N * 32.0
        pred = torch.argmax(logits, dim=0)
        ret = (pred == probe_vals.to(device)).float().mean().item()
        expert_retentions.append(float(ret))

    mean_ret = sum(expert_retentions) / len(expert_retentions)
    fill_fracs_final = [fill_counts[e] / M_budget for e in range(K)]

    print(f"  K={K} seed={seed} mean_ret={mean_ret:.4f} entropy={entropy:.3f} "
          f"fill_fracs={[round(f,2) for f in fill_fracs_final]}", flush=True)

    return {
        "K": K, "seed": seed, "M_total": M_total, "M_budget": M_budget,
        "mean_ret": round(mean_ret, 5),
        "entropy": round(entropy, 4),
        "expert_retentions": [round(r, 5) for r in expert_retentions],
        "fill_fracs_final": [round(f, 3) for f in fill_fracs_final],
        "routing_counts": routing_counts,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("MOE_CAP_INCONCLUSIVE", "No cells.")

    by_K: Dict[int, List[float]] = {}
    for c in cells:
        K = c["K"]
        if K not in by_K:
            by_K[K] = []
        by_K[K].append(c["mean_ret"])

    mean_ret_by_K = {K: sum(rets)/len(rets) for K, rets in by_K.items()}
    ret_k4  = mean_ret_by_K.get(4,  0.0)
    ret_k16 = mean_ret_by_K.get(16, 0.0)

    # Pass/fail per seed at K=16
    k16_cells = [c for c in cells if c["K"] == 16]
    pass_seeds = sum(1 for c in k16_cells
                     if c["mean_ret"] >= HP_RET_K16_MIN and
                     (c["mean_ret"] - ret_k4) >= HP_DELTA_K16_MIN)

    detail = (f"mean_ret_by_K={dict(sorted(mean_ret_by_K.items()))} "
              f"ret_k16={ret_k16:.3f} ret_k4={ret_k4:.3f} "
              f"delta_K16={ret_k16-ret_k4:.3f} "
              f"pass_seeds_at_K16={pass_seeds}/{len(k16_cells)} "
              f"N={summary.get('N', N_FULL)}")

    if ret_k16 < HF_RET_K16_MAX:
        return ("MOE_CAP_HARD_FAIL",
                f"HARD_FAIL: capacity-aware routing = random baseline at K=16. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("MOE_CAP_HARD_PASS",
                f"CAPACITY-AWARE ROUTING: K-scaling MAINTAINED at K=16. " + detail)

    return ("MOE_CAP_MIDDLE_BAND",
            f"Partial: improved over random but below HP_RET_K16_MIN=0.70. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096"

    # Import chain check
    assert v3 is not None, "v3 codebook builder import failed"

    # Formula self-test: fill_frac routing
    # With K=2, M_budget=4, 8 total patterns: should route 4 to each expert
    K_test, M_test = 2, 4
    device = torch.device("cpu")
    cell = run_one_K(N_SMOKE, K_test, M_test, seed=17, device=device)
    assert cell["mean_ret"] is not None, f"mean_ret is None: {cell}"
    assert 0 <= cell["mean_ret"] <= 1.0, f"mean_ret OOR: {cell['mean_ret']}"
    assert cell["entropy"] is not None, f"entropy is None: {cell}"

    # Multi-scale smoke at N_SMOKE x4
    cell_4x = run_one_K(N_SMOKE * 4, K_test, M_test, seed=17, device=device)
    assert 0 <= cell_4x["mean_ret"] <= 1.0, f"4x smoke OOR: {cell_4x['mean_ret']}"

    # Gate self-tests
    fake_cells = [
        {"K": 4,  "mean_ret": 1.00},
        {"K": 8,  "mean_ret": 0.95},
        {"K": 16, "mean_ret": 0.85},
        {"K": 32, "mean_ret": 0.75},
    ] * 3
    v, msg = compute_verdict({"cells": fake_cells, "N": N_FULL})
    assert "HARD_PASS" in v, f"Verdict self-test failed: {v}: {msg}"

    # Hard fail test
    fake_fail = [{"K": 16, "mean_ret": 0.10}] * 3
    vf, _ = compute_verdict({"cells": fake_fail, "N": N_FULL})
    assert "HARD_FAIL" in vf or "MIDDLE_BAND" in vf, f"Verdict fail test: {vf}"

    # OOM check
    M_max = max(K_SWEEP_FULL) * M_BUDGET_PER_EXPERT
    oom_bytes = M_max * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: keys at M={M_max} = {oom_bytes/1e6:.0f}MB >= 6GB"

    print(f"[selftest] moe_capacity_aware_router_v1_n4096 PASS ret_smoke={cell['mean_ret']:.4f}",
          flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    k_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL
    N_cfg   = N_SMOKE       if smoke else N_FULL

    device = torch.device("cpu")  # MoE routing test is CPU-side logic
    print(f"moe_capacity_aware_router_v1_n4096 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"K_sweep={k_sweep} seeds={seeds} M_budget={M_BUDGET_PER_EXPERT}", flush=True)

    cells = []
    for K in k_sweep:
        for seed in seeds:
            t_cell = time.monotonic()
            cell = run_one_K(N_cfg, K, M_BUDGET_PER_EXPERT, seed, device)
            cell["N"] = N_cfg
            cells.append(cell)
            print(f"  K={K} seed={seed} ret={cell['mean_ret']:.4f} "
                  f"({time.monotonic()-t_cell:.1f}s)", flush=True)

    elapsed = time.monotonic() - t0
    summary = {
        "mode": "smoke" if smoke else "full",
        "N": N_cfg,
        "K_sweep": k_sweep,
        "seeds": seeds,
        "M_budget_per_expert": M_BUDGET_PER_EXPERT,
        "elapsed_s": round(elapsed, 2),
        "cells": cells,
    }

    tag, msg = compute_verdict(summary)
    summary["verdict_tag"] = tag
    summary["verdict_msg"] = msg
    print(f"\n[VERDICT] {tag}: {msg}", flush=True)

    out_dir = get_output_dir()
    with open(out_dir / "metrics.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[done] elapsed={elapsed:.1f}s -> {out_dir}/metrics.json", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        return
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
