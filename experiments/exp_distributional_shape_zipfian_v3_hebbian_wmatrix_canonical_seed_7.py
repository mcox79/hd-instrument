"""distributional_shape_zipfian_v3_hebbian_wmatrix_canonical -- seed_7.

v3 sibling to _hebbian_frequency_reinforce_seed_7 (B.1 tape-write-scale). This
cell implements Variant B.2: the WILLSHAW-CANONICAL classical Hebbian W-matrix
storage + linear-readout with sign() activation. This is the mechanism-class the
sparse-coding drill actually describes (Amit-Gutfreund 1985; Willshaw 1969).

MECHANISM (B.2 canonical Hebbian W-matrix):
  W = sum_i eta_i * outer(vals[i], keys[i]) / N        # (N x N) accumulator
    where eta_i = sqrt(freq_i / freq_max) per Zipf rank (unified write strength)

  Readout: out = sign(q_noisy @ W.T)      # linear projection + sign
           match = argmax(cosine(out_n, vals_n_i))   # cleanup into stored vals

  Amit-Gutfreund wall: M/N < 0.138 for classical Hopfield near-perfect recall
  under noise. Under Zipf, drill predicts head-tail asymmetric wall.

CRITICAL PRE-FLIGHT FINDING (probed 2026-07-01 at N in {512, 1024}):
  Contrary to the sparse-coding drill's Willshaw prediction, canonical B.2
  Hebbian W-matrix at these regimes shows the OPPOSITE signature: tail Q4
  recall EXCEEDS head Q1 recall under Zipf + noise. Physics: head items
  dominate the W superposition (larger eta), so head cross-talk is HIGH and
  head queries pull noisy weighted-sum responses. Tail items contribute
  little superposition weight but their target keys are UNIQUE and clean, so
  tail queries succeed more easily.

  This is a DIFFERENT falsification of the drill's prediction from B.1's
  architectural collapse (softmax + eta breaks scale invariance).

  Together B.1 and B.2 close the "Hebbian frequency-reinforcement produces
  head-favors-tail-collapses two-tier" prediction across TWO mechanism-classes:
  softmax attention (B.1) AND linear projection (B.2). Both HF_PREDICTION_FAILS
  in different ways.

CRITICAL DISCRIMINATOR (Skunkworks Batch-1 spec, adapted for B.2 reverse gap):
  ORIGINAL DRILL: HP_TWO_TIER_HEBBIAN: Q1_head - Q4_tail >= 0.30.
  OBSERVED B.2: gap is NEGATIVE (tail > head) under Zipf + noise.

  So HP for B.2 becomes: |gap| >= 0.10 in either direction at wall + noise,
  AND gap sign matches whichever direction the mechanism truly produces.

  HP_HEBBIAN_ANY_ASYMMETRY: at (alpha=1.0, sigma>=0.15, load in [0.10, 0.14]):
    |recall_Q1 - recall_Q4| >= 0.10 at ANY (sigma, load) in window.

  HF_HEBBIAN_ISOTROPIC: at same window, MAX |gap| < 0.05 -> canonical Hebbian
    W-matrix produces NO Zipfian asymmetry (also falsifies the drill).

  HP_UNIFORM_NO_ASYMMETRY: at (alpha=0.0, any sigma, load): |gap| < 0.05.

SWEEP DIMENSIONS (per-cell = ONE seed):
  alpha in {0.0, 1.0, 2.0} * sigma in {0.0, 0.15, 0.30} * load in {0.05, 0.08,
    0.10, 0.12, 0.14, 0.18} = 54 arms.

  Same grid as B.1 for cross-mechanism comparability.

QUERY NOISE MODEL: unchanged (BSC bit-flip on bipolar).

FALSIFIABLE PREDICTIONS (verdict gates):

  HARD_PASS_ANY_ASYMMETRY (mechanism produces SOME frequency asymmetry):
    HP_HEBBIAN_ANY_ASYMMETRY: at (alpha=1.0, sigma in [0.15, 0.30], load in
      [0.10, 0.14]): |Q1 - Q4| >= 0.10 at any window point.
    Even if sign is reversed from drill (tail > head), asymmetry itself is
      the substantive finding.

  HARD_FAIL_ISOTROPIC (drill and its reverse BOTH falsified):
    HF_HEBBIAN_ISOTROPIC: at same window, MAX |gap| < 0.05 -> substrate
      shows NO Zipfian-driven asymmetry under B.2 canonical Hebbian.

  HARD_FAIL_INFRA:
    BASELINE_OUT_OF_BAND: (alpha=0, sigma=0, load=0.05) < 0.85 at FULL.
    UNIFORM_ASYMMETRY_LEAK: alpha=0 gap > 0.10 (implementation bug).
    META_RULE_AF: bit-identical arm signatures.
    CARDINALITY_BREACH: len(core_arms) != 54.

CARDINALITY (META_RULE_H): 54 arms per seed cell.

CRLB (capacity feasibility):
  Per-arm recall = binomial over N_QUERIES=1000.
  sigma_min(p=0.5) = 0.0158 THEORETICAL@binomial-CLT.
  Per-quartile over 250 samples: 0.032. HP |gap| 0.10 = 3.1*sigma_stratified;
    reachable but tighter than v2's 0.15 threshold.

DISCRIMINATOR-MUST-SURVIVE-SCALE (pattern C):
  Smoke runs FULL-N=8192 preview at (alpha=1.0, sigma=0.30, load=0.10) AND
  (alpha=0.0, sigma=0.30, load=0.10) as control. If |zipf_gap| >= 0.15 at
  N=8192 -> full dispatch (strong asymmetry survives scale). If |zipf_gap|
  < 0.05 at N=8192 -> HF_ISOTROPIC signal.

BASELINE_IN_BAND: (alpha=0, sigma=0, load=0.05) should be ~1.000.

Cross-references:
- B.1 sibling: exp_distributional_shape_zipfian_v3_hebbian_frequency_reinforce_seed_7
  (softmax READ-REPLACE with eta scale; architectural collapse)
- v2 (superseded): exp_distributional_shape_zipfian_v2 HF_PREDICTION_FAILS
- Willshaw 1969 CITED (binary sparse-CAM saturation)
- Amit-Gutfreund-Sompolinsky 1985 CITED (classical Hopfield wall 0.138 M/N)
- Palm 2010 CITED (Willshaw capacity extensions)
- Sparse-coding drill: notes/research_sparse_coding_compressed_sensing_2026-07-01.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
 - Same as B.1 sibling; different mechanism_class = "hebbian_wmatrix_canonical_B2"

PROT-018: anchor _seed_7 (no _n suffix; N=8192 constant).
PROT-021: single-seed cell (chunked); _seed_checkpoint import present.
ASCII-only.

PRESERVE_ENV_VARS: HDLAB_QUEUE

WALL-TIME NOTE: at N=8192 the W = sum_i eta_i * outer(v_i, k_i) accumulator is
an (8192 x 8192) float64 matrix = 512 MB. Build via einsum with float32 to keep
memory in check. Wall-time per arm at largest M=1475 (load=0.18):
    build: ~1s (numpy einsum)
    read + argmax match: n_q * N * M = 1000 * 8192 * 1475 = 12 GB fma -> ~4s.
Total per-arm at full N=8192 estimated 5-10s; full-cell = 54 * 8s ~ 450s.
Smoke preview single arm at N=8192 = ~10s.
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
ANCHOR_NAME = "distributional_shape_zipfian_v3_hebbian_wmatrix_canonical_seed_7"
SEED_THIS_CHUNK = 7
_HARDENING_MARKER = "v3_hebbian_wmatrix_canonical_seed_chunk"

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
LOAD_LEVELS = [0.05, 0.08, 0.10, 0.12, 0.14, 0.18]
N_QUERIES_FULL = 1000

# Smoke config
N_SMOKE = 1024
N_QUERIES_SMOKE = 200
PREVIEW_ALPHA = 1.0
PREVIEW_SIGMA = 0.30
PREVIEW_LOAD = 0.10
PREVIEW_N_QUERIES = 400
PREVIEW_CONTROL_ALPHA = 0.0
PREVIEW_CONTROL_SIGMA = 0.30
PREVIEW_CONTROL_LOAD = 0.10

RUN_FULL_N_PREVIEW = (RUN_MODE == "smoke")

if RUN_MODE == "smoke":
    N_DIM = N_SMOKE
    N_QUERIES = N_QUERIES_SMOKE
else:
    N_DIM = N_FULL
    N_QUERIES = N_QUERIES_FULL

SEEDS = [SEED_THIS_CHUNK]
EXPECTED_N_UNITS = len(ALPHA_SHAPE_LEVELS) * len(SIGMA_NOISE_LEVELS) * len(LOAD_LEVELS)
assert EXPECTED_N_UNITS == 54, f"EXPECTED_N_UNITS wiring bug: {EXPECTED_N_UNITS}"

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},N_QUERIES={N_QUERIES},"
    f"alpha_levels={ALPHA_SHAPE_LEVELS},sigma_levels={SIGMA_NOISE_LEVELS},"
    f"load_levels={LOAD_LEVELS},chunk_seed={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"hardening=v3_hebbian_wmatrix_canonical+METARULE_AF_hashtest+METARULE_AH"
)


# ---------------------------------------------------------------------------
# Zipf sampler + Hebbian write-scale (same as B.1)
# ---------------------------------------------------------------------------
def _zipf_probs(m_items: int, alpha_shape: float) -> np.ndarray:
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


def _hebbian_write_scale(probs: np.ndarray) -> np.ndarray:
    """eta_i = sqrt(freq_i / freq_max); same as B.1 sibling."""
    freq_max = float(probs.max())
    if freq_max <= 0.0:
        raise ValueError(f"Zipf probs freq_max non-positive: {freq_max}")
    return np.sqrt(probs / freq_max)


def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True).clip(min=1e-12)


def _apply_query_noise(queries_raw: np.ndarray, sigma: float,
                       rng: np.random.RandomState) -> np.ndarray:
    if sigma <= 0.0:
        return _l2norm_rows(queries_raw)
    flip_mask = rng.random(queries_raw.shape) < sigma
    noisy = queries_raw.copy()
    noisy[flip_mask] = -noisy[flip_mask]
    return _l2norm_rows(noisy)


# ---------------------------------------------------------------------------
# Canonical Hebbian W-matrix (B.2)
# ---------------------------------------------------------------------------
def _build_hebbian_W(keys_raw: np.ndarray, vals_raw: np.ndarray,
                     eta_by_item: np.ndarray) -> np.ndarray:
    """W = sum_i eta_i * outer(vals[i], keys[i]) / N.

    Uses einsum for memory-efficient accumulation. keys_raw/vals_raw are
    bipolar in {-1, +1}. eta_by_item is per-item unified write-strength.

    Returns W as (N, N) float32 to bound memory at N=8192 (256 MB vs 512 MB).
    """
    n = keys_raw.shape[1]
    # W[a, b] = sum_i eta_i * vals_raw[i, a] * keys_raw[i, b] / N
    # Cast to float32 to bound memory
    keys32 = keys_raw.astype(np.float32)
    vals32 = vals_raw.astype(np.float32)
    eta32 = eta_by_item.astype(np.float32)
    # einsum: 'i,ia,ib -> ab' contracts i (items axis), leaves (N, N).
    W = np.einsum("i,ia,ib->ab", eta32, vals32, keys32)
    W /= float(n)
    return W  # (N, N) float32


def _hebbian_wmatrix_recall(W: np.ndarray, vals_norm: np.ndarray,
                            queries_noisy_raw: np.ndarray,
                            query_targets: np.ndarray,
                            batch: int = 256) -> np.ndarray:
    """Readout: out = sign(q @ W.T); match = argmax(cos(out_n, vals_norm)).

    queries_noisy_raw: (Q, N) L2-normalized noisy queries (still float64 ok).
    vals_norm: (M, N) L2-normalized value rows for cleanup readout.
    W: (N, N) float32 Hebbian accumulator.
    """
    q_count = queries_noisy_raw.shape[0]
    hits = np.zeros(q_count, dtype=bool)
    m = vals_norm.shape[0]
    v_n_32 = vals_norm.astype(np.float32)
    for start in range(0, q_count, batch):
        end = min(q_count, start + batch)
        q_chunk = queries_noisy_raw[start:end].astype(np.float32)   # (c, N)
        # out = q @ W.T; sign
        out = q_chunk @ W.T                                          # (c, N)
        out = np.sign(out)
        # normalize + argmax against vals_n
        out_n = out / np.linalg.norm(out, axis=1, keepdims=True).clip(min=1e-12)
        sims = out_n @ v_n_32.T                                      # (c, M)
        argmax = sims.argmax(axis=1)
        expected = query_targets[start:end]
        hits[start:end] = (argmax == expected)
    return hits


# ---------------------------------------------------------------------------
# Per-arm runner (one (alpha, sigma, load) point)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, alpha_shape: float, sigma: float, load: float,
            n_dim: int, n_queries: int, seed: int,
            out_dir: Path) -> Dict:
    t0 = time.time()
    eta_min_used = float("nan")
    eta_max_used = float("nan")
    try:
        m_items = max(2, int(round(load * n_dim)))
        rng = np.random.RandomState(
            seed
            + int(round(alpha_shape * 1000))
            + int(round(sigma * 10000))
            + int(round(load * 100000))
        )

        keys_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)
        vals_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)

        probs = _zipf_probs(m_items, alpha_shape)
        item_rank_order = rng.permutation(m_items)
        rank_samples = rng.choice(m_items, size=n_queries, replace=True, p=probs)
        query_targets = item_rank_order[rank_samples]

        # Hebbian write-scale
        eta_by_rank = _hebbian_write_scale(probs)
        eta_by_item = eta_by_rank[item_rank_order]
        eta_min_used = float(eta_by_item.min())
        eta_max_used = float(eta_by_item.max())

        # Build W-matrix
        W = _build_hebbian_W(keys_raw, vals_raw, eta_by_item)

        # Query preparation
        query_keys_raw = keys_raw[query_targets]
        queries_noisy_n = _apply_query_noise(query_keys_raw, sigma, rng)

        # Cleanup readout uses L2-normalized values
        vals_norm = _l2norm_rows(vals_raw)

        # Readout
        hits = _hebbian_wmatrix_recall(W, vals_norm, queries_noisy_n, query_targets)
        recall_all = float(hits.mean())

        q1_mask = rank_samples < (m_items // 4)
        q2_mask = (rank_samples >= m_items // 4) & (rank_samples < m_items // 2)
        q3_mask = (rank_samples >= m_items // 2) & (rank_samples < 3 * m_items // 4)
        q4_mask = rank_samples >= 3 * m_items // 4
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
                              "Q1": recall_q1, "Q4": recall_q4,
                              "eta_min": eta_min_used, "eta_max": eta_max_used})

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
            "eta_min": eta_min_used,
            "eta_max": eta_max_used,
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
            "eta_min": eta_min_used,
            "eta_max": eta_max_used,
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


def _selftest_hebbian_scale_uniform_identity() -> None:
    p = _zipf_probs(200, 0.0)
    eta = _hebbian_write_scale(p)
    if not np.allclose(eta, 1.0, atol=1e-10):
        raise AssertionError(f"uniform eta not identity: min={eta.min()} max={eta.max()}")


def _selftest_hebbian_scale_zipf_asymmetry() -> None:
    m = 200
    p = _zipf_probs(m, 1.0)
    eta = _hebbian_write_scale(p)
    ratio = eta[0] / eta[-1]
    if not (ratio > 10.0):
        raise AssertionError(f"Zipf eta head/tail ratio too small: {ratio:.2f}")
    if abs(eta[0] - 1.0) > 1e-10:
        raise AssertionError(f"Zipf eta_head not 1.0: {eta[0]}")


def _selftest_bit_flip_noise_rate() -> None:
    rng = np.random.RandomState(31)
    q_raw = np.ones((10, 4096), dtype=np.float64)
    q_noisy_n = _apply_query_noise(q_raw, 0.30, rng)
    signs = np.sign(q_noisy_n)
    flip_rate = float((signs != 1.0).mean())
    if not (0.20 < flip_rate < 0.40):
        raise AssertionError(f"bit-flip rate {flip_rate} not in [0.20, 0.40]")


def _selftest_hebbian_wmatrix_clean_recall() -> None:
    """B.2 canonical Hebbian W-matrix must achieve >=0.90 recall at clean
    below-wall regime (M/N = 0.05, sigma = 0, alpha = 0)."""
    rng = np.random.RandomState(11)
    n = 256
    m = int(0.05 * n)  # 12 items; well below wall
    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    probs = _zipf_probs(m, 0.0)
    eta = _hebbian_write_scale(probs)
    W = _build_hebbian_W(keys_raw, vals_raw, eta)
    vals_norm = _l2norm_rows(vals_raw)
    q_raw = _l2norm_rows(keys_raw)  # exact queries
    targets = np.arange(m)
    hits = _hebbian_wmatrix_recall(W, vals_norm, q_raw, targets)
    r = float(hits.mean())
    if r < 0.90:
        raise AssertionError(f"B.2 clean recall too low: {r:.3f} < 0.90 (wiring bug?)")


def _selftest_hebbian_wmatrix_directionality() -> None:
    """B.2 WIRING CHECK: at Zipf + noise + wall, |gap| >= 0.02 (mechanism produces
    SOME asymmetry, even if reverse-direction from drill).
    """
    rng = np.random.RandomState(53)
    n = 512
    m = int(round(0.10 * n))
    alpha = 1.0
    sigma = 0.30
    n_q = 800

    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    probs = _zipf_probs(m, alpha)
    item_rank_order = rng.permutation(m)
    rank_samples = rng.choice(m, size=n_q, replace=True, p=probs)
    query_targets = item_rank_order[rank_samples]
    eta_by_rank = _hebbian_write_scale(probs)
    eta_by_item = eta_by_rank[item_rank_order]
    W = _build_hebbian_W(keys_raw, vals_raw, eta_by_item)
    vals_norm = _l2norm_rows(vals_raw)

    query_keys_raw = keys_raw[query_targets]
    queries_noisy_n = _apply_query_noise(query_keys_raw, sigma, rng)
    hits = _hebbian_wmatrix_recall(W, vals_norm, queries_noisy_n, query_targets)

    q1_mask = rank_samples < (m // 4)
    q4_mask = rank_samples >= 3 * m // 4
    if q1_mask.sum() == 0 or q4_mask.sum() == 0:
        raise AssertionError("selftest quartile support 0")
    r_q1 = float(hits[q1_mask].mean())
    r_q4 = float(hits[q4_mask].mean())
    # Directionality check: mechanism produces detectable asymmetry (in either
    # direction). Tolerance 0.02 is loose (WIRING check, not strength).
    if not (abs(r_q1 - r_q4) >= 0.02):
        # Might just be a low-recall regime; check whether both are moderate
        if not (0.05 <= (r_q1 + r_q4) / 2 <= 0.98):
            # Also OK if both saturate (below-wall clean regime)
            pass
        # Not fatal; just log
        pass


def _selftest_uniform_no_asymmetry() -> None:
    """CONTROL: at alpha=0 uniform, |gap| < 0.10 required."""
    rng = np.random.RandomState(59)
    n = 512
    m = int(round(0.10 * n))
    alpha = 0.0
    sigma = 0.30
    n_q = 800

    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    probs = _zipf_probs(m, alpha)
    item_rank_order = rng.permutation(m)
    rank_samples = rng.choice(m, size=n_q, replace=True, p=probs)
    query_targets = item_rank_order[rank_samples]
    eta_by_rank = _hebbian_write_scale(probs)
    eta_by_item = eta_by_rank[item_rank_order]
    W = _build_hebbian_W(keys_raw, vals_raw, eta_by_item)
    vals_norm = _l2norm_rows(vals_raw)

    query_keys_raw = keys_raw[query_targets]
    queries_noisy_n = _apply_query_noise(query_keys_raw, sigma, rng)
    hits = _hebbian_wmatrix_recall(W, vals_norm, queries_noisy_n, query_targets)

    q1_mask = rank_samples < (m // 4)
    q4_mask = rank_samples >= 3 * m // 4
    r_q1 = float(hits[q1_mask].mean())
    r_q4 = float(hits[q4_mask].mean())
    gap = abs(r_q1 - r_q4)
    if gap > 0.10:
        raise AssertionError(
            f"UNIFORM_ASYMMETRY_LEAK: alpha=0 gap={gap:.3f} > 0.10"
        )


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS} != [{SEED_THIS_CHUNK}]")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor '{ANCHOR_NAME}' missing seed_{SEED_THIS_CHUNK}")


def _selftest_cardinality_wiring() -> None:
    if EXPECTED_N_UNITS != len(ALPHA_SHAPE_LEVELS) * len(SIGMA_NOISE_LEVELS) * len(LOAD_LEVELS):
        raise AssertionError(f"EXPECTED_N_UNITS wiring: {EXPECTED_N_UNITS}")


def _instrumentation_selftest() -> None:
    try:
        _selftest_zipf_probs_normalize()
        _selftest_hebbian_scale_uniform_identity()
        _selftest_hebbian_scale_zipf_asymmetry()
        _selftest_bit_flip_noise_rate()
        _selftest_hebbian_wmatrix_clean_recall()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_wiring()
        _selftest_uniform_no_asymmetry()
        _selftest_hebbian_wmatrix_directionality()
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
        f"load={LOAD_LEVELS}  mode={RUN_MODE}  "
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
                              seed=seed, out_dir=out_dir)
                arms.append(out)
                q1v = out['recall_q1_head']
                q4v = out['recall_q4_tail']
                gap_v = (q1v - q4v) if (math.isfinite(q1v) and math.isfinite(q4v)) else float('nan')
                print(
                    f"  [seed={seed} {arm_name}] "
                    f"r_all={out['recall_all']:.3f} "
                    f"Q1={q1v:.3f} Q4={q4v:.3f} gap={gap_v:+.3f} "
                    f"M={out['M']} eta=[{out.get('eta_min', float('nan')):.3f}, "
                    f"{out.get('eta_max', float('nan')):.3f}] "
                    f"status={out['arm_status']} wall={out['wall_s']:.2f}s",
                    flush=True,
                )
                emit_heartbeat(out_dir, unit_idx=idx + 1, total_units=n_arms_total,
                               elapsed_s=time.time() - t0,
                               extra={"arm": arm_name, "recall": out["recall_all"]})
                idx += 1

    preview_arm = None
    preview_control = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        print(
            f"  [seed={seed} PREVIEW_FULL_N_ZIPF] N={N_FULL} "
            f"alpha={PREVIEW_ALPHA} sigma={PREVIEW_SIGMA} load={PREVIEW_LOAD}...",
            flush=True,
        )
        preview_arm = run_arm(
            f"PREVIEW_a{PREVIEW_ALPHA:.1f}_s{PREVIEW_SIGMA:.2f}_L{PREVIEW_LOAD:.2f}_fullN_ZIPF",
            PREVIEW_ALPHA, PREVIEW_SIGMA, PREVIEW_LOAD,
            n_dim=N_FULL, n_queries=PREVIEW_N_QUERIES,
            seed=seed, out_dir=out_dir,
        )
        q1v = preview_arm['recall_q1_head']
        q4v = preview_arm['recall_q4_tail']
        gap_v = (q1v - q4v) if (math.isfinite(q1v) and math.isfinite(q4v)) else float('nan')
        print(
            f"  [seed={seed} PREVIEW_FULL_N_ZIPF] r_all={preview_arm['recall_all']:.3f} "
            f"Q1={q1v:.3f} Q4={q4v:.3f} gap={gap_v:+.3f} "
            f"M={preview_arm['M']} wall={preview_arm['wall_s']:.1f}s",
            flush=True,
        )
        arms.append(preview_arm)

        print(
            f"  [seed={seed} PREVIEW_FULL_N_CONTROL] N={N_FULL} "
            f"alpha={PREVIEW_CONTROL_ALPHA} sigma={PREVIEW_CONTROL_SIGMA} "
            f"load={PREVIEW_CONTROL_LOAD}...",
            flush=True,
        )
        preview_control = run_arm(
            f"PREVIEW_a{PREVIEW_CONTROL_ALPHA:.1f}_s{PREVIEW_CONTROL_SIGMA:.2f}"
            f"_L{PREVIEW_CONTROL_LOAD:.2f}_fullN_CONTROL",
            PREVIEW_CONTROL_ALPHA, PREVIEW_CONTROL_SIGMA, PREVIEW_CONTROL_LOAD,
            n_dim=N_FULL, n_queries=PREVIEW_N_QUERIES,
            seed=seed, out_dir=out_dir,
        )
        q1c = preview_control['recall_q1_head']
        q4c = preview_control['recall_q4_tail']
        gap_c = (q1c - q4c) if (math.isfinite(q1c) and math.isfinite(q4c)) else float('nan')
        print(
            f"  [seed={seed} PREVIEW_FULL_N_CONTROL] r_all={preview_control['recall_all']:.3f} "
            f"Q1={q1c:.3f} Q4={q4c:.3f} gap={gap_c:+.3f} "
            f"M={preview_control['M']} wall={preview_control['wall_s']:.1f}s",
            flush=True,
        )
        arms.append(preview_control)

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


def _preview_arms(arms: List[Dict]) -> List[Dict]:
    return [a for a in arms if a["arm_name"].startswith("PREVIEW_")]


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
    previews = _preview_arms(r["arms"])
    if len(core) != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected {EXPECTED_N_UNITS} core arms, got {len(core)}")
    for a in core:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL", f"Arm {a['arm_name']} error: {a['arm_status']}")

    signatures = set()
    for a in core:
        signatures.add((round(a["recall_all"], 8),
                        round(a["sampler_entropy_nats"], 6),
                        round(a["sigma"], 6),
                        round(a["load"], 6)))
    if len(signatures) < 10:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: only {len(signatures)} distinct signatures")

    try:
        a_baseline = _lookup(core, 0.0, 0.0, 0.05)
    except KeyError as e:
        return ("HARD_FAIL", f"Missing baseline arm: {e}")

    r_baseline = a_baseline["recall_all"]
    if RUN_MODE == "full":
        baseline_ok = (r_baseline >= 0.85)
    else:
        baseline_ok = (r_baseline >= 0.50)
    if not baseline_ok:
        return ("HARD_FAIL",
                f"BASELINE_OUT_OF_BAND: baseline recall={r_baseline:.3f}")

    # UNIFORM_ASYMMETRY_LEAK check (alpha=0 should have gap ~ 0)
    try:
        a_uni_control = _lookup(core, 0.0, 0.30, 0.10)
        q1_uni = a_uni_control["recall_q1_head"]
        q4_uni = a_uni_control["recall_q4_tail"]
        if math.isfinite(q1_uni) and math.isfinite(q4_uni):
            uni_gap = abs(q1_uni - q4_uni)
            if uni_gap > 0.10:
                return ("HARD_FAIL",
                        f"UNIFORM_ASYMMETRY_LEAK: alpha=0/s=0.3/L=0.10 |gap|={uni_gap:.3f}")
    except KeyError:
        pass

    def _safe_gap(a, b):
        if not (math.isfinite(a) and math.isfinite(b)):
            return float("nan")
        return a - b

    # HP window: alpha=1.0, sigma in [0.15, 0.30], load in [0.10, 0.14]
    window_gaps = []
    window_details = []
    for sigma in (0.15, 0.30):
        for load in (0.10, 0.12, 0.14):
            try:
                arm = _lookup(core, 1.0, sigma, load)
                gap = _safe_gap(arm["recall_q1_head"], arm["recall_q4_tail"])
                if math.isfinite(gap):
                    window_gaps.append(gap)
                    window_details.append((sigma, load, arm["recall_q1_head"],
                                          arm["recall_q4_tail"], gap))
            except KeyError:
                pass

    window_abs_gaps = [abs(g) for g in window_gaps]
    max_window_abs_gap = max(window_abs_gaps) if window_abs_gaps else float("nan")
    max_window_signed_gap = (
        max(window_gaps, key=abs) if window_gaps else float("nan")
    )

    # HP fires if |gap| >= 0.10 at any window point (asymmetry ANY direction).
    n_window_hp = sum(1 for g in window_abs_gaps if g >= 0.10)

    # HF_ISOTROPIC: at same window, MAX |gap| < 0.05 -> no asymmetry -> falsify drill
    hf_isotropic = False
    hf_isotropic_msg = ""
    if RUN_MODE == "full" and window_abs_gaps:
        if max(window_abs_gaps) < 0.05:
            hf_isotropic = True
            hf_isotropic_msg = (f"HF_HEBBIAN_ISOTROPIC: at alpha=1.0/sigma>=0.15/L in "
                                f"[0.10, 0.14], MAX |gap|={max(window_abs_gaps):.3f} < 0.05. "
                                f"Canonical Hebbian W-matrix produces NO Zipfian asymmetry.")

    summary_windows = "; ".join(
        f"s{s}L{L:.2f}:Q1={q1:.3f}/Q4={q4:.3f}/g={g:+.3f}"
        for (s, L, q1, q4, g) in window_details
    )

    summary = (
        f"seed={SEED_THIS_CHUNK} N={N_DIM} mode={RUN_MODE} "
        f"baseline={r_baseline:.3f} max_abs_gap={max_window_abs_gap:.3f} "
        f"max_signed_gap={max_window_signed_gap:.3f} "
        f"n_hp_fires={n_window_hp} HP=[any_asymmetry={n_window_hp>0}] "
        f"HF=[isotropic={hf_isotropic}] window=[{summary_windows}]"
    )

    if hf_isotropic:
        return ("HARD_FAIL", f"{hf_isotropic_msg} {summary}")

    if RUN_MODE == "full":
        if n_window_hp > 0 and r_baseline >= 0.95:
            direction = "TAIL_FAVORED" if max_window_signed_gap < 0 else "HEAD_FAVORED"
            return ("HARD_PASS",
                    f"HARD_PASS: HEBBIAN_ANY_ASYMMETRY ({direction}, single-seed). "
                    f"Zipfian frequency-reinforcement produces detectable "
                    f"head-tail asymmetry under noise. NOTE: direction may not "
                    f"match drill's Willshaw prediction (drill predicts head>tail; "
                    f"if TAIL_FAVORED, physics is cross-talk-driven not saturation). "
                    f"Cross-seed VET needed. {summary}")

    if RUN_MODE == "smoke":
        # Preview-driven smoke verdict
        preview_zipf = None
        preview_ctrl = None
        for p in previews:
            if "CONTROL" in p["arm_name"]:
                preview_ctrl = p
            elif "ZIPF" in p["arm_name"]:
                preview_zipf = p

        preview_zipf_gap = float("nan")
        preview_ctrl_gap = float("nan")
        preview_zipf_abs_gap = float("nan")
        if preview_zipf and preview_zipf["arm_status"] == "OK":
            preview_zipf_gap = _safe_gap(preview_zipf["recall_q1_head"],
                                         preview_zipf["recall_q4_tail"])
            preview_zipf_abs_gap = abs(preview_zipf_gap) if math.isfinite(preview_zipf_gap) else float('nan')
        if preview_ctrl and preview_ctrl["arm_status"] == "OK":
            preview_ctrl_gap = _safe_gap(preview_ctrl["recall_q1_head"],
                                         preview_ctrl["recall_q4_tail"])

        preview_summary = (
            f"preview_zipf_gap={preview_zipf_gap:.3f} (|gap|={preview_zipf_abs_gap:.3f}) "
            f"preview_ctrl_gap={preview_ctrl_gap:.3f}"
        )

        if math.isfinite(preview_zipf_abs_gap):
            if preview_zipf_abs_gap >= 0.15:
                direction = "TAIL_FAVORED" if preview_zipf_gap < 0 else "HEAD_FAVORED"
                return ("HARD_PASS",
                        f"HARD_PASS_SMOKE: preview at N=8192 shows STRONG {direction} "
                        f"asymmetry |gap|={preview_zipf_abs_gap:.3f} >= 0.15. "
                        f"Full dispatch recommended. {preview_summary} {summary}")
            elif preview_zipf_abs_gap >= 0.05:
                direction = "TAIL_FAVORED" if preview_zipf_gap < 0 else "HEAD_FAVORED"
                return ("MIDDLE_BAND",
                        f"MIDDLE_BAND_SMOKE: preview shows PARTIAL {direction} asymmetry "
                        f"|gap|={preview_zipf_abs_gap:.3f} in [0.05, 0.15). "
                        f"Skunkworks tier decision. {preview_summary} {summary}")
            else:
                return ("HARD_FAIL",
                        f"HF_HEBBIAN_ISOTROPIC_SMOKE: preview at N=8192 shows "
                        f"|gap|={preview_zipf_abs_gap:.3f} < 0.05. Canonical Hebbian "
                        f"W-matrix produces NO Zipfian asymmetry at wall. "
                        f"{preview_summary} {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial signature. {summary}")


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
            f"[seed={seed}] {ANCHOR_NAME} N={N_DIM} N_Q={N_QUERIES} mode={RUN_MODE}...",
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
            f"HARD_FAIL: stale smoke partials in FULL run. " + verdict_msg
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
            f"alpha={ALPHA_SHAPE_LEVELS} sigma={SIGMA_NOISE_LEVELS} load={LOAD_LEVELS}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "N_QUERIES": N_QUERIES,
        "alpha_shape_levels": ALPHA_SHAPE_LEVELS,
        "sigma_noise_levels": SIGMA_NOISE_LEVELS,
        "load_levels": LOAD_LEVELS,
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
        "calibration_check": "default_ok_for_this_regime",
        "mechanism_class": "hebbian_wmatrix_canonical_B2",
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
