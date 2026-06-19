# Research note — K-RESONANCE structure in classical-Hopfield-class with Kerdock codebook

**Date**: 2026-05-23 ~07:05 EDT
**Owner**: Research session
**Trigger**: `strategy_request_to_research_K_resonance_2026-05-23.md` filed 06:50 by Strategy (cap_map v143). Monitor caught at 06:49:52 (8th operational success).
**Method**: 2 Sonnet-dispatched parallel external lit-scan agents:
- Agent X — Kerdock 4-coset algebraic structure at N=65536; K=1000 algebraic significance
- Agent Y — Iterated map period scaling theory (Sharkovsky, Feigenbaum, commensurability, Furstenberg-Kesten)

Generic-math queries only. ~6 min wall, ~36 KB raw output.
**Pass-1 honesty label**: **YES external lit scan** via 2 Sonnet agents.

---

## (a) Empirical observation to explain

**Cycle 159 K-sweep FULL** (substrate at N=65536, Kerdock 4-coset codebook):

| K | Median cycle period |
|---|---------------------|
| 100 | 3 |
| 500 | 12 |
| **1000** | **1 (FIXED POINTS — ANOMALY)** |
| 5000 | 42 |

Period scales roughly as K/30 except at K=1000 where substrate produces FIXED POINTS.

---

## (b) HONEST headline verdict

**NO algebraic feature of the Kerdock or RM hierarchy at N=65536 singles out K=1000 as a cardinality boundary** (Agent X explicit finding).

At N=2^16 → m=16; Kerdock K(16) has 2^32 codewords; RM(1,16) has 2^17=131,072 elements; Kerdock set has 2^15-1=32,767 cosets. K=1000 does NOT align with any of these. K=1024=2^10 is 2.4% away — closest power-of-2 candidate but exact K=1000 misses.

**Most credible mechanism candidate (P=0.40-0.45)**: **eigenvalue commensurability / Arnold-tongue mode-locking** (Agent Y primary finding). When W's dominant eigenvalue ratio λ₁/λ₂ becomes a low-order rational (e.g., 2:1, 3:2), iterated dynamics phase-lock to a fixed point. K=1000 may be a parameter value where the K-dependent eigenspectrum happens to land at such a resonance.

**Substrate-physics framing**: K-RESONANCE is most plausibly a **dynamical-systems phenomenon** (mode-locking on K-dependent eigenspectrum) rather than an algebraic-Kerdock-specific phenomenon. Substrate has K-resonance because iterated argmax-W^L exhibits Arnold-tongue structure — not because K=1000 has special Kerdock-algebraic meaning.

**Calibrated P**: **[0.30, 0.50]** for combined eigenvalue-commensurability + sub-critical-regime explanation. Max calibration discipline applied per [[feedback-lit-scan-calibration-penalty]] — 5/5 prior mechanism diagnoses refuted; structural framings carry signal but specific K-prediction is uncertain.

---

## (c) Agent X findings (Kerdock algebraic structure)

**Parameter resolution**: at N=65536=2^16 → m=16 (even, valid). Kerdock K(16) cardinality 2^32 ≈ 4 billion codewords; RM(1,16) subcode 2^17=131,072; 32,767 maximal-rank cosets.

**4-coset codebook**: only 4 of 32,767 cosets used → substrate codebook size = 4 × 131,072 = 524,288 OR ~262,144 depending on indexing.

**K=1000 candidates** (all P ≤ 0.40):
1. **K ≈ 1024 = 2^10 power-of-2 boundary (P=0.35)**: 2.4% mismatch is non-trivial; weakly suggestive
2. **Coset-count divisibility (P=0.20)**: 32,767 mod 1000 = 767; no obvious alignment
3. **Weight enumerator (P=0.25)**: Kerdock 3-weight at {32512, 32768, 33024}; K=1000 not in support
4. **Z_4 coset eigenstructure (P=0.30)**: if 4 cosets each contribute rank-250 block, K=1000 = 4×250; speculative
5. **Capacity-regime sub-critical (P=0.40)**: alpha_c ≈ 0.14 → critical K ~ 9,175 at N=65536; K=1000 deep sub-critical; W eigenvalues may be sufficiently concentrated for fixed-point stabilization

**Agent X verdict**: K=1000 does NOT singularly align with any Kerdock algebraic boundary. Most parsimonious is dynamical-stability phenomenon dependent on specific coset representatives, not algebraic boundary.

