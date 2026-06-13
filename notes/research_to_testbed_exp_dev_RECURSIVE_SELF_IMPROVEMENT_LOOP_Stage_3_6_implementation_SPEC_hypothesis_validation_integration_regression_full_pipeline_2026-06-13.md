# Research -> Testbed + Exp-Dev: RECURSIVE self-improvement loop Stage 3-6 implementation SPEC -- hypothesis-formulation + empirical-validation + integration + regression-check -- Phase 3 R3.1 deliverable

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per enforcement rule do-not-stop)
**Re:** MASTER PLAN Phase 3 R3.1 deliverable; completes 6-stage recursive self-improvement loop architecture (Stage 1+2 spec'd in R2.1; Stage 5 partially operational via CELL KP P1+P4)

## Loop architecture (6 stages) -- recap + completion

| Stage | Title | Spec status | Cell |
|---|---|---|---|
| 1 | ISSUE DETECTION | THIS SPEC stage 1 below | substrate_query.py monitor-cap-map |
| 2 | ISSUE RESOLUTION via knowledge poll | R2.1 spec'd | substrate_query.py find-relevant-knowledge |
| 3 | HYPOTHESIS FORMULATION | R2.1 partially (compose-fix); THIS SPEC stage 3 expands hypothesis-tree | substrate_query.py compose-fix-tree |
| 4 | EMPIRICAL VALIDATION | THIS SPEC stage 4 | substrate_query.py verify-fix-spec + Testbed cell ship loop |
| 5 | INTEGRATION | OPERATIONAL via CELL KP P1+P4; THIS SPEC formalizes integrate-fix-spec | substrate_query.py integrate-verified-fix |
| 6 | REGRESSION CHECK | THIS SPEC stage 6 | substrate_query.py regression-baseline-check |

## Stage 1: ISSUE DETECTION SPEC

```python
"""
substrate_query.py monitor-cap-map [--scorecard-path data/scorecard.json] [--threshold-drop 0.005]

Periodically check cap_map scorecard for degradation; identify cap_map axes / capabilities that DROPPED
beyond threshold. Returns ranked issue list for downstream stages.
"""
def cmd_monitor_cap_map(args):
    scorecard = load_scorecard(args.scorecard_path)
    history = load_scorecard_history(scorecard, lookback_cycles=5)
    
    issues = []
    for axis in scorecard.axes:
        current = axis.current_score
        baseline_avg = sum(h.score for h in history[axis.name][-5:]) / 5
        delta = current - baseline_avg
        if delta < -args.threshold_drop:
            issues.append({
                "axis": axis.name,
                "current_score": current,
                "baseline_avg": baseline_avg,
                "delta": delta,
                "severity": -delta / args.threshold_drop,
                "metric_class": axis.metric_class,
                "candidate_atoms": substrate.atoms_with_serves_capability(axis.name)[:20],
            })
    issues.sort(key=lambda i: -i["severity"])
    return {"issues": issues, "issue_count": len(issues), "scorecard_state": scorecard.summary()}
```

## Stage 3: HYPOTHESIS FORMULATION SPEC (expanded)

```python
"""
substrate_query.py compose-fix-tree <issue> [--max-hypotheses-per-issue=5] [--max-depth=5]

Build hypothesis tree for issue resolution:
- Each issue node has K candidate atoms (from find-relevant-knowledge)
- Each candidate atom expands to N fix-specs via L6-PROOF + Pi/Sigma + SHARES_MATH
- Each fix-spec is scored for expected impact + risk
- Returns ranked tree of fix-spec hypotheses
"""
def cmd_compose_fix_tree(args):
    issue = args.issue
    K = args.max_hypotheses_per_issue
    
    # Step 1: poll knowledge (reuse Stage 2)
    poll_result = substrate.find_relevant_knowledge(issue.about, top_k=K * 3)
    candidates = poll_result["top_k"]
    
    # Step 2: for each candidate atom, generate N fix-spec hypotheses
    hypothesis_tree = {"issue": issue, "root_hypotheses": []}
    for candidate in candidates:
        # Generate hypotheses via:
        # 2a: direct L6-PROOF chain
        l6_proof_paths = substrate.prove_paths_to_issue(candidate, issue, max_depth=args.max_depth)
        # 2b: Pi/Sigma dependent-type composition
        pi_sigma_hypotheses = substrate.pi_sigma_compose(candidate, issue, max_depth=args.max_depth)
        # 2c: SHARES_MATH equivalence-class expansion
        shares_math_hypotheses = substrate.shares_math_expand(candidate, issue)
        
        hypotheses = l6_proof_paths + pi_sigma_hypotheses + shares_math_hypotheses
        for hyp in hypotheses:
            hyp["scoring"] = {
                "estimated_macro_impact": estimate_macro_impact(hyp, issue),
                "regression_risk_axes": identify_risk_axes(hyp, issue),
                "authoring_cost": estimate_authoring_cost(hyp),
                "shares_math_amortization_factor": compute_amortization_factor(hyp),
            }
            hyp["priority_score"] = (
                hyp["scoring"]["estimated_macro_impact"]
                * hyp["scoring"]["shares_math_amortization_factor"]
                / (hyp["scoring"]["authoring_cost"] + len(hyp["scoring"]["regression_risk_axes"]))
            )
        
        hypothesis_tree["root_hypotheses"].append({
            "candidate_atom": candidate.canonical_name,
            "candidate_relevance": candidate.relevance,
            "hypotheses": sorted(hypotheses, key=lambda h: -h["priority_score"])[:K],
        })
    
    return hypothesis_tree
```

## Stage 4: EMPIRICAL VALIDATION SPEC

```python
"""
substrate_query.py verify-fix-spec <fix-spec-json> [--testbed-cell-template path] [--max-iterations=3]

Ship fix-spec to Testbed verification cell; collect HARD-PASS / HARD-FAIL / MIDDLE verdict.
"""
def cmd_verify_fix_spec(args):
    fix_spec = load_fix_spec(args.fix_spec_json)
    
    # Step 1: generate cell from template
    cell_path = generate_testbed_cell(fix_spec, args.testbed_cell_template)
    
    # Step 2: ship to Testbed verification queue
    verification_request = {
        "fix_spec": fix_spec,
        "cell_path": cell_path,
        "pre_reg_HARD_PASS": fix_spec["pre_reg_HARD_PASS"],
        "max_iterations": args.max_iterations,
    }
    testbed_ticket = submit_to_testbed_queue(verification_request)
    
    # Step 3: poll for verdict (with timeout)
    verdict = wait_for_verdict(testbed_ticket, timeout_hours=24)
    
    return {
        "fix_spec": fix_spec,
        "verdict": verdict,
        "cell_path": cell_path,
        "next_action": determine_next_action(verdict),  # INTEGRATE / DISCARD / REVISE
    }


def determine_next_action(verdict):
    if verdict["status"] == "HARD_PASS":
        return {"action": "INTEGRATE", "reason": "empirical validation succeeded"}
    elif verdict["status"] == "HARD_FAIL":
        return {"action": "DISCARD", "reason": "fix-spec falsified; mark as anti-hypothesis"}
    elif verdict["status"] == "MIDDLE":
        return {"action": "REVISE", "reason": "iterate fix-spec parameters; 9th-rule refinement"}
```

## Stage 5: INTEGRATION SPEC (formalize existing KP)

```python
"""
substrate_query.py integrate-verified-fix <verified-fix-spec-json>

Apply verified fix-spec to substrate via Phase-2-light + Phase-6 ingest + CELL KP promotion.
Uses existing KP operator (P1 + P4 + post-P3/P5 once SHARES_MATH + Pi/Sigma ship).
"""
def cmd_integrate_verified_fix(args):
    fix_spec = load_verified_fix_spec(args.verified_fix_spec_json)
    
    # Step 1: add new atoms via Phase-6 bulk JSONL
    atoms_to_add = fix_spec["structural_changes"]["atoms_to_add"]
    if atoms_to_add:
        substrate.phase6_bulk_ingest_atoms(atoms_to_add)
    
    # Step 2: add new edges via Phase-2-light
    edges_to_add = fix_spec["structural_changes"]["edges_to_add"]
    if edges_to_add:
        substrate.phase2_light_ingest_edges(edges_to_add)
    
    # Step 3: tier promotions via CELL KP
    tier_promotions = fix_spec["structural_changes"]["tier_promotions"]
    if tier_promotions:
        for promotion in tier_promotions:
            substrate.kp_promote_atom(promotion["atom"], promotion["from_tier"], promotion["to_tier"])
    
    # Step 4: cleanup parameter tweaks
    cleanup_tweaks = fix_spec["structural_changes"]["cleanup_param_tweaks"]
    if cleanup_tweaks:
        substrate.update_cleanup_params(cleanup_tweaks)
    
    # Step 5: commit + atomic snapshot
    snapshot_id = substrate.atomic_snapshot()
    return {
        "snapshot_id": snapshot_id,
        "atoms_added": len(atoms_to_add),
        "edges_added": len(edges_to_add),
        "tier_promotions": len(tier_promotions),
        "cleanup_tweaks": len(cleanup_tweaks),
    }
```

## Stage 6: REGRESSION CHECK SPEC

```python
"""
substrate_query.py regression-baseline-check [--snapshot-id <pre-fix-snapshot>] [--benchmark-suite cap_map]

Run benchmark scorecard pre/post fix integration; revert if regression detected.
"""
def cmd_regression_baseline_check(args):
    pre_fix_snapshot = args.snapshot_id
    
    # Step 1: run benchmark suite at current state
    current_scorecard = substrate.run_benchmark_suite(args.benchmark_suite)
    
    # Step 2: load pre-fix scorecard
    pre_fix_scorecard = substrate.load_scorecard_at_snapshot(pre_fix_snapshot)
    
    # Step 3: compute axis-wise delta
    deltas = {}
    for axis in current_scorecard.axes:
        deltas[axis.name] = current_scorecard.axes[axis.name].score - pre_fix_scorecard.axes[axis.name].score
    
    # Step 4: regression detection
    regressions = {axis: delta for axis, delta in deltas.items() if delta < -0.005}
    improvements = {axis: delta for axis, delta in deltas.items() if delta > 0.005}
    
    # Step 5: decision
    if regressions and max(-d for d in regressions.values()) > sum(improvements.values()):
        # Net regression: revert
        substrate.revert_to_snapshot(pre_fix_snapshot)
        return {
            "action": "REVERT",
            "regressions": regressions,
            "improvements": improvements,
            "reverted_to_snapshot": pre_fix_snapshot,
        }
    else:
        # Net improvement OR no significant regression: commit
        return {
            "action": "COMMIT",
            "regressions": regressions,
            "improvements": improvements,
            "net_macro_delta": sum(deltas.values()) / len(deltas),
        }
```

## End-to-end loop orchestration

```python
"""
tools/substrate_recursive_self_improvement_loop_v1.py

Orchestrates Stages 1-6 in a continuous loop until cap_map scorecard stable.
"""
def main_loop():
    iteration = 0
    while True:
        iteration += 1
        print(f"=== Iteration {iteration} ===")
        
        # Stage 1: detect issues
        issues = substrate.monitor_cap_map(threshold_drop=0.005)
        if not issues["issues"]:
            print("No issues detected; loop stable. Exiting.")
            break
        
        for issue in issues["issues"][:3]:  # top-3 issues per iteration
            print(f"\nProcessing issue: {issue['axis']} (severity {issue['severity']:.2f})")
            
            # Stage 2: poll knowledge
            poll = substrate.find_relevant_knowledge(issue["axis"], top_k=10)
            
            # Stage 3: hypothesis formulation
            tree = substrate.compose_fix_tree(issue, max_hypotheses_per_issue=5, max_depth=5)
            
            # Pick top hypothesis
            top_hyp = max(
                (h for root in tree["root_hypotheses"] for h in root["hypotheses"]),
                key=lambda h: h["priority_score"],
                default=None,
            )
            if not top_hyp:
                print(f"  No hypothesis found for {issue['axis']}; skipping.")
                continue
            
            # Stage 4: empirical validation
            verdict = substrate.verify_fix_spec(top_hyp, max_iterations=3)
            
            if verdict["next_action"]["action"] == "INTEGRATE":
                # Stage 5: integrate
                snapshot_pre = substrate.atomic_snapshot()
                integrate_result = substrate.integrate_verified_fix(verdict["fix_spec"])
                
                # Stage 6: regression check
                regression = substrate.regression_baseline_check(
                    snapshot_id=snapshot_pre,
                    benchmark_suite="cap_map",
                )
                
                if regression["action"] == "REVERT":
                    print(f"  Regression detected for {issue['axis']}; reverted.")
                else:
                    print(f"  Successfully integrated fix; net macro delta {regression['net_macro_delta']:+.4f}")
            else:
                print(f"  Verdict: {verdict['next_action']['action']} -- {verdict['next_action']['reason']}")
        
        # Optional: short delay between iterations to allow cap_map to update
        time.sleep(60)
```

## Substrate-product positioning artifact

Recursive self-improvement loop OPERATIONAL = substrate-product positioning destination:
- LLMs cannot self-improve structurally; substrate's loop does
- 6 stages composed via 8 substrate_query.py subcommands (verify + prove + find + pi + sigma + id-type + find-relevant-knowledge + compose-fix-tree + verify-fix-spec + integrate-verified-fix + regression-baseline-check + monitor-cap-map)
- Each stage HARD-PASS-able independently
- Loop terminates only at cap_map scorecard stability

## Cost estimate

| Stage | LOC | Build time |
|---|---|---|
| Stage 1 monitor-cap-map | ~120 LOC | 0.5 day |
| Stage 3 compose-fix-tree | ~200 LOC | 1 day |
| Stage 4 verify-fix-spec | ~150 LOC | 1 day |
| Stage 5 integrate-verified-fix | ~150 LOC | 0.5 day (reuses KP) |
| Stage 6 regression-baseline-check | ~150 LOC | 0.5 day |
| Orchestrator main_loop | ~100 LOC | 0.5 day |
| **TOTAL** | **~870 LOC** | **~4 days** Testbed build |

Plus Stage 2 (find-relevant-knowledge ~150 LOC; spec'd R2.1) = ~1020 LOC cumulative.

## Pre-reg HARD-PASS for full recursive loop

- All 6 stages execute end-to-end on 10 known cap_map issues
- At least 3 of 10 fix-specs INTEGRATE and PASS regression check
- Cumulative macro F1 lift >= +0.005 after 10 iterations
- Zero unintended regressions surviving regression check (Stage 6 catches all)
- LLM categorical gap: NO LLM-based system can execute Stage 1-6 with checkable verification at each stage

## Routing

- **Testbed**: implement Stage 1 + 3-6 specs (~870 LOC; ~4 days); composes with R2.1 Stage 2; ship to remote_cpu_queue
- **Exp-Dev**: standing for Stage 4 verification cell template + 10 known cap_map issues for end-to-end test
- **Research**: filing this spec; standing for ship verdicts; methodology rule entry for "loop is operational when 6 stages compose without manual orchestration"

## Cross-references

- notes/research_to_testbed_exp_dev_RECURSIVE_SELF_IMPROVEMENT_LOOP_Stage_1_2_*.md (R2.1 predecessor)
- notes/research_to_testbed_exp_dev_USER_VISION_all_knowledge_on_substrate_*.md (USER vision 6-stage loop architecture source)
- notes/research_drill_optimal_external_corpus_to_VSA_HRR_substrate_ingest_methodology_knowledge_promotion_mechanism_3x_2026-06-13.md (Stage 5 KP operator drill source)
- memory `substrate-CELL-KP-knowledge-promotion-operator-P1-P4-HARD-PASS-2-of-5-paths-multi-mechanism-validated-2026-06-13` (Stage 5 partially operational)

---

**Testbed + Exp-Dev:** RECURSIVE SELF-IMPROVEMENT LOOP Stage 3-6 implementation SPEC + Stage 1 monitor-cap-map + Stage 3 compose-fix-tree hypothesis-tree-expansion via L6-PROOF + Pi/Sigma + SHARES_MATH + Stage 4 verify-fix-spec Testbed cell ship loop + Stage 5 integrate-verified-fix reuses CELL KP + Stage 6 regression-baseline-check + revert + orchestrator main_loop ~870 LOC ~4 days build + composes with R2.1 Stage 2 ~150 LOC + ~1020 LOC cumulative + 8 substrate_query.py subcommands total + Phase 4 USER vision destination operational + USER full-auto overnight continuing.
