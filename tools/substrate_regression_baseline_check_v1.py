"""regression-baseline-check v1: Stage 6 of RECURSIVE self-improvement loop.

Per R3.1 Stage 6 spec. After Stages 4-5 (validate-fix-spec + integrate-verified-fix)
ship a change, this stage answers: "Did the integrated fix cause net regression?"

Approach: compare the most recent cycle (post-integration) to the prior cycle
(pre-integration); compute per-axis + macro deltas; classify each as
IMPROVED / UNCHANGED / REGRESSED / TARGETED_DROP (if the fix was meant to
trade-off that axis); produce overall verdict (NET_IMPROVEMENT / NET_REGRESSION /
NEUTRAL).

Composes with substrate_scorecard_schema_v1.py + substrate_monitor_cap_map_v1.py
to close the recursive-loop architecture Stage 6 entry-to-exit.

If verdict is NET_REGRESSION, recommends revert (per Stage 6 spec: "if drop -> revert").

Usage:
  python tools/substrate_regression_baseline_check_v1.py
      [--scorecard-path data/substrate_index/bench_reports/scorecard.json]
      [--regression-threshold 0.005]
      [--targeted-axes A]

NO LLM. NO bge. Pure stdlib. Runs in milliseconds.
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path


def classify_delta(delta: float, threshold: float, is_targeted: bool) -> str:
    if abs(delta) < threshold:
        return "UNCHANGED"
    if delta > 0:
        return "IMPROVED"
    return "TARGETED_DROP" if is_targeted else "REGRESSED"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--scorecard-path", default="data/substrate_index/bench_reports/scorecard.json")
    ap.add_argument("--regression-threshold", type=float, default=0.005,
                    help="Minimum |delta| to classify as IMPROVED/REGRESSED")
    ap.add_argument("--targeted-axes", nargs="*", default=[],
                    help="Axes the fix was meant to trade-off (drops here are NOT regression)")
    ap.add_argument("--json-output", default="data/substrate_index/bench_reports/regression_baseline_check.json")
    args = ap.parse_args()

    sp = Path(args.scorecard_path)
    if not sp.exists():
        print(f"ERROR: scorecard not found at {sp}")
        sys.exit(2)
    scorecard = json.loads(sp.read_text(encoding="utf-8"))
    history = sorted(scorecard.get("history", []),
                     key=lambda h: (h.get("cycle_id", 0), h.get("timestamp_iso", "")))
    if len(history) < 2:
        print(f"ERROR: scorecard has only {len(history)} row(s); need at least 2 for delta")
        sys.exit(2)
    prior = history[-2]
    post = history[-1]

    axes = scorecard.get("axes", [])
    targeted = set(args.targeted_axes)

    print(f"=== regression-baseline-check v1 ===")
    print(f"prior cycle: cycle={prior.get('cycle_id')} phase={prior.get('cycle_phase')} macro={prior.get('macro_f1')}")
    print(f"post  cycle: cycle={post.get('cycle_id')} phase={post.get('cycle_phase')} macro={post.get('macro_f1')}")
    if targeted:
        print(f"targeted-axes (drops here NOT regression): {sorted(targeted)}")

    # Macro delta
    p_macro = prior.get("macro_f1")
    n_macro = post.get("macro_f1")
    macro_delta = None
    macro_class = None
    if p_macro is not None and n_macro is not None:
        macro_delta = n_macro - p_macro
        macro_class = classify_delta(macro_delta, args.regression_threshold, is_targeted=False)

    # Per-axis deltas
    per_axis = []
    for axis in axes:
        p = (prior.get("per_axis_f1") or {}).get(axis)
        n = (post.get("per_axis_f1") or {}).get(axis)
        if p is None or n is None:
            continue
        delta = n - p
        cls = classify_delta(delta, args.regression_threshold, is_targeted=(axis in targeted))
        per_axis.append({
            "axis": axis,
            "axis_description": scorecard.get("axis_descriptions", {}).get(axis, ""),
            "prior_score": p,
            "post_score": n,
            "delta": round(delta, 4),
            "classification": cls,
        })

    # Overall verdict
    improved_count = sum(1 for a in per_axis if a["classification"] == "IMPROVED")
    regressed_count = sum(1 for a in per_axis if a["classification"] == "REGRESSED")
    targeted_drop_count = sum(1 for a in per_axis if a["classification"] == "TARGETED_DROP")
    unchanged_count = sum(1 for a in per_axis if a["classification"] == "UNCHANGED")

    if macro_class == "IMPROVED" and regressed_count == 0:
        verdict = "NET_IMPROVEMENT"
        revert_recommended = False
    elif macro_class == "REGRESSED" and improved_count == 0:
        verdict = "NET_REGRESSION"
        revert_recommended = True
    elif macro_class == "REGRESSED" and improved_count > 0:
        verdict = "MIXED_REGRESSION"
        revert_recommended = True
    elif macro_class == "IMPROVED" and regressed_count > 0:
        verdict = "MIXED_IMPROVEMENT"
        revert_recommended = False
    else:
        verdict = "NEUTRAL"
        revert_recommended = False

    print(f"\nmacro: prior {p_macro:.4f} -> post {n_macro:.4f}; delta {macro_delta:.4f}; class {macro_class}")
    print(f"\nper-axis classifications:")
    for a in per_axis:
        marker = {"IMPROVED": "+", "REGRESSED": "-", "TARGETED_DROP": "~", "UNCHANGED": " "}.get(a["classification"], "?")
        print(f"  {marker} {a['axis']}: {a['prior_score']:.4f} -> {a['post_score']:.4f}  delta {a['delta']:+.4f}  [{a['classification']}]")

    print(f"\noverall counts: improved={improved_count}  regressed={regressed_count}  targeted_drop={targeted_drop_count}  unchanged={unchanged_count}")
    print(f"VERDICT: {verdict}")
    print(f"revert_recommended: {revert_recommended}")
    if revert_recommended:
        print(f"\n[Stage 6 per spec] If drop -> revert; root-cause analysis on regressed axes")
    else:
        print(f"\n[Stage 6 per spec] Net acceptable; integration confirmed.")

    out = {
        "scorecard_path": str(sp),
        "prior_cycle": {"cycle_id": prior.get("cycle_id"), "cycle_phase": prior.get("cycle_phase"), "macro_f1": p_macro},
        "post_cycle": {"cycle_id": post.get("cycle_id"), "cycle_phase": post.get("cycle_phase"), "macro_f1": n_macro},
        "macro_delta": round(macro_delta, 4) if macro_delta is not None else None,
        "macro_classification": macro_class,
        "regression_threshold": args.regression_threshold,
        "targeted_axes": sorted(targeted),
        "per_axis_classifications": per_axis,
        "counts": {
            "improved": improved_count, "regressed": regressed_count,
            "targeted_drop": targeted_drop_count, "unchanged": unchanged_count,
        },
        "verdict": verdict,
        "revert_recommended": revert_recommended,
    }
    op = Path(args.json_output)
    op.parent.mkdir(parents=True, exist_ok=True)
    with op.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nfull JSON: {op}")


if __name__ == "__main__":
    main()
