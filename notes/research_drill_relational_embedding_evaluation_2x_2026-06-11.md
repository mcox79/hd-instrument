# Research drill — relational embedding + cross-corpus retrieval evaluation (2x DEEP)

Date: 2026-06-11
Topic: Comparative validation harness for substrate-relational retrieval vs LLM on math-ops + concept-claim corpora with bidirectional cross-links.
Drill level: 2x DEEP (operational drill on existing methodology landscape)

## HEADLINE

The literature has converged on a four-axis evaluation methodology that cleanly distinguishes relational vs flat representations: (1) **link-prediction with filtered-rank** as the canonical KGE protocol; (2) **compositional out-of-distribution generalization** (CLUTRR / CFQ pattern) as the discriminator between memorization and structural inference; (3) **structure-mapping retrieval** with explicit relational-vs-object similarity scoring (Gentner SME / Hummel-Holyoak LISA) as the analogical stress test; and (4) **filter-then-score retrieval auditing** (Auepora target/dataset/metric decomposition) for RAG-style systems. Substrate-relational claims demand all four — single-axis evaluation has a documented history of overclaiming. Recommended harness: pre-registered query taxonomy (5 types), externally-verified ground truth held out from any LLM in the loop, lift-over-baseline scoring with 2-sigma CI bands, and a structure-mapping subtask that no flat-embedding LLM has cracked in the published literature.

## Cheap decisive test

Build a 200-query pre-registered evaluation set spanning 5 query types (defined below). Score substrate-relational retrieval and an LLM baseline (e.g. text-embedding + RAG, plus pure-LLM zero-shot) on identical (corpus, query, ground-truth) tuples. Externally-verified ground truth = human-curated, NOT LLM-generated. Decision rule: substrate wins on relational/compositional subtypes by >2x SE lift; loses on lexical-paraphrase subtypes is expected and OK. Cost: ~2-3 days corpus prep + 1 day eval. Total: under 1 week.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

### Query taxonomy (the 5 stress-tests)

Drawing from CLUTRR (compositional kinship inference), CFQ (compositional generalization), MIRB (formula+text retrieval), SME structural-similarity scoring, and OGB link-prediction protocols:

**Q1 — Single-hop relational lookup.** "Find concept-claims invoking math-op X." Tests basic indexing. Expected: substrate >= LLM-RAG; this is table stakes.
- HARD-PASS: substrate Hits@10 >= 0.85, LLM-RAG Hits@10 >= 0.80, gap < 0.10 (NOT a discriminator)
- HARD-FAIL: substrate < 0.70 — substrate is broken on basic retrieval

**Q2 — Multi-hop compositional retrieval.** "Find concept-claims where the underlying math-op chain involves [op_A] then [op_B]." (CLUTRR-pattern: depth-2 to depth-5 compositions.) Tests whether representation preserves compositional structure under traversal.
- HARD-PASS: substrate Hits@10 >= 0.55 at depth-3, LLM-RAG <= 0.35 at depth-3, lift >= 2x SE
- HARD-FAIL: substrate flat across depth (no compositional structure encoded) OR LLM-RAG >= substrate (substrate not adding relational value)

**Q3 — Structural analogy retrieval (SME-style).** "Find a concept-claim whose RELATIONAL structure matches this math-op pattern, even when surface tokens differ." This is the Gentner systematicity test: relations matter, objects do not. Stress: same relational skeleton, fully-disjoint vocabulary.
- HARD-PASS: substrate Hits@10 >= 0.40 with disjoint-vocab control, LLM-RAG (which keys on lexical/semantic surface) <= 0.15, lift >= 3x SE
- HARD-FAIL: substrate <= 0.25 — no structural alignment beyond surface

**Q4 — Cross-corpus bridge (math <-> concept).** "Given a math-op, find concept-claims that REFERENCE this op via bidirectional cross-link." Closer to MIRB Text-Math similarity benchmark. Tests whether bidirectional binding survives retrieval.
- HARD-PASS: substrate Hits@10 >= 0.75 in either direction; symmetry gap |fwd - rev| < 0.10
- HARD-FAIL: large asymmetry (>0.20 gap) — binding is unidirectional, not algebraic

