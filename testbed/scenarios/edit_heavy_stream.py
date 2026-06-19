"""Scenario 11: edit_heavy_stream (realistic workload).

Setup: store M_base items. Stream: N_edits sequential edits where each
edit picks a random stored key, swaps the VALUE STRING, then immediately
re-queries the same key and verifies the new value is retrieved.

IMPORTANT FRAMING (read this before interpreting results):

  This scenario tests **value-only edits** (the value-string at a key changes,
  but the KEY VECTOR stays the same). This is the most common real-world
  edit pattern: "update the answer string for question X". Under this
  interpretation:

    - Substrate: edit = O(1) outer-product subtract + add, no rebuild.
      Query after edit just re-runs retrieve(). Total edit-then-query cost
      ~= 14 ms (7 ms edit + 7 ms retrieve) on substrate.

    - FAISS: edit = O(1) dict update on _id_to_value (the VECTOR is unchanged,
      so the FAISS IndexFlatIP needs NO rebuild). Query is the usual O(M*d)
      flat search. Edit-then-query ~= a fraction of a millisecond.

    - Dict: trivial dict update. Query is brute-force cosine over all stored.

  Baselines WIN on this scenario by raw speed. That is the honest result and
  the scenario reports it as such. The substrate's structural advantage is
  in **vector-changing edits** (when the stored vector itself changes, FAISS
  needs a full IndexFlatIP rebuild, which is O(M*d); substrate's in-place
  outer-product is still O(N)). A Phase 2 vector-edit scenario will show the
  inverse. We do not run that here to keep the framing fair.

Per-edit correctness check: after edit, the SAME key vector is queried; the
returned value MUST equal new_value. Substrate-specific edge: if the substrate
allocates the same value-atom row for new_value as a different stored key
(collision), the retrieve will surface the older key_id; correctness fails.
The scenario reports the fraction of edits where post-edit-correctness == 1
so the user can see this happening under capacity pressure.

HARD_PASS substrate:
  mean_edit_query_wall_us < 30000 (30 ms) AND post_edit_correctness_rate == 1.0
HARD_PASS baselines:
  mean_edit_query_wall_us < 5000 (5 ms)  AND post_edit_correctness_rate == 1.0

Returns:
  mean_edit_query_wall_us
  p95_edit_query_wall_us
  p99_edit_query_wall_us
  mean_edit_us  (edit() call alone)
  mean_query_us (retrieve() call alone)
  post_edit_correctness_rate
  n_edits_run
  hard_pass_substrate / hard_pass_baselines
  edit_interpretation: literal string "value_only" so downstream consumers
    know which path was exercised.
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
    M_base = int(config.get("edit_heavy_M_base", config.get("M_base", 2000)))
    N_edits = int(config.get("edit_heavy_N_edits", config.get("N_edits", 5000)))
    dim = int(config.get("dim", 4096))
    seed = _first_seed(config)
    rng = np.random.default_rng(seed + 7200)

    raw = rng.integers(0, 2, size=(M_base, dim), dtype=np.int8).astype(np.float32)
    key_vecs = raw * 2.0 - 1.0
    key_ids = [f"ehs_{i:07d}" for i in range(M_base)]
    values = [f"ev_init_{i}" for i in range(M_base)]

    # Pre-sample edit choices for determinism.
    edit_indices = rng.integers(0, M_base, size=N_edits).tolist()

    return {
        "key_ids": key_ids,
        "key_vecs": key_vecs,
        "values": values,
        "edit_indices": edit_indices,
        "M_base": M_base,
        "N_edits": N_edits,
        "dim": dim,
        "seed": seed,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    key_ids: list[str] = data["key_ids"]
    key_vecs: np.ndarray = data["key_vecs"]
    values: list[str] = data["values"]
    edit_indices: list[int] = data["edit_indices"]
    M_base = int(data["M_base"])
    N_edits = int(data["N_edits"])

    is_substrate = (
        backend.name == "substrate"
        or backend.name.startswith("substrate_v")
        or backend.name == "substrate_sharded"
    )

    # Setup: store all M_base items.
    for i in range(M_base):
        backend.store(key_ids[i], key_vecs[i], values[i])

    edit_only_us: list[float] = []
    query_only_us: list[float] = []
    edit_query_us: list[float] = []
    correct_count = 0
    errors = 0

    for step, idx in enumerate(edit_indices):
        kid = key_ids[idx]
        new_value = f"ev_edit_{step}_for_{idx}"
        kvec = key_vecs[idx]

        t0 = time.perf_counter_ns()
        try:
            backend.edit(kid, new_value)
        except Exception:
            errors += 1
            continue
        t1 = time.perf_counter_ns()
        try:
            res = backend.retrieve(kvec, k=1)
        except Exception:
            errors += 1
            continue
        t2 = time.perf_counter_ns()

        edit_us = (t1 - t0) / 1000.0
        query_us = (t2 - t1) / 1000.0
        eq_us = (t2 - t0) / 1000.0
        edit_only_us.append(edit_us)
        query_only_us.append(query_us)
        edit_query_us.append(eq_us)

        # Correctness: returned value must match new_value AND returned
        # key_id must be the edited one. Substrate may surface
        # near_uniform_flag = True if the value-atom row is shared with
        # another stored key (collision); that still counts as incorrect
        # under "value-only edit" framing.
        if res.value == new_value and res.key_id == kid:
            correct_count += 1

    n_run = len(edit_query_us)
    correctness_rate = correct_count / n_run if n_run else 0.0
    mean_eq_us = float(np.mean(edit_query_us)) if edit_query_us else 0.0

    if is_substrate:
        hard_pass = bool(mean_eq_us < 30000.0 and correctness_rate >= 1.0)
        hp_sub = hard_pass
        hp_bsl = False
    else:
        hard_pass = bool(mean_eq_us < 5000.0 and correctness_rate >= 1.0)
        hp_sub = False
        hp_bsl = hard_pass

    return {
        "scenario": "edit_heavy_stream",
        "backend": backend.name,
        "edit_interpretation": "value_only",
        "edit_interpretation_note": (
            "Value string changes; key vector is unchanged. Baselines need "
            "no index rebuild and win on raw speed. A separate vector-edit "
            "scenario (Phase 2) would invert this comparison."
        ),
        "M_base": M_base,
        "N_edits_requested": N_edits,
        "n_edits_run": n_run,
        "errors": errors,
        "mean_edit_us": float(np.mean(edit_only_us)) if edit_only_us else 0.0,
        "p95_edit_us": _percentile(edit_only_us, 95),
        "mean_query_us": float(np.mean(query_only_us)) if query_only_us else 0.0,
        "p95_query_us": _percentile(query_only_us, 95),
        "mean_edit_query_wall_us": mean_eq_us,
        "p95_edit_query_wall_us": _percentile(edit_query_us, 95),
        "p99_edit_query_wall_us": _percentile(edit_query_us, 99),
        "post_edit_correctness_rate": correctness_rate,
        "hard_pass_substrate": hp_sub,
        "hard_pass_baselines": hp_bsl,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {
                "mean_edit_query_wall_us_lt": 30000.0,
                "post_edit_correctness_rate_ge": 1.0,
            },
            "hard_fail": {
                "mean_edit_query_wall_us_gt": 100000.0,
                "post_edit_correctness_rate_lt": 0.90,
            },
        },
        "baselines": {
            "hard_pass": {
                "mean_edit_query_wall_us_lt": 5000.0,
                "post_edit_correctness_rate_ge": 1.0,
            },
            "hard_fail": {
                "mean_edit_query_wall_us_gt": 20000.0,
                "post_edit_correctness_rate_lt": 0.99,
            },
        },
    }
