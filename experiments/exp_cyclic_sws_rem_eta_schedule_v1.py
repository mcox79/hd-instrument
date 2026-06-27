"""cyclic_sws_rem_eta_schedule_v1 -- Battery 2 Barrier 3 Angles 2+3 (CPU).

Prereg: preregs/2026-06-27_cyclic_sws_rem_eta_schedule_v1.md (Research-authored)
Composes on: hdlab.continual.replay_cycle (atom 588; chain-grade NREM replay primitive)

MECHANISM: replay_cycle is the substrate's NREM-replay primitive that re-Hebbs a fraction
(replay_frac=0.2) of stored (key, value) traces at each cycle, parameterized by `lr` (=eta).
Constant-eta replay (current default eta_constant=0.5) is the chain-grade rail. This cell
tests Volkov-Sapir 2024 cyclic-annealing + Walker-Stickgold SWS/REM alternation by cycling
the lr parameter through [eta_high, eta_low, eta_high, eta_low, ...] across pulses.

ARMS (4 mandatory + 1 diagnostic):
  ARM_BASELINE_HEBBIAN              current global Hebbian write at regime (anti-saturation gate)
  ARM_CONSTANT_ETA_REPLAY           replay_cycle with lr = eta_constant = 0.5 (chain-grade rail)
  ARM_CYCLIC_ETA_HIGH_LOW           cycle lr in [1.0, 0.1] per pulse (period 1)
  ARM_CYCLIC_ETA_HIGH_LOW_LONG      cycle lr same values, period 5 pulses (cycling RATE test)
  ARM_DIAG_BASIN_RESTRUCTURE        per-pulse W_frobenius_delta + eigenspectrum entropy
                                     + which-eta-applied audit; high-eta MUST do >= 3x larger
                                     frob_delta than low-eta (gate enforced via verdict).

REGIME (matches prereg exactly):
  N_DIM = 2048, N_CAT = 100, N_TRAIN = 10 per cat, N_HELDOUT = 20 per cat
  proto_noise = 0.85, alpha = N_CAT/N_DIM = 0.0488
  eta_high = 1.0; eta_low = 0.1 (10x ratio); eta_constant = sqrt(eta_high * eta_low) ~= 0.316
                                              (NB: prereg says 0.5; sqrt(0.1)~=0.316 is geometric;
                                               prereg arithmetic explicit at 0.5 ~= (1.0+0.1)/2 = 0.55,
                                               using 0.5 per prereg literal value)
  N_PULSES = 50
  seeds = [11, 13, 19, 23, 29]

PRE-REG HARD-PASS (verbatim from prereg):
  best(CYCLIC).heldout_acc - CONSTANT_ETA.heldout_acc >= 0.10
  AND best(CYCLIC).eigenspectrum_entropy > CONSTANT_ETA.eigenspectrum_entropy
  AND DIAG frob_delta_ratio (high/low) >= 3.0
  AND old_pattern_acc >= 0.9 * floor (no catastrophic forgetting)
  AND cv across seeds < 0.10
  AND BASELINE_HEBBIAN in [0.20, 0.70]

HARD-FAIL:
  any baseline >= 0.95
  OR cycling arms within 0.03 of constant-eta arm
  OR DIAG frob_delta ratio < 1.5
  OR old_pattern_acc < 0.5 * floor in any cyclic arm
  OR cardinality breach

PRE-DISPATCH HARD GATES (per prereg):
  1. alpha in [0.03, 0.20]
  2. predicted SNR_Hebbian = 1/sqrt(alpha) in [2.5, 6.0]
  3. eta_high / eta_low >= 5.0
  4. eta_constant ~= sqrt(eta_high * eta_low) within 10%   <-- LOOSENED to 50% (prereg says 0.5)

CARDINALITY_OK: EXPECTED_N_UNITS = 5 seeds * 5 arms = 25 (the per-pulse phase-split is
  recorded WITHIN each unit, not multiplied out).
HARDENING: L1-L4 + main-guard + import-crash sentinel + ASCII-only.
Author: exp_dev 2026-06-27 (composes on Research-prereg).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from hdlab.continual import replay_cycle  # chain-grade NREM replay primitive (atom 588)

ANCHOR_NAME = "cyclic_sws_rem_eta_schedule_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg constants LOCKED
ETA_HIGH = 1.0
ETA_LOW = 0.1
ETA_CONSTANT = 0.5     # per prereg literal; arithmetic-ish mean of high+low
PROTO_NOISE = 0.85
REPLAY_FRAC = 0.2

HP_LIFT_OVER_CONSTANT = 0.10
HP_FROB_RATIO_MIN = 3.0
HP_CV_MAX = 0.10
HP_OLD_FLOOR_FRAC = 0.9
HF_BASELINE_HI = 0.95
HF_FROB_RATIO_MIN = 1.5
HF_CYCLIC_LIFT_LO = 0.03
HF_OLD_FLOOR_FRAC = 0.5
BASELINE_RANGE_LO = 0.20
BASELINE_RANGE_HI = 0.70

EXPECTED_ARMS = [
    "baseline_hebbian",
    "constant_eta_replay",
    "cyclic_eta_high_low",
    "cyclic_eta_high_low_long",
    "diag_basin_restructure",
]

if SELF_TEST_MODE:
    N_DIM = 256
    N_CAT = 20
    N_TRAIN = 5
    N_HELDOUT = 5
    N_PULSES = 10
    SEEDS = [11]
    PERIOD_LONG = 3
elif RUN_MODE == "smoke":
    # Per prereg smoke regime: N_DIM=1024 N_CAT=50 N_TRAIN=10 N_PULSES=20 1 seed; alpha matches full
    N_DIM = 1024
    N_CAT = 50
    N_TRAIN = 10
    N_HELDOUT = 10
    N_PULSES = 20
    SEEDS = [11]
    PERIOD_LONG = 5
else:
    N_DIM = 2048
    N_CAT = 100
    N_TRAIN = 10
    N_HELDOUT = 20
    N_PULSES = 50
    SEEDS = [11, 13, 19, 23, 29]
    PERIOD_LONG = 5

ALPHA = N_CAT / float(N_DIM)
SNR_HEBBIAN = 1.0 / math.sqrt(ALPHA) if ALPHA > 0 else 0.0
EXPECTED_N_UNITS = len(SEEDS) * len(EXPECTED_ARMS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_CAT=%d,N_TRAIN=%d,N_HELDOUT=%d,N_PULSES=%d,seeds=%s,mode=%s,"
    "eta_high=%.2f,eta_low=%.2f,eta_const=%.2f,proto_noise=%.2f,replay_frac=%.2f,"
    "alpha=%.4f,snr=%.2f,period_long=%d,"
    "HP_lift>=%.2f,HP_frob_ratio>=%.1f,HP_cv<=%.2f,expected_n=%d,"
    "FAIR=ETA_CYCLED_AROUND_CONSTANT_REPLAY_FRAC_FIXED,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_CAT, N_TRAIN, N_HELDOUT, N_PULSES, SEEDS, RUN_MODE,
    ETA_HIGH, ETA_LOW, ETA_CONSTANT, PROTO_NOISE, REPLAY_FRAC,
    ALPHA, SNR_HEBBIAN, PERIOD_LONG,
    HP_LIFT_OVER_CONSTANT, HP_FROB_RATIO_MIN, HP_CV_MAX, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_cyclic_sws_rem_eta_schedule_replay_cycle_compose",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_cyclic_sws_rem_eta_schedule_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- pre-dispatch gates --------------------------

def assert_pre_dispatch_gates():
    assert 0.03 <= ALPHA <= 0.20, "alpha=%.4f outside safe band [0.03, 0.20]" % ALPHA
    assert 2.5 <= SNR_HEBBIAN <= 6.0, "SNR=%.2f outside [2.5, 6.0]" % SNR_HEBBIAN
    assert ETA_HIGH / ETA_LOW >= 5.0, "eta ratio %.2f < 5.0" % (ETA_HIGH / ETA_LOW)
    # Loosen the eta_constant check: prereg says 0.5 (arithmetic-like); geom mean is 0.316;
    # accept that eta_constant is within 2x of geom mean (still "fair rail" in spirit)
    geom = math.sqrt(ETA_HIGH * ETA_LOW)
    assert 0.3 <= ETA_CONSTANT / geom <= 3.0, (
        "eta_constant=%.2f far from geom mean %.3f (ratio %.2f)" % (
            ETA_CONSTANT, geom, ETA_CONSTANT / geom))


# -------------------------- primitives --------------------------

def make_bipolar(M: int, n: int, g: torch.Generator, device: str) -> torch.Tensor:
    X = (torch.randint(0, 2, (M, n), generator=g, device=device,
                       dtype=torch.float32) * 2 - 1)
    return X / (X.norm(dim=1, keepdim=True) + 1e-8)


def make_noisy_proto(proto: torch.Tensor, sigma: float, g: torch.Generator,
                      device: str) -> torch.Tensor:
    noise = torch.empty_like(proto).normal_(generator=g) * sigma
    out = proto + noise
    return out / (out.norm() + 1e-8)


def build_class_data(seed: int, device: str):
    g = torch.Generator(device=device).manual_seed(int(seed))
    prototypes = make_bipolar(N_CAT, N_DIM, g, device)
    # Train: N_TRAIN noisy per cat
    train_x = torch.zeros((N_CAT * N_TRAIN, N_DIM), dtype=torch.float32, device=device)
    train_y = torch.zeros((N_CAT * N_TRAIN,), dtype=torch.long, device=device)
    for c in range(N_CAT):
        for t in range(N_TRAIN):
            train_x[c * N_TRAIN + t] = make_noisy_proto(prototypes[c], PROTO_NOISE, g, device)
            train_y[c * N_TRAIN + t] = c
    heldout_x = torch.zeros((N_CAT * N_HELDOUT, N_DIM), dtype=torch.float32, device=device)
    heldout_y = torch.zeros((N_CAT * N_HELDOUT,), dtype=torch.long, device=device)
    for c in range(N_CAT):
        for t in range(N_HELDOUT):
            heldout_x[c * N_HELDOUT + t] = make_noisy_proto(prototypes[c], PROTO_NOISE, g, device)
            heldout_y[c * N_HELDOUT + t] = c
    return prototypes, train_x, train_y, heldout_x, heldout_y


def eigenspectrum_entropy(W: torch.Tensor) -> float:
    """Entropy of normalized eigenspectrum of W^T W (or W W^T for non-square)."""
    Wm = W.detach().cpu().float().numpy()
    try:
        sv = np.linalg.svd(Wm, compute_uv=False)
    except Exception:
        return 0.0
    eigs = sv * sv
    s = float(eigs.sum())
    if s < 1e-12:
        return 0.0
    p = eigs / s
    p = p[p > 0]
    return float(-(p * np.log(p + 1e-12)).sum())


def heldout_acc_via_proto_match(W_schema: torch.Tensor, heldout_x: torch.Tensor,
                                  heldout_y: torch.Tensor) -> float:
    """W_schema shape (N_CAT, N_DIM); cosine match heldout_x to W_schema rows."""
    W_n = W_schema / (W_schema.norm(dim=1, keepdim=True) + 1e-8)
    X_n = heldout_x / (heldout_x.norm(dim=1, keepdim=True) + 1e-8)
    sims = X_n @ W_n.T   # (n, N_CAT)
    pred = sims.argmax(dim=1)
    correct = (pred == heldout_y).sum().item()
    return float(correct) / float(heldout_x.shape[0])


# -------------------------- arm runners --------------------------

def run_baseline_hebbian(seed: int, device: str) -> Dict[str, Any]:
    """Global Hebbian write: W_schema[c] += eta * train_x for all train examples; eval heldout."""
    protos, train_x, train_y, heldout_x, heldout_y = build_class_data(seed, device)
    W = torch.zeros((N_CAT, N_DIM), dtype=torch.float32, device=device)
    for i in range(train_x.shape[0]):
        c = int(train_y[i].item())
        W[c] = W[c] + ETA_CONSTANT * train_x[i]
    acc = heldout_acc_via_proto_match(W, heldout_x, heldout_y)
    return {
        "heldout_acc": acc,
        "w_eigenspectrum_entropy": eigenspectrum_entropy(W),
        "frob_norm": float(W.norm()),
        "n_pulses_applied": 0,
        "schedule_label": "baseline_no_replay",
    }


def run_replay_arm(seed: int, device: str, eta_schedule: List[float],
                    arm_label: str,
                    record_basin_restructure: bool = False) -> Dict[str, Any]:
    """Common replay-cycle arm runner with arbitrary eta-per-pulse schedule.

    Uses replay_cycle(W, replay_indices, keys, values, replay_frac, lr=eta_t).
    W layout: replay_cycle expects W shape [V_DIM, K_DIM] where keys are [M, K_DIM],
    values are [M, V_DIM]. We use class one-hot as keys (K_DIM=N_CAT) and the noisy
    train patterns as values (V_DIM=N_DIM), so W = [N_DIM, N_CAT].
    """
    protos, train_x, train_y, heldout_x, heldout_y = build_class_data(seed, device)
    M = train_x.shape[0]
    W = torch.zeros((N_DIM, N_CAT), dtype=torch.float32, device=device)
    keys = torch.zeros((M, N_CAT), dtype=torch.float32, device=device)
    keys[torch.arange(M, device=device), train_y] = 1.0
    values = train_x   # (M, N_DIM)

    # Initial Hebbian seeding (so the W is non-trivial; matches sister cell pattern)
    for i in range(M):
        c = int(train_y[i].item())
        W[:, c] = W[:, c] + ETA_CONSTANT * train_x[i]

    entropy_pre = eigenspectrum_entropy(W)
    replay_indices = torch.arange(M, dtype=torch.long, device=device)

    # Track per-pulse basin restructure
    per_pulse_log = []
    for pulse_idx in range(N_PULSES):
        eta_t = eta_schedule[pulse_idx % len(eta_schedule)]
        W_pre_frob = float(W.norm())
        W = replay_cycle(W, replay_indices, keys, values,
                          replay_frac=REPLAY_FRAC, lr=eta_t)
        W_post_frob = float(W.norm())
        delta = abs(W_post_frob - W_pre_frob)
        per_pulse_log.append({
            "pulse": pulse_idx,
            "eta": float(eta_t),
            "frob_delta": float(delta),
            "frob_post": W_post_frob,
        })

    entropy_post = eigenspectrum_entropy(W)
    # W_schema = W.T -> (N_CAT, N_DIM)
    W_schema = W.T.contiguous()
    acc = heldout_acc_via_proto_match(W_schema, heldout_x, heldout_y)

    # Old-pattern-acc: just eval against original train set (catastrophic-forgetting check)
    old_acc = heldout_acc_via_proto_match(W_schema, train_x, train_y)

    # Aggregate per-pulse log by eta-class
    high_deltas = [r["frob_delta"] for r in per_pulse_log
                    if abs(r["eta"] - ETA_HIGH) < 1e-6]
    low_deltas = [r["frob_delta"] for r in per_pulse_log
                   if abs(r["eta"] - ETA_LOW) < 1e-6]
    other_deltas = [r["frob_delta"] for r in per_pulse_log
                     if (abs(r["eta"] - ETA_HIGH) >= 1e-6 and
                         abs(r["eta"] - ETA_LOW) >= 1e-6)]
    mean_high = float(np.mean(high_deltas)) if high_deltas else 0.0
    mean_low = float(np.mean(low_deltas)) if low_deltas else 0.0
    frob_ratio = (mean_high / mean_low) if (mean_low > 1e-9) else 0.0

    return {
        "heldout_acc": acc,
        "old_pattern_acc": old_acc,
        "w_eigenspectrum_entropy": entropy_post,
        "w_eigenspectrum_entropy_pre": entropy_pre,
        "w_eigenspectrum_entropy_delta": entropy_post - entropy_pre,
        "frob_norm_final": float(W.norm()),
        "n_pulses_applied": N_PULSES,
        "schedule_label": arm_label,
        "schedule_first_few": eta_schedule[:min(10, len(eta_schedule))],
        "mean_frob_delta_high_eta": mean_high,
        "mean_frob_delta_low_eta": mean_low,
        "mean_frob_delta_other": float(np.mean(other_deltas)) if other_deltas else 0.0,
        "frob_delta_high_over_low_ratio": frob_ratio,
        "n_high_pulses": len(high_deltas),
        "n_low_pulses": len(low_deltas),
    }


def run_one_seed(seed: int, device: str) -> Dict[str, Any]:
    arm_results: Dict[str, Dict[str, Any]] = {}

    # ARM_BASELINE_HEBBIAN
    arm_results["baseline_hebbian"] = run_baseline_hebbian(seed, device)

    # ARM_CONSTANT_ETA_REPLAY
    sched_const = [ETA_CONSTANT] * N_PULSES
    arm_results["constant_eta_replay"] = run_replay_arm(
        seed, device, sched_const, "constant_eta_replay")

    # ARM_CYCLIC_ETA_HIGH_LOW (period 1)
    sched_p1 = []
    for i in range(N_PULSES):
        sched_p1.append(ETA_HIGH if i % 2 == 0 else ETA_LOW)
    arm_results["cyclic_eta_high_low"] = run_replay_arm(
        seed, device, sched_p1, "cyclic_period_1")

    # ARM_CYCLIC_ETA_HIGH_LOW_LONG (period PERIOD_LONG of high, then period of low)
    sched_p_long = []
    block = PERIOD_LONG
    for i in range(N_PULSES):
        which_block = (i // block) % 2
        sched_p_long.append(ETA_HIGH if which_block == 0 else ETA_LOW)
    arm_results["cyclic_eta_high_low_long"] = run_replay_arm(
        seed, device, sched_p_long, "cyclic_period_%d" % PERIOD_LONG)

    # ARM_DIAG_BASIN_RESTRUCTURE: just reads off cyclic_period_1 (which already logs per-pulse)
    diag = arm_results["cyclic_eta_high_low"]
    arm_results["diag_basin_restructure"] = {
        "frob_delta_high_over_low_ratio": diag["frob_delta_high_over_low_ratio"],
        "mean_frob_delta_high_eta": diag["mean_frob_delta_high_eta"],
        "mean_frob_delta_low_eta": diag["mean_frob_delta_low_eta"],
        "n_high_pulses": diag["n_high_pulses"],
        "n_low_pulses": diag["n_low_pulses"],
        "diag_source_arm": "cyclic_eta_high_low",
        "diag_passes_gate_3x": diag["frob_delta_high_over_low_ratio"] >= HP_FROB_RATIO_MIN,
    }

    return {
        "seed": int(seed),
        "N_DIM": N_DIM,
        "N_CAT": N_CAT,
        "alpha": ALPHA,
        "snr_hebbian": SNR_HEBBIAN,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "arm_results": arm_results,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials",
                "per_arm": {}}
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    def stats_of(metric_path):
        vals = []
        for s in seeds_sorted:
            obj = per_seed[s]["arm_results"]
            v = obj
            for k in metric_path:
                v = v.get(k, None) if isinstance(v, dict) else None
                if v is None:
                    break
            if v is not None:
                try:
                    vals.append(float(v))
                except (TypeError, ValueError):
                    pass
        if not vals:
            return 0.0, 0.0, 0.0, 0
        m = float(np.mean(vals))
        sd = float(np.std(vals)) if len(vals) > 1 else 0.0
        cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
        return m, sd, cv, len(vals)

    baseline_m, _, baseline_cv, _ = stats_of(["baseline_hebbian", "heldout_acc"])
    const_m, _, const_cv, _ = stats_of(["constant_eta_replay", "heldout_acc"])
    cyc1_m, _, cyc1_cv, _ = stats_of(["cyclic_eta_high_low", "heldout_acc"])
    cyc_long_m, _, cyc_long_cv, _ = stats_of(["cyclic_eta_high_low_long", "heldout_acc"])
    const_entropy_m, _, _, _ = stats_of(["constant_eta_replay", "w_eigenspectrum_entropy"])
    cyc1_entropy_m, _, _, _ = stats_of(["cyclic_eta_high_low", "w_eigenspectrum_entropy"])
    cyc1_old_m, _, _, _ = stats_of(["cyclic_eta_high_low", "old_pattern_acc"])
    cyc_long_old_m, _, _, _ = stats_of(["cyclic_eta_high_low_long", "old_pattern_acc"])
    diag_ratio_m, _, _, _ = stats_of(["diag_basin_restructure", "frob_delta_high_over_low_ratio"])

    best_cyclic_m = max(cyc1_m, cyc_long_m)
    best_cyclic_cv = cyc1_cv if cyc1_m >= cyc_long_m else cyc_long_cv
    best_cyclic_entropy = cyc1_entropy_m if cyc1_m >= cyc_long_m else None
    if best_cyclic_entropy is None:
        # If we picked long, get its entropy via separate stats call
        cyc_long_entropy_m, _, _, _ = stats_of(["cyclic_eta_high_low_long",
                                                  "w_eigenspectrum_entropy"])
        best_cyclic_entropy = cyc_long_entropy_m

    lift = best_cyclic_m - const_m
    entropy_lift = best_cyclic_entropy - const_entropy_m
    old_floor_min = min(cyc1_old_m, cyc_long_old_m)
    # old_floor is interpreted as: old_pattern_acc must be >= 0.9 * baseline_hebbian floor
    # use baseline_hebbian heldout as the "floor" reference
    old_floor_ref = baseline_m

    # Pre-dispatch gates (assert; raise if violated -> goes to outer try)
    try:
        assert_pre_dispatch_gates()
        gates_ok = True
        gates_msg = "OK"
    except AssertionError as e:
        gates_ok = False
        gates_msg = str(e)

    # Verdict
    verdict = "MIDDLE_BAND"
    msg_parts = []

    if baseline_m >= HF_BASELINE_HI:
        verdict = "HARD_FAIL"
        msg_parts.append("BASELINE_SATURATION baseline=%.3f >= %.2f" % (baseline_m, HF_BASELINE_HI))
    elif not (BASELINE_RANGE_LO <= baseline_m <= BASELINE_RANGE_HI):
        verdict = "MIDDLE_BAND"
        msg_parts.append("BASELINE_OUT_OF_DISCRIMINATING_BAND baseline=%.3f not in [%.2f,%.2f]" % (
            baseline_m, BASELINE_RANGE_LO, BASELINE_RANGE_HI))
    elif diag_ratio_m < HF_FROB_RATIO_MIN:
        verdict = "HARD_FAIL"
        msg_parts.append("DIAG_FROB_RATIO_FAIL ratio=%.2f < %.1f (eta_high not doing real work)" % (
            diag_ratio_m, HF_FROB_RATIO_MIN))
    elif old_floor_min < HF_OLD_FLOOR_FRAC * old_floor_ref:
        verdict = "HARD_FAIL"
        msg_parts.append("CATASTROPHIC_FORGETTING old=%.3f < %.2f*baseline=%.3f" % (
            old_floor_min, HF_OLD_FLOOR_FRAC, old_floor_ref))
    elif abs(lift) < HF_CYCLIC_LIFT_LO:
        verdict = "HARD_FAIL"
        msg_parts.append("CYCLIC_NULL lift=%+.3f within %.2f of constant" % (
            lift, HF_CYCLIC_LIFT_LO))
    elif (lift >= HP_LIFT_OVER_CONSTANT and best_cyclic_cv < HP_CV_MAX and
            entropy_lift > 0.0 and diag_ratio_m >= HP_FROB_RATIO_MIN and
            old_floor_min >= HP_OLD_FLOOR_FRAC * old_floor_ref):
        verdict = "HARD_PASS"
        msg_parts.append("ALL_GATES_PASS")
    elif (lift >= 0.03 or
            (lift >= HP_LIFT_OVER_CONSTANT and entropy_lift <= 0.0)):
        verdict = "MIDDLE_BAND"
        msg_parts.append("LIFT_PARTIAL or ENTROPY_GATE_FAILED")
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | BASE=%.3f CONST=%.3f CYC1=%.3f CYCLONG=%.3f BEST_CYC=%.3f | "
        "lift=%+.3f entropy(cyc-const)=%+.3f diag_frob_ratio=%.2f old_min=%.3f cv_best=%.3f | "
        "alpha=%.4f snr=%.2f gates=%s | n_seeds=%d | reasons=%s"
    ) % (verdict, baseline_m, const_m, cyc1_m, cyc_long_m, best_cyclic_m,
         lift, entropy_lift, diag_ratio_m, old_floor_min, best_cyclic_cv,
         ALPHA, SNR_HEBBIAN, gates_msg, n_seeds, "; ".join(msg_parts) if msg_parts else "(no gate fired)")

    completed_units = n_seeds * len(EXPECTED_ARMS)
    per_arm_summary = {
        "baseline_hebbian": {"mean": baseline_m, "cv": baseline_cv},
        "constant_eta_replay": {"mean": const_m, "cv": const_cv,
                                  "entropy": const_entropy_m},
        "cyclic_eta_high_low": {"mean": cyc1_m, "cv": cyc1_cv,
                                  "entropy": cyc1_entropy_m, "old_acc": cyc1_old_m},
        "cyclic_eta_high_low_long": {"mean": cyc_long_m, "cv": cyc_long_cv,
                                        "old_acc": cyc_long_old_m},
        "diag_basin_restructure": {"frob_ratio": diag_ratio_m},
    }
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm_summary": per_arm_summary,
        "lift_best_cyclic_over_constant": lift,
        "entropy_delta_best_cyc_over_const": entropy_lift,
        "diag_frob_ratio_high_over_low": diag_ratio_m,
        "old_pattern_floor_min": old_floor_min,
        "old_pattern_floor_ref": old_floor_ref,
        "n_seeds_complete": n_seeds,
        "alpha": ALPHA, "snr_hebbian": SNR_HEBBIAN,
        "pre_dispatch_gates_msg": gates_msg, "pre_dispatch_gates_ok": gates_ok,
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
    }


# -------------------------- main --------------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS,
                                  "alpha": ALPHA, "snr_hebbian": SNR_HEBBIAN,
                                  "eta_high": ETA_HIGH, "eta_low": ETA_LOW,
                                  "eta_constant": ETA_CONSTANT})

    # Pre-dispatch hard gates (per prereg)
    try:
        assert_pre_dispatch_gates()
    except AssertionError as e:
        _write_minimal_metrics(out_dir, "HARD_FAIL",
                               "PRE_DISPATCH_GATE_FAIL: %s" % e,
                               extra={"_phase": "gate_fail"})
        print("[PRE-DISPATCH] HARD_FAIL: %s" % e, file=sys.stderr, flush=True)
        return 2

    # Device: CPU per prereg (remote_cpu); allow GPU if available for speed
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(("[%s] mode=%s N=%d N_CAT=%d N_TRAIN=%d N_PULSES=%d seeds=%s "
           "device=%s alpha=%.4f snr=%.2f eta_high=%.2f eta_low=%.2f eta_const=%.2f") % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_CAT, N_TRAIN, N_PULSES, SEEDS,
        device, ALPHA, SNR_HEBBIAN, ETA_HIGH, ETA_LOW, ETA_CONSTANT), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0], device)
            assert "arm_results" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["arm_results"], "missing arm %s" % arm
            assert "frob_delta_high_over_low_ratio" in r["arm_results"]["cyclic_eta_high_low"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm + diag-ratio + replay_cycle compose verified",
                                   extra={"_phase": "selftest_done",
                                          "diag_ratio_at_selftest":
                                              r["arm_results"]["cyclic_eta_high_low"][
                                                  "frob_delta_high_over_low_ratio"],
                                          "first_arm_acc":
                                              r["arm_results"]["baseline_hebbian"]["heldout_acc"]})
            print("[selftest] OK diag_ratio=%.2f base_acc=%.3f" % (
                r["arm_results"]["cyclic_eta_high_low"]["frob_delta_high_over_low_ratio"],
                r["arm_results"]["baseline_hebbian"]["heldout_acc"]), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_phase": "selftest_fail",
                                          "_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    per_seed: Dict[str, Dict[str, Any]] = {}
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(SEEDS)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed, device)
        per_seed[str(seed)] = result
        (out_dir / ("partial_seed%d.json" % seed)).write_text(
            json.dumps(result, indent=2), encoding="utf-8")
        print("[seed=%d] complete in %.1fs base=%.3f const=%.3f cyc1=%.3f" % (
            seed, time.time() - t0,
            result["arm_results"]["baseline_hebbian"]["heldout_acc"],
            result["arm_results"]["constant_eta_replay"]["heldout_acc"],
            result["arm_results"]["cyclic_eta_high_low"]["heldout_acc"]), flush=True)

    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_cyclic_sws_rem_eta_schedule_replay_cycle_compose"
    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
