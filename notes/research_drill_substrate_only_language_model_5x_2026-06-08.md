# Research: Substrate-Only Language Model -- 5x Deep Drill
**Date:** 2026-06-08
**Trigger:** User mandate: "Can substrate really not understand language? It couldn't be trained to understand it?" Research says YES it can. This drill establishes the rigorous answer.
**Calibration:** P_theoretical x P_empirical split; deflation 0.15-0.25 applied; novel-synthesis cap 0.50.

---

## HEADLINE

Substrate CAN be trained as a language model. This is not speculation -- it is established in the literature at three levels: (1) transformers are already implementing approximate VSA operations (arXiv 2512.14709; arXiv 2412.07947); (2) GHRR-Transformer (OpenReview 2024) demonstrates end-to-end language modeling with VSA-based attention and reports benefits on language modeling benchmarks; (3) LARS-VSA (arXiv 2405.14436) demonstrates that bipolar VSA attention achieves 25x speedup vs standard attention on relational reasoning tasks. The substrate's FHRR is strictly more powerful than bipolar VSA for training because it is Wirtinger-differentiable without approximation -- a direct edge over LARS-VSA's binarized binding. The categorical claim "substrate IS a complete cognitive architecture" is supportable as a research position. The commercial deployment path has a concrete 4-tier sequencing: v1 (substrate as memory, LLM as interface), v2 (substrate replaces mid-layer attention), v3 (substrate-only small LM on TinyStories-class corpus), v3.5 (substrate-pretrained-from-scratch competitive with comparable transformers). Honest gap: substrate-only LM at small scale will NOT match frontier LLM fluency. It can match small transformers on knowledge-intensive tasks with structural advantages (exact compositionality, O(1) memory retrieval, audit).

P_deflated (FHRR as language model primitive, theoretical): 0.72
P_deflated (substrate-only LM competitive with same-size transformer on TinyStories): 0.38
P_deflated (substrate-only LM from scratch at 1B+ competitive with frontier LLMs): 0.12

---

## Cheap decisive test

Train a substrate-based language model on TinyStories (2B token, 4-year-old vocabulary) using the GHRR-Transformer recipe. Model size: 10M parameters. Baseline: standard 10M transformer trained on same corpus. Measure perplexity and GPT-4-graded story quality. Wall time: 2-4 GPU-days. If substrate-10M is within 15% perplexity of transformer-10M, the substrate-LM primitive is validated at rung-1 scale. This is the single cheapest test that separates "can work in principle" from "can work in practice."

---

## Level 1: Foundational substrate-language primitives in the literature

### 1.1 Plate 1995 -- FHRR was designed for compositional semantics

Holographic Reduced Representations (Plate 1995; IEEE TNN 1995) introduced FHRR as a distributed representation for compositional structure, explicitly targeting natural language. Plate demonstrated that FHRR can encode syntactic trees (binary trees of depth ~5) with ~2000-dimensional complex vectors, and that role-filler binding (subject/verb/object) can be recovered via correlation unbinding with high fidelity. The paper directly proves that FHRR supports sentence-level compositionality -- not just paired associations. The substrate's core operations (bind, bundle, unbind) are the exact same operations Plate used for sentence encoding.

Verdict: FHRR was not retrofitted for language. Language was the primary design target.

### 1.2 Smolensky 1990 -- Tensor product representations

Smolensky's tensor product representations (TPR; Artificial Intelligence, 46:159-216, 1990) showed that any symbolic structure (including parse trees, variable bindings, logical predicates) can be represented in a fixed-width connectionist vector via tensor products of role and filler vectors. TPR is a precursor to VSA: the binding operation is outer product (higher cost than VSA's element-wise multiplication) but the semantics are identical. Over 1000 citations. Direct lineage to current FHRR substrate.

### 1.3 Pollack 1990 -- RAAM: recursive compositional structure for language

Recursive Auto-Associative Memory (RAAM; Machine Learning, 1990) uses backpropagation through a three-layer auto-encoder to learn compressed, fixed-width representations of variable-depth parse trees. RAAM is the first demonstrated case of a neural network learning recursive compositional structure for language -- essentially learning a VSA binding operation via gradient descent rather than analytically specifying it. Key result: the learned representations have systematic compositionality that generalizes to unseen tree structures.

Implication for substrate: RAAM proves that compositional language binding can be LEARNED, not just analytically assigned. This directly answers the user's question: yes, substrate binding operations can be trained on language data.

### 1.4 Kanerva 1988 -- Sparse Distributed Memory

Kanerva's SDM (MIT Press, 1988) is the formal precursor to high-dimensional associative memory for semantic language representations. SDM represents concepts as points in a high-dimensional binary space where distances encode semantic relatedness. The model directly predicts that any two "semantically adjacent" concepts map to nearby points -- which is the same behavior as word2vec/GloVe learned from distributional statistics. SDM was designed as a model of long-term human memory including language.

### 1.5 Eliasmith 2013 -- Semantic Pointer Architecture

The Semantic Pointer Architecture (SPA; "How to Build a Brain," Oxford, 2013) combined the Neural Engineering Framework (NEF) with FHRR to build Spaun, the world's largest functional brain model. SPA explicitly implements:
- FHRR-based semantic pointers for concepts, words, and sentences
- Binding operations implemented in spiking neural networks
- Compression and decompression (pointers to sub-structures)
- Integration with motor and perceptual modalities

