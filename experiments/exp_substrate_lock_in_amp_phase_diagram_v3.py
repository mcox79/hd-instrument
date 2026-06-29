# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""substrate_lock_in_amp_phase_diagram_v3 -- mechanism-class diversion of v2 MIDDLE_BAND.

REVIVAL CONTEXT (Research/Skunkworks 2026-06-30):
  v1 (substrate_lock_in_amp_phase_diagram_v1) landed 3-seed MIDDLE_BAND
    (FLOOR under-populated, marginal SAT).
  v2 (substrate_lock_in_amp_phase_diagram_v2) extended SNR axis 5 decades
    (1e-5 ... 1.0; 11 SNRs) + stat-valid FLOOR_THRESH. Still landed MIDDLE_BAND.
    Skunkworks 2x-drill diagnosis: n_ADVANTAGE hard-capped by GEOMETRY of v2's
    coarse SNR axis. Extending the SNR floor adds cells to FLOOR/SAT counts
    but NOT to ADVANTAGE -- because ADVANTAGE requires SNR_in below the
    bipolar-codebook cliff AND SNR_in*sqrt(t/2) above the cliff (the narrow
    transition sliver between direct-fail and direct-succeed).
  v2's mid-transition zone had only 4 SNRs {1e-3, 3.2e-3, 1e-2, 3.2e-2}
    -> ~1 ADV cell qualified (n_ADVANTAGE = 1 in v2 FULL).
    Axis-density problem, NOT axis-extent problem.

