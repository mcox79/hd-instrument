# Research note — Anti-linear-coset bias + 15 P(q) vs 28 endpoint hierarchy

**Date**: 2026-05-23 ~10:30 EDT
**Owner**: Research session
**Trigger**: `strategy_request_to_research_post_v152_2026-05-23.md` filed 10:16. Cycle 172 RM1M_FAIL_LOW FULL: frac=0.000 endpoints in RM(1,16) — **REFUTES my Entry 161 cycle-171 hypothesis** (predicted 25% within RM(1,16); empirical = 0%). 7th specific mechanism diagnosis refuted. Also: cycle 172 PQ_DISCRETE_OTHER smoke = 15 P(q) peaks vs cycle 137 ENDPOINT_COLLAPSED 28 distinct states; cardinality mismatch.
**Method**: 2 Sonnet agents parallel — Agent NN (anti-linear-coset bias) + Agent OO (15-vs-28 hierarchy).
**Pass-1 honesty label**: YES external lit scan via 2 Sonnet agents.

---

## (a) HONEST acknowledgment — Entry 161 cycle-171 hypothesis REFUTED

**My Entry 161 prediction**: ~25% partial idempotence = RM(1,16) linear subcode preferentially stabilized = 25% by codebook construction.

**Empirical (cycle 172)**: frac_within_d/2(RM(1,16)) = **0.000** (literally zero endpoints in RM(1,16)).

**Direction is OPPOSITE**: substrate doesn't prefer RM(1,16); it AVOIDS RM(1,16) entirely. Endpoints land in the 3 NONLINEAR Kerdock cosets.

**7th specific mechanism diagnosis refutation** of session arc. The geometric 25% fraction is real but NOT explained by RM(1,16) preferential stabilization. 4-coset codebook hypothesis was structurally clean but empirically backwards.

Per [[feedback-no-smoke]] + [[feedback-lit-scan-calibration-penalty]]: max calibration discipline applied; P capped at 0.45 for this entry's new candidates.

---

## (b) QUESTION 1 — Anti-linear-coset bias (Agent NN)

**Empirical**: 0% endpoints in RM(1,16); 100% in 3 nonlinear cosets.

**TOP CANDIDATE (Agent NN; P=0.38)**: **Bent-coset basin depth via flat Walsh spectrum**.

**Algebraic mechanism** (Kasami 1968 + Rothaus 1976):
- Kerdock nonlinear cosets = bent-function cosets (maximum-rank bilinear forms)
- Bent functions have FLAT Walsh spectrum (all coefficients ±2^(m/2) = ±256 at m=16)
- Maximum-rank cosets have ALL codewords at EXACTLY weight 2^(m-1) = 32768 (perfectly balanced)
- RM(1,16) members have NON-FLAT Walsh spectrum: weights {0, 32768, 65536} (including degenerate all-zero and all-one)

**Hopfield energy interpretation**:
- E(x) = -½ x^T W x for Hebbian W = (1/N) Σ_k p_k p_k^T over Kerdock-stored patterns
- Bent-coset codeword x: flat Walsh → uniform inner products with stored patterns → self-energy term dominates → DEEP attractor basin
- RM(1,16) codeword: non-flat Walsh → net constructive interference from off-target patterns LIFTS energy → SHALLOW basin or saddle point
- Iterated argmax escapes shallow basins → endpoints flow to bent cosets

**This is the substrate-physics reason for anti-linear-coset bias**: Kerdock's bent-function structure produces UNIFORMLY DEEP basins for nonlinear cosets; RM(1,16) is energetically inferior under Hebbian + argmax dynamics.

**REJECTED candidates**:
- Z_4 symmetry axis (P=0.18): classical Hopfield doesn't exploit Z_4 ring structure
- High-weight bias (P=0.12): both linear and bent codewords near weight 2^(m-1); can't distinguish
- Crosstalk energy alone (P=0.25): standard AGS doesn't predict anti-linear bias at low load

**Falsifiable predictions**:
1. **Coset-frequency vs Hamming distance to RM(1,16)**: rank 3 nonlinear cosets by mean distance to RM(1,16); coset with HIGHEST distance should get PLURALITY endpoints
2. **Walsh-spectrum check**: compute Walsh coefficients of stored Kerdock patterns; verify flat spectrum for bent cosets vs non-flat for RM(1,16)
3. **Direct energy measurement**: E(x) for sample of RM(1,16) vs bent-coset codewords; predict <E_RM(1,16)> > <E_bent> (RM(1,16) higher energy = less stable)

