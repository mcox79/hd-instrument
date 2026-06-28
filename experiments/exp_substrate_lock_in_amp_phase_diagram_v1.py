# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""substrate_lock_in_amp_phase_diagram_v1 -- Stage 2 phase-diagram fill (PARTIAL -> HIGH).

SCIENTIFIC QUESTION (Research 2026-06-28):
  Lock-in amp is an existing chain-grade substrate primitive (HARD_PASS at
  exp_lock_in_amplifier_hd_frequency_smoke_v1: P32 lift x4.32, P8 x3.73, at
  baseline=0.232 cliff). Stage 2 characteristics table: 70% completeness, phase
  coverage PARTIAL. What is the SHAPE of the SNR phase diagram across
  (SNR_input x integration_time x N_DIM)? Where does phase-coherent integration
  extract signal above noise (lock-in WINS); where does it saturate (both arms
  trivially recover signal); where does it floor (signal lost regardless)?

  Physics prediction (textbook): for additive white noise transmission with
  phase-coherent integration over t samples, lock-in SNR_output = SNR_input *
  sqrt(t/2). Substrate-native analog: signal v transmitted as cos-modulated
  noisy copies; coherent demodulation integrates signal coherently while noise
  averages.

PRIMITIVE-ISOLATION DESIGN:
  - codebook of M bipolar HD vectors (the "memory"); each query targets one entry v
  - TRANSMIT: t phase-shifted copies; for each p in 0..t-1:
        carrier_p   = cos(2*pi*signal_freq*p)
        transmit_p  = v * carrier_p
        received_p  = transmit_p + sigma * noise_p     (sigma = 1/SNR_input)
  - DEMODULATE (ARM_LOCK_IN): coherent integration weighted by carrier_p:
        decoded = (2/t) * sum_p received_p * carrier_p
    Signal coheres as (2/t) * sum_p cos^2 = (2/t) * (t/2) = 1 -> recovers v.
    Noise variance: (2/t)^2 * sigma^2 * sum_p cos^2 = 2*sigma^2/t
    -> SNR_output = SNR_input * sqrt(t/2).
  - ARM_DIRECT_COSINE: take SINGLE noisy sample p=0; cosine-match without
    integration. SNR_output = SNR_input. No coherence advantage.
  - ARM_NOISE_FLOOR: ignore transmission; return random gaussian vector.
    Recall_at_1 ~= 1/M (chance retrieval; sanity floor).

  PRE-REG: at LOW SNR_input + HIGH t, lock-in should LIFT recall above direct;
  at HIGH SNR_input, both saturate to 1.0; at LOW SNR_input + LOW t, both floor
  to ~chance.

  Predicted cliff at SNR_input * sqrt(t/2) ~ 0.3 (the bipolar-codebook
  cosine-recall transition zone in the existing lock-in cell at sigma=32, N=4096:
  baseline recall=0.232 -> the analog of SNR_in ~ 0.03 here; with t=32 lock-in
  gets sqrt(16) = 4x to 0.12 effective SNR_out -> recall=1.0 as observed).

GRID AXES (60 points = 5 x 4 x 3; freq fixed at 0.1):
  SNR_input  in {0.001, 0.0032, 0.01, 0.032, 0.1}   [5; half-decade spacing
                                                     centered on bipolar-codebook
                                                     cosine-recall cliff]
  integration_time t in {10, 100, 1000, 10000}      [4]
  N          in {2048, 4096, 8192}                   [3]
  signal_freq fixed = 0.1
  M (codebook size) fixed = 100
  N_EVAL queries per grid point = 30 (averaged for recall stability)
  TOTAL = 5 * 4 * 3 = 60 grid points per seed

  CALIBRATION (probe of {SNR_in x t x N} 2026-06-28 at n_eval=15):
    - SNR_in=0.001 + low t   -> FLOOR (LOCK_IN ~ DIRECT ~ 0)
    - SNR_in=0.001 + t=1000 + N=8192 -> partial ADVANTAGE (LOCK=0.47, DIR=0.07)
    - SNR_in=0.0032 + t>=100 -> ADVANTAGE
    - SNR_in=0.01 + t>=100   -> deep ADVANTAGE (LOCK=1.0, DIR=0)
    - SNR_in=0.032 + t>=10   -> ADVANTAGE (LOCK=1.0, DIR~0.27)
    - SNR_in=0.1 across all t/N -> SAT (LOCK=DIR=1.0)
    Expected regime counts (60 pts):
    - SAT      ~ 12 pts (all SNR=0.1 cells; possibly some SNR=0.032 at high N)
    - FLOOR    ~ 10-12 pts (most SNR=0.001 cells)
    - ADVANTAGE ~ 20-30 pts (the SNR x t cliff transition)

