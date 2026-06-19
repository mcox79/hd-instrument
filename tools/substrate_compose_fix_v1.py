"""compose-fix v1: Stage 3 of RECURSIVE self-improvement loop.

Per research_to_testbed_exp_dev_RECURSIVE_SELF_IMPROVEMENT_LOOP_Stage_1_2_*.md
R2.1 deliverable Stage 2 (named "compose-fix" in spec but architecturally Stage 3:
HYPOTHESIS FORMULATION).

Workflow:
  1. Input: an issue spec (axis + capability OR free-text topic)
  2. Call find-relevant-knowledge to get top-K candidate atoms (Stage 2 output)
  3. For each candidate, detect "structural gaps" via graph metrics:
       - Missing serves_capability link to issue.capability
       - Missing DEPENDS_ON edge that would compose with existing structure
       - SHARES_MATH neighbors that broaden coverage (if SHARES_MATH edges exist)
  4. Emit fix-spec per candidate: structural_changes (atoms_to_add + edges_to_add +
     tier_promotions) + estimated_macro_impact (heuristic) + regression_risk_axes
  5. Rank fix-specs by impact / risk; return top-K

Composes with substrate_find_relevant_knowledge_v1.py via in-process import.

DEGRADED MODE: substrate_query.py prove subcommand is canonical-remote-only;
without it, "would this close a proof gap" is unprovable. v1 uses graph-walk +
edge-presence checks as PROXIES for proof closure. When prove() ships locally,
upgrade is one substitution (~30 LOC).

Output: data/substrate_index/bench_reports/compose_fix_<issue_label>.json

NO LLM. NO bge. NO torch. Pure graph metrics; runs in seconds.

Usage:
  python tools/substrate_compose_fix_v1.py \\
      --topic "cosine cleanup similarity" \\
      --axis C \\
      --capability CAP_cleanup \\
      --max-fix-specs 5
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


HISTORY_PREFIXES = (
    "decision_history::", "findings_history::", "research_history::",
    "exp_dev_history::", "testbed_history::", "session_history::",
)


def is_history(qid: str) -> bool:
    return any(qid.startswith(p) for p in HISTORY_PREFIXES)


def detect_gaps(candidate_atom, issue: dict, ps: PartitionedStore) -> dict:
    """For a candidate atom, detect structural gaps relative to the issue.

    Returns dict with detected gap categories + ranked-fix proposals."""
    qid = candidate_atom.qualified_id
    gaps = {
        "missing_serves_capability": [],
        "missing_depends_on_to_t1": [],
        "shares_math_underutilized": [],
        "tier_promotion_eligible": False,
    }
    proposals = {
        "atoms_to_add": [],
        "edges_to_add": [],
        "tier_promotions": [],
        "metadata_field_backfill": [],
    }

    # Gap 1: missing serves_capability for issue.capability
    issue_cap = issue.get("capability")
    if issue_cap:
        caps = set(candidate_atom.serves_capability or ())
        cap_full = issue_cap if "::" in issue_cap else f"concept::{issue_cap}"
        if cap_full not in caps:
            gaps["missing_serves_capability"].append(cap_full)
            proposals["metadata_field_backfill"].append({
                "atom": qid,
                "field": "serves_capability",
                "value_to_add": cap_full,
                "rationale": f"candidate semantically related to issue but not currently serving {cap_full}",
            })

    # Gap 2: missing DEPENDS_ON chain to T1 axioms
    # Walk outgoing DEPENDS_ON; if no path reaches a T1 atom within depth 3, flag.
    deps_out = ps.out_neighbors(qid, RelationType.DEPENDS_ON) or set()
    deps_out = {q for q in deps_out if not is_history(q)}
    reaches_t1 = False
    if deps_out:
        frontier = set(deps_out)
        for _ in range(3):
            new_frontier = set()
            for q in frontier:
                a = ps.get_atom(q)
                if a and a.tier.value == "T1":
                    reaches_t1 = True
                    break
                nxt = ps.out_neighbors(q, RelationType.DEPENDS_ON) or set()
                new_frontier.update(n for n in nxt if not is_history(n))
            if reaches_t1:
                break
            frontier = new_frontier
    if not reaches_t1 and candidate_atom.tier.value in ("T2", "T3"):
        gaps["missing_depends_on_to_t1"].append({
            "atom": qid,
            "tier": candidate_atom.tier.value,
            "explanation": "no DEPENDS_ON path to T1 axioms within depth-3; authoring lever per drill 2 recipe",
        })
        # Propose an edge target heuristically: a T1 atom in same algebra fingerprint family
        alg = candidate_atom.algebra or {}
        domain_hint = alg.get("domain") or alg.get("structure")
        if domain_hint:
            proposals["edges_to_add"].append({
                "src": qid,
                "rel_type": "DEPENDS_ON",
                "tgt": f"math::T1/<authored_T1_in_domain_{domain_hint}>",
                "rationale": f"candidate has domain={domain_hint!r} but no DEPENDS_ON to T1; author T1 axiom in this domain",
                "speculative": True,
            })

    # Gap 3: SHARES_MATH underutilized
    # If candidate has known dual_of in algebra dict but no edge authored
    alg = candidate_atom.algebra or {}
    dual_of = alg.get("dual_of") or alg.get("inverse_atom")
    if dual_of and "::" in str(dual_of):
        # Check if a SHARES_MATH or DUAL edge already exists
        try:
            existing = (ps.out_neighbors(qid, RelationType.DUAL) or set()) \
                       | (ps.out_neighbors(qid, RelationType.EQUIVALENT_UNDER) or set())
        except Exception:
            existing = set()
        if str(dual_of) not in existing:
            gaps["shares_math_underutilized"].append({
                "atom": qid,
                "dual_target": str(dual_of),
                "explanation": "candidate has dual_of metadata but no DUAL/EQUIVALENT_UNDER edge",
            })
            proposals["edges_to_add"].append({
                "src": qid,
                "rel_type": "DUAL",
                "tgt": str(dual_of),
                "rationale": "wire authored dual_of metadata as explicit DUAL edge",
                "speculative": False,
            })

    # Gap 4: tier promotion eligibility (re-using KP P1 frequency-promotion criterion)
    if candidate_atom.tier.value == "T3":
        in_deps = ps.in_neighbors(qid, RelationType.DEPENDS_ON) or set()
        in_deps = {q for q in in_deps if not is_history(q)}
        if len(in_deps) >= 3:
            # check ref-corpora diversity (use corpus partitions of in-neighbors)
            corpora = set()
            for src_q in in_deps:
                src = ps.get_atom(src_q)
                if src:
                    corpora.add(src.corpus.value)
            if len(corpora) >= 2:
                gaps["tier_promotion_eligible"] = True
                proposals["tier_promotions"].append({
                    "atom": qid,
                    "from": "T3",
                    "to": "T2",
                    "rationale": f"in_degree={len(in_deps)} across {len(corpora)} corpora; KP P1 frequency-promotion criterion satisfied",
                })

    return {"gaps": gaps, "proposals": proposals}


def estimate_impact(proposals: dict, issue: dict) -> float:
    """Heuristic macro-impact estimate per fix-spec.

    Without prove(), this is a rule-of-thumb. When prove() is wired, replace with
    actual proof-gap-closure delta."""
    score = 0.0
    score += 0.015 * len(proposals.get("metadata_field_backfill", []))
    score += 0.010 * len([e for e in proposals.get("edges_to_add", []) if not e.get("speculative")])
    score += 0.003 * len([e for e in proposals.get("edges_to_add", []) if e.get("speculative")])
    score += 0.020 * len(proposals.get("tier_promotions", []))
    score += 0.005 * len(proposals.get("atoms_to_add", []))
    return round(score, 4)


def identify_risk_axes(candidate_atom, issue: dict) -> list:
    """Identify which axes might regress if fix-spec applied."""
    risks = []
    # If candidate is T1 axiom and issue axis is A (factual), no risk
    # If candidate spans multiple capabilities, applying narrow C-axis backfill might
    # affect B-axis routing
    caps = candidate_atom.serves_capability or ()
    if len(caps) >= 5:
        risks.append({"axis": "B", "reason": f"candidate serves {len(caps)} caps; B-axis routing may shift"})
    # Tier promotion creates a T2 dup of T3 atom; both compete in serves_capability
    # which was observed to depress macro retention by 0.0285 in KP P1 actual run.
    return risks


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--topic", required=True, help="Free-text issue topic")
    ap.add_argument("--axis", default=None, help="Issue axis label (A/B/C/D/E/F/G)")
    ap.add_argument("--capability", default=None, help="Issue capability qid (e.g. concept::CAP_cleanup)")
    ap.add_argument("--max-candidates", type=int, default=15)
    ap.add_argument("--max-fix-specs", type=int, default=5)
    ap.add_argument("--max-depth", type=int, default=2)
    ap.add_argument("--json-output", type=str, default=None)
    args = ap.parse_args()

    issue = {
        "topic": args.topic,
        "axis": args.axis,
        "capability": args.capability,
    }

    print(f"=== compose-fix v1 ===")
    print(f"issue: {issue}")

    # Stage 1: poll knowledge via find-relevant-knowledge logic (in-process import)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from substrate_find_relevant_knowledge_v1 import (
        tokenize, score_atom, walk_reachable, is_history as _is_hist,
    )

    ps = PartitionedStore(Path("data/substrate_index"))
    all_atoms = [a for a in ps.all_atoms() if not is_history(a.qualified_id)]

    query_tokens = tokenize(args.topic)
    print(f"query tokens: {sorted(query_tokens)}")
    direct_hits = []
    for atom in all_atoms:
        sc = score_atom(atom, query_tokens)
        if sc["relevance"] >= 0.1:
            direct_hits.append((atom, sc))
    direct_hits.sort(key=lambda t: -t[1]["relevance"])
    print(f"direct hits: {len(direct_hits)}")

    seed_qids = {a.qualified_id for a, _ in direct_hits[: args.max_candidates]}
    reachable = walk_reachable(ps, seed_qids, args.max_depth) if seed_qids else set()
    reachable = {q for q in reachable if not is_history(q)}
    qid_to_atom = {a.qualified_id: a for a in all_atoms}

    # Combine direct + walked; cap at max_candidates
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
    print(f"compose-fix candidate set: {len(candidates)} atoms")

    # Stage 2: detect gaps + build fix-specs per candidate
    fix_specs = []
    for atom, sc in candidates:
        result = detect_gaps(atom, issue, ps)
        if not any(v for v in result["gaps"].values()):
            continue  # no actionable gap
        impact = estimate_impact(result["proposals"], issue)
        risks = identify_risk_axes(atom, issue)
        fix_specs.append({
            "candidate_atom": atom.qualified_id,
            "candidate_name": atom.name,
            "candidate_relevance": round(sc["relevance"], 3),
            "candidate_tier": atom.tier.value,
            "detected_gaps": result["gaps"],
            "proposed_structural_changes": result["proposals"],
            "estimated_macro_impact": impact,
            "regression_risk_axes": risks,
            "pre_reg_hard_pass": {
                "macro_F1_lift": ">= 0.005",
                "axis_lift_specific": "+0.01 on issue axis",
                "regression_check": "no other axis drops > -0.005",
            },
            "validation_status_v1": "graph-walk + edge-presence heuristic (prove() integration pending canonical-remote)",
        })

    fix_specs.sort(key=lambda f: (f["estimated_macro_impact"], -len(f["regression_risk_axes"])), reverse=True)
    top = fix_specs[: args.max_fix_specs]

    print(f"\n=== TOP {len(top)} FIX-SPECS for '{args.topic}' ===")
    for i, f in enumerate(top, 1):
        print(f"  {i}. {f['candidate_atom']:55s} [{f['candidate_tier']}] impact={f['estimated_macro_impact']:.4f} risks={len(f['regression_risk_axes'])}")
        for cat, items in f["proposed_structural_changes"].items():
            if items:
                print(f"     -> {cat}: {len(items)} item(s)")

    out = {
        "issue": issue,
        "candidate_count": len(candidates),
        "fix_spec_count": len(fix_specs),
        "top_k_fix_specs": top,
    }
    if args.json_output:
        Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_output, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, default=str)
        print(f"\nfull JSON: {args.json_output}")


if __name__ == "__main__":
    main()
