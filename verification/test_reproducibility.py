"""Same spec + same seed produces bit-identical results in a single process.

True cross-machine determinism is asserted by running this on different machines via CI; here
we verify the in-process invariant that the harness uses seeded generators consistently.
"""

from __future__ import annotations

from pathlib import Path

import torch

from hdlab import atoms, binding, bundling, experiment, learning, modulators


def _reproducibility_workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    n = ctx.spec.n
    a = atoms.make_atom_fhrr(n, gen)
    b = atoms.make_atom_fhrr(n, gen)
    c = binding.bind(a, b)
    bundled = bundling.bundle(torch.stack([a, b]))
    h = learning.HebbianAssociations(decay=0.05)
    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(20):
            h.update(["a", "b"])
    return {
        "atom_a_re_sum": float(a.real.sum()),
        "atom_b_re_sum": float(b.real.sum()),
        "bind_re_sum": float(c.real.sum()),
        "bundle_re_sum": float(bundled.real.sum()),
        "hebbian_weight": h.weight("a", "b"),
    }


def test_deterministic_with_seed(tmp_path: Path) -> None:
    """Two runs of the same spec yield identical numeric outputs."""
    spec1 = experiment.ExperimentSpec(
        name="repro1",
        seed=42,
        n=512,
        output_dir=tmp_path / "r1",
        results_log=tmp_path / "results.md",
    )
    spec2 = experiment.ExperimentSpec(
        name="repro2",
        seed=42,
        n=512,
        output_dir=tmp_path / "r2",
        results_log=tmp_path / "results.md",
    )
    r1 = experiment.run(spec1, _reproducibility_workload)
    r2 = experiment.run(spec2, _reproducibility_workload)
    for key in (
        "atom_a_re_sum",
        "atom_b_re_sum",
        "bind_re_sum",
        "bundle_re_sum",
        "hebbian_weight",
    ):
        v1 = r1.metrics[key]
        v2 = r2.metrics[key]
        assert v1 == v2, f"{key} differs between runs: {v1} vs {v2}"


def test_different_seeds_differ(tmp_path: Path) -> None:
    """Negative control: different seeds produce different atom samples."""
    spec1 = experiment.ExperimentSpec(
        name="repro_s1",
        seed=1,
        n=512,
        output_dir=tmp_path / "s1",
        results_log=tmp_path / "results.md",
    )
    spec2 = experiment.ExperimentSpec(
        name="repro_s2",
        seed=2,
        n=512,
        output_dir=tmp_path / "s2",
        results_log=tmp_path / "results.md",
    )
    r1 = experiment.run(spec1, _reproducibility_workload)
    r2 = experiment.run(spec2, _reproducibility_workload)
    assert r1.metrics["atom_a_re_sum"] != r2.metrics["atom_a_re_sum"]


def test_artifacts_persisted(tmp_path: Path) -> None:
    """The harness writes trace.duckdb, dashboard.pdf, metrics.json, and appends to results log."""
    spec = experiment.ExperimentSpec(
        name="repro_artifacts",
        seed=7,
        n=256,
        output_dir=tmp_path / "art",
        results_log=tmp_path / "results.md",
    )
    result = experiment.run(spec, _reproducibility_workload)
    assert result.trace_path.exists()
    assert result.pdf_path.exists()
    assert result.metrics_path.exists()
    assert spec.results_log.exists()
    assert spec.results_log.read_text().count(spec.name) == 1
