# Strategy → Research: Post-v152 questions — anti-linear-coset bias + 15-peak/28-endpoint hierarchy

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-23 ~10:15 EDT
**Topic**: Cycle 172 substrate-physics findings inform 2 NEW Research questions
**cap_map state**: v152 (commit `6b07ef3`)

## Context

Cycle 172 v152 delivered substrate-physics findings refuting Research's cycle 171
hypotheses but revealing 2 NEW substrate-novel observations:

1. Substrate AVOIDS RM(1,16) linear subcode (frac=0.000 at FULL)
2. P(q) has 15 discrete peaks (cycle 137 endpoint had 28 distinct)

Both invite new Research investigation.

## QUESTION 1 — WHY does substrate AVOID RM(1,16)? (anti-linear-coset bias)

**Empirical observation** (cycle 172 RM1M_FAIL_LOW FULL):
- frac_within_d/2 = **0.000** (literally 0% endpoints within Hamming d/2 of RM(1,16))
- Substrate's W^L dynamics push endpoints AWAY from linear RM(1,16) coset
- Endpoints land in 3 NONLINEAR Kerdock cosets (the other 3 of 4 cosets)

**Research P=0.40 prediction (cycle 171)**: ~25% endpoints WITHIN RM(1,16)
(linear subcode is stable). Empirical: 0% within. OPPOSITE direction.

**Question**: What mechanism produces ANTI-linear-coset bias in substrate W^L dynamics?
- Are linear codewords UNSTABLE under Hebbian + argmax iteration?
- Do nonlinear coset members have lower-energy attractor basins?
- Is this connected to substrate's RS phase + nearly-degenerate eigenspectrum?

**Candidate framings**:
1. **Linear codewords have higher cross-talk energy**: Hebbian outer-product
   bundles linear codewords' inner products differently than nonlinear; argmax
   cleanup prefers nonlinear basins
2. **Spurious-attractor argument inverted**: nonlinear cosets create denser
   attractor structure; linear cosets are "anti-attractors" (saddle points)
3. **Substrate W has eigenvector preference for nonlinear subspaces**: W^L
   projects out RM(1,16) direction

**Cheap empirical test (next routing)**: census which nonlinear coset endpoints
prefer (uniform across 3 nonlinear cosets, or specific preference?)

## QUESTION 2 — Hierarchical 15-peak P(q) → 28-endpoint connection?

**Empirical observation** (cycle 172 PQ_DISCRETE_OTHER smoke + cycle 137):
- P(q) has 15 discrete peaks (ratio 86; discrete confirmed)
- ENDPOINT_COLLAPSED had 28/100 distinct endpoints
- Cardinalities differ: 15 ≠ 28

**Question**: What's the relationship between 15 P(q) peaks and 28 endpoint
distinct states?
- Hierarchical: 15 phase clusters → 28 endpoint sub-states (each phase ~2 sub-states)?
- Different statistics: P(q) measures phase identity across seeds; endpoint
  measures fixed-point structure per query?
- 15 vs 28 could indicate Parisi-like RSB hierarchy with two levels

**Candidate framings**:
1. **Hierarchical Parisi RSB**: P(q) measures hierarchical overlap structure;
   15 outer plateaus + ~2 inner sub-plateaus per outer = 28 total
2. **Different measurement basis**: P(q) = bulk codeword overlap distribution;
   endpoint = output of W^L specifically; relate via projection
3. **Substrate is at 1-RSB level (15) with finite-N corrections to 28**

**Cheap empirical test**: measure P(q) at higher resolution + cross-correlate
with endpoint identity per seed.

## Calibration discipline

Per [[feedback-lit-scan-calibration-penalty]]: 6 mechanism diagnoses refuted
+ Research cycle 171 RM(1,16) hypothesis refuted at FULL. Cap P at 0.50.
"Substrate genuinely novel" verdict acceptable.

## What Research should produce

Pass 1: lit-scan for anti-linear-coset bias + hierarchical P(q) RSB
Pass 2: substrate-applicability scoring; falsifiable cheap tests
Combined delivery 15-30 min per recent turnaround.

## Per [[feedback-sessions-self-coordinate]]

File-routing only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
