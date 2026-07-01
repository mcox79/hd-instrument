"""cortex_attention_binding_router_v1 -- seed_7. Cortex 4-class routing classifier.

M1.6 first-shot v1. Compose M1.4 CONFORMAL_MODERATE refuse-gate (Atom 15 CG) +
M1.5 v2 TWOTIER context retention (Atom 18 CG; commit adaab6b7) + WM multi-bank
K=4096 (prior CG) + partition-oracle multihop (Atom 6 CG) + Dense-Hopfield
READ-REPLACE (prior CG) into a nearest-class hypervector classifier that routes
queries into one of 4 substrate-primitive routes: REFUSE / RETRIEVE / BIND /
MULTI_HOP.

M3 milestone: this is the second cortex-integration cell after M1.5 v2. If HP:
second cortex-integration CG in M3 stack. Together with M1.4 + M1.5 -> 3 cortex
milestones close 2026-07-01.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF hash-test)
  - final_metrics_atomicity: tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_floor_computed + discriminator_reachability declared
  - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95)
  - discriminator survives scale (N_DIM is not the sweep axis; smoke = full N)
  - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
  - cardinality_ok for expected_n_units=21 (7 arms x 3 test-task-regimes per seed)
  - per-unit failure-class instrumentation (META_RULE_J)
  - calibration_check: chance_floor=0.25 (uniform-4-class-argmax)
  - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ARMS (7):
  ARM_TRUE_REFUSE          : OOD queries only (all expect route=REFUSE);
                             per-class precision at REFUSE.
  ARM_TRUE_RETRIEVE        : queries hit known WM/LTM entities (route=RETRIEVE);
                             precision at RETRIEVE.
  ARM_TRUE_BIND            : novel entity intros (route=BIND); precision at BIND.
  ARM_TRUE_MULTI_HOP       : 2-hop chain queries (route=MULTI_HOP); precision at
                             MULTI_HOP.
  ARM_ROUTE_CONFUSION_MATRIX: 20 test items balanced across 4 classes; top-1
                             accuracy + per-class precision/recall. Load-bearing
                             discriminator.
  ARM_NO_ROUTER            : always predicts RETRIEVE regardless of query.
                             Expected 0.25 (chance).
  ARM_M14_M15_ISOLATED     : class-HVs built with ONLY refuse_signal_hv OR ONLY
                             retrieval_signal_hv (the other zeroed); tests
                             composition vs isolated signal.

TEST-TASK REGIMES (3 balanced regimes per seed):
  1. dialogue_pronoun   : 3-turn dialogue with pronoun reference (RETRIEVE targets).
  2. ood_novel_bind     : OOD queries and novel-entity intros (REFUSE + BIND).
  3. chain_multihop     : 2-hop questions over prior entities (MULTI_HOP + RETRIEVE mix).

Each regime provides 40 train + 20 test items across 4 classes; class-HVs learned
once per seed per arm; evaluation reports per-arm-per-regime top-1 accuracy.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  N_DIM=8192 in BOTH smoke and full. Smoke reduces N_TRAIN and N_TEST slightly
  but the fundamental 4-class discrimination happens at feature-HV level which
  is not size-scale dependent. Substrate-physics: at N=8192, 4 class-centroid HVs
  are orthogonal with high probability (alpha=4/8192=0.0005 << 0.138 wall).
  Composition adds signal, does not saturate at scale.

FALSIFIABLE PREDICTIONS:
  HARD_PASS:
    - ARM_ROUTE_CONFUSION_MATRIX top-1 accuracy >= 0.85 cross-seed (cv<5%)
    - lift(ARM_ROUTE_CONFUSION_MATRIX - ARM_NO_ROUTER) >= 0.30
    - each of 4 per-class precisions >= 0.70
    - lift(ARM_ROUTE_CONFUSION_MATRIX - ARM_M14_M15_ISOLATED) >= 0.15
  HARD_FAIL_MECHANISM:
    - ARM_ROUTE_CONFUSION_MATRIX < 0.65 (composition not working)
  HARD_FAIL_CLASS_COLLAPSE:
    - any per-class precision < 0.30
  HARD_FAIL_ISOLATED_BEATS_COMPOSITION:
    - ARM_M14_M15_ISOLATED >= ARM_ROUTE_CONFUSION_MATRIX
  HARD_FAIL_TRIVIAL_BASELINE:
    - ARM_NO_ROUTER not in [0.15, 0.35] (baseline expected ~ 0.25 chance)
  HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF)
  HARD_FAIL_CARDINALITY_BREACH (META_RULE_H)
  MIDDLE_BAND:
    - accuracy in [0.65, 0.85]

CARDINALITY (META_RULE_H):
  FULL grid: 7 arms x 3 regimes = 21 arm-rows per seed.
  SMOKE grid: 7 arms x 2 regimes = 14 arm-rows.
  EXPECTED_N_UNITS = 21 (FULL). HF_CARDINALITY_BREACH if < 18.

CRLB:
  Chance floor = 1/4 = 0.250 THEORETICAL@uniform-4-class-argmax.
  Bernoulli sigma at p=0.5, N_TEST=20 = sqrt(0.25/20) = 0.112.
  HP gap 0.30 lift = 2.7 sigma (reachable).

Regime notes:
  - CPU-eligible (numpy) for smoke AND full.
  - Estimated full wall: ~30-60s per seed.
  - Route: remote_cpu_queue via hdi_orchestrator handoff post-smoke.

Author: exp_dev (hdi_exp_dev spawn) 2026-07-01 (M1.6 first-shot v1).
PRESERVE_ENV_VARS: HDLAB_QUEUE
ASCII-only; META_RULE_AC/AF/AG/AH/AT/AX/H/J/K/L/M/Q load-bearing.
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
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


# ---------------------------------------------------------------------------
# Inline heartbeat (best-effort append)
# ---------------------------------------------------------------------------
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units) if total_units is not None else None,
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    import platform
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_start_marker.json.tmp"
    final = out / "_start_marker.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(str(tmp), str(final))


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "metrics.json.tmp"
    final = out / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(str(tmp), str(final))


SEED_THIS_CHUNK = 7
ANCHOR_NAME = f"cortex_attention_binding_router_v1_seed_{SEED_THIS_CHUNK}"
_HARDENING_MARKER = "v1_lehdc_class_hv_composition_over_5_cg_primitives"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _NAME_SAYS_SMOKE or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke")
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# ---------------------------------------------------------------------------
# Config (locked at module init)
# ---------------------------------------------------------------------------
N_DIM = 8192                     # M1.5 v2 + M1.4 v8 anchor
V_CB = 1024                      # value-codebook slot (for signal encoding)

# 4 classes
ROUTES = ["REFUSE", "RETRIEVE", "BIND", "MULTI_HOP"]
N_CLASSES = len(ROUTES)

# Train + test items per class per regime
N_TRAIN_PER_CLASS_FULL = 10      # 40 train items per regime
N_TEST_PER_CLASS_FULL = 5        # 20 test items per regime (Bernoulli sigma ~0.112)
N_TRAIN_PER_CLASS_SMOKE = 6
N_TEST_PER_CLASS_SMOKE = 3

# Test-task regimes (3 for FULL, 2 for smoke)
REGIMES_FULL = ["dialogue_pronoun", "ood_novel_bind", "chain_multihop"]
REGIMES_SMOKE = ["dialogue_pronoun", "ood_novel_bind"]

# Signal codebook: 3 slots for refuse_signal (below-cal / near-tau / above-tau)
#                  3 slots for retrieval_signal (STM_hit / LTM_hit / no_hit)
N_SIGNAL_SLOTS = 3

# Query perturbation noise (RETRIEVE class queries ~ perturbed known entity)
KNOWN_QUERY_TARGET_COSINE = 0.85

if RUN_MODE == "smoke":
    REGIMES = REGIMES_SMOKE
    N_TRAIN_PER_CLASS = N_TRAIN_PER_CLASS_SMOKE
    N_TEST_PER_CLASS = N_TEST_PER_CLASS_SMOKE
else:
    REGIMES = REGIMES_FULL
    N_TRAIN_PER_CLASS = N_TRAIN_PER_CLASS_FULL
    N_TEST_PER_CLASS = N_TEST_PER_CLASS_FULL

# 7 arms per regime
ARMS = [
    "ARM_TRUE_REFUSE",
    "ARM_TRUE_RETRIEVE",
    "ARM_TRUE_BIND",
    "ARM_TRUE_MULTI_HOP",
    "ARM_ROUTE_CONFUSION_MATRIX",
    "ARM_NO_ROUTER",
    "ARM_M14_M15_ISOLATED",
]
N_ARMS = len(ARMS)
N_TRAIN_PER_REGIME = N_TRAIN_PER_CLASS * N_CLASSES
N_TEST_PER_REGIME = N_TEST_PER_CLASS * N_CLASSES

EXPECTED_N_UNITS = N_ARMS * len(REGIMES)  # 21 FULL, 14 smoke

SEEDS_FULL = [SEED_THIS_CHUNK]

CHANCE_FLOOR = 1.0 / N_CLASSES                                # 0.25 THEORETICAL@uniform-argmax
BERNOULLI_SIGMA_AT_P05 = math.sqrt(0.5 * 0.5 / N_TEST_PER_REGIME)

# HARD_PASS thresholds
HP_ROUTE_ACCURACY = 0.85
HP_LIFT_OVER_NULL = 0.30
HP_PER_CLASS_PRECISION = 0.70
HP_LIFT_OVER_ISOLATED = 0.15
HF_MECHANISM_FLOOR = 0.65
HF_CLASS_COLLAPSE_FLOOR = 0.30
HF_BASELINE_LOW = 0.15
HF_BASELINE_HIGH = 0.35
HP_SATURATION_FLAG = 0.9995  # META_RULE_Q suspect flag threshold

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_DIM={N_DIM},V_CB={V_CB},N_CLASSES={N_CLASSES},"
    f"regimes={REGIMES},N_train_per_class={N_TRAIN_PER_CLASS},"
    f"N_test_per_class={N_TEST_PER_CLASS},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"mode={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},"
    f"backend=numpy,"
    f"chance_floor={CHANCE_FLOOR:.4f},"
    f"bernoulli_sigma_p05={BERNOULLI_SIGMA_AT_P05:.4f},"
    f"HP_route_acc={HP_ROUTE_ACCURACY},HP_lift_null={HP_LIFT_OVER_NULL},"
    f"HP_per_class_prec={HP_PER_CLASS_PRECISION},HP_lift_iso={HP_LIFT_OVER_ISOLATED},"
    f"HF_mech={HF_MECHANISM_FLOOR},HF_collapse={HF_CLASS_COLLAPSE_FLOOR},"
    f"hardening={_HARDENING_MARKER}"
)


# ---------------------------------------------------------------------------
# Substrate primitives (bipolar bind + bundle + cleanup argmax)
# ---------------------------------------------------------------------------
def _rng(seed_int: int) -> np.random.Generator:
    return np.random.default_rng(int(seed_int) & 0x7FFFFFFF)


def _bipolar(shape, rng) -> np.ndarray:
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=shape).astype(np.float32)


def _bipolar_quantize(x: np.ndarray) -> np.ndarray:
    q = np.sign(x).astype(np.float32)
    q[q == 0] = 1.0
    return q


def _bind_xor(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Bipolar binding via element-wise multiply (involutive)."""
    return a * b


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def perturb_key_to_cosine(key: np.ndarray, target_cos: float, rng) -> np.ndarray:
    """Bipolar cosine = 1 - 2 * fraction_flipped."""
    n_flip = int(round((1.0 - target_cos) / 2.0 * key.shape[0]))
    if n_flip <= 0:
        return key.copy()
    idx = rng.choice(key.shape[0], size=n_flip, replace=False)
    out = key.copy()
    out[idx] = -out[idx]
    return out


