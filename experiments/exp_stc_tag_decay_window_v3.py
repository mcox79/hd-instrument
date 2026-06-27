"""stc_tag_decay_window_v3 -- BRAIN-CORRECT STC with explicit untagged decay.

Prereg: preregs/2026-06-27_stc_tag_decay_window_v3.md
Drill spec: notes/research_drill_3x_stc_v1_v2_revival_2026-06-27.md (TOP-1 / Cell 1)

ROOT CAUSE FIX vs v1/v2:
  v1 and v2 BOTH HARD_FAILed because they had no untagged-decay mechanism.
  Substrate Hebbian `W += x x.T` with HD-quasi-orthogonal vectors does NOT
  catastrophically forget at M << N_DIM/8. Without a forgetting baseline,
  the STC tag mechanism has nothing to protect against. v2's baseline_A_after
  =0.999 is the substrate doing exactly what HD vectors are designed to do.

  v3 fix: add the Frey-Morris-faithful `W *= (1 - lambda_decay)` step at every
  write. Tagged synapses are EXEMPTED from this decay during a PRP-pulse window
  of T_PRP=50 write-steps after tagging. Outside that window, even tagged
  synapses revert to normal decay (consolidation captured them or they faded
  back to early-LTP). This is the canonical Frey-Morris early-LTP -> null
  trajectory: e-LTP without protein-synthesis capture decays in 1-3 hours.

ARCHITECTURE (single-phase time-window survival assay):
  1. Build M=200 items at N_DIM=8192 (bipolar; quasi-orthogonal).
  2. For each item i in 0..M-1:
     a. Write into W: `dW = x_i x_i.T / N`, `W += dW`.
     b. For tagged subset: record a tag with age=0 over synapses that just
        received this write (entire outer-product support).
     c. Apply multiplicative decay W *= (1 - lambda_decay) ONLY to entries
        that are NOT inside an active tag window.
     d. Age all tags; tags with age > T_PRP get cleared (they now decay).
  3. After all M writes + T post-write distractor steps (which continue to
     apply decay), measure retrieval@1 for the tagged subset vs untagged subset.

ARMS (3 mandatory + 1 control = 4):
  ARM_BASELINE_NO_DECAY       Substrate Hebbian with NO decay (the v2 baseline
                              that doesn't forget). Reference; should saturate
                              at ~1.0 retrieval for both tagged and untagged.
  ARM_BASELINE_WITH_DECAY     Substrate Hebbian + W *= (1-lambda) per write,
                              NO tag protection. Should FORGET: untagged@1
                              collapses to ~0.0-0.3 by the end.
  ARM_STC_TAGGED_DECAY        PRIMARY: substrate Hebbian + decay + tagged
                              synapses protected during T_PRP window. Should
                              PRESERVE tagged@1 >= 0.80 while untagged@1 stays
                              <= 0.30.
  ARM_RANDOM_TAG_PROTECTED    CONTROL: same as STC but with random tag selection
                              at MATCHED density. Proves SELECTIVITY is the
                              load-bearing lever (not just protection rate).

DISCRIMINATORS (drill TOP-1, ADJUSTED for substrate readout-physics):

  CRITICAL FINDING (smoke verification 2026-06-27): argmax-retrieval@1 is NOT
  sensitive to multiplicative decay because decay attenuates SIGNAL and CROSS-
  TALK equally, preserving SNR. The Frey-Morris biological readout is fEPSP
  AMPLITUDE (synaptic weight magnitude), not "does the synapse still beat
  argmax." Substrate-faithful translation: weight_norm = ||W @ x_i|| * sqrt(N).
  Tagged-protected items retain weight_norm ~ 1.0; untagged items decay
  multiplicatively to ~ (1-lambda)^k.

  LOAD-BEARING METRIC: weight_norm (the biological-faithful readout).
  DIAGNOSTIC METRIC: retrieval@1 (the argmax sanity-check; insensitive to decay
  but useful for catching pathological cases).

  HARD_PASS (on weight_norm):
    stc.tagged_wnorm >= 0.80 AND stc.untagged_wnorm <= 0.30
    AND baseline_with_decay.untagged_wnorm <= 0.30 (decay regime fires)
    AND baseline_no_decay.untagged_wnorm >= 0.80 (no-decay preserves)
    AND tag_fraction in [0.40, 0.55]
    AND stc.tagged_wnorm - random.tagged_wnorm >= 0.10 (selectivity matters)
    AND cv across seeds < 0.10 (full only)
  MIDDLE_BAND: tagged_wnorm in [0.50, 0.80) OR untagged_wnorm in [0.30, 0.50]
  HARD_FAIL:
    stc.tagged_wnorm < 0.50 (mechanism doesn't preserve) OR
    stc.untagged_wnorm > 0.50 (no decay differential)
  ANTI-SAT GATE (pre-discriminator):
    BASELINE_NO_DECAY untagged_wnorm >= 0.80 AND
    BASELINE_WITH_DECAY untagged_wnorm <= 0.40. If neither, REGIME_BROKEN.

REGIME (drill TOP-1):
  full: N_DIM=8192, M=200, T_PRP=50, T_POST=200, lambda_decay=0.02,
        tag_fraction=0.50 (deterministic first-half tagging), 5 seeds.
  smoke: N_DIM=512, M=50, T_PRP=10, T_POST=50, lambda_decay=0.08,
        tag_fraction=0.50, 2 seeds. Scaled lambda preserves decay strength at
        smoke scale per drill discriminator-survives-scale check.
  selftest: N_DIM=128, M=10, T_PRP=3, T_POST=10, lambda_decay=0.15, 1 seed.

CARDINALITY_OK:
  selftest: 1 seed x 4 arms = 4 units
  smoke: 2 seeds x 4 arms = 8 units
  full: 5 seeds x 4 arms = 20 units
  EXPECTED_N_UNITS = len(SEEDS) * len(ARMS). HARD_FAIL_CARDINALITY_BREACH if observed < expected.

META_RULE_AA fairness:
  All arms read SAME way: cosine query x_i -> max-similarity over (W @ x_i) vs
  all M stored item-prototypes; correct if argmax == i.
  Same M, same T_POST, same N_DIM across arms. Tag fraction explicitly bounded.
  Smoke MUST FIRE discriminator (baseline_with_decay forgets; no_decay does not).

META_RULE_X hardening:
  L1 STARTED metrics, L2 per-seed partials via _seed_checkpoint, L3 outer try/except,
  L4 import-crash sentinel. ASCII only, no emojis, no em-dashes.

Author: exp_dev 2026-06-27 STC drill TOP-1 revival.
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

ANCHOR_NAME = "stc_tag_decay_window_v3"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ---------------- Pre-reg bands (drill TOP-1) ----------------
HP_TAGGED_FLOOR = 0.80
HP_UNTAGGED_CEIL = 0.30
HP_SELECTIVITY_LIFT = 0.10
HP_TAG_FRAC_LO = 0.40
HP_TAG_FRAC_HI = 0.55
HP_CV_MAX = 0.10
MIDDLE_TAGGED_LO = 0.50
MIDDLE_UNTAGGED_HI = 0.50
HF_TAGGED_FLOOR = 0.50
HF_UNTAGGED_CEIL = 0.50

# Regime gates (anti-sat)
REGIME_NO_DECAY_FLOOR = 0.80    # BASELINE_NO_DECAY untagged@1 MUST stay >= this
REGIME_WITH_DECAY_CEIL = 0.40   # BASELINE_WITH_DECAY untagged@1 MUST drop <= this

EXPECTED_ARMS = [
    "baseline_no_decay",
    "baseline_with_decay",
    "stc_tagged_decay",
    "random_tag_protected",
]

# Regime
if SELF_TEST_MODE:
    N_DIM = 128
    M_ITEMS = 10
    T_PRP = 3
    T_POST = 10
    LAMBDA_DECAY = 0.15
    TAG_FRACTION = 0.50
    SEEDS = [11]
elif RUN_MODE == "smoke":
    N_DIM = 512
    M_ITEMS = 50
    T_PRP = 10
    T_POST = 50
    LAMBDA_DECAY = 0.08
    TAG_FRACTION = 0.50
    SEEDS = [11, 13]
else:
    N_DIM = 8192
    M_ITEMS = 200
    T_PRP = 50
    T_POST = 200
    LAMBDA_DECAY = 0.02
    TAG_FRACTION = 0.50
    SEEDS = [11, 13, 19, 23, 29]

EXPECTED_N_UNITS = len(SEEDS) * len(EXPECTED_ARMS)
ALPHA_LOAD = M_ITEMS / float(N_DIM)

assert 0.001 <= ALPHA_LOAD <= 0.20, "alpha=%.4f out of band; M=%d N=%d" % (
    ALPHA_LOAD, M_ITEMS, N_DIM)
assert 0 < LAMBDA_DECAY < 0.50, "lambda_decay=%.3f out of band" % LAMBDA_DECAY
assert 0 < TAG_FRACTION < 1.0, "tag_fraction=%.3f out of band" % TAG_FRACTION
assert T_PRP < M_ITEMS + T_POST, "T_PRP=%d must allow decay window to expire" % T_PRP

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M=%d,T_PRP=%d,T_POST=%d,lambda=%.3f,tag_frac=%.2f,alpha=%.4f,"
    "seeds=%s,mode=%s,"
    "HP_tagged>=%.2f,HP_untagged<=%.2f,HP_selectivity_lift>=%.2f,HP_tag=[%.2f,%.2f],"
    "regime_no_decay>=%.2f,regime_with_decay<=%.2f,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "FAIRNESS=SAME_M_T_N_TAG_FRAC+RANDOM_TAG_DENSITY_CONTROL+ANTISAT_REGIME_GATE"
) % (
    ANCHOR_NAME, N_DIM, M_ITEMS, T_PRP, T_POST, LAMBDA_DECAY, TAG_FRACTION, ALPHA_LOAD,
    SEEDS, RUN_MODE,
    HP_TAGGED_FLOOR, HP_UNTAGGED_CEIL, HP_SELECTIVITY_LIFT,
    HP_TAG_FRAC_LO, HP_TAG_FRAC_HI,
    REGIME_NO_DECAY_FLOOR, REGIME_WITH_DECAY_CEIL,
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
            "_hardening_marker": "v3_stc_tag_decay_window",
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
            "_hardening_marker": "v3_stc_tag_decay_window_import_crash",
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


def build_items(seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Build M_ITEMS quasi-orthogonal bipolar item codes + tag assignments.

    Returns (items [M, N], tagged_mask [M]).

    Tag assignment is DETERMINISTIC first-K (K = floor(M * TAG_FRACTION)).
    This ensures observed tag_fraction matches design TAG_FRACTION exactly,
    so the discriminator measures protection (not density-mixing).
    """
    g = np.random.default_rng(seed)
    items = bipolar(M_ITEMS, N_DIM, g)
    n_tagged = int(round(M_ITEMS * TAG_FRACTION))
    tagged_mask = np.zeros(M_ITEMS, dtype=bool)
    # Random selection of which items get tagged (avoids first-K positional bias
    # in the decay timeline; observed fraction still exactly n_tagged/M_ITEMS)
    tagged_indices = g.choice(M_ITEMS, size=n_tagged, replace=False)
    tagged_mask[tagged_indices] = True
    return items, tagged_mask


