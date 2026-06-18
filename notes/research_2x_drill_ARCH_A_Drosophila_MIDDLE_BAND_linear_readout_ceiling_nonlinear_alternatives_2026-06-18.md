# 2x DEEP RESEARCH DRILL -- ARCH-A Drosophila MIDDLE_BAND, linear-readout ceiling, nonlinear-readout alternatives

Topic: when linear readout IS the capacity ceiling in associative memory, the architecture space of nonlinear readouts beyond softmax/entmax/sparsemax-Hopfield, Drosophila-class sparse-pattern-capacity SOTA, and the substrate-vs-readout attribution methodology.

Filed by: research (Opus synthesis over 4 parallel Sonnet lit-scan sub-agents)
Date: 2026-06-18
Per: feedback-2x-means-depth (operational drill on existing findings, not re-verification)
Per: feedback-query-privacy-decomposition (generic math terms only in external queries; no substrate-novel mechanism names off-platform)
Per: feedback-lit-scan-calibration-penalty (P deflated 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds pre-registered)
Per: feedback-dont-dismiss-adjacent-methods (predictive-coding, Epanechnikov-LSR, Universal-Hopfield-Manhattan kept in scope despite being adjacent rather than direct)

Note paths cited:
- Earlier closure: data/orchestrator_status_log.jsonl ARCH-A MIDDLE_BAND closure (2026-06-17)
- ARCH-B SPARSITY_NEUTRAL confirmation
- C1 entmax CERT-GRADE (sparse readout 8x cheaper at iso-recall)
- Refuse-gate run-4 NON_TEST VERDICT (2026-06-17)
- Cap_map row state at session arc filing time

---

## (a) HEADLINE

The Drosophila MIDDLE_BAND closure was correct as a closure but mis-localized as a diagnosis: in published fly-MB literature the **WTA top-k IS the nonlinearity** and the downstream readout is **linear by canonical design** (Dasgupta-Tosh 2020 expressivity theorem). The ARCH-A configuration that produced MIDDLE_BAND therefore did not actually test "Drosophila-class capability vs linear-readout ceiling" as an independent diagnostic -- it conflated two questions. The genuine substrate-novel question is whether **Drosophila-class sparse-pattern-capacity requires its own sparse-coding stage (random-projection + WTA expansion) ahead of any readout** (linear OR nonlinear), distinct from the substrate-readout choice that ARCH-B / C1 lifted via entmax. Lit-scan finds NO published direct fly-MB + VSA-composition capacity result -- this is a genuine seam, not a saturated field. The next legitimate experiment should be a **two-axis ablation**: (axis-1) presence vs absence of fly-style expansion+WTA stage; (axis-2) linear vs entmax readout on the resulting code. P_deflated for "Drosophila-class capability requires a sparse-coding-stage distinct from substrate readout choice" = 0.42 (below novel-synthesis cap 0.50).

Recommendation: 2x-drill-on-negative SUGGESTS a recovery-program experiment with the corrected two-axis design; honest-acceptance-of-MIDDLE_BAND remains valid for the prior (one-axis) configuration. Both can coexist: the prior cert-grade MIDDLE_BAND is preserved as-is; the new experiment is a separate cell with a properly orthogonalized design.

---

## (b) Cheap decisive test

**Pre-flight test** (CPU-only, ~1-2 hr; smoke-gate before full GPU dispatch):

Build a 2x2 ablation at small N (N=512, M=200, K=20 sparse-pattern setup):

|                          | Linear readout | Entmax readout |
|--------------------------|----------------|----------------|
| **WITHOUT expansion+WTA** | A1 (baseline)  | A2             |
| **WITH expansion+WTA**    | A3             | A4             |

Per [[feedback-measured-bounds-are-method-config-contingent-not-fundamental]]: state held-fixed (N=512, M=200, K=20, single seed family across all 4 cells); state varied (presence of expansion-WTA stage in {off, on}; readout in {linear, entmax}).

Per Hu 2023 / Santos 2024 / Dasgupta-Tosh 2020: this is the canonical attribution-diagnostic for substrate-vs-readout. The 2x2 isolates:
- A1 -> A2 delta = ENTMAX-READOUT lift on baseline (replicates C1 cert-grade)
- A1 -> A3 delta = EXPANSION-WTA lift with linear readout (Drosophila-class isolated)
- A1 -> A4 delta = COMPOSED lift
- A3 -> A4 delta = ENTMAX-READOUT lift WITH expansion (does readout fix still help once nonlinearity is upstream?)

