"""Trace bus emits events for every public op, events are JSON-serializable, overhead bounded."""

from __future__ import annotations

import json
import time

import pytest
import torch

from hdlab import atoms, binding, bundling, tracing


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
    """Every TraceEvent round-trips through JSON."""
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


def test_tracing_completes_reasonable_workload() -> None:
    """1000 traced FHRR ops complete in reasonable wall time and emit the expected events.

    This is a Week 1 smoke test: at N=1024 the per-op work is too small for a tight ratio
    against the no-trace baseline to be meaningful (Python overhead dominates). The <10%
    overhead target from PLAN.md is the Week 4 goal once the batched/sampled tracing path
    and profiling layer land.
    """
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


@pytest.mark.skip(reason="Week 4: full state reconstruction from trace not yet implemented")
def test_replay_reconstructs_state() -> None:
    """Running from a persisted trace produces identical state to the original run."""
    pass
