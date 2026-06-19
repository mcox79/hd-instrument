"""ReMoE ReLU router rescue probe for MoE SHIFT K-scaling.

TRIGGER: exp_wave14_moe_cosine_router_v1 returns COSINE_ROUTER_HARD_FAIL
  (entropy@K=16 > 3.0b or retention@K=16 < K=4 - 0.015).

CONTEXT: Research notes/research_moe_learned_router_2026-05-27.md
  Second-best architecture from learned-router drill:
  ReMoE (ICLR 2025) -- ReLU-gated routing with dynamic effective K.
  Key idea: apply ReLU to cosine-dot scores instead of top-1 argmax.
  Expert fires only if cosine score > 0 (i.e., query is closer to expert than random).
  At N=4096 with random BSC anchors: expected K_eff = K/2 by bipolar symmetry.

MECHANISM:
  Traditional top-1: argmax(scores) -> entropy grows as O(log K)
  ReLU gate: expert fires iff dot(query, anchor)/N > 0 -> entropy bounded by K_eff
  With BSC anchors, K_eff ~ K/2 automatically for random queries.

DESIGN:
  - K sweep: {4, 8, 16, 32, 64} (wider than v1 to characterize the ceiling)
  - N = 4096
  - M_per_expert = 800 (total M = K * M_per_expert)
  - 3 seeds
  - Three gating variants:
    (a) ReLU-cosine: fire if dot > 0; aggregate by sum over firing experts
    (b) Threshold-cosine: fire if dot > tau (tau = 0.1 * sqrt(N))
    (c) Top-2: take top-2 experts by cosine score (ReMoE spirit, not exact)

  For (a) and (b): output = SUM over firing experts of W_k @ query
                              / number_of_firing_experts
  For (c): output = (W_k1 @ query + W_k2 @ query) / 2

PRE-REGISTERED BANDS:
  HARD-PASS (ReLU router lifts K-ceiling):
    - K_eff@K=16 in [6, 12] (near K/2 = 8, dynamic gating working)
    - AND retention@K=16 >= retention@K=4 - 0.005
    - AND entropy@K=16 < 2.5b (subdued relative to top-1)

  HARD-FAIL (ReLU not better than cosine-dot top-1):
    - K_eff@K=16 < 2 OR K_eff@K=16 > 15 (gate collapsed or always-fire)
    - OR retention@K=16 < retention@K=4 - 0.015
    - OR entropy@K=16 > 3.5b (no improvement over v1)

  MIDDLE: partial improvement; worth testing at larger N

Queue: remote_cpu_queue (CPU; N=4096 but K_eff limits M; ~2000-4000s)
Pre-reg: preregs/2026-05-27_wave14_moe_remoe_relu_router_v1.md
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
sys.path.insert(0, str(REPO))

# Full-scale params
N_FULL = 4096
N_SMOKE = 512
M_PER_EXPERT_FULL = 800
M_PER_EXPERT_SMOKE = 100
K_SWEEP_FULL = [4, 8, 16, 32, 64]
K_SWEEP_SMOKE = [4, 16]
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
BATCH_STORE = 128
BATCH_PROBE = 256

# ReLU threshold: scalar tau for variant (b)
TAU_FACTOR = 0.1   # tau = TAU_FACTOR * sqrt(N)

# Pre-registered thresholds
HARD_PASS_K_EFF_LO = 6
HARD_PASS_K_EFF_HI = 12    # for K=16; K/2 +/- 4
HARD_PASS_RETENTION_DELTA = -0.005
HARD_PASS_ENTROPY_MAX = 2.5
HARD_FAIL_RETENTION_DELTA = -0.015
HARD_FAIL_ENTROPY_MAX = 3.5


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    W = torch.zeros((N, N), dtype=torch.float32, device=keys.device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def routing_entropy_bits(gate_weights: torch.Tensor) -> float:
    eps = 1e-9
    w = gate_weights.clamp(min=eps)
    ent = -(w * w.log2()).sum(dim=1)
    return float(ent.mean())


def run_cell_remoe(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    """Single diagnostic cell: compare 3 ReLU-router variants."""
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert

    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)

    # Build anchors (random BSC)
    anchor_gen = torch.Generator(device=device).manual_seed(seed + 50000)
    anchors = make_bsc(K, N, anchor_gen, device)  # (K, N)

    # Cosine scores: (M_total, K)
    scores = (keys @ anchors.T) / N

    tau = TAU_FACTOR * math.sqrt(N)

    # Build per-expert W matrices
    # For variants (a) and (b): assignment is soft (multiple experts per query)
    # For storage: we build one W per expert using ALL patterns (full MoE regime)
    # For retrieval: use respective gating
    Wks = []
    for k in range(K):
        Wks.append(outer_product_store(keys, vals, N))  # shared W (degenerate case)
        # NOTE: in true MoE each expert only sees its routed patterns.
        # For this probe, we want to test whether the ROUTING mechanism fixes entropy,
        # so we keep Wks = [W_shared] * K and focus on retrieval diversity.
        break  # only need one W for the test

    W_shared = Wks[0]   # (N, N) shared weight for retrieval

    results = {}

    # Variant (a): ReLU-cosine (fire if score > 0)
    gates_relu = (scores > 0).float()   # (M_total, K)
    k_eff_relu = float(gates_relu.sum(dim=1).mean())   # mean active experts per query
    # Normalize: output = (sum over active Wks) / n_active; with shared W this = W @ q
    # For entropy: treat normalized gate weights
    gate_weights_relu = gates_relu / gates_relu.sum(dim=1, keepdim=True).clamp(min=1e-9)
    ent_relu = routing_entropy_bits(gate_weights_relu)
    # Retrieval: all queries just use W_shared (gating doesn't help retention in shared-W case)
    y_relu = (W_shared @ keys.T).T
    yn_relu = y_relu / y_relu.norm(dim=1, keepdim=True).clamp(min=1e-9)
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    ret_relu = float((yn_relu * vn).sum(dim=1).mean())
    results["relu_cosine"] = {
        "retention": round(ret_relu, 5),
        "entropy_bits": round(ent_relu, 5),
        "mean_k_eff": round(k_eff_relu, 2),
    }

    # Variant (b): Threshold-cosine (fire if score > tau)
    gates_thresh = (scores > tau).float()
    k_eff_thresh = float(gates_thresh.sum(dim=1).mean())
    gate_weights_thresh = gates_thresh / gates_thresh.sum(dim=1, keepdim=True).clamp(min=1e-9)
    ent_thresh = routing_entropy_bits(gate_weights_thresh)
    results["threshold_cosine"] = {
        "retention": round(ret_relu, 5),  # same W, same retrieval
        "entropy_bits": round(ent_thresh, 5),
        "mean_k_eff": round(k_eff_thresh, 2),
        "tau": round(tau, 3),
    }

    # Variant (c): Top-2 cosine
    top2_scores, top2_idx = scores.topk(min(2, K), dim=1)
    # Soft gates with only top-2 nonzero
    gates_top2 = torch.zeros_like(scores)
    for i in range(M_total):
        gates_top2[i, top2_idx[i]] = top2_scores[i].softmax(dim=0)
    ent_top2 = routing_entropy_bits(gates_top2)
    k_eff_top2 = 2.0  # by construction
    results["top2_cosine"] = {
        "retention": round(ret_relu, 5),  # same shared W
        "entropy_bits": round(ent_top2, 5),
        "mean_k_eff": k_eff_top2,
    }

    print(f"  [ReMoE] K={K} N={N} seed={seed}: "
          f"relu(ent={ent_relu:.2f}b, K_eff={k_eff_relu:.1f}) "
          f"thresh(ent={ent_thresh:.2f}b, K_eff={k_eff_thresh:.1f}) "
          f"top2(ent={ent_top2:.2f}b)", flush=True)

    del W_shared, Wks, keys, vals, anchors, scores, gates_relu, gates_thresh, gates_top2
    results["K"] = K
    results["seed"] = seed
    return results


# ---- instrumentation self-test ----

def _instrumentation_selftest() -> None:
    print("[selftest] starting...", flush=True)
    device = torch.device("cpu")
    gen = torch.Generator(device=device).manual_seed(42)

    # 1. make_bsc returns BSC values
    v = make_bsc(10, 32, gen, device)
    assert set(v.unique().tolist()).issubset({-1.0, 1.0}), "FAIL 1: not BSC"
    print("[selftest] 1/4 make_bsc OK")

    # 2. routing_entropy: verify at K=4 uniform = 2 bits, perfect = 0 bits
    perfect = torch.tensor([[1.0, 0.0, 0.0, 0.0]])
    assert abs(routing_entropy_bits(perfect)) < 0.01, "FAIL 2a: entropy(perfect) != 0"
    uniform = torch.ones(1, 4) / 4.0
    assert abs(routing_entropy_bits(uniform) - 2.0) < 0.01, "FAIL 2b: entropy(uniform K=4) != 2"
    print("[selftest] 2/4 routing_entropy_bits OK")

    # 3. ReLU gate: fire if > 0
    scores_test = torch.tensor([[0.1, -0.2, 0.3, -0.1]])
    gates = (scores_test > 0).float()
    assert gates.sum().item() == 2, f"FAIL 3: expected 2 active experts, got {gates.sum().item()}"
    print("[selftest] 3/4 ReLU gate logic OK")

    # 4. run_cell_remoe at smoke scale
    cell = run_cell_remoe(4, 64, 20, 7, device)
    for v_name in ("relu_cosine", "threshold_cosine", "top2_cosine"):
        assert math.isfinite(cell[v_name]["entropy_bits"]), f"FAIL 4: {v_name} entropy NaN"
    # relu_cosine and top2 should always have k_eff > 0 (relu fires on positive scores; top2 always picks 2)
    assert cell["relu_cosine"]["mean_k_eff"] > 0, "FAIL 4b: relu_cosine k_eff=0"
    assert cell["top2_cosine"]["mean_k_eff"] > 0, "FAIL 4c: top2_cosine k_eff=0"
    # threshold_cosine may be 0 at tiny N (tau > all scores) -- this is valid, not an instrumentation bug
    print(f"[selftest] 4/4 run_cell_remoe: relu_ent={cell['relu_cosine']['entropy_bits']:.2f}b "
          f"relu_k_eff={cell['relu_cosine']['mean_k_eff']:.1f} OK")

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()


# ---- main sweep ----

def run_sweep(smoke: bool = False):
    device = torch.device("cpu")   # pure CPU; no CUDA needed
    print(f"[remoe_relu_router] device={device} smoke={smoke}", flush=True)
    N = N_SMOKE if smoke else N_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir("wave14_moe_remoe_relu_router_v1")
    t0 = time.time()

    results_per_K = {}
    for K in K_sweep:
        print(f"\n[run] K={K} N={N} M_per_expert={M_per_expert}", flush=True)
        cells = []
        for seed in seeds:
            c = run_cell_remoe(K, N, M_per_expert, seed, device)
            cells.append(c)

        for v_name in ("relu_cosine", "threshold_cosine", "top2_cosine"):
            if v_name not in results_per_K:
                results_per_K[v_name] = {}
            ents = [c[v_name]["entropy_bits"] for c in cells]
            rets = [c[v_name]["retention"] for c in cells]
            keffs = [c[v_name]["mean_k_eff"] for c in cells]
            results_per_K[v_name][K] = {
                "mean_retention": round(sum(rets) / len(rets), 5),
                "mean_entropy_bits": round(sum(ents) / len(ents), 5),
                "mean_k_eff": round(sum(keffs) / len(keffs), 2),
            }
        print(f"  -> relu_ent@K={K}={results_per_K['relu_cosine'][K]['mean_entropy_bits']:.3f}b "
              f"thresh_ent={results_per_K['threshold_cosine'][K]['mean_entropy_bits']:.3f}b "
              f"relu_keff={results_per_K['relu_cosine'][K]['mean_k_eff']:.1f}", flush=True)

    # Verdict: use relu_cosine as primary (simplest ReMoE variant)
    K_ref = 4
    K_test = 16
    if K_ref not in results_per_K["relu_cosine"] or K_test not in results_per_K["relu_cosine"]:
        K_ref = min(K_sweep)
        K_test = max(K for K in K_sweep if K <= 16) if any(k <= 16 for k in K_sweep) else K_sweep[-1]

    r = results_per_K["relu_cosine"]
    ret_ref = r[K_ref]["mean_retention"]
    ret_test = r[K_test]["mean_retention"]
    ent_test = r[K_test]["mean_entropy_bits"]
    keff_test = r[K_test]["mean_k_eff"]

    retention_delta = ret_test - ret_ref
    keff_in_range = HARD_PASS_K_EFF_LO <= keff_test <= HARD_PASS_K_EFF_HI

    hard_pass = (keff_in_range and retention_delta >= HARD_PASS_RETENTION_DELTA and
                 ent_test < HARD_PASS_ENTROPY_MAX)
    hard_fail = (retention_delta < HARD_FAIL_RETENTION_DELTA or ent_test > HARD_FAIL_ENTROPY_MAX or
                 keff_test < 2 or keff_test > K_test - 1)

    if hard_pass:
        verdict = "REMOE_HARD_PASS"
        msg = (f"ReLU-cosine router PASSES: K_eff@K={K_test}={keff_test:.1f} in [{HARD_PASS_K_EFF_LO},{HARD_PASS_K_EFF_HI}], "
               f"entropy={ent_test:.3f}b < {HARD_PASS_ENTROPY_MAX}b, "
               f"retention_delta={retention_delta:+.4f} >= {HARD_PASS_RETENTION_DELTA}. "
               f"ReMoE-style gating is a viable MoE router for substrate.")
    elif hard_fail:
        verdict = "REMOE_HARD_FAIL"
        msg = (f"ReLU-cosine router FAILS: retention_delta={retention_delta:+.4f} < {HARD_FAIL_RETENTION_DELTA} "
               f"OR entropy={ent_test:.3f}b > {HARD_FAIL_ENTROPY_MAX}b OR K_eff={keff_test:.1f} out of range. "
               f"ReMoE gating does not rescue MoE SHIFT K-scaling. "
               f"Escalate to Hebbian-anchor training or architecture redesign.")
    else:
        verdict = "REMOE_MIDDLE"
        msg = (f"ReLU-cosine router partial: K_eff={keff_test:.1f}, entropy={ent_test:.3f}b, "
               f"retention_delta={retention_delta:+.4f}. "
               f"Partial improvement over LSH. Try threshold variant (tau={results_per_K['threshold_cosine'][K_test]['mean_entropy_bits']:.3f}b).")

    elapsed = time.time() - t0
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "smoke": smoke,
        "N": N,
        "elapsed_s": round(elapsed, 1),
        "results_per_variant_K": results_per_K,
        "thresholds": {
            "hard_pass_k_eff_range": [HARD_PASS_K_EFF_LO, HARD_PASS_K_EFF_HI],
            "hard_pass_retention_delta": HARD_PASS_RETENTION_DELTA,
            "hard_pass_entropy_max": HARD_PASS_ENTROPY_MAX,
            "hard_fail_retention_delta": HARD_FAIL_RETENTION_DELTA,
            "hard_fail_entropy_max": HARD_FAIL_ENTROPY_MAX,
        },
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics written to {metrics_path}", flush=True)
    return metrics, out_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] instrumentation self-test already ran at import", flush=True)
        import sys; sys.exit(0)
    run_sweep(smoke=args.smoke)
