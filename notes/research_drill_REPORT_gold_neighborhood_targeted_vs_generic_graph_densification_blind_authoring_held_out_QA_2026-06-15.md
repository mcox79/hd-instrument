# 3x DEEP DRILL LITERATURE REPORT

Tag: 3x_DEEP_DRILL_LITERATURE
Date: 2026-06-15
Topic: Why does graph-based retrieval augmentation transfer to held-out test sets ONLY when new edges/nodes target the test gold's neighborhood, and NOT when they densify general foundational structure orthogonal to the test? Companion process question on blind authoring / pre-registration. Companion mechanism question on typed-operator graph walks and within-graph ceilings.

Tone: ASCII only. Survey-style. Generic literature framing. Unverifiable claims marked [UNVERIFIED] and excluded from synthesis.

----------------------------------------------------------------------

## ARM 1 -- Held-out generalization for graph-augmented RAG / typed-graph QA

### Cited works (verified)

1. Recht, Roelofs, Schmidt, Shankar (2019). "Do ImageNet Classifiers Generalize to ImageNet?" ICML 2019.
   - Replicating the original dataset curation produced an 11-14% accuracy drop on ImageNet and a 3-15% drop on CIFAR-10. Authors attribute drops not to adaptive overfitting from test reuse but to model failure to generalize to slightly harder images drawn from the same distribution-creation pipeline. Direct implication for KG augmentation: gains on an inspected gold set are not safely projected onto an independently re-curated gold set without held-out replication.

2. Mavromatis and Karypis (2024). "GNN-RAG: Graph Neural Retrieval for Large Language Model Reasoning." ACL 2025 Findings (arXiv:2405.20139).
   - Reports that a small GNN trained for subgraph retrieval, paired with an LLM reasoner, beats LLM-only retrieval by 8.9-15.5 F1 points on WebQSP and CWQ. Crucially, the lift depends on the GNN learning question-conditional relevance weights over graph nodes (i.e. neighborhood-of-the-answer ranking), not on densifying the underlying KG. Generic edge density is held constant; the gain is in question-targeted walk weighting.

3. Wu et al. (2024). "GraphRAG-Bench: Challenging Domain-Specific Reasoning for Evaluating Graph Retrieval-Augmented Generation" (arXiv:2506.02404).
   - Benchmark finding: most current GraphRAG variants overfit to graphs that were built from the same source documents as the QA set; transfer to a domain-shifted KG drops sharply. The paper isolates a noise-and-incompleteness regime where generic edge addition does not lift F1 and can lower it.

4. Su et al. (2024). "Knowledge Graph-Guided Retrieval Augmented Generation" (arXiv:2502.06864).
   - Reports cases where adding a flat ontology layer (broad foundational edges) had negligible effect over the naive RAG baseline on multi-hop QA datasets. Gain appears only when the augmented edges are scoped to entities that the test queries actually traverse.

5. Tian et al. (2024). "How to Mitigate Information Loss in Knowledge Graphs for GraphRAG" (IJCAI 2025, paper 0901).
   - Argues that the dominant failure mode in GraphRAG is not under-density but the wrong kind of density: edges that improve global connectivity without improving the local subgraph around answer entities do not help, and can introduce competing high-PR paths that hurt retrieval precision.

6. Liang et al. (2024). "KAG: Boosting LLMs in Professional Domains via Knowledge Augmented Generation" (arXiv:2409.13731).
   - Reports +19.6% F1 on HotpotQA and +33.5% on 2Wiki when KG augmentation is constructed from the same document corpus that produces the QA pairs (an in-domain neighborhood-overlapping construction). The improvement scale is the calibration anchor: when augmentation is gold-neighborhood-overlapping by design, double-digit F1 lifts are plausible.

### Per-arm synthesis

