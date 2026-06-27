"""edge_importance v3.2 TRACE-only with D1 audit -- v2 arm-count fix.

USER 2026-06-27 NO LOCAL + GPU+CPU idle. exp_dev 2026-06-27 cell 3.

Pre-reg: preregs/2026-06-27_edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count_fix.md

PROVENANCE:

v3.2 v1 (exp_edge_importance_v3p2_trace_only_with_D1_audit_v1) HARD_FAILed
META_RULE_H cardinality_ok: expected 2 arms got 6. Root cause: the
data/exp_edge_importance_v3p2_trace_only_with_D1_audit_v1/ output dir
held STALE PARTIALS from an earlier v3-lineage run (BASELINE_RANDOM +
TRACE_ONLY + ULTRA_ONLY + 3x TRACE_X_CORENESS for lambda sweep). The
v3.2 cell declares only 2 ARM_NAMES but resumable_seeds loaded the
v3-lineage 6-arm partials whose run_config matched (same N, M, alpha,
run_mode).

Per drill (notes/research_drill_v3p2_trace_only_with_D1_audit) the right
fix is "drop ULTRA composition entirely" -- keep only 2 arms (RAND +
TRACE_ONLY) -- and ensure the v2 cell doesn't pick up v1's stale 6-arm
partials.

v2 fixes:
1. NEW anchor name (v2_arm_count_fix) -> different output dir -> no
   stale-partial collision with v1.
2. At startup: optionally NUKE stale partials in the v2 output dir if
   any exist (defensive; should be no partials at first run).
3. Per drill: 2 arms only (ARM_BASELINE_RANDOM_IMPORTANCE + ARM_TRACE_ONLY);
   ULTRAMETRIC composition dropped permanently.
4. Pre-reg + ARM_NAMES declare EXACTLY 2 arms; META_RULE_H breach if
   any partial dict has != 2 arms.

ARMS (2 mandatory; HONEST-BOUND per drill):
  ARM_BASELINE_RANDOM_IMPORTANCE -- random importance (control rail)
  ARM_TRACE_ONLY                 -- importance = retrieval_trace_score
                                    (THE mechanism; primary verdict)

PRE-REG BANDS (load-bearing; identical to v1):
  HARD_PASS (all hold across 3 seeds):
    TRACE D1_AUC mean >= 0.65 AND cv <= 0.05 AND
    (TRACE D1_AUC - RAND D1_AUC) >= 0.05 AND
    n_downscaled > 0 in TRACE arm AND
    cor(importance, |W|) < 0.30

  MIDDLE_BAND: TRACE D1_AUC >= 0.55 AND cv <= 0.10 AND mechanism fired

  HARD_FAIL: any of:
    arms within 0.05 of each other on D1_AUC (saturation)
    cor(importance, |W|) >= 0.30
    n_downscaled == 0 in TRACE arm (inert)
    H_n_edges < 50 (workload didn't populate H)
    TRACE D1_AUC < 0.55 (mechanism does NOT rank retrieved above
                         unretrieved)
    any caught exception (META_RULE_J)
    META_RULE_H cardinality_ok breach (per-seed arm count != 2)
    STALE_PARTIAL_DETECTED (loaded partial has != 2 arms; v1's bug)

DISCIPLINES:
  META_RULE_H cardinality_ok: per-seed expected arm count = EXACTLY 2.
  META_RULE_J no-silent-except: setup + each arm wrapped.
  META_RULE_K smoke-fires-discriminator: smoke must produce
    trace_total > 0 AND H_n_edges >= 50 AND mean D1_AUC > 0.50.
  META_RULE_L band-floor strictly-above-floor.

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

# v3 source cell parses its own argv at import time and sys.exit(0)s on
# --self-test. Strip those flags for the duration of the v3 import.
_SAVED_ARGV = list(sys.argv)
sys.argv = [a for a in sys.argv if a not in ("--self-test", "--smoke")]

from experiments._seed_checkpoint import (  # noqa: E402
    aggregate_partials, get_output_dir, resumable_seeds, write_partial,
)
from hdlab.edge_importance import (  # noqa: E402
    EdgeImportance, HConfig, correlation_E_vs_magnitude,
)

# Re-use v3's deterministic setup so this cell composes on the same
# substrate workload (brain STC analog) without re-implementing the
# substrate. Coreness is IGNORED per drill recommendation.
from experiments.exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3 import (  # noqa: E402,E501
    setup_substrate_with_trace_and_clusters,
    importance_random,
    importance_trace_only,
    recall_subset,
    predict,
)

sys.argv = _SAVED_ARGV


# v2 anchor: NEW NAME to avoid v1's stale-partial collision
ANCHOR_NAME = "edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count_fix"
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

# Inherit v3 high-alpha regime; v3 setup uses these constants internally.
N_FULL = 512
M_OLD_FULL = 600
M_RECENT_FULL = 400
N_COMPOSITE_QUERIES_FULL = 3000
COMPOSITE_ARITY = 3
USE_FRAC_FULL = 0.40
DOWNSCALE_SCALE = 0.20
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200

# Smoke discipline: smoke runs at FULL-N parameters; only J / seeds /
# N_QUERIES reduced (META_RULE_K + USER 2026-06-26).
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
    f"DOWNSCALE_SCALE={DOWNSCALE_SCALE},"
    f"N_PRUNE_FRAC={N_PRUNE_FRAC},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"N_QUERIES={N_QUERIES},RUN_MODE={RUN_MODE},v2_arm_count_fix=true"
)


# ---------------------------------------------------------------------------
# Discriminator math (D1 / D2 / D3 -- copy from v1; unchanged)
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
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, scores.shape[0] + 1, dtype=np.float64)
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


def _top_k_precision(importance: np.ndarray, positive_idx: np.ndarray,
                     k: int) -> float:
    if k <= 0 or k > importance.shape[0]:
        return float("nan")
    top_k_idx = np.argsort(-importance)[:k]
    pos_set = set(positive_idx.tolist())
    n_hits = int(sum(1 for i in top_k_idx if int(i) in pos_set))
    return float(n_hits) / float(k)


def _km_proxy_top_vs_bottom_quantile_separation(
    importance: np.ndarray, positive_idx: np.ndarray, q: float = 0.10,
) -> float:
    n = importance.shape[0]
    k = max(1, int(round(q * n)))
    order = np.argsort(-importance)
    top_idx = order[:k]
    bot_idx = order[-k:]
    pos_set = set(positive_idx.tolist())
    frac_top = float(sum(1 for i in top_idx if int(i) in pos_set)) / float(k)
    frac_bot = float(sum(1 for i in bot_idx if int(i) in pos_set)) / float(k)
    return frac_top - frac_bot


def select_prune_indices_low(importance: np.ndarray, n_prune: int,
                             seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 13131)
    jitter = rng.rand(importance.shape[0]) * 1e-6
    score = importance + jitter
    return np.argsort(score)[:n_prune]


# ---------------------------------------------------------------------------
# Self-tests (META_RULE_K)
# ---------------------------------------------------------------------------
def _selftest_auc_known_values() -> bool:
    labels = np.array([0, 0, 0, 1, 1, 1])
    scores = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    auc = _roc_auc(labels, scores)
    assert abs(auc - 1.0) < 1e-6, f"AUC perfect: expected 1.0, got {auc}"
    auc_inv = _roc_auc(labels, -scores)
    assert abs(auc_inv - 0.0) < 1e-6, f"AUC inverted: expected 0.0, got {auc_inv}"
    auc_tie = _roc_auc(labels, np.zeros_like(scores))
    assert abs(auc_tie - 0.5) < 1e-6, f"AUC tied: expected 0.5, got {auc_tie}"
    return True


def _selftest_topk_precision_known() -> bool:
    imp = np.array([10.0, 9.0, 8.0, 1.0, 2.0, 3.0])
    pos = np.array([0, 1, 5])
    p = _top_k_precision(imp, pos, 3)
    assert abs(p - 2.0 / 3.0) < 1e-6, f"top-K: expected 2/3, got {p}"
    return True


def _selftest_km_proxy_known() -> bool:
    imp = np.array([10.0, 9.0, 8.0, 1.0, 2.0, 3.0])
    pos = np.array([0, 1])
    gap = _km_proxy_top_vs_bottom_quantile_separation(imp, pos, q=0.34)
    assert abs(gap - 1.0) < 1e-6, f"KM proxy: expected 1.0, got {gap}"
    return True


def _selftest_alpha_regime_is_high() -> bool:
    assert ALPHA >= 1.5, (
        f"v3.2 must run at HIGH-alpha regime; got alpha={ALPHA:.3f} < 1.5. "
        f"N={N}, M_TOTAL={M_TOTAL}."
    )
    return True


def _selftest_trace_only_no_ultra() -> bool:
    """v3.2 v2 MUST be TRACE-only; no LAMBDA_LIST; no ULTRA arm."""
    assert "LAMBDA_LIST" not in globals(), (
        "v3.2 v2 must NOT carry LAMBDA_LIST (ULTRA composition dropped)"
    )
    assert "ARM_ULTRAMETRIC_ONLY" not in [a for a in ARM_NAMES], (
        "v3.2 v2 must NOT carry ULTRA arm"
    )
    assert "ARM_TRACE_X_CORENESS" not in [a for a in ARM_NAMES], (
        "v3.2 v2 must NOT carry composition arm"
    )
    return True


def _selftest_arm_count_exactly_2() -> bool:
    """v2 ARM-COUNT FIX: exactly 2 arms; reject any drift."""
    assert len(ARM_NAMES) == 2, (
        f"v2 must declare EXACTLY 2 arms; got {len(ARM_NAMES)}: {ARM_NAMES}"
    )
    assert "ARM_BASELINE_RANDOM_IMPORTANCE" in ARM_NAMES, (
        f"v2 must include ARM_BASELINE_RANDOM_IMPORTANCE; got {ARM_NAMES}"
    )
    assert "ARM_TRACE_ONLY" in ARM_NAMES, (
        f"v2 must include ARM_TRACE_ONLY; got {ARM_NAMES}"
    )
    return True


def _selftest_anchor_name_differs_from_v1() -> bool:
    """v2 anchor MUST differ from v1 so stale partials don't collide."""
    assert ANCHOR_NAME != "edge_importance_v3p2_trace_only_with_D1_audit_v1", (
        f"v2 anchor must differ from v1 to avoid stale-partial collision; "
        f"got {ANCHOR_NAME}"
    )
    assert "v2" in ANCHOR_NAME, (
        f"v2 anchor must contain 'v2'; got {ANCHOR_NAME}"
    )
    return True


