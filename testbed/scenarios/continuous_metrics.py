"""Continuous-metric extraction for response-surface analysis.

Each scenario emits a labeled gate-pass/fail outcome plus underlying
continuous metrics. The sweep machinery needs the continuous floats only,
keyed by a stable name. This module owns that mapping in one place so
sweep.py and response_surface.py never have to know scenario internals.

Per CLAUDE.md: ASCII only, terse.
"""

from __future__ import annotations

from typing import Any


def _safe_float(x: Any, default: float = float("nan")) -> float:
    """Coerce to float or return default. None -> default."""
    if x is None:
        return default
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def extract_point_recall(metrics: dict) -> dict[str, float]:
    return {
        "recall_at_1": _safe_float(metrics.get("recall_at_1")),
        "recall_at_5": _safe_float(metrics.get("recall_at_5")),
        "mean_native_confidence": _safe_float(metrics.get("mean_native_confidence")),
        "p50_retrieve_us": _safe_float(metrics.get("p50_retrieve_us")),
        "p95_retrieve_us": _safe_float(metrics.get("p95_retrieve_us")),
        "wall_s": _safe_float(metrics.get("wall_s")),
    }


def extract_edit_isolation(metrics: dict) -> dict[str, float]:
    return {
        "max_isolation_ratio": _safe_float(metrics.get("max_isolation_ratio")),
        "mean_isolation_ratio": _safe_float(metrics.get("mean_isolation_ratio")),
        "within_theory_frac": _safe_float(metrics.get("within_theory_frac")),
        "edit_wall_us": _safe_float(metrics.get("edit_wall_us")),
        "wall_s": _safe_float(metrics.get("wall_s")),
    }


def extract_deletion_verify(metrics: dict) -> dict[str, float]:
    return {
        "mean_var_ratio": _safe_float(metrics.get("mean_var_ratio")),
        "erase_success_rate": _safe_float(metrics.get("erase_success_rate")),
        "p50_delete_us": _safe_float(metrics.get("p50_delete_us")),
        "p95_delete_us": _safe_float(metrics.get("p95_delete_us")),
        "wall_s": _safe_float(metrics.get("wall_s")),
    }


def extract_hallu_detect(metrics: dict) -> dict[str, float]:
    """Pull top-level aggregates plus the last sub-run (worst fraction)."""
    out = {
        "max_above_thresh_frac": _safe_float(metrics.get("max_above_thresh_frac")),
        "max_mean_oos_max_conf": _safe_float(metrics.get("max_mean_oos_max_conf")),
        "wall_s": _safe_float(metrics.get("wall_s")),
    }
    sub = metrics.get("per_subrun") or []
    if sub:
        last = sub[-1]
        out["near_uniform_frac"] = _safe_float(last.get("near_uniform_frac"))
        out["mean_oos_max_conf"] = _safe_float(last.get("mean_oos_max_conf"))
        out["recall_at_1_on_OOS"] = _safe_float(last.get("recall_at_1_on_OOS"))
    else:
        out["near_uniform_frac"] = float("nan")
        out["mean_oos_max_conf"] = float("nan")
        out["recall_at_1_on_OOS"] = float("nan")
    return out


def extract_continual_4stage(metrics: dict) -> dict[str, float]:
    return {
        "ret_A_after_A": _safe_float(metrics.get("ret_A_after_A")),
        "ret_A_after_D": _safe_float(metrics.get("ret_A_after_D")),
        "ret_B_after_D": _safe_float(metrics.get("ret_B_after_D")),
        "ret_C_after_D": _safe_float(metrics.get("ret_C_after_D")),
        "ret_D_after_D": _safe_float(metrics.get("ret_D_after_D")),
        "wall_s": _safe_float(metrics.get("wall_s")),
    }


def extract_storage_latency(metrics: dict) -> dict[str, float]:
    """Pull the largest-M sub-run's continuous metrics."""
    per_M = metrics.get("per_M") or {}
    if not per_M:
        return {
            "p50_retrieve_us": float("nan"),
            "p95_retrieve_us": float("nan"),
            "p50_store_us": float("nan"),
            "disk_bytes": float("nan"),
            "wall_s": _safe_float(metrics.get("wall_s")),
        }
    largest_key = max(per_M.keys(), key=lambda k: int(per_M[k].get("M", 0)))
    largest = per_M[largest_key]
    return {
        "p50_retrieve_us": _safe_float(largest.get("p50_retrieve_us")),
        "p95_retrieve_us": _safe_float(largest.get("p95_retrieve_us")),
        "p50_store_us": _safe_float(largest.get("p50_store_us")),
        "disk_bytes": _safe_float(largest.get("disk_bytes")),
        "wall_s": _safe_float(metrics.get("wall_s")),
    }


_EXTRACTORS = {
    "point_recall": extract_point_recall,
    "edit_isolation": extract_edit_isolation,
    "deletion_verify": extract_deletion_verify,
    "hallu_detect": extract_hallu_detect,
    "continual_4stage": extract_continual_4stage,
    "storage_latency": extract_storage_latency,
}


def continuous_metrics(scenario: str, metrics: dict) -> dict[str, float]:
    """Dispatch to the per-scenario extractor; return {} on unknown name."""
    fn = _EXTRACTORS.get(scenario)
    if fn is None:
        return {}
    try:
        return fn(metrics)
    except Exception as exc:
        return {"_extract_error": 1.0, "_extract_msg_present": 1.0}


def all_known_scenarios() -> list[str]:
    return list(_EXTRACTORS.keys())
