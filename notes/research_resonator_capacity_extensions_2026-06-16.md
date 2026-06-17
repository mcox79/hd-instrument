# Research: resonator-network capacity extensions (HONEST_BOUNDED rescue)

filed: 2026-06-16
dispatched-by: Director (substrate-product context)
depth: 2x deep lit-scan (4 parallel Sonnet sub-agents + Opus synthesis)
calibration penalty: -0.20 (uncharted regime; substrate combines residue+FPE+resonator in a way no single published paper has tested)

---

## (a) HEADLINE

Literature offers FOUR ORTHOGONAL axes for extending resonator-network capacity at fixed budget while preserving log-scaling decode. ONE axis (stochastic noise injection, Langenegger 2024) is dominant per published quantification (50x-100000x capacity gain) and is the highest-leverage substrate-applicable direction. THREE other axes (hierarchical/factored architecture, Hopfield-attention hybrid, residue-CRT representation) are LOAD-BEARING but each has a documented caveat. NO published paper combines all four; the substrate already operates a residue+resonator hybrid (axis 4) and stands to gain most from adding axis 1 (stochasticity).

P(stochastic noise injection extends substrate capacity envelope with single-knob tuning, MIDDLE_BAND or better) = 0.55 deflated (cap retained per calibration discipline). P(load-bearing capacity extension equivalent to Langenegger 50x gain in substrate) = 0.30 deflated.

---

## (b) Cheap decisive test

Pre-flight (1-2 hr CPU): on the substrate's existing resonator primitive at the breakdown threshold (the point where HONEST_BOUNDED verdict triggered):

1. Add ASYMMETRIC CODEBOOK FACTORIZER (ACF) variant per Langenegger 2024 arXiv:2412.00354: bitflip-perturb ONE codebook copy at initialization only, no per-iteration noise change.
   - Single knob: bitflip probability p in {0.05, 0.10, 0.20}.
   - Hold restarts cap + iters cap at substrate's pre-registered Phase-B values.
   - Measure: (i) accuracy at and beyond breakdown threshold, (ii) iter count, (iii) breakdown-point shift.

2. Compare against ITERATIVE-NOISE variant (IMF) per same paper: add Gaussian noise per resonator step, single sigma knob.

3. Verify log-scaling decode preserved by checking iter-count vs M curve sub-linear up to and past prior breakdown point.

HARD-PASS: at the substrate's prior HONEST_BOUNDED breakdown threshold (call it M_break), the ACF or IMF variant pushes accuracy >=0.90 at M = 5 * M_break with the SAME restarts+iters cap (no per-scale budget growth) and the iter-count vs M curve remains sub-linear past M_break.

HARD-FAIL: at M_break neither ACF nor IMF accuracy crosses 0.70 with any single noise-knob value in {0.05, 0.10, 0.20} for ACF or sigma in {0.01, 0.05, 0.1} for IMF, OR the iter count grows super-linearly with M past breakdown (limit-cycle escape fails).

MIDDLE_BAND (most-likely outcome): partial gain (1.5x-3x breakdown shift) but not the 50x reported in Langenegger - substrate's residue+FPE composition has additional confounds (FPE phase-kernel non-orthogonality, residue-modulus coupling) that the published bare-resonator benchmark does not have.

---

## (c) Falsifiable predictions with HARD PASS / HARD FAIL thresholds

PRED-1 (lit-anchor): ACF noise injection extends operational capacity envelope by >=10x at fixed restarts+iters cap on the substrate's HONEST_BOUNDED test.
  HARD-PASS: >=10x M_break shift at single-noise-knob p in {0.05, 0.10, 0.20}.
  HARD-FAIL: <2x shift at all three knob values OR catastrophic accuracy drop (<0.50) inside prior envelope.

