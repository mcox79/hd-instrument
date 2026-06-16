# research: DEEP DRILL — Phase C TIER-3 architecture decision-prep

Date: 2026-06-16 14:14
Triggered: USER deep-research drill; ordering hypothesis residue → modern-Hopfield → GHRR (per Drill 3 this session)
Mode: lit-scan calibration penalty applied (P deflated 0.15–0.25; novel-synthesis P capped at 0.50)
Scope: SUBSTRATE-INTERNAL ONLY per Drill 3 3-line definition (RNG-seed-derived / closed-form algebraic / substrate-resident; no external labels; no external loss; auditable end-to-end)

---

## HEADLINE

ORDER CONFIRMED with one structural amendment: **residue/FPE → modern-Hopfield → GHRR** is correct on cost AND on capability-gain ordering, but **modern-Hopfield's beta MUST be the Ramsauer Theorem-4 closed form `beta = f(d, |codebook|, M, Delta_min)` measured from the substrate codebook — NOT learned and NOT the transformer `1/sqrt(d)` default**. With that one constraint, all three candidates are substrate-internal-admissible per the Drill 3 definition. Residue/FPE is the natural Phase-B-HARD-FAIL follow-on (cardinality primitive does not emerge autonomously); modern-Hopfield is the natural follow-on if FPE lands cardinality but the substrate still lacks soft-subset retrieval at scale; GHRR is the LAST resort, justified only if the symmetry-axis (the bimodal symmetric-OR-asymmetric split across 38 binders) proves non-resolvable by any FPE+Hopfield composition.

P(order is correct as ranked) = **0.50** (capped at novel-synthesis ceiling).

---

## Cheap decisive test

For EACH candidate, the cheap substrate-internal pre-flight check (≤1 day each):

- **Residue/FPE**: implement FPE for a single integer scalar n in [0..K], specified-by-construction (unit-modulus phases, uniform). Verify (1) closed-form decode via projection onto base-vector powers recovers n with capability_preservation=1.0 on 1k random ints at N=4096; (2) FPE atoms compose with existing FHRR bind/unbind WITHOUT capability loss on a held-out 100-relation panel. HARD-PASS = both gates green; HARD-FAIL = either gate red.

- **Modern-Hopfield**: implement Ramsauer single-step update on existing codebook as the cleanup operator. Set `beta` from Theorem-4 closed form using measured Delta_min over current codebook (no sweep, no learning). HARD-PASS = (a) NN-cleanup capability preserved (argmax cases unchanged on held-out panel) AND (b) soft-subset retrieval emerges on bundles `bundle(a,b)` at N=4096 with both a and b in top-k for k=2. HARD-FAIL = (a) loses ANY NN-cleanup capability or (b) bundle(a,b) returns only one component.

- **GHRR**: implement m=2 block-diagonal binding alongside FHRR (m=1 backward-compatible). HARD-PASS = (a) m=1 GHRR exactly reproduces existing FHRR binder outputs on 100-relation regression panel AND (b) m=2 demonstrates partial-symmetric binding (commutator norm continuously tunable via diagonality of unitary factor) on 10 synthetic pairs. HARD-FAIL = m=1 regression breaks OR partial-symmetric knob is discontinuous/non-monotone.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

### Per-question verdict

**Q1. IMPLEMENTATION COST (person-days, experienced VSA implementer, integrate + verify + ratify):**
| Candidate | Core impl | Verification | Ratification | TOTAL |
|---|---|---|---|---|
| Residue/FPE | 1-2 d | 1-2 d | 1 d | **3-5 person-days** |
| Modern-Hopfield | 1 d | 2 d | 1-2 d | **4-5 person-days** |
| GHRR | 2-3 d | 3-5 d (m-sweep + regression panel) | 2-3 d | **7-11 person-days** |

Rank by cost: FPE ≤ Hopfield ≪ GHRR.

**Q2. INTEGRATION PATH:** FPE cleanest (literally repeated FHRR binding with real exponent; element-wise phase multiplication in Fourier domain; composes with all 38 binders with zero re-derivation). Hopfield second (codebook → memory matrix is mechanical; softmax separation is the only choice). GHRR third (m=1 is FHRR-compatible by construction but the 38 binders only auto-lift if they are pure-FHRR; any MAP/BSC/sparse-flavored binders need re-derivation).

Broadest downstream impact: **GHRR** (strictly larger algebra; partial-symmetric binding is a genuine new capability class). FPE second (cardinality/counting/continuous-magnitude — a new axis but compositional with current axes). Hopfield third (retrieval-side upgrade, not a new capability axis — soft-subset is a refinement of cleanup).

