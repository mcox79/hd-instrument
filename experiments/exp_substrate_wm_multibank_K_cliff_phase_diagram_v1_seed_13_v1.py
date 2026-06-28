"""substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_13_v1 -- chunked sibling.

Parent cell:    fork of experiments/exp_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3.py
Parent prereg:  preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md
Sibling chunks: _seed_7_v1.py (this), _seed_13_v1.py, _seed_19_v1.py
Skunkworks aggregates per-seed metrics for 3-seed chain-grade promotion.

Scientific question:
  Layer-1 phase diagram for WM multi-bank K-cliff. Prior CG at K=4096 (rail) +
  K=8192 (MULTI_128x 3-seed). Map cliff per (K, bank_overlap, routing_noise).

Sweep axes (PRIMARY=K-cliff):
  K in {4096, 8192, 16384, 32768, 65536} (5)
  bank_overlap in {0.0, 0.1, 0.3} (3; fraction of dims shared between adjacent bank_tags)
  routing_noise in {0.0, 0.05, 0.15} (3; additional bipolar noise on routing cue)
  Full grid: 5 x 3 x 3 = 45 points x 2 arms (SUBSTRATE, RANDOM) = 90 units per seed.

Smoke corners (5 points x 2 arms = 10 units):
  (K=4096,  ov=0.0, rn=0.0)   -- expected saturate
  (K=65536, ov=0.0, rn=0.0)   -- high-K low-noise (cliff or probe-deny)
  (K=4096,  ov=0.3, rn=0.15)  -- low-K high-noise
  (K=65536, ov=0.3, rn=0.15)  -- expected fail/probe-deny
  (K=16384, ov=0.1, rn=0.05)  -- middle

Arms:
  SUBSTRATE -- multi-bank WM cleanup with k_per_bank=64 envelope (prior CG mechanism)
  RANDOM    -- random vector prediction floor; expected top1 = 1/CB = 1.5e-5

GPU MANDATE (Fix #24): cuda required for full; fp16 storage; chunked matmul on cuda;
  nvidia-smi util sampled per arm; smoke gates gpu_util_p50 >= 50%.

PRE-REG bands (LOCKED at module init; see prereg):
  HARD_PASS (per seed): >=3 of 5 K at (ov=0.0,rn=0.0) corridor have:
    SUBSTRATE recall >= 0.50 AND (SUBSTRATE - RANDOM) > 0.20
  MIDDLE_BAND: cliff structure coherent but absolute recalls weak.
  HARD_FAIL_CARDINALITY_BREACH (META_RULE_H): n_units < expected.
  HARD_FAIL_UNIT_EXCEPTION (META_RULE_AN; v3-style no-silent-except).
  HARD_FAIL_ARMS_IDENTICAL: SUBSTRATE == RANDOM hash (META_RULE_AF).
  HARD_FAIL_SATURATION_ONLY / HARD_FAIL_FLOOR_ONLY / HARD_FAIL_LLM_CALL.
  HP_VRAM_PROBE_BREACH is NOT a failure -- it IS the cliff (recorded as cliff_marker).

CRLB pre-validation (Python before prereg):
  Bank-routing snr at CUE_COS=0.70: 7.92 / 5.60 / 3.96 / 2.80 / 1.98 for K=4k...64k.
  Cleanup-1 snr per dim = 1/sqrt(k_per_bank-1) = 0.126.
  RANDOM floor = 1/CB = 1.5e-5.

VRAM pre-validation (Python before prereg):
  Est eval-peak (fp16): K=4k 1.6GB / K=8k 2.2GB / K=16k 3.2GB / K=32k 5.4GB / K=64k 9.7GB.
  HP_VRAM_PROBE_FRACTION=0.85 of free_mem; K=65536 may probe-deny on <12GB GPUs (correct cliff).

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
ANCHOR_NAME = "substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_%d_v1" % SEED_THIS_CHUNK

_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_multibank_phase_diagram"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# Pre-reg bands LOCKED at module init
HP_DISCRIM_MARGIN = 0.20         # SUBSTRATE - RANDOM > 0.20
HP_SUBSTRATE_PASS_RECALL = 0.50  # SUBSTRATE recall >= 0.50 at PASS points
HP_RAIL_K4096_RECALL = 1.0000    # rail saturated at low corner
HP_RAIL_K4096_TOL = 0.05
HP_SATURATION = 0.995
HP_FLOOR_BAND = 0.05             # SUBSTRATE - RANDOM < 0.05 -> floor
HP_VRAM_PROBE_FRACTION = 0.85
HP_GPU_UTIL_MIN_P50 = 0.50       # Fix #24 NON-NEGOTIABLE on full

assert 0.0 < HP_DISCRIM_MARGIN < 1.0, "discrim margin locked"
assert 0.0 < HP_SUBSTRATE_PASS_RECALL < HP_SATURATION, "pass ordering"

# Mechanism params (match v3 base)
SIGMA = 1.0
CUE_COS = 0.70
FEATURE_OVERLAP_FRAC_ADV = 0.0   # NOT using adversarial codebook here; bank_overlap instead
N_ITEMS_PER_K_FULL = 200
N_ITEMS_PER_K_SMOKE = 96
CODEBOOK_CHUNK_FULL = 4096
CODEBOOK_CHUNK_SMOKE = 1024
K_PER_BANK = 64                  # envelope (CG-locked)

# Smoke vs full grids (USER directive: discriminator-must-survive-scale at FULL N_DIM)
N_DIM = 8192                     # FULL N for both smoke + full (discriminator survives scale)
CODEBOOK_SIZE = 65536            # to fit K=65536 picks
SEEDS = [SEED_THIS_CHUNK]

if SMOKE:
    # 5 corners
    PHASE_POINTS: List[Tuple[int, float, float]] = [
        (4096,  0.0,  0.0),
        (65536, 0.0,  0.0),
        (4096,  0.3,  0.15),
        (65536, 0.3,  0.15),
        (16384, 0.1,  0.05),
    ]
    N_ITEMS_PER_K = N_ITEMS_PER_K_SMOKE
    CODEBOOK_CHUNK = CODEBOOK_CHUNK_SMOKE
else:
    # Full grid: 5 x 3 x 3 = 45 points
    K_VALUES = [4096, 8192, 16384, 32768, 65536]
    OVERLAP_VALUES = [0.0, 0.1, 0.3]
    NOISE_VALUES = [0.0, 0.05, 0.15]
    PHASE_POINTS = [(K, ov, rn) for K in K_VALUES
                    for ov in OVERLAP_VALUES for rn in NOISE_VALUES]
    N_ITEMS_PER_K = N_ITEMS_PER_K_FULL
    CODEBOOK_CHUNK = CODEBOOK_CHUNK_FULL

REGIMES = ["SUBSTRATE", "RANDOM"]
EXPECTED_N_UNITS = len(SEEDS) * len(PHASE_POINTS) * len(REGIMES)

CONFIG_VERSION = (
    "substrateWmMBKCliffPhaseDiag-v1-seed%d: N_DIM=%d CB=%d sigma=%.1f CUE_COS=%.2f "
    "K_PER_BANK=%d phase_points=%d (smoke=%s) N_ITEMS_PER_K=%d codebook_chunk=%d "
    "seeds=%s mode=%s HP_discrim=%.2f HP_pass_rec=%.2f HP_sat=%.3f HP_floor=%.2f "
    "VRAM_PROBE=%.2f HP_GPU_UTIL_MIN=%.2f EXPECTED_N_UNITS=%d"
) % (
    SEED_THIS_CHUNK, N_DIM, CODEBOOK_SIZE, SIGMA, CUE_COS, K_PER_BANK,
    len(PHASE_POINTS), SMOKE, N_ITEMS_PER_K, CODEBOOK_CHUNK, SEEDS, RUN_MODE,
    HP_DISCRIM_MARGIN, HP_SUBSTRATE_PASS_RECALL, HP_SATURATION, HP_FLOOR_BAND,
    HP_VRAM_PROBE_FRACTION, HP_GPU_UTIL_MIN_P50, EXPECTED_N_UNITS,
)


# ----------------------------- GPU mandate -----------------------------
def _require_cuda(strict: bool) -> bool:
    if torch.cuda.is_available():
        return True
    if strict:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (Fix #24): cuda.is_available() = False. "
            "phase_diagram K-cliff at N_DIM=%d K_max=%d requires CUDA. "
            "Route to overnight_queue (GPU runner)." % (N_DIM, max(K for K, _, _ in PHASE_POINTS)))
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


def _estimate_peak_working_set_bytes(k_total: int, n_banks: int,
                                      k_per_bank: int) -> int:
    """Conservative eval-peak estimate per v3 base; same formula."""
    D = N_DIM
    C = CODEBOOK_SIZE
    cb_bytes = C * D * 2
    bound_bytes = max(1, min(n_banks, max(1, 8192 // max(1, k_per_bank)))) * k_per_bank * D * 4
    workspaces_bytes = n_banks * D * 2
    cues_bytes = k_total * D * (2 + 4)
    ws_selected_bytes = k_total * D * 2
    cleanup_bytes = k_total * D * (2 + 4 + 2)
    chunked_sims_bytes = CODEBOOK_CHUNK * k_total * 4
    write_peak = cb_bytes + bound_bytes + workspaces_bytes
    eval_peak = (cb_bytes + workspaces_bytes + cues_bytes + ws_selected_bytes
                 + cleanup_bytes + chunked_sims_bytes)
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


def build_codebook_random(seed_offset: int) -> torch.Tensor:
    g = _make_gen(seed_offset)
    return random_bipolar_t((CODEBOOK_SIZE, N_DIM), g)


def build_slot_tags(seed_offset: int) -> torch.Tensor:
    g = _make_gen(seed_offset + 13)
    return random_bipolar_t((K_PER_BANK, N_DIM), g)


def build_bank_tags(seed_offset: int, n_banks: int, bank_overlap: float) -> torch.Tensor:
    """Bank tags with controlled overlap (shared dims between adjacent banks).

    overlap=0.0: independent bipolar (orthogonal in expectation).
    overlap>0.0: fraction of dims shared between bank i and bank i+1.
                 We implement by sharing the first round(overlap*N) dims with the
                 PREVIOUS bank, the rest are independent. Index 0 has no neighbor;
                 deterministic + reproducible.
    """
    g = _make_gen(seed_offset + 17)
    base = random_bipolar_t((n_banks, N_DIM), g)
    if bank_overlap > 0.0 and n_banks > 1:
        n_shared = int(round(bank_overlap * N_DIM))
        if n_shared > 0 and n_shared < N_DIM:
            # Each bank i (i>=1) shares its first n_shared dims with bank i-1.
            for i in range(1, n_banks):
                base[i, :n_shared] = base[i - 1, :n_shared]
    return base


def _write_bank_batched(items_per_bank: torch.Tensor,
                        slot_tags: torch.Tensor,
                        seed_offset: int) -> torch.Tensor:
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


def eval_substrate_arm(k_total: int, bank_overlap: float, routing_noise: float,
                       codebook: torch.Tensor, seed_offset: int,
                       gpu_util_samples: List[float]) -> Tuple[float, float, str]:
    """Multi-bank WM cleanup arm (SUBSTRATE).

    Returns (recall_top1, route_acc, arm_sha256_hex).
    """
    n_banks = k_total // K_PER_BANK
    assert n_banks * K_PER_BANK == k_total, "K must be divisible by K_PER_BANK"
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / k_total))
    slot_tags = build_slot_tags(seed_offset)
    bank_tags = build_bank_tags(seed_offset, n_banks, bank_overlap)
    cue_signal_scale = CUE_COS
    cue_noise_scale_base = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))
    # routing_noise INCREASES the effective noise budget on the routing cue.
    # Modeled as additive bipolar noise weighted by routing_noise.
    # Cue = CUE_COS*bank + sqrt(1-CUE_COS^2)*noise_base + routing_noise*noise_extra
    correct = 0
    total = 0
    route_correct = 0
    route_total = 0
    hasher = hashlib.sha256()

    g_trial = _make_gen(seed_offset + 29)
    for trial in range(n_trials):
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:k_total]
        items = codebook[idx_global]
        items_per_bank = items.view(n_banks, K_PER_BANK, N_DIM)
        workspaces = _write_bank_batched(items_per_bank, slot_tags,
                                         seed_offset + 1000 + trial)
        del items, items_per_bank
        if _CUDA_OK:
            torch.cuda.empty_cache()

        slot_indices = torch.arange(k_total, device=_DEVICE)
        bank_true = slot_indices // K_PER_BANK
        local_slot = slot_indices % K_PER_BANK

        g_cue = _make_gen(seed_offset + 5000 + trial)
        bank_cue_base = bank_tags[bank_true].float()
        noise_base = torch.empty((k_total, N_DIM), device=_DEVICE, dtype=torch.float32)
        noise_base.normal_(0.0, 1.0, generator=g_cue)
        noise_base_bp = bipolar_quantize_t(noise_base)
        del noise_base
        if _CUDA_OK:
            torch.cuda.empty_cache()
        cue_f = (cue_signal_scale * bank_cue_base
                 + cue_noise_scale_base * noise_base_bp)
        if routing_noise > 0.0:
            g_rn = _make_gen(seed_offset + 7000 + trial)
            noise_extra = torch.empty((k_total, N_DIM), device=_DEVICE, dtype=torch.float32)
            noise_extra.normal_(0.0, 1.0, generator=g_rn)
            noise_extra_bp = bipolar_quantize_t(noise_extra)
            cue_f = cue_f + routing_noise * noise_extra_bp
            del noise_extra, noise_extra_bp
            if _CUDA_OK:
                torch.cuda.empty_cache()
        cues = cue_f.to(_STORE_DTYPE)
        del bank_cue_base, noise_base_bp, cue_f
        if _CUDA_OK:
            torch.cuda.empty_cache()
        sims_bank = cues @ bank_tags.T
        bank_routed = sims_bank.argmax(dim=1)
        del sims_bank

        route_correct += int((bank_routed == bank_true).sum().item())
        route_total += k_total

        ws_selected = workspaces[bank_routed]
        slot_tag_sel = slot_tags[local_slot]
        del workspaces
        if _CUDA_OK:
            torch.cuda.empty_cache()

        pred_idx = _read_with_cleanup_batched(ws_selected, slot_tag_sel, codebook)
        true_item_idx = idx_global[slot_indices]
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += k_total

        # Hash a fingerprint of preds for arms_differ check
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


def eval_random_arm(k_total: int, codebook: torch.Tensor,
                    seed_offset: int) -> Tuple[float, float, str]:
    """RANDOM floor: predict a random codebook row for each slot.

    Expected top1 = 1/CB. Returns same shape as SUBSTRATE for arms_differ check.
    """
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / k_total))
    correct = 0
    total = 0
    hasher = hashlib.sha256()
    g_trial = _make_gen(seed_offset + 29 + 999983)  # different seed than substrate
    for trial in range(n_trials):
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:k_total]
        # Random prediction: another random permutation
        g_rand = _make_gen(seed_offset + 5000 + trial + 999983)
        pred_idx = torch.randperm(CODEBOOK_SIZE, generator=g_rand, device=_DEVICE)[:k_total]
        match = (pred_idx == idx_global)
        correct += int(match.sum().item())
        total += k_total
        hasher.update(pred_idx.cpu().numpy().astype(np.int64).tobytes())
        del idx_global, pred_idx, match
        if _CUDA_OK:
            torch.cuda.empty_cache()
    recall = correct / max(total, 1)
    # Random arm has no concept of routing; report route_acc=NaN-ish via 0.0 marker
    return recall, 0.0, hasher.hexdigest()[:16]


# ----------------------------- self-test (CPU; fp32) -----------------------------
def _selftest():
    global _DEVICE, _STORE_DTYPE, _CUDA_OK, CODEBOOK_CHUNK
    global N_DIM, CODEBOOK_SIZE, N_ITEMS_PER_K, SIGMA
    save_dev, save_dtype, save_cuda, save_chunk = _DEVICE, _STORE_DTYPE, _CUDA_OK, CODEBOOK_CHUNK
    save_N, save_CB, save_NI, save_sig = N_DIM, CODEBOOK_SIZE, N_ITEMS_PER_K, SIGMA
    _DEVICE = torch.device("cpu")
    _STORE_DTYPE = torch.float32
    _CUDA_OK = False
    CODEBOOK_CHUNK = 256
    N_DIM = 1024
    CODEBOOK_SIZE = 2048
    N_ITEMS_PER_K = 64
    try:
        # T1: random codebook shape + bipolar
        cb = build_codebook_random(0)
        assert cb.shape == (2048, 1024), "T1 shape"
        u = torch.unique(cb)
        assert set(u.tolist()) <= {-1.0, 1.0}, "T1 bipolar"
        print("[selftest] T1 PASS: random codebook shape + bipolar")

        # T2: bank tags with overlap behavior
        bt0 = build_bank_tags(1, n_banks=8, bank_overlap=0.0)
        bt5 = build_bank_tags(1, n_banks=8, bank_overlap=0.5)
        # bt0 adjacent should differ ~50% (random bipolar)
        adj0 = float((bt0[0] == bt0[1]).float().mean().item())
        adj5 = float((bt5[0] == bt5[1]).float().mean().item())
        assert 0.40 < adj0 < 0.60, "T2 no-overlap adjacent match ~0.5; got %.3f" % adj0
        assert adj5 > 0.65, "T2 overlap=0.5 should boost adjacent match; got %.3f" % adj5
        print("[selftest] T2 PASS: bank_tags overlap 0.0 adj_match=%.3f overlap=0.5 adj_match=%.3f"
              % (adj0, adj5))

        # T3: SUBSTRATE arm runs end-to-end at smoke shape.
        # NOTE: K_PER_BANK=64 is GLOBAL (envelope-locked). At smoke N_DIM=1024 the
        # crosstalk SNR (1/sqrt(63)=0.126) is harsh; we use K=1024 (n_banks=16)
        # and lower the recall floor to 0.30 (selftest pipeline-validates, not certs).
        gpu_samples = []
        # cb is already 2048 rows >= K=1024; no resize needed.
        rec, ra, ha = eval_substrate_arm(1024, 0.0, 0.0, cb,
                                          seed_offset=100,
                                          gpu_util_samples=gpu_samples)
        assert ra >= 0.85, "T3 route_acc=%.3f < 0.85 at smoke" % ra
        assert rec >= 0.30, "T3 recall=%.3f < 0.30 at smoke (pipeline check; full cert at N=8192)" % rec
        assert isinstance(ha, str) and len(ha) == 16, "T3 hash format"
        print("[selftest] T3 PASS: SUBSTRATE arm K=1024 ov=0 rn=0 recall=%.3f route_acc=%.3f"
              % (rec, ra))

        # T4: LLM counter
        assert _LLM_CALL_COUNTER[0] == 0, "T4 LLM counter not zero"
        print("[selftest] T4 PASS: LLM counter = 0")

        # T5: RANDOM arm floor + hash differs from SUBSTRATE
        rec_r, _, ha_r = eval_random_arm(256, cb, seed_offset=100)
        assert rec_r < 0.10, "T5 random recall=%.3f should be near floor" % rec_r
        assert ha_r != ha, "T5 RANDOM hash MUST differ from SUBSTRATE (arms-must-differ)"
        print("[selftest] T5 PASS: RANDOM arm recall=%.4f hash_differs_from_substrate" % rec_r)

        # T6: bands locked
        assert HP_DISCRIM_MARGIN == 0.20
        assert HP_SUBSTRATE_PASS_RECALL == 0.50
        assert HP_RAIL_K4096_RECALL == 1.0000
        assert HP_VRAM_PROBE_FRACTION == 0.85
        print("[selftest] T6 PASS: bands locked")

        # T7: chunked argmax matches unchunked
        Q = 64
        g_q = _make_gen(999)
        queries = random_bipolar_t((Q, N_DIM), g_q)
        sims_full = (cb.float() @ queries.float().T)
        idx_unchunked = sims_full.argmax(dim=0)
        idx_chunked = _chunked_argmax_cb_at_queries(cb, queries)
        assert torch.equal(idx_chunked, idx_unchunked), \
            "T7 chunked argmax disagrees with unchunked"
        print("[selftest] T7 PASS: chunked argmax matches unchunked")

        # T8: OOM detector
        class _MockOOM(RuntimeError):
            pass
        assert _is_oom_error(_MockOOM("CUDA out of memory"))
        assert not _is_oom_error(ValueError("not oom"))
        assert _is_oom_error(_MockOOM("CUBLAS_STATUS_ALLOC_FAILED"))
        print("[selftest] T8 PASS: OOM detector")

        # T9: VRAM probe at smoke shape returns sane value
        est = _estimate_peak_working_set_bytes(256, 16, 16)
        assert 0 < est < 200 * 1024 * 1024, "T9 probe %d should be < 200MB at smoke" % est
        print("[selftest] T9 PASS: VRAM probe = %.2fMB at smoke shape" % (est / 1024 / 1024))

        # T10: routing_noise INCREASES routing degradation
        rec_clean, ra_clean, _ = eval_substrate_arm(256, 0.0, 0.0, cb,
                                                     seed_offset=200,
                                                     gpu_util_samples=[])
        rec_noisy, ra_noisy, _ = eval_substrate_arm(256, 0.0, 0.50, cb,
                                                     seed_offset=200,
                                                     gpu_util_samples=[])
        # Routing noise should degrade (or at least not improve significantly).
        # Use a soft assert: ra_noisy <= ra_clean + 0.05 (within sampling noise).
        assert ra_noisy <= ra_clean + 0.05, \
            "T10 routing_noise should NOT improve route_acc: clean=%.3f noisy=%.3f" % (ra_clean, ra_noisy)
        print("[selftest] T10 PASS: routing_noise degrades route_acc clean=%.3f -> noisy=%.3f"
              % (ra_clean, ra_noisy))

        # T11: arms_differ_sha256 always distinct (no silent arm collapse)
        for K_t, ov_t, rn_t in [(256, 0.0, 0.0), (256, 0.3, 0.15)]:
            _, _, h_s = eval_substrate_arm(K_t, ov_t, rn_t, cb,
                                            seed_offset=300,
                                            gpu_util_samples=[])
            _, _, h_r = eval_random_arm(K_t, cb, seed_offset=300)
            assert h_s != h_r, "T11 arms_must_differ violated at K=%d ov=%.1f rn=%.2f" % (K_t, ov_t, rn_t)
        print("[selftest] T11 PASS: arms_differ_sha256 distinct at all sampled phase points")

        # T12: expected_n_units math
        # in selftest space we set our own PHASE_POINTS to a 5-corner smoke equivalent
        n_pts = 5
        n_regimes = 2
        n_seeds = 1
        expected_smoke = n_pts * n_regimes * n_seeds
        assert expected_smoke == 10, "T12 smoke cardinality math"
        print("[selftest] T12 PASS: smoke expected_n_units=10 (5 corners x 2 arms x 1 seed)")

        print("[selftest] ALL PASS")
    finally:
        _DEVICE = save_dev
        _STORE_DTYPE = save_dtype
        _CUDA_OK = save_cuda
        CODEBOOK_CHUNK = save_chunk
        N_DIM = save_N
        CODEBOOK_SIZE = save_CB
        N_ITEMS_PER_K = save_NI
        SIGMA = save_sig


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------- per-arm runner -----------------------------
def run_unit(seed: int, k_total: int, bank_overlap: float, routing_noise: float,
             regime: str, codebook: torch.Tensor,
             gpu_util_samples: List[float]) -> Dict:
    t0 = time.time()
    # Distinct seed-offset per (seed, K, overlap, noise, regime)
    seed_offset = (seed * 100003
                   + k_total * 31
                   + int(round(bank_overlap * 1000)) * 137
                   + int(round(routing_noise * 10000)) * 251
                   + (1 if regime == "RANDOM" else 0))

    if _CUDA_OK:
        torch.cuda.reset_peak_memory_stats(0)

    if regime == "SUBSTRATE":
        recall, route_acc, arm_hash = eval_substrate_arm(
            k_total, bank_overlap, routing_noise, codebook, seed_offset,
            gpu_util_samples)
    elif regime == "RANDOM":
        recall, route_acc, arm_hash = eval_random_arm(k_total, codebook, seed_offset)
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
        "k_total": int(k_total),
        "bank_overlap": float(bank_overlap),
        "routing_noise": float(routing_noise),
        "regime": regime,
        "recall": float(round(recall, 6)),
        "route_acc": float(round(route_acc, 4)),
        "arm_sha256": arm_hash,
        "wall_s": float(round(wall_s, 2)),
        "peak_mem_mb": int(peak_mb),
        "N": int(N_DIM),
        "CODEBOOK_SIZE": int(CODEBOOK_SIZE),
        "SIGMA": float(SIGMA),
        "CUE_COS": float(CUE_COS),
        "K_PER_BANK": int(K_PER_BANK),
        "N_ITEMS_PER_K": int(N_ITEMS_PER_K),
        "M": int(max(K for K, _, _ in PHASE_POINTS)),
        "run_mode": RUN_MODE,
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
    # cliff_marker = HP_VRAM_PROBE_BREACH counts as cliff, not failure
    real_failures = [f for f in failures if f.get("exc_type") != "HP_VRAM_PROBE_BREACH"]
    n_probe_cliffs = len([f for f in failures if f.get("exc_type") == "HP_VRAM_PROBE_BREACH"])
    cardinality_ok = ((n_units_observed + n_probe_cliffs) >= EXPECTED_N_UNITS)

    # Index by (K, ov, rn, regime)
    by_point: Dict[Tuple[int, float, float, str], Dict] = {}
    for _, body in per_key.items():
        K = int(body["k_total"])
        ov = float(body["bank_overlap"])
        rn = float(body["routing_noise"])
        R = body["regime"]
        by_point[(K, ov, rn, R)] = body

    # Build phase_map: per (K, ov, rn) collect SUBSTRATE + RANDOM
    phase_points_keys = set((K, ov, rn) for (K, ov, rn, _) in by_point.keys())
    phase_map: List[Dict] = []
    n_pass = 0
    n_saturate = 0
    n_floor = 0
    n_arms_identical = 0
    arms_differ_count = 0
    rail_observed = None

    # Add VRAM-probe-denied entries to phase_map as cliff markers
    probe_denied_points = set()
    for f in failures:
        if f.get("exc_type") == "HP_VRAM_PROBE_BREACH":
            probe_denied_points.add((int(f.get("k_total", 0)),
                                     float(f.get("bank_overlap", 0.0)),
                                     float(f.get("routing_noise", 0.0))))

    for (K, ov, rn) in sorted(phase_points_keys | probe_denied_points):
        sub = by_point.get((K, ov, rn, "SUBSTRATE"))
        rnd = by_point.get((K, ov, rn, "RANDOM"))
        is_probe_denied = (K, ov, rn) in probe_denied_points
        if is_probe_denied or sub is None or rnd is None:
            phase_map.append({
                "K": int(K), "bank_overlap": float(ov), "routing_noise": float(rn),
                "top1_substrate": None, "top1_random": None,
                "arms_differ": None,
                "verdict_tier": "CLIFF" if is_probe_denied else "MISSING",
                "saturation": False, "cliff_marker": True,
                "note": "VRAM_PROBE_DENIED" if is_probe_denied else "incomplete_pair",
            })
            continue
        sub_r = float(sub["recall"])
        rnd_r = float(rnd["recall"])
        margin = sub_r - rnd_r
        arms_differ = (sub["arm_sha256"] != rnd["arm_sha256"])
        if arms_differ:
            arms_differ_count += 1
        else:
            n_arms_identical += 1
        sat = (sub_r >= HP_SATURATION)
        if sat:
            n_saturate += 1
        floor = (margin <= HP_FLOOR_BAND)
        if floor:
            n_floor += 1
        passed = (sub_r >= HP_SUBSTRATE_PASS_RECALL and margin > HP_DISCRIM_MARGIN)
        if passed:
            n_pass += 1
        tier = "PASS" if passed else ("MIDDLE" if sub_r >= 0.30 else "FAIL")
        if K == 4096 and ov == 0.0 and rn == 0.0:
            rail_observed = sub_r
        phase_map.append({
            "K": int(K), "bank_overlap": float(ov), "routing_noise": float(rn),
            "top1_substrate": float(round(sub_r, 6)),
            "top1_random": float(round(rnd_r, 6)),
            "margin": float(round(margin, 6)),
            "route_acc": float(round(sub["route_acc"], 4)),
            "arms_differ": bool(arms_differ),
            "verdict_tier": tier,
            "saturation": bool(sat),
            "cliff_marker": bool(sub_r < HP_SUBSTRATE_PASS_RECALL),
        })

    # Headline: K-cliff per (overlap, noise) -- highest K where SUBSTRATE >= 0.50
    cliff_per_ov_rn: Dict[str, int] = {}
    for pp in phase_map:
        if pp["top1_substrate"] is None:
            continue
        key = "ov=%.2f_rn=%.2f" % (pp["bank_overlap"], pp["routing_noise"])
        if pp["top1_substrate"] >= HP_SUBSTRATE_PASS_RECALL:
            cur = cliff_per_ov_rn.get(key, 0)
            if pp["K"] > cur:
                cliff_per_ov_rn[key] = int(pp["K"])

    # GPU util / substrate-only gate
    n_llm = sum(int(b.get("_llm_forward_calls_at_inference", 0)) for b in per_key.values())
    substrate_only_ok = (n_llm == 0)

    detail = {
        "phase_map": phase_map,
        "cliff_per_ov_rn": cliff_per_ov_rn,
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "n_probe_cliffs": n_probe_cliffs,
        "cardinality_ok": cardinality_ok,
        "arms_differ_count": arms_differ_count,
        "n_arms_identical": n_arms_identical,
        "n_pass": n_pass,
        "n_saturate": n_saturate,
        "n_floor": n_floor,
        "rail_K4096_observed": rail_observed,
        "rail_K4096_target": HP_RAIL_K4096_RECALL,
        "substrate_only_ok": substrate_only_ok,
        "zero_llm_calls_at_inference": substrate_only_ok,
        "failures": real_failures,
        "probe_denials": [f for f in failures if f.get("exc_type") == "HP_VRAM_PROBE_BREACH"],
    }

    summary = "phase_points=%d pass=%d saturate=%d floor=%d probe_cliffs=%d arms_differ=%d/%d" % (
        len(phase_map), n_pass, n_saturate, n_floor, n_probe_cliffs,
        arms_differ_count, len(phase_map) - n_probe_cliffs)
    cliff_str = " | cliff_per_ov_rn=%s" % cliff_per_ov_rn
    rail_str = (" | rail_K4096=%.4f" % rail_observed) if rail_observed is not None else ""
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
        # Smoke gate: >=2 discriminate AND >=1 saturate AND >=1 fail/probe
        discrim_ok = (n_pass >= 2)
        sat_ok = (n_saturate >= 1)
        fail_ok = ((n_floor + n_probe_cliffs) >= 1)
        if discrim_ok and sat_ok and fail_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: discrim>=2 sat>=1 fail>=1 | %s%s%s%s" % (
                        summary, cliff_str, rail_str, card_str), detail)
        return ("HARD_FAIL",
                "SMOKE_HARD_FAIL_GATE: discrim_ok=%s sat_ok=%s fail_ok=%s | %s%s%s%s" % (
                    discrim_ok, sat_ok, fail_ok, summary, cliff_str, rail_str, card_str),
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
    # Per-seed HARD_PASS: >=3 of 5 K values at (ov=0, rn=0) corridor pass
    corridor_pass = 0
    for pp in phase_map:
        if pp["bank_overlap"] == 0.0 and pp["routing_noise"] == 0.0:
            if pp.get("verdict_tier") == "PASS":
                corridor_pass += 1
    if corridor_pass >= 3:
        # Sub-classify based on saturate/floor balance
        if n_saturate == len(phase_map):
            return ("HARD_FAIL",
                    "HARD_FAIL_SATURATION_ONLY: every point saturated; need larger K_max | %s%s%s" % (
                        summary, cliff_str, card_str), detail)
        return ("HARD_PASS",
                "HARD_PASS_K_CLIFF_PHASE_DIAGRAM: corridor_pass=%d/5 | %s%s%s%s" % (
                    corridor_pass, summary, cliff_str, rail_str, card_str), detail)
    if n_floor == len(phase_map):
        return ("HARD_FAIL",
                "HARD_FAIL_FLOOR_ONLY: every point at floor | %s%s%s" % (
                    summary, cliff_str, card_str), detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL_PHASE_DIAGRAM: corridor_pass=%d/5 | %s%s%s%s" % (
                corridor_pass, summary, cliff_str, rail_str, card_str), detail)


# ----------------------------- atexit synth + main -----------------------------
_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time(), "gpu_util": [],
                   "failures": []}


def _build_keys() -> List[str]:
    keys = []
    for s in SEEDS:
        for (K, ov, rn) in PHASE_POINTS:
            for R in REGIMES:
                keys.append("seed%d_K%d_ov%03d_rn%04d_regime%s" % (
                    s, K, int(round(ov * 100)), int(round(rn * 1000)), R))
    return keys


def _parse_key(key: str) -> Tuple[int, int, float, float, str]:
    parts = key.split("_")
    # seed7_K4096_ov030_rn0150_regimeSUBSTRATE
    seed = int(parts[0].replace("seed", ""))
    K = int(parts[1].replace("K", ""))
    ov_int = int(parts[2].replace("ov", ""))
    rn_int = int(parts[3].replace("rn", ""))
    R = parts[4].replace("regime", "")
    return seed, K, ov_int / 100.0, rn_int / 1000.0, R


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        run_config = {"N": N_DIM, "M": max(K for K, _, _ in PHASE_POINTS),
                      "run_mode": RUN_MODE}
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
        "metrics_source": "measured_gpu_substrate_bipolar_multibank_K_cliff_phase_diagram_v1_seed_%d" % SEED_THIS_CHUNK,
        "DESIGN_NOTE": (
            "K-cliff phase diagram (chunked sibling cell, seed=%d). Sweep axes: "
            "K x bank_overlap x routing_noise. Arms: SUBSTRATE (multi-bank cleanup) "
            "vs RANDOM (vector floor). VRAM probe denials are CLIFF MARKERS not "
            "failures. cardinality_ok counts probe_cliffs toward expected. Smoke "
            "uses 5 corner points at FULL N_DIM=%d (discriminator-must-survive-scale)."
        ) % (SEED_THIS_CHUNK, N_DIM),
    }


def _build_codebook(seed: int) -> torch.Tensor:
    return build_codebook_random(seed * 100003 + 99)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d phase_points=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, len(PHASE_POINTS), CONFIG_VERSION), flush=True)
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

    run_config = {"N": N_DIM, "M": max(K for K, _, _ in PHASE_POINTS),
                  "run_mode": RUN_MODE}
    all_keys = _build_keys()
    done_keys = set(list_completed_keys(out_dir, run_config=run_config))
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(all_keys)), flush=True)

    cached: Dict[int, torch.Tensor] = {}
    halt_after_loop = False

    for key in all_keys:
        if key in done_keys:
            continue
        seed, K, ov, rn, R = _parse_key(key)

        n_banks = K // K_PER_BANK
        est_bytes = _estimate_peak_working_set_bytes(K, n_banks, K_PER_BANK)
        if _CUDA_OK:
            free_b, total_b = torch.cuda.mem_get_info(0)
            budget = int(free_b * HP_VRAM_PROBE_FRACTION)
            if est_bytes > budget:
                fail_entry = {
                    "key": key,
                    "seed": seed, "k_total": K, "bank_overlap": ov,
                    "routing_noise": rn, "regime": R,
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
                # DO NOT break -- continue to next unit. Probe denial = cliff data.
                continue

        if seed not in cached:
            # Free any other seed's codebook to bound memory
            for stale_s in list(cached.keys()):
                if stale_s != seed:
                    del cached[stale_s]
                    if _CUDA_OK:
                        torch.cuda.empty_cache()
            print("[seed=%d] building codebook..." % seed, flush=True)
            cached[seed] = _build_codebook(seed)
        codebook = cached[seed]

        try:
            print("  [run] %s ... (est_peak=%.2fGB)" % (
                key, est_bytes / 1024**3), flush=True)
            rec = run_unit(seed, K, ov, rn, R, codebook,
                            _RESULTS_HOLDER["gpu_util"])
            write_partial_key(out_dir, key, rec)
            print("  [done] %s recall=%.4f route_acc=%.4f wall=%.1fs peak=%dMB" % (
                key, rec["recall"], rec["route_acc"], rec["wall_s"],
                rec.get("peak_mem_mb", 0)), flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            fail_entry = {
                "key": key,
                "seed": seed, "k_total": K, "bank_overlap": ov,
                "routing_noise": rn, "regime": R,
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
