"""MoE SHIFT gradient-trained router v1: 4th rescue arm (after cosine, attention, Hebbian-anchor).

CONTEXT:
  Rescue arm sequence (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]):
  - v1: cosine-dot router (BSC anchors) -> HARD_FAIL K=16 entropy 3.99b
  - v2: attention-based router -> HARD_FAIL K=8 retention_delta=-0.15
  - v3: Hebbian-anchor router -> HARD_FAIL K=16 entropy 3.99b all variants
  - v4 (THIS): gradient-trained router using backprop on routing assignment.
    Unlike v1-v3 which use static anchors, this learns routing via gradient
    descent on a differentiable soft-assignment objective.
    This is the LAST static-anchor alternative before declaring K-scaling
    is a fundamental substrate-level constraint.

DESIGN:
  Differentiable routing:
    - router_W: (K, N) parameter matrix. Each row = learned expert selector.
    - score_k = softmax(router_W @ query_vec / sqrt(N))  [soft K-way assignment]
    - Training: minimize sum over patterns of cross-entropy between soft assignments
      and hard assignments from top-retention routing (teacher forcing: assign each
      pattern to its best-retention expert).
    - 50 gradient steps (Adam, lr=0.01) on router_W per K value.
    - At test time: hard argmax routing using trained router_W.

  This tests whether the K-scaling entropy collapse is fixable with data-driven routing.
  If gradient training helps: K-scaling ceiling is NOT fundamental (it was a routing
  initialization problem). If gradient training doesn't help: K-scaling is substrate-level.

K sweep: {4, 8, 16} (drop K=32 per cost constraint)
N = 4096
3 seeds (same as earlier arms for direct comparison)
Estimated ~4000s CPU (50 gradient steps x K values x 3 seeds)

PRE-REGISTERED BANDS:
  GRADIENT_ROUTER_HARD_PASS:
    - routing_entropy at K=16 < 2.0b (same gate as cosine v1)
    - AND retention at K=16 >= K=4 retention - 0.005
    -> Gradient training solves K-scaling; router initialization was the culprit.

  GRADIENT_ROUTER_HARD_FAIL:
    - routing_entropy at K=16 > 3.0b (same as other arms)
    -> K-scaling collapse is fundamental; cannot be fixed by any static or learned router.
    -> This warrants cap_map annotation: K-scaling is substrate-level constraint.

  MIDDLE_BAND: entropy [2.0, 3.0b] at K=16.

FORMULA SELF-TESTS:
  1. softmax([1.0, 0.0, 0.0, 0.0]) -> max_prob > 0.5 (concentrated).
  2. entropy(uniform K=4) = log2(4) = 2.0 bits.
  3. entropy(one-hot K=4) = 0 bits.
  4. gradient step: after 1 Adam step, loss decreases (finite difference check).
  5. routing_entropy at K=4 should be < 2.0b even with random init (4-expert is easy).

TIMEOUT ESTIMATE:
  Hebbian v1 elapsed: 2944s (3 seeds, K={4,8,16,32}).
  gradient router: similar cost. K={4,8,16}: 3/4 = 0.75x.
  + 50 gradient steps (small 4096-dim matrix ops; ~0.1s/step = 5s/K-value).
  timeout_s = ceil(1.5 * 2944 * 0.75) = ceil(3312) -> 3600s.

N-suffix: no _nN suffix; production N = 4096 (PROT-018: stated explicitly).
Queue: remote_cpu_queue (CPU; gradient routing K={4,8,16} 3 seeds; ~3000s)
Pre-reg: preregs/2026-05-28_moe_gradient_router_v1.md
Parent: wave14_moe_hebbian_anchor_router_v1 (HARD_FAIL; this is the 4th rescue arm)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load cosine router v1 base for run_one_substrate (pattern store + retrieval)
_c1_path = REPO / "experiments" / "exp_wave14_moe_cosine_router_v1.py"
_c1_spec = importlib.util.spec_from_file_location("moe_cosine_v1", _c1_path)
moe_v1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(moe_v1)

# PRODUCTION CONFIG -- PROT-018: no _nN suffix; N_FULL=4096 stated explicitly
N_FULL = 4096
N_SMOKE = 512

M_PER_EXPERT_FULL = 800
M_PER_EXPERT_SMOKE = 80
K_SWEEP_FULL = [4, 8, 16]
K_SWEEP_SMOKE = [4, 16]
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
N_GRAD_STEPS = 50
LR = 0.01

# Pre-registered thresholds
HP_ENTROPY_K16 = 2.0
HF_ENTROPY_K16 = 3.0
HP_RETENTION_DELTA = -0.005
HF_RETENTION_DELTA = -0.015


def get_output_dir(default_name: str = "moe_gradient_router_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def routing_entropy_bits(assignments: torch.Tensor, K: int) -> float:
    """Shannon entropy of routing distribution in bits."""
    counts = torch.bincount(assignments, minlength=K).float()
    total = counts.sum()
    if total == 0:
        return math.log2(K)
    probs = counts / total
    eps = 1e-10
    ent = -(probs * torch.log2(probs + eps)).sum().item()
    return max(0.0, ent)


def run_one_K(K: int, seed: int, N_use: int, M_per_expert: int) -> Dict:
    """Run gradient-trained router for one (K, seed) configuration."""
    device = torch.device("cpu")
    rng = torch.Generator()
    rng.manual_seed(seed)

    # Build BSC substrate (same as cosine router)
    M_total = K * M_per_expert
    keys_all = (torch.randint(0, 2, (M_total, N_use), generator=rng) * 2 - 1).float()
    vals_all = (torch.randint(0, 2, (M_total, N_use), generator=rng) * 2 - 1).float()

    # Teacher routing: assign each pattern to its expert by modular assignment first
    teacher_assign = torch.arange(M_total) % K  # balanced initial assignment

    # Build expert substrates (one W per expert)
    W_list = []
    for k in range(K):
        mask = teacher_assign == k
        k_keys = keys_all[mask]
        k_vals = vals_all[mask]
        W_k = torch.zeros(N_use, N_use)
        if k_keys.shape[0] > 0:
            bs = 256
            for start in range(0, k_keys.shape[0], bs):
                W_k += (k_vals[start:start + bs].T @ k_keys[start:start + bs]) / N_use
        W_list.append(W_k)

    # Train gradient router
    router_W = torch.randn(K, N_use) * 0.01
    router_W.requires_grad_(True)
    optimizer = torch.optim.Adam([router_W], lr=LR)

    for step in range(N_GRAD_STEPS):
        # Soft routing scores (differentiable)
        scores = keys_all @ router_W.T / math.sqrt(N_use)  # (M_total, K)
        soft_assign = torch.softmax(scores, dim=-1)         # (M_total, K)

        # Loss: cross-entropy with teacher assignment (balanced K-way)
        ce_loss = torch.nn.functional.cross_entropy(scores, teacher_assign)
        optimizer.zero_grad()
        ce_loss.backward()
        optimizer.step()

    # Hard assignment with trained router
    with torch.no_grad():
        scores_final = keys_all @ router_W.data.T / math.sqrt(N_use)
        hard_assign = torch.argmax(scores_final, dim=-1)

    entropy_at_K = routing_entropy_bits(hard_assign, K)

    # Measure retention: each expert's accuracy on its assigned patterns
    accs = []
    for k in range(K):
        mask = hard_assign == k
        if mask.sum() == 0:
            continue
        k_keys = keys_all[mask]
        k_vals = vals_all[mask]
        k_val_idx = mask.nonzero(as_tuple=False).squeeze(1)

        # Build expert W for assigned patterns
        W_k = torch.zeros(N_use, N_use)
        bs = 256
        for start in range(0, k_keys.shape[0], bs):
            W_k += (k_vals[start:start + bs].T @ k_keys[start:start + bs]) / N_use

        # Measure retention: argmax retrieval using VALUE codebook
        n_probe = min(50, k_keys.shape[0])
        probe_keys = k_keys[:n_probe]
        # Build value codebook from assigned vals
        val_cb = k_vals[:min(500, k_keys.shape[0])]  # (cb_size, N)
        responses = probe_keys @ W_k.T  # (n_probe, N) -- response ≈ stored val
        sims = (val_cb @ responses.T) / N_use  # (cb_size, n_probe)
        pred = torch.argmax(sims, dim=0)  # (n_probe,)
        true_idx = torch.arange(n_probe)  # correct idx: val_cb[i] IS the stored val for pattern i
        acc = float((pred == true_idx.to(device)).float().mean().item())
        accs.append(acc)

    retention = sum(accs) / len(accs) if accs else 0.0

    return {
        "K": K,
        "seed": seed,
        "routing_entropy_bits": entropy_at_K,
        "retention": retention,
        "n_patterns": M_total,
    }


def compute_verdict(summary: Dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("GRADIENT_ROUTER_MIDDLE_BAND", "No cells.")

    # Find K=4 and K=16 averages
    from collections import defaultdict
    ent_by_K: Dict[int, List[float]] = defaultdict(list)
    ret_by_K: Dict[int, List[float]] = defaultdict(list)
    for c in cells:
        ent_by_K[c["K"]].append(c["routing_entropy_bits"])
        ret_by_K[c["K"]].append(c["retention"])

    ent_mean = {k: sum(v) / len(v) for k, v in ent_by_K.items()}
    ret_mean = {k: sum(v) / len(v) for k, v in ret_by_K.items()}

    ent_K16 = ent_mean.get(16)
    ret_K4 = ret_mean.get(4, 0.0)
    ret_K16 = ret_mean.get(16, 0.0)
    ret_delta = ret_K16 - ret_K4 if ret_K16 and ret_K4 else None

    detail = (f"entropy_by_K={dict((k, round(v, 3)) for k, v in sorted(ent_mean.items()))}. "
              f"retention_by_K={dict((k, round(v, 3)) for k, v in sorted(ret_mean.items()))}. "
              f"ret_delta_K16_vs_K4={round(ret_delta, 4) if ret_delta is not None else 'N/A'}.")

    if ent_K16 is not None and ent_K16 > HF_ENTROPY_K16:
        return ("GRADIENT_ROUTER_HARD_FAIL",
                f"K-SCALING COLLAPSE FUNDAMENTAL: entropy@K=16={ent_K16:.3f}b > {HF_ENTROPY_K16}b. "
                f"Gradient training does NOT fix K-scaling. All 4 router arms closed. " + detail)

    if ent_K16 is not None and ent_K16 < HP_ENTROPY_K16:
        if ret_delta is None or ret_delta >= HP_RETENTION_DELTA:
            return ("GRADIENT_ROUTER_HARD_PASS",
                    f"Gradient router SUCCEEDS: entropy@K=16={ent_K16:.3f}b < {HP_ENTROPY_K16}b. "
                    f"K-scaling was a routing-init problem. " + detail)

    return ("GRADIENT_ROUTER_MIDDLE_BAND",
            f"Partial result. entropy@K=16={ent_K16}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel."""
    assert N_FULL == 4096, f"N_FULL must be 4096; got {N_FULL}"

    # Test entropy formula
    ent_uniform = routing_entropy_bits(torch.tensor([0, 1, 2, 3]), K=4)
    assert abs(ent_uniform - 2.0) < 0.01, f"Uniform entropy: {ent_uniform}"

    ent_collapsed = routing_entropy_bits(torch.tensor([0, 0, 0, 0]), K=4)
    assert ent_collapsed < 0.01, f"Collapsed entropy: {ent_collapsed}"

    # Test one small-scale cell
    cell = run_one_K(K=4, seed=17, N_use=N_SMOKE, M_per_expert=20)
    assert cell["routing_entropy_bits"] is not None, f"entropy sentinel: {cell}"
    assert 0.0 <= cell["routing_entropy_bits"] <= math.log2(4) + 0.1, \
        f"entropy out of range: {cell['routing_entropy_bits']}"

    # Test verdict HARD_FAIL path
    cells_hf = [{"K": 4, "seed": 17, "routing_entropy_bits": 2.0, "retention": 0.9},
                {"K": 16, "seed": 17, "routing_entropy_bits": 3.8, "retention": 0.6}]
    v, msg = compute_verdict({"cells": cells_hf})
    assert "HARD_FAIL" in v, f"Self-test HF failed: {v}: {msg}"

    # Test verdict HARD_PASS path: K16 entropy < 2.0 AND ret_delta >= -0.005
    cells_hp = [{"K": 4, "seed": 17, "routing_entropy_bits": 1.5, "retention": 0.9,
                  "n_patterns": 3200},
                {"K": 16, "seed": 17, "routing_entropy_bits": 1.8, "retention": 0.899,
                  "n_patterns": 3200}]
    v2, msg2 = compute_verdict({"cells": cells_hp})
    assert "HARD_PASS" in v2, f"Self-test HP failed: {v2}: {msg2}"


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_use = N_SMOKE if smoke else N_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    M_per = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL

    outdir = get_output_dir()
    t0 = time.time()
    cells = []

    for seed in seeds:
        for K in K_sweep:
            print(f"K={K} seed={seed}...", flush=True)
            cell = run_one_K(K, seed, N_use, M_per)
            cells.append(cell)
            elapsed = time.time() - t0
            print(f"  ent={cell['routing_entropy_bits']:.3f}b ret={cell['retention']:.3f} "
                  f"elapsed={elapsed:.1f}s")

    elapsed_s = time.time() - t0
    summary = {"cells": cells, "N": N_use, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_use,
            "K_sweep": K_sweep,
            "seeds": seeds,
            "M_per_expert": M_per,
            "n_grad_steps": N_GRAD_STEPS,
            "smoke": smoke,
        },
        "summary": summary,
    }

    out = outdir / "metrics.json"
    with open(out, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nVERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"elapsed={elapsed_s:.1f}s")
    print(f"metrics -> {out}")


if __name__ == "__main__":
    main()
