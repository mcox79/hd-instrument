"""Shared core: stage2 Dim F batched QPS at commercial M validation.

Motivation:
    Sonnet Dim F drill (notes/research_dim_f_throughput_scaling_batch_qps_2026-07-02.md)
    predicted batch B=64 throughput at M=500k = ~19,000 QPS (32x over sequential
    ~590 QPS). Cell empirically validates the batched-scaling prediction that
    determines M3 Phase 1 100-user shard viability.

Design:
    - N=8192, M=500,000, V=256, backend=torch.cuda, INT8 keys (matches hippo v5
      chain-grade regime at M=500k for direct QPS comparison).
    - Sweep batch_size in {1, 4, 16, 64, 256} (5 conditions).
    - Reuse hdlab/gpu_generated_streaming_attention primitive
      (gpu_generated_streaming_readout, mode='attention'). Each dispatch =
      one invocation of the primitive with n_queries=batch_size.
    - Warmup 20 dispatches; measure 200 dispatches per B; report:
        total_wall_s, effective_qps, memory_peak_mb, per-batch p50/p95/p99.

Prior-work check (substrate-KB, 2026-07-02):
    Q: 'batched QPS throughput scaling streaming attention batch size dispatch'
    top hits cosine 0.31-0.37 = generic LLM batching notes and encoder pre-test.
    NONE measure substrate primitive batched QPS. Cell genuinely novel.

FALSIFIABLE gates:
    HP_BATCH_LINEAR:        QPS(B=64) / QPS(B=1) >= 32
    HP_100USER_SHARD:       QPS(B=64) >= 3000
    HP_MEMORY_CONTROLLED:   memory_peak_mb <= 200 at B=256
    HP_TAIL_CONTROLLED:     p99/p50 < 3.0 at every B
    HF_BATCH_PLATEAUS_EARLY:QPS(B=64) / QPS(B=1) < 8
    HF_1000USER_INFEASIBLE: QPS(B=256) < 5000
    HF_MECHANISM_DEATH:     recall_cosine_mean < 0.80 at any B
    HF_MEMORY_BLOWUP:       memory_peak_mb > 1000 at any B
    HF_CARDINALITY:         n_arm_outcomes != EXPECTED_N_UNITS (per seed = 5)

CARDINALITY (META_RULE_H): EXPECTED_N_UNITS = 5 per seed cell (5 batch sizes).

DISCRIMINATOR-MUST-SURVIVE-SCALE:
    Smoke runs at the SAME full-N=8192 / M=500k regime as full. Timing
    measurement is by construction at the target scale; smoke and full differ
    only in seed count.

ASCII-only. tmp+os.replace (META_RULE_AH). hash-test (META_RULE_AF).
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


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
M_FULL = 500_000
BETA_BASE = 13.0
M_REF = 100_000
ATTN_CHUNK_FULL = 1024

# Batch sizes swept.
BATCH_SIZES_FULL: List[int] = [1, 4, 16, 64, 256]

# Warmup + measurement dispatch counts per batch size.
N_WARMUP_FULL = 20
N_MEASURE_FULL = 200

# Smoke uses the SAME regime as full — timing measurement is by construction
# at target scale. Difference: smoke does fewer measurement dispatches so it
# completes in ~2-3min instead of ~20min. This satisfies
# DISCRIMINATOR-MUST-SURVIVE-SCALE (smoke IS at full-N / full-M).
BATCH_SIZES_SMOKE: List[int] = [1, 4, 16, 64, 256]
N_WARMUP_SMOKE = 5
N_MEASURE_SMOKE = 30

# HP / HF thresholds (all THEORETICAL@Sonnet_drill / M3 deployment requirements).
HP_BATCH_LINEAR_MIN_SPEEDUP = 32.0   # QPS(B=64)/QPS(B=1) >= 32
HP_100USER_SHARD_QPS_MIN = 3000.0    # QPS(B=64) >= 3000
HP_MEMORY_CONTROLLED_MB_MAX = 200.0  # memory_peak_mb <= 200 at B=256
HP_TAIL_P99_P50_RATIO_MAX = 3.0      # p99/p50 < 3.0 at every B

HF_BATCH_PLATEAUS_EARLY_MAX_SPEEDUP = 8.0   # QPS(B=64)/QPS(B=1) < 8
HF_1000USER_INFEASIBLE_QPS_MAX = 5000.0     # QPS(B=256) < 5000
HF_MECHANISM_DEATH_RECALL_MIN = 0.80        # any B recall < 0.80
HF_MEMORY_BLOWUP_MB_MAX = 1000.0            # any B memory_peak_mb > 1000

# Positive-control (Gate D) reproducer at B=1 vs hippo v5 M=500k baseline.
POSITIVE_CONTROL_RECALL_MIN = 0.80


def adaptive_beta(M: int, m_ref: int = M_REF, beta_base: float = BETA_BASE) -> float:
    """Adaptive beta per M. THEORETICAL@log2-scaling preserves logit_gap
    (matches hippo v5 core's adaptive_beta so batched-B=1 reproduces v5 recall)."""
    if M <= m_ref:
        return beta_base
    return beta_base * math.log2(M) / math.log2(m_ref)


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
# One batched-QPS arm: sweeps N_MEASURE dispatches at fixed batch_size.
# ---------------------------------------------------------------------------
def _dispatch_seed(seed: int, batch_size: int, dispatch_idx: int) -> int:
    """Deterministic per-dispatch master seed."""
    return (seed * 2_147_483_647 + batch_size * 100003 + dispatch_idx * 31 + 1) & 0xFFFFFFFF


def run_one_batch_size(
    seed: int, batch_size: int, M: int, N: int, V: int,
    chunk_size: int, n_warmup: int, n_measure: int, out_dir: Path,
) -> Dict:
    """Run n_warmup + n_measure primitive dispatches at fixed batch_size.

    Each dispatch = one gpu_generated_streaming_readout call with
    n_queries=batch_size. Records per-dispatch wall_s + aggregate QPS +
    peak memory.
    """
    if not _TORCH_AVAILABLE:
        raise RuntimeError("torch required for batched QPS cell")

    from hdlab.gpu_generated_streaming_attention import (
        GpuGenSpec, gpu_generated_streaming_readout,
    )

    device = torch.device("cuda" if _CUDA_AVAILABLE else "cpu")
    beta = adaptive_beta(M)

    print(
        f"    [B={batch_size} M={M}] warmup={n_warmup} measure={n_measure} "
        f"beta={beta:.2f} device={device.type}",
        flush=True,
    )

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.empty_cache()

    # ── Warmup (JIT / cudnn algo selection) ─────────────────────────────────
    for w in range(n_warmup):
        spec_w = GpuGenSpec(
            arm_seed=_dispatch_seed(seed, batch_size, -1 - w),
            M=M, N=N, V=V, n_queries=batch_size,
            chunk_size=chunk_size, device=device, query_noise_std=0.05,
            use_int8_keys=True,
        )
        r_w, vt_w, _ = gpu_generated_streaming_readout(
            spec_w, mode="attention", beta=beta,
        )
        del r_w, vt_w
    if device.type == "cuda":
        torch.cuda.synchronize(device)
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)

    # ── Measurement ─────────────────────────────────────────────────────────
    per_dispatch_wall_s: List[float] = []
    recall_samples: List[float] = []
    arm_hashes: List[str] = []

    t_all_start = time.time()
    for d in range(n_measure):
        spec = GpuGenSpec(
            arm_seed=_dispatch_seed(seed, batch_size, d),
            M=M, N=N, V=V, n_queries=batch_size,
            chunk_size=chunk_size, device=device, query_noise_std=0.05,
            use_int8_keys=True,
        )
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        t0 = time.time()
        readout, v_target, tel = gpu_generated_streaming_readout(
            spec, mode="attention", beta=beta,
        )
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        wall = time.time() - t0
        per_dispatch_wall_s.append(float(wall))

        # Recall sample (positive control across all B; catches
        # HF_MECHANISM_DEATH).
        r_norm = readout / readout.norm(dim=-1, keepdim=True).clamp_min(1e-9)
        t_norm = v_target.to(torch.float32) / v_target.to(torch.float32).norm(
            dim=-1, keepdim=True
        ).clamp_min(1e-9)
        per_q_cos = (r_norm * t_norm).sum(dim=-1)
        recall_samples.append(float(per_q_cos.mean().item()))

        if d < 3:
            # Only hash first 3 dispatches (bounded footprint for arm_hash test).
            readout_cpu = readout.detach().cpu().to(torch.float32).contiguous().numpy()
            arm_hashes.append(
                hashlib.sha256(readout_cpu.tobytes()).hexdigest()[:16]
            )
        del readout, v_target
    t_all_end = time.time()
    total_wall_s = t_all_end - t_all_start

    gpu_mem_peak_mb = 0.0
    if device.type == "cuda":
        gpu_mem_peak_mb = float(torch.cuda.max_memory_allocated(device) / 1e6)

    # Effective QPS = total queries / total wall.
    total_queries = n_measure * batch_size
    effective_qps = float(total_queries) / max(total_wall_s, 1e-9)

    # Per-batch percentiles (over per-dispatch wall_s samples).
    wall_np = np.array(per_dispatch_wall_s, dtype=np.float64)
    p50 = float(np.percentile(wall_np, 50))
    p95 = float(np.percentile(wall_np, 95))
    p99 = float(np.percentile(wall_np, 99))
    p50_p99_ratio = p99 / max(p50, 1e-9)

    recall_mean = float(np.mean(recall_samples)) if recall_samples else 0.0
    recall_std = float(np.std(recall_samples)) if recall_samples else 0.0

    # arm_hash = digest across first 3 dispatch hashes (batch-varying by seed).
    combined = "".join(arm_hashes).encode("utf-8") if arm_hashes else b""
    arm_hash = hashlib.sha256(combined).hexdigest()[:16] if combined else "n/a"

    result = {
        "arm_name": f"B={batch_size}",
        "seed": int(seed),
        "batch_size": int(batch_size),
        "M": int(M), "N": int(N), "V": int(V),
        "chunk_size": int(chunk_size),
        "n_warmup": int(n_warmup),
        "n_measure": int(n_measure),
        "beta": float(beta),
        "backend": "torch.cuda" if device.type == "cuda" else "torch.cpu",
        "int8_keys": True,
        "total_wall_s": float(total_wall_s),
        "total_queries": int(total_queries),
        "effective_qps": float(effective_qps),
        "recall_cosine_mean": recall_mean,
        "recall_cosine_std": recall_std,
        "per_dispatch_wall_p50": p50,
        "per_dispatch_wall_p95": p95,
        "per_dispatch_wall_p99": p99,
        "per_dispatch_wall_p99_p50_ratio": float(p50_p99_ratio),
        "gpu_mem_peak_mb": gpu_mem_peak_mb,
        "arm_hash": arm_hash,
    }

    print(
        f"    [B={batch_size} M={M}] qps={effective_qps:.1f} wall={total_wall_s:.2f}s "
        f"recall={recall_mean:.3f} peak_mb={gpu_mem_peak_mb:.1f} "
        f"p50={p50*1000:.1f}ms p99={p99*1000:.1f}ms tail_ratio={p50_p99_ratio:.2f}",
        flush=True,
    )
    return result


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------
def compute_verdict(
    per_arm: List[Dict], run_mode: str, expected_n_units: int,
) -> Tuple[str, str, Dict]:
    """Return (verdict, verdict_msg, headline_dict).

    HP fires iff ALL 4 HP gates satisfied.
    HF fires if ANY HF gate hits.
    Otherwise MIDDLE_BAND with speedup ratio surfaced.
    """
    n_arm_outcomes = len(per_arm)
    if n_arm_outcomes != expected_n_units:
        return (
            "HARD_FAIL",
            (
                f"HF_CARDINALITY_META_RULE_H_expected={expected_n_units}_"
                f"got={n_arm_outcomes}"
            ),
            {"n_arm_outcomes": n_arm_outcomes, "expected": expected_n_units},
        )

    by_B: Dict[int, Dict] = {int(a["batch_size"]): a for a in per_arm}
    qps_by_B = {b: a["effective_qps"] for b, a in by_B.items()}
    mem_by_B = {b: a["gpu_mem_peak_mb"] for b, a in by_B.items()}
    recall_by_B = {b: a["recall_cosine_mean"] for b, a in by_B.items()}
    tail_by_B = {b: a["per_dispatch_wall_p99_p50_ratio"] for b, a in by_B.items()}
    arm_hashes = [(int(a["batch_size"]), a["arm_hash"]) for a in per_arm]

    hf_flags: List[str] = []
    hp_flags: List[str] = []

    # HF_MECHANISM_DEATH
    for b, r in recall_by_B.items():
        if r < HF_MECHANISM_DEATH_RECALL_MIN:
            hf_flags.append(
                f"HF_MECHANISM_DEATH_B={b}_recall={r:.3f}_below_"
                f"{HF_MECHANISM_DEATH_RECALL_MIN}"
            )

    # HF_MEMORY_BLOWUP
    for b, m in mem_by_B.items():
        if m > HF_MEMORY_BLOWUP_MB_MAX:
            hf_flags.append(
                f"HF_MEMORY_BLOWUP_B={b}_peak_mb={m:.1f}_above_"
                f"{HF_MEMORY_BLOWUP_MB_MAX}"
            )

    # HF_ARM_IDENTICAL (META_RULE_AF): different B must yield different arm_hash
    hash_by_b = {b: h for b, h in arm_hashes}
    keys = sorted(hash_by_b.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            if hash_by_b[keys[i]] == hash_by_b[keys[j]] and hash_by_b[keys[i]] != "n/a":
                hf_flags.append(
                    f"HF_ARM_IDENTICAL_B={keys[i]}_and_B={keys[j]}_"
                    f"META_RULE_AF_VIOLATION"
                )

    # Speedup and HP/HF batch-scaling gates
    speedup_b64_b1 = None
    if 1 in qps_by_B and 64 in qps_by_B and qps_by_B[1] > 0:
        speedup_b64_b1 = qps_by_B[64] / qps_by_B[1]

    if speedup_b64_b1 is not None:
        if speedup_b64_b1 < HF_BATCH_PLATEAUS_EARLY_MAX_SPEEDUP:
            hf_flags.append(
                f"HF_BATCH_PLATEAUS_EARLY_speedup_64_over_1={speedup_b64_b1:.2f}_"
                f"below_{HF_BATCH_PLATEAUS_EARLY_MAX_SPEEDUP}"
            )
        if speedup_b64_b1 >= HP_BATCH_LINEAR_MIN_SPEEDUP:
            hp_flags.append(
                f"HP_BATCH_LINEAR_speedup={speedup_b64_b1:.2f}"
            )

    if 64 in qps_by_B:
        if qps_by_B[64] >= HP_100USER_SHARD_QPS_MIN:
            hp_flags.append(f"HP_100USER_SHARD_qps_B64={qps_by_B[64]:.1f}")

    if 256 in qps_by_B:
        if qps_by_B[256] < HF_1000USER_INFEASIBLE_QPS_MAX:
            hf_flags.append(
                f"HF_1000USER_INFEASIBLE_qps_B256={qps_by_B[256]:.1f}_"
                f"below_{HF_1000USER_INFEASIBLE_QPS_MAX}"
            )

    if 256 in mem_by_B:
        if mem_by_B[256] <= HP_MEMORY_CONTROLLED_MB_MAX:
            hp_flags.append(f"HP_MEMORY_CONTROLLED_peak_mb_B256={mem_by_B[256]:.1f}")

    all_tails_ok = all(t < HP_TAIL_P99_P50_RATIO_MAX for t in tail_by_B.values())
    if all_tails_ok:
        max_tail = max(tail_by_B.values()) if tail_by_B else 0.0
        hp_flags.append(f"HP_TAIL_CONTROLLED_max_p99_p50={max_tail:.2f}")

    headline = {
        "qps_by_B": qps_by_B,
        "mem_by_B": mem_by_B,
        "recall_by_B": recall_by_B,
        "tail_ratio_by_B": tail_by_B,
        "speedup_B64_over_B1": speedup_b64_b1,
        "hp_flags": hp_flags,
        "hf_flags": hf_flags,
        "n_arm_outcomes": n_arm_outcomes,
        "expected_n_units": expected_n_units,
    }

    if hf_flags:
        return ("HARD_FAIL", "; ".join(hf_flags), headline)

    # All 4 HP gates must be present.
    HP_REQUIRED = {"HP_BATCH_LINEAR", "HP_100USER_SHARD", "HP_MEMORY_CONTROLLED",
                   "HP_TAIL_CONTROLLED"}
    hp_fired_names = {f.split("_")[0] + "_" + f.split("_")[1] + "_" + f.split("_")[2]
                      for f in hp_flags if f.startswith("HP_")}
    # Simpler: check each explicitly.
    got_hp_linear = any(f.startswith("HP_BATCH_LINEAR") for f in hp_flags)
    got_hp_100u = any(f.startswith("HP_100USER_SHARD") for f in hp_flags)
    got_hp_mem = any(f.startswith("HP_MEMORY_CONTROLLED") for f in hp_flags)
    got_hp_tail = any(f.startswith("HP_TAIL_CONTROLLED") for f in hp_flags)

    all_hp = got_hp_linear and got_hp_100u and got_hp_mem and got_hp_tail
    if all_hp:
        return ("HARD_PASS", "; ".join(hp_flags), headline)

    return (
        "MIDDLE_BAND",
        (
            f"MB: hp_fired={hp_flags}; "
            f"missing=[linear={got_hp_linear} 100u={got_hp_100u} "
            f"mem={got_hp_mem} tail={got_hp_tail}]"
        ),
        headline,
    )


# ---------------------------------------------------------------------------
# Selftest — must run BEFORE dispatch (formula self-tests + primitive check)
# ---------------------------------------------------------------------------
def run_all_selftests(seed: int, anchor: str) -> None:
    """Selftest per META_RULE_AC."""
    # (a) adaptive_beta parity with hippo v5 core.
    assert abs(adaptive_beta(M_REF) - BETA_BASE) < 1e-9, "adaptive_beta at M_REF wrong"
    assert adaptive_beta(1_000_000) > BETA_BASE, "adaptive_beta should grow with M"

    # (b) verdict logic: hand-crafted HP case
    fake_hp = [
        {"batch_size": 1, "effective_qps": 590.0, "gpu_mem_peak_mb": 100.0,
         "recall_cosine_mean": 0.85, "per_dispatch_wall_p99_p50_ratio": 1.5,
         "arm_hash": "aaaa"},
        {"batch_size": 4, "effective_qps": 2300.0, "gpu_mem_peak_mb": 100.0,
         "recall_cosine_mean": 0.85, "per_dispatch_wall_p99_p50_ratio": 1.5,
         "arm_hash": "bbbb"},
        {"batch_size": 16, "effective_qps": 9000.0, "gpu_mem_peak_mb": 120.0,
         "recall_cosine_mean": 0.85, "per_dispatch_wall_p99_p50_ratio": 1.5,
         "arm_hash": "cccc"},
        {"batch_size": 64, "effective_qps": 19000.0, "gpu_mem_peak_mb": 150.0,
         "recall_cosine_mean": 0.85, "per_dispatch_wall_p99_p50_ratio": 1.8,
         "arm_hash": "dddd"},
        {"batch_size": 256, "effective_qps": 30000.0, "gpu_mem_peak_mb": 180.0,
         "recall_cosine_mean": 0.85, "per_dispatch_wall_p99_p50_ratio": 2.0,
         "arm_hash": "eeee"},
    ]
    v, msg, head = compute_verdict(fake_hp, "full", 5)
    assert v == "HARD_PASS", f"selftest HP case gave {v}: {msg}"

    # (c) HF_MECHANISM_DEATH
    fake_death = list(fake_hp)
    fake_death[3] = dict(fake_death[3])
    fake_death[3]["recall_cosine_mean"] = 0.3
    v, msg, _ = compute_verdict(fake_death, "full", 5)
    assert v == "HARD_FAIL" and "HF_MECHANISM_DEATH" in msg, (
        f"selftest death case wrong: {v} {msg}"
    )

    # (d) HF_BATCH_PLATEAUS_EARLY
    fake_plateau = list(fake_hp)
    fake_plateau[3] = dict(fake_plateau[3])
    fake_plateau[3]["effective_qps"] = 2000.0  # speedup 2000/590 ~= 3.4 < 8
    v, msg, _ = compute_verdict(fake_plateau, "full", 5)
    assert v == "HARD_FAIL" and "HF_BATCH_PLATEAUS_EARLY" in msg, (
        f"selftest plateau case wrong: {v} {msg}"
    )

    # (e) HF_CARDINALITY
    v, msg, _ = compute_verdict(fake_hp[:3], "full", 5)
    assert v == "HARD_FAIL" and "HF_CARDINALITY" in msg, (
        f"selftest cardinality case wrong: {v} {msg}"
    )

    # (f) HF_ARM_IDENTICAL
    fake_dup = list(fake_hp)
    fake_dup[3] = dict(fake_dup[3])
    fake_dup[3]["arm_hash"] = "cccc"  # match B=16 hash
    v, msg, _ = compute_verdict(fake_dup, "full", 5)
    assert v == "HARD_FAIL" and "HF_ARM_IDENTICAL" in msg, (
        f"selftest arm-identical case wrong: {v} {msg}"
    )

    # (g) MIDDLE_BAND (all HF absent, some HP missing)
    fake_mb = list(fake_hp)
    fake_mb[3] = dict(fake_mb[3])
    fake_mb[3]["effective_qps"] = 10000.0  # speedup 10000/590 ~= 17 (not <8, not >=32)
    v, msg, _ = compute_verdict(fake_mb, "full", 5)
    assert v == "MIDDLE_BAND", f"selftest MB case wrong: {v} {msg}"

    print(
        f"[selftest] PASS  adaptive_beta_ref={BETA_BASE} adaptive_1M={adaptive_beta(1_000_000):.2f} "
        f"verdict_HP_ok verdict_death_ok verdict_plateau_ok verdict_cardinality_ok "
        f"verdict_arm_identical_ok verdict_MB_ok "
        f"torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE}",
        flush=True,
    )
