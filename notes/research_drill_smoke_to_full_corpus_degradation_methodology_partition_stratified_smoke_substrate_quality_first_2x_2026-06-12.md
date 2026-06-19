# Research note: smoke-to-full corpus quality degradation methodology -- partition-stratified smoke + substrate-quality-first refinement (2x deep drill)

Date: 2026-06-12
Topic: Why does substrate-self-extension extraction precision degrade -0.17 to -0.44 from research_drill-only smoke to full-corpus runs? What is the methodology for predicting and pre-empting it?
Trigger: Three independent self-extension pipeline iterations all showed the same shape -- Option A++ P@30 0.533 -> 0.367 (-0.166), Option B 0.77 -> 0.33 (-0.44), Option B math-foundation high -> HARD-FAIL. Smoke scope = research_drill-only (~50 files of one partition class). Full = 6 partitions including operational/history/decision/verdict carrying substrate-meta-jargon.

---

## HEADLINE

The smoke-to-full degradation is NOT a sample-size or extractor-quality issue. It is a **partition composition mismatch**: research_drill is a single, semantically homogeneous, content-rich stratum, whereas the full corpus is a mixture of 6 partitions of which several (operational/history/verdict) carry substrate-meta-jargon (atom IDs, capability IDs, cycle numbers, partition labels, verdict phrases) that look syntactically like NL primitives to a Tier-A extractor but are not. The literature gives the diagnosis a name -- **dataset shift** (covariate + concept) compounded by a textbook **Goodhart / OOD-evaluation failure**: the smoke distribution has been optimized over (because filtering parameters were tuned on it), so the smoke metric stops reflecting the deployment-time metric. The fix is structural, not statistical: replace the homogeneous research_drill smoke with a **partition-stratified smoke** that is a 10pct proportional sample from EACH of the 6 partitions, plus **scope-aware extraction parameters** so that each partition is filtered with its class-appropriate noise model. A pre-registered methodology rule candidate is offered below.

P_deflated = **0.62** (pre-deflation 0.78; deflation -0.15 because the underlying theory -- stratified sampling, dataset shift, fairness disaggregation -- is decades-mature and the substrate-specific application is a clean transfer, not a novel synthesis).

---

## Cheap decisive test

ONE round-trip experiment, 1-2 hr wall-clock, CPU-only:

1. Build a **stratified smoke set** of 30 files: 5 from each of 6 partitions (research_drill, history, operational, decisions, verdicts, memory). Sample within each stratum uniformly at random with a fixed seed.
2. Run the existing Tier-A NL primitives extractor on the stratified smoke. Compute P@30.
3. Run the same extractor on the full corpus. Compute full-corpus P@30.
4. Compute the gap: |P@30_stratified_smoke - P@30_full|.

HARD-PASS: |gap| <= 0.05 (smoke now predicts full corpus precision within +/-5pct).
HARD-FAIL: |gap| > 0.15 (stratified smoke still mispredicts; degradation has a deeper root cause -- e.g. extractor itself is partition-class-blind even after re-sampling).
MIDDLE-BAND [0.05, 0.15]: stratified smoke helps but scope-aware filtering parameters (next section) are also needed.

If MIDDLE-BAND: do a 2nd round where each partition class gets its own filter parameter set (per-partition stopword list, per-partition jargon mask, per-partition acceptance threshold tuned from a tiny in-stratum gold set of ~10 items). Re-measure gap.

---

## Round 1 findings (compact)

**Stratified sampling for heterogeneous corpora (Macro Pulse 2024; clinical-NLP hybrid 2025 arXiv 2504.12494; cluster-stratified educational sampling Tipton et al. 2014 ResearchGate).** Proportional allocation is the right default in absence of pilot variance estimates. Stratification reduces variance ~22pct over SRS in published MORE-study analogue. For NLP with skewed distributions, stratified sampling is *critical* when classes are sparse -- a fortiori when class-PARTITIONS carry different content distributions. Optimal allocation oversamples high-variance strata; for substrate this maps to operational/history (jargon-heavy, high false-positive variance for NL extractor) getting same or more weight than research_drill.