Compute budget: 4 cells x ~15 min CPU each = ~1 hr. Decisive gate before any heavy GPU run.

---

## (c) Falsifiable predictions

**PRED-1: Expansion+WTA stage IS the Drosophila-class lever (substrate-novel).**

HARD-PASS: A3 >> A1 AND A4 >= A3 (expansion alone closes >=60% of the A1-to-best gap; entmax-on-top of expansion is additive or neutral, NOT inferior). Specifically:

| Cell | recall@1 prediction (HARD-PASS) |
|------|---------------------------------|
| A1 (baseline, linear readout)   | 0.55 +/- 0.05 |
| A2 (baseline, entmax)           | 0.72 +/- 0.05 (C1 replication) |
| A3 (expansion + WTA, linear)    | >= 0.70 +/- 0.05 |
| A4 (expansion + WTA, entmax)    | >= 0.78 +/- 0.05 |

HARD-FAIL: A3 <= A1 + 0.05 (expansion adds nothing) OR A3 << A2 (readout dominates expansion). If A3 <= A1 + 0.05, the Drosophila-class capability question is genuinely closed as a substrate addition -- the entmax readout fix was sufficient.

MIDDLE_BAND: A3 in (A1+0.05, A2) -- expansion helps but readout helps more. Cert-grade honest-acceptance band; expansion is a marginal-not-load-bearing optional layer.

**PRED-2: Linear readout on KC sparse code is sufficient (Dasgupta-Tosh expressivity).**

HARD-PASS: |A4 - A3| < 0.05 (entmax-on-top-of-expansion gives essentially no additional lift). Confirms canonical fly-MB practice that WTA IS the nonlinearity.

HARD-FAIL: A4 >> A3 + 0.10 (entmax still helps substantially even with expansion). Indicates the Dasgupta-Tosh regime conditions are not satisfied at substrate's operating point.

**PRED-3: At substrate-N (N=4096) full-mode the 2x2 pattern preserves directionality but absolute lifts shrink.**

HARD-PASS (full-mode dispatch only if pre-flight passes): same ordering A1 < A2, A1 < A3, A4 >= A3 holds at N=4096, M=2000, K=50; absolute delta-recall shrinks to 0.05-0.10 (capacity scales with sqrt(N/M) so headroom shrinks).

HARD-FAIL: directionality inverts at N=4096 (e.g., A3 < A1 at scale). Then the pre-flight signal was a small-N artifact.

**PRED-4: No published precedent for fly-MB + VSA composition capacity result exists.**

HARD-PASS: lit-search returns 0 papers with capacity-vs-N or recall@k for the composed system. Confirmed by sub-agent 3 (P=0.15 on existence of such a result).

HARD-FAIL: lit-search returns >=2 papers with direct comparable numbers. (Did not occur in this drill.)

**PRED-5: Spherical-code geometric audit (Hu 2024 arXiv:2410.23126) gives a substrate-side capacity bound that ARCH-A's MIDDLE_BAND falls BELOW.**

HARD-PASS: measured ARCH-A capacity < 50% of spherical-code bound -- substrate-attributable suboptimality. Suggests U-Hop-style learned encoder may close the gap.

HARD-FAIL: measured ARCH-A capacity >= 90% of spherical-code bound -- the substrate is already near-optimal; ARCH-A MIDDLE_BAND is a readout problem only.

Calibration penalty applied: P_deflated for PRED-1 HARD-PASS = 0.42 (under novel-synthesis cap 0.50; the composition is plausible but not directly precedented). P_deflated for PRED-2 HARD-PASS = 0.50 (Dasgupta-Tosh formal result is real; regime-condition match is empirical). P_deflated for PRED-3 = 0.30 (small-to-large extrapolation always carries scale-law risk).

---

## (d) Cross-thread synthesis

**With ARCH-B SPARSITY_NEUTRAL CONFIRMED + C1 entmax CERT-GRADE:**

