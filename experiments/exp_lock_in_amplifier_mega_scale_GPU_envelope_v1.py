"""
exp_lock_in_amplifier_mega_scale_GPU_envelope_v1 -- LLM-scale envelope mapping
of the substrate-native lock-in amplifier mechanism (torch.cuda; overnight_queue).

SCIENTIFIC QUESTION (USER intuition 2026-06-23, mega-scale envelope):
  The smoke (N=1024, M=50) confirmed lock-in (HARD_PASS smoke). The v1_FULL
  (N=8192, M=500) gave 16x lift -- chain-grade-eligible at substrate scale.
  Does the mechanism still hold at LLM scale (N=32768, M=5000)? And where in
  (sigma, k_signal, P) does it saturate? Mega-scale envelope mapping tells us
  the operating regime substrate-product can claim for the lock-in primitive.

  Pre-reg formal chain-grade promotion candidate: ARM_LOCK_IN_P256 lift >=
  sqrt(P/2) = sqrt(128) = 11.31x baseline at the discriminating sigma at
  N_DIM=32768, M=5000.

MECHANISM (identical to v1_FULL; torch.cuda batched):
  pi_k(v) = torch.roll(v, k)        cyclic-rotation permutation operator
  TRANSMIT_p(cue) = roll(cue, p*k) * cos(2*pi*p/P)        + noise_p
  DEMOD_p         = roll(received, -p*k) * cos(2*pi*p/P)
  decoded         = (2/P) * sum_p DEMOD_p
  Signal coheres   (2/P)*sum_p cue*cos^2 = cue                (P>=3)
  Noise variance   (2/P)^2 * sigma^2 * P/2 = 2*sigma^2 / P
  SNR lift factor  sqrt(P/2)

PRE-REGISTERED HARD_PASS (chain-grade promotion candidate):
  ARM_LOCK_IN_P256 lift >= sqrt(128) = 11.31x ARM_BASELINE_SINGLE_SHOT at the
  discriminating sigma (baseline recall in band [0.05, 0.30])
  AT N_DIM=32768, M=5000, cv (std/mean) across {seeds x k_signal} <= 0.20 at
  P=256 / discrim_sigma, frequency-invariance confirmed (lift uniform across
  k_signal), sanity self-tests pass.

PRE-REGISTERED HARD_FAIL:
  ARM_LOCK_IN_P64 lift < 2.0x at N=32768, M=5000 -- mechanism stops working at
  LLM scale; smoke + v1_FULL were small-regime artifacts; chain-grade scope-
  narrow to M<=500.

MIDDLE_BAND:
  lift in (2.0x, 5.0x) at P=256 -- partial mechanism characterization; tune
  P or k_signal further.

SANITY SELF-TESTS (mandatory; run at import):
  (a) P=1 endpoint: lock_in == baseline byte-for-byte across all sigmas
  (b) sigma=0 endpoint: lock-in v2 protocol recovers signal exactly via
      cos^2 sum normalization (P>=3)
  (c) Permutation orthogonality at N=32768: |roll(v, k) @ v / N| < 0.1 for
      k in {1, 127, 1023, 4095}
  (d) At sigma=2 (well-below noise-band-onset), all arms recall ~= 1.0 --
      lock-in unnecessary below noise floor.

CONFIG:
  smoke: N=1024, M=50, seeds=[7, 17], sigmas=[8, 32, 128], k=[31], P={1, 16, 64}
  full : N=32768, M=5000, seeds=[7, 17, 23], sigmas=[8, 16, 32, 64, 128, 256, 512],
         k_signal=[31, 127, 1023, 4095], P_sweep={1, 16, 32, 64, 128, 256}
         6 arms: BASELINE_SINGLE_SHOT, LOCK_IN_P{16, 32, 64, 128, 256}

ROUTING: overnight_queue (GPU). torch.cuda batched matmul + torch.roll vectorized.
PROT-020: imports torch (GPU queue allowed). PROT-021: imports _seed_checkpoint
voluntarily (anchor has no _n<N> suffix so PROT-021 is no-op; voluntary discipline).
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

ANCHOR_NAME = "lock_in_amplifier_mega_scale_GPU_envelope_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

SMOKE = RUN_MODE == "smoke"

# Device selection: prefer cuda; tolerate CPU for laptop pre-flight smoke/self-test.
if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
    print(f"[device] cuda={torch.cuda.get_device_name(0)}", flush=True)
else:
    DEVICE = torch.device("cpu")
    print(f"[device] cpu (cuda unavailable; OK for --self-test and laptop --smoke)", flush=True)

if SMOKE:
    # Tiny smoke for laptop --smoke gate (must run in <180s on CPU).
    SEEDS = [7, 17]
    N_DIM = 1024
    M = 50
    SIGMAS = [8.0, 32.0, 128.0]
    K_SIGNAL_SWEEP = [31]
    P_SWEEP = [1, 16, 64]
    N_EVAL = 50
else:
    # PRODUCTION mega-scale (USER-spec LLM-scale envelope; ~30-60min GPU)
    SEEDS = [7, 17, 23]
    N_DIM = 32768
    M = 5000
    SIGMAS = [8.0, 16.0, 32.0, 64.0, 128.0, 256.0, 512.0]
    K_SIGNAL_SWEEP = [31, 127, 1023, 4095]
    P_SWEEP = [1, 16, 32, 64, 128, 256]
    N_EVAL = 500

# Mechanism bands (USER pre-reg):
# HARD_PASS pinned to sqrt(P/2) textbook lift at P=256: sqrt(128) = 11.31x
HP_P256_LIFT_FACTOR = 11.31  # sqrt(P/2) at P=256
HF_P64_LIFT_FACTOR = 2.0
MIDDLE_P256_LIFT_HI = 5.0
HP_CV_MAX = 0.20
DISCRIM_BAND_LO = 0.05
DISCRIM_BAND_HI = 0.30


# ---- core primitives (torch.cuda batched) ----

def lock_in_demod_batched(
    cues: torch.Tensor,   # shape (B, N) -- B queries; each cue is target codebook row
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
    Vectorized over batch dim B. Per-phase loop kept (P typically <=256) to
    avoid materializing (B, P, N) intermediate which would blow VRAM at mega-scale.
    """
    if P == 1:
        # Endpoint: single-shot baseline. received = cue + noise.
        noise = sigma * torch.randn(cues.shape, generator=gen, device=cues.device, dtype=cues.dtype)
        return cues + noise

    acc = torch.zeros_like(cues)
    for p in range(P):
        carrier_p = math.cos(2.0 * math.pi * p / P)
        rolled = torch.roll(cues, shifts=p * k_signal, dims=-1)
        noise_p = sigma * torch.randn(cues.shape, generator=gen, device=cues.device, dtype=cues.dtype)
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
    """At sigma=0, lock-in protocol recovers signal exactly:
    decoded = (2/P) * sum_p cue * cos^2(2*pi*p/P) = (2/P)*(P/2)*cue = cue (P>=3).
    Tested at the production P_SWEEP values used here (16, 32, 64, 128, 256).
    """
    N_t = 64
    for P_t in [16, 32, 64, 128, 256]:
        cue = torch.randn(3, N_t, generator=torch.Generator(device="cpu").manual_seed(9), device="cpu")
        gen = torch.Generator(device="cpu").manual_seed(11)
        out = lock_in_demod_batched(cue, P=P_t, k_signal=31, sigma=0.0, gen=gen)
        sum_cos2 = sum(math.cos(2.0 * math.pi * p / P_t) ** 2 for p in range(P_t))
        expected_factor = (2.0 / P_t) * sum_cos2
        expected = expected_factor * cue
        diff = float((out - expected).abs().max())
        assert diff < 1e-5, f"sigma=0 signal recovery FAIL at P={P_t}: diff={diff} factor={expected_factor}"
        assert abs(expected_factor - 1.0) < 1e-9, f"cos^2 sum normalization off at P={P_t}: {expected_factor}"


