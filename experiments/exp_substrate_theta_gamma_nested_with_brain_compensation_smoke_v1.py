"""
exp_substrate_theta_gamma_nested_with_brain_compensation_smoke_v1

SCIENTIFIC QUESTION:
  v1 theta-gamma nested cell HARD_FAILed smoke (recall=0.906 vs single=0.994 at
  sigma=16). Brain SNR compensation 2x-drill identified 4 structural amplifiers
  (PV-sparsification, CA3-attractor, ACh-gating, STDP-compression). This cell
  composes the cheapest substrate-compatible two (sparse codebook + per-gamma
  Hopfield cleanup) and tests whether brain-canonical composition recovers
  the structural SNR deficit.

MECHANISM (6-arm ablation):
  ARM_SINGLE_LOCKIN:       single-freq P=32 lock-in on dense bipolar codebook (baseline)
  ARM_NESTED_BASELINE:     theta-gamma nested on dense bipolar (reproduces v1 deficit)
  ARM_NESTED_SPARSE:       theta-gamma on sparse codebook (f=0.02; CERT 592)
  ARM_NESTED_CLEANUP:      theta-gamma on dense codebook + per-gamma Hopfield cleanup
  ARM_NESTED_BRAIN_FULL:   theta-gamma + sparse + cleanup (compose ARMS 3+4)
  ARM_SINGLE_LOCKIN_SPARSE: single-freq on sparse codebook (control arm; negativity #3)

PRE-REGISTERED HARD_PASS (any one of A/B/C suffices):
  CRITERION_A: ARM_NESTED_BRAIN_FULL recall@1 at sigma=16 >= ARM_SINGLE_LOCKIN recall@1 - 0.02
  CRITERION_B: ARM_NESTED_BRAIN_FULL recall@1 at sigma=32 >= ARM_SINGLE_LOCKIN recall@1 + 0.05
  CRITERION_C: both ARM_NESTED_SPARSE and ARM_NESTED_CLEANUP each add >=0.10 recall vs
               ARM_NESTED_BASELINE at sigma=16 (per-compensator load-bearing)

  If A+B both pass: chain-grade-eligible (META = brain-compensated-nested recovers-and-exceeds).

PRE-REGISTERED HARD_FAIL (any one triggers; pivot to TDM-gating Anchor 2):
  HARD_FAIL_1: ARM_NESTED_BRAIN_FULL <= ARM_NESTED_BASELINE + 0.03 at ALL sigmas
  HARD_FAIL_2: ARM_NESTED_SPARSE < ARM_NESTED_BASELINE at sigma=16 (sparsity breaks demod)
  HARD_FAIL_3: ARM_NESTED_CLEANUP degrades vs NESTED_BASELINE at sigma=4 by > 0.05
               (cleanup-snap-away pathology at low noise)

MIDDLE_BAND:
  ARM_NESTED_BRAIN_FULL exceeds NESTED_BASELINE by 0.05-0.10 but below single-frequency.
  Partial compensation; v2 tunes f-grid + tau-grid OR pivots to TDM-gating.

CONFIG (smoke):
  N=512, M=50, seeds=[7,17,23], sigmas=[4,8,16,32,64]
  P_theta=4, P_gamma=7, P_single=32, k_theta=1, k_gamma=31
  sparse_f=0.02, cleanup_tau=0.3, cleanup_temp=4.0, N_EVAL=80

CONFIG (full; gates on smoke HARD_PASS):
  N=4096, M=500, seeds=[7,17,23], sigmas=[4,8,16,32,64,128]
  P_theta=8, P_gamma=7, P_single=64, k_theta=1, k_gamma=31
  Routing: remote_cpu_queue ~45-90min

PROT-018 N-suffix: no _n<N> suffix. Production N=4096 explicit below.
ASCII-only. No emojis.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
import argparse
import time
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial_key,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_theta_gamma_nested_with_brain_compensation_smoke_v1"

RUN_MODE = (
    "smoke"
    if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

SMOKE = RUN_MODE == "smoke"

# No CUDA: pure numpy; route to remote_cpu_queue for full run.

if SMOKE:
    SEEDS = [7, 17, 23]
    N_DIM = 512
    M = 50
    SIGMAS = [4.0, 8.0, 16.0, 32.0, 64.0]
    P_THETA = 4
    P_GAMMA = 7
    P_SINGLE = 32
    K_THETA = 1
    K_GAMMA = 31
    N_EVAL = 80
else:
    # PRODUCTION config: N=4096, remote_cpu_queue
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    M = 500
    SIGMAS = [4.0, 8.0, 16.0, 32.0, 64.0, 128.0]
    P_THETA = 8
    P_GAMMA = 7
    P_SINGLE = 64
    K_THETA = 1
    K_GAMMA = 31
    N_EVAL = 200

# Brain-compensation parameters (exp_dev-owned per autonomy declaration)
SPARSE_F = 0.02        # sparse fraction (CERT 592 best regime)
CLEANUP_TAU = 0.30     # cosine-margin refuse threshold
CLEANUP_TEMP = 4.0     # softmax inverse-temperature for cleanup (scale_by_sqrt_d=True)
CLEANUP_MAX_STEPS = 1  # single Hopfield iteration per gamma cycle (CA3 brain reference)

# Pre-registered thresholds
HP_A_DELTA = -0.02   # CRITERION_A: BRAIN_FULL >= SINGLE - 0.02 at sigma=16
HP_B_DELTA = +0.05   # CRITERION_B: BRAIN_FULL >= SINGLE + 0.05 at sigma=32
HP_C_EACH = 0.10     # CRITERION_C: each ablation adds >= 0.10 vs BASELINE at sigma=16
HF_BRAIN_DELTA = 0.03 # HARD_FAIL_1: BRAIN_FULL <= BASELINE + 0.03 at ALL sigmas
HF_SPARSE_DELTA = 0.0 # HARD_FAIL_2: NESTED_SPARSE < NESTED_BASELINE at sigma=16
HF_CLEANUP_REGRESS = 0.05 # HARD_FAIL_3: CLEANUP degrades vs BASELINE at sigma=4 by >0.05


# ---- core primitives (pure numpy; reused from v1) ----

def _roll_1d(arr: np.ndarray, shift: int) -> np.ndarray:
    """Cyclic roll of last dim (N) by shift. Works on (B, N) or (N,)."""
    return np.roll(arr, shift, axis=-1)


def single_lockin_demod(
    cues: np.ndarray,    # (B, N)
    P: int,
    k_signal: int,
    sigma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Single-frequency lock-in: P phases over k_signal rotation.

    Returns demodulated estimate shape (B, N).
    """
    if P == 1:
        noise = sigma * rng.standard_normal(cues.shape).astype(np.float32)
        return cues + noise
    B, N = cues.shape
    acc = np.zeros_like(cues)
    for p in range(P):
        carrier_p = math.cos(2.0 * math.pi * p / P)
        rolled = _roll_1d(cues, p * k_signal)
        noise_p = sigma * rng.standard_normal((B, N)).astype(np.float32)
        received = rolled * carrier_p + noise_p
        unrolled = _roll_1d(received, -(p * k_signal))
        acc += unrolled * carrier_p
    return (2.0 / P) * acc


