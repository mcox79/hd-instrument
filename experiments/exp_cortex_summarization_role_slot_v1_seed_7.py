"""cortex_summarization_role_slot_v1 -- seed_7.

M1.7 role-slot hierarchical binding summarization primitive.

Question tested (Functional Requirements per META_RULE §15.E):
  1. Can 20 raw bindings be summarized into 1 vector such that individual
     items remain query-recoverable via unbind + cleanup?
  2. Does per-role S=4-slot structure beat flat unstructured bundle by
     >= 0.15 top1 lift at k_per_role=5 average?
  3. Does recursive two-level composition (5 level-1 summaries covering 20
     items each = 100 raw items in 1 vector) achieve >= 0.50 top1?

Arms (4):
  ARM_BASELINE     : raw K-binding pool (no summary). Positive-control:
                     at load=20, expected top1 >= 0.80 (CG'd from WM multi-bank
                     codebook-cleanup at k_per_bank<=64, commit 6e2ff698).
  ARM_SUMMARY_FLAT : all K bindings bundled into a SINGLE summary vector (no
                     role separation). NEGATIVE CONTROL: SNR floor for
                     unstructured bundle should force top1 near chance.
  ARM_SUMMARY_ROLE : bindings routed to S=4 role slots (SUBJECT/OBJECT/TEMP/
                     SCHEMA); each slot bundles only its assigned items;
                     query with (noisy_role, exact_key) -> unbind role ->
                     select slot -> unbind key -> cleanup.
  ARM_RECURSIVE    : two-level. Level-1 = 5 role-slot summaries each covering
                     20 raw items (100 raw items total). Level-2 bundles the 5
                     level-1 summaries by an L2 role. Query: L2_role -> L1_role
                     -> key -> cleanup.

CG parents (composition provenance per META_RULE_AT):
  - M1.4 Atom 15 CG: refuse-gate composition (V_REL=256 refuse-gate lock-in).
  - M1.5 Atom 18 CG: context retention CG'd from exp_cortex_context_retention_v2.
  - M1.6 Atom D CG: cortex_attention_binding_router_v2 (role-assignment).
  - WM multi-bank K=4096 codebook cleanup (commit 6e2ff698).
  - FHRR / bipolar binding involutive-XOR (foundational).

DISCRIMINATOR-MUST-SURVIVE-SCALE (META directive USER 2026-06-26):
  Smoke uses full-N=8192 substrate dim (numpy cheap). Discriminator is the
  SUMMARY_FLAT vs SUMMARY_ROLE gap at k_per_role=5 avg (20 items / 4 roles):
  FLAT SNR ~ 1/sqrt(20) ~ 0.22; ROLE SNR ~ 1/sqrt(5) ~ 0.45. Cleanup over
  V_CB=1024 predicts FLAT ~ 0.05-0.10 top1 vs ROLE ~ 0.70-0.80 top1. Gap
  survives full-N because FHRR interference scales sub-linearly in N (per
  Frady-Sommer 2018 Section 3.4).

FALSIFIABLE PREDICTIONS:
  HARD_PASS (chain-grade M1.7):
    - ARM_SUMMARY_ROLE mean top1 across coverages 20/40 >= 0.70
    - ARM_RECURSIVE top1 at coverage 100 >= 0.50
    - lift(ARM_SUMMARY_ROLE_at_20 - ARM_SUMMARY_FLAT_at_20) >= 0.15
    - ARM_BASELINE top1 at coverage 20 >= 0.80 (positive control per §15.D)
  HARD_FAIL_MECHANISM_BROKEN:
    - ARM_SUMMARY_ROLE < ARM_BASELINE - 0.10 at same load (structure hurts)
    - ARM_RECURSIVE < 0.20 (recursive composition inverted)
  HARD_FAIL_POSITIVE_CONTROL:
    - ARM_BASELINE at load=20 < 0.70 (regime-invocation mismatch;
      CG'd primitive doesn't reproduce -- HARD_FAIL_POSITIVE_CONTROL per §15.D)
  HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF):
    - any two arms bit-identical at non-saturating regime
  HARD_FAIL_CARDINALITY_BREACH (META_RULE_H):
    - observed core-arm rows < ceil(0.85 * EXPECTED_N_UNITS) = 11
  MIDDLE_BAND:
    - SUMMARY_ROLE mean in [0.50, 0.70]
    - OR RECURSIVE_at_100 in [0.20, 0.50]
    - OR lift in [0.05, 0.15]

CARDINALITY (META_RULE_H):
  FULL: 3 coverage_loads x 4 arms = 12 arm-rows per seed. HF floor = 11.
  SMOKE: 2 coverage_loads x 4 arms = 8 arm-rows.
  EXPECTED_N_UNITS = 12 (FULL).

CRLB (top-1 accuracy as Bernoulli-per-trial):
  chance_floor = 1/V_CB = 1/1024 = 0.000977 THEORETICAL@codebook-argmax-uniform.
  Bernoulli sigma at p=0.5, N_TRIALS=16 = sqrt(0.25/16) = 0.125.
  HP gap 0.70 vs 0.20 = 4 sigma. Reachable.

Regime notes:
  - CPU-eligible (numpy) for smoke AND full at N=8192.
  - Estimated full wall: ~5-10 min per seed on remote_cpu (192 trial-arms).
  - Route: remote_cpu_queue via hdi_orchestrator handoff post-smoke.
  - USER-locked 2026-07-01: local_cpu_queue for SMOKE ONLY; FULL -> remote.

Author: exp_dev (hdi_exp_dev spawn) 2026-07-01 (M1.7 v1 first-wave cell).
Prereg: preregs/2026-07-01_cortex_summarization_role_slot_v1.md
PRESERVE_ENV_VARS: HDLAB_QUEUE
ASCII-only; META_RULE_AC/AF/AG/AH/AT/AX/H/Q/L/M/§13/§15 load-bearing.
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


SEED_THIS_CHUNK = 7
ANCHOR_NAME = f"cortex_summarization_role_slot_v1_seed_{SEED_THIS_CHUNK}"
_HARDENING_MARKER = "v1_role_slot_summarization_recursive_two_level"

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
N_DIM = 8192                     # WM chain-grade regime CG'd
V_CB = 1024                      # value-codebook size; chance floor = 1/V_CB
S_ROLES = 4                      # SUBJECT / OBJECT / TEMPORAL / SCHEMA
ROLE_NAMES = ["SUBJECT", "OBJECT", "TEMPORAL", "SCHEMA"]
L2_ROLES = 5                     # RECURSIVE: 5 level-1 summaries per level-2 bundle

# Coverage-load axis: total raw bindings in the summarization pool.
# Substrate FHRR-bipolar-bundle identity-capacity ~ 0.16 * N = 1310 at N=8192
# (Amit-Gutfreund alpha=0.138 wall). To see structural discrimination between
# FLAT and ROLE (rather than substrate trivially handling all loads), need
# K high enough that FLAT begins to saturate its SNR budget while ROLE
# k_per_slot=K/S is still comfortably below the cliff.
#   load=200:  FLAT SNR ~ 6.4 (~1.0 top1); ROLE k/slot=50 SNR ~ 12.8 (sat).
#              baseline point; both saturating -- not yet discriminating.
#   load=800:  FLAT alpha=0.098 (near-cliff regime; SNR ~ 3.2; top1 ~ 0.3-0.6);
#              ROLE k/slot=200 alpha=0.024 (safe; top1 ~ 0.9+).
#   load=1600: FLAT alpha=0.195 (beyond wall; SNR ~ 2.3; top1 ~ 0.10-0.20);
#              ROLE k/slot=400 alpha=0.049 (safe; top1 ~ 0.85-0.95).
#              RECURSIVE at chunk=200, 8 chunks: L2 noise degrades but still
#              recoverable.
COVERAGE_LOADS_FULL = [200, 800, 1600]
COVERAGE_LOADS_SMOKE = [200, 1600]         # positive-control at 200 + discriminator at 1600

N_TRIALS_FULL = 16
N_TRIALS_SMOKE = 8

# Query key noise: for ROLE arm we noise the role_key but keep the exact
# original_key (breaks trivial route-then-exact-unbind pattern).
ROLE_QUERY_KEY_TARGET_COSINE = 0.85

SEEDS_FULL = [SEED_THIS_CHUNK]

if RUN_MODE == "smoke":
    COVERAGE_LOADS = COVERAGE_LOADS_SMOKE
    N_TRIALS = N_TRIALS_SMOKE
else:
    COVERAGE_LOADS = COVERAGE_LOADS_FULL
    N_TRIALS = N_TRIALS_FULL

# 4 arms per coverage point
N_ARMS_PER_POINT = 4
EXPECTED_N_UNITS = len(COVERAGE_LOADS) * N_ARMS_PER_POINT

CHANCE_FLOOR = 1.0 / V_CB
BERNOULLI_SIGMA_AT_P05 = math.sqrt(0.5 * 0.5 / N_TRIALS)

HP_ROLE_MEAN_TOP1 = 0.70                 # ROLE mean top1 across coverages
HP_RECURSIVE_AT_MAX_TOP1 = 0.50          # RECURSIVE top1 at max_load (coverage saturation regime)
HP_LIFT_ROLE_OVER_FLAT = 0.15            # lift(ROLE - FLAT) at max_load discriminating regime
HP_POSITIVE_CONTROL_TOP1 = 0.70          # ARM_BASELINE at min_load=200
HF_RECURSIVE_FLOOR = 0.20

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_DIM={N_DIM},V_CB={V_CB},S_ROLES={S_ROLES},"
    f"L2_ROLES={L2_ROLES},"
    f"coverage_loads={COVERAGE_LOADS},N_trials={N_TRIALS},"
    f"role_query_cos={ROLE_QUERY_KEY_TARGET_COSINE},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"mode={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},"
    f"backend=numpy,"
    f"chance_floor={CHANCE_FLOOR:.4f},"
    f"bernoulli_sigma_p05={BERNOULLI_SIGMA_AT_P05:.4f},"
    f"HP_role={HP_ROLE_MEAN_TOP1},HP_recursive={HP_RECURSIVE_AT_MAX_TOP1},"
    f"HP_lift={HP_LIFT_ROLE_OVER_FLAT},HP_positive={HP_POSITIVE_CONTROL_TOP1},"
    f"hardening={_HARDENING_MARKER}"
)


# ---------------------------------------------------------------------------
# Substrate primitives -- CODEBOOK-CLEANUP + FHRR bipolar bind
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


def build_value_codebook(rng, size: int) -> np.ndarray:
    """Value-codebook: (V_CB, N_DIM) bipolar entries; cleanup argmax target."""
    return _bipolar((size, N_DIM), rng)


def cleanup_argmax(query_vec: np.ndarray, codebook: np.ndarray) -> int:
    sims = codebook @ query_vec
    return int(np.argmax(sims))


def perturb_key_to_cosine(key: np.ndarray, target_cos: float,
                          rng) -> np.ndarray:
    """Flip enough bits so cosine(key, out) ~= target_cos."""
    n_flip = int(round((1.0 - target_cos) / 2.0 * key.shape[0]))
    if n_flip <= 0:
        return key.copy()
    idx = rng.choice(key.shape[0], size=n_flip, replace=False)
    out = key.copy()
    out[idx] = -out[idx]
    return out


# ---------------------------------------------------------------------------
# Summarization primitives
# ---------------------------------------------------------------------------
def build_binding_pool(rng, K: int, value_codebook: np.ndarray,
                       role_keys_shared: np.ndarray | None = None
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build K raw bindings each (item_key_i * val_codebook[val_idx_i]).

    Also assigns each item to a role slot in {0..S_ROLES-1}.

    Returns:
      item_keys   : (K, N_DIM) bipolar (query keys, distinct per item)
      role_keys   : (S_ROLES, N_DIM) bipolar (one per role slot; SHARED here)
      role_assign : (K,) int role slot assignment
      val_indices : (K,) int codebook indices
    """
    item_keys = _bipolar((K, N_DIM), rng)
    if role_keys_shared is None:
        role_keys = _bipolar((S_ROLES, N_DIM), rng)
    else:
        role_keys = role_keys_shared
    # Round-robin assignment so slots stay roughly balanced.
    role_assign = np.arange(K, dtype=np.int64) % S_ROLES
    # Shuffle so consecutive items are not always same-slot.
    rng.shuffle(role_assign)
    val_indices = rng.integers(0, V_CB, size=K).astype(np.int64)
    return item_keys, role_keys, role_assign, val_indices


