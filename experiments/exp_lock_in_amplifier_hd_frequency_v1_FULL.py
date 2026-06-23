"""
exp_lock_in_amplifier_hd_frequency_v1_FULL -- production-scale lock-in amplifier (GPU torch).

SCIENTIFIC QUESTION (production-scale validation of smoke HARD_PASS):
  The smoke (N=1024, M=50, sigma sweep) confirmed a substrate-native "lock-in
  amplifier" mechanism: cyclic-permutation as HD frequency carrier, transmit-side
  cos-weighting, demodulate-and-match against codebook. P=32 lifted recall@1
  8.17x over baseline at sigma=32 (in-band stress). Does the mechanism scale
  to N_DIM=8192, M=500 (10x capacity)? Pre-reg targets sqrt(P/2) SNR-lift
  factor across P in {4,8,16,32,64} and frequency-invariance across coprime
  k_signal in {1,7,31,127,1023}.

MECHANISM (substrate-native lock-in amplifier; ported numpy->torch.cuda):
  pi_k(v) = torch.roll(v, k)        cyclic-rotation permutation operator
  TRANSMIT_p(cue) = roll(cue, p*k) * cos(2*pi*p/P)        + noise_p
  DEMOD_p         = roll(received, -p*k) * cos(2*pi*p/P)
  decoded         = (2/P) * sum_p DEMOD_p
  Signal coheres   (2/P)*sum_p cue*cos^2 = cue                (P>=2 even)
  Noise variance   (2/P)^2 * sigma^2 * P/2 = 2*sigma^2 / P
  SNR lift factor  sqrt(P/2)

PRE-REGISTERED HARD_PASS (chain-grade-eligible primitive):
  ARM_LOCK_IN_P64 lift >= sqrt(32) = 5.65x over ARM_BASELINE_SINGLE_SHOT
  at the discriminating sigma (baseline recall@1 in band [0.05, 0.30])
  AT N_DIM=8192, M=500, AND cv across {seeds x k_signal} <= 0.20 AT P=64,
  AND sanity self-tests pass.

PRE-REGISTERED HARD_FAIL:
  ARM_LOCK_IN_P32 lift < 2.0x at discriminating sigma -- mechanism collapses
  at production scale; smoke result was small-regime artifact.

MIDDLE_BAND:
  lift in (1.0x, 2.0x) -- partial mechanism characterization; tune P or k_signal.

SANITY SELF-TESTS (mandatory; run at import):
  (a) P=1 endpoint: lock_in == baseline byte-for-byte across all sigmas
  (b) sigma=0 endpoint: all arms recall=1.000
  (c) Permutation orthogonality at N=8192: |roll(v, k)@v / N| ~ 0 for k=1023

CONFIG:
  smoke: N=1024, M=50, seeds=[7,17], sigmas=[4,8,16,32,64], k=[31], P={1,8,32}
  full : N=8192, M=500, seeds=[7,17,23], sigmas=[4,8,16,32,64,128],
         k_signal=[1,7,31,127,1023], P_sweep={1,4,8,16,32,64}
         6 arms: BASELINE_SINGLE_SHOT, LOCK_IN_P{4,8,16,32,64}

ROUTING: overnight_queue (GPU). torch.cuda batched matmul + torch.roll vectorized.
PROT-020: imports torch (GPU queue allowed). PROT-021: imports _seed_checkpoint.
ASCII-only. No unicode. write_metrics with REQUIRED_FIELDS.
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

try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)

import numpy as np

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial_key,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "lock_in_amplifier_hd_frequency_v1_FULL"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

SMOKE = RUN_MODE == "smoke"

# Device selection: prefer cuda; tolerate CPU for laptop pre-flight smoke.
if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
    print(f"[device] cuda={torch.cuda.get_device_name(0)}", flush=True)
else:
    DEVICE = torch.device("cpu")
    print(f"[device] cpu (cuda unavailable; OK for --self-test and laptop --smoke)", flush=True)

if SMOKE:
    SEEDS = [7, 17]
    N_DIM = 1024
    M = 50
    SIGMAS = [4.0, 8.0, 16.0, 32.0, 64.0]
    K_SIGNAL_SWEEP = [31]
    P_SWEEP = [1, 8, 32]
    N_EVAL = 100
else:
    # PRODUCTION config (USER-spec lock-in amplifier validation at substrate scale)
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    M = 500
    SIGMAS = [4.0, 8.0, 16.0, 32.0, 64.0, 128.0]
    K_SIGNAL_SWEEP = [1, 7, 31, 127, 1023]
    P_SWEEP = [1, 4, 8, 16, 32, 64]
    N_EVAL = 200

# Mechanism band (substrate-honest):
# HARD_PASS pinned to sqrt(P/2) textbook lift; P64 -> sqrt(32) = 5.65x
HP_P64_LIFT_FACTOR = 5.65
HF_P32_LIFT_FACTOR = 2.0
HP_CV_MAX = 0.20
DISCRIM_BAND_LO = 0.05
DISCRIM_BAND_HI = 0.30


# ---- core primitives (torch.cuda batched) ----

def lock_in_demod_batched(
    cues: torch.Tensor,   # shape (B, N)  -- B queries; each cue is target codebook row
    P: int,
    k_signal: int,
    sigma: float,
    gen: torch.Generator,
) -> torch.Tensor:
    """Lock-in transmit+demod for a batch of cues. Returns demodulated estimate shape (B, N).

    For each cue:
      transmit_p = roll(cue, p*k) * cos(2*pi*p/P)
      received_p = transmit_p + noise_p          (independent noise per phase)
      demod_p    = roll(received_p, -p*k) * cos(2*pi*p/P)
      decoded    = (2/P) * sum_p demod_p
    Vectorized over batch dim B.
    """
    if P == 1:
        # Endpoint: single-shot baseline. received = cue + noise.
        noise = sigma * torch.randn(cues.shape, generator=gen, device=cues.device, dtype=cues.dtype)
        return cues + noise

    B, N = cues.shape
    acc = torch.zeros_like(cues)
    for p in range(P):
        carrier_p = math.cos(2.0 * math.pi * p / P)
        rolled = torch.roll(cues, shifts=p * k_signal, dims=-1)
        noise_p = sigma * torch.randn(B, N, generator=gen, device=cues.device, dtype=cues.dtype)
        received = rolled * carrier_p + noise_p
        unrolled = torch.roll(received, shifts=-p * k_signal, dims=-1)
        acc = acc + unrolled * carrier_p
    return (2.0 / P) * acc


def baseline_transmit_batched(
    cues: torch.Tensor,
    sigma: float,
    gen: torch.Generator,
) -> torch.Tensor:
    """ARM_BASELINE_SINGLE_SHOT: received = cue + noise. No lock-in."""
    noise = sigma * torch.randn(cues.shape, generator=gen, device=cues.device, dtype=cues.dtype)
    return cues + noise


# ---- self-tests (formula correctness) ----

def _selftest_p1_endpoint() -> None:
    """At P=1 the lock_in branch short-circuits to baseline. Verify same-seed identity."""
    N_t = 64
    sig = 0.5
    cues = torch.randn(4, N_t, generator=torch.Generator(device="cpu").manual_seed(123), device="cpu")
    gen_a = torch.Generator(device="cpu").manual_seed(456)
    gen_b = torch.Generator(device="cpu").manual_seed(456)
    out_a = lock_in_demod_batched(cues, P=1, k_signal=31, sigma=sig, gen=gen_a)
    out_b = baseline_transmit_batched(cues, sigma=sig, gen=gen_b)
    diff = float((out_a - out_b).abs().max())
    assert diff < 1e-12, f"P=1 endpoint selftest FAIL: max|diff|={diff}"


def _selftest_sigma0_signal_recovery() -> None:
    """At sigma=0, lock-in v2 protocol recovers signal exactly:
    decoded = (2/P) * sum_p cue * cos^2(2*pi*p/P) = (2/P)*(P/2)*cue = cue (P>=2 even).
    """
    N_t = 64
    # P=2 is degenerate: cos basis = {1, -1} so sum cos^2 = 2, factor=(2/2)*2=2.0.
    # The lock-in identity sum_p cos^2(2*pi*p/P) = P/2 (hence factor = 1.0) holds
    # for P >= 3. Our production P_SWEEP excludes P=2, so we self-test the actually-
    # used values {4, 8, 32} where the textbook normalization holds.
    for P_t in [4, 8, 32]:
        cue = torch.randn(3, N_t, generator=torch.Generator(device="cpu").manual_seed(9), device="cpu")
        gen = torch.Generator(device="cpu").manual_seed(11)
        out = lock_in_demod_batched(cue, P=P_t, k_signal=31, sigma=0.0, gen=gen)
        # Expected normalization factor = (2/P) * sum_p cos^2(2*pi*p/P)
        sum_cos2 = sum(math.cos(2.0 * math.pi * p / P_t) ** 2 for p in range(P_t))
        expected_factor = (2.0 / P_t) * sum_cos2
        expected = expected_factor * cue
        diff = float((out - expected).abs().max())
        assert diff < 1e-5, f"sigma=0 signal recovery FAIL at P={P_t}: diff={diff} factor={expected_factor}"
        assert abs(expected_factor - 1.0) < 1e-9, f"cos^2 sum normalization off at P={P_t}: {expected_factor}"


def _selftest_roll_orthogonality() -> None:
    """random v at N=8192: |roll(v, 1023) @ v / N| ~ 0 (orthogonal frequency basis)."""
    N_t = 8192
    v = torch.randn(N_t, generator=torch.Generator(device="cpu").manual_seed(7), device="cpu")
    v_self = float((v @ v) / N_t)
    v_rot_1023 = float((torch.roll(v, 1023) @ v) / N_t)
    v_rot_1 = float((torch.roll(v, 1) @ v) / N_t)
    v_rot_127 = float((torch.roll(v, 127) @ v) / N_t)
    assert v_self > 0.5, f"random gaussian self-norm should be ~1: got {v_self}"
    assert abs(v_rot_1023) < 0.1, f"k=1023 orthogonality FAIL: got {v_rot_1023}"
    assert abs(v_rot_1) < 0.1, f"k=1 orthogonality FAIL: got {v_rot_1}"
    assert abs(v_rot_127) < 0.1, f"k=127 orthogonality FAIL: got {v_rot_127}"


def _instrumentation_selftest() -> None:
    _selftest_p1_endpoint()
    _selftest_sigma0_signal_recovery()
    _selftest_roll_orthogonality()
    print(
        "[selftest] PASS lock-in primitives: P=1 endpoint -> baseline, sigma=0 -> signal-recovery, "
        "roll-orthogonality at N=8192 across k in {1,127,1023}.",
        flush=True,
    )


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ---- main experiment ----

def _arm_label(P: int) -> str:
    if P == 1:
        return "ARM_BASELINE_SINGLE_SHOT"
    return f"ARM_LOCK_IN_P{P}"


def run_seed(seed: int) -> Dict[str, Any]:
    t_seed_start = time.time()
    print(f"[seed={seed}] starting N_DIM={N_DIM} M={M} arms={len(P_SWEEP)} k_signals={K_SIGNAL_SWEEP}", flush=True)

    # Per-seed deterministic codebook + eval order
    gen_book = torch.Generator(device=DEVICE).manual_seed(seed)
    gen_eval = torch.Generator(device=DEVICE).manual_seed(seed + 10_000)
    gen_noise = torch.Generator(device=DEVICE).manual_seed(seed + 20_000)

    # Bipolar codebook (+1/-1): rows are stored patterns. Shape (M, N_DIM).
    codebook = (torch.randint(0, 2, (M, N_DIM), generator=gen_book, device=DEVICE).float() * 2.0 - 1.0)

    # Sample N_EVAL target indices deterministically per seed
    target_indices = torch.randint(0, M, (N_EVAL,), generator=gen_eval, device=DEVICE)

    # Cues (B=N_EVAL, N_DIM) -- target codebook rows
    cues = codebook[target_indices]  # shape (N_EVAL, N_DIM)

    # Per-arm x per-sigma x per-k_signal recall@1
    per_arm: Dict[str, Dict[str, Dict[str, float]]] = {}

    for P in P_SWEEP:
        arm_name = _arm_label(P)
        per_arm[arm_name] = {}
        # For ARM_BASELINE_SINGLE_SHOT and P==1 baseline, k_signal does not enter
        # the math; we still iterate so the schema is uniform, but the result
        # depends only on noise -- different noise draws across k_signal still
        # measure baseline-recall variance which is informative.
        for k_signal in K_SIGNAL_SWEEP:
            per_arm[arm_name][f"k_{k_signal}"] = {}
            for sigma in SIGMAS:
                if P == 1:
                    received = baseline_transmit_batched(cues, sigma=sigma, gen=gen_noise)
                else:
                    received = lock_in_demod_batched(
                        cues, P=P, k_signal=k_signal, sigma=sigma, gen=gen_noise,
                    )
                # codebook @ received.T  -> (M, N_EVAL); argmax over M
                scores = received @ codebook.t()  # (N_EVAL, M)
                pred = scores.argmax(dim=-1)      # (N_EVAL,)
                correct = (pred == target_indices).float().mean().item()
                per_arm[arm_name][f"k_{k_signal}"][f"sigma_{sigma}"] = float(correct)
                print(
                    f"  [seed={seed} arm={arm_name} k={k_signal} sigma={sigma}] recall@1={correct:.4f}",
                    flush=True,
                )

    elapsed = time.time() - t_seed_start
    return {
        "seed": seed,
        "N": N_DIM,
        "M": M,
        "run_mode": RUN_MODE,
        "per_arm": per_arm,
        "K_SIGNAL_SWEEP": K_SIGNAL_SWEEP,
        "P_SWEEP": P_SWEEP,
        "SIGMAS": SIGMAS,
        "N_EVAL": N_EVAL,
        "elapsed_s": float(elapsed),
    }


def aggregate(per_seed: Dict[str, Dict[str, Any]]) -> Tuple[Dict, Dict]:
    """Return (summary_by_arm_sigma_avg_over_seeds_and_k, per_arm_cv).

    summary[arm][sigma] = mean(recall@1) across seeds and k_signal values
    per_arm_cv[arm][sigma] = std / mean of recall across seeds*k_signal
    """
    summary: Dict[str, Dict[str, float]] = {}
    cv: Dict[str, Dict[str, float]] = {}

    arm_names = [_arm_label(P) for P in P_SWEEP]
    seed_keys = sorted(per_seed.keys())

    for arm in arm_names:
        summary[arm] = {}
        cv[arm] = {}
        for sigma in SIGMAS:
            sig_key = f"sigma_{sigma}"
            vals: List[float] = []
            for sk in seed_keys:
                body = per_seed[sk]
                per_arm = body.get("per_arm", {})
                arm_map = per_arm.get(arm, {})
                for k_signal in K_SIGNAL_SWEEP:
                    k_key = f"k_{k_signal}"
                    k_map = arm_map.get(k_key, {})
                    v = k_map.get(sig_key)
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


def _find_discriminating_sigma(base_by_sig: Dict[str, float]) -> Tuple[str, float]:
    """Pick sigma where baseline recall is in [DISCRIM_BAND_LO, DISCRIM_BAND_HI].
    Prefer HIGHEST in-band baseline (more headroom for lift to ceiling 1.0).
    """
    in_band = [(k, v) for k, v in base_by_sig.items() if DISCRIM_BAND_LO <= v <= DISCRIM_BAND_HI]
    if in_band:
        return max(in_band, key=lambda kv: kv[1])
    center = (DISCRIM_BAND_LO + DISCRIM_BAND_HI) / 2.0
    return min(base_by_sig.items(), key=lambda kv: abs(kv[1] - center))


def verdict(summary: Dict[str, Dict[str, float]], cv: Dict[str, Dict[str, float]]) -> Tuple[str, str]:
    base_map = summary.get("ARM_BASELINE_SINGLE_SHOT", {})
    p32_map = summary.get("ARM_LOCK_IN_P32", {})
    p64_map = summary.get("ARM_LOCK_IN_P64")  # may be absent in smoke mode

    if not base_map or not p32_map:
        return ("HARD_FAIL", f"HARD_FAIL: missing baseline or P32 arm. arms_seen={list(summary.keys())}")

    # In smoke mode (no P64), fall back to P32 lift as the smoke validator.
    smoke_mode_no_p64 = p64_map is None or not p64_map

    sig_key, base = _find_discriminating_sigma(base_map)
    p32 = p32_map.get(sig_key, 0.0)
    p64 = (p64_map or {}).get(sig_key, 0.0)

    lift_p32 = (p32 / base) if base > 1e-9 else float("inf")
    lift_p64 = (p64 / base) if base > 1e-9 else float("inf")

    if smoke_mode_no_p64:
        # Smoke validator: P32 lift >= 2x is the SMOKE_PASS gate (replicating the
        # original smoke HARD_PASS condition without chain-grade claim).
        smoke_lift_ok = lift_p32 >= 2.0
        smoke_s = (
            f"SMOKE discrim_sigma={sig_key} (baseline={base:.4f}): P32={p32:.4f}(x{lift_p32:.2f}); "
            f"N_DIM={N_DIM} M={M}; SMOKE_PASS gate=P32-lift>=2.0x. summary={summary}"
        )
        if smoke_lift_ok:
            return ("SMOKE_PASS", f"SMOKE_PASS: lock-in mechanism replicates in smoke. " + smoke_s)
        return ("SMOKE_FAIL", f"SMOKE_FAIL: lock-in does not replicate in smoke. " + smoke_s)

    base_in_band = DISCRIM_BAND_LO <= base <= DISCRIM_BAND_HI
    cv_p64 = cv.get("ARM_LOCK_IN_P64", {}).get(sig_key, 1.0)
    cv_p32 = cv.get("ARM_LOCK_IN_P32", {}).get(sig_key, 1.0)

    s = (
        f"discrim_sigma={sig_key} (baseline={base:.4f} {'in-band' if base_in_band else 'OUT-of-band'}): "
        f"P32={p32:.4f}(x{lift_p32:.2f},cv={cv_p32:.3f}) P64={p64:.4f}(x{lift_p64:.2f},cv={cv_p64:.3f}); "
        f"N_DIM={N_DIM} M={M} k_sweep={K_SIGNAL_SWEEP}; summary={summary}"
    )

    # HARD_FAIL: P32 lift collapses at production scale
    if lift_p32 < HF_P32_LIFT_FACTOR:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: lock-in amplifier mechanism does not scale. ARM_LOCK_IN_P32 lift x{lift_p32:.2f} "
            f"< HF threshold {HF_P32_LIFT_FACTOR}x at production N_DIM={N_DIM} M={M}. "
            f"Smoke result was small-regime artifact. " + s
        )

    # HARD_PASS: textbook sqrt(P/2) lift AND cv tight AND baseline in-band
    if (
        base_in_band
        and lift_p64 >= HP_P64_LIFT_FACTOR
        and cv_p64 <= HP_CV_MAX
    ):
        return (
            "HARD_PASS",
            f"HARD_PASS: lock-in amplifier scales to production. ARM_LOCK_IN_P64 lifts recall "
            f"x{lift_p64:.2f} (HP>={HP_P64_LIFT_FACTOR}x) with cv={cv_p64:.3f} (HP<={HP_CV_MAX}) "
            f"over baseline at {sig_key}, N_DIM={N_DIM} M={M}. Substrate-native lock-in amplifier "
            f"is a chain-grade primitive across substrate scales. " + s
        )

    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: partial mechanism. P64 x{lift_p64:.2f} (HP>={HP_P64_LIFT_FACTOR}x); "
        f"cv={cv_p64:.3f} (HP<={HP_CV_MAX}); base_in_band={base_in_band}. " + s
    )


def main() -> int:
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS}", flush=True)
    print(
        f"[config] N_DIM={N_DIM} M={M} sigmas={SIGMAS} k_signal={K_SIGNAL_SWEEP} "
        f"P_sweep={P_SWEEP} N_EVAL={N_EVAL}", flush=True,
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
    summary, cv = aggregate(per_seed)
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
            "K_SIGNAL_SWEEP": K_SIGNAL_SWEEP,
            "P_SWEEP": P_SWEEP,
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