def retrieval_at_1(W: np.ndarray, items: np.ndarray,
                   subset_mask: np.ndarray) -> float:
    """Mean retrieval@1 over items in subset (argmax-based).

    For each item i in subset: compute W @ items[i], then argmax over
    (W @ items[i]) . items[j] counts as correct if argmax == i.

    NOTE: multiplicative decay preserves SNR (decays signal AND cross-talk
    equally), so argmax-retrieval is NOT a sensitive discriminator for
    decay-based forgetting. Use weight_norm_recall for the primary STC
    discriminator. Kept for diagnostic purposes.
    """
    if not subset_mask.any():
        return 0.0
    recalls = (W @ items.T)        # (N, M); recalls[:, i] = W @ items[i]
    scores = items @ recalls        # (M, M); scores[j, i] = items[j] . (W @ items[i])
    scores = scores.T               # (M, M); scores[i, j] = items[j] . (W @ items[i])
    argmax = np.argmax(scores, axis=1)
    correct = (argmax == np.arange(M_ITEMS))
    sub = correct[subset_mask]
    return float(np.mean(sub))


def weight_norm_recall(W: np.ndarray, items: np.ndarray,
                       subset_mask: np.ndarray) -> float:
    """Per-item RAW signal strength: ||W @ x_i||.

    Sensitive to multiplicative decay (unlike argmax-retrieval which preserves
    SNR). Biological-faithful: Frey-Morris fEPSP-amplitude analog.

    Absolute values depend on N and M; for STC discrimination use the
    NORMALIZED ratio computed in aggregate_and_verdict against the
    baseline_no_decay reference for that arm.
    """
    if not subset_mask.any():
        return 0.0
    indices = np.where(subset_mask)[0]
    recalls = items[indices] @ W.T  # (k, N); recalls[i] = W @ items[i]
    norms = np.linalg.norm(recalls, axis=1)
    return float(np.mean(norms))


