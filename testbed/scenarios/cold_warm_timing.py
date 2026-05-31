"""Scenario: cold_warm_timing (Q4 / E2.4).

Characterizes per-operation latency across phases of a backend's lifetime:
- cold (first ~10 ops): just-instantiated backend, no warm-up
- warming (~ops 11-100): warm-up window; caches priming, JIT warming, etc.
- warm (ops ~100-1000): expected steady-state
- long-running (ops ~1000-2000): sustained operation

What this scenario surfaces:
  1. Cold-start latency multiplier vs warm steady-state (do first 10 ops
     pay a 5x penalty vs op 500?).
  2. Time to reach steady-state (does p50 latency stabilize at op 50? op 200?
     op 1000?).
  3. Backend-specific warmup signatures: FAISS may have first-search JIT,
     substrate may have codebook lazy materialization, dict may have GC
     overhead.

Design:
  - Store M_base items quickly (bulk store, not measured in phases).
  - Run N_probe_ops retrieves against random stored keys.
  - Tag each op with its phase based on its index.
  - Emit per-phase latency distributions (mean, p50, p95, p99) and per-phase
    throughput.

Per-cell progress logging (ASCII-only) + per-phase partial JSON for restart
per feedback_testbed_progress_logging_and_restart.

HARD_PASS substrate:
  cold_to_warm_p50_ratio <= 5.0 (cold start within 5x of warm) AND
  warm_to_long_p50_ratio in [0.85, 1.15] (no drift from warm to long-running).

HARD_PASS baselines:
  cold_to_warm_p50_ratio <= 10.0 AND warm_to_long_p50_ratio in [0.85, 1.15].
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from testbed.api import MemoryBackend


def _first_seed(config: dict) -> int:
    seeds = config.get("seeds", [7])
    return int(seeds[0]) if seeds else 7


def _percentile(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    return float(np.percentile(np.asarray(samples, dtype=np.float64), q))


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] cold_warm_timing: {msg}", flush=True)


def setup(config: dict) -> dict:
    M_base = int(config.get("cold_warm_M_base", config.get("M_base", 2000)))
    N_probe_ops = int(config.get("cold_warm_N_probe_ops", 2000))
    dim = int(config.get("dim", 2048))
    seed = _first_seed(config)
    # Phase boundaries (cumulative). Default: 10, 100, 1000, 2000.
    phase_boundaries = list(config.get("cold_warm_phase_boundaries",
                                        [10, 100, 1000, 2000]))
    if phase_boundaries[-1] < N_probe_ops:
        phase_boundaries = phase_boundaries[:-1] + [N_probe_ops]
    phase_names = list(config.get("cold_warm_phase_names",
                                   ["cold", "warming", "warm", "long_running"]))
    partial_out = config.get("cold_warm_partial_dir",
                              "testbed_data/cold_warm_partial")

    rng = np.random.default_rng(seed + 8400)
    raw = rng.integers(0, 2, size=(M_base, dim), dtype=np.int8).astype(np.float32)
    initial_vecs = raw * 2.0 - 1.0
    initial_ids = [f"cw_init_{i:07d}" for i in range(M_base)]
    # Probe targets: random indices into the live set, drawn ahead of time.
    probe_target_idx = rng.integers(0, M_base, size=N_probe_ops)

    return {
        "initial_ids": initial_ids,
        "initial_vecs": initial_vecs,
        "M_base": M_base,
        "N_probe_ops": N_probe_ops,
        "phase_boundaries": phase_boundaries,
        "phase_names": phase_names,
        "probe_target_idx": probe_target_idx,
        "partial_out": partial_out,
        "seed": seed,
    }


def _phase_for_index(idx: int, phase_boundaries: list[int]) -> int:
    for p, boundary in enumerate(phase_boundaries):
        if idx < boundary:
            return p
    return len(phase_boundaries) - 1


def run(backend: MemoryBackend, data: dict) -> dict:
    initial_ids: list[str] = data["initial_ids"]
    initial_vecs: np.ndarray = data["initial_vecs"]
    M_base = int(data["M_base"])
    N_probe_ops = int(data["N_probe_ops"])
    phase_boundaries: list[int] = data["phase_boundaries"]
    phase_names: list[str] = data["phase_names"]
    probe_target_idx: np.ndarray = data["probe_target_idx"]
    partial_out: str = data["partial_out"]

    is_substrate = (
        backend.name == "substrate"
        or backend.name.startswith("substrate_v")
        or backend.name == "substrate_sharded"
    )

    partial_dir = Path(partial_out)
    partial_dir.mkdir(parents=True, exist_ok=True)

    _log(f"backend={backend.name} M_base={M_base} N_probe_ops={N_probe_ops} "
         f"phase_boundaries={phase_boundaries}")

    # Bulk-store M_base items (warm-up the substrate to the regime we'll probe).
    # NOT included in phase timing -- this is the pre-probe build phase.
    t_build_0 = time.perf_counter_ns()
    chunk = 64
    for i in range(0, M_base, chunk):
        end = min(i + chunk, M_base)
        backend.store_batch(
            [(initial_ids[j], initial_vecs[j], f"cv_init_{j}") for j in range(i, end)]
        )
    build_wall_s = (time.perf_counter_ns() - t_build_0) / 1e9
    _log(f"build phase: stored {M_base} items in {build_wall_s:.2f}s "
         f"({M_base/build_wall_s:.1f} stores/s)")

    # IMPORTANT: the probe loop runs immediately after build with NO
    # synchronization barrier. First op latency reflects whatever caching /
    # JIT / lazy-init state the backend is in immediately post-build.

    per_phase_us: dict[str, list[float]] = {name: [] for name in phase_names}
    per_phase_count: dict[str, int] = {name: 0 for name in phase_names}

    progress_interval = max(N_probe_ops // 10, 100)
    last_progress = 0

    t_probe_0 = time.perf_counter_ns()

    for step in range(N_probe_ops):
        if step - last_progress >= progress_interval and step > 0:
            elapsed = (time.perf_counter_ns() - t_probe_0) / 1e9
            _log(f"probe progress: {step}/{N_probe_ops} "
                 f"({100.0*step/N_probe_ops:.1f}%) elapsed {elapsed:.1f}s")
            last_progress = step

        phase_idx = _phase_for_index(step, phase_boundaries)
        phase = phase_names[phase_idx]
        kvec = initial_vecs[int(probe_target_idx[step])]

        t0 = time.perf_counter_ns()
        try:
            backend.retrieve(kvec, k=1)
        except Exception:
            t1 = time.perf_counter_ns()
            per_phase_us[phase].append((t1 - t0) / 1000.0)
            per_phase_count[phase] += 1
            continue
        t1 = time.perf_counter_ns()
        per_phase_us[phase].append((t1 - t0) / 1000.0)
        per_phase_count[phase] += 1

    total_probe_wall_s = (time.perf_counter_ns() - t_probe_0) / 1e9

    per_phase_stats = {}
    for name in phase_names:
        samples = per_phase_us[name]
        per_phase_stats[name] = {
            "n_ops": len(samples),
            "mean_us": float(np.mean(samples)) if samples else 0.0,
            "p50_us": _percentile(samples, 50),
            "p95_us": _percentile(samples, 95),
            "p99_us": _percentile(samples, 99),
            "min_us": float(np.min(samples)) if samples else 0.0,
            "max_us": float(np.max(samples)) if samples else 0.0,
        }

    # Cold-to-warm ratio: first-phase p50 / mid-phase p50.
    cold_p50 = per_phase_stats[phase_names[0]]["p50_us"]
    # Use the "warm" phase if present, else the second-to-last phase.
    warm_name = "warm" if "warm" in phase_names else phase_names[max(0, len(phase_names)-2)]
    warm_p50 = per_phase_stats[warm_name]["p50_us"]
    cold_to_warm = cold_p50 / warm_p50 if warm_p50 > 0 else 0.0

    # Warm-to-long ratio.
    long_name = phase_names[-1]
    long_p50 = per_phase_stats[long_name]["p50_us"]
    warm_to_long = long_p50 / warm_p50 if warm_p50 > 0 else 0.0

    # HARD_PASS gates.
    if is_substrate:
        hp_sub = bool(cold_to_warm <= 5.0 and 0.85 <= warm_to_long <= 1.15)
        hp_bsl = False
    else:
        hp_sub = False
        hp_bsl = bool(cold_to_warm <= 10.0 and 0.85 <= warm_to_long <= 1.15)

    result = {
        "scenario": "cold_warm_timing",
        "backend": backend.name,
        "M_base": M_base,
        "N_probe_ops": N_probe_ops,
        "phase_boundaries": phase_boundaries,
        "phase_names": phase_names,
        "build_wall_s": build_wall_s,
        "total_probe_wall_s": total_probe_wall_s,
        "per_phase": per_phase_stats,
        "cold_to_warm_p50_ratio": cold_to_warm,
        "warm_to_long_p50_ratio": warm_to_long,
        "hard_pass_substrate": hp_sub,
        "hard_pass_baselines": hp_bsl,
    }

    partial_path = partial_dir / f"{backend.name}.json"
    with open(partial_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    _log(f"wrote partial result: {partial_path}")

    _log(f"done: cold/warm ratio = {cold_to_warm:.2f}x, warm/long ratio = "
         f"{warm_to_long:.3f}, total probe wall {total_probe_wall_s:.1f}s")

    return result


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {
                "cold_to_warm_p50_ratio_le": 5.0,
                "warm_to_long_p50_ratio_in_band": [0.85, 1.15],
            },
            "hard_fail": {
                "cold_to_warm_p50_ratio_gt": 20.0,
                "warm_to_long_p50_ratio_below": 0.5,
            },
        },
        "baselines": {
            "hard_pass": {
                "cold_to_warm_p50_ratio_le": 10.0,
                "warm_to_long_p50_ratio_in_band": [0.85, 1.15],
            },
            "hard_fail": {
                "cold_to_warm_p50_ratio_gt": 50.0,
                "warm_to_long_p50_ratio_below": 0.5,
            },
        },
    }