def _instrumentation_selftest():
    _selftest_auc_known_values()
    _selftest_topk_precision_known()
    _selftest_km_proxy_known()
    _selftest_alpha_regime_is_high()
    _selftest_trace_only_no_ultra()
    _selftest_arm_count_exactly_2()
    _selftest_anchor_name_differs_from_v1()
    print(
        f"[selftest] PASS  N={N}  M_OLD={M_OLD}  M_RECENT={M_RECENT}  "
        f"alpha={ALPHA:.3f}  J_comp={N_COMPOSITE_QUERIES}  "
        f"arity={COMPOSITE_ARITY}  N_USE={N_USE}  mode={RUN_MODE} "
        f"arms=TRACE-only-v2 (ARM_COUNT_FIX; ULTRA dropped per drill)",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Arm definition (2 mandatory; TRACE-only + RAND control rail)
# ---------------------------------------------------------------------------
ARM_NAMES = [
    "ARM_BASELINE_RANDOM_IMPORTANCE",
    "ARM_TRACE_ONLY",
]


_instrumentation_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner (META_RULE_J no-silent-except; META_RULE_H cardinality_ok)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int, shared: Tuple) -> Dict:
    t0 = time.time()
    (W_base, all_keys, all_values, edge_graph,
     retrieved_idx, unretrieved_idx,
     retrieval_trace_score, _ultrametric_coreness_unused) = shared

    W = W_base.copy()
    W_norm_pre = float(np.linalg.norm(W))

    if arm_name == "ARM_BASELINE_RANDOM_IMPORTANCE":
        importance = importance_random(seed)
    elif arm_name == "ARM_TRACE_ONLY":
        importance = importance_trace_only(retrieval_trace_score)
    else:
        raise ValueError(f"unknown arm {arm_name}")

    labels = np.zeros(M_TOTAL, dtype=np.float64)
    labels[retrieved_idx] = 1.0

    d1_auc = _roc_auc(labels, importance)
    d2_topk = _top_k_precision(importance, retrieved_idx, k=N_USE)
    d2_top50 = _top_k_precision(importance, retrieved_idx, k=50)
    d3_km = _km_proxy_top_vs_bottom_quantile_separation(
        importance, retrieved_idx, q=0.10,
    )
    assert np.isfinite(d1_auc), (
        f"D1 AUC non-finite for {arm_name} seed={seed}"
    )
    assert importance.shape[0] == M_TOTAL, (
        f"importance vector wrong size for {arm_name}"
    )

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
    ret_query = rng_eval.choice(retrieved_idx, size=n_q_ret, replace=False)
    unret_query = rng_eval.choice(unretrieved_idx, size=n_q_unret,
                                  replace=False)
    rec_query = rng_eval.choice(M_RECENT, size=n_q_rec,
                                replace=False) + M_OLD

    recall_old_retrieved = recall_subset(W, all_keys, ret_query, all_values)
    recall_old_unretrieved = recall_subset(W, all_keys, unret_query,
                                           all_values)
    recall_recent = recall_subset(W, all_keys, rec_query, all_values)

    elapsed = time.time() - t0
    return {
        "arm_name": arm_name,
        "D1_partition_AUC": float(d1_auc),
        "D2_topK_precision_at_N_USE": float(d2_topk),
        "D2_topK_precision_at_50": float(d2_top50),
        "D3_KM_quantile_gap_top10_bot10": float(d3_km),
        "n_atoms_scored": int(importance.shape[0]),
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


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(
        f"  [seed={seed}] setup + populate H + trace "
        f"(J_comp={N_COMPOSITE_QUERIES}, arity={COMPOSITE_ARITY}, "
        f"N_USE={N_USE} of M_OLD={M_OLD})...", flush=True,
    )
    try:
        t_setup = time.time()
        shared = setup_substrate_with_trace_and_clusters(seed)
        trace_total = float(np.sum(shared[6]))
        n_edges = shared[3].n_edges()
        coreness_count = int(np.sum(shared[7]))
        print(
            f"  [seed={seed}] setup done in {time.time()-t_setup:.1f}s  "
            f"H_edges={n_edges} trace_total={trace_total:.0f} "
            f"(coreness_atoms={coreness_count}; v2 IGNORES coreness)",
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
    for arm_name in ARM_NAMES:
        try:
            out = run_arm(arm_name, seed, shared=shared)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name}] "
                f"D1_AUC={out['D1_partition_AUC']:.3f} "
                f"D2_p@N_USE={out['D2_topK_precision_at_N_USE']:.3f} "
                f"D2_p@50={out['D2_topK_precision_at_50']:.3f} "
                f"D3_KM={out['D3_KM_quantile_gap_top10_bot10']:.3f} "
                f"rec_RETR={out['recall_old_RETRIEVED']:.3f} "
                f"rec_UNRETR={out['recall_old_UNRETRIEVED']:.3f} "
                f"cor={out['cor_importance_magnitude']:.3f} "
                f"n_down={out['n_downscaled']} "
                f"wall={out['wall_s']:.1f}s", flush=True,
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
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(N_QUERIES), "n_use": int(N_USE),
        "downscale_scale": DOWNSCALE_SCALE,
        "n_composite_queries": N_COMPOSITE_QUERIES,
        "composite_arity": COMPOSITE_ARITY,
        "n_prune_frac": float(N_PRUNE_FRAC),
        "n_edges_H": int(shared[3].n_edges()),
        "trace_total": float(np.sum(shared[6])),
        "n_retrieved": int(shared[4].shape[0]),
        "n_unretrieved": int(shared[5].shape[0]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (META_RULE_H + META_RULE_J + drill bands; verbatim v1)
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
            arm_names_got = [a.get("arm_name") for a in r.get("arms", [])]
            return ("HARD_FAIL",
                    f"HARD_FAIL: META_RULE_H cardinality_ok breach "
                    f"seed={r['seed']}: expected {expected_per_seed} arm "
                    f"entries, got {got} (arms={arm_names_got}) -- "
                    f"v1-bug-recurrence; partial may be stale from v1 run")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate violated.")

    def _agg(arm_name: str) -> Dict[str, float]:
        per = []
        for r in results:
            per.extend(_arms_by_name(r["arms"], arm_name))
        if not per:
            return {}
        aucs = [float(a.get("D1_partition_AUC", float("nan"))) for a in per]
        topks = [float(a.get("D2_topK_precision_at_N_USE", float("nan"))) for a in per]
        top50s = [float(a.get("D2_topK_precision_at_50", float("nan"))) for a in per]
        kms = [float(a.get("D3_KM_quantile_gap_top10_bot10", float("nan"))) for a in per]
        rec_retr = [float(a.get("recall_old_RETRIEVED", float("nan"))) for a in per]
        rec_unretr = [float(a.get("recall_old_UNRETRIEVED", float("nan"))) for a in per]
        cor = [float(a.get("cor_importance_magnitude", float("nan"))) for a in per]
        ndown = [int(a.get("n_downscaled", 0)) for a in per]
        mean_auc = float(np.nanmean(aucs))
        return {
            "mean_D1_AUC": mean_auc,
            "std_D1_AUC": float(np.nanstd(aucs)),
            "cv_D1_AUC": (float(np.nanstd(aucs) / max(abs(mean_auc), 1e-9))
                          if np.isfinite(mean_auc) else float("nan")),
            "mean_D2_topK_at_N_USE": float(np.nanmean(topks)),
            "mean_D2_topK_at_50": float(np.nanmean(top50s)),
            "mean_D3_KM_gap": float(np.nanmean(kms)),
            "mean_rec_RETRIEVED": float(np.nanmean(rec_retr)),
            "mean_rec_UNRETRIEVED": float(np.nanmean(rec_unretr)),
            "mean_cor_imp_W": float(np.nanmean(cor)),
            "mean_n_downscaled": float(np.mean(ndown)),
        }

    agg_rand = _agg("ARM_BASELINE_RANDOM_IMPORTANCE")
    agg_trace = _agg("ARM_TRACE_ONLY")

    summary = (
        f"alpha={ALPHA:.3f} mode={RUN_MODE} "
        f"RAND(D1_AUC={agg_rand.get('mean_D1_AUC', float('nan')):.3f}); "
        f"TRACE(D1_AUC={agg_trace.get('mean_D1_AUC', float('nan')):.3f},"
        f"cv={agg_trace.get('cv_D1_AUC', float('nan')):.3f},"
        f"D2_p@N_USE={agg_trace.get('mean_D2_topK_at_N_USE', float('nan')):.3f},"
        f"D2_p@50={agg_trace.get('mean_D2_topK_at_50', float('nan')):.3f},"
        f"D3_KM={agg_trace.get('mean_D3_KM_gap', float('nan')):.3f},"
        f"cor={agg_trace.get('mean_cor_imp_W', float('nan')):.3f},"
        f"n_down={agg_trace.get('mean_n_downscaled', 0):.0f})"
    )

    for name, a in [("RAND", agg_rand), ("TRACE", agg_trace)]:
        if not np.isfinite(a.get("mean_D1_AUC", float("nan"))):
            return ("HARD_FAIL",
                    f"HARD_FAIL: non-finite D1 AUC in {name}. {summary}")

    trace_auc = agg_trace["mean_D1_AUC"]
    trace_cv = agg_trace["cv_D1_AUC"]
    rand_auc = agg_rand["mean_D1_AUC"]
    trace_cor = agg_trace["mean_cor_imp_W"]
    trace_ndown = agg_trace["mean_n_downscaled"]

    if trace_ndown <= 0:
        return ("HARD_FAIL",
                f"HARD_FAIL: TRACE mechanism inert (n_downscaled=0). {summary}")
    if abs(trace_auc - rand_auc) < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: arms within 0.05 on D1_AUC "
                f"(spread={abs(trace_auc - rand_auc):.3f}). {summary}")
    if trace_cor >= 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: fairness gate cor(importance,|W|)="
                f"{trace_cor:.3f} >= 0.30. {summary}")
    if trace_auc < 0.55:
        return ("HARD_FAIL",
                f"HARD_FAIL: TRACE D1_AUC={trace_auc:.3f} < 0.55. {summary}")

    hp_auc = trace_auc >= 0.65
    hp_cv = trace_cv <= 0.05
    hp_lift = (trace_auc - rand_auc) >= 0.05
    hp_fired = trace_ndown > 0
    hp_fair = trace_cor < 0.30

    if all([hp_auc, hp_cv, hp_lift, hp_fired, hp_fair]):
        return ("HARD_PASS",
                f"HARD_PASS: TRACE-only-v2-arm-count-fix at alpha={ALPHA:.3f} "
                f"D1_AUC={trace_auc:.3f} >= 0.65, cv={trace_cv:.3f} <= 0.05, "
                f"lift={trace_auc - rand_auc:+.3f} >= 0.05, "
                f"fired, fair (cor={trace_cor:.3f}). HONEST-BOUND ship "
                f"per drill 2026-06-27. {summary}")

    mb_auc = trace_auc >= 0.55
    mb_cv = trace_cv <= 0.10
    if all([mb_auc, mb_cv, hp_fired, hp_fair]):
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: TRACE D1_AUC={trace_auc:.3f} above-chance "
                f"but PASS bands not cleared. hp_checks=[auc>=0.65:{hp_auc},"
                f"cv<=0.05:{hp_cv},lift>=0.05:{hp_lift},fired:{hp_fired},"
                f"fair:{hp_fair}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: did not clear PASS or MIDDLE. "
            f"hp_checks=[auc>=0.65:{hp_auc},cv<=0.05:{hp_cv},"
            f"lift>=0.05:{hp_lift},fired:{hp_fired},fair:{hp_fair}]. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main driver (v2: defensive partial-cleanup at startup)
