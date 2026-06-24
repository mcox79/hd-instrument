"""
exp_substrate_theta_gamma_nested_oscillation_LM_v1 -- theta-gamma nested oscillation extension.

SCIENTIFIC QUESTION:
  The chain-grade lock-in amplifier (cert ledger row 678) uses a single
  frequency k_signal with P phases. Lisman-Idiart neuroscience model: theta
  oscillation (5 Hz) is the carrier; 7+-2 gamma (40 Hz) sub-cycles per theta
  cycle, each holding ONE item. Does composing two nested HD frequencies
  (k_theta=1 slow carrier + k_gamma=31 fast item) lift recall@1 or sigma
  capacity over the best single-frequency arm?

MECHANISM (two-frequency nested lock-in):
  Single-frequency arm (baseline): demod over P phases of k=31 only.
  Theta-gamma nested arm:
    Each theta phase t in {0..P_theta-1}:
      - encode item at gamma sub-cycle: roll(cue, t*k_theta + p_gamma*k_gamma)
      - weight: cos(2*pi*t/P_theta) * cos(2*pi*p_gamma/P_gamma)
      - add noise per phase
      - demodulate: unroll both frequencies, accumulate
    Normalization: (2/P_theta) * (2/P_gamma) factor pair; equivalent SNR
    reduction factor is sqrt(P_theta*P_gamma/4) per phase pair.
    P_theta*P_gamma = 8*7 = 56; sqrt(56/4) = sqrt(14) ~ 3.74x SNR lift.
    This is LESS than single P=64 (sqrt(32)=5.65x) at equal total phases (56 vs 64).
    The hypothesis: theta-gamma gains from temporal STRUCTURE (items bound to
    theta phase position = sequenced recall) which lifts sigma_capacity at
    recall>=0.95 even if peak-recall lift is lower.

PRE-REGISTERED HARD_PASS (two independent criteria, either suffices):
  CRITERION_A: theta_gamma_recall@1 > single_lock_in_recall@1 by >= 0.10
    at the same discriminating sigma across all 3 seeds.
  CRITERION_B: theta_gamma_sigma_capacity >= 2x single_lock_in_sigma_capacity
    where sigma_capacity = highest sigma at recall@1 >= 0.95.

PRE-REGISTERED HARD_FAIL:
  theta_gamma_recall@1 <= single_lock_in_recall@1 across ALL sigmas tested;
  no sigma where theta-gamma exceeds single-lock-in (nested oscillation adds
  nothing over single-frequency).

MIDDLE_BAND:
  Theta-gamma exceeds single-lock-in at some sigmas but not by >=0.10 margin,
  OR sigma_capacity improvement is in [1.0x, 2.0x). Partial structure benefit.

CONFIG:
  smoke: N=512, M=50, seeds=[7,17], sigmas=[4,8,16,32,64], k_gamma=31, k_theta=1,
         P_theta=4, P_gamma=7, P_single=32 (single-freq baseline)
  full:  N=4096, M=500, seeds=[7,17,23], sigmas=[4,8,16,32,64,128,256],
         k_gamma=31, k_theta=1, P_theta=8, P_gamma=7, P_single=64

ROUTING: remote_cpu_queue (pure CPU; no CUDA; wall expected ~20-40 min at N=4096).
PROT-018: no _n<N> suffix; production N=4096 explicit in config. See NOTE below.
ASCII-only. No emojis. write_metrics with REQUIRED_FIELDS.

NOTE ON N-SUFFIX: anchor name substrate_theta_gamma_nested_oscillation_LM_v1
contains no _n<NUMBER> suffix (per PROT-018 rule 3: explicitly stated here).
Production N = 4096. Rationale: this is a mechanism-comparison cell not a
capacity-scaling cell; N=4096 chosen for CPU tractability on remote_cpu_queue.
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

ANCHOR_NAME = "substrate_theta_gamma_nested_oscillation_LM_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

SMOKE = RUN_MODE == "smoke"

# No CUDA: remote_cpu_queue routing. numpy only.

if SMOKE:
    SEEDS = [7, 17]
    N_DIM = 512
    M = 50
    SIGMAS = [4.0, 8.0, 16.0, 32.0, 64.0]
    K_GAMMA = 31   # fast item frequency
    K_THETA = 1    # slow carrier frequency
    P_THETA = 4    # theta phases (smoke: reduced for speed)
    P_GAMMA = 7    # gamma sub-cycles per theta (Lisman: 7+-2)
    P_SINGLE = 32  # single-frequency baseline P (smoke)
    N_EVAL = 80
else:
    # PRODUCTION config: N=4096, remote_cpu_queue
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    M = 500
    SIGMAS = [4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0]
    K_GAMMA = 31
    K_THETA = 1
    P_THETA = 8    # theta phases (Lisman: 7+-2; use 8 for even-P normalization)
    P_GAMMA = 7    # gamma sub-cycles per theta
    P_SINGLE = 64  # single-frequency baseline P (full)
    N_EVAL = 200

# Pre-registered threshold constants
HP_RECALL_DELTA = 0.10   # CRITERION_A: theta-gamma beats single by >= 0.10 recall
HP_SIGMA_CAP_RATIO = 2.0 # CRITERION_B: theta-gamma sigma_capacity >= 2x single
RECALL_95_THRESH = 0.95  # sigma_capacity definition threshold


# ---- core primitives (pure numpy) ----

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
    Matches exp_lock_in_amplifier_hd_frequency_v1_FULL.py mechanism exactly.
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
    """Two-frequency nested oscillation lock-in (Lisman-Idiart substrate model).

    Each (t, g) phase pair:
      shift = t*k_theta + g*k_gamma
      carrier = cos(2*pi*t/P_theta) * cos(2*pi*g/P_gamma)
      transmitted_tg = roll(cue, shift) * carrier
      received_tg = transmitted_tg + noise_tg
      demod_tg = roll(received_tg, -shift) * carrier
    decoded = (2/P_theta) * (2/P_gamma) * sum_{t,g} demod_{t,g}

    Signal term: (2/P_theta)*(2/P_gamma)*sum_t cos^2(2pi*t/P_theta)*sum_g cos^2(2pi*g/P_gamma)
    = (2/P_theta)*(P_theta/2) * (2/P_gamma)*(P_gamma/2) * cue = cue  (for P>=3 even or P=P_gamma=7 approx)
    Noise variance per term: sigma^2; total phases = P_theta*P_gamma
    Factor = (2/P_theta)^2 * (2/P_gamma)^2 * sigma^2 * sum noise = (4/P_theta*P_gamma) * sigma^2
    SNR lift ~ sqrt(P_theta*P_gamma/4)
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