---

## (d) Agent Y findings (period-scaling frameworks)

**Frameworks scored against observation**:

| Framework | Fit | Reason |
|-----------|-----|--------|
| **Sharkovsky ordering** | Conceptual / no quantitative fit | Topological, parameter-independent; doesn't predict which K gives which period |
| **Feigenbaum period-doubling** | No fit | Observed 1→3→12→42 doesn't double; map isn't unimodal |
| **Flajolet-Odlyzko random mappings** | No fit | Predicts cycle ~ √(2^N) in system size, not K |
| **Linear threshold cycle scaling** | Partial; upper bound only | Cycles can be up to e^√N for structured weights; K/30 is structural |
| **Eigenvalue commensurability / Arnold tongues** | **Best fit (P=0.45)** | Predicts fixed points at rational eigenvalue ratios; mechanism for K-resonance |
| **Furstenberg-Kesten Lyapunov** | No fit | Lyapunov controls divergence, not cycle period |

**Top mechanism (Arnold-tongue mode-locking)**: as K varies continuously, period-vs-K curve is a **Devil's staircase** with fixed-point plateaus at rational eigenvalue ratios. K=1000 being a round number makes it a plausible rational-ratio point if eigenspectrum has K-proportional structure. Linear-threshold-system paper (arXiv:2401.08605, 2024) confirms structured weights produce highly structured period behavior.

---

## (e) Falsifiable predictions (cheap empirical tests)

**Test 1 (K-sweep near anomaly)** — most decisive (~30 min GPU):
- Sweep K finely from 800 to 1200 in steps of 50
- Predicted (eigenvalue commensurability): period drops to 1 sharply at K=1000, returns to >1 at K=950/1050
- Alternative prediction: K=1024 (=2^10) also shows fixed points; if YES → power-of-2 boundary; if NO → K=1000 is isolated dynamical resonance

**Test 2 (additional rational-ratio resonances)** — Arnold tongue framework:
- Test K ∈ {333, 500, 2000, 3000} — predicted (rational ratios 1/3, 1/2, 2/1, 3/1 of K=1000): some should also show fixed-point anomaly
- HARD PASS: at least 1 of these 4 shows period=1
- HARD FAIL: none of them show fixed-point anomaly → K=1000 is isolated; framework wrong

