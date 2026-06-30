"""Shared core for substrate_anchor4_encoder_family_phase_diagram_v3 siblings.

ANCHOR 4 encoder-family phase diagram v3 (META_RULE_AX fix; GPU torch port).

v1 + v2 ratified MEASURED_MECHANISM (not chain-grade) per Skunkworks
audit 2026-06-29 / 2026-06-30. Two load-bearing flaws caught:
  - encoder slots were observationally cosmetic: 3 of 4 encoders
    (binary_bipolar, hrr_real, fhrr) produced byte-identical phase
    outputs at n_atoms=200, n_buckets=64, dim<=1024 saturated regime.
  - chain-grade Pareto-AUC gate had no recency_decode_acc floor; sparse
    seed_13 by-construction-pass had recency at chance (0.405).

v3 promotion path (per Skunkworks audit recommendation, verbatim):
  - N >= 4096 AND n_atoms >= 1000 (push out of byte-degeneracy)
  - Add a 5th encoder family (sparse_real) constructed to be distinct
  - Add recency_decode_acc >= 0.30 floor to per-encoder gate (META_RULE_AP)
  - Run at FULL (>= 60 phase points minimum)
  - Pre-reg includes EXPECTED_N_PAIRS_DIFFER >= 5 / 10 as a discriminator
    (HARD_FAIL_DEGENERATE_ENCODERS rule; META_RULE_AX)

v3 additions:
  - PyTorch GPU backend (required for overnight_queue routing-gate compliance
    per PROT-020; scaled regime gives real GPU work; fp32 storage).
  - 5 encoder families:
        binary_bipolar : {-1,+1}^N dense; elementwise mul bind
        hrr_real       : N(0, 1/N) Gaussian; FFT circular convolution bind
        fhrr           : exp(i*phi) in C^(N/2); elementwise complex mul bind
        sparse_bipolar : {-1,0,+1}^N density 0.05; elementwise mul bind
        sparse_real    : N(0,1)^N density 0.10; elementwise mul bind (NEW)
  - HARD_FAIL_DEGENERATE_ENCODERS: cross-encoder distinct-pair count
    over C(5,2)=10 pairs MUST >= 5 (META_RULE_AX).
  - Per-encoder chain-grade gate now requires recency_decode_acc_mean
    >= 0.30 (META_RULE_AP; companion to Pareto-AUC).
  - Cross-encoder mechanism-hash distinctness asserted at smoke gate.

Anchor: substrate_anchor4_encoder_family_phase_diagram_v3_seed_{7,13,19}.

Pre-reg: preregs/2026-06-30_substrate_anchor4_encoder_family_phase_diagram_v3.md

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
import torch  # PROT-020: overnight_queue routing gate requires `import torch`


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
# v2 ratified Pareto-AUC thresholds (verbatim port; preserve semantics)
HP_DOMINANCE_RATE_LO = 0.85
HP_NET_DOMINANCE_LO = 0.70
HP_RD_LOSS_RATE_HI = 0.05

# META_RULE_AP: pair Pareto-AUC chain-grade gate with readout floor
HP_RECENCY_DECODE_FLOOR = 0.30  # per-encoder mean recency_decode_acc

# META_RULE_AX: cross-encoder distinctness (5 encoders -> C(5,2)=10 pairs)
HP_MIN_PAIRS_DIFFER = 5  # of 10 pairs

# Encoder families (OUTER axis; LOCKED at module init; 5 distinct families)
ENCODER_FAMILIES = (
    "binary_bipolar",
    "hrr_real",
    "fhrr",
    "sparse_bipolar",
    "sparse_real",
)

# Simulation params (SCALED from v1; n_atoms 200 -> 1500 / R_BUCKETS 64 -> 128
# per Skunkworks promotion-path: push out of byte-degeneracy regime)
N_ATOMS_BASE = 1500
N_DAYS_SIM = 365
RECENT_QUERY_DAYS = 30
QUERY_DECAY_TAU = 60.0
R_BUCKETS = 128

# Encoder dimension axis (cliff regime exposes encoder discrimination)
# v1 had {128, 1024}; v3 scales up to honor "N >= 4096" promotion-path
N_DIM_SWEEP_FULL = [1024, 4096, 8192]
N_DIM_SWEEP_SMOKE = [1024, 4096]
N_DIM_DEFAULT = 4096  # used by positive-control point
SPARSE_BIPOLAR_DENSITY = 0.05
SPARSE_REAL_DENSITY = 0.10  # higher density than bipolar for distinctness

# Sweep axes (decay, load) -- v1 axes preserved for v2 op-point reproduction
DECAY_RATE_DAYS_FULL = [30, 90, 180]
CAPACITY_LOAD_RATIO_FULL = [1.0, 5.0]
DECAY_RATE_DAYS_SMOKE = [30, 90]
CAPACITY_LOAD_RATIO_SMOKE = [1.0, 5.0]

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (
    len(ENCODER_FAMILIES) * len(DECAY_RATE_DAYS_FULL)
    * len(CAPACITY_LOAD_RATIO_FULL) * len(N_DIM_SWEEP_FULL)
)  # 5 * 3 * 2 * 3 = 90
EXPECTED_N_UNITS_SMOKE = (
    len(ENCODER_FAMILIES) * len(DECAY_RATE_DAYS_SMOKE)
    * len(CAPACITY_LOAD_RATIO_SMOKE) * len(N_DIM_SWEEP_SMOKE)
)  # 5 * 2 * 2 * 2 = 40

# Positive control: binary_bipolar at (decay=90, load=1.0) at N_DIM_DEFAULT
# must reproduce v2 TD_DOMINATES outcome.
POSITIVE_CONTROL = {
    "encoder_family": "binary_bipolar",
    "decay_rate_days": 90,
    "capacity_load_ratio": 1.0,
    "N_DIM": N_DIM_DEFAULT,
    "expected_pareto_outcome": "TD_DOMINATES",
    "min_recency_decode_acc": 0.80,
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Device setup (GPU when available; CPU fallback for selftest/smoke)
# ---------------------------------------------------------------------------
def _get_device(strict_gpu: bool = False) -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    if strict_gpu:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (PROT-020 / Fix #24): cuda.is_available()=False. "
            "v3 encoder family phase diagram at N_DIM up to %d requires CUDA "
            "for OVERNIGHT_QUEUE routing. Route to overnight_queue or run with "
            "--smoke / --self-test for local CPU fallback." % max(N_DIM_SWEEP_FULL)
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
# Encoder family primitives (torch tensors on _device)
# ---------------------------------------------------------------------------
def _make_gen(seed: int, device: torch.device) -> torch.Generator:
    g = torch.Generator(device=device)
    g.manual_seed(int(seed))
    return g


def _build_binary_bipolar_t(n_items: int, dim: int, seed: int,
                             device: torch.device) -> torch.Tensor:
    """Dense bipolar {-1, +1}^N (n_items, dim) float32 torch tensor."""
    g = _make_gen(seed, device)
    x = torch.empty(n_items, dim, device=device, dtype=torch.float32)
    x.bernoulli_(0.5, generator=g).mul_(2.0).sub_(1.0)
    return x


def _build_hrr_real_t(n_items: int, dim: int, seed: int,
                       device: torch.device) -> torch.Tensor:
    """Dense Gaussian N(0, 1/N), L2-normalized (n_items, dim) float32."""
    g = _make_gen(seed, device)
    x = torch.empty(n_items, dim, device=device, dtype=torch.float32)
    x.normal_(0.0, 1.0 / math.sqrt(dim), generator=g)
    norms = x.norm(dim=1, keepdim=True).clamp_min(1e-12)
    return x / norms


def _build_fhrr_t(n_items: int, dim: int, seed: int,
                   device: torch.device) -> torch.Tensor:
    """Unit-modulus complex exp(i*phi) in C^(dim/2); returned as complex64.

    Output shape: (n_items, dim/2) complex64. Total real DoF = dim.
    """
    if dim % 2 != 0:
        raise ValueError(f"FHRR requires even dim; got dim={dim}")
    n_complex = dim // 2
    g = _make_gen(seed, device)
    phi = torch.empty(n_items, n_complex, device=device, dtype=torch.float32)
    phi.uniform_(0.0, 2.0 * math.pi, generator=g)
    real = torch.cos(phi)
    imag = torch.sin(phi)
    return torch.complex(real, imag)


def _build_sparse_bipolar_t(n_items: int, dim: int, seed: int,
                              device: torch.device) -> torch.Tensor:
    """Sparse-ternary {-1, 0, +1}^N at density 0.05 (n_items, dim) float32."""
    g = _make_gen(seed, device)
    s = max(1, int(round(SPARSE_BIPOLAR_DENSITY * dim)))
    arr = torch.zeros(n_items, dim, device=device, dtype=torch.float32)
    # Per-row sparse pattern: top-s positions chosen by random scores
    scores = torch.empty(n_items, dim, device=device, dtype=torch.float32)
    scores.normal_(0.0, 1.0, generator=g)
    # Top-s indices per row
    topk_vals, topk_idx = scores.topk(s, dim=1)
    # Random signs at those positions
    sign_score = torch.empty(n_items, s, device=device, dtype=torch.float32)
    sign_score.bernoulli_(0.5, generator=g)
    signs = sign_score * 2.0 - 1.0
    arr.scatter_(1, topk_idx, signs)
    return arr


def _build_sparse_real_t(n_items: int, dim: int, seed: int,
                          device: torch.device) -> torch.Tensor:
    """Sparse REAL Gaussian N(0,1) at density 0.10 (n_items, dim) float32.

    Distinct from sparse_bipolar via continuous magnitudes + 2x higher density.
    META_RULE_AX 5th encoder family: constructed to be NON-degenerate vs the
    other 4 at N >= 1024 / n_atoms >= 1000.
    """
    g = _make_gen(seed, device)
    s = max(1, int(round(SPARSE_REAL_DENSITY * dim)))
    arr = torch.zeros(n_items, dim, device=device, dtype=torch.float32)
    scores = torch.empty(n_items, dim, device=device, dtype=torch.float32)
    scores.normal_(0.0, 1.0, generator=g)
    topk_vals, topk_idx = scores.topk(s, dim=1)
    # Use Gaussian values at those positions (NOT bipolar sign)
    gauss = torch.empty(n_items, s, device=device, dtype=torch.float32)
    gauss.normal_(0.0, 1.0, generator=g)
    arr.scatter_(1, topk_idx, gauss)
    # L2-normalize per row for cosine-comparable scoring
    norms = arr.norm(dim=1, keepdim=True).clamp_min(1e-12)
    return arr / norms


# Bind ops (elementwise for bipolar/sparse/fhrr; FFT circular conv for hrr_real)
def _bind_elementwise_real_t(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    return (A * B).to(torch.float32)


def _bind_circular_conv_t(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    """FFT-based circular convolution along dim=1 (HRR-real)."""
    fa = torch.fft.rfft(A, dim=1)
    fb = torch.fft.rfft(B, dim=1)
    out = torch.fft.irfft(fa * fb, n=A.shape[1], dim=1).to(torch.float32)
    return out


def _bind_complex_mul_t(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    return (A * B).to(torch.complex64)


# Unbind / decode ops
def _unbind_elementwise_real_t(bound: torch.Tensor,
                                key: torch.Tensor) -> torch.Tensor:
    """For bipolar self-inverse (1/key = key). For sparse, mask zeros to 0."""
    inv = torch.where(
        key != 0,
        torch.sign(key),
        torch.zeros_like(key),
    )
    return (bound * inv).to(torch.float32)


def _unbind_circular_corr_t(bound: torch.Tensor,
                              key: torch.Tensor) -> torch.Tensor:
    """Circular correlation = conv(bound, conj(key))."""
    fa = torch.fft.rfft(bound, dim=1)
    fb_conj = torch.fft.rfft(key, dim=1).conj()
    out = torch.fft.irfft(fa * fb_conj, n=bound.shape[1], dim=1).to(torch.float32)
    return out


def _unbind_complex_mul_t(bound: torch.Tensor,
                           key: torch.Tensor) -> torch.Tensor:
    return (bound * key.conj()).to(torch.complex64)


# Score ops (cosine for real codes; complex-analog for FHRR)
def _score_real_t(Q: torch.Tensor, X: torch.Tensor) -> torch.Tensor:
    """Real cosine (n_query, n_items). Q/X already on same device."""
    qn = Q.norm(dim=1, keepdim=True).clamp_min(1e-12)
    xn = X.norm(dim=1, keepdim=True).clamp_min(1e-12)
    return ((Q / qn) @ (X / xn).T).to(torch.float32)


def _score_fhrr_t(Q: torch.Tensor, X: torch.Tensor) -> torch.Tensor:
    """Re(Q . conj(X.T)) normalized by n_complex bins."""
    sims = (Q @ X.conj().T).real
    n_complex = X.shape[1]
    return (sims / float(n_complex)).to(torch.float32)


# Encoder dim actually used (FHRR is dim/2 complex; total real DoF = dim)
def _encoder_dim(family: str, dim: int) -> int:
    return dim // 2 if family == "fhrr" else dim


_ENCODER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "binary_bipolar": {
        "build": _build_binary_bipolar_t,
        "bind": _bind_elementwise_real_t,
        "unbind": _unbind_elementwise_real_t,
        "score": _score_real_t,
        "complex": False,
        "dtype_label": "float32",
    },
    "hrr_real": {
        "build": _build_hrr_real_t,
        "bind": _bind_circular_conv_t,
        "unbind": _unbind_circular_corr_t,
        "score": _score_real_t,
        "complex": False,
        "dtype_label": "float32",
    },
    "fhrr": {
        "build": _build_fhrr_t,
        "bind": _bind_complex_mul_t,
        "unbind": _unbind_complex_mul_t,
        "score": _score_fhrr_t,
        "complex": True,
        "dtype_label": "complex64",
    },
    "sparse_bipolar": {
        "build": _build_sparse_bipolar_t,
        "bind": _bind_elementwise_real_t,
        "unbind": _unbind_elementwise_real_t,
        "score": _score_real_t,
        "complex": False,
        "dtype_label": "float32",
    },
    "sparse_real": {
        "build": _build_sparse_real_t,
        "bind": _bind_elementwise_real_t,
        "unbind": _unbind_elementwise_real_t,
        "score": _score_real_t,
        "complex": False,
        "dtype_label": "float32",
    },
}


# ---------------------------------------------------------------------------
# Substrate timeline (PORTED VERBATIM from v1 for v2 op-point reproduction)
# ---------------------------------------------------------------------------
def simulate_atom_timeline(
    n_atoms: int, n_days: int, capacity_load_ratio: float,
    query_decay_tau: float, seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Port of v1/v2 timeline. Returns arrival_day, last_query_day, is_working_set.

    Kept numpy (RNG match v1/v2 for positive-control reproducibility).
    """
    rng = np.random.RandomState(seed)
    arrival_day = rng.randint(0, n_days, size=n_atoms).astype(np.int64)
    is_core = rng.rand(n_atoms) < 0.30
    last_query_day = np.full(n_atoms, -1, dtype=np.int64)
    for i in range(n_atoms):
        a = arrival_day[i]
        if is_core[i]:
            last_query_day[i] = n_days - 1 - rng.randint(0, RECENT_QUERY_DAYS)
        else:
            age_at_end = n_days - a
            mean_interval = query_decay_tau * capacity_load_ratio
            lam = max(0.0, age_at_end / max(mean_interval, 1e-6))
            n_reqs = rng.poisson(lam) if lam > 0 else 0
            if n_reqs == 0:
                last_query_day[i] = a
            else:
                qs = rng.randint(a, n_days, size=n_reqs)
                last_query_day[i] = int(qs.max())
    is_working_set = (last_query_day >= n_days - RECENT_QUERY_DAYS) & (last_query_day >= 0)
    return arrival_day, last_query_day, is_working_set


