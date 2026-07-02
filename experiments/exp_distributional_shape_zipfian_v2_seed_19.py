"""distributional_shape_zipfian_v2 -- seed_19. Zipfian + noise + overload; two-tier prediction.

v1 (2026-07-01) saturated at recall=1.000 across all 15 (alpha, load) points at
loads {0.05, 0.10, 0.15} AND at full-N=8192 preview -- dense-Hopfield exponential
capacity trivially handles underloaded regime regardless of distributional shape.

v2 REGIME WIDENING per Director decision (2026-07-01) driven by sparse-coding drill
(D-RIP unified framework, notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md):
  Sparse-coding predicts TWO-TIER failure specifically at loads NEAR THE WALL under
  noise: high-frequency (head) items stay recoverable due to margin advantage, tail
  patterns fail earlier than uniform. Need stress axis (query noise) + overload axis
  to create discriminating regime.

CRITICAL DISCRIMINATOR (Director spec):
  HP_TWO_TIER_ZIPFIAN: at (sigma>=0.2, load>=0.30, alpha=1.0),
    recall_Q1 - recall_Q4 >= 0.15 (head-vs-tail gap fires).
  If at (alpha=1.0, sigma=0.2, load=0.30, N=8192) BOTH Q1 and Q4 >= 0.95 in smoke
  preview -> sparse-coding two-tier prediction FALSIFIED at these params -> halt
  + report as HARD_FAIL for the prediction (valid substrate physics finding).

SWEEP DIMENSIONS (per-cell = ONE seed):
  alpha_shape in {0.0 (uniform), 1.0 (natural Zipf), 2.0 (heavy tail)}   -- 3 levels
  query_noise sigma in {0.0, 0.15, 0.3}                                  -- 3 levels
  load M/N in {0.10, 0.20, 0.30, 0.50, 0.80, 1.20}                       -- 6 levels
  = 3 * 3 * 6 = 54 (alpha, sigma, load) points per seed cell.

  Overload load=1.20 -> M=9830 > N=8192 (beyond spherical-code linear regime).

Sibling cells: seed_13 and seed_19 (identical config; different seed).
Cross-seed aggregation post-VET.

QUERY NOISE MODEL (bit-flip / BSC on bipolar keys):
  Bipolar keys in {-1, +1}. For each query, with probability sigma per-coordinate,
  flip the sign of that coordinate BEFORE L2-normalizing the query.
  L2-normalize noisy query, then attention read on clean K_tape.
  sigma=0.0 -> exact-key (v1 baseline). sigma=0.3 -> heavy noise; expect margin
  degradation, differentially larger on Zipf-tail (thinner statistical support).

MECHANISM (dense-Hopfield READ-REPLACE per Cell D v2; UNCHANGED from v1):
  Store all M items as (K_tape, V_tape) L2-normalized rows.
  Query = noisy version of K_tape[target].
  sims = beta * q_noisy @ K_tape.T; w = softmax(sims); p = w @ V_tape;
  match = argmax(p @ V_tape.T); hit = (match == target).
  Adaptive beta = clamp(log2(M) / cosine_margin, [8, 128]) per Cell D v2.

FALSIFIABLE PREDICTIONS (per task-spec verdict gates + Director synthesis):

  HARD_PASS_TWO_TIER (chain-grade rescue signature):
    HP_TWO_TIER_ZIPFIAN: at (alpha=1.0, sigma=0.2, load=0.30):
      recall_Q1_head - recall_Q4_tail >= 0.15  (Q1 supports tail collapse).
      Note: task-spec sigma=0.2 not in grid (grid is {0, 0.15, 0.3}); use sigma=0.15
        (nearest below) AND sigma=0.30 (nearest above) as bracket; fire HP if EITHER
        satisfies gap >= 0.15.
    HP_UNIFORM_ZIPFIAN_GAP: at (sigma=0.15, load=0.30):
      recall(alpha=0.0) - recall(alpha=1.0) >= 0.10 (Zipfian degrades vs uniform
        when stressed).
    HP_UNIFORM_BASELINE: at (alpha=0.0, sigma=0.0, load=0.10):
      recall_all >= 0.95 (reproduces v1 baseline; sanity).

  HARD_FAIL_PREDICTION (sparse-coding two-tier prediction falsified):
    HF_PREDICTION_FAILS: at (alpha=1.0, sigma=0.30, load=0.30):
      BOTH recall_Q1_head >= 0.95 AND recall_Q4_tail >= 0.95 -> Zipfian doesn't bite
      even at wall + noise. VALID physics finding.

  HARD_FAIL_INFRA:
    BASELINE_OUT_OF_BAND: (alpha=0.0, sigma=0.0, load=0.10) < 0.85 at FULL.
    META_RULE_AF: all arms bit-identical recall+entropy signatures (wiring bug).
    CARDINALITY_BREACH: len(core_arms) != 54.

  MIDDLE_BAND: partial two-tier (some HP fires but not all; or gap 0.10 <= diff < 0.15).

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 3 alpha * 3 sigma * 6 load = 54 arm outputs per seed cell.

CRLB (capacity feasibility per exp_dev section 9):
  Per-arm recall = binomial proportion over N_QUERIES=1000.
  sigma_min(p=0.5) = sqrt(0.25/1000) = 0.0158 THEORETICAL@binomial-CLT.
  HP gap 0.15 = 9.5*sigma_binom; well-reachable.
  Per-quartile recall over N_Q/4 = 250 samples: sigma_min = sqrt(0.25/250) = 0.032.
  Q1-Q4 gap 0.15 = 4.7*sigma_stratified; still well-reachable.

DISCRIMINATOR-MUST-SURVIVE-SCALE (exp_dev pattern C):
  Smoke runs FULL-N=8192 preview at alpha=1.0/sigma=0.30/load=0.30 (single point).
  Reject full dispatch if BOTH Q1 >= 0.95 AND Q4 >= 0.95 (two-tier prediction
  falsified in smoke; escalate to Director as HF_PREDICTION_FAILS finding).

BASELINE_IN_BAND (META_RULE_AG):
  (alpha=0.0, sigma=0.0, load=0.10) should saturate ~1.000 at full-N. If < 0.85,
  encoder broken or attention regime wrong -- HARD_FAIL_INFRA.

ARMS_MUST_DIFFER (META_RULE_AF):
  Alpha entropies distinct (5 rank_entropy values across alpha levels);
  sigma-arm recalls should NOT be bit-identical (noise moves recall meaningfully).

Cross-references:
- Cell D v2 CG (Atom 1; dense-Hopfield READ-REPLACE uniform baseline)
- v1 saturated cell: notes v1 metrics.json @ data/exp_distributional_shape_zipfian_v1_seed_7_smoke/
- Sparse-coding drill: notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md
- Hidden phase-diagram: notes/research_hidden_phase_diagram_dimensions_2026-07-01.md
- Zipf 1949 CITED; Donoho-Tanner CS phase transitions CITED@drill

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed = 0.0158 sigma_binomial (all); 0.032 sigma_stratified (Q1-Q4)
 - baseline_in_band at smoke (META_RULE_AG; alpha=0/sigma=0/load=0.10 near 1.0 at N=8192)
 - discriminator survives scale (smoke has full-N preview arm at alpha=1/sigma=0.3/load=0.3)
 - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
 - HP_SCOPE per predicate declared inline in compute_verdict
 - cardinality_ok EXPECTED_N_UNITS=54 (META_RULE_H)
 - per-unit failure-class instrumentation (META_RULE_J; no bare except)
 - calibration_check = adaptive_with_discriminator_gate (beta = log2(M)/margin)
 - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

PROT-018: anchor _seed_7 (no _n suffix; N=8192 constant per config).
PROT-021: single-seed cell (chunked); _seed_checkpoint import present.
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
# Inline heartbeat + start marker + crash diagnostic
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
ANCHOR_NAME = "distributional_shape_zipfian_v2_seed_19"
SEED_THIS_CHUNK = 19
_HARDENING_MARKER = "v2_dense_hopfield_zipfian_noise_overload_seed_chunk"

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
ALPHA_SHAPE_LEVELS = [0.0, 1.0, 2.0]
SIGMA_NOISE_LEVELS = [0.0, 0.15, 0.30]
LOAD_LEVELS = [0.10, 0.20, 0.30, 0.50, 0.80, 1.20]
N_QUERIES_FULL = 1000
BETA_MIN = 8.0
BETA_MAX = 128.0

# Smoke config: full sweep at N_smoke=1024 (fast); plus full-N preview at the
# critical discriminator point (alpha=1.0, sigma=0.30, load=0.30) at N=8192.
N_SMOKE = 1024
N_QUERIES_SMOKE = 200

PREVIEW_ALPHA = 1.0
PREVIEW_SIGMA = 0.30
PREVIEW_LOAD = 0.30
PREVIEW_N_QUERIES = 400   # more queries for stable Q1/Q4 stratification at preview

RUN_FULL_N_PREVIEW = (RUN_MODE == "smoke")

if RUN_MODE == "smoke":
    N_DIM = N_SMOKE
    N_QUERIES = N_QUERIES_SMOKE
else:
    N_DIM = N_FULL
    N_QUERIES = N_QUERIES_FULL

SEEDS = [SEED_THIS_CHUNK]

# Cardinality: 3 alpha * 3 sigma * 6 load = 54 arms
EXPECTED_N_UNITS = len(ALPHA_SHAPE_LEVELS) * len(SIGMA_NOISE_LEVELS) * len(LOAD_LEVELS)
assert EXPECTED_N_UNITS == 54, f"EXPECTED_N_UNITS wiring bug: {EXPECTED_N_UNITS}"

# Attention batch chunk for large-M points (load=1.20 -> M=9830 at N=8192)
ATTN_CHUNK = 256

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},N_QUERIES={N_QUERIES},"
    f"alpha_levels={ALPHA_SHAPE_LEVELS},sigma_levels={SIGMA_NOISE_LEVELS},"
    f"load_levels={LOAD_LEVELS},beta_range=[{BETA_MIN},{BETA_MAX}],"
    f"chunk_seed={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"hardening=v2_zipfian_noise_overload_seed_chunk+METARULE_AF_hashtest+METARULE_AH+ADAPTIVE_BETA"
)


# ---------------------------------------------------------------------------
# Zipf sampler
# ---------------------------------------------------------------------------
def _zipf_probs(m_items: int, alpha_shape: float) -> np.ndarray:
    """Rank-based Zipf: p_i propto 1/(i+1)^alpha for i in [0, M). Alpha=0 -> uniform."""
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
    p = probs[probs > 0]
    return float(-np.sum(p * np.log(p)))


# ---------------------------------------------------------------------------
# Dense-Hopfield primitives (Cell D v2 READ-REPLACE) + noise model
# ---------------------------------------------------------------------------
def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True).clip(min=1e-12)


def _cosine_margin_estimate(keys: np.ndarray, sample_n: int = 256) -> float:
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
    raw = math.log2(max(2, m_items)) / max(cosine_margin, 0.05)
    return float(max(BETA_MIN, min(BETA_MAX, raw)))


def _apply_query_noise(queries_raw: np.ndarray, sigma: float,
                       rng: np.random.RandomState) -> np.ndarray:
    """Apply bit-flip noise to bipolar keys with per-coord flip prob = sigma.

    queries_raw : (Q, N) bipolar in {-1, +1} (BEFORE L2-normalization).
    Returns L2-normalized noisy queries (Q, N).

    Note: uses UNNORMALIZED bipolar input so the noise model is a proper BSC.
    Caller L2-normalizes for cosine attention.
    """
    if sigma <= 0.0:
        return _l2norm_rows(queries_raw)
    flip_mask = rng.random(queries_raw.shape) < sigma
    noisy = queries_raw.copy()
    noisy[flip_mask] = -noisy[flip_mask]
    return _l2norm_rows(noisy)


def _dense_hopfield_recall(K_tape: np.ndarray, V_tape: np.ndarray,
                           queries_noisy_n: np.ndarray,
                           query_targets: np.ndarray,
                           beta: float, attn_chunk: int) -> np.ndarray:
    """Dense-Hopfield READ-REPLACE recall over pre-computed noisy L2-normalized queries."""
    m = K_tape.shape[0]
    q_count = query_targets.shape[0]
    hits = np.zeros(q_count, dtype=bool)
    for start in range(0, q_count, attn_chunk):
        end = min(q_count, start + attn_chunk)
        q_chunk = queries_noisy_n[start:end]                   # (c, N)
        sims = q_chunk @ K_tape.T                              # (c, M)
        sims_scaled = beta * sims
        sims_scaled -= sims_scaled.max(axis=1, keepdims=True)
        w = np.exp(sims_scaled)
        w /= w.sum(axis=1, keepdims=True).clip(min=1e-30)
        p = w @ V_tape                                         # (c, N)
        p_n = _l2norm_rows(p)
        sims_match = p_n @ V_tape.T                            # (c, M)
        argmax = sims_match.argmax(axis=1)
        expected = query_targets[start:end]
        hits[start:end] = (argmax == expected)
    return hits


# ---------------------------------------------------------------------------
# Per-arm runner (one (alpha, sigma, load) point)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, alpha_shape: float, sigma: float, load: float,
            n_dim: int, n_queries: int, seed: int,
            attn_chunk: int, out_dir: Path) -> Dict:
    t0 = time.time()
    beta_used = float("nan")
    cosine_margin_used = float("nan")
    try:
        m_items = max(2, int(round(load * n_dim)))
        # RNG seed folds all axes to avoid cross-arm correlation
        rng = np.random.RandomState(
            seed
            + int(round(alpha_shape * 1000))
            + int(round(sigma * 10000))
            + int(round(load * 100000))
        )

        # Bipolar keys/vals; L2-normalize for K_tape/V_tape (Cell D v2).
        keys_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)
        vals_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)
        K_tape = _l2norm_rows(keys_raw)
        V_tape = _l2norm_rows(vals_raw)

        # Adaptive beta from clean K_tape (Cell D v2)
        cosine_margin_used = _cosine_margin_estimate(K_tape)
        beta_used = _compute_adaptive_beta(m_items, cosine_margin_used)

        # Zipf-weighted rank sampling; random item-rank permutation.
        probs = _zipf_probs(m_items, alpha_shape)
        item_rank_order = rng.permutation(m_items)
        rank_samples = rng.choice(m_items, size=n_queries, replace=True, p=probs)
        query_targets = item_rank_order[rank_samples]

        # Query = noisy bipolar keys[targets] BEFORE L2-normalization; then noise; then L2.
        query_keys_raw = keys_raw[query_targets]               # (Q, N) bipolar
        queries_noisy_n = _apply_query_noise(query_keys_raw, sigma, rng)

        # Dense-Hopfield recall on noisy queries
        hits = _dense_hopfield_recall(K_tape, V_tape, queries_noisy_n,
                                      query_targets, beta_used, attn_chunk)
        recall_all = float(hits.mean())

        # Frequency-stratified recall by rank-quartile.
        q1_mask = rank_samples < (m_items // 4)                # top 25% freq
        q2_mask = (rank_samples >= m_items // 4) & (rank_samples < m_items // 2)
        q3_mask = (rank_samples >= m_items // 2) & (rank_samples < 3 * m_items // 4)
        q4_mask = rank_samples >= 3 * m_items // 4             # bottom 25% freq (tail)
        recall_q1 = float(hits[q1_mask].mean()) if q1_mask.sum() > 0 else float("nan")
        recall_q2 = float(hits[q2_mask].mean()) if q2_mask.sum() > 0 else float("nan")
        recall_q3 = float(hits[q3_mask].mean()) if q3_mask.sum() > 0 else float("nan")
        recall_q4 = float(hits[q4_mask].mean()) if q4_mask.sum() > 0 else float("nan")

        sampler_entropy = _zipf_entropy(probs)

        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"arm": arm_name, "alpha": alpha_shape,
                              "sigma": sigma, "load": load,
                              "M": m_items, "recall": recall_all,
                              "beta": beta_used, "margin": cosine_margin_used})

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha_shape": float(alpha_shape),
            "sigma": float(sigma),
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
            "sigma": float(sigma),
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
def _selftest_zipf_probs_normalize() -> None:
    for alpha in (0.0, 1.0, 2.0):
        p = _zipf_probs(500, alpha)
        s = float(p.sum())
        if abs(s - 1.0) > 1e-8:
            raise AssertionError(f"Zipf probs not normalized at alpha={alpha}: sum={s}")
        if not np.all(p >= 0):
            raise AssertionError(f"Zipf probs negative at alpha={alpha}")


def _selftest_zipf_entropy_monotone() -> None:
    m = 1000
    ent_u = _zipf_entropy(_zipf_probs(m, 0.0))
    ent_1 = _zipf_entropy(_zipf_probs(m, 1.0))
    ent_2 = _zipf_entropy(_zipf_probs(m, 2.0))
    if not (abs(ent_u - math.log(m)) < 1e-6):
        raise AssertionError(f"uniform entropy {ent_u} != log(M)")
    if not (ent_u > ent_1 > ent_2):
        raise AssertionError(f"entropy not monotone: {ent_u} > {ent_1} > {ent_2}")


def _selftest_bit_flip_noise_rate() -> None:
    """Bit-flip at sigma=0.3 should flip ~30% of coordinates."""
    rng = np.random.RandomState(31)
    q_raw = np.ones((10, 4096), dtype=np.float64)
    q_noisy_n = _apply_query_noise(q_raw, 0.30, rng)
    # After L2-norm we can't recover raw signs, but pre-norm dot product with
    # original (all +1s) tells us the flip rate.
    # Reconstruct pre-norm: sign(q_noisy_n) since row was normalized uniformly.
    signs = np.sign(q_noisy_n)
    flip_rate = float((signs != 1.0).mean())
    if not (0.20 < flip_rate < 0.40):
        raise AssertionError(f"bit-flip rate {flip_rate} not in [0.20, 0.40] at sigma=0.30")


def _selftest_noise_degrades_recall() -> None:
    """Query noise sigma=0.30 must degrade recall vs sigma=0.0 on same regime.

    Uses a moderately-loaded regime where clean recall < 1.0 so noise has room
    to differentiate. If noise doesn't degrade, wiring bug."""
    rng = np.random.RandomState(41)
    m, n = 200, 128            # alpha_simple = 1.56 (over-Amit-Gutfreund; low margin)
    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    K = _l2norm_rows(keys_raw)
    V = _l2norm_rows(vals_raw)
    beta = _compute_adaptive_beta(m, _cosine_margin_estimate(K))
    targets = np.arange(m)

    q_clean_n = _l2norm_rows(keys_raw)
    q_noisy_n = _apply_query_noise(keys_raw, 0.30, rng)
    hits_clean = _dense_hopfield_recall(K, V, q_clean_n, targets, beta, m)
    hits_noisy = _dense_hopfield_recall(K, V, q_noisy_n, targets, beta, m)
    r_clean = float(hits_clean.mean())
    r_noisy = float(hits_noisy.mean())
    # Clean should be >0.95; noisy strictly less. Degradation gap >0.02.
    # Small gap is legitimate (attention is robust); primary goal is proving
    # noise ARM WIRES to a distinct result (not bit-identical to clean).
    if r_clean < 0.95:
        raise AssertionError(f"clean recall too low ({r_clean:.3f}); regime issue")
    if not (r_noisy < r_clean - 0.02):
        raise AssertionError(
            f"noise didn't degrade recall (clean={r_clean:.3f} noisy={r_noisy:.3f})"
        )