**Q3. SUBSTRATE-INTERNAL VERIFIABILITY (subtle risks):**
- FPE: base-vector selection. Uniform unit-modulus phases work by construction; conjugate symmetry for real outputs and length-scale tuning are knobs but are NOT external losses (chosen from substrate dimension and target range). Risk LOW.
- Modern-Hopfield: **beta tuning is the only real risk**. Transformer default `1/sqrt(d)` is geometry-only but ignores codebook-specific Delta_min; Ramsauer Theorem-4 closed form `beta_min = f(d, |M|, Delta_min, target_err)` IS substrate-internal (measured from codebook, not learned). If implementers default to learned beta the substrate-internal property breaks. MITIGATION: encode the Theorem-4 inversion as a substrate primitive, not a hyperparameter. Risk MEDIUM if the closed-form discipline is enforced; HIGH if a learning loop slips in.
- GHRR: block size `m` has NO published derivation rule. Free hyperparameter chosen via sweep. If m is derived from dimension factorization (e.g., m = smallest prime divisor of N), the choice becomes specified-by-construction. Risk MEDIUM, MITIGATABLE.

**Q4. CAPABILITY GAIN PROFILE:**
- Residue/FPE: cardinality (via RNS + CRT layer, Kymn 2024 confirms logarithmic dynamic-range scaling), counting, modular arithmetic, integer factorization, continuous-magnitude, kernel similarity for continuous lookup, grid-cell spatial codes.
- Modern-Hopfield: native bundle decode (returns convex combination, NN cannot); partial/ternary retrieval (via Fenchel-Young alpha-entmax for hard-sparse); exponential capacity in d (>>10^6 patterns at d=4096 vs ~570 for Hebbian); auditable separation step via Millidge 2022 Universal Hopfield decomposition.
- GHRR: strictly-larger algebra (m=1 ⊃ FHRR); **continuously tunable symmetry** (diagonal-Q → commutative, permutation-Q → maximally non-commutative, intermediate → partial-symmetric) — directly addresses the bimodal symmetric-OR-asymmetric basis gap.

OVERLAP: FPE and Hopfield are **near-orthogonal** (encoding axis vs retrieval axis). GHRR overlaps with neither — it's a binding-algebra extension. **Three roughly-orthogonal capability axes.**

**Q5. EMPIRICAL VALIDATION at substrate-comparable scale (N ≥ 4096):**
- FPE/SSP: D ∈ [1k, 16k] in Frady-Kanerva-Sommer 2022 (arXiv:2109.03429); kernel similarity preserved analytically; Komer 2019 benchmarks 122 datasets at D up to 4k. **HARD-PASS at scale.**
- RNS-HDC (Kymn 2024 arXiv:2311.04872): D in 1k-10k range; resonator-network factorization with 40 codebook vectors (vs 220 baseline). **HARD-PASS but at moderate dim, not 16k+.**
- Modern-Hopfield: Ramsauer 2020 d up to 1024 reported; immune-repertoire follow-up at d=1024 with >>10^5 patterns. **PARTIAL — no published N=4096 result in the lit-scan window.** Theory (Krotov-Hopfield) predicts exponential capacity scaling, so N=4096 is on-curve, but unverified empirically.
- GHRR (Yeung 2024 arXiv:2405.09689): D up to ~1000 with m ∈ {1,2,3}; effective dim ~9000. **NO N ≥ 4096 published.** This is the weakest empirical-validation candidate.

**Q6. RISK RANKING:**
- LOWEST risk: **Residue/FPE**. Simplest derivation, well-published at scale, no learned parameters, composes cleanly with FHRR, base-vector specifiability is a 30-year-old issue with known solutions.
- MEDIUM risk: **Modern-Hopfield**. Beta tuning is the only failure mode; closed-form discipline mitigates. Substrate-comparable scale unverified but extrapolation from theory is sound.
- HIGHEST risk: **GHRR**. Block-size hyperparameter undefined in source paper; no N ≥ 4096 published validation; integration only mechanical for pure-FHRR binders.

**Q7. RECOMMENDATION on order:** **CONFIRM residue/FPE → modern-Hopfield → GHRR.** Reasoning: cost-ordering matches capability-orthogonality ordering matches risk-ordering. No evidence to reorder.

ONE AMENDMENT: between FPE and Hopfield, INSERT a substrate-pause-and-evaluate gate. FPE may resolve cardinality-C3 without needing Hopfield at all; if so, Hopfield should be deferred until a SEPARATE retrieval-side gap is empirically demonstrated. Don't ship Hopfield speculatively.