ARMS (3-arm bracket per task spec):
  ARM_LOCK_IN         -- phase-coherent integration over t with known reference
  ARM_DIRECT_COSINE   -- single-sample cosine-match (no modulation processing)
  ARM_NOISE_FLOOR     -- random gaussian guess (chance recall = 1/M = 0.01)

PRE-REGISTERED BANDS (PHASE-MAP framing; mirrors ultrametric phase-map):

  HARD_PASS chain-grade (PARTIAL -> HIGH coverage):
    ALL FOUR of:
    - >= 20% of grid points show SATURATED regime
      (ARM_LOCK_IN.recall >= 0.95 AND ARM_DIRECT.recall >= 0.95):
      trivial-signal endpoint sanity.
    - >= 20% of grid points show FLOOR regime
      (ARM_LOCK_IN.recall <= 1.5/M AND ARM_DIRECT.recall <= 1.5/M):
      below-cliff endpoint sanity.
    - >= 20% of grid points show LOCK-IN-ADVANTAGE regime
      (ARM_LOCK_IN.recall - ARM_DIRECT.recall >= 0.30): the mechanism FIRES.
    - >= 50% of grid points are discriminating
      (|ARM_LOCK_IN.recall - ARM_DIRECT.recall| > 0.05) OR
      (LOCK_IN >= 0.95 AND DIRECT >= 0.95) OR
      (LOCK_IN <= 1.5/M AND DIRECT <= 1.5/M) [i.e., regime-classified, not noise].

  MIDDLE_BAND:
    discriminating-fraction >= 50% AND at least 1 of {SAT, FLOOR, ADVANTAGE} populated
    but NOT all 3 regimes populated at >= 20%.

  HARD_FAIL gates (load-bearing per §15):
    - HARD_FAIL_CARDINALITY_BREACH: any seed observed n_grid_points < EXPECTED_N_UNITS (60).
    - HARD_FAIL_BY_CONSTRUCTION_SAT: ARM_LOCK_IN.recall >= 0.99 at every grid point
      (ceiling-saturated; grid too easy).
    - HARD_FAIL_BY_CONSTRUCTION_FLOOR: ARM_LOCK_IN.recall <= 1.5/M at every grid point
      (mechanism floored everywhere; sweep below cliff).
    - HARD_FAIL_ARMS_IDENTICAL: |LOCK_IN.recall - DIRECT.recall| < 0.02 at >= 90%
      of grid points (mechanism not firing).
    - HARD_FAIL_NOISE_FLOOR_LEAK: ARM_NOISE_FLOOR.recall > 0.10 at any grid point
      (chance-baseline broken; cell wiring bug).
    - HARD_FAIL_LLM_LEAK: n_llm_calls > 0 (substrate-only-decode gate violated).

CALIBRATION (positive control + cliff prediction):
  POSITIVE CONTROL (SNR_input=10, t=10, N=8192): both arms recall ~= 1.0 (trivial).
  CLIFF: at SNR_in=0.01 + t=1000, lock-in SNR_out ~ 0.01*sqrt(500) = 0.22
    (just-below-cliff; LOCK_IN ~ 0.5-0.9; DIRECT ~ 0 = chance).
  FLOOR: at SNR_in=0.001 + t=10, both arms below chance.

