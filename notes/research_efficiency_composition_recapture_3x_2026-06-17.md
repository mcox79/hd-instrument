# Research: efficiency-composition RECAPTURE (3x deep drill)

Date: 2026-06-17
Trigger: substrate empirical MIDDLE sub-multiplicative 16x verdict on efficiency-composition cell
Drill mode: 3-angle parallel lit-scan + Opus synthesis
Calibration penalty applied: P estimates deflated 0.15-0.25; novel-synthesis cap 0.50

## (a) HEADLINE

True multiplicative k^d compositional scaling is provably UNREACHABLE in any
fixed-width VSA without paying N^d storage (Smolensky tensor-product result).
What look like "multiplicative" recaptures in the VSA literature are one of three
distinct mechanisms: (1) UNITARY binding operators that prevent variance
amplification so the linear-in-N capacity slope is FULL not partial (Gosmann-
Eliasmith 2019; Plate unitary HRR); (2) RESONATOR / factorizer decoders that
make a linear-capacity vector ADDRESS a multiplicative k^f composite SPACE in
near-linear time (Frady-Kent-Sommer 2020; Hersche GSBC 2023-2025); (3) DENSE /
MODERN HOPFIELD energies whose order-n polynomial buys D^(n-1) capacity from
nonlinearity (Krotov-Hopfield 2016; Ramsauer 2020). The MIDDLE sub-multiplicative
16x verdict is most consistent with a UNITARITY DEFICIT plus DECODER-CEILING
combination - the current operator is not fully unitary, and the decoder is not
exploiting resonator-style superposition search. Both are addressable.

## (b) Cheap decisive test

Run a 3-arm bake-off on the existing efficiency-composition cell, NO new
substrate atoms required, all arms reuse cell harness with operator-swap only:

- ARM A (unitarity recapture): swap current binder for a unitary projection
  (Plate complex-magnitude or Gosmann VTB). Holds N fixed. Predicts capacity
  slope at full linear-in-N (not the partial slope of vanilla circular conv).
- ARM B (resonator decoder recapture): keep current binder, swap decoder for
  resonator dynamics (Kent-Frady 2020 Eq. 4-6 iterative codebook projection).
  Predicts addressable composite space k^f at O(f*k) decode cost vs current
  O(k^f) brute search. Holds storage fixed.
- ARM C (sparse block-code recapture): swap to GSBC (Hersche 2023) sparse
  binding plus stochastic factorizer. Predicts multiplicative addressable
  reach AND lower decode latency than ARM B.

Cell decisive metric: ratio observed_capacity / theoretical_multiplicative on
held-out composition depths d=2,3,4. Pre-register the 3-arm bake-off as a
single composition-recapture exp_dev anchor.

## (c) Falsifiable predictions

HARD-PASS thresholds (recapture confirmed):
- ARM A: capacity slope >= 0.85 * linear-in-N theoretical at d=2; sub-mult
  factor closes to <= 4x (currently 16x).
- ARM B: factorization success rate >= 0.80 at f=3, k=N^(1/3); decode latency
  scales as O(f*k) not O(k^f).
- ARM C: GSBC matches ARM B success at >= 2x faster wall-clock; sparsity
  preserved across iterated binding (>= 3 depths).

HARD-FAIL thresholds (recapture DEAD, sub-mult ceiling intrinsic):
- ARM A: capacity slope <= 0.60 of linear-in-N theoretical -> binder is NOT
  the bottleneck.
- ARM B: factorization success rate <= 0.50 at f=3 -> decoder dynamics do
  not recover multiplicative reach in this codebook regime.
- ARM C: sparsity collapses (density grows linearly with depth) -> sparse
  binding does not iterate stably.
- ALL THREE arms fail HARD -> sub-multiplicative scaling is NOT a
  unitarity/decoder/sparsity artifact; it is INTRINSIC to the substrate's
  same-space binding choice, and the only recapture path remaining is
  Smolensky-style unreduced tensor product (storage-prohibitive) OR Dense-
  Hopfield-style order-n energy (architectural pivot, not operator swap).

## (d) Cross-thread synthesis

This drill resolves the open question from research_composition_operators_5x
(2026-06-08) and exp_dev_handoff_research_composition_cascade_closure
(2026-06-07): the cascade-closure was NOT a generic dead-end. It was an
operator-level ceiling at the binder+decoder layer that the 5x drill did not
distinguish from a substrate-architectural limit. The new 3x evidence
DISTINGUISHES the two cases via the 3-arm bake-off.

