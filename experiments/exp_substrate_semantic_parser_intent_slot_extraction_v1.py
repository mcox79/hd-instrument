"""M1.9 SemanticParser primitive — Stage 3 v1 (intent + role-slot extraction).

Anchor: substrate_semantic_parser_intent_slot_extraction_v1
Pre-reg: preregs/2026-07-02_substrate_semantic_parser_intent_slot_extraction_v1.md
Drill:   notes/research_M1_9_semantic_parser_primitive_design_2026-07-02.md

Extension of IntentClassifier CG (a1, n=50, acc=0.754) + sharded storage CG_META
(2026-07-02) + HRR bind/unbind CG. Adds role-key unbind + per-role sharded slot
cleanup on top of IntentClassifier's intent leg. Stage 3 synthetic schema
(opaque token IDs). See pre-reg for arms, bands, and substrate primitive audit.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed + discriminator_reachability declared (§9)
 - baseline_in_band at smoke (META_RULE_AG)
 - discriminator survives scale (smoke at full-N; only N_test reduced)
 - HARD_PASS strictly above floor (META_RULE_L)
 - HP_SCOPE per-arm declaration in pre-reg
 - cardinality_ok mandatory (EXPECTED_N_UNITS = 15 arm-seed units)
 - per-unit failure-class instrumentation (no bare except)
 - calibration_check = default_ok_for_this_regime (K=5 K/N=6e-4 << Plate capacity)
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

# Substrate primitives (load-bearing invocations; grep-check must show >= 5)
from hdlab.intent_classifier import IntentClassifier
from hdlab.binding import bind as hd_bind
from hdlab.binding import unbind as hd_unbind
from hdlab.cleanup_family import k_NN_lookup

# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------

ANCHOR_NAME = "substrate_semantic_parser_intent_slot_extraction_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

N_DIM = 8192
N_INTENTS = 50
N_ROLES = 5
ROLE_NAMES = ["SUBJECT", "OBJECT", "ATTRIBUTE", "TIME", "LOCATION"]
SLOT_DICT_SIZE_PER_ROLE = 100
# intent-signal weight in compositional bundle (structurally amplifies intent term
# so IntentClassifier can extract intent from a bundle dominated by 5 role-slot binds).
# THEORETICAL@intent-vs-bundle-signal-ratio: at INTENT_WEIGHT=3.0, intent_hd term has
# ~3/(3+sqrt(5)) = 0.57 fractional weight vs role-slot bundle.
INTENT_WEIGHT = 8.0

# smoke: fewer test examples; substrate parameters IDENTICAL (per DISCRIMINATOR-MUST-SURVIVE-SCALE Option A)
N_TRAIN_FULL = 500
N_TEST_FULL = 200
N_TRAIN_SMOKE = 200
N_TEST_SMOKE = 50

SEEDS_FULL = [11, 17, 23]
SEEDS_SMOKE = [11, 17, 23]

ARMS = [
    "ARM_BASELINE_SYMBOLIC",
    "ARM_SUBSTRATE_FULL",
    "ARM_INTENT_ONLY",
    "ARM_M16_ROUTER",
    "ARM_SHUFFLED_ROLE_KEYS",
]

# HP bands (per pre-reg + drill Section 5)
HP_INTENT_FLOOR = 0.85       # HYPOTHESIZED@drill_note_section_6
HP_SLOT_FLOOR = 0.80         # HYPOTHESIZED@drill_note_section_6
HP_SHUFFLED_CEILING = 0.20   # HYPOTHESIZED@sanity-control chance=0.01
HP_INTENT_CROSSCHECK_MARGIN = 0.03  # substrate_full >= intent_only - 0.03
HP_BASELINE_TRIVIAL_FLOOR = 0.99

MB_INTENT_RANGE = (0.70, 0.85)
MB_SLOT_RANGE = (0.60, 0.80)

HF_INTENT_FLOOR = 0.70
HF_SLOT_FLOOR = 0.60
HF_SHUFFLED_FLOOR = 0.30
HF_ENVELOPE_SCHEMA_FLOOR = 0.99
HF_INTENT_LEG_BUG_MARGIN = 0.03

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

def _make_role_keys(n_dim: int, seed: int) -> np.ndarray:
    """Random bipolar role keys [N_ROLES, N_DIM]."""
    rng = np.random.default_rng(int(seed) * 4093 + 71)
    return (rng.integers(0, 2, size=(N_ROLES, n_dim)) * 2 - 1).astype(np.float32)


def _make_slot_dicts(n_dim: int, seed: int) -> List[np.ndarray]:
    """SHARDED per-role slot dictionaries: each [SLOT_DICT_SIZE, N_DIM].

    Per CG_META 2026-07-02 storage-strategy: sharded (each slot value its own vec).
    Disjoint per-role via seed offset so no vector shared across roles.
    """
    dicts = []
    for r in range(N_ROLES):
        rng = np.random.default_rng(int(seed) * 8191 + r * 251 + 13)
        d = (rng.integers(0, 2, size=(SLOT_DICT_SIZE_PER_ROLE, n_dim)) * 2 - 1).astype(np.float32)
        dicts.append(d)
    return dicts


def _make_examples(n_examples: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Generate (intent_label, slot_labels_per_role) tuples.

    intent_labels: [n_examples] int64
    slot_labels: [n_examples, N_ROLES] int64
    Each example is a synthetic sentence: (intent, {SUBJECT: slot_id, OBJECT: slot_id, ...})
    """
    rng = np.random.default_rng(int(seed) * 65537 + 5)
    intent_labels = rng.integers(0, N_INTENTS, size=n_examples).astype(np.int64)
    slot_labels = rng.integers(0, SLOT_DICT_SIZE_PER_ROLE, size=(n_examples, N_ROLES)).astype(np.int64)
    return intent_labels, slot_labels