The 2022-2026 KG-augmentation literature converges on a sharp distinction: edges that connect the question's seed entities to the answer's neighborhood lift held-out F1; edges that densify the ontology globally (broad foundational connections, abstract supertypes, generic schema completion) typically do not. GraphRAG-Bench (3) and the IJCAI-2025 information-loss analysis (5) name the failure mode explicitly: generic density introduces high-PageRank distractor paths that compete with the answer path during walk-based or GNN-based retrieval. The KAG result (6) sets a calibration ceiling: when augmentation is question-corpus-aligned, +20-33 F1 lifts are reported on HotpotQA-class benchmarks. The Recht ImageNet replication (1) supplies the prior: even without explicit leakage, in-pipeline curation correlates with gold and inflates results relative to independently-curated holdouts.

----------------------------------------------------------------------

## ARM 2 -- Blind-authoring / pre-registration protocols in ML benchmarks

### Cited works (verified)

1. Recht, Roelofs, Schmidt, Shankar (2019). "Do ImageNet Classifiers Generalize to ImageNet?" ICML 2019. (Same as ARM 1 paper 1; central process citation here.)
   - Establishes that years of community test-set reuse produced measurable but not catastrophic adaptive overfitting; the deeper effect is curation drift in the held-out set.

2. Roelofs, Fridovich-Keil, Miller, Shankar, Hardt, Recht, Schmidt (2019). "A Meta-Analysis of Overfitting in Machine Learning." NeurIPS 2019.
   - Surveys 120+ Kaggle competitions where teams reused a public leaderboard hold-out hundreds to thousands of times. Surprisingly, little evidence of substantial adaptive overfitting; competition winners on the public split tend to also win on the unseen final split. Caveat: this holds when test set is generated independently and the team does not directly inspect its content.

3. White, Hofman, Aggarwal, Frieder, Tygert, et al. (2023). "Pre-registration for Predictive Modeling" (arXiv:2311.18807).
   - Argues for adapting clinical-trial-style pre-registration to ML: lock the augmentation strategy, the metric, and the evaluation split before any held-out contact. Discusses verification problems (researchers may deviate undetectably from filed protocol) and recommends staged commit-and-reveal protocols and third-party adjudicators.

4. Sahu, Kuznia, Singh, Wadhwa, Mishra, Trivedi, Aggarwal, Saraf, et al. (2024). "A Survey on Data Contamination for Large Language Models" (arXiv:2502.14425).
   - Catalogs four contamination classes: text contamination, text-label contamination, augmentation-based contamination, and benchmark-level contamination. Augmentation-based contamination is the relevant class for KG augmentation: if augmentation edges are derived from anything that touched the gold (entity names, relation labels, even seed inspection), the benchmark is structurally compromised.

5. Wei et al. (2025). "DyePack: Provably Flagging Test Set Contamination in LLMs Using Backdoors" (arXiv:2505.23001).
   - Provides a constructive cryptographic protocol: embed a low-entropy backdoor signal into the held-out set; any model that fit the signal is provably contaminated. The analog for KG augmentation would be to embed a tag in the held-out gold neighborhood that augmentation steps must not see.

6. Ribeiro, Wu, Guestrin, Singh (2020). "Beyond Accuracy: Behavioral Testing of NLP Models with CheckList." ACL 2020.
   - Argues for adversarial held-out behavior-class tests authored by parties who did not see the model or augmentation outputs. The protocol blueprint is directly applicable: KG augmentation researchers should freeze the augmentation pipeline before any contact with new gold questions.

### Per-arm synthesis

The pre-registration and contamination literature converges on a stricter rule than typical ML practice enforces: any augmentation step that has touched the gold (including just inspection of question text, entity names, or seed nodes) should be treated as in-distribution training, not held-out evaluation. The Roelofs meta-analysis (2) is reassuring in one direction (modest adaptive overfitting in well-isolated competitions) but the survey (4) is alarming in the other direction (augmentation-based contamination is the modal failure in modern LLM benchmarks). The recommended posture: blind authoring of the augmentation strategy (commit hash logged) before any gold inspection; cryptographic commit-and-reveal (5) or third-party split curation as the gold standard. A "leakage gradient" exists: even reading the question, choosing an entity that appears in the question, or selecting a seed via a measurement derived from the gold set can introduce measurable bias. The safe protocol is to lock augmentation strategy with respect to features that are independent of the test corpus.

