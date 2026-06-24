"""
exp_substrate_lock_in_P_discriminating_regime_v1 -- pure-numpy P-sweep discriminating regime.

SCIENTIFIC QUESTION:
  Is P=64 over-spec for the lock-in amplifier primitive? Hypothesis: by-construction-saturation
  patterns Skunkworks repeatedly catches stem from P=64 being too easy (all arms saturate at
  recall=1.000). If P=16 shows a discriminating regime [0.4, 0.95] at sigma=64, then P=16 is
  the chain-grade default; P=64 is only needed for extreme noise.

MECHANISM (pure-numpy; no torch):
  codebook: (M, N) bipolar (+1/-1) patterns
  lock-in transmit+demod (P phases):
    transmit_p = roll(cue, p*k) * cos(2*pi*p/P) + noise_p   per phase
    decoded    = (2/P) * sum_p roll(received_p, -p*k) * cos(2*pi*p/P)
  recall@1: decoded cue matched against codebook (nearest-neighbor cosine)

PRE-REGISTERED HARD BANDS (exp_dev, 2026-06-23):
  HARD_PASS:
    P=64 recall@sigma=64 = 1.000 (within 0.005 tolerance)
    AND P=16 recall@sigma=64 in [0.4, 0.95] (discriminating regime at P=16)
  MIDDLE_BAND:
    P=16 recall@sigma=64 in [0.95, 1.0] OR < 0.4 (no clean discriminating region)
  HARD_FAIL:
    all P in {7, 16, 32, 64} recall@sigma=64 >= 0.99 (inherent saturation; P=4+ too easy)
    i.e., no discriminating regime exists across entire P sweep -- by-construction structural

CONFIG:
  smoke: N=512, M=100, sigma=[16,32,64,128], P={4,7,16,32,64}, k=31, seeds=[7,17]
  full : N=8192, M=500, sigma=[16,32,64,128], P={4,7,16,32,64}, k=31, seeds=[7,17,23]

ROUTING: remote_cpu_queue (pure numpy; no torch). N=8192 M=500 lightweight matmul.
WHAT_THIS_DOES_NOT_SHOW: does not show whether P=64 mechanism is chain-grade vs by-construction
  at full LM scale; does not test k_signal sweep (fixed k=31); does not test sigma<16.
  Does not establish chain-grade cert -- establishes discriminating-regime operating point
  for future discriminator design.
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
from typing import Dict, Any, Tuple, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial_key,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_lock_in_P_discriminating_regime_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke"
            else "full")
SMOKE = RUN_MODE == "smoke"

# ---- CONFIG ----
if SMOKE:
    N = 512
    M = 100
    SEEDS = [7, 17]
    N_EVAL = 100
else:
    N = 8192
    M = 500
    SEEDS = [7, 17, 23]
    N_EVAL = 200

P_SWEEP = [4, 7, 16, 32, 64]
K_SIGNAL = 31
SIGMAS = [16.0, 32.0, 64.0, 128.0]

# Pre-registered verdict bands
HP_P64_SIGMA64_MIN = 0.995    # P=64 recall@sigma=64 must be >= this
HP_P16_SIGMA64_LO = 0.40      # P=16 recall@sigma=64 discriminating band
HP_P16_SIGMA64_HI = 0.95
HF_ALL_P_SIGMA64_MIN = 0.99   # HARD_FAIL: all P in {7,16,32,64} saturate at >=0.99


# ---- core: pure numpy lock-in demod ----

def _cos_weights(P: int) -> np.ndarray:
    """Carrier weights cos(2*pi*p/P) for p in 0..P-1."""
    return np.array([math.cos(2.0 * math.pi * p / P) for p in range(P)], dtype=np.float64)


def lock_in_demod_np(
    cues: np.ndarray,   # (B, N)
    P: int,
    k: int,
    sigma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Lock-in transmit+demod for cues batch. Returns decoded (B, N).

    For P == 1: short-circuit to single-shot baseline (cue + noise).
    For P >= 2:
      transmit_p = roll(cue, p*k) * cos(2*pi*p/P) + noise_p
      demod_p    = roll(received_p, -p*k) * cos(2*pi*p/P)
      decoded    = (2/P) * sum_p demod_p
    Signal recovery: (2/P)*sum cos^2(2pi*p/P) = (2/P)*(P/2) = 1.0 for P>=4 even.
    """
    if P == 1:
        # Single-shot: no lock-in, P=1 reduces to baseline (cue + noise).
        noise = rng.normal(0.0, sigma, size=cues.shape)
        return cues + noise

    B, Nd = cues.shape
    acc = np.zeros((B, Nd), dtype=np.float64)
    weights = _cos_weights(P)
    for p in range(P):
        w = weights[p]
        rolled = np.roll(cues, p * k, axis=-1)
        noise = rng.normal(0.0, sigma, size=(B, Nd))
        received = rolled * w + noise
        unrolled = np.roll(received, -(p * k), axis=-1)
        acc += unrolled * w
    return (2.0 / P) * acc


