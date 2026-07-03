# Research drill — 5x drill component 5/5: ML/AI literature angle on substrate-content critical negative

**Date:** 2026-07-02
**Author:** research (Opus, team-lead) + 3 parallel Sonnet lit-scan sub-agents
**Trigger:** Stage 4 validation critical negative (verify-the-referent, off-disk): brain-analog competitive-Hebbian sparse (k=2%) LOSES to bag-of-char-trigrams on WordNet held-out-synonym retrieval, confirming Stage 4 caveat (c) real-corpus-transfer as FAILED. Substrate has ~140K real symbolic concepts (WordNet + ConceptNet + FrameNet + GO) but the brain-analog mechanism can't handle them.
**Method:** 3 parallel Sonnet WebSearch lit-scans (generic math/ML terms only, no substrate-novel names off-platform) + Opus synthesis. Lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]].
**Companion drills:** this is component 5/5 of a 5x drill; components 1-4 cover other angles (math/info-theory, etc. — see `research_5x_drill_2_math_info_theory_pc_complexity_2026-07-02.md` for a sibling component).

---

## 1. HEADLINE

**The GENERAL SHAPE of this failure — simple surface/lexical features beating learned representations on held-out / out-of-distribution retrieval — is a well-established, heavily-cited pattern in ML/IR (BEIR, Vapnik's principle, fastText "bag of tricks," Levy-Goldberg-Dagan). But the SPECIFIC combination tested here — a from-scratch competitive-Hebbian/WTA sparse network, at k~2% sparsity, applied to a real symbolic corpus (WordNet-style), evaluated on held-out synonym retrieval against a trigram baseline — has essentially ZERO direct precedent in the literature.** Competitive-Hebbian/WTA methods (SoftHebb and lineage) are validated almost exclusively on vision benchmarks; Foldiak's trace rule (1991) has never been applied to text in any citable published work found. The nearest analog family — sparse word-vector methods DERIVED FROM pretrained dense embeddings (SPOWV, SPINE, Word2Sense) — actually reports parity-or-improvement over dense baselines, not underperformance, which is an important counter-signal: sparsity per se is not the culprit; the LEARNING SIGNAL (local competitive/Hebbian vs. distributional/co-occurrence-derived) appears to be what matters.

**Verdict: hybrid — KNOWN FAILURE MODE at the pattern level, NOVEL FINDING at the mechanism-instance level.** P_deflated = **0.45** (see Section 7 for the calibration derivation; capped below the 0.50 novel-synthesis ceiling because this is a previously untested mechanism x corpus combination, not a replication of an existing negative result).

---

## 2. Cheap decisive test (carried over / sharpened from Stage 4)

The existing Stage 4 test (competitive-Hebbian sparse-k vs. trigram baseline on WordNet held-out-synonym retrieval) is already the cheap decisive test for the FAILURE observation. What the lit scan adds is a cheap decisive test for the DIAGNOSIS — i.e., is it the sparsity, or the learning signal, that's responsible?

**New cheap test:** Add a 3rd arm — sparse code derived from a co-occurrence/distributional signal (PPMI + top-k thresholding, or SVD-then-hard-threshold — a SPOWV/SPINE-style "sparsify a dense/distributional embedding" construction) — NOT a from-scratch competitive-Hebbian WTA network. Compare all three arms (dense distributional baseline, competitive-Hebbian sparse, PPMI-sparsified) against the trigram baseline on the same held-out-synonym WordNet task.

- **HARD-PASS for the "learning signal, not sparsity" diagnosis:** PPMI-sparsified arm recall/precision on held-out synonyms is within 10% (relative) of the dense distributional baseline AND beats trigram baseline by >=5 points absolute. This would show sparsity is not inherently the problem — a co-occurrence-derived sparse code transfers to real corpora while a locally-competitive one does not.
- **HARD-FAIL for that diagnosis:** PPMI-sparsified arm ALSO loses to trigram baseline by a similar margin as the competitive-Hebbian arm. This would mean the failure is about SPARSITY ITSELF at k~2% on symbolic data (a much bigger structural problem, since it would refute the SPOWV/SPINE precedent transferring to WordNet-scale symbolic-relation data specifically, as opposed to word-vector-similarity data).
- **MIDDLE-BAND:** PPMI-sparsified beats competitive-Hebbian arm materially (>10 points) but still loses to trigram. This would mean "sparsify-a-distributional-signal" is a real improvement direction but insufficient alone — additional engineering (dimensionality, thresholding strategy, or hybrid lexical+distributional scoring) is needed.

Cost: cheap — PPMI computation and top-k thresholding on an already-tokenized WordNet-derived corpus is minutes of CPU; no training loop, no gradient, reuses existing held-out-synonym eval harness from Stage 4.

---

## 3. Falsifiable predictions

**Prediction 1 (sparsity-is-not-the-problem):** If the diagnosis in Section 2 confirms "learning signal not sparsity," then ANY future forward-only/Hebbian-style mechanism that routes through a co-occurrence-derived (not purely locally-competitive) signal should also transfer to real corpora. HARD-FAIL: co-occurrence-derived sparse arm ALSO loses to trigram (implies the WordNet-held-out-synonym task itself may be dominated by morphological overlap that NO distributional method, sparse or dense, can beat without lexical features — see Section 6).

**Prediction 2 (vision-bias artifact):** Given that SoftHebb/competitive-Hebbian and Foldiak-trace have literally never been validated on text (not "tried and failed" but "never tried"), the HF observed here may be the FIRST published-adjacent data point on this exact question. If so, a wider sweep (different k, different corpus, different competitive-learning variant) should show the failure is ROBUST (not sensitive to k or corpus choice) if it is a structural mismatch between local-competitive learning and symbolic/discrete co-occurrence statistics. HARD-FAIL for "structural mismatch" claim: a modest k sweep (k=1%, 4%, 8%) or corpus swap (ConceptNet vs WordNet) flips the ranking — implies this was a narrow config-specific failure, not a mechanism-class failure (consistent with memory [[feedback-measured-bounds-are-method-config-contingent]]).

**Prediction 3 (benchmark contamination):** Given the Faruqui et al. 2016 critique that intrinsic word-similarity benchmarks are poorly validated, and the absence of any published decomposition of WordNet-synonym accuracy into "true semantic" vs. "morphological overlap" components, part of the trigram baseline's apparent strength may be an artifact of WordNet synonym pairs sharing substrings/roots (a lexicographic-construction artifact, not a semantic one). HARD-PASS for this alternative explanation: on a MORPHOLOGY-CONTROLLED held-out subset (synonym pairs with <20% character n-gram overlap, e.g. "car"/"automobile"), competitive-Hebbian sparse recall improves relative to trigram (even if it doesn't fully close the gap). HARD-FAIL: trigram baseline STILL wins on the morphology-controlled subset — this would mean the failure is genuinely about the learned representation's semantic content, not a benchmark artifact.

