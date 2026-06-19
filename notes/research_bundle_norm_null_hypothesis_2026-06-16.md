# Research drill — bundle-norm-only null hypothesis for cardinality/quantifiers under binding and cleanup

Date: 2026-06-16
Drill type: targeted null-hypothesis lit-scan (3 parallel Sonnet sub-agents)
Cycle context: follow-up to `research_cardinality_fpe_rns_counting_accuracy_2026-06-16.md`; sharpens "how strong is the bundle-only baseline?" question for upcoming Phase-B counting experiments.

## (a) HEADLINE

The published bundle-only baseline IS analytically strong on raw-atom retrieval (Frady-Sommer SNR=sqrt(N/M), near-perfect at N=4096 for k<=50), BUT bundle-norm-as-cardinality-readout is an UNPOSED question in the canonical corpus (Plate, Kanerva, Gayler, Frady-Sommer, Schlegel, Kleyko surveys). Under binding (role-filler pairs), mechanism-theory predicts the norm signal degrades from linear-in-k to sqrt(k) random-walk noise — but Clarkson-Kleyko-Frady-Sommer 2023 (arXiv:2301.10352) gives formal bundle-only capacity bounds for set-cardinality estimation, so the "must add primitive" claim is under-evidenced in literature. Net: NULL is moderately strong on RAW-ATOM bundles; NULL is weak-to-neutral on BOUND bundles; no published head-to-head exists where FPE/RNS/NEF cleanly beats a bundle-norm baseline on a counting/quantifier task.

## (b) Cheap decisive test

Single substrate sweep at N=4096, k in {1, 2, 4, 8, 16, 32, 50}, M (codebook size) in {64, 512, 4096}, seeds={0..9}:

- T1 (raw bundle): build bundle = sum(random_atoms_k), measure (i) norm-CV = std(||bundle||) / mean(||bundle||), (ii) cardinality-recovery R^2 of k_hat vs k_true via norm-only linear regression, (iii) at-least-K accuracy via norm threshold.
- T2 (bound bundle): build bundle = sum(bind(role_i, filler_i) for i in 1..k), repeat (i)-(iii).
- T3 (cleanup-enumeration baseline): cosine-against-codebook, threshold at tau, count hits; measure same metrics + wallclock.

Decisive cut: if T1 norm-only beats T3 cleanup on accuracy AND wallclock at small-k, bundle-norm-only is operationally strong (null is hard to beat — added primitive must be justified by a DIFFERENT regime). If T2 norm-CV blows up to ~1/sqrt(k), binding washes norm and an explicit count primitive becomes architecturally necessary.

## (c) Falsifiable predictions

### HARD-PASS (strong-null confirmed; bundle-norm baseline is the operational primitive)
- T1 raw-atom: norm-only linear-regression R^2(k_hat, k_true) >= 0.97 for k in [1,32] at N=4096
- T1 at-least-K accuracy >= 0.95 with norm-threshold-only readout for k in [5,50]
- T2 bound-bundle: norm-CV remains <= 0.15 across k in [1,32]; R^2 still >= 0.90
- T1+T2 multi-seed std on accuracy <= 0.03 (concentration-of-measure regime confirmed)

### HARD-FAIL (weak-null; added primitive justified)
- T2 bound-bundle: R^2(k_hat, k_true) <= 0.50 OR norm-CV >= 0.40 (sqrt(k) random-walk confirmed)
- T1 multi-seed std on accuracy >= 0.10 (concentration violated, suggesting Plate-2003 sub-Gaussian regime broken)
- T3 cleanup-enumeration beats T1 norm-only by >= 15% absolute on at-least-K accuracy

### MIDDLE_BAND (partial-null; primitive gives marginal gain only)
- 0.15 < T2 norm-CV < 0.40 AND 0.50 < R^2 < 0.90: bundle norm partially survives binding; explicit FPE/RNS primitive provides additive but not necessary capability
- This is the most-likely empirical outcome (P_deflated ~ 0.40)

## (d) Cross-thread synthesis

Three independent angles converged on the same picture but emphasize different regimes:

| Sub-agent | Angle | Verdict on bundle-norm-NULL strength |
|---|---|---|
| A (Plate/Kanerva/Gayler foundational) | Capacity math (SNR=sqrt(N/k)) | Q1 SUPPORTS-strong-null on raw bundles; Q2 WARNING-weak-null on norm-as-readout (unposed); Q3 WARNING-weak-null Gayler omits counting; Q4 NEUTRAL Kanerva attribution slightly off |
| B (Kleyko surveys + Schlegel + cleanup noise) | Empirical capacity tables + Thomas Thm 8 norm-only bound | Q1 SUPPORTS-strong-null on membership; SUPPORTS-strong-null that exact-count IS a literature gap; Q3 WARNING-weak-null on cleanup-sigma-x-codebook-M-x-k joint curve (not published); Q5 NEUTRAL no published N=4096 multi-seed empirical sweep on bundle-norm tails |
| C (Bound bundles + FPE/RNS/NEF comparators) | Mechanism-theory + capacity-bound | Q1 WARNING-weak-null (no head-to-head exists); Q2 SUPPORTS norm-washed-by-binding via mechanism; Q4 SUPPORTS-orthogonal-pitch (RNS/FPE framed as resource-efficiency/continuous-scalar, not bundle-counting-fix); Clarkson 2023 ACTIVELY argues bundle suffices for cardinality (counter-evidence to "must add primitive") |

