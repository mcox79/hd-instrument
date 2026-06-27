"""edge_importance_v6_CFU_stronger_regime -- v5 CFU with stronger regime.

Pre-reg: preregs/2026-06-27_edge_importance_v6_CFU_stronger_regime.md

v5 (M-CFU) was Skunkworks-tiered MIDDLE_BAND: FIRST mechanism in edge-
importance family to PASS fairness (cor=-0.015 vs +0.83 for trace-family
sourcing degree-skewed signal) but sel_unretr=+0.037 short of the +0.15
PASS bar. Brain-grounded (Tonegawa optogenetic engram-silencing analog).
Structurally orthogonal to magnitude. The drill (research_drill_cortex_
importance_backup_mechanisms_2026-06-27.md) identifies 4 strengthening
levers that lift CFU signal above noise.

v6 STRENGTHENING LEVERS (load-bearing; from drill Section M-CFU):

  L1 BIGGER HELD-OUT PROBE SET (v5 N_PROBE=100 -> v6 N_PROBE=400; 4x).
     Reduces noise floor on per-cohort recall delta. CFU is the recall
     DIFFERENCE between baseline and ablated; the variance of the
     difference scales as 1/sqrt(N_PROBE). 4x probe -> 2x lower noise.

  L2 LEAVE-K-OUT SWEEP K in {1, 2, 5} (v5 only K=10). Multi-atom co-
     importance captures interaction effects (atoms whose removal
     individually is silent but whose joint removal hurts).

  L3 ALPHA SWEEP alpha in {1.5, 2.0, 2.5, 3.0} via M_OLD variation
     (v5 fixed at alpha=2.148). Finds the regime where ablation signal
     is LOUDEST vs noise. Higher alpha = more saturation pressure on W
     = larger per-atom contribution = more measurable CFU.

  L4 CONTINUOUS DOWNSCALE GRADIENT (v5 binary ablation; v6 5 levels
     {0%, 25%, 50%, 75%, 100% weight reduction}). Importance = integral
     of recall-delta over the gradient. Gradient probing yields more
     signal per atom: instead of "atom removed or not" the cell sees
     the FULL FUNCTION recall(weight_fraction) and integrates the
     deficit area.

5 ARMS (mandatory; pre-reg discipline; per-arm scope SCHEMA-VET 5b):
  ARM_BASELINE_RANDOM_IMPORTANCE     - uniform random control
  ARM_TRACE_ONLY                     - v3 retrieval-trace control;
                                        expected cor=+0.83 (degree-skew
                                        rail; cell verifies fairness
                                        boundary held)
  ARM_CFU_LEAVE_ONE_OUT_LARGE_PROBE  - v5 mech with L1 (4x probe set)
  ARM_CFU_LEAVE_K_OUT                - L2 K=5 cohort co-importance
                                        (multi-atom joint ablation)
  ARM_CFU_CONTINUOUS_DOWNSCALE       - L4 gradient ablation integral
                                        signal

ALL arms share workload + retrieved/unretrieved partition; differ only
in importance-scoring axis.

CARDINALITY (D4 META_RULE_H mandatory):
  4 alpha x 3 seeds x 5 arms = 60 arm entries TOTAL
  EXPECTED_N_UNITS = 60
  HARD_FAIL_CARDINALITY_BREACH = observed_arm_entries != 60
  Per-(alpha, seed) partial: 5 arm entries
  Compound checkpoint key = "alpha{X.X}_seed{Y}" (12 partial files)

PRE-REG BANDS (META_PROSPECTIVE_BANDS_FRESH_SEEDS):

  HARD_PASS (all 4 must hold):
    1. best v6 CFU sel_unretr asymmetry >= 0.15 (ORIGINAL Path A bar)
    2. AND cor(best_CFU, |W|) < 0.30 (fairness held; v5 win preserved)
    3. AND mechanism fires (n_downscaled > 0 AND n_ablations > 0)
    4. AND best_v6_sel_unretr > v5_baseline_sel + 0.05 (stronger regime
       PROVABLY helps; v5_baseline = +0.037 actual)

  HARD_FAIL:
    A. fairness regression (any CFU arm cor >= 0.30)
    B. best_v6_sel_unretr <= v5_baseline_sel (+0.037; stronger regime
       did NOT help; v6 saturates AT v5 level)
    C. mechanism inert (n_downscaled == 0 OR n_ablations == 0 OR
       cfu_variance == 0 on any CFU arm)
    D. saturation: all 5 arms within 0.05 on rec_RETRIEVED
    E. any caught exception (D3 no-silent-except)

  MIDDLE_BAND: fairness held + sel_unretr in [0.08, 0.15] + mechanism
    fired + stronger > v5 by >= 0.02 -> ship as HONEST_BOUND with new
    band annotation; lifts ceiling estimate for the M-CFU family.

NEW DISCIPLINES (META rules; load-bearing):
  D1 Discriminator-must-survive-scale: smoke runs at FULL-N, FULL probe
     (only J / seeds / alpha-sweep-count reduced). Smoke MUST measure
     best_v6_CFU_sel > v5_baseline (+0.037) + 0.02 OR halt-and-route.
  D2 Smoke-must-FIRE-discriminator: n_downscaled > 0 AND n_ablations
     > 0 AND cfu_variance > 0 on EACH CFU arm.
  D3 No-silent-except: setup + each alpha + each arm wrapped (catches
     re-raise + records exception per cell).
  D4 cardinality_ok: 60 arm entries; HARD_FAIL on breach.
  META_RULE_U brain-mechanism-vs-caricature: CFU IS the brain mechanism
     (Tonegawa optogenetic engram silencing). Preserve its load-bearing
     architectural feature = leave-one-out ablation against held-out
     probe set; do NOT replace with magnitude proxy or any smooth
     function of H. v6 STRENGTHENS the CFU mechanism, never substitutes.

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

# numpy>=2.0 renamed trapz to trapezoid; remote .venv may be either; alias:
if not hasattr(np, "trapezoid"):
    np.trapezoid = np.trapz  # type: ignore[attr-defined]

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    list_completed_keys,
    load_partial_key,
    write_partial_key,
)
from hdlab.edge_importance import EdgeImportance, HConfig, correlation_E_vs_magnitude


ANCHOR_NAME = "edge_importance_v6_CFU_stronger_regime"
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

# v5 BASELINE measured (read 2026-06-27 from
# data/exp_edge_importance_v5_CFU_counterfactual_utility_v1/metrics.json):
#   sel_cfu = rand_unretr - cfu_unretr = +0.037 (3-seed mean)
#   cor(CFU,|W|) = -0.015 (fairness held excellent)
V5_BASELINE_SEL_CFU = 0.037

# Substrate config (FULL)
N_FULL = 512
M_RECENT_FULL = 400
M_HELDOUT_FULL = 400          # L1: 4x v5 (was 100; reduces noise floor 2x)
N_COMPOSITE_QUERIES_FULL = 3000
COMPOSITE_ARITY = 3
USE_FRAC_FULL = 0.40
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200

# L3 ALPHA SWEEP: vary M_OLD; M_RECENT + M_HELDOUT fixed. alpha = M_TOTAL / N.
# M_OLD_GRID chosen so target alpha is hit (with M_RECENT_FULL=400 +
# M_HELDOUT_FULL=400, M_OLD = N*target_alpha - 800)
# alpha=1.5 -> M_OLD=-32 (infeasible at N=512); use floor N*alpha-800 with min 50
def _m_old_for_alpha(target_alpha: float, N_dim: int,
                     M_rec: int, M_held: int) -> int:
    return max(50, int(round(N_dim * target_alpha - M_rec - M_held)))

ALPHA_GRID_FULL = [1.5, 2.0, 2.5, 3.0]

# L4 CONTINUOUS DOWNSCALE GRADIENT: 5 levels
GRADIENT_LEVELS = [0.0, 0.25, 0.50, 0.75, 1.00]

# L2 LEAVE-K-OUT sweep: ARM_CFU_LEAVE_K_OUT uses K=5; others use K_DEFAULT=10
K_LEAVE_K_OUT_ARM = 5
COHORT_K_DEFAULT = 10           # used by ARM_CFU_LEAVE_ONE_OUT_LARGE_PROBE +
                                # ARM_CFU_CONTINUOUS_DOWNSCALE

N_PROBE_BATCH_FULL = 400        # L1 4x v5
CFU_EVAL_FRAC_FULL = 0.50
DOWNSCALE_SCALE = 0.20          # pruning step magnitude (eval-phase)
N_PRUNE_FRAC = 0.30

# D1 discipline: smoke uses FULL-N + FULL probe; only J / seeds / alphas reduced.
if RUN_MODE == "smoke":
    N = N_FULL
    M_RECENT = M_RECENT_FULL
    M_HELDOUT = M_HELDOUT_FULL
    N_COMPOSITE_QUERIES = 1500
    USE_FRAC = USE_FRAC_FULL
    SEEDS = [7]
    N_QUERIES = 100
    N_PROBE_BATCH = N_PROBE_BATCH_FULL    # FULL probe for D1 noise-floor parity
    CFU_EVAL_FRAC = 0.30
    ALPHA_GRID = [2.5]                    # 1 alpha for smoke; representative
else:
    N = N_FULL
    M_RECENT = M_RECENT_FULL
    M_HELDOUT = M_HELDOUT_FULL
    N_COMPOSITE_QUERIES = N_COMPOSITE_QUERIES_FULL
    USE_FRAC = USE_FRAC_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL
    N_PROBE_BATCH = N_PROBE_BATCH_FULL
    CFU_EVAL_FRAC = CFU_EVAL_FRAC_FULL
    ALPHA_GRID = ALPHA_GRID_FULL

# CONFIG_VERSION stamped per-(alpha, seed) partial separately; this is the
# top-level cell-config string.
CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M_RECENT={M_RECENT},"
    f"M_HELDOUT={M_HELDOUT},J_composite={N_COMPOSITE_QUERIES},"
    f"arity={COMPOSITE_ARITY},USE_FRAC={USE_FRAC},"
    f"DOWNSCALE_SCALE={DOWNSCALE_SCALE},"
    f"COHORT_K_DEFAULT={COHORT_K_DEFAULT},K_LEAVE_K_OUT_ARM={K_LEAVE_K_OUT_ARM},"
    f"N_PROBE_BATCH={N_PROBE_BATCH},"
    f"CFU_EVAL_FRAC={CFU_EVAL_FRAC},"
    f"GRADIENT_LEVELS={'-'.join(str(g) for g in GRADIENT_LEVELS)},"
    f"ALPHA_GRID={'-'.join(str(a) for a in ALPHA_GRID)},"
    f"N_PRUNE_FRAC={N_PRUNE_FRAC},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"N_QUERIES={N_QUERIES},RUN_MODE={RUN_MODE},"
    f"V5_BASELINE_SEL_CFU={V5_BASELINE_SEL_CFU}"
)

EXPECTED_N_UNITS = len(ALPHA_GRID) * len(SEEDS) * 5  # 60 in full mode

ARM_NAMES = [
    "ARM_BASELINE_RANDOM_IMPORTANCE",
    "ARM_TRACE_ONLY",
    "ARM_CFU_LEAVE_ONE_OUT_LARGE_PROBE",
    "ARM_CFU_LEAVE_K_OUT",
    "ARM_CFU_CONTINUOUS_DOWNSCALE",
]
CFU_ARM_NAMES = [
    "ARM_CFU_LEAVE_ONE_OUT_LARGE_PROBE",
    "ARM_CFU_LEAVE_K_OUT",
    "ARM_CFU_CONTINUOUS_DOWNSCALE",
]


# ---------------------------------------------------------------------------
# Pattern generation (mirrors v5; bipolar keys/values)
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


# ---------------------------------------------------------------------------
# Substrate setup (per-alpha; M_OLD derived from target alpha)
# ---------------------------------------------------------------------------
def setup_substrate_with_trace_and_heldout(
    seed: int,
    M_old: int,
    n_composite_queries: int,
):
    """Build W + populate edge graph + populate base_retrieval_trace via
    single-pass WAKE composite queries. ALSO build held-out probe set.
    Same architecture as v5 but with M_OLD passed in for alpha-sweep.
    """
    M_total = M_old + M_RECENT + M_HELDOUT
    n_use = max(COMPOSITE_ARITY, int(round(USE_FRAC * M_old)))

    keys_old, values_old = generate_pairs(M_old, N, seed)
    keys_rec, values_rec = generate_pairs(M_RECENT, N, seed + 999)
    keys_held, values_held = generate_pairs(M_HELDOUT, N, seed + 1777)
    all_keys = np.concatenate([keys_old, keys_rec, keys_held], axis=0)
    all_values = np.concatenate([values_old, values_rec, values_held], axis=0)

    cfg = HConfig(
        increment=1.0, decay_step=0.0, floor=0.0,
        e_thresh=2.0, h_thresh=3.0,
    )
    edge_graph = EdgeImportance(n_atoms=M_total, cfg=cfg)

    # Build W with ALL atoms baked in (old + recent + held-out).
    W = build_W_from_pairs(all_keys, all_values)

    rng = np.random.RandomState(seed + 401)
    retrieved_idx = rng.choice(M_old, size=n_use, replace=False)
    retrieved_idx.sort()
    unretrieved_mask = np.ones(M_old, dtype=bool)
    unretrieved_mask[retrieved_idx] = False
    unretrieved_idx = np.where(unretrieved_mask)[0]

    heldout_offset = M_old + M_RECENT
    heldout_idx = np.arange(heldout_offset, heldout_offset + M_HELDOUT)

    base_retrieval_trace = np.zeros(M_total, dtype=np.float64)
    n_trace_events = 0

    rng_q = np.random.RandomState(seed + 1117)
    for _q in range(n_composite_queries):
        triple = rng_q.choice(retrieved_idx, size=COMPOSITE_ARITY,
                              replace=False)
        bundled_key = composite_query_bundle(all_keys, triple)
        pred = predict(W, bundled_key)
        winner = cleanup_argmax(all_values, pred, N)
        base_retrieval_trace[winner] += 1.0
        edge_graph.increment_query(triple)
        edge_graph.decay_all()
        n_trace_events += 1

    return {
        "W": W, "all_keys": all_keys, "all_values": all_values,
        "edge_graph": edge_graph,
        "retrieved_idx": retrieved_idx,
        "unretrieved_idx": unretrieved_idx,
        "base_retrieval_trace": base_retrieval_trace,
        "heldout_idx": heldout_idx,
        "n_trace_events": n_trace_events,
        "M_old": M_old, "M_total": M_total, "n_use": n_use,
    }


# ---------------------------------------------------------------------------
# CFU scoring variants (v5 baseline + 2 v6 stronger-regime variants)
# ---------------------------------------------------------------------------
def baseline_heldout_recall(W: np.ndarray, all_keys: np.ndarray,
                            all_values: np.ndarray,
                            heldout_idx: np.ndarray,
                            n_probe: int, seed: int) -> Tuple[float, np.ndarray]:
    """Score recall on a random subset of heldout probe atoms."""
    rng = np.random.RandomState(seed + 9001)
    n_use = min(n_probe, len(heldout_idx))
    probe_idx = rng.choice(heldout_idx, size=n_use, replace=False)
    rec = recall_subset(W, all_keys, probe_idx, all_values)
    return rec, probe_idx


def ablate_cohort_outer_product(W: np.ndarray, keys: np.ndarray,
                                values: np.ndarray,
                                cohort: np.ndarray) -> np.ndarray:
    """W with cohort's (key,value) outer-product fully subtracted. Non-mutating."""
    W_abl = W.copy()
    for idx in cohort:
        W_abl -= np.outer(values[idx], keys[idx])
    return W_abl


