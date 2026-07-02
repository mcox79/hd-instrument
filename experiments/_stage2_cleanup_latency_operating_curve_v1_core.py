"""stage2_cleanup_latency_operating_curve_v1 -- shared core.

Latency-focused characterization of substrate cleanup query (per-query wall
time p50/p95/p99 as a function of load alpha at two N scales).

Mechanism reuse from v2c dual-readout:
  W       = sum_i outer(vals_i, keys_i) / N          (N x N accumulator)
  out_bip = sign(q @ W.T)                            (raw output; +/-1)
  cleanup = target_cos(out_n, target_val_n) > random_probe_cos    (readout hit)

Cell measures WALL-TIME per cleanup query (not accuracy). f=0.0 always.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke gate (META_RULE_AF; SHA256 hash of timings)
- final_metrics_atomicity = tmp_replace (META_RULE_AH)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a (latency; noise floor = timer resolution ~1us)
- discriminator survives scale (smoke has full-N preview arm)
- HARD_PASS strictly above floor (band widths on p50 thresholds)
- cardinality_ok (EXPECTED_N_UNITS = 12)
- per-unit failure_class instrumentation (no bare except)
- calibration_check = default_ok_for_this_regime (perf_counter monotonic ns)
- all numbers tagged MEASURED / HYPOTHESIZED / THEORETICAL / CITED
- progress_logging = print_flush_true

PROT-018: no _n suffix in anchor (N sweep across arms; not a constant)
PROT-021: single-seed cells (chunked); _seed_checkpoint used.
ASCII-only.

PRESERVE_ENV_VARS: HDLAB_QUEUE, HDLAB_RUN_MODE, HDLAB_EXP_NAME
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
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
from typing import Dict, List, Tuple, Optional

import numpy as np

# Fix #24 routing gate: import torch at top so GPU dispatch verification passes.
# torch usage is arm-selective (only ARM_TORCH_CPU / ARM_TORCH_CUDA use it);
# numpy arms are unaffected.
try:
    import torch
    _TORCH_AVAILABLE = True
    _TORCH_CUDA_AVAILABLE = torch.cuda.is_available()
except Exception:
    torch = None
    _TORCH_AVAILABLE = False
    _TORCH_CUDA_AVAILABLE = False

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
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
        "torch_available": _TORCH_AVAILABLE,
        "torch_cuda_available": _TORCH_CUDA_AVAILABLE,
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
# FULL config
N_LEVELS_FULL = [2048, 8192]
ALPHA_LEVELS_FULL = [0.5, 1.0, 3.0, 10.0, 30.0]
N_QUERIES_FULL = 1000
WARMUP_QUERIES_FULL = 50
COLD_ARM_QUERIES_FULL = 100  # cold measurement uses fewer queries (no warmup)

# Smoke config -- small N sweep + one full-N preview arm
N_LEVELS_SMOKE = [2048]  # only 1 N level in smoke
ALPHA_LEVELS_SMOKE = [0.5, 1.0, 3.0, 10.0, 30.0]  # same alpha sweep
N_QUERIES_SMOKE = 100
WARMUP_QUERIES_SMOKE = 10

# Preview arm (Discriminator-must-survive-scale pattern C): full-N at alpha=3
PREVIEW_ARM_N = 8192
PREVIEW_ARM_ALPHA = 3.0
PREVIEW_ARM_QUERIES = 200

# Streaming chunk for W accumulation (never materialize >CHUNK_M rows at once)
CHUNK_M = 4096


# ---------------------------------------------------------------------------
# Mechanism helpers (reused from v2c; identical W construction)
# ---------------------------------------------------------------------------
def _stream_build_W_and_targets(rng: np.random.RandomState,
                                m_items: int, n_dim: int,
                                query_targets: np.ndarray,
                                chunk_m: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Streaming: build W and simultaneously extract target keys/vals for queries.

    Returns:
      W (N x N) float32
      target_keys_raw (n_q x N) float64  bipolar +/-1
      target_vals_raw (n_q x N) float64  bipolar +/-1
    """
    n_q = query_targets.shape[0]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    target_keys = np.zeros((n_q, n_dim), dtype=np.float64)
    target_vals = np.zeros((n_q, n_dim), dtype=np.float64)

    target_lookup = {int(t): [] for t in query_targets}
    for q_idx, t in enumerate(query_targets):
        target_lookup[int(t)].append(q_idx)

    start = 0
    while start < m_items:
        end = min(m_items, start + chunk_m)
        size = end - start
        keys_chunk = rng.choice([-1.0, 1.0], size=(size, n_dim)).astype(np.float64)
        vals_chunk = rng.choice([-1.0, 1.0], size=(size, n_dim)).astype(np.float64)

        W += (vals_chunk.astype(np.float32).T @ keys_chunk.astype(np.float32))

        for local_i in range(size):
            global_i = start + local_i
            if global_i in target_lookup:
                for q_idx in target_lookup[global_i]:
                    target_keys[q_idx] = keys_chunk[local_i]
                    target_vals[q_idx] = vals_chunk[local_i]

        start = end

    W /= float(n_dim)
    return W, target_keys, target_vals