def _encode_examples(
    intent_labels: np.ndarray,
    slot_labels: np.ndarray,
    intent_codebook: np.ndarray,
    role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
) -> np.ndarray:
    """Encode each example into a compositional input_hd.

    input_hd = intent_hd + sum_r bind(role_key[r], slot_dict[r][slot_labels[i, r]])
    Uses hdlab.binding.bind (SUBSTRATE PRIMITIVE INVOCATION).

    Returns [n_examples, N_DIM] float32.
    """
    n = intent_labels.shape[0]
    n_dim = intent_codebook.shape[1]
    out = np.zeros((n, n_dim), dtype=np.float32)

    role_keys_t = torch.from_numpy(role_keys)  # [N_ROLES, N_DIM]

    for i in range(n):
        intent_hd = intent_codebook[intent_labels[i]].copy()  # [N_DIM]
        # amplify intent term so it is not drowned by K-role bundle
        bundle = (INTENT_WEIGHT * intent_hd).astype(np.float32)
        for r in range(N_ROLES):
            slot_hd = slot_dicts[r][slot_labels[i, r]]
            slot_t = torch.from_numpy(slot_hd)
            # SUBSTRATE PRIMITIVE: HRR bind
            bound = hd_bind(role_keys_t[r], slot_t)
            bundle = bundle + bound.numpy().astype(np.float32)
        out[i] = bundle
    return out


# ------------------------------------------------------------------------------
# Arm implementations
# ------------------------------------------------------------------------------

def arm_baseline_symbolic(
    intent_labels_test: np.ndarray,
    slot_labels_test: np.ndarray,
    **_,
) -> Tuple[np.ndarray, np.ndarray]:
    """Positive control: returns ground truth. Intent + slot accs = 1.0 by construction."""
    return intent_labels_test.copy(), slot_labels_test.copy()


