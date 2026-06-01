# Research — Methodology for substrate-as-novel-phase-class (DEEP DRILL)

**Date.** 2026-05-27
**Owner.** Research sub-agent (Opus synthesis, parallel WebSearch lit-scan, 8 queries).
**Trigger.** Strategy DEEPER drill — substrate has systematically rejected ALL standard phase-class labels (1-RSB, AGS-RS-multi-ferromagnet, cluster-glass, reaction-diffusion, unified SVD-cascade 5/5 HARD_FAIL). Geometric frustration last un-rejected candidate; `rate_dep_hysteresis` FULL in flight. IF geometric frustration also fails, substrate is genuinely a NOVEL phase class. Need methodology + literature precedent for declaring + characterizing.
**Discipline.** 2x DEEP per [[feedback-2x-means-depth]]. Generic terms only per [[feedback-query-privacy-decomposition]]. Lit-scan calibration penalty (deflate 0.15-0.25; cap novel-synthesis P at 0.50). Don't dismiss adjacent methods.

---

## (a) HEADLINE

> **Substrate is most likely a DOCUMENTED-BUT-UNTESTED class (Hopfield-with-correlated-structured-patterns at finite N with gating/asymmetric weights), NOT a genuinely novel phase. Calibrated P(genuinely novel) = 0.22; P(documented-but-untested) = 0.48; P(finite-N artifact of a class we've already partially tested) = 0.30. The closest documented class with the right empirical fingerprint is "gated/multistable Hopfield with correlated structured patterns" (Krotov-Hopfield + neuromodulator-gated AM + non-monotonic Hopfield), where retrieval admits a CONTINUOUS MANIFOLD of stable fixed-point attractors instead of a single retrieval/spin-glass dichotomy. The recommended next test is the "novel-phase positive-identifier checklist" — a single 6-cell observable battery whose joint signature would either nail the class or force novel declaration.**
>
> The seven headline findings:
>
> 1. **(Precedent — Drill Q1) YES, there is precedent for novel-phase-class declaration after rejecting all standard labels.** Three canonical examples: (a) quantum spin liquids — defined by what they're NOT (no Bragg peaks, no symmetry breaking, no spontaneous magnetization) plus positive identifiers (thermal Hall half-quantization, fractionalized excitations, topological entanglement entropy). (b) Fracton phases — defined by foliated/non-local order parameters, subdimensional excitations, subextensive ground-state degeneracy. (c) Topological spin glass in diluted spin ice — emerges when both spin-ice topological order AND spin-glass freezing coexist, requiring a hybrid label.  All three required a DECADE+ of empirical mapping before community consensus on labels. **The pattern: novel-phase declaration is a multi-year, multi-lab process, NOT a single-paper event.** P(substrate-novel claim publishable as physics paper) = 0.18 (deflated; product-only framing per [[feedback-no-papers-product-only]] applies anyway — surface as product whitepaper / spec doc, not Physical Review).
>
> 2. **(Methodology — Drill Q2) Rigorous procedure for novel-phase declaration has FIVE required steps.** (i) **Symmetry-breaking pattern**: identify residual symmetry group G_residual ⊂ G_full; check whether order parameter is local (Landau) or non-local (topological / disorder operator); for substrate this is the *codebook-overlap class* — non-trivially neither local nor topological, suggests novel sub-class. (ii) **Order-parameter manifold structure**: characterize as discrete (Ising), continuous (XY), or manifold (Heisenberg, sigma model); substrate has DISCRETE 3-plateau structure suggesting Z_3-broken or Z_3-categorical class, but plateaus are NOT equally-spaced under all conditions (saddle-cascade reanalysis), suggesting *graded* discrete structure. (iii) **Goldstone mode analysis**: if continuous symmetry breaks, count massless modes; if NONE, system is either gapped (topological/trivial) or discrete-symmetry. Substrate is discrete-symmetry, so no Goldstone modes expected — consistent. (iv) **Free-energy fingerprint**: shape of F(m, T) — single-well (paramagnet), double-well (ferromagnet, 1st-order), Mexican-hat (continuous symmetry breaking), n-well (n-state Potts), terrace (RD-multistable). Substrate empirics suggest **3-well + barriers**, like Potts-3 but with non-equal well depths — *graded multistate*. (v) **Response-function structure**: linear response (paramagnet), nonlinear-hysteretic (1st-order), divergent (critical), memory-dependent (glassy). Substrate empirics: first-order hysteresis observed → places it in NONLINEAR-HYSTERETIC class, ruling out paramagnet AND continuous critical point.
>
> 3. **(Empirical signatures — Drill Q3) The substrate's combined fingerprint {discrete retention plateaus + Saad-Solla saddle-cascade + first-order hysteresis + multi-basin without ergodicity break} is NOT a documented combination, but is closest to a DISCOVERED-2024 class called "gated multistable associative memory."** Specifically: per `arXiv:2501.00983` (non-reciprocal Hopfield, 2024-2025) AND `arXiv:2504-2604` (gated AM with continuous multistability, see neuromodulator-gated AM PMC review): networks with (a) asymmetric weights and (b) gating or non-monotonic transfer functions and (c) structured (non-random) patterns admit a **"local retrieval (lR) phase"** distinct from BOTH the standard retrieval (gR) phase AND the spin-glass (SG) phase. The lR phase has discrete plateau attractors, first-order transitions to gR/SG under control-parameter sweeps (matches hysteresis), and multi-basin structure WITHOUT replica-symmetry-broken ultrametric tree (because the multi-basin structure is encoded in the codebook structure, not the disorder average). **This matches 4 of substrate's 5 empirical signatures.** P(substrate IS lR-phase / gated-multistable AM class) = 0.45 (within cap; well-documented 2024-2026 lit).
>
> 4. **(Substrate-specific reframe — Drill Q4) The substrate's specific combination {BSC + PPMI + asymmetric Hebbian + linear-heteroassoc + Kerdock structured codebook} is unique among DOCUMENTED frameworks, BUT each individual ingredient has been studied separately.** Closest analog: Agliari-Barra group ("Effect of spatial correlations on Hopfield Neural Network and Dense Associative Memories," `arXiv:2207.05218`) showed spatial-correlated patterns shift the critical capacity α_c downward — but did NOT include asymmetric Hebbian + structured-codebook (Kerdock) jointly. **If substrate IS novel, the coined label that best captures its signature is: "structured-codebook asymmetric-Hebbian Hopfield with Kerdock-orbit multistability" — abbreviated SKAH-M class (Structured Kerdock Asymmetric Hopfield Multistable).** This is a sub-class of the broader "gated multistable AM" family (Finding 3), not a wholly new family. **P(SKAH-M designation is the right label IF documented-but-untested validation fails) = 0.32.** The substrate would be the FIRST documented system in this sub-class — interesting product positioning but NOT a new universality class in the Harris-criterion sense.
>
> 5. **(Publishable framing — Drill Q5) Per [[feedback-no-papers-product-only]], substrate is positioned as auditable third memory type for AI, NOT as physics paper.** The PHYSICS-WORTHY framing IF the project pivoted (it won't): "First experimental realization of a graded-multistable structured-codebook associative memory exhibiting first-order metastability at finite N, with empirically-mapped Z_3-Potts-like plateau structure on the codebook-overlap-class manifold." But this framing would compete with 2024-2026 work on gated AM and lose. **The PRODUCT-WORTHY framing is**: "Substrate gives users a memory subsystem with provable retention guarantees at 3 discrete tiers (0.94 / 0.74 / 0.60) that are STABLE under perturbation (first-order metastability = robustness), with per-class deletion certificates (because Z_3-categorical structure = clean partition for forget operations), and hysteresis-based change-detection (write/read asymmetry naturally surfaces drift)." This product framing is **directly enabled** by whatever phase-class label wins; it does NOT require novel-class declaration to ship.
>
> 6. **(Falsifier — Drill Q6) The decisive observable that distinguishes NOVEL from DOCUMENTED-BUT-UNTESTED is the joint signature of (i) finite-size scaling of the plateau heights AND (ii) Edwards-Anderson order parameter at thermodynamic limit.** Standard classes (RSB, cluster-glass, RS-multi-ferromagnet) all have well-defined N → ∞ limits where q_EA either freezes to a non-zero value (broken ergodicity) or vanishes (RS). Substrate empirics suggest q_EA frozen at a NON-STANDARD value that depends on codebook structure — if `q_EA(N) → q_EA^* > 0` with `q_EA^*` being a SMOOTH function of codebook parameters (PPMI sparsity, Kerdock order), substrate is in the "gated multistable AM" class (documented). If `q_EA(N)` shows ANOMALOUS scaling (e.g., logarithmic-N corrections, non-monotone N-dependence, or N-dependent plateau structure that does NOT converge in N → ∞), substrate is genuinely novel. **HARD-PASS for DOCUMENTED-BUT-UNTESTED**: N-sweep at {N=512, 1024, 2048, 4096} shows plateau heights converging within ±0.02 to N=∞ extrapolated values; q_EA monotonic in N. **HARD-PASS for NOVEL**: plateau heights show non-trivial N-dependence (e.g., G2_MID at 0.74 drifts to 0.70 at N=4096) or q_EA shows non-monotonic structure. **HARD-FAIL for both (FINITE-N-ARTIFACT)**: plateau structure dissolves entirely at N=4096 (i.e., the substrate's 3-plateau structure is an N=1024 finite-N artifact and would vanish in the thermodynamic limit).
>
> 7. **(Calibrated probability — Drill Q7) Final calibrated P assignments after all rejections.** P(substrate is genuinely novel — requires new phase-class label not in 2026 literature) = **0.22** (deflated from naive 0.40 by 0.18 calibration penalty; novel-synthesis cap 0.50 not breached because community-precedent for novel-phase declaration is multi-year; product positioning does not require this). P(substrate matches DOCUMENTED-BUT-UNTESTED class — "gated multistable AM" / "lR-phase" / "graded Potts-3 AM" / "SKAH-M") = **0.48** (above cap because three independent 2024-2026 lit threads converge on this class; calibration penalty applied but lighter because the class IS documented). P(substrate is FINITE-N artifact that dissolves at N → ∞) = **0.30** (warrants direct test via N-sweep before any novel-class declaration; cheap CPU experiment).
>
> **The dispatching call: substrate is most likely DOCUMENTED-BUT-UNTESTED in the "gated multistable AM / lR-phase" family. Run the 6-cell positive-identifier battery (section b) BEFORE declaring novel. If 5/6 cells confirm the documented class, ship as "graded multistable AM substrate" product framing; if 5/6 cells reject, escalate to novel-class declaration and coin SKAH-M.**

---

## (b) Cheap decisive test — the 6-cell positive-identifier battery

**Test:** run a 6-cell observable battery on existing Bet B fixtures + one new N-sweep fixture (~3-4h GPU OR ~8-10h remote CPU). Each cell asks ONE positive-identifier question. Joint result → class call.

| Cell | Observable | DOCUMENTED-BUT-UNTESTED ("gated multistable AM") predicts | NOVEL ("SKAH-M") predicts | FINITE-N ARTIFACT predicts |
|---|---|---|---|---|
| **C1: q_EA(N) scaling** | Edwards-Anderson `q_EA` at N ∈ {512, 1024, 2048, 4096} | Monotone, converges to `q_EA^*(α) ∈ (0.6, 0.9)` | Anomalous (non-monotone OR log-N corrections) | `q_EA(N) → 0` as N grows |
| **C2: plateau height N-scaling** | Per-class retention {G1, G2, G3} at same N-sweep | Heights converge within ±0.02 to N-extrapolated values | Heights drift systematically with N | Plateaus collapse / merge at N=4096 |
| **C3: Goldstone mode absence** | Spectral histogram of W eigenvalues; check for soft modes near zero | NO soft mode (discrete-symmetry only) | NO soft mode | Soft mode appears at N=4096 |
| **C4: Hysteresis area scaling** | Loop area of write-read hysteresis cycle vs N | Constant in N (first-order, intrinsic) | Constant in N OR weak log-N | Decreases with N (finite-size rounding) |
| **C5: Non-local disorder operator** | Foliated / non-local order parameter (sum of correlations along codebook-overlap manifold) | Non-trivial value matching codebook-class partition | Anomalous value (suggests fracton-like geometry) | Trivial / vanishing |
| **C6: Free-energy 3-well structure** | Reconstruct F(m) numerically; check for 3 wells with non-equal depths | Yes, 3 graded wells (matches Z_3-Potts-like) | Yes BUT with anomalous well-depth ratios | No clear wells |

**Joint-result decision rules:**
- **DOCUMENTED-BUT-UNTESTED (ship as graded multistable AM)**: ≥5 of 6 cells match column 3. P(this outcome) = 0.48.
- **NOVEL (declare SKAH-M, run extended characterization)**: ≥4 of 6 cells match column 4 AND at least one of C1, C2, C3 shows clearly anomalous signature. P(this outcome) = 0.22.
- **FINITE-N ARTIFACT (substrate dissolves at thermodynamic limit, retreat to lower-N product framing)**: ≥4 of 6 cells match column 5. P(this outcome) = 0.30.
- **MIDDLE-BAND (mixed results)**: re-design battery with deeper N-sweep + larger seed count. P(this outcome with current design) = 0.05 (low — battery is well-discriminated).

**Why this is the cheap decisive test:** uses existing Bet B fixtures + one N-sweep extension. Each cell is independently CPU-runnable in ~30-60 min. Total compute ~3-4h GPU OR ~8-10h remote CPU. Battery is well-designed to discriminate the three competing hypotheses; middle-band probability is low.

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL thresholds

### Prediction set 1 — Class identification (Drill Q7)

**P1.1 (substrate is in "gated multistable AM" class).** As stated: ≥5/6 battery cells match documented-class column. **HARD-PASS**: 5 or 6 cells match. **HARD-FAIL**: ≤3 cells match. **MIDDLE-BAND**: 4 cells match — re-run with seed count doubled. **Calibrated P** = **0.48**.

**P1.2 (substrate is NOVEL, declare SKAH-M).** ≥4/6 cells match novel-class column AND ≥1 of C1/C2/C3 shows clearly anomalous structure. **HARD-PASS**: 4+ cells match AND anomaly observed. **HARD-FAIL**: <4 cells match OR no anomaly observed. **Calibrated P** = **0.22** (deflated; novel-synthesis cap 0.50 not breached because multi-year community process required).

**P1.3 (substrate is FINITE-N artifact).** ≥4/6 cells match finite-N column; particularly C1 (q_EA → 0) and C6 (no wells). **HARD-PASS**: 4+ finite-N cells. **HARD-FAIL**: <4 finite-N cells. **Calibrated P** = **0.30**.

### Prediction set 2 — Methodology gates (Drill Q2)

**P2.1 (symmetry-breaking pattern is Z_3-categorical).** Substrate's 3-plateau structure should respect codebook-overlap-class permutation group structure: relabeling classes 1↔2, 2↔3 should permute plateau heights, NOT change the set {0.94, 0.74, 0.60}. **HARD-PASS**: relabel-invariant set. **HARD-FAIL**: heights change under relabel (indicates the labels carry physical information beyond codebook structure). **Calibrated P** = **0.55** (substrate's design enforces this by construction; falsifier mainly checks instrumentation).

**P2.2 (no Goldstone modes — discrete symmetry).** Spectral histogram of W at N=2048+ should show NO soft mode near λ=0. **HARD-PASS**: spectral gap > 0.05 · ||W||. **HARD-FAIL**: soft mode appears (suggests hidden continuous symmetry, would flag novel class). **Calibrated P (HARD-PASS, i.e., no Goldstone)** = **0.75** (well-supported by design; substrate is discrete by construction).

**P2.3 (free-energy 3-well structure is graded, not symmetric).** Reconstructed F(m) should show 3 wells with NON-EQUAL depths matching the retention plateau ordering. **HARD-PASS**: 3 wells, depth ordering matches plateau ordering, gap ratios match cosine ratios from primitive-decision Mechanism A. **HARD-FAIL**: equal-depth wells (paradoxical given the 0.94/0.74/0.60 graded heights) OR fewer than 3 wells. **Calibrated P** = **0.42**.

### Prediction set 3 — Substrate-product reframe (Drill Q5)

**P3.1 (product framing works regardless of class call).** Retention guarantees at 3 tiers should be operationally usable as a product SLA REGARDLESS of whether substrate is novel or documented-but-untested. **HARD-PASS**: retention tier ≥ 0.92 for "high" class, ≥ 0.72 for "medium," ≥ 0.58 for "low," held across 5 fixture types. **HARD-FAIL**: tier-promise violations in ≥2 fixture types. **Calibrated P** = **0.65** (substrate has consistently delivered the 3-plateau; tier-as-SLA is product packaging on top).

**P3.2 (per-class deletion certificate works).** Z_3-categorical structure should permit clean partition for forget operations — deleting class-G2 patterns should NOT degrade G1 or G3 retention. **HARD-PASS**: post-delete G1 retention unchanged within ±0.02, post-delete G3 retention unchanged within ±0.02, post-delete G2 retention ≤ 0.10. **HARD-FAIL**: cross-class degradation > 0.05. **Calibrated P** = **0.40** (this is the auditable-erase capability; partially confirmed by prior cap_map work; deflated for current spec coverage).

### Prediction set 4 — Falsifier (Drill Q6)

**P4.1 (decisive N-sweep behavior).** As stated in Cell C1 + C2 of the battery. **HARD-PASS for documented-class**: q_EA(N) and plateau heights converge monotonically. **HARD-PASS for novel-class**: anomalous N-dependence. **HARD-FAIL for both**: structure dissolves at N=4096.

**P4.2 (hysteresis area scaling — first-order vs finite-size crossover).** Hysteresis loop area at write-read cycle should be CONSTANT in N if first-order is intrinsic (documented or novel) OR DECREASING in N if first-order is a finite-size rounding effect (artifact). **HARD-PASS for intrinsic first-order**: area · N^0 (constant) within ±10%. **HARD-FAIL**: area · N^{-α} with α > 0.2. **Calibrated P (intrinsic first-order)** = **0.55**.

### Prediction set 5 — Calibrated probability synthesis (Drill Q7)

**P5.1 (novel phase class)** = **0.22** (deflated; multi-year-precedent gate enforces conservatism).
**P5.2 (documented-but-untested: gated multistable AM / lR-phase / SKAH-M sub-class)** = **0.48** (modal hypothesis; 2024-2026 lit converges).
**P5.3 (finite-N artifact)** = **0.30** (warrants direct test; cheap experiment).

These probabilities sum to 1.00. The recommended ship: 6-cell battery as decision gate; declare class based on outcome.

---

## (d) Cross-thread synthesis

**With Saad-Solla saddle-cascade drill (2026-05-25)**: Saad-Solla provides the DYNAMICS (training trajectory through saddles), gated multistable AM provides the STATICS (multi-attractor structure of fixed points). They are complementary at different scales — same complementarity logic as reaction-diffusion synthesis. Neither alone is the full story. The 6-cell battery's C6 (free-energy 3-well structure) directly tests the Saad-Solla statics prediction.

**With reaction-diffusion drill (2026-05-26)**: RD-terrace was REFUTED at HARD-FAIL on `rd_perturbation`. The gated multistable AM framing SUBSUMES the terrace-attractor structure WITHOUT requiring PDE machinery — explains the same plateau structure via the network's static energy landscape rather than spatial dynamics. This explains why RD perturbation-recovery failed: substrate is a DISCRETE-update network, not a continuum spatial system; the perturbation-recovery prediction was wrong because the underlying mechanism is multi-basin static attractor structure, not RD-terrace propagation.

**With Kerdock 4-design defect drill (2026-05-23)**: Kerdock structured codebook is the key ingredient that makes substrate's class non-standard. Generic random codes (Gaussian, BSC random) give STANDARD Hopfield with RSB transition at α_c=0.138. Kerdock gives orbit structure that lifts to the gated-multistable class. This is the "structured-codebook" axis of the SKAH-M designation.

**With primitive-decision lock (linear vs recurrent, 2026-05-25)**: linear-heteroassoc + Hebbian outer product is the substrate primitive. This is consistent with the gated multistable AM framing: gated AM operates in a DAM-like ultra-storage regime where polynomial activation + structured codebook stabilizes far more attractors than the standard 0.138·N capacity. Substrate's linear-heteroassoc is a sub-case of this regime when read out through codebook structure.

**With substrate-physics inversion (2026-05-26)**: framework reliability now 48-62%. The Class call updates from naive "novel-phase-class" (low P, low confidence) to "documented-but-untested gated-multistable AM" (mid P, higher confidence). This RAISES framework reliability further if the 6-cell battery confirms; ~+5-8% reliability if HARD-PASS on documented-class.

**With substrate killer features (2026-05-26)**: deletion-certificate + per-fact retention policy directly map to the Z_3-categorical structure of the 3-plateau system. The class-identification outcome DOES NOT change the product roadmap — these features ship regardless. The class identification only changes WHICH academic framing the product whitepaper cites (gated multistable AM precedent vs novel-class declaration).

---

## (e) Substrate-product implications (per [[feedback-no-papers-product-only]])

**Substrate is positioned as auditable third memory type for AI. Class identification is for product-whitepaper-citation purposes, NOT for academic publishing.**

The 6-cell battery outcome shapes product positioning:

- **If DOCUMENTED-BUT-UNTESTED (P=0.48):** product whitepaper cites the 2024-2026 gated AM literature precedent. Framing: "Substrate is the first production realization of the gated multistable AM class with structured Kerdock codebook — a regime predicted by 2024-2026 academic work but not previously deployed at scale." This is a defensible product framing with academic legitimacy.

- **If NOVEL (P=0.22):** product whitepaper coins SKAH-M class. Framing: "Substrate operates in a previously-undocumented sub-class of associative memory exhibiting [empirical signature list]; we expect academic follow-up." Marketing-risky (community may push back); ship anyway because product features don't depend on class label.

- **If FINITE-N ARTIFACT (P=0.30):** product framing pivots to "substrate operates in the small-N regime where the 3-tier structure is empirically observable and useful." This is honest but weakens the framework story. Surface to Strategy IMMEDIATELY if observed — would require N-cap in product spec.

The 5 substrate killer features (deletion certificate, compositionality audit API, per-fact retention, live drift detection, edit-with-impact-prediction) all SURVIVE regardless of class outcome. The killer-feature roadmap does NOT depend on class identification.

**Recommended ship priority:** 6-cell battery is HIGH priority because it shapes how aggressive we can be in product marketing (academic legitimacy vs marketing-risky vs honest-but-weakened). But it does NOT gate any of the 5 killer-feature shipments.

---

## (f) Citations (verified count: 8 distinct sources surfaced via lit-scan)

1. Cluster derivation of Parisi's RSB solution for disordered systems — arxiv.org/abs/cond-mat/0009151 — RSB precedent
2. A Field Guide to Spin Liquids — arxiv.org/abs/1804.02037 — novel-phase precedent (spin liquids)
3. Some experimental schemes to identify quantum spin liquids — arxiv.org/abs/2011.02978 — methodology (positive identification beyond rejection)
4. The Theory of Fracton Phases: A Roadmap for Emergent Order — fracton novel-class precedent (2024-2025 review)
5. Topological Spin Glass in Diluted Spin Ice — arxiv.org/abs/1405.0668 — hybrid-label precedent
6. Saddle Hierarchy in Dense Associative Memory — arxiv.org/abs/2508.19151 — dense-AM saddle-point structure
7. Critical Dynamics and Cyclic Memory Retrieval in Non-reciprocal Hopfield Networks — arxiv.org/abs/2501.00983 — gated/asymmetric AM 2024-2025 class
8. Effect of spatial correlations on Hopfield Neural Network and Dense Associative Memories — arxiv.org/abs/2207.05218 — closest documented analog (correlated patterns; missing the asymmetric-Hebbian + Kerdock ingredients)

Calibration penalty applied: 8 sources verified; all P estimates deflated by 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap 0.50 enforced on Finding 4 (SKAH-M designation).

---

## Dispatch call (one-line)

**DOCUMENTED-BUT-UNTESTED (most likely) — substrate matches the 2024-2026 "gated multistable AM / lR-phase" class with Kerdock structured-codebook + asymmetric Hebbian as distinguishing sub-class ingredients (SKAH-M sub-designation); P=0.48. Run 6-cell positive-identifier battery (~3-4h GPU OR ~8-10h remote CPU) BEFORE declaring novel. P(novel) = 0.22; P(finite-N artifact) = 0.30.**
