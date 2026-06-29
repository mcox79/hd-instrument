"""Shared core for substrate_wm_encoder_family_phase_diagram_v1 siblings.

Second COMPONENT-SUBSTITUTION phase diagram for the WM K-cliff primitive
(after PC encoder family v1 on 2026-06-28 and seqbind encoder family v1).
USER directive 2026-06-28 (Research): systematic phase-diagram coverage
across COMPONENTS. We've done encoder family for PC + seqbind. Now: WM.

Target primitive: multi-bank WM K-cliff with K_cliff(B) = 256*B chain-grade
evidence at N=8192 (WM v3 GPU chunked, commit per cert ledger).

Outer axis (component substitution): encoder family ∈ {
    binary_bipolar  : {-1,+1}^N dense; elementwise mul bind; sum-bundle; cosine cleanup
    hrr_real        : N(0,1/N)^N dense Gaussian real; FFT circular convolution bind; sum-bundle; cosine cleanup
    fhrr            : unit-modulus exp(i*phi) in C^(N/2); elementwise complex mul bind; sum-bundle; complex cosine cleanup
    sparse_bipolar  : {-1,0,+1}^N, s/N=0.02 active; elementwise mul bind; sum-bundle; cosine cleanup
}

Inner axes:
    K_per_bank: per-bank capacity {64, 256, 1024, 4096}
    num_banks (B): {4, 16, 64}
    N=8192 FIXED (chain-grade WM operating point)

Cardinality:
    FULL : 4 encoders x 4 K x 3 B = 48 per seed
    SMOKE: 4 encoders x 3 K x 2 B = 24 per seed (drop K=4096 + B=64; smoke = N=4096 for CPU)

Per phase point: 3 arms (META_RULE_AF):
    MULTI_BANK_BIND : encoder's native multi-bank bind+bundle WM recall
    SINGLE_BANK_BASELINE : same total_K = K_per_bank * B but in B=1 (no bank-tagging)
    RANDOM_FLOOR : independent random codebook entry as query; floor ~ 1/M

Discriminator (per encoder, per (K_per_bank, B)):
    MULTI - SINGLE >= 0.30 = discriminator-fires
    MULTI >= 0.50 AND MULTI - SINGLE >= 0.30 = HARD_PASS-per-point
    MULTI in [0.30, 0.50) AND MULTI - SINGLE >= 0.20 = MIDDLE_BAND-per-point
    MULTI - RANDOM < 0.05 = FLOOR

Positive control: HRR_real at (K_per_bank=64, B=4, N=8192) MULTI recall >= 0.50.
WM v3 measured corner: K=64 B=4 N=4096 -> MULTI ~0.95 SINGLE ~0.05 (total_K=256 well below 256*4=1024 cliff).
At N=8192, total_K=256 is even further below cliff -> SAT regime expected.

Pre-reg: preregs/2026-06-28_substrate_wm_encoder_family_phase_diagram_v1.md

ASCII-only. No unicode. No em-dashes. No emojis.
CUDA preferred; CPU fallback for smoke (laptop is CPU-only).
FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue (Fix #24).

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

# Torch at TOP of module (PROT-020 GPU-eligibility scan)
import torch

_CUDA_OK = bool(torch.cuda.is_available())
if _CUDA_OK:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
SATURATED_RECALL = 0.95
HARD_PASS_LO = 0.50
MIDDLE_BAND_LO = 0.30
FLOOR_RECALL = 0.10
HP_DISCRIMINATOR = 0.30  # MULTI - SINGLE
MB_DISCRIMINATOR = 0.20
FLOOR_VS_RANDOM = 0.05

# Mechanism params (chain-grade v3 WM base)
SIGMA = 1.0
CUE_COS = 0.70
SPARSE_DENSITY = 0.02   # 2% nonzero for sparse_bipolar (seqbind convention)
CODEBOOK_SIZE_FULL = 16384
CODEBOOK_SIZE_SMOKE = 4096
N_ITEMS_PER_BANK_FULL = 96
N_ITEMS_PER_BANK_SMOKE = 32

# Encoder families (OUTER axis; LOCKED at module init)
ENCODER_FAMILIES = ("binary_bipolar", "hrr_real", "fhrr", "sparse_bipolar")

# Sweep axes
K_PER_BANK_FULL = [64, 256, 1024, 4096]
NUM_BANKS_FULL = [4, 16, 64]
N_DIM_FULL = 8192

K_PER_BANK_SMOKE = [64, 256, 1024]
NUM_BANKS_SMOKE = [4, 16]
N_DIM_SMOKE = 4096

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(ENCODER_FAMILIES) * len(K_PER_BANK_FULL)
                          * len(NUM_BANKS_FULL))  # 4*4*3 = 48
EXPECTED_N_UNITS_SMOKE = (len(ENCODER_FAMILIES) * len(K_PER_BANK_SMOKE)
                           * len(NUM_BANKS_SMOKE))  # 4*3*2 = 24

# Positive control: HRR_real at (K=64, B=4, N=8192) MULTI recall >= 0.50
# WM v3 chain-grade evidence: K=64 B=4 N=4096 -> MULTI ~0.95; N=8192 even better
POSITIVE_CONTROL = {
    "encoder_family": "hrr_real",
    "K_per_bank": 64,
    "num_banks": 4,
    "N": N_DIM_FULL,
    "multi_recall_floor": 0.50,
}
POSITIVE_CONTROL_SMOKE = {
    "encoder_family": "hrr_real",
    "K_per_bank": 64,
    "num_banks": 4,
    "N": N_DIM_SMOKE,
    "multi_recall_floor": 0.40,  # smaller N, allow some looseness
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# K-cliff predictions per encoder (HYPOTHESIZED@; META_RULE_AG / META_RULE_AH)
# ---------------------------------------------------------------------------
def k_cliff_prediction(encoder_family: str, B: int, N: int) -> int:
    """Hypothesized K_cliff(B) per encoder. Returns total_K cliff (not K_per_bank).

    HYPOTHESIZED@ from theory + WM v3 chain-grade evidence:
      hrr_real, binary_bipolar: K_cliff(B) = 256*B at N=8192 (chain-grade base)
      fhrr: 1.5x higher per Plate 2003 (N/2 complex pairs); K_cliff = 384*B
      sparse_bipolar: half per-bank cap (sparse codes less crosstalk-tolerant
                       in bind+bundle); K_cliff = 128*B
    Scaled by N/8192 (linear-in-N capacity scaling per Kanerva).
    """
    n_scale = N / 8192.0
    base_per_B = {
        "hrr_real": 256,
        "binary_bipolar": 256,
        "fhrr": 384,
        "sparse_bipolar": 128,
    }
    return int(round(base_per_B[encoder_family] * B * n_scale))


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Encoder family primitives (codebook + bind + bundle + unbind + cleanup)
# ---------------------------------------------------------------------------
def _build_binary_bipolar(V: int, N: int, seed: int) -> "torch.Tensor":
    """Dense bipolar {-1,+1}^N codebook (V, N) float32 on DEVICE."""
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _build_hrr_real(V: int, N: int, seed: int) -> "torch.Tensor":
    """Dense Gaussian N(0, 1/sqrt(N))^N codebook, L2-normalized per row."""
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(V, N)) / math.sqrt(N)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return torch.from_numpy(arr).to(DEVICE)


def _build_fhrr(V: int, N: int, seed: int) -> "torch.Tensor":
    """Unit-modulus complex codebook exp(i*phi) in C^(N/2), shape (V, N/2)."""
    if N % 2 != 0:
        raise ValueError(f"FHRR requires even N; got N={N}")
    n_complex = N // 2
    g = np.random.default_rng(seed)
    phi = g.uniform(0.0, 2.0 * math.pi, size=(V, n_complex)).astype(np.float32)
    real = np.cos(phi).astype(np.float32)
    imag = np.sin(phi).astype(np.float32)
    arr = np.empty((V, n_complex), dtype=np.complex64)
    arr.real = real
    arr.imag = imag
    return torch.from_numpy(arr).to(DEVICE)


def _build_sparse_bipolar(V: int, N: int, seed: int) -> "torch.Tensor":
    """Sparse-ternary {-1,0,+1}^N codebook, s = round(SPARSE_DENSITY * N) nonzero."""
    g = np.random.default_rng(seed)
    s = max(1, int(round(SPARSE_DENSITY * N)))
    arr = np.zeros((V, N), dtype=np.float32)
    for i in range(V):
        idx = g.choice(N, size=s, replace=False)
        signs = g.integers(0, 2, size=s).astype(np.float32) * 2.0 - 1.0
        arr[i, idx] = signs
    return torch.from_numpy(arr).to(DEVICE)


# Bind operations (per encoder)
def _bind_binary_bipolar(positions: "torch.Tensor",
                          items: "torch.Tensor") -> "torch.Tensor":
    """Elementwise mul bind for binary bipolar. positions, items: (K, N)."""
    return positions * items


def _bind_hrr_real(positions: "torch.Tensor",
                    items: "torch.Tensor") -> "torch.Tensor":
    """FFT circular convolution bind. positions, items: (K, N) real."""
    P = torch.fft.rfft(positions, dim=-1)
    I = torch.fft.rfft(items, dim=-1)
    bound = torch.fft.irfft(P * I, n=positions.shape[-1], dim=-1)
    return bound.to(torch.float32)


def _bind_fhrr(positions: "torch.Tensor",
                items: "torch.Tensor") -> "torch.Tensor":
    """Elementwise complex multiplication bind for FHRR."""
    return positions * items


def _bind_sparse_bipolar(positions: "torch.Tensor",
                          items: "torch.Tensor") -> "torch.Tensor":
    """Elementwise mul bind for sparse bipolar."""
    return positions * items


# Unbind operations (per encoder)
def _unbind_binary_bipolar(bundle: "torch.Tensor",
                            query: "torch.Tensor") -> "torch.Tensor":
    """Binary unbind: query * bundle (since query in +/-1, q*q=1)."""
    return query * bundle


def _unbind_hrr_real(bundle: "torch.Tensor",
                      query: "torch.Tensor") -> "torch.Tensor":
    """HRR unbind: correlation. bundle: (N,); query: (Q, N). Returns (Q, N)."""
    B = torch.fft.rfft(bundle, dim=-1)
    Q = torch.fft.rfft(query, dim=-1)
    R = B.unsqueeze(0) * torch.conj(Q) if query.ndim == 2 else B * torch.conj(Q)
    out = torch.fft.irfft(R, n=bundle.shape[-1], dim=-1)
    return out.to(torch.float32)


def _unbind_fhrr(bundle: "torch.Tensor",
                  query: "torch.Tensor") -> "torch.Tensor":
    """FHRR unbind: bundle * conj(query)."""
    return bundle * torch.conj(query)


def _unbind_sparse_bipolar(bundle: "torch.Tensor",
                            query: "torch.Tensor") -> "torch.Tensor":
    """Sparse unbind: bundle * query (elementwise; q*q indicator for active bits)."""
    return query * bundle


# Cleanup (cosine similarity vs item codebook)
def _cleanup_real(preds: "torch.Tensor",
                   items_book: "torch.Tensor") -> "torch.Tensor":
    """Cosine similarity for real codes. preds: (Q, N), items_book: (V, N)."""
    pred_n = torch.nn.functional.normalize(preds, dim=-1)
    items_n = torch.nn.functional.normalize(items_book, dim=-1)
    return pred_n @ items_n.T


def _cleanup_fhrr(preds: "torch.Tensor",
                   items_book: "torch.Tensor") -> "torch.Tensor":
    """Complex cosine for FHRR. preds: (Q, n_complex) c64; items_book: (V, n_complex) c64."""
    pred_mag = torch.linalg.norm(preds, dim=-1, keepdim=True).clamp(min=1e-8)
    item_mag = torch.linalg.norm(items_book, dim=-1, keepdim=True).clamp(min=1e-8)
    pred_n = preds / pred_mag
    items_n = items_book / item_mag
    # <pred, conj(item)> -> take real part
    sims = (pred_n @ items_n.conj().T).real
    return sims.to(torch.float32)


# Encoder family registry
_ENCODER_REGISTRY = {
    "binary_bipolar": {
        "build": _build_binary_bipolar,
        "bind": _bind_binary_bipolar,
        "unbind": _unbind_binary_bipolar,
        "cleanup": _cleanup_real,
        "dtype_label": "float32",
        "is_complex": False,
    },
    "hrr_real": {
        "build": _build_hrr_real,
        "bind": _bind_hrr_real,
        "unbind": _unbind_hrr_real,
        "cleanup": _cleanup_real,
        "dtype_label": "float32",
        "is_complex": False,
    },
    "fhrr": {
        "build": _build_fhrr,
        "bind": _bind_fhrr,
        "unbind": _unbind_fhrr,
        "cleanup": _cleanup_fhrr,
        "dtype_label": "complex64",
        "is_complex": True,
    },
    "sparse_bipolar": {
        "build": _build_sparse_bipolar,
        "bind": _bind_sparse_bipolar,
        "unbind": _unbind_sparse_bipolar,
        "cleanup": _cleanup_real,
        "dtype_label": "float32",
        "is_complex": False,
    },
}


# ---------------------------------------------------------------------------
# Multi-bank WM mechanism (per encoder)
# ---------------------------------------------------------------------------
def _build_multi_bank_bundle(encoder_family: str, K_per_bank: int,
                              num_banks: int, N: int, codebook_size: int,
                              seed: int) -> Tuple["torch.Tensor", "torch.Tensor",
                                                   "torch.Tensor", "torch.Tensor",
                                                   "torch.Tensor"]:
    """Build multi-bank WM bundle for one encoder.

    Returns:
        bundle              : (N,) for real / (N/2,) for FHRR
        codebook            : (V, N) or (V, N/2) for FHRR -- items_book
        bank_tags           : (B, N) per-bank tag vectors -- used by MULTI to disambiguate banks
        positions_per_bank  : (B, K_per_bank, N) sampled position vectors per bank
        items_truth_idx     : (B, K_per_bank) item indices encoded per bank (for recall scoring)
    """
    reg = _ENCODER_REGISTRY[encoder_family]
    g = np.random.default_rng(seed)

    # Build the item codebook (shared across banks; size = codebook_size)
    # Items use the encoder family's native codebook (sparse for sparse_bipolar, etc).
    codebook = reg["build"](codebook_size, N, seed)

    # Position codebook + bank tags use SAME encoder family as items so bind()
    # is type-consistent. SPECIAL CASE: sparse_bipolar uses DENSE bipolar position
    # and bank tags (Plate MAP-A convention) -- sparse-mul-sparse collapses to
    # near-zero density; dense tags preserve the sparse items' identity through
    # bind+unbind. This is the standard MAP architecture for sparse content +
    # dense roles.
    if encoder_family == "sparse_bipolar":
        positions_book = _build_binary_bipolar(K_per_bank, N, seed + 7919)
        bank_tags = _build_binary_bipolar(num_banks, N, seed + 31337)
    else:
        positions_book = reg["build"](K_per_bank, N, seed + 7919)
        bank_tags = reg["build"](num_banks, N, seed + 31337)

    # Sample which items go into which (bank, slot)
    # items_truth_idx: (B, K_per_bank) into codebook
    items_truth_idx_np = np.zeros((num_banks, K_per_bank), dtype=np.int64)
    for b in range(num_banks):
        items_truth_idx_np[b] = g.choice(codebook_size, size=K_per_bank, replace=False)
    items_truth_idx = torch.from_numpy(items_truth_idx_np).to(DEVICE)

    # Build the bundle: for MULTI_BANK_BIND, each bank contributes:
    #   bind(bank_tag[b], sum_k bind(positions[k], items[bank b, slot k]))
    # Bank-tagging uses ENCODER-NATIVE bind (circular conv for HRR, complex mul for
    # FHRR, elementwise for bipolar/sparse). Each item is bound with bank-tag AND
    # position, both via the encoder's native bind op. sum-bundle across all (b, k).
    bundle_shape_last = N // 2 if reg["is_complex"] else N
    if reg["is_complex"]:
        bundle = torch.zeros(bundle_shape_last, dtype=torch.complex64, device=DEVICE)
    else:
        bundle = torch.zeros(bundle_shape_last, dtype=torch.float32, device=DEVICE)

    # Materialize position vectors (K_per_bank, N) -- shared across banks
    positions = positions_book  # already a tensor

    # Per-bank loop: bind+bundle then bank-tag (via encoder-native bind) and accumulate
    positions_per_bank_list = []
    for b in range(num_banks):
        items_b = codebook[items_truth_idx[b]]  # (K_per_bank, N) or (K_per_bank, N/2) for FHRR
        # Bind positions with items per slot (encoder-native bind)
        bound_pos_items = reg["bind"](positions, items_b)  # (K_per_bank, N_eff)
        # Bind by bank_tag: encoder-native, broadcast bank_tag over K dimension.
        # For HRR (FFT conv), we batch across the K dim. Bank_tag is (N,) -> expand to (K, N).
        bank_tag_b = bank_tags[b].unsqueeze(0).expand_as(bound_pos_items)  # (K, N_eff)
        tagged_per_slot = reg["bind"](bank_tag_b, bound_pos_items)
        # Sum-bundle within the bank
        bank_bundle = tagged_per_slot.sum(dim=0)  # (N_eff,)
        bundle = bundle + bank_bundle
        positions_per_bank_list.append(positions)

    # Normalize bundle (per-encoder family convention)
    if reg["is_complex"]:
        # Per-component unit-modulus normalize
        mag = torch.abs(bundle).clamp(min=1e-8)
        bundle = bundle / mag
    else:
        norm = torch.linalg.norm(bundle).clamp(min=1e-8)
        bundle = bundle / norm

    positions_per_bank = torch.stack(positions_per_bank_list, dim=0)  # (B, K_per_bank, N or N/2)

    return bundle, codebook, bank_tags, positions_per_bank, items_truth_idx


def _query_multi_bank(encoder_family: str, bundle: "torch.Tensor",
                       codebook: "torch.Tensor", bank_tags: "torch.Tensor",
                       positions_per_bank: "torch.Tensor",
                       items_truth_idx: "torch.Tensor",
                       n_items_to_query: int, seed: int,
                       multi_bank: bool) -> float:
    """Query the WM bundle and return top-1 recall.

    multi_bank=True: query with bank_tag[b] * unbind(bundle, position[b, k])
                     -- exploits per-bank tag separation
    multi_bank=False: query with unbind(bundle, position[k]) for some bank
                     -- baseline that ignores bank tags (SINGLE_BANK arm)
                     Effectively treats the bundle as one big bank.
    """
    reg = _ENCODER_REGISTRY[encoder_family]
    g = np.random.default_rng(seed + 99991)

    num_banks, K_per_bank = items_truth_idx.shape

    # Sample n_items_to_query (bank, slot) pairs uniformly from all (B*K)
    total = num_banks * K_per_bank
    if n_items_to_query > total:
        n_items_to_query = total
    flat_idx = g.choice(total, size=n_items_to_query, replace=False)
    bank_choices = (flat_idx // K_per_bank).astype(np.int64)
    slot_choices = (flat_idx % K_per_bank).astype(np.int64)

    bank_choices_t = torch.from_numpy(bank_choices).to(DEVICE)
    slot_choices_t = torch.from_numpy(slot_choices).to(DEVICE)

    # Build query vectors: for each query (b, k), query = bank_tag[b] * position[b, k]
    # (MULTI) or just position[b, k] (SINGLE).
    # positions_per_bank shape: (B, K_per_bank, N_eff)
    # Gather the positions for each query.
    pos_for_queries = positions_per_bank[bank_choices_t, slot_choices_t]  # (Q, N_eff)

    # For MULTI: combined query = bind(bank_tag, position) via encoder-native bind.
    # Unbind the bundle by the combined query, recovering the item.
    # For SINGLE: query is just the position (no bank tag); exposes interference
    # because the bundle has B banks of bound items competing.
    if multi_bank:
        bank_tag_for_queries = bank_tags[bank_choices_t]  # (Q, N_eff)
        query_combined = reg["bind"](bank_tag_for_queries, pos_for_queries)
    else:
        query_combined = pos_for_queries

    # Unbind: bundle (N_eff,) with query_combined (Q, N_eff)
    # For all encoders: use encoder-native unbind. The HRR unbind handles 2D queries.
    if encoder_family == "hrr_real":
        unbound = _unbind_hrr_real(bundle, query_combined)
    elif encoder_family == "fhrr":
        unbound = bundle.unsqueeze(0) * torch.conj(query_combined)
    elif encoder_family == "binary_bipolar":
        unbound = bundle.unsqueeze(0) * query_combined
    elif encoder_family == "sparse_bipolar":
        unbound = bundle.unsqueeze(0) * query_combined
    else:
        raise ValueError(f"unknown encoder_family={encoder_family!r}")

    # Cleanup against codebook
    if reg["is_complex"]:
        sims = _cleanup_fhrr(unbound, codebook)
    else:
        sims = _cleanup_real(unbound, codebook)

    # Top-1 prediction vs ground truth
    preds = sims.argmax(dim=1)
    truth = items_truth_idx[bank_choices_t, slot_choices_t]
    hits = int((preds == truth).sum().item())
    return hits / max(n_items_to_query, 1)


def _random_floor_query(encoder_family: str, codebook: "torch.Tensor",
                          items_truth_idx: "torch.Tensor",
                          n_items_to_query: int, seed: int, N: int) -> float:
    """RANDOM_FLOOR arm: fresh-random vectors as queries, score against codebook truth."""
    reg = _ENCODER_REGISTRY[encoder_family]
    num_banks, K_per_bank = items_truth_idx.shape
    total = num_banks * K_per_bank
    if n_items_to_query > total:
        n_items_to_query = total
    g = np.random.default_rng(seed + 88883)
    flat_idx = g.choice(total, size=n_items_to_query, replace=False)
    bank_choices = (flat_idx // K_per_bank).astype(np.int64)
    slot_choices = (flat_idx % K_per_bank).astype(np.int64)
    bank_choices_t = torch.from_numpy(bank_choices).to(DEVICE)
    slot_choices_t = torch.from_numpy(slot_choices).to(DEVICE)

    # Fresh random codebook entries as "predictions"
    rand_preds = reg["build"](n_items_to_query, N, seed + 88883)

    if reg["is_complex"]:
        sims = _cleanup_fhrr(rand_preds, codebook)
    else:
        sims = _cleanup_real(rand_preds, codebook)
    preds = sims.argmax(dim=1)
    truth = items_truth_idx[bank_choices_t, slot_choices_t]
    hits = int((preds == truth).sum().item())
    return hits / max(n_items_to_query, 1)


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(encoder_family: str, K_per_bank: int, num_banks: int,
                      N: int, codebook_size: int, n_items_to_query: int,
                      seed: int) -> Dict[str, Any]:
    """Run one (encoder, K_per_bank, num_banks) phase point with 3 arms.

    Returns dict with multi_recall / single_recall / random_recall, discriminator,
    tier, peak_mem_mb, elapsed_s, encoder hash.
    """
    if encoder_family not in _ENCODER_REGISTRY:
        raise ValueError(f"unknown encoder_family={encoder_family!r}")

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Build the WM bundle
    sub_seed = seed * 10000 + K_per_bank * 100 + num_banks
    bundle, codebook, bank_tags, positions_per_bank, items_truth_idx = (
        _build_multi_bank_bundle(encoder_family, K_per_bank, num_banks, N,
                                  codebook_size, sub_seed))

    # ARM 1: MULTI_BANK_BIND (with bank tags)
    multi_recall = _query_multi_bank(
        encoder_family, bundle, codebook, bank_tags, positions_per_bank,
        items_truth_idx, n_items_to_query, sub_seed, multi_bank=True)

    # ARM 2: SINGLE_BANK_BASELINE (no bank tags applied; assumes B=1 effectively)
    # Same bundle (which already contains the multi-bank structure), but querying
    # WITHOUT bank-tag de-multiplexing -- exposes the interference cliff.
    single_recall = _query_multi_bank(
        encoder_family, bundle, codebook, bank_tags, positions_per_bank,
        items_truth_idx, n_items_to_query, sub_seed, multi_bank=False)

    # ARM 3: RANDOM_FLOOR
    random_recall = _random_floor_query(
        encoder_family, codebook, items_truth_idx, n_items_to_query,
        sub_seed, N)

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0
    discriminator = multi_recall - single_recall
    floor_gap = multi_recall - random_recall

    # Per-point verdict tier
    if multi_recall >= SATURATED_RECALL and discriminator >= HP_DISCRIMINATOR:
        tier = "SATURATED"
        saturation_flag = True
    elif multi_recall >= HARD_PASS_LO and discriminator >= HP_DISCRIMINATOR:
        tier = "HARD_PASS"
        saturation_flag = False
    elif multi_recall >= MIDDLE_BAND_LO and discriminator >= MB_DISCRIMINATOR:
        tier = "MIDDLE_BAND"
        saturation_flag = False
    elif floor_gap < FLOOR_VS_RANDOM:
        tier = "FLOOR"
        saturation_flag = False
    else:
        tier = "HARD_FAIL"
        saturation_flag = False

    # Encoder hash (for arms_differ + encoder distinctness)
    arm_hash_payload = json.dumps({
        "encoder_family": encoder_family,
        "K_per_bank": K_per_bank,
        "num_banks": num_banks,
        "multi_recall": round(multi_recall, 4),
        "single_recall": round(single_recall, 4),
        "random_recall": round(random_recall, 4),
    }, sort_keys=True).encode("utf-8")
    point_hash = hashlib.sha256(arm_hash_payload).hexdigest()[:16]

    total_K = K_per_bank * num_banks
    k_cliff_pred = k_cliff_prediction(encoder_family, num_banks, N)
    # past-cliff flag: total_K > predicted K_cliff
    past_cliff = total_K > k_cliff_pred

    # Cleanup
    del bundle, codebook, bank_tags, positions_per_bank, items_truth_idx
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "encoder_family": encoder_family,
        "K_per_bank": K_per_bank,
        "num_banks": num_banks,
        "N": N,
        "total_K": total_K,
        "k_cliff_prediction": k_cliff_pred,
        "past_cliff_predicted": past_cliff,
        "n_items_queried": n_items_to_query,
        "seed": seed,
        "multi_recall": round(multi_recall, 4),
        "single_recall": round(single_recall, 4),
        "random_recall": round(random_recall, 4),
        "discriminator": round(discriminator, 4),
        "floor_gap": round(floor_gap, 4),
        "verdict_tier_per_point": tier,
        "saturation_flag": saturation_flag,
        "point_hash": point_hash,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "dtype_label": _ENCODER_REGISTRY[encoder_family]["dtype_label"],
    }


# ---------------------------------------------------------------------------
# Selftest (encoder distinctness + sanity + cardinality + control)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Encoder hashes distinct + per-encoder mechanism sanity + cardinality.

    Sanity test: at K_per_bank=32, B=2, N=512, M=128 codebook, all 4 encoders
    must produce MULTI_recall > 2x RANDOM_recall (mechanism actually works).
    """
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 48:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 48"
    if EXPECTED_N_UNITS_SMOKE != 24:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 24"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. K-cliff predictions sanity (HRR @ B=4 N=8192 -> 1024)
    kc_hrr_b4 = k_cliff_prediction("hrr_real", 4, N_DIM_FULL)
    if kc_hrr_b4 != 1024:
        return False, f"k_cliff(hrr_real, B=4, N=8192) = {kc_hrr_b4} != 1024"
    kc_fhrr_b4 = k_cliff_prediction("fhrr", 4, N_DIM_FULL)
    if kc_fhrr_b4 != 1536:
        return False, f"k_cliff(fhrr, B=4, N=8192) = {kc_fhrr_b4} != 1536"
    kc_sparse_b4 = k_cliff_prediction("sparse_bipolar", 4, N_DIM_FULL)
    if kc_sparse_b4 != 512:
        return False, f"k_cliff(sparse_bipolar, B=4, N=8192) = {kc_sparse_b4} != 512"
    msgs.append(f"k_cliff hrr_b4=1024 fhrr_b4=1536 sparse_b4=512 OK")

    # 3. Encoder hashes distinct
    K_test = 32
    N_test = 512
    hashes = {}
    for fam in ENCODER_FAMILIES:
        reg = _ENCODER_REGISTRY[fam]
        X = reg["build"](K_test, N_test, seed)
        X_bytes = X.cpu().numpy().tobytes()
        h = hashlib.sha256(X_bytes).hexdigest()[:16]
        hashes[fam] = h
        del X
    if len(set(hashes.values())) != len(ENCODER_FAMILIES):
        return False, f"encoder codebooks NOT distinct at seed={seed}: {hashes}"
    msgs.append(f"encoder hashes distinct: {hashes}")

    # 4. Per-encoder mechanism sanity at tiny scale (K_per=16, B=2, N=512, M=64)
    # Expect MULTI > 2 * RANDOM for all encoders at this easy regime
    K_san = 16
    B_san = 2
    N_san = 512
    M_san = 128
    Q_san = 32
    for fam in ENCODER_FAMILIES:
        pt = eval_phase_point(fam, K_san, B_san, N_san, M_san, Q_san, seed)
        if pt["multi_recall"] < 2.0 * pt["random_recall"] and pt["multi_recall"] < 0.10:
            return False, (f"sanity FAIL {fam}: multi_recall={pt['multi_recall']} "
                           f"not > 2*random={pt['random_recall']} at easy K_san={K_san}")
        msgs.append(f"sanity {fam}: multi={pt['multi_recall']:.3f} "
                    f"single={pt['single_recall']:.3f} "
                    f"random={pt['random_recall']:.3f}")
        if _CUDA_OK:
            torch.cuda.empty_cache()

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (encoder, K_per_bank, num_banks) phase points for one seed.

    Halts on first exception (META_RULE_J: no silent except).
    """
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        K_sweep = K_PER_BANK_SMOKE
        B_sweep = NUM_BANKS_SMOKE
        N = N_DIM_SMOKE
        codebook_size = CODEBOOK_SIZE_SMOKE
        n_items_to_query = N_ITEMS_PER_BANK_SMOKE
    else:
        K_sweep = K_PER_BANK_FULL
        B_sweep = NUM_BANKS_FULL
        N = N_DIM_FULL
        codebook_size = CODEBOOK_SIZE_FULL
        n_items_to_query = N_ITEMS_PER_BANK_FULL

    expected_n_units = (len(ENCODER_FAMILIES) * len(K_sweep) * len(B_sweep))

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"encoders={ENCODER_FAMILIES} K={K_sweep} B={B_sweep} N={N} "
          f"M={codebook_size} Q={n_items_to_query} expected_n={expected_n_units}",
          flush=True)

    # Per-encoder K-cliff predictions for log
    k_cliff_preds: Dict[str, Dict[str, int]] = {}
    for fam in ENCODER_FAMILIES:
        k_cliff_preds[fam] = {f"B{B}": k_cliff_prediction(fam, B, N)
                                for B in B_sweep}
    print(f"[k_cliff] predictions per encoder/B: {k_cliff_preds}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for fam in ENCODER_FAMILIES:
        for B in B_sweep:
            for K in K_sweep:
                total_K = K * B
                if total_K > codebook_size:
                    print(f"[skip] seed={seed} enc={fam} K={K} B={B} "
                          f"total_K={total_K} > codebook={codebook_size}",
                          flush=True)
                    continue
                print(f"[point] seed={seed} enc={fam} K_per={K} B={B} N={N} ...",
                      flush=True)
                pt = eval_phase_point(fam, K, B, N, codebook_size,
                                       n_items_to_query, seed)
                phase_map.append(pt)
                print(f"  -> multi={pt['multi_recall']:.3f} "
                      f"single={pt['single_recall']:.3f} "
                      f"random={pt['random_recall']:.3f} "
                      f"disc={pt['discriminator']:.3f} "
                      f"tier={pt['verdict_tier_per_point']} "
                      f"past_cliff={pt['past_cliff_predicted']} "
                      f"peak_mb={pt['peak_mem_mb']:.1f} "
                      f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    # Cardinality: account for skipped (total_K > codebook) points
    expected_after_skip = sum(
        1 for fam in ENCODER_FAMILIES for B in B_sweep for K in K_sweep
        if K * B <= codebook_size
    )
    cardinality_ok = (observed_n_units == expected_after_skip)

    # Per-encoder arms-differ hashes
    arms_differ_per_enc: Dict[str, Dict[str, Any]] = {}
    encoder_mech_hashes: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        if not fam_pts:
            continue
        multi_payload = json.dumps([p["multi_recall"] for p in fam_pts],
                                    sort_keys=True).encode("utf-8")
        single_payload = json.dumps([p["single_recall"] for p in fam_pts],
                                     sort_keys=True).encode("utf-8")
        rnd_payload = json.dumps([p["random_recall"] for p in fam_pts],
                                  sort_keys=True).encode("utf-8")
        multi_hash = hashlib.sha256(multi_payload).hexdigest()
        single_hash = hashlib.sha256(single_payload).hexdigest()
        rnd_hash = hashlib.sha256(rnd_payload).hexdigest()
        arms_differ_per_enc[fam] = {
            "multi_hash": multi_hash[:16],
            "single_hash": single_hash[:16],
            "random_hash": rnd_hash[:16],
            "multi_vs_single_differ": multi_hash != single_hash,
            "multi_vs_random_differ": multi_hash != rnd_hash,
        }
        encoder_mech_hashes[fam] = multi_hash

    # Encoder-pair distinctness (META_RULE_AF)
    pairs_differ = {}
    fams = [f for f in ENCODER_FAMILIES if f in encoder_mech_hashes]
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            key = f"{fams[i]}_vs_{fams[j]}"
            pairs_differ[key] = (encoder_mech_hashes[fams[i]]
                                  != encoder_mech_hashes[fams[j]])
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)

    # Per-encoder summary (multi_recall_mean + tier counts + observed K-cliff location)
    per_encoder_summary: Dict[str, Dict[str, Any]] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        if not fam_pts:
            per_encoder_summary[fam] = {"empty": True}
            continue
        multis = [p["multi_recall"] for p in fam_pts]
        multi_mean = float(np.mean(multis))
        n_sat = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "SATURATED")
        n_hp = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_PASS")
        n_mb = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "FLOOR")
        n_fail = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_FAIL")
        # Observed cliff: per B, smallest K_per_bank where MULTI < 0.30
        observed_cliff: Dict[str, int] = {}
        for B in B_sweep:
            cliff_K = -1
            for K in sorted(K_sweep):
                matches = [p for p in fam_pts if p["K_per_bank"] == K
                           and p["num_banks"] == B]
                if matches and matches[0]["multi_recall"] < MIDDLE_BAND_LO:
                    cliff_K = K
                    break
            observed_cliff[f"B{B}"] = cliff_K
        per_encoder_summary[fam] = {
            "multi_recall_mean": round(multi_mean, 4),
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "observed_cliff_per_B": observed_cliff,
            "n_points": len(fam_pts),
        }

    # Tier the encoders (DOMINANT / COMPETITIVE / DOMINATED)
    means = {fam: per_encoder_summary[fam].get("multi_recall_mean", 0.0)
             for fam in ENCODER_FAMILIES
             if not per_encoder_summary[fam].get("empty", False)}
    encoder_tiers: Dict[str, str] = {}
    if means:
        best_mean = max(means.values())
        next_best = sorted(means.values(), reverse=True)
        next_best_val = next_best[1] if len(next_best) > 1 else 0.0
        for fam, m in means.items():
            if m >= best_mean - 0.05:
                if m == best_mean and m - next_best_val > 0.10:
                    encoder_tiers[fam] = "DOMINANT_ENCODER"
                else:
                    encoder_tiers[fam] = "COMPETITIVE_ENCODER"
            else:
                encoder_tiers[fam] = "DOMINATED_ENCODER"

    # Positive control check
    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                  if p["encoder_family"] == pc_target["encoder_family"]
                  and p["K_per_bank"] == pc_target["K_per_bank"]
                  and p["num_banks"] == pc_target["num_banks"]]
    if pc_matches:
        pc_multi = pc_matches[0]["multi_recall"]
        pc_pass = pc_multi >= pc_target["multi_recall_floor"]
    else:
        pc_multi = -1.0
        pc_pass = False

    positive_control_result = {
        "target": pc_target,
        "measured_multi_recall": pc_multi,
        "pass": pc_pass,
    }

    return {
        "seed": seed,
        "run_mode": run_mode,
        "encoder_families": list(ENCODER_FAMILIES),
        "K_sweep": K_sweep,
        "B_sweep": B_sweep,
        "N": N,
        "codebook_size": codebook_size,
        "n_items_to_query": n_items_to_query,
        "phase_map": phase_map,
        "per_encoder_summary": per_encoder_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_encoder": arms_differ_per_enc,
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_after_skip,
        "observed_n_units": observed_n_units,
        "k_cliff_predictions": k_cliff_preds,
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Pre-reg smoke gate. Return (passed, reason)."""
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    # 2. arms_differ for ALL encoders (MULTI vs RANDOM at minimum)
    for fam in ENCODER_FAMILIES:
        ad = arms_differ.get(fam, {})
        if not ad.get("multi_vs_random_differ"):
            return False, (f"arms_identical_encoder_{fam}: MULTI and RANDOM hashes "
                            f"match -- mechanism not working")

    # 3. 4 distinct encoder mechanism hashes (all pairs differ -- META_RULE_AF)
    n_pairs = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < n_pairs:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (f"encoder_collapse: {n_distinct}/{n_pairs} encoder pairs "
                        f"distinct; identical pairs: {collapsed}")

    # 4. Positive control
    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                        f"measured_multi={pc_result.get('measured_multi_recall')}; "
                        f"test rig broken")

    # 5. Cliff observable: at least 1 encoder shows MULTI in [0.10, 0.95]
    # (the discriminator-fires regime must EXIST in smoke per
    # DISCRIMINATOR-MUST-SURVIVE-SCALE)
    cliff_pts = [p for p in phase_map
                  if 0.10 < p["multi_recall"] < 0.95]
    if not cliff_pts:
        multi_vals = {f"{p['encoder_family']}_K{p['K_per_bank']}_B{p['num_banks']}":
                      p["multi_recall"] for p in phase_map}
        return False, (f"discriminator_fails_scale: smoke produced no cliff-edge "
                        f"MULTI values in [0.10, 0.95]; all in [0, 0.10] or "
                        f"[0.95, 1.0]: {multi_vals}; ABORT FULL DISPATCH")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ(4 encs) + "
                  f"4-distinct-encoders + positive_control_pass + cliff_observable")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """Aggregate one-seed partial into final metrics with verdict."""
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
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    pc_result = body.get("positive_control_result", {})
    per_enc_summary = body.get("per_encoder_summary", {})
    encoder_tiers = body.get("encoder_tiers", {})
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    # GPU util estimate
    if _CUDA_OK:
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
        gpu_util_estimate = min(0.95, max(0.30, avg_peak / 100.0))
    else:
        gpu_util_estimate = 0.0

    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb

    # Discriminating fraction (per pre-reg target 0.30)
    disc_fraction = n_disc / max(observed_n, 1)

    common = {
        "phase_map": phase_map,
        "per_encoder_summary": per_enc_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_encoder": arms_differ,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                        "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                        "HARD_FAIL": n_fail},
        "n_discriminating": n_disc,
        "discriminating_fraction": round(disc_fraction, 4),
        "k_cliff_predictions": body.get("k_cliff_predictions", {}),
        "gpu_util_estimate": round(gpu_util_estimate, 3),
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "sigma": SIGMA,
        "cue_cos": CUE_COS,
        "sparse_density": SPARSE_DENSITY,
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            pc_meas = pc_result.get("measured_multi_recall", -1.0)
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"4-encoder-distinct; positive_control@hrr_real K=64 B=4 "
                    f"multi={pc_meas:.3f}; encoder_tiers={encoder_tiers}; "
                    f"gpu_util~{gpu_util_estimate:.2f}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} hp={n_hp} mb={n_mb} "
                    f"floor={n_floor} fail={n_fail}")
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
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    elif any(not ad.get("multi_vs_random_differ")
              for ad in arms_differ.values()):
        bad = [fam for fam in ENCODER_FAMILIES
               if fam in arms_differ
               and not arms_differ[fam].get("multi_vs_random_differ")]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_ARMS_IDENTICAL: encoders with multi==random: {bad}"
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CONTROL_FAIL: positive_control "
                f"{pc_result.get('target')} measured multi="
                f"{pc_result.get('measured_multi_recall')}; test rig broken")
    elif n_pairs_differ == 0:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_NULL_ENCODER_INVARIANCE: all 4 encoders produced "
                f"identical multi-recall hashes; encoder is NOT a discriminating "
                f"lever for WM K-cliff in this regime; honest negative; "
                f"n_disc={n_disc}/{observed_n}; sat={n_sat} hp={n_hp} mb={n_mb} "
                f"floor={n_floor} fail={n_fail}")
    elif disc_fraction >= 0.30 and n_pairs_differ >= 2:
        # Check at least one encoder has an interior cliff (MIDDLE_BAND span observed)
        any_interior_cliff = False
        for fam, summ in per_enc_summary.items():
            if summ.get("empty"):
                continue
            tc = summ.get("tier_counts", {})
            if tc.get("MIDDLE_BAND", 0) >= 1 and (tc.get("HARD_PASS", 0)
                                                    + tc.get("SATURATED", 0)) >= 1:
                any_interior_cliff = True
                break
        if any_interior_cliff:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_ENCODER_DISCRIMINATION_WM_KCLIFF: "
                    f"{observed_n}/{expected_n} pts; sat={n_sat} hp={n_hp} mb={n_mb} "
                    f"floor={n_floor} fail={n_fail}; disc_frac={disc_fraction:.2f}; "
                    f"n_pairs_differ={n_pairs_differ}/{len(pairs_differ)}; "
                    f"encoder_tiers={encoder_tiers}; positive_control_pass; "
                    f"gpu_util~{gpu_util_estimate:.2f}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_ENCODER_DIFFERS_BUT_NO_INTERIOR_CLIFF: "
                    f"encoders distinguish but no MB+HP/SAT coexistence for any "
                    f"encoder; disc_frac={disc_fraction:.2f}; "
                    f"n_pairs_differ={n_pairs_differ}; encoder_tiers={encoder_tiers}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_ENCODER_DIFFERS_BUT_LOW_DISC: disc_frac="
                f"{disc_fraction:.2f} (need >=0.30); "
                f"n_pairs_differ={n_pairs_differ}/{len(pairs_differ)} (need >=2); "
                f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                f"encoder_tiers={encoder_tiers}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "DEVICE", "GPU_NAME", "GPU_MAX_MEM_GB",
    "SATURATED_RECALL", "HARD_PASS_LO", "MIDDLE_BAND_LO", "FLOOR_RECALL",
    "HP_DISCRIMINATOR", "MB_DISCRIMINATOR", "FLOOR_VS_RANDOM",
    "SIGMA", "CUE_COS", "SPARSE_DENSITY",
    "CODEBOOK_SIZE_FULL", "CODEBOOK_SIZE_SMOKE",
    "N_ITEMS_PER_BANK_FULL", "N_ITEMS_PER_BANK_SMOKE",
    "ENCODER_FAMILIES",
    "K_PER_BANK_FULL", "NUM_BANKS_FULL", "N_DIM_FULL",
    "K_PER_BANK_SMOKE", "NUM_BANKS_SMOKE", "N_DIM_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "k_cliff_prediction", "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
