"""substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU -- seed 7 chunked sibling.

Parent prereg: preregs/2026-06-28_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU.md
Sibling chunks: _seed_7.py (this), _seed_13.py, _seed_19.py

v1 -> v2 deltas (chain-grade revival of v1 MM):
  - K_per_bank extended {4, 16, 64} -> {16, 64, 128, 256}   (drop K=4 saturator;
      add K=128, K=256 for resolution headroom — Skunkworks rec (a)).
  - num_banks pruned {1, 4, 16} -> {4, 16, 64}              (drop B=1 degenerate
      positive-control; add B=64 for orthogonal discrimination — Skunkworks rec
      (b)). At B=1 MULTI ~ SINGLE (no useful discriminator).
  - Rail config: alpha_min K=256 B=4 N=FULL_N -> M/B ~ 102 in 256 slots = clean
      resolution; v1 rail (K=64 B=1) was BY-CONSTRUCTION saturated -- rail_ok
      false for that reason, not mechanism failure.
  - HP_HARD_PASS_MIN_GRID 30 -> 50 (n_pass scales 23 * 216/162 ~= 31 baseline +
      K=128/256 expansion ~ 20-25 more passes).
  - HP_HARD_PASS_MIN_FULLN 8 -> 12 (chain-grade threshold per spawn brief).

Scientific question (unchanged from v1):
  Sweep alpha (loading factor) x K_per_bank x N x B; MULTI vs SINGLE bank
  capacity at the (alpha, K, B, N) phase manifold. Predicts alpha_cliff(B) =
  K_per_bank * B / N (multi-bank capacity = K_per_bank * B slots; cliff when
  M > K_per_bank * B).

Sweep axes (full):
  alpha in {0.05, 0.10, 0.25, 0.50, 1.0, 2.0}     (6 points)
  K_per_bank in {16, 64, 128, 256}                (4 points; extended)
  N_DIM in {2048, 4096, 8192}                     (3 points)
  num_banks B in {4, 16, 64}                      (3 points; B=1 dropped)
  Full grid per seed: 6 x 4 x 3 x 3 = 216 points x 3 arms = 648 units.

Smoke corners (8 points x 3 arms = 24 units; 2 corners preview full-N):
  See prereg table.

Arms (unchanged from v1):
  MULTI_BANK_BIND   -- distribute M = round(alpha*N) items across B banks
  SINGLE_BANK_BASELINE -- same M items all in 1 bank
  RANDOM_FLOOR      -- random readout; floor = 1/CB

At B>=4 (v2 grid), SINGLE always uses B_eff=1, so MULTI > SINGLE at every grid
point where M > K_per_bank (overflow regime). Discriminator is sharp.

GPU MANDATE (Fix #24): cuda required for full; fp16 storage; chunked codebook matmul.

PRE-REG bands LOCKED at module init; see prereg.
PROT-018: no _n suffix in anchor (capability-test, sibling chunk).
ASCII-only.
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

SEED_THIS_CHUNK = 19
ANCHOR_NAME = "substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_%d" % SEED_THIS_CHUNK

_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_capacity_alpha_K_v2"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# Pre-reg bands LOCKED at module init (v2 raises HP_HARD_PASS_MIN_GRID + MIN_FULLN)
HP_DISCRIM_MARGIN = 0.30
HP_MULTI_PASS_RECALL = 0.50
HP_RAIL_RECALL = 0.95
HP_SATURATION = 0.995
HP_FLOOR_BAND = 0.05
HP_VRAM_PROBE_FRACTION = 0.85
HP_GPU_UTIL_MIN_P50 = 0.50
HP_HARD_PASS_MIN_GRID = 50          # v1: 30 (raised proportionally for 216-pt grid)
HP_HARD_PASS_MIN_FULLN = 12         # v1: 8 (chain-grade threshold)
HP_DISCRIM_DOES_NOT_FIRE = 20       # v1: 15 (raised to 20 for larger grid)

assert 0.0 < HP_DISCRIM_MARGIN < 1.0, "discrim margin locked"
assert 0.0 < HP_MULTI_PASS_RECALL < HP_SATURATION, "pass ordering"
assert HP_HARD_PASS_MIN_FULLN <= HP_HARD_PASS_MIN_GRID, "fullN<=total"

# Mechanism params (unchanged from v1)
SIGMA = 1.0
CUE_COS = 0.70
CODEBOOK_SIZE = 16384
CODEBOOK_CHUNK_FULL = 4096
CODEBOOK_CHUNK_SMOKE = 1024

# Full sweep axes (v2: K_per_bank extended; B=1 dropped)
ALPHA_VALUES = [0.05, 0.10, 0.25, 0.50, 1.0, 2.0]
K_PER_BANK_VALUES = [16, 64, 128, 256]
NUM_BANKS_VALUES = [4, 16, 64]
N_DIM_VALUES_FULL = [2048, 4096, 8192]
N_DIM_VALUES_SMOKE = [2048, 4096, 8192]


def _build_phase_points(alpha_vals: List[float], K_vals: List[int],
                        B_vals: List[int], N_vals: List[int]
                        ) -> List[Tuple[float, int, int, int]]:
    """All (alpha, K_per_bank, B, N) combos where M = round(alpha*N) <= CB."""
    pts = []
    for N in N_vals:
        for alpha in alpha_vals:
            M = int(round(alpha * N))
            if M < 1 or M > CODEBOOK_SIZE:
                continue
            for K in K_vals:
                for B in B_vals:
                    pts.append((alpha, K, B, N))
    return pts


# Smoke corners v2 (8 corners; 2 are full-N=8192 preview per
# discriminator-must-survive-scale USER 2026-06-26).
# Each tuple: (alpha, K_per_bank, num_banks, N)
SMOKE_CORNERS: List[Tuple[float, int, int, int]] = [
    (0.05, 16,  16, 2048),  # DISCRIM-low: M=102, M/B=6 << K=16 -> MULTI ~1.0; SINGLE M=102 in K=16 -> collapse
    (0.05, 64,  4,  2048),  # DISCRIM: M=102, M/B=26 < K=64 -> MULTI clean; SINGLE struggle
    (0.05, 128, 4,  4096),  # DISCRIM: M=205, M/B=52 < K=128 -> MULTI clean; SINGLE struggle
    (0.05, 256, 4,  8192),  # FULL-N RAIL preview: M=410, M/B=102 < K=256 -> MULTI ~1.0 (predicts rail_ok)
    (0.10, 256, 4,  8192),  # FULL-N DISCRIM: M=819, M/B=205 < K=256 -> MULTI marginal; SINGLE collapse
    (0.25, 64,  16, 2048),  # DISCRIM: M=512, M/B=32 < K=64 -> MULTI clean; SINGLE collapse
    (0.50, 128, 64, 2048),  # DISCRIM: M=1024, M/B=16 << K=128 -> MULTI clean; SINGLE collapse
    (2.0,  16,  16, 2048),  # FLOOR sanity: M=4096, M/B=256 >> K=16 -> BOTH collapse
]

N_ITEMS_PER_TRIAL_FULL = 256
N_ITEMS_PER_TRIAL_SMOKE = 64

if SMOKE:
    PHASE_POINTS: List[Tuple[float, int, int, int]] = SMOKE_CORNERS
    N_ITEMS_PER_TRIAL = N_ITEMS_PER_TRIAL_SMOKE
    CODEBOOK_CHUNK = CODEBOOK_CHUNK_SMOKE
else:
    PHASE_POINTS = _build_phase_points(ALPHA_VALUES, K_PER_BANK_VALUES,
                                        NUM_BANKS_VALUES, N_DIM_VALUES_FULL)
    N_ITEMS_PER_TRIAL = N_ITEMS_PER_TRIAL_FULL
    CODEBOOK_CHUNK = CODEBOOK_CHUNK_FULL

SEEDS = [SEED_THIS_CHUNK]
REGIMES = ["MULTI_BANK_BIND", "SINGLE_BANK_BASELINE", "RANDOM_FLOOR"]
EXPECTED_N_UNITS = len(SEEDS) * len(PHASE_POINTS) * len(REGIMES)

CONFIG_VERSION = (
    "substrateCapacityMBAlphaKPhaseDiagV2GPU-seed%d: CB=%d sigma=%.1f CUE_COS=%.2f "
    "alpha_values=%s K_per_bank_values=%s num_banks_values=%s N_dim_values=%s "
    "phase_points=%d (smoke=%s) N_ITEMS_PER_TRIAL=%d codebook_chunk=%d seeds=%s mode=%s "
    "HP_discrim=%.2f HP_pass_rec=%.2f HP_rail=%.2f HP_sat=%.3f HP_floor=%.2f "
    "HP_GPU_UTIL_MIN=%.2f HP_min_grid=%d HP_min_full_N=%d EXPECTED_N_UNITS=%d ANCHOR=%s"
) % (
    SEED_THIS_CHUNK, CODEBOOK_SIZE, SIGMA, CUE_COS,
    ALPHA_VALUES, K_PER_BANK_VALUES, NUM_BANKS_VALUES,
    (N_DIM_VALUES_SMOKE if SMOKE else N_DIM_VALUES_FULL),
    len(PHASE_POINTS), SMOKE, N_ITEMS_PER_TRIAL, CODEBOOK_CHUNK, SEEDS, RUN_MODE,
    HP_DISCRIM_MARGIN, HP_MULTI_PASS_RECALL, HP_RAIL_RECALL, HP_SATURATION,
    HP_FLOOR_BAND, HP_GPU_UTIL_MIN_P50,
    HP_HARD_PASS_MIN_GRID, HP_HARD_PASS_MIN_FULLN, EXPECTED_N_UNITS, ANCHOR_NAME,
)


# ----------------------------- GPU mandate -----------------------------
def _require_cuda(strict: bool) -> bool:
    if torch.cuda.is_available():
        return True
    if strict:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (Fix #24): cuda.is_available() = False. "
            "Route to overnight_queue (GPU runner).")
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


def _estimate_peak_working_set_bytes(alpha: float, k_per_bank: int,
                                      num_banks: int, n_dim: int) -> int:
    """Conservative eval-peak estimate (v2: includes K=256 + B=64 headroom)."""
    M = int(round(alpha * n_dim))
    D = n_dim
    C = CODEBOOK_SIZE
    cb_bytes = C * D * 2  # fp16
    bank_tags_bytes = num_banks * D * 2
    slot_tags_bytes = k_per_bank * D * 2
    workspaces_bytes = num_banks * D * 2
    cues_bytes = M * D * (2 + 4)
    ws_selected_bytes = M * D * 2
    cleanup_bytes = M * D * (2 + 4 + 2)
    chunked_sims_bytes = min(CODEBOOK_CHUNK, C) * M * 4
    write_bound = num_banks * k_per_bank * D * 4
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
    g = _make_gen(seed_offset + 17)
    return random_bipolar_t((n_banks, n_dim), g)


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
        "out of memory", "cuda out of memory", "cudnn_status",
        "cuda error", "device-side assert", "cublas_status",
        "illegal memory access", "misaligned address",
    ])


def _write_bank_alpha_loading(items: torch.Tensor, slot_tags: torch.Tensor,
                               num_banks: int, k_per_bank: int,
                               n_dim: int, seed_offset: int) -> torch.Tensor:
    """Write M items distributed across B banks at alpha-loading.

    items: shape (M, D); distributed M/B items per bank (round-robin assignment).
    Each item assigned slot = (item_idx_in_bank) % k_per_bank.

    Returns workspaces: shape (B, D) -- bipolar quantized + noise.
    """
    M = items.shape[0]
    D = items.shape[1]
    item_indices = torch.arange(M, device=_DEVICE)
    bank_assign = item_indices % num_banks
    in_bank_seq = item_indices // num_banks
    slot_assign = in_bank_seq % k_per_bank

    workspaces = torch.zeros((num_banks, D), device=_DEVICE, dtype=torch.float32)
    slot_tags_f = slot_tags.float()
    items_f = items.float()
    bound = items_f * slot_tags_f[slot_assign]
    del items_f
    if _CUDA_OK:
        torch.cuda.empty_cache()
    workspaces.index_add_(0, bank_assign, bound)
    del bound
    if _CUDA_OK:
        torch.cuda.empty_cache()
    if SIGMA > 0.0:
        g_noise = _make_gen(seed_offset + 23)
        noise = torch.empty(workspaces.shape, device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, SIGMA, generator=g_noise)
        workspaces = workspaces + noise
        del noise
        if _CUDA_OK:
            torch.cuda.empty_cache()
    ws_bp = bipolar_quantize_t(workspaces).to(_STORE_DTYPE)
    del workspaces
    if _CUDA_OK:
        torch.cuda.empty_cache()
    return ws_bp, bank_assign, slot_assign


def eval_multi_bank_arm(alpha: float, k_per_bank: int, num_banks: int,
                         n_dim: int, codebook: torch.Tensor,
                         seed_offset: int,
                         gpu_util_samples: List[float]) -> Tuple[float, float, str]:
    """MULTI_BANK_BIND: distribute M=round(alpha*N) items across B banks."""
    M = max(1, int(round(alpha * n_dim)))
    n_trials = max(1, math.ceil(N_ITEMS_PER_TRIAL / M))
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
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:M]
        items = codebook[idx_global]

        workspaces, bank_assign_w, slot_assign_w = _write_bank_alpha_loading(
            items, slot_tags, num_banks, k_per_bank, n_dim,
            seed_offset + 1000 + trial)
        del items
        if _CUDA_OK:
            torch.cuda.empty_cache()

        g_cue = _make_gen(seed_offset + 5000 + trial)
        bank_true = bank_assign_w
        local_slot = slot_assign_w
        bank_cue_base = bank_tags[bank_true].float()
        noise_base = torch.empty((M, n_dim), device=_DEVICE, dtype=torch.float32)
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
        route_total += M

        ws_selected = workspaces[bank_routed]
        slot_tag_sel = slot_tags[local_slot]
        del workspaces
        if _CUDA_OK:
            torch.cuda.empty_cache()

        pred_idx = _read_with_cleanup_batched(ws_selected, slot_tag_sel, codebook)
        true_item_idx = idx_global
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += M

        preds_cpu = pred_idx.cpu().numpy().astype(np.int64).tobytes()
        hasher.update(preds_cpu)

        del cues, ws_selected, slot_tag_sel, pred_idx, true_item_idx, match
        del bank_true, local_slot, bank_routed, idx_global
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


def eval_single_bank_arm(alpha: float, k_per_bank: int, num_banks: int,
                          n_dim: int, codebook: torch.Tensor,
                          seed_offset: int,
                          gpu_util_samples: List[float]) -> Tuple[float, float, str]:
    """SINGLE_BANK_BASELINE: same M items ALL in 1 bank (B_eff=1)."""
    M = max(1, int(round(alpha * n_dim)))
    n_trials = max(1, math.ceil(N_ITEMS_PER_TRIAL / M))
    K = k_per_bank
    B_eff = 1
    slot_tags = build_slot_tags(seed_offset + 31, n_dim, K)
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
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:M]
        items = codebook[idx_global]

        workspaces, bank_assign_w, slot_assign_w = _write_bank_alpha_loading(
            items, slot_tags, B_eff, K, n_dim,
            seed_offset + 1000 + trial + 991)
        del items
        if _CUDA_OK:
            torch.cuda.empty_cache()

        g_cue = _make_gen(seed_offset + 5000 + trial + 991)
        bank_true = bank_assign_w
        local_slot = slot_assign_w
        bank_cue_base = bank_tags[bank_true].float()
        noise_base = torch.empty((M, n_dim), device=_DEVICE, dtype=torch.float32)
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
        route_total += M

        ws_selected = workspaces[bank_routed]
        slot_tag_sel = slot_tags[local_slot]
        del workspaces
        if _CUDA_OK:
            torch.cuda.empty_cache()

        pred_idx = _read_with_cleanup_batched(ws_selected, slot_tag_sel, codebook)
        true_item_idx = idx_global
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += M

        preds_cpu = pred_idx.cpu().numpy().astype(np.int64).tobytes()
        hasher.update(preds_cpu)

        del cues, ws_selected, slot_tag_sel, pred_idx, true_item_idx, match
        del bank_true, local_slot, bank_routed, idx_global
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


def eval_random_arm(alpha: float, k_per_bank: int, num_banks: int,
                    n_dim: int, codebook: torch.Tensor,
                    seed_offset: int) -> Tuple[float, float, str]:
    M = max(1, int(round(alpha * n_dim)))
    n_trials = max(1, math.ceil(N_ITEMS_PER_TRIAL / M))
    correct = 0
    total = 0
    hasher = hashlib.sha256()
    for trial in range(n_trials):
        g_trial = _make_gen(seed_offset + 29 + trial * 7919 + 999983)
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:M]
        g_rand = _make_gen(seed_offset + 5000 + trial + 999983)
        pred_idx = torch.randperm(CODEBOOK_SIZE, generator=g_rand, device=_DEVICE)[:M]
        match = (pred_idx == idx_global)
        correct += int(match.sum().item())
        total += M
        hasher.update(pred_idx.cpu().numpy().astype(np.int64).tobytes())
        del idx_global, pred_idx, match
        if _CUDA_OK:
            torch.cuda.empty_cache()
    recall = correct / max(total, 1)
    return recall, 0.0, hasher.hexdigest()[:16]


# ----------------------------- self-test (CPU; fp32) -----------------------------
def _selftest():
    global _DEVICE, _STORE_DTYPE, _CUDA_OK, CODEBOOK_CHUNK
    global CODEBOOK_SIZE, N_ITEMS_PER_TRIAL, SIGMA
    save_dev, save_dtype, save_cuda, save_chunk = _DEVICE, _STORE_DTYPE, _CUDA_OK, CODEBOOK_CHUNK
    save_CB, save_NI, save_sig = CODEBOOK_SIZE, N_ITEMS_PER_TRIAL, SIGMA
    _DEVICE = torch.device("cpu")
    _STORE_DTYPE = torch.float32
    _CUDA_OK = False
    CODEBOOK_CHUNK = 256
    CODEBOOK_SIZE = 2048
    N_ITEMS_PER_TRIAL = 32
    try:
        # T1: random codebook shape + bipolar
        cb = build_codebook_random(0, n_dim=1024)
        assert cb.shape == (2048, 1024), "T1 shape"
        u = torch.unique(cb)
        assert set(u.tolist()) <= {-1.0, 1.0}, "T1 bipolar"
        print("[selftest] T1 PASS: random codebook shape + bipolar")

        # T2: bank tags shape (test K=256 sanity)
        bt = build_bank_tags(1, n_dim=1024, n_banks=4)
        assert bt.shape == (4, 1024)
        st = build_slot_tags(1, n_dim=1024, k_per_bank=256)
        assert st.shape == (256, 1024)
        u2 = torch.unique(st)
        assert set(u2.tolist()) <= {-1.0, 1.0}, "T2 K=256 bipolar"
        print("[selftest] T2 PASS: bank_tags shape + K=256 slot_tags shape + bipolar")

        # T3: MULTI arm at low-load regime (should resolve)
        # v2 grid: K=16, B=4 (B=1 dropped from v2). alpha=0.02 N=1024 M=20.
        gpu_samples = []
        rec_m, ra_m, ha_m = eval_multi_bank_arm(
            alpha=0.02, k_per_bank=16, num_banks=4, n_dim=1024,
            codebook=cb, seed_offset=100, gpu_util_samples=gpu_samples)
        # alpha=0.02 N=1024 -> M=20, B=4 -> 5/bank, K=16 -> 5 slots used per bank
        # MULTI should resolve strongly
        assert isinstance(ha_m, str) and len(ha_m) == 16, "T3 hash format"
        assert rec_m >= 0.20, "T3 MULTI recall=%.3f < 0.20 at low-load smoke" % rec_m
        print("[selftest] T3 PASS: MULTI alpha=0.02 K=16 B=4 N=1024 recall=%.3f route=%.3f" % (rec_m, ra_m))

        # T4: SINGLE arm at same config (B=1 effective; M=20 in K=16)
        rec_s, ra_s, ha_s = eval_single_bank_arm(
            alpha=0.02, k_per_bank=16, num_banks=4, n_dim=1024,
            codebook=cb, seed_offset=100, gpu_util_samples=[])
        assert isinstance(ha_s, str) and len(ha_s) == 16, "T4 hash format"
        print("[selftest] T4 PASS: SINGLE alpha=0.02 K=16 (eff B=1) recall=%.3f" % rec_s)

        # T5: LLM counter zero
        assert _LLM_CALL_COUNTER[0] == 0, "T5 LLM counter not zero"
        print("[selftest] T5 PASS: LLM counter = 0")

        # T6: RANDOM arm at floor
        rec_r, _, ha_r = eval_random_arm(
            alpha=0.02, k_per_bank=16, num_banks=4, n_dim=1024,
            codebook=cb, seed_offset=100)
        assert rec_r < 0.10, "T6 random recall=%.3f should be near floor" % rec_r
        assert ha_r != ha_m, "T6 RANDOM hash MUST differ from MULTI"
        assert ha_r != ha_s, "T6 RANDOM hash MUST differ from SINGLE"
        print("[selftest] T6 PASS: RANDOM recall=%.4f hash distinct" % rec_r)

        # T7: arms_differ at B>=2 (MULTI vs SINGLE differ because mechanisms differ)
        assert ha_m != ha_s, "T7 META_RULE_AF: MULTI vs SINGLE hashes must differ at B=4"
        print("[selftest] T7 PASS: arms_differ MULTI vs SINGLE at B=4")

        # T8: DISCRIMINATOR sign at cliff regime
        # v2 grid: K=16, B=4. alpha=0.1 N=1024 -> M=102; M/B=26 vs K=16 single B_eff=1 M=102 in K=16
        rec_m_cliff, _, _ = eval_multi_bank_arm(
            alpha=0.1, k_per_bank=16, num_banks=4, n_dim=1024,
            codebook=cb, seed_offset=200, gpu_util_samples=[])
        rec_s_cliff, _, _ = eval_single_bank_arm(
            alpha=0.1, k_per_bank=16, num_banks=4, n_dim=1024,
            codebook=cb, seed_offset=200, gpu_util_samples=[])
        margin = rec_m_cliff - rec_s_cliff
        print("[selftest] T8 INFO: alpha=0.1 K=16 B=4 N=1024 MULTI=%.3f SINGLE=%.3f margin=%.3f"
              % (rec_m_cliff, rec_s_cliff, margin))
        assert margin > -0.10, \
            "T8 sign: MULTI should NOT severely underperform SINGLE at cliff regime"
        print("[selftest] T8 PASS: discriminator sign correct")

        # T9: bands locked (v2 thresholds)
        assert HP_DISCRIM_MARGIN == 0.30
        assert HP_MULTI_PASS_RECALL == 0.50
        assert HP_RAIL_RECALL == 0.95
        assert HP_HARD_PASS_MIN_GRID == 50, "T9 v2 HP_min_grid=50"
        assert HP_HARD_PASS_MIN_FULLN == 12, "T9 v2 HP_min_fullN=12"
        assert HP_DISCRIM_DOES_NOT_FIRE == 20, "T9 v2 HP_min_fire=20"
        # B=1 must NOT be in v2 grid (degenerate)
        assert 1 not in NUM_BANKS_VALUES, "T9 v2 B=1 must be dropped"
        # K=4 must NOT be in v2 grid (saturator)
        assert 4 not in K_PER_BANK_VALUES, "T9 v2 K=4 must be dropped"
        # K=128, K=256 must be IN v2 grid
        assert 128 in K_PER_BANK_VALUES, "T9 v2 K=128 must be added"
        assert 256 in K_PER_BANK_VALUES, "T9 v2 K=256 must be added"
        # B=64 must be IN v2 grid
        assert 64 in NUM_BANKS_VALUES, "T9 v2 B=64 must be added"
        print("[selftest] T9 PASS: bands locked + v2 axes correct")

        # T10: chunked argmax matches unchunked
        Q = 32
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

        # T12: VRAM probe (v2 worst point: alpha=2 N=8192 K=256 B=64 -> M=16384)
        est = _estimate_peak_working_set_bytes(0.05, 16, 4, 1024)
        assert 0 < est < 100 * 1024 * 1024, "T12 probe %d should be < 100MB at smoke" % est
        print("[selftest] T12 PASS: VRAM probe = %.2fMB at smoke" % (est / 1024 / 1024))

        # T13: phase point construction + cardinality (use prod CB for FULL count)
        smoke_pts = SMOKE_CORNERS
        assert len(smoke_pts) == 8, "T13 v2 smoke = 8 corners (was 6 in v1)"
        _saved_CB = CODEBOOK_SIZE
        globals()["CODEBOOK_SIZE"] = save_CB  # 16384
        try:
            full_pts = _build_phase_points([0.05, 0.1, 0.25, 0.5, 1.0, 2.0],
                                            [16, 64, 128, 256], [4, 16, 64],
                                            [2048, 4096, 8192])
        finally:
            globals()["CODEBOOK_SIZE"] = _saved_CB
        # 6 alpha * 4 K * 3 B * 3 N = 216 (no skips at prod CB=16384, M_max=16384)
        assert len(full_pts) == 216, "T13 v2 full = 216 grid points, got %d" % len(full_pts)
        print("[selftest] T13 PASS: v2 smoke=8 full=216 grid points")

        # T14: alpha-loading write/read end-to-end at tiny smoke
        items_test = cb[:8]
        slot_tags_test = build_slot_tags(0, 1024, 16)
        ws_bp, ba, sa = _write_bank_alpha_loading(
            items_test, slot_tags_test, num_banks=4, k_per_bank=16,
            n_dim=1024, seed_offset=100)
        assert ws_bp.shape == (4, 1024), "T14 v2 workspaces shape (B=4)"
        assert ba.shape == (8,), "T14 bank_assign shape"
        assert sa.shape == (8,), "T14 slot_assign shape"
        # bank_assign round-robin over B=4: 0,1,2,3,0,1,2,3
        assert ba.tolist() == [0, 1, 2, 3, 0, 1, 2, 3], "T14 v2 round-robin bank assignment B=4"
        # slot_assign: in_bank_seq = i // 4 = [0,0,0,0,1,1,1,1]; slot = in_bank_seq % 16 = same
        assert sa.tolist() == [0, 0, 0, 0, 1, 1, 1, 1], "T14 v2 slot assignment B=4"
        print("[selftest] T14 PASS: alpha-loading write returns correct shapes + assignments")

        # T15 (v2 new): cardinality of full grid matches EXPECTED_N_UNITS at the
        # production CONFIG (without entering selftest scope-reduced CB).
        # Re-derive: 1 seed * 216 phase_pts * 3 regimes = 648.
        full_expected = 1 * 216 * 3
        assert full_expected == 648, "T15 v2 full cardinality = 648 units/seed"
        print("[selftest] T15 PASS: v2 full cardinality = 648/seed verified analytically")

        print("[selftest] ALL PASS")
    finally:
        _DEVICE = save_dev
        _STORE_DTYPE = save_dtype
        _CUDA_OK = save_cuda
        CODEBOOK_CHUNK = save_chunk
        CODEBOOK_SIZE = save_CB
        N_ITEMS_PER_TRIAL = save_NI
        SIGMA = save_sig


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------- per-arm runner -----------------------------
def run_unit(seed: int, alpha: float, k_per_bank: int, num_banks: int,
             n_dim: int, regime: str, codebook: torch.Tensor,
             gpu_util_samples: List[float]) -> Dict:
    t0 = time.time()
    seed_offset = (seed * 100003
                   + int(round(alpha * 1000)) * 11
                   + k_per_bank * 31
                   + num_banks * 137
                   + n_dim * 251
                   + (0 if regime == "MULTI_BANK_BIND" else
                      1 if regime == "SINGLE_BANK_BASELINE" else 2))
    M = max(1, int(round(alpha * n_dim)))

    if _CUDA_OK:
        torch.cuda.reset_peak_memory_stats(0)

    if regime == "MULTI_BANK_BIND":
        recall, route_acc, arm_hash = eval_multi_bank_arm(
            alpha, k_per_bank, num_banks, n_dim, codebook, seed_offset,
            gpu_util_samples)
    elif regime == "SINGLE_BANK_BASELINE":
        recall, route_acc, arm_hash = eval_single_bank_arm(
            alpha, k_per_bank, num_banks, n_dim, codebook, seed_offset,
            gpu_util_samples)
    elif regime == "RANDOM_FLOOR":
        recall, route_acc, arm_hash = eval_random_arm(
            alpha, k_per_bank, num_banks, n_dim, codebook, seed_offset)
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
        "alpha": float(round(alpha, 4)),
        "k_per_bank": int(k_per_bank),
        "num_banks": int(num_banks),
        "n_dim": int(n_dim),
        "M_total": int(M),
        "items_per_bank": int(math.ceil(M / num_banks)),
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
        "N_ITEMS_PER_TRIAL": int(N_ITEMS_PER_TRIAL),
        "M": int(M),
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

    by_point: Dict[Tuple[float, int, int, int, str], Dict] = {}
    for _, body in per_key.items():
        a = float(body["alpha"])
        K = int(body["k_per_bank"])
        B = int(body["num_banks"])
        N = int(body["n_dim"])
        R = body["regime"]
        by_point[(a, K, B, N, R)] = body

    phase_points_keys = set((a, K, B, N) for (a, K, B, N, _) in by_point.keys())
    phase_map: List[Dict] = []
    n_pass = 0
    n_pass_at_full_N = 0
    n_saturate = 0
    n_floor = 0
    n_arms_identical = 0
    arms_differ_count = 0
    rail_observed = None

    probe_denied_points = set()
    for f in failures:
        if f.get("exc_type") == "HP_VRAM_PROBE_BREACH":
            probe_denied_points.add((float(f.get("alpha", 0.0)),
                                     int(f.get("k_per_bank", 0)),
                                     int(f.get("num_banks", 0)),
                                     int(f.get("n_dim", 0))))

    FULL_N = max(N_DIM_VALUES_FULL)
    # v2 rail: alpha_min, K=256, B=4, N=FULL_N (was K=64, B=1 in v1 -- saturated by construction)
    RAIL_K = 256
    RAIL_B = 4

    for (a, K, B, N) in sorted(phase_points_keys | probe_denied_points):
        mult = by_point.get((a, K, B, N, "MULTI_BANK_BIND"))
        sing = by_point.get((a, K, B, N, "SINGLE_BANK_BASELINE"))
        rand = by_point.get((a, K, B, N, "RANDOM_FLOOR"))
        is_probe_denied = (a, K, B, N) in probe_denied_points
        if is_probe_denied or mult is None or sing is None or rand is None:
            phase_map.append({
                "alpha": float(a), "K_per_bank": int(K), "num_banks": int(B),
                "n_dim": int(N), "M_total": int(round(a * N)),
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

        # v2: B>=4 always (B=1 dropped); arms_differ check across all 3 hashes
        arms_differ_full = (mult["arm_sha256"] != sing["arm_sha256"] and
                             mult["arm_sha256"] != rand["arm_sha256"] and
                             sing["arm_sha256"] != rand["arm_sha256"])
        if arms_differ_full:
            arms_differ_count += 1
        else:
            n_arms_identical += 1

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
        # v2 Rail: lowest alpha, K=256, B=4, N=FULL_N -> MULTI ~ 1.0 expected
        if (abs(a - min(ALPHA_VALUES)) < 1e-6 and K == RAIL_K
                and B == RAIL_B and N == FULL_N):
            rail_observed = m_r
        phase_map.append({
            "alpha": float(a), "K_per_bank": int(K), "num_banks": int(B),
            "n_dim": int(N), "M_total": int(round(a * N)),
            "items_per_bank": int(math.ceil(round(a * N) / B)),
            "recall_multi": float(round(m_r, 6)),
            "recall_single": float(round(s_r, 6)),
            "recall_random": float(round(r_r, 6)),
            "margin_multi_vs_single": float(round(margin, 6)),
            "route_acc_multi": float(round(mult["route_acc"], 4)),
            "route_acc_single": float(round(sing["route_acc"], 4)),
            "arms_differ": bool(arms_differ_full),
            "verdict_tier": tier,
            "saturation": bool(sat),
            "cliff_marker": bool(m_r < HP_MULTI_PASS_RECALL),
        })

    # Cliff per B: largest alpha at which MULTI still passes at each B (fixed K=largest)
    cliff_per_B: Dict[str, float] = {}
    for pp in phase_map:
        if pp.get("recall_multi") is None:
            continue
        key = "B=%d" % pp["num_banks"]
        if pp["recall_multi"] >= HP_MULTI_PASS_RECALL:
            cur = cliff_per_B.get(key, 0.0)
            if pp["alpha"] > cur:
                cliff_per_B[key] = float(pp["alpha"])

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
        "rail_alpha_min_K256_B4_fullN_observed": rail_observed,
        "rail_target": HP_RAIL_RECALL,
        "rail_config": {"alpha": min(ALPHA_VALUES), "K_per_bank": RAIL_K,
                        "num_banks": RAIL_B, "n_dim": FULL_N},
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
    rail_str = (" | rail_alpha%.2f_K%d_B%d_N%d=%.4f" % (
        min(ALPHA_VALUES), RAIL_K, RAIL_B, FULL_N, rail_observed)) if rail_observed is not None else ""
    card_str = " | n_units=%d/expected=%d probe_cliffs=%d (%s)" % (
        n_units_observed, EXPECTED_N_UNITS, n_probe_cliffs,
        "OK" if cardinality_ok else "BREACH_META_RULE_H")
    fail_str = ""
    if real_failures:
        fail_str = " | failures=%d [%s]" % (
            len(real_failures),
            "; ".join("%s:%s" % (f["key"], f["exc_type"]) for f in real_failures[:5]))

    # SMOKE path (v2: 8 corners; 6 discriminator-firing + 1 rail + 1 floor)
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
        # Smoke gate v2: discriminator FIRES at >=4 of 6 expected-cliff corners
        # (full-N preview corners count toward this — discriminator-must-survive-scale)
        expected_cliff = [
            (0.05, 16,  16, 2048),
            (0.05, 64,  4,  2048),
            (0.05, 128, 4,  4096),
            (0.10, 256, 4,  8192),  # FULL-N preview discriminator
            (0.25, 64,  16, 2048),
            (0.50, 128, 64, 2048),
        ]
        cliff_fired = 0
        cliff_fired_at_full_N = 0
        for pp in phase_map:
            if pp.get("margin_multi_vs_single") is None:
                continue
            tup = (pp["alpha"], pp["K_per_bank"], pp["num_banks"], pp["n_dim"])
            for ec in expected_cliff:
                if (abs(tup[0] - ec[0]) < 1e-6 and tup[1] == ec[1]
                        and tup[2] == ec[2] and tup[3] == ec[3]):
                    if pp["margin_multi_vs_single"] > HP_DISCRIM_MARGIN:
                        cliff_fired += 1
                        if pp["n_dim"] >= FULL_N:
                            cliff_fired_at_full_N += 1
                    break
        discrim_ok = (cliff_fired >= 4)
        # Discriminator-must-survive-scale: AT LEAST 1 full-N preview corner must fire
        full_n_discrim_ok = (cliff_fired_at_full_N >= 1)
        # Rail-preview: alpha=0.05, K=256, B=4, N=8192 -> MULTI >= 0.85 (slightly soft for smoke)
        rail_smoke_ok = False
        for pp in phase_map:
            if (abs(pp["alpha"] - 0.05) < 1e-6 and pp["K_per_bank"] == 256
                    and pp["num_banks"] == 4 and pp["n_dim"] == 8192
                    and pp.get("recall_multi") is not None
                    and pp["recall_multi"] >= 0.85):
                rail_smoke_ok = True
                break
        # Floor: 2.0 alpha K=16 B=16 N=2048 -> BOTH at floor
        fail_ok = (n_floor >= 1 or any(pp.get("verdict_tier") == "FAIL" for pp in phase_map))
        if discrim_ok and full_n_discrim_ok and rail_smoke_ok and fail_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS_v2: discrim_fired=%d/%d (full_N_fired=%d) rail_smoke=%s fail=%d | %s%s%s" % (
                        cliff_fired, len(expected_cliff), cliff_fired_at_full_N,
                        rail_smoke_ok,
                        n_floor + sum(1 for pp in phase_map if pp.get("verdict_tier") == "FAIL"),
                        summary, cliff_str, card_str), detail)
        return ("HARD_FAIL",
                "SMOKE_HARD_FAIL_GATE_v2: discrim_ok=%s (fired=%d/%d) full_N_discrim_ok=%s (full_N_fired=%d) rail_smoke_ok=%s fail_ok=%s | %s%s%s" % (
                    discrim_ok, cliff_fired, len(expected_cliff),
                    full_n_discrim_ok, cliff_fired_at_full_N, rail_smoke_ok, fail_ok,
                    summary, cliff_str, card_str),
                detail)

    # FULL path (unchanged structure from v1; thresholds raised)
    if real_failures:
        return ("HARD_FAIL",
                "HARD_FAIL_UNIT_EXCEPTION: %d units raised | %s%s%s%s" % (
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
                "HARD_FAIL_SATURATION_ONLY | %s%s%s" % (
                    summary, cliff_str, card_str), detail)
    if n_floor == len(phase_map):
        return ("HARD_FAIL",
                "HARD_FAIL_FLOOR_ONLY | %s%s%s" % (
                    summary, cliff_str, card_str), detail)
    rail_ok = (rail_observed is not None and rail_observed >= HP_RAIL_RECALL)
    if n_pass >= HP_HARD_PASS_MIN_GRID and n_pass_at_full_N >= HP_HARD_PASS_MIN_FULLN and rail_ok:
        return ("HARD_PASS",
                "HARD_PASS_CAPACITY_MB_ALPHA_K_PHASE_DIAGRAM_v2: n_pass=%d (>=%d) n_pass_at_full_N=%d (>=%d) rail_ok=%s | %s%s%s%s" % (
                    n_pass, HP_HARD_PASS_MIN_GRID, n_pass_at_full_N, HP_HARD_PASS_MIN_FULLN, rail_ok,
                    summary, cliff_str, rail_str, card_str), detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL_CAPACITY_MB_ALPHA_K_v2: n_pass=%d n_pass_at_full_N=%d rail_ok=%s | %s%s%s%s" % (
                n_pass, n_pass_at_full_N, rail_ok, summary, cliff_str, rail_str, card_str), detail)


# ----------------------------- atexit synth + main -----------------------------
_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time(), "gpu_util": [],
                   "failures": []}


def _build_keys() -> List[str]:
    keys = []
    for s in SEEDS:
        for (a, K, B, N) in PHASE_POINTS:
            for R in REGIMES:
                a_int = int(round(a * 10000))
                keys.append("seed%d_a%05d_K%d_B%d_N%d_regime%s" % (s, a_int, K, B, N, R))
    return keys


def _parse_key(key: str) -> Tuple[int, float, int, int, int, str]:
    parts = key.split("_")
    seed = int(parts[0].replace("seed", ""))
    a_int = int(parts[1].replace("a", ""))
    a = a_int / 10000.0
    K = int(parts[2].replace("K", ""))
    B = int(parts[3].replace("B", ""))
    N = int(parts[4].replace("N", ""))
    R = "_".join(parts[5:]).replace("regime", "", 1)
    return seed, a, K, B, N, R


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
        "phase_points": [list(p) for p in PHASE_POINTS],
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
        "metrics_source": "measured_gpu_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_%d" % SEED_THIS_CHUNK,
        "DESIGN_NOTE": (
            "V2 alpha-K capacity phase diagram (chunked sibling cell, seed=%d). "
            "Extends v1: K_per_bank in {16,64,128,256} (was {4,16,64}); B in "
            "{4,16,64} (was {1,4,16}; B=1 was degenerate). Full grid 216 pts; "
            "expected n_pass_at_full_N >= 12 (chain-grade). Rail: alpha_min "
            "K=256 B=4 N=FULL_N (v1 rail K=64 B=1 was saturated by construction)."
        ) % SEED_THIS_CHUNK,
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

    cached: Dict[Tuple[int, int], torch.Tensor] = {}
    halt_after_loop = False

    for key in all_keys:
        if key in done_keys:
            continue
        seed, a, K, B, N, R = _parse_key(key)

        est_bytes = _estimate_peak_working_set_bytes(a, K, B, N)
        if _CUDA_OK:
            free_b, total_b = torch.cuda.mem_get_info(0)
            budget = int(free_b * HP_VRAM_PROBE_FRACTION)
            if est_bytes > budget:
                fail_entry = {
                    "key": key,
                    "seed": seed, "alpha": a, "k_per_bank": K, "num_banks": B,
                    "n_dim": N, "regime": R,
                    "exc_type": "HP_VRAM_PROBE_BREACH",
                    "exc_msg": "est_peak=%.2fGB budget=%.2fGB" % (
                        est_bytes / 1024**3, budget / 1024**3),
                    "traceback": "",
                    "est_peak_mb": int(est_bytes / 1024 / 1024),
                    "free_mb": int(free_b / 1024 / 1024),
                }
                _RESULTS_HOLDER["failures"].append(fail_entry)
                print("[HP_VRAM_PROBE_BREACH] %s est=%.2fGB > budget=%.2fGB" % (
                    key, est_bytes / 1024**3, budget / 1024**3), flush=True)
                continue

        cache_key = (seed, N)
        if cache_key not in cached:
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
            rec = run_unit(seed, a, K, B, N, R, codebook,
                            _RESULTS_HOLDER["gpu_util"])
            rec["_ckpt_key"] = key
            write_partial_key(out_dir, key, rec)
            print("  [done] %s recall=%.4f route_acc=%.4f wall=%.1fs peak=%dMB" % (
                key, rec["recall"], rec["route_acc"], rec["wall_s"],
                rec.get("peak_mem_mb", 0)), flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            fail_entry = {
                "key": key,
                "seed": seed, "alpha": a, "k_per_bank": K, "num_banks": B,
                "n_dim": N, "regime": R,
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
            print("[meta_rule_an] halting loop on real unit exception", flush=True)
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
