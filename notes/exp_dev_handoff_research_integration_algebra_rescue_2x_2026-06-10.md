# exp_dev hand-off -- research: integration algebra rescue 2x

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_integration_algebra_rescue_2x_2026-06-10.md
Sprint 2 MIDDLE_BAND context: integrated(0.019) vs equal-weight(0.022) vs best-single(0.029)

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist.
Do not ship if paused.

---

## Root cause (from 2x drill)

The algebraic mechanism is identified. Additive softmax-weighted superposition of K=5
near-orthogonal drive vectors produces a combined vector with norm 1/sqrt(K) ~ 0.447.
This vector sits in the "desert" between drive attractors -- equidistant from all K
basins. The cleanup step from this desert gives suppressed or random retrieval.
That is why integrated_minsat(0.019) < best-single_minsat(0.029).

The T1 multiplicative result (0.038 > best-single 0.032) is a SEPARATE mechanism:
multiplicative gating does not use additive superposition and bypasses the norm dilution.

L2 renormalization of the integrated vector (one normalize call) is the cheapest fix.
Multiplicative gating is the partially-validated fix. GWT broadcast avoids the problem
entirely by never creating a blended vector.

---

## Anchor Candidates (rank-ordered by P_actionable x dependency order)

### 1. INTEG-RENORM-T1 -- L2 renormalization gate (HIGHEST PRIORITY, CHEAPEST)

Anchor pointer: INTEG-RENORM-T1 (new, not yet queued)
Substrate-product reading: Tests whether adding one L2 normalize call after
  x_int = sum_k w_k * d_k resolves the norm dilution failure mode. Algebraically
  guaranteed to lift target drive's cleanup score for sharp softmax weights.
  If min_sat improves above best-single, this is the immediate Sprint 2 fix.
Tier hint: CPU laptop; < 5 min wall; modify existing Sprint 2 experiment only
Why-now: Zero engineering cost. One normalize call. If HARD-PASS, sprint blocker resolved
  in 5 minutes. Gates all other integration paths.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: integrated_minsat(renorm) > 0.029 (= best-single baseline)
  MIDDLE-BAND: integrated_minsat(renorm) in [0.022, 0.029] (renorm helps but not enough)
  HARD-FAIL: integrated_minsat(renorm) <= 0.022 (= equal-weight; renorm adds nothing)
             Implies weights are too uniform; investigate Failure Mode 2/3 next.

Implementation note: the change is minimal -- take the existing Sprint 2 experiment
code, find the line that produces x_int (the weighted sum), and add a normalize step.

### 2. INTEG-MULT-SPRINT2-T2 -- Multiplicative gating in Sprint 2 context

Anchor pointer: INTEG-MULT-SPRINT2-T2 (new, not yet queued)
Substrate-product reading: Re-runs Sprint 2 experiment with multiplicative gating
  (validated at 0.038 > best-single 0.032 in INTEG-SOFTMAX-T1) instead of additive.
  Tests whether the T1 advantage transfers to the full Sprint 2 setup.
Tier hint: CPU laptop; < 10 min wall; modify existing Sprint 2 experiment
Why-now: T1 already validated multiplicative beats best-single. Only missing: does
  this hold in Sprint 2 setup (different drive structure, same min_sat metric)?

Pre-reg bands:
  HARD-PASS: multiplicative_minsat(Sprint2) > 0.029 + 0.005 = 0.034
  MIDDLE-BAND: multiplicative_minsat in [0.029, 0.034]
  HARD-FAIL: multiplicative_minsat <= 0.029 (T1 advantage does not transfer to Sprint 2)

Run T1 and T2 in parallel (both < 10 min, both CPU, independent).

### 3. INTEG-CONFLICT-T3 -- Conflict-weighted mode switch (ACC-analog)

Anchor pointer: INTEG-CONFLICT-T3 (new, not yet queued; dispatch after T1/T2 results)
Substrate-product reading: Tests whether computing the K x K drive cosine matrix
  and using it to select integration mode (low conflict -> blend, high conflict -> WTA)
  beats both pure integration and best-single on the min_sat metric.
Tier hint: CPU laptop; < 30 min wall; new code but simple (matrix multiply + threshold)
Why-now: The conflict-weighted mode switch is the most mechanistically complete
  single-step fix. If T1 is MIDDLE-BAND and T2 is MIDDLE-BAND, this is the next test.

Pre-reg bands:
  HARD-PASS: conflict-weighted_minsat > max(best-single=0.029, integrated=0.019) + 0.01
  MIDDLE-BAND: conflict-weighted_minsat > 0.029 but lift < 0.01
  HARD-FAIL: conflict-weighted_minsat <= 0.029 (mode switch does not help)

