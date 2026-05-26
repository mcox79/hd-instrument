"""Oracle-comparison helpers for experiment smoke tests.

Each function checks that an empirical measurement falls within the theoretical
prediction's expected range. Raises AssertionError on out-of-range — used in
--smoke modes to abort early before the full experiment runs.

Pattern: an experiment script's smoke mode runs a small config, computes a
metric, and calls one of these. If the metric is outside the prediction's
sanity band, the script's setup is wrong (not its result is bad — its SETUP).
"""
from __future__ import annotations

from typing import Tuple


def assert_in_range(name: str, measured: float, band: Tuple[float, float]) -> None:
    """Generic helper: raise AssertionError with informative message if out of band."""
    lo, hi = band
    if not (lo <= measured <= hi):
        raise AssertionError(
            f"SANITY FAIL [{name}]: measured={measured:.4f} outside band [{lo:.4f}, {hi:.4f}]. "
            f"Test setup is wrong."
        )


def assert_distinguishable(name: str, a: float, b: float, min_gap: float = 0.10) -> None:
    """For A/B comparisons: assert the two outputs differ by at least min_gap.
    If they're identical, the test isn't measuring whatever distinction it claims to.
    """
    if abs(a - b) < min_gap:
        raise AssertionError(
            f"SANITY FAIL [{name}]: A={a:.4f} vs B={b:.4f}, gap={abs(a-b):.4f} < {min_gap}. "
            f"Methods are indistinguishable under this measurement; test setup is wrong."
        )


def assert_baseline_high(name: str, baseline: float, expected_low: float = 0.85) -> None:
    """For erase/edit tests: assert the no-edit baseline shows high retrieval.
    If baseline is low, the substrate isn't actually storing the facts — bug.
    """
    if baseline < expected_low:
        raise AssertionError(
            f"SANITY FAIL [{name}]: baseline retrieval={baseline:.4f} < {expected_low}. "
            f"Substrate isn't storing facts correctly; test setup is wrong."
        )


def assert_recovery_above_floor(name: str, recovery: float, K: int, N: int,
                                 alpha_c_predicted: float, margin: float = 0.2) -> None:
    """For capacity tests: at K/N well below alpha_c (margin factor), recovery MUST be near 1.
    If recovery is poor below capacity, the test's retrieval mechanism is buggy.
    """
    safe_alpha = alpha_c_predicted * (1 - margin)
    if K / N > safe_alpha:
        return  # Outside the assertable regime
    if recovery < 0.85:
        raise AssertionError(
            f"SANITY FAIL [{name}]: K/N={K/N:.3f} < safe_alpha={safe_alpha:.3f} but "
            f"recovery={recovery:.3f} < 0.85. Retrieval mechanism is broken."
        )
