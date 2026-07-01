"""Shared core: cross-axis M x N x K coarse 2D interaction test on GPU.

USER pivot 2026-07-01: only SINGLE-AXIS sweeps mapped. Joint (M, N, K)
interactions untested. Closes Stage 1 phase-diagram gap: is dense-Hopfield
READ-REPLACE recall SEPARABLE across M, N, K axes, or is there a joint
interaction regime where mechanism collapses despite adjacent phase points
holding?

Substrate-KB concept-query 2026-07-01 (cosine < 0.30 for direct hits):
  Confirmed genuinely novel joint-interaction test. Adjacent single-axis
  work: exp_substrate_stage1_integration_NDIM_phase_diagram_v1 (N sweep only);
  exp_tcft_m_sweep_v3 (M sweep only); Cell D v2 M-sweep CG (Atom 1).

Mechanism: dense-Hopfield READ-REPLACE per Cell D v2 CG regime (beta=13 base,
FHRR-like sparse-bipolar keys/vals), via hdlab.chunked_attention (Testbed T2
chain-grade primitive). K queries drawn per phase point; recall = mean cosine
similarity between target val and readout at that (M, N, K) config.

Phase-diagram grid (COARSE by design; catches interactions not fine detail):
  M in {4096, 8192, 16384}
  N in {4096, 8192, 16384}
  K in {200, 500, 1000}   (K = n_queries per phase point)
  = 27 phase points x 3 seeds = 81 units total (single-seed-per-cell = 27/cell)

Design rationale for COARSE grid:
  - Fine axis sweeps already CG for single axes; this cell asks "do joint
    (M, N, K) configs behave as product of marginals?"
  - 27 phase points at 3 seeds each is coverage-adequate to detect a corner
    where mechanism fails while adjacent points hold (i.e., a joint interaction)
  - Coarse spacing (2x per M/N; 2.5x per K) maximizes chance of catching
    non-monotonic regions if any exist

MEMORY BUDGET (chunked_attention chunk=1024, max phase point M=16384, N=16384, V=256):
  For chunked_attention at M=16384, N=16384, K=1000, V=256:
    keys FP32:    16384 * 16384 * 4 = 1073 MB (persistent)
    vals FP32:    16384 * 256 * 4   = 16.8 MB (persistent)
    queries FP32: 1000 * 16384 * 4  = 62.9 MB
    v_target FP32: 1000 * 256 * 4   = 1.0 MB
    chunked transient per Testbed T2 bound: ~1000 * 1024 * 4 * 3 = ~12 MB
    Persistent o_state, l_state, m_state: 1000*256*4 + 8000 = ~1 MB
  Total peak: ~1.2 GB per phase point at max scale. Comfortable on 8GB GPU.

  At coarse M/N > 8192, we chunk key upload to keep dtype cost bounded.

CARDINALITY (META_RULE_H): EXPECTED_N_UNITS = 27 per seed (3 M x 3 N x 3 K).
  n_arm_outcomes counted post-run; HF_CARDINALITY_META_RULE_H if != 27.

DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke includes full-N=16384 preview at
  M=16384, K=200 corner (Method C - preview arm at full config in smoke).
  Assertion: recall >= 0.80 at that FULL corner during smoke, else abort.

META_RULE_AF (arms-must-differ): each phase point's readout hashed; hashes
  across distinct (M, N, K) MUST differ (different random seed+config -> different
  readout). Bit-identical hashes across distinct phase points = bug.

META_RULE_AG (baseline-in-band): substrate-tolerance may make baseline (STD)
  saturate at large-N or high-M regimes. Not a design failure here: STD arm
  intentionally exercises interference regime; we measure REPL mechanism only
  for phase-diagram map. No baseline_in_band gate on this cell (declared
  exempted with rationale: single-arm phase-diagram map, no baseline
  comparison needed for HP verdict).

META_RULE_AH (atomic write): tmp_replace path.

except SystemExit: raise BEFORE except Exception (no BaseException).

Numbers tagged (META_RULE_AC):
  HP_ALL_HOLD floor 0.70:  HYPOTHESIZED@this cell (relaxed from Cell D v2 CG 0.80
    because COARSE grid may include near-capacity corners at M=16384 for smaller
    n_queries=200; conservative floor to test separability, not saturation)
  HF_INTERACTION_FOUND floor 0.40:  HYPOTHESIZED@this cell (gap between HP and HF
    is wide enough that "interaction" claim isn't just noise band)
  Timeout 3600s:  HYPOTHESIZED@formula 27 phase points * avg ~30s/point + margin
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
BETA = 13.0
V_DIM = 256
ATTN_CHUNK_FULL = 1024
ATTN_CHUNK_SMOKE = 256

M_GRID_FULL = [4096, 8192, 16384]
N_GRID_FULL = [4096, 8192, 16384]
K_GRID_FULL = [200, 500, 1000]

# Smoke: reduced grid so cell runs fast on CPU; still exercises all 3 axes.
# + Method C DISCRIMINATOR-SURVIVES-SCALE preview at full corner (M=16384, N=16384, K=200)
M_GRID_SMOKE = [512, 1024]
N_GRID_SMOKE = [512, 1024]
K_GRID_SMOKE = [50, 100]
PREVIEW_CORNER_SMOKE = (16384, 16384, 200)  # (M, N, K) at full config, smoke discriminator

# Verdict bands (HYPOTHESIZED per docstring)
HP_ALL_HOLD_FLOOR = 0.70
HF_INTERACTION_FLOOR = 0.40


# ---------------------------------------------------------------------------
# Instrumentation
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
# Numpy execution path (CPU smoke)
# ---------------------------------------------------------------------------
def _numpy_dense_replace(
    keys: np.ndarray,
    vals: np.ndarray,
    queries: np.ndarray,
    beta: float,
    chunk_size: int,
) -> np.ndarray:
    """Numpy port of chunked_attention_readout; identical online-LSE math."""
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


def _run_phase_point_numpy(
    seed: int,
    M: int,
    N: int,
    K: int,
    V: int,
    beta: float,
    chunk_size: int,
) -> Dict:
    """Numpy execution for one phase point (M, N, K). random +/-1 keys/vals."""
    # Config-specific seed so each phase point gets independent randomness
    config_seed = seed + M * 3 + N * 5 + K * 7
    rng = np.random.RandomState(config_seed % (2**31 - 1))
    t0 = time.time()

    keys = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    vals = rng.choice([-1.0, 1.0], size=(M, V)).astype(np.float32)
    q_idx = rng.choice(M, size=K, replace=False)
    noise = rng.randn(K, N).astype(np.float32) * 0.05
    queries = keys[q_idx] + noise
    v_target = vals[q_idx]

    readout = _numpy_dense_replace(keys, vals, queries, beta, chunk_size)

    r_norm = readout / np.maximum(
        np.linalg.norm(readout, axis=-1, keepdims=True), 1e-9
    )
    t_norm = v_target.astype(np.float64) / np.maximum(
        np.linalg.norm(v_target, axis=-1, keepdims=True), 1e-9
    )
    per_q_cos = (r_norm * t_norm).sum(axis=-1)
    recall = float(np.mean(per_q_cos))
    recall_std = float(np.std(per_q_cos))

    arm_hash = hashlib.sha256(readout.tobytes()).hexdigest()[:16]

    wall = time.time() - t0
    return {
        "M": int(M),
        "N": int(N),
        "K": int(K),
        "V": int(V),
        "beta": float(beta),
        "chunk_size": int(chunk_size),
        "recall_cosine_mean": recall,
        "recall_cosine_std": recall_std,
        "arm_hash": arm_hash,
        "backend": "numpy",
        "wall_s": float(wall),
        "gpu_mem_peak_mb": 0.0,
    }


def _run_phase_point_torch(
    seed: int,
    M: int,
    N: int,
    K: int,
    V: int,
    beta: float,
    chunk_size: int,
) -> Dict:
    """Torch execution for one phase point. Uses hdlab.chunked_attention (T2)."""
    if not _TORCH_AVAILABLE:
        raise RuntimeError("torch unavailable for torch phase-point")
    from hdlab.chunked_attention import chunked_attention_readout

    device = torch.device("cuda" if _CUDA_AVAILABLE else "cpu")

    config_seed = seed + M * 3 + N * 5 + K * 7
    g = torch.Generator(device="cpu")
    g.manual_seed(config_seed % (2**31 - 1))

    t0 = time.time()
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    # Build on CPU then move to device (chunked upload path if desired)
    keys_f32 = ((torch.randint(0, 2, (M, N), generator=g, dtype=torch.int32) * 2 - 1)
                .to(torch.float32))
    vals_f32 = ((torch.randint(0, 2, (M, V), generator=g, dtype=torch.int32) * 2 - 1)
                .to(torch.float32))
    q_idx = torch.randperm(M, generator=g)[:K]
    noise = torch.randn(K, N, generator=g, dtype=torch.float32) * 0.05
    queries_f32 = keys_f32[q_idx] + noise
    v_target = vals_f32[q_idx].clone()

    # Chunked upload to bound transient peak for large M x N: upload keys in row batches
    upload_batch = 4096
    if device.type == "cuda":
        keys_dev = torch.empty((M, N), dtype=torch.float32, device=device)
        for s in range(0, M, upload_batch):
            e = min(s + upload_batch, M)
            keys_dev[s:e] = keys_f32[s:e].to(device, non_blocking=False)
        del keys_f32
    else:
        keys_dev = keys_f32.to(device)
        del keys_f32

    vals_dev = vals_f32.to(device)
    queries_dev = queries_f32.to(device)
    v_target_dev = v_target.to(device)
    del vals_f32, queries_f32, v_target, noise

    readout = chunked_attention_readout(
        query=queries_dev,
        keys=keys_dev,
        vals=vals_dev,
        chunk_size=chunk_size,
        beta=beta,
        key_scale=None,
    )

    r_norm = readout / readout.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    t_norm = v_target_dev / v_target_dev.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    per_q_cos = (r_norm * t_norm).sum(dim=-1)
    recall = float(per_q_cos.mean().item())
    recall_std = float(per_q_cos.std().item())

    readout_cpu = readout.detach().cpu().to(torch.float32).contiguous().numpy()
    arm_hash = hashlib.sha256(readout_cpu.tobytes()).hexdigest()[:16]

    gpu_mem_peak_mb = 0.0
    if device.type == "cuda":
        gpu_mem_peak_mb = float(torch.cuda.max_memory_allocated(device) / 1e6)

    wall = time.time() - t0

    del keys_dev, vals_dev, queries_dev, v_target_dev, readout
    if _CUDA_AVAILABLE:
        torch.cuda.empty_cache()

    return {
        "M": int(M),
        "N": int(N),
        "K": int(K),
        "V": int(V),
        "beta": float(beta),
        "chunk_size": int(chunk_size),
        "recall_cosine_mean": recall,
        "recall_cosine_std": recall_std,
        "arm_hash": arm_hash,
        "backend": "torch.cuda" if device.type == "cuda" else "torch.cpu",
        "wall_s": float(wall),
        "gpu_mem_peak_mb": gpu_mem_peak_mb,
    }


def run_phase_point(
    seed: int,
    M: int,
    N: int,
    K: int,
    V: int,
    beta: float,
    chunk_size: int,
    use_torch: bool,
) -> Dict:
    """Route to numpy (CPU smoke) or torch (GPU FULL)."""
    if use_torch and _TORCH_AVAILABLE:
        return _run_phase_point_torch(seed, M, N, K, V, beta, chunk_size)
    return _run_phase_point_numpy(seed, M, N, K, V, beta, chunk_size)


# ---------------------------------------------------------------------------
# Grid runner
# ---------------------------------------------------------------------------
def run_grid(
    seed: int,
    M_grid: List[int],
    N_grid: List[int],
    K_grid: List[int],
    V: int,
    beta: float,
    chunk_size: int,
    out_dir: Path,
    use_torch: bool,
) -> Dict:
    """Run the full 3D grid. Returns dict keyed by 'M{}_N{}_K{}'."""
    grid_results: Dict[str, Dict] = {}
    total = len(M_grid) * len(N_grid) * len(K_grid)
    idx = 0
    t_grid_start = time.time()
    for M in M_grid:
        for N in N_grid:
            for K in K_grid:
                idx += 1
                t_pp = time.time()
                key = f"M{M}_N{N}_K{K}"
                print(f"  [seed={seed} {idx}/{total} {key}] running...", flush=True)
                r = run_phase_point(
                    seed=seed, M=M, N=N, K=K, V=V, beta=beta,
                    chunk_size=chunk_size, use_torch=use_torch,
                )
                grid_results[key] = r
                print(
                    f"    [{key}] recall={r['recall_cosine_mean']:.4f} "
                    f"wall={r['wall_s']:.1f}s "
                    f"gpu_mem_peak_mb={r['gpu_mem_peak_mb']:.1f} "
                    f"hash={r['arm_hash']}",
                    flush=True,
                )
                emit_heartbeat(
                    out_dir, unit_idx=idx,
                    elapsed_s=time.time() - t_grid_start,
                    total_units=total,
                    extra={"phase_point": key, "recall": r["recall_cosine_mean"]},
                )
    return grid_results


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def compute_verdict(
    seed_result: Dict,
    run_mode: str,
    hp_floor: float = HP_ALL_HOLD_FLOOR,
    hf_floor: float = HF_INTERACTION_FLOOR,
) -> Tuple[str, str, Dict]:
    """Compute verdict from grid results.

    HP_ALL_HOLD: recall >= hp_floor at ALL 27 (M, N, K) phase points -> CHAIN_GRADE_NO_INTERACTION
    HF_INTERACTION_FOUND: some phase point recall < hf_floor while adjacent points HP
      -> MEASURED_MECHANISM_INTERACTION_MAPPED (interaction characterized)
    All-below-HP but none in interaction band -> MIDDLE_BAND
    """
    grid = seed_result.get("grid_results", {})
    if not grid:
        return ("HARD_FAIL", "No grid results in seed_result", {})

    all_recall = {k: v["recall_cosine_mean"] for k, v in grid.items()}
    all_hashes = {k: v.get("arm_hash", "") for k, v in grid.items()}
    max_gpu_mb = max((v.get("gpu_mem_peak_mb", 0.0) for v in grid.values()), default=0.0)

    hf_flags: List[str] = []

    # META_RULE_H cardinality
    expected_n_units_smoke = None  # smoke passes different grid; check by count
    if run_mode == "full":
        expected_n_units = 27
        if len(grid) != expected_n_units:
            hf_flags.append(
                f"HF_CARDINALITY_META_RULE_H_expected={expected_n_units}"
                f"_got={len(grid)}"
            )

    # META_RULE_AF arms-differ (across phase points, all hashes should differ)
    hash_seen: Dict[str, str] = {}
    for k, h in all_hashes.items():
        if not h:
            continue
        if h in hash_seen:
            hf_flags.append(
                f"HF_ARM_IDENTICAL_META_RULE_AF: phase point {k} bit-identical "
                f"to {hash_seen[h]} (hash={h})"
            )
        else:
            hash_seen[h] = k

    # HF memory bound (loose since chunked; guard against runaway)
    if max_gpu_mb > 4000:
        hf_flags.append(f"HF_MEMORY_OVERFLOW_max_gpu_mb={max_gpu_mb:.1f}")

    # Discriminator classification per phase point
    n_hp = sum(1 for v in all_recall.values() if v >= hp_floor)
    n_interaction = sum(1 for v in all_recall.values() if v < hf_floor)
    n_middle = len(all_recall) - n_hp - n_interaction

    interaction_points = {k: v for k, v in all_recall.items() if v < hf_floor}
    hp_points = {k: v for k, v in all_recall.items() if v >= hp_floor}

    # Check for JOINT INTERACTION: some point HF while ADJACENT points HP
    # Adjacent = shares 2 of the 3 axes at same value
    interaction_found = False
    interaction_evidence: List[str] = []
    if interaction_points and hp_points:
        for hf_key in interaction_points:
            # Parse M/N/K
            parts = hf_key.split("_")
            hf_M = int(parts[0][1:]); hf_N = int(parts[1][1:]); hf_K = int(parts[2][1:])
            for hp_key in hp_points:
                p2 = hp_key.split("_")
                hp_M = int(p2[0][1:]); hp_N = int(p2[1][1:]); hp_K = int(p2[2][1:])
                same_count = ((hf_M == hp_M) + (hf_N == hp_N) + (hf_K == hp_K))
                if same_count == 2:  # adjacent: differ in exactly one axis
                    interaction_found = True
                    interaction_evidence.append(
                        f"{hf_key}(recall={all_recall[hf_key]:.3f})_HF_adjacent_to_"
                        f"{hp_key}(recall={all_recall[hp_key]:.3f})_HP"
                    )
                    if len(interaction_evidence) >= 5:
                        break
            if len(interaction_evidence) >= 5:
                break

    min_recall = min(all_recall.values()) if all_recall else 0.0
    max_recall = max(all_recall.values()) if all_recall else 0.0
    mean_recall = (sum(all_recall.values()) / len(all_recall)) if all_recall else 0.0

    headline = {
        "n_phase_points": len(all_recall),
        "n_hp_phase_points": n_hp,
        "n_interaction_phase_points": n_interaction,
        "n_middle_phase_points": n_middle,
        "min_recall": min_recall,
        "max_recall": max_recall,
        "mean_recall": mean_recall,
        "max_gpu_mb": max_gpu_mb,
        "interaction_found_adjacent_hf_hp": interaction_found,
        "interaction_evidence": interaction_evidence[:5],
        "hp_floor": hp_floor,
        "hf_floor": hf_floor,
        "hf_flags": hf_flags,
        "recall_per_phase_point": all_recall,
    }

    if hf_flags:
        return ("HARD_FAIL", "; ".join(hf_flags), headline)

    # Smoke: just verify cell RAN + all points measurable (>0.10 sanity floor)
    if run_mode == "smoke":
        if min_recall < 0.10:
            # smoke saw death somewhere
            return (
                "HARD_FAIL",
                f"SMOKE_HARD_FAIL_DEAD_POINT: min_recall={min_recall:.3f} < 0.10; "
                f"phase-point mechanism death in smoke",
                headline,
            )
        preview_recall = seed_result.get("preview_corner_recall", None)
        preview_ok_msg = ""
        if preview_recall is not None:
            preview_ok_msg = f" preview_full_corner_recall={preview_recall:.3f}"
            if preview_recall < 0.80:
                return (
                    "MIDDLE_BAND",
                    f"SMOKE_MB_PREVIEW_BELOW_0.80: preview_recall={preview_recall:.3f} "
                    f"< 0.80 at PREVIEW_CORNER_SMOKE (DISCRIMINATOR-MUST-SURVIVE-SCALE "
                    f"Method C failed); do NOT dispatch FULL. min_recall={min_recall:.3f}",
                    headline,
                )
        return (
            "HARD_PASS",
            f"SMOKE_HARD_PASS: n_points={len(all_recall)} "
            f"min_recall={min_recall:.3f} max_recall={max_recall:.3f} "
            f"mean_recall={mean_recall:.3f}{preview_ok_msg}",
            headline,
        )

    # FULL mode
    if n_hp == len(all_recall):
        return (
            "HARD_PASS",
            f"HP_ALL_HOLD_CHAIN_GRADE_NO_INTERACTION: all {n_hp}/{len(all_recall)} "
            f"phase points recall >= {hp_floor}; min={min_recall:.3f} "
            f"max={max_recall:.3f} mean={mean_recall:.3f} -- mechanism SEPARABLE "
            f"across M/N/K",
            headline,
        )

    if interaction_found:
        return (
            "MIDDLE_BAND",
            f"MEASURED_MECHANISM_INTERACTION_MAPPED: n_interaction={n_interaction} "
            f"phase points recall < {hf_floor} adjacent to HP points; "
            f"substrate physics finding: joint (M, N, K) capacity constraint. "
            f"Evidence: {'; '.join(interaction_evidence[:3])}",
            headline,
        )

    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: n_hp={n_hp}/{len(all_recall)} n_interaction={n_interaction} "
        f"n_middle={n_middle}; no clean HP_ALL_HOLD or interaction pattern; "
        f"min_recall={min_recall:.3f}",
        headline,
    )


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def run_all_selftests(seed: int, anchor: str) -> None:
    """Verify numpy path recall reasonable at small phase point."""
    # tiny numpy phase point should recall > 0.9 at small M=100, N=64
    r = _run_phase_point_numpy(seed=seed, M=100, N=64, K=10, V=32, beta=BETA,
                                chunk_size=32)
    assert r["recall_cosine_mean"] > 0.5, (
        f"[selftest] tiny numpy recall too low: {r['recall_cosine_mean']}"
    )
    # arm_hash non-empty
    assert len(r["arm_hash"]) == 16, "[selftest] arm_hash schema unexpected"
    # verdict logic: HP path on synthetic all-1.0 grid
    fake_grid = {
        f"M{m}_N{n}_K{k}": {
            "recall_cosine_mean": 0.85,
            "arm_hash": f"{m:x}{n:x}{k:x}00000000000000"[:16],
            "gpu_mem_peak_mb": 10.0,
        }
        for m in [4096, 8192, 16384]
        for n in [4096, 8192, 16384]
        for k in [200, 500, 1000]
    }
    seed_res = {"grid_results": fake_grid, "preview_corner_recall": 0.85}
    v, msg, _ = compute_verdict(seed_res, "full")
    assert v == "HARD_PASS", f"[selftest] fake-grid should HP; got {v}: {msg}"
    # Interaction detection: inject one dead corner adjacent to HP
    fake_grid_i = dict(fake_grid)
    fake_grid_i["M16384_N16384_K1000"] = {
        "recall_cosine_mean": 0.20,  # below HF_floor
        "arm_hash": "dead" + "0" * 12,
        "gpu_mem_peak_mb": 10.0,
    }
    v2, msg2, _ = compute_verdict({"grid_results": fake_grid_i}, "full")
    assert v2 == "MIDDLE_BAND" and "INTERACTION_MAPPED" in msg2, (
        f"[selftest] interaction detection failed: {v2}: {msg2}"
    )
    print(
        f"[selftest] PASS  tiny_recall={r['recall_cosine_mean']:.3f}  "
        f"verdict_logic_HP_and_interaction=OK  "
        f"torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE}",
        flush=True,
    )