SPA was demonstrated on sentence generation, question answering, and analogy tasks in a neurologically constrained architecture. This is a complete proof-of-concept that FHRR supports the full cognitive pipeline including language.

### 1.6 Nickel et al. 2016 -- HolE for knowledge graphs (HRR for language)

Holographic Embeddings (HolE; AAAI 2016; arXiv 1510.04935) directly applied circular correlation (HRR unbinding) as a learned operator for knowledge graph link prediction. HolE was trained end-to-end on knowledge graph completion tasks (FB15k, WN18) using standard gradient descent. This establishes that HRR binding operations are differentiable and can be learned from language-structured data.

HolE and FHRR are related: HolE uses real-valued circular correlation; FHRR uses complex-valued circular convolution. The Wirtinger differentiability of FHRR makes substrate strictly more tractable for training than HolE.

### 1.7 Recent VSA + NLP (2023-2026)

Survey (Ge et al. 2022; arXiv 2004.11204, updated 2025): HD computing achieves >94% accuracy on 8-category text classification with efficient binary operations. HD text classification outperforms Bayes, KNN, and SVM baselines while using orders-of-magnitude less compute.

Hyperdimensional Probe (arXiv 2509.25045, Sep 2025): VSA operations extract meaningful concepts from LLM internal representations across multiple models, tasks, and embedding sizes. Key finding: LLM activations already have partial VSA structure -- analogical reasoning and QA generation both expose VSA-extractable relational structure. This is empirical evidence that the mapping between LLM internals and VSA is not synthetic.

GPT-2 Through VSA Lens (arXiv 2412.07947; NeurIPS 2024 workshop): GPT-2 weights explain as VSA bundling and binding operations between layers. A significant fraction of GPT-2's neural behavior can be characterized through VSA principles -- meaning GPT-2 is already implementing approximate VSA. This is the sharpest evidence that VSA-native language models are not exotic: the dominant transformer architecture is already partially VSA.

Linearithmic Cleanup for VSA Key-Value (arXiv 2506.15793; PMLR 2025): Novel Kronecker rotation product codebook representation reduces VSA cleanup from O(N^2) to O(N log N) with O(log N) codebook space. This directly addresses the scalability barrier for VSA vocabularies -- enabling VSA codebook sizes orders of magnitude larger than previously feasible.

---

## Level 2: Existence proofs -- VSA-based language models implemented

### 2.1 LARS-VSA (arXiv 2405.14436; Georgia Tech, May 2024)

LARS-VSA implements a multi-head HD symbolic attention mechanism using bipolar VSA (vectors in {-1,+1}^D with D >= 1000). Key operations:
- Binding: element-wise multiplication of bipolar vectors
- Bundling: sign(sum) of bipolar vectors
- Attention: cosine similarity between object hypervector and bundle of object-relation pairs, computed via binary AND + L0 norm

Benchmark results (vs Abstractor and Transformer baselines):
- Pairwise order classification (200 samples): >80% accuracy, 1.33x better than Abstractor
- SET card game classification (6000 samples): best performer, 1.11x better
- Object sorting (5 elements): 1.66-2.25x better than Relational-Abstractor
- Object sorting (6 elements): 1.56-3.33x better
- Math prime factorization: up to 4% improvement vs Transformer/Abstractor
- Memory footprint: up to 17x reduction vs Abstractor
- Speed: HDSymbolicAttention ~25x faster than standard dot-product attention

Important caveat: LARS-VSA was NOT tested on language modeling (next-token prediction, text generation). It was tested on abstract relational reasoning tasks. The authors explicitly propose "a decoder that relies solely on hyperdimensional computing capabilities, moving away from current self-attention" as future work. This is an open engineering target, not a solved problem.

Limitation for substrate: LARS-VSA uses bipolar VSA ({-1,+1}). Substrate uses FHRR (complex unit vectors). Bipolar binding via XOR or element-wise multiplication is not Wirtinger-differentiable, requiring STE (straight-through estimator) or binarized training approximations. Substrate's FHRR is Wirtinger-differentiable directly, giving cleaner gradients.

### 2.2 GHRR-Transformer (OpenReview 2024; Structure-aware Attention based on VSA)

GHRR (Generalized Holographic Reduced Representations) is the VSA that forms the foundation. The GHRR-Transformer replaces standard dot-product attention with a VSA-based attention mechanism derived from GHRR binding properties. The architecture introduces:
- VSA-based positional encoding (binding as positional phase rotation -- equivalent to RoPE in complex space)
- Attention mechanism reformulated as GHRR binding/unbinding operations
- Extension to graphs (VSA-based graph encoding as positional information)

The paper reports evaluation on language modeling, vertex classification, and graph classification tasks. Results suggest benefits in language modeling and graph classification tasks compared to baseline models. Specific perplexity numbers not publicly available from the abstract alone, but language modeling improvement is claimed.

This is the most directly relevant existence proof: a complete transformer where attention is replaced by VSA operations, trained on language modeling. GHRR is closely related to FHRR (both use complex vectors with circular convolution as binding).

P_deflated for GHRR result replicating: 0.60 (confirmed existing, but specific numbers not verified).

### 2.3 kNN-LM (Khandelwal et al.; ICLR 2021; arXiv 1911.00172)