**Q8. PHASE C TIER-3 TRIGGER LOGIC:**
- C3 HARD-PASS (substrate-internal abstraction discovers cardinality primitive autonomously): TIER-3 NOT NEEDED FOR CARDINALITY. The remaining trigger (symmetry-axis bimodality) is independent — still motivates GHRR if and only if symmetry-axis bimodality persists after Phase-B consolidation.
- C3 HARD-FAIL (cardinality does NOT emerge autonomously from substrate-internal abstraction over current basis): **Residue/FPE is the cleanest natural follow-on.** Specified-by-construction, drop-in compatible with FHRR, published at scale, lowest cost, lowest risk. Modern-Hopfield is NOT triggered by C3 alone — it's triggered by a separate retrieval-side gap (e.g., bundle decode failure at high codebook size or soft-subset failure).
- Symmetry-axis bimodality persists: **GHRR is the only published mechanism for continuously-tunable symmetry**. Triggered only if FPE+Hopfield composition cannot resolve.

---

## Cross-thread synthesis

- Composes with DECISION 142 strategic direction (CONSOLIDATE then GROW BASIS): TIER-3 is held for later USER decision; this drill is decision-PREP not execute-authorization.
- Composes with the bimodal-symmetric-OR-asymmetric finding across 38 binders (Phase-A gap-source result): GHRR is the only candidate that directly addresses the symmetry axis. FPE and Hopfield do not.
- Composes with Drill 3 substrate-internal 3-line definition: all three candidates are admissible IF the implementation respects (a) RNG-seed-derived OR closed-form algebraic, (b) no learned parameters via external loss, (c) substrate-resident state. The single failure mode is modern-Hopfield's beta — closed-form Theorem-4 discipline is required.
- Composes with 10th methodology rule (VERIFY-BEFORE-ASSERTING): each candidate has a cheap pre-flight check authored above; ratification gates exist.
- Composes with 11th USER-LOCKED rule (substrate-standalone capability FIRST): TIER-3 candidates extend substrate's own algebraic capability before any LLM-comparison framing.

---

## Substrate-product implications

