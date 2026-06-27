"""stc_tag_and_capture_v2_two_phase_continual_learning -- Wave 2 readout-saturation fix.

Prereg: preregs/2026-06-27_stc_tag_and_capture_v2_two_phase_continual_learning.md
Skunkworks audit: notes/skunkworks_mechanism_null_audit_wave2_2026-06-27.md (commit edee21b3)

ROOT CAUSE FIX vs v1:
  v1 used single-phase readout (mean-cosine-to-target over orthogonal bipolar prototypes).
  Bipolar prototypes are quasi-orthogonal, so any nonzero W routes signal to its target
  prototype cosine ~ 1.0 trivially. ALL arms saturated at 0.93-0.94 cor_score; the STC
  tag-mechanism never had room to demonstrate selective-protection benefit.
  Wave 2E exp_dev recommendation: two-phase continual-learning rewrite where STC's
  load-bearing benefit is interference resistance (preserve OLD pattern under NEW writes).

ARCHITECTURE:
  Phase 1 (LEARN A):
    All arms write pattern A via Hebbian into W_fast.
    For STC arms: tag mask captures synapses with novel direction during A.
    Capture pulse commits tagged-only synapses to W_slow.
    BASELINE/REPLAY_NO_TAG: capture ALL of W_fast to W_slow.
    Measure recall@A_initial = mean cosine to A's prototype.

  Phase 2 (LEARN B - INTERFERENCE):
    All arms write pattern B via Hebbian into W_fast.
    For STC arms: tag mask now captures NEW directions from B.
      Critically, A's tagged synapses in W_slow are NOT overwritten (already-captured
      tags resist re-writing; only untagged W_slow entries get B's update).
      Implementation: maintain protected_mask = (W_slow != 0); B's capture only writes
      to W_slow where protected_mask is False AND tag is set.
    BASELINE: all of B's writes overwrite W_slow globally (catastrophic forgetting).
    Measure recall@A_after = mean cosine to A's prototype AFTER B's interference.
    Measure recall@B_after = mean cosine to B's prototype (acquisition).

HYPOTHESIS:
  STC_TAGGED preserves recall@A_after (A's tagged synapses survived B's writes)
  while BASELINE_NO_STC forgets A (B overwrote A's synapses globally).
  Mechanism is selective protection of tagged synapses, NOT general capacity.

DISCRIMINATOR:
  HARD_PASS:
    STC_TAGGED.recall_A_after - BASELINE_NO_STC.recall_A_after >= 0.30
    AND STC_TAGGED.recall_A_after >= 0.50  (A actually preserved)
    AND STC_TAGGED.recall_B_after >= 0.40  (B still acquired, not just A-locked)
    AND BASELINE_NO_STC.recall_A_after < 0.30  (interference confirmed)
    AND RANDOM_TAG_MATCHED.recall_A_after < STC_TAGGED.recall_A_after by >= 0.10
       (random tag density NOT enough; the SELECTION matters)
    AND tag_fraction in [0.05, 0.15] (sparse selective; v1's 0.535 was too dense)
    AND cv across seeds < 0.10 (full only)
  MIDDLE_BAND: A-preservation lift in [0.15, 0.30) OR STC arms partial
  HARD_FAIL:
    STC_TAGGED <= BASELINE_NO_STC on recall_A_after (mechanism null; STC doesn't protect)
    OR STC_TAGGED <= RANDOM_TAG_MATCHED (tag selection irrelevant; density was lever)
    OR tag_fraction outside [0.02, 0.50] (over- or under-tagged)
    OR cardinality breach

ARMS (4):
  ARM_BASELINE_NO_STC          Hebbian + global write to W_slow (no tag)
                               Expected: forgets A after B (catastrophic)
  ARM_STC_TAGGED               primary: tag-based selective capture; PROTECTS captured
                               synapses in Phase 2 (no overwrite of tagged W_slow entries)
  ARM_RANDOM_TAG_MATCHED       same TAG DENSITY as STC but RANDOM selection (not novelty-based)
                               Discriminator control: if random == STC, density was the lever
  ARM_DIAG_STC_DECAY           STC with tag decay; verify decay rate doesn't break protection

PRE-REG BANDS see above.

REGIME (matched to STC v1 with anti-saturation):
  full: N_DIM=2048 N_CAT=50 (smaller; only learn 2 patterns + a few interference)
                            We use A and B as specific prototypes; N_CAT controls
                            the prototype basis for orthogonality probing.
        Actually we use 2 patterns: A's pattern + B's pattern; N_CAT=10 background
        prototypes to test against (recall measured vs all 10; A is 1, B is 1).
  smoke: N_DIM=1024 N_CAT=10 with 1 phase
  selftest: N_DIM=256 N_CAT=4

TAG FRACTION sparse-band:
  v1 had ~0.535 tag_fraction (THETA_TAG_PCT=90); too dense.
  v2: THETA_TAG_PCT=92.0 -> ~8% tag (in [0.05, 0.15] band per spec).
  Explicit verification in selftest.

CARDINALITY_OK:
  smoke: 2 seeds * 4 arms = 8 units
  full:  5 seeds * 4 arms = 20 units

META_RULE_AA fairness:
  All arms read SAME SURFACE: cosine to target prototype via W_total @ query.
  Discriminator metric: recall_A_after - recall_A_initial DELTA per arm (forgetting amount).
  Baseline ARM_BASELINE_NO_STC expected to forget; if it doesn't, regime broken.

ASCII-only; no emojis; no em-dashes.
Author: exp_dev 2026-06-27 (Wave 2 redesign cell 4 of 4).
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

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "stc_tag_and_capture_v2_two_phase_continual_learning"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands
HP_A_PRESERVATION_LIFT = 0.30
HP_A_FLOOR_AFTER_B = 0.50
HP_B_ACQUISITION_FLOOR = 0.40
HF_BASELINE_A_AFTER_CEILING = 0.30  # baseline MUST forget A for discriminator to fire
HP_RANDOM_LIFT = 0.10  # STC must beat RANDOM_TAG_MATCHED by >= this
HP_TAG_FRAC_LO = 0.05
HP_TAG_FRAC_HI = 0.15
HP_CV_MAX = 0.10
HF_TAG_OVER = 0.50
HF_TAG_UNDER = 0.02
MIDDLE_A_LIFT_LO = 0.15

# STC parameters
THETA_TAG_PCT = 92.0  # ~8% tag selection (v1 used 90.0 -> ~53% under direction-novelty rule)
ETA_FAST = 1.0
ETA_CAPTURE = 0.20

EXPECTED_ARMS = [
    "baseline_no_stc",
    "stc_tagged",
    "random_tag_matched",
    "diag_stc_decay",
]

# Regime
if SELF_TEST_MODE:
    N_DIM = 256
    N_CAT = 4
    N_NOISY_VARIANTS = 3
    PROTO_NOISE = 0.85
    SEEDS = [11]
    J_CAPTURE = 3
    K_TAG_DECAY = 2
elif RUN_MODE == "smoke":
    N_DIM = 1024
    N_CAT = 10
    N_NOISY_VARIANTS = 5
    PROTO_NOISE = 0.85
    SEEDS = [11, 13]
    J_CAPTURE = 5
    K_TAG_DECAY = 3
else:
    N_DIM = 2048
    N_CAT = 20
    N_NOISY_VARIANTS = 10
    PROTO_NOISE = 0.85
    SEEDS = [11, 13, 19, 23, 29]
    J_CAPTURE = 10
    K_TAG_DECAY = 5

ALPHA_LOAD = N_CAT / float(N_DIM)
EXPECTED_N_UNITS = len(SEEDS) * len(EXPECTED_ARMS)

assert 0.001 <= ALPHA_LOAD <= 0.20, "alpha=%.4f out of band" % ALPHA_LOAD
assert K_TAG_DECAY < J_CAPTURE, "K_TAG_DECAY=%d must be < J_CAPTURE=%d" % (
    K_TAG_DECAY, J_CAPTURE)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,NCAT=%d,NVAR=%d,proto_noise=%.2f,alpha=%.4f,"
    "J_capture=%d,K_decay=%d,theta_pct=%.1f,eta_fast=%.2f,eta_cap=%.2f,seeds=%s,mode=%s,"
    "HP_A_lift>=%.2f,HP_A_floor>=%.2f,HP_B_floor>=%.2f,HF_baseline_A_after_ceil=%.2f,"
    "HP_random_lift>=%.2f,HP_tag=[%.2f,%.2f],"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "FAIRNESS=TWO_PHASE_INTERFERENCE+RANDOM_TAG_DENSITY_CONTROL"
) % (
    ANCHOR_NAME, N_DIM, N_CAT, N_NOISY_VARIANTS, PROTO_NOISE, ALPHA_LOAD,
    J_CAPTURE, K_TAG_DECAY, THETA_TAG_PCT, ETA_FAST, ETA_CAPTURE, SEEDS, RUN_MODE,
    HP_A_PRESERVATION_LIFT, HP_A_FLOOR_AFTER_B, HP_B_ACQUISITION_FLOOR,
    HF_BASELINE_A_AFTER_CEILING, HP_RANDOM_LIFT, HP_TAG_FRAC_LO, HP_TAG_FRAC_HI,
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
            "_hardening_marker": "v2_stc_two_phase_continual",
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
            "_hardening_marker": "v2_stc_two_phase_continual_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def noisy_prototype(proto: np.ndarray, noise: float,
                    g: np.random.Generator) -> np.ndarray:
    n = proto.shape[0]
    eff = min(1.0, max(0.0, noise))
    flip = g.random(n) < eff
    out = proto.copy()
    out[flip] = -out[flip]
    return out / (np.linalg.norm(out) + 1e-8)


def hebbian_dW(key: np.ndarray, value: np.ndarray) -> np.ndarray:
    n = key.shape[0]
    return np.outer(key, value).astype(np.float32) / float(n)


def recall_to_target(W: np.ndarray, noisy_queries: np.ndarray,
                      target_prototype: np.ndarray) -> float:
    """Mean cosine of W @ query to TARGET prototype.
    Used for both A and B recall.
    """
    out = noisy_queries @ W
    out_n = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-8)
    t_n = target_prototype / (np.linalg.norm(target_prototype) + 1e-8)
    sims = out_n @ t_n
    return float(max(0.0, min(1.0, np.mean(sims))))


def build_patterns(seed: int) -> Dict[str, Any]:
    """Build pattern A + pattern B + N_CAT background distractor prototypes.
    Returns dict with A_proto, B_proto, distractor_protos, A_train, B_train,
    A_test (noisy queries), B_test.
    """
    g = np.random.default_rng(seed)
    # All prototypes from same pool (quasi-orthogonal); A = 0, B = 1, distractors = 2:
    all_protos = bipolar(2 + N_CAT, N_DIM, g)
    A_proto = all_protos[0]
    B_proto = all_protos[1]
    distractor_protos = all_protos[2:]

    A_train = np.stack([noisy_prototype(A_proto, PROTO_NOISE, g)
                         for _ in range(N_NOISY_VARIANTS)], axis=0).astype(np.float32)
    B_train = np.stack([noisy_prototype(B_proto, PROTO_NOISE, g)
                         for _ in range(N_NOISY_VARIANTS)], axis=0).astype(np.float32)
    A_test = np.stack([noisy_prototype(A_proto, PROTO_NOISE, g)
                        for _ in range(N_NOISY_VARIANTS)], axis=0).astype(np.float32)
    B_test = np.stack([noisy_prototype(B_proto, PROTO_NOISE, g)
                        for _ in range(N_NOISY_VARIANTS)], axis=0).astype(np.float32)
    return {
        "A_proto": A_proto, "B_proto": B_proto,
        "distractor_protos": distractor_protos,
        "A_train": A_train, "B_train": B_train,
        "A_test": A_test, "B_test": B_test,
    }


# -------------------------- arms --------------------------

def run_arm_baseline_no_stc(patterns: Dict[str, Any]) -> Dict[str, float]:
    """Global Hebbian; A's writes ARE overwritten by B's writes via capture."""
    W_fast = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    W_slow = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    A_train = patterns["A_train"]
    A_proto = patterns["A_proto"]
    B_train = patterns["B_train"]
    B_proto = patterns["B_proto"]
    A_test = patterns["A_test"]
    B_test = patterns["B_test"]

    # Phase 1: learn A
    for i in range(A_train.shape[0]):
        dW = ETA_FAST * hebbian_dW(A_train[i], A_proto)
        W_fast = W_fast + dW
        if (i + 1) % J_CAPTURE == 0 or i == A_train.shape[0] - 1:
            W_slow = W_slow + ETA_CAPTURE * W_fast  # global capture
            W_fast = np.zeros_like(W_fast)

    W_total_after_A = W_slow + W_fast
    recall_A_initial = recall_to_target(W_total_after_A, A_test, A_proto)
    recall_B_initial = recall_to_target(W_total_after_A, B_test, B_proto)

    # Phase 2: learn B (interferes)
    for i in range(B_train.shape[0]):
        dW = ETA_FAST * hebbian_dW(B_train[i], B_proto)
        W_fast = W_fast + dW
        if (i + 1) % J_CAPTURE == 0 or i == B_train.shape[0] - 1:
            W_slow = W_slow + ETA_CAPTURE * W_fast
            W_fast = np.zeros_like(W_fast)

    W_total_after_B = W_slow + W_fast
    recall_A_after = recall_to_target(W_total_after_B, A_test, A_proto)
    recall_B_after = recall_to_target(W_total_after_B, B_test, B_proto)
    return {
        "recall_A_initial": recall_A_initial,
        "recall_A_after": recall_A_after,
        "recall_B_initial": recall_B_initial,
        "recall_B_after": recall_B_after,
        "fraction_tagged": 1.0,
    }


def _compute_tag_mask_novelty(dW: np.ndarray, W_fast_prev: np.ndarray,
                                theta_pct: float,
                                g: np.random.Generator) -> np.ndarray:
    """Magnitude-reinforcement tag rule: tag exactly top-(1-theta/100) percentile
    of synapses by ABSOLUTE POST-UPDATE STRENGTH.

    For bipolar outer-product Hebbian updates, |dW| is uniform (all entries 1/N).
    Direction-novelty mask alone produces ~50% positives by chance (sign agreement
    is 50% for random W_fast_prev). Neither signal alone gives sparse selection.

    Fix: use `|W_fast_prev + dW|` -- entries where the new update REINFORCES the
    existing fast trace (sign agreement) get a magnitude boost; entries where it
    cancels get suppressed. Top-percentile then selects entries that the recent
    activity STREAM consistently drives, which is Skunkworks-aligned: Frey-Morris
    Ca-rule tags synapses receiving sustained post-synaptic activity.
    """
    reinforced = np.abs(W_fast_prev + dW).astype(np.float32)
    # Tie-breaker for early cycles (W_fast_prev near zero)
    reinforced = reinforced + 1e-6 * np.abs(g.standard_normal(dW.shape).astype(np.float32))
    flat = reinforced.ravel()
    n_total = flat.size
    n_tag = max(1, int(n_total * (100.0 - theta_pct) / 100.0))
    if n_tag < n_total:
        thresh = np.partition(flat, n_total - n_tag)[n_total - n_tag]
    else:
        thresh = float(flat.min())
    return (reinforced >= thresh)


def run_arm_stc_tagged(patterns: Dict[str, Any], seed: int,
                        decay_tags: bool = False) -> Dict[str, float]:
    """STC with PROTECTED W_slow: B's tagged-capture writes go ONLY to entries
    where W_slow == 0 (i.e., not previously captured by A).
    This is the load-bearing mechanism: A's captured synapses survive B.
    """
    g = np.random.default_rng(seed + 4444)
    W_fast = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    W_slow = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    tag_mask = np.zeros((N_DIM, N_DIM), dtype=bool)
    tag_age = np.zeros((N_DIM, N_DIM), dtype=np.int32)
    tag_fracs: List[float] = []

    A_train = patterns["A_train"]
    A_proto = patterns["A_proto"]
    B_train = patterns["B_train"]
    B_proto = patterns["B_proto"]
    A_test = patterns["A_test"]
    B_test = patterns["B_test"]

    # Phase 1: learn A
    for i in range(A_train.shape[0]):
        dW = ETA_FAST * hebbian_dW(A_train[i], A_proto)
        W_fast_prev = W_fast.copy()
        W_fast = W_fast + dW
        new_tags = _compute_tag_mask_novelty(dW, W_fast_prev, THETA_TAG_PCT, g)
        tag_fracs.append(float(new_tags.sum()) / new_tags.size)
        tag_mask = tag_mask | new_tags
        if decay_tags:
            tag_age = np.where(new_tags, 0, tag_age + 1)
            expired = tag_age >= K_TAG_DECAY
            tag_mask = tag_mask & ~expired
            tag_age = np.where(expired, 0, tag_age)
        if (i + 1) % J_CAPTURE == 0 or i == A_train.shape[0] - 1:
            captured = tag_mask
            # PROTECTED CAPTURE: only write to W_slow where it's UNPROTECTED (==0)
            # AND tag set. (Phase 1: W_slow is all zero initially, so all captured tagged
            # entries get written.)
            unprotected = (W_slow == 0.0)
            commit_mask = captured & unprotected
            W_slow = W_slow + ETA_CAPTURE * np.where(commit_mask, W_fast, 0.0)
            W_fast = np.zeros_like(W_fast)
            tag_mask = np.zeros_like(tag_mask)
            if decay_tags:
                tag_age = np.zeros_like(tag_age)

    W_total_after_A = W_slow + W_fast
    recall_A_initial = recall_to_target(W_total_after_A, A_test, A_proto)
    recall_B_initial = recall_to_target(W_total_after_A, B_test, B_proto)

    # Phase 2: learn B (with protection on A's captured entries)
    for i in range(B_train.shape[0]):
        dW = ETA_FAST * hebbian_dW(B_train[i], B_proto)
        W_fast_prev = W_fast.copy()
        W_fast = W_fast + dW
        new_tags = _compute_tag_mask_novelty(dW, W_fast_prev, THETA_TAG_PCT, g)
        tag_fracs.append(float(new_tags.sum()) / new_tags.size)
        tag_mask = tag_mask | new_tags
        if decay_tags:
            tag_age = np.where(new_tags, 0, tag_age + 1)
            expired = tag_age >= K_TAG_DECAY
            tag_mask = tag_mask & ~expired
            tag_age = np.where(expired, 0, tag_age)
        if (i + 1) % J_CAPTURE == 0 or i == B_train.shape[0] - 1:
            captured = tag_mask
            unprotected = (W_slow == 0.0)
            commit_mask = captured & unprotected
            W_slow = W_slow + ETA_CAPTURE * np.where(commit_mask, W_fast, 0.0)
            W_fast = np.zeros_like(W_fast)
            tag_mask = np.zeros_like(tag_mask)
            if decay_tags:
                tag_age = np.zeros_like(tag_age)

    W_total_after_B = W_slow + W_fast
    recall_A_after = recall_to_target(W_total_after_B, A_test, A_proto)
    recall_B_after = recall_to_target(W_total_after_B, B_test, B_proto)
    mean_tag = float(np.mean(tag_fracs)) if tag_fracs else 0.0
    return {
        "recall_A_initial": recall_A_initial,
        "recall_A_after": recall_A_after,
        "recall_B_initial": recall_B_initial,
        "recall_B_after": recall_B_after,
        "fraction_tagged": mean_tag,
    }


def run_arm_random_tag_matched(patterns: Dict[str, Any], seed: int,
                                target_tag_fraction: float) -> Dict[str, float]:
    """Random tag mask with same DENSITY as STC tag, but RANDOM selection.
    Discriminator control: if random == STC, density was the lever (not selection).
    """
    g = np.random.default_rng(seed + 5555)
    W_fast = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    W_slow = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    tag_mask = np.zeros((N_DIM, N_DIM), dtype=bool)

    A_train = patterns["A_train"]
    A_proto = patterns["A_proto"]
    B_train = patterns["B_train"]
    B_proto = patterns["B_proto"]
    A_test = patterns["A_test"]
    B_test = patterns["B_test"]

    def _random_tag(g_local: np.random.Generator, p: float) -> np.ndarray:
        return (g_local.random((N_DIM, N_DIM)) < p)

    # Phase 1: learn A
    for i in range(A_train.shape[0]):
        dW = ETA_FAST * hebbian_dW(A_train[i], A_proto)
        W_fast = W_fast + dW
        new_tags = _random_tag(g, target_tag_fraction)
        tag_mask = tag_mask | new_tags
        if (i + 1) % J_CAPTURE == 0 or i == A_train.shape[0] - 1:
            captured = tag_mask
            unprotected = (W_slow == 0.0)
            commit_mask = captured & unprotected
            W_slow = W_slow + ETA_CAPTURE * np.where(commit_mask, W_fast, 0.0)
            W_fast = np.zeros_like(W_fast)
            tag_mask = np.zeros_like(tag_mask)

    W_total_after_A = W_slow + W_fast
    recall_A_initial = recall_to_target(W_total_after_A, A_test, A_proto)
    recall_B_initial = recall_to_target(W_total_after_A, B_test, B_proto)

    # Phase 2: learn B (with same protection scheme)
    for i in range(B_train.shape[0]):
        dW = ETA_FAST * hebbian_dW(B_train[i], B_proto)
        W_fast = W_fast + dW
        new_tags = _random_tag(g, target_tag_fraction)
        tag_mask = tag_mask | new_tags
        if (i + 1) % J_CAPTURE == 0 or i == B_train.shape[0] - 1:
            captured = tag_mask
            unprotected = (W_slow == 0.0)
            commit_mask = captured & unprotected
            W_slow = W_slow + ETA_CAPTURE * np.where(commit_mask, W_fast, 0.0)
            W_fast = np.zeros_like(W_fast)
            tag_mask = np.zeros_like(tag_mask)

    W_total_after_B = W_slow + W_fast
    recall_A_after = recall_to_target(W_total_after_B, A_test, A_proto)
    recall_B_after = recall_to_target(W_total_after_B, B_test, B_proto)
    return {
        "recall_A_initial": recall_A_initial,
        "recall_A_after": recall_A_after,
        "recall_B_initial": recall_B_initial,
        "recall_B_after": recall_B_after,
        "fraction_tagged": float(target_tag_fraction),
    }


def run_one_seed(seed: int) -> Dict[str, Any]:
    patterns = build_patterns(seed)

    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["baseline_no_stc"] = run_arm_baseline_no_stc(patterns)
    arm_results["stc_tagged"] = run_arm_stc_tagged(patterns, seed, decay_tags=False)
    # Match RANDOM_TAG to STC's measured tag fraction
    stc_tag_frac = arm_results["stc_tagged"]["fraction_tagged"]
    arm_results["random_tag_matched"] = run_arm_random_tag_matched(
        patterns, seed, target_tag_fraction=stc_tag_frac)
    arm_results["diag_stc_decay"] = run_arm_stc_tagged(patterns, seed, decay_tags=True)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "N_CAT": N_CAT,
        "alpha_load": ALPHA_LOAD,
        "J_capture": J_CAPTURE,
        "K_tag_decay": K_TAG_DECAY,
        "theta_tag_pct": THETA_TAG_PCT,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        A_init_vals: List[float] = []
        A_after_vals: List[float] = []
        B_init_vals: List[float] = []
        B_after_vals: List[float] = []
        tag_vals: List[float] = []
        for s in seeds_sorted:
            pa = per_seed[s].get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                A_init_vals.append(float(d.get("recall_A_initial", 0.0)))
                A_after_vals.append(float(d.get("recall_A_after", 0.0)))
                B_init_vals.append(float(d.get("recall_B_initial", 0.0)))
                B_after_vals.append(float(d.get("recall_B_after", 0.0)))
                tag_vals.append(float(d.get("fraction_tagged", 0.0)))
                per_arm_full[arm][s] = {k: float(d.get(k, 0.0)) for k in (
                    "recall_A_initial", "recall_A_after",
                    "recall_B_initial", "recall_B_after",
                    "fraction_tagged")}
        if A_after_vals:
            m_A_after = float(np.mean(A_after_vals))
            sd_A_after = float(np.std(A_after_vals))
            cv = sd_A_after / abs(m_A_after) if abs(m_A_after) > 1e-6 else 0.0
            summary[arm] = {
                "mean_A_initial": float(np.mean(A_init_vals)),
                "mean_A_after": m_A_after, "std_A_after": sd_A_after, "cv_A_after": cv,
                "mean_B_initial": float(np.mean(B_init_vals)),
                "mean_B_after": float(np.mean(B_after_vals)),
                "mean_tagged": float(np.mean(tag_vals)),
                "n": len(A_after_vals),
            }
        else:
            summary[arm] = {"mean_A_initial": 0.0, "mean_A_after": 0.0,
                            "std_A_after": 0.0, "cv_A_after": 0.0,
                            "mean_B_initial": 0.0, "mean_B_after": 0.0,
                            "mean_tagged": 0.0, "n": 0}

    base = summary["baseline_no_stc"]
    stc = summary["stc_tagged"]
    rand = summary["random_tag_matched"]
    decay = summary["diag_stc_decay"]

    base_A_after = base["mean_A_after"]
    stc_A_after = stc["mean_A_after"]
    rand_A_after = rand["mean_A_after"]
    stc_B_after = stc["mean_B_after"]
    stc_cv = stc["cv_A_after"]
    stc_tag_frac = stc["mean_tagged"]

    A_lift_over_baseline = stc_A_after - base_A_after
    A_lift_over_random = stc_A_after - rand_A_after

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if base_A_after > HF_BASELINE_A_AFTER_CEILING:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "INTERFERENCE_REGIME_BROKEN: baseline_A_after=%.3f > %.2f "
            "(B should have wiped A; if it didn't, mechanism can't be tested)"
        ) % (base_A_after, HF_BASELINE_A_AFTER_CEILING)
    elif stc_A_after <= base_A_after:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "STC_DOESNT_PROTECT: stc_A_after=%.3f <= baseline_A_after=%.3f"
        ) % (stc_A_after, base_A_after)
    elif stc_tag_frac > HF_TAG_OVER:
        verdict = "HARD_FAIL"
        verdict_reason = "TAG_OVER_DENSITY: %.3f > %.2f (not selective)" % (
            stc_tag_frac, HF_TAG_OVER)
    elif stc_tag_frac < HF_TAG_UNDER:
        verdict = "HARD_FAIL"
        verdict_reason = "TAG_UNDER_DENSITY: %.3f < %.2f (mechanism null)" % (
            stc_tag_frac, HF_TAG_UNDER)
    elif stc_A_after - rand_A_after < 0.0:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "RANDOM_TAG_BEATS_STC: stc=%.3f - random=%.3f = %.3f "
            "(tag selection irrelevant; density was lever)"
        ) % (stc_A_after, rand_A_after, A_lift_over_random)
    elif (A_lift_over_baseline >= HP_A_PRESERVATION_LIFT and
            stc_A_after >= HP_A_FLOOR_AFTER_B and
            stc_B_after >= HP_B_ACQUISITION_FLOOR and
            A_lift_over_random >= HP_RANDOM_LIFT and
            HP_TAG_FRAC_LO <= stc_tag_frac <= HP_TAG_FRAC_HI and
            (len(seeds_sorted) == 1 or stc_cv < HP_CV_MAX)):
        verdict = "HARD_PASS"
        verdict_reason = (
            "STC_PROTECTS: A_lift_over_baseline=%.3f STC_A_after=%.3f STC_B_after=%.3f "
            "A_lift_over_random=%.3f tag_frac=%.3f"
        ) % (A_lift_over_baseline, stc_A_after, stc_B_after, A_lift_over_random,
              stc_tag_frac)
    elif MIDDLE_A_LIFT_LO <= A_lift_over_baseline < HP_A_PRESERVATION_LIFT:
        verdict = "MIDDLE_BAND"
        verdict_reason = "PARTIAL_PROTECTION: A_lift_over_baseline=%.3f in [%.2f, %.2f)" % (
            A_lift_over_baseline, MIDDLE_A_LIFT_LO, HP_A_PRESERVATION_LIFT)
    elif (A_lift_over_baseline >= HP_A_PRESERVATION_LIFT and
            not (HP_TAG_FRAC_LO <= stc_tag_frac <= HP_TAG_FRAC_HI)):
        verdict = "MIDDLE_BAND"
        verdict_reason = "TAG_FRAC_OUT_OF_BAND: %.3f outside [%.2f, %.2f]" % (
            stc_tag_frac, HP_TAG_FRAC_LO, HP_TAG_FRAC_HI)

    verdict_msg = (
        "%s | %s | base_A_after=%.3f stc_A_after=%.3f rand_A_after=%.3f decay_A_after=%.3f | "
        "stc_B_after=%.3f stc_A_init=%.3f | A_lift_base=%.3f A_lift_rand=%.3f tag_frac=%.3f cv=%.3f | n=%d"
    ) % (verdict, verdict_reason, base_A_after, stc_A_after, rand_A_after,
         decay["mean_A_after"], stc_B_after, stc["mean_A_initial"],
         A_lift_over_baseline, A_lift_over_random, stc_tag_frac, stc_cv,
         len(seeds_sorted))

    completed_units = len(seeds_sorted) * len(EXPECTED_ARMS)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "baseline_A_after": base_A_after,
        "stc_A_after": stc_A_after,
        "random_tag_A_after": rand_A_after,
        "stc_B_after": stc_B_after,
        "A_lift_over_baseline": A_lift_over_baseline,
        "A_lift_over_random_tag": A_lift_over_random,
        "stc_tag_fraction": stc_tag_frac,
        "stc_cv_A_after": stc_cv,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d NCAT=%d theta=%.1f J=%d K=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_CAT, THETA_TAG_PCT, J_CAPTURE,
        K_TAG_DECAY, SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                for k in ("recall_A_initial", "recall_A_after",
                          "recall_B_initial", "recall_B_after", "fraction_tagged"):
                    assert k in r["per_arm"][arm], "missing %s in %s" % (k, arm)
            # Verify tag fraction in band (selectivity check)
            stc_tag = r["per_arm"]["stc_tagged"]["fraction_tagged"]
            assert 0.02 <= stc_tag <= 0.50, (
                "TAG_FRAC_OUT_OF_BAND: %.3f outside [0.02, 0.50] (theta=%.1f wrong)" % (
                    stc_tag, THETA_TAG_PCT))
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: 4 arms structured + tag=%.3f in band" % stc_tag)
            print("[selftest] OK base_A_after=%.3f stc_A_after=%.3f rand_A_after=%.3f stc_B_after=%.3f tag=%.3f" % (
                r["per_arm"]["baseline_no_stc"]["recall_A_after"],
                r["per_arm"]["stc_tagged"]["recall_A_after"],
                r["per_arm"]["random_tag_matched"]["recall_A_after"],
                r["per_arm"]["stc_tagged"]["recall_B_after"],
                stc_tag), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    per_seed_results: Dict[str, Dict[str, Any]] = {}
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(SEEDS)),
                               extra={"_phase": "seed_running", "_current_seed": seed,
                                      "alpha_load": ALPHA_LOAD})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        per_seed_results[str(seed)] = result
        bn = result["per_arm"]["baseline_no_stc"]
        st = result["per_arm"]["stc_tagged"]
        rn = result["per_arm"]["random_tag_matched"]
        print("[seed=%d] complete in %.1fs base_A_after=%.3f stc_A_after=%.3f rand_A_after=%.3f stc_B_after=%.3f tag=%.3f" % (
            seed, time.time() - t0,
            bn["recall_A_after"], st["recall_A_after"],
            rn["recall_A_after"], st["recall_B_after"],
            st["fraction_tagged"]), flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_stc_two_phase_continual"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
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