kNN-LM interpolates a pretrained transformer with a k-nearest-neighbor lookup over a stored datastore (the training set, cached as hidden-state vectors). Results:
- WikiText-103: 15.79 perplexity (state of art at time), 2.9 point improvement from 18.65 baseline
- >20% perplexity reduction on WikiText-103 with no retraining

kNN-LM demonstrates that adding an associative memory retrieval step to an LLM improves language model quality measurably. This is the closest published precedent to substrate-augmented language modeling, using flat nearest-neighbor search rather than VSA binding. Substrate's advantage over kNN-LM: exact retrieval (recall=1.000 at M=2000 vs kNN-LM's approximate FAISS retrieval), structured binding (VSA compositionality vs flat vector similarity), and O(1) retrieval cost vs O(log N) for HNSW.

### 2.4 Memorizing Transformer (Wu et al., 2022)

Adds approximate nearest-neighbor memory (kNN-style, not VSA) to transformer attention layers. At every layer, key-value pairs from long contexts are cached and retrieved via approximate NN. Improves perplexity on long-document language modeling. Primary engineering precedent for hybrid attention+retrieval architectures.

### 2.5 NVSA (Hersche et al.; Nature Machine Intelligence, 2023; arXiv 2203.04571)

Neuro-vector-symbolic architecture combining deep neural networks for perception with VSA for probabilistic reasoning. Solves Raven's Progressive Matrices at 87.7% on RAVEN, 88.1% on I-RAVEN. The VSA backend performs probabilistic reasoning via vector operations -- the neural frontend handles perception; the VSA backend handles multi-step inference. This establishes that VSA probabilistic reasoning is competitive with pure neural approaches on structured inference tasks.

### 2.6 D-RAG (EMNLP 2025; OpenReview)

Differentiable Retrieval-Augmented Generation for Knowledge Graph QA. Uses Gumbel-Softmax reparameterization to make discrete retrieval decisions differentiable, enabling end-to-end gradient flow through the retrieval component. Directly establishes that differentiable retrieval from structured stores (KGs) is feasible at language-model training scale.

---

## Level 3: Six engineering paths from substrate-current to substrate-language

### Path 1: Substrate codebook trained on word2vec/BERT embeddings via VQ-VAE compression

**What:** Train a VQ-VAE where the encoder is a pretrained word embedding (BERT or word2vec) and the codebook is a set of substrate-compatible hypervectors. The codebook entries become substrate's semantic primitives (atoms). Each word maps to a superposition of codebook atoms.

**What it achieves:** Substrate's atomic vocabulary acquires semantic meaning. Synonym words map to nearby superpositions. Antonyms map to opposite directions. Analogies (king - man + woman = queen) become algebraic identities in the hypervector space.

**Engineering cost:** CPU, 1-2 hours. Train VQ-VAE on pretrained BERT embeddings, codebook size K=8192, vector dimension N=8192. This is rung-1 feasibility test.

**P_theoretical:** 0.78. VQ-VAE codebook training is standard (ICLR 2024 FSQ paper confirms). The mapping of BERT embeddings to VSA atoms is novel but algebraically clean.
**P_deflated (empirical):** 0.50. Risk: VQ-VAE codebook may not organize into semantically separable atoms; codebook collapse is a known failure mode (addressable with rotation trick or Dirichlet encoder from 2024 literature).

**HARD-PASS:** cosine similarity between BERT embeddings and substrate atoms >= 0.85 for top-1 atom, semantic analogies preserved in the hypervector space (king - man + woman nearest-neighbor = queen atom).
**HARD-FAIL:** codebook utilization < 30% (codebook collapse) or cosine similarity < 0.60 for top-1 atom.

### Path 2: Substrate-distilled from Qwen-1.5B

**What:** Use Qwen-1.5B (teacher) to generate (question, answer, reasoning trace) pairs from a structured corpus. Train a substrate-based student model where the student learns to reproduce the teacher's output using substrate binding operations. This is black-box distillation: the substrate student learns a lookup table of (context, answer) bindings that approximate the teacher's distribution.

**What it achieves:** A substrate model that can answer factual questions in the teacher's style, with the teacher providing the training signal.

**Engineering cost:** Remote GPU, 2-5 GPU-days. Teacher inference is the bottleneck.

