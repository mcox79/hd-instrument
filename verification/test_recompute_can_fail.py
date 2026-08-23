"""Scaffold-free witness for harness_cannot_recompute: a re-run through the fresh path CAN FAIL.

Runs with no tracing and no substrate dependency. Three independent claims:

  1. REDIRECT INVARIANTS -- fresh_recompute.fresh_run_output_dir is a no-op with the env unset
     (backward-compatible) and a NEW sibling with a tag set (landed dir never targeted).
  2. FALSIFICATION PROTOCOL (hermetic, real tools.exp_checkpoint + real write_metrics):
       naive re-run          -> REPLAYED_NOT_A_REPRODUCTION, verdict unchanged, 0 units computed
       fresh, same input     -> RECOMPUTED, verdict REPRODUCES        (negative control)
       fresh, corrupt input  -> RECOMPUTED, verdict CHANGES           (deciding control -- CAN FAIL)
       base dir byte-identical across every fresh re-run; units.jsonl never mutated by any re-run
  3. REAL-ARCHIVE CONTRACT -- the census sees real replay cells, and a small real sample exercised
     through the actual replay path (completed_units/load_units) classifies REPLAYED, read-only.

Run:  python verification/test_recompute_can_fail.py
      (or via pytest: the test_* functions assert the same claims)
ASCII-only. No em dashes in output.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
import tempfile
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.fresh_recompute import fresh_run_output_dir, FRESH_ENV, _selftest as _fr_selftest
from experiments.exp_recompute_falsification_demo_v1 import falsification_protocol
from experiments.exercise_replay_sample import exercise
from tools.reproduction_check import census


def test_redirect_invariants():
    """Env unset -> unchanged (backward compatible); tag -> a distinct sibling."""
    saved = os.environ.pop(FRESH_ENV, None)
    try:
        base = "/repo/data/exp_x_v1"
        assert fresh_run_output_dir(base) == base, "unset env must be a no-op"
        sib = fresh_run_output_dir(base, "t")
        assert sib == base + "__fresh_t" and sib != base, "tag must yield a distinct sibling"
        assert fresh_run_output_dir(sib, "t") == sib, "idempotent"
    finally:
        if saved is not None:
            os.environ[FRESH_ENV] = saved
    assert _fr_selftest(), "fresh_recompute self-test failed"


def test_falsification_protocol_can_fail():
    """The whole bar, hermetic: negative control reproduces, deciding control flips the verdict."""
    with tempfile.TemporaryDirectory(prefix="recompute_witness_") as td:
        rec = falsification_protocol(Path(td))
    steps = {s["name"]: s for s in rec["steps"]}

    assert steps["NAIVE_RERUN"]["status"] == "REPLAYED_NOT_A_REPRODUCTION"
    assert steps["NAIVE_RERUN"]["n_computed"] == 0
    assert steps["NAIVE_RERUN"]["verdict"] == rec["v0"], "the incident: replay returns V0 with no work"

    assert steps["FRESH_SAME_INPUT"]["status"] == "RECOMPUTED"
    assert steps["FRESH_SAME_INPUT"]["verdict"] == rec["v0"], "negative control must reproduce"

    assert steps["FRESH_CORRUPT_INPUT"]["status"] == "RECOMPUTED"
    assert steps["FRESH_CORRUPT_INPUT"]["verdict"] != rec["v0"], \
        "deciding control: a fresh re-run must be ABLE to fail"
    assert rec["v0"] == "HARD_PASS" and rec["v_corrupt"] == "HARD_FAIL"

    assert rec["units_shard_immutable"], "units.jsonl must never be mutated by a re-run"
    assert rec["fresh_path_never_touched_base"], "fresh path must never touch the landed dir"


def test_real_archive_sample_replays():
    """A small real sample, exercised read-only through the real replay path, all classify REPLAYED."""
    landed, replay_landed, orphan, rows = census()
    assert replay_landed > 0, "census should see real replay cells (positive control)"
    rep = exercise(8)
    assert rep["n_sampled"] >= 1
    assert rep["n_replayed"] == rep["n_sampled"], "every sampled real cell must replay"
    assert rep["all_byte_identical"], "exercising the sample must not mutate any landed dir"


def _main() -> int:
    ok = True
    for fn in (test_redirect_invariants, test_falsification_protocol_can_fail,
               test_real_archive_sample_replays):
        try:
            fn()
            print("[witness] PASS", fn.__name__)
        except AssertionError as e:
            ok = False
            print("[witness] FAIL", fn.__name__, "--", e, file=sys.stderr)
    print("[witness] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main())
