"""On-GPU seeded key/val generation + streaming attention (v4 CPU-bottleneck fix).

Extends hdlab.streaming_attention: instead of pre-materializing (M, N) keys and
(M, V) vals in CPU RAM and streaming them to GPU per chunk, this primitive
generates each chunk's keys/vals DIRECTLY on GPU with a deterministic per-chunk
seed. Zero CPU RAM for the substrate; zero CPU->GPU key transfer.

Why this exists (v4 fix per Orchestrator M=500k probe):
    v3 chunked streaming attention was correct (peak GPU M-independent ~35-43 MB)
    but wall_s was CPU-dominated: 21-25s cpu-build + 12s INT8-quantize at M=500k,
    with GPU util 1-3% steady-state. Root cause: v3 materialized full-M keys+vals
    in CPU RAM per arm. v4 eliminates that entirely by generating each chunk on
    GPU. Expected: wall_s ~= GPU-only time (~2-5s per arm at M=500k), util >= 30%.

Determinism model:
    Each chunk's random state is derived from (arm_seed, chunk_start). The same
    (arm_seed, chunk_start) always produces the same chunk contents, so:
      - Query-key rows can be extracted from their containing chunk during a
        pre-pass and cached (Q * N * 4 bytes on GPU; small).
      - Streaming attention pass regenerates each chunk from the same seed
        scheme and gets bit-identical contents.
      - Arm hash / recall are reproducible across runs.

Standard use:
    from hdlab.gpu_generated_streaming_attention import (
        gpu_generated_streaming_readout, GpuGenSpec,
    )
    spec = GpuGenSpec(arm_seed=seed_for_arm, M=1_000_000, N=8192, V=256,
                     n_queries=200, chunk_size=1024, device=torch.device('cuda'))
    readout, v_target = gpu_generated_streaming_readout(
        spec, mode='attention', beta=13.0,   # ARM_REPL
    )
    # or
    readout, v_target = gpu_generated_streaming_readout(
        spec, mode='hebbian',                # ARM_STD
    )

GPU util measurement:
    Optional GpuUtilSampler background-thread samples torch.cuda.utilization()
    every N ms during the pass. Returns mean util_pct over samples where
    util_pct >= 0 (torch.cuda.utilization returns 0 when NVML unavailable).
    Falls back to pynvml if importable; else best-effort 0 (HF gate downstream).
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

import torch


@dataclass
class GpuGenSpec:
    """Descriptor for on-GPU generated key/val substrate.

    Args:
        arm_seed: master seed for this arm. Per-chunk seed = arm_seed * 1000003 + chunk_start.
        M: total number of items (keys/vals).
        N: key dimensionality.
        V: value dimensionality.
        n_queries: number of query slots. Queries = subset of keys + small noise.
        chunk_size: rows per streaming chunk.
        device: target CUDA device.
        query_noise_std: std of Gaussian noise added to query keys.
        use_int8_keys: if True, quantize each chunk to INT8 before matmul (REPL path
            with INT8 pareto per Atom 5). If False, use FP16.
    """
    arm_seed: int
    M: int
    N: int
    V: int
    n_queries: int
    chunk_size: int
    device: torch.device
    query_noise_std: float = 0.05
    use_int8_keys: bool = False


def _chunk_seed(arm_seed: int, chunk_start: int) -> int:
    """Deterministic per-chunk seed. Same (arm_seed, chunk_start) -> same chunk."""
    return (arm_seed * 1_000_003 + chunk_start * 31 + 1) & 0xFFFFFFFF


def _generate_chunk_on_gpu(
    spec: GpuGenSpec,
    chunk_start: int,
    chunk_end: int,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Generate one (chunk, N) FP16 keys + (chunk, V) FP16 vals on GPU.

    Bipolar {-1, +1} entries. Seeded deterministically per chunk_start.
    Peak transient (on GPU) = 2 * chunk_size * (N + V) bytes (INT8 pre-cast)
    + chunk_size * (N + V) * 2 bytes (FP16 result) — small.
    """
    seed = _chunk_seed(spec.arm_seed, chunk_start)
    g = torch.Generator(device=spec.device)
    g.manual_seed(seed)
    rows = chunk_end - chunk_start
    # Bipolar in-place: randint(0, 2) -> {0, 1} -> *2-1 -> {-1, +1}
    k_i8 = torch.randint(
        0, 2, (rows, spec.N), generator=g, dtype=torch.int8, device=spec.device
    )
    v_i8 = torch.randint(
        0, 2, (rows, spec.V), generator=g, dtype=torch.int8, device=spec.device
    )
    k_fp16 = (k_i8.to(torch.float16) * 2.0) - 1.0
    v_fp16 = (v_i8.to(torch.float16) * 2.0) - 1.0
    del k_i8, v_i8
    return k_fp16, v_fp16


