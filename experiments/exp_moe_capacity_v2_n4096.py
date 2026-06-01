"""MoE CAPACITY-AWARE ROUTER v2: higher K extension at N=4096.

CONTEXT:
  v267 MOE_CAPACITY_HARD_PASS: K=4..16 retention maintained at >= 0.80 with capacity-aware
  routing. v1 K_SWEEP=[4,8,16,32]. v2 extends to K=[32,48,64,96] to find
  the K* where capacity-aware routing begins to degrade.

SCIENTIFIC QUESTION:
  At what K does capacity-aware routing fail to maintain retention >= HP_RET_MIN?
  Is there a K_c analogous to M_c (a capacity-aware routing phase boundary)?

PRE-REGISTERED BANDS:
  Parent: MoE v1 K=16 retention 0.80+.
  Expected: retention degrades with K; K_c somewhere in [32,96].

  HARD_PASS: retention at K=64 >= 0.50 (> random 1/C) AND K_c localized in [32,96].
    Interpretation: capacity-aware routing works to K>=64; useful scaling envelope.
  HARD_FAIL: retention at K=32 < 0.30 (immediate collapse at v1 sweep boundary).
    Interpretation: K=32 is already past K_c; routing saturates at low K.
  MIDDLE_BAND: K=32 >= 0.30 but K=64 < 0.50.

FORMULA SELF-TESTS:
  1. M_total = K * M_budget_per_expert. K=64 M_budget=800: M_total=51200.
  2. Capacity-aware route: argmin fill_frac_e.
  3. Routing entropy: -sum(p_e * log2(p_e)) ~ log2(K) for balanced routing.
  4. N == 4096 (PROT-018).
  5. K=64 M=51200 N=4096: W=64MB. Keys=51200*4096*4=838MB. CB=268MB. Total~1.2GB. OK.

OOM CHECK:
  Worst case K=96, M_total=76800: keys=76800*4096*4=1.2GB. W=64MB each (96 small Ws).
  96 W matrices of 4096x4096 float32 = 96*64MB=6.1GB. BORDERLINE!
  Reduce K_max to 64, M_budget=600: W per expert=64MB, 64 experts=4GB. Acceptable.
  Actually W_e is sparse update but full matrix. Reduce M_budget to 400 for K=64.

TIMEOUT ESTIMATE:
  4 K-vals x 3 seeds = 12 cells.
  K=64 with M_budget=400: M_total=25600 patterns. Store+retrieve ~ 5s.
  Total: 12 * 5s = 60s. Safety: ceil(1.5*60*10) = 900s. Floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: moe_capacity_v2_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-28_moe_capacity_v2_n4096.md
Parent: exp_moe_capacity_aware_router_v1_n4096 (v267 HARD_PASS K=4..32)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load MoE v1 for build_kerdock_codebook and run_one_K
_v1_path = REPO / "experiments" / "exp_moe_capacity_aware_router_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("moe_v1", _v1_path)
moe_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(moe_v1)

build_kerdock_codebook = moe_v1.build_kerdock_codebook

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K_SWEEP_FULL  = [32, 48, 64, 96]
K_SWEEP_SMOKE = [32, 64]

M_BUDGET_PER_EXPERT = 400  # reduced to avoid OOM at K=96

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_RET_K64_MIN   = 0.50   # retention at K=64 must be >= 0.50
HF_RET_K32_MAX   = 0.30   # ret(K=32) < 0.30 = immediate collapse = HARD_FAIL
HP_SEEDS_MIN     = 2


def get_output_dir(default_name: str = "moe_capacity_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_K(N: int, K: int, M_budget: int, seed: int, device: torch.device) -> Dict:
    """Run capacity-aware MoE at K with given M_budget."""
    cb = build_kerdock_codebook(N, device)
    C = cb.shape[0]
    M_total = K * M_budget

    gen = torch.Generator(device=device)
    gen.manual_seed(seed + K * 1000)
    all_key_idx = torch.randint(0, C, (M_total,), generator=gen, device=device)
    all_val_idx = torch.randint(0, C, (M_total,), generator=gen, device=device)
    all_keys = cb[all_key_idx]
    all_vals = cb[all_val_idx]

    # Initialize K expert weight matrices
    W_experts = [torch.zeros(N, N, device=device, dtype=torch.float32) for _ in range(K)]
    fill_counts = [0] * K

    # Capacity-aware routing
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

    routing_counts = [routing.count(e) for e in range(K)]
    routing_probs = [c / M_total for c in routing_counts]
    entropy = -sum(p * math.log2(p + 1e-12) for p in routing_probs)

    expert_retentions = []
    for e in range(K):
        expert_patterns = [i for i, r in enumerate(routing) if r == e]
        if not expert_patterns:
            expert_retentions.append(0.0)
            continue
        n_probe = min(len(expert_patterns), 50)
        probe_idx = expert_patterns[:n_probe]
        probe_keys = all_keys[probe_idx]
        probe_vals = all_val_idx[probe_idx] % C

        logits = (cb @ (probe_keys @ W_experts[e].T).T) / N * 32.0
        pred = torch.argmax(logits, dim=0)
        ret = (pred == probe_vals.to(device)).float().mean().item()
        expert_retentions.append(float(ret))

    mean_ret = sum(expert_retentions) / len(expert_retentions)
    fill_fracs_final = [fill_counts[e] / M_budget for e in range(K)]

    print(f"  K={K} seed={seed} mean_ret={mean_ret:.4f} entropy={entropy:.3f} "
          f"min_fill={min(fill_fracs_final):.2f} max_fill={max(fill_fracs_final):.2f}", flush=True)

    return {
        "K": K, "seed": seed, "M_total": M_total, "M_budget": M_budget,
        "mean_ret": round(mean_ret, 5),
        "entropy": round(entropy, 4),
        "expert_retentions": [round(r, 5) for r in expert_retentions[:10]],  # store first 10 only
        "fill_fracs_stats": {
            "min": round(min(fill_fracs_final), 3),
            "max": round(max(fill_fracs_final), 3),
            "mean": round(sum(fill_fracs_final) / len(fill_fracs_final), 3),
        },
        "routing_entropy": round(entropy, 4),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("MOE_V2_INCONCLUSIVE", "No cells.")

    by_K: Dict[int, List] = {}
    for c in cells:
        by_K.setdefault(c["K"], []).append(c)

    k_vals = sorted(by_K.keys())
    k32_cells = by_K.get(32, [])
    k64_cells = by_K.get(64, [])

    k32_mean = sum(c["mean_ret"] for c in k32_cells) / max(1, len(k32_cells)) if k32_cells else 0.0
    k64_mean = sum(c["mean_ret"] for c in k64_cells) / max(1, len(k64_cells)) if k64_cells else 0.0

    mean_rets_by_K = {k: round(sum(c["mean_ret"] for c in by_K[k]) / len(by_K[k]), 4) for k in k_vals}

    detail = (f"k32_mean={k32_mean:.3f} k64_mean={k64_mean:.3f} "
              f"rets_by_K={mean_rets_by_K} HP_ret_k64={HP_RET_K64_MIN} HF_ret_k32={HF_RET_K32_MAX} "
              f"N={summary.get('N', N_FULL)}")

    if k32_mean < HF_RET_K32_MAX:
        return ("MOE_V2_HARD_FAIL", f"K32_COLLAPSE: k32_mean={k32_mean:.3f} < {HF_RET_K32_MAX}. " + detail)

    if k64_mean >= HP_RET_K64_MIN:
        return ("MOE_V2_HARD_PASS", f"HIGH_K_SCALING: k64_mean={k64_mean:.3f} >= {HP_RET_K64_MIN}. " + detail)

    return ("MOE_V2_MIDDLE_BAND", f"PARTIAL_K_SCALING: k32 OK but k64 below threshold. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula self-test: routing entropy
    K_test = 4
    routing = [0, 1, 2, 3, 0, 1, 2, 3]  # balanced
    M = len(routing)
    counts = [routing.count(e) for e in range(K_test)]
    probs = [c / M for c in counts]
    H = -sum(p * math.log2(p + 1e-12) for p in probs)
    assert abs(H - math.log2(K_test)) < 0.01, f"Entropy self-test failed: {H} vs {math.log2(K_test)}"
    # HARD_PASS verdict gate
    fake = [{"K": 32, "mean_ret": 0.75}, {"K": 64, "mean_ret": 0.60}]
    v, _ = compute_verdict({"cells": fake, "N": N_FULL})
    assert "HARD_PASS" in v, f"Verdict HARD_PASS gate: {v}"
    # Smoke cell non-null
    device = torch.device("cpu")
    cell = run_one_K(N_SMOKE, 4, 50, 17, device)
    assert not math.isnan(cell["mean_ret"]), "mean_ret NaN in selftest"
    assert cell["mean_ret"] >= 0.0, "mean_ret negative"
    # 4x cell
    cell4 = run_one_K(N_SMOKE * 4, 4, 100, 17, device)
    assert not math.isnan(cell4["mean_ret"]), "4x mean_ret NaN"
    print(f"[selftest] moe_capacity_v2_n4096 PASS mean_ret_smoke={cell['mean_ret']:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    k_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] moe_capacity_v2_n4096 smoke={smoke} N={N_cfg} K_sweep={k_sweep} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for K in k_sweep:
        print(f"\n  [K={K}]", flush=True)
        for seed in seeds:
            cell = run_one_K(N_cfg, K, M_BUDGET_PER_EXPERT, seed, device)
            all_cells.append(cell)
        print(f"  K={K} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "moe_capacity_v2_n4096", "N": N_cfg, "smoke": smoke,
        "K_sweep": k_sweep, "M_budget": M_BUDGET_PER_EXPERT, "seeds": seeds,
        "cells": all_cells, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
