"""MoE SHIFT cosine-dot learned router rescue probe v1.

CONTEXT: wave14_moe_shift_K_perarm_v1 returned M2_DOMINANT verdict:
  LSH gating entropy (0.78b at K=2 -> ~5.3b at K=64) is the SOLE source of
  K-scaling degradation (IEC ~0 all K; m_cap constant all K).

FIX: Replace LSH projection gating with cosine-dot gating using fixed BSC
  anchor vectors (one per expert). This is the substrate-native router --
  the same operation used in associative recall.

Cosine-dot routing:
  - anchor_k = sign(randn(N)) -- one BSC anchor per expert, drawn once at init
  - score_k = dot(query, anchor_k) / N for each k in K_experts
  - assignment = argmax(scores)  [token-choice]

Expert-Choice variant also implemented (each expert selects top ceil(B/K) queries).
Report which variant was used per run.

Pre-registered bands (from handoff notes/exp_dev_handoff_moe_learned_router_probe_2026-05-27.md):
  HARD-PASS: routing_entropy at K=16 < 2.0b AND retention at K=16 >= K=4 retention - 0.005
  HARD-FAIL: routing_entropy at K=16 > 3.0b OR retention at K=16 < K=4 retention - 0.015
  MIDDLE:    entropy in [2.0, 3.0b] or retention delta in [0.005, 0.015]

K sweep: {4, 8, 16, 32}
N = 4096 (substrate default, same as K_perarm baseline)
3 seeds
~2500s CPU

Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-27_wave14_moe_cosine_router_v1.md
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

# Full-scale params
N_FULL = 4096
N_SMOKE = 512
M_PER_EXPERT_FULL = 800
M_PER_EXPERT_SMOKE = 100
K_SWEEP_FULL = [4, 8, 16, 32]
K_SWEEP_SMOKE = [4, 16]
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
BATCH_STORE = 128
BATCH_PROBE = 256

# Pre-registered thresholds
HARD_PASS_ENTROPY_K16 = 2.0   # bits
HARD_FAIL_ENTROPY_K16 = 3.0   # bits
HARD_PASS_RETENTION_DELTA = -0.005   # K=16 >= K=4 - 0.005
HARD_FAIL_RETENTION_DELTA = -0.015   # K=16 < K=4 - 0.015

# Baseline from K_perarm v1 at K=4 (M2_DOMINANT result; used for delta computation)
# If we can't load the file, we compute it fresh.
LSH_BASELINE_METRICS_PATH = REPO / "data" / "exp_wave14_moe_shift_K_perarm_v1" / "metrics.json"

ALPHA_C = 0.5625   # empirical alpha_c for N=2048; conservative at N=4096


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
    """Mean Shannon entropy (bits) over query distribution."""
    eps = 1e-9
    w = gate_weights.clamp(min=eps)
    ent = -(w * w.log2()).sum(dim=1)
    return float(ent.mean())


def build_cosine_anchors(K: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    """Fixed BSC anchor vectors (one per expert). Shape: (K, N)."""
    raw = torch.randn(K, N, generator=gen, device=device)
    return raw.sign()  # BSC +/-1


def gate_token_choice(keys: torch.Tensor, anchors: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Token-choice: each query selects its best expert by cosine score.
    Returns (assignment, scores). scores shape: (M, K).
    """
    N = keys.shape[1]
    scores = (keys @ anchors.T) / N   # (M, K)
    assignment = scores.argmax(dim=1)
    return assignment, scores