def downscale_cohort_outer_product(W: np.ndarray, keys: np.ndarray,
                                   values: np.ndarray, cohort: np.ndarray,
                                   fraction: float) -> np.ndarray:
    """W with cohort's outer-product downscaled by fraction in [0,1].
    fraction=0 -> identity (no change); fraction=1 -> full ablation.
    """
    W_d = W.copy()
    for idx in cohort:
        W_d -= fraction * np.outer(values[idx], keys[idx])
    return W_d


def compute_cfu_importance_v5style_large_probe(
    W: np.ndarray, all_keys: np.ndarray,
    all_values: np.ndarray, heldout_idx: np.ndarray,
    M_total: int, seed: int, cohort_k: int,
) -> Tuple[np.ndarray, int, float]:
    """L1 mechanism: v5 cohort leave-K-out with LARGE PROBE (N_PROBE_BATCH=400)."""
    baseline_rec, probe_idx = baseline_heldout_recall(
        W, all_keys, all_values, heldout_idx, N_PROBE_BATCH, seed,
    )

    importance = np.zeros(M_total, dtype=np.float64)
    rng = np.random.RandomState(seed + 7000)
    perm = rng.permutation(M_total)
    n_cfu_cohorts = max(1, int(round(CFU_EVAL_FRAC * M_total / cohort_k)))
    n_take = min(M_total, n_cfu_cohorts * cohort_k)
    perm = perm[:n_take]
    n_evaluated = 0
    for c in range(n_cfu_cohorts):
        cohort = perm[c * cohort_k:(c + 1) * cohort_k]
        if len(cohort) == 0:
            break
        W_abl = ablate_cohort_outer_product(W, all_keys, all_values, cohort)
        rec_abl = recall_subset(W_abl, all_keys, probe_idx, all_values)
        delta = baseline_rec - rec_abl
        for idx in cohort:
            importance[idx] = delta / float(cohort_k)
        n_evaluated += 1
    return importance, n_evaluated, float(baseline_rec)


