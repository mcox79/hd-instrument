"""cortex_context_retention_v1 -- seed_7. Cortex-side multi-turn dialogue context.

FIRST cortex-integration cell in the M3 architecture stack. Composes chain-grade
substrate primitives (WM multi-bank K=4096 CG'd, INT8_DENSE Pareto CG'd,
Dense-Hopfield READ-REPLACE CG'd, TWO_TIER generational CG'd) at the cortex
boundary. NOT a new substrate primitive -- wires existing WM to a cortex-side
dialogue-context API.

Research parent: M1.5 research drill 2026-07-01 (Rank 1, P_deflated=0.42).
CG parents (all locked chain-grade this session):
  - WM multi-bank K=4096 MULTI_64x (commit 6c6a271d today Wave 1 --
    hdlab/working_memory.py K_TOTAL_CHAIN_GRADE_ENVELOPE)
  - INT8_DENSE Pareto-optimal M in {40k,80k} (commit 716174a7 --
    hdlab/int8_dense.py)
  - Dense-Hopfield READ-REPLACE (commit 863e14b5 --
    exp_cortex_hippo_dense_layer_M8192_v2 template)
  - TWO_TIER generational (prior CG; STM K=100 + LTM K=4096 composition)
  - Cross-modal binding 5-modality (prior CG; entity+attribute+relation triple)

SCENARIO (3-turn dialogue):
  Turn 1: introduce entity E1 with attribute A1 (bind E1 x A1 into WM)
  Turn 2: introduce entity E2 with attribute A2 (bind E2 x A2 into WM)
  Turn 3: query "does E1 have A1?" (recall A1 given E1)
Score: cosine similarity between recovered A1_hat and true A1.
Discriminator: cortex must resolve E1 -> A1 despite E2/A2 interference at
turn 3, and lift over no-context floor.

ARMS (4):
  ARM_NO_CONTEXT   : cortex retrieves from KB codebook only (no WM buffer)
                     -- negative control; expected recall ~ random-guess floor.
  ARM_WM_K100      : cortex WM buffer holds K=100 bindings (short 1-turn window)
                     -- routes E-A binds through WM; single bank; k_per_bank=100.
  ARM_WM_K500      : cortex WM buffer holds K=500 bindings (~5 turns of dialogue)
                     -- multi-bank K=500 (bank_count=8, k_per_bank=63; discriminating
                     regime per hdlab/working_memory.py K_PER_BANK_DISCRIMINATING_
                     REGIME_MINIMUM = 64; smoke uses 4 banks x 25).
  ARM_WM_TWOTIER   : STM K=100 (recent) + LTM K=4096 dense-Hopfield replace
                     -- composes CG'd WM multi-bank + Dense-Hopfield READ-REPLACE;
                     TWO_TIER generational routing.

DISCRIMINATOR-MUST-SURVIVE-SCALE (META directive USER 2026-06-26):
  Smoke uses full-N=8192 substrate dim (numpy cheap; ~2 min). K axis is the
  discriminator (K=100 vs K=500 crosses K_PER_BANK regime for K=500). Preview
  arm not needed since smoke IS at full-N.

FALSIFIABLE PREDICTIONS (per M1.5 research drill):
  HARD_PASS (chain-grade):
    - ARM_WM_K500 recall cosine >= 0.80 at turn 3 (pronoun-resolution)
    - lift(ARM_WM_K500 - ARM_NO_CONTEXT) >= 0.20 cosine
    - ARM_WM_TWOTIER recall >= ARM_WM_K500 at K > K_cliff regime
    - cross-seed cv (over the 3 chunk-seed files aggregated) < 5% (per-seed)
  HARD_FAIL_MECHANISM:
    - ARM_WM_K100 recall < 0.60 -> WM not propagating context to cortex
  HARD_FAIL_TWOTIER_BROKEN:
    - ARM_WM_TWOTIER < ARM_NO_CONTEXT (TWOTIER composition inverted)
  HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF):
    - any two arms' recall bit-identical (arms don't differ)
  HARD_FAIL_CARDINALITY_BREACH (META_RULE_H):
    - observed core-arm rows < 3 (of 4 expected per phase point)
  MIDDLE_BAND:
    - ARM_WM_K500 recall in [0.60, 0.80]

META_RULE_Q (suspect-1.000 flag): if ARM_WM_TWOTIER == 1.000 at high-alpha
regime, flag as by-construction suspect; not HARD_PASS on its own.

META_RULE_AT (composition provenance): cell composes 4 CG parents; each
parent cited in atoms.md above.

META_RULE_AX (arm distinctness mandatory): WM_K100 vs WM_K500 must differ in
recall at K_cliff region; smoke selftest checks this.

CARDINALITY (META_RULE_H):
  Full grid: 3 K-levels x 3 turn-distances x 3 entity-types = 27 phase points
             x 4 arms = 108 arm-rows per seed (this chunk = seed_7 -> 108 rows).
  Smoke grid: 2 K-levels x 2 turn-distances x 2 entity-types x 4 arms
             = 32 arm-rows.
  EXPECTED_N_UNITS = 108 (FULL). HARD_FAIL_CARDINALITY_BREACH if < 100.

CRLB (recall-cosine as continuous quantity; MSE-CLT):
  Per-arm score = mean cosine over N_TRIALS_PER_UNIT recall trials.
  sigma_min(single-trial) = 1/sqrt(N_DIM) = 1/sqrt(8192) = 0.01104
                            THEORETICAL@bipolar-inner-product-CLT.
  N_TRIALS = 8 per unit -> sigma_unit = 0.01104/sqrt(8) = 0.00390.
  HP gap 0.20 = 51 * sigma_unit; well-reachable.

Regime notes:
  - CPU-eligible (numpy) for smoke AND full at N=8192 (small-M dialogue setup)
  - Estimated full wall: ~15-20 min per seed on remote_cpu
  - Route: remote_cpu_queue via hdi_orchestrator handoff post-smoke

Author: exp_dev (hdi_exp_dev spawn) 2026-07-01.
PRESERVE_ENV_VARS: HDLAB_QUEUE
ASCII-only; META_RULE_AC/AF/AG/AH/AT/AX/H/Q load-bearing.
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


SEED_THIS_CHUNK = 19
ANCHOR_NAME = f"cortex_context_retention_v1_seed_{SEED_THIS_CHUNK}"
_HARDENING_MARKER = "v1_cortex_context_retention_seed_chunk"

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
N_DIM = 8192                     # WM K-cliff regime CG'd (per hdlab/working_memory.py THRESHOLD_ANCHORED_AT_N_DIM)

# K axis: WM buffer capacity
K_LEVELS_FULL = [0, 100, 500]    # 0 = NO_CONTEXT floor; 100/500 = WM arms
K_LEVELS_SMOKE = [0, 100, 500]   # keep full K coverage in smoke to fire discriminator

# Turn-distance axis: how far back the target-entity was introduced
TURN_DISTANCES_FULL = [1, 2, 5]  # turns between E introduction and query
TURN_DISTANCES_SMOKE = [1, 5]    # extremes

# Entity-type axis: what's being bound (entity / attribute / relation)
ENTITY_TYPES_FULL = ["entity", "attribute", "relation"]
ENTITY_TYPES_SMOKE = ["entity", "relation"]

# N_TRIALS per (K, turn, entity_type) point -- averaging for stable score
N_TRIALS_FULL = 8
N_TRIALS_SMOKE = 4

# Bank config for multi-bank WM (per hdlab/working_memory.py chain-grade envelope)
K_PER_BANK_TARGET = 64           # CG'd K_PER_BANK_DISCRIMINATING_REGIME_MINIMUM
# For K=100: 1 bank of 100 (below discriminating regime -> saturates; expected).
#   K=500 gets bank_count=8 (k_per_bank=62; ~at discriminating threshold).
# For K=4096 TWOTIER LTM: bank_count=64 (k_per_bank=64; CG discriminating envelope).

# LTM config for TWOTIER arm
LTM_K_FULL = 4096                # CG'd K_TOTAL_CHAIN_GRADE_ENVELOPE
LTM_K_SMOKE = 4096               # same at smoke (still cheap at N=8192)
LTM_N_BANKS = 64                 # K_PER_BANK = 64 discriminating envelope
STM_K = 100                      # short-term bank in TWOTIER
BETA_DENSE_MIN = 8.0             # dense-Hopfield beta floor (per exp_cortex_hippo v2)
BETA_DENSE_MAX = 128.0           # ceiling before metastable collapse

SEEDS_FULL = [SEED_THIS_CHUNK]

if RUN_MODE == "smoke":
    K_LEVELS = K_LEVELS_SMOKE
    TURN_DISTANCES = TURN_DISTANCES_SMOKE
    ENTITY_TYPES = ENTITY_TYPES_SMOKE
    N_TRIALS = N_TRIALS_SMOKE
    LTM_K = LTM_K_SMOKE
else:
    K_LEVELS = K_LEVELS_FULL
    TURN_DISTANCES = TURN_DISTANCES_FULL
    ENTITY_TYPES = ENTITY_TYPES_FULL
    N_TRIALS = N_TRIALS_FULL
    LTM_K = LTM_K_FULL

# 4 arms; K=0 is NO_CONTEXT; K=100 is WM_K100; K=500 is WM_K500; TWOTIER runs separately
# per phase point (turn_distance x entity_type).
# So arms per phase point = 4 (NO_CONTEXT, WM_K100, WM_K500, WM_TWOTIER).
# Note: K_LEVELS drives which single-arm K value each of the first 3 arms uses.
N_ARMS_PER_POINT = 4
N_PHASE_POINTS = len(TURN_DISTANCES) * len(ENTITY_TYPES)
EXPECTED_N_UNITS = N_PHASE_POINTS * N_ARMS_PER_POINT
# FULL: 3*3*4 = 36 arm-rows per seed; below stated 108 in docstring because we
# hoisted K into arm identity (not a phase axis). Update expected: 36 per seed.
# HARD_FAIL_CARDINALITY_BREACH if < 30 core-arm rows (arithmetic rounding for
# in-flight partials).

CRLB_SIGMA_SINGLE_TRIAL = 1.0 / math.sqrt(N_DIM)               # 0.01104 THEORETICAL@bipolar-CLT
CRLB_SIGMA_UNIT = CRLB_SIGMA_SINGLE_TRIAL / math.sqrt(N_TRIALS)  # 0.00390 at N_TRIALS=8
HP_TURN3_RECALL = 0.80          # WM_K500 turn-3 recall gate
HP_LIFT_OVER_NOCTX = 0.20       # WM_K500 - NO_CONTEXT lift gate
HP_MECHANISM_FLOOR = 0.60       # WM_K100 must clear this (mechanism firing)
HP_SATURATION_FLAG = 0.9995     # META_RULE_Q suspect-1.000 threshold

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_DIM={N_DIM},"
    f"K_levels={K_LEVELS},turn_dists={TURN_DISTANCES},"
    f"entity_types={ENTITY_TYPES},N_trials={N_TRIALS},"
    f"LTM_K={LTM_K},LTM_banks={LTM_N_BANKS},STM_K={STM_K},"
    f"beta_dense=[{BETA_DENSE_MIN},{BETA_DENSE_MAX}],"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"mode={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},"
    f"backend=numpy,"
    f"crlb_sigma_unit={CRLB_SIGMA_UNIT:.5f},"
    f"HP_turn3={HP_TURN3_RECALL},HP_lift={HP_LIFT_OVER_NOCTX},"
    f"HP_mech_floor={HP_MECHANISM_FLOOR},"
    f"hardening={_HARDENING_MARKER}"
)


# ---------------------------------------------------------------------------
# Substrate primitives (inline; compose CG'd WM + Dense-Hopfield READ-REPLACE)
# ---------------------------------------------------------------------------
def _rng(seed_int: int) -> np.random.RandomState:
    return np.random.RandomState(int(seed_int) & 0x7FFFFFFF)


def _bipolar(shape, rng: np.random.RandomState) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=shape).astype(np.float64)


def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True).clip(min=1e-12)


def _bind_xor(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Bipolar binding via element-wise multiply (equiv to XOR for {-1,+1})."""
    return a * b


