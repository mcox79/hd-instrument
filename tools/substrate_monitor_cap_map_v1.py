"""monitor-cap-map v1: Stage 1 of RECURSIVE self-improvement loop.

Per research_to_testbed_exp_dev_RECURSIVE_SELF_IMPROVEMENT_LOOP_Stage_3_6_*.md
(R3.1 Stage 1: ISSUE DETECTION). Reads scorecard.json + history; identifies axes
that DROPPED beyond threshold relative to baseline; emits ranked issue list for
downstream stages (find-relevant-knowledge -> compose-fix -> validation).

Usage:
  python tools/substrate_monitor_cap_map_v1.py [--threshold-drop 0.005] [--lookback 3]

Outputs:
  - stdout summary of detected issues
  - data/substrate_index/bench_reports/monitor_cap_map_issues.json

Composes with substrate_find_relevant_knowledge_v1.py + substrate_compose_fix_v1.py
to close the Stage 1+2+3 loop end-to-end:
  1. monitor-cap-map detects A-axis dropped 0.78 -> 0.6625 (-0.118 > 0.005 threshold)
  2. find-relevant-knowledge "A-axis factual retrieval" returns top atoms
  3. compose-fix uses those atoms + issue spec -> fix-spec JSON
  4. (canonical-remote) verify-fix-spec runs validation cell
  5. (canonical-remote) integrate-verified-fix ships via Phase 6
  6. monitor-cap-map regression-baseline-check confirms macro delta on next cycle

NO LLM. NO bge. Pure stdlib. Runs in milliseconds.
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


SCORECARD_PATH = Path("data/substrate_index/bench_reports/scorecard.json")
ISSUES_PATH = Path("data/substrate_index/bench_reports/monitor_cap_map_issues.json")


def detect_issues(scorecard: dict, threshold_drop: float, lookback: int) -> dict:
    """For each axis, compute current vs lookback-window baseline; flag drops."""
    history = scorecard.get("history", [])
    axes = scorecard.get("axes", [])
    if len(history) < 2:
        return {
            "scorecard_state": "insufficient_history",
            "history_rows": len(history),
            "issues": [],
            "warning": "fewer than 2 history rows; cannot detect issues",
        }

    # Sort history chronologically (already done in scorecard but defensive)
    history = sorted(history, key=lambda h: (h.get("cycle_id", 0), h.get("timestamp_iso", "")))
    current = history[-1]
    baseline_window = history[-(lookback + 1):-1] if len(history) > 1 else history[:1]

    issues = []
    # Macro F1 issue. Use BEST-of-lookback as baseline to surface "lost ground vs peak".
    macro_current = current.get("macro_f1")
    macro_baseline_vals = [h.get("macro_f1") for h in baseline_window if h.get("macro_f1") is not None]
    if macro_current is not None and macro_baseline_vals:
        macro_best = max(macro_baseline_vals)
        macro_delta = macro_current - macro_best
        if macro_delta < -threshold_drop:
            best_cycle = next((h for h in baseline_window if h.get("macro_f1") == macro_best), {})
            issues.append({
                "scope": "macro",
                "current_score": macro_current,
                "baseline_best": round(macro_best, 4),
                "baseline_best_phase": best_cycle.get("cycle_phase"),
                "delta": round(macro_delta, 4),
                "severity": round(-macro_delta / max(threshold_drop, 1e-6), 2),
                "interpretation": (
                    f"macro F1 lost {-macro_delta:.4f} vs lookback-best ({macro_best:.4f} at "
                    f"{best_cycle.get('cycle_phase', '?')}); likely cause: corpus growth without "
                    f"retention mitigation OR Q-tuning erosion"
                ),
            })

    # Per-axis issues; same best-of-lookback semantics.
    for axis in axes:
        cur = (current.get("per_axis_f1") or {}).get(axis)
        bl_vals = [(h.get("per_axis_f1") or {}).get(axis) for h in baseline_window]
        bl_vals = [v for v in bl_vals if v is not None]
        if cur is None or not bl_vals:
            continue
        best = max(bl_vals)
        delta = cur - best
        if delta < -threshold_drop:
            best_cycle = next(
                (h for h in baseline_window
                 if (h.get("per_axis_f1") or {}).get(axis) == best),
                {},
            )
            issues.append({
                "scope": "axis",
                "axis": axis,
                "axis_description": scorecard.get("axis_descriptions", {}).get(axis, ""),
                "current_score": cur,
                "baseline_best": round(best, 4),
                "baseline_best_phase": best_cycle.get("cycle_phase"),
                "delta": round(delta, 4),
                "severity": round(-delta / max(threshold_drop, 1e-6), 2),
                "interpretation": (
                    f"axis {axis} lost {-delta:.4f} vs lookback-best ({best:.4f} at "
                    f"{best_cycle.get('cycle_phase', '?')}); candidate compose-fix topic: "
                    f"{scorecard.get('axis_descriptions', {}).get(axis, axis)}"
                ),
            })

    issues.sort(key=lambda i: -i["severity"])

    return {
        "scorecard_state": "current",
        "current_cycle_id": current.get("cycle_id"),
        "current_cycle_phase": current.get("cycle_phase"),
        "baseline_lookback": lookback,
        "threshold_drop": threshold_drop,
        "history_rows": len(history),
        "macro_current": macro_current,
        "issue_count": len(issues),
        "issues": issues,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--scorecard-path", default=str(SCORECARD_PATH))
    ap.add_argument("--threshold-drop", type=float, default=0.005,
                    help="Minimum delta (negative) to flag as issue")
    ap.add_argument("--lookback", type=int, default=3,
                    help="Number of prior cycles to average for baseline")
    ap.add_argument("--json-output", type=str, default=str(ISSUES_PATH))
    args = ap.parse_args()

    sp = Path(args.scorecard_path)
    if not sp.exists():
        print(f"ERROR: scorecard not found at {sp}")
        print(f"Run: python tools/substrate_scorecard_schema_v1.py --populate-cycle-51")
        sys.exit(2)

    scorecard = json.loads(sp.read_text(encoding="utf-8"))
    result = detect_issues(scorecard, args.threshold_drop, args.lookback)

    print(f"=== monitor-cap-map v1 ===")
    print(f"scorecard_state: {result['scorecard_state']}")
    print(f"current_cycle: {result.get('current_cycle_id')} phase={result.get('current_cycle_phase')}")
    print(f"history_rows: {result['history_rows']}")
    print(f"baseline_lookback: {result.get('baseline_lookback')}; threshold_drop: {result.get('threshold_drop')}")
    print(f"macro_current: {result.get('macro_current')}")
    print(f"\nissues detected: {result.get('issue_count', 0)}")
    for i, issue in enumerate(result.get("issues", []), 1):
        scope = issue["scope"]
        if scope == "macro":
            print(f"  {i}. MACRO drop: {issue['current_score']:.4f} vs best {issue['baseline_best']:.4f} "
                  f"({issue.get('baseline_best_phase', '?')}); delta {issue['delta']:.4f}; severity {issue['severity']}")
            print(f"     -> {issue['interpretation']}")
        else:
            print(f"  {i}. AXIS {issue['axis']} drop: {issue['current_score']:.4f} vs best {issue['baseline_best']:.4f} "
                  f"({issue.get('baseline_best_phase', '?')}); delta {issue['delta']:.4f}; severity {issue['severity']}")
            print(f"     -> {issue['interpretation']}")

    op = Path(args.json_output)
    op.parent.mkdir(parents=True, exist_ok=True)
    with op.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nfull JSON: {op}")
    print(f"\nNext: pipe issues into find-relevant-knowledge per issue topic; then compose-fix.")


if __name__ == "__main__":
    main()