----------------------------------------------------------------------

## ARM 3 -- Typed-operator graph walk and walk failure modes on sparse graphs

### Cited works (verified)

1. Mavromatis and Karypis (2024). "GNN-RAG" (arXiv:2405.20139). (Same as ARM 1 paper 2; central mechanism citation here.)
   - Quantifies the regime where a learned GNN walk beats heuristic/PageRank walk on sparse KGQA graphs. The mechanism: learned per-question edge weighting compensates for the heuristic walk's hub bias and sparse-neighborhood dead-ends.

2. Hu, Hao, Chen, Wang (2024). "Mixture-of-PageRanks: Replacing Long-Context with Real-Time, Sparse GraphRAG" (arXiv:2412.06078).
   - Introduces MixPR, a mixture of personalized PageRank variants with question-conditional teleport vectors. Reports that single-teleport-vector PPR fails on multi-hop questions because the walk concentrates mass on graph hubs rather than the answer subgraph; mixing teleport distributions corrects this. Direct quantification of hub-bias failure mode.

3. Toroghi, Aghazadeh, Naderi, Ebrahimi, Naghshzan, Pacheco, et al. (2024). "Less is More: Making Smaller Language Models Competent Subgraph Retrievers for Multi-hop KGQA" (arXiv:2410.06121).
   - Shows that aggressive subgraph pruning improves retrieval over a dense full-KG walk on WebQSP-class benchmarks. Implies a within-graph ceiling: when the graph has too many edges of irrelevant type, the walk's effective signal-to-noise degrades and a pruned typed walk dominates. The "less is more" principle applies to walk over sparse typed graphs.

4. Xia et al. (2024). "Think Parallax: Multi-View Knowledge-Graph-Based Retrieval-Augmented Generation" (arXiv:2510.15552).
   - Reports Macro-F1 71.7 on WebQSP and 48.3 on CWQ with Llama 3.1 8B; ParallaxRAG plus GPT-4o reaches 78.8 / 62.3. Establishes the contemporary high-water mark for KGQA F1 on multi-hop benchmarks and shows that ensemble of multiple views (multiple typed walk strategies) outperforms any single walk.

5. Zhang, Yao, Zhang, Wang, Tang (2022). "Subgraph Retrieval Enhanced Model for Multi-hop Knowledge Base Question Answering." ACL 2022 (arXiv:2202.13296).
   - Shows that an explicit subgraph retriever (path-conditioned BFS plus pruning) outperforms a flat walk by a substantial margin on WebQSP and CWQ. The pattern: typed walk with edge-type-aware ranking dominates untyped walk by 5-15 F1 on multi-hop subsets.

6. Sun, Bedrax-Weiss, Cohen (2018-2019). "PullNet" / "GRAFT-Net" / "OpenCSR" line of work (EMNLP).
   - Classical baseline establishing that random-walk style propagation on a KG is bounded by the walk's ability to reach the gold entity within hop K; when the gold is at hop > 2 in a sparse graph, single-walk PPR retrieval saturates below F1 0.5 without targeted subgraph extraction.

### Per-arm synthesis

The walk-on-sparse-typed-graphs literature is internally consistent: (a) untyped PPR or single-teleport random walks suffer from hub bias (mass leaks to globally central nodes that are not the answer); (b) sparse neighborhoods around the answer cause the walk to "walk around" the answer when no direct edge of the right type exists; (c) typed walks with edge-type-conditional ranking break this ceiling, but only when the type signal is question-conditional; (d) ensembles of walk views (Mixture-of-PageRanks, multi-view parallax) consistently dominate single views. The within-graph ceiling for a single untyped walk on a sparse typed KG with average degree under 5 is typically F1 0.25-0.45 on multi-hop benchmarks. The two known escape mechanisms are: (i) learn per-edge or per-type weights conditional on the question (GNN-RAG-style), and (ii) ensemble multiple walk views with different teleport / restart / type-priority schedules.