Composes with the field-coverage advisory:
- modern-hopfield Tier-1 fruit-bearing -> ARM B/C of bake-off opens a future
  Dense-Hopfield drill if ALL ARMS HARD-FAIL (architectural pivot path).
- sparse-coding-compressed-sensing Tier-1b new field -> GSBC arm directly
  exercises this field (first drill on sparse-block-code substrate use).
- spin-glass / RSB -> resonator dynamics map cleanly onto replica-symmetric
  fixed-point analysis (Frady-Sommer 2020 Sec. 4); if ARM B HARD-PASSes, a
  follow-up RSB drill would tighten the f,k upper bound.

Per [[feedback-dont-dismiss-adjacent-methods]]: the modern-Hopfield arm was
deliberately NOT pre-dismissed despite the cascade-closure framing - it is
mathematically adjacent (energy-function generalization of HRR cleanup
memory) and gets its own ARM C-prime if A/B/C are inconclusive.

## (e) Substrate-product implications

The MIDDLE sub-multiplicative 16x verdict is currently being read as a
PARTIAL win on composition. The lit-scan reframes this honestly:

- Method-contingent framing (per USER-LOCKED rule on measured bounds): the
  16x is "envelope OF THIS METHOD/CONFIG (current binder + current decoder +
  current sparsity), NOT fundamental". Extension via unitary projection,
  resonator decoder, or sparse block coding is UNTESTED on this substrate.
- Product positioning: do not claim "compositional efficiency" as a substrate
  win until ARM A/B/C bake-off lands. The current cell reading SUPPORTS a
  qualified claim ("composition works at sub-mult ceiling under fixed
  operator class") but DOES NOT support a "multiplicative composition"
  claim.
- If ARM B/C HARD-PASS, the substrate gains a genuinely novel
  capability-class anchor: linear-capacity vectors addressing a k^f
  composite space via resonator/factorizer decode - this would be a
  cap_map green and a product differentiator vs vanilla seq2seq baselines
  (which empirically scale sub-mult per Lake-Baroni SCAN and Dziri 2023).

Calibrated probabilities (deflation applied):
- P(ARM A HARD-PASS) = 0.45 (lit precedent is strong for unitarity benefit
  but slope-recapture depth is uncharted for this substrate)
- P(ARM B HARD-PASS) = 0.40 (Kent-Frady 2020 direct precedent but resonator
  convergence regime is codebook-distribution-dependent)
- P(ARM C HARD-PASS) = 0.35 (Hersche 2023 strong but sparse-block-code is
  the most distant operator class from current substrate)
- P(at least one HARD-PASS) = 0.65
- P(all three HARD-FAIL, intrinsic ceiling) = 0.20

## (f) Citations (verified count: 18)

Foundational:
- Smolensky 1990 "Tensor Product Variable Binding", Artificial Intelligence
- Plate 1995 "Holographic Reduced Representations", IEEE TNN
- Plate 2003 HRR book
- Kanerva 2009 "Hyperdimensional Computing", Cognitive Computation
- Gayler 2003 MAP "Jackal of all trades"

Capacity theory:
- Frady, Kleyko, Sommer 2018 "Theory of Sequence Indexing" (arXiv 1803.00412)
- Frady, Sommer 2020 robust HD computation
- Schlegel, Neubert, Protzel 2022 VSA comparison (arXiv 2001.11797)
- Kleyko et al. 2022 HDC/VSA Survey (arXiv 2111.06077)
- Demidovskij et al. 2024 VSA capacity (arXiv 2301.10352)
- Gallant, Okaywe 2013 MBAT, Neural Computation

Operator improvements / ceiling-lifting:
- Gosmann, Eliasmith 2019 Vector-derived Transformation Binding (FHRR-style)
- Kent, Frady, Sommer, Olshausen 2020 Resonator Networks II
- Frady, Kent, Olshausen, Sommer 2020 Resonator Networks I
- Laiho et al. 2015 sparse high-dim binding
- Hersche et al. 2023-2025 GSBC sparse block-code factorizers

Compositional gap (anti-multiplicative empirics):
- Lake, Baroni 2017 SCAN
- Dziri et al. 2023 "Faith and Fate" (arXiv 2305.18654)

## Next-drill candidate

If ARM B HARD-PASS: dispatch RSB / cavity-method drill on resonator
fixed-point capacity (spin-glass Tier-1 fruit-bearing, adjacency anchor
established).

If ALL ARMS HARD-FAIL: dispatch modern-Hopfield Tier-1 drill on
order-n-energy compositional capacity (architectural pivot path).
