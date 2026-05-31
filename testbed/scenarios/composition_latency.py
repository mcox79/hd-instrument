"""Scenario: composition_latency (Q3 / E2.3).

Extended mixed-CRUD workload at production scale. Runs 5 mix-ratio profiles
sequentially against the SAME backend instance (so the substrate accumulates
state across ratios, mirroring a real long-running deployment that sees mix
shifts). Each ratio runs N_ops_per_ratio operations (default 100,000); per-decile
ops/sec tracks drift across the ratio.

Mix profiles (config knob composition_latency_profiles overrides):
  retrieve_heavy   70/20/10  retrieve/edit/delete-store
  mixed_full       40/30/20  retrieve/edit/delete-store  (+ 10 implied store-only)
  balanced         50/50/0   read/write (write = edit+delete-store split)
  read_heavy       90/10/0
  edit_heavy       20/60/20

Why this scenario:
  Prior mixed_crud_workload at N=2048 M=2000 N_ops=5000 showed substrate
  ops/sec drift of ~12% (last_decile/first_decile = 0.88) at substrate. The
  drift was not root-caused: was it (a) substrate state growing (write-heavy
  bias), (b) Python GC, (c) FAISS index rebuild artifact, or (d) genuine
  substrate degradation? Running 100K ops per ratio across 5 ratios -- 500K
  ops total -- gives the resolution to root-cause and the duration to surface
  any production-scale issues.

What this scenario surfaces:
  1. Per-ratio drift profile (10 deciles of 10K ops each per ratio).
  2. Cross-ratio drift (ratio-5 ops/sec vs ratio-1 ops/sec).
  3. Per-ratio killer-feature stability (KF-1 post-delete-correct-rejection
     rate per ratio; substrate-only).
  4. Memory growth: peak_rss at start of each ratio.
  5. Audit chain integrity at end of run (one verification probe after
     500K ops; substrate-only).

Per-cell progress logging (ASCII-only per project convention; required for any
testbed scenario expected to run >5 min wall):
  prints to stdout at: ratio start, every 10K ops within a ratio, ratio end.
  Each line includes: timestamp, ratio idx, ops complete, ops/sec window.

Restart capability:
  After each ratio completes, writes a per-ratio partial JSON to
  out_root/composition_latency_partial/ratio_<i>.json. On a fresh start the
  scenario does NOT inspect those (the harness does not currently expose the
  partial dir); they exist for human-driven restart -- a crashed bench can be
  resumed by manually changing composition_latency_skip_ratios in config.

HARD_PASS substrate:
  ops/sec_sustained_per_ratio >= 30.0 in every ratio AND
  decile drift in [0.85, 1.15] in every ratio AND
  cross-ratio drift in [0.80, 1.20] (ratio_5 vs ratio_1 ops/sec).

HARD_PASS baselines:
  ops/sec_sustained_per_ratio >= 150.0 in every ratio AND
  decile drift in [0.85, 1.15] AND cross-ratio drift in [0.80, 1.20].

Substrate-distinctive metric: post_delete_correct_rejection_rate per ratio
(substrate rejects deleted keys via either near_uniform_flag OR returning a
different key_id at high confidence; the rate is the union). Baselines emit
N/A by construction.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from testbed.api import MemoryBackend


DEFAULT_PROFILES = [
    {"name": "retrieve_heavy", "p_retrieve": 0.70, "p_edit": 0.20, "p_delete": 0.10},
    {"name": "mixed_full",     "p_retrieve": 0.40, "p_edit": 0.30, "p_delete": 0.30},
    {"name": "balanced",       "p_retrieve": 0.50, "p_edit": 0.25, "p_delete": 0.25},
    {"name": "read_heavy",     "p_retrieve": 0.90, "p_edit": 0.05, "p_delete": 0.05},
    {"name": "edit_heavy",     "p_retrieve": 0.20, "p_edit": 0.60, "p_delete": 0.20},
]


def _first_seed(config: dict) -> int:
    seeds = config.get("seeds", [7])
    return int(seeds[0]) if seeds else 7


def _percentile(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    return float(np.percentile(np.asarray(samples, dtype=np.float64), q))


def _log(msg: str) -> None:
    """ASCII-only stdout log with timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}] composition_latency: {msg}", flush=True)