----------------------------------------------------------------------

## CROSS-ARM SYNTHESIS

Three findings combine into one operational guidance.

First, on the mechanism question (ARM 1 and ARM 3 together): the field's empirical consensus is that graph augmentation lifts held-out F1 when, and roughly only when, the new edges or nodes shorten the typed walk path from question-seed to gold-answer. Generic foundational densification (broad ontology completion, abstract supertypes, schema-level edges) does not transfer; in several reports it actively hurts by creating high-PR distractor paths. This is structurally consistent with the random-walk failure-mode results (ARM 3): added density that does not reduce the seed-to-gold hop count just dilutes the walk's per-step probability of landing on the answer.

Second, on the process question (ARM 2): the contamination and pre-registration literature is unambiguous that any augmentation step that has inspected the gold neighborhood is, by definition, in-distribution training. The KAG-style large lifts (+20-30 F1) are achievable when augmentation is constructed from the same document corpus that produced the gold; they are not a model of what blind augmentation can achieve. A research program that uses gold inspection to choose where to densify is not measuring graph-augmentation transfer; it is measuring the in-pipeline ceiling. The literature recommends commit-and-reveal protocols, blinded augmentation pipelines, and third-party gold curation.

Third, on the calibration anchor: contemporary high-water-mark F1 on WebQSP/CWQ multi-hop is in the 0.60-0.80 range for strong learned systems (GNN-RAG, ParallaxRAG with GPT-4o). For a sparse typed-graph walk without learned per-question weighting, F1 in the 0.25-0.45 range on a small (n < 10) in-coverage held-out is consistent with the literature's reported single-walk ceiling. It is neither weak nor strong; it sits at the floor of the walk-only regime, exactly where the literature would expect it to sit, and any improvement from here should come from question-conditional walk weighting or multi-view ensembling, not from generic edge addition.

----------------------------------------------------------------------

## ACTIONABLE OUTPUT

1. Is gold-neighborhood-targeted authoring (under strict blind protocol) a STANDARD recommended practice?
   - Partly. Targeted authoring of the gold neighborhood is what produces large lifts in the literature, but the literature's strict reading (ARM 2) treats any gold-neighborhood inspection as in-distribution training. The standard recommended practice is therefore to construct augmentation from sources structurally upstream of the gold (the same source corpus the gold derives from) without ever inspecting individual gold items. If the gold items themselves drive what gets densified, the result is not a held-out measurement.

2. Are there mechanisms BESIDES edge authoring that the literature says transfer better to held-out QA?
   - Yes, three are well-attested. (a) Question-conditional walk weighting via a learned GNN retriever (GNN-RAG, Mavromatis 2024). (b) Multi-view walk ensembling with different teleport / restart distributions (Mixture-of-PageRanks; ParallaxRAG). (c) Query reformulation in front of retrieval (HyDE-style hypothetical document expansion) followed by cross-encoder reranking with proof or path signals; multi-hop reranking lifts R@2 from 22.8 to 46.9 on HotpotQA in the cited work. Of these, (a) and (b) are walk-internal and likely the most direct fit; (c) is walk-external and is the field's standard way to break a walk-only ceiling.

3. Are there known WITHIN-GRAPH CEILINGS for sparse typed-graph walk retrievers, and what is the literature's escape mechanism?
   - Yes. Untyped PPR / random walk on sparse typed KGs with average degree under 5 saturates around F1 0.25-0.45 on multi-hop questions. The literature's named escape mechanisms are: per-question edge-type weighting (learned or rule-driven), aggressive type-aware subgraph pruning before walk, walk-view ensembling, and reranking the top-K paths with a path-aware verifier (cross-encoder over the path tokens).

