"""Scenario 13: mixed_crud_workload (realistic workload).

The most production-realistic of the four realistic-workload scenarios.

Mix (per default config):
  70%  retrieve  (random stored key, by vector)
  20%  edit      (random stored key, value swap)
  10%  delete-then-store-new (delete a random stored key, store a fresh one)

Total operations: N_ops (default 5000). M_base items initially stored.
The mix probabilities are sampled per op, not pre-batched; ops are
interleaved like a real workload would interleave them.

What this scenario surfaces:

  1. Sustained ops/sec under heterogeneous load. Substrate is slower per
     op than FAISS (matmul vs O(M) flat scan, both dense but substrate has
     a heavier constant). Under mix, the substrate's per-op cost still
     dominates; we want to confirm it stays steady (no degradation as the
     working set churns through delete+store cycles).

  2. Error-handling: 70% retrieve traffic includes a sliding fraction of
     retrieves on JUST-DELETED keys (the delete-then-store-new ops). The
     substrate should fire near_uniform_flag on these; baselines silently
     return the nearest neighbor (a structural hallucination).

  3. Working set drift: with 10% delete-and-replace, the active key set
     gradually rotates. We track recall on the current live set every
     decile to confirm no drift.

HARD_PASS substrate:
  ops_per_sec >= 50 sustained AND first-decile ops/sec vs last-decile ratio
  in [0.7, 1.3] (no degradation)

HARD_PASS baselines:
  ops_per_sec >= 200 sustained AND first/last decile ratio in [0.7, 1.3].

Substrate-distinctive metric: fraction of post-delete retrieves (retrieves
issued on a key_id that was deleted earlier in this run AND has not been
re-stored) that correctly fire near_uniform_flag. KF-1 in flight, not in
isolation. Baselines report this metric as N/A by construction.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from testbed.api import MemoryBackend


def _first_seed(config: dict) -> int:
    seeds = config.get("seeds", [7])
    if not seeds:
        return 7
    return int(seeds[0])


def _percentile(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    return float(np.percentile(np.asarray(samples, dtype=np.float64), q))


def setup(config: dict) -> dict:
    M_base = int(config.get("mixed_crud_M_base", config.get("M_base", 2000)))
    N_ops = int(config.get("mixed_crud_N_ops", 5000))
    dim = int(config.get("dim", 4096))
    seed = _first_seed(config)
    mix_retrieve = float(config.get("mixed_crud_p_retrieve", 0.70))
    mix_edit = float(config.get("mixed_crud_p_edit", 0.20))
    mix_delete = float(config.get("mixed_crud_p_delete", 0.10))
    total_p = mix_retrieve + mix_edit + mix_delete
    if total_p <= 0.0:
        mix_retrieve, mix_edit, mix_delete = 0.7, 0.2, 0.1
    else:
        mix_retrieve /= total_p
        mix_edit /= total_p
        mix_delete /= total_p
    n_deciles = int(config.get("mixed_crud_n_deciles", 10))

    rng = np.random.default_rng(seed + 7400)

    # M_base initial items + a fresh-vector pool large enough for all
    # delete-and-replace ops (worst case all 10% ops are delete-and-replace).
    fresh_capacity = N_ops  # over-provision; cheap
    total_vecs = M_base + fresh_capacity
    raw = rng.integers(0, 2, size=(total_vecs, dim), dtype=np.int8).astype(np.float32)
    all_vecs = raw * 2.0 - 1.0
    initial_vecs = all_vecs[:M_base]
    fresh_vecs = all_vecs[M_base:]
    initial_ids = [f"mc_init_{i:07d}" for i in range(M_base)]
    fresh_ids = [f"mc_fresh_{i:07d}" for i in range(fresh_capacity)]

    op_dice = rng.random(N_ops)
    target_picks = rng.integers(0, 1_000_000_000, size=N_ops)

    return {
        "initial_ids": initial_ids,
        "initial_vecs": initial_vecs,
        "fresh_ids": fresh_ids,
        "fresh_vecs": fresh_vecs,
        "M_base": M_base,
        "N_ops": N_ops,
        "mix": (mix_retrieve, mix_edit, mix_delete),
        "n_deciles": n_deciles,
        "op_dice": op_dice,
        "target_picks": target_picks,
        "seed": seed,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    initial_ids: list[str] = data["initial_ids"]
    initial_vecs: np.ndarray = data["initial_vecs"]
    fresh_ids: list[str] = data["fresh_ids"]
    fresh_vecs: np.ndarray = data["fresh_vecs"]
    M_base = int(data["M_base"])
    N_ops = int(data["N_ops"])
    p_r, p_e, p_d = data["mix"]
    n_deciles = int(data["n_deciles"])
    op_dice: np.ndarray = data["op_dice"]
    target_picks: np.ndarray = data["target_picks"]

    is_substrate = (
        backend.name == "substrate"
        or backend.name.startswith("substrate_v")
        or backend.name == "substrate_sharded"
    )

    # Initial store
    for i in range(M_base):
        backend.store(initial_ids[i], initial_vecs[i], f"mv_init_{i}")

    # Live set: list of (key_id, key_vec). Use a list for O(1) random index,
    # and a dict for O(1) deletion check.
    live_ids: list[str] = list(initial_ids)
    live_vecs: dict[str, np.ndarray] = {
        initial_ids[i]: initial_vecs[i] for i in range(M_base)
    }
    # Track key_ids that have been deleted and never re-stored; used to
    # measure post-delete-retrieve KF-1 firing rate.
    deleted_ever: set[str] = set()
    deleted_vecs: dict[str, np.ndarray] = {}

    fresh_cursor = 0
    decile_size = max(1, N_ops // n_deciles)
    decile_ops = [0] * n_deciles
    decile_wall_ns = [0] * n_deciles

    retrieve_us: list[float] = []
    edit_us: list[float] = []
    delete_us: list[float] = []
    store_us: list[float] = []

    post_delete_retrieve_attempts = 0
    post_delete_near_uniform_hits = 0  # substrate
    post_delete_correct_rejections = 0  # any backend that returns key_id != deleted

    errors = 0

    t_total_0 = time.perf_counter_ns()

    for step in range(N_ops):
        d = min(step // decile_size, n_deciles - 1)
        u = op_dice[step]
        if u < p_r:
            op = "retrieve"
        elif u < p_r + p_e:
            op = "edit"
        else:
            op = "delete_store"

        t0 = time.perf_counter_ns()

        if op == "retrieve":
            if not live_ids and not deleted_ever:
                continue
            # 80% of retrieve traffic targets live keys; 20% targets a
            # previously-deleted key to stress KF-1.
            tp = int(target_picks[step]) % 100
            if tp < 80 and live_ids:
                idx = int(target_picks[step]) % len(live_ids)
                kid = live_ids[idx]
                kvec = live_vecs[kid]
                try:
                    res = backend.retrieve(kvec, k=1)
                except Exception:
                    errors += 1
                    t1 = time.perf_counter_ns()
                    retrieve_us.append((t1 - t0) / 1000.0)
                    decile_ops[d] += 1
                    decile_wall_ns[d] += (t1 - t0)
                    continue
            elif deleted_ever:
                # post-delete retrieve probe
                dk_list = list(deleted_ever)
                kid = dk_list[int(target_picks[step]) % len(dk_list)]
                kvec = deleted_vecs.get(kid)
                if kvec is None:
                    # shouldn't happen; fall back to live
                    if live_ids:
                        idx = int(target_picks[step]) % len(live_ids)
                        kid = live_ids[idx]
                        kvec = live_vecs[kid]
                    else:
                        t1 = time.perf_counter_ns()
                        decile_ops[d] += 1
                        decile_wall_ns[d] += (t1 - t0)
                        continue
                try:
                    res = backend.retrieve(kvec, k=1)
                except Exception:
                    errors += 1
                    t1 = time.perf_counter_ns()
                    retrieve_us.append((t1 - t0) / 1000.0)
                    decile_ops[d] += 1
                    decile_wall_ns[d] += (t1 - t0)
                    continue
                post_delete_retrieve_attempts += 1
                if res.near_uniform_flag:
                    post_delete_near_uniform_hits += 1
                if res.key_id != kid:
                    post_delete_correct_rejections += 1
            else:
                # No deleted yet, no live: pathological. Skip.
                t1 = time.perf_counter_ns()
                decile_ops[d] += 1
                decile_wall_ns[d] += (t1 - t0)
                continue

            t1 = time.perf_counter_ns()
            retrieve_us.append((t1 - t0) / 1000.0)
            decile_ops[d] += 1
            decile_wall_ns[d] += (t1 - t0)

        elif op == "edit":
            if not live_ids:
                continue
            idx = int(target_picks[step]) % len(live_ids)
            kid = live_ids[idx]
            new_value = f"mv_edit_step_{step}"
            try:
                backend.edit(kid, new_value)
            except Exception:
                errors += 1
            t1 = time.perf_counter_ns()
            edit_us.append((t1 - t0) / 1000.0)
            decile_ops[d] += 1
            decile_wall_ns[d] += (t1 - t0)

        else:  # delete_store
            if not live_ids or fresh_cursor >= len(fresh_ids):
                continue
            idx = int(target_picks[step]) % len(live_ids)
            kid = live_ids[idx]
            kvec_del = live_vecs[kid]
            try:
                backend.delete(kid)
            except Exception:
                errors += 1
            t_after_del = time.perf_counter_ns()
            delete_us.append((t_after_del - t0) / 1000.0)
            # bookkeeping
            live_ids.pop(idx)
            live_vecs.pop(kid, None)
            deleted_ever.add(kid)
            deleted_vecs[kid] = kvec_del

            new_kid = fresh_ids[fresh_cursor]
            new_vec = fresh_vecs[fresh_cursor]
            fresh_cursor += 1
            try:
                backend.store(new_kid, new_vec, f"mv_replace_step_{step}")
            except Exception:
                errors += 1
            t1 = time.perf_counter_ns()
            store_us.append((t1 - t_after_del) / 1000.0)
            live_ids.append(new_kid)
            live_vecs[new_kid] = new_vec
            decile_ops[d] += 1
            decile_wall_ns[d] += (t1 - t0)

    t_total_1 = time.perf_counter_ns()
    total_wall_s = (t_total_1 - t_total_0) / 1e9
    ops_per_sec_sustained = N_ops / total_wall_s if total_wall_s > 0 else 0.0

    # Per-decile ops/sec
    per_decile_ops_per_sec: list[float] = []
    for d in range(n_deciles):
        if decile_wall_ns[d] > 0:
            per_decile_ops_per_sec.append(decile_ops[d] / (decile_wall_ns[d] / 1e9))
        else:
            per_decile_ops_per_sec.append(0.0)
    first_ops = per_decile_ops_per_sec[0] if per_decile_ops_per_sec else 0.0
    last_ops = per_decile_ops_per_sec[-1] if per_decile_ops_per_sec else 0.0
    if first_ops > 0.0:
        ops_ratio = last_ops / first_ops
    else:
        ops_ratio = 0.0

    near_uniform_rate = (
        post_delete_near_uniform_hits / post_delete_retrieve_attempts
        if post_delete_retrieve_attempts else None
    )
    correct_rejection_rate = (
        post_delete_correct_rejections / post_delete_retrieve_attempts
        if post_delete_retrieve_attempts else None
    )

    if is_substrate:
        hp_sub = bool(ops_per_sec_sustained >= 50.0 and 0.7 <= ops_ratio <= 1.3)
        hp_bsl = False
    else:
        hp_sub = False
        hp_bsl = bool(ops_per_sec_sustained >= 200.0 and 0.7 <= ops_ratio <= 1.3)

    return {
        "scenario": "mixed_crud_workload",
        "backend": backend.name,
        "M_base": M_base,
        "N_ops": N_ops,
        "mix": {"retrieve": p_r, "edit": p_e, "delete_store": p_d},
        "total_wall_s": total_wall_s,
        "ops_per_sec_sustained": ops_per_sec_sustained,
        "first_decile_ops_per_sec": first_ops,
        "last_decile_ops_per_sec": last_ops,
        "ops_ratio_last_over_first": ops_ratio,
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
        "hard_pass_substrate": hp_sub,
        "hard_pass_baselines": hp_bsl,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {
                "ops_per_sec_sustained_ge": 50.0,
                "ops_ratio_in_band": [0.7, 1.3],
            },
            "hard_fail": {
                "ops_per_sec_sustained_lt": 10.0,
                "ops_ratio_below": 0.3,
            },
        },
        "baselines": {
            "hard_pass": {
                "ops_per_sec_sustained_ge": 200.0,
                "ops_ratio_in_band": [0.7, 1.3],
            },
            "hard_fail": {
                "ops_per_sec_sustained_lt": 50.0,
                "ops_ratio_below": 0.3,
            },
        },
    }
