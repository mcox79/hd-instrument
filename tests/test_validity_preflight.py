"""Regression fixtures for experiments/_validity_preflight.py.

Proves the pre-dispatch validity preflight FLAGS all 4 of today's real failures
(each burned a run in VET before the gate existed) and PASSES a clean cell (no
false-positive that would block good cells).

Run with:  python -m pytest tests/test_validity_preflight.py -v

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "experiments"))

from _validity_preflight import (  # type: ignore  # noqa: E402
    ValidityPreflightError,
    assert_full_gates_exercised_at_selftest,
    assert_metric_moves,
    assert_negative_control_fails_with_margin,
    assert_positive_control_passes,
    run_validity_preflight,
)

ENFORCE = "enforce"
WARN = "warn"


# =========================================================================== #
# FIXTURE 1: unwinnable HARD-PASS bar -- positive control cannot clear it.      #
# Replays the grounding-percolation degree-preserving-scramble cell whose      #
# must-fail control was unwinnable by construction.                            #
# =========================================================================== #

def test_fixture1_unwinnable_bar_flagged_enforce():
    # The oracle/synthetic arm that SHOULD clear the bar does NOT -> bar is
    # unwinnable / mis-directed -> BLOCK under enforce.
    with pytest.raises(ValidityPreflightError):
        assert_positive_control_passes(
            False, control_name="oracle_shortcut_graph",
            headline_name="real_beats_scramble_median_hop",
            run_mode="selftest", mode=ENFORCE)


def test_fixture1_unwinnable_bar_warns_not_raises_warn():
    # Warn mode: logs loudly, returns False, does NOT raise (bake period).
    ok = assert_positive_control_passes(
        False, control_name="oracle_shortcut_graph",
        run_mode="selftest", mode=WARN)
    assert ok is False


# =========================================================================== #
# FIXTURE 2: structurally frozen metric -- exact 0.0 while a real readout moves.#
# Replays the ladder FPE readout stuck at EXACTLY 0.0 at 4/6 rungs.            #
# =========================================================================== #

def test_fixture2_frozen_exact_zero_pair_flagged_enforce():
    # FPE readout is 0.0 on both null and known-good input -> broken, not
    # negative -> BLOCK.
    with pytest.raises(ValidityPreflightError):
        assert_metric_moves(
            metric_name="fpe_readout", before=0.0, after=0.0,
            run_mode="selftest", mode=ENFORCE)


def test_fixture2_frozen_series_all_zero_flagged_enforce():
    # values form: every rung exactly 0.0.
    with pytest.raises(ValidityPreflightError):
        assert_metric_moves(
            metric_name="fpe_readout", values=[0.0, 0.0, 0.0, 0.0],
            run_mode="selftest", mode=ENFORCE)


def test_fixture2_frozen_constant_nonzero_series_flagged_enforce():
    # A metric frozen at a constant non-zero value also ignores input.
    with pytest.raises(ValidityPreflightError):
        assert_metric_moves(
            metric_name="fpe_readout", values=[0.3, 0.3, 0.3],
            run_mode="selftest", mode=ENFORCE)


def test_fixture2_frozen_warns_not_raises_warn():
    ok = assert_metric_moves(
        metric_name="fpe_readout", before=0.0, after=0.0,
        run_mode="selftest", mode=WARN)
    assert ok is False


# =========================================================================== #
# FIXTURE 3: FULL-only fail-closed gate not exercised at self-test.            #
# Replays the GNN comparator split-identity assertion armed only at            #
# run_mode=full (self-test used assert_identity=false).                        #
# =========================================================================== #

def test_fixture3_full_only_gate_flagged_enforce():
    with pytest.raises(ValidityPreflightError):
        assert_full_gates_exercised_at_selftest(
            full_fail_closed_gates=["split_identity", "cardinality"],
            exercised_gates={"cardinality"},   # split_identity never fired here
            run_mode="selftest", mode=ENFORCE)


def test_fixture3_full_only_gate_warns_not_raises_warn():
    ok = assert_full_gates_exercised_at_selftest(
        full_fail_closed_gates=["split_identity"],
        exercised_gates=set(),
        run_mode="selftest", mode=WARN)
    assert ok is False


# =========================================================================== #
# FIXTURE 4: nondeterministic must-fail control -- passed once (lucky hit).     #
# Replays the vacuous-smoke gate that passed/failed nondeterministically.      #
# =========================================================================== #

def test_fixture4_nondeterministic_control_flagged_enforce():
    # higher_is_pass: pass region is score >= 0.5. One repeat (0.55) got a lucky
    # hit into the pass region -> not robustly failing -> BLOCK.
    with pytest.raises(ValidityPreflightError):
        assert_negative_control_fails_with_margin(
            control_scores=[0.20, 0.18, 0.55, 0.22],
            headline_threshold=0.5, higher_is_pass=True, margin=0.05,
            control_name="untrained_control", run_mode="selftest", mode=ENFORCE)


def test_fixture4_no_margin_flagged_enforce():
    # All below threshold but one sits inside the margin band (0.48 within 0.05
    # of 0.5) -> no-margin fail -> BLOCK.
    with pytest.raises(ValidityPreflightError):
        assert_negative_control_fails_with_margin(
            control_scores=[0.20, 0.48, 0.22],
            headline_threshold=0.5, higher_is_pass=True, margin=0.05,
            run_mode="selftest", mode=ENFORCE)


def test_fixture4_too_few_repeats_flagged_enforce():
    # Only one repeat -> cannot prove determinism -> BLOCK.
    with pytest.raises(ValidityPreflightError):
        assert_negative_control_fails_with_margin(
            control_scores=[0.20],
            headline_threshold=0.5, higher_is_pass=True, margin=0.05,
            n_repeats_min=3, run_mode="selftest", mode=ENFORCE)


def test_fixture4_lower_is_pass_direction_flagged_enforce():
    # higher_is_pass=False: pass region is score <= threshold. A robust fail
    # needs score >= threshold + margin. 0.51 sits inside the margin band.
    with pytest.raises(ValidityPreflightError):
        assert_negative_control_fails_with_margin(
            control_scores=[0.90, 0.51, 0.88],
            headline_threshold=0.5, higher_is_pass=False, margin=0.05,
            run_mode="selftest", mode=ENFORCE)


def test_fixture4_nondeterministic_warns_not_raises_warn():
    ok = assert_negative_control_fails_with_margin(
        control_scores=[0.20, 0.18, 0.55],
        headline_threshold=0.5, higher_is_pass=True, margin=0.05,
        run_mode="selftest", mode=WARN)
    assert ok is False


# =========================================================================== #
# CLEAN CELL: passes all four checks -> no false-positive that blocks good cells#
# =========================================================================== #

def test_clean_cell_passes_all_four_enforce():
    # 1. positive control clears the bar
    assert assert_positive_control_passes(
        True, control_name="oracle", run_mode="selftest", mode=ENFORCE) is True
    # 2. metric moves under known-good input
    assert assert_metric_moves(
        metric_name="direct_readout", before=0.02, after=0.71,
        run_mode="selftest", mode=ENFORCE) is True
    # 3. every FULL fail-closed gate exercised at self-test
    assert assert_full_gates_exercised_at_selftest(
        full_fail_closed_gates=["split_identity", "cardinality"],
        exercised_gates={"split_identity", "cardinality", "arms_differ"},
        run_mode="selftest", mode=ENFORCE) is True
    # 4. must-fail control fails every repeat with margin
    assert assert_negative_control_fails_with_margin(
        control_scores=[0.20, 0.18, 0.19, 0.21],
        headline_threshold=0.5, higher_is_pass=True, margin=0.05,
        run_mode="selftest", mode=ENFORCE) is True


def test_clean_cell_via_orchestrator_enforce():
    ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": True,
         "control_name": "oracle", "headline_name": "median_hop"},
        {"kind": "metric_moves", "metric_name": "direct_readout",
         "before": 0.02, "after": 0.71},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["split_identity"],
         "exercised_gates": {"split_identity"}},
        {"kind": "negative_control_margin",
         "control_scores": [0.20, 0.18, 0.19],
         "headline_threshold": 0.5, "margin": 0.05},
    ], run_mode="selftest", mode=ENFORCE)
    assert ok is True


def test_orchestrator_blocks_on_first_declared_failure_enforce():
    with pytest.raises(ValidityPreflightError):
        run_validity_preflight([
            {"kind": "positive_control",
             "positive_control_passed_headline_gate": False,
             "control_name": "oracle"},
        ], run_mode="selftest", mode=ENFORCE)


def test_orchestrator_unknown_kind_always_hard_errors():
    # A mistyped kind must never silently skip a gate, even in warn mode.
    with pytest.raises(ValidityPreflightError):
        run_validity_preflight(
            [{"kind": "postive_control", "x": 1}],  # deliberate typo
            run_mode="selftest", mode=WARN)


# =========================================================================== #
# BACKWARD-COMPAT: undeclared checks warn (return True) even under enforce.     #
# =========================================================================== #

def test_missing_positive_control_warns_true_even_enforce():
    assert assert_positive_control_passes(
        None, run_mode="selftest", mode=ENFORCE) is True


def test_missing_metric_move_warns_true_even_enforce():
    assert assert_metric_moves(
        metric_name="unwired", run_mode="selftest", mode=ENFORCE) is True


def test_missing_full_gates_warns_true_even_enforce():
    assert assert_full_gates_exercised_at_selftest(
        None, None, run_mode="selftest", mode=ENFORCE) is True


def test_missing_negative_control_warns_true_even_enforce():
    assert assert_negative_control_fails_with_margin(
        None, 0.5, run_mode="selftest", mode=ENFORCE) is True


# =========================================================================== #
# FULL runs are no-ops: the FULL is the science, not a gate self-check.         #
# =========================================================================== #

def test_full_run_is_noop_positive_control():
    # Even a failing declaration passes through untouched at run_mode=full.
    assert assert_positive_control_passes(
        False, run_mode="full", mode=ENFORCE) is True


def test_full_run_is_noop_metric_moves():
    assert assert_metric_moves(
        metric_name="fpe", before=0.0, after=0.0,
        run_mode="full", mode=ENFORCE) is True


def test_full_run_is_noop_full_gates():
    assert assert_full_gates_exercised_at_selftest(
        ["split_identity"], set(), run_mode="full", mode=ENFORCE) is True


def test_full_run_is_noop_negative_control():
    assert assert_negative_control_fails_with_margin(
        [0.55], 0.5, run_mode="full", mode=ENFORCE) is True


# =========================================================================== #
# MODE RESOLUTION: env-driven default is warn; env=enforce blocks.             #
# =========================================================================== #

def test_env_default_is_warn(monkeypatch):
    monkeypatch.delenv("VALIDITY_PREFLIGHT_MODE", raising=False)
    monkeypatch.delenv("VALIDITY_PREFLIGHT_WARN", raising=False)
    # No explicit mode -> resolves to warn -> returns False, no raise.
    ok = assert_positive_control_passes(False, run_mode="selftest")
    assert ok is False


def test_env_enforce_blocks(monkeypatch):
    monkeypatch.setenv("VALIDITY_PREFLIGHT_MODE", "enforce")
    monkeypatch.delenv("VALIDITY_PREFLIGHT_WARN", raising=False)
    with pytest.raises(ValidityPreflightError):
        assert_positive_control_passes(False, run_mode="selftest")


def test_env_warn_override_beats_enforce(monkeypatch):
    # VALIDITY_PREFLIGHT_WARN=1 forces warn even if MODE=enforce.
    monkeypatch.setenv("VALIDITY_PREFLIGHT_MODE", "enforce")
    monkeypatch.setenv("VALIDITY_PREFLIGHT_WARN", "1")
    ok = assert_positive_control_passes(False, run_mode="selftest")
    assert ok is False


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