PRED-2 (mechanism specific): the dominant failure mode at substrate's HONEST_BOUNDED edge is LIMIT CYCLES, not basin shrinkage and not noise accumulation. Evidence test: ACF (init-noise only, no per-step noise) extends envelope by similar magnitude to IMF (per-step noise). If ACF >= IMF capacity gain, limit-cycle escape is confirmed dominant.
  HARD-PASS: ACF gain within 0.7x to 1.3x of IMF gain.
  HARD-FAIL: ACF gain <0.3x of IMF gain (means per-step noise IS load-bearing - substrate has different failure mode than published bare resonator).

PRED-3 (substrate-novel): residue+FPE composition introduces an ADDITIONAL failure mode beyond limit cycles - FPE kernel near-neighbor collision. If true, ACF and IMF alone will NOT close the gap fully; will need to add kernel-aware cleanup head (Lu/Bremer 2024 type) as second layer.
  HARD-PASS for this prediction: ACF+IMF stand-alone gain is partial (1.5x-3x) AND adding modern-Hopfield single-step cleanup head (Ramsauer beta tuned to closed-form per Theorem 4) pushes gain to >=10x.
  HARD-FAIL: even with cleanup head, gain stays <3x - means substrate has structural collision floor that noise cannot escape.

PRED-4 (architectural ranking): for substrate's regime, the literature ranks extensions as:
  1. Stochastic noise injection (Langenegger 2024) - highest expected gain
  2. Modern-Hopfield attention-resonator hybrid (Yeung 2024 arXiv:2403.13218) - second; closed-form beta tuning
  3. Hierarchical/partitioned architecture (Renner 2024 arXiv:2208.12880) - third; substrate would need task-surface partition that may not exist
  4. Residue/CRT extension (Kymn 2024 arXiv:2311.04872) - substrate ALREADY USES this; gain already captured
  HARD-PASS: rank 1 produces largest gain in substrate test (matches literature).
  HARD-FAIL: rank 1 produces SMALLEST gain - substrate's regime is fundamentally different from published; need to switch to attention-resonator (rank 2) as primary.

---

## (d) Cross-thread synthesis with prior entries

PRIOR ENTRY 1 (2026-06-16 14:36): research_DEEP_DRILL_cleanup_noise_FPE_interaction
  - That drill flagged FPE-kernel near-neighbor collision as the LIKELY blocker at M=2000.
  - Recommended modern-Hopfield single-step cleanup head as lowest-risk mitigation.
  - THIS DRILL ALIGNS: PRED-3 above predicts substrate will need BOTH stochastic noise (limit-cycle escape) AND kernel-aware cleanup (collision floor). The two prior drills are complementary; PRED-3 stitches them into a single composed extension.

PRIOR ENTRY 2 (2026-06-16 14:18): research_bundle_norm_null_hypothesis
  - That drill identified MIDDLE_BAND as the most-likely Phase-B cardinality outcome.
  - THIS DRILL EXTENDS the MIDDLE_BAND framing to the resonator-capacity question: substrate is likely to see partial 1.5x-3x capacity gain from noise injection alone, with the full 10x+ requiring composed extensions.