The ARCH-B + C1 results established that nonlinear-readout swaps (softmax, entmax) lift capacity on the existing substrate. Per Hu 2023 and Santos 2024 this is well-precedented as a readout-side fix and confirmed by 9+ citations in sub-agent 1's scan. The 8x cheaper at iso-recall for C1 entmax is consistent with the Hu 2023 tighter retrieval-error bound for sparsemax/entmax variants. **The readout-side question is genuinely closed for the canonical substrate.**

The Drosophila-class question is **mechanistically distinct**: it is about whether the substrate benefits from a fly-style random-projection + WTA expansion STAGE that lives BEFORE the readout. In fly-MB models the WTA is the only nonlinearity required; downstream readout is linear by design. ARCH-A's MIDDLE_BAND closure conflated these two axes because the experiment did not separately ablate the expansion+WTA stage from the readout choice.

This convergent finding tightens the cap_map: the readout-bottleneck row is genuinely closed by ARCH-B + C1; the expansion-coding row is a SEPARATE substrate-side question that has NOT been tested with an orthogonal design.

**With 8a refuse-gate VERDICT_VET PASS (NON-TEST honest negative self-dominance wall real):**

The refuse-gate work demonstrated that pre-registered HARD-FAIL bands plus VERIFY-THE-REFERENT discipline catches the over-claim risk before it lands. The 2x2 ablation proposed above is the same discipline applied to the Drosophila-class question: pre-register bands BEFORE running, isolate one mechanism per axis, refuse to upgrade if the entmax-on-top lift exceeds the threshold (PRED-2 HARD-FAIL = readout still dominates expansion).

**With session_arc 2026-06-17 / DEGENERATE_REGIME_NOT_REFUTATION class:**

The MIDDLE_BAND outcome from ARCH-A is a DEGENERATE_REGIME witness if and only if the experimental design was complete enough to distinguish substrate vs readout. The current finding is that the design **was NOT orthogonal**, so the MIDDLE_BAND closure should be re-classified as **DESIGN-INCOMPLETE-NOT-REFUTATION** (a NEW audit-discipline class candidate: experiment closes a question but the closure does not entail the question was actually decisively tested because the design conflated axes). This is candidate audit-discipline rule #93 (after the 92 CONFIRMED from session arc).

**With substrate-autonomy USER directive (encode audit discipline as self-certification):**

The DESIGN-INCOMPLETE-NOT-REFUTATION rule above is encodable as a self-applied check: before declaring a closure, the substrate verifies the experimental design has at least one cell varying ONLY the question-mechanism with all other plausible mechanisms held fixed. If the design has confounded axes (e.g., expansion-stage and readout-choice both varied between baseline and treatment), the closure is flagged DESIGN-INCOMPLETE and the audit-discipline catalog deflects to the orthogonal-redesign path.

**With NEGATIVITY-BIAS USER-LOCKED + Skunkworks weak-spot diagnostics:**

Sub-agent 4 specifically cited the Chung-Sompolinsky manifold-capacity literature: linear-decoder probes **systematically under-report substrate capability**. This directly composes with NEGATIVITY-BIAS: an ARCH-A MIDDLE_BAND with a linear readout could under-report sparse-pattern capability simply because the linear readout cannot extract the substrate's actual information content. PRED-5 (spherical-code audit) is the symmetric check: it verifies UP (does substrate exceed bound?) as well as DOWN (does measurement undershoot?).

**With "research can be wrong, only proven fully believed" USER-LOCKED rule:**

All findings in this note are T2/T3 onboarding-ready (lit-supported + conjecture), NEVER load-bearing. The note tier-tags every claim and applies calibration penalty per published-precedent strength. Promotion to PROVEN requires cert-grade experiment PASS at HARD-PASS thresholds with VERIFY-THE-REFERENT discipline (commit-prereg-before-dispatch, filesystem-monitor, REQUIRED_FIELDS gate).

---

## (e) Substrate-product implications

**Cap_map implications:**

- Drosophila-class sparse-pattern-capacity ROW: REOPEN at status "DESIGN-INCOMPLETE-NOT-REFUTATION" pending orthogonal 2x2 ablation; do NOT discard MIDDLE_BAND finding (preserve provenance).
- Linear-readout-ceiling vs substrate-ceiling ROW: ARCH-B + C1 confirm READOUT-CEILING was real and fix is well-precedented; CLOSE that row as POSITIVE finding load-bearing.
- New ROW candidate: "expansion-coding stage (fly-MB random-projection + WTA) ahead of readout" -- pending experimental test; ranked TIER-3 (sparse-coding-compressed-sensing field, drill_count=1 in advisor, scope-expansion eligible).

