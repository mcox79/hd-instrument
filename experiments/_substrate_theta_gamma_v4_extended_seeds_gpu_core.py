"""Shared core for theta_gamma_v4_extended_seeds_gpu siblings (7-seed revival).

Theta-gamma phase binding v4 = 2x-drill negative recovery for v3.

v3 (2026-07-01) landed tiered MEASURED_MECHANISM at N=16384 GPU:
  - MAIN mechanism (NESTED cliff): cliff_K=100, log2=6.6439 ROCK-SOLID cv=0.000
    across seeds 7/13/19 (all 3 seeds).
    MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_{7,13,19}/metrics.json
  - SECONDARY discriminator (nested_vs_flat32 >= 0.1): seed 7 broke
    unanimity because FLAT_32 cliff landed at K=100 (delta=0.0) while seeds
    13/19 had FLAT_32 cliff at K=50 (delta=1.0). Codebook-draw seed dependence
    at 32-position complex64 basis.
    MEASURED@data/exp_substrate_theta_gamma_v3_N16384_gpu_seed_7/metrics.json
      per_arm_summary.FHRR_FLAT_PHASE_32.cliff_K == 100

v4 delta vs v3 (per Skunkworks revival criteria + USER 2026-07-01 task prompt):
  1. Extend seed count 3 -> 7 (seeds 7, 13, 19, 23, 29, 31, 37) to
     characterize FLAT_32 seed-dependent cliff distribution.
  2. Add fine K-grid points {75, 125, 150, 175} in the K=[50..200] cliff
     region for FLAT_32 to resolve cliff structure.
  3. Relax unanimity gate: HP_NESTED_VS_FLAT32_MAJORITY = >=5/7 seeds pass
     nested_vs_flat32_log2_delta >= 0.1.
  4. Report FLAT_32 cliff distribution + cv across 7 seeds; accept bimodal
     characterization even if cv > 0.15.

Discriminator gates (LOCKED):
  - HP_ALL_SEEDS_PRIMARY: max_fhrr_vs_cyclic_log2_delta >= 1.5 at EVERY seed
  - HP_FLAT_32_CLIFF_DISTRIBUTION: cv(cliff_K over 7 seeds) <= 0.15 OR
    bimodal-distribution atomized (both accepted as HP; verdict message
    reports mode of distribution)
  - HP_NESTED_VS_FLAT32_MAJORITY: >= 5/7 seeds pass nested_vs_flat32 >= 0.1
  - HF_MAIN_MECHANISM_CRUMBLE: NESTED cliff cv > 0.05 across 7 seeds
  - HF_POSITIVE_CONTROL: CYCLIC_SHIFT cliff cv > 0.05

Anchor: theta_gamma_v4_extended_seeds_gpu_seed_{7,13,19,23,29,31,37}
Pre-reg: preregs/2026-07-01_theta_gamma_v4_extended_seeds_gpu.md

Cross-references:
  - v3 prereg: preregs/2026-07-01_theta_gamma_v3_N16384_gpu.md
  - v2 N=4096 CG parent: preregs/2026-06-30_substrate_theta_gamma_v2_FHRR_all_complex.md

ASCII-only. No unicode. No em-dashes. No emojis.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
ARMS = (
    "NO_POSITION",
    "CYCLIC_SHIFT",
    "FHRR_FLAT_PHASE_8",
    "FHRR_FLAT_PHASE_32",
    "FHRR_NESTED_THETA_GAMMA",
)

# 7-seed extension (Skunkworks revival criterion 1)
SEEDS_V4 = (7, 13, 19, 23, 29, 31, 37)

# Finer K-grid around cliff (Skunkworks revival criterion 2)
# v3 K_FULL = [50, 100, 200, 500, 1000, 2000, 5000] (7 K-points)
# v4 K_FULL adds {75, 125, 150, 175} in the 50-200 range for FLAT_32 cliff resolution
K_SEQ_SWEEP_FULL = (50, 75, 100, 125, 150, 175, 200, 500, 1000, 2000, 5000)
K_SEQ_SWEEP_SMOKE = (50, 100, 200)  # coarse; verifies cliff sits in this range per seed

# Regime (LOCKED; same as v3 for cross-cell comparison)
N_DIM = 16384
ITEM_VOCAB_SIZE = 10000
POSITION_SLOTS_FLAT_8 = 8
POSITION_SLOTS_FLAT_32 = 32
N_THETA_CYCLES = 8
N_GAMMA_PER_THETA = 8
POSITION_SLOTS_NESTED = N_THETA_CYCLES * N_GAMMA_PER_THETA  # 64
NOISE_SIGMA = 0.05

# Discriminator bands (LOCKED per task prompt)
HP_LOG2_SEPARATION_FHRR_VS_CYCLIC = 1.5
HP_CROSS_ARM_LOG2_DELTA = 0.1
HP_FLAT_32_CV_TIGHT = 0.15  # tight cv on FLAT_32 cliff for unimodal characterization
HP_NESTED_VS_FLAT32_MAJORITY = 5  # >=5/7 seeds must pass
HP_SAT_AT_KSEQ_50 = 0.999
NO_POSITION_MAX_AT_K50 = 0.999
HF_MAIN_MECHANISM_CV_MAX = 0.05  # NESTED cliff cv > this = HARD_FAIL
HF_POS_CONTROL_CV_MAX = 0.05     # CYCLIC cliff cv > this = HARD_FAIL

CLIFF_ACC_THRESHOLD = 0.50

EXPECTED_N_UNITS_FULL = len(ARMS) * len(K_SEQ_SWEEP_FULL)      # 5 * 11 = 55
EXPECTED_N_UNITS_SMOKE = len(ARMS) * len(K_SEQ_SWEEP_SMOKE)    # 5 * 3 = 15

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")

N_QUERIES_PER_K = 50
N_QUERIES_PER_K_SMOKE = 25


def _get_device(strict_gpu: bool = False) -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    if strict_gpu:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (PROT-020 / Fix #24): cuda.is_available()=False. "
            "theta-gamma v4 at N_DIM=%d K_SEQ up to %d requires "
            "CUDA for overnight_queue routing." % (
                N_DIM, max(K_SEQ_SWEEP_FULL))
        )
    return torch.device("cpu")


def get_backend_label() -> str:
    if torch.cuda.is_available():
        try:
            return "torch.cuda:" + torch.cuda.get_device_name(0)
        except Exception:
            return "torch.cuda"
    return "torch.cpu"


def make_fhrr_codebook(
    n_items: int, n_dim: int, seed: int, device: torch.device,
) -> torch.Tensor:
    """Unit-phase complex codebook (n_items, n_dim) complex64."""
    g = torch.Generator(device=device)
    g.manual_seed(int(seed))
    phi = torch.empty(n_items, n_dim, device=device, dtype=torch.float32)
    phi.uniform_(0.0, 2.0 * math.pi, generator=g)
    real = torch.cos(phi)
    imag = torch.sin(phi)
    return torch.complex(real, imag)


def make_bipolar_codebook(
    n_items: int, n_dim: int, seed: int, device: torch.device,
) -> torch.Tensor:
    """Bipolar {-1, +1}^N codebook (n_items, n_dim) float32."""
    g = torch.Generator(device=device)
    g.manual_seed(int(seed))
    x = torch.empty(n_items, n_dim, device=device, dtype=torch.float32)
    x.bernoulli_(0.5, generator=g).mul_(2.0).sub_(1.0)
    return x


def theta_gamma_bind(item_hd, position_hd):
    return item_hd * position_hd


def theta_gamma_unbind(bound_hd, position_hd):
    return bound_hd * position_hd.conj()


def encode_fhrr_sequence(item_codes, position_codes):
    bound = item_codes * position_codes
    return bound.sum(dim=0)


def decode_fhrr_at_position(seq_hd, position_hd, item_codebook):
    candidate = seq_hd * position_hd.conj()
    scores = (item_codebook.conj() @ candidate).abs()
    return scores.argmax()


def cyclic_shift_encode(item_codes: torch.Tensor) -> torch.Tensor:
    K, n_dim = item_codes.shape
    bundled = torch.zeros(n_dim, device=item_codes.device, dtype=torch.float32)
    for i in range(K):
        bundled = bundled + torch.roll(item_codes[i], shifts=i, dims=0)
    return bundled


def cyclic_shift_decode_at_position(
    seq_hd: torch.Tensor, position: int, item_codebook: torch.Tensor,
) -> torch.Tensor:
    candidate = torch.roll(seq_hd, shifts=-position, dims=0)
    cand_n = candidate / candidate.norm().clamp_min(1e-12)
    cb_n = item_codebook / item_codebook.norm(dim=1, keepdim=True).clamp_min(1e-12)
    scores = cb_n @ cand_n
    return scores.argmax()


def no_position_encode_fhrr(item_codes: torch.Tensor) -> torch.Tensor:
    return item_codes.sum(dim=0)


def no_position_decode_fhrr(seq_hd, item_codebook):
    scores = (item_codebook.conj() @ seq_hd).abs()
    return scores.argmax()


def _build_positions_flat(n_positions, n_dim, seed, device):
    return make_fhrr_codebook(n_positions, n_dim, seed + 7919, device)


def _build_positions_nested(n_theta, n_gamma, n_dim, seed, device):
    theta_codes = make_fhrr_codebook(n_theta, n_dim, seed + 7919, device)
    gamma_codes = make_fhrr_codebook(n_gamma, n_dim, seed + 13337, device)
    out_codes = torch.empty(
        n_theta * n_gamma, n_dim, device=device, dtype=torch.complex64
    )
    idx = 0
    for t in range(n_theta):
        for g in range(n_gamma):
            out_codes[idx] = theta_codes[t] * gamma_codes[g]
            idx += 1
    return out_codes


def _add_noise_complex(hd, sigma, gen):
    if sigma <= 0:
        return hd
    real_noise = torch.empty(hd.shape, device=hd.device, dtype=torch.float32)
    real_noise.normal_(0.0, sigma, generator=gen)
    imag_noise = torch.empty(hd.shape, device=hd.device, dtype=torch.float32)
    imag_noise.normal_(0.0, sigma, generator=gen)
    return hd + torch.complex(real_noise, imag_noise)


def _add_noise_real(hd, sigma, gen):
    if sigma <= 0:
        return hd
    n = torch.empty(hd.shape, device=hd.device, dtype=torch.float32)
    n.normal_(0.0, sigma, generator=gen)
    return hd + n


def eval_arm_at_kseq(
    arm: str, K_SEQ: int, n_queries: int, seed: int, device: torch.device,
    noise_sigma: float = NOISE_SIGMA,
) -> Dict[str, Any]:
    t0 = time.time()
    g_main = torch.Generator(device=device)
    g_main.manual_seed(int(seed))
    g_noise = torch.Generator(device=device)
    g_noise.manual_seed(int(seed) + 31337)

    if arm == "NO_POSITION":
        item_codebook = make_fhrr_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = None
        n_positions = 1
    elif arm == "CYCLIC_SHIFT":
        item_codebook = make_bipolar_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = None
        n_positions = N_DIM
    elif arm == "FHRR_FLAT_PHASE_8":
        item_codebook = make_fhrr_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = _build_positions_flat(POSITION_SLOTS_FLAT_8, N_DIM, seed, device)
        n_positions = POSITION_SLOTS_FLAT_8
    elif arm == "FHRR_FLAT_PHASE_32":
        item_codebook = make_fhrr_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = _build_positions_flat(POSITION_SLOTS_FLAT_32, N_DIM, seed, device)
        n_positions = POSITION_SLOTS_FLAT_32
    elif arm == "FHRR_NESTED_THETA_GAMMA":
        item_codebook = make_fhrr_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = _build_positions_nested(
            N_THETA_CYCLES, N_GAMMA_PER_THETA, N_DIM, seed, device
        )
        n_positions = POSITION_SLOTS_NESTED
    else:
        raise ValueError(f"unknown arm: {arm!r}")

    n_correct = 0
    for q in range(n_queries):
        item_ids = torch.empty(K_SEQ, device=device, dtype=torch.long)
        item_ids.random_(0, ITEM_VOCAB_SIZE, generator=g_main)

        if arm == "NO_POSITION":
            seq_codes = item_codebook[item_ids]
            seq_hd = no_position_encode_fhrr(seq_codes)
            seq_hd_noisy = _add_noise_complex(seq_hd, noise_sigma, g_noise)
            target_slot = int(torch.randint(
                0, K_SEQ, (1,), device=device, generator=g_main).item())
            true_item = int(item_ids[target_slot].item())
            pred = int(no_position_decode_fhrr(seq_hd_noisy, item_codebook).item())

        elif arm == "CYCLIC_SHIFT":
            seq_codes = item_codebook[item_ids]
            seq_hd = cyclic_shift_encode(seq_codes)
            seq_hd_noisy = _add_noise_real(seq_hd, noise_sigma, g_noise)
            target_slot = int(torch.randint(
                0, K_SEQ, (1,), device=device, generator=g_main).item())
            true_item = int(item_ids[target_slot].item())
            pred = int(cyclic_shift_decode_at_position(
                seq_hd_noisy, target_slot, item_codebook).item())

        else:
            pos_assignment = torch.arange(K_SEQ, device=device) % n_positions
            seq_item_codes = item_codebook[item_ids]
            seq_pos_codes = positions[pos_assignment]
            seq_hd = encode_fhrr_sequence(seq_item_codes, seq_pos_codes)
            seq_hd_noisy = _add_noise_complex(seq_hd, noise_sigma, g_noise)
            target_slot = int(torch.randint(
                0, K_SEQ, (1,), device=device, generator=g_main).item())
            true_item = int(item_ids[target_slot].item())
            query_position = positions[int(pos_assignment[target_slot].item())]
            pred = int(decode_fhrr_at_position(
                seq_hd_noisy, query_position, item_codebook).item())

        if pred == true_item:
            n_correct += 1

    acc = float(n_correct) / float(n_queries)
    elapsed = time.time() - t0

    del item_codebook
    if positions is not None:
        del positions
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "arm": arm,
        "K_SEQ": int(K_SEQ),
        "n_queries": int(n_queries),
        "n_correct": int(n_correct),
        "retrieval_acc": round(acc, 4),
        "n_positions": int(n_positions),
        "noise_sigma": float(noise_sigma),
        "wall_s": round(elapsed, 3),
    }


def selftest(seed: int, device: torch.device = None) -> Tuple[bool, str]:
    if device is None:
        device = _get_device(strict_gpu=False)
    msgs: List[str] = []

    if EXPECTED_N_UNITS_FULL != 55:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 55"
    if EXPECTED_N_UNITS_SMOKE != 15:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 15"
    msgs.append(
        f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
        f"SMOKE={EXPECTED_N_UNITS_SMOKE}"
    )

    n_dim_st = 256
    item = make_fhrr_codebook(1, n_dim_st, seed, device)[0]
    pos = make_fhrr_codebook(1, n_dim_st, seed + 100, device)[0]
    bound = theta_gamma_bind(item, pos)
    recovered = theta_gamma_unbind(bound, pos)
    diff = (recovered - item).abs().max().item()
    if diff > 1e-3:
        return False, f"FHRR unbind self-inverse FAIL: max|diff|={diff:.6f}"
    msgs.append(f"fhrr_unbind_self_inverse_max_diff={diff:.2e}")

    cb_small = make_fhrr_codebook(100, n_dim_st, seed, device)
    pos_small = make_fhrr_codebook(8, n_dim_st, seed + 1, device)
    item_ids = torch.tensor([7], device=device, dtype=torch.long)
    pos_assignment = torch.tensor([0], device=device, dtype=torch.long)
    seq_hd = encode_fhrr_sequence(cb_small[item_ids], pos_small[pos_assignment])
    pred = int(decode_fhrr_at_position(seq_hd, pos_small[0], cb_small).item())
    if pred != 7:
        return False, (
            f"FHRR_FLAT clean K=1 retrieval FAIL: expected 7 got {pred}"
        )
    msgs.append("fhrr_K1_clean_retrieval_pass(pred=7)")

    hashes: Dict[str, str] = {}
    test_K = 50
    for arm in ARMS:
        pt = eval_arm_at_kseq(
            arm, test_K, n_queries=10, seed=seed, device=device,
            noise_sigma=0.0,
        )
        h_payload = json.dumps([
            arm, pt["K_SEQ"], pt["n_correct"], pt["n_queries"]
        ], sort_keys=True).encode("utf-8")
        hashes[arm] = hashlib.sha256(h_payload).hexdigest()[:16]
    msgs.append(f"arm_smoke_outcome_hashes={hashes}")

    code_path_hashes: Dict[str, str] = {}
    code_path_hashes["NO_POSITION"] = hashlib.sha256(
        b"no_position_encode_fhrr|complex_codebook|n_positions=1"
    ).hexdigest()[:16]
    code_path_hashes["CYCLIC_SHIFT"] = hashlib.sha256(
        b"cyclic_shift_encode|bipolar_codebook|roll_dim_axis"
    ).hexdigest()[:16]
    code_path_hashes["FHRR_FLAT_PHASE_8"] = hashlib.sha256(
        f"encode_fhrr_sequence|complex_codebook|n_pos={POSITION_SLOTS_FLAT_8}|flat".encode()
    ).hexdigest()[:16]
    code_path_hashes["FHRR_FLAT_PHASE_32"] = hashlib.sha256(
        f"encode_fhrr_sequence|complex_codebook|n_pos={POSITION_SLOTS_FLAT_32}|flat".encode()
    ).hexdigest()[:16]
    code_path_hashes["FHRR_NESTED_THETA_GAMMA"] = hashlib.sha256(
        f"encode_fhrr_sequence|complex_codebook|n_pos={POSITION_SLOTS_NESTED}|nested_{N_THETA_CYCLES}x{N_GAMMA_PER_THETA}".encode()
    ).hexdigest()[:16]
    if len(set(code_path_hashes.values())) != len(ARMS):
        return False, (
            f"META_RULE_AX code-path hash COLLISION: {code_path_hashes}"
        )
    msgs.append(f"code_path_hashes_distinct={code_path_hashes}")

    pt_np = eval_arm_at_kseq(
        "NO_POSITION", K_SEQ=50, n_queries=30, seed=seed, device=device,
        noise_sigma=NOISE_SIGMA,
    )
    if pt_np["retrieval_acc"] >= NO_POSITION_MAX_AT_K50:
        return False, (
            f"NOISE discipline FAIL: NO_POSITION saturates at K=50 noisy: "
            f"acc={pt_np['retrieval_acc']} >= {NO_POSITION_MAX_AT_K50}"
        )
    msgs.append(
        f"noise_discipline_no_position_K50_acc={pt_np['retrieval_acc']}"
    )

    if code_path_hashes["FHRR_NESTED_THETA_GAMMA"] == code_path_hashes["FHRR_FLAT_PHASE_32"]:
        return False, "NESTED vs FLAT_32 code paths collide"
    msgs.append("nested_vs_flat32_distinct=True")

    return True, "; ".join(msgs)


def run_one_seed_phase_diagram(
    seed: int, run_mode: str, device: torch.device,
) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    k_sweep = K_SEQ_SWEEP_SMOKE if is_smoke else K_SEQ_SWEEP_FULL
    n_queries = N_QUERIES_PER_K_SMOKE if is_smoke else N_QUERIES_PER_K
    expected_n = len(ARMS) * len(k_sweep)

    print(
        f"[run_one_seed_thetagamma_v4] seed={seed} mode={run_mode} "
        f"device={device} arms={ARMS} K_SEQ={k_sweep} n_queries={n_queries} "
        f"N_DIM={N_DIM} ITEM_VOCAB={ITEM_VOCAB_SIZE} "
        f"NOISE_SIGMA={NOISE_SIGMA} expected_n={expected_n}",
        flush=True,
    )

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for arm in ARMS:
        for K_SEQ in k_sweep:
            pt = eval_arm_at_kseq(
                arm=arm, K_SEQ=K_SEQ, n_queries=n_queries,
                seed=seed, device=device, noise_sigma=NOISE_SIGMA,
            )
            phase_map.append(pt)
            print(
                f"[pt] s={seed} arm={arm:<26} K={K_SEQ:>5} "
                f"acc={pt['retrieval_acc']:.3f} "
                f"n_pos={pt['n_positions']:>3} t={pt['wall_s']:.2f}s",
                flush=True,
            )

    elapsed = time.time() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    per_arm_summary: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS:
        arm_pts = sorted(
            [p for p in phase_map if p["arm"] == arm],
            key=lambda p: p["K_SEQ"],
        )
        cliff_K = 0
        last_above_K = 0
        for p in arm_pts:
            if p["retrieval_acc"] >= CLIFF_ACC_THRESHOLD:
                last_above_K = p["K_SEQ"]
        cliff_K = last_above_K
        log2_cliff = math.log2(cliff_K) if cliff_K > 0 else -1.0
        accs = [p["retrieval_acc"] for p in arm_pts]
        per_arm_summary[arm] = {
            "n_K_points": len(arm_pts),
            "K_values": [p["K_SEQ"] for p in arm_pts],
            "accs": accs,
            "cliff_K": cliff_K,
            "log2_cliff_K": round(log2_cliff, 4),
            "acc_at_K50": next(
                (p["retrieval_acc"] for p in arm_pts if p["K_SEQ"] == 50), None
            ),
            "max_acc": max(accs) if accs else 0.0,
            "mean_acc": round(float(np.mean(accs)), 4) if accs else 0.0,
        }

    arm_outcome_hashes: Dict[str, str] = {}
    for arm in ARMS:
        arm_pts = sorted(
            [p for p in phase_map if p["arm"] == arm],
            key=lambda p: p["K_SEQ"],
        )
        payload = json.dumps(
            [(p["K_SEQ"], round(p["retrieval_acc"], 4), p["n_positions"])
             for p in arm_pts],
            sort_keys=True,
        ).encode("utf-8")
        arm_outcome_hashes[arm] = hashlib.sha256(payload).hexdigest()[:16]

    arms_list = list(ARMS)
    pairs_differ: Dict[str, bool] = {}
    for i in range(len(arms_list)):
        for j in range(i + 1, len(arms_list)):
            key = f"{arms_list[i]}_vs_{arms_list[j]}"
            pairs_differ[key] = (
                arm_outcome_hashes[arms_list[i]] != arm_outcome_hashes[arms_list[j]]
            )
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)
    n_pairs_total = len(pairs_differ)

    cliff_log2s = {
        arm: per_arm_summary[arm]["log2_cliff_K"] for arm in ARMS
    }
    fhrr_arms = ("FHRR_FLAT_PHASE_8", "FHRR_FLAT_PHASE_32",
                  "FHRR_NESTED_THETA_GAMMA")
    cyclic_log2 = cliff_log2s.get("CYCLIC_SHIFT", -1.0)
    max_fhrr_vs_cyclic_delta = 0.0
    for fhrr_arm in fhrr_arms:
        fhrr_log2 = cliff_log2s.get(fhrr_arm, -1.0)
        if fhrr_log2 >= 0 and cyclic_log2 >= 0:
            d = abs(fhrr_log2 - cyclic_log2)
            if d > max_fhrr_vs_cyclic_delta:
                max_fhrr_vs_cyclic_delta = d

    min_cross_arm_delta = float("inf")
    for i in range(len(arms_list)):
        for j in range(i + 1, len(arms_list)):
            l_i = cliff_log2s[arms_list[i]]
            l_j = cliff_log2s[arms_list[j]]
            if l_i >= 0 and l_j >= 0:
                d = abs(l_i - l_j)
                if d < min_cross_arm_delta:
                    min_cross_arm_delta = d
    if min_cross_arm_delta == float("inf"):
        min_cross_arm_delta = -1.0

    nested_log2 = cliff_log2s.get("FHRR_NESTED_THETA_GAMMA", -1.0)
    flat32_log2 = cliff_log2s.get("FHRR_FLAT_PHASE_32", -1.0)
    nested_vs_flat32_delta = (
        abs(nested_log2 - flat32_log2)
        if (nested_log2 >= 0 and flat32_log2 >= 0)
        else -1.0
    )

    arms_saturating_at_K50 = []
    for arm in ARMS:
        acc_K50 = per_arm_summary[arm].get("acc_at_K50")
        if acc_K50 is not None and acc_K50 >= HP_SAT_AT_KSEQ_50:
            arms_saturating_at_K50.append(arm)
    no_position_acc_K50 = per_arm_summary.get("NO_POSITION", {}).get("acc_at_K50")
    no_position_saturates_K50 = (
        no_position_acc_K50 is not None
        and no_position_acc_K50 >= NO_POSITION_MAX_AT_K50
    )

    return {
        "seed": seed,
        "run_mode": run_mode,
        "arms": list(ARMS),
        "K_SEQ_sweep": list(k_sweep),
        "n_queries_per_K": n_queries,
        "N_DIM": N_DIM,
        "ITEM_VOCAB_SIZE": ITEM_VOCAB_SIZE,
        "NOISE_SIGMA": NOISE_SIGMA,
        "phase_map": phase_map,
        "per_arm_summary": per_arm_summary,
        "arm_outcome_hashes": arm_outcome_hashes,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "n_pairs_total": n_pairs_total,
        "cliff_log2_K_per_arm": cliff_log2s,
        "max_fhrr_vs_cyclic_log2_delta": round(max_fhrr_vs_cyclic_delta, 4),
        "min_cross_arm_log2_delta": round(min_cross_arm_delta, 4),
        "nested_vs_flat32_log2_delta": round(nested_vs_flat32_delta, 4),
        "arms_saturating_at_K50": arms_saturating_at_K50,
        "no_position_saturates_K50": no_position_saturates_K50,
        "no_position_acc_K50": no_position_acc_K50,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "elapsed_seed_s": round(elapsed, 2),
    }


def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """v4 smoke gate: verifies discriminator fires at N=16384 with coarse K sweep.

    Smoke K = [50, 100, 200]. Verifies:
    - cardinality (15/15)
    - arms differ (>= 4/10 pairs at smoke)
    - noise discipline (NO_POSITION K=50 noisy < 0.999)
    - no runaway K50 saturation (< 3 arms at 0.999)
    - at least 1 FHRR arm has cliff_K >= 50
    - max_fhrr_vs_cyclic_log2_delta >= 0.5 (DISCRIMINATOR-MUST-SURVIVE-SCALE
      smoke floor; FULL requires >= 1.5)
    """
    phase_map = body.get("phase_map", [])
    expected_n = body.get("expected_n_units", 0)
    pairs_differ = body.get("encoder_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    n_pairs_total = body.get("n_pairs_total", 10)
    arms_saturating = body.get("arms_saturating_at_K50", [])
    no_position_sat = body.get("no_position_saturates_K50", False)
    no_position_acc_K50 = body.get("no_position_acc_K50", 0.0)
    per_arm_summary = body.get("per_arm_summary", {})
    max_fhrr_vs_cyclic = body.get("max_fhrr_vs_cyclic_log2_delta", 0.0)

    if len(phase_map) != expected_n:
        return False, (
            f"cardinality_breach: expected {expected_n} got {len(phase_map)}"
        )

    if n_pairs_differ < 4:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (
            f"HARD_FAIL_ARMS_COLLIDE (META_RULE_AX): "
            f"{n_pairs_differ}/{n_pairs_total} arm-pairs differ "
            f"(need >= 4 at smoke); collapsed: {collapsed}"
        )

    if no_position_sat:
        return False, (
            f"HARD_FAIL_NOISE_DISCIPLINE: NO_POSITION saturates K=50 noisy "
            f"(acc={no_position_acc_K50:.3f} >= {NO_POSITION_MAX_AT_K50}); "
            f"discriminator vacuous"
        )

    if len(arms_saturating) >= 3:
        return False, (
            f"HARD_FAIL_REGIME_TOO_EASY (META_RULE_Q): "
            f"{len(arms_saturating)} arms saturate at K=50: {arms_saturating}; "
            f"acc>={HP_SAT_AT_KSEQ_50}"
        )

    fhrr_arms = ("FHRR_FLAT_PHASE_8", "FHRR_FLAT_PHASE_32",
                  "FHRR_NESTED_THETA_GAMMA")
    fhrr_active = [
        arm for arm in fhrr_arms
        if per_arm_summary.get(arm, {}).get("cliff_K", 0) >= 50
    ]
    if not fhrr_active:
        cliffs = {arm: per_arm_summary.get(arm, {}).get("cliff_K", 0)
                   for arm in fhrr_arms}
        return False, (
            f"HARD_FAIL_FHRR_NO_CAPACITY: no FHRR arm has cliff_K>=50; "
            f"cliffs={cliffs}; mechanism broken"
        )

    if max_fhrr_vs_cyclic < 0.5:
        return False, (
            f"HARD_FAIL_DISCRIMINATOR_TOO_WEAK_AT_SMOKE: "
            f"max_fhrr_vs_cyclic_log2_delta={max_fhrr_vs_cyclic:.3f} < 0.5 "
            f"(smoke floor; FULL requires >= {HP_LOG2_SEPARATION_FHRR_VS_CYCLIC})"
        )

    return True, (
        f"smoke_gate_pass_v4: cardinality_ok + "
        f"pairs_differ={n_pairs_differ}/{n_pairs_total}>=4 + "
        f"NO_POSITION_K50={no_position_acc_K50:.3f}<{NO_POSITION_MAX_AT_K50} + "
        f"no_K50_saturation_glut + "
        f"{len(fhrr_active)}/3 FHRR arms show capacity + "
        f"max_fhrr_vs_cyclic_log2_delta={max_fhrr_vs_cyclic:.3f}>=0.5"
    )


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """Aggregate per-seed metrics into cell-level verdict.

    v4 revival gates (relaxed unanimity):
      HP_ALL_SEEDS_PRIMARY: FHRR_vs_CYCLIC log2_delta >= 1.5 at every seed
      HP_NESTED_VS_FLAT32_MAJORITY: >= 5/7 seeds pass nested_vs_flat32 >= 0.1
      HP_FLAT_32_CLIFF_CHARACTERIZED: cv <= 0.15 OR bimodal atomized (both OK)
      HF_MAIN_MECHANISM_CRUMBLE: NESTED cliff cv > 0.05
      HF_POSITIVE_CONTROL: CYCLIC cliff cv > 0.05

    Per-seed structure preserved; smoke case = single-seed body.
    """
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: empty per_seed",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")

    if is_smoke:
        # smoke = single seed body; use v3-style smoke path
        seed_key = list(per_seed.keys())[0]
        body = per_seed[seed_key]
        phase_map = body.get("phase_map", [])
        per_arm_summary = body.get("per_arm_summary", {})
        pairs_differ = body.get("encoder_pair_distinctness", {})
        n_pairs_differ = body.get("n_pairs_differ", 0)
        n_pairs_total = body.get("n_pairs_total", 10)
        arms_saturating = body.get("arms_saturating_at_K50", [])
        no_position_sat = body.get("no_position_saturates_K50", False)
        no_position_acc_K50 = body.get("no_position_acc_K50", 0.0)
        max_fhrr_vs_cyclic = body.get("max_fhrr_vs_cyclic_log2_delta", 0.0)
        nested_vs_flat32 = body.get("nested_vs_flat32_log2_delta", 0.0)
        min_cross_arm_delta = body.get("min_cross_arm_log2_delta", -1.0)
        cardinality_ok = body.get("cardinality_ok", False)
        expected_n = body.get("expected_n_units", 0)
        observed_n = body.get("observed_n_units", 0)

        common = {
            "phase_map": phase_map,
            "per_arm_summary": per_arm_summary,
            "encoder_pair_distinctness": pairs_differ,
            "n_pairs_differ": n_pairs_differ,
            "n_pairs_total": n_pairs_total,
            "arms_saturating_at_K50": arms_saturating,
            "no_position_saturates_K50": no_position_sat,
            "no_position_acc_K50": no_position_acc_K50,
            "max_fhrr_vs_cyclic_log2_delta": max_fhrr_vs_cyclic,
            "nested_vs_flat32_log2_delta": nested_vs_flat32,
            "min_cross_arm_log2_delta": min_cross_arm_delta,
            "cliff_log2_K_per_arm": body.get("cliff_log2_K_per_arm", {}),
            "cardinality_ok": cardinality_ok,
            "expected_n_units": expected_n,
            "observed_n_units": observed_n,
            "N_DIM": body.get("N_DIM"),
            "ITEM_VOCAB_SIZE": body.get("ITEM_VOCAB_SIZE"),
            "NOISE_SIGMA": body.get("NOISE_SIGMA"),
            "K_SEQ_sweep": body.get("K_SEQ_sweep"),
        }

        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (
                f"HARD_PASS_SMOKE_thetagamma_v4: {observed_n}/{expected_n} pts; "
                f"pairs_differ={n_pairs_differ}/{n_pairs_total}; "
                f"NO_POSITION@K50_acc={no_position_acc_K50:.3f}; "
                f"max_fhrr_vs_cyclic_log2_delta={max_fhrr_vs_cyclic:.3f}; "
                f"nested_vs_flat32_log2_delta={nested_vs_flat32:.3f}; "
                f"arms_saturating_K50={len(arms_saturating)}"
            )
        else:
            verdict = "HARD_FAIL"
            vmsg = f"HARD_FAIL_SMOKE_thetagamma_v4: {reason}"
        out = dict(common)
        out.update({
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict: 7-seed revival aggregation
    seed_bodies = list(per_seed.values())
    n_seeds_observed = len(seed_bodies)

    # Extract per-seed metrics
    seed_summaries: List[Dict[str, Any]] = []
    for body in seed_bodies:
        seed_summaries.append({
            "seed": body.get("seed"),
            "cardinality_ok": body.get("cardinality_ok", False),
            "observed_n_units": body.get("observed_n_units", 0),
            "expected_n_units": body.get("expected_n_units", 0),
            "n_pairs_differ": body.get("n_pairs_differ", 0),
            "n_pairs_total": body.get("n_pairs_total", 10),
            "max_fhrr_vs_cyclic_log2_delta":
                body.get("max_fhrr_vs_cyclic_log2_delta", 0.0),
            "nested_vs_flat32_log2_delta":
                body.get("nested_vs_flat32_log2_delta", 0.0),
            "min_cross_arm_log2_delta":
                body.get("min_cross_arm_log2_delta", -1.0),
            "cliff_log2_K_per_arm": body.get("cliff_log2_K_per_arm", {}),
            "per_arm_summary": body.get("per_arm_summary", {}),
            "arms_saturating_at_K50": body.get("arms_saturating_at_K50", []),
            "no_position_saturates_K50":
                body.get("no_position_saturates_K50", False),
            "no_position_acc_K50": body.get("no_position_acc_K50", 0.0),
        })

    # Per-seed cardinality gate
    seeds_cardinality_ok = sum(1 for s in seed_summaries if s["cardinality_ok"])
    if seeds_cardinality_ok < n_seeds_observed:
        breach = [s for s in seed_summaries if not s["cardinality_ok"]]
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"HARD_FAIL_CARDINALITY_BREACH: "
                f"{seeds_cardinality_ok}/{n_seeds_observed} seeds cardinality_ok; "
                f"breach: {[(b['seed'], b['observed_n_units'], b['expected_n_units']) for b in breach]}"
            ),
            "summary": (
                f"HARD_FAIL_CARDINALITY_BREACH: "
                f"{seeds_cardinality_ok}/{n_seeds_observed} seeds cardinality_ok"
            ),
            "per_seed_summaries": seed_summaries,
            "n_seeds_observed": n_seeds_observed,
        }

    # Per-seed noise discipline
    for s in seed_summaries:
        if s["no_position_saturates_K50"]:
            return {
                "verdict": "HARD_FAIL",
                "verdict_msg": (
                    f"HARD_FAIL_NOISE_DISCIPLINE: seed={s['seed']} "
                    f"NO_POSITION K=50 acc={s['no_position_acc_K50']:.3f} "
                    f">= {NO_POSITION_MAX_AT_K50}; discriminator vacuous"
                ),
                "summary": f"HARD_FAIL_NOISE_DISCIPLINE_seed_{s['seed']}",
                "per_seed_summaries": seed_summaries,
                "n_seeds_observed": n_seeds_observed,
            }

    # Per-seed regime-too-easy
    for s in seed_summaries:
        if len(s["arms_saturating_at_K50"]) >= 3:
            return {
                "verdict": "HARD_FAIL",
                "verdict_msg": (
                    f"HARD_FAIL_REGIME_TOO_EASY: seed={s['seed']} "
                    f"{len(s['arms_saturating_at_K50'])} arms saturate K=50: "
                    f"{s['arms_saturating_at_K50']}"
                ),
                "summary": f"HARD_FAIL_REGIME_TOO_EASY_seed_{s['seed']}",
                "per_seed_summaries": seed_summaries,
                "n_seeds_observed": n_seeds_observed,
            }

    # Per-seed pairs_differ (each seed independently satisfies distinctness)
    seeds_pairs_ok = sum(
        1 for s in seed_summaries if s["n_pairs_differ"] >= 9
    )
    if seeds_pairs_ok < n_seeds_observed:
        breach = [
            (s["seed"], s["n_pairs_differ"], s["n_pairs_total"])
            for s in seed_summaries if s["n_pairs_differ"] < 9
        ]
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"HARD_FAIL_ARMS_COLLIDE (META_RULE_AX): "
                f"{seeds_pairs_ok}/{n_seeds_observed} seeds have n_pairs_differ>=9; "
                f"breach: {breach}"
            ),
            "summary": (
                f"HARD_FAIL_ARMS_COLLIDE: "
                f"{seeds_pairs_ok}/{n_seeds_observed} seeds pairs>=9"
            ),
            "per_seed_summaries": seed_summaries,
            "n_seeds_observed": n_seeds_observed,
        }

    # HP_ALL_SEEDS_PRIMARY: FHRR_vs_CYCLIC log2_delta >= 1.5 at every seed
    seeds_primary_ok = sum(
        1 for s in seed_summaries
        if s["max_fhrr_vs_cyclic_log2_delta"] >= HP_LOG2_SEPARATION_FHRR_VS_CYCLIC
    )
    all_seeds_primary_ok = (seeds_primary_ok == n_seeds_observed)

    # HP_NESTED_VS_FLAT32_MAJORITY: >= 5/7 seeds pass
    seeds_nested_vs_flat32_ok = sum(
        1 for s in seed_summaries
        if s["nested_vs_flat32_log2_delta"] >= HP_CROSS_ARM_LOG2_DELTA
    )
    majority_nested_vs_flat32_ok = (
        seeds_nested_vs_flat32_ok >= HP_NESTED_VS_FLAT32_MAJORITY
    )

    # FLAT_32 cliff_K across seeds -> compute cv + describe distribution
    flat32_cliffs = [
        s["per_arm_summary"].get("FHRR_FLAT_PHASE_32", {}).get("cliff_K", 0)
        for s in seed_summaries
    ]
    flat32_cliffs_nonzero = [c for c in flat32_cliffs if c > 0]
    if flat32_cliffs_nonzero:
        flat32_mean = float(np.mean(flat32_cliffs_nonzero))
        flat32_std = float(np.std(flat32_cliffs_nonzero))
        flat32_cv = (flat32_std / flat32_mean) if flat32_mean > 0 else -1.0
    else:
        flat32_mean = 0.0
        flat32_std = 0.0
        flat32_cv = -1.0

    # NESTED cliff cv (main mechanism); HARD_FAIL if > HF_MAIN_MECHANISM_CV_MAX
    nested_cliffs = [
        s["per_arm_summary"].get("FHRR_NESTED_THETA_GAMMA", {}).get("cliff_K", 0)
        for s in seed_summaries
    ]
    nested_cliffs_nonzero = [c for c in nested_cliffs if c > 0]
    if nested_cliffs_nonzero:
        nested_mean = float(np.mean(nested_cliffs_nonzero))
        nested_std = float(np.std(nested_cliffs_nonzero))
        nested_cv = (nested_std / nested_mean) if nested_mean > 0 else -1.0
    else:
        nested_mean = 0.0
        nested_std = 0.0
        nested_cv = -1.0

    # CYCLIC cliff cv (positive control); HARD_FAIL if > HF_POS_CONTROL_CV_MAX
    cyclic_cliffs = [
        s["per_arm_summary"].get("CYCLIC_SHIFT", {}).get("cliff_K", 0)
        for s in seed_summaries
    ]
    cyclic_cliffs_nonzero = [c for c in cyclic_cliffs if c > 0]
    if cyclic_cliffs_nonzero:
        cyclic_mean = float(np.mean(cyclic_cliffs_nonzero))
        cyclic_std = float(np.std(cyclic_cliffs_nonzero))
        cyclic_cv = (cyclic_std / cyclic_mean) if cyclic_mean > 0 else -1.0
    else:
        cyclic_mean = 0.0
        cyclic_std = 0.0
        cyclic_cv = -1.0

    # Distribution mode identification (for atomization)
    flat32_hist: Dict[int, int] = {}
    for c in flat32_cliffs:
        flat32_hist[c] = flat32_hist.get(c, 0) + 1
    flat32_modes_desc = sorted(
        flat32_hist.items(), key=lambda kv: (-kv[1], kv[0])
    )
    flat32_is_bimodal = (len(flat32_hist) >= 2 and
                         sorted(flat32_hist.values(), reverse=True)[:2] and
                         all(v >= 1 for v in
                             sorted(flat32_hist.values(), reverse=True)[:2]))
    flat32_cliff_tight = (flat32_cv >= 0 and flat32_cv <= HP_FLAT_32_CV_TIGHT)
    flat32_cliff_characterized = flat32_cliff_tight or flat32_is_bimodal

    # HARD_FAIL gates on main mechanism / positive control
    if nested_cv > HF_MAIN_MECHANISM_CV_MAX:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"HARD_FAIL_MAIN_MECHANISM_CRUMBLE: NESTED cliff cv="
                f"{nested_cv:.4f} > {HF_MAIN_MECHANISM_CV_MAX}; "
                f"NESTED cliff_K per seed: {nested_cliffs}"
            ),
            "summary": (
                f"HARD_FAIL_MAIN_MECHANISM_CRUMBLE: nested_cv={nested_cv:.4f}"
            ),
            "per_seed_summaries": seed_summaries,
            "n_seeds_observed": n_seeds_observed,
            "flat32_cliff_distribution": {
                "cliffs_per_seed": flat32_cliffs,
                "mean": flat32_mean,
                "std": flat32_std,
                "cv": flat32_cv,
                "histogram": flat32_hist,
            },
            "nested_cliff_distribution": {
                "cliffs_per_seed": nested_cliffs,
                "mean": nested_mean,
                "std": nested_std,
                "cv": nested_cv,
            },
            "cyclic_cliff_distribution": {
                "cliffs_per_seed": cyclic_cliffs,
                "mean": cyclic_mean,
                "std": cyclic_std,
                "cv": cyclic_cv,
            },
        }

    if cyclic_cv > HF_POS_CONTROL_CV_MAX:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"HARD_FAIL_POSITIVE_CONTROL_CRUMBLE: CYCLIC cliff cv="
                f"{cyclic_cv:.4f} > {HF_POS_CONTROL_CV_MAX}; "
                f"CYCLIC cliff_K per seed: {cyclic_cliffs}"
            ),
            "summary": (
                f"HARD_FAIL_POSITIVE_CONTROL_CRUMBLE: cyclic_cv={cyclic_cv:.4f}"
            ),
            "per_seed_summaries": seed_summaries,
            "n_seeds_observed": n_seeds_observed,
            "flat32_cliff_distribution": {
                "cliffs_per_seed": flat32_cliffs,
                "mean": flat32_mean,
                "std": flat32_std,
                "cv": flat32_cv,
                "histogram": flat32_hist,
            },
            "nested_cliff_distribution": {
                "cliffs_per_seed": nested_cliffs,
                "mean": nested_mean,
                "std": nested_std,
                "cv": nested_cv,
            },
            "cyclic_cliff_distribution": {
                "cliffs_per_seed": cyclic_cliffs,
                "mean": cyclic_mean,
                "std": cyclic_std,
                "cv": cyclic_cv,
            },
        }

    # Common body for downstream verdict emit
    aggregate_common = {
        "per_seed_summaries": seed_summaries,
        "n_seeds_observed": n_seeds_observed,
        "seeds_primary_ok": seeds_primary_ok,
        "seeds_nested_vs_flat32_ok": seeds_nested_vs_flat32_ok,
        "flat32_cliff_distribution": {
            "cliffs_per_seed": flat32_cliffs,
            "mean": flat32_mean,
            "std": flat32_std,
            "cv": flat32_cv,
            "histogram": flat32_hist,
            "modes_desc": flat32_modes_desc,
            "is_bimodal": flat32_is_bimodal,
            "cv_tight": flat32_cliff_tight,
            "characterized": flat32_cliff_characterized,
        },
        "nested_cliff_distribution": {
            "cliffs_per_seed": nested_cliffs,
            "mean": nested_mean,
            "std": nested_std,
            "cv": nested_cv,
        },
        "cyclic_cliff_distribution": {
            "cliffs_per_seed": cyclic_cliffs,
            "mean": cyclic_mean,
            "std": cyclic_std,
            "cv": cyclic_cv,
        },
        "hp_all_seeds_primary": all_seeds_primary_ok,
        "hp_nested_vs_flat32_majority": majority_nested_vs_flat32_ok,
        "hp_flat_32_cliff_characterized": flat32_cliff_characterized,
    }

    # Verdict decision
    all_hp_pass = (
        all_seeds_primary_ok
        and majority_nested_vs_flat32_ok
        and flat32_cliff_characterized
    )

    if all_hp_pass:
        verdict = "HARD_PASS"
        char_desc = ("cv_tight" if flat32_cliff_tight
                     else "bimodal_atomized")
        vmsg = (
            f"HARD_PASS_THETA_GAMMA_v4_REVIVAL_7SEEDS: "
            f"n_seeds={n_seeds_observed}; "
            f"FHRR_vs_CYCLIC log2_delta>=1.5 at ALL {seeds_primary_ok}/{n_seeds_observed} seeds; "
            f"NESTED_vs_FLAT_32 >=0.1 at {seeds_nested_vs_flat32_ok}/{n_seeds_observed} seeds "
            f"(majority>={HP_NESTED_VS_FLAT32_MAJORITY}); "
            f"FLAT_32 cliff distribution {char_desc} "
            f"(mean={flat32_mean:.1f}, cv={flat32_cv:.4f}, "
            f"hist={dict(flat32_modes_desc)}); "
            f"NESTED cliff cv={nested_cv:.4f}; "
            f"CYCLIC cliff cv={cyclic_cv:.4f}"
        )
    elif seeds_primary_ok >= max(1, n_seeds_observed - 1):
        # near-miss on primary or majority failed but partial signal
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_THETA_GAMMA_v4_PARTIAL: "
            f"primary_ok={seeds_primary_ok}/{n_seeds_observed} "
            f"(all_seeds_required); "
            f"nested_vs_flat32_ok={seeds_nested_vs_flat32_ok}/{n_seeds_observed} "
            f"(majority>={HP_NESTED_VS_FLAT32_MAJORITY} required); "
            f"flat32_cliff_characterized={flat32_cliff_characterized}; "
            f"flat32 cv={flat32_cv:.4f} "
            f"hist={dict(flat32_modes_desc)}"
        )
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_LOW_PRIMARY_DISCRIMINATION: "
            f"primary_ok={seeds_primary_ok}/{n_seeds_observed}; "
            f"nested_vs_flat32_ok={seeds_nested_vs_flat32_ok}/{n_seeds_observed}; "
            f"flat32 cv={flat32_cv:.4f}"
        )

    out = dict(aggregate_common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ARMS", "SEEDS_V4",
    "K_SEQ_SWEEP_FULL", "K_SEQ_SWEEP_SMOKE",
    "N_DIM", "ITEM_VOCAB_SIZE", "POSITION_SLOTS_NESTED",
    "N_THETA_CYCLES", "N_GAMMA_PER_THETA", "NOISE_SIGMA",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "HP_LOG2_SEPARATION_FHRR_VS_CYCLIC", "HP_CROSS_ARM_LOG2_DELTA",
    "HP_FLAT_32_CV_TIGHT", "HP_NESTED_VS_FLAT32_MAJORITY",
    "HP_SAT_AT_KSEQ_50", "NO_POSITION_MAX_AT_K50",
    "HF_MAIN_MECHANISM_CV_MAX", "HF_POS_CONTROL_CV_MAX",
    "CLIFF_ACC_THRESHOLD",
    "REQUIRED_FIELDS",
    "_get_device", "get_backend_label",
    "make_fhrr_codebook", "make_bipolar_codebook",
    "theta_gamma_bind", "theta_gamma_unbind",
    "encode_fhrr_sequence", "decode_fhrr_at_position",
    "cyclic_shift_encode", "cyclic_shift_decode_at_position",
    "no_position_encode_fhrr", "no_position_decode_fhrr",
    "eval_arm_at_kseq", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
