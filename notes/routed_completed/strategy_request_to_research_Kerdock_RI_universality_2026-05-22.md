# Strategy → Research: Kerdock 4-coset codebook — RI universality assessment for Bayes-AMP/VAMP applicability

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-22 ~15:30 EDT
**Topic**: Pre-investigation — does substrate's Kerdock 4-coset codebook satisfy AMP state-evolution matrix-class requirements?
**cap_map state**: v114 (commit `95795f1`)
**Predecessor**: `strategy_request_to_research_RS_phase_capacity_mechanisms_2026-05-22.md` (delivered as Research note 15:15 EDT)

## Context — cycle 114 critical caveat

Cycle 114 Research delivery identified **Bayes-AMP/VAMP P=0.75 substrate-novel candidate** replacing refuted modern dense AM (cycle 105). Couples to Bet Z.1 SRHT (cycle 110 viable) + cued holistic readout (cycle 110).

But Research flagged a critical caveat (verbatim):

> "AMP's state-evolution proofs assume IID Gaussian (Bayes-AMP) OR
> right-rotationally-invariant (VAMP) measurement matrix. Substrate's
> 4-coset (Kerdock) codebook is an algebraic / deterministic
> construction — it is NOT automatically in the RI universality class.
> Berthier-Montanari-Nguyen 2020 establishes universality for
> sub-Gaussian IID columns but does NOT extend to fully correlated
> algebraic codebooks. Whether substrate's codebook satisfies AMP's
> matrix-class assumption is an open empirical question that must be
> tested before any AMP-based readout claim is shipped."

**This empirical question gates substrate-product roadmap**:
- If Kerdock satisfies RI universality → Bayes-AMP/VAMP can ship as Bet Z.3 (substrate-novel mechanism replacement)
- If Kerdock does NOT satisfy RI universality → Bayes-AMP/VAMP doesn't apply at substrate; need alternative mechanism (pseudoinverse F2, three-threshold F2, or V3 substrate investigation)

## Question for Research (generic-math framing)

**Pass 1 (external lit-scan)**:

1. **Kerdock code matrix class**: Kerdock 4-coset codes are derived from Reed-Muller R(1, m) shifted by Z_4 cosets. What is the matrix-class characterization of Kerdock matrices in the AMP universality literature?
   - Are they known to satisfy Berthier-Montanari-Nguyen 2020 sub-Gaussian universality? (Substrate would need columns of Kerdock matrix to be sub-Gaussian iid — likely NOT given algebraic structure.)
   - Are they right-rotationally-invariant (VAMP class)? (Likely NOT — algebraic construction, not Haar-distributed right singular vectors.)
   - Do they satisfy any weaker universality class (e.g., asymptotic singular value distribution that matches AMP state-evolution predictions empirically)?

2. **Structured codebook AMP universality results**:
   - Hadamard matrices (Subsampled Randomized Hadamard Transform per cycle 110 Bet Z.1): proven to satisfy AMP universality at sub-sampling rate per Krzakala et al? Or specific theoretical results?
   - Reed-Muller / RM codes: any AMP universality results?
   - Bent functions / Kerdock-class specifically: any published AMP analysis?

3. **Empirical AMP universality tests for non-IID structured codebooks**:
   - What empirical tests exist that diagnose whether a given matrix class supports AMP state-evolution? (E.g., singular value distribution matching Marchenko-Pastur? Sub-Gaussian moment conditions?)
   - Cheap empirical pre-tests that don't require full AMP implementation.

**Pass 2 (substrate drill)**:

4. **Substrate-applicable verdict**: based on lit-scan + substrate's specific Kerdock 4-coset construction at N=4096:
   - Does Kerdock satisfy AMP universality? Honest YES / NO / OPEN.
   - If YES: under what conditions (e.g., specific Kerdock variant, specific α regime)?
   - If NO: what minimal modification could move substrate to RI-class codebook?
   - If OPEN: what's the cheapest empirical test substrate could run to answer?

5. **Mechanism candidate viability**:
   - If Kerdock fails RI → Bayes-AMP/VAMP doesn't apply → which F2 mechanism (pseudoinverse P=0.65 vs three-threshold P=0.60) becomes substrate-novel candidate?
   - Substrate-product implications for Bet Z.3 candidate slot

## What Research should produce

Research note with:

- Kerdock 4-coset matrix-class characterization vs AMP universality requirements
- 3-5 published references on structured-codebook AMP universality (or absence of such)
- Verdict: YES / NO / OPEN on Kerdock RI universality
- If YES: minimal viability conditions + Bet Z.3 = Bayes-AMP/VAMP shipping clearance
- If NO: substrate-product implications + alternative mechanism recommendation (F2 family)
- If OPEN: cheapest empirical test specification

## Cost estimate

- 1-2 Research cycles (analytical-only; no GPU)
- 2x Sonnet-dispatched lit-scan agents per [[feedback-subagent-model-optimization]]
- Generic-math queries only per [[feedback-query-privacy-decomposition]] (e.g., "Kerdock code matrix AMP universality" / "Reed-Muller AMP state evolution" — generic enough)

## Strategic significance

Per cycle 114 + cycle 115 user direction on V3 investigation triggers:

This pre-investigation determines whether substrate is on track for
substantive substrate-product mechanism replacement (Bayes-AMP/VAMP as
Bet Z.3) OR whether substrate is constrained to F2 mechanisms (or
needs V3 substrate investigation).

**Decision tree**:
- **Kerdock YES on RI** → Bayes-AMP/VAMP ships → Bet Y V2.D simplified scope gains posterior-inference layer → substrate-product roadmap strengthens
- **Kerdock NO on RI** → F2 mechanism (pseudoinverse or three-threshold perceptron) becomes primary → substrate-product roadmap modifies but stays within V2
- **Kerdock OPEN** → empirical test specified → cheap follow-up routes the decision

Per [[feedback-no-smoke]]: pre-investigation BEFORE attempting to
build Bayes-AMP/VAMP avoids wasted Exp Dev cycles. Per
[[feedback-rehabilitation-after-rejection]]: if Bayes-AMP fails, F2
mechanisms remain as rehabilitation candidates within V2; V3 still
not warranted.

## What I need from you

Generic external lit scan + Pass 2 substrate drill. Expected delivery
1-2 cycles per recent patterns (~20-30 min like cycle 114).

Per [[feedback-sessions-self-coordinate]]: file-routing only; no user
coordination needed.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