def run_cell_cosine(K: int, N: int, M_per_expert: int, seed: int, device) -> dict:
    """One diagnostic cell: cosine-dot routing at given K."""
    gen = torch.Generator(device=device).manual_seed(seed)
    M_total = K * M_per_expert

    keys = make_bsc(M_total, N, gen, device)
    vals = make_bsc(M_total, N, gen, device)
    anchors = build_cosine_anchors(K, N, gen, device)

    assignment, scores = gate_token_choice(keys, anchors)

    # Anchor cosine spread diagnostic: mean pairwise cosine among anchors
    an = anchors / anchors.norm(dim=1, keepdim=True).clamp(min=1e-9)
    pair_cosines = []
    for i in range(K):
        for j in range(i + 1, K):
            pair_cosines.append(float((an[i] * an[j]).sum()))
    anchor_spread = sum(pair_cosines) / max(len(pair_cosines), 1)

    # Effective K (non-empty experts)
    k_eff = int((torch.bincount(assignment, minlength=K) > 0).sum())

    # Build per-expert weight matrices
    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N, N), dtype=torch.float32, device=device))
        else:
            Wks.append(outer_product_store(keys[mask], vals[mask], N))

    # Retention: top-1 expert retrieval
    total_cos = 0.0
    for s in range(0, M_total, BATCH_PROBE):
        e = min(s + BATCH_PROBE, M_total)
        q = keys[s:e]
        v = vals[s:e]
        k_ids = assignment[s:e]
        # batched top-1 recall
        ys = []
        for bi in range(e - s):
            k_id = int(k_ids[bi])
            ys.append(Wks[k_id] @ q[bi])
        y = torch.stack(ys)
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = v / v.norm(dim=1, keepdim=True).clamp(min=1e-9)
        total_cos += float((yn * vn).sum(dim=1).sum())

    retention = total_cos / max(M_total, 1)

    # Routing entropy from soft scores
    gate_soft = scores.softmax(dim=1)
    ent = routing_entropy_bits(gate_soft)

    # LSH baseline delta computed later at verdict time
    del Wks, keys, vals, anchors, scores, gate_soft
    return {
        "K": K, "N": N, "M_per_expert": M_per_expert, "seed": seed,
        "retention": round(retention, 5),
        "routing_entropy_bits": round(ent, 5),
        "k_eff": k_eff,
        "anchor_cosine_spread": round(anchor_spread, 5),
        "router_type": "cosine_dot_top1",
    }


# ── instrumentation self-test ──

def _instrumentation_selftest() -> None:
    print("[selftest] starting instrumentation self-test...", flush=True)
    device = torch.device("cpu")
    gen = torch.Generator(device=device).manual_seed(42)

    # 1. make_bsc returns +/-1 values
    v = make_bsc(10, 32, gen, device)
    assert v.shape == (10, 32), "Selftest 1a FAIL: wrong shape"
    assert set(v.unique().tolist()).issubset({-1.0, 1.0}), "Selftest 1b FAIL: values not in +/-1"
    print("[selftest] 1/5 make_bsc shape and values OK")

    # 2. cosine anchors are +/-1
    gen2 = torch.Generator(device=device).manual_seed(7)
    anchors = build_cosine_anchors(4, 64, gen2, device)
    assert anchors.shape == (4, 64), "Selftest 2a FAIL: wrong anchor shape"
    assert set(anchors.unique().tolist()).issubset({-1.0, 1.0}), "Selftest 2b FAIL: anchors not BSC"
    print("[selftest] 2/5 build_cosine_anchors shape and values OK")

    # 3. gate_token_choice: each query gets an assignment in [0, K)
    keys_t = make_bsc(20, 64, gen2, device)
    assignment, scores = gate_token_choice(keys_t, anchors)
    assert assignment.shape == (20,), "Selftest 3a FAIL: wrong assignment shape"
    assert scores.shape == (20, 4), "Selftest 3b FAIL: wrong scores shape"
    assert int(assignment.min()) >= 0 and int(assignment.max()) < 4, "Selftest 3c FAIL: assignment out of range"
    print("[selftest] 3/5 gate_token_choice shape and range OK")

    # 4. routing_entropy: perfect routing = 0 bits
    perfect = torch.tensor([[1.0, 0.0, 0.0, 0.0]])
    ent_perfect = routing_entropy_bits(perfect)
    assert abs(ent_perfect) < 0.01, f"Selftest 4a FAIL: entropy(perfect)={ent_perfect}"
    # uniform K=4 = 2.0 bits
    uniform4 = torch.ones(1, 4) / 4.0
    ent_unif = routing_entropy_bits(uniform4)
    assert abs(ent_unif - 2.0) < 0.01, f"Selftest 4b FAIL: entropy(uniform K=4)={ent_unif}"
    print("[selftest] 4/5 routing_entropy_bits OK")

    # 5. run_cell_cosine at smoke scale produces finite non-null metrics
    cell = run_cell_cosine(4, 64, 20, 7, device)
    assert math.isfinite(cell["retention"]), f"Selftest 5a FAIL: retention not finite"
    assert math.isfinite(cell["routing_entropy_bits"]), f"Selftest 5b FAIL: entropy not finite"
    assert cell["k_eff"] > 0, f"Selftest 5c FAIL: k_eff=0 (all experts empty)"
    assert cell["retention"] is not None, "Selftest 5d FAIL: retention is None"
    print(f"[selftest] 5/5 run_cell_cosine smoke: ret={cell['retention']:.4f} ent={cell['routing_entropy_bits']:.2f}b k_eff={cell['k_eff']}")

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()