---

## 4. Cross-thread synthesis

- **Prior substrate note `research_drill_sparse_allocation_routing_learning_2026-06-23.md`:** established that SoftHebb's prior HARD_FAIL was on ENCODER-WEIGHT learning at sigma=1.5 noise robustness (a different layer/problem than allocation-routing). This lit-scan's finding that SoftHebb has literally never been applied to text at all (vision-only in both the original paper and all follow-ups, including the 2024 survey arXiv:2407.17305) SHARPENS that prior finding: the SoftHebb precedent (Moraitis 2021, Journe 2022) was ALWAYS vision-scoped, so neither the prior HARD_FAIL nor this new HF should be read as "SoftHebb was tried on text and failed twice" — it is "SoftHebb-family mechanisms have zero text validation in the literature, and the substrate's two independent tests (encoder noise-robustness, and now WordNet held-out-synonym retrieval) are among the only data points that exist anywhere for this mechanism-class x text-domain combination."
- **Prior substrate note `research_drill_substrate_vs_competitors_tier4_2x_2026-06-07.md`:** noted Hebbian-FW (arXiv 2510.21908) validated only on Omniglot/CIFAR-FS (toy vision-adjacent benchmarks), reinforcing the same absence-of-text-validation pattern found independently in this drill for SoftHebb and Foldiak-trace. Three separate substrate research threads now independently converge on: **the entire competitive/fast-weight Hebbian literature is vision-and-toy-benchmark bound; text is uncharted territory for this whole mechanism family.**
- **Prior substrate note `exp_dev_handoff_research_field_modern_hopfield_5x_2026-06-07.md`:** sparse Hopfield (Hu et al. 2023, arXiv:2402.13725) showed TIGHTER retrieval bounds than dense at top-k sparsemax attention — but this is a DIFFERENT mechanism class (associative-memory retrieval with a global energy function / attention-style softmax-to-sparsemax substitution) from competitive-Hebbian WTA (local, no global energy/attention structure). The lit-scan in this drill found no evidence that sparse-Hopfield's advantage transfers to allocation/coding-style competitive Hebbian networks — these are mathematically distinct sparsity mechanisms (attention-sparsification vs. representation-sparsification) and should not be conflated. This is a genuine adjacency worth a follow-up drill (Trigger C, adjacency-cascade): does sparse-Hopfield-style RETRIEVAL sparsity (not competitive-Hebbian ENCODING sparsity) fare better on WordNet-style symbolic retrieval?
- **Prior substrate note `exp_dev_to_research_exconcept_honest_baselines_2026-06-05.md`:** substrate's own honest-baseline history already found char-trigram beating substrate's next-concept generative mechanism at the bigram/trigram level on a DIFFERENT task (sequence prediction). This is now the THIRD substrate-internal instance of "simple lexical baseline matches or beats a more elaborate mechanism" — a recurring internal pattern that this lit-scan confirms is ALSO a recurring EXTERNAL pattern (BEIR, fastText, Levy-Goldberg-Dagan). The substrate's own experience is not an outlier; it is a specific instance of a documented, general phenomenon.
- **META atom implication:** the convergence across 3 substrate-internal threads (allocation-routing note, competitor-comparison note, honest-baseline note) plus this external lit-scan supports promoting a substrate-level META: "trigram/lexical-overlap baselines are disproportionately strong on THIS substrate's real-corpus tasks specifically because WordNet/ConceptNet-style resources are lexicographically constructed with high morphological regularity — any new mechanism must be benchmarked against trigram baseline BY DEFAULT, not as an afterthought." This is consistent with existing memory [[feedback-clean-encoder-tests]] and [[feedback-brain-grounded-higher-prior]] tension: brain-groundedness gives a prior, but does not exempt a mechanism from the trigram-baseline gate.

