# Strategy → Research: 2x drill on ORDER_PARAM_NONE refutation — substrate has universality class but no stable order parameter

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-23 ~09:35 EDT
**Topic**: META Gap 2 ORDER_PARAM_NONE at FULL refutes smoke STABLE — what mechanism produces universality class without order parameter?
**cap_map state**: v149 (commit `855a837`)
**User directive**: "research negative 2x" per [[feedback-rehabilitation-after-rejection]] discipline

## Context — cycle 168 ORDER_PARAM_NONE at FULL

META Gap 2 cycle 163 smoke claimed Parisi-like q_overlap STABLE (seed-consistency
0.940 > 0.85 threshold). Cycle 168 FULL refuted: q_overlap=0.743 < 0.85 threshold.

19th smoke→FULL DIVERGENCE anchor in DEGRADATION direction. META Gap 2
recommendation REFUTED at FULL.

**3 order parameter candidates tested (all FAILED at FULL)**:
- φ_distribution: histogram of cycle phase ϕ(c)
- q_overlap: Parisi-like overlap (1/K) Σ_i,j δ(ϕ_i, ϕ_j)
- C_endpoint: input-codeword to endpoint correlation

## The puzzle

**Substrate-physics paradox**:
- ✅ Universality class identified at FULL (EXPONENTIAL-decay, r²=0.922)
- ✅ RS phase at FULL (5 cross-family anchors at FULL)
- ✅ Limit cycles, partial idempotence, K-resonance structure
- ❌ **NO STABLE ORDER PARAMETER at FULL** across 3 candidates

In materials science, substrates with identified universality classes typically
HAVE order parameters. Critical exponents define how the order parameter scales
near criticality. **Universality class without stable order parameter is unusual**.

Three possibilities:
1. **Substrate genuinely lacks order parameter** (substrate-novel — universality
   class without distinguishing observable)
2. **3 candidates were wrong**: φ_distribution, q_overlap, C_endpoint don't
   capture the substrate's actual order parameter
3. **Order parameter is structurally complex**: multi-component, hierarchical
   Parisi q(x), non-self-averaging, or finite-N artifact

## Question for Research

**Generic-math framing** per [[feedback-query-privacy-decomposition]]:

What mechanism in classical-Hopfield-class associative memory with structured
codebook produces a system with:
- Identified universality class (exponential decay near critical K)
- RS / paramagnet thermodynamic phase
- Limit-cycle dynamics with K-resonance band structure
- ~25% partial idempotence stable across diagnostic tests
- BUT NO stable simple order parameter (Parisi-like q_overlap, cycle-phase
  histogram, input-endpoint correlation all fail)?

Specifically investigate:

1. **Universality classes without order parameters**: are there published
   spin-glass-class systems with critical exponents but no stable
   single-component order parameter?

2. **Non-self-averaging order parameters**: substrate may have order parameter
   that doesn't average across seeds — typical of glassy systems with replica
   symmetry breaking (RSB). Substrate is CERTIFIED RS by 5 cross-family probes,
   but does substrate have HIDDEN RSB at fine scales?

3. **Multi-component order parameters**: Parisi q(x) is hierarchical function,
   not scalar. Substrate's order parameter may be multi-component (e.g.,
   per-K-region order; per-cycle-period order). Single-component candidates
   miss this.

4. **Finite-N artifact**: substrate's order parameter may be defined only at
   N → ∞ thermodynamic limit. At finite N=4096-65536 the order parameter
   is well-defined per realization but doesn't average — seed-consistency
   drops by definition.

5. **Hidden symmetry breaking**: substrate may have spontaneous symmetry
   breaking that produces different "phases" across seeds — q_overlap captures
   one realization but not the symmetry-broken family.

6. **Other substrate-physics mechanisms Research surfaces**

## Calibration discipline

Per [[feedback-lit-scan-calibration-penalty]]: 6 mechanism diagnoses refuted +
META Gap 2 smoke→FULL refutation. Cap P at 0.50. Honest "no fit" verdict
acceptable.

This is a 2x discipline drill on a SPECIFIC negative (ORDER_PARAM_NONE), not
a 7th-attempt mechanism diagnosis. Research's task: characterize the
substrate-novel observation "universality class without stable order parameter".

## What Research should produce

**Pass 1 — external lit-scan**:
- Universality classes without order parameters (or with subtle order parameters)
- Non-self-averaging order parameters in spin-glass-class systems
- Multi-component / hierarchical Parisi q(x) order parameters
- Finite-N vs thermodynamic-limit order parameter behavior

**Pass 2 — substrate drill**:
- For each top 3 candidates, propose substrate-physics test to identify whether
  substrate's order parameter is non-self-averaging, multi-component, or
  finite-N artifact
- If no clean candidate emerges: honest verdict "substrate is in universality
  class without stable single-component order parameter; substrate-novel"

## Cost estimate

- 1 Research cycle (analytical only)
- 2-3 Sonnet-dispatched lit-scan agents
- Generic-math queries

## Substrate-product context

Substrate-product Demo 1 + Demo 2 + N=524K HOLD at v148 level. Order parameter
question is substrate-physics characterization gain, not substrate-product
blocking.

If substrate is in universality class without simple order parameter:
substrate-physics positioning becomes "substrate-novel deterministic
dynamical-system class with exponential-decay universality but no stable
single-component order parameter" — substantial substrate-novel finding.

## Per [[feedback-no-smoke]]

19 smoke→FULL divergence anchors. ORDER_PARAM_NONE at FULL is reliable;
smoke STABLE was wrong. Apply discipline: trust FULL, drill the negative.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 15-30 min.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