FIX INVENTORY:
  - _LLM_CALL_COUNTER = [0] at module scope; asserted == 0 (substrate-only gate).
  - ANCHOR_NAME, CONFIG_VERSION baked module-level.
  - run_mode='full' default; HDLAB_RUN_MODE / --smoke flag honored.
  - allow_synthetic=True (BY DESIGN; primitive-isolation; mirrors c1 / a8 / ultrametric).
  - per_unit entry per (seed, grid_point) into metrics.json.
  - Per-seed checkpoint via experiments/_seed_checkpoint.py.
  - CARDINALITY_OK: EXPECTED_N_UNITS=60.
  - DISCRIMINATOR_SURVIVES_SCALE: smoke grid contains 1 SAT + 1 FLOOR + 1
    advantage point at N=2048 (the substrate's smallest N); FULL grid expands
    to N=8192 where physics is identical (sqrt(t/2) SNR formula is N-independent
    at fixed SNR_in -- N affects only the codebook-cosine-recall cliff sharpness).

FORMULA SELF-TESTS:
  1. ARM_LOCK_IN at SNR_in=inf (sigma=0), t=10, N=512, M=20: recall = 1.000 (clean).
  2. ARM_DIRECT at SNR_in=inf: recall = 1.000 (clean cue).
  3. ARM_NOISE_FLOOR at any SNR_in: recall ~= 1/M (chance; small N_EVAL tolerance).
  4. cos^2 sum normalization: (2/t) * sum_p cos^2(2*pi*f*p) for f=0.1, t=10 ~ 1.0.
  5. Lock-in MID-REGIME discriminator FIRES: at SNR_in=0.1, t=1000, N=2048:
     ARM_LOCK_IN.recall - ARM_DIRECT.recall >= 0.30.

ASCII-only. NumPy-only. Single-file. Resumable.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
import json
import argparse
import time
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "substrate_lock_in_amp_phase_diagram_v1"

# Substrate-only-decode gate. Asserted == 0 at end. Any LLM call MUST increment.
_LLM_CALL_COUNTER = [0]

RUN_MODE = (
    "smoke" if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

# In-cell smoke detection: HDLAB_EXP_NAME ending in _smoke triggers smoke (per fix
# inventory mirror from p1_action_at_any_position_phase_diagram_v1).
if RUN_MODE != "smoke":
    _exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if _exp_name.endswith("_smoke"):
        RUN_MODE = "smoke"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---------------------------------------------------------------------------
# Grid axes
# ---------------------------------------------------------------------------
# Fixed across all modes
SIGNAL_FREQ = 0.1
M_CODEBOOK = 100  # codebook size; chance recall = 1/M = 0.01

# FULL grid (60 points per seed)
# SNR_input axis: half-decade spacing centered on the cliff (probed 2026-06-28).
SNR_INPUT_AXIS_FULL = [0.001, 0.0032, 0.01, 0.032, 0.1]
INTEGRATION_TIME_AXIS_FULL = [10, 100, 1000, 10000]
N_AXIS_FULL = [2048, 4096, 8192]
N_EVAL_FULL = 30
EXPECTED_N_UNITS_FULL = (
    len(SNR_INPUT_AXIS_FULL) * len(INTEGRATION_TIME_AXIS_FULL) * len(N_AXIS_FULL)
)  # 60

# SMOKE grid -- minimum to FIRE all three regimes + discriminator at MID config.
SNR_INPUT_AXIS_SMOKE = [0.001, 0.01, 0.1]   # FLOOR + ADVANTAGE + SAT endpoints
INTEGRATION_TIME_AXIS_SMOKE = [10, 1000]    # short + long
N_AXIS_SMOKE = [2048]                        # smallest production N
N_EVAL_SMOKE = 20
EXPECTED_N_UNITS_SMOKE = (
    len(SNR_INPUT_AXIS_SMOKE) * len(INTEGRATION_TIME_AXIS_SMOKE) * len(N_AXIS_SMOKE)
)  # 6

SEED_DEFAULT = int(os.environ.get("HDLAB_SEED_OVERRIDE", "7"))

if RUN_MODE == "smoke":
    SNR_INPUT_AXIS = SNR_INPUT_AXIS_SMOKE
    INTEGRATION_TIME_AXIS = INTEGRATION_TIME_AXIS_SMOKE
    N_AXIS = N_AXIS_SMOKE
    N_EVAL = N_EVAL_SMOKE
    SEEDS = [SEED_DEFAULT]
    EXPECTED_N_UNITS = EXPECTED_N_UNITS_SMOKE
else:
    SNR_INPUT_AXIS = SNR_INPUT_AXIS_FULL
    INTEGRATION_TIME_AXIS = INTEGRATION_TIME_AXIS_FULL
    N_AXIS = N_AXIS_FULL
    N_EVAL = N_EVAL_FULL
    SEEDS = [SEED_DEFAULT]
    EXPECTED_N_UNITS = EXPECTED_N_UNITS_FULL

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},"
    f"SNR_AXIS={'-'.join(str(x) for x in SNR_INPUT_AXIS)},"
    f"T_AXIS={'-'.join(str(x) for x in INTEGRATION_TIME_AXIS)},"
    f"N_AXIS={'-'.join(str(x) for x in N_AXIS)},"
    f"SIGNAL_FREQ={SIGNAL_FREQ},M={M_CODEBOOK},N_EVAL={N_EVAL},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"EXPECTED_N_UNITS={EXPECTED_N_UNITS}"
)