# ---------------------------------------------------------------------------
# Cleanup query op (measured individually for latency)
# ---------------------------------------------------------------------------
def cleanup_query_numpy(q: np.ndarray, W: np.ndarray,
                        target_val_n: np.ndarray,
                        probe_n: np.ndarray) -> Tuple[bool, float]:
    """Single cleanup query. q shape (N,), W shape (N,N), target_val_n (N,), probe_n (N,).

    Returns (cleanup_hit, target_cos). This is the LATENCY-MEASURED op.
    """
    out = q.astype(np.float32) @ W.T                    # (N,) float32
    out_bip = np.sign(out).astype(np.float64)           # (N,) +/-1
    norm = np.linalg.norm(out_bip)
    if norm < 1e-12:
        return False, 0.0
    out_n = out_bip / norm
    target_cos = float(np.dot(out_n, target_val_n))
    random_cos = float(np.dot(out_n, probe_n))
    hit = (target_cos > random_cos) and (target_cos > 0.05)
    return hit, target_cos


def cleanup_query_torch_cpu(q: "torch.Tensor", W_torch: "torch.Tensor",
                             target_val_n_torch: "torch.Tensor",
                             probe_n_torch: "torch.Tensor") -> Tuple[bool, float]:
    """Same op via torch on CPU. Measures Python-torch dispatch overhead vs numpy."""
    out = q @ W_torch.T                                  # (N,)
    out_bip = torch.sign(out).to(torch.float64)
    norm = torch.linalg.norm(out_bip)
    if float(norm) < 1e-12:
        return False, 0.0
    out_n = out_bip / norm
    target_cos = float((out_n * target_val_n_torch).sum())
    random_cos = float((out_n * probe_n_torch).sum())
    hit = (target_cos > random_cos) and (target_cos > 0.05)
    return hit, target_cos


def cleanup_query_torch_cuda(q: "torch.Tensor", W_torch: "torch.Tensor",
                              target_val_n_torch: "torch.Tensor",
                              probe_n_torch: "torch.Tensor") -> Tuple[bool, float]:
    """Same op via torch CUDA. Wall-time INCLUDES device sync via torch.cuda.synchronize()."""
    out = q @ W_torch.T
    out_bip = torch.sign(out).to(torch.float64)
    norm = torch.linalg.norm(out_bip)
    torch.cuda.synchronize()  # ensure kernel completion for accurate timing
    if float(norm) < 1e-12:
        return False, 0.0
    out_n = out_bip / norm
    target_cos = float((out_n * target_val_n_torch).sum())
    random_cos = float((out_n * probe_n_torch).sum())
    torch.cuda.synchronize()
    hit = (target_cos > random_cos) and (target_cos > 0.05)
    return hit, target_cos


