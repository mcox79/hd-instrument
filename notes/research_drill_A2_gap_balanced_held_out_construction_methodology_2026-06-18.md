# Research drill: A2 gap-balanced held-out construction methodology

Filed: 2026-06-18
Topic: Methodology for constructing a research-grade GAP-balanced held-out test set for the substrate refuse-gate component.
Dispatch context: USER overnight directive + Skunkworks routing of A2-precursor research; grounds USER's eventual A2 prioritization decision; provides verify-the-referent check on Skunkworks's DATA-BLOCKED ruling on current q54-q65 (12 answerable / 1 gap, statistically un-testable).
Author: research sub-agent (Opus synthesis from 4 parallel Sonnet lit-scans).
Lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated 0.15-0.25; novel-synthesis P capped at 0.50; hard-fail thresholds explicit.

---

## (a) HEADLINE

The published literature converges on two-paradigm construction (adversarial-similarity authorship + model-conditioned partitioning) with double-validator re-annotation as the gold-standard verification step; the binding constraint on the substrate's A2 design is statistical-power floor (Hanley-McNeil): a Hanley-McNeil AUROC test discriminating 0.7 from null=0.5 at alpha=0.05, power=0.80 requires roughly 27 gap and 27 in-coverage items at 1:1 balance, and a meaningful CI-half-width floor demands at least ~22 per cell -- the current 1-gap held-out is approximately 22-27x below the minimum and CANNOT be rescued by re-analysis; a fresh research-grade build is mandatory, with adversarial-similarity authorship by an independent annotator + a substrate-side verify-absence procedure before the LoRA Stage 2 test can be pre-registered.

P_deflated headline = 0.62 (raw lit-scan consensus ~0.80, deflated 0.18 for substrate-novel application).

---

## (b) Cheap decisive test

Pre-LoRA, the cheap decisive test that the candidate A2 set is VALID for Stage 2:

1. Construct a candidate gap-balanced held-out at minimum 30 gap + 30 in-cov (slightly above the 27/27 power floor), total 60.
2. Run the CURRENT (un-tuned) substrate's refuse-gate against all 60 items and compute AUROC. If AUROC is already >= 0.7, the set is leaky (gap items are trivially detectable by surface form; not measuring the mechanism we intend to learn).
3. Run a TF-IDF or simple BM25 baseline classifier on the question text alone. If TF-IDF achieves AUROC >= 0.65, the set has lexical-shortcut leakage and must be rebuilt.
4. Inter-author verification: an independent annotator (or second LLM, blinded) must correctly classify gap vs in-cov at >= 0.85 accuracy. If <0.85, the gap-label is itself ill-defined.

Set is "decisive-test PASS" only if: untuned-substrate AUROC in [0.45, 0.60] (near-chance, room to improve) AND TF-IDF baseline AUROC < 0.65 AND human-blind classifier >= 0.85.

Cost estimate: ~1-2 GPU-hour for substrate forward passes + ~4-8 hours of annotator-equivalent work (or ~2 hours LLM-as-second-annotator if substrate-text-only and we use a held-out judge model).

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE)

These are pre-registered for the EVENTUAL A2 Stage 2 LoRA learned-adapter test, conditional on the gap-balanced set existing and passing (b).

**Prediction P1: Separation AUROC**
- HARD-PASS: post-LoRA refuse-gate AUROC >= 0.75 on gap-balanced held-out (>= 30 gap, >= 30 in-cov), 95% CI lower bound > 0.60.
- HARD-FAIL: post-LoRA AUROC <= 0.55 with 95% CI upper bound < 0.65 (no separation distinguishable from noise after sufficient N).
- MIDDLE_BAND: AUROC in (0.55, 0.75) -- partial mechanism evidence; report and decide whether to scale N or revise adapter design.

**Prediction P2: Calibration on gap-side**
- HARD-PASS: gap-side mean predicted P(in-cov) <= 0.40 (the substrate confidently refuses gap items as a population).
- HARD-FAIL: gap-side mean predicted P(in-cov) >= 0.60 (model confidently mis-accepts gap items; the LoRA learned the wrong direction).
- Brier score gap-side <= 0.25 = HARD-PASS calibration; >= 0.45 = HARD-FAIL.

