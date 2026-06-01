# Strategy → Research: Multi-hop chain reasoning rehabilitation at N=65536

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-22 ~18:55 EDT
**Topic**: Multi-hop K=100 at N=65536 FULL KILLED — apply [[feedback-rehabilitation-after-rejection]] 2x-research discipline
**cap_map state**: v121 (commit `accce42`)
**User directive**: "remember to research negative results 2x"

## Context — negative result

`wave14_multihop_K100_N65536_v1` FULL (cycle 121) = **MULTIHOP_N65K_KILLED**:
- acc_50hop = **0.217** < 0.4 threshold
- per_depth: 1→0.983, 5→0.817, 10→0.567, 25→0.250, 50→0.217

**Comparison**:
- N=4096 K=100 FULL (cycle 96 NEW HIGH): acc_50hop = 0.767
- N=65536 K=100 FULL (cycle 121): acc_50hop = 0.217
- **3.5× degradation** at N=65536

**1-hop retrieval works fine** at N=65536 (acc_1hop=0.983) — chain
composition degrades, not single-hop retrieval.

**Cycle 117 smoke 0.100 → cycle 121 FULL 0.217**: 8th smoke→FULL
divergence in IMPROVEMENT direction but still below 0.4 threshold.
Pattern is genuine.

## Question for Research

**Generic-math framing** (per [[feedback-query-privacy-decomposition]]):

In structured-codebook Hopfield-class associative memory systems with
high N (∼65K), what mechanisms cause multi-hop chain composition
accuracy to degrade with depth, and what rehabilitation paths exist?

Specifically:

1. **Mechanism diagnosis** — why does multi-hop chain composition
   degrade at large N when single-hop retrieval is clean?
   - Cleanup cross-talk accumulation per hop?
   - Error compounding (per cycle 96 K=100 N=4096 per-hop retention
     0.9947 = 0.53% per-hop loss; at N=65536 implied per-hop retention
     ≈ 0.95-0.96 from acc_50=0.217)
   - Substrate's RS-phase + RSB-capable W structure creating
     "memory leakage" between hops at high N?
   - Random walk arguments: chain composition = random walk in
     substrate-vector space; at large N more dilute?

2. **Known rehabilitation mechanisms** for multi-hop / chain composition
   at large N in classical-Hopfield-class systems:
   - Per-hop β scaling (different β per retrieval/binding/cleanup step)?
   - Sparse cleanup intermediate (filter low-confidence states between hops)?
   - Hybrid binding mechanism (different binding at different chain depths)?
   - Layered substrate (sparse top + dense bottom; per cycle 93 addendum)?
   - Iterative cleanup vs single-shot cleanup (per Resonator Networks
     Frady-Kent-Sommer 2020)?

3. **VAMP-based chain composition** (per cycle 120 substrate-novel
   readout):
   - Does VAMP with cached SVD enable iterative chain composition that
     scales with N?
   - State Evolution applied at chain depth — would aggregate posterior
     over depth-50 chains preserve information?

4. **N-scaling literature for chain composition specifically**:
   - HRR / VSA chain inversion (Plate 1995 / Kleyko 2022) at large N
   - Modern Hopfield chain composition (Demircigil 2017 / Krotov-Hopfield 2020)
   - Recent (2024-2026) results on chain composition + N-scaling

## What Research should produce

**Pass 1 (external lit-scan)**:
- Multi-hop chain composition + N-scaling literature
- Cleanup cross-talk accumulation analysis
- Hopfield-class chain inversion mechanisms at large N
- VAMP / iterative inference applied to chain composition

**Pass 2 (substrate drill)**:
- Why does substrate at N=65536 K=100 give acc_50hop=0.217 vs N=4096
  acc_50hop=0.767?
- 3-5 rescue mechanism candidates with substrate-applicability scoring
- Predicted acc_50hop at N=65536 for each candidate
- Cheapest empirical test path

## Expected output

Research note with:
- Mechanism diagnosis for multi-hop N=65536 degradation
- 3-5 rehabilitation mechanism candidates ranked by P(ships)
- Connection to cycle 121 FULL data (per_depth curve) + cycle 96
  N=4096 baseline (0.767)
- Substrate-product implications for Bet Y V2.D N=65536 multi-hop
  capability

## Per [[feedback-no-smoke]] + [[feedback-rehabilitation-after-rejection]]

Per user directive "research negative results 2x": this multi-hop
N=65536 KILL is the cycle 121 primary negative. Applying 2x discipline.

Per cycle 93 addendum rescue list framework: K-scaling + partial bipolar
relaxation + layered substrate are remaining Bet Y V2.D rescue paths;
multi-hop chain rehabilitation may overlap with these.

Per [[feedback-value-creation-not-competition]]: substrate-product
positioning is currently "1-hop excellent K≤500 + multi-hop bounded at
N=65536". Rehabilitation could extend Lane D agent memory SDK Demo 1
positioning back to deep-chain reasoning at N=65536 if substrate-novel
mechanism identified.

## Cost estimate

- 1-2 Research cycles (analytical only; no GPU)
- 2x Sonnet-dispatched lit-scan agents per [[feedback-subagent-model-optimization]]
- Generic-math queries only per [[feedback-query-privacy-decomposition]]

## What I need from you

Generic external lit scan + Pass 2 substrate drill. Expected delivery
1-2 cycles per recent patterns (~15-30 min).

Per [[feedback-sessions-self-coordinate]]: file-routing only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
