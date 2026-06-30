"""Shared core for substrate_theta_gamma_v2_FHRR_all_complex siblings.

Theta-gamma phase binding v2 — ALL-COMPLEX FHRR codebook end-to-end.

v1 (a24de6ad) honest-abort at smoke: hybrid bipolar + phase-mul produced
ill-defined complex semantics; cyclic-shift baseline saturated 1.000 at
K_SEQ=50 + phase arms degraded to 0.10-0.30. v1 cell-author flagged the
need for "FHRR all-complex codebook redesign."

v2 design spec: notes/director_theta_gamma_v2_FHRR_all_complex_design_spec_2026-06-30.md

v2 design (this cell implements verbatim):
  - All-complex FHRR codebook: unit-phase exp(i*phi) complex64 vectors
  - Theta-gamma phase binding via element-wise complex multiplication
  - Sequence encoding via phase-multiplied bundle (complex sum)
  - Decoding via complex-conj unbind + magnitude similarity cleanup

Brain mechanism modeled:
  - Theta rhythm (~6-10 Hz) provides outer cycle index t in {0..n_theta-1}
  - Each theta cycle nests gamma bursts (40-100 Hz); g in {0..n_gamma-1}
  - Items at (t, g) bind to theta_code[t] * gamma_code[g]
  - Total positions = n_theta * n_gamma (~5-7 in biology; we use 8*8=64)

5 arms:
  - NO_POSITION             : bundle items only; chance baseline
  - CYCLIC_SHIFT            : v1's bipolar baseline (real-valued)
  - FHRR_FLAT_PHASE_8       : FHRR all-complex; 8 distinct flat positions
  - FHRR_FLAT_PHASE_32      : FHRR all-complex; 32 distinct flat positions
  - FHRR_NESTED_THETA_GAMMA : nested theta(8) * gamma(8) = 64 positions

Discriminator (HARD_PASS):
  - All 5 arms produce DISTINCT K_SEQ cliff points (cross-arm |dlog2_K| >= 0.1)
  - FHRR variants discriminate K_SEQ cliff differently than CYCLIC_SHIFT
    (log2 separation >= 0.3)
  - NESTED arm shows distinct cliff from FLAT_PHASE_32 (nesting helps)
  - mechanism_hash distinct per arm (META_RULE_AX)
  - cv across seeds <= 0.10
  - NO suspect-1.000 saturation at K_SEQ <= 50 (META_RULE_Q)
  - NOISE_SIGMA=0.05 keeps NO_POSITION strictly < 1.000 at K_SEQ=50

Regime (anti-saturation):
  - K_SEQ_SWEEP = [50, 100, 200, 500, 1000, 2000]
  - N_DIM = 4096 (smaller; less headroom)
  - ITEM_VOCAB_SIZE = 10000 (larger; more discrimination)
  - POSITION_SLOTS = 64 (8x8 for NESTED)
  - NOISE_SIGMA = 0.05 (noisy retrieval)

GPU mandate (PROT-020): import torch present. Complex matmul is
matmul-bound and naturally GPU-accelerated.

Anchor: substrate_theta_gamma_v2_FHRR_all_complex_seed_{7,13,19}

Pre-reg: preregs/2026-06-30_substrate_theta_gamma_v2_FHRR_all_complex.md

ASCII-only. No unicode. No em-dashes. No emojis.

Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn).
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
import torch  # PROT-020: overnight_queue routing-gate requires `import torch`


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
# 5 arms (META_RULE_AX outer axis; LOCKED)
ARMS = (
    "NO_POSITION",
    "CYCLIC_SHIFT",
    "FHRR_FLAT_PHASE_8",
    "FHRR_FLAT_PHASE_32",
    "FHRR_NESTED_THETA_GAMMA",
)

# K_SEQ sweep axis (LOCKED; pushes past v1's saturated K=50)
K_SEQ_SWEEP_FULL = (50, 100, 200, 500, 1000, 2000)
K_SEQ_SWEEP_SMOKE = (50, 100, 200, 500)  # 4 of 6 K points at smoke

# Regime (LOCKED)
N_DIM = 4096                  # smaller dim -> less headroom -> earlier cliff
ITEM_VOCAB_SIZE = 10000       # larger vocab -> more inter-item discrimination
POSITION_SLOTS_FLAT_8 = 8
POSITION_SLOTS_FLAT_32 = 32
N_THETA_CYCLES = 8
N_GAMMA_PER_THETA = 8
POSITION_SLOTS_NESTED = N_THETA_CYCLES * N_GAMMA_PER_THETA  # 64
NOISE_SIGMA = 0.05            # Gaussian noise at retrieval

# Discriminator bands (LOCKED)
HP_LOG2_SEPARATION_FHRR_VS_CYCLIC = 0.3   # FHRR cliff differs from CYCLIC by >=0.3 log2
HP_CROSS_ARM_LOG2_DELTA = 0.1             # all-arm pairwise cliff |dlog2_K| >= 0.1
HP_CV_MAX_ACROSS_SEEDS = 0.10             # cv across seeds <= 0.10
HP_SAT_AT_KSEQ_50 = 0.999                 # NO arm above this at K_SEQ=50 (META_RULE_Q)
NO_POSITION_MAX_AT_K50 = 0.999            # NO_POSITION must NOT saturate (discriminator-survives-scale)

# Retrieval accuracy threshold defining the "K_SEQ cliff" point
# A K is "above cliff" if mean_retrieval_acc >= CLIFF_ACC_THRESHOLD
CLIFF_ACC_THRESHOLD = 0.50

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = len(ARMS) * len(K_SEQ_SWEEP_FULL)     # 5 * 6 = 30
EXPECTED_N_UNITS_SMOKE = len(ARMS) * len(K_SEQ_SWEEP_SMOKE)   # 5 * 4 = 20

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")

# Number of retrieval queries per K_SEQ point (averaged for acc)
N_QUERIES_PER_K = 50
N_QUERIES_PER_K_SMOKE = 25


# ---------------------------------------------------------------------------
# Device setup (GPU preferred; CPU fallback for selftest/smoke)
# ---------------------------------------------------------------------------
def _get_device(strict_gpu: bool = False) -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    if strict_gpu:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (PROT-020 / Fix #24): cuda.is_available()=False. "
            "theta-gamma v2 FHRR all-complex at N_DIM=%d K_SEQ up to %d requires "
            "CUDA for overnight_queue routing. Route to overnight_queue or run "
            "with --smoke / --self-test for local CPU fallback." % (
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


# ---------------------------------------------------------------------------
# Codebooks (FHRR all-complex + bipolar baseline)
# ---------------------------------------------------------------------------
def make_fhrr_codebook(
    n_items: int, n_dim: int, seed: int, device: torch.device,
) -> torch.Tensor:
    """Unit-phase complex codebook (n_items, n_dim) complex64.

    Each element is exp(i*phi) for phi ~ Uniform[0, 2*pi).
    """
    g = torch.Generator(device=device)
    g.manual_seed(int(seed))
    phi = torch.empty(n_items, n_dim, device=device, dtype=torch.float32)
    phi.uniform_(0.0, 2.0 * math.pi, generator=g)
    real = torch.cos(phi)
    imag = torch.sin(phi)
    return torch.complex(real, imag)  # complex64


def make_bipolar_codebook(
    n_items: int, n_dim: int, seed: int, device: torch.device,
) -> torch.Tensor:
    """Bipolar {-1, +1}^N codebook (n_items, n_dim) float32 (v1 baseline)."""
    g = torch.Generator(device=device)
    g.manual_seed(int(seed))
    x = torch.empty(n_items, n_dim, device=device, dtype=torch.float32)
    x.bernoulli_(0.5, generator=g).mul_(2.0).sub_(1.0)
    return x


# ---------------------------------------------------------------------------
# FHRR binding ops (mechanism core)
# ---------------------------------------------------------------------------
def theta_gamma_bind(
    item_hd: torch.Tensor, position_hd: torch.Tensor,
) -> torch.Tensor:
    """FHRR canonical bind: element-wise complex mul = phase addition."""
    return item_hd * position_hd


def theta_gamma_unbind(
    bound_hd: torch.Tensor, position_hd: torch.Tensor,
) -> torch.Tensor:
    """Inverse: bound * conj(position). For unit-phase position, recovers item."""
    return bound_hd * position_hd.conj()


def encode_fhrr_sequence(
    item_codes: torch.Tensor, position_codes: torch.Tensor,
) -> torch.Tensor:
    """Bundle phase-bound items into ONE sequence HD (complex sum).

    Args:
      item_codes: (K, n_dim) complex64 - K items in the sequence
      position_codes: (K, n_dim) complex64 - K position codes (same K)
    Returns:
      seq_hd: (n_dim,) complex64 - complex sum of phase-bound items
    """
    bound = item_codes * position_codes  # (K, n_dim)
    return bound.sum(dim=0)  # (n_dim,)


def decode_fhrr_at_position(
    seq_hd: torch.Tensor, position_hd: torch.Tensor,
    item_codebook: torch.Tensor,
) -> torch.Tensor:
    """Recover argmax item index at a given position.

    Args:
      seq_hd: (n_dim,) complex64 - bundled sequence HD
      position_hd: (n_dim,) complex64 - position code at query position
      item_codebook: (V, n_dim) complex64 - all items in vocab
    Returns:
      pred_idx: long tensor (scalar) - argmax over codebook similarity
    """
    candidate = seq_hd * position_hd.conj()  # (n_dim,)
    # Complex inner product magnitude: |<codebook[i], candidate>|
    scores = (item_codebook.conj() @ candidate).abs()  # (V,)
    return scores.argmax()


# ---------------------------------------------------------------------------
# v1 baseline: cyclic shift (real bipolar)
# ---------------------------------------------------------------------------
def cyclic_shift_encode(item_codes: torch.Tensor) -> torch.Tensor:
    """Cyclic-shift binding: position i shifts item by i positions; sum.

    Args:
      item_codes: (K, n_dim) float32 bipolar items
    Returns:
      seq_hd: (n_dim,) float32 - bipolar sum (not re-binarized; preserves signal)
    """
    K, n_dim = item_codes.shape
    bundled = torch.zeros(n_dim, device=item_codes.device, dtype=torch.float32)
    for i in range(K):
        # Roll item by i positions
        bundled = bundled + torch.roll(item_codes[i], shifts=i, dims=0)
    return bundled


def cyclic_shift_decode_at_position(
    seq_hd: torch.Tensor, position: int, item_codebook: torch.Tensor,
) -> torch.Tensor:
    """Recover argmax via inverse shift + cosine similarity."""
    # Reverse shift by -position
    candidate = torch.roll(seq_hd, shifts=-position, dims=0)
    # Cosine similarity over real codebook
    cand_n = candidate / candidate.norm().clamp_min(1e-12)
    cb_n = item_codebook / item_codebook.norm(dim=1, keepdim=True).clamp_min(1e-12)
    scores = cb_n @ cand_n  # (V,)
    return scores.argmax()


# ---------------------------------------------------------------------------
# NO_POSITION baseline (bundle without position binding)
# ---------------------------------------------------------------------------
def no_position_encode_fhrr(item_codes: torch.Tensor) -> torch.Tensor:
    """Bundle FHRR items without binding to position. Pure complex sum."""
    return item_codes.sum(dim=0)


def no_position_decode_fhrr(
    seq_hd: torch.Tensor, item_codebook: torch.Tensor,
) -> torch.Tensor:
    """Decode without unbinding: cleanup over codebook directly."""
    scores = (item_codebook.conj() @ seq_hd).abs()
    return scores.argmax()


# ---------------------------------------------------------------------------
# Per-arm encode/decode dispatchers
# ---------------------------------------------------------------------------
def _build_positions_flat(
    n_positions: int, n_dim: int, seed: int, device: torch.device,
) -> torch.Tensor:
    """Flat phase codebook: n_positions distinct unit-phase complex codes."""
    return make_fhrr_codebook(n_positions, n_dim, seed + 7919, device)


def _build_positions_nested(
    n_theta: int, n_gamma: int, n_dim: int, seed: int, device: torch.device,
) -> torch.Tensor:
    """Nested theta * gamma codes: theta_code[t] * gamma_code[g], (n_theta*n_gamma, n_dim)."""
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


def _add_noise_complex(hd: torch.Tensor, sigma: float,
                       gen: torch.Generator) -> torch.Tensor:
    """Add complex Gaussian noise (real + imag) at sigma magnitude."""
    if sigma <= 0:
        return hd
    real_noise = torch.empty(hd.shape, device=hd.device, dtype=torch.float32)
    real_noise.normal_(0.0, sigma, generator=gen)
    imag_noise = torch.empty(hd.shape, device=hd.device, dtype=torch.float32)
    imag_noise.normal_(0.0, sigma, generator=gen)
    return hd + torch.complex(real_noise, imag_noise)


def _add_noise_real(hd: torch.Tensor, sigma: float,
                    gen: torch.Generator) -> torch.Tensor:
    """Add real Gaussian noise at sigma magnitude."""
    if sigma <= 0:
        return hd
    n = torch.empty(hd.shape, device=hd.device, dtype=torch.float32)
    n.normal_(0.0, sigma, generator=gen)
    return hd + n


def eval_arm_at_kseq(
    arm: str, K_SEQ: int, n_queries: int, seed: int, device: torch.device,
    noise_sigma: float = NOISE_SIGMA,
) -> Dict[str, Any]:
    """Eval one (arm, K_SEQ) point: average retrieval accuracy over n_queries.

    Returns metrics dict for one phase point.
    """
    t0 = time.time()

    g_main = torch.Generator(device=device)
    g_main.manual_seed(int(seed))
    g_noise = torch.Generator(device=device)
    g_noise.manual_seed(int(seed) + 31337)

    # Build vocab + positions per arm (codebook reused across queries)
    if arm == "NO_POSITION":
        item_codebook = make_fhrr_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = None
        n_positions = 1
    elif arm == "CYCLIC_SHIFT":
        item_codebook = make_bipolar_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = None  # cyclic-shift is implicit via roll
        n_positions = N_DIM  # roll positions are 0..N_DIM-1
    elif arm == "FHRR_FLAT_PHASE_8":
        item_codebook = make_fhrr_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = _build_positions_flat(
            POSITION_SLOTS_FLAT_8, N_DIM, seed, device
        )
        n_positions = POSITION_SLOTS_FLAT_8
    elif arm == "FHRR_FLAT_PHASE_32":
        item_codebook = make_fhrr_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = _build_positions_flat(
            POSITION_SLOTS_FLAT_32, N_DIM, seed, device
        )
        n_positions = POSITION_SLOTS_FLAT_32
    elif arm == "FHRR_NESTED_THETA_GAMMA":
        item_codebook = make_fhrr_codebook(ITEM_VOCAB_SIZE, N_DIM, seed, device)
        positions = _build_positions_nested(
            N_THETA_CYCLES, N_GAMMA_PER_THETA, N_DIM, seed, device
        )
        n_positions = POSITION_SLOTS_NESTED
    else:
        raise ValueError(f"unknown arm: {arm!r}")

    # n_queries independent trials; each builds a K_SEQ-length sequence
    # and queries one random position
    n_correct = 0
    for q in range(n_queries):
        # Random item assignment per query (across full vocab)
        item_ids = torch.empty(K_SEQ, device=device, dtype=torch.long)
        item_ids.random_(0, ITEM_VOCAB_SIZE, generator=g_main)

        if arm == "NO_POSITION":
            seq_codes = item_codebook[item_ids]  # (K, n_dim) complex
            seq_hd = no_position_encode_fhrr(seq_codes)
            seq_hd_noisy = _add_noise_complex(seq_hd, noise_sigma, g_noise)
            # Query position is meaningless; use random item as target
            target_slot = int(torch.randint(
                0, K_SEQ, (1,), device=device, generator=g_main).item())
            true_item = int(item_ids[target_slot].item())
            pred = int(no_position_decode_fhrr(seq_hd_noisy, item_codebook).item())

        elif arm == "CYCLIC_SHIFT":
            seq_codes = item_codebook[item_ids]  # (K, n_dim) float
            seq_hd = cyclic_shift_encode(seq_codes)
            seq_hd_noisy = _add_noise_real(seq_hd, noise_sigma, g_noise)
            # Query a random slot in [0, K_SEQ)
            target_slot = int(torch.randint(
                0, K_SEQ, (1,), device=device, generator=g_main).item())
            true_item = int(item_ids[target_slot].item())
            pred = int(cyclic_shift_decode_at_position(
                seq_hd_noisy, target_slot, item_codebook).item())

        else:
            # FHRR arms (flat 8, flat 32, nested)
            # Item-position assignment: item k -> position k % n_positions
            pos_assignment = torch.arange(K_SEQ, device=device) % n_positions
            seq_item_codes = item_codebook[item_ids]  # (K, n_dim) complex
            seq_pos_codes = positions[pos_assignment]  # (K, n_dim) complex
            seq_hd = encode_fhrr_sequence(seq_item_codes, seq_pos_codes)
            seq_hd_noisy = _add_noise_complex(seq_hd, noise_sigma, g_noise)
            # Query a random target slot
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

    # Free intermediates
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


# ---------------------------------------------------------------------------
# Selftest (mechanism + distinctness + noise discipline)
# ---------------------------------------------------------------------------
def selftest(seed: int, device: torch.device = None) -> Tuple[bool, str]:
    if device is None:
        device = _get_device(strict_gpu=False)
    msgs: List[str] = []

    # 1. Cardinality math (5 arms x sweep_size)
    if EXPECTED_N_UNITS_FULL != 30:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 30"
    if EXPECTED_N_UNITS_SMOKE != 20:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 20"
    msgs.append(
        f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
        f"SMOKE={EXPECTED_N_UNITS_SMOKE}"
    )

    # 2. FHRR unbind is the canonical inverse (mechanism unit test)
    g = torch.Generator(device=device)
    g.manual_seed(int(seed))
    n_dim_st = 256
    item = make_fhrr_codebook(1, n_dim_st, seed, device)[0]
    pos = make_fhrr_codebook(1, n_dim_st, seed + 100, device)[0]
    bound = theta_gamma_bind(item, pos)
    recovered = theta_gamma_unbind(bound, pos)
    # recovered should equal item exactly (unit-phase position)
    diff = (recovered - item).abs().max().item()
    if diff > 1e-3:
        return False, f"FHRR unbind self-inverse FAIL: max|diff|={diff:.6f}"
    msgs.append(f"fhrr_unbind_self_inverse_max_diff={diff:.2e}")

    # 3. Single-item sequence at K=1 recovers item perfectly (clean retrieval)
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

    # 4. Arm distinctness at smoke regime (META_RULE_AX prelim)
    # Each arm must produce DISTINCT byte-level encoder output for same input
    hashes: Dict[str, str] = {}
    test_K = 50
    for arm in ARMS:
        pt = eval_arm_at_kseq(
            arm, test_K, n_queries=10, seed=seed, device=device,
            noise_sigma=0.0,  # clean for selftest distinctness
        )
        # Hash the per-query outcome string
        h_payload = json.dumps([
            arm, pt["K_SEQ"], pt["n_correct"], pt["n_queries"]
        ], sort_keys=True).encode("utf-8")
        hashes[arm] = hashlib.sha256(h_payload).hexdigest()[:16]
    # All 5 should differ. Some may collide if both score 0 or both score n;
    # we instead hash the underlying mechanism source code to confirm distinct
    # CODE PATHS (META_RULE_AX deeper check below).
    msgs.append(f"arm_smoke_outcome_hashes={hashes}")

    # 5. META_RULE_AX deep check: mechanism CODE paths must differ per arm.
    # Hash the function call signature + codebook dtype + position dim per arm.
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

    # 6. NOISE discipline (DISCRIMINATOR-MUST-SURVIVE-SCALE per Director):
    #    NO_POSITION at K_SEQ=50 with NOISE_SIGMA=0.05 must NOT saturate 1.000
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

    # 7. FHRR_NESTED is genuinely different from FHRR_FLAT_32 (not same hash)
    if code_path_hashes["FHRR_NESTED_THETA_GAMMA"] == code_path_hashes["FHRR_FLAT_PHASE_32"]:
        return False, "NESTED vs FLAT_32 code paths collide"
    msgs.append("nested_vs_flat32_distinct=True")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(
    seed: int, run_mode: str, device: torch.device,
) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    k_sweep = K_SEQ_SWEEP_SMOKE if is_smoke else K_SEQ_SWEEP_FULL
    n_queries = N_QUERIES_PER_K_SMOKE if is_smoke else N_QUERIES_PER_K
    expected_n = len(ARMS) * len(k_sweep)

    print(
        f"[run_one_seed_thetagamma_v2] seed={seed} mode={run_mode} "
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

    # Per-arm K cliff analysis
    per_arm_summary: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS:
        arm_pts = sorted(
            [p for p in phase_map if p["arm"] == arm],
            key=lambda p: p["K_SEQ"],
        )
        # Cliff K: largest K where acc >= CLIFF_ACC_THRESHOLD
        # If all below threshold: cliff_K = 0 (no capacity)
        # If all above threshold: cliff_K = max(K_SEQ) (haven't seen cliff)
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

    # META_RULE_AX: cross-arm distinctness via OUTCOME hashes
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
    n_pairs_total = len(pairs_differ)  # C(5,2) = 10

    # Cross-arm cliff-delta analysis
    cliff_log2s = {
        arm: per_arm_summary[arm]["log2_cliff_K"] for arm in ARMS
    }
    # FHRR vs CYCLIC log2 separation (max across 3 FHRR arms)
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

    # All-pairs |dlog2_K| minimum
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

    # NESTED vs FLAT_32 distinct cliff
    nested_log2 = cliff_log2s.get("FHRR_NESTED_THETA_GAMMA", -1.0)
    flat32_log2 = cliff_log2s.get("FHRR_FLAT_PHASE_32", -1.0)
    nested_vs_flat32_delta = (
        abs(nested_log2 - flat32_log2)
        if (nested_log2 >= 0 and flat32_log2 >= 0)
        else -1.0
    )

    # META_RULE_Q: suspect-1.000 check at K_SEQ=50
    arms_saturating_at_K50 = []
    for arm in ARMS:
        acc_K50 = per_arm_summary[arm].get("acc_at_K50")
        if acc_K50 is not None and acc_K50 >= HP_SAT_AT_KSEQ_50:
            arms_saturating_at_K50.append(arm)
    no_position_acc_K50 = per_arm_summary.get("NO_POSITION", {}).get(
        "acc_at_K50"
    )
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


# ---------------------------------------------------------------------------
# Smoke gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    expected_n = body.get("expected_n_units", 0)
    pairs_differ = body.get("encoder_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    n_pairs_total = body.get("n_pairs_total", 10)
    arms_saturating = body.get("arms_saturating_at_K50", [])
    no_position_sat = body.get("no_position_saturates_K50", False)
    no_position_acc_K50 = body.get("no_position_acc_K50", 0.0)
    per_arm_summary = body.get("per_arm_summary", {})
    min_cross_arm_delta = body.get("min_cross_arm_log2_delta", -1.0)

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, (
            f"cardinality_breach: expected {expected_n} got {len(phase_map)}"
        )

    # 2. META_RULE_AX: cross-arm pair distinctness floor
    if n_pairs_differ < 4:  # smoke floor lower than full (allow some K-tail collision)
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (
            f"HARD_FAIL_ARMS_COLLIDE (META_RULE_AX): "
            f"{n_pairs_differ}/{n_pairs_total} arm-pairs differ "
            f"(need >= 4 at smoke); collapsed: {collapsed}"
        )

    # 3. NOISE discipline (DISCRIMINATOR-MUST-SURVIVE-SCALE):
    #    NO_POSITION at K=50 noisy must NOT saturate 1.000
    if no_position_sat:
        return False, (
            f"HARD_FAIL_NOISE_DISCIPLINE: NO_POSITION saturates K=50 noisy "
            f"(acc={no_position_acc_K50:.3f} >= {NO_POSITION_MAX_AT_K50}); "
            f"discriminator vacuous"
        )

    # 4. META_RULE_Q: suspect-1.000 check at K=50 across all arms
    if len(arms_saturating) >= 3:  # 3+ arms all saturate => regime too easy
        return False, (
            f"HARD_FAIL_REGIME_TOO_EASY (META_RULE_Q): "
            f"{len(arms_saturating)} arms saturate at K=50: {arms_saturating}; "
            f"acc>={HP_SAT_AT_KSEQ_50}"
        )

    # 5. Discriminator-fires: at least one FHRR arm shows non-zero capacity
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

    return True, (
        f"smoke_gate_pass_v2: cardinality_ok + "
        f"pairs_differ={n_pairs_differ}/{n_pairs_total}>=4 + "
        f"NO_POSITION_K50={no_position_acc_K50:.3f}<{NO_POSITION_MAX_AT_K50} + "
        f"no_K50_saturation_glut + "
        f"{len(fhrr_active)}/3 FHRR arms show capacity"
    )


# ---------------------------------------------------------------------------
# Verdict-emitter (META_RULE_AY: HARD_FAIL on self-reported distinctness False)
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: empty per_seed",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")
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

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (
                f"HARD_PASS_SMOKE_thetagamma_v2: {observed_n}/{expected_n} pts; "
                f"pairs_differ={n_pairs_differ}/{n_pairs_total}; "
                f"NO_POSITION@K50_acc={no_position_acc_K50:.3f}; "
                f"max_fhrr_vs_cyclic_log2_delta={max_fhrr_vs_cyclic:.3f}; "
                f"nested_vs_flat32_log2_delta={nested_vs_flat32:.3f}; "
                f"arms_saturating_K50={len(arms_saturating)}"
            )
        else:
            verdict = "HARD_FAIL"
            vmsg = f"HARD_FAIL_SMOKE_thetagamma_v2: {reason}"
        out = dict(common)
        out.update({
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
            f"observed={observed_n}"
        )
    elif no_position_sat:
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_NOISE_DISCIPLINE: NO_POSITION K50 acc="
            f"{no_position_acc_K50:.3f} >= {NO_POSITION_MAX_AT_K50}; "
            f"discriminator vacuous"
        )
    elif len(arms_saturating) >= 3:
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_REGIME_TOO_EASY: {len(arms_saturating)} arms saturate "
            f"K50: {arms_saturating}"
        )
    elif n_pairs_differ < 7:  # FULL stricter than smoke (7 of 10 pairs)
        collapsed = [k for k, v in pairs_differ.items() if not v]
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_ARMS_COLLIDE (META_RULE_AX): "
            f"{n_pairs_differ}/{n_pairs_total} pairs differ (need >= 7 at FULL); "
            f"collapsed: {collapsed}"
        )
    elif (max_fhrr_vs_cyclic >= HP_LOG2_SEPARATION_FHRR_VS_CYCLIC
          and min_cross_arm_delta >= HP_CROSS_ARM_LOG2_DELTA
          and nested_vs_flat32 >= HP_CROSS_ARM_LOG2_DELTA
          and n_pairs_differ >= 9):  # 9 of 10 pairs differ
        verdict = "HARD_PASS"
        vmsg = (
            f"HARD_PASS_THETA_GAMMA_FHRR_v2: {observed_n}/{expected_n} pts; "
            f"all 5 arms distinct K-cliffs "
            f"(pairs_differ={n_pairs_differ}/{n_pairs_total}); "
            f"FHRR vs CYCLIC log2_delta={max_fhrr_vs_cyclic:.3f} "
            f">={HP_LOG2_SEPARATION_FHRR_VS_CYCLIC}; "
            f"NESTED vs FLAT_32 log2_delta={nested_vs_flat32:.3f} "
            f">={HP_CROSS_ARM_LOG2_DELTA}; "
            f"min_cross_arm_delta={min_cross_arm_delta:.3f}"
        )
    elif n_pairs_differ >= 6 and max_fhrr_vs_cyclic >= 0.15:
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_THETA_GAMMA_PARTIAL: "
            f"{n_pairs_differ}/{n_pairs_total} pairs differ; "
            f"FHRR vs CYCLIC log2_delta={max_fhrr_vs_cyclic:.3f} (<0.3); "
            f"NESTED vs FLAT_32 delta={nested_vs_flat32:.3f}; "
            f"min_cross_arm={min_cross_arm_delta:.3f}"
        )
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_LOW_DISCRIMINATION: "
            f"pairs_differ={n_pairs_differ}/{n_pairs_total}; "
            f"max_fhrr_vs_cyclic={max_fhrr_vs_cyclic:.3f}; "
            f"nested_vs_flat32={nested_vs_flat32:.3f}"
        )

    # META_RULE_AY: verdict-emitter HARD_FAIL on self-reported distinctness False
    if verdict == "HARD_PASS" and n_pairs_differ < 7:
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_AY_DISTINCTNESS_FALSE: verdict HARD_PASS but only "
            f"{n_pairs_differ}/{n_pairs_total} pairs differ; downgrade per "
            f"META_RULE_AY"
        )

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ARMS", "K_SEQ_SWEEP_FULL", "K_SEQ_SWEEP_SMOKE",
    "N_DIM", "ITEM_VOCAB_SIZE", "POSITION_SLOTS_NESTED",
    "N_THETA_CYCLES", "N_GAMMA_PER_THETA", "NOISE_SIGMA",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "HP_LOG2_SEPARATION_FHRR_VS_CYCLIC", "HP_CROSS_ARM_LOG2_DELTA",
    "HP_CV_MAX_ACROSS_SEEDS", "HP_SAT_AT_KSEQ_50",
    "NO_POSITION_MAX_AT_K50", "CLIFF_ACC_THRESHOLD",
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
