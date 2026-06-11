# exp_dev hand-off -- research: integration complete 3x

**Filed-by:** research sub-agent (2026-06-10)
**Trigger:** notes/research_drill_integration_complete_3x_2026-06-10.md
**Sprint 2 context:** integrated_minsat(0.019) < equal-weight(0.022) < best-single(0.029);
  INTEGRATION-RENORM 2x established L2 renorm fix algebraically; 3x drill establishes
  the complete architecture stack and ranks 10 systems by cost and P_deflated.

**Per [[feedback-no-experiment-design-in-prompts]]**: this file names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, drive count K, seed count, threshold bands, queue choice,
anchor name, ETA, smoke profile, FULL profile. Research recommendations below are
STRATEGIC POINTERS -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist.
Do not ship if paused.

---

## Root cause summary (from 3x drill)

The complete diagnosis has three components:

1. NORM DILUTION (primary): additive softmax over K=5 near-orthogonal drives gives a
   combined vector with norm 1/sqrt(K) = 0.447. The cleanup lands in the "desert" between
   attractors. L2 renorm is the direct fix (algebraically guaranteed for sharp softmax).

2. NEAR-UNIFORM WEIGHTS (secondary): Sprint 2 softmax weights are likely near-uniform
   (w_k ~ 1/K) rather than sharp. With uniform weights, renorm does not help -- all drives
   score equally. The fix is top-2 sparse selection before renorm (MoE insight).

3. SINGLE TIMESCALE + NO PRIORITY CYCLING (tertiary): no mechanism prevents one drive from
   monopolizing the integration slot across steps. GWT priority decay fixes this.

The 3x drill also established that GWT broadcast (System 5) and Resonator factorization
(System 7) are ORTHOGONAL and can be composed into a complete pipeline:
  Resonator: exact recovery of individual drives from superposition bundle.
  GWT: broadcast selected drive and cycle through others via priority decay.
  Together: exact recovery -> principled selection -> temporal cycling.

---

## Anchor candidates (rank-ordered by P_actionable x dependency order)

### 1. INTEG-SPARSE-RENORM-T0 -- Top-2 + L2 renorm gate (CHEAPEST, < 30 min CPU)

Anchor pointer: INTEG-SPARSE-RENORM-T0 (new; highest priority)
Substrate-product reading: tests whether selecting only the top-2 urgency-weighted drives
  (not all K=5) and L2-renormalizing the blend resolves the norm dilution + uniform-weight
  failure modes simultaneously. Algebraically guaranteed to lift target score when
  w_top2 > 0.5 (combined top-2 weight). Gates all other integration systems.
Tier hint: CPU laptop; < 30 min wall; modify Sprint 2 integration code only (top-2 mask + renorm).
Why-now: ZERO new architecture. One conditional mask + one normalize call. If HARD-PASS,
  Sprint 2 sprint blocker resolved in < 30 min. Gates all other integration paths.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: integrated_minsat(top2-renorm) > best-single_minsat (0.029)
  MIDDLE-BAND: integrated_minsat in [0.022, 0.029]
  HARD-FAIL: integrated_minsat <= 0.022 (equal-weight; top-2 mask + renorm adds nothing)
             Implies: weights are too uniform OR drives are anti-correlated in action space.

Diagnostic to run BEFORE this anchor: print max(softmax(urgency/tau)) to check if
  w_best > 0.5. If w_best > 0.5: System 1 will work. If w_best < 0.3: need System 5.

### 2. INTEG-GWT-BROADCAST-T1 -- Global-workspace broadcast (< 2 hr CPU)

Anchor pointer: INTEG-GWT-BROADCAST-T1 (new)
Substrate-product reading: implements the 5-step GWT broadcast protocol from
  notes/research_drill_integration_complete_3x_2026-06-10.md Section B2.
  New components: W_slot (N-dim tensor, initialized to goal), priority (K scalars),
  3 scalar HPs (decay, beta_gw, tau_gw). Uses existing substrate cosine primitives.
  Fixes all three root causes: top-k selection (System 1) + context conditioning (W_slot)
  + priority decay for temporal cycling.
Tier hint: CPU laptop; < 2 hr wall; can be dispatched in same run as INTEG-SPARSE-RENORM-T0.
Why-now: run AFTER INTEG-SPARSE-RENORM-T0 if that is MIDDLE-BAND. Also run in parallel
  if INTEG-SPARSE-RENORM-T0 result is ambiguous. GWT subsumes L2 renorm as special case.

Pre-reg bands:
  HARD-PASS: GWT_minsat > best-single_minsat (0.029) within 10 GWT steps
  MIDDLE-BAND: GWT_minsat in [0.022, 0.029] OR convergence requires > 10 steps
  HARD-FAIL: GWT_minsat <= equal-weight (0.022) at any number of steps

Test: sweep decay in [0.8, 0.9, 0.95]; tau_gw in [0.5, 1.0, 2.0]; report best combo.

### 3. INTEG-RESONATOR-T2 -- Resonator network drive factorization (< 2 hr CPU)

