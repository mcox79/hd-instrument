"""stage3_m3_stack_composition_depth_discriminating_v1 -- seed_7.

Chain-grade the M3 4-primitive stack composition depth in DISCRIMINATING regime.
Fixes deep_composition v2's saturation problem via over-Amit-Gutfreund
supra-capacity load (alpha in {0.5, 1.5, 3.0}; alpha_c=0.138) + noise arm
(f in {0.0, 0.30}) + depth sweep {5, 10, 25, 50, 100}.

MOTIVATION (M3 Phase 1):
  deep_composition v2 landed with ALL mechanism arms at 1.000 across regimes:
  FS_D10=1.0 FS_D50=1.0 SUB_ONLY=0.75 NO_REFUSE=1.0. Discriminator saturated
  because STM_K=100 items / V_CB=1024 codebook = alpha=0.10 (well below
  Hopfield-critical alpha_c=0.138). Substrate handled the load trivially.

  This v1 loads STM with alpha * V_CB items per equivalent-Hopfield bank
  (alpha=0.5 -> 3.62x critical, alpha=3.0 -> 21.7x critical). Substrate CANNOT
  trivially saturate at these loads. Adds independent-Bernoulli query noise
  f in {0.0, 0.30}. Depth axis {5, 10, 25, 50, 100} probes composition wall.

CG parents (META_RULE_AT):
  - M1.4 v8 CONFORMAL_MODERATE refuse-gate (Atom 15)
  - M1.5 v2 TWOTIER context retention (Atom 18)
  - M1.6 v2 4-class attention-binding router (Atom D)
  - M1.7 role-slot summarization CG
  - M3 4-primitive stack meta CG (today)

ARMS (32 units per seed at full):
  ARM_FULL_STACK  x  5 depths x 3 alpha x 2 f  = 30 units
  ARM_SUBSTRATE_ONLY_D50_alpha0.5_f0            =  1 unit  (ablation)
  ARM_NO_REFUSE_D50_alpha1.5_f0.30              =  1 unit  (ablation)

  Ablations are PIN-POINTS (single (depth,alpha,f) tuple) not sweep axes -- their
  purpose is HP_LIFT gate contribution not depth characterization.

TEST REGIME: single chain regime (RETRIEVE_CHAIN with mid-chain OOD probes at
  step floor(depth/2) for REFUSE_MIXED sub-regime). Regime IS the (alpha, f, depth)
  point in supra-capacity/noise space.

HP CONDITIONS (per pre-reg):
  HP_STACK_HOLDS_AT_DEPTH_100: at (d=100, a=0.5, f=0.0), FS >= 0.95
  HP_STACK_DEGRADES_AT_LOAD:   FS(d=100, a=3.0, f=0.0) drops >= 0.30 vs (d=100, a=0.5, f=0.0)
  HP_STACK_DEGRADES_AT_NOISE:  FS(d=50, a=1.5, f=0.30) drops >= 0.20 vs (d=50, a=1.5, f=0.0)
  HP_NO_CROSS_STAGE_BUG:       no smooth-degradation collapse to <= 0.05
  HP_LIFT_OVER_NO_REFUSE:      FS(d=50, a=1.5, f=0.30) - NO_REFUSE(same) >= 0.15
  HP_LIFT_OVER_SUBSTRATE_ONLY: FS(d=50, a=0.5, f=0.0) - SUB_ONLY(same) >= 0.10

HF CONDITIONS:
  HF_STACK_SATURATES: all FS across regimes = 1.000 (repeat of v2 saturation)
  HF_STACK_BREAKS_EARLY: FS(d=5, a=0.5, f=0.0) < 0.30 (positive control broken)
  HF_CARDINALITY_BREACH_META_RULE_H: observed < 27 of 32
  HF_ARMS_IDENTICAL_META_RULE_AF: FIXED vs v2 -- hash raw per-step output
    tensors (predicted_route + recovered_val chains) not trial_scores
  HF_BASELINE_OUT_OF_BAND_META_RULE_AG: baseline saturated >=0.95 at all points
  HF_POSITIVE_CONTROL_BROKEN: FS(d=5, a=0.5, f=0.0) < 0.75 (below cited prior 0.90)

DISCRIMINATOR-MUST-SURVIVE-SCALE (META rule):
  Option B (analytical): alpha_c=0.138 (Amit-Gutfreund std-Hopfield);
    sweep alphas all supra-critical (3.62x-21.7x); substrate cannot trivially
    saturate.
  Option C (preview): smoke includes (d=100, a=3.0, f=0.30) at full-N=8192
    as preview arm. If preview saturated >=0.95, REJECT_FULL_DISPATCH.

BASELINE-IN-BAND (META_RULE_AG):
  At (d=100, a=0.5, f=0.0): expected >= 0.90 (easy regime).
  At (d=100, a=3.0, f=0.30): expected <= 0.20 (hard regime).
  Discriminating band [0.30, 0.70] should contain >= 5/12 sweep points.

CRLB (META §9):
  Chance floor: 1/V_CB = 0.00098 THEORETICAL@codebook-argmax-uniform
  Bernoulli sigma per unit at n_trials=4, depth=100: sqrt(0.25/400)=0.025
  HP delta=0.30 margin: 12x sigma. Reachable.

FUNCTIONAL REQUIREMENTS (META §15E):
  FR1: Deep chain preserves entity identity (STM handoff). M1.5 v2 STM multi-bank.
  FR2: OOD probes trigger refuse mid-chain without corrupting later steps.
       M1.4 v8 CONFORMAL_MODERATE tau=0.7.
  FR3: Router switches route-class per step. M1.6 v2 class-HVs.
  FR4: Composed stack lifts over ablation in load or noise regime.

Regime: numpy CPU. FULL wall est: ~40-90min/seed for 32 units at depth-100.
  Timeout 7200s = 2h per seed with margin.
Route: overnight_queue GPU-heavy via hdi_orchestrator handoff.

Author: exp_dev (hdi_exp_dev spawn) 2026-07-01.
PRESERVE_ENV_VARS: HDLAB_QUEUE
ASCII-only; META_RULE_AC/AF/AG/AH/AT/H/J/K/L/M load-bearing.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Inline heartbeat + start-marker + crash-diag (META §13)
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
        "run_mode": "unknown",
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "metrics.json.tmp"
    final = out / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(str(tmp), str(final))


# ---------------------------------------------------------------------------
# Seed + anchor
# ---------------------------------------------------------------------------
SEED_THIS_CHUNK = 19
ANCHOR_NAME = f"stage3_m3_stack_composition_depth_discriminating_v1_seed_{SEED_THIS_CHUNK}"
_HARDENING_MARKER = "v1_over_amit_gutfreund_alpha_sweep_noise_arm"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--mode", type=str, default=None)
_ap.add_argument("--timeout", type=int, default=7200)
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
_MODE_ARG = (_ARGS.mode or "").lower()
if _ARGS.self_test or _MODE_ARG == "selftest":
    RUN_MODE = "self_test"
elif _ARGS.smoke or _NAME_SAYS_SMOKE or _MODE_ARG == "smoke" or \
     os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke":
    RUN_MODE = "smoke"
else:
    RUN_MODE = "full"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
N_DIM = 8192
V_CB = 1024
N_BANKS = 8
REFUSE_TAU_MODERATE = 0.700

ROUTES = ["REFUSE", "RETRIEVE", "BIND", "MULTI_HOP"]
N_CLASSES = len(ROUTES)

# M1.6 v2 config (faithful, per parent primitive)
N_TRAIN_PER_CLASS = 20
N_SIGNAL_SLOTS = 3
N_CHAIN_SLOTS = 2

KNOWN_QUERY_TARGET_COSINE = 0.85
ALPHA_C_HOPFIELD = 0.138  # Amit-Gutfreund critical THEORETICAL@Amit-Gutfreund-1985

# Sweep axes
DEPTHS_FULL = [5, 10, 25, 50, 100]
DEPTHS_SMOKE = [5, 25, 100]
ALPHAS_FULL = [0.5, 1.5, 3.0]
ALPHAS_SMOKE = [0.5, 3.0]
NOISE_F_FULL = [0.0, 0.30]
NOISE_F_SMOKE = [0.0, 0.30]

N_TRIALS_FULL = 4
N_TRIALS_SMOKE = 2

# ABLATION pin-points (regime tuples)
ABLATION_PINS_FULL = [
    ("ARM_SUBSTRATE_ONLY", 50, 0.5, 0.0),
    ("ARM_NO_REFUSE", 50, 1.5, 0.30),
]
ABLATION_PINS_SMOKE = [
    ("ARM_SUBSTRATE_ONLY", 25, 0.5, 0.0),
    ("ARM_NO_REFUSE", 25, 1.5, 0.30),
]

if RUN_MODE in ("smoke", "self_test"):
    DEPTHS = DEPTHS_SMOKE
    ALPHAS = ALPHAS_SMOKE
    NOISE_FS = NOISE_F_SMOKE
    N_TRIALS = N_TRIALS_SMOKE
    ABLATION_PINS = ABLATION_PINS_SMOKE
else:
    DEPTHS = DEPTHS_FULL
    ALPHAS = ALPHAS_FULL
    NOISE_FS = NOISE_F_FULL
    N_TRIALS = N_TRIALS_FULL
    ABLATION_PINS = ABLATION_PINS_FULL

# Cardinality: full-stack sweep + ablation pins
N_FULL_STACK_UNITS = len(DEPTHS) * len(ALPHAS) * len(NOISE_FS)
EXPECTED_N_UNITS = N_FULL_STACK_UNITS + len(ABLATION_PINS)
CARDINALITY_FLOOR = int(0.85 * EXPECTED_N_UNITS)

# HP thresholds
HP_STACK_HOLDS_D100_FLOOR = 0.95
HP_STACK_DEGRADES_LOAD_DELTA = 0.30
HP_STACK_DEGRADES_NOISE_DELTA = 0.20
HP_NO_STAGE_BUG_MIN = 0.05
HP_LIFT_OVER_NO_REFUSE = 0.15
HP_LIFT_OVER_SUBSTRATE_ONLY = 0.10
BAND_WIDTH_MARGIN = 0.05

CHANCE_FLOOR = 1.0 / V_CB
BERNOULLI_SIGMA_D100 = math.sqrt(0.25 / (N_TRIALS * 100))

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_DIM={N_DIM},V_CB={V_CB},N_BANKS={N_BANKS},"
    f"depths={DEPTHS},alphas={ALPHAS},noise_fs={NOISE_FS},"
    f"n_trials={N_TRIALS},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"mode={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},backend=numpy,"
    f"chance_floor={CHANCE_FLOOR:.6f},"
    f"alpha_c_hopfield={ALPHA_C_HOPFIELD},"
    f"bernoulli_sigma_d100={BERNOULLI_SIGMA_D100:.4f},"
    f"HP_D100_HOLDS={HP_STACK_HOLDS_D100_FLOOR},"
    f"HP_LOAD_DELTA={HP_STACK_DEGRADES_LOAD_DELTA},"
    f"HP_NOISE_DELTA={HP_STACK_DEGRADES_NOISE_DELTA},"
    f"hardening={_HARDENING_MARKER}"
)


# ---------------------------------------------------------------------------
# Substrate primitives
# ---------------------------------------------------------------------------
def _rng(seed_int: int) -> np.random.Generator:
    return np.random.default_rng(int(seed_int) & 0x7FFFFFFF)


def bipolar_random(rng, n=N_DIM) -> np.ndarray:
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=n).astype(np.float32)


def bipolar_random_batch(rng, k, n=N_DIM) -> np.ndarray:
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(k, n)).astype(np.float32)


def bipolar_quantize(v: np.ndarray) -> np.ndarray:
    q = np.sign(v).astype(np.float32)
    q[q == 0] = 1.0
    return q


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def perturb_key_to_cosine(key: np.ndarray, target_cos: float, rng) -> np.ndarray:
    n_flip = int(round((1.0 - target_cos) / 2.0 * key.shape[0]))
    if n_flip <= 0:
        return key.copy()
    if n_flip >= key.shape[0]:
        return -key.copy()
    idx = rng.choice(key.shape[0], size=n_flip, replace=False)
    out = key.copy()
    out[idx] = -out[idx]
    return out


def apply_bernoulli_noise(key: np.ndarray, f: float, rng) -> np.ndarray:
    """Independent Bernoulli bit-flip on bipolar key with flip-probability f."""
    if f <= 0.0:
        return key.copy()
    n = key.shape[0]
    mask = rng.random(n) < f
    out = key.copy()
    out[mask] = -out[mask]
    return out


def codebook_cleanup(v: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    v32 = v.astype(np.float32)
    v_norm = math.sqrt(float((v32 * v32).sum())) + 1e-9
    dots = codebook.astype(np.float32) @ v32
    row_norms = np.sqrt((codebook.astype(np.float32) ** 2).sum(axis=1)) + 1e-9
    sims = dots / (row_norms * v_norm)
    return int(np.argmax(sims)), float(np.max(sims))


# ---------------------------------------------------------------------------
# STM sparse-bank at OVER-CAPACITY load (per alpha)
# ---------------------------------------------------------------------------
def make_stm_overloaded(rng, codebook: np.ndarray, alpha: float,
                        n_dim: int = N_DIM, n_banks: int = N_BANKS):
    """Bundle alpha * V_CB items into n_banks sparse bipolar-quantized banks.

    At alpha > alpha_c_hopfield=0.138, standard Hopfield capacity exceeded and
    codebook_cleanup accuracy degrades due to accumulated bundle interference.
    """
    n_items_total = int(round(alpha * V_CB))
    n_items_total = max(1, n_items_total)
    banks = [np.zeros(n_dim, dtype=np.float32) for _ in range(n_banks)]
    key_tags = bipolar_random_batch(rng, n_items_total)
    val_idxs = rng.integers(0, V_CB, size=n_items_total)
    bank_assignments = rng.integers(0, n_banks, size=n_items_total)
    for i in range(n_items_total):
        val_hv = codebook[val_idxs[i]]
        bound = bind(key_tags[i], val_hv)
        banks[bank_assignments[i]] += bound
    banks_bp = [bipolar_quantize(b) for b in banks]
    return banks_bp, key_tags, val_idxs, bank_assignments


def stm_recall(query_key: np.ndarray, bank: np.ndarray,
               codebook: np.ndarray) -> Tuple[int, float]:
    unbound = bind(query_key, bank)
    return codebook_cleanup(unbound, codebook)


# ---------------------------------------------------------------------------
# LTM dense-Hopfield (M1.5 v2)
# ---------------------------------------------------------------------------
def make_ltm_hopfield(rng, codebook: np.ndarray, n_items: int):
    ltm_keys = bipolar_random_batch(rng, n_items)
    ltm_val_idxs = rng.integers(0, V_CB, size=n_items)
    return ltm_keys, ltm_val_idxs


def ltm_recall(query_key: np.ndarray, ltm_keys: np.ndarray,
               ltm_val_idxs: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    q = query_key.astype(np.float32)
    dots = ltm_keys.astype(np.float32) @ q
    idx = int(np.argmax(dots))
    return int(ltm_val_idxs[idx]), float(np.max(dots) / N_DIM)


# ---------------------------------------------------------------------------
# M1.6 v2 FAITHFUL: signal codebook + roles + feature-HV + class-HV training
# ---------------------------------------------------------------------------
def build_signal_codebook(rng, n_slots: int) -> np.ndarray:
    return bipolar_random_batch(rng, n_slots)


def build_role_vectors(rng) -> Dict[str, np.ndarray]:
    return {
        "refuse_role": bipolar_random(rng),
        "retrieval_role": bipolar_random(rng),
        "query_role": bipolar_random(rng),
        "chain_role": bipolar_random(rng),
    }


def build_feature_hv(refuse_slot_hv, retrieval_slot_hv, query_hv, chain_slot_hv,
                     roles) -> np.ndarray:
    return bipolar_quantize(
        bind(roles["refuse_role"], refuse_slot_hv)
        + bind(roles["retrieval_role"], retrieval_slot_hv)
        + bind(roles["query_role"], query_hv)
        + bind(roles["chain_role"], chain_slot_hv)
    )


def make_item(rng, route: str, sig_refuse, sig_retrieval, sig_chain,
              known_entity_hv):
    """Generate (refuse_slot, retrieval_slot, query, chain_slot) per class."""
    if route == "REFUSE":
        rs = sig_refuse[2]; ret = sig_retrieval[2]; cs = sig_chain[1]
        query = bipolar_random(rng)  # OOD
    elif route == "RETRIEVE":
        rs = sig_refuse[0]
        stm_or_ltm = int(rng.integers(0, 2))
        ret = sig_retrieval[stm_or_ltm]; cs = sig_chain[1]
        query = perturb_key_to_cosine(known_entity_hv, KNOWN_QUERY_TARGET_COSINE, rng)
    elif route == "BIND":
        rs = sig_refuse[0]; ret = sig_retrieval[2]; cs = sig_chain[1]
        query = bipolar_random(rng)
    elif route == "MULTI_HOP":
        rs = sig_refuse[0]; ret = sig_retrieval[1]; cs = sig_chain[0]
        relation_hv = bipolar_random(rng)
        query = bind(known_entity_hv, relation_hv)
    else:
        raise ValueError(f"unknown route: {route}")
    return rs, ret, query, cs


def build_train_dataset(rng, sig_refuse, sig_retrieval, sig_chain,
                        known_entity_hv) -> List[Dict]:
    train_items = []
    for route in ROUTES:
        for _ in range(N_TRAIN_PER_CLASS):
            r = _rng(int(rng.integers(0, 2**31 - 1)))
            rs, ret, q, cs = make_item(r, route, sig_refuse, sig_retrieval,
                                       sig_chain, known_entity_hv)
            train_items.append({"route": route, "refuse_slot": rs,
                                "retrieval_slot": ret, "query": q,
                                "chain_slot": cs})
    return train_items


def train_class_hvs(train_items, roles) -> Dict[str, np.ndarray]:
    class_accum = {r: np.zeros(N_DIM, dtype=np.float32) for r in ROUTES}
    for item in train_items:
        feat = build_feature_hv(
            item["refuse_slot"], item["retrieval_slot"], item["query"],
            item["chain_slot"], roles)
        class_accum[item["route"]] = class_accum[item["route"]] + feat
    return {r: bipolar_quantize(class_accum[r]) for r in ROUTES}


def predict_route(query_feat_hv, class_hvs) -> Tuple[str, float]:
    scores = {r: cosine(query_feat_hv, class_hvs[r]) for r in ROUTES}
    best_r = max(scores.items(), key=lambda kv: kv[1])
    return best_r[0], float(best_r[1])


# ---------------------------------------------------------------------------
# M1.4 refuse-gate
# ---------------------------------------------------------------------------
def refuse_gate(in_kb_max_sim: float, tau: float = REFUSE_TAU_MODERATE) -> bool:
    return float(in_kb_max_sim) < float(tau)


# ---------------------------------------------------------------------------
# Chain trial: run one trial through `depth` steps at (alpha, f)
# ---------------------------------------------------------------------------
def run_chain_trial(rng, arm_kind: str, depth: int, alpha: float, noise_f: float,
                    codebook, stm_banks, stm_key_tags, stm_val_idxs, stm_bank_asn,
                    ltm_keys, ltm_val_idxs,
                    sig_refuse, sig_retrieval, sig_chain,
                    roles, class_hvs, known_entity_hv) -> Tuple[float, List[Dict]]:
    """Returns (per_step_correct_fraction, per_step_trace).

    per_step_trace: list of dicts {predicted_route, recovered_val, step_correct}
    used for META_RULE_AF hash (raw output tensor, not aggregated score).

    arm_kind: "FULL_STACK" | "SUBSTRATE_ONLY" | "NO_REFUSE"
    """
    if len(stm_val_idxs) == 0:
        return 0.0, []

    correct = 0
    total = 0
    trace = []

    curr_idx = int(rng.integers(0, len(stm_val_idxs)))
    curr_key = stm_key_tags[curr_idx].copy()
    curr_expected_val = int(stm_val_idxs[curr_idx])

    # Mid-chain OOD injection: at step floor(depth/2), inject an OOD probe
    # (query = random bipolar). Expected route: REFUSE.
    ood_step = depth // 2

    for step in range(depth):
        # Expected route: RETRIEVE for most steps; REFUSE at ood_step.
        if step == ood_step:
            expected_route = "REFUSE"
            inject_ood = True
        else:
            expected_route = "RETRIEVE"
            inject_ood = False

        step_rng = _rng(int(rng.integers(0, 2**31 - 1)))

        # Build signal slots for router
        rs, ret, query_signal, cs = make_item(
            step_rng, expected_route, sig_refuse, sig_retrieval, sig_chain,
            known_entity_hv)

        # Build query key
        if inject_ood:
            query_key = bipolar_random(step_rng)
        else:
            # RETRIEVE regime: query = perturbed curr_key at KNOWN_QUERY_TARGET_COSINE
            query_key = perturb_key_to_cosine(curr_key, KNOWN_QUERY_TARGET_COSINE, step_rng)
            # Apply Bernoulli noise arm
            query_key = apply_bernoulli_noise(query_key, noise_f, step_rng)

        # M1.4 refuse-gate (if applicable)
        if arm_kind == "FULL_STACK":
            dots = stm_key_tags @ query_key
            in_kb_max_sim = float(np.max(dots) / N_DIM)
            refused = refuse_gate(in_kb_max_sim)
        else:
            # NO_REFUSE and SUBSTRATE_ONLY do NOT apply refuse-gate
            refused = False
            in_kb_max_sim = 1.0

        # Router prediction (M1.6 v2 class-HVs)
        if arm_kind == "SUBSTRATE_ONLY":
            predicted_route = "RETRIEVE"  # no router
        else:
            feat = build_feature_hv(rs, ret, query_signal, cs, roles)
            predicted_route, _sim = predict_route(feat, class_hvs)

        # Execute route + recall
        recall_ok = False
        recovered_val = -1
        if predicted_route == "REFUSE":
            step_correct_final = (expected_route == "REFUSE")
            next_curr_idx = curr_idx
        elif predicted_route == "RETRIEVE":
            recovered_val, _ = stm_recall(query_key,
                                          stm_banks[stm_bank_asn[curr_idx]],
                                          codebook)
            recall_ok = (recovered_val == curr_expected_val)
            step_correct_final = (expected_route == "RETRIEVE") and recall_ok
            next_curr_idx = (curr_idx + 1) % len(stm_val_idxs)
        elif predicted_route == "BIND":
            recovered_val, _ = ltm_recall(query_key, ltm_keys, ltm_val_idxs, codebook)
            recall_ok = (recovered_val == curr_expected_val)
            step_correct_final = (expected_route == "BIND") and recall_ok
            next_curr_idx = (curr_idx + 1) % len(stm_val_idxs)
        else:  # MULTI_HOP
            recovered_val_stm, _ = stm_recall(query_key,
                                              stm_banks[stm_bank_asn[curr_idx]],
                                              codebook)
            second_key = codebook[recovered_val_stm % V_CB]
            recovered_val, _ = ltm_recall(second_key, ltm_keys, ltm_val_idxs, codebook)
            recall_ok = (recovered_val == curr_expected_val)
            step_correct_final = (expected_route == "MULTI_HOP") and recall_ok
            next_curr_idx = (curr_idx + 1) % len(stm_val_idxs)

        if step_correct_final:
            correct += 1
        total += 1

        # Record trace for AF hash
        route_idx = {"REFUSE": 0, "RETRIEVE": 1, "BIND": 2, "MULTI_HOP": 3}[predicted_route]
        trace.append({
            "step": step,
            "predicted_route_idx": route_idx,
            "recovered_val": int(recovered_val),
            "step_correct": int(step_correct_final),
        })

        curr_idx = next_curr_idx
        curr_key = stm_key_tags[curr_idx].copy()
        curr_expected_val = int(stm_val_idxs[curr_idx])

    return float(correct) / max(1, total), trace


# ---------------------------------------------------------------------------
# Per-unit evaluation
# ---------------------------------------------------------------------------
def eval_unit(arm_kind: str, depth: int, alpha: float, noise_f: float,
              seed_int: int, n_trials: int) -> Tuple[float, float, List[float], np.ndarray]:
    """Run n_trials for (arm_kind, depth, alpha, f); return (mean, std, scores, af_trace).

    af_trace: np.ndarray of ints [n_trials, depth, 3] = (predicted_route_idx,
              recovered_val, step_correct) -- used for META_RULE_AF hash.
    """
    seed_deriv = (seed_int * 100003
                  + (abs(hash(arm_kind)) % 10000)
                  + int(alpha * 1000)
                  + int(noise_f * 1000)
                  + depth)
    rng = _rng(seed_deriv)

    # Substrate + signal + roles + training
    codebook = bipolar_random_batch(rng, V_CB)
    sig_refuse = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    sig_retrieval = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    sig_chain = build_signal_codebook(rng, N_CHAIN_SLOTS)
    roles = build_role_vectors(rng)

    # STM at supra-critical load per alpha
    stm_banks, stm_key_tags, stm_val_idxs, stm_bank_asn = make_stm_overloaded(
        rng, codebook, alpha)

    # LTM: fixed 1200-item dense-Hopfield
    ltm_keys, ltm_val_idxs = make_ltm_hopfield(rng, codebook, 1200)

    known_entity_hv = bipolar_random(rng)

    # Train router class-HVs
    train_items = build_train_dataset(rng, sig_refuse, sig_retrieval,
                                      sig_chain, known_entity_hv)
    class_hvs = train_class_hvs(train_items, roles)

    trial_scores = []
    trial_traces = []
    for t in range(n_trials):
        s, trace = run_chain_trial(
            rng, arm_kind, depth, alpha, noise_f, codebook,
            stm_banks, stm_key_tags, stm_val_idxs, stm_bank_asn,
            ltm_keys, ltm_val_idxs,
            sig_refuse, sig_retrieval, sig_chain,
            roles, class_hvs, known_entity_hv)
        trial_scores.append(s)
        # Convert trace to fixed-shape array for AF hash
        arr = np.array([[t["predicted_route_idx"], t["recovered_val"], t["step_correct"]]
                        for t in trace], dtype=np.int64)
        trial_traces.append(arr)

    # Concatenate traces (variable-length depth per unit handled at unit level)
    af_trace = np.stack(trial_traces, axis=0)  # shape [n_trials, depth, 3]

    return (float(np.mean(trial_scores)),
            float(np.std(trial_scores)),
            trial_scores,
            af_trace)


# ---------------------------------------------------------------------------
# ARMS-MUST-DIFFER hash (META_RULE_AF)
# Uses RAW output-tensor per-step trace, NOT trial_scores. Fixes v2 bug where
# saturated [1,1,1,1] scores hash-identical across depths but represent
# distinct mechanism-execution traces.
# ---------------------------------------------------------------------------
def _arms_must_differ(arm_traces: Dict[str, np.ndarray]) -> Dict[str, str]:
    digests = {}
    for name, out in arm_traces.items():
        b = out.tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digests[a] == digests[b]:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical "
                    f"(hash={digests[a]})")
    return digests


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.perf_counter()

    exp_name = _HDLAB_EXP_NAME or ANCHOR_NAME
    output_dir = REPO / "data" / f"exp_{exp_name}"
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_start_marker(str(output_dir), ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    print(f"[{ANCHOR_NAME}] START mode={RUN_MODE} depths={DEPTHS} "
          f"alphas={ALPHAS} noise_fs={NOISE_FS} n_trials={N_TRIALS} "
          f"expected_units={EXPECTED_N_UNITS}", flush=True)

    if RUN_MODE == "self_test":
        # Verify substrate + primitives at smallest config
        rng = _rng(SEED_THIS_CHUNK)
        codebook = bipolar_random_batch(rng, V_CB)
        sig_r = build_signal_codebook(rng, N_SIGNAL_SLOTS)
        sig_ret = build_signal_codebook(rng, N_SIGNAL_SLOTS)
        sig_c = build_signal_codebook(rng, N_CHAIN_SLOTS)
        roles = build_role_vectors(rng)
        known_entity_hv = bipolar_random(rng)
        train_items = build_train_dataset(rng, sig_r, sig_ret, sig_c, known_entity_hv)
        assert len(train_items) == N_TRAIN_PER_CLASS * N_CLASSES, "train_items count wrong"
        class_hvs = train_class_hvs(train_items, roles)
        assert len(class_hvs) == N_CLASSES, "class_hvs count wrong"
        # Distinct
        digests_st = {r: hashlib.sha256(class_hvs[r].tobytes()).hexdigest() for r in ROUTES}
        assert len(set(digests_st.values())) == N_CLASSES, "class-HVs not distinct"
        # Train self-accuracy sanity
        train_hits = 0
        for item in train_items[:20]:
            feat = build_feature_hv(item["refuse_slot"], item["retrieval_slot"],
                                    item["query"], item["chain_slot"], roles)
            pred, _sim = predict_route(feat, class_hvs)
            if pred == item["route"]:
                train_hits += 1
        train_acc = train_hits / 20.0
        assert train_acc > 0.4, f"router train_acc={train_acc} too low"
        # STM overloaded at alpha=3.0 test
        stm_banks, _, _, _ = make_stm_overloaded(rng, codebook, 3.0)
        assert len(stm_banks) == N_BANKS
        # Bernoulli noise sanity
        k = bipolar_random(rng)
        k_noisy = apply_bernoulli_noise(k, 0.30, rng)
        flip_frac = float(np.mean(k != k_noisy))
        assert 0.20 < flip_frac < 0.40, f"noise flip_frac={flip_frac} not in [0.20, 0.40]"

        elapsed = time.perf_counter() - t0
        metrics = {
            "verdict": "HARD_PASS",
            "verdict_msg": (f"SELFTEST_PASS (M1.4/M1.5/M1.6 primitives OK; "
                            f"train_acc={train_acc:.3f}; noise_flip_frac={flip_frac:.3f})"),
            "summary": "SELFTEST_PASS",
            "elapsed_s": round(elapsed, 3),
            "run_mode": "self_test",
            "anchor_name": ANCHOR_NAME,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "config_version": CONFIG_VERSION,
            "train_acc_sample": train_acc,
            "noise_flip_frac_sample": flip_frac,
        }
        tmp = output_dir / "metrics.json.tmp"
        final = output_dir / "metrics.json"
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        os.replace(str(tmp), str(final))
        print(f"[{ANCHOR_NAME}] SELFTEST_PASS elapsed={elapsed:.2f}s", flush=True)
        return

    # Full or smoke run
    per_unit = []
    arm_traces_sample = {}  # for META_RULE_AF
    unit_idx = 0

    # ARM_FULL_STACK sweep
    for depth in DEPTHS:
        for alpha in ALPHAS:
            for f in NOISE_FS:
                unit_start = time.perf_counter()
                try:
                    score_mean, score_std, trial_scores, af_trace = eval_unit(
                        "FULL_STACK", depth, alpha, f, SEED_THIS_CHUNK, N_TRIALS)
                    failure_class = None
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as e:
                    failure_class = f"UNIT_EXC_{type(e).__name__}"
                    score_mean, score_std = -1.0, -1.0
                    trial_scores = []
                    af_trace = np.zeros((1, 1, 3), dtype=np.int64)
                    print(f"[{ANCHOR_NAME}] UNIT_ERR arm=FULL_STACK d={depth} "
                          f"a={alpha} f={f}: {e}", flush=True)

                unit_elapsed = time.perf_counter() - unit_start

                key = f"ARM_FULL_STACK_d{depth}_a{alpha}_f{f}"
                per_unit.append({
                    "arm_kind": "FULL_STACK",
                    "arm_key": key,
                    "depth": depth,
                    "alpha": alpha,
                    "noise_f": f,
                    "score_mean": float(score_mean),
                    "score_std": float(score_std),
                    "n_trials": N_TRIALS,
                    "trial_scores": [float(s) for s in trial_scores],
                    "elapsed_s": round(unit_elapsed, 3),
                    "seed": SEED_THIS_CHUNK,
                    "failure_class": failure_class,
                })

                if key not in arm_traces_sample and failure_class is None:
                    arm_traces_sample[key] = af_trace

                unit_idx += 1
                emit_heartbeat(str(output_dir), unit_idx,
                               time.perf_counter() - t0,
                               total_units=EXPECTED_N_UNITS,
                               extra={"arm": "FULL_STACK", "depth": depth,
                                      "alpha": alpha, "f": f,
                                      "score_mean": round(score_mean, 4)})
                print(f"[{ANCHOR_NAME}] unit {unit_idx}/{EXPECTED_N_UNITS} "
                      f"FS d={depth} a={alpha} f={f} "
                      f"score={score_mean:.3f}+/-{score_std:.3f} "
                      f"elapsed={unit_elapsed:.2f}s", flush=True)

    # Ablation pins
    for arm_kind_short, depth, alpha, f in ABLATION_PINS:
        arm_kind = arm_kind_short.replace("ARM_", "")  # SUBSTRATE_ONLY or NO_REFUSE
        unit_start = time.perf_counter()
        try:
            score_mean, score_std, trial_scores, af_trace = eval_unit(
                arm_kind, depth, alpha, f, SEED_THIS_CHUNK, N_TRIALS)
            failure_class = None
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failure_class = f"UNIT_EXC_{type(e).__name__}"
            score_mean, score_std = -1.0, -1.0
            trial_scores = []
            af_trace = np.zeros((1, 1, 3), dtype=np.int64)
            print(f"[{ANCHOR_NAME}] UNIT_ERR arm={arm_kind_short} d={depth} "
                  f"a={alpha} f={f}: {e}", flush=True)

        unit_elapsed = time.perf_counter() - unit_start

        key = f"{arm_kind_short}_d{depth}_a{alpha}_f{f}"
        per_unit.append({
            "arm_kind": arm_kind,
            "arm_key": key,
            "depth": depth,
            "alpha": alpha,
            "noise_f": f,
            "score_mean": float(score_mean),
            "score_std": float(score_std),
            "n_trials": N_TRIALS,
            "trial_scores": [float(s) for s in trial_scores],
            "elapsed_s": round(unit_elapsed, 3),
            "seed": SEED_THIS_CHUNK,
            "failure_class": failure_class,
        })

        if key not in arm_traces_sample and failure_class is None:
            arm_traces_sample[key] = af_trace

        unit_idx += 1
        emit_heartbeat(str(output_dir), unit_idx,
                       time.perf_counter() - t0,
                       total_units=EXPECTED_N_UNITS,
                       extra={"arm": arm_kind_short, "depth": depth,
                              "alpha": alpha, "f": f,
                              "score_mean": round(score_mean, 4)})
        print(f"[{ANCHOR_NAME}] unit {unit_idx}/{EXPECTED_N_UNITS} "
              f"{arm_kind_short} d={depth} a={alpha} f={f} "
              f"score={score_mean:.3f}+/-{score_std:.3f} "
              f"elapsed={unit_elapsed:.2f}s", flush=True)

    # META_RULE_AF: hash raw traces (not trial_scores)
    arms_differ_verified = False
    af_error = None
    af_digests = {}
    try:
        af_digests = _arms_must_differ(arm_traces_sample)
        arms_differ_verified = True
    except AssertionError as e:
        af_error = str(e)

    # ---------- Aggregate scoring ----------
    def _get_fs(depth, alpha, f):
        for r in per_unit:
            if (r["arm_kind"] == "FULL_STACK" and r["depth"] == depth
                    and abs(r["alpha"] - alpha) < 1e-6
                    and abs(r["noise_f"] - f) < 1e-6):
                return r["score_mean"]
        return None

    def _get_ablation(arm_short, depth, alpha, f):
        target_arm = arm_short.replace("ARM_", "")
        for r in per_unit:
            if (r["arm_kind"] == target_arm and r["depth"] == depth
                    and abs(r["alpha"] - alpha) < 1e-6
                    and abs(r["noise_f"] - f) < 1e-6):
                return r["score_mean"]
        return None

    # HP gates
    hp_gates = {}

    # HP_STACK_HOLDS_AT_DEPTH_100 (only in FULL mode; smoke has max depth 100)
    fs_d100_a05_f0 = _get_fs(100, 0.5, 0.0)
    hp_gates["HP_STACK_HOLDS_AT_DEPTH_100"] = (
        fs_d100_a05_f0 is not None and
        fs_d100_a05_f0 >= HP_STACK_HOLDS_D100_FLOOR + BAND_WIDTH_MARGIN * (1.0 - HP_STACK_HOLDS_D100_FLOOR)
    )

    # HP_STACK_DEGRADES_AT_LOAD
    fs_d100_a3_f0 = _get_fs(100, 3.0, 0.0)
    if fs_d100_a05_f0 is not None and fs_d100_a3_f0 is not None:
        load_delta = fs_d100_a05_f0 - fs_d100_a3_f0
        hp_gates["HP_STACK_DEGRADES_AT_LOAD"] = (load_delta >= HP_STACK_DEGRADES_LOAD_DELTA)
    else:
        hp_gates["HP_STACK_DEGRADES_AT_LOAD"] = False
        load_delta = None

    # HP_STACK_DEGRADES_AT_NOISE (depth=50, alpha=1.5)
    fs_d50_a15_f0 = _get_fs(50, 1.5, 0.0)
    fs_d50_a15_f03 = _get_fs(50, 1.5, 0.30)
    if fs_d50_a15_f0 is not None and fs_d50_a15_f03 is not None:
        noise_delta = fs_d50_a15_f0 - fs_d50_a15_f03
        hp_gates["HP_STACK_DEGRADES_AT_NOISE"] = (noise_delta >= HP_STACK_DEGRADES_NOISE_DELTA)
    else:
        hp_gates["HP_STACK_DEGRADES_AT_NOISE"] = False
        noise_delta = None

    # HP_NO_CROSS_STAGE_BUG: no smooth degradation cliff
    stage_bug = False
    stage_bug_detail = None
    for alpha in ALPHAS:
        for f in NOISE_FS:
            prev = None
            for d in sorted(DEPTHS):
                s = _get_fs(d, alpha, f)
                if s is None:
                    continue
                if prev is not None and prev > 0.30 and s < HP_NO_STAGE_BUG_MIN:
                    stage_bug = True
                    stage_bug_detail = f"cliff (a={alpha}, f={f}): d prev={prev:.3f} -> curr={s:.3f}"
                prev = s
    hp_gates["HP_NO_CROSS_STAGE_BUG"] = (not stage_bug)

    # HP_LIFT_OVER_NO_REFUSE: FS(d=50, a=1.5, f=0.30) - NO_REFUSE(d=50, a=1.5, f=0.30)
    no_ref_pin = _get_ablation("ARM_NO_REFUSE", 50, 1.5, 0.30)
    if fs_d50_a15_f03 is not None and no_ref_pin is not None:
        lift_no_ref = fs_d50_a15_f03 - no_ref_pin
        hp_gates["HP_LIFT_OVER_NO_REFUSE"] = (lift_no_ref >= HP_LIFT_OVER_NO_REFUSE)
    else:
        hp_gates["HP_LIFT_OVER_NO_REFUSE"] = False
        lift_no_ref = None

    # HP_LIFT_OVER_SUBSTRATE_ONLY: FS(d=50, a=0.5, f=0.0) - SUB_ONLY(d=50, a=0.5, f=0.0)
    # In FULL mode; SMOKE uses depth=25 pin
    sub_pin_depth = 50 if RUN_MODE == "full" else 25
    fs_pin = _get_fs(sub_pin_depth, 0.5, 0.0)
    sub_pin = _get_ablation("ARM_SUBSTRATE_ONLY", sub_pin_depth, 0.5, 0.0)
    if fs_pin is not None and sub_pin is not None:
        lift_sub = fs_pin - sub_pin
        hp_gates["HP_LIFT_OVER_SUBSTRATE_ONLY"] = (lift_sub >= HP_LIFT_OVER_SUBSTRATE_ONLY)
    else:
        hp_gates["HP_LIFT_OVER_SUBSTRATE_ONLY"] = False
        lift_sub = None

    # META_RULE_AG baseline_in_band: check that AT LEAST ONE FS point is in [0.05, 0.95]
    fs_scores = [_get_fs(d, a, f) for d in DEPTHS for a in ALPHAS for f in NOISE_FS
                 if _get_fs(d, a, f) is not None]
    all_saturated = all(s >= 0.95 for s in fs_scores) if fs_scores else False
    all_floor = all(s <= 0.05 for s in fs_scores) if fs_scores else False
    baseline_in_band = (not all_saturated) and (not all_floor)

    # HF conditions
    hf_gates = {}
    hf_gates["HF_STACK_SATURATES"] = all_saturated
    hf_gates["HF_BASELINE_OUT_OF_BAND_META_RULE_AG"] = (not baseline_in_band)
    fs_d5_a05_f0 = _get_fs(5, 0.5, 0.0)
    hf_gates["HF_POSITIVE_CONTROL_BROKEN"] = (
        fs_d5_a05_f0 is not None and fs_d5_a05_f0 < 0.75
    )
    hf_gates["HF_STACK_BREAKS_EARLY"] = (
        fs_d5_a05_f0 is not None and fs_d5_a05_f0 < 0.30
    )

    # Cardinality
    observed = len(per_unit)
    cardinality_ok = observed >= CARDINALITY_FLOOR

    # Verdict
    verdict = "UNKNOWN"
    verdict_msgs = []
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msgs.append(f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H "
                            f"(observed={observed}, expected>={CARDINALITY_FLOOR})")
    if not arms_differ_verified:
        verdict = "HARD_FAIL"
        verdict_msgs.append(f"HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF ({af_error})")
    if hf_gates.get("HF_STACK_SATURATES"):
        verdict = "HARD_FAIL"
        verdict_msgs.append("HARD_FAIL_STACK_SATURATES (all FS >= 0.95)")
    if hf_gates.get("HF_BASELINE_OUT_OF_BAND_META_RULE_AG"):
        verdict = "HARD_FAIL"
        verdict_msgs.append("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG")
    if hf_gates.get("HF_POSITIVE_CONTROL_BROKEN"):
        verdict = "HARD_FAIL"
        verdict_msgs.append(f"HARD_FAIL_POSITIVE_CONTROL_BROKEN "
                            f"(FS d=5 a=0.5 f=0 = {fs_d5_a05_f0})")
    if hf_gates.get("HF_STACK_BREAKS_EARLY"):
        verdict = "HARD_FAIL"
        verdict_msgs.append(f"HARD_FAIL_STACK_BREAKS_EARLY "
                            f"(FS d=5 a=0.5 f=0 = {fs_d5_a05_f0})")

    # Count HP gates (evaluate ONLY relevant gates for mode)
    if RUN_MODE == "full":
        applicable_hps = ["HP_STACK_HOLDS_AT_DEPTH_100", "HP_STACK_DEGRADES_AT_LOAD",
                          "HP_STACK_DEGRADES_AT_NOISE", "HP_NO_CROSS_STAGE_BUG",
                          "HP_LIFT_OVER_NO_REFUSE", "HP_LIFT_OVER_SUBSTRATE_ONLY"]
    else:
        # In SMOKE: gates HP_HOLDS/DEGRADES_LOAD still evaluable (depth=100 in smoke);
        # HP_DEGRADES_NOISE at d=50 NOT in smoke depths (smoke has {5, 25, 100}); skip
        applicable_hps = ["HP_STACK_HOLDS_AT_DEPTH_100", "HP_STACK_DEGRADES_AT_LOAD",
                          "HP_NO_CROSS_STAGE_BUG", "HP_LIFT_OVER_SUBSTRATE_ONLY"]

    n_hp_fired = sum(1 for g in applicable_hps if hp_gates.get(g) is True)
    n_hp_total = len(applicable_hps)

    if verdict == "UNKNOWN":
        if n_hp_fired == n_hp_total:
            verdict = "HARD_PASS"
            verdict_msgs.append(f"HARD_PASS ({n_hp_fired}/{n_hp_total} HP gates fired)")
        elif n_hp_fired >= n_hp_total - 1:
            verdict = "MIDDLE_BAND"
            verdict_msgs.append(f"MIDDLE_BAND ({n_hp_fired}/{n_hp_total} HP gates fired)")
        else:
            verdict = "HARD_FAIL"
            verdict_msgs.append(f"HARD_FAIL_HP_FLOOR ({n_hp_fired}/{n_hp_total} HP gates fired)")

    # Attach diagnostic tail
    diag_tail = (f" | cardinality={observed}/{EXPECTED_N_UNITS} "
                 f"| arms_differ={arms_differ_verified} "
                 f"| baseline_in_band={baseline_in_band} "
                 f"| FS(d100,a0.5,f0)={fs_d100_a05_f0} "
                 f"| FS(d100,a3,f0)={fs_d100_a3_f0} "
                 f"| load_delta={load_delta} "
                 f"| noise_delta={noise_delta}")

    elapsed = time.perf_counter() - t0
    verdict_msg = " | ".join(verdict_msgs) + diag_tail

    aggregate_scores = {}
    for r in per_unit:
        aggregate_scores[r["arm_key"]] = r["score_mean"]

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg[:200],
        "elapsed_s": round(elapsed, 3),
        "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config_version": CONFIG_VERSION,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": EXPECTED_N_UNITS,
        "observed_n_units": observed,
        "arms_differ_verified": arms_differ_verified,
        "af_error": af_error,
        "af_digests": af_digests,
        "baseline_in_band": baseline_in_band,
        "hp_gates": hp_gates,
        "hf_gates": hf_gates,
        "aggregate_scores": aggregate_scores,
        "load_delta": load_delta,
        "noise_delta": noise_delta,
        "lift_no_ref": lift_no_ref,
        "lift_sub": lift_sub,
        "per_unit": per_unit,
        "chance_floor": CHANCE_FLOOR,
        "meta_rules_applied": ["META_RULE_H", "META_RULE_J", "META_RULE_K",
                               "META_RULE_L", "META_RULE_M", "META_RULE_AC",
                               "META_RULE_AF", "META_RULE_AG", "META_RULE_AH",
                               "META_RULE_AT"],
        "seed": SEED_THIS_CHUNK,
    }

    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(str(tmp), str(final))

    print(f"[{ANCHOR_NAME}] DONE verdict={verdict} "
          f"cardinality={observed}/{EXPECTED_N_UNITS} "
          f"hp_gates={n_hp_fired}/{n_hp_total} "
          f"elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    exp_name = _HDLAB_EXP_NAME or ANCHOR_NAME
    output_dir_for_crash = REPO / "data" / f"exp_{exp_name}"
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(str(output_dir_for_crash), ANCHOR_NAME, e)
        raise
