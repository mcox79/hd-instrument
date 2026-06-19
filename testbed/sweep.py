"""Sweep driver: cross-product a parameter grid, run the testbed scenarios
at every cell, emit raw CSV + structured JSON + a response-surface report.

Closes Gap 1 (parameter-sweep automation) and Gap 2 (continuous-metric
output for response-surface analysis).

Usage:
    python -m testbed sweep --grid testbed/configs/sweeps/grid_explore.yaml \\
        --backend substrate

Per CLAUDE.md: ASCII only, no em-dashes, terse.
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import itertools
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from testbed.scenarios.continuous_metrics import continuous_metrics


# ---------------------------------------------------------------------------
# YAML loading (reuses __main__ helpers when possible)
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        from testbed.__main__ import _minimal_yaml
        return _minimal_yaml(text)


# ---------------------------------------------------------------------------
# Grid expansion
# ---------------------------------------------------------------------------


def expand_grid(grid: dict[str, list]) -> list[dict[str, Any]]:
    """Cross-product the grid into a list of {param: value} cells.

    Empty grid -> one cell with no overrides.
    """
    if not grid:
        return [{}]
    keys = list(grid.keys())
    value_lists = [list(grid[k]) for k in keys]
    cells: list[dict[str, Any]] = []
    for combo in itertools.product(*value_lists):
        cells.append({k: v for k, v in zip(keys, combo)})
    return cells


def cell_hash(cell: dict[str, Any]) -> str:
    """Stable short hash of a cell's params for use as a file id."""
    blob = json.dumps(cell, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha1(blob).hexdigest()[:10]


# ---------------------------------------------------------------------------
# Config overlay
# ---------------------------------------------------------------------------


def apply_cell(base_config: dict, cell: dict[str, Any]) -> dict:
    """Return base_config with cell overrides applied at the top level.

    Special handling: codebook_C overrides codebook_scale derived from N.
    """
    cfg = dict(base_config)
    for k, v in cell.items():
        cfg[k] = v
    # If both N and codebook_C are set, derive codebook_scale so the substrate
    # ctor actually uses the requested codebook size.
    if "codebook_C" in cfg and "N" in cfg:
        try:
            N = int(cfg["N"])
            C = int(cfg["codebook_C"])
            if N > 0 and C >= N:
                cfg["codebook_scale"] = max(1, C // N)
        except (TypeError, ValueError):
            pass
    # Mirror N -> dim for scenarios that read dim.
    if "N" in cfg and "dim" not in cell:
        cfg["dim"] = int(cfg["N"])
    return cfg


# ---------------------------------------------------------------------------
# Per-cell runner
# ---------------------------------------------------------------------------


def _build_backend_for_cell(name: str, config: dict):
    """Defer to __main__'s _build_backend to keep one backend factory.

    Workaround: when the user asks for "substrate" the variants registry
    returns SubstrateV1Reference whose .name attribute is "substrate_v1".
    Several scenarios (hallu_detect, storage_latency) dispatch their
    fresh-backend factory off backend.name == "substrate". Without this
    normalization the factory falls through to cls() with no kwargs and
    builds a default-N=4096 substrate, which mismatches the cell's N.
    We rebind name to the user-facing alias just for the request name.
    """
    from testbed.__main__ import _build_backend
    backend = _build_backend(name, config)
    nm = name.strip().lower() if isinstance(name, str) else name
    if nm == "substrate":
        try:
            backend.name = "substrate"
        except AttributeError:
            pass
    return backend


def _scenario_module(name: str):
    return importlib.import_module(f"testbed.scenarios.{name}")


def _run_one_cell(
    cell: dict[str, Any],
    base_config: dict,
    scenarios: list[str],
    backends: list[str],
    cells_dir: Path,
) -> list[dict]:
    """Run all (scenario, backend) pairs at one grid cell.

    Returns a list of row dicts suitable for CSV output.
    """
    cfg = apply_cell(base_config, cell)
    chash = cell_hash(cell)
    rows: list[dict] = []
    per_cell: dict[str, Any] = {
        "cell_hash": chash,
        "cell": cell,
        "config": cfg,
        "scenarios": scenarios,
        "backends": backends,
        "results": [],
        "errors": [],
    }

    for backend_name in backends:
        for scen in scenarios:
            row: dict[str, Any] = {
                "cell_hash": chash,
                "backend": backend_name,
                "scenario": scen,
            }
            # Inject grid params as columns.
            for k, v in cell.items():
                row[k] = v
            try:
                mod = _scenario_module(scen)
            except ImportError as exc:
                row["error"] = f"import: {exc}"
                per_cell["errors"].append({"scenario": scen, "backend": backend_name,
                                           "stage": "import", "error": str(exc)})
                rows.append(row)
                continue
            try:
                data = mod.setup(cfg)
            except Exception as exc:
                row["error"] = f"setup: {exc}"
                per_cell["errors"].append({"scenario": scen, "backend": backend_name,
                                           "stage": "setup", "error": str(exc)})
                rows.append(row)
                continue
            try:
                backend = _build_backend_for_cell(backend_name, cfg)
            except Exception as exc:
                row["error"] = f"build: {exc}"
                per_cell["errors"].append({"scenario": scen, "backend": backend_name,
                                           "stage": "build", "error": str(exc)})
                rows.append(row)
                continue
            t0 = time.perf_counter()
            try:
                metrics = mod.run(backend, data)
                wall_s = time.perf_counter() - t0
                if not isinstance(metrics, dict):
                    metrics = {"result": metrics}
                metrics["wall_s"] = wall_s
            except Exception as exc:
                wall_s = time.perf_counter() - t0
                row["error"] = f"run: {exc}"
                row["wall_s"] = wall_s
                per_cell["errors"].append({
                    "scenario": scen, "backend": backend_name, "stage": "run",
                    "error": f"{exc}\n{traceback.format_exc()}",
                })
                rows.append(row)
                continue

            cont = continuous_metrics(scen, metrics)
            for k, v in cont.items():
                row[k] = v
            row["wall_s"] = float(metrics.get("wall_s", wall_s))
            per_cell["results"].append({
                "scenario": scen,
                "backend": backend_name,
                "metrics": metrics,
                "continuous": cont,
            })
            rows.append(row)

    cells_dir.mkdir(parents=True, exist_ok=True)
    out_path = cells_dir / f"{chash}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(per_cell, f, indent=2, default=str)
    return rows


# ---------------------------------------------------------------------------
# CSV / summary writers
# ---------------------------------------------------------------------------


def _collect_columns(rows: list[dict]) -> list[str]:
    """Stable column ordering: cell_hash, backend, scenario, grid params, metrics."""
    grid_keys: list[str] = []
    metric_keys: list[str] = []
    fixed = {"cell_hash", "backend", "scenario"}
    for row in rows:
        for k in row.keys():
            if k in fixed:
                continue
            if k in ("error", "wall_s"):
                continue
            if isinstance(row.get(k), (int, float, bool)) and k not in metric_keys:
                # Heuristic: grid params are int/float and have small value count;
                # metrics tend to be floats. We treat known scenario metrics as
                # metric_keys via _continuous_metrics; everything else is grid.
                pass
    # Easier: peek at the first row's cell to find grid params.
    seen_grid: list[str] = []
    seen_metric: list[str] = []
    for row in rows:
        for k in row.keys():
            if k in fixed or k in ("error",):
                continue
            if k == "wall_s":
                if k not in seen_metric:
                    seen_metric.append(k)
                continue
            # Anything declared in cell (grid) we want to identify; we infer it
            # by checking against the first cell's keys. Since cells are
            # appended uniformly, we track via order.
            if k not in seen_grid and k not in seen_metric:
                # Default: append to metric; we'll re-sort grid via row context.
                seen_metric.append(k)
    return ["cell_hash", "backend", "scenario"] + seen_metric + ["error"]


def write_raw_csv(rows: list[dict], path: Path, grid_keys: list[str]) -> None:
    """Write rows to CSV. Column order: cell_hash, backend, scenario,
    grid params, metric columns (alphabetical), wall_s, error."""
    if not rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("cell_hash,backend,scenario\n")
        return

    metric_cols: set[str] = set()
    for row in rows:
        for k in row.keys():
            if k in ("cell_hash", "backend", "scenario", "error", "wall_s"):
                continue
            if k in grid_keys:
                continue
            metric_cols.add(k)
    metric_cols_sorted = sorted(metric_cols)

    cols = ["cell_hash", "backend", "scenario"] + list(grid_keys) + metric_cols_sorted + ["wall_s", "error"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            out = {c: row.get(c, "") for c in cols}
            w.writerow(out)


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------


def _iso_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")


def run_sweep(
    grid_path: Path,
    backend_override: list[str] | None = None,
    out_root: Path | None = None,
) -> dict:
    """Run the full sweep and emit raw.csv, sweep_summary.json,
    response_surface.md. Returns a dict with paths + counts.
    """
    grid_cfg = _load_yaml(grid_path)
    base_cfg_path = grid_cfg.get("base_config")
    if not base_cfg_path:
        raise ValueError("sweep grid YAML must set 'base_config'")
    base_cfg = _load_yaml(Path(base_cfg_path))

    scenarios = list(grid_cfg.get("scenarios") or [
        "point_recall", "edit_isolation", "deletion_verify",
        "hallu_detect", "continual_4stage", "storage_latency",
    ])
    backends = list(backend_override or grid_cfg.get("backends") or ["substrate"])
    grid = dict(grid_cfg.get("grid") or {})

    cells = expand_grid(grid)
    grid_keys = list(grid.keys())

    out_root = out_root or Path("testbed_data/benchmarks")
    ts = _iso_ts()
    sweep_dir = Path(out_root) / "sweeps" / ts
    cells_dir = sweep_dir / "cells"
    sweep_dir.mkdir(parents=True, exist_ok=True)

    print(f"[sweep] grid={grid_path} cells={len(cells)} "
          f"scenarios={len(scenarios)} backends={len(backends)}")
    print(f"[sweep] out={sweep_dir}")

    t0 = time.perf_counter()
    all_rows: list[dict] = []
    cell_summaries: list[dict] = []
    for i, cell in enumerate(cells):
        print(f"[sweep] cell {i+1}/{len(cells)}: {cell}")
        cell_rows = _run_one_cell(cell, base_cfg, scenarios, backends, cells_dir)
        all_rows.extend(cell_rows)
        cell_summaries.append({
            "cell_hash": cell_hash(cell),
            "cell": cell,
            "n_rows": len(cell_rows),
            "n_errors": sum(1 for r in cell_rows if r.get("error")),
        })
    wall = time.perf_counter() - t0

    raw_csv = sweep_dir / "raw.csv"
    write_raw_csv(all_rows, raw_csv, grid_keys)

    summary = {
        "timestamp": ts,
        "grid_path": str(grid_path),
        "base_config_path": str(base_cfg_path),
        "scenarios": scenarios,
        "backends": backends,
        "grid": grid,
        "n_cells": len(cells),
        "n_rows": len(all_rows),
        "wall_s": wall,
        "cells": cell_summaries,
    }
    summary_path = sweep_dir / "sweep_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    # Response surface analysis.
    from testbed.response_surface import render_response_surface
    rs_path = sweep_dir / "response_surface.md"
    md = render_response_surface(raw_csv, grid_keys, scenarios, backends)
    rs_path.write_text(md, encoding="utf-8")

    print(f"[sweep] wrote {raw_csv}")
    print(f"[sweep] wrote {summary_path}")
    print(f"[sweep] wrote {rs_path}")
    print(f"[sweep] wall {wall:.2f}s n_rows={len(all_rows)}")

    return {
        "sweep_dir": sweep_dir,
        "raw_csv": raw_csv,
        "summary": summary_path,
        "response_surface": rs_path,
        "wall_s": wall,
        "n_rows": len(all_rows),
        "n_cells": len(cells),
    }


# ---------------------------------------------------------------------------
# CLI entry point (callable from __main__.py)
# ---------------------------------------------------------------------------


def cmd_sweep(args) -> int:
    grid_path = Path(args.grid)
    if not grid_path.exists():
        print(f"[sweep] grid not found: {grid_path}", file=sys.stderr)
        return 2
    backends = None
    if getattr(args, "backend", None):
        backends = [b.strip() for b in args.backend.split(",") if b.strip()]
    out_root = Path(args.out_dir) if getattr(args, "out_dir", None) else None
    try:
        result = run_sweep(grid_path, backend_override=backends, out_root=out_root)
    except Exception as exc:
        print(f"[sweep] FAILED: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1
    if result["n_rows"] == 0:
        print("[sweep] zero rows produced", file=sys.stderr)
        return 3
    return 0