def _selftest_roll_orthogonality_mega() -> None:
    """random v at N=32768: |roll(v, k) @ v / N| ~ 0 for k in {1, 127, 1023, 4095}."""
    N_t = 32768
    v = torch.randn(N_t, generator=torch.Generator(device="cpu").manual_seed(7), device="cpu")
    v_self = float((v @ v) / N_t)
    assert v_self > 0.5, f"random gaussian self-norm should be ~1: got {v_self}"
    for k in [1, 127, 1023, 4095]:
        v_rot = float((torch.roll(v, k) @ v) / N_t)
        assert abs(v_rot) < 0.1, f"k={k} orthogonality FAIL at N={N_t}: got {v_rot}"


def _selftest_low_sigma_all_arms_recall_1() -> None:
    """At sigma=2 (well below noise-band onset for N=1024), all arms recall ~= 1.0
    on a small codebook. Lock-in is unnecessary below noise floor.
    """
    N_t = 1024
    M_t = 20
    sigma_low = 2.0
    gen_book = torch.Generator(device="cpu").manual_seed(31)
    codebook = (torch.randint(0, 2, (M_t, N_t), generator=gen_book, device="cpu").float() * 2.0 - 1.0)
    targets = torch.arange(M_t)
    cues = codebook[targets]
    for P_t in [1, 16, 64]:
        gen_noise = torch.Generator(device="cpu").manual_seed(101 + P_t)
        if P_t == 1:
            recv = baseline_transmit_batched(cues, sigma=sigma_low, gen=gen_noise)
        else:
            recv = lock_in_demod_batched(cues, P=P_t, k_signal=31, sigma=sigma_low, gen=gen_noise)
        scores = recv @ codebook.t()
        pred = scores.argmax(dim=-1)
        recall = float((pred == targets).float().mean())
        assert recall >= 0.95, f"low-sigma recall FAIL: P={P_t} sigma={sigma_low} recall={recall}"


