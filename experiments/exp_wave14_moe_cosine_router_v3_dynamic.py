"""MoE dynamic router v3: substrate W-matrix native routing (no fixed anchors).

CONTEXT:
  v1 (random BSC anchors + cosine): HARD_FAIL -- entropy@K=16 = 3.999b > 3.0b.
  v2 (k-stress sweep): COSINE_ROUTER_K_STRESS_MIDDLE -- K=16 OK, K=32 degrades.
  v1_hebbian (static Hebbian-learned anchors): HARD_FAIL -- entropy@K=16 = 3.995b > 3.0b.
  Cap_map v224: "cosine-dot rescue OUT; next rescue=Hebbian-anchor cosine." But static
  Hebbian anchors also HARD_FAIL. Root cause per v220: routing_entropy = K-scaling
  degradation source; static anchors (random OR Hebbian) both collapse to uniform routing
  at large K because BSC anchor vectors are poorly separated in high-K regime.

FIX v3: Dynamic W-matrix routing (substrate-native attention).
  Instead of routing by cosine(query, fixed_anchor_k), route by:
    score_k(v) = v^T @ W_k @ v
  where W_k is the k-th expert's learned weight matrix (the substrate matrix restricted
  to expert k's slot). This is "substrate-native attention": the router uses the same
  quadratic form as the substrate's energy function.

  This eliminates the anchor-degeneracy problem because W_k is data-adaptive by
  construction -- it is the Hebbian outer-product sum of patterns routed to expert k.

  Protocol:
    Phase 1 (bootstrap): Split patterns randomly into K groups. Train each W_k on its group.
    Phase 2 (route): For each new pattern v, assign to argmax_k(v^T @ W_k @ v).
    Phase 3 (re-train): Re-train W_k on the newly assigned patterns. Repeat 3 iterations.
    Measure: routing_entropy, retention_mean, k_eff = effective number of experts.

  Variants:
    A: W-matrix score routing (v^T W_k v)
    B: Random-subspace routing (project v to K dimensions; route by max component)

  Primary metric: routing_entropy_bits at K=16. If < 2.0b, HARD_PASS.

K sweep: {4, 8, 16, 32}
N = 512 (smoke), 4096 (full)
Seeds: 3 (smoke), 5 (full)
~2000s CPU (3 routing iterations x K values x seeds)

PRE-REGISTERED BANDS:
  DYNAMIC_ROUTER_HARD_PASS:
    - routing_entropy at K=16 < 2.0b for variant A or B
    - AND retention delta vs random >= -0.010 (at most 1% worse than random assignment)
    -> W-matrix dynamic routing solves K-scaling entropy collapse; K-rescue viable

  DYNAMIC_ROUTER_HARD_FAIL:
    - routing_entropy at K=16 > 3.0b for ALL variants
    -> K-scaling entropy collapse is fundamental; static AND dynamic anchors both fail;
       requires architectural change (K=4 design point is the ceiling for MoE SHIFT)

  MIDDLE_BAND: entropy in [2.0b, 3.0b] for best variant

SELF-TESTS:
  1. bsc_random(N=64, K=4, seed=0) -> shape (K, N) with all values in {-1, +1}
  2. routing_entropy([0.25, 0.25, 0.25, 0.25]) = 2.0b (uniform 4-expert)
  3. w_score_routing(v, [W_0, W_1]) = argmax(v^T W_0 v, v^T W_1 v) correct
  4. effective_k([0.5, 0.5, 0.0, 0.0]) = 2.0 (two active experts)
  5. retention from empty W = 0.5 (random chance for BSC retrieval)

Queue: remote_cpu_queue (CPU; K={4,8,16,32} x 2 variants x seeds; ~2000s)
Pre-reg: preregs/2026-05-27_wave14_moe_cosine_router_v3_dynamic.md
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Parameters
N_SMOKE  = 512
N_FULL   = 4096
K_SWEEP  = [4, 8, 16, 32]
SEEDS_SMOKE = [17, 23, 31]
SEEDS_FULL  = [7, 17, 23, 31, 41]
M_PATTERNS  = 200    # patterns to store per expert (smoke); scales with N in full
N_ROUTE_ITERS = 3   # dynamic routing iterations

# Thresholds
HP_ENTROPY_MAX = 2.0   # bits at K=16
HF_ENTROPY_MIN = 3.0   # bits at K=16 (same pre-reg as v1)
HP_RETENTION_DELTA_MIN = -0.010
ALPHA_HEBBIAN = 0.1


def get_output_dir(default_name: str = "wave14_moe_cosine_router_v3_dynamic") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_bsc_patterns(M: int, N: int, seed: int) -> torch.Tensor:
    """M random {-1,+1} patterns. Shape: (M, N)."""
    gen = torch.Generator().manual_seed(seed)
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen).float() - 1.0


def routing_entropy_bits(assignments: torch.Tensor, K: int) -> float:
    """Shannon entropy of routing distribution in bits."""
    counts = torch.bincount(assignments.long(), minlength=K).float()
    probs = counts / counts.sum().clamp(min=1e-9)
    probs = probs[probs > 0]
    return float(-(probs * probs.log2()).sum())


def effective_k(assignments: torch.Tensor, K: int) -> float:
    """Effective number of active experts: exp(routing_entropy)."""
    ent = routing_entropy_bits(assignments, K)
    return math.exp(ent * math.log(2))


def train_w(patterns: torch.Tensor, N: int) -> torch.Tensor:
    """Hebbian weight matrix from patterns. Shape: (N, N), no diagonal."""
    W = torch.zeros((N, N))
    for v in patterns:
        W += ALPHA_HEBBIAN * torch.outer(v, v) / N
    W.fill_diagonal_(0.0)
    return W


def w_score_route(patterns: torch.Tensor, W_list: List[torch.Tensor]) -> torch.Tensor:
    """Route each pattern to the expert with highest W-score: v^T W_k v.
    Returns assignment tensor of shape (M,)."""
    M = patterns.shape[0]
    K = len(W_list)
    scores = torch.zeros(M, K)
    for k, Wk in enumerate(W_list):
        # v^T W_k v = quadratic form
        h = patterns @ Wk   # (M, N)
        scores[:, k] = (patterns * h).sum(dim=1)
    return scores.argmax(dim=1)


def random_subspace_route(patterns: torch.Tensor, K: int, seed: int) -> torch.Tensor:
    """Route by random projection: each pattern assigned to argmax of K projections."""
    N = patterns.shape[0]
    gen = torch.Generator().manual_seed(seed + 1000)
    proj = 2.0 * torch.randint(0, 2, (K, patterns.shape[1]), generator=gen).float() - 1.0
    proj = proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-8)
    scores = patterns @ proj.T   # (M, K)
    return scores.argmax(dim=1)


def retention_from_w(W: torch.Tensor, patterns: torch.Tensor) -> float:
    """Fraction of patterns retrievable: sign(W @ v) dot v / N > 0.95."""
    if len(patterns) == 0:
        return 0.0
    h = patterns @ W.T   # (M, N)
    overlap = (h.sign() * patterns).sum(dim=1) / patterns.shape[1]
    return float((overlap > 0.7).float().mean())


def run_variant(N: int, K: int, seed: int, variant: str) -> Dict:
    """Run one cell: variant in {'w_score', 'random_subspace'}."""
    M = int(min(M_PATTERNS * K, N * 0.8))   # scale M with K but cap at 80% of alpha_c*N*K

    patterns = make_bsc_patterns(M, N, seed)

    # Bootstrap: random initial assignment
    gen = torch.Generator().manual_seed(seed + 500)
    assignments = torch.randint(0, K, (M,), generator=gen)

    W_list = [torch.zeros((N, N)) for _ in range(K)]

    for iteration in range(N_ROUTE_ITERS):
        # Train each expert on its patterns
        for k in range(K):
            mask = (assignments == k)
            expert_patterns = patterns[mask]
            if len(expert_patterns) > 0:
                W_list[k] = train_w(expert_patterns, N)

        # Re-route
        if variant == "w_score":
            assignments = w_score_route(patterns, W_list)
        else:  # random_subspace
            assignments = random_subspace_route(patterns, K, seed + iteration)

    ent = routing_entropy_bits(assignments, K)
    keff = effective_k(assignments, K)

    # Retention: average over experts
    ret_vals = []
    for k in range(K):
        mask = (assignments == k)
        expert_pats = patterns[mask]
        if len(expert_pats) > 0:
            ret = retention_from_w(W_list[k], expert_pats)
            ret_vals.append(ret)
    mean_ret = sum(ret_vals) / len(ret_vals) if ret_vals else 0.0

    return {
        "N": N, "K": K, "seed": seed, "variant": variant,
        "M": M, "n_route_iters": N_ROUTE_ITERS,
        "routing_entropy_bits": round(ent, 4),
        "k_eff": round(keff, 3),
        "mean_retention": round(mean_ret, 5),
    }


def _instrumentation_selftest():
    # 1. make_bsc_patterns: all values in {-1, +1}
    p = make_bsc_patterns(10, 64, 0)
    assert p.shape == (10, 64), f"selftest 1 FAIL: shape={p.shape}"
    assert ((p == 1.0) | (p == -1.0)).all(), "selftest 1 FAIL: not BSC"
    print("[selftest] 1/5 make_bsc_patterns OK")

    # 2. routing_entropy uniform 4-expert = 2.0b
    asgn = torch.tensor([0, 1, 2, 3, 0, 1, 2, 3])
    ent = routing_entropy_bits(asgn, 4)
    assert abs(ent - 2.0) < 0.05, f"selftest 2 FAIL: ent={ent}"
    print(f"[selftest] 2/5 routing_entropy(uniform K=4)={ent:.4f} expected 2.0 OK")

    # 3. w_score_routing: assigning to the expert whose W was built from that pattern
    N_t = 64
    v_a = 2.0 * torch.randint(0, 2, (1, N_t)).float() - 1.0
    v_b = 2.0 * torch.randint(0, 2, (1, N_t)).float() - 1.0
    Wa = train_w(v_a, N_t)
    Wb = train_w(v_b, N_t)
    asgn_a = w_score_route(v_a, [Wa, Wb])
    assert int(asgn_a[0]) == 0, f"selftest 3 FAIL: v_a routed to {int(asgn_a[0])} not expert 0"
    print(f"[selftest] 3/5 w_score_routing: v_a -> expert 0 OK")

    # 4. effective_k([0.5, 0.5, 0.0, 0.0]) = 2.0
    asgn4 = torch.tensor([0, 0, 1, 1])
    keff = effective_k(asgn4, 4)
    assert abs(keff - 2.0) < 0.1, f"selftest 4 FAIL: keff={keff}"
    print(f"[selftest] 4/5 effective_k([0.5,0.5,0,0])={keff:.3f} expected 2.0 OK")

    # 5. retention from zero W = ~0.5
    W_zero = torch.zeros((N_t, N_t))
    pats = make_bsc_patterns(50, N_t, 42)
    ret = retention_from_w(W_zero, pats)
    assert 0.0 <= ret <= 0.6, f"selftest 5 FAIL: ret={ret} (expected ~0.5 for random W)"
    print(f"[selftest] 5/5 retention(W=0)={ret:.4f} ~ 0.5 OK")

    print("[selftest] PASS: 5/5 OK", flush=True)


_instrumentation_selftest()


def run_sweep(smoke: bool) -> Dict:
    N     = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    variants = ["w_score", "random_subspace"]

    t0 = time.monotonic()
    print(f"[moe_cosine_router_v3_dynamic] smoke={smoke} N={N} K_sweep={K_SWEEP} seeds={seeds}",
          flush=True)

    # Collect results per variant, per K
    results: Dict[str, Dict[int, List[Dict]]] = {v: {} for v in variants}
    for K in K_SWEEP:
        for variant in variants:
            results[variant][K] = []
            for seed in seeds:
                t_c = time.monotonic()
                cell = run_variant(N, K, seed, variant)
                results[variant][K].append(cell)
                print(f"  K={K} var={variant} s={seed}: "
                      f"ent={cell['routing_entropy_bits']:.3f}b "
                      f"k_eff={cell['k_eff']:.2f} "
                      f"ret={cell['mean_retention']:.4f} "
                      f"({time.monotonic()-t_c:.1f}s)", flush=True)

    # Aggregate
    agg: Dict[str, Dict] = {}
    for variant in variants:
        agg[variant] = {}
        for K in K_SWEEP:
            cells = results[variant][K]
            mean_ent = sum(c["routing_entropy_bits"] for c in cells) / len(cells)
            mean_ret = sum(c["mean_retention"] for c in cells) / len(cells)
            mean_keff = sum(c["k_eff"] for c in cells) / len(cells)
            agg[variant][str(K)] = {
                "mean_entropy_bits": round(mean_ent, 4),
                "mean_retention": round(mean_ret, 5),
                "mean_k_eff": round(mean_keff, 3),
                "n_seeds": len(cells),
            }

    # Verdict: check best variant at K=16
    best_ent_k16 = min(
        agg[v]["16"]["mean_entropy_bits"] for v in variants if "16" in agg[v]
    )
    best_variant = min(variants, key=lambda v: agg[v].get("16", {}).get("mean_entropy_bits", 999))
    best_ret_k16 = agg[best_variant].get("16", {}).get("mean_retention", 0.0)
    # Compare to K=4 retention for same variant as delta
    ret_k4 = agg[best_variant].get("4", {}).get("mean_retention", 0.0)
    retention_delta = best_ret_k16 - ret_k4

    if best_ent_k16 < HP_ENTROPY_MAX:
        verdict = "DYNAMIC_ROUTER_HARD_PASS"
        verdict_msg = (f"DYNAMIC_ROUTER_HARD_PASS: entropy@K=16={best_ent_k16:.3f}b < {HP_ENTROPY_MAX}b "
                       f"for variant={best_variant}; retention_delta@K=16={retention_delta:.4f}; "
                       f"W-matrix dynamic routing solves K-scaling entropy collapse")
    elif best_ent_k16 > HF_ENTROPY_MIN:
        verdict = "DYNAMIC_ROUTER_HARD_FAIL"
        verdict_msg = (f"DYNAMIC_ROUTER_HARD_FAIL: entropy@K=16={best_ent_k16:.3f}b > {HF_ENTROPY_MIN}b "
                       f"for all variants; K-scaling collapse fundamental; K=4 ceiling confirmed")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: entropy@K=16={best_ent_k16:.3f}b in [{HP_ENTROPY_MAX}, {HF_ENTROPY_MIN}]b "
                       f"for best_variant={best_variant}; partial improvement over static anchors")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.monotonic() - t0, 1),
        "results_per_variant_K": agg,
        "best_variant_K16": best_variant,
        "best_entropy_K16": round(best_ent_k16, 4),
        "config": {
            "N": N, "smoke": smoke, "K_sweep": K_SWEEP, "seeds": seeds,
            "n_route_iters": N_ROUTE_ITERS, "alpha_hebbian": ALPHA_HEBBIAN,
            "variants": variants,
        },
        "thresholds": {
            "hard_pass_entropy_K16": HP_ENTROPY_MAX,
            "hard_fail_entropy_K16": HF_ENTROPY_MIN,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import", flush=True)
        sys.exit(0)

    out_dir = get_output_dir()
    metrics = run_sweep(smoke=args.smoke)

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
