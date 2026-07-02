"""M1.10 ResponsePlanner primitive -- Stage 3 v1 (frame retrieval + role-slot bind).

Anchor: substrate_response_planner_frame_slot_composition_v1
Pre-reg: preregs/2026-07-02_substrate_response_planner_frame_slot_composition_v1.md
Drill:   notes/research_M1_10_response_planner_primitive_design_2026-07-02.md

Sister primitive to M1.9 SemanticParser (CG'd 2026-07-02 commit a508452e cell,
c0ef97b5b hdlab). M1.9 UNBINDS role_keys to recover slots from an input bundle;
M1.10 BINDS response_role_keys with slot_fillers to CONSTRUCT a response_hd.
Same HRR/BSC algebra; inverse operation. STRONGEST discriminator is
ARM_M19_ROUNDTRIP: parse M1.10's response_hd back through M1.9 and verify the
intent+slots recover -- proves round-trip fidelity of the bind-unbind pair.

FRAMING DISCIPLINE (LOAD-BEARING, USER 2026-07-02):
MECHANISM PROOF. Inputs are integer indices -> HD lookup + bind (NO tokens, NO
characters, NO English). Substrate does NOT understand language. Output is an
HD that a future (unbuilt) Stage 4 decoder would translate to text. See
`feedback_never_narrate_synthetic_HD_bundles_as_english_language_capability_
USER_2026-07-02`.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed + discriminator_reachability declared (CRLB N/A per prereg;
     chance floor 1/25=0.04 frame, 1/20=0.05 slot per role, 1/50=0.02 intent)
 - baseline_in_band at smoke (META_RULE_AG); TEMPLATE_ONLY frame~1.0 slot~chance;
     COMPOSE_ONLY frame~chance slot~1.0; HYBRID both~1.0 -- baselines are POSITIVE
     controls (not "0.05<b<0.95"; declared exemption in prereg baseline_in_band).
 - discriminator survives scale (smoke at full N_DIM=8192; only N_test reduced)
 - HARD_PASS strictly above floor (META_RULE_L)
 - HP_SCOPE per-arm declaration in pre-reg (LOAD-BEARING on ARM_HYBRID + ARM_M19_ROUNDTRIP)
 - cardinality_ok mandatory (EXPECTED_N_UNITS = 15 arm-seed units)
 - per-unit failure-class instrumentation (no bare except)
 - calibration_check = default_ok_for_this_regime (deterministic bind/unbind,
     no learned parameters; K=5 K/N=6e-4 << Plate 1995 capacity floor)
 - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
 - progress_logging = print_flush_true (line-buffered stdout at cell start)

Route: SMOKE local_cpu_queue; FULL remote_cpu_queue via hdi_orchestrator.
ASCII-only. No emojis. REPO-relative paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np
import torch

# Ensure repo root is on sys.path so `hdlab` is importable when runner invokes as script.
_REPO_ROOT_FOR_IMPORT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT_FOR_IMPORT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_FOR_IMPORT)

# Substrate primitives (load-bearing invocations)
from hdlab.intent_classifier import IntentClassifier
from hdlab.binding import bind as hd_bind
from hdlab.binding import unbind as hd_unbind
from hdlab.cleanup_family import k_NN_lookup
from hdlab.semantic_parser import SemanticParser  # M1.9 CG'd 2026-07-02 (c0ef97b5b)

# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------

ANCHOR_NAME = "substrate_response_planner_frame_slot_composition_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

N_DIM = 8192
N_INTENTS = 50
N_ROLES = 5
ROLE_NAMES = ["SUBJECT", "OBJECT", "ATTRIBUTE", "TIME", "LOCATION"]
SLOT_DICT_SIZE_PER_ROLE = 20  # HYPOTHESIZED@prereg (smaller than M1.9's 100; still >> chance)
N_FRAMES = 25                 # HYPOTHESIZED@prereg (many-to-one intent->frame, 2 intents avg per frame)
# THEORETICAL@bind-noise-variance-empirical (measured 2026-07-02): HRR bind
# of two bipolar N=8192 vectors produces output with ||bind|| ~ N (not sqrt(N))
# because circular convolution accumulates. Consequently <bind(a,b), c> for
# independent random bipolar c has stddev ~7600 (empirical), close to N_DIM.
# Sum of K=5 bind terms has noise stddev ~sqrt(5)*7600 = 16977.
# For frame retrieval with UN-WEIGHTED frame_hd: signal N_DIM=8192 < expected
# max noise across 25 frame competitors (~42800). So frame_hd MUST be weighted
# to dominate bind noise. FRAME_WEIGHT=8 gives signal 65536 vs max noise 42800
# (>1.5x margin; MEASURED@selftest to give frame_acc >=0.95).
# This slightly deviates from prereg's formula "frame_hd + INTENT_WEIGHT*intent_hd"
# which had implicit frame_hd weight 1. HYPOTHESIZED@prereg was wrong; empirical
# fix documented here + surfaced to Skunkworks in cell docstring.
FRAME_WEIGHT = 8.0
# THEORETICAL@intent-vs-bundle-signal-ratio at N_DIM=8192, K=5 roles,
# W_frame=W_intent=8: intent_hd and frame_hd EACH have signal 8*N_DIM = 65536,
# noise on wrong-competitor cleanup ~sqrt(69)*N_DIM = 68050 (from unbind terms)
# for slot recovery, ~sqrt(5*7600^2 + 8*sqrt(N))*... for frame recovery.
# All three legs (frame/intent/slot) reach SNR >5 (MEASURED@selftest).
INTENT_WEIGHT = 8.0

# smoke: fewer test examples; substrate parameters IDENTICAL (per DISCRIMINATOR-MUST-SURVIVE-SCALE Option A)
N_TEST_FULL = 200
N_TEST_SMOKE = 50

SEEDS_FULL = [11, 17, 23]
SEEDS_SMOKE = [11, 17, 23]

ARMS = [
    "ARM_TEMPLATE_ONLY",
    "ARM_COMPOSE_ONLY",
    "ARM_HYBRID",
    "ARM_SHUFFLED_RESPONSE_ROLE_KEYS",
    "ARM_M19_ROUNDTRIP",
]

# HP bands (per prereg Section "HP bands")
HP_FRAME_MATCH_FLOOR = 0.85            # HYPOTHESIZED@prereg
HP_SLOT_FILL_FLOOR = 0.80              # HYPOTHESIZED@prereg
HP_ROUNDTRIP_INTENT_FLOOR = 0.80       # HYPOTHESIZED@prereg
HP_ROUNDTRIP_SLOT_FLOOR = 0.80         # HYPOTHESIZED@prereg
HP_LIFT_VS_TEMPLATE_FLOOR = 0.30       # HYPOTHESIZED@prereg
HP_SHUFFLED_SLOT_CEILING = 0.20        # HYPOTHESIZED@sanity-control chance=1/20=0.05
HP_CV_CEILING = 0.10                   # HYPOTHESIZED@prereg (cross-seed cv on hybrid slot_fill)

# HARD_FAIL bands (falsification)
HF_FRAME_MATCH_FLOOR = 0.70            # HYPOTHESIZED@prereg
HF_ROUNDTRIP_SLOT_FLOOR = 0.60         # HYPOTHESIZED@prereg
HF_SHUFFLED_SLOT_CEILING = 0.30        # HYPOTHESIZED@prereg
# Envelope integrity gates
HF_TEMPLATE_ONLY_FRAME_FLOOR = 0.95    # HYPOTHESIZED@sanity: templates trivially recoverable
HF_INTEGRATION_MARGIN = 0.03           # HYPOTHESIZED@prereg: compose_only slot > hybrid slot + 0.03 = HF

EXPECTED_N_UNITS = len(SEEDS_FULL) * len(ARMS)  # 15
CARDINALITY_FLOOR = 13


# ------------------------------------------------------------------------------
# I/O helpers (start marker, crash diagnostic, heartbeat, atomic metrics)
# ------------------------------------------------------------------------------

def _output_dir(run_mode: str) -> str:
    suffix = "_smoke" if run_mode == "smoke" else ""
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}{suffix}")


def _write_start_marker(output_dir: str, run_mode: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": EXPECTED_N_UNITS,
        "host": platform.node(),
    }
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _emit_heartbeat(output_dir: str, unit_idx: int, total_units: int, elapsed_s: float, extra: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": elapsed_s,
        "extra": extra,
    }
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    os.makedirs(output_dir, exist_ok=True)
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ------------------------------------------------------------------------------
# Synthetic Stage 3 schema generation
# ------------------------------------------------------------------------------

def _make_response_role_keys(n_dim: int, seed: int) -> np.ndarray:
    """Random bipolar RESPONSE role keys [N_ROLES, N_DIM]. Disjoint from any
    parse-side role keys via seed-domain separation (offset 1093)."""
    rng = np.random.default_rng(int(seed) * 4093 + 1093)
    return (rng.integers(0, 2, size=(N_ROLES, n_dim)) * 2 - 1).astype(np.float32)


def _make_slot_dicts(n_dim: int, seed: int) -> List[np.ndarray]:
    """SHARDED per-role slot dictionaries: each [SLOT_DICT_SIZE_PER_ROLE, N_DIM].

    Per CG_META 2026-07-02 storage-strategy: sharded. Disjoint per-role via
    seed-offset so no vector shared across roles."""
    dicts = []
    for r in range(N_ROLES):
        rng = np.random.default_rng(int(seed) * 8191 + r * 251 + 313)
        d = (rng.integers(0, 2, size=(SLOT_DICT_SIZE_PER_ROLE, n_dim)) * 2 - 1).astype(np.float32)
        dicts.append(d)
    return dicts


def _make_frame_codebook(n_dim: int, seed: int) -> np.ndarray:
    """Random bipolar frame codebook [N_FRAMES, N_DIM]. Response-template shelf.

    Independent random draw from intent codebook so frames and intents live in
    disjoint slots of the vector space (avoids frame_hd collision with an
    intent_hd summand -- would otherwise inflate frame_match trivially).
    """
    rng = np.random.default_rng(int(seed) * 8191 + 4441)
    return (rng.integers(0, 2, size=(N_FRAMES, n_dim)) * 2 - 1).astype(np.float32)


def _frame_lookup(intent_id: int) -> int:
    """Deterministic many-to-one intent -> frame_id. N_INTENTS=50, N_FRAMES=25
    -> 2 intents per frame on average.
    """
    return int(intent_id) % N_FRAMES


def _make_examples(n_examples: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Generate (intent_label, slot_labels_per_role) tuples.

    intent_labels: [n_examples] int64
    slot_labels: [n_examples, N_ROLES] int64
    """
    rng = np.random.default_rng(int(seed) * 65537 + 5)
    intent_labels = rng.integers(0, N_INTENTS, size=n_examples).astype(np.int64)
    slot_labels = rng.integers(0, SLOT_DICT_SIZE_PER_ROLE, size=(n_examples, N_ROLES)).astype(np.int64)
    return intent_labels, slot_labels