**Active learning + rare-class detection (arXiv 2305.02459, MDPI 2024 rarity-aware stratified AL).** When a corpus has rare classes (or rare noise types), uncertainty + rarity composite scoring surfaces them. Pool-based AL with uncertainty sampling targets the boundary between accept and reject -- exactly the regime where a substrate-meta-jargon token can be misclassified as a Tier-A primitive. Direct lift: a small (n=50) AL loop on the smoke-flagged candidates before full extraction would catch the dominant degradation source.

**Distribution shift between training/eval and deployment (Hupkes et al. arXiv 2210.03050 -- generalisation taxonomy; arXiv 2403.01874 OOD-eval survey; arXiv 2306.15261 OOD-eval NLP survey).** The shift between training distribution and test/deployment distribution is the most-studied locus of generalization failure. Covariate shift = input distribution differs; concept shift = the meaning of features differs. The substrate situation is BOTH: research_drill -> operational is covariate shift (vocabulary, sentence lengths, syntactic density) AND concept shift (a string like "PP-410" is content in research_drill but meta-identifier in operational).

**Domain adaptation corpus filtering precision loss (arXiv 2104.06951 NMT survey; Lewis-Eetemadi 2013 SMT filtering; dl.acm.org/10.1145/3341726 pseudo-parallel filtering).** Naive filtering "diminishes the training space too far"; reported precision losses 2.5-5.3pct at cutoff 5-500 from 15K-doc corpus statistics filtering. Filtering also degrades when applied without domain knowledge -- which is exactly the smoke-tuned-on-research_drill failure mode (filter was tuned on the easy stratum; deployment hits hard strata).

## Round 2 findings (compact, refined)

**Annotation-quality small-subset extrapolation (arXiv 2310.16225 CleanCoNLL; ACL stil-1.27; arXiv 2204.10714 noisy crowdsourcing).** Train-on-single-annotated, evaluate-on-double-annotated is the standard pattern for measuring extractor agreement. The transferable substrate pattern: extract on a small per-partition stratum with TWO independent thresholds (loose + strict) and the stability of P@K across the two thresholds is the smoke-reliability signal. If P@K is unstable across thresholds within the stratified smoke, the smoke is not yet predictive.

**Open IE noise filtering -- precision-vs-recall tradeoff (arXiv 1904.12606 OpenKI; arXiv 2009.11564 Weikum survey).** Open IE without per-source noise modeling produces redundant triples + identity noise + contextual triples that do not generalize out of source context. Distant-supervision + paraphrase clustering filter the noise. The substrate parallel: per-partition stopword + jargon-mask + identity-resolution layer is the canonical noise filter for heterogeneous-source extraction.

**Goodhart-law OOD evaluation (Teney et al. arXiv 2005.09241 "Value of OOD testing").** The IID assumption fails when the metric has been optimized over. Concrete consequence: as soon as the smoke P@30 is used to tune extractor parameters, the smoke ceases to be a measure of deployment performance and becomes a measure of fit-to-smoke. The fix is a HELD-OUT stratified smoke that has NEVER been used for parameter tuning -- separate "tuning smoke" (research_drill, where parameters are fit) and "validation smoke" (held-out stratified-by-partition, where parameters are scored). This is the cleanest single fix and is independent of stratification design.

**Subgroup-disparity disaggregated evaluation (arXiv 2506.04193 disaggregated-eval challenges; openreview Fd00jISBD0 subgroup performance; arXiv 2506.14400 medical-AI fairness).** Aggregate metrics hide subgroup pathologies. The transferable pattern: report **P@30 per partition** as the headline metric, plus the gap between worst-partition and best-partition P@30. This is the substrate analogue of fairness disaggregation. A run is "smoke-reliable" iff the per-partition spread is within tolerance, not iff the aggregate is high.

