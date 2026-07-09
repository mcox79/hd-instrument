"""Scaffold-free witness for the ACC/EVC adaptive-halting dial in hdlab.self_manager.

Reproduces the FULL-certified phenomenon in miniature WITHOUT the substrate: on a heterogeneous-
length corpus, a FIXED hop budget over-runs short items (drifting PAST an already-reached goal) and
under-runs long items, while adaptive halting on a clean arrival-confidence signal matches-or-beats
task accuracy at EQUAL average compute -- reallocation, not trimming. The discriminator fires: a
fixed-threshold control at the SAME matched budget must underperform, a scrambled-signal control
collapses toward depth-variance, and a random-depth control confirms the arrival SIGNAL (not variance)
is load-bearing. Also checks the tuner (argmax accuracy-per-compute), the first-crossing reflex, the
controller apply-paths (scalar / numpy), and input validation.

Passes with tracing=False (numpy-only; no substrate tracing state involved).

Certified source: substrate_acc_evc_adaptive_halting_v1 (FULL 5-seed HARD_PASS 2026-07-08;
data/exp_substrate_acc_evc_adaptive_halting_v1/metrics.json:
accpc[FIXED=0.0446 ADAPT=0.1878] acc[FIXED=0.178 ADAPT=0.769] hops[FIXED=4.00 ADAPT=4.10]
scramble_gap=0.812 corr[A=1.000 S=-0.026] closure=1.000). Honest tier MEASURED_MECHANISM (clean
arrival signal; noisy/graded arrival not covered) -- Skunkworks owns landed-VET / cert-atom filing.
"""
from __future__ import annotations

import numpy as np
import pytest

from hdlab.self_manager import (
    accuracy_per_compute,
    tune_halt_threshold,
    run_halting,
    AdaptiveHaltController,
)

FROZEN_DD = 4
L_SUPPORT = np.array([2, 3, 4, 5, 6])  # mean 4 == FROZEN_DD (strongest possible fixed baseline)


def _make_halting_corpus(seed: int, n: int = 4000):
    """Synthetic heterogeneous-length halting problem with a CLEAN arrival-confidence signal.

    Returns (conf, true_L): conf[i, h] = arrival confidence after h hops, peaking (~1) exactly at the
    true arrival hop true_L[i] and low elsewhere (reached-then-drifted physics). An item is 'correct'
    iff it STOPS exactly at true_L (accepts the true target).
    """
    rng = np.random.default_rng(seed)
    true_L = rng.choice(L_SUPPORT, size=n)
    T = int(L_SUPPORT.max()) + 1
    conf = 0.05 * rng.standard_normal((n, T))
    conf[np.arange(n), true_L] += 1.0
    conf = np.clip(conf, -0.3, 1.3)
    return conf, true_L, rng


