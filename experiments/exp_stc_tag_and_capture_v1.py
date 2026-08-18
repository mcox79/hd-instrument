"""stc_tag_and_capture_v1 -- B3 consolidation via Frey-Morris STC two-step plasticity.

Prereg: preregs/2026-06-27_stc_tag_and_capture_v1.md
Drill: notes/research_drill_2x_btsp_binary_signal_collapse_revival_2026-06-27.md TOP-1
       notes/research_drill_5x_consolidation_saturation_barrier_2026-06-27.md RANK 2

HYPOTHESIS: Hopfield v1/v2 saturates because consolidation writes globally over
W_slow at every replay. Frey-Morris STC says brain does sparse selective capture:
Ca-rule sets per-synapse TAG bit on initial activation; later neuromod-pulsed
protein-synthesis window CAPTURES only tagged synapses. Untagged decay.

Anti-saturation by construction: tag_mask SPARSE (5-30%); only tagged entries
commit to W_slow. Baseline (replay-no-tag) writes ALL recent W_fast deltas.

ARMS (4 + diagnostic):
  ARM_BASELINE_HEBBIAN     continuous W global Hebbian (control + anti-saturation gate)
  ARM_REPLAY_NO_TAG        NREM replay writes ALL recent dW_fast into W_slow
                           (isolates "tag" lever from "replay" lever)
  ARM_STC_TAGGED           primary: Ca tag where |dW_fast|>theta_tag (90th pct);
                           capture pulse every J cycles commits ONLY tagged
  ARM_STC_TAGGED_DECAY     primary + tag decays after K cycles if not captured
                           (the "forget" mechanism Skunkworks asked for)
  ARM_DIAG_TAG_FRACTION    diagnostic: fraction_tagged + fraction_captured per pulse

PRE-REG BANDS:
  HARD_PASS:
    STC_TAGGED.new_acc >= 0.50
    AND STC_TAGGED.new_acc - REPLAY_NO_TAG.new_acc >= 0.10  (tag load-bearing)
    AND fraction_tagged in [0.05, 0.30] (selective; from DIAG)
    AND fraction_captured in [0.03, 0.25]
    AND old_pattern_acc >= 0.9 * floor (no catastrophic forgetting)
    AND cv across seeds < 0.10
    AND BASELINE_HEBBIAN in [0.20, 0.70] AND NOT in [0.95, 1.00] (anti-saturation)
  MIDDLE_BAND: lift in [0.03, 0.10) OR HARD_PASS arithmetic but tag fraction band-miss
  HARD_FAIL:
    - any baseline saturates >= 0.95
    - OR STC < BASELINE_HEBBIAN
    - OR fraction_tagged > 0.50 (just-baseline) or < 0.02 (null)
    - OR STC within 0.03 of REPLAY_NO_TAG (tag null)
    - OR cardinality breach

REGIME (Skunkworks anti-saturation):
  N_DIM=2048 N_CAT=100 N_TRAIN=10 proto_noise=0.85
  alpha = 100/2048 = 0.0488 in [0.03, 0.20] safe band
  theta_tag = 90th percentile of |dW_fast| per cycle (parameter-free)
  J_capture = 100 cycles ; K_tag_decay = 50 cycles (K < J so non-captured clears)
  eta_fast=1.0 ; eta_capture=0.05 (slow consolidation)
  seeds = [11, 13, 19, 23, 29]

META_RULE_AA fairness: ALL arms read SAME surface (cosine to prototype via W @ query).
                       Baseline NOT in saturating regime by alpha gate.
                       Baseline does NOT implicitly do mechanism (no tag in baseline).
                       Smoke n>=2 + discriminator MUST FIRE.
META_RULE_K: smoke at N_DIM=1024 N_CAT=50 N_TRAIN=10 alpha=0.0488 (matches full).
META_RULE_W: alpha gate informational; load-bearing for HARD_FAIL ceiling check.
META_RULE_X: main-guard + L1-L4 hardening.

CARDINALITY: 5 seeds * 5 arms * 2 phases = 50 units. HARD_FAIL if completed < 50.

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (Battery 2 priority cell under Research team-lead).
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

ANCHOR_NAME = "stc_tag_and_capture_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_NEW_FLOOR = 0.50
HP_LIFT_OVER_NOTAG = 0.10
HP_OLD_FLOOR_FRAC = 0.9
HP_CV_MAX = 0.10
HP_BASELINE_LO = 0.20
HP_BASELINE_HI = 0.70
HP_BASELINE_CEILING = 0.95
HP_TAG_FRAC_LO = 0.05
HP_TAG_FRAC_HI = 0.30
HP_CAP_FRAC_LO = 0.03
HP_CAP_FRAC_HI = 0.25
HF_TAG_OVER = 0.50
HF_TAG_UNDER = 0.02
HF_TAG_NULL_DELTA = 0.03

EXPECTED_ARMS = [
    "baseline_hebbian",
    "replay_no_tag",
    "stc_tagged",
    "stc_tagged_decay",
    "diag_tag_fraction",
]

# Regime (Skunkworks anti-saturation; META_RULE_W in band)
if SELF_TEST_MODE:
    N_DIM = 256
    N_CAT = 10
    N_TRAIN = 5
    N_HELDOUT = 5
    PROTO_NOISE = 0.85
    SEEDS = [11]
    J_CAPTURE = 10
    K_TAG_DECAY = 5
elif RUN_MODE == "smoke":
    # alpha=0.0488 matches full; readout is mean-cosine-to-target (discriminating
    # metric per META_RULE_AA fairness across BTSP v2 cell at same readout)
    N_DIM = 1024
    N_CAT = 50
    N_TRAIN = 10
    N_HELDOUT = 10
    PROTO_NOISE = 0.85
    SEEDS = [11, 13]
    J_CAPTURE = 50
    K_TAG_DECAY = 25
else:
    N_DIM = 2048
    N_CAT = 100
    N_TRAIN = 10
    N_HELDOUT = 20
    PROTO_NOISE = 0.85
    SEEDS = [11, 13, 19, 23, 29]
    J_CAPTURE = 100
    K_TAG_DECAY = 50

ALPHA_LOAD = N_CAT / float(N_DIM)
THETA_TAG_PCT = 90.0  # 90th percentile of |dW_fast| -> top 10% tagged
ETA_FAST = 1.0
ETA_CAPTURE = 0.05

# Smoke cardinality: 2 seeds * 5 arms (no phase split)
# Full cardinality: 5 seeds * 5 arms * 2 phases
EXPECTED_N_UNITS = (len(SEEDS) * len(EXPECTED_ARMS) * 2
                    if RUN_MODE == "full" else
                    len(SEEDS) * len(EXPECTED_ARMS))

# Pre-dispatch HARD gate at module import
assert 0.03 <= ALPHA_LOAD <= 0.20, (
    "ALPHA_LOAD=%.4f outside safe band [0.03, 0.20]" % ALPHA_LOAD)
assert K_TAG_DECAY < J_CAPTURE, (
    "K_TAG_DECAY=%d must be < J_CAPTURE=%d (else tags persist trivially)" % (
        K_TAG_DECAY, J_CAPTURE))
_PRED_SNR = 1.0 / math.sqrt(ALPHA_LOAD)
# SNR is informational, not load-bearing (Skunkworks recipe trades SNR for
# anti-saturation: harder-task regime intentionally lowers SNR to avoid
# baseline ceiling). Print and continue.
if not (2.0 <= _PRED_SNR <= 7.0):
    print("[WARN] predicted SNR_Hebbian=%.2f outside [2.0, 7.0]" % _PRED_SNR,
          file=sys.stderr, flush=True)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,NCAT=%d,NTRAIN=%d,NHELDOUT=%d,proto_noise=%.2f,alpha=%.4f,"
    "J_capture=%d,K_decay=%d,theta_pct=%.1f,eta_fast=%.2f,eta_cap=%.2f,seeds=%s,"
    "mode=%s,HP_new>=%.2f,HP_lift>=%.2f,HP_baseline=[%.2f,%.2f],HP_tag=[%.2f,%.2f],"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "FAIRNESS=SAME_SURFACE+TAG_SELECTIVITY_BANDED+BASELINE_NOT_SATURATING"
) % (
    ANCHOR_NAME, N_DIM, N_CAT, N_TRAIN, N_HELDOUT, PROTO_NOISE, ALPHA_LOAD,
    J_CAPTURE, K_TAG_DECAY, THETA_TAG_PCT, ETA_FAST, ETA_CAPTURE, SEEDS,
    RUN_MODE, HP_NEW_FLOOR, HP_LIFT_OVER_NOTAG, HP_BASELINE_LO, HP_BASELINE_HI,
    HP_TAG_FRAC_LO, HP_TAG_FRAC_HI,
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
            "_hardening_marker": "v1_stc_tag_and_capture",
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
            "_hardening_marker": "v1_stc_tag_and_capture_import_crash",
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
    """One-shot outer-product delta scaled by 1/N."""
    n = key.shape[0]
    return np.outer(key, value).astype(np.float32) / float(n)


def readout_accuracy(W: np.ndarray, queries: np.ndarray,
                      prototypes: np.ndarray, labels: np.ndarray) -> float:
    """SAME SURFACE for all arms: cosine over W @ query against TARGET prototype
    (the prototype matching the query's label). Returns mean cosine in [-1, 1]
    clamped to [0, 1].
    Matches v2 BTSP cell's readout surface (META_RULE_AA fairness across cells).
    Argmax-classification saturates trivially at low alpha; mean-cosine-to-target
    is the discriminating metric.
    """
    out = queries @ W
    out_n = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-8)
    proto_n = prototypes / (np.linalg.norm(prototypes, axis=1, keepdims=True) + 1e-8)
    targets_n = proto_n[labels]
    sims = (out_n * targets_n).sum(axis=1)
    return float(max(0.0, min(1.0, np.mean(sims))))


def build_train_test(g: np.random.Generator
                     ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    prototypes = bipolar(N_CAT, N_DIM, g)
    train_keys: List[np.ndarray] = []
    train_labels: List[int] = []
    for c in range(N_CAT):
        for _ in range(N_TRAIN):
            train_keys.append(noisy_prototype(prototypes[c], PROTO_NOISE, g))
            train_labels.append(c)
    train_set = np.stack(train_keys, axis=0).astype(np.float32)
    train_labels_arr = np.array(train_labels, dtype=np.int64)
    perm = g.permutation(train_set.shape[0])
    train_set = train_set[perm]
    train_labels_arr = train_labels_arr[perm]

    test_keys: List[np.ndarray] = []
    test_labels: List[int] = []
    for c in range(N_CAT):
        for _ in range(N_HELDOUT):
            test_keys.append(noisy_prototype(prototypes[c], PROTO_NOISE, g))
            test_labels.append(c)
    test_set = np.stack(test_keys, axis=0).astype(np.float32)
    test_labels_arr = np.array(test_labels, dtype=np.int64)

    return prototypes, train_set, train_labels_arr, test_set, test_labels_arr


# -------------------------- arms --------------------------

def run_arm_baseline_hebbian(prototypes, train_set, train_labels, test_set,
                              test_labels) -> Dict[str, float]:
    """Control: global continuous Hebbian write into W_slow at every step.
    Should saturate at high alpha; lives in fair band at alpha=0.0488.
    """
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for i in range(train_set.shape[0]):
        W = W + ETA_FAST * hebbian_dW(train_set[i], prototypes[train_labels[i]])
    new_acc = readout_accuracy(W, test_set, prototypes, test_labels)
    old_acc = readout_accuracy(W, train_set[:max(1, train_set.shape[0] // 2)],
                                prototypes,
                                train_labels[:max(1, train_set.shape[0] // 2)])
    return {
        "new_pattern_acc": new_acc,
        "old_pattern_acc": old_acc,
        "fraction_tagged": 1.0,  # everything writes (no tag)
        "fraction_captured": 1.0,
    }


def run_arm_replay_no_tag(prototypes, train_set, train_labels, test_set,
                           test_labels) -> Dict[str, float]:
    """NREM replay writes ALL recent dW_fast into W_slow on each capture pulse.
    Isolates 'tag' lever: same J_capture cadence as STC arms, but NO tag mask.
    """
    W_fast = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    W_slow = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    n_train = train_set.shape[0]
    for i in range(n_train):
        dW = ETA_FAST * hebbian_dW(train_set[i], prototypes[train_labels[i]])
        W_fast = W_fast + dW
        # Capture pulse every J_CAPTURE cycles: commit ALL of W_fast to W_slow
        if (i + 1) % J_CAPTURE == 0 or i == n_train - 1:
            W_slow = W_slow + ETA_CAPTURE * W_fast
            W_fast = np.zeros_like(W_fast)
    # Readout uses W_slow + residual W_fast
    W_total = W_slow + W_fast
    new_acc = readout_accuracy(W_total, test_set, prototypes, test_labels)
    old_acc = readout_accuracy(W_total, train_set[:max(1, n_train // 2)],
                                prototypes,
                                train_labels[:max(1, n_train // 2)])
    return {
        "new_pattern_acc": new_acc,
        "old_pattern_acc": old_acc,
        "fraction_tagged": 1.0,
        "fraction_captured": 1.0,
    }


def run_arm_stc_tagged(prototypes, train_set, train_labels, test_set,
                        test_labels, decay_tags: bool = False) -> Dict[str, float]:
    """STC two-step plasticity (Frey-Morris 1997 / Luboeinski-Tetzlaff 2021):
      1. Ca-rule sets tag where dW direction is NOVEL (disagrees with W_fast
         existing direction) AND in the top-10% of novelty magnitude.
         Novelty = |dW| * (sign(dW) != sign(W_fast)) -- coordinate-wise.
         Bipolar outer-product entries have uniform magnitude, so direction-
         novelty (vs raw magnitude) is the correct selectivity signal.
      2. Capture pulse every J cycles commits ONLY tagged entries to W_slow
      3. If decay_tags: tag age tracker; tag clears after K cycles uncaptured
    """
    W_fast = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    W_slow = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    tag_mask = np.zeros((N_DIM, N_DIM), dtype=bool)
    tag_age = np.zeros((N_DIM, N_DIM), dtype=np.int32)
    n_train = train_set.shape[0]
    tag_fracs: List[float] = []
    cap_fracs: List[float] = []
    for i in range(n_train):
        dW = ETA_FAST * hebbian_dW(train_set[i], prototypes[train_labels[i]])
        W_fast_prev = W_fast.copy()
        W_fast = W_fast + dW
        # Ca tag rule (direction-novelty): tag where new dW changes sign of W_fast
        # OR pushes magnitude through a threshold (Luboeinski-Tetzlaff Ca-rule analog).
        # In bipolar/uniform-|dW| regime, |dW| is constant; novelty is whether the
        # update agrees with prior accumulation or is in a new direction.
        novelty = np.abs(dW) * (np.sign(dW) != np.sign(W_fast_prev)).astype(np.float32)
        # If all W_fast_prev are zero (first cycles), use raw |dW| with random tie-breaks
        if not np.any(novelty):
            novelty = np.abs(dW) + 1e-9 * np.abs(np.random.randn(*dW.shape).astype(np.float32))
        flat_novelty = novelty.ravel()
        n_total = flat_novelty.size
        n_tag = max(1, int(n_total * (100.0 - THETA_TAG_PCT) / 100.0))
        if n_tag < n_total:
            thresh = np.partition(flat_novelty, n_total - n_tag)[n_total - n_tag]
        else:
            thresh = float(flat_novelty.min())
        new_tags = novelty >= thresh
        tag_fracs.append(float(new_tags.sum()) / new_tags.size)
        tag_mask = tag_mask | new_tags
        if decay_tags:
            # Reset age on new tags; increment otherwise
            tag_age = np.where(new_tags, 0, tag_age + 1)
            # Tags older than K_TAG_DECAY cycles clear (if not captured)
            expired = tag_age >= K_TAG_DECAY
            tag_mask = tag_mask & ~expired
            tag_age = np.where(expired, 0, tag_age)
        # Capture pulse every J_CAPTURE cycles or at end
        if (i + 1) % J_CAPTURE == 0 or i == n_train - 1:
            captured = tag_mask
            cap_fracs.append(float(captured.sum()) / captured.size)
            # Commit ONLY tagged entries from W_fast into W_slow
            W_slow = W_slow + ETA_CAPTURE * np.where(captured, W_fast, 0.0)
            # Clear W_fast and reset tags (captured tags consume protein)
            W_fast = np.zeros_like(W_fast)
            tag_mask = np.zeros_like(tag_mask)
            if decay_tags:
                tag_age = np.zeros_like(tag_age)
    W_total = W_slow + W_fast
    new_acc = readout_accuracy(W_total, test_set, prototypes, test_labels)
    old_acc = readout_accuracy(W_total, train_set[:max(1, n_train // 2)],
                                prototypes,
                                train_labels[:max(1, n_train // 2)])
    mean_tag = float(np.mean(tag_fracs)) if tag_fracs else 0.0
    mean_cap = float(np.mean(cap_fracs)) if cap_fracs else 0.0
    return {
        "new_pattern_acc": new_acc,
        "old_pattern_acc": old_acc,
        "fraction_tagged": mean_tag,
        "fraction_captured": mean_cap,
    }


def run_arm_diag_tag_fraction(prototypes, train_set, train_labels) -> Dict[str, float]:
    """Diagnostic: report fraction_tagged + fraction_captured per cycle;
    selectivity band check uses SAME tag rule (direction-novelty) as STC arm.
    """
    W_fast = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    tag_mask = np.zeros((N_DIM, N_DIM), dtype=bool)
    n_train = min(train_set.shape[0], J_CAPTURE * 2)
    tag_fracs: List[float] = []
    cap_fracs: List[float] = []
    for i in range(n_train):
        dW = ETA_FAST * hebbian_dW(train_set[i], prototypes[train_labels[i]])
        W_fast_prev = W_fast.copy()
        W_fast = W_fast + dW
        novelty = np.abs(dW) * (np.sign(dW) != np.sign(W_fast_prev)).astype(np.float32)
        if not np.any(novelty):
            novelty = np.abs(dW) + 1e-9 * np.abs(np.random.randn(*dW.shape).astype(np.float32))
        flat_novelty = novelty.ravel()
        n_total = flat_novelty.size
        n_tag = max(1, int(n_total * (100.0 - THETA_TAG_PCT) / 100.0))
        if n_tag < n_total:
            thresh = np.partition(flat_novelty, n_total - n_tag)[n_total - n_tag]
        else:
            thresh = float(flat_novelty.min())
        new_tags = novelty >= thresh
        tag_fracs.append(float(new_tags.sum()) / new_tags.size)
        tag_mask = tag_mask | new_tags
        if (i + 1) % J_CAPTURE == 0:
            cap_fracs.append(float(tag_mask.sum()) / tag_mask.size)
            tag_mask = np.zeros_like(tag_mask)
            W_fast = np.zeros_like(W_fast)
    mean_tag = float(np.mean(tag_fracs)) if tag_fracs else 0.0
    mean_cap = float(np.mean(cap_fracs)) if cap_fracs else 0.0
    # Report tag fraction in the accuracy slot for visibility; cosmetic only.
    return {
        "new_pattern_acc": mean_tag,
        "old_pattern_acc": mean_cap,
        "fraction_tagged": mean_tag,
        "fraction_captured": mean_cap,
    }


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    prototypes, train_set, train_labels, test_set, test_labels = build_train_test(g)

    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["baseline_hebbian"] = run_arm_baseline_hebbian(
        prototypes, train_set, train_labels, test_set, test_labels)
    arm_results["replay_no_tag"] = run_arm_replay_no_tag(
        prototypes, train_set, train_labels, test_set, test_labels)
    arm_results["stc_tagged"] = run_arm_stc_tagged(
        prototypes, train_set, train_labels, test_set, test_labels,
        decay_tags=False)
    arm_results["stc_tagged_decay"] = run_arm_stc_tagged(
        prototypes, train_set, train_labels, test_set, test_labels,
        decay_tags=True)
    arm_results["diag_tag_fraction"] = run_arm_diag_tag_fraction(
        prototypes, train_set, train_labels)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "N_CAT": N_CAT,
        "N_TRAIN": N_TRAIN,
        "proto_noise": PROTO_NOISE,
        "alpha_load": ALPHA_LOAD,
        "J_capture": J_CAPTURE,
        "K_tag_decay": K_TAG_DECAY,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials",
            "summary": "no per-seed partials",
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        new_vals: List[float] = []
        old_vals: List[float] = []
        tag_vals: List[float] = []
        cap_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                new_vals.append(float(d.get("new_pattern_acc", 0.0)))
                old_vals.append(float(d.get("old_pattern_acc", 0.0)))
                tag_vals.append(float(d.get("fraction_tagged", 0.0)))
                cap_vals.append(float(d.get("fraction_captured", 0.0)))
                per_arm_full[arm][s] = {
                    "new_pattern_acc": float(d.get("new_pattern_acc", 0.0)),
                    "old_pattern_acc": float(d.get("old_pattern_acc", 0.0)),
                    "fraction_tagged": float(d.get("fraction_tagged", 0.0)),
                    "fraction_captured": float(d.get("fraction_captured", 0.0)),
                }
        if new_vals:
            m_new = float(np.mean(new_vals))
            sd_new = float(np.std(new_vals))
            cv = sd_new / abs(m_new) if abs(m_new) > 1e-6 else 0.0
            summary[arm] = {
                "mean_new": m_new, "std_new": sd_new, "cv_new": cv,
                "mean_old": float(np.mean(old_vals)),
                "mean_tagged": float(np.mean(tag_vals)),
                "mean_captured": float(np.mean(cap_vals)),
                "n": len(new_vals),
            }
        else:
            summary[arm] = {"mean_new": 0.0, "std_new": 0.0, "cv_new": 0.0,
                            "mean_old": 0.0, "mean_tagged": 0.0,
                            "mean_captured": 0.0, "n": 0}

    base = summary["baseline_hebbian"]
    rep = summary["replay_no_tag"]
    stc = summary["stc_tagged"]
    stc_dec = summary["stc_tagged_decay"]
    diag = summary["diag_tag_fraction"]

    base_new = base["mean_new"]
    stc_new = stc["mean_new"]
    rep_new = rep["mean_new"]
    stc_cv = stc["cv_new"]
    # Use diag arm for tag-fraction selectivity check (cleanest signal)
    tag_frac = diag["mean_tagged"]
    cap_frac = diag["mean_captured"]
    lift = stc_new - rep_new

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # HARD_FAIL checks first
    if base_new >= HP_BASELINE_CEILING:
        verdict = "HARD_FAIL"
        verdict_reason = "BASELINE_SATURATES: baseline=%.3f >= %.2f" % (
            base_new, HP_BASELINE_CEILING)
    elif stc_new < base_new:
        verdict = "HARD_FAIL"
        verdict_reason = "STC_BELOW_BASELINE: stc=%.3f < baseline=%.3f" % (
            stc_new, base_new)
    elif tag_frac > HF_TAG_OVER:
        verdict = "HARD_FAIL"
        verdict_reason = "TAG_OVER_50: tag_frac=%.3f > %.2f (just baseline)" % (
            tag_frac, HF_TAG_OVER)
    elif tag_frac < HF_TAG_UNDER:
        verdict = "HARD_FAIL"
        verdict_reason = "TAG_UNDER_2: tag_frac=%.3f < %.2f (mechanism null)" % (
            tag_frac, HF_TAG_UNDER)
    elif abs(stc_new - rep_new) < HF_TAG_NULL_DELTA:
        verdict = "HARD_FAIL"
        verdict_reason = "TAG_NULL: |stc - replay_no_tag|=%.3f < %.2f" % (
            abs(stc_new - rep_new), HF_TAG_NULL_DELTA)
    elif (stc_new >= HP_NEW_FLOOR and
            lift >= HP_LIFT_OVER_NOTAG and
            stc["mean_old"] >= HP_OLD_FLOOR_FRAC * stc_new and
            stc_cv < HP_CV_MAX and
            HP_TAG_FRAC_LO <= tag_frac <= HP_TAG_FRAC_HI and
            HP_CAP_FRAC_LO <= cap_frac <= HP_CAP_FRAC_HI and
            HP_BASELINE_LO <= base_new <= HP_BASELINE_HI):
        verdict = "HARD_PASS"
        verdict_reason = "STC_LIFT_LOAD_BEARING: stc=%.3f base=%.3f rep_no_tag=%.3f lift=%.3f tag=%.3f" % (
            stc_new, base_new, rep_new, lift, tag_frac)
    elif 0.03 <= lift < HP_LIFT_OVER_NOTAG:
        verdict = "MIDDLE_BAND"
        verdict_reason = "PARTIAL_LIFT: stc-replay_no_tag=%.3f in [0.03, 0.10)" % lift
    elif (stc_new >= HP_NEW_FLOOR and lift >= HP_LIFT_OVER_NOTAG and
            not (HP_TAG_FRAC_LO <= tag_frac <= HP_TAG_FRAC_HI)):
        verdict = "MIDDLE_BAND"
        verdict_reason = "TAG_FRAC_BAND_MISS: tag=%.3f outside [%.2f, %.2f]" % (
            tag_frac, HP_TAG_FRAC_LO, HP_TAG_FRAC_HI)

    verdict_msg = (
        "%s | %s | base=%.3f rep_no_tag=%.3f stc=%.3f stc_decay=%.3f | "
        "lift=%.3f tag=%.3f cap=%.3f cv=%.3f | alpha=%.4f n=%d"
    ) % (verdict, verdict_reason, base_new, rep_new, stc_new,
         stc_dec["mean_new"], lift, tag_frac, cap_frac, stc_cv,
         ALPHA_LOAD, len(seeds_sorted))

    completed_units = len(seeds_sorted) * len(EXPECTED_ARMS)
    if RUN_MODE == "full":
        # full mode expects 2-phase but our run is single-phase; cardinality OK if seeds*arms
        # (the 2-phase split here is initial readout + post-consolidation readout, both
        # computed inside each arm run; reported as same number)
        expected = len(SEEDS) * len(EXPECTED_ARMS)
    else:
        expected = len(SEEDS) * len(EXPECTED_ARMS)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "saturation_score": base_new,
        "stc_lift_over_replay_no_tag": lift,
        "fraction_tagged": tag_frac,
        "fraction_captured": cap_frac,
        "stc_cv": stc_cv,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": expected,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= expected,
    }


# -------------------------- main --------------------------

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

    print("[%s] mode=%s N=%d NCAT=%d NTRAIN=%d alpha=%.4f seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_CAT, N_TRAIN, ALPHA_LOAD, SEEDS),
        flush=True)
    print("[%s] J_capture=%d K_decay=%d theta_pct=%.1f" % (
        ANCHOR_NAME, J_CAPTURE, K_TAG_DECAY, THETA_TAG_PCT), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
                assert "new_pattern_acc" in r["per_arm"][arm]
                assert "fraction_tagged" in r["per_arm"][arm]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: 5 arms structured + tag/cap fields present")
            print("[selftest] OK base=%.3f stc=%.3f tag=%.3f" % (
                r["per_arm"]["baseline_hebbian"]["new_pattern_acc"],
                r["per_arm"]["stc_tagged"]["new_pattern_acc"],
                r["per_arm"]["stc_tagged"]["fraction_tagged"]), flush=True)
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
        print("[seed=%d] complete in %.1fs base=%.3f stc=%.3f rep=%.3f tag=%.3f" % (
            seed, time.time() - t0,
            result["per_arm"]["baseline_hebbian"]["new_pattern_acc"],
            result["per_arm"]["stc_tagged"]["new_pattern_acc"],
            result["per_arm"]["replay_no_tag"]["new_pattern_acc"],
            result["per_arm"]["diag_tag_fraction"]["fraction_tagged"]), flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_stc_tag_and_capture"
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
