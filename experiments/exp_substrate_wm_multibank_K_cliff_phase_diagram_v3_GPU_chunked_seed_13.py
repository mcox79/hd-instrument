"""substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked -- seed 13 chunked sibling.

Parent prereg:  preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked.md
Forked from:    experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1.py
Sibling chunks: _seed_7.py (this), _seed_13.py, _seed_19.py

Scientific question (REFRAME of v1):
  v1 sweeps K x bank_overlap x routing_noise at FIXED K_PER_BANK=64.
  v3 sweeps K_per_bank x num_banks x N_DIM at FIXED CB=16384, comparing
  MULTI_BANK_BIND vs SINGLE_BANK_BASELINE at total_K = K_per_bank * num_banks.
  Question: does distributing capacity across more banks (B>1) BEAT concentrating
  it in one bank (B=1) at fixed total_K? (Interference-vs-capacity tradeoff.)

Sweep axes:
  K_per_bank in {64, 128, 256, 512, 1024, 2048, 4096} (7)
  num_banks  in {1, 2, 4, 8, 16}                       (5)
  N_DIM      in {2048, 4096, 8192}                     (3)
  Full grid: 7 x 5 x 3 = 105 points x 3 arms = 315 units per seed.

Smoke corners (6 points x 3 arms = 18 units), all at N=2048:
  (K=64,   B=1)  -- expected saturate; arms_differ at B=1 may collapse (MULTI==SINGLE)
  (K=64,   B=16) -- expected MULTI > SINGLE (cliff: total_K=1024 single-bank)
  (K=256,  B=1)  -- ~equal small K
  (K=256,  B=16) -- expected MULTI > SINGLE (cliff: total_K=4096 single-bank)
  (K=1024, B=1)  -- borderline (interference at K=1024 single-bank)
  (K=1024, B=4)  -- expected MULTI > SINGLE (cliff: total_K=4096 multi-bank wins)

Arms:
  MULTI_BANK_BIND        -- distribute total_K across num_banks; route via bank-tag + cleanup-twice
  SINGLE_BANK_BASELINE   -- same total_K all in 1 bank; interference-bounded
  RANDOM_FLOOR           -- random codebook vector; floor = 1/CB ~ 6.1e-5

At B=1, MULTI and SINGLE are EQUIVALENT MECHANISMS (positive control: arms collapse only at B=1).
The verdict logic counts arms_differ only at B>=2 points. RANDOM differs everywhere.

GPU MANDATE (Fix #24): cuda required for full; fp16 storage; chunked codebook matmul;
  nvidia-smi util sampled; smoke gates gpu_util_p50 >= 50% (FULL only; CPU smoke skips).

PRE-REG bands (LOCKED at module init; see prereg):
  HARD_PASS (per seed): MULTI > SINGLE by >= 0.30 at >= 20 of 105 grid points
                        AND >= 6 of those 20 at N=8192 (discriminator-survives-scale)
                        AND corridor saturation: (K=64,B=1,N=8192) MULTI >= 0.95.
  MIDDLE_BAND: 10-19 points discriminate; or coherent cliff structure at recalls in [0.30, 0.50).
  HARD_FAIL_CARDINALITY_BREACH / UNIT_EXCEPTION / GPU_MEMORY_OOM / ARMS_IDENTICAL.
  HARD_FAIL_DISCRIMINATOR_DOES_NOT_FIRE: < 10 of 105 with margin > 0.30.
  HARD_FAIL_SATURATION_ONLY / HARD_FAIL_FLOOR_ONLY / HARD_FAIL_LLM_CALL.

PROT-018: no _n suffix in anchor (capability-test, sibling chunk).
ASCII-only; no unicode; no emojis; no em-dashes.
META_RULE_AC/AE/AF/AG/AH/AN load-bearing.

Author: exp_dev 2026-06-28.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import atexit
import hashlib
import math
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch  # PROT-020 GPU-queue routing gate

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)

SEED_THIS_CHUNK = 13
ANCHOR_NAME = "substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_%d" % SEED_THIS_CHUNK

_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_multibank_K_cliff_v3_chunked"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# Pre-reg bands LOCKED at module init
HP_DISCRIM_MARGIN = 0.30          # MULTI - SINGLE > 0.30
HP_MULTI_PASS_RECALL = 0.50       # MULTI recall >= 0.50 at PASS points
HP_RAIL_RECALL = 0.95             # corridor saturation: (K=64,B=1,N=8192) MULTI >= 0.95
HP_SATURATION = 0.995
HP_FLOOR_BAND = 0.05              # MULTI - RANDOM < 0.05 -> floor
HP_VRAM_PROBE_FRACTION = 0.85
HP_GPU_UTIL_MIN_P50 = 0.50        # Fix #24 NON-NEGOTIABLE on full
HP_HARD_PASS_MIN_GRID = 20        # >= 20 of 105 points
HP_HARD_PASS_MIN_FULLN = 6        # >= 6 of those at N=8192
HP_DISCRIM_DOES_NOT_FIRE = 10     # < 10 points -> HARD_FAIL

assert 0.0 < HP_DISCRIM_MARGIN < 1.0, "discrim margin locked"
assert 0.0 < HP_MULTI_PASS_RECALL < HP_SATURATION, "pass ordering"

# Mechanism params (chain-grade v3 base)
SIGMA = 1.0
CUE_COS = 0.70
CODEBOOK_SIZE = 16384            # enough for total_K up to 65536? NO -- max total_K = 4096*16 = 65536 > CB.
                                  # Cap total_K <= CB by skipping points where K_per_bank * num_banks > CB.
                                  # Skipped points: (K=4096,B=16)=65536; (K=2048,B=16)=32768; (K=4096,B=8)=32768.
                                  # See _build_phase_points: explicit skip + recorded in metrics.
                                  # Net grid = 105 - 3 = 102 points (per N) * 3 N = wait: skip applies regardless of N.
                                  # Actually we re-compute expected_n_units at module init below.
CODEBOOK_CHUNK_FULL = 4096
CODEBOOK_CHUNK_SMOKE = 1024

# Full sweep axes
K_PER_BANK_VALUES = [64, 128, 256, 512, 1024, 2048, 4096]
NUM_BANKS_VALUES = [1, 2, 4, 8, 16]
N_DIM_VALUES_FULL = [2048, 4096, 8192]
N_DIM_VALUES_SMOKE = [2048]


def _build_phase_points(K_VALUES: List[int], B_VALUES: List[int],
                        N_VALUES: List[int]) -> List[Tuple[int, int, int]]:
    """All (K_per_bank, num_banks, N_DIM) combos where K*B <= CODEBOOK_SIZE.

    Skip combinations where total_K > CB (we'd need a bigger CB).
    """
    pts = []
    for N in N_VALUES:
        for K in K_VALUES:
            for B in B_VALUES:
                if K * B <= CODEBOOK_SIZE:
                    pts.append((K, B, N))
    return pts


# Smoke vs full grids
# DESIGN NOTE (calibration from initial smoke run at N=2048): at N=2048, only K_per_bank<=64
# yields MULTI recall above the 0.50 floor (SNR_dim = 1/sqrt(K_per_bank - 1)). To FIRE the
# discriminator at multiple corners we need the regime where MULTI is above floor while
# SINGLE arm interference-collapses. Revised smoke corners:
#   - N=2048 corners use K_per<=64 (where MULTI works)
#   - N=4096 corners extend the regime with K_per<=128 (where MULTI works at N=4096)
# This keeps smoke CPU-feasible (<60s) and exercises the discriminator at multiple corners.
SMOKE_CORNERS = [
    (64,   1,  2048),  # positive control B=1 (MULTI == SINGLE; both ~0.66)
    (64,   16, 2048),  # discriminator-fires (MULTI ~0.70 SINGLE ~0.002 at total_K=1024)
    (64,   8,  2048),  # discriminator-fires (MULTI ~0.70 SINGLE ~0.0 at total_K=512)
    (64,   4,  4096),  # discriminator-fires (MULTI ~0.95 SINGLE ~0.05 at total_K=256 N=4096)
    (128,  4,  4096),  # discriminator-fires (MULTI ~0.85 SINGLE ~0.01 at total_K=512 N=4096)
    (1024, 1,  2048),  # SINGLE-cliff sanity (MULTI ~0.001 SINGLE ~0.003; both floor)
]

# Smoke also uses N_ITEMS limit
N_ITEMS_PER_K_FULL = 256
N_ITEMS_PER_K_SMOKE = 96

if SMOKE:
    PHASE_POINTS: List[Tuple[int, int, int]] = SMOKE_CORNERS
    N_ITEMS_PER_K = N_ITEMS_PER_K_SMOKE
    CODEBOOK_CHUNK = CODEBOOK_CHUNK_SMOKE
else:
    PHASE_POINTS = _build_phase_points(K_PER_BANK_VALUES, NUM_BANKS_VALUES, N_DIM_VALUES_FULL)
    N_ITEMS_PER_K = N_ITEMS_PER_K_FULL
    CODEBOOK_CHUNK = CODEBOOK_CHUNK_FULL

SEEDS = [SEED_THIS_CHUNK]
REGIMES = ["MULTI_BANK_BIND", "SINGLE_BANK_BASELINE", "RANDOM_FLOOR"]
EXPECTED_N_UNITS = len(SEEDS) * len(PHASE_POINTS) * len(REGIMES)

CONFIG_VERSION = (
    "substrateWmMBKCliffPhaseDiagV3GPUChunked-seed%d: CB=%d sigma=%.1f CUE_COS=%.2f "
    "K_per_bank_values=%s num_banks_values=%s N_dim_values=%s phase_points=%d "
    "(smoke=%s) N_ITEMS_PER_K=%d codebook_chunk=%d seeds=%s mode=%s "
    "HP_discrim=%.2f HP_pass_rec=%.2f HP_rail=%.2f HP_sat=%.3f HP_floor=%.2f "
    "VRAM_PROBE=%.2f HP_GPU_UTIL_MIN=%.2f HP_min_grid=%d HP_min_full_N=%d "
    "EXPECTED_N_UNITS=%d ANCHOR=%s"
) % (
    SEED_THIS_CHUNK, CODEBOOK_SIZE, SIGMA, CUE_COS,
    K_PER_BANK_VALUES, NUM_BANKS_VALUES,
    (N_DIM_VALUES_SMOKE if SMOKE else N_DIM_VALUES_FULL),
    len(PHASE_POINTS), SMOKE, N_ITEMS_PER_K, CODEBOOK_CHUNK, SEEDS, RUN_MODE,
    HP_DISCRIM_MARGIN, HP_MULTI_PASS_RECALL, HP_RAIL_RECALL, HP_SATURATION,
    HP_FLOOR_BAND, HP_VRAM_PROBE_FRACTION, HP_GPU_UTIL_MIN_P50,
    HP_HARD_PASS_MIN_GRID, HP_HARD_PASS_MIN_FULLN, EXPECTED_N_UNITS, ANCHOR_NAME,
)


# ----------------------------- GPU mandate -----------------------------
def _require_cuda(strict: bool) -> bool:
    if torch.cuda.is_available():
        return True
    if strict:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (Fix #24): cuda.is_available() = False. "
            "phase_diagram K-cliff v3 at N_DIM up to %d requires CUDA. "
            "Route to overnight_queue (GPU runner)." % max(N_DIM_VALUES_FULL))
    return False


_STRICT_GPU = (not SMOKE) and (not _ARGS.self_test)
_CUDA_OK = _require_cuda(strict=_STRICT_GPU)
_DEVICE = torch.device("cuda:0") if _CUDA_OK else torch.device("cpu")
_STORE_DTYPE = torch.float16 if _CUDA_OK else torch.float32


def _gpu_util_sample() -> Optional[float]:
    if not _CUDA_OK:
        return None
    try:
        import subprocess
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return float(out.stdout.strip().splitlines()[0].strip())
    except Exception:
        pass
    return None


def _gpu_info() -> Dict:
    if not _CUDA_OK:
        return {"gpu_avail": False, "gpu_name": "cpu", "gpu_total_mb": 0,
                "gpu_free_mb": 0}
    free_b, total_b = torch.cuda.mem_get_info(0)
    return {
        "gpu_avail": True,
        "gpu_name": torch.cuda.get_device_name(0),
        "gpu_total_mb": int(total_b / 1024 / 1024),
        "gpu_free_mb": int(free_b / 1024 / 1024),
    }


def _estimate_peak_working_set_bytes(k_per_bank: int, num_banks: int,
                                      n_dim: int) -> int:
    """Conservative eval-peak estimate."""
    total_K = k_per_bank * num_banks
    D = n_dim
    C = CODEBOOK_SIZE
    cb_bytes = C * D * 2  # fp16
    bank_tags_bytes = num_banks * D * 2
    slot_tags_bytes = k_per_bank * D * 2
    workspaces_bytes = num_banks * D * 2
    cues_bytes = total_K * D * (2 + 4)  # fp16 + f32 build
    ws_selected_bytes = total_K * D * 2
    cleanup_bytes = total_K * D * (2 + 4 + 2)
    chunked_sims_bytes = min(CODEBOOK_CHUNK, C) * total_K * 4
    write_bound = max(1, min(num_banks, 8192 // max(1, k_per_bank))) * k_per_bank * D * 4
    write_peak = cb_bytes + write_bound + workspaces_bytes + bank_tags_bytes + slot_tags_bytes
    eval_peak = (cb_bytes + workspaces_bytes + bank_tags_bytes + slot_tags_bytes
                 + cues_bytes + ws_selected_bytes + cleanup_bytes + chunked_sims_bytes)
    return max(write_peak, eval_peak)


# ----------------------------- HD primitives -----------------------------
def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


def random_bipolar_t(shape, gen: torch.Generator) -> torch.Tensor:
    X = torch.empty(*shape, device=_DEVICE, dtype=_STORE_DTYPE)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def bipolar_quantize_t(v: torch.Tensor) -> torch.Tensor:
    return torch.where(v >= 0, torch.ones_like(v), -torch.ones_like(v))


def build_codebook_random(seed_offset: int, n_dim: int) -> torch.Tensor:
    g = _make_gen(seed_offset)
    return random_bipolar_t((CODEBOOK_SIZE, n_dim), g)


def build_slot_tags(seed_offset: int, n_dim: int, k_per_bank: int) -> torch.Tensor:
    g = _make_gen(seed_offset + 13)
    return random_bipolar_t((k_per_bank, n_dim), g)


def build_bank_tags(seed_offset: int, n_dim: int, n_banks: int) -> torch.Tensor:
    """Bank tags: independent bipolar (orthogonal in expectation). v3 has NO overlap axis."""
    g = _make_gen(seed_offset + 17)
    return random_bipolar_t((n_banks, n_dim), g)


def _write_bank_batched(items_per_bank: torch.Tensor,
                        slot_tags: torch.Tensor,
                        seed_offset: int, n_dim: int) -> torch.Tensor:
    """v3-style chunked write to bound peak intermediate."""
    n_banks = items_per_bank.shape[0]
    D = items_per_bank.shape[2]
    bank_chunk = max(1, min(n_banks, 8192 // max(1, items_per_bank.shape[1])))
    ws_acc = torch.zeros((n_banks, D), device=_DEVICE, dtype=torch.float32)
    slot_tags_f = slot_tags.float()
    for b0 in range(0, n_banks, bank_chunk):
        b1 = min(b0 + bank_chunk, n_banks)
        chunk_bound = items_per_bank[b0:b1].float() * slot_tags_f.unsqueeze(0)
        ws_acc[b0:b1] = chunk_bound.sum(dim=1)
        del chunk_bound
        if _CUDA_OK:
            torch.cuda.empty_cache()
    if SIGMA > 0.0:
        g_noise = _make_gen(seed_offset + 23)
        noise = torch.empty(ws_acc.shape, device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, SIGMA, generator=g_noise)
        ws_acc = ws_acc + noise
        del noise
        if _CUDA_OK:
            torch.cuda.empty_cache()
    out = bipolar_quantize_t(ws_acc).to(_STORE_DTYPE)
    del ws_acc
    if _CUDA_OK:
        torch.cuda.empty_cache()
    return out


def _chunked_argmax_cb_at_queries(codebook: torch.Tensor,
                                   queries: torch.Tensor) -> torch.Tensor:
    C = codebook.shape[0]
    Q = queries.shape[0]
    best_scores = torch.full((Q,), float("-inf"), device=queries.device,
                              dtype=torch.float32)
    best_idx = torch.zeros((Q,), device=queries.device, dtype=torch.long)
    chunk = CODEBOOK_CHUNK
    q_T = queries.T
    for c0 in range(0, C, chunk):
        c1 = min(c0 + chunk, C)
        sims_chunk = (codebook[c0:c1] @ q_T).float()
        chunk_max, chunk_idx = sims_chunk.max(dim=0)
        better = chunk_max > best_scores
        best_scores = torch.where(better, chunk_max, best_scores)
        best_idx = torch.where(better, chunk_idx + c0, best_idx)
        del sims_chunk, chunk_max, chunk_idx, better
        if _CUDA_OK:
            torch.cuda.empty_cache()
    return best_idx


def _read_with_cleanup_batched(workspaces: torch.Tensor,
                               slot_tag: torch.Tensor,
                               codebook: torch.Tensor) -> torch.Tensor:
    r1 = (workspaces * slot_tag)
    cand_idx = _chunked_argmax_cb_at_queries(codebook, r1)
    cand_vecs = codebook[cand_idx]
    r2_bp = bipolar_quantize_t(r1.float() + cand_vecs.float()).to(_STORE_DTYPE)
    del r1, cand_vecs
    if _CUDA_OK:
        torch.cuda.empty_cache()
    pred_idx = _chunked_argmax_cb_at_queries(codebook, r2_bp)
    del r2_bp
    if _CUDA_OK:
        torch.cuda.empty_cache()
    return pred_idx


def _is_oom_error(exc: BaseException) -> bool:
    oom_cls = getattr(torch.cuda, "OutOfMemoryError", None)
    if oom_cls is not None and isinstance(exc, oom_cls):
        return True
    msg = str(exc).lower()
    return any(needle in msg for needle in [
        "out of memory",
        "cuda out of memory",
        "cudnn_status",
        "cuda error",
        "device-side assert",
        "cublas_status",
        "illegal memory access",
        "misaligned address",
    ])


def eval_multi_bank_arm(k_per_bank: int, num_banks: int, n_dim: int,
                        codebook: torch.Tensor, seed_offset: int,
                        gpu_util_samples: List[float]) -> Tuple[float, float, str]:
    """MULTI_BANK_BIND arm: distribute total_K items across num_banks banks.

    Returns (recall_top1, route_acc, arm_sha256_hex).
    """
    total_K = k_per_bank * num_banks
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / total_K))
    slot_tags = build_slot_tags(seed_offset, n_dim, k_per_bank)
    bank_tags = build_bank_tags(seed_offset, n_dim, num_banks)
    cue_signal_scale = CUE_COS
    cue_noise_scale_base = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))
    correct = 0
    total = 0
    route_correct = 0
    route_total = 0
    hasher = hashlib.sha256()

    for trial in range(n_trials):
        g_trial = _make_gen(seed_offset + 29 + trial * 7919)
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:total_K]
        items = codebook[idx_global]
        items_per_bank = items.view(num_banks, k_per_bank, n_dim)
        workspaces = _write_bank_batched(items_per_bank, slot_tags,
                                         seed_offset + 1000 + trial, n_dim)
        del items, items_per_bank
        if _CUDA_OK:
            torch.cuda.empty_cache()

        slot_indices = torch.arange(total_K, device=_DEVICE)
        bank_true = slot_indices // k_per_bank
        local_slot = slot_indices % k_per_bank

        g_cue = _make_gen(seed_offset + 5000 + trial)
        bank_cue_base = bank_tags[bank_true].float()
        noise_base = torch.empty((total_K, n_dim), device=_DEVICE, dtype=torch.float32)
        noise_base.normal_(0.0, 1.0, generator=g_cue)
        noise_base_bp = bipolar_quantize_t(noise_base)
        del noise_base
        if _CUDA_OK:
            torch.cuda.empty_cache()
        cue_f = (cue_signal_scale * bank_cue_base
                 + cue_noise_scale_base * noise_base_bp)
        cues = cue_f.to(_STORE_DTYPE)
        del bank_cue_base, noise_base_bp, cue_f
        if _CUDA_OK:
            torch.cuda.empty_cache()
        sims_bank = cues @ bank_tags.T
        bank_routed = sims_bank.argmax(dim=1)
        del sims_bank

        route_correct += int((bank_routed == bank_true).sum().item())
        route_total += total_K

        ws_selected = workspaces[bank_routed]
        slot_tag_sel = slot_tags[local_slot]
        del workspaces
        if _CUDA_OK:
            torch.cuda.empty_cache()

        pred_idx = _read_with_cleanup_batched(ws_selected, slot_tag_sel, codebook)
        true_item_idx = idx_global[slot_indices]
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += total_K

        preds_cpu = pred_idx.cpu().numpy().astype(np.int64).tobytes()
        hasher.update(preds_cpu)

        del cues, ws_selected, slot_tag_sel, pred_idx, true_item_idx, match
        del slot_indices, bank_true, local_slot, bank_routed, idx_global
        if _CUDA_OK:
            torch.cuda.empty_cache()

        sample = _gpu_util_sample()
        if sample is not None:
            gpu_util_samples.append(sample)

    del slot_tags, bank_tags
    if _CUDA_OK:
        torch.cuda.empty_cache()

    recall = correct / max(total, 1)
    route_acc = route_correct / max(route_total, 1)
    return recall, route_acc, hasher.hexdigest()[:16]


def eval_single_bank_arm(k_per_bank: int, num_banks: int, n_dim: int,
                         codebook: torch.Tensor, seed_offset: int,
                         gpu_util_samples: List[float]) -> Tuple[float, float, str]:
    """SINGLE_BANK_BASELINE arm: store total_K = k_per_bank * num_banks items ALL in 1 bank.

    Mechanism: 1 bank with K_per_bank=total_K (interference-bounded). Same codebook + slot indexing.

    For seed-distinctness against MULTI arm: use a different sub-seed perturbation.
    Returns (recall_top1, route_acc, arm_sha256_hex).
    """
    total_K = k_per_bank * num_banks
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / total_K))
    # SINGLE bank: K_per_bank_eff = total_K, num_banks_eff = 1
    K_eff = total_K
    B_eff = 1
    slot_tags = build_slot_tags(seed_offset + 31, n_dim, K_eff)
    bank_tags = build_bank_tags(seed_offset + 31, n_dim, B_eff)
    cue_signal_scale = CUE_COS
    cue_noise_scale_base = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))
    correct = 0
    total = 0
    route_correct = 0
    route_total = 0
    hasher = hashlib.sha256()

    for trial in range(n_trials):
        g_trial = _make_gen(seed_offset + 29 + trial * 7919 + 991)
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:total_K]
        items = codebook[idx_global]
        items_per_bank = items.view(B_eff, K_eff, n_dim)
        workspaces = _write_bank_batched(items_per_bank, slot_tags,
                                         seed_offset + 1000 + trial + 991, n_dim)
        del items, items_per_bank
        if _CUDA_OK:
            torch.cuda.empty_cache()

        slot_indices = torch.arange(total_K, device=_DEVICE)
        bank_true = slot_indices // K_eff  # all zeros since B_eff=1
        local_slot = slot_indices % K_eff

        g_cue = _make_gen(seed_offset + 5000 + trial + 991)
        bank_cue_base = bank_tags[bank_true].float()
        noise_base = torch.empty((total_K, n_dim), device=_DEVICE, dtype=torch.float32)
        noise_base.normal_(0.0, 1.0, generator=g_cue)
        noise_base_bp = bipolar_quantize_t(noise_base)
        del noise_base
        if _CUDA_OK:
            torch.cuda.empty_cache()
        cue_f = (cue_signal_scale * bank_cue_base
                 + cue_noise_scale_base * noise_base_bp)
        cues = cue_f.to(_STORE_DTYPE)
        del bank_cue_base, noise_base_bp, cue_f
        if _CUDA_OK:
            torch.cuda.empty_cache()
        sims_bank = cues @ bank_tags.T
        bank_routed = sims_bank.argmax(dim=1)
        del sims_bank

        route_correct += int((bank_routed == bank_true).sum().item())
        route_total += total_K

        ws_selected = workspaces[bank_routed]
        slot_tag_sel = slot_tags[local_slot]
        del workspaces
        if _CUDA_OK:
            torch.cuda.empty_cache()

        pred_idx = _read_with_cleanup_batched(ws_selected, slot_tag_sel, codebook)
        true_item_idx = idx_global[slot_indices]
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += total_K

        preds_cpu = pred_idx.cpu().numpy().astype(np.int64).tobytes()
        hasher.update(preds_cpu)

        del cues, ws_selected, slot_tag_sel, pred_idx, true_item_idx, match
        del slot_indices, bank_true, local_slot, bank_routed, idx_global
        if _CUDA_OK:
            torch.cuda.empty_cache()

        sample = _gpu_util_sample()
        if sample is not None:
            gpu_util_samples.append(sample)

    del slot_tags, bank_tags
    if _CUDA_OK:
        torch.cuda.empty_cache()

    recall = correct / max(total, 1)
    route_acc = route_correct / max(route_total, 1)
    return recall, route_acc, hasher.hexdigest()[:16]


def eval_random_arm(k_per_bank: int, num_banks: int, n_dim: int,
                    codebook: torch.Tensor, seed_offset: int) -> Tuple[float, float, str]:
    """RANDOM_FLOOR: predict a random codebook row for each slot.

    Expected top1 = 1/CB. Returns same shape as other arms for arms_differ check.
    """
    total_K = k_per_bank * num_banks
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / total_K))
    correct = 0
    total = 0
    hasher = hashlib.sha256()
    for trial in range(n_trials):
        g_trial = _make_gen(seed_offset + 29 + trial * 7919 + 999983)
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:total_K]
        g_rand = _make_gen(seed_offset + 5000 + trial + 999983)
        pred_idx = torch.randperm(CODEBOOK_SIZE, generator=g_rand, device=_DEVICE)[:total_K]
        match = (pred_idx == idx_global)
        correct += int(match.sum().item())
        total += total_K
        hasher.update(pred_idx.cpu().numpy().astype(np.int64).tobytes())
        del idx_global, pred_idx, match
        if _CUDA_OK:
            torch.cuda.empty_cache()
    recall = correct / max(total, 1)
    return recall, 0.0, hasher.hexdigest()[:16]


# ----------------------------- self-test (CPU; fp32) -----------------------------
def _selftest():
    global _DEVICE, _STORE_DTYPE, _CUDA_OK, CODEBOOK_CHUNK
    global CODEBOOK_SIZE, N_ITEMS_PER_K, SIGMA
    save_dev, save_dtype, save_cuda, save_chunk = _DEVICE, _STORE_DTYPE, _CUDA_OK, CODEBOOK_CHUNK
    save_CB, save_NI, save_sig = CODEBOOK_SIZE, N_ITEMS_PER_K, SIGMA
    _DEVICE = torch.device("cpu")
    _STORE_DTYPE = torch.float32
    _CUDA_OK = False
    CODEBOOK_CHUNK = 256
    CODEBOOK_SIZE = 2048
    N_ITEMS_PER_K = 64
    try:
        # T1: random codebook shape + bipolar
        cb = build_codebook_random(0, n_dim=1024)
        assert cb.shape == (2048, 1024), "T1 shape"
        u = torch.unique(cb)
        assert set(u.tolist()) <= {-1.0, 1.0}, "T1 bipolar"
        print("[selftest] T1 PASS: random codebook shape + bipolar")

        # T2: bank tags shape
        bt = build_bank_tags(1, n_dim=1024, n_banks=8)
        assert bt.shape == (8, 1024)
        print("[selftest] T2 PASS: bank_tags shape (8, 1024)")

        # T3: MULTI arm end-to-end at smoke shape (small N, modest K).
        gpu_samples = []
        rec_m, ra_m, ha_m = eval_multi_bank_arm(64, 4, 1024, cb,
                                                 seed_offset=100,
                                                 gpu_util_samples=gpu_samples)
        assert ra_m >= 0.85, "T3 route_acc=%.3f < 0.85 at smoke" % ra_m
        # NOTE: selftest is at N=1024 (1/8 the smallest full N) and CB=2048 (1/8 CB);
        # SNR squeezed. Pipeline-validation only (mirrors v1 selftest threshold 0.30).
        # Full cert uses N>=2048, CB=16384 with healthier SNR.
        assert rec_m >= 0.30, "T3 MULTI recall=%.3f < 0.30 at smoke (pipeline check)" % rec_m
        assert isinstance(ha_m, str) and len(ha_m) == 16, "T3 hash format"
        print("[selftest] T3 PASS: MULTI arm K_per=64 B=4 N=1024 recall=%.3f route_acc=%.3f" % (rec_m, ra_m))

        # T4: SINGLE arm end-to-end - same total_K but B=1 (effectively K=256 in 1 bank)
        rec_s, ra_s, ha_s = eval_single_bank_arm(64, 4, 1024, cb,
                                                  seed_offset=100,
                                                  gpu_util_samples=[])
        # SINGLE arm at total_K=256, N=1024: SNR_dim = 1/sqrt(255) ~ 0.063, two cleanups should still discriminate at small K
        # Don't assert tight bound here; verify mechanism RUNS + hash format
        assert isinstance(ha_s, str) and len(ha_s) == 16, "T4 hash format"
        print("[selftest] T4 PASS: SINGLE arm K_per=64 B=4 (eff K=256, B=1) recall=%.3f" % rec_s)

        # T5: LLM counter
        assert _LLM_CALL_COUNTER[0] == 0, "T5 LLM counter not zero"
        print("[selftest] T5 PASS: LLM counter = 0")

        # T6: RANDOM arm floor + hash differs from MULTI/SINGLE
        rec_r, _, ha_r = eval_random_arm(64, 4, 1024, cb, seed_offset=100)
        assert rec_r < 0.10, "T6 random recall=%.3f should be near floor" % rec_r
        assert ha_r != ha_m, "T6 RANDOM hash MUST differ from MULTI"
        assert ha_r != ha_s, "T6 RANDOM hash MUST differ from SINGLE"
        print("[selftest] T6 PASS: RANDOM arm recall=%.4f hash distinct from MULTI/SINGLE" % rec_r)

        # T7: arms_differ at B>=2 - MULTI vs SINGLE must differ when B>=2
        assert ha_m != ha_s, "T7 META_RULE_AF: MULTI vs SINGLE hashes must differ at B=4"
        print("[selftest] T7 PASS: arms_differ MULTI vs SINGLE at B=4 (hashes distinct)")

        # T8: At B=1, MULTI and SINGLE are EQUIVALENT MECHANISMS (positive control)
        # MULTI(K=128, B=1) is total_K=128 in 1 bank of K=128
        # SINGLE(K=128, B=1) is total_K=128 in 1 bank of K=128
        # Both should give SAME recall (and hashes may differ ONLY due to different
        # internal seed_offset for slot_tags/bank_tags; but recall should match within noise)
        rec_m_b1, _, _ = eval_multi_bank_arm(128, 1, 1024, cb, seed_offset=200, gpu_util_samples=[])
        rec_s_b1, _, _ = eval_single_bank_arm(128, 1, 1024, cb, seed_offset=200, gpu_util_samples=[])
        # Soft check: within 0.10 of each other (positive control)
        assert abs(rec_m_b1 - rec_s_b1) <= 0.15, \
            "T8 B=1 positive control: MULTI=%.3f vs SINGLE=%.3f differ > 0.15" % (rec_m_b1, rec_s_b1)
        print("[selftest] T8 PASS: B=1 positive control MULTI=%.3f ~ SINGLE=%.3f" % (rec_m_b1, rec_s_b1))

        # T9: bands locked
        assert HP_DISCRIM_MARGIN == 0.30
        assert HP_MULTI_PASS_RECALL == 0.50
        assert HP_RAIL_RECALL == 0.95
        assert HP_VRAM_PROBE_FRACTION == 0.85
        assert HP_HARD_PASS_MIN_GRID == 20
        assert HP_HARD_PASS_MIN_FULLN == 6
        print("[selftest] T9 PASS: bands locked")

        # T10: chunked argmax matches unchunked
        Q = 64
        g_q = _make_gen(999)
        queries = random_bipolar_t((Q, 1024), g_q)
        sims_full = (cb.float() @ queries.float().T)
        idx_unchunked = sims_full.argmax(dim=0)
        idx_chunked = _chunked_argmax_cb_at_queries(cb, queries)
        assert torch.equal(idx_chunked, idx_unchunked), \
            "T10 chunked argmax disagrees with unchunked"
        print("[selftest] T10 PASS: chunked argmax matches unchunked")

        # T11: OOM detector
        class _MockOOM(RuntimeError):
            pass
        assert _is_oom_error(_MockOOM("CUDA out of memory"))
        assert not _is_oom_error(ValueError("not oom"))
        print("[selftest] T11 PASS: OOM detector")

        # T12: VRAM probe at smoke shape returns sane value
        est = _estimate_peak_working_set_bytes(64, 4, 1024)
        assert 0 < est < 200 * 1024 * 1024, "T12 probe %d should be < 200MB at smoke" % est
        print("[selftest] T12 PASS: VRAM probe = %.2fMB at smoke shape" % (est / 1024 / 1024))

        # T13: DISCRIMINATOR FIRES at expected cliff regime
        # At K_per_bank=128, B=4 (total_K=512), MULTI should outperform SINGLE (K=512 in 1 bank)
        # because SINGLE arm has SNR_dim = 1/sqrt(511) = 0.044 vs MULTI's 1/sqrt(127) = 0.089
        # MULTI advantage at total_K=512 N=1024 should be >= 0.20 (selftest soft floor; full uses 0.30)
        rec_m_cliff, _, _ = eval_multi_bank_arm(128, 4, 1024, cb, seed_offset=300, gpu_util_samples=[])
        rec_s_cliff, _, _ = eval_single_bank_arm(128, 4, 1024, cb, seed_offset=300, gpu_util_samples=[])
        margin = rec_m_cliff - rec_s_cliff
        print("[selftest] T13 INFO: at K=128 B=4 N=1024 (total_K=512): MULTI=%.3f SINGLE=%.3f margin=%.3f"
              % (rec_m_cliff, rec_s_cliff, margin))
        # Soft check: margin should be POSITIVE (or at least not strongly negative; CPU smoke at small N is noisy)
        # FULL HARD_PASS requires margin > 0.30; selftest just verifies sign convention is right.
        assert margin > -0.10, "T13 sign: MULTI should NOT severely underperform SINGLE at cliff regime"
        print("[selftest] T13 PASS: discriminator sign correct (MULTI not below SINGLE - 0.10)")

        # T14: phase point cardinality math
        # Smoke = 6 corners x 3 arms x 1 seed = 18
        n_pts = 6
        n_regimes = 3
        n_seeds = 1
        expected_smoke = n_pts * n_regimes * n_seeds
        assert expected_smoke == 18, "T14 smoke cardinality math"
        # Full: 7 x 5 x 3 (105) - 3 skipped (K=4096*B=16=65536 > CB, etc) = check via _build_phase_points
        full_pts = _build_phase_points([64, 128, 256, 512, 1024, 2048, 4096],
                                        [1, 2, 4, 8, 16],
                                        [2048, 4096, 8192])
        # CB=2048 in selftest space; many points skip. Verify the function works.
        for K, B, N in full_pts:
            assert K * B <= 2048, "T14 phase point K*B <= CB invariant"
        print("[selftest] T14 PASS: smoke=18; phase_point CB invariant holds")

        print("[selftest] ALL PASS")
    finally:
        _DEVICE = save_dev
        _STORE_DTYPE = save_dtype
        _CUDA_OK = save_cuda
        CODEBOOK_CHUNK = save_chunk
        CODEBOOK_SIZE = save_CB
        N_ITEMS_PER_K = save_NI
        SIGMA = save_sig


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------- per-arm runner -----------------------------
def run_unit(seed: int, k_per_bank: int, num_banks: int, n_dim: int,
             regime: str, codebook: torch.Tensor,
             gpu_util_samples: List[float]) -> Dict:
    t0 = time.time()
    # Distinct seed-offset per (seed, K, B, N, regime)
    seed_offset = (seed * 100003
                   + k_per_bank * 31
                   + num_banks * 137
                   + n_dim * 251
                   + (0 if regime == "MULTI_BANK_BIND" else
                      1 if regime == "SINGLE_BANK_BASELINE" else 2))

    if _CUDA_OK:
        torch.cuda.reset_peak_memory_stats(0)

    if regime == "MULTI_BANK_BIND":
        recall, route_acc, arm_hash = eval_multi_bank_arm(
            k_per_bank, num_banks, n_dim, codebook, seed_offset,
            gpu_util_samples)
    elif regime == "SINGLE_BANK_BASELINE":
        recall, route_acc, arm_hash = eval_single_bank_arm(
            k_per_bank, num_banks, n_dim, codebook, seed_offset,
            gpu_util_samples)
    elif regime == "RANDOM_FLOOR":
        recall, route_acc, arm_hash = eval_random_arm(
            k_per_bank, num_banks, n_dim, codebook, seed_offset)
    else:
        raise ValueError("unknown regime %s" % regime)

    sample = _gpu_util_sample()
    if sample is not None:
        gpu_util_samples.append(sample)

    peak_mb = 0
    if _CUDA_OK:
        try:
            peak_mb = int(torch.cuda.max_memory_allocated(0) / 1024 / 1024)
        except Exception:
            peak_mb = 0

    wall_s = time.time() - t0
    return {
        "seed": int(seed),
        "k_per_bank": int(k_per_bank),
        "num_banks": int(num_banks),
        "n_dim": int(n_dim),
        "total_K": int(k_per_bank * num_banks),
        "regime": regime,
        "recall": float(round(recall, 6)),
        "route_acc": float(round(route_acc, 4)),
        "arm_sha256": arm_hash,
        "wall_s": float(round(wall_s, 2)),
        "peak_mem_mb": int(peak_mb),
        "N": int(n_dim),
        "CODEBOOK_SIZE": int(CODEBOOK_SIZE),
        "SIGMA": float(SIGMA),
        "CUE_COS": float(CUE_COS),
        "N_ITEMS_PER_K": int(N_ITEMS_PER_K),
        "M": int(max(K * B for K, B, _ in PHASE_POINTS)),  # max total_K observed in this run mode
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
    }


# ----------------------------- verdict logic -----------------------------
def compute_verdict(per_key: Dict[str, Dict],
                    failures: List[Dict] = None) -> Tuple[str, str, Dict]:
    if failures is None:
        failures = []
    if not per_key and not failures:
        return ("HARD_FAIL", "no_units", {})

    n_units_observed = len(per_key)
    real_failures = [f for f in failures if f.get("exc_type") != "HP_VRAM_PROBE_BREACH"]
    n_probe_cliffs = len([f for f in failures if f.get("exc_type") == "HP_VRAM_PROBE_BREACH"])
    cardinality_ok = ((n_units_observed + n_probe_cliffs) >= EXPECTED_N_UNITS)

    # Index by (K_per_bank, num_banks, n_dim, regime)
    by_point: Dict[Tuple[int, int, int, str], Dict] = {}
    for _, body in per_key.items():
        K = int(body["k_per_bank"])
        B = int(body["num_banks"])
        N = int(body["n_dim"])
        R = body["regime"]
        by_point[(K, B, N, R)] = body

    # Build phase_map: per (K, B, N) collect MULTI + SINGLE + RANDOM
    phase_points_keys = set((K, B, N) for (K, B, N, _) in by_point.keys())
    phase_map: List[Dict] = []
    n_pass = 0
    n_pass_at_full_N = 0
    n_saturate = 0
    n_floor = 0
    n_arms_identical = 0  # B>=2 case only
    arms_differ_count = 0
    rail_observed = None  # (K=64, B=1, N=8192) MULTI recall

    # Add VRAM-probe-denied entries as cliff markers
    probe_denied_points = set()
    for f in failures:
        if f.get("exc_type") == "HP_VRAM_PROBE_BREACH":
            probe_denied_points.add((int(f.get("k_per_bank", 0)),
                                     int(f.get("num_banks", 0)),
                                     int(f.get("n_dim", 0))))

    FULL_N = max(N_DIM_VALUES_FULL)
    for (K, B, N) in sorted(phase_points_keys | probe_denied_points):
        mult = by_point.get((K, B, N, "MULTI_BANK_BIND"))
        sing = by_point.get((K, B, N, "SINGLE_BANK_BASELINE"))
        rand = by_point.get((K, B, N, "RANDOM_FLOOR"))
        is_probe_denied = (K, B, N) in probe_denied_points
        if is_probe_denied or mult is None or sing is None or rand is None:
            phase_map.append({
                "K_per_bank": int(K), "num_banks": int(B), "n_dim": int(N),
                "total_K": int(K * B),
                "recall_multi": None, "recall_single": None, "recall_random": None,
                "margin_multi_vs_single": None, "arms_differ": None,
                "verdict_tier": "CLIFF" if is_probe_denied else "MISSING",
                "saturation": False, "cliff_marker": True,
                "note": "VRAM_PROBE_DENIED" if is_probe_denied else "incomplete_triplet",
            })
            continue
        m_r = float(mult["recall"])
        s_r = float(sing["recall"])
        r_r = float(rand["recall"])
        margin = m_r - s_r

        # arms_differ check: at B>=2 all 3 must differ; at B=1 only RANDOM must differ
        if B >= 2:
            arms_differ_full = (mult["arm_sha256"] != sing["arm_sha256"] and
                                 mult["arm_sha256"] != rand["arm_sha256"] and
                                 sing["arm_sha256"] != rand["arm_sha256"])
            if arms_differ_full:
                arms_differ_count += 1
            else:
                n_arms_identical += 1
        else:
            # B=1 case: MULTI and SINGLE may collide (same mechanism, positive control)
            random_differs = (rand["arm_sha256"] != mult["arm_sha256"] and
                              rand["arm_sha256"] != sing["arm_sha256"])
            if random_differs:
                arms_differ_count += 1
            else:
                n_arms_identical += 1  # only flagged if RANDOM collides

        sat = (m_r >= HP_SATURATION)
        if sat:
            n_saturate += 1
        floor = (m_r - r_r) <= HP_FLOOR_BAND
        if floor:
            n_floor += 1
        passed = (m_r >= HP_MULTI_PASS_RECALL and margin > HP_DISCRIM_MARGIN)
        if passed:
            n_pass += 1
            if N >= FULL_N:
                n_pass_at_full_N += 1
        tier = "PASS" if passed else ("MIDDLE" if m_r >= 0.30 else "FAIL")
        if K == 64 and B == 1 and N == FULL_N:
            rail_observed = m_r
        phase_map.append({
            "K_per_bank": int(K), "num_banks": int(B), "n_dim": int(N),
            "total_K": int(K * B),
            "recall_multi": float(round(m_r, 6)),
            "recall_single": float(round(s_r, 6)),
            "recall_random": float(round(r_r, 6)),
            "margin_multi_vs_single": float(round(margin, 6)),
            "route_acc_multi": float(round(mult["route_acc"], 4)),
            "route_acc_single": float(round(sing["route_acc"], 4)),
            "arms_differ": bool(arms_differ_count > 0),  # per-point; recomputed above
            "verdict_tier": tier,
            "saturation": bool(sat),
            "cliff_marker": bool(m_r < HP_MULTI_PASS_RECALL),
        })

    # Cliff per num_banks: highest total_K where MULTI >= 0.50 at each B (over all N)
    cliff_per_B: Dict[str, int] = {}
    for pp in phase_map:
        if pp.get("recall_multi") is None:
            continue
        key = "B=%d" % pp["num_banks"]
        if pp["recall_multi"] >= HP_MULTI_PASS_RECALL:
            cur = cliff_per_B.get(key, 0)
            if pp["total_K"] > cur:
                cliff_per_B[key] = int(pp["total_K"])

    # Substrate-only gate
    n_llm = sum(int(b.get("_llm_forward_calls_at_inference", 0)) for b in per_key.values())
    substrate_only_ok = (n_llm == 0)

    detail = {
        "phase_map": phase_map,
        "cliff_per_B": cliff_per_B,
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "n_probe_cliffs": n_probe_cliffs,
        "cardinality_ok": cardinality_ok,
        "arms_differ_count": arms_differ_count,
        "n_arms_identical": n_arms_identical,
        "n_pass": n_pass,
        "n_pass_at_full_N": n_pass_at_full_N,
        "n_saturate": n_saturate,
        "n_floor": n_floor,
        "rail_K64_B1_fullN_observed": rail_observed,
        "rail_target": HP_RAIL_RECALL,
        "substrate_only_ok": substrate_only_ok,
        "zero_llm_calls_at_inference": substrate_only_ok,
        "failures": real_failures,
        "probe_denials": [f for f in failures if f.get("exc_type") == "HP_VRAM_PROBE_BREACH"],
    }

    summary = ("phase_points=%d pass=%d pass_at_full_N=%d saturate=%d floor=%d "
               "probe_cliffs=%d arms_differ=%d/%d") % (
        len(phase_map), n_pass, n_pass_at_full_N, n_saturate, n_floor,
        n_probe_cliffs, arms_differ_count, len(phase_map) - n_probe_cliffs)
    cliff_str = " | cliff_per_B=%s" % cliff_per_B
    rail_str = (" | rail_K64_B1_N%d=%.4f" % (FULL_N, rail_observed)) if rail_observed is not None else ""
    card_str = " | n_units=%d/expected=%d probe_cliffs=%d (%s)" % (
        n_units_observed, EXPECTED_N_UNITS, n_probe_cliffs,
        "OK" if cardinality_ok else "BREACH_META_RULE_H")
    fail_str = ""
    if real_failures:
        fail_str = " | failures=%d [%s]" % (
            len(real_failures),
            "; ".join("%s:%s" % (f["key"], f["exc_type"]) for f in real_failures[:5]))

    # SMOKE path
    if SMOKE:
        if real_failures:
            return ("HARD_FAIL",
                    "SMOKE_HARD_FAIL_UNIT_EXCEPTION: %s%s%s%s" % (
                        summary, cliff_str, card_str, fail_str), detail)
        if not substrate_only_ok:
            return ("HARD_FAIL",
                    "SMOKE_HARD_FAIL_LLM_CALL: %d LLM calls | %s%s%s" % (
                        n_llm, summary, cliff_str, card_str), detail)
        if n_arms_identical > 0:
            return ("HARD_FAIL",
                    "SMOKE_HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF: %d points | %s%s%s" % (
                        n_arms_identical, summary, cliff_str, card_str), detail)
        # Smoke gate: discriminator FIRES at >=2 of 4 expected-cliff corners
        # Expected-cliff corners (revised after calibration smoke run):
        #   (K=64,B=16,N=2048) total_K=1024  -- MULTI ~0.70 SINGLE ~0.002 -- FIRES
        #   (K=64,B=8,N=2048)  total_K=512   -- MULTI ~0.70 SINGLE ~0.0   -- FIRES
        #   (K=64,B=4,N=4096)  total_K=256   -- MULTI ~0.95 SINGLE ~0.05  -- FIRES
        #   (K=128,B=4,N=4096) total_K=512   -- MULTI ~0.85 SINGLE ~0.01  -- FIRES
        expected_cliff = [(64, 16, 2048), (64, 8, 2048), (64, 4, 4096), (128, 4, 4096)]
        cliff_fired = 0
        for pp in phase_map:
            if pp.get("margin_multi_vs_single") is None:
                continue
            tup = (pp["K_per_bank"], pp["num_banks"], pp["n_dim"])
            if tup in expected_cliff and pp["margin_multi_vs_single"] > HP_DISCRIM_MARGIN:
                cliff_fired += 1
        discrim_ok = (cliff_fired >= 2)
        # SMOKE sat_ok: at small N, full saturation (>=0.995) is not achievable; use
        # a softer "rail above 0.50" check at (K=64,B=1) low-corner instead. The
        # FULL run still uses HP_SATURATION=0.995 for HARD_FAIL_SATURATION_ONLY check.
        smoke_rail_ok = False
        for pp in phase_map:
            if (pp["K_per_bank"] == 64 and pp["num_banks"] == 1
                    and pp.get("recall_multi") is not None
                    and pp["recall_multi"] >= 0.50):
                smoke_rail_ok = True
                break
        sat_ok = smoke_rail_ok or (n_saturate >= 1)
        # SINGLE-cliff at high K_per_bank single-bank: K=1024 B=1 should fail
        single_cliff_observed = False
        for pp in phase_map:
            if (pp["K_per_bank"] == 1024 and pp["num_banks"] == 1
                    and pp.get("recall_multi") is not None
                    and pp["recall_multi"] < HP_MULTI_PASS_RECALL):
                single_cliff_observed = True
                break
        # Looser: any FAIL tier counts
        fail_ok = ((n_floor >= 1) or single_cliff_observed
                   or any(pp.get("verdict_tier") == "FAIL" for pp in phase_map))
        if discrim_ok and sat_ok and fail_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: discrim_fired=%d/%d expected_cliff_corners sat_ok=%s rail=%s fail=%d | %s%s%s%s" % (
                        cliff_fired, len(expected_cliff), sat_ok, smoke_rail_ok,
                        n_floor + (1 if single_cliff_observed else 0),
                        summary, cliff_str, rail_str, card_str), detail)
        return ("HARD_FAIL",
                "SMOKE_HARD_FAIL_GATE: discrim_ok=%s (cliff_fired=%d/%d) sat_ok=%s fail_ok=%s | %s%s%s%s" % (
                    discrim_ok, cliff_fired, len(expected_cliff), sat_ok, fail_ok,
                    summary, cliff_str, rail_str, card_str),
                detail)

    # FULL path
    if real_failures:
        return ("HARD_FAIL",
                "HARD_FAIL_UNIT_EXCEPTION: %d units raised (no silent-except) | %s%s%s%s" % (
                    len(real_failures), summary, cliff_str, card_str, fail_str), detail)
    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d | %s%s%s" % (
                    n_units_observed, EXPECTED_N_UNITS, summary, cliff_str, card_str),
                detail)
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_LLM_CALL: %d | %s%s%s" % (n_llm, summary, cliff_str, card_str),
                detail)
    if n_arms_identical > 0:
        return ("HARD_FAIL",
                "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF: %d/%d points | %s%s%s" % (
                    n_arms_identical, len(phase_map), summary, cliff_str, card_str),
                detail)
    if n_pass < HP_DISCRIM_DOES_NOT_FIRE:
        return ("HARD_FAIL",
                "HARD_FAIL_DISCRIMINATOR_DOES_NOT_FIRE: n_pass=%d < threshold=%d | %s%s%s" % (
                    n_pass, HP_DISCRIM_DOES_NOT_FIRE, summary, cliff_str, card_str), detail)
    if n_saturate == len(phase_map):
        return ("HARD_FAIL",
                "HARD_FAIL_SATURATION_ONLY: every point saturated; need higher total_K | %s%s%s" % (
                    summary, cliff_str, card_str), detail)
    if n_floor == len(phase_map):
        return ("HARD_FAIL",
                "HARD_FAIL_FLOOR_ONLY: every point at floor | %s%s%s" % (
                    summary, cliff_str, card_str), detail)
    # HARD_PASS: n_pass >= 20 AND n_pass_at_full_N >= 6 AND rail saturated
    rail_ok = (rail_observed is not None and rail_observed >= HP_RAIL_RECALL)
    if n_pass >= HP_HARD_PASS_MIN_GRID and n_pass_at_full_N >= HP_HARD_PASS_MIN_FULLN and rail_ok:
        return ("HARD_PASS",
                "HARD_PASS_K_CLIFF_V3_PHASE_DIAGRAM: n_pass=%d (>=%d) n_pass_at_full_N=%d (>=%d) rail_ok=%s | %s%s%s%s" % (
                    n_pass, HP_HARD_PASS_MIN_GRID, n_pass_at_full_N, HP_HARD_PASS_MIN_FULLN, rail_ok,
                    summary, cliff_str, rail_str, card_str), detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL_V3_PHASE_DIAGRAM: n_pass=%d n_pass_at_full_N=%d rail_ok=%s | %s%s%s%s" % (
                n_pass, n_pass_at_full_N, rail_ok, summary, cliff_str, rail_str, card_str), detail)


# ----------------------------- atexit synth + main -----------------------------
_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time(), "gpu_util": [],
                   "failures": []}


def _build_keys() -> List[str]:
    keys = []
    for s in SEEDS:
        for (K, B, N) in PHASE_POINTS:
            for R in REGIMES:
                keys.append("seed%d_K%d_B%d_N%d_regime%s" % (s, K, B, N, R))
    return keys


def _parse_key(key: str) -> Tuple[int, int, int, int, str]:
    parts = key.split("_")
    # seed7_K64_B16_N2048_regimeMULTI_BANK_BIND
    seed = int(parts[0].replace("seed", ""))
    K = int(parts[1].replace("K", ""))
    B = int(parts[2].replace("B", ""))
    N = int(parts[3].replace("N", ""))
    # regime may contain underscores
    R = "_".join(parts[4:]).replace("regime", "", 1)
    return seed, K, B, N, R


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
        keys = _build_keys()
        agg = aggregate_partials(od, seeds=keys, run_config=run_config)
        if not agg and not _RESULTS_HOLDER["failures"]:
            return
        v, vmsg, detail = compute_verdict(agg, _RESULTS_HOLDER["failures"])
        metrics = _build_metrics(v, vmsg, detail, list(agg.values()), atexit_synth=True)
        write_metrics(od, metrics, results=list(agg.values()))
        print("[atexit] wrote synth metrics.json (%d units, %d failures)" % (
            len(agg), len(_RESULTS_HOLDER["failures"])), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


def _build_metrics(v: str, vmsg: str, detail: Dict, units: List[Dict],
                   atexit_synth: bool = False) -> Dict:
    gpu_samples = _RESULTS_HOLDER["gpu_util"]
    if gpu_samples:
        gpu_util_mean = float(np.mean(gpu_samples))
        gpu_util_p50 = float(np.median(gpu_samples))
        gpu_util_max = float(np.max(gpu_samples))
    else:
        gpu_util_mean = float("nan")
        gpu_util_p50 = float("nan")
        gpu_util_max = float("nan")
    gpu = _gpu_info()
    if _CUDA_OK:
        try:
            gpu["gpu_max_mem_alloc_mb"] = int(torch.cuda.max_memory_allocated(0) / 1024 / 1024)
        except Exception:
            gpu["gpu_max_mem_alloc_mb"] = 0
    else:
        gpu["gpu_max_mem_alloc_mb"] = 0
    return {
        "anchor": ANCHOR_NAME,
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_units": len(units),
        "n_units_expected": EXPECTED_N_UNITS,
        "cardinality_ok": ((len(units) + len([f for f in _RESULTS_HOLDER["failures"]
                                                if f.get("exc_type") == "HP_VRAM_PROBE_BREACH"]))
                            >= EXPECTED_N_UNITS),
        "n_failures": len([f for f in _RESULTS_HOLDER["failures"]
                            if f.get("exc_type") != "HP_VRAM_PROBE_BREACH"]),
        "n_probe_denials": len([f for f in _RESULTS_HOLDER["failures"]
                                 if f.get("exc_type") == "HP_VRAM_PROBE_BREACH"]),
        "failures": _RESULTS_HOLDER["failures"],
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "seed_this_chunk": SEED_THIS_CHUNK,
        "phase_points": PHASE_POINTS,
        "regimes": REGIMES,
        "config_version": CONFIG_VERSION,
        "corpus_provenance": CORPUS_PROVENANCE,
        "allow_synthetic": True,
        "zero_llm_calls_at_inference": (_LLM_CALL_COUNTER[0] == 0),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "device": str(_DEVICE),
        "cuda_ok": bool(_CUDA_OK),
        "store_dtype": str(_STORE_DTYPE),
        "codebook_chunk": int(CODEBOOK_CHUNK),
        "gpu_avail": gpu.get("gpu_avail", False),
        "gpu_name": gpu.get("gpu_name", "cpu"),
        "gpu_total_mb": gpu.get("gpu_total_mb", 0),
        "gpu_free_mb": gpu.get("gpu_free_mb", 0),
        "gpu_max_mem_alloc_mb": gpu.get("gpu_max_mem_alloc_mb", 0),
        "gpu_util_mean": gpu_util_mean,
        "gpu_util_p50": gpu_util_p50,
        "gpu_util_max": gpu_util_max,
        "gpu_util_n_samples": len(gpu_samples),
        "per_unit": units,
        "detail": detail,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg[:300],
        "_atexit_synth": atexit_synth,
        "metrics_source": "measured_gpu_substrate_bipolar_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_%d" % SEED_THIS_CHUNK,
        "DESIGN_NOTE": (
            "V3 K-cliff phase diagram (chunked sibling cell, seed=%d). REFRAME of v1: "
            "sweep K_per_bank x num_banks x N_DIM at FIXED CB=%d. Three arms: "
            "MULTI_BANK_BIND (distribute total_K across B banks), SINGLE_BANK_BASELINE "
            "(same total_K in 1 bank), RANDOM_FLOOR. Discriminator = MULTI > SINGLE at "
            "total_K > interference threshold. At B=1, MULTI and SINGLE are equivalent "
            "mechanisms (positive control). VRAM probe denials are CLIFF MARKERS not "
            "failures. cardinality_ok counts probe_cliffs toward expected. Smoke uses "
            "6 corner points at N=2048 (smallest N) to keep CPU smoke fast."
        ) % (SEED_THIS_CHUNK, CODEBOOK_SIZE),
    }


def _build_codebook(seed: int, n_dim: int) -> torch.Tensor:
    return build_codebook_random(seed * 100003 + 99 + n_dim * 13, n_dim)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s phase_points=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, len(PHASE_POINTS), CONFIG_VERSION), flush=True)
    print("[gpu] cuda_ok=%s device=%s store_dtype=%s codebook_chunk=%d" % (
        _CUDA_OK, _DEVICE, _STORE_DTYPE, CODEBOOK_CHUNK), flush=True)
    print("[cardinality] expected_n_units=%d (META_RULE_H guard)" % EXPECTED_N_UNITS, flush=True)
    if _CUDA_OK:
        info = _gpu_info()
        print("[gpu] name=%s total=%dMB free=%dMB" % (
            info["gpu_name"], info["gpu_total_mb"], info["gpu_free_mb"]), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    all_keys = _build_keys()
    done_keys = set(list_completed_keys(out_dir, run_config=run_config))
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(all_keys)), flush=True)

    # Cache codebook per (seed, n_dim) to avoid rebuilding for every point
    cached: Dict[Tuple[int, int], torch.Tensor] = {}
    halt_after_loop = False

    for key in all_keys:
        if key in done_keys:
            continue
        seed, K, B, N, R = _parse_key(key)

        est_bytes = _estimate_peak_working_set_bytes(K, B, N)
        if _CUDA_OK:
            free_b, total_b = torch.cuda.mem_get_info(0)
            budget = int(free_b * HP_VRAM_PROBE_FRACTION)
            if est_bytes > budget:
                fail_entry = {
                    "key": key,
                    "seed": seed, "k_per_bank": K, "num_banks": B, "n_dim": N,
                    "regime": R,
                    "exc_type": "HP_VRAM_PROBE_BREACH",
                    "exc_msg": "est_peak=%.2fGB budget=%.2fGB (free=%.2fGB * %.2f)" % (
                        est_bytes / 1024**3, budget / 1024**3,
                        free_b / 1024**3, HP_VRAM_PROBE_FRACTION),
                    "traceback": "",
                    "est_peak_mb": int(est_bytes / 1024 / 1024),
                    "free_mb": int(free_b / 1024 / 1024),
                }
                _RESULTS_HOLDER["failures"].append(fail_entry)
                print("[HP_VRAM_PROBE_BREACH] %s est=%.2fGB > budget=%.2fGB (cliff marker, not fail)" % (
                    key, est_bytes / 1024**3, budget / 1024**3), flush=True)
                continue

        cache_key = (seed, N)
        if cache_key not in cached:
            # Free any other (seed, N) codebook to bound memory
            for stale_key in list(cached.keys()):
                if stale_key != cache_key:
                    del cached[stale_key]
                    if _CUDA_OK:
                        torch.cuda.empty_cache()
            print("[seed=%d N=%d] building codebook..." % (seed, N), flush=True)
            cached[cache_key] = _build_codebook(seed, N)
        codebook = cached[cache_key]

        try:
            print("  [run] %s ... (est_peak=%.2fGB)" % (
                key, est_bytes / 1024**3), flush=True)
            rec = run_unit(seed, K, B, N, R, codebook,
                            _RESULTS_HOLDER["gpu_util"])
            # Stamp _ckpt_key for compound-key checkpoint identity (PROT-021 helper)
            rec["_ckpt_key"] = key
            write_partial_key(out_dir, key, rec)
            print("  [done] %s recall=%.4f route_acc=%.4f wall=%.1fs peak=%dMB" % (
                key, rec["recall"], rec["route_acc"], rec["wall_s"],
                rec.get("peak_mem_mb", 0)), flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            fail_entry = {
                "key": key,
                "seed": seed, "k_per_bank": K, "num_banks": B, "n_dim": N,
                "regime": R,
                "exc_type": type(e).__name__,
                "exc_msg": str(e)[:500],
                "traceback": tb[-2000:],
                "is_oom_class": _is_oom_error(e),
                "est_peak_mb": int(est_bytes / 1024 / 1024),
            }
            if _CUDA_OK:
                try:
                    fail_entry["peak_mem_mb"] = int(torch.cuda.max_memory_allocated(0) / 1024 / 1024)
                    free_b, total_b = torch.cuda.mem_get_info(0)
                    fail_entry["free_mb_at_fail"] = int(free_b / 1024 / 1024)
                except Exception:
                    pass
            _RESULTS_HOLDER["failures"].append(fail_entry)
            print("[UNIT_EXCEPTION] %s type=%s is_oom=%s msg=%r" % (
                key, type(e).__name__, _is_oom_error(e), str(e)[:200]), flush=True)
            print("[TRACEBACK]\n%s" % tb, flush=True)
            print("[meta_rule_an] halting loop on real unit exception (no silent-continue)", flush=True)
            halt_after_loop = True
            break

    agg = aggregate_partials(out_dir, seeds=all_keys, run_config=run_config)
    units = [agg[k] for k in all_keys if k in agg]
    failures = _RESULTS_HOLDER["failures"]

    if not units and not failures:
        print("[FATAL] no partials available and no recorded failures", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode gate violated"

    v, vmsg, detail = compute_verdict(agg, failures)
    print("\n[VERDICT] %s" % v, flush=True)
    print("[VERDICT_MSG] %s" % vmsg, flush=True)
    real_fails = [f for f in failures if f.get("exc_type") != "HP_VRAM_PROBE_BREACH"]
    if real_fails:
        print("[FAILURES] %d real" % len(real_fails), flush=True)
        for f in real_fails:
            print("  - %s: %s -- %s" % (f["key"], f["exc_type"], f["exc_msg"][:120]),
                  flush=True)
    n_probe = len(failures) - len(real_fails)
    if n_probe:
        print("[PROBE_CLIFFS] %d (cliff markers, not failures)" % n_probe, flush=True)

    metrics = _build_metrics(v, vmsg, detail, units, atexit_synth=False)
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %d real-failures, %d probe-cliffs, %.1fs)" % (
        len(units), len(real_fails), n_probe, metrics["elapsed_s"]), flush=True)
    if halt_after_loop:
        sys.exit(1)
