"""Verification witnesses for the semantic trace + ablation layer.

The observability layer is meaningless if it lies. These tests prove:
- Every event inside a query_span carries the right query_id (no leakage in or out).
- Semantic emit helpers produce structured events with the documented payload shape.
- Ablation is causal: with ablation active, the gated component is not exercised, and
  the same query without ablation does exercise it.
- The semantic trace is deterministic: same inputs, same trace, byte-equal after stripping
  wall-clock timestamps.
- Round-trip through TraceStore preserves query_id and tags.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

from hdlab import (
    ablation,
    atoms,
    binding,
    learning,
    modulators,
    semantic,
    snapshots,
    store,
    tracing,
)


def _drop_volatile(events):
    """Return event dicts with wall-clock and timing fields zeroed for byte-equality."""
    out = []
    for e in events:
        d = e.to_dict()
        d["timestamp_ns"] = 0
        d["elapsed_ns"] = 0
        out.append(d)
    return out


def test_query_span_stamps_query_id_on_every_event() -> None:
    """Every event inside query_span carries that span's query_id; events outside don't."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        gen = torch.Generator().manual_seed(0)
        outside_atom = atoms.make_atom_fhrr(64, gen)  # noqa: F841
        with tracing.query_span("q-42", kind="multi_hop", source="alice"):
            inside_atom = atoms.make_atom_fhrr(64, gen)  # noqa: F841
            semantic.cleanup_hit("bob", score=0.91, threshold=0.3, hop_idx=0)
        outside_atom_2 = atoms.make_atom_fhrr(64, gen)  # noqa: F841

    events = bus.flush()
    by_op = {e.op: e for e in events}

    # Outside-span events: query_id None
    outside = [e for e in events if e.query_id is None]
    inside = [e for e in events if e.query_id == "q-42"]
    assert len(outside) == 2, f"Expected 2 events outside span, got {len(outside)}"
    assert len(inside) >= 3, f"Expected >=3 events inside span (start, atom, hit, end), got {len(inside)}"

    # query_start carries the kind tag in inputs, and on every inside event tags is propagated
    start = by_op["semantic.query_start"]
    assert start.inputs["query_id"] == "q-42"
    assert start.inputs["kind"] == "multi_hop"
    for e in inside:
        assert e.tags.get("kind") == "multi_hop"
        assert e.tags.get("source") == "alice"

    # query_end exists
    assert "semantic.query_end" in by_op


def test_semantic_helpers_emit_expected_payloads() -> None:
    """Each helper produces the documented event op and payload keys."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        with tracing.query_span("q-1"):
            semantic.hop(0, current="alice")
            semantic.cleanup_hit("bob", 0.8, 0.3, hop_idx=0)
            semantic.relation_activated("parent_of", contribution=0.55, hop_idx=0, n_edges_fired=3)
            semantic.edge_traversed("parent_of", "alice", "bob", weight=0.72, hop_idx=0)
            semantic.modulator_gate("attention", before=0.0, after=0.5, gated_op="memory.lookup")
            semantic.query_answer("bob", confidence=0.91, hops_taken=2)

    ops = [e.op for e in bus.flush() if e.op.startswith("semantic.")]
    expected = {
        "semantic.query_start",
        "semantic.hop",
        "semantic.cleanup_hit",
        "semantic.relation_activated",
        "semantic.edge_traversed",
        "semantic.modulator_gate",
        "semantic.query_answer",
        "semantic.query_end",
    }
    assert expected.issubset(set(ops)), f"Missing ops: {expected - set(ops)}"


def test_ablation_relation_is_causal_for_traversal() -> None:
    """An ablated relation is not traversed; the non-ablated control is."""
    bus = tracing.TraceBus(enabled=True)

    def run(use_ablation: bool):
        with tracing.using(bus), tracing.query_span("q-causal"):
            for relation in ["parent_of", "spouse_of"]:
                if ablation.is_relation_ablated(relation):
                    continue
                semantic.edge_traversed(relation, "alice", "bob", weight=0.5, hop_idx=0)

    bus._buffer.clear()
    run(use_ablation=False)
    control = [e for e in bus.flush() if e.op == "semantic.edge_traversed"]
    relations_seen_control = {e.inputs["relation"] for e in control}
    assert relations_seen_control == {"parent_of", "spouse_of"}

    bus._buffer.clear()
    with ablation.relation("spouse_of"):
        run(use_ablation=True)
    ablated = [e for e in bus.flush() if e.op == "semantic.edge_traversed"]
    relations_seen_ablated = {e.inputs["relation"] for e in ablated}
    assert relations_seen_ablated == {"parent_of"}, (
        f"Ablation failed to gate traversal; saw {relations_seen_ablated}"
    )


def test_ablation_edge_is_directional_symmetric() -> None:
    """An ablated edge is masked in both directions."""
    with ablation.edges("knows", [("alice", "bob")]):
        assert ablation.is_edge_ablated("knows", "alice", "bob")
        assert ablation.is_edge_ablated("knows", "bob", "alice")  # symmetric
        assert not ablation.is_edge_ablated("knows", "alice", "carol")
        assert not ablation.is_edge_ablated("other_rel", "alice", "bob")
    # After exit, the edge is no longer ablated
    assert not ablation.is_edge_ablated("knows", "alice", "bob")


def test_ablation_active_event_emitted() -> None:
    """Entering an ablation scope emits semantic.ablation_active for each target."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        with ablation.relation("rel_x"):
            with ablation.edges("rel_y", [("a", "b"), ("c", "d")]):
                with ablation.modulator("attention"):
                    pass
    events = [e for e in bus.flush() if e.op == "semantic.ablation_active"]
    kinds = sorted((e.inputs["target_kind"], e.inputs["target_id"]) for e in events)
    assert kinds == [
        ("edge", "rel_y:a->b"),
        ("edge", "rel_y:c->d"),
        ("modulator", "attention"),
        ("relation", "rel_x"),
    ]


