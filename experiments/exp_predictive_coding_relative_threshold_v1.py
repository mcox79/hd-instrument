"""
predictive_coding_relative_threshold_v1 -- EST-style RELATIVE (self-referential)
event-boundary flag vs the current ABSOLUTE threshold_gate.

MOTIVATION (Research hand-off notes/exp_dev_handoff_research_brain_script_
acquisition_consolidation_2026-08-09.md, anchor 2; parent research note
notes/research_brain_script_acquisition_consolidation_2026-08-09.md section 1):
  The currently-wired FLAG teacher (hdlab.consequence_learning_loop.teacher_
  verdict(signal_mode="signal_a_only")) is isolated verb-lemma MET/UNMET
  polarity -- no notion of a recurring event-type, no self-relative surprise
  computation. Two independent literatures (Event Segmentation Theory's
  computational model, Reynolds/Zacks/Braver 2007; statistical event-structure
  learning, Baldwin et al. 2008 / Stahl et al. 2014) converge on a RELATIVE
  (current-error-vs-own-recent-baseline) prediction-error signal as the brain-
  faithful FLAG, not a fixed absolute threshold. hdlab/predictive_coding.py's
  existing threshold_gate is absolute (compares residual_magnitude(t) against
  a fixed constant in [0, 1]).

  This cell is BUILDING that brain-faithful signal, not claiming the substrate
  already owns it: the brain-fidelity audit rated the EST principle PRINCIPLE-
  FOUNDATIONAL but the currently-wired flag a DEVIATION. hdlab.predictive_
  coding.relative_threshold_gate (added this session) is the new function;
  this cell is its A/B proof, isolated from the schema-grain question (anchor
  3 in the hand-off) per the project's own one-variable-at-a-time design gate.

HYPOTHESIS (PRE-REG, must answer in verdict):
  Reynolds/Zacks/Braver 2007's own motivation for a self-referential (ratio-
  to-own-recent-baseline) comparison, rather than a fixed absolute constant,
  is CONTEXT-DEPENDENT noise: different stretches of experience carry
  different intrinsic prediction-error levels (a fixed threshold that is
  well-calibrated in a "quiet" context either misses boundaries in a noisier
  context, or false-alarms constantly once applied to it). The cell tests
  this directly with a HETEROSCEDASTIC corpus: alternating blocks of events
  with a LOW sensory-noise level (p_flip=0, the ideal case) and a MODERATE
  sensory-noise level (p_flip=P_NOISY, corrupting a fraction of the observed
  value's bits before it is compared to the substrate's prediction -- the
  underlying key/value association written into memory is always the TRUE,
  uncorrupted pair; only the CURRENT observation being compared against the
  prediction is corrupted, per block). A single FIXED absolute threshold must
  compromise across both noise regimes; a RATIO-to-running-average tracks
  each regime's own local baseline. The cell measures whether this predicted
  advantage is REAL on a labeled synthetic corpus, not assumed -- exploratory
  corpus-design iteration (multiple candidate drift mechanisms: monotonic
  Hebbian-crosstalk-only drift, a single clean/noisy split, several block
  sizes/decay constants) consistently found the ABSOLUTE gate matching or
  beating the RELATIVE gate on this substrate's bounded [0, ~0.5]
  cosine-residual measure (residual saturates near "chance" ~0.5 for any
  fully-uncorrelated comparison, so the "boundary spike" is a near-fixed
  ceiling rather than something that itself scales multiplicatively with
  context noise -- and dividing by a single noisy point-estimate running mean
  amplifies per-step noise as much as it corrects for genuine drift, at
  moderate corruption levels). The FINAL corpus/decay below is the best-
  faith, non-cherry-picked design from that exploration (not selected to
  force a particular verdict) -- see verdict_msg for the measured outcome.

CORPUS (labeled-boundary; exp_dev's construction, see build_event_stream):
  EVENTS distinct single-item "scenes", each contributing ONE BRAND-NEW
  bipolar (key, value) pair, cycled REPEATS_PER_EVENT times (a stable
  feature persisting across repeated observations within a scene, matching
  the literal Zacks movie-segmentation paradigm more directly than a multi-
  item "script" would -- ITEMS_PER_EVENT=1 also removes a labeling confound
  an earlier multi-item draft had: with >1 item per event, the 2nd/3rd item's
  own first appearance is equally "novel" as the 1st item's, but only the
  1st item's step was labeled boundary=1, corrupting precision for BOTH
  gates identically and telling us nothing about the relative-vs-absolute
  question). A boundary label=1 marks the FIRST step of every event except
  event 0 (a genuine never-seen-before pattern shift, with no prior event to
  transition FROM); label=0 everywhere else (within-event repeats).

  Events are grouped into BLOCK-sized runs; each block is uniformly LOW-
  noise (p_flip=0) or MODERATE-noise (p_flip=P_NOISY), alternating block to
  block (see _noise_schedule). The underlying memory W accumulates the TRUE
  (key, value) pair every step via vanilla_hebbian_write, UNCONDITIONAL on
  either gate -- both gates are evaluated against the IDENTICAL W trajectory
  and the IDENTICAL (noise-corrupted) observation stream in a single online
  pass, isolating PURELY the gate-comparison logic from any write-policy
  confound.

MANDATORY PRE-CHECK (hand-off contract, verbatim): confirm residual_magnitude
  itself discriminates a synthetic coherent-repeat sequence from a scrambled/
  shuffled control FIRST. Operationalized here (see
  _selftest_residual_discriminates_coherent_vs_scrambled): "coherent" = the
  SAME (key, value) pair shown repeatedly into an initially-empty W (should
  become highly predictable, residual -> ~0 after the first exposure);
  "scrambled" = a BRAND-NEW random (key, value) pair every single step (never
  repeats, nothing to learn, residual stays at chance ~0.5 throughout). This
  mirrors the analogous coherent/scrambled invariant test already applied to
  schema_consistency_split_half in hdlab/grounding_acquisition_loop.py::
  self_test, one layer down (raw residual measurement, not the schema gate).
  A flat/negative downstream F1 result is treated as a HARNESS BUG (verdict
  PRECHECK_FAIL_HARNESS_BUG), never as a mechanism negative, unless this
  pre-check passes first. NOTE: this pre-check uses the plain (noise-free)
  predict/residual_magnitude path -- it validates the base measurement
  instrument, independent of the block-noise corpus used for the F1 question.

PRE-REGISTERED HARD BANDS (from the hand-off, verbatim; not exp_dev's to
loosen):
  HARD_PASS: relative-threshold boundary/flag F1 >= 0.75 against the known
    labeled boundaries (mean across seeds) AND not worse than the absolute
    threshold_gate's own F1 by more than 0.05 F1 in the worst-case seed
    (min over seeds of (rel_f1 - abs_f1) >= -0.05).
  HARD_FAIL: relative-threshold F1 (mean across seeds) < 0.50 -- ONLY after
    the mandatory pre-check above passes.
  MIDDLE_BAND: everything else (0.50 <= rel_f1_mean < 0.75, OR rel_f1_mean
    >= 0.75 but the worst-case margin condition fails).
  PRECHECK_FAIL_HARNESS_BUG: the mandatory pre-check itself fails -- refuses
    to interpret any F1 number below as a mechanism verdict.

Both gates are evaluated via a threshold SWEEP (grid fixed a priori, NOT
tuned post-hoc to the observed corpus draw -- calibration_check =
"default_ok_for_this_regime"), reporting each gate's own BEST achievable F1
on the identical eval stream -- the fairest possible "matched task" reading
of the hand-off's F1-comparison bands (both gates get an equally generous
sweep).

A RANDOM_FLAG_CONTROL (uniform random prediction at the TRUE base rate) is
also reported (NOT part of the HARD-PASS/FAIL gate -- pure telemetry) so the
report can sanity-check that a given F1 is a non-trivial bar given class
imbalance.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF; hash-test on the boolean
    prediction arrays of ABS vs REL gates on the first seed)
  - final_metrics_atomicity: tmp_replace (via experiments._seed_checkpoint.
    write_metrics)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: this is a binary boundary-detection F1 cell, not an argmax/
    top-k associative-recall capacity cell; no CRLB/capacity-feasibility
    ceiling applies.
  - baseline_in_band at smoke (META_RULE_AG; 0.05 < ABS_GATE best F1 < 0.95)
  - discriminator survives scale: smoke uses FULL-N corpus parameters (option
    A of DISCRIMINATOR-MUST-SURVIVE-SCALE), only n_seeds is reduced (1 vs 5)
  - HARD_PASS strictly above floor + 5% band-width (META_RULE_L): the 0.75
    HARD_PASS bar and 0.50 HARD_FAIL floor come verbatim from the hand-off's
    pre-registered bands (not loosened)
  - HP_SCOPE: REL_GATE carries both HARD_PASS conditions; ABS_GATE is the
    comparison baseline (no HP gate of its own)
  - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS) (single sweep axis = seed)
  - per-unit failure-class instrumentation (META_RULE_J; no bare except)
  - calibration_check: default_ok_for_this_regime (fixed a priori grids,
    span near-degenerate to near-never-fire for both gates symmetrically;
    corpus noise level P_NOISY and block size fixed a priori from the
    exploration documented above, not tuned per-seed)
  - all numbers in this docstring are THEORETICAL/CITED framing, not
    MEASURED -- MEASURED numbers appear only in the verdict_msg /
    metrics.json this script itself writes (META_RULE_AC)

ASCII-only; no unicode; no emojis.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
    write_metrics, record_gate, assert_discriminator_fires,
)

# ---------------------------------------------------------------------------
# Predictive-coding primitives (inlined verbatim -- keeps the cell
# self-contained on the remote runner without requiring a separate
# hdlab/predictive_coding.py SCP; matches exp_pc1_predictive_coding_
# residual_gate_v1's precedent). Canonical copy: hdlab/predictive_coding.py.
# ---------------------------------------------------------------------------
from dataclasses import dataclass
from typing import Optional


def predict(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Substrate's current bipolar prediction for value bound to key."""
    raw = W @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def residual_magnitude(observed: np.ndarray, predicted: np.ndarray) -> float:
    """Normalized mismatch fraction in [0, 1] (0=perfect, 1=opposite)."""
    obs = observed.ravel()
    pred = predicted.ravel()
    n = obs.shape[0]
    if n == 0:
        return 0.0
    obs_n = float(np.linalg.norm(obs))
    pred_n = float(np.linalg.norm(pred))
    if obs_n <= 1e-12 or pred_n <= 1e-12:
        return 1.0
    cos = float(np.dot(obs, pred)) / (obs_n * pred_n)
    cos = max(-1.0, min(1.0, cos))
    return 0.5 * (1.0 - cos)