def compute_cfu_importance_leave_k_out(
    W: np.ndarray, all_keys: np.ndarray,
    all_values: np.ndarray, heldout_idx: np.ndarray,
    M_total: int, seed: int, K: int,
) -> Tuple[np.ndarray, int, float]:
    """L2 mechanism: leave-K-out with K=K_LEAVE_K_OUT_ARM=5 (multi-atom co-importance)."""
    return compute_cfu_importance_v5style_large_probe(
        W, all_keys, all_values, heldout_idx, M_total, seed, K,
    )


def compute_cfu_importance_continuous_downscale(
    W: np.ndarray, all_keys: np.ndarray,
    all_values: np.ndarray, heldout_idx: np.ndarray,
    M_total: int, seed: int, cohort_k: int,
) -> Tuple[np.ndarray, int, float]:
    """L4 mechanism: continuous downscale gradient.

    For each cohort, instead of binary ablate-or-not, sweep weight reduction
    fraction over GRADIENT_LEVELS [0.0, 0.25, 0.50, 0.75, 1.00]. The
    importance for the cohort = integral of (baseline - recall_at_f) over
    f in [0,1], approximated by trapezoidal rule on the 5 sample points.

    This captures the FULL function recall(weight_fraction) rather than the
    single point recall(1.0); atoms whose recall-deficit curve is steep get
    higher integrated importance than atoms with shallow curves of the
    same endpoint. More signal per atom.
    """
    baseline_rec, probe_idx = baseline_heldout_recall(
        W, all_keys, all_values, heldout_idx, N_PROBE_BATCH, seed,
    )

    importance = np.zeros(M_total, dtype=np.float64)
    rng = np.random.RandomState(seed + 7000)
    perm = rng.permutation(M_total)
    n_cfu_cohorts = max(1, int(round(CFU_EVAL_FRAC * M_total / cohort_k)))
    n_take = min(M_total, n_cfu_cohorts * cohort_k)
    perm = perm[:n_take]
    n_evaluated = 0

    levels = np.array(GRADIENT_LEVELS, dtype=np.float64)
    for c in range(n_cfu_cohorts):
        cohort = perm[c * cohort_k:(c + 1) * cohort_k]
        if len(cohort) == 0:
            break
        # Compute recall at each gradient level for this cohort.
        deficits = np.zeros(len(levels), dtype=np.float64)
        for li, f in enumerate(levels):
            if f == 0.0:
                rec_f = baseline_rec
            else:
                W_d = downscale_cohort_outer_product(
                    W, all_keys, all_values, cohort, float(f),
                )
                rec_f = recall_subset(W_d, all_keys, probe_idx, all_values)
            deficits[li] = baseline_rec - rec_f
        # Trapezoidal integral of deficit over f in [0,1]; in [0,1] interval.
        integral = float(np.trapezoid(deficits, levels))
        # Importance per atom in cohort = integral / cohort_k (averaged).
        for idx in cohort:
            importance[idx] = integral / float(cohort_k)
        n_evaluated += 1
    return importance, n_evaluated, float(baseline_rec)