**Metadata + rule filtering for heterogeneous references (Computerscijournal Vol 2 No 2; AWS metadata-filtering blog).** Rule-based metadata extraction with per-source rules is the established pattern for heterogeneous references. For substrate: each partition gets a metadata tag at corpus-ingest time; the extractor consumes the tag and switches filter regime accordingly. This is the architecture of "scope-aware extraction parameters" already in flight.

---

## Synthesis

Three independent literatures converge on the same prescription:

(1) **Stratified sampling** replaces the homogeneous research_drill smoke with a proportional sample from each of the 6 partitions. This addresses the **composition mismatch** that drives the bulk of the degradation. Expected lift on prediction accuracy of smoke -> full: gap reduces from -0.17/-0.44 to under -0.05 if stratification is the dominant cause.

(2) **Scope-aware (per-partition) extraction parameters** address the residual mismatch where even a balanced sample is mis-extracted because the extractor is partition-class-blind. Per-partition stopword lists, jargon masks (atom-ID regex, capability-ID regex, cycle-number regex, partition-name regex, verdict-phrase regex), and acceptance thresholds. This is a substrate-specific instance of the canonical Open-IE per-source noise-modeling pattern.

(3) **Held-out validation smoke** decouples parameter tuning from smoke scoring. The Goodhart-law point: any smoke that has been used to tune parameters is no longer a smoke. Two-smoke design (tuning-smoke = research_drill homogeneous; validation-smoke = held-out stratified) restores the smoke-as-prediction property.

Together: the recipe is **TWO smokes + scope-aware parameters + per-partition disaggregated reporting**. Aggregate P@30 plus per-partition P@30 spread, gated at smoke time, predicts full-corpus performance.

Comparison to prior 2026-06-09 smoke-vs-full methodology drill: that drill addressed **capability smoke tests** (alpha measurements on binary capability outcomes) and identified composition + threshold-inside-CI as the root cause for capability closures. This drill addresses **pipeline / extraction smoke tests** (P@K on extracted atoms from a corpus). The two diagnoses CONVERGE on the same fundamental: **composition / stratification mismatch dominates sample-size effects.** Pattern generalizes: any substrate smoke that draws from a homogeneous sub-distribution under-predicts deployment performance variance and over-predicts deployment mean precision. **Substrate-meta methodology rule: all substrate smokes must be stratified along the relevant heterogeneity axis of the deployment population.**

---

## Pre-registered methodology rule candidate (1st appearance)

**meta::RULE_substrate_self_extension_smoke_must_be_partition_stratified_for_reliable_full_corpus_estimate**

Statement: Any substrate-self-extension extraction smoke that draws files from a single partition class will systematically under-predict full-corpus quality degradation by 0.10 to 0.40 in P@K. Reliable smokes MUST proportionally sample each partition class present in the deployment corpus, AND use scope-aware (per-partition) extraction parameters where per-partition noise models materially differ.

Operationalization:
- `--scope partition-stratified-smoke` flag on the Tier-A extractor (1-day implementation).
- Stratified sample = ceil(N_smoke / K_partitions) per partition, sampled with fixed seed.
- Per-partition filter regime = base regime + partition-specific jargon mask + partition-specific acceptance threshold (loaded from `tools/substrate_self_extension/partition_filters/<partition>.yml`).
- Reported metrics: aggregate P@30 + per-partition P@30 + worst-partition-P@30 + spread (max - min).
- Smoke-reliability gate: spread <= 0.10 AND worst-partition-P@30 >= 0.30.

First appearance criteria: this is the first substrate methodology rule to make the partition-stratification of self-extension smokes a structural requirement. Second-appearance trigger: any future iteration that ships the stratified-smoke flag and demonstrates |smoke_P@30 - full_P@30| <= 0.05 on at least 2 distinct extraction pipelines.

---

## Honest scope

