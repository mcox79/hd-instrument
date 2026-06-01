# Strategy → Research: Multi-hop N=65536 mechanism 3rd-attempt diagnosis (post VAMP-on-chain success)

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-22 ~20:15 EDT
**Topic**: 3rd-attempt mechanism diagnosis — VAMP-on-chain success reveals structural clue; 2 prior attempts both refuted
**cap_map state**: v127 (commit `ddfc81e`)
**User directive**: "don't we need to research negative results 2x?" — applying [[feedback-rehabilitation-after-rejection]] discipline; deferring mechanism question (cycle 127 "don't know why" framing) was wrong call

## Context — 2 mechanism diagnoses already refuted; structural clue from rehabilitation success

**Cycle 123 (1st attempt)**: signal eigenvalue near-degeneracy at large N (Agent G P=0.70)
- **REFUTED at cycle 124**: spectral validation smoke shows spans don't cluster as predicted

**Cycle 126 (2nd attempt)**: Hubness × DPI information contraction (P=0.45)
- **REFUTED at cycle 127**: skew DECREASES with N (not grows as predicted); N=4096→1.088, N=16384→0.761, N=65536→0.670

**Plus**: standard cleanup cross-talk (K-1)/N falsified at cycle 123 (predicts shrink with N; opposite of empirical).

**3 mechanism hypotheses refuted total**.

**BUT**: cycle 127 VAMP-on-chain FULL = PERFECT acc_50hop=1.000 reveals
a **STRUCTURAL clue** about the failure mode:

| Mechanism class | Cycle | Result | Structural |
|---|---|---|---|
| Loopy-iterative within-hop (Resonator) | 124 | FAIL 0.200 | within-hop posterior iteration cycles |
| Tree-exact single-pass cross-hop (VAMP-on-chain) | 127 | PERFECT 1.000 | forward-backward EP succeeds |
| Per-hop sparse cleanup | 127 | FAIL 0.200 | within-hop threshold-AMP cycles |
| Bidirectional inference | 127 | FAIL 0.225 | Mofrad-class also cycles |
| K-scaling K=25 | 127 | FAIL 0.000 | bounded but K too small |
| K-scaling K=50 | 127 | PARTIAL 0.417 | K-restricted but works |

**Structural distinction**: tree-exact single-pass works PERFECTLY;
loopy-iterative + within-hop methods FAIL.

## Question for Research — 3rd attempt mechanism diagnosis

**Generic-math framing** (per [[feedback-query-privacy-decomposition]]):

What mechanism would cause multi-hop chain composition in
classical-Hopfield-class associative memory at large N to:
- Degrade chain composition (acc_50hop=0.217 at K=100 N=65536)
- BUT recover PERFECTLY (acc_50hop=1.000) with tree-exact single-pass
  forward-backward EP
- AND NOT recover with loopy-iterative within-hop methods (Resonator,
  Sparse cleanup, Bidirectional)
- AND fail at standard cleanup cross-talk + eigenvalue near-degeneracy
  + Hubness × DPI diagnoses

The structural clue (tree-exact succeeds + loopy-iterative fails)
points to mechanisms where:
- **Forward-only information propagation is lossy** (per-hop accumulates
  drift / partial information)
- **Backward smoothing from downstream evidence corrects** (tree-exact
  message-passing recovers correct chain)
- **Within-hop iteration cycles** (Resonator failure mode)

### Candidate mechanism families to investigate

1. **Partial-observation Hidden Markov Models** — chain hops are
   "noisy emissions" from true latent states; argmax cleanup uses only
   forward info; Kalman-smoother / Viterbi backward pass essential.
   Substrate-applicability?

2. **Lossy information channels with feedback** — per-hop loses ~1-5%
   information (cycle 121 per-hop retention 0.96-0.98); accumulates
   exponentially in forward-only; backward EP recovers via smoothing.
   This is the cycle 126 DPI argument WITHOUT hubness as the
   amplifier.

3. **Substrate "memory leakage" at large N** — argmax cleanup with
   K-dim signal subspace mixed state; without backward correction
   substrate drifts away from correct codeword. Different framing
   from eigenvalue near-degeneracy (which was cycle 123 falsified).

4. **High-D distance concentration without absorbing-state hubness** —
   distance concentration mild contributor; combined with argmax
   commit-or-fail = unrecoverable; smoothing forward-backward recovers
   probability mass.

5. **Information-theoretic bottleneck from K-dim signal in N-dim
   substrate** — at N=65536 K=100, only K/N = 0.0015 fraction of
   substrate dimensions carry signal; argmax cleanup commits to
   highest single dimension; backward pass aggregates across dimensions.

6. **Other mechanisms** Research surfaces

### Pass 1 — external lit scan

Investigate:
- Hidden Markov Models + Kalman smoothing literature
- Lossy channel + feedback / correction literature
- High-D substrate memory leakage without hubness
- Information-theoretic bottlenecks for sparse signals in dense substrates
- Why tree-exact methods succeed where iterative posterior cycling fails

### Pass 2 — substrate drill

- Which candidate mechanism is most consistent with substrate's empirical
  pattern (PERFECT 1.000 with VAMP-on-chain; FAIL with all 4 within-hop
  iterative methods)?
- Substrate-physics implication: what does the rehabilitation success
  tell us about substrate's information flow under multi-hop?
- Honest probability estimates for each candidate (per cycle 126
  calibration discipline: deflate P 0.15-0.25; top P ≤ 0.50)

## What Research should produce

Research note with:
- Mechanism candidates ranked by P (calibrated)
- Substrate-applicability scoring
- Connection to cycle 127 VAMP-on-chain success structural insight
- Substrate-physics characterization gain (even if mechanism not
  fully resolved)

## Per [[feedback-no-smoke]]

Cycle 127 framing "don't know why, know how to fix" + "deferrable to
academic Research" was WRONG call per user pushback. Substrate-physics
mechanism characterization has substrate-product value:
- Helps predict OTHER substrate failure modes at large N
- Anchors substrate-product positioning ("known failure mode" + "known
  fix" = stronger story than "fix without theory")
- Could inform V3 substrate restructuring if needed

Per [[feedback-rehabilitation-after-rejection]]: drill the negative
even when rehabilitation works. Mechanism question still open after 2
attempts.

## Cost estimate

- 1-2 Research cycles (analytical only)
- 2-3x Sonnet-dispatched lit-scan agents
- Generic-math queries only

## Strategic significance

3rd-attempt mechanism diagnosis informed by:
- Structural insight from cycle 127 (tree-exact succeeds + loopy fails)
- Calibration discipline from cycle 126 (deflate P; top ≤ 0.50)
- Per cycle 124 user directive 2x-research-after-rejection (this is
  the 3rd drill applying the discipline)

If 3rd attempt also fails: substrate-physics question genuinely open;
honest framing stands. If succeeds: substrate-product positioning
gains theoretical anchor.

## What I need from you

Generic external lit scan + Pass 2 substrate drill. Expected delivery
1-2 cycles per recent patterns (15-30 min).

Per [[feedback-sessions-self-coordinate]]: file-routing only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