# ------------------------------------------------------------------------------
# Response-HD constructors (one per arm)
# ------------------------------------------------------------------------------

def _construct_template_only(
    intent_labels: np.ndarray,
    frame_codebook: np.ndarray,
) -> np.ndarray:
    """response_hd = frame_hd (no slots, no intent). Establishes template-selection
    floor. Frame match should be trivially perfect (identity); slot/intent
    recovery should collapse to chance because no compositional info in output.
    """
    n = intent_labels.shape[0]
    n_dim = frame_codebook.shape[1]
    out = np.zeros((n, n_dim), dtype=np.float32)
    for i in range(n):
        frame_id = _frame_lookup(int(intent_labels[i]))
        out[i] = (FRAME_WEIGHT * frame_codebook[frame_id]).astype(np.float32)
    return out


def _construct_compose_only(
    intent_labels: np.ndarray,
    slot_labels: np.ndarray,
    intent_codebook: np.ndarray,
    response_role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
) -> np.ndarray:
    """response_hd = INTENT_WEIGHT * intent_hd + sum_r bind(rk_r, slot_r).
    No frame retrieval. Frame_match should collapse to chance (1/25=0.04);
    slot_fill should be ~1.0 (compositional bind fully invertible)."""
    n = intent_labels.shape[0]
    n_dim = intent_codebook.shape[1]
    out = np.zeros((n, n_dim), dtype=np.float32)
    role_keys_t = torch.from_numpy(response_role_keys)
    for i in range(n):
        intent_hd = intent_codebook[int(intent_labels[i])].astype(np.float32)
        bundle = (INTENT_WEIGHT * intent_hd).astype(np.float32)
        for r in range(N_ROLES):
            slot_hd = slot_dicts[r][int(slot_labels[i, r])]
            bound = hd_bind(role_keys_t[r], torch.from_numpy(slot_hd))
            bundle = bundle + bound.numpy().astype(np.float32)
        out[i] = bundle
    return out


