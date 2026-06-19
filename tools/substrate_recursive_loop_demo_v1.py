"""RECURSIVE self-improvement loop end-to-end demo v1.

Chains all 3 shipped recursive-loop stages into one demonstration run:
  Stage 1 ISSUE DETECTION:        monitor-cap-map reads scorecard.json -> issues
  Stage 2 ISSUE RESOLUTION:       find-relevant-knowledge polls substrate per issue
  Stage 3 HYPOTHESIS FORMULATION: compose-fix builds fix-spec per top candidate

Stages 4-6 are spec'd by Research but require canonical-remote integration
(validation cell + Phase 6 integrate + regression-baseline-check). This demo
covers the locally-runnable arc.

Usage:
  python tools/substrate_recursive_loop_demo_v1.py
      [--scorecard-path data/substrate_index/bench_reports/scorecard.json]
      [--max-issues 3] [--max-candidates 8] [--max-fix-specs 3]

Output (stdout + JSON):
  data/substrate_index/bench_reports/recursive_loop_demo.json

NO LLM. NO bge. Composes 3 prior tools in-process. Heat-safe.
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--scorecard-path", default="data/substrate_index/bench_reports/scorecard.json")
    ap.add_argument("--threshold-drop", type=float, default=0.005)
    ap.add_argument("--lookback", type=int, default=3)
    ap.add_argument("--max-issues", type=int, default=3)
    ap.add_argument("--max-candidates", type=int, default=8)
    ap.add_argument("--max-fix-specs", type=int, default=3)
    ap.add_argument("--max-depth", type=int, default=2)
    ap.add_argument("--output", default="data/substrate_index/bench_reports/recursive_loop_demo.json")
    args = ap.parse_args()

    # Stage 1: import + run monitor-cap-map detection logic
    from substrate_monitor_cap_map_v1 import detect_issues
    sp = Path(args.scorecard_path)
    if not sp.exists():
        print(f"ERROR: scorecard not found at {sp}")
        print(f"Run: python tools/substrate_scorecard_schema_v1.py --populate-cycle-51")
        sys.exit(2)
    scorecard = json.loads(sp.read_text(encoding="utf-8"))

    print(f"=== Recursive Loop Demo ===")
    print(f"Stage 1: monitor-cap-map (ISSUE DETECTION)")
    stage1 = detect_issues(scorecard, args.threshold_drop, args.lookback)
    print(f"  scorecard rows: {stage1['history_rows']}")
    print(f"  issues: {stage1['issue_count']}")

    issues_top = stage1.get("issues", [])[: args.max_issues]
    for i, issue in enumerate(issues_top, 1):
        scope = issue["scope"]
        if scope == "macro":
            print(f"    {i}. MACRO drop {issue['delta']:.4f} severity {issue['severity']}")
        else:
            print(f"    {i}. {issue['axis']} drop {issue['delta']:.4f} severity {issue['severity']}: {issue['axis_description']}")

    # Stage 2 + 3 per issue
    from substrate_find_relevant_knowledge_v1 import (
        tokenize, score_atom, walk_reachable, is_history,
    )
    from substrate_compose_fix_v1 import detect_gaps, estimate_impact, identify_risk_axes

    ps = PartitionedStore(Path("data/substrate_index"))
    all_atoms = [a for a in ps.all_atoms() if not is_history(a.qualified_id)]
    qid_to_atom = {a.qualified_id: a for a in all_atoms}

    full_report = {
        "scorecard_path": str(sp),
        "stage_1_issues": stage1,
        "per_issue_resolutions": [],
    }

    for issue_idx, issue in enumerate(issues_top, 1):
        scope = issue["scope"]
        if scope == "macro":
            topic = "macro F1 substrate self-knowledge retention"
            axis_label = None
        else:
            axis_label = issue["axis"]
            topic = issue.get("axis_description") or f"axis {axis_label}"

        print(f"\n--- Issue {issue_idx}: {topic[:70]}")
        print(f"  Stage 2: find-relevant-knowledge")
        query_tokens = tokenize(topic)
        direct_hits = []
        for atom in all_atoms:
            sc = score_atom(atom, query_tokens)
            if sc["relevance"] >= 0.10:
                direct_hits.append((atom, sc))
        direct_hits.sort(key=lambda t: -t[1]["relevance"])

        seed_qids = {a.qualified_id for a, _ in direct_hits[: args.max_candidates]}
        reachable = walk_reachable(ps, seed_qids, args.max_depth) if seed_qids else set()
        reachable = {q for q in reachable if not is_history(q)}

        candidates = list(direct_hits[: args.max_candidates])
        walk_only = reachable - {a.qualified_id for a, _ in candidates}
        for q in list(walk_only)[: max(0, args.max_candidates - len(candidates))]:
            a = qid_to_atom.get(q)
            if a is None:
                continue
            sc = score_atom(a, query_tokens)
            sc["walk_only_bonus"] = 0.1
            sc["relevance"] += 0.1
            candidates.append((a, sc))
        print(f"    {len(candidates)} candidates polled")

        # Stage 3: compose-fix
        print(f"  Stage 3: compose-fix")
        issue_spec = {
            "topic": topic,
            "axis": axis_label,
            "capability": None,
        }
        fix_specs = []
        for atom, sc in candidates:
            gap_result = detect_gaps(atom, issue_spec, ps)
            if not any(v for v in gap_result["gaps"].values()):
                continue
            impact = estimate_impact(gap_result["proposals"], issue_spec)
            risks = identify_risk_axes(atom, issue_spec)
            fix_specs.append({
                "candidate_atom": atom.qualified_id,
                "candidate_name": atom.name,
                "candidate_relevance": round(sc["relevance"], 3),
                "candidate_tier": atom.tier.value,
                "detected_gaps": gap_result["gaps"],
                "proposed_structural_changes": gap_result["proposals"],
                "estimated_macro_impact": impact,
                "regression_risk_axes": risks,
            })
        fix_specs.sort(key=lambda f: (f["estimated_macro_impact"], -len(f["regression_risk_axes"])), reverse=True)
        top_fix = fix_specs[: args.max_fix_specs]
        print(f"    {len(fix_specs)} fix-specs generated; top {len(top_fix)} ranked")
        for i, f in enumerate(top_fix, 1):
            print(f"      {i}. {f['candidate_atom']} impact={f['estimated_macro_impact']:.4f} risks={len(f['regression_risk_axes'])}")

        full_report["per_issue_resolutions"].append({
            "issue": issue,
            "topic": topic,
            "candidates_count": len(candidates),
            "fix_specs_count": len(fix_specs),
            "top_fix_specs": top_fix,
        })

    # Write full report
    op = Path(args.output)
    op.parent.mkdir(parents=True, exist_ok=True)
    with op.open("w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2, default=str)
    print(f"\n=== Recursive Loop Demo COMPLETE ===")
    print(f"  stage 1 issues:      {stage1['issue_count']}")
    print(f"  per-issue arc:        ran for top {len(issues_top)}")
    print(f"  full report:          {op}")
    print(f"  Stages 4-6 (canonical-remote): validate -> integrate -> regression-check")


if __name__ == "__main__":
    main()