---

## 5. Substrate-product implications

**If the Section-2 diagnosis test HARD-PASSes (learning signal is the problem, not sparsity):** the substrate should NOT abandon sparse/brain-analog coding wholesale. Instead, pivot the mechanism from "sparse code learned via local competitive/Hebbian dynamics" to "sparse code DERIVED FROM a distributional/co-occurrence signal" (PPMI-then-threshold, or SVD-then-threshold) — this is forward-only-compatible (no backprop needed, PPMI/SVD are closed-form), reuses existing chain-grade KG co-occurrence statistics, and has direct, positive lit precedent (SPOWV/SPINE/Word2Sense) at word-level tasks, plus Random Indexing's ~72% TOEFL-synonym accuracy for a VSA/HDC-flavored precedent using distributional (not competitive-Hebbian) input. Cost: cheap (closed-form, no training loop) — could be a 1-cycle cell.

**If the Section-2 diagnosis test HARD-FAILs (sparsity itself is the problem at k~2% on symbolic data):** this is a much bigger structural finding — it would mean the substrate's core sparse-coding bet is mismatched to real symbolic/relational corpora regardless of HOW the sparse code is learned. Product implication: the substrate's competitive advantage would need to be repositioned away from "brain-analog sparse coding beats simple baselines on real content" and toward the compliance/compositional/audit-trail differentiators already identified in `research_drill_substrate_vs_competitors_tier4_2x_2026-06-07.md` (GDPR Art.17 erasure, bitemporal queries, per-fact provenance) — i.e., the moat is structural/compliance, not representational-quality, for real symbolic corpora. This does NOT close synthetic/controlled-corpus capability results (chain-grade KG, capacity-cliff, etc.), which remain valid on their own terms; it specifically bounds the "beats simple baselines on REAL uncontrolled text" claim.

**Either way:** the substrate should NOT interpret this HF as "sparse/brain-analog mechanisms are dead" — the lit scan found the negative result is UNPRECEDENTED (no one has published this exact test), so it's new information, not a confirmation of an already-known dead end. The honest read is: brain-analog competitive-Hebbian sparse coding, in its purest from-scratch form, has never had a text success story published anywhere — the substrate is at the frontier of testing it, not repeating someone else's failed experiment.

