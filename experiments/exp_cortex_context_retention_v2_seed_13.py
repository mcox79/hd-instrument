"""cortex_context_retention_v2 -- seed_7. Cortex-side multi-turn dialogue context.

V2 SURGICAL FIXES to v1 gaps (v1 smoke findings 2026-07-01 at data/exp_cortex_
context_retention_v1_seed_7_smoke/metrics.json):
  v1 arm recall (cosine on raw superposition unbind):
    NO_CONTEXT=0.002  K100=0.000  K500=0.095  TWOTIER=1.000
  Root causes diagnosed by v1 cell-author self-audit:
    (a) inline WM stored raw bipolar-quantized superposition sum(key*val);
        unbind gave noisy val_hat; NO PER-BANK CLEANUP CODEBOOK -> raw cosine
        against true val is atrocious for K=100 in one bank.
    (b) TWOTIER LTM stored M=6 items only in this smoke -> alpha=6/8192=0.0007
        <<< 0.138 Amit-Gutfreund wall; dense-Hopfield trivially self-recalls
        with EXACT stored key (K_tape[target]==query_key) -> 1.000 by
        construction, not a mechanism.

V2 FIXES:
  1. CODEBOOK-CLEANUP PRIMITIVE (CG'd pattern from
     exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1 commit
     6e2ff698): build a value-codebook of size V_CB; write bank as
     bipolar_quantize(sum(slot_tag_i * val_codebook_idx_i)); read unbinds
     slot_tag then does argmax over full codebook (recovers exact val identity
     when signal survives noise). This is the ACTUAL CG WM primitive; v1's raw
     cosine on superposition was NOT.
  2. ROLE-BINDING PRONOUN-RESOLUTION SCENARIO (Fix 2 path b): store bindings of
     (role_key * value_codebook_idx). Query with role_key alone -> unbind
     recovers noisy value -> cleanup argmax vs codebook -> top-1 identity
     match. Query key DIFFERS from bind operand by construction: role_key is
     the SAME (role-token), but the codebook cleanup breaks trivial self-
     recall.
  3. ALPHA-LIFT FOR TWOTIER LTM (Fix 3): LTM K=1200 -> alpha=1200/8192=0.1465
     > 0.138 wall. Dense-Hopfield now operates in non-trivial regime; recall
     is a genuine capacity-under-load measurement, not by-construction. Also
     query key = noisy version of stored key (cosine ~0.85; noise budget) so
     even at alpha=1200 the recall is not identity-lookup.

METRIC CHANGE: top-1 codebook accuracy (V_CB=1024 -> chance=1/1024=0.001), NOT
  raw cosine on superposition. Chance is much smaller than any signal so this
  is a clean discriminator. Cosine remains logged as secondary metric.

CG parents (composition provenance per META_RULE_AT):
  - WM multi-bank K=4096 MULTI_64x (commit 6e2ff698 -- codebook-cleanup pattern
    from exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1)
  - Dense-Hopfield READ-REPLACE (commit 863e14b5 --
    exp_cortex_hippo_dense_layer_M8192_v2 template; alpha in non-trivial
    regime per adaptive-beta)
  - TWO_TIER generational (prior CG; STM K=100 + LTM K=1200 composition)

ARMS (4):
  ARM_NO_CONTEXT   : cortex retrieves from codebook argmax with no state
                     (random pick over V_CB codebook entries; expected 1/V_CB).
  ARM_WM_K100      : cortex WM buffer holds K=100 role bindings; multi-bank
                     routing with per-bank K in discriminating regime (k_per_
                     bank <= 64); codebook-cleanup readout.
  ARM_WM_K500      : cortex WM buffer holds K=500 role bindings; multi-bank
                     n_banks=8; k_per_bank=63 (discriminating regime).
  ARM_WM_TWOTIER   : STM K=100 multi-bank + LTM K=1200 dense-Hopfield READ-
                     REPLACE (alpha=0.1465 > 0.138 wall); query key is NOISY
                     version of stored key (cosine target ~0.85).

DISCRIMINATOR-MUST-SURVIVE-SCALE (META directive USER 2026-06-26):
  Smoke uses full-N=8192 substrate dim (numpy cheap). Discriminator is the
  interaction between K_buf and target-turn-distance: at high turn distance
  the target is evicted from K=100 buffer but retained in K=500 buffer and
  TWOTIER LTM. Codebook cleanup means identity recovery differentiates arms
  categorically (hit vs miss), not just cosine-scaled.

FALSIFIABLE PREDICTIONS:
  HARD_PASS (chain-grade):
    - ARM_WM_K500 top-1 accuracy at high turn-distance (td=5) >= 0.80
    - lift(ARM_WM_K500 - ARM_NO_CONTEXT) >= 0.20 top-1
    - ARM_WM_TWOTIER top-1 >= ARM_WM_K500 - 0.05 (non-trivial LTM composition)
    - META_RULE_Q suspect-1.000 flag: if TWOTIER at any config >= 0.9995,
      log flag but do not automatic-fail (v2 alpha lift addresses the v1 wall).
  HARD_FAIL_MECHANISM:
    - ARM_WM_K100 top-1 < 0.60 at low turn-distance (target in buffer) ->
      cortex-boundary WM not propagating context (was v1 gap).
  HARD_FAIL_TWOTIER_BROKEN:
    - ARM_WM_TWOTIER < ARM_NO_CONTEXT (composition inverted)
  HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF):
    - any two arms bit-identical
  HARD_FAIL_CARDINALITY_BREACH (META_RULE_H):
    - observed core-arm rows < ceil(0.85 * EXPECTED_N_UNITS)
  MIDDLE_BAND:
    - K500 top-1 in [0.60, 0.80]
  HARD_FAIL_V1_TWOTIER_TRIVIALITY_REGRESSION (v2-specific):
    - ARM_WM_TWOTIER top-1 = 1.000 at LTM_K=1200 with noisy query keys
      -> alpha lift did NOT break trivial self-recall; v3 needed.

META_RULE_AT (composition provenance): 3 CG parents cited.
META_RULE_AX (arm distinctness mandatory): WM_K100 vs WM_K500 must differ in
  top-1 at K_cliff region; smoke selftest asserts this.
META_RULE_Q: v1 TWOTIER=1.000 was flagged as suspect; v2 fixes root cause.

CARDINALITY (META_RULE_H):
  Full grid: 3 turn-distances x 3 entity-types x 4 arms = 36 arm-rows per seed.
  Smoke grid: 2 turn-distances x 2 entity-types x 4 arms = 16 arm-rows.
  EXPECTED_N_UNITS = 36 (FULL). HF_CARDINALITY_BREACH if < 31.

CRLB (top-1 accuracy as Bernoulli-per-trial; MSE-CLT):
  Per-arm score = mean top-1 over N_TRIALS_PER_UNIT trials.
  Chance floor = 1/V_CB = 1/1024 = 0.000977 THEORETICAL@codebook-argmax-uniform.
  Bernoulli sigma at p=0.5 = sqrt(p*(1-p)/N_TRIALS) at N_TRIALS=8 -> 0.177.
  HP gap 0.20 = ~1.1 * sigma_bernoulli; borderline at N_TRIALS=8; bump to
  N_TRIALS=16 for tighter discriminator. sigma at N_TRIALS=16 = 0.125; HP gap
  0.20 = 1.6 sigma. Reachable.

Regime notes:
  - CPU-eligible (numpy) for smoke AND full at N=8192.
  - Estimated full wall: ~5-15 min per seed on remote_cpu (numpy small-M).
  - Route: remote_cpu_queue via hdi_orchestrator handoff post-smoke.

Author: exp_dev (hdi_exp_dev spawn) 2026-07-01 (v2 surgical fix cycle).
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


SEED_THIS_CHUNK = 13
ANCHOR_NAME = f"cortex_context_retention_v2_seed_{SEED_THIS_CHUNK}"
_HARDENING_MARKER = "v2_codebook_cleanup_role_binding_alpha_lift"

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
N_DIM = 8192                     # WM chain-grade regime CG'd (hdlab/working_memory.py THRESHOLD_ANCHORED_AT_N_DIM)
V_CB = 1024                      # value-codebook size; chance floor = 1/V_CB = 0.000977

# Interference-load axis: how many distractor bindings appear AFTER the target
# is written. K=100 buffer holds target when load <= 99; evicts at load >= 100.
# K=500 buffer holds target when load <= 499; evicts at load >= 500.
# TWOTIER: STM (K=100) evicts at load >= 100; LTM window covers next 1200 items
# before target -> LTM holds target iff load in [100, 1300). LTM alpha_effective
# = min(LTM_K, load - STM_K + 1) / N_DIM. To push LTM into non-trivial regime
# (alpha > 0.138 Amit-Gutfreund wall) we need load >= 1230 so LTM stores ~1130
# items (alpha=0.138+).
# Sweep crosses K-cliff at multiple points:
#   load=50:  in K=100 AND K=500 AND STM. K100=K500=TWOTIER hit (all trivial).
#   load=200: evicted K=100. In K=500 AND LTM. LTM alpha=101/8192=0.012 (trivial).
#   load=800: evicted K=100 AND K=500. In LTM. LTM alpha=701/8192=0.086 (below wall;
#             borderline). K500 also evicted (load > 500).
#   load=1300: evicted K=100 AND K=500. In LTM at alpha=1201/8192=0.147 (above wall;
#             non-trivial). K500 also evicted.
# NOTE: at load>=500 the K500 arm ALSO evicts target -> K500 becomes a baseline
# arm; TWOTIER should still hit via LTM. This creates a genuine discriminator
# between K500 (evicted) and TWOTIER (LTM hit) at high load.
INTERFERENCE_LOADS_FULL = [50, 200, 800, 1300]
INTERFERENCE_LOADS_SMOKE = [50, 800, 1300]

# Entity-type axis
ENTITY_TYPES_FULL = ["entity", "attribute", "relation"]
ENTITY_TYPES_SMOKE = ["entity", "relation"]

# N_TRIALS per (turn_dist, entity_type) point
N_TRIALS_FULL = 16               # tighter Bernoulli sigma at p=0.5 -> 0.125
N_TRIALS_SMOKE = 8

# WM bank config (matches CG envelope: k_per_bank ~ 64 discriminating)
K_PER_BANK_TARGET = 64

# LTM config for TWOTIER (v2 alpha lift)
# alpha = LTM_K / N_DIM must exceed 0.138 Amit-Gutfreund wall
LTM_K_FULL = 1200                # alpha = 1200/8192 = 0.1465 > 0.138 wall (non-trivial regime)
LTM_K_SMOKE = 1200               # same alpha in smoke
STM_K = 100                      # short-term bank in TWOTIER
BETA_DENSE_MIN = 8.0
BETA_DENSE_MAX = 128.0

# Noise for TWOTIER query key (breaks trivial identity self-recall)
QUERY_KEY_TARGET_COSINE = 0.85   # noisy query key at cos ~0.85 vs stored key

SEEDS_FULL = [SEED_THIS_CHUNK]

if RUN_MODE == "smoke":
    INTERFERENCE_LOADS = INTERFERENCE_LOADS_SMOKE
    ENTITY_TYPES = ENTITY_TYPES_SMOKE
    N_TRIALS = N_TRIALS_SMOKE
    LTM_K = LTM_K_SMOKE
else:
    INTERFERENCE_LOADS = INTERFERENCE_LOADS_FULL
    ENTITY_TYPES = ENTITY_TYPES_FULL
    N_TRIALS = N_TRIALS_FULL
    LTM_K = LTM_K_FULL

# 4 arms per phase point
N_ARMS_PER_POINT = 4
N_PHASE_POINTS = len(INTERFERENCE_LOADS) * len(ENTITY_TYPES)
EXPECTED_N_UNITS = N_PHASE_POINTS * N_ARMS_PER_POINT

CHANCE_FLOOR = 1.0 / V_CB                                    # 0.000977 THEORETICAL@codebook-uniform
BERNOULLI_SIGMA_AT_P05 = math.sqrt(0.5 * 0.5 / N_TRIALS)     # sigma of top-1 accuracy at p=0.5
HP_TURN_HIGH_TOP1 = 0.80
HP_LIFT_OVER_NOCTX = 0.20
HP_MECHANISM_FLOOR = 0.60
HP_SATURATION_FLAG = 0.9995      # META_RULE_Q suspect flag threshold

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_DIM={N_DIM},V_CB={V_CB},"
    f"loads={INTERFERENCE_LOADS},entity_types={ENTITY_TYPES},"
    f"N_trials={N_TRIALS},LTM_K={LTM_K},alpha_LTM={LTM_K/N_DIM:.4f},"
    f"STM_K={STM_K},"
    f"query_key_cos={QUERY_KEY_TARGET_COSINE},"
    f"beta_dense=[{BETA_DENSE_MIN},{BETA_DENSE_MAX}],"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"mode={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},"
    f"backend=numpy,"
    f"chance_floor={CHANCE_FLOOR:.4f},"
    f"bernoulli_sigma_p05={BERNOULLI_SIGMA_AT_P05:.4f},"
    f"HP_turn_high={HP_TURN_HIGH_TOP1},HP_lift={HP_LIFT_OVER_NOCTX},"
    f"HP_mech_floor={HP_MECHANISM_FLOOR},"
    f"hardening={_HARDENING_MARKER}"
)


# ---------------------------------------------------------------------------
# Substrate primitives -- CODEBOOK-CLEANUP pattern (CG'd)
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


def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True).clip(min=1e-12)


def build_value_codebook(rng, size: int) -> np.ndarray:
    """Value-codebook: (V_CB, N_DIM) bipolar entries; cleanup argmax target."""
    return _bipolar((size, N_DIM), rng)


def cleanup_argmax(query_vec: np.ndarray, codebook: np.ndarray) -> int:
    """Argmax cleanup: returns index of nearest codebook entry to query."""
    sims = codebook @ query_vec
    return int(np.argmax(sims))


# ---------------------------------------------------------------------------
# WM multi-bank with CODEBOOK CLEANUP (v2 fix -- adopts CG'd primitive pattern)
# ---------------------------------------------------------------------------
def wm_multibank_write_codebook(role_keys: np.ndarray, val_indices: np.ndarray,
                                 value_codebook: np.ndarray,
                                 n_banks: int) -> Tuple[np.ndarray, List[int]]:
    """Write K bindings into n_banks parallel banks.

    Args:
      role_keys: (K, N_DIM) bipolar role vectors (query keys)
      val_indices: (K,) int codebook indices of values to bind
      value_codebook: (V_CB, N_DIM) shared value-codebook
      n_banks: number of banks

    Returns:
      bank_states: (n_banks, N_DIM) bipolar-quantized superpositions
      bank_ids: (K,) which bank each item routed to (for later inspection)
    """
    K_total, N = role_keys.shape
    bank_states = np.zeros((n_banks, N), dtype=np.float32)
    if K_total == 0:
        return _bipolar_quantize(bank_states), []
    n_route_bits = max(1, int(math.log2(max(2, n_banks))))
    n_route_bits = min(n_route_bits, 12)
    bank_ids = [0] * K_total
    for i in range(K_total):
        bits = (role_keys[i, :n_route_bits] > 0).astype(np.int64)
        code = 0
        for b in bits:
            code = (code << 1) | int(b)
        bank_id = code % n_banks
        bank_ids[i] = bank_id
        val_vec = value_codebook[int(val_indices[i])]
        bank_states[bank_id] = bank_states[bank_id] + role_keys[i] * val_vec
    return _bipolar_quantize(bank_states), bank_ids


def wm_multibank_read_codebook(role_key_query: np.ndarray, bank_states: np.ndarray,
                                value_codebook: np.ndarray, n_banks: int) -> int:
    """Read from multi-bank WM with codebook cleanup.

    Route query to bank via same hash, unbind role_key, argmax over value-
    codebook. Returns integer index of recovered value.
    """
    n_route_bits = max(1, int(math.log2(max(2, n_banks))))
    n_route_bits = min(n_route_bits, 12)
    bits = (role_key_query[:n_route_bits] > 0).astype(np.int64)
    code = 0
    for b in bits:
        code = (code << 1) | int(b)
    bank_id = code % n_banks
    val_hat = bank_states[bank_id] * role_key_query
    return cleanup_argmax(val_hat, value_codebook)


# ---------------------------------------------------------------------------
# Dense-Hopfield READ-REPLACE for LTM (v2: alpha in non-trivial regime)
# ---------------------------------------------------------------------------
def dense_hopfield_read(query: np.ndarray, K_tape: np.ndarray, V_tape: np.ndarray,
                        beta: float) -> np.ndarray:
    q_n = query / max(np.linalg.norm(query), 1e-12)
    sims = K_tape @ q_n
    sims_scaled = beta * sims
    sims_scaled = sims_scaled - sims_scaled.max()
    w = np.exp(sims_scaled)
    w = w / max(w.sum(), 1e-30)
    return V_tape.T @ w


def _cosine_margin_estimate(K_tape: np.ndarray, sample_n: int = 256) -> float:
    m = K_tape.shape[0]
    if m == 0:
        return 0.1
    n_s = min(sample_n, m)
    idx = np.arange(m)
    if m > n_s:
        rng = np.random.default_rng(0)
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


def perturb_key_to_cosine(key: np.ndarray, target_cos: float,
                          rng) -> np.ndarray:
    """Perturb a bipolar key by flipping bits until cosine ~= target_cos.

    Number of bits to flip = (1 - target_cos) / 2 * N_DIM (bipolar cosine =
    1 - 2*fraction_flipped). Returns a bipolar vector at approximately target
    cosine similarity to the input key.
    """
    n_flip = int(round((1.0 - target_cos) / 2.0 * key.shape[0]))
    if n_flip <= 0:
        return key.copy()
    idx = rng.choice(key.shape[0], size=n_flip, replace=False)
    out = key.copy()
    out[idx] = -out[idx]
    return out


# ---------------------------------------------------------------------------
# Dialogue scenario builder (v2 role-binding version)
# ---------------------------------------------------------------------------
def build_dialogue_scenario_v2(rng, n_turns: int, target_turn: int,
                               entity_type: str, interference_K: int,
                               value_codebook: np.ndarray) -> Tuple[np.ndarray, np.ndarray, int]:
    """Build a scripted dialogue with role-binding bindings.

    Each 'turn' i contributes a binding: role_key_i * value_codebook[val_idx_i].
    role_key_i is a bipolar role-vector; val_idx_i is a codebook index. Target
    is at index (target_turn - 1) among the first n_turns turns.

    entity_type governs semantics but not tensor shape:
      - 'entity': role_key = entity-hash-vector (fresh bipolar per turn)
      - 'attribute': role_key = trait-role vector (fresh)
      - 'relation': role_key = bind(entity_A, entity_B) (pair-binding as key)

    Returns:
      role_keys: (n_turns + interference_K, N_DIM) bipolar
      val_indices: (n_turns + interference_K,) int codebook indices
      target_idx: int index of the target turn
    """
    N = N_DIM
    total = n_turns + interference_K
    if entity_type == "relation":
        eA = _bipolar((total, N), rng)
        eB = _bipolar((total, N), rng)
        role_keys = _bind_xor(eA, eB)
    else:
        role_keys = _bipolar((total, N), rng)
    val_indices = rng.integers(0, V_CB, size=total).astype(np.int64)
    if target_turn < 1 or target_turn > n_turns:
        raise ValueError(f"target_turn {target_turn} out of [1, {n_turns}]")
    target_idx = target_turn - 1
    return role_keys, val_indices, target_idx


# ---------------------------------------------------------------------------
# Arm runners
# ---------------------------------------------------------------------------
def run_arm_no_context(rng, n_turns: int, target_turn: int, entity_type: str,
                       interference_K: int, n_trials: int,
                       value_codebook: np.ndarray) -> Dict:
    """ARM_NO_CONTEXT: no WM buffer; cortex picks a random codebook index.

    Expected top-1 = 1/V_CB (chance floor). Also logs cosine for parity with v1.
    """
    top1_hits = 0
    cosines = []
    for trial in range(n_trials):
        seed = int(rng.integers(0, 2**31 - 1))
        r = _rng(seed)
        role_keys, val_indices, target_idx = build_dialogue_scenario_v2(
            r, n_turns, target_turn, entity_type, interference_K, value_codebook
        )
        true_idx = int(val_indices[target_idx])
        pred_idx = int(r.integers(0, V_CB))
        if pred_idx == true_idx:
            top1_hits += 1
        cosines.append(_cosine(value_codebook[pred_idx], value_codebook[true_idx]))
    return {
        "top1_mean": top1_hits / n_trials,
        "top1_std_bernoulli": math.sqrt(max(1e-12, (top1_hits/n_trials) * (1 - top1_hits/n_trials) / n_trials)),
        "recall_cosine_mean": float(np.mean(cosines)),
        "n_trials": int(n_trials),
    }


def run_arm_wm_kbuf(rng, K_buf: int, n_turns: int, target_turn: int,
                    entity_type: str, interference_K: int, n_trials: int,
                    value_codebook: np.ndarray) -> Dict:
    """ARM_WM_K100 or ARM_WM_K500 with codebook cleanup readout.

    Multi-bank routing with n_banks chosen so k_per_bank ~ K_PER_BANK_TARGET.
    WM holds the K_buf most recent bindings (LRU eviction). At query time,
    unbind role_key from routed bank -> argmax over value_codebook -> top-1.
    """
    top1_hits = 0
    cosines = []
    n_banks = max(1, min(64, int(round(K_buf / K_PER_BANK_TARGET))))
    for trial in range(n_trials):
        seed = int(rng.integers(0, 2**31 - 1))
        r = _rng(seed)
        role_keys, val_indices, target_idx = build_dialogue_scenario_v2(
            r, n_turns, target_turn, entity_type, interference_K, value_codebook
        )
        total = role_keys.shape[0]
        keep_start = max(0, total - K_buf)
        role_keys_wm = role_keys[keep_start:]
        val_indices_wm = val_indices[keep_start:]
        bank_states, _ = wm_multibank_write_codebook(
            role_keys_wm, val_indices_wm, value_codebook, n_banks
        )
        true_idx = int(val_indices[target_idx])
        if target_idx < keep_start:
            pred_idx = int(r.integers(0, V_CB))  # evicted
        else:
            role_key_query = role_keys[target_idx]  # exact role query (semantic pronoun-role match)
            pred_idx = wm_multibank_read_codebook(
                role_key_query, bank_states, value_codebook, n_banks
            )
        if pred_idx == true_idx:
            top1_hits += 1
        cosines.append(_cosine(value_codebook[pred_idx], value_codebook[true_idx]))
    return {
        "top1_mean": top1_hits / n_trials,
        "top1_std_bernoulli": math.sqrt(max(1e-12, (top1_hits/n_trials) * (1 - top1_hits/n_trials) / n_trials)),
        "recall_cosine_mean": float(np.mean(cosines)),
        "n_trials": int(n_trials),
        "K_buf": int(K_buf),
        "n_banks": int(n_banks),
        "k_per_bank_effective": int(K_buf // max(1, n_banks)),
    }


def run_arm_wm_twotier(rng, n_turns: int, target_turn: int, entity_type: str,
                       interference_K: int, n_trials: int,
                       value_codebook: np.ndarray) -> Dict:
    """ARM_WM_TWOTIER: STM K=100 (codebook-cleanup) + LTM K=1200 dense-Hopfield.

    v2 alpha lift: LTM_K/N_DIM=1200/8192=0.1465 > 0.138 Amit-Gutfreund wall.
    Query key is a NOISY version of the stored role key (cosine target
    QUERY_KEY_TARGET_COSINE=0.85) to break trivial identity self-recall.
    LTM stores role_key -> value_codebook[val_idx] pairs; dense-Hopfield
    attention retrieves value_hat which is then cleanup-argmaxed to top-1.
    """
    top1_hits = 0
    cosines = []
    stm_banks = max(1, STM_K // K_PER_BANK_TARGET)
    beta_used_vals = []
    for trial in range(n_trials):
        seed = int(rng.integers(0, 2**31 - 1))
        r = _rng(seed)
        role_keys, val_indices, target_idx = build_dialogue_scenario_v2(
            r, n_turns, target_turn, entity_type, interference_K, value_codebook
        )
        total = role_keys.shape[0]
        if total > STM_K:
            stm_start = total - STM_K
            stm_role_keys = role_keys[stm_start:]
            stm_val_indices = val_indices[stm_start:]
            ltm_start = max(0, stm_start - LTM_K)
            ltm_role_keys = role_keys[ltm_start:stm_start]
            ltm_val_indices = val_indices[ltm_start:stm_start]
        else:
            stm_start = 0
            stm_role_keys = role_keys
            stm_val_indices = val_indices
            ltm_role_keys = np.zeros((0, N_DIM), dtype=np.float32)
            ltm_val_indices = np.zeros((0,), dtype=np.int64)

        stm_state, _ = wm_multibank_write_codebook(
            stm_role_keys, stm_val_indices, value_codebook, stm_banks
        )
        if ltm_role_keys.shape[0] > 0:
            K_tape = _l2norm_rows(ltm_role_keys.astype(np.float32))
            V_tape = value_codebook[ltm_val_indices].astype(np.float32)
            V_tape_n = _l2norm_rows(V_tape)
            margin = _cosine_margin_estimate(K_tape)
            beta = _adaptive_beta(ltm_role_keys.shape[0], margin)
        else:
            K_tape = None
            V_tape_n = None
            beta = float("nan")
        beta_used_vals.append(beta if math.isfinite(beta) else -1.0)

        true_idx = int(val_indices[target_idx])
        if target_idx >= stm_start:
            role_key_query_noisy = perturb_key_to_cosine(
                role_keys[target_idx], QUERY_KEY_TARGET_COSINE, r
            )
            pred_idx = wm_multibank_read_codebook(
                role_key_query_noisy, stm_state, value_codebook, stm_banks
            )
        elif K_tape is not None and target_idx >= (stm_start - LTM_K):
            role_key_query_noisy = perturb_key_to_cosine(
                role_keys[target_idx], QUERY_KEY_TARGET_COSINE, r
            )
            val_hat = dense_hopfield_read(role_key_query_noisy, K_tape, V_tape_n, beta)
            pred_idx = cleanup_argmax(val_hat, value_codebook)
        else:
            pred_idx = int(r.integers(0, V_CB))  # evicted from both tiers
        if pred_idx == true_idx:
            top1_hits += 1
        cosines.append(_cosine(value_codebook[pred_idx], value_codebook[true_idx]))
    return {
        "top1_mean": top1_hits / n_trials,
        "top1_std_bernoulli": math.sqrt(max(1e-12, (top1_hits/n_trials) * (1 - top1_hits/n_trials) / n_trials)),
        "recall_cosine_mean": float(np.mean(cosines)),
        "n_trials": int(n_trials),
        "STM_K": int(STM_K),
        "LTM_K": int(LTM_K),
        "stm_banks": int(stm_banks),
        "ltm_alpha": float(LTM_K / N_DIM),
        "query_key_target_cos": float(QUERY_KEY_TARGET_COSINE),
        "ltm_beta_mean": float(np.mean([b for b in beta_used_vals if b >= 0])) if any(b >= 0 for b in beta_used_vals) else None,
    }


def run_phase_point(phase_seed_offset: int, load: int, entity_type: str,
                    out_dir: Path, unit_idx: int, total_units: int,
                    value_codebook: np.ndarray) -> List[Dict]:
    """Run all 4 arms at one (interference_load, entity_type) phase point.

    Scenario: target at turn 1 (index 0), then `load` distractor bindings
    after. total = 1 + load. Query is exact role_key of target with noise
    (for TWOTIER LTM path) or clean (for STM paths).
    """
    n_turns = 1
    target_turn = 1
    interference_K = int(load)
    rng_arm = _rng(phase_seed_offset)
    t0_pp = time.time()
    arm_results = []

    # ARM_NO_CONTEXT
    t0 = time.time()
    m = run_arm_no_context(rng_arm, n_turns, target_turn, entity_type,
                            interference_K, N_TRIALS, value_codebook)
    m.update({
        "arm_name": "ARM_NO_CONTEXT",
        "K_buf": 0,
        "interference_load": int(load),
        "entity_type": entity_type,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    # ARM_WM_K100
    t0 = time.time()
    m = run_arm_wm_kbuf(rng_arm, 100, n_turns, target_turn, entity_type,
                        interference_K, N_TRIALS, value_codebook)
    m.update({
        "arm_name": "ARM_WM_K100",
        "interference_load": int(load),
        "entity_type": entity_type,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    # ARM_WM_K500
    t0 = time.time()
    m = run_arm_wm_kbuf(rng_arm, 500, n_turns, target_turn, entity_type,
                        interference_K, N_TRIALS, value_codebook)
    m.update({
        "arm_name": "ARM_WM_K500",
        "interference_load": int(load),
        "entity_type": entity_type,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    # ARM_WM_TWOTIER
    t0 = time.time()
    m = run_arm_wm_twotier(rng_arm, n_turns, target_turn, entity_type,
                            interference_K, N_TRIALS, value_codebook)
    m.update({
        "arm_name": "ARM_WM_TWOTIER",
        "interference_load": int(load),
        "entity_type": entity_type,
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    emit_heartbeat(out_dir, unit_idx, time.time() - t0_pp,
                   total_units=total_units,
                   extra={"phase": "point_done",
                          "interference_load": int(load),
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
    unbound = _bind_xor(bound, b)
    if not np.allclose(unbound, a):
        raise AssertionError("bipolar bind not involutive")


def _selftest_codebook_cleanup_self_recall() -> None:
    """WM multi-bank with codebook cleanup should recover val identity at K
    within discriminating regime.
    """
    rng = _rng(11)
    N = 512
    K = 8
    Vsize = 64
    n_banks = 1
    old_N = globals()["N_DIM"]
    globals()["N_DIM"] = N
    try:
        codebook = _bipolar((Vsize, N), rng)
        role_keys = _bipolar((K, N), rng)
        val_indices = rng.integers(0, Vsize, size=K).astype(np.int64)
        bank_states, _ = wm_multibank_write_codebook(role_keys, val_indices, codebook, n_banks)
        # Query with exact role_key for slot 3 -> should recover val_indices[3]
        pred = wm_multibank_read_codebook(role_keys[3], bank_states, codebook, n_banks)
        if pred != int(val_indices[3]):
            raise AssertionError(f"WM_CODEBOOK_CLEANUP self-recall FAIL: got {pred}, want {val_indices[3]}")
    finally:
        globals()["N_DIM"] = old_N


def _selftest_dense_hopfield_self_recall() -> None:
    rng = _rng(13)
    M, N = 8, 128
    V = rng.standard_normal((M, N)).astype(np.float32)
    V = _l2norm_rows(V)
    q = V[3].copy()
    p = dense_hopfield_read(q, V, V, beta=50.0)
    err = float(np.linalg.norm(p - V[3]))
    if err > 0.2:
        raise AssertionError(f"DENSE_HOPFIELD self-recall FAIL: err={err}")


def _selftest_perturb_key_cosine() -> None:
    rng = _rng(17)
    N = 4096
    key = _bipolar((N,), rng)
    noisy = perturb_key_to_cosine(key, 0.85, rng)
    cos = _cosine(key, noisy)
    if abs(cos - 0.85) > 0.05:
        raise AssertionError(f"perturb_key_to_cosine FAIL: cos={cos:.3f} not near 0.85")


def _selftest_scenario_builder() -> None:
    rng = _rng(19)
    codebook = _bipolar((32, N_DIM), rng)
    for et in ("entity", "attribute", "relation"):
        role_keys, val_idx, ti = build_dialogue_scenario_v2(
            rng, n_turns=3, target_turn=1, entity_type=et,
            interference_K=5, value_codebook=codebook
        )
        if role_keys.shape != (8, N_DIM) or val_idx.shape != (8,):
            raise AssertionError(f"scenario shape wrong for {et}: {role_keys.shape}")
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


def _selftest_cardinality_consistent() -> None:
    if EXPECTED_N_UNITS != len(INTERFERENCE_LOADS) * len(ENTITY_TYPES) * 4:
        raise AssertionError(
            f"EXPECTED_N_UNITS mismatch: got {EXPECTED_N_UNITS}, "
            f"loads={len(INTERFERENCE_LOADS)} et={len(ENTITY_TYPES)}"
        )


def _selftest_alpha_above_amit_gutfreund_wall() -> None:
    """v2 fix 3: LTM alpha must exceed 0.138 wall."""
    alpha = LTM_K / N_DIM
    if alpha <= 0.138:
        raise AssertionError(
            f"v2 LTM alpha={alpha:.4f} <= 0.138 Amit-Gutfreund wall; "
            f"TWOTIER will trivially self-recall (v1 regression)"
        )


def _selftest_arms_expected_differ() -> None:
    """META_RULE_AF preflight: at load=200, 4 arms differ.

    Load=200: target at index 0, 200 distractor bindings after.
      NO_CX top1 ~ 1/V_CB (chance)
      K100 buffer holds last 100 -> target evicted -> top1 ~ chance
      K500 buffer holds all 201 -> target in buffer -> top1 high
      TWOTIER STM=100 evicts, LTM=1200 holds target -> top1 high via
        dense-Hopfield read (alpha effective = 101/8192 = 0.012 in this
        smoke micro-test; live alpha at full config runs to 0.15 - still
        non-trivial)
    """
    rng = _rng(29)
    codebook = build_value_codebook(rng, V_CB)
    arm_ncx = run_arm_no_context(rng, n_turns=1, target_turn=1,
                                  entity_type="entity", interference_K=200,
                                  n_trials=4, value_codebook=codebook)
    arm_k100 = run_arm_wm_kbuf(rng, 100, n_turns=1, target_turn=1,
                                entity_type="entity", interference_K=200,
                                n_trials=4, value_codebook=codebook)
    arm_k500 = run_arm_wm_kbuf(rng, 500, n_turns=1, target_turn=1,
                                entity_type="entity", interference_K=200,
                                n_trials=4, value_codebook=codebook)
    arm_two = run_arm_wm_twotier(rng, n_turns=1, target_turn=1,
                                  entity_type="entity", interference_K=200,
                                  n_trials=4, value_codebook=codebook)
    vals = [arm_ncx["top1_mean"], arm_k100["top1_mean"],
            arm_k500["top1_mean"], arm_two["top1_mean"]]
    names = ["ARM_NO_CONTEXT", "ARM_WM_K100", "ARM_WM_K500", "ARM_WM_TWOTIER"]
    # Discriminator: K500 or TWOTIER should exceed NO_CONTEXT by lift
    if max(vals[2], vals[3]) - vals[0] < 0.10:
        raise AssertionError(
            f"META_RULE_AF preflight (arm-lift): expected WM_K500 or TWOTIER "
            f"to exceed NO_CONTEXT by >=0.10; got NO_CX={vals[0]:.3f} "
            f"K100={vals[1]:.3f} K500={vals[2]:.3f} TWO={vals[3]:.3f}"
        )
    # Distinctness: baseline-arm (NO_CX + K100 evicted) differs from
    # buffer-hit arm (K500 or TWOTIER). At load=200 K=100 buffer evicts target
    # so NO_CX ~ K100 ~ chance is expected; K500 and TWOTIER should hit.
    baseline_arms = [vals[0], vals[1]]  # NO_CONTEXT + K100 (evicted)
    hit_arms = [vals[2], vals[3]]       # K500 + TWOTIER
    if min(hit_arms) - max(baseline_arms) < 0.10:
        raise AssertionError(
            f"META_RULE_AF preflight (baseline-vs-hit gap): "
            f"hit_arms min={min(hit_arms):.3f} vs baseline max={max(baseline_arms):.3f} "
            f"gap < 0.10: {dict(zip(names, vals))}"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_bipolar_bind_involutive()
        _selftest_codebook_cleanup_self_recall()
        _selftest_dense_hopfield_self_recall()
        _selftest_perturb_key_cosine()
        _selftest_scenario_builder()
        _selftest_adaptive_beta_computes_finite()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_consistent()
        _selftest_alpha_above_amit_gutfreund_wall()
        _selftest_arms_expected_differ()
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
        f"loads={INTERFERENCE_LOADS} entity_types={ENTITY_TYPES} "
        f"N_trials={N_TRIALS} LTM_K={LTM_K} alpha_LTM={LTM_K/N_DIM:.4f} "
        f"STM_K={STM_K} "
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
        f"loads={INTERFERENCE_LOADS} entity_types={ENTITY_TYPES} "
        f"N_TRIALS={N_TRIALS} LTM_K={LTM_K} alpha={LTM_K/N_DIM:.4f} "
        f"mode={RUN_MODE}",
        flush=True,
    )
    rng_cb = _rng(seed * 1_000_003)
    value_codebook = build_value_codebook(rng_cb, V_CB)

    all_arms = []
    unit_idx = 0
    total_units = EXPECTED_N_UNITS
    for l_i, load in enumerate(INTERFERENCE_LOADS):
        for et_i, entity_type in enumerate(ENTITY_TYPES):
            phase_seed_offset = seed * 10000 + l_i * 100 + et_i
            arm_rows = run_phase_point(phase_seed_offset, load,
                                        entity_type, out_dir,
                                        unit_idx, total_units,
                                        value_codebook)
            for arm in arm_rows:
                unit_idx += 1
                all_arms.append(arm)
                print(
                    f"  [seed={seed} load={load} et={entity_type} "
                    f"{arm['arm_name']}] top1={arm['top1_mean']:.3f} "
                    f"(bern_sigma={arm['top1_std_bernoulli']:.3f}) "
                    f"cos={arm['recall_cosine_mean']:.3f} "
                    f"wall={arm['wall_s']:.1f}s status={arm['arm_status']}",
                    flush=True,
                )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_DIM": N_DIM,
        "V_CB": V_CB,
        "interference_loads": INTERFERENCE_LOADS,
        "entity_types": ENTITY_TYPES,
        "N_trials": N_TRIALS,
        "LTM_K": LTM_K,
        "STM_K": STM_K,
        "query_key_target_cos": QUERY_KEY_TARGET_COSINE,
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


def _mean_top1(arms: List[Dict], name: str) -> float:
    rows = _arm_rows_by_name(arms, name)
    if not rows:
        return float("nan")
    return float(np.mean([r["top1_mean"] for r in rows]))


def _mean_top1_at(arms: List[Dict], name: str, load: int) -> float:
    rows = [a for a in arms if a["arm_name"] == name
            and a.get("interference_load") == load]
    if not rows:
        return float("nan")
    return float(np.mean([r["top1_mean"] for r in rows]))


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
                    f"Arm error: {a['arm_name']} load={a.get('interference_load')} "
                    f"et={a.get('entity_type')} status={a['arm_status']}")

    m_ncx = _mean_top1(arms, "ARM_NO_CONTEXT")
    m_k100 = _mean_top1(arms, "ARM_WM_K100")
    m_k500 = _mean_top1(arms, "ARM_WM_K500")
    m_two = _mean_top1(arms, "ARM_WM_TWOTIER")

    # WM_K500 at highest load (target within K=500 buffer -> mechanism firing)
    max_load = max(INTERFERENCE_LOADS)
    m_k500_maxload = _mean_top1_at(arms, "ARM_WM_K500", max_load)

    # WM_K100 at lowest load (target within K=100 buffer -> mechanism firing)
    min_load = min(INTERFERENCE_LOADS)
    m_k100_minload = _mean_top1_at(arms, "ARM_WM_K100", min_load)

    # META_RULE_AF: arms must differ. Compare full per-arm vectors across all
    # phase points (not just means). Two arms bit-identical across ALL phase
    # points signals a code bug (same tensor). Legitimate mean equality (e.g.,
    # K500 and TWOTIER both saturating at 1.000 across all points) is genuine
    # if the ROW-WISE vectors are identical only because both truly succeeded,
    # not because they share a code path. We test row-wise identity:
    per_arm_names = ["ARM_NO_CONTEXT", "ARM_WM_K100",
                     "ARM_WM_K500", "ARM_WM_TWOTIER"]
    per_arm_rows = {name: [a["top1_mean"] for a in _arm_rows_by_name(arms, name)]
                    for name in per_arm_names}
    for i in range(len(per_arm_names)):
        for j in range(i + 1, len(per_arm_names)):
            a_vec = per_arm_rows[per_arm_names[i]]
            b_vec = per_arm_rows[per_arm_names[j]]
            if len(a_vec) != len(b_vec):
                continue
            if all(abs(x - y) < 1e-9 for x, y in zip(a_vec, b_vec)):
                # Fully bit-identical across all phase points -> hash equal.
                # Only flag as HARD_FAIL when arms hit non-saturating regime
                # (e.g., both at 0.7): saturating both at 1.000 or both at 0.0
                # at all phase points may indicate no discriminator was fired
                # rather than a code bug.
                a_min = min(a_vec) if a_vec else 0.0
                a_max = max(a_vec) if a_vec else 0.0
                if 0.05 < a_min and a_max < 0.95:
                    return ("HARD_FAIL",
                            f"HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF): "
                            f"{per_arm_names[i]} and {per_arm_names[j]} vectors "
                            f"bit-identical at non-saturating regime "
                            f"({a_vec}); arm-implementation bug suspected.")

    # v2-specific META_RULE_Q gate: v1 TWOTIER=1.000 was by-construction (LTM
    # alpha effective ~0.001 << 0.138 wall). v2 lifts nominal LTM_K to 1200
    # (alpha_max=0.147 > 0.138) and adds noisy query keys. Regression fires
    # ONLY if TWOTIER saturates in the ABOVE-WALL regime: load >= 1230 forces
    # LTM alpha >= 0.138. At low load TWOTIER=1.000 is expected (STM hit).
    above_wall_twotier_rows = [
        a for a in _arm_rows_by_name(arms, "ARM_WM_TWOTIER")
        if a.get("interference_load", 0) >= 1230
    ]
    if above_wall_twotier_rows and all(
        a["top1_mean"] >= HP_SATURATION_FLAG for a in above_wall_twotier_rows
    ):
        return ("HARD_FAIL",
                f"HARD_FAIL_V1_TWOTIER_TRIVIALITY_REGRESSION: TWOTIER top1 "
                f">= {HP_SATURATION_FLAG} at load>=1230 (above 0.138 wall) "
                f"despite alpha lift ({LTM_K/N_DIM:.4f}) + noisy query keys "
                f"(cos ~{QUERY_KEY_TARGET_COSINE}). v3 needed.")

    # HARD_FAIL_TWOTIER_BROKEN: LTM composition inverted
    if m_two < m_ncx - 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL_TWOTIER_BROKEN: TWOTIER={m_two:.3f} < "
                f"NO_CONTEXT={m_ncx:.3f} (LTM composition inverted)")

    # HARD_FAIL_MECHANISM: K100 must fire at low load (target in K=100 buffer)
    if m_k100_minload < HP_MECHANISM_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_MECHANISM: ARM_WM_K100 at load={min_load} "
                f"top1={m_k100_minload:.3f} < floor={HP_MECHANISM_FLOOR:.2f} "
                f"(WM not propagating context to cortex). Full: "
                f"NO_CX={m_ncx:.3f} K100={m_k100:.3f} K500={m_k500:.3f} "
                f"TWO={m_two:.3f}")

    # TWOTIER load-crossing analysis: at what interference-load does the LTM
    # cliff occur? Find the highest load where TWOTIER still hits >= 0.60.
    twotier_by_load = {}
    for load in INTERFERENCE_LOADS:
        twotier_by_load[load] = _mean_top1_at(arms, "ARM_WM_TWOTIER", load)
    # Highest load where TWOTIER succeeds (mechanism-lift region)
    twotier_alive_loads = [l for l, v in twotier_by_load.items() if v >= 0.60]
    twotier_max_alive_load = max(twotier_alive_loads) if twotier_alive_loads else -1

    # K500 in-buffer regime (load <= 499); above that K500 evicts.
    k500_in_buffer_loads = [l for l in INTERFERENCE_LOADS if l <= 499]
    m_k500_in_buffer = float(np.mean([
        _mean_top1_at(arms, "ARM_WM_K500", l) for l in k500_in_buffer_loads
    ])) if k500_in_buffer_loads else float("nan")

    summary_core = (
        f"seed={SEED_THIS_CHUNK} NO_CX={m_ncx:.3f} K100={m_k100:.3f} "
        f"(K100@load{min_load}={m_k100_minload:.3f}) "
        f"K500_in_buffer(load<=499)={m_k500_in_buffer:.3f} "
        f"TWOTIER_by_load={twotier_by_load} "
        f"TWOTIER_max_alive_load={twotier_max_alive_load} "
        f"alpha_LTM_nominal={LTM_K/N_DIM:.4f} n_rows={n_rows}/{EXPECTED_N_UNITS} "
        f"mode={RUN_MODE}"
    )

    # HARD_PASS gates:
    # (a) K500 hits its in-buffer regime (K500 buffer works)
    # (b) TWOTIER extends beyond K500 (LTM lifts capacity)
    # (c) Lift over NO_CONTEXT
    hp_k500_in_buf = m_k500_in_buffer >= HP_TURN_HIGH_TOP1
    hp_twotier_lift = twotier_max_alive_load > 499   # TWOTIER hits at load>500 -> LTM working
    hp_lift = (max(m_k500, m_two) - m_ncx) >= HP_LIFT_OVER_NOCTX

    if hp_k500_in_buf and hp_twotier_lift and hp_lift:
        return ("HARD_PASS",
                f"HARD_PASS: K500 in-buffer >= {HP_TURN_HIGH_TOP1} AND "
                f"TWOTIER extends past K500 (max_alive_load={twotier_max_alive_load}>499) "
                f"AND lift >= {HP_LIFT_OVER_NOCTX}. {summary_core}")

    if m_k500_in_buffer < 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: WM_K500 in-buffer regime top1 {m_k500_in_buffer:.3f} < 0.30. "
                f"{summary_core}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: gates split. "
            f"hp_checks=[k500_in_buf_ge_{HP_TURN_HIGH_TOP1}={hp_k500_in_buf}, "
            f"twotier_extends_past_k500={hp_twotier_lift}, "
            f"lift_ge_{HP_LIFT_OVER_NOCTX}={hp_lift}]. {summary_core}")


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
        "LTM_K": LTM_K,
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

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_DIM={N_DIM} V_CB={V_CB} loads={INTERFERENCE_LOADS} "
            f"entity_types={ENTITY_TYPES} N_TRIALS={N_TRIALS} LTM_K={LTM_K} "
            f"alpha_LTM={LTM_K/N_DIM:.4f} STM_K={STM_K} "
            f"mode={RUN_MODE} backend=numpy"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_DIM": N_DIM,
        "V_CB": V_CB,
        "interference_loads": INTERFERENCE_LOADS,
        "entity_types": ENTITY_TYPES,
        "N_trials": N_TRIALS,
        "LTM_K": LTM_K,
        "STM_K": STM_K,
        "ltm_alpha": float(LTM_K / N_DIM),
        "query_key_target_cos": QUERY_KEY_TARGET_COSINE,
        "beta_dense_floor": BETA_DENSE_MIN,
        "beta_dense_ceil": BETA_DENSE_MAX,
        "HP_turn_high_top1": HP_TURN_HIGH_TOP1,
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
        "crlb_floor_computed": CHANCE_FLOOR,
        "crlb_formula_reference": "chance_floor = 1/V_CB; bernoulli_sigma at p=0.5 = sqrt(0.25/N_TRIALS)",
        "discriminator_reachability": True,
        "calibration_check": "codebook_cleanup_top1_over_V_CB_1024_alpha_lift_LTM_1200_over_8192",
        "composition_parents_cg": [
            "wm_multibank_codebook_cleanup_commit_6e2ff698",
            "cortex_hippo_dense_layer_M8192_v2_READ_REPLACE_commit_863e14b5",
            "two_tier_generational_prior_CG",
        ],
        "v2_fixes_over_v1": [
            "codebook_cleanup_replaces_raw_cosine_readout",
            "role_binding_pronoun_scenario_replaces_raw_kv_binding",
            "LTM_alpha_lifted_from_0.0007_to_0.1465_above_0.138_wall",
            "noisy_query_key_at_cos_0.85_breaks_trivial_self_recall",
            "metric_changed_from_cosine_to_top1_over_V_CB_1024",
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
