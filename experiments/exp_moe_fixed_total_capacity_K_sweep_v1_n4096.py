"""MoE fixed-total-capacity K-sweep v1: TRUE K-scaling-ceiling test at N=4096.

CONTEXT:
  moe_gradient_router_v1 (HARD_FAIL smoke): entropy@K=16=3.99b with M_per_expert=800 FIXED.
    retention=1.0 at K=4 and K=16 (total capacity scaled 4x: 3200->12800).
    HARD_FAIL on entropy gate but retention was fine -- entropy collapse is routing issue.

  Per strategy_request_to_exp_dev_v260_moe_fixed_total_capacity_K_sweep_2026-05-28.md:
    v1 did NOT test K-scaling ceiling because total capacity scaled with K.
    This experiment holds M_total=3200 CONSTANT, varying M_per_expert=M_total/K:
      K=4  -> M_per_expert=800  (baseline)
      K=8  -> M_per_expert=400  (each expert sees half the patterns)
      K=16 -> M_per_expert=200  (each expert sees 1/4 the patterns)
      K=32 -> M_per_expert=100  (if budget allows)

  If retention HOLDS at K=16 fixed-total-capacity -> MoE K-scaling was entropy artifact.
  If retention DEGRADES at K=16 fixed-total-capacity -> TRUE K-scaling ceiling exists.

  CAUSAL MODEL: v220 M2_DOMINANT said "LSH entropy is sole degradation source."
    Gradient-router v1 showed entropy=3.99b with retention=1.0 (entropy != degradation source).
    This experiment resolves whether retention degrades under EQUAL total capacity.

SCIENTIFIC QUESTION:
  At M_total=3200 (fixed), does retention degrade as K increases from 4 to 16?
  Do entropy patterns (routing quality) differ from constant-M_per_expert regime?

K_sweep: {4, 8, 16, 32} (K=32 included if wall time allows).
M_total: 3200 (= 800 * 4 = baseline K=4 capacity).
Seeds: {7, 17, 23} (3-seed; same as gradient router v1 for direct comparison).
N: 4096.
Router: gradient-trained (same architecture as moe_gradient_router_v1).

PRE-REGISTERED BANDS:
  HARD_PASS_NO_CEILING: retention at K=16 >= retention at K=4 - 0.05 under fixed M_total.
    AND ret_K16 >= 0.70 (absolute floor above chance).
    Interpretation: MoE K-scaling was entropy artifact; K=16 design point LIFTS TO ACTIVE.
  HARD_FAIL_CEILING: retention at K=16 < retention at K=4 - 0.15 under fixed M_total.
    AND ret_K16 < 0.50.
    Interpretation: TRUE K-scaling ceiling exists; row annotated with fixed-capacity bound.
  MIDDLE_BAND: ret_delta in (-0.15, -0.05); partial degradation, likely capacity-limited.

FORMULA SELF-TESTS:
  1. M_per_expert = M_total // K. At K=4: 800. At K=8: 400. At K=16: 200. At K=32: 100.
  2. entropy(uniform K=4) = log2(4) = 2.0 bits. entropy(uniform K=16) = log2(16) = 4.0 bits.
  3. HARD_PASS gate: ret_K16=0.92, ret_K4=0.95 -> delta=-0.03 >= -0.05 AND 0.92>=0.70 -> PASS.
  4. HARD_FAIL gate: ret_K16=0.30, ret_K4=0.95 -> delta=-0.65 < -0.15 AND 0.30<0.50 -> FAIL.
  5. N stated explicitly (PROT-018: no _nN suffix; N_FULL=4096 below).
     Wait: anchor name IS _n4096. PROT-018: _n4096 binds N_FULL=4096.

OOM CHECK:
  W float32 at N=4096 per expert: 64MB x K=16 = 1024MB.
  BUT: we build W_k sequentially (not simultaneously), peak = 64MB + keys/vals.
  M_total=3200 x N=4096 x float32 = 52MB for keys. Total peak: ~130MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  gradient router v1 FULL elapsed not recorded (smoke only 0.20s).
  Similar arms (hebbian_anchor v1) elapsed: 2944s at 3 seeds K={4,8,16,32}.
  gradient router adds 50 grad steps per K; comparable to Hebbian v1 routing overhead.
  This experiment: K={4,8,16,32} x 3 seeds x gradient training.
  Estimate: ~3000s. Safety: ceil(1.5 * 3000) = 4500s.
  timeout_s = 4500.
  Under 2h: no extra flag.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Queue: remote_cpu_queue (CPU; pure numpy/torch no CUDA; K-sweep x 3 seeds)
Pre-reg: preregs/2026-05-28_moe_fixed_total_capacity_K_sweep_v1_n4096.md
Parent: moe_gradient_router_v1 (HARD_FAIL entropy; retained retention data unblocks this)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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

# Load moe_gradient_router_v1 base (routing_entropy_bits)
_gv1_path = REPO / "experiments" / "exp_moe_gradient_router_v1.py"
_gv1_spec = importlib.util.spec_from_file_location("moe_gr_v1_fixed", _gv1_path)
gv1 = importlib.util.module_from_spec(_gv1_spec)
_gv1_spec.loader.exec_module(gv1)

routing_entropy_bits = gv1.routing_entropy_bits

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096     # PROT-018 binding contract
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_TOTAL_FULL = 3200    # fixed total capacity across all K
M_TOTAL_SMOKE = 320    # smoke scale

K_SWEEP_FULL = [4, 8, 16, 32]
K_SWEEP_SMOKE = [4, 16]

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

N_GRAD_STEPS = 50
LR = 0.01

# Pre-registered thresholds
HP_RET_DELTA = -0.05     # retention_K16 >= retention_K4 - 0.05 (no-ceiling HARD_PASS)
HP_RET_ABS = 0.70        # ret_K16 >= 0.70 absolute floor for HARD_PASS
HF_RET_DELTA = -0.15     # retention_K16 < retention_K4 - 0.15 (ceiling HARD_FAIL)
HF_RET_ABS = 0.50        # ret_K16 < 0.50 for HARD_FAIL


def get_output_dir(default_name: str = "moe_fixed_total_capacity_K_sweep_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_fixed_cap(K: int, seed: int, N_use: int, M_total: int) -> Dict:
    """Run gradient-trained router for one (K, seed) with FIXED total capacity."""
    device = torch.device("cpu")
    M_per_expert = M_total // K
    if M_per_expert == 0:
        return {"K": K, "seed": seed, "retention": 0.0,
                "routing_entropy_bits": math.log2(K),
                "M_per_expert": M_per_expert, "M_total": M_total, "error": "M_per_expert=0"}

    rng = torch.Generator()
    rng.manual_seed(seed)

    # Generate M_total patterns (fixed total, NOT K * M_per_expert_fixed)
    keys_all = (torch.randint(0, 2, (M_total, N_use), generator=rng) * 2 - 1).float()
    vals_all = (torch.randint(0, 2, (M_total, N_use), generator=rng) * 2 - 1).float()

    # Teacher routing: balanced assignment (M_per_expert patterns per expert)
    teacher_assign = torch.arange(M_total) % K

    # Train gradient router (same architecture as gradient_router_v1)
    router_W = torch.randn(K, N_use) * 0.01
    router_W.requires_grad_(True)
    optimizer = torch.optim.Adam([router_W], lr=LR)

    for step in range(N_GRAD_STEPS):
        scores = keys_all @ router_W.T / math.sqrt(N_use)  # (M_total, K)
        ce_loss = torch.nn.functional.cross_entropy(scores, teacher_assign)
        optimizer.zero_grad()
        ce_loss.backward()
        optimizer.step()

    # Hard assignment with trained router
    with torch.no_grad():
        scores_final = keys_all @ router_W.data.T / math.sqrt(N_use)
        hard_assign = torch.argmax(scores_final, dim=-1)

    entropy_at_K = routing_entropy_bits(hard_assign, K)

    # Measure retention per expert (each expert retrieves its M_per_expert patterns)
    accs = []
    for k in range(K):
        mask = hard_assign == k
        if mask.sum() == 0:
            continue
        k_keys = keys_all[mask]
        k_vals = vals_all[mask]

        W_k = torch.zeros(N_use, N_use)
        bs = 256
        for start in range(0, k_keys.shape[0], bs):
            W_k += (k_vals[start:start + bs].T @ k_keys[start:start + bs]) / N_use

        n_probe = min(50, k_keys.shape[0])
        probe_keys = k_keys[:n_probe]
        val_cb = k_vals[:min(500, k_keys.shape[0])]
        responses = probe_keys @ W_k.T
        sims = (val_cb @ responses.T) / N_use
        pred = torch.argmax(sims, dim=0)
        true_idx = torch.arange(n_probe)
        acc = float((pred == true_idx).float().mean().item())
        accs.append(acc)

    retention = sum(accs) / len(accs) if accs else 0.0

    return {
        "K": K,
        "seed": seed,
        "routing_entropy_bits": entropy_at_K,
        "retention": retention,
        "M_total": M_total,
        "M_per_expert": M_per_expert,
        "n_patterns_routed": int(hard_assign.shape[0]),
    }


def compute_verdict(summary: Dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("MOE_FIXED_CAP_MIDDLE_BAND", "No cells.")

    from collections import defaultdict
    ent_by_K: Dict[int, List[float]] = defaultdict(list)
    ret_by_K: Dict[int, List[float]] = defaultdict(list)
    for c in cells:
        ent_by_K[c["K"]].append(c["routing_entropy_bits"])
        ret_by_K[c["K"]].append(c["retention"])

    ent_mean = {k: sum(v) / len(v) for k, v in ent_by_K.items()}
    ret_mean = {k: sum(v) / len(v) for k, v in ret_by_K.items()}

    ret_K4 = ret_mean.get(4, None)
    ret_K16 = ret_mean.get(16, None)
    ret_delta = (ret_K16 - ret_K4) if (ret_K16 is not None and ret_K4 is not None) else None

    detail = (f"M_total={summary.get('M_total', M_TOTAL_FULL)}. "
              f"entropy_by_K={dict((k, round(v, 3)) for k, v in sorted(ent_mean.items()))}. "
              f"retention_by_K={dict((k, round(v, 3)) for k, v in sorted(ret_mean.items()))}. "
              f"ret_delta_K16_vs_K4={round(ret_delta, 4) if ret_delta is not None else 'N/A'}.")

    if ret_delta is not None:
        # HARD_PASS: no ceiling (delta >= -0.05 AND ret_K16 >= 0.70)
        if ret_delta >= HP_RET_DELTA and ret_K16 >= HP_RET_ABS:
            return ("MOE_FIXED_CAP_HARD_PASS_NO_CEILING",
                    f"NO K-SCALING CEILING: ret_delta={ret_delta:.4f}>={HP_RET_DELTA} "
                    f"AND ret_K16={ret_K16:.4f}>={HP_RET_ABS}. "
                    f"MoE K-scaling was entropy artifact; K=16 unblocked. " + detail)

        # HARD_FAIL: ceiling confirmed
        if ret_delta < HF_RET_DELTA and ret_K16 < HF_RET_ABS:
            return ("MOE_FIXED_CAP_HARD_FAIL_CEILING",
                    f"TRUE K-SCALING CEILING: ret_delta={ret_delta:.4f}<{HF_RET_DELTA} "
                    f"AND ret_K16={ret_K16:.4f}<{HF_RET_ABS}. "
                    f"Fixed-capacity retention degrades with K. " + detail)

    return ("MOE_FIXED_CAP_MIDDLE_BAND",
            f"Partial. ret_delta={round(ret_delta, 4) if ret_delta else 'N/A'}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Test M_per_expert computation
    for K_test, expected in [(4, 800), (8, 400), (16, 200), (32, 100)]:
        assert M_TOTAL_FULL // K_test == expected, \
            f"M_per_expert at K={K_test}: {M_TOTAL_FULL // K_test} != {expected}"

    # Test entropy formula
    ent_uniform_4 = routing_entropy_bits(torch.tensor([0, 1, 2, 3]), K=4)
    assert abs(ent_uniform_4 - 2.0) < 0.01, f"Uniform entropy K=4: {ent_uniform_4}"
    ent_uniform_16 = routing_entropy_bits(torch.tensor(list(range(16))), K=16)
    assert abs(ent_uniform_16 - 4.0) < 0.01, f"Uniform entropy K=16: {ent_uniform_16}"

    # Test one cell at smoke scale
    cell = run_one_fixed_cap(K=4, seed=17, N_use=N_SMOKE, M_total=M_TOTAL_SMOKE)
    assert "retention" in cell and cell["retention"] is not None, f"retention sentinel: {cell}"
    assert 0.0 <= cell["retention"] <= 1.0, f"retention out of [0,1]: {cell['retention']}"
    assert "routing_entropy_bits" in cell, f"entropy missing: {cell}"

    # Test verdict HARD_PASS path
    cells_hp = [{"K": 4, "seed": s, "routing_entropy_bits": 2.0, "retention": 0.95,
                  "M_total": 3200, "M_per_expert": 800}
                for s in [7, 17, 23]] + \
               [{"K": 16, "seed": s, "routing_entropy_bits": 3.9, "retention": 0.93,
                  "M_total": 3200, "M_per_expert": 200}
                for s in [7, 17, 23]]
    v, msg = compute_verdict({"cells": cells_hp, "M_total": 3200})
    assert "HARD_PASS" in v, f"Self-test HP failed: {v}: {msg}"

    # Test verdict HARD_FAIL path
    cells_hf = [{"K": 4, "seed": 17, "routing_entropy_bits": 2.0, "retention": 0.95,
                  "M_total": 3200, "M_per_expert": 800},
                {"K": 16, "seed": 17, "routing_entropy_bits": 4.0, "retention": 0.30,
                  "M_total": 3200, "M_per_expert": 200}]
    v2, msg2 = compute_verdict({"cells": cells_hf, "M_total": 3200})
    assert "HARD_FAIL" in v2, f"Self-test HF failed: {v2}: {msg2}"

    # OOM pre-check (sequential W build, peak ~130MB at N=4096)
    peak_bytes = N_FULL * N_FULL * 4 + M_TOTAL_FULL * N_FULL * 4 * 2
    assert peak_bytes < 6e9, f"OOM check: {peak_bytes:.2e} >= 6GB"

    print(f"[SELFTEST PASS] moe_fixed_total_capacity_K_sweep_v1_n4096: "
          f"N_FULL={N_FULL} M_TOTAL={M_TOTAL_FULL} smoke_ret={cell['retention']:.3f} "
          f"OOM={peak_bytes:.2e}",
          flush=True)


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=4500)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_use = N_SMOKE if smoke else N_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    M_total = M_TOTAL_SMOKE if smoke else M_TOTAL_FULL

    outdir = get_output_dir()
    t0 = time.time()
    cells = []

    for seed in seeds:
        for K in K_sweep:
            M_per = M_total // K
            print(f"K={K} M_per_expert={M_per} seed={seed}...", flush=True)
            cell = run_one_fixed_cap(K, seed, N_use, M_total)
            cells.append(cell)
            elapsed = time.time() - t0
            print(f"  ent={cell['routing_entropy_bits']:.3f}b ret={cell['retention']:.3f} "
                  f"elapsed={elapsed:.1f}s", flush=True)

    elapsed_s = time.time() - t0
    summary = {"cells": cells, "N": N_use, "smoke": smoke, "M_total": M_total}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_use,
            "K_sweep": K_sweep,
            "seeds": seeds,
            "M_total": M_total,
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