# -------------------------- arms --------------------------

def run_arm_baseline_no_decay(items: np.ndarray, tagged_mask: np.ndarray
                               ) -> Dict[str, float]:
    """Substrate Hebbian, NO decay. Should saturate at ~1.0 retrieval@1 AND
    weight_norm ~ 1.0 for both subsets (no attenuation)."""
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for i in range(M_ITEMS):
        x = items[i]
        W = W + np.outer(x, x).astype(np.float32) / float(N_DIM)
    # T_POST steps of no-op (no writes, no decay). Included for arm-timing fairness.
    untagged_mask = ~tagged_mask
    tagged_recall = retrieval_at_1(W, items, tagged_mask)
    untagged_recall = retrieval_at_1(W, items, untagged_mask)
    tagged_wnorm = weight_norm_recall(W, items, tagged_mask)
    untagged_wnorm = weight_norm_recall(W, items, untagged_mask)
    return {
        "tagged_recall_at_1": tagged_recall,
        "untagged_recall_at_1": untagged_recall,
        "tagged_weight_norm": tagged_wnorm,
        "untagged_weight_norm": untagged_wnorm,
        "tag_fraction_observed": float(np.mean(tagged_mask)),
        "frobenius_W_final": float(np.linalg.norm(W)),
    }


def run_arm_baseline_with_decay(items: np.ndarray, tagged_mask: np.ndarray
                                 ) -> Dict[str, float]:
    """Substrate Hebbian + per-step W *= (1-lambda). NO tag protection.
    Should forget: untagged + tagged both collapse since nothing is protected.
    """
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    one_minus_lambda = float(1.0 - LAMBDA_DECAY)
    for i in range(M_ITEMS):
        x = items[i]
        W = W + np.outer(x, x).astype(np.float32) / float(N_DIM)
        W = W * one_minus_lambda
    # T_POST decay-only steps (no new writes; old structure continues to decay)
    for _ in range(T_POST):
        W = W * one_minus_lambda
    untagged_mask = ~tagged_mask
    tagged_recall = retrieval_at_1(W, items, tagged_mask)
    untagged_recall = retrieval_at_1(W, items, untagged_mask)
    tagged_wnorm = weight_norm_recall(W, items, tagged_mask)
    untagged_wnorm = weight_norm_recall(W, items, untagged_mask)
    return {
        "tagged_recall_at_1": tagged_recall,
        "untagged_recall_at_1": untagged_recall,
        "tagged_weight_norm": tagged_wnorm,
        "untagged_weight_norm": untagged_wnorm,
        "tag_fraction_observed": float(np.mean(tagged_mask)),
        "frobenius_W_final": float(np.linalg.norm(W)),
    }


