"""Shared core for metric-dependence sweep v2 (Dim S OVERLOAD+NOISE respec).

v1 result: HF_METRICS_IDENTICAL at underloaded dense-Hopfield regime
(all 6 metrics = 1.000 at alpha in [0.10, 8.0]). v1 hand-off note
(notes/exp_dev_findings/exp_metric_dependence_top_k_semantic_v1_HF_METRICS_IDENTICAL_2026-07-01.md)
recommended pushing into overload regime where interference-explosion
should force metric-family differentiation.

QUESTION (v2):
  Does the 6-metric family collapse persist under (a) overload alpha and
  (b) query noise sigma? The canonical prediction is:
    - overload alone: adaptive-beta softmax attention still resolves stored
      patterns; may still saturate.
    - query noise alone at underload: readout degrades but K-neighborhood
      may still contain target -> top-K should exceed top-1.
    - COMBINED overload+noise: interference-explosion + softmax margin
      degradation -> top-1 collapse (fast argmax lottery), top-K survival
      (target in K-neighborhood at moderate rates), cosine broken (readout
      norm degraded).

  This is Sparse Hopfield NeurIPS 2023 territory: dense-bipolar noise impact
  is EXPONENTIAL in load; both axes together push the substrate over the
  wall.

MECHANISM (single arm; sweep = alpha x sigma x seed):
  Substrate build: Cell D v2 dense-Hopfield READ-REPLACE construction
    (bipolar keys/vals -> DG sparse-separate -> cortex-project -> L2-norm ->
     softmax(beta * K @ q) @ V read-out) — SAME as v1.

  Query-noise injection (NEW in v2):
    For each stored key q_i, form noisy query q_i_noisy = q_i + sigma*n
    where n is FHRR-style Gaussian noise, THEN L2-renormalize. sigma is a
    dimensionless multiplier on the pre-projection random component.

  For every noisy query, compute readout p_n once, then evaluate ALL 6
  metrics simultaneously against V_tape.

  Sweep axes:
    alpha in {0.30, 0.50, 1.00, 1.50}  (M/N ratio; from underload edge to
      well over-Amit-Gutfreund wall at 0.14N)
    sigma in {0.0, 0.3, 0.5, 0.7}      (query noise multiplier)
    metric axis: FREE (all 6 measured per landing; no re-run)

PRE-REG (P_deflated = 0.55; HP band; INCREASED FROM v1 0.45 because prior
data from v1 rules out underload; overload+noise is where interference
theory PREDICTS differentiation):
  HP_METRIC_SPREAD_UNDER_STRESS: at (alpha=1.0, sigma=0.5),
    max_metric_recall - top1_recall >= 0.20
    (top-K should survive when top-1 collapses).
  HP_TOP_K_SURVIVES: at (alpha=1.5, sigma=0.7),
    top10_recall >= 0.60 while top1_recall < 0.30.
  HF_UNIFORM_COLLAPSE: at (alpha=1.5, sigma=0.7), all 6 metrics < 0.10
    (substrate is genuinely broken in overload+noise combined regime; no
    metric axis structure to find because everything is at chance).

  CHAIN_GRADE_METRIC_DEPENDENCE_MAPPED if any HP fires cross-seed.

CARDINALITY (META_RULE_H):
  FULL: 4 alphas x 4 sigmas x 1 arm = 16 units per seed. Aggregate 3
        seeds => 48 units.
  SMOKE: subset — 3 alphas {0.30, 1.00, 1.50} x 2 sigmas {0.0, 0.7} = 6
         units, PLUS preview arm at (alpha=1.50, sigma=0.70) full-config
         to confirm interference-regime discriminator fires at scale.
         SMOKE MUST FIRE DISCRIMINATOR: preview must show top1 < 0.90
         (baseline-out-of-saturation) OR HALT_ATOMIZE per META_RULE_AG.

CRLB (per META_RULE_AC / capacity-feasibility):
  top1 argmax-noise floor at N=8192 with M=alpha*N items:
    sigma_min = sqrt(0.25 / M) (binomial-CLT).
  At alpha=1.50, M=12288: sigma_min = sqrt(0.25/12288) = 0.00451.
  HP_METRIC_SPREAD_UNDER_STRESS gap 0.20 = ~44*sigma_min; well-reachable.
  HP_TOP_K_SURVIVES: top1<0.30 with top10>=0.60 = ~66*sigma_min separation;
  well-reachable.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke uses N=8192 (full N) with reduced (alpha x sigma) resolution AND
  explicit preview arm at (alpha=1.50, sigma=0.70) full-config. If preview
  shows top1 >= 0.90 (substrate still saturating even in intended overload),
  discriminator does NOT survive scale — HALT_ATOMIZE + revisit design.

BASELINE-IN-BAND (META_RULE_AG):
  At (alpha=0.30, sigma=0.0) top1 expected near ceiling (v1 verified 1.000
  as underloaded-baseline anchor).
  At (alpha=1.50, sigma=0.70) top1 expected near floor per interference
  theory.
  Sweep bracket includes discriminating band by construction.
  Substrate saturation escape check: v1 already CONFIRMED baseline
  saturation up to alpha=8.0 WITHOUT noise; sigma axis is the escape
  mechanism.

META_RULE_AF (arms-must-differ):
  Only 1 mechanism arm (dense-hopfield read-replace with noisy query).
  (alpha x sigma) grid is a CONFIGURATION sweep, not an arm sweep. Metric
  axis produces 6 distinct numeric outputs per query with different
  denominators; same by-construction exemption as v1.
  arms_differ_exempted for the 6-metric family: 6 metric outputs share
  readout p_n but apply DIFFERENT post-processing (argmax-top-K vs
  cosine-threshold) — structurally distinct functions. Verified in
  selftest.

ASCII-only; META_RULE_AH atomic-write; SystemExit before Exception (no
BaseException).
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
import math
import os
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
# Fixed config
# ---------------------------------------------------------------------------
N_HIPPO_FULL = 4096
N_CORTEX_FULL = 8192      # per pre-reg (same as v1)
HIPPO_SPARSITY = 0.10
ETA_HIPPO_FULL = 1.0
BETA_MIN = 8.0
BETA_MAX = 128.0
N_QUERY = 500            # per pre-reg: query with 500 stored items
N_RAW = 64               # raw key/val dimension before DG projection

# OVERLOAD alpha sweep (v2 respec: pushes past AGS wall 0.14 and beyond)
ALPHA_SWEEP_FULL: Tuple[float, ...] = (0.30, 0.50, 1.00, 1.50)
# NOISE sigma sweep (v2 NEW axis)
SIGMA_SWEEP_FULL: Tuple[float, ...] = (0.0, 0.3, 0.5, 0.7)

# Smoke: reduced grid but must include most-stressful (alpha=1.5, sigma=0.7)
ALPHA_SWEEP_SMOKE: Tuple[float, ...] = (0.30, 1.00, 1.50)
SIGMA_SWEEP_SMOKE: Tuple[float, ...] = (0.0, 0.7)
# Preview at heaviest cell
PREVIEW_ALPHA: float = 1.50
PREVIEW_SIGMA: float = 0.70

# Metric family (SAME 6 as v1)
METRIC_NAMES: Tuple[str, ...] = (
    "top1_recall", "top5_recall", "top10_recall", "top50_recall",
    "cos05_recall", "cos08_recall",
)


# ---------------------------------------------------------------------------
# Instrumentation helpers (identical to v1)
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


def write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    import platform
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


def write_crash_metrics(output_dir, anchor_name, exc):
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
# Substrate primitives (numpy) — IDENTICAL to v1 for mechanism-class parity
# ---------------------------------------------------------------------------
def _pattern_separate_sparse_batched(X: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    """Batched k-WTA sparse-bipolar pattern separator (Cell D v2 primitive)."""
    h_raw = X @ P.T
    abs_h = np.abs(h_raw)
    idx = np.argpartition(-abs_h, k - 1, axis=1)[:, :k]
    signs = np.sign(np.take_along_axis(h_raw, idx, axis=1))
    signs[signs == 0] = 1.0
    out = np.zeros_like(h_raw)
    np.put_along_axis(out, idx, signs, axis=1)
    return out


def _encode_all(keys_raw: np.ndarray, vals_raw: np.ndarray,
                P_in: np.ndarray, P_hc: np.ndarray, k_active: int
                ) -> Tuple[np.ndarray, np.ndarray]:
    """Encode keys/vals through sparse-DG + cortex projection; L2-normalize."""
    keys_h = _pattern_separate_sparse_batched(keys_raw, P_in, k_active)
    vals_h = _pattern_separate_sparse_batched(vals_raw, P_in, k_active)
    keys_c_raw = keys_h @ P_hc.T
    keys_c = keys_c_raw / np.linalg.norm(keys_c_raw, axis=1, keepdims=True).clip(min=1e-12)
    vals_c_raw = vals_h @ P_hc.T
    vals_c = vals_c_raw / np.linalg.norm(vals_c_raw, axis=1, keepdims=True).clip(min=1e-12)
    return keys_c, vals_c


def _cosine_margin_estimate(keys_c: np.ndarray, sample_n: int = 256) -> float:
    m = keys_c.shape[0]
    n_s = min(sample_n, m)
    idx = np.arange(m)
    if m > n_s:
        rng = np.random.RandomState(0)
        idx = rng.choice(m, size=n_s, replace=False)
    sub = keys_c[idx]
    sim = sub @ sub.T
    mask = ~np.eye(n_s, dtype=bool)
    off_mean_abs = float(np.abs(sim[mask]).mean())
    margin = 1.0 - off_mean_abs
    if not math.isfinite(margin) or margin <= 0.0:
        return 0.1
    return margin


def _compute_adaptive_beta(m_items: int, cosine_margin: float) -> float:
    raw = math.log2(max(2, m_items)) / max(cosine_margin, 0.05)
    return float(max(BETA_MIN, min(BETA_MAX, raw)))


def _compute_all_metrics(p_n: np.ndarray, V_tape: np.ndarray,
                         target_idx: np.ndarray) -> Dict[str, float]:
    """Given readout matrix p_n [Q,d] and V_tape [M,d] and target indices [Q],
    compute all 6 metrics simultaneously. IDENTICAL to v1."""
    sims = p_n @ V_tape.T                  # [Q, M]
    Q, M = sims.shape

    top_ks = (1, 5, 10, 50)
    top_k_hits: Dict[int, float] = {}
    for K in top_ks:
        K_eff = min(K, M)
        if K_eff == 1:
            argmax_top = sims.argmax(axis=1)
            hits = int((argmax_top == target_idx).sum())
        else:
            top_idx = np.argpartition(-sims, K_eff - 1, axis=1)[:, :K_eff]
            hits = int((top_idx == target_idx[:, None]).any(axis=1).sum())
        top_k_hits[K] = hits / float(Q)

    target_sims = sims[np.arange(Q), target_idx]
    cos05_hits = int((target_sims >= 0.5).sum()) / float(Q)
    cos08_hits = int((target_sims >= 0.8).sum()) / float(Q)

    return {
        "top1_recall":  top_k_hits[1],
        "top5_recall":  top_k_hits[5],
        "top10_recall": top_k_hits[10],
        "top50_recall": top_k_hits[50],
        "cos05_recall": cos05_hits,
        "cos08_recall": cos08_hits,
    }


# ---------------------------------------------------------------------------
# Per-(alpha, sigma) cell runner
# ---------------------------------------------------------------------------
def run_one_cell(seed: int, alpha_load: float, sigma_noise: float,
                 n_h: int, n_c: int, hippo_sparsity: float,
                 n_query: int, out_dir: Path, unit_idx: int) -> Dict:
    """Build substrate at (n_c, M=alpha*n_c), inject noise sigma_noise into
    query, evaluate all 6 metrics.

    NEW in v2: noisy_query = L2normalize(keys_c[i] + sigma*randn(d)).
    This is the escape mechanism from v1 substrate-saturation.
    """
    t0 = time.time()
    m_items = max(1, int(round(alpha_load * n_c)))
    n_q_eff = min(n_query, m_items)
    k_active = max(1, int(round(hippo_sparsity * n_h)))

    try:
        # Unique RNG state per (seed, alpha, sigma)
        seed_key = (seed * 10007
                    + int(round(alpha_load * 10000))
                    + int(round(sigma_noise * 100000)) * 31)
        rng = np.random.RandomState(seed_key)
        P_in = rng.randn(n_h, N_RAW).astype(np.float64) / np.sqrt(N_RAW)
        P_hc = rng.randn(n_c, n_h).astype(np.float64) / np.sqrt(n_h)
        keys_raw = rng.choice([-1.0, 1.0], size=(m_items, N_RAW)).astype(np.float64)
        vals_raw = rng.choice([-1.0, 1.0], size=(m_items, N_RAW)).astype(np.float64)

        keys_c, vals_c = _encode_all(keys_raw, vals_raw, P_in, P_hc, k_active)
        emit_heartbeat(out_dir, unit_idx=unit_idx, elapsed_s=time.time() - t0,
                       extra={"phase": "encoded", "alpha": alpha_load,
                              "sigma": sigma_noise, "M": m_items, "N_c": n_c})

        cosine_margin = _cosine_margin_estimate(keys_c)
        beta = _compute_adaptive_beta(m_items, cosine_margin)

        q_idx = np.arange(n_q_eff)
        target_idx = q_idx.astype(np.int64)

        # NEW in v2: query noise injection
        clean_queries = keys_c[q_idx]  # [Q, N_c]
        if sigma_noise > 0.0:
            noise = rng.randn(n_q_eff, n_c).astype(np.float64)
            noisy_queries_raw = clean_queries + sigma_noise * noise
            queries = noisy_queries_raw / np.linalg.norm(
                noisy_queries_raw, axis=1, keepdims=True).clip(min=1e-12)
        else:
            queries = clean_queries

        # Softmax attention readout
        sims_qk = beta * (queries @ keys_c.T)
        sims_qk -= sims_qk.max(axis=1, keepdims=True)
        w = np.exp(sims_qk)
        w /= w.sum(axis=1, keepdims=True).clip(min=1e-30)
        p = w @ vals_c
        p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)

        emit_heartbeat(out_dir, unit_idx=unit_idx + 1, elapsed_s=time.time() - t0,
                       extra={"phase": "readout_done", "alpha": alpha_load,
                              "sigma": sigma_noise, "M": m_items, "beta": beta,
                              "cosine_margin": cosine_margin})

        metrics_dict = _compute_all_metrics(p_n, vals_c, target_idx)

        wall = time.time() - t0
        return {
            "alpha_load": float(alpha_load),
            "sigma_noise": float(sigma_noise),
            "M": int(m_items),
            "N_c": int(n_c),
            "N_h": int(n_h),
            "n_query_eff": int(n_q_eff),
            "beta_used": float(beta),
            "cosine_margin_used": float(cosine_margin),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": "OK",
            "metrics": metrics_dict,
        }
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "alpha_load": float(alpha_load),
            "sigma_noise": float(sigma_noise),
            "M": int(m_items),
            "N_c": int(n_c),
            "N_h": int(n_h),
            "n_query_eff": int(n_q_eff),
            "beta_used": float("nan"),
            "cosine_margin_used": float("nan"),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
            "metrics": {name: float("nan") for name in METRIC_NAMES},
        }


# ---------------------------------------------------------------------------
# Self-tests (META_RULE_AC number provenance + formula verification)
# ---------------------------------------------------------------------------
def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_h_t = 512
    N_raw_t = 32
    k_t = max(1, int(round(HIPPO_SPARSITY * N_h_t)))
    P = rng.randn(N_h_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    x = rng.choice([-1.0, 1.0], size=N_raw_t).astype(np.float64)
    x_batch = x[np.newaxis, :]
    h = _pattern_separate_sparse_batched(x_batch, P, k_t)[0]
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != k_t:
        raise AssertionError(f"k-WTA sparsity wrong: got {n_active} != {k_t}")


def _selftest_dense_hopfield_perfect_recall() -> None:
    rng = np.random.RandomState(11)
    M_t, N_t = 8, 32
    V = rng.randn(M_t, N_t).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    q = V[3].copy()
    sims = 50.0 * (V @ q)
    sims -= sims.max()
    w = np.exp(sims)
    w /= w.sum()
    p = V.T @ w
    err = float(np.linalg.norm(p - V[3]))
    if err > 0.1:
        raise AssertionError(f"DENSE_HOPFIELD_SELFTEST FAIL: err={err}")


def _selftest_all_metrics_ordering() -> None:
    rng = np.random.RandomState(19)
    Q, M, d = 64, 128, 32
    V = rng.randn(M, d).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    target_idx = rng.choice(M, size=Q, replace=True).astype(np.int64)
    p_n = V[target_idx] + 0.3 * rng.randn(Q, d)
    p_n = p_n / np.linalg.norm(p_n, axis=1, keepdims=True).clip(min=1e-12)
    metrics = _compute_all_metrics(p_n, V, target_idx)
    if not (metrics["top1_recall"] <= metrics["top5_recall"] + 1e-9):
        raise AssertionError(f"top1={metrics['top1_recall']} > top5={metrics['top5_recall']}")
    if not (metrics["top5_recall"] <= metrics["top10_recall"] + 1e-9):
        raise AssertionError(f"top5={metrics['top5_recall']} > top10={metrics['top10_recall']}")
    if not (metrics["top10_recall"] <= metrics["top50_recall"] + 1e-9):
        raise AssertionError(f"top10={metrics['top10_recall']} > top50={metrics['top50_recall']}")
    if not (metrics["cos08_recall"] <= metrics["cos05_recall"] + 1e-9):
        raise AssertionError(f"cos08={metrics['cos08_recall']} > cos05={metrics['cos05_recall']}")


def _selftest_perfect_readout_all_top_k_1() -> None:
    rng = np.random.RandomState(23)
    Q, M, d = 32, 64, 16
    V = rng.randn(M, d).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    target_idx = np.arange(Q).astype(np.int64)
    p_n = V[target_idx].copy()
    metrics = _compute_all_metrics(p_n, V, target_idx)
    for name in ("top1_recall", "top5_recall", "top10_recall", "top50_recall",
                 "cos05_recall", "cos08_recall"):
        if metrics[name] < 0.999:
            raise AssertionError(f"perfect readout {name}={metrics[name]} < 1.0")


def _selftest_zero_readout_top1_at_chance() -> None:
    rng = np.random.RandomState(29)
    Q, M, d = 100, 200, 32
    V = rng.randn(M, d).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    target_idx = rng.choice(M, size=Q).astype(np.int64)
    p_n = rng.randn(Q, d).astype(np.float64)
    p_n = p_n / np.linalg.norm(p_n, axis=1, keepdims=True).clip(min=1e-12)
    metrics = _compute_all_metrics(p_n, V, target_idx)
    if metrics["top1_recall"] > 0.10:
        raise AssertionError(f"random readout top1={metrics['top1_recall']} suspiciously high")
    if metrics["cos05_recall"] > 0.10:
        raise AssertionError(f"random readout cos>=0.5={metrics['cos05_recall']} suspiciously high")


def _selftest_sweep_cardinality() -> None:
    if len(ALPHA_SWEEP_FULL) != 4:
        raise AssertionError(f"ALPHA_SWEEP_FULL must have 4 values; got {ALPHA_SWEEP_FULL}")
    if set(ALPHA_SWEEP_FULL) != {0.30, 0.50, 1.00, 1.50}:
        raise AssertionError(f"ALPHA_SWEEP_FULL values wrong: {ALPHA_SWEEP_FULL}")
    if len(SIGMA_SWEEP_FULL) != 4:
        raise AssertionError(f"SIGMA_SWEEP_FULL must have 4 values; got {SIGMA_SWEEP_FULL}")
    if set(SIGMA_SWEEP_FULL) != {0.0, 0.3, 0.5, 0.7}:
        raise AssertionError(f"SIGMA_SWEEP_FULL values wrong: {SIGMA_SWEEP_FULL}")


def _selftest_metrics_family_arms_differ() -> None:
    rng = np.random.RandomState(31)
    Q, M, d = 128, 256, 64
    V = rng.randn(M, d).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    target_idx = np.arange(Q).astype(np.int64)
    p_n = V[target_idx] + 0.5 * rng.randn(Q, d)
    p_n = p_n / np.linalg.norm(p_n, axis=1, keepdims=True).clip(min=1e-12)
    metrics = _compute_all_metrics(p_n, V, target_idx)
    vals = list(metrics.values())
    spread = max(vals) - min(vals)
    if spread < 0.01:
        raise AssertionError(
            f"metrics-family collapsed at moderate noise: spread={spread} vals={metrics}"
        )


def _selftest_adaptive_beta_computes_finite() -> None:
    for m_test in (800, 2400, 4096, 8192, 12288):
        b = _compute_adaptive_beta(m_test, 0.7)
        if not math.isfinite(b):
            raise AssertionError(f"beta not finite at M={m_test}: {b}")
        if not (BETA_MIN <= b <= BETA_MAX):
            raise AssertionError(f"beta {b} not in [{BETA_MIN},{BETA_MAX}] at M={m_test}")


def _selftest_noise_injection_moves_metrics() -> None:
    """v2 NEW: adding query noise to a known-clean substrate MUST measurably
    degrade top1_recall (at moderate substrate size where perfect recall is
    the baseline). This verifies the noise-injection mechanism actually
    changes the physics.
    """
    rng = np.random.RandomState(41)
    M_t, d = 100, 128
    # Small under-loaded substrate at d/M = 1.28 (well below saturation)
    keys = rng.randn(M_t, d).astype(np.float64)
    keys = keys / np.linalg.norm(keys, axis=1, keepdims=True).clip(min=1e-12)
    vals = rng.randn(M_t, d).astype(np.float64)
    vals = vals / np.linalg.norm(vals, axis=1, keepdims=True).clip(min=1e-12)
    Q = 50
    q_idx = np.arange(Q)
    target = q_idx.astype(np.int64)
    beta = 30.0

    # Clean readout (sigma=0)
    q_clean = keys[q_idx]
    sims_c = beta * (q_clean @ keys.T); sims_c -= sims_c.max(axis=1, keepdims=True)
    w_c = np.exp(sims_c); w_c /= w_c.sum(axis=1, keepdims=True).clip(min=1e-30)
    p_c = w_c @ vals
    p_c = p_c / np.linalg.norm(p_c, axis=1, keepdims=True).clip(min=1e-12)
    m_clean = _compute_all_metrics(p_c, vals, target)

    # Noisy readout (sigma=1.5 — heavy noise so degradation is guaranteed)
    noise = rng.randn(Q, d).astype(np.float64)
    q_noisy_raw = q_clean + 1.5 * noise
    q_noisy = q_noisy_raw / np.linalg.norm(q_noisy_raw, axis=1, keepdims=True).clip(min=1e-12)
    sims_n = beta * (q_noisy @ keys.T); sims_n -= sims_n.max(axis=1, keepdims=True)
    w_n = np.exp(sims_n); w_n /= w_n.sum(axis=1, keepdims=True).clip(min=1e-30)
    p_n = w_n @ vals
    p_n = p_n / np.linalg.norm(p_n, axis=1, keepdims=True).clip(min=1e-12)
    m_noisy = _compute_all_metrics(p_n, vals, target)

    # Clean should be near-perfect; noisy top1 should degrade materially
    if m_clean["top1_recall"] < 0.95:
        raise AssertionError(f"noise-injection selftest: clean top1={m_clean['top1_recall']} < 0.95 (substrate misconfigured)")
    degradation = m_clean["top1_recall"] - m_noisy["top1_recall"]
    if degradation < 0.10:
        raise AssertionError(
            f"noise-injection selftest: sigma=1.5 top1 degraded only {degradation:.3f} "
            f"(clean={m_clean['top1_recall']:.3f} noisy={m_noisy['top1_recall']:.3f}); "
            f"noise mechanism has no measurable effect on physics"
        )


def run_all_selftests(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        _selftest_sparse_pattern_separator()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_all_metrics_ordering()
        _selftest_perfect_readout_all_top_k_1()
        _selftest_zero_readout_top1_at_chance()
        _selftest_sweep_cardinality()
        _selftest_metrics_family_arms_differ()
        _selftest_adaptive_beta_computes_finite()
        _selftest_noise_injection_moves_metrics()
        if f"seed_{seed_this_chunk}" not in anchor_name:
            raise AssertionError(
                f"anchor '{anchor_name}' missing seed_{seed_this_chunk}"
            )
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _cell_key(alpha: float, sigma: float) -> str:
    """Stable key for per-cell dict."""
    return f"a{int(round(alpha * 10000))}_s{int(round(sigma * 100000))}"


def compute_verdict(per_seed_result: Dict, run_mode: str
                    ) -> Tuple[str, str, Dict]:
    """Aggregate per-cell (alpha x sigma) metrics into HP/HF/MB verdict."""
    per_cell = per_seed_result.get("per_cell", {})
    if run_mode == "full":
        alpha_sweep = ALPHA_SWEEP_FULL
        sigma_sweep = SIGMA_SWEEP_FULL
    else:
        alpha_sweep = ALPHA_SWEEP_SMOKE
        sigma_sweep = SIGMA_SWEEP_SMOKE
    expected_n = len(alpha_sweep) * len(sigma_sweep)

    if len(per_cell) != expected_n:
        return ("HARD_FAIL",
                f"CELL_CARDINALITY_BREACH: expected {expected_n} cells, "
                f"got {len(per_cell)}: {sorted(per_cell.keys())}",
                {})

    def m(alpha: float, sigma: float, name: str) -> float:
        key = _cell_key(alpha, sigma)
        row = per_cell.get(key)
        if row is None:
            return float("nan")
        return float(row.get("metrics", {}).get(name, float("nan")))

    # Build headline
    headline: Dict = {"cells": {}}
    for alpha in alpha_sweep:
        for sigma in sigma_sweep:
            key = _cell_key(alpha, sigma)
            row = per_cell.get(key)
            if row is None:
                continue
            headline["cells"][key] = {
                "alpha": alpha,
                "sigma": sigma,
                "M": row.get("M"),
                "beta": row.get("beta_used"),
                "metrics": row.get("metrics", {}),
            }

    reasons = []
    hp_flags = {}

    # HP_METRIC_SPREAD_UNDER_STRESS: at (alpha=1.0, sigma=0.5),
    # max_metric_recall - top1_recall >= 0.20
    stress_alpha, stress_sigma = 1.0, 0.5
    # Smoke may not include sigma=0.5; use sigma=0.7 as smoke fallback if needed
    if stress_sigma not in sigma_sweep:
        stress_sigma = 0.7 if 0.7 in sigma_sweep else sigma_sweep[-1]
    if stress_alpha in alpha_sweep:
        row = per_cell.get(_cell_key(stress_alpha, stress_sigma))
        if row is not None:
            mets = row.get("metrics", {})
            top1 = float(mets.get("top1_recall", float("nan")))
            max_other = max(
                float(mets.get("top5_recall", float("nan"))),
                float(mets.get("top10_recall", float("nan"))),
                float(mets.get("top50_recall", float("nan"))),
                float(mets.get("cos05_recall", float("nan"))),
                float(mets.get("cos08_recall", float("nan"))),
            )
            if math.isfinite(top1) and math.isfinite(max_other):
                gap = max_other - top1
                hp_flags["HP_METRIC_SPREAD_UNDER_STRESS"] = (gap >= 0.20)
                reasons.append(
                    f"spread@(a={stress_alpha},s={stress_sigma})={gap:+.3f}(HP>=0.20)"
                )

    # HP_TOP_K_SURVIVES: at (alpha=1.5, sigma=0.7),
    # top10_recall >= 0.60 AND top1_recall < 0.30
    if 1.5 in alpha_sweep and 0.7 in sigma_sweep:
        top1_hard = m(1.5, 0.7, "top1_recall")
        top10_hard = m(1.5, 0.7, "top10_recall")
        if math.isfinite(top1_hard) and math.isfinite(top10_hard):
            fired = (top10_hard >= 0.60 and top1_hard < 0.30)
            hp_flags["HP_TOP_K_SURVIVES"] = fired
            reasons.append(
                f"top1@(1.5,0.7)={top1_hard:.3f} top10@(1.5,0.7)={top10_hard:.3f}"
                f"(HP: top10>=0.60 & top1<0.30)"
            )

    # HF_UNIFORM_COLLAPSE: at (alpha=1.5, sigma=0.7), all 6 metrics < 0.10
    hf_uniform_collapse = False
    if 1.5 in alpha_sweep and 0.7 in sigma_sweep:
        row = per_cell.get(_cell_key(1.5, 0.7))
        if row is not None:
            mets = row.get("metrics", {})
            vals = [float(mets.get(n, float("nan"))) for n in METRIC_NAMES]
            if all(math.isfinite(v) for v in vals):
                hf_uniform_collapse = all(v < 0.10 for v in vals)
                reasons.append(
                    f"uniform-collapse@(1.5,0.7)=[max={max(vals):.3f}](HF<0.10)"
                )

    # Diagnostic: max spread over all cells
    max_spread_all = 0.0
    for row in per_cell.values():
        mvals = list(row.get("metrics", {}).values())
        mvals = [v for v in mvals if isinstance(v, (int, float)) and math.isfinite(v)]
        if mvals:
            spread = max(mvals) - min(mvals)
            max_spread_all = max(max_spread_all, spread)
    reasons.append(f"max_spread_all_cells={max_spread_all:.3f}")

    headline["hp_flags"] = hp_flags
    headline["max_spread_all_cells"] = float(max_spread_all)
    headline["hf_uniform_collapse"] = bool(hf_uniform_collapse)

    # Decision
    if hf_uniform_collapse:
        verdict = "HARD_FAIL"
        msg = "HF_UNIFORM_COLLAPSE: all 6 metrics <0.10 at (a=1.5,s=0.7); " + " ".join(reasons)
    else:
        any_hp = any(hp_flags.values())
        if any_hp:
            passed = [k for k, v in hp_flags.items() if v]
            verdict = "HARD_PASS"
            msg = f"HP fires: {passed} | " + " ".join(reasons)
        else:
            verdict = "MIDDLE_BAND"
            msg = "no HP gate fires; overload+noise sweep completed; " + " ".join(reasons)

    return (verdict, msg, headline)
