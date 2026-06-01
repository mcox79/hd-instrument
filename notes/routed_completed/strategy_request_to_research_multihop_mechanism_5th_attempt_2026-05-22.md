# Strategy → Research: 5th-attempt mechanism diagnosis — cluster census smoke REFUTES cluster-trapping quantitative predictions

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-22 ~21:40 EDT
**Topic**: Cluster census Phase 1 smokes deliver MIXED validation; user-directed 2x discipline drill on new negatives
**cap_map state**: v135 (commit `650a9d3`)
**User directive**: "research 2x negative results" — per [[feedback-rehabilitation-after-rejection]] discipline applied to cluster-trapping quantitative refutation

## Context — 5th attempt warranted by user signal

Cycle 136 cluster census Phase 1 smokes (cycle 134 routing `40f9e1f` pickup):
delivered MIXED validation of cluster-trapping framework:
- **CONFIRMED at smoke**: forward chain trapping + W^L rank collapse
- **REFUTED at smoke**: specific cluster size (1 not ~5) + N-scaling (γ=0 not 0.73)

Per user signal, drilling the negatives for 5th-attempt mechanism diagnosis.

**Caveat per [[feedback-no-smoke]] + 15-anchor smoke→FULL precedent**: cluster
census FULLs are pending; smoke could overturn either direction. This 5th
attempt addresses the NEGATIVES at smoke; Research should integrate FULL
verdicts when they arrive.

## Track record (4 attempts; all refuted at empirical FULL)

| Cycle | Attempt | Predicted | Refuted by |
|-------|---------|-----------|------------|
| 123 | Signal eigenvalue near-degeneracy P=0.70 | spectral clustering | cycle 124 SPECTRAL_FLAT |
| 126 | Hubness × DPI P=0.45 | skew increases with N | cycle 127 skew DECREASES |
| 131 | HMM/BCJR cascade P=[0.55, 0.80] | soft > hard | cycle 132 soft = hard |
| 134 | Cluster trapping (cluster ~5; N^0.73) P=[0.55, 0.70] | cluster ~5, N^0.73 | cycle 136 cluster=1, γ=0 |
| 137 (THIS) | TBD | TBD | PENDING |

**This is the 5th attempt drill per user discipline application**.

## Updated empirical signature (cycle 136 cluster census smoke addendum)

The empirical signature for the 5th candidate mechanism is the 8-constraint
signature from cycle 134 ADDENDUM PLUS the new cluster census smoke findings:

**8 constraints from cycle 134 ADDENDUM** (substrate-physics structure):
1. 1-hop clean (acc_1hop=0.983 at N=65536 K=100)
2. ALL forward-only init methods fail at acc~0.20-0.25 floor
3. Soft = hard (no posterior representation gain)
4. Plateau at acc~0.20 for L=50,100
5. Loopy PERFECT given backward-warmstart
6. ALL backward-evidence init methods succeed PERFECT
7. Per-hop p_fail≈0.035; plateau ABOVE cascade (1-p)^50=0.168
8. VAMP N-universal; argmax non-monotonic in N

**3 NEW constraints from cycle 136 cluster census smoke**:
9. **Forward chain DETERMINISTIC at substrate**: cluster size = 1
   (500 chains from same true codeword → all 500 converge to same destination)
10. **W^L rank → 0 at L=50** (CONFIRMED): substrate W^50 has effectively
    zero rank at 1% eigenvalue threshold (rank(L=1)=100 → rank(L=50)=0)
11. **Cluster size N-INVARIANT** at smoke: cluster_per_N={4096:1, 8192:1};
    γ=0; cluster-trapping framework's N^0.73 scaling REFUTED

## What this NEW signature suggests

**Cluster-trapping framework is structurally WRONG** in 2 key ways:
- Predicted stochastic cluster of ~5 codewords; empirical is DETERMINISTIC
  single-codeword destination
- Predicted N^0.73 cluster growth; empirical is N-INVARIANT

**But structural insight HOLDS**:
- Forward trapping exists (cluster=1 IS trapping)
- W^L rank collapse exists (subspace collapse mechanism CONFIRMS)
- Backward rescue works (SMOOTHER_ONLY at FULL confirmed)

**The 5th candidate must explain**:
- Substrate W is a DETERMINISTIC operator with eigenvalue structure that
  collapses to rank-0 at L=50
- Each codeword has a deterministic destination under W^50
- The destination is DETERMINISTIC not stochastic (cluster=1 not ~5)
- Different codewords have different destinations (otherwise acc=0 or 1
  across queries; empirical is 0.217 = 22% of codewords are self-fixed)
- N-invariant trap structure (substrate's spectrum doesn't change with N
  in a way that affects trap size)