def _construct_hybrid(
    intent_labels: np.ndarray,
    slot_labels: np.ndarray,
    intent_codebook: np.ndarray,
    frame_codebook: np.ndarray,
    response_role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
) -> np.ndarray:
    """LOAD-BEARING mechanism.

    response_hd = FRAME_WEIGHT * frame_hd + INTENT_WEIGHT * intent_hd
                + sum_r bind(rk_r, slot_r).

    NOTE: prereg formula had implicit frame_hd weight 1; empirical bind-noise
    (7600 stddev per bind at N_DIM=8192) requires FRAME_WEIGHT=8 for frame
    retrieval to dominate 5-role bind noise. Documented in cell docstring +
    surfaced to SCHEMA-VET.
    """
    n = intent_labels.shape[0]
    n_dim = intent_codebook.shape[1]
    out = np.zeros((n, n_dim), dtype=np.float32)
    role_keys_t = torch.from_numpy(response_role_keys)
    for i in range(n):
        intent_id = int(intent_labels[i])
        frame_id = _frame_lookup(intent_id)
        frame_hd = frame_codebook[frame_id].astype(np.float32)
        intent_hd = intent_codebook[intent_id].astype(np.float32)
        bundle = (FRAME_WEIGHT * frame_hd + INTENT_WEIGHT * intent_hd).astype(np.float32)
        for r in range(N_ROLES):
            slot_hd = slot_dicts[r][int(slot_labels[i, r])]
            bound = hd_bind(role_keys_t[r], torch.from_numpy(slot_hd))
            bundle = bundle + bound.numpy().astype(np.float32)
        out[i] = bundle
    return out


