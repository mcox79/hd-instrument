# Research: Cardinality / counting / quantifier accuracy in FPE and RNS-HDC literature

Date: 2026-06-16
Dispatch: lit-scan from cardinality-primitive direction inquiry
Sub-agents: 3 parallel Sonnet lit-scans (FPE/RNS, SSP-lineage, benchmarks)
Lit-scan calibration penalty applied: P-estimates deflated 0.15-0.25; novel-synthesis cap = 0.50

## (a) HEADLINE

The FPE / RNS-HDC literature documents **factorization capacity** at high vector dim (Kymn et al. 2023/2024 arXiv:2311.04872; Kent et al. 2020 arXiv:1906.11684) and **continuous magnitude / position decoding** (Komer 2019/2020; SSP-SLAM 2023), but it does NOT report **exact-count RMSE or quantifier-style accuracy at N=4096** anywhere. Only ONE prior VSA-specific cardinality probe exists (Alam et al. 2023 arXiv:2312.15310, subitizing with HRR loss). The cleanest external benchmark for an FPE/RNS counting primitive is the **Steinert-Threlkeld & Szymanik quantifier-RNN suite** (at-least-k / exactly-k / majority, public synthetic generators), with **bAbI Task 7** as a saturated reference floor (EntNet ~100%, vanilla LSTM ~80%).

The gap is real but narrow: adding an FPE/RNS cardinality primitive to a substrate is genuinely uncovered territory for an EXACT-COUNT / QUANTIFIER axis, while bundling-only capacity bounds (Kleyko et al. 2023 arXiv:2301.10352; Schlegel et al. 2022 arXiv:2001.11797) constrain the bundle-norm-only baseline.

## (b) Cheap decisive test

**Two-tier test, both runnable on a CPU smoke under ~30 min:**

1. **Quantifier-RNN suite** (Steinert-Threlkeld github.com/shanest/quantifier-rnn-learning): generate ~5K examples each of at-least-k, exactly-k, majority. Test substrate's FPE/RNS cardinality primitive vs bundle-norm-only baseline. Multi-seed n=5.
2. **bAbI Task 7 1K split** (canonical counting): tiny, public, known floor.

Both tests are pre-existing public benchmarks — defensible against ad-hoc-synthetic critique (per [[feedback-no-papers-internal-tracking-documents-only]] still applies; this is internal tracking, not paper publication, but external benchmarks remove a confound class).

## (c) Falsifiable predictions

### HARD-PASS thresholds (must hit to claim cardinality primitive is load-bearing)

- **Exact-count RMSE at N=4096:** substrate FPE/RNS primitive achieves **RMSE <= 0.5** on uniform-cardinality range [1, 20] with bundle-size <= 12, vs bundle-norm-only baseline RMSE >= 1.5. Required gap: **>=3x**.
- **Quantifier accuracy at N=4096:** substrate primitive achieves **>= 0.90** on at-least-k (k=3,5,7) and **>= 0.80** on exactly-k (k=3,5), with bundle-norm-only baseline **<= 0.65** on the same items. Required gap: **>=15 pp** on at-least-k.
- **Multi-seed variance n=5:** seed-to-seed std on RMSE **<= 0.15** (tight); std on quantifier accuracy **<= 0.03**.
- **bAbI T7 1K floor:** substrate primitive reaches **>= 0.85** (above vanilla LSTM 0.80, well below EntNet 1.00 — this is a sanity floor, not novelty).

### HARD-FAIL thresholds (any one triggers refutation)

- Exact-count RMSE > 1.0 at N=4096 with bundle <= 12 (no separation from baseline).
- Quantifier majority/exactly-k accuracy < 0.65 (below trivial-majority baseline).
- Multi-seed std on RMSE > 0.40 (wide, suggests non-self-averaging / pathological regime).
- bAbI T7 < 0.65 (below vanilla baseline, indicates primitive harms rather than helps).
- Cleanup interaction: when cleanup-noise > 0.30, exact-count accuracy collapses to bundle-norm-only floor (primitive does no work above cleanup limits — adjacent to [[feedback-dont-dismiss-adjacent-methods]] warning that cleanup can be the binding constraint).

### Calibrated P estimates (deflated 0.20 per protocol)