def test_semantic_trace_is_deterministic() -> None:
    """Re-running the same scripted span produces a byte-identical trace (mod wall-clock)."""

    def scripted_run():
        bus = tracing.TraceBus(enabled=True)
        with tracing.using(bus):
            gen = torch.Generator().manual_seed(123)
            a = atoms.make_atom_fhrr(128, gen)
            b = atoms.make_atom_fhrr(128, gen)
            with tracing.query_span("q-det", kind="test"):
                semantic.hop(0)
                _ = binding.bind(a, b)
                semantic.cleanup_hit("x", 0.6, 0.3, hop_idx=0)
                semantic.edge_traversed("r", "u", "v", weight=0.4, hop_idx=0)
                semantic.query_answer("x", confidence=0.6, hops_taken=1)
        return bus.flush()

    run1 = _drop_volatile(scripted_run())
    run2 = _drop_volatile(scripted_run())
    assert run1 == run2, "Semantic trace is non-deterministic"


def test_query_id_round_trips_through_store(tmp_path: Path) -> None:
    """query_id and tags survive a write-read cycle through TraceStore."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        with tracing.query_span("q-store", kind="multi_hop", source="alice"):
            semantic.hop(0)
            semantic.cleanup_hit("bob", 0.7, 0.3, hop_idx=0)
    original = bus.flush()

    db_path = tmp_path / "trace.duckdb"
    with store.TraceStore(db_path) as ts:
        ts.append(original)
    with store.TraceStore(db_path) as ts:
        reloaded = ts.all_events()

    assert len(reloaded) == len(original)
    for o, r in zip(original, reloaded):
        assert o.query_id == r.query_id, f"query_id lost: {o.query_id!r} -> {r.query_id!r}"
        assert o.tags == r.tags, f"tags lost: {o.tags!r} -> {r.tags!r}"


def test_snapshots_capture_includes_hebbian_state() -> None:
    """A snapshot taken after Hebbian updates contains the current weights."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        h = learning.HebbianAssociations(decay=0.0)
        with modulators.using(reward=1.0, arousal=1.0):
            for _ in range(5):
                h.update(["alice", "bob"])
        with tracing.query_span("q-snap"):
            payload = snapshots.capture("after-warmup", hebbian=h)

    assert "alice|bob" in payload["hebbian_weights"]
    assert payload["hebbian_weights"]["alice|bob"] > 0
    assert payload["hebbian_step"] == 5

    snap_events = [e for e in bus.flush() if e.op == "semantic.snapshot"]
    assert len(snap_events) == 1
    assert snap_events[0].query_id == "q-snap"
    assert snap_events[0].output["label"] == "after-warmup"


def test_snapshot_records_active_ablations() -> None:
    """A snapshot inside an ablation scope records which ablations were active."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        with ablation.relation("rel_a"):
            with tracing.query_span("q-abl"):
                payload = snapshots.capture("during-ablation")
    assert "rel_a" in payload["ablations"]["relations"]


def test_disabled_bus_emits_no_semantic_events() -> None:
    """When the bus is disabled, semantic helpers are zero-cost."""
    bus = tracing.TraceBus(enabled=False)
    with tracing.using(bus):
        with tracing.query_span("q-quiet"):
            semantic.cleanup_hit("x", 0.5, 0.3)
            semantic.edge_traversed("r", "a", "b", weight=0.1)
    assert bus.flush() == []


def test_query_id_does_not_leak_after_exit() -> None:
    """Nested spans restore the outer query_id correctly."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        with tracing.query_span("outer"):
            assert tracing.current_query_id() == "outer"
            with tracing.query_span("inner"):
                assert tracing.current_query_id() == "inner"
            assert tracing.current_query_id() == "outer"
        assert tracing.current_query_id() is None
