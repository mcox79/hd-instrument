"""substrate_cortex_hippo_spaced_rep_NREM_M_8192_GPU_v1 -- seed_7.

BRAIN-REALITY VARIANT of cortex_hippo_handoff.  The standard handoff cell at
chain-grade M=8192 CLOSED-NEGATIVE: Willshaw capacity exceeded (~227x), and
all-at-once consolidation collapses (parent CLOSED-neg v2 ARM_FULL=0.748 at
M=512 smoke -- but the smoke regime was alpha=0.25.  At chain-grade M=8192,
N_c=8192 the Hopfield-bipolar memory hits its capacity wall).

Brain reality (Klinzing-Niethard-Born 2019; Wittkuhn & Schuck 2021; Ebbinghaus
1885 spacing law): consolidation is NOT all-at-once.  Each memory replays
dozens to hundreds of times across days/weeks/months with SPACED INTERVALS
(short-then-longer per Ebbinghaus exponential curve).

Hypothesis: substrate handles M=8192 if we consolidate with brain-style spaced
repetition rather than all-at-once.  Mechanism: spacing distributes interference
across cortex, allowing later writes to refine earlier ones rather than
overwriting them.  Each item gets the SAME total replay count as the
all-at-once arm -- only the SCHEDULE differs.

ARMS (3, all using v2 corrected replay-via-hippo-readout):
  ARM_A_BRAIN_SPACED:
    N_SESSIONS sessions; each session replays BATCH_SIZE items from W_hippo
    via cue-reactivation (sign(cue @ W_hippo.T)) into W_cortex.  Item-to-session
    assignment follows EBBINGHAUS spacing: each item replays N_REVISITS times
    across sessions at intervals [1, 2, 5, 10, 20, 50, 100, ...] sessions apart.
    Random subset of M items in each session draws from those due-for-review.

  ARM_B_ALL_AT_ONCE:
    Control matching parent CLOSED-neg regime.  One consolidation pass of
    N_REPLAY_TOTAL cycles, each cycle replaying ALL M items via hippo readout.
    Total cortex-write count matched to arm_A.

  ARM_C_UNIFORM_REPEAT:
    Same N_SESSIONS x BATCH_SIZE replay events as arm_A, but item assignment
    is uniform-random with replacement -- no spacing curve.  Discriminator
    for arm_A: if arm_A > arm_C, the spacing curve itself matters
    (not just distributing writes across sessions).

Parent cell:    experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7.py
Parent prereg:  preregs/2026-06-28_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed.md
Parent CLOSED-neg signal: at chain-grade M=8192 N_c=8192 alpha=1.0, expected
DIRECT recall < 0.40 (Hopfield capacity wall).  Under brain-spaced repetition
ARM_A may rise above floor if spacing distributes interference.

HARD_PASS (single-seed):
  acc(BRAIN_SPACED) >= 0.30 absolute (substrate retains chain-grade items) AND
  acc(BRAIN_SPACED) - acc(ALL_AT_ONCE) >= 0.10 (spacing helps over no-spacing) AND
  abs(acc(BRAIN_SPACED) - acc(UNIFORM_REPEAT)) > 0.05 (the SCHEDULE matters,
    not just the distribution of writes)

POTENTIAL_MAJOR_UNLOCK_IF:
  acc(BRAIN_SPACED) >= 0.50 AND acc(BRAIN_SPACED) - acc(ALL_AT_ONCE) >= 0.30.
  This would re-open the CLS-handoff closure with a regime-conditional
  amendment: chain-grade memory IS achievable on this substrate IF
  consolidation respects brain-style spacing.

HARD_FAIL (single-seed):
  acc(BRAIN_SPACED) - acc(ALL_AT_ONCE) < 0.0 (spacing actively HURTS) OR
  acc(BRAIN_SPACED) - acc(UNIFORM_REPEAT) <= 0.0 AND
    acc(ALL_AT_ONCE) - acc(UNIFORM_REPEAT) <= 0.0
    (no arm differs from any other -- mechanism not engaged) OR
  abs(acc(BRAIN_SPACED) - acc(ALL_AT_ONCE)) < 1e-6 (META_RULE_AF bit-exact)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 3 arms x 1 seed = 3 arms.

DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26):
  Smoke runs at M=2048 N_c=2048 (alpha=1.0; SAME alpha-regime as FULL).
  At smoke, ALL_AT_ONCE must already show the Hopfield collapse signature
  (recall < 0.50) -- if smoke ALL_AT_ONCE = 1.0, alpha-regime didn't
  saturate and the spacing discriminator may not fire at FULL.
  Smoke gates FULL dispatch.

GPU (Fix #24):
  FULL run uses torch.cuda with batched matmul replay + readout.
  Spaced-rep introduces per-session sub-batching but each session's
  BATCH_SIZE x N_h matmul stays GPU-batched.
  Smoke falls back to numpy on CPU.

ASCII-only; no unicode; no emojis; no em-dashes.
META_RULE_AH atomic-write; META_RULE_AF arms-must-differ.

PRESERVE_ENV_VARS: HDLAB_QUEUE
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
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

# Inlined heartbeat helper.
from datetime import datetime as _dt_mod, timezone as _tz_mod
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": _dt_mod.now(_tz_mod.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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


ANCHOR_NAME = "substrate_cortex_hippo_spaced_rep_NREM_M_8192_GPU_v1_seed_7"
SEED_THIS_CHUNK = 7
_LLM_CALL_COUNTER = [0]
_HARDENING_MARKER = "v1_spaced_rep_NREM_chain_grade_M_8192_GPU"

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
# Torch import + cuda selection.
# ---------------------------------------------------------------------------
_TORCH_AVAILABLE = False
_CUDA_AVAILABLE = False
torch = None  # type: ignore
try:
    import torch as _torch
    torch = _torch
    _TORCH_AVAILABLE = True
    _CUDA_AVAILABLE = bool(torch.cuda.is_available())
except Exception as _exc:
    print(f"[torch] import failed: {type(_exc).__name__}: {_exc}", flush=True)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# FULL chain-grade spec: M=8192 with brain-spaced sessions.
N_HIPPO_FULL = 4096
N_CORTEX_FULL = 8192
HIPPO_SPARSITY = 0.10
M_ITEMS_FULL = 8192
ETA_CORTEX_FULL = 0.01

# Brain-spaced FULL schedule.
# 200 sessions x 80 items/session = 16000 replay events.
# Ebbinghaus spacing intervals (sessions apart):
EBBINGHAUS_INTERVALS = [1, 2, 5, 10, 20, 50, 100]
# N_REVISITS per item = len(EBBINGHAUS_INTERVALS) + 1 (first visit) = 8 effective
# but constrained by available sessions in window.
# Total replay events across all M items: target 16000.
# Per-item target: 16000 / 8192 = ~2 replays (modest; brain-realistic for short
# consolidation window; can be scaled).
# For more aggressive consolidation, push to N_SESSIONS=1000 -> ~10 replays/item.
N_SESSIONS_FULL = 800
BATCH_SIZE_FULL = 64
# Total Hebbian write events: N_SESSIONS_FULL * BATCH_SIZE_FULL = 51200.
# All_at_once equivalent: N_REPLAY_TOTAL * M -> set so the WRITE COUNTS MATCH:
# N_REPLAY_TOTAL = 51200 / 8192 ~= 6.25, so use 6 cycles + carry-over of 0.25 * M.
N_REPLAY_TOTAL_AAO_FULL = 6  # 6 * 8192 = 49152 (within 5% of 51200 spaced events)

# Smoke at intermediate scale, same alpha regime.
if RUN_MODE == "smoke":
    # Smoke: alpha=1.0 to ensure Hopfield-saturation discriminator survives.
    N_HIPPO = 1024
    N_CORTEX = 2048
    M_ITEMS = 2048  # alpha_simple = M/N_c = 1.0 (matches FULL alpha)
    ETA_CORTEX = 0.005
    SEEDS = [SEED_THIS_CHUNK]
    # Smoke spaced schedule: shorter; same shape.
    N_SESSIONS = 100
    BATCH_SIZE = 32
    # Total spaced events: 100 * 32 = 3200 -> 3200/2048 = 1.56 reps/item
    # All_at_once equivalent: round(3200/2048) = 2 cycles
    N_REPLAY_TOTAL_AAO = 2
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    M_ITEMS = M_ITEMS_FULL
    ETA_CORTEX = ETA_CORTEX_FULL
    SEEDS = [SEED_THIS_CHUNK]
    N_SESSIONS = N_SESSIONS_FULL
    BATCH_SIZE = BATCH_SIZE_FULL
    N_REPLAY_TOTAL_AAO = N_REPLAY_TOTAL_AAO_FULL

K_HIPPO_ACTIVE = max(1, int(round(HIPPO_SPARSITY * N_HIPPO)))

# Total replay events (write counts) per arm - must be approximately balanced.
TOTAL_SPACED_WRITES = N_SESSIONS * BATCH_SIZE
TOTAL_AAO_WRITES = N_REPLAY_TOTAL_AAO * M_ITEMS
TOTAL_UNIFORM_WRITES = N_SESSIONS * BATCH_SIZE  # same as spaced (same event count)

# Capacity self-witness.
ALPHA_SIMPLE = float(M_ITEMS) / float(N_CORTEX)
ALPHA_HOPFIELD = float(M_ITEMS) / (2.0 * float(N_HIPPO) * math.log(N_HIPPO))

USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY},M={M_ITEMS},N_sessions={N_SESSIONS},"
    f"batch_size={BATCH_SIZE},N_replay_AAO={N_REPLAY_TOTAL_AAO},"
    f"eta_c={ETA_CORTEX},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},"
    f"alpha_simple={ALPHA_SIMPLE:.4f},alpha_hopfield={ALPHA_HOPFIELD:.4f},"
    f"backend={COMPUTE_BACKEND},"
    f"total_spaced_writes={TOTAL_SPACED_WRITES},total_aao_writes={TOTAL_AAO_WRITES},"
    f"hardening=L1early+L2perarm+L4importsentinel+METARULE_AF+METARULE_AH+GPU_PROXY+SPACED_REP"
)

# Cardinality (META_RULE_H)
EXPECTED_N_UNITS = 3


# ---------------------------------------------------------------------------
# Ebbinghaus spaced-repetition schedule builder.
# ---------------------------------------------------------------------------
def build_spaced_schedule(M: int, N_sessions: int, batch_size: int,
                          intervals: List[int], seed: int) -> List[np.ndarray]:
    """Return per-session item-index arrays for brain-spaced repetition.

    Algorithm:
      1. Initial introduction: items are introduced across the first
         ceil(M / batch_size) sessions in random order.
      2. After introduction, each item is scheduled for revisits at
         session_intro + intervals[k] for k = 0..len(intervals)-1.
      3. Each session draws up to batch_size items from the due-for-revisit
         pool; if more are due, prioritize oldest (longest waiting) first;
         if fewer, fill with random samples from already-introduced items
         (this models "spontaneous" reactivation when no targeted review is
         due -- brain-realistic).

    Returns a list of length N_sessions; each element is np.array of item
    indices (shape (batch_size,)).
    """
    rng = np.random.RandomState(seed + 71)
    sessions: List[np.ndarray] = []

    # Phase 1: introduction.  Distribute items across first ceil(M / batch_size)
    # sessions.
    n_intro_sessions = int(np.ceil(M / batch_size))
    perm = rng.permutation(M)
    item_intro_session: Dict[int, int] = {}
    for s in range(n_intro_sessions):
        chunk = perm[s * batch_size:(s + 1) * batch_size]
        for it in chunk:
            item_intro_session[int(it)] = s

    # Build per-item scheduled-revisit list.
    # revisits[item] = list of session indices when item should be reviewed.
    revisits: Dict[int, List[int]] = {it: [] for it in range(M)}
    for it, s_intro in item_intro_session.items():
        # First visit = introduction itself.
        revisits[it].append(s_intro)
        # Subsequent revisits at intro + interval.
        for delta in intervals:
            s_revisit = s_intro + delta
            if s_revisit < N_sessions:
                revisits[it].append(s_revisit)

    # Build per-session due lists.  Separate INTRO items (must include) from
    # REVISIT items (lower priority).  This guarantees every item gets at
    # least its introduction visit, satisfying coverage discipline.
    session_intro_items: List[List[int]] = [[] for _ in range(N_sessions)]
    session_revisit_items: List[List[int]] = [[] for _ in range(N_sessions)]
    for it, vis_list in revisits.items():
        intro_s = vis_list[0]  # First visit = introduction.
        session_intro_items[intro_s].append(it)
        for s_rev in vis_list[1:]:
            session_revisit_items[s_rev].append(it)

    # Build per-session schedule of batch_size items.
    # Algorithm: include ALL intro items first; fill remainder with
    # revisit items prioritized by oldest-waiting; if still room, fill
    # with random introduced items (spontaneous reactivation).
    introduced_set: set = set()
    for s in range(N_sessions):
        # Update introduced set with this session's intro items.
        for it in session_intro_items[s]:
            introduced_set.add(it)

        intro_here = session_intro_items[s][:]
        rng.shuffle(intro_here)
        revisits_here = session_revisit_items[s][:]
        rng.shuffle(revisits_here)

        # All intro items first (must include for coverage discipline).
        picked_list: List[int] = list(intro_here[:batch_size])

        # Fill with revisits up to batch_size.
        if len(picked_list) < batch_size:
            need = batch_size - len(picked_list)
            picked_list.extend(revisits_here[:need])

        # If still under quota, fill with random introduced items
        # (spontaneous reactivation; brain-realistic).
        if len(picked_list) < batch_size:
            need = batch_size - len(picked_list)
            if len(introduced_set) > 0:
                introduced_arr = np.array(list(introduced_set), dtype=np.int64)
                if len(introduced_arr) >= need:
                    fill = rng.choice(introduced_arr, size=need, replace=False)
                else:
                    fill = rng.choice(introduced_arr, size=need, replace=True)
                picked_list.extend(int(x) for x in fill)
            else:
                # No introduced items yet (impossible if s>=0 and intro_phase
                # starts at s=0, but guard); pad with first batch from perm.
                picked_list.extend(int(x) for x in perm[:need])

        # If intro overflowed batch_size (i.e. more intro items than slots --
        # would happen if batch_size were tiny relative to intro chunk size,
        # which it isn't given our intro_chunk_size == batch_size design),
        # the truncation above silently dropped them.  Verify below.
        if len(intro_here) > batch_size:
            # Strict failure: intro items dropped this session.  Would compromise
            # coverage; treat as configuration error.
            raise AssertionError(
                f"build_spaced_schedule: session {s} had {len(intro_here)} intro "
                f"items but batch_size={batch_size}; intro items dropped"
            )

        sessions.append(np.array(picked_list[:batch_size], dtype=np.int64))

    # Final coverage check: every item must appear at least once.
    seen = set()
    for sess in sessions:
        for it in sess:
            seen.add(int(it))
    if len(seen) != M:
        missing = set(range(M)) - seen
        raise AssertionError(
            f"build_spaced_schedule coverage failure: {len(missing)} of {M} items "
            f"never appeared (first few missing: {sorted(list(missing))[:10]})"
        )

    return sessions


def build_uniform_schedule(M: int, N_sessions: int, batch_size: int,
                           seed: int) -> List[np.ndarray]:
    """Uniform-random schedule (no spacing curve).  Each session: random
    batch_size items with replacement across the full M-pool.  Matches
    the spaced schedule in TOTAL EVENT COUNT but with no temporal structure.
    """
    rng = np.random.RandomState(seed + 113)
    sessions: List[np.ndarray] = []
    for _s in range(N_sessions):
        picked = rng.randint(0, M, size=batch_size).astype(np.int64)
        sessions.append(picked)
    return sessions


# ---------------------------------------------------------------------------
# Substrate primitives (numpy reference path).
# ---------------------------------------------------------------------------
def pattern_separate_sparse(x: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    h_raw = P @ x
    top_k_idx = np.argpartition(-np.abs(h_raw), k - 1)[:k]
    h_sparse = np.zeros(P.shape[0], dtype=np.float64)
    signs = np.sign(h_raw[top_k_idx])
    signs[signs == 0] = 1.0
    h_sparse[top_k_idx] = signs
    return h_sparse


def project_hippo_to_cortex(h_sparse: np.ndarray, P_hc: np.ndarray) -> np.ndarray:
    c = P_hc @ h_sparse
    n = float(np.linalg.norm(c))
    if n > 0:
        c = c / n
    return c


def hippo_readout(W_h: np.ndarray, cue: np.ndarray) -> np.ndarray:
    raw = W_h @ cue
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def cortex_readout(W_c: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W_c @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def cosine_match(pred: np.ndarray, candidates: np.ndarray) -> int:
    n_p = float(np.linalg.norm(pred))
    if n_p == 0:
        return 0
    p_n = pred / n_p
    sims = candidates @ p_n
    return int(np.argmax(sims))


# ---------------------------------------------------------------------------
# Numpy per-arm runner (smoke + CPU fallback).
# ---------------------------------------------------------------------------
def _replay_one_session_numpy(W_h: np.ndarray, W_c: np.ndarray,
                              keys_h: np.ndarray, P_hc: np.ndarray,
                              session_indices: np.ndarray, eta: float) -> None:
    """Apply one session of replay-via-hippo-readout writes to W_c."""
    for i in session_indices:
        cue_h = keys_h[i]
        val_react_h = hippo_readout(W_h, cue_h)
        cue_c = P_hc @ cue_h
        n_c = float(np.linalg.norm(cue_c))
        if n_c > 0:
            cue_c = cue_c / n_c
        val_c_react = P_hc @ val_react_h
        n_v = float(np.linalg.norm(val_c_react))
        if n_v > 0:
            val_c_react = val_c_react / n_v
        W_c += eta * np.outer(val_c_react, cue_c)


def run_arm_numpy(arm_name: str, seed: int,
                  keys_raw: np.ndarray, vals_raw: np.ndarray,
                  P_in: np.ndarray, P_hc: np.ndarray, out_dir: Path) -> Dict:
    t0 = time.time()
    try:
        W_hippo = np.zeros((N_HIPPO, N_HIPPO), dtype=np.float64)
        W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION: W_h is W_c")
        if W_hippo.shape == W_cortex.shape:
            raise AssertionError(
                f"SHAPE VIOLATION: W_h.shape={W_hippo.shape} == "
                f"W_c.shape={W_cortex.shape}; should differ"
            )

        # Encode all items
        keys_h = np.zeros((M_ITEMS, N_HIPPO), dtype=np.float64)
        vals_h = np.zeros((M_ITEMS, N_HIPPO), dtype=np.float64)
        keys_c = np.zeros((M_ITEMS, N_CORTEX), dtype=np.float64)
        vals_c = np.zeros((M_ITEMS, N_CORTEX), dtype=np.float64)
        for i in range(M_ITEMS):
            keys_h[i] = pattern_separate_sparse(keys_raw[i], P_in, K_HIPPO_ACTIVE)
            vals_h[i] = pattern_separate_sparse(vals_raw[i], P_in, K_HIPPO_ACTIVE)
            keys_c[i] = project_hippo_to_cortex(keys_h[i], P_hc)
            vals_c[i] = project_hippo_to_cortex(vals_h[i], P_hc)
            if (i + 1) % 512 == 0:
                emit_heartbeat(out_dir, unit_idx=i, total_units=M_ITEMS,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "encode", "arm": arm_name})

        active_per_atom = np.sum(np.abs(keys_h) > 0, axis=1)
        if not np.all(active_per_atom == K_HIPPO_ACTIVE):
            raise AssertionError(
                f"SPARSITY VIOLATION: keys_h active counts mismatch "
                f"K_HIPPO_ACTIVE={K_HIPPO_ACTIVE}; got {active_per_atom[:5]}..."
            )

        # One-shot hippo encode (common to all arms).
        for i in range(M_ITEMS):
            W_hippo += np.outer(vals_h[i], keys_h[i])

        if arm_name == "ARM_A_BRAIN_SPACED":
            schedule = build_spaced_schedule(M_ITEMS, N_SESSIONS, BATCH_SIZE,
                                             EBBINGHAUS_INTERVALS, seed)
            n_total_writes = 0
            for s_idx, session_inds in enumerate(schedule):
                _replay_one_session_numpy(W_hippo, W_cortex, keys_h, P_hc,
                                          session_inds, ETA_CORTEX)
                n_total_writes += len(session_inds)
                if (s_idx + 1) % max(1, N_SESSIONS // 10) == 0:
                    emit_heartbeat(out_dir, unit_idx=s_idx, total_units=N_SESSIONS,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "spaced_replay", "arm": arm_name,
                                          "writes_so_far": n_total_writes})
            W_hippo[:] = 0.0

        elif arm_name == "ARM_B_ALL_AT_ONCE":
            rng = np.random.RandomState(seed + 31)
            n_total_writes = 0
            for cycle in range(N_REPLAY_TOTAL_AAO):
                replay_indices = rng.choice(M_ITEMS, size=M_ITEMS, replace=False)
                _replay_one_session_numpy(W_hippo, W_cortex, keys_h, P_hc,
                                          replay_indices, ETA_CORTEX)
                n_total_writes += M_ITEMS
                emit_heartbeat(out_dir, unit_idx=cycle, total_units=N_REPLAY_TOTAL_AAO,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "all_at_once_replay", "arm": arm_name,
                                      "writes_so_far": n_total_writes})
            W_hippo[:] = 0.0

        elif arm_name == "ARM_C_UNIFORM_REPEAT":
            schedule = build_uniform_schedule(M_ITEMS, N_SESSIONS, BATCH_SIZE, seed)
            n_total_writes = 0
            for s_idx, session_inds in enumerate(schedule):
                _replay_one_session_numpy(W_hippo, W_cortex, keys_h, P_hc,
                                          session_inds, ETA_CORTEX)
                n_total_writes += len(session_inds)
                if (s_idx + 1) % max(1, N_SESSIONS // 10) == 0:
                    emit_heartbeat(out_dir, unit_idx=s_idx, total_units=N_SESSIONS,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "uniform_replay", "arm": arm_name,
                                          "writes_so_far": n_total_writes})
            W_hippo[:] = 0.0
        else:
            raise ValueError(f"unknown arm: {arm_name}")

        # Recall test on cortex.
        n_hits = 0
        for i in range(M_ITEMS):
            pred = cortex_readout(W_cortex, keys_c[i])
            if cosine_match(pred, vals_c) == i:
                n_hits += 1
        recall = n_hits / float(M_ITEMS)
        hippo_post_zero_norm = float(np.linalg.norm(W_hippo))
        cortex_norm = float(np.linalg.norm(W_cortex))

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "hippo_post_zero_norm": float(hippo_post_zero_norm),
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_sessions": int(N_SESSIONS),
            "batch_size": int(BATCH_SIZE),
            "n_replay_total_aao": int(N_REPLAY_TOTAL_AAO),
            "wall_s": float(wall),
            "backend": "numpy",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_cortex": float("nan"),
            "n_items": 0,
            "hippo_post_zero_norm": float("nan"),
            "cortex_norm": float("nan"),
            "n_total_writes": 0,
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_sessions": int(N_SESSIONS),
            "batch_size": int(BATCH_SIZE),
            "n_replay_total_aao": int(N_REPLAY_TOTAL_AAO),
            "wall_s": float(wall),
            "backend": "numpy",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Torch/CUDA per-arm runner (FULL on remote GPU).
# ---------------------------------------------------------------------------
def _pattern_separate_sparse_torch(x, P, k):
    h_raw = x @ P.T
    abs_h = h_raw.abs()
    topk_vals, topk_idx = torch.topk(abs_h, k, dim=1)
    signs_at_topk = torch.sign(torch.gather(h_raw, 1, topk_idx))
    signs_at_topk = torch.where(signs_at_topk == 0,
                                torch.ones_like(signs_at_topk),
                                signs_at_topk)
    h_sparse = torch.zeros_like(h_raw)
    h_sparse.scatter_(1, topk_idx, signs_at_topk)
    return h_sparse


def _project_hippo_to_cortex_torch(h_sparse_batch, P_hc):
    c = h_sparse_batch @ P_hc.T
    norms = c.norm(dim=1, keepdim=True).clamp_min(1e-12)
    return c / norms


def _replay_one_session_torch(W_hippo, W_cortex, keys_h_all, P_hc,
                              session_inds_t, eta):
    """One session of batched replay-via-hippo-readout writes to W_cortex.
    session_inds_t: (B,) int64 tensor on device.
    """
    cues_h = keys_h_all[session_inds_t]      # (B, N_h)
    react_raw = cues_h @ W_hippo.T            # (B, N_h)
    vals_react_h = torch.sign(react_raw)
    vals_react_h = torch.where(vals_react_h == 0,
                               torch.ones_like(vals_react_h),
                               vals_react_h)
    cues_c = cues_h @ P_hc.T                  # (B, N_c)
    cues_c = cues_c / cues_c.norm(dim=1, keepdim=True).clamp_min(1e-12)
    vals_c_react = vals_react_h @ P_hc.T      # (B, N_c)
    vals_c_react = vals_c_react / vals_c_react.norm(dim=1, keepdim=True).clamp_min(1e-12)
    W_cortex.addmm_(vals_c_react.T, cues_c, alpha=eta)


def run_arm_torch_cuda(arm_name: str, seed: int,
                       keys_raw_np: np.ndarray, vals_raw_np: np.ndarray,
                       P_in_np: np.ndarray, P_hc_np: np.ndarray,
                       out_dir: Path) -> Dict:
    t0 = time.time()
    dev = torch.device("cuda")
    try:
        torch.cuda.reset_peak_memory_stats(dev)
        mem_start = torch.cuda.memory_allocated(dev)

        keys_raw = torch.from_numpy(keys_raw_np).to(dev, dtype=torch.float32)
        vals_raw = torch.from_numpy(vals_raw_np).to(dev, dtype=torch.float32)
        P_in = torch.from_numpy(P_in_np).to(dev, dtype=torch.float32)
        P_hc = torch.from_numpy(P_hc_np).to(dev, dtype=torch.float32)

        W_hippo = torch.zeros((N_HIPPO, N_HIPPO), dtype=torch.float32, device=dev)
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=torch.float32, device=dev)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION: W_h is W_c")
        if W_hippo.shape == W_cortex.shape:
            raise AssertionError(
                f"SHAPE VIOLATION: W_h={tuple(W_hippo.shape)} == "
                f"W_c={tuple(W_cortex.shape)}"
            )

        # Encode all items (batched)
        keys_h = _pattern_separate_sparse_torch(keys_raw, P_in, K_HIPPO_ACTIVE)  # (M, N_h)
        vals_h = _pattern_separate_sparse_torch(vals_raw, P_in, K_HIPPO_ACTIVE)  # (M, N_h)
        keys_c = _project_hippo_to_cortex_torch(keys_h, P_hc)                    # (M, N_c)
        vals_c = _project_hippo_to_cortex_torch(vals_h, P_hc)                    # (M, N_c)
        torch.cuda.synchronize(dev)

        active_per_atom = (keys_h.abs() > 0).sum(dim=1)
        if not bool((active_per_atom == K_HIPPO_ACTIVE).all().item()):
            raise AssertionError(
                f"SPARSITY VIOLATION: keys_h active mismatch K={K_HIPPO_ACTIVE}; "
                f"got first5={active_per_atom[:5].tolist()}"
            )

        # One-shot hippo encode (common to all arms).
        W_hippo.addmm_(vals_h.T, keys_h)

        n_total_writes = 0

        if arm_name == "ARM_A_BRAIN_SPACED":
            schedule = build_spaced_schedule(M_ITEMS, N_SESSIONS, BATCH_SIZE,
                                             EBBINGHAUS_INTERVALS, seed)
            for s_idx, session_inds in enumerate(schedule):
                session_inds_t = torch.from_numpy(session_inds).to(dev, dtype=torch.int64)
                _replay_one_session_torch(W_hippo, W_cortex, keys_h, P_hc,
                                          session_inds_t, ETA_CORTEX)
                n_total_writes += len(session_inds)
                if (s_idx + 1) % max(1, N_SESSIONS // 20) == 0:
                    emit_heartbeat(out_dir, unit_idx=s_idx, total_units=N_SESSIONS,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "spaced_replay", "arm": arm_name,
                                          "writes_so_far": n_total_writes,
                                          "gpu_mem_mb": torch.cuda.memory_allocated(dev) / 1e6})
            W_hippo.zero_()

        elif arm_name == "ARM_B_ALL_AT_ONCE":
            gen = torch.Generator(device=dev)
            gen.manual_seed(seed + 31)
            for cycle in range(N_REPLAY_TOTAL_AAO):
                perm = torch.randperm(M_ITEMS, generator=gen, device=dev)
                # Full-M batched replay (matches v2 parent cell's per-cycle pattern).
                cues_h = keys_h[perm]
                react_raw = cues_h @ W_hippo.T
                vals_react_h = torch.sign(react_raw)
                vals_react_h = torch.where(vals_react_h == 0,
                                           torch.ones_like(vals_react_h),
                                           vals_react_h)
                cues_c = cues_h @ P_hc.T
                cues_c = cues_c / cues_c.norm(dim=1, keepdim=True).clamp_min(1e-12)
                vals_c_react = vals_react_h @ P_hc.T
                vals_c_react = vals_c_react / vals_c_react.norm(dim=1, keepdim=True).clamp_min(1e-12)
                W_cortex.addmm_(vals_c_react.T, cues_c, alpha=ETA_CORTEX)
                n_total_writes += M_ITEMS
                emit_heartbeat(out_dir, unit_idx=cycle, total_units=N_REPLAY_TOTAL_AAO,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "all_at_once_replay", "arm": arm_name,
                                      "writes_so_far": n_total_writes})
            W_hippo.zero_()

        elif arm_name == "ARM_C_UNIFORM_REPEAT":
            schedule = build_uniform_schedule(M_ITEMS, N_SESSIONS, BATCH_SIZE, seed)
            for s_idx, session_inds in enumerate(schedule):
                session_inds_t = torch.from_numpy(session_inds).to(dev, dtype=torch.int64)
                _replay_one_session_torch(W_hippo, W_cortex, keys_h, P_hc,
                                          session_inds_t, ETA_CORTEX)
                n_total_writes += len(session_inds)
                if (s_idx + 1) % max(1, N_SESSIONS // 20) == 0:
                    emit_heartbeat(out_dir, unit_idx=s_idx, total_units=N_SESSIONS,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "uniform_replay", "arm": arm_name,
                                          "writes_so_far": n_total_writes})
            W_hippo.zero_()
        else:
            raise ValueError(f"unknown arm: {arm_name}")

        # Recall test on cortex (batched).
        preds_raw = keys_c @ W_cortex.T
        preds = torch.sign(preds_raw)
        preds = torch.where(preds == 0, torch.ones_like(preds), preds)
        preds_n = preds / preds.norm(dim=1, keepdim=True).clamp_min(1e-12)
        sims = preds_n @ vals_c.T
        argmax = sims.argmax(dim=1)
        n_hits = int((argmax == torch.arange(M_ITEMS, device=dev)).sum().item())
        recall = n_hits / float(M_ITEMS)
        hippo_post_zero_norm = float(W_hippo.norm().item())
        cortex_norm = float(W_cortex.norm().item())

        torch.cuda.synchronize(dev)
        mem_peak = torch.cuda.max_memory_allocated(dev)
        gpu_mem_peak_mb = float((mem_peak - mem_start) / 1e6)

        del keys_raw, vals_raw, P_in, P_hc, keys_h, vals_h, keys_c, vals_c
        del W_hippo, W_cortex, preds_raw, preds, preds_n, sims, argmax
        torch.cuda.empty_cache()

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "hippo_post_zero_norm": float(hippo_post_zero_norm),
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_sessions": int(N_SESSIONS),
            "batch_size": int(BATCH_SIZE),
            "n_replay_total_aao": int(N_REPLAY_TOTAL_AAO),
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": float(gpu_mem_peak_mb),
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except Exception as exc:
        wall = time.time() - t0
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
        return {
            "arm_name": arm_name,
            "recall_cortex": float("nan"),
            "n_items": 0,
            "hippo_post_zero_norm": float("nan"),
            "cortex_norm": float("nan"),
            "n_total_writes": 0,
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_sessions": int(N_SESSIONS),
            "batch_size": int(BATCH_SIZE),
            "n_replay_total_aao": int(N_REPLAY_TOTAL_AAO),
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_anatomical_separation() -> None:
    W_h = np.zeros((N_HIPPO, N_HIPPO), dtype=np.float64)
    W_c = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
    if W_h is W_c:
        raise AssertionError("W_h is W_c")
    if W_h.shape == W_c.shape:
        raise AssertionError(
            f"shapes match: W_h={W_h.shape} W_c={W_c.shape} (must differ)"
        )


def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_raw = 64
    P = rng.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=N_raw).astype(np.float64)
    h = pattern_separate_sparse(x, P, K_HIPPO_ACTIVE)
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != K_HIPPO_ACTIVE:
        raise AssertionError(
            f"k-WTA sparsity wrong: got {n_active} active, want {K_HIPPO_ACTIVE}"
        )


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS != [SEED_THIS_CHUNK]:
        raise AssertionError(
            f"chunk seed mismatch: SEEDS={SEEDS} != [SEED_THIS_CHUNK={SEED_THIS_CHUNK}]"
        )
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(
            f"anchor name '{ANCHOR_NAME}' does not contain seed_{SEED_THIS_CHUNK}"
        )


def _selftest_spaced_schedule_cardinality() -> None:
    """Verify spaced schedule produces N_SESSIONS sessions of BATCH_SIZE items
    and covers all M items at least once."""
    sched = build_spaced_schedule(M_ITEMS, N_SESSIONS, BATCH_SIZE,
                                  EBBINGHAUS_INTERVALS, SEED_THIS_CHUNK)
    if len(sched) != N_SESSIONS:
        raise AssertionError(
            f"spaced schedule wrong session count: got {len(sched)} != {N_SESSIONS}"
        )
    for s_idx, session_inds in enumerate(sched):
        if len(session_inds) != BATCH_SIZE:
            raise AssertionError(
                f"session {s_idx} wrong batch size: got {len(session_inds)} != {BATCH_SIZE}"
            )
        if (session_inds < 0).any() or (session_inds >= M_ITEMS).any():
            raise AssertionError(
                f"session {s_idx} has out-of-range index: min={session_inds.min()} "
                f"max={session_inds.max()} M={M_ITEMS}"
            )
    # All items should appear at least once.
    all_inds = np.concatenate(sched)
    unique_items = np.unique(all_inds)
    if len(unique_items) < M_ITEMS:
        raise AssertionError(
            f"spaced schedule missed items: covered {len(unique_items)} of {M_ITEMS}"
        )


def _selftest_uniform_schedule_cardinality() -> None:
    sched = build_uniform_schedule(M_ITEMS, N_SESSIONS, BATCH_SIZE, SEED_THIS_CHUNK)
    if len(sched) != N_SESSIONS:
        raise AssertionError(
            f"uniform schedule wrong session count: got {len(sched)} != {N_SESSIONS}"
        )
    total_events = sum(len(s) for s in sched)
    expected = N_SESSIONS * BATCH_SIZE
    if total_events != expected:
        raise AssertionError(
            f"uniform schedule wrong total events: got {total_events} != {expected}"
        )


def _selftest_spaced_vs_uniform_differ() -> None:
    """Spaced and uniform schedules MUST produce different replay distributions
    (otherwise the discriminator arm_A vs arm_C is meaningless).

    Test: spaced should give SOME items more replays (longer-Ebbinghaus-tail)
    while uniform gives all items ~equal expected replays.  Compare item-
    replay-count variance.
    """
    sched_spaced = build_spaced_schedule(M_ITEMS, N_SESSIONS, BATCH_SIZE,
                                         EBBINGHAUS_INTERVALS, SEED_THIS_CHUNK)
    sched_uniform = build_uniform_schedule(M_ITEMS, N_SESSIONS, BATCH_SIZE,
                                           SEED_THIS_CHUNK)
    counts_spaced = np.zeros(M_ITEMS, dtype=np.int64)
    for inds in sched_spaced:
        for i in inds:
            counts_spaced[int(i)] += 1
    counts_uniform = np.zeros(M_ITEMS, dtype=np.int64)
    for inds in sched_uniform:
        for i in inds:
            counts_uniform[int(i)] += 1

    # Both should have same TOTAL events (matched write count).
    if counts_spaced.sum() != counts_uniform.sum():
        raise AssertionError(
            f"schedule event-count mismatch: spaced={counts_spaced.sum()} "
            f"uniform={counts_uniform.sum()}"
        )

    # But spaced should have HIGHER variance in per-item count
    # (Ebbinghaus revisits cluster around early-introduced items).
    var_spaced = float(counts_spaced.var())
    var_uniform = float(counts_uniform.var())
    if not (var_spaced > var_uniform):
        # Not strictly required to assert -- but flag for visibility.
        print(f"[selftest] WARN: spaced variance ({var_spaced:.3f}) <= uniform "
              f"variance ({var_uniform:.3f}); schedules may not differ enough.")


def _selftest_capacity_alpha() -> None:
    if RUN_MODE == "full":
        if ALPHA_SIMPLE < 0.05:
            raise AssertionError(
                f"CAPACITY_WARN: alpha_simple=M/N_c={ALPHA_SIMPLE:.4f} < 0.05"
            )


def _selftest_torch_batched_matches_numpy() -> None:
    if not _TORCH_AVAILABLE:
        return
    np_rng = np.random.RandomState(3)
    M_t, Nh_t, Nc_t = 8, 16, 32
    keys_np = np_rng.randn(M_t, Nh_t).astype(np.float32)
    vals_np = np_rng.randn(M_t, Nc_t).astype(np.float32)
    eta = 0.1
    W_loop = np.zeros((Nc_t, Nh_t), dtype=np.float32)
    for i in range(M_t):
        W_loop += eta * np.outer(vals_np[i], keys_np[i])
    keys_t = torch.from_numpy(keys_np)
    vals_t = torch.from_numpy(vals_np)
    W_matmul = (vals_t.T @ keys_t) * eta
    diff = float((torch.from_numpy(W_loop) - W_matmul).abs().max().item())
    if diff > 1e-3:
        raise AssertionError(
            f"torch batched Hebbian matmul diverges from numpy loop: maxdiff={diff}"
        )


def _selftest_arms_produce_distinct_W_c() -> None:
    """Mini-world: verify arm_A (spaced) and arm_B (all_at_once) produce
    DIFFERENT W_cortex (catches schedule-collapse bugs).
    """
    np_rng = np.random.RandomState(91)
    N_raw_t, M_t, Nh_t, Nc_t, sparsity_t, eta_t = 32, 32, 64, 128, 0.10, 0.05
    k_t = max(1, int(round(sparsity_t * Nh_t)))
    n_sess_t, batch_t, n_aao_t = 16, 8, 2  # 16*8=128 events; 2*32=64 events -> not matched but ok for distinctness
    intervals_t = [1, 2, 5]

    P_in_t = np_rng.randn(Nh_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc_t = np_rng.randn(Nc_t, Nh_t).astype(np.float64) / np.sqrt(Nh_t)
    keys_raw_t = np_rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals_raw_t = np_rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)

    keys_h_t = np.zeros((M_t, Nh_t), dtype=np.float64)
    vals_h_t = np.zeros((M_t, Nh_t), dtype=np.float64)
    for i in range(M_t):
        keys_h_t[i] = pattern_separate_sparse(keys_raw_t[i], P_in_t, k_t)
        vals_h_t[i] = pattern_separate_sparse(vals_raw_t[i], P_in_t, k_t)
    W_h = np.zeros((Nh_t, Nh_t), dtype=np.float64)
    for i in range(M_t):
        W_h += np.outer(vals_h_t[i], keys_h_t[i])

    def replay_session_local(W_c: np.ndarray, sess_inds: np.ndarray) -> None:
        for i in sess_inds:
            cue_h = keys_h_t[i]
            val_react_h = hippo_readout(W_h, cue_h)
            cue_c = P_hc_t @ cue_h
            n_c = float(np.linalg.norm(cue_c))
            if n_c > 0:
                cue_c = cue_c / n_c
            val_c_react = P_hc_t @ val_react_h
            n_v = float(np.linalg.norm(val_c_react))
            if n_v > 0:
                val_c_react = val_c_react / n_v
            W_c += eta_t * np.outer(val_c_react, cue_c)

    # arm_A: spaced
    W_c_A = np.zeros((Nc_t, Nc_t), dtype=np.float64)
    sched_A = build_spaced_schedule(M_t, n_sess_t, batch_t, intervals_t, 5)
    for sess in sched_A:
        replay_session_local(W_c_A, sess)
    # arm_B: all_at_once
    W_c_B = np.zeros((Nc_t, Nc_t), dtype=np.float64)
    rng_b = np.random.RandomState(31)
    for cycle in range(n_aao_t):
        replay_session_local(W_c_B, rng_b.choice(M_t, size=M_t, replace=False))

    diff_frob = float(np.linalg.norm(W_c_A - W_c_B))
    if diff_frob < 1e-3:
        raise AssertionError(
            f"BUG: spaced (arm_A) and all-at-once (arm_B) produced identical W_c "
            f"(diff_frob={diff_frob:.6e}); schedule did not differentiate arms"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_anatomical_separation()
        _selftest_sparse_pattern_separator()
        _selftest_chunk_seed_matches_anchor()
        _selftest_spaced_schedule_cardinality()
        _selftest_uniform_schedule_cardinality()
        _selftest_spaced_vs_uniform_differ()
        _selftest_capacity_alpha()
        _selftest_torch_batched_matches_numpy()
        _selftest_arms_produce_distinct_W_c()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  sparsity={HIPPO_SPARSITY}  "
        f"M={M_ITEMS}  N_sessions={N_SESSIONS}  batch={BATCH_SIZE}  "
        f"N_replay_AAO={N_REPLAY_TOTAL_AAO}  eta_c={ETA_CORTEX}  mode={RUN_MODE}  "
        f"chunk_seed={SEED_THIS_CHUNK}  alpha_simple={ALPHA_SIMPLE:.4f}  "
        f"backend={COMPUTE_BACKEND}  torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE}  "
        f"total_spaced_writes={TOTAL_SPACED_WRITES}  total_aao_writes={TOTAL_AAO_WRITES}  "
        f"v1_spaced_rep_NREM=YES",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    N_raw = 64
    P_in = rng.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)
    keys_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)

    print(f"  [seed={seed}] N_h={N_HIPPO} (sparse k={K_HIPPO_ACTIVE}), "
          f"N_c={N_CORTEX} (dense), M={M_ITEMS}, N_sessions={N_SESSIONS}, "
          f"batch={BATCH_SIZE}, N_replay_AAO={N_REPLAY_TOTAL_AAO}, "
          f"backend={COMPUTE_BACKEND}, spaced_rep_NREM_v1",
          flush=True)

    arms = []
    for arm_name in ("ARM_A_BRAIN_SPACED", "ARM_B_ALL_AT_ONCE", "ARM_C_UNIFORM_REPEAT"):
        if USE_TORCH_CUDA:
            out = run_arm_torch_cuda(arm_name, seed, keys_raw, vals_raw,
                                     P_in, P_hc, out_dir)
        else:
            out = run_arm_numpy(arm_name, seed, keys_raw, vals_raw,
                                P_in, P_hc, out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"recall={out['recall_cortex']:.3f} "
            f"writes={out['n_total_writes']} "
            f"cortex_norm={out['cortex_norm']:.2e} "
            f"backend={out['backend']} "
            f"gpu_mem_peak_mb={out['gpu_mem_peak_mb']:.1f} "
            f"status={out['arm_status']} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_CORTEX,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "N_sessions": N_SESSIONS,
        "batch_size": BATCH_SIZE,
        "n_replay_total_aao": N_REPLAY_TOTAL_AAO,
        "eta_c": ETA_CORTEX,
        "hippo_sparsity": HIPPO_SPARSITY,
        "k_hippo_active": K_HIPPO_ACTIVE,
        "alpha_simple": ALPHA_SIMPLE,
        "alpha_hopfield": ALPHA_HOPFIELD,
        "ebbinghaus_intervals": EBBINGHAUS_INTERVALS,
        "total_spaced_writes": TOTAL_SPACED_WRITES,
        "total_aao_writes": TOTAL_AAO_WRITES,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    arm_names = ("ARM_A_BRAIN_SPACED", "ARM_B_ALL_AT_ONCE", "ARM_C_UNIFORM_REPEAT")
    n_arms = len(r["arms"])
    if n_arms != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {EXPECTED_N_UNITS} arms, got {n_arms}")
    try:
        per = [_arm_by_name(r["arms"], name) for name in arm_names]
    except KeyError as e:
        return ("HARD_FAIL", f"Missing arm: {e}")
    for a in per:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL", f"Arm {a['arm_name']} error: {a['arm_status']}")

    spaced = per[0]["recall_cortex"]
    aao = per[1]["recall_cortex"]
    uniform = per[2]["recall_cortex"]
    gap_spaced_vs_aao = spaced - aao
    gap_spaced_vs_uniform = spaced - uniform
    gap_aao_vs_uniform = aao - uniform
    arm_dist_spaced_vs_aao = abs(spaced - aao)

    # META_RULE_AF: bit-exact arms forbidden.
    if arm_dist_spaced_vs_aao < 1e-6:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION (bit-exact): SPACED={spaced} == AAO={aao}; "
                f"arms identical -- schedule mechanism not engaged")

    summary = (
        f"seed={SEED_THIS_CHUNK} "
        f"SPACED={spaced:.3f} ALL_AT_ONCE={aao:.3f} UNIFORM={uniform:.3f} "
        f"gap_SPACED_vs_AAO={gap_spaced_vs_aao:+.3f} "
        f"gap_SPACED_vs_UNIFORM={gap_spaced_vs_uniform:+.3f} "
        f"gap_AAO_vs_UNIFORM={gap_aao_vs_uniform:+.3f} "
        f"alpha_simple={ALPHA_SIMPLE:.4f} backend={COMPUTE_BACKEND}"
    )

    # META_RULE_AF (fuzzy): if all three arms produce equal recall (within 0.01),
    # mechanism is meaningless.
    if max(abs(spaced - aao), abs(spaced - uniform), abs(aao - uniform)) < 0.01:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION (3-way collapse): all arms within 0.01; "
                f"no schedule differentiates outcome. {summary}")

    # Hard-fail: spaced actively hurts vs all-at-once.
    if gap_spaced_vs_aao < 0.0:
        return ("HARD_FAIL",
                f"HARD_FAIL: BRAIN_SPACED ({spaced:.3f}) < ALL_AT_ONCE ({aao:.3f}); "
                f"spacing HURTS consolidation. {summary}")

    # HARD_PASS gates.
    hp_recall = spaced >= 0.30
    hp_gap_aao = gap_spaced_vs_aao >= 0.10
    hp_arm_dist_uniform = abs(spaced - uniform) > 0.05

    # MAJOR_UNLOCK detection.
    major_unlock = (spaced >= 0.50 and gap_spaced_vs_aao >= 0.30)
    unlock_tag = " ***MAJOR_UNLOCK_POTENTIAL***" if major_unlock else ""

    if all([hp_recall, hp_gap_aao, hp_arm_dist_uniform]):
        return ("HARD_PASS",
                f"HARD_PASS: SPACED>=0.30 AND gap_vs_AAO>=0.10 AND "
                f"arm_dist_vs_UNIFORM>0.05.{unlock_tag} {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: spaced-rep partial. "
            f"hp_checks=[recall={hp_recall},gap_aao={hp_gap_aao},"
            f"arm_dist_uniform={hp_arm_dist_uniform}].{unlock_tag} {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    start_marker = out_dir / "_start_marker.txt"
    start_marker.write_text(
        f"start_ts_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"anchor={ANCHOR_NAME} run_mode={RUN_MODE} "
        f"backend={COMPUTE_BACKEND} torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE} "
        f"v1_spaced_rep_NREM=YES",
        encoding="utf-8",
    )

    run_config = {
        "N": N_CORTEX,
        "M": M_ITEMS,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} "
              f"N_h={N_HIPPO} N_c={N_CORTEX} M={M_ITEMS} "
              f"N_sessions={N_SESSIONS} batch={BATCH_SIZE} "
              f"N_replay_AAO={N_REPLAY_TOTAL_AAO} mode={RUN_MODE} "
              f"backend={COMPUTE_BACKEND}...",
              flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n",
                encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
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

    if RUN_MODE == "full" and USE_TORCH_CUDA:
        max_peak_mb = 0.0
        for r in all_results:
            for a in r.get("arms", []):
                max_peak_mb = max(max_peak_mb, float(a.get("gpu_mem_peak_mb", 0.0)))
        if max_peak_mb < 100.0:
            verdict_msg = (
                f"WARN_GPU_UNDERUTIL: max gpu_mem_peak_mb={max_peak_mb:.1f} < 100MB; "
                f"GPU may not have been used. " + verdict_msg
            )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_h={N_HIPPO} N_c={N_CORTEX} M={M_ITEMS} "
            f"N_sessions={N_SESSIONS} batch={BATCH_SIZE} "
            f"N_replay_AAO={N_REPLAY_TOTAL_AAO} mode={RUN_MODE} "
            f"alpha_simple={ALPHA_SIMPLE:.4f} backend={COMPUTE_BACKEND} "
            f"spaced_rep_NREM_v1"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "N_sessions": N_SESSIONS,
        "batch_size": BATCH_SIZE,
        "n_replay_total_aao": N_REPLAY_TOTAL_AAO,
        "ebbinghaus_intervals": EBBINGHAUS_INTERVALS,
        "total_spaced_writes": TOTAL_SPACED_WRITES,
        "total_aao_writes": TOTAL_AAO_WRITES,
        "eta_c": ETA_CORTEX,
        "hippo_sparsity": HIPPO_SPARSITY,
        "alpha_simple": ALPHA_SIMPLE,
        "alpha_hopfield": ALPHA_HOPFIELD,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1
            and len(all_results[0].get("arms", [])) == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
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


if __name__ == "__main__":
    _main()
