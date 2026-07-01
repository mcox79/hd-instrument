# Partition-Oracle Recovery Mechanism — Honest Reframing of Extreme-Depth "Over-Performance"

**Filed:** 2026-07-01 late-session
**Trigger:** Research drill on Atom 11 over-performance revealed the mechanism is partition-oracle-specific, NOT a semantic reasoning win

## The Correction

**Prior framing (INCORRECT):** substrate multi-hop over-performs Atom 11's per-hop 0.985 prediction → substrate can do 500-hop reasoning at commercial scale → 10x deeper than LLMs.

**Actual mechanism (Mechanism G, P_deflated 0.88):** partition-oracle test routes every hop to the TRUE target partition using ground-truth `target_o`, independent of predicted state. This creates a non-zero recovery probability `r=0.006` after errors, producing a Markov floor at `q* = r/(1-p+r) = 0.286` rather than exponential-to-zero.

## Correct Model

- **Product model (WRONG):** q_d = p^d — assumes r=0
- **Markov model (CORRECT for oracle chains):** q_d = r + (p-r)·q_{d-1}, floor at q* = r/(1-p+r)

Fitted values at N=8192, V_C=200, PART_SIZE=10:
- p = 0.985 (matches Atom 11 cross-landing average)
- r = 0.006 (from d=5-15 full-run fit)
- q* = 0.286 (Markov floor)

Wave 22 observations (d=200=0.640, d=500=0.360) are well within Markov predictions given oracle routing.

## Does NOT Transfer to Semantic Chains

Without oracle routing (real reasoning):
- r → 0 (wrong state produces random-direction W query)
- Chain accuracy → 0 exponentially at rate p
- At p=0.985: d=80 → 0.30, d=500 → 0.0006

**Atom 11's original prediction was correct for non-oracle chains.**

## What DOES Transfer

- Structured chains with routing (tool chains, database traversal, pipelines with known structure): substrate 500-hop viable
- Cost advantage per hop (10^4x cheaper than LLM): holds regardless
- Determinism + interpretability: holds regardless
- **NOT: 10x-deeper semantic reasoning claim**

## Real M3 Research Question

Can substrate-native routing (M1.6 successor / RC1/RC2/RC3 candidates) achieve r > 0 WITHOUT an oracle? Even r=0.003 (half oracle value) gives floor ~0.15 for 500-hop structured chains.

This is the actual Stage 4 substrate-language question.

## Skunkworks VET Guidance for Wave 22 (when landed)

Do NOT tier Wave 22 as "substrate over-performs Atom 11." Correct tier: Markov model with r=0.006 fits observed within noise → **partition-oracle-recovery finding**, not per-hop accuracy revision.

Atom 11 stays valid for non-oracle chains. New atom candidate: partition-oracle-recovery mechanism at r=0.006 → substrate physics finding at STRUCTURED chain regime.

## Cross-references

- Atom 11 MM_STANDARD (per-step scale-invariance)
- Wave 22 FULL landing (pending)
- Research drill 2026-07-01 late session
- Kanerva SDM literature (r>0 recovery in clustered SDM is well-established)
- Romani-Amit 2006 attractor depth literature
- Gayler 2003 VSA composition depth (sqrt(N) decay in unconstrained space)

## Discipline Note

Test structure REGULARITY was flagged earlier as a caveat but not enforced when framing extreme-depth results to USER. Future extreme-depth findings must explicitly identify:
1. Is the test structure oracle-routed (Wave 22 style)?
2. Is r > 0 by construction?
3. Does the mechanism translate to open-ended semantic content?
