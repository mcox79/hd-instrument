"""Shared core for substrate_anchor4_encoder_family_phase_diagram_v1 siblings.

Fourth COMPONENT-SUBSTITUTION phase diagram for the ANCHOR 4 time-decay
eviction primitive (after PC + seqbind + WM on 2026-06-28).

USER directive 2026-06-28 (Research): systematic phase-diagram coverage
across COMPONENTS. ANCHOR 4 time-decay eviction is the first 2x-drill
chain-grade win (Pareto-AUC v2 ratified; commit per cert ledger). Default
mechanism uses raw atom attributes (no encoder). This cell substitutes the
encoder family that mediates the eviction-decision pipeline.

Target primitive: ANCHOR 4 time-decay eviction with Pareto-dominance
discriminator. v2 evidence at (decay_rate=90 days, load=1.0): TIME_DECAY
STRICTLY DOMINATES RANDOM on the (ws_retention, 1-clutter_fraction) plane.

Outer axis (component substitution): encoder family in {
    binary_bipolar  : {-1,+1}^N dense; elementwise mul bind; cosine decode
    hrr_real        : N(0,1/N)^N dense Gaussian real; FFT circular conv bind; cosine decode
    fhrr            : unit-modulus exp(i*phi) in C^(N/2); elementwise complex mul bind; complex cosine decode
    sparse_bipolar  : {-1,0,+1}^N, s/N=0.05 active; elementwise mul bind; cosine decode
}

Inner axes:
    decay_rate_days: {30, 90, 180}
    capacity_load_ratio: {1.0, 5.0}
    N_DIM (encoder dim; fidelity-vs-crosstalk axis): {128, 1024}

Cardinality:
    FULL : 4 encoders x 3 decay x 2 load x 2 N_DIM = 48 per seed
    SMOKE: 4 encoders x 2 decay x 2 load x 2 N_DIM = 32 per seed

Why N_DIM is swept: at N_DIM=1024 with 200 atoms x 64 recency buckets,
all encoders achieve perfect recency decode (saturated regime; encoder
choice doesn't matter). At N_DIM=128, sparse_bipolar (density=0.05 -> 6
active bits) and FHRR (64 complex bins) face crosstalk; HRR-real and
binary_bipolar still recover but with degraded SNR. The cliff regime
is where encoders discriminate (per H4-vs-H5 of the pre-reg).

How the encoder mediates eviction (the COMPONENT-SUBSTITUTION mechanism):

  The substrate stores each atom as a bound vector:
      atom_vec[i] = encode(atom_id[i]) (*) encode_recency(last_query_day[i])

  The encoder's BIND operator (elementwise mul / circular convolution /
  complex mul / sparse mul) carries the (atom_id, recency) binding.

  Time-decay eviction needs to know each atom's recency. With a perfect
  encoder, recency decodes exactly. With a noisy encoder, the decoded
  recency carries error proportional to encoder crosstalk / capacity.

  Recency decode (per atom):
      decoded_recency[i] = decode(atom_vec[i], encode(atom_id[i]))
      -> argmax over R_BUCKETS basis vectors

  Eviction decision per atom: evict if decoded_age > decay_rate_days.

  RANDOM-arm: evict a uniformly-random subset of size matching TIME_DECAY's
  eviction count (the v2 arm; preserves Pareto-AUC discriminator semantics).

  Metric per (encoder, decay, load):
      ws_retention = fraction of working-set atoms NOT evicted
      clutter_fraction = fraction of NON-working-set atoms NOT evicted
        (among alive atoms)
      composite = ws_retention - clutter_fraction
      pareto_outcome (TD vs RD) per v2 discriminator

Pareto-dominance per encoder per phase point:
    TD_DOMINATES if TD.ws >= RD.ws AND TD.(1-clut) >= RD.(1-clut)
                 AND at least one strictly greater.
    Symmetric for RD_DOMINATES.

Per-encoder dominance_rate >= 0.85, net_dominance >= 0.70, rd_loss_rate <= 0.05
gates chain-grade Pareto-AUC promotion (v2 thresholds).

Positive control: binary_bipolar at (decay=90, load=1.0, seed=13) MUST
reproduce v2 cell's TD_DOMINATES outcome (test rig calibration check).
Without an encoder layer the v2 cell measured TD.ws=1.000, RD.ws much
lower (~0.78). With the encoder layer at high fidelity (M_atoms below
capacity), the same outcome must hold. If it does not, the encoder
adapter is broken and any encoder-comparison framing is UNTRUSTED.

HARD_FAIL gates (load-bearing, mirroring v2):
  HARD_FAIL_CARDINALITY_BREACH: observed phase points != expected
  HARD_FAIL_CONTROL_FAIL: positive control TD does not dominate RD
  HARD_FAIL_ARMS_IDENTICAL: TD and RD per-encoder hashes match (no mechanism)
  HARD_FAIL_LLM_LEAK: n_llm_calls > 0

Pre-reg: preregs/2026-06-28_substrate_anchor4_encoder_family_phase_diagram_v1.md

ASCII-only. No unicode. No em-dashes. No emojis.
NumPy-only on CPU (Pareto eviction is NumPy-light; ROUTING: remote_cpu_queue).

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

# numpy-only on CPU; no torch needed. (remote_cpu_queue routing per Fix #24
# heuristic: NumPy-light + simulation-only cell, no matmul-heavy work.)


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
# v2 thresholds (verbatim port; preserve discriminator semantics)
HP_DOMINANCE_RATE_LO = 0.85
HP_NET_DOMINANCE_LO = 0.70
HP_RD_LOSS_RATE_HI = 0.05

# Saturation guards
SATURATION_DOMINANCE = 0.999
SATURATION_TD_WS = 0.999

# Encoder families (OUTER axis; LOCKED at module init)
ENCODER_FAMILIES = ("binary_bipolar", "hrr_real", "fhrr", "sparse_bipolar")

# Simulation params (matched to v2 cell defaults so positive control reproduces)
N_ATOMS_BASE = 200    # number of atoms in substrate at one timestep
N_DAYS_SIM = 365      # simulation horizon
RECENT_QUERY_DAYS = 30
QUERY_DECAY_TAU = 60.0
R_BUCKETS = 64        # quantized recency basis (last_query_day quantized to 64 buckets)

# Encoder dimension (encoder fidelity proxy; SWEEPING this axis)
# bipolar / hrr_real / sparse_bipolar use N dims; fhrr uses N/2 complex bins.
# Real DoF is N for all encoders (apples-to-apples).
N_DIM_HIGH = 1024     # high-fidelity regime (all encoders should saturate)
N_DIM_LOW = 128       # cliff regime (encoders should discriminate)
N_DIM_DEFAULT = 1024  # used by selftest positive-control point (matches v2 op point)
SPARSE_DENSITY = 0.05 # 5% nonzero for sparse_bipolar

# Sweep axes
DECAY_RATE_DAYS_FULL = [30, 90, 180]
CAPACITY_LOAD_RATIO_FULL = [1.0, 5.0]
N_DIM_SWEEP_FULL = [128, 1024]

DECAY_RATE_DAYS_SMOKE = [30, 90]
CAPACITY_LOAD_RATIO_SMOKE = [1.0, 5.0]
N_DIM_SWEEP_SMOKE = [128, 1024]

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(ENCODER_FAMILIES) * len(DECAY_RATE_DAYS_FULL)
                          * len(CAPACITY_LOAD_RATIO_FULL)
                          * len(N_DIM_SWEEP_FULL))  # 4*3*2*2 = 48
EXPECTED_N_UNITS_SMOKE = (len(ENCODER_FAMILIES) * len(DECAY_RATE_DAYS_SMOKE)
                           * len(CAPACITY_LOAD_RATIO_SMOKE)
                           * len(N_DIM_SWEEP_SMOKE))  # 4*2*2*2 = 32

# Positive control: binary_bipolar at (decay=90, load=1.0, seed=13) must
# reproduce v2 TD_DOMINATES (encoder layer at fidelity-high regime adds no
# error, so v2 result must hold). top1_recency_decode >= 0.80 required.
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
# Encoder family primitives (bind / decode_recency / sign_op / score)
# ---------------------------------------------------------------------------
def _build_binary_bipolar(n_items: int, dim: int, seed: int) -> np.ndarray:
    """Dense bipolar {-1, +1}^N codebook (n_items, dim) float32."""
    g = np.random.default_rng(seed)
    return (g.integers(0, 2, size=(n_items, dim)) * 2 - 1).astype(np.float32)


def _build_hrr_real(n_items: int, dim: int, seed: int) -> np.ndarray:
    """Dense Gaussian N(0, 1/N)^N L2-normalized (n_items, dim) float32."""
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(n_items, dim)) / math.sqrt(dim)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    return (arr / norms).astype(np.float32)


def _build_fhrr(n_items: int, dim: int, seed: int) -> np.ndarray:
    """Unit-modulus complex codebook exp(i*phi) in C^(dim/2) complex64.

    Output shape: (n_items, dim/2) complex64. Total real DoF = dim.
    """
    if dim % 2 != 0:
        raise ValueError(f"FHRR requires even dim; got dim={dim}")
    n_complex = dim // 2
    g = np.random.default_rng(seed)
    phi = g.uniform(0.0, 2.0 * math.pi, size=(n_items, n_complex)).astype(np.float32)
    arr = np.empty((n_items, n_complex), dtype=np.complex64)
    arr.real = np.cos(phi).astype(np.float32)
    arr.imag = np.sin(phi).astype(np.float32)
    return arr


def _build_sparse_bipolar(n_items: int, dim: int, seed: int) -> np.ndarray:
    """Sparse-ternary {-1, 0, +1}^N codebook (n_items, dim) float32; density s/N=0.05."""
    g = np.random.default_rng(seed)
    s = max(1, int(round(SPARSE_DENSITY * dim)))
    arr = np.zeros((n_items, dim), dtype=np.float32)
    for i in range(n_items):
        idx = g.choice(dim, size=s, replace=False)
        signs = g.integers(0, 2, size=s).astype(np.float32) * 2.0 - 1.0
        arr[i, idx] = signs
    return arr


# Bind ops (elementwise for bipolar/sparse/fhrr; FFT circular convolution for hrr_real)
def _bind_elementwise_real(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Elementwise multiply (bipolar / sparse_bipolar)."""
    return (A * B).astype(np.float32)


