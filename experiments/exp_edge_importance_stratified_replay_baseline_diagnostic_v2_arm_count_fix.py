"""edge_importance stratified-replay baseline diagnostic v2 (arm-count fix).

USER 2026-06-27 NO LOCAL + GPU+CPU idle. exp_dev cell-author 2026-06-27.

v2 FIX (root cause): v1 imported setup_substrate_with_trace_and_clusters
from exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3, but
v3 has an UNGUARDED top-level main driver. The import ran the v3 driver,
which called get_output_dir(v3_anchor); because the runner sets
HDLAB_EXP_NAME=v1_anchor, get_output_dir resolved to v1's dir and v3 wrote
its 6-arm partials (ARM_BASELINE_RANDOM_IMPORTANCE / ARM_TRACE_ONLY /
ARM_ULTRAMETRIC_ONLY / 3x ARM_TRACE_X_CORENESS) into v1's out_dir. v1's
aggregator then loaded the foreign partials, breaching META_RULE_H
cardinality_ok (got 6 expected 4).

v2 inlines the substrate-setup function + its 7 helpers (~120 lines)
verbatim from v3, eliminating the v3-module import entirely. ARM_NAMES
remains 4 (same as v1; per stub 3). Pre-reg bands unchanged.

Pre-reg: preregs/2026-06-27_edge_importance_stratified_replay_baseline_diagnostic_v2.md

Drill provenance:
  notes/research_drill_v4_nrem_replay_fairness_violation_3x_2026-06-27.md
  Section "3 actionable cell stubs" stub 3 -- cheap verify-the-referent on
  the fairness-math conjecture. Drill ANGLE 1 hypothesis: Cauchy-Schwarz
  says any sampling-count signal over substrate retrieval correlates with
  |W|; stratified sampling by |W|-quantile should BREAK that correlation if
  the hypothesis holds.

Mechanism (THE diagnostic):
  STRATIFIED_REPLAY -- bin atoms by |W|-decile (10 bins); sample equal
                       replay-count per bin; importance = stratified-count.
                       If cor(importance, |W|) drops below ~0.30 (vs v4
                       trace/replay cor of 0.83/0.98), the math is right
                       and fairness violation is a sampling-bias artifact.

ARMS (4 mandatory; per stub 3):
  ARM_RAND_IMPORTANCE        -- random importance baseline (control rail)
  ARM_TRACE_ONLY             -- v3.2 lineage; raw retrieval_trace_count
                                (reproduce drill's cor=0.83 claim)
  ARM_STRATIFIED_REPLAY      -- THE diagnostic; bin by |W|-decile, count
                                replays per bin, importance = bin-uniform
  ARM_INVERSE_WEIGHTED_REPLAY -- Liu IS: count / ||a||^2

PRE-REG BANDS (LOCKED):
  DIAGNOSTIC_PASS_A: cor(STRATIFIED_REPLAY, |W|) < 0.30
                     (proves math holds; fairness is sampling artifact)
  DIAGNOSTIC_PASS_B: cor(INVERSE_WEIGHTED, |W|) < 0.30
                     (Liu IS correction also valid in HD substrate)
  REPRODUCE_V4_TRACE_BIAS: cor(TRACE_ONLY, |W|) >= 0.70
                          (confirms drill's measurement; SC predicts >=0.7)

  HARD_PASS: EITHER DIAGNOSTIC_PASS_A OR DIAGNOSTIC_PASS_B holds AND
             REPRODUCE_V4_TRACE_BIAS holds AND mechanism fires.
  MIDDLE_BAND: TRACE bias reproduced but neither STRATIFIED nor INVERSE
               clears the 0.30 gate; partial diagnostic value.
  HARD_FAIL: TRACE_ONLY cor < 0.30 (drill claim contradicted; surprise
             negative -- means the math is wrong OR test rigging wrong)
             OR cardinality breach OR caught exception.

DISCIPLINES:
  META_RULE_H cardinality_ok: per-seed expected arm count = 4.
  META_RULE_J no-silent-except: setup + each arm wrapped.
  META_RULE_K smoke fires discriminator: smoke must reproduce TRACE-bias
    (cor >= 0.5 at smoke; full-N predicted >= 0.7).
  META_RULE_L band-floor strictly-above-floor.

PROT-020: numpy-only; routes to remote_cpu_queue.
ASCII-only. No emojis. No em-dashes.
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

from experiments._seed_checkpoint import (  # noqa: E402
    aggregate_partials, get_output_dir, resumable_seeds, write_partial,
)
from hdlab.edge_importance import (  # noqa: E402
    EdgeImportance, HConfig, correlation_E_vs_magnitude,
)
from hdlab.ultrametric_clustering import (  # noqa: E402
    UltrametricConfig,
    cosine_distance_matrix,
    cluster_atom_lookup,
    filter_qualifying_clusters,
    single_linkage_clusters,
)


ANCHOR_NAME = "edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# Inherit v3.2 / v4 regime (alpha=1.953 high-alpha; discriminator scales).
N_FULL = 512
M_OLD_FULL = 600
M_RECENT_FULL = 400
SEEDS_FULL = [7, 17, 23]

# v3 substrate-setup constants (copied verbatim; required by inlined setup):
N_COMPOSITE_QUERIES_FULL = 3000
COMPOSITE_ARITY = 3
USE_FRAC_FULL = 0.40
ULTRAMETRIC_COSINE_THRESH = 0.85
ULTRAMETRIC_MIN_CLUSTER_SIZE = 5

# Smoke discipline per META_RULE_K + USER 2026-06-26 D1: smoke at FULL-N.
# Only SEEDS reduced.
if RUN_MODE == "smoke":
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    N_COMPOSITE_QUERIES = 1500   # half J cycles (matches v3 smoke pattern)
    USE_FRAC = USE_FRAC_FULL
    SEEDS = [7]
else:
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    N_COMPOSITE_QUERIES = N_COMPOSITE_QUERIES_FULL
    USE_FRAC = USE_FRAC_FULL
    SEEDS = SEEDS_FULL

M_TOTAL = M_OLD + M_RECENT
ALPHA = M_TOTAL / N
N_USE = max(COMPOSITE_ARITY, int(round(USE_FRAC * M_OLD)))
N_BINS_STRATIFIED = 10
# Replay budget: replay K_PER_BIN atoms PER bin (so STRATIFIED has uniform
# coverage across |W|-deciles; total replays = K_PER_BIN * N_BINS_STRATIFIED).
# Default 8 per bin * 10 bins = 80 replay events total per arm.
K_PER_BIN = 8
TOTAL_REPLAY_EVENTS = K_PER_BIN * N_BINS_STRATIFIED

# Pre-reg constants (LOCKED)
DIAGNOSTIC_COR_GATE = 0.30
REPRODUCE_TRACE_BIAS_FLOOR_FULL = 0.70
REPRODUCE_TRACE_BIAS_FLOOR_SMOKE = 0.50

ARM_NAMES = [
    "ARM_RAND_IMPORTANCE",
    "ARM_TRACE_ONLY",
    "ARM_STRATIFIED_REPLAY",
    "ARM_INVERSE_WEIGHTED_REPLAY",
]

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M_OLD={M_OLD},M_RECENT={M_RECENT},"
    f"alpha={ALPHA:.3f},N_BINS={N_BINS_STRATIFIED},"
    f"K_PER_BIN={K_PER_BIN},TOTAL_REPLAY_EVENTS={TOTAL_REPLAY_EVENTS},"
    f"J_composite={N_COMPOSITE_QUERIES},arity={COMPOSITE_ARITY},"
    f"USE_FRAC={USE_FRAC},N_USE={N_USE},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Substrate-setup helpers (inlined from
# experiments/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py
# lines 212-341, VERBATIM minus docstring trims, to avoid v3's unguarded
# module-level main driver running on import and writing foreign partials
# into v2's out_dir).
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
    """Build W + populate edge graph + populate retrieval_trace_score +
    compute ultrametric clusters. INLINED from v3 to avoid import-time
    driver (see module docstring root-cause note).
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
# Arm-importance computations (purely from shared substrate state)
# ---------------------------------------------------------------------------
def importance_random(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 7777)
    return rng.rand(M_TOTAL)