- P(quantifier at-least-k HARD-PASS at N=4096) = **0.40** (deflated from naive 0.60). Adjacent: LSTMs known to struggle on non-universal quantifiers (Steinert-Threlkeld 2019); FPE phase encoding has the right algebraic shape, but no precedent at exactly this configuration.
- P(exact-count RMSE HARD-PASS) = **0.30** (deflated from 0.50). FPE magnitude decoding is documented for continuous positions (SSP-SLAM RMSE 5.76 +/- 3.70 at d=181 trajectory), but exact-integer RMSE at the sub-unit level is harder.
- P(multi-seed variance tight, std <= 0.15) = **0.50** (deflated from 0.70). Crosstalk-noise theory (Frady & Sommer 2018) implies tight concentration at large D, but empirical confirmation at N=4096 is not in the scanned literature.
- P(both HARD-PASS thresholds met simultaneously, joint) = **0.18** (capped well below novel-synthesis cap 0.50).
- P(at least one HARD-FAIL) = **0.55** (priors favor refutation given the calibration discipline; this is healthy).

## (d) Cross-thread synthesis

- **vs DECISION 142 strategic direction** (substrate_director_session_2026_06_15_16): adding a cardinality primitive is a Phase B "GROW BASIS" candidate — extends substrate's operator basis beyond current 38 binders to include a counting-typed operator. Aligns with USER's scale/basis-intuition empirical validation (corr(bundle(a,b),c) Tier-2 was a basis-gap close; cardinality would be a Tier-2 basis-gap candidate of a different signature class — quantifier-typed, not relation-typed).
- **vs DECISION 100 substrate-product positioning 15-claim** (substrate_director_session_2026_06_15_DAY_DECISION_100): would extend the 4 non-additive op classes by introducing a 5th (numerosity / quantifier closure). Tier-2 claim 5 (operator-class-invariant 4-gate pre-check) would need a 5th class spec.
- **vs Goal 4 (LLM-class language mastery, aspirational)** (substrate_USER_decisions_2026_06_13): quantifiers are a known LSTM weak point (Steinert-Threlkeld); a counting primitive is on the path to genuine language-foundation extension via FraCaS-style decidable inference. Composes with the math-to-language bridge (status_log 2026-06-13: type-theoretic compositional semantics B1 highest payoff bridge).
- **Field-coverage**: this drill is NOT in the 22 fields scored by research_field_advisor — closest neighbors are `coding-theory` (44%, 9 drills, adjacent) and `inference` (10%, 10 drills, saturated). It's effectively a SCOPE-EXPANSION drill into a new field "vector-symbolic-cardinality" with drill_count=1. Trigger B (scope-expansion cadence) applies.
- **Adjacency warning** (per [[feedback-dont-dismiss-adjacent-methods]]): cleanup noise was flagged in TWO independent sub-agent reports as the binding constraint at high D. Do not assume the primitive's contribution is additive on top of cleanup — pre-register a cleanup-noise stress sweep, do not dismiss.

## (e) Substrate-product implications

- **Internal tracking doc framing** (per [[feedback-no-papers-internal-tracking-documents-only]]): if HARD-PASS, this extends substrate-on-its-own claim set from "non-additive operator algebra" toward "quantifier-typed operator closure" — a categorical capability LLMs cannot expose with shape-guarantees.
- **USER 11th rule**: substrate-standalone capability MUST be measured first (cardinality primitive accuracy in absolute terms). Only after standalone HARD-PASS do we discuss LLM-comparison (LSTMs at ~0.65 on non-universal quantifiers per Steinert-Threlkeld).
- **Operator-self-model extension** (DECISION 100 Phase 4a): a 5th non-additive class would need a CHTV-verified signature in the self-model. Pre-register signature type before measurement to avoid post-hoc gerrymandering.
- **Cap_map row candidate**: if the HARD-PASS thresholds in (c) hit, it justifies opening a new row "cap_cardinality_primitive" with anchor = quantifier-RNN suite + bAbI T7 1K floor. Strategy decides whether to bump.

## (f) Citations (verified count: 16)