---

## 6. ML/AI verdict — known failure mode or novel finding? (calibration penalty applied explicitly)

**Decomposing the claim into two levels:**

**(a) Pattern-level claim: "simple surface features beat learned/dense representations on held-out or out-of-distribution retrieval."** This is a KNOWN, well-established, heavily-replicated finding:
- BEIR (Thakur et al. 2021, arXiv:2104.08663): BM25 (pure lexical) beats most dense neural retrievers zero-shot/out-of-domain across 18 datasets, even though dense wins in-domain.
- Vapnik's principle (Vapnik 1998, *Statistical Learning Theory*): don't solve a harder, more general problem (learn "meaning") when a narrower, more direct one (lexical overlap) suffices for the task at hand.
- fastText "Bag of Tricks" (Joulin et al. 2016, arXiv:1607.01759): simple bag-of-n-grams linear classifier on par with deep models.
- Levy, Goldberg & Dagan 2015 (TACL, ACL Anthology Q15-1016): word2vec/GloVe's apparent superiority over classical count-based methods evaporates once hyperparameters are matched.
- Domain-specific analog found: BERT failing to beat TF-IDF on tasks where "the correct answer is defined by exact/near-exact token identity rather than paraphrase" — structurally identical to WordNet synonym pairs, which are lexicographically curated and often share morphological roots.

Raw P for "the pattern-level explanation accounts for the observed HF" before calibration: ~0.70 (strong, repeated, multi-source confirmation).

**(b) Mechanism-instance-level claim: "THIS specific brain-analog competitive-Hebbian sparse (k=2%) mechanism, applied to real symbolic corpora specifically, is a documented failure."** This is NOT established — it is UNTESTED territory:
- SoftHebb/competitive-Hebbian (Moraitis 2021 arXiv:2107.05747; Journe 2022 arXiv:2209.11883; 2024 survey arXiv:2407.17305): vision-only, zero text applications found across multiple independent search angles.
- Foldiak's trace rule (1991, *Neural Computation* 3(2):194-200): zero text applications found; vision/neuroscience only, including all descendants (Wallis & Rolls 2012, PMC3385587).
- Kohonen SOM on real corpora: thin evidence, and what exists (Springer LNCS chapter, IJCTE 2009) suggests SOM does REASONABLY on document classification vs other unsupervised methods — not a clean confirmatory negative for the specific retrieval-task framing here.
- HDC/VSA on WordNet-style symbolic retrieval: Kleyko et al. 2022 surveys (arXiv:2111.06077, arXiv:2112.15424) catalog general text applications but no controlled WordNet-retrieval-vs-dense-baseline comparison was found — genuinely open/understudied.
- Counter-signal: sparse-word-vector methods DERIVED FROM dense embeddings (SPOWV/Faruqui 2015 arXiv:1506.02004, SPINE/Subramanian 2018 arXiv:1711.08792, Word2Sense/Panigrahi 2019) report PARITY OR IMPROVEMENT over dense baselines on interpretability and some similarity tasks — meaning "sparse loses on text" is NOT a clean, unconditional rule even within the sparse-representation literature. The one clear negative case found (Faruqui SimLex-999 sparse vectors underperforming the original skip-gram they were derived from) is a secondary-source-paraphrased finding, not independently verified from primary text — flagged as needing direct verification if load-bearing.