def vanilla_hebbian_write(W: np.ndarray, key: np.ndarray, value: np.ndarray) -> np.ndarray:
    W += np.outer(value, key)
    return W


@dataclass(frozen=True)
class WriteDecision:
    write_strength: float
    residual_mag: float
    skipped: bool
    reason: str


def threshold_gate(observed: np.ndarray, predicted: np.ndarray, *,
                   threshold: float) -> WriteDecision:
    """ABSOLUTE gate (the CURRENT signal this cell tests the relative gate
    against): fires iff residual_magnitude >= a fixed constant."""
    mag = residual_magnitude(observed, predicted)
    fires = mag >= threshold
    return WriteDecision(1.0 if fires else 0.0, mag, not fires,
                         f"mag={mag:.3f} {'>=' if fires else '<'} {threshold}")


def running_avg_update(prev_avg: Optional[float], new_value: float, *,
                       decay: float = 0.05) -> float:
    """0.05-weighted low-pass filter (Reynolds/Zacks/Braver 2007 Eq. 8)."""
    if prev_avg is None:
        return float(new_value)
    return float(decay * new_value + (1.0 - decay) * prev_avg)


@dataclass(frozen=True)
class BoundaryDecision:
    is_boundary: bool
    residual_mag: float
    running_avg: float
    ratio: float
    reason: str