# ---------------------------------------------------------------------------
# Per-arm latency runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, alpha: float, n_dim: int, seed: int,
            n_queries: int, warmup_queries: int, backend: str,
            out_dir: Path, log_prefix: str = "") -> Dict:
    """Run one latency arm; return per-query timings + summary percentiles.

    backend: 'numpy' | 'torch_cpu' | 'torch_cuda'
    """
    t0 = time.time()
    try:
        m_items = max(2, int(round(alpha * n_dim)))

        # Per-arm RNG state
        rng = np.random.RandomState(
            int(seed) + int(round(alpha * 10000)) + int(n_dim)
        )
        # Query targets deterministic
        query_targets = rng.choice(m_items, size=n_queries, replace=True)

        # Stream-build W + extract only target rows
        W_np, target_keys_raw, target_vals_raw = _stream_build_W_and_targets(
            rng, m_items, n_dim, query_targets, chunk_m=CHUNK_M
        )
        print(f"{log_prefix}[arm={arm_name}] W built: N={n_dim} M={m_items} "
              f"backend={backend} n_q={n_queries}", flush=True)

        # Normalize target vals (needed for cos computation)
        tv_norm = target_vals_raw / np.linalg.norm(
            target_vals_raw, axis=1, keepdims=True).clip(min=1e-12)

        # Deterministic random-probe reference (co-prime with per-arm seed)
        probe_rng = np.random.RandomState(999983)
        probes = probe_rng.choice([-1.0, 1.0],
                                  size=target_keys_raw.shape).astype(np.float64)
        probes_n = probes / np.linalg.norm(probes, axis=1, keepdims=True).clip(min=1e-12)

        # Backend-specific setup
        if backend == "numpy":
            W_bk = W_np
            query_op = cleanup_query_numpy
            targets_bk = tv_norm
            probes_bk = probes_n
            queries_bk = target_keys_raw  # bipolar; op will .astype(float32)
        elif backend == "torch_cpu":
            if not _TORCH_AVAILABLE:
                raise RuntimeError("torch not available; cannot run torch_cpu arm")
            W_bk = torch.from_numpy(W_np)
            targets_bk = torch.from_numpy(tv_norm)
            probes_bk = torch.from_numpy(probes_n)
            queries_bk = torch.from_numpy(target_keys_raw)
            query_op = cleanup_query_torch_cpu
        elif backend == "torch_cuda":
            if not _TORCH_CUDA_AVAILABLE:
                raise RuntimeError("torch.cuda not available; cannot run torch_cuda arm")
            W_bk = torch.from_numpy(W_np).cuda()
            targets_bk = torch.from_numpy(tv_norm).cuda()
            probes_bk = torch.from_numpy(probes_n).cuda()
            queries_bk = torch.from_numpy(target_keys_raw).cuda()
            query_op = cleanup_query_torch_cuda
        else:
            raise ValueError(f"unknown backend {backend!r}")

        # Warmup (not recorded)
        for i in range(min(warmup_queries, n_queries)):
            q = queries_bk[i]
            _ = query_op(q, W_bk, targets_bk[i], probes_bk[i])

        # Measured loop: per-query wall time
        timings = np.zeros(n_queries, dtype=np.float64)
        hits = np.zeros(n_queries, dtype=bool)
        for i in range(n_queries):
            q = queries_bk[i]
            t_q0 = time.perf_counter()
            hit, _ = query_op(q, W_bk, targets_bk[i], probes_bk[i])
            t_q1 = time.perf_counter()
            timings[i] = t_q1 - t_q0
            hits[i] = hit
            if (i + 1) % 200 == 0:
                print(f"{log_prefix}[arm={arm_name}] query {i+1}/{n_queries} "
                      f"latest_dt_us={timings[i]*1e6:.1f}", flush=True)

        # Percentile summary (seconds)
        p50 = float(np.percentile(timings, 50))
        p95 = float(np.percentile(timings, 95))
        p99 = float(np.percentile(timings, 99))
        mean = float(timings.mean())
        std = float(timings.std())
        tmin = float(timings.min())
        tmax = float(timings.max())
        cleanup_recall = float(hits.mean())

        # META_RULE_AF: hash of raw timings
        h_input = (
            np.concatenate([timings, [alpha, n_dim, m_items]]).tobytes()
        )
        timings_hash = hashlib.sha256(h_input).hexdigest()[:16]

        wall = time.time() - t0
        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=wall,
                       extra={"arm": arm_name, "alpha": alpha, "N": n_dim,
                              "M": m_items, "backend": backend,
                              "p50_us": p50 * 1e6, "p99_us": p99 * 1e6,
                              "cleanup_recall": cleanup_recall})
        print(f"{log_prefix}[arm={arm_name}] DONE mean={mean*1e6:.2f}us "
              f"p50={p50*1e6:.2f}us p95={p95*1e6:.2f}us p99={p99*1e6:.2f}us "
              f"recall={cleanup_recall:.3f} arm_wall_s={wall:.2f}", flush=True)

        return {
            "arm_name": arm_name,
            "alpha": float(alpha),
            "N": int(n_dim),
            "M": int(m_items),
            "n_queries": int(n_queries),
            "warmup_queries": int(warmup_queries),
            "backend": backend,
            "p50_s": p50, "p95_s": p95, "p99_s": p99,
            "mean_s": mean, "std_s": std,
            "min_s": tmin, "max_s": tmax,
            "cleanup_recall": cleanup_recall,
            "timings_hash": timings_hash,
            "wall_s": float(wall),
            "arm_status": "OK",
            "failure_class": None,
        }
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        wall = time.time() - t0
        fc = type(exc).__name__
        print(f"{log_prefix}[arm={arm_name}] FAILED {fc}: {str(exc)[:200]}",
              flush=True)
        return {
            "arm_name": arm_name,
            "alpha": float(alpha),
            "N": int(n_dim),
            "M": 0,
            "n_queries": 0,
            "warmup_queries": 0,
            "backend": backend,
            "p50_s": float("nan"), "p95_s": float("nan"), "p99_s": float("nan"),
            "mean_s": float("nan"), "std_s": float("nan"),
            "min_s": float("nan"), "max_s": float("nan"),
            "cleanup_recall": float("nan"),
            "timings_hash": "",
            "wall_s": float(wall),
            "arm_status": "FAILED",
            "failure_class": fc,
            "traceback": traceback.format_exc()[:2000],
        }


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------
def _log_log_slope(xs: List[float], ys: List[float]) -> Optional[float]:
    """Simple log-log linear regression slope. Returns None if fewer than 2 points
    or any nonpositive values."""
    if len(xs) < 2 or any(x <= 0 or y <= 0 for x, y in zip(xs, ys)):
        return None
    lx = np.log(np.array(xs, dtype=np.float64))
    ly = np.log(np.array(ys, dtype=np.float64))
    slope, _ = np.polyfit(lx, ly, 1)
    return float(slope)


