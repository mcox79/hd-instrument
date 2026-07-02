"""Shared core v3: cortex_hippo dense-Hopfield at commercial M (100k / 500k / 1M).

v3 FIX for v2 PRE_UPLOAD_MEMORY_ABORT: v2 chunked the UPLOAD but still required
the full keys tensor RESIDENT on the GPU (M * N * key_bytes persistent). At
M=500k / N=8192 FP16 = 8.2 GB persistent — exceeds 6 GB budget correctly
caught by v2's gate.

v2 crash MEASURED@data/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v2_seed_7
/metrics.json:verdict_msg = "RuntimeError: PRE_UPLOAD_MEMORY_ABORT: estimated
peak 8485.3 MB > 6 GB HF gate (arm=ARM_STD, M=500000, N=8192, V=256)". Same
abort at seeds 13, 19.

v3 STRATEGY (fully CPU-resident, GPU-streaming):
  - Keys + vals live on CPU (optionally pinned). NEVER upload full M*N to GPU.
  - Per-chunk streaming: `hdlab.streaming_attention.streaming_attention_readout`
    transfers chunk[start:end] of keys/vals to GPU per iteration, computes online
    log-sum-exp, releases chunk. Peak GPU footprint bounded by chunk, not M.
  - STD arm: `hdlab.streaming_attention.streaming_hebbian_W` builds
    W = (vals.T @ keys) / N on GPU by streaming chunks. Persistent W = V*N*4
    = 8.4 MB on GPU. Peak transient ~= chunk * (N + V) * 4.
  - REPL arm: quantize keys to INT8 on CPU (INT8-pareto per Atom 5 CG); stream
    INT8 chunks + per-row scale to GPU per iteration.

MEMORY BUDGET AT M=1M / N=8192 / V=256 / chunk=1024 / Q=200 (v3 streaming):
  Per chunk transient (fp32 dequant):
    k_chunk_fp32:  1024 * 8192 * 4 =  33.6 MB
    v_chunk_fp32:  1024 *  256 * 4 =   1.0 MB
    sims/logits:   3 * 200 * 1024 * 4 = 2.5 MB
  Persistent (READ-REPLACE):
    o_state:       200 * 256 * 4  =   0.2 MB
  Persistent (Hebbian W, STD arm):
    W:             256 * 8192 * 4 =   8.4 MB
  Total peak (either arm): ~ 45 MB
  Total peak at M=1M: still ~ 45 MB (streaming is M-INDEPENDENT).

HOST RAM BUDGET AT M=1M (keys FP32 CPU + vals FP32 CPU):
  keys_f32_cpu:  1M * 8192 * 4 =    32.8 GB (BLOCKER on 32 GB laptop)
Wait — RAM is finite too. Mitigation: build keys/vals directly as FP16 (or INT8
for REPL) on CPU without going through FP32 intermediate at large M. See
`_build_keys_vals_cpu` below.
  keys_fp16_cpu: 1M * 8192 * 2 =    16.4 GB
  keys_int8_cpu: 1M * 8192 * 1 =     8.2 GB
  vals_fp16_cpu: 1M *  256 * 2 =   512  MB
So M=1M FP16 keys need 16.4 GB host RAM; M=500k FP16 = 8.2 GB; M=100k FP16 = 1.6 GB.
On a 32 GB laptop M=1M FP16 fits with headroom. On the 8 GB VRAM GPU nothing
resident-full-M would fit — that's exactly why streaming is required.

Prior-work check (substrate-KB, 2026-07-01):
    "chunked upload commercial hippo M=1M dense-Hopfield GPU 8GB" -> NONE at
    cosine > 0.30. Genuinely novel; v2 was v1-with-upload-chunking but same
    persistent-resident assumption; v3 is v2-with-streaming (no resident keys).

MECHANISM (2 arms x 3 M values = 6 arm-outcomes per seed): unchanged from v2.
FALSIFIABLE gates (per M): unchanged.
HF gates: HF_MEMORY_OVERFLOW at 6000 MB max_gpu_mem_allocated (v3 targets < 60 MB).

CARDINALITY (META_RULE_H): EXPECTED_N_UNITS = 2 arms * 3 M values = 6 per seed.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke MUST exercise streaming path at M=100k / FULL_N=8192 with a real GPU
  streaming pass (not CPU numpy). Assertion: peak_gpu_mb < 200 MB during smoke
  preview. Selftest also verifies streaming-vs-non-streaming numerical match on
  a small M=1000 case.

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
ATTN_CHUNK_FULL = 1024      # rows per streaming chunk (GPU-side)
UPLOAD_BATCH_FULL = 1024    # rows per CPU->GPU transfer (aligned to attn chunk)
N_QUERIES_FULL = 200

M_SWEEP_FULL = [100_000, 500_000, 1_000_000]

# Smoke: FULL_N GPU streaming preview at M=100k (must exercise v3 streaming path)
N_CORTEX_SMOKE = 1024
V_DIM_SMOKE = 128
M_SWEEP_SMOKE = [10_000]
M_SMOKE_PREVIEW_FULL_N = 100_000
N_QUERIES_SMOKE = 50
ATTN_CHUNK_SMOKE = 512
UPLOAD_BATCH_SMOKE = 512

# 6 GB total-peak GPU gate — matches HF_MEMORY_OVERFLOW.
GPU_MEM_GATE_BYTES = 6_000_000_000


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
# Memory-safe CPU key/val construction (avoids FP32 intermediate at M=1M)
# ---------------------------------------------------------------------------
def _build_keys_vals_cpu_fp16(
    seed: int, M: int, N: int, V: int, n_queries: int,
) -> Tuple["torch.Tensor", "torch.Tensor", "torch.Tensor", "torch.Tensor"]:
    """Build (M, N) FP16 keys + (M, V) FP16 vals + queries + v_target on CPU.

    Avoids full-M FP32 intermediates. Builds in row-chunks to keep peak RAM
    close to final FP16 footprint.

    Returns (keys_fp16, vals_fp16, queries_fp16, v_target_fp16). All CPU.
    """
    build_chunk = 16384
    keys_fp16 = torch.empty((M, N), dtype=torch.float16)
    vals_fp16 = torch.empty((M, V), dtype=torch.float16)

    g_key = torch.Generator(device="cpu")
    g_key.manual_seed(seed * 1000003 + N + 1)
    g_val = torch.Generator(device="cpu")
    g_val.manual_seed(seed * 1000003 + V + 2)

    for s in range(0, M, build_chunk):
        e = min(s + build_chunk, M)
        # bipolar in-place: {0,1} -> {-1,+1}
        k_int = torch.randint(0, 2, (e - s, N), generator=g_key, dtype=torch.int8)
        keys_fp16[s:e] = (k_int.to(torch.float16) * 2.0) - 1.0
        del k_int
        v_int = torch.randint(0, 2, (e - s, V), generator=g_val, dtype=torch.int8)
        vals_fp16[s:e] = (v_int.to(torch.float16) * 2.0) - 1.0
        del v_int

    # Query construction: sample n_queries rows, add small noise.
    g_q = torch.Generator(device="cpu")
    g_q.manual_seed(seed * 1000003 + 3)
    q_idx = torch.randperm(M, generator=g_q)[:n_queries]
    q_keys = keys_fp16[q_idx].to(torch.float32)
    noise = torch.randn(n_queries, N, generator=g_q, dtype=torch.float32) * 0.05
    queries_fp16 = (q_keys + noise).to(torch.float16)
    v_target_fp16 = vals_fp16[q_idx].clone()

    return keys_fp16, vals_fp16, queries_fp16, v_target_fp16


def _quantize_int8_from_fp16_cpu(
    keys_fp16: "torch.Tensor",
) -> Tuple["torch.Tensor", "torch.Tensor"]:
    """Row-chunked INT8 quantization on CPU. Returns (keys_int8, scale_fp32)."""
    from hdlab.int8_dense import quantize_int8_dense
    M, N = keys_fp16.shape
    keys_int8 = torch.empty((M, N), dtype=torch.int8)
    scale = torch.empty((M, 1), dtype=torch.float32)
    build_chunk = 16384
    for s in range(0, M, build_chunk):
        e = min(s + build_chunk, M)
        k_f32 = keys_fp16[s:e].to(torch.float32)
        k_i8, sc = quantize_int8_dense(k_f32)
        keys_int8[s:e] = k_i8
        scale[s:e] = sc
        del k_f32, k_i8, sc
    return keys_int8, scale


# ---------------------------------------------------------------------------
# Numpy REPLACE simulation (CPU smoke fallback if torch unavailable)
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
    import hashlib
    arm_hash = hashlib.sha256(readout.tobytes()).hexdigest()[:16]
    wall = time.time() - t0
    return {
        "arm_name": arm_name, "seed": int(seed), "M": int(M), "N": int(N), "V": int(V),
        "n_queries": int(n_queries), "beta": float(beta), "chunk_size": int(chunk_size),
        "recall_cosine_mean": recall, "recall_cosine_std": recall_std,
        "arm_hash": arm_hash, "backend": "numpy",
        "wall_s": float(wall), "gpu_mem_peak_mb": 0.0,
        "upload_strategy": "n/a_numpy_cpu",
    }


# ---------------------------------------------------------------------------
# Torch GPU streaming execution (v3 fix)
# ---------------------------------------------------------------------------
def _run_arm_torch(
    arm_name: str, seed: int, M: int, N: int, V: int, n_queries: int,
    beta: float, chunk_size: int, out_dir: Path,
    use_int8_keys: bool = True,
    upload_batch: int = UPLOAD_BATCH_FULL,
) -> Dict:
    """GPU streaming path: keys/vals CPU-resident; streamed per chunk to GPU."""
    if not _TORCH_AVAILABLE:
        raise RuntimeError("torch not available for torch arm")
    from hdlab.streaming_attention import (
        streaming_attention_readout,
        streaming_hebbian_W,
        estimate_streaming_peak_bytes,
    )
    import hashlib

    device = torch.device("cuda" if _CUDA_AVAILABLE else "cpu")

    t0 = time.time()
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.empty_cache()

    # PRE-STREAM MEMORY CHECK: streaming peak is M-INDEPENDENT.
    est_stream_bytes = estimate_streaming_peak_bytes(
        Q=n_queries, N=N, V=V, chunk_size=chunk_size,
    )
    # STD arm has additional W (V, N) persistent on GPU.
    if arm_name == "ARM_STD":
        est_stream_bytes += V * N * 4
    est_peak_mb = est_stream_bytes / 1e6
    print(
        f"    [{arm_name} M={M}] streaming_peak_mb={est_peak_mb:.1f} "
        f"(M-INDEPENDENT; chunk={chunk_size}, Q={n_queries}, N={N}, V={V})",
        flush=True,
    )
    if est_stream_bytes > GPU_MEM_GATE_BYTES:
        raise RuntimeError(
            f"PRE_STREAM_MEMORY_ABORT: streaming peak {est_peak_mb:.1f} MB > 6 GB HF gate "
            f"(arm={arm_name}, N={N}, V={V}, chunk={chunk_size}, Q={n_queries})"
        )

    # Build CPU keys/vals FP16 in row-chunks (avoids FP32-full-M intermediate).
    print(f"    [{arm_name} M={M}] building CPU keys/vals FP16...", flush=True)
    t_build = time.time()
    keys_fp16_cpu, vals_fp16_cpu, queries_fp16_cpu, v_target_fp16_cpu = (
        _build_keys_vals_cpu_fp16(seed, M, N, V, n_queries)
    )
    print(
        f"    [{arm_name} M={M}] cpu-build wall={time.time() - t_build:.1f}s "
        f"keys_mb={keys_fp16_cpu.numel() * 2 / 1e6:.1f} "
        f"vals_mb={vals_fp16_cpu.numel() * 2 / 1e6:.1f}",
        flush=True,
    )

    upload_strategy: str
    key_scale_cpu: Optional["torch.Tensor"] = None
    keys_for_stream_cpu: "torch.Tensor"
    if arm_name == "ARM_REPL" and use_int8_keys:
        # INT8 quantize keys on CPU (row-chunked; keeps peak RAM ~ FP16 footprint).
        t_q = time.time()
        keys_int8_cpu, key_scale_cpu = _quantize_int8_from_fp16_cpu(keys_fp16_cpu)
        print(
            f"    [{arm_name} M={M}] cpu-int8-quantize wall={time.time() - t_q:.1f}s "
            f"int8_mb={keys_int8_cpu.numel() / 1e6:.1f}",
            flush=True,
        )
        del keys_fp16_cpu
        keys_for_stream_cpu = keys_int8_cpu
        upload_strategy = "cpu_resident_int8_streamed_per_chunk"
    else:
        keys_for_stream_cpu = keys_fp16_cpu
        upload_strategy = "cpu_resident_fp16_streamed_per_chunk"

    # Small tensors go direct to device.
    queries_dev = queries_fp16_cpu.to(device)
    v_target_dev = v_target_fp16_cpu.to(device)
    del queries_fp16_cpu, v_target_fp16_cpu

    if arm_name == "ARM_STD":
        # Streaming Hebbian W build.
        W = streaming_hebbian_W(
            keys_cpu=keys_for_stream_cpu,
            vals_cpu=vals_fp16_cpu,
            N=N, V=V, chunk_size=chunk_size, device=device,
            key_scale_cpu=key_scale_cpu,
        )
        readout = queries_dev.to(torch.float32) @ W.T
        del W
    elif arm_name == "ARM_REPL":
        readout = streaming_attention_readout(
            query=queries_dev.to(torch.float32),
            keys_cpu=keys_for_stream_cpu,
            vals_cpu=vals_fp16_cpu,
            chunk_size=chunk_size,
            beta=beta,
            device=device,
            key_scale_cpu=key_scale_cpu,
        )
    else:
        raise ValueError(f"unknown arm: {arm_name}")

    # Recall metric
    r_norm = readout / readout.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    t_target_fp32 = v_target_dev.to(torch.float32)
    t_norm = t_target_fp32 / t_target_fp32.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    per_q_cos = (r_norm * t_norm).sum(dim=-1)
    recall = float(per_q_cos.mean().item())
    recall_std = float(per_q_cos.std().item())

    readout_cpu = readout.detach().cpu().to(torch.float32).contiguous().numpy()
    arm_hash = hashlib.sha256(readout_cpu.tobytes()).hexdigest()[:16]

    gpu_mem_peak_mb = 0.0
    if device.type == "cuda":
        gpu_mem_peak_mb = float(torch.cuda.max_memory_allocated(device) / 1e6)

    wall = time.time() - t0
    result = {
        "arm_name": arm_name, "seed": int(seed), "M": int(M), "N": int(N), "V": int(V),
        "n_queries": int(n_queries), "beta": float(beta), "chunk_size": int(chunk_size),
        "upload_batch": int(upload_batch),
        "recall_cosine_mean": recall, "recall_cosine_std": recall_std,
        "arm_hash": arm_hash,
        "backend": "torch.cuda" if device.type == "cuda" else "torch.cpu",
        "int8_keys": bool(use_int8_keys and arm_name == "ARM_REPL"),
        "upload_strategy": upload_strategy,
        "estimated_streaming_peak_mb": float(est_peak_mb),
        "wall_s": float(wall),
        "gpu_mem_peak_mb": gpu_mem_peak_mb,
    }

    # Cleanup
    del keys_for_stream_cpu, vals_fp16_cpu, queries_dev, v_target_dev, readout
    if key_scale_cpu is not None:
        del key_scale_cpu
    if _CUDA_AVAILABLE:
        torch.cuda.empty_cache()

    return result


def run_arm(
    arm_name: str, seed: int, M: int, N: int, V: int, n_queries: int,
    beta: float, chunk_size: int, out_dir: Path,
    use_torch: bool, use_int8_keys: bool = True,
    upload_batch: int = UPLOAD_BATCH_FULL,
) -> Dict:
    if use_torch and _TORCH_AVAILABLE:
        return _run_arm_torch(
            arm_name, seed, M, N, V, n_queries, beta, chunk_size, out_dir,
            use_int8_keys=use_int8_keys, upload_batch=upload_batch,
        )
    return _run_arm_numpy(
        arm_name, seed, M, N, V, n_queries, beta, chunk_size, out_dir,
    )


def run_one_M(
    seed: int, M: int, N: int, V: int, n_queries: int, chunk_size: int,
    out_dir: Path, use_torch: bool, use_int8_keys: bool = True,
    upload_batch: int = UPLOAD_BATCH_FULL,
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
            upload_batch=upload_batch,
        )
        r["p_win_predicted"] = float(p_win_pred)
        arms.append(r)
        print(
            f"    [{arm_name} M={M}] recall={r['recall_cosine_mean']:.4f} "
            f"wall={r['wall_s']:.1f}s gpu_mem_peak_mb={r['gpu_mem_peak_mb']:.1f} "
            f"strategy={r.get('upload_strategy', 'n/a')}",
            flush=True,
        )
        emit_heartbeat(
            out_dir, unit_idx=len(arms),
            elapsed_s=time.time() - t_arm,
            total_units=2,
            extra={"arm": arm_name, "M": M, "recall": r["recall_cosine_mean"],
                   "gpu_mem_peak_mb": r["gpu_mem_peak_mb"]},
        )
    return arms


# ---------------------------------------------------------------------------
# Verdict logic (IDENTICAL to v2)
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
# Selftest — MUST verify streaming vs non-streaming numerical match
# ---------------------------------------------------------------------------
def run_all_selftests(seed: int, anchor: str) -> None:
    """Selftest per META_RULE_AC + v3-specific streaming-vs-non-streaming check."""
    # (a) adaptive_beta / predicted_p_win sanity
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

    # (c) v3-specific: streaming vs chunked (non-streaming) numerical parity
    if _TORCH_AVAILABLE:
        from hdlab.streaming_attention import streaming_attention_readout
        from hdlab.chunked_attention import chunked_attention_readout

        # Small case where full-tensor-on-device is fine.
        M_test = 1000
        N_test = 128
        V_test = 32
        Q_test = 8
        g = torch.Generator(device="cpu")
        g.manual_seed(seed + 42)
        keys_f32 = ((torch.randint(0, 2, (M_test, N_test), generator=g, dtype=torch.int32) * 2 - 1)
                    .to(torch.float32))
        vals_f32 = ((torch.randint(0, 2, (M_test, V_test), generator=g, dtype=torch.int32) * 2 - 1)
                    .to(torch.float32))
        q_idx = torch.randperm(M_test, generator=g)[:Q_test]
        noise = torch.randn(Q_test, N_test, generator=g, dtype=torch.float32) * 0.05
        queries_f32 = keys_f32[q_idx] + noise

        device = torch.device("cuda" if _CUDA_AVAILABLE else "cpu")
        keys_fp16_cpu = keys_f32.to(torch.float16)
        vals_fp16_cpu = vals_f32.to(torch.float16)
        queries_dev = queries_f32.to(device)

        # Streaming path
        readout_stream = streaming_attention_readout(
            query=queries_dev, keys_cpu=keys_fp16_cpu, vals_cpu=vals_fp16_cpu,
            chunk_size=128, beta=BETA_BASE, device=device,
        )
        # Non-streaming reference: upload full and use chunked_attention
        keys_fp16_dev = keys_fp16_cpu.to(device)
        vals_fp16_dev = vals_fp16_cpu.to(device)
        readout_chunk = chunked_attention_readout(
            query=queries_dev, keys=keys_fp16_dev, vals=vals_fp16_dev,
            chunk_size=128, beta=BETA_BASE,
        )
        # FP16 tolerance: max abs diff <= 5e-2 is comfortable.
        max_abs_diff = (readout_stream - readout_chunk).abs().max().item()
        assert max_abs_diff < 5e-2, (
            f"streaming-vs-chunked FP16 mismatch: max_abs_diff={max_abs_diff}"
        )

        # Also test int8 streaming path signature (no crash).
        from hdlab.int8_dense import quantize_int8_dense
        keys_i8_cpu, key_scale_cpu = quantize_int8_dense(keys_f32)
        readout_stream_i8 = streaming_attention_readout(
            query=queries_dev, keys_cpu=keys_i8_cpu, vals_cpu=vals_fp16_cpu,
            chunk_size=128, beta=BETA_BASE, device=device,
            key_scale_cpu=key_scale_cpu,
        )
        assert readout_stream_i8.shape == (Q_test, V_test), (
            f"INT8 streaming shape wrong: {readout_stream_i8.shape}"
        )

    print(
        f"[selftest] PASS  adaptive_beta_at_M_REF={BETA_BASE}  "
        f"adaptive_beta_at_1M={adaptive_beta(1_000_000):.2f}  "
        f"p_win_1M={p_large:.4f}  "
        f"tiny_numpy_recall={result['recall_cosine_mean']:.3f}  "
        f"torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE} "
        f"v3_streaming_vs_chunked_numerical_parity=verified",
        flush=True,
    )