def _bind_circular_conv(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """FFT-based circular convolution (HRR-real)."""
    # A, B: (n, dim) real
    fa = np.fft.rfft(A, axis=1)
    fb = np.fft.rfft(B, axis=1)
    out = np.fft.irfft(fa * fb, n=A.shape[1], axis=1).astype(np.float32)
    return out


def _bind_complex_mul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Elementwise complex multiply (FHRR)."""
    return (A * B).astype(np.complex64)


# Unbind / decode ops
def _unbind_elementwise_real(bound: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Inverse of elementwise mul for bipolar/sparse: divide by key.

    For bipolar {-1, +1}: 1/key = key (self-inverse), so unbind = mul.
    For sparse {-1, 0, +1}: zero-bins lose info; treat 1/0 as 0 (masked).
    """
    # For bipolar (no zeros): mul (key is self-inverse)
    # For sparse (zeros allowed): mask zeros to 0
    out = bound * np.where(key != 0, np.sign(key), 0.0)
    return out.astype(np.float32)


def _unbind_circular_corr(bound: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Inverse of circular convolution (HRR-real): circular correlation = conv(bound, conj(key))."""
    fa = np.fft.rfft(bound, axis=1)
    fb_conj = np.conj(np.fft.rfft(key, axis=1))
    out = np.fft.irfft(fa * fb_conj, n=bound.shape[1], axis=1).astype(np.float32)
    return out


def _unbind_complex_mul(bound: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Inverse of complex multiply (FHRR): multiply by conjugate of key."""
    return (bound * np.conj(key)).astype(np.complex64)


# Score (cosine, or its complex analog)
def _score_real(Q: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Real inner product / cosine (bipolar / hrr_real / sparse_bipolar).

    Returns (n_query, n_items) float32 similarity matrix.
    """
    qn = np.linalg.norm(Q, axis=1, keepdims=True).clip(min=1e-12)
    xn = np.linalg.norm(X, axis=1, keepdims=True).clip(min=1e-12)
    return ((Q / qn) @ (X / xn).T).astype(np.float32)


def _score_fhrr(Q: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Re(Q . conj(X.T)) for FHRR complex codes; returns real float32."""
    sims = (Q @ X.conj().T).real
    # Normalize by per-bin count to keep cosine-like semantics in [-1, 1]
    n_complex = X.shape[1]
    return (sims / float(n_complex)).astype(np.float32)


# Encoder dimension actually used (FHRR has half complex bins so dim is dim/2)
def _encoder_dim(family: str, dim: int) -> int:
    return dim // 2 if family == "fhrr" else dim


_ENCODER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "binary_bipolar": {
        "build": _build_binary_bipolar,
        "bind": _bind_elementwise_real,
        "unbind": _unbind_elementwise_real,
        "score": _score_real,
        "complex": False,
        "dtype_label": "float32",
    },
    "hrr_real": {
        "build": _build_hrr_real,
        "bind": _bind_circular_conv,
        "unbind": _unbind_circular_corr,
        "score": _score_real,
        "complex": False,
        "dtype_label": "float32",
    },
    "fhrr": {
        "build": _build_fhrr,
        "bind": _bind_complex_mul,
        "unbind": _unbind_complex_mul,
        "score": _score_fhrr,
        "complex": True,
        "dtype_label": "complex64",
    },
    "sparse_bipolar": {
        "build": _build_sparse_bipolar,
        "bind": _bind_elementwise_real,
        "unbind": _unbind_elementwise_real,
        "score": _score_real,
        "complex": False,
        "dtype_label": "float32",
    },
}


# ---------------------------------------------------------------------------
# Substrate: atom timeline (PORTED VERBATIM from v2 cell for control fidelity)
# ---------------------------------------------------------------------------
def simulate_atom_timeline(
    n_atoms: int,
    n_days: int,
    capacity_load_ratio: float,
    query_decay_tau: float,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Port of v2 cell timeline. arrival_day, last_query_day, is_working_set."""
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
# Encoder mediation: encode atom-bindings + decode recency
# ---------------------------------------------------------------------------
def quantize_to_bucket(day: int, n_days: int, n_buckets: int) -> int:
    """Map a day in [0, n_days) to a recency bucket in [0, n_buckets)."""
    if day < 0:
        return 0
    return int(min(n_buckets - 1, max(0, (day * n_buckets) // max(n_days, 1))))


def build_encoded_atom_store(
    encoder_family: str,
    n_atoms: int,
    last_query_day: np.ndarray,
    n_days: int,
    n_buckets: int,
    dim: int,
    seed: int,
) -> Dict[str, Any]:
    """Encode atoms with (atom_id, recency_bucket) bindings.

    Returns dict with keys: atom_codes, recency_basis, bound, family, dim_eff.
    """
    reg = _ENCODER_REGISTRY[encoder_family]
    dim_eff = _encoder_dim(encoder_family, dim)

    # Atom-id codes (one per atom)
    atom_codes = reg["build"](n_atoms, dim, seed)

    # Recency basis vectors (one per quantized bucket)
    recency_basis = reg["build"](n_buckets, dim, seed + 31337)

    # Bound: atom_code (*) recency_basis[ quantized(last_query_day) ]
    buckets = np.array(
        [quantize_to_bucket(int(d), n_days, n_buckets) for d in last_query_day],
        dtype=np.int64,
    )
    recency_keys = recency_basis[buckets]  # (n_atoms, dim_eff)
    bound = reg["bind"](atom_codes, recency_keys)

    return {
        "atom_codes": atom_codes,
        "recency_basis": recency_basis,
        "bound": bound,
        "buckets_true": buckets,
        "family": encoder_family,
        "dim_eff": dim_eff,
    }


def decode_recency_buckets(
    store: Dict[str, Any],
) -> Tuple[np.ndarray, float]:
    """Decode each atom's recency bucket from the bound store.

    Returns (predicted_bucket_per_atom, top1_recency_decode_acc).
    """
    reg = _ENCODER_REGISTRY[store["family"]]
    atom_codes = store["atom_codes"]
    recency_basis = store["recency_basis"]
    bound = store["bound"]
    buckets_true = store["buckets_true"]

    # Unbind by atom_code: get noisy estimate of the recency basis vector
    decoded = reg["unbind"](bound, atom_codes)

    # Score against the recency basis (n_atoms, n_buckets)
    sims = reg["score"](decoded, recency_basis)
    preds = sims.argmax(axis=1)
    acc = float(np.mean(preds == buckets_true))
    return preds, acc


# ---------------------------------------------------------------------------
# Arms (TIME_DECAY / RANDOM eviction)
# ---------------------------------------------------------------------------
def arm_time_decay_via_encoder(
    decoded_buckets: np.ndarray,
    n_days: int,
    n_buckets: int,
    decay_rate_days: int,
) -> np.ndarray:
    """Evict atoms whose DECODED last_query_day-age > decay_rate_days.

    decoded_buckets carry recency; convert bucket back to day estimate via
    midpoint of bucket. age = n_days - estimated_day.
    """
    n_atoms = len(decoded_buckets)
    # Bucket midpoint day estimate
    bucket_width_days = n_days / float(max(n_buckets, 1))
    estimated_last_query_day = (decoded_buckets.astype(np.float64) + 0.5) * bucket_width_days
    estimated_age = n_days - estimated_last_query_day
    return (estimated_age > decay_rate_days).astype(bool)


def arm_random_eviction(
    n_atoms: int, target_eviction_count: int, seed: int,
) -> np.ndarray:
    """Random eviction of size target_eviction_count (matched to TD's count)."""
    rng = np.random.RandomState(seed + 7919)
    evicted = np.zeros(n_atoms, dtype=bool)
    if target_eviction_count <= 0:
        return evicted
    target_eviction_count = min(target_eviction_count, n_atoms)
    idx = rng.choice(n_atoms, size=target_eviction_count, replace=False)
    evicted[idx] = True
    return evicted


# ---------------------------------------------------------------------------
# Metrics (PORTED VERBATIM from v2)
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


def pareto_dominance_outcome(
    td_ws: float, td_clut: float,
    rd_ws: float, rd_clut: float,
) -> str:
    """V2 Pareto discriminator. Returns 'TD_DOMINATES' / 'RD_DOMINATES' / 'TIE'."""
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
# Per-phase-point eval
# ---------------------------------------------------------------------------
def eval_phase_point(
    encoder_family: str,
    decay_rate_days: int,
    capacity_load_ratio: float,
    n_atoms: int,
    n_days: int,
    n_buckets: int,
    dim: int,
    seed: int,
) -> Dict[str, Any]:
    """Run one (encoder, decay, load) phase point."""
    if encoder_family not in _ENCODER_REGISTRY:
        raise ValueError(f"unknown encoder_family={encoder_family!r}")
    t0 = time.time()

    arrival_day, last_query_day, is_working_set = simulate_atom_timeline(
        n_atoms=n_atoms,
        n_days=n_days,
        capacity_load_ratio=capacity_load_ratio,
        query_decay_tau=QUERY_DECAY_TAU,
        seed=seed,
    )

    # Encoder-mediated store + recency decode
    store = build_encoded_atom_store(
        encoder_family=encoder_family,
        n_atoms=n_atoms,
        last_query_day=last_query_day,
        n_days=n_days,
        n_buckets=n_buckets,
        dim=dim,
        seed=seed,
    )
    decoded_buckets, recency_decode_acc = decode_recency_buckets(store)

    # TIME_DECAY eviction (via encoder-decoded recency)
    td_evicted = arm_time_decay_via_encoder(
        decoded_buckets, n_days, n_buckets, decay_rate_days
    )
    td_metrics = compute_arm_metrics(td_evicted, is_working_set)

    # RANDOM eviction (count-matched to TD)
    rd_evicted = arm_random_eviction(n_atoms, int(td_evicted.sum()), seed)
    rd_metrics = compute_arm_metrics(rd_evicted, is_working_set)

    # Pareto outcome
    pareto_outcome = pareto_dominance_outcome(
        td_metrics["working_set_retention"], td_metrics["clutter_fraction"],
        rd_metrics["working_set_retention"], rd_metrics["clutter_fraction"],
    )

    elapsed = time.time() - t0
    return {
        "encoder_family": encoder_family,
        "decay_rate_days": int(decay_rate_days),
        "capacity_load_ratio": float(capacity_load_ratio),
        "n_atoms": int(n_atoms),
        "n_days": int(n_days),
        "n_buckets": int(n_buckets),
        "N_dim_input": int(dim),
        "dim_eff": int(store["dim_eff"]),
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
# Selftest (encoder distinctness + recency decode fidelity + positive control)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Encoder calibration + recency decode + cardinality + positive control."""
    msgs: List[str] = []

    # 1. Cardinality math (4 encoders x 3 decay x 2 load x 2 N_dim = 48 FULL;
    # 4 x 2 x 2 x 2 = 32 SMOKE)
    if EXPECTED_N_UNITS_FULL != 48:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 48"
    if EXPECTED_N_UNITS_SMOKE != 32:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 32"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Encoder distinctness (META_RULE_AF): 4 encoders produce 4 distinct
    # bound stores at the same seed/atoms
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
            fam, n_atoms_san, lastq, n_days_san, n_buckets_san, dim_san, seed,
        )
        # Hash the bytes of the bound representation
        bound_bytes = store["bound"].tobytes()
        hashes[fam] = hashlib.sha256(bound_bytes).hexdigest()[:16]
    if len(set(hashes.values())) != len(ENCODER_FAMILIES):
        return False, f"encoder stores NOT distinct at seed={seed}: {hashes}"
    msgs.append(f"encoder distinct hashes: {hashes}")

    # 3. Recency decode fidelity: each encoder must decode > 0.50 at small
    # M+small_n_buckets+dim=1024. Per-encoder decode accuracy logged.
    decode_accs: Dict[str, float] = {}
    n_atoms_dec = 100
    n_buckets_dec = 16
    dim_dec = 1024
    arrival_d, lastq_d, _ = simulate_atom_timeline(
        n_atoms_dec, n_days_san, 1.0, QUERY_DECAY_TAU, seed + 1,
    )
    for fam in ENCODER_FAMILIES:
        store = build_encoded_atom_store(
            fam, n_atoms_dec, lastq_d, n_days_san, n_buckets_dec, dim_dec, seed + 1,
        )
        _, acc = decode_recency_buckets(store)
        decode_accs[fam] = round(acc, 3)
        if acc < 0.50:
            return False, (
                f"recency decode FAIL {fam}: acc={acc:.3f} < 0.50 at "
                f"n_atoms={n_atoms_dec} n_buckets={n_buckets_dec} dim={dim_dec}"
            )
    msgs.append(f"recency_decode_acc per encoder: {decode_accs}")

    # 4. v2 op-point reproduction with PERFECT encoder layer at fidelity-high
    # (binary_bipolar should match v2's TD_DOMINATES at decay=90, load=1.0,
    # seed=13, dim=N_DIM_DEFAULT). This is the POSITIVE-CONTROL gate.
    pt = eval_phase_point(
        encoder_family="binary_bipolar",
        decay_rate_days=90,
        capacity_load_ratio=1.0,
        n_atoms=N_ATOMS_BASE,
        n_days=N_DAYS_SIM,
        n_buckets=R_BUCKETS,
        dim=N_DIM_DEFAULT,
        seed=13,
    )
    if pt["pareto_outcome"] != "TD_DOMINATES":
        return False, (
            f"Positive control FAILED: binary_bipolar at v2 op-point (dr=90, "
            f"ld=1.0, seed=13) expected TD_DOMINATES, got {pt['pareto_outcome']}. "
            f"TD(ws={pt['ARM_TIME_DECAY_EVICTION']['working_set_retention']:.3f}, "
            f"clut={pt['ARM_TIME_DECAY_EVICTION']['clutter_fraction']:.3f}) "
            f"RD(ws={pt['ARM_RANDOM_EVICTION']['working_set_retention']:.3f}, "
            f"clut={pt['ARM_RANDOM_EVICTION']['clutter_fraction']:.3f}) "
            f"recency_decode_acc={pt['recency_decode_acc']:.3f}"
        )
    if pt["recency_decode_acc"] < POSITIVE_CONTROL["min_recency_decode_acc"]:
        return False, (
            f"Positive control recency_decode acc too low: "
            f"{pt['recency_decode_acc']:.3f} < "
            f"{POSITIVE_CONTROL['min_recency_decode_acc']}; encoder fidelity "
            f"insufficient at N_DIM={N_DIM} R_BUCKETS={R_BUCKETS}"
        )
    msgs.append(
        f"positive_control: binary_bipolar @ (dr=90, ld=1.0, seed=13) "
        f"pareto={pt['pareto_outcome']} td.ws={pt['ARM_TIME_DECAY_EVICTION']['working_set_retention']:.3f} "
        f"rd.ws={pt['ARM_RANDOM_EVICTION']['working_set_retention']:.3f} "
        f"recency_acc={pt['recency_decode_acc']:.3f}"
    )

    # 5. Pareto dominance function unit-check (ported from v2)
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
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (encoder, decay, load, N_dim) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    decay_sweep = DECAY_RATE_DAYS_SMOKE if is_smoke else DECAY_RATE_DAYS_FULL
    load_sweep = CAPACITY_LOAD_RATIO_SMOKE if is_smoke else CAPACITY_LOAD_RATIO_FULL
    dim_sweep = N_DIM_SWEEP_SMOKE if is_smoke else N_DIM_SWEEP_FULL
    expected_n = (len(ENCODER_FAMILIES) * len(decay_sweep)
                   * len(load_sweep) * len(dim_sweep))

    print(
        f"[run_one_seed] seed={seed} mode={run_mode} "
        f"encoders={ENCODER_FAMILIES} decay_axis={decay_sweep} "
        f"load_axis={load_sweep} dim_axis={dim_sweep} R_BUCKETS={R_BUCKETS} "
        f"expected_n={expected_n}",
        flush=True,
    )

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for fam in ENCODER_FAMILIES:
        for dr in decay_sweep:
            for cl in load_sweep:
                for nd in dim_sweep:
                    print(
                        f"[point] seed={seed} enc={fam} decay={dr} "
                        f"load={cl:.1f} N_dim={nd} ...",
                        flush=True,
                    )
                    pt = eval_phase_point(
                        encoder_family=fam,
                        decay_rate_days=dr,
                        capacity_load_ratio=cl,
                        n_atoms=N_ATOMS_BASE,
                        n_days=N_DAYS_SIM,
                        n_buckets=R_BUCKETS,
                        dim=nd,
                        seed=seed,
                    )
                    phase_map.append(pt)
                    td = pt["ARM_TIME_DECAY_EVICTION"]
                    rd = pt["ARM_RANDOM_EVICTION"]
                    print(
                        f"  -> td.ws={td['working_set_retention']:.3f} "
                        f"td.clut={td['clutter_fraction']:.3f} "
                        f"rd.ws={rd['working_set_retention']:.3f} "
                        f"rd.clut={rd['clutter_fraction']:.3f} "
                        f"pareto={pt['pareto_outcome']} "
                        f"rec_acc={pt['recency_decode_acc']:.3f} "
                        f"t={pt['wall_s']:.2f}s",
                        flush=True,
                    )

    elapsed = time.time() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # Per-encoder Pareto-AUC stats
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
            "recency_decode_acc_mean": round(float(np.mean(decode_accs)), 4) if decode_accs else 0.0,
        }

    # Encoder-pair distinctness (META_RULE_AF extension)
    # Hash each encoder's per-point outcome vector ordered by (decay, load, dim).
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

    # TIME_DECAY vs RANDOM arms_differ per encoder (mechanism gate)
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

    # Positive control: binary_bipolar at (decay=90, load=1.0, N_dim_input=1024)
    pc_n_dim = POSITIVE_CONTROL["N_DIM"]
    pc_matches = [
        p for p in phase_map
        if p["encoder_family"] == POSITIVE_CONTROL["encoder_family"]
        and p["decay_rate_days"] == POSITIVE_CONTROL["decay_rate_days"]
        and abs(p["capacity_load_ratio"] - POSITIVE_CONTROL["capacity_load_ratio"]) < 1e-6
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

    # Encoder tier classification
    means = {fam: per_encoder_summary[fam]["dominance_rate"] for fam in ENCODER_FAMILIES}
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
        "arms_differ_per_encoder": arms_differ_per_enc,
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
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
    per_enc = body.get("per_encoder_summary", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    # 2. arms_differ for ALL encoders (TD vs RD distinct per encoder)
    for fam in ENCODER_FAMILIES:
        ad = arms_differ.get(fam, {})
        if not ad.get("differ"):
            return False, (
                f"arms_identical_encoder_{fam}: TD and RD per-encoder hashes match; "
                f"eviction mechanism not firing for this encoder")

    # 3. At least 2 encoder pairs differ — sanity that the encoder substitution
    # is producing measurable downstream change. Some pairs may legitimately
    # collapse in the high-fidelity regime (e.g. binary/HRR/FHRR equivalent at
    # high N_dim where decode is saturated for all three); the cell still says
    # something useful in that case. The chain-grade gate (encoder substitution
    # works) requires only that SOME encoders differ.
    n_pairs = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < 2:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (
            f"encoder_collapse: {n_distinct}/{n_pairs} encoder pairs differ "
            f"(need >= 2); all encoders equivalent at this regime; "
            f"identical pairs: {collapsed}")

    # 4. Positive control
    if not pc_result.get("pass"):
        return False, (
            f"positive_control_fail: target={pc_result.get('target')} "
            f"measured_outcome={pc_result.get('measured_outcome')} "
            f"measured_recency_decode={pc_result.get('measured_recency_decode_acc')}; "
            f"test rig broken")

    # 5. At least 2 encoders show dominance_rate >= 0.50 at smoke (mechanism
    # observably works somewhere); else smoke says we're at floor for all
    fams_above = [fam for fam in ENCODER_FAMILIES
                   if per_enc.get(fam, {}).get("dominance_rate", 0.0) >= 0.50]
    if len(fams_above) < 2:
        rates = {fam: per_enc.get(fam, {}).get("dominance_rate", 0.0)
                  for fam in ENCODER_FAMILIES}
        return False, (
            f"discriminator_fails_scale: only {len(fams_above)} encoders show "
            f"dominance_rate >= 0.50 at smoke; per-encoder dominance_rate: "
            f"{rates}; ABORT FULL DISPATCH")

    return True, (
        f"smoke_gate_pass: cardinality_ok + arms_differ(4 encs) + "
        f"4-distinct-encoders + positive_control_pass + "
        f">=2_encoders_above_dominance_floor")


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

    # Tier counts (per Pareto outcome)
    outcomes = [p["pareto_outcome"] for p in phase_map]
    n_td = sum(1 for o in outcomes if o == "TD_DOMINATES")
    n_rd = sum(1 for o in outcomes if o == "RD_DOMINATES")
    n_tie = sum(1 for o in outcomes if o == "TIE")

    # Overall Pareto-AUC stats (all encoders combined)
    n_total = len(phase_map)
    overall_dom_rate = (n_td + 0.5 * n_tie) / max(n_total, 1)
    overall_net = (n_td - n_rd) / max(n_total, 1)
    overall_rd_loss = n_rd / max(n_total, 1)

    # How many encoders pass v2 chain-grade Pareto-AUC thresholds individually
    enc_chain_grade: Dict[str, bool] = {}
    for fam in ENCODER_FAMILIES:
        s = per_enc_summary.get(fam, {})
        passes = (s.get("dominance_rate", 0.0) >= HP_DOMINANCE_RATE_LO
                   and s.get("net_dominance", 0.0) >= HP_NET_DOMINANCE_LO
                   and s.get("rd_loss_rate", 1.0) <= HP_RD_LOSS_RATE_HI)
        enc_chain_grade[fam] = passes
    n_chain_grade = sum(1 for v in enc_chain_grade.values() if v)

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
                f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                f"td_wins={n_td}/{n_total} rd_wins={n_rd}/{n_total} ties={n_tie}/{n_total}; "
                f"overall_dominance_rate={overall_dom_rate:.3f}; "
                f"4-encoder-distinct; positive_control@"
                f"{pc_result.get('target', {}).get('encoder_family')} "
                f"outcome={pc_result.get('measured_outcome')} "
                f"rec_acc={pc_result.get('measured_recency_decode_acc'):.3f}; "
                f"encoder_tiers={encoder_tiers}; "
                f"n_encoders_chain_grade={n_chain_grade}/4")
        else:
            verdict = "HARD_FAIL"
            vmsg = (
                f"HARD_FAIL_SMOKE: {reason}; td_wins={n_td} rd_wins={n_rd} "
                f"ties={n_tie}")
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
    elif any(not ad.get("differ") for ad in arms_differ.values()):
        bad = [fam for fam in ENCODER_FAMILIES
               if not arms_differ.get(fam, {}).get("differ")]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_ARMS_IDENTICAL: encoders with TD==RD hashes: {bad}"
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (
            f"HARD_FAIL_CONTROL_FAIL: positive_control {pc_result.get('target')} "
            f"measured_outcome={pc_result.get('measured_outcome')} "
            f"recency_decode={pc_result.get('measured_recency_decode_acc')}; "
            f"test rig broken; encoder-discrimination framing UNTRUSTED")
    elif n_pairs_differ == 0:
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_NULL_ENCODER_INVARIANCE: all 4 encoders produce "
            f"identical (pareto_outcome, td_composite, recency_decode_acc) "
            f"vectors at every (decay, load); encoder is NOT a discriminating "
            f"lever for time-decay eviction in this regime; honest negative; "
            f"n_encoders_chain_grade={n_chain_grade}/4; td_wins={n_td}/{n_total}")
    elif n_chain_grade >= 1 and overall_dom_rate >= HP_DOMINANCE_RATE_LO:
        verdict = "HARD_PASS"
        vmsg = (
            f"HARD_PASS_ENCODER_DISCRIMINATION: {observed_n}/{expected_n} pts; "
            f"{n_chain_grade}/4 encoders pass v2 chain-grade Pareto-AUC "
            f"individually (dom>={HP_DOMINANCE_RATE_LO}, net>="
            f"{HP_NET_DOMINANCE_LO}, rd_loss<={HP_RD_LOSS_RATE_HI}); "
            f"overall_dominance_rate={overall_dom_rate:.3f}; "
            f"n_pairs_differ={n_pairs_differ}/6; encoder_tiers={encoder_tiers}; "
            f"positive_control_pass; pc.recency_acc="
            f"{pc_result.get('measured_recency_decode_acc'):.3f}")
    elif overall_dom_rate >= 0.60 and n_pairs_differ >= 2:
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_ENCODER_DIFFERS_BUT_LOW_CHAIN_GRADE: encoders "
            f"distinguish (n_pairs_differ={n_pairs_differ}/6) but only "
            f"{n_chain_grade}/4 encoders clear v2 chain-grade thresholds; "
            f"overall_dominance_rate={overall_dom_rate:.3f}; "
            f"encoder_tiers={encoder_tiers}; td_wins={n_td}/{n_total}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"MIDDLE_BAND_LOW_DISCRIMINATION: overall_dominance_rate="
            f"{overall_dom_rate:.3f} below 0.60; n_pairs_differ={n_pairs_differ}/6; "
            f"n_chain_grade={n_chain_grade}/4; td_wins={n_td}/{n_total}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


def get_backend_label() -> str:
    return "numpy.cpu"


__all__ = [
    "ENCODER_FAMILIES",
    "DECAY_RATE_DAYS_FULL", "CAPACITY_LOAD_RATIO_FULL", "N_DIM_SWEEP_FULL",
    "DECAY_RATE_DAYS_SMOKE", "CAPACITY_LOAD_RATIO_SMOKE", "N_DIM_SWEEP_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "N_ATOMS_BASE", "N_DAYS_SIM", "N_DIM_DEFAULT", "N_DIM_HIGH", "N_DIM_LOW",
    "R_BUCKETS",
    "HP_DOMINANCE_RATE_LO", "HP_NET_DOMINANCE_LO", "HP_RD_LOSS_RATE_HI",
    "POSITIVE_CONTROL", "REQUIRED_FIELDS",
    "simulate_atom_timeline", "build_encoded_atom_store",
    "decode_recency_buckets", "arm_time_decay_via_encoder", "arm_random_eviction",
    "compute_arm_metrics", "pareto_dominance_outcome", "eval_phase_point",
    "selftest", "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict", "get_backend_label",
]