- The substrate-product positioning artifact gains a THIRD axis if TIER-3 ships: (1) sound by construction, (2) auditable end-to-end, (3) algebraically extensible via substrate-internal primitives (no external supervision).
- Residue/FPE is the cheapest extension AND the one most likely to demonstrate "substrate discovers a new primitive when given the right algebraic scaffold" — strong product narrative ("we did not bolt arithmetic on; we extended the algebra and the substrate took the new primitive").
- GHRR carries the highest product-narrative payoff IF it lands ("substrate basis becomes continuously-tunable across the symmetric/asymmetric spectrum") but lowest empirical-grounding-at-scale today. RESERVE for after FPE lands and Phase-B-CONSOLIDATE completes.
- Modern-Hopfield carries the LEAST product-narrative payoff (it's a known retrieval upgrade with attention-flavor association that might mute the substrate-distinct framing). Ship only if a concrete retrieval-side gap demands it.

---

## TOP 3 RISKS per candidate

### Residue / Fractional-Power Encoding
1. Base-vector phase distribution sensitivity (Komer 2019; 2025 phasor-learning paper shows non-uniform bases sometimes outperform — but uniform is correct-by-construction).
2. RNS-CRT readout requires a resonator network (Kymn 2024) — added complexity beyond pure FPE if cardinality scope expands past single-magnitude.
3. Length-scale tuning for continuous-magnitude readout — knob exists but is substrate-derivable (target range / max dynamic range / dimension).

### Modern Hopfield as operator
1. **Beta tuning. Closed-form discipline must be enforced.** Highest single risk.
2. Meta-stable-state collapse at large codebook + high dimension — addressed in Santos 2024 (HEN) via pattern encoding before storage; may add complexity.
3. Soft-subset retrieval requires alpha-entmax / Fenchel-Young (Hu 2024 arXiv:2411.08590) for hard-sparse — moderate-cost extra layer if soft-but-dense retrieval is insufficient.

### GHRR
1. **Block size `m` is undefined in source paper.** Highest single risk; must be derived from substrate (e.g., `m = smallest prime divisor of N`).
2. NO published validation at N ≥ 4096. Substrate-scale unknown.
3. Re-derivation cost for non-FHRR-flavored binders among the 38; only m=1 is fully backward-compatible.

---

## ESTIMATED PERSON-DAYS (substrate-product positioning planning)

| Candidate | Implementation | Verification + ratification | TOTAL |
|---|---|---|---|
| Residue/FPE (basic, single-magnitude) | 1-2 | 2 | **3-4 person-days** |
| Residue/FPE + RNS-CRT cardinality | 3-4 | 3-4 | **6-8 person-days** |
| Modern-Hopfield (with Theorem-4 closed-form beta) | 1 | 3 | **4 person-days** |
| GHRR (m=1 + m=2 + partial-sym verification) | 3 | 5 | **8 person-days** |
| GHRR full m-sweep + 38-binder re-derivation | 5-7 | 7-10 | **12-17 person-days** |

---

## PHASE C TRIGGER LOGIC (decision matrix)

| Phase-B outcome | Trigger | Recommended TIER-3 candidate |
|---|---|---|
| C3 HARD-PASS (cardinality emerges autonomously) | NO new cardinality trigger | hold — re-evaluate symmetry-axis only |
| C3 HARD-FAIL + symmetry-axis bimodality resolved | cardinality gap only | **Residue/FPE** (cheapest, cleanest) |
| C3 HARD-FAIL + symmetry-axis bimodality persists | both gaps | **Residue/FPE FIRST**, then re-evaluate whether symmetry axis still needs GHRR after FPE composes with existing binders |
| C3 HARD-PASS + symmetry-axis bimodality persists | symmetry gap only | **GHRR** — directly addresses symmetry; only published mechanism |
| Retrieval-side gap demonstrated (bundle decode fails or soft-subset needed) | retrieval gap | **Modern-Hopfield** with Theorem-4 closed-form beta |

---

## Citations (verified count = 17)

Residue / FPE thread:
1. Frady, Kleyko, Kymn, Olshausen, Sommer 2022 "Computing on Functions Using Randomized Vector Representations" arXiv:2109.03429 (Neural Computation). Canonical FPE/SSP.
2. Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen 2024 "Computing with Residue Numbers in High-Dimensional Representation" arXiv:2311.04872 (Neural Computation 37(1)). RNS-HDC; resonator factorization 40 vs 220 codebook.
3. Komer 2019 UWaterloo thesis "Biologically Inspired Spatial Representation"; Komer, Stewart, Voelker, Eliasmith 2019 CogSci "A neural representation of continuous space using fractional binding". 122-dataset SSP benchmark.
4. Plate 1995 IEEE TNN 6(3):623-641 "Holographic Reduced Representations". Origin of HRR/FHRR.
5. "Improved Cleanup and Decoding of Fractional Power Encodings" arXiv:2412.00488 (2024). Decoding accuracy.
6. "Learning encoding phasors with fractional power encoding" IEEE 2025. Non-uniform phase distributions.
7. "A Grid Cell-Inspired Structured Vector Algebra for Cognitive Maps" arXiv:2503.08608 (2025). Grid-cell composition.
8. Kleyko 2022 arXiv:2203.00920. Integer factorization via VSA.

Modern-Hopfield thread:
9. Ramsauer et al. 2020 "Hopfield Networks Is All You Need" arXiv:2008.02217. Softmax-attention retrieval; Theorem-4 separation bound (beta closed form).
10. Krotov & Hopfield 2016/2021 arXiv:1606.01164 / arXiv:2008.06996. Dense associative memory; exponential capacity.
11. Millidge et al. 2022 "Universal Hopfield Networks" arXiv:2202.04557. Similarity→separation→projection decomposition; auditable.
12. Hu/Wu et al. 2024 "Hopfield-Fenchel-Young Networks" arXiv:2411.08590. Sparse retrieval via alpha-entmax.
13. Santos et al. 2024 "Modern Hopfield Networks meet Encoded Neural Representations" arXiv:2409.16408. Meta-stable-state collapse mitigation.
14. Wu et al. 2023 arXiv:2311.18434. Temperature-dependent phase transition; beta_c characterization.

GHRR thread:
15. Yeung, Zou, Jeong, Huang, Bastian, Imani 2024 "Generalized Holographic Reduced Representations" arXiv:2405.09689. Block-diagonal binding; tunable symmetry via diagonality.
16. Schlegel, Neubert, Protzel 2020 "A comparison of vector symbolic architectures" doi:10.1007/s10462-021-10110-3. VSA taxonomy.
17. Gayler 1998 "Multiplicative Binding, Representation Operators & Analogy". MAP; element-wise binding.

---

## P_deflated (lit-scan calibration penalty applied)

- P(residue/FPE drop-in lands cardinality cleanly on existing substrate): **0.50** (deflated from 0.70).
- P(modern-Hopfield with Theorem-4 closed-form beta lands soft-subset retrieval without learned parameters): **0.45** (deflated from 0.60; novel-synthesis cap respected).
- P(GHRR partial-symmetric binding lands at N ≥ 4096 with m=2 substrate-derived): **0.30** (deflated from 0.50; weakest empirical validation, undefined block-size derivation).
- P(proposed order residue → Hopfield → GHRR is correct): **0.50** (novel-synthesis cap).

---

## Next-drill candidate

Field: **FPE / RNS-HDC operational drill at N ≥ 4096** — if Phase-B closes with C3 HARD-FAIL, the immediate next research drill is operational-depth on RNS-CRT readout via resonator network (Kymn 2024), specifically resolving (a) length-scale tuning, (b) base-vector phase distribution choice, (c) integration test panel with existing 38 binders. This is Tier-1 fruit-bearing field-adjacent (modern-Hopfield neighbor; sparse-coding-compressed-sensing neighbor) and has the cleanest empirical at-scale grounding.