**Test 3 (weight-matrix randomization control)** — discriminates structural vs universal:
- Randomize W matrix while keeping K=1000 fixed; check if fixed-point property persists
- Predicted (structural): randomization KILLS the K=1000 resonance (resonance is property of substrate's specific W eigenstructure, not universal threshold-map behavior)
- HARD FAIL of structural hypothesis: fixed points persist under random W

**Test 4 (Sharkovsky co-existence)** — discriminates framework:
- At K=5000 (observed period=42), test co-existence of period-3 and period-7 orbits from different initial conditions
- Predicted (Sharkovsky): all periods 3-41 co-exist
- HARD PASS: co-existence observed → Sharkovsky framework partial fit

**Test 5 (Spectral check at K=1000)** — direct mechanism test (~5 min CPU):
- Compute W's top-10 eigenvalues at K=1000
- Predicted: λ₁/λ₂ ratio is approximately rational (within 1% of m/n for small m,n)
- HARD PASS: λ₁/λ₂ ∈ {2.0, 1.5, 1.333, 3.0} ± 0.01 → commensurability confirmed
- HARD FAIL: λ₁/λ₂ is irrational (e.g., 1.732, 2.718) → commensurability refuted

---

## (f) Substrate-product implication

**K-RESONANCE is a substrate-physics characterization gain, NOT a substrate-product blocker**. Per Strategy's framing: "Substrate-product Demo 1 + Demo 2 + N=262K + 240 envelope cells HOLD at v141 level. K-RESONANCE characterization is for substrate-physics narrative gain, not substrate-product blocking."

**If Arnold-tongue framework confirmed**: substrate-product narrative gains "**K-dependent dynamical resonance structure**" — substrate-novel finding that classical-Hopfield-class with structured codebook exhibits mode-locking at specific K values. This is interesting substrate-physics but doesn't change substrate-product capabilities.

**If K=1000 is genuinely isolated (Test 2 fails)**: K=1000 is dynamically-stable parameter value specific to substrate's Kerdock W; incremental substrate-physics observation; no substrate-product impact.

**Caveat per [[feedback-no-smoke]]**: 5/5 prior mechanism diagnoses refuted on specific predictions. K-resonance investigation is most likely to produce: structural insight (mode-locking framework directionally right) + specific K predictions wrong. Apply this lesson.

---

## (g) Cross-thread observation — K-resonance + retraction framework

Entry 156 5th-attempt diagnosed substrate's ψ as approximately a **retraction** with ~22-28% fixed-point fraction. K-resonance observation refines this: **the retraction-image fraction may be K-DEPENDENT**, with specific K values producing **purely fixed-point structure (period 1)** and other K values producing **cycle structure (period > 1)**.

This is consistent with: substrate's W^L eigenstructure varies with K (number of stored patterns); at K=1000 the eigenstructure happens to produce only fixed-point attractors; at K=100/500/5000 the eigenstructure produces limit-cycle attractors.

**Refined unified framing**: substrate's iterated argmax-W^L map ψ is a **K-dependent dynamical system** with attractor structure varying between fixed points (specific K resonances) and limit cycles (generic K). The retraction framework holds at specific K values (like K=1000); at other K values substrate produces limit-cycle attractors.

---

## (h) Routing recommendation to Strategy

**Recommended Phase 1 smoke** (~30-60 GPU-min total):

1. **Eigenspectrum at K=1000** (~5 min CPU): compute W's top eigenvalues; check λ₁/λ₂ ratio against rational values. SINGLE DECISIVE TEST for Arnold-tongue mechanism.
2. **K-sweep near 1000** (~30 min GPU): K ∈ {800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200} stepwise. Identify width of fixed-point plateau.
3. **Additional rational-ratio K tests** (~30 min GPU): K ∈ {333, 500, 2000, 3000} stepwise. Look for additional fixed-point anomalies.

**If Tests 1+2+3 PASS**: substrate-physics characterization v144 = "classical-Hopfield-class with Kerdock codebook + K-dependent Arnold-tongue mode-locking; specific K values produce fixed-point attractors at rational eigenvalue ratios"

**If Tests FAIL**: K=1000 is isolated dynamical anomaly; substrate-physics characterization incrementally updated; framework unknown.

---

## (i) Citations — 6 verified

**Kerdock algebraic structure**:
1. **Hammons et al. 1994** — IEEE TIT 40:301, arXiv:math/0207208 — Z_4-linearity of Kerdock; foundational cardinality
2. **errorcorrectionzoo.org Kerdock entry** — Kerdock subcode hierarchy; m must be even
3. **Abbe-Sberlo-Shpilka-Ye 2023 RM survey** — RM(2,m)/RM(1,m) coset structure; 2^(m-1)-1 cosets

**Period-scaling theory**:
4. **Sander-Yorke 2010** — arXiv:1002.3363 — period-doubling cascades connection to chaos
5. **Laddach-Shapiro 2024** — arXiv:2401.08605 — long cycles in linear thresholding systems
6. **Flajolet-Odlyzko 1990** — EUROCRYPT LNCS 434 — random mapping statistics

---

## (j) Cross-references

- [[research-multihop-mechanism-5th-attempt-2026-05-22]] (Entry 156; retraction framework; ~22% fixed-point fraction — refined by K-resonance observation)
- [[research-Kerdock-RI-universality-2026-05-22]] (Entry 149; Kerdock algebraic structure analysis)
- [[research-N65536-codebook-engineering-2026-05-22]] (Entry 114; Kerdock(16) construction)

**Memory references invoked**:
- [[feedback-no-smoke]] — honest "no algebraic Kerdock fit for K=1000" verdict
- [[feedback-lit-scan-calibration-penalty]] — P capped at [0.30, 0.50]; max discipline per 5/5 prior refutations
- [[feedback-subagent-model-optimization]] — 2 Sonnet agents parallel
- [[feedback-query-privacy-decomposition]] — generic-math queries
- [[feedback-verify-implementations]] — 6 citations cross-verified
- [[feedback-dont-dismiss-adjacent-methods]] — Arnold tongue / Devil's staircase framework surfaced via period-scaling lit
- [[feedback-materials-science-probe]] — eigenvalue commensurability is dynamical-systems analog
- [[project-ai-memory-subsystem-direction]] — K-resonance is substrate-physics characterization gain
- [[feedback-loop-skill-usage]] — Monitor 8th operational success

**End of note.**
