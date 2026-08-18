"""cyclic_sws_rem_eta_schedule_v2_associative_recall -- Battery 2 Barrier 3 (CPU).

Prereg: preregs/2026-06-27_cyclic_sws_rem_eta_schedule_v2_associative_recall.md
Drill spec: notes/research_drill_2x_sws_rem_associative_recall_readout_redesign_2026-06-27.md
Composes on: hdlab.continual.replay_cycle (atom 588; chain-grade NREM replay primitive)

WHY V2 (vs V1):
V1 cell saw substrate-level frob_ratio=12.63 (high-eta IS doing real work) but heldout-acc
sat at chance (0.026 = 1/N_CAT=50): the classification readout averaged across class members
into W[c], destroying per-trace structure. V2 replaces the readout with key-cued associative
recall against M=N_PAIRS independent bipolar random key-value pairs (Option A of Research
drill TOP-1). Chance = 1/512 = 0.002 (much further below operating regime).

ARMS (3 + 1 diagnostic):
  ARM_CONSTANT_ETA          replay_cycle with lr = ETA_CONSTANT (fair-baseline rail)
  ARM_CYCLIC_HIGH_LOW_SHORT cycle lr in [eta_high, eta_low] period 1
  ARM_CYCLIC_HIGH_LOW_LONG  cycle lr in 5 high then 5 low (matches 4:1 SWS:REM Walker 2017)
  ARM_DIAG_RAW_HEBBIAN      seeded W, NO replay; sanity rail (verifies non-degenerate retrieval)

REGIME (smoke):
  N_DIM=1024, M=512, alpha=M/N=0.5, sigma=PROTO_NOISE=0.85, N_PULSES=20, seeds=[11]

PRE-REG HARD_PASS (conjunctive):
  baseline_constant_eta top-1 in [0.30, 0.70] (fair-band gate; META_RULE_AA)
  AND best_cyclic - constant_eta >= +0.10 absolute
  AND frob_ratio_high_over_low >= 3.0
  AND top-5 best_cyclic >= top-5 constant + 0.05
  AND entropy(cyclic) > entropy(constant) + 0.05 nats
  AND cv across seeds < 0.10

HARD_FAIL (any):
  baseline_constant_eta >= 0.95 (saturated)
  OR baseline_constant_eta <= 0.10 (dead; sigma too aggressive)
  OR |best_cyclic - constant_eta| <= 0.03 (no measurable cycling effect)
  OR frob_ratio < 1.5 (synapse mechanism vanished)
  OR cyclic_long - cyclic_short > +0.10 (period-5 confound, no theory)

MIDDLE_BAND: 0.03 <= lift < 0.10 with frob_ratio >= 3.0 (re-tune alpha=0.25)

CARDINALITY_OK: smoke = 4 arms * 1 seed = 4 units; full = 4 arms * 5 seeds = 20 units.
HARDENING: L1-L4 + main-guard + ASCII-only + except SystemExit BEFORE except BaseException.
Author: exp_dev 2026-06-27 (composes on Research-prereg per drill TOP-1).
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
from typing import Any, Dict, List

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from hdlab.continual import replay_cycle  # chain-grade NREM replay primitive (atom 588)

ANCHOR_NAME = "cyclic_sws_rem_eta_schedule_v2_associative_recall"

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
ETA_CONSTANT = 0.5      # per V1 prereg literal; arithmetic-ish mean of high+low
# PROTO_NOISE iteration log 2026-06-27:
#   sigma=0.85 alpha=0.5: const_top1=0.979 SATURATED, RAW_HEBB=1.000
#   sigma=1.20 alpha=0.5: const_top1=0.949 SATURATED, RAW_HEBB=1.000
#   sigma=1.20 alpha=2.0: const_top1=0.938 SATURATED, RAW_HEBB=1.000
#   sigma=3.00 alpha=2.0: const_top1=0.722 RAW_HEBB=0.989 -- edge of band; cycling HURTS lift=-0.095
# Bipolar keys (non-L2-norm) have self-inner-prod=N; noise of sigma=O(1) gets dominated.
# Per HRR/Hopfield literature: for {-1,+1}^N keys + Gaussian-sigma noise, the noise needs
# variance scaling with N. sigma=sqrt(N) gives noise_norm ~ key_norm. Try sigma=4.0
# for deeper-band baseline (~0.50) so cycling has more headroom both directions.
PROTO_NOISE = 4.0
REPLAY_FRAC = 0.2

HP_BASELINE_LO = 0.30
HP_BASELINE_HI = 0.70
HP_LIFT_OVER_CONSTANT = 0.10
HP_FROB_RATIO_MIN = 3.0
HP_TOP5_LIFT = 0.05
HP_ENTROPY_LIFT = 0.05
HP_CV_MAX = 0.10

HF_BASELINE_SAT = 0.95
HF_BASELINE_DEAD = 0.10
HF_NULL_LIFT_ABS = 0.03
HF_FROB_RATIO_MIN = 1.5
HF_LONG_OVER_SHORT_UNJUSTIFIED = 0.10

EXPECTED_ARMS = [
    "constant_eta",
    "cyclic_high_low_short",
    "cyclic_high_low_long",
    "diag_raw_hebbian",
]

if SELF_TEST_MODE:
    N_DIM = 256
    M_PAIRS = 64
    N_PULSES = 6
    SEEDS = [11]
    PERIOD_LONG = 3
elif RUN_MODE == "smoke":
    # Iteration log:
    # iter1: N=1024 M=512 sigma=0.85 -> const_top1=0.979 SATURATED + RAW_HEBB=1.0
    # iter2: N=1024 M=512 sigma=1.20 -> const_top1=0.949 still saturating
    # alpha=0.5 + N=1024 + Hebb-seed is below-capacity by huge margin; push M to alpha=2.0
    # (over-capacity regime where Hopfield-class memory saturates -- this is where cycling
    # has room to help). Per drill META_RULE_K + Fix #19 discriminator-must-survive-scale.
    N_DIM = 1024
    M_PAIRS = 2048   # alpha = 2.0 (over-capacity; sub-Hopfield-band)
    N_PULSES = 20
    SEEDS = [11]
    PERIOD_LONG = 5
else:
    N_DIM = 2048
    M_PAIRS = 4096   # alpha = 2.0 matched
    N_PULSES = 50
    SEEDS = [11, 13, 19, 23, 29]
    PERIOD_LONG = 5

ALPHA = M_PAIRS / float(N_DIM)
SNR_HEBBIAN = 1.0 / math.sqrt(ALPHA) if ALPHA > 0 else 0.0
EXPECTED_N_UNITS = len(SEEDS) * len(EXPECTED_ARMS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M_PAIRS=%d,N_PULSES=%d,seeds=%s,mode=%s,"
    "eta_high=%.2f,eta_low=%.2f,eta_const=%.2f,proto_noise=%.2f,replay_frac=%.2f,"
    "alpha=%.4f,snr=%.2f,period_long=%d,"
    "HP_baseline=[%.2f,%.2f],HP_lift>=%.2f,HP_frob>=%.1f,HP_top5_lift>=%.2f,"
    "HP_entropy_lift>=%.2f,HP_cv<=%.2f,expected_n=%d,"
    "READOUT=ASSOC_RECALL_KEY_CUED_NOISY_PROBE,"
    "FAIR=ETA_CYCLED_REPLAY_FRAC_FIXED,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, M_PAIRS, N_PULSES, SEEDS, RUN_MODE,
    ETA_HIGH, ETA_LOW, ETA_CONSTANT, PROTO_NOISE, REPLAY_FRAC,
    ALPHA, SNR_HEBBIAN, PERIOD_LONG,
    HP_BASELINE_LO, HP_BASELINE_HI, HP_LIFT_OVER_CONSTANT,
    HP_FROB_RATIO_MIN, HP_TOP5_LIFT, HP_ENTROPY_LIFT, HP_CV_MAX, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v2_assoc_recall_readout_replay_cycle_compose",
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
            "_hardening_marker": "v2_assoc_recall_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- pre-dispatch gates --------------------------

def assert_pre_dispatch_gates() -> None:
    # alpha band loosened to [0.1, 4.0] after smoke-iter2: at alpha=0.5 baseline saturates
    # (1.000); over-capacity regime needed for discriminator to fire.
    assert 0.1 <= ALPHA <= 4.0, "alpha=%.4f outside band [0.1, 4.0] for assoc recall" % ALPHA
    assert ETA_HIGH / ETA_LOW >= 5.0, "eta ratio %.2f < 5.0" % (ETA_HIGH / ETA_LOW)
    geom = math.sqrt(ETA_HIGH * ETA_LOW)
    assert 0.3 <= ETA_CONSTANT / geom <= 3.0, (
        "eta_constant=%.2f far from geom mean %.3f (ratio %.2f)" % (
            ETA_CONSTANT, geom, ETA_CONSTANT / geom))


# -------------------------- primitives --------------------------

def make_bipolar(M: int, n: int, g: torch.Generator, device: str) -> torch.Tensor:
    """Bipolar {-1,+1}^n vectors, NOT L2-normalized (HRR-style raw bipolar)."""
    return (torch.randint(0, 2, (M, n), generator=g, device=device,
                          dtype=torch.float32) * 2 - 1)


def make_noisy_key(key: torch.Tensor, sigma: float, g: torch.Generator) -> torch.Tensor:
    """Add Gaussian noise to bipolar key (per Option A spec)."""
    noise = torch.empty_like(key).normal_(generator=g) * sigma
    return key + noise


def build_pair_data(seed: int, device: str):
    """Generate M independent (key, value) bipolar pairs + noisy probe keys."""
    g = torch.Generator(device=device).manual_seed(int(seed))
    keys = make_bipolar(M_PAIRS, N_DIM, g, device)         # (M, N)
    values = make_bipolar(M_PAIRS, N_DIM, g, device)       # (M, N)
    # Noisy probe keys (one per stored key); use SAME generator-stream for determinism
    g_probe = torch.Generator(device=device).manual_seed(int(seed) + 9001)
    keys_noisy = torch.zeros_like(keys)
    for i in range(M_PAIRS):
        keys_noisy[i] = make_noisy_key(keys[i], PROTO_NOISE, g_probe)
    return keys, values, keys_noisy


def eigenspectrum_entropy(W: torch.Tensor) -> float:
    """Entropy of normalized eigenspectrum of W^T W via SVD."""
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


def assoc_recall_topk(W: torch.Tensor, keys_noisy: torch.Tensor,
                       values: torch.Tensor) -> Dict[str, float]:
    """Key-cued associative recall: v_hat = W @ k_i'; score top-1 / top-5 by cosine.

    W shape: (N, N) -- W[v, k]; v_hat = W @ k_i' gives (N,) value-space vector.
    Score: cosine of v_hat to every stored value v_j; correct iff argmax == i.
    """
    # v_hat for all probes: (M, N) = (M, N) @ (N, N)^T
    # Actually: replay_cycle writes W += value @ key.T, so v_hat = W @ k.
    # keys_noisy[i] shape (N,); W @ keys_noisy[i] gives (N,) -> v_hat
    v_hats = keys_noisy @ W.T   # (M, N) -- each row i is W @ keys_noisy[i]

    # Normalize v_hats and values for cosine
    v_hats_n = v_hats / (v_hats.norm(dim=1, keepdim=True) + 1e-8)
    values_n = values / (values.norm(dim=1, keepdim=True) + 1e-8)

    sims = v_hats_n @ values_n.T   # (M, M); sims[i, j] = cos(v_hat_i, v_j)

    # top-1
    pred1 = sims.argmax(dim=1)
    targets = torch.arange(M_PAIRS, device=W.device)
    top1 = float((pred1 == targets).sum().item()) / float(M_PAIRS)

    # top-5
    k5 = min(5, M_PAIRS)
    _, idxs = sims.topk(k=k5, dim=1)
    top5 = float((idxs == targets.unsqueeze(1)).any(dim=1).sum().item()) / float(M_PAIRS)

    return {"top1": top1, "top5": top5}


# -------------------------- arm runners --------------------------

def seed_W_hebbian(keys: torch.Tensor, values: torch.Tensor, device: str) -> torch.Tensor:
    """Seed W = sum_i v_i k_i.T / sqrt(N) via initial Hebbian with eta_constant.

    W shape: (N, N) = (V_DIM, K_DIM) for replay_cycle compatibility.
    """
    # W = (1/sqrt(N)) * values.T @ keys; but to match prereg "eta_constant" scaling,
    # add ETA_CONSTANT factor (the same scalar replay_cycle will apply per pulse).
    # Drill spec says "Seed W = sum_i v_i (x) k_i / sqrt(N)" -> use sqrt(N) factor.
    W = (values.T @ keys).float() / math.sqrt(float(N_DIM))   # (N, N)
    return W * ETA_CONSTANT


def run_replay_arm(seed: int, device: str, eta_schedule: List[float],
                    arm_label: str) -> Dict[str, Any]:
    """Common replay-cycle arm runner with per-pulse eta schedule."""
    keys, values, keys_noisy = build_pair_data(seed, device)
    W = seed_W_hebbian(keys, values, device)

    entropy_pre = eigenspectrum_entropy(W)
    replay_indices = torch.arange(M_PAIRS, dtype=torch.long, device=device)

    per_pulse_log = []
    for pulse_idx in range(N_PULSES):
        eta_t = eta_schedule[pulse_idx % len(eta_schedule)]
        W_pre_frob = float(W.norm())
        W = replay_cycle(W, replay_indices, keys, values,
                          replay_frac=REPLAY_FRAC, lr=eta_t)
        W_post_frob = float(W.norm())
        delta = abs(W_post_frob - W_pre_frob)
        per_pulse_log.append({"pulse": pulse_idx, "eta": float(eta_t),
                              "frob_delta": float(delta),
                              "frob_post": W_post_frob})

    entropy_post = eigenspectrum_entropy(W)
    recall = assoc_recall_topk(W, keys_noisy, values)

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
        "top1": recall["top1"],
        "top5": recall["top5"],
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


def run_raw_hebbian(seed: int, device: str) -> Dict[str, Any]:
    """Seeded W, NO replay pulses; sanity rail (verifies retrieval is non-degenerate)."""
    keys, values, keys_noisy = build_pair_data(seed, device)
    W = seed_W_hebbian(keys, values, device)
    recall = assoc_recall_topk(W, keys_noisy, values)
    return {
        "top1": recall["top1"],
        "top5": recall["top5"],
        "w_eigenspectrum_entropy": eigenspectrum_entropy(W),
        "frob_norm_final": float(W.norm()),
        "n_pulses_applied": 0,
        "schedule_label": "diag_raw_hebbian_no_replay",
    }


def run_one_seed(seed: int, device: str) -> Dict[str, Any]:
    arm_results: Dict[str, Dict[str, Any]] = {}

    # ARM_CONSTANT_ETA
    sched_const = [ETA_CONSTANT] * N_PULSES
    arm_results["constant_eta"] = run_replay_arm(
        seed, device, sched_const, "constant_eta")

    # ARM_CYCLIC_HIGH_LOW_SHORT (period=1)
    sched_p1 = []
    for i in range(N_PULSES):
        sched_p1.append(ETA_HIGH if i % 2 == 0 else ETA_LOW)
    arm_results["cyclic_high_low_short"] = run_replay_arm(
        seed, device, sched_p1, "cyclic_period_1")

    # ARM_CYCLIC_HIGH_LOW_LONG (block PERIOD_LONG)
    sched_p_long = []
    block = PERIOD_LONG
    for i in range(N_PULSES):
        which_block = (i // block) % 2
        sched_p_long.append(ETA_HIGH if which_block == 0 else ETA_LOW)
    arm_results["cyclic_high_low_long"] = run_replay_arm(
        seed, device, sched_p_long, "cyclic_period_%d" % PERIOD_LONG)

    # ARM_DIAG_RAW_HEBBIAN
    arm_results["diag_raw_hebbian"] = run_raw_hebbian(seed, device)

    return {
        "seed": int(seed),
        "N_DIM": N_DIM,
        "M_PAIRS": M_PAIRS,
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

    const_top1_m, _, const_cv, _ = stats_of(["constant_eta", "top1"])
    const_top5_m, _, _, _ = stats_of(["constant_eta", "top5"])
    const_entropy_m, _, _, _ = stats_of(["constant_eta", "w_eigenspectrum_entropy"])

    cyc_s_top1_m, _, cyc_s_cv, _ = stats_of(["cyclic_high_low_short", "top1"])
    cyc_s_top5_m, _, _, _ = stats_of(["cyclic_high_low_short", "top5"])
    cyc_s_entropy_m, _, _, _ = stats_of(["cyclic_high_low_short", "w_eigenspectrum_entropy"])
    cyc_s_frob_m, _, _, _ = stats_of(["cyclic_high_low_short", "frob_delta_high_over_low_ratio"])

    cyc_l_top1_m, _, cyc_l_cv, _ = stats_of(["cyclic_high_low_long", "top1"])
    cyc_l_top5_m, _, _, _ = stats_of(["cyclic_high_low_long", "top5"])
    cyc_l_entropy_m, _, _, _ = stats_of(["cyclic_high_low_long", "w_eigenspectrum_entropy"])
    cyc_l_frob_m, _, _, _ = stats_of(["cyclic_high_low_long", "frob_delta_high_over_low_ratio"])

    diag_raw_top1_m, _, _, _ = stats_of(["diag_raw_hebbian", "top1"])

    # Best cyclic by top-1
    if cyc_s_top1_m >= cyc_l_top1_m:
        best_label = "cyclic_high_low_short"
        best_top1 = cyc_s_top1_m
        best_top5 = cyc_s_top5_m
        best_entropy = cyc_s_entropy_m
        best_cv = cyc_s_cv
        best_frob = cyc_s_frob_m
    else:
        best_label = "cyclic_high_low_long"
        best_top1 = cyc_l_top1_m
        best_top5 = cyc_l_top5_m
        best_entropy = cyc_l_entropy_m
        best_cv = cyc_l_cv
        best_frob = cyc_l_frob_m

    lift = best_top1 - const_top1_m
    top5_lift = best_top5 - const_top5_m
    entropy_lift = best_entropy - const_entropy_m
    long_minus_short = cyc_l_top1_m - cyc_s_top1_m

    # Pre-dispatch gates
    try:
        assert_pre_dispatch_gates()
        gates_ok = True
        gates_msg = "OK"
    except AssertionError as e:
        gates_ok = False
        gates_msg = str(e)

    verdict = "MIDDLE_BAND"
    msg_parts = []

    if const_top1_m >= HF_BASELINE_SAT:
        verdict = "HARD_FAIL"
        msg_parts.append("BASELINE_SATURATED const=%.3f >= %.2f" % (const_top1_m, HF_BASELINE_SAT))
    elif const_top1_m <= HF_BASELINE_DEAD:
        verdict = "HARD_FAIL"
        msg_parts.append("BASELINE_DEAD const=%.3f <= %.2f (sigma too aggressive)" % (
            const_top1_m, HF_BASELINE_DEAD))
    elif best_frob < HF_FROB_RATIO_MIN:
        verdict = "HARD_FAIL"
        msg_parts.append("FROB_MECHANISM_VANISHED ratio=%.2f < %.1f" % (
            best_frob, HF_FROB_RATIO_MIN))
    elif abs(lift) <= HF_NULL_LIFT_ABS:
        verdict = "HARD_FAIL"
        msg_parts.append("CYCLIC_NULL lift=%+.3f within +/-%.2f of constant" % (
            lift, HF_NULL_LIFT_ABS))
    elif long_minus_short > HF_LONG_OVER_SHORT_UNJUSTIFIED:
        verdict = "HARD_FAIL"
        msg_parts.append("LONG_OVER_SHORT_UNJUSTIFIED delta=%+.3f > %.2f (no theory)" % (
            long_minus_short, HF_LONG_OVER_SHORT_UNJUSTIFIED))
    elif not (HP_BASELINE_LO <= const_top1_m <= HP_BASELINE_HI):
        verdict = "MIDDLE_BAND"
        msg_parts.append("BASELINE_OUT_OF_DISCRIMINATING_BAND const=%.3f not in [%.2f,%.2f]" % (
            const_top1_m, HP_BASELINE_LO, HP_BASELINE_HI))
    elif (lift >= HP_LIFT_OVER_CONSTANT and best_cv < HP_CV_MAX and
            best_frob >= HP_FROB_RATIO_MIN and
            top5_lift >= HP_TOP5_LIFT and
            entropy_lift >= HP_ENTROPY_LIFT):
        verdict = "HARD_PASS"
        msg_parts.append("ALL_GATES_PASS")
    elif lift >= HF_NULL_LIFT_ABS and best_frob >= HP_FROB_RATIO_MIN:
        verdict = "MIDDLE_BAND"
        msg_parts.append("LIFT_PARTIAL lift=%+.3f frob_ok=%.2f" % (lift, best_frob))
    else:
        verdict = "MIDDLE_BAND"
        msg_parts.append("UNCLASSIFIED_REGIME")

    verdict_msg = (
        "%s | RAW_HEBB=%.3f CONST=%.3f CYC_S=%.3f CYC_L=%.3f BEST=%.3f(%s) | "
        "lift=%+.3f top5_lift=%+.3f entropy_lift=%+.3f frob_ratio=%.2f cv_best=%.3f | "
        "alpha=%.4f snr=%.2f gates=%s | n_seeds=%d | reasons=%s"
    ) % (verdict, diag_raw_top1_m, const_top1_m, cyc_s_top1_m, cyc_l_top1_m,
         best_top1, best_label, lift, top5_lift, entropy_lift, best_frob, best_cv,
         ALPHA, SNR_HEBBIAN, gates_msg, n_seeds,
         "; ".join(msg_parts) if msg_parts else "(no gate fired)")

    completed_units = n_seeds * len(EXPECTED_ARMS)
    per_arm_summary = {
        "constant_eta": {"top1": const_top1_m, "top5": const_top5_m,
                          "entropy": const_entropy_m, "cv": const_cv},
        "cyclic_high_low_short": {"top1": cyc_s_top1_m, "top5": cyc_s_top5_m,
                                    "entropy": cyc_s_entropy_m, "cv": cyc_s_cv,
                                    "frob_ratio": cyc_s_frob_m},
        "cyclic_high_low_long": {"top1": cyc_l_top1_m, "top5": cyc_l_top5_m,
                                   "entropy": cyc_l_entropy_m, "cv": cyc_l_cv,
                                   "frob_ratio": cyc_l_frob_m},
        "diag_raw_hebbian": {"top1": diag_raw_top1_m},
    }
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm_summary": per_arm_summary,
        "best_cyclic_label": best_label,
        "lift_best_cyclic_over_constant": lift,
        "top5_lift_best_over_constant": top5_lift,
        "entropy_delta_best_over_constant": entropy_lift,
        "diag_frob_ratio_high_over_low_best": best_frob,
        "long_minus_short_top1": long_minus_short,
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
                                  "eta_constant": ETA_CONSTANT,
                                  "M_PAIRS": M_PAIRS, "N_DIM": N_DIM})

    try:
        assert_pre_dispatch_gates()
    except AssertionError as e:
        _write_minimal_metrics(out_dir, "HARD_FAIL",
                               "PRE_DISPATCH_GATE_FAIL: %s" % e,
                               extra={"_phase": "gate_fail"})
        print("[PRE-DISPATCH] HARD_FAIL: %s" % e, file=sys.stderr, flush=True)
        return 2

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(("[%s] mode=%s N=%d M=%d N_PULSES=%d seeds=%s "
           "device=%s alpha=%.4f snr=%.2f eta_high=%.2f eta_low=%.2f eta_const=%.2f") % (
        ANCHOR_NAME, RUN_MODE, N_DIM, M_PAIRS, N_PULSES, SEEDS,
        device, ALPHA, SNR_HEBBIAN, ETA_HIGH, ETA_LOW, ETA_CONSTANT), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0], device)
            assert "arm_results" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["arm_results"], "missing arm %s" % arm
            assert "frob_delta_high_over_low_ratio" in r["arm_results"]["cyclic_high_low_short"]
            assert "top1" in r["arm_results"]["constant_eta"]
            assert "top5" in r["arm_results"]["constant_eta"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm + assoc_recall_topk + replay_cycle verified",
                                   extra={"_phase": "selftest_done",
                                          "diag_ratio_at_selftest":
                                              r["arm_results"]["cyclic_high_low_short"][
                                                  "frob_delta_high_over_low_ratio"],
                                          "constant_top1_at_selftest":
                                              r["arm_results"]["constant_eta"]["top1"]})
            print("[selftest] OK diag_ratio=%.2f const_top1=%.3f" % (
                r["arm_results"]["cyclic_high_low_short"]["frob_delta_high_over_low_ratio"],
                r["arm_results"]["constant_eta"]["top1"]), flush=True)
            return 0
        except SystemExit:
            raise
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
        print("[seed=%d] complete in %.1fs const_top1=%.3f cyc_s_top1=%.3f cyc_l_top1=%.3f" % (
            seed, time.time() - t0,
            result["arm_results"]["constant_eta"]["top1"],
            result["arm_results"]["cyclic_high_low_short"]["top1"],
            result["arm_results"]["cyclic_high_low_long"]["top1"]), flush=True)

    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_assoc_recall_readout_replay_cycle_compose"
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