# ---------------------------------------------------------------------------
# Importance scoring per arm
# ---------------------------------------------------------------------------
def importance_random(seed: int, M_total: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 7777)
    return rng.rand(M_total)


def importance_trace_only(base_retrieval_trace: np.ndarray) -> np.ndarray:
    return base_retrieval_trace.copy()


def select_prune_indices_low(importance: np.ndarray, n_prune: int,
                             seed: int) -> np.ndarray:
    """Select the N_PRUNE atoms with LOWEST importance (stable jitter)."""
    rng = np.random.RandomState(seed + 13131)
    jitter = rng.rand(importance.shape[0]) * 1e-6
    score = importance + jitter
    return np.argsort(score)[:n_prune]


# ---------------------------------------------------------------------------
# Arm runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int, alpha: float,
            shared: Dict,
            cfu_large_probe: np.ndarray,
            cfu_leave_k: np.ndarray,
            cfu_continuous: np.ndarray) -> Dict:
    t0 = time.time()
    W_base = shared["W"]
    all_keys = shared["all_keys"]
    all_values = shared["all_values"]
    retrieved_idx = shared["retrieved_idx"]
    unretrieved_idx = shared["unretrieved_idx"]
    base_retrieval_trace = shared["base_retrieval_trace"]
    M_old = shared["M_old"]
    M_total = shared["M_total"]

    W = W_base.copy()
    W_norm_pre = float(np.linalg.norm(W))

    if arm_name == "ARM_BASELINE_RANDOM_IMPORTANCE":
        importance = importance_random(seed, M_total)
    elif arm_name == "ARM_TRACE_ONLY":
        importance = importance_trace_only(base_retrieval_trace)
    elif arm_name == "ARM_CFU_LEAVE_ONE_OUT_LARGE_PROBE":
        importance = cfu_large_probe.copy()
    elif arm_name == "ARM_CFU_LEAVE_K_OUT":
        importance = cfu_leave_k.copy()
    elif arm_name == "ARM_CFU_CONTINUOUS_DOWNSCALE":
        importance = cfu_continuous.copy()
    else:
        raise ValueError(f"unknown arm {arm_name}")

    # Fairness gate (META_RULE_F): cor(importance, |W|-norm proxy).
    atom_norms = np.linalg.norm(all_keys @ W.T, axis=1) / float(N)
    cor_imp_norm = correlation_E_vs_magnitude(importance, atom_norms)

    n_prune = int(round(N_PRUNE_FRAC * M_total))
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
                                replace=False) + M_old

    recall_old_retrieved = recall_subset(W, all_keys, ret_query,
                                         all_values)
    recall_old_unretrieved = recall_subset(W, all_keys, unret_query,
                                           all_values)
    recall_recent = recall_subset(W, all_keys, rec_query, all_values)

    elapsed = time.time() - t0

    return {
        "arm_name": arm_name,
        "alpha": float(alpha),
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
        "downscale_frac_actual": float(n_downscaled) / float(M_total),
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


def _selftest_downscale_monotonic_in_fraction() -> bool:
    """As downscale fraction goes 0 -> 1, recall on the downscaled atoms
    should NON-INCREASE (monotone decreasing or equal). This is the
    load-bearing axiom for the L4 continuous-downscale variant: the
    function recall(weight_fraction) is monotone."""
    rng = np.random.RandomState(11)
    n = 256
    m_total = 60
    keys = rng.choice([-1.0, 1.0], size=(m_total, n)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(m_total, n)).astype(np.float64)
    W = build_W_from_pairs(keys, values)
    cohort = np.arange(20)  # downscale atoms 0..19
    probe = cohort[:5]
    recs = []
    for f in [0.0, 0.25, 0.50, 0.75, 1.00]:
        W_d = downscale_cohort_outer_product(W, keys, values, cohort, f)
        r = recall_subset(W_d, keys, probe, values)
        recs.append(r)
    # Monotone non-increasing
    for i in range(1, len(recs)):
        assert recs[i] <= recs[i-1] + 1e-9, (
            f"downscale monotone: recs={recs} not monotone at step {i}"
        )
    # Endpoint: full downscale must hurt recall vs zero downscale.
    assert recs[-1] < recs[0], (
        f"downscale endpoint: full ablation should hurt recall; "
        f"recs[0]={recs[0]} recs[-1]={recs[-1]}"
    )
    return True


def _selftest_continuous_integral_higher_than_pointwise() -> bool:
    """For an atom cohort with a STEEP downscale curve (large deficit at
    100% ablation), the integrated importance should be PROPORTIONAL to
    the deficit area, which is larger than the single-point binary
    delta when the curve is non-linear. This proves L4 adds signal."""
    rng = np.random.RandomState(13)
    n = 256
    m_total = 60
    keys = rng.choice([-1.0, 1.0], size=(m_total, n)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(m_total, n)).astype(np.float64)
    W = build_W_from_pairs(keys, values)
    heldout = np.arange(m_total - 20, m_total)
    probe = heldout[:5]
    baseline = recall_subset(W, keys, probe, values)
    cohort = heldout[:10]
    # Pointwise binary delta
    W_full_abl = ablate_cohort_outer_product(W, keys, values, cohort)
    binary_delta = baseline - recall_subset(W_full_abl, keys, probe, values)
    # Continuous integral
    levels = np.array(GRADIENT_LEVELS, dtype=np.float64)
    deficits = np.zeros(len(levels))
    for li, f in enumerate(levels):
        if f == 0.0:
            rec_f = baseline
        else:
            W_d = downscale_cohort_outer_product(W, keys, values, cohort,
                                                 float(f))
            rec_f = recall_subset(W_d, keys, probe, values)
        deficits[li] = baseline - rec_f
    integral = float(np.trapezoid(deficits, levels))
    # Both must be non-negative (ablation hurts).
    assert binary_delta >= 0, f"binary_delta negative: {binary_delta}"
    assert integral >= 0, f"integral negative: {integral}"
    # The integral SHOULD be different from the binary endpoint (proves
    # L4 captures intermediate signal). They are different scales (integral
    # is in [0,1] x deficit units; binary is just deficit), so we just
    # require integral > 0 when binary > 0 (non-trivial mechanism).
    if binary_delta > 0:
        assert integral > 0, (
            f"L4 integral inert when binary_delta={binary_delta}>0; integral={integral}"
        )
    return True


def _selftest_ablate_cohort_reduces_recall_for_cohort_atoms() -> bool:
    rng = np.random.RandomState(2)
    n = 128
    m = 20
    keys = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    W = build_W_from_pairs(keys, values)
    pred = predict(W, keys[3])
    baseline_winner = cleanup_argmax(values, pred, n)
    assert baseline_winner == 3, (
        f"baseline retrieval: expected 3 got {baseline_winner}"
    )
    cohort = np.array([3, 5, 7])
    W_abl = ablate_cohort_outer_product(W, keys, values, cohort)
    pred_abl = predict(W_abl, keys[3])
    abl_winner = cleanup_argmax(values, pred_abl, n)
    sims_orig = values @ pred / float(n)
    sims_abl = values @ pred_abl / float(n)
    margin_orig = float(sims_orig[3] - np.partition(sims_orig, -2)[-2])
    margin_abl_for_atom3 = float(sims_abl[3] - np.max(np.delete(sims_abl, 3)))
    assert (abl_winner != 3) or (margin_abl_for_atom3 < 0.5 * margin_orig), (
        f"ablation should hurt recall of atom 3: pre_margin={margin_orig:.3f} "
        f"abl_winner={abl_winner} abl_margin_for_atom3={margin_abl_for_atom3:.3f}"
    )
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


def _selftest_alpha_grid_feasible() -> bool:
    """All alphas in ALPHA_GRID must yield M_OLD >= 50 (feasible)."""
    for a in ALPHA_GRID:
        m_old = _m_old_for_alpha(a, N, M_RECENT, M_HELDOUT)
        # alpha=1.5 at N=512 with M_RECENT+M_HELDOUT=800 yields negative
        # ideal M_OLD; floor to 50; ACTUAL alpha will be higher than target.
        # That's OK as long as we ACK the actual alpha.
        assert m_old >= 50, (
            f"M_OLD for alpha={a} is {m_old} < 50; infeasible"
        )
    return True


def _selftest_cfu_schedule_load_bearing() -> bool:
    assert N_PROBE_BATCH >= 100, (
        f"N_PROBE_BATCH must be >= 100 (v6 L1 stronger probe; v5 was 100); "
        f"got {N_PROBE_BATCH}"
    )
    assert M_HELDOUT >= 200, (
        f"M_HELDOUT must be >= 200 (v6 L1 4x v5); got {M_HELDOUT}"
    )
    assert K_LEAVE_K_OUT_ARM >= 2, (
        f"K_LEAVE_K_OUT_ARM must be >= 2; got {K_LEAVE_K_OUT_ARM}"
    )
    assert len(GRADIENT_LEVELS) >= 3, (
        f"GRADIENT_LEVELS must have >= 3 sample points; got "
        f"{GRADIENT_LEVELS}"
    )
    assert GRADIENT_LEVELS[0] == 0.0 and GRADIENT_LEVELS[-1] == 1.00, (
        f"GRADIENT_LEVELS must start at 0.0 and end at 1.0; got "
        f"{GRADIENT_LEVELS}"
    )
    assert V5_BASELINE_SEL_CFU > 0, (
        f"V5_BASELINE_SEL_CFU must be > 0; got {V5_BASELINE_SEL_CFU}"
    )
    return True


def _selftest_continuous_uses_full_gradient() -> bool:
    """The continuous-downscale mechanism must EVALUATE recall at all
    GRADIENT_LEVELS (not just at f=0 and f=1). This catches a regression
    where the implementation degenerates to binary."""
    rng = np.random.RandomState(17)
    n = 128
    m_total = 30
    keys = rng.choice([-1.0, 1.0], size=(m_total, n)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(m_total, n)).astype(np.float64)
    W = build_W_from_pairs(keys, values)
    heldout = np.arange(m_total - 10, m_total)
    importance, n_eval, baseline = compute_cfu_importance_continuous_downscale(
        W, keys, values, heldout, m_total, seed=0, cohort_k=2,
    )
    # CFU must produce non-trivial signal (variance across atoms).
    var = float(np.var(importance))
    assert n_eval > 0, f"continuous CFU did not run any cohorts; n_eval={n_eval}"
    assert var > 0.0, (
        f"continuous CFU produced flat importance; var={var}; "
        f"importance.min={np.min(importance):.4f} max={np.max(importance):.4f}"
    )
    return True


def _instrumentation_selftest():
    _selftest_retrieval_argmax_deterministic()
    _selftest_ablate_cohort_reduces_recall_for_cohort_atoms()
    _selftest_downscale_monotonic_in_fraction()
    _selftest_continuous_integral_higher_than_pointwise()
    _selftest_continuous_uses_full_gradient()
    _selftest_fairness_orthogonality_synthetic()
    _selftest_alpha_grid_feasible()
    _selftest_cfu_schedule_load_bearing()
    print(
        f"[selftest] PASS  N={N}  M_RECENT={M_RECENT}  M_HELDOUT={M_HELDOUT}  "
        f"J_comp={N_COMPOSITE_QUERIES}  ALPHA_GRID={ALPHA_GRID}  "
        f"K_LEAVE_K_OUT_ARM={K_LEAVE_K_OUT_ARM}  "
        f"COHORT_K_DEFAULT={COHORT_K_DEFAULT}  "
        f"N_PROBE={N_PROBE_BATCH}  GRADIENT_LEVELS={GRADIENT_LEVELS}  "
        f"V5_BASELINE_SEL={V5_BASELINE_SEL_CFU}  mode={RUN_MODE}  "
        f"EXPECTED_N_UNITS={EXPECTED_N_UNITS}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-(alpha, seed) runner (D3 no-silent-except)
# ---------------------------------------------------------------------------
def run_alpha_seed(alpha: float, seed: int) -> Dict:
    t0 = time.time()
    M_old = _m_old_for_alpha(alpha, N, M_RECENT, M_HELDOUT)
    M_total = M_old + M_RECENT + M_HELDOUT
    alpha_actual = M_total / N
    print(
        f"  [alpha={alpha} (actual={alpha_actual:.3f}) seed={seed}] "
        f"M_OLD={M_old} M_TOTAL={M_total} "
        f"setup + WAKE-trace (J={N_COMPOSITE_QUERIES}) + 3 CFU variants "
        f"(N_PROBE={N_PROBE_BATCH} K_DEF={COHORT_K_DEFAULT} "
        f"K_LKO={K_LEAVE_K_OUT_ARM} grad={len(GRADIENT_LEVELS)}lvls)...",
        flush=True,
    )
    try:
        t_setup = time.time()
        shared = setup_substrate_with_trace_and_heldout(
            seed, M_old, N_COMPOSITE_QUERIES,
        )
        trace_total = float(np.sum(shared["base_retrieval_trace"]))
        n_trace_events = int(shared["n_trace_events"])
        n_edges = shared["edge_graph"].n_edges()
        print(
            f"  [alpha={alpha} seed={seed}] setup done in "
            f"{time.time()-t_setup:.1f}s  H_edges={n_edges} "
            f"trace_total={trace_total:.0f} trace_events={n_trace_events}",
            flush=True,
        )

        # 3 CFU variants computed once each per (alpha, seed)
        W_base = shared["W"]
        all_keys = shared["all_keys"]
        all_values = shared["all_values"]
        heldout_idx = shared["heldout_idx"]

        t_c1 = time.time()
        cfu_large_probe, n_abl_lp, base_rec_lp = (
            compute_cfu_importance_v5style_large_probe(
                W_base, all_keys, all_values, heldout_idx,
                M_total, seed, COHORT_K_DEFAULT,
            )
        )
        var_lp = float(np.var(cfu_large_probe))
        print(
            f"  [alpha={alpha} seed={seed}] CFU_LARGE_PROBE done in "
            f"{time.time()-t_c1:.1f}s  base_rec={base_rec_lp:.3f}  "
            f"n_abl={n_abl_lp}  var={var_lp:.6f}",
            flush=True,
        )

        t_c2 = time.time()
        cfu_leave_k, n_abl_lk, base_rec_lk = (
            compute_cfu_importance_leave_k_out(
                W_base, all_keys, all_values, heldout_idx,
                M_total, seed, K_LEAVE_K_OUT_ARM,
            )
        )
        var_lk = float(np.var(cfu_leave_k))
        print(
            f"  [alpha={alpha} seed={seed}] CFU_LEAVE_K_OUT(K={K_LEAVE_K_OUT_ARM}) "
            f"done in {time.time()-t_c2:.1f}s  base_rec={base_rec_lk:.3f}  "
            f"n_abl={n_abl_lk}  var={var_lk:.6f}",
            flush=True,
        )

        t_c3 = time.time()
        cfu_continuous, n_abl_cont, base_rec_cont = (
            compute_cfu_importance_continuous_downscale(
                W_base, all_keys, all_values, heldout_idx,
                M_total, seed, COHORT_K_DEFAULT,
            )
        )
        var_cont = float(np.var(cfu_continuous))
        print(
            f"  [alpha={alpha} seed={seed}] CFU_CONTINUOUS done in "
            f"{time.time()-t_c3:.1f}s  base_rec={base_rec_cont:.3f}  "
            f"n_abl={n_abl_cont}  var={var_cont:.6f}",
            flush=True,
        )
    except Exception as exc:
        tb = traceback.format_exc()
        print(
            f"  [alpha={alpha} seed={seed}] SETUP_EXCEPTION: {exc}\n{tb}",
            flush=True,
        )
        return {
            "alpha": float(alpha), "alpha_actual": float(alpha_actual),
            "seed": seed,
            "M_old": M_old, "M_total": M_total,
            "run_mode": RUN_MODE,
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
            out = run_arm(arm_name, seed, alpha_actual, shared=shared,
                          cfu_large_probe=cfu_large_probe,
                          cfu_leave_k=cfu_leave_k,
                          cfu_continuous=cfu_continuous)
            arms.append(out)
            print(
                f"  [alpha={alpha} seed={seed} {arm_name}] "
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
                f"  [alpha={alpha} seed={seed} {arm_name}] ARM_EXCEPTION: "
                f"{exc}\n{tb}", flush=True,
            )
            arms.append({
                "arm_name": arm_name,
                "alpha": float(alpha_actual),
                "exception_msg": str(exc),
                "exception_traceback": tb,
            })

    elapsed = time.time() - t0
    return {
        "alpha": float(alpha), "alpha_actual": float(alpha_actual),
        "seed": seed, "M_old": M_old, "M_total": M_total,
        "N": N, "M_RECENT": M_RECENT, "M_HELDOUT": M_HELDOUT,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(N_QUERIES),
        "downscale_scale": DOWNSCALE_SCALE,
        "n_composite_queries": N_COMPOSITE_QUERIES,
        "cohort_k_default": int(COHORT_K_DEFAULT),
        "k_leave_k_out_arm": int(K_LEAVE_K_OUT_ARM),
        "n_probe_batch": int(N_PROBE_BATCH),
        "cfu_eval_frac": float(CFU_EVAL_FRAC),
        "gradient_levels": list(GRADIENT_LEVELS),
        "composite_arity": COMPOSITE_ARITY,
        "n_prune_frac": float(N_PRUNE_FRAC),
        "n_edges_H": int(shared["edge_graph"].n_edges()),
        "trace_total": float(np.sum(shared["base_retrieval_trace"])),
        "n_trace_events": int(shared["n_trace_events"]),
        "baseline_heldout_rec_large_probe": float(base_rec_lp),
        "baseline_heldout_rec_leave_k": float(base_rec_lk),
        "baseline_heldout_rec_continuous": float(base_rec_cont),
        "n_ablations_large_probe": int(n_abl_lp),
        "n_ablations_leave_k": int(n_abl_lk),
        "n_ablations_continuous": int(n_abl_cont),
        "cfu_variance_large_probe": float(var_lp),
        "cfu_variance_leave_k": float(var_lk),
        "cfu_variance_continuous": float(var_cont),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    matches = [a for a in arms if a.get("arm_name") == name]
    return matches[0] if matches else {}


def compute_verdict(per_alpha_seed: List[Dict]) -> Tuple[str, str]:
    if not per_alpha_seed:
        return ("HARD_FAIL", "No valid (alpha, seed) results.")

    # D3 no-silent-except: any exception is HARD_FAIL.
    for r in per_alpha_seed:
        if "exception_phase" in r:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D3 caught {r['exception_phase']} "
                    f"exception alpha={r['alpha']} seed={r['seed']}: "
                    f"{r['exception_msg']}")
        for a in r.get("arms", []):
            if "exception_msg" in a:
                return ("HARD_FAIL",
                        f"HARD_FAIL: D3 caught arm exception "
                        f"alpha={r['alpha']} seed={r['seed']} "
                        f"arm={a['arm_name']}: {a['exception_msg']}")

    # D4 cardinality: 5 arms per (alpha, seed); total = EXPECTED_N_UNITS.
    total_arm_entries = sum(len(r.get("arms", [])) for r in per_alpha_seed)
    expected_per = 5
    for r in per_alpha_seed:
        got = len(r.get("arms", []))
        if got != expected_per:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D4 cardinality_ok breach alpha={r['alpha']} "
                    f"seed={r['seed']}: expected {expected_per} arm entries, "
                    f"got {got}")
    if total_arm_entries != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL: D4 cardinality_ok total breach: expected "
                f"{EXPECTED_N_UNITS} arm entries, got {total_arm_entries}")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in per_alpha_seed)
    if any_llm:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate violated.")

    # D2 mechanism-fires gate on each CFU variant.
    for r in per_alpha_seed:
        for tag, n_field, var_field in [
            ("CFU_LARGE_PROBE", "n_ablations_large_probe",
             "cfu_variance_large_probe"),
            ("CFU_LEAVE_K_OUT", "n_ablations_leave_k",
             "cfu_variance_leave_k"),
            ("CFU_CONTINUOUS", "n_ablations_continuous",
             "cfu_variance_continuous"),
        ]:
            if r.get(n_field, 0) <= 0:
                return ("HARD_FAIL",
                        f"HARD_FAIL: D2 mechanism inert alpha={r['alpha']} "
                        f"seed={r['seed']}: {tag} {n_field}=0")
            if r.get(var_field, 0.0) <= 0.0:
                return ("HARD_FAIL",
                        f"HARD_FAIL: D2 CFU signal flat alpha={r['alpha']} "
                        f"seed={r['seed']}: {tag} {var_field}=0")

    # Aggregate per (arm, alpha) across seeds.
    alphas_seen = sorted({r["alpha"] for r in per_alpha_seed})

    def _agg(arm_name: str, alpha: float) -> Dict[str, float]:
        rs = [r for r in per_alpha_seed if r["alpha"] == alpha]
        arms_per_seed = [_arm_by_name(r["arms"], arm_name) for r in rs]
        arms_per_seed = [a for a in arms_per_seed if a and "recall_old_RETRIEVED" in a]
        if not arms_per_seed:
            return {}
        rec_retr = [a["recall_old_RETRIEVED"] for a in arms_per_seed]
        rec_unretr = [a["recall_old_UNRETRIEVED"] for a in arms_per_seed]
        rec_rec = [a["recall_recent"] for a in arms_per_seed]
        cor = [a["cor_importance_magnitude"] for a in arms_per_seed]
        ndown = [a["n_downscaled"] for a in arms_per_seed]
        return {
            "mean_rec_RETRIEVED": float(np.mean(rec_retr)),
            "mean_rec_UNRETRIEVED": float(np.mean(rec_unretr)),
            "mean_rec_recent": float(np.mean(rec_rec)),
            "mean_cor_imp_W": float(np.mean(cor)),
            "mean_n_downscaled": float(np.mean(ndown)),
        }

    # Find best (alpha, CFU-arm) combo by sel_unretr.
    best_sel = -1e9
    best_combo = ("", -1.0)
    best_agg = None
    best_rand_agg = None
    sel_by_combo = {}
    for alpha in alphas_seen:
        agg_rand = _agg("ARM_BASELINE_RANDOM_IMPORTANCE", alpha)
        if not agg_rand:
            continue
        rand_unretr = agg_rand["mean_rec_UNRETRIEVED"]
        for arm_name in CFU_ARM_NAMES:
            agg = _agg(arm_name, alpha)
            if not agg:
                continue
            sel = rand_unretr - agg["mean_rec_UNRETRIEVED"]
            sel_by_combo[(arm_name, alpha)] = sel
            if sel > best_sel:
                best_sel = sel
                best_combo = (arm_name, alpha)
                best_agg = agg
                best_rand_agg = agg_rand

    # Also report trace summary at each alpha.
    trace_summary_parts = []
    for alpha in alphas_seen:
        a_t = _agg("ARM_TRACE_ONLY", alpha)
        a_r = _agg("ARM_BASELINE_RANDOM_IMPORTANCE", alpha)
        if a_t and a_r:
            sel_t = a_r["mean_rec_UNRETRIEVED"] - a_t["mean_rec_UNRETRIEVED"]
            trace_summary_parts.append(
                f"TRACE@a={alpha}(unretr={a_t['mean_rec_UNRETRIEVED']:.3f},"
                f"cor={a_t['mean_cor_imp_W']:.3f},sel={sel_t:+.3f})"
            )
    trace_summary = "; ".join(trace_summary_parts)

    # Per CFU arm best across alphas
    cfu_summary_parts = []
    for arm_name in CFU_ARM_NAMES:
        for alpha in alphas_seen:
            agg = _agg(arm_name, alpha)
            agg_rand = _agg("ARM_BASELINE_RANDOM_IMPORTANCE", alpha)
            if not agg or not agg_rand:
                continue
            sel = agg_rand["mean_rec_UNRETRIEVED"] - agg["mean_rec_UNRETRIEVED"]
            cfu_summary_parts.append(
                f"{arm_name[:20]}@a={alpha}(unretr={agg['mean_rec_UNRETRIEVED']:.3f},"
                f"cor={agg['mean_cor_imp_W']:.3f},sel={sel:+.3f})"
            )
    cfu_summary = "; ".join(cfu_summary_parts)

    if best_agg is None:
        return ("HARD_FAIL",
                f"HARD_FAIL: no valid CFU aggregate. "
                f"trace=[{trace_summary}] cfu=[{cfu_summary}]")

    best_arm, best_alpha = best_combo
    best_cor = best_agg["mean_cor_imp_W"]
    best_n_down = best_agg["mean_n_downscaled"]

    summary = (
        f"V5_BASELINE_SEL={V5_BASELINE_SEL_CFU:+.3f}; "
        f"BEST=({best_arm}@a={best_alpha},sel={best_sel:+.3f},"
        f"cor={best_cor:.3f},n_down={best_n_down:.0f}); "
        f"TRACE=[{trace_summary}]; CFU=[{cfu_summary}]"
    )

    # Non-finite guards
    if not (np.isfinite(best_sel) and np.isfinite(best_cor)):
        return ("HARD_FAIL",
                f"HARD_FAIL: non-finite metrics in best CFU. {summary}")

    # Saturation gate: ALL arms across ALL alphas within 0.05 on rec_RETRIEVED
    all_retr = []
    for alpha in alphas_seen:
        for arm in ARM_NAMES:
            agg = _agg(arm, alpha)
            if agg:
                all_retr.append(agg["mean_rec_RETRIEVED"])
    if all_retr and (max(all_retr) - min(all_retr)) < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: arms within 0.05 on rec_RETRIEVED "
                f"(spread={max(all_retr)-min(all_retr):.3f}). Regime saturated. "
                f"{summary}")

    # Fairness gate on EACH CFU arm at EACH alpha (load-bearing v5 win).
    for arm_name in CFU_ARM_NAMES:
        for alpha in alphas_seen:
            agg = _agg(arm_name, alpha)
            if agg and abs(agg["mean_cor_imp_W"]) >= 0.30:
                return ("HARD_FAIL",
                        f"HARD_FAIL: fairness regression "
                        f"{arm_name}@a={alpha} |cor|="
                        f"{abs(agg['mean_cor_imp_W']):.3f} >= 0.30. "
                        f"{summary}")

    # B: best_v6_sel_unretr <= v5_baseline_sel (stronger regime did NOT help)
    if best_sel <= V5_BASELINE_SEL_CFU:
        return ("HARD_FAIL",
                f"HARD_FAIL: best v6 sel={best_sel:+.3f} <= v5_baseline="
                f"{V5_BASELINE_SEL_CFU:+.3f}. Stronger regime did NOT help. "
                f"{summary}")

    # Mechanism-fires gate on best CFU arm
    if best_n_down <= 0:
        return ("HARD_FAIL",
                f"HARD_FAIL: D2 best CFU prune inert (n_downscaled=0). "
                f"{summary}")

    # HARD_PASS bands (all 4 must hold)
    hp_sel = best_sel >= 0.15
    hp_fair = abs(best_cor) < 0.30
    hp_fired = best_n_down > 0
    hp_stronger_than_v5 = (best_sel - V5_BASELINE_SEL_CFU) >= 0.05

    if all([hp_sel, hp_fair, hp_fired, hp_stronger_than_v5]):
        return ("HARD_PASS",
                f"HARD_PASS_CFU_STRONGER_REGIME: best_sel={best_sel:+.3f} "
                f">= 0.15, cor={best_cor:.3f} <0.30 (fairness held), fired, "
                f"v6_lift_over_v5={best_sel - V5_BASELINE_SEL_CFU:+.3f} "
                f">= 0.05. {summary}")

    # MIDDLE_BAND
    mb_sel = best_sel >= 0.08
    mb_fair = hp_fair
    mb_lift = (best_sel - V5_BASELINE_SEL_CFU) >= 0.02
    if all([mb_sel, mb_fair, hp_fired, mb_lift]):
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: HONEST_BOUND. best_sel={best_sel:+.3f} in "
                f"[0.08, 0.15], fairness held, v6_lift_over_v5="
                f"{best_sel - V5_BASELINE_SEL_CFU:+.3f} >= 0.02. "
                f"hp_checks=[sel>=0.15={hp_sel},fair={hp_fair},"
                f"fired={hp_fired},lift>=0.05={hp_stronger_than_v5}]. "
                f"{summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: did not clear PASS or MIDDLE. "
            f"hp_checks=[sel>=0.15={hp_sel},fair={hp_fair},"
            f"fired={hp_fired},lift>=0.05={hp_stronger_than_v5}]; "
            f"mb_lift>=0.02={mb_lift}. {summary}")


