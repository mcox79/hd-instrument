"""Print per-arm numbers from a metrics.json BEFORE writing any framing.

Fix #28 automation: Skunkworks has overridden Director's chain-grade recs 5+ times in 2
sessions; root cause is writing framing from verdict_msg without grep'ing per-arm. This
tool spits the load-bearing numbers in <5s readable format. Call it BEFORE any tier
recommendation, atomization spawn, or cross-cell convergence claim.

Fix #28a extensions (2026-06-23): 3 new structural-check flags derived from substrate-LM
methodology drill L4 Tier-1 item 2:
    --check-by-construction-saturation
    --check-baseline-provenance
    --check-metric-class

Usage:
    python tools/peek_arm_metrics.py <metrics.json> [more.json ...]
    python tools/peek_arm_metrics.py <metrics.json> --check-by-construction-saturation
    python tools/peek_arm_metrics.py <metrics.json> --check-baseline-provenance
    python tools/peek_arm_metrics.py <metrics.json> --check-metric-class [--preflight-spec <yaml>]
    python tools/peek_arm_metrics.py <metrics.json> --all-checks
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def fmt_num(v):
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


# ---------------------------------------------------------------------------
# Fix #28a: structural check helpers
# ---------------------------------------------------------------------------

_BCS_MAX_THRESHOLD = 0.99    # max-arm >= this => BY-CONSTRUCTION-SATURATION
_BCS_CV_THRESHOLD = 0.005    # cv < this across all arms => BY-CONSTRUCTION-SATURATION

_CROSS_CELL_MARKERS = [
    "fair_harness",
    "chain_grade_baseline",
    "from_cell",
    "quoted_from",
    "per_",
    "external_baseline",
    "prior_cell",
    "from_run",
    "from another cell",
    "from prev",
    "prev_cell",
]

_RANK_BASED_METRIC_KEYS = {
    "top_1_accuracy", "top_5_accuracy", "top_k_accuracy",
    "recall_at_1", "recall_at_5", "recall_at_k",
    "recall_discriminator_mean", "recall_harder_mean", "recall_gentle_mean",
    "accuracy", "em", "exact_match", "hit_rate",
}

_CALIBRATION_METRIC_KEYS = {
    "bpc", "perplexity", "nll", "cross_entropy", "loss",
    "bits_per_char", "bits_per_word",
}

_RANK_BASED_MECHANISM_KEYWORDS = [
    "sparse", "hd", "hyperdimensional", "vsa", "retrieval",
    "associative", "pattern_completion", "top_k", "top_1",
    "bipolar", "ternary", "frady", "kleyko",
]


def check_by_construction_saturation(d: dict) -> list[str]:
    """
    Flag if max-arm metric >= 0.99 OR cv < 0.005 across any arm.

    Source: substrate-LM drill L4 Tier-1 item 2 (Fix #28a flag 1)
    """
    flags: list[str] = []
    detail = d.get("detail", {})
    by_arm = detail.get("by_arm_agg") or detail.get("by_arm") or {}

    if not isinstance(by_arm, dict):
        return flags

    # Collect scalar primary metric values per arm
    metric_keys_priority = [
        "recall_at_1", "accuracy", "em", "top_1_accuracy", "recall_discriminator_mean",
    ]

    arm_values: dict[str, float] = {}
    arm_cvs: dict[str, float] = {}

    for arm, vals in by_arm.items():
        if isinstance(vals, dict):
            for k in metric_keys_priority:
                if k in vals and isinstance(vals[k], (int, float)):
                    arm_values[arm] = float(vals[k])
                    break
            for k in vals:
                if (k.endswith("_cv") or k.endswith("_std")) and isinstance(vals[k], (int, float)):
                    arm_cvs[arm] = float(vals[k])
                    break
        elif isinstance(vals, (int, float)):
            arm_values[arm] = float(vals)

    if arm_values:
        max_val = max(arm_values.values())
        if max_val >= _BCS_MAX_THRESHOLD:
            max_arm = max(arm_values, key=arm_values.__getitem__)
            flags.append(
                f"[BCS-SATURATION] max arm '{max_arm}' = {max_val:.4f} >= {_BCS_MAX_THRESHOLD} "
                f"-- BY-CONSTRUCTION-SATURATION: tier capped at MEASURED_MECHANISM "
                f"regardless of vs_baseline lift"
            )

    if arm_cvs:
        low_cv_arms = {a: cv for a, cv in arm_cvs.items() if cv < _BCS_CV_THRESHOLD}
        if len(low_cv_arms) >= max(1, len(arm_cvs) // 2):
            flags.append(
                f"[BCS-SATURATION] {len(low_cv_arms)}/{len(arm_cvs)} arms have cv < {_BCS_CV_THRESHOLD} "
                f"({dict(list(low_cv_arms.items())[:3])}) "
                f"-- low variance across seeds suggests deterministic/non-discriminating metric"
            )

    return flags


def check_baseline_provenance(d: dict, metrics_path: Path | None = None) -> list[str]:
    """
    Grep for cross-cell baseline references in metrics.json.
    Warns if found without matching baseline_provenance field in preflight_spec.yaml.

    Source: substrate-LM drill L4 Tier-1 item 2 (Fix #28a flag 2)
    Lit anchor: Biderman 2024 'Lessons from Trenches' -- never quote baseline from another harness.
    """
    flags: list[str] = []
    text = json.dumps(d)

    found_markers = []
    for marker in _CROSS_CELL_MARKERS:
        if marker.lower() in text.lower():
            found_markers.append(marker)

    if not found_markers:
        return flags

    # Check if there is a preflight_spec.yaml with baseline_provenance.rerun_in_this_cell=true
    preflight_ok = False
    if metrics_path is not None:
        spec_path = metrics_path.parent / "preflight_spec.yaml"
        if spec_path.exists():
            try:
                spec_text = spec_path.read_text(encoding="utf-8")
                if "rerun_in_this_cell: true" in spec_text:
                    preflight_ok = True
            except Exception:
                pass

    if not preflight_ok:
        flags.append(
            f"[BASELINE-PROVENANCE] cross-cell markers found in metrics.json: {found_markers}. "
            f"This may indicate a cross-cell baseline quote without COMPARABILITY clause. "
            f"Verify: baseline_provenance.rerun_in_this_cell=true in preflight_spec.yaml "
            f"(Biderman 2024: never quote baseline numbers from another harness/cell). "
            + ("No preflight_spec.yaml found." if metrics_path and not (metrics_path.parent / "preflight_spec.yaml").exists()
               else "preflight_spec.yaml present but rerun_in_this_cell not confirmed true.")
        )

    return flags


def check_metric_class(d: dict, metrics_path: Path | None = None) -> list[str]:
    """
    Warn on metric/mechanism mismatch (e.g. calibration_based metric on rank-based LM cell).
    Reads preflight_spec.yaml if it exists.

    Source: substrate-LM drill L4 Tier-1 item 2 (Fix #28a flag 3)
    Lit anchor: REFORMS item 4.3 -- justify the evaluation metric for the scientific claim.
    Root cause of rigged-harness failure: BPC (calibration_based) on sparse top-1 mechanism.
    """
    flags: list[str] = []
    detail = d.get("detail", {})

    # Infer metric class from what's present in the metrics
    has_rank_metric = any(k in detail for k in _RANK_BASED_METRIC_KEYS)
    has_calib_metric = any(k in detail for k in _CALIBRATION_METRIC_KEYS)

    # Also check by_arm
    by_arm = detail.get("by_arm_agg") or detail.get("by_arm") or {}
    if isinstance(by_arm, dict):
        for arm_vals in by_arm.values():
            if isinstance(arm_vals, dict):
                has_rank_metric = has_rank_metric or any(k in arm_vals for k in _RANK_BASED_METRIC_KEYS)
                has_calib_metric = has_calib_metric or any(k in arm_vals for k in _CALIBRATION_METRIC_KEYS)

    # Check verdict_msg for mechanism keywords
    verdict_msg = ""
    for key in ("verdict_msg", "verdict"):
        if key in d and isinstance(d[key], str):
            verdict_msg = d[key]
            break
        if key in detail and isinstance(detail[key], str):
            verdict_msg = detail[key]
            break

    anchor_name = str(d.get("anchor_name", d.get("anchor", "")))
    all_text = (verdict_msg + " " + anchor_name).lower()
    has_rank_mechanism = any(kw in all_text for kw in _RANK_BASED_MECHANISM_KEYWORDS)

    # Core check: calibration metric on rank-based mechanism (the rigged-harness failure mode)
    if has_calib_metric and not has_rank_metric and has_rank_mechanism:
        flags.append(
            "[METRIC-CLASS-MISMATCH] WARN: calibration-based metric (bpc/perplexity/nll) "
            "detected in metrics but anchor/verdict references rank-based mechanism keywords "
            f"({[kw for kw in _RANK_BASED_MECHANISM_KEYWORDS if kw in all_text][:3]}). "
            "Calibration metrics CANNOT fail-gate a sparse top-1/retrieval mechanism. "
            "This is the 'rigged harness' failure pattern (BPC-as-LM-gate on VSA substrate). "
            "Use rank_based metric (recall@1/top-K) as primary, report BPC as secondary only. "
            "(Pineau 2021 sec 5.6; REFORMS item 4.3)"
        )

    # Check preflight_spec.yaml if present
    if metrics_path is not None:
        spec_path = metrics_path.parent / "preflight_spec.yaml"
        if spec_path.exists():
            try:
                spec_text = spec_path.read_text(encoding="utf-8")
                # Check for declared metric_class vs what is actually in metrics
                if "metric_class: calibration_based" in spec_text and has_rank_mechanism:
                    flags.append(
                        "[METRIC-CLASS-PREFLIGHT-MISMATCH] WARN: preflight_spec.yaml declares "
                        "metric_class=calibration_based but metrics reference rank-based mechanism. "
                        "Review preflight_spec.yaml metric_scope section."
                    )
                elif "metric_class: rank_based" in spec_text and has_calib_metric and not has_rank_metric:
                    flags.append(
                        "[METRIC-CLASS-PREFLIGHT-MISMATCH] WARN: preflight_spec.yaml declares "
                        "metric_class=rank_based but metrics only contain calibration-based fields. "
                        "Check that the cell actually computes rank-based (top-K/recall) metrics."
                    )
            except Exception:
                pass

    return flags


# ---------------------------------------------------------------------------
# Original peek_one (extended with Fix #28a flags)
# ---------------------------------------------------------------------------

def peek_one(path: Path, extra_checks: dict[str, bool] | None = None) -> None:
    if not path.exists():
        print(f"[NOT FOUND] {path}")
        return
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[PARSE ERROR] {path}: {e}")
        return

    name = d.get("anchor_name") or d.get("anchor") or path.parent.name
    verdict = d.get("verdict", "?")
    run_mode = d.get("run_mode", "?")
    n_seeds = d.get("n_seeds", "?")
    elapsed = d.get("elapsed_s", "?")

    print(f"\n=== {name} ===")
    print(f"  verdict={verdict}  run_mode={run_mode}  n_seeds={n_seeds}  elapsed_s={elapsed}")

    detail = d.get("detail", {})
    by_arm = detail.get("by_arm_agg") or detail.get("mean_accuracy") or detail.get(
        "mean_recall_at_1"
    )

    if isinstance(by_arm, dict):
        if by_arm and isinstance(next(iter(by_arm.values())), dict):
            # nested per-arm structure
            print("  per-arm:")
            keys_of_interest = [
                "recall_discriminator_mean",
                "recall_harder_mean",
                "recall_at_1",
                "accuracy",
                "em",
                "gram_ratio",
                "factual_ratio",
                "bpc",
                "recall_gentle_mean",
            ]
            for arm, vals in by_arm.items():
                kvs = []
                for k in keys_of_interest:
                    if k in vals:
                        kvs.append(f"{k}={fmt_num(vals[k])}")
                if not kvs:
                    kvs = [
                        f"{k}={fmt_num(v)}"
                        for k, v in vals.items()
                        if isinstance(v, (int, float))
                    ][:3]
                cv = vals.get("recall_discriminator_cv") or vals.get("recall_harder_cv")
                if cv is not None:
                    kvs.append(f"cv={fmt_num(cv)}")
                print(f"    {arm:42s} {' | '.join(kvs)}")
        else:
            # flat arm -> scalar
            print("  per-arm:")
            for arm, v in by_arm.items():
                print(f"    {arm:42s} {fmt_num(v)}")

    # surface key Director-claim fields
    surface_fields = [
        "best_substrate_arm",
        "best_substrate_recall_at_1",
        "best_omp_arm",
        "best_omp_lift_over_argmax",
        "best_alpha",
        "best_alpha_em",
        "composed_lift_vs_harness",
        "gram_lift_templated_vs_raw",
        "fact_delta_templated_vs_raw",
        "majority_multiplier",
        "random_multiplier",
        "sanity_omp_k1_vs_argmax_sigma0_ok",
        "sanity_sigma0_ok",
    ]
    surfaced = {k: detail.get(k) for k in surface_fields if k in detail}
    if surfaced:
        print("  key fields:")
        for k, v in surfaced.items():
            print(f"    {k} = {fmt_num(v)}")

    # honest_scope is often where the cell-author flags by-construction-saturation risk
    honest = detail.get("honest_scope")
    if honest:
        print(f"  honest_scope: {honest[:250]}{'...' if len(honest) > 250 else ''}")

    # baselines vs substrate ratio sanity
    if "substrate_acc" in detail and "random_acc" in detail and "majority_acc" in detail:
        sa = detail["substrate_acc"]
        ra = detail["random_acc"]
        ma = detail["majority_acc"]
        print(
            f"  3-arm discriminator: substrate={sa:.3f} random={ra:.3f}"
            f" majority={ma:.3f} | rand_mult={sa/max(ra,1e-9):.2f}x"
            f" maj_mult={sa/max(ma,1e-9):.2f}x"
        )

    # by-construction-saturation flag (existing heuristic)
    if isinstance(by_arm, dict) and by_arm:
        values = []
        std_or_cv_values = []
        for v in by_arm.values():
            if isinstance(v, dict):
                for k in ("recall_at_1", "accuracy", "em", "factual_ratio"):
                    if k in v:
                        values.append(v[k])
                        break
                for sk in v.keys():
                    if sk.endswith("_std") or sk.endswith("_cv"):
                        if isinstance(v[sk], (int, float)):
                            std_or_cv_values.append(v[sk])
            elif isinstance(v, (int, float)):
                values.append(v)
        if len(values) >= 3:
            spread = max(values) - min(values)
            if spread < 0.01 and max(values) > 0.95:
                print(
                    f"  [WARN] BY-CONSTRUCTION-SATURATION: all arms at ceiling"
                    f" (max-min={spread:.4f}, max={max(values):.3f})"
                )
            elif spread < 0.005:
                print(
                    f"  [WARN] FLAT-ARMS: all arms within 0.005"
                    f" -- check if discriminator is informative (max-min={spread:.4f})"
                )
        if std_or_cv_values and len(std_or_cv_values) >= 3:
            if all(abs(s) < 1e-9 for s in std_or_cv_values):
                print(
                    f"  [WARN] DETERMINISTIC_METRIC_OR_FIXED_SEEDS: all per-arm std/cv"
                    f" exactly 0.0 ({len(std_or_cv_values)} values) -- likely a grid-search"
                    f" threshold or quantized metric not a continuous noisy measurement;"
                    f" Skunkworks tiers MEASURED_MECHANISM not chain-grade for these"
                )

    # Fix #28a: run structural checks if requested
    if extra_checks:
        if extra_checks.get("by_construction_saturation"):
            bcs_flags = check_by_construction_saturation(d)
            for f in bcs_flags:
                print(f"  {f}")
            if not bcs_flags:
                print("  [BCS-SATURATION] OK: no saturation ceiling detected")

        if extra_checks.get("baseline_provenance"):
            bp_flags = check_baseline_provenance(d, metrics_path=path)
            for f in bp_flags:
                print(f"  {f}")
            if not bp_flags:
                print("  [BASELINE-PROVENANCE] OK: no cross-cell baseline markers detected")

        if extra_checks.get("metric_class"):
            mc_flags = check_metric_class(d, metrics_path=path)
            for f in mc_flags:
                print(f"  {f}")
            if not mc_flags:
                print("  [METRIC-CLASS] OK: no metric/mechanism mismatch detected")


def main():
    # Parse arguments: support both old-style (positional files only) and new-style (flags)
    # Maintain backward compat: if no flags starting with '--check' are present, use legacy mode
    args_list = sys.argv[1:]
    has_flags = any(a.startswith("--") for a in args_list)

    if not has_flags:
        # Legacy mode: just positional files
        if not args_list:
            print(__doc__)
            sys.exit(1)
        for p in args_list:
            peek_one(Path(p))
        return

    # Full argparse mode (Fix #28a)
    parser = argparse.ArgumentParser(
        description=(
            "Print per-arm metrics from metrics.json BEFORE framing. "
            "Fix #28 automation + Fix #28a structural checks."
        )
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="metrics.json",
        help="One or more metrics.json files to inspect",
    )
    parser.add_argument(
        "--check-by-construction-saturation",
        action="store_true",
        help="[Fix #28a] Flag if max-arm >= 0.99 or cv < 0.005 across any arm",
    )
    parser.add_argument(
        "--check-baseline-provenance",
        action="store_true",
        help="[Fix #28a] Grep for cross-cell baseline references; warn if found without "
             "matching baseline_provenance field in preflight_spec.yaml",
    )
    parser.add_argument(
        "--check-metric-class",
        action="store_true",
        help="[Fix #28a] Warn on metric/mechanism mismatch "
             "(e.g. calibration_based metric on rank-based mechanism cell)",
    )
    parser.add_argument(
        "--all-checks",
        action="store_true",
        help="[Fix #28a] Enable all three structural check flags",
    )
    args = parser.parse_args()

    if not args.files:
        parser.print_help()
        sys.exit(1)

    extra_checks = {
        "by_construction_saturation": (
            args.check_by_construction_saturation or args.all_checks
        ),
        "baseline_provenance": (
            args.check_baseline_provenance or args.all_checks
        ),
        "metric_class": (
            args.check_metric_class or args.all_checks
        ),
    }

    for p in args.files:
        peek_one(Path(p), extra_checks=extra_checks)


if __name__ == "__main__":
    main()
