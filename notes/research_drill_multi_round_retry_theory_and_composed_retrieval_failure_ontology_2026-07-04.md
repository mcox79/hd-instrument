# Research drill — multi-round retry theory + composed-retrieval failure ontology (2026-07-04)

## (a) HEADLINE
Across four independent literatures (VSA/resonator, Bayesian VOI/SPRT, best-arm identification, SDT + ASR dialog theory) the "when does a second look add value" condition collapses to ONE universal inequality: `(current evidence gap) × (informativeness of one more query) ≤ (cost of that query)`. Single-shot argmax dominates any retry/clarify policy in the high-SNR / high-baseline-accuracy / low-informativeness / high-fixed-cost regime — exactly the regime the motivating negative result occupied. This is not a novel finding on any single axis; it IS a novel cross-literature convergence result that predicts (i) revival at higher noise should PASS if implemented correctly, (ii) there are ≥5 other failure modes beyond "argmax-lucky" that are prereg-detectable and mutually distinguishable, and (iii) a 6-axis regime signature is REQUIRED before any composed-retrieval architectural claim earns regime-invariant status.

P_deflated (headline synthesis, capped at novel-synthesis 0.50 per lit-scan calibration): **0.45**.

## (b) Cheap decisive test
One noise-sweep grid `{σ ∈ [σ_lo, σ_hi], 5 points}` × `{single-shot argmax, composed-retry}`, held-out queries, fixed compute budget per query pair. Predictions:
- At `σ_lo` (near-ceiling baseline): `Δacc(retry − single) ≤ +0.02` and compute-normalized `Δacc / cost ≤ 0`. HARD-FAIL of "retry helps in general" if this fails to appear.
- At `σ_hi` (baseline accuracy < 0.75): `Δacc(retry − single) ≥ +0.05` net of retry cost. HARD-FAIL of "retry helps at all" if this fails.
- Crossover in between: `∃ σ* ∈ (σ_lo, σ_hi)` at which the sign flips. HARD-PASS if a monotone crossover exists AND is characterized by top-1/top-2 posterior gap ≈ utility-derived threshold.

Total: ~5-10 CPU-hours if reusing existing task infrastructure. Cheap and decisive.

## (c) Falsifiable predictions (HARD-PASS + HARD-FAIL)

| # | Prediction | HARD-PASS threshold | HARD-FAIL threshold | Source lit |
|---|---|---|---|---|
| P1 | Retry gain scales inversely with baseline confidence margin | corr(Δacc_retry, margin_baseline) ≤ −0.5 across ≥5 noise points | corr ≥ 0 | SDT Q3; SPRT Q2 |
| P2 | At high SNR, retry gain ≤ retry cost | Δacc(retry) < k/(U_A−U_FA) for baseline_acc ≥ 0.90 | Δacc ≥ 2·k/(U_A−U_FA) | Paek-Horvitz EDU; Egan ROC |
| P3 | Under deterministic-bias errors, retry accuracy = single-shot accuracy | cross-round error correlation ρ ≥ 0.7 in mechanism-mismatch mode | ρ ≤ 0.3 (would falsify mechanism-mismatch account) | Shannon channel; Bohus |
| P4 | Under i.i.d. stochastic-noise errors, retry accuracy > single-shot at low margin | ρ ≤ 0.3 AND Δacc(retry) ≥ +0.05 when margin ≤ 0.10 | Δacc ≤ 0 in same regime | Wald SPRT; BAI (Kaufmann) |
| P5 | For factorized retrieval with F≥2 factors, iteration is structurally required regardless of SNR | single-shot at F≥2 stays at chance regardless of σ | single-shot achieves ≥0.5 at F=2 at any σ | Frady/Kent resonator networks |
| P6 | Limit-cycle failure mode is empirically identifiable per-round argmax trajectory | ≥30% of failures cycle among ≤3 candidates without settling | limit-cycle rate < 5% in retry failures | Kleyko 2024 arXiv:2412.00354 |