def recall_at_1(decoded: np.ndarray, codebook: np.ndarray, target_indices: np.ndarray) -> float:
    """Nearest-neighbor recall@1 in codebook. decoded: (B, N); codebook: (M, N)."""
    # scores: (B, M) = decoded @ codebook.T
    scores = decoded @ codebook.T
    pred = scores.argmax(axis=-1)
    return float((pred == target_indices).mean())


# ---- self-tests (formula correctness) ----

def _selftest_single_lockin_p1_endpoint() -> None:
    """P=1 single-frequency lock-in must equal baseline (add noise only)."""
    rng_a = np.random.default_rng(42)
    rng_b = np.random.default_rng(42)
    cues = rng_a.standard_normal((4, 64)).astype(np.float32)
    sigma = 0.5
    out_a = single_lockin_demod(cues.copy(), P=1, k_signal=31, sigma=sigma, rng=np.random.default_rng(7))
    out_b = single_lockin_demod(cues.copy(), P=1, k_signal=31, sigma=sigma, rng=np.random.default_rng(7))
    diff = float(np.abs(out_a - out_b).max())
    assert diff < 1e-9, f"P=1 determinism FAIL: diff={diff}"


def _selftest_single_lockin_sigma0() -> None:
    """sigma=0: single_lockin_demod recovers signal with known normalization factor."""
    N_t = 64
    for P_t in [4, 8, 32]:
        cue = np.random.default_rng(9).standard_normal((3, N_t)).astype(np.float32)
        rng = np.random.default_rng(11)
        out = single_lockin_demod(cue, P=P_t, k_signal=31, sigma=0.0, rng=rng)
        sum_cos2 = sum(math.cos(2.0 * math.pi * p / P_t) ** 2 for p in range(P_t))
        expected_factor = (2.0 / P_t) * sum_cos2
        expected = expected_factor * cue
        diff = float(np.abs(out - expected).max())
        assert diff < 1e-4, f"single_lockin sigma=0 recovery FAIL at P={P_t}: diff={diff}"
        assert abs(expected_factor - 1.0) < 1e-6, f"normalization off at P={P_t}: {expected_factor}"


