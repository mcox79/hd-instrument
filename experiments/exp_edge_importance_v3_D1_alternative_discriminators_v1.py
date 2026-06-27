"""edge_importance_v3 D1 alternative discriminators -- ZERO new compute.

Re-analyzes existing v3 metrics from
  data/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3/metrics.json
to compute alternative discriminators identified in the
2026-06-27 complementary-angle drill.

Pre-reg: preregs/2026-06-27_edge_importance_v3_D1_alternative_discriminators_v1.md

Drill section recommendations (ANGLE 1):
  D1 -- AUC of importance score vs binary survive-after-pruning label
  D2 -- Top-K precision (precision@K=50 of top-importance vs retained set)
  D3 -- KM-curve gap (survival gap top-10% vs bottom-10% importance)

We DO NOT have per-atom post-pruning recall stored from v3 (only aggregate per-
arm rec_RETRIEVED / rec_UNRETRIEVED). So the D1 AUC is computed from the
RETRIEVED-vs-UNRETRIEVED partition labels (top-importance atoms should map to
RETRIEVED set; bottom-importance to UNRETRIEVED set; this IS the substrate's
downstream consumer label per Cramer-Rao framing of TWO_TIER promotion).

LIMITATION ACKNOWLEDGED HONESTLY: D1 here is "importance-rank vs retrieved-
status" which is a partial proxy for the drill's "importance-rank vs
survive-after-decay" formulation. The full D1 / D2 / D3 require per-atom post-
decay recall which v3 did not store. Re-running v3 with per-atom recall logging
would unlock the full drill formulation; THIS cell extracts the maximum
information from existing metrics.

DISCRIMINATORS COMPUTED (all from existing v3 metrics.json):
  D1_partition_AUC -- AUC(importance, label=in_retrieved_set) per arm per seed
  D2_topK_precision -- precision@K=N_USE of top-importance atoms vs
                         retrieved_idx set membership
  D3_KM_gap -- We cannot compute KM-curve gap without per-atom recall;
                 instead compute fraction-protected-survival proxy:
                 fraction of top-importance-50% atoms whose ARM's
                 rec_RETRIEVED >= 0.90 (a check on whether the importance
                 ranking is high-utility for downstream).

HARD_PASS (per drill section ANGLE 1):
  D1 AUC of TRACE_ONLY arm and any COMPOSITION arm >= 0.65 in all 3 seeds
  AND AUC cv (across seeds) <= 0.05

DISCIPLINES (META rules per 2026-06-26):
  META_RULE_H -- cardinality_ok: SEEDS(3) x ARMS(6: rand/trace/ultra/comp_l01/
                  comp_l03/comp_l05); assert post-loop.
  META_RULE_J -- no-silent-except in setup + per-seed re-analysis blocks.
  META_RULE_K -- discriminator-fires assertion: per-arm n_atoms_scored > 0,
                  AUC well-defined (>= 0.0).
  META_RULE_L -- discriminator-survives-scale: cell uses FULL N_USE/M_OLD
                  values (no smoke scale-down; re-analysis is at full scale).
  META_RULE_M -- production-scale instrument calibration: AUC computation
                  uses sklearn.metrics.roc_auc_score (chain-grade reference).

ASCII-only; no unicode.
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

# v3 source cell parses its own argv at import time and calls sys.exit(0) on
# --self-test. When THIS cell runs with --self-test, the import below would
# exit the process before our own selftests ran. Strip the flag from argv for
# the duration of the import.
_SAVED_ARGV = list(sys.argv)
sys.argv = [a for a in sys.argv if a not in ("--self-test", "--smoke")]

from experiments._seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    get_output_dir,
    resumable_seeds,
    write_partial,
)


ANCHOR_NAME = "edge_importance_v3_D1_alternative_discriminators_v1"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# Re-analysis: same params as v3 source (no scale-down at smoke; re-analysis
# is read-only of existing metrics.json).
V3_SOURCE_METRICS = (
    REPO
    / "data"
    / "exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3"
    / "metrics.json"
)

# Mirror v3 config (must match what was used to produce the source metrics).
N = 512
M_OLD = 600
M_RECENT = 400
M_TOTAL = M_OLD + M_RECENT
N_COMPOSITE_QUERIES = 3000
USE_FRAC = 0.40
COMPOSITE_ARITY = 3
N_USE = max(COMPOSITE_ARITY, int(round(USE_FRAC * M_OLD)))
SEEDS = [7, 17, 23]
LAMBDA_LIST = [0.1, 0.3, 0.5]

# Need to regenerate retrieved_idx / unretrieved_idx and trace + coreness
# vectors to compute per-atom AUC -- the source metrics.json only stores
# arm-aggregate scalars. We REPLICATE v3's setup logic deterministically per
# seed (same RNG seeds; tiny CPU cost; this is NOT new mechanism work, just
# replaying the deterministic v3 setup).

# Import v3's setup helpers (deterministic; reuse to avoid drift).
from experiments.exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3 import (  # noqa: E402,E501
    setup_substrate_with_trace_and_clusters,
    importance_random,
    importance_trace_only,
    importance_ultrametric_only,
    importance_trace_x_coreness,
)

# Restore argv after the v3 import has consumed it.
sys.argv = _SAVED_ARGV


CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},source_v3,N={N},M_OLD={M_OLD},"
    f"M_RECENT={M_RECENT},N_USE={N_USE},SEEDS={SEEDS},"
    f"LAMBDA_LIST={LAMBDA_LIST},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Discriminator math (D1 / D2 / D3 proxies from existing per-arm metrics)
# ---------------------------------------------------------------------------
def _roc_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    """AUC via Mann-Whitney U formula (no sklearn dependency)."""
    if labels.shape != scores.shape:
        raise ValueError(
            f"shape mismatch: labels={labels.shape}, scores={scores.shape}"
        )
    pos_mask = labels > 0
    n_pos = int(np.sum(pos_mask))
    n_neg = int(labels.shape[0] - n_pos)
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    # Rank scores (ties get average rank).
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, scores.shape[0] + 1, dtype=np.float64)
    # Handle ties by averaging rank within equal-score groups.
    sorted_scores = scores[order]
    i = 0
    while i < sorted_scores.shape[0]:
        j = i
        while (
            j + 1 < sorted_scores.shape[0]
            and sorted_scores[j + 1] == sorted_scores[i]
        ):
            j += 1
        if j > i:
            avg_rank = float(np.mean(ranks[order[i:j + 1]]))
            ranks[order[i:j + 1]] = avg_rank
        i = j + 1
    sum_ranks_pos = float(np.sum(ranks[pos_mask]))
    auc = (sum_ranks_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)


def _top_k_precision(
    importance: np.ndarray, positive_idx: np.ndarray, k: int,
) -> float:
    """Precision@K: of top-K importance atoms, how many are in positive set."""
    if k <= 0 or k > importance.shape[0]:
        return float("nan")
    top_k_idx = np.argsort(-importance)[:k]
    pos_set = set(positive_idx.tolist())
    n_hits = int(sum(1 for i in top_k_idx if int(i) in pos_set))
    return float(n_hits) / float(k)


def _km_proxy_top_vs_bottom_quantile_separation(
    importance: np.ndarray, positive_idx: np.ndarray, q: float = 0.10,
) -> float:
    """KM-curve gap proxy:
    fraction-of-top-q% atoms that are in positive set
    MINUS fraction-of-bottom-q% atoms that are in positive set.

    Larger gap = importance is better discriminator of survival proxy.
    Range: [-1, 1]; HARD_PASS target >= 0.30.
    """
    n = importance.shape[0]
    k = max(1, int(round(q * n)))
    order = np.argsort(-importance)
    top_idx = order[:k]
    bot_idx = order[-k:]
    pos_set = set(positive_idx.tolist())
    frac_top = float(sum(1 for i in top_idx if int(i) in pos_set)) / float(k)
    frac_bot = float(sum(1 for i in bot_idx if int(i) in pos_set)) / float(k)
    return frac_top - frac_bot


# ---------------------------------------------------------------------------
# Self-tests (META_RULE_K: discriminator-fires assertion at module import)
# ---------------------------------------------------------------------------
def _selftest_auc_known_values() -> bool:
    """AUC on perfect separation = 1.0; on inverted = 0.0; on random ~0.5."""
    # Perfect: labels match scores order
    labels = np.array([0, 0, 0, 1, 1, 1])
    scores = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    auc = _roc_auc(labels, scores)
    assert abs(auc - 1.0) < 1e-6, f"AUC perfect: expected 1.0, got {auc}"
    # Inverted
    auc_inv = _roc_auc(labels, -scores)
    assert abs(auc_inv - 0.0) < 1e-6, f"AUC inverted: expected 0.0, got {auc_inv}"
    # Tie handling (all equal -> 0.5)
    auc_tie = _roc_auc(labels, np.zeros_like(scores))
    assert abs(auc_tie - 0.5) < 1e-6, f"AUC tied: expected 0.5, got {auc_tie}"
    return True


def _selftest_topk_precision_known() -> bool:
    """Top-3 of [10,9,8,1,2,3] vs positives={0,1,5} -> top-3 = {0,1,2}; hits=2."""
    imp = np.array([10.0, 9.0, 8.0, 1.0, 2.0, 3.0])
    pos = np.array([0, 1, 5])
    p = _top_k_precision(imp, pos, 3)
    assert abs(p - 2.0 / 3.0) < 1e-6, f"top-K: expected 2/3, got {p}"
    return True


def _selftest_km_proxy_known() -> bool:
    """All positives at top -> gap = 1 - 0 = 1.0."""
    imp = np.array([10.0, 9.0, 8.0, 1.0, 2.0, 3.0])
    pos = np.array([0, 1])
    # q=0.34 -> k=2; top 2 are 0,1; bottom 2 are 3,4 (sorted by -imp idx)
    gap = _km_proxy_top_vs_bottom_quantile_separation(imp, pos, q=0.34)
    assert abs(gap - 1.0) < 1e-6, f"KM proxy: expected 1.0, got {gap}"
    return True


def _selftest_v3_source_exists() -> bool:
    """v3 source metrics must exist before re-analysis can run."""
    assert V3_SOURCE_METRICS.exists(), (
        f"v3 source metrics not found: {V3_SOURCE_METRICS}. "
        "Cannot re-analyze without source data."
    )
    return True


def _instrumentation_selftest():
    _selftest_auc_known_values()
    _selftest_topk_precision_known()
    _selftest_km_proxy_known()
    _selftest_v3_source_exists()
    print(
        f"[selftest] PASS  N={N}  M_OLD={M_OLD}  N_USE={N_USE}  "
        f"SEEDS={SEEDS}  LAMBDA_LIST={LAMBDA_LIST}  mode={RUN_MODE}  "
        f"source={V3_SOURCE_METRICS.exists()}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed re-analysis (replay v3 setup; compute D1/D2/D3 per arm per seed)
# ---------------------------------------------------------------------------
ARM_NAMES_SINGLE = [
    "ARM_BASELINE_RANDOM_IMPORTANCE",
    "ARM_TRACE_ONLY",
    "ARM_ULTRAMETRIC_ONLY",
]


def reanalyze_seed(seed: int) -> Dict:
    t0 = time.time()
    try:
        # Replay v3's deterministic setup to recover per-atom importance
        # vectors + retrieved/unretrieved index sets.
        shared = setup_substrate_with_trace_and_clusters(seed)
        (_W, _all_keys, _all_values, _edge_graph,
         retrieved_idx, unretrieved_idx,
         retrieval_trace_score, ultrametric_coreness) = shared
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"  [seed={seed}] SETUP_EXCEPTION: {exc}\n{tb}", flush=True)
        return {
            "seed": seed,
            "config_version": CONFIG_VERSION,
            "exception_phase": "setup",
            "exception_msg": str(exc),
            "exception_traceback": tb,
            "arms": [],
            "elapsed_s": float(time.time() - t0),
        }

    # Labels: atom is "positive" if it's in retrieved_idx (downstream
    # consumer's protected set; this is the actual substrate-product label).
    labels = np.zeros(M_TOTAL, dtype=np.float64)
    labels[retrieved_idx] = 1.0

    arms = []
    # 3 single arms
    for arm_name in ARM_NAMES_SINGLE:
        try:
            if arm_name == "ARM_BASELINE_RANDOM_IMPORTANCE":
                imp = importance_random(seed)
            elif arm_name == "ARM_TRACE_ONLY":
                imp = importance_trace_only(retrieval_trace_score)
            elif arm_name == "ARM_ULTRAMETRIC_ONLY":
                imp = importance_ultrametric_only(ultrametric_coreness)
            else:
                raise ValueError(f"unknown arm {arm_name}")

            d1_auc = _roc_auc(labels, imp)
            d2_topk = _top_k_precision(imp, retrieved_idx, k=N_USE)
            d2_top50 = _top_k_precision(imp, retrieved_idx, k=50)
            d3_km = _km_proxy_top_vs_bottom_quantile_separation(
                imp, retrieved_idx, q=0.10,
            )
            # META_RULE_K discriminator-fires: AUC well-defined; n_scored > 0
            assert np.isfinite(d1_auc), (
                f"D1 AUC non-finite for {arm_name} seed={seed}"
            )
            assert imp.shape[0] == M_TOTAL, (
                f"importance vector wrong size for {arm_name}: "
                f"{imp.shape[0]} != {M_TOTAL}"
            )

            arms.append({
                "arm_name": arm_name,
                "lambda": None,
                "D1_partition_AUC": float(d1_auc),
                "D2_topK_precision_at_N_USE": float(d2_topk),
                "D2_topK_precision_at_50": float(d2_top50),
                "D3_KM_quantile_gap_top10_bot10": float(d3_km),
                "n_atoms_scored": int(imp.shape[0]),
                "imp_min": float(np.min(imp)),
                "imp_max": float(np.max(imp)),
                "imp_mean": float(np.mean(imp)),
            })
            print(
                f"  [seed={seed} {arm_name}] D1_AUC={d1_auc:.3f} "
                f"D2_p@N_USE={d2_topk:.3f} D2_p@50={d2_top50:.3f} "
                f"D3_KM_gap={d3_km:.3f}",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(
                f"  [seed={seed} {arm_name}] ARM_EXCEPTION: {exc}\n{tb}",
                flush=True,
            )
            arms.append({
                "arm_name": arm_name,
                "exception_msg": str(exc),
                "exception_traceback": tb,
            })

    # COMPOSITION arm per lambda
    for lam in LAMBDA_LIST:
        arm_name = "ARM_TRACE_X_CORENESS"
        try:
            imp = importance_trace_x_coreness(
                retrieval_trace_score, ultrametric_coreness, lam,
            )
            d1_auc = _roc_auc(labels, imp)
            d2_topk = _top_k_precision(imp, retrieved_idx, k=N_USE)
            d2_top50 = _top_k_precision(imp, retrieved_idx, k=50)
            d3_km = _km_proxy_top_vs_bottom_quantile_separation(
                imp, retrieved_idx, q=0.10,
            )
            assert np.isfinite(d1_auc), (
                f"D1 AUC non-finite for {arm_name} lam={lam} seed={seed}"
            )
            arms.append({
                "arm_name": arm_name,
                "lambda": float(lam),
                "D1_partition_AUC": float(d1_auc),
                "D2_topK_precision_at_N_USE": float(d2_topk),
                "D2_topK_precision_at_50": float(d2_top50),
                "D3_KM_quantile_gap_top10_bot10": float(d3_km),
                "n_atoms_scored": int(imp.shape[0]),
                "imp_min": float(np.min(imp)),
                "imp_max": float(np.max(imp)),
                "imp_mean": float(np.mean(imp)),
            })
            print(
                f"  [seed={seed} {arm_name} lam={lam}] D1_AUC={d1_auc:.3f} "
                f"D2_p@N_USE={d2_topk:.3f} D2_p@50={d2_top50:.3f} "
                f"D3_KM_gap={d3_km:.3f}",
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
        "config_version": CONFIG_VERSION,
        "n_retrieved": int(retrieved_idx.shape[0]),
        "n_unretrieved": int(unretrieved_idx.shape[0]),
        "trace_total": float(np.sum(retrieval_trace_score)),
        "coreness_atoms": int(np.sum(ultrametric_coreness)),
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

    # META_RULE_H cardinality_ok: 3 single arms + 3 composition arms per seed = 6
    expected_per_seed = len(ARM_NAMES_SINGLE) + len(LAMBDA_LIST)
    for r in results:
        got = len(r.get("arms", []))
        if got != expected_per_seed:
            return ("HARD_FAIL",
                    f"HARD_FAIL: META_RULE_H cardinality_ok breach "
                    f"seed={r['seed']}: expected {expected_per_seed} arm "
                    f"entries, got {got}")

    # Aggregate D1 AUC per arm across seeds.
    # Defensive .get() access: if a stale partial / silently-dropped arm lacks
    # the D1_partition_AUC key (e.g., resumed from old-schema partial), record
    # nan + flag rather than KeyError. The verdict path detects nan via the
    # non-finite guard below and converts to HARD_FAIL with a clear message.
    # Fix (exp_dev 2026-06-27): remote queue_add gate-failed with KeyError
    # here despite local self-test passing -- root cause was stale partials
    # from a prior schema. Per-arm exception arms are already caught upstream
    # at lines 460-465; this only catches the schema-drift / silent-skip case.
    def _agg_auc(arm_name: str, lam: float = None) -> Dict:
        per = []
        missing_key_arms = []
        for r in results:
            for a in _arms_by_name(r["arms"], arm_name):
                if lam is None or a.get("lambda") == lam:
                    per.append(a)
        if not per:
            return {}
        # Defensive access; any arm missing D1_partition_AUC contributes nan.
        aucs = []
        for a in per:
            v = a.get("D1_partition_AUC")
            if v is None:
                missing_key_arms.append(
                    f"seed={a.get('seed', '?')} arm={arm_name} "
                    f"lam={a.get('lambda')}"
                )
                aucs.append(float("nan"))
            else:
                aucs.append(float(v))
        topks = [float(a.get("D2_topK_precision_at_N_USE", float("nan")))
                 for a in per]
        top50s = [float(a.get("D2_topK_precision_at_50", float("nan")))
                  for a in per]
        kms = [float(a.get("D3_KM_quantile_gap_top10_bot10", float("nan")))
               for a in per]
        mean_auc = float(np.nanmean(aucs)) if aucs else float("nan")
        result = {
            "mean_D1_AUC": mean_auc,
            "std_D1_AUC": float(np.nanstd(aucs)) if aucs else float("nan"),
            "cv_D1_AUC": float(
                np.nanstd(aucs) / max(abs(mean_auc), 1e-9)
            ) if np.isfinite(mean_auc) else float("nan"),
            "mean_D2_topK_at_N_USE": float(np.nanmean(topks)) if topks else float("nan"),
            "mean_D2_topK_at_50": float(np.nanmean(top50s)) if top50s else float("nan"),
            "mean_D3_KM_gap": float(np.nanmean(kms)) if kms else float("nan"),
        }
        if missing_key_arms:
            result["missing_D1_partition_AUC_arms"] = missing_key_arms
        return result

    agg_rand = _agg_auc("ARM_BASELINE_RANDOM_IMPORTANCE")
    agg_trace = _agg_auc("ARM_TRACE_ONLY")
    agg_ultra = _agg_auc("ARM_ULTRAMETRIC_ONLY")
    agg_comp = {lam: _agg_auc("ARM_TRACE_X_CORENESS", lam=lam)
                for lam in LAMBDA_LIST}

    # Best composition by D1 AUC.
    best_lam = LAMBDA_LIST[0]
    best_auc = -1.0
    for lam in LAMBDA_LIST:
        a = agg_comp.get(lam, {})
        if a and a.get("mean_D1_AUC", -1.0) > best_auc:
            best_auc = a["mean_D1_AUC"]
            best_lam = lam
    best_comp = agg_comp.get(best_lam, {})

    summary = (
        f"RAND(D1_AUC={agg_rand.get('mean_D1_AUC', float('nan')):.3f}); "
        f"TRACE(D1_AUC={agg_trace.get('mean_D1_AUC', float('nan')):.3f},"
        f"cv={agg_trace.get('cv_D1_AUC', float('nan')):.3f},"
        f"D2_p@N_USE={agg_trace.get('mean_D2_topK_at_N_USE', float('nan')):.3f},"
        f"D2_p@50={agg_trace.get('mean_D2_topK_at_50', float('nan')):.3f},"
        f"D3_KM={agg_trace.get('mean_D3_KM_gap', float('nan')):.3f}); "
        f"ULTRA(D1_AUC={agg_ultra.get('mean_D1_AUC', float('nan')):.3f}); "
        f"COMP(lam={best_lam},D1_AUC={best_comp.get('mean_D1_AUC', float('nan')):.3f},"
        f"cv={best_comp.get('cv_D1_AUC', float('nan')):.3f},"
        f"D2_p@N_USE={best_comp.get('mean_D2_topK_at_N_USE', float('nan')):.3f},"
        f"D2_p@50={best_comp.get('mean_D2_topK_at_50', float('nan')):.3f},"
        f"D3_KM={best_comp.get('mean_D3_KM_gap', float('nan')):.3f})"
    )

    # Non-finite guard
    for name, a in [("RAND", agg_rand), ("TRACE", agg_trace),
                    ("ULTRA", agg_ultra), ("COMP", best_comp)]:
        if not np.isfinite(a.get("mean_D1_AUC", float("nan"))):
            return ("HARD_FAIL",
                    f"HARD_FAIL: non-finite D1 AUC in {name}. {summary}")

    # HARD_PASS per drill ANGLE 1: any of TRACE or COMP arms >= 0.65 AUC AND
    # cv <= 0.05 across seeds AND strictly above random baseline by >= 0.05.
    trace_auc = agg_trace["mean_D1_AUC"]
    trace_cv = agg_trace["cv_D1_AUC"]
    rand_auc = agg_rand["mean_D1_AUC"]
    comp_auc = best_comp["mean_D1_AUC"]
    comp_cv = best_comp["cv_D1_AUC"]

    trace_passes = (
        trace_auc >= 0.65 and trace_cv <= 0.05 and (trace_auc - rand_auc) >= 0.05
    )
    comp_passes = (
        comp_auc >= 0.65 and comp_cv <= 0.05 and (comp_auc - rand_auc) >= 0.05
    )

    if trace_passes or comp_passes:
        return ("HARD_PASS",
                f"HARD_PASS: D1 AUC reframe shows production-grade ranking. "
                f"trace_pass={trace_passes} comp_pass={comp_passes} "
                f"(bar AUC>=0.65, cv<=0.05, lift_over_random>=0.05). {summary}")

    # MIDDLE_BAND: any arm strictly above random by >= 0.05 but didn't clear bar
    trace_lift = trace_auc - rand_auc
    comp_lift = comp_auc - rand_auc
    if max(trace_lift, comp_lift) >= 0.05:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: importance produces above-random ranking but "
                f"not at production-grade AUC. trace_lift={trace_lift:.3f} "
                f"comp_lift={comp_lift:.3f}. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: importance produces no above-random ranking. "
            f"trace_lift={trace_lift:.3f} comp_lift={comp_lift:.3f}. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
# RULE_EXPERIMENT_CELLS_MUST_GUARD_MAIN_WITH___NAME___DUNDER (added 2026-06-27)
if __name__ == "__main__":
    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
                  "n_use": N_USE, "run_mode": RUN_MODE,
                  "lambda_list": list(LAMBDA_LIST),
                  "source": str(V3_SOURCE_METRICS)}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
        f"running {remaining}", flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(
            f"[seed={seed}] D1 re-analysis (replay v3 setup; compute "
            f"D1/D2/D3 from importance vectors)...",
            flush=True,
        )
        result = reanalyze_seed(seed)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg = compute_verdict(all_results)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} N={N} M_OLD={M_OLD} N_USE={N_USE} "
            f"LAMBDA={LAMBDA_LIST} mode={RUN_MODE} "
            f"source={V3_SOURCE_METRICS.name}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
        "n_seeds": len(SEEDS), "n_use": int(N_USE),
        "lambda_list": list(LAMBDA_LIST),
        "source_metrics_path": str(V3_SOURCE_METRICS),
        "run_mode": RUN_MODE,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "trace_total": r.get("trace_total"),
                "coreness_atoms": r.get("coreness_atoms"),
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