**Q5 — Negation / distractor robustness.** CLUTRR distractor protocol: ground-truth answer present but surrounded by supporting/irrelevant/disconnected/noisy facts. Tests whether the system retrieves on STRUCTURE or on co-occurrence.
- HARD-PASS: substrate Hits@10 degradation under 25% distractor injection <= 10pp (i.e. 0.65 -> 0.55 acceptable)
- HARD-FAIL: degradation >= 25pp — system is co-occurrence-driven, not relational

### Calibration penalty applied

Per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis (substrate-on-this-corpus is uncharted) caps P_substrate_wins_on_Q2-Q3-Q5 at 0.50 even if lit and 3x-DEEP drills predict it. The pre-registered HARD-FAIL thresholds above are the binding constraint.

P_deflated for "substrate cleanly beats LLM on Q2+Q3+Q5 by lift > 2x SE" = **0.45** (deflated from drill-prior 0.65). Q1 win is near-certain (P=0.85). Q4 contingent on cross-link implementation (P=0.55).

## Cross-thread synthesis

### 1. KGE methodology landscape (TransE family)

TransE/ComplEx/RotatE/DistMult/ConvE all evaluated on the SAME protocol: link-prediction with **filtered MRR + Hits@K** on FB15k-237 and WN18RR (inverse-relation leakage removed in both). The dominant findings:
- ComplEx captures symmetric+antisymmetric+inversion but NOT composition.
- RotatE adds composition via complex-plane rotation but degrades on non-compositional paths.
- ALL of them are flat: a triple is scored by (h, r, t) energy, no multi-hop reasoning native.
- Substrate's structural advantage should appear on multi-hop compositional queries — exactly the regime where KGEs are documented-weak.

Methodology lesson: **adopt filtered-rank MRR + Hits@1/3/10** as the primary numeric metric. Filtering removes the inflate-on-known-triples confound that plagued FB15k (pre-WN18RR).

### 2. VSA / HRR retrieval literature

