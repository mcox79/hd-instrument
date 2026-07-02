"""stage2_commercial_M_latency_percentiles_v1 -- shared core.

Wall-time (p50/p95/p99) per full cortex round-trip cleanup query at
COMMERCIAL M scales (M in {100k, 500k, 1M}), N=8192 fixed, across
three backends (numpy / torch_cpu / torch_cuda) with per-backend
fallback if unavailable on runner.

Companion cell to stage2_cleanup_latency_operating_curve_v1: v1 sweeps
alpha at N in {2048,8192} and shows the cleanup op is O(N^2) per query,
constant in M/alpha. This cell HOLDS N=8192 fixed and pushes M to the
commercial regime -- what happens to (a) W storage, (b) W build time, and
critically (c) per-query wall latency when M is large but N is unchanged.

MECHANISM (identical to cleanup_latency v1 for query op):
  W          = sum_i outer(vals_i, keys_i) / N          (N x N accumulator)
  out_bip    = sign(q @ W.T)                            (raw output; +/-1)
  cleanup    = (target_cos(out_n, target_val_n) > random_probe_cos)
               AND (target_cos > 0.05)

The per-query op is O(N^2) regardless of M -- that is the substrate's
key SLA property. This cell is the M3 Phase 1 SLA baseline evidence:
if per-query p50 < 100ms at M=1M with torch.cuda, M3 can promise
real-time conversational routing at commercial scale.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke gate (META_RULE_AF; SHA256 hash of timings)
- final_metrics_atomicity = tmp_replace (META_RULE_AH)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: latency measurement; noise floor = perf_counter resolution (~ns).
  HP thresholds are policy targets not statistical claims; no CRLB applies.
- discriminator survives scale: smoke includes M=100k preview arm at FULL N
- HARD_PASS strictly above floor
- cardinality_ok: EXPECTED_N_UNITS declared per run_mode
- per-unit failure_class instrumentation (no bare except)
- calibration_check = default_ok_for_this_regime (perf_counter monotonic;
  torch.cuda.synchronize before/after ensures kernel completion)
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
- progress_logging = print_flush_true
- baseline_in_band: N/A (latency measurement not accuracy; ARM diverge on
  timing not on saturation; arms_differ hash-check is the AG-equivalent)

PROT-018: no _n suffix in anchor (single fixed N=8192; not a sweep axis).
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

from experiments._seed_checkpoint import get_output_dir


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
# FULL config: fixed N=8192, sweep M x backend
N_DIM_FULL = 8192
M_SWEEP_FULL = [100_000, 500_000, 1_000_000]
# Backends attempted; each is skipped/marked ARM_UNAVAILABLE if unsupported.
BACKENDS_FULL = ["numpy", "torch_cpu", "torch_cuda"]
N_QUERIES_FULL = 1000
WARMUP_QUERIES_FULL = 100

# Smoke config: FULL N=8192 kept (discriminator-must-survive-scale pattern A);
# reduce M sweep + query count. Smoke MUST fire at commercial regime M=100k so
# result is diagnostic of actual behavior, not toy-M.
N_DIM_SMOKE = 8192
M_SWEEP_SMOKE = [100_000]                    # single commercial M
BACKENDS_SMOKE = ["numpy", "torch_cpu"]      # torch_cuda not attempted in smoke
N_QUERIES_SMOKE = 50
WARMUP_QUERIES_SMOKE = 10

# Preview arm (Discriminator-must-survive-scale pattern C):
# even in smoke, attempt one torch_cuda arm at M=100k -- confirms GPU pathway
# fires without burning full time. Marked ARM_UNAVAILABLE if no CUDA.
PREVIEW_ARM_M = 100_000
PREVIEW_ARM_BACKEND = "torch_cuda"
PREVIEW_ARM_QUERIES = 50

# Streaming chunk for W accumulation (never materialize >CHUNK_M rows at once)
CHUNK_M_NUMPY = 4096
CHUNK_M_TORCH = 4096

# HP thresholds (policy targets; all HYPOTHESIZED@this_module)
HP_M1M_CUDA_P50_S = 0.100           # 100ms at (M=1M, backend=torch_cuda)
HP_M100K_CUDA_P50_S = 0.010         # 10ms at (M=100k, backend=torch_cuda)
HP_TAIL_RATIO_MAX = 3.0             # p99/p50 < 3.0 everywhere
HP_NUMPY_M_RATIO_MIN = 0.5          # numpy p50 M-invariance (op is O(N^2))
HP_NUMPY_M_RATIO_MAX = 5.0          # allow some cache effects
HP_CUDA_SPEEDUP_MAX = 0.5           # torch_cuda p50 < 0.5 * numpy p50 at M=1M

# HF thresholds
HF_M1M_P50_S = 1.0                  # any backend > 1s at M=1M = commercial-blown
HF_TAIL_RATIO_MAX = 100.0           # p99/p50 > 100 = pathological


# ---------------------------------------------------------------------------
# Mechanism helpers
# ---------------------------------------------------------------------------
def _stream_build_W_and_targets_numpy(
    rng: np.random.RandomState,
    m_items: int, n_dim: int,
    query_targets: np.ndarray,
    chunk_m: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Streaming numpy build. Returns (W float32 (N,N), target_keys (n_q,N),
    target_vals (n_q,N)). Never materializes >chunk_m rows at once."""
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
    out = q.astype(np.float32) @ W.T                    # (N,) float32
    out_bip = np.sign(out).astype(np.float64)
    norm = np.linalg.norm(out_bip)
    if norm < 1e-12:
        return False, 0.0
    out_n = out_bip / norm
    target_cos = float(np.dot(out_n, target_val_n))
    random_cos = float(np.dot(out_n, probe_n))
    hit = (target_cos > random_cos) and (target_cos > 0.05)
    return hit, target_cos