Anchor pointer: INTEG-RESONATOR-T2 (new)
Substrate-product reading: tests whether encoding drives as bind(ID_k, content_k) and
  running a resonator network on the superposition bundle recovers each drive with cosine
  > 0.8 within 30 iterations. If resonator converges, select the recovered drive with max
  cosine(content_k, goal) -- this avoids ALL norm dilution and spurious-attractor issues.
  Convergence theorem (Frady & Sommer 2021): approaches probability 1 as N grows for K << N^0.3.
  For K=5, N=8192: K/N^0.3 = 0.22 << 1. Theorem predicts convergence.
Tier hint: CPU laptop; < 2 hr wall. Requires resonator primitive in substrate.
  If resonator primitive absent: implementation cost is < 50 lines Python (iterative unbind-cleanup).
Why-now: this is the MOST ROBUST integration path (exact recovery, not approximate blend).
  Run after INTEG-GWT-BROADCAST-T1. If resonator converges, it becomes the recommended
  integration standard for all subsequent drive work.

Pre-reg bands:
  HARD-PASS: all K=5 drives recovered with cosine > 0.8 within 30 iterations;
             selected drive minsat > best-single (0.029)
  MIDDLE-BAND: factorization converges for K <= 3 but fails for K=5 at N=8192
  HARD-FAIL: factorization fails to converge (cosine of recovered content < 0.5) for K=3.

### 4. INTEG-DIAGNOSTIC-SWEEP -- Conflict index + condensate fraction routing (< 1 hr CPU)

Anchor pointer: INTEG-DIAGNOSTIC-SWEEP (new; supports all other anchors)
Substrate-product reading: computes the three routing diagnostics BEFORE any integration
  experiment: (a) w_best = max softmax weight; (b) C = conflict index; (c) condensate
  fraction = lambda_1(S)/K. These three sub-1ms diagnostics route to the correct integration
  system WITHOUT running the full experiment.
  Validates the routing oracle: does condensate_fraction predict which system is optimal
  across 20 random drive configurations?
Tier hint: CPU laptop; < 1 hr wall; pure diagnostic, no architecture changes.
Why-now: if diagnostics predict system correctly, exp_dev can use them as PRE-FLIGHT checks
  before every integration experiment, saving iterations on future sprint blockers.

Pre-reg bands:
  HARD-PASS: condensate_fraction correctly routes to optimal system for >= 15/20 random configs.
  HARD-FAIL: condensate_fraction shows no correlation with optimal system (< 10/20 correct routing).

### 5. INTEG-PARETO-DIAGNOSTIC -- Pareto front of Sprint 2 drive action space (< 1 hr CPU)

Anchor pointer: INTEG-PARETO-DIAGNOSTIC (new; diagnostic only)
Substrate-product reading: computes the 5-drive Pareto front for the Sprint 2 action space.
  If the front collapses to a single point (drives are positively correlated in action space),
  best-single IS the Pareto-optimal strategy -- integration is unnecessary and the product
  requirement should be reconsidered.
  If the front is a curve (drives anti-correlate), integration CAN improve minsat and the
  Pareto-compromise action (System 9) is the prescription.
Tier hint: CPU laptop; < 1 hr; runs on Sprint 2 codebase without modification.
Why-now: this is the CONTINGENCY DIAGNOSTIC for the case where all 4 integration systems
  (anchors 1-4) produce HARD-FAIL. It determines whether the failure is architectural
  (fixable) or structural (drives do not conflict; integration is impossible to improve).

---

## Context pointers (file paths, not summaries)

- Primary research note: d:/AI/hd-instrument/notes/research_drill_integration_complete_3x_2026-06-10.md
- Prior 2x drill (L2 renorm algebra): d:/AI/hd-instrument/notes/research_drill_integration_algebra_rescue_2x_2026-06-10.md
- Prior 5x drill (5-stream breadth): d:/AI/hd-instrument/notes/research_drill_substrate_integration_5x_2026-06-10.md
- Prior 2x handoff (queue context): d:/AI/hd-instrument/notes/exp_dev_handoff_research_integration_algebra_rescue_2x_2026-06-10.md
- Sprint 2 integration experiment: check data/ for most recent sprint2 integration metrics.json

---

## Contract section

exp_dev owns ALL experiment design decisions. This file provides:
  - Strategic direction (which root cause to target first)
  - Research-informed anchor candidates with P_deflated estimates
  - Context pointers for look-up during design

exp_dev is NOT bound to the pre-reg bands above -- these are research recommendations;
exp_dev may tighten or relax them based on the actual Sprint 2 metric distributions.
exp_dev may reorder anchors based on current queue state and sprint priority.

---

## Autonomy declaration

exp_dev designs and dispatches anchors 1-5 without further orchestrator confirmation
provided:
  (a) data/orchestrator_paused.flag does NOT exist
  (b) exp_dev follows the standard smoke gate before full dispatch
  (c) anchors target CPU-local queue (no cloud dispatch authorization in this handoff)

Cloud dispatch requires separate orchestrator authorization per
[[feedback-cloud-only-when-absolutely-necessary]].