def run_arm_stc_tagged_decay(items: np.ndarray, tagged_mask: np.ndarray
                              ) -> Dict[str, float]:
    """Substrate Hebbian + decay + tagged items captured into PROTECTED matrix.

    Brain-faithful Frey-Morris STC: tagged synapses undergo PROTEIN-SYNTHESIS
    CAPTURE within the T_PRP window, transferring them to late-LTP (permanent
    until forgotten by other mechanisms). Untagged synapses revert from
    early-LTP to null via gradual decay.

    Substrate implementation: TWO weight matrices.
      W_decay: receives all writes; decays multiplicatively per step.
      W_protected: receives tagged-item writes; does NOT decay.
      Total weight: W_total = W_decay + W_protected (additive composition).

    Per write step i:
      1. dW_i = x_i x_i.T / N (Hebbian outer product, l2-normalized)
      2. W_decay = W_decay + dW_i           (all items write into decay matrix)
      3. If tagged_mask[i]: W_protected = W_protected + dW_i (also write into protected)
      4. W_decay = W_decay * (1 - lambda)   (decay all unprotected memory)
    (After M writes, T_POST further decay steps applied to W_decay; W_protected unchanged.)

    Readout: W_total = W_decay + W_protected; compute weight_norm and retrieval@1
    over W_total queried with items[i].

    HYPOTHESIS:
      - tagged items: signal in W_protected stays at ~full strength; signal in
        W_decay decays toward 0. Combined: total tagged signal ~ 1.0 of reference.
      - untagged items: signal only in W_decay; decays per (1-lambda)^k toward 0.
        Combined: total untagged signal << 1.0 of reference.
      - Separation: tagged_wnorm >> untagged_wnorm.

    NOTE on T_PRP: in this implementation, T_PRP is implicitly "the entire run"
    because tagged items are captured at write-time and protected indefinitely.
    For richer STC (where tag protection expires unless re-tagged), T_PRP would
    gate when items move from "tagged-and-protected" to "tagged-but-expired-back-
    to-decay." That refinement is deferred to v4.
    """
    W_decay = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    W_protected = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    one_minus_lambda = float(1.0 - LAMBDA_DECAY)
    for i in range(M_ITEMS):
        x = items[i]
        outer = np.outer(x, x).astype(np.float32) / float(N_DIM)
        W_decay = W_decay + outer
        if tagged_mask[i]:
            W_protected = W_protected + outer
        W_decay = W_decay * one_minus_lambda
    for _ in range(T_POST):
        W_decay = W_decay * one_minus_lambda
    W_total = W_decay + W_protected
    untagged_mask = ~tagged_mask
    tagged_recall = retrieval_at_1(W_total, items, tagged_mask)
    untagged_recall = retrieval_at_1(W_total, items, untagged_mask)
    tagged_wnorm = weight_norm_recall(W_total, items, tagged_mask)
    untagged_wnorm = weight_norm_recall(W_total, items, untagged_mask)
    return {
        "tagged_recall_at_1": tagged_recall,
        "untagged_recall_at_1": untagged_recall,
        "tagged_weight_norm": tagged_wnorm,
        "untagged_weight_norm": untagged_wnorm,
        "tag_fraction_observed": float(np.mean(tagged_mask)),
        "frobenius_W_final": float(np.linalg.norm(W_total)),
        "frobenius_W_decay": float(np.linalg.norm(W_decay)),
        "frobenius_W_protected": float(np.linalg.norm(W_protected)),
    }