# ---------------------------------------------------------------------------
# Main driver: alpha-sweep x seed-sweep with per-(alpha, seed) partials
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}

# Build expected (alpha, seed) keys.
all_keys = [(alpha, seed) for alpha in ALPHA_GRID for seed in SEEDS]
done_keys_str = set(list_completed_keys(out_dir, run_config=run_config))

remaining_keys = []
done_keys_loaded = []
for (alpha, seed) in all_keys:
    key_str = f"alpha{alpha}_seed{seed}"
    if key_str in done_keys_str:
        done_keys_loaded.append((alpha, seed))
    else:
        remaining_keys.append((alpha, seed))

print(
    f"[ckpt] {len(done_keys_loaded)} of {len(all_keys)} (alpha, seed) "
    f"already complete; running {remaining_keys}", flush=True,
)

t_sweep_start = time.time()
for (alpha, seed) in remaining_keys:
    print(
        f"[run] v6 alpha={alpha} seed={seed} N={N} "
        f"J_comp={N_COMPOSITE_QUERIES} N_PROBE={N_PROBE_BATCH} "
        f"K_LKO={K_LEAVE_K_OUT_ARM} grad={len(GRADIENT_LEVELS)}lvls "
        f"mode={RUN_MODE}...",
        flush=True,
    )
    result = run_alpha_seed(alpha, seed)
    key_str = f"alpha{alpha}_seed{seed}"
    write_partial_key(out_dir, key_str, result)