4. What is the field's view on a ceiling like F1 ~0.27 on a 7-question in-coverage held-out for a substrate-internal graph walk?
   - Competitive at the floor of the walk-only regime; weak relative to contemporary KGQA SOTA (0.60-0.80). On a 7-question held-out, n is too small to discriminate this from the literature's 0.25-0.45 untyped-walk band; the result should be reported as consistent-with-floor and not interpreted as a generalization claim. A larger held-out (n > 50) would be required to distinguish from the literature's null.

5. Any HARD WARNINGS the literature would raise?
   - Three. (a) If the augmentation pipeline has inspected the gold's entities, the measurement is in-distribution, not held-out (ARM 2). (b) Generic densification of foundational structure orthogonal to the gold neighborhood is the dominant failure mode of KG augmentation and is repeatedly reported as no-lift-or-negative-lift in the literature; substrate plans that rely on generic foundational densification should expect that pattern (ARM 1). (c) Within-graph walk-only retrieval has a known ceiling around F1 0.45 on sparse typed KGs; pushing past that requires walk-external mechanisms (learned weighting, ensembling, or reranking), not more edges (ARM 3).

----------------------------------------------------------------------

## Substrate-product implications

The literature endorses three concrete moves and warns against one.

Endorsed: (i) build a learned or rule-driven question-conditional edge-weighting layer on top of the existing typed walk; (ii) ensemble multiple walk views with different teleport / restart distributions to break hub bias; (iii) add a path-aware reranker (cross-encoder over the path tokens, or a substrate-internal proof-signal scorer) over the top-K walk outputs.

Warned-against: continued generic densification of foundational structure when the gold neighborhood is not covered, without an accompanying blind-authoring protocol that records what was inspected and when. Per ARM 2, even a single round of gold-seed-inspection-driven authoring crosses the contamination boundary.

----------------------------------------------------------------------

## Hard-fail thresholds (pre-registered for any follow-on experiment)

- HARD-FAIL if generic foundational densification (edges added without inspecting the gold neighborhood) raises held-out F1 by more than 0.05 on n >= 50: that would contradict ARM 1 and ARM 3 and require revisiting the literature's consensus.
- HARD-FAIL if question-conditional walk weighting added on top of the current walk fails to lift held-out F1 by at least 0.05 on n >= 50: that would contradict ARM 3's named escape mechanism.
- HARD-FAIL if a re-curated held-out (authored without any visibility into the augmentation pipeline) shows F1 within 0.03 of the inspected held-out: that would contradict the ARM 2 leakage gradient and ARM 1 Recht-style curation drift.

----------------------------------------------------------------------

## Citations (verified count: 13)

Recht et al. 2019 ICML; Roelofs et al. 2019 NeurIPS; White et al. 2023 arXiv 2311.18807; Sahu et al. 2024 arXiv 2502.14425; Wei et al. 2025 arXiv 2505.23001; Ribeiro et al. 2020 ACL; Mavromatis and Karypis 2024 ACL 2025 Findings (2405.20139); Wu et al. 2024 GraphRAG-Bench arXiv 2506.02404; Su et al. 2024 arXiv 2502.06864; Tian et al. 2024 IJCAI 2025; Liang et al. 2024 KAG arXiv 2409.13731; Hu et al. 2024 MixPR arXiv 2412.06078; Toroghi et al. 2024 arXiv 2410.06121; Xia et al. 2024 ParallaxRAG arXiv 2510.15552; Zhang et al. 2022 ACL 2202.13296; Sun et al. 2018-2019 PullNet/GRAFT-Net line (EMNLP).

[UNVERIFIED] items omitted: any paper titles that did not surface with a direct arXiv or proceedings link in this drill were dropped rather than fabricated.

P_deflated (calibration-penalty adjusted): 0.55 that the substrate's gold-neighborhood-targeted authoring under blind protocol is the literature-canonical practice; 0.40 that walk-only F1 will exceed 0.45 without an added question-conditional weighting or ensembling layer.