**Prediction P3: Lexical-shortcut control**
- HARD-FAIL: TF-IDF baseline matches or exceeds the substrate's AUROC after LoRA (the LoRA did not learn refuse-gate mechanism; it learned text-statistics).
- HARD-PASS: substrate AUROC exceeds TF-IDF baseline by >= 0.10 with non-overlapping CIs.

**Prediction P4: Near-gap robustness**
- HARD-FAIL: substrate AUROC drops by > 0.15 when evaluated on near-gap items (semantically similar to in-cov topic but verified-absent content) vs far-gap items (different topic entirely). This indicates the substrate is detecting topic-mismatch, not knowledge-gap.
- HARD-PASS: near-gap and far-gap AUROC within 0.05 of each other.

**Prediction P5: Statistical-validity gate**
- HARD-FAIL: if final held-out has n_gap < 22 OR n_in-cov < 22, the AUROC estimate is reported but flagged NON-TESTABLE per Hanley-McNeil and Cortes-Mohri CI floors. Do not allow the Stage 2 verdict to clear without this gate.
- HARD-PASS: n_gap >= 27 AND n_in-cov >= 27 (80% power floor); CIs computed.

---

## (d) Cross-thread synthesis

**With the existing refuse-gate NON_TEST finding (Skunkworks, self-dominance wall on real held-out):**

The NON_TEST verdict on q54-q65 is consistent with the lit-scan finding: a 1-gap-item evaluation is INCAPABLE of statistical separation testing regardless of mechanism. Skunkworks's call to flag this DATA-BLOCKED rather than NEGATIVE is methodologically correct -- the Hanley-McNeil floor of ~22 per arm puts the current held-out 22x below the minimum to even compute a meaningful CI. The "self-dominance wall" observation (substrate confidently answers everything) is not refutable on n_gap=1; it could be either a real refuse-gate failure OR a single-item artifact. We cannot distinguish without more gap items.

This converges with NEGATIVITY-BIAS rule (USER 2026-06-17): pre-registered bands sacrosanct both directions -- the cell didn't fail the mechanism, the test lacked power to evaluate it. The atom dictionary should label this DATA-BLOCKED-NOT-REFUTED, parallel to DEGENERATE-REGIME-NOT-REFUTATION (4 witnesses today per session arc).

**With the verify-the-referent discipline (USER-LOCKED 2026-06-17):**
The lit-scan flags that "gap" labels in popular benchmarks routinely leak: NaturalQuestions "null" items are reformulatable into answerable in ~25-40% of cases (CLAP-NQ 2024); DPR/ANCE hard-negatives have ~70% false-negative rate (NV-Retriever 2024). VERIFY-THE-REFERENT applied here means: a gap item is not "verified absent" until we have attempted to retrieve / generate / answer it through the substrate's full pipeline + an alternate path (e.g., a research-only adjacent path) and confirmed both fail. The annotator's intent is necessary but not sufficient.

**With research-can-be-wrong trust-tier (USER 2026-06-17):**
Methodology recommendations below are T2 (lit-supported) -- they should onboard as queryable but NON-load-bearing until the A2 Stage 2 experiment produces a cert-grade PASS or FAIL. A clean A2 PASS would promote the gap-construction methodology to PROVEN for the substrate. A FAIL on a well-constructed set is also valuable: it would rule out the LoRA-learned-adapter approach for refuse-gating, leaving the architectural alternatives (Stage-1 confidence threshold; explicit retrieval-failure detector; external uncertainty head).

**With corpus-completeness / remote-vs-local rule:**
Construction MUST audit against the full substrate corpus (the 31k+ atoms, both local and remote) to declare a topic "absent." Auditing only local atoms would repeat the half-data audit incident (2026-06-17 morning). The verify-absence procedure should run remote-side atomically against the full Store.

---

## (e) Substrate-product implications

**For the refuse-gate as a product feature:**
A refuse-gate that triggers on the substrate's INTERNAL uncertainty signal (rather than on a learned text-classifier proxy) is the cert-grade product offering. The A2 Stage 2 LoRA learned-adapter is one path; an alternative is a direct internal-readout abstain head (no LoRA, just a calibrated thresholder on existing internal scores). Both need the same gap-balanced eval to be measurable.

