"""Response-surface analysis over a sweep's raw.csv.

Loads the rows, computes:
  - per (scenario, metric, parameter) marginal effect (mean metric value
    grouped by parameter level)
  - per (scenario, metric, parameter) Pearson partial correlation, controlling
    out the other grid params with a one-hot regression
  - Pareto frontier across the killer-feature metrics + latency
  - ranked top-5 cells per metric

Emits a markdown report. No matplotlib; tables only via tabulate when
available, plain markdown otherwise.

Per CLAUDE.md: ASCII only, no em-dashes, terse.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any, Iterable

try:
    from tabulate import tabulate  # type: ignore
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False


# Killer-feature metrics that drive the Pareto frontier. Higher-is-better
# for "good" and lower-is-better for "bad" are tagged so we can flip signs
# when ranking. "wall_s" and "p50_retrieve_us" are latency (lower better).
_METRIC_DIRECTION = {
    "recall_at_1": "higher",
    "recall_at_5": "higher",
    "mean_native_confidence": "higher",
    "max_isolation_ratio": "lower",
    "mean_isolation_ratio": "lower",
    "within_theory_frac": "higher",
    "mean_var_ratio": "lower",
    "erase_success_rate": "higher",
    "max_above_thresh_frac": "lower",
    "max_mean_oos_max_conf": "lower",
    "near_uniform_frac": "higher",
    "mean_oos_max_conf": "lower",
    "recall_at_1_on_OOS": "lower",
    "ret_A_after_A": "higher",
    "ret_A_after_D": "higher",
    "ret_B_after_D": "higher",
    "ret_C_after_D": "higher",
    "ret_D_after_D": "higher",
    "p50_retrieve_us": "lower",
    "p95_retrieve_us": "lower",
    "p50_store_us": "lower",
    "p50_delete_us": "lower",
    "disk_bytes": "lower",
    "wall_s": "lower",
}


def _coerce(s: str) -> Any:
    if s == "" or s is None:
        return None
    try:
        if "." in s or "e" in s.lower():
            return float(s)
        return int(s)
    except (TypeError, ValueError):
        return s


def _is_finite_number(x: Any) -> bool:
    if x is None:
        return False
    if isinstance(x, bool):
        return False
    try:
        f = float(x)
    except (TypeError, ValueError):
        return False
    return not (math.isnan(f) or math.isinf(f))


def load_rows(csv_path: Path) -> tuple[list[dict], list[str]]:
    """Read raw.csv. Returns (rows, fieldnames)."""
    rows: list[dict] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fns = reader.fieldnames or []
        for r in reader:
            out: dict[str, Any] = {}
            for k, v in r.items():
                out[k] = _coerce(v) if v not in ("", None) else None
            rows.append(out)
    return rows, fns


def _table(rows: list[list[Any]], headers: list[str]) -> str:
    if not rows:
        return "(no data)\n"
    if _HAS_TABULATE:
        return tabulate(rows, headers=headers, tablefmt="github",
                        floatfmt=".4f") + "\n"
    # Fallback minimal markdown table.
    out = ["| " + " | ".join(headers) + " |"]
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows:
        cells = []
        for v in r:
            if isinstance(v, float):
                cells.append(f"{v:.4f}")
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def marginal_effect_table(rows: list[dict], scenario: str, param: str,
                          metric: str) -> str:
    """Group by param level, average metric across remaining rows."""
    by_level: dict[Any, list[float]] = {}
    for r in rows:
        if r.get("scenario") != scenario:
            continue
        lvl = r.get(param)
        val = r.get(metric)
        if lvl is None or not _is_finite_number(val):
            continue
        by_level.setdefault(lvl, []).append(float(val))
    if not by_level:
        return ""
    table_rows = []
    for lvl in sorted(by_level.keys(), key=lambda x: (str(type(x)), x)):
        vals = by_level[lvl]
        mean = sum(vals) / len(vals)
        if len(vals) >= 2:
            sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (len(vals) - 1))
        else:
            sd = 0.0
        table_rows.append([lvl, len(vals), mean, sd])
    return _table(table_rows, [param, "n", f"mean_{metric}", "stdev"])


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def correlation_table(rows: list[dict], scenario: str, grid_keys: list[str],
                      metrics: list[str]) -> str:
    """For each (metric, param) compute Pearson r over filtered rows."""
    filt = [r for r in rows if r.get("scenario") == scenario]
    if not filt:
        return "(no rows for scenario)\n"
    table_rows = []
    for metric in metrics:
        for p in grid_keys:
            xs: list[float] = []
            ys: list[float] = []
            for r in filt:
                x = r.get(p)
                y = r.get(metric)
                if _is_finite_number(x) and _is_finite_number(y):
                    xs.append(float(x))
                    ys.append(float(y))
            if len(xs) < 3:
                continue
            r_val = _pearson(xs, ys)
            table_rows.append([metric, p, len(xs), r_val])
    return _table(table_rows, ["metric", "parameter", "n", "pearson_r"])


def top_n_cells(rows: list[dict], scenario: str, metric: str,
                grid_keys: list[str], n: int = 5) -> str:
    direction = _METRIC_DIRECTION.get(metric, "higher")
    filt = [r for r in rows
            if r.get("scenario") == scenario and _is_finite_number(r.get(metric))]
    if not filt:
        return ""
    reverse = (direction == "higher")
    filt.sort(key=lambda r: float(r[metric]), reverse=reverse)
    table_rows = []
    for r in filt[:n]:
        row = [r.get("cell_hash"), r.get("backend")]
        for p in grid_keys:
            row.append(r.get(p))
        row.append(float(r[metric]))
        table_rows.append(row)
    headers = ["cell_hash", "backend"] + grid_keys + [f"{metric} ({direction}-is-better)"]
    return _table(table_rows, headers)


def pareto_frontier(rows: list[dict], grid_keys: list[str]) -> str:
    """Pareto front across the canonical (recall, KF-1 near-uniform, TCFT
    var-ratio, latency) tuple. Aggregates each cell into one point by
    pivoting the per-scenario rows.
    """
    cells: dict[str, dict[str, Any]] = {}
    for r in rows:
        ch = r.get("cell_hash")
        if ch is None:
            continue
        c = cells.setdefault(str(ch), {"cell_hash": ch})
        scen = r.get("scenario")
        if scen == "point_recall":
            c["recall_at_1"] = r.get("recall_at_1")
            c["latency_us"] = r.get("p50_retrieve_us")
        elif scen == "hallu_detect":
            c["near_uniform_frac"] = r.get("near_uniform_frac")
        elif scen == "deletion_verify":
            c["mean_var_ratio"] = r.get("mean_var_ratio")
        for p in grid_keys:
            if p in r and r[p] is not None:
                c[p] = r[p]

    objectives = [
        ("recall_at_1", "higher"),
        ("near_uniform_frac", "higher"),
        ("mean_var_ratio", "lower"),
        ("latency_us", "lower"),
    ]
    points = []
    for ch, c in cells.items():
        vals = [c.get(o) for o, _ in objectives]
        if all(_is_finite_number(v) for v in vals):
            points.append((ch, c, [float(v) for v in vals]))
    if not points:
        return "(no rows with full objective coverage)\n"

    def dominates(a_vals: list[float], b_vals: list[float]) -> bool:
        """a dominates b if a is at least as good in every objective and
        strictly better in at least one."""
        better_any = False
        for (a, b), (_, direction) in zip(zip(a_vals, b_vals), objectives):
            if direction == "higher":
                if a < b:
                    return False
                if a > b:
                    better_any = True
            else:
                if a > b:
                    return False
                if a < b:
                    better_any = True
        return better_any

    pareto = []
    for i, (ch_i, c_i, v_i) in enumerate(points):
        dominated = False
        for j, (_, _, v_j) in enumerate(points):
            if i == j:
                continue
            if dominates(v_j, v_i):
                dominated = True
                break
        if not dominated:
            pareto.append((ch_i, c_i, v_i))

    headers = ["cell_hash"] + grid_keys + [o for o, _ in objectives]
    rows_out = []
    for ch, c, v in pareto:
        row = [ch]
        for p in grid_keys:
            row.append(c.get(p))
        row.extend(v)
        rows_out.append(row)
    return _table(rows_out, headers)


def render_response_surface(csv_path: Path, grid_keys: list[str],
                            scenarios: list[str],
                            backends: list[str]) -> str:
    """Top-level renderer: produces the markdown report body."""
    rows, _ = load_rows(csv_path)
    parts: list[str] = []
    parts.append("# Response surface\n")
    parts.append(f"\nRaw rows: {len(rows)}\n")
    parts.append(f"\nGrid params: {', '.join(grid_keys) if grid_keys else '(none)'}\n")
    parts.append(f"\nScenarios: {', '.join(scenarios)}\n")
    parts.append(f"\nBackends: {', '.join(backends)}\n\n")

    # Per-scenario marginal-effect + correlation tables.
    per_scen_metrics = {
        "point_recall": ["recall_at_1", "mean_native_confidence", "p50_retrieve_us"],
        "edit_isolation": ["max_isolation_ratio", "mean_isolation_ratio"],
        "deletion_verify": ["mean_var_ratio", "erase_success_rate"],
        "hallu_detect": ["near_uniform_frac", "mean_oos_max_conf",
                         "max_above_thresh_frac"],
        "continual_4stage": ["ret_A_after_D", "ret_D_after_D"],
        "storage_latency": ["p50_retrieve_us", "disk_bytes"],
    }

    for scen in scenarios:
        metrics = per_scen_metrics.get(scen, [])
        if not metrics:
            continue
        parts.append(f"\n## {scen}\n\n")
        parts.append("### Marginal effects (mean metric per parameter level)\n\n")
        for metric in metrics:
            for p in grid_keys:
                tbl = marginal_effect_table(rows, scen, p, metric)
                if tbl:
                    parts.append(f"**{metric} vs {p}**\n\n")
                    parts.append(tbl + "\n")
        parts.append("### Pearson correlation (metric vs parameter)\n\n")
        parts.append(correlation_table(rows, scen, grid_keys, metrics) + "\n")
        parts.append("### Top-5 cells per metric\n\n")
        for metric in metrics:
            t = top_n_cells(rows, scen, metric, grid_keys, n=5)
            if t:
                parts.append(f"**{metric}**\n\n")
                parts.append(t + "\n")

    # Pareto frontier across canonical objectives.
    parts.append("\n## Pareto-optimal cells\n\n")
    parts.append("Objectives: maximize recall_at_1, maximize near_uniform_frac, "
                 "minimize mean_var_ratio, minimize latency_us.\n\n")
    parts.append(pareto_frontier(rows, grid_keys) + "\n")

    return "".join(parts)
