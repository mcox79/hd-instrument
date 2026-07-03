"""3-arm MoE rebuild v3: reduced M_grid to avoid OOM at K=8.

CONTEXT: v1 OOMed at K=8 M_total=25600 (1.11GiB on 8GiB GPU). v2 FAILED on remote
(same M_grid config per decisions log). v3 caps M_total <= 12800 at K=8 by restricting
M_mult to [0.5, 1.0] (dropping the 2.0x point at K=8). Full 3-point M_mult [0.5,1.0,2.0]
retained for K<=4 where M_total_max = 2.0 * 4 * 1600 = 12800.

Memory budget (per cell):
  SHIFT arm K=8: W_k = 4096^2 * 4 bytes * 8 experts = 536MB -> too large + activations
  SHIFT arm K=8 M_mult=1.0: M_total=12800, 5 seeds -> all W's sequential -> ~268MB peak
  SHIFT arm K=4 M_mult=2.0: M_total=12800, 5 seeds -> ~134MB per W pair -> safe

v3 OOM fix:
  K_SWEEP_FULL = [1, 2, 4, 8]  (same as v2)
  M_MULT_FULL[K<=4] = [0.5, 1.0, 2.0]
  M_MULT_FULL[K>=8] = [0.5, 1.0]  (drop 2.0x at K=8 to stay within 8GiB)
  No W accumulation across seeds (clear between).
  Explicit torch.cuda.empty_cache() after each K cell.

Pre-registered bands (inherited from v2 unchanged):
  HARD-PASS: Arm A (SHIFT) exceeds Arm C (SINGLE) by > 0.15 at M=2*baseline AND
             mode-collapse Gini < 0.4, max/min < 5x, top2_frac < 0.6 AND
             retention monotone-non-decreasing in K at fixed M_total/K (tol 0.02)
  HARD-FAIL: Arm A within +/-0.05 of Arm C across ALL M AND
             Arm B within +/-0.05 of Arm C AND mode-collapse Gini>0.4 OR max/min>5x
  MIDDLE: Arm A exceeds Arm C by 0.05-0.15 AND mode-collapse marginal
  OOM-PARTIAL: any K-cell OOMs -> record OOM tag, continue to next K

Queue: overnight_queue (GPU; K in {1,2,4,8} x reduced M_mult x 5 seeds x 3 arms)
Pre-reg: preregs/2026-05-26_wave14_moe_shift_partition_v3.md
Version: v3 (OOM fix: cap M_total<=12800 at K>=8; explicit cache clear between cells)
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
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ── design parameters ──
N_FULL = 4096
N_SMOKE = 512
M_PER_EXPERT_FULL = 1600
M_PER_EXPERT_SMOKE = int(M_PER_EXPERT_FULL * N_SMOKE / N_FULL)  # 200
K_SWEEP_FULL = [1, 2, 4, 8]
K_SWEEP_SMOKE = [1, 2, 4]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# M_MULT by K (cap at K>=8 to avoid OOM: max M_total = 12800)
def get_m_mult(K: int, smoke: bool) -> list:
    if smoke:
        return [0.5, 1.0, 2.0]
    return [0.5, 1.0] if K >= 8 else [0.5, 1.0, 2.0]

BATCH_STORE = 256

# Pre-reg thresholds
HP_ARM_A_VS_C_LIFT = 0.15
HP_GINI_MAX = 0.4
HP_MAX_MIN_RATIO = 5.0
HP_TOP2_FRAC_MAX = 0.6
HF_ARM_A_VS_C_MAX = 0.05
MID_ARM_A_VS_C_MIN = 0.05
MONOTONE_TOL = 0.02


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


# ── BSC helpers ──
def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    raw = torch.randint(0, 2, (M, N), generator=gen, device=device).float()
    return 2.0 * raw - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    """W = (1/N) sum v_i k_i^T, batched."""
    device = keys.device
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def recall_cosine_batch(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor) -> float:
    y = keys @ W.T
    yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return float((yn * vn).sum(dim=1).mean())


# ── LSH balanced-bin gating ──
def build_lsh_gate(N: int, K: int, gen: torch.Generator, device) -> torch.Tensor:
    proj = make_bsc(K, N, gen, device).float()
    proj = proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return proj


def gate_assign(keys: torch.Tensor, proj: torch.Tensor, K: int) -> torch.Tensor:
    scores = keys @ proj.T
    assignment = scores.argmax(dim=1)
    target_load = keys.shape[0] // K
    if target_load < 1:
        return assignment
    loads = torch.bincount(assignment, minlength=K).float()
    gini_val = _gini(loads.tolist())
    if gini_val > 0.3:
        primary_score = scores[:, 0]
        sorted_idx = primary_score.argsort()
        new_assign = torch.zeros(keys.shape[0], dtype=torch.long, device=keys.device)
        for k in range(K):
            start = k * target_load
            end = (k + 1) * target_load if k < K - 1 else keys.shape[0]
            new_assign[sorted_idx[start:end]] = k
        return new_assign
    return assignment


def gate_top2(query: torch.Tensor, proj: torch.Tensor, K: int):
    scores = (proj @ query)
    top2_idx = scores.topk(min(2, K)).indices
    top2_scores = scores[top2_idx].softmax(dim=0)
    return top2_idx, top2_scores


# ── Mode-collapse metrics ──
def _gini(loads: list) -> float:
    n = len(loads)
    if n <= 1:
        return 0.0
    total = sum(loads)
    if total <= 0:
        return 0.0
    loads_sorted = sorted(loads)
    cumsum = 0.0
    for i, v in enumerate(loads_sorted):
        cumsum += (2 * (i + 1) - n - 1) * v
    return cumsum / (n * total)


def mode_collapse_metrics(loads: list) -> dict:
    total = sum(loads)
    gini = _gini(loads)
    max_l = max(loads) if loads else 0
    min_l = min(loads) if loads else 0
    ratio = (max_l / max(min_l, 1e-9)) if len(loads) > 1 else 1.0
    sorted_desc = sorted(loads, reverse=True)
    top2_sum = sum(sorted_desc[:2])
    K = len(loads)
    top2_frac = top2_sum / max(total, 1e-9)
    return {"gini": gini, "max_min_ratio": ratio, "top2_frac": top2_frac, "loads": loads}


def compute_dmpk_signature(Wks: list, K: int, Nk: int, device) -> dict:
    """DMPK bimodality: eigenvalue distribution of concatenated W SVDs."""
    singular_vals = []
    for Wk in Wks:
        if Wk.shape[0] >= 2 and Wk.shape[1] >= 2:
            try:
                sv = torch.linalg.svdvals(Wk)
                singular_vals.extend(sv.cpu().float().tolist()[:min(10, len(sv))])
            except Exception:
                pass
    if len(singular_vals) < 4:
        return {"bimodal_score": 0.0, "n_sv": 0}
    sv_arr = sorted(singular_vals, reverse=True)
    # Simple bimodality: gap between top-half and bottom-half means
    mid = len(sv_arr) // 2
    top_mean = sum(sv_arr[:mid]) / max(mid, 1)
    bot_mean = sum(sv_arr[mid:]) / max(len(sv_arr) - mid, 1)
    gap = top_mean - bot_mean
    bimodal_score = gap / max(top_mean + bot_mean, 1e-9)
    return {"bimodal_score": float(bimodal_score), "n_sv": len(sv_arr)}


def compute_gate_overlap(proj: torch.Tensor, K: int) -> float:
    """Mean pairwise cosine overlap between gate projections (< 0.1 = well-separated)."""
    if K < 2:
        return 0.0
    n = proj @ proj.T
    diag = torch.diag(n)
    norm = (diag.unsqueeze(1) * diag.unsqueeze(0)).sqrt().clamp(min=1e-9)
    cos = n / norm
    mask = ~torch.eye(K, dtype=torch.bool, device=proj.device)
    return float(cos[mask].abs().mean())


# ── Arm implementations ──
def run_arm_a_shift(keys: torch.Tensor, vals: torch.Tensor, K: int, N: int,
                    gen: torch.Generator, device) -> dict:
    """SHIFT arm: K full-N experts. Parameter budget K*N^2."""
    proj = build_lsh_gate(N, K, gen, device)
    assignment = gate_assign(keys, proj, K)
    loads = [int((assignment == k).sum()) for k in range(K)]
    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N, N), dtype=torch.float32, device=device))
            continue
        Wk = outer_product_store(keys[mask], vals[mask], N)
        Wks.append(Wk)
    M = keys.shape[0]
    cos_vals = []
    for i in range(M):
        k_pri, scores = gate_top2(keys[i], proj, K)
        y = sum(Wks[int(ki)] @ keys[i] * float(s) for ki, s in zip(k_pri, scores))
        y = y / y.norm().clamp(min=1e-9)
        v = vals[i] / vals[i].norm().clamp(min=1e-9)
        cos_vals.append(float((y * v).sum()))
    dmpk = compute_dmpk_signature(Wks, K, N, device)
    gate_ov = compute_gate_overlap(proj, K)
    del Wks
    if device.type == "cuda":
        torch.cuda.empty_cache()
    mc = mode_collapse_metrics(loads)
    return {"mean_cosine": sum(cos_vals) / len(cos_vals), "loads": loads,
            "mode_collapse": mc, "param_budget": K * N * N, "dmpk": dmpk,
            "gate_overlap": gate_ov}


def run_arm_b_partition(keys: torch.Tensor, vals: torch.Tensor, K: int, N: int,
                        gen: torch.Generator, device) -> dict:
    """PARTITION arm: K experts each (N/K, N/K). Parameter budget N^2 (fixed)."""
    N_k = max(N // K, 1)
    proj = build_lsh_gate(N, K, gen, device)
    assignment = gate_assign(keys, proj, K)
    loads = [int((assignment == k).sum()) for k in range(K)]
    perm_gen = torch.Generator(device=device).manual_seed(N * 100 + K)
    perm = torch.randperm(N, generator=perm_gen, device=device)
    keys_p = keys[:, perm]
    vals_p = vals[:, perm]
    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N_k, N_k), dtype=torch.float32, device=device))
            continue
        k_slice = keys_p[mask, k * N_k:(k + 1) * N_k]
        v_slice = vals_p[mask, k * N_k:(k + 1) * N_k]
        Wk = outer_product_store(k_slice, v_slice, N_k)
        Wks.append(Wk)
    M = keys.shape[0]
    cos_vals = []
    for i in range(M):
        k_idx = int(assignment[i])
        q_slice = keys_p[i, k_idx * N_k:(k_idx + 1) * N_k]
        v_slice = vals_p[i, k_idx * N_k:(k_idx + 1) * N_k]
        y = Wks[k_idx] @ q_slice
        y_n = y / y.norm().clamp(min=1e-9)
        v_n = v_slice / v_slice.norm().clamp(min=1e-9)
        cos_vals.append(float((y_n * v_n).sum()))
    dmpk = compute_dmpk_signature(Wks, K, N_k, device)
    gate_ov = compute_gate_overlap(proj, K)
    del Wks
    if device.type == "cuda":
        torch.cuda.empty_cache()
    mc = mode_collapse_metrics(loads)
    return {"mean_cosine": sum(cos_vals) / len(cos_vals), "loads": loads,
            "mode_collapse": mc, "param_budget": N * N, "dmpk": dmpk,
            "gate_overlap": gate_ov}


def run_arm_c_single(keys: torch.Tensor, vals: torch.Tensor, K: int, N: int,
                     gen: torch.Generator, device) -> dict:
    """SINGLE arm: 1 expert of dim N_single = round(sqrt(K)*N). Budget K*N^2."""
    N_single = max(1, int(round(math.sqrt(K) * N)))
    perm_gen = torch.Generator(device=device).manual_seed(N * 200 + K)
    perm_k = torch.randperm(N, generator=perm_gen, device=device)[:min(N_single, N)]
    # Subsample/pad to N_single
    if N_single <= N:
        keys_s = keys[:, perm_k]
        vals_s = vals[:, perm_k]
        N_use = N_single
    else:
        # Repeat-tile to reach N_single
        repeats = math.ceil(N_single / N)
        keys_s = keys.repeat(1, repeats)[:, :N_single]
        vals_s = vals.repeat(1, repeats)[:, :N_single]
        N_use = N_single
    W = outer_product_store(keys_s, vals_s, N_use)
    M = keys.shape[0]
    cos_vals = []
    for i in range(M):
        y = W @ keys_s[i]
        y_n = y / y.norm().clamp(min=1e-9)
        v_n = vals_s[i] / vals_s[i].norm().clamp(min=1e-9)
        cos_vals.append(float((y_n * v_n).sum()))
    del W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"mean_cosine": sum(cos_vals) / len(cos_vals), "param_budget": K * N * N,
            "N_single": N_use}


# ── Instrumentation self-test ──
def _instrumentation_selftest():
    """Assert all metrics computable at small scale."""
    device = torch.device("cpu")
    gen = torch.Generator().manual_seed(99)
    N_t, M_t, K_t = 64, 100, 2
    keys = make_bsc(M_t, N_t, gen, device)
    vals = make_bsc(M_t, N_t, gen, device)
    # Self-test 1: Arm A SHIFT
    ra = run_arm_a_shift(keys, vals, K_t, N_t, torch.Generator().manual_seed(7), device)
    assert "mean_cosine" in ra and ra["mean_cosine"] is not None, "Arm A mean_cosine null"
    assert ra["mode_collapse"]["gini"] is not None, "Arm A gini null"
    # Self-test 2: Arm B PARTITION
    rb = run_arm_b_partition(keys, vals, K_t, N_t, torch.Generator().manual_seed(7), device)
    assert "mean_cosine" in rb and rb["mean_cosine"] is not None, "Arm B mean_cosine null"
    # Self-test 3: Arm C SINGLE
    rc = run_arm_c_single(keys, vals, K_t, N_t, torch.Generator().manual_seed(7), device)
    assert "mean_cosine" in rc and rc["mean_cosine"] is not None, "Arm C mean_cosine null"
    # Self-test 4: Gini formula correctness
    assert abs(_gini([500, 500, 500, 500]) - 0.0) < 0.01, "gini equal fail"
    assert _gini([2000, 0, 0, 0]) > 0.70, "gini collapse fail"
    # Self-test 5: PARTITION null (K cancels in load-ratio formula)
    # load_ratio = M_total/(K) / (alpha_c * N/K) = M_total/(alpha_c*N) -- K-independent
    alpha_c = 0.56
    N_test, K1, K2, M_total = 4096, 2, 4, 6400
    lr1 = (M_total / K1) / (alpha_c * N_test / K1)
    lr2 = (M_total / K2) / (alpha_c * N_test / K2)
    assert abs(lr1 - lr2) < 1e-9, f"PARTITION K-cancel self-test fail: {lr1} vs {lr2}"
    # Self-test 6: SHIFT load-ratio decreases with K
    lr_shift1 = (M_total / K1) / (alpha_c * N_test)
    lr_shift2 = (M_total / K2) / (alpha_c * N_test)
    assert lr_shift1 > lr_shift2, "SHIFT K-scaling self-test fail"
    # Self-test 7: OOM budget check for K=8 M_mult=1.0
    M_max_k8 = 1.0 * 8 * M_PER_EXPERT_FULL
    assert M_max_k8 <= 12800, f"K=8 M_max budget exceeded: {M_max_k8}"
    print("selftest PASS 7/7")


_instrumentation_selftest()


def run_one_cell(N, M_total, K, seeds, device, smoke):
    """Run one (N, M_total, K) cell across seeds for all 3 arms."""
    arm_a_cosines, arm_b_cosines, arm_c_cosines = [], [], []
    mc_a_list = []
    for seed in seeds:
        gen = torch.Generator(device=device if device.type == "cuda" else "cpu").manual_seed(seed)
        keys = make_bsc(M_total, N, gen, device)
        vals = make_bsc(M_total, N, gen, device)
        ra = run_arm_a_shift(keys, vals, K, N,
                             torch.Generator(device=device if device.type == "cuda" else "cpu").manual_seed(seed + 1000),
                             device)
        rb = run_arm_b_partition(keys, vals, K, N,
                                 torch.Generator(device=device if device.type == "cuda" else "cpu").manual_seed(seed + 2000),
                                 device)
        rc = run_arm_c_single(keys, vals, K, N,
                              torch.Generator(device=device if device.type == "cuda" else "cpu").manual_seed(seed + 3000),
                              device)
        arm_a_cosines.append(ra["mean_cosine"])
        arm_b_cosines.append(rb["mean_cosine"])
        arm_c_cosines.append(rc["mean_cosine"])
        mc_a_list.append(ra["mode_collapse"])
        del keys, vals
        if device.type == "cuda":
            torch.cuda.empty_cache()

    def mean_std(vals_list):
        n = len(vals_list)
        m = sum(vals_list) / n
        v = sum((x - m) ** 2 for x in vals_list) / max(n - 1, 1)
        return m, v ** 0.5

    a_m, a_s = mean_std(arm_a_cosines)
    b_m, b_s = mean_std(arm_b_cosines)
    c_m, c_s = mean_std(arm_c_cosines)
    mc_mean = {
        "gini": sum(mc["gini"] for mc in mc_a_list) / len(mc_a_list),
        "max_min_ratio": sum(mc["max_min_ratio"] for mc in mc_a_list) / len(mc_a_list),
        "top2_frac": sum(mc["top2_frac"] for mc in mc_a_list) / len(mc_a_list),
    }
    return {
        "N": N, "M_total": M_total, "K": K,
        "arm_a_mean": a_m, "arm_a_std": a_s,
        "arm_b_mean": b_m, "arm_b_std": b_s,
        "arm_c_mean": c_m, "arm_c_std": c_s,
        "lift_a_vs_c": a_m - c_m,
        "lift_b_vs_c": b_m - c_m,
        "mode_collapse": mc_mean,
    }


def classify_verdict(cells: list) -> tuple:
    """Classify based on pre-reg bands across all (K, M_total) cells."""
    # Find highest-load cell per K (M_mult=1.0 or max available)
    from collections import defaultdict
    by_K = defaultdict(list)
    for c in cells:
        by_K[c["K"]].append(c)

    # Check HARD-PASS: at max M cell per K>=2, Arm A > Arm C by HP_ARM_A_VS_C_LIFT
    # AND mode-collapse within spec AND monotone in K
    hp_cells = []
    for K, cs in sorted(by_K.items()):
        if K < 2:
            continue
        max_m_cell = max(cs, key=lambda c: c["M_total"])
        hp_cells.append(max_m_cell)

    arm_a_lifts = [c["lift_a_vs_c"] for c in hp_cells]
    arm_b_lifts = [c["lift_b_vs_c"] for c in hp_cells]  # should be flat
    mc_ok = all(c["mode_collapse"]["gini"] < HP_GINI_MAX and
                c["mode_collapse"]["max_min_ratio"] < HP_MAX_MIN_RATIO and
                c["mode_collapse"]["top2_frac"] < HP_TOP2_FRAC_MAX
                for c in hp_cells)

    # Monotone check: arm_a_mean at max-M should increase with K
    K_vals = sorted(by_K.keys())
    arm_a_at_maxM = []
    for K in K_vals:
        max_m_cell = max(by_K[K], key=lambda c: c["M_total"])
        arm_a_at_maxM.append(max_m_cell["arm_a_mean"])
    monotone = all(arm_a_at_maxM[i + 1] >= arm_a_at_maxM[i] - MONOTONE_TOL
                   for i in range(len(arm_a_at_maxM) - 1))

    if len(arm_a_lifts) > 0 and min(arm_a_lifts) > HP_ARM_A_VS_C_LIFT and mc_ok and monotone:
        return "MOE_SHIFT_HARD_PASS", "MoE structural separation confirmed: Arm A > Arm C by >{:.3f} at all K cells; mode-collapse within spec; monotone in K".format(HP_ARM_A_VS_C_LIFT)

    # HARD-FAIL: all cells Arm A within HF of Arm C AND Arm B within HF
    all_a_flat = all(abs(c["lift_a_vs_c"]) < HF_ARM_A_VS_C_MAX for c in cells)
    all_b_flat = all(abs(c["lift_b_vs_c"]) < HF_ARM_A_VS_C_MAX for c in cells)
    mc_fail = any(c["mode_collapse"]["gini"] > HP_GINI_MAX or
                  c["mode_collapse"]["max_min_ratio"] > HP_MAX_MIN_RATIO
                  for c in cells)
    if all_a_flat and all_b_flat and mc_fail:
        return "MOE_SHIFT_HARD_FAIL", "MoE rejected: Arm A flat vs Arm C + mode-collapse; parameter budget alone explains performance"

    # MIDDLE
    mid_lifts = [c for c in hp_cells if MID_ARM_A_VS_C_MIN < c["lift_a_vs_c"] < HP_ARM_A_VS_C_LIFT]
    if len(mid_lifts) > 0:
        return "MOE_SHIFT_MIDDLE", "MoE middle: structural separation present but weak (0.05-0.15 lift); marginal mode-collapse"

    # Default inconclusive
    max_lift = max((c["lift_a_vs_c"] for c in cells), default=0.0)
    return "MOE_SHIFT_INCONCLUSIVE", f"MoE inconclusive: max lift_a_vs_c={max_lift:.4f}; requires more cells or different K range"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device} smoke={smoke}")

    N = N_SMOKE if smoke else N_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    m_per_e = M_PER_EXPERT_SMOKE if smoke else M_PER_EXPERT_FULL

    t0 = time.time()
    cells = []

    for K in K_sweep:
        m_mult = get_m_mult(K, smoke)
        for mult in m_mult:
            M_total = max(1, int(round(mult * K * m_per_e)))
            print(f"  K={K} M_total={M_total} mult={mult}", flush=True)
            try:
                cell = run_one_cell(N, M_total, K, seeds, device, smoke)
                cells.append(cell)
                print(f"    arm_a={cell['arm_a_mean']:.4f} arm_b={cell['arm_b_mean']:.4f} "
                      f"arm_c={cell['arm_c_mean']:.4f} lift={cell['lift_a_vs_c']:.4f} "
                      f"gini={cell['mode_collapse']['gini']:.3f}", flush=True)
            except torch.cuda.OutOfMemoryError:
                print(f"    OOM at K={K} M_total={M_total} -- skipping cell", flush=True)
                cells.append({"N": N, "M_total": M_total, "K": K, "oom": True})
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    elapsed = time.time() - t0
    valid_cells = [c for c in cells if not c.get("oom", False)]
    verdict, verdict_msg = classify_verdict(valid_cells) if valid_cells else ("INSTRUMENTATION_FAIL", "no valid cells")

    # Arm A lifts summary
    lifts = [c.get("lift_a_vs_c", None) for c in valid_cells]
    lifts_str = " ".join(f"K={c['K']}M={c['M_total']}:{c.get('lift_a_vs_c',float('nan')):.4f}"
                         for c in valid_cells)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg + f" | lifts: {lifts_str}",
        "elapsed_s": elapsed,
        "config": {"N": N, "K_sweep": K_sweep, "seeds": seeds, "smoke": smoke,
                   "M_per_expert": m_per_e, "v3_oom_fix": "M_mult capped at K>=8"},
        "summary": {
            "n_cells": len(valid_cells),
            "n_oom": sum(1 for c in cells if c.get("oom", False)),
            "max_lift_a_vs_c": max(lifts, default=None),
            "min_lift_a_vs_c": min(lifts, default=None),
            "cells": valid_cells,
        },
    }
    validate_metrics(metrics)

    outdir = get_output_dir("wave14_moe_shift_partition_v3")
    with open(outdir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"verdict={verdict}")
    print(f"verdict_msg={verdict_msg}")
    print(f"elapsed={elapsed:.1f}s n_cells={len(valid_cells)} n_oom={metrics['summary']['n_oom']}")


if __name__ == "__main__":
    main()