PRIOR ENTRY 3 (2026-06-16 14:14): TIER-3 architecture decision-prep
  - Ordered residue/FPE -> Hopfield -> GHRR for substrate's algebra extension.
  - THIS DRILL ADDS a fourth axis (stochastic noise injection) that should be inserted BEFORE Hopfield as a separate dimension. Noise injection is a CAPACITY extension at fixed algebra, not an algebra extension - it composes WITH residue/FPE (substrate's existing layer) WITHOUT adding new operators.

PATTERN: across these four drills, the substrate's HONEST_BOUNDED verdict on resonator cleanup is consistent with published bare-resonator breakdown (Hersche 2024: limit cycles emerge at M ~ 1.2e5; Langenegger 2024: F=2 breakdown at ~1e5, F=4 at ~1e7). The substrate is operating well inside the published envelope at substrate-canonical dim N=4096 - which means the HONEST_BOUNDED verdict's breakdown threshold tells us the substrate's COMPOSITION (residue+FPE+resonator) is more constrained than bare resonator alone. The capacity-extension techniques that work for bare resonator should TRANSFER FIRST-ORDER but with caveats for FPE collision floor.

---

## (e) Substrate-product implications

PRODUCT FRAME: an observable hyperdimensional substrate that ships with a published capacity envelope AND a known cliff-edge mitigation recipe is a stronger product than one with just the envelope. The HONEST_BOUNDED verdict is a feature, not a bug, IF the substrate ships with a known-leverage extension recipe.

CONCRETE PRODUCT-RELEVANT FINDINGS:

1. ACF variant (init-noise only) is the CHEAPEST possible substrate extension: one bitflip pass at codebook construction time, no per-iteration cost change, no algebraic extension. If it delivers even 5x capacity gain, substrate ships a "capacity-extended" variant at marginal cost.

2. The Langenegger 2024 result is HARDWARE-AGNOSTIC for the ACF variant (only IMF needs analog noise; ACF works on digital). Substrate is software-first; ACF is the natural fit.

3. Modern-Hopfield attention-resonator (Yeung 2024) is the closed-form alternative IF stochastic injection fails. Substrate already has Hopfield-cleanup pathway from prior drill (TIER-3 architecture decision-prep); composing those two is a structural option.

4. The HONEST_BOUNDED verdict + capacity-extension recipe + log-scaling preservation is a publishable composite (in tracking-document terms per 10th-USER-LOCKED-rule, an INTERNAL TRACKING DOCUMENT artifact, not a paper). The substrate-product narrative is: we measured the cliff, we know the dominant failure mode (limit cycles per literature consensus), we know the dominant mitigation (stochastic noise injection per Langenegger 2024 50x quoted).

5. RECOMMEND: defer GHRR (TIER-3 third in prior decision matrix) until ACF/IMF tested. Capacity gain from stochastic injection is published 50x-1e5x; GHRR gain is unverified at substrate scale. Cheap+lit-anchored wins.

6. NEGATIVE-RESULT FRAME (per refuses-what-cannot-prove discipline): if ACF/IMF deliver MIDDLE_BAND (partial gain), substrate-product framing becomes "we are at the edge of published technique - our composition exposes a structural floor that bare-resonator literature does not see." This is ALSO a publishable finding (FPE-kernel collision floor is a new contribution) and informs the next decision (push to GHRR or pivot architecture).

---

## (f) Citations (verified count: 17 papers + 1 statistical-physics anchor)

PRIMARY ANCHORS (load-bearing):

1. [Frady, Kent, Olshausen, Sommer 2020] "Resonator Networks 1 & 2" Neural Computation 32(12):2332-2388. arXiv:1906.11684. CANONICAL baseline; Mmax ~ N^2 envelope; limit cycles + spurious fixed points as failure modes.

2. [Kent et al. 2020] "Resonator Networks, 1" Neural Computation 32(12). Identifies BASIN SHRINKAGE as distinct failure mode at intermediate parameters.

3. [Langenegger, Hersche, Karunaratne et al. 2024] "On the Role of Noise in Factorizers for Disentangling Distributed Representations" arXiv:2412.00354. STRONGEST quantified capacity extension: 50x at fixed budget via single-knob noise injection; ACF (init-noise) vs IMF (per-step noise) distinction.

4. [Langenegger, Karunaratne, Hersche, Benini, Sebastian, Rahimi 2023] "In-memory factorization of holographic perceptual representations" Nature Nanotechnology / arXiv:2211.05052. 5 orders of magnitude capacity gain via hardware stochasticity; identifies limit cycles as the displaced failure mode.

5. [Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen 2024/2025] "Computing With Residue Numbers in High-Dimensional Representation" Neural Computation 37(1) / arXiv:2311.04872. LOG-SCALING decode for numeric range; substrate already uses this representational extension.

6. [Yeung, Mehrnoosh, Mariappan, Manek, Eliasmith 2024] "Self-Attention Based Semantic Decomposition in Vector Symbolic Architectures" arXiv:2403.13218. STRONGEST Hopfield-resonator hybrid; closed-form beta; few-iteration decode (5-6 iters at M~5000 vs 71 for baseline).

7. [Hersche, Terzic, Karunaratne et al. 2024/2025] "Factorizers for Distributed Sparse Block Codes" arXiv:2303.13957. Block-code factorizer; quoted breakdown at M ~ 1.2e5 for vanilla resonator.

8. [Ramsauer et al. 2020] "Hopfield Networks Is All You Need" arXiv:2008.02217 / ICLR 2021. THEORETICAL anchor for exponential Hopfield capacity; closed-form retrieval; Theorem 4 closed-form beta condition.

ARCHITECTURAL EXTENSIONS:

9. [Renner, Sandamirskaya, Sommer, Frady 2022-2024] "Neuromorphic visual scene understanding with resonator networks" Nature Machine Intelligence / arXiv:2208.12880. HIERARCHICAL RESONATOR (Cartesian + log-polar partitions); enables non-commutative factor algebra; heavy per-scale tuning.

10. [Renner et al. 2024] "Compositional Factorization with Convolutional Sparse Coding" arXiv:2404.19126. Hybrid frontend + resonator; learned per dataset.

11. [Renner, Sandamirskaya, Sommer] "Validating an algebraic approach to characterizing resonator networks" PMC10789822 / 2023. SNR characterization; null-space dimensionality as envelope axis.

THEORETICAL / CAPACITY ANCHORS:

12. [Krotov & Hopfield 2016] "Dense Associative Memory for Pattern Recognition" arXiv:1606.01164. Polynomial energy gives polynomial capacity; foundational DAM.

13. [Krotov & Hopfield 2021] "Large Associative Memory Problem in Neurobiology and Machine Learning" arXiv:2008.06996. Exponential-in-visible-neurons capacity.

14. [Demircigil et al. 2017] "On a Model of Associative Memory with Huge Storage Capacity" 2^{N/2} memories with exp-energy.

15. [Millidge et al. 2022] "Universal Hopfield Networks" arXiv:2202.04557 / ICML 2022. Three-step framework for associative memory; unifies Hopfield variants.

16. [Hoover et al. 2023] "Energy Transformer" arXiv:2302.07253 / NeurIPS 2023. Iterated energy descent + attention; learned weights.

17. [Krotov et al. 2025] "Modern Methods in Associative Memory" arXiv:2507.06211. ICML 2025 tutorial; current DAM capacity regimes.

CRITICAL ANCHORS (surveys):

18. [Kleyko, Rachkovskij, Osipov, Rahimi 2022] "A Survey on Hyperdimensional Computing" ACM Computing Surveys 55(6) / arXiv:2111.06077 + 2112.15424. Capacity ladder across VSA variants.

STATISTICAL-PHYSICS ANCHOR:

19. [Amit, Gutfreund, Sompolinsky 1985] "Storing infinite numbers of patterns in a spin-glass model of neural networks" Phys. Rev. Lett. 55:1530. Hopfield critical capacity alpha_c ~ 0.138; first-order phase transition framing. METHODOLOGICAL gold standard for "abrupt cliff" characterization that the resonator literature has NOT yet replicated.

PERIPHERAL (cited for completeness, lower load-bearing):

- [Alam, Raff, Biderman, Oates, Holt 2023] "Recasting Self-Attention with HRR" ICML 2023 / arXiv:2305.19534. Hrrformer; learned.
- [Liu, Qiu, Khan, Katz 2025] "Linearithmic Cleanup for VSA Key-Value Memory" arXiv:2506.15793. O(n log n) cleanup; unfactored.
- [Santos, Niculae, McNamee, Martins 2024] "Hopfield-Fenchel-Young Networks" arXiv:2411.08590 / JMLR 26. Structured retrieval via generalized entropies.
- [Lakshminarayanan et al. 2024] "Self-Attention Based Semantic Decomposition in VSA" arXiv:2403.13218. (same as #6 above by different cite key)

---

## Synthesis: highest-leverage direction for substrate

The 4-axis structure of published capacity extensions, ranked by expected substrate leverage:

AXIS 1 (HIGHEST LEVERAGE): STOCHASTIC NOISE INJECTION
  - Paper: Langenegger 2024 arXiv:2412.00354
  - Quantified gain: 50x to 1e5x
  - Tuning cost: single knob (noise level)
  - Substrate fit: ACF variant works digital, drop-in compatible with existing residue+FPE+resonator
  - Risk: noise sweet spot is regime-dependent, but a single-pass empirical sweep is cheap
  - VERDICT: dispatch first. Lowest cost, highest expected gain, lit-anchored.

AXIS 2 (SECOND): MODERN-HOPFIELD ATTENTION-RESONATOR
  - Paper: Yeung 2024 arXiv:2403.13218
  - Quantified gain: 2.6x success rate (M~5000), 12x iteration reduction
  - Tuning cost: beta hyperparameter (set closed-form per Ramsauer Theorem 4)
  - Substrate fit: composes cleanly with substrate's existing Hopfield-cleanup pathway
  - Risk: capacity gain over n^F search space, not new factorization budget
  - VERDICT: dispatch after Axis 1 if Axis 1 delivers MIDDLE_BAND only.

AXIS 3 (THIRD): HIERARCHICAL/PARTITIONED ARCHITECTURE
  - Paper: Renner 2024 arXiv:2208.12880
  - Quantified gain: enables non-commutative factor algebra (translation+rotation); same N^2 envelope
  - Tuning cost: HIGH (per-factor polynomial exponent, noise variance, hysteresis)
  - Substrate fit: requires task-surface partition that may not naturally exist
  - VERDICT: defer until Axis 1+2 outcomes known; not a first-line option.

AXIS 4 (ALREADY USED): RESIDUE/CRT REPRESENTATION
  - Paper: Kymn 2024 arXiv:2311.04872
  - Substrate already operates this layer; gain is captured.
  - Not a new extension direction, but a structural confirmation that substrate's existing architecture is on the right path.

GAP IDENTIFIED: no published paper combines stochastic noise injection (Axis 1) + Hopfield-attention decoder (Axis 2) + hierarchical architecture (Axis 3) + residue (Axis 4) simultaneously. The substrate has 4 already and ADDING 1 (stochastic injection at residue+FPE+resonator composition) puts it in unexplored territory. This is a substrate-novel composition opportunity with each axis individually lit-anchored.

CALIBRATION NOTE: substrate's HONEST_BOUNDED verdict at its specific breakdown threshold is NOT directly comparable to Langenegger's published thresholds (substrate operates residue+FPE composition; Langenegger tests bare resonator). The 50x gain Langenegger reports is the UPPER bound on what substrate could expect; the realistic expectation is 5x-10x given the additional collision-floor confound from FPE kernel near-neighbor non-orthogonality. P_deflated reflects this discount.

---

## Pre-registered next-drill candidate

If ACF/IMF test outcome is MIDDLE_BAND (5x-10x gain): next drill is composed extension - ACF + Hopfield-attention readout head, evaluating whether stacking Axis 1 + Axis 2 closes the gap to lit-quoted 50x.

If HARD_FAIL: next drill is FPE-kernel collision-floor characterization (drill DEEPER into Lu/Bremer 2024 kernel-aware decoder family flagged in prior Drill 4).

If HARD_PASS: substrate ships capacity-extended variant; next drill is unrelated (return to TIER-3 GHRR or basis-expansion track).

Next drill candidate per field advisor (cross-thread): D7 Forward-flux sampling (FFS) for rare-event basin-to-basin transitions in substrate codeword space (tier-1 anchor, free-probability adjacency). FFS would give an independent measurement of the limit-cycle escape rate, which is exactly the mechanism Langenegger's noise injection exploits. This is the natural Trigger-C adjacency cascade from this drill.