# ---------------------------------------------------------------------------
# RULE_EXPERIMENT_CELLS_MUST_GUARD_MAIN_WITH___NAME___DUNDER (added 2026-06-27)
if __name__ == "__main__":
    out_dir = get_output_dir(ANCHOR_NAME)

    # v2 ARM-COUNT FIX: defensively scan existing partials for arm-count
    # mismatches before resumable_seeds loads them. Any partial whose arms
    # field has != 2 entries is stale and would re-trigger the v1 bug.
    if out_dir.exists():
        stale_count = 0
        for partial_path in out_dir.glob("partial_metrics_*.json"):
            try:
                partial_data = json.loads(partial_path.read_text(encoding="utf-8"))
                body = partial_data.get("body", partial_data)
                n_arms_in_partial = len(body.get("arms", []))
                if n_arms_in_partial != 2:
                    print(f"[v2-defensive] STALE partial detected at {partial_path.name}: "
                          f"n_arms={n_arms_in_partial} != 2; deleting", flush=True)
                    partial_path.unlink()
                    stale_count += 1
            except (json.JSONDecodeError, OSError) as e:
                print(f"[v2-defensive] partial {partial_path.name} unreadable: {e}; "
                      f"deleting", flush=True)
                try:
                    partial_path.unlink()
                except OSError:
                    pass
                stale_count += 1
        if stale_count > 0:
            print(f"[v2-defensive] removed {stale_count} stale partials; "
                  f"clean start", flush=True)

    run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
                  "alpha": float(ALPHA), "J": N_COMPOSITE_QUERIES,
                  "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
        f"running {remaining}", flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(
            f"[seed={seed}] v3.2-v2 N={N} alpha={ALPHA:.3f} "
            f"J_comp={N_COMPOSITE_QUERIES} arity={COMPOSITE_ARITY} "
            f"N_USE={N_USE} mode={RUN_MODE} arms=TRACE-only-v2 "
            f"(EXACTLY 2 arms enforced)...", flush=True,
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
            f"N_USE={N_USE} mode={RUN_MODE} arms=TRACE-only-v2 "
            f"N_PRUNE_FRAC={N_PRUNE_FRAC} v2_arm_count_fix=true"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
        "alpha": float(ALPHA),
        "n_seeds": len(SEEDS), "n_queries": N_QUERIES, "n_use": int(N_USE),
        "n_composite_queries": N_COMPOSITE_QUERIES,
        "composite_arity": COMPOSITE_ARITY,
        "downscale_scale": float(DOWNSCALE_SCALE),
        "n_prune_frac": float(N_PRUNE_FRAC),
        "run_mode": RUN_MODE,
        "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
        "expected_arms_per_seed": len(ARM_NAMES),
        "v2_arm_count_fix": True,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "trace_total": r.get("trace_total"),
                "n_edges_H": r.get("n_edges_H"),
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