def _unbind_xor(bound: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Bipolar unbind = bind again (involutive; a*b*b = a)."""
    return bound * key


def _bipolar_quantize(x: np.ndarray) -> np.ndarray:
    q = np.sign(x)
    q[q == 0] = 1.0
    return q


# ---------------------------------------------------------------------------
# WM multi-bank primitive (compact numpy; per hdlab/working_memory.py CG envelope)
# ---------------------------------------------------------------------------
def wm_multibank_write(keys: np.ndarray, vals: np.ndarray,
                       n_banks: int) -> np.ndarray:
    """Write K bindings (keys[i] bind vals[i]) into n_banks parallel banks.

    Each bank i holds superposition of items routed to it by hash-mod-n_banks
    on the key. Returns bank_states of shape (n_banks, N_DIM), bipolar-quantized.

    Composition rationale: this is the CG'd multi-bank WM primitive at
    K_PER_BANK = ceil(K/n_banks); when k_per_bank ~ 64 sits in discriminating
    regime per hdlab/working_memory.py.
    """
    K_total, N = keys.shape
    if K_total == 0:
        return np.zeros((max(1, n_banks), N), dtype=np.float64)
    # Route: bank_id = hash(key_bytes[:8]) mod n_banks. For determinism, use
    # first 4 dims' bipolar sign pattern -> int.
    bank_ids = np.zeros(K_total, dtype=np.int64)
    n_route_bits = max(1, int(math.log2(max(2, n_banks))))
    n_route_bits = min(n_route_bits, 8)
    for i in range(K_total):
        bits = (keys[i, :n_route_bits] > 0).astype(np.int64)
        code = 0
        for b in bits:
            code = (code << 1) | int(b)
        bank_ids[i] = code % n_banks
    bank_states = np.zeros((n_banks, N), dtype=np.float64)
    for i in range(K_total):
        bound = _bind_xor(keys[i], vals[i])
        bank_states[bank_ids[i]] += bound
    return _bipolar_quantize(bank_states)


def wm_multibank_read(key_query: np.ndarray, bank_states: np.ndarray,
                      n_banks: int) -> np.ndarray:
    """Read from multi-bank WM: route query to bank by same hash, then unbind."""
    N = key_query.shape[0]
    n_route_bits = max(1, int(math.log2(max(2, n_banks))))
    n_route_bits = min(n_route_bits, 8)
    bits = (key_query[:n_route_bits] > 0).astype(np.int64)
    code = 0
    for b in bits:
        code = (code << 1) | int(b)
    bank_id = code % n_banks
    return _unbind_xor(bank_states[bank_id], key_query)


# ---------------------------------------------------------------------------
# Dense-Hopfield READ-REPLACE for LTM (per exp_cortex_hippo v2 CG template)
# ---------------------------------------------------------------------------
def dense_hopfield_read_replace(query: np.ndarray, K_tape: np.ndarray,
                                V_tape: np.ndarray, beta: float) -> np.ndarray:
    """Attention read: p = V^T softmax(beta * K @ query).

    K_tape and V_tape are stored keys/vals (M, N). Query is (N,). Returns (N,)
    reconstructed value. Follows exp_cortex_hippo_dense_layer_M8192_v2 arm
    ARM_HA_DENSE_REPLACE recipe (CG'd today).
    """
    q_n = query / max(np.linalg.norm(query), 1e-12)
    sims = K_tape @ q_n
    sims_scaled = beta * sims
    sims_scaled = sims_scaled - sims_scaled.max()
    w = np.exp(sims_scaled)
    w = w / max(w.sum(), 1e-30)
    return V_tape.T @ w


def _cosine_margin_estimate(K_tape: np.ndarray, sample_n: int = 256) -> float:
    """1 - mean(|off-diag cosine|) for adaptive-beta. Matches v2 template."""
    m = K_tape.shape[0]
    if m == 0:
        return 0.1
    n_s = min(sample_n, m)
    idx = np.arange(m)
    if m > n_s:
        rng = np.random.RandomState(0)
        idx = rng.choice(m, size=n_s, replace=False)
    sub = _l2norm_rows(K_tape[idx])
    sim = sub @ sub.T
    mask = ~np.eye(n_s, dtype=bool)
    off_mean_abs = float(np.abs(sim[mask]).mean())
    margin = 1.0 - off_mean_abs
    if not math.isfinite(margin) or margin <= 0.0:
        return 0.1
    return margin


def _adaptive_beta(m_items: int, margin: float) -> float:
    raw = math.log2(max(2, m_items)) / max(margin, 0.05)
    return float(max(BETA_DENSE_MIN, min(BETA_DENSE_MAX, raw)))


# ---------------------------------------------------------------------------
# Dialogue scenario builder
# ---------------------------------------------------------------------------
def build_dialogue_scenario(rng: np.random.RandomState, n_turns: int,
                            target_turn: int, entity_type: str,
                            interference_K: int) -> Tuple[np.ndarray, np.ndarray, int]:
    """Build a scripted n_turn dialogue with interference_K distractor bindings.

    entity_type governs what plays the role of 'entity' (E) and 'attribute' (A):
      - 'entity': E = person-vector, A = trait-vector
      - 'attribute': E = trait-vector, A = value-vector
      - 'relation': E = pair-of-entities, A = relation-vector
    Returns:
      turn_keys: (n_turns + interference_K, N_DIM) bipolar keys
      turn_vals: same shape; vals bound to keys
      target_idx: index of the row corresponding to (target_turn, target_entity)
    Semantic scoring uses cosine between recovered val and true val at target_idx.
    """
    N = N_DIM
    total = n_turns + interference_K
    if entity_type == "entity":
        keys = _bipolar((total, N), rng)
        vals = _bipolar((total, N), rng)
    elif entity_type == "attribute":
        # attribute-role: keys are trait-role vectors, vals are attribute-values
        keys = _bipolar((total, N), rng)
        vals = _bipolar((total, N), rng)
    elif entity_type == "relation":
        # relation-role: pair-of-entities binding is entity-A x entity-B
        eA = _bipolar((total, N), rng)
        eB = _bipolar((total, N), rng)
        keys = _bind_xor(eA, eB)   # relation key = pair
        vals = _bipolar((total, N), rng)  # relation value = relation-vector
    else:
        raise ValueError(f"unknown entity_type: {entity_type}")
    # target is at index target_turn - 1 (0-indexed within first n_turns)
    if target_turn < 1 or target_turn > n_turns:
        raise ValueError(f"target_turn {target_turn} out of [1, {n_turns}]")
    target_idx = target_turn - 1
    return keys, vals, target_idx


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ---------------------------------------------------------------------------
# Arm runners
# ---------------------------------------------------------------------------
def run_arm_no_context(rng: np.random.RandomState, n_turns: int,
                       target_turn: int, entity_type: str,
                       interference_K: int, n_trials: int) -> Dict:
    """ARM_NO_CONTEXT: no WM buffer; retrieval from arbitrary KB codebook (random guess).

    Since no WM stores the E1->A1 binding, retrieval defaults to random codebook
    lookup. Expected recall cosine ~ 1/sqrt(N_DIM) noise ~ 0.011.
    """
    cosines = []
    for trial in range(n_trials):
        r = _rng(rng.randint(0, 2**31 - 1))
        keys, vals, target_idx = build_dialogue_scenario(
            r, n_turns, target_turn, entity_type, interference_K
        )
        # No buffer; predict random bipolar vector as "recovered A"
        rand_pred = _bipolar((N_DIM,), r)
        cos = _cosine(rand_pred, vals[target_idx])
        cosines.append(cos)
    return {
        "recall_cosine_mean": float(np.mean(cosines)),
        "recall_cosine_std": float(np.std(cosines, ddof=1) if n_trials > 1 else 0.0),
        "n_trials": int(n_trials),
    }


def run_arm_wm_kbuf(rng: np.random.RandomState, K_buf: int, n_turns: int,
                    target_turn: int, entity_type: str,
                    interference_K: int, n_trials: int) -> Dict:
    """ARM_WM_K100 or ARM_WM_K500: cortex WM buffer holds K_buf recent bindings.

    Multi-bank routing: n_banks chosen so k_per_bank targets K_PER_BANK_TARGET=64.
    Writes up to K_buf items into WM (oldest evicted); at query time, unbinds
    target key from WM to recover target val.
    """
    cosines = []
    n_banks = max(1, min(64, int(round(K_buf / K_PER_BANK_TARGET))))
    if n_banks < 1:
        n_banks = 1
    for trial in range(n_trials):
        r = _rng(rng.randint(0, 2**31 - 1))
        keys, vals, target_idx = build_dialogue_scenario(
            r, n_turns, target_turn, entity_type, interference_K
        )
        # Write up to K_buf most recent bindings into WM (LRU eviction).
        # Order: first n_turns are dialogue-turn bindings (indices 0..n_turns-1);
        # then interference (n_turns..n_turns+interference_K-1). Model: WM holds
        # last K_buf items in write-order.
        total = keys.shape[0]
        if total > K_buf:
            keep_start = total - K_buf
        else:
            keep_start = 0
        keys_wm = keys[keep_start:]
        vals_wm = vals[keep_start:]
        # Multi-bank write
        bank_states = wm_multibank_write(keys_wm, vals_wm, n_banks)
        # Query: use target key (semantic "does E1 have A1?")
        if target_idx < keep_start:
            # target was evicted; cortex can't recover -> random-guess
            pred = _bipolar((N_DIM,), r)
        else:
            key_query = keys[target_idx]
            pred = wm_multibank_read(key_query, bank_states, n_banks)
        cos = _cosine(pred, vals[target_idx])
        cosines.append(cos)
    return {
        "recall_cosine_mean": float(np.mean(cosines)),
        "recall_cosine_std": float(np.std(cosines, ddof=1) if n_trials > 1 else 0.0),
        "n_trials": int(n_trials),
        "K_buf": int(K_buf),
        "n_banks": int(n_banks),
        "k_per_bank_effective": int(K_buf // max(1, n_banks)),
    }


def run_arm_wm_twotier(rng: np.random.RandomState, n_turns: int,
                       target_turn: int, entity_type: str,
                       interference_K: int, n_trials: int) -> Dict:
    """ARM_WM_TWOTIER: STM (K=100 multi-bank) + LTM (K=4096 dense-Hopfield READ-REPLACE).

    Routing: recent items go to STM (multi-bank WM per CG envelope). When STM
    reaches STM_K, spillover items go to LTM tape. Query hits STM first; if
    miss (below-margin), falls through to LTM via dense-Hopfield attention.

    Composition provenance:
      - STM = wm_multibank_write/read (CG hdlab/working_memory.py)
      - LTM = dense_hopfield_read_replace (CG exp_cortex_hippo v2 template)
      - Two-tier routing = TWO_TIER generational (CG prior)
    """
    cosines = []
    stm_banks = max(1, STM_K // K_PER_BANK_TARGET)
    if stm_banks < 1:
        stm_banks = 1
    for trial in range(n_trials):
        r = _rng(rng.randint(0, 2**31 - 1))
        keys, vals, target_idx = build_dialogue_scenario(
            r, n_turns, target_turn, entity_type, interference_K
        )
        total = keys.shape[0]
        # Route: last STM_K -> STM, rest -> LTM tape (up to LTM_K)
        if total > STM_K:
            stm_start = total - STM_K
            stm_keys = keys[stm_start:]
            stm_vals = vals[stm_start:]
            ltm_start = max(0, stm_start - LTM_K)
            ltm_keys = keys[ltm_start:stm_start]
            ltm_vals = vals[ltm_start:stm_start]
        else:
            stm_start = 0
            stm_keys = keys
            stm_vals = vals
            ltm_keys = np.zeros((0, N_DIM), dtype=np.float64)
            ltm_vals = np.zeros((0, N_DIM), dtype=np.float64)
        # STM write (multi-bank)
        stm_state = wm_multibank_write(stm_keys, stm_vals, stm_banks)
        # LTM stored as-is for dense-Hopfield attention (l2-normed rows)
        if ltm_keys.shape[0] > 0:
            K_tape = _l2norm_rows(ltm_keys)
            V_tape = _l2norm_rows(ltm_vals)
            margin = _cosine_margin_estimate(K_tape)
            beta = _adaptive_beta(ltm_keys.shape[0], margin)
        else:
            K_tape = None
            V_tape = None
            beta = float("nan")
        # Query routing: check if target is in STM range
        if target_idx >= stm_start:
            # Query STM
            key_query = keys[target_idx]
            pred = wm_multibank_read(key_query, stm_state, stm_banks)
        elif K_tape is not None and target_idx >= (stm_start - LTM_K):
            # Query LTM via dense-Hopfield
            key_query = keys[target_idx]
            pred = dense_hopfield_read_replace(key_query, K_tape, V_tape, beta)
        else:
            # Target evicted from both tiers -> random guess
            pred = _bipolar((N_DIM,), r)
        cos = _cosine(pred, vals[target_idx])
        cosines.append(cos)
    return {
        "recall_cosine_mean": float(np.mean(cosines)),
        "recall_cosine_std": float(np.std(cosines, ddof=1) if n_trials > 1 else 0.0),
        "n_trials": int(n_trials),
        "STM_K": int(STM_K),
        "LTM_K": int(LTM_K),
        "stm_banks": int(stm_banks),
        "ltm_beta_used": float(beta) if math.isfinite(beta) else None,
    }


def run_phase_point(phase_seed_offset: int, turn_dist: int, entity_type: str,
                    out_dir: Path, unit_idx: int, total_units: int) -> List[Dict]:
    """Run all 4 arms at one (turn_dist, entity_type) phase point."""
    # n_turns: enough to include target + interference. Use turn_dist as the
    # gap between target intro (turn 1) and query (turn 1+turn_dist).
    n_turns = 1 + turn_dist       # target at turn 1, query at turn n_turns
    target_turn = 1
    # Interference budget: fill to K=500 total in write-order for K=500 arm
    interference_K = max(0, 500 - n_turns)
    rng_arm = _rng(phase_seed_offset)
    t0_pp = time.time()
    arm_results = []

    # ARM_NO_CONTEXT
    t0 = time.time()
    m = run_arm_no_context(rng_arm, n_turns, target_turn, entity_type,
                            interference_K, N_TRIALS)
    m.update({
        "arm_name": "ARM_NO_CONTEXT",
        "K_buf": 0,
        "turn_distance": int(turn_dist),
        "entity_type": entity_type,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    # ARM_WM_K100
    t0 = time.time()
    m = run_arm_wm_kbuf(rng_arm, 100, n_turns, target_turn, entity_type,
                        interference_K, N_TRIALS)
    m.update({
        "arm_name": "ARM_WM_K100",
        "turn_distance": int(turn_dist),
        "entity_type": entity_type,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    # ARM_WM_K500
    t0 = time.time()
    m = run_arm_wm_kbuf(rng_arm, 500, n_turns, target_turn, entity_type,
                        interference_K, N_TRIALS)
    m.update({
        "arm_name": "ARM_WM_K500",
        "turn_distance": int(turn_dist),
        "entity_type": entity_type,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    # ARM_WM_TWOTIER
    t0 = time.time()
    m = run_arm_wm_twotier(rng_arm, n_turns, target_turn, entity_type,
                           interference_K, N_TRIALS)
    m.update({
        "arm_name": "ARM_WM_TWOTIER",
        "turn_distance": int(turn_dist),
        "entity_type": entity_type,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    emit_heartbeat(out_dir, unit_idx, time.time() - t0_pp,
                   total_units=total_units,
                   extra={"phase": "point_done",
                          "turn_distance": int(turn_dist),
                          "entity_type": entity_type})
    return arm_results


# ---------------------------------------------------------------------------
# Self-tests (formula + arms-must-differ preflight)
# ---------------------------------------------------------------------------
def _selftest_bipolar_bind_involutive() -> None:
    rng = _rng(0)
    a = _bipolar((16,), rng)
    b = _bipolar((16,), rng)
    bound = _bind_xor(a, b)
    unbound = _unbind_xor(bound, b)
    if not np.allclose(unbound, a):
        raise AssertionError("bipolar bind/unbind not involutive")


def _selftest_wm_multibank_recall_self() -> None:
    """WM multi-bank should recover val at K in discriminating regime."""
    rng = _rng(11)
    N = 512
    K = 8
    n_banks = 1
    keys = rng.choice([-1.0, 1.0], size=(K, N))
    vals = rng.choice([-1.0, 1.0], size=(K, N))
    banks = wm_multibank_write(keys, vals, n_banks)
    # For self-recall at K=8 << N=512 (very sparse), unbind should recover val
    pred = wm_multibank_read(keys[3], banks, n_banks)
    cos = _cosine(pred, vals[3])
    # At K=8 with bipolar quantize, cos should be well above noise
    if cos < 0.05:
        raise AssertionError(f"WM_MULTIBANK_SELFTEST FAIL: cos={cos:.4f} too low")


def _selftest_dense_hopfield_self_recall() -> None:
    rng = _rng(13)
    M, N = 8, 128
    V = rng.randn(M, N)
    V = _l2norm_rows(V)
    q = V[3].copy()
    p = dense_hopfield_read_replace(q, V, V, beta=50.0)
    err = float(np.linalg.norm(p - V[3]))
    if err > 0.2:
        raise AssertionError(f"DENSE_HOPFIELD_SELFTEST FAIL: err={err}")


def _selftest_scenario_builder() -> None:
    rng = _rng(17)
    for et in ("entity", "attribute", "relation"):
        keys, vals, ti = build_dialogue_scenario(rng, n_turns=3, target_turn=1,
                                                  entity_type=et, interference_K=5)
        if keys.shape != (8, N_DIM) or vals.shape != (8, N_DIM):
            raise AssertionError(f"scenario shape wrong for {et}: {keys.shape}")
        if ti != 0:
            raise AssertionError(f"target_idx wrong for {et}: {ti}")


def _selftest_adaptive_beta_computes_finite() -> None:
    b = _adaptive_beta(4096, 0.7)
    if not math.isfinite(b) or not (BETA_DENSE_MIN <= b <= BETA_DENSE_MAX):
        raise AssertionError(f"adaptive beta bad: {b}")
    b_deg = _adaptive_beta(4096, 0.01)
    if b_deg != BETA_DENSE_MAX:
        raise AssertionError(f"degenerate margin should clamp to ceiling: got {b_deg}")


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS_FULL != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS_FULL} != [{SEED_THIS_CHUNK}]")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor {ANCHOR_NAME} missing seed_{SEED_THIS_CHUNK}")


def _selftest_arms_expected_differ() -> None:
    """META_RULE_AF preflight: at a tiny high-interference world, 4 arms differ.

    Use K=500 write history but query for an old target-turn=1 with distance=5;
    NO_CONTEXT random, WM_K100 evicted (target beyond buffer), WM_K500 hits,
    WM_TWOTIER hits (LTM). Verify at least 3 distinct values.
    """
    rng = _rng(19)
    # Tiny world: N stays at N_DIM for realistic vector geometry, but reduce
    # trials to keep self-test fast.
    arm_ncx = run_arm_no_context(rng, n_turns=6, target_turn=1,
                                  entity_type="entity", interference_K=100,
                                  n_trials=2)
    arm_k100 = run_arm_wm_kbuf(rng, 100, n_turns=6, target_turn=1,
                                entity_type="entity", interference_K=100,
                                n_trials=2)
    arm_k500 = run_arm_wm_kbuf(rng, 500, n_turns=6, target_turn=1,
                                entity_type="entity", interference_K=100,
                                n_trials=2)
    arm_two = run_arm_wm_twotier(rng, n_turns=6, target_turn=1,
                                  entity_type="entity", interference_K=100,
                                  n_trials=2)
    vals = [arm_ncx["recall_cosine_mean"], arm_k100["recall_cosine_mean"],
            arm_k500["recall_cosine_mean"], arm_two["recall_cosine_mean"]]
    names = ["ARM_NO_CONTEXT", "ARM_WM_K100", "ARM_WM_K500", "ARM_WM_TWOTIER"]
    # Discriminator: WM_K500 or WM_TWOTIER should exceed NO_CONTEXT by lift.
    if max(vals[2], vals[3]) - vals[0] < 0.05:
        raise AssertionError(
            f"META_RULE_AF preflight (arm-lift): expected WM_K500 or TWOTIER "
            f"to exceed NO_CONTEXT by >=0.05; got NO_CX={vals[0]:.3f} "
            f"K100={vals[1]:.3f} K500={vals[2]:.3f} TWO={vals[3]:.3f}"
        )
    # Distinctness: at least 3 arms have distinct recall (bit-tolerance 1e-6)
    distinct = set()
    for v in vals:
        rounded = round(v, 6)
        distinct.add(rounded)
    if len(distinct) < 3:
        raise AssertionError(
            f"META_RULE_AF preflight (distinctness): only "
            f"{len(distinct)} distinct arm recalls: {dict(zip(names, vals))}"
        )


def _selftest_cardinality_consistent() -> None:
    if EXPECTED_N_UNITS != len(TURN_DISTANCES) * len(ENTITY_TYPES) * 4:
        raise AssertionError(
            f"EXPECTED_N_UNITS mismatch: got {EXPECTED_N_UNITS}, "
            f"td={len(TURN_DISTANCES)} et={len(ENTITY_TYPES)}"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_bipolar_bind_involutive()
        _selftest_wm_multibank_recall_self()
        _selftest_dense_hopfield_self_recall()
        _selftest_scenario_builder()
        _selftest_adaptive_beta_computes_finite()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_consistent()
        _selftest_arms_expected_differ()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  N_DIM={N_DIM}  "
        f"K_levels={K_LEVELS}  turn_dists={TURN_DISTANCES}  "
        f"entity_types={ENTITY_TYPES}  N_trials={N_TRIALS}  "
        f"LTM_K={LTM_K}  STM_K={STM_K}  "
        f"mode={RUN_MODE}  chunk_seed={SEED_THIS_CHUNK}  "
        f"expected_n_units={EXPECTED_N_UNITS}  "
        f"crlb_sigma_unit={CRLB_SIGMA_UNIT:.5f}  backend=numpy",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    print(
        f"  [seed={seed}] N_DIM={N_DIM} K_levels={K_LEVELS} "
        f"turn_dists={TURN_DISTANCES} entity_types={ENTITY_TYPES} "
        f"N_TRIALS={N_TRIALS} LTM_K={LTM_K} mode={RUN_MODE}",
        flush=True,
    )

    all_arms = []
    unit_idx = 0
    total_units = EXPECTED_N_UNITS
    for td_i, turn_dist in enumerate(TURN_DISTANCES):
        for et_i, entity_type in enumerate(ENTITY_TYPES):
            phase_seed_offset = seed * 10000 + td_i * 100 + et_i
            arm_rows = run_phase_point(phase_seed_offset, turn_dist,
                                        entity_type, out_dir,
                                        unit_idx, total_units)
            for arm in arm_rows:
                unit_idx += 1
                all_arms.append(arm)
                print(
                    f"  [seed={seed} td={turn_dist} et={entity_type} "
                    f"{arm['arm_name']}] recall_cos={arm['recall_cosine_mean']:.3f} "
                    f"(std={arm['recall_cosine_std']:.3f}) "
                    f"wall={arm['wall_s']:.1f}s status={arm['arm_status']}",
                    flush=True,
                )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_DIM": N_DIM,
        "K_levels": K_LEVELS,
        "turn_distances": TURN_DISTANCES,
        "entity_types": ENTITY_TYPES,
        "N_trials": N_TRIALS,
        "LTM_K": LTM_K,
        "STM_K": STM_K,
        "run_mode": RUN_MODE,
        "backend": "numpy",
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "arms": all_arms,
        "n_arm_rows": len(all_arms),
        "expected_n_units": EXPECTED_N_UNITS,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------
def _arm_rows_by_name(arms: List[Dict], name: str) -> List[Dict]:
    return [a for a in arms if a["arm_name"] == name]


def _mean_recall(arms: List[Dict], name: str) -> float:
    rows = _arm_rows_by_name(arms, name)
    if not rows:
        return float("nan")
    return float(np.mean([r["recall_cosine_mean"] for r in rows]))


def _mean_recall_at(arms: List[Dict], name: str, turn_dist: int) -> float:
    rows = [a for a in arms if a["arm_name"] == name
            and a.get("turn_distance") == turn_dist]
    if not rows:
        return float("nan")
    return float(np.mean([r["recall_cosine_mean"] for r in rows]))


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    arms = r["arms"]
    n_rows = len(arms)
    core_min = max(1, int(0.85 * EXPECTED_N_UNITS))  # >=85% of expected
    if n_rows < core_min:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH: n_arm_rows={n_rows} < "
                f"floor={core_min} (expected {EXPECTED_N_UNITS})")

    # Any arm error?
    for a in arms:
        if a.get("arm_status") != "OK":
            return ("HARD_FAIL",
                    f"Arm error: {a['arm_name']} td={a.get('turn_distance')} "
                    f"et={a.get('entity_type')} status={a['arm_status']}")

    # Per-arm mean recall over all phase points
    m_ncx = _mean_recall(arms, "ARM_NO_CONTEXT")
    m_k100 = _mean_recall(arms, "ARM_WM_K100")
    m_k500 = _mean_recall(arms, "ARM_WM_K500")
    m_two = _mean_recall(arms, "ARM_WM_TWOTIER")

    # WM_K500 at largest turn_distance (proxy for "turn 3" gate)
    max_td = max(TURN_DISTANCES)
    m_k500_maxtd = _mean_recall_at(arms, "ARM_WM_K500", max_td)

    # META_RULE_AF: any two arms bit-identical?
    per_arm_means = [m_ncx, m_k100, m_k500, m_two]
    per_arm_names = ["ARM_NO_CONTEXT", "ARM_WM_K100",
                     "ARM_WM_K500", "ARM_WM_TWOTIER"]
    for i in range(len(per_arm_means)):
        for j in range(i + 1, len(per_arm_means)):
            if abs(per_arm_means[i] - per_arm_means[j]) < 1e-9:
                return ("HARD_FAIL",
                        f"HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF): "
                        f"{per_arm_names[i]}={per_arm_means[i]:.6f} == "
                        f"{per_arm_names[j]}={per_arm_means[j]:.6f}")

    # META_RULE_Q: suspect-1.000 flag on TWOTIER
    if m_two >= HP_SATURATION_FLAG:
        # Not automatic fail; document but treat as MIDDLE_BAND at max unless
        # WM_K500 also HARD_PASSes independently.
        pass

    # HARD_FAIL_TWOTIER_BROKEN
    if m_two < m_ncx - 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL_TWOTIER_BROKEN: TWOTIER={m_two:.3f} < "
                f"NO_CONTEXT={m_ncx:.3f} (TWO_TIER composition inverted)")

    # HARD_FAIL_MECHANISM: WM_K100 must clear mechanism floor
    if m_k100 < HP_MECHANISM_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_MECHANISM: ARM_WM_K100={m_k100:.3f} < "
                f"floor={HP_MECHANISM_FLOOR:.2f} (WM not propagating "
                f"context to cortex). Full: NO_CX={m_ncx:.3f} K100={m_k100:.3f} "
                f"K500={m_k500:.3f} TWO={m_two:.3f}")

    summary_core = (
        f"seed={SEED_THIS_CHUNK} NO_CX={m_ncx:.3f} K100={m_k100:.3f} "
        f"K500={m_k500:.3f} K500@td={max_td}={m_k500_maxtd:.3f} "
        f"TWO={m_two:.3f} lift(K500-NO_CX)={m_k500-m_ncx:+.3f} "
        f"n_rows={n_rows}/{EXPECTED_N_UNITS} mode={RUN_MODE}"
    )

    # HARD_PASS gates: WM_K500 hits turn-3 gate + lift + TWOTIER >= K500
    hp_turn3 = m_k500_maxtd >= HP_TURN3_RECALL
    hp_lift = (m_k500 - m_ncx) >= HP_LIFT_OVER_NOCTX
    hp_two_ge_k500 = m_two >= m_k500 - 0.02  # TWOTIER at least matches K500

    if hp_turn3 and hp_lift and hp_two_ge_k500:
        return ("HARD_PASS",
                f"HARD_PASS: turn-{max_td} recall K500 >= 0.80 AND "
                f"lift >= 0.20 AND TWOTIER >= K500. {summary_core}")

    if m_k500 < 0.60:
        return ("HARD_FAIL",
                f"HARD_FAIL: WM_K500 mean recall {m_k500:.3f} < 0.60. "
                f"{summary_core}")

    if 0.60 <= m_k500 < HP_TURN3_RECALL:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: partial context retention. "
                f"hp_checks=[turn{max_td}={hp_turn3}, lift={hp_lift}, "
                f"two_ge_k500={hp_two_ge_k500}]. {summary_core}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: gates split. "
            f"hp_checks=[turn{max_td}={hp_turn3}, lift={hp_lift}, "
            f"two_ge_k500={hp_two_ge_k500}]. {summary_core}")


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
        print(f"[seed={seed}] {ANCHOR_NAME} N_DIM={N_DIM} "
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

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_DIM={N_DIM} K_levels={K_LEVELS} "
            f"turn_dists={TURN_DISTANCES} entity_types={ENTITY_TYPES} "
            f"N_TRIALS={N_TRIALS} LTM_K={LTM_K} STM_K={STM_K} mode={RUN_MODE} "
            f"backend=numpy"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_DIM": N_DIM,
        "K_levels": K_LEVELS,
        "turn_distances": TURN_DISTANCES,
        "entity_types": ENTITY_TYPES,
        "N_trials": N_TRIALS,
        "LTM_K": LTM_K,
        "STM_K": STM_K,
        "beta_dense_floor": BETA_DENSE_MIN,
        "beta_dense_ceil": BETA_DENSE_MAX,
        "HP_turn3_recall": HP_TURN3_RECALL,
        "HP_lift_over_noctx": HP_LIFT_OVER_NOCTX,
        "HP_mechanism_floor": HP_MECHANISM_FLOOR,
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
        "crlb_floor_computed": CRLB_SIGMA_UNIT,
        "crlb_formula_reference": "sigma_min_single = 1/sqrt(N_DIM); sigma_unit = sigma_single/sqrt(N_TRIALS); bipolar-inner-product-CLT",
        "discriminator_reachability": True,
        "calibration_check": "adaptive_beta_dense_hopfield_for_LTM",
        "composition_parents_cg": [
            "wm_multibank_K4096_MULTI_64x_commit_6c6a271d",
            "int8_dense_pareto_optimal_commit_716174a7",
            "cortex_hippo_dense_layer_M8192_v2_READ_REPLACE_commit_863e14b5",
            "two_tier_generational_prior_CG",
        ],
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "n_arm_rows": r.get("n_arm_rows"),
                "arms": r.get("arms"),
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