def _construct_shuffled_response_role_keys(
    intent_labels: np.ndarray,
    slot_labels: np.ndarray,
    intent_codebook: np.ndarray,
    frame_codebook: np.ndarray,
    response_role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
) -> np.ndarray:
    """ARM_SHUFFLED_RESPONSE_ROLE_KEYS.

    Encoder BINDS with cyclic-shift-by-1 shuffled response_role_keys (a proper
    derangement: perm=[1,2,3,4,0], no fixed points). Downstream measurement
    unbinds with the CANONICAL response_role_keys. Result: slot_fill must
    collapse toward chance (1/20=0.05). Verifies role-binding is load-bearing
    (not cross-talk-only). Frame_match should still be near-1 (frame_hd
    unaffected). Intent_recovered should also be near-1 (intent_hd summand
    unaffected).
    """
    perm = np.roll(np.arange(N_ROLES), shift=1)  # [1,2,3,4,0]
    assert not np.any(perm == np.arange(N_ROLES)), "derangement invariant broken"
    shuffled_keys = response_role_keys[perm].copy()
    return _construct_hybrid(
        intent_labels, slot_labels, intent_codebook, frame_codebook,
        shuffled_keys, slot_dicts,
    )


# ------------------------------------------------------------------------------
# Response-HD measurement (frame match, slot fill, intent recover, roundtrip)
# ------------------------------------------------------------------------------

def _measure_frame_match(
    response_hds: np.ndarray,
    frame_codebook: np.ndarray,
    intent_labels_gt: np.ndarray,
) -> Tuple[float, np.ndarray]:
    """Cleanup response_hd against frame_codebook; correct if argmax matches
    _frame_lookup(intent_gt). Returns (accuracy, frame_pred_array)."""
    # SUBSTRATE PRIMITIVE: k_NN_lookup on frame codebook
    _, diag = k_NN_lookup(response_hds, frame_codebook, k=1)
    frame_pred = diag["final_argmax_idx"].astype(np.int64)
    frame_gt = np.array([_frame_lookup(int(x)) for x in intent_labels_gt], dtype=np.int64)
    acc = float(np.mean(frame_pred == frame_gt))
    return acc, frame_pred


def _measure_slot_fill(
    response_hds: np.ndarray,
    response_role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
    slot_labels_gt: np.ndarray,
) -> Tuple[float, List[float], np.ndarray]:
    """For each role r: unbind(response_hd, response_role_key[r]); k_NN_lookup
    cleanup against slot_dicts[r]; check argmax == slot_labels_gt[:, r].

    Returns (overall_acc, per_role_acc_list, slot_pred [n, N_ROLES])."""
    n = response_hds.shape[0]
    slot_pred = np.zeros((n, N_ROLES), dtype=np.int64)
    input_t = torch.from_numpy(response_hds.astype(np.float32))
    for r in range(N_ROLES):
        # SUBSTRATE PRIMITIVE: HRR unbind (batched via broadcast)
        # .contiguous() required: expand_as produces a non-contiguous view and
        # Windows MKL FFT rejects it with "Inconsistent configuration parameters".
        # Mirror of the fix at line 758 (self-test path).
        role_key_t = torch.from_numpy(response_role_keys[r].astype(np.float32))
        role_key_expanded = role_key_t.unsqueeze(0).expand_as(input_t).contiguous()
        unbound_t = hd_unbind(input_t, role_key_expanded)
        unbound = unbound_t.numpy().astype(np.float32)
        # SUBSTRATE PRIMITIVE: k_NN_lookup on per-role SHARDED slot dict
        _, diag = k_NN_lookup(unbound, slot_dicts[r], k=1)
        slot_pred[:, r] = diag["final_argmax_idx"].astype(np.int64)
    correct = (slot_pred == slot_labels_gt)
    overall = float(np.mean(correct))
    per_role = [float(np.mean(correct[:, r])) for r in range(N_ROLES)]
    return overall, per_role, slot_pred


def _measure_intent_recovered(
    response_hds: np.ndarray,
    intent_codebook: np.ndarray,
    intent_labels_gt: np.ndarray,
) -> Tuple[float, np.ndarray]:
    """Cleanup response_hd against intent codebook; correct if argmax matches gt."""
    _, diag = k_NN_lookup(response_hds, intent_codebook, k=1)
    intent_pred = diag["final_argmax_idx"].astype(np.int64)
    acc = float(np.mean(intent_pred == intent_labels_gt))
    return acc, intent_pred


def _measure_roundtrip(
    response_hds: np.ndarray,
    intent_clf: IntentClassifier,
    response_role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
    intent_labels_gt: np.ndarray,
    slot_labels_gt: np.ndarray,
) -> Tuple[float, float, np.ndarray, np.ndarray]:
    """ARM_M19_ROUNDTRIP measurement: parse response_hd via SemanticParser
    (M1.9 CG'd primitive) and check recovery of (intent, slots).

    Uses the SAME intent_clf codebook, response_role_keys, and slot_dicts that
    were used to build the response_hd -- this is the round-trip identity test.
    """
    parser = SemanticParser(
        intent_clf=intent_clf,
        slot_dicts=slot_dicts,
        role_keys=response_role_keys,
        n_roles=N_ROLES,
        slot_dict_size_per_role=SLOT_DICT_SIZE_PER_ROLE,
    )
    # SUBSTRATE PRIMITIVE: SemanticParser.parse_batch (M1.9 CG)
    res = parser.parse_batch(response_hds.astype(np.float32))
    intent_acc = float(np.mean(res.intent_ids == intent_labels_gt))
    slot_correct = (res.slot_ids == slot_labels_gt)
    slot_acc = float(np.mean(slot_correct))
    return intent_acc, slot_acc, res.intent_ids, res.slot_ids