def importance_trace_only(retrieval_trace_score: np.ndarray) -> np.ndarray:
    """v3.2 lineage: raw cleanup-argmax counter."""
    return retrieval_trace_score.copy()


def _atom_norms_from_substrate(all_keys: np.ndarray, W: np.ndarray) -> np.ndarray:
    """Compute per-atom |W| equivalent norm (matches v3/v4 fairness metric)."""
    return np.linalg.norm(all_keys @ W.T, axis=1) / float(N)


def importance_stratified_replay(
    atom_norms: np.ndarray,
    retrieval_trace_score: np.ndarray,
    seed: int,
    n_bins: int = N_BINS_STRATIFIED,
    k_per_bin: int = K_PER_BIN,
) -> np.ndarray:
    """Bin atoms by |W|-decile; sample k_per_bin atoms per bin proportional
    to within-bin retrieval_trace_score; importance = replay-event count.

    Per drill ANGLE 1: if math holds, this distribution is uniform within
    bins so cor(importance, |W|) approaches 0.
    """
    rng = np.random.RandomState(seed + 22227)
    quantiles = np.quantile(atom_norms, np.linspace(0, 1, n_bins + 1))
    quantiles[-1] = quantiles[-1] + 1e-9
    bins = np.digitize(atom_norms, quantiles[1:-1])
    importance = np.zeros(M_TOTAL, dtype=np.float64)
    for b in range(n_bins):
        bin_atom_idx = np.where(bins == b)[0]
        if len(bin_atom_idx) == 0:
            continue
        weights = retrieval_trace_score[bin_atom_idx] + 1.0
        weights = weights / weights.sum()
        k_eff = min(k_per_bin, len(bin_atom_idx))
        if k_eff < k_per_bin:
            sampled = rng.choice(bin_atom_idx, size=k_per_bin,
                                 replace=True, p=weights)
        else:
            sampled = rng.choice(bin_atom_idx, size=k_per_bin,
                                 replace=False, p=weights)
        for s in sampled:
            importance[s] += 1.0
    return importance


