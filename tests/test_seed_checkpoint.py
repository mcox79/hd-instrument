"""Tests for experiments/_seed_checkpoint.py (per-seed resume helper).

Run with:  python -m pytest tests/test_seed_checkpoint.py -v

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "experiments"))

from _seed_checkpoint import (  # type: ignore  # noqa: E402
    aggregate_partials,
    clear_partials,
    list_completed_keys,
    load_partial_key,
    resumable_seeds,
    write_partial,
    write_partial_key,
)


# ---------- empty dir -> all seeds remain ----------

def test_empty_dir_all_seeds_remain(tmp_path):
    seeds = [7, 17, 23, 31, 41]
    done, remaining = resumable_seeds(seeds, tmp_path)
    assert done == []
    assert remaining == seeds


def test_nonexistent_dir_safe(tmp_path):
    fake = tmp_path / "does_not_exist"
    done, remaining = resumable_seeds([1, 2, 3], fake)
    assert done == []
    assert remaining == [1, 2, 3]
    assert list_completed_keys(fake) == []


# ---------- partial dir -> only remaining run ----------

def test_partial_dir_two_of_five_complete(tmp_path):
    seeds = [7, 17, 23, 31, 41]
    # Mark 7 and 23 done
    write_partial(tmp_path, 7, {"retention": 0.91, "max_dev": 0.12})
    write_partial(tmp_path, 23, {"retention": 0.88, "max_dev": 0.15})

    done, remaining = resumable_seeds(seeds, tmp_path)
    assert done == [7, 23]
    assert remaining == [17, 31, 41]


def test_partial_dir_preserves_input_order(tmp_path):
    seeds = [41, 7, 31, 17, 23]   # deliberately scrambled
    write_partial(tmp_path, 17, {"r": 0.5})
    write_partial(tmp_path, 41, {"r": 0.6})

    done, remaining = resumable_seeds(seeds, tmp_path)
    # done preserves the order in which input seeds first appear
    assert done == [41, 17]
    assert remaining == [7, 31, 23]


def test_all_complete_remaining_empty(tmp_path):
    seeds = [7, 17]
    for s in seeds:
        write_partial(tmp_path, s, {"r": 0.9})
    done, remaining = resumable_seeds(seeds, tmp_path)
    assert done == seeds
    assert remaining == []


# ---------- atomicity + corruption recovery ----------

def test_simulate_crash_mid_write_tmp_residue_ignored(tmp_path):
    """A leftover .tmp from a mid-write crash must not satisfy the gate."""
    # Simulate crash mid-write: only the .tmp exists (final json never created).
    tmp_residue = tmp_path / "partial_metrics_17.json.tmp"
    tmp_residue.write_text('{"seed": "17", "retention": 0.5}', encoding="utf-8")

    done, remaining = resumable_seeds([7, 17, 23], tmp_path)
    assert done == []
    assert remaining == [7, 17, 23]
    assert list_completed_keys(tmp_path) == []


def test_corrupted_partial_treated_as_incomplete(tmp_path):
    """A truncated json.load failure causes the seed to be re-run."""
    bad = tmp_path / "partial_metrics_17.json"
    bad.write_text('{"seed": "17", "retention": 0.5', encoding="utf-8")  # truncated

    # Good partial for seed 7 so we exercise the mixed case
    write_partial(tmp_path, 7, {"retention": 0.8})

    done, remaining = resumable_seeds([7, 17, 23], tmp_path)
    assert done == [7]
    assert remaining == [17, 23]


def test_partial_schema_mismatch_rejected(tmp_path):
    """A file with the right name but wrong 'seed' field is rejected."""
    bad = tmp_path / "partial_metrics_17.json"
    bad.write_text(json.dumps({"seed": "99", "retention": 0.5}),
                   encoding="utf-8")

    done, remaining = resumable_seeds([7, 17, 23], tmp_path)
    assert done == []
    assert remaining == [7, 17, 23]


def test_non_dict_partial_rejected(tmp_path):
    """A json file whose top-level is a list / scalar must be rejected."""
    bad = tmp_path / "partial_metrics_17.json"
    bad.write_text("[1, 2, 3]", encoding="utf-8")

    done, remaining = resumable_seeds([17], tmp_path)
    assert done == []
    assert remaining == [17]


def test_partial_missing_seed_field_rejected(tmp_path):
    """A dict partial without 'seed'/'key' must be rejected."""
    bad = tmp_path / "partial_metrics_17.json"
    bad.write_text(json.dumps({"retention": 0.5}), encoding="utf-8")

    done, remaining = resumable_seeds([17], tmp_path)
    assert done == []


# ---------- write + load round-trip ----------

def test_write_partial_round_trip(tmp_path):
    payload = {"retention": 0.91, "max_dev": 0.12, "cells": {"0.5": 0.88}}
    p = write_partial(tmp_path, 7, payload)
    assert p.exists()
    body = load_partial_key(tmp_path, 7)
    assert body is not None
    assert body["seed"] == "7"
    assert body["retention"] == 0.91
    assert body["max_dev"] == 0.12
    assert body["cells"] == {"0.5": 0.88}
    assert "_partial_written_at" in body


def test_write_partial_idempotent_overwrite(tmp_path):
    """Re-writing the same seed must overwrite cleanly (no stale .tmp)."""
    write_partial(tmp_path, 7, {"retention": 0.5})
    write_partial(tmp_path, 7, {"retention": 0.9})
    body = load_partial_key(tmp_path, 7)
    assert body["retention"] == 0.9
    # no .tmp residue
    assert not (tmp_path / "partial_metrics_7.json.tmp").exists()


def test_write_partial_stamps_seed_if_missing(tmp_path):
    """Even if caller forgets seed in payload, helper stamps it."""
    payload = {"retention": 0.91}   # no 'seed'
    write_partial(tmp_path, 7, payload)
    body = load_partial_key(tmp_path, 7)
    assert body["seed"] == "7"


def test_write_partial_respects_explicit_seed(tmp_path):
    """If payload already has 'seed', helper does not overwrite it."""
    payload = {"seed": "7", "retention": 0.91}
    write_partial(tmp_path, 7, payload)
    body = load_partial_key(tmp_path, 7)
    assert body["seed"] == "7"


def test_write_partial_key_with_string_key(tmp_path):
    """Helper accepts non-int keys (e.g. for inverted loops)."""
    write_partial_key(tmp_path, "N4096_seed7", {"bid": 42.5})
    body = load_partial_key(tmp_path, "N4096_seed7")
    assert body is not None
    assert body["bid"] == 42.5


# ---------- aggregate ----------

def test_aggregate_all_seeds(tmp_path):
    seeds = [7, 17, 23]
    for s in seeds:
        write_partial(tmp_path, s, {"retention": 0.8 + s / 100})
    agg = aggregate_partials(tmp_path, seeds)
    assert set(agg.keys()) == {"7", "17", "23"}
    assert abs(agg["7"]["retention"] - 0.87) < 1e-9
    assert abs(agg["17"]["retention"] - 0.97) < 1e-9


def test_aggregate_skips_missing(tmp_path):
    write_partial(tmp_path, 7, {"r": 0.8})
    agg = aggregate_partials(tmp_path, [7, 17, 23])
    assert set(agg.keys()) == {"7"}


def test_aggregate_no_seeds_arg_returns_all(tmp_path):
    write_partial(tmp_path, 7, {"r": 0.8})
    write_partial(tmp_path, 17, {"r": 0.9})
    agg = aggregate_partials(tmp_path)
    assert set(agg.keys()) == {"7", "17"}


# ---------- clear_partials ----------

def test_clear_partials_removes_files(tmp_path):
    write_partial(tmp_path, 7, {"r": 0.8})
    write_partial(tmp_path, 17, {"r": 0.9})
    # also drop a .tmp residue
    (tmp_path / "partial_metrics_99.json.tmp").write_text("{}", encoding="utf-8")
    n = clear_partials(tmp_path)
    assert n == 3
    assert list_completed_keys(tmp_path) == []


def test_clear_partials_leaves_metrics_json(tmp_path):
    """clear_partials must not nuke the final aggregate."""
    write_partial(tmp_path, 7, {"r": 0.8})
    (tmp_path / "metrics.json").write_text('{"verdict": "OK"}', encoding="utf-8")
    clear_partials(tmp_path)
    assert (tmp_path / "metrics.json").exists()


# ---------- realistic end-to-end ----------

def test_resume_after_crash_end_to_end(tmp_path):
    """Run 1: completes 2 of 5 seeds then 'crashes'. Run 2: resumes."""
    seeds = [7, 17, 23, 31, 41]

    # Run 1: simulate 2 completes then crash
    run1_done, run1_remaining = resumable_seeds(seeds, tmp_path)
    assert run1_done == []
    assert run1_remaining == seeds

    write_partial(tmp_path, 7, {"retention": 0.91, "max_dev": 0.12})
    write_partial(tmp_path, 17, {"retention": 0.88, "max_dev": 0.15})
    # simulated CUDA crash after seed 17 -- no further partials written

    # Run 2: fresh process scans dir
    run2_done, run2_remaining = resumable_seeds(seeds, tmp_path)
    assert run2_done == [7, 17]
    assert run2_remaining == [23, 31, 41]

    # Complete run 2
    for s in run2_remaining:
        write_partial(tmp_path, s, {"retention": 0.85, "max_dev": 0.18})

    agg = aggregate_partials(tmp_path, seeds)
    assert set(agg.keys()) == {"7", "17", "23", "31", "41"}
    # run1 data preserved
    assert abs(agg["7"]["retention"] - 0.91) < 1e-9
    assert abs(agg["17"]["max_dev"] - 0.15) < 1e-9
    # run2 data present
    assert abs(agg["41"]["retention"] - 0.85) < 1e-9


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
