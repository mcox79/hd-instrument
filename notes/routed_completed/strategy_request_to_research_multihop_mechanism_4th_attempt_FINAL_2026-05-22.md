# Strategy → Research: Multi-hop N=65536 mechanism 4th-attempt diagnosis — FINAL run

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-22 ~21:15 EDT
**Topic**: 4th-attempt mechanism diagnosis — TIGHT structural constraint stack from cycle 132 HMM/BCJR refutation
**cap_map state**: v131 (commit `0b013f9`)
**User directive**: "research is free - maybe this is the final run"; 4th drill applying [[feedback-rehabilitation-after-rejection]] 2x discipline (3 attempts already done)

## Context — 4 mechanism diagnoses refuted; structural constraint stack tightened

This is the **4th and likely final attempt** at substrate-physics mechanism
diagnosis for multi-hop N=65536 chain degradation. If this attempt also fails,
substrate is in genuinely unprecedented regime and substrate-physics
characterization stands at "structurally constrained, mechanism unknown".

**Track record of 4 refuted attempts**:

| Attempt | Cycle | Mechanism | Predicted | Actual | Refuted by |
|---------|-------|-----------|-----------|--------|------------|
| 1 | 123 | Signal eigenvalue near-degeneracy P=0.70 | spectral clustering of K signal eigvals | SPECTRAL_FLAT no clustering | cycle 124 |
| 2 | 126 | Hubness × DPI information contraction P=0.45 | skew increases with N | skew DECREASES with N | cycle 127 |
| 3 | 131 | HMM/BCJR cascade with hard-quantization P=[0.55, 0.80] | soft > hard (acc_B ∈ [0.5, 0.95]) | soft = hard (no information gain) | cycle 132 |
| baseline | 123 | Standard cleanup cross-talk (K-1)/N | decreases with N | substrate shows 3.5× DEGRADATION at large N | cycle 123 |

**4 frameworks tried + all refuted** = substrate empirically does NOT match
published chain-composition mechanism frameworks. Per [[feedback-no-smoke]]:
substrate is in unprecedented territory.

## The question — find 5th candidate OR conclude "structurally novel"

What single mechanism explains ALL of these phenomenological constraints
simultaneously in classical-Hopfield-class associative memory with structured
codebook at large N?

### Constraint stack (all must hold simultaneously)

1. **1-hop clean**: acc_1hop=0.983 at N=65536 K=100 — per-hop retrieval works
2. **Forward-only fails**: hard argmax acc_50hop=0.25; chain composition degrades
3. **Soft posterior provides NO benefit over hard** (cycle 132): soft=0.217 ≈ hard=0.250 — information loss is NOT from quantization
4. **Plateau at acc~0.20 for L=50,100** (cycle 132): not random 1/K=0.01; not geometric decay; substrate hits a confused-attractor subspace at depth >50 and stays there
5. **Loopy within-hop fails WORSE than argmax** (cycle 127): Resonator + Sparse + Bidirectional all 0.20-0.225 < argmax 0.25 — iterative correction is harmful
6. **Backward smoothing recovers PERFECT** (cycle 127): VAMP-on-chain forward-backward EP acc=1.000 — information IS available cross-hop just not extractable forward-only
7. **N-dependent at fixed K**: N=4096 K=100 works (acc_50hop=0.767); N=65536 K=100 fails (acc_50hop=0.217); 3.5× degradation at same K

### What's already eliminated

- **Per-hop posterior quantization loss** (HMM cascade) — refuted by soft=hard
- **Per-pattern cross-talk (K-1)/N** — refuted by direction (should decrease with N)
- **Eigenvalue near-degeneracy** — refuted by SPECTRAL_FLAT
- **Hubness near-absorbing states** — refuted by skew decreasing with N
- **Memoryless Markov DPI cascade** — refuted by plateau (not geometric decay)
- **Cycle-induced fixed-point** (loopy BP) — refuted by loopy fails MORE than argmax
- **Within-hop refinement** (any kind) — refuted by no-soft-gain + loopy fails

### What structurally must be true

The information that's lost forward-only but recoverable via backward smoothing
must be:
- NOT in the per-hop posterior (else soft would help)
- NOT in iterative within-hop correction (else loopy would help)
- ONLY in **cross-hop backward information flow** — the END of the chain
  observably constrains the BEGINNING in a way that forward propagation cannot

This is unusual structurally. In standard HMM/BCJR, the forward-backward
advantage comes from posterior representation. Here it doesn't. The
substrate-specific mechanism must produce a CHAIN-LEVEL structural
constraint that forward cannot resolve but backward can.

## Candidate framings to investigate (Research can add or replace)

These are seed hypotheses with the constraint signature; Research should
treat as suggestive not exhaustive:

1. **Subspace collapse in W^L at depth** — substrate's W applied L times
   produces a low-rank or degenerate subspace where multiple codewords
   become indistinguishable; forward-only sees superposition; backward
   smoothing observes end-point and constrains backward through the
   degenerate subspace. Investigate W^L spectral structure at growing L.

