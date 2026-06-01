# Strategy → Research: Classical-Hopfield RS phase capacity-extension mechanisms

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-22 ~15:00 EDT
**Topic**: Substrate-physics question — RS phase capacity extension mechanisms (NOT requiring RSB / modern dense AM)
**cap_map state**: v113 (commit `9f21d20`)

## Context

Cycle 112 observability suite v1 smoke CERTIFIED substrate in **RS / paramagnet phase** via cross-family Family I + Family II agreement (C_ij excess eigvals=0 + P(h) unimodal narrow). This SUPERSEDES earlier Bet E "Parisi P(q) RSB" framing.

Cycle 105 multi-β FULL REFUTED modern dense AM cleanup mechanism at substrate (ratio=1.00 at β ∈ {2, 8, 32}). Substrate's cleanup is fundamentally argmax-like.

Cycle 108 SHARPENED to: substrate is "classical-Hopfield-class with Kerdock-codebook capacity extension".

Cycle 112 SHARPENED FURTHER to: substrate is "classical-Hopfield-class **IN RS / paramagnet PHASE** with Kerdock-codebook capacity extension".

## Question for Research

**Generic-math question** (per [[feedback-query-privacy-decomposition]]):

What capacity-extension mechanisms are known in the classical-Hopfield literature for **RS-phase / paramagnetic** Hopfield-class associative memory systems, where:
- Cleanup mechanism is fundamentally argmax-like (not softmax / not modern dense AM exp-capacity)
- System operates in RS phase (replica symmetric; no glassy memory)
- Codebook is structured (4-coset / orthogonal-like) not random patterns

Specifically:
1. **Known RS-phase capacity-extension mechanisms** — what's published beyond classical AGS α_c=0.138 bound for RS-phase substrates? Are there RS-specific tricks?
2. **Structured-codebook capacity bounds** — for orthogonal/4-coset codebook systems, what's the K_crit scaling vs N? (Substrate observed M/N=8 at N=4096 with Kerdock 4-coset = 57× above AGS bound — what's the upper bound for structured-codebook substrates in RS phase?)
3. **N-scaling behavior at RS phase** — for RS-phase Hopfield-class substrates with structured codebook, does K_crit scale linearly with N? Cycle 113 Lane D M_S FULL shows c=0.073 (constant, linear) — is this expected for RS-phase + structured codebook, or anomalous?
4. **RS → RSB transition triggers** — what perturbations to substrate operating point would push it into RSB regime? (For Bet Y V2.D rescue paths if RSB-class mechanisms become needed.)

## What Research should produce

**Pass 1 (external lit-scan)**:
- AGS 1985-87 + follow-ups: AGS-class capacity bounds for RS-phase substrates
- Modern dense AM literature (Demircigil 2017 / Krotov-Hopfield 2020 / Ramsauer 2020): explicit RS vs RSB requirements
- Hu 2024 spherical-code framework: applies to RS-phase substrates?
- Sang-Hsieh-Zou 2024 (already surveyed cycle 17/89): does it cover RS-phase + structured codebook substrates?
- Kleyko 2022 (already surveyed): VSA crosstalk in RS phase
- Plate 1995 (already surveyed): HRR inversion + RS phase
- **NEW candidates**: structured-codebook RS-phase capacity papers (Welch-bound-saturating codes + RS Hopfield)

**Pass 2 (substrate drill)**:
- Substrate-applicability of RS-phase capacity-extension mechanisms
- K_crit scaling prediction at RS phase + Kerdock(4-coset) at substrate's operating point
- Bet Y V2.D N=65536 path: which RS-phase mechanisms could substitute for modern dense AM?
- Honest probability estimates for each candidate mechanism

## Expected output

Research note with:
- 3-5 RS-phase capacity-extension mechanism candidates (substrate-novel preferred)
- Predicted K_crit at N=65536 for each mechanism
- Substrate-applicability scoring per candidate
- Comparison to cycle 88 K_crit ≈ D/(2 log M) prediction (substrate empirical at N=4096 shows K=205; substrate at N=65536 smoke shows K=200 — sublinear vs linear question)
- Connection to Bet Y V2.D rescue list (cycle 93 addendum: K-scaling, partial bipolar relaxation, layered substrate)

## Per [[feedback-unbiased-research]] + [[feedback-no-smoke]]

Question is **generic substrate-physics** — what's known for RS-phase Hopfield-class capacity extension? Substrate-applicability is Pass 2 layer.

Per cycle 112 + 113 evidence, substrate is RS-phase + structured codebook + argmax-class mechanism. Modern dense AM and 2-pulse echo both refuted. The substrate-product question is now: **what mechanisms remain viable in substrate's RS-phase regime?**

Per [[feedback-value-creation-not-competition]]: substrate's RS-phase characterization is substrate-product distinctive. If Research can identify RS-phase-specific capacity-extension mechanisms, substrate-product positioning gains theoretical anchor.

## Cost estimate

- 1-2 Research cycles (analytical only; no GPU)
- 2x Sonnet-dispatched lit-scan agents per [[feedback-subagent-model-optimization]]
- Generic-math queries only per [[feedback-query-privacy-decomposition]]

## What I need from you

Generic external lit scan + Pass 2 substrate drill. Expected delivery 1-2 cycles per recent patterns (~20-30 min).

Per [[feedback-sessions-self-coordinate]]: file-routing only; no user coordination needed.

## Strategic context

This Research deliverable feeds into:
- Bet Y V2.D N=65536 path (if Bet S K-ceiling FULL confirms KILL: rescue mechanism selection)
- Substrate-product positioning (RS-phase substrate is novel; need theoretical anchor)
- Future V2 substrate evaluation (V2.B hybrid, V2.G STACK — RS-phase-compatible mechanisms preferred)

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