def _selftest_theta_gamma_sigma0() -> None:
    """sigma=0: theta_gamma_nested_demod recovers signal up to joint normalization factor."""
    N_t = 64
    P_th, P_gm = 4, 4  # use even P for exact cos^2 identity
    cue = np.random.default_rng(13).standard_normal((2, N_t)).astype(np.float32)
    rng = np.random.default_rng(17)
    out = theta_gamma_nested_demod(cue, P_theta=P_th, P_gamma=P_gm,
                                    k_theta=1, k_gamma=31, sigma=0.0, rng=rng)
    # Expected: (2/P_th)*sum_t cos^2(t) * (2/P_gm)*sum_g cos^2(g) * cue
    s_th = sum(math.cos(2.0 * math.pi * t / P_th) ** 2 for t in range(P_th))
    s_gm = sum(math.cos(2.0 * math.pi * g / P_gm) ** 2 for g in range(P_gm))
    factor = (2.0 / P_th) * s_th * (2.0 / P_gm) * s_gm
    expected = factor * cue
    diff = float(np.abs(out - expected).max())
    assert diff < 1e-4, f"theta_gamma sigma=0 recovery FAIL: diff={diff} factor={factor}"
    assert abs(factor - 1.0) < 1e-5, f"joint normalization off: {factor}"


def _selftest_recall_nontrivial() -> None:
    """At sigma=0, both arms should achieve recall@1 = 1.000 on a tiny codebook."""
    N_t, M_t = 128, 20
    rng = np.random.default_rng(55)
    codebook = rng.standard_normal((M_t, N_t)).astype(np.float32)
    # Normalize rows to unit length for cosine recall
    norms = np.linalg.norm(codebook, axis=-1, keepdims=True)
    codebook = codebook / (norms + 1e-9)
    targets = np.array([0, 5, 10, 15])
    cues = codebook[targets]

    # Single lock-in, sigma=0 -> decoded = cue (exact or factor*cue)
    decoded_s = single_lockin_demod(cues.copy(), P=8, k_signal=31, sigma=0.0, rng=np.random.default_rng(0))
    r_s = recall_at_1(decoded_s, codebook, targets)
    assert r_s >= 0.99, f"single_lockin sigma=0 recall FAIL: {r_s:.4f} (expected ~1.0)"

    decoded_tg = theta_gamma_nested_demod(cues.copy(), P_theta=4, P_gamma=4,
                                           k_theta=1, k_gamma=31, sigma=0.0,
                                           rng=np.random.default_rng(0))
    r_tg = recall_at_1(decoded_tg, codebook, targets)
    assert r_tg >= 0.99, f"theta_gamma sigma=0 recall FAIL: {r_tg:.4f} (expected ~1.0)"

    print(f"  [selftest] sigma=0 recall: single={r_s:.4f} theta_gamma={r_tg:.4f}", flush=True)


def _instrumentation_selftest() -> None:
    _selftest_single_lockin_p1_endpoint()
    _selftest_single_lockin_sigma0()
    _selftest_theta_gamma_sigma0()
    _selftest_recall_nontrivial()
    print(
        "[selftest] PASS theta-gamma nested: P=1-endpoint, sigma=0 recovery "
        "(single + nested), recall@1=1.000 at sigma=0.",
        flush=True,
    )


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ---- main experiment ----

