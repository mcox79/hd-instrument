# Strategy → Research: K-RESONANCE structure in classical-Hopfield-class with structured codebook — substrate-novel finding

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-23 ~06:50 EDT
**Topic**: K=1000 FIXED POINTS anomaly + cycle period scales with K — what published frameworks explain K-resonance?
**cap_map state**: v143 (commit `c30d48f`)
**Trigger**: User signal "research needs research guidance"; cycle 159 K-sweep FULL revealed substrate-novel K-RESONANCE structure

## Context

Cycle 159 limit cycle K-sweep FULL revealed substrate-novel substrate-physics
behavior:

| K | Median cycle period |
|---|---|
| 100 | 3 (cycle) |
| 500 | 12 (cycle) |
| **1000** | **1 (FIXED POINTS — anomaly)** |
| 5000 | 42 (cycle) |

**Substrate has K-RESONANCE structure** — specific K values produce qualitatively
different substrate dynamics (cycles vs fixed points).

This is a substantive substrate-physics observation NOT covered by the 5 prior
mechanism attempts (eigenvalue near-degeneracy + Hubness × DPI + HMM/BCJR +
cluster trapping + RETRACTION — all refuted at FULL).

**Substrate-physics characterization v143**:
> "Substrate W^L produces LIMIT CYCLES at depth with **N-invariant +
> K-SCALES + K-RESONANCE** signature. Different K values produce qualitatively
> different dynamics (cycles vs fixed points). Substrate W has K-specific
> algebraic structure connecting Kerdock codebook properties to cycle period."

## Question for Research

What published literature explains K-RESONANCE behavior in classical-Hopfield-class
associative memory with structured (Kerdock 4-coset) codebook at large N?

Specifically:
1. **K-resonance / commensurability in iterated linear systems**: do specific
   K values produce qualitatively different dynamics under Wx → argmax → x'
   iteration?
2. **Kerdock 4-coset algebraic structure**: is K=1000 a special algebraic
   value relative to Kerdock codebook construction? (Kerdock 4-coset has
   |C| = 2^(2m+2) at N=2^(2m+2); for N=65536 = 2^16 → m=7 → |C|=512 base
   Reed-Muller code? Or different)
3. **Period-1 fixed points in iterated argmax-cleanup systems**: what
   algebraic conditions produce fixed points rather than cycles?
4. **K-scaling cycle period**: substrate observes period ~K/30 at large K;
   what theoretical framework predicts this scaling?

## Substrate empirical observations to integrate

Cycle 159 FULL data:
- N-invariant cycles (median 2-5 across N=4096-65536)
- K-scaling: K=100→3, K=500→12, K=5000→42 (period ~K/30)
- K=1000 anomaly: FIXED POINTS (period 1)
- Substrate codebook: Kerdock 4-coset, K stored patterns out of |C|

Prior empirical findings (cycle 145):
- 100% codewords enter cycles at K=100
- 54% with period [2, 100]
- ENDPOINT_COLLAPSED 28/100 distinct endpoints at K=100

## Candidate framings to investigate

1. **Algebraic Kerdock RM(1,m) subcode resonance**: at K = |RM(1,m)| substrate
   has fixed points; other K values produce cycles. Cycle 137 5th-attempt
   Research mentioned RM(1,m) subcode as Agent S sub-hypothesis (P=0.30).

2. **Z_4-linear coset arithmetic**: Kerdock 4-coset Z_4 coset structure could
   produce K-dependent algebraic invariants. K=1000 specific resonance.

3. **Commensurability in iterated affine maps**: K specific values align with
   substrate W eigenstructure to produce fixed points.

4. **Chaos theory / Sharkovsky theorem**: period-1 → period-2 → period-3 cycles
   in iterated maps follow Sharkovsky ordering. K-resonance could reflect
   ordering structure.

5. **Random matrix product Lyapunov spectrum with structured codebook**:
   substrate's W has structured eigenstructure where K=1000 aligns with
   dominant eigenvalue.

6. **Other substrate-specific mechanisms Research surfaces**

## Calibration discipline

Per [[feedback-lit-scan-calibration-penalty]]: 5 prior mechanism attempts
refuted (80% refutation rate). Cap P at 0.50. Honest "no fit" verdict acceptable.

**This is NOT a 6th-attempt mechanism diagnosis** in the same sense as cycles
123-141. It's a NEW substrate-physics observation (K-RESONANCE) that emerged
from cycle 159 K-sweep FULL. Research's task is to characterize/explain
the K-RESONANCE structure, not to propose another mechanism for the original
"forward fails + backward works" puzzle.

## What Research should produce

### Pass 1 — external lit-scan
- K-resonance in iterated argmax-cleanup classical-Hopfield-class systems
- Kerdock 4-coset Z_4 algebraic structure (RM(1,m) subcode size at substrate N)
- Period-1 vs period-N cycles in iterated maps
- Random matrix product Lyapunov spectrum with structured codebook

### Pass 2 — substrate drill
- Predict K-resonance values for substrate's specific Kerdock construction
- Falsifiable empirical predictions (does K=512 or K=2048 show fixed points?)
- Connection to substrate-product positioning (K-resonance affects K-ceiling
  characterization)

## Cost estimate

- 1 Research cycle (analytical only; no GPU)
- 2-3 Sonnet-dispatched lit-scan agents per [[feedback-subagent-model-optimization]]
- Generic-math queries per [[feedback-query-privacy-decomposition]]

## Substrate-product context

Substrate-product Demo 1 + Demo 2 + N=262K + 240 envelope cells HOLD at v141
level. K-RESONANCE characterization is for substrate-physics narrative gain,
not substrate-product blocking.

If K-resonance pattern identified → substrate-product positioning gains
theoretical anchor: "substrate has K-specific algebraic structure connecting
Kerdock codebook properties to cycle period; specific K values produce
substrate-novel fixed-point behavior."

If K-resonance unique to K=1000 only → substrate-physics characterization
incrementally updated; K=1000 noted as substrate-specific algebraic alignment.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 15-30 min per recent Research turnaround.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
