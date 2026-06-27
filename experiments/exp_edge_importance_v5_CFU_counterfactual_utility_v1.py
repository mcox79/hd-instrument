"""edge_importance_v5_CFU_counterfactual_utility_v1 -- ablation-utility importance.

Pre-reg: preregs/2026-06-27_edge_importance_v5_CFU_counterfactual_utility_v1.md

v1-v4 (PageRank-centrality + retrieval-trace + ultrametric-coreness +
NREM-replay-modulated-trace) saturate inside the smooth-function-of-H
family: top-K importance correlates with degree, and the discriminator's
'retrieved-old' set IS the high-degree set; sel_unretr asymmetry is
structurally bounded by workload degree distribution.

v5 (M-CFU) breaks the saturation by sourcing importance from a
CATEGORICALLY ORTHOGONAL signal axis: ABLATION RECALL DELTA against a
HELD-OUT probe set. Tonegawa optogenetic engram-silencing analog: per-
atom importance = recall_full - recall_when_atom_ablated. Atoms whose
removal MOST hurts retrieval = highest importance. Crucially:
  - Probe set is HELD-OUT (atoms written in a cold window; never queried
    during the wake-trace phase). This decouples CFU from retrieval-trace.
  - High-degree hubs that are redundant with neighbors get LOW CFU
    (neighborhood absorbs removal); penalizes redundancy directly.
  - Categorically off the H-smooth-integral axis.

Mechanism:

  importance_CFU[atom] = baseline_recall(P_held) - recall_when_atom_ablated(P_held)

  where ablation = zero out atom's (key,value) outer-product contribution
  to W (cohort-K leave-one-out averaging: ablate K=COHORT_K atoms at once
  and divide the delta by K to amplify signal beyond per-atom noise).

  ARM_COMBINED uses CFU * TRACE (geom-mean style); composes orthogonally
  with the retrieval-trace from v3 lineage.

4 ARMS (mandatory; pre-reg discipline):
  ARM_BASELINE_RANDOM_IMPORTANCE  - control rail; uniform random
  ARM_CFU_LEAVE_ONE_OUT           - THE MECHANISM (cohort-K=10 ablation)
  ARM_TRACE_ONLY                  - v3 retrieval-trace comparison rail
  ARM_COMBINED                    - CFU * TRACE composition; tests
                                    orthogonal stacking

ALL arms share the SAME workload + SAME retrieved/unretrieved partition;
they differ only in importance-scoring + which counters they consume.

PRE-REG BANDS (load-bearing; META_PROSPECTIVE_BANDS_FRESH_SEEDS):
  HARD_PASS (all 4 must hold):
    best CFU sel_unretr asymmetry >= 0.15 (ORIGINAL Path A PASS bar;
      CFU brain-grounded prior says P=0.50)
    AND cor(CFU_importance, |W|) < 0.30 (USER fairness gate META_RULE_F)
    AND mechanism fires (n_downscaled > 0 AND n_ablations_evaluated > 0)
    AND COMP over CFU_ONLY: combined sel >= cfu_sel + 0.03 (composition
      adds value; if not, composition is over-engineering)

  HARD_FAIL:
    All four arms within 0.05 on rec_RETRIEVED (saturation)
    OR cor(CFU, |W|) >= 0.30 (fairness regression)
    OR n_downscaled == 0 OR n_ablations_evaluated == 0 (inert)
    OR ARM_COMBINED UNDERPERFORMS ARM_CFU by > 0.02 sel_unretr (composition
      actively hurts)
    OR any caught exception (D3 no-silent-except)

  MIDDLE_BAND: fairness held + mechanism fired + some CFU signal but
    PASS bands not cleared.

NEW DISCIPLINES (META rules):
  D1 Discriminator-must-survive-scale: smoke runs at FULL-N (same N,
     M_OLD, M_RECENT); only J / seeds / N_QUERIES reduced. CFU mechanism
     must show sel_unretr > 0 at smoke or stop and route back.
  D2 Smoke-must-FIRE-discriminator: n_downscaled > 0 AND
     n_ablations_evaluated > 0 AND CFU has nonzero variance across atoms.
  D3 No-silent-except: setup + each arm wrapped.
  D4 cardinality_ok: SEEDS x 4 arm entries; HARD_FAIL on cardinality
     breach (D4 cardinality field).
  SCHEMA-VET 5b per-arm HP scope: each arm's metrics fully reported per
     seed; verdict reads per-arm not summary text (Fix #28).

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


ANCHOR_NAME = "edge_importance_v5_CFU_counterfactual_utility_v1"
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

# Inherit v3/v4 high-alpha regime so the discriminator survives scale.
N_FULL = 512
M_OLD_FULL = 600
M_RECENT_FULL = 400
M_HELDOUT_FULL = 100              # held-out probe set; never queried in WAKE
N_COMPOSITE_QUERIES_FULL = 3000   # WAKE-phase trace population (matches v3/v4)
COMPOSITE_ARITY = 3
USE_FRAC_FULL = 0.40
DOWNSCALE_SCALE = 0.20
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200

# v5 CFU schedule (load-bearing; brain-grounded)
COHORT_K = 10                      # leave-K-out cohort ablation
N_PROBE_BATCH_FULL = 100           # probe-set queries scored per ablation
CFU_EVAL_FRAC_FULL = 0.50          # fraction of atoms scored by CFU (top-CFU
                                   # cohorts; bounds compute O(M_TOTAL*K))

# D1 discipline: smoke uses FULL-N. Only J / seeds / N_QUERIES reduced.
if RUN_MODE == "smoke":
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    M_HELDOUT = M_HELDOUT_FULL
    N_COMPOSITE_QUERIES = 1500     # half full budget
    USE_FRAC = USE_FRAC_FULL
    SEEDS = [7]
    N_QUERIES = 100
    N_PROBE_BATCH = 50
    CFU_EVAL_FRAC = 0.30           # smaller fraction for smoke compute bound
else:
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    M_HELDOUT = M_HELDOUT_FULL
    N_COMPOSITE_QUERIES = N_COMPOSITE_QUERIES_FULL
    USE_FRAC = USE_FRAC_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL
    N_PROBE_BATCH = N_PROBE_BATCH_FULL
    CFU_EVAL_FRAC = CFU_EVAL_FRAC_FULL

M_TOTAL = M_OLD + M_RECENT + M_HELDOUT
ALPHA = M_TOTAL / N
N_USE = max(COMPOSITE_ARITY, int(round(USE_FRAC * M_OLD)))
N_PRUNE_FRAC = 0.30
# CFU scoring: number of atom-COHORTS evaluated; floors at 1.
N_CFU_COHORTS = max(1, int(round(CFU_EVAL_FRAC * M_TOTAL / COHORT_K)))

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M_OLD={M_OLD},M_RECENT={M_RECENT},"
    f"M_HELDOUT={M_HELDOUT},alpha={ALPHA:.3f},"
    f"J_composite={N_COMPOSITE_QUERIES},arity={COMPOSITE_ARITY},"
    f"USE_FRAC={USE_FRAC},DOWNSCALE_SCALE={DOWNSCALE_SCALE},"
    f"COHORT_K={COHORT_K},N_PROBE_BATCH={N_PROBE_BATCH},"
    f"CFU_EVAL_FRAC={CFU_EVAL_FRAC},N_CFU_COHORTS={N_CFU_COHORTS},"
    f"N_PRUNE_FRAC={N_PRUNE_FRAC},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"N_QUERIES={N_QUERIES},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Pattern generation (mirrors v3/v4 conventions; bipolar keys/values)
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
    sims = all_values @ pred / float(N_dim)
    return int(np.argmax(sims))


def setup_substrate_with_trace_and_heldout(
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, EdgeImportance,
           np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    """Build W + populate edge graph + populate base_retrieval_trace via
    single-pass WAKE composite queries. ALSO build held-out probe set
    (index range [M_OLD+M_RECENT, M_OLD+M_RECENT+M_HELDOUT)).

    The held-out probe set is BAKED INTO W (so the substrate KNOWS those
    patterns) but is NEVER QUERIED during the WAKE-trace phase (so it
    doesn't contaminate the retrieval-trace counter). CFU is then scored
    on recall of the held-out probe set under cohort ablations.

    Returns:
      W (N, N) -- consolidated W (old + recent + held-out)
      all_keys (M_TOTAL, N)
      all_values (M_TOTAL, N)
      edge_graph -- chain-grade EdgeImportance (populated during WAKE)
      retrieved_idx (N_USE,) -- atoms drawn from in composite queries
      unretrieved_idx (M_OLD - N_USE,)
      base_retrieval_trace (M_TOTAL,) -- per-atom cleanup-argmax count
      heldout_idx (M_HELDOUT,) -- held-out probe set (absolute indices)
      n_trace_events -- int (= N_COMPOSITE_QUERIES; total WAKE events)
    """
    keys_old, values_old = generate_pairs(M_OLD, N, seed)
    keys_rec, values_rec = generate_pairs(M_RECENT, N, seed + 999)
    keys_held, values_held = generate_pairs(M_HELDOUT, N, seed + 1777)
    all_keys = np.concatenate([keys_old, keys_rec, keys_held], axis=0)
    all_values = np.concatenate([values_old, values_rec, values_held], axis=0)

    cfg = HConfig(
        increment=1.0, decay_step=0.0, floor=0.0,
        e_thresh=2.0, h_thresh=3.0,
    )
    edge_graph = EdgeImportance(n_atoms=M_TOTAL, cfg=cfg)

    # Build W with ALL atoms baked in (old + recent + held-out). The
    # held-out atoms are part of the substrate's memory; they're "held-
    # out" only in the sense of NOT being queried during the wake-trace
    # population phase. CFU scoring later does query them as probes.
    W = build_W_from_pairs(all_keys, all_values)

    rng = np.random.RandomState(seed + 401)
    retrieved_idx = rng.choice(M_OLD, size=N_USE, replace=False)
    retrieved_idx.sort()
    unretrieved_mask = np.ones(M_OLD, dtype=bool)
    unretrieved_mask[retrieved_idx] = False
    unretrieved_idx = np.where(unretrieved_mask)[0]

    # Held-out probe set absolute indices
    heldout_offset = M_OLD + M_RECENT
    heldout_idx = np.arange(heldout_offset, heldout_offset + M_HELDOUT)

    base_retrieval_trace = np.zeros(M_TOTAL, dtype=np.float64)
    n_trace_events = 0

    rng_q = np.random.RandomState(seed + 1117)
    for _q in range(N_COMPOSITE_QUERIES):
        triple = rng_q.choice(retrieved_idx, size=COMPOSITE_ARITY,
                              replace=False)
        bundled_key = composite_query_bundle(all_keys, triple)
        pred = predict(W, bundled_key)
        winner = cleanup_argmax(all_values, pred, N)
        base_retrieval_trace[winner] += 1.0
        edge_graph.increment_query(triple)
        edge_graph.decay_all()
        n_trace_events += 1

    return (W, all_keys, all_values, edge_graph, retrieved_idx,
            unretrieved_idx, base_retrieval_trace, heldout_idx,
            n_trace_events)


# ---------------------------------------------------------------------------
# CFU scoring: cohort leave-K-out ablation against held-out probe set
# ---------------------------------------------------------------------------
def baseline_heldout_recall(W: np.ndarray, all_keys: np.ndarray,
                            all_values: np.ndarray,
                            heldout_idx: np.ndarray,
                            n_probe: int, seed: int) -> Tuple[float, np.ndarray]:
    """Score recall on a random subset of heldout probe atoms.

    Returns (recall_fraction, probe_idx). probe_idx is reused across
    ablations so CFU delta is comparable per atom.
    """
    rng = np.random.RandomState(seed + 9001)
    n_use = min(n_probe, len(heldout_idx))
    probe_idx = rng.choice(heldout_idx, size=n_use, replace=False)
    rec = recall_subset(W, all_keys, probe_idx, all_values)
    return rec, probe_idx


def ablate_cohort_outer_product(W: np.ndarray, keys: np.ndarray,
                                values: np.ndarray,
                                cohort: np.ndarray) -> np.ndarray:
    """Return W with cohort's (key,value) outer-product subtracted.

    This is "soft delete" of cohort atoms from W. Non-destructive: caller
    must use the returned W; original W is not mutated.
    """
    W_abl = W.copy()
    for idx in cohort:
        W_abl -= np.outer(values[idx], keys[idx])
    return W_abl


def compute_cfu_importance(W: np.ndarray, all_keys: np.ndarray,
                           all_values: np.ndarray,
                           heldout_idx: np.ndarray,
                           seed: int) -> Tuple[np.ndarray, int, float]:
    """Compute per-atom CFU importance via cohort leave-K-out.

    Atoms are partitioned into cohorts of size COHORT_K (random shuffle
    per seed). For each cohort, compute recall delta on the held-out
    probe set; assign delta/K as importance to each atom in the cohort.
    Atoms not in any scored cohort retain importance = 0.

    Returns (importance_array, n_ablations_evaluated, baseline_recall).
    """
    baseline_rec, probe_idx = baseline_heldout_recall(
        W, all_keys, all_values, heldout_idx, N_PROBE_BATCH, seed,
    )

    importance = np.zeros(M_TOTAL, dtype=np.float64)
    rng = np.random.RandomState(seed + 7000)
    # All M_TOTAL atoms are candidates for cohort assignment.
    perm = rng.permutation(M_TOTAL)
    # Take first N_CFU_COHORTS * COHORT_K atoms (drop tail if not aligned)
    n_take = min(M_TOTAL, N_CFU_COHORTS * COHORT_K)
    perm = perm[:n_take]
    n_evaluated = 0
    for c in range(N_CFU_COHORTS):
        cohort = perm[c * COHORT_K:(c + 1) * COHORT_K]
        if len(cohort) == 0:
            break
        W_abl = ablate_cohort_outer_product(W, all_keys, all_values, cohort)
        rec_abl = recall_subset(W_abl, all_keys, probe_idx, all_values)
        delta = baseline_rec - rec_abl
        # Importance per atom in cohort = delta / K (averaged over cohort)
        for idx in cohort:
            importance[idx] = delta / float(COHORT_K)
        n_evaluated += 1

    return importance, n_evaluated, float(baseline_rec)


# ---------------------------------------------------------------------------
# Importance scoring per arm
# ---------------------------------------------------------------------------
def importance_random(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 7777)
    return rng.rand(M_TOTAL)


def importance_trace_only(base_retrieval_trace: np.ndarray) -> np.ndarray:
    return base_retrieval_trace.copy()


def importance_cfu_only(cfu: np.ndarray) -> np.ndarray:
    return cfu.copy()


def importance_cfu_x_trace(cfu: np.ndarray,
                           trace: np.ndarray) -> np.ndarray:
    """Composition: CFU * TRACE (signed; supports negative CFU).

    Per design doc: 'requires BOTH utility AND surprise'. Here trace is
    quasi-frequency; multiplication weights CFU by query exposure. Atoms
    with high CFU AND high trace get highest composition score.
    """
    # Normalize each axis to [0,1] approximate scale; multiplicative
    # composition without normalization is sensitive to one axis's scale.
    cfu_max = max(np.max(np.abs(cfu)), 1e-9)
    tr_max = max(np.max(trace), 1e-9)
    cfu_n = cfu / cfu_max
    tr_n = trace / tr_max
    return cfu_n * tr_n


def select_prune_indices_low(importance: np.ndarray,
                             n_prune: int,
                             seed: int) -> np.ndarray:
    """Select the N_PRUNE atoms with LOWEST importance (stable jitter)."""
    rng = np.random.RandomState(seed + 13131)
    jitter = rng.rand(importance.shape[0]) * 1e-6
    score = importance + jitter
    return np.argsort(score)[:n_prune]


# ---------------------------------------------------------------------------
# Arm runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            shared: Tuple,
            cfu_importance: np.ndarray) -> Dict:
    t0 = time.time()
    (W_base, all_keys, all_values, edge_graph,
     retrieved_idx, unretrieved_idx,
     base_retrieval_trace, heldout_idx, n_trace_events) = shared

    W = W_base.copy()
    W_norm_pre = float(np.linalg.norm(W))

    if arm_name == "ARM_BASELINE_RANDOM_IMPORTANCE":
        importance = importance_random(seed)
    elif arm_name == "ARM_TRACE_ONLY":
        importance = importance_trace_only(base_retrieval_trace)
    elif arm_name == "ARM_CFU_LEAVE_ONE_OUT":
        importance = importance_cfu_only(cfu_importance)
    elif arm_name == "ARM_COMBINED":
        importance = importance_cfu_x_trace(cfu_importance,
                                            base_retrieval_trace)
    else:
        raise ValueError(f"unknown arm {arm_name}")

    # Fairness gate (META_RULE_F): cor(importance, |W| equivalent).
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
        "recall_old_RETRIEVED": float(recall_old_retrieved),
        "recall_old_UNRETRIEVED": float(recall_old_unretrieved),
        "recall_recent": float(recall_recent),
        "W_norm_pre": W_norm_pre,
        "W_norm_post": W_norm_post,
        "cor_importance_magnitude": float(cor_imp_norm),
        "importance_min": float(np.min(importance)),
        "importance_max": float(np.max(importance)),
        "importance_mean": float(np.mean(importance)),
        "importance_std": float(np.std(importance)),
        "n_downscaled": int(n_downscaled),
        "downscale_frac_actual": float(n_downscaled) / float(M_TOTAL),
        "wall_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Self-tests (MUST FIRE the discriminator at module import time)
# ---------------------------------------------------------------------------
def _selftest_retrieval_argmax_deterministic() -> bool:
    rng = np.random.RandomState(0)
    keys = rng.choice([-1.0, 1.0], size=(20, 64)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(20, 64)).astype(np.float64)
    W = values.T @ keys
    pred = predict(W, keys[3])
    winner = cleanup_argmax(values, pred, 64)
    assert winner == 3, f"cleanup-argmax: expected 3; got {winner}"
    return True


def _selftest_ablate_cohort_reduces_recall_for_cohort_atoms() -> bool:
    """Ablating a cohort REMOVES (key,value) outer-product so that cohort
    atom no longer cleanly retrieves from its own key. This is the load-
    bearing axiom: ablation HURTS recall of the ablated atom."""
    rng = np.random.RandomState(2)
    n = 128
    m = 20
    keys = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    W = build_W_from_pairs(keys, values)

    # Baseline: atom 3 retrieves itself.
    pred = predict(W, keys[3])
    baseline_winner = cleanup_argmax(values, pred, n)
    assert baseline_winner == 3, (
        f"baseline retrieval: expected 3 got {baseline_winner}"
    )

    # Ablate cohort containing atom 3.
    cohort = np.array([3, 5, 7])
    W_abl = ablate_cohort_outer_product(W, keys, values, cohort)
    pred_abl = predict(W_abl, keys[3])
    abl_winner = cleanup_argmax(values, pred_abl, n)
    # After ablation, atom 3 should NOT retrieve to itself (or much
    # worse signal). Either argmax changed OR margin collapsed.
    sims_orig = values @ pred / float(n)
    sims_abl = values @ pred_abl / float(n)
    margin_orig = float(sims_orig[3] - np.partition(sims_orig, -2)[-2])
    # margin_abl could be negative if atom 3 not on top anymore; that's OK
    # The axiom: post-ablation winner != 3 OR margin collapsed by > 50%.
    margin_abl_for_atom3 = float(sims_abl[3] - np.max(np.delete(sims_abl, 3)))
    assert (abl_winner != 3) or (margin_abl_for_atom3 < 0.5 * margin_orig), (
        f"ablation should hurt recall of atom 3: pre_margin={margin_orig:.3f} "
        f"abl_winner={abl_winner} abl_margin_for_atom3={margin_abl_for_atom3:.3f}"
    )
    return True


def _selftest_cfu_nonzero_when_ablation_hurts() -> bool:
    """When the held-out probe set is fully reconstructable from W and
    we ablate atoms IN the probe set, recall drops -> CFU > 0 for those
    cohorts. Construction: ensure the probe atoms get cohort assignment
    in the test."""
    rng = np.random.RandomState(3)
    n = 256
    m_total = 50
    m_heldout = 10
    keys = rng.choice([-1.0, 1.0], size=(m_total, n)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(m_total, n)).astype(np.float64)
    W = build_W_from_pairs(keys, values)
    heldout = np.arange(m_total - m_heldout, m_total)
    # Baseline recall on heldout
    probe = heldout[:5]
    baseline = recall_subset(W, keys, probe, values)
    # Ablate the heldout atoms via cohort
    cohort = heldout
    W_abl = ablate_cohort_outer_product(W, keys, values, cohort)
    rec_abl = recall_subset(W_abl, keys, probe, values)
    delta = baseline - rec_abl
    assert delta > 0, (
        f"selftest CFU positivity: baseline={baseline} abl={rec_abl} "
        f"delta={delta} should be > 0 (ablation hurts probe recall)"
    )
    return True


def _selftest_composition_differs_from_singles() -> bool:
    """CFU*TRACE composition produces a different prune set than either
    CFU alone or TRACE alone when both axes are non-trivial."""
    n = 60
    rng = np.random.RandomState(42)
    cfu = rng.rand(n) - 0.5    # mix of signs (some "redundant")
    trace = rng.randint(0, 20, size=n).astype(np.float64)
    imp_cfu = importance_cfu_only(cfu)
    imp_trace = importance_trace_only(trace)
    imp_comp = importance_cfu_x_trace(cfu, trace)
    p_cfu = set(select_prune_indices_low(imp_cfu, 20, 0).tolist())
    p_trace = set(select_prune_indices_low(imp_trace, 20, 0).tolist())
    p_comp = set(select_prune_indices_low(imp_comp, 20, 0).tolist())
    assert p_comp != p_cfu, "composition should differ from CFU-alone"
    assert p_comp != p_trace, "composition should differ from TRACE-alone"
    return True


def _selftest_fairness_orthogonality_synthetic() -> bool:
    rng = np.random.RandomState(0)
    importance = rng.rand(200)
    atom_norms = rng.rand(200)
    cor = correlation_E_vs_magnitude(importance, atom_norms)
    assert abs(cor) < 0.30, (
        f"orthogonality: |cor|={abs(cor):.3f} should be < 0.30"
    )
    return True


def _selftest_alpha_regime_is_high() -> bool:
    """v5 must run in v3/v4 high-alpha regime (alpha >= 1.5)."""
    assert ALPHA >= 1.5, (
        f"v5 must run at HIGH-alpha regime; got alpha={ALPHA:.3f} < 1.5. "
        f"N={N}, M_TOTAL={M_TOTAL}."
    )
    return True


def _selftest_cfu_schedule_load_bearing() -> bool:
    assert COHORT_K >= 2, f"COHORT_K must be >= 2; got {COHORT_K}"
    assert N_PROBE_BATCH >= 10, (
        f"N_PROBE_BATCH must be >= 10 for stable CFU; got {N_PROBE_BATCH}"
    )
    assert N_CFU_COHORTS >= 1, (
        f"N_CFU_COHORTS must be >= 1; got {N_CFU_COHORTS}"
    )
    assert M_HELDOUT >= 50, (
        f"M_HELDOUT must be >= 50 for stable held-out recall; "
        f"got {M_HELDOUT}"
    )
    return True


def _instrumentation_selftest():
    _selftest_retrieval_argmax_deterministic()
    _selftest_ablate_cohort_reduces_recall_for_cohort_atoms()
    _selftest_cfu_nonzero_when_ablation_hurts()
    _selftest_composition_differs_from_singles()
    _selftest_fairness_orthogonality_synthetic()
    _selftest_alpha_regime_is_high()
    _selftest_cfu_schedule_load_bearing()
    print(
        f"[selftest] PASS  N={N}  M_OLD={M_OLD}  M_RECENT={M_RECENT}  "
        f"M_HELDOUT={M_HELDOUT}  alpha={ALPHA:.3f}  "
        f"J_comp={N_COMPOSITE_QUERIES}  COHORT_K={COHORT_K}  "
        f"N_PROBE={N_PROBE_BATCH}  N_CFU_COHORTS={N_CFU_COHORTS}  "
        f"arity={COMPOSITE_ARITY}  N_USE={N_USE}  mode={RUN_MODE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner (D3 no-silent-except)
# ---------------------------------------------------------------------------
ARM_NAMES = [
    "ARM_BASELINE_RANDOM_IMPORTANCE",
    "ARM_TRACE_ONLY",
    "ARM_CFU_LEAVE_ONE_OUT",
    "ARM_COMBINED",
]


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(
        f"  [seed={seed}] setup + populate H + wake-trace "
        f"(J={N_COMPOSITE_QUERIES} arity={COMPOSITE_ARITY} N_USE={N_USE}) "
        f"+ score CFU (cohorts={N_CFU_COHORTS} K={COHORT_K} "
        f"probe={N_PROBE_BATCH})...",
        flush=True,
    )
    try:
        t_setup = time.time()
        shared = setup_substrate_with_trace_and_heldout(seed)
        trace_total = float(np.sum(shared[6]))
        n_trace_events = int(shared[8])
        n_edges = shared[3].n_edges()
        print(
            f"  [seed={seed}] setup done in {time.time()-t_setup:.1f}s  "
            f"H_edges={n_edges} trace_total={trace_total:.0f} "
            f"trace_events={n_trace_events}",
            flush=True,
        )

        # Score CFU once per seed (used by ARM_CFU and ARM_COMBINED).
        t_cfu = time.time()
        W_base = shared[0]
        all_keys = shared[1]
        all_values = shared[2]
        heldout_idx = shared[7]
        cfu_importance, n_ablations_evaluated, baseline_heldout_rec = (
            compute_cfu_importance(W_base, all_keys, all_values,
                                   heldout_idx, seed)
        )
        cfu_var = float(np.var(cfu_importance))
        cfu_max_abs = float(np.max(np.abs(cfu_importance)))
        print(
            f"  [seed={seed}] CFU done in {time.time()-t_cfu:.1f}s  "
            f"baseline_heldout_rec={baseline_heldout_rec:.3f}  "
            f"n_ablations={n_ablations_evaluated}  "
            f"cfu_var={cfu_var:.6f}  cfu_max_abs={cfu_max_abs:.4f}",
            flush=True,
        )
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"  [seed={seed}] SETUP_EXCEPTION: {exc}\n{tb}", flush=True)
        return {
            "seed": seed,
            "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
            "M_HELDOUT": M_HELDOUT,
            "alpha": float(ALPHA), "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "exception_phase": "setup_or_cfu",
            "exception_msg": str(exc),
            "exception_traceback": tb,
            "arms": [],
            "elapsed_s": float(time.time() - t0),
        }

    arms = []
    for arm_name in ARM_NAMES:
        try:
            out = run_arm(arm_name, seed, shared=shared,
                          cfu_importance=cfu_importance)
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

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
        "M_HELDOUT": M_HELDOUT,
        "alpha": float(ALPHA), "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(N_QUERIES), "n_use": int(N_USE),
        "downscale_scale": DOWNSCALE_SCALE,
        "n_composite_queries": N_COMPOSITE_QUERIES,
        "cohort_k": int(COHORT_K),
        "n_probe_batch": int(N_PROBE_BATCH),
        "n_cfu_cohorts": int(N_CFU_COHORTS),
        "cfu_eval_frac": float(CFU_EVAL_FRAC),
        "composite_arity": COMPOSITE_ARITY,
        "n_prune_frac": float(N_PRUNE_FRAC),
        "n_edges_H": int(shared[3].n_edges()),
        "trace_total": float(np.sum(shared[6])),
        "n_trace_events": int(shared[8]),
        "baseline_heldout_rec": float(baseline_heldout_rec),
        "n_ablations_evaluated": int(n_ablations_evaluated),
        "cfu_variance": float(cfu_var),
        "cfu_max_abs": float(cfu_max_abs),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    matches = [a for a in arms if a.get("arm_name") == name]
    return matches[0] if matches else {}


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

    # D4 cardinality: 4 arm entries per seed.
    expected_per_seed = len(ARM_NAMES)
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

    # D2 mechanism-fires gate: n_ablations_evaluated > 0 across all seeds
    # AND cfu_variance > 0 (mechanism produced signal).
    for r in results:
        if r.get("n_ablations_evaluated", 0) <= 0:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D2 mechanism inert seed={r['seed']}: "
                    f"n_ablations_evaluated=0 (CFU did not run).")
        if r.get("cfu_variance", 0.0) <= 0.0:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D2 CFU signal flat seed={r['seed']}: "
                    f"cfu_variance=0.0 (no per-atom differentiation).")

    # Aggregate per arm across seeds.
    def _agg(arm_name: str) -> Dict[str, float]:
        per = [_arm_by_name(r["arms"], arm_name) for r in results]
        per = [a for a in per if a]
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

    agg_rand = _agg("ARM_BASELINE_RANDOM_IMPORTANCE")
    agg_trace = _agg("ARM_TRACE_ONLY")
    agg_cfu = _agg("ARM_CFU_LEAVE_ONE_OUT")
    agg_comb = _agg("ARM_COMBINED")

    rand_unretr = agg_rand["mean_rec_UNRETRIEVED"]
    trace_unretr = agg_trace["mean_rec_UNRETRIEVED"]
    cfu_unretr = agg_cfu["mean_rec_UNRETRIEVED"]
    comb_unretr = agg_comb["mean_rec_UNRETRIEVED"]

    sel_trace = rand_unretr - trace_unretr
    sel_cfu = rand_unretr - cfu_unretr
    sel_comb = rand_unretr - comb_unretr

    summary = (
        f"alpha={ALPHA:.3f} "
        f"RAND(retr={agg_rand['mean_rec_RETRIEVED']:.3f},"
        f"unretr={rand_unretr:.3f}); "
        f"TRACE(retr={agg_trace['mean_rec_RETRIEVED']:.3f},"
        f"unretr={trace_unretr:.3f},sel={sel_trace:+.3f}); "
        f"CFU(retr={agg_cfu['mean_rec_RETRIEVED']:.3f},"
        f"unretr={cfu_unretr:.3f},cor={agg_cfu['mean_cor_imp_W']:.3f},"
        f"sel={sel_cfu:+.3f}); "
        f"COMB(retr={agg_comb['mean_rec_RETRIEVED']:.3f},"
        f"unretr={comb_unretr:.3f},cor={agg_comb['mean_cor_imp_W']:.3f},"
        f"sel={sel_comb:+.3f})"
    )

    # Non-finite guards
    for name, a in [("RAND", agg_rand), ("TRACE", agg_trace),
                    ("CFU", agg_cfu), ("COMB", agg_comb)]:
        if not (np.isfinite(a["mean_rec_RETRIEVED"]) and
                np.isfinite(a["mean_rec_UNRETRIEVED"])):
            return ("HARD_FAIL",
                    f"HARD_FAIL: non-finite metrics in {name}. {summary}")

    # D2 mechanism-fires gate on CFU arm
    if agg_cfu["mean_n_downscaled"] <= 0:
        return ("HARD_FAIL",
                f"HARD_FAIL: D2 CFU prune inert (n_downscaled=0). "
                f"{summary}")

    # Fairness gate on CFU arm
    if agg_cfu["mean_cor_imp_W"] >= 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: fairness gate cor(CFU,|W|)="
                f"{agg_cfu['mean_cor_imp_W']:.3f} >= 0.30. {summary}")

    # Saturation gate: all 4 arms within 0.05 on rec_RETRIEVED
    max_retr = max(agg_rand["mean_rec_RETRIEVED"],
                   agg_trace["mean_rec_RETRIEVED"],
                   agg_cfu["mean_rec_RETRIEVED"],
                   agg_comb["mean_rec_RETRIEVED"])
    min_retr = min(agg_rand["mean_rec_RETRIEVED"],
                   agg_trace["mean_rec_RETRIEVED"],
                   agg_cfu["mean_rec_RETRIEVED"],
                   agg_comb["mean_rec_RETRIEVED"])
    if (max_retr - min_retr) < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: arms within 0.05 on rec_RETRIEVED "
                f"(spread={max_retr-min_retr:.3f}). Regime saturated. "
                f"{summary}")

    # ARM_COMBINED must not actively HURT ARM_CFU
    if sel_comb < (sel_cfu - 0.02):
        return ("HARD_FAIL",
                f"HARD_FAIL: COMBINED UNDERPERFORMS CFU by "
                f"{(sel_cfu - sel_comb):+.3f} > 0.02 on sel_unretr. "
                f"{summary}")

    # HARD_PASS bands (all 4 must hold)
    hp_sel_unretr = sel_cfu >= 0.15
    hp_fair = agg_cfu["mean_cor_imp_W"] < 0.30
    hp_fired = (agg_cfu["mean_n_downscaled"] > 0)
    hp_comp_over_cfu = sel_comb >= (sel_cfu + 0.03)

    if all([hp_sel_unretr, hp_fair, hp_fired, hp_comp_over_cfu]):
        return ("HARD_PASS",
                f"HARD_PASS_CFU_BREAKS_SATURATION: alpha={ALPHA:.3f} "
                f"CFU sel_unretr={sel_cfu:+.3f} >= 0.15, cor<0.30, fired, "
                f"COMBINED over CFU={sel_comb - sel_cfu:+.3f} >= 0.03. "
                f"{summary}")

    # MIDDLE_BAND
    mb_fair = agg_cfu["mean_cor_imp_W"] < 0.50
    mb_sel = sel_cfu > 0.0
    if all([mb_fair, mb_sel, hp_fired]):
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: CFU operational but PASS bands not "
                f"cleared. hp_checks=[sel_unretr={hp_sel_unretr},"
                f"fair={hp_fair},fired={hp_fired},"
                f"comp_over_cfu={hp_comp_over_cfu}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: did not clear PASS or MIDDLE. "
            f"hp_checks=[sel_unretr={hp_sel_unretr},"
            f"fair={hp_fair},fired={hp_fired},"
            f"comp_over_cfu={hp_comp_over_cfu}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
              "M_HELDOUT": M_HELDOUT,
              "alpha": float(ALPHA), "J": N_COMPOSITE_QUERIES,
              "run_mode": RUN_MODE,
              "cohort_k": int(COHORT_K),
              "n_cfu_cohorts": int(N_CFU_COHORTS)}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
    f"running {remaining}", flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] v5 N={N} alpha={ALPHA:.3f} "
        f"J_comp={N_COMPOSITE_QUERIES} COHORT_K={COHORT_K} "
        f"N_CFU_COHORTS={N_CFU_COHORTS} N_PROBE={N_PROBE_BATCH} "
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
        f"M_RECENT={M_RECENT} M_HELDOUT={M_HELDOUT} alpha={ALPHA:.3f} "
        f"J_comp={N_COMPOSITE_QUERIES} COHORT_K={COHORT_K} "
        f"N_CFU_COHORTS={N_CFU_COHORTS} N_PROBE={N_PROBE_BATCH} "
        f"arity={COMPOSITE_ARITY} N_USE={N_USE} mode={RUN_MODE} "
        f"N_PRUNE_FRAC={N_PRUNE_FRAC}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT, "M_HELDOUT": M_HELDOUT,
    "alpha": float(ALPHA),
    "n_seeds": len(SEEDS), "n_queries": N_QUERIES, "n_use": int(N_USE),
    "n_composite_queries": N_COMPOSITE_QUERIES,
    "cohort_k": int(COHORT_K),
    "n_probe_batch": int(N_PROBE_BATCH),
    "n_cfu_cohorts": int(N_CFU_COHORTS),
    "cfu_eval_frac": float(CFU_EVAL_FRAC),
    "composite_arity": COMPOSITE_ARITY,
    "downscale_scale": float(DOWNSCALE_SCALE),
    "n_prune_frac": float(N_PRUNE_FRAC),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "trace_total": r.get("trace_total"),
            "n_trace_events": r.get("n_trace_events"),
            "baseline_heldout_rec": r.get("baseline_heldout_rec"),
            "n_ablations_evaluated": r.get("n_ablations_evaluated"),
            "cfu_variance": r.get("cfu_variance"),
            "cfu_max_abs": r.get("cfu_max_abs"),
            "n_edges_H": r.get("n_edges_H"),
            "arms": r.get("arms"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
