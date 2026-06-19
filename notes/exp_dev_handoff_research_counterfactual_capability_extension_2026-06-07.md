# exp_dev hand-off -- research: Counterfactual Capability Extension

## Filed-by
Research sub-agent, 2026-06-07

## Trigger
Research note: notes/research_drill_counterfactual_capability_extension_2026-06-07.md
Topic: Capability-extension drill -- 5 counterfactual query types enabled by hybrid bitemporal
       stack + engineering extensions (Components 10/11/12) for empirical causal estimation
       and Pearl DAG annotation.

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
Anchors A1-A2 (CPU smoke) are not pause-gated.
Anchors A3-A4 (Component 11 estimator + end-to-end) are pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only.
Exp_dev designs the anchor grid, sweep parameters, threshold formulas, and queue assignment.

---

## Anchor candidates (rank-ordered)

### Anchor A1 (HIGHEST PRIORITY -- CPU, <1 day -- Type A-E smoke confirmation)
Pointer: Research note Part 1, Cheap Decisive Test (5 steps, 50 facts)
Substrate-product reading: Confirms that Types A-E counterfactual queries work end-to-end
  using Chain 2 Drill 3 components (BiTemporalFact schema + retroactive_correction + K-hop).
  This is the ZERO-COST gate: all components already specified; smoke costs 1 engineer-day.
  HARD-PASS: Types A-E each show non-degenerate counterfactual divergence (>=60% Type A, >=80%
  Type E) on the 50-fact scenario. HARD-FAIL: K-hop returns identical results pre/post
  correction (snapshot isolation bug) or Type D identical to non-temporally-ordered K-hop.
Tier hint: CPU only; no GPU; uses existing Drill 3 infrastructure; <1 day engineering + <1 min
  run time once implemented.
Why-now: Confirms the architectural claim before any downstream engineering (Components 10/11/12)
  begins. If Type A-E fail, the research note's entire premise requires revision before spending
  8-9 weeks on the extension suite.
Task: Implement 50-fact BiTemporalFact scenario; write 5 sub-tests per research note Part 1
  Cheap Decisive Test steps (a)-(e); report divergence rates per type; flag PASS/FAIL per
  pre-registered HARD-PASS/HARD-FAIL thresholds above.

### Anchor A2 (CPU, 2 weeks -- Component 11: Empirical causal effect estimator)
Pointer: Research note Part 4, Component 11 spec (~800 lines Python)
Substrate-product reading: Adds empirical ATE (average treatment effect) estimation to the
  product surface. Core loop: sample S alternate values for attribute X; S retroactive
  corrections + S K-hops; DuckDB aggregation for ATE + 95% CI via bootstrap. This is the
  product story item for healthcare AI (causal impact of treatment) and financial AI (causal
  impact of position/policy).
Tier hint: CPU; async batch evaluator; no GPU required for S<=1000; DuckDB for stats.
Why-now: Highest ROI engineering item -- 2 weeks, clearest product value, directly
  demonstrable in sales scenarios. Depends only on Anchor A1 passing.
Task: Implement Component 11 per research note Part 4 spec: Sampler + BatchEvaluator +
  Extractor + Aggregator. Test on synthetic 3-entity clinical scenario: known ground-truth
  causal relationship X->Y; confirm ATE is significantly non-zero (>2 sigma CI excludes 0)
  for S=100. Report ATE estimate, 95% CI, wall time for S=100.

### Anchor A3 (CPU/GPU, 3-4 weeks -- Component 10: Counterfactual query compiler)
Pointer: Research note Part 4, Component 10 spec (~1,500 lines Python)
Substrate-product reading: Makes counterfactual queries accessible without Python API
  knowledge. SPARQL-like syntax with AS_OF(T) and CORRECT(entity, attribute, value, T)
  operators. Named scenarios with audit trail. This is the user-facing API layer.
Tier hint: CPU; significant engineering; depends on Anchors A1 + A2 passing and Drill 4
  Protocol E (atomic multi-write) being confirmed.
Why-now: After Component 11 works, the compiler is the customer-facing packaging. Without it,
  counterfactual queries require manual Python orchestration (acceptable for API customers,
  not for non-technical users).
Task: Implement Component 10 per research note Part 4: Parser + Planner + Executor + Auditor.
  Named scenarios must co-exist (multiple scenario_ids simultaneously). Test: compile 3
  distinct "what if?" queries to execution plans; verify plans are correct; run against Anchor
  A1 scenario; confirm audit trail records scenario_id + fact corrections.

### Anchor A4 (CPU, 3 weeks -- Component 12: DAG annotation + Pearl identification)
Pointer: Research note Part 4, Component 12 spec (~1,200 lines Python)
Substrate-product reading: Customer-supplied causal DAG stored in DuckDB. ID algorithm
  (Shpitser-Pearl 2006) checks identifiability. Hybrid evaluation: identification formula from
  DAG + numerical estimates from Component 11. Enables "Pearl-grade causal claims" in the
  product for high-compliance (regulatory, academic) customers.
Tier hint: CPU; depends on Component 11; requires correct ID algorithm implementation
  (~500 lines graph algorithm). Customer onboarding burden is high (must supply DAG).
Why-now: Lowest urgency of the three components but highest defensibility. Sequence LAST.
  Only start after Components 10+11 are proven.
Task: Implement Component 12 per research note Part 4: DAG loader (RDF) + ID algorithm (Pearl
  1995 do-calculus rules 1-3 + Shpitser-Pearl ID) + hybrid evaluator. Test: supply a 3-variable
  DAG (X -> M -> Y, X <-> Y confounded) with known identification formula; verify ID algorithm
  correctly identifies frontdoor formula; verify numerical estimate from Component 11 matches
  expected value within 10% at S=100.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_counterfactual_capability_extension_2026-06-07.md
- Bitemporal spec (Components 1-5): d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill3_2026-06-07.md
- Atomic multi-write (Protocol E): d:/AI/hd-instrument/notes/research_drill_substrate_developer_experience_5x_chain2_drill4_2026-06-07.md
- ZKL certificate (cycle 150): see cap_map row for zkl_curve_k_sweep HP verdict
- K-hop K_max bounds: data/exp_khop_k_sweep/ (cycle 137, K=20) + data/exp_lie_chain_100/ (cycle 146, K=12)
- Phase 2 Gold findings (ZKP soundness, EU AI Act Article 12): d:/AI/hd-instrument/notes/phase2_5x_chains_gold_findings_2026-06-07.md

---

## Contract

- Do NOT design experiments inline. Design and queue grid once dispatched.
- HARD-PASS and HARD-FAIL thresholds are pre-registered above. Do not adjust post-hoc.
- Anchor A1 is a GATE: if Types A-E smoke fails, flag to orchestrator before proceeding to A2.
- Components 10/11/12 sequence is fixed: 11 before 10 before 12.
- Smoke test scale before scale-up: Anchor A1 is 50 facts; A2 is S=100; do not skip to large N.

## Autonomy declaration

Exp_dev designs the anchor grid, queue assignment, and per-cell pre-registration independently.
Orchestrator is informed; Testbed is not required for these CPU anchors.
Cloud GPU dispatch requires explicit user authorization per [[feedback-cloud-only-when-absolutely-necessary]].
