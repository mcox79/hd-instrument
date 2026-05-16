"""PDF dashboard report generation produces well-formed multi-page output."""

from __future__ import annotations

from pathlib import Path

import torch

from hdlab import atoms, binding, bundling, learning, memory, modulators, tracing
from hdlab.dashboard.report import (
    cleanup_lookup_df,
    events_to_df,
    generate_report,
    hebbian_weights_df,
)


def test_generate_report_writes_pdf(tmp_path: Path) -> None:
    """A diverse workload produces a non-empty PDF with the expected helpers populated."""
    bus = tracing.TraceBus(enabled=True)
    cb = memory.Codebook(256, torch.complex64)
    h = learning.HebbianAssociations(decay=0.05)
    with tracing.using(bus):
        gen = torch.Generator().manual_seed(0)
        for i in range(5):
            v = atoms.make_atom_fhrr(256, gen)
            cb.add(f"a{i}", v)
        a = atoms.make_atom_fhrr(256, gen)
        b = atoms.make_atom_fhrr(256, gen)
        c = binding.bind(a, b)
        _ = bundling.bundle(torch.stack([a, b]))
        _ = cb.lookup(a)
        with modulators.using(reward=1.0, arousal=1.0):
            for _ in range(20):
                h.update(["x", "y"])
    events = bus.flush()

    df = events_to_df(events)
    hw = hebbian_weights_df(events)
    cu = cleanup_lookup_df(events)
    assert not df.empty
    assert not hw.empty
    assert not cu.empty

    output = tmp_path / "report.pdf"
    result = generate_report(events, output, run_name="test", extra={"note": "diverse workload"})
    assert result.exists()
    assert result.stat().st_size > 5_000  # a real multi-page PDF is well over 5 KB


def test_generate_report_empty(tmp_path: Path) -> None:
    """An empty trace produces a valid PDF (overview page only)."""
    output = tmp_path / "empty.pdf"
    result = generate_report([], output, run_name="empty")
    assert result.exists()
    assert result.stat().st_size > 1_000


def test_helpers_return_expected_columns() -> None:
    """events_to_df / hebbian_weights_df / cleanup_lookup_df have stable column sets."""
    df = events_to_df([])
    assert list(df.columns) == [
        "step", "op", "elapsed_ns", "timestamp_ns",
        "attention", "reward", "arousal", "recency",
    ]
    hw = hebbian_weights_df([])
    assert list(hw.columns) == ["hebbian_step", "pair", "weight"]
    cu = cleanup_lookup_df([])
    assert list(cu.columns) == ["step", "name", "score", "k"]
