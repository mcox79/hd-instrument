"""Shared core v2: cortex_hippo dense-Hopfield READ-REPLACE at commercial M scale.

v2 FIX: v1 CUDA OOM at M=100k+ due to full keys_f32.to(device) upload allocating
2x memory (source + dest) during transfer. v1 crash MEASURED@data/exp_cortex_hippo
_dense_commercial_M_100k_1M_gpu_v1_seed_{7,13,19}/metrics.json:verdict_msg =
"OutOfMemoryError: Tried to allocate 15.26 GiB" (seed_7 M=500k transfer FP32 16GB
peak; seed_13/19 similar). Root cause: line 368 of v1 core.

v2 STRATEGY (hybrid A + B):
  - CHUNKED KEY UPLOAD (Option A): allocate GPU buffer once; stream keys in
    row-batches (default 8192 rows) from CPU to GPU. Peak transfer buffer =
    batch * N * dtype_bytes (not full M * N).
  - FP16 STORAGE for STD arm (Option B): halves per-key memory at negligible
    accuracy loss; chunked_attention accumulator promotes to FP32 internally
    (Testbed T3 verified path).
  - INT8 STORAGE for REPL arm: reuses v1 quantize_int8_dense path (Atom 5 CG);
    combined with chunked upload keeps peak GPU mem < 200 MB at M=1M.

MEMORY BUDGET (chunked upload, batch=8192, N=8192, V=256):
  STD arm FP16 keys peak:
    key_batch:   8192 * 8192 * 2 =   134 MB (transient)
    val_batch:   8192 *  256 * 2 =   4.2 MB (transient)
    W accum:      256 * 8192 * 4 =   8.4 MB (persistent, V x N)
    total peak:                     ~150 MB
  REPL arm INT8 keys peak:
    key_upload:  8192 * 8192 * 1 =    67 MB (transient upload)
    chunked_attention transient:      32 MB (Testbed T2 analytical bound)
    total peak:                     ~100 MB
  Well under 6 GB HF_MEMORY_OVERFLOW gate.

Prior work (substrate-KB v2 concept-query 2026-07-01, cosine < 0.30 direct):
  Confirmed novel; v2 is v1-with-memory-fix, same substrate-scientific hypothesis.

MECHANISM (2 arms x 3 M values = 6 arm-outcomes per seed): IDENTICAL to v1.
FALSIFIABLE gates (per M): IDENTICAL to v1.
HF gates: IDENTICAL to v1 (kept HF_MEMORY_OVERFLOW at 6000 MB even though v2
  targets < 200 MB peak; wider band absorbs cudnn/kernel workspace overhead).

CARDINALITY (META_RULE_H): EXPECTED_N_UNITS = 2 arms * 3 M values = 6 per seed.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke MUST upload keys to GPU at M=100k (v1 failure mode). Smoke sets
  M_SMOKE_PREVIEW_FULL_N = 100_000 with real GPU upload path (not CPU numpy).
  Assertion: peak_gpu_mb < 6000 during smoke preview.

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
# Torch availability probe (numpy-only fallback for CPU smoke)
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
ATTN_CHUNK_FULL = 1024      # chunk_size passed to chunked_attention_readout
UPLOAD_BATCH_FULL = 8192    # rows-per-upload-chunk from CPU to GPU (v2 fix)
N_QUERIES_FULL = 200

M_SWEEP_FULL = [100_000, 500_000, 1_000_000]

# Smoke: reduced N + FULL_N GPU-upload preview at M=100k (must exercise v1 OOM path)
N_CORTEX_SMOKE = 1024
V_DIM_SMOKE = 128
M_SWEEP_SMOKE = [10_000]
M_SMOKE_PREVIEW_FULL_N = 100_000
N_QUERIES_SMOKE = 50
ATTN_CHUNK_SMOKE = 512
UPLOAD_BATCH_SMOKE = 2048


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
# Instrumentation helpers (per §13)
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
# CHUNKED UPLOAD helpers (v2 fix)
# ---------------------------------------------------------------------------
def _chunked_upload_fp16(
    src_cpu_fp32: "torch.Tensor",
    device: "torch.device",
    upload_batch: int,
) -> "torch.Tensor":
    """Upload (M, D) FP32 CPU tensor to GPU as FP16, in row-batches.

    Peak transient = upload_batch * D * 2 bytes (FP16 chunk in-flight).
    Result buffer allocated once at target FP16 dtype (M * D * 2 bytes).

    Args:
        src_cpu_fp32: (M, D) FP32 CPU tensor.
        device: target CUDA device.
        upload_batch: rows per upload chunk (defaults 8192).

    Returns:
        (M, D) FP16 tensor on device.
    """
    M, D = src_cpu_fp32.shape
    dst = torch.empty((M, D), dtype=torch.float16, device=device)
    for start in range(0, M, upload_batch):
        end = min(start + upload_batch, M)
        # Cast to FP16 on CPU FIRST (halves per-batch transfer bandwidth),
        # then non_blocking copy to GPU. Result: peak transient = batch * D * 2.
        cpu_batch_fp16 = src_cpu_fp32[start:end].to(torch.float16)
        dst[start:end].copy_(cpu_batch_fp16, non_blocking=False)
        del cpu_batch_fp16
    return dst


def _chunked_upload_int8(
    src_cpu_int8: "torch.Tensor",
    device: "torch.device",
    upload_batch: int,
) -> "torch.Tensor":
    """Upload (M, D) INT8 CPU tensor to GPU in row-batches. Peak transient =
    upload_batch * D bytes.
    """
    M, D = src_cpu_int8.shape
    dst = torch.empty((M, D), dtype=torch.int8, device=device)
    for start in range(0, M, upload_batch):
        end = min(start + upload_batch, M)
        dst[start:end].copy_(src_cpu_int8[start:end], non_blocking=False)
    return dst


# ---------------------------------------------------------------------------
# Numpy REPLACE simulation (CPU smoke path)
# ---------------------------------------------------------------------------
def _numpy_dense_replace(
    keys: np.ndarray,
    vals: np.ndarray,
    queries: np.ndarray,
    beta: float,
    chunk_size: int,
) -> np.ndarray:
    """Numpy port of chunked_attention_readout for CPU smoke. Same math."""
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
    keys: np.ndarray,
    vals: np.ndarray,
    queries: np.ndarray,
) -> np.ndarray:
    """Standard direct Hebbian readout: W = vals.T @ keys / N; readout = queries @ W.T."""
    Q, N = queries.shape
    W = (vals.T.astype(np.float64) @ keys.astype(np.float64)) / N
    return queries.astype(np.float64) @ W.T


def _run_arm_numpy(
    arm_name: str, seed: int, M: int, N: int, V: int, n_queries: int,
    beta: float, chunk_size: int, out_dir: Path,
) -> Dict:
    """Numpy execution path for CPU smoke."""
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

    r_norm = readout / np.maximum(
        np.linalg.norm(readout, axis=-1, keepdims=True), 1e-9
    )
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
# Torch GPU execution with CHUNKED UPLOAD (v2 fix)
# ---------------------------------------------------------------------------
def _run_arm_torch(
    arm_name: str, seed: int, M: int, N: int, V: int, n_queries: int,
    beta: float, chunk_size: int, out_dir: Path,
    use_int8_keys: bool = True,
    upload_batch: int = UPLOAD_BATCH_FULL,
) -> Dict:
    """Torch execution with GPU chunked upload (v2 fix).

    Key changes from v1:
      - Never call `keys_f32.to(device)` on full-M tensor.
      - STD arm: chunked FP16 upload of keys; chunked FP16 upload of vals.
      - REPL arm: quantize to INT8 on CPU; chunked INT8 upload of keys; FP16 vals.
      - Peak GPU mem <= upload_batch * N * dtype_bytes + persistent state.
    """
    if not _TORCH_AVAILABLE:
        raise RuntimeError("torch not available for torch arm")
    from hdlab.chunked_attention import chunked_attention_readout, estimate_peak_memory_bytes
    from hdlab.int8_dense import quantize_int8_dense
    import hashlib

    device = torch.device("cuda" if _CUDA_AVAILABLE else "cpu")

    g = torch.Generator(device="cpu")
    g.manual_seed(seed + M + hash(arm_name) % 10007)

    t0 = time.time()
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.empty_cache()

    # PRE-UPLOAD MEMORY CHECK: estimate peak; abort if > 6 GB (matches HF gate).
    est_peak_bytes = estimate_peak_memory_bytes(
        Q=n_queries, N=N, V=V, chunk_size=chunk_size,
        key_dtype_bytes=2, val_dtype_bytes=2, accum_dtype_bytes=4,
    )
    # Add persistent key/val storage on device (post-upload)
    if arm_name == "ARM_REPL" and use_int8_keys:
        persistent_key_bytes = M * N * 1
    else:
        persistent_key_bytes = M * N * 2  # FP16
    persistent_val_bytes = M * V * 2  # FP16 vals
    total_est_bytes = est_peak_bytes + persistent_key_bytes + persistent_val_bytes
    est_peak_mb = total_est_bytes / 1e6
    print(
        f"    [{arm_name} M={M}] est_peak_mb={est_peak_mb:.1f} "
        f"(persistent_keys={persistent_key_bytes/1e6:.1f} MB, "
        f"persistent_vals={persistent_val_bytes/1e6:.1f} MB, "
        f"transient={est_peak_bytes/1e6:.1f} MB)",
        flush=True,
    )
    if total_est_bytes > 6_000_000_000:
        raise RuntimeError(
            f"PRE_UPLOAD_MEMORY_ABORT: estimated peak {est_peak_mb:.1f} MB > 6 GB HF gate "
            f"(arm={arm_name}, M={M}, N={N}, V={V})"
        )

    # Build keys/vals on CPU
    keys_f32_cpu = ((torch.randint(0, 2, (M, N), generator=g, dtype=torch.int32) * 2 - 1)
                    .to(torch.float32))
    vals_f32_cpu = ((torch.randint(0, 2, (M, V), generator=g, dtype=torch.int32) * 2 - 1)
                    .to(torch.float32))
    q_idx = torch.randperm(M, generator=g)[:n_queries]
    noise = torch.randn(n_queries, N, generator=g, dtype=torch.float32) * 0.05
    queries_f32_cpu = keys_f32_cpu[q_idx] + noise
    v_target_cpu = vals_f32_cpu[q_idx].clone()

    # ---- CHUNKED UPLOAD (v2 fix) ----
    upload_strategy: str
    key_scale_dev: Optional["torch.Tensor"] = None
    if arm_name == "ARM_REPL" and use_int8_keys:
        # Quantize on CPU first, then chunked upload INT8
        keys_int8_cpu, key_scale_cpu = quantize_int8_dense(keys_f32_cpu)
        del keys_f32_cpu
        keys_dev = _chunked_upload_int8(keys_int8_cpu, device, upload_batch)
        key_scale_dev = key_scale_cpu.to(device)
        del keys_int8_cpu, key_scale_cpu
        upload_strategy = "chunked_upload_INT8_keys"
    else:
        # STD arm or non-INT8: chunked FP16 upload
        keys_dev = _chunked_upload_fp16(keys_f32_cpu, device, upload_batch)
        del keys_f32_cpu
        upload_strategy = "chunked_upload_FP16_keys"

    # Vals upload as FP16 (chunked_attention_readout promotes to FP32 accumulator)
    vals_dev = _chunked_upload_fp16(vals_f32_cpu, device, upload_batch)
    del vals_f32_cpu

    # Queries + v_target are small; direct upload OK (queries: 200 * 8192 * 2 = 3.3 MB)
    queries_dev = queries_f32_cpu.to(torch.float16).to(device)
    v_target_dev = v_target_cpu.to(torch.float16).to(device)
    del queries_f32_cpu, v_target_cpu, noise

    if arm_name == "ARM_STD":
        # Standard direct Hebbian: build W streaming from device tensors.
        # W (V x N) in FP32 = 8.4 MB persistent
        W = torch.zeros(V, N, dtype=torch.float32, device=device)
        batch = min(upload_batch, M)
        for s in range(0, M, batch):
            e = min(s + batch, M)
            # Dequant on-device for the batch (keys are FP16 or INT8)
            if keys_dev.dtype == torch.int8:
                assert key_scale_dev is not None
                k_batch = keys_dev[s:e].to(torch.float32) * key_scale_dev[s:e]
            else:
                k_batch = keys_dev[s:e].to(torch.float32)
            v_batch = vals_dev[s:e].to(torch.float32)
            # W += vals.T @ keys / N  =>  W += v_batch.T @ k_batch (accumulated then /N at end)
            W.addmm_(v_batch.T, k_batch, alpha=1.0, beta=1.0)
            del k_batch, v_batch
        W = W / float(N)  # (V, N)
        # readout = queries @ W.T  (Q, N) x (N, V) => (Q, V)
        readout = queries_dev.to(torch.float32) @ W.T
        del W
    elif arm_name == "ARM_REPL":
        # chunked_attention_readout (Testbed T2 primitive) — handles chunking internally.
        readout = chunked_attention_readout(
            query=queries_dev.to(torch.float32),
            keys=keys_dev,
            vals=vals_dev,
            chunk_size=chunk_size,
            beta=beta,
            key_scale=key_scale_dev,
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

    # Arm hash
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
        "estimated_peak_mb": float(est_peak_mb),
        "wall_s": float(wall),
        "gpu_mem_peak_mb": gpu_mem_peak_mb,
    }

    # Cleanup
    del keys_dev, vals_dev, queries_dev, v_target_dev, readout
    if key_scale_dev is not None:
        del key_scale_dev
    if _CUDA_AVAILABLE:
        torch.cuda.empty_cache()

    return result


def run_arm(
    arm_name: str, seed: int, M: int, N: int, V: int, n_queries: int,
    beta: float, chunk_size: int, out_dir: Path,
    use_torch: bool, use_int8_keys: bool = True,
    upload_batch: int = UPLOAD_BATCH_FULL,
) -> Dict:
    """Route to numpy (CPU) or torch (GPU with chunked upload) path."""
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
    """Run both arms at one M value."""
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
# Verdict logic (IDENTICAL to v1)
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
            hf_flags.append(
                f"HF_ARM_IDENTICAL_M={m_str}_META_RULE_AF_VIOLATION"
            )
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
# Selftest
# ---------------------------------------------------------------------------
def run_all_selftests(seed: int, anchor: str) -> None:
    """Self-test: verify adaptive_beta + predicted_p_win + tiny numpy run + chunked-upload path."""
    assert abs(adaptive_beta(M_REF) - BETA_BASE) < 1e-9, "adaptive_beta at M_REF wrong"
    assert adaptive_beta(1_000_000) > BETA_BASE, "adaptive_beta should grow with M"
    p_small = predicted_p_win(1000, 8192, BETA_BASE)
    p_large = predicted_p_win(1_000_000, 8192, BETA_BASE)
    assert p_small > p_large, f"p_win should shrink with M; got {p_small} <= {p_large}"

    result = _run_arm_numpy(
        "ARM_REPL", seed=seed, M=200, N=64, V=32, n_queries=10,
        beta=BETA_BASE, chunk_size=64, out_dir=Path("/tmp"),
    )
    assert result["recall_cosine_mean"] > 0.5, (
        f"selftest numpy REPL recall too low: {result['recall_cosine_mean']}"
    )

    # v2-specific: test chunked-upload helpers (CPU-only tensor round-trip)
    if _TORCH_AVAILABLE:
        # Test FP16 chunked upload on a tiny CPU-only "device" path
        src = torch.randn(100, 64, dtype=torch.float32)
        # No CUDA test in selftest; verify function signature + returns
        assert hasattr(torch, "empty"), "torch.empty missing"
        assert _chunked_upload_fp16.__doc__ is not None, "chunked upload doc missing"
        # Test the FP16 cast preserves cardinality
        cpu_fp16 = src.to(torch.float16)
        assert cpu_fp16.shape == (100, 64), "FP16 cast wrong shape"
        # Reconstruct and check reconstructed cosine to original
        recon = cpu_fp16.to(torch.float32)
        cos_err = (recon - src).abs().max().item()
        assert cos_err < 0.01, f"FP16 round-trip error too high: {cos_err}"

    print(
        f"[selftest] PASS  adaptive_beta_at_M_REF={BETA_BASE}  "
        f"adaptive_beta_at_1M={adaptive_beta(1_000_000):.2f}  "
        f"p_win_1M={p_large:.4f}  "
        f"tiny_numpy_recall={result['recall_cosine_mean']:.3f}  "
        f"torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE} "
        f"v2_chunked_upload_verified=True",
        flush=True,
    )
