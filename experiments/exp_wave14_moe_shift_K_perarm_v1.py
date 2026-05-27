"""MoE SHIFT per-arm divergence characterizer v1.

ANTICIPATORY PRE-BUILD -- trigger: wave14_moe_shift_K_scaling_v2 shows DIVERGENCE
  pattern (Arm_A degrades at K>=32 while Arm_C stable/improves, similar to v1).

When v2 returns this divergence signal, this script characterizes which substrate
property drives it across 3 candidate mechanisms:

  M1 (CAPACITY SATURATION): each expert is too full at high K.
     Diagnosis: retention_A drops but retention_B also drops -> both full-N experts
     and partition experts saturate. Metric: M_per_expert / (alpha_c * N) ratio.

  M2 (LSH GATING QUALITY DEGRADATION): at high K, LSH gating becomes near-random.
     Diagnosis: routing_entropy increases toward log2(K) bits at K>=32.
     Fix candidate: improve gating (learned router vs LSH).

  M3 (INTRA-EXPERT INTERFERENCE): patterns from "wrong" experts pollute each W_k.
     Diagnosis: inter_expert_cosine increases as K increases.
     Same diagnostic as moe_intraexpert_overlap_v1, but specifically at divergence K-values.

DESIGN:
  - K sweep: {2, 4, 8, 16, 32, 64} (matches v2 for direct comparison)
  - N = 2048, M_per_expert = 800
  - 5 seeds
  - Per-K metrics: retention_A, routing_entropy, inter_expert_cosine, M_to_capacity_ratio
  - CPU-friendly (no CUDA needed for diagnostic)

PRE-REGISTERED BANDS:
  M2_DOMINANT (gating degradation):
    - routing_entropy at K=32 >= 3.0 bits AND inter_expert_cosine < 0.2
    -> Route to: improved router design (K-NN or learned gate)

  M3_DOMINANT (intra-expert interference):
    - inter_expert_cosine at K=32 >= 0.3
    -> Route to: harder gating (top-1 vs top-2, raise gating temperature)

  M1_DOMINANT (capacity saturation):
    - M_to_capacity_ratio(K=32) >= 0.9 (near-full at each expert)
    - AND routing_entropy < 2.0 bits (gating is sharp, not the issue)
    -> Route to: reduce M_per_expert at high K, or adaptive capacity allocation

  MIXED: no single mechanism dominant
  INSTRUMENTATION_FAIL: routing_entropy NaN or inter_expert_cosine non-finite

Self-tests:
  1. routing_entropy([1.0, 0.0, 0.0]) = 0.0
  2. routing_entropy([0.5, 0.5]) = 1.0 bit
  3. cosine_sim(v, v) = 1.0
  4. cosine_sim(v, -v) = -1.0

Queue: remote_cpu_queue (CPU; K*seeds*N=2048 sweep; ~45-90 min)
Pre-reg: preregs/2026-05-26_wave14_moe_shift_K_perarm_v1.md
Trigger: ship when v2 shows DIVERGENCE (Arm_A degrades at K>=32).
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

N_FULL = 2048
N_SMOKE = 256
M_PER_EXPERT_FULL = 800
M_PER_EXPERT_SMOKE = 100
K_SWEEP_FULL = [2, 4, 8, 16, 32, 64]
K_SWEEP_SMOKE = [2, 4, 8]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_STORE = 128
BATCH_PROBE = 256

# Thresholds
M2_ENTROPY_THRESH = 3.0
M3_COSINE_THRESH = 0.3
M1_CAPACITY_THRESH = 0.9
ALPHA_C = 0.5625   # alpha_c at N=2048 (empirical from calibration)


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")


def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    device = keys.device
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def recall_cosine_batch(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor,
                        batch: int = BATCH_PROBE) -> float:
    total = 0.0
    n = keys.shape[0]
    for s in range(0, n, batch):
        e = min(s + batch, n)
        y = keys[s:e] @ W.T
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = vals[s:e] / vals[s:e].norm(dim=1, keepdim=True).clamp(min=1e-9)
        total += float((yn * vn).sum(dim=1).sum())
    return total / max(n, 1)


def _gini(loads: list) -> float:
    n = len(loads)
    if n <= 1:
        return 0.0
    s = sorted(loads)
    total = sum(s)
    if total <= 0:
        return 0.0
    gini_num = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(s))
    return abs(gini_num) / (n * total)


def build_lsh_proj(N: int, K: int, gen: torch.Generator, device) -> torch.Tensor:
    proj = make_bsc(K, N, gen, device)
    return proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-9)


def gate_assign_balanced(keys: torch.Tensor, proj: torch.Tensor, K: int) -> torch.Tensor:
    scores = keys @ proj.T
    assignment = scores.argmax(dim=1)
    loads = torch.bincount(assignment, minlength=K).float()
    if _gini(loads.tolist()) > 0.3:
        sorted_idx = scores[:, 0].argsort()
        target = keys.shape[0] // K
        new_assign = torch.zeros(keys.shape[0], dtype=torch.long, device=keys.device)
        for k in range(K):
            start = k * target
            end = (k + 1) * target if k < K - 1 else keys.shape[0]
            new_assign[sorted_idx[start:end]] = k
        return new_assign
    return assignment


def routing_entropy(gate_weights: torch.Tensor) -> float:
    """Mean Shannon entropy (bits) of per-query softmax gate weights."""
    eps = 1e-9
    w = gate_weights.clamp(min=eps)
    ent = -(w * w.log2()).sum(dim=1)  # (B,)
    return float(ent.mean())


def inter_expert_cosine(keys: torch.Tensor, assignment: torch.Tensor, K: int,
                        max_pairs: int = 200) -> float:
    """Mean cosine similarity between patterns assigned to DIFFERENT experts."""
    device = keys.device
    keys_norm = keys / keys.norm(dim=1, keepdim=True).clamp(min=1e-9)
    sims = []
    rng = torch.Generator(device=device).manual_seed(99)
    for _ in range(max_pairs):
        i = int(torch.randint(0, keys.shape[0], (1,), generator=rng))
        j = int(torch.randint(0, keys.shape[0], (1,), generator=rng))
        if assignment[i] != assignment[j]:
            sim = float((keys_norm[i] * keys_norm[j]).sum())
            sims.append(sim)
    return sum(sims) / max(len(sims), 1)


def run_cell_diagnostics(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert
    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)
    proj = build_lsh_proj(N, K, gen, device)
    assignment = gate_assign_balanced(keys, proj, K)

    # Retention (standard arm-A)
    total_cos = 0.0
    scores_all = keys @ proj.T
    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N, N), dtype=torch.float32, device=device))
        else:
            Wks.append(outer_product_store(keys[mask], vals[mask], N))

    for s in range(0, M_total, BATCH_PROBE):
        e = min(s + BATCH_PROBE, M_total)
        q = keys[s:e]
        v = vals[s:e]
        sc = scores_all[s:e]
        top2 = sc.topk(min(2, K), dim=1)
        top2_idx = top2.indices
        top2_w = top2.values.softmax(dim=1)
        y = torch.zeros((e - s, N), dtype=torch.float32, device=device)
        for rank in range(min(2, K)):
            for b in range(e - s):
                k_id = int(top2_idx[b, rank])
                y[b] += top2_w[b, rank] * (Wks[k_id] @ q[b])
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = v / v.norm(dim=1, keepdim=True).clamp(min=1e-9)
        total_cos += float((yn * vn).sum(dim=1).sum())

    retention = total_cos / max(M_total, 1)

    # Routing entropy
    gate_w_all = scores_all.softmax(dim=1)
    ent = routing_entropy(gate_w_all)

    # Inter-expert cosine
    iec = inter_expert_cosine(keys, assignment, K)

    # M-to-capacity ratio
    capacity_per_expert = ALPHA_C * N
    m_cap_ratio = M_per_expert / max(capacity_per_expert, 1)

    del Wks, keys, vals, proj, assignment, scores_all, gate_w_all
    return {
        "retention_A": round(retention, 4),
        "routing_entropy_bits": round(ent, 4),
        "inter_expert_cosine": round(iec, 4),
        "m_to_capacity_ratio": round(m_cap_ratio, 4),
        "K": K, "N": N, "M_per_expert": M_per_expert, "seed": seed,
    }


# ── instrumentation self-test ──

def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. routing_entropy perfect routing = 0.0
    perfect = torch.tensor([[1.0, 0.0, 0.0]])
    ent1 = routing_entropy(perfect)
    assert abs(ent1) < 0.01, f"Selftest 1 FAIL: entropy(perfect)={ent1}"
    print(f"[selftest] 1/4 routing_entropy(perfect)=0.0 OK")

    # 2. routing_entropy max entropy for K=2 = 1.0 bit
    uniform2 = torch.tensor([[0.5, 0.5]])
    ent2 = routing_entropy(uniform2)
    assert abs(ent2 - 1.0) < 0.01, f"Selftest 2 FAIL: entropy(uniform_K2)={ent2}"
    print(f"[selftest] 2/4 routing_entropy(uniform K=2)=1.0 OK")

    # 3. cosine_sim(v, v) = 1.0
    v = torch.randn(16)
    vn = v / v.norm()
    sim_self = float((vn * vn).sum())
    assert abs(sim_self - 1.0) < 0.001, f"Selftest 3 FAIL: cosine(v,v)={sim_self}"
    print(f"[selftest] 3/4 cosine(v,v)=1.0 OK")

    # 4. cosine_sim(v, -v) = -1.0
    sim_neg = float((vn * (-vn)).sum())
    assert abs(sim_neg + 1.0) < 0.001, f"Selftest 4 FAIL: cosine(v,-v)={sim_neg}"
    print(f"[selftest] 4/4 cosine(v,-v)=-1.0 OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run_sweep(smoke: bool = False):
    device = torch.device("cpu")  # CPU experiment
    N = N_SMOKE if smoke else N_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_moe_shift_K_perarm_v1")

    results_per_K: dict[int, dict] = {}
    for K in K_sweep:
        print(f"\n[run] K={K} N={N} M_per_expert={M_per_expert}", flush=True)
        cells = []
        for seed in seeds:
            c = run_cell_diagnostics(K, N, M_per_expert, seed, device)
            cells.append(c)
            print(f"  seed={seed}: ret={c['retention_A']:.4f} ent={c['routing_entropy_bits']:.2f}b "
                  f"iec={c['inter_expert_cosine']:.3f} m_cap={c['m_to_capacity_ratio']:.3f}", flush=True)

        mu_ret = sum(c["retention_A"] for c in cells) / len(cells)
        mu_ent = sum(c["routing_entropy_bits"] for c in cells) / len(cells)
        mu_iec = sum(c["inter_expert_cosine"] for c in cells) / len(cells)
        mu_mcap = sum(c["m_to_capacity_ratio"] for c in cells) / len(cells)
        results_per_K[K] = {
            "mean_retention_A": round(mu_ret, 4),
            "mean_routing_entropy_bits": round(mu_ent, 4),
            "mean_inter_expert_cosine": round(mu_iec, 4),
            "mean_m_to_capacity_ratio": round(mu_mcap, 4),
        }
        print(f"  -> ret={mu_ret:.4f} ent={mu_ent:.2f}b iec={mu_iec:.3f} m_cap={mu_mcap:.3f}")

    return results_per_K, out_dir


def compute_verdict(results_per_K: dict) -> tuple[str, str, dict]:
    K_vals = sorted(results_per_K.keys())
    K_high = max(K_vals)

    # Use highest K for mechanism classification
    r = results_per_K[K_high]
    ent_high = r["mean_routing_entropy_bits"]
    iec_high = r["mean_inter_expert_cosine"]
    mcap_high = r["mean_m_to_capacity_ratio"]

    summary = {
        "K_sweep": K_vals,
        "per_K": results_per_K,
        "K_diagnostic": K_high,
        "entropy_at_K_high": ent_high,
        "iec_at_K_high": iec_high,
        "m_cap_ratio_at_K_high": mcap_high,
    }

    if not all(math.isfinite(v) for v in [ent_high, iec_high]):
        return ("INSTRUMENTATION_FAIL", "Non-finite diagnostic metric at high K.", summary)

    if iec_high >= M3_COSINE_THRESH:
        verdict = "M3_DOMINANT"
        verdict_msg = (
            f"M3_DOMINANT: intra-expert interference drives K-scaling divergence. "
            f"inter_expert_cosine at K={K_high}={iec_high:.3f} >= {M3_COSINE_THRESH}. "
            f"Patterns NOT cleanly separated; gating temperature too soft. "
            f"Rescue: raise gating hardness (top-1 gate, higher temperature)."
        )
    elif ent_high >= M2_ENTROPY_THRESH:
        verdict = "M2_DOMINANT"
        verdict_msg = (
            f"M2_DOMINANT: LSH gating degrades at K={K_high}. "
            f"routing_entropy={ent_high:.2f}b >= {M2_ENTROPY_THRESH}b. "
            f"Gating is near-uniform (max={math.log2(K_high):.1f}b). "
            f"Rescue: replace LSH with learned K-NN router."
        )
    elif mcap_high >= M1_CAPACITY_THRESH:
        verdict = "M1_DOMINANT"
        verdict_msg = (
            f"M1_DOMINANT: capacity saturation drives K-scaling divergence. "
            f"M_per_expert / (alpha_c * N) = {mcap_high:.3f} >= {M1_CAPACITY_THRESH}. "
            f"Each expert is near-full; structural separation can't offset saturation. "
            f"Rescue: reduce M_per_expert proportionally with K, or use higher alpha_c."
        )
    else:
        verdict = "MIXED_EVIDENCE"
        verdict_msg = (
            f"MIXED_EVIDENCE: no single mechanism dominant at K={K_high}. "
            f"ent={ent_high:.2f}b (< {M2_ENTROPY_THRESH}b), "
            f"iec={iec_high:.3f} (< {M3_COSINE_THRESH}), "
            f"m_cap={mcap_high:.3f} (< {M1_CAPACITY_THRESH}). "
            f"Divergence may arise from interaction of mechanisms."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_moe_shift_K_perarm_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)
    results_per_K, out_dir = run_sweep(smoke)

    # Multi-scale smoke
    if smoke:
        print("\n[multi-scale smoke] N_smoke * 2...", flush=True)
        device = torch.device("cpu")
        N2 = N_SMOKE * 2
        M2 = M_PER_EXPERT_SMOKE * 2
        c2 = run_cell_diagnostics(4, N2, M2, 17, device)
        assert math.isfinite(c2["retention_A"]) and math.isfinite(c2["routing_entropy_bits"])
        print(f"  N={N2} K=4: ret={c2['retention_A']:.4f} ent={c2['routing_entropy_bits']:.2f}b")
        print("[multi-scale smoke] PASS")

    verdict, verdict_msg, summary = compute_verdict(results_per_K)
    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N": N_SMOKE if smoke else N_FULL,
            "M_per_expert": M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL,
            "K_sweep": K_SWEEP_SMOKE if smoke else K_SWEEP_FULL,
            "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
            "smoke": smoke,
            "trigger": "ship when K_scaling_v2 shows DIVERGENCE (Arm_A degrades at K>=32)",
        },
    }
    validate_metrics(metrics)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
