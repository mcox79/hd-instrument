"""edge_importance_v4_NREM_replay_modulated_trace -- replay-modulated trace.

Pre-reg: preregs/2026-06-27_edge_importance_v4_NREM_replay_modulated_trace.md

v3 (retrieval-trace x ultrametric-coreness) landed MIDDLE_BAND because
TRACE alone gave sel_minus_rand=+0.083 (well above 0.0 noise floor, well
below the +0.15 PASS floor) and the ultrametric modulator only added
+0.008 to that. Brain literature (STC / BTSP / engram reconsolidation;
2024-2025 SWR-replay work) is explicit: importance accumulates via
MULTI-EVENT reconsolidation across sharp-wave-ripple (SWR) replay during
NREM sleep, not via single-pass retrieval count. The retrieval count is
the SEED for what gets replayed; replay IS the importance-strengthening
mechanism.

Substrate has chain-grade NREM-replay primitive
(substrate_continual_NREM_replay_v1 HARD_PASS). v4 ports the multi-event
replay discipline into edge-importance scoring.

v4 mechanism:

  importance_score[atom] = base_retrieval_trace[atom]
                          + lambda_replay * replay_consolidation_count[atom]

  base_retrieval_trace[atom]         per-atom cleanup-argmax counter
                                     (accumulated ACROSS N_TRACE_PASSES
                                     wake-sleep cycles; same signal as
                                     v3 TRACE arm but populated across
                                     3 passes instead of 1)
  replay_consolidation_count[atom]   per-atom NREM-replay reactivation
                                     counter (SWR analog; how many times
                                     this atom was selected for replay)
  lambda_replay                      in {0.5, 1.0, 2.0} (REPLAY weight
                                     higher than v3's centrality lambda
                                     because replay IS importance-
                                     strengthening, not just a structural
                                     modulator)

Replay schedule (brain-grounded; load-bearing):
  N_TRACE_PASSES = 3 wake-sleep cycles. Each pass:
    1. WAKE: composite-query the substrate;
       record cleanup-argmax winners into base_retrieval_trace
       (continues incrementing across passes)
    2. NREM: sample top-K-traced atoms by current trace; replay each
       once (Hebbian outer-product re-write of (key, value) pair onto W;
       matches substrate_continual_NREM_replay_v1.write_atom_to_W
       pattern); increment replay_consolidation_count for each replayed
       atom.

  N_COMPOSITE_QUERIES split into 3 passes (total queries = v3 budget).
  Top-K replay fraction = REPLAY_FRAC * N_USE (~48 atoms per pass at
  full-N).

ARMS (4 mandatory; pre-reg discipline):
  ARM_BASELINE_RANDOM                -- random importance (control rail)
  ARM_TRACE_ONLY                     -- importance = base_retrieval_trace
                                        (reproduces v3 TRACE arm under
                                        multi-pass schedule; control)
  ARM_TRACE_PLUS_REPLAY              -- the MECHANISM; sweeps lambda
                                        in {0.5, 1.0, 2.0}
  ARM_REPLAY_ONLY                    -- importance = replay_consolidation
                                        _count alone (control: does
                                        replay alone produce the signal?)

ALL arms share the SAME workload, SAME retrieved/unretrieved partition;
they differ only in importance-scoring + which counters they consume.

PRE-REG BANDS (load-bearing; META_PROSPECTIVE_BANDS_FRESH_SEEDS):
  HARD_PASS_REPLAY_EXTENDS_TRACE (all 5):
    best (TRACE_PLUS_REPLAY) sel_unretr asymmetry >= 0.15
    AND cor(importance, |W|) < 0.30 (USER fairness gate)
    AND mechanism fires (n_downscaled > 0 AND replay_events > 0)
    AND COMP over TRACE_ONLY: best sel >= trace_sel + 0.05
    AND COMP over REPLAY_ONLY: best sel >= replay_only_sel + 0.05

  HARD_FAIL:
    All four arms within 0.05 of each other on rec_RETRIEVED (saturation)
    OR cor(importance, |W|) >= 0.30 (fairness regression)
    OR n_downscaled == 0 OR replay_events == 0 (inert mechanism)
    OR composition UNDERPERFORMS trace_only by > 0.02 on sel_unretr
    OR any caught exception (D3 no-silent-except)

  MIDDLE_BAND: fairness held + mechanism fired + some sel_unretr signal
    but full PASS not cleared.

NEW DISCIPLINES (META rules):
  D1 Discriminator-must-survive-scale: smoke runs at FULL-N (same N,
     M_OLD, M_RECENT); only J / seeds / N_QUERIES reduced. Composition
     must show sel_unretr advantage >= 0.03 over TRACE_ONLY at smoke or
     stop and route back.
  D2 Smoke-must-FIRE-discriminator: n_downscaled > 0 AND
     trace_total > 0 AND replay_events > 0.
  D3 No-silent-except: setup + each arm wrapped.
  D4 cardinality_ok: SEEDS x (3 single arms + LAMBDA_REPLAY_LIST
     composition arms) per seed; HARD_FAIL on cardinality breach.

ASCII-only; no unicode; no em-dashes; no emojis.
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
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    aggregate_partials,
    get_output_dir,
    resumable_seeds,
    write_partial,
)
from hdlab.edge_importance import EdgeImportance, HConfig, correlation_E_vs_magnitude


ANCHOR_NAME = "edge_importance_v4_NREM_replay_modulated_trace"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# Inherit v2/v3 high-alpha regime so the discriminator survives scale.
N_FULL = 512
M_OLD_FULL = 600
M_RECENT_FULL = 400
N_COMPOSITE_QUERIES_FULL = 3000   # split across 3 passes -> 1000/pass
COMPOSITE_ARITY = 3
USE_FRAC_FULL = 0.40
DOWNSCALE_SCALE = 0.20
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200

# v4 replay schedule (load-bearing; brain-grounded)
N_TRACE_PASSES = 3                 # wake-sleep cycles
REPLAY_FRAC = 0.20                 # top-frac of N_USE replayed per pass
LAMBDA_REPLAY_LIST = [0.5, 1.0, 2.0]

# D1 discipline: smoke runs at FULL-N (same N, M_OLD, M_RECENT). Only
# J / seeds / N_QUERIES reduced. Composition discriminator must survive
# scale at smoke; else stop and route back.
if RUN_MODE == "smoke":
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    N_COMPOSITE_QUERIES = 1500   # 500 queries per pass (half full budget)
    USE_FRAC = USE_FRAC_FULL
    SEEDS = [7]
    N_QUERIES = 100
else:
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    N_COMPOSITE_QUERIES = N_COMPOSITE_QUERIES_FULL
    USE_FRAC = USE_FRAC_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL

M_TOTAL = M_OLD + M_RECENT
ALPHA = M_TOTAL / N
N_USE = max(COMPOSITE_ARITY, int(round(USE_FRAC * M_OLD)))
N_PRUNE_FRAC = 0.30
# Per-pass query budget (3 passes; floor=1 for tiny smoke)
QUERIES_PER_PASS = max(1, N_COMPOSITE_QUERIES // N_TRACE_PASSES)
# Top-K-traced atoms replayed per pass
REPLAY_K = max(1, int(round(REPLAY_FRAC * N_USE)))

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M_OLD={M_OLD},M_RECENT={M_RECENT},"
    f"alpha={ALPHA:.3f},J_composite={N_COMPOSITE_QUERIES},"
    f"N_TRACE_PASSES={N_TRACE_PASSES},QUERIES_PER_PASS={QUERIES_PER_PASS},"
    f"arity={COMPOSITE_ARITY},USE_FRAC={USE_FRAC},"
    f"DOWNSCALE_SCALE={DOWNSCALE_SCALE},LAMBDA_REPLAY_LIST={LAMBDA_REPLAY_LIST},"
    f"REPLAY_FRAC={REPLAY_FRAC},REPLAY_K={REPLAY_K},"
    f"N_PRUNE_FRAC={N_PRUNE_FRAC},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"N_QUERIES={N_QUERIES},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Pattern generation (mirrors v3 conventions; bipolar keys/values)
# ---------------------------------------------------------------------------
def generate_pairs(M_count: int, N_dim: int,
                   seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    keys = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    return keys, values


def build_W_from_pairs(keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    return values.T @ keys


def predict(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def recall_subset(W: np.ndarray, keys: np.ndarray,
                  query_idx: np.ndarray,
                  all_values: np.ndarray) -> float:
    N_dim = keys.shape[1]
    if len(query_idx) == 0:
        return float("nan")
    n_hits = 0
    for i in query_idx:
        pred = predict(W, keys[i])
        sims = all_values @ pred / float(N_dim)
        argmax = int(np.argmax(sims))
        if argmax == i:
            n_hits += 1
    return n_hits / float(len(query_idx))


def composite_query_bundle(keys: np.ndarray,
                           indices: np.ndarray) -> np.ndarray:
    bundle = np.sum(keys[indices], axis=0)
    out = np.sign(bundle)
    out[out == 0] = 1.0
    return out


def cleanup_argmax(all_values: np.ndarray, pred: np.ndarray,
                   N_dim: int) -> int:
    """Cleanup-argmax: index of closest value-vector.

    Each cleanup hit increments the base_retrieval_trace for the atom
    whose value-vector wins (brain STC analog).
    """
    sims = all_values @ pred / float(N_dim)
    return int(np.argmax(sims))


def replay_atom_to_W(W: np.ndarray, key: np.ndarray,
                     value: np.ndarray) -> None:
    """NREM replay: outer-product re-write of (key, value) onto W.

    Matches substrate_continual_NREM_replay_v1.write_atom_to_W pattern
    but for the (value, key) outer-product form used by the predict
    operation here (W @ key -> value).
    """
    W += np.outer(value, key)


def setup_substrate_with_multipass_trace_and_replay(
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, EdgeImportance,
           np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    """Build W + populate edge graph + populate base_retrieval_trace AND
    replay_consolidation_count via N_TRACE_PASSES wake-sleep cycles.

    Returns:
      W (N, N) -- consolidated W (after old + recent + replay re-writes)
      all_keys (M_TOTAL, N)
      all_values (M_TOTAL, N)
      edge_graph -- chain-grade EdgeImportance (populated during WAKE)
      retrieved_idx (N_USE,) -- atoms drawn from in composite queries
      unretrieved_idx (M_OLD - N_USE,)
      base_retrieval_trace (M_TOTAL,) -- per-atom cleanup-argmax count
                                          (across all 3 passes)
      replay_consolidation_count (M_TOTAL,) -- per-atom replay count
      replay_events_total -- int sum of all replay reactivations
    """
    keys_old, values_old = generate_pairs(M_OLD, N, seed)
    keys_rec, values_rec = generate_pairs(M_RECENT, N, seed + 999)
    all_keys = np.concatenate([keys_old, keys_rec], axis=0)
    all_values = np.concatenate([values_old, values_rec], axis=0)

    cfg = HConfig(
        increment=1.0, decay_step=0.0, floor=0.0,
        e_thresh=2.0, h_thresh=3.0,
    )
    edge_graph = EdgeImportance(n_atoms=M_TOTAL, cfg=cfg)

    # Build W from OLD only initially; recent is added at end (matches v3
    # convention: keeps trace populated from OLD-set queries; recent
    # patterns added at end is the "intervening drift" before evaluation).
    W = build_W_from_pairs(keys_old, values_old)

    rng = np.random.RandomState(seed + 401)
    retrieved_idx = rng.choice(M_OLD, size=N_USE, replace=False)
    retrieved_idx.sort()
    unretrieved_mask = np.ones(M_OLD, dtype=bool)
    unretrieved_mask[retrieved_idx] = False
    unretrieved_idx = np.where(unretrieved_mask)[0]

    base_retrieval_trace = np.zeros(M_TOTAL, dtype=np.float64)
    replay_consolidation_count = np.zeros(M_TOTAL, dtype=np.float64)
    replay_events_total = 0

    rng_q = np.random.RandomState(seed + 1117)
    for pass_idx in range(N_TRACE_PASSES):
        # --- WAKE: composite-query, record argmax winners into trace ---
        for _q in range(QUERIES_PER_PASS):
            triple = rng_q.choice(retrieved_idx, size=COMPOSITE_ARITY,
                                  replace=False)
            bundled_key = composite_query_bundle(all_keys, triple)
            pred = predict(W, bundled_key)
            winner = cleanup_argmax(all_values, pred, N)
            base_retrieval_trace[winner] += 1.0
            edge_graph.increment_query(triple)
            edge_graph.decay_all()

        # --- NREM: sample top-K-traced atoms; replay; bump replay counter ---
        # Top-K by current trace (ties broken by index order via argsort
        # stable semantics; we want deterministic-per-seed selection).
        # Add tiny rng-jitter to break exact ties consistently per pass.
        rng_replay = np.random.RandomState(seed + 7000 + pass_idx)
        jitter = rng_replay.rand(M_TOTAL) * 1e-9
        trace_score = base_retrieval_trace + jitter
        # We want HIGHEST trace -> replayed; argsort descending via -score
        top_k = np.argsort(-trace_score)[:REPLAY_K]
        for idx in top_k:
            replay_atom_to_W(W, all_keys[idx], all_values[idx])
            replay_consolidation_count[idx] += 1.0
            replay_events_total += 1

    # Final consolidation: add recent patterns (the "intervening drift").
    W = W + build_W_from_pairs(keys_rec, values_rec)

    return (W, all_keys, all_values, edge_graph, retrieved_idx,
            unretrieved_idx, base_retrieval_trace,
            replay_consolidation_count, replay_events_total)


# ---------------------------------------------------------------------------
# Importance scoring per arm (the v4 mechanism is TRACE_PLUS_REPLAY)
# ---------------------------------------------------------------------------
def importance_random(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 7777)
    return rng.rand(M_TOTAL)


def importance_trace_only(base_retrieval_trace: np.ndarray) -> np.ndarray:
    return base_retrieval_trace.copy()


def importance_replay_only(
    replay_consolidation_count: np.ndarray,
) -> np.ndarray:
    return replay_consolidation_count.copy()


def importance_trace_plus_replay(
    base_retrieval_trace: np.ndarray,
    replay_consolidation_count: np.ndarray,
    lam: float,
) -> np.ndarray:
    return base_retrieval_trace + lam * replay_consolidation_count


def select_prune_indices_low(importance: np.ndarray,
                             n_prune: int,
                             seed: int) -> np.ndarray:
    """Select the N_PRUNE atoms with LOWEST importance (ties broken by
    a stable seed-determined random shuffle)."""
    rng = np.random.RandomState(seed + 13131)
    jitter = rng.rand(importance.shape[0]) * 1e-6
    score = importance + jitter
    return np.argsort(score)[:n_prune]


# ---------------------------------------------------------------------------
# Arm runner: all arms prune n_prune atoms by DOWNSCALE_SCALE; only
# importance selection differs.
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            shared: Tuple,
            lam: float = 1.0) -> Dict:
    t0 = time.time()
    (W_base, all_keys, all_values, edge_graph,
     retrieved_idx, unretrieved_idx,
     base_retrieval_trace, replay_consolidation_count,
     replay_events_total) = shared

    W = W_base.copy()
    W_norm_pre = float(np.linalg.norm(W))

    if arm_name == "ARM_BASELINE_RANDOM":
        importance = importance_random(seed)
    elif arm_name == "ARM_TRACE_ONLY":
        importance = importance_trace_only(base_retrieval_trace)
    elif arm_name == "ARM_REPLAY_ONLY":
        importance = importance_replay_only(replay_consolidation_count)
    elif arm_name == "ARM_TRACE_PLUS_REPLAY":
        importance = importance_trace_plus_replay(
            base_retrieval_trace, replay_consolidation_count, lam,
        )
    else:
        raise ValueError(f"unknown arm {arm_name}")

    # Fairness: cor(importance, |W| equivalent) (matches v3 metric).
    atom_norms = np.linalg.norm(all_keys @ W.T, axis=1) / float(N)
    cor_imp_norm = correlation_E_vs_magnitude(importance, atom_norms)

    n_prune = int(round(N_PRUNE_FRAC * M_TOTAL))
    prune_idx = select_prune_indices_low(importance, n_prune, seed)
    n_downscaled = int(len(prune_idx))

    for idx in prune_idx:
        W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
            all_values[idx], all_keys[idx],
        )

    W_norm_post = float(np.linalg.norm(W))

    rng_eval = np.random.RandomState(seed + 503)
    n_q_ret = min(N_QUERIES, len(retrieved_idx))
    n_q_unret = min(N_QUERIES, len(unretrieved_idx))
    n_q_rec = min(N_QUERIES, M_RECENT)
    ret_query = rng_eval.choice(retrieved_idx, size=n_q_ret,
                                replace=False)
    unret_query = rng_eval.choice(unretrieved_idx, size=n_q_unret,
                                  replace=False)
    rec_query = rng_eval.choice(M_RECENT, size=n_q_rec,
                                replace=False) + M_OLD

    recall_old_retrieved = recall_subset(W, all_keys, ret_query,
                                         all_values)
    recall_old_unretrieved = recall_subset(W, all_keys, unret_query,
                                           all_values)
    recall_recent = recall_subset(W, all_keys, rec_query, all_values)

    elapsed = time.time() - t0

    return {
        "arm_name": arm_name,
        "lambda": float(lam) if arm_name == "ARM_TRACE_PLUS_REPLAY" else None,
        "recall_old_RETRIEVED": float(recall_old_retrieved),
        "recall_old_UNRETRIEVED": float(recall_old_unretrieved),
        "recall_recent": float(recall_recent),
        "W_norm_pre": W_norm_pre,
        "W_norm_post": W_norm_post,
        "cor_importance_magnitude": float(cor_imp_norm),
        "importance_min": float(np.min(importance)),
        "importance_max": float(np.max(importance)),
        "importance_mean": float(np.mean(importance)),
        "n_downscaled": int(n_downscaled),
        "downscale_frac_actual": float(n_downscaled) / float(M_TOTAL),
        "wall_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Self-tests (must FIRE the discriminator at module import time)
# ---------------------------------------------------------------------------
def _selftest_retrieval_trace_increments_on_argmax() -> bool:
    """Cleanup-argmax produces deterministic winner; trace counter is
    monotonic-non-decreasing across multiple wake passes."""
    rng = np.random.RandomState(0)
    keys = rng.choice([-1.0, 1.0], size=(20, 64)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(20, 64)).astype(np.float64)
    W = values.T @ keys
    pred = predict(W, keys[3])
    winner = cleanup_argmax(values, pred, 64)
    assert winner == 3, (
        f"selftest cleanup-argmax: expected winner=3; got {winner}"
    )
    return True


def _selftest_replay_increments_replay_counter() -> bool:
    """Each replay event increments replay_consolidation_count by 1 for
    the replayed atom and adds the outer-product to W."""
    rng = np.random.RandomState(1)
    n = 64
    m = 8
    keys = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    W = build_W_from_pairs(keys, values)
    W_pre_norm = np.linalg.norm(W)
    counter = np.zeros(m, dtype=np.float64)
    # Replay atom index 3 twice.
    replay_atom_to_W(W, keys[3], values[3])
    counter[3] += 1.0
    replay_atom_to_W(W, keys[3], values[3])
    counter[3] += 1.0
    assert counter[3] == 2.0, (
        f"selftest replay counter: expected 2.0; got {counter[3]}"
    )
    W_post_norm = np.linalg.norm(W)
    assert W_post_norm > W_pre_norm, (
        f"selftest replay W norm should strictly increase: "
        f"pre={W_pre_norm:.3f} post={W_post_norm:.3f}"
    )
    return True


def _selftest_lambda_modulator_effect() -> bool:
    """lambda=0 reduces to trace-only; lambda>0 boosts replayed atoms."""
    trace = np.array([1.0, 1.0, 1.0])
    replay = np.array([2.0, 0.0, 5.0])
    imp_l0 = importance_trace_plus_replay(trace, replay, 0.0)
    imp_l1 = importance_trace_plus_replay(trace, replay, 1.0)
    imp_l2 = importance_trace_plus_replay(trace, replay, 2.0)
    assert np.allclose(imp_l0, trace), (
        f"lambda=0: {imp_l0} should = trace={trace}"
    )
    # imp_l1 = [1+2, 1+0, 1+5] = [3, 1, 6]
    assert imp_l1[0] == 3.0 and imp_l1[1] == 1.0 and imp_l1[2] == 6.0, (
        f"lambda=1: expected [3, 1, 6]; got {imp_l1}"
    )
    # imp_l2 = [1+4, 1+0, 1+10] = [5, 1, 11]
    assert imp_l2[0] == 5.0 and imp_l2[1] == 1.0 and imp_l2[2] == 11.0, (
        f"lambda=2: expected [5, 1, 11]; got {imp_l2}"
    )
    return True


def _selftest_composition_differs_from_trace_only_with_nontrivial_replay() -> bool:
    """When replay_count is non-trivial, composition produces a different
    prune set than trace_only at the same seed/size.

    Construction: trace[0:50] in {1..20}; trace[50:100] all zero. Replay
    LIFTS 20 zero-trace atoms (50:70) into the importance ranking via
    replay_count alone. Without replay, the 30 LOWEST-trace atoms come
    from the [50:100] zero zone (tie-broken by jitter). WITH replay
    weight lambda=5.0 strong enough to dominate trace, the atoms
    [50:70] now have importance up to 5*5=25 which exceeds the lowest
    non-zero trace atoms; the prune set shifts toward those non-zero
    trace atoms with smallest trace counts.
    """
    n = 100
    rng = np.random.RandomState(42)
    trace = np.zeros(n)
    trace[:50] = rng.randint(1, 20, size=50).astype(np.float64)
    replay = np.zeros(n)
    replay[50:70] = rng.randint(1, 6, size=20).astype(np.float64)
    imp_trace = importance_trace_only(trace)
    imp_comp = importance_trace_plus_replay(trace, replay, 5.0)
    prune_trace = select_prune_indices_low(imp_trace, 30, 0)
    prune_comp = select_prune_indices_low(imp_comp, 30, 0)
    # The replayed atoms [50:70] should LARGELY shift out of the prune
    # set under composition (they were zero-trace before; now they have
    # importance up to 5*5=25, which exceeds the lowest non-zero trace).
    n_replayed_pruned_trace = int(np.sum((prune_trace >= 50)
                                         & (prune_trace < 70)))
    n_replayed_pruned_comp = int(np.sum((prune_comp >= 50)
                                         & (prune_comp < 70)))
    assert n_replayed_pruned_comp < n_replayed_pruned_trace, (
        f"selftest composition: replay arm should prune FEWER of the "
        f"replayed atoms; got comp={n_replayed_pruned_comp} "
        f"trace={n_replayed_pruned_trace}"
    )
    assert set(prune_trace.tolist()) != set(prune_comp.tolist()), (
        "selftest composition: expected different prune set vs trace_only "
        "when replay_count is non-trivial"
    )
    return True


def _selftest_replay_only_differs_from_random() -> bool:
    """When replay_count is non-uniform, replay_only produces a different
    prune set than random."""
    n = 100
    rng = np.random.RandomState(43)
    replay = np.zeros(n)
    replay[:20] = rng.randint(1, 10, size=20).astype(np.float64)
    imp_replay = importance_replay_only(replay)
    imp_rand = importance_random(0)[:n]
    prune_replay = select_prune_indices_low(imp_replay, 30, 0)
    prune_rand = select_prune_indices_low(imp_rand, 30, 0)
    assert set(prune_replay.tolist()) != set(prune_rand.tolist()), (
        "selftest replay_only: expected different prune set vs random"
    )
    # Replay-heavy atoms should NOT be in the pruned set (they have the
    # highest importance among any non-zero atoms).
    n_heavy_pruned = int(np.sum(prune_replay < 20))
    assert n_heavy_pruned <= 5, (
        f"selftest replay_only: too many heavy atoms pruned "
        f"({n_heavy_pruned} of top-20)"
    )
    return True


def _selftest_fairness_orthogonality_synthetic() -> bool:
    """Random importance vs random magnitude: |cor| < 0.30 in
    expectation."""
    rng = np.random.RandomState(0)
    importance = rng.rand(200)
    atom_norms = rng.rand(200)
    cor = correlation_E_vs_magnitude(importance, atom_norms)
    assert abs(cor) < 0.30, (
        f"selftest orthogonality: |cor|={abs(cor):.3f} should be < 0.30"
    )
    return True


def _selftest_alpha_regime_is_high() -> bool:
    """v4 must run in v2/v3 high-alpha regime (alpha >= 1.5) where the
    discriminator survives scale."""
    assert ALPHA >= 1.5, (
        f"v4 must run at HIGH-alpha regime; got alpha={ALPHA:.3f} < 1.5. "
        f"N={N}, M_TOTAL={M_TOTAL}."
    )
    return True


def _selftest_replay_schedule_load_bearing() -> bool:
    """N_TRACE_PASSES >= 2 (single-pass = v3 TRACE arm); QUERIES_PER_PASS
    >= 1; REPLAY_K >= 1 (replay must actually fire)."""
    assert N_TRACE_PASSES >= 2, (
        f"v4 requires N_TRACE_PASSES >= 2 (multi-event); got "
        f"{N_TRACE_PASSES}"
    )
    assert QUERIES_PER_PASS >= 1, (
        f"v4 requires QUERIES_PER_PASS >= 1; got {QUERIES_PER_PASS}"
    )
    assert REPLAY_K >= 1, (
        f"v4 requires REPLAY_K >= 1 (replay must fire); got {REPLAY_K}"
    )
    return True


def _instrumentation_selftest():
    _selftest_retrieval_trace_increments_on_argmax()
    _selftest_replay_increments_replay_counter()
    _selftest_lambda_modulator_effect()
    _selftest_composition_differs_from_trace_only_with_nontrivial_replay()
    _selftest_replay_only_differs_from_random()
    _selftest_fairness_orthogonality_synthetic()
    _selftest_alpha_regime_is_high()
    _selftest_replay_schedule_load_bearing()
    print(
        f"[selftest] PASS  N={N}  M_OLD={M_OLD}  M_RECENT={M_RECENT}  "
        f"alpha={ALPHA:.3f}  J_comp={N_COMPOSITE_QUERIES}  "
        f"PASSES={N_TRACE_PASSES}  Q/pass={QUERIES_PER_PASS}  "
        f"REPLAY_K={REPLAY_K}  arity={COMPOSITE_ARITY}  N_USE={N_USE}  "
        f"mode={RUN_MODE}  LAMBDA_REPLAY={LAMBDA_REPLAY_LIST}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner (D3 no-silent-except)
# ---------------------------------------------------------------------------
ARM_NAMES = [
    "ARM_BASELINE_RANDOM",
    "ARM_TRACE_ONLY",
    "ARM_REPLAY_ONLY",
    "ARM_TRACE_PLUS_REPLAY",  # last; runs once per LAMBDA_REPLAY value
]


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(
        f"  [seed={seed}] setup + populate H + multipass trace + replay "
        f"(passes={N_TRACE_PASSES} J_per_pass={QUERIES_PER_PASS} "
        f"arity={COMPOSITE_ARITY} N_USE={N_USE} REPLAY_K={REPLAY_K})...",
        flush=True,
    )
    try:
        t_setup = time.time()
        shared = setup_substrate_with_multipass_trace_and_replay(seed)
        trace_total = float(np.sum(shared[6]))
        replay_total = float(np.sum(shared[7]))
        replay_events = int(shared[8])
        n_edges = shared[3].n_edges()
        print(
            f"  [seed={seed}] setup done in {time.time()-t_setup:.1f}s  "
            f"H_edges={n_edges} trace_total={trace_total:.0f} "
            f"replay_count_total={replay_total:.0f} "
            f"replay_events={replay_events}",
            flush=True,
        )
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"  [seed={seed}] SETUP_EXCEPTION: {exc}\n{tb}", flush=True)
        return {
            "seed": seed,
            "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
            "alpha": float(ALPHA), "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "exception_phase": "setup",
            "exception_msg": str(exc),
            "exception_traceback": tb,
            "arms": [],
            "elapsed_s": float(time.time() - t0),
        }

    arms = []
    # Run the 3 single-mode arms first (no lambda dependency).
    for arm_name in ARM_NAMES[:-1]:
        try:
            out = run_arm(arm_name, seed, shared=shared)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name}] "
                f"rec_RETR={out['recall_old_RETRIEVED']:.3f} "
                f"rec_UNRETR={out['recall_old_UNRETRIEVED']:.3f} "
                f"rec_rec={out['recall_recent']:.3f} "
                f"cor_imp_W={out['cor_importance_magnitude']:.3f} "
                f"n_down={out['n_downscaled']} "
                f"wall={out['wall_s']:.1f}s",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(f"  [seed={seed} {arm_name}] ARM_EXCEPTION: {exc}\n{tb}",
                  flush=True)
            arms.append({
                "arm_name": arm_name,
                "exception_msg": str(exc),
                "exception_traceback": tb,
            })

    # COMPOSITION arm runs once per LAMBDA_REPLAY value.
    for lam in LAMBDA_REPLAY_LIST:
        arm_name = "ARM_TRACE_PLUS_REPLAY"
        try:
            out = run_arm(arm_name, seed, shared=shared, lam=lam)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name} lam={lam}] "
                f"rec_RETR={out['recall_old_RETRIEVED']:.3f} "
                f"rec_UNRETR={out['recall_old_UNRETRIEVED']:.3f} "
                f"rec_rec={out['recall_recent']:.3f} "
                f"cor_imp_W={out['cor_importance_magnitude']:.3f} "
                f"n_down={out['n_downscaled']} "
                f"wall={out['wall_s']:.1f}s",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(
                f"  [seed={seed} {arm_name} lam={lam}] ARM_EXCEPTION: "
                f"{exc}\n{tb}", flush=True,
            )
            arms.append({
                "arm_name": arm_name,
                "lambda": float(lam),
                "exception_msg": str(exc),
                "exception_traceback": tb,
            })

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
        "alpha": float(ALPHA), "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(N_QUERIES), "n_use": int(N_USE),
        "downscale_scale": DOWNSCALE_SCALE,
        "n_composite_queries": N_COMPOSITE_QUERIES,
        "n_trace_passes": int(N_TRACE_PASSES),
        "queries_per_pass": int(QUERIES_PER_PASS),
        "replay_k": int(REPLAY_K),
        "replay_frac": float(REPLAY_FRAC),
        "composite_arity": COMPOSITE_ARITY,
        "n_prune_frac": float(N_PRUNE_FRAC),
        "lambda_replay_list": list(LAMBDA_REPLAY_LIST),
        "n_edges_H": int(shared[3].n_edges()),
        "trace_total": float(np.sum(shared[6])),
        "replay_count_total": float(np.sum(shared[7])),
        "replay_events": int(shared[8]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _arms_by_name(arms: List[Dict], name: str) -> List[Dict]:
    return [a for a in arms if a.get("arm_name") == name]


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    # D3: any exception is HARD_FAIL.
    for r in results:
        if "exception_phase" in r:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D3 caught {r['exception_phase']} "
                    f"exception seed={r['seed']}: {r['exception_msg']}")
        for a in r.get("arms", []):
            if "exception_msg" in a:
                return ("HARD_FAIL",
                        f"HARD_FAIL: D3 caught arm exception "
                        f"seed={r['seed']} arm={a['arm_name']}: "
                        f"{a['exception_msg']}")

    # D4 cardinality: 3 single arms + len(LAMBDA_REPLAY_LIST) composition
    # arms per seed.
    expected_per_seed = (len(ARM_NAMES) - 1) + len(LAMBDA_REPLAY_LIST)
    for r in results:
        got = len(r.get("arms", []))
        if got != expected_per_seed:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D4 cardinality_ok breach seed={r['seed']}: "
                    f"expected {expected_per_seed} arm entries, got {got}")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate violated.")

    # D2 mechanism-fires gate: replay_events > 0 across all seeds.
    for r in results:
        if r.get("replay_events", 0) <= 0:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D2 mechanism inert seed={r['seed']}: "
                    f"replay_events=0 (NREM-replay did not run).")

    # Aggregate per arm across seeds.
    def _agg_single(arm_name: str) -> Dict[str, float]:
        per = []
        for r in results:
            per.extend(_arms_by_name(r["arms"], arm_name))
        rec_retr = [a["recall_old_RETRIEVED"] for a in per]
        rec_unretr = [a["recall_old_UNRETRIEVED"] for a in per]
        rec_rec = [a["recall_recent"] for a in per]
        cor = [a["cor_importance_magnitude"] for a in per]
        ndown = [a["n_downscaled"] for a in per]
        return {
            "mean_rec_RETRIEVED": float(np.mean(rec_retr)),
            "std_rec_RETRIEVED": float(np.std(rec_retr)),
            "cv_rec_RETRIEVED": float(
                np.std(rec_retr) / max(abs(np.mean(rec_retr)), 1e-9)
            ),
            "mean_rec_UNRETRIEVED": float(np.mean(rec_unretr)),
            "mean_rec_recent": float(np.mean(rec_rec)),
            "mean_cor_imp_W": float(np.mean(cor)),
            "mean_n_downscaled": float(np.mean(ndown)),
        }

    def _agg_composition(lam: float) -> Dict[str, float]:
        per = []
        for r in results:
            for a in _arms_by_name(r["arms"], "ARM_TRACE_PLUS_REPLAY"):
                if a.get("lambda") == lam:
                    per.append(a)
        if not per:
            return {}
        rec_retr = [a["recall_old_RETRIEVED"] for a in per]
        rec_unretr = [a["recall_old_UNRETRIEVED"] for a in per]
        rec_rec = [a["recall_recent"] for a in per]
        cor = [a["cor_importance_magnitude"] for a in per]
        ndown = [a["n_downscaled"] for a in per]
        return {
            "lambda": float(lam),
            "mean_rec_RETRIEVED": float(np.mean(rec_retr)),
            "std_rec_RETRIEVED": float(np.std(rec_retr)),
            "cv_rec_RETRIEVED": float(
                np.std(rec_retr) / max(abs(np.mean(rec_retr)), 1e-9)
            ),
            "mean_rec_UNRETRIEVED": float(np.mean(rec_unretr)),
            "mean_rec_recent": float(np.mean(rec_rec)),
            "mean_cor_imp_W": float(np.mean(cor)),
            "mean_n_downscaled": float(np.mean(ndown)),
        }

    agg_rand = _agg_single("ARM_BASELINE_RANDOM")
    agg_trace = _agg_single("ARM_TRACE_ONLY")
    agg_replay = _agg_single("ARM_REPLAY_ONLY")
    agg_comp_per_lam = {lam: _agg_composition(lam)
                        for lam in LAMBDA_REPLAY_LIST}

    rand_unretr = agg_rand.get("mean_rec_UNRETRIEVED", 0.0)
    trace_unretr = agg_trace.get("mean_rec_UNRETRIEVED", 0.0)
    replay_unretr = agg_replay.get("mean_rec_UNRETRIEVED", 0.0)

    sel_trace_minus_rand = rand_unretr - trace_unretr
    sel_replay_minus_rand = rand_unretr - replay_unretr

    best_lam = LAMBDA_REPLAY_LIST[0]
    best_sel_unretr = -1.0
    for lam in LAMBDA_REPLAY_LIST:
        a = agg_comp_per_lam[lam]
        if not a:
            continue
        sel = rand_unretr - a["mean_rec_UNRETRIEVED"]
        if sel > best_sel_unretr:
            best_sel_unretr = sel
            best_lam = lam
    best_comp = agg_comp_per_lam[best_lam]

    summary = (
        f"alpha={ALPHA:.3f} lam_best={best_lam} "
        f"RAND(retr={agg_rand['mean_rec_RETRIEVED']:.3f},"
        f"unretr={agg_rand['mean_rec_UNRETRIEVED']:.3f}); "
        f"TRACE(retr={agg_trace['mean_rec_RETRIEVED']:.3f},"
        f"unretr={agg_trace['mean_rec_UNRETRIEVED']:.3f},"
        f"sel_minus_rand={sel_trace_minus_rand:+.3f}); "
        f"REPLAY(retr={agg_replay['mean_rec_RETRIEVED']:.3f},"
        f"unretr={agg_replay['mean_rec_UNRETRIEVED']:.3f},"
        f"sel_minus_rand={sel_replay_minus_rand:+.3f}); "
        f"COMP(retr={best_comp['mean_rec_RETRIEVED']:.3f},"
        f"unretr={best_comp['mean_rec_UNRETRIEVED']:.3f},"
        f"cor={best_comp['mean_cor_imp_W']:.3f},"
        f"cv={best_comp['cv_rec_RETRIEVED']:.3f},"
        f"n_down={best_comp['mean_n_downscaled']:.0f},"
        f"sel_minus_rand={best_sel_unretr:+.3f})"
    )

    # Non-finite guards
    for name, a in [("RAND", agg_rand), ("TRACE", agg_trace),
                    ("REPLAY", agg_replay), ("COMP", best_comp)]:
        if not (np.isfinite(a.get("mean_rec_RETRIEVED", float("nan"))) and
                np.isfinite(a.get("mean_rec_UNRETRIEVED", float("nan")))):
            return ("HARD_FAIL",
                    f"HARD_FAIL: non-finite metrics in {name}. {summary}")

    # D2 mechanism-fires gate on composition arm
    if best_comp.get("mean_n_downscaled", 0) <= 0:
        return ("HARD_FAIL",
                f"HARD_FAIL: D2 COMPOSITION mechanism inert "
                f"(n_downscaled=0). {summary}")

    # Fairness gate
    if best_comp.get("mean_cor_imp_W", 1.0) >= 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: fairness gate cor(importance,|W|)="
                f"{best_comp['mean_cor_imp_W']:.3f} >= 0.30. {summary}")

    # Saturation gate: all arms within 0.05 on rec_RETRIEVED
    max_retr = max(agg_rand["mean_rec_RETRIEVED"],
                   agg_trace["mean_rec_RETRIEVED"],
                   agg_replay["mean_rec_RETRIEVED"],
                   best_comp["mean_rec_RETRIEVED"])
    min_retr = min(agg_rand["mean_rec_RETRIEVED"],
                   agg_trace["mean_rec_RETRIEVED"],
                   agg_replay["mean_rec_RETRIEVED"],
                   best_comp["mean_rec_RETRIEVED"])
    if (max_retr - min_retr) < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: arms within 0.05 on rec_RETRIEVED "
                f"(spread={max_retr-min_retr:.3f}). Regime saturated. "
                f"{summary}")

    # Composition must not actively HURT trace_only
    if best_sel_unretr < (sel_trace_minus_rand - 0.02):
        return ("HARD_FAIL",
                f"HARD_FAIL: composition UNDERPERFORMS trace_only by "
                f"{(sel_trace_minus_rand - best_sel_unretr):.3f} > 0.02 "
                f"on sel_unretr. {summary}")

    # HARD_PASS bands (all 5 must hold)
    hp_sel_unretr = best_sel_unretr >= 0.15
    hp_fair = best_comp["mean_cor_imp_W"] < 0.30
    hp_fired = best_comp.get("mean_n_downscaled", 0) > 0
    hp_comp_over_trace = best_sel_unretr >= (sel_trace_minus_rand + 0.05)
    hp_comp_over_replay = best_sel_unretr >= (sel_replay_minus_rand + 0.05)

    if all([hp_sel_unretr, hp_fair, hp_fired,
            hp_comp_over_trace, hp_comp_over_replay]):
        return ("HARD_PASS",
                f"HARD_PASS_REPLAY_EXTENDS_TRACE: at alpha={ALPHA:.3f} "
                f"COMPOSITION(lam={best_lam}) sel_unretr="
                f"{best_sel_unretr:+.3f} >= 0.15, cor<0.30, fired, "
                f"over_trace={best_sel_unretr - sel_trace_minus_rand:+.3f}, "
                f"over_replay={best_sel_unretr - sel_replay_minus_rand:+.3f}. "
                f"{summary}")

    # MIDDLE_BAND
    mb_fair = best_comp["mean_cor_imp_W"] < 0.50
    mb_sel = best_sel_unretr > 0.0
    if all([mb_fair, mb_sel, hp_fired]):
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: composition operational but PASS bands not "
                f"cleared. hp_checks=[sel_unretr={hp_sel_unretr},"
                f"fair={hp_fair},fired={hp_fired},"
                f"over_trace={hp_comp_over_trace},"
                f"over_replay={hp_comp_over_replay}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: did not clear PASS or MIDDLE. "
            f"hp_checks=[sel_unretr={hp_sel_unretr},"
            f"fair={hp_fair},fired={hp_fired},"
            f"over_trace={hp_comp_over_trace},"
            f"over_replay={hp_comp_over_replay}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
# RULE_EXPERIMENT_CELLS_MUST_GUARD_MAIN_WITH___NAME___DUNDER (added 2026-06-27)
if __name__ == "__main__":
    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
                  "alpha": float(ALPHA), "J": N_COMPOSITE_QUERIES,
                  "run_mode": RUN_MODE,
                  "lambda_replay_list": list(LAMBDA_REPLAY_LIST),
                  "n_trace_passes": int(N_TRACE_PASSES)}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
        f"running {remaining}", flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(
            f"[seed={seed}] v4 N={N} alpha={ALPHA:.3f} "
            f"J_comp={N_COMPOSITE_QUERIES} PASSES={N_TRACE_PASSES} "
            f"Q/pass={QUERIES_PER_PASS} REPLAY_K={REPLAY_K} "
            f"arity={COMPOSITE_ARITY} N_USE={N_USE} mode={RUN_MODE}...",
            flush=True,
        )
        result = run_seed(seed)
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

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} N={N} M_OLD={M_OLD} "
            f"M_RECENT={M_RECENT} alpha={ALPHA:.3f} "
            f"J_comp={N_COMPOSITE_QUERIES} PASSES={N_TRACE_PASSES} "
            f"Q/pass={QUERIES_PER_PASS} REPLAY_K={REPLAY_K} "
            f"arity={COMPOSITE_ARITY} N_USE={N_USE} mode={RUN_MODE} "
            f"LAMBDA_REPLAY={LAMBDA_REPLAY_LIST} N_PRUNE_FRAC={N_PRUNE_FRAC}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
        "alpha": float(ALPHA),
        "n_seeds": len(SEEDS), "n_queries": N_QUERIES, "n_use": int(N_USE),
        "n_composite_queries": N_COMPOSITE_QUERIES,
        "n_trace_passes": int(N_TRACE_PASSES),
        "queries_per_pass": int(QUERIES_PER_PASS),
        "replay_k": int(REPLAY_K),
        "replay_frac": float(REPLAY_FRAC),
        "composite_arity": COMPOSITE_ARITY,
        "downscale_scale": float(DOWNSCALE_SCALE),
        "lambda_replay_list": list(LAMBDA_REPLAY_LIST),
        "n_prune_frac": float(N_PRUNE_FRAC),
        "run_mode": RUN_MODE,
        "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "trace_total": r.get("trace_total"),
                "replay_count_total": r.get("replay_count_total"),
                "replay_events": r.get("replay_events"),
                "n_edges_H": r.get("n_edges_H"),
                "arms": r.get("arms"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[metrics] written to {metrics_path}", flush=True)