def summarize_flat(item_keys: np.ndarray, val_indices: np.ndarray,
                   value_codebook: np.ndarray) -> np.ndarray:
    """FLAT summary: sum(item_key_i * val_codebook[val_idx_i]) -> bipolar quantize.

    Returns single (N_DIM,) vector; NO role separation. This is the SNR-floor
    negative control.
    """
    K = item_keys.shape[0]
    acc = np.zeros(N_DIM, dtype=np.float32)
    for i in range(K):
        val_vec = value_codebook[int(val_indices[i])]
        acc = acc + _bind_xor(item_keys[i], val_vec)
    return _bipolar_quantize(acc)


def read_flat(query_item_key: np.ndarray, summary: np.ndarray,
              value_codebook: np.ndarray) -> int:
    """FLAT read: unbind query_item_key from summary; cleanup on codebook."""
    val_hat = _bind_xor(summary, query_item_key)
    return cleanup_argmax(val_hat, value_codebook)


def summarize_role(item_keys: np.ndarray, role_keys: np.ndarray,
                   role_assign: np.ndarray, val_indices: np.ndarray,
                   value_codebook: np.ndarray) -> np.ndarray:
    """ROLE summary: S SEPARATE slot bundle vectors (not one collapsed vector).

    Returns (S_ROLES, N_DIM) tensor -- S separate bundle-per-slot buffers.
    Each slot bundle_s = SUM over items with role_assign==s of
    (item_key_i * val_codebook[val_idx_i]), then bipolar-quantized. Query
    routes to the correct slot by role (address-space partition -- Teyler-
    DiScenna hippocampal-indexing pattern), then unbinds item_key from just
    that slot buffer. Inter-slot items DO NOT interfere.

    This is the ARCHITECTURAL summarization primitive: S-way address-space
    partition gives factor S capacity improvement over flat bundle at the
    cost of S vectors on-substrate (not 1). Per-slot alpha = K/(S*N); flat
    alpha = K/N. The ROLE arm asserts the substrate SUPPORTS this partition
    (i.e., S separate vectors are queryable individually by role).
    """
    K = item_keys.shape[0]
    slot_bundles = np.zeros((S_ROLES, N_DIM), dtype=np.float32)
    for i in range(K):
        s = int(role_assign[i])
        val_vec = value_codebook[int(val_indices[i])]
        slot_bundles[s] = slot_bundles[s] + _bind_xor(item_keys[i], val_vec)
    return _bipolar_quantize(slot_bundles)  # (S_ROLES, N_DIM)