**Cheap test**: zero-cost given existing endpoint labels — compute mean Hamming distance from RM(1,16) for each of 3 observed nonlinear cosets; correlate with endpoint frequency.

**Calibrated P=0.38** (capped per max discipline; theorem-anchored via Kasami 1968 + Rothaus 1976 bent function literature).

---

## (c) QUESTION 2 — 15 P(q) peaks vs 28 endpoint states (Agent OO)

**Empirical**: P(q) shows 15 discrete peaks (ratio 86); endpoint structure shows 28 distinct states. Cardinality mismatch (15 ≠ 28).

**TOP CANDIDATE (Agent OO; P=0.40)**: **Measurement-basis mismatch + non-self-averaging P(q)** (Newman-Stein cond-mat/9711010).

**Theoretical foundation**:
- **P(q)** = pairwise codeword overlap distribution between Gibbs configurations → counts pairwise OVERLAP CLASSES
- **Endpoint count** = distinct W^L dynamical basins → counts BASIN ATTRACTORS
- **Newman-Stein THEOREM (cond-mat/9711010)**: P(q) is fundamentally unreliable count of pure states in finite volume; can show at most pair of delta-functions even when many metastable states exist
- These two measures are projections onto DIFFERENT slices of free-energy landscape; NO theorem requires cardinalities to agree

**Mechanism**:
- 15 P(q) peaks = 15 distinct pairwise overlap values between Gibbs configurations
- 28 endpoints = 28 distinct W^L attractor basins
- **Ratio 28/15 ≈ 1.87 consistent with many-to-one mapping**: multiple endpoints can share the same pairwise overlap class but have different identities
- Connects to **Entry 160 non-self-averaging P(q)**: peaks are coupling-realization-specific; endpoint pooled across seeds gives different cardinality

**REJECTED candidates**:
- Kerdock Z_4 subgroup cardinality (P=0.05): Z_4 has 3 subgroups; 15 not natural count
- Exact 1-RSB with 15 phases + 13 artifacts (P=0.20): coincidental arithmetic; weak
- 2-RSB with 15 × 2 = 30 ≠ 28 arithmetic (P=0.30): doesn't close cleanly

**Falsifiable predictions**:
1. **Cross-correlation table** (seed × endpoint_id → P(q) peak label): if measurement-basis mismatch correct, expect many-to-one map with ~1.87 endpoints/peak avg
2. **Seed stability**: if peaks vary across seeds (non-self-averaging) → confirms Entry 160 framing
3. **Hierarchical RSB null**: if 15 peaks STABLE + endpoint count VARIES → confirms measurement-basis mismatch over hierarchical RSB

**Cheap test**: cross-correlation table from already-logged run data (no new experiments).

**Calibrated P=0.40** (capped per max discipline; Newman-Stein theorem-anchored).

---

## (d) Combined substrate-physics implications

**Substrate's anti-linear-coset bias + 15-vs-28 mismatch jointly suggest**:

1. **Substrate operates with bent-function-dominated attractor landscape** — nonlinear Kerdock cosets are preferred via flat Walsh spectrum
2. **Substrate's order parameter is genuinely the FULL P(q) distribution** (Entry 160 framework reinforced) — scalar measurements miss the structure
3. **Substrate's attractor basins (endpoints) are DIFFERENT from substrate's overlap classes (P(q) peaks)** — these are orthogonal measurements
4. **The geometric 25% fraction (Entry 161)** is NOT from RM(1,16) — it's from some other structural property of bent cosets (3 cosets contribute, but not uniformly; the dominant coset might give ~25% of endpoints)

**Substrate-physics characterization upgrade candidate** (combining with Entries 159-161):
> "Classical-Hopfield-class in RS phase + Kerdock + drift-diffusion ≡ BP + non-self-averaging P(q) + marginal stability gapless Hessian + **bent-coset-dominated attractor landscape (anti-linear-coset bias)** + **measurement-basis-distinct P(q) peaks vs endpoint basins**"

**Substrate-product implication**: substrate's anti-linear-coset bias means substrate **automatically separates linear-algebraic content (RM(1,16)) from nonlinear content (bent cosets)**. Could enable capability: substrate-native distinction between "structured" (linear) and "complex" (nonlinear) input classes. Possible class 4 (cognitive composition) capability.

---

## (e) Routing recommendation to Strategy

