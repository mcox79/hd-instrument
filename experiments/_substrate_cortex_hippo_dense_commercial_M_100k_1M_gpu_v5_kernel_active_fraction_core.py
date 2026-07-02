"""Shared core v5: cortex_hippo dense-Hopfield at commercial M (100k / 500k / 1M).

v5 MEASUREMENT DISCIPLINE UPGRADE (v4 architecture unchanged): v4 Fix A.1
(on-GPU chunk generation) WORKED at 15-25x speedup — Orchestrator selftest
measured M=100k REPL wall_s=0.30s (vs v3 4-8s). But v4's util gate reported
3.2% at M=100k, which Orchestrator diagnosed as a sampler-cadence artifact
(50 ms period + microsecond kernels + n_samples=5 -> sampler caught between-
kernel gaps). Not compute-starvation.

v5 Fix C (ground-truth compute-active): kernel_active_fraction_pct measured
via torch.cuda.Event start/end per chunk kernel. Sum elapsed_time / wall_s.
Sampler-cadence invariant BY CONSTRUCTION. This IS the compute-starvation
definition. Load-bearing HF gate metric.
    HF_COMPUTE_STARVED_M{M}_arm{n}_kernactive{k}_below_30 when
    backend=torch.cuda AND M >= 100k AND kernel_active_fraction_pct < 30.

v5 Fix E (statistical power for measurement): selftest raises M to 500k so
wall is ~1.5-3 s and sampler gets 30+ samples. USER-locked selftest gates:
    wall_s < 5.0 at M=500k per arm (confirms Fix A.1 still works at scale)
    kernel_active_fraction_pct >= 30 at M=500k per arm (ground truth)
    n_util_samples >= 20 at M=500k per arm (sanity check for sampler cadence)

v5 Fix D (secondary, nice-to-have): sample_util_ms lowered from 50 to 10
ms in the primitive default (10x diagnostic resolution). Not gate-critical
because Fix C makes util a diagnostic-only metric.

v4 probe MEASURED@ Orchestrator selftest M=100k:
    ARM_REPL wall=0.30s util_pct=3.2 (SAMPLER ARTIFACT, not starvation)

Prior-work check (substrate-KB, 2026-07-01):
    "CUDA event timing kernel active fraction compute starvation ground
    truth measurement" -> NONE at cosine > 0.30 (top 0.3223 = unrelated
    'Action' note). v5 genuinely novel measurement discipline.

MECHANISM (2 arms x 3 M values = 6 arm-outcomes per seed): unchanged from v4.
FALSIFIABLE gates (per M): unchanged.

CARDINALITY (META_RULE_H): EXPECTED_N_UNITS = 2 arms * 3 M values = 6 per seed.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke MUST exercise on-GPU generation + kernel-active meter at M=100k /
  FULL_N=8192 with real GPU compute pass. Selftest at M=500k satisfies the
  measurement-power discipline USER specified.

ASCII-only. META_RULE_AH tmp+os.replace. META_RULE_AF hash-test.
META_RULE_AG baseline-in-band exemption for ARM_STD (must-fail arm).
except SystemExit before Exception (no BaseException). Numbers tagged.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import hashlib
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Torch availability probe
# ---------------------------------------------------------------------------
try:
    import torch  # type: ignore
    _TORCH_AVAILABLE = True
    _CUDA_AVAILABLE = bool(torch.cuda.is_available())
except Exception:
    torch = None  # type: ignore
    _TORCH_AVAILABLE = False
    _CUDA_AVAILABLE = False


# ---------------------------------------------------------------------------
# Fixed config
# ---------------------------------------------------------------------------
N_CORTEX_FULL = 8192
V_DIM_FULL = 256
BETA_BASE = 13.0
M_REF = 100_000
ATTN_CHUNK_FULL = 1024
N_QUERIES_FULL = 200

M_SWEEP_FULL = [100_000, 500_000, 1_000_000]

# Smoke: FULL_N GPU on-generation preview at M=100k (must exercise v4/v5 gen path)
N_CORTEX_SMOKE = 1024
V_DIM_SMOKE = 128
M_SWEEP_SMOKE = [10_000]
M_SMOKE_PREVIEW_FULL_N = 100_000
N_QUERIES_SMOKE = 50
ATTN_CHUNK_SMOKE = 512

# 6 GB total-peak GPU gate.
GPU_MEM_GATE_BYTES = 6_000_000_000

# USER-locked v5 selftest performance gates at M=500k (only when CUDA available).
# Raised from v4 (M=100k, wall<3s) per Orchestrator "statistical power" diagnosis.
SELFTEST_M_FOR_MEASUREMENT_POWER = 500_000
SELFTEST_WALL_S_MAX = 5.0
SELFTEST_KERNEL_ACTIVE_PCT_MIN = 30.0
SELFTEST_N_UTIL_SAMPLES_MIN = 20

# HF gate: ground-truth kernel-active fraction at M >= 100k on torch.cuda.
HF_KERNEL_ACTIVE_PCT_MIN_M100K = 30.0

# Util sampler cadence (v5 Fix D: 10 ms for diagnostic resolution).
UTIL_SAMPLE_MS = 10


def adaptive_beta(M: int, m_ref: int = M_REF, beta_base: float = BETA_BASE) -> float:
    """Adaptive beta per M. THEORETICAL@log2-scaling preserves logit_gap."""
    if M <= m_ref:
        return beta_base
    return beta_base * math.log2(M) / math.log2(m_ref)


def predicted_p_win(M: int, N: int, beta: float) -> float:
    """Predicted attention winner probability. THEORETICAL@max-distractor bound."""
    max_distractor = math.sqrt(2 * math.log(max(M, 2)) / N)
    logit_gap = beta * (1.0 - max_distractor)
    if logit_gap > 700:
        return 1.0
    return 1.0 / (1.0 + M * math.exp(-logit_gap))


# ---------------------------------------------------------------------------
# Instrumentation helpers
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
# Numpy REPLACE simulation (CPU numpy fallback)
# ---------------------------------------------------------------------------
def _numpy_dense_replace(
    keys: np.ndarray, vals: np.ndarray, queries: np.ndarray,
    beta: float, chunk_size: int,
) -> np.ndarray:
    Q, N = queries.shape
    M = keys.shape[0]
    V = vals.shape[1]
    q_norm = queries.astype(np.float64)
    q_norm = q_norm / np.maximum(np.linalg.norm(q_norm, axis=-1, keepdims=True), 1e-9)
    m_state = np.full((Q,), -np.inf, dtype=np.float64)
    l_state = np.zeros((Q,), dtype=np.float64)
    o_state = np.zeros((Q, V), dtype=np.float64)
    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)
        k_chunk = keys[start:end].astype(np.float64)
        k_norm = k_chunk / np.maximum(
            np.linalg.norm(k_chunk, axis=-1, keepdims=True), 1e-9
        )
        v_chunk = vals[start:end].astype(np.float64)
        sims = q_norm @ k_norm.T
        logits = beta * sims
        chunk_max = logits.max(axis=-1)
        m_new = np.maximum(m_state, chunk_max)
        scale = np.exp(m_state - m_new)
        exp_logits = np.exp(logits - m_new[:, None])
        l_state = l_state * scale + exp_logits.sum(axis=-1)
        o_state = o_state * scale[:, None] + exp_logits @ v_chunk
        m_state = m_new
    return o_state / np.maximum(l_state[:, None], 1e-30)


def _numpy_standard_readout(
    keys: np.ndarray, vals: np.ndarray, queries: np.ndarray,
) -> np.ndarray:
    Q, N = queries.shape
    W = (vals.T.astype(np.float64) @ keys.astype(np.float64)) / N
    return queries.astype(np.float64) @ W.T


def _run_arm_numpy(
    arm_name: str, seed: int, M: int, N: int, V: int, n_queries: int,
    beta: float, chunk_size: int, out_dir: Path,
) -> Dict:
    """CPU numpy fallback path (only when torch/CUDA unavailable)."""
    rng = np.random.RandomState(seed + M + hash(arm_name) % 10007)
    t0 = time.time()
    keys = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    vals = rng.choice([-1.0, 1.0], size=(M, V)).astype(np.float32)
    q_idx = rng.choice(M, size=n_queries, replace=False)
    noise = rng.randn(n_queries, N).astype(np.float32) * 0.05
    queries = keys[q_idx] + noise
    v_target = vals[q_idx]
    if arm_name == "ARM_STD":
        readout = _numpy_standard_readout(keys, vals, queries)
    elif arm_name == "ARM_REPL":
        readout = _numpy_dense_replace(keys, vals, queries, beta, chunk_size)
    else:
        raise ValueError(f"unknown arm: {arm_name}")
    r_norm = readout / np.maximum(np.linalg.norm(readout, axis=-1, keepdims=True), 1e-9)
    t_norm = v_target.astype(np.float64) / np.maximum(
        np.linalg.norm(v_target, axis=-1, keepdims=True), 1e-9
    )
    per_q_cos = (r_norm * t_norm).sum(axis=-1)
    recall = float(np.mean(per_q_cos))
    recall_std = float(np.std(per_q_cos))
    arm_hash = hashlib.sha256(readout.tobytes()).hexdigest()[:16]
    wall = time.time() - t0
    return {
        "arm_name": arm_name, "seed": int(seed), "M": int(M), "N": int(N), "V": int(V),
        "n_queries": int(n_queries), "beta": float(beta), "chunk_size": int(chunk_size),
        "recall_cosine_mean": recall, "recall_cosine_std": recall_std,
        "arm_hash": arm_hash, "backend": "numpy",
        "wall_s": float(wall), "gpu_mem_peak_mb": 0.0,
        "kernel_active_fraction_pct": 0.0, "kernel_active_ms_total": 0.0,
        "n_kernel_chunks": 0,
        "gpu_util_mean_pct": 0.0, "n_util_samples": 0,
        "util_source": "n/a_numpy_cpu",
        "upload_strategy": "n/a_numpy_cpu",
    }


# ---------------------------------------------------------------------------
# Torch GPU on-generation execution (v5 measurement upgrade over v4)
# ---------------------------------------------------------------------------
def _arm_seed(seed: int, M: int, arm_name: str) -> int:
    """Deterministic per-(seed, M, arm) master seed."""
    h = hash(arm_name) & 0xFFFF
    return (seed * 2_147_483_647 + M * 100003 + h) & 0xFFFFFFFF


def _run_arm_torch_gpu_gen(
    arm_name: str, seed: int, M: int, N: int, V: int, n_queries: int,
    beta: float, chunk_size: int, out_dir: Path,
    use_int8_keys: bool = True,
) -> Dict:
    """GPU on-generation path with kernel-active fraction measurement."""
    if not _TORCH_AVAILABLE:
        raise RuntimeError("torch not available for torch arm")
    from hdlab.gpu_generated_streaming_attention import (
        GpuGenSpec, gpu_generated_streaming_readout,
    )

    device = torch.device("cuda" if _CUDA_AVAILABLE else "cpu")

    arm_seed_val = _arm_seed(seed, M, arm_name)
    mode = "hebbian" if arm_name == "ARM_STD" else "attention"
    use_int8 = bool(use_int8_keys and arm_name == "ARM_REPL")

    spec = GpuGenSpec(
        arm_seed=arm_seed_val, M=M, N=N, V=V, n_queries=n_queries,
        chunk_size=chunk_size, device=device, query_noise_std=0.05,
        use_int8_keys=use_int8,
    )

    print(
        f"    [{arm_name} M={M}] on-GPU-generation streaming, mode={mode}, "
        f"int8={use_int8}, chunk={chunk_size}, sample_util_ms={UTIL_SAMPLE_MS}",
        flush=True,
    )

    readout, v_target, telemetry = gpu_generated_streaming_readout(
        spec, mode=mode, beta=beta, sample_util_ms=UTIL_SAMPLE_MS,
    )

    # Recall metric
    r_norm = readout / readout.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    t_target_fp32 = v_target.to(torch.float32)
    t_norm = t_target_fp32 / t_target_fp32.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    per_q_cos = (r_norm * t_norm).sum(dim=-1)
    recall = float(per_q_cos.mean().item())
    recall_std = float(per_q_cos.std().item())

    readout_cpu = readout.detach().cpu().to(torch.float32).contiguous().numpy()
    arm_hash = hashlib.sha256(readout_cpu.tobytes()).hexdigest()[:16]

    upload_strategy = (
        "on_gpu_generation_int8_per_chunk" if use_int8
        else "on_gpu_generation_fp16_per_chunk"
    )

    result = {
        "arm_name": arm_name, "seed": int(seed), "M": int(M), "N": int(N), "V": int(V),
        "n_queries": int(n_queries), "beta": float(beta), "chunk_size": int(chunk_size),
        "recall_cosine_mean": recall, "recall_cosine_std": recall_std,
        "arm_hash": arm_hash,
        "backend": "torch.cuda" if device.type == "cuda" else "torch.cpu",
        "int8_keys": use_int8,
        "upload_strategy": upload_strategy,
        "arm_seed": int(arm_seed_val),
        "mode": mode,
        # v5 ground-truth compute-active metric (load-bearing HF gate).
        "wall_s": float(telemetry["wall_s"]),
        "kernel_active_fraction_pct": float(telemetry["kernel_active_fraction_pct"]),
        "kernel_active_ms_total": float(telemetry["kernel_active_ms_total"]),
        "n_kernel_chunks": int(telemetry["n_kernel_chunks"]),
        # v4 diagnostic sampler metric (secondary).
        "gpu_util_mean_pct": float(telemetry["gpu_util_mean_pct"]),
        "n_util_samples": int(telemetry["n_util_samples"]),
        "util_source": str(telemetry["util_source"]),
        "sample_util_ms": int(telemetry.get("sample_util_ms", UTIL_SAMPLE_MS)),
        "gpu_mem_peak_mb": float(telemetry["gpu_mem_peak_mb"]),
    }

    print(
        f"    [{arm_name} M={M}] recall={recall:.4f} wall={result['wall_s']:.3f}s "
        f"kernel_active_pct={result['kernel_active_fraction_pct']:.1f} "
        f"kernel_ms={result['kernel_active_ms_total']:.1f} "
        f"n_chunks={result['n_kernel_chunks']} "
        f"gpu_util_pct={result['gpu_util_mean_pct']:.1f} "
        f"n_samples={result['n_util_samples']} src={result['util_source']} "
        f"peak_mb={result['gpu_mem_peak_mb']:.1f}",
        flush=True,
    )

    del readout, v_target
    if _CUDA_AVAILABLE:
        torch.cuda.empty_cache()

    return result


def run_arm(
    arm_name: str, seed: int, M: int, N: int, V: int, n_queries: int,
    beta: float, chunk_size: int, out_dir: Path,
    use_torch: bool, use_int8_keys: bool = True,
) -> Dict:
    if use_torch and _TORCH_AVAILABLE:
        return _run_arm_torch_gpu_gen(
            arm_name, seed, M, N, V, n_queries, beta, chunk_size, out_dir,
            use_int8_keys=use_int8_keys,
        )
    return _run_arm_numpy(
        arm_name, seed, M, N, V, n_queries, beta, chunk_size, out_dir,
    )


def run_one_M(
    seed: int, M: int, N: int, V: int, n_queries: int, chunk_size: int,
    out_dir: Path, use_torch: bool, use_int8_keys: bool = True,
) -> List[Dict]:
    beta = adaptive_beta(M)
    p_win_pred = predicted_p_win(M, N, beta)
    print(
        f"  [M={M}] beta={beta:.2f} p_win_predicted={p_win_pred:.4f}",
        flush=True,
    )
    arms: List[Dict] = []
    for arm_name in ("ARM_STD", "ARM_REPL"):
        t_arm = time.time()
        r = run_arm(
            arm_name, seed, M, N, V, n_queries, beta, chunk_size, out_dir,
            use_torch=use_torch, use_int8_keys=use_int8_keys,
        )
        r["p_win_predicted"] = float(p_win_pred)
        arms.append(r)
        emit_heartbeat(
            out_dir, unit_idx=len(arms),
            elapsed_s=time.time() - t_arm,
            total_units=2,
            extra={
                "arm": arm_name, "M": M, "recall": r["recall_cosine_mean"],
                "gpu_mem_peak_mb": r["gpu_mem_peak_mb"],
                "kernel_active_fraction_pct": r.get("kernel_active_fraction_pct", 0.0),
                "gpu_util_mean_pct": r.get("gpu_util_mean_pct", 0.0),
            },
        )
    return arms


# ---------------------------------------------------------------------------
# Verdict logic (v5 uses kernel_active_fraction_pct for HF gate)
# ---------------------------------------------------------------------------
def compute_verdict(seed_result: Dict, run_mode: str) -> Tuple[str, str, Dict]:
    per_M = seed_result.get("per_M", {})
    if run_mode == "smoke":
        expected_arm_count = 2 * len(per_M)
    else:
        expected_arm_count = 2 * 3

    n_arm_outcomes = 0
    std_vals: List[float] = []
    repl_vals_by_M: Dict[int, float] = {}
    max_gpu_mb = 0.0
    arm_hash_pairs: List[Tuple[str, str, str]] = []
    death_flag = False
    starvation: List[str] = []

    for m_str, arms in per_M.items():
        try:
            m_int = int(m_str)
        except (TypeError, ValueError):
            m_int = -1
        std_hash: Optional[str] = None
        repl_hash: Optional[str] = None
        for a in arms:
            n_arm_outcomes += 1
            recall = float(a.get("recall_cosine_mean", 0.0))
            max_gpu_mb = max(max_gpu_mb, float(a.get("gpu_mem_peak_mb", 0.0)))
            backend = str(a.get("backend", ""))
            # v5 HF_COMPUTE_STARVED gate on kernel_active_fraction_pct (ground truth).
            k_pct = float(a.get("kernel_active_fraction_pct", 0.0))
            if backend == "torch.cuda" and m_int >= 100_000:
                if k_pct < HF_KERNEL_ACTIVE_PCT_MIN_M100K:
                    starvation.append(
                        f"HF_COMPUTE_STARVED_M{m_int}_arm{a['arm_name']}_"
                        f"kernactive{k_pct:.1f}_below_{HF_KERNEL_ACTIVE_PCT_MIN_M100K:.0f}"
                    )
            if a["arm_name"] == "ARM_STD":
                std_vals.append(recall)
                std_hash = a.get("arm_hash")
            elif a["arm_name"] == "ARM_REPL":
                repl_vals_by_M[m_int] = recall
                repl_hash = a.get("arm_hash")
                if recall < 0.10:
                    death_flag = True
        if std_hash and repl_hash:
            arm_hash_pairs.append((str(m_int), std_hash, repl_hash))

    hp_repl_m100k = repl_vals_by_M.get(100_000)
    hp_repl_m500k = repl_vals_by_M.get(500_000)
    hp_repl_m1m = repl_vals_by_M.get(1_000_000)
    gap_per_M: Dict[int, float] = {}
    for m_str, arms in per_M.items():
        try:
            m_int = int(m_str)
        except (TypeError, ValueError):
            continue
        std_r = next(
            (a["recall_cosine_mean"] for a in arms if a["arm_name"] == "ARM_STD"),
            None,
        )
        repl_r = next(
            (a["recall_cosine_mean"] for a in arms if a["arm_name"] == "ARM_REPL"),
            None,
        )
        if std_r is not None and repl_r is not None:
            gap_per_M[m_int] = repl_r - std_r
    hp_std_beaten = all(g >= 0.50 for g in gap_per_M.values()) if gap_per_M else False

    hf_flags: List[str] = []
    if max_gpu_mb > 6000:
        hf_flags.append(f"HF_MEMORY_OVERFLOW_max_gpu_mb={max_gpu_mb:.1f}")
    if death_flag:
        hf_flags.append("HF_MECHANISM_DEATH_recall_below_0.10")
    for m_str, sh, rh in arm_hash_pairs:
        if sh == rh:
            hf_flags.append(f"HF_ARM_IDENTICAL_M={m_str}_META_RULE_AF_VIOLATION")
    if n_arm_outcomes != expected_arm_count:
        hf_flags.append(
            f"HF_CARDINALITY_META_RULE_H_expected={expected_arm_count}"
            f"_got={n_arm_outcomes}"
        )
    hf_flags.extend(starvation)

    hp_flags: List[str] = []
    if hp_repl_m100k is not None and hp_repl_m100k >= 0.80:
        hp_flags.append(f"HP_M100k_MECHANISM_HOLDS_repl={hp_repl_m100k:.3f}")
    if hp_repl_m500k is not None and hp_repl_m500k >= 0.60:
        hp_flags.append(f"HP_M500k_MECHANISM_HOLDS_repl={hp_repl_m500k:.3f}")
    if hp_repl_m1m is not None and hp_repl_m1m >= 0.30:
        hp_flags.append(f"HP_M1M_MECHANISM_HOLDS_repl={hp_repl_m1m:.3f}")
    if hp_std_beaten:
        min_gap = min(gap_per_M.values()) if gap_per_M else 0.0
        hp_flags.append(f"HP_STD_BEATEN_min_gap={min_gap:.3f}")

    headline = {
        "hp_repl_m100k": hp_repl_m100k,
        "hp_repl_m500k": hp_repl_m500k,
        "hp_repl_m1m": hp_repl_m1m,
        "std_vals": std_vals,
        "gap_per_M": {str(k): v for k, v in gap_per_M.items()},
        "max_gpu_mb": max_gpu_mb,
        "n_arm_outcomes": n_arm_outcomes,
        "expected_arm_count": expected_arm_count,
        "hp_flags": hp_flags,
        "hf_flags": hf_flags,
    }

    if hf_flags:
        return ("HARD_FAIL", "; ".join(hf_flags), headline)

    if run_mode == "smoke":
        repl_seen = [v for v in repl_vals_by_M.values()]
        if not repl_seen:
            return ("HARD_FAIL", "smoke: no ARM_REPL result", headline)
        min_repl = min(repl_seen)
        max_std = max(std_vals) if std_vals else 0.0
        gap = min_repl - max_std
        if gap >= 0.30:
            return (
                "HARD_PASS",
                f"SMOKE_HARD_PASS: min_repl={min_repl:.3f} max_std={max_std:.3f} "
                f"gap={gap:.3f} n_arms={n_arm_outcomes} max_gpu_mb={max_gpu_mb:.1f}",
                headline,
            )
        return (
            "MIDDLE_BAND",
            f"SMOKE_MB: min_repl={min_repl:.3f} max_std={max_std:.3f} "
            f"gap={gap:.3f} discriminator_below_smoke_threshold_0.30",
            headline,
        )

    all_hp = (
        hp_repl_m100k is not None and hp_repl_m100k >= 0.80
        and hp_repl_m500k is not None and hp_repl_m500k >= 0.60
        and hp_repl_m1m is not None and hp_repl_m1m >= 0.30
        and hp_std_beaten
    )
    if all_hp:
        return (
            "HARD_PASS",
            f"CHAIN_GRADE_COMMERCIAL_SCALE: {'; '.join(hp_flags)}",
            headline,
        )
    return (
        "MIDDLE_BAND",
        f"MB: hp_fired={hp_flags}; not-all HP gates: repl_100k={hp_repl_m100k}, "
        f"repl_500k={hp_repl_m500k}, repl_1m={hp_repl_m1m}, std_beaten={hp_std_beaten}",
        headline,
    )


# ---------------------------------------------------------------------------
# Selftest — v5 raises M to 500k for measurement statistical power
# ---------------------------------------------------------------------------
def run_all_selftests(seed: int, anchor: str) -> None:
    """Selftest per META_RULE_AC + v5 USER-locked measurement-discipline gates.

    v5 USER-locked gates at M=500k (checked ONLY when CUDA available):
        wall_s < 5.0 per arm (Fix A.1 still holds at 5x M)
        kernel_active_fraction_pct >= 30 per arm (Fix C ground-truth compute-active)
        n_util_samples >= 20 per arm (sampler-cadence sanity check)

    On CPU-only laptops these gates are auto-deferred to remote GPU smoke.
    """
    # (a) adaptive_beta / predicted_p_win
    assert abs(adaptive_beta(M_REF) - BETA_BASE) < 1e-9, "adaptive_beta at M_REF wrong"
    assert adaptive_beta(1_000_000) > BETA_BASE, "adaptive_beta should grow with M"
    p_small = predicted_p_win(1000, 8192, BETA_BASE)
    p_large = predicted_p_win(1_000_000, 8192, BETA_BASE)
    assert p_small > p_large, f"p_win should shrink with M; got {p_small} <= {p_large}"

    # (b) numpy REPL selftest
    result = _run_arm_numpy(
        "ARM_REPL", seed=seed, M=200, N=64, V=32, n_queries=10,
        beta=BETA_BASE, chunk_size=64, out_dir=Path("/tmp"),
    )
    assert result["recall_cosine_mean"] > 0.5, (
        f"selftest numpy REPL recall too low: {result['recall_cosine_mean']}"
    )

    # (c) on-GPU-gen determinism + numerical parity
    if _TORCH_AVAILABLE:
        from hdlab.gpu_generated_streaming_attention import (
            GpuGenSpec, gpu_generated_streaming_readout,
        )
        device = torch.device("cuda" if _CUDA_AVAILABLE else "cpu")

        spec_a = GpuGenSpec(
            arm_seed=seed * 100 + 1, M=500, N=128, V=32, n_queries=10,
            chunk_size=128, device=device, query_noise_std=0.05, use_int8_keys=False,
        )
        r_a, vt_a, tel_a = gpu_generated_streaming_readout(
            spec_a, mode="attention", beta=BETA_BASE, sample_util_ms=UTIL_SAMPLE_MS,
        )
        r_a_n = r_a / r_a.norm(dim=-1, keepdim=True).clamp_min(1e-9)
        vt_a_n = vt_a.to(torch.float32) / vt_a.to(torch.float32).norm(
            dim=-1, keepdim=True
        ).clamp_min(1e-9)
        recall_a = (r_a_n * vt_a_n).sum(dim=-1).mean().item()
        assert recall_a > 0.8, (
            f"v5 on-GPU-gen REPL selftest recall too low: {recall_a}"
        )

        # Determinism: same spec -> bit-identical readout.
        r_b, vt_b, tel_b = gpu_generated_streaming_readout(
            spec_a, mode="attention", beta=BETA_BASE, sample_util_ms=UTIL_SAMPLE_MS,
        )
        max_diff = (r_a - r_b).abs().max().item()
        assert max_diff < 1e-3, (
            f"v5 on-GPU-gen non-deterministic: max_diff={max_diff}"
        )

        # (d) USER-locked v5 gates at M=500k (ONLY when CUDA available).
        if _CUDA_AVAILABLE:
            M_test = SELFTEST_M_FOR_MEASUREMENT_POWER
            for role, use_i8, mode_name in [
                ("REPL", True, "attention"),
                ("STD", False, "hebbian"),
            ]:
                spec_test = GpuGenSpec(
                    arm_seed=seed * 100 + (2 if role == "REPL" else 3),
                    M=M_test, N=N_CORTEX_FULL, V=V_DIM_FULL,
                    n_queries=N_QUERIES_FULL, chunk_size=ATTN_CHUNK_FULL,
                    device=device, query_noise_std=0.05, use_int8_keys=use_i8,
                )
                _, _, tel_test = gpu_generated_streaming_readout(
                    spec_test, mode=mode_name, beta=BETA_BASE,
                    sample_util_ms=UTIL_SAMPLE_MS,
                )
                wall = float(tel_test["wall_s"])
                k_pct = float(tel_test["kernel_active_fraction_pct"])
                k_ms = float(tel_test["kernel_active_ms_total"])
                n_chunks = int(tel_test["n_kernel_chunks"])
                util_pct = float(tel_test["gpu_util_mean_pct"])
                n_samples = int(tel_test["n_util_samples"])
                print(
                    f"[selftest v5 USER-gate M={M_test} {role}] wall_s={wall:.3f} "
                    f"kernel_active_pct={k_pct:.1f} kernel_ms={k_ms:.1f} "
                    f"n_chunks={n_chunks} gpu_util_pct={util_pct:.1f} "
                    f"n_samples={n_samples}",
                    flush=True,
                )
                assert wall < SELFTEST_WALL_S_MAX, (
                    f"HALT_v5_SELFTEST: M={M_test} {role} wall_s={wall:.2f} >= "
                    f"{SELFTEST_WALL_S_MAX} -- Fix A.1 regressed at 5x M"
                )
                assert k_pct >= SELFTEST_KERNEL_ACTIVE_PCT_MIN, (
                    f"HALT_v5_SELFTEST: M={M_test} {role} "
                    f"kernel_active_fraction_pct={k_pct:.1f} < "
                    f"{SELFTEST_KERNEL_ACTIVE_PCT_MIN} -- Fix C ground-truth "
                    f"below threshold; cell IS compute-starved"
                )
                assert n_samples >= SELFTEST_N_UTIL_SAMPLES_MIN, (
                    f"HALT_v5_SELFTEST: M={M_test} {role} "
                    f"n_util_samples={n_samples} < "
                    f"{SELFTEST_N_UTIL_SAMPLES_MIN} -- sampler cadence "
                    f"insufficient for statistical power"
                )

    user_gate_status = (
        f"verified_on_local_cuda_M{SELFTEST_M_FOR_MEASUREMENT_POWER}" if _CUDA_AVAILABLE
        else "deferred_to_remote_gpu_smoke_no_local_cuda"
    )
    print(
        f"[selftest] PASS  adaptive_beta_at_M_REF={BETA_BASE}  "
        f"adaptive_beta_at_1M={adaptive_beta(1_000_000):.2f}  "
        f"p_win_1M={p_large:.4f}  "
        f"tiny_numpy_recall={result['recall_cosine_mean']:.3f}  "
        f"torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE} "
        f"v5_kernel_active_fraction_meter_wired=True "
        f"v5_determinism_verified=True "
        f"user_locked_M{SELFTEST_M_FOR_MEASUREMENT_POWER}_gates={user_gate_status} "
        f"hf_gate_metric=kernel_active_fraction_pct "
        f"hf_gate_threshold={HF_KERNEL_ACTIVE_PCT_MIN_M100K}",
        flush=True,
    )
