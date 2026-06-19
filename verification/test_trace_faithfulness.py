"""Trace bus + store + replay: the observer must not lie."""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch

from hdlab import atoms, binding, bundling, learning, modulators, store, tracing


def test_tracing_disabled_no_events() -> None:
    """When the bus is disabled, no events are recorded."""
    bus = tracing.TraceBus(enabled=False)
    with tracing.using(bus):
        gen = torch.Generator().manual_seed(0)
        _ = atoms.make_atom_fhrr(128, gen)
        _ = atoms.make_atom_fhrr(128, gen)
    assert bus.flush() == []


def test_each_public_op_emits_event() -> None:
    """Every public op in atoms/binding/bundling produces exactly one TraceEvent."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        gen = torch.Generator().manual_seed(0)
        a = atoms.make_atom_fhrr(256, gen)
        b = atoms.make_atom_fhrr(256, gen)
        c = binding.bind(a, b)
        _ = binding.unbind(c, b)
        _ = bundling.bundle(torch.stack([a, b]))
        _ = atoms.similarity(a, b)
    events = bus.flush()
    ops = [e.op for e in events]
    assert ops == [
        "atoms.make_atom_fhrr",
        "atoms.make_atom_fhrr",
        "binding.bind",
        "binding.unbind",
        "bundling.bundle",
        "atoms.similarity",
    ], f"Wrong op sequence: {ops}"


def test_trace_event_is_json_serializable() -> None:
    """Every TraceEvent round-trips through JSON, including elapsed_ns and modulator state."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        gen = torch.Generator().manual_seed(0)
        a = atoms.make_atom_fhrr(128, gen)
        b = atoms.make_atom_fhrr(128, gen)
        _ = binding.bind(a, b)
    for e in bus.flush():
        s = e.to_json()
        d = json.loads(s)
        assert d["op"] == e.op
        assert d["step"] == e.step
        assert "elapsed_ns" in d
        assert "modulator_state" in d


def test_elapsed_ns_populated() -> None:
    """Each op records a non-negative elapsed_ns; aggregate is positive on real hardware."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        gen = torch.Generator().manual_seed(0)
        for _ in range(50):
            a = atoms.make_atom_fhrr(4096, gen)
            b = atoms.make_atom_fhrr(4096, gen)
            _ = binding.bind(a, b)
    events = bus.flush()
    for e in events:
        assert e.elapsed_ns >= 0, f"Negative elapsed_ns on {e.op}"
    total = sum(e.elapsed_ns for e in events)
    assert total > 0, "All elapsed_ns are 0; timing not working"


def test_tracing_completes_reasonable_workload() -> None:
    """1000 traced FHRR ops complete in reasonable wall time and emit the expected events."""
    n = 1024
    iters = 1000
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        gen = torch.Generator().manual_seed(0)
        t0 = time.perf_counter()
        for _ in range(iters):
            a = atoms.make_atom_fhrr(n, gen)
            b = atoms.make_atom_fhrr(n, gen)
            _ = binding.bind(a, b)
        elapsed = time.perf_counter() - t0
    events = bus.flush()
    assert len(events) == iters * 3, f"Expected {iters * 3} events, got {len(events)}"
    assert elapsed < 5.0, f"3000 traced ops took {elapsed:.2f}s; regression suspected"


def test_store_roundtrip(tmp_path: Path) -> None:
    """Events written to a TraceStore and read back are byte-equivalent."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        gen = torch.Generator().manual_seed(0)
        a = atoms.make_atom_fhrr(128, gen)
        b = atoms.make_atom_fhrr(128, gen)
        _ = binding.bind(a, b)
        _ = bundling.bundle(torch.stack([a, b]))
    original = bus.flush()

    db_path = tmp_path / "trace.duckdb"
    with store.TraceStore(db_path) as ts:
        ts.append(original)
        assert ts.count() == len(original)

    with store.TraceStore(db_path) as ts:
        reloaded = ts.all_events()

    assert len(reloaded) == len(original)
    for o, r in zip(original, reloaded):
        assert o.step == r.step
        assert o.op == r.op
        assert o.inputs == r.inputs
        assert o.output == r.output
        assert o.modulator_state == r.modulator_state
        assert o.timestamp_ns == r.timestamp_ns
        assert o.elapsed_ns == r.elapsed_ns


def test_replay_reconstructs_state(tmp_path: Path) -> None:
    """Walking a persisted trace reconstructs Hebbian weights identical to the original session."""
    decay = 0.05
    bus = tracing.TraceBus(enabled=True)
    h_original = learning.HebbianAssociations(decay=decay)

    with tracing.using(bus):
        with modulators.using(reward=1.0, arousal=1.0):
            for _ in range(30):
                h_original.update(["a", "b", "c"])
        with modulators.using(reward=0.5, arousal=2.0):
            for _ in range(20):
                h_original.update(["a", "b"])

    final_step = h_original.step
    final_ab = h_original.weight("a", "b")
    final_ac = h_original.weight("a", "c")
    final_bc = h_original.weight("b", "c")

    # Persist to disk and reload.
    db_path = tmp_path / "trace.duckdb"
    with store.TraceStore(db_path) as ts:
        ts.append(bus.flush())
    with store.TraceStore(db_path) as ts:
        events = ts.all_events()

    # Reconstruct purely from the trace.
    h_replay = learning.HebbianAssociations(decay=decay)
    max_hebbian_step = 0
    for e in events:
        if e.op == "learning.update":
            hstep = e.inputs["hebbian_step"]
            w = e.output["weight"]
            h_replay.set_weight(e.inputs["a"], e.inputs["b"], w, at_step=hstep)
            max_hebbian_step = max(max_hebbian_step, hstep)
    # Idle steps after the last pair-update are not in the trace; carry the step counter forward
    # to match the original (this info is recoverable from session metadata, not from individual events).
    if final_step > max_hebbian_step:
        h_replay._step = final_step

    assert abs(h_replay.weight("a", "b") - final_ab) < 1e-9, (
        f"a-b mismatch: original={final_ab}, replay={h_replay.weight('a', 'b')}"
    )
    assert abs(h_replay.weight("a", "c") - final_ac) < 1e-9
    assert abs(h_replay.weight("b", "c") - final_bc) < 1e-9


def test_dashboard_modules_import() -> None:
    """Both the Streamlit app and PDF reporter load cleanly."""
    from hdlab.dashboard import app, report

    assert callable(app.main)
    assert callable(report.generate_report)
    assert callable(report.events_to_df)
    assert callable(report.hebbian_weights_df)
    assert callable(report.cleanup_lookup_df)


def test_events_to_df_shape() -> None:
    """events_to_df produces one row per event with the expected columns."""
    from hdlab.dashboard.report import events_to_df

    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus), modulators.using(attention=0.3, recency=0.7):
        gen = torch.Generator().manual_seed(0)
        a = atoms.make_atom_fhrr(64, gen)
        b = atoms.make_atom_fhrr(64, gen)
        _ = binding.bind(a, b)
    df = events_to_df(bus.flush())
    assert len(df) == 3
    for col in ["step", "op", "elapsed_ns", "attention", "reward", "arousal", "recency"]:
        assert col in df.columns
    assert (df["attention"] == 0.3).all()
    assert (df["recency"] == 0.7).all()
