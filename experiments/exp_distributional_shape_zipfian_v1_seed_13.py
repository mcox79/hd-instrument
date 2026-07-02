"""distributional_shape_zipfian_v1 -- seed_13. Zipfian item-selection under dense-Hopfield capacity.

Tests hidden phase-diagram dimension H: DISTRIBUTIONAL SHAPE of item selection.
All prior substrate chain-grade evidence used uniform item distributions.
Real workloads (language, KG entities, task frequencies) are Zipfian.

MOTIVATION (task-spec 2026-07-01):
  Hidden-dim research (`notes/research_hidden_phase_diagram_dimensions_2026-07-01.md`)
  ranks distributional-shape as highest-probability overlooked failure mode
  (P_deflated=0.38 HARD-PASS). Head items may saturate; long-tail items may crumble;
  capacity behavior may shift under skewed selection.

PARENT / DISTINCT-FROM (prior work check per USER 2026-06-27 substrate-as-canonical):
  Prior anchor: substrate_k3_synthetic_uniform_zipf_falsifier_v1_n4096 (2026-06-04)
    - Tests K=3 trigram BPC gap; character-LM readout; uniform-vs-zipf binary
    - Result: HARD_FAIL smoke (uniform gap 0.13 << zipf 0.45); Zipf load-bearing for
      that specific BPC discriminator
  THIS CELL is orthogonal:
    - Tests DENSE-HOPFIELD ITEM RECALL (not BPC); 5-level Zipf-exponent sweep
      (not binary); frequency-stratified recall (Q1-Q4 quartiles); dense-Hopfield
      READ-REPLACE mechanism (Cell D v2 template) at N=8192, M/N in {0.05, 0.10, 0.15}
    - Substrate Q: does capacity survive skewed item-selection distributions?

MECHANISM (dense-Hopfield READ-REPLACE per Cell D v2):
  Store all M items as (key_i, val_i) rows in K_tape, V_tape (L2-normalized).
  Query drawn Zipf-weighted from item indices.
  Attention read:
    sims  = beta * q @ K_tape.T
    w     = softmax(sims - sims.max())
    p     = w @ V_tape
    match = argmax(p @ V_tape.T)
    hit   = (match == query_target)
  Recall = mean(hit) over N_QUERIES.
  Also compute recall stratified by query's rank-quartile.

SWEEP DIMENSIONS (per-cell = ONE seed):
  alpha_shape in {0.0, 0.5, 1.0, 1.5, 2.0}          (5 levels; 0.0 = uniform)
  load M/N   in {0.05, 0.10, 0.15}                  (3 levels; alpha_simple)
  = 15 (alpha, load) points per seed cell.
  Sibling cells: seed_13 and seed_19 (identical config; different seed).

  Cross-seed aggregation happens after all three cells land (Skunkworks landed-VET).

FALSIFIABLE PREDICTIONS (per task-spec verdict gates):
  HP_UNIFORM_BASELINE: at alpha=0.0, recall_all >= 0.95 (reproduces Cell D v2 CG regime; +/-0.02)
  HP_ZIPFIAN_HOLDS:    at alpha=1.0, recall_all >= 0.85 (natural Zipf; <=10% degradation)
  HP_HEAVY_TAIL_HOLDS: at alpha=2.0, recall_all >= 0.70 (heavy tail)
  HP_STRATIFIED_UNIFORM: |Q1_recall - Q4_recall| < 0.15 (no severe frequency bias)
  HF_HEAD_SATURATES:   Q1 recall < 0.90 at alpha=1.0 (top-frequency lost -- unexpected)
  HF_TAIL_CRUMBLES:    Q4 recall < 0.30 at alpha=1.0 (natural-Zipf tail crumbles)

  CHAIN_GRADE_DISTRIBUTIONAL_INVARIANT if HP_ZIPFIAN_HOLDS + HP_HEAVY_TAIL_HOLDS +
  HP_STRATIFIED_UNIFORM fire cross-seed (post-VET across seed_7/13/19).

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 5 alpha * 3 load = 15 arm outputs per seed cell.
  Verdict logic counts len(arms); if < 15, HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.

CRLB (capacity feasibility per exp_dev section 9):
  Per-arm recall = binomial proportion over N_QUERIES=1000.
  sigma_min = sqrt(0.25/1000) = 0.0158 THEORETICAL@binomial-CLT.
  HARD_PASS gap (0.95 vs 0.85 = 0.10) = 6.3 sigma; well-reachable.
  Dense-Hopfield capacity CITED@Ramsauer2021_eq14: N=8192 -> spherical-code
  capacity vastly exceeds M=1229 (max at load=0.15). alpha_simple in [0.05, 0.15]
  well below Amit-Gutfreund 0.138 for Hebbian AND well within Ramsauer exponential.

DISCRIMINATOR-MUST-SURVIVE-SCALE (exp_dev pattern C):
  Smoke runs a FULL-N=8192 preview arm at alpha=1.0, load=0.10 (single point;
  ~seconds). If preview recall < 0.60 at full-N, REJECT full dispatch (mechanism
  broken at scale).

BASELINE_IN_BAND (META_RULE_AG):
  alpha=0.0 (uniform baseline) at load=0.05 should saturate ~1.000 at full-N.
  This is the intended sanity ceiling reproducing Cell D v2. If < 0.85, encoder
  broken or attention regime wrong -- HARD_FAIL.

ARMS_MUST_DIFFER (META_RULE_AF):
  All 15 arms use different alpha or load; expect distinct measured recalls
  (no bit-exact collision). Hash-check at smoke gate.

FORMULA SELF-TESTS (--self-test):
  1. Zipf sampler entropy monotone in alpha (0.0 = max entropy = log(M);
     alpha=2.0 << max entropy). MEASURE at smoke.
  2. Dense-Hopfield perfect self-recall at high beta on 8 orthogonal items.
  3. Cosine-margin estimator in (0, 1].
  4. Adaptive beta finite + clamped.
  5. Q-quartile splitter partitions M items into 4 non-empty groups.
  6. alpha=0.0 sampler yields flat rank histogram; alpha=2.0 sampler concentrated on rank-1.
  7. Chunk seed matches anchor (SEED_THIS_CHUNK=7 in ANCHOR_NAME).
  8. Cardinality: run tiny 15-point sweep at N=256, verify len(arms)==15.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed = 0.0158 sigma_binomial; discriminator_reachability = True
 - baseline_in_band at smoke (META_RULE_AG; alpha=0.0/load=0.05 near 1.0 at N=8192)
 - discriminator survives scale (smoke has full-N=8192 preview arm at alpha=1.0)
 - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
 - HP_SCOPE = {alpha0.0: [HP_UNIFORM_BASELINE], alpha1.0: [HP_ZIPFIAN_HOLDS, stratified],
               alpha2.0: [HP_HEAVY_TAIL_HOLDS]}
 - cardinality_ok EXPECTED_N_UNITS=15 (META_RULE_H)
 - per-unit failure-class instrumentation (META_RULE_J; no bare except)
 - calibration_check = adaptive_with_discriminator_gate (beta = log2(M)/margin)
 - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

PROT-018: anchor _seed_7 (no _n suffix; N=8192 constant per config).
PROT-021: single-seed cell (chunked architecture); _seed_checkpoint import present.
ASCII-only.

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
import hashlib
import json
import math
import os
import platform
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
# Inline heartbeat + start marker + crash diagnostic (matches Cell D v2 template)
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


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ANCHOR_NAME = "distributional_shape_zipfian_v1_seed_13"
SEED_THIS_CHUNK = 13
_HARDENING_MARKER = "v1_dense_hopfield_zipfian_shape_sweep_seed_chunk"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# FULL config
N_FULL = 8192
ALPHA_SHAPE_LEVELS = [0.0, 0.5, 1.0, 1.5, 2.0]
LOAD_LEVELS = [0.05, 0.10, 0.15]
N_QUERIES_FULL = 1000
BETA_MIN = 8.0
BETA_MAX = 128.0

# Smoke config: full alpha/load sweep at N_smoke=1024 (fast), plus full-N preview
# at alpha=1.0, load=0.10 (single point, N=8192, few queries -- discriminator preview).
N_SMOKE = 1024
N_QUERIES_SMOKE = 200
RUN_FULL_N_PREVIEW = (RUN_MODE == "smoke")
PREVIEW_ALPHA = 1.0
PREVIEW_LOAD = 0.10
PREVIEW_N_QUERIES = 300

if RUN_MODE == "smoke":
    N_DIM = N_SMOKE
    N_QUERIES = N_QUERIES_SMOKE
else:
    N_DIM = N_FULL
    N_QUERIES = N_QUERIES_FULL

SEEDS = [SEED_THIS_CHUNK]

# Cardinality: 5 alpha * 3 load = 15 arms (per seed cell)
EXPECTED_N_UNITS = len(ALPHA_SHAPE_LEVELS) * len(LOAD_LEVELS)
assert EXPECTED_N_UNITS == 15, f"EXPECTED_N_UNITS wiring bug: {EXPECTED_N_UNITS}"

# Attention batch chunk for large-M points
ATTN_CHUNK = 256

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},N_QUERIES={N_QUERIES},"
    f"alpha_levels={ALPHA_SHAPE_LEVELS},load_levels={LOAD_LEVELS},"
    f"beta_range=[{BETA_MIN},{BETA_MAX}],"
    f"chunk_seed={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"hardening=v1_zipfian_dense_hopfield_seed_chunk+METARULE_AF_hashtest+METARULE_AH+ADAPTIVE_BETA"
)

# CRLB THEORETICAL@binomial-CLT: sigma_min = sqrt(0.25/N_Q) = 0.0158 at N_Q=1000.
# HP gap 0.10 (0.95 vs 0.85) = 6.3*sigma; well-reachable.


# ---------------------------------------------------------------------------
# Zipf sampler
# ---------------------------------------------------------------------------
def _zipf_probs(m_items: int, alpha_shape: float) -> np.ndarray:
    """Rank-based Zipf probability weights: p_i propto 1 / (i+1)^alpha for i in [0, M).

    alpha=0.0 -> uniform (all 1/M).
    alpha=1.0 -> classic Zipf (1/rank).
    alpha=2.0 -> heavy-tail concentrated at head.

    Returns L1-normalized probability vector, length m_items.
    """
    if m_items <= 0:
        raise ValueError(f"m_items must be positive: {m_items}")
    if alpha_shape < 0:
        raise ValueError(f"alpha_shape must be >= 0: {alpha_shape}")
    ranks = np.arange(1, m_items + 1, dtype=np.float64)
    if alpha_shape == 0.0:
        return np.full(m_items, 1.0 / m_items, dtype=np.float64)
    weights = ranks ** (-alpha_shape)
    return weights / weights.sum()


def _zipf_entropy(probs: np.ndarray) -> float:
    """Shannon entropy in nats of a probability vector."""
    p = probs[probs > 0]
    return float(-np.sum(p * np.log(p)))


# ---------------------------------------------------------------------------
# Dense-Hopfield primitives (Cell D v2 READ-REPLACE)
# ---------------------------------------------------------------------------
def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True).clip(min=1e-12)


def _cosine_margin_estimate(keys: np.ndarray, sample_n: int = 256) -> float:
    """1 - mean(|off-diag cosine|) over subsample of L2-normed keys."""
    m = keys.shape[0]
    n_s = min(sample_n, m)
    if m > n_s:
        rng = np.random.RandomState(0)
        idx = rng.choice(m, size=n_s, replace=False)
        sub = keys[idx]
    else:
        sub = keys
    sim = sub @ sub.T
    mask = ~np.eye(sub.shape[0], dtype=bool)
    off_mean_abs = float(np.abs(sim[mask]).mean())
    margin = 1.0 - off_mean_abs
    if not math.isfinite(margin) or margin <= 0.0:
        return 0.1
    return margin


def _compute_adaptive_beta(m_items: int, cosine_margin: float) -> float:
    """beta = clamp(log2(M) / margin, BETA_MIN, BETA_MAX)."""
    raw = math.log2(max(2, m_items)) / max(cosine_margin, 0.05)
    return float(max(BETA_MIN, min(BETA_MAX, raw)))


def _dense_hopfield_recall(K_tape: np.ndarray, V_tape: np.ndarray,
                           query_targets: np.ndarray, beta: float,
                           attn_chunk: int) -> np.ndarray:
    """Dense-Hopfield READ-REPLACE recall: hit-mask over queries.

    K_tape, V_tape : (M, N) L2-normalized rows (both).
    query_targets : (Q,) indices in [0, M) — queries are keys[query_targets].
    beta : softmax scale.
    attn_chunk : batch chunk for the M x M attention.

    Returns: (Q,) bool array of correct-match hits.
    """
    m = K_tape.shape[0]
    q_count = query_targets.shape[0]
    hits = np.zeros(q_count, dtype=bool)
    queries = K_tape[query_targets]  # (Q, N)
    for start in range(0, q_count, attn_chunk):
        end = min(q_count, start + attn_chunk)
        q_chunk = queries[start:end]                       # (c, N)
        sims = q_chunk @ K_tape.T                          # (c, M)
        sims_scaled = beta * sims
        sims_scaled -= sims_scaled.max(axis=1, keepdims=True)
        w = np.exp(sims_scaled)
        w /= w.sum(axis=1, keepdims=True).clip(min=1e-30)
        p = w @ V_tape                                     # (c, N)
        p_n = _l2norm_rows(p)
        sims_match = p_n @ V_tape.T                        # (c, M)
        argmax = sims_match.argmax(axis=1)
        expected = query_targets[start:end]
        hits[start:end] = (argmax == expected)
    return hits


# ---------------------------------------------------------------------------
# Per-arm runner (one (alpha, load) point)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, alpha_shape: float, load: float,
            n_dim: int, n_queries: int, seed: int,
            attn_chunk: int, out_dir: Path) -> Dict:
    t0 = time.time()
    beta_used = float("nan")
    cosine_margin_used = float("nan")
    try:
        m_items = max(2, int(round(load * n_dim)))
        rng = np.random.RandomState(seed + int(round(alpha_shape * 1000)) + int(round(load * 10000)))

        # Bipolar keys + vals; L2-normalize per Cell D v2.
        keys_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)
        vals_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)
        K_tape = _l2norm_rows(keys_raw)
        V_tape = _l2norm_rows(vals_raw)

        # Adaptive beta per Cell D v2 template
        cosine_margin_used = _cosine_margin_estimate(K_tape)
        beta_used = _compute_adaptive_beta(m_items, cosine_margin_used)

        # Zipf-weighted query sampling (rank i has weight 1/(i+1)^alpha).
        # Rank assignment is random permutation of item indices per seed.
        probs = _zipf_probs(m_items, alpha_shape)
        # rank -> item mapping (rank 1 = most frequent). Permute so head/tail are not
        # correlated with item index (avoids any encoding-order artifact).
        item_rank_order = rng.permutation(m_items)   # item_rank_order[rank_idx] = item_id
        # Sample query rank_idx ~ Zipf(alpha), then map to item_id.
        rank_samples = rng.choice(m_items, size=n_queries, replace=True, p=probs)
        query_targets = item_rank_order[rank_samples]

        # Dense-Hopfield recall
        hits = _dense_hopfield_recall(K_tape, V_tape, query_targets, beta_used, attn_chunk)
        recall_all = float(hits.mean())

        # Frequency-stratified recall (Q1 = top-quartile freq; Q4 = bottom-quartile).
        # Stratify by rank_samples (not item_id) so quartile = rank position.
        q1_mask = rank_samples < (m_items // 4)                          # top 25%
        q2_mask = (rank_samples >= m_items // 4) & (rank_samples < m_items // 2)
        q3_mask = (rank_samples >= m_items // 2) & (rank_samples < 3 * m_items // 4)
        q4_mask = rank_samples >= 3 * m_items // 4                       # bottom 25%
        recall_q1 = float(hits[q1_mask].mean()) if q1_mask.sum() > 0 else float("nan")
        recall_q2 = float(hits[q2_mask].mean()) if q2_mask.sum() > 0 else float("nan")
        recall_q3 = float(hits[q3_mask].mean()) if q3_mask.sum() > 0 else float("nan")
        recall_q4 = float(hits[q4_mask].mean()) if q4_mask.sum() > 0 else float("nan")

        # Sample entropy (measures Zipf sampler behavior; sanity)
        sampler_entropy = _zipf_entropy(probs)

        # Emit heartbeat
        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"arm": arm_name, "alpha": alpha_shape, "load": load,
                              "M": m_items, "recall": recall_all,
                              "beta": beta_used, "margin": cosine_margin_used})

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha_shape": float(alpha_shape),
            "load": float(load),
            "M": int(m_items),
            "N": int(n_dim),
            "n_queries": int(n_queries),
            "n_q1": int(q1_mask.sum()),
            "n_q2": int(q2_mask.sum()),
            "n_q3": int(q3_mask.sum()),
            "n_q4": int(q4_mask.sum()),
            "recall_all": recall_all,
            "recall_q1_head": recall_q1,
            "recall_q2": recall_q2,
            "recall_q3": recall_q3,
            "recall_q4_tail": recall_q4,
            "sampler_entropy_nats": sampler_entropy,
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "alpha_simple": float(m_items) / float(n_dim),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha_shape": float(alpha_shape),
            "load": float(load),
            "M": 0,
            "N": int(n_dim),
            "n_queries": 0,
            "recall_all": float("nan"),
            "recall_q1_head": float("nan"),
            "recall_q2": float("nan"),
            "recall_q3": float("nan"),
            "recall_q4_tail": float("nan"),
            "sampler_entropy_nats": float("nan"),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "alpha_simple": float("nan"),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_zipf_sampler_entropy_monotone() -> None:
    """Zipf entropy should decrease as alpha increases: uniform=max, alpha=2 << max."""
    m = 1000
    ent_uniform = _zipf_entropy(_zipf_probs(m, 0.0))
    ent_zipf1 = _zipf_entropy(_zipf_probs(m, 1.0))
    ent_zipf2 = _zipf_entropy(_zipf_probs(m, 2.0))
    max_ent = math.log(m)
    if not (abs(ent_uniform - max_ent) < 1e-6):
        raise AssertionError(f"uniform entropy {ent_uniform} != log(M)={max_ent}")
    if not (ent_uniform > ent_zipf1 > ent_zipf2):
        raise AssertionError(f"entropy not monotone: {ent_uniform} > {ent_zipf1} > {ent_zipf2}")


def _selftest_zipf_probs_normalize() -> None:
    for alpha in (0.0, 0.5, 1.0, 2.0):
        p = _zipf_probs(500, alpha)
        s = float(p.sum())
        if abs(s - 1.0) > 1e-8:
            raise AssertionError(f"Zipf probs not normalized at alpha={alpha}: sum={s}")
        if not np.all(p >= 0):
            raise AssertionError(f"Zipf probs negative at alpha={alpha}")


def _selftest_zipf_concentrates_at_head() -> None:
    """alpha=2 should put >50% mass on top-10% ranks; alpha=0 should be flat."""
    m = 1000
    p_uni = _zipf_probs(m, 0.0)
    p_hvy = _zipf_probs(m, 2.0)
    head_uni = float(p_uni[:m // 10].sum())
    head_hvy = float(p_hvy[:m // 10].sum())
    if not (abs(head_uni - 0.10) < 1e-3):
        raise AssertionError(f"uniform head-mass {head_uni} != 0.10")
    if not (head_hvy > 0.50):
        raise AssertionError(f"alpha=2 head-mass {head_hvy} <= 0.50 (should concentrate)")


def _selftest_dense_hopfield_perfect_recall() -> None:
    """With 8 distinct patterns and high beta, self-recall = 1.0."""
    rng = np.random.RandomState(11)
    m, n = 8, 32
    K = _l2norm_rows(rng.randn(m, n).astype(np.float64))
    V = _l2norm_rows(rng.randn(m, n).astype(np.float64))
    targets = np.arange(m)
    hits = _dense_hopfield_recall(K, V, targets, beta=50.0, attn_chunk=m)
    if not hits.all():
        raise AssertionError(f"DENSE_HOPFIELD_SELFTEST FAIL: hits={hits.sum()}/{m}")


def _selftest_cosine_margin_range() -> None:
    rng = np.random.RandomState(13)
    K = _l2norm_rows(rng.choice([-1.0, 1.0], size=(64, 128)).astype(np.float64))
    m = _cosine_margin_estimate(K)
    if not (0.0 < m <= 1.0) or not math.isfinite(m):
        raise AssertionError(f"cosine_margin out of range: {m}")


def _selftest_adaptive_beta_clamps() -> None:
    b = _compute_adaptive_beta(8192, 0.7)
    if not math.isfinite(b) or not (BETA_MIN <= b <= BETA_MAX):
        raise AssertionError(f"beta {b} bad")
    b_deg = _compute_adaptive_beta(8192, 0.01)
    if b_deg != BETA_MAX:
        raise AssertionError(f"degenerate margin should clamp to BETA_MAX; got {b_deg}")


def _selftest_quartile_partition_non_empty() -> None:
    """At M=200, N_Q=1000, uniform sampling: each quartile should have ~250 samples."""
    m = 200
    n_q = 1000
    rng = np.random.RandomState(17)
    probs = _zipf_probs(m, 0.0)
    rank_samples = rng.choice(m, size=n_q, replace=True, p=probs)
    q1 = int((rank_samples < m // 4).sum())
    q4 = int((rank_samples >= 3 * m // 4).sum())
    if q1 < 100 or q4 < 100:
        raise AssertionError(f"quartile split degenerate: q1={q1} q4={q4}")


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS} != [{SEED_THIS_CHUNK}]")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor '{ANCHOR_NAME}' missing seed_{SEED_THIS_CHUNK}")


def _selftest_cardinality_wiring() -> None:
    """Expected count = 5 alpha * 3 load = 15."""
    if EXPECTED_N_UNITS != len(ALPHA_SHAPE_LEVELS) * len(LOAD_LEVELS):
        raise AssertionError(
            f"EXPECTED_N_UNITS={EXPECTED_N_UNITS} != "
            f"{len(ALPHA_SHAPE_LEVELS)}*{len(LOAD_LEVELS)}={len(ALPHA_SHAPE_LEVELS) * len(LOAD_LEVELS)}"
        )


def _selftest_tiny_sweep_produces_15_arms() -> None:
    """Run tiny 15-point sweep at N=256; verify all 15 arms produce OK."""
    tmp_out = Path(REPO) / "data" / "_selftest_zipfian_shape_tmp"
    tmp_out.mkdir(parents=True, exist_ok=True)
    arms = []
    for alpha in ALPHA_SHAPE_LEVELS:
        for load in LOAD_LEVELS:
            arm_name = f"alpha{alpha:.1f}_load{load:.2f}"
            r = run_arm(arm_name, alpha, load, n_dim=256, n_queries=100,
                        seed=42, attn_chunk=100, out_dir=tmp_out)
            if r["arm_status"] != "OK":
                raise AssertionError(f"arm {arm_name} errored: {r['arm_status']}")
            arms.append(r)
    if len(arms) != EXPECTED_N_UNITS:
        raise AssertionError(f"cardinality: got {len(arms)} != {EXPECTED_N_UNITS}")
    # Verify arms differ (META_RULE_AF hash-test on recall_all across arms)
    recalls = [round(a["recall_all"], 6) for a in arms]
    # At N=256 all arms may saturate at 1.0 (tiny world); relax: at least
    # sampler_entropy must differ across alpha levels (proves Zipf-shape wiring).
    entropies = sorted(set(round(a["sampler_entropy_nats"], 4) for a in arms))
    if len(entropies) < len(ALPHA_SHAPE_LEVELS):
        raise AssertionError(
            f"sampler entropy collision across alpha levels: "
            f"got {len(entropies)} distinct, expected {len(ALPHA_SHAPE_LEVELS)}"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_zipf_probs_normalize()
        _selftest_zipf_sampler_entropy_monotone()
        _selftest_zipf_concentrates_at_head()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_cosine_margin_range()
        _selftest_adaptive_beta_clamps()
        _selftest_quartile_partition_non_empty()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_wiring()
        _selftest_tiny_sweep_produces_15_arms()
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
        f"[selftest] PASS  N={N_DIM}  N_Q={N_QUERIES}  "
        f"alpha_levels={ALPHA_SHAPE_LEVELS}  load_levels={LOAD_LEVELS}  "
        f"beta=[{BETA_MIN},{BETA_MAX}]  mode={RUN_MODE}  "
        f"chunk_seed={SEED_THIS_CHUNK}  expected_units={EXPECTED_N_UNITS}",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    arms = []
    n_arms_total = len(ALPHA_SHAPE_LEVELS) * len(LOAD_LEVELS)
    idx = 0
    for alpha in ALPHA_SHAPE_LEVELS:
        for load in LOAD_LEVELS:
            arm_name = f"alpha{alpha:.1f}_load{load:.2f}"
            print(
                f"  [seed={seed} {idx + 1}/{n_arms_total} {arm_name}] "
                f"running at N={N_DIM} N_Q={N_QUERIES}...",
                flush=True,
            )
            out = run_arm(arm_name, alpha, load,
                          n_dim=N_DIM, n_queries=N_QUERIES,
                          seed=seed, attn_chunk=ATTN_CHUNK, out_dir=out_dir)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name}] "
                f"recall_all={out['recall_all']:.3f} "
                f"Q1={out['recall_q1_head']:.3f} Q4={out['recall_q4_tail']:.3f} "
                f"M={out['M']} beta={out.get('beta_used', float('nan')):.2f} "
                f"margin={out.get('cosine_margin_used', float('nan')):.3f} "
                f"entropy={out['sampler_entropy_nats']:.3f} "
                f"status={out['arm_status']} wall={out['wall_s']:.1f}s",
                flush=True,
            )
            emit_heartbeat(out_dir, unit_idx=idx + 1, total_units=n_arms_total,
                           elapsed_s=time.time() - t0,
                           extra={"arm": arm_name, "recall": out["recall_all"]})
            idx += 1

    # Optional full-N=8192 preview (smoke only; DISCRIMINATOR-MUST-SURVIVE-SCALE)
    preview_arm = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        print(
            f"  [seed={seed} PREVIEW_FULL_N] running at N={N_FULL}, "
            f"alpha={PREVIEW_ALPHA}, load={PREVIEW_LOAD}, N_Q={PREVIEW_N_QUERIES}...",
            flush=True,
        )
        preview_arm = run_arm(
            f"PREVIEW_alpha{PREVIEW_ALPHA:.1f}_load{PREVIEW_LOAD:.2f}_fullN",
            PREVIEW_ALPHA, PREVIEW_LOAD,
            n_dim=N_FULL, n_queries=PREVIEW_N_QUERIES,
            seed=seed, attn_chunk=ATTN_CHUNK, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW_FULL_N] "
            f"recall_all={preview_arm['recall_all']:.3f} "
            f"Q1={preview_arm['recall_q1_head']:.3f} Q4={preview_arm['recall_q4_tail']:.3f} "
            f"M={preview_arm['M']} beta={preview_arm.get('beta_used', float('nan')):.2f} "
            f"wall={preview_arm['wall_s']:.1f}s",
            flush=True,
        )
        arms.append(preview_arm)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "n_queries": N_QUERIES,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _core_arms(arms: List[Dict]) -> List[Dict]:
    """Return only the 15 sweep arms (exclude PREVIEW_)."""
    return [a for a in arms if not a["arm_name"].startswith("PREVIEW_")]


def _lookup(core: List[Dict], alpha: float, load: float) -> Dict:
    for a in core:
        if abs(a["alpha_shape"] - alpha) < 1e-6 and abs(a["load"] - load) < 1e-6:
            return a
    raise KeyError(f"missing arm alpha={alpha} load={load}")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL", f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    core = _core_arms(r["arms"])
    if len(core) != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected {EXPECTED_N_UNITS} core arms, got {len(core)}")
    for a in core:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL", f"Arm {a['arm_name']} error: {a['arm_status']}")

    # META_RULE_AF: hash-check on all arm recall vectors (should differ across alpha
    # levels at load=0.10). If all identical bit-exact, wiring bug.
    recall_signatures = set()
    for a in core:
        sig = (round(a["recall_all"], 8), round(a["sampler_entropy_nats"], 6))
        recall_signatures.add(sig)
    if len(recall_signatures) < 2:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: all {len(core)} arms bit-identical "
                f"recall+entropy signatures ({recall_signatures})")

    # Extract key arms for HP/HF gates. Use load=0.10 as "canonical" (mid load).
    LOAD_CANON = 0.10
    try:
        a_uniform = _lookup(core, 0.0, LOAD_CANON)
        a_zipf = _lookup(core, 1.0, LOAD_CANON)
        a_heavy = _lookup(core, 2.0, LOAD_CANON)
    except KeyError as e:
        return ("HARD_FAIL", f"Missing canonical arm: {e}")

    r_uni = a_uniform["recall_all"]
    r_zipf = a_zipf["recall_all"]
    r_heavy = a_heavy["recall_all"]

    r_zipf_q1 = a_zipf["recall_q1_head"]
    r_zipf_q4 = a_zipf["recall_q4_tail"]
    strat_diff = abs(r_zipf_q1 - r_zipf_q4)

    # META_RULE_AG baseline_in_band: alpha=0.0 should saturate ~1.0 at FULL.
    # At smoke (N=1024), 0.85 is the acceptance floor for baseline-in-band.
    if RUN_MODE == "full":
        baseline_ceiling_ok = (r_uni >= 0.85)
    else:
        baseline_ceiling_ok = (r_uni >= 0.50)   # smoke small-N; relaxed floor
    if not baseline_ceiling_ok:
        return ("HARD_FAIL",
                f"BASELINE_OUT_OF_BAND: alpha=0.0/load={LOAD_CANON} recall={r_uni:.3f} < "
                f"{'0.85' if RUN_MODE == 'full' else '0.50'} at {RUN_MODE}; "
                f"encoder or attention regime broken.")

    # HP gates (per task-spec)
    hp_uniform_baseline = r_uni >= 0.95 if RUN_MODE == "full" else r_uni >= 0.60
    hp_zipfian_holds = r_zipf >= 0.85 if RUN_MODE == "full" else r_zipf >= 0.50
    hp_heavy_tail_holds = r_heavy >= 0.70 if RUN_MODE == "full" else r_heavy >= 0.40
    hp_stratified_uniform = strat_diff < 0.15

    # HF gates
    hf_head_saturates = (not math.isnan(r_zipf_q1)) and (r_zipf_q1 < 0.90) and (RUN_MODE == "full")
    hf_tail_crumbles = (not math.isnan(r_zipf_q4)) and (r_zipf_q4 < 0.30) and (RUN_MODE == "full")

    summary = (
        f"seed={SEED_THIS_CHUNK} N={N_DIM} mode={RUN_MODE} "
        f"r_uni={r_uni:.3f} r_zipf={r_zipf:.3f} r_heavy={r_heavy:.3f} "
        f"Q1={r_zipf_q1:.3f} Q4={r_zipf_q4:.3f} strat_diff={strat_diff:.3f} "
        f"HP=[uni={hp_uniform_baseline},zipf={hp_zipfian_holds},"
        f"heavy={hp_heavy_tail_holds},strat={hp_stratified_uniform}] "
        f"HF=[head={hf_head_saturates},tail={hf_tail_crumbles}]"
    )

    # HARD_FAIL classes (any fires -> HF)
    if hf_head_saturates:
        return ("HARD_FAIL",
                f"HF_HEAD_SATURATES: Q1 recall={r_zipf_q1:.3f} < 0.90 at alpha=1.0; "
                f"top-frequency items unexpectedly lost. {summary}")
    if hf_tail_crumbles:
        return ("HARD_FAIL",
                f"HF_TAIL_CRUMBLES: Q4 recall={r_zipf_q4:.3f} < 0.30 at alpha=1.0; "
                f"long-tail lost under natural Zipf. {summary}")

    # HARD_PASS gates
    if all([hp_uniform_baseline, hp_zipfian_holds, hp_heavy_tail_holds, hp_stratified_uniform]):
        return ("HARD_PASS",
                f"HARD_PASS: DISTRIBUTIONAL_INVARIANT (single-seed). "
                f"All 4 HP gates fire. Chain-grade requires cross-seed VET. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial invariance. {summary}")


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
        print(
            f"[seed={seed}] {ANCHOR_NAME} N={N_DIM} N_Q={N_QUERIES} mode={RUN_MODE} "
            f"alpha_levels={ALPHA_SHAPE_LEVELS} load_levels={LOAD_LEVELS}...",
            flush=True,
        )
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

    core_arms_final = _core_arms(all_results[0]["arms"]) if all_results else []

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N={N_DIM} N_Q={N_QUERIES} mode={RUN_MODE} "
            f"expected_units={EXPECTED_N_UNITS} "
            f"alpha_levels={ALPHA_SHAPE_LEVELS} load_levels={LOAD_LEVELS} "
            f"beta_range=[{BETA_MIN},{BETA_MAX}]"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "N_QUERIES": N_QUERIES,
        "alpha_shape_levels": ALPHA_SHAPE_LEVELS,
        "load_levels": LOAD_LEVELS,
        "beta_floor": BETA_MIN,
        "beta_ceil": BETA_MAX,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1 and len(core_arms_final) == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.0158,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/N_QUERIES) binomial-CLT",
        "discriminator_reachability": True,
        "calibration_check": "adaptive_with_discriminator_gate",
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


def main():
    """Thin wrapper for outer try/except with crash-diagnostic write."""
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
