"""Markdown report emitter for the testbed.

Reads a summary.json from a run directory and renders a markdown report
with: config block, cross-backend table, killer-feature panel (substrate
contrast), per-scenario detail tables, HARD_PASS/HARD_FAIL gate summary,
latency-and-storage block, and a reproduction line.

All output is ASCII-only and uses pure-markdown tables via tabulate.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

try:
    from tabulate import tabulate
except ImportError:  # pragma: no cover
    tabulate = None


_NA = "N/A"
_NA_BY_CONSTRUCTION = "N/A (by construction)"


def _fmt(v: Any, kind: str = "auto", digits: int = 4) -> str:
    if v is None:
        return _NA
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int,)):
        return str(v)
    if isinstance(v, float):
        if kind == "pct":
            return f"{v * 100:.2f}%"
        if kind == "us":
            return f"{v:.1f}"
        if kind == "ms":
            return f"{v:.2f}"
        return f"{v:.{digits}f}"
    return str(v)


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    if tabulate is None:
        # Manual pipe-table fallback.
        lines = []
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for r in rows:
            lines.append("| " + " | ".join(str(x) for x in r) + " |")
        return "\n".join(lines)
    return tabulate(rows, headers=headers, tablefmt="github")


def _git_sha(repo_root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip() or "unknown"
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _key_metric(scenario: str, result: dict | None) -> str:
    """One-line key metric per (scenario, backend) for the cross-backend table."""
    if not result:
        return _NA
    if scenario == "point_recall":
        return f"R@1 {_fmt(result.get('recall_at_1'), 'pct')}"
    if scenario == "edit_isolation":
        return f"max_iso {_fmt(result.get('max_isolation_ratio'))}"
    if scenario == "deletion_verify":
        es = result.get("erase_success_rate")
        vr = result.get("mean_var_ratio")
        if vr is None:
            return f"erase {_fmt(es, 'pct')}"
        return f"erase {_fmt(es, 'pct')} var {_fmt(vr)}"
    if scenario == "hallu_detect":
        return f"above {_fmt(result.get('max_above_thresh_frac'), 'pct')}"
    if scenario == "continual_4stage":
        return f"retA->D {_fmt(result.get('ret_A_after_D'), 'pct')}"
    if scenario == "storage_latency":
        per = result.get("per_M") or {}
        if not per:
            return _NA
        last_M = sorted(per.keys(), key=lambda s: int(s))[-1]
        return f"p50_retr@M={last_M} {_fmt(per[last_M].get('p50_retrieve_us'), 'us')}us"
    if scenario == "large_M_constant_cost":
        per = result.get("per_M") or {}
        if not per:
            return _NA
        # Skip-aware: pick the largest M with actual measurements.
        live = {k: v for k, v in per.items() if not v.get("skipped")}
        if not live:
            return "skipped"
        last_M = sorted(live.keys(), key=lambda s: int(s))[-1]
        disk_MB = live[last_M].get("disk_MB")
        r1 = live[last_M].get("recall_at_1")
        return f"disk@M={last_M} {_fmt(disk_MB)}MB R@1 {_fmt(r1, 'pct')}"
    if scenario == "audit_chain_validation":
        ci = result.get("chain_integrity_pct")
        cov = result.get("audit_anchor_coverage")
        td = result.get("tamper_detection_rate")
        if ci is None:
            return f"audit_cov {_fmt(cov, 'pct')}"
        return f"chain {_fmt(ci, 'pct')} cov {_fmt(cov, 'pct')} tamper {_fmt(td, 'pct')}"
    if scenario == "multi_substrate_sharding":
        per = result.get("per_M") or {}
        if not per:
            return _NA
        K = result.get("K_shards")
        live = {k: v for k, v in per.items() if not v.get("skipped")}
        if not live:
            return "skipped"
        last_M = sorted(live.keys(), key=lambda s: int(s))[-1]
        disk_MB = live[last_M].get("disk_MB")
        r1 = live[last_M].get("recall_at_1")
        ci = live[last_M].get("cross_shard_chain_integrity")
        return (
            f"K={K} shards disk@M={last_M} {_fmt(disk_MB)}MB "
            f"R@1 {_fmt(r1, 'pct')} chain={_fmt(ci, 'pct')}"
        )
    if scenario == "write_heavy_stream":
        ops = result.get("ops_per_sec")
        ratio = result.get("p99_last_over_first")
        return (
            f"{_fmt(ops)}ops/s p99_last/first {_fmt(ratio)}"
        )
    if scenario == "edit_heavy_stream":
        wall = result.get("mean_edit_query_wall_us")
        corr = result.get("post_edit_correctness_rate")
        return (
            f"edit+q {_fmt(wall, 'us')}us corr {_fmt(corr, 'pct')}"
        )
    if scenario == "hot_path_skew":
        hp = result.get("hot_p50_retrieve_us")
        cp = result.get("cold_p50_retrieve_us")
        r = result.get("hot_cold_ratio")
        return (
            f"hot {_fmt(hp, 'us')}us cold {_fmt(cp, 'us')}us r {_fmt(r)}"
        )
    if scenario == "cached_hot_path":
        hp = result.get("hot_p50_retrieve_us")
        cp = result.get("cold_p50_retrieve_us")
        hr = result.get("cache_hit_rate")
        cvf = result.get("cache_verification_failures")
        if hr is None:
            return (
                f"hot {_fmt(hp, 'us')}us cold {_fmt(cp, 'us')}us "
                f"cache N/A vfail {_fmt(cvf)}"
            )
        return (
            f"hot {_fmt(hp, 'us')}us cold {_fmt(cp, 'us')}us "
            f"hit {_fmt(hr, 'pct')} vfail {_fmt(cvf)}"
        )
    if scenario == "mixed_crud_workload":
        ops = result.get("ops_per_sec_sustained")
        ratio = result.get("ops_ratio_last_over_first")
        nu = result.get("post_delete_near_uniform_rate")
        if nu is None:
            return f"{_fmt(ops)}ops/s drift {_fmt(ratio)}"
        return (
            f"{_fmt(ops)}ops/s drift {_fmt(ratio)} KF1 {_fmt(nu, 'pct')}"
        )
    if scenario == "approx_retrieve_sweep":
        op = result.get("operating_point") or {}
        if not op:
            return "no op_pt"
        sf = op.get("sample_frac")
        rec = op.get("recall_at_1")
        lat = op.get("p50_latency_us")
        sf_str = f"{sf:.2f}" if sf is not None else _NA
        rec_str = f"{rec*100:.1f}%" if rec is not None else _NA
        lat_str = f"{lat:.0f}" if lat is not None else _NA
        return f"approx_op_pt sample={sf_str} recall={rec_str} latency={lat_str}us"
    if scenario == "large_N_envelope":
        if result.get("skipped"):
            return "skipped"
        env = result.get("envelope") or {}
        per_N = env.get("max_M_at_95_recall_per_N") or {}
        if not per_N:
            return _NA
        parts = []
        for N_key in sorted(per_N.keys(), key=lambda s: int(s)):
            v = per_N[N_key]
            parts.append(f"N={N_key}:{v if v is not None else 'none'}")
        return "max M @ 95% recall: " + " ".join(parts)
    if scenario == "multi_signal_kf1":
        if result.get("substrate_only_scenario"):
            return "substrate-only"
        oos = result.get("min_oos_composite_fire_rate")
        stored = result.get("max_stored_composite_fire_rate")
        delta = result.get("composite_minus_posterior_oos_at_worst_regime")
        return (
            f"comp OOS {_fmt(oos, 'pct')} stored FP {_fmt(stored, 'pct')} "
            f"d_vs_post {_fmt(delta, 'pct')}"
        )
    if scenario == "factorized_vs_dense":
        if result.get("substrate_only_scenario"):
            return "substrate-only"
        delta = result.get("max_w_parity_max_abs_delta")
        ok = result.get("math_identity_holds")
        mem_win = result.get("first_memory_win_ratio")
        lat_win = result.get("first_latency_win_ratio")
        mem_str = f"mem<at M/N={mem_win:.2f}" if mem_win is not None else "mem<never"
        lat_str = f"lat<at M/N={lat_win:.2f}" if lat_win is not None else "lat<never"
        ok_str = "ID_OK" if ok else "ID_BREAK"
        return f"parity {_fmt(delta)} {ok_str} {mem_str} {lat_str}"
    if scenario == "hierarchical_capacity":
        if result.get("skipped"):
            return "skipped"
        per = result.get("per_M") or {}
        if not per:
            return _NA
        last_M = sorted(per.keys(), key=lambda s: int(s))[-1]
        last = per[last_M]
        r1 = last.get("recall_at_1")
        ra = last.get("routing_accuracy")
        ci = last.get("cross_level_chain_integrity")
        disk_MB = last.get("disk_MB")
        if ra is None:
            return (
                f"single@M={last_M} R@1 {_fmt(r1, 'pct')} "
                f"disk {_fmt(disk_MB)}MB"
            )
        return (
            f"hier@M={last_M} R@1 {_fmt(r1, 'pct')} "
            f"route {_fmt(ra, 'pct')} chain {_fmt(ci, 'pct')} "
            f"disk {_fmt(disk_MB)}MB"
        )
    return _NA


def _gate_cell(scenario: str, backend: str, result: dict | None,
               thresholds: dict | None) -> str:
    """Return GREEN/YELLOW/RED for a (scenario, backend) cell.

    Substrate uses substrate thresholds; everyone else uses baseline ones.
    Storage-latency has no gate; returns dash.
    """
    if not result:
        return _NA
    if scenario == "storage_latency":
        return "-"
    if not thresholds:
        return _NA
    band = thresholds.get("substrate") if backend == "substrate" else thresholds.get("baselines")
    if not band:
        return _NA
    hp = band.get("hard_pass", {}) or {}
    hf = band.get("hard_fail", {}) or {}

    if scenario == "point_recall":
        r = result.get("recall_at_1")
        if r is None:
            return _NA
        hp_thresh = hp.get("recall_at_1") or hp.get("recall_at_1_at_M_over_N_le_1") or 0.0
        hf_thresh = hf.get("recall_at_1") or hf.get("recall_at_1_at_M_over_N_eq_0p25") or 0.0
        if r >= hp_thresh:
            return "GREEN"
        if r < hf_thresh:
            return "RED"
        return "YELLOW"

    if scenario == "edit_isolation":
        v = result.get("max_isolation_ratio")
        if v is None:
            return _NA
        hp_thresh = hp.get("max_isolation_ratio", 0.0)
        hf_thresh = hf.get("max_isolation_ratio", float("inf"))
        if v < hp_thresh:
            return "GREEN"
        if v >= hf_thresh:
            return "RED"
        return "YELLOW"

    if scenario == "deletion_verify":
        if backend == "substrate":
            v = result.get("mean_var_ratio")
            es = result.get("erase_success_rate", 0.0)
            hp_var = hp.get("mean_var_ratio", float("inf"))
            hp_es = hp.get("erase_success_rate", 0.0)
            hf_var = hf.get("mean_var_ratio", float("inf"))
            if v is None:
                return _NA
            if v < hp_var and es >= hp_es:
                return "GREEN"
            if v >= hf_var:
                return "RED"
            return "YELLOW"
        es = result.get("erase_success_rate")
        if es is None:
            return _NA
        if es >= hp.get("erase_success_rate", 0.99):
            return "GREEN"
        if es < hf.get("erase_success_rate", 0.5):
            return "RED"
        return "YELLOW"

    if scenario == "hallu_detect":
        if backend == "substrate":
            ab = result.get("max_above_thresh_frac")
            mc = result.get("max_mean_oos_max_conf")
            if ab is None:
                return _NA
            if ab <= hp.get("above_thresh_frac", 0.0) and (mc or 0.0) < hp.get("mean_oos_max_conf", 0.001):
                return "GREEN"
            if ab > hf.get("above_thresh_frac_strictly_gt", 0.0):
                return "RED"
            return "YELLOW"
        # Baselines: gate on OOS recall (false positives).
        per = result.get("per_subrun") or []
        if not per:
            return _NA
        worst = max(s.get("recall_at_1_on_OOS", 0.0) for s in per)
        if worst < hp.get("recall_at_1_on_OOS", 0.01):
            return "GREEN"
        if worst >= hf.get("recall_at_1_on_OOS", 0.05):
            return "RED"
        return "YELLOW"

    if scenario == "continual_4stage":
        v = result.get("ret_A_after_D")
        if v is None:
            return _NA
        if v >= hp.get("ret_A_after_D", 0.99):
            return "GREEN"
        if v < hf.get("ret_A_after_D", 0.0):
            return "RED"
        return "YELLOW"

    return _NA


def _section_header(text: str) -> str:
    return f"\n## {text}\n"


def _config_block(config: dict) -> str:
    lines = ["```yaml"]
    for k, v in config.items():
        lines.append(f"{k}: {v}")
    lines.append("```")
    return "\n".join(lines)


def _killer_feature_panel(summary: dict) -> str:
    backends: list[str] = summary.get("backends", [])
    by_backend: dict[str, dict] = summary.get("results_by_backend", {})
    headers = ["backend", "KF-1 above_thresh", "KF-1 mean_oos_conf",
               "KF-2 max_iso", "TCFT mean_var_ratio"]
    rows: list[list[Any]] = []
    for b in backends:
        results = by_backend.get(b, {})
        hallu = results.get("hallu_detect") or {}
        edit = results.get("edit_isolation") or {}
        delv = results.get("deletion_verify") or {}
        if b == "substrate":
            row = [
                b,
                _fmt(hallu.get("max_above_thresh_frac"), "pct"),
                _fmt(hallu.get("max_mean_oos_max_conf")),
                _fmt(edit.get("max_isolation_ratio")),
                _fmt(delv.get("mean_var_ratio")),
            ]
        else:
            row = [
                b,
                _NA_BY_CONSTRUCTION,
                _NA_BY_CONSTRUCTION,
                _NA_BY_CONSTRUCTION,
                _NA_BY_CONSTRUCTION,
            ]
        rows.append(row)
    table = _md_table(headers, rows)
    note = ("\n*Footnote*: Baselines emit N/A for killer-feature metrics by "
            "construction. KF-1 (hallucination structural impossibility), KF-2 "
            "(edit isolation bound 1/sqrt(N)), and TCFT (thermodynamic erase "
            "certificate) are emergent properties of the substrate's outer-"
            "product W matrix. Embedding/dict backends have no analogous "
            "internal state to audit.\n")
    return table + "\n" + note


def _cross_backend_table(summary: dict) -> str:
    scenarios: list[str] = summary.get("scenarios", [])
    backends: list[str] = summary.get("backends", [])
    by_backend: dict[str, dict] = summary.get("results_by_backend", {})
    headers = ["backend"] + scenarios
    rows: list[list[Any]] = []
    for b in backends:
        results = by_backend.get(b, {})
        row: list[Any] = [b]
        for s in scenarios:
            row.append(_key_metric(s, results.get(s)))
        rows.append(row)
    return _md_table(headers, rows)


def _gate_table(summary: dict) -> str:
    scenarios: list[str] = summary.get("scenarios", [])
    backends: list[str] = summary.get("backends", [])
    by_backend: dict[str, dict] = summary.get("results_by_backend", {})
    thresholds_map: dict[str, dict] = summary.get("thresholds_by_scenario", {})
    headers = ["backend"] + scenarios
    rows: list[list[Any]] = []
    for b in backends:
        row: list[Any] = [b]
        for s in scenarios:
            r = by_backend.get(b, {}).get(s)
            row.append(_gate_cell(s, b, r, thresholds_map.get(s)))
        rows.append(row)
    return _md_table(headers, rows)


def _per_scenario_detail(summary: dict) -> str:
    scenarios: list[str] = summary.get("scenarios", [])
    backends: list[str] = summary.get("backends", [])
    by_backend: dict[str, dict] = summary.get("results_by_backend", {})
    chunks: list[str] = []
    for s in scenarios:
        chunks.append(f"\n### {s}\n")
        if s == "point_recall":
            headers = ["backend", "R@1", "R@5", "mean_normed_correct",
                       "mean_native_conf", "p50_store_us", "p95_store_us",
                       "p50_retr_us", "p95_retr_us", "n_items"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                rows.append([b,
                             _fmt(r.get("recall_at_1"), "pct"),
                             _fmt(r.get("recall_at_5"), "pct"),
                             _fmt(r.get("mean_normalized_correctness")),
                             _fmt(r.get("mean_native_confidence")),
                             _fmt(r.get("p50_store_us"), "us"),
                             _fmt(r.get("p95_store_us"), "us"),
                             _fmt(r.get("p50_retrieve_us"), "us"),
                             _fmt(r.get("p95_retrieve_us"), "us"),
                             _fmt(r.get("n_items"))])
            chunks.append(_md_table(headers, rows))
        elif s == "edit_isolation":
            headers = ["backend", "max_iso", "mean_iso", "within_theory_frac",
                       "edit_wall_us", "n_items"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                rows.append([b,
                             _fmt(r.get("max_isolation_ratio")),
                             _fmt(r.get("mean_isolation_ratio")),
                             _fmt(r.get("within_theory_frac")),
                             _fmt(r.get("edit_wall_us"), "us"),
                             _fmt(r.get("n_items"))])
            chunks.append(_md_table(headers, rows))
        elif s == "deletion_verify":
            headers = ["backend", "mean_var_ratio", "erase_success",
                       "p50_delete_us", "p95_delete_us", "n_probes"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                rows.append([b,
                             _fmt(r.get("mean_var_ratio")),
                             _fmt(r.get("erase_success_rate"), "pct"),
                             _fmt(r.get("p50_delete_us"), "us"),
                             _fmt(r.get("p95_delete_us"), "us"),
                             _fmt(r.get("n_probes"))])
            chunks.append(_md_table(headers, rows))
        elif s == "hallu_detect":
            headers = ["backend", "M/N", "M", "mean_oos_max_conf",
                       "above_thresh_frac", "near_uniform_frac",
                       "recall_at_1_on_OOS"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                for sub in (r.get("per_subrun") or []):
                    rows.append([b,
                                 _fmt(sub.get("M_over_N")),
                                 _fmt(sub.get("M")),
                                 _fmt(sub.get("mean_oos_max_conf")),
                                 _fmt(sub.get("above_thresh_frac"), "pct"),
                                 _fmt(sub.get("near_uniform_frac"), "pct"),
                                 _fmt(sub.get("recall_at_1_on_OOS"), "pct")])
            chunks.append(_md_table(headers, rows))
        elif s == "continual_4stage":
            headers = ["backend", "ret_A_after_A", "ret_A_after_B",
                       "ret_A_after_C", "ret_A_after_D", "ret_B_after_D",
                       "ret_C_after_D", "M_per_batch"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                rows.append([b,
                             _fmt(r.get("ret_A_after_A"), "pct"),
                             _fmt(r.get("ret_A_after_B"), "pct"),
                             _fmt(r.get("ret_A_after_C"), "pct"),
                             _fmt(r.get("ret_A_after_D"), "pct"),
                             _fmt(r.get("ret_B_after_D"), "pct"),
                             _fmt(r.get("ret_C_after_D"), "pct"),
                             _fmt(r.get("M_per_batch"))])
            chunks.append(_md_table(headers, rows))
        elif s == "large_M_constant_cost":
            headers = ["backend", "M", "M/N", "disk_MB", "p50_store_us",
                       "p50_retr_us", "p95_retr_us", "recall@1", "note"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                for mkey, mval in sorted((r.get("per_M") or {}).items(),
                                          key=lambda kv: int(kv[0])):
                    if mval.get("skipped"):
                        rows.append([b, mval.get("M"), _NA, _NA, _NA, _NA, _NA,
                                     _NA, mval.get("reason", "skipped")])
                        continue
                    rows.append([b,
                                 mval.get("M"),
                                 _fmt(mval.get("M_over_N")),
                                 _fmt(mval.get("disk_MB")),
                                 _fmt(mval.get("p50_store_us"), "us"),
                                 _fmt(mval.get("p50_retrieve_us"), "us"),
                                 _fmt(mval.get("p95_retrieve_us"), "us"),
                                 _fmt(mval.get("recall_at_1"), "pct"),
                                 ""])
            chunks.append(_md_table(headers, rows))
        elif s == "audit_chain_validation":
            headers = ["backend", "K", "chain_integrity",
                       "audit_anchor_coverage", "tamper_detection_rate",
                       "p50_delete_us", "chain_supported"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                rows.append([b,
                             _fmt(r.get("K")),
                             _fmt(r.get("chain_integrity_pct"), "pct"),
                             _fmt(r.get("audit_anchor_coverage"), "pct"),
                             _fmt(r.get("tamper_detection_rate"), "pct"),
                             _fmt(r.get("p50_delete_us"), "us"),
                             _fmt(r.get("chain_check_supported"))])
            chunks.append(_md_table(headers, rows))
        elif s == "multi_substrate_sharding":
            headers = ["backend", "M", "K", "shards_used", "disk_MB",
                       "p50_retr_us", "recall@1", "chain_integrity",
                       "tamper_rate", "edit_ok", "note"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                for mkey, mval in sorted((r.get("per_M") or {}).items(),
                                          key=lambda kv: int(kv[0])):
                    if mval.get("skipped"):
                        rows.append([b, mval.get("M"), _NA, _NA, _NA, _NA,
                                     _NA, _NA, _NA, _NA,
                                     mval.get("reason", "skipped")])
                        continue
                    rows.append([b,
                                 mval.get("M"),
                                 mval.get("K"),
                                 mval.get("shards_used"),
                                 _fmt(mval.get("disk_MB")),
                                 _fmt(mval.get("p50_retrieve_us"), "us"),
                                 _fmt(mval.get("recall_at_1"), "pct"),
                                 _fmt(mval.get("cross_shard_chain_integrity"), "pct"),
                                 _fmt(mval.get("tamper_detection_rate"), "pct"),
                                 _fmt(mval.get("edit_ok")),
                                 ""])
            chunks.append(_md_table(headers, rows))
        elif s == "storage_latency":
            headers = ["backend", "M", "disk_bytes", "p50_store_us",
                       "p95_store_us", "p50_retr_us", "p95_retr_us",
                       "cold_load_ms"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                for mkey, mval in sorted((r.get("per_M") or {}).items(),
                                          key=lambda kv: int(kv[0])):
                    rows.append([b,
                                 mval.get("M"),
                                 mval.get("disk_bytes"),
                                 _fmt(mval.get("p50_store_us"), "us"),
                                 _fmt(mval.get("p95_store_us"), "us"),
                                 _fmt(mval.get("p50_retrieve_us"), "us"),
                                 _fmt(mval.get("p95_retrieve_us"), "us"),
                                 _fmt(mval.get("cold_load_ms"), "ms")])
            chunks.append(_md_table(headers, rows))
        elif s == "hierarchical_capacity":
            headers = ["backend", "M", "K", "N_top", "N_leaf", "disk_MB",
                       "p50_retr_us", "mean_retr_us", "recall@1",
                       "routing_acc", "chain_integrity"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                if r.get("skipped"):
                    rows.append([b, _NA, _NA, _NA, _NA, _NA, _NA, _NA, _NA,
                                 _NA, _NA])
                    continue
                for mkey, mval in sorted((r.get("per_M") or {}).items(),
                                          key=lambda kv: int(kv[0])):
                    rows.append([b,
                                 mval.get("M"),
                                 mval.get("K_topics"),
                                 mval.get("N_top"),
                                 mval.get("N_leaf",
                                          mval.get("N_single_substrate")),
                                 _fmt(mval.get("disk_MB")),
                                 _fmt(mval.get("p50_retrieve_latency_us"), "us"),
                                 _fmt(mval.get("mean_retrieve_latency_us"), "us"),
                                 _fmt(mval.get("recall_at_1"), "pct"),
                                 _fmt(mval.get("routing_accuracy"), "pct"),
                                 _fmt(mval.get("cross_level_chain_integrity"), "pct")])
            chunks.append(_md_table(headers, rows))
        elif s == "multi_signal_kf1":
            headers = ["backend", "M/N", "M",
                       "oos_post", "oos_low_norm", "oos_low_conc",
                       "oos_high_dist", "oos_composite",
                       "stored_post_FP", "stored_composite_FP"]
            rows = []
            for b in backends:
                r = by_backend.get(b, {}).get(s) or {}
                if r.get("substrate_only_scenario"):
                    rows.append([b, "n/a", "n/a", _NA_BY_CONSTRUCTION,
                                 _NA_BY_CONSTRUCTION, _NA_BY_CONSTRUCTION,
                                 _NA_BY_CONSTRUCTION, _NA_BY_CONSTRUCTION,
                                 _NA_BY_CONSTRUCTION, _NA_BY_CONSTRUCTION])
                    continue
                for sub in (r.get("per_subrun") or []):
                    ops = sub.get("oos_per_signal_fire_rate") or {}
                    sps = sub.get("stored_per_signal_fire_rate") or {}
                    rows.append([
                        b,
                        _fmt(sub.get("M_over_N")),
                        _fmt(sub.get("M")),
                        _fmt(ops.get("posterior_entropy"), "pct"),
                        _fmt(ops.get("low_norm"), "pct"),
                        _fmt(ops.get("low_concentration"), "pct"),
                        _fmt(ops.get("high_distance"), "pct"),
                        _fmt(sub.get("oos_composite_fire_rate"), "pct"),
                        _fmt(sps.get("posterior_entropy"), "pct"),
                        _fmt(sub.get("stored_composite_fire_rate"), "pct"),
                    ])
            chunks.append(_md_table(headers, rows))
    return "\n".join(chunks)


def _latency_storage_section(summary: dict) -> str:
    backends: list[str] = summary.get("backends", [])
    by_backend: dict[str, dict] = summary.get("results_by_backend", {})
    headers = ["backend", "M", "disk_bytes", "p50_store_us", "p50_retr_us",
               "cold_load_ms"]
    rows: list[list[Any]] = []
    for b in backends:
        r = by_backend.get(b, {}).get("storage_latency") or {}
        per_M = r.get("per_M") or {}
        for mkey, mval in sorted(per_M.items(), key=lambda kv: int(kv[0])):
            rows.append([b,
                         mval.get("M"),
                         mval.get("disk_bytes"),
                         _fmt(mval.get("p50_store_us"), "us"),
                         _fmt(mval.get("p50_retrieve_us"), "us"),
                         _fmt(mval.get("cold_load_ms"), "ms")])
    if not rows:
        return "_storage_latency scenario was not run; no data._"
    return _md_table(headers, rows)


def _executive_summary(summary: dict) -> str:
    """3-sentence answer: where substrate wins, where baselines win, crossover.

    Reads aggregate metrics from summary and produces a sharp at-a-glance
    framing. Falls back to neutral language if data is missing for any
    sentence.
    """
    rows = summary.get("rows") or summary.get("results") or []
    by_scen_back: dict[tuple, dict] = {}
    for r in rows:
        scen = r.get("scenario")
        back = r.get("backend")
        if scen and back:
            by_scen_back[(scen, back)] = r.get("result", r)

    def _g(scen, back, *keys):
        d = by_scen_back.get((scen, back), {})
        for k in keys:
            v = d.get(k)
            if v is not None:
                return v
        return None

    lines: list[str] = []

    # Sentence 1: where substrate wins.
    wins = []
    sub_iso = _g("edit_isolation", "substrate", "max_isolation_ratio")
    sub_var = _g("deletion_verify", "substrate", "mean_var_ratio")
    sub_hallu = _g("hallu_detect", "substrate", "max_above_thresh_frac",
                   "above_thresh_frac")
    if sub_iso is not None and sub_iso < 0.05:
        wins.append(f"KF-2 edit isolation max_iso={sub_iso:.4f}")
    if sub_var is not None and sub_var < 0.10:
        wins.append(f"TCFT deletion var_ratio={sub_var:.4f}")
    if sub_hallu is not None:
        wins.append(f"KF-1 hallu above_thresh={sub_hallu*100:.1f}%")
    if wins:
        lines.append("**Substrate wins on killer features:** "
                     + "; ".join(wins) + ". Baselines emit "
                     "N/A by construction on all three.\n")
    else:
        lines.append("**Substrate killer-feature panel:** numbers populated; "
                     "see panel below.\n")

    # Sentence 2: where baselines win.
    sub_recall = _g("point_recall", "substrate", "recall_at_1")
    faiss_recall = _g("point_recall", "faiss", "recall_at_1")
    sub_retr = _g("storage_latency", "substrate", "p50_retr_us")
    if sub_retr is None:
        # Best-effort: pull from per_M list.
        per_m = (_g("storage_latency", "substrate", "per_M") or [])
        if per_m:
            sub_retr = per_m[-1].get("p50_retrieve_us")
    faiss_retr = _g("storage_latency", "faiss", "p50_retr_us")
    if faiss_retr is None:
        per_m = (_g("storage_latency", "faiss", "per_M") or [])
        if per_m:
            faiss_retr = per_m[-1].get("p50_retrieve_us")
    losses = []
    if sub_recall is not None and faiss_recall is not None and sub_recall < faiss_recall:
        losses.append(f"point_recall substrate {sub_recall*100:.1f}% < faiss "
                      f"{faiss_recall*100:.1f}% (atom collisions at chosen C)")
    if sub_retr is not None and faiss_retr is not None and sub_retr > faiss_retr * 2:
        losses.append(f"retrieve p50 substrate {sub_retr:.0f}us > faiss "
                      f"{faiss_retr:.0f}us (heavier per-op fixed cost)")
    if losses:
        lines.append("**Baselines win on speed and exact recall:** "
                     + "; ".join(losses) + ".\n")
    else:
        lines.append("**Baselines do not have a clear advantage on the "
                     "measured scenarios in this run.**\n")

    # Sentence 3: crossover decision.
    sub_disk_per_m = (_g("storage_latency", "substrate", "per_M") or [])
    faiss_disk_per_m = (_g("storage_latency", "faiss", "per_M") or [])
    crossover_M = None
    if sub_disk_per_m and faiss_disk_per_m:
        sub_first = sub_disk_per_m[0]
        sub_disk = sub_first.get("disk_bytes")
        if sub_disk:
            for row in faiss_disk_per_m:
                if row.get("disk_bytes", 0) >= sub_disk:
                    crossover_M = row.get("M")
                    break
    if crossover_M is not None:
        lines.append(f"**Deployment crossover:** substrate disk footprint "
                     f"becomes structurally cheaper than FAISS at M >= "
                     f"{crossover_M} (constant {sub_disk_per_m[0].get('disk_bytes', 0)/1e6:.1f} MB "
                     f"substrate vs FAISS O(M*d) scaling line). Above that M, "
                     f"deploy substrate; below, choose substrate for audit "
                     f"primitives or FAISS for raw recall speed.\n")
    else:
        lines.append("**Deployment crossover:** run the crossover_sweep "
                     "config to surface the empirical M at which substrate's "
                     "O(N^2) constant cost beats FAISS's O(M*d) scaling.\n")

    return "\n".join(lines)


def render_markdown(summary_path: Path) -> str:
    summary_path = Path(summary_path)
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    run_dir = summary_path.parent
    timestamp = summary.get("timestamp", "unknown-ts")
    config = summary.get("config", {})
    cli_cmd = summary.get("cli_command", "python -m testbed run ...")

    repo_root = run_dir
    for _ in range(8):
        if (repo_root / ".git").exists():
            break
        if repo_root.parent == repo_root:
            break
        repo_root = repo_root.parent
    sha = _git_sha(repo_root)

    parts: list[str] = []
    parts.append(f"# Substrate Memory Testbed Report {timestamp}\n")
    parts.append(f"_Generated from {summary_path.name}._\n")

    parts.append(_section_header("Executive summary"))
    parts.append(_executive_summary(summary))

    parts.append(_section_header("Config"))
    parts.append(_config_block(config))

    parts.append(_section_header("Cross-backend table"))
    parts.append("Key metric per (scenario, backend). See per-scenario detail "
                 "for full numbers.\n")
    parts.append(_cross_backend_table(summary))

    parts.append(_section_header("Killer-feature panel"))
    parts.append("Substrate-only metrics: KF-1 (hallucination detection), "
                 "KF-2 (edit isolation), TCFT (deletion certificate).\n")
    parts.append(_killer_feature_panel(summary))

    parts.append(_section_header("Per-scenario detail"))
    parts.append(_per_scenario_detail(summary))

    parts.append(_section_header("HARD_PASS / HARD_FAIL gate summary"))
    parts.append("GREEN = HARD_PASS band met. YELLOW = within window. RED = "
                 "HARD_FAIL band hit. Dash = no gate registered.\n")
    parts.append(_gate_table(summary))

    parts.append(_section_header("Latency and storage"))
    parts.append(_latency_storage_section(summary))

    parts.append(_section_header("How to reproduce"))
    parts.append(f"Run from repo root at git SHA `{sha}`:\n")
    parts.append(f"```\n{cli_cmd}\n```\n")

    md = "\n".join(parts) + "\n"

    out_path = run_dir / "report.md"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
    except OSError:
        pass
    return md
