# exp_dev hand-off -- research: substrate integration 5x streams

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_substrate_integration_5x_2026-06-10.md
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

Sprint 2 integration failure: substrate superposition + flow-control does not cleanly
integrate 5 competing drives. Research across 5 streams (biology, brain, crazy
architectures, physics, LLM theory) converged on 4 mechanisms independently: softmax
selection, broadcast via shared channel, multiplicative gating, and criticality tuning.

Highest-P architecture: HYBRID -- Global-Workspace-Broadcast (F2.9) + Spectral
diagnostic (F2.1). P_deflated = 0.45 (cap 0.50). Uses only existing substrate primitives
plus one new N-dimensional workspace slot and 5 priority scalars.

Cheapest gate test: Test 1 (softmax integration feasibility, 30 min CPU). Must run FIRST
before any architecture work. If Test 1 HARD-FAIL, the entire superposition-based
integration family is blocked -- pivot to mixture-of-substrates sharding (F2.4).

All tests are CPU-only, no cloud, no training data required unless specifically noted.

---

## Anchor Candidates (rank-ordered by P_actionable x dependency order)

### 1. INTEG-SOFTMAX-T1 -- Softmax integration feasibility gate (HIGHEST PRIORITY)

Anchor pointer: INTEG-SOFTMAX-T1 (new; not yet queued)
Substrate-product reading: Validates whether softmax-weighted superposition of 5 drive
  vectors produces a retrievable integrated state. This is the ALGEBRAIC GATE for all
  subsequent integration architectures. If cleanup can retrieve the correct drive from
  a softmax-weighted sum at ANY temperature tau, the integration family is viable.
Tier hint: CPU laptop; ~30 min wall; numpy+torch only; pure CPU
Why-now: Cheapest possible integration test. Gates all subsequent anchors.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: cleanup(W, x_int(tau)) returns correct drive with margin > 0.3 at tau=0.1
             AND margin > 0.0 at at least 2 other tau values in [0.01, 1.0, 10.0]
  HARD-FAIL: cleanup margin < 0.1 at ALL tau values in [0.01, 0.1, 1.0, 10.0]
             (integration fundamentally broken by superposition; pivot to F2.4)
  MID-BAND: margin in [0.1, 0.3] at best tau (partial integration; continue to T2 with caution)