**Calibration applied:** per [[feedback-lit-scan-calibration-penalty]], deflate by 0.15-0.25 for uncharted-regime status (competitive-Hebbian x text x held-out-synonym-retrieval has no published precedent at all), and cap novel-synthesis P at 0.50 (this drill's synthesis — "the failure is about learning-signal not sparsity" — is itself a novel hypothesis, not lit-confirmed).

Starting from the pattern-level P (~0.70) and applying the maximum deflation (0.25) for the mechanism-instance gap: **0.70 - 0.25 = 0.45.**

**P_deflated = 0.45** that "known ML pattern (surface features beat learned reps OOD) fully explains this HF, AND the specific diagnosis that it's the local-competitive learning signal (not sparsity per se) that's responsible" — capped comfortably under the 0.50 novel-synthesis ceiling.

**Bottom line: this is a KNOWN FAILURE MODE AT THE PATTERN LEVEL (bag-of-features-beats-learned-reps-OOD is textbook IR/NLP knowledge) but a NOVEL FINDING AT THE MECHANISM-INSTANCE LEVEL (no one has published this exact competitive-Hebbian x WordNet x held-out-synonym test before).** The substrate is not repeating a known failed experiment; it is generating new data at the intersection of two separately-documented phenomena that had never been combined in the literature.

---

## 7. Recommended v2 mechanism variants from ML/AI lit, with citations

Ranked by cost (cheapest first) and directness of lit precedent:

**V2-A (top pick): sparsify a co-occurrence/distributional signal instead of learning sparse codes via local competitive dynamics.** Compute PPMI or SVD-reduced co-occurrence vectors over the existing chain-grade KG / WordNet-derived corpus (closed-form, no training loop), then hard-threshold to top-k per position (matching current k~2% sparsity budget) to get a sparse code. This directly mirrors SPOWV (Faruqui et al. 2015, ACL, arXiv:1506.02004) and SPINE (Subramanian et al. 2018, AAAI, arXiv:1711.08792), both of which sparsify an existing distributional/dense signal and report parity-or-improvement over the dense original on similarity and interpretability tasks — i.e., sparsity survives when it's a POST-HOC transform of a distributional signal rather than a from-scratch locally-learned code. Cost: cheap, forward-only, no backprop, reuses existing co-occurrence infrastructure.

**V2-B: distributional random-projection (Random Indexing) instead of competitive-Hebbian allocation.** Build sparse random ternary "index vectors" for context words and accumulate them (Sahlgren, "An Introduction to Random Indexing," 2005 and subsequent TOEFL-synonym work) — reports ~72% accuracy on TOEFL-style synonym tests with lemmatization, using a co-occurrence-accumulation signal, NOT a competitive/WTA learning rule. This is the closest VSA/HDC-flavored precedent with an actual reported synonym-retrieval number, and it succeeds by leaning on distributional statistics rather than local competition. Cost: cheap-moderate (accumulation over corpus, no gradient).

**V2-C: learned-sparse retrieval with a GLOBAL contrastive/gradient signal (SPLADE-style), if backprop-fallback is authorized.** SPLADE-family learned-sparse retrieval closes/reverses the BM25-vs-dense gap by keeping sparse activation over a vocabulary-sized space but training it with a global contrastive objective (not a local Hebbian rule). This is evidence that SPARSITY is not the bottleneck — the GLOBAL LEARNING SIGNAL is what competitive-Hebbian lacks. Only recommended as fallback if V2-A and V2-B both HARD-FAIL the Section-2 diagnostic, consistent with the existing substrate policy (per `research_drill_sparse_allocation_routing_learning_2026-06-23.md`) of trying minimum-viable forward-only variants before authorizing backprop infrastructure.

**Explicitly NOT recommended without a fresh cheap test first:** a second from-scratch competitive-Hebbian/WTA variant (e.g., different k, different lateral-inhibition schedule) on the SAME corpus. Per [[feedback-2x-drill-negatives-before-capability-closure]] and the substrate's own prior discipline (`research_drill_sparse_allocation_routing_learning_2026-06-23.md`: "if HARD_FAIL, do NOT propose a 2nd Hebbian-allocation variant"), re-trying the same mechanism CLASS on the same corpus without changing the learning signal is the lowest-value next move given the lit scan's finding that the learning signal (not sparsity, not the corpus) is the most likely culprit.

---

## Citations (verified count: 34 unique sources across 3 parallel lit-scans, deduplicated)

**Competitive-Hebbian / SoftHebb / fast-weight (vision-only, zero text validation found):**
1. Moraitis, Toichkin, Journe, Chua, Guo. "SoftHebb: Bayesian Inference in Unsupervised Hebbian Soft Winner-Take-All Networks." arXiv:2107.05747; *Neuromorphic Computing and Engineering* (IOP), 2022.
2. Journe, Garcia Rodriguez, Guo, Moraitis. "Hebbian Deep Learning Without Feedback." arXiv:2209.11883, ICLR 2023.
3. "Continual Learning with Hebbian Plasticity in Sparse and Predictive Coding Networks: A Survey and Perspective." arXiv:2407.17305.
4. Hebbian-FW (fast-weight modules): arXiv:2510.21908; companion ViT integration arXiv:2605.02920 (Omniglot/CIFAR-FS/DeiT/Swin, toy-scale, no text).

**Sparse word-vector methods (derived from dense; parity/improvement, NOT clean underperformance):**
5. Murphy, Talukdar, Mitchell. "Learning Effective and Interpretable Semantic Models Using Non-Negative Sparse Embedding" (NNSE). COLING 2012, ACL Anthology C12-1118.
6. Faruqui, Tsvetkov, Yogatama, Dyer, Smith. "Sparse Overcomplete Word Vector Representations" (SPOWV). ACL 2015, arXiv:1506.02004.
7. Subramanian, Pruthi, Jhamtani, Berg-Kirkpatrick, Hovy. "SPINE: SParse Interpretable Neural Embeddings." AAAI 2018, arXiv:1711.08792.
8. Panigrahi, Simhadri, Bhattacharyya. "Word2Sense: Sparse Interpretable Word Embeddings." ACL 2019.
9. Berend. "Sparse Coding of Neural Word Embeddings for Multilingual Sequence Labeling." TACL 2017, arXiv:1612.07130.

**Modern sparse autoencoders on LM activations (clean negative results, different setup than from-scratch sparse coding):**
10. "Negative Results for Sparse Autoencoders on Downstream Tasks and Deprioritising SAE Research." DeepMind interpretability team, 2025.
11. "Disentangling Dense Embeddings with Sparse Autoencoders." arXiv:2408.00657.
12. "Decoding Dense Embeddings: Sparse Autoencoders for Interpreting and Discretizing Dense Retrieval." arXiv:2506.00041.
13. "Rethinking Evaluation of Sparse Autoencoders through the Representation of Polysemous Words." arXiv:2501.06254.

**Kohonen SOM on text (thin evidence):**
14. "Self-Organising Maps in Document Classification: A Comparison with Six Machine Learning Methods." Springer LNCS 978-3-642-20282-7_27, 2011.
15. "Classification of Documents Using Kohonen's Self-Organizing Map." IJCTE 1(5), 2009.
16. "Self Organizing Map-based Document Clustering Using WordNet Ontologies." IJCSI 9(1-2), 2012.

**Foldiak trace rule (vision/neuroscience only, zero text applications found):**
17. Foldiak. "Learning Invariance from Transformation Sequences." *Neural Computation* 3(2):194-200, 1991.
18. Wallis, Rolls et al. "Learning and Disrupting Invariance in Visual Recognition with a Temporal Association Rule." *Frontiers in Computational Neuroscience*, 2012, PMC3385587.
19. Wiskott & Sejnowski Slow Feature Analysis (Scholarpedia); "Robustifying ASR by Extracting Slowly Varying Features." arXiv:2112.07400.

**Sparse coding theory / curse of dimensionality:**
20. Olshausen, Field. "Emergence of simple-cell receptive field properties by learning a sparse code for natural images." *Nature* 381, 1996.
21. "Can a Hebbian-like learning rule be avoiding the curse of dimensionality in sparse distributed data?" *Biological Cybernetics*, 2024, PMC11588804.

**Contrastive learning / learned-sparse retrieval:**
22. Gao, Yao, Chen. "SimCSE: Simple Contrastive Learning of Sentence Embeddings." EMNLP 2021, arXiv:2104.08821.
23. "Sparse Contrastive Learning of Sentence Embeddings" (SparseCSE). arXiv:2311.03881.
24. Xiong et al. "Approximate Nearest Neighbor Negative Contrastive Learning for Dense Text Retrieval" (ANCE). arXiv:2007.00808.
25. Chuang. "Information Retrieval with Dense and Sparse Representations." MIT MS Thesis, 2024.

**HDC / VSA / holographic on symbolic retrieval:**
26. Kleyko, Davies, Frady, Kanerva, Kent, Olshausen, Osipov, Rabaey, Rachkovskij, Rahimi, Sommer. "Vector Symbolic Architectures as a Computing Framework for Emerging Hardware." *Proc. IEEE*, arXiv:2106.05268, 2022.
27. Kleyko, Rachkovskij, Osipov, Rahimi. "A Survey on Hyperdimensional Computing aka VSA, Part I." *ACM Computing Surveys*, arXiv:2111.06077, 2022.
28. Kleyko, Rachkovskij, Osipov, Rahimi. "A Survey on Hyperdimensional Computing aka VSA, Part II: Applications." *ACM Computing Surveys*, arXiv:2112.15424, 2022.
29. Sahlgren. "An Introduction to Random Indexing." 2005, and TOEFL-synonym-test extensions.
30. Jones, Mewhort. "Representing Word Meaning and Order Information in a Composite Holographic Lexicon" (BEAGLE). *Psychological Review* 114(1), 2007.
31. Recchia, Jones, Sahlgren, Kanerva. "Toward a Scalable Holographic Word-Form Representation." *Behavior Research Methods* 43, 2011.
32. Hu et al. "Sparse Hopfield / sparse modern Hopfield networks with tighter retrieval bounds." arXiv:2402.13725, 2023 (adjacency reference, not directly tested on WordNet).

**Bag-of-features / simple-baseline-beats-learned-reps OOD pattern (well-established):**
33. Thakur, Reimers, Rücklé, Srivastava, Gurevych. "BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of IR Models." NeurIPS D&B, arXiv:2104.08663, 2021.
34. Joulin, Grave, Bojanowski, Mikolov. "Bag of Tricks for Efficient Text Classification." arXiv:1607.01759, 2016.
35. Levy, Goldberg, Dagan. "Improving Distributional Similarity with Lessons Learned from Word Embeddings." TACL, ACL Anthology Q15-1016, 2015.
36. Hendrycks et al. "Pretrained Transformers Improve Out-of-Distribution Robustness." arXiv:2004.06100, 2020.
37. "Specialized Foundation Models Struggle to Beat Supervised Baselines." arXiv:2411.02796, 2024.
38. "Bag-of-Words vs. Graph vs. Sequence in Text Classification." ACL 2022, aclanthology.org/2022.acl-long.279.

**Benchmark validity / morphological-overlap confound in word-similarity tasks:**
39. Faruqui, Tsvetkov, Rastogi, Dyer. "Problems With Evaluation of Word Embeddings Using Word Similarity Tasks." arXiv:1605.02276, ACL Anthology W16-2506, 2016.
40. Hill, Reichart, Korhonen. "SimLex-999: Evaluating Semantic Models With (Genuine) Similarity Estimation." *Computational Linguistics* 41(4), arXiv:1408.3456, 2015.
41. "Antonyms are similar: paradigmatic association approach to rating similarity in SimLex-999 and WordSim-353." ScienceDirect.
42. Muennighoff et al. "MTEB: Massive Text Embedding Benchmark." EACL, aclanthology.org/2023.eacl-main.148, 2023.
43. Reimers, Gurevych. "Sentence-BERT." EMNLP 2019, arXiv:1908.10084.

Total distinct sources cited across the 3 sub-agent scans: **43** (some overlap between sub-agents on Kleyko/Faruqui/SoftHebb citations was deduplicated in this list; raw combined citation count before dedup was ~49).

---

## Confidence caveats (carried from sub-agent reports, not smoothed over)

- The Faruqui et al. 2015 "sparse vectors underperformed original skip-gram on SimLex-999" finding was reported via search-snippet paraphrase by one sub-agent, NOT a directly-fetched primary-source quote. Flag for direct verification (fetch the ACL PDF table) before treating as load-bearing evidence for "sparse loses to dense on lexical-similarity."
- The SOM-vs-baseline comparison (Springer LNCS chapter) was also snippet-only (paywalled). Treat as weak/indicative, not confirmed.
- No sub-agent found a directly-fetched primary source establishing WHY sparse coding underperforms on discrete/symbolic vs continuous image data at a theoretical level — this remains an open question, not a citable closed theorem.
- The WordNet-synonym-retrieval-vs-BERT-with-morphology-decomposition question (Q9 in the task) came back as a genuine literature GAP, not a resolved finding either way — treat the substrate's own morphology-controlled subset test (Prediction 3, Section 3) as the way to close this gap rather than expecting a prior citation to resolve it.