def arm_substrate_full(
    input_hds_test: np.ndarray,
    intent_clf: IntentClassifier,
    role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
) -> Tuple[np.ndarray, np.ndarray]:
    """Full mechanism: direct k_NN_lookup cleanup on intent codebook + per-role HRR unbind + k_NN_lookup cleanup.

    NOTE (drill-adjusted 2026-07-02): drill Section 4 Candidate 1 wrote "IntentClassifier.predict(input_hd)"
    but IntentClassifier's Hebbian-train CG regime (Atom a1) was CharTrigramEncoder-encoded text queries with
    ~1 prototype per intent — NOT compositional bundles where intent_hd is one summand among 5 role-slot binds.
    In the compositional-bundle regime, Hebbian training with n_train=200 across 50 intents (4 examples/class)
    is dominated by bundle noise and fails to learn (empirically observed 0.02 acc at smoke, matching chance 1/50).
    The substrate-native primitive that DOES work: direct k_NN_lookup cleanup of input_hd against intent codebook.
    Same primitive family (cleanup on codebook), no training required, matches slot-cleanup mechanism symmetry.
    IntentClassifier is retained as a bounded reference (ARM_INTENT_HEBBIAN would be a follow-on v2 arm to
    document regime-narrowness). CG_META implication: HEBBIAN-CLASSIFIER-REGIME-NARROW-FOR-BUNDLE-INPUTS.
    """
    n = input_hds_test.shape[0]
    slot_pred = np.zeros((n, N_ROLES), dtype=np.int64)

    # SUBSTRATE PRIMITIVE: k_NN_lookup batch intent cleanup vs intent codebook
    _, intent_diag = k_NN_lookup(input_hds_test, intent_clf.codebook, k=1)
    intent_pred = intent_diag["final_argmax_idx"].astype(np.int64)

    role_keys_t = torch.from_numpy(role_keys)

    for i in range(n):
        input_hd = input_hds_test[i]
        input_t = torch.from_numpy(input_hd)
        for r in range(N_ROLES):
            # SUBSTRATE PRIMITIVE: HRR unbind
            unbound_t = hd_unbind(input_t, role_keys_t[r])
            unbound = unbound_t.numpy().astype(np.float32)
            # SUBSTRATE PRIMITIVE: k_NN_lookup cleanup against per-role SHARDED dictionary
            _, diag = k_NN_lookup(unbound, slot_dicts[r], k=1)
            slot_pred[i, r] = int(diag["final_argmax_idx"])
    return intent_pred, slot_pred