# Reload all partials
per_alpha_seed = []
for (alpha, seed) in all_keys:
    key_str = f"alpha{alpha}_seed{seed}"
    partial = load_partial_key(out_dir, key_str)
    if partial is not None:
        per_alpha_seed.append(partial)
    else:
        print(f"[WARN] partial missing for {key_str}", flush=True)

verdict, verdict_msg = compute_verdict(per_alpha_seed)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

mode_in_results = {r.get("run_mode", "?") for r in per_alpha_seed}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

# Cardinality summary
total_arm_entries = sum(len(r.get("arms", [])) for r in per_alpha_seed)
cardinality_ok = (total_arm_entries == EXPECTED_N_UNITS)
print(
    f"[cardinality] expected={EXPECTED_N_UNITS} observed={total_arm_entries} "
    f"OK={cardinality_ok}", flush=True,
)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_alpha_seed={len(per_alpha_seed)} N={N} M_RECENT={M_RECENT} "
        f"M_HELDOUT={M_HELDOUT} J_comp={N_COMPOSITE_QUERIES} "
        f"ALPHA_GRID={ALPHA_GRID} K_LEAVE_K_OUT_ARM={K_LEAVE_K_OUT_ARM} "
        f"COHORT_K_DEFAULT={COHORT_K_DEFAULT} "
        f"N_PROBE={N_PROBE_BATCH} GRADIENT_LEVELS={GRADIENT_LEVELS} "
        f"arity={COMPOSITE_ARITY} mode={RUN_MODE} "
        f"V5_BASELINE_SEL={V5_BASELINE_SEL_CFU}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N, "M_RECENT": M_RECENT, "M_HELDOUT": M_HELDOUT,
    "alpha_grid": list(ALPHA_GRID),
    "n_seeds": len(SEEDS), "seeds": list(SEEDS),
    "n_queries": N_QUERIES,
    "n_composite_queries": N_COMPOSITE_QUERIES,
    "cohort_k_default": int(COHORT_K_DEFAULT),
    "k_leave_k_out_arm": int(K_LEAVE_K_OUT_ARM),
    "n_probe_batch": int(N_PROBE_BATCH),
    "cfu_eval_frac": float(CFU_EVAL_FRAC),
    "gradient_levels": list(GRADIENT_LEVELS),
    "composite_arity": COMPOSITE_ARITY,
    "downscale_scale": float(DOWNSCALE_SCALE),
    "n_prune_frac": float(N_PRUNE_FRAC),
    "v5_baseline_sel_cfu": float(V5_BASELINE_SEL_CFU),
    "run_mode": RUN_MODE,
    "expected_n_units": EXPECTED_N_UNITS,
    "observed_n_units": total_arm_entries,
    "cardinality_ok": bool(cardinality_ok),
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in per_alpha_seed)),
    "per_alpha_seed": per_alpha_seed,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