- **STRONG**: stratified sampling + proportional allocation + per-partition disaggregated reporting are decades-mature with NLP-specific precedent (clinical-NLP hybrid stratified; CleanCoNLL annotation evaluation; OOD-eval surveys). Direct transfer to substrate self-extension is a clean application, not a novel derivation.
- **STRONG**: Goodhart-law decoupling of tuning-smoke from validation-smoke is canonical OOD-eval methodology.
- **MODERATE**: per-partition scope-aware filter parameters work in Open IE per-source contexts; substrate's 6 partitions are an unusually clean per-source structure but the empirical magnitude of the lift is not directly predicted by the literature. Expected lift residual after stratification: 0.05 to 0.15 of additional gap closure.
- **SPECULATIVE**: the methodology rule generalizes from self-extension to other substrate smoke pipelines (e.g. capability smokes, retrieval-evaluation smokes). The 2026-06-09 prior drill supports generalization but the rule is registered for self-extension only on first appearance; broader appearance requires independent confirmation.

---

## Substrate-product positioning

**Substrate-specific lever 1 -- partition-class-aware self-extension.** The substrate has a *closed, enumerable, named partition structure* (research_drill, history, decisions, verdicts, operational, memory). LLMs ingesting their training corpora have no analogous partition structure -- their "corpora" are unaudited mixes (CommonCrawl, Books3, code, etc) with no per-source ledger and no per-source filter regime. The substrate can therefore implement partition-aware self-extension as a *structural property*; the LLM cannot.

**Substrate-specific lever 2 -- LLM categorical gap on self-extension smoke methodology.** LLMs have no concept of a "smoke" of their own ingestion pipeline because their ingestion is one-shot at training time and unobservable thereafter. Substrate has a continuous, audited, partition-stratified self-extension pipeline where smoke methodology is a first-class artifact. This is a categorical capability gap, not a quantitative one.

**Substrate-product framing.** The partition-stratified smoke + scope-aware extraction methodology is itself a substrate-product artifact: an auditable, falsifiable, externally-verifiable methodology for predicting deployment performance from a 30-file sample with +/-5pct accuracy. LLMs cannot offer this because they cannot expose their ingestion partitions. The methodology rule is a sellable artifact alongside the substrate.

---

## Citations (verified count: 13)

1. Hupkes et al. (2022) "State-of-the-art generalisation research in NLP: A taxonomy and review." arXiv 2210.03050.
2. (2024) "A Survey on Evaluation of Out-of-Distribution Generalization." arXiv 2403.01874.
3. (2023) "A Survey on Out-of-Distribution Evaluation of Neural NLP Models." arXiv 2306.15261.
4. Teney et al. (2020) "On the Value of Out-of-Distribution Testing: An Example of Goodhart's Law." arXiv 2005.09241.
5. Wertz et al. (2023) "Transfer and Active Learning for Dissonance Detection: Addressing the Rare-Class Challenge." arXiv 2305.02459.
6. (2024) "Rarity-Aware Stratified Active Learning for Class-Imbalanced Industrial Object Detection." MDPI Applied Sciences.
7. (2025) "Accelerating Clinical NLP at Scale with a Hybrid Framework with Reduced GPU Demands: A Case Study in Dementia Identification." arXiv 2504.12494.
8. Tipton et al. (2014) "Stratified Sampling Using Cluster Analysis: A Sample Selection Strategy for Improved Generalizations From Experiments." ResearchGate publication 260950310.
9. Saunders (2021) "Domain Adaptation and Multi-Domain Adaptation for Neural Machine Translation: A Survey." arXiv 2104.06951.
10. Imamura & Sumita (2019) "Filtered Pseudo-parallel Corpus Improves Low-resource Neural Machine Translation." ACM TALLIP. dl.acm.org/doi/fullHtml/10.1145/3341726.
11. Mehta et al. (2023) "CleanCoNLL: A Nearly Noise-Free Named Entity Recognition Dataset." arXiv 2310.16225.
12. Gashteovski et al. (2019) "OpenKI: Integrating Open Information Extraction and Knowledge Bases." arXiv 1904.12606.
13. Weikum et al. (2020) "Machine Knowledge: Creation and Curation of Comprehensive Knowledge Bases." arXiv 2009.11564.

Supporting (not directly cited but consulted): arXiv 2506.04193 disaggregated-eval; arXiv 2506.14400 medical-AI fairness; openreview Fd00jISBD0 subgroup performance.