# ---------------------------------------------------------------------------
# Core mechanism: substrate-native lock-in amplifier
# ---------------------------------------------------------------------------
def _carrier(t: int, freq: float) -> np.ndarray:
    """cos(2*pi*freq*p) for p in 0..t-1."""
    return np.cos(2.0 * np.pi * freq * np.arange(t, dtype=np.float64))


def arm_lock_in_decode(
    v: np.ndarray,
    t_int: int,
    sigma: float,
    freq: float,
    rng: np.random.RandomState,
) -> np.ndarray:
    """Phase-coherent integration over t_int samples.

    For p in 0..t_int-1:
      carrier_p = cos(2*pi*freq*p)
      transmit_p = v * carrier_p
      received_p = transmit_p + sigma * noise_p   (independent noise per p)
    decoded = (2/t_int) * sum_p received_p * carrier_p
    Signal: (2/t_int) * v * sum_p cos^2(...) ~= v (for many samples).
    Noise: variance = (2/t_int)^2 * sigma^2 * sum_p cos^2(...) ~= 2*sigma^2/t_int.
    -> SNR_out = SNR_in * sqrt(t_int/2).
    """
    N = v.shape[0]
    carriers = _carrier(t_int, freq)              # (t_int,)
    # Normalization factor: (2/t_int) * sum_p cos^2.  For incommensurate freq it's
    # approximately 1.0 but not exactly; compute explicitly for accuracy.
    cos2_sum = float(np.sum(carriers ** 2))       # ~ t_int/2 for many samples
    norm_factor = 2.0 / float(t_int)              # outer factor
    # Sum sig contribution: v * sum_p carrier_p * carrier_p = v * cos2_sum.
    signal_acc = v * cos2_sum
    # Sum noise contribution: sum_p (sigma * noise_p) * carrier_p; vectorized:
    # We avoid materializing t_int x N matrix when t_int is large by streaming
    # in chunks; for t_int <= 10000 and N <= 8192, t_int*N <= 8.2e7 floats =
    # 640MB worst-case, too large -> stream.
    CHUNK = max(1, min(t_int, 500_000 // max(1, N)))  # cap chunk to ~500k elements
    noise_acc = np.zeros(N, dtype=np.float64)
    p_start = 0
    while p_start < t_int:
        p_end = min(t_int, p_start + CHUNK)
        chunk_size = p_end - p_start
        # noise shape (chunk_size, N); each row is noise_p for p in [p_start, p_end)
        noise = rng.randn(chunk_size, N).astype(np.float64) * sigma
        # weight each row by carrier[p]
        weights = carriers[p_start:p_end]                  # (chunk_size,)
        noise_acc += (noise.T @ weights)                   # (N,)
        p_start = p_end
    total_acc = signal_acc + noise_acc
    decoded = norm_factor * total_acc
    return decoded


def arm_direct_decode(
    v: np.ndarray,
    sigma: float,
    rng: np.random.RandomState,
) -> np.ndarray:
    """Single-sample reception. No modulation. received = v + noise.
    This is the BASELINE (no lock-in advantage)."""
    N = v.shape[0]
    noise = rng.randn(N).astype(np.float64) * sigma
    return v + noise


def arm_noise_floor_decode(
    v: np.ndarray,
    rng: np.random.RandomState,
) -> np.ndarray:
    """Chance retrieval: random vector with no signal content."""
    return rng.randn(v.shape[0]).astype(np.float64)


def recall_at_1(received: np.ndarray, codebook: np.ndarray, target_idx: int) -> int:
    """Return 1 if argmax(codebook @ received) == target_idx else 0."""
    scores = codebook @ received
    return int(np.argmax(scores) == target_idx)


# ---------------------------------------------------------------------------
# Per-grid-point: compute recall for each arm
# ---------------------------------------------------------------------------
def run_grid_point(
    snr_input: float,
    t_int: int,
    n_dim: int,
    seed: int,
) -> Dict:
    """Run one (snr_input, t_int, n_dim) grid point: M codebook entries, N_EVAL queries.

    sigma = 1/snr_input (the additive-noise std at the receiver).
    """
    t0 = time.time()
    rng = np.random.RandomState(seed * 1_000_003 + int(snr_input * 1e6) + t_int * 13 + n_dim)
    rng_eval = np.random.RandomState(seed * 7919 + int(snr_input * 1e6) + t_int * 7 + n_dim + 1)

    # Bipolar codebook (substrate convention: per-coord +/- 1)
    codebook = rng.choice([-1.0, 1.0], size=(M_CODEBOOK, n_dim)).astype(np.float64)

    sigma = 1.0 / snr_input

    lock_in_correct = 0
    direct_correct = 0
    noise_floor_correct = 0
    for q in range(N_EVAL):
        target_idx = int(rng_eval.randint(M_CODEBOOK))
        v = codebook[target_idx]
        # Independent RNG per query to keep noise realizations decoupled
        rng_lock_in = np.random.RandomState(rng_eval.randint(0, 2**31 - 1))
        rng_direct = np.random.RandomState(rng_eval.randint(0, 2**31 - 1))
        rng_floor = np.random.RandomState(rng_eval.randint(0, 2**31 - 1))

        lock_in_recv = arm_lock_in_decode(
            v, t_int=t_int, sigma=sigma, freq=SIGNAL_FREQ, rng=rng_lock_in,
        )
        direct_recv = arm_direct_decode(v, sigma=sigma, rng=rng_direct)
        floor_recv = arm_noise_floor_decode(v, rng=rng_floor)

        lock_in_correct += recall_at_1(lock_in_recv, codebook, target_idx)
        direct_correct += recall_at_1(direct_recv, codebook, target_idx)
        noise_floor_correct += recall_at_1(floor_recv, codebook, target_idx)

    lock_in_recall = lock_in_correct / float(N_EVAL)
    direct_recall = direct_correct / float(N_EVAL)
    noise_floor_recall = noise_floor_correct / float(N_EVAL)

    elapsed = time.time() - t0

    # Predicted lock-in SNR_output (textbook): SNR_in * sqrt(t/2)
    snr_output_predicted = snr_input * math.sqrt(max(t_int, 1) / 2.0)

    return {
        "snr_input": float(snr_input),
        "integration_time": int(t_int),
        "n_dim": int(n_dim),
        "signal_freq": float(SIGNAL_FREQ),
        "M": int(M_CODEBOOK),
        "N_EVAL": int(N_EVAL),
        "snr_output_predicted": float(snr_output_predicted),
        "ARM_LOCK_IN": {
            "recall_at_1": float(lock_in_recall),
            "n_correct": int(lock_in_correct),
        },
        "ARM_DIRECT_COSINE": {
            "recall_at_1": float(direct_recall),
            "n_correct": int(direct_correct),
        },
        "ARM_NOISE_FLOOR": {
            "recall_at_1": float(noise_floor_recall),
            "n_correct": int(noise_floor_correct),
        },
        "lock_in_minus_direct": float(lock_in_recall - direct_recall),
        "wall_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Per-seed driver: sweep the grid
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    grid_points: List[Dict] = []
    point_idx = 0
    for snr in SNR_INPUT_AXIS:
        for t_int in INTEGRATION_TIME_AXIS:
            for nd in N_AXIS:
                point_idx += 1
                t_pt = time.time()
                result = run_grid_point(
                    snr_input=snr, t_int=t_int, n_dim=nd, seed=seed,
                )
                grid_points.append(result)
                print(
                    f"  [seed={seed} pt={point_idx}/{EXPECTED_N_UNITS}] "
                    f"SNR_in={snr} t={t_int} N={nd} "
                    f"SNR_out_pred={result['snr_output_predicted']:.3f} "
                    f"L={result['ARM_LOCK_IN']['recall_at_1']:.3f} "
                    f"D={result['ARM_DIRECT_COSINE']['recall_at_1']:.3f} "
                    f"F={result['ARM_NOISE_FLOOR']['recall_at_1']:.3f} "
                    f"L-D={result['lock_in_minus_direct']:+.3f} "
                    f"wall={time.time()-t_pt:.1f}s",
                    flush=True,
                )
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_grid_points": len(grid_points),
        "expected_n_units": EXPECTED_N_UNITS,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "grid_points": grid_points,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Self-tests (formula correctness)
# ---------------------------------------------------------------------------
def _selftest_clean_endpoint_lock_in() -> bool:
    """At sigma=0, ARM_LOCK_IN recovers signal exactly (modulo cos^2 sum factor).

    (2/t) * sum_p cos^2(2*pi*f*p) approaches 1.0 for incommensurate f and large t.
    For f=0.1 t=10 the sum is exactly periodic over 10 samples:
      sum_p cos^2(2*pi*0.1*p) for p=0..9 = 5.0 -> norm factor = 5/10 * 2 = 1.0 exactly.
    """
    N_t = 512
    rng = np.random.RandomState(13)
    v = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    decoded = arm_lock_in_decode(v, t_int=10, sigma=0.0, freq=SIGNAL_FREQ, rng=rng)
    # Norm factor = (2/10) * sum_{p=0..9} cos^2(2*pi*0.1*p)
    carriers = _carrier(10, SIGNAL_FREQ)
    expected_factor = (2.0 / 10.0) * float(np.sum(carriers ** 2))
    expected = expected_factor * v
    diff = float(np.max(np.abs(decoded - expected)))
    assert diff < 1e-10, (
        f"clean-endpoint lock-in FAIL: max|diff|={diff} expected_factor={expected_factor}"
    )
    # For f=0.1 t=10, expected_factor MUST be exactly 1.0 (sum of cos^2 over a full
    # period = t/2 = 5; norm = 2/10 * 5 = 1).
    assert abs(expected_factor - 1.0) < 1e-10, (
        f"f=0.1 t=10 cos^2 sum norm should be 1.0; got {expected_factor}"
    )
    return True


def _selftest_clean_direct_recall_one() -> bool:
    """At sigma=0, ARM_DIRECT recovers signal trivially -> recall=1.0 on a tiny codebook."""
    N_t = 256
    M_t = 20
    rng = np.random.RandomState(17)
    codebook = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    n_correct = 0
    for q in range(50):
        target = int(rng.randint(M_t))
        v = codebook[target]
        recv = arm_direct_decode(v, sigma=0.0, rng=rng)
        scores = codebook @ recv
        n_correct += int(np.argmax(scores) == target)
    recall = n_correct / 50.0
    assert recall >= 0.99, f"clean-endpoint direct recall FAIL: recall={recall}"
    return True


def _selftest_noise_floor_at_chance() -> bool:
    """ARM_NOISE_FLOOR recall ~= 1/M (chance retrieval).

    For M=20, chance = 0.05. Allow [0, 0.20] for stats on n_eval=200 trials.
    """
    N_t = 256
    M_t = 20
    rng = np.random.RandomState(23)
    codebook = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    n_correct = 0
    n_eval = 200
    for q in range(n_eval):
        target = int(rng.randint(M_t))
        v = codebook[target]
        recv = arm_noise_floor_decode(v, rng=rng)
        scores = codebook @ recv
        n_correct += int(np.argmax(scores) == target)
    recall = n_correct / float(n_eval)
    # Chance = 0.05; allow wide band for stats.
    assert 0.0 <= recall <= 0.20, (
        f"noise-floor chance recall FAIL: recall={recall:.3f} expected ~ {1.0/M_t}"
    )
    return True


def _selftest_cos2_normalization() -> bool:
    """(2/t) * sum_p cos^2(2*pi*0.1*p) for t in {10,100,1000,10000} converges to 1.0."""
    for t_int in [10, 100, 1000, 10000]:
        carriers = _carrier(t_int, SIGNAL_FREQ)
        norm = (2.0 / t_int) * float(np.sum(carriers ** 2))
        # f=0.1 with t multiple of 10 -> exact 1.0.  For other t (not multiple of 10)
        # there is a small residual.
        assert abs(norm - 1.0) < 0.01, (
            f"t={t_int}: (2/t)*sum cos^2 = {norm}; expected ~1.0"
        )
    return True


def _selftest_lock_in_discriminator_fires_at_mid() -> bool:
    """At SNR_in=0.01, t=1000, N=2048: LOCK_IN.recall - DIRECT.recall >= 0.30.

    SNR_out for lock-in = 0.01 * sqrt(500) = 0.224 (above-cliff for bipolar codebook).
    SNR_out for direct  = 0.01 (well below-cliff -> recall ~ 0).
    Probe 2026-06-28: LOCK=1.000 DIRECT=0.000 delta=+1.000 at this config.
    """
    # Use the production run_grid_point at MID config; this is the smoke gate.
    result = run_grid_point(snr_input=0.01, t_int=1000, n_dim=2048, seed=7)
    L = result["ARM_LOCK_IN"]["recall_at_1"]
    D = result["ARM_DIRECT_COSINE"]["recall_at_1"]
    delta = L - D
    assert delta >= 0.30, (
        f"MID-regime discriminator did NOT fire: LOCK_IN={L:.3f} DIRECT={D:.3f} "
        f"delta={delta:.3f} (expected >= 0.30 at SNR=0.01 t=1000 N=2048)"
    )
    return True


def _instrumentation_selftest() -> None:
    _selftest_clean_endpoint_lock_in()
    _selftest_clean_direct_recall_one()
    _selftest_noise_floor_at_chance()
    _selftest_cos2_normalization()
    _selftest_lock_in_discriminator_fires_at_mid()
    print(
        f"[selftest] PASS  mode={RUN_MODE}  axes(SNR,t,N)="
        f"{SNR_INPUT_AXIS}x{INTEGRATION_TIME_AXIS}x{N_AXIS}  "
        f"freq={SIGNAL_FREQ}  M={M_CODEBOOK}  N_eval={N_EVAL}  "
        f"expected_n_units={EXPECTED_N_UNITS}  seed={SEED_DEFAULT}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------
def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode gate violated.")

    # CARDINALITY_OK: each seed must have EXPECTED_N_UNITS points.
    for r in results:
        n_obs = r.get("n_grid_points", 0)
        if n_obs < EXPECTED_N_UNITS:
            return ("HARD_FAIL",
                    f"HARD_FAIL_CARDINALITY_BREACH: seed={r.get('seed')} "
                    f"observed {n_obs} grid points; expected {EXPECTED_N_UNITS}.")

    # Aggregate grid-points across seeds.
    all_points: List[Dict] = []
    for r in results:
        all_points.extend(r.get("grid_points", []))

    n_points = len(all_points)
    if n_points == 0:
        return ("HARD_FAIL", "HARD_FAIL: no grid points.")

    lock_in_recalls = np.array([p["ARM_LOCK_IN"]["recall_at_1"] for p in all_points])
    direct_recalls = np.array([p["ARM_DIRECT_COSINE"]["recall_at_1"] for p in all_points])
    floor_recalls = np.array([p["ARM_NOISE_FLOOR"]["recall_at_1"] for p in all_points])
    delta_LD = lock_in_recalls - direct_recalls

    # HARD_FAIL_NOISE_FLOOR_LEAK: chance baseline broken.
    if np.any(floor_recalls > 0.10):
        offenders = int(np.sum(floor_recalls > 0.10))
        return ("HARD_FAIL",
                f"HARD_FAIL_NOISE_FLOOR_LEAK: ARM_NOISE_FLOOR.recall > 0.10 at "
                f"{offenders}/{n_points} grid points; chance baseline broken; "
                f"cell wiring bug.")

    chance_thresh = 1.5 / float(M_CODEBOOK)  # = 0.015 for M=100

    # HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR (on primary mechanism arm).
    if np.all(lock_in_recalls >= 0.99):
        return ("HARD_FAIL",
                f"HARD_FAIL_BY_CONSTRUCTION_SAT: ARM_LOCK_IN.recall >= 0.99 at "
                f"every point ({n_points} points); ceiling saturated; grid too easy.")
    if np.all(lock_in_recalls <= chance_thresh):
        return ("HARD_FAIL",
                f"HARD_FAIL_BY_CONSTRUCTION_FLOOR: ARM_LOCK_IN.recall <= {chance_thresh:.3f} "
                f"at every point ({n_points} points); mechanism floored.")

    # HARD_FAIL_ARMS_IDENTICAL.
    n_identical = int(np.sum(np.abs(delta_LD) < 0.02))
    if n_identical >= int(0.90 * n_points):
        return ("HARD_FAIL",
                f"HARD_FAIL_ARMS_IDENTICAL: |LOCK_IN - DIRECT| < 0.02 at "
                f"{n_identical}/{n_points} (>= 90%) grid points; lock-in mechanism "
                f"not firing.")

    # PHASE-MAP regime classification.
    sat_mask = (lock_in_recalls >= 0.95) & (direct_recalls >= 0.95)
    floor_mask = (lock_in_recalls <= chance_thresh) & (direct_recalls <= chance_thresh)
    advantage_mask = delta_LD >= 0.30
    discriminating_mask = (
        (np.abs(delta_LD) > 0.05) | sat_mask | floor_mask
    )

    n_sat = int(np.sum(sat_mask))
    n_floor = int(np.sum(floor_mask))
    n_advantage = int(np.sum(advantage_mask))
    n_discrim = int(np.sum(discriminating_mask))

    pct_thresh = max(1, int(math.ceil(0.20 * n_points)))
    discrim_floor = max(1, int(math.ceil(0.50 * n_points)))

    summary = (
        f"n_points={n_points} "
        f"lock_in_recall_mean={lock_in_recalls.mean():.3f} "
        f"(min={lock_in_recalls.min():.3f}, max={lock_in_recalls.max():.3f}); "
        f"direct_recall_mean={direct_recalls.mean():.3f}; "
        f"floor_recall_mean={floor_recalls.mean():.3f}; "
        f"delta_LD_mean={delta_LD.mean():+.3f}; "
        f"n_SAT(L>=0.95 AND D>=0.95)={n_sat}/{n_points} (need >= {pct_thresh}); "
        f"n_FLOOR(L<={chance_thresh:.3f} AND D<={chance_thresh:.3f})={n_floor}/{n_points} "
        f"(need >= {pct_thresh}); "
        f"n_ADVANTAGE(L-D>=0.30)={n_advantage}/{n_points} (need >= {pct_thresh}); "
        f"n_DISCRIMINATING={n_discrim}/{n_points} (need >= {discrim_floor})"
    )

    hp_sat = n_sat >= pct_thresh
    hp_floor = n_floor >= pct_thresh
    hp_advantage = n_advantage >= pct_thresh
    hp_discrim = n_discrim >= discrim_floor

    if all([hp_sat, hp_floor, hp_advantage, hp_discrim]):
        return ("HARD_PASS",
                f"HARD_PASS phase-map: SNR phase diagram populated in all 3 regimes "
                f"(SAT / FLOOR / LOCK-IN-ADVANTAGE) at >= 20% each, and "
                f"discriminating at >= 50%. Lock-in amp phase coverage "
                f"PARTIAL -> HIGH. {summary}")

    if hp_discrim and (hp_sat or hp_advantage or hp_floor):
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: phase diagram discriminating at >= 50% but not "
                f"all 3 regimes populated at >= 20%. "
                f"hp=[sat={hp_sat},floor={hp_floor},adv={hp_advantage},"
                f"discrim={hp_discrim}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: phase diagram does not clear PASS or MIDDLE bands. "
            f"hp=[sat={hp_sat},floor={hp_floor},adv={hp_advantage},"
            f"discrim={hp_discrim}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {
    "SNR_INPUT_AXIS": list(SNR_INPUT_AXIS),
    "INTEGRATION_TIME_AXIS": list(INTEGRATION_TIME_AXIS),
    "N_AXIS": list(N_AXIS),
    "run_mode": RUN_MODE,
    "anchor": ANCHOR_NAME,
}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] lock-in amp phase-diagram v1 "
        f"axes(SNR,t,N)={SNR_INPUT_AXIS}x{INTEGRATION_TIME_AXIS}x{N_AXIS} "
        f"freq={SIGNAL_FREQ} M={M_CODEBOOK} N_eval={N_EVAL} "
        f"expected_n_units={EXPECTED_N_UNITS} mode={RUN_MODE}",
        flush=True,
    )
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start

mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} "
        f"axes(SNR,t,N)={SNR_INPUT_AXIS}x{INTEGRATION_TIME_AXIS}x{N_AXIS} "
        f"freq={SIGNAL_FREQ} M={M_CODEBOOK} N_eval={N_EVAL} "
        f"expected_n_units={EXPECTED_N_UNITS} mode={RUN_MODE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "SNR_INPUT_AXIS": list(SNR_INPUT_AXIS),
    "INTEGRATION_TIME_AXIS": list(INTEGRATION_TIME_AXIS),
    "N_AXIS": list(N_AXIS),
    "signal_freq": float(SIGNAL_FREQ),
    "M_codebook": int(M_CODEBOOK),
    "N_EVAL": int(N_EVAL),
    "expected_n_units": int(EXPECTED_N_UNITS),
    "n_seeds": len(SEEDS),
    "seeds": list(SEEDS),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "n_grid_points": r.get("n_grid_points"),
            "grid_points": r.get("grid_points"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