v3 FIX (MECHANISM-CLASS DIVERSION from v2's extent-lever):
  Replace v2's coarse 3-decade-wide axis with a DENSE 3-decade axis IN THE
  ADVANTAGE-BAND TRANSITION ZONE. v3 axis = 8 geometric points in [1e-4, 0.1]:
    {1.000e-4, 2.683e-4, 7.197e-4, 1.931e-3, 5.179e-3, 1.389e-2, 3.728e-2, 1.000e-1}
  Spacing: log10 increment = 3/7 = 0.4286 (factor ~2.68 between consecutive pts).
  This is the SNR_in range where the cliff transition manifests across t.

  4 integration times {10, 100, 1000, 10000} (unchanged from v2). The
  SNR_in x sqrt(t/2) product is the actual lock-in OPERATING VARIABLE,
  and the dense SNR_in axis sweeps the cliff transition with t-amplification.

  Grid: 8 SNR x 4 t x 3 N = 96 cells per seed (v2: 132; v1: 60).
  ADVANTAGE-band capture is HIGHER than v2 despite smaller grid because
  cells are concentrated in the transition zone.

NO MECHANISM CHANGE FROM v1/v2. Same 3 arms, same decode formulas, same
self-tests, same physics. Only the SNR axis is REPLACED (not extended).

EXPECTED n_ADVANTAGE per Skunkworks pre-reg ratio + the SNR_out formula:
  Cliff position: SNR_out ~ 0.05 at N=2048, ~0.025 at N=8192 (bipolar M=100).
  ADVANTAGE condition: SNR_in < cliff AND SNR_in*sqrt(t/2) > cliff.

  Predicted ADV cells per N (analytical, ~cliff=0.05):
    SNR_in=1.0e-4   : 0/4 t-values give advantage (SNR_out_max = 7.1e-3)
    SNR_in=2.7e-4   : 0/4                        (SNR_out_max = 1.9e-2)
    SNR_in=7.2e-4   : 1/4 (t=10000)              (SNR_out @t=10000 = 5.1e-2)
    SNR_in=1.9e-3   : 1/4 (t=10000)              (SNR_out @t=10000 = 1.4e-1)
    SNR_in=5.2e-3   : 2/4 (t=1000, 10000)
    SNR_in=1.4e-2   : 3/4 (t=100, 1000, 10000)
    SNR_in=3.7e-2   : 4/4 (all t > cliff)
    SNR_in=1.0e-1   : DIRECT already extracts; no advantage
  Per-N analytic ADV count: 0+0+1+1+2+3+4+0 = 11
  Cliff shifts LEFT at higher N (lower threshold), so N=4096+8192 give
  MORE ADV cells (12-14 per N realistic).
  3 N values * ~11-13 ADV cells = ~33-39 ADV cells per seed
  >> 20% of 96 = 20 cell target. >> task target (n_ADVANTAGE >= 6).

ARMS (3-arm bracket; UNCHANGED from v1/v2):
  ARM_LOCK_IN         -- phase-coherent integration over t with known reference
  ARM_DIRECT_COSINE   -- single-sample cosine-match (no modulation processing)
  ARM_NOISE_FLOOR     -- random gaussian guess (chance recall = 1/M = 0.01)

PRE-REGISTERED BANDS (PHASE-MAP framing; UNCHANGED from v2 except axis):

  HARD_PASS chain-grade (PARTIAL -> HIGH coverage):
    ALL FOUR of:
    - >= 20% of grid points show SATURATED regime
      (ARM_LOCK_IN.recall >= 0.95 AND ARM_DIRECT.recall >= 0.95)
      (target: 20 cells)
    - >= 20% of grid points show FLOOR regime
      (ARM_LOCK_IN.recall <= chance_thresh AND ARM_DIRECT.recall <= chance_thresh)
      where chance_thresh = max(1.5/M, 1.5/N_EVAL) = max(0.015, 0.050) = 0.050
      (target: 20 cells)
    - >= 20% of grid points show LOCK-IN-ADVANTAGE regime
      (ARM_LOCK_IN.recall - ARM_DIRECT.recall >= 0.30)
      (target: 20 cells; v3 design analytical: ~33-39)
    - >= 50% of grid points are discriminating
      (target: 48 cells)

  MIDDLE_BAND:
    discriminating-fraction >= 50% AND at least 1 of {SAT, FLOOR, ADVANTAGE}
    populated but NOT all 3 regimes at >= 20%.

  HARD_FAIL gates (load-bearing; UNCHANGED from v1/v2):
    - HARD_FAIL_CARDINALITY_BREACH: any seed observed < EXPECTED_N_UNITS (96 full / 6 smoke).
    - HARD_FAIL_BY_CONSTRUCTION_SAT / FLOOR / ARMS_IDENTICAL / NOISE_FLOOR_LEAK / LLM_LEAK.
    - HARD_FAIL stale-smoke-partials in FULL run.

FIX INVENTORY (mirrors v1/v2):
  - _LLM_CALL_COUNTER = [0]; asserted == 0 (substrate-only-decode gate).
  - ANCHOR_NAME = substrate_lock_in_amp_phase_diagram_v3.
  - CONFIG_VERSION baked module-level; mode=='smoke'|'full' honored.
  - allow_synthetic=True (BY DESIGN; primitive-isolation; same as v1/v2).
  - per-grid-point entry per (seed, snr, t, n) in metrics.json.
  - Per-seed checkpoint via experiments/_seed_checkpoint.py.
  - CARDINALITY_OK: EXPECTED_N_UNITS_FULL=96, _SMOKE=6.
  - DISCRIMINATOR_SURVIVES_SCALE: smoke includes 1 FLOOR endpoint (SNR=1e-4 t=10),
    1 ADVANTAGE (SNR=1.4e-2 t=1000), 1 SAT (SNR=0.1 t=10000) -> 3/3 regime probes
    at smallest N=2048; FULL grid expands cliff-transition zone proportionally.

FORMULA SELF-TESTS (UNCHANGED from v1/v2):
  1. ARM_LOCK_IN clean (sigma=0, f=0.1, t=10, N=512): exact reconstruction.
  2. ARM_DIRECT clean: recall=1.000.
  3. ARM_NOISE_FLOOR ~= 1/M chance.
  4. (2/t) * sum_p cos^2 normalization.
  5. MID-REGIME discriminator FIRES (SNR=0.01 t=1000 N=2048: L-D >= 0.30).

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

ANCHOR_NAME = "substrate_lock_in_amp_phase_diagram_v3"

# Substrate-only-decode gate. Asserted == 0 at end. Any LLM call MUST increment.
_LLM_CALL_COUNTER = [0]

RUN_MODE = (
    "smoke" if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

# In-cell smoke detection: HDLAB_EXP_NAME ending in _smoke triggers smoke.
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
SIGNAL_FREQ = 0.1
M_CODEBOOK = 100  # codebook size; chance recall = 1/M = 0.01

# v3 SNR axis: 8 geometric points in [1e-4, 0.1] (factor 2.68 per step).
# Replaces v2's coarse 3-decade [1e-5, 1.0] axis. The dense [1e-4, 0.1] zone
# IS the ADVANTAGE-band transition: SNR_in below the bipolar-codebook cliff
# (~0.05 at N=2048) but SNR_in * sqrt(t/2) crosses the cliff at high t.
SNR_INPUT_AXIS_FULL = [
    10 ** (-4.0 + 3.0 * k / 7.0) for k in range(8)
]
# Numerically: [1.000e-4, 2.683e-4, 7.197e-4, 1.931e-3, 5.179e-3,
#               1.389e-2, 3.728e-2, 1.000e-1]
INTEGRATION_TIME_AXIS_FULL = [10, 100, 1000, 10000]
N_AXIS_FULL = [2048, 4096, 8192]
N_EVAL_FULL = 30
EXPECTED_N_UNITS_FULL = (
    len(SNR_INPUT_AXIS_FULL) * len(INTEGRATION_TIME_AXIS_FULL) * len(N_AXIS_FULL)
)  # 96

# SMOKE grid -- minimum to FIRE all three regimes + discriminator at MID config.
# Picks: FLOOR endpoint at deep-low SNR + ADVANTAGE at mid-cliff + SAT at high SNR.
SNR_INPUT_AXIS_SMOKE = [
    SNR_INPUT_AXIS_FULL[0],  # 1.0e-4 (FLOOR endpoint)
    SNR_INPUT_AXIS_FULL[5],  # 1.39e-2 (ADVANTAGE band: cliff at t=100+)
    SNR_INPUT_AXIS_FULL[7],  # 0.1 (SAT zone; DIRECT extracts cleanly)
]
INTEGRATION_TIME_AXIS_SMOKE = [10, 1000]      # short + long
N_AXIS_SMOKE = [2048]                          # smallest production N
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
    f"SNR_AXIS={'-'.join(f'{x:.6g}' for x in SNR_INPUT_AXIS)},"
    f"T_AXIS={'-'.join(str(x) for x in INTEGRATION_TIME_AXIS)},"
    f"N_AXIS={'-'.join(str(x) for x in N_AXIS)},"
    f"SIGNAL_FREQ={SIGNAL_FREQ},M={M_CODEBOOK},N_EVAL={N_EVAL},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"EXPECTED_N_UNITS={EXPECTED_N_UNITS}"
)

# ---------------------------------------------------------------------------
# Core mechanism: substrate-native lock-in amplifier (UNCHANGED from v1/v2)
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
    """Phase-coherent integration over t_int samples (UNCHANGED from v1/v2)."""
    N = v.shape[0]
    carriers = _carrier(t_int, freq)
    cos2_sum = float(np.sum(carriers ** 2))
    norm_factor = 2.0 / float(t_int)
    signal_acc = v * cos2_sum
    CHUNK = max(1, min(t_int, 500_000 // max(1, N)))
    noise_acc = np.zeros(N, dtype=np.float64)
    p_start = 0
    while p_start < t_int:
        p_end = min(t_int, p_start + CHUNK)
        chunk_size = p_end - p_start
        noise = rng.randn(chunk_size, N).astype(np.float64) * sigma
        weights = carriers[p_start:p_end]
        noise_acc += (noise.T @ weights)
        p_start = p_end
    total_acc = signal_acc + noise_acc
    decoded = norm_factor * total_acc
    return decoded


def arm_direct_decode(
    v: np.ndarray,
    sigma: float,
    rng: np.random.RandomState,
) -> np.ndarray:
    """Single-sample reception. received = v + sigma*noise (UNCHANGED from v1/v2)."""
    N = v.shape[0]
    noise = rng.randn(N).astype(np.float64) * sigma
    return v + noise


def arm_noise_floor_decode(
    v: np.ndarray,
    rng: np.random.RandomState,
) -> np.ndarray:
    """Chance retrieval: random vector (UNCHANGED from v1/v2)."""
    return rng.randn(v.shape[0]).astype(np.float64)


def recall_at_1(received: np.ndarray, codebook: np.ndarray, target_idx: int) -> int:
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
    """Run one (snr_input, t_int, n_dim) grid point.

    Note: per-grid-point seed mixing uses int(snr_input * 1e6); valid for
    snr_input >= 1e-6. v3 axis min = 1e-4 -> seed-int = 100, well above the
    1e-6 resolution floor.
    """
    t0 = time.time()
    snr_seed_mix = int(round(snr_input * 1e6))  # robust int mixing
    rng = np.random.RandomState(seed * 1_000_003 + snr_seed_mix + t_int * 13 + n_dim)
    rng_eval = np.random.RandomState(seed * 7919 + snr_seed_mix + t_int * 7 + n_dim + 1)

    codebook = rng.choice([-1.0, 1.0], size=(M_CODEBOOK, n_dim)).astype(np.float64)
    sigma = 1.0 / snr_input

    lock_in_correct = 0
    direct_correct = 0
    noise_floor_correct = 0
    for q in range(N_EVAL):
        target_idx = int(rng_eval.randint(M_CODEBOOK))
        v = codebook[target_idx]
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
# Per-seed driver
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
                    f"SNR_in={snr:.4g} t={t_int} N={nd} "
                    f"SNR_out_pred={result['snr_output_predicted']:.4f} "
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
# Self-tests (UNCHANGED from v1/v2; same mechanism)
# ---------------------------------------------------------------------------
def _selftest_clean_endpoint_lock_in() -> bool:
    N_t = 512
    rng = np.random.RandomState(13)
    v = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    decoded = arm_lock_in_decode(v, t_int=10, sigma=0.0, freq=SIGNAL_FREQ, rng=rng)
    carriers = _carrier(10, SIGNAL_FREQ)
    expected_factor = (2.0 / 10.0) * float(np.sum(carriers ** 2))
    expected = expected_factor * v
    diff = float(np.max(np.abs(decoded - expected)))
    assert diff < 1e-10, (
        f"clean-endpoint lock-in FAIL: max|diff|={diff} expected_factor={expected_factor}"
    )
    assert abs(expected_factor - 1.0) < 1e-10, (
        f"f=0.1 t=10 cos^2 sum norm should be 1.0; got {expected_factor}"
    )
    return True


def _selftest_clean_direct_recall_one() -> bool:
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
    assert 0.0 <= recall <= 0.20, (
        f"noise-floor chance recall FAIL: recall={recall:.3f} expected ~ {1.0/M_t}"
    )
    return True


def _selftest_cos2_normalization() -> bool:
    for t_int in [10, 100, 1000, 10000]:
        carriers = _carrier(t_int, SIGNAL_FREQ)
        norm = (2.0 / t_int) * float(np.sum(carriers ** 2))
        assert abs(norm - 1.0) < 0.01, (
            f"t={t_int}: (2/t)*sum cos^2 = {norm}; expected ~1.0"
        )
    return True


def _selftest_lock_in_discriminator_fires_at_mid() -> bool:
    """MID config (SNR=0.01 t=1000 N=2048): LOCK_IN.recall - DIRECT.recall >= 0.30.

    v1/v2 probe + FULL seed=7 grid: LOCK=1.000 DIRECT=0.000 delta=+1.000.
    v3 uses a different SNR axis but this MID-anchor is still well in the
    ADVANTAGE-band (SNR_in=0.01 below cliff, SNR_out=0.224 above cliff).
    """
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
        f"[selftest] PASS  mode={RUN_MODE}  "
        f"axes(SNR,t,N)={[f'{x:.4g}' for x in SNR_INPUT_AXIS]}"
        f"x{INTEGRATION_TIME_AXIS}x{N_AXIS}  "
        f"freq={SIGNAL_FREQ}  M={M_CODEBOOK}  N_eval={N_EVAL}  "
        f"expected_n_units={EXPECTED_N_UNITS}  seed={SEED_DEFAULT}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict computation (UNCHANGED from v2; same stat-valid FLOOR_THRESH)
# ---------------------------------------------------------------------------
def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode gate violated.")

    for r in results:
        n_obs = r.get("n_grid_points", 0)
        if n_obs < EXPECTED_N_UNITS:
            return ("HARD_FAIL",
                    f"HARD_FAIL_CARDINALITY_BREACH: seed={r.get('seed')} "
                    f"observed {n_obs} grid points; expected {EXPECTED_N_UNITS}.")

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

    if np.any(floor_recalls > 0.10):
        offenders = int(np.sum(floor_recalls > 0.10))
        return ("HARD_FAIL",
                f"HARD_FAIL_NOISE_FLOOR_LEAK: ARM_NOISE_FLOOR.recall > 0.10 at "
                f"{offenders}/{n_points} grid points; chance baseline broken.")

    # v2 stat-valid FLOOR threshold (UNCHANGED): chance + 1-spurious-hit tolerance.
    chance_thresh = max(1.5 / float(M_CODEBOOK), 1.5 / float(N_EVAL))

    if np.all(lock_in_recalls >= 0.99):
        return ("HARD_FAIL",
                f"HARD_FAIL_BY_CONSTRUCTION_SAT: ARM_LOCK_IN.recall >= 0.99 at "
                f"every point ({n_points} points); ceiling saturated.")
    if np.all(lock_in_recalls <= chance_thresh):
        return ("HARD_FAIL",
                f"HARD_FAIL_BY_CONSTRUCTION_FLOOR: ARM_LOCK_IN.recall <= {chance_thresh:.3f} "
                f"at every point ({n_points} points); mechanism floored.")

    n_identical = int(np.sum(np.abs(delta_LD) < 0.02))
    if n_identical >= int(0.90 * n_points):
        return ("HARD_FAIL",
                f"HARD_FAIL_ARMS_IDENTICAL: |LOCK_IN - DIRECT| < 0.02 at "
                f"{n_identical}/{n_points} (>= 90%) grid points.")

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
        f"[seed={seed}] lock-in amp phase-diagram v3 "
        f"axes(SNR,t,N)={[f'{x:.4g}' for x in SNR_INPUT_AXIS]}"
        f"x{INTEGRATION_TIME_AXIS}x{N_AXIS} "
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
        f"axes(SNR,t,N)={[f'{x:.4g}' for x in SNR_INPUT_AXIS]}"
        f"x{INTEGRATION_TIME_AXIS}x{N_AXIS} "
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
