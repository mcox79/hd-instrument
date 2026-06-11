# exp_dev hand-off -- research: empowerment policy bridge (2x)

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_empowerment_policy_bridge_2x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Sprint 2 D2.5 EMPOWERMENT: emp_corr=1.000 (perfect signal) but policy lift only 6.8%.
Diagnosis: substrate computes empowerment as a state scalar E(s). This does not provide
a control gradient. The bridge requires converting E(s) to either:
  (a) Q(s,a) = E[E(s') | s, a]  -- per-action future-empowerment Q-value
  (b) p*(a|s) from the variational source distribution used to compute E(s)
  (c) finite-difference gradient del_a E(s' | s, a)

Three paths are proposed in rank order. All are CPU-tier experiments. No cloud needed.

---

## Anchor candidates (rank-ordered by P_actionable x engineering cost)

### 1. EMP-VARIATE-POLICY (HIGHEST PRIORITY -- zero new infrastructure)

Anchor pointer: EMP-VARIATE-POLICY (new; not yet queued)
Substrate-product reading: The variational empowerment estimator computes a source
  distribution p*(a | s_t) as part of computing E(s). If that distribution is saved
  rather than discarded, using it directly as the action-selection policy is a zero-cost
  bridge. This tests whether the substrate's existing variational machinery already
  contains the policy implicitly.
Tier hint: CPU laptop; ~30-60 min wall; uses existing empowerment estimator
Why-now: Zero engineering cost if p*(a|s_t) is already computed. If this passes, all
  other paths are secondary. Test FIRST.

Pre-reg bands (research recommendation):
  HARD-PASS: Policy lift >= 18% within 200 steps using p*(a|s_t) as action distribution
             (vs 6.8% scalar baseline)
  HARD-FAIL: Policy lift < 10% after 200 steps (source dist no better than scalar proxy)
  MID-BAND: Policy lift 10-18% (investigate n-step extension of source distribution)

Pre-condition: Verify whether the empowerment estimator exposes p*(a|s_t) or only E(s).
  If only E(s) is exposed, skip to EMP-Q-TABLE.

### 2. EMP-Q-TABLE (HIGH PRIORITY -- 1-2 day implementation)

Anchor pointer: EMP-Q-TABLE (new; not yet queued)
Substrate-product reading: Build Q(s,a) = running mean of E(s') for observed
  (s, a, s', E(s')) tuples. Policy = softmax(Q(s,:)) with temperature tau. Tests whether
  one-step lookahead (what empowerment does this action tend to produce?) closes the
  6.8% -> 25%+ policy lift gap.
Tier hint: CPU laptop; ~1-2 hr wall for 2K steps of Q-table collection + evaluation
Why-now: Best cost-to-P ratio after EMP-VARIATE-POLICY. No neural net training required.
  Directly implements the biological basal ganglia analogue (per-action Q-value storage).

Pre-reg bands:
  HARD-PASS: Policy lift >= 25% within 2K steps at Q-table hit rate >= 50%
  HARD-FAIL: Q-table hit rate < 20% after 1K steps (state space too large; flag for D3)
             OR policy lift < 12% at hit rate >= 50%
  MID-BAND: Policy lift 12-25% at hit rate >= 30% (increase collection steps before verdict)

Sweep: temperature tau in {0.1, 0.5, 1.0, 2.0}; report policy lift and Q-hit-rate per tau.

### 3. EMP-REINFORCE-FD (MEDIUM PRIORITY -- finite-difference policy gradient)

Anchor pointer: EMP-REINFORCE-FD (new; not yet queued)
Substrate-product reading: Sample K=16 actions per state, execute each in model, record
  E(s') for each, compute REINFORCE gradient with E(s') as return. Applies standard
  policy gradient machinery to the empowerment signal.
Tier hint: CPU laptop; ~2-4 hr wall for 1K gradient steps at K=16
Why-now: Required only if EMP-VARIATE-POLICY fails AND EMP-Q-TABLE shows hit-rate failure.
  Has higher engineering cost (K forward model rollouts per step) and higher variance.

Pre-reg bands:
  HARD-PASS: Policy lift >= 20% within 1K steps at K=16
  HARD-FAIL: Relative gradient variance > 100 at K=16 (impractical; K > 100 needed) OR
             policy lift < 10% at K=32
  MID-BAND: Policy lift 10-20% with decreasing variance trend (increase K to 32-64)

Smoke: 200 steps at K=16. Compute relative variance = var(grad) / mean(grad)^2. If > 100,
  abort and flag this path as requiring variance reduction before retest.

### 4. EMP-BONUS (LOW PRIORITY -- exploration bonus, does not solve core problem)

Anchor pointer: EMP-BONUS (new; not yet queued)
Substrate-product reading: Adds lambda * E(s) to task reward. Not a policy bridge but
  a reward shaping baseline. Run only to establish a LOWER BOUND on empowerment utility
  so D1-D3 paths have a concrete comparison point.
Tier hint: CPU laptop; ~30 min wall; sweep lambda in {0.01, 0.1, 1.0, 5.0}
Why-now: Run in parallel with or after EMP-VARIATE-POLICY to establish baseline.

Pre-reg bands:
  HARD-PASS: Some lambda achieves lift >= 20% (reward shaping sufficient -- cheaper path wins)
  HARD-FAIL: No lambda achieves lift > 10% (confirms need for structural bridge)
  MID-BAND: Best lambda achieves 10-20% (partial; structural bridge still recommended)

---

## Dispatch priority order

1. EMP-VARIATE-POLICY (gate: is p*(a|s_t) exposed by empowerment estimator?)
   - If YES: dispatch immediately, ~30-60 min smoke
   - If NO: skip, go to step 2
2. EMP-Q-TABLE (independent of step 1 if p*(a|s_t) not available; run in parallel if available)
3. EMP-BONUS (run in parallel with step 1 or 2 to establish baseline)
4. EMP-REINFORCE-FD (only if steps 1 and 2 HARD-FAIL or MID-BAND at < 15%)

All four are CPU-only. No cloud dispatch needed. Total wall time: 3-6 hours for all four
sequentially; 1.5-3 hours if steps 1, 2, 3 run in parallel.

---

## Context pointers

- Research note (full analysis with 8 rescue paths and 5 empirical tests):
  d:/AI/hd-instrument/notes/research_drill_empowerment_policy_bridge_2x_2026-06-10.md
- Sprint 2 D2.5 empowerment experiment (the MIDDLE_BAND verdict that triggered this drill):
  Look in data/exp_*/metrics.json for the empowerment sprint 2 anchor with emp_corr=1.000
- Substrate capability map (empowerment-related rows):
  d:/AI/hd-instrument/data/substrate_capability_map.md

---

## Contract section

This hand-off is research-to-experiment. The 4 anchor specs above are provided as
pre-reg recommendations. Exp_dev is responsible for:
- Checking whether p*(a|s_t) is exposed by the current empowerment estimator
- Implementing test scripts for EMP-Q-TABLE (hash map + moving average)
- Assigning to correct queue (all CPU laptop tier)
- Writing verdict notes for each test per standard protocol
- Escalating any HARD-PASS to orchestrator for cap_map update and Sprint 3 routing

## Autonomy declaration

Exp_dev may dispatch all four anchors independently without orchestrator approval (all
are CPU pre-tests, low cost, low risk). Any result showing policy lift >= 25% should be
escalated to orchestrator immediately for Sprint 3 routing decision. A result showing
all four paths HARD-FAIL (lift < 10%) should be escalated as a potential representation
problem requiring research re-drill on the empowerment state-space definition.