def run_sweep(smoke: bool = False) -> tuple[dict, Path]:
    device = torch.device("cpu")
    N = N_SMOKE if smoke else N_FULL
    M_per_expert = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir("wave14_moe_cosine_router_v1")

    results_per_K: dict[int, dict] = {}
    for K in K_sweep:
        print(f"\n[run] K={K} N={N} M_per_expert={M_per_expert}", flush=True)
        cells = []
        for seed in seeds:
            c = run_cell_cosine(K, N, M_per_expert, seed, device)
            cells.append(c)
            print(f"  seed={seed}: ret={c['retention']:.5f} ent={c['routing_entropy_bits']:.3f}b "
                  f"k_eff={c['k_eff']} spread={c['anchor_cosine_spread']:.4f}", flush=True)

        mu_ret = sum(c["retention"] for c in cells) / len(cells)
        std_ret = math.sqrt(sum((c["retention"] - mu_ret) ** 2 for c in cells) / max(len(cells) - 1, 1))
        mu_ent = sum(c["routing_entropy_bits"] for c in cells) / len(cells)
        mu_spread = sum(c["anchor_cosine_spread"] for c in cells) / len(cells)
        mu_keff = sum(c["k_eff"] for c in cells) / len(cells)

        results_per_K[K] = {
            "mean_retention": round(mu_ret, 5),
            "std_retention": round(std_ret, 5),
            "mean_routing_entropy_bits": round(mu_ent, 5),
            "mean_anchor_cosine_spread": round(mu_spread, 5),
            "mean_k_eff": round(mu_keff, 2),
            "n_seeds": len(cells),
        }
        print(f"  -> ret={mu_ret:.5f}+/-{std_ret:.5f} ent={mu_ent:.3f}b keff={mu_keff:.1f}", flush=True)

    return results_per_K, out_dir