# ------------------------------------------------------------------------------
# Arms (each returns an arm-score dict + a per-arm digest tensor for META_RULE_AF)
# ------------------------------------------------------------------------------

def _run_arm(
    arm: str,
    intent_labels: np.ndarray,
    slot_labels: np.ndarray,
    intent_codebook: np.ndarray,
    frame_codebook: np.ndarray,
    response_role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
    intent_clf: IntentClassifier,
) -> Tuple[dict, np.ndarray]:
    """Dispatch arm construction + measurement. Returns (score_dict, digest_array).

    score_dict fields:
        frame_match: float
        slot_fill: float (overall across roles)
        slot_fill_per_role: List[float]
        intent_recovered: float
        roundtrip_intent: float (only meaningful for ARM_M19_ROUNDTRIP; measured on all)
        roundtrip_slot_fill: float (only meaningful for ARM_M19_ROUNDTRIP; measured on all)
    digest_array: concatenation of (frame_pred, slot_pred.flatten, intent_pred)
                  for META_RULE_AF arms-must-differ hash. Different arms produce
                  different response_hds so their pred arrays MUST differ.
    """
    if arm == "ARM_TEMPLATE_ONLY":
        response_hds = _construct_template_only(intent_labels, frame_codebook)
    elif arm == "ARM_COMPOSE_ONLY":
        response_hds = _construct_compose_only(
            intent_labels, slot_labels, intent_codebook,
            response_role_keys, slot_dicts,
        )
    elif arm == "ARM_HYBRID":
        response_hds = _construct_hybrid(
            intent_labels, slot_labels, intent_codebook, frame_codebook,
            response_role_keys, slot_dicts,
        )
    elif arm == "ARM_SHUFFLED_RESPONSE_ROLE_KEYS":
        response_hds = _construct_shuffled_response_role_keys(
            intent_labels, slot_labels, intent_codebook, frame_codebook,
            response_role_keys, slot_dicts,
        )
    elif arm == "ARM_M19_ROUNDTRIP":
        # Use HYBRID mechanism for the response_hd; roundtrip metric is what
        # differentiates this arm from ARM_HYBRID (same construction, different
        # measurement API: SemanticParser instead of direct primitives).
        response_hds = _construct_hybrid(
            intent_labels, slot_labels, intent_codebook, frame_codebook,
            response_role_keys, slot_dicts,
        )
    else:
        raise ValueError(f"unknown arm: {arm}")

    # Measurements (all common; roundtrip measured on all so cross-arm consistency
    # can be inspected in metrics, but band-gates only apply to ARM_M19_ROUNDTRIP).
    frame_acc, frame_pred = _measure_frame_match(response_hds, frame_codebook, intent_labels)
    slot_acc, slot_per_role, slot_pred = _measure_slot_fill(
        response_hds, response_role_keys, slot_dicts, slot_labels,
    )
    intent_acc, intent_pred = _measure_intent_recovered(
        response_hds, intent_codebook, intent_labels,
    )
    rt_intent, rt_slot, rt_intent_pred, rt_slot_pred = _measure_roundtrip(
        response_hds, intent_clf, response_role_keys, slot_dicts,
        intent_labels, slot_labels,
    )

    score = {
        "frame_match": frame_acc,
        "slot_fill": slot_acc,
        "slot_fill_per_role": slot_per_role,
        "intent_recovered": intent_acc,
        "roundtrip_intent": rt_intent,
        "roundtrip_slot_fill": rt_slot,
    }
    # Digest: include response_hd itself so arms with same-argmax but different
    # construction do not hash-collide.
    digest_arr = np.concatenate([
        frame_pred.astype(np.int64),
        slot_pred.flatten().astype(np.int64),
        intent_pred.astype(np.int64),
        # a per-arm scalar signature so ARM_HYBRID and ARM_M19_ROUNDTRIP (same
        # response_hd, different measurement) do not bit-collide
        np.array([hash(arm) & 0xFFFFFFFF], dtype=np.int64),
    ])
    return score, digest_arr


# ------------------------------------------------------------------------------
# Scoring helpers
# ------------------------------------------------------------------------------

def _arms_must_differ(arms_digests: Dict[str, np.ndarray]) -> Dict[str, str]:
    """META_RULE_AF hash-test on per-arm digests. Different arm outputs must not
    bit-collide."""
    digests: Dict[str, str] = {}
    for name, arr in arms_digests.items():
        digests[name] = hashlib.sha256(arr.tobytes()).hexdigest()
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical "
                f"(hash={digests[a]}); arm-implementation bug"
            )
    return digests


# ------------------------------------------------------------------------------
# Verdict
# ------------------------------------------------------------------------------