# ---------------------------------------------------------------------------
# Encoder mediation: encode atom-bindings + decode recency (torch GPU)
# ---------------------------------------------------------------------------
def quantize_to_bucket(day: int, n_days: int, n_buckets: int) -> int:
    if day < 0:
        return 0
    return int(min(n_buckets - 1, max(0, (day * n_buckets) // max(n_days, 1))))


def build_encoded_atom_store(
    encoder_family: str, n_atoms: int, last_query_day: np.ndarray,
    n_days: int, n_buckets: int, dim: int, seed: int,
    device: torch.device,
) -> Dict[str, Any]:
    """Encode atoms with (atom_id, recency_bucket) bindings (torch tensors)."""
    reg = _ENCODER_REGISTRY[encoder_family]

    # Atom-id codes (n_atoms, dim_eff)
    atom_codes = reg["build"](n_atoms, dim, seed, device)

    # Recency basis vectors (n_buckets, dim_eff)
    recency_basis = reg["build"](n_buckets, dim, seed + 31337, device)

    # Buckets per atom
    buckets = np.array(
        [quantize_to_bucket(int(d), n_days, n_buckets) for d in last_query_day],
        dtype=np.int64,
    )
    buckets_t = torch.from_numpy(buckets).to(device)

    # Gather recency keys per atom; (n_atoms, dim_eff)
    recency_keys = recency_basis[buckets_t]

    # Bind: atom_code (*) recency_basis[bucket]
    bound = reg["bind"](atom_codes, recency_keys)

    return {
        "atom_codes": atom_codes,
        "recency_basis": recency_basis,
        "bound": bound,
        "buckets_true": buckets,        # CPU numpy for later compare
        "buckets_true_t": buckets_t,    # GPU torch for accuracy compute
        "family": encoder_family,
        "dim_eff": _encoder_dim(encoder_family, dim),
    }


def decode_recency_buckets(
    store: Dict[str, Any],
) -> Tuple[torch.Tensor, float]:
    """Decode each atom's recency bucket from the bound store.

    Returns (preds_t (long, on device), top1_acc as Python float).
    """
    reg = _ENCODER_REGISTRY[store["family"]]
    atom_codes = store["atom_codes"]
    recency_basis = store["recency_basis"]
    bound = store["bound"]
    buckets_true_t = store["buckets_true_t"]

    decoded = reg["unbind"](bound, atom_codes)
    sims = reg["score"](decoded, recency_basis)
    preds_t = sims.argmax(dim=1)
    acc = float((preds_t == buckets_true_t).to(torch.float32).mean().item())
    return preds_t, acc


# ---------------------------------------------------------------------------
# Arms (TIME_DECAY / RANDOM eviction)
# ---------------------------------------------------------------------------
def arm_time_decay_via_encoder(
    decoded_buckets_t: torch.Tensor, n_days: int, n_buckets: int,
    decay_rate_days: int,
) -> np.ndarray:
    """Evict atoms whose DECODED last_query_day-age > decay_rate_days."""
    decoded_cpu = decoded_buckets_t.detach().cpu().numpy().astype(np.int64)
    bucket_width_days = n_days / float(max(n_buckets, 1))
    estimated_last_query_day = (decoded_cpu.astype(np.float64) + 0.5) * bucket_width_days
    estimated_age = n_days - estimated_last_query_day
    return (estimated_age > decay_rate_days).astype(bool)


def arm_random_eviction(
    n_atoms: int, target_eviction_count: int, seed: int,
) -> np.ndarray:
    rng = np.random.RandomState(seed + 7919)
    evicted = np.zeros(n_atoms, dtype=bool)
    if target_eviction_count <= 0:
        return evicted
    target_eviction_count = min(target_eviction_count, n_atoms)
    idx = rng.choice(n_atoms, size=target_eviction_count, replace=False)
    evicted[idx] = True
    return evicted


# ---------------------------------------------------------------------------
# Metrics (v2 ratified discriminator)
# ---------------------------------------------------------------------------
def compute_arm_metrics(evicted: np.ndarray, is_working_set: np.ndarray) -> Dict[str, Any]:
    n_atoms = len(evicted)
    n_ws = int(is_working_set.sum())
    n_alive = int((~evicted).sum())
    n_evicted = int(evicted.sum())
    if n_ws == 0:
        ws_retention = float("nan")
    else:
        ws_retention = float(((~evicted) & is_working_set).sum() / n_ws)
    if n_alive == 0:
        clutter_fraction = float("nan")
    else:
        clutter_fraction = float(((~evicted) & (~is_working_set)).sum() / n_alive)
    if np.isnan(ws_retention) or np.isnan(clutter_fraction):
        composite = float("nan")
    else:
        composite = ws_retention - clutter_fraction
    return {
        "working_set_retention": float(ws_retention),
        "clutter_fraction": float(clutter_fraction),
        "composite": float(composite),
        "n_alive": int(n_alive),
        "n_evicted": int(n_evicted),
        "eviction_fraction": float(n_evicted / n_atoms) if n_atoms else 0.0,
    }


def pareto_dominance_outcome(td_ws, td_clut, rd_ws, rd_clut) -> str:
    if any(np.isnan(x) for x in (td_ws, td_clut, rd_ws, rd_clut)):
        return "TIE"
    td_y = 1.0 - td_clut
    rd_y = 1.0 - rd_clut
    if td_ws >= rd_ws and td_y >= rd_y and (td_ws > rd_ws or td_y > rd_y):
        return "TD_DOMINATES"
    if rd_ws >= td_ws and rd_y >= td_y and (rd_ws > td_ws or rd_y > td_y):
        return "RD_DOMINATES"
    return "TIE"


# ---------------------------------------------------------------------------
# Per-phase-point eval (uses GPU torch for build + decode)
# ---------------------------------------------------------------------------
def eval_phase_point(
    encoder_family: str, decay_rate_days: int, capacity_load_ratio: float,
    n_atoms: int, n_days: int, n_buckets: int, dim: int, seed: int,
    device: torch.device,
) -> Dict[str, Any]:
    if encoder_family not in _ENCODER_REGISTRY:
        raise ValueError(f"unknown encoder_family={encoder_family!r}")
    t0 = time.time()

    arrival_day, last_query_day, is_working_set = simulate_atom_timeline(
        n_atoms=n_atoms, n_days=n_days,
        capacity_load_ratio=capacity_load_ratio,
        query_decay_tau=QUERY_DECAY_TAU, seed=seed,
    )

    store = build_encoded_atom_store(
        encoder_family=encoder_family, n_atoms=n_atoms,
        last_query_day=last_query_day, n_days=n_days, n_buckets=n_buckets,
        dim=dim, seed=seed, device=device,
    )
    decoded_buckets_t, recency_decode_acc = decode_recency_buckets(store)

    td_evicted = arm_time_decay_via_encoder(
        decoded_buckets_t, n_days, n_buckets, decay_rate_days,
    )
    td_metrics = compute_arm_metrics(td_evicted, is_working_set)

    rd_evicted = arm_random_eviction(n_atoms, int(td_evicted.sum()), seed)
    rd_metrics = compute_arm_metrics(rd_evicted, is_working_set)

    pareto_outcome = pareto_dominance_outcome(
        td_metrics["working_set_retention"], td_metrics["clutter_fraction"],
        rd_metrics["working_set_retention"], rd_metrics["clutter_fraction"],
    )

    # Free GPU tensors
    del store, decoded_buckets_t
    if device.type == "cuda":
        torch.cuda.empty_cache()

    elapsed = time.time() - t0
    return {
        "encoder_family": encoder_family,
        "decay_rate_days": int(decay_rate_days),
        "capacity_load_ratio": float(capacity_load_ratio),
        "n_atoms": int(n_atoms),
        "n_days": int(n_days),
        "n_buckets": int(n_buckets),
        "N_dim_input": int(dim),
        "dim_eff": _encoder_dim(encoder_family, dim),
        "n_working_set_atoms": int(is_working_set.sum()),
        "recency_decode_acc": round(recency_decode_acc, 4),
        "ARM_TIME_DECAY_EVICTION": td_metrics,
        "ARM_RANDOM_EVICTION": rd_metrics,
        "td_minus_random_ws_retention": round(
            td_metrics["working_set_retention"] - rd_metrics["working_set_retention"], 4),
        "td_minus_random_clutter_fraction": round(
            td_metrics["clutter_fraction"] - rd_metrics["clutter_fraction"], 4),
        "td_minus_random_composite": round(
            td_metrics["composite"] - rd_metrics["composite"], 4),
        "pareto_outcome": pareto_outcome,
        "wall_s": round(elapsed, 3),
        "dtype_label": _ENCODER_REGISTRY[encoder_family]["dtype_label"],
    }


# ---------------------------------------------------------------------------
# Selftest (encoder distinctness + recency decode + positive control)
# ---------------------------------------------------------------------------
def selftest(seed: int, device: torch.device = None) -> Tuple[bool, str]:
    if device is None:
        device = _get_device(strict_gpu=False)
    msgs: List[str] = []

    # 1. Cardinality math (5 encoders -> bigger grid)
    if EXPECTED_N_UNITS_FULL != 90:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 90"
    if EXPECTED_N_UNITS_SMOKE != 40:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 40"
    msgs.append(
        f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
        f"SMOKE={EXPECTED_N_UNITS_SMOKE}"
    )

    # 2. Encoder distinctness at small scale (META_RULE_AF / META_RULE_AX prelim)
    n_atoms_san = 50
    n_days_san = 180
    n_buckets_san = 32
    dim_san = 512
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms_san, n_days_san, 1.0, QUERY_DECAY_TAU, seed,
    )
    hashes: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        store = build_encoded_atom_store(
            fam, n_atoms_san, lastq, n_days_san, n_buckets_san, dim_san,
            seed, device,
        )
        bound_cpu = store["bound"].detach().cpu().numpy()
        # FHRR is complex; bytes still distinct per family
        bound_bytes = bound_cpu.tobytes()
        hashes[fam] = hashlib.sha256(bound_bytes).hexdigest()[:16]
        del store
        if device.type == "cuda":
            torch.cuda.empty_cache()
    if len(set(hashes.values())) != len(ENCODER_FAMILIES):
        return False, (
            f"encoder stores NOT distinct at seed={seed} dim={dim_san}: {hashes}"
        )
    msgs.append(f"encoder distinct hashes(dim={dim_san}): {hashes}")

    # 3. Recency decode fidelity per encoder at N_DIM_DEFAULT (>= 0.50 each)
    decode_accs: Dict[str, float] = {}
    n_atoms_dec = 200
    n_buckets_dec = 32
    dim_dec = N_DIM_DEFAULT
    arrival_d, lastq_d, _ = simulate_atom_timeline(
        n_atoms_dec, n_days_san, 1.0, QUERY_DECAY_TAU, seed + 1,
    )
    for fam in ENCODER_FAMILIES:
        store = build_encoded_atom_store(
            fam, n_atoms_dec, lastq_d, n_days_san, n_buckets_dec, dim_dec,
            seed + 1, device,
        )
        _, acc = decode_recency_buckets(store)
        decode_accs[fam] = round(acc, 3)
        del store
        if device.type == "cuda":
            torch.cuda.empty_cache()
        if acc < 0.50:
            return False, (
                f"recency decode FAIL {fam}: acc={acc:.3f} < 0.50 at "
                f"n_atoms={n_atoms_dec} n_buckets={n_buckets_dec} dim={dim_dec}"
            )
    msgs.append(f"recency_decode_acc per encoder(dim={dim_dec}): {decode_accs}")

    # 4. v2 op-point reproduction
    pt = eval_phase_point(
        encoder_family="binary_bipolar", decay_rate_days=90,
        capacity_load_ratio=1.0, n_atoms=N_ATOMS_BASE,
        n_days=N_DAYS_SIM, n_buckets=R_BUCKETS, dim=N_DIM_DEFAULT,
        seed=13, device=device,
    )
    if pt["pareto_outcome"] != "TD_DOMINATES":
        return False, (
            f"Positive control FAILED: binary_bipolar at v2 op-point (dr=90, "
            f"ld=1.0, seed=13, N_DIM={N_DIM_DEFAULT}) expected TD_DOMINATES, "
            f"got {pt['pareto_outcome']}. "
            f"TD(ws={pt['ARM_TIME_DECAY_EVICTION']['working_set_retention']:.3f}, "
            f"clut={pt['ARM_TIME_DECAY_EVICTION']['clutter_fraction']:.3f}) "
            f"recency_acc={pt['recency_decode_acc']:.3f}"
        )
    if pt["recency_decode_acc"] < POSITIVE_CONTROL["min_recency_decode_acc"]:
        return False, (
            f"Positive control recency_decode acc too low: "
            f"{pt['recency_decode_acc']:.3f} < "
            f"{POSITIVE_CONTROL['min_recency_decode_acc']}"
        )
    msgs.append(
        f"positive_control: binary_bipolar @ (dr=90, ld=1.0, seed=13, "
        f"N_DIM={N_DIM_DEFAULT}) pareto={pt['pareto_outcome']} "
        f"td.ws={pt['ARM_TIME_DECAY_EVICTION']['working_set_retention']:.3f} "
        f"rd.ws={pt['ARM_RANDOM_EVICTION']['working_set_retention']:.3f} "
        f"recency_acc={pt['recency_decode_acc']:.3f}"
    )

    # 5. Pareto dominance unit-checks
    assert pareto_dominance_outcome(0.9, 0.1, 0.5, 0.4) == "TD_DOMINATES"
    assert pareto_dominance_outcome(0.5, 0.4, 0.9, 0.1) == "RD_DOMINATES"
    assert pareto_dominance_outcome(0.5, 0.3, 0.5, 0.3) == "TIE"
    assert pareto_dominance_outcome(0.9, 0.4, 0.5, 0.1) == "TIE"
    assert pareto_dominance_outcome(float("nan"), 0.1, 0.5, 0.4) == "TIE"
    msgs.append("pareto_dominance unit-tests pass")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(
    seed: int, run_mode: str, device: torch.device,
) -> Dict[str, Any]:
    """Run all (encoder, decay, load, N_dim) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    decay_sweep = DECAY_RATE_DAYS_SMOKE if is_smoke else DECAY_RATE_DAYS_FULL
    load_sweep = CAPACITY_LOAD_RATIO_SMOKE if is_smoke else CAPACITY_LOAD_RATIO_FULL
    dim_sweep = N_DIM_SWEEP_SMOKE if is_smoke else N_DIM_SWEEP_FULL
    expected_n = (
        len(ENCODER_FAMILIES) * len(decay_sweep)
        * len(load_sweep) * len(dim_sweep)
    )

    print(
        f"[run_one_seed v3] seed={seed} mode={run_mode} device={device} "
        f"encoders={ENCODER_FAMILIES} decay_axis={decay_sweep} "
        f"load_axis={load_sweep} dim_axis={dim_sweep} "
        f"R_BUCKETS={R_BUCKETS} n_atoms={N_ATOMS_BASE} "
        f"expected_n={expected_n}",
        flush=True,
    )

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for fam in ENCODER_FAMILIES:
        for dr in decay_sweep:
            for cl in load_sweep:
                for nd in dim_sweep:
                    pt = eval_phase_point(
                        encoder_family=fam, decay_rate_days=dr,
                        capacity_load_ratio=cl, n_atoms=N_ATOMS_BASE,
                        n_days=N_DAYS_SIM, n_buckets=R_BUCKETS, dim=nd,
                        seed=seed, device=device,
                    )
                    phase_map.append(pt)
                    td = pt["ARM_TIME_DECAY_EVICTION"]
                    rd = pt["ARM_RANDOM_EVICTION"]
                    print(
                        f"[pt] s={seed} {fam[:14]:<14} dr={dr:>3} ld={cl:.1f} "
                        f"N={nd:>5} td.ws={td['working_set_retention']:.3f} "
                        f"rd.ws={rd['working_set_retention']:.3f} "
                        f"pareto={pt['pareto_outcome']:<14} "
                        f"rec={pt['recency_decode_acc']:.3f} "
                        f"t={pt['wall_s']:.2f}s",
                        flush=True,
                    )

    elapsed = time.time() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # Per-encoder Pareto-AUC stats + recency_decode_mean
    per_encoder_summary: Dict[str, Dict[str, Any]] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        outcomes = [p["pareto_outcome"] for p in fam_pts]
        td_wins = sum(1 for o in outcomes if o == "TD_DOMINATES")
        rd_wins = sum(1 for o in outcomes if o == "RD_DOMINATES")
        ties = sum(1 for o in outcomes if o == "TIE")
        n_pts_fam = len(fam_pts)
        dom_rate = (td_wins + 0.5 * ties) / max(n_pts_fam, 1)
        net_dom = (td_wins - rd_wins) / max(n_pts_fam, 1)
        rd_loss = rd_wins / max(n_pts_fam, 1)
        decode_accs = [p["recency_decode_acc"] for p in fam_pts]
        per_encoder_summary[fam] = {
            "n_points": n_pts_fam,
            "td_wins": td_wins,
            "rd_wins": rd_wins,
            "ties": ties,
            "dominance_rate": round(dom_rate, 4),
            "net_dominance": round(net_dom, 4),
            "rd_loss_rate": round(rd_loss, 4),
            "recency_decode_acc_mean": round(
                float(np.mean(decode_accs)), 4) if decode_accs else 0.0,
        }

    # META_RULE_AX: cross-encoder pair distinctness over C(5,2)=10 pairs
    # Hash per-encoder per-point outcome vector ordered by (decay, load, dim)
    encoder_outcome_hashes: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = sorted(
            [p for p in phase_map if p["encoder_family"] == fam],
            key=lambda p: (p["decay_rate_days"], p["capacity_load_ratio"],
                            p["N_dim_input"]),
        )
        payload = json.dumps(
            [(p["pareto_outcome"],
              round(p["ARM_TIME_DECAY_EVICTION"]["composite"], 4),
              round(p["recency_decode_acc"], 4))
             for p in fam_pts],
            sort_keys=True,
        ).encode("utf-8")
        encoder_outcome_hashes[fam] = hashlib.sha256(payload).hexdigest()[:16]

    fams = list(ENCODER_FAMILIES)
    pairs_differ: Dict[str, bool] = {}
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            key = f"{fams[i]}_vs_{fams[j]}"
            pairs_differ[key] = (encoder_outcome_hashes[fams[i]]
                                  != encoder_outcome_hashes[fams[j]])
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)
    n_pairs_total = len(pairs_differ)  # 10 for C(5,2)

    # TIME_DECAY vs RANDOM per encoder (mechanism gate; META_RULE_AF within-arm)
    arms_differ_per_enc: Dict[str, Dict[str, Any]] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        td_payload = json.dumps(
            [round(p["ARM_TIME_DECAY_EVICTION"]["composite"], 4) for p in fam_pts],
            sort_keys=True,
        ).encode("utf-8")
        rd_payload = json.dumps(
            [round(p["ARM_RANDOM_EVICTION"]["composite"], 4) for p in fam_pts],
            sort_keys=True,
        ).encode("utf-8")
        td_hash = hashlib.sha256(td_payload).hexdigest()[:16]
        rd_hash = hashlib.sha256(rd_payload).hexdigest()[:16]
        arms_differ_per_enc[fam] = {
            "mechanism_hash": td_hash,
            "random_hash": rd_hash,
            "differ": td_hash != rd_hash,
        }

    # Positive control
    pc_n_dim = POSITIVE_CONTROL["N_DIM"]
    pc_matches = [
        p for p in phase_map
        if p["encoder_family"] == POSITIVE_CONTROL["encoder_family"]
        and p["decay_rate_days"] == POSITIVE_CONTROL["decay_rate_days"]
        and abs(p["capacity_load_ratio"]
                - POSITIVE_CONTROL["capacity_load_ratio"]) < 1e-6
        and p["N_dim_input"] == pc_n_dim
    ]
    if pc_matches:
        pc_pt = pc_matches[0]
        pc_outcome = pc_pt["pareto_outcome"]
        pc_decode = pc_pt["recency_decode_acc"]
        pc_pass = (pc_outcome == POSITIVE_CONTROL["expected_pareto_outcome"]
                    and pc_decode >= POSITIVE_CONTROL["min_recency_decode_acc"])
    else:
        pc_outcome = "MISSING"
        pc_decode = -1.0
        pc_pass = False

    positive_control_result = {
        "target": POSITIVE_CONTROL,
        "measured_outcome": pc_outcome,
        "measured_recency_decode_acc": pc_decode,
        "pass": pc_pass,
    }

    # Encoder tier classification (per-encoder dominance_rate-ranked)
    means = {fam: per_encoder_summary[fam]["dominance_rate"]
             for fam in ENCODER_FAMILIES}
    best = max(means.values()) if means else 0.0
    encoder_tiers: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        m = means[fam]
        if m >= best - 0.05:
            others = [v for k, v in means.items() if k != fam]
            next_best = max(others) if others else 0.0
            if m == best and m - next_best > 0.10:
                encoder_tiers[fam] = "DOMINANT_ENCODER"
            else:
                encoder_tiers[fam] = "COMPETITIVE_ENCODER"
        else:
            encoder_tiers[fam] = "DOMINATED_ENCODER"

    return {
        "seed": seed,
        "run_mode": run_mode,
        "encoder_families": list(ENCODER_FAMILIES),
        "decay_sweep": decay_sweep,
        "load_sweep": load_sweep,
        "dim_sweep": dim_sweep,
        "N_DIM_DEFAULT": N_DIM_DEFAULT,
        "R_BUCKETS": R_BUCKETS,
        "n_atoms": N_ATOMS_BASE,
        "n_days": N_DAYS_SIM,
        "phase_map": phase_map,
        "per_encoder_summary": per_encoder_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "n_pairs_total": n_pairs_total,
        "arms_differ_per_encoder": arms_differ_per_enc,
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke gate (META_RULE_AX + META_RULE_AP)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    per_enc = body.get("per_encoder_summary", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, (
            f"cardinality_breach: expected {expected_n} got {len(phase_map)}"
        )

    # 2. arms_differ for ALL encoders (TD vs RD distinct per encoder)
    for fam in ENCODER_FAMILIES:
        ad = arms_differ.get(fam, {})
        if not ad.get("differ"):
            return False, (
                f"arms_identical_encoder_{fam}: TD and RD per-encoder hashes match"
            )

    # 3. META_RULE_AX: cross-encoder pair distinctness >= HP_MIN_PAIRS_DIFFER
    n_pairs_total = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < HP_MIN_PAIRS_DIFFER:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (
            f"HARD_FAIL_DEGENERATE_ENCODERS (META_RULE_AX): "
            f"{n_distinct}/{n_pairs_total} encoder pairs differ "
            f"(need >= {HP_MIN_PAIRS_DIFFER}); collapsed pairs: {collapsed}"
        )

    # 4. Positive control
    if not pc_result.get("pass"):
        return False, (
            f"positive_control_fail: target={pc_result.get('target')} "
            f"outcome={pc_result.get('measured_outcome')} "
            f"recency={pc_result.get('measured_recency_decode_acc')}"
        )

    # 5. META_RULE_AP: per-encoder recency_decode_acc floor >= HP_RECENCY_DECODE_FLOOR
    failing_decode = {}
    for fam in ENCODER_FAMILIES:
        rda = per_enc.get(fam, {}).get("recency_decode_acc_mean", 0.0)
        if rda < HP_RECENCY_DECODE_FLOOR:
            failing_decode[fam] = rda
    if failing_decode:
        return False, (
            f"HARD_FAIL_READOUT_FLOOR (META_RULE_AP): per-encoder "
            f"recency_decode_acc_mean below {HP_RECENCY_DECODE_FLOOR}: "
            f"{failing_decode}; chain-grade gate requires working readout"
        )

    # 6. Discriminator-fires: >= 2 encoders show dominance_rate >= 0.50 at smoke
    fams_above = [fam for fam in ENCODER_FAMILIES
                   if per_enc.get(fam, {}).get("dominance_rate", 0.0) >= 0.50]
    if len(fams_above) < 2:
        rates = {fam: per_enc.get(fam, {}).get("dominance_rate", 0.0)
                  for fam in ENCODER_FAMILIES}
        return False, (
            f"discriminator_fails_scale: only {len(fams_above)} encoders show "
            f"dominance_rate >= 0.50 at smoke; rates={rates}"
        )

    return True, (
        f"smoke_gate_pass_v3: cardinality_ok + arms_differ(5 enc) + "
        f"pairs_differ={n_distinct}/{n_pairs_total} >= {HP_MIN_PAIRS_DIFFER} + "
        f"positive_control_pass + readout_floor_ok + "
        f">=2 encoders above dominance_floor"
    )


# ---------------------------------------------------------------------------
# Aggregate + verdict
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
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    n_pairs_total = body.get("n_pairs_total", 10)
    pc_result = body.get("positive_control_result", {})
    per_enc_summary = body.get("per_encoder_summary", {})
    encoder_tiers = body.get("encoder_tiers", {})
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    outcomes = [p["pareto_outcome"] for p in phase_map]
    n_td = sum(1 for o in outcomes if o == "TD_DOMINATES")
    n_rd = sum(1 for o in outcomes if o == "RD_DOMINATES")
    n_tie = sum(1 for o in outcomes if o == "TIE")

    n_total = len(phase_map)
    overall_dom_rate = (n_td + 0.5 * n_tie) / max(n_total, 1)
    overall_net = (n_td - n_rd) / max(n_total, 1)
    overall_rd_loss = n_rd / max(n_total, 1)

    # Per-encoder chain-grade (v2 thresholds + META_RULE_AP readout floor)
    enc_chain_grade: Dict[str, bool] = {}
    for fam in ENCODER_FAMILIES:
        s = per_enc_summary.get(fam, {})
        passes = (
            s.get("dominance_rate", 0.0) >= HP_DOMINANCE_RATE_LO
            and s.get("net_dominance", 0.0) >= HP_NET_DOMINANCE_LO
            and s.get("rd_loss_rate", 1.0) <= HP_RD_LOSS_RATE_HI
            and s.get("recency_decode_acc_mean", 0.0) >= HP_RECENCY_DECODE_FLOOR
        )
        enc_chain_grade[fam] = passes
    n_chain_grade = sum(1 for v in enc_chain_grade.values() if v)

    common = {
        "phase_map": phase_map,
        "per_encoder_summary": per_enc_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "n_pairs_total": n_pairs_total,
        "arms_differ_per_encoder": arms_differ,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "pareto_outcome_counts": {
            "TD_DOMINATES": n_td, "RD_DOMINATES": n_rd, "TIE": n_tie},
        "overall_dominance_rate": round(overall_dom_rate, 4),
        "overall_net_dominance": round(overall_net, 4),
        "overall_rd_loss_rate": round(overall_rd_loss, 4),
        "per_encoder_chain_grade_pass": enc_chain_grade,
        "n_encoders_chain_grade": n_chain_grade,
        "N_DIM_sweep": body.get("dim_sweep"),
        "R_BUCKETS": body.get("R_BUCKETS"),
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (
                f"HARD_PASS_SMOKE_v3: {observed_n}/{expected_n} pts; "
                f"td_wins={n_td}/{n_total} rd_wins={n_rd}/{n_total} "
                f"ties={n_tie}/{n_total}; "
                f"overall_dom={overall_dom_rate:.3f}; "
                f"pairs_differ={n_pairs_differ}/{n_pairs_total}; "
                f"positive_control@"
                f"{pc_result.get('target', {}).get('encoder_family')} "
                f"outcome={pc_result.get('measured_outcome')} "
                f"rec={pc_result.get('measured_recency_decode_acc'):.3f}; "
                f"encoder_tiers={encoder_tiers}; "
                f"n_encoders_chain_grade={n_chain_grade}/5"
            )
        else:
            verdict = "HARD_FAIL"
            vmsg = (
                f"HARD_FAIL_SMOKE_v3: {reason}; "
                f"td_wins={n_td} rd_wins={n_rd} ties={n_tie}"
            )
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
    elif any(not ad.get("differ") for ad in arms_differ.values()):
        bad = [fam for fam in ENCODER_FAMILIES
               if not arms_differ.get(fam, {}).get("differ")]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_ARMS_IDENTICAL: encoders with TD==RD: {bad}"
    elif n_pairs_differ < HP_MIN_PAIRS_DIFFER:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_DEGENERATE_ENCODERS (META_RULE_AX): "
            f"{n_pairs_differ}/{n_pairs_total} pairs differ "
            f"(need >= {HP_MIN_PAIRS_DIFFER}); collapsed: {collapsed}"
        )
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_CONTROL_FAIL: positive_control "
            f"outcome={pc_result.get('measured_outcome')} "
            f"recency={pc_result.get('measured_recency_decode_acc')}"
        )
    elif n_chain_grade >= 2 and overall_dom_rate >= HP_DOMINANCE_RATE_LO:
        # v3 stricter: require >= 2 encoders to clear chain-grade (Skunkworks
        # caught v1 sparse_seed_13 as by-construction; adding readout floor
        # forces real readout; requiring >= 2 prevents single-encoder pass).
        verdict = "HARD_PASS"
        vmsg = (
            f"HARD_PASS_ENCODER_DISCRIMINATION_v3: {observed_n}/{expected_n} pts; "
            f"{n_chain_grade}/5 encoders pass v2-PB+AP chain-grade "
            f"(dom>={HP_DOMINANCE_RATE_LO}, net>={HP_NET_DOMINANCE_LO}, "
            f"rd_loss<={HP_RD_LOSS_RATE_HI}, "
            f"rec>={HP_RECENCY_DECODE_FLOOR}); "
            f"overall_dom={overall_dom_rate:.3f}; "
            f"pairs_differ={n_pairs_differ}/{n_pairs_total}; "
            f"encoder_tiers={encoder_tiers}; positive_control_pass"
        )
    elif overall_dom_rate >= 0.60 and n_pairs_differ >= HP_MIN_PAIRS_DIFFER:
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_ENCODER_DIFFERS_BUT_LOW_CHAIN_GRADE: encoders "
            f"distinguish ({n_pairs_differ}/{n_pairs_total}) but only "
            f"{n_chain_grade}/5 clear chain-grade; "
            f"overall_dom={overall_dom_rate:.3f}; tiers={encoder_tiers}"
        )
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_LOW_DISCRIMINATION: overall_dom="
            f"{overall_dom_rate:.3f}; pairs_differ={n_pairs_differ}; "
            f"n_chain_grade={n_chain_grade}/5"
        )

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ENCODER_FAMILIES",
    "DECAY_RATE_DAYS_FULL", "CAPACITY_LOAD_RATIO_FULL", "N_DIM_SWEEP_FULL",
    "DECAY_RATE_DAYS_SMOKE", "CAPACITY_LOAD_RATIO_SMOKE", "N_DIM_SWEEP_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "N_ATOMS_BASE", "N_DAYS_SIM", "N_DIM_DEFAULT",
    "R_BUCKETS",
    "HP_DOMINANCE_RATE_LO", "HP_NET_DOMINANCE_LO", "HP_RD_LOSS_RATE_HI",
    "HP_RECENCY_DECODE_FLOOR", "HP_MIN_PAIRS_DIFFER",
    "POSITIVE_CONTROL", "REQUIRED_FIELDS",
    "_get_device", "get_backend_label",
    "simulate_atom_timeline", "build_encoded_atom_store",
    "decode_recency_buckets", "arm_time_decay_via_encoder",
    "arm_random_eviction",
    "compute_arm_metrics", "pareto_dominance_outcome", "eval_phase_point",
    "selftest", "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