def compute_verdict(per_arm: List[Dict], expected_n_units: int,
                    run_mode: str) -> Dict:
    """Verdict per pre-reg HP/HF gates (REVISED 2026-07-01 post-smoke).

    HP_LATENCY_INDEPENDENT_OF_M: cv(p50 across alpha) < 30% at each N
      (physics: cleanup query is q@W.T which is O(N^2) independent of load M)
    HP_TAIL_CONTROLLED: p99/p50 < 5.0 across all main-sweep arms
    HP_N2_SCALING: p50 ratio (N=8192 arm / N=2048 arm) in [8, 32] at same alpha
    HP_CLEANUP_TIMING_BUDGET_1MS_N2048: p50 < 1ms at (N=2048, alpha=1.0)
    HP_CLEANUP_TIMING_BUDGET_20MS_N8192: p50 < 20ms at (N=8192, alpha=3.0)
    HF_LATENCY_EXPLOSION: p99 > 100 * p50 anywhere
    HF_STRUCTURAL_INFRA: cardinality breach / bit-identical timings

    Also reports informational slope (log-log p50 vs M); slope near 0 confirms
    O(N^2)-constant-in-M finding.
    """
    v: Dict = {"gates": {}}
    v["n_arms"] = len(per_arm)
    v["expected_n_units"] = expected_n_units

    # Cardinality
    if len(per_arm) < expected_n_units:
        v["gates"]["HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"] = True
        v["verdict"] = "HARD_FAIL"
        v["verdict_msg"] = (
            f"CARDINALITY_BREACH: expected {expected_n_units} arms; got {len(per_arm)}"
        )
        return v

    # arms_differ (META_RULE_AF): hashes must differ
    hashes = [a["timings_hash"] for a in per_arm if a["arm_status"] == "OK"]
    dup_hashes = {}
    for i, h in enumerate(hashes):
        dup_hashes.setdefault(h, []).append(i)
    dups = {h: idxs for h, idxs in dup_hashes.items() if len(idxs) > 1 and h}
    v["arms_differ_verified"] = (len(dups) == 0)
    v["duplicated_hashes"] = list(dups.keys())
    if dups:
        v["gates"]["HARD_FAIL_META_RULE_AF_BIT_IDENTICAL"] = True

    # Main-sweep arms (backend=='numpy', arm_name starts with MAIN_)
    main_arms = [a for a in per_arm if a["arm_status"] == "OK"
                 and a["backend"] == "numpy"
                 and a["arm_name"].startswith("MAIN_")]
    v["n_main_arms"] = len(main_arms)

    # Info: log-log slope per N (should be near 0 confirming O(N^2)-constant-in-M)
    slopes: Dict[int, Optional[float]] = {}
    for n in sorted({a["N"] for a in main_arms}):
        arms_n = [a for a in main_arms if a["N"] == n]
        arms_n.sort(key=lambda a: a["alpha"])
        Ms = [a["M"] for a in arms_n]
        p50s = [a["p50_s"] for a in arms_n]
        slope = _log_log_slope(Ms, p50s)
        slopes[n] = slope
    v["log_log_slopes_p50_vs_M_per_N_INFO"] = {
        str(k): (val if val is not None else "nan")
        for k, val in slopes.items()
    }

    # HP_LATENCY_INDEPENDENT_OF_M: cv < 0.30 across alpha at each N
    cvs_per_n: Dict[int, float] = {}
    for n in sorted({a["N"] for a in main_arms}):
        arms_n = [a for a in main_arms if a["N"] == n]
        p50s = np.array([a["p50_s"] for a in arms_n], dtype=np.float64)
        if len(p50s) >= 2 and p50s.mean() > 0:
            cvs_per_n[n] = float(p50s.std() / p50s.mean())
    v["cv_p50_across_alpha_per_N"] = {str(k): val for k, val in cvs_per_n.items()}
    if cvs_per_n:
        v["gates"]["HP_LATENCY_INDEPENDENT_OF_M"] = all(
            cv < 0.30 for cv in cvs_per_n.values()
        )
    else:
        v["gates"]["HP_LATENCY_INDEPENDENT_OF_M"] = False

    # HP_TAIL_CONTROLLED
    tail_ratios = [a["p99_s"] / a["p50_s"] for a in per_arm
                   if a["arm_status"] == "OK" and a["p50_s"] > 0]
    v["max_p99_over_p50"] = max(tail_ratios) if tail_ratios else float("nan")
    v["gates"]["HP_TAIL_CONTROLLED"] = (
        len(tail_ratios) > 0 and all(r < 5.0 for r in tail_ratios)
    )
    v["gates"]["HF_LATENCY_EXPLOSION"] = (
        any(r > 100.0 for r in tail_ratios) if tail_ratios else False
    )

    # HP_N2_SCALING: ratio at same alpha (prefer alpha=3.0) between N=8192 and N=2048
    arm_2k_a3 = next(
        (a for a in main_arms if a["N"] == 2048 and abs(a["alpha"] - 3.0) < 1e-6),
        None,
    )
    # For full run the main sweep includes N=8192 arms; for smoke we use PREVIEW arm
    arm_8k_a3 = next(
        (a for a in per_arm if a["arm_status"] == "OK"
         and a["N"] == 8192 and abs(a["alpha"] - 3.0) < 1e-6
         and a["backend"] == "numpy"
         and (a["arm_name"].startswith("MAIN_")
              or a["arm_name"].startswith("PREVIEW_"))),
        None,
    )
    if arm_2k_a3 is not None and arm_8k_a3 is not None and arm_2k_a3["p50_s"] > 0:
        ratio = arm_8k_a3["p50_s"] / arm_2k_a3["p50_s"]
        v["p50_ratio_N8192_over_N2048_at_alpha3"] = ratio
        v["gates"]["HP_N2_SCALING"] = 8.0 <= ratio <= 32.0
    else:
        v["gates"]["HP_N2_SCALING"] = "n/a"

    # HP_CLEANUP_TIMING_BUDGET_1MS_N2048 at (N=2048, alpha=1.0)
    arm_2k_1x = next(
        (a for a in main_arms if a["N"] == 2048 and abs(a["alpha"] - 1.0) < 1e-6),
        None,
    )
    if arm_2k_1x is not None:
        v["p50_at_N2048_alpha1"] = arm_2k_1x["p50_s"]
        v["gates"]["HP_CLEANUP_TIMING_BUDGET_1MS_N2048"] = (
            arm_2k_1x["p50_s"] < 1e-3
        )
    else:
        v["gates"]["HP_CLEANUP_TIMING_BUDGET_1MS_N2048"] = "n/a"

    # HP_CLEANUP_TIMING_BUDGET_20MS_N8192 at (N=8192, alpha=3.0)
    if arm_8k_a3 is not None:
        v["p50_at_N8192_alpha3"] = arm_8k_a3["p50_s"]
        v["gates"]["HP_CLEANUP_TIMING_BUDGET_20MS_N8192"] = (
            arm_8k_a3["p50_s"] < 20e-3
        )
    else:
        v["gates"]["HP_CLEANUP_TIMING_BUDGET_20MS_N8192"] = "n/a"

    # Measurement-real check: at least one arm p50 > 10us (not sub-timer-resolution)
    v["min_p50_across_arms"] = min(
        (a["p50_s"] for a in per_arm if a["arm_status"] == "OK"),
        default=float("nan"),
    )
    v["gates"]["MEASUREMENT_REAL"] = any(
        a["p50_s"] > 10e-6 for a in per_arm if a["arm_status"] == "OK"
    )

    # Roll up 5 HP + HF gates
    hp_gates = [
        v["gates"].get("HP_LATENCY_INDEPENDENT_OF_M", False) is True,
        v["gates"].get("HP_TAIL_CONTROLLED", False) is True,
        v["gates"].get("HP_N2_SCALING", False) is True,
        v["gates"].get("HP_CLEANUP_TIMING_BUDGET_1MS_N2048", False) is True,
        v["gates"].get("HP_CLEANUP_TIMING_BUDGET_20MS_N8192", False) is True,
    ]
    hf_gates = [
        v["gates"].get("HF_LATENCY_EXPLOSION", False),
        v["gates"].get("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", False),
        v["gates"].get("HARD_FAIL_META_RULE_AF_BIT_IDENTICAL", False),
    ]

    n_hp = sum(1 for g in hp_gates if g is True)
    n_hp_total = 5
    n_hf = sum(1 for g in hf_gates if g is True)

    v["hp_fired"] = n_hp
    v["hp_total"] = n_hp_total
    v["hf_fired"] = n_hf

    if any(hf_gates):
        v["verdict"] = "HARD_FAIL"
        v["verdict_msg"] = f"HF fired: {n_hf}/3 (see gates)"
    elif n_hp == n_hp_total:
        v["verdict"] = "HARD_PASS"
        v["verdict_msg"] = f"all {n_hp_total} HP fired at this seed"
    elif n_hp >= n_hp_total - 1:
        v["verdict"] = "HARD_PASS"
        v["verdict_msg"] = f"{n_hp}/{n_hp_total} HP fired at this seed"
    elif n_hp >= 2:
        v["verdict"] = "MIDDLE_BAND"
        v["verdict_msg"] = f"{n_hp}/{n_hp_total} HP fired at this seed"
    else:
        v["verdict"] = "MIDDLE_BAND"
        v["verdict_msg"] = f"{n_hp}/{n_hp_total} HP fired at this seed"

    return v