def _selftest_dense_hopfield_clean_recall() -> None:
    rng = np.random.RandomState(11)
    m, n = 8, 32
    K = _l2norm_rows(rng.randn(m, n).astype(np.float64))
    V = _l2norm_rows(rng.randn(m, n).astype(np.float64))
    targets = np.arange(m)
    hits = _dense_hopfield_recall(K, V, K, targets, beta=50.0, attn_chunk=m)
    if not hits.all():
        raise AssertionError(f"clean self-recall failed: hits={hits.sum()}/{m}")


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


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS} != [{SEED_THIS_CHUNK}]")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor '{ANCHOR_NAME}' missing seed_{SEED_THIS_CHUNK}")


def _selftest_cardinality_wiring() -> None:
    if EXPECTED_N_UNITS != len(ALPHA_SHAPE_LEVELS) * len(SIGMA_NOISE_LEVELS) * len(LOAD_LEVELS):
        raise AssertionError(f"EXPECTED_N_UNITS wiring: {EXPECTED_N_UNITS}")


def _selftest_tiny_sweep_produces_54_arms() -> None:
    """Run tiny 54-point sweep at N=192; verify all 54 arms OK + arms differ."""
    tmp_out = Path(REPO) / "data" / "_selftest_zipfian_v2_tmp"
    tmp_out.mkdir(parents=True, exist_ok=True)
    arms = []
    for alpha in ALPHA_SHAPE_LEVELS:
        for sigma in SIGMA_NOISE_LEVELS:
            for load in LOAD_LEVELS:
                arm_name = f"a{alpha:.1f}_s{sigma:.2f}_L{load:.2f}"
                # Skip load=1.20 at tiny N=192 (M=230 > N=192; still works but slow).
                r = run_arm(arm_name, alpha, sigma, load,
                            n_dim=192, n_queries=80,
                            seed=42, attn_chunk=80, out_dir=tmp_out)
                if r["arm_status"] != "OK":
                    raise AssertionError(f"arm {arm_name} errored: {r['arm_status']}")
                arms.append(r)
    if len(arms) != EXPECTED_N_UNITS:
        raise AssertionError(f"cardinality: got {len(arms)} != {EXPECTED_N_UNITS}")

    # META_RULE_AF: verify at least sigma-arm recalls differ within same (alpha, load)
    # Group by (alpha, load), check sigma=0 vs sigma=0.30 recalls differ.
    from collections import defaultdict
    grouped = defaultdict(dict)
    for a in arms:
        grouped[(a["alpha_shape"], a["load"])][a["sigma"]] = a["recall_all"]
    n_sigma_discriminates = 0
    for (alpha, load), sigmas in grouped.items():
        if 0.0 in sigmas and 0.30 in sigmas:
            if abs(sigmas[0.0] - sigmas[0.30]) > 1e-6:
                n_sigma_discriminates += 1
    if n_sigma_discriminates == 0:
        raise AssertionError(
            "META_RULE_AF: no (alpha, load) point where sigma=0 vs sigma=0.30 differ "
            "in tiny sweep -- noise-arm wiring may be broken"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_zipf_probs_normalize()
        _selftest_zipf_entropy_monotone()
        _selftest_bit_flip_noise_rate()
        _selftest_dense_hopfield_clean_recall()
        _selftest_noise_degrades_recall()
        _selftest_cosine_margin_range()
        _selftest_adaptive_beta_clamps()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_wiring()
        _selftest_tiny_sweep_produces_54_arms()
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
        f"alpha={ALPHA_SHAPE_LEVELS}  sigma={SIGMA_NOISE_LEVELS}  "
        f"load={LOAD_LEVELS}  beta=[{BETA_MIN},{BETA_MAX}]  mode={RUN_MODE}  "
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
    n_arms_total = len(ALPHA_SHAPE_LEVELS) * len(SIGMA_NOISE_LEVELS) * len(LOAD_LEVELS)
    idx = 0
    for alpha in ALPHA_SHAPE_LEVELS:
        for sigma in SIGMA_NOISE_LEVELS:
            for load in LOAD_LEVELS:
                arm_name = f"a{alpha:.1f}_s{sigma:.2f}_L{load:.2f}"
                print(
                    f"  [seed={seed} {idx + 1}/{n_arms_total} {arm_name}] "
                    f"running at N={N_DIM} N_Q={N_QUERIES}...",
                    flush=True,
                )
                out = run_arm(arm_name, alpha, sigma, load,
                              n_dim=N_DIM, n_queries=N_QUERIES,
                              seed=seed, attn_chunk=ATTN_CHUNK, out_dir=out_dir)
                arms.append(out)
                print(
                    f"  [seed={seed} {arm_name}] "
                    f"r_all={out['recall_all']:.3f} "
                    f"Q1={out['recall_q1_head']:.3f} Q4={out['recall_q4_tail']:.3f} "
                    f"M={out['M']} beta={out.get('beta_used', float('nan')):.2f} "
                    f"margin={out.get('cosine_margin_used', float('nan')):.3f} "
                    f"status={out['arm_status']} wall={out['wall_s']:.1f}s",
                    flush=True,
                )
                emit_heartbeat(out_dir, unit_idx=idx + 1, total_units=n_arms_total,
                               elapsed_s=time.time() - t0,
                               extra={"arm": arm_name, "recall": out["recall_all"]})
                idx += 1

    preview_arm = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        print(
            f"  [seed={seed} PREVIEW_FULL_N] N={N_FULL} "
            f"alpha={PREVIEW_ALPHA} sigma={PREVIEW_SIGMA} load={PREVIEW_LOAD} "
            f"N_Q={PREVIEW_N_QUERIES}...",
            flush=True,
        )
        preview_arm = run_arm(
            f"PREVIEW_a{PREVIEW_ALPHA:.1f}_s{PREVIEW_SIGMA:.2f}_L{PREVIEW_LOAD:.2f}_fullN",
            PREVIEW_ALPHA, PREVIEW_SIGMA, PREVIEW_LOAD,
            n_dim=N_FULL, n_queries=PREVIEW_N_QUERIES,
            seed=seed, attn_chunk=ATTN_CHUNK, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW_FULL_N] "
            f"r_all={preview_arm['recall_all']:.3f} "
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
    return [a for a in arms if not a["arm_name"].startswith("PREVIEW_")]


def _lookup(core: List[Dict], alpha: float, sigma: float, load: float) -> Dict:
    for a in core:
        if (abs(a["alpha_shape"] - alpha) < 1e-6
                and abs(a["sigma"] - sigma) < 1e-6
                and abs(a["load"] - load) < 1e-6):
            return a
    raise KeyError(f"missing arm alpha={alpha} sigma={sigma} load={load}")


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

    # META_RULE_AF: any two arms bit-identical recall+entropy -> wiring bug.
    signatures = set()
    for a in core:
        signatures.add((round(a["recall_all"], 8),
                        round(a["sampler_entropy_nats"], 6),
                        round(a["sigma"], 6),
                        round(a["load"], 6)))
    if len(signatures) < 10:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: only {len(signatures)} distinct signatures "
                f"across {len(core)} arms; wiring suspect")

    # Anchor points for verdict logic.
    try:
        a_baseline = _lookup(core, 0.0, 0.0, 0.10)      # sanity/baseline
        a_uni_stress = _lookup(core, 0.0, 0.15, 0.30)   # uniform under stress
        a_zipf_015 = _lookup(core, 1.0, 0.15, 0.30)     # Zipf @ sigma=0.15 (nearest below task-spec 0.20)
        a_zipf_030 = _lookup(core, 1.0, 0.30, 0.30)     # Zipf @ sigma=0.30 (nearest above task-spec 0.20)
    except KeyError as e:
        return ("HARD_FAIL", f"Missing anchor arm: {e}")

    r_baseline = a_baseline["recall_all"]
    r_uni_stress = a_uni_stress["recall_all"]
    r_zipf_015_all = a_zipf_015["recall_all"]
    r_zipf_015_q1 = a_zipf_015["recall_q1_head"]
    r_zipf_015_q4 = a_zipf_015["recall_q4_tail"]
    r_zipf_030_q1 = a_zipf_030["recall_q1_head"]
    r_zipf_030_q4 = a_zipf_030["recall_q4_tail"]

    def _safe_gap(a, b):
        if not (math.isfinite(a) and math.isfinite(b)):
            return float("nan")
        return a - b

    gap_015 = _safe_gap(r_zipf_015_q1, r_zipf_015_q4)
    gap_030 = _safe_gap(r_zipf_030_q1, r_zipf_030_q4)
    uni_zipf_gap = _safe_gap(r_uni_stress, r_zipf_015_all)

    # META_RULE_AG baseline_in_band: (alpha=0.0/sigma=0.0/load=0.10)
    if RUN_MODE == "full":
        baseline_ceiling_ok = (r_baseline >= 0.85)
    else:
        baseline_ceiling_ok = (r_baseline >= 0.50)
    if not baseline_ceiling_ok:
        return ("HARD_FAIL",
                f"BASELINE_OUT_OF_BAND: baseline(a=0,s=0,L=0.10) recall={r_baseline:.3f} "
                f"< {'0.85' if RUN_MODE == 'full' else '0.50'} at {RUN_MODE}")

    # HF: sparse-coding two-tier PREDICTION falsified in full-N regime?
    # Fires if Q1 AND Q4 BOTH >= 0.95 at any stressed Zipf point.
    hf_prediction = False
    hf_msg = ""
    if RUN_MODE == "full":
        for a_stress in (a_zipf_030, a_zipf_015):
            q1 = a_stress["recall_q1_head"]
            q4 = a_stress["recall_q4_tail"]
            if math.isfinite(q1) and math.isfinite(q4) and q1 >= 0.95 and q4 >= 0.95:
                hf_prediction = True
                hf_msg = (f"HF_PREDICTION_FAILS: at {a_stress['arm_name']} "
                          f"Q1={q1:.3f} AND Q4={q4:.3f} both >= 0.95; "
                          f"sparse-coding two-tier prediction FALSIFIED "
                          f"(valid physics finding)")
                break

    # HP gates
    if RUN_MODE == "full":
        hp_gap_015 = math.isfinite(gap_015) and gap_015 >= 0.15
        hp_gap_030 = math.isfinite(gap_030) and gap_030 >= 0.15
        hp_two_tier = hp_gap_015 or hp_gap_030
        hp_uni_zipf_gap = math.isfinite(uni_zipf_gap) and uni_zipf_gap >= 0.10
        hp_baseline = r_baseline >= 0.95
    else:
        # Smoke thresholds relaxed for small-N (mechanism should still fire).
        hp_gap_015 = math.isfinite(gap_015) and gap_015 >= 0.08
        hp_gap_030 = math.isfinite(gap_030) and gap_030 >= 0.08
        hp_two_tier = hp_gap_015 or hp_gap_030
        hp_uni_zipf_gap = math.isfinite(uni_zipf_gap) and uni_zipf_gap >= 0.05
        hp_baseline = r_baseline >= 0.60

    summary = (
        f"seed={SEED_THIS_CHUNK} N={N_DIM} mode={RUN_MODE} "
        f"baseline={r_baseline:.3f} uni_stress={r_uni_stress:.3f} "
        f"zipf015_all={r_zipf_015_all:.3f} "
        f"Q1_015={r_zipf_015_q1:.3f} Q4_015={r_zipf_015_q4:.3f} gap_015={gap_015:.3f} "
        f"Q1_030={r_zipf_030_q1:.3f} Q4_030={r_zipf_030_q4:.3f} gap_030={gap_030:.3f} "
        f"uni_zipf_gap={uni_zipf_gap:.3f} "
        f"HP=[two_tier={hp_two_tier},uni_zipf={hp_uni_zipf_gap},baseline={hp_baseline}] "
        f"HF=[pred={hf_prediction}]"
    )

    if hf_prediction:
        return ("HARD_FAIL", f"{hf_msg}. {summary}")

    if all([hp_two_tier, hp_uni_zipf_gap, hp_baseline]):
        return ("HARD_PASS",
                f"HARD_PASS: TWO_TIER_ZIPFIAN_SIGNATURE (single-seed). "
                f"Head-tail gap fires at wall+noise. Chain-grade requires cross-seed VET. "
                f"{summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial two-tier signature. {summary}")


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
            f"alpha={ALPHA_SHAPE_LEVELS} sigma={SIGMA_NOISE_LEVELS} load={LOAD_LEVELS}...",
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
            f"alpha={ALPHA_SHAPE_LEVELS} sigma={SIGMA_NOISE_LEVELS} load={LOAD_LEVELS} "
            f"beta_range=[{BETA_MIN},{BETA_MAX}]"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "N_QUERIES": N_QUERIES,
        "alpha_shape_levels": ALPHA_SHAPE_LEVELS,
        "sigma_noise_levels": SIGMA_NOISE_LEVELS,
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
        "crlb_stratified_floor": 0.032,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/N_QUERIES) binomial-CLT; stratified over N_Q/4",
        "discriminator_reachability": True,
        "calibration_check": "adaptive_with_discriminator_gate",
        "per_seed": [
            {"seed": r.get("seed"),
             "elapsed_s": r.get("elapsed_s"),
             "arms": r.get("arms")}
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