## (d) Cross-thread synthesis — the universal inequality
Four independent literatures give the same shape:
- **EVSI** (Raiffa-Schlaifer): sample iff `EVSI(e) − c(e) > 0`, equivalently iff the sample can with nonzero prob. flip the argmax action.
- **SPRT** (Wald): first observation collapses the test to n=1 when `KL(H1‖H0) ≫ log(1/α) + log(1/β)`.
- **BAI** (Kaufmann-Cappé-Garivier): pulls ∝ log(1/δ) / gap; collapses to 1 as gap → large.
- **SDT + dialog** (Green-Swets, Paek-Horvitz): accept-and-commit dominates iff `P(ŷ|x) ≥ θ* + k/(U_A − U_FA)`.
- **Resonator networks** (Frady 2020; Kleyko 2024): F=1 single-shot; F≥2 structurally iterative; noise-injection helps within a unimodal band.

All four are the same inequality restated. `gap × informativeness ≤ cost` predicts NO retry gain. This is the load-bearing synthesis.

**Adjacency (LDPC / Maxwell construction, Measson-Montanari-Urbanke 2005)**: coding theory has a rigorously closed-form treatment of the iterative-vs-MAP gap via the EXIT-curve area argument. This is the template for how the VSA lit's "no closed-form crossover" gap could be filled — flagged for later drill.

## (e) Anti-drift / regime-signature framework
Six axes MUST be swept before a composed-retrieval architectural claim earns regime-invariant status:

| Axis | Load-bearing? | Known-invariant from lit? | Sweep grid recommended |
|---|---|---|---|
| 1. Noise / retrieval SNR (σ) | **YES — dominant** | No; controls crossover directly | ≥5 points spanning baseline_acc ∈ [0.60, 0.95] |
| 2. Task class (F=1 vs F≥2 factored) | YES — structural | Partly (resonator lit: F=1 is single-shot equivalent) | Include both regimes |
| 3. Retry cost shape (fixed vs superlinear) | YES | No | ≥2 shapes; include compounding |
| 4. Utility shape (linear vs concave; ceiling headroom) | YES — dominant when baseline high | No | ≥2 shapes |
| 5. Query difficulty distribution (i.i.d. vs deterministic-bias) | YES — determines mechanism-mismatch failure | Yes (Shannon channel: retry cannot beat deterministic bias) | ≥2 distributions |
| 6. Ceiling headroom (max achievable accuracy) | YES — dominant when baseline near ceiling | Partly (Q4 dialog: high baseline → clarify negative EV) | ≥2 ceilings |

**Load-bearing pair**: axes 1 (SNR) × 6 (ceiling headroom) — the crossover position depends on the difference `ceiling − baseline_at_σ`. Neither alone predicts crossover; the product does. This is what the motivating negative result missed: baseline sat near the ceiling, so retry had no headroom to earn cost, regardless of composition mechanism.

Anti-drift rule: NO architectural claim survives without sweep on axes 1 & 6 minimum, and 3-axis regime signature `(σ, F, utility_shape)` for any positive claim.

## (f) Failure-mode ontology (composed-retrieval + retry)