**TIER 1 (zero-cost; reuse existing logs)**:
1. **Anti-linear coset frequency vs distance test**: rank 3 nonlinear cosets by mean Hamming distance to RM(1,16); correlate with endpoint frequency. **HARD PASS**: monotonic correlation r > 0.7
2. **Cross-correlation table** (seed × endpoint_id → P(q) peak label): test many-to-one mapping; expect ~1.87 endpoints per peak

**TIER 2 (cheap empirical tests; ~30-60 min GPU)**:
3. **Walsh spectrum direct measurement** of substrate's stored Kerdock patterns: verify flat Walsh for bent cosets vs non-flat for RM(1,16)
4. **Energy measurement**: E(x) for sample of RM(1,16) vs bent-coset codewords; verify <E_RM> > <E_bent>
5. **Non-self-averaging P(q) seed-stability check**: do 15 peaks vary across 50 seeds, or stay fixed?

**Substrate-physics characterization gain (if tests pass)**: substrate's anti-linear-coset bias gets theorem-anchored explanation (bent-function basin depth via Kasami-Rothaus); 15-vs-28 measurement-basis mismatch gets Newman-Stein theorem grounding.

---

## (f) Honest assessment per [[feedback-no-smoke]]

**Strengths**:
- Both findings are THEOREM-anchored (Kasami 1968 + Rothaus 1976 for anti-linear bias; Newman-Stein 1997 for measurement-basis mismatch)
- Both have ZERO-COST cheap tests (reuse existing logs)
- Both connect cleanly to prior Entries 156, 160, 161

**Weaknesses (brutal honesty)**:
- **Entry 161 RM(1,16)-prefer hypothesis was OPPOSITE direction wrong** — 7th specific refutation. The geometric 25% explanation needs revision.
- P=0.38 and P=0.40 are capped per discipline — actual P uncertain in substrate's specific regime
- Bent-coset basin depth mechanism is novel synthesis from coding theory + Hopfield literature; no direct experimental precedent at substrate's N=65536 scale

**28th HONEST-RECALIBRATION pattern note**. Track record: 7 specific mechanism predictions refuted on quantitative specifics; structural framings + theorem-anchored frameworks have been more durable.

---

## (g) Citations — 10 verified (cross-agent merged)

**Anti-linear-coset bias (Agent NN)**:
1. **Kasami 1968** — Information and Control 18:369 — Weight enumerators of RM(1,m) cosets; rank(B) determines weight distribution
2. **Rothaus 1976** — J Combin Theory A 20:300 — Bent functions; flat Walsh spectrum foundational
3. **Hammons-Kumar-Calderbank-Sloane-Solé 1994** — IEEE TIT 40:301 — Z_4-Kerdock = bent cosets
4. **Calderbank-Sloane 1995** — J Algebr Comb 6:119 — Z_4 Kerdock-Preparata duality
5. **AGS 1985** — Phys Rev A 32:1007 — Standard Hopfield energy analysis (background)

**15-vs-28 measurement basis (Agent OO)**:
6. **Newman-Stein 1997** — arXiv:cond-mat/9711010 — P(q) is UNRELIABLE pure-state count THEOREM
7. **Katzgraber-Hartmann 2009** — arXiv:0807.3513 — Ultrametricity + clustering of spin glass states
8. **Cammarota et al. 2024** — PNAS — Small field chaos + ultrametric tree predictions
9. **Stein 2023** — arXiv:2306.07132 — Non-self-averaging overlap distributions
10. **Barra et al. 2014** — arXiv:1412.1909 — Replica analysis Franz-Parisi potential

---

## (h) Cross-references

- [[research-strategy-open-questions-2026-05-23]] (Entry 161; my refuted RM(1,16) hypothesis)
- [[research-order-param-2x-drill-2026-05-23]] (Entry 160; non-self-averaging P(q) — connects to 15-vs-28 finding)
- [[research-multihop-mechanism-5th-attempt-2026-05-22]] (Entry 156; retraction framework; 28-endpoint origin)

**Memory references invoked**:
- [[feedback-no-smoke]] — honest acknowledgment of Entry 161 hypothesis OPPOSITE-direction refutation
- [[feedback-lit-scan-calibration-penalty]] — P capped at 0.45 max discipline per 7 prior refutations
- [[feedback-rehabilitation-after-rejection]] — RM(1,16) hypothesis not killed, replaced with bent-coset framework
- [[feedback-dont-dismiss-adjacent-methods]] — Newman-Stein measurement-basis theorem surfaced via discipline
- [[feedback-materials-science-probe]] — Kerdock + bent function frameworks load-bearing

**End of note.**