def _tune_on_calibration(conf, true_L):
    cal = np.arange(conf.shape[0] // 2)
    conf_cal, L_cal = conf[cal], true_L[cal]

    def evaluate(theta):
        hops = run_halting(conf_cal, theta, min_hops=1)
        return (hops == L_cal).astype(np.int8), hops

    return AdaptiveHaltController.tuned([0.15, 0.25, 0.35, 0.45, 0.55], evaluate)


def test_adaptive_beats_fixed_at_equal_compute() -> None:
    """The headline certified claim: adaptive halting beats fixed accuracy at EQUAL average compute."""
    conf, true_L, _ = _make_halting_corpus(seed=0)
    ctrl = _tune_on_calibration(conf, true_L)
    ev = np.arange(conf.shape[0] // 2, conf.shape[0])
    L_ev = true_L[ev]

    hops_fixed = np.full(ev.size, FROZEN_DD, dtype=np.int64)
    hops_adapt = ctrl.run(conf[ev], min_hops=1)
    acc_fixed = float(np.mean(hops_fixed == L_ev))
    acc_adapt = float(np.mean(hops_adapt == L_ev))
    mh_fixed, mh_adapt = float(np.mean(hops_fixed)), float(np.mean(hops_adapt))

    # accuracy strictly and substantially higher...
    assert acc_adapt > acc_fixed + 0.20, (acc_adapt, acc_fixed)
    # ...at equal-or-lower average compute (matched budget; the non-trivial part).
    assert mh_adapt <= mh_fixed * 1.10, (mh_adapt, mh_fixed)
    # accuracy-per-compute win clears the certified >=15% relative HARD_PASS gate.
    apc_fixed = accuracy_per_compute((hops_fixed == L_ev).astype(np.int8), hops_fixed)
    apc_adapt = accuracy_per_compute((hops_adapt == L_ev).astype(np.int8), hops_adapt)
    assert apc_adapt > apc_fixed * 1.15, (apc_adapt, apc_fixed)


def test_discriminator_fires_fixed_at_matched_budget_underperforms() -> None:
    """A fixed-threshold control at the SAME average budget as adaptive must underperform it."""
    conf, true_L, _ = _make_halting_corpus(seed=1)
    ctrl = _tune_on_calibration(conf, true_L)
    ev = np.arange(conf.shape[0] // 2, conf.shape[0])
    L_ev = true_L[ev]

    hops_adapt = ctrl.run(conf[ev], min_hops=1)
    acc_adapt = float(np.mean(hops_adapt == L_ev))
    matched_depth = int(round(float(np.mean(hops_adapt))))
    acc_fixed_matched = float(np.mean(np.full(ev.size, matched_depth) == L_ev))
    assert acc_adapt > acc_fixed_matched + 0.20, (acc_adapt, matched_depth, acc_fixed_matched)


def test_signal_load_bearing_not_depth_variance() -> None:
    """RANDOM_DEPTH control: depth variance ALONE does not match adaptive (the arrival signal does)."""
    conf, true_L, rng = _make_halting_corpus(seed=2)
    ctrl = _tune_on_calibration(conf, true_L)
    ev = np.arange(conf.shape[0] // 2, conf.shape[0])
    L_ev = true_L[ev]

    hops_adapt = ctrl.run(conf[ev], min_hops=1)
    rand_depth = rng.choice(L_SUPPORT, size=ev.size)
    apc_adapt = accuracy_per_compute((hops_adapt == L_ev).astype(np.int8), hops_adapt)
    apc_rand = accuracy_per_compute((rand_depth == L_ev).astype(np.int8), rand_depth)
    assert apc_adapt > apc_rand * 1.5, (apc_adapt, apc_rand)


def test_telemetry_sensitivity_scramble_collapses() -> None:
    """SCRAMBLED_HALT guard: shuffling the arrival signal (matched scale) collapses the gain."""
    conf, true_L, rng = _make_halting_corpus(seed=3)
    ctrl = _tune_on_calibration(conf, true_L)
    ev = np.arange(conf.shape[0] // 2, conf.shape[0])
    L_ev = true_L[ev]

    hops_adapt = ctrl.run(conf[ev], min_hops=1)
    hops_scr = run_halting(conf[ev][rng.permutation(ev.size)], ctrl.theta, min_hops=1)
    apc_adapt = accuracy_per_compute((hops_adapt == L_ev).astype(np.int8), hops_adapt)
    apc_scr = accuracy_per_compute((hops_scr == L_ev).astype(np.int8), hops_scr)
    # scramble collapses toward the random-depth floor (certified scramble_gap=0.812).
    assert apc_scr < apc_adapt * 0.75, (apc_scr, apc_adapt)


def test_genuine_reallocation_not_collapse_to_fixed() -> None:
    """Adaptive genuinely VARIES its depth (does not match fixed by collapsing to a single value)."""
    conf, true_L, _ = _make_halting_corpus(seed=4)
    ctrl = _tune_on_calibration(conf, true_L)
    ev = np.arange(conf.shape[0] // 2, conf.shape[0])
    hops_adapt = ctrl.run(conf[ev], min_hops=1)
    assert float(np.std(hops_adapt)) >= 0.5, float(np.std(hops_adapt))


def test_tuner_picks_argmax_accuracy_per_compute() -> None:
    """tune_halt_threshold returns the accpc-maximizing theta with a full inspectable curve."""
    conf, true_L, _ = _make_halting_corpus(seed=5)
    cal = np.arange(conf.shape[0] // 2)
    conf_cal, L_cal = conf[cal], true_L[cal]

    def evaluate(theta):
        hops = run_halting(conf_cal, theta, min_hops=1)
        return (hops == L_cal).astype(np.int8), hops

    grid = [0.15, 0.25, 0.35, 0.45, 0.55]
    res = tune_halt_threshold(grid, evaluate)
    assert res["theta_star"] in grid
    assert len(res["curve"]) == len(grid)
    # theta_star must be the grid entry with the maximum accpc on the curve.
    best = max(res["curve"], key=lambda r: r["accpc"])
    assert res["theta_star"] == best["theta"]
    assert res["accpc_star"] == pytest.approx(best["accpc"])


def test_run_halting_first_crossing_semantics() -> None:
    """First-crossing reflex: halt at the first hop >= min_hops where confidence >= theta; else ceiling."""
    # rows: (a) crosses at hop 2, (b) never crosses -> ceiling T-1=3, (c) crosses at hop 0 but min_hops gates it.
    conf = np.array([
        [0.0, 0.1, 0.9, 0.9],   # crosses at 2
        [0.0, 0.1, 0.2, 0.1],   # never crosses
        [0.9, 0.9, 0.9, 0.9],   # would cross at 0, but min_hops=1 forces >= 1
    ])
    hops = run_halting(conf, theta=0.5, min_hops=1)
    assert hops.tolist() == [2, 3, 1]
    # min_hops=0 lets the third row halt immediately at 0.
    hops0 = run_halting(conf, theta=0.5, min_hops=0)
    assert hops0.tolist() == [2, 3, 0]


def test_controller_should_halt_scalar_and_array() -> None:
    """should_halt works elementwise on python scalars and numpy arrays with min_hops gating."""
    ctrl = AdaptiveHaltController(0.5)
    assert bool(ctrl.should_halt(0.9)) is True
    assert bool(ctrl.should_halt(0.1)) is False
    conf = np.array([0.9, 0.1, 0.9])
    hops_used = np.array([0, 5, 3])
    mask = ctrl.should_halt(conf, hops_used=hops_used, min_hops=1)
    # row0 arrived but hops_used=0 < min_hops -> not eligible; row2 arrived and eligible.
    assert mask.tolist() == [False, False, True]


def test_input_validation() -> None:
    """Malformed inputs raise rather than silently mis-behave."""
    with pytest.raises(ValueError):
        tune_halt_threshold([], lambda th: (np.zeros(1), np.ones(1)))
    with pytest.raises(ValueError):
        run_halting(np.zeros(5), theta=0.5)  # 1-D, not (n, T)
    with pytest.raises(ValueError):
        accuracy_per_compute(np.array([]), np.array([]))