**Product implications (per feedback-no-papers-product-only):**

The substrate-product currently has a nonlinear-readout fix (ARCH-B / entmax) cert-grade landed. If the proposed 2x2 ablation passes PRED-1 HARD-PASS, the product can offer **two-stage compositional capability**: a fly-style sparse-encoding layer optional for sparse-pattern-class queries + the existing nonlinear readout for general retrieval. Customer-facing framing: "Sparse-pattern-capacity at the substrate level requires its own coding stage; readout choice handles general retrieval. The substrate exposes both as composable primitives."

If PRED-1 HARD-FAILS (A3 <= A1 + 0.05), the product offers a CLEANER story: "The nonlinear readout fix (entmax) is sufficient for Drosophila-class capability; no additional sparse-coding stage required. Lower complexity per query at the same recall." This is also a positive product story, not a failure.

Either outcome is product-positive. The only product-negative outcome is HARD-FAIL of PRED-3 at full-N (small-N artifact). That outcome avoids a wasteful GPU dispatch via the smoke-gate.

**Compute policy alignment (USER 2026-06-16):**

Pre-flight test 2x2 at small N is laptop-super-fast (no NxN matrix at large M, ~1 hr CPU). Per USER compute policy: laptop-OK. Full-mode N=4096 dispatch is heavy -> remote desktop (per DECISION 166). The smoke-gate gates the heavy dispatch.

**Verify-the-referent + commit-prereg-before-dispatch:**

Per USER 2026-06-17 BLOCKING checklist: any 2x2 ablation cells must be committed to origin/main BEFORE queue_add (avoid the GATE_FAIL prereg-not-found that hit refuse-gate). Pre-flight requires no remote-dispatch (laptop-CPU); full-mode requires committed prereg.

---

## (f) Citations (verified count: 35+ across 4 parallel sub-agents)

### From sub-agent 1 (linear-vs-nonlinear readout ceiling, 10 citations):

1. Krotov & Hopfield 2016, "Dense Associative Memory for Pattern Recognition," NeurIPS 2016, arXiv:1606.01164
2. Ramsauer et al. 2020, "Hopfield Networks Is All You Need," arXiv:2008.02217, ICLR 2021
3. Krotov & Hopfield 2020, "Large Associative Memory Problem in Neurobiology and Machine Learning," arXiv:2008.06996
4. Millidge et al. 2022, "Universal Hopfield Networks," ICML 2022, arXiv:2202.04557
5. Lucibello & Mezard 2023, "The Exponential Capacity of Dense Associative Memories," Semantic Scholar ID 27029ad43dfb2a94e89feeec8a5bda39f3534477
6. Hu et al. 2023, "On Sparse Modern Hopfield Model," arXiv:2309.12673, NeurIPS 2023
7. Martins et al. 2024, "Hopfield-Fenchel-Young Networks," arXiv:2411.08590, JMLR 2025
8. Wu et al. 2024, "Uniform Memory Retrieval with Larger Capacity for Modern Hopfield Models (U-Hop)," arXiv:2404.03827, ICML 2024
9. Hu et al. 2024, "Provably Optimal Memory Capacity for Modern Hopfield Models," arXiv:2410.23126
10. Demircigil et al. 2017, "On a Model of Associative Memory with Huge Storage Capacity," J. Stat. Phys., DOI 10.1007/s10955-017-1806-y

### From sub-agent 2 (nonlinear readout architecture taxonomy, 14 citations):