**Concrete methodology recommendation for substrate A2 build:**

1. **Target size:** 60 items minimum (30 gap + 30 in-cov; 80% power for AUROC 0.7 vs 0.5). Stretch target: 100 (50/50, comfortably above floor; allows subgroup analysis near-gap vs far-gap).

2. **Construction protocol:**
   - **In-cov items:** drawn from existing answerable corpus, stratified to match the topic distribution of gap items.
   - **Gap items:** authored by adversarial-similarity protocol (SQuAD 2.0 / SelfAware style). For each in-cov item, an annotator (or LLM-then-verifier) writes a question that:
     - References entities/topics on-domain (so it is not trivially distinguishable by topic shift),
     - Is genuinely outside the substrate's coverage (verified by the substrate-side absence procedure below),
     - Cannot be answered by a simple reformulation of an existing in-cov item (CLAP-NQ failure mode).
   - **Near-gap vs far-gap split:** authorize 15 near-gap (semantically similar to in-cov but content-absent; e.g., a question about a related-but-uncovered fact in a covered domain) + 15 far-gap (entirely different topic). This enables P4 to be tested.

3. **Verify-absence procedure (the verify-the-referent step):**
   - For each candidate gap item, query the full Store (remote + local) for related atoms using both embedding-similarity (top-k=50 nearest atoms) and lexical-similarity (BM25 top-k=50).
   - An annotator (or a separate LLM-as-judge with the retrieved atoms as context) confirms: does the substrate hold enough to answer this question? If yes -> recategorize as in-cov; if no -> confirmed gap.
   - Repeat with a SECOND independent verifier; both must agree (parallel to ANLI's writer + verifier protocol). Disagreement items dropped.
   - Record the verifier-agreement rate as a dataset-quality metric (target >= 0.85; below indicates ambiguous gap definition).

4. **Lexical-shortcut audit (the leakage gate):**
   - Train a TF-IDF binary classifier on the 60-item set with leave-one-out CV. If LOO-CV AUROC >= 0.65, the gap and in-cov items are lexically distinguishable -- rebuild with controlled lexical statistics.
   - Optional stronger gate: a frozen sentence-BERT classifier; if it exceeds 0.70, reject.

5. **Pre-registration template:**
   - Filed BEFORE any LoRA training; includes the gap-balanced held-out, the 5 predictions above with their bands, and the analysis plan.
   - Bands sacrosanct both directions (NEGATIVITY-BIAS rule).

**Risk-of-failure modes guarded against:**

| Failure mode | Source | Guard |
|---|---|---|
| Gap-as-known-form-but-novel-content | CLAP-NQ reformulation 25-40% leak | adversarial-similarity authorship + verifier re-annotation |
| Gap-as-different-form-trivial-distractor | SelfAware stylistic leak signal | TF-IDF / sentence-BERT leakage audit (P3) |
| Single-annotator bias | DPR/ANCE 70% false-neg | double-verifier agreement gate |
| Lexical shortcut learning | ANLI / contrast-set literature | P3 baseline + reject if baseline competes |
| Under-powered N | Hanley-McNeil floor | P5 statistical-validity gate |
| ID leakage in OOD set | OpenOOD's re-cleaning of TinyImages | substrate-side absence procedure run against full remote+local Store |
| Topic-shift confound | GLUE-X near-vs-far decoupling | P4 near-gap / far-gap split |
| Selector collapse (abstain-everywhere) | SelectiveNet auxiliary-head insight | P2 calibration gate (gap-side mean P, Brier) |
| Marginal-not-conditional coverage | KnowNo limitation | P4 + report per-subgroup AUROC |
| Self-fooling (LLM annotator both writes and verifies) | adversarial NLI human-loop necessity | use SEPARATE judges; ideally one human or one alternate model not used to author |

---

## (f) Citations (verified count: 30)

Construction methodology (unanswerable QA):
- [Rajpurkar et al. 2018 SQuAD 2.0](https://arxiv.org/abs/1806.03822)
- [Kwiatkowski et al. 2019 Natural Questions](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00276/43518/)
- [Asai & Choi 2021 challenges in information-seeking QA](https://aclanthology.org/2021.acl-long.118.pdf)
- [Rosenthal et al. 2024 CLAP-NQ / I Could've Asked That](https://arxiv.org/pdf/2407.17469)
- [Yin et al. 2023 SelfAware](https://aclanthology.org/2023.findings-acl.551/)
- [Zhang/Diao et al. 2024 R-Tuning NAACL](https://arxiv.org/abs/2311.09677)
- [Cheng et al. 2024 Idk dataset](https://arxiv.org/abs/2401.13275)
- [Ren et al. 2023 KnowNo CoRL](https://arxiv.org/abs/2307.01928)
- [Kadavath et al. 2022 LMs know what they know](https://arxiv.org/abs/2207.05221)

OOD detection benchmarks:
- [Hendrycks & Gimpel 2017 baseline](https://arxiv.org/abs/1610.02136)
- [Geifman & El-Yaniv 2017 selective classification](https://arxiv.org/pdf/1705.08500)
- [Geifman & El-Yaniv 2019 SelectiveNet](https://arxiv.org/pdf/1901.09192)
- [Huang & Li 2021 MOS](https://arxiv.org/abs/2105.01879)
- [Yang et al. 2022 OpenOOD v1.0](https://ar5iv.labs.arxiv.org/html/2210.07242)
- [Yang et al. 2023 OpenOOD v1.5](https://arxiv.org/abs/2306.09301)
- [Vaze et al. 2022 SSB](https://github.com/sgvaze/SSB)
- [Gangal et al. 2020 ROSTD](https://arxiv.org/abs/1912.12800)
- [Yang et al. 2023 GLUE-X](https://arxiv.org/abs/2211.08073)

Adversarial / hard-negative construction:
- [Nie et al. 2020 ANLI](https://aclanthology.org/2020.acl-main.441/)
- [Ribeiro et al. 2020 CheckList](https://aclanthology.org/2020.acl-main.442/)
- [Gardner et al. 2020 contrast sets](https://aclanthology.org/2020.findings-emnlp.117/)
- [Kaushik et al. 2020 CAD](https://arxiv.org/abs/1909.12434)
- [Bartolo et al. 2020 AdversarialQA](https://huggingface.co/datasets/UCLNLP/adversarial_qa)
- [Xiong et al. 2021 ANCE](https://arxiv.org/abs/2007.00808)
- [NV-Retriever positive-aware hard-negative mining 2024](https://arxiv.org/html/2407.15831)

Sample size / statistical power:
- [Hanley & McNeil 1982 (NCSS PASS reference)](https://www.ncss.com/wp-content/themes/ncss/pdf/Procedures/PASS/Confidence_Intervals_for_the_Area_Under_an_ROC_Curve.pdf)
- [Obuchowski 1994 sample size for ROC](https://pubmed.ncbi.nlm.nih.gov/8169102/)
- [Cortes & Mohri 2004 AUC confidence intervals](https://cs.nyu.edu/~mohri/pub/area.pdf)
- [Naeini et al. 2015 Bayesian binning calibration](https://www.researchgate.net/publication/275666914)
- [powerROC tool 2025](https://arxiv.org/html/2501.03155v1)
- [AUROC and AUPRC under class imbalance 2024](https://arxiv.org/html/2401.06091v1)

Total verified citations: 30.

---

## Drill Q5 closing 3 bullets

- **Most underexplored gap-construction angle:** the **substrate-internal verify-absence procedure** (not just annotator-judgment of absence). Published literature relies on annotator intent (SQuAD 2.0, SelfAware) or lexical heuristic (DPR, ANCE), with 25-70% false-negative rates documented. A substrate that can interrogate its OWN coverage (full Store query + retrieval + answer-attempt + judge) provides a stronger absence guarantee than any human-only protocol. This is also a substrate-product differentiator: the absence-verification capability IS the refuse-gate's underlying mechanism, so the construction tool IS the product probe.

- **Strongest no-Goodhart-aware measurement:** **near-gap vs far-gap AUROC delta (Prediction P4)**, combined with the **TF-IDF lexical-shortcut baseline (P3)**. Goodhart's law on AUROC alone says "the metric becomes the target; the system learns to hit the metric." But if the model EQUALLY discriminates near-gap (semantically similar to in-cov) and far-gap (different topic), it has learned the absence signal, not the topic signal. The TF-IDF baseline pins down the lexical-shortcut floor. Together these are 2 orthogonal Goodhart guards; both ANLI and OpenOOD literature use functionally-equivalent dual-guards.

- **Open theoretical question:** **what is the right epistemic primitive for substrate-internal "knowledge absence"?** The closest analogues -- conformal prediction (KnowNo), value-head self-knowledge (Kadavath P(IK)), and selective classification (Geifman-El-Yaniv) -- all rely on external calibration data. A hyperdimensional substrate has access to internal geometric signals (cleanup-distance, bundle-strength, atom-isolation-margin) that human/external benchmarks don't. The unexplored question is: does a closed-form geometric "absence signature" exist (e.g., minimum distance to any cleanup atom > some threshold => absent), and if so, is it more reliable than a learned LoRA adapter? Cheap test: compute the internal geometric features on a candidate gap-balanced set and benchmark them as a fixed-rule baseline. If a 0-parameter geometric rule achieves AUROC >= 0.7, the LoRA Stage 2 is unjustified -- the architectural alternative (calibrated internal threshold) wins for cert-grade.

---

## Pre-deflation calibration table

| Claim | Raw lit-scan P | Deflation | P_deflated | Reason for deflation |
|---|---|---|---|---|
| Hanley-McNeil floor applies here (n >= 22-27/arm) | 0.95 | 0.05 | 0.90 | Pure math, minimal substrate-specific risk |
| Adversarial-similarity authorship transfers to substrate domain | 0.75 | 0.20 | 0.55 | SQuAD 2.0 paradigm well-established but substrate has no human-readable text in some atom classes |
| Substrate-internal absence procedure outperforms human-only | 0.50 | 0.20 (capped) | 0.45 | Novel synthesis -- no direct lit precedent |
| LoRA Stage 2 will produce AUROC >= 0.75 given valid gap set | 0.50 | 0.20 | 0.40 | Untested architectural choice; could fail mechanism-wise |
| Near-gap vs far-gap delta < 0.05 (P4 PASS) | 0.50 | 0.25 | 0.30 | Optimistic; OpenOOD literature shows near-OOD is hardest |
| TF-IDF baseline AUROC < 0.65 on well-constructed set | 0.85 | 0.15 | 0.70 | Lit precedent in ANLI and contrast-set work supports this |
| Verifier-agreement rate >= 0.85 achievable | 0.80 | 0.18 | 0.62 | Standard for inter-annotator agreement in published QA work |
| Geometric absence-signature is closed-form for the substrate | 0.40 | 0.20 | 0.30 | Truly speculative; needs experimental confirmation |

P_deflated for the OVERALL methodology recommendation (decisive test + Stage 2 will yield interpretable result conditional on construction passing audits): **0.62**.

---

## Status log entry

Filed via `python -c "from tools.orchestrator.state import log_event; log_event('research_delivery', ...)"`.
- topic: A2 gap-balanced held-out construction methodology
- importance: HIGH
- plain_language: Researched how academic literature builds "known-unknown" evaluation sets (where some test questions are deliberately outside the system's knowledge). Key finding: any meaningful gap-vs-coverage separation test needs at least 22-27 gap examples (current set has 1). Recommended a concrete construction methodology with double-verifier review, lexical-shortcut audit, and near-gap/far-gap split. The current held-out cannot be rescued by re-analysis; a fresh build is mandatory before any LoRA Stage 2 refuse-gate test is statistically interpretable.

---

## Next-drill candidate

`semiconductor` (under-drilled, 2 prior, 100% yield) -- adjacent angle: DLTS K-pulse decay analogue for the substrate's absence-signature retention timescale. OR `network-science-graph-theory` (Tier-1b new field) -- expander / spectral-gap analyses of the substrate's retrieval graph predict whether a "geometric absence signature" admits closed-form characterization (open question Q5-3 above).