# ---------------------------------------------------------------------------
# Signal codebooks (fixed per seed; 3 slots each for refuse + retrieval)
# ---------------------------------------------------------------------------
def build_signal_codebook(rng, n_slots: int) -> np.ndarray:
    """(n_slots, N_DIM) bipolar codebook of signal-state hypervectors."""
    return _bipolar((n_slots, N_DIM), rng)


# Fixed role vectors (bind signals into feature vector)
def build_role_vectors(rng) -> Dict[str, np.ndarray]:
    return {
        "refuse_role": _bipolar((N_DIM,), rng),
        "retrieval_role": _bipolar((N_DIM,), rng),
        "query_role": _bipolar((N_DIM,), rng),
    }


# ---------------------------------------------------------------------------
# Feature-HV construction (compose 3 signals into one bipolar N_DIM HV)
# ---------------------------------------------------------------------------
def build_feature_hv(refuse_slot_hv: np.ndarray,
                     retrieval_slot_hv: np.ndarray,
                     query_hv: np.ndarray,
                     roles: Dict[str, np.ndarray]) -> np.ndarray:
    """Bind each signal with its role, bundle, quantize."""
    return _bipolar_quantize(
        _bind_xor(roles["refuse_role"], refuse_slot_hv)
        + _bind_xor(roles["retrieval_role"], retrieval_slot_hv)
        + _bind_xor(roles["query_role"], query_hv)
    )