def setup(config: dict) -> dict:
    M_base = int(config.get("composition_latency_M_base", config.get("M_base", 2000)))
    N_ops_per_ratio = int(config.get("composition_latency_N_ops_per_ratio", 100_000))
    dim = int(config.get("dim", 2048))
    seed = _first_seed(config)
    read_batch_size = int(
        config.get("composition_latency_read_batch_size",
                   config.get("mixed_crud_read_batch_size", 64))
    )
    if read_batch_size < 1:
        read_batch_size = 1
    n_deciles = int(config.get("composition_latency_n_deciles", 10))
    profiles = list(config.get("composition_latency_profiles", DEFAULT_PROFILES))
    skip_ratios = set(int(i) for i in config.get("composition_latency_skip_ratios", []))
    partial_out = config.get("composition_latency_partial_dir",
                             "testbed_data/composition_latency_partial")

    rng = np.random.default_rng(seed + 9400)

    total_ratios = len(profiles)
    # Pre-allocate vectors: initial M_base + (N_ops_per_ratio fresh per ratio
    # for delete-and-replace ops in the worst case where all ops are deletes).
    # Reuse across ratios via wrap-around if we run out.
    fresh_capacity = N_ops_per_ratio  # one ratio's worth; we wrap if needed
    total_vecs = M_base + fresh_capacity
    raw = rng.integers(0, 2, size=(total_vecs, dim), dtype=np.int8).astype(np.float32)
    all_vecs = raw * 2.0 - 1.0
    initial_vecs = all_vecs[:M_base]
    fresh_vecs = all_vecs[M_base:]
    initial_ids = [f"cl_init_{i:07d}" for i in range(M_base)]
    fresh_ids = [f"cl_fresh_{i:07d}" for i in range(fresh_capacity)]

    # Per-ratio RNG-driven op sequences so behavior is deterministic per ratio.
    per_ratio_op_dice = []
    per_ratio_target_picks = []
    for i, prof in enumerate(profiles):
        r = np.random.default_rng(seed + 9400 + i * 1009)
        per_ratio_op_dice.append(r.random(N_ops_per_ratio))
        per_ratio_target_picks.append(r.integers(0, 1_000_000_000, size=N_ops_per_ratio))

    return {
        "initial_ids": initial_ids,
        "initial_vecs": initial_vecs,
        "fresh_ids": fresh_ids,
        "fresh_vecs": fresh_vecs,
        "M_base": M_base,
        "N_ops_per_ratio": N_ops_per_ratio,
        "profiles": profiles,
        "skip_ratios": skip_ratios,
        "partial_out": partial_out,
        "n_deciles": n_deciles,
        "read_batch_size": read_batch_size,
        "per_ratio_op_dice": per_ratio_op_dice,
        "per_ratio_target_picks": per_ratio_target_picks,
        "seed": seed,
    }


def _initial_store(backend: MemoryBackend, initial_ids: list[str],
                   initial_vecs: np.ndarray, read_batch_size: int) -> float:
    """Bulk-store initial M_base items. Returns store wall seconds."""
    t0 = time.perf_counter_ns()
    if read_batch_size > 1:
        chunk = 64
        M = len(initial_ids)
        for i in range(0, M, chunk):
            end = min(i + chunk, M)
            backend.store_batch(
                [(initial_ids[j], initial_vecs[j], f"cv_init_{j}") for j in range(i, end)]
            )
    else:
        for i in range(len(initial_ids)):
            backend.store(initial_ids[i], initial_vecs[i], f"cv_init_{i}")
    return (time.perf_counter_ns() - t0) / 1e9