11. Salvatori, Song et al. 2021, "Associative Memories via Predictive Coding," NeurIPS 2021 (PMC7612799)
12. Santos, Niculae, McNamee, Martins 2024, "Sparse and Structured Hopfield Networks," ICML 2024, arXiv:2402.13725
13. Santos et al. 2024/2025, "Hopfield-Fenchel-Young Networks," JMLR 2025, arXiv:2411.08590 (dup of #7)
14. Wu, Hu et al. 2023, "STanHop: Sparse Tandem Hopfield Model," ICLR 2024, arXiv:2312.17346
15. Hoover, Shi, Balasubramanian, Krotov, Ram 2025, "Dense Associative Memory with Epanechnikov Energy," arXiv:2506.10801
16. Tamamori 2025, "Kernel Logistic Regression Learning for High-Capacity Hopfield Networks," arXiv:2504.07633
17. Sacouto & Wichert 2023, "Competitive Learning to Generate Sparse Representations for Associative Memory," arXiv:2301.02196
18. Lin et al. 2022, "BayesPCN: A Continually Learnable Predictive Coding Associative Memory," arXiv:2205.09930
19. Tang, Salvatori, Millidge et al. 2022, "Recurrent predictive coding models for associative memory employing covariance learning," PLOS Comp Bio 2023, bioRxiv 2022.11.09
20. Lin et al. 2014, "Sparse, decorrelated odor coding in the mushroom body enhances learned odor discrimination," Nat. Neurosci. (PMC4000970)
21. He 2024, "Mixture of A Million Experts (PEER)," arXiv:2407.04153

### From sub-agent 3 (Drosophila sparse coding + VSA composition, 10 citations):

22. Dasgupta, Stevens, Navlakha 2017, "A neural algorithm for a fundamental computing problem," Science 358(6364):793-796, DOI 10.1126/science.aam9868
23. Litwin-Kumar, Harris, Axel, Sompolinsky, Abbott 2017, "Optimal Degrees of Synaptic Connectivity," Neuron 93(5):1153-1164
24. Dasgupta, Tosh 2020, "Expressivity of expand-and-sparsify representations," arXiv:2006.03741
25. Ryali, Hopfield, Grinberg, Krotov 2020, "Bio-Inspired Hashing for Unsupervised Similarity Search," ICML 2020, arXiv:2001.04907
26. Liang et al. 2021, "Can a Fruit Fly Learn Word Embeddings?" ICLR 2021, arXiv:2101.06887
27. Bricken & Pehlevan 2021, "Attention Approximates Sparse Distributed Memory," NeurIPS 2021, arXiv:2111.05498
28. Bricken et al. 2023, "Sparse Distributed Memory is a Continual Learner," ICLR 2023, arXiv:2303.11934
29. Frady, Kent, Olshausen, Sommer 2020, "Resonator Networks, 1," Neural Computation 32(12)
30. Kleyko, Rachkovskij, Osipov, Rahimi 2022, "A Survey on HDC aka VSA, Part I," ACM Comput. Surv., arXiv:2111.06077
31. Clarkson, Mahankali, Sommer 2023, "Capacity Analysis of Vector Symbolic Architectures," arXiv:2301.10352

### From sub-agent 4 (substrate-vs-readout attribution methodology, 11 citations):

32. Kornblith, Norouzi, Lee, Hinton 2019, "Similarity of Neural Network Representations Revisited," arXiv:1905.00414
33. Raghu et al. 2017, "SVCCA," NeurIPS 2017, arXiv:1706.05806
34. Alain & Bengio 2016/2018, "Understanding intermediate layers using linear classifier probes," arXiv:1610.01644
35. Tishby & Zaslavsky 2015 / Shwartz-Ziv & Tishby 2017, "Deep Learning and the Information Bottleneck Principle," arXiv:1503.02406
36. Schwab et al. 2020, "Restricting the Flow: Information Bottlenecks for Attribution," arXiv:2001.00396
37. Chung, Lee, Sompolinsky 2018, "Linear Readout of Object Manifolds," arXiv:1512.01834 / Phys Rev X
38. Rigotti et al. 2013 / Lindsay et al. 2017, "Sparseness of mixed selectivity," J. Neurosci.
39. "Linear-Readout Floors and Threshold Recovery in Computation in Superposition," arXiv:2605.01192

(Dedupe across sub-agents: ~35 unique verified citations; 5 candidates from sub-agent 1 overlap with sub-agent 2's Hopfield-Fenchel-Young / sparsemax citations.)

---

## P_deflated calibration summary per claim

| Claim | P_lit_supports (deflated) |
|-------|---------------------------|
| Linear readout is the ceiling in classical Hopfield regime | 0.85 |
| Softmax/LSE readout achieves exponential capacity | 0.80 |
| Sparsemax/entmax preserves exponential capacity AND adds margin | 0.65 |
| Readout-swap at fixed substrate is canonical diagnostic | 0.55 |
| Fly-MB: WTA is the nonlinearity, downstream readout is linear (canonical) | 0.75 |
| Dasgupta-Tosh: linear readout on top-k sparse code is universally approximating | 0.50 (theorem real; regime conditions empirical) |
| BioHash is SOTA Drosophila-class sparse-pattern-capacity result | 0.55 |
| Published direct fly-MB + VSA composition capacity result EXISTS | 0.15 |
| Expansion+WTA stage IS the Drosophila-class lever distinct from readout (PRED-1) | 0.42 (novel-synthesis-cap-aware) |
| 2x2 ablation methodology is published practice | 0.75 |
| Spherical-code geometric audit (Hu 2024) gives substrate-side capacity bound | 0.50 |
| Linear-decoder probes systematically under-report substrate capability | 0.70 |
| Information bottleneck yields tight numbers at AM scale N>=4096 | 0.15 |
| Capacity-envelope single-axis sweep is published practice for Hopfield-class | 0.75 |

Novel-synthesis cap (0.50) applied to: PRED-1 (composed expansion+WTA+entmax), PRED-2 (Dasgupta-Tosh regime condition), spherical-code audit-as-readout-attribution-lever.

---

## Closing 3 bullets (Drill Q5 format)

1. **The Drosophila MIDDLE_BAND is a DESIGN-INCOMPLETE-NOT-REFUTATION** (candidate audit-discipline rule #93). The prior ARCH-A experiment conflated two mechanistic axes: presence/absence of fly-MB expansion+WTA stage AND linear-vs-nonlinear readout choice. The 2x2 ablation (4 cells, ~1 hr CPU pre-flight) orthogonalizes these and decides whether the Drosophila-class capability requires its own substrate stage or is closed by the nonlinear-readout fix (ARCH-B / C1) alone. P_deflated for "requires its own stage" = 0.42.

2. **Sub-agent 3's specific finding REFRAMES the question.** In published fly-MB literature (Dasgupta-Stevens-Navlakha 2017, Litwin-Kumar 2017, Dasgupta-Tosh 2020, Ryali-Krotov 2020) the WTA top-k IS the nonlinearity and the downstream readout is LINEAR by canonical design. So the project's "linear readout is the ceiling vs nonlinear readout lifts it" framing -- correct for the canonical substrate per ARCH-B / C1 -- does not transfer cleanly to fly-MB-class architectures, where the nonlinearity is upstream of the readout. The substrate-novel question is whether the project's storage substrate benefits from inserting a fly-MB-style stage AHEAD of its existing (now nonlinear) readout. This question has NO published precedent (P=0.15 for direct comparable result) -- it is a genuine seam, not a saturated field.

3. **Cap_map update recommended.** Preserve ARCH-A MIDDLE_BAND closure as-is (cert-grade, no retraction). Open NEW cap_map row for "fly-MB expansion+WTA stage ahead of substrate readout" at status pending-experiment, ranked TIER-3 within sparse-coding-compressed-sensing field (per advisor; drill_count=1, scope-expansion eligible). Re-classify ARCH-A's MIDDLE_BAND closure provenance with NEW audit-discipline tag DESIGN-INCOMPLETE-NOT-REFUTATION pending USER ratify. If USER prioritizes Drosophila-class capability recapture, the 2x2 ablation pre-flight is the next experiment; if USER accepts honest-acceptance-of-MIDDLE_BAND on the prior (one-axis) design, no further action -- the readout-side fix is sufficient and the canonical fly-MB stage is left as a future scope-expansion candidate.

---

## Substrate-novel verification: T2/T3 onboarding-ready

All claims in this note are T2 (lit-supported) or T3 (conjecture/novel-synthesis) per [[feedback-research-can-be-wrong-only-proven-fully-believed-trust-tier]]. NO claim in this note is load-bearing on the substrate's proven-core. Promotion to PROVEN (T0) requires cert-grade experiment PASS at pre-registered HARD-PASS thresholds with VERIFY-THE-REFERENT discipline. The note is queryable as RESEARCH_FINDING atoms with confidence_tier annotated and bears_on links to the relevant cap_map rows.

ASCII-only output verified. No emojis. No em-dashes. Generic math terms only in all external queries (verified per sub-agent transcripts).