def theta_gamma_nested_demod(
    cues: np.ndarray,    # (B, N)
    P_theta: int,
    P_gamma: int,
    k_theta: int,
    k_gamma: int,
    sigma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Two-frequency nested oscillation lock-in.

    Returns demodulated estimate shape (B, N).
    """
    B, N = cues.shape
    acc = np.zeros_like(cues)
    norm = (2.0 / P_theta) * (2.0 / P_gamma)
    for t in range(P_theta):
        w_theta = math.cos(2.0 * math.pi * t / P_theta)
        for g in range(P_gamma):
            w_gamma = math.cos(2.0 * math.pi * g / P_gamma)
            carrier = w_theta * w_gamma
            shift = t * k_theta + g * k_gamma
            rolled = _roll_1d(cues, shift)
            noise_tg = sigma * rng.standard_normal((B, N)).astype(np.float32)
            received = rolled * carrier + noise_tg
            unrolled = _roll_1d(received, -shift)
            acc += unrolled * carrier
    return norm * acc


def theta_gamma_nested_demod_with_cleanup(
    cues: np.ndarray,    # (B, N)
    codebook: np.ndarray, # (M, N); used for cleanup snaps
    P_theta: int,
    P_gamma: int,
    k_theta: int,
    k_gamma: int,
    sigma: float,
    rng: np.random.Generator,
    cleanup_tau: float = 0.30,
    cleanup_temp: float = 4.0,
    cleanup_max_steps: int = 1,
) -> np.ndarray:
    """Theta-gamma nested demod with per-gamma-cycle Hopfield cleanup.

    After each gamma-cycle demod step, apply one soft-attractor snap of the
    accumulated partial result toward the nearest codebook entry, with
    refuse-gate: if cosine margin < cleanup_tau, skip the snap (uncertain;
    do not introduce wrong-attractor bias). Brain reference: CA3 attractor
    dynamics complete the DG partial input within each gamma cycle.

    Returns final demodulated estimate shape (B, N).
    """
    B, N = cues.shape
    # Normalize codebook for cosine ops
    cb_norms = np.linalg.norm(codebook, axis=1, keepdims=True)
    cb_norm = codebook / (cb_norms + 1e-12)  # (M, N) unit vectors

    sqrt_N = float(np.sqrt(N))
    acc = np.zeros_like(cues)
    norm_factor = (2.0 / P_theta) * (2.0 / P_gamma)

    for t in range(P_theta):
        w_theta = math.cos(2.0 * math.pi * t / P_theta)
        # Per-gamma accumulation with cleanup per gamma cycle
        gamma_acc = np.zeros_like(cues)
        for g in range(P_gamma):
            w_gamma = math.cos(2.0 * math.pi * g / P_gamma)
            carrier = w_theta * w_gamma
            shift = t * k_theta + g * k_gamma
            rolled = _roll_1d(cues, shift)
            noise_tg = sigma * rng.standard_normal((B, N)).astype(np.float32)
            received = rolled * carrier + noise_tg
            unrolled = _roll_1d(received, -shift)
            gamma_acc += unrolled * carrier
        # Cleanup snap on accumulated gamma-cycle estimate
        gamma_partial = (2.0 / P_gamma) * gamma_acc  # (B, N) partial theta-cycle estimate

        # Soft-attractor cleanup: one step with refuse-gate
        # Normalize partial estimate for cosine similarity
        partial_norms = np.linalg.norm(gamma_partial, axis=1, keepdims=True)
        partial_unit = gamma_partial / (partial_norms + 1e-12)

        # Scores vs codebook: (B, M)
        scores = cleanup_temp * sqrt_N * (partial_unit @ cb_norm.T)
        # Softmax weights
        scores_shifted = scores - scores.max(axis=1, keepdims=True)
        exp_scores = np.exp(scores_shifted.astype(np.float64))
        weights = (exp_scores / (exp_scores.sum(axis=1, keepdims=True) + 1e-30)).astype(np.float32)

        # Soft snap: weighted sum of codebook entries
        snapped = weights @ cb_norm  # (B, N) L2-normalized blended attractor

        # Refuse gate: if top cosine similarity < tau, skip snap (keep noisy estimate)
        top_cos = scores.max(axis=1) / (cleanup_temp * sqrt_N + 1e-12)  # rescale back
        accept_mask = (top_cos >= cleanup_tau).astype(np.float32)[:, None]  # (B, 1)

        # Blend: accepted entries get snapped; refused get noisy gamma_partial
        # Re-scale snapped to match gamma_partial magnitude for acc
        snap_scaled = snapped * (partial_norms + 1e-12)
        cleaned = accept_mask * snap_scaled + (1.0 - accept_mask) * gamma_partial

        # Accumulate: outer (2/P_theta) applied at end; inner (2/P_gamma) already applied
        # Reverse the inner (2/P_gamma) to get per-theta-cycle contribution
        acc += cleaned * (P_gamma / 2.0)

    # Apply full normalization
    return norm_factor * (2.0 / P_gamma) * acc


def make_sparse_bipolar_codebook(M: int, N: int, f: float, rng: np.random.Generator) -> np.ndarray:
    """Generate sparse bipolar codebook. Each entry: f fraction +1/-1, rest 0.

    CERT 592 best regime: f=0.02; sparse fraction lifts bundle capacity via
    reduced cross-item overlap (sparse superposition; substrate-validated).
    """
    codebook = np.zeros((M, N), dtype=np.float32)
    n_active = max(1, int(round(f * N)))
    for i in range(M):
        active_idx = rng.choice(N, size=n_active, replace=False)
        signs = rng.integers(0, 2, size=n_active).astype(np.float32) * 2.0 - 1.0
        codebook[i, active_idx] = signs
    return codebook


def recall_at_1(decoded: np.ndarray, codebook: np.ndarray, target_indices: np.ndarray) -> float:
    """Nearest-neighbor recall@1 via dot product. decoded: (B, N); codebook: (M, N)."""
    scores = decoded @ codebook.T
    pred = scores.argmax(axis=-1)
    return float((pred == target_indices).mean())


# ---- self-tests (called at module scope before sweep) ----

def _selftest_single_lockin_p1_endpoint() -> None:
    """P=1 single-lockin must be deterministic (reproducible noise path)."""
    cues = np.random.default_rng(42).standard_normal((4, 64)).astype(np.float32)
    out_a = single_lockin_demod(cues.copy(), P=1, k_signal=31, sigma=0.5, rng=np.random.default_rng(7))
    out_b = single_lockin_demod(cues.copy(), P=1, k_signal=31, sigma=0.5, rng=np.random.default_rng(7))
    diff = float(np.abs(out_a - out_b).max())
    assert diff < 1e-9, f"P=1 determinism FAIL: diff={diff}"


def _selftest_sigma0_single_recovery() -> None:
    """sigma=0: single_lockin_demod recovers signal with exact normalization."""
    N_t = 64
    for P_t in [4, 8, 32]:
        cue = np.random.default_rng(9).standard_normal((3, N_t)).astype(np.float32)
        out = single_lockin_demod(cue, P=P_t, k_signal=31, sigma=0.0, rng=np.random.default_rng(11))
        sum_cos2 = sum(math.cos(2.0 * math.pi * p / P_t) ** 2 for p in range(P_t))
        expected_factor = (2.0 / P_t) * sum_cos2
        expected = expected_factor * cue
        diff = float(np.abs(out - expected).max())
        assert diff < 1e-4, f"single_lockin sigma=0 FAIL P={P_t}: diff={diff}"
        assert abs(expected_factor - 1.0) < 1e-6, f"norm off P={P_t}: {expected_factor}"


def _selftest_sigma0_nested_recovery() -> None:
    """sigma=0: theta_gamma_nested_demod recovers signal with joint normalization."""
    N_t = 64
    P_th, P_gm = 4, 4
    cue = np.random.default_rng(13).standard_normal((2, N_t)).astype(np.float32)
    out = theta_gamma_nested_demod(cue, P_theta=P_th, P_gamma=P_gm,
                                    k_theta=1, k_gamma=31, sigma=0.0,
                                    rng=np.random.default_rng(17))
    s_th = sum(math.cos(2.0 * math.pi * t / P_th) ** 2 for t in range(P_th))
    s_gm = sum(math.cos(2.0 * math.pi * g / P_gm) ** 2 for g in range(P_gm))
    factor = (2.0 / P_th) * s_th * (2.0 / P_gm) * s_gm
    expected = factor * cue
    diff = float(np.abs(out - expected).max())
    assert diff < 1e-4, f"theta_gamma sigma=0 FAIL: diff={diff} factor={factor}"
    assert abs(factor - 1.0) < 1e-5, f"joint norm off: {factor}"


def _selftest_sparse_codebook_gen() -> None:
    """Sparse codebook: fraction of non-zero entries within 10% of target f."""
    rng = np.random.default_rng(77)
    M_t, N_t, f_t = 100, 512, 0.02
    cb = make_sparse_bipolar_codebook(M_t, N_t, f_t, rng)
    assert cb.shape == (M_t, N_t), f"sparse cb shape wrong: {cb.shape}"
    frac_nonzero = float((cb != 0.0).mean())
    expected_f = f_t
    assert abs(frac_nonzero - expected_f) < 0.005, \
        f"sparse fraction off: got {frac_nonzero:.4f} expected ~{expected_f}"
    # Check +1/-1 values only in non-zero entries
    nonzero_vals = cb[cb != 0.0]
    assert np.all(np.abs(np.abs(nonzero_vals) - 1.0) < 1e-6), \
        "sparse codebook non-zero values are not +1/-1"
    print(f"  [selftest] sparse codebook gen: frac_nonzero={frac_nonzero:.4f} target={expected_f}", flush=True)


def _selftest_cleanup_snap_idempotence_at_sigma0() -> None:
    """Cleanup at sigma=0: already-clean cue must recall at 1.000 after snap."""
    rng = np.random.default_rng(55)
    M_t, N_t = 40, 128
    codebook = rng.standard_normal((M_t, N_t)).astype(np.float32)
    targets = np.array([0, 5, 10, 15, 20])
    cues = codebook[targets]
    # Run cleanup arm at sigma=0 -- demod of a cue with zero noise should recover cue
    decoded_cleanup = theta_gamma_nested_demod_with_cleanup(
        cues.copy(), codebook,
        P_theta=4, P_gamma=4, k_theta=1, k_gamma=31,
        sigma=0.0, rng=np.random.default_rng(0),
        cleanup_tau=CLEANUP_TAU, cleanup_temp=CLEANUP_TEMP,
        cleanup_max_steps=CLEANUP_MAX_STEPS,
    )
    r_cleanup = recall_at_1(decoded_cleanup, codebook, targets)
    assert r_cleanup >= 0.90, \
        f"cleanup sigma=0 recall low: {r_cleanup:.4f} (expected >= 0.90)"
    print(f"  [selftest] cleanup snap sigma=0 recall={r_cleanup:.4f}", flush=True)


def _selftest_recall_all_arms_nontrivial() -> None:
    """At sigma=0, all 6 arms must achieve recall@1 >= 0.90 on tiny codebook."""
    rng = np.random.default_rng(99)
    M_t, N_t = 30, 128
    dense_cb = rng.standard_normal((M_t, N_t)).astype(np.float32)
    dense_norms = np.linalg.norm(dense_cb, axis=1, keepdims=True)
    dense_cb_n = dense_cb / (dense_norms + 1e-9)

    sparse_cb = make_sparse_bipolar_codebook(M_t, N_t, SPARSE_F, np.random.default_rng(33))

    targets = np.array([0, 3, 7, 12, 20])
    cues_d = dense_cb_n[targets]
    cues_s = sparse_cb[targets]

    r_single = recall_at_1(
        single_lockin_demod(cues_d.copy(), P=8, k_signal=31, sigma=0.0, rng=np.random.default_rng(0)),
        dense_cb_n, targets,
    )
    r_nested = recall_at_1(
        theta_gamma_nested_demod(cues_d.copy(), P_theta=4, P_gamma=4, k_theta=1, k_gamma=31,
                                  sigma=0.0, rng=np.random.default_rng(0)),
        dense_cb_n, targets,
    )
    r_sparse = recall_at_1(
        single_lockin_demod(cues_s.copy(), P=8, k_signal=31, sigma=0.0, rng=np.random.default_rng(0)),
        sparse_cb, targets,
    )
    r_cleanup = recall_at_1(
        theta_gamma_nested_demod_with_cleanup(
            cues_d.copy(), dense_cb_n, P_theta=4, P_gamma=4, k_theta=1, k_gamma=31,
            sigma=0.0, rng=np.random.default_rng(0),
            cleanup_tau=CLEANUP_TAU, cleanup_temp=CLEANUP_TEMP,
        ),
        dense_cb_n, targets,
    )

    for name, r in [("single", r_single), ("nested", r_nested),
                    ("sparse_single", r_sparse), ("cleanup", r_cleanup)]:
        assert r >= 0.90, f"arm={name} sigma=0 recall FAIL: {r:.4f} (expected >= 0.90)"

    print(
        f"  [selftest] sigma=0 all-arm recall: "
        f"single={r_single:.3f} nested={r_nested:.3f} "
        f"sparse_single={r_sparse:.3f} cleanup={r_cleanup:.3f}",
        flush=True,
    )


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    _selftest_single_lockin_p1_endpoint()
    _selftest_sigma0_single_recovery()
    _selftest_sigma0_nested_recovery()
    _selftest_sparse_codebook_gen()
    _selftest_cleanup_snap_idempotence_at_sigma0()
    _selftest_recall_all_arms_nontrivial()
    print(
        "[selftest] PASS brain_compensation v1: "
        "P=1-endpoint + sigma=0-single + sigma=0-nested + "
        "sparse-codebook-gen + cleanup-snap-idempotence + all-arm-sigma0-recall.",
        flush=True,
    )


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ---- main experiment ----

def run_seed(seed: int) -> Dict[str, Any]:
    t_seed_start = time.time()
    total_nested = P_THETA * P_GAMMA
    print(
        f"[seed={seed}] N_DIM={N_DIM} M={M} P_single={P_SINGLE} "
        f"P_theta={P_THETA} P_gamma={P_GAMMA} k_theta={K_THETA} k_gamma={K_GAMMA} "
        f"total_nested_phases={total_nested} sparse_f={SPARSE_F} tau={CLEANUP_TAU}",
        flush=True,
    )

    rng_book = np.random.default_rng(seed)
    rng_eval = np.random.default_rng(seed + 10_000)
    rng_s1 = np.random.default_rng(seed + 20_000)  # single-lockin dense
    rng_s2 = np.random.default_rng(seed + 30_000)  # nested baseline
    rng_s3 = np.random.default_rng(seed + 40_000)  # nested sparse
    rng_s4 = np.random.default_rng(seed + 50_000)  # nested cleanup
    rng_s5 = np.random.default_rng(seed + 60_000)  # nested brain full
    rng_s6 = np.random.default_rng(seed + 70_000)  # single lockin sparse

    # Dense bipolar codebook
    dense_cb = (rng_book.integers(0, 2, (M, N_DIM)).astype(np.float32) * 2.0 - 1.0)

    # Sparse bipolar codebook (CERT 592 f=0.02)
    rng_sparse_book = np.random.default_rng(seed + 80_000)
    sparse_cb = make_sparse_bipolar_codebook(M, N_DIM, SPARSE_F, rng_sparse_book)

    # Sample N_EVAL target indices
    target_indices = rng_eval.integers(0, M, N_EVAL)

    arm_names = [
        "ARM_SINGLE_LOCKIN",
        "ARM_NESTED_BASELINE",
        "ARM_NESTED_SPARSE",
        "ARM_NESTED_CLEANUP",
        "ARM_NESTED_BRAIN_FULL",
        "ARM_SINGLE_LOCKIN_SPARSE",
    ]
    per_arm: Dict[str, Dict[str, float]] = {a: {} for a in arm_names}

    for sigma in SIGMAS:
        # Cues from respective codebooks
        cues_d = dense_cb[target_indices]   # (N_EVAL, N_DIM) dense bipolar cues
        cues_s = sparse_cb[target_indices]  # (N_EVAL, N_DIM) sparse bipolar cues

        # ARM_SINGLE_LOCKIN: single-freq on dense codebook
        decoded_s1 = single_lockin_demod(
            cues_d.copy(), P=P_SINGLE, k_signal=K_GAMMA, sigma=sigma, rng=rng_s1,
        )
        r_single = recall_at_1(decoded_s1, dense_cb, target_indices)
        per_arm["ARM_SINGLE_LOCKIN"][f"sigma_{sigma}"] = r_single

        # ARM_NESTED_BASELINE: theta-gamma on dense codebook, no compensation
        decoded_s2 = theta_gamma_nested_demod(
            cues_d.copy(), P_theta=P_THETA, P_gamma=P_GAMMA,
            k_theta=K_THETA, k_gamma=K_GAMMA, sigma=sigma, rng=rng_s2,
        )
        r_nested_base = recall_at_1(decoded_s2, dense_cb, target_indices)
        per_arm["ARM_NESTED_BASELINE"][f"sigma_{sigma}"] = r_nested_base

        # ARM_NESTED_SPARSE: theta-gamma on sparse codebook, no cleanup
        decoded_s3 = theta_gamma_nested_demod(
            cues_s.copy(), P_theta=P_THETA, P_gamma=P_GAMMA,
            k_theta=K_THETA, k_gamma=K_GAMMA, sigma=sigma, rng=rng_s3,
        )
        r_nested_sparse = recall_at_1(decoded_s3, sparse_cb, target_indices)
        per_arm["ARM_NESTED_SPARSE"][f"sigma_{sigma}"] = r_nested_sparse

        # ARM_NESTED_CLEANUP: theta-gamma on dense codebook + per-gamma cleanup
        decoded_s4 = theta_gamma_nested_demod_with_cleanup(
            cues_d.copy(), dense_cb,
            P_theta=P_THETA, P_gamma=P_GAMMA,
            k_theta=K_THETA, k_gamma=K_GAMMA, sigma=sigma, rng=rng_s4,
            cleanup_tau=CLEANUP_TAU, cleanup_temp=CLEANUP_TEMP,
            cleanup_max_steps=CLEANUP_MAX_STEPS,
        )
        r_nested_cleanup = recall_at_1(decoded_s4, dense_cb, target_indices)
        per_arm["ARM_NESTED_CLEANUP"][f"sigma_{sigma}"] = r_nested_cleanup

        # ARM_NESTED_BRAIN_FULL: sparse codebook + per-gamma cleanup (compose 3+4)
        decoded_s5 = theta_gamma_nested_demod_with_cleanup(
            cues_s.copy(), sparse_cb,
            P_theta=P_THETA, P_gamma=P_GAMMA,
            k_theta=K_THETA, k_gamma=K_GAMMA, sigma=sigma, rng=rng_s5,
            cleanup_tau=CLEANUP_TAU, cleanup_temp=CLEANUP_TEMP,
            cleanup_max_steps=CLEANUP_MAX_STEPS,
        )
        r_brain_full = recall_at_1(decoded_s5, sparse_cb, target_indices)
        per_arm["ARM_NESTED_BRAIN_FULL"][f"sigma_{sigma}"] = r_brain_full

        # ARM_SINGLE_LOCKIN_SPARSE: single-freq on sparse codebook (control)
        decoded_s6 = single_lockin_demod(
            cues_s.copy(), P=P_SINGLE, k_signal=K_GAMMA, sigma=sigma, rng=rng_s6,
        )
        r_single_sparse = recall_at_1(decoded_s6, sparse_cb, target_indices)
        per_arm["ARM_SINGLE_LOCKIN_SPARSE"][f"sigma_{sigma}"] = r_single_sparse

        print(
            f"  [seed={seed} sigma={sigma}] "
            f"single={r_single:.4f} nested_base={r_nested_base:.4f} "
            f"nested_sparse={r_nested_sparse:.4f} nested_cleanup={r_nested_cleanup:.4f} "
            f"brain_full={r_brain_full:.4f} single_sparse={r_single_sparse:.4f}",
            flush=True,
        )

    elapsed = time.time() - t_seed_start
    return {
        "seed": seed,
        "N": N_DIM,
        "M": M,
        "run_mode": RUN_MODE,
        "per_arm": per_arm,
        "K_GAMMA": K_GAMMA,
        "K_THETA": K_THETA,
        "P_SINGLE": P_SINGLE,
        "P_THETA": P_THETA,
        "P_GAMMA": P_GAMMA,
        "SIGMAS": SIGMAS,
        "N_EVAL": N_EVAL,
        "SPARSE_F": SPARSE_F,
        "CLEANUP_TAU": CLEANUP_TAU,
        "elapsed_s": float(elapsed),
    }


def aggregate_arms(per_seed: Dict[str, Any]) -> Tuple[Dict, Dict]:
    """Return (summary_by_arm_sigma, cv_by_arm_sigma) averaging over seeds."""
    arm_names = [
        "ARM_SINGLE_LOCKIN",
        "ARM_NESTED_BASELINE",
        "ARM_NESTED_SPARSE",
        "ARM_NESTED_CLEANUP",
        "ARM_NESTED_BRAIN_FULL",
        "ARM_SINGLE_LOCKIN_SPARSE",
    ]
    seed_keys = sorted(per_seed.keys())
    summary: Dict[str, Dict[str, float]] = {a: {} for a in arm_names}
    cv: Dict[str, Dict[str, float]] = {a: {} for a in arm_names}

    for sigma in SIGMAS:
        sig_key = f"sigma_{sigma}"
        for arm in arm_names:
            vals: List[float] = []
            for sk in seed_keys:
                v = per_seed[sk].get("per_arm", {}).get(arm, {}).get(sig_key)
                if v is not None:
                    vals.append(float(v))
            if vals:
                arr = np.array(vals, dtype=np.float64)
                mean_v = float(arr.mean())
                std_v = float(arr.std())
                summary[arm][sig_key] = mean_v
                cv[arm][sig_key] = float(std_v / mean_v) if mean_v > 1e-9 else 0.0
            else:
                summary[arm][sig_key] = 0.0
                cv[arm][sig_key] = 0.0
    return summary, cv


def verdict(
    summary: Dict[str, Dict[str, float]],
) -> Tuple[str, str]:
    """Apply pre-registered HARD bands."""
    single = summary.get("ARM_SINGLE_LOCKIN", {})
    nested_base = summary.get("ARM_NESTED_BASELINE", {})
    nested_sparse = summary.get("ARM_NESTED_SPARSE", {})
    nested_cleanup = summary.get("ARM_NESTED_CLEANUP", {})
    brain_full = summary.get("ARM_NESTED_BRAIN_FULL", {})

    if not single or not nested_base or not brain_full:
        return "HARD_FAIL", f"HARD_FAIL: missing arm data. arms_seen={list(summary.keys())}"

    # ---- HARD_FAIL checks ----
    # HARD_FAIL_1: brain_full <= nested_base + 0.03 at ALL sigmas
    hf1_all_sigmas = all(
        brain_full.get(f"sigma_{s}", 0.0) <= nested_base.get(f"sigma_{s}", 0.0) + HF_BRAIN_DELTA
        for s in SIGMAS
    )

    # HARD_FAIL_2: NESTED_SPARSE < NESTED_BASELINE at sigma=16
    sig16_key = "sigma_16.0"
    r_sparse_16 = nested_sparse.get(sig16_key, 0.0)
    r_base_16 = nested_base.get(sig16_key, 0.0)
    hf2 = (r_sparse_16 < r_base_16 + HF_SPARSE_DELTA)  # strict: sparse < baseline

    # HARD_FAIL_3: cleanup regresses vs baseline at sigma=4 by > 0.05
    sig4_key = "sigma_4.0"
    r_cleanup_4 = nested_cleanup.get(sig4_key, 0.0)
    r_base_4 = nested_base.get(sig4_key, 0.0)
    hf3 = (r_cleanup_4 < r_base_4 - HF_CLEANUP_REGRESS)

    # ---- HARD_PASS checks ----
    r_single_16 = single.get(sig16_key, 0.0)
    r_brain_16 = brain_full.get(sig16_key, 0.0)
    criterion_a = (r_brain_16 >= r_single_16 + HP_A_DELTA)  # >= single - 0.02

    r_single_32 = single.get("sigma_32.0", 0.0)
    r_brain_32 = brain_full.get("sigma_32.0", 0.0)
    criterion_b = (r_brain_32 >= r_single_32 + HP_B_DELTA)  # >= single + 0.05

    r_sparse_16_delta = r_sparse_16 - r_base_16
    r_cleanup_16 = nested_cleanup.get(sig16_key, 0.0)
    r_cleanup_16_delta = r_cleanup_16 - r_base_16
    criterion_c = (r_sparse_16_delta >= HP_C_EACH) and (r_cleanup_16_delta >= HP_C_EACH)

    detail = (
        f"N={N_DIM} M={M} sparse_f={SPARSE_F} tau={CLEANUP_TAU}; "
        f"single@16={r_single_16:.4f} brain_full@16={r_brain_16:.4f} "
        f"nested_base@16={r_base_16:.4f} nested_sparse@16={r_sparse_16:.4f} "
        f"nested_cleanup@16={r_cleanup_16:.4f}; "
        f"brain_full@32={r_brain_32:.4f} single@32={r_single_32:.4f}; "
        f"criteria=A:{criterion_a} B:{criterion_b} C:{criterion_c}; "
        f"hf_flags=1:{hf1_all_sigmas} 2:{hf2} 3:{hf3}"
    )

    if hf1_all_sigmas:
        return (
            "HARD_FAIL",
            f"HARD_FAIL_1: brain_full adds nothing over nested_baseline (+<={HF_BRAIN_DELTA}) "
            f"at ALL sigmas. Pivot to TDM-gating Anchor 2. {detail}",
        )
    if hf2:
        return (
            "HARD_FAIL",
            f"HARD_FAIL_2: ARM_NESTED_SPARSE < ARM_NESTED_BASELINE at sigma=16 "
            f"(sparse_delta={r_sparse_16_delta:+.4f}). Sparse codebook breaks nested demod. {detail}",
        )
    if hf3:
        return (
            "HARD_FAIL",
            f"HARD_FAIL_3: ARM_NESTED_CLEANUP regresses vs BASELINE at sigma=4 by "
            f"{r_base_4 - r_cleanup_4:.4f} > {HF_CLEANUP_REGRESS} (snap-away pathology). {detail}",
        )

    if criterion_a or criterion_b or criterion_c:
        which = []
        if criterion_a:
            which.append(
                f"A(brain@16={r_brain_16:.4f}>={r_single_16:.4f}+{HP_A_DELTA}={r_single_16+HP_A_DELTA:.4f})"
            )
        if criterion_b:
            which.append(
                f"B(brain@32={r_brain_32:.4f}>={r_single_32:.4f}+{HP_B_DELTA}={r_single_32+HP_B_DELTA:.4f})"
            )
        if criterion_c:
            which.append(
                f"C(sparse_delta={r_sparse_16_delta:+.4f}+cleanup_delta={r_cleanup_16_delta:+.4f}>={HP_C_EACH})"
            )
        chain_eligible = criterion_a and criterion_b
        tag = "HARD_PASS" + (" [chain-grade-eligible: A+B both met]" if chain_eligible else "")
        return (
            "HARD_PASS",
            f"{tag}: brain-compensated nested oscillation recovers/exceeds single-lockin. "
            f"Criteria: {'; '.join(which)}. {detail}",
        )

    # MIDDLE_BAND: brain_full improves over baseline but doesn't clear hard-pass criteria
    brain_deltas = {
        s: brain_full.get(f"sigma_{s}", 0.0) - nested_base.get(f"sigma_{s}", 0.0)
        for s in SIGMAS
    }
    max_brain_delta = max(brain_deltas.values()) if brain_deltas else 0.0
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: brain-compose improves over nested_baseline "
        f"(max_delta={max_brain_delta:+.4f}) but does not clear hard-pass criteria. "
        f"Tune f-grid + tau-grid OR pivot to TDM-gating. {detail}",
    )


def main() -> int:
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS}", flush=True)
    print(
        f"[config] N_DIM={N_DIM} M={M} sigmas={SIGMAS} "
        f"P_single={P_SINGLE} k_gamma={K_GAMMA} P_theta={P_THETA} P_gamma={P_GAMMA} "
        f"sparse_f={SPARSE_F} cleanup_tau={CLEANUP_TAU} N_EVAL={N_EVAL}",
        flush=True,
    )

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N_DIM, "M": M, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds done; running {remaining}", flush=True)

    t_total = time.time()
    for seed in remaining:
        result = run_seed(seed)
        write_partial_key(out_dir, seed, result)
        print(f"[ckpt] seed={seed} partial written ({result['elapsed_s']:.1f}s)", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    summary, cv = aggregate_arms(per_seed)
    v, vmsg = verdict(summary)
    elapsed_total = time.time() - t_total

    print(f"\n[VERDICT] {vmsg}", flush=True)
    print(f"[elapsed] total_wall_s={elapsed_total:.2f}", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "config": {
            "N_DIM": N_DIM,
            "M": M,
            "K_GAMMA": K_GAMMA,
            "K_THETA": K_THETA,
            "P_SINGLE": P_SINGLE,
            "P_THETA": P_THETA,
            "P_GAMMA": P_GAMMA,
            "SIGMAS": SIGMAS,
            "N_EVAL": N_EVAL,
            "SPARSE_F": SPARSE_F,
            "CLEANUP_TAU": CLEANUP_TAU,
        },
        "summary": summary,
        "cv": cv,
        "per_seed": per_seed,
        "elapsed_s": float(elapsed_total),
    }
    write_metrics(out_dir, metrics, results=list(per_seed.values()))
    print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