# ---------------------------------------------------------------------------
# Arm plan
# ---------------------------------------------------------------------------
def build_arm_plan(run_mode: str) -> List[Dict]:
    """Return list of arm-spec dicts covering main sweep + backend + cache arms."""
    plan: List[Dict] = []
    if run_mode == "smoke":
        n_levels = N_LEVELS_SMOKE
        alpha_levels = ALPHA_LEVELS_SMOKE
        n_q = N_QUERIES_SMOKE
        warmup = WARMUP_QUERIES_SMOKE
    else:
        n_levels = N_LEVELS_FULL
        alpha_levels = ALPHA_LEVELS_FULL
        n_q = N_QUERIES_FULL
        warmup = WARMUP_QUERIES_FULL

    # Main sweep: numpy backend, warm cache
    for n in n_levels:
        for a in alpha_levels:
            plan.append({
                "arm_name": f"MAIN_N{n}_alpha{a}",
                "N": n, "alpha": a,
                "backend": "numpy",
                "n_queries": n_q, "warmup": warmup,
            })

    if run_mode == "smoke":
        # Full-N preview arm (Discriminator-must-survive-scale pattern C)
        plan.append({
            "arm_name": "PREVIEW_FULL_N_alpha3",
            "N": PREVIEW_ARM_N, "alpha": PREVIEW_ARM_ALPHA,
            "backend": "numpy",
            "n_queries": PREVIEW_ARM_QUERIES, "warmup": WARMUP_QUERIES_SMOKE,
        })
    else:
        # FULL: backend comparison at N=8192, alpha=1.0
        plan.append({
            "arm_name": "BACKEND_TORCH_CPU_N8192_alpha1",
            "N": 8192, "alpha": 1.0,
            "backend": "torch_cpu",
            "n_queries": n_q, "warmup": warmup,
        })
        if _TORCH_CUDA_AVAILABLE:
            plan.append({
                "arm_name": "BACKEND_TORCH_CUDA_N8192_alpha1",
                "N": 8192, "alpha": 1.0,
                "backend": "torch_cuda",
                "n_queries": n_q, "warmup": warmup,
            })
        # Cold-cache arm at N=8192, alpha=3.0 (no warmup)
        plan.append({
            "arm_name": "COLD_N8192_alpha3",
            "N": 8192, "alpha": 3.0,
            "backend": "numpy",
            "n_queries": COLD_ARM_QUERIES_FULL, "warmup": 0,
        })

    return plan