Two tensions to resolve empirically:

1. Mechanism-theory (Plate 1995, Frady 2018) predicts binding randomizes -> norm-cardinality degrades. Capacity-theory (Clarkson 2023) says bundle has formal cardinality-estimation capacity up to a derived N. Resolution: noise floor exists, but discriminability above it is what Clarkson bounds. Substrate question: at our N=4096 and operational k, is bound-bundle norm above noise floor?

2. No published head-to-head on counting benchmarks means "FPE beats bundle on counting" is a CONJECTURE in the field, not a demonstrated fact. The substrate is positioned to potentially produce the FIRST such head-to-head — which is either a publishable novelty (if FPE wins clearly) or a null result that strengthens Clarkson's bundle-suffices position.

Composes with prior research deliveries:
- `research_DEEP_DRILL_phase_B_cardinality_basis_orthogonal_validation_20260616_0746.md` claimed cardinality is orthogonal to binding basis. This drill SHARPENS that to: orthogonal in MECHANISM-theory but contested in CAPACITY-theory; empirically untested at substrate scale.
- `research_cardinality_fpe_rns_counting_accuracy_2026-06-16.md` set HARD-PASS thresholds for the substrate counting experiment. This drill adds the BASELINE-COMPARISON requirement: the experiment MUST include a bundle-norm-only baseline arm (T1/T2/T3 above), otherwise the FPE/RNS primitive's value is unmeasured.
- DECISION 142 tier-2 novel-composition existence-proof framing: a head-to-head bundle-vs-FPE on counting that produces a clear primitive-win would constitute additional tier-2 evidence; a null (bundle baseline wins or ties) would refine the tier-3 architecture decision (don't add the primitive yet).

## (e) Substrate-product implications

Per 11th USER-LOCKED rule (substrate-standalone capability first), the substrate-product positioning around cardinality/quantifier capability MUST be measured against the bundle-only null before claiming the added primitive (FPE/RNS) is required. Three product paths:

1. **NULL holds (HARD-PASS):** Substrate's basis already does cardinality via norm; no primitive addition needed; product positioning is "bundle algebra is sufficient for set-cardinality reasoning at high N" — a strong, low-architecture-cost claim. Risk: Clarkson 2023 already implies this in the lit, so novelty is reduced to empirical demonstration at N=4096 with the substrate's specific operator basis.

2. **NULL fails on bound bundles only (MIDDLE_BAND, most-likely):** Substrate basis handles raw-atom cardinality; structured counting (role-filler pairs) needs added primitive. Product positioning splits: "raw cardinality is basis-native; structured cardinality requires FPE register." This is the cleanest tier-3-architecture rationale and the strongest substrate-product story.

3. **NULL fails broadly (HARD-FAIL):** Bundle baseline weak even on raw atoms; concentration-of-measure violated; substrate has a deeper problem than missing a count primitive. Triggers cap_map row red for "high-N concentration in the substrate's specific basis" — would need free-probability / random-matrix follow-up.

Per [[feedback-no-papers-product-only]]: framing is internal-tracking-document only; no academic-paper artifact.

## (f) Citations (verified count: 15 across 3 sub-agent traces)

1. Plate, T.A. (1995) "Holographic Reduced Representations." IEEE Trans NN 6(3):623-641. doi:10.1109/72.377968. Foundational HRR; circular-convolution binding produces ~Gaussian components var ~ 1/D.
2. Plate, T.A. (2003) "Holographic Reduced Representations: Distributed Representation for Cognitive Structures." Univ Chicago Press. Capacity appendix for superposition memory.
3. Gayler, R.W. (2003) "Vector Symbolic Architectures Answer Jackendoff's Challenges." arXiv:cs/0412059. No explicit cardinality primitive; sets are bundled, decoded via cleanup.
4. Kanerva, P. (2009) "Hyperdimensional Computing." Cogn Comp 1:139-159. doi:10.1007/s12559-009-9009-8. Canonical D=10000; capacity linear in D; N/log(M) form is downstream restatement.
5. Frady, E.P., Kleyko, D., Sommer, F.T. (2018) "Theory of the superposition principle for randomized connectionist representations." arXiv:1707.01429. SNR=sqrt(N/M); Gaussian retrieval error CDF; channel capacity ~0.5 bit/neuron.
6. Frady, Kleyko, Sommer (2018 NeCo) arXiv:1803.00412. N < 8 M log(D/epsilon) bound for inner-product/WTA readout; CLT self-averaging.
7. Schlegel, K., Neubert, P., Protzel, P. (2022) "A comparison of vector symbolic architectures." arXiv:2001.11797 / Artif Intell Rev. 11 VSAs compared on bundle capacity, unbinding, combined ops; FHRR most dim-efficient; no counting benchmark; no norm-only readout.
8. Kleyko, D. et al. (2022) "Survey on Hyperdimensional Computing aka VSA, Part I." arXiv:2111.06077. Defers capacity to Frady-Sommer + Plate; no exact-count readout.
9. Kleyko, D. et al. (2022) Part II. arXiv:2112.15424. Mentions Bloom-filter + count-min-sketch via Sparse Block Codes; no empirical counting benchmark.
10. Thomas, A., Dasgupta, S., Rosing, T. (2021) "Theoretical Perspective on HDC." arXiv:2010.07426. Thm 8: norm-only bundle distortion O(s^2 mu); exact-count requires tighter mu. Thm 4: Hanson-Wright concentration at high d.
11. Clarkson, K., Kleyko, D., Frady, E.P., Sommer, F.T. (2023) "Capacity Analysis of Vector Symbolic Architectures." arXiv:2301.10352. **Counter-evidence to "must add count primitive":** formal capacity bounds for set-cardinality estimation using bundle alone, up to derived N.
12. Ganesan et al. (2021) "Learning with Holographic Reduced Representations." arXiv:2109.02157. Confirms linear-in-d capacity; projection step restores theoretical scaling.
13. Komer, B., Stewart, T.C., Voelker, A.R., Eliasmith, C. (2019) "A neural representation of continuous space using fractional binding." arXiv:1907.13321 / CogSci 2019. Spatial Semantic Pointers via FPE; framed as continuous-scalar capability, NOT bundle-counting-fix.
14. Kymn, C., Mazelet, S., Frady, E.P., Sommer, F.T., Olshausen, B. (2023) "Computing with residue numbers in high-dimensional representation." arXiv:2311.04872. RNS-HDC; logarithmic resource in dynamic range; framed as efficiency complement.
15. Hersche, M., Karunaratne, G., Cherubini, G., Sebastian, A., Benini, L., Rahimi, A. (2022) "Constrained Few-shot Class-incremental Learning." arXiv:2203.16588. C-FSCIL uses cosine-similarity to mean-prototypes, NOT raw bundle norm; operational pattern in the field.

## Calibration

- Raw P(bundle-norm baseline survives bound regime at substrate N=4096): ~0.55 mechanism + ~0.65 Clarkson capacity = ~0.60 blended.
- Deflated by 0.20 (lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]]): **P_deflated = 0.40**.
- Capped at 0.50 (novel-synthesis ceiling); no additional cap binds.
- HARD-PASS / HARD-FAIL thresholds pre-registered above.