def importance_inverse_weighted_replay(
    atom_norms: np.ndarray,
    retrieval_trace_score: np.ndarray,
    seed: int,
    n_events: int = TOTAL_REPLAY_EVENTS,
) -> np.ndarray:
    """Liu IS: importance = replay_count / ||a||^2."""
    rng = np.random.RandomState(seed + 33337)
    weights = retrieval_trace_score + 1.0
    weights = weights / weights.sum()
    sampled = rng.choice(M_TOTAL, size=n_events, replace=True, p=weights)
    raw_count = np.zeros(M_TOTAL, dtype=np.float64)
    for s in sampled:
        raw_count[s] += 1.0
    denom = np.maximum(atom_norms ** 2, 1e-9)
    return raw_count / denom


def run_arm(arm_name: str, seed: int, shared: Tuple) -> Dict:
    t0 = time.time()
    (W_base, all_keys, all_values, edge_graph,
     retrieved_idx, unretrieved_idx,
     retrieval_trace_score, _ultrametric_coreness_unused) = shared
    atom_norms = _atom_norms_from_substrate(all_keys, W_base)

    if arm_name == "ARM_RAND_IMPORTANCE":
        importance = importance_random(seed)
    elif arm_name == "ARM_TRACE_ONLY":
        importance = importance_trace_only(retrieval_trace_score)
    elif arm_name == "ARM_STRATIFIED_REPLAY":
        importance = importance_stratified_replay(
            atom_norms, retrieval_trace_score, seed,
        )
    elif arm_name == "ARM_INVERSE_WEIGHTED_REPLAY":
        importance = importance_inverse_weighted_replay(
            atom_norms, retrieval_trace_score, seed,
        )
    else:
        raise ValueError(f"unknown arm {arm_name}")

    assert importance.shape[0] == M_TOTAL, (
        f"importance vector wrong size for {arm_name}: "
        f"{importance.shape[0]} != {M_TOTAL}"
    )

    cor_imp_norm = correlation_E_vs_magnitude(importance, atom_norms)

    n_nonzero = int(np.sum(importance > 0))
    elapsed = time.time() - t0
    return {
        "arm_name": arm_name,
        "cor_importance_magnitude": float(cor_imp_norm),
        "importance_min": float(np.min(importance)),
        "importance_max": float(np.max(importance)),
        "importance_mean": float(np.mean(importance)),
        "n_nonzero_atoms": int(n_nonzero),
        "atom_norms_min": float(np.min(atom_norms)),
        "atom_norms_max": float(np.max(atom_norms)),
        "atom_norms_mean": float(np.mean(atom_norms)),
        "wall_s": float(elapsed),
    }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(f"  [seed={seed}] setup substrate (inlined v3 setup)...",
          flush=True)
    try:
        shared = setup_substrate_with_trace_and_clusters(seed)
        trace_total = float(np.sum(shared[6]))
        print(f"  [seed={seed}] setup done trace_total={trace_total:.0f}",
              flush=True)
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"  [seed={seed}] SETUP_EXCEPTION: {exc}\n{tb}", flush=True)
        return {
            "seed": seed, "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
            "alpha": float(ALPHA), "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "exception_phase": "setup",
            "exception_msg": str(exc),
            "exception_traceback": tb,
            "arms": [],
            "elapsed_s": float(time.time() - t0),
        }

    arms = []
    for arm_name in ARM_NAMES:
        try:
            out = run_arm(arm_name, seed, shared=shared)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name}] "
                f"cor={out['cor_importance_magnitude']:+.4f} "
                f"n_nonzero={out['n_nonzero_atoms']} "
                f"wall={out['wall_s']:.2f}s",
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
        "alpha": float(ALPHA), "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": 0,
        "trace_total": float(np.sum(shared[6])),
        "n_retrieved": int(shared[4].shape[0]),
        "n_unretrieved": int(shared[5].shape[0]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Self-tests (META_RULE_K)
# ---------------------------------------------------------------------------
def _selftest_stratified_breaks_correlation_synthetic() -> bool:
    rng = np.random.RandomState(0)
    m_test = M_TOTAL
    atom_norms_test = np.linspace(0.1, 1.0, m_test)
    rng.shuffle(atom_norms_test)
    trace_test = atom_norms_test ** 2 * 100.0 + rng.rand(m_test) * 0.5

    cor_trace = correlation_E_vs_magnitude(trace_test, atom_norms_test)
    assert cor_trace > 0.6, (
        f"selftest synthetic trace-bias: expected cor > 0.6 "
        f"(Cauchy-Schwarz scaling); got {cor_trace:.4f}"
    )

    rng_strat = np.random.RandomState(1)
    quantiles = np.quantile(atom_norms_test, np.linspace(0, 1, 11))
    quantiles[-1] += 1e-9
    bins = np.digitize(atom_norms_test, quantiles[1:-1])
    importance_strat = np.zeros(m_test)
    for b in range(10):
        bin_idx = np.where(bins == b)[0]
        if len(bin_idx) == 0:
            continue
        sampled = rng_strat.choice(bin_idx,
                                    size=min(8, len(bin_idx)),
                                    replace=False)
        for s in sampled:
            importance_strat[s] += 1.0
    cor_strat = correlation_E_vs_magnitude(importance_strat, atom_norms_test)
    assert abs(cor_strat) < 0.30, (
        f"selftest synthetic stratified: expected |cor| < 0.30; "
        f"got {cor_strat:.4f}"
    )
    return True


def _selftest_inverse_weighted_correction_synthetic() -> bool:
    rng = np.random.RandomState(2)
    m_test = M_TOTAL
    atom_norms_test = np.linspace(0.1, 1.0, m_test)
    rng.shuffle(atom_norms_test)
    raw_count = atom_norms_test ** 2 * 50.0
    inverse_weighted = raw_count / np.maximum(atom_norms_test ** 2, 1e-9)
    cor_raw = correlation_E_vs_magnitude(raw_count, atom_norms_test)
    cor_inv = correlation_E_vs_magnitude(inverse_weighted, atom_norms_test)
    assert cor_raw > 0.6, f"selftest raw_count cor: {cor_raw:.4f}"
    assert abs(cor_inv) < 0.20, (
        f"selftest inverse_weighted: expected |cor| < 0.20; got {cor_inv:.4f}"
    )
    return True


def _selftest_alpha_regime_is_high() -> bool:
    assert ALPHA >= 1.5, (
        f"diagnostic must run at HIGH-alpha regime; got alpha={ALPHA:.3f}"
    )
    return True


def _selftest_4_arms_required() -> bool:
    assert len(ARM_NAMES) == 4, (
        f"diagnostic requires 4 arms; got {len(ARM_NAMES)}: {ARM_NAMES}"
    )
    return True


def _instrumentation_selftest():
    _selftest_4_arms_required()
    _selftest_alpha_regime_is_high()
    _selftest_stratified_breaks_correlation_synthetic()
    _selftest_inverse_weighted_correction_synthetic()
    print(
        f"[selftest] PASS N={N} M_TOTAL={M_TOTAL} alpha={ALPHA:.3f} "
        f"n_bins={N_BINS_STRATIFIED} k_per_bin={K_PER_BIN} mode={RUN_MODE} "
        f"arms={ARM_NAMES}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict (drill stub 3 bands)
# ---------------------------------------------------------------------------
def _arms_by_name(arms: List[Dict], name: str) -> List[Dict]:
    return [a for a in arms if a.get("arm_name") == name]


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    for r in results:
        if "exception_phase" in r:
            return ("HARD_FAIL",
                    f"HARD_FAIL: META_RULE_J caught {r['exception_phase']} "
                    f"exception seed={r['seed']}: {r['exception_msg']}")
        for a in r.get("arms", []):
            if "exception_msg" in a:
                return ("HARD_FAIL",
                        f"HARD_FAIL: META_RULE_J caught arm exception "
                        f"seed={r['seed']} arm={a['arm_name']}: "
                        f"{a['exception_msg']}")

    expected_per_seed = len(ARM_NAMES)
    for r in results:
        got = len(r.get("arms", []))
        if got != expected_per_seed:
            return ("HARD_FAIL",
                    f"HARD_FAIL: META_RULE_H cardinality_ok breach "
                    f"seed={r['seed']}: expected {expected_per_seed} arms, "
                    f"got {got}")

    def _agg_cor(arm_name: str) -> float:
        per = []
        for r in results:
            per.extend(_arms_by_name(r["arms"], arm_name))
        if not per:
            return float("nan")
        cors = [float(a.get("cor_importance_magnitude", float("nan")))
                for a in per]
        return float(np.nanmean(cors))

    cor_rand = _agg_cor("ARM_RAND_IMPORTANCE")
    cor_trace = _agg_cor("ARM_TRACE_ONLY")
    cor_strat = _agg_cor("ARM_STRATIFIED_REPLAY")
    cor_inv = _agg_cor("ARM_INVERSE_WEIGHTED_REPLAY")

    summary = (
        f"alpha={ALPHA:.3f} mode={RUN_MODE} "
        f"cor(RAND)={cor_rand:+.3f} "
        f"cor(TRACE)={cor_trace:+.3f} "
        f"cor(STRAT)={cor_strat:+.3f} "
        f"cor(INV_WGT)={cor_inv:+.3f}"
    )

    bias_floor = (
        REPRODUCE_TRACE_BIAS_FLOOR_SMOKE if RUN_MODE == "smoke"
        else REPRODUCE_TRACE_BIAS_FLOOR_FULL
    )

    trace_bias_reproduced = abs(cor_trace) >= bias_floor
    diagnostic_pass_a = abs(cor_strat) < DIAGNOSTIC_COR_GATE
    diagnostic_pass_b = abs(cor_inv) < DIAGNOSTIC_COR_GATE

    if not trace_bias_reproduced and abs(cor_trace) < 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: TRACE cor={cor_trace:+.3f} below {0.30} -- "
                f"drill claim contradicted; either Cauchy-Schwarz math is "
                f"wrong OR test rigging wrong. SURPRISE_NEGATIVE. {summary}")

    if trace_bias_reproduced and (diagnostic_pass_a or diagnostic_pass_b):
        which = []
        if diagnostic_pass_a:
            which.append("STRATIFIED")
        if diagnostic_pass_b:
            which.append("INVERSE_WEIGHTED")
        return ("HARD_PASS",
                f"DIAGNOSTIC_PASS: TRACE reproduces |W|-bias "
                f"(cor={cor_trace:+.3f} >= {bias_floor}); "
                f"{'+'.join(which)} clears 0.30 gate -- fairness violation "
                f"IS sampling-bias artifact; v5 M-CFU / stratified path "
                f"endorsed. {summary}")

    if trace_bias_reproduced and not (diagnostic_pass_a or diagnostic_pass_b):
        return ("MIDDLE_BAND",
                f"PARTIAL_DIAGNOSTIC: TRACE reproduces bias "
                f"(cor={cor_trace:+.3f}) but neither STRATIFIED "
                f"(cor={cor_strat:+.3f}) nor INVERSE "
                f"(cor={cor_inv:+.3f}) breaks <0.30; sampling tricks "
                f"insufficient; deeper substrate property suspected. "
                f"{summary}")

    return ("MIDDLE_BAND",
            f"UNEXPECTED: trace_bias_reproduced={trace_bias_reproduced} "
            f"diagnostic_pass_a={diagnostic_pass_a} "
            f"diagnostic_pass_b={diagnostic_pass_b}. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
              "alpha": float(ALPHA), "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
      f"running {remaining}", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] stratified-replay diagnostic v2 N={N} "
          f"alpha={ALPHA:.3f} mode={RUN_MODE} arms={ARM_NAMES}...",
          flush=True)
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
        f"n_seeds={len(all_results)} N={N} M_TOTAL={M_TOTAL} "
        f"alpha={ALPHA:.3f} n_bins={N_BINS_STRATIFIED} "
        f"k_per_bin={K_PER_BIN} mode={RUN_MODE} arms={ARM_NAMES} "
        f"DIAGNOSTIC_COR_GATE={DIAGNOSTIC_COR_GATE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
    "alpha": float(ALPHA),
    "n_seeds": len(SEEDS),
    "n_bins_stratified": N_BINS_STRATIFIED,
    "k_per_bin": K_PER_BIN,
    "total_replay_events": TOTAL_REPLAY_EVENTS,
    "diagnostic_cor_gate": DIAGNOSTIC_COR_GATE,
    "run_mode": RUN_MODE,
    "n_llm_calls_total": 0,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "trace_total": r.get("trace_total"),
            "n_retrieved": r.get("n_retrieved"),
            "n_unretrieved": r.get("n_unretrieved"),
            "arms": r.get("arms"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