### FPE/RNS-HDC core
1. Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen (2023/2024). "Computing with Residue Numbers in High-Dimensional Representation." arXiv:2311.04872 / Neural Computation 37(1):1. Defines RHDC; factorization capacity C(4096) > 2e6 reported, but NOT exact-count RMSE at N=4096.
2. Frady, Kleyko, Kymn, Olshausen, Sommer (2021). "Computing on Functions Using Randomized Vector Representations" (VFA). arXiv:2109.03429.
3. Frady & Sommer (2018). "A Theory of Sequence Indexing and Working Memory in Recurrent Neural Networks." arXiv:1803.00412 / Neural Computation 30(6):1449. Closed-form crosstalk-noise theory implies tight concentration at large D (theoretical, not empirical-seed).
4. Frady, Kent, Olshausen, Sommer (2020). "Resonator Networks, 1." Neural Computation 32(12):2311.
5. Kent, Frady, Sommer, Olshausen (2020). "Resonator Networks, 2: Factorization Performance and Capacity." arXiv:1906.11684. Capacity-vs-D scaling.
6. Anonymous (2024). "Improved Cleanup and Decoding of Fractional Power Encodings." arXiv:2412.00488. d=1024 FHRR; "failure fraction" not RMSE; CLE+MLE iterative cleanup beats baselines.

### SSP / Eliasmith-Stewart-Komer lineage
7. Komer, Stewart, Voelker, Eliasmith (2019). "A neural representation of continuous space using fractional binding." CogSci 2019.
8. Lu, Voelker, Komer, Eliasmith (2019). "Representing spatial relations with fractional binding." CogSci 2019. Spatial relations only, NOT cardinality.
9. Komer (2020). "Biologically Inspired Spatial Representation." PhD thesis, U. Waterloo. https://uwspace.uwaterloo.ca/handle/10012/16430
10. Voelker, Blouw, Choo, Dumont, Stewart, Eliasmith (2021). "Simulating and Predicting Dynamical Systems With Spatial Semantic Pointers." Neural Computation 33(8):2033.
11. Dumont, Furlong et al. (2023). "SSP-SLAM." Frontiers in Neuroscience. d=181, trajectory RMSE 5.76 +/- 3.70 (position, not cardinality).

### Capacity bounds (bundle-norm-only baseline)
12. Schlegel, Neubert, Protzel (2022). "A comparison of Vector Symbolic Architectures." arXiv:2001.11797.
13. Clarkson, Gayler, Levy et al. (2023). "Capacity Analysis of Vector Symbolic Architectures." arXiv:2301.10352. Bundling cap ~899 dim for 20 bundled / 1000 distractors at 98% error-free.

### Benchmarks
14. Weston et al. "Towards AI-Complete QA: A Set of Prerequisite Toy Tasks" (bAbI). Task 7 (counting): EntNet ~100%, DNC 99.4%, vanilla LSTM 80.4%.
15. Steinert-Threlkeld & Szymanik (2018/2019). Quantifier-RNN suite. https://github.com/shanest/quantifier-rnn-learning . LSTMs learn quantity + monotonicity universals fast; non-universal quantifiers slower (the gap a substrate primitive could close).
16. Alam et al. (2023). "Towards Generalization in Subitizing with Neuro-Symbolic Loss using Holographic Reduced Representations." arXiv:2312.15310. THE ONLY direct VSA-cardinality precedent; MNIST-derived subitizing; HRR loss improves OOD vs CNN.

### Adjacent (not load-bearing for this drill but logged)
- Steinert-Threlkeld papers on "most" semantics (arXiv:1904.02734) and quantifier conservativity (arXiv:1809.05733).
- NumGLUE (arXiv:2204.05660) — multi-task confound, NOT recommended as primary benchmark.

## Top 2 risks

1. **Cleanup-noise is the binding constraint, not the primitive.** Two independent sub-agent reports flag cleanup as the dominant capacity limit at high D. If cleanup dominates, adding an FPE/RNS counting primitive looks load-bearing in low-noise regime but collapses to bundle-norm-only in production-realistic noise. **Mitigation:** pre-register a cleanup-noise stress sweep (sigma in {0.05, 0.10, 0.20, 0.40}); HARD-FAIL if primitive's gap over baseline disappears at sigma=0.20.
2. **Benchmark saturation refutes novelty axis.** bAbI T7 is saturated (EntNet 100%); even strong substrate result there proves only that the primitive is functional, not novel. Quantifier-RNN suite is the only externally-validated axis where novelty can be claimed, and even there the SOTA LSTM baseline is unclear (Steinert-Threlkeld reports LSTM struggles on non-universal but doesn't give a clean accuracy table per quantifier class). **Mitigation:** before running, reproduce the LSTM baseline on the chosen quantifier classes to nail down the actual reference floor. If LSTM baseline already > 0.85 on at-least-k, the primitive's headroom is thin and the test loses decisiveness.

---

Pre-registered: this note is internal tracking per USER 10th rule, not a publication artifact. Cap_map bump decision belongs to Strategy, not Research.
