# Strategy → Research: V2 substrate evaluation — gain/loss assessment for each candidate

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-21 ~20:45 EDT
**Topic**: User-directed — evaluate the 5+ V2 substrate candidates with quantitative gain/loss assessment

## Context

Per cap_map v77 + v78 + Bet X UNIFYING insight: substrate's d=25
compositional cliff IS the VSA-class bound. Current-arch rescues
(Bet P/R31/R32/Bet R/R27 L.2/R33) can extend d marginally WITHIN the
bound; exceeding it requires V2 substrate architectural change.

User direction: "have research evaluate the highest value v2
substrates, and come to a guess on what we gain and lose."

## V2 substrate candidates to evaluate

Strategy-identified candidates from accumulated research notes:

### V2.A — Hyperbolic-tiling substrate (R34 / R17 Sketch A)
- Atoms on {5,4} hyperbolic tiling / Bethe lattice instead of flat N=4096 codebook
- Enables HaPPY codes (Pastawski-Yoshida-Harlow-Preskill 2015)
- Okunishi-Takayanagi 2024 holographic RG for classical Ising
- p-adic AdS/CFT predictions for boundary scaling dimensions

### V2.B — Hybrid HRR + bipolar substrate (Bet X research)
- Current bipolar ±1 substrate PRESERVED
- Add parallel real-valued HRR pool for compositional sequences
- Substrate retrieves from bipolar for capacity/Mirage probes; uses HRR pool for chained composition
- Bet X P(ships) jumps 30-40% → 60-70%

### V2.C — N≥65536 with codebook optimization (R36)
- Larger N (8-16× current N=4096)
- Per-codebook ε_corr optimization (R36 deep-drill: v4 Kerdock optimal at ε_corr=0.4 vs v8's 0.15)
- Not just scaling N — requires codebook structural redesign

### V2.D — Explicit modern exponential-capacity dense AM (R38 lit scan)
- Replace softmax(β=32) approximation with explicit Demircigil exponential energy
- Welch-bound-saturating codebooks (Hu 2024 spherical-code framework)
- Per R38: "modern exponential-capacity dense AM is the real competitor, not vanilla Hopfield"

### V2.E — Operator-algebra QEC code substrate (R17 Sketch C)
- Cast substrate AS operator-algebra QEC code per Harlow 2017
- R17 Probe 1 already empirically supports (area-law-like Renyi-2 scaling at large N)
- Area-law entropy guarantees; substrate-as-code framing

### V2.F — Magnon / phasor codebook (R32 M.1)
- Standing-wave-mode codewords instead of random ±1
- Substrate-novel construction validated by R32 Pass 2
- Collective dynamics; structured-codebook tradeoffs

## What Research should produce

For EACH V2 candidate (V2.A through V2.F), per [[feedback-no-smoke]]
+ [[feedback-value-creation-not-competition]] + brutal honesty:

### Quantitative gain/loss table per V2 candidate

| Substrate-product axis | Current v1 substrate | V2.X gain/loss | Confidence |
|---|---|---|---|
| Capacity (M/N at N=4096) | Bet C ✅ M/N=8 (Kerdock v4) | ? | ? |
| Multi-hop depth d | d=25 (VSA-class bound) | ? | ? |
| Multi-task CL retention | 0.954 (Bet B EMA-blend ✅) | ? | ? |
| Cleanup compute per query | O(N·K) | ? | ? |
| Memory footprint | O(N²) for W | ? | ? |
| Engineering complexity (relative) | baseline 1.0 | ? | ? |
| Compatibility with existing primitives | preserves all 8 Tier-1 ✅ | ? loses what? | ? |
| Substrate-novel insight potential | 5-source spin-glass; d=25 VSA-bound | ? | ? |

### Honest probability estimates per V2 candidate

- P(V2.X ships as substrate-product within 6 months engineering): ?
- P(V2.X exceeds current N=4096 substrate on ≥3 axes): ?
- P(V2.X loses ≥1 current ✅ capability — i.e., breaks something): ?
- P(V2.X is dominated by another V2 candidate): ?

### Recommended substrate-product priority

- Which V2 candidate has highest expected substrate-product value?
- Which is closest to actionable (engineering tractable)?
- Which is highest theoretical risk (might not deliver)?
- Should ANY V2 candidate be promoted to active development?

## Per [[feedback-unbiased-research]]: 2x deep research

### Pass 1 (external lit-scan, broad)

For each V2 candidate, locate:
- Recent (2020-2026) empirical demonstrations or theoretical analyses
- Engineering tractability assessments
- Performance comparisons to vanilla Hopfield / fully-connected
- Failure modes / things that don't work

### Pass 2 (substrate drill)

For each V2 candidate:
- Which current substrate primitives (Bet 1 ICL / Bet 2 erase / Bet A
  edit-then-query / Bet B EMA-blend / Bet C Kerdock M/N=8 / Bet G
  calibration / Bet H autoregressive) survive intact?
- Which break or require redesign?
- Substrate-product framing: what does this V2 give the substrate that
  current-arch can't?
- Engineering cost estimate (cycles, GPU-hours, complexity)

## Per [[feedback-no-papers-product-only]]

Frame as substrate-product engineering choice, not novel-framework
paper. The output is "which V2 to build first" — not "substrate as
[novel mathematical framework]."

## Output expected

Research note `research_V2_substrate_evaluation_<date>.md` with:
- Per-candidate gain/loss tables
- Honest probability estimates
- Recommended sequencing (which V2 to evaluate first)
- Cross-V2 comparison: dominance relationships?

## Sequencing recommendation

This is HIGH PRIORITY research per user direction. Suggested order:
1. **V2 substrate evaluation** (this request) — substrate-product roadmap
2. Phase-transformation research (separate request — substrate regime switching)
3. Bet P-Theory deepening (R36 partial → full bridge)

## What you need from me

Nothing — V2 candidates fully specified above. Per
[[feedback-unbiased-research]], Research's Pass 2 should generate
candidate evaluation independently; Strategy's V2.A-V2.F list is
starting points only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