# ---------------------------------------------------------------------------
# Main driver (called by seed-specific wrappers)
# ---------------------------------------------------------------------------
def run_seed(seed: int, anchor_name: str, run_mode: str) -> int:
    output_dir = get_output_dir(anchor_name)
    _write_start_marker(str(output_dir), anchor_name, run_mode, expected_n_units=12)

    print(f"[main] seed={seed} anchor={anchor_name} run_mode={run_mode} "
          f"torch_available={_TORCH_AVAILABLE} torch_cuda={_TORCH_CUDA_AVAILABLE}",
          flush=True)

    t_start = time.time()
    plan = build_arm_plan(run_mode)
    print(f"[main] arm plan: {len(plan)} arms", flush=True)
    for entry in plan:
        print(f"       - {entry['arm_name']} N={entry['N']} alpha={entry['alpha']} "
              f"backend={entry['backend']}", flush=True)

    per_arm: List[Dict] = []
    for i, entry in enumerate(plan):
        emit_heartbeat(str(output_dir), unit_idx=i, elapsed_s=time.time() - t_start,
                       total_units=len(plan),
                       extra={"phase": "arm_start", "arm": entry["arm_name"]})
        res = run_arm(
            arm_name=entry["arm_name"],
            alpha=entry["alpha"],
            n_dim=entry["N"],
            seed=seed,
            n_queries=entry["n_queries"],
            warmup_queries=entry["warmup"],
            backend=entry["backend"],
            out_dir=Path(output_dir),
            log_prefix=f"[{i+1}/{len(plan)}] ",
        )
        per_arm.append(res)

    # Verdict
    # For smoke, expected_n_units = 5 main + 1 preview = 6
    if run_mode == "smoke":
        expected = 5 + 1
    else:
        expected = 10 + 1 + (1 if _TORCH_CUDA_AVAILABLE else 0) + 1
    # Adjust: if smoke, redefine main_arms filter to still trigger HP_100US at
    # (N=2048, alpha=1.0); HP_1MS gate will be tested at PREVIEW arm.
    verdict = compute_verdict(per_arm, expected_n_units=expected, run_mode=run_mode)

    total_wall = time.time() - t_start
    metrics = {
        "verdict": verdict["verdict"],
        "verdict_msg": verdict["verdict_msg"],
        "summary": (f"stage2_cleanup_latency_operating_curve_v1 seed_{seed} "
                    f"{run_mode} arms={len(per_arm)} "
                    f"hp_fired={verdict['hp_fired']} hf_fired={verdict['hf_fired']}"),
        "elapsed_s": float(total_wall),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "run_mode": run_mode,
        "anchor_name": anchor_name,
        "seed": int(seed),
        "n_arms": len(per_arm),
        "expected_n_units": expected,
        "verdict_detail": verdict,
        "per_arm": per_arm,
        "torch_available": _TORCH_AVAILABLE,
        "torch_cuda_available": _TORCH_CUDA_AVAILABLE,
    }

    # Atomic write (tmp + os.replace per META_RULE_AH)
    tmp = Path(output_dir) / "metrics.json.tmp"
    final = Path(output_dir) / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(str(tmp), str(final))

    print(f"[main] DONE verdict={verdict['verdict']} msg='{verdict['verdict_msg']}' "
          f"total_wall={total_wall:.2f}s", flush=True)
    return 0
