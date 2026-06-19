# Strategy → Research: 2 follow-up routings from cycle 109 burst

**Sender**: Strategy session (session 1)
**Recipient**: Research session (session 4)
**Date**: 2026-05-22 ~08:40 EDT
**Topic**: User-flagged 2 open follow-ups from Research cycle 109 (3-deliverable burst Entries 113-115); routing as new R-questions

## Context

User direction: "nothing from cycle 109 that should be routed to
research?" — surfaces that Research's 3-deliverable burst (Entries
113 Bet S K-ceiling + 114 N=65536 codebook + 115 substrate-as-OAQEC)
identified two open follow-up questions that weren't routed back.

Filing both as new research questions.

## Request A — R36 retrieval-side capacity drop at N=65536 (substrate-product roadmap)

### From Research Entry 114 (N=65536 codebook engineering)

Direct quote: "codebook cardinality M/N=8 is solved... what's NOT
solved is whether substrate's RETRIEVAL CAPACITY at M/N=8 transfers
from N=4096 (Bet C ✅) to N=65536. R36 deep-drill predicts M/N ∈
[1.2, 6.1] LOWER at N=65536 with current Kerdock v4 due to mechanisms
BEYOND codebook coherence (Hopfield AGS bound + cleanup cross-talk
scaling)."

### Open question

What specific retrieval-side mechanism(s) cause M/N to drop with N at
N=4096 → N=65536? Two candidate mechanisms identified by R36:
- **Hopfield AGS bound scaling**: α_c = 0.138·N grows linearly with N,
  so M_max grows but not as fast as some predictions suggest. Why?
- **Cleanup cross-talk scaling**: K_crit = D/(2 log M) grows with D
  but M also grows. Net effect?

Substrate-product engineering needs precise quantitative prediction:
what's the EXPECTED M/N at N=65536 for Kerdock(16) substrate, and
what mechanism limits it?

### What Research should produce

**Pass 1 (external lit-scan)**:
- Hopfield AGS at N scaling beyond α_c=0.138 — does α_c saturate at
  large N? Recent rigorous results (Hu 2024, Lucibello-Mézard 2024)
- Cleanup cross-talk + extreme-value statistics at large M (Schlegel
  2022 + Ganesan 2021)
- Bidirectional recall capacity at large N (heteroassociative
  literature)
- Modern Hopfield exponential capacity vs AGS classical bound — when
  does which apply?
- M/N scaling with N in published Hopfield literature (any
  measurements at N≥10K?)

**Pass 2 (substrate drill)**:
- Quantitative M/N prediction at N=65536 with Kerdock(16) — closed
  form via combined AGS + cleanup-cross-talk + cross-modal terms
- Mechanism identification: which term dominates at large N?
- Engineering implications: can substrate-product engineering work
  around (e.g., Bet Y V2.D + larger β extends regime)?
- Coupling to Bet Y V2.D modern dense AM: does explicit exponential
  energy avoid the AGS scaling? (Modern Hopfield literature suggests
  α_c → 1 with appropriate F(x))

### Expected output

Research note with:
- Quantitative M/N at N=65536 for Kerdock(16) substrate (numeric range)
- Mechanism identification (which dominates)
- Substrate-product engineering recommendations
- Compatibility / coupling to Bet Y V2.D development

### Cost: 1-2 cycles (analytical-heavy)

## Request B — Geometric entropy + non-commuting structure in Bet Y V2.D (OAQEC pre-investigation)

### From Research Entry 115 (substrate-as-OAQEC)

Direct quote: "DEFER until substrate V2 introduces non-commuting
structure (**Bet Y V2.D modern dense AM exponential energy has
potential non-commuting features per arXiv:2604.07401 geometric
entropy framework**)."

### Open question

Does Bet Y V2.D (modern dense AM with explicit exp(β·x) energy and
softmax-attention-equivalent cleanup) actually introduce non-commuting
structure to substrate? If yes, OAQEC framework (Harlow 2017
RT-from-QEC theorem) becomes applicable at V2 — substrate-novel
theoretical grounding axis re-opens.

Pre-investigation BEFORE Bet Y build avoids wasted exploration.

### What Research should produce

**Pass 1 (external lit-scan)**:
- arXiv:2604.07401 geometric entropy framework precise content
- Modern Hopfield exponential energy + non-commutativity (Krotov-
  Hopfield 2020, Ramsauer 2020 — do their cleanup operators commute?)
- Softmax attention non-commutativity literature
- Quantum-inspired classical AM with non-commuting features

**Pass 2 (substrate drill)**:
- Concrete prediction: does Bet Y V2.D substrate's `argmin_y E(y)` 
  energy descent on E(s) = −β⁻¹ log Σ exp(β·xᵢᵀs) introduce
  non-commuting operators?
- If yes: precise statement of which operators don't commute
- Connection to Harlow 2017 OAQEC theorem (non-commutative algebra
  requirement)
- Probability that Bet Y V2.D enables OAQEC theoretical grounding
- Pre-investigation cost vs Bet Y build cost (engineering vs theory)

### Expected output

Research note with:
- arXiv:2604.07401 substrate-applicability assessment
- Bet Y V2.D non-commuting structure: YES/NO/CONDITIONAL
- If YES: substrate-novel theoretical grounding via OAQEC becomes
  V2 development priority
- If NO: substrate-as-OAQEC stays deferred indefinitely; R16 BBP
  remains primary theoretical anchor

### Cost: 1 cycle (analytical-only; no GPU needed)

## Sequencing recommendation

Both requests are analytical/theoretical with no experimental
dependency. Can run in parallel.

Priority:
1. **Request A** (R36 mechanism investigation) — substrate-product
   roadmap-critical; informs Bet Y V2.D + Kerdock(16) target M/N
2. **Request B** (Bet Y V2.D OAQEC pre-investigation) — theoretical
   grounding axis; lower-urgency than Request A

Both 1-2 cycles per item. Should land before Bet Y empirical work
starts.

## Per [[feedback-unbiased-research]] + [[feedback-no-smoke]]

Both follow-ups derive directly from Research's own cycle 109 notes
flagging open questions. Per [[feedback-no-smoke]]: don't manufacture
new research; route the explicit follow-ups Research itself
identified. Per [[feedback-unbiased-research]]: Pass 2 should generate
mechanism answers independently; Strategy's framing above is starting
point only.

## What you need from me

Nothing — both questions are direct extensions of Research's existing
notes (Entries 114 + 115). Research has full context already.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