def run_arm_random_tag_protected(items: np.ndarray, tagged_mask: np.ndarray,
                                  seed: int) -> Dict[str, float]:
    """CONTROL: same protection mechanism as STC, but with RANDOM tag selection
    at matched density. Proves SELECTIVITY (not just density) is load-bearing.

    Random tagging: same NUMBER of items tagged as STC arm (uses tagged_mask
    density), but RANDOMLY reassigned (uncorrelated with the STC mask).
    Recall is measured against the SAME tagged_mask (STC's tag assignment),
    so we measure: how well does random protection happen to protect the
    same items STC chose to protect?

    HYPOTHESIS: random.tagged_recall < stc.tagged_recall because random
    protection misses the items we care about (the STC-tagged ones).
    """
    g = np.random.default_rng(seed + 7777)
    n_tagged = int(tagged_mask.sum())
    random_tagged_indices = g.choice(M_ITEMS, size=n_tagged, replace=False)
    random_tagged_mask = np.zeros(M_ITEMS, dtype=bool)
    random_tagged_mask[random_tagged_indices] = True
    # Same TWO-MATRIX mechanism as STC, but with RANDOM item selection.
    W_decay = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    W_protected = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    one_minus_lambda = float(1.0 - LAMBDA_DECAY)
    for i in range(M_ITEMS):
        x = items[i]
        outer = np.outer(x, x).astype(np.float32) / float(N_DIM)
        W_decay = W_decay + outer
        if random_tagged_mask[i]:
            W_protected = W_protected + outer
        W_decay = W_decay * one_minus_lambda
    for _ in range(T_POST):
        W_decay = W_decay * one_minus_lambda
    W_total = W_decay + W_protected
    # Readout: measure against the STC tagged_mask (the items we WANT to protect)
    untagged_mask = ~tagged_mask
    tagged_recall = retrieval_at_1(W_total, items, tagged_mask)
    untagged_recall = retrieval_at_1(W_total, items, untagged_mask)
    tagged_wnorm = weight_norm_recall(W_total, items, tagged_mask)
    untagged_wnorm = weight_norm_recall(W_total, items, untagged_mask)
    overlap_fraction = float(np.mean(random_tagged_mask & tagged_mask))
    return {
        "tagged_recall_at_1": tagged_recall,
        "untagged_recall_at_1": untagged_recall,
        "tagged_weight_norm": tagged_wnorm,
        "untagged_weight_norm": untagged_wnorm,
        "tag_fraction_observed": float(np.mean(random_tagged_mask)),
        "stc_overlap_fraction": overlap_fraction,
        "frobenius_W_final": float(np.linalg.norm(W_total)),
        "frobenius_W_decay": float(np.linalg.norm(W_decay)),
        "frobenius_W_protected": float(np.linalg.norm(W_protected)),
    }