def relative_threshold_gate(observed: np.ndarray, predicted: np.ndarray, *,
                            running_avg_prev: Optional[float],
                            threshold: float) -> BoundaryDecision:
    """RELATIVE (self-referential) gate: fires iff residual_magnitude /
    running_avg_prev >= threshold. This is the mechanism under test."""
    mag = residual_magnitude(observed, predicted)
    if running_avg_prev is None or running_avg_prev <= 1e-9:
        return BoundaryDecision(False, mag, float(running_avg_prev or 0.0),
                                float("inf") if mag > 1e-9 else 0.0, "warmup")
    ratio = mag / running_avg_prev
    fires = ratio >= threshold
    return BoundaryDecision(fires, mag, float(running_avg_prev), float(ratio),
                            f"ratio={ratio:.3f}")


ANCHOR_NAME = "predictive_coding_relative_threshold_v1"

# ---------------------------------------------------------------------------
# Substrate-only decode audit (Skunkworks structural blocker): this module
# imports no LLM / transformer / huggingface modules; counter stays 0 by
# structural guarantee, logged for auditability.
# ---------------------------------------------------------------------------
_LLM_CALL_COUNTER = [0]

# ---------------------------------------------------------------------------
# CLI / run mode
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# ---------------------------------------------------------------------------
# Corpus / gate constants (exp_dev autonomy per hand-off contract: exact
# running-average decay + threshold sweep + corpus construction are mine).
# DISCRIMINATOR-MUST-SURVIVE-SCALE option A: smoke uses the SAME N/EVENTS/
# REPEATS_PER_EVENT/BLOCK/P_NOISY as FULL (only n_seeds shrinks 5 -> 1); this
# cell is cheap enough (N=256, 300 steps/seed) that there is no reason to run
# a smaller, potentially-non-discriminating smoke regime.
# ---------------------------------------------------------------------------
N_DIM = 256
EVENTS = 60
REPEATS_PER_EVENT = 5
BLOCK_EVENTS = 15            # events per noise-block (block length in steps
                              # = 75, >> 1/DECAY=20 so the running average has
                              # time to settle within a block, not just react
                              # to the transient right after a switch)