Parameters to sweep: C_low in [0.05, 0.15], C_high in [0.2, 0.4].
Use the existing Sprint 2 drive vectors; compute 5x5 cosine matrix from them.

### 4. INTEG-DRIVE-COSINE-DIAG -- Drive cosine diagnostic (informational)

Anchor pointer: INTEG-DRIVE-COSINE-DIAG (new, not yet queued; can run immediately)
Substrate-product reading: Computes the 5x5 drive cosine matrix from Sprint 2 drives,
  frustration index F, and Fiedler value lambda_2. Routes to the correct integration
  mechanism: F < 0.2 -> renorm+additive; F > 0.5 -> WTA/GWT; F in [0.2, 0.5] -> multiplicative.
Tier hint: CPU laptop; < 2 min wall; diagnostic only (no queue, no metrics.json needed)
Why-now: This diagnostic should run BEFORE any integration architecture work.
  It reveals whether drives are anti-correlated (frustration), correlated (cooperative),
  or orthogonal (independent), which determines which rescue path is correct.

No pre-reg thresholds (informational only). Output: frustration index F + Fiedler value.
Findings route exp_dev to the correct T1/T2/T3 emphasis.

### 5. INTEG-GWT-T4 -- Global Workspace Broadcast (complete architecture)

Anchor pointer: INTEG-GWT-T4 (from earlier handoff, renamed for ordering)
Previously: INTEG-GWT-T2 from exp_dev_handoff_research_substrate_integration_5x_2026-06-10.md
Substrate-product reading: Tests GWT broadcast (winning drive writes to shared slot,
  all drives read from slot, priority decays after selection). Avoids norm dilution
  entirely. Most complete mechanistic fix, addressing all 5 failure modes.
Tier hint: CPU laptop; ~ 60 min wall; new protocol but only dot products + scalar ops
Why-now: Dispatch only if T1 and T2 are both MIDDLE-BAND or HARD-FAIL.

Pre-reg bands:
  HARD-PASS: W_slot cosine similarity to correct drive > 0.8 within 5 steps for
             drive overlap conditions [0.0, 0.05, 0.10, 0.15]
  MIDDLE-BAND: converges within 5-15 steps at overlap <= 0.10
  HARD-FAIL: W_slot cosine < 0.5 after 20 steps at drive overlap = 0.0

---

## Context pointers

- Primary research note: d:/AI/hd-instrument/notes/research_drill_integration_algebra_rescue_2x_2026-06-10.md
- Earlier integration research: d:/AI/hd-instrument/notes/research_drill_substrate_integration_5x_2026-06-10.md
- Earlier arbitration research: d:/AI/hd-instrument/notes/research_drill_multi_drive_arbitration_5x_2026-06-10.md
- Sprint 2 experiment metrics: d:/AI/hd-instrument/data/exp_integration_algebra_flow_cpu_v1/metrics.json
- T1 softmax experiment metrics: d:/AI/hd-instrument/data/exp_integ_softmax_t1_cpu_v1/metrics.json
- Earlier GWT handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_integration_5x_2026-06-10.md

---

## Contract section

exp_dev MUST:
1. Run INTEG-DRIVE-COSINE-DIAG first (< 2 min, diagnostic, informs all subsequent anchors).
2. Run INTEG-RENORM-T1 and INTEG-MULT-SPRINT2-T2 in parallel (both < 10 min, independent).
3. Report T1+T2 verdicts before dispatching T3 or T4.
4. Do NOT dispatch T4 (GWT) until T1 and T2 are both MIDDLE-BAND or HARD-FAIL.
5. All tests are CPU-only. No cloud.
6. Use the existing Sprint 2 experiment drive vectors, not synthetic -- the frustration
   structure of the actual Sprint 2 drives is what matters.

---

## Autonomy declaration

exp_dev is authorized to:
- Choose any normalize implementation (torch.nn.functional.normalize, /torch.norm, etc.)
- Set multiplicative formula (exp(sum_k w_k * log(d_k)), elementwise product, or geometric mean)
- Tune C_low, C_high thresholds within [0.05, 0.4] for T3
- Run T1, T2, and diagnostic simultaneously if CPU capacity allows
- Declare early verdict if margin difference is unambiguous after first seed
- Write results to data/exp_INTEG_RENORM_*/metrics.json etc. per standard format
- Combine T1 (renorm) + T2 (multiplicative) into a single T1+T2 joint experiment if
  code structure allows
