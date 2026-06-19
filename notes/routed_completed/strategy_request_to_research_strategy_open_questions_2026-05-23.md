# Strategy → Research: Strategy's open substrate-physics questions at v149

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-23 ~09:40 EDT
**Topic**: Strategy's open Research questions beyond cycle 169 ORDER_PARAM_NONE 2x drill (`36450c5`)
**cap_map state**: v149 (commit `855a837`)
**User directive**: "and ask research your questions"

## Context

User asked Strategy to surface its open Research questions. Beyond cycle 169
2x drill on ORDER_PARAM_NONE (already filed `36450c5`), Strategy has 3 additional
substrate-physics questions open at v149.

## QUESTION 1 — ~25% partial idempotence convergence across 4 measurements

**Empirical pattern**:
- Cycle 121 plateau acc_50hop = 22%
- Cycle 137 ENDPOINT_COLLAPSED = 28/100 distinct endpoints (28%)
- Cycle 145 cluster_census plateau = 22%
- Cycle 164 retraction idem at FULL = 25.5%

**4 independent measurements converge around ~25% substrate-physics "stable
fraction"** at depth L=50 (substrate W^L iteration).

**Strategy question**: what does the ~25% fraction MEAN structurally? Is it:
- A universal Hopfield-class fixed-point fraction at K/N=0.0015?
- Specific to substrate's Kerdock 4-coset codebook?
- Connected to substrate's nearly-degenerate eigenspectrum (cycle 162 K=1000
  λ₁/λ₂=0.986)?
- An emergent property of EXPONENTIAL-decay universality class (cycle 168 Gap 1)?

**Calibration**: this is a SUBSTRATE-NOVEL observation worth characterizing, NOT
a 7th mechanism hypothesis. Per [[feedback-lit-scan-calibration-penalty]]: P ≤ 0.50;
"no published precedent" verdict acceptable.

## QUESTION 2 — BROAD K-resonance band K=900-1500 (non-Arnold-tongue mechanism)

**Empirical pattern** (cycle 165 K_resonance_fine_sweep FULL):
- K=800: period 2
- K=900: period 1 (fixed point)
- K=950: period 1
- K=1000: period 1
- K=1050: period 1
- K=1100: period 2
- K=1200: period 1
- K=1500: period 1
- K=2000: period 31

**Substrate has BROAD K-resonance band K≈900-1500 with fixed-point structure**.
Arnold-tongue mode-locking REFUTED (cycle 162 K1000_IRRATIONAL_FAR λ₁/λ₂=0.986
not rational).

**Strategy question**: what non-Arnold-tongue mechanism produces broad K-resonance
band with fixed-point structure? Specifically:
- Sub-critical regime spectrum gap?
- Kerdock codebook RM(1,m) algebraic resonance band (NOT single K)?
- Substrate W has spectrum gap that aligns with K=900-1500 range?
- Statistical-mechanics phase boundary at K-fraction ~ 1.4-2.3% (K/N ranges)?

## QUESTION 3 — substrate's near-degenerate eigenspectrum interpretation

**Empirical pattern** (cycle 162 K1000_IRRATIONAL_FAR):
- λ₁/λ₂ ≈ 0.986 at K=1000 N=65536 (nearly-degenerate)
- Eigenvalues very close together (not rational commensurability)

**Strategy question**: what substrate-physics meaning does
near-degenerate-but-not-commensurate eigenspectrum have?
- Spectral gap closes at large N?
- Multiple near-equal eigenvalues produce "soft modes" beyond cycle 119 Hessian
  VDOS soft-modes finding (85% near-zero eigenvalues)?
- Connection to EXPONENTIAL-decay universality class (cycle 168 Gap 1)?

## Strategy-relevant context

**Substrate-physics characterization status at v149**:
- ✅ Universality class: EXPONENTIAL-decay (Gap 1 CONFIRMED at FULL)
- ❌ Order parameter: NO stable single-component (Gap 2 REFUTED at FULL; 2x drill filed `36450c5`)
- ✅ RS phase: 5 cross-family anchors at FULL
- 🔬 ~25% partial idempotence (4 independent measurements)
- 🔬 BROAD K-resonance band K=900-1500 (substrate-novel)
- 🔬 Nearly-degenerate eigenspectrum (λ₁/λ₂=0.986 at K=1000)
- 🔬 SHORT LIMIT CYCLES (median 2-8) + N-INVARIANT + weakly K-dependent
- 🔬 28-element endpoint partition
- ❌ 6 mechanism diagnoses refuted (cleanup cross-talk + eigenvalue near-degeneracy
  + Hubness × DPI + HMM/BCJR + cluster trapping + RETRACTION + Arnold-tongue)

**Substrate-novel framing**:
> "Substrate is a deterministic dynamical system in EXPONENTIAL-decay universality
> class, RS phase, with limit-cycle attractor structure (SHORT cycles + BROAD
> K-resonance band + ~25% stable fraction + nearly-degenerate eigenspectrum +
> 28-element endpoint partition). No stable order parameter. 6 mechanism
> diagnoses refuted; substrate-novel."

## What Research should produce

For the 3 questions above:
- Pass 1 — external lit-scan
- Pass 2 — substrate drill: substrate-applicability scoring
- Honest P ≤ 0.50 per [[feedback-lit-scan-calibration-penalty]]
- "Substrate genuinely novel" verdict acceptable

Combine with order parameter 2x drill (`36450c5`) for comprehensive substrate-physics
characterization update.

## Cost estimate

- 1-2 Research cycles
- 2-3 Sonnet-dispatched lit-scan agents
- Generic-math queries per [[feedback-query-privacy-decomposition]]

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery ~15-30 min combined with cycle 169 2x drill.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
