#!/usr/bin/env python3
"""Director-side substrate-mine: for every capability, cross-reference
existing METHODOLOGY_RULE recommendations against current_best_solution
+ application_log to identify capabilities not using optimal approach
per known evidence.

USER directive 2026-06-18: "make sure, for all of our capabilities,
that we're mining our existing body of experiments and results to make
sure we're doing the optimal thing for performance, at least based on
existing results."
"""
import json
from pathlib import Path
from collections import defaultdict


ROOT = Path("data/substrate_index")


def load_atoms(kind):
    """Yield (corpus, atom_dict) for every atom of the given kind across the Store."""
    for atoms_file in ROOT.glob("*/atoms.jsonl"):
        corpus = atoms_file.parent.name
        with atoms_file.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if a.get("kind") == kind:
                    yield corpus, a


def main():
    caps = list(load_atoms("capability"))
    rules = list(load_atoms("methodology_rule"))
    findings = list(load_atoms("finding"))

    print(f"Loaded: {len(caps)} CAPABILITY + {len(rules)} METHODOLOGY_RULE + {len(findings)} FINDING")
    print()

    # Index methodology rules
    rule_by_id = {r["id"]: r for _, r in rules}
    rule_by_trigger = defaultdict(list)
    for _, r in rules:
        md = r.get("metadata") or {}
        trig = md.get("triggering_pattern") or ""
        if trig:
            rule_by_trigger[trig.lower()].append(r)

    # Index capability current_best_solution
    cap_summary = []
    for _, c in caps:
        cid = c["id"]
        name = c.get("name", "")
        desc = (c.get("description") or "")[:200]
        current_best = c.get("current_best_solution")
        history = c.get("solution_history") or []
        tier = c.get("tier", "")

        # Extract previous solutions (replaced_date != null)
        prev_solutions = [h.get("solution_atom_id") for h in history if h.get("replaced_date")]
        replacement_reasons = [(h.get("replacement_reason") or "")[:120] for h in history]

        cap_summary.append({
            "id": cid,
            "name": name,
            "tier": tier,
            "desc": desc,
            "current_best": current_best,
            "history_len": len(history),
            "prev_solutions": prev_solutions,
            "replacement_reasons": replacement_reasons,
        })

    # For each rule, find capabilities to which it might apply
    actions = []
    for _, r in rules:
        rid = r["id"]
        md = r.get("metadata") or {}
        trig = (md.get("triggering_pattern") or "").lower()
        from_sol = md.get("from_solution") or md.get("triggering_solution") or ""
        to_sol = md.get("recommended_replacement") or md.get("to_solution") or ""
        avg_lift = md.get("avg_lift")
        n_caps = md.get("n_capabilities") or len(md.get("source_capabilities") or [])
        source_caps = md.get("source_capabilities") or []
        confidence = md.get("confidence")
        applog = md.get("application_log") or []
        status = md.get("status", "")
        validation = md.get("validation", "")
        tier4_pending = md.get("tier_4_cell_test_pending", "")

        if not from_sol and not to_sol:
            continue

        rule_summary = {
            "rule_id": rid,
            "rule_name": r.get("name", ""),
            "from_solution": from_sol,
            "to_solution": to_sol,
            "trigger": trig,
            "avg_lift": avg_lift,
            "n_capabilities": n_caps,
            "source_capabilities": source_caps,
            "confidence": confidence,
            "application_log": applog,
            "status": status,
            "validation": validation,
            "tier4_pending": tier4_pending,
            "applies_to": [],
        }

        # Match capabilities where current_best == from_solution (rule says: try to_sol instead)
        for cs in cap_summary:
            if cs["current_best"] and from_sol and cs["current_best"] == from_sol:
                # Has this capability already moved to to_sol? Check history
                history_solutions = [cs["current_best"]] + cs["prev_solutions"]
                already_applied = to_sol in history_solutions
                rule_summary["applies_to"].append({
                    "cap_id": cs["id"],
                    "cap_name": cs["name"],
                    "current_best": cs["current_best"],
                    "to_solution": to_sol,
                    "already_applied": already_applied,
                    "tier": cs["tier"],
                })

        if rule_summary["applies_to"]:
            actions.append(rule_summary)

    # Print summary
    print("=" * 90)
    print("PART 1: METHODOLOGY_RULE -> CAPABILITY APPLICABILITY MATRIX")
    print("=" * 90)
    print()
    pending_actions = []
    for rs in actions:
        not_applied = [a for a in rs["applies_to"] if not a["already_applied"]]
        applied = [a for a in rs["applies_to"] if a["already_applied"]]
        if not_applied:
            pending_actions.append((rs, not_applied))
        print(f"RULE: {rs['rule_id']}")
        print(f"  {rs['rule_name']}")
        print(f"  from: {rs['from_solution']} -> to: {rs['to_solution']}")
        if rs["avg_lift"] is not None:
            print(f"  avg_lift: {rs['avg_lift']} (n={rs['n_capabilities']} caps; confidence={rs['confidence']})")
        if rs["status"]:
            print(f"  status: {rs['status']}")
        if rs["validation"]:
            print(f"  validation: {rs['validation']}")
        if rs["tier4_pending"]:
            print(f"  tier4_pending: {rs['tier4_pending']}")
        print(f"  source_capabilities: {rs['source_capabilities']}")
        print(f"  application_log: {len(rs['application_log'])} entries")
        if applied:
            print(f"  APPLIED already in {len(applied)} cap(s):")
            for a in applied[:5]:
                print(f"    - {a['cap_id']} ({a['cap_name'][:60]})")
        if not_applied:
            print(f"  NOT-YET-APPLIED in {len(not_applied)} cap(s) -- ACTION CANDIDATES:")
            for a in not_applied[:10]:
                print(f"    -> {a['cap_id']} ({a['cap_name'][:60]}) tier={a['tier']}")
                print(f"         current_best = {a['current_best']}")
                print(f"         rule recommends = {a['to_solution']}")
        print()

    print()
    print("=" * 90)
    print("PART 2: PENDING ACTIONS (capabilities NOT using known-best per evidence)")
    print("=" * 90)
    print()
    n_actions_total = sum(len(na) for _, na in pending_actions)
    print(f"TOTAL pending actions: {n_actions_total}")
    print()
    for rs, na in pending_actions:
        lift = rs["avg_lift"]
        n_caps = rs["n_capabilities"]
        for a in na:
            print(f"ACTION: {a['cap_id']} ({a['cap_name'][:60]})")
            print(f"  current: {a['current_best']}")
            print(f"  recommended: {rs['to_solution']}")
            print(f"  evidence: {rs['rule_id']} | avg_lift={lift} | n={n_caps}")
            print(f"  rule_status: {rs['status']} | validation: {rs['validation']}")
            if rs["tier4_pending"]:
                print(f"  GATED: tier4_pending = {rs['tier4_pending']}")
            print()

    # Also report capabilities with NO current_best (gap signal)
    print("=" * 90)
    print("PART 3: CAPABILITIES WITHOUT current_best_solution (gap signal)")
    print("=" * 90)
    print()
    no_best = [cs for cs in cap_summary if not cs["current_best"]]
    print(f"TOTAL: {len(no_best)} of {len(cap_summary)} capabilities lack current_best_solution")
    print()
    for cs in no_best[:30]:
        print(f"  {cs['id']}  ({cs['name'][:70]}) tier={cs['tier']}")

    # Also: capabilities where history is empty (no prior measurement)
    print()
    print("=" * 90)
    print("PART 4: CAPABILITIES WITH solution_history (recent evidence)")
    print("=" * 90)
    print()
    with_hist = sorted([cs for cs in cap_summary if cs["history_len"] > 0], key=lambda x: -x["history_len"])
    print(f"TOTAL: {len(with_hist)} capabilities with at least 1 solution_history entry")
    for cs in with_hist[:20]:
        print(f"  {cs['id']} -- history={cs['history_len']} -- current_best={cs['current_best']}")
        for r in (cs['replacement_reasons'] or [])[:2]:
            print(f"      reason: {r}")


if __name__ == "__main__":
    main()