def _instrumentation_selftest() -> None:
    _selftest_p1_endpoint()
    _selftest_sigma0_signal_recovery()
    _selftest_roll_orthogonality_mega()
    _selftest_low_sigma_all_arms_recall_1()
    print(
        "[selftest] PASS lock-in mega-scale primitives: P=1 endpoint -> baseline, "
        "sigma=0 -> signal-recovery (P in {16,32,64,128,256}), roll-orthogonality "
        "at N=32768 across k in {1,127,1023,4095}, low-sigma all-arms recall ~= 1.0.",
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

    gen_book = torch.Generator(device=DEVICE).manual_seed(seed)
    gen_eval = torch.Generator(device=DEVICE).manual_seed(seed + 10_000)
    gen_noise = torch.Generator(device=DEVICE).manual_seed(seed + 20_000)

    # Bipolar codebook (+1/-1): rows are stored patterns. Shape (M, N_DIM).
    codebook = (torch.randint(0, 2, (M, N_DIM), generator=gen_book, device=DEVICE).float() * 2.0 - 1.0)
    print(f"[seed={seed}] codebook built: shape={tuple(codebook.shape)} dtype={codebook.dtype} device={codebook.device}", flush=True)

    # Sample N_EVAL target indices deterministically per seed
    target_indices = torch.randint(0, M, (N_EVAL,), generator=gen_eval, device=DEVICE)
    cues = codebook[target_indices]  # (N_EVAL, N_DIM)

    per_arm: Dict[str, Dict[str, Dict[str, float]]] = {}

    for P in P_SWEEP:
        arm_name = _arm_label(P)
        per_arm[arm_name] = {}
        for k_signal in K_SIGNAL_SWEEP:
            per_arm[arm_name][f"k_{k_signal}"] = {}
            for sigma in SIGMAS:
                t_cfg = time.time()
                if P == 1:
                    received = baseline_transmit_batched(cues, sigma=sigma, gen=gen_noise)
                else:
                    received = lock_in_demod_batched(
                        cues, P=P, k_signal=k_signal, sigma=sigma, gen=gen_noise,
                    )
                # codebook @ received.T -> (N_EVAL, M); argmax over M
                scores = received @ codebook.t()
                pred = scores.argmax(dim=-1)
                correct = (pred == target_indices).float().mean().item()
                per_arm[arm_name][f"k_{k_signal}"][f"sigma_{sigma}"] = float(correct)
                dt = time.time() - t_cfg
                print(
                    f"  [seed={seed} arm={arm_name} k={k_signal} sigma={sigma}] "
                    f"recall@1={correct:.4f}  dt={dt:.2f}s",
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


def _frequency_invariance_cv(per_seed: Dict[str, Dict[str, Any]], arm: str, sig_key: str) -> float:
    """Compute CV of mean-recall across k_signal values (mean over seeds first).
    Small CV here means lift is uniform across frequency choices (mechanism is
    frequency-invariant within the coprime-to-N subspace).
    """
    per_k_means: List[float] = []
    for k_signal in K_SIGNAL_SWEEP:
        k_key = f"k_{k_signal}"
        vals: List[float] = []
        for sk in sorted(per_seed.keys()):
            v = per_seed[sk].get("per_arm", {}).get(arm, {}).get(k_key, {}).get(sig_key)
            if v is not None:
                vals.append(float(v))
        if vals:
            per_k_means.append(float(np.mean(vals)))
    if not per_k_means:
        return 0.0
    arr = np.array(per_k_means, dtype=np.float64)
    mean_v = float(arr.mean())
    if mean_v <= 1e-9:
        return 0.0
    return float(arr.std() / mean_v)


def verdict(
    summary: Dict[str, Dict[str, float]],
    cv: Dict[str, Dict[str, float]],
    per_seed: Dict[str, Dict[str, Any]],
) -> Tuple[str, str]:
    base_map = summary.get("ARM_BASELINE_SINGLE_SHOT", {})
    p64_map = summary.get("ARM_LOCK_IN_P64", {})
    p256_map = summary.get("ARM_LOCK_IN_P256")

    if not base_map or not p64_map:
        return ("HARD_FAIL", f"HARD_FAIL: missing baseline or P64 arm. arms_seen={list(summary.keys())}")

    smoke_mode_no_p256 = p256_map is None or not p256_map

    sig_key, base = _find_discriminating_sigma(base_map)
    p64 = p64_map.get(sig_key, 0.0)
    p256 = (p256_map or {}).get(sig_key, 0.0)

    lift_p64 = (p64 / base) if base > 1e-9 else float("inf")
    lift_p256 = (p256 / base) if base > 1e-9 else float("inf")

    if smoke_mode_no_p256:
        # Smoke validator: P64 lift >= 2x is the SMOKE_PASS gate.
        smoke_lift_ok = lift_p64 >= 2.0
        smoke_s = (
            f"SMOKE discrim_sigma={sig_key} (baseline={base:.4f}): P64={p64:.4f}(x{lift_p64:.2f}); "
            f"N_DIM={N_DIM} M={M}; SMOKE_PASS gate=P64-lift>=2.0x. summary={summary}"
        )
        if smoke_lift_ok:
            return ("SMOKE_PASS", "SMOKE_PASS: lock-in mechanism replicates in smoke. " + smoke_s)
        return ("SMOKE_FAIL", "SMOKE_FAIL: lock-in does not replicate in smoke. " + smoke_s)

    base_in_band = DISCRIM_BAND_LO <= base <= DISCRIM_BAND_HI
    cv_p256 = cv.get("ARM_LOCK_IN_P256", {}).get(sig_key, 1.0)
    cv_p64 = cv.get("ARM_LOCK_IN_P64", {}).get(sig_key, 1.0)
    freq_cv_p256 = _frequency_invariance_cv(per_seed, "ARM_LOCK_IN_P256", sig_key)

    s = (
        f"discrim_sigma={sig_key} (baseline={base:.4f} {'in-band' if base_in_band else 'OUT-of-band'}): "
        f"P64={p64:.4f}(x{lift_p64:.2f},cv={cv_p64:.3f}) "
        f"P256={p256:.4f}(x{lift_p256:.2f},cv={cv_p256:.3f},freq_cv={freq_cv_p256:.3f}); "
        f"N_DIM={N_DIM} M={M} k_sweep={K_SIGNAL_SWEEP}; summary={summary}"
    )

    # HARD_FAIL: P64 lift collapses at LLM scale
    if lift_p64 < HF_P64_LIFT_FACTOR:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: lock-in amplifier mechanism does not scale to LLM regime. "
            f"ARM_LOCK_IN_P64 lift x{lift_p64:.2f} < HF threshold {HF_P64_LIFT_FACTOR}x at "
            f"N_DIM={N_DIM} M={M}. Smoke + v1_FULL were small-regime artifacts; chain-grade "
            f"scope-narrow to M<=500. " + s
        )

    # HARD_PASS: textbook sqrt(P/2) lift at P=256 AND cv tight AND baseline in-band AND
    # frequency-invariance confirmed (freq_cv low)
    if (
        base_in_band
        and lift_p256 >= HP_P256_LIFT_FACTOR
        and cv_p256 <= HP_CV_MAX
        and freq_cv_p256 <= HP_CV_MAX
    ):
        return (
            "HARD_PASS",
            f"HARD_PASS: lock-in amplifier mechanism scales to LLM regime. "
            f"ARM_LOCK_IN_P256 lifts recall x{lift_p256:.2f} (HP>={HP_P256_LIFT_FACTOR}x) with "
            f"cv={cv_p256:.3f} (HP<={HP_CV_MAX}) and freq_invariance_cv={freq_cv_p256:.3f} "
            f"(HP<={HP_CV_MAX}) over baseline at {sig_key}, N_DIM={N_DIM} M={M}. "
            f"Formal chain-grade promotion candidate; substrate-native lock-in amplifier is "
            f"a chain-grade primitive across LLM-scale substrate. " + s
        )

    if lift_p256 < MIDDLE_P256_LIFT_HI:
        return (
            "MIDDLE_BAND",
            f"MIDDLE_BAND: partial mechanism. P256 x{lift_p256:.2f} (HP>={HP_P256_LIFT_FACTOR}x); "
            f"cv={cv_p256:.3f} (HP<={HP_CV_MAX}); freq_cv={freq_cv_p256:.3f}; "
            f"base_in_band={base_in_band}. " + s
        )

    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: lift {lift_p256:.2f}x present but failed HP gate "
        f"(base_in_band={base_in_band}, cv={cv_p256:.3f}, freq_cv={freq_cv_p256:.3f}). " + s
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
    v, vmsg = verdict(summary, cv, per_seed)
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