| Mode | Mechanism sketch | Prereg-detectable discriminator | Distinguishes from |
|---|---|---|---|
| **F1. Argmax-lucky-at-ceiling** | Baseline confidence exceeds SDT threshold; EVSI=0 | baseline_acc ≥ 0.90 AND Δacc(retry) ≤ 0.02 | Not F2 (retry cost is not the issue — even free retry wouldn't help); not F3 (errors are i.i.d.) |
| **F2. Retry-cost-unrecoverable** | Fixed cost k > Δacc·(U_A−U_FA) even when retry improves accuracy | Δacc(retry) > 0 BUT compute-normalized net utility < 0 | Not F1 (retry does improve accuracy); not F5 (utility isn't saturated) |
| **F3. Mechanism-mismatch (deterministic bias)** | Errors are systematic function of input (embedding bias, ASR mishearing); retry reproduces same error | cross-round error correlation ρ ≥ 0.7; retry error set ≈ single-shot error set | Not F4 (this is bias not noise); not F1 (retry doesn't work even at low baseline) |
| **F4. Utility-shape saturation** | Upside capped by ceiling; retry cannot earn back cost near ceiling regardless of accuracy gain | marginal_utility(correct_answer_n+1) → 0 as n grows; ceiling_headroom < k/(U_A−U_FA) | Not F1 (baseline could be moderate); not F2 (cost isn't structural — utility shape is) |
| **F5. Task-shape monotone / no second-look info** | Query provides no additional signal beyond first observation (measurement complete on turn 1) | H(y \| x_1, x_2) = H(y \| x_1); mutual information gain = 0 | Not F3 (no bias — just no info gain); not F1 (baseline can be moderate) |
| **F6. Limit-cycle / spurious-fixed-point** (resonator canon) | Iterative dynamics oscillates among small set of wrong codevectors | ≥30% of failures show argmax cycling among ≤3 candidates | Not F1-F5 — this is a dynamics failure, not a decision-theoretic one |
| **F7. Noninformative-prior backfire** (Grünwald-Halpern) | Vague prior + Bayesian update fights the wrong minimax battle | retry helps under informative prior; hurts under uniform/vague prior in same task | Not F3 (errors can still be i.i.d.); not F1 (baseline can be low) |

7 modes, all mutually distinguishable by the discriminators listed. Prereg any composed-retrieval revival with all 7 discriminators computed; the mode that fires WILL be visible.

## (g) Recommendations — post-revival experiments, ranked by info-gain / compute

| Rank | Experiment | Info-gain | Cost | HARD-PASS | HARD-FAIL |
|---|---|---|---|---|---|
| 1 | **Noise × ceiling sweep** (σ × ceiling_headroom grid) | Highest — directly tests load-bearing axes | 5-10 CPU-h | Monotone crossover in σ, position ∝ ceiling−baseline | No crossover; retry uniformly worse OR uniformly better across σ |
| 2 | **i.i.d. vs deterministic-bias sweep** (cross-round error correlation ρ measurement) | High — distinguishes F1/F3 mechanistically | ~1 CPU-h | ρ < 0.3 in stochastic regime, ρ > 0.7 in bias regime; retry gain only in stochastic | ρ pattern doesn't match retry-gain pattern |
| 3 | **Retry-cost shape sweep** (fixed / linear / superlinear per-round cost) | Medium — separates F2 from F1/F4 | ~2 CPU-h | Break-even round R* moves monotone with cost slope | R* invariant to cost — implies retry doesn't earn cost at any budget |
| 4 | **Utility-shape sweep** (linear vs concave, w/ vs w/o headroom cap) | Medium — separates F1 from F4 | ~2 CPU-h | Retry gain concentrates where headroom exists | Retry gain independent of headroom — implies decision-theoretic failure not utility failure |
| 5 | **Factorized task class** (F=1 vs F=2 vs F=4 with matched task difficulty) | High — tests P5 structural claim | ~5 CPU-h | Single-shot degenerate at F≥2 regardless of σ | Single-shot handles F=2 — falsifies resonator-lit structural claim |

Rank 1 is the load-bearing experiment. Ranks 2-5 map the ontology.

## (h) Substrate-product implications
- The composed multi-round retrieval architecture is NOT killed by the low-noise negative — that outcome is predicted by argmax-lucky-at-ceiling (F1) failure mode. In-flight higher-noise revival should PASS if implementation is correct.
- Any future composed-retrieval claim must ship with a 3-axis regime signature `(σ, F, utility_shape)` in its atomization; single-operating-point claims should be treated as `TBD` regardless of effect size.
- Prereg discipline for retry architectures: compute all 7 discriminators from the ontology table so the failure mode is diagnostic when the test fails.
- Retrieval SNR × ceiling headroom is the load-bearing pair for architectural claims — orchestrator's pipeline signature reporting should include both.

## (i) Citations (verified via WebSearch, tier-1)
1. Frady, Kent, Olshausen, Sommer. "Resonator Networks 1." Neural Computation 32(12), 2020. arXiv:1906.11684. https://arxiv.org/abs/1906.11684
2. Kent, Frady, Sommer, Olshausen. "Resonator Networks 2." Neural Computation 32(12), 2020. https://direct.mit.edu/neco/article/32/12/2332/95653/
3. Kleyko et al. "On the Role of Noise in Factorizers." arXiv:2412.00354, 2024. https://arxiv.org/html/2412.00354v1
4. "A comparative study of nonlinear cleanup rules in resonator networks." Frontiers in AI, 2026. https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1793314/full
5. Ganesan et al. "Learning with Holographic Reduced Representations." NeurIPS 2021. arXiv:2109.02157. https://proceedings.neurips.cc/paper/2021/file/d71dd235287466052f1630f31bde7932-Paper.pdf
6. Raiffa & Schlaifer. Applied Statistical Decision Theory. 1961.
7. Wald. Sequential Analysis. 1947. (SPRT canonical.)
8. Chaloner & Verdinelli. "Bayesian Experimental Design: A Review." Statistical Science 10(3), 1995. https://projecteuclid.org/journals/statistical-science/volume-10/issue-3
9. Settles. Active Learning Literature Survey. 2010. https://burrsettles.com/pub/settles.activelearning.pdf
10. Kaufmann, Cappé & Garivier. "On the Complexity of Best Arm Identification." JMLR 17, 2016. https://jmlr.org/papers/v17/kaufman16a.html
11. Grünwald & Halpern. "When Ignorance is Bliss." arXiv:1407.7188.
12. Green & Swets. Signal Detection Theory and Psychophysics. 1966.
13. Egan. Signal Detection Theory and ROC Analysis. 1975.
14. Jiang. "Confidence measures for speech recognition: a survey." Speech Communication 45, 2005. https://www.sciencedirect.com/science/article/abs/pii/S0167639305000051
15. Bohus & Rudnicky. "Sorry, I Didn't Catch That!" SIGdial 2005. https://aclanthology.org/2005.sigdial-1.14.pdf
16. Paek & Horvitz. "Conversation as Action Under Uncertainty." UAI 2000. https://arxiv.org/pdf/1301.3883
17. Williams & Young. "POMDPs for spoken dialog systems." Computer Speech & Language 21(2), 2007.
18. Measson, Montanari, Urbanke. "Maxwell Construction." arXiv:cs/0506083 (adjacency, not core).

Verified: 18 tier-1 citations across 3 literatures + 1 adjacency.

## (j) P_deflated per finding (lit-scan calibration penalty applied: −0.20 typical; novel-synthesis capped at 0.50)

| Finding | Raw P | Deflated | Notes |
|---|---|---|---|
| Universal "gap × informativeness ≤ cost" cross-lit synthesis | 0.45 (already capped) | **0.45** | novel synthesis; cap holds |
| P1 retry gain ∝ 1/margin | 0.65 | **0.45** | 4 lit convergent, strong direction |
| P2 high-SNR retry unrecoverable | 0.70 | **0.50** | direct Q4 dialog result + SPRT |
| P3 deterministic-bias mode | 0.55 | **0.35** | Shannon adjacency, not empirically shown for VSA |
| P4 i.i.d.-noise retry works | 0.55 | **0.35** | classical result, VSA transfer unproven |
| P5 F≥2 structural iteration | 0.80 | **0.60** | strong lit; not deflated to cap because direct citation |
| P6 limit-cycle rate | 0.70 | **0.50** | direct citation, cap applied |
| F1-F7 ontology completeness | 0.40 | **0.30** | novel synthesis, cap; ontology may be incomplete |
| Anti-drift 6-axis framework | 0.45 | **0.35** | novel framework; requires empirical validation |

Headline `P_deflated = 0.45`.

Next-drill candidate: **Maxwell-construction adjacency to VSA retrieval** (LDPC iterative-vs-MAP gap has a rigorously closed-form crossover; the VSA lit has no such derivation). Field: coding-theory (Tier-2, moderate yield) but adjacency to resonator canon is direct. Alternative: **F4 free-cumulants** (top ranked by advisor) but not directly on-topic for retry theory.