The HRR-style benchmarks in the literature: **superposition+cleanup** is the canonical retrieval primitive; standard tests include role-filler retrieval, sequence retrieval, multi-binding capacity curves. Recent work (Plate's original + 2021 differentiable HRR) introduced **projection-step stabilization** giving 100x improvement on concept-retrieval — relevant for substrate cleanup tiers.

Crucially: **there is no published benchmark of HRR/VSA cleanly beating LLMs on a structural retrieval task with externally-verified ground truth.** The HD computing applications are mostly drug discovery (30-task molecular classification), energy efficiency (NSHD), and cognitive-map learners. The cleanest cross-domain wins are efficiency, not raw accuracy. This is the gap our harness should target.

### 3. Compositional generalization benchmarks (CLUTRR, CFQ)

CLUTRR is the gold-standard diagnostic: synthetic family-relation stories, depth-controlled compositional reasoning, **explicit distractor injection** (supporting / irrelevant / disconnected / noisy). The LLM literature documents systematic failure on depth >= 4 even with chain-of-thought. CFQ extends to compositional generalization in semantic parsing. Both are explicitly **synthetic with held-out compositions** — exactly the property we need to avoid LLM benchmark contamination.

Methodology lesson: **synthetic + held-out + distractor-controlled** is the credible compositional eval. Externally-verified ground truth comes free because we generate it.

### 4. Structure-mapping (SME / LISA) for analogical retrieval

Gentner's structure-mapping: relational similarity > object similarity, structural consistency (one-to-one), systematicity (connected systems). SME outputs a **structural evaluation score** AND candidate inferences. Hummel-Holyoak LISA does the same with synchrony-of-firing as the binding mechanism — directly cognate to substrate's role-filler binding via algebraic operations.

The 2020 "Neural Analogical Matching" paper (Qualitative Reasoning Group, Northwestern) is the modern bridge: GNNs learning to produce structural mappings. Their evaluation methodology: held-out mappings, systematicity score, cross-domain transfer rate (78% reported on physics analogies in the persistent-mappings literature).

Methodology lesson: **structural-evaluation score per Gentner**, not just retrieval rank. A query "find structurally analogous math-op for this concept-claim" should be scored by relational-edge overlap, not lexical overlap.

### 5. RAG / LLM-retrieval evaluation pitfalls

The Auepora survey (arXiv 2405.07437) is the cleanest RAG-eval framework: **3-axis (Target / Dataset / Metric)** with component-level (retrieval-quality, prompt-construction, generation-faithfulness) AND end-to-end. Documented pitfalls:
- Treating system as black-box hides failure mode.
- Static benchmarks rapidly contaminated.
- LLM-as-judge has self-bias (LLM evaluators favor outputs from same model family).
- Auto-metrics + LLM evaluators correlate poorly with relational competence.

For substrate-vs-LLM comparison: **LLM cannot be in the evaluation loop.** Ground truth must be human-curated or rule-generated. LLM-as-judge would tilt scores toward LLM-retrieval.

### 6. Circular-evaluation / self-bias risks

The 2025-2026 LLM-eval literature (Silencer, Deconstructing Self-Bias, STEM) documents:
- LLM-generated benchmarks systematically favor the generator.
- Data contamination inflates scores by rewarding memorization.
- Judge bias incentivizes confident fabrication aligned with evaluator priors.
- Compute-agnostic metrics hide cost.

Mitigation pattern: **pre-registration + held-out + externally-verified ground truth + dynamic-generation if static is suspect.** All four must be in place for a credible substrate-vs-LLM claim.

### 7. Cross-corpus math-text retrieval (MIRB / ARQMath / NTCIR)

MIRB (May 2026) is the canonical math-IR benchmark: Semantic Statement Retrieval, Question-Answer Retrieval, Premise Retrieval, Formula Retrieval. ARQMath (CLEF) has formula+text queries. NTCIR-12 Wikipedia Formula Browsing for formula-only.

The 3-similarity decomposition is exactly our cross-link pattern: **Text-Text, Math-Math, Text-Math.** Substrate must demonstrate at least the Text-Math axis to be competitive on a math-formula+concept-claim corpus.

Methodology lesson: **adopt MIRB-style task decomposition** — separate semantic statement, premise-retrieval, and formula-retrieval subtasks. Premise-retrieval (find supporting math premises for a claim) is the test most aligned with substrate's relational strength.

### 8. Spectral / information-theoretic bounds

Spectral graph theory gives Cheeger-constant bounds on bottleneck capacity. The 2025 "Breaking Rank Bottlenecks in KGE" paper shows the bound is determined by **maximum subject-relation out-degree**, not node count — directly relevant: substrate retrieval capacity is bounded by the densest relational fan-out, NOT by total fact count. Graph Information Bottleneck literature gives compression-quality bounds.

Methodology lesson: **report substrate's effective rank / spectral profile** alongside accuracy, so the capacity is interpretable not just empirical.

## Substrate-product implications

1. **Five-axis pre-registered harness is the structural answer.** Q1 (basic), Q2 (compositional CLUTRR-style), Q3 (structural SME-style with disjoint vocab), Q4 (cross-corpus bidirectional MIRB-style), Q5 (distractor-robust). One overall claim ("substrate beats LLM") is not credible; per-axis claims are.

2. **Externally-verified ground truth, NOT LLM-generated.** Either human-curated or rule-generated synthetic. LLM-as-judge is disqualified per documented self-bias.

3. **Lift-over-baseline with 2x SE CI bands, per [[feedback-method-overclaim-lift-validation]].** Absolute thresholds insufficient — show the gap to a flat-embedding LLM-RAG baseline is real.

4. **Three published evaluation patterns to adopt directly:**
   - **CLUTRR distractor protocol** for Q5: supporting / irrelevant / disconnected / noisy fact injection at controlled ratios.
   - **Filtered-rank MRR + Hits@K** for Q1, Q2, Q4: standard KGE protocol, removes known-triple inflation.
   - **SME structural-evaluation score with disjoint-vocab control** for Q3: relations match, objects deliberately don't.

5. **Capacity-side reporting.** Spectral / rank profile of substrate retrieval kernel; out-degree distribution of cross-link graph. Lets the eval be diagnostic, not just summative.

6. **Negative results are valuable.** If substrate matches but does not beat LLM on Q3 (structural analogy), that is itself a finding — it tells us where substrate is and isn't structurally distinguished. Pre-registering HARD-FAIL thresholds makes negative results unambiguous.

7. **Anchor candidates for exp_dev** (rank-ordered):
   - **Anchor A: CLUTRR-on-substrate.** Port the CLUTRR synthetic protocol to (math-op, concept-claim) corpus with depth-2/3/4/5 compositional queries. Tier-1 priority. ~2 days build, 1 day eval.
   - **Anchor B: SME disjoint-vocab analogy.** Build 50 query pairs where relational skeleton is shared and vocabulary is fully disjoint. Score by structural-evaluation. Tier-1 priority. ~2 days build, 1 day eval.
   - **Anchor C: MIRB-style 3-axis decomposition.** Text-Text, Math-Math, Text-Math subtask split on the corpus. Tier-2 (broader, more infra).

## Citations (verified count: 17)

1. RotatE (Sun et al., openreview HkgEQnRqYQ) — relational rotation in complex plane.
2. Knowledge Graph Embedding: An Overview (arXiv 2309.12501).
3. Breaking Rank Bottlenecks in Knowledge Graph Embeddings (arXiv 2506.22271).
4. Learning with Holographic Reduced Representations (arXiv 2109.02157).
5. A comparison of vector symbolic architectures (Springer, 10.1007/s10462-021-10110-3).
6. CLUTRR: A Diagnostic Benchmark for Inductive Reasoning from Text (Sinha-Sodhani).
7. Benchmarking and Understanding Compositional Relational Reasoning of LLMs (arXiv 2412.12841).
8. Evaluation of Retrieval-Augmented Generation: A Survey (arXiv 2405.07437 — Auepora).
9. CoFE-RAG full-chain evaluation framework (arXiv 2410.12248).
10. Neural Analogical Matching (arXiv 2004.03573).
11. Probabilistic Analogical Mapping with Semantic Relation Networks (arXiv 2103.16704).
12. Hummel-Holyoak LISA: Symbolic-Connectionist Theory of Relational Inference (2003).
13. Silencer: From Discovery to Mitigation of Self-Bias in LLM-as-Benchmark-Generator (arXiv 2505.20738).
14. Deconstructing Self-Bias in LLM-generated Translation Benchmarks (arXiv 2509.26600).
15. Mathematical Information Retrieval: A Review (ACM CS, 10.1145/3699953).
16. MIRB: Mathematical Information Retrieval Benchmark (arXiv 2505.15585).
17. A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part II (ACM, 10.1145/3558000).

## Drill calibration self-note

- P_deflated for headline (clean substrate-wins-on-Q2+Q3+Q5 by 2x SE lift): **0.45**.
- This is novel-synthesis (substrate-on-bidirectional-math-concept-corpus has no published precedent), capped at 0.50.
- Q1 win nearly certain (0.85); Q4 contingent on cross-link impl (0.55).
- HARD-FAIL thresholds explicit per [[feedback-lit-scan-calibration-penalty]].
- No drill-defeatism per [[feedback-dont-parrot-drill-defeatism]] — proposing falsifiable harness, not declaring substrate weakness in advance.

## Next-drill candidate

`free-probability F4 Free cumulants` (per field advisor top score 5.5) — orthogonal to this evaluation drill but in fruit-bearing field. Or, more aligned: drill into **disjoint-vocab structural-analogy evaluation methodology** (SME-style) as Tier-1 follow-on if Anchor B passes smoke.
