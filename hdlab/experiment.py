"""Declarative experiment definition and runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExperimentSpec:
    """Declarative experiment: dataset, seed, modulator schedule, learning rule, metrics, output paths."""

    name: str
    seed: int
    output_dir: Path


def run(spec: ExperimentSpec) -> dict:
    """Execute an experiment and return its metrics."""
    raise NotImplementedError("Week 5")
