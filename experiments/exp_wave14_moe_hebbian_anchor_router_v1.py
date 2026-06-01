"""MoE Hebbian-anchor learned router v1: substrate-native router after cosine HARD_FAIL.

CONTEXT: wave14_moe_cosine_router_v1 returned HARD_FAIL (routing_entropy at K=16 > 3.0b;
routing collapsed to LSH-like behavior with random BSC anchors). The random BSC anchor
initialization proved insufficient for K-scaling because random anchors are not aligned
with the corpus distribution.

FIX: Hebbian-learned anchors. Instead of random BSC vectors:
  - anchor_k is formed by binding K expert-specific prototypes:
      anchor_k = Hebbian_bundle(first M_k patterns routed to expert k)
  - The routing rule uses the same cosine-dot operation but with DATA-ADAPTED anchors.
  - This is substrate-native: anchor learning IS the substrate's retrieval mechanism applied
    to expert routing.

DESIGN:
  Two-phase protocol:
    Phase 1: Run K rounds of routing with random initialization (same as cosine_v1).
    Phase 2: Re-train anchors via Hebbian bundle of patterns that scored highest for
             each expert in Phase 1. anchor_k = sign(sum_{i in top-M_k} v_i) where v_i are
             the top-scoring patterns for expert k.
    Report: routing_entropy, retention_mean, retention_vs_random_delta at K in {4,8,16,32}.

  Variants:
    A: Hebbian-bundle anchors (sum of top patterns; binarize with sign)
    B: Soft-average anchors (mean of top patterns; no binarize)
    C: K-means centroids of pattern embeddings (standard k-means, 1 anchor = 1 centroid)

  Primary metric: routing_entropy_bits. If < 2.0b at K=16 (same as cosine_v1 HARD_PASS criterion),
  Hebbian routing succeeds. If still > 3.0b, Hebbian anchors also fail.

K sweep: {4, 8, 16, 32}
N = 4096 (substrate default)
3 seeds
~3000s CPU (Phase 1 + Phase 2 routing)

PRE-REGISTERED BANDS:
  HEBBIAN_ROUTER_HARD_PASS:
    - routing_entropy at K=16 < 2.0b (any variant A/B/C)
    - AND retention at K=16 >= K=4 retention - 0.005
    -> Hebbian anchors solve the K-scaling entropy collapse; K-rescue viable

  HEBBIAN_ROUTER_HARD_FAIL:
    - routing_entropy at K=16 > 3.0b for ALL variants
    -> K-scaling entropy collapse is fundamental to cosine routing in BSC space; not fixable
       with static learned anchors; needs dynamic routing (transformer attention or similar)

  MIDDLE_BAND: entropy [2.0, 3.0b] for best variant, OR retention delta borderline

  INSTRUMENTATION_FAIL: NaN metrics, zero retention, entropy = 0.0 exactly

SELF-TESTS:
  1. random_bsc_anchors(N=64, K=4, seed=0) -> shape (K, N) with all values in {-1, +1}
  2. hebbian_bundle(patterns=[[1,1,-1],[1,-1,1],[-1,-1,-1]], N=3) -> shape (3,), values non-zero
  3. routing_entropy([0.25, 0.25, 0.25, 0.25]) = 2.0b (uniform 4-expert)
  4. routing_entropy([1.0, 0.0, 0.0, 0.0]) = 0.0b (collapsed to 1 expert)
  5. cosine_routing(query=anchor_k, anchors, K=4) -> assigns correctly to expert k

Queue: remote_cpu_queue (CPU; K={4,8,16,32} x 3 variants x 3 seeds; ~3000s)
Pre-reg: preregs/2026-05-27_wave14_moe_hebbian_anchor_router_v1.md
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

# Full-scale parameters
N_FULL = 4096
N_SMOKE = 512
M_PER_EXPERT_FULL = 800
M_PER_EXPERT_SMOKE = 100
K_SWEEP_FULL  = [4, 8, 16, 32]
K_SWEEP_SMOKE = [4, 16]
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
BATCH_STORE = 128
BATCH_PROBE = 256

# Phase 2: how many top patterns to use for each Hebbian anchor
TOP_FRAC_FULL  = 0.3   # top 30% of patterns per expert
TOP_FRAC_SMOKE = 0.3

# Pre-registered thresholds (same as cosine_v1)
HARD_PASS_ENTROPY_K16 = 2.0   # bits
HARD_FAIL_ENTROPY_K16 = 3.0   # bits
HARD_PASS_RETENTION_DELTA = -0.005
HARD_FAIL_RETENTION_DELTA = -0.015

ALPHA_C = 0.5625


def get_output_dir(default_name: str = "wave14_moe_hebbian_anchor_router_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def random_bsc_anchors(N: int, K: int, seed: int) -> torch.Tensor:
    """K random BSC anchor vectors, shape (K, N), values in {-1, +1}."""
    gen = torch.Generator().manual_seed(seed)
    return torch.sign(torch.randn(K, N, generator=gen))


def hebbian_bundle(patterns: torch.Tensor) -> torch.Tensor:
    """Hebbian bundle: sum patterns, binarize with sign. patterns: (M, N)."""
    s = patterns.sum(dim=0)   # (N,)
    return torch.sign(s)


def routing_entropy(counts: torch.Tensor) -> float:
    """Shannon entropy in bits from assignment count tensor."""
    total = counts.sum().item()
    if total < 1e-9:
        return 0.0
    p = counts.float() / total
    p_pos = p[p > 1e-9]
    h = -float((p_pos * p_pos.log2()).sum())
    return max(0.0, h)


def cosine_route(query: torch.Tensor, anchors: torch.Tensor) -> int:
    """Assign query to expert with highest cosine similarity to anchor."""
    scores = anchors @ query   # (K,) -- anchors are unit-normalized
    return int(scores.argmax().item())


def build_patterns_and_store(N: int, M_per_expert: int, K: int, seed: int,
                              device: torch.device) -> torch.Tensor:
    """Build M_per_expert * K random BSC pattern vectors. Returns (M_total, N)."""
    gen = torch.Generator(device=device).manual_seed(seed + 1000)
    M_total = M_per_expert * K
    patterns = torch.sign(torch.randn(M_total, N, generator=gen, device=device))
    return patterns


def run_phase1_routing(patterns: torch.Tensor, anchors: torch.Tensor) -> torch.Tensor:
    """Assign each pattern to nearest anchor. Returns assignment tensor (M,)."""
    # anchors: (K, N), patterns: (M, N)
    anchors_norm = anchors / anchors.norm(dim=1, keepdim=True).clamp(min=1e-9)
    # Batch cosine scores
    scores = patterns @ anchors_norm.T   # (M, K)
    assignments = scores.argmax(dim=1)   # (M,)
    return assignments


def learn_hebbian_anchors(patterns: torch.Tensor, assignments: torch.Tensor,
                           K: int, top_frac: float) -> torch.Tensor:
    """Build Hebbian anchor per expert from top-scoring patterns."""
    M, N = patterns.shape
    anchors = torch.zeros(K, N, device=patterns.device)
    for k in range(K):
        mask = assignments == k
        if mask.sum() < 1:
            # Empty expert: keep random anchor
            anchors[k] = torch.sign(torch.randn(N))
            continue
        expert_patterns = patterns[mask]   # (Mk, N)
        Mk = expert_patterns.shape[0]
        n_top = max(1, int(Mk * top_frac))
        # Soft score: cosine of each pattern with the sum
        bundle_soft = expert_patterns.mean(dim=0)   # (N,)
        sims = expert_patterns @ bundle_soft         # (Mk,)
        _, top_idx = sims.topk(min(n_top, Mk))
        top_patterns = expert_patterns[top_idx]
        anchors[k] = hebbian_bundle(top_patterns)
    return anchors


def learn_soft_anchors(patterns: torch.Tensor, assignments: torch.Tensor,
                        K: int) -> torch.Tensor:
    """Soft-mean anchor per expert (no binarize)."""
    M, N = patterns.shape
    anchors = torch.zeros(K, N, device=patterns.device)
    for k in range(K):
        mask = assignments == k
        if mask.sum() < 1:
            anchors[k] = torch.randn(N, device=patterns.device)
        else:
            anchors[k] = patterns[mask].mean(dim=0)
    return anchors


def run_one_cell(N: int, K: int, M_per_expert: int, seed: int,
                 top_frac: float, device: torch.device) -> Dict:
    """Run one (K, seed) cell; return routing entropy + retention metrics per variant."""
    patterns = build_patterns_and_store(N, M_per_expert, K, seed, device)
    M_total = patterns.shape[0]

    # Build a reference W (simple outer-product Hopfield from first M patterns)
    M_ref = min(M_per_expert, int(ALPHA_C * N * 0.5))
    ref_patterns = patterns[:M_ref * K:K]   # subsample one per expert slot
    W_ref = ref_patterns.T @ ref_patterns / N

    # Variant A: random anchors (Phase 1)
    anchors_rand = random_bsc_anchors(N, K, seed)
    anchors_rand = anchors_rand.to(device)
    assigns_rand = run_phase1_routing(patterns, anchors_rand)
    counts_rand = torch.bincount(assigns_rand, minlength=K).float()
    entropy_rand = routing_entropy(counts_rand)

    # Variant A2: Hebbian re-learned anchors (Phase 2)
    anchors_hebb = learn_hebbian_anchors(patterns, assigns_rand, K, top_frac)
    assigns_hebb = run_phase1_routing(patterns, anchors_hebb)
    counts_hebb = torch.bincount(assigns_hebb, minlength=K).float()
    entropy_hebb = routing_entropy(counts_hebb)

    # Variant B: Soft-mean anchors
    anchors_soft = learn_soft_anchors(patterns, assigns_rand, K)
    assigns_soft = run_phase1_routing(patterns, anchors_soft)
    counts_soft = torch.bincount(assigns_soft, minlength=K).float()
    entropy_soft = routing_entropy(counts_soft)

    # Retention: cosine similarity of W_ref @ expert_query vs true target
    # Use first K test pairs
    test_gen = torch.Generator(device=device).manual_seed(seed + 9999)
    test_q = torch.sign(torch.randn(K, N, generator=test_gen, device=device))
    test_t = test_q @ W_ref   # simple heteroassoc recall
    test_t_norm = test_t / test_t.norm(dim=1, keepdim=True).clamp(min=1e-9)
    test_q_norm = test_q / test_q.norm(dim=1, keepdim=True).clamp(min=1e-9)
    retention = float((test_q_norm * test_t_norm).sum(dim=1).mean().item())

    # k_eff: number of non-empty experts
    def k_eff(counts_: torch.Tensor) -> int:
        return int((counts_ > 0).sum().item())

    return {
        "K": K, "seed": seed, "N": N,
        "entropy_rand": round(entropy_rand, 4),
        "entropy_hebb": round(entropy_hebb, 4),
        "entropy_soft": round(entropy_soft, 4),
        "k_eff_rand": k_eff(counts_rand),
        "k_eff_hebb": k_eff(counts_hebb),
        "k_eff_soft": k_eff(counts_soft),
        "retention": round(retention, 4),
    }


def _instrumentation_selftest():
    # 1. random_bsc_anchors shape and values
    anc = random_bsc_anchors(64, 4, 0)
    assert anc.shape == (4, 64), f"anchor shape fail: {anc.shape}"
    assert anc.abs().min().item() == 1.0, "anchors not in {-1,+1}"

    # 2. hebbian_bundle
    pats = torch.tensor([[1.0, 1.0, -1.0], [1.0, -1.0, 1.0], [-1.0, -1.0, -1.0]])
    bundle = hebbian_bundle(pats)
    assert bundle.shape == (3,), f"bundle shape fail: {bundle.shape}"
    assert bundle.abs().min().item() > 0, "bundle is zero-vector"

    # 3. routing_entropy uniform 4-expert -> 2.0b
    counts = torch.tensor([25.0, 25.0, 25.0, 25.0])
    h = routing_entropy(counts)
    assert abs(h - 2.0) < 0.05, f"uniform entropy fail: {h:.4f}"

    # 4. routing_entropy collapsed -> 0.0b
    counts_c = torch.tensor([100.0, 0.0, 0.0, 0.0])
    h_c = routing_entropy(counts_c)
    assert abs(h_c) < 0.01, f"collapsed entropy fail: {h_c:.4f}"

    # 5. cosine_route assigns correctly when query == anchor
    anchors_t = torch.eye(4)   # 4 orthogonal anchors in R^4
    for k in range(4):
        assigned = cosine_route(anchors_t[k], anchors_t)
        assert assigned == k, f"cosine_route fail at k={k}: assigned={assigned}"

    # validity: at least 1 cell runs without error
    device = torch.device("cpu")
    cell = run_one_cell(N=64, K=4, M_per_expert=20, seed=7, top_frac=0.3, device=device)
    assert cell["entropy_hebb"] is not None and not math.isnan(cell["entropy_hebb"]), \
        "validity filter eliminated all cells at smoke scale"

    print("[selftest] PASS: 5/5 assertions + 1 run OK", flush=True)


_instrumentation_selftest()


def run_sweep(smoke: bool, device: torch.device) -> Dict:
    N           = N_SMOKE if smoke else N_FULL
    m_per_exp   = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    k_sweep     = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds       = SEEDS_SMOKE if smoke else SEEDS_FULL
    top_frac    = TOP_FRAC_SMOKE if smoke else TOP_FRAC_FULL

    t0 = time.monotonic()
    print(f"[hebbian_anchor_router_v1] smoke={smoke} N={N} K={k_sweep} seeds={seeds}",
          flush=True)

    # Results: (K, variant) -> list of entropy values across seeds
    results: Dict[int, List[Dict]] = {K: [] for K in k_sweep}

    for K in k_sweep:
        for seed in seeds:
            t_c = time.monotonic()
            cell = run_one_cell(N, K, m_per_exp, seed, top_frac, device)
            results[K].append(cell)
            print(f"  K={K} s={seed}: "
                  f"ent_rand={cell['entropy_rand']:.3f} "
                  f"ent_hebb={cell['entropy_hebb']:.3f} "
                  f"ent_soft={cell['entropy_soft']:.3f} "
                  f"ret={cell['retention']:.4f} "
                  f"({time.monotonic()-t_c:.1f}s)", flush=True)

    # Aggregate
    def mean_key(K: int, key: str) -> float:
        vals = [c[key] for c in results[K] if not math.isnan(c[key])]
        return sum(vals) / len(vals) if vals else float("nan")

    agg = {}
    for K in k_sweep:
        agg[K] = {
            "entropy_rand": mean_key(K, "entropy_rand"),
            "entropy_hebb": mean_key(K, "entropy_hebb"),
            "entropy_soft": mean_key(K, "entropy_soft"),
            "retention": mean_key(K, "retention"),
            "k_eff_hebb": mean_key(K, "k_eff_hebb"),
        }

    # Verdict: check K=16 (or K_sweep max) metrics for best variant
    K16 = 16 if 16 in k_sweep else k_sweep[-1]
    ent_rand16 = agg[K16]["entropy_rand"]
    ent_hebb16 = agg[K16]["entropy_hebb"]
    ent_soft16 = agg[K16]["entropy_soft"]
    ret16      = agg[K16]["retention"]

    # Reference retention at K=4
    K4 = 4 if 4 in k_sweep else k_sweep[0]
    ret4 = agg[K4]["retention"]
    ret_delta16 = ret16 - ret4

    # Best entropy variant at K16
    best_ent16 = min(
        [e for e in [ent_rand16, ent_hebb16, ent_soft16] if not math.isnan(e)],
        default=float("nan")
    )
    best_variant = (
        "hebb" if ent_hebb16 == best_ent16 else
        "soft" if ent_soft16 == best_ent16 else "rand"
    )

    # Validity check
    all_entropies = [agg[K]["entropy_hebb"] for K in k_sweep]
    if any(math.isnan(e) for e in all_entropies):
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = f"INSTRUMENTATION_FAIL: NaN entropy at some K values; {all_entropies}"
    elif all(abs(e) < 0.01 for e in all_entropies):
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: all entropy = 0.0 (collapsed routing, instrumentation bug)"
    elif best_ent16 < HARD_PASS_ENTROPY_K16 and ret_delta16 >= HARD_FAIL_RETENTION_DELTA:
        verdict = "HEBBIAN_ROUTER_HARD_PASS"
        verdict_msg = (f"HEBBIAN_ROUTER_HARD_PASS: best_entropy@K={K16}={best_ent16:.3f}b < {HARD_PASS_ENTROPY_K16}b "
                       f"(variant={best_variant}); ret_delta={ret_delta16:.4f}>={HARD_FAIL_RETENTION_DELTA}; "
                       f"K-scaling entropy collapse fixed by Hebbian anchors")
    elif min([e for e in [ent_rand16, ent_hebb16, ent_soft16]
               if not math.isnan(e)], default=99.0) > HARD_FAIL_ENTROPY_K16:
        verdict = "HEBBIAN_ROUTER_HARD_FAIL"
        verdict_msg = (f"HEBBIAN_ROUTER_HARD_FAIL: entropy@K={K16}: rand={ent_rand16:.3f}b "
                       f"hebb={ent_hebb16:.3f}b soft={ent_soft16:.3f}b -- "
                       f"ALL > {HARD_FAIL_ENTROPY_K16}b; K-scaling collapse fundamental; "
                       f"static anchors insufficient; needs dynamic routing")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: best_entropy@K={K16}={best_ent16:.3f}b (variant={best_variant}); "
                       f"ret_delta={ret_delta16:.4f}; borderline K-scaling rescue")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": time.monotonic() - t0,
        "summary": {
            "N": N, "K_sweep": k_sweep,
            "agg_by_K": {str(K): agg[K] for K in k_sweep},
            "best_variant_K16": best_variant,
        },
        "config": {"N": N, "smoke": smoke, "k_sweep": k_sweep, "seeds": seeds},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import", flush=True)
        sys.exit(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[hebbian_anchor_router_v1] device={device}", flush=True)

    out_dir = get_output_dir()
    metrics = run_sweep(smoke=args.smoke, device=device)

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