def run_seed(seed: int) -> Dict[str, Any]:
    t_seed_start = time.time()
    total_phases = P_THETA * P_GAMMA
    print(
        f"[seed={seed}] N_DIM={N_DIM} M={M} "
        f"P_single={P_SINGLE} k_gamma={K_GAMMA} "
        f"P_theta={P_THETA} P_gamma={P_GAMMA} k_theta={K_THETA} "
        f"total_nested_phases={total_phases}",
        flush=True,
    )

    rng_book = np.random.default_rng(seed)
    rng_eval = np.random.default_rng(seed + 10_000)
    rng_noise_s = np.random.default_rng(seed + 20_000)
    rng_noise_tg = np.random.default_rng(seed + 30_000)

    # Bipolar codebook (+1/-1): shape (M, N_DIM)
    codebook = (rng_book.integers(0, 2, (M, N_DIM)).astype(np.float32) * 2.0 - 1.0)

    # Sample N_EVAL target indices
    target_indices = rng_eval.integers(0, M, N_EVAL)

    # Cues: target codebook rows
    cues = codebook[target_indices]  # (N_EVAL, N_DIM)

    per_arm: Dict[str, Dict[str, float]] = {
        "ARM_SINGLE_LOCKIN": {},
        "ARM_THETA_GAMMA_NESTED": {},
    }

    for sigma in SIGMAS:
        # ARM_SINGLE_LOCKIN
        decoded_s = single_lockin_demod(
            cues.copy(), P=P_SINGLE, k_signal=K_GAMMA, sigma=sigma, rng=rng_noise_s,
        )
        r_single = recall_at_1(decoded_s, codebook, target_indices)
        per_arm["ARM_SINGLE_LOCKIN"][f"sigma_{sigma}"] = r_single

        # ARM_THETA_GAMMA_NESTED
        decoded_tg = theta_gamma_nested_demod(
            cues.copy(), P_theta=P_THETA, P_gamma=P_GAMMA,
            k_theta=K_THETA, k_gamma=K_GAMMA,
            sigma=sigma, rng=rng_noise_tg,
        )
        r_nested = recall_at_1(decoded_tg, codebook, target_indices)
        per_arm["ARM_THETA_GAMMA_NESTED"][f"sigma_{sigma}"] = r_nested

        print(
            f"  [seed={seed} sigma={sigma}] single={r_single:.4f} nested={r_nested:.4f} "
            f"delta={r_nested - r_single:+.4f}",
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
        "elapsed_s": float(elapsed),
    }


def aggregate(per_seed: Dict[str, Any]) -> Tuple[Dict, Dict, Dict]:
    """Return (summary_by_arm_sigma, cv_by_arm_sigma, raw_vals_by_arm_sigma).

    summary[arm][sigma_key] = mean over seeds
    cv[arm][sigma_key] = std/mean over seeds
    """
    arm_names = ["ARM_SINGLE_LOCKIN", "ARM_THETA_GAMMA_NESTED"]
    seed_keys = sorted(per_seed.keys())

    summary: Dict[str, Dict[str, float]] = {a: {} for a in arm_names}
    cv: Dict[str, Dict[str, float]] = {a: {} for a in arm_names}
    raw: Dict[str, Dict[str, List[float]]] = {a: {} for a in arm_names}

    for sigma in SIGMAS:
        sig_key = f"sigma_{sigma}"
        for arm in arm_names:
            vals: List[float] = []
            for sk in seed_keys:
                body = per_seed[sk]
                v = body.get("per_arm", {}).get(arm, {}).get(sig_key)
                if v is not None:
                    vals.append(float(v))
            raw[arm][sig_key] = vals
            if vals:
                arr = np.array(vals, dtype=np.float64)
                mean_v = float(arr.mean())
                std_v = float(arr.std())
                summary[arm][sig_key] = mean_v
                cv[arm][sig_key] = float(std_v / mean_v) if mean_v > 1e-9 else 0.0
            else:
                summary[arm][sig_key] = 0.0
                cv[arm][sig_key] = 0.0

    return summary, cv, raw