P_NOISY = 0.35                # moderate corruption of the OBSERVED value's
                              # bits in "noisy" blocks (fraction of bits
                              # flipped); chosen well short of the 0.5
                              # (fully-uncorrelated) degenerate ceiling where
                              # the task becomes unsolvable for ANY method
DECAY = 0.05                  # literature-pinned (Reynolds/Zacks/Braver 2007
                              # Eq. 8); exp_dev's default choice (exploration
                              # also tried 0.10/0.15/0.20/0.30 -- see
                              # docstring HYPOTHESIS section; none reversed
                              # the qualitative finding)

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7]
SEEDS = SEEDS_SMOKE if RUN_MODE == "smoke" else SEEDS_FULL

# Threshold sweeps fixed a priori (calibration_check=default_ok_for_this_regime):
# ABS grid spans the full [0,1] residual_magnitude range at fine granularity;
# REL grid spans ratio=1.05 (barely above baseline, near-always-fires) up to
# ratio=10 (only a huge spike fires) -- both symmetric "near-degenerate to
# near-never-fire" coverage, neither tuned to this specific corpus draw.
THRESH_ABS_GRID = [round(0.02 + 0.02 * i, 3) for i in range(30)]   # 0.02..0.60
THRESH_REL_GRID = [1.05, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0,
                   2.2, 2.5, 2.8, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0]

TOTAL_STEPS = EVENTS * REPEATS_PER_EVENT
CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},EVENTS={EVENTS},"
    f"REPEATS_PER_EVENT={REPEATS_PER_EVENT},BLOCK_EVENTS={BLOCK_EVENTS},"
    f"P_NOISY={P_NOISY},TOTAL_STEPS={TOTAL_STEPS},DECAY={DECAY},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE}"
)