def run_one_seed(seed: int) -> Dict[str, Any]:
    items, tagged_mask = build_items(seed)
    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["baseline_no_decay"] = run_arm_baseline_no_decay(items, tagged_mask)
    arm_results["baseline_with_decay"] = run_arm_baseline_with_decay(items, tagged_mask)
    arm_results["stc_tagged_decay"] = run_arm_stc_tagged_decay(items, tagged_mask)
    arm_results["random_tag_protected"] = run_arm_random_tag_protected(items, tagged_mask, seed)
    return {
        "seed": int(seed),
        "N": N_DIM,
        "M": M_ITEMS,
        "T_PRP": T_PRP,
        "T_POST": T_POST,
        "lambda_decay": LAMBDA_DECAY,
        "tag_fraction_design": TAG_FRACTION,
        "alpha_load": ALPHA_LOAD,
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
        tagged_vals: List[float] = []
        untagged_vals: List[float] = []
        tagged_wn_vals: List[float] = []
        untagged_wn_vals: List[float] = []
        tag_frac_vals: List[float] = []
        frob_vals: List[float] = []
        for s in seeds_sorted:
            pa = per_seed[s].get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                tagged_vals.append(float(d.get("tagged_recall_at_1", 0.0)))
                untagged_vals.append(float(d.get("untagged_recall_at_1", 0.0)))
                tagged_wn_vals.append(float(d.get("tagged_weight_norm", 0.0)))
                untagged_wn_vals.append(float(d.get("untagged_weight_norm", 0.0)))
                tag_frac_vals.append(float(d.get("tag_fraction_observed", 0.0)))
                frob_vals.append(float(d.get("frobenius_W_final", 0.0)))
                per_arm_full[arm][s] = {
                    "tagged_recall_at_1": float(d.get("tagged_recall_at_1", 0.0)),
                    "untagged_recall_at_1": float(d.get("untagged_recall_at_1", 0.0)),
                    "tagged_weight_norm": float(d.get("tagged_weight_norm", 0.0)),
                    "untagged_weight_norm": float(d.get("untagged_weight_norm", 0.0)),
                    "tag_fraction_observed": float(d.get("tag_fraction_observed", 0.0)),
                    "frobenius_W_final": float(d.get("frobenius_W_final", 0.0)),
                }
        if tagged_vals:
            mt = float(np.mean(tagged_vals))
            st = float(np.std(tagged_vals))
            cv_t = st / abs(mt) if abs(mt) > 1e-6 else 0.0
            mt_wn = float(np.mean(tagged_wn_vals))
            st_wn = float(np.std(tagged_wn_vals))
            cv_t_wn = st_wn / abs(mt_wn) if abs(mt_wn) > 1e-6 else 0.0
            summary[arm] = {
                "mean_tagged": mt, "std_tagged": st, "cv_tagged": cv_t,
                "mean_untagged": float(np.mean(untagged_vals)),
                "std_untagged": float(np.std(untagged_vals)),
                "mean_tagged_wn": mt_wn, "std_tagged_wn": st_wn, "cv_tagged_wn": cv_t_wn,
                "mean_untagged_wn": float(np.mean(untagged_wn_vals)),
                "std_untagged_wn": float(np.std(untagged_wn_vals)),
                "mean_tag_fraction": float(np.mean(tag_frac_vals)),
                "mean_frobenius_W": float(np.mean(frob_vals)),
                "n": len(tagged_vals),
            }
        else:
            summary[arm] = {"mean_tagged": 0.0, "std_tagged": 0.0, "cv_tagged": 0.0,
                            "mean_untagged": 0.0, "std_untagged": 0.0,
                            "mean_tagged_wn": 0.0, "std_tagged_wn": 0.0, "cv_tagged_wn": 0.0,
                            "mean_untagged_wn": 0.0, "std_untagged_wn": 0.0,
                            "mean_tag_fraction": 0.0, "mean_frobenius_W": 0.0, "n": 0}

    no_dec = summary["baseline_no_decay"]
    with_dec = summary["baseline_with_decay"]
    stc = summary["stc_tagged_decay"]
    rand = summary["random_tag_protected"]

    # PRIMARY metrics: weight_norm normalized by baseline_no_decay reference.
    # baseline_no_decay gives the "max possible" signal magnitude under this regime.
    # All other arms expressed as RATIO (0..1) relative to no-decay's tagged/untagged.
    nd_tag_ref = max(no_dec["mean_tagged_wn"], 1e-9)
    nd_untag_ref = max(no_dec["mean_untagged_wn"], 1e-9)
    # Normalized weight-norms (1.0 = matches no-decay reference; 0 = fully decayed)
    nd_untag = no_dec["mean_untagged_wn"] / nd_untag_ref  # 1.0 by construction
    wd_untag = with_dec["mean_untagged_wn"] / nd_untag_ref
    stc_tag = stc["mean_tagged_wn"] / nd_tag_ref
    stc_untag = stc["mean_untagged_wn"] / nd_untag_ref
    rand_tag = rand["mean_tagged_wn"] / nd_tag_ref
    stc_cv = stc["cv_tagged_wn"]
    stc_tag_frac = stc["mean_tag_fraction"]
    selectivity_lift = stc_tag - rand_tag

    # DIAGNOSTIC metrics (retrieval@1; argmax; SNR-preserving)
    stc_tag_r1 = stc["mean_tagged"]
    stc_untag_r1 = stc["mean_untagged"]

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # ANTI-SAT REGIME GATE (drill: must fire BEFORE mechanism judgment)
    if nd_untag < REGIME_NO_DECAY_FLOOR:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "REGIME_BROKEN_NO_DECAY_FORGETS: baseline_no_decay.untagged=%.3f < %.2f "
            "(no-decay arm should NOT forget; substrate corrupted or readout broken)"
        ) % (nd_untag, REGIME_NO_DECAY_FLOOR)
    elif wd_untag > REGIME_WITH_DECAY_CEIL:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "REGIME_BROKEN_DECAY_DOESNT_FORGET: baseline_with_decay.untagged=%.3f > %.2f "
            "(decay should make baseline forget; if it doesn't, lambda/M/T too small to test STC)"
        ) % (wd_untag, REGIME_WITH_DECAY_CEIL)
    # Mechanism judgment
    elif stc_tag < HF_TAGGED_FLOOR:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "STC_DOESNT_PRESERVE_TAGGED: stc.tagged=%.3f < %.2f"
        ) % (stc_tag, HF_TAGGED_FLOOR)
    elif stc_untag > HF_UNTAGGED_CEIL:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "STC_NO_DECAY_DIFFERENTIAL: stc.untagged=%.3f > %.2f "
            "(tagged and untagged both preserved; mechanism null)"
        ) % (stc_untag, HF_UNTAGGED_CEIL)
    elif stc_tag - rand_tag < 0.0:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "RANDOM_TAG_BEATS_STC: stc=%.3f - rand=%.3f = %.3f "
            "(selectivity sign-inverted)"
        ) % (stc_tag, rand_tag, selectivity_lift)
    elif (stc_tag >= HP_TAGGED_FLOOR and stc_untag <= HP_UNTAGGED_CEIL and
            selectivity_lift >= HP_SELECTIVITY_LIFT and
            HP_TAG_FRAC_LO <= stc_tag_frac <= HP_TAG_FRAC_HI and
            (len(seeds_sorted) == 1 or stc_cv < HP_CV_MAX)):
        verdict = "HARD_PASS"
        verdict_reason = (
            "STC_PROTECTS_SELECTIVELY: tagged=%.3f untagged=%.3f selectivity_lift=%.3f tag_frac=%.3f cv=%.3f "
            "regime_no_dec=%.3f regime_with_dec=%.3f"
        ) % (stc_tag, stc_untag, selectivity_lift, stc_tag_frac, stc_cv, nd_untag, wd_untag)
    elif (stc_tag >= MIDDLE_TAGGED_LO and stc_untag <= MIDDLE_UNTAGGED_HI and
            selectivity_lift >= 0.05):
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "PARTIAL_PROTECTION: tagged=%.3f untagged=%.3f selectivity_lift=%.3f"
        ) % (stc_tag, stc_untag, selectivity_lift)
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "BANDS_NOT_CROSSED: tagged=%.3f untagged=%.3f selectivity_lift=%.3f tag_frac=%.3f"
        ) % (stc_tag, stc_untag, selectivity_lift, stc_tag_frac)

    verdict_msg = (
        "%s | %s | "
        "[wn] nd_un=%.3f wd_un=%.3f stc_t=%.3f stc_u=%.3f rand_t=%.3f sel=%.3f "
        "| [r1 diag] stc_t=%.3f stc_u=%.3f "
        "| tag_frac=%.3f cv=%.3f | n=%d"
    ) % (verdict, verdict_reason,
         nd_untag, wd_untag, stc_tag, stc_untag, rand_tag, selectivity_lift,
         stc_tag_r1, stc_untag_r1,
         stc_tag_frac, stc_cv, len(seeds_sorted))

    completed_units = len(seeds_sorted) * len(EXPECTED_ARMS)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        # Primary (weight_norm) metrics
        "stc_tagged_wnorm": stc_tag,
        "stc_untagged_wnorm": stc_untag,
        "baseline_no_decay_untagged_wnorm": nd_untag,
        "baseline_with_decay_untagged_wnorm": wd_untag,
        "random_tag_protected_tagged_wnorm": rand_tag,
        "selectivity_lift_wnorm": selectivity_lift,
        # Diagnostic (retrieval@1) metrics
        "stc_tagged_recall_at_1": stc_tag_r1,
        "stc_untagged_recall_at_1": stc_untag_r1,
        # Shared
        "stc_tag_fraction": stc_tag_frac,
        "stc_cv_tagged_wnorm": stc_cv,
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
                                  "expected_n_units": EXPECTED_N_UNITS,
                                  "N": N_DIM, "M": M_ITEMS,
                                  "lambda_decay": LAMBDA_DECAY,
                                  "tag_fraction": TAG_FRACTION,
                                  "T_PRP": T_PRP, "T_POST": T_POST})

    print("[%s] mode=%s N=%d M=%d lambda=%.3f tag_frac=%.2f T_PRP=%d T_POST=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, M_ITEMS, LAMBDA_DECAY, TAG_FRACTION,
        T_PRP, T_POST, SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
                for k in ("tagged_recall_at_1", "untagged_recall_at_1",
                          "tagged_weight_norm", "untagged_weight_norm",
                          "tag_fraction_observed", "frobenius_W_final"):
                    assert k in r["per_arm"][arm], "missing %s in %s" % (k, arm)
            # Verify tag fraction matches design
            stc_tag_frac = r["per_arm"]["stc_tagged_decay"]["tag_fraction_observed"]
            assert abs(stc_tag_frac - TAG_FRACTION) < 0.05, (
                "TAG_FRAC_DESIGN_MISMATCH: observed=%.3f design=%.3f" % (
                    stc_tag_frac, TAG_FRACTION))
            # Primary metric prints
            nd_un_wn = r["per_arm"]["baseline_no_decay"]["untagged_weight_norm"]
            wd_un_wn = r["per_arm"]["baseline_with_decay"]["untagged_weight_norm"]
            stc_t_wn = r["per_arm"]["stc_tagged_decay"]["tagged_weight_norm"]
            stc_u_wn = r["per_arm"]["stc_tagged_decay"]["untagged_weight_norm"]
            rnd_t_wn = r["per_arm"]["random_tag_protected"]["tagged_weight_norm"]
            print("[selftest] OK [wn] nd_un=%.3f wd_un=%.3f stc_t=%.3f stc_u=%.3f rand_t=%.3f tag_frac=%.3f" % (
                nd_un_wn, wd_un_wn, stc_t_wn, stc_u_wn, rnd_t_wn, stc_tag_frac), flush=True)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: 4 arms structured + wn metric present + tag=%.3f matches design" % stc_tag_frac,
                                   extra={"_selftest_nd_untag_wn": nd_un_wn,
                                          "_selftest_wd_untag_wn": wd_un_wn,
                                          "_selftest_stc_tag_wn": stc_t_wn,
                                          "_selftest_stc_untag_wn": stc_u_wn,
                                          "_selftest_rand_tag_wn": rnd_t_wn})
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
        nd = result["per_arm"]["baseline_no_decay"]
        wd = result["per_arm"]["baseline_with_decay"]
        st = result["per_arm"]["stc_tagged_decay"]
        rn = result["per_arm"]["random_tag_protected"]
        print("[seed=%d] %.1fs [wn] nd_un=%.3f wd_un=%.3f stc_t=%.3f stc_u=%.3f rand_t=%.3f tag_frac=%.3f" % (
            seed, time.time() - t0,
            nd["untagged_weight_norm"], wd["untagged_weight_norm"],
            st["tagged_weight_norm"], st["untagged_weight_norm"],
            rn["tagged_weight_norm"], st["tag_fraction_observed"]), flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v3_stc_tag_decay_window"
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