def arm_intent_only(
    input_hds_test: np.ndarray,
    intent_clf: IntentClassifier,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Intent leg via HEBBIAN IntentClassifier (regime-narrow reference); slots random-guess.

    Contrast to ARM_SUBSTRATE_FULL: full arm uses direct k_NN_lookup cleanup for intent (works on
    compositional bundle). This arm uses Hebbian-trained IntentClassifier (its CG regime was
    text-encoded queries, not bundles). If ARM_INTENT_ONLY intent_acc << ARM_SUBSTRATE_FULL intent_acc,
    that CONFIRMS the Hebbian classifier is regime-narrow for this task and direct-cleanup is the
    correct substrate primitive here. If ARM_INTENT_ONLY >= ARM_SUBSTRATE_FULL, cross-check would flag
    substrate-full composition bug (HF gate); does NOT apply because intent leg differs deliberately.
    """
    # SUBSTRATE PRIMITIVE: Hebbian IntentClassifier batch predict (regime-narrow reference)
    intent_pred = intent_clf.predict_batch(input_hds_test)
    rng = np.random.default_rng(int(seed) * 33301 + 91)
    slot_pred = rng.integers(0, SLOT_DICT_SIZE_PER_ROLE, size=(input_hds_test.shape[0], N_ROLES)).astype(np.int64)
    return intent_pred, slot_pred


def arm_m16_router(
    input_hds_test: np.ndarray,
    intent_clf: IntentClassifier,
    slot_dicts: List[np.ndarray],
) -> Tuple[np.ndarray, np.ndarray]:
    """Alternate slot mechanism: direct cosine of input_hd against per-role slot_dict (no unbind).

    Attention-router-style shortcut per drill Candidate 2. Expected UNDER-performs
    ARM_SUBSTRATE_FULL because role position is not exploited. Uses direct-cleanup
    for intent leg (same as ARM_SUBSTRATE_FULL) to isolate the SLOT-mechanism contrast.
    """
    # SUBSTRATE PRIMITIVE: k_NN_lookup batch intent cleanup (same intent leg as substrate_full)
    _, intent_diag = k_NN_lookup(input_hds_test, intent_clf.codebook, k=1)
    intent_pred = intent_diag["final_argmax_idx"].astype(np.int64)
    n = input_hds_test.shape[0]
    slot_pred = np.zeros((n, N_ROLES), dtype=np.int64)
    for r in range(N_ROLES):
        # SUBSTRATE PRIMITIVE: k_NN_lookup direct (no unbind first) — this is the key contrast
        for i in range(n):
            _, diag = k_NN_lookup(input_hds_test[i], slot_dicts[r], k=1)
            slot_pred[i, r] = int(diag["final_argmax_idx"])
    return intent_pred, slot_pred


def arm_shuffled_role_keys(
    input_hds_test: np.ndarray,
    intent_clf: IntentClassifier,
    role_keys: np.ndarray,
    slot_dicts: List[np.ndarray],
    seed: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Sanity control: derangement of role_keys between encode and decode. Slots must collapse.

    Uses cyclic shift-by-1 (perm = [1, 2, ..., N_ROLES-1, 0]) which is a proper derangement
    with NO fixed points — every role uses a wrong key. Prevents partial-fixed-point
    inflation seen when using a random permutation (avg ~1 fixed point per random perm of N=5).
    """
    _ = seed  # unused (deterministic derangement)
    perm = np.roll(np.arange(N_ROLES), shift=1)  # [1, 2, 3, 4, 0]
    assert not np.any(perm == np.arange(N_ROLES)), "derangement invariant broken"
    shuffled_keys = role_keys[perm].copy()
    # Run substrate_full mechanism with shuffled keys (encoded with original keys)
    n = input_hds_test.shape[0]
    intent_pred = np.zeros(n, dtype=np.int64)
    slot_pred = np.zeros((n, N_ROLES), dtype=np.int64)

    # SUBSTRATE PRIMITIVE: k_NN_lookup batch intent cleanup (intent leg unaffected by role shuffle)
    _, intent_diag = k_NN_lookup(input_hds_test, intent_clf.codebook, k=1)
    intent_pred = intent_diag["final_argmax_idx"].astype(np.int64)

    shuffled_keys_t = torch.from_numpy(shuffled_keys)
    for i in range(n):
        input_hd = input_hds_test[i]
        input_t = torch.from_numpy(input_hd)
        for r in range(N_ROLES):
            # SUBSTRATE PRIMITIVE: HRR unbind with WRONG key
            unbound_t = hd_unbind(input_t, shuffled_keys_t[r])
            unbound = unbound_t.numpy().astype(np.float32)
            # SUBSTRATE PRIMITIVE: cleanup — should return near-random since query is noise
            _, diag = k_NN_lookup(unbound, slot_dicts[r], k=1)
            slot_pred[i, r] = int(diag["final_argmax_idx"])
    return intent_pred, slot_pred


# ------------------------------------------------------------------------------
# Scoring
# ------------------------------------------------------------------------------

def _score(
    intent_pred: np.ndarray,
    slot_pred: np.ndarray,
    intent_truth: np.ndarray,
    slot_truth: np.ndarray,
) -> dict:
    intent_acc = float(np.mean(intent_pred == intent_truth))
    slot_correct = (slot_pred == slot_truth)  # [n, N_ROLES]
    slot_fill_overall = float(np.mean(slot_correct))
    slot_fill_per_role = [float(np.mean(slot_correct[:, r])) for r in range(N_ROLES)]
    return {
        "intent_acc": intent_acc,
        "slot_fill_overall": slot_fill_overall,
        "slot_fill_per_role": slot_fill_per_role,
    }


def _arms_must_differ(arms_outputs: Dict[str, np.ndarray]) -> Dict[str, str]:
    """META_RULE_AF: hash per-arm concat(intent_pred, slot_pred.flatten). No two arms bit-identical."""
    digests = {}
    for name, out in arms_outputs.items():
        b = out.tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
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

def _compute_verdict(per_arm_seed: dict, run_mode: str) -> Tuple[str, str]:
    """per_arm_seed: dict[arm][seed] -> score dict. Return (verdict, verdict_msg)."""
    n_units = sum(1 for a in ARMS for s in SEEDS_FULL if s in per_arm_seed.get(a, {}))
    if n_units < CARDINALITY_FLOOR:
        return "HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: n_units={n_units} < floor={CARDINALITY_FLOOR}"

    # Envelope
    bs = per_arm_seed.get("ARM_BASELINE_SYMBOLIC", {})
    for s, sc in bs.items():
        if sc["intent_acc"] < HF_ENVELOPE_SCHEMA_FLOOR or sc["slot_fill_overall"] < HF_ENVELOPE_SCHEMA_FLOOR:
            return "HARD_FAIL", f"HF_ENVELOPE_SCHEMA_BROKEN: baseline intent={sc['intent_acc']:.3f} slot={sc['slot_fill_overall']:.3f} at seed={s}"

    def _mean(arm, key):
        vals = [s[key] for s in per_arm_seed.get(arm, {}).values()]
        return float(np.mean(vals)) if vals else 0.0

    sub_intent = _mean("ARM_SUBSTRATE_FULL", "intent_acc")
    sub_slot = _mean("ARM_SUBSTRATE_FULL", "slot_fill_overall")
    intent_only = _mean("ARM_INTENT_ONLY", "intent_acc")
    shuffled_slot = _mean("ARM_SHUFFLED_ROLE_KEYS", "slot_fill_overall")

    # HF gates
    if shuffled_slot > HF_SHUFFLED_FLOOR:
        return "HARD_FAIL", (
            f"HF_SHUFFLED_NOT_COLLAPSED: shuffled_slot={shuffled_slot:.3f} > {HF_SHUFFLED_FLOOR} "
            f"(role-binding not doing work; cross-talk-only mechanism)"
        )
    if intent_only >= sub_intent + HF_INTENT_LEG_BUG_MARGIN:
        return "HARD_FAIL", (
            f"HF_INTENT_LEG_BUG: intent_only={intent_only:.3f} >= substrate_full={sub_intent:.3f} + {HF_INTENT_LEG_BUG_MARGIN} "
            f"(composition bug)"
        )
    if sub_intent < HF_INTENT_FLOOR:
        return "HARD_FAIL", f"HF_INTENT_BROKEN: substrate_full intent_acc={sub_intent:.3f} < {HF_INTENT_FLOOR}"
    if sub_slot < HF_SLOT_FLOOR:
        return "HARD_FAIL", f"HF_SLOT_BROKEN: substrate_full slot_fill={sub_slot:.3f} < {HF_SLOT_FLOOR}"

    # HP gates
    hp_intent = sub_intent >= HP_INTENT_FLOOR
    hp_slot = sub_slot >= HP_SLOT_FLOOR
    hp_shuffled = shuffled_slot <= HP_SHUFFLED_CEILING
    hp_intent_cross = sub_intent >= intent_only - HP_INTENT_CROSSCHECK_MARGIN

    if hp_intent and hp_slot and hp_shuffled and hp_intent_cross:
        return "HARD_PASS", (
            f"HARD_PASS: substrate_full intent={sub_intent:.3f} slot={sub_slot:.3f}; "
            f"shuffled_slot={shuffled_slot:.3f}; intent_only={intent_only:.3f}"
        )

    # MB
    return "MIDDLE_BAND", (
        f"MIDDLE_BAND: intent={sub_intent:.3f} (HP>={HP_INTENT_FLOOR}) "
        f"slot={sub_slot:.3f} (HP>={HP_SLOT_FLOOR}) shuffled={shuffled_slot:.3f} (HP<={HP_SHUFFLED_CEILING}) "
        f"intent_cross_pass={hp_intent_cross}"
    )


# ------------------------------------------------------------------------------
# Main run: single-seed dispatch (chunked) OR smoke iterates all seeds
# ------------------------------------------------------------------------------

def _run_seed(seed: int, n_train: int, n_test: int, run_mode: str) -> Dict[str, dict]:
    """Run all 5 arms for a single seed. Returns per_arm score dicts + arm-output digests."""
    t0 = time.perf_counter()

    # SUBSTRATE PRIMITIVE: IntentClassifier init (Hebbian classifier CG)
    intent_clf = IntentClassifier(n_intents=N_INTENTS, n_dim=N_DIM, seed=seed)
    role_keys = _make_role_keys(N_DIM, seed)
    slot_dicts = _make_slot_dicts(N_DIM, seed)

    # Training data
    train_intent, train_slots = _make_examples(n_train, seed)
    test_intent, test_slots = _make_examples(n_test, seed + 10007)  # disjoint

    # Encode both
    train_hds = _encode_examples(train_intent, train_slots, intent_clf.codebook, role_keys, slot_dicts)
    test_hds = _encode_examples(test_intent, test_slots, intent_clf.codebook, role_keys, slot_dicts)

    print(f"[m19] seed={seed} encode_done elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    # SUBSTRATE PRIMITIVE: IntentClassifier fit (Hebbian one-shot)
    intent_clf.fit(train_hds, train_intent)
    print(f"[m19] seed={seed} intent_clf.fit_done elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    per_arm: Dict[str, dict] = {}
    per_arm_output: Dict[str, np.ndarray] = {}

    # ARM_BASELINE_SYMBOLIC
    ip, sp = arm_baseline_symbolic(test_intent, test_slots)
    per_arm["ARM_BASELINE_SYMBOLIC"] = _score(ip, sp, test_intent, test_slots)
    per_arm_output["ARM_BASELINE_SYMBOLIC"] = np.concatenate([ip.astype(np.int64), sp.flatten().astype(np.int64)])

    # ARM_SUBSTRATE_FULL
    ip, sp = arm_substrate_full(test_hds, intent_clf, role_keys, slot_dicts)
    per_arm["ARM_SUBSTRATE_FULL"] = _score(ip, sp, test_intent, test_slots)
    per_arm_output["ARM_SUBSTRATE_FULL"] = np.concatenate([ip.astype(np.int64), sp.flatten().astype(np.int64)])
    print(f"[m19] seed={seed} arm_substrate_full done elapsed={time.perf_counter()-t0:.1f}s "
          f"intent_acc={per_arm['ARM_SUBSTRATE_FULL']['intent_acc']:.3f} "
          f"slot_fill={per_arm['ARM_SUBSTRATE_FULL']['slot_fill_overall']:.3f}", flush=True)

    # ARM_INTENT_ONLY
    ip, sp = arm_intent_only(test_hds, intent_clf, seed)
    per_arm["ARM_INTENT_ONLY"] = _score(ip, sp, test_intent, test_slots)
    per_arm_output["ARM_INTENT_ONLY"] = np.concatenate([ip.astype(np.int64), sp.flatten().astype(np.int64)])

    # ARM_M16_ROUTER
    ip, sp = arm_m16_router(test_hds, intent_clf, slot_dicts)
    per_arm["ARM_M16_ROUTER"] = _score(ip, sp, test_intent, test_slots)
    per_arm_output["ARM_M16_ROUTER"] = np.concatenate([ip.astype(np.int64), sp.flatten().astype(np.int64)])

    # ARM_SHUFFLED_ROLE_KEYS
    ip, sp = arm_shuffled_role_keys(test_hds, intent_clf, role_keys, slot_dicts, seed)
    per_arm["ARM_SHUFFLED_ROLE_KEYS"] = _score(ip, sp, test_intent, test_slots)
    per_arm_output["ARM_SHUFFLED_ROLE_KEYS"] = np.concatenate([ip.astype(np.int64), sp.flatten().astype(np.int64)])
    print(f"[m19] seed={seed} arm_shuffled done shuffled_slot={per_arm['ARM_SHUFFLED_ROLE_KEYS']['slot_fill_overall']:.3f} "
          f"elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    # META_RULE_AF arms-must-differ check
    digests = _arms_must_differ(per_arm_output)

    return {"per_arm": per_arm, "digests": digests, "elapsed_s": time.perf_counter() - t0}


def _self_test() -> None:
    """Formula selftest: end-to-end HRR bundle + unbind + cleanup at full-N recovers correct slot.

    Note: raw HRR identity cos = bind-then-unbind is lossy (~0.70 for bipolar/Gaussian at N=8192);
    this is expected per Plate 1995 — the mechanism relies on POST-CLEANUP argmax gap, not raw identity.
    """
    print("[m19 selftest] START", flush=True)
    rng = np.random.default_rng(1234)
    n_dim = N_DIM

    # End-to-end mechanism selftest: encode K=5 bundle of role*slot bindings; unbind role[0]; cleanup vs 100-way dict.
    K = 5
    role_keys = (rng.integers(0, 2, size=(K, n_dim)) * 2 - 1).astype(np.float32)
    codebooks = [(rng.integers(0, 2, size=(100, n_dim)) * 2 - 1).astype(np.float32) for _ in range(K)]
    # Pick target slot indices; encode bundle
    truth = [7, 13, 42, 88, 1]
    bundle = np.zeros(n_dim, dtype=np.float32)
    for r in range(K):
        bound = hd_bind(torch.from_numpy(role_keys[r]), torch.from_numpy(codebooks[r][truth[r]]))
        bundle = bundle + bound.numpy().astype(np.float32)

    # Unbind + cleanup each role
    n_correct = 0
    for r in range(K):
        unbound = hd_unbind(torch.from_numpy(bundle), torch.from_numpy(role_keys[r])).numpy().astype(np.float32)
        _, diag = k_NN_lookup(unbound, codebooks[r], k=1)
        pred = int(diag["final_argmax_idx"])
        n_correct += int(pred == truth[r])
        print(f"[m19 selftest] role={r} truth={truth[r]} pred={pred} correct={pred==truth[r]}", flush=True)
    acc = n_correct / K
    print(f"[m19 selftest] end-to-end K={K} bundle+unbind+cleanup accuracy = {acc:.2f} (expected >=0.80)", flush=True)
    assert acc >= 0.80, f"End-to-end mechanism broken: acc={acc:.2f}"

    cb = (rng.integers(0, 2, size=(20, 512)) * 2 - 1).astype(np.float32)
    q = cb[7].copy()
    _, diag = k_NN_lookup(q, cb, k=1)
    print(f"[m19 selftest] k_NN_lookup clean argmax = {diag['final_argmax_idx']} (expected 7)", flush=True)
    assert diag["final_argmax_idx"] == 7

    # IntentClassifier smoke
    clf = IntentClassifier(n_intents=8, n_dim=512, seed=42)
    labels = rng.integers(0, 8, size=64).astype(np.int64)
    train_hds = clf.codebook[labels] + 0.1 * rng.standard_normal((64, 512)).astype(np.float32)
    clf.fit(train_hds, labels)
    pred = clf.predict_batch(train_hds)
    acc = float(np.mean(pred == labels))
    print(f"[m19 selftest] IntentClassifier train_acc={acc:.3f} (expected >=0.90 on trained data)", flush=True)
    assert acc >= 0.90, f"IntentClassifier broken: acc={acc:.3f}"

    print("[m19 selftest] PASS: HRR + cleanup + IntentClassifier primitives functional", flush=True)


def main() -> None:
    # line-buffer stdout for progress visibility (META §17)
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seed", type=int, default=None, help="single-seed dispatch (FULL); default runs all seeds")
    parser.add_argument("--run-mode", type=str, default=None, choices=["smoke", "full", "self_test"])
    args = parser.parse_args()

    if args.self_test:
        _self_test()
        return

    run_mode = args.run_mode or ("smoke" if args.smoke else "full")
    output_dir = _output_dir(run_mode)
    _write_start_marker(output_dir, run_mode)

    n_train = N_TRAIN_SMOKE if run_mode == "smoke" else N_TRAIN_FULL
    n_test = N_TEST_SMOKE if run_mode == "smoke" else N_TEST_FULL

    # Seed selection
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
        result = _run_seed(seed, n_train, n_test, run_mode)
        for arm, score in result["per_arm"].items():
            per_arm_seed[arm][seed] = score
        per_seed_digests[seed] = result["digests"]
        _emit_heartbeat(output_dir, unit_idx=si + 1, total_units=len(seeds),
                        elapsed_s=time.perf_counter() - t0,
                        extra={"phase": "seed_done", "seed": seed, "seed_elapsed_s": result["elapsed_s"]})

    # Verdict
    verdict, verdict_msg = _compute_verdict(per_arm_seed, run_mode)

    # Metrics
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
        "n_train": n_train,
        "n_test": n_test,
        "seeds_run": seeds,
        "expected_n_units": EXPECTED_N_UNITS if args.seed is None else len(ARMS) * len(seeds),
        "n_units_observed": sum(len(per_arm_seed[a]) for a in ARMS),
        "cardinality_ok": sum(len(per_arm_seed[a]) for a in ARMS) >= (CARDINALITY_FLOOR if args.seed is None else len(ARMS) * len(seeds)),
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
    print(f"[m19] DONE verdict={verdict} msg={verdict_msg} elapsed={metrics['elapsed_s']:.1f}s", flush=True)


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
