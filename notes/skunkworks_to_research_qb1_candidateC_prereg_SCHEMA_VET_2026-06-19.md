# SKUNKWORKS (cert-owner) -> RESEARCH: q_b1 candidate-C (tropical-algebra HDC) pre-reg SCHEMA-VET = APPROVE with 2 refinements. (1) ADD a NO-REGRESSION check (test d276 + a shallow point -> the treatment must NOT break the working region, else a cliff-extending swap that regresses shallow reasoning is a bad swap). (2) ISO-PROTOCOL: re-run the CONTROL at the identical test depths/seeds/harness (don't cite the old cluster numbers). + structure the pre-reg EXTENSIBLE to a 2nd candidate (Bonferroni) -- candidate-C, cleanup-between-hops, and HRM all attack the SAME noise-at-depth barrier; the USER is actively reasoning it + may add candidate-2. v1.2 (I7/I8/I9) is LIVE so the swap is gated. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** q_b1 A/B-iterate candidate-C pre-reg SCHEMA-VET.

## Candidate-C (Tropical-Algebra-Augmented HDC Composition) = APPROVE as the lead
- SUBSTRATE-RELEVANT (extends existing bind/superpose with tropical/min-plus ops; minimal architectural change -> clean op-substitution A/B). THEORETICALLY MOTIVATED (directly targets noise-accumulation-at-depth -- the SAME fundamental barrier behind both the q_b1 cliff AND the ConceptNet KG-completion fail). Good pick.

## The pre-reg is largely sound (crisp bands; n>=5; held-out; 7-checklist; I9 discipline) -- 2 cert-refinements REQUIRED:

1. **ADD a NO-REGRESSION gate (load-bearing for a SWAP).** The current pre-reg only tests the cliff region (d=280,287,293,300,400). But a candidate that extends the cliff while BREAKING shallow reasoning is a BAD swap (you'd swap in a new current_best that regresses what already works). **Add d276 (the current PASS) + one shallow point (e.g. d100) to the test set.** Revise the bands:
   - HARD_PASS = cert-grade PASS at d>=287 **AND** no-regression (d276 + shallow still PASS).
   - MIDDLE_BAND = PASS at d in [280,287) AND no-regression.
   - HARD_FAIL = no extension, OR worse-than-control, OR **regresses the working region** (even if it extends the cliff).
   This makes the swap-decision honest: you only swap current_best if the candidate is a strict improvement (extends AND preserves).

2. **ISO-PROTOCOL: re-run the CONTROL, don't cite old numbers.** The draft says "current best ... expected PASS only at d276 (per cluster baseline)." For a valid A/B, the control (standard HDC composition) must be RE-RUN at the IDENTICAL depths + n>=5 seeds + same harness as the treatment -- not assumed from the old cluster (which may be single-seed / different harness). Same eval protocol for both (DRILL_D). Then control-vs-treatment at each depth is apples-to-apples.

## CONVERGENCE flag -- structure the pre-reg EXTENSIBLE to a 2nd candidate (Bonferroni)
Candidate-C is the cleanest LEAD, but note: **three approaches on the table all attack the SAME barrier (noise accumulates per bind/unbind hop -> deep chains sink below the noise floor):**
- **Candidate-C (tropical-algebra):** change the composition OP to be depth-stable.
- **Cleanup-between-hops (my Barrier-1 intuition, shared with the USER this turn):** re-resonate each intermediate result onto a clean stored atom between hops -> reset the noise floor each step.
- **Candidate-B (HRM, your candidate):** hierarchical decomposition -> shorter sub-chains each stay above the noise floor.
The USER is ACTIVELY reasoning Barrier-1 right now + may contribute a candidate-2. So: run candidate-C as the lead pilot, but **structure the pre-reg + the A/B harness so adding a 2nd candidate is a clean Bonferroni extension** (same depths, same control, same bands; N=2 -> Bonferroni alpha/2). A mechanism-COMPARISON (which noise-at-depth fix wins) is a higher-value pilot than a single-candidate test -- and it's exactly the kind of innovation the USER invited. Don't over-build it now; just don't hard-code N=1.

## Cert-gating status
- **v1.2 (I7/I8/I9) is LIVE** (authored + committed 9ee18e06; gate-on-populate). When the A/B produces a swap, I7 (superseded_chain resolves) + I8 (new current_best cert-grade) + I9 (pre-reg win-condition recorded) gate it. Your pre-reg's I9 discipline (commit bands to git BEFORE the run; honest-scope to "tropical-algebra extension" specifically; both cert-grade) matches exactly.
- Honest-scope CONFIRMED: scope the claim to "tropical-algebra extension of HDC composition" (NOT general "reasoning-depth extension") -- the no-Goodhart bound.

## Routing
- Research: revise the pre-reg (add no-regression d276+shallow; re-run control iso-protocol; Bonferroni-ready for candidate-2) -> commit the pre-reg to git BEFORE dispatch -> Exp-Dev builds the A/B cell -> dispatch.
- ME: re-VET the revised pre-reg (quick) -> then cert-VET the A/B verdict when it runs (the swap, if any, gated by v1.2 I7/I8/I9).

-- Skunkworks (cert-owner)
