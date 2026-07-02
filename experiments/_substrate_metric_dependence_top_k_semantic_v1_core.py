"""Shared core for metric-dependence sweep v1 (Dim S from hidden-dim research 2026-07-01).

QUESTION:
  Prior substrate chain-grade evidence uses top-1 recall exclusively. Real M3
  workloads use top-K, semantic-similarity (cosine>=tau), or downstream-task
  quality. Same substrate may have MUCH higher effective capacity when measured
  by top-5 / top-10 / cosine>=0.5 than by exact top-1.

  This cell varies the RETRIEVAL METRIC axis directly at a load sweep to map
  metric-vs-capacity phase boundaries.

MECHANISM (single arm; sweep = load x metric x seed):
  Substrate build: Cell D v2 dense-Hopfield READ-REPLACE construction
    (bipolar keys/vals -> DG sparse-separate -> cortex-project -> L2-norm ->
     softmax(beta * K @ q) @ V read-out).
  For every stored query key, compute readout vector p_n once, then evaluate
  ALL 6 metrics simultaneously against V_tape:
    - top1_recall:  argmax(p_n @ V^T) == target
    - top5_recall:  target in top-5 argmax
    - top10_recall: target in top-10 argmax
    - top50_recall: target in top-50 argmax
    - cos05_recall: sim(p_n, V[target]) >= 0.5
    - cos08_recall: sim(p_n, V[target]) >= 0.8

  Sweep axes:
    load in {0.10, 0.15, 0.20, 0.25, 0.30}  (M/N ratio)
    metric axis is FREE (all 6 measured per landing; no re-run)

PRE-REG (P_deflated = 0.45; HP band):
  HP_TOP1_WALL:      at alpha=0.15, top1 recall >= 0.80 (reproduces prior CG).
  HP_TOPK_HIGHER:    top10 recall >= top1 + 0.15 at alpha=0.20.
  HP_SEMANTIC_HIGHER: cos05 recall >= top1 + 0.20 at alpha=0.20.
  HF_METRICS_IDENTICAL: max spread across 6 metrics at any load < 0.05.
  HF_TOPK_CATASTROPHIC: at alpha=0.30, top1 < 0.30 AND top50 < 0.60.

  CHAIN_GRADE_METRIC_DEPENDENCE_MAPPED if any HP fires cross-seed.

CARDINALITY (META_RULE_H):
  FULL: 5 loads x 1 arm = 5 units per seed (metric axis IS the free measurement
        surface; not a separate compute unit). Aggregate 3 seeds => 15 units.
  SMOKE: 3 loads (0.10, 0.20, 0.30) + 1 FULL_N preview at heaviest load.

CRLB (per META_RULE_AC / capacity-feasibility):
  top1 argmax-noise floor at N=8192 with M=alpha*N items:
    sigma_min = sqrt(0.25 / M) (binomial-CLT).
  At alpha=0.30, M=2458: sigma_min = 0.0101.
  HP_TOPK_HIGHER gap 0.15 = ~15*sigma; well-reachable.
  HP_SEMANTIC_HIGHER gap 0.20 = ~20*sigma; well-reachable.
  top1 ceiling per Principle S argmax-noise: bounded by V/V_per_cat gap;
  at alpha=0.30 (M=2458 << N=8192) argmax-noise floor still admits top1 recall
  in [0.0, 1.0] range; discriminator reachable.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke uses N=8192 (full N) with reduced M-loads (0.10, 0.20, 0.30 only,
  not the full 5-point sweep). Scale is preserved; sweep resolution reduced.
  Preview arm at alpha=0.30 full-N confirms discriminator fires.

BASELINE-IN-BAND (META_RULE_AG):
  At alpha=0.10 (M=819) top1 expected near ceiling (baseline high); at
  alpha=0.30 (M=2458) top1 expected near floor. Sweep bracket includes
  discriminating band.

META_RULE_AF (arms-must-differ):
  Only 1 arm (dense-hopfield read-replace). Metric axis produces 6 DISTINCT
  numeric outputs per query with different denominators; not the same as arm
  identity. arms_differ_exempted for the 6-metric family by construction:
  the 6 metric outputs share the readout tensor p_n but apply DIFFERENT
  post-processing (argmax-top-K vs cosine-threshold) which are structurally
  distinct functions. Verified in selftest below.

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
N_CORTEX_FULL = 8192      # per pre-reg
HIPPO_SPARSITY = 0.10
ETA_HIPPO_FULL = 1.0
BETA_MIN = 8.0
BETA_MAX = 128.0
N_QUERY = 500            # per pre-reg: query with 500 stored items
N_RAW = 64               # raw key/val dimension before DG projection

# Load sweep (M/N ratio at N_CORTEX_FULL=8192)
LOAD_SWEEP_FULL: Tuple[float, ...] = (0.10, 0.15, 0.20, 0.25, 0.30)
LOAD_SWEEP_SMOKE: Tuple[float, ...] = (0.10, 0.20, 0.30)  # bracket only
LOAD_SWEEP_PREVIEW_ALPHA: float = 0.30                    # heaviest for preview

# Metric family
METRIC_NAMES: Tuple[str, ...] = (
    "top1_recall", "top5_recall", "top10_recall", "top50_recall",
    "cos05_recall", "cos08_recall",
)


# ---------------------------------------------------------------------------
# Instrumentation helpers (inline; per META_RULE_13 defensive-error-checking)
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
# Substrate primitives (numpy)
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
    compute all 6 metrics simultaneously.

    top-K:   argpartition top-K of sims; target in top-K set.
    cos>=tau: sim(p_n, V[target]) >= tau (direct threshold, not competitive).

    Returns dict of metric_name -> recall (fraction of Q queries hitting).
    """
    sims = p_n @ V_tape.T                  # [Q, M]
    Q, M = sims.shape

    # top-K family (K in {1, 5, 10, 50})
    top_ks = (1, 5, 10, 50)
    top_k_hits: Dict[int, float] = {}
    for K in top_ks:
        K_eff = min(K, M)
        if K_eff == 1:
            argmax_top = sims.argmax(axis=1)  # [Q]
            hits = int((argmax_top == target_idx).sum())
        else:
            # argpartition to get top-K unordered indices per row
            top_idx = np.argpartition(-sims, K_eff - 1, axis=1)[:, :K_eff]  # [Q, K]
            # target in top-K set
            hits = int((top_idx == target_idx[:, None]).any(axis=1).sum())
        top_k_hits[K] = hits / float(Q)

    # Cosine-threshold family: sim(p_n[i], V_tape[target[i]])
    target_sims = sims[np.arange(Q), target_idx]  # [Q]
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
# Per-load runner: dense-Hopfield READ-REPLACE + 6-metric readout
# ---------------------------------------------------------------------------
def run_one_load(seed: int, alpha_load: float,
                 n_h: int, n_c: int, hippo_sparsity: float,
                 n_query: int, out_dir: Path, unit_idx: int) -> Dict:
    """Build substrate at (n_c, M=alpha*n_c), then evaluate all 6 metrics on
    N_QUERY stored items (per pre-reg query-with-500-stored-items).
    """
    t0 = time.time()
    m_items = max(1, int(round(alpha_load * n_c)))
    n_q_eff = min(n_query, m_items)  # cannot query more than stored
    k_active = max(1, int(round(hippo_sparsity * n_h)))

    try:
        rng = np.random.RandomState(seed * 10007 + int(round(alpha_load * 10000)))
        P_in = rng.randn(n_h, N_RAW).astype(np.float64) / np.sqrt(N_RAW)
        P_hc = rng.randn(n_c, n_h).astype(np.float64) / np.sqrt(n_h)
        keys_raw = rng.choice([-1.0, 1.0], size=(m_items, N_RAW)).astype(np.float64)
        vals_raw = rng.choice([-1.0, 1.0], size=(m_items, N_RAW)).astype(np.float64)

        keys_c, vals_c = _encode_all(keys_raw, vals_raw, P_in, P_hc, k_active)
        emit_heartbeat(out_dir, unit_idx=unit_idx, elapsed_s=time.time() - t0,
                       extra={"phase": "encoded", "alpha": alpha_load,
                              "M": m_items, "N_c": n_c})

        # Adaptive beta from margin (same formula as Cell D v2)
        cosine_margin = _cosine_margin_estimate(keys_c)
        beta = _compute_adaptive_beta(m_items, cosine_margin)

        # Select N_QUERY stored items to query (first n_q_eff)
        q_idx = np.arange(n_q_eff)
        queries = keys_c[q_idx]                              # [Q, N_c]
        target_idx = q_idx.astype(np.int64)

        # Softmax attention readout: p = softmax(beta * q @ K^T) @ V
        sims_qk = beta * (queries @ keys_c.T)               # [Q, M]
        sims_qk -= sims_qk.max(axis=1, keepdims=True)
        w = np.exp(sims_qk)
        w /= w.sum(axis=1, keepdims=True).clip(min=1e-30)
        p = w @ vals_c                                       # [Q, N_c]
        p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)

        emit_heartbeat(out_dir, unit_idx=unit_idx + 1, elapsed_s=time.time() - t0,
                       extra={"phase": "readout_done", "alpha": alpha_load,
                              "M": m_items, "beta": beta,
                              "cosine_margin": cosine_margin})

        # Compute all 6 metrics from same readout
        metrics_dict = _compute_all_metrics(p_n, vals_c, target_idx)

        wall = time.time() - t0
        return {
            "alpha_load": float(alpha_load),
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
    """top1 <= top5 <= top10 <= top50 by monotonicity of top-K.
    cos>=0.8 <= cos>=0.5 by monotonicity of threshold.
    ORDER-INVARIANT properties MUST hold for the metric formulas to be
    correctly implemented.
    """
    rng = np.random.RandomState(19)
    Q, M, d = 64, 128, 32
    V = rng.randn(M, d).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    # p_n = noisy V (each target with noise)
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
    """When readout equals target exactly, all top-K metrics should be 1.0
    and cos>=0.5 / cos>=0.8 should be 1.0."""
    rng = np.random.RandomState(23)
    Q, M, d = 32, 64, 16
    V = rng.randn(M, d).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    target_idx = np.arange(Q).astype(np.int64)
    p_n = V[target_idx].copy()  # perfect readout
    metrics = _compute_all_metrics(p_n, V, target_idx)
    for name in ("top1_recall", "top5_recall", "top10_recall", "top50_recall",
                 "cos05_recall", "cos08_recall"):
        if metrics[name] < 0.999:
            raise AssertionError(f"perfect readout {name}={metrics[name]} < 1.0")


def _selftest_zero_readout_top1_at_chance() -> None:
    """When readout is uncorrelated with target, top1 should be near
    1/M (chance) but cos>=0.5 should be near 0 (random cosine noise is small).
    We only check argmax != target for >50% of queries."""
    rng = np.random.RandomState(29)
    Q, M, d = 100, 200, 32
    V = rng.randn(M, d).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    target_idx = rng.choice(M, size=Q).astype(np.int64)
    p_n = rng.randn(Q, d).astype(np.float64)
    p_n = p_n / np.linalg.norm(p_n, axis=1, keepdims=True).clip(min=1e-12)
    metrics = _compute_all_metrics(p_n, V, target_idx)
    # top1 should be ~ 1/M = 0.005; very unlikely to be > 0.1
    if metrics["top1_recall"] > 0.10:
        raise AssertionError(f"random readout top1={metrics['top1_recall']} suspiciously high")
    # cos>=0.5 should be very rare with random unit vectors in d=32
    if metrics["cos05_recall"] > 0.10:
        raise AssertionError(f"random readout cos>=0.5={metrics['cos05_recall']} suspiciously high")


def _selftest_load_sweep_cardinality() -> None:
    if len(LOAD_SWEEP_FULL) != 5:
        raise AssertionError(f"LOAD_SWEEP_FULL must have 5 values; got {LOAD_SWEEP_FULL}")
    if set(LOAD_SWEEP_FULL) != {0.10, 0.15, 0.20, 0.25, 0.30}:
        raise AssertionError(f"LOAD_SWEEP_FULL values wrong: {LOAD_SWEEP_FULL}")


def _selftest_metrics_family_arms_differ() -> None:
    """META_RULE_AF-adjacent: the 6 metrics from a REALISTIC readout must not
    all coincide (else metric axis is meaningless). Use a moderately-degraded
    readout so top1 differs from top50 and cos>=0.5 differs from cos>=0.8."""
    rng = np.random.RandomState(31)
    Q, M, d = 128, 256, 64
    V = rng.randn(M, d).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    target_idx = np.arange(Q).astype(np.int64)
    # Moderate noise: recall should be intermediate for top1 vs top50 to differ
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
    for m_test in (800, 1200, 1600, 2000, 2400):
        b = _compute_adaptive_beta(m_test, 0.7)
        if not math.isfinite(b):
            raise AssertionError(f"beta not finite at M={m_test}: {b}")
        if not (BETA_MIN <= b <= BETA_MAX):
            raise AssertionError(f"beta {b} not in [{BETA_MIN},{BETA_MAX}] at M={m_test}")


def run_all_selftests(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        _selftest_sparse_pattern_separator()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_all_metrics_ordering()
        _selftest_perfect_readout_all_top_k_1()
        _selftest_zero_readout_top1_at_chance()
        _selftest_load_sweep_cardinality()
        _selftest_metrics_family_arms_differ()
        _selftest_adaptive_beta_computes_finite()
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
def compute_verdict(per_seed_result: Dict, run_mode: str
                    ) -> Tuple[str, str, Dict]:
    """Aggregate per-load metrics into HP/HF/MB verdict."""
    per_load = per_seed_result.get("per_load", {})
    load_sweep = LOAD_SWEEP_FULL if run_mode == "full" else LOAD_SWEEP_SMOKE
    expected_n_loads = len(load_sweep)
    if len(per_load) != expected_n_loads:
        return ("HARD_FAIL",
                f"LOAD_CARDINALITY_BREACH: expected {expected_n_loads} loads, "
                f"got {len(per_load)}: {sorted(per_load.keys())}",
                {})

    # Extract metrics per load
    def m(alpha: float, name: str) -> float:
        # per_load keys are int(round(alpha*10000)); return NaN if missing
        key = int(round(alpha * 10000))
        row = per_load.get(key) or per_load.get(str(key))
        if row is None:
            return float("nan")
        return float(row.get("metrics", {}).get(name, float("nan")))

    # Diagnostic headline
    headline: Dict = {}
    for alpha in load_sweep:
        key = int(round(alpha * 10000))
        row = per_load.get(key) or per_load.get(str(key))
        if row is None:
            continue
        headline[f"alpha_{alpha:.2f}"] = {
            "M": row.get("M"),
            "beta": row.get("beta_used"),
            "metrics": row.get("metrics", {}),
        }

    # Verdict gates
    verdict = "MIDDLE_BAND"
    reasons = []
    hp_flags = {}

    # HP_TOP1_WALL: at alpha=0.15, top1 >= 0.80 (FULL only; smoke uses 0.10,0.20,0.30)
    top1_at_015 = m(0.15, "top1_recall")
    if run_mode == "full" and math.isfinite(top1_at_015):
        hp_flags["HP_TOP1_WALL"] = (top1_at_015 >= 0.80)
        reasons.append(f"top1@0.15={top1_at_015:.3f}(HP>=0.80)")

    # HP_TOPK_HIGHER: top10 recall >= top1 + 0.15 at alpha=0.20
    top1_at_020 = m(0.20, "top1_recall")
    top10_at_020 = m(0.20, "top10_recall")
    if math.isfinite(top1_at_020) and math.isfinite(top10_at_020):
        gap = top10_at_020 - top1_at_020
        hp_flags["HP_TOPK_HIGHER"] = (gap >= 0.15)
        reasons.append(f"top10-top1@0.20={gap:+.3f}(HP>=0.15)")

    # HP_SEMANTIC_HIGHER: cos05 recall >= top1 + 0.20 at alpha=0.20
    cos05_at_020 = m(0.20, "cos05_recall")
    if math.isfinite(top1_at_020) and math.isfinite(cos05_at_020):
        gap = cos05_at_020 - top1_at_020
        hp_flags["HP_SEMANTIC_HIGHER"] = (gap >= 0.20)
        reasons.append(f"cos05-top1@0.20={gap:+.3f}(HP>=0.20)")

    # HF_METRICS_IDENTICAL: max spread across 6 metrics at any load < 0.05
    max_spread_across_loads = 0.0
    for alpha in load_sweep:
        key = int(round(alpha * 10000))
        row = per_load.get(key) or per_load.get(str(key))
        if row is None:
            continue
        mvals = list(row.get("metrics", {}).values())
        if mvals:
            spread = max(mvals) - min(mvals)
            max_spread_across_loads = max(max_spread_across_loads, spread)
    hf_identical = max_spread_across_loads < 0.05
    reasons.append(f"max_spread={max_spread_across_loads:.3f}")

    # HF_TOPK_CATASTROPHIC: at alpha=0.30, top1 < 0.30 AND top50 < 0.60
    top1_at_030 = m(0.30, "top1_recall")
    top50_at_030 = m(0.30, "top50_recall")
    hf_catastrophic = False
    if math.isfinite(top1_at_030) and math.isfinite(top50_at_030):
        hf_catastrophic = (top1_at_030 < 0.30 and top50_at_030 < 0.60)
        reasons.append(
            f"top1@0.30={top1_at_030:.3f} top50@0.30={top50_at_030:.3f}"
        )

    headline["hp_flags"] = hp_flags
    headline["max_spread_across_loads"] = float(max_spread_across_loads)
    headline["hf_metrics_identical"] = bool(hf_identical)
    headline["hf_topk_catastrophic"] = bool(hf_catastrophic)

    # Decision
    if hf_identical:
        verdict = "HARD_FAIL"
        msg = "HF_METRICS_IDENTICAL: metric-axis flat; " + " ".join(reasons)
    elif hf_catastrophic:
        verdict = "HARD_FAIL"
        msg = "HF_TOPK_CATASTROPHIC: top1<0.30 & top50<0.60 at alpha=0.30; " + " ".join(reasons)
    else:
        any_hp = any(hp_flags.values())
        if any_hp:
            passed = [k for k, v in hp_flags.items() if v]
            verdict = "HARD_PASS"
            msg = f"HP fires: {passed} | " + " ".join(reasons)
        else:
            verdict = "MIDDLE_BAND"
            msg = "no HP gate fires; metric-axis measured but no strong pattern; " + " ".join(reasons)

    return (verdict, msg, headline)