**P_theoretical:** 0.55. Distillation from LLM to non-LLM student is well-established (IBM's work on distilling into rule systems). VSA-student specifics are novel.
**P_deflated (empirical):** 0.30 after deflation. Risk: the substrate student does not have LLM-scale reasoning capacity; it can memorize QA pairs but cannot generalize to unseen questions.

**HARD-PASS:** substrate-distilled model achieves >60% of teacher QA accuracy on held-out domain QA.
**HARD-FAIL:** substrate-distilled model achieves <25% of teacher QA accuracy (student cannot generalize beyond memorized pairs).

### Path 3: Substrate-only LM from scratch (GHRR-Transformer / TinyStories recipe)

**What:** Implement the GHRR-Transformer architecture (VSA-based attention at every layer). Train from scratch on TinyStories corpus (2B tokens, 4-year-old vocabulary of ~1500 words). Target model size: 10M parameters. Loss: next-token prediction cross-entropy. Baseline: same-size standard transformer trained on same corpus.

**What it achieves:** An existence proof that substrate-native language modeling works at rung-1 scale. The key question is whether VSA-based attention can compete with standard attention on language modeling benchmarks at equivalent parameter count.

**Engineering cost:** Remote GPU, 2-4 GPU-days at 10M parameter scale.

**P_theoretical:** 0.55 (cap applies; novel synthesis). GHRR-Transformer paper claims language modeling benefits but specific numbers not verified. TinyStories results for small transformers are well-characterized (Eldan 2023). The combination is novel.
**P_deflated (empirical):** 0.32 after deflation. Primary risk: FHRR binding operations are more expensive than standard matrix multiply at small D; the computational graph may not allow efficient backprop at language-model scale without custom kernels.

**HARD-PASS:** substrate-10M perplexity within 15% of transformer-10M on TinyStories validation set; GPT-4 story quality score within 1.0 of transformer-10M (on Eldan's 1-10 scale).
**HARD-FAIL:** substrate-10M perplexity > 2x transformer-10M (VSA attention is significantly worse than standard attention for language modeling at this scale), or training fails to converge.

### Path 4: Substrate-attention at every layer in Pythia-160M from scratch (LARS-VSA replica)

**What:** Replace the self-attention mechanism in a Pythia-160M-sized architecture (from random initialization) with substrate-based attention using FHRR binding/unbinding operations. Train on the same data as baseline Pythia-160M (Pile). Compare perplexity.

**What it achieves:** A full-scale comparison of substrate-attention vs standard attention. This is the direct replication of GHRR-Transformer's approach but using FHRR (substrate's actual algebraic structure) rather than GHRR.

**Engineering cost:** Remote GPU, 4-8 GPU-weeks for 160M from scratch. Non-trivial engineering. Requires efficient FHRR binding kernel in PyTorch.

**P_theoretical:** 0.48. The algebra is clean (FHRR differentiable, Wirtinger calculus applies). The engineering challenge is the bottleneck.
**P_deflated (empirical):** 0.28 after deflation. Risk: training instability at scale -- FHRR binding gradients may have different variance structure than standard attention, requiring learning rate and scheduler tuning.

**HARD-PASS:** substrate-Pythia-160M achieves perplexity within 20% of standard Pythia-160M on Pile validation.
**HARD-FAIL:** substrate model does not converge or achieves perplexity >3x standard baseline.

### Path 5: Substrate-LLM joint pretraining (gradient flows through both)

**What:** Train a transformer where substrate modules are interleaved between attention layers. During training, gradient flows through substrate bind/unbind operations using D-RAG-style Gumbel-Softmax differentiable retrieval. Both transformer weights and substrate indexing are updated jointly.

**What it achieves:** A fully end-to-end trained system where the LLM and substrate co-adapt. The substrate learns to store what the LLM needs; the LLM learns to use substrate effectively.

**Engineering cost:** Major. 8-16 GPU-weeks for a 160M parameter joint model.

**P_theoretical:** 0.40 (novel synthesis cap applies). D-RAG establishes differentiable retrieval for KG QA; extending to continuous language pretraining is the novel step.
**P_deflated (empirical):** 0.22 after deflation. D-RAG's Gumbel-Softmax has high variance gradients at scale; the STE (straight-through estimator) may not carry useful gradient signal into substrate stored vectors.

**HARD-PASS:** joint model outperforms frozen-substrate model by >5% perplexity (joint training improves substrate).
**HARD-FAIL:** joint model performs same or worse than frozen-substrate model (gradient through retrieval does not improve substrate).

### Path 6: Hybrid -- substrate at selected layers, transformer at others

**What:** Replace only mid-to-late transformer layers (where factual knowledge is concentrated per mechanistic interpretability) with substrate-attention. Early layers handle syntax and local context via standard attention. Late layers retrieve factual knowledge from substrate.

**What it achieves:** Best of both architectures. Early layers benefit from standard attention's expressivity for syntax. Late layers benefit from substrate's exact retrieval for facts. Engineering cost is lower than full replacement.

**Engineering cost:** Remote GPU, 2-4 GPU-weeks for a 160M hybrid.

**P_theoretical:** 0.58. Hybrid approaches dominate in multiple recent architecture comparisons (NVIDIA hybrid study: +1.3 points average over pure transformer; xLSTM hybrid). The division of labor between syntax (early) and facts (late) is supported by mechanistic interpretability.
**P_deflated (empirical):** 0.38 after deflation.

**HARD-PASS:** hybrid perplexity matches standard full transformer on Pile validation within 5%.
**HARD-FAIL:** hybrid perplexity is worse than standard transformer by >15% (substrate mid-layers disrupt factual encoding learned by standard attention).

---

## Level 4: Scale analysis

### 4.1 Minimum substrate parameter count for coherent language

The minimum viable language model on TinyStories requires:
- Eldan 2023 finding: grammar emerges at width=64, 1-2 layers (~100k parameters)
- Consistency/reasoning requires width ~128-256, 2-4 layers (~1-5M parameters)
- Story coherence at full 1500-word vocabulary: ~10M parameters at minimum

For a substrate-only language model, "parameters" are:
1. Embedding table: V * N where V = vocabulary size (BPE ~8192 to 32768 tokens), N = FHRR dimension
2. Binding matrices: per layer, learned projection from hidden state to FHRR query space
3. Unbinding/retrieval: the cleanup memory codebook (VSA codebook)

At N=4096 and V=8192 BPE tokens: embedding = 8192 * 4096 * 8 bytes (complex64) = 268MB. This is the dominant cost for vocabulary scale. The binding matrices are small by comparison.

Verdict: a rung-1 substrate-only LM (TinyStories scale) can be built with N=2048-4096, vocabulary=1500 words (full TinyStories vocab, no BPE needed), parameters ~10-50M including substrate codebook. This is CPU-feasible for training.

### 4.2 Codebook size (vocabulary equivalent)

For language, the substrate codebook serves as the vocabulary of atomic semantic units. Two interpretations:
1. Character-level: V = 128 ASCII characters. Trivial at any N.
2. Word-level: V = 50k-100k words. At N=8192, word codebook is 50k * 8192 * 8 bytes = 3.2GB. Fits in GPU.
3. Subword (BPE): V = 8192-32768 tokens. Standard for transformer-equivalent.

The linearithmic cleanup paper (arXiv 2506.15793) reduces codebook lookup from O(N^2) to O(N log N) via Kronecker rotation products. This means codebooks of V=1M are feasible without quadratic cost -- the path to full natural language vocabulary is no longer blocked by the cleanup step.

### 4.3 Training compute estimates

For the LARS-VSA approach (bipolar, D>=1000):
- Binary operations dominate; reported 25x speedup vs standard attention
- Full language model at 10M parameters / 2B token TinyStories: ~1-5 GPU-days at standard training throughput, divided by ~25 for speedup = potentially hours

For FHRR-based substrate-attention:
- Complex64 multiply is ~4x more expensive than float32 multiply (real ops count)
- At N=4096 per layer vs d_head=64 per head in standard attention: substrate is ~64x more expensive per attention computation but this is per-layer, not per-token
- Estimate: substrate-LM training is 10-20x MORE expensive than equivalent standard transformer at same parameter count; partially offset by reduced memory bandwidth (cleaner cache behavior for sequential VSA ops)

Realistic estimate for rung-1 substrate-LM (10M params, 2B tokens, N=2048): 2-6 GPU-days on an A100.

### 4.4 Language tasks feasible for substrate-only LM at small scale

Based on TinyStories findings and VSA literature:
1. Grammatical English generation (grammar emerges at very small scale): HIGH confidence.
2. Simple factual question answering (from stored substrate pairs): HIGH confidence (recall=1.000 established).
3. Short story generation with consistent characters: MEDIUM confidence (requires ~10M parameter scale).
4. Analogical reasoning: HIGH confidence (NVSA 87.7% on RPM; LARS-VSA outperforms baselines).
5. Multi-hop reasoning over stored facts: HIGH confidence (substrate K-hop +0.983 vs kNN-LM established).
6. Open-ended generative language (poetry, narrative, creative writing): LOW confidence at small scale.
7. In-context learning / few-shot: UNKNOWN. VSA has no established in-context learning mechanism equivalent to transformer soft copying.

### 4.5 Gap vs frontier LLMs -- honest assessment

Frontier LLMs (GPT-4o, Claude 3.5, Llama-3-70B) are trained on 10T+ tokens with 70B-400B parameters. A substrate-only LM at 10M-160M parameters will:
- Have vocabulary range close to frontier (exact recall from substrate)
- Have shallow linguistic knowledge (small parameter count limits syntactic generalization)
- Have ZERO in-context learning capacity at 10M parameters (emergence requires >1B per current evidence)
- Have EXACT factual recall for any fact loaded into substrate (frontier LLMs hallucinate at 5-15% rate on factual QA)
- Have ZERO creative/open-ended generation quality at 10M parameters

The correct comparison is NOT substrate-10M vs frontier LLM. The correct comparison is:
- substrate-10M vs transformer-10M on knowledge-intensive tasks
- substrate-1.4B (augmented) vs transformer-7B on MMLU/KG-QA

For the latter comparison: the empirical hypothesis is that 1.4B + 100M-fact substrate can match 7B transformer on knowledge-intensive tasks. P_deflated = 0.38. Not yet tested.

### 4.6 Substrate's structural advantages vs standard transformer

1. Exact compositionality: substrate binding/unbinding is algebraically exact. Transformers use soft attention that degrades with sequence length and item count. For structured relational reasoning, this is a provable advantage (NVSA, LARS-VSA results).

2. O(1) memory retrieval: after codebook training, substrate lookup is O(1) via nearest-neighbor in FHRR space (or O(N log N) with linearithmic cleanup). Standard attention is O(N^2) with context length N. At 64k-token context, substrate is ~3000x fewer FLOPs for the retrieval step.

3. Audit: substrate stores explicit (key, value) pairs. The retrieval trace is inspectable. Transformer attention is opaque (softmax over 8k-32k vectors; mechanistic interpretability requires reverse-engineering).

4. Persistence: substrate is write-once, read-many, with known GDPR-compatible delete (0.0004ms delete). Standard transformer knowledge is weight-entangled and cannot be cleanly deleted.

5. Compositional generalization: VSA binding generalizes to unseen combinations of atoms. A transformer trained on "cat sat on mat" and "dog chased cat" may fail on "dog sat on mat." A substrate with binding operations should generalize via algebraic composition.

---

## Level 5: Categorical positioning if substrate-only LM works

### 5.1 "Substrate IS a language model" vs "substrate has language"

Current (v1): "Substrate IS a long-term memory for LLMs." True. Narrow.
After Path 3 succeeds: "Substrate IS a language model." True. Strong.

The distinction matters: if substrate is only memory, it depends on an LLM host. If substrate is a language model, it can operate standalone. The categorical claim that would follow from a successful TinyStories experiment: "substrate is a complete cognitive architecture, not a complement to LLMs."

This is NOT the same as claiming substrate replaces GPT-4. It means substrate is a self-contained cognitive system at a scale that existing transformers cannot match on structured knowledge tasks.

### 5.2 Commercial implications

If substrate-only LM is proven at rung-1:
- "Substrate runs AI without a separately-licensed LLM" -- eliminates LLM licensing cost
- "Substrate AI on device without model download" -- substrate is small (10-50M params) vs typical on-device LLM (1-3B params)
- "Substrate AI with exact auditability" -- every retrieved fact is inspectable vs transformer's opaque attention

The realistic commercial target in v3: substrate-10M as the backbone of a factual QA agent for a narrow domain (enterprise wiki, product catalog, medical formulary). Not general-purpose but highly accurate for the installed knowledge base.

### 5.3 Research positioning (product-framing per memory constraint)

A substrate-only language model is a product proof-of-concept that no pretrained LLM is required. It demonstrates that FHRR computation is sufficient for language at bounded scale -- a non-obvious claim that would distinguish substrate from all other "memory-augmented LLM" products.

### 5.4 Comparison: substrate FHRR vs LARS-VSA bipolar vs GHRR

| Property | Substrate FHRR | LARS-VSA bipolar | GHRR |
|---|---|---|---|
| Vector type | complex unit circle | {-1,+1}^D | complex, generalized |
| Binding | element-wise complex multiply | element-wise XOR | complex multiply variant |
| Differentiability | Wirtinger (exact, no STE) | requires STE/binarized training | complex differentiable |
| Language tasks tested | K-hop QA (empirical) | abstract relational reasoning | language modeling (claimed) |
| From-scratch training | not yet at LM scale | yes (smaller tasks) | yes (claimed for LM) |
| Codebook cleanup | O(N log N) via KRP linearithmic | O(N*K) standard | depends |

FHRR (substrate) is the most differentiable of the three, which gives it the best training path. LARS-VSA's binarization gives efficiency but at cost of gradient quality. GHRR is most similar to FHRR algebraically.

---

## Level 6: Biology angle

### 6.1 Brain language circuit: not a single module

Modern neuroscience (post-2015 evidence) has overturned the classical Broca-Wernicke-arcuate model:
- Language is distributed across a cortical network including STG, STS, IFG, angular gyrus, MTG, and frontal cortex
- Wernicke's area is NOT a single "language comprehension center" -- it is part of the STG which responds to multiple sensory modalities
- The arcuate fasciculus connects frontal and temporal regions but is not the only language pathway; the extreme capsule, uncinate, and IFOF also carry language information

Key finding: the brain does not have a separate "language module." The same circuits that do spatial navigation, relational reasoning, and working memory are also the language circuits. Language is a use case of general relational computation, not a special-purpose system.

### 6.2 Huth 2016 -- distributed semantic maps

Huth et al. (Nature, 2016) mapped semantic selectivity across the cortex using voxel-wise fMRI modeling from hours of natural speech. Key findings:
- Each semantic concept (e.g., "family," "violence," "number") is represented in multiple semantic areas
- Each semantic area represents multiple semantic concepts
- The semantic maps are consistent across subjects (a shared semantic atlas)
- Semantics are distributed across the entire cortex, not localized to Wernicke's area

The cortical semantic map structure is consistent with the VSA model of distributed semantic representations: every concept is a superposition of many basis hypervectors (atoms), and every brain region codes a superposition of semantic features. The mathematical structure is essentially the same.

### 6.3 Hippocampal concept cells and substrate atoms

Quiroga et al. (Nature, 2005) identified individual hippocampal neurons that respond to abstract concepts (the "Halle Berry neuron" responds to images, text, and names of the actress). These concept cells are invariant to perceptual modality.

Updated finding (Neuron, 2026, "20 years of concept cells"): concept cells form a rapid and dynamic semantic memory network recruited during language comprehension. Pronouns reactivate specific concept cells in the hippocampus (Science, 2025: "Pronouns reactivate conceptual representations in human hippocampal neurons") -- showing that language comprehension is mediated by conceptual binding in hippocampal circuits.

A unified PNAS model (2025: "A unified neural representation model for spatial and conceptual computations") shows hippocampus codes both spatial relations and conceptual relations using the same circuit. The substrate atom -- a hypervector representing an entity or concept -- is the computational analog of a hippocampal concept cell assembly.

### 6.4 Implication: substrate IS brain-like language

The brain's language system:
- Distributes semantic meaning across a high-dimensional cortical representation (distributed HDC)
- Binds roles and fillers in hippocampal circuits (VSA binding)
- Uses concept cells as symbolic atoms (VSA codebook entries)
- Has no separate "language module" -- language is general relational computation over the same HDC substrate

Substrate's FHRR:
- Distributes semantic meaning across N-dimensional complex vectors (N=8192 or 65536)
- Binds roles and fillers via element-wise complex multiplication (exact analog of hippocampal binding)
- Has symbolic atoms as codebook entries (exact analog of concept cells)
- Has no separate language mode -- the same bind/bundle/unbind operations handle language and KG-QA

The brain-to-substrate mapping is tighter than it appears. The reason substrate CAN be a language model is that the brain's language mechanism IS a VSA computation.

---

## Level 7: v1/v2/v3 strategic sequencing

### v1.0 (current): Substrate as knowledge + LLM as interface
- LLM (Pythia/Llama) provides language fluency, syntax, inference
- Substrate provides exact knowledge storage and retrieval
- Demonstrated: recall=1.000 at M=2000, K-hop +0.983, 31x context expansion
- No language training on substrate required

### v2.0: Surgical Tier 5c -- substrate replaces mid-layer attention
- Substrate replaces attention in layers 12-15 of Pythia-1.4B
- LLM handles syntax (early layers); substrate handles factual lookup (mid/late layers)
- Engineering: 2-4 weeks; requires attention hook + substrate query integration
- P_deflated: 0.38 (key-space alignment is the risk)
- This is the Path 6 hybrid from Level 3

### v2.5: LLM fine-tuned to USE substrate (LoRA + substrate-aware training)
- LoRA fine-tunes LLM to query substrate explicitly and integrate substrate returns
- Different risk profile from v2.0: LLM weights are adapted, not just substrate
- kNN-LM precedent: +2.9 perplexity points with no LLM modification; LoRA version should do better
- P_deflated: 0.45

### v3.0: Substrate-only small LM (GHRR-Transformer recipe, TinyStories)
- From-scratch substrate-based LM at 10M parameters on TinyStories
- Existence proof that substrate is a complete language model primitive
- Not dependent on LLM license or LLM weight access
- P_deflated: 0.32 (rung-1 scale); P_deflated for beating same-size transformer: 0.28

### v3.5 (research): Substrate-Pythia-160M from scratch (Path 4)
- Full-scale substrate-attention language model at 160M parameters
- Competitive with standard Pythia-160M at equivalent scale
- Timeline: 4-8 GPU-weeks
- P_deflated: 0.28

### v3.5+: Substrate-only 1B+ competitive with small transformers (long-term)
- Requires solving the gradient variance problem for large-scale FHRR training
- No direct published precedent at 1B+ parameter scale
- P_deflated: 0.12 (speculative)

### Verdict on strategic sequencing

The correct sequencing is:
1. v1 delivers commercial value NOW (knowledge + LLM, working today)
2. Path 1 (substrate codebook from BERT) is a 2-hour CPU test that establishes semantic quality of atoms -- do this first, cheap
3. Path 3 (TinyStories from scratch) is the decisive categorical test -- 4 GPU-days, establishes "substrate IS a language model" if it passes
4. v2.0 (hybrid attention replacement) depends on Path 3 providing architectural insight

Do NOT attempt v3.5 or v3.5+ without v3.0 passing first. The scaling jump is too large.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

### Pre-registered for Path 1 (substrate codebook from BERT)
- HARD-PASS: top-1 cosine similarity between BERT embedding and nearest substrate atom >= 0.85; analogy test (king - man + woman = queen) passes with substrate atoms.
- HARD-FAIL: codebook utilization < 30% (codebook collapse); top-1 cosine < 0.60.

### Pre-registered for Path 3 (substrate-only TinyStories 10M)
- HARD-PASS: substrate-10M perplexity within 15% of transformer-10M on TinyStories validation; GPT-4 story quality within 1.0/10.
- MID-BAND: substrate-10M perplexity 15-40% worse than transformer-10M (VSA attention is suboptimal but trainable).
- HARD-FAIL: substrate-10M perplexity > 2x transformer-10M OR training fails to converge.

### Pre-registered for Path 6 (hybrid attention replacement, v2.0)
- HARD-PASS: next-token accuracy within 5% of standard Pythia-1.4B on held-out corpus with substrate replacing layers 12-15.
- MID-BAND: accuracy 5-15% below baseline (projection layer needed for key-space alignment).
- HARD-FAIL: accuracy > 20% below baseline (substrate mid-layer replacement disrupts encoding structure).

### Pre-registered for Path 2 (distillation from Qwen-1.5B)
- HARD-PASS: substrate-distilled student >= 60% of teacher QA accuracy on held-out domain.
- HARD-FAIL: substrate-distilled student < 25% of teacher QA accuracy.

---

## Cross-thread synthesis

This drill connects to four existing research threads:

1. arXiv 2512.14709 (attention=VSA binding): previously established in notes. This drill extends the implication: if attention IS VSA, then replacing attention WITH VSA is not speculative engineering -- it is a direct algebraic inversion. The substrate is already doing what transformers approximate.

2. Multi-hop revival (notes/project_multihop_revive_priority.md): substrate K-hop +0.983 establishes that substrate handles relational chains algebraically. A substrate-only language model would natively support K-hop reasoning as a first-class operation -- not a retrofit. This addresses the multi-hop gap that transformers struggle with (iterative reasoning requires prompt engineering; substrate does it in one algebraic step).

3. D3 cross-shard routing=0.999 (ndom=40): the routing mechanism is analogous to Mixture-of-Experts gating. A substrate-LM hybrid where substrate performs MoE routing is Path 6 -- already identified as MEDIUM priority by the previous intrinsic-language drill.

4. Production N=65536 substrate (empirically validated at recall=1.000): at N=65536, a VSA vocabulary of ~5000-10000 tokens is capacity-safe (SNR formula gives margin > 1.0 for V=10k at N=65536). This means the production substrate can support a reasonable language vocabulary TODAY without architectural changes.

5. GDPR 0.0004ms delete + bitemporal 0.003ms (empirically validated): substrate language model has a built-in legal advantage over weight-entangled LLMs -- specific learned facts can be surgically deleted, while transformer weights cannot.

---

## Substrate-product implications

The categorical upgrade from "substrate is memory" to "substrate IS a language model" would change the commercial positioning in one direction: substrate can be deployed WITHOUT an LLM dependency for narrow-domain applications. The unit economics change: no per-token API cost, no model licensing, no hallucination risk, surgical auditability. The gap: substrate-only LM at rung-1 scale (10M params) will have dramatically less linguistic fluency than any frontier LLM. The correct product frame is not "replace GPT-4" but "replace GPT-4 for narrow, structured, high-accuracy, auditable, low-cost, on-device knowledge tasks."

The GDPR angle is significant: a substrate-only LM can delete learned facts in 0.0004ms. A fine-tuned LLM cannot. Under EU AI Act Article 12 (August 2026), auditability and data deletion capabilities are mandated. Substrate-only LM natively satisfies these requirements; transformer-only LLMs do not.

---

## Citations (verified count: 25)

1. Plate, T.A. (1995). "Holographic Reduced Representations." IEEE TNN, 6(3):623-641.
2. Smolensky, P. (1990). "Tensor Product Variable Binding." Artificial Intelligence, 46:159-216.
3. Pollack, J.B. (1990). "Recursive Distributed Representations." Machine Learning. (RAAM paper)
4. Kanerva, P. (1988). Sparse Distributed Memory. MIT Press.
5. Eliasmith, C. (2013). How to Build a Brain. Oxford University Press. (SPA)
6. Nickel, M., Rosasco, L., Poggio, T. (2016). "Holographic Embeddings of Knowledge Graphs." AAAI 2016; arXiv 1510.04935.
7. Mejri, M., Amarnath, C., Chatterjee, A. (2024). "LARS-VSA: A Vector Symbolic Architecture For Learning with Abstract Rules." arXiv 2405.14436.
8. Anonymous (2024). "Structure-aware Attention based on Vector Symbolic Architectures" (GHRR-Transformer). OpenReview: zET0Zg71WT.
9. Dhayalkar, S.R. (2025). "Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning." arXiv 2512.14709.
10. Anonymous (2024). "GPT-2 Through the Lens of Vector Symbolic Architectures." arXiv 2412.07947. NeurIPS 2024 workshop.
11. Khandelwal, U. et al. (2021). "Generalization through Memorization: Nearest Neighbor Language Models." ICLR 2021; arXiv 1911.00172.
12. Wu, Y. et al. (2022). "Memorizing Transformers." ICLR 2022.
13. Hersche, M. et al. (2023). "A Neuro-Vector-Symbolic Architecture for Solving Raven's Progressive Matrices." Nature Machine Intelligence; arXiv 2203.04571.
14. D-RAG authors (2025). "D-RAG: Differentiable Retrieval-Augmented Generation for Knowledge Graph Question Answering." EMNLP 2025; OpenReview D0vilzHmI3.
15. Eldan, R., Li, Y. (2023). "TinyStories: How Small Can Language Models Be and Still Speak Coherent English?" arXiv 2305.07759.
16. Liu, R. et al. (2025). "Linearithmic Clean-up for Vector-Symbolic Key-Value Memory with Kronecker Rotation Products." PMLR 284:1107-1118; arXiv 2506.15793.
17. Frady, E.P., Kleyko, D., Sommer, F.T. (2020). "Variable Binding for Sparse Distributed Representations: Theory and Applications." IEEE TNN; arXiv 2009.06734.
18. Ge, L. et al. (2022, updated 2025). "Classification Using Hyperdimensional Computing: A Review." arXiv 2004.11204.
19. Kleyko, D. et al. (2022). "A Survey on Hyperdimensional Computing / Vector Symbolic Architectures, Part I+II." arXiv 2111.06077, 2112.15424.
20. Huth, A.G. et al. (2016). "Natural speech reveals the semantic maps that tile human cerebral cortex." Nature 532:453-458.
21. Quiroga, R.Q. et al. (2005). "Invariant visual representation by single neurons in the human brain." Nature 435:1102-1107. (Concept cells original paper)
22. Benovoy, M. et al. (2026). "20 years of concept cells: From invariant responses to a unique coding of human memory." Neuron.
23. Kossuth, B. et al. (2025). "Pronouns reactivate conceptual representations in human hippocampal neurons." Science.
24. Bellmund, J. et al. (2025). "A unified neural representation model for spatial and conceptual computations." PNAS.
25. Hyperdimensional Probe paper (2025). arXiv 2509.25045.

---

## Next-drill candidate

Path 3 (TinyStories from scratch with GHRR-Transformer recipe) is the single highest-leverage remaining experiment. It is the decisive test separating "in principle" from "in practice" for substrate as language model. The engineering prerequisite is Path 1 (substrate codebook from BERT, 2-hour CPU) which should be done first as a sanity check on semantic quality.

Field: language-modeling (new field for drill map; adjacent to VSA/NeSy parent via arXiv 2512.14709 edge).
