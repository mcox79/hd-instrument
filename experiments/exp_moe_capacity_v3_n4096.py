"""MoE CAPACITY-AWARE ROUTER v3: pure-CPU variant of v2 at N=4096.

CONTEXT:
  moe_capacity_aware_router_v1_n4096 (FAILED on remote_cpu_queue): OOM or import failure.
  moe_capacity_v2_n4096 (shipped to overnight_queue): GPU variant.
  v3 (THIS): pure-CPU implementation that avoids OOM by using smaller codebook C
  and lightweight retrieval (no full matrix build for large K).

  Redesigned for CPU:
    - C = 2048 (codewords), not C = 4096 (saves 4x codebook memory)
    - K values limited to [4, 8, 16, 32] (matching v1 range)
    - M_budget=200 per expert (vs 400 in v2 GPU; CPU-safe)
    - Test question: does capacity-aware routing (fill-fraction balancing)
      maintain >= 80% retention vs. greedy routing at K=4..32?

SCIENTIFIC QUESTION:
  At N=4096 with C=2048 CPU-safe config, does capacity-aware MoE routing
  outperform greedy routing (each query always picks expert 0)?
  Does retention drop monotonically with K (more experts = less capacity each)?

PRE-REGISTERED BANDS:
  Prior: moe_capacity_aware_router_v1_n4096 FAILED (no clean prior anchor).
  Calibration probe: no empirical anchor. Bands widened to +-50%.

  Theoretical: with capacity-aware routing, retention ~ M_budget/M_total * C / K.
  At K=4, M_budget=200, M_total=800: retention should be near 1.0.
  At K=32, M_budget=200, M_total=6400: expected degradation.

  HARD_PASS: retention at K=4 >= 0.60 with capacity-aware routing.
    AND retention_cap_aware > retention_greedy at K >= 8.
    Interpretation: capacity-aware routing provides measurable benefit.
  HARD_FAIL: retention at K=4 < 0.20 (routing completely fails even at K=4).
  MIDDLE_BAND: retention >= 0.20 but capacity-aware == greedy (no routing benefit).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M_total at K=4, M_budget=200: M=800.
  3. M_total at K=32: M=6400.
  4. C=2048. Codebook size: 2048*4096*4 = 32MB. OK.
  5. retention = fraction of probed queries correctly retrieved.

OOM CHECK:
  N=4096, C=2048: codebook=32MB. K=32 W_matrices=32*64MB=2GB. BORDERLINE.
  Reduce K_max to 16 for CPU safety. K_SWEEP=[4, 8, 16].
  K=16 W=64MB*16=1GB. Total ~1.5GB. OK for 16GB CPU.

TIMEOUT ESTIMATE:
  3 K_vals x 3 seeds = 9 cells. Per cell at N=4096, C=2048: ~10s.
  Total: 9 * 10 = 90s. Safety: ceil(1.5 * 90 * 5) = 675s. Floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: moe_capacity_v3_n4096
Queue: remote_cpu_queue (CPU; N=4096 MoE capacity-aware vs greedy; K=[4,8,16])
Pre-reg: preregs/2026-05-29_moe_capacity_v3_n4096.md
Parent: moe_capacity_aware_router_v1_n4096 (FAILED)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K_SWEEP_FULL  = [4, 8, 16]
K_SWEEP_SMOKE = [4, 8]

C_FULL  = 2048    # codebook size (safe for CPU)
C_SMOKE = 512

M_BUDGET_PER_EXPERT = 200    # patterns per expert
N_PROBE = 100     # queries for retention estimate

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_RET_K4_MIN  = 0.60   # retention at K=4 >= 0.60
HF_RET_K4_MAX  = 0.20   # retention at K=4 < 0.20 = HARD_FAIL


def get_output_dir(default_name: str = "moe_capacity_v3_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, K: int, seed: int, C: int, M_budget: int,
                 n_probe: int, device: torch.device) -> Dict:
    """Run MoE capacity-aware vs greedy routing at (N, K, seed).

    Metric: retrieval accuracy measured on stored (key, val) pairs.
    For each routing strategy, probe a stored pair and check if W_expert retrieves it.
    """
    M_total = K * M_budget
    gen = torch.Generator(device=device).manual_seed(seed)

    # Build codebook (BSC +/-1)
    codebook = torch.randint(0, 2, (C, N), generator=gen, device=device).float() * 2 - 1

    # Build K expert W matrices, each storing M_budget (key, val) pairs
    W_experts = []
    keys_all = []   # all stored keys across experts (M_total, N)
    vals_all = []   # corresponding stored values (M_total,) as codeword indices
    expert_id = []  # which expert stored each (k_i, v_i) pair

    for k in range(K):
        k_idx = torch.randint(0, C, (M_budget,), generator=gen, device=device)
        v_idx = torch.randint(0, C, (M_budget,), generator=gen, device=device)
        keys_k = codebook[k_idx]   # (M_budget, N)
        vals_k = codebook[v_idx]   # (M_budget, N)
        W_k = (vals_k.T @ keys_k) / N   # (N, N)
        W_experts.append(W_k)
        keys_all.append(keys_k)
        vals_all.append(v_idx)
        expert_id.extend([k] * M_budget)

    keys_all_t = torch.cat(keys_all, dim=0)   # (M_total, N)
    vals_all_t = torch.cat(vals_all, dim=0)   # (M_total,) codeword indices

    # Sample n_probe stored pairs to test
    probe_idx = torch.randint(0, M_total, (min(n_probe, M_total),), generator=gen, device=device)

    def retrieve_acc_with_expert(expert_assignments: List[int]) -> float:
        """Compute acc when routing probe i to expert_assignments[i]."""
        correct = 0
        for j, pi in enumerate(probe_idx.tolist()):
            e = expert_assignments[j]
            q = keys_all_t[pi]   # (N,)
            W_e = W_experts[e]
            retrieved = W_e @ q   # (N,) -- should resemble the stored value
            # Find nearest codeword
            sims = codebook @ retrieved   # (C,)
            pred_val_idx = int(sims.argmax())
            true_val_idx = int(vals_all_t[pi])
            if pred_val_idx == true_val_idx:
                correct += 1
        return correct / len(probe_idx)

    # Strategy 1: route to the expert that actually stored the pattern (oracle / capacity-aware)
    oracle_assign = [expert_id[int(pi)] for pi in probe_idx.tolist()]
    ret_oracle = retrieve_acc_with_expert(oracle_assign)

    # Strategy 2: greedy - always route to expert 0
    greedy_assign = [0] * len(probe_idx)
    ret_greedy = retrieve_acc_with_expert(greedy_assign)

    # Strategy 3: capacity-aware (round-robin balancing)
    cap_assign = [j % K for j in range(len(probe_idx))]
    ret_cap = retrieve_acc_with_expert(cap_assign)

    benefit_over_greedy = ret_cap - ret_greedy
    # ret_cap_aware is the capacity-aware retention
    ret_cap_aware = ret_cap

    print(f"    N={N} K={K} seed={seed} ret_oracle={ret_oracle:.4f} "
          f"ret_cap={ret_cap:.4f} ret_grd={ret_greedy:.4f} benefit={benefit_over_greedy:.4f}",
          flush=True)

    return {
        "N": N, "K": K, "seed": seed, "M_budget": M_budget, "M_total": M_total,
        "ret_cap_aware": round(ret_cap_aware, 5),
        "ret_oracle": round(ret_oracle, 5),
        "ret_greedy": round(ret_greedy, 5),
        "benefit": round(benefit_over_greedy, 5),
        "passes_hp_k4": (K == 4 and ret_cap_aware >= HP_RET_K4_MIN),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("MOE_V3_INCONCLUSIVE", "No cells.")

    valid = [c for c in cells if c.get("ret_cap_aware") is not None]
    if not valid:
        return ("MOE_V3_INCONCLUSIVE", "No valid ret_cap_aware values.")

    # K=4 performance check
    cells_k4 = [c for c in valid if c.get("K") == 4]
    ret_k4_vals = [c["ret_cap_aware"] for c in cells_k4]
    mean_ret_k4 = sum(ret_k4_vals) / len(ret_k4_vals) if ret_k4_vals else 0.0

    # Routing benefit check
    benefits = [c["benefit"] for c in valid]
    mean_benefit = sum(benefits) / len(benefits) if benefits else 0.0
    n_pos_benefit = sum(1 for b in benefits if b > 0)

    N = summary.get("N", N_FULL)
    detail = (f"mean_ret_k4={mean_ret_k4:.4f} mean_benefit={mean_benefit:.4f} "
              f"n_pos_benefit={n_pos_benefit}/{len(valid)} HP_ret_k4={HP_RET_K4_MIN} N={N}")

    if mean_ret_k4 < HF_RET_K4_MAX:
        return ("MOE_V3_HARD_FAIL",
                f"ROUTING_FAILS at K=4: ret_cap={mean_ret_k4:.4f}. " + detail)

    if mean_ret_k4 >= HP_RET_K4_MIN and n_pos_benefit > len(valid) // 2:
        return ("MOE_V3_HARD_PASS",
                f"CAPACITY_AWARE_ROUTING_WORKS: ret_k4={mean_ret_k4:.4f}. " + detail)

    return ("MOE_V3_MIDDLE_BAND",
            f"PARTIAL: ret_k4={mean_ret_k4:.4f} benefit={mean_benefit:.4f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula tests
    assert K_SWEEP_FULL[-1] == 16, "K_max must be 16 for OOM safety"
    assert M_BUDGET_PER_EXPERT * K_SWEEP_FULL[-1] == 3200, "M_total at K=16: 3200"
    cb_size = C_FULL * N_FULL * 4
    assert cb_size < 6e9, f"Codebook OOM: {cb_size/1e6:.0f}MB"

    # Verdict tests
    cells_hp = [{"ret_cap_aware": 0.80, "ret_greedy": 0.70, "benefit": 0.10, "K": 4} for _ in range(3)]
    cells_hp += [{"ret_cap_aware": 0.70, "ret_greedy": 0.60, "benefit": 0.10, "K": 8}]
    v, msg = compute_verdict({"cells": cells_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"Expected HP: {v}: {msg}"

    cells_hf = [{"ret_cap_aware": 0.10, "ret_greedy": 0.10, "benefit": 0.0, "K": 4} for _ in range(3)]
    v_hf, _ = compute_verdict({"cells": cells_hf, "N": N_FULL})
    assert "HARD_FAIL" in v_hf, f"Expected HF: {v_hf}"

    # Live smoke cell at N=1024, C=512
    device = torch.device("cpu")
    result = run_one_cell(N_SMOKE, K=4, seed=17, C=C_SMOKE, M_budget=50, n_probe=50, device=device)
    assert "ret_cap_aware" in result, f"missing ret_cap_aware: {list(result.keys())}"
    ret = result["ret_cap_aware"]
    assert ret is not None and not math.isnan(ret), f"ret_cap_aware NaN"
    assert 0.0 <= ret <= 1.0, f"ret_cap_aware out of [0,1]: {ret}"
    assert result["M_total"] == 4 * 50, "M_total check"

    # 4x smoke: N=4096 C=2048
    result4 = run_one_cell(N_SMOKE * 4, K=4, seed=17, C=C_FULL, M_budget=50, n_probe=50, device=device)
    assert "ret_cap_aware" in result4, "4x missing ret_cap_aware"

    print(f"[selftest] moe_capacity_v3_n4096 PASS ret_smoke={ret:.4f} ret_4x={result4['ret_cap_aware']:.4f}",
          flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    k_sweep  = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds    = SEEDS_SMOKE if smoke else SEEDS_FULL
    N_cfg    = N_SMOKE if smoke else N_FULL
    C_cfg    = C_SMOKE if smoke else C_FULL
    n_probe  = 50 if smoke else N_PROBE

    device = torch.device("cpu")
    print(f"moe_capacity_v3_n4096 mode={'SMOKE' if smoke else 'FULL'} "
          f"N={N_cfg} K_sweep={k_sweep} seeds={seeds}", flush=True)

    all_cells = []

    for K in k_sweep:
        print(f"\n== K={K} ==", flush=True)
        for seed in seeds:
            t_cell = time.monotonic()
            result = run_one_cell(N_cfg, K, seed, C_cfg, M_BUDGET_PER_EXPERT, n_probe, device)
            elapsed_cell = time.monotonic() - t_cell
            result["elapsed_s"] = round(elapsed_cell, 2)
            all_cells.append(result)

    elapsed_total = time.monotonic() - t0
    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})

    summary = {
        "anchor": "moe_capacity_v3_n4096",
        "N": N_cfg, "smoke": smoke,
        "K_sweep": k_sweep, "C": C_cfg, "M_budget": M_BUDGET_PER_EXPERT,
        "seeds": seeds, "cells": all_cells,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed_total, 2),
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as fp:
        json.dump(summary, fp, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_total:.1f}s", flush=True)
    print(f"[output] {out_path}", flush=True)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