- Backward smoothing escapes via endpoint information

## Candidate framings to investigate (Research can add or replace)

1. **Single-dominant-eigenvalue forward collapse (SPECTRAL)**: substrate W
   has 1 dominant eigenvalue + 99 subdominant; at L=50 only dominant
   eigenvalue survives (rank → 1 effectively); argmax cleanup picks
   deterministic destination based on dominant eigenvector direction;
   ~22% of codewords self-aligned with dominant eigenvector

2. **W^L as deterministic projection to fixed-point subspace (PROJECTION)**:
   W^L → projection operator at large L; image is small set of fixed
   points; ~22% of codewords self-project; rest project to wrong
   fixed-points (deterministic destinations)

3. **Algebraic Kerdock fixed-point structure**: substrate's Kerdock 4-coset
   codebook has Z_4-linear coset arithmetic; W^L applied to codeword
   produces algebraic fixed-points by coset structure; deterministic
   destination determined by coset

4. **Hebbian W self-similarity at depth**: substrate's Hebbian outer-product
   W has self-similarity structure that produces fixed-points under
   iteration; deterministic destination determined by Hebbian eigenstructure

5. **Substrate is non-Markov deterministic dynamical system**: chain
   composition is NOT a Markov chain (stochastic); it's a deterministic
   dynamical system with attractor structure; cluster-trapping framework
   assumed stochastic and was wrong

6. **Self-dual codeword structure with fixed-point partition**: codewords
   pair up via substrate symmetry; ~22% are self-paired (fixed); rest
   map to partners

7. **Other deterministic-dynamical mechanism Research surfaces**

## What Research should produce

### Pass 1 — external lit-scan

Investigate mechanisms that produce:
- Deterministic forward collapse with single-codeword destination
- W^L rank collapse to 1-dim or 0-dim at L=50
- N-invariant trap structure
- Backward-smoothing rescue from endpoint

Avoid stochastic cluster-trapping framings (refuted at smoke). Focus on
DETERMINISTIC DYNAMICAL SYSTEMS literature, spectral collapse of iterated
operators, Z_4 algebraic Kerdock fixed-point structure.

### Pass 2 — substrate drill + final verdict

- Score top 3 candidates against 11-constraint signature (8 old + 3 new)
- Honest P range per [[feedback-lit-scan-calibration-penalty]] — 4-attempt
  refutation history = 80% miss rate; deflate P heavily
- If NO candidate fits: honest verdict substrate is genuinely beyond all
  published mechanism frameworks; 5 attempts refuted; substrate-physics
  characterization stands at "structurally constrained, mechanism unknown
  after 5 attempts"

### Critical falsification check (cheapest single test)

If Research identifies a candidate predicting specific W spectrum structure
(e.g., "1 dominant eigenvalue at substrate W; ratio λ_1/λ_2 > 5"), provide
falsifiable spectral prediction. Strategy can route a single eigenspectrum
check at substrate W (~5 min CPU).

## Cost estimate

- 1-2 Research cycles (analytical only; no GPU)
- 3 Sonnet-dispatched lit-scan agents (parallel) per [[feedback-subagent-model-optimization]]
- Generic-math queries per [[feedback-query-privacy-decomposition]]

## Substrate-product context

**Substrate-product Demo 1 capstone HOLDS regardless of mechanism diagnosis**:
- Cycle 130 Lane D E2E at N=65536 PASS (composed_acc=1.000)
- Cycle 135 backward-smoother-only operating envelope d=500/30% noise/N-universal
- Cycle 135 mega variants 5/5 V_PASS at FULL
- This research is for substrate-physics characterization gain, not blocking

## Critical caveat per [[feedback-no-smoke]]

**Cluster census FULLs pending**. Smoke could overturn:
- If FULL shows cluster size = 5 (matches cycle 134 ADDENDUM): cluster-trapping
  framework holds; this 5th routing becomes redundant
- If FULL shows cluster size = 1 (smoke confirms): substrate-physics characterization
  needs revision per this routing
- If FULL inconclusive: ambiguous evidence

Research should integrate cluster census FULL verdicts when they arrive
(check dashboard before delivering 5th-attempt note).

## Honest framing requested

Per [[feedback-no-smoke]] and 80% refutation track record:
- Maximum calibration discipline: cap P ≤ 0.50 for novel synthesis
- If no candidate convincingly fits, state plainly: substrate is novel
- 5 mechanism diagnoses refuted is itself substantive substrate-physics finding

This may be the LAST mechanism diagnosis attempt before honest "structurally
constrained, mechanism unknown" framing becomes the substrate-physics terminal
characterization.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 15-30 min per recent Research turnaround.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