## Top 2 risks for "null is too strong" (added primitive doesn't beat baseline)

1. **Clarkson-2023 capacity bound has already formalized bundle-cardinality sufficiency.** If the substrate's N=4096 sits comfortably inside Clarkson's derived capacity regime, the added FPE/RNS primitive could turn out to give zero advantage on counting accuracy — only resource-efficiency wins (which is the Kymn 2023 pitch). Mitigation: include T1/T2/T3 baseline arms in the Phase-B experiment so the primitive's value is measured, not assumed.

2. **Cleanup-noise is the operational binding constraint, not the missing primitive.** Per Thomas 2021 Thm 8 + Frady 2018 Phi^(D-1) factor, the joint (cleanup-sigma, codebook-M, k) interaction is the under-published regime — and may dominate the counting-task error budget. If so, both bundle-norm AND FPE perform poorly together because cleanup-noise floors them both; the primitive doesn't beat baseline because the cleanup stage is the bottleneck. Mitigation: sweep cleanup-sigma orthogonally in the Phase-B design; if T1/T3 both degrade similarly under cleanup noise, the primitive question is moot and the cap_map row moves to "cleanup-noise robustness."

## Next-drill candidate field

`sparse-coding-compressed-sensing` (Tier-1b adjacent to free-probability) — Donoho/Candes-Tao phase-transition framework gives sharp predictions for when k_recovered = k_true above noise floor as a function of (N, k, cross-talk variance). This is the right framework to convert the Phase-B cheap-decisive-test into a pre-registered phase-transition prediction. Specifically: the L1-recovery vs L2-norm-only readout dichotomy in compressed sensing maps directly onto the cleanup-enumeration vs bundle-norm dichotomy in T1/T3.

Per role contract — no cap_map modifications here; this note is read by Strategy/Exp-Dev for Phase-B experiment design.