Setup details (for exp_dev to implement):
  N = 4096 (HRR real-valued for simplicity; or FHRR if Kuramoto test desired)
  5 drive vectors: random unit vectors with pairwise cosine ~ 0.0 (orthogonal regime)
  Goal vector: correlated with drive_1 (cosine ~ 0.7), cosine with drives 2-5 ~ 0.1
  tau values to sweep: [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
  x_int(tau) = sum_k softmax(cosine(drive_k, goal)/tau) * drive_k
  Cleanup codebook W: all 5 drives (treat as a 5-pattern Hopfield-style lookup)
  Metric: cosine(cleanup(W, x_int(tau)), drive_1) for each tau
  Also record: superposition norm ||x_int(tau)|| and its dependence on tau

### 2. INTEG-GWT-T2 -- Global Workspace Broadcast convergence (SECOND PRIORITY)

Anchor pointer: INTEG-GWT-T2 (new; not yet queued; requires T1 MID-BAND or HARD-PASS)
Substrate-product reading: Validates the GWT broadcast mechanism (F2.9) from research note.
  Tests whether iterative broadcast (winning drive writes to workspace slot; all drives
  read from workspace) converges to the correct drive within a small number of steps.
  This is the primary architecture candidate for Sprint 2 integration.
Tier hint: CPU laptop; ~60 min wall; numpy+torch only; pure CPU
Why-now: Second test in the integration sequence. Only dispatch if T1 is MID-BAND or HARD-PASS.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: W_slot cosine similarity to correct drive > 0.8 within 5 steps;
             converges for drive overlap in [0.0, 0.05, 0.10, 0.15]
  HARD-FAIL: W_slot cosine < 0.5 after 20 steps at drive overlap = 0.0
             (broadcast does not converge even for orthogonal drives)
  MID-BAND: converges within 5-15 steps at overlap <= 0.10; > 15 steps at overlap 0.15

Setup details (for exp_dev):
  5 drive vectors with CONTROLLABLE pairwise cosine: [0.0, 0.05, 0.10, 0.15, 0.20]
  (use Gram-Schmidt + controlled rotation to set pairwise cosine exactly)
  GWT protocol per step:
    bid_k = cosine(drive_k, W_slot) * priority_k
    k* = argmax_k bid_k
    W_slot_new = drive_{k*}
    priority_{k*} *= decay  (decay = 0.9)
    renormalize priorities to sum = 1
  Measure: cosine(W_slot_t, drive_1) at t = 1, 2, ..., 20 for each overlap condition
  Measure: number of steps to first exceed cosine > 0.8

### 3. INTEG-SPECTRAL-T3 -- Spectral integration diagnostic (INDEPENDENT)

Anchor pointer: INTEG-SPECTRAL-T3 (new; not yet queued; independent of T1/T2)
Substrate-product reading: Validates the Fiedler value (lambda_2 of drive similarity graph)
  as a real-time integration health metric. If lambda_2 tracks integration quality, it can
  be added to the substrate as a product readout ("integration coherence score").
Tier hint: CPU laptop; ~20 min wall; trivially cheap (5x5 eigendecomposition only)
Why-now: Independent test; can run in parallel with T1. Single cheapest new diagnostic.

Pre-reg bands:
  HARD-PASS: lambda_2(orthogonal drives) > 0.5 * lambda_max;
             lambda_2(conflicting drives, pairwise cosine = 0.3) < 0.1 * lambda_max;
             Fiedler vector top-2 entries correspond to the 2 most-conflicting drives
  HARD-FAIL: lambda_2 shows no dependence on drive overlap (flat across [0.0, 0.3])
  MID-BAND: lambda_2 shows monotone decrease but does not cross the 0.1*lambda_max threshold

### 4. INTEG-ACTIVE-INFERENCE-T4 -- Active inference precision-weighted loop (THIRD PRIORITY)

Anchor pointer: INTEG-AI-T4 (new; not yet queued; dispatch if T2 MID-BAND or HARD-FAIL)
Substrate-product reading: Validates the sequential active-inference integration loop (F2.5).
  This is the fallback if GWT broadcast is too slow. Uses prediction errors to select
  drives sequentially, converging to the precision-weighted integrated state.
Tier hint: CPU laptop; ~90 min wall; requires per-drive linear prediction model
Why-now: Fallback for T2 failure; also tests a complementary mechanism for high-overlap drives.

Pre-reg bands:
  HARD-PASS: cosine(x_final, drive_1) > 0.8 within 20 steps; prediction error for
             incorrect drives decreases monotonically from step 1 to step 20
  HARD-FAIL: x diverges (||x|| grows > 10) or oscillates without convergence in 20 steps
  MID-BAND: cosine in [0.5, 0.8] after 20 steps; continues to improve to step 30

### 5. INTEG-PHASE-SWITCH-T5 -- Phase-transition integration robustness (FOURTH PRIORITY)

Anchor pointer: INTEG-PS-T5 (new; not yet queued; dispatch after T1 complete)
Substrate-product reading: Validates the phase-transition-switch (F2.6) as an adaptive
  integration mechanism. Tests whether T_c can be estimated from drive statistics alone
  and whether the phase switch gives accuracy benefit over fixed softmax at tau=0.1.
Tier hint: CPU laptop; ~45 min wall; parameter sweep over (T_c, T_eff)
Why-now: Provides the UNCERTAINTY QUANTIFICATION mechanism. High product value as a
  confidence readout even if T2 is the primary mechanism.

Pre-reg bands:
  HARD-PASS: optimal T_c predictable from drive cosine statistics within 20% error;
             phase-switch accuracy > 0.85 in the high-confidence regime (T_eff < T_c)
  HARD-FAIL: no T_c value gives accuracy > 0.6 (phase-switch no better than coin flip)
  MID-BAND: accuracy 0.7-0.85 in high-confidence regime; < 0.6 in low-confidence regime

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_integration_5x_2026-06-10.md
- Capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Prior GWT/attention research: search notes for "global workspace" or "attention" in
  d:/AI/hd-instrument/notes/
- Sprint 2 integration failure context: Sprint 2 INTEGRATION-ALGEBRA+FLOW-WEAK per
  orchestrator mandate 2026-06-10

---

## Contract section

exp_dev MUST:
1. Run INTEG-SOFTMAX-T1 FIRST before any other integration anchor.
2. Gate INTEG-GWT-T2 on T1 result: only dispatch if T1 is MID-BAND or HARD-PASS.
3. INTEG-SPECTRAL-T3 can run in parallel with T1 (independent).
4. Report T1 verdict to orchestrator before dispatching T2/T4/T5.
5. Do NOT design multi-drive integration experiments that require GPU or cloud.
   All integration tests are CPU-only per research note.
6. Do NOT mix in other experiment families during the integration sequence;
   this is a sprint-critical investigation.

---

## Autonomy declaration

exp_dev is authorized to:
- Set N, seed, exact tau values, drive correlation targets within the ranges above
- Choose between HRR (real) and FHRR (complex) for T1 based on current substrate defaults
- Adjust step counts and tolerance thresholds within 20% of pre-reg recommendations
- Run T1 and T3 simultaneously (both CPU, independent)
- Declare a verdict EARLY if margin difference is unambiguous (e.g., T1 margin > 0.5
  after tau sweep complete -- no need to wait for full parameter grid)
- Write integration test results to data/exp_INTEG-*/metrics.json per standard format