2. **Coherent (non-iid) error correlation across hops** — per-hop errors
   are CORRELATED via shared substrate structure (Kerdock codebook
   algebraic relations? Hebbian W self-similarity at depth?); forward
   marginalization over correlated errors fails because errors are not
   independent samples; backward smoothing observes downstream error
   pattern, infers correct error correlation backward.

3. **Substrate W^L grows null space at depth** — null space of W^L grows
   with L; forward-only loses dimensions into null space; backward
   smoothing observes downstream output (not in null space) and infers
   the part of input that was projected away.

4. **Algebraic mode mixing specific to Kerdock 4-coset codebook** — Z_4-linear
   coset phase structure (cycle 115 Kerdock RI universality leaning NO)
   introduces deterministic mode mixing at depth that pure-iid noise
   models miss; backward smoothing leverages algebraic structure to
   decode.

5. **Non-Markov chain structure** — substrate's chain composition is NOT
   a Markov chain (higher-order dependencies via W's Hebbian self-similarity);
   HMM/BCJR assumes Markov property; if non-Markov, forward marginalization
   is incorrect; backward smoothing might still work if it observes
   sufficient downstream evidence.

6. **Attractor-manifold collapse** — at depth >50, chain enters a small
   attractor manifold containing the correct codeword + ~5 confusable
   codewords (explains 0.20 plateau = ~1/5); forward cannot escape
   manifold; backward smoothing observes end-point outside manifold,
   identifies which manifold member is correct.

7. **Substrate operates in non-equilibrium / aging regime at depth** —
   substrate's RSB-capable soft-mode structure (cycle 119/121/122) implies
   non-equilibrium dynamics at certain depths; forward chains drift into
   aging-regime where standard ergodic statistics fail; backward smoothing
   exploits violations of detailed balance to decode.

8. **Other substrate-specific mechanism Research surfaces** that fits
   the 7-constraint signature

## What Research should produce

### Pass 1 — external lit-scan
- Subspace collapse / W^L spectral structure at large L
- Coherent error correlation in iterated linear/quasi-linear maps
- Non-Markov chain composition with cross-hop constraints
- Algebraic Kerdock/Reed-Muller depth-mode interaction
- Attractor manifold collapse in large-N classical AM
- RSB / aging-regime chain composition
- Other mechanism families that fit the structural constraint

### Pass 2 — substrate drill + final verdict
- For each top 3-5 candidate mechanism, score against ALL 7 constraints
  (per cycle 126 calibration: deflate P 0.15-0.25; top P ≤ 0.50)
- If NO candidate fits all 7 constraints → honest verdict: substrate-physics
  characterization stands at "structurally constrained, mechanism unknown
  after 4 attempts; substrate empirically beyond all published frameworks"
- If a candidate fits all 7 constraints → falsifiable predictions for Phase 1
  empirical validation (cheap discriminator like cycle 131 Test 1 structure)

## Cost estimate

- 1-2 Research cycles (analytical only; no GPU)
- 3-4 Sonnet-dispatched lit-scan agents (parallel)
- Generic-math queries only per [[feedback-query-privacy-decomposition]]

## Substrate-product context (Research should know)

**Substrate-product roadmap is NOT BLOCKED by this question**:
- Demo 1 Lane D capstone DEMONSTRATED at FULL (cycle 130 commit `a382833`)
- VAMP-on-chain operating envelope K=5000+d=200+noise-robust (cycle 128)
- Substrate-product positioning at N=65536 = production-viable via VAMP-on-chain

This 4th-attempt research is for **substrate-physics characterization gain**,
not substrate-product unblocking. If mechanism remains unknown, substrate-product
story still holds with honest "structurally constrained, mechanism open question"
framing.

## Honest assessment requested per [[feedback-no-smoke]]

If Research's 5th candidate has lit-scan precedent that fits all 7 constraints
with empirical-numeric grounding (like cycle 131 HMM 0.97^50 ≈ 0.22), 
proceed with falsifiable predictions.

If Research's best 5th candidate is speculative or doesn't fit all 7
constraints, **state plainly**: substrate is in unprecedented regime;
4 mechanism diagnoses refuted; mechanism question genuinely open;
substrate-product Demo 1 capstone holds regardless. Honest negative is
substantive — substrate-physics finding is "substrate empirically does NOT
match any published chain-composition framework after 4 attempts".

## Per [[feedback-rehabilitation-after-rejection]] 2x discipline + user signal

User signal: "research is free - maybe this is the final run". 4th-attempt
applies discipline 4 times across cycles 123/125/128/131. After this attempt:

- If 5th candidate identified + validates at Phase 1: substrate-physics
  characterization gains theoretical anchor
- If 5th candidate identified + refutes at Phase 1: 5 mechanisms refuted;
  substrate is genuinely novel; final answer
- If no 5th candidate emerges: substrate-physics characterization stands
  at "structurally constrained mechanism unknown" — final answer

In all cases, this is the **last drill of the 2x-research-after-rejection
discipline on this question**. Substrate-product roadmap continues regardless.

## What I need from you

Generic external lit scan + Pass 2 substrate drill with the tightened
7-constraint signature. Expected delivery 1-2 cycles per recent patterns
(~15-30 min).

Per [[feedback-sessions-self-coordinate]]: file-routing only.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