def cleanup_query_torch_cpu(q, W_torch, target_val_n_torch, probe_n_torch):
    # q is float64 (bipolar) but W_torch is float32; cast q to f32 to match
    # (mirrors numpy path which does q.astype(float32)).
    out = q.to(torch.float32) @ W_torch.T
    out_bip = torch.sign(out).to(torch.float64)
    norm = torch.linalg.norm(out_bip)
    if float(norm) < 1e-12:
        return False, 0.0
    out_n = out_bip / norm
    target_cos = float((out_n * target_val_n_torch).sum())
    random_cos = float((out_n * probe_n_torch).sum())
    hit = (target_cos > random_cos) and (target_cos > 0.05)
    return hit, target_cos


def cleanup_query_torch_cuda(q, W_torch, target_val_n_torch, probe_n_torch):
    # Wall time INCLUDES sync so we measure end-to-end kernel completion.
    # q is float64 (bipolar) but W_torch is float32; cast q to f32.
    out = q.to(torch.float32) @ W_torch.T
    out_bip = torch.sign(out).to(torch.float64)
    norm = torch.linalg.norm(out_bip)
    torch.cuda.synchronize()
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
def run_arm(arm_name: str, m_items: int, n_dim: int, seed: int,
            n_queries: int, warmup_queries: int, backend: str,
            out_dir: Path, log_prefix: str = "") -> Dict:
    """Run one latency arm; return per-query timings + summary percentiles."""
    t0 = time.time()
    try:
        # Availability preflight
        if backend == "torch_cpu" and not _TORCH_AVAILABLE:
            raise RuntimeError("torch not available; cannot run torch_cpu arm")
        if backend == "torch_cuda" and not _TORCH_CUDA_AVAILABLE:
            raise RuntimeError("torch.cuda not available; cannot run torch_cuda arm")

        # Per-arm RNG (M-and-backend-varying seed offset)
        rng = np.random.RandomState(
            int(seed) + int(m_items // 1000) * 1009 + hash(backend) % 991
        )
        query_targets = rng.choice(m_items, size=n_queries, replace=True)

        t_build_start = time.time()
        W_np, target_keys_raw, target_vals_raw = _stream_build_W_and_targets_numpy(
            rng, m_items, n_dim, query_targets, chunk_m=CHUNK_M_NUMPY
        )
        t_build_s = time.time() - t_build_start
        print(f"{log_prefix}[arm={arm_name}] W built M={m_items} N={n_dim} "
              f"backend={backend} n_q={n_queries} build_s={t_build_s:.2f}", flush=True)

        tv_norm = target_vals_raw / np.linalg.norm(
            target_vals_raw, axis=1, keepdims=True).clip(min=1e-12)
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
            queries_bk = target_keys_raw
        elif backend == "torch_cpu":
            W_bk = torch.from_numpy(W_np)
            targets_bk = torch.from_numpy(tv_norm)
            probes_bk = torch.from_numpy(probes_n)
            queries_bk = torch.from_numpy(target_keys_raw)
            query_op = cleanup_query_torch_cpu
        elif backend == "torch_cuda":
            W_bk = torch.from_numpy(W_np).cuda()
            targets_bk = torch.from_numpy(tv_norm).cuda()
            probes_bk = torch.from_numpy(probes_n).cuda()
            queries_bk = torch.from_numpy(target_keys_raw).cuda()
            query_op = cleanup_query_torch_cuda
            torch.cuda.synchronize()
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

        p50 = float(np.percentile(timings, 50))
        p95 = float(np.percentile(timings, 95))
        p99 = float(np.percentile(timings, 99))
        mean = float(timings.mean())
        std = float(timings.std())
        tmin = float(timings.min())
        tmax = float(timings.max())
        cleanup_recall = float(hits.mean())

        # META_RULE_AF: hash of raw timings + config
        h_input = np.concatenate(
            [timings, [float(m_items), float(n_dim), float(hash(backend) % 10007)]]
        ).tobytes()
        timings_hash = hashlib.sha256(h_input).hexdigest()[:16]

        wall = time.time() - t0
        emit_heartbeat(out_dir, unit_idx=0, elapsed_s=wall,
                       extra={"arm": arm_name, "M": m_items, "N": n_dim,
                              "backend": backend,
                              "p50_us": p50 * 1e6, "p99_us": p99 * 1e6,
                              "cleanup_recall": cleanup_recall,
                              "build_s": t_build_s})
        print(f"{log_prefix}[arm={arm_name}] DONE p50={p50*1e6:.2f}us "
              f"p95={p95*1e6:.2f}us p99={p99*1e6:.2f}us "
              f"recall={cleanup_recall:.3f} arm_wall_s={wall:.2f}", flush=True)

        return {
            "arm_name": arm_name,
            "M": int(m_items),
            "N": int(n_dim),
            "n_queries": int(n_queries),
            "warmup_queries": int(warmup_queries),
            "backend": backend,
            "p50_s": p50, "p95_s": p95, "p99_s": p99,
            "mean_s": mean, "std_s": std,
            "min_s": tmin, "max_s": tmax,
            "cleanup_recall": cleanup_recall,
            "timings_hash": timings_hash,
            "wall_s": float(wall),
            "build_s": float(t_build_s),
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
        # Backend-unavailable is a NORMAL condition on this runner (e.g. no CUDA)
        # -- distinguish from real crash.
        msg = str(exc)[:200]
        is_unavailable = ("not available" in msg)
        arm_status = "UNAVAILABLE" if is_unavailable else "FAILED"
        print(f"{log_prefix}[arm={arm_name}] {arm_status} {fc}: {msg}", flush=True)
        return {
            "arm_name": arm_name,
            "M": int(m_items),
            "N": int(n_dim),
            "n_queries": 0,
            "warmup_queries": 0,
            "backend": backend,
            "p50_s": float("nan"), "p95_s": float("nan"), "p99_s": float("nan"),
            "mean_s": float("nan"), "std_s": float("nan"),
            "min_s": float("nan"), "max_s": float("nan"),
            "cleanup_recall": float("nan"),
            "timings_hash": "",
            "wall_s": float(wall),
            "build_s": 0.0,
            "arm_status": arm_status,
            "failure_class": fc if not is_unavailable else None,
            "traceback": traceback.format_exc()[:2000] if not is_unavailable else "",
        }


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------
def _get_arm(per_arm: List[Dict], M: int, backend: str) -> Optional[Dict]:
    """Return the OK arm matching (M, backend); None if not present or not OK."""
    for a in per_arm:
        if (a["arm_status"] == "OK" and a["M"] == M
                and a["backend"] == backend):
            return a
    return None


def compute_verdict(per_arm: List[Dict], expected_n_units: int,
                    run_mode: str) -> Dict:
    """Verdict per pre-reg HP/HF gates.

    HP_M1M_UNDER_100MS       at (M=1M, torch_cuda): p50 < 100ms
    HP_M100K_UNDER_10MS      at (M=100k, torch_cuda): p50 < 10ms
    HP_TAIL_CONTROLLED       all OK arms: p99/p50 < 3.0
    HP_NUMPY_SCALES_INVARIANT numpy p50 at M=1M / M=100k in [0.5, 5.0]
                              (per-query op is O(N^2) independent of M)
    HP_CUDA_SPEEDUP          torch_cuda p50 at M=1M < 0.5 * numpy p50 at M=1M
    HF_M1M_INFEASIBLE        any backend p50 > 1000ms at M=1M
    HF_TAIL_EXPLOSION        p99/p50 > 100 anywhere
    HF_STRUCTURAL_INFRA      cardinality breach / bit-identical timings

    Notes:
    - HP gates requiring torch_cuda evaluate to "n/a" if the runner lacks CUDA;
      they are excluded from n_hp_total when n/a (so verdict still reachable).
    - HP_NUMPY_SCALES_INVARIANT tests the M-invariance FINDING from v1 at N=8192
      commercial regime. If p50 ratio departs [0.5, 5.0], the M dependence
      is real at these scales and M3 SLA must budget for it.
    """
    v: Dict = {"gates": {}}
    v["n_arms"] = len(per_arm)
    v["expected_n_units"] = expected_n_units

    # Cardinality: count ALL arms (OK + UNAVAILABLE + FAILED). Backend unavailability
    # is a NORMAL condition; UNAVAILABLE arms count toward cardinality.
    if len(per_arm) < expected_n_units:
        v["gates"]["HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"] = True
        v["verdict"] = "HARD_FAIL"
        v["verdict_msg"] = (
            f"CARDINALITY_BREACH: expected {expected_n_units} arms; "
            f"got {len(per_arm)}"
        )
        return v

    # arms_differ (META_RULE_AF): non-empty hashes must be unique
    hashes = [a["timings_hash"] for a in per_arm if a["timings_hash"]]
    dup_map = {}
    for i, h in enumerate(hashes):
        dup_map.setdefault(h, []).append(i)
    dups = {h: idxs for h, idxs in dup_map.items() if len(idxs) > 1}
    v["arms_differ_verified"] = (len(dups) == 0)
    v["duplicated_hashes"] = list(dups.keys())
    if dups:
        v["gates"]["HARD_FAIL_META_RULE_AF_BIT_IDENTICAL"] = True

    # Track which arms ran OK vs UNAVAILABLE (for reporting)
    v["arm_status_summary"] = {}
    for a in per_arm:
        key = f"{a['backend']}_M{a['M']}"
        v["arm_status_summary"][key] = a["arm_status"]

    ok_arms = [a for a in per_arm if a["arm_status"] == "OK"]
    v["n_ok_arms"] = len(ok_arms)

    # ---- HP_TAIL_CONTROLLED (all OK arms) ----
    tail_ratios = [a["p99_s"] / a["p50_s"] for a in ok_arms if a["p50_s"] > 0]
    v["max_p99_over_p50"] = max(tail_ratios) if tail_ratios else float("nan")
    if tail_ratios:
        v["gates"]["HP_TAIL_CONTROLLED"] = all(r < HP_TAIL_RATIO_MAX
                                               for r in tail_ratios)
        v["gates"]["HF_TAIL_EXPLOSION"] = any(r > HF_TAIL_RATIO_MAX
                                              for r in tail_ratios)
    else:
        v["gates"]["HP_TAIL_CONTROLLED"] = False
        v["gates"]["HF_TAIL_EXPLOSION"] = False

    # ---- HP_M1M_UNDER_100MS (torch_cuda at M=1M) ----
    cuda_1m = _get_arm(per_arm, 1_000_000, "torch_cuda")
    if cuda_1m is None:
        v["gates"]["HP_M1M_UNDER_100MS"] = "n/a"
    else:
        v["p50_cuda_M1M"] = cuda_1m["p50_s"]
        v["gates"]["HP_M1M_UNDER_100MS"] = (cuda_1m["p50_s"] < HP_M1M_CUDA_P50_S)

    # ---- HP_M100K_UNDER_10MS (torch_cuda at M=100k) ----
    cuda_100k = _get_arm(per_arm, 100_000, "torch_cuda")
    if cuda_100k is None:
        v["gates"]["HP_M100K_UNDER_10MS"] = "n/a"
    else:
        v["p50_cuda_M100K"] = cuda_100k["p50_s"]
        v["gates"]["HP_M100K_UNDER_10MS"] = (cuda_100k["p50_s"]
                                             < HP_M100K_CUDA_P50_S)

    # ---- HP_NUMPY_SCALES_INVARIANT (M-invariance of per-query op) ----
    numpy_1m = _get_arm(per_arm, 1_000_000, "numpy")
    numpy_100k = _get_arm(per_arm, 100_000, "numpy")
    if (numpy_1m is None or numpy_100k is None
            or numpy_100k["p50_s"] <= 0):
        v["gates"]["HP_NUMPY_SCALES_INVARIANT"] = "n/a"
    else:
        ratio = numpy_1m["p50_s"] / numpy_100k["p50_s"]
        v["numpy_p50_ratio_M1M_over_M100K"] = ratio
        v["gates"]["HP_NUMPY_SCALES_INVARIANT"] = (
            HP_NUMPY_M_RATIO_MIN <= ratio <= HP_NUMPY_M_RATIO_MAX
        )

    # ---- HP_CUDA_SPEEDUP (torch_cuda beats numpy at M=1M) ----
    if (cuda_1m is None or numpy_1m is None or numpy_1m["p50_s"] <= 0):
        v["gates"]["HP_CUDA_SPEEDUP"] = "n/a"
    else:
        speedup_ratio = cuda_1m["p50_s"] / numpy_1m["p50_s"]
        v["cuda_over_numpy_p50_ratio_at_M1M"] = speedup_ratio
        v["gates"]["HP_CUDA_SPEEDUP"] = (speedup_ratio < HP_CUDA_SPEEDUP_MAX)

    # ---- HF_M1M_INFEASIBLE (any backend > 1s at M=1M) ----
    m1m_arms_ok = [a for a in per_arm
                   if a["arm_status"] == "OK" and a["M"] == 1_000_000]
    v["p50_all_backends_M1M"] = {a["backend"]: a["p50_s"] for a in m1m_arms_ok}
    if m1m_arms_ok:
        v["gates"]["HF_M1M_INFEASIBLE"] = any(
            a["p50_s"] > HF_M1M_P50_S for a in m1m_arms_ok
        )
    else:
        v["gates"]["HF_M1M_INFEASIBLE"] = False

    # ---- Measurement-real check ----
    v["min_p50_across_ok_arms_s"] = min(
        (a["p50_s"] for a in ok_arms), default=float("nan"),
    )
    v["gates"]["MEASUREMENT_REAL"] = any(a["p50_s"] > 10e-6 for a in ok_arms)

    # ---- Roll up HP + HF ----
    # HP roll-up: count only gates that are True/False; n/a excluded from denom.
    hp_gates_named = [
        "HP_M1M_UNDER_100MS", "HP_M100K_UNDER_10MS",
        "HP_TAIL_CONTROLLED", "HP_NUMPY_SCALES_INVARIANT",
        "HP_CUDA_SPEEDUP",
    ]
    hp_true = 0
    hp_denom = 0
    for name in hp_gates_named:
        val = v["gates"].get(name, "n/a")
        if val == "n/a":
            continue
        hp_denom += 1
        if val is True:
            hp_true += 1

    hf_true = sum(
        1 for name in [
            "HF_M1M_INFEASIBLE", "HF_TAIL_EXPLOSION",
            "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "HARD_FAIL_META_RULE_AF_BIT_IDENTICAL",
        ] if v["gates"].get(name) is True
    )

    v["hp_fired"] = hp_true
    v["hp_denominator"] = hp_denom
    v["hp_total_defined"] = len(hp_gates_named)
    v["hf_fired"] = hf_true

    # Band-floor discipline (META_RULE_L): HARD_PASS requires enough evaluable
    # HP gates to be substantive. Config with < 3 evaluable HP gates (e.g. no
    # CUDA on runner) cannot fire HARD_PASS regardless -- report MIDDLE_BAND.
    HP_HARD_PASS_MIN_DENOM = 3

    if hf_true > 0:
        v["verdict"] = "HARD_FAIL"
        v["verdict_msg"] = f"HF fired: {hf_true} (see gates)"
    elif hp_denom == 0:
        v["verdict"] = "MIDDLE_BAND"
        v["verdict_msg"] = "no HP gate evaluable at this config (denom=0)"
    elif hp_denom < HP_HARD_PASS_MIN_DENOM:
        # Too few evaluable gates for HARD_PASS. Report MIDDLE_BAND regardless
        # of hp_true -- runner config is insufficient (e.g. CUDA missing +
        # cross-backend arms failed).
        v["verdict"] = "MIDDLE_BAND"
        v["verdict_msg"] = (
            f"only {hp_denom} HP evaluable (need >= {HP_HARD_PASS_MIN_DENOM} "
            f"for HARD_PASS); {hp_true} fired"
        )
    elif hp_true == hp_denom:
        v["verdict"] = "HARD_PASS"
        v["verdict_msg"] = (
            f"all {hp_true}/{hp_denom} evaluable HP fired "
            f"({v['hp_total_defined']} defined)"
        )
    elif hp_true >= hp_denom - 1:
        v["verdict"] = "HARD_PASS"
        v["verdict_msg"] = (
            f"{hp_true}/{hp_denom} evaluable HP fired "
            f"({v['hp_total_defined']} defined)"
        )
    elif hp_true >= max(1, hp_denom // 2):
        v["verdict"] = "MIDDLE_BAND"
        v["verdict_msg"] = f"{hp_true}/{hp_denom} evaluable HP fired"
    else:
        v["verdict"] = "MIDDLE_BAND"
        v["verdict_msg"] = f"{hp_true}/{hp_denom} evaluable HP fired"

    return v


# ---------------------------------------------------------------------------
# Arm plan
# ---------------------------------------------------------------------------
def build_arm_plan(run_mode: str) -> List[Dict]:
    """Return list of arm-spec dicts. Every (M, backend) combo gets an arm even
    if the backend is unavailable -- that yields a UNAVAILABLE arm (counted
    toward cardinality but not toward HP evaluation)."""
    plan: List[Dict] = []
    if run_mode == "smoke":
        n_dim = N_DIM_SMOKE
        m_sweep = M_SWEEP_SMOKE
        backends = BACKENDS_SMOKE
        n_q = N_QUERIES_SMOKE
        warmup = WARMUP_QUERIES_SMOKE
        for M in m_sweep:
            for backend in backends:
                plan.append({
                    "arm_name": f"MAIN_M{M}_backend_{backend}",
                    "M": M, "N": n_dim,
                    "backend": backend,
                    "n_queries": n_q, "warmup": warmup,
                })
        # Preview CUDA arm at commercial M (fires only if CUDA is present)
        plan.append({
            "arm_name": f"PREVIEW_M{PREVIEW_ARM_M}_backend_{PREVIEW_ARM_BACKEND}",
            "M": PREVIEW_ARM_M, "N": n_dim,
            "backend": PREVIEW_ARM_BACKEND,
            "n_queries": PREVIEW_ARM_QUERIES, "warmup": WARMUP_QUERIES_SMOKE,
        })
    else:
        n_dim = N_DIM_FULL
        m_sweep = M_SWEEP_FULL
        backends = BACKENDS_FULL
        n_q = N_QUERIES_FULL
        warmup = WARMUP_QUERIES_FULL
        for M in m_sweep:
            for backend in backends:
                plan.append({
                    "arm_name": f"MAIN_M{M}_backend_{backend}",
                    "M": M, "N": n_dim,
                    "backend": backend,
                    "n_queries": n_q, "warmup": warmup,
                })
    return plan


def expected_n_units_for(run_mode: str) -> int:
    return len(build_arm_plan(run_mode))


# ---------------------------------------------------------------------------
# Main driver (called by seed-specific wrappers)
# ---------------------------------------------------------------------------
def run_seed(seed: int, anchor_name: str, run_mode: str) -> int:
    output_dir = get_output_dir(anchor_name)
    expected = expected_n_units_for(run_mode)
    _write_start_marker(str(output_dir), anchor_name, run_mode,
                        expected_n_units=expected)

    print(f"[main] seed={seed} anchor={anchor_name} run_mode={run_mode} "
          f"torch_available={_TORCH_AVAILABLE} torch_cuda={_TORCH_CUDA_AVAILABLE}",
          flush=True)

    t_start = time.time()
    plan = build_arm_plan(run_mode)
    print(f"[main] arm plan: {len(plan)} arms", flush=True)
    for entry in plan:
        print(f"       - {entry['arm_name']} M={entry['M']} N={entry['N']} "
              f"backend={entry['backend']} n_q={entry['n_queries']}", flush=True)

    per_arm: List[Dict] = []
    for i, entry in enumerate(plan):
        emit_heartbeat(str(output_dir), unit_idx=i, elapsed_s=time.time() - t_start,
                       total_units=len(plan),
                       extra={"phase": "arm_start", "arm": entry["arm_name"]})
        res = run_arm(
            arm_name=entry["arm_name"],
            m_items=entry["M"],
            n_dim=entry["N"],
            seed=seed,
            n_queries=entry["n_queries"],
            warmup_queries=entry["warmup"],
            backend=entry["backend"],
            out_dir=Path(output_dir),
            log_prefix=f"[{i+1}/{len(plan)}] ",
        )
        per_arm.append(res)

    verdict = compute_verdict(per_arm, expected_n_units=expected, run_mode=run_mode)
    total_wall = time.time() - t_start
    metrics = {
        "verdict": verdict["verdict"],
        "verdict_msg": verdict["verdict_msg"],
        "summary": (f"stage2_commercial_M_latency_percentiles_v1 seed_{seed} "
                    f"{run_mode} arms={len(per_arm)} "
                    f"hp_fired={verdict['hp_fired']}/{verdict['hp_denominator']} "
                    f"hf_fired={verdict['hf_fired']}"),
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