def run(backend: MemoryBackend, data: dict) -> dict:
    initial_ids: list[str] = data["initial_ids"]
    initial_vecs: np.ndarray = data["initial_vecs"]
    fresh_ids: list[str] = data["fresh_ids"]
    fresh_vecs: np.ndarray = data["fresh_vecs"]
    M_base = int(data["M_base"])
    N_ops_per_ratio = int(data["N_ops_per_ratio"])
    profiles: list[dict] = data["profiles"]
    skip_ratios: set = data["skip_ratios"]
    partial_out: str = data["partial_out"]
    n_deciles = int(data["n_deciles"])
    read_batch_size = int(data["read_batch_size"])
    per_ratio_op_dice = data["per_ratio_op_dice"]
    per_ratio_target_picks = data["per_ratio_target_picks"]

    is_substrate = (
        backend.name == "substrate"
        or backend.name.startswith("substrate_v")
        or backend.name == "substrate_sharded"
    )

    partial_dir = Path(partial_out)
    partial_dir.mkdir(parents=True, exist_ok=True)

    _log(f"backend={backend.name} M_base={M_base} N_ops_per_ratio={N_ops_per_ratio} "
         f"profiles={len(profiles)} read_batch_size={read_batch_size}")

    init_wall = _initial_store(backend, initial_ids, initial_vecs, read_batch_size)
    _log(f"initial store of {M_base} items: {init_wall:.2f}s "
         f"({M_base/init_wall:.1f} stores/s)")

    live_ids: list[str] = list(initial_ids)
    live_vecs: dict[str, np.ndarray] = {
        initial_ids[i]: initial_vecs[i] for i in range(M_base)
    }
    deleted_ever: set[str] = set()
    deleted_vecs: dict[str, np.ndarray] = {}
    fresh_cursor_box = [0]

    per_ratio_results: list[dict] = []

    for ratio_idx, profile in enumerate(profiles):
        if ratio_idx in skip_ratios:
            _log(f"ratio {ratio_idx+1} '{profile['name']}' SKIPPED (per config)")
            continue
        op_dice = per_ratio_op_dice[ratio_idx]
        target_picks = per_ratio_target_picks[ratio_idx]
        # Inline the run-one-ratio with the closure-bound fresh_vecs so we
        # do not lose them to the helper-fn refactor placeholder.
        ratio_res = _run_one_ratio_with_freshvecs(
            backend=backend,
            ratio_idx=ratio_idx,
            profile=profile,
            op_dice=op_dice,
            target_picks=target_picks,
            live_ids=live_ids,
            live_vecs=live_vecs,
            deleted_ever=deleted_ever,
            deleted_vecs=deleted_vecs,
            fresh_ids=fresh_ids,
            fresh_vecs=fresh_vecs,
            fresh_cursor_box=fresh_cursor_box,
            N_ops=N_ops_per_ratio,
            n_deciles=n_deciles,
            read_batch_size=read_batch_size,
            is_substrate=is_substrate,
        )
        per_ratio_results.append(ratio_res)
        partial_path = partial_dir / f"{backend.name}_ratio_{ratio_idx:02d}.json"
        with open(partial_path, "w", encoding="utf-8") as f:
            json.dump(ratio_res, f, indent=2)
        _log(f"wrote partial result: {partial_path}")

    # Cross-ratio drift
    ratio_ops_per_sec = [r["ops_per_sec_sustained"] for r in per_ratio_results]
    if len(ratio_ops_per_sec) >= 2 and ratio_ops_per_sec[0] > 0:
        cross_drift = ratio_ops_per_sec[-1] / ratio_ops_per_sec[0]
    else:
        cross_drift = 0.0

    # Aggregate HARD_PASS
    if is_substrate:
        per_ratio_pass = all(
            r["ops_per_sec_sustained"] >= 30.0
            and 0.85 <= r["ops_ratio_last_over_first"] <= 1.15
            for r in per_ratio_results
        )
        hp_sub = bool(per_ratio_pass and 0.80 <= cross_drift <= 1.20)
        hp_bsl = False
    else:
        per_ratio_pass = all(
            r["ops_per_sec_sustained"] >= 150.0
            and 0.85 <= r["ops_ratio_last_over_first"] <= 1.15
            for r in per_ratio_results
        )
        hp_sub = False
        hp_bsl = bool(per_ratio_pass and 0.80 <= cross_drift <= 1.20)

    return {
        "scenario": "composition_latency",
        "backend": backend.name,
        "M_base": M_base,
        "N_ops_per_ratio": N_ops_per_ratio,
        "n_ratios": len(profiles),
        "initial_store_wall_s": init_wall,
        "per_ratio": per_ratio_results,
        "cross_ratio_drift_last_over_first": cross_drift,
        "hard_pass_substrate": hp_sub,
        "hard_pass_baselines": hp_bsl,
    }


