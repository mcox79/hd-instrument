"""Declarative experiment harness: seeded RNG, traced execution, persisted artifacts.

Workload pattern:

    def my_workload(ctx: ExperimentContext) -> dict:
        gen = ctx.generator
        # use hdlab.atoms / binding / etc. - tracing is already active
        return {"some_metric": 42.0}

    result = run(ExperimentSpec(name="my_exp", seed=42, n=1024), my_workload)
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import torch

from . import store, tracing
from .dashboard.report import generate_report
from .tracing import TraceEvent


@dataclass
class ExperimentSpec:
    """Declarative experiment configuration."""

    name: str
    seed: int = 42
    n: int = 1024
    dtype: str = "complex64"  # "complex64" (FHRR) or "float32" (HRR)
    output_dir: Path | None = None
    notes_path: Path | None = None
    results_log: Path = field(default_factory=lambda: Path("RESULTS.md"))


@dataclass
class ExperimentContext:
    """Runtime context handed to a workload function."""

    spec: ExperimentSpec
    generator: torch.Generator
    bus: tracing.TraceBus


@dataclass
class ExperimentResult:
    """Outputs of one `run()` invocation."""

    spec: ExperimentSpec
    metrics: dict
    trace_path: Path
    pdf_path: Path
    metrics_path: Path
    events: list[TraceEvent]


def _resolve_dtype(name: str) -> torch.dtype:
    if name == "complex64":
        return torch.complex64
    if name == "float32":
        return torch.float32
    raise ValueError(f"Unsupported dtype: {name}")


def _classify_outcome(metrics: dict[str, Any]) -> str:
    """Heuristic PASS/REVIEW based on common pre-registered criteria in workload metrics."""
    if metrics.get("falsified") is True:
        return "FAIL"
    if metrics.get("review") is True:
        return "REVIEW"
    return "PASS"


def _append_results_log(
    log_path: Path,
    spec: ExperimentSpec,
    metrics: dict[str, Any],
    trace_path: Path,
    pdf_path: Path,
    metrics_path: Path,
) -> None:
    if not log_path.exists():
        log_path.write_text(
            "# Results log\n\n"
            "| Date | Experiment | Outcome | Key metric | Notes |\n"
            "|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    outcome = _classify_outcome(metrics)
    key = metrics.get("headline", "")
    line = (
        f"| {metrics.get('timestamp', '')[:10]} "
        f"| {spec.name} "
        f"| {outcome} "
        f"| {key} "
        f"| [pdf]({pdf_path.as_posix()}) "
        f"[trace]({trace_path.as_posix()}) "
        f"[metrics]({metrics_path.as_posix()}) |\n"
    )
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line)


def run(spec: ExperimentSpec, workload: Callable[[ExperimentContext], dict[str, Any]]) -> ExperimentResult:
    """Execute an experiment: set seeds, trace, persist trace + PDF + metrics, append to results log."""
    out_dir = spec.output_dir if spec.output_dir else Path("data") / spec.name
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(spec.seed)
    gen = torch.Generator().manual_seed(spec.seed)
    bus = tracing.TraceBus(enabled=True)

    workload_metrics: dict[str, Any] = {}
    with tracing.using(bus):
        out = workload(ExperimentContext(spec=spec, generator=gen, bus=bus))
        if out:
            workload_metrics.update(out)

    # Pull out PDF-extras callables before the metrics dict gets JSON-serialized.
    pdf_extras = workload_metrics.pop("_pdf_extras", None)

    events = bus.flush()
    metrics: dict[str, Any] = {
        "spec": {"name": spec.name, "seed": spec.seed, "n": spec.n, "dtype": spec.dtype},
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total_events": len(events),
        "total_wall_time_us": sum(e.elapsed_ns for e in events) / 1000.0,
        **workload_metrics,
    }

    trace_path = out_dir / "trace.duckdb"
    if trace_path.exists():
        trace_path.unlink()
    with store.TraceStore(trace_path) as ts:
        ts.append(events)

    pdf_path = out_dir / "dashboard.pdf"
    extra = {"headline": metrics.get("headline", "")} if metrics.get("headline") else None
    generate_report(events, pdf_path, run_name=spec.name, extra=extra, extra_pages=pdf_extras)

    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, default=str), encoding="utf-8")

    _append_results_log(spec.results_log, spec, metrics, trace_path, pdf_path, metrics_path)

    return ExperimentResult(
        spec=spec,
        metrics=metrics,
        trace_path=trace_path,
        pdf_path=pdf_path,
        metrics_path=metrics_path,
        events=events,
    )