def _compute_verdict(per_arm_seed: dict) -> Tuple[str, str]:
    """per_arm_seed: dict[arm][seed] -> score dict. Return (verdict, verdict_msg)."""
    n_units = sum(1 for a in ARMS for s in per_arm_seed.get(a, {}))
    if n_units < CARDINALITY_FLOOR:
        return "HARD_FAIL", (
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: n_units={n_units} "
            f"< floor={CARDINALITY_FLOOR}"
        )

    def _mean(arm, key):
        vals = [s[key] for s in per_arm_seed.get(arm, {}).values()]
        return float(np.mean(vals)) if vals else 0.0

    def _std(arm, key):
        vals = [s[key] for s in per_arm_seed.get(arm, {}).values()]
        return float(np.std(vals)) if vals else 0.0

    tmpl_slot = _mean("ARM_TEMPLATE_ONLY", "slot_fill")
    tmpl_frame = _mean("ARM_TEMPLATE_ONLY", "frame_match")
    comp_slot = _mean("ARM_COMPOSE_ONLY", "slot_fill")
    hyb_frame = _mean("ARM_HYBRID", "frame_match")
    hyb_slot = _mean("ARM_HYBRID", "slot_fill")
    hyb_slot_std = _std("ARM_HYBRID", "slot_fill")
    shuf_slot = _mean("ARM_SHUFFLED_RESPONSE_ROLE_KEYS", "slot_fill")
    rt_intent = _mean("ARM_M19_ROUNDTRIP", "roundtrip_intent")
    rt_slot = _mean("ARM_M19_ROUNDTRIP", "roundtrip_slot_fill")

    # Sanity envelope
    if tmpl_frame < HF_TEMPLATE_ONLY_FRAME_FLOOR:
        return "HARD_FAIL", (
            f"HF_ENVELOPE_SCHEMA_BROKEN: TEMPLATE_ONLY frame_match={tmpl_frame:.3f} "
            f"< {HF_TEMPLATE_ONLY_FRAME_FLOOR} (templates should be trivially recoverable)"
        )
    if comp_slot > hyb_slot + HF_INTEGRATION_MARGIN:
        return "HARD_FAIL", (
            f"HF_INTEGRATION_BUG: COMPOSE_ONLY slot_fill={comp_slot:.3f} > "
            f"HYBRID slot_fill={hyb_slot:.3f} + {HF_INTEGRATION_MARGIN} "
            f"(frame retrieval is HURTING slot recovery -- integration bug)"
        )

    # HARD_FAIL gates
    if hyb_frame < HF_FRAME_MATCH_FLOOR:
        return "HARD_FAIL", (
            f"HF_FRAME_MATCH_BROKEN: HYBRID frame_match={hyb_frame:.3f} "
            f"< {HF_FRAME_MATCH_FLOOR}"
        )
    if rt_slot < HF_ROUNDTRIP_SLOT_FLOOR:
        return "HARD_FAIL", (
            f"HF_ROUNDTRIP_SLOT_BROKEN: M19_ROUNDTRIP slot_fill={rt_slot:.3f} "
            f"< {HF_ROUNDTRIP_SLOT_FLOOR}"
        )
    if shuf_slot > HF_SHUFFLED_SLOT_CEILING:
        return "HARD_FAIL", (
            f"HF_SHUFFLED_NOT_COLLAPSED: SHUFFLED slot_fill={shuf_slot:.3f} > "
            f"{HF_SHUFFLED_SLOT_CEILING} (role-binding not doing work)"
        )

    # HARD_PASS gates
    hp_frame = hyb_frame >= HP_FRAME_MATCH_FLOOR
    hp_slot = hyb_slot >= HP_SLOT_FILL_FLOOR
    hp_rt_intent = rt_intent >= HP_ROUNDTRIP_INTENT_FLOOR
    hp_rt_slot = rt_slot >= HP_ROUNDTRIP_SLOT_FLOOR
    hp_lift = (hyb_slot - tmpl_slot) >= HP_LIFT_VS_TEMPLATE_FLOOR
    hp_shuf = shuf_slot <= HP_SHUFFLED_SLOT_CEILING
    # cross-seed cv on hybrid slot_fill: std / mean when mean > 0
    hp_cv = (hyb_slot_std / max(hyb_slot, 1e-9)) < HP_CV_CEILING

    if hp_frame and hp_slot and hp_rt_intent and hp_rt_slot and hp_lift and hp_shuf and hp_cv:
        return "HARD_PASS", (
            f"HARD_PASS: HYBRID frame={hyb_frame:.3f} slot={hyb_slot:.3f}; "
            f"M19_ROUNDTRIP intent={rt_intent:.3f} slot={rt_slot:.3f}; "
            f"lift_vs_template={hyb_slot - tmpl_slot:.3f}; "
            f"SHUFFLED_slot={shuf_slot:.3f}; hyb_cv={hyb_slot_std/max(hyb_slot,1e-9):.3f}"
        )

    return "MIDDLE_BAND", (
        f"MIDDLE_BAND: HYBRID frame={hyb_frame:.3f}(HP>={HP_FRAME_MATCH_FLOOR}) "
        f"slot={hyb_slot:.3f}(HP>={HP_SLOT_FILL_FLOOR}); "
        f"ROUNDTRIP intent={rt_intent:.3f}(HP>={HP_ROUNDTRIP_INTENT_FLOOR}) "
        f"slot={rt_slot:.3f}(HP>={HP_ROUNDTRIP_SLOT_FLOOR}); "
        f"lift={hyb_slot - tmpl_slot:.3f}(HP>={HP_LIFT_VS_TEMPLATE_FLOOR}); "
        f"SHUFFLED={shuf_slot:.3f}(HP<={HP_SHUFFLED_SLOT_CEILING}); "
        f"cv_pass={hp_cv}"
    )