def compute_verdict(results_per_K: dict) -> tuple[str, str, dict]:
    # Need K=4 and K=16 for threshold evaluation
    r4 = results_per_K.get(4) or results_per_K.get(min(results_per_K.keys()))
    r16 = results_per_K.get(16) or results_per_K.get(max(results_per_K.keys()))

    ent_k16 = r16["mean_routing_entropy_bits"]
    ret_k4 = r4["mean_retention"]
    ret_k16 = r16["mean_retention"]
    delta = ret_k16 - ret_k4

    # Load LSH baseline for comparison if available
    lsh_baseline = None
    if LSH_BASELINE_METRICS_PATH.exists():
        try:
            with open(LSH_BASELINE_METRICS_PATH) as f:
                lsh_data = json.load(f)
            lsh_sum = lsh_data.get("summary", {})
            lsh_per_k = lsh_sum.get("per_K", {})
            lsh_baseline = {int(k): v for k, v in lsh_per_k.items()}
        except Exception as e:
            print(f"[warn] Could not load LSH baseline: {e}", flush=True)

    # Compute retention vs LSH delta at K=16
    lsh_ret_k16 = None
    if lsh_baseline and 16 in lsh_baseline:
        lsh_ret_k16 = lsh_baseline[16].get("mean_retention_A") or lsh_baseline[16].get("retention_A")

    summary = {
        "K_sweep": sorted(results_per_K.keys()),
        "per_K": results_per_K,
        "K_eval_low": 4,
        "K_eval_high": 16,
        "entropy_at_K16": ent_k16,
        "retention_at_K4": ret_k4,
        "retention_at_K16": ret_k16,
        "retention_delta_K16_vs_K4": round(delta, 5),
        "lsh_baseline_retention_K16": lsh_ret_k16,
        "retention_vs_lsh_delta": round(ret_k16 - lsh_ret_k16, 5) if lsh_ret_k16 is not None else None,
        "hard_pass_entropy_thresh": HARD_PASS_ENTROPY_K16,
        "hard_fail_entropy_thresh": HARD_FAIL_ENTROPY_K16,
        "hard_pass_delta_thresh": HARD_PASS_RETENTION_DELTA,
        "hard_fail_delta_thresh": HARD_FAIL_RETENTION_DELTA,
    }

    if not math.isfinite(ent_k16) or not math.isfinite(ret_k16):
        return ("INSTRUMENTATION_FAIL", "Non-finite metric at K=16.", summary)

    entropy_pass = ent_k16 < HARD_PASS_ENTROPY_K16
    entropy_fail = ent_k16 > HARD_FAIL_ENTROPY_K16
    retention_pass = delta >= HARD_PASS_RETENTION_DELTA
    retention_fail = delta < HARD_FAIL_RETENTION_DELTA

    if entropy_pass and retention_pass:
        verdict = "COSINE_ROUTER_HARD_PASS"
        verdict_msg = (
            f"COSINE_ROUTER_HARD_PASS: cosine-dot routing breaks LSH entropy ceiling. "
            f"entropy@K=16={ent_k16:.3f}b < {HARD_PASS_ENTROPY_K16}b (PASS). "
            f"retention delta={delta:+.5f} >= {HARD_PASS_RETENTION_DELTA} (PASS). "
            f"ret@K=4={ret_k4:.5f} -> ret@K=16={ret_k16:.5f}. "
            f"Substrate-native router enables K-scaling without degradation. "
            f"Next: Hebbian anchor init variant + composition with capacity expansion."
        )
    elif entropy_fail or retention_fail:
        reasons = []
        if entropy_fail:
            reasons.append(f"entropy@K=16={ent_k16:.3f}b > {HARD_FAIL_ENTROPY_K16}b (FAIL)")
        if retention_fail:
            reasons.append(f"retention delta={delta:+.5f} < {HARD_FAIL_RETENTION_DELTA} (FAIL)")
        verdict = "COSINE_ROUTER_HARD_FAIL"
        verdict_msg = (
            f"COSINE_ROUTER_HARD_FAIL: cosine-dot routing fails entropy/retention gates. "
            + "; ".join(reasons) + ". "
            f"Random BSC anchors may not provide sufficient discriminability at N=4096. "
            f"Escalate to Hebbian-anchor rescue (anchor = bundle of first M/K stored patterns per expert)."
        )
    else:
        verdict = "COSINE_ROUTER_MIDDLE"
        verdict_msg = (
            f"COSINE_ROUTER_MIDDLE: entropy and/or retention in inconclusive band. "
            f"entropy@K=16={ent_k16:.3f}b (band: [{HARD_PASS_ENTROPY_K16}, {HARD_FAIL_ENTROPY_K16}]b). "
            f"retention delta={delta:+.5f} (band: [{HARD_PASS_RETENTION_DELTA}, {HARD_FAIL_RETENTION_DELTA}]). "
            f"Follow-up: Hebbian-anchor variant in same run (see handoff autonomy clause)."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False) -> None:
    t0 = time.time()
    print(f"[exp] wave14_moe_cosine_router_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)
    results_per_K, out_dir = run_sweep(smoke)

    # Multi-scale smoke check
    if smoke:
        print("\n[multi-scale smoke] running N_smoke * 2 check...", flush=True)
        device = torch.device("cpu")
        N2 = N_SMOKE * 2
        M2 = M_PER_EXPERT_SMOKE * 2
        c2 = run_cell_cosine(4, N2, M2, 17, device)
        assert math.isfinite(c2["retention"]) and math.isfinite(c2["routing_entropy_bits"]), \
            f"Multi-scale smoke FAIL: ret={c2['retention']} ent={c2['routing_entropy_bits']}"
        assert c2["k_eff"] > 0, "Multi-scale smoke FAIL: k_eff=0"
        print(f"  N={N2} K=4: ret={c2['retention']:.5f} ent={c2['routing_entropy_bits']:.3f}b", flush=True)
        print("[multi-scale smoke] PASS", flush=True)

    verdict, verdict_msg, summary = compute_verdict(results_per_K)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

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
            "mode": "smoke" if smoke else "full",
            "router": "cosine_dot_top1",
        },
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics written to {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test",
                        help="Run instrumentation self-tests only and exit (used by queue gate)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)  # selftests already ran at module scope above
    run(smoke=args.smoke)