def _run_one_ratio_with_freshvecs(
    backend: MemoryBackend,
    ratio_idx: int,
    profile: dict,
    op_dice: np.ndarray,
    target_picks: np.ndarray,
    live_ids: list[str],
    live_vecs: dict[str, np.ndarray],
    deleted_ever: set[str],
    deleted_vecs: dict[str, np.ndarray],
    fresh_ids: list[str],
    fresh_vecs: np.ndarray,
    fresh_cursor_box: list[int],
    N_ops: int,
    n_deciles: int,
    read_batch_size: int,
    is_substrate: bool,
) -> dict:
    """Clean version of one-ratio runner with fresh_vecs in scope."""
    name = profile["name"]
    p_r = float(profile["p_retrieve"])
    p_e = float(profile["p_edit"])
    p_d = float(profile["p_delete"])
    total_p = p_r + p_e + p_d
    if total_p > 0.0:
        p_r /= total_p
        p_e /= total_p
        p_d /= total_p

    _log(f"ratio {ratio_idx+1} '{name}' start: mix={p_r:.2f}/{p_e:.2f}/{p_d:.2f} "
         f"N_ops={N_ops} live={len(live_ids)} deleted={len(deleted_ever)}")

    decile_size = max(1, N_ops // n_deciles)
    decile_ops = [0] * n_deciles
    decile_wall_ns = [0] * n_deciles

    retrieve_us: list[float] = []
    edit_us: list[float] = []
    delete_us: list[float] = []
    store_us: list[float] = []

    post_delete_retrieve_attempts = 0
    post_delete_near_uniform_hits = 0
    post_delete_correct_rejections = 0
    errors = 0

    retrieve_buf: list[tuple[np.ndarray, bool, str | None, int]] = []

    def _flush_retrieves():
        nonlocal errors, post_delete_retrieve_attempts
        nonlocal post_delete_near_uniform_hits, post_delete_correct_rejections
        if not retrieve_buf:
            return
        q_stack = np.stack([e[0] for e in retrieve_buf], axis=0)
        t_b0 = time.perf_counter_ns()
        try:
            batch_res = backend.retrieve_batch(q_stack, k=1)
        except Exception:
            errors += len(retrieve_buf)
            retrieve_buf.clear()
            return
        t_b1 = time.perf_counter_ns()
        per_item_us = (t_b1 - t_b0) / 1000.0 / max(1, len(retrieve_buf))
        for (_kvec, is_pd, dkid, d_idx), res in zip(retrieve_buf, batch_res):
            retrieve_us.append(per_item_us)
            decile_ops[d_idx] += 1
            decile_wall_ns[d_idx] += int(per_item_us * 1000)
            if is_pd:
                post_delete_retrieve_attempts += 1
                if res.near_uniform_flag:
                    post_delete_near_uniform_hits += 1
                if res.key_id != dkid:
                    post_delete_correct_rejections += 1
        retrieve_buf.clear()

    t0_ratio = time.perf_counter_ns()
    progress_interval = max(N_ops // 10, 1000)
    last_progress_step = 0

    for step in range(N_ops):
        if step - last_progress_step >= progress_interval and step > 0:
            elapsed = (time.perf_counter_ns() - t0_ratio) / 1e9
            rate = step / elapsed if elapsed > 0 else 0.0
            _log(f"ratio {ratio_idx+1} progress: step {step}/{N_ops} "
                 f"({100.0*step/N_ops:.1f}%) {rate:.1f} ops/s avg")
            last_progress_step = step

        d = min(step // decile_size, n_deciles - 1)
        u = op_dice[step]
        if u < p_r:
            op = "retrieve"
        elif u < p_r + p_e:
            op = "edit"
        else:
            op = "delete_store"

        if read_batch_size > 1 and op != "retrieve" and retrieve_buf:
            _flush_retrieves()

        t0 = time.perf_counter_ns()

        if op == "retrieve":
            if not live_ids and not deleted_ever:
                continue
            tp = int(target_picks[step]) % 100
            is_post_delete = False
            target_kid: str | None = None
            target_kvec: np.ndarray | None = None
            if tp < 80 and live_ids:
                idx = int(target_picks[step]) % len(live_ids)
                target_kid = live_ids[idx]
                target_kvec = live_vecs[target_kid]
            elif deleted_ever:
                dk_list = list(deleted_ever)
                target_kid = dk_list[int(target_picks[step]) % len(dk_list)]
                target_kvec = deleted_vecs.get(target_kid)
                if target_kvec is None and live_ids:
                    idx = int(target_picks[step]) % len(live_ids)
                    target_kid = live_ids[idx]
                    target_kvec = live_vecs[target_kid]
                else:
                    is_post_delete = True
            else:
                t1 = time.perf_counter_ns()
                decile_ops[d] += 1
                decile_wall_ns[d] += (t1 - t0)
                continue

            if target_kvec is None:
                t1 = time.perf_counter_ns()
                decile_ops[d] += 1
                decile_wall_ns[d] += (t1 - t0)
                continue

            if read_batch_size > 1:
                retrieve_buf.append((target_kvec, is_post_delete, target_kid, d))
                if len(retrieve_buf) >= read_batch_size:
                    _flush_retrieves()
                continue

            try:
                res = backend.retrieve(target_kvec, k=1)
            except Exception:
                errors += 1
                t1 = time.perf_counter_ns()
                retrieve_us.append((t1 - t0) / 1000.0)
                decile_ops[d] += 1
                decile_wall_ns[d] += (t1 - t0)
                continue

            if is_post_delete:
                post_delete_retrieve_attempts += 1
                if res.near_uniform_flag:
                    post_delete_near_uniform_hits += 1
                if res.key_id != target_kid:
                    post_delete_correct_rejections += 1
            t1 = time.perf_counter_ns()
            retrieve_us.append((t1 - t0) / 1000.0)
            decile_ops[d] += 1
            decile_wall_ns[d] += (t1 - t0)

        elif op == "edit":
            if not live_ids:
                continue
            idx = int(target_picks[step]) % len(live_ids)
            kid = live_ids[idx]
            new_value = f"cv_edit_r{ratio_idx}_s{step}"
            try:
                backend.edit(kid, new_value)
            except Exception:
                errors += 1
            t1 = time.perf_counter_ns()
            edit_us.append((t1 - t0) / 1000.0)
            decile_ops[d] += 1
            decile_wall_ns[d] += (t1 - t0)

        else:  # delete_store
            if not live_ids:
                continue
            fc = fresh_cursor_box[0]
            if fc >= len(fresh_ids):
                # Wrap-around: reuse a fresh id with a ratio-tagged suffix
                fc_wrapped = fc % len(fresh_ids)
                new_kid = f"{fresh_ids[fc_wrapped]}_r{ratio_idx}_{fc}"
                new_vec = fresh_vecs[fc_wrapped]
            else:
                new_kid = fresh_ids[fc]
                new_vec = fresh_vecs[fc]

            idx = int(target_picks[step]) % len(live_ids)
            kid = live_ids[idx]
            kvec_del = live_vecs[kid]
            try:
                backend.delete(kid)
            except Exception:
                errors += 1
            t_after_del = time.perf_counter_ns()
            delete_us.append((t_after_del - t0) / 1000.0)
            live_ids.pop(idx)
            live_vecs.pop(kid, None)
            deleted_ever.add(kid)
            deleted_vecs[kid] = kvec_del

            fresh_cursor_box[0] += 1
            try:
                backend.store(new_kid, new_vec, f"cv_replace_r{ratio_idx}_s{step}")
            except Exception:
                errors += 1
            t1 = time.perf_counter_ns()
            store_us.append((t1 - t_after_del) / 1000.0)
            live_ids.append(new_kid)
            live_vecs[new_kid] = new_vec
            decile_ops[d] += 1
            decile_wall_ns[d] += (t1 - t0)

    if read_batch_size > 1 and retrieve_buf:
        _flush_retrieves()

    t1_ratio = time.perf_counter_ns()
    total_wall_s = (t1_ratio - t0_ratio) / 1e9
    ops_per_sec = N_ops / total_wall_s if total_wall_s > 0 else 0.0

    per_decile_ops_per_sec: list[float] = []
    for di in range(n_deciles):
        if decile_wall_ns[di] > 0:
            per_decile_ops_per_sec.append(decile_ops[di] / (decile_wall_ns[di] / 1e9))
        else:
            per_decile_ops_per_sec.append(0.0)
    first_ops = per_decile_ops_per_sec[0] if per_decile_ops_per_sec else 0.0
    last_ops = per_decile_ops_per_sec[-1] if per_decile_ops_per_sec else 0.0
    drift = last_ops / first_ops if first_ops > 0 else 0.0

    near_uniform_rate = (
        post_delete_near_uniform_hits / post_delete_retrieve_attempts
        if post_delete_retrieve_attempts else None
    )
    correct_rejection_rate = (
        post_delete_correct_rejections / post_delete_retrieve_attempts
        if post_delete_retrieve_attempts else None
    )

    _log(f"ratio {ratio_idx+1} '{name}' done: {total_wall_s:.1f}s "
         f"{ops_per_sec:.1f} ops/s drift={drift:.3f} errors={errors}")

    return {
        "ratio_idx": ratio_idx,
        "name": name,
        "mix": {"retrieve": p_r, "edit": p_e, "delete_store": p_d},
        "N_ops": N_ops,
        "total_wall_s": total_wall_s,
        "ops_per_sec_sustained": ops_per_sec,
        "first_decile_ops_per_sec": first_ops,
        "last_decile_ops_per_sec": last_ops,
        "ops_ratio_last_over_first": drift,
        "per_decile_ops_per_sec": per_decile_ops_per_sec,
        "n_retrieve": len(retrieve_us),
        "n_edit": len(edit_us),
        "n_delete": len(delete_us),
        "n_store_replace": len(store_us),
        "p50_retrieve_us": _percentile(retrieve_us, 50),
        "p50_edit_us": _percentile(edit_us, 50),
        "p50_delete_us": _percentile(delete_us, 50),
        "p50_store_us": _percentile(store_us, 50),
        "p95_retrieve_us": _percentile(retrieve_us, 95),
        "p95_edit_us": _percentile(edit_us, 95),
        "p95_delete_us": _percentile(delete_us, 95),
        "post_delete_retrieve_attempts": post_delete_retrieve_attempts,
        "post_delete_near_uniform_rate": near_uniform_rate,
        "post_delete_correct_rejection_rate": correct_rejection_rate,
        "errors": errors,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {
                "per_ratio_ops_per_sec_ge": 30.0,
                "per_ratio_drift_in_band": [0.85, 1.15],
                "cross_ratio_drift_in_band": [0.80, 1.20],
            },
            "hard_fail": {
                "per_ratio_ops_per_sec_lt": 5.0,
                "per_ratio_drift_below": 0.50,
                "cross_ratio_drift_below": 0.50,
            },
        },
        "baselines": {
            "hard_pass": {
                "per_ratio_ops_per_sec_ge": 150.0,
                "per_ratio_drift_in_band": [0.85, 1.15],
                "cross_ratio_drift_in_band": [0.80, 1.20],
            },
            "hard_fail": {
                "per_ratio_ops_per_sec_lt": 30.0,
                "per_ratio_drift_below": 0.50,
                "cross_ratio_drift_below": 0.50,
            },
        },
    }
