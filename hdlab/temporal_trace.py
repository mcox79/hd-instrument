"""Stage 2 Spoke 2 -- Foldiak-style temporal-contiguity trace mechanism.

Post-synaptic exponential-decay running trace for use as a Foldiak trace
factor in Hebbian outer-product updates. Given a stream of surface HDs
grouped into documents (each document = temporally-contiguous sentences
about the same concept cluster), the trace maintains a running average
that pulls temporally-adjacent inputs' representations together.

============================================================================
NAMING / SCOPE HONESTY (USER 2026-07-02 mechanism-vs-task-analog distinction)
============================================================================
The MECHANISM (exponential-decay trace + Hebbian on trace-post-synaptic-
factor) IS brain-analog (Foldiak 1991 slow-feature-analysis, complex-cell
learning in V1). The TEST REGIME (supervised synthetic corpus with
designer-imposed 25-cluster structure + per-sentence concept_labels +
document boundaries hand-crafted around concept clusters) is NOT brain-
analog -- brain does unsupervised temporal-contiguity discovery from raw
sensory streams without integer labels and without designer-imposed
document boundaries. Framing this as "brain-analog invariance learning"
overstates scope. Accurate frame:

    "given a stream of surface HDs with designer-supplied document
    boundaries indicating temporal contiguity, the trace mechanism
    pulls temporally-adjacent inputs' representations together via
    Foldiak-style post-synaptic exponential trace."

See:
- feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_
  is_supervised_regime_USER_LOCKED_2026-07-02.md (parent USER-locked rule)
- hdlab.concept_encoder module docstring (sibling scope-honesty template
  for Spoke 1 v3-D competitive-Hebbian)

============================================================================
INPUT REGIME
============================================================================
TemporalTrace.update(x) accepts a real-valued vector (float32/float64) of
shape [n_dim] and returns the current trace state (also float32 [n_dim]).
The caller is responsible for:
- calling reset() at document boundaries so cross-document contamination
  does not leak into the trace
- passing surface HDs (float or bipolar) in a temporally-meaningful order
  (adjacent update() calls represent adjacent-in-time inputs)

============================================================================
MECHANISM
============================================================================
Trace update rule (per Foldiak 1991 / Wiskott 2002 slow-feature-analysis):

    trace_0 = x_0                                  # on first call after reset
    trace_t = alpha * x_t + (1 - alpha) * trace_{t-1}

alpha in (0.0, 1.0]:
- alpha=1.0 collapses to instantaneous (no trace; equivalent to no
  temporal-contiguity mechanism)
- alpha=0.1 gives ~10-step memory (a step is one update() call, typically
  one sentence); Spoke 2 default
- alpha=0.5 gives ~2-step memory (nearly no smoothing; ablation arm)

Document-boundary reset: caller invokes reset() at each document boundary.
Failure to reset produces cross-document contamination -- earlier concept
document's residual trace pollutes the next document's early updates.

============================================================================
COMPUTE ARCHITECTURE (per USER-locked storage-strategy law CG_META
2026-07-02)
============================================================================
Storage strategy: STATEFUL_SINGLE_VECTOR (per-stream running trace; NOT
persistent SHARDED storage of concepts/atoms). The trace is a per-stream
transient buffer that reset()s at document boundaries; it is NOT a
persistent atom table.

This is not a composition-depth concern (no chained retrieval or planning
against the trace). The trace is a pure filter over the input stream,
consumed by downstream Hebbian in the same pass.

============================================================================
Version: v1 (Spoke 2 primitive)
ASCII-only. No emojis. No em dashes.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


class TemporalTrace:
    """Exponential-decay running trace of a vector-valued input stream.

    Foldiak/Wiskott slow-feature-analysis primitive: at each step, blend the
    new input with the running trace, yielding a temporally-smoothed
    representation. Used as the post-synaptic factor in a Hebbian update
    rule so temporally-adjacent inputs pull each other together in weight
    space.

    Args:
        alpha: mixing coefficient in (0.0, 1.0]. Smaller = longer memory.
        n_dim: expected input dimensionality (raises on mismatch in update()).

    State:
        _trace: current trace vector (None until first update() or after
                reset()).

    API:
        update(x) -> trace (returned as a copy; caller may mutate without
                    corrupting state)
        reset() -> None (clears trace so next update() re-seeds)
        state -> property; returns current trace or None
    """

    def __init__(self, alpha: float, n_dim: int) -> None:
        if not (0.0 < float(alpha) <= 1.0):
            raise ValueError(
                f"alpha must be in (0.0, 1.0]; got {alpha!r}"
            )
        if not isinstance(n_dim, int) or n_dim <= 0:
            raise ValueError(
                f"n_dim must be positive int; got {n_dim!r}"
            )
        self.alpha = float(alpha)
        self.n_dim = int(n_dim)
        self._trace: Optional[np.ndarray] = None

    def reset(self) -> None:
        """Clear trace state -- next update() re-seeds from the input."""
        self._trace = None

    def update(self, x: np.ndarray) -> np.ndarray:
        """Blend x into the running trace and return the current trace.

        On the first update() after construction or reset(), the trace is
        seeded to x (no blending; alpha does not apply on step 0).
        Subsequent calls apply the exponential-decay rule:
            trace_t = alpha * x_t + (1 - alpha) * trace_{t-1}

        Args:
            x: np.ndarray shape [n_dim] float (float32 or float64).

        Returns:
            np.ndarray shape [n_dim] float32 -- copy of the current trace.
            Caller may mutate without corrupting internal state.
        """
        x = np.asarray(x)
        if x.ndim != 1:
            raise ValueError(
                f"update expects 1-D input; got shape {x.shape}"
            )
        if x.shape[0] != self.n_dim:
            raise ValueError(
                f"update input dim {x.shape[0]} != TemporalTrace.n_dim "
                f"{self.n_dim}"
            )
        x_f = x.astype(np.float32, copy=False)
        if self._trace is None:
            self._trace = x_f.copy()
        else:
            self._trace = (
                self.alpha * x_f + (1.0 - self.alpha) * self._trace
            ).astype(np.float32)
        return self._trace.copy()

    @property
    def state(self) -> Optional[np.ndarray]:
        """Return current trace state (or None if reset / uninitialized)."""
        return None if self._trace is None else self._trace.copy()


# ---------------------------------------------------------------------------
# Selftests.
# ---------------------------------------------------------------------------

def _selftest_1_seed_on_first_update() -> None:
    """First update after reset seeds trace to input (no blend)."""
    t = TemporalTrace(alpha=0.1, n_dim=4)
    x = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    out = t.update(x)
    if not np.allclose(out, x):
        raise AssertionError(
            f"selftest_1 trace seed mismatch: got {out}, expected {x}"
        )


def _selftest_2_blend_after_seed() -> None:
    """Second update applies alpha blend against seeded trace."""
    t = TemporalTrace(alpha=0.25, n_dim=4)
    x0 = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
    x1 = np.array([4.0, 4.0, 4.0, 4.0], dtype=np.float32)
    _ = t.update(x0)
    out = t.update(x1)
    expected = 0.25 * x1 + 0.75 * x0
    if not np.allclose(out, expected):
        raise AssertionError(
            f"selftest_2 blend mismatch: got {out}, expected {expected}"
        )


def _selftest_3_reset_reseeds() -> None:
    """reset() clears state; next update seeds fresh."""
    t = TemporalTrace(alpha=0.1, n_dim=3)
    _ = t.update(np.array([1.0, 1.0, 1.0], dtype=np.float32))
    _ = t.update(np.array([2.0, 2.0, 2.0], dtype=np.float32))
    t.reset()
    if t.state is not None:
        raise AssertionError("selftest_3 reset() did not clear state")
    x = np.array([9.0, 9.0, 9.0], dtype=np.float32)
    out = t.update(x)
    if not np.allclose(out, x):
        raise AssertionError(
            f"selftest_3 post-reset seed mismatch: got {out}, expected {x}"
        )


def _selftest_4_alpha_1_is_instantaneous() -> None:
    """alpha=1.0 collapses to instantaneous (no memory of prior step)."""
    t = TemporalTrace(alpha=1.0, n_dim=3)
    _ = t.update(np.array([1.0, 2.0, 3.0], dtype=np.float32))
    x1 = np.array([7.0, 8.0, 9.0], dtype=np.float32)
    out = t.update(x1)
    if not np.allclose(out, x1):
        raise AssertionError(
            f"selftest_4 alpha=1.0 not instantaneous: got {out}, expected {x1}"
        )


def _selftest_5_small_alpha_long_memory() -> None:
    """alpha=0.05 gives long memory; after 10 constant-input steps, trace
    approaches the input value asymptotically (not equal, but > 40%)."""
    t = TemporalTrace(alpha=0.05, n_dim=2)
    _ = t.update(np.array([0.0, 0.0], dtype=np.float32))
    x = np.array([1.0, 1.0], dtype=np.float32)
    for _ in range(10):
        out = t.update(x)
    # trace_10 = 1 - (0.95)^10 ~ 0.401
    lo, hi = 0.35, 0.45
    if not (lo <= out[0] <= hi):
        raise AssertionError(
            f"selftest_5 long-memory value {out[0]:.3f} outside [{lo},{hi}]"
        )


def _selftest_6_dim_mismatch_raises() -> None:
    """update() with wrong dim raises ValueError."""
    t = TemporalTrace(alpha=0.1, n_dim=4)
    ok = False
    try:
        t.update(np.array([1.0, 2.0, 3.0], dtype=np.float32))
    except ValueError:
        ok = True
    if not ok:
        raise AssertionError(
            "selftest_6 expected ValueError on dim mismatch"
        )


def _selftest_7_ctor_validation_alpha() -> None:
    """Constructor rejects bad alpha values."""
    for bad in (0.0, -0.1, 1.1, 2.0):
        ok = False
        try:
            TemporalTrace(alpha=bad, n_dim=4)
        except ValueError:
            ok = True
        if not ok:
            raise AssertionError(
                f"selftest_7 expected ValueError on alpha={bad}"
            )


def _selftest_8_ctor_validation_n_dim() -> None:
    """Constructor rejects bad n_dim values."""
    for bad in (0, -3):
        ok = False
        try:
            TemporalTrace(alpha=0.1, n_dim=bad)
        except ValueError:
            ok = True
        if not ok:
            raise AssertionError(
                f"selftest_8 expected ValueError on n_dim={bad}"
            )


def _selftest_9_returned_trace_is_copy() -> None:
    """Mutating returned trace does not corrupt internal state."""
    t = TemporalTrace(alpha=0.5, n_dim=3)
    x = np.array([1.0, 1.0, 1.0], dtype=np.float32)
    out = t.update(x)
    out[0] = 999.0
    x2 = np.array([2.0, 2.0, 2.0], dtype=np.float32)
    out2 = t.update(x2)
    expected = 0.5 * x2 + 0.5 * x  # not 999.0-tainted
    if not np.allclose(out2, expected):
        raise AssertionError(
            f"selftest_9 internal state was mutated via returned copy: "
            f"got {out2}, expected {expected}"
        )


def _selftest_10_scale_sentinel_n_8192() -> None:
    """Scale sentinel at production N=8192 -- no NaN / Inf after many updates."""
    n = 8192
    t = TemporalTrace(alpha=0.1, n_dim=n)
    rng = np.random.default_rng(11)
    for _ in range(200):
        x = rng.standard_normal(n).astype(np.float32)
        _ = t.update(x)
    s = t.state
    if s is None:
        raise AssertionError(
            "selftest_10 trace state None after 200 updates"
        )
    n_nan = int(np.isnan(s).sum())
    n_inf = int(np.isinf(s).sum())
    if n_nan > 0 or n_inf > 0:
        raise AssertionError(
            f"selftest_10 SCALE_SENTINEL at N={n}: n_nan={n_nan} n_inf={n_inf}"
        )


_SELFTESTS = [
    ("1_seed_on_first_update", _selftest_1_seed_on_first_update),
    ("2_blend_after_seed", _selftest_2_blend_after_seed),
    ("3_reset_reseeds", _selftest_3_reset_reseeds),
    ("4_alpha_1_is_instantaneous", _selftest_4_alpha_1_is_instantaneous),
    ("5_small_alpha_long_memory", _selftest_5_small_alpha_long_memory),
    ("6_dim_mismatch_raises", _selftest_6_dim_mismatch_raises),
    ("7_ctor_validation_alpha", _selftest_7_ctor_validation_alpha),
    ("8_ctor_validation_n_dim", _selftest_8_ctor_validation_n_dim),
    ("9_returned_trace_is_copy", _selftest_9_returned_trace_is_copy),
    ("10_scale_sentinel_n_8192", _selftest_10_scale_sentinel_n_8192),
]


def _run_all_selftests() -> dict:
    passed = []
    failed = []
    for name, fn in _SELFTESTS:
        try:
            fn()
            passed.append(name)
            print(f"[temporal_trace selftest] PASS {name}", flush=True)
        except AssertionError as e:
            failed.append((name, str(e)))
            print(f"[temporal_trace selftest] FAIL {name}: {e}", flush=True)
        except Exception as e:  # noqa: BLE001
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(
                f"[temporal_trace selftest] ERROR {name}: "
                f"{type(e).__name__}: {e}",
                flush=True,
            )
    return {
        "n_passed": len(passed),
        "n_failed": len(failed),
        "passed": passed,
        "failed": failed,
    }


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    result = _run_all_selftests()
    print(
        f"[temporal_trace selftest] {result['n_passed']}/{len(_SELFTESTS)} "
        f"passed; failed={[n for n, _ in result['failed']]}",
        flush=True,
    )
    if result["n_failed"] > 0:
        sys.exit(1)
