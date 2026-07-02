"""stage2_commercial_M_latency_percentiles_v2_timeout_fixed -- shared core.

v2 forks v1 with TWO architectural fixes for the 3600s-timeout salvage
lesson (2026-07-02 3-seed dispatch: 7/9 arms per seed captured only in
heartbeat, metrics.json never written, M=1M torch_cpu / M=1M torch_cuda
missing across all 3 seeds).

FIX 1 -- Shared W per M (build W ONCE per M value, reuse across all 3 backends).

v1 built W independently for each (M, backend) arm -> 3x M build cost per
seed. Since W is deterministic per (M, seed) and the 3 backends only differ
in the query operator (numpy sign/dot vs torch sign/dot), we can build W
once as numpy and convert to torch tensors for the torch arms. Same
per-query op measurement; ~50% wall reduction.

  Measured savings (from v1 heartbeat.jsonl):
    v1 seed_7 build cost: 3*(98 + 461 + 922) = 4443s  (all 9 builds)
    v2 predicted:         98 + 461 + 922 = 1481s     (3 builds shared)
    Savings: ~2960s per seed (49 min). Total wall predicted ~1900s.

FIX 2 -- Per-arm incremental checkpoint (never lose completed arms).

After EACH arm completes, append the arm-record to _arm_results.jsonl AND
rewrite metrics.json atomically with all arms-so-far. If timeout hits
mid-run, metrics.json reflects everything completed up to that point
(verdict = "SALVAGE_PARTIAL" while incomplete; final verdict computed only
when all 9 arms have landed). Runner-timeout kill loses at most 1 in-flight
arm instead of ALL arms.

Both fixes preserve v1's mechanism (identical query op, identical hash-
based arms_differ discipline, identical HP/HF gates); only orchestration
changes.

MECHANISM (identical to v1 / v2c dual-readout / cleanup_latency v1):
  W          = sum_i outer(vals_i, keys_i) / N          (N x N accumulator)
  out_bip    = sign(q @ W.T)                            (raw output; +/-1)
  cleanup    = (target_cos(out_n, target_val_n) > random_probe_cos)
               AND (target_cos > 0.05)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke gate (META_RULE_AF; SHA256 hash of timings)
- final_metrics_atomicity = tmp_replace (META_RULE_AH; PER ARM, not just final)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: latency measurement; noise floor = perf_counter resolution (~ns)
- discriminator survives scale: smoke includes M=100k preview arm at FULL N
- HARD_PASS strictly above floor; requires >=3 evaluable HP gates
- cardinality_ok: EXPECTED_N_UNITS declared per run_mode
- per-unit failure_class instrumentation (no bare except)
- calibration_check = default_ok_for_this_regime
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
- progress_logging = print_flush_true
- baseline_in_band: N/A (latency measurement not accuracy)
- cell_chunked = true (3 single-seed cells)

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
BACKENDS_FULL = ["numpy", "torch_cpu", "torch_cuda"]
N_QUERIES_FULL = 1000
WARMUP_QUERIES_FULL = 100

# Smoke config: FULL N=8192 kept (discriminator-must-survive-scale pattern A);
# reduce M sweep + query count. Smoke MUST fire at commercial regime M=100k so
# result is diagnostic of actual behavior, not toy-M.
N_DIM_SMOKE = 8192
M_SWEEP_SMOKE = [100_000]                    # single commercial M
BACKENDS_SMOKE = ["numpy", "torch_cpu"]      # torch_cuda handled via preview
N_QUERIES_SMOKE = 50
WARMUP_QUERIES_SMOKE = 10

# Preview arm (Discriminator-must-survive-scale pattern C):
# a torch_cuda arm at M=100k -- confirms GPU pathway if CUDA available on runner.
PREVIEW_ARM_M = 100_000
PREVIEW_ARM_BACKEND = "torch_cuda"
PREVIEW_ARM_QUERIES = 50

# Streaming chunk for W accumulation (never materialize >CHUNK_M rows at once)
CHUNK_M_NUMPY = 4096

# HP thresholds (policy targets; all HYPOTHESIZED@this_module + refined from
# v1 heartbeat salvage 2026-07-02)
HP_M1M_CUDA_P50_S = 0.100           # 100ms at (M=1M, backend=torch_cuda)
HP_M100K_CUDA_P50_S = 0.010         # 10ms at (M=100k, backend=torch_cuda)
HP_TAIL_RATIO_MAX = 3.0             # p99/p50 < 3.0 everywhere
HP_NUMPY_M_RATIO_MIN = 0.5          # numpy p50 M-invariance (op is O(N^2))
HP_NUMPY_M_RATIO_MAX = 5.0          # allow cache effects
HP_CUDA_SPEEDUP_MAX = 0.5           # torch_cuda p50 < 0.5 * numpy p50 at M=1M

# HF thresholds
HF_M1M_P50_S = 1.0                  # any backend > 1s at M=1M = commercial-blown
HF_TAIL_RATIO_MAX = 100.0           # p99/p50 > 100 = pathological

# Verdict roll-up
HP_HARD_PASS_MIN_DENOM = 3


# ---------------------------------------------------------------------------
# Mechanism helpers (build W once; reuse across backends)
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
# Cleanup query ops per backend (identical to v1)
# ---------------------------------------------------------------------------
def cleanup_query_numpy(q: np.ndarray, W: np.ndarray,
                        target_val_n: np.ndarray,
                        probe_n: np.ndarray) -> Tuple[bool, float]:
    out = q.astype(np.float32) @ W.T
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
# Per-M W-build (shared across backends within one M value)
# ---------------------------------------------------------------------------
def build_shared_W_for_M(seed: int, m_items: int, n_dim: int,
                         n_queries: int, log_prefix: str = "") -> Dict:
    """Build W + query targets ONCE for a given M; return dict of numpy arrays
    that all 3 backends will consume."""
    t0 = time.time()
    rng = np.random.RandomState(int(seed) + int(m_items // 1000) * 1009)
    query_targets = rng.choice(m_items, size=n_queries, replace=True)
    W_np, target_keys_raw, target_vals_raw = _stream_build_W_and_targets_numpy(
        rng, m_items, n_dim, query_targets, chunk_m=CHUNK_M_NUMPY,
    )
    tv_norm = target_vals_raw / np.linalg.norm(
        target_vals_raw, axis=1, keepdims=True).clip(min=1e-12)
    probe_rng = np.random.RandomState(999983)
    probes = probe_rng.choice([-1.0, 1.0],
                              size=target_keys_raw.shape).astype(np.float64)
    probes_n = probes / np.linalg.norm(
        probes, axis=1, keepdims=True).clip(min=1e-12)
    build_s = time.time() - t0
    print(f"{log_prefix}[W-build M={m_items} N={n_dim} n_q={n_queries}] "
          f"done in {build_s:.2f}s (shared across backends)", flush=True)
    return {
        "W": W_np,
        "targets_normalized": tv_norm,
        "probes_normalized": probes_n,
        "queries": target_keys_raw,
        "build_s": build_s,
    }


# ---------------------------------------------------------------------------
# Per-arm latency runner (consumes shared W bundle)
# ---------------------------------------------------------------------------
def run_arm_with_shared_W(
    arm_name: str, m_items: int, n_dim: int, backend: str,
    shared_W: Dict, n_queries: int, warmup_queries: int,
    out_dir: Path, log_prefix: str = "",
) -> Dict:
    """Run one latency arm consuming pre-built shared W. Return per-query
    timings + summary percentiles."""
    t0 = time.time()
    try:
        if backend == "torch_cpu" and not _TORCH_AVAILABLE:
            raise RuntimeError("torch not available; cannot run torch_cpu arm")
        if backend == "torch_cuda" and not _TORCH_CUDA_AVAILABLE:
            raise RuntimeError("torch.cuda not available; cannot run torch_cuda arm")

        W_np = shared_W["W"]
        tv_norm = shared_W["targets_normalized"]
        probes_n = shared_W["probes_normalized"]
        queries_raw = shared_W["queries"]

        # Backend-specific setup (build_s is the SHARED build; not double-counted)
        if backend == "numpy":
            W_bk = W_np
            query_op = cleanup_query_numpy
            targets_bk = tv_norm
            probes_bk = probes_n
            queries_bk = queries_raw
        elif backend == "torch_cpu":
            W_bk = torch.from_numpy(W_np)
            targets_bk = torch.from_numpy(tv_norm)
            probes_bk = torch.from_numpy(probes_n)
            queries_bk = torch.from_numpy(queries_raw)
            query_op = cleanup_query_torch_cpu
        elif backend == "torch_cuda":
            W_bk = torch.from_numpy(W_np).cuda()
            targets_bk = torch.from_numpy(tv_norm).cuda()
            probes_bk = torch.from_numpy(probes_n).cuda()
            queries_bk = torch.from_numpy(queries_raw).cuda()
            query_op = cleanup_query_torch_cuda
            torch.cuda.synchronize()
        else:
            raise ValueError(f"unknown backend {backend!r}")

        print(f"{log_prefix}[arm={arm_name}] setup done backend={backend} "
              f"M={m_items} N={n_dim} n_q={n_queries}", flush=True)

        # Warmup (not recorded)
        for i in range(min(warmup_queries, n_queries)):
            q = queries_bk[i]
            _ = query_op(q, W_bk, targets_bk[i], probes_bk[i])

        # Measured loop
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
            [timings, [float(m_items), float(n_dim),
                       float(hash(backend) % 10007)]]
        ).tobytes()
        timings_hash = hashlib.sha256(h_input).hexdigest()[:16]

        wall = time.time() - t0
        emit_heartbeat(out_dir, unit_idx=0, elapsed_s=wall,
                       extra={"arm": arm_name, "M": m_items, "N": n_dim,
                              "backend": backend,
                              "p50_us": p50 * 1e6, "p99_us": p99 * 1e6,
                              "cleanup_recall": cleanup_recall,
                              "build_s_shared": shared_W["build_s"]})
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
            "build_s_shared": float(shared_W["build_s"]),
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
        msg = str(exc)[:200]
        is_unavailable = ("not available" in msg)
        arm_status = "UNAVAILABLE" if is_unavailable else "FAILED"
        print(f"{log_prefix}[arm={arm_name}] {arm_status} {fc}: {msg}",
              flush=True)
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
            "build_s_shared": float(shared_W.get("build_s", 0.0)),
            "arm_status": arm_status,
            "failure_class": fc if not is_unavailable else None,
            "traceback": (traceback.format_exc()[:2000]
                          if not is_unavailable else ""),
        }


# ---------------------------------------------------------------------------
# Verdict logic (unchanged from v1 modulo band-floor gate + partial support)
# ---------------------------------------------------------------------------
def _get_arm(per_arm: List[Dict], M: int, backend: str) -> Optional[Dict]:
    for a in per_arm:
        if (a["arm_status"] == "OK" and a["M"] == M
                and a["backend"] == backend):
            return a
    return None


def compute_verdict(per_arm: List[Dict], expected_n_units: int,
                    run_mode: str, is_partial: bool = False) -> Dict:
    """Verdict per pre-reg HP/HF gates.

    is_partial=True skips cardinality HF gate (partial writes during a run
    have fewer arms than expected but that's not a breach).
    """
    v: Dict = {"gates": {}, "is_partial": bool(is_partial)}
    v["n_arms"] = len(per_arm)
    v["expected_n_units"] = expected_n_units

    if not is_partial and len(per_arm) < expected_n_units:
        v["gates"]["HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"] = True
        v["verdict"] = "HARD_FAIL"
        v["verdict_msg"] = (
            f"CARDINALITY_BREACH: expected {expected_n_units} arms; "
            f"got {len(per_arm)}"
        )
        return v

    # arms_differ (META_RULE_AF): non-empty hashes must be unique
    hashes = [a["timings_hash"] for a in per_arm if a["timings_hash"]]
    dup_map: Dict[str, List[int]] = {}
    for i, h in enumerate(hashes):
        dup_map.setdefault(h, []).append(i)
    dups = {h: idxs for h, idxs in dup_map.items() if len(idxs) > 1}
    v["arms_differ_verified"] = (len(dups) == 0)
    v["duplicated_hashes"] = list(dups.keys())
    if dups:
        v["gates"]["HARD_FAIL_META_RULE_AF_BIT_IDENTICAL"] = True

    v["arm_status_summary"] = {}
    for a in per_arm:
        key = f"{a['backend']}_M{a['M']}"
        v["arm_status_summary"][key] = a["arm_status"]

    ok_arms = [a for a in per_arm if a["arm_status"] == "OK"]
    v["n_ok_arms"] = len(ok_arms)

    # HP_TAIL_CONTROLLED
    tail_ratios = [a["p99_s"] / a["p50_s"] for a in ok_arms if a["p50_s"] > 0]
    v["max_p99_over_p50"] = max(tail_ratios) if tail_ratios else float("nan")
    if tail_ratios:
        v["gates"]["HP_TAIL_CONTROLLED"] = all(
            r < HP_TAIL_RATIO_MAX for r in tail_ratios
        )
        v["gates"]["HF_TAIL_EXPLOSION"] = any(
            r > HF_TAIL_RATIO_MAX for r in tail_ratios
        )
    else:
        v["gates"]["HP_TAIL_CONTROLLED"] = False
        v["gates"]["HF_TAIL_EXPLOSION"] = False

    # HP_M1M_UNDER_100MS (torch_cuda at M=1M) -- LOAD-BEARING M3 SLA gate
    cuda_1m = _get_arm(per_arm, 1_000_000, "torch_cuda")
    if cuda_1m is None:
        v["gates"]["HP_M1M_UNDER_100MS"] = "n/a"
    else:
        v["p50_cuda_M1M"] = cuda_1m["p50_s"]
        v["gates"]["HP_M1M_UNDER_100MS"] = (cuda_1m["p50_s"] < HP_M1M_CUDA_P50_S)

    # HP_M100K_UNDER_10MS (torch_cuda at M=100k)
    cuda_100k = _get_arm(per_arm, 100_000, "torch_cuda")
    if cuda_100k is None:
        v["gates"]["HP_M100K_UNDER_10MS"] = "n/a"
    else:
        v["p50_cuda_M100K"] = cuda_100k["p50_s"]
        v["gates"]["HP_M100K_UNDER_10MS"] = (
            cuda_100k["p50_s"] < HP_M100K_CUDA_P50_S
        )

    # HP_NUMPY_SCALES_INVARIANT
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

    # HP_CUDA_SPEEDUP (torch_cuda beats numpy at M=1M)
    if (cuda_1m is None or numpy_1m is None or numpy_1m["p50_s"] <= 0):
        v["gates"]["HP_CUDA_SPEEDUP"] = "n/a"
    else:
        speedup_ratio = cuda_1m["p50_s"] / numpy_1m["p50_s"]
        v["cuda_over_numpy_p50_ratio_at_M1M"] = speedup_ratio
        v["gates"]["HP_CUDA_SPEEDUP"] = (speedup_ratio < HP_CUDA_SPEEDUP_MAX)

    # HF_M1M_INFEASIBLE
    m1m_arms_ok = [a for a in per_arm
                   if a["arm_status"] == "OK" and a["M"] == 1_000_000]
    v["p50_all_backends_M1M"] = {a["backend"]: a["p50_s"] for a in m1m_arms_ok}
    if m1m_arms_ok:
        v["gates"]["HF_M1M_INFEASIBLE"] = any(
            a["p50_s"] > HF_M1M_P50_S for a in m1m_arms_ok
        )
    else:
        v["gates"]["HF_M1M_INFEASIBLE"] = False

    v["min_p50_across_ok_arms_s"] = min(
        (a["p50_s"] for a in ok_arms), default=float("nan"),
    )
    v["gates"]["MEASUREMENT_REAL"] = any(
        a["p50_s"] > 10e-6 for a in ok_arms
    )

    # HP roll-up
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

    if is_partial:
        v["verdict"] = "SALVAGE_PARTIAL"
        v["verdict_msg"] = (
            f"partial: {len(per_arm)}/{expected_n_units} arms; "
            f"hp_fired={hp_true}/{hp_denom}"
        )
        return v

    if hf_true > 0:
        v["verdict"] = "HARD_FAIL"
        v["verdict_msg"] = f"HF fired: {hf_true} (see gates)"
    elif hp_denom == 0:
        v["verdict"] = "MIDDLE_BAND"
        v["verdict_msg"] = "no HP gate evaluable at this config (denom=0)"
    elif hp_denom < HP_HARD_PASS_MIN_DENOM:
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
# Arm plan (M-major, backend-minor -- enables W-sharing within M)
# ---------------------------------------------------------------------------
def build_arm_plan(run_mode: str) -> List[Dict]:
    plan: List[Dict] = []
    if run_mode == "smoke":
        n_dim = N_DIM_SMOKE
        m_sweep = M_SWEEP_SMOKE
        n_q = N_QUERIES_SMOKE
        warmup = WARMUP_QUERIES_SMOKE
        for M in m_sweep:
            for backend in BACKENDS_SMOKE:
                plan.append({
                    "arm_name": f"MAIN_M{M}_backend_{backend}",
                    "M": M, "N": n_dim,
                    "backend": backend,
                    "n_queries": n_q, "warmup": warmup,
                })
        # Preview CUDA arm at commercial M (same M as MAIN so it reuses shared W)
        plan.append({
            "arm_name": f"PREVIEW_M{PREVIEW_ARM_M}_backend_{PREVIEW_ARM_BACKEND}",
            "M": PREVIEW_ARM_M, "N": n_dim,
            "backend": PREVIEW_ARM_BACKEND,
            "n_queries": PREVIEW_ARM_QUERIES, "warmup": WARMUP_QUERIES_SMOKE,
        })
    else:
        n_dim = N_DIM_FULL
        m_sweep = M_SWEEP_FULL
        n_q = N_QUERIES_FULL
        warmup = WARMUP_QUERIES_FULL
        for M in m_sweep:
            for backend in BACKENDS_FULL:
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
# Incremental metrics writer (FIX 2 -- per-arm checkpoint)
# ---------------------------------------------------------------------------
def _write_incremental_metrics(
    out_dir: Path, seed: int, anchor_name: str, run_mode: str,
    per_arm_so_far: List[Dict], expected: int, t_start: float,
    is_partial: bool,
) -> None:
    """Atomically write metrics.json reflecting all arms completed so far.
    Called after EACH arm completes so a timeout kill preserves data."""
    verdict = compute_verdict(per_arm_so_far, expected_n_units=expected,
                              run_mode=run_mode, is_partial=is_partial)
    total_wall = time.time() - t_start
    metrics = {
        "verdict": verdict["verdict"],
        "verdict_msg": verdict["verdict_msg"],
        "summary": (f"stage2_commercial_M_latency_percentiles_v2 seed_{seed} "
                    f"{run_mode} arms={len(per_arm_so_far)}/{expected} "
                    f"hp_fired={verdict['hp_fired']}/{verdict['hp_denominator']} "
                    f"hf_fired={verdict['hf_fired']}"
                    f"{' (PARTIAL)' if is_partial else ''}"),
        "elapsed_s": float(total_wall),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "run_mode": run_mode,
        "anchor_name": anchor_name,
        "seed": int(seed),
        "n_arms": len(per_arm_so_far),
        "expected_n_units": expected,
        "verdict_detail": verdict,
        "per_arm": per_arm_so_far,
        "torch_available": _TORCH_AVAILABLE,
        "torch_cuda_available": _TORCH_CUDA_AVAILABLE,
        "cell_version": "v2_timeout_fixed",
        "checkpoint_kind": ("per_arm_incremental" if is_partial
                            else "final_complete"),
    }
    tmp = Path(out_dir) / "metrics.json.tmp"
    final = Path(out_dir) / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(str(tmp), str(final))


def _append_arm_result(out_dir: Path, arm_record: Dict) -> None:
    """Append arm record to _arm_results.jsonl (audit trail)."""
    p = Path(out_dir) / "_arm_results.jsonl"
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(arm_record) + "\n")


# ---------------------------------------------------------------------------
# Main driver -- M-major loop with shared-W and per-arm checkpoint
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

    # Group plan by M (preserves order) so we build W once per M and iterate
    # backends within.
    per_M_backends: Dict[int, List[Dict]] = {}
    per_M_order: List[int] = []
    for entry in plan:
        M = entry["M"]
        if M not in per_M_backends:
            per_M_backends[M] = []
            per_M_order.append(M)
        per_M_backends[M].append(entry)

    per_arm: List[Dict] = []
    arm_global_idx = 0
    for M_idx, M in enumerate(per_M_order):
        entries_for_M = per_M_backends[M]
        # All backends share the same (N, n_queries) config? Take n_q from first
        # entry (smoke may have PREVIEW arm with different n_queries; if so we
        # use max n_queries so the shared queries buffer covers all backends).
        n_dim = entries_for_M[0]["N"]
        n_q_shared = max(e["n_queries"] for e in entries_for_M)

        emit_heartbeat(str(output_dir), unit_idx=arm_global_idx,
                       elapsed_s=time.time() - t_start,
                       total_units=len(plan),
                       extra={"phase": "W_build_start", "M": M,
                              "backends_upcoming": [e["backend"]
                                                    for e in entries_for_M]})
        shared_W = build_shared_W_for_M(
            seed=seed, m_items=M, n_dim=n_dim, n_queries=n_q_shared,
            log_prefix=f"[M {M_idx+1}/{len(per_M_order)}] ",
        )

        for entry in entries_for_M:
            emit_heartbeat(str(output_dir), unit_idx=arm_global_idx,
                           elapsed_s=time.time() - t_start,
                           total_units=len(plan),
                           extra={"phase": "arm_start",
                                  "arm": entry["arm_name"]})
            # If the arm's n_queries < shared n_q, we still run the arm but only
            # measure entry["n_queries"] queries; the shared buffer has all n_q
            # ready.
            res = run_arm_with_shared_W(
                arm_name=entry["arm_name"],
                m_items=entry["M"],
                n_dim=entry["N"],
                backend=entry["backend"],
                shared_W=shared_W,
                n_queries=entry["n_queries"],
                warmup_queries=entry["warmup"],
                out_dir=Path(output_dir),
                log_prefix=f"[{arm_global_idx+1}/{len(plan)}] ",
            )
            per_arm.append(res)
            _append_arm_result(Path(output_dir), res)
            # FIX 2: write PARTIAL metrics.json after every arm.
            _write_incremental_metrics(
                out_dir=Path(output_dir), seed=seed, anchor_name=anchor_name,
                run_mode=run_mode, per_arm_so_far=per_arm,
                expected=expected, t_start=t_start,
                is_partial=(len(per_arm) < expected),
            )
            arm_global_idx += 1

        # Free shared_W (large; up to ~256 MB W + query buffers) before next M
        del shared_W

    # Final metrics: rewrite with is_partial=False (triggers verdict roll-up)
    _write_incremental_metrics(
        out_dir=Path(output_dir), seed=seed, anchor_name=anchor_name,
        run_mode=run_mode, per_arm_so_far=per_arm,
        expected=expected, t_start=t_start,
        is_partial=False,
    )
    total_wall = time.time() - t_start
    final_verdict = compute_verdict(
        per_arm, expected_n_units=expected, run_mode=run_mode, is_partial=False,
    )
    print(f"[main] DONE verdict={final_verdict['verdict']} "
          f"msg='{final_verdict['verdict_msg']}' "
          f"total_wall={total_wall:.2f}s", flush=True)
    return 0
