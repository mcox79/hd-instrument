"""MoE cosine-dot router K=32/64/128 stress test v2.

TRIGGER: exp_wave14_moe_cosine_router_v1 returns COSINE_ROUTER_HARD_PASS
  (routing_entropy@K=16 < 2.0b AND retention@K=16 >= retention@K=4 - 0.005).

CONTEXT: v1 tested cosine-dot routing at K in {4, 8, 16, 32}. If it passes,
  this v2 pushes to K in {32, 64, 128} to determine whether the router extends
  the MoE K-scaling ceiling all the way to K=128.

DESIGN (reuses v1 infrastructure):
  - K sweep: {32, 64, 128} (extreme-K stress; overlap at K=32 for continuity)
  - N = 4096 (same as v1)
  - M_per_expert = 800 (same as v1; total M scales with K)
  - 3 seeds
  - Router: cosine-dot top-1 (v1 base) + Expert-Choice variant (see below)
  - Anchor types: (a) random BSC, (b) Hebbian-trained (bundle of first M/K stored)

ROUTER UPGRADE FROM V1:
  - v1 used token-choice (each query argmaxes over K experts).
  - v2 adds Expert-Choice: each expert selects its top ceil(M_total/K) queries.
  - Expert-Choice is load-balanced by design; expected entropy lower than token-choice.
  - Both variants reported; PASS is on the better-performing variant.

PRE-REGISTERED BANDS:
  HARD-PASS (K-ceiling extends to K=128):
    - BEST VARIANT retention@K=128 >= retention@K=32 * 0.95 (< 5% degradation across 4x K range)
    - AND routing_entropy@K=128 < 3.0b (doesn't collapse to LSH baseline)

  HARD-FAIL (K-ceiling is below K=64):
    - retention@K=64 < retention@K=32 - 0.015 (sharp degradation at K=64)
    - OR routing_entropy@K=64 > 4.0b (entropy recovers to near-maximum)

  MIDDLE:
    - K=64 OK but K=128 degrades > 5%
    -> Report: cosine-dot extends ceiling to K=64 but not K=128.

Queue: overnight_queue (GPU; M_total = 128 * 800 = 102400 patterns at K=128 is GPU-only)
Pre-reg: preregs/2026-05-27_wave14_moe_cosine_router_v2_k_stress.md
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
K_SWEEP_FULL = [32, 64, 128]
K_SWEEP_SMOKE = [8, 16, 32]  # scaled down for smoke
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
BATCH_STORE = 128
BATCH_PROBE = 256

# Pre-registered thresholds
HARD_PASS_RETENTION_FRAC = 0.95   # K=128 >= K=32 * 0.95
HARD_FAIL_RETENTION_DELTA = -0.015   # K=64 < K=32 - 0.015
HARD_PASS_ENTROPY_K128 = 3.0
HARD_FAIL_ENTROPY_K64 = 4.0


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


def build_cosine_anchors(K: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    raw = torch.randn(K, N, generator=gen, device=device)
    return raw.sign()


def build_hebbian_anchors(K: int, N: int, keys: torch.Tensor, assignment: torch.Tensor) -> torch.Tensor:
    """Hebbian anchors: bundle of patterns assigned to each expert."""
    anchors = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() > 0:
            bundle = keys[mask].mean(dim=0).sign()
        else:
            bundle = torch.zeros(N, device=keys.device)
        anchors.append(bundle)
    return torch.stack(anchors)


def gate_token_choice(keys: torch.Tensor, anchors: torch.Tensor) -> tuple:
    """Token-choice top-1 cosine routing."""
    N = keys.shape[1]
    scores = (keys @ anchors.T) / N
    assignment = scores.argmax(dim=1)
    return assignment, scores


def gate_expert_choice(keys: torch.Tensor, anchors: torch.Tensor, K: int) -> tuple:
    """Expert-Choice: each expert selects its top ceil(M/K) queries."""
    M, N = keys.shape
    capacity = math.ceil(M / K)
    scores = (keys @ anchors.T) / N   # (M, K)
    # Each expert picks its top-C
    assignment = torch.full((M,), -1, dtype=torch.long, device=keys.device)
    for k in range(K):
        topk_ids = scores[:, k].topk(min(capacity, M)).indices
        assignment[topk_ids] = k
    # Any unassigned -> token-choice fallback
    unassigned = (assignment == -1)
    if unassigned.any():
        assignment[unassigned] = scores[unassigned].argmax(dim=1)
    return assignment, scores


def compute_retention_from_routing(keys: torch.Tensor, vals: torch.Tensor,
                                   assignment: torch.Tensor, K: int, N: int) -> float:
    """Build per-expert Ws and compute mean retrieval retention."""
    M_total = keys.shape[0]
    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N, N), dtype=torch.float32, device=keys.device))
        else:
            Wks.append(outer_product_store(keys[mask], vals[mask], N))

    total_cos = 0.0
    for s in range(0, M_total, BATCH_PROBE):
        e = min(s + BATCH_PROBE, M_total)
        q = keys[s:e]
        v = vals[s:e]
        k_ids = assignment[s:e]
        ys = []
        for bi in range(e - s):
            k_id = int(k_ids[bi])
            ys.append(Wks[k_id] @ q[bi])
        y = torch.stack(ys)
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = v / v.norm(dim=1, keepdim=True).clamp(min=1e-9)
        total_cos += float((yn * vn).sum(dim=1).sum())

    del Wks
    return total_cos / max(M_total, 1)


def run_cell_k_stress(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    """Run one diagnostic cell for K-stress test: both token-choice and expert-choice."""
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert

    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)

    # --- Token-choice with random BSC anchors ---
    anchor_gen = torch.Generator(device=device).manual_seed(seed + 10000)
    anchors_rand = build_cosine_anchors(K, N, anchor_gen, device)
    assignment_tc, scores_tc = gate_token_choice(keys, anchors_rand)
    ret_tc = compute_retention_from_routing(keys, vals, assignment_tc, K, N)
    ent_tc = routing_entropy_bits(scores_tc.softmax(dim=1))
    k_eff_tc = int((torch.bincount(assignment_tc, minlength=K) > 0).sum())

    # --- Expert-Choice with random BSC anchors ---
    assignment_ec, scores_ec = gate_expert_choice(keys, anchors_rand, K)
    ret_ec = compute_retention_from_routing(keys, vals, assignment_ec, K, N)
    ent_ec = routing_entropy_bits(scores_ec.softmax(dim=1))
    k_eff_ec = int((torch.bincount(assignment_ec.clamp(min=0), minlength=K) > 0).sum())

    # --- Hebbian anchors (token-choice) ---
    anchors_hebb = build_hebbian_anchors(K, N, keys, assignment_tc)
    assignment_hebb, scores_hebb = gate_token_choice(keys, anchors_hebb)
    ret_hebb = compute_retention_from_routing(keys, vals, assignment_hebb, K, N)
    ent_hebb = routing_entropy_bits(scores_hebb.softmax(dim=1))

    del keys, vals, anchors_rand, anchors_hebb
    del scores_tc, scores_ec, scores_hebb

    return {
        "K": K, "N": N, "M_per_expert": M_per_expert, "seed": seed,
        "token_choice": {
            "retention": round(ret_tc, 5),
            "entropy_bits": round(ent_tc, 5),
            "k_eff": k_eff_tc,
        },
        "expert_choice": {
            "retention": round(ret_ec, 5),
            "entropy_bits": round(ent_ec, 5),
            "k_eff": k_eff_ec,
        },
        "hebbian_tc": {
            "retention": round(ret_hebb, 5),
            "entropy_bits": round(ent_hebb, 5),
        },
    }


# ---- instrumentation self-test ----

def _instrumentation_selftest() -> None:
    print("[selftest] starting...", flush=True)
    device = torch.device("cpu")
    gen = torch.Generator(device=device).manual_seed(42)

    # 1. build_cosine_anchors: (K, N) shape
    anchors = build_cosine_anchors(4, 64, gen, device)
    assert anchors.shape == (4, 64), f"FAIL 1: shape={anchors.shape}"
    assert set(anchors.unique().tolist()).issubset({-1.0, 1.0}), "FAIL 1b: not BSC"
    print("[selftest] 1/5 build_cosine_anchors OK")

    # 2. gate_token_choice: assignments in [0, K)
    gen2 = torch.Generator(device=device).manual_seed(7)
    keys_t = make_bsc(20, 64, gen2, device)
    assignment, scores = gate_token_choice(keys_t, anchors)
    assert assignment.shape == (20,), f"FAIL 2: shape={assignment.shape}"
    assert int(assignment.min()) >= 0 and int(assignment.max()) < 4, "FAIL 2b: out of range"
    print("[selftest] 2/5 gate_token_choice OK")

    # 3. gate_expert_choice: all assignments in [0, K)
    assignment_ec, scores_ec = gate_expert_choice(keys_t, anchors, 4)
    assert assignment_ec.shape == (20,), f"FAIL 3: shape={assignment_ec.shape}"
    assert int(assignment_ec.min()) >= 0 and int(assignment_ec.max()) < 4, "FAIL 3b: out of range"
    print("[selftest] 3/5 gate_expert_choice OK")

    # 4. routing_entropy: max at uniform
    uniform = torch.ones(1, 4) / 4.0
    ent = routing_entropy_bits(uniform)
    assert abs(ent - 2.0) < 0.01, f"FAIL 4: entropy(uniform K=4)={ent}"
    print("[selftest] 4/5 routing_entropy_bits OK")

    # 5. run_cell_k_stress: finite metrics, k_eff > 0
    cell = run_cell_k_stress(4, 64, 20, 7, device)
    assert math.isfinite(cell["token_choice"]["retention"]), "FAIL 5a: tc retention NaN"
    assert math.isfinite(cell["expert_choice"]["retention"]), "FAIL 5b: ec retention NaN"
    assert cell["token_choice"]["k_eff"] > 0, "FAIL 5c: k_eff=0"
    print(f"[selftest] 5/5 run_cell_k_stress: tc_ret={cell['token_choice']['retention']:.4f} "
          f"ec_ret={cell['expert_choice']['retention']:.4f} OK")

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()


# ---- main sweep ----

def run_sweep(smoke: bool = False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[cosine_router_v2_k_stress] device={device} smoke={smoke}", flush=True)
    N = N_SMOKE if smoke else N_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir("wave14_moe_cosine_router_v2_k_stress")
    t0 = time.time()

    results_per_K = {}
    for K in K_sweep:
        print(f"\n[run] K={K} N={N} M_per_expert={M_per_expert}", flush=True)
        cells = []
        for seed in seeds:
            c = run_cell_k_stress(K, N, M_per_expert, seed, device)
            cells.append(c)
            tc = c["token_choice"]
            ec = c["expert_choice"]
            hebb = c["hebbian_tc"]
            print(f"  seed={seed}: TC ret={tc['retention']:.5f} ent={tc['entropy_bits']:.3f}b | "
                  f"EC ret={ec['retention']:.5f} ent={ec['entropy_bits']:.3f}b | "
                  f"Hebb ret={hebb['retention']:.5f} ent={hebb['entropy_bits']:.3f}b", flush=True)

        # Aggregate: pick best variant per cell
        for variant in ("token_choice", "expert_choice", "hebbian_tc"):
            rets = [c[variant]["retention"] for c in cells]
            ents = [c[variant]["entropy_bits"] for c in cells]
            mu_ret = sum(rets) / len(rets)
            mu_ent = sum(ents) / len(ents)
            if variant not in results_per_K:
                results_per_K[variant] = {}
            results_per_K[variant][K] = {
                "mean_retention": round(mu_ret, 5),
                "mean_entropy_bits": round(mu_ent, 5),
                "n_seeds": len(cells),
            }
        print(f"  -> TC mean_ret={results_per_K['token_choice'][K]['mean_retention']:.5f} "
              f"EC mean_ret={results_per_K['expert_choice'][K]['mean_retention']:.5f}", flush=True)

    # Verdict: use best variant at each K
    K_min = min(K_sweep)
    K_mid = K_sweep[1] if len(K_sweep) > 1 else K_min
    K_max = max(K_sweep)

    # Find best variant: highest mean retention at K_min
    best_variant = max(["token_choice", "expert_choice", "hebbian_tc"],
                       key=lambda v: results_per_K[v][K_min]["mean_retention"])

    ret_kmin = results_per_K[best_variant][K_min]["mean_retention"]
    ret_kmax = results_per_K[best_variant].get(K_max, {}).get("mean_retention", 0.0)
    ent_kmax = results_per_K[best_variant].get(K_max, {}).get("mean_entropy_bits", 9.9)
    ret_kmid = results_per_K[best_variant].get(K_mid, {}).get("mean_retention", ret_kmin)
    ret_delta_mid = ret_kmid - ret_kmin

    # Verdict conditions (relative to K_min, which is K=32)
    hard_pass = (ret_kmax >= ret_kmin * HARD_PASS_RETENTION_FRAC and ent_kmax < HARD_PASS_ENTROPY_K128)
    hard_fail = (ret_delta_mid < HARD_FAIL_RETENTION_DELTA or
                 (K_mid in results_per_K[best_variant] and
                  results_per_K[best_variant][K_mid]["mean_entropy_bits"] > HARD_FAIL_ENTROPY_K64))

    if hard_pass:
        verdict = "COSINE_ROUTER_K_STRESS_HARD_PASS"
        msg = (f"Cosine-dot router extends K-ceiling to K={K_max}: "
               f"retention@K={K_max}={ret_kmax:.4f} >= "
               f"retention@K={K_min}={ret_kmin:.4f} * {HARD_PASS_RETENTION_FRAC:.2f}. "
               f"Best variant: {best_variant}. "
               f"entropy@K={K_max}={ent_kmax:.3f}b < {HARD_PASS_ENTROPY_K128:.1f}b threshold.")
    elif hard_fail:
        verdict = "COSINE_ROUTER_K_STRESS_HARD_FAIL"
        msg = (f"Cosine-dot router fails at K={K_mid}: "
               f"delta_ret={ret_delta_mid:.4f} < {HARD_FAIL_RETENTION_DELTA:.3f} threshold. "
               f"K-ceiling is below K={K_mid}. Best variant: {best_variant}.")
    else:
        verdict = "COSINE_ROUTER_K_STRESS_MIDDLE"
        msg = (f"Cosine-dot router partial extension: K={K_mid} OK but K={K_max} degrades. "
               f"Report: ceiling extended to K={K_mid} but not K={K_max}. "
               f"Best variant: {best_variant}.")

    elapsed = time.time() - t0
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "smoke": smoke,
        "N": N,
        "best_variant": best_variant,
        "elapsed_s": round(elapsed, 1),
        "results_per_variant_K": results_per_K,
        "thresholds": {
            "hard_pass_retention_frac": HARD_PASS_RETENTION_FRAC,
            "hard_fail_retention_delta": HARD_FAIL_RETENTION_DELTA,
            "hard_pass_entropy_kmax": HARD_PASS_ENTROPY_K128,
            "hard_fail_entropy_kmid": HARD_FAIL_ENTROPY_K64,
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
    args = parser.parse_args()
    run_sweep(smoke=args.smoke)
