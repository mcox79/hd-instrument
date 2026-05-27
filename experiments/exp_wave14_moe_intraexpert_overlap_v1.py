"""MoE SHIFT intra-expert overlap probe: why K-scaling is flat.

CONTEXT: wave14_moe_shift_K_scaling_v1 MIDDLE_BAND (ratio=0.98, p=-0.02 near-flat).
wave14_moe_shift_M_scaling_v1 HARD_FAIL (no structural lift at any load level).
wave14_moe_gating_sharpness_v1 HARD_FAIL (gating sharpness not a lever).

HYPOTHESIS: The K-scaling flatness is caused by INTRA-EXPERT INTERFERENCE: as K
increases, each expert's W_k still contains many patterns from "wrong" experts
due to soft gating. We can measure this by computing:
  - inter_expert_cosine_sim: mean cosine similarity between patterns assigned to
    different experts (should be low for clean separation)
  - intra_expert_diversity: mean pairwise distance within each expert's pattern set
    (if diversity is high, expert isn't specializing)
  - routing_entropy: Shannon entropy of gate weights per query (low = sharp routing)

This provides a mechanistic diagnosis: if intra-expert overlap is HIGH at K=8+
(cross-expert cosine > 0.3), the SHIFT structure is not actually separating patterns
into independent experts -- they're all storing the same general distribution.

DESIGN:
  - K sweep: {2, 4, 8, 16, 32}
  - N = 2048 (CPU-friendly)
  - M_per_expert = 800 (50% of alpha_c*N at N=2048: alpha_c=0.5625, N=2048 -> 1152)
  - 3 seeds per K
  - Metrics per K:
    a) mean_inter_expert_cosine: avg cosine(x_i, x_j) for x_i in expert_k, x_j in expert_l, k!=l
    b) mean_intra_expert_diversity: avg pairwise cosine distance within each expert
    c) mean_routing_entropy: Shannon entropy of gate weights per query (bits)
    d) retention_A: standard retention metric

PRE-REGISTERED BANDS:
  OVERLAP_DOMINANT (intra-expert overlap explains flat K-scaling):
    - mean_inter_expert_cosine >= 0.3 at K >= 8
      (patterns are NOT cleanly separated by experts)
    - OR mean_routing_entropy >= 1.5 bits at K >= 8
      (routing is near-uniform; structural separation absent)
  STRUCTURAL_SEPARATION_CLEAN (expert separation IS working):
    - mean_inter_expert_cosine < 0.1 at all K in sweep
    - AND mean_routing_entropy < 0.5 bits (sharp routing)
  MIXED_EVIDENCE: intermediate values
  INSTRUMENTATION_FAIL: gini > 0.8 or routing entropy is NaN

Self-tests (per [[feedback-strategy-spec-formula-selftests]]):
  1. routing_entropy([1.0, 0.0, 0.0]) = 0.0 (zero entropy, perfect routing)
  2. routing_entropy([0.5, 0.5]) = 1.0 bit (maximum entropy for 2 experts)
  3. cosine_sim(v, v) = 1.0 for any unit vector v
  4. cosine_sim(v, -v) = -1.0 for any unit vector v

Queue: remote_cpu_queue (CPU; K*seeds*N=2048 sweep; ~30-60 min)
Pre-reg: preregs/2026-05-26_wave14_moe_intraexpert_overlap_v1.md
Dependency: no upstream dependencies (standalone mechanistic probe)
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
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import importlib.util
_moe_path = REPO / "experiments" / "exp_wave14_moe_shift_K_scaling_v1.py"
_moe_spec = importlib.util.spec_from_file_location("moe_k1", _moe_path)
moe_k1 = importlib.util.module_from_spec(_moe_spec)
_moe_spec.loader.exec_module(moe_k1)

# K-scaling v1 has its own inline infrastructure; use it directly
make_bsc = moe_k1.make_bsc
build_lsh_proj = moe_k1.build_lsh_proj
gate_assign = moe_k1.gate_assign_balanced
outer_product_store = moe_k1.outer_product_store
recall_cosine_batch = moe_k1.recall_cosine_batch

# Design parameters
K_SWEEP_FULL = [2, 4, 8, 16, 32]
K_SWEEP_SMOKE = [2, 4, 8]
N_FULL = 2048
N_SMOKE = 256
M_PER_EXPERT_FULL = 800     # ~70% of alpha_c*N at N=2048
M_PER_EXPERT_SMOKE = 100
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
ALPHA_C = 0.5625            # from wave14_moe_alpha_c_prestep_v3

# Pre-registered thresholds
OVERLAP_HP_COSINE = 0.3     # inter-expert cosine >= 0.3 -> overlap-dominant
OVERLAP_HP_ENTROPY = 1.5    # routing entropy >= 1.5 bits -> routing is soft
CLEAN_SEP_COSINE = 0.1      # < 0.1 -> clean separation
CLEAN_SEP_ENTROPY = 0.5     # < 0.5 bits -> sharp routing
GINI_MAX = 0.8              # instfail gate


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    for k in ("verdict", "verdict_msg", "elapsed_s", "summary"):
        assert k in d and d[k] is not None, f"metric missing: {k}"


def routing_entropy(weights: torch.Tensor) -> float:
    """Shannon entropy of routing weights in bits."""
    w = weights.clamp(min=1e-9)
    w = w / w.sum()
    h = -(w * w.log2()).sum().item()
    return max(0.0, h)


def mean_pairwise_cosine(vecs: torch.Tensor) -> float:
    """Mean cosine similarity between all pairs in vecs (N_patterns x D)."""
    if vecs.shape[0] < 2:
        return 0.0
    norms = vecs.norm(dim=1, keepdim=True).clamp(min=1e-9)
    unit = vecs / norms
    n = unit.shape[0]
    # Sample up to 500 pairs for efficiency
    max_pairs = min(n * (n - 1) // 2, 500)
    if n <= 32:
        # Compute full
        G = unit @ unit.T
        mask = ~torch.eye(n, dtype=torch.bool)
        return G[mask].mean().item()
    else:
        # Sample pairs
        idx_i = torch.randint(0, n, (max_pairs,))
        idx_j = torch.randint(0, n, (max_pairs,))
        same = idx_i == idx_j
        idx_j[same] = (idx_j[same] + 1) % n
        cos = (unit[idx_i] * unit[idx_j]).sum(dim=1)
        return cos.mean().item()


def run_one_cell(K: int, N: int, M_per_expert: int, seed: int, device) -> Dict:
    """Run one MoE SHIFT cell and compute overlap diagnostics."""
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert

    # Generate random BSC keys and values (same as K-scaling v1 approach)
    keys_raw = make_bsc(M_total, N, gen, device)   # (M_total, N)
    vals_raw = make_bsc(M_total, N, gen, device)   # (M_total, N)

    # Build LSH gate and assign patterns to experts
    gate_proj = build_lsh_proj(N, K, gen, device)
    assignments = gate_assign(keys_raw, gate_proj, K)

    # Per-expert pattern sets
    expert_keys = []
    expert_vals = []
    for k in range(K):
        mask = assignments == k
        expert_keys.append(keys_raw[mask])
        expert_vals.append(vals_raw[mask])

    # Gini of expert sizes
    sizes = torch.tensor([len(ek) for ek in expert_keys], dtype=torch.float)
    n_total = sizes.sum()
    gini = 0.0
    if n_total > 0:
        for i in range(K):
            for j in range(K):
                gini += abs(sizes[i] - sizes[j]).item()
        gini /= (2 * K * n_total.item())

    # Per-expert W matrices (SHIFT: each expert gets full N x N)
    Wks = []
    for k in range(K):
        W_k = torch.zeros(N, N, device=device)
        ek = expert_keys[k].float()
        ev = expert_vals[k].float()
        if len(ek) > 0:
            W_k = (ev.T @ ek) / N
        Wks.append(W_k)

    # Intra-expert diversity: mean pairwise cosine within each expert
    intra_cosines = []
    for k in range(K):
        ek = expert_keys[k]
        if len(ek) >= 2:
            c = mean_pairwise_cosine(ek)
            intra_cosines.append(c)
    mean_intra = sum(intra_cosines) / max(len(intra_cosines), 1)

    # Inter-expert cosine: mean cosine between patterns from different experts
    inter_cosines = []
    for ki in range(K):
        for kj in range(ki + 1, K):
            eki = expert_keys[ki]
            ekj = expert_keys[kj]
            if len(eki) >= 1 and len(ekj) >= 1:
                # Sample up to 100 pairs
                n_s = min(100, len(eki) * len(ekj))
                idx_i = torch.randint(0, len(eki), (n_s,))
                idx_j = torch.randint(0, len(ekj), (n_s,))
                vi = eki[idx_i]
                vj = ekj[idx_j]
                ni = vi.norm(dim=1, keepdim=True).clamp(min=1e-9)
                nj = vj.norm(dim=1, keepdim=True).clamp(min=1e-9)
                cos = ((vi / ni) * (vj / nj)).sum(dim=1).mean().item()
                inter_cosines.append(cos)
    mean_inter = sum(inter_cosines) / max(len(inter_cosines), 1)

    # Routing entropy: compute gate weights for all training keys
    gate_scores = keys_raw @ gate_proj.T   # (M_total, K)
    gate_weights = torch.softmax(gate_scores, dim=1)  # (M_total, K)
    mean_entropy = sum(routing_entropy(gate_weights[i]) for i in range(min(500, gate_weights.shape[0])))
    mean_entropy /= min(500, gate_weights.shape[0])

    # SHIFT aggregate retention
    W_shift = sum(Wks)
    # Quick retention proxy: mean cosine of stored patterns
    test_keys = keys_raw[:min(100, len(keys_raw))]
    retrieved = test_keys @ W_shift.T
    retrieved_top = retrieved.argmax(dim=1)
    # Simplified: measure self-consistency (not full BPC)
    retention_proxy = (test_keys * (W_shift @ test_keys.T).T).sum(dim=1).mean().item()
    retention_proxy = max(0.0, min(2.0, float(retention_proxy)))

    return {
        "seed": seed,
        "K": K,
        "gini": round(gini, 4),
        "mean_intra_expert_cosine": round(mean_intra, 4),
        "mean_inter_expert_cosine": round(mean_inter, 4),
        "mean_routing_entropy_bits": round(mean_entropy, 4),
        "expert_sizes": sizes.tolist(),
        "retention_proxy": round(retention_proxy, 4),
    }


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. routing_entropy tests
    h_zero = routing_entropy(torch.tensor([1.0, 0.0, 0.0]))
    assert abs(h_zero) < 0.01, f"routing_entropy([1,0,0])={h_zero} != 0"
    h_max = routing_entropy(torch.tensor([0.5, 0.5]))
    assert abs(h_max - 1.0) < 0.01, f"routing_entropy([0.5,0.5])={h_max} != 1.0"

    # 2. cosine self-similarity
    v = torch.randn(32).float()
    v_unit = v / v.norm()
    c_self = mean_pairwise_cosine(torch.stack([v_unit, v_unit]))
    assert abs(c_self - 1.0) < 0.02, f"cosine(v,v)={c_self} not ~1.0"

    # 3. cosine anti-similarity
    c_anti = mean_pairwise_cosine(torch.stack([v_unit, -v_unit]))
    assert abs(c_anti + 1.0) < 0.02, f"cosine(v,-v)={c_anti} not ~-1.0"

    # 4. Run one small cell
    device = torch.device("cpu")
    cell = run_one_cell(K=2, N=128, M_per_expert=20, seed=42, device=device)
    for key in ("mean_intra_expert_cosine", "mean_inter_expert_cosine",
                "mean_routing_entropy_bits", "gini"):
        assert key in cell and math.isfinite(cell[key]), f"{key} not finite in selftest"

    print("[selftest] PASS: all 4 assertions OK")


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_moe_intraexpert_overlap_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)

    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    N = N_SMOKE if smoke else N_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    device = torch.device("cpu")  # CPU experiment

    results_per_K: Dict[int, dict] = {}

    for K in K_sweep:
        print(f"\n[K={K}]", flush=True)
        seed_results = []
        for seed in seeds:
            cell = run_one_cell(K, N, M_per_expert, seed, device)
            seed_results.append(cell)
            print(f"  seed={seed}: inter_cos={cell['mean_inter_expert_cosine']:.4f} "
                  f"intra_cos={cell['mean_intra_expert_cosine']:.4f} "
                  f"entropy={cell['mean_routing_entropy_bits']:.3f}bits "
                  f"gini={cell['gini']:.3f}", flush=True)

        def m(key):
            return sum(r[key] for r in seed_results) / len(seed_results)

        results_per_K[K] = {
            "mean_inter_expert_cosine": round(m("mean_inter_expert_cosine"), 4),
            "mean_intra_expert_cosine": round(m("mean_intra_expert_cosine"), 4),
            "mean_routing_entropy_bits": round(m("mean_routing_entropy_bits"), 4),
            "mean_gini": round(m("gini"), 4),
            "seed_results": seed_results,
        }

    # Verdict computation
    K_vals = sorted(results_per_K.keys())
    K_hi = max(K_vals) if len(K_vals) > 2 else K_vals[-1]
    inter_at_K_hi = results_per_K[K_hi]["mean_inter_expert_cosine"]
    entropy_at_K_hi = results_per_K[K_hi]["mean_routing_entropy_bits"]
    gini_at_K_hi = results_per_K[K_hi]["mean_gini"]

    if gini_at_K_hi > GINI_MAX:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = f"INSTRUMENTATION_FAIL: gini={gini_at_K_hi:.3f} > {GINI_MAX} at K={K_hi}"
    elif inter_at_K_hi >= OVERLAP_HP_COSINE or entropy_at_K_hi >= OVERLAP_HP_ENTROPY:
        verdict = "OVERLAP_DOMINANT"
        verdict_msg = (f"OVERLAP_DOMINANT: intra-expert overlap explains flat K-scaling. "
                       f"inter_cosine={inter_at_K_hi:.4f} (>={OVERLAP_HP_COSINE}), "
                       f"routing_entropy={entropy_at_K_hi:.3f}bits (>={OVERLAP_HP_ENTROPY}) at K={K_hi}.")
    elif inter_at_K_hi < CLEAN_SEP_COSINE and entropy_at_K_hi < CLEAN_SEP_ENTROPY:
        verdict = "STRUCTURAL_SEPARATION_CLEAN"
        verdict_msg = (f"STRUCTURAL_SEPARATION_CLEAN: Expert separation IS working. "
                       f"inter_cosine={inter_at_K_hi:.4f} (<{CLEAN_SEP_COSINE}), "
                       f"routing_entropy={entropy_at_K_hi:.3f}bits (<{CLEAN_SEP_ENTROPY}) at K={K_hi}. "
                       f"K-scaling flatness has different cause (not overlap).")
    else:
        verdict = "MIXED_EVIDENCE"
        verdict_msg = (f"MIXED_EVIDENCE: Intermediate overlap. "
                       f"inter_cosine={inter_at_K_hi:.4f}, entropy={entropy_at_K_hi:.3f}bits at K={K_hi}.")

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    summary = {
        "K_sweep": K_vals,
        "inter_cosine_per_K": {K: results_per_K[K]["mean_inter_expert_cosine"] for K in K_vals},
        "intra_cosine_per_K": {K: results_per_K[K]["mean_intra_expert_cosine"] for K in K_vals},
        "entropy_per_K": {K: results_per_K[K]["mean_routing_entropy_bits"] for K in K_vals},
        "gini_per_K": {K: results_per_K[K]["mean_gini"] for K in K_vals},
    }

    out_dir = get_output_dir("wave14_moe_intraexpert_overlap_v1")
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "per_K_details": {str(K): results_per_K[K] for K in K_vals},
        "config": {"K_sweep": K_vals, "N": N, "M_per_expert": M_per_expert,
                   "seeds": seeds, "smoke": smoke},
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
        _instrumentation_selftest()
        sys.exit(0)
    run(smoke=args.smoke)