def _snapshot_query_slots(
    spec: GpuGenSpec, q_idx: torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Pre-pass: generate chunks that contain query rows; extract those rows only.

    Peak transient = one chunk on GPU. Result: (Q, N) FP16 query-keys and
    (Q, V) FP16 v_target on GPU. Small persistent footprint.
    """
    Q = q_idx.numel()
    q_keys = torch.empty((Q, spec.N), dtype=torch.float16, device=spec.device)
    v_target = torch.empty((Q, spec.V), dtype=torch.float16, device=spec.device)

    # q_idx sorted for a single sequential pass.
    q_sorted, sort_perm = torch.sort(q_idx)
    q_sorted_cpu = q_sorted.cpu()  # small: 200 ints
    inv_perm = torch.argsort(sort_perm)

    q_ptr = 0
    for chunk_start in range(0, spec.M, spec.chunk_size):
        chunk_end = min(chunk_start + spec.chunk_size, spec.M)
        # Advance q_ptr past any query indices in [chunk_start, chunk_end).
        # (early exit if no more query indices remain)
        if q_ptr >= Q:
            break
        # Skip chunk if no query row is in it.
        if q_sorted_cpu[q_ptr].item() >= chunk_end:
            continue

        k_chunk, v_chunk = _generate_chunk_on_gpu(spec, chunk_start, chunk_end)
        while q_ptr < Q and q_sorted_cpu[q_ptr].item() < chunk_end:
            row_in_chunk = q_sorted_cpu[q_ptr].item() - chunk_start
            sorted_pos = q_ptr
            # Write to the position in the (Q, ...) tensor at sorted order.
            q_keys[sorted_pos] = k_chunk[row_in_chunk]
            v_target[sorted_pos] = v_chunk[row_in_chunk]
            q_ptr += 1
        del k_chunk, v_chunk

    # Un-sort to match original q_idx order.
    q_keys = q_keys[inv_perm]
    v_target = v_target[inv_perm]
    return q_keys, v_target


def _build_queries(
    spec: GpuGenSpec, q_idx: torch.Tensor, q_keys: torch.Tensor,
) -> torch.Tensor:
    """Add small Gaussian noise to query-key snapshots. Returns (Q, N) FP16 on GPU."""
    g = torch.Generator(device=spec.device)
    g.manual_seed(spec.arm_seed * 1_000_003 + 7)
    noise = torch.randn(
        spec.n_queries, spec.N, generator=g, dtype=torch.float32, device=spec.device,
    ) * spec.query_noise_std
    return (q_keys.to(torch.float32) + noise).to(torch.float16)


class GpuUtilSampler:
    """Background thread sampling torch.cuda.utilization every sample_ms.

    Non-blocking start/stop. mean_pct() returns average over samples where
    util >= 0 (torch.cuda.utilization returns 0 when NVML unavailable).

    If pynvml is importable, uses NVML directly (more reliable). Else falls
    back to torch.cuda.utilization().
    """

    def __init__(self, device: torch.device, sample_ms: int = 50):
        self.device = device
        self.sample_ms = sample_ms
        self._samples: List[int] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._use_pynvml = False
        self._nvml_handle = None
        try:
            import pynvml  # type: ignore
            pynvml.nvmlInit()
            idx = device.index if device.index is not None else 0
            self._nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
            self._pynvml = pynvml
            self._use_pynvml = True
        except Exception:
            self._use_pynvml = False

    def _sample_once(self) -> int:
        if self._use_pynvml and self._nvml_handle is not None:
            try:
                rates = self._pynvml.nvmlDeviceGetUtilizationRates(self._nvml_handle)
                return int(rates.gpu)
            except Exception:
                return -1
        # Fallback: torch.cuda.utilization
        try:
            return int(torch.cuda.utilization(self.device))
        except Exception:
            return -1

    def _run(self) -> None:
        while not self._stop.is_set():
            u = self._sample_once()
            if u >= 0:
                self._samples.append(u)
            self._stop.wait(self.sample_ms / 1000.0)

    def start(self) -> None:
        if self.device.type != "cuda":
            return  # no-op on CPU
        self._stop.clear()
        self._samples = []
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return
        self._stop.set()
        self._thread.join(timeout=1.0)
        self._thread = None

    def mean_pct(self) -> float:
        if not self._samples:
            return 0.0
        return float(sum(self._samples)) / float(len(self._samples))

    def n_samples(self) -> int:
        return len(self._samples)

    def source(self) -> str:
        return "pynvml" if self._use_pynvml else "torch.cuda.utilization"


def gpu_generated_streaming_readout(
    spec: GpuGenSpec,
    mode: str,
    beta: float = 13.0,
    sample_util_ms: int = 50,
) -> Tuple[torch.Tensor, torch.Tensor, dict]:
    """Streaming READ-REPLACE ('attention') or Hebbian ('hebbian') readout.

    Generates each chunk on GPU (zero CPU RAM for keys/vals), runs the compute,
    frees the chunk. Peak GPU footprint is M-INDEPENDENT.

    Args:
        spec: GpuGenSpec descriptor.
        mode: 'attention' (ARM_REPL) or 'hebbian' (ARM_STD).
        beta: softmax sharpness (attention mode only).
        sample_util_ms: GPU util sampler period.

    Returns:
        (readout, v_target, telemetry) — readout (Q, V) FP32 on device;
        v_target (Q, V) FP16 on device; telemetry dict with wall_s /
        gpu_util_mean_pct / n_util_samples / util_source / gpu_mem_peak_mb.
    """
    if mode not in ("attention", "hebbian"):
        raise ValueError(f"mode must be 'attention' or 'hebbian'; got {mode!r}")

    device = spec.device
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.empty_cache()

    # (1) Choose query indices (small CPU tensor, deterministic).
    g_qidx = torch.Generator(device="cpu")
    g_qidx.manual_seed(spec.arm_seed * 1_000_003 + 5)
    q_idx = torch.randperm(spec.M, generator=g_qidx)[: spec.n_queries]
    q_idx_dev = q_idx.to(device)

    # (2) Pre-pass: snapshot query rows only from their containing chunks.
    q_keys, v_target = _snapshot_query_slots(spec, q_idx)
    queries = _build_queries(spec, q_idx_dev, q_keys)  # (Q, N) FP16 on GPU
    del q_keys

    # (3) Start GPU util sampler for the main compute pass.
    util = GpuUtilSampler(device, sample_ms=sample_util_ms)
    util.start()
    t0 = time.time()

    try:
        if mode == "attention":
            # Online log-sum-exp streaming attention.
            Q = spec.n_queries
            V_ = spec.V
            q32 = queries.to(torch.float32)
            q_normed = q32 / q32.norm(dim=-1, keepdim=True).clamp_min(1e-9)
            m_state = torch.full((Q,), float("-inf"), device=device, dtype=torch.float32)
            l_state = torch.zeros((Q,), device=device, dtype=torch.float32)
            o_state = torch.zeros((Q, V_), device=device, dtype=torch.float32)

            for chunk_start in range(0, spec.M, spec.chunk_size):
                chunk_end = min(chunk_start + spec.chunk_size, spec.M)
                k_chunk, v_chunk = _generate_chunk_on_gpu(spec, chunk_start, chunk_end)

                if spec.use_int8_keys:
                    # Per-chunk INT8 quantize on GPU (row-max scale).
                    k_f32 = k_chunk.to(torch.float32)
                    row_max = k_f32.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
                    scale = row_max / 127.0
                    k_i8 = torch.round(k_f32 / scale).clamp_(-127, 127).to(torch.int8)
                    del k_f32
                    k_use = k_i8.to(torch.float32) * scale
                    del k_i8, scale
                else:
                    k_use = k_chunk.to(torch.float32)

                v_use = v_chunk.to(torch.float32)
                del k_chunk, v_chunk

                # Cosine sims (Q, chunk).
                k_normed = k_use / k_use.norm(dim=-1, keepdim=True).clamp_min(1e-9)
                sims = q_normed @ k_normed.T
                logits = beta * sims
                chunk_max = logits.max(dim=-1).values
                m_new = torch.maximum(m_state, chunk_max)
                s = torch.exp(m_state - m_new)
                exp_logits = torch.exp(logits - m_new.unsqueeze(-1))
                l_state = l_state * s + exp_logits.sum(dim=-1)
                o_state = o_state * s.unsqueeze(-1) + exp_logits @ v_use
                m_state = m_new
                del k_use, v_use, k_normed, sims, logits, exp_logits

            readout = o_state / l_state.unsqueeze(-1).clamp_min(1e-30)

        else:
            # Hebbian: W = (vals.T @ keys) / N; readout = queries @ W.T
            W = torch.zeros(spec.V, spec.N, dtype=torch.float32, device=device)
            for chunk_start in range(0, spec.M, spec.chunk_size):
                chunk_end = min(chunk_start + spec.chunk_size, spec.M)
                k_chunk, v_chunk = _generate_chunk_on_gpu(spec, chunk_start, chunk_end)
                k_f32 = k_chunk.to(torch.float32)
                v_f32 = v_chunk.to(torch.float32)
                del k_chunk, v_chunk
                W.addmm_(v_f32.T, k_f32, alpha=1.0, beta=1.0)
                del k_f32, v_f32
            W.div_(float(spec.N))
            readout = queries.to(torch.float32) @ W.T
            del W

        # Force sync so util sampler sees kernel completion before stopping.
        if device.type == "cuda":
            torch.cuda.synchronize(device)
    finally:
        util.stop()

    wall_s = time.time() - t0
    gpu_mem_peak_mb = 0.0
    if device.type == "cuda":
        gpu_mem_peak_mb = float(torch.cuda.max_memory_allocated(device) / 1e6)

    telemetry = {
        "wall_s": float(wall_s),
        "gpu_util_mean_pct": float(util.mean_pct()),
        "n_util_samples": int(util.n_samples()),
        "util_source": util.source(),
        "gpu_mem_peak_mb": float(gpu_mem_peak_mb),
        "mode": mode,
        "M": int(spec.M),
        "N": int(spec.N),
        "V": int(spec.V),
        "chunk_size": int(spec.chunk_size),
        "use_int8_keys": bool(spec.use_int8_keys),
    }
    return readout, v_target, telemetry


__all__ = [
    "GpuGenSpec",
    "GpuUtilSampler",
    "gpu_generated_streaming_readout",
]
