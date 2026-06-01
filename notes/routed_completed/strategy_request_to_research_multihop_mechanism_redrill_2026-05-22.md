# Strategy → Research: Multi-hop N=65536 mechanism re-diagnosis + revised rehabilitation after Resonator REFUTATION

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-22 ~19:15 EDT
**Topic**: Cycle 123 hypotheses BOTH refuted; need re-diagnosis
**cap_map state**: v124 (commit `6d66d71`)
**User directive**: "2x negative research right" — applying [[feedback-rehabilitation-after-rejection]] 2x discipline to cycle 124 negatives

## Context — both cycle 123 hypotheses refuted

Cycle 123 Research (multi-hop rehabilitation) delivered:
- **Agent G mechanism diagnosis P=0.70**: signal eigenvalue near-degeneracy at large N
- **Agent H top rehabilitation P=0.65**: Resonator Network per-hop iteration (Frady et al. 2020)

**Cycle 124 empirical results**:
- **Spectral validation smoke** = SPECTRAL_FLAT "Top-K eigenvalue span does NOT cluster as predicted. **Mechanism hypothesis falsified.**" Agent G P=0.70 hypothesis refuted at smoke (FULL pending but data clear).
- **Resonator FULL** = RESONATOR_INSUFFICIENT "acc_50hop=0.200 (<0.3) vs argmax baseline 0.250. **Research's rehabilitation hypothesis falsified; substrate-level restructuring needed.**" Agent H P=0.65 hypothesis hard-falsified at FULL; Resonator UNDERPERFORMS argmax.

**Both cycle 123 hypotheses (mechanism + top rehabilitation) refuted**.

Substrate's multi-hop K=100 N=65536 FULL acc_50hop=0.217 (cycle 121)
vs argmax baseline 0.250 (cycle 124) — chain composition genuinely
fails at N=65536 with unknown mechanism.

## Question for Research

**Generic-math framing** (per [[feedback-query-privacy-decomposition]]):

### Question 1 — Mechanism re-diagnosis

If neither standard cleanup cross-talk ((K-1)/N — falsified cycle 123)
nor signal eigenvalue near-degeneracy (cycle 123 Agent G — falsified
cycle 124) explains multi-hop chain composition degradation at large
N in classical-Hopfield-class associative memory systems with structured
codebooks, what OTHER mechanisms could explain:
- 1-hop retrieval clean (acc_1hop=0.983 at N=65536)
- Multi-hop chain degrades monotonically: 5→0.817, 10→0.567, 25→0.250, 50→0.217
- Plateau at acc_50hop=0.22 (not at random 1/K=0.01)
- 3.5× degradation N=4096→N=65536 at K=100 fixed

Specifically investigate:
- **Curse of dimensionality / volume concentration**: at large N, equally-distant points → ambiguity in argmax cleanup
- **Hub effects** in high-D similarity / nearest-neighbor structure (per Radovanović et al. 2010 hub effects in high dim)
- **Concentration of measure**: substrate's bipolar +/-1 codebook may concentrate at large N → less discriminable
- **Walk dynamics in absorbing-state Markov chain**: chain composition as random walk with structured transition matrix
- **Information-theoretic bound**: how much information CAN flow through 50-hop chain given substrate channel capacity?
- **Other mechanisms** Research can surface

### Question 2 — Revised rehabilitation candidates

Given:
- Resonator Network REFUTED (P=0.65 candidate — underperformed argmax)
- Cycle 123 remaining candidates: VAMP-on-chain P=0.55 + sparse cleanup P=0.50 + bidirectional P=0.45 + hierarchical P=0.35

Question: with NEW mechanism diagnosis (Question 1 outcome), which
rehabilitation candidate is most likely to succeed? Are there other
rehabilitation mechanisms NOT in cycle 123 list that should be
investigated?

Specifically:
- **VAMP-on-chain P=0.55** (cycle 123): forward-backward EP with
  soft marginals. Does NEW mechanism diagnosis support this approach?
- **Per-hop sparse cleanup P=0.50**: threshold-AMP before next hop.
  Does substrate at α=0.124 + Kerdock have sparse-cleanup-amenable
  structure?
- **Codebook-level rehabilitation**: substrate currently uses Kerdock
  4-coset. Would different codebook (Reed-Muller higher-order? ETF?
  sparse? balanced?) help chain composition?
- **Substrate-level restructuring** (per Resonator verdict_msg): if
  no per-hop mechanism works, what substrate-level changes could
  restore deep-chain composition at N=65536?

### Question 3 — V3 substrate investigation trigger evaluation

Per cycle 115 V3-investigation trigger logic:
- Substrate's multi-hop chain at N=65536 may be fundamentally limited
- If ALL rehabilitation candidates from cycle 123 fail, substrate-level
  restructuring (V3) becomes warranted
- Cycle 124 Resonator REFUTED is 1 of 5 candidates ruled out — 4 remain

Question: based on revised mechanism diagnosis, can Research predict
which rehabilitation candidates are MORE LIKELY to share Resonator's
failure mode (and thus also fail), vs which work via fundamentally
different mechanism?

## What Research should produce

**Pass 1 (external lit-scan)**:
- Multi-hop chain composition + N-scaling literature (beyond cycle 123
  agents G+H surveyed; surface adjacent methods per
  [[feedback-dont-dismiss-adjacent-methods]])
- Curse of dimensionality / hub effects in high-D classical AM
- Information-theoretic chain capacity bounds
- VAMP / EP / iterative-inference chain composition specifically
- Codebook-level rehabilitation for chain composition

**Pass 2 (substrate drill)**:
- Revised mechanism diagnosis with cycle 124 falsifications integrated
- Which of cycle 123 remaining 4 rehabilitation candidates most likely
  succeeds vs likely also fails
- Other rehabilitation mechanisms not in cycle 123 list
- V3 substrate investigation trigger evaluation: if rehabilitation
  list exhausted, what substrate-level changes warrant testing?

## Cost estimate

- 1-2 Research cycles (analytical only; no GPU)
- 2-3x Sonnet-dispatched lit-scan agents per [[feedback-subagent-model-optimization]]
- Generic-math queries only per [[feedback-query-privacy-decomposition]]

## Strategic significance

This is the 2x-research-after-rejection drill (cycle 123 first; cycle
125 second). Per Strategy session pattern at cycle 93 → cycle 100:
first Research delivery's mechanism diagnosis can be wrong; second
delivery often refines with new evidence.

Substrate-product implications:
- Demo 1 Lane D agent memory SDK depends on multi-hop chain at N=65536
  resolving
- Bet Y V2.D N=65536 substrate-product scope depends on rehabilitation
  succeeding
- V3 trigger discussion (cycle 115) becomes substantive if rehabilitation
  list exhausts

Per [[feedback-no-smoke]]: both cycle 123 hypotheses refuted is
substantive empirical evidence requiring re-diagnosis, not denial.

## What I need from you

Generic external lit scan + Pass 2 substrate drill. Expected delivery
1-2 cycles (~15-30 min per recent patterns).

Per [[feedback-sessions-self-coordinate]]: file-routing only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