def _noise_schedule(event_idx: int) -> float:
    """p_flip for the given event index -- alternating LOW/MODERATE-noise
    blocks of BLOCK_EVENTS events each (block 0 = clean, block 1 = noisy,
    block 2 = clean, ...)."""
    return P_NOISY if (event_idx // BLOCK_EVENTS) % 2 == 1 else 0.0


# ---------------------------------------------------------------------------
# Corpus construction (labeled event-boundary stream, heteroscedastic noise)
# ---------------------------------------------------------------------------
def build_event_stream(seed: int, n_dim: int, n_events: int,
                       repeats_per_event: int, noise_schedule
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Synthetic sequential stream with EST-style event structure PLUS
    heteroscedastic per-block observation noise.

    Each event contributes ONE brand-new bipolar (key, value) pair, cycled
    repeats_per_event times (a stable feature persisting across a "scene").
    boundary_label=1 at the first step of every event except event 0; label=0
    everywhere else. noise_schedule(event_idx) -> p_flip in [0, 1]: the
    fraction of the OBSERVED value's bits independently flipped before it is
    compared to the prediction (the memory itself always consolidates the
    TRUE, uncorrupted value -- see values_true vs values_obs).

    Deterministic per-seed (np.random.RandomState -- no built-in hash(),
    PROT-023/F.5 compliant).

    Returns (keys[T,N], values_true[T,N], values_obs[T,N],
    boundary_labels[T] int64) where T = n_events * repeats_per_event.
    """
    rng = np.random.RandomState(seed)
    keys: List[np.ndarray] = []
    values_true: List[np.ndarray] = []
    values_obs: List[np.ndarray] = []
    labels: List[int] = []
    for e in range(n_events):
        key = rng.choice([-1.0, 1.0], size=n_dim).astype(np.float64)
        val = rng.choice([-1.0, 1.0], size=n_dim).astype(np.float64)
        p_flip = float(noise_schedule(e))
        for r in range(repeats_per_event):
            keys.append(key)
            values_true.append(val)
            flip_mask = rng.random(n_dim) < p_flip
            val_obs = val.copy()
            val_obs[flip_mask] *= -1.0
            values_obs.append(val_obs)
            labels.append(1 if (e > 0 and r == 0) else 0)
    return (np.stack(keys), np.stack(values_true), np.stack(values_obs),
           np.array(labels, dtype=np.int64))


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def f1_precision_recall(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, float, float]:
    """Binary F1/precision/recall (no sklearn dependency)."""
    y_true = np.asarray(y_true).astype(bool)
    y_pred = np.asarray(y_pred).astype(bool)
    tp = int(np.sum(y_true & y_pred))
    fp = int(np.sum(~y_true & y_pred))
    fn = int(np.sum(y_true & ~y_pred))
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return float(f1), float(precision), float(recall)


def sweep_best_f1(scores: np.ndarray, labels: np.ndarray, grid: List[float]
                  ) -> Tuple[float, float, float, float, Dict[str, List[float]]]:
    """Return (best_f1, best_threshold, best_precision, best_recall, all_f1s).

    all_f1s is {"grid": grid, "f1": [f1 per grid point]} for post-hoc
    discriminating-band auditing (gate B style).
    """
    f1s = []
    best = (-1.0, grid[0], 0.0, 0.0)
    for t in grid:
        pred = scores >= t
        f1, p, r = f1_precision_recall(labels, pred)
        f1s.append(f1)
        if f1 > best[0]:
            best = (f1, t, p, r)
    return best[0], best[1], best[2], best[3], {"grid": list(grid), "f1": f1s}


# ---------------------------------------------------------------------------
# MANDATORY PRE-CHECK (hand-off contract): residual_magnitude must
# discriminate a coherent-repeat sequence from a scrambled control BEFORE any
# downstream HARD-FAIL is accepted as a mechanism negative.
# ---------------------------------------------------------------------------
def _selftest_residual_discriminates_coherent_vs_scrambled() -> Dict:
    """Coherent (same pair repeated -> learnable, residual -> ~0) vs
    scrambled (brand-new random pair EVERY step -> never learnable, residual
    stays ~0.5 chance) using the exact predict/residual_magnitude/
    vanilla_hebbian_write primitives this cell's boundary detectors run on.
    Uses the plain noise-free path -- validates the base measurement
    instrument, independent of the block-noise corpus used downstream.
    """
    rng = np.random.RandomState(12345)
    n_t = 128
    r_count = 12

    key_c = rng.choice([-1.0, 1.0], size=n_t).astype(np.float64)
    val_c = rng.choice([-1.0, 1.0], size=n_t).astype(np.float64)
    W_c = np.zeros((n_t, n_t), dtype=np.float64)
    coherent_residuals = []
    for _ in range(r_count):
        pred = predict(W_c, key_c)
        coherent_residuals.append(residual_magnitude(val_c, pred))
        vanilla_hebbian_write(W_c, key_c, val_c)
    coherent_late_mean = float(np.mean(coherent_residuals[2:]))

    W_s = np.zeros((n_t, n_t), dtype=np.float64)
    scrambled_residuals = []
    for _ in range(r_count):
        key_s = rng.choice([-1.0, 1.0], size=n_t).astype(np.float64)
        val_s = rng.choice([-1.0, 1.0], size=n_t).astype(np.float64)
        pred = predict(W_s, key_s)
        scrambled_residuals.append(residual_magnitude(val_s, pred))
        vanilla_hebbian_write(W_s, key_s, val_s)
    scrambled_late_mean = float(np.mean(scrambled_residuals[2:]))

    gap = scrambled_late_mean - coherent_late_mean
    passed = bool(coherent_late_mean < 0.15 and scrambled_late_mean > 0.35 and gap > 0.20)
    return {
        "precheck_passed": passed,
        "coherent_late_mean_residual": coherent_late_mean,
        "scrambled_late_mean_residual": scrambled_late_mean,
        "gap": gap,
        "coherent_residuals": [float(x) for x in coherent_residuals],
        "scrambled_residuals": [float(x) for x in scrambled_residuals],
    }


# ---------------------------------------------------------------------------
# Other self-tests
# ---------------------------------------------------------------------------
def _selftest_gates_agree_on_trivial_cases():
    obs = np.ones(16)
    pred_same = np.ones(16)
    pred_opp = -np.ones(16)
    dec_abs_no = threshold_gate(obs, pred_same, threshold=0.3)
    assert dec_abs_no.skipped, "abs gate must not fire on perfect prediction"
    dec_abs_yes = threshold_gate(obs, pred_opp, threshold=0.3)
    assert not dec_abs_yes.skipped, "abs gate must fire on total mismatch"
    dec_rel_no = relative_threshold_gate(obs, pred_same, running_avg_prev=0.2, threshold=2.0)
    assert not dec_rel_no.is_boundary, "rel gate must not fire on perfect prediction"
    dec_rel_yes = relative_threshold_gate(obs, pred_opp, running_avg_prev=0.1, threshold=2.0)
    assert dec_rel_yes.is_boundary, "rel gate must fire when mag/baseline >> threshold"
    return True


def _selftest_corpus_shape_and_labels():
    keys, v_true, v_obs, labels = build_event_stream(
        0, 32, n_events=5, repeats_per_event=3, noise_schedule=lambda e: 0.0)
    expected_total = 5 * 3
    assert keys.shape == (expected_total, 32), f"keys shape {keys.shape}"
    assert v_true.shape == (expected_total, 32), f"values_true shape {v_true.shape}"
    assert v_obs.shape == (expected_total, 32), f"values_obs shape {v_obs.shape}"
    assert labels.shape == (expected_total,), f"labels shape {labels.shape}"
    assert int(labels.sum()) == 4, f"expected 4 boundaries (events 1..4), got {labels.sum()}"
    assert labels[0] == 0, "event 0 first step is not a boundary"
    assert labels[3] == 1, "event 1's first step (index 3) must be a boundary"
    # p_flip=0 everywhere -> values_obs must equal values_true exactly.
    assert np.array_equal(v_true, v_obs), "p_flip=0 schedule must leave values unchanged"
    return True


def _selftest_noise_schedule_flips_bits():
    keys, v_true, v_obs, labels = build_event_stream(
        0, 64, n_events=4, repeats_per_event=6, noise_schedule=lambda e: 1.0)
    # p_flip=1.0 -> every bit flipped -> values_obs == -values_true exactly.
    assert np.array_equal(v_obs, -v_true), "p_flip=1.0 must flip every bit"
    return True


def _selftest_f1_sanity():
    y_true = np.array([0, 0, 1, 0, 1, 0, 0, 1])
    y_pred_perfect = y_true.copy()
    f1, p, r = f1_precision_recall(y_true, y_pred_perfect)
    assert abs(f1 - 1.0) < 1e-9, f"perfect prediction F1={f1}"
    y_pred_none = np.zeros_like(y_true)
    f1b, _, _ = f1_precision_recall(y_true, y_pred_none)
    assert f1b == 0.0, f"never-fire F1={f1b}"
    return True


def _instrumentation_selftest():
    _selftest_gates_agree_on_trivial_cases()
    _selftest_corpus_shape_and_labels()
    _selftest_noise_schedule_flips_bits()
    _selftest_f1_sanity()
    precheck = _selftest_residual_discriminates_coherent_vs_scrambled()
    print(
        f"[selftest] PASS  precheck_passed={precheck['precheck_passed']}  "
        f"coherent_late={precheck['coherent_late_mean_residual']:.3f}  "
        f"scrambled_late={precheck['scrambled_late_mean_residual']:.3f}  "
        f"gap={precheck['gap']:.3f}  N={N_DIM}  EVENTS={EVENTS}  mode={RUN_MODE}",
        flush=True,
    )
    return precheck


_PRECHECK_RESULT = _instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner: SINGLE online pass shared by both gates (isolates PURELY
# the gate-comparison logic -- identical W trajectory / residual trace).
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    keys, v_true, v_obs, labels = build_event_stream(
        seed, N_DIM, EVENTS, REPEATS_PER_EVENT, _noise_schedule)
    T = keys.shape[0]
    W = np.zeros((N_DIM, N_DIM), dtype=np.float64)

    # t=0: seed the running average, write, no eval (label[0] is always 0 by
    # construction -- excluded from the eval range for BOTH gates so the
    # comparison stays apples-to-apples).
    pred0 = predict(W, keys[0])
    mag0 = residual_magnitude(v_obs[0], pred0)
    running_avg = running_avg_update(None, mag0, decay=DECAY)
    vanilla_hebbian_write(W, keys[0], v_true[0])

    eval_mags = np.zeros(T - 1, dtype=np.float64)
    eval_ratios = np.zeros(T - 1, dtype=np.float64)
    eval_labels = labels[1:].copy()

    for t in range(1, T):
        pred = predict(W, keys[t])
        mag = residual_magnitude(v_obs[t], pred)
        ratio = mag / running_avg if running_avg > 1e-9 else float("inf")
        eval_mags[t - 1] = mag
        eval_ratios[t - 1] = ratio
        running_avg = running_avg_update(running_avg, mag, decay=DECAY)
        vanilla_hebbian_write(W, keys[t], v_true[t])

    abs_best_f1, abs_best_t, abs_best_p, abs_best_r, abs_all = sweep_best_f1(
        eval_mags, eval_labels, THRESH_ABS_GRID)
    rel_best_f1, rel_best_t, rel_best_p, rel_best_r, rel_all = sweep_best_f1(
        eval_ratios, eval_labels, THRESH_REL_GRID)

    # Telemetry-only RANDOM_FLAG_CONTROL at the true base rate (NOT part of
    # the HARD-PASS/FAIL gate).
    base_rate = float(eval_labels.sum()) / float(len(eval_labels))
    rng_rnd = np.random.RandomState(seed + 9001)
    rnd_pred = rng_rnd.random(len(eval_labels)) < base_rate
    rnd_f1, rnd_p, rnd_r = f1_precision_recall(eval_labels, rnd_pred)

    # META_RULE_AF arms-must-differ: hash the two boolean prediction arrays
    # at each gate's OWN best threshold.
    abs_pred_bits = (eval_mags >= abs_best_t)
    rel_pred_bits = (eval_ratios >= rel_best_t)
    digest_abs = hashlib.sha256(abs_pred_bits.tobytes()).hexdigest()
    digest_rel = hashlib.sha256(rel_pred_bits.tobytes()).hexdigest()
    arms_differ = digest_abs != digest_rel

    elapsed = time.time() - t0
    print(
        f"  [seed={seed}] T={T} boundaries={int(eval_labels.sum())} "
        f"base_rate={base_rate:.3f}  "
        f"ABS: f1={abs_best_f1:.3f}@t={abs_best_t:.3f}(p={abs_best_p:.3f},r={abs_best_r:.3f})  "
        f"REL: f1={rel_best_f1:.3f}@t={rel_best_t:.2f}(p={rel_best_p:.3f},r={rel_best_r:.3f})  "
        f"RND: f1={rnd_f1:.3f}  arms_differ={arms_differ}  elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "T": int(T),
        "n_boundaries": int(eval_labels.sum()),
        "base_rate": base_rate,
        "abs_gate": {
            "best_f1": abs_best_f1, "best_threshold": abs_best_t,
            "best_precision": abs_best_p, "best_recall": abs_best_r,
            "sweep": abs_all,
        },
        "rel_gate": {
            "best_f1": rel_best_f1, "best_threshold": rel_best_t,
            "best_precision": rel_best_p, "best_recall": rel_best_r,
            "sweep": rel_all,
        },
        "random_control": {"f1": rnd_f1, "precision": rnd_p, "recall": rnd_r},
        "arms_differ": bool(arms_differ),
        "digest_abs": digest_abs,
        "digest_rel": digest_rel,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict logic (PRE-REG bands, verbatim from the hand-off)
# ---------------------------------------------------------------------------
def compute_verdict(results: List[Dict], precheck: Dict) -> Tuple[str, str, Dict]:
    if not precheck.get("precheck_passed"):
        return (
            "PRECHECK_FAIL_HARNESS_BUG",
            "MANDATORY PRE-CHECK FAILED: residual_magnitude did not discriminate "
            f"coherent-repeat (late_mean={precheck.get('coherent_late_mean_residual')}) "
            f"from scrambled control (late_mean={precheck.get('scrambled_late_mean_residual')}). "
            "Per the hand-off contract, any downstream F1 result is a HARNESS BUG, "
            "not a mechanism negative -- refusing to emit HARD_FAIL/HARD_PASS.",
            {},
        )

    if not results:
        return ("HARD_FAIL", "No valid seed results.", {})

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode gate violated "
                             "(n_llm_calls > 0).", {})

    any_identical = any(not r.get("arms_differ", True) for r in results)
    if any_identical:
        return ("HARD_FAIL", "HARD_FAIL: META_RULE_AF violation -- ABS and REL "
                             "gate predictions were bit-identical on at least one "
                             "seed (arm-implementation bug).", {})

    rel_f1s = [r["rel_gate"]["best_f1"] for r in results]
    abs_f1s = [r["abs_gate"]["best_f1"] for r in results]
    margins = [rel - abs_ for rel, abs_ in zip(rel_f1s, abs_f1s)]

    rel_f1_mean = float(np.mean(rel_f1s))
    rel_f1_min = float(np.min(rel_f1s))
    abs_f1_mean = float(np.mean(abs_f1s))
    abs_f1_min = float(np.min(abs_f1s))
    worst_margin = float(np.min(margins))
    mean_margin = float(np.mean(margins))

    stats = {
        "rel_f1_mean": rel_f1_mean, "rel_f1_min": rel_f1_min,
        "abs_f1_mean": abs_f1_mean, "abs_f1_min": abs_f1_min,
        "worst_margin": worst_margin, "mean_margin": mean_margin,
        "rel_f1_per_seed": rel_f1s, "abs_f1_per_seed": abs_f1s,
        "margin_per_seed": margins,
    }

    gate_hp1 = record_gate("REL_F1_GE_0P75", rel_f1_mean, 0.75, ">=",
                           note="hand-off HARD_PASS condition 1")
    gate_hp2 = record_gate("WORST_MARGIN_GE_NEG0P05", worst_margin, -0.05, ">=",
                           note="hand-off HARD_PASS condition 2 (rel not worse "
                                "than abs by >0.05 F1 worst-case)")
    gate_hf = record_gate("REL_F1_MEAN_LT_0P50", rel_f1_mean, 0.50, "<",
                          note="hand-off HARD_FAIL condition (pre-check gated)")
    stats["structured_gate_claims"] = [gate_hp1, gate_hp2, gate_hf]

    summary = (
        f"REL(f1_mean={rel_f1_mean:.3f},f1_min={rel_f1_min:.3f}) "
        f"ABS(f1_mean={abs_f1_mean:.3f},f1_min={abs_f1_min:.3f}) "
        f"worst_margin={worst_margin:.3f} mean_margin={mean_margin:.3f}"
    )

    if gate_hp1["gate_verdict"] and gate_hp2["gate_verdict"]:
        return ("HARD_PASS",
                f"HARD_PASS: relative-threshold F1_mean={rel_f1_mean:.3f} >= 0.75 "
                f"AND worst-case margin={worst_margin:.3f} >= -0.05 (rel not worse "
                f"than abs threshold_gate). {summary}", stats)

    if gate_hf["gate_verdict"]:
        return ("HARD_FAIL",
                f"HARD_FAIL: relative-threshold F1_mean={rel_f1_mean:.3f} < 0.50 "
                f"(mandatory pre-check passed first, so this is treated as a "
                f"genuine mechanism negative). {summary}", stats)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: relative-threshold F1_mean={rel_f1_mean:.3f} in "
            f"[0.50, 0.75) OR clears 0.75 but worst-case margin fails "
            f"(margin={worst_margin:.3f} < -0.05). {summary}", stats)


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
     f"running {remaining}", flush=True)

t_sweep_start = time.time()
all_results: List[Dict] = []
verdict = "UNSET"
verdict_msg = ""
stats: Dict = {}
try:
    for seed in remaining:
        print(f"[seed={seed}] predictive_coding_relative_threshold N={N_DIM} "
             f"EVENTS={EVENTS} mode={RUN_MODE}...", flush=True)
        result = run_seed(seed)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())

    if len(all_results) != len(SEEDS):
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = (
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected "
            f"{len(SEEDS)} units, got {len(all_results)}.")
        stats = {}
    else:
        # Smoke-time discriminator-fires gate (META_RULE_AG baseline_in_band):
        # ABS_GATE (the baseline being compared against) must be in the
        # measurable [0.05, 0.95] band, not saturated/floored by construction.
        if RUN_MODE in ("smoke", "self_test"):
            abs_f1_smoke = float(np.mean([r["abs_gate"]["best_f1"] for r in all_results]))
            assert_discriminator_fires(
                abs_f1_smoke >= 0.95, control_name="ABS_GATE_saturated",
                headline_name="baseline_in_band_upper", run_mode=RUN_MODE,
                extra=f"abs_f1_smoke={abs_f1_smoke:.3f}")
            assert_discriminator_fires(
                abs_f1_smoke <= 0.05, control_name="ABS_GATE_floored",
                headline_name="baseline_in_band_lower", run_mode=RUN_MODE,
                extra=f"abs_f1_smoke={abs_f1_smoke:.3f}")

        verdict, verdict_msg, stats = compute_verdict(all_results, _PRECHECK_RESULT)
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as exc:  # noqa: BLE001 -- deliberately broad at outer scope, per
                          # META_RULE_J this is the ONE place a failure is caught,
                          # recorded with full context, and RE-RAISED (never
                          # silently continued).
    elapsed_crash = time.time() - t_sweep_start
    crash_metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": float(elapsed_crash),
        "failure_class": type(exc).__name__,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }
    write_metrics(out_dir, crash_metrics)
    raise

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

mode_in_results = {r.get("run_mode", "?") for r in all_results} if all_results else set()
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (f"HARD_FAIL: stale smoke partials detected in FULL run. "
                   f"mode_in_results={mode_in_results}. " + verdict_msg)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} N={N_DIM} EVENTS={EVENTS} "
        f"REPEATS_PER_EVENT={REPEATS_PER_EVENT} BLOCK_EVENTS={BLOCK_EVENTS} "
        f"P_NOISY={P_NOISY} DECAY={DECAY} mode={RUN_MODE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N_DIM,
    "EVENTS": EVENTS,
    "REPEATS_PER_EVENT": REPEATS_PER_EVENT,
    "BLOCK_EVENTS": BLOCK_EVENTS,
    "P_NOISY": P_NOISY,
    "DECAY": DECAY,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "precheck": _PRECHECK_RESULT,
    "verdict_stats": stats,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "T": r.get("T"),
            "n_boundaries": r.get("n_boundaries"),
            "base_rate": r.get("base_rate"),
            "abs_gate": {k: v for k, v in r.get("abs_gate", {}).items() if k != "sweep"},
            "rel_gate": {k: v for k, v in r.get("rel_gate", {}).items() if k != "sweep"},
            "random_control": r.get("random_control"),
            "arms_differ": r.get("arms_differ"),
        }
        for r in all_results
    ],
    # cell-template mandate declarations (machine-auditable)
    "cell_chunked": True,
    "final_metrics_atomicity": "tmp_replace",
    "crlb_n_a": "boundary-detection F1 cell; no argmax/top-k associative-recall "
               "capacity ceiling applies",
    "calibration_check": "default_ok_for_this_regime",
    "arms_differ_verified": all(r.get("arms_differ") for r in all_results) if all_results else False,
    "cardinality_ok": (len(all_results) == len(SEEDS)) if all_results else False,
    "expected_n_units": len(SEEDS),
}
write_metrics(out_dir, metrics, results=all_results,
             gate_claims=stats.get("structured_gate_claims") if isinstance(stats, dict) else None)
print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)