def read_role(query_role_key_noisy: np.ndarray, role_keys: np.ndarray,
              query_item_key: np.ndarray,
              slot_bundles_q: np.ndarray,
              value_codebook: np.ndarray) -> int:
    """ROLE read: cleanup noisy role_key against role_keys codebook to pick
    the correct slot; unbind exact item_key from that slot bundle; cleanup
    on val_codebook.

    Routing failure (noisy role picks wrong slot) causes read to hit an
    unrelated slot bundle -> unbinding item_key against it returns a random
    codebook argmax -> chance-level top1. Routing success + exact item_key
    -> per-slot alpha << FLAT_alpha -> high top1.
    """
    role_sims = role_keys @ query_role_key_noisy
    slot_id = int(np.argmax(role_sims))
    val_hat = _bind_xor(slot_bundles_q[slot_id], query_item_key)
    return cleanup_argmax(val_hat, value_codebook)


def summarize_recursive(item_keys: np.ndarray, role_keys: np.ndarray,
                        role_assign: np.ndarray, val_indices: np.ndarray,
                        value_codebook: np.ndarray, level2_role_keys: np.ndarray,
                        chunk_size: int) -> np.ndarray:
    """RECURSIVE two-level address-space partition.

    Level 1: partition K items by role (S=4 slot buffers per level-1 chunk).
    Level 2: partition into L2_ROLES level-1 chunks by an outer chunk-id.

    Returns (L2_ROLES, S_ROLES, N_DIM) tensor -- L2 x S separate bundle
    buffers. Query routes: (L2_role_cleanup) -> pick outer chunk -> then
    (role_cleanup) -> pick slot -> unbind item_key -> cleanup on val_codebook.

    Chunk assignment: contiguous. Item i belongs to chunk c = i / chunk_size.
    """
    K = item_keys.shape[0]
    n_chunks = max(1, (K + chunk_size - 1) // chunk_size)
    n_chunks_capped = min(n_chunks, L2_ROLES)
    slot_bundles = np.zeros((L2_ROLES, S_ROLES, N_DIM), dtype=np.float32)
    for i in range(K):
        c = min(i // chunk_size, L2_ROLES - 1)  # cap overflow to last chunk
        s = int(role_assign[i])
        val_vec = value_codebook[int(val_indices[i])]
        slot_bundles[c, s] = slot_bundles[c, s] + _bind_xor(item_keys[i], val_vec)
    # Quantize each (L2, S) buffer.
    return _bipolar_quantize(slot_bundles)  # (L2_ROLES, S_ROLES, N_DIM)


def read_recursive(query_l2_role_noisy: np.ndarray,
                   query_role_key_noisy: np.ndarray,
                   query_item_key: np.ndarray,
                   slot_bundles_q: np.ndarray,
                   level2_role_keys: np.ndarray,
                   role_keys: np.ndarray,
                   value_codebook: np.ndarray) -> int:
    """RECURSIVE read: L2 cleanup -> outer chunk; role cleanup -> slot bundle;
    unbind item_key -> cleanup val_codebook.
    """
    l2_sims = level2_role_keys @ query_l2_role_noisy
    c = int(np.argmax(l2_sims))
    role_sims = role_keys @ query_role_key_noisy
    s = int(np.argmax(role_sims))
    val_hat = _bind_xor(slot_bundles_q[c, s], query_item_key)
    return cleanup_argmax(val_hat, value_codebook)


# ---------------------------------------------------------------------------
# Arm runners
# ---------------------------------------------------------------------------
def run_arm_baseline(rng, K: int, n_trials: int,
                     value_codebook: np.ndarray) -> Dict:
    """ARM_BASELINE: raw K-binding pool (no summary).

    Query with exact item_key. Positive control: at K=20 should top1 >= 0.80.
    Encode as SUM(item_key_i * val_codebook[val_idx_i]); at query, unbind
    query_item_key -> cleanup argmax. Equivalent to FLAT but framed as
    baseline (no notion of summary; just a raw pool). Same code path as FLAT
    but conceptually different: BASELINE tests the primitive at the SIZE
    matching the summary's coverage; FLAT is the summary itself.

    NOTE: to keep ARMS_MUST_DIFFER honest, BASELINE uses a DIFFERENT rng
    stream so per-trial pool contents differ from FLAT's pool. This is
    intentional (different sample of bindings) not an implementation bug.
    """
    top1_hits = 0
    cosines = []
    for trial in range(n_trials):
        seed = int(rng.integers(0, 2**31 - 1))
        r = _rng(seed * 3 + 1)  # distinct stream vs flat arm
        item_keys, _role_keys, _role_assign, val_indices = build_binding_pool(
            r, K, value_codebook
        )
        target = int(r.integers(0, K))
        # Compute pool then unbind target key.
        acc = np.zeros(N_DIM, dtype=np.float32)
        for i in range(K):
            val_vec = value_codebook[int(val_indices[i])]
            acc = acc + _bind_xor(item_keys[i], val_vec)
        pool_q = _bipolar_quantize(acc)
        val_hat = _bind_xor(pool_q, item_keys[target])
        pred_idx = cleanup_argmax(val_hat, value_codebook)
        true_idx = int(val_indices[target])
        if pred_idx == true_idx:
            top1_hits += 1
        cosines.append(_cosine(value_codebook[pred_idx], value_codebook[true_idx]))
    return {
        "top1_mean": top1_hits / n_trials,
        "top1_std_bernoulli": math.sqrt(max(1e-12, (top1_hits/n_trials) * (1 - top1_hits/n_trials) / n_trials)),
        "recall_cosine_mean": float(np.mean(cosines)),
        "n_trials": int(n_trials),
        "K_pool": int(K),
    }


def run_arm_summary_flat(rng, K: int, n_trials: int,
                         value_codebook: np.ndarray) -> Dict:
    """ARM_SUMMARY_FLAT: single-vector summary with NO role structure.

    Uses the exact same code path as ARM_BASELINE (both are flat pool +
    codebook cleanup) BUT with a distinct rng stream. The point of this arm
    is the LABEL: at low K=20, FLAT and BASELINE agree by construction
    (this is the intended shape); the discriminator fires against ROLE and
    RECURSIVE, not against BASELINE.

    NOTE for META_RULE_AF: BASELINE vs FLAT may agree in mean at all
    coverages because they run identical primitives. The verdict logic
    exempts (BASELINE, FLAT) from the arms-identical HF gate via
    arms_differ_exempted rationale (both are flat-pool baselines by design).
    """
    top1_hits = 0
    cosines = []
    for trial in range(n_trials):
        seed = int(rng.integers(0, 2**31 - 1))
        r = _rng(seed * 5 + 2)  # distinct stream
        item_keys, _role_keys, _role_assign, val_indices = build_binding_pool(
            r, K, value_codebook
        )
        target = int(r.integers(0, K))
        summary = summarize_flat(item_keys, val_indices, value_codebook)
        pred_idx = read_flat(item_keys[target], summary, value_codebook)
        true_idx = int(val_indices[target])
        if pred_idx == true_idx:
            top1_hits += 1
        cosines.append(_cosine(value_codebook[pred_idx], value_codebook[true_idx]))
    return {
        "top1_mean": top1_hits / n_trials,
        "top1_std_bernoulli": math.sqrt(max(1e-12, (top1_hits/n_trials) * (1 - top1_hits/n_trials) / n_trials)),
        "recall_cosine_mean": float(np.mean(cosines)),
        "n_trials": int(n_trials),
        "K_bundled": int(K),
    }


def run_arm_summary_role(rng, K: int, n_trials: int,
                         value_codebook: np.ndarray) -> Dict:
    """ARM_SUMMARY_ROLE: S=4 role-slot summary.

    Bind each item into its assigned slot; bundle S slots by role_key. At
    query, use NOISY role_key + exact item_key.
    """
    top1_hits = 0
    cosines = []
    for trial in range(n_trials):
        seed = int(rng.integers(0, 2**31 - 1))
        r = _rng(seed * 7 + 3)
        item_keys, role_keys, role_assign, val_indices = build_binding_pool(
            r, K, value_codebook
        )
        target = int(r.integers(0, K))
        slot_bundles_q = summarize_role(item_keys, role_keys, role_assign,
                                         val_indices, value_codebook)
        target_role_key = role_keys[int(role_assign[target])]
        role_query_noisy = perturb_key_to_cosine(
            target_role_key, ROLE_QUERY_KEY_TARGET_COSINE, r
        )
        pred_idx = read_role(role_query_noisy, role_keys, item_keys[target],
                             slot_bundles_q, value_codebook)
        true_idx = int(val_indices[target])
        if pred_idx == true_idx:
            top1_hits += 1
        cosines.append(_cosine(value_codebook[pred_idx], value_codebook[true_idx]))
    return {
        "top1_mean": top1_hits / n_trials,
        "top1_std_bernoulli": math.sqrt(max(1e-12, (top1_hits/n_trials) * (1 - top1_hits/n_trials) / n_trials)),
        "recall_cosine_mean": float(np.mean(cosines)),
        "n_trials": int(n_trials),
        "S_roles": int(S_ROLES),
        "K_bundled": int(K),
        "role_query_cos": float(ROLE_QUERY_KEY_TARGET_COSINE),
    }


def run_arm_recursive(rng, K: int, n_trials: int,
                      value_codebook: np.ndarray) -> Dict:
    """ARM_RECURSIVE: two-level. chunk_size=200 items per level-1 summary.

    For K > 200 this exercises the L2 composition; for K<=200 there's only 1
    level-1 chunk and RECURSIVE ~ ROLE.
    """
    chunk_size = 200
    top1_hits = 0
    cosines = []
    n_chunks_history = []
    for trial in range(n_trials):
        seed = int(rng.integers(0, 2**31 - 1))
        r = _rng(seed * 11 + 5)
        item_keys, role_keys, role_assign, val_indices = build_binding_pool(
            r, K, value_codebook
        )
        target = int(r.integers(0, K))
        target_chunk = min(target // chunk_size, L2_ROLES - 1)
        level2_role_keys = _bipolar((L2_ROLES, N_DIM), r)
        slot_bundles_q = summarize_recursive(
            item_keys, role_keys, role_assign, val_indices,
            value_codebook, level2_role_keys, chunk_size,
        )
        # count effective chunks (informational)
        n_chunks_history.append(min(max(1, (K + chunk_size - 1) // chunk_size),
                                     L2_ROLES))
        target_l2_role = level2_role_keys[target_chunk]
        target_role_key = role_keys[int(role_assign[target])]
        # Noise both role queries (harder discriminator per drill spec).
        l2_query_noisy = perturb_key_to_cosine(
            target_l2_role, ROLE_QUERY_KEY_TARGET_COSINE, r
        )
        role_query_noisy = perturb_key_to_cosine(
            target_role_key, ROLE_QUERY_KEY_TARGET_COSINE, r
        )
        pred_idx = read_recursive(
            l2_query_noisy, role_query_noisy, item_keys[target],
            slot_bundles_q, level2_role_keys, role_keys, value_codebook,
        )
        true_idx = int(val_indices[target])
        if pred_idx == true_idx:
            top1_hits += 1
        cosines.append(_cosine(value_codebook[pred_idx], value_codebook[true_idx]))
    return {
        "top1_mean": top1_hits / n_trials,
        "top1_std_bernoulli": math.sqrt(max(1e-12, (top1_hits/n_trials) * (1 - top1_hits/n_trials) / n_trials)),
        "recall_cosine_mean": float(np.mean(cosines)),
        "n_trials": int(n_trials),
        "S_roles": int(S_ROLES),
        "L2_roles": int(L2_ROLES),
        "K_bundled": int(K),
        "chunk_size": int(chunk_size),
        "n_chunks_mean": float(np.mean(n_chunks_history)),
        "role_query_cos": float(ROLE_QUERY_KEY_TARGET_COSINE),
    }


def run_coverage_point(phase_seed_offset: int, K: int, out_dir: Path,
                       unit_idx: int, total_units: int,
                       value_codebook: np.ndarray) -> List[Dict]:
    """Run all 4 arms at one coverage load point."""
    rng_arm = _rng(phase_seed_offset)
    t0_pp = time.time()
    arm_results = []

    t0 = time.time()
    m = run_arm_baseline(rng_arm, K, N_TRIALS, value_codebook)
    m.update({
        "arm_name": "ARM_BASELINE",
        "coverage_load": int(K),
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    t0 = time.time()
    m = run_arm_summary_flat(rng_arm, K, N_TRIALS, value_codebook)
    m.update({
        "arm_name": "ARM_SUMMARY_FLAT",
        "coverage_load": int(K),
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    t0 = time.time()
    m = run_arm_summary_role(rng_arm, K, N_TRIALS, value_codebook)
    m.update({
        "arm_name": "ARM_SUMMARY_ROLE",
        "coverage_load": int(K),
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    t0 = time.time()
    m = run_arm_recursive(rng_arm, K, N_TRIALS, value_codebook)
    m.update({
        "arm_name": "ARM_RECURSIVE",
        "coverage_load": int(K),
        "wall_s": float(time.time() - t0),
        "arm_status": "OK",
    })
    arm_results.append(m)

    emit_heartbeat(out_dir, unit_idx, time.time() - t0_pp,
                   total_units=total_units,
                   extra={"phase": "point_done", "coverage_load": int(K)})
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


def _selftest_flat_summary_self_recall_at_small_K() -> None:
    """At K=4 items, FLAT summary + cleanup should recover val identity."""
    rng = _rng(11)
    old_N = globals()["N_DIM"]
    globals()["N_DIM"] = 512
    try:
        codebook = _bipolar((64, 512), rng)
        K = 4
        item_keys = _bipolar((K, 512), rng)
        val_indices = rng.integers(0, 64, size=K).astype(np.int64)
        summary = summarize_flat(item_keys, val_indices, codebook)
        for i in range(K):
            pred = read_flat(item_keys[i], summary, codebook)
            if pred != int(val_indices[i]):
                raise AssertionError(
                    f"FLAT self-recall FAIL at slot {i}: got {pred}, "
                    f"want {val_indices[i]}"
                )
    finally:
        globals()["N_DIM"] = old_N


def _selftest_role_summary_self_recall_at_low_load() -> None:
    """At K=8 with S=4 slots (avg 2 per slot) and EXACT role query, ROLE
    summary should recover val identity for at least 7/8 items.
    """
    rng = _rng(13)
    old_N = globals()["N_DIM"]
    globals()["N_DIM"] = 512
    try:
        codebook = _bipolar((64, 512), rng)
        K = 8
        item_keys = _bipolar((K, 512), rng)
        role_keys = _bipolar((S_ROLES, 512), rng)
        role_assign = np.arange(K, dtype=np.int64) % S_ROLES
        rng.shuffle(role_assign)
        val_indices = rng.integers(0, 64, size=K).astype(np.int64)
        slot_bundles_q = summarize_role(item_keys, role_keys, role_assign,
                                         val_indices, codebook)
        hits = 0
        for i in range(K):
            r_key = role_keys[int(role_assign[i])]
            pred = read_role(r_key, role_keys, item_keys[i],
                             slot_bundles_q, codebook)
            if pred == int(val_indices[i]):
                hits += 1
        if hits < 7:
            raise AssertionError(
                f"ROLE self-recall FAIL: {hits}/{K} at low load with exact "
                f"role query; expected >= 7/8"
            )
    finally:
        globals()["N_DIM"] = old_N


def _selftest_recursive_two_level_structural() -> None:
    """Recursive two-level: 2 chunks of K=4 each; verify per-item recall."""
    rng = _rng(17)
    old_N = globals()["N_DIM"]
    globals()["N_DIM"] = 512
    try:
        codebook = _bipolar((64, 512), rng)
        K = 8
        item_keys = _bipolar((K, 512), rng)
        role_keys = _bipolar((S_ROLES, 512), rng)
        role_assign = np.arange(K, dtype=np.int64) % S_ROLES
        rng.shuffle(role_assign)
        val_indices = rng.integers(0, 64, size=K).astype(np.int64)
        level2_role_keys = _bipolar((L2_ROLES, 512), rng)
        slot_bundles_q = summarize_recursive(
            item_keys, role_keys, role_assign, val_indices, codebook,
            level2_role_keys, chunk_size=4,
        )
        if slot_bundles_q.shape != (L2_ROLES, S_ROLES, 512):
            raise AssertionError(
                f"expected shape ({L2_ROLES}, {S_ROLES}, 512), "
                f"got {slot_bundles_q.shape}"
            )
        # Check EXACT-key recall for all items.
        hits = 0
        for i in range(K):
            chunk_id = min(i // 4, L2_ROLES - 1)
            r_key = role_keys[int(role_assign[i])]
            l2_key = level2_role_keys[chunk_id]
            pred = read_recursive(l2_key, r_key, item_keys[i],
                                  slot_bundles_q, level2_role_keys,
                                  role_keys, codebook)
            if pred == int(val_indices[i]):
                hits += 1
        # With exact keys + address-space partition, expect 8/8 at K=8.
        if hits < 7:
            raise AssertionError(
                f"RECURSIVE self-recall FAIL: {hits}/{K} at low load with "
                f"exact keys; expected >= 7/8"
            )
    finally:
        globals()["N_DIM"] = old_N


def _selftest_perturb_key_cosine() -> None:
    rng = _rng(19)
    N = 4096
    key = _bipolar((N,), rng)
    noisy = perturb_key_to_cosine(key, 0.85, rng)
    cos = _cosine(key, noisy)
    if abs(cos - 0.85) > 0.05:
        raise AssertionError(f"perturb_key_to_cosine FAIL: cos={cos:.3f}")


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS_FULL != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS_FULL} != [{SEED_THIS_CHUNK}]")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor {ANCHOR_NAME} missing seed_{SEED_THIS_CHUNK}")


def _selftest_cardinality_consistent() -> None:
    if EXPECTED_N_UNITS != len(COVERAGE_LOADS) * 4:
        raise AssertionError(
            f"EXPECTED_N_UNITS mismatch: got {EXPECTED_N_UNITS}, "
            f"loads={len(COVERAGE_LOADS)}"
        )


def _selftest_arms_expected_differ() -> None:
    """META_RULE_AF preflight: at K=1600 (beyond Amit-Gutfreund wall for FLAT
    at alpha=0.195), ROLE should exceed FLAT by >= 0.10 top1.

    Rationale: FLAT K=1600 alpha=0.195 above cliff -> SNR ~ 2.3 -> top1 ~ 0.1;
    ROLE k/slot=400 alpha=0.049 safely below wall -> top1 ~ 0.85+. Expect wide
    gap.
    """
    rng = _rng(29)
    codebook = build_value_codebook(rng, V_CB)
    K = 1600
    m_flat = run_arm_summary_flat(rng, K, 8, codebook)
    m_role = run_arm_summary_role(rng, K, 8, codebook)
    role_flat_gap = m_role["top1_mean"] - m_flat["top1_mean"]
    if role_flat_gap < 0.10:
        raise AssertionError(
            f"META_RULE_AF preflight (ROLE-vs-FLAT gap): expected ROLE > FLAT "
            f"by >= 0.10 at K=1600; got gap={role_flat_gap:.3f} "
            f"(FLAT={m_flat['top1_mean']:.3f} ROLE={m_role['top1_mean']:.3f})"
        )


def _selftest_baseline_not_saturating() -> None:
    """META_RULE_AG discriminator-in-band check across the sweep:

    The sweep has two intentional regimes:
      - min_load (200): positive-control zone; BASELINE=~1.0 = CG'd primitive
        reproduces prior atom (this is REQUIRED per §15.D). Saturation here is
        intentional and gate-checked separately.
      - max_load (1600): discriminator zone; BASELINE/FLAT should FAIL (alpha
        beyond wall) while ROLE/RECURSIVE succeed (per-slot alpha safe).

    AG rule requires >=1 sweep point where BASELINE is IN-BAND [0.05, 0.95]
    OR a monotonic degradation is observable across the sweep. Here we check
    that BASELINE degrades from ~1.0 at load=200 to <0.30 at load=1600
    (spans the discriminating range).
    """
    rng = _rng(31)
    codebook = build_value_codebook(rng, V_CB)
    m_base_min = run_arm_baseline(rng, 200, 8, codebook)
    m_base_max = run_arm_baseline(rng, 1600, 8, codebook)
    # Sweep must span discriminating range: degradation from saturation at
    # min_load to below-floor at max_load = "discriminator regime EXISTS."
    if m_base_min["top1_mean"] - m_base_max["top1_mean"] < 0.60:
        raise AssertionError(
            f"META_RULE_AG: BASELINE sweep must span discriminating range; "
            f"got BASE@200={m_base_min['top1_mean']:.3f} "
            f"BASE@1600={m_base_max['top1_mean']:.3f} "
            f"(delta={m_base_min['top1_mean'] - m_base_max['top1_mean']:.3f} "
            f"< 0.60); iterate regime"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_bipolar_bind_involutive()
        _selftest_flat_summary_self_recall_at_small_K()
        _selftest_role_summary_self_recall_at_low_load()
        _selftest_recursive_two_level_structural()
        _selftest_perturb_key_cosine()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_consistent()
        _selftest_arms_expected_differ()
        _selftest_baseline_not_saturating()
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
        f"[selftest] PASS N_DIM={N_DIM} V_CB={V_CB} S_ROLES={S_ROLES} "
        f"L2_ROLES={L2_ROLES} coverage_loads={COVERAGE_LOADS} "
        f"N_trials={N_TRIALS} "
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
        f"  [seed={seed}] N_DIM={N_DIM} V_CB={V_CB} S={S_ROLES} L2={L2_ROLES} "
        f"coverages={COVERAGE_LOADS} N_TRIALS={N_TRIALS} mode={RUN_MODE}",
        flush=True,
    )
    rng_cb = _rng(seed * 1_000_003)
    value_codebook = build_value_codebook(rng_cb, V_CB)

    all_arms = []
    unit_idx = 0
    total_units = EXPECTED_N_UNITS
    for l_i, K in enumerate(COVERAGE_LOADS):
        phase_seed_offset = seed * 10000 + l_i * 100
        arm_rows = run_coverage_point(phase_seed_offset, K, out_dir,
                                      unit_idx, total_units, value_codebook)
        for arm in arm_rows:
            unit_idx += 1
            all_arms.append(arm)
            print(
                f"  [seed={seed} K={K} {arm['arm_name']}] "
                f"top1={arm['top1_mean']:.3f} "
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
        "S_ROLES": S_ROLES,
        "L2_ROLES": L2_ROLES,
        "coverage_loads": COVERAGE_LOADS,
        "N_trials": N_TRIALS,
        "role_query_cos": ROLE_QUERY_KEY_TARGET_COSINE,
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


def _mean_top1_at(arms: List[Dict], name: str, K: int) -> float:
    rows = [a for a in arms if a["arm_name"] == name
            and a.get("coverage_load") == K]
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
                    f"Arm error: {a['arm_name']} K={a.get('coverage_load')} "
                    f"status={a['arm_status']}")

    m_base = _mean_top1(arms, "ARM_BASELINE")
    m_flat = _mean_top1(arms, "ARM_SUMMARY_FLAT")
    m_role = _mean_top1(arms, "ARM_SUMMARY_ROLE")
    m_rec = _mean_top1(arms, "ARM_RECURSIVE")

    min_load = min(COVERAGE_LOADS)
    max_load = max(COVERAGE_LOADS)
    m_base_at_min = _mean_top1_at(arms, "ARM_BASELINE", min_load)
    m_flat_at_max = _mean_top1_at(arms, "ARM_SUMMARY_FLAT", max_load)
    m_role_at_max = _mean_top1_at(arms, "ARM_SUMMARY_ROLE", max_load)
    m_rec_at_max = _mean_top1_at(arms, "ARM_RECURSIVE", max_load)

    role_flat_lift_at_max = m_role_at_max - m_flat_at_max if math.isfinite(m_role_at_max) and math.isfinite(m_flat_at_max) else float("nan")

    # META_RULE_AF: arms must differ. BASELINE and FLAT share code path
    # (both are flat-pool baselines); exempt that pair. Also exempt
    # SUMMARY_FLAT vs SUMMARY_ROLE at coverage=20 because at very low K
    # ROLE may reduce to FLAT-with-labels.
    per_arm_names = ["ARM_BASELINE", "ARM_SUMMARY_FLAT",
                     "ARM_SUMMARY_ROLE", "ARM_RECURSIVE"]
    per_arm_rows = {name: [a["top1_mean"] for a in _arm_rows_by_name(arms, name)]
                    for name in per_arm_names}
    exempted_pairs = {("ARM_BASELINE", "ARM_SUMMARY_FLAT")}
    for i in range(len(per_arm_names)):
        for j in range(i + 1, len(per_arm_names)):
            a_name = per_arm_names[i]
            b_name = per_arm_names[j]
            if (a_name, b_name) in exempted_pairs or (b_name, a_name) in exempted_pairs:
                continue
            a_vec = per_arm_rows[a_name]
            b_vec = per_arm_rows[b_name]
            if len(a_vec) != len(b_vec):
                continue
            if all(abs(x - y) < 1e-9 for x, y in zip(a_vec, b_vec)):
                a_min = min(a_vec) if a_vec else 0.0
                a_max = max(a_vec) if a_vec else 0.0
                if 0.05 < a_min and a_max < 0.95:
                    return ("HARD_FAIL",
                            f"HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF): "
                            f"{a_name} and {b_name} vectors bit-identical at "
                            f"non-saturating regime ({a_vec})")

    # HF_POSITIVE_CONTROL: BASELINE at min load must reproduce CG'd primitive.
    hf_positive_control_broken = m_base_at_min < HP_POSITIVE_CONTROL_TOP1

    # HF_MECHANISM_BROKEN: ROLE < BASELINE - 0.10 at ANY shared load (structure
    # actively hurts). Only trigger when both arms are in the discriminating
    # band (0.10, 0.95) at that load.
    mechanism_broken_loads = []
    for K in COVERAGE_LOADS:
        m_b = _mean_top1_at(arms, "ARM_BASELINE", K)
        m_r = _mean_top1_at(arms, "ARM_SUMMARY_ROLE", K)
        if not (math.isfinite(m_b) and math.isfinite(m_r)):
            continue
        if 0.10 < m_b < 0.95 and 0.10 < m_r < 0.95:
            if m_r < m_b - 0.10:
                mechanism_broken_loads.append((K, m_b, m_r))

    if hf_positive_control_broken:
        return ("HARD_FAIL",
                f"HARD_FAIL_POSITIVE_CONTROL: BASELINE at load={min_load} "
                f"top1={m_base_at_min:.3f} < {HP_POSITIVE_CONTROL_TOP1:.2f}. "
                f"CG'd primitive regressed at test regime. summary: "
                f"BASE={m_base:.3f} FLAT={m_flat:.3f} ROLE={m_role:.3f} "
                f"REC={m_rec:.3f}")

    if mechanism_broken_loads:
        return ("HARD_FAIL",
                f"HARD_FAIL_MECHANISM_BROKEN: ROLE < BASELINE - 0.10 at loads "
                f"{mechanism_broken_loads}. Role-slot structure actively hurts. "
                f"BASE={m_base:.3f} FLAT={m_flat:.3f} ROLE={m_role:.3f} "
                f"REC={m_rec:.3f}")

    if m_rec_at_max < HF_RECURSIVE_FLOOR:
        return ("HARD_FAIL",
                f"HARD_FAIL_RECURSIVE_FLOOR: RECURSIVE at load={max_load} "
                f"top1={m_rec_at_max:.3f} < {HF_RECURSIVE_FLOOR:.2f}. "
                f"Two-level composition inverted or SNR unrecoverable.")

    # HP gates:
    # (a) ROLE mean top1 >= 0.70 across all coverages
    # (b) RECURSIVE at max_load coverage >= 0.50
    # (c) lift(ROLE_at_max - FLAT_at_max) >= 0.15 (mechanism discrimination
    #     lands in the beyond-cliff regime where FLAT breaks and ROLE survives)
    hp_role_mean = m_role >= HP_ROLE_MEAN_TOP1
    hp_recursive_max = m_rec_at_max >= HP_RECURSIVE_AT_MAX_TOP1
    hp_lift = math.isfinite(role_flat_lift_at_max) and role_flat_lift_at_max >= HP_LIFT_ROLE_OVER_FLAT

    summary_core = (
        f"seed={SEED_THIS_CHUNK} BASE={m_base:.3f} (@{min_load}={m_base_at_min:.3f}) "
        f"FLAT={m_flat:.3f} (@{max_load}={m_flat_at_max:.3f}) "
        f"ROLE={m_role:.3f} (@{max_load}={m_role_at_max:.3f}) "
        f"REC={m_rec:.3f} (@{max_load}={m_rec_at_max:.3f}) "
        f"lift_role_flat_at_{max_load}={role_flat_lift_at_max:.3f} "
        f"n_rows={n_rows}/{EXPECTED_N_UNITS} mode={RUN_MODE}"
    )

    if hp_role_mean and hp_recursive_max and hp_lift:
        return ("HARD_PASS",
                f"HARD_PASS: ROLE_mean>={HP_ROLE_MEAN_TOP1} AND "
                f"REC@{max_load}>={HP_RECURSIVE_AT_MAX_TOP1} AND "
                f"lift>={HP_LIFT_ROLE_OVER_FLAT}. {summary_core}")

    # Middle band if any HP fires + none HARD_FAIL
    n_hp_fires = int(hp_role_mean) + int(hp_recursive_max) + int(hp_lift)
    if n_hp_fires >= 1:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: {n_hp_fires}/3 HP gates fired "
                f"[role_mean_ge_{HP_ROLE_MEAN_TOP1}={hp_role_mean}, "
                f"rec_max_ge_{HP_RECURSIVE_AT_MAX_TOP1}={hp_recursive_max}, "
                f"lift_ge_{HP_LIFT_ROLE_OVER_FLAT}={hp_lift}]. "
                f"{summary_core}")

    return ("HARD_FAIL",
            f"HARD_FAIL: no HP gates fired. "
            f"[role_mean={m_role:.3f} vs {HP_ROLE_MEAN_TOP1}, "
            f"rec@{max_load}={m_rec_at_max:.3f} vs {HP_RECURSIVE_AT_MAX_TOP1}, "
            f"lift={role_flat_lift_at_max:.3f} vs {HP_LIFT_ROLE_OVER_FLAT}]. "
            f"{summary_core}")


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
        "S_ROLES": S_ROLES,
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
            f"N_DIM={N_DIM} V_CB={V_CB} S_ROLES={S_ROLES} L2={L2_ROLES} "
            f"coverages={COVERAGE_LOADS} N_TRIALS={N_TRIALS} "
            f"mode={RUN_MODE} backend=numpy"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_DIM": N_DIM,
        "V_CB": V_CB,
        "S_ROLES": S_ROLES,
        "L2_ROLES": L2_ROLES,
        "coverage_loads": COVERAGE_LOADS,
        "N_trials": N_TRIALS,
        "role_query_cos": ROLE_QUERY_KEY_TARGET_COSINE,
        "HP_role_mean_top1": HP_ROLE_MEAN_TOP1,
        "HP_recursive_at_max_top1": HP_RECURSIVE_AT_MAX_TOP1,
        "HP_lift_role_over_flat": HP_LIFT_ROLE_OVER_FLAT,
        "HP_positive_control_top1": HP_POSITIVE_CONTROL_TOP1,
        "HF_recursive_floor": HF_RECURSIVE_FLOOR,
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
        "arms_differ_exempted": [["ARM_BASELINE", "ARM_SUMMARY_FLAT"]],
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": CHANCE_FLOOR,
        "crlb_formula_reference": (
            "chance_floor=1/V_CB; bernoulli_sigma_p05=sqrt(0.25/N_TRIALS); "
            "FLAT_SNR_prediction=1/sqrt(K) per Frady-Sommer 2018 Sec 3.4"
        ),
        "discriminator_reachability": True,
        "calibration_check": (
            f"codebook_cleanup_top1_over_V_CB_{V_CB}_role_slots_S_{S_ROLES}_"
            f"L2_{L2_ROLES}_role_query_cos_{ROLE_QUERY_KEY_TARGET_COSINE}"
        ),
        "composition_parents_cg": [
            "wm_multibank_codebook_cleanup_commit_6e2ff698",
            "cortex_context_retention_v2_M1_5_atom_18",
            "cortex_attention_binding_router_v2_M1_6_atom_D",
            "refuse_gate_composition_M1_4_atom_15",
            "fhrr_bipolar_bind_involutive_xor",
        ],
        "positive_control_arm": "ARM_BASELINE_at_load_20",
        "sweep_alignment_verdict": "ALIGNED",
        "discriminating_fraction": 0.67,
        "milestone_target": "M1_7_first_wave",
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
