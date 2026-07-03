"""MoE attention-routing v1: soft attention over expert keys as router.

CONTEXT:
  MoE K-scaling has failed with 3 router variants:
  - cosine_router_v1: HARD_FAIL (entropy@K=16=3.999b > 3.0b; random BSC anchors)
  - remoe_relu_router_v1: HARD_FAIL (K_eff dynamic but retention collapses)
  - hebbian_anchor_router_v1: HARD_FAIL (entropy@K=16=3.995b; even learned anchors fail)
  The common failure mode: static per-expert keys cannot discriminate queries in BSC space
  because cosine distance distributes uniformly over K experts (all overlaps ~ 0).

NEW DIRECTION: attention-routing (transformer-style key-value lookup).
  Instead of hard router (argmax), use SOFT attention weights:
    alpha_k = softmax(query @ key_k / sqrt(N))
    output = sum_k alpha_k * W_k @ query

  Where key_k = the mean stored pattern for expert k (learned from the corpus).
  This is substrate-native: the "key" is a compressed prototype of expert k's patterns.
  Soft attention allows gradient to flow through all experts simultaneously.

  The HARD routing entropy problem does NOT apply to soft attention because we use
  the full distribution alpha_k, not argmax. K-scaling test: does soft-attention
  output retain task-A quality as K grows?

DESIGN:
  - N = 4096 (standard substrate)
  - K sweep: {4, 8, 16, 32}
  - M_per_expert = 200 (each expert learns 200 patterns)
  - 3 seeds
  - Router: soft attention with temperature tau (sweep tau in {0.5, 1.0, 2.0})
  - Keys: mean of each expert's stored patterns (after random assignment of corpus)
  - Metrics:
    1. attention_entropy_bits: entropy of alpha distribution
    2. retention_mean: mean retention across stored patterns
    3. k_effective: exp(-sum_k alpha_k * log alpha_k) effective expert count
    4. retention_vs_baseline_delta: delta from K=4 single-expert baseline

PRE-REGISTERED BANDS:
  HARD-PASS (attention routing lifts K-ceiling):
    - attention_entropy_bits at K=16 in [1.0, 3.5] (not collapsed, not uniform)
    - AND retention at K=16 >= K=4 baseline - 0.01 (within 1% of single-expert)
  HARD-FAIL (attention routing fails):
    - retention at K=16 < K=4 baseline - 0.05 (>5% degradation)
    - OR attention_entropy at K=16 > 3.8b (essentially uniform -- no routing signal)
  MIDDLE: entropy [1.0, 3.8] but retention delta in [-0.05, -0.01]

FORMULA SELF-TESTS:
  1. softmax([0,0,0,0]) -> [0.25, 0.25, 0.25, 0.25] (uniform; entropy = 2.0b at K=4)
  2. softmax([100,0,0,0]) -> [1,0,0,0] (collapsed; entropy = 0.0b)
  3. attention_entropy([0.25,0.25,0.25,0.25]) = 2.0b
  4. attention_entropy([1.0,0,0,0]) = 0.0b
  5. With K=1 expert: single-expert baseline, attention trivially routes all to it.

Timeout estimate:
  K=32 x 3 seeds x 3 tau values: ~3x of cosine_v1 (2288.9s) = ~6867s.
  But soft attention is cheaper than hard routing (no sorting/argmax):
  ~2500s * 3 seeds. timeout_s = ceil(1.5 * 2500 * 3) = 11250s -> exceeds 4h.
  REVISED: K={4,8,16} only (drop K=32) and 2 seeds. ~2500 * 0.75 * 2 = 3750s.
  timeout_s = ceil(1.5 * 3750) = 5625 -> 6000s. Under 4h.

N-suffix: no _nN suffix; production N = 4096.
Queue: remote_cpu_queue (CPU; softmax routing cheap; ~2-3h)
Pre-reg: preregs/2026-05-27_wave14_moe_attention_routing_v1.md
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

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Production config
N_FULL = 4096
N_SMOKE = 512
M_PER_EXPERT_FULL = 200
M_PER_EXPERT_SMOKE = 50
K_SWEEP_FULL = [4, 8, 16]
K_SWEEP_SMOKE = [4, 8]
TEMP_VALUES_FULL = [0.5, 1.0, 2.0]   # softmax temperature
TEMP_VALUES_SMOKE = [1.0]
SEEDS_FULL = [7, 17]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1

HP_ENTROPY_LOW = 1.0
HP_ENTROPY_HIGH = 3.5
HP_RETENTION_DELTA = -0.01
HF_ENTROPY_UNIFORM = 3.8
HF_RETENTION_DELTA = -0.05


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def softmax_with_temp(scores: torch.Tensor, temp: float) -> torch.Tensor:
    """Softmax with temperature scaling."""
    return torch.softmax(scores / max(temp, 1e-6), dim=-1)


def attention_entropy_bits(alpha: torch.Tensor) -> float:
    """Shannon entropy of attention weights in bits."""
    eps = 1e-12
    alpha_safe = alpha.clamp(eps, 1.0)
    H = -float((alpha_safe * alpha_safe.log()).sum()) / math.log(2.0)
    return H


def build_expert_substrate(N: int, M_per_expert: int, K: int, seed: int):
    """Build K expert weight matrices + learned keys."""
    g = torch.Generator()
    g.manual_seed(seed)
    W_experts = []
    keys = []
    all_patterns = []
    for k in range(K):
        # Expert k's patterns
        pats = torch.sign(torch.rand(M_per_expert, N, generator=g) - 0.5)
        pats[pats == 0] = 1.0
        all_patterns.append(pats)
        # Expert k's W (Hebbian)
        W_k = torch.zeros(N, N)
        for v in pats:
            W_k += ALPHA_HEBBIAN * torch.outer(v, v) / N
        W_k.fill_diagonal_(0.0)
        W_experts.append(W_k)
        # Key: mean of expert patterns (prototype)
        key_k = torch.sign(pats.mean(dim=0))
        key_k[key_k == 0] = 1.0
        keys.append(key_k)
    return W_experts, torch.stack(keys, dim=0), all_patterns


def run_one_K(N: int, M_per_expert: int, K: int, seed: int, temp: float) -> Dict:
    W_experts, keys, all_patterns = build_expert_substrate(N, M_per_expert, K, seed)
    g = torch.Generator()
    g.manual_seed(seed + 77777)

    # Baseline: single expert (K=1) retention
    W_single = W_experts[0].clone()
    for k in range(1, K):
        W_single = W_single + W_experts[k]
    W_single.fill_diagonal_(0.0)

    # Test retention for each expert's patterns
    total_correct = 0
    total_queries = 0
    entropy_vals = []
    k_eff_vals = []

    for k in range(K):
        pats_k = all_patterns[k]
        M_k = pats_k.shape[0]
        for mu in range(min(M_k, 10)):   # sample 10 patterns per expert
            v_target = pats_k[mu]
            v_noisy = v_target.clone()
            flip_mask = torch.rand(N, generator=g) < 0.1
            v_noisy[flip_mask] *= -1.0

            # Attention routing
            scores = (keys @ v_noisy) / math.sqrt(N)   # (K,) cosine-like scores
            alpha = softmax_with_temp(scores, temp)     # (K,) attention weights

            # Soft-attention output: weighted sum of expert retrievals
            output = torch.zeros(N)
            for k2 in range(K):
                retrieved = torch.sign(W_experts[k2] @ v_noisy)
                retrieved[retrieved == 0] = 1.0
                output = output + alpha[k2] * retrieved
            v_out = torch.sign(output)
            v_out[v_out == 0] = 1.0

            # Check if matches target expert's pattern
            overlap = float((v_out * v_target).sum()) / N
            total_correct += int(overlap > 0.7)
            total_queries += 1

            H = attention_entropy_bits(alpha)
            k_eff = float(torch.exp(-torch.sum(alpha * alpha.clamp(1e-12).log())))
            entropy_vals.append(H)
            k_eff_vals.append(k_eff)

    retention = total_correct / max(total_queries, 1)
    mean_entropy = float(sum(entropy_vals) / max(len(entropy_vals), 1))
    mean_k_eff = float(sum(k_eff_vals) / max(len(k_eff_vals), 1))

    return {
        "K": K, "N": N, "M_per_expert": M_per_expert, "seed": seed, "temp": temp,
        "retention": retention,
        "attention_entropy_bits": mean_entropy,
        "k_effective": mean_k_eff,
        "n_queries": total_queries,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: softmax formula
    scores_uniform = torch.zeros(4)
    alpha_uniform = softmax_with_temp(scores_uniform, 1.0)
    assert abs(float(alpha_uniform.mean()) - 0.25) < 1e-5, "uniform softmax error"

    scores_collapsed = torch.tensor([100.0, 0.0, 0.0, 0.0])
    alpha_collapsed = softmax_with_temp(scores_collapsed, 1.0)
    assert float(alpha_collapsed[0]) > 0.99, "collapsed softmax should route to expert 0"

    # Self-test 2: attention entropy
    H_uniform = attention_entropy_bits(torch.tensor([0.25, 0.25, 0.25, 0.25]))
    assert abs(H_uniform - 2.0) < 0.01, f"uniform 4-expert entropy should be 2.0b; got {H_uniform:.3f}"

    H_collapsed = attention_entropy_bits(torch.tensor([1.0, 0.0, 0.0, 0.0]))
    assert H_collapsed < 0.01, f"collapsed entropy should be ~0; got {H_collapsed:.3f}"

    # Self-test 3: run at smoke scale
    r = run_one_K(N_SMOKE, M_PER_EXPERT_SMOKE, K=4, seed=17, temp=1.0)
    assert "retention" in r, "missing retention"
    assert "attention_entropy_bits" in r, "missing attention_entropy_bits"
    assert 0.0 <= r["retention"] <= 1.0, f"retention out of range: {r['retention']}"
    assert r["attention_entropy_bits"] >= 0.0, f"entropy negative: {r['attention_entropy_bits']}"
    assert r["n_queries"] > 0, "no queries ran"

    # Self-test 4: multi-scale smoke
    r_smoke = run_one_K(N_SMOKE, M_PER_EXPERT_SMOKE, K=4, seed=17, temp=1.0)
    r_smoke4 = run_one_K(N_SMOKE * 4, M_PER_EXPERT_SMOKE * 2, K=4, seed=17, temp=1.0)
    assert r_smoke["retention"] >= 0.0, "smoke retention negative"
    assert r_smoke4["retention"] >= 0.0, "4x smoke retention negative"

    print(f"[selftest] v1 attention_routing PASSED: N={N_SMOKE} K=4 "
          f"retention={r['retention']:.3f} entropy={r['attention_entropy_bits']:.2f}b", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0_run = time.time()
    N = N_SMOKE if smoke else N_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    temps = TEMP_VALUES_SMOKE if smoke else TEMP_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "wave14_moe_attention_routing_v1")

    print(f"[run] {exp_name} {mode_str} N={N} K_sweep={K_sweep} temps={temps} seeds={seeds}", flush=True)
    out_dir = get_output_dir(exp_name)

    per_K: Dict[str, Dict] = {}
    for K in K_sweep:
        k_results = []
        for seed in seeds:
            for temp in temps:
                r = run_one_K(N, M_per_expert, K, seed, temp)
                k_results.append(r)
                print(f"  K={K} seed={seed} temp={temp}: "
                      f"ret={r['retention']:.3f} H={r['attention_entropy_bits']:.2f}b", flush=True)
        # Best temp: min entropy while max retention
        best_r = max(k_results, key=lambda x: x["retention"] - 0.1 * x["attention_entropy_bits"])
        per_K[str(K)] = {
            "mean_retention": float(sum(r["retention"] for r in k_results) / len(k_results)),
            "mean_entropy": float(sum(r["attention_entropy_bits"] for r in k_results) / len(k_results)),
            "best_retention": best_r["retention"],
            "best_entropy": best_r["attention_entropy_bits"],
            "best_temp": best_r["temp"],
        }

    # Verdict: compare K=16 (or highest K) vs K=4 baseline
    k4_retention = per_K.get("4", {}).get("mean_retention", 0.5)
    k16_key = "16" if "16" in per_K else str(K_sweep[-1])
    k16_retention = per_K.get(k16_key, {}).get("mean_retention", 0.0)
    k16_entropy = per_K.get(k16_key, {}).get("mean_entropy", 4.0)

    retention_delta = k16_retention - k4_retention

    if (HP_ENTROPY_LOW <= k16_entropy <= HP_ENTROPY_HIGH and
            retention_delta >= HP_RETENTION_DELTA):
        verdict = "ATTENTION_ROUTER_HARD_PASS"
        verdict_msg = (
            f"ATTENTION_ROUTER_HARD_PASS: entropy@K={k16_key}={k16_entropy:.2f}b in [{HP_ENTROPY_LOW},{HP_ENTROPY_HIGH}] "
            f"AND retention_delta={retention_delta:.3f} >= {HP_RETENTION_DELTA}. "
            f"Soft-attention routing succeeds where cosine/ReLU/Hebbian failed."
        )
    elif (k16_entropy > HF_ENTROPY_UNIFORM or retention_delta < HF_RETENTION_DELTA):
        verdict = "ATTENTION_ROUTER_HARD_FAIL"
        verdict_msg = (
            f"ATTENTION_ROUTER_HARD_FAIL: entropy@K={k16_key}={k16_entropy:.2f}b > {HF_ENTROPY_UNIFORM} "
            f"OR retention_delta={retention_delta:.3f} < {HF_RETENTION_DELTA}. "
            f"MoE K-scaling fundamentally broken in BSC space for all router families."
        )
    else:
        verdict = "ATTENTION_ROUTER_MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: entropy@K={k16_key}={k16_entropy:.2f}b, "
            f"retention_delta={retention_delta:.3f}. Partial routing success."
        )

    elapsed = round(time.time() - t0_run, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": f"moe_attention_v1 {mode_str}: K={k16_key} ret_delta={retention_delta:.3f} H={k16_entropy:.2f}b",
        "k4_retention": k4_retention,
        "k16_retention": k16_retention,
        "k16_entropy": k16_entropy,
        "retention_delta_k16_vs_k4": retention_delta,
        "per_K": per_K,
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
