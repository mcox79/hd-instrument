"""Hebbian update rule produces the predicted dynamics."""

from __future__ import annotations

from hdlab import learning, modulators, tracing
from verification import theory


def test_coactivation_grows_weight() -> None:
    """Sustained co-activation with reward=+1 grows the association weight from 0."""
    h = learning.HebbianAssociations(decay=0.01)
    assert h.weight("a", "b") == 0.0
    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(50):
            h.update(["a", "b"])
    assert h.weight("a", "b") > 5.0, f"weight did not grow: {h.weight('a', 'b')}"


def test_negative_reward_shrinks_weight() -> None:
    """Co-activation with reward=-1 reduces a previously-built association."""
    h = learning.HebbianAssociations(decay=0.01)
    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(30):
            h.update(["a", "b"])
    w_positive = h.weight("a", "b")
    with modulators.using(reward=-1.0, arousal=1.0):
        for _ in range(30):
            h.update(["a", "b"])
    w_after = h.weight("a", "b")
    assert w_after < w_positive, f"expected decrease: {w_positive} -> {w_after}"


def test_no_drift_without_reward_beyond_decay() -> None:
    """With reward=0, weights decay exactly geometrically with no extra drift."""
    decay = 0.05
    h = learning.HebbianAssociations(decay=decay)
    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(20):
            h.update(["a", "b"])
    w_before = h.weight("a", "b")
    steps_idle = 10
    with modulators.using(reward=0.0, arousal=1.0):
        for _ in range(steps_idle):
            h.update(["a", "b"])
    w_after = h.weight("a", "b")
    expected = w_before * (1.0 - decay) ** steps_idle
    assert abs(w_after - expected) < 1e-5, (
        f"drift beyond decay: w_after={w_after}, expected={expected}"
    )


def test_steady_state_matches_theory() -> None:
    """Long-run weight matches the analytic steady-state formula within 1% relative."""
    decay = 0.05
    eta = 1.0  # arousal * reward
    h = learning.HebbianAssociations(decay=decay)
    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(2000):
            h.update(["a", "b"])
    w_empirical = h.weight("a", "b")
    w_theoretical = theory.hebbian_steady_state(eta=eta, decay=decay)
    ratio = w_empirical / w_theoretical
    assert 0.99 < ratio < 1.01, (
        f"steady-state mismatch: empirical={w_empirical:.4f}, "
        f"theoretical={w_theoretical:.4f}, ratio={ratio:.4f}"
    )


def test_arousal_scales_learning_rate() -> None:
    """Doubling arousal at fixed reward doubles the per-step delta (effective eta)."""
    decay = 0.02
    h_low = learning.HebbianAssociations(decay=decay)
    h_high = learning.HebbianAssociations(decay=decay)
    steps = 500
    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(steps):
            h_low.update(["a", "b"])
    with modulators.using(reward=1.0, arousal=2.0):
        for _ in range(steps):
            h_high.update(["a", "b"])
    ratio = h_high.weight("a", "b") / h_low.weight("a", "b")
    assert 1.95 < ratio < 2.05, f"arousal should scale steady state linearly; ratio={ratio:.3f}"


def test_storage_stays_sparse() -> None:
    """Updates over many atom names only allocate entries for actually co-active pairs."""
    h = learning.HebbianAssociations(decay=0.01)
    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(100):
            h.update(["a", "b"])
    assert len(h) == 1
    pairs = [("x0", "x1"), ("x2", "x3"), ("x4", "x5"), ("x6", "x7"), ("x8", "x9")]
    with modulators.using(reward=1.0, arousal=1.0):
        for p in pairs:
            h.update(list(p))
    assert len(h) == 6


def test_weight_update_emits_trace_event() -> None:
    """Every reinforced pair produces exactly one trace event."""
    bus = tracing.TraceBus(enabled=True)
    h = learning.HebbianAssociations(decay=0.01)
    with tracing.using(bus), modulators.using(reward=1.0, arousal=1.0):
        h.update(["a", "b", "c"])  # 3 atoms -> 3 pairs
    events = [e for e in bus.flush() if e.op == "learning.update"]
    assert len(events) == 3, f"expected 3 weight-update events, got {len(events)}"
    keys = sorted([(e.inputs["a"], e.inputs["b"]) for e in events])
    assert keys == [("a", "b"), ("a", "c"), ("b", "c")]