def baseline_np(
    cues: np.ndarray,   # (B, N)
    sigma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Single-shot baseline: received = cue + noise. P=1 equivalent."""
    noise = rng.normal(0.0, sigma, size=cues.shape)
    return cues + noise


def recall_at_1(decoded: np.ndarray, codebook: np.ndarray, targets: np.ndarray) -> float:
    """Nearest-neighbor recall@1: decoded (B,N) vs codebook (M,N) -> scalar."""
    # scores (B, M) = decoded @ codebook.T
    scores = decoded @ codebook.T
    pred = scores.argmax(axis=-1)
    return float((pred == targets).mean())


# ---- instrumentation self-test ----

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. Verify P=1 lock_in equals baseline on same seed
    rng_a = np.random.default_rng(seed=99)
    rng_b = np.random.default_rng(seed=99)
    cues_t = np.random.default_rng(42).choice([-1.0, 1.0], size=(4, 32)).astype(np.float64)
    # P=1 lock-in: single phase, cos(0)=1, one noise draw -> identical to baseline_np
    out_lockin = lock_in_demod_np(cues_t, P=1, k=31, sigma=0.5, rng=rng_a)
    out_baseline = baseline_np(cues_t, sigma=0.5, rng=rng_b)
    diff = float(np.abs(out_lockin - out_baseline).max())
    assert diff < 1e-10, f"P=1 selftest FAIL: max|diff|={diff}"

    # 2. Sigma=0 recovery: decoded ~ cue for large P
    rng_c = np.random.default_rng(0)
    cues_s = np.random.default_rng(1).choice([-1.0, 1.0], size=(2, 16)).astype(np.float64)
    decoded_s = lock_in_demod_np(cues_s, P=8, k=3, sigma=0.0, rng=rng_c)
    # Expected factor = (2/P) * sum cos^2 = (2/8) * (8/2) = 1.0 for P=8 even
    sum_cos2 = sum(math.cos(2.0 * math.pi * p / 8) ** 2 for p in range(8))
    factor = (2.0 / 8) * sum_cos2
    expected = factor * cues_s
    diff2 = float(np.abs(decoded_s - expected).max())
    assert diff2 < 1e-10, f"sigma=0 selftest FAIL: diff={diff2} factor={factor}"
    assert abs(factor - 1.0) < 1e-9, f"cos^2 norm FAIL: factor={factor}"

    # 3. recall_at_1 returns a valid float in [0,1] and passes at least 1 item
    rng_d = np.random.default_rng(7)
    cb = rng_d.choice([-1.0, 1.0], size=(20, 32)).astype(np.float64)
    idxs = np.array([0, 5, 10])
    decoded_clean = cb[idxs].copy()   # perfect recall
    r = recall_at_1(decoded_clean, cb, idxs)
    assert r == 1.0, f"recall@1 selftest FAIL: perfect recall got {r}"
    assert isinstance(r, float), "recall@1 must return float"

    # 4. Assert outputs are non-null and non-zero across a sample arm
    rng_e = np.random.default_rng(seed=17)
    cues_4 = rng_e.choice([-1.0, 1.0], size=(4, 32)).astype(np.float64)
    cb4 = rng_e.choice([-1.0, 1.0], size=(10, 32)).astype(np.float64)
    tgts = np.array([0, 1, 2, 3])
    rng_f = np.random.default_rng(0)
    decoded_4 = lock_in_demod_np(cues_4, P=16, k=31, sigma=4.0, rng=rng_f)
    r4 = recall_at_1(decoded_4, cb4, tgts)
    assert r4 is not None and not math.isnan(r4), f"recall non-null selftest FAIL: r4={r4}"
    assert 0.0 <= r4 <= 1.0, f"recall out of range: {r4}"

    print("[selftest] PASS: P=1 endpoint -> baseline; sigma=0 -> recovery; recall@1 valid", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    print("[self-test] passed; exiting", flush=True)
    sys.exit(0)


# ---- per-seed experiment ----

def run_seed(seed: int) -> Dict[str, Any]:
    t_start = time.time()
    print(f"[seed={seed}] N={N} M={M} P_sweep={P_SWEEP} sigmas={SIGMAS} k={K_SIGNAL}", flush=True)

    rng = np.random.default_rng(seed=seed)

    # Bipolar codebook
    codebook = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)

    # Eval indices
    target_indices = rng.integers(0, M, size=N_EVAL)
    cues = codebook[target_indices]   # (N_EVAL, N)

    per_P: Dict[str, Dict[str, float]] = {}

    for P in P_SWEEP:
        arm = f"P{P}"
        per_P[arm] = {}
        rng_noise = np.random.default_rng(seed=seed + P * 1000)
        for sigma in SIGMAS:
            rng_s = np.random.default_rng(seed=rng_noise.integers(0, 2**31))
            if P == 1:
                decoded = baseline_np(cues, sigma=sigma, rng=rng_s)
            else:
                decoded = lock_in_demod_np(cues, P=P, k=K_SIGNAL, sigma=sigma, rng=rng_s)
            r = recall_at_1(decoded, codebook, target_indices)
            per_P[arm][f"sigma_{sigma:.0f}"] = r
            print(f"  [seed={seed} P={P} sigma={sigma}] recall@1={r:.4f}", flush=True)

    elapsed = time.time() - t_start
    return {
        "seed": seed,
        "N": N,
        "M": M,
        "run_mode": RUN_MODE,
        "per_P": per_P,
        "P_SWEEP": P_SWEEP,
        "SIGMAS": [float(s) for s in SIGMAS],
        "K_SIGNAL": K_SIGNAL,
        "N_EVAL": N_EVAL,
        "elapsed_s": float(elapsed),
    }


def aggregate_seeds(per_seed: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Mean recall@1 over seeds, keyed by P-arm then sigma."""
    summary: Dict[str, Dict[str, float]] = {}
    seed_keys = sorted(per_seed.keys())
    for P in P_SWEEP:
        arm = f"P{P}"
        summary[arm] = {}
        for sigma in SIGMAS:
            sk_key = f"sigma_{sigma:.0f}"
            vals: List[float] = []
            for sk in seed_keys:
                v = per_seed[sk].get("per_P", {}).get(arm, {}).get(sk_key)
                if v is not None:
                    vals.append(float(v))
            if vals:
                summary[arm][sk_key] = float(np.mean(vals))
            else:
                summary[arm][sk_key] = 0.0
    return summary


def verdict(summary: Dict[str, Dict[str, float]]) -> Tuple[str, str]:
    """Evaluate pre-registered HARD_PASS / HARD_FAIL / MIDDLE_BAND."""
    p64 = summary.get("P64", {})
    p16 = summary.get("P16", {})

    if not p64 or not p16:
        return ("HARD_FAIL",
                "HARD_FAIL: missing P64 or P16 arm data. summary=" + str(list(summary.keys())))

    r_p64_s64 = p64.get("sigma_64", None)
    r_p16_s64 = p16.get("sigma_64", None)

    if r_p64_s64 is None or r_p16_s64 is None:
        return ("HARD_FAIL",
                "HARD_FAIL: sigma_64 missing from P64 or P16. summary=" + repr(summary))

    # Check HARD_FAIL: all P in {7,16,32,64} saturate at >= 0.99
    all_saturate = all(
        summary.get(f"P{P}", {}).get("sigma_64", 0.0) >= HF_ALL_P_SIGMA64_MIN
        for P in [7, 16, 32, 64]
    )

    # Build per-arm sigma_64 summary for verdict_msg
    s64_map = {f"P{P}": summary.get(f"P{P}", {}).get("sigma_64", float("nan")) for P in P_SWEEP}
    s64_str = ", ".join(f"P{P}={s64_map[f'P{P}']:.4f}" for P in P_SWEEP)

    what_not_shown = (
        "WHAT_THIS_DOES_NOT_SHOW: does not establish chain-grade cert; does not test k_signal sweep "
        "(fixed k=31); does not test sigma<16; does not show performance on LM tasks. "
        "Establishes discriminating-regime operating point for discriminator design only."
    )

    if all_saturate:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: by-construction-saturation structural -- all P in {{7,16,32,64}} "
            f"recall@sigma=64 >= {HF_ALL_P_SIGMA64_MIN}. Lock-in P is not a discriminating axis "
            f"at this N/M/sigma regime. sigma_64 results: [{s64_str}]. N={N} M={M} k={K_SIGNAL}. "
            + what_not_shown
        )

    p64_ok = r_p64_s64 >= HP_P64_SIGMA64_MIN
    p16_discriminating = HP_P16_SIGMA64_LO <= r_p16_s64 <= HP_P16_SIGMA64_HI

    if p64_ok and p16_discriminating:
        return (
            "HARD_PASS",
            f"HARD_PASS: discriminating regime confirmed at P=16. "
            f"P64@sigma=64={r_p64_s64:.4f} (>={HP_P64_SIGMA64_MIN}); "
            f"P16@sigma=64={r_p16_s64:.4f} (in [{HP_P16_SIGMA64_LO},{HP_P16_SIGMA64_HI}]). "
            f"P=16 is the chain-grade discriminator default; P=64 saturates. "
            f"sigma_64 results: [{s64_str}]. N={N} M={M} k={K_SIGNAL}. "
            + what_not_shown
        )

    # MIDDLE_BAND
    reason_parts = []
    if not p64_ok:
        reason_parts.append(
            f"P64@sigma=64={r_p64_s64:.4f} < threshold {HP_P64_SIGMA64_MIN} (P=64 not saturating)"
        )
    if not p16_discriminating:
        if r_p16_s64 > HP_P16_SIGMA64_HI:
            reason_parts.append(
                f"P16@sigma=64={r_p16_s64:.4f} > {HP_P16_SIGMA64_HI} (P=16 also saturates)"
            )
        else:
            reason_parts.append(
                f"P16@sigma=64={r_p16_s64:.4f} < {HP_P16_SIGMA64_LO} (P=16 too noisy at sigma=64)"
            )
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: partial result. " + "; ".join(reason_parts) + ". "
        f"sigma_64 results: [{s64_str}]. N={N} M={M} k={K_SIGNAL}. "
        + what_not_shown
    )


def main() -> int:
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS}", flush=True)
    print(f"[config] N={N} M={M} P_sweep={P_SWEEP} sigmas={SIGMAS} k={K_SIGNAL} N_EVAL={N_EVAL}",
          flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "M": M, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds done; running {remaining}", flush=True)

    t_total = time.time()
    for seed in remaining:
        result = run_seed(seed)
        write_partial_key(out_dir, seed, result)
        print(f"[ckpt] seed={seed} written ({result['elapsed_s']:.1f}s)", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    summary = aggregate_seeds(per_seed)
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
            "N": N,
            "M": M,
            "P_SWEEP": P_SWEEP,
            "K_SIGNAL": K_SIGNAL,
            "SIGMAS": [float(s) for s in SIGMAS],
            "N_EVAL": N_EVAL,
        },
        "summary": summary,
        "per_seed": per_seed,
        "elapsed_s": float(elapsed_total),
    }
    write_metrics(out_dir, metrics, results=list(per_seed.values()))
    print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