def _sigma_capacity(arm_by_sig: Dict[str, float]) -> float:
    """Highest sigma at which recall@1 >= RECALL_95_THRESH (0.95)."""
    best = 0.0
    for sig_key, recall in arm_by_sig.items():
        if recall >= RECALL_95_THRESH:
            sigma_val = float(sig_key.replace("sigma_", ""))
            if sigma_val > best:
                best = sigma_val
    return best


def verdict(
    summary: Dict[str, Dict[str, float]],
    cv: Dict[str, Dict[str, float]],
) -> Tuple[str, str]:
    s_map = summary.get("ARM_SINGLE_LOCKIN", {})
    tg_map = summary.get("ARM_THETA_GAMMA_NESTED", {})

    if not s_map or not tg_map:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: missing arm data. arms_seen={list(summary.keys())}",
        )

    # Per-arm sigma capacity
    sc_single = _sigma_capacity(s_map)
    sc_nested = _sigma_capacity(tg_map)
    cap_ratio = sc_nested / sc_single if sc_single > 1e-9 else 0.0

    # Per-sigma recall deltas
    deltas = {sig: tg_map.get(sig, 0.0) - s_map.get(sig, 0.0) for sig in s_map}
    max_delta = max(deltas.values()) if deltas else 0.0
    any_positive = any(d > 0 for d in deltas.values())
    all_nonpositive = all(d <= 0.0 for d in deltas.values())

    detail = (
        f"N_DIM={N_DIM} M={M} P_single={P_SINGLE} "
        f"P_theta={P_THETA} P_gamma={P_GAMMA} k_gamma={K_GAMMA} k_theta={K_THETA}; "
        f"sigma_capacity_single={sc_single} sigma_capacity_nested={sc_nested} "
        f"cap_ratio={cap_ratio:.3f}; max_recall_delta={max_delta:+.4f}; "
        f"summary_single={s_map}; summary_nested={tg_map}"
    )

    # HARD_FAIL: theta-gamma never exceeds single-lockin at any sigma
    if all_nonpositive:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: nested oscillation adds nothing over single-frequency "
            f"lock-in across all sigmas tested. {detail}",
        )

    # HARD_PASS: either criterion met
    criterion_a = max_delta >= HP_RECALL_DELTA
    criterion_b = cap_ratio >= HP_SIGMA_CAP_RATIO

    if criterion_a or criterion_b:
        which = []
        if criterion_a:
            which.append(f"CRITERION_A(max_delta={max_delta:+.4f}>={HP_RECALL_DELTA})")
        if criterion_b:
            which.append(f"CRITERION_B(cap_ratio={cap_ratio:.3f}>={HP_SIGMA_CAP_RATIO})")
        return (
            "HARD_PASS",
            f"HARD_PASS: theta-gamma nested oscillation improves over single lock-in. "
            f"Criteria met: {', '.join(which)}. {detail}",
        )

    # MIDDLE_BAND: theta-gamma exceeds single at some sigmas but below hard-pass thresholds
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: theta-gamma exceeds single-lockin at some sigmas "
        f"(max_delta={max_delta:+.4f}<{HP_RECALL_DELTA}, "
        f"cap_ratio={cap_ratio:.3f}<{HP_SIGMA_CAP_RATIO}). {detail}",
    )


def main() -> int:
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS}", flush=True)
    print(
        f"[config] N_DIM={N_DIM} M={M} sigmas={SIGMAS} "
        f"P_single={P_SINGLE} k_gamma={K_GAMMA} "
        f"P_theta={P_THETA} P_gamma={P_GAMMA} k_theta={K_THETA} N_EVAL={N_EVAL}",
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
    summary, cv, _ = aggregate(per_seed)
    v, vmsg = verdict(summary, cv)
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