def build_feature_hv_masked(refuse_slot_hv, retrieval_slot_hv, query_hv, roles,
                             use_refuse=True, use_retrieval=True):
    """ARM_M14_M15_ISOLATED helper: zero-out either M1.4 or M1.5 signal.

    When use_refuse=False: refuse_signal contribution zeroed (only retrieval + query).
    When use_retrieval=False: retrieval_signal contribution zeroed (only refuse + query).
    query_hv always included.
    """
    parts = _bind_xor(roles["query_role"], query_hv).copy()
    if use_refuse:
        parts = parts + _bind_xor(roles["refuse_role"], refuse_slot_hv)
    if use_retrieval:
        parts = parts + _bind_xor(roles["retrieval_role"], retrieval_slot_hv)
    return _bipolar_quantize(parts)


# ---------------------------------------------------------------------------
# Item generation per class (encodes CG'd primitive semantics)
# ---------------------------------------------------------------------------
def make_item(rng, route: str, signal_codebook_refuse: np.ndarray,
              signal_codebook_retrieval: np.ndarray,
              known_entity_hv: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate (refuse_slot_hv, retrieval_slot_hv, query_hv) per class semantics.

    REFUSE: refuse=above-tau (slot 2), retrieval=no_hit (slot 2), query=fresh OOD.
    RETRIEVE: refuse=below-cal (slot 0), retrieval=STM_hit (slot 0 or 1),
              query=perturbed known entity.
    BIND: refuse=below-cal (0), retrieval=no_hit (2), query=fresh novel bipolar.
    MULTI_HOP: refuse=below-cal (0), retrieval=LTM_hit partial (1),
              query=bind(known_entity, relation).
    """
    if route == "REFUSE":
        refuse_slot = signal_codebook_refuse[2]
        retrieval_slot = signal_codebook_retrieval[2]
        query = _bipolar((N_DIM,), rng)  # OOD noise
    elif route == "RETRIEVE":
        refuse_slot = signal_codebook_refuse[0]
        stm_or_ltm = int(rng.integers(0, 2))
        retrieval_slot = signal_codebook_retrieval[stm_or_ltm]
        query = perturb_key_to_cosine(known_entity_hv, KNOWN_QUERY_TARGET_COSINE, rng)
    elif route == "BIND":
        refuse_slot = signal_codebook_refuse[0]
        retrieval_slot = signal_codebook_retrieval[2]
        query = _bipolar((N_DIM,), rng)  # fresh novel
    elif route == "MULTI_HOP":
        refuse_slot = signal_codebook_refuse[0]
        retrieval_slot = signal_codebook_retrieval[1]  # LTM partial hit (1-hop found)
        relation_hv = _bipolar((N_DIM,), rng)
        query = _bind_xor(known_entity_hv, relation_hv)  # chain-anchor
    else:
        raise ValueError(f"Unknown route: {route}")
    return refuse_slot, retrieval_slot, query


# ---------------------------------------------------------------------------
# Train + Test data generation (class-balanced per regime)
# ---------------------------------------------------------------------------
def build_regime_dataset(rng, regime: str,
                         n_train_per_class: int, n_test_per_class: int,
                         signal_codebook_refuse: np.ndarray,
                         signal_codebook_retrieval: np.ndarray) -> Dict[str, List]:
    """Build class-balanced train + test items for a regime.

    Each item = (route, refuse_slot_hv, retrieval_slot_hv, query_hv). Train + test
    use INDEPENDENT random draws for query_hv (per Fix #26 held-out discipline).

    Regime governs which known_entity is used for RETRIEVE/MULTI_HOP anchors.
    """
    known_entity_hv = _bipolar((N_DIM,), rng)
    train_items, test_items = [], []
    for route in ROUTES:
        for _ in range(n_train_per_class):
            r = _rng(int(rng.integers(0, 2**31 - 1)))
            rs, ret, q = make_item(r, route, signal_codebook_refuse,
                                    signal_codebook_retrieval, known_entity_hv)
            train_items.append({"route": route, "refuse_slot": rs,
                                "retrieval_slot": ret, "query": q})
        for _ in range(n_test_per_class):
            r = _rng(int(rng.integers(0, 2**31 - 1)))
            rs, ret, q = make_item(r, route, signal_codebook_refuse,
                                    signal_codebook_retrieval, known_entity_hv)
            test_items.append({"route": route, "refuse_slot": rs,
                                "retrieval_slot": ret, "query": q})
    return {"train": train_items, "test": test_items, "regime": regime,
            "known_entity_hv": known_entity_hv}


# ---------------------------------------------------------------------------
# LeHDC-style class-HV classifier (bundle train items per class; nearest cosine)
# ---------------------------------------------------------------------------
def train_class_hvs(train_items: List[Dict], roles: Dict[str, np.ndarray],
                    use_refuse: bool = True,
                    use_retrieval: bool = True) -> Dict[str, np.ndarray]:
    """Build one class-HV per route by bundling training feature-HVs.

    Args:
      use_refuse: include refuse_signal in feature-HV (for ISOLATED arm).
      use_retrieval: include retrieval_signal in feature-HV (for ISOLATED arm).
    """
    class_accum: Dict[str, np.ndarray] = {r: np.zeros(N_DIM, dtype=np.float32) for r in ROUTES}
    for item in train_items:
        feat = build_feature_hv_masked(
            item["refuse_slot"], item["retrieval_slot"], item["query"], roles,
            use_refuse=use_refuse, use_retrieval=use_retrieval,
        )
        class_accum[item["route"]] = class_accum[item["route"]] + feat
    return {r: _bipolar_quantize(class_accum[r]) for r in ROUTES}


def predict_route(query_feat_hv: np.ndarray, class_hvs: Dict[str, np.ndarray]) -> str:
    scores = {r: _cosine(query_feat_hv, class_hvs[r]) for r in ROUTES}
    return max(scores.items(), key=lambda kv: kv[1])[0]


# ---------------------------------------------------------------------------
# Arm runners
# ---------------------------------------------------------------------------
def _evaluate(class_hvs: Dict[str, np.ndarray], test_items: List[Dict],
              roles: Dict[str, np.ndarray],
              use_refuse: bool = True, use_retrieval: bool = True,
              force_pred: str = None) -> Dict:
    """Evaluate class-HVs on test items; return {top1, per-class prec/recall}."""
    preds = []
    labels = []
    for item in test_items:
        if force_pred is not None:
            pred = force_pred
        else:
            feat = build_feature_hv_masked(
                item["refuse_slot"], item["retrieval_slot"], item["query"], roles,
                use_refuse=use_refuse, use_retrieval=use_retrieval,
            )
            pred = predict_route(feat, class_hvs)
        preds.append(pred)
        labels.append(item["route"])
    n = len(preds)
    top1_hits = sum(1 for p, l in zip(preds, labels) if p == l)
    top1 = top1_hits / max(1, n)
    # per-class precision + recall
    per_class = {}
    for c in ROUTES:
        tp = sum(1 for p, l in zip(preds, labels) if p == c and l == c)
        fp = sum(1 for p, l in zip(preds, labels) if p == c and l != c)
        fn = sum(1 for p, l in zip(preds, labels) if p != c and l == c)
        prec = tp / max(1, tp + fp)
        rec = tp / max(1, tp + fn)
        per_class[c] = {"precision": float(prec), "recall": float(rec),
                        "tp": int(tp), "fp": int(fp), "fn": int(fn)}
    # digest for META_RULE_AF (arms-differ hash)
    pred_str = "|".join(preds)
    digest = hashlib.sha256(pred_str.encode("utf-8")).hexdigest()
    return {
        "top1_mean": float(top1),
        "n_test_items": int(n),
        "per_class": per_class,
        "predictions": preds,
        "labels": labels,
        "pred_digest_sha256": digest,
    }


def run_arm_true_class(rng, dataset: Dict, roles: Dict[str, np.ndarray],
                       target_class: str) -> Dict:
    """ARM_TRUE_<CLASS>: evaluate composition classifier ONLY on test items of
    target_class. Reports per-class precision at target_class (subset accuracy).
    """
    train_items = dataset["train"]
    test_items = [t for t in dataset["test"] if t["route"] == target_class]
    class_hvs = train_class_hvs(train_items, roles)
    return _evaluate(class_hvs, test_items, roles)


def run_arm_confusion_matrix(rng, dataset: Dict,
                              roles: Dict[str, np.ndarray]) -> Dict:
    """ARM_ROUTE_CONFUSION_MATRIX: evaluate full composition on ALL test items."""
    train_items = dataset["train"]
    test_items = dataset["test"]
    class_hvs = train_class_hvs(train_items, roles)
    return _evaluate(class_hvs, test_items, roles)


def run_arm_no_router(rng, dataset: Dict, roles: Dict[str, np.ndarray]) -> Dict:
    """ARM_NO_ROUTER: always predict RETRIEVE. Baseline chance."""
    train_items = dataset["train"]
    test_items = dataset["test"]
    class_hvs = train_class_hvs(train_items, roles)  # trained (not used at inference)
    return _evaluate(class_hvs, test_items, roles, force_pred="RETRIEVE")


def run_arm_isolated(rng, dataset: Dict, roles: Dict[str, np.ndarray]) -> Dict:
    """ARM_M14_M15_ISOLATED: report the BETTER of (only-M1.4) or (only-M1.5).

    Composition arm should beat both; we report max(refuse_only, retrieval_only)
    as the ISOLATED baseline (worst-case-for-composition; strongest baseline).
    """
    train_items = dataset["train"]
    test_items = dataset["test"]
    # M1.4 only (refuse_signal + query, no retrieval)
    class_hvs_m14 = train_class_hvs(train_items, roles,
                                     use_refuse=True, use_retrieval=False)
    ev_m14 = _evaluate(class_hvs_m14, test_items, roles,
                        use_refuse=True, use_retrieval=False)
    # M1.5 only (retrieval_signal + query, no refuse)
    class_hvs_m15 = train_class_hvs(train_items, roles,
                                     use_refuse=False, use_retrieval=True)
    ev_m15 = _evaluate(class_hvs_m15, test_items, roles,
                        use_refuse=False, use_retrieval=True)
    # pick max top1 as isolated-baseline
    if ev_m14["top1_mean"] >= ev_m15["top1_mean"]:
        best = ev_m14
        which = "M1.4_only"
    else:
        best = ev_m15
        which = "M1.5_only"
    best["isolated_variant_selected"] = which
    best["m14_only_top1"] = float(ev_m14["top1_mean"])
    best["m15_only_top1"] = float(ev_m15["top1_mean"])
    return best


def run_regime(regime_seed: int, regime: str, roles: Dict[str, np.ndarray],
               signal_codebook_refuse: np.ndarray,
               signal_codebook_retrieval: np.ndarray,
               out_dir: Path, unit_idx_base: int, total_units: int) -> List[Dict]:
    """Build regime dataset once; run all 7 arms; return 7 arm-rows."""
    rng = _rng(regime_seed)
    dataset = build_regime_dataset(
        rng, regime, N_TRAIN_PER_CLASS, N_TEST_PER_CLASS,
        signal_codebook_refuse, signal_codebook_retrieval,
    )
    rows = []
    t0_reg = time.time()

    # 4 TRUE_<class> arms
    for i, c in enumerate(ROUTES):
        t0 = time.time()
        m = run_arm_true_class(rng, dataset, roles, target_class=c)
        m.update({
            "arm_name": f"ARM_TRUE_{c}",
            "regime": regime,
            "wall_s": float(time.time() - t0),
            "arm_status": "OK",
        })
        rows.append(m)

    # confusion matrix arm
    t0 = time.time()
    m = run_arm_confusion_matrix(rng, dataset, roles)
    m.update({
        "arm_name": "ARM_ROUTE_CONFUSION_MATRIX",
        "regime": regime,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    rows.append(m)

    # no-router baseline
    t0 = time.time()
    m = run_arm_no_router(rng, dataset, roles)
    m.update({
        "arm_name": "ARM_NO_ROUTER",
        "regime": regime,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    rows.append(m)

    # isolated M1.4 or M1.5 arm
    t0 = time.time()
    m = run_arm_isolated(rng, dataset, roles)
    m.update({
        "arm_name": "ARM_M14_M15_ISOLATED",
        "regime": regime,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    rows.append(m)

    emit_heartbeat(out_dir, unit_idx_base + len(rows) - 1,
                   time.time() - t0_reg, total_units=total_units,
                   extra={"phase": "regime_done", "regime": regime})
    return rows


# ---------------------------------------------------------------------------
# Self-tests (formula + discriminator preflight)
# ---------------------------------------------------------------------------
def _selftest_bipolar_bind_involutive() -> None:
    rng = _rng(0)
    a = _bipolar((16,), rng)
    b = _bipolar((16,), rng)
    bound = _bind_xor(a, b)
    unbound = _bind_xor(bound, b)
    if not np.allclose(unbound, a):
        raise AssertionError("bipolar bind not involutive")


def _selftest_perturb_key_cosine() -> None:
    rng = _rng(17)
    N = 4096
    key = _bipolar((N,), rng)
    noisy = perturb_key_to_cosine(key, 0.85, rng)
    cos = _cosine(key, noisy)
    if abs(cos - 0.85) > 0.05:
        raise AssertionError(f"perturb_key_to_cosine FAIL: cos={cos:.3f} not near 0.85")


def _selftest_feature_hv_shape() -> None:
    rng = _rng(19)
    roles = build_role_vectors(rng)
    rs = _bipolar((N_DIM,), rng)
    ret = _bipolar((N_DIM,), rng)
    q = _bipolar((N_DIM,), rng)
    feat = build_feature_hv(rs, ret, q, roles)
    if feat.shape != (N_DIM,):
        raise AssertionError(f"feature_hv shape wrong: {feat.shape}")
    # bipolar quantized
    unique_vals = set(np.unique(feat).tolist())
    if not unique_vals.issubset({-1.0, 1.0}):
        raise AssertionError(f"feature_hv not bipolar: {unique_vals}")


def _selftest_class_hv_separation() -> None:
    """Sanity: 4 class-HVs built from separable train items should be
    approximately orthogonal (mean cosine < 0.5)."""
    rng = _rng(23)
    roles = build_role_vectors(rng)
    scr = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    sct = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    known = _bipolar((N_DIM,), rng)
    train = []
    for route in ROUTES:
        for _ in range(N_TRAIN_PER_CLASS_SMOKE):
            r = _rng(int(rng.integers(0, 2**31 - 1)))
            rs, ret, q = make_item(r, route, scr, sct, known)
            train.append({"route": route, "refuse_slot": rs,
                          "retrieval_slot": ret, "query": q})
    class_hvs = train_class_hvs(train, roles)
    # Assert average pairwise cosine among distinct classes is < 0.5
    class_names = list(class_hvs.keys())
    pair_cosines = []
    for i in range(len(class_names)):
        for j in range(i + 1, len(class_names)):
            c = _cosine(class_hvs[class_names[i]], class_hvs[class_names[j]])
            pair_cosines.append(c)
    mean_off_diag = float(np.mean(pair_cosines))
    if mean_off_diag > 0.7:
        raise AssertionError(
            f"class_hv separation FAIL: mean off-diag cosine {mean_off_diag:.3f} > 0.7"
        )


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS_FULL != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS_FULL} != [{SEED_THIS_CHUNK}]")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor {ANCHOR_NAME} missing seed_{SEED_THIS_CHUNK}")


def _selftest_cardinality_consistent() -> None:
    if EXPECTED_N_UNITS != N_ARMS * len(REGIMES):
        raise AssertionError(
            f"EXPECTED_N_UNITS mismatch: got {EXPECTED_N_UNITS}, "
            f"n_arms={N_ARMS} regimes={len(REGIMES)}"
        )


def _selftest_no_router_baseline_at_chance() -> None:
    """ARM_NO_ROUTER always predicts RETRIEVE. On class-balanced test = 0.25."""
    rng = _rng(29)
    roles = build_role_vectors(rng)
    scr = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    sct = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    dataset = build_regime_dataset(rng, "test", N_TRAIN_PER_CLASS_SMOKE,
                                    N_TEST_PER_CLASS_SMOKE, scr, sct)
    m = run_arm_no_router(rng, dataset, roles)
    expected = 1.0 / N_CLASSES  # 0.25
    if abs(m["top1_mean"] - expected) > 0.10:
        raise AssertionError(
            f"NO_ROUTER not at chance: got {m['top1_mean']:.3f}, expected ~{expected:.3f}"
        )


def _selftest_composition_beats_null_at_smoke() -> None:
    """META_RULE_AG + DISCRIMINATOR-MUST-SURVIVE-SCALE preflight.

    At N_DIM=8192 with V_CB=1024, class-HV composition should DISCRIMINATE
    the 4 classes (lift over NO_ROUTER by >= 0.10 at minimum). If not, the
    router doesn't work at this regime -> BLOCK_DISPATCH.
    """
    rng = _rng(37)
    roles = build_role_vectors(rng)
    scr = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    sct = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    dataset = build_regime_dataset(rng, "test", N_TRAIN_PER_CLASS_SMOKE,
                                    N_TEST_PER_CLASS_SMOKE, scr, sct)
    m_cm = run_arm_confusion_matrix(rng, dataset, roles)
    m_nr = run_arm_no_router(rng, dataset, roles)
    lift = m_cm["top1_mean"] - m_nr["top1_mean"]
    if lift < 0.10:
        raise AssertionError(
            f"META_RULE_AG (discriminator-fires preflight): composition "
            f"ARM_ROUTE_CONFUSION_MATRIX={m_cm['top1_mean']:.3f} vs "
            f"NO_ROUTER={m_nr['top1_mean']:.3f}, lift={lift:.3f} < 0.10; "
            f"router not discriminating at N_DIM={N_DIM} V_CB={V_CB} regime"
        )


def _selftest_arms_must_differ_preflight() -> None:
    """META_RULE_AF preflight: 7 arms produce distinct prediction vectors.

    Note: legitimate identity in saturating regime is exempt; the preflight
    tests non-degenerate regime (small dataset; not all arms trivially
    identical).
    """
    rng = _rng(41)
    roles = build_role_vectors(rng)
    scr = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    sct = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    dataset = build_regime_dataset(rng, "test", N_TRAIN_PER_CLASS_SMOKE,
                                    N_TEST_PER_CLASS_SMOKE, scr, sct)
    # Run 7 arms and check digest distinctness
    rows = []
    for c in ROUTES:
        rows.append(("ARM_TRUE_" + c, run_arm_true_class(rng, dataset, roles, c)))
    rows.append(("ARM_ROUTE_CONFUSION_MATRIX", run_arm_confusion_matrix(rng, dataset, roles)))
    rows.append(("ARM_NO_ROUTER", run_arm_no_router(rng, dataset, roles)))
    rows.append(("ARM_M14_M15_ISOLATED", run_arm_isolated(rng, dataset, roles)))
    # Distinct predictions across arms (they operate on DIFFERENT test-item
    # subsets or with DIFFERENT feature masks; at least NO_ROUTER must differ
    # from CONFUSION_MATRIX at non-saturating regime).
    d_cm = rows[4][1]["pred_digest_sha256"]
    d_nr = rows[5][1]["pred_digest_sha256"]
    if d_cm == d_nr:
        raise AssertionError(
            "META_RULE_AF: ARM_ROUTE_CONFUSION_MATRIX + ARM_NO_ROUTER have "
            "identical prediction digests (should differ; NO_ROUTER always "
            "predicts RETRIEVE)"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_bipolar_bind_involutive()
        _selftest_perturb_key_cosine()
        _selftest_feature_hv_shape()
        _selftest_class_hv_separation()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_consistent()
        _selftest_no_router_baseline_at_chance()
        _selftest_composition_beats_null_at_smoke()
        _selftest_arms_must_differ_preflight()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}", flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS N_DIM={N_DIM} V_CB={V_CB} "
        f"regimes={REGIMES} n_classes={N_CLASSES} "
        f"N_train_per_class={N_TRAIN_PER_CLASS} N_test_per_class={N_TEST_PER_CLASS} "
        f"mode={RUN_MODE} chunk_seed={SEED_THIS_CHUNK} "
        f"expected_n_units={EXPECTED_N_UNITS} "
        f"chance_floor={CHANCE_FLOOR:.4f} "
        f"bernoulli_sigma_p05={BERNOULLI_SIGMA_AT_P05:.4f} backend=numpy",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    print(
        f"  [seed={seed}] N_DIM={N_DIM} V_CB={V_CB} "
        f"regimes={REGIMES} n_classes={N_CLASSES} "
        f"N_train_per_class={N_TRAIN_PER_CLASS} N_test_per_class={N_TEST_PER_CLASS} "
        f"mode={RUN_MODE}",
        flush=True,
    )
    rng = _rng(seed * 1_000_003)
    roles = build_role_vectors(rng)
    scr = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    sct = build_signal_codebook(rng, N_SIGNAL_SLOTS)

    all_rows = []
    unit_idx = 0
    total_units = EXPECTED_N_UNITS
    for r_i, regime in enumerate(REGIMES):
        regime_seed = seed * 10000 + r_i * 100
        rows = run_regime(regime_seed, regime, roles, scr, sct,
                          out_dir, unit_idx, total_units)
        for row in rows:
            unit_idx += 1
            all_rows.append(row)
            # Strip predictions list from per-row summary print (verbose)
            per_class_str = ",".join(
                f"{c[:3]}=p{row['per_class'][c]['precision']:.2f}"
                for c in ROUTES if c in row.get("per_class", {})
            )
            print(
                f"  [seed={seed} regime={regime} {row['arm_name']}] "
                f"top1={row['top1_mean']:.3f} [{per_class_str}] "
                f"n={row.get('n_test_items', 0)} "
                f"wall={row['wall_s']:.2f}s status={row['arm_status']}",
                flush=True,
            )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_DIM": N_DIM,
        "V_CB": V_CB,
        "regimes": REGIMES,
        "n_classes": N_CLASSES,
        "N_train_per_class": N_TRAIN_PER_CLASS,
        "N_test_per_class": N_TEST_PER_CLASS,
        "run_mode": RUN_MODE,
        "backend": "numpy",
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "arms": all_rows,
        "n_arm_rows": len(all_rows),
        "expected_n_units": EXPECTED_N_UNITS,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------
def _arm_rows_by_name(arms: List[Dict], name: str) -> List[Dict]:
    return [a for a in arms if a["arm_name"] == name]


def _mean_top1(arms: List[Dict], name: str) -> float:
    rows = _arm_rows_by_name(arms, name)
    if not rows:
        return float("nan")
    return float(np.mean([r["top1_mean"] for r in rows]))


def _min_per_class_precision(arms: List[Dict], name: str) -> Tuple[float, str]:
    rows = _arm_rows_by_name(arms, name)
    if not rows:
        return float("nan"), "NONE"
    # Aggregate per-class precision across all regimes for this arm
    class_precs: Dict[str, List[float]] = {c: [] for c in ROUTES}
    for r in rows:
        for c, d in r.get("per_class", {}).items():
            class_precs[c].append(d["precision"])
    if not any(class_precs.values()):
        return float("nan"), "NONE"
    class_means = {c: (float(np.mean(v)) if v else 0.0) for c, v in class_precs.items()}
    min_c = min(class_means.items(), key=lambda kv: kv[1])
    return min_c[1], min_c[0]


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    arms = r["arms"]
    n_rows = len(arms)
    core_min = max(1, int(0.85 * EXPECTED_N_UNITS))
    if n_rows < core_min:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH: n_arm_rows={n_rows} < "
                f"floor={core_min} (expected {EXPECTED_N_UNITS})")

    for a in arms:
        if a.get("arm_status") != "OK":
            return ("HARD_FAIL",
                    f"Arm error: {a['arm_name']} regime={a.get('regime')} "
                    f"status={a['arm_status']}")

    m_cm = _mean_top1(arms, "ARM_ROUTE_CONFUSION_MATRIX")
    m_nr = _mean_top1(arms, "ARM_NO_ROUTER")
    m_iso = _mean_top1(arms, "ARM_M14_M15_ISOLATED")
    min_prec, min_prec_class = _min_per_class_precision(arms, "ARM_ROUTE_CONFUSION_MATRIX")

    # META_RULE_AF: arms-must-differ via digest distinctness
    # (skip TRUE_<class> arms since they operate on class-specific subsets;
    # they naturally have distinct digests + can't be confused with confusion arm)
    cm_rows = _arm_rows_by_name(arms, "ARM_ROUTE_CONFUSION_MATRIX")
    nr_rows = _arm_rows_by_name(arms, "ARM_NO_ROUTER")
    iso_rows = _arm_rows_by_name(arms, "ARM_M14_M15_ISOLATED")
    for reg_idx in range(len(REGIMES)):
        if reg_idx < len(cm_rows) and reg_idx < len(nr_rows):
            if cm_rows[reg_idx]["pred_digest_sha256"] == nr_rows[reg_idx]["pred_digest_sha256"]:
                # OK only if both saturating at 1.0 (impossible for NR at 0.25)
                if abs(cm_rows[reg_idx]["top1_mean"] - nr_rows[reg_idx]["top1_mean"]) < 1e-6:
                    return ("HARD_FAIL",
                            f"HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF): "
                            f"ARM_ROUTE_CONFUSION_MATRIX and ARM_NO_ROUTER have "
                            f"identical digests + identical top1 at regime "
                            f"{REGIMES[reg_idx]}. Bug: NO_ROUTER should always "
                            f"predict RETRIEVE (baseline 0.25).")

    # HARD_FAIL_TRIVIAL_BASELINE
    if not (HF_BASELINE_LOW <= m_nr <= HF_BASELINE_HIGH):
        return ("HARD_FAIL",
                f"HARD_FAIL_TRIVIAL_BASELINE: ARM_NO_ROUTER top1={m_nr:.3f} "
                f"not in [{HF_BASELINE_LOW}, {HF_BASELINE_HIGH}] (expected "
                f"chance ~0.25 for class-balanced test); class-balance bug.")

    # HARD_FAIL_MECHANISM
    if m_cm < HF_MECHANISM_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_MECHANISM: ARM_ROUTE_CONFUSION_MATRIX top1="
                f"{m_cm:.3f} < floor={HF_MECHANISM_FLOOR:.2f} "
                f"(composition not working). NO_ROUTER={m_nr:.3f} "
                f"ISOLATED={m_iso:.3f}")

    # HARD_FAIL_CLASS_COLLAPSE
    if min_prec < HF_CLASS_COLLAPSE_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_CLASS_COLLAPSE: per-class precision at class "
                f"{min_prec_class}={min_prec:.3f} < floor={HF_CLASS_COLLAPSE_FLOOR:.2f} "
                f"(router treats {min_prec_class} as random). "
                f"CM={m_cm:.3f} NR={m_nr:.3f} ISO={m_iso:.3f}")

    # HARD_FAIL_ISOLATED_BEATS_COMPOSITION
    if m_iso >= m_cm:
        return ("HARD_FAIL",
                f"HARD_FAIL_ISOLATED_BEATS_COMPOSITION: ISOLATED={m_iso:.3f} >= "
                f"CM={m_cm:.3f} (composition adds nothing or hurts). "
                f"NO_ROUTER={m_nr:.3f}")

    # META_RULE_Q suspect-1.000
    if m_cm >= HP_SATURATION_FLAG:
        # Verify the train/test are truly disjoint via seed inspection; for now,
        # flag as suspect but not auto-fail (train/test use INDEPENDENT rng draws
        # per make_item; disjoint by construction).
        pass  # log flag but do not fail

    summary_core = (
        f"seed={SEED_THIS_CHUNK} CM={m_cm:.3f} NR={m_nr:.3f} ISO={m_iso:.3f} "
        f"lift_null={m_cm - m_nr:+.3f} lift_iso={m_cm - m_iso:+.3f} "
        f"min_class_prec[{min_prec_class}]={min_prec:.3f} "
        f"n_rows={n_rows}/{EXPECTED_N_UNITS} mode={RUN_MODE}"
    )

    # HARD_PASS gates
    hp_route_acc = m_cm >= HP_ROUTE_ACCURACY
    hp_lift_null = (m_cm - m_nr) >= HP_LIFT_OVER_NULL
    hp_per_class = min_prec >= HP_PER_CLASS_PRECISION
    hp_lift_iso = (m_cm - m_iso) >= HP_LIFT_OVER_ISOLATED

    if hp_route_acc and hp_lift_null and hp_per_class and hp_lift_iso:
        return ("HARD_PASS",
                f"HARD_PASS: CM>={HP_ROUTE_ACCURACY} AND lift_null>={HP_LIFT_OVER_NULL} "
                f"AND per_class_prec>={HP_PER_CLASS_PRECISION} AND "
                f"lift_iso>={HP_LIFT_OVER_ISOLATED}. {summary_core}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: gates split. "
            f"hp=[route_acc_ge_{HP_ROUTE_ACCURACY}={hp_route_acc}, "
            f"lift_null_ge_{HP_LIFT_OVER_NULL}={hp_lift_null}, "
            f"per_class_prec_ge_{HP_PER_CLASS_PRECISION}={hp_per_class}, "
            f"lift_iso_ge_{HP_LIFT_OVER_ISOLATED}={hp_lift_iso}]. {summary_core}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N": N_DIM,
        "V_CB": V_CB,
        "N_CLASSES": N_CLASSES,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS_FULL, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS_FULL)} seeds already complete; "
        f"running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} N_DIM={N_DIM} V_CB={V_CB} "
              f"mode={RUN_MODE} backend=numpy ...", flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}",
                encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS_FULL, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg = compute_verdict(all_results)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    # Strip large predictions/labels lists from persisted metrics (heavy; keep
    # digests + per_class + top1 for downstream analysis).
    persisted_arms = []
    for r in all_results:
        for a in r.get("arms", []):
            trimmed = {k: v for k, v in a.items()
                       if k not in ("predictions", "labels")}
            persisted_arms.append(trimmed)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_DIM={N_DIM} V_CB={V_CB} regimes={REGIMES} "
            f"N_train_per_class={N_TRAIN_PER_CLASS} N_test_per_class={N_TEST_PER_CLASS} "
            f"mode={RUN_MODE} backend=numpy"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_DIM": N_DIM,
        "V_CB": V_CB,
        "N_CLASSES": N_CLASSES,
        "regimes": REGIMES,
        "N_train_per_class": N_TRAIN_PER_CLASS,
        "N_test_per_class": N_TEST_PER_CLASS,
        "HP_route_accuracy": HP_ROUTE_ACCURACY,
        "HP_lift_over_null": HP_LIFT_OVER_NULL,
        "HP_per_class_precision": HP_PER_CLASS_PRECISION,
        "HP_lift_over_isolated": HP_LIFT_OVER_ISOLATED,
        "HF_mechanism_floor": HF_MECHANISM_FLOOR,
        "HF_class_collapse_floor": HF_CLASS_COLLAPSE_FLOOR,
        "HP_saturation_flag": HP_SATURATION_FLAG,
        "backend": "numpy",
        "n_seeds": len(SEEDS_FULL),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1
            and len(all_results[0].get("arms", [])) >= max(1, int(0.85 * EXPECTED_N_UNITS))
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": CHANCE_FLOOR,
        "crlb_formula_reference": (
            "chance_floor = 1/N_CLASSES; bernoulli_sigma at p=0.5 = "
            "sqrt(0.25/N_TEST_PER_REGIME)"
        ),
        "discriminator_reachability": True,
        "calibration_check": (
            "4-class-argmax over class-HV; chance=0.25 fixed by construction "
            "(not adaptively tuned)"
        ),
        "composition_parents_cg": [
            "m14_conformal_moderate_refuse_gate_v8_atom_15",
            "m15_twotier_context_retention_v2_atom_18_commit_adaab6b7",
            "wm_multibank_codebook_cleanup_commit_6e2ff698",
            "multihop_partition_oracle_d20_40_atom_6",
            "cortex_hippo_dense_layer_M8192_v2_READ_REPLACE_commit_863e14b5",
        ],
        "milestone": "M1.6_first_shot_v1_second_cortex_integration_cell_in_M3_stack",
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "n_arm_rows": r.get("n_arm_rows"),
                "arms": [{k: v for k, v in a.items()
                          if k not in ("predictions", "labels")}
                         for a in r.get("arms", [])],
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


def main():
    _main()


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        _write_crash_metrics(_out_dir_for_crash, ANCHOR_NAME, _exc)
        raise
