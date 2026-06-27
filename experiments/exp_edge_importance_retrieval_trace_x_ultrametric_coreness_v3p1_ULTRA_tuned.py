"""edge_importance_retrieval_trace_x_ultrametric_coreness_v3.1 ULTRA-tuned.

CLONE of v3 with ULTRA_COS 0.85 -> 0.70 and ULTRA_MIN_SIZE 5 -> 3.

Pre-reg: preregs/2026-06-27_edge_importance_retrieval_trace_x_ultrametric_coreness_v3p1_ULTRA_tuned.md

Why v3.1 exists (drill 2026-06-27 ANGLE 3 finding):
  v3 ULTRA arm collapsed to ZERO coreness atoms across all 3 seeds
  (importance_max = 0.0; importance_mean = 0.0). At N=512 with
  ULTRA_COS=0.85 the threshold was too strict; no atoms qualified as
  cluster-resident. Therefore the COMPOSITION arm reduced to TRACE-only:
    importance = trace * (1 + lam * 0) = trace
  v3 verdict was "TRACE-only @ +0.083" not "composition @ +0.083"; the
  composition was not actually tested.

v3.1 patches ONLY:
  ULTRA_COS:        0.85 -> 0.70   (looser cosine cluster threshold)
  ULTRA_MIN_SIZE:   5    -> 3      (smaller qualifying clusters allowed)

Plus a NEW META_RULE_K (discriminator-fires) assertion at smoke time:
  setup_substrate_with_trace_and_clusters() must produce
  coreness_atoms > 0; HARD_FAIL on cardinality breach.

Predicted (from drill): ULTRA at 0.70 threshold produces 5-15 coreness
atoms per seed; composition gains +0.02-0.04 over TRACE-only. This is
small but unblocks the honest composition reading.

ALL OTHER PARAMS UNCHANGED FROM v3:
  N=512, M_OLD=600, M_RECENT=400, alpha=1.953
  J_composite=3000, arity=3, USE_FRAC=0.40, N_USE=240
  DOWNSCALE_SCALE=0.20, N_PRUNE_FRAC=0.30
  SEEDS=[7, 17, 23], N_QUERIES=200
  LAMBDA_LIST=[0.1, 0.3, 0.5]

PRE-REG BANDS: identical to v3 (sel_unretr asymmetry >= 0.15 for HARD_PASS;
composition value-add >= 0.03 over TRACE_ONLY).

DISCIPLINES:
  D1 -- Discriminator-must-survive-scale (v3): smoke at FULL-N.
  D2 -- Smoke-must-FIRE-discriminator: n_downscaled > 0 AND H_edges >= 50.
  D3 -- No-silent-except: setup + each arm wrapped.
  D4 -- cardinality_ok: SEEDS x (3 single + 3 composition) per seed.
  NEW: META_RULE_K coreness-fires: coreness_atoms > 0 in EVERY seed
       (else ULTRA arm is degenerate again; HARD_FAIL).

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
from hdlab.ultrametric_clustering import (
    UltrametricConfig,
    cosine_distance_matrix,
    cluster_atom_lookup,
    filter_qualifying_clusters,
    single_linkage_clusters,
)


ANCHOR_NAME = "edge_importance_retrieval_trace_x_ultrametric_coreness_v3p1_ULTRA_tuned"
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

# Inherit v3 high-alpha regime; only ULTRA_COS + ULTRA_MIN_SIZE changed.
N_FULL = 512
M_OLD_FULL = 600
M_RECENT_FULL = 400
N_COMPOSITE_QUERIES_FULL = 3000
COMPOSITE_ARITY = 3
USE_FRAC_FULL = 0.40
DOWNSCALE_SCALE = 0.20
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200
LAMBDA_LIST = [0.1, 0.3, 0.5]

# v3.1 PATCH: ULTRA_COS 0.85 -> 0.70; ULTRA_MIN_SIZE 5 -> 3 (drill 2026-06-27
# ANGLE 3 finding -- v3 had ULTRA arm collapse to zero; v3.1 looser thresholds
# allow non-zero coreness at N=512).
ULTRAMETRIC_COSINE_THRESH = 0.70
ULTRAMETRIC_MIN_CLUSTER_SIZE = 3

# Smoke discipline (D1): smoke runs at FULL-N parameters; only J / seeds /
# N_QUERIES reduced.
if RUN_MODE == "smoke":
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    N_COMPOSITE_QUERIES = 1500
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

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M_OLD={M_OLD},M_RECENT={M_RECENT},"
    f"alpha={ALPHA:.3f},J_composite={N_COMPOSITE_QUERIES},"
    f"arity={COMPOSITE_ARITY},USE_FRAC={USE_FRAC},"
    f"DOWNSCALE_SCALE={DOWNSCALE_SCALE},LAMBDA_LIST={LAMBDA_LIST},"
    f"ULTRA_COS={ULTRAMETRIC_COSINE_THRESH},"
    f"ULTRA_MIN_SIZE={ULTRAMETRIC_MIN_CLUSTER_SIZE},"
    f"N_PRUNE_FRAC={N_PRUNE_FRAC},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"N_QUERIES={N_QUERIES},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Pattern generation (mirrors v3 conventions exactly)
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


def setup_substrate_with_trace_and_clusters(
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, EdgeImportance,
           np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    keys_old, values_old = generate_pairs(M_OLD, N, seed)
    keys_rec, values_rec = generate_pairs(M_RECENT, N, seed + 999)
    all_keys = np.concatenate([keys_old, keys_rec], axis=0)
    all_values = np.concatenate([values_old, values_rec], axis=0)

    cfg = HConfig(
        increment=1.0, decay_step=0.0, floor=0.0,
        e_thresh=2.0, h_thresh=3.0,
    )
    edge_graph = EdgeImportance(n_atoms=M_TOTAL, cfg=cfg)

    W = build_W_from_pairs(keys_old, values_old)

    rng = np.random.RandomState(seed + 401)
    retrieved_idx = rng.choice(M_OLD, size=N_USE, replace=False)
    retrieved_idx.sort()
    unretrieved_mask = np.ones(M_OLD, dtype=bool)
    unretrieved_mask[retrieved_idx] = False
    unretrieved_idx = np.where(unretrieved_mask)[0]

    retrieval_trace_score = np.zeros(M_TOTAL, dtype=np.float64)

    rng_q = np.random.RandomState(seed + 1117)
    for _q in range(N_COMPOSITE_QUERIES):
        triple = rng_q.choice(retrieved_idx, size=COMPOSITE_ARITY,
                              replace=False)
        bundled_key = composite_query_bundle(all_keys, triple)
        pred = predict(W, bundled_key)
        winner = cleanup_argmax(all_values, pred, N)
        retrieval_trace_score[winner] += 1.0
        edge_graph.increment_query(triple)
        edge_graph.decay_all()

    W = W + build_W_from_pairs(keys_rec, values_rec)

    # v3.1 PATCH: looser cluster threshold (0.70) + smaller min_size (3)
    ultra_cfg = UltrametricConfig(
        cosine_thresh=ULTRAMETRIC_COSINE_THRESH,
        min_cluster_size=ULTRAMETRIC_MIN_CLUSTER_SIZE,
    )
    D = cosine_distance_matrix(all_keys)
    max_dist = 1.0 - ULTRAMETRIC_COSINE_THRESH
    raw_clusters = single_linkage_clusters(D, max_distance=max_dist)
    qual_clusters = filter_qualifying_clusters(raw_clusters, all_keys,
                                               ultra_cfg)
    cluster_lookup = cluster_atom_lookup(qual_clusters, M_TOTAL)
    ultrametric_coreness = (cluster_lookup >= 0).astype(np.float64)

    return (W, all_keys, all_values, edge_graph, retrieved_idx,
            unretrieved_idx, retrieval_trace_score, ultrametric_coreness)


# ---------------------------------------------------------------------------
# Importance scoring per arm (identical to v3)
# ---------------------------------------------------------------------------
def importance_random(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 7777)
    return rng.rand(M_TOTAL)


def importance_trace_only(retrieval_trace_score: np.ndarray) -> np.ndarray:
    return retrieval_trace_score.copy()


def importance_ultrametric_only(
    ultrametric_coreness: np.ndarray,
) -> np.ndarray:
    return ultrametric_coreness.copy()


def importance_trace_x_coreness(
    retrieval_trace_score: np.ndarray,
    ultrametric_coreness: np.ndarray,
    lam: float,
) -> np.ndarray:
    return retrieval_trace_score * (1.0 + lam * ultrametric_coreness)


def select_prune_indices_low(importance: np.ndarray,
                             n_prune: int,
                             seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 13131)
    jitter = rng.rand(importance.shape[0]) * 1e-6
    score = importance + jitter
    return np.argsort(score)[:n_prune]


# ---------------------------------------------------------------------------
# Arm runner (identical to v3)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            shared: Tuple,
            lam: float = 0.3) -> Dict:
    t0 = time.time()
    (W_base, all_keys, all_values, edge_graph,
     retrieved_idx, unretrieved_idx,
     retrieval_trace_score, ultrametric_coreness) = shared

    W = W_base.copy()
    W_norm_pre = float(np.linalg.norm(W))

    if arm_name == "ARM_BASELINE_RANDOM_IMPORTANCE":
        importance = importance_random(seed)
    elif arm_name == "ARM_TRACE_ONLY":
        importance = importance_trace_only(retrieval_trace_score)
    elif arm_name == "ARM_ULTRAMETRIC_ONLY":
        importance = importance_ultrametric_only(ultrametric_coreness)
    elif arm_name == "ARM_TRACE_X_CORENESS":
        importance = importance_trace_x_coreness(
            retrieval_trace_score, ultrametric_coreness, lam,
        )
    else:
        raise ValueError(f"unknown arm {arm_name}")

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
        "lambda": float(lam) if arm_name == "ARM_TRACE_X_CORENESS" else None,
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


def _selftest_ultrametric_coreness_at_v3p1_thresholds() -> bool:
    """v3.1 thresholds (cos=0.70, min=3) must FIRE on a synthetic 3-atom
    cluster + 2 isolated atoms."""
    rng = np.random.RandomState(0)
    dim = 256
    cfg = UltrametricConfig(
        cosine_thresh=ULTRAMETRIC_COSINE_THRESH,
        min_cluster_size=ULTRAMETRIC_MIN_CLUSTER_SIZE,
    )
    # 4 atoms in a tight cluster + 2 isolated; threshold 0.70 must fire.
    # Empirical (rng.seed=0, dim=256): sigma=0.10 gives pairwise cos ~0.31 (too
    # loose); sigma=0.04 gives 0.70-0.72 (boundary; some pairs dip below);
    # sigma=0.02 gives 0.91+ (clean qualification). Use 0.02 to give the
    # filter genuine margin above 0.70 threshold.
    base = rng.randn(dim)
    base /= np.linalg.norm(base)
    cluster = [base + 0.02 * rng.randn(dim) for _ in range(4)]
    cluster = [a / np.linalg.norm(a) for a in cluster]
    iso = [rng.randn(dim) for _ in range(2)]
    iso = [a / np.linalg.norm(a) for a in iso]
    W = np.array(cluster + iso)
    D = cosine_distance_matrix(W)
    raw = single_linkage_clusters(D, max_distance=1.0 - ULTRAMETRIC_COSINE_THRESH)
    qual = filter_qualifying_clusters(raw, W, cfg)
    lookup = cluster_atom_lookup(qual, W.shape[0])
    coreness = (lookup >= 0).astype(np.float64)
    assert np.sum(coreness[:4]) >= 3, (
        f"v3.1 selftest: at cos=0.70/min=3 expected >=3 of 4 cluster atoms "
        f"to qualify; got coreness[:4]={coreness[:4]}"
    )
    return True


def _selftest_v3p1_thresholds_correct() -> bool:
    """v3.1 must use loosened thresholds (0.70/3) vs v3 (0.85/5)."""
    assert ULTRAMETRIC_COSINE_THRESH == 0.70, (
        f"v3.1 must use ULTRA_COS=0.70 (drill ANGLE 3); got "
        f"{ULTRAMETRIC_COSINE_THRESH}"
    )
    assert ULTRAMETRIC_MIN_CLUSTER_SIZE == 3, (
        f"v3.1 must use ULTRA_MIN_SIZE=3 (drill ANGLE 3); got "
        f"{ULTRAMETRIC_MIN_CLUSTER_SIZE}"
    )
    return True


def _selftest_composition_orthogonal_to_random_baseline() -> bool:
    n = 100
    rng = np.random.RandomState(42)
    trace = np.zeros(n)
    trace[:30] = rng.randint(1, 20, size=30).astype(np.float64)
    coreness = np.zeros(n)
    coreness[:15] = 1.0
    importance_comp = trace * (1.0 + 0.3 * coreness)
    importance_rand = rng.rand(n)
    prune_comp = select_prune_indices_low(importance_comp, 30, 0)
    prune_rand = select_prune_indices_low(importance_rand, 30, 0)
    assert set(prune_comp.tolist()) != set(prune_rand.tolist()), (
        "selftest composition: expected different prune set vs random"
    )
    n_zero_traced_pruned = int(np.sum(prune_comp >= 30))
    assert n_zero_traced_pruned >= 25, (
        f"selftest composition: expected >= 25 of 30 pruned to be "
        f"zero-traced atoms; got {n_zero_traced_pruned}"
    )
    return True


def _selftest_fairness_orthogonality_synthetic() -> bool:
    rng = np.random.RandomState(0)
    importance = rng.rand(200)
    atom_norms = rng.rand(200)
    cor = correlation_E_vs_magnitude(importance, atom_norms)
    assert abs(cor) < 0.30, (
        f"selftest orthogonality: |cor|={abs(cor):.3f} should be < 0.30"
    )
    return True


def _selftest_alpha_regime_is_high() -> bool:
    assert ALPHA >= 1.5, (
        f"v3.1 must run at HIGH-alpha regime; got alpha={ALPHA:.3f} < 1.5. "
        f"N={N}, M_TOTAL={M_TOTAL}."
    )
    return True


def _selftest_lambda_modulator_effect() -> bool:
    trace = np.array([1.0, 1.0, 1.0])
    coreness = np.array([1.0, 0.0, 1.0])
    imp_l0 = trace * (1.0 + 0.0 * coreness)
    imp_l05 = trace * (1.0 + 0.5 * coreness)
    assert np.allclose(imp_l0, trace), f"lambda=0: {imp_l0} should = trace"
    assert imp_l05[0] == 1.5 and imp_l05[1] == 1.0 and imp_l05[2] == 1.5, (
        f"lambda=0.5: expected [1.5, 1.0, 1.5]; got {imp_l05}"
    )
    return True


def _instrumentation_selftest():
    _selftest_v3p1_thresholds_correct()
    _selftest_retrieval_trace_increments_on_argmax()
    _selftest_ultrametric_coreness_at_v3p1_thresholds()
    _selftest_composition_orthogonal_to_random_baseline()
    _selftest_fairness_orthogonality_synthetic()
    _selftest_alpha_regime_is_high()
    _selftest_lambda_modulator_effect()
    print(
        f"[selftest] PASS  N={N}  M_OLD={M_OLD}  M_RECENT={M_RECENT}  "
        f"alpha={ALPHA:.3f}  J_comp={N_COMPOSITE_QUERIES}  "
        f"arity={COMPOSITE_ARITY}  N_USE={N_USE}  mode={RUN_MODE} "
        f"LAMBDA_LIST={LAMBDA_LIST} "
        f"ULTRA_COS={ULTRAMETRIC_COSINE_THRESH} "
        f"ULTRA_MIN_SIZE={ULTRAMETRIC_MIN_CLUSTER_SIZE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner (D3 no-silent-except; v3.1 adds META_RULE_K coreness-fires)
# ---------------------------------------------------------------------------
ARM_NAMES = [
    "ARM_BASELINE_RANDOM_IMPORTANCE",
    "ARM_TRACE_ONLY",
    "ARM_ULTRAMETRIC_ONLY",
    "ARM_TRACE_X_CORENESS",
]


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(
        f"  [seed={seed}] setup + populate H + trace + ultrametric "
        f"(J_comp={N_COMPOSITE_QUERIES}, arity={COMPOSITE_ARITY}, "
        f"N_USE={N_USE} of M_OLD={M_OLD}, ULTRA_COS={ULTRAMETRIC_COSINE_THRESH}, "
        f"ULTRA_MIN_SIZE={ULTRAMETRIC_MIN_CLUSTER_SIZE})...",
        flush=True,
    )
    try:
        t_setup = time.time()
        shared = setup_substrate_with_trace_and_clusters(seed)
        trace_total = float(np.sum(shared[6]))
        coreness_count = int(np.sum(shared[7]))
        n_edges = shared[3].n_edges()
        print(
            f"  [seed={seed}] setup done in {time.time()-t_setup:.1f}s  "
            f"H_edges={n_edges} trace_total={trace_total:.0f} "
            f"coreness_atoms={coreness_count}",
            flush=True,
        )
        # NEW META_RULE_K coreness-fires assertion: v3.1's whole point is
        # that ULTRA arm produces non-zero variance; if coreness=0 at any
        # seed, v3.1 is degenerate same as v3 was. HARD_FAIL at this gate.
        if coreness_count <= 0:
            raise RuntimeError(
                f"META_RULE_K coreness-fires FAIL: coreness_atoms="
                f"{coreness_count} at seed={seed} with ULTRA_COS="
                f"{ULTRAMETRIC_COSINE_THRESH}, ULTRA_MIN_SIZE="
                f"{ULTRAMETRIC_MIN_CLUSTER_SIZE}. v3.1 cell is DEGENERATE "
                f"at these thresholds -- composition would silently reduce "
                f"to TRACE-only. Tune thresholds looser OR raise N. v3 had "
                f"the same issue at (0.85, 5); v3.1 must NOT repeat it."
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

    for lam in LAMBDA_LIST:
        arm_name = "ARM_TRACE_X_CORENESS"
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
        "composite_arity": COMPOSITE_ARITY,
        "n_prune_frac": float(N_PRUNE_FRAC),
        "lambda_list": list(LAMBDA_LIST),
        "ultrametric_cosine_thresh": float(ULTRAMETRIC_COSINE_THRESH),
        "ultrametric_min_cluster_size": int(ULTRAMETRIC_MIN_CLUSTER_SIZE),
        "n_edges_H": int(shared[3].n_edges()),
        "trace_total": float(np.sum(shared[6])),
        "coreness_atoms": int(np.sum(shared[7])),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (identical to v3 + an early-fail on META_RULE_K coreness)
# ---------------------------------------------------------------------------
def _arms_by_name(arms: List[Dict], name: str) -> List[Dict]:
    return [a for a in arms if a.get("arm_name") == name]


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

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

    # NEW v3.1 gate: every seed must have coreness_atoms > 0 (META_RULE_K).
    for r in results:
        if r.get("coreness_atoms", 0) <= 0:
            return ("HARD_FAIL",
                    f"HARD_FAIL: META_RULE_K coreness-fires breach "
                    f"seed={r['seed']}: coreness_atoms="
                    f"{r.get('coreness_atoms')}. v3.1 thresholds "
                    f"({ULTRAMETRIC_COSINE_THRESH}, "
                    f"{ULTRAMETRIC_MIN_CLUSTER_SIZE}) still degenerate.")

    expected_per_seed = len(ARM_NAMES) - 1 + len(LAMBDA_LIST)
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
            for a in _arms_by_name(r["arms"], "ARM_TRACE_X_CORENESS"):
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

    agg_rand = _agg_single("ARM_BASELINE_RANDOM_IMPORTANCE")
    agg_trace = _agg_single("ARM_TRACE_ONLY")
    agg_ultra = _agg_single("ARM_ULTRAMETRIC_ONLY")
    agg_comp_per_lam = {lam: _agg_composition(lam) for lam in LAMBDA_LIST}

    rand_unretr = agg_rand.get("mean_rec_UNRETRIEVED", 0.0)
    trace_unretr = agg_trace.get("mean_rec_UNRETRIEVED", 0.0)
    ultra_unretr = agg_ultra.get("mean_rec_UNRETRIEVED", 0.0)

    sel_trace_minus_rand = rand_unretr - trace_unretr
    sel_ultra_minus_rand = rand_unretr - ultra_unretr

    best_lam = LAMBDA_LIST[0]
    best_sel_unretr = -1.0
    for lam in LAMBDA_LIST:
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
        f"ULTRA_COS={ULTRAMETRIC_COSINE_THRESH} "
        f"ULTRA_MIN_SIZE={ULTRAMETRIC_MIN_CLUSTER_SIZE} "
        f"RAND(retr={agg_rand['mean_rec_RETRIEVED']:.3f},"
        f"unretr={agg_rand['mean_rec_UNRETRIEVED']:.3f}); "
        f"TRACE(retr={agg_trace['mean_rec_RETRIEVED']:.3f},"
        f"unretr={agg_trace['mean_rec_UNRETRIEVED']:.3f},"
        f"sel_minus_rand={sel_trace_minus_rand:+.3f}); "
        f"ULTRA(retr={agg_ultra['mean_rec_RETRIEVED']:.3f},"
        f"unretr={agg_ultra['mean_rec_UNRETRIEVED']:.3f},"
        f"sel_minus_rand={sel_ultra_minus_rand:+.3f}); "
        f"COMP(retr={best_comp['mean_rec_RETRIEVED']:.3f},"
        f"unretr={best_comp['mean_rec_UNRETRIEVED']:.3f},"
        f"cor={best_comp['mean_cor_imp_W']:.3f},"
        f"cv={best_comp['cv_rec_RETRIEVED']:.3f},"
        f"n_down={best_comp['mean_n_downscaled']:.0f},"
        f"sel_minus_rand={best_sel_unretr:+.3f})"
    )

    for name, a in [("RAND", agg_rand), ("TRACE", agg_trace),
                    ("ULTRA", agg_ultra), ("COMP", best_comp)]:
        if not (np.isfinite(a.get("mean_rec_RETRIEVED", float("nan"))) and
                np.isfinite(a.get("mean_rec_UNRETRIEVED", float("nan")))):
            return ("HARD_FAIL",
                    f"HARD_FAIL: non-finite metrics in {name}. {summary}")

    if best_comp.get("mean_n_downscaled", 0) <= 0:
        return ("HARD_FAIL",
                f"HARD_FAIL: D2 COMPOSITION mechanism inert "
                f"(n_downscaled=0). {summary}")

    if best_comp.get("mean_cor_imp_W", 1.0) >= 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: fairness gate cor(importance,|W|)="
                f"{best_comp['mean_cor_imp_W']:.3f} >= 0.30. {summary}")

    max_retr = max(agg_rand["mean_rec_RETRIEVED"],
                   agg_trace["mean_rec_RETRIEVED"],
                   agg_ultra["mean_rec_RETRIEVED"],
                   best_comp["mean_rec_RETRIEVED"])
    min_retr = min(agg_rand["mean_rec_RETRIEVED"],
                   agg_trace["mean_rec_RETRIEVED"],
                   agg_ultra["mean_rec_RETRIEVED"],
                   best_comp["mean_rec_RETRIEVED"])
    if (max_retr - min_retr) < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: arms within 0.05 on rec_RETRIEVED "
                f"(spread={max_retr-min_retr:.3f}). Regime saturated. "
                f"{summary}")

    if best_sel_unretr < (sel_trace_minus_rand - 0.02):
        return ("HARD_FAIL",
                f"HARD_FAIL: composition UNDERPERFORMS trace_only by "
                f"{(sel_trace_minus_rand - best_sel_unretr):.3f} > 0.02 "
                f"on sel_unretr. {summary}")

    hp_sel_unretr = best_sel_unretr >= 0.15
    hp_rec_retr = best_comp["mean_rec_RETRIEVED"] >= 0.80
    hp_fair = best_comp["mean_cor_imp_W"] < 0.30
    hp_fired = best_comp.get("mean_n_downscaled", 0) > 0
    hp_comp_over_trace = best_sel_unretr >= (sel_trace_minus_rand + 0.03)
    hp_comp_over_ultra = best_sel_unretr >= (sel_ultra_minus_rand + 0.03)

    if all([hp_sel_unretr, hp_rec_retr, hp_fair, hp_fired,
            hp_comp_over_trace, hp_comp_over_ultra]):
        return ("HARD_PASS",
                f"HARD_PASS: at alpha={ALPHA:.3f} COMPOSITION(lam={best_lam}) "
                f"sel_unretr={best_sel_unretr:.3f} >= 0.15, "
                f"rec_RETR>=0.80, cor<0.30, fired, "
                f"composition over_trace="
                f"{best_sel_unretr - sel_trace_minus_rand:+.3f}, "
                f"over_ultra="
                f"{best_sel_unretr - sel_ultra_minus_rand:+.3f}. "
                f"{summary}")

    mb_fair = best_comp["mean_cor_imp_W"] < 0.50
    mb_rec_retr = best_comp["mean_rec_RETRIEVED"] >= 0.60
    mb_sel = best_sel_unretr > 0.0
    if all([mb_fair, mb_rec_retr, mb_sel, hp_fired]):
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: composition operational but PASS bands not "
                f"cleared. hp_checks=[sel_unretr={hp_sel_unretr},"
                f"rec_retr={hp_rec_retr},fair={hp_fair},fired={hp_fired},"
                f"over_trace={hp_comp_over_trace},"
                f"over_ultra={hp_comp_over_ultra}]. "
                f"{summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: did not clear PASS or MIDDLE. "
            f"hp_checks=[sel_unretr={hp_sel_unretr},rec_retr={hp_rec_retr},"
            f"fair={hp_fair},fired={hp_fired},"
            f"over_trace={hp_comp_over_trace},over_ultra={hp_comp_over_ultra}]. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
              "alpha": float(ALPHA), "J": N_COMPOSITE_QUERIES,
              "run_mode": RUN_MODE,
              "lambda_list": list(LAMBDA_LIST),
              "ultra_cos": float(ULTRAMETRIC_COSINE_THRESH),
              "ultra_min_size": int(ULTRAMETRIC_MIN_CLUSTER_SIZE)}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
    f"running {remaining}", flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] v3.1 N={N} alpha={ALPHA:.3f} "
        f"J_comp={N_COMPOSITE_QUERIES} arity={COMPOSITE_ARITY} "
        f"N_USE={N_USE} mode={RUN_MODE} "
        f"ULTRA_COS={ULTRAMETRIC_COSINE_THRESH} "
        f"ULTRA_MIN_SIZE={ULTRAMETRIC_MIN_CLUSTER_SIZE}...",
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
        f"J_comp={N_COMPOSITE_QUERIES} arity={COMPOSITE_ARITY} "
        f"N_USE={N_USE} mode={RUN_MODE} "
        f"LAMBDA={LAMBDA_LIST} N_PRUNE_FRAC={N_PRUNE_FRAC} "
        f"ULTRA_COS={ULTRAMETRIC_COSINE_THRESH} "
        f"ULTRA_MIN_SIZE={ULTRAMETRIC_MIN_CLUSTER_SIZE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
    "alpha": float(ALPHA),
    "n_seeds": len(SEEDS), "n_queries": N_QUERIES, "n_use": int(N_USE),
    "n_composite_queries": N_COMPOSITE_QUERIES,
    "composite_arity": COMPOSITE_ARITY,
    "downscale_scale": float(DOWNSCALE_SCALE),
    "lambda_list": list(LAMBDA_LIST),
    "n_prune_frac": float(N_PRUNE_FRAC),
    "ultrametric_cosine_thresh": float(ULTRAMETRIC_COSINE_THRESH),
    "ultrametric_min_cluster_size": int(ULTRAMETRIC_MIN_CLUSTER_SIZE),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "trace_total": r.get("trace_total"),
            "coreness_atoms": r.get("coreness_atoms"),
            "n_edges_H": r.get("n_edges_H"),
            "arms": r.get("arms"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