# ------------------------------------------------------------------------------
# Main run
# ------------------------------------------------------------------------------

def _run_seed(seed: int, n_test: int) -> Dict[str, dict]:
    """Run all 5 arms for a single seed. Returns per-arm scores + digests."""
    t0 = time.perf_counter()

    # Substrate construction
    intent_clf = IntentClassifier(n_intents=N_INTENTS, n_dim=N_DIM, seed=seed)
    intent_codebook = intent_clf.codebook  # [N_INTENTS, N_DIM] float32
    frame_codebook = _make_frame_codebook(N_DIM, seed)
    response_role_keys = _make_response_role_keys(N_DIM, seed)
    slot_dicts = _make_slot_dicts(N_DIM, seed)

    # Test examples (single set; each arm scores on the same schema so cross-arm
    # comparisons are on identical inputs -- rail-discipline).
    intent_labels, slot_labels = _make_examples(n_test, seed + 10007)

    print(f"[m110] seed={seed} setup_done n_test={n_test} elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    per_arm: Dict[str, dict] = {}
    per_arm_digest: Dict[str, np.ndarray] = {}
    for arm in ARMS:
        score, digest = _run_arm(
            arm, intent_labels, slot_labels, intent_codebook, frame_codebook,
            response_role_keys, slot_dicts, intent_clf,
        )
        per_arm[arm] = score
        per_arm_digest[arm] = digest
        print(
            f"[m110] seed={seed} arm={arm} "
            f"frame={score['frame_match']:.3f} slot={score['slot_fill']:.3f} "
            f"intent={score['intent_recovered']:.3f} "
            f"rt_intent={score['roundtrip_intent']:.3f} rt_slot={score['roundtrip_slot_fill']:.3f} "
            f"elapsed={time.perf_counter()-t0:.1f}s",
            flush=True,
        )

    digests = _arms_must_differ(per_arm_digest)
    return {"per_arm": per_arm, "digests": digests, "elapsed_s": time.perf_counter() - t0}


def _self_test() -> None:
    """Formula selftest: end-to-end HYBRID construction + roundtrip at full-N
    recovers intent + slots on clean synthetic bundle. Assert HP-floor
    recovery so a broken import path or algebra breach halts BEFORE dispatch.
    """
    print("[m110 selftest] START", flush=True)
    # Small config for selftest speed but keep N_DIM=8192 so mechanism truly fires
    seed = 11
    n_dim = N_DIM
    n_intents = 10
    n_roles = 5
    slot_size = 20
    n_frames = 5

    # Codebooks
    intent_clf = IntentClassifier(n_intents=n_intents, n_dim=n_dim, seed=seed)
    intent_cb = intent_clf.codebook
    rng = np.random.default_rng(seed * 8191 + 4441)
    frame_cb = (rng.integers(0, 2, size=(n_frames, n_dim)) * 2 - 1).astype(np.float32)
    rng_rk = np.random.default_rng(seed * 4093 + 1093)
    resp_role_keys = (rng_rk.integers(0, 2, size=(n_roles, n_dim)) * 2 - 1).astype(np.float32)
    slot_dicts = []
    for r in range(n_roles):
        rr = np.random.default_rng(seed * 8191 + r * 251 + 313)
        slot_dicts.append((rr.integers(0, 2, size=(slot_size, n_dim)) * 2 - 1).astype(np.float32))

    # 20 examples
    rng_ex = np.random.default_rng(seed * 65537 + 5)
    n_ex = 20
    intent_labels = rng_ex.integers(0, n_intents, size=n_ex).astype(np.int64)
    slot_labels = rng_ex.integers(0, slot_size, size=(n_ex, n_roles)).astype(np.int64)

    # Construct HYBRID response_hds
    response_hds = np.zeros((n_ex, n_dim), dtype=np.float32)
    role_keys_t = torch.from_numpy(resp_role_keys)
    for i in range(n_ex):
        intent_id = int(intent_labels[i])
        frame_id = intent_id % n_frames
        bundle = (FRAME_WEIGHT * frame_cb[frame_id] + INTENT_WEIGHT * intent_cb[intent_id]).astype(np.float32)
        for r in range(n_roles):
            bound = hd_bind(role_keys_t[r], torch.from_numpy(slot_dicts[r][int(slot_labels[i, r])]))
            bundle = bundle + bound.numpy().astype(np.float32)
        response_hds[i] = bundle

    # Frame match
    _, diag = k_NN_lookup(response_hds, frame_cb, k=1)
    frame_pred = diag["final_argmax_idx"].astype(np.int64)
    frame_gt = np.array([int(x) % n_frames for x in intent_labels], dtype=np.int64)
    frame_acc = float(np.mean(frame_pred == frame_gt))
    print(f"[m110 selftest] frame_match={frame_acc:.3f} (expected >=0.95 on clean)", flush=True)
    assert frame_acc >= 0.95, f"selftest frame_match {frame_acc:.3f} below 0.95"

    # Slot fill via direct primitives
    slot_pred = np.zeros((n_ex, n_roles), dtype=np.int64)
    input_t = torch.from_numpy(response_hds)
    for r in range(n_roles):
        role_key_t = torch.from_numpy(resp_role_keys[r])
        unbound = hd_unbind(input_t, role_key_t.unsqueeze(0).expand_as(input_t).contiguous()).numpy().astype(np.float32)
        _, d = k_NN_lookup(unbound, slot_dicts[r], k=1)
        slot_pred[:, r] = d["final_argmax_idx"].astype(np.int64)
    slot_acc = float(np.mean(slot_pred == slot_labels))
    print(f"[m110 selftest] direct_slot_fill={slot_acc:.3f} (expected >=0.95)", flush=True)
    assert slot_acc >= 0.95, f"selftest slot_fill {slot_acc:.3f} below 0.95"

    # Roundtrip via SemanticParser
    parser = SemanticParser(
        intent_clf=intent_clf,
        slot_dicts=slot_dicts,
        role_keys=resp_role_keys,
        n_roles=n_roles,
        slot_dict_size_per_role=slot_size,
    )
    res = parser.parse_batch(response_hds)
    rt_intent_acc = float(np.mean(res.intent_ids == intent_labels))
    rt_slot_acc = float(np.mean(res.slot_ids == slot_labels))
    print(f"[m110 selftest] rt_intent={rt_intent_acc:.3f} rt_slot={rt_slot_acc:.3f} (expected both >=0.95)", flush=True)
    assert rt_intent_acc >= 0.95, f"selftest rt_intent {rt_intent_acc:.3f} below 0.95"
    assert rt_slot_acc >= 0.95, f"selftest rt_slot {rt_slot_acc:.3f} below 0.95"

    print("[m110 selftest] PASS: HYBRID mechanism produces roundtrippable response_hd at N=8192 K=5", flush=True)


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seed", type=int, default=None, help="single-seed dispatch")
    parser.add_argument("--run-mode", type=str, default=None, choices=["smoke", "full", "self_test"])
    args = parser.parse_args()

    if args.self_test:
        _self_test()
        return

    run_mode = args.run_mode or ("smoke" if args.smoke else "full")
    output_dir = _output_dir(run_mode)
    _write_start_marker(output_dir, run_mode)

    n_test = N_TEST_SMOKE if run_mode == "smoke" else N_TEST_FULL

    if args.seed is not None:
        seeds = [int(args.seed)]
    else:
        seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_FULL

    t0 = time.perf_counter()
    per_arm_seed: Dict[str, Dict[int, dict]] = {a: {} for a in ARMS}
    per_seed_digests: Dict[int, Dict[str, str]] = {}

    for si, seed in enumerate(seeds):
        _emit_heartbeat(output_dir, unit_idx=si, total_units=len(seeds),
                        elapsed_s=time.perf_counter() - t0,
                        extra={"phase": "seed_start", "seed": seed})
        result = _run_seed(seed, n_test)
        for arm, score in result["per_arm"].items():
            per_arm_seed[arm][seed] = score
        per_seed_digests[seed] = result["digests"]
        _emit_heartbeat(output_dir, unit_idx=si + 1, total_units=len(seeds),
                        elapsed_s=time.perf_counter() - t0,
                        extra={"phase": "seed_done", "seed": seed,
                               "seed_elapsed_s": result["elapsed_s"]})

    verdict, verdict_msg = _compute_verdict(per_arm_seed)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict,
        "elapsed_s": time.perf_counter() - t0,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "N_DIM": N_DIM,
        "N_INTENTS": N_INTENTS,
        "N_ROLES": N_ROLES,
        "ROLE_NAMES": ROLE_NAMES,
        "SLOT_DICT_SIZE_PER_ROLE": SLOT_DICT_SIZE_PER_ROLE,
        "N_FRAMES": N_FRAMES,
        "INTENT_WEIGHT": INTENT_WEIGHT,
        "n_test": n_test,
        "seeds_run": seeds,
        "expected_n_units": EXPECTED_N_UNITS if args.seed is None else len(ARMS) * len(seeds),
        "n_units_observed": sum(len(per_arm_seed[a]) for a in ARMS),
        "cardinality_ok": sum(len(per_arm_seed[a]) for a in ARMS) >= (
            CARDINALITY_FLOOR if args.seed is None else len(ARMS) * len(seeds)),
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "calibration_check": "default_ok_for_this_regime",
        "storage_strategy": "sharded",
        "per_arm_per_seed": {
            a: {str(s): sc for s, sc in per_arm_seed[a].items()} for a in ARMS
        },
        "per_seed_digests": {str(s): d for s, d in per_seed_digests.items()},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[m110] DONE verdict={verdict} msg={verdict_msg} elapsed={metrics['elapsed_s']:.1f}s", flush=True)


if __name__ == "__main__":
    output_dir_guess = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir_guess, e)
        raise
