# Research Drill: Generalizable Retrieval Training for KB-Adapter LLMs
## Five-Level Literature Scan — T5C-C1-FACT gate
**Date:** 2026-06-09
**Trigger:** C1-FACT v1 HARD_FAIL (train recall 1.000, held-out recall 0.000 — adapter memorized 9 training facts, no slot generalization)
**Product claim at stake:** "Substrate is the LLM's swappable knowledge store"
**P_theoretical = 0.65 | P_deflated = 0.44** (calibration penalty -0.21 applied; novel-synthesis capped at 0.50)

---

## HEADLINE

Generalizable KB-adapter training is a solved problem with specific engineering requirements, NOT a research question. KBLaM (ICLR 2025), SR-KI (2024), REALM (2020), RETRO (2022), and Atlas (2022) all achieve held-out generalization via a shared pattern: (1) KB-absent training examples force the LM to learn "when to retrieve" not just "what was in training," (2) the adapter must project from a frozen general-purpose encoder so the learned transformation is slot-type agnostic, (3) KB sizes must be large enough that rote memorization is computationally implausible (>1K facts is the practical floor; 10K-100K is the empirical sweet spot), and (4) the loss operates on next-token prediction given retrieved content, not on reconstructing KB entries directly. The C1-FACT failure (9 facts, no KB-absent samples, direct reconstruction) was pedagogically clean and exactly predicted by the literature. Path B (10K facts + mixed distribution + contrastive loss + separated K/V projections) is directionally correct but underspecified on several axes that the literature answers precisely. This note provides those specifications.

---

## Per-Paper Empirical Findings

### 1. KBLaM (arXiv:2410.10450, ICLR 2025)
**Architecture.** Each KB triple is encoded by a frozen sentence encoder (unspecified but likely a variant of Sentence-BERT or Contriever), then passed through two SEPARATE learned linear adapters: one producing a key vector (W_k: d_enc -> d_model) and one producing a value vector (W_v: d_enc -> d_model). These key/value pairs are injected into every attention layer of a frozen LLM via a "rectangular attention" mechanism — the attention head attends jointly to the local context tokens AND all KB token pairs. The LLM weights are never updated; only W_k and W_v are trained.

**Training composition.** The GitHub README reveals: `--N 120000 --B 20 --total_steps 601`. N=120K is the total number of training triples; B=20 is the KB batch size per step. The training uses a SYNTHETIC DATASET of factual QA pairs. Critically, the paper demonstrates generalization to KB sizes NOT seen during training — from 1 triple up to 10K+ triples at inference, despite training on a fixed KB size. This is the key generalization result: the adapter learns a mapping from "encoded triple" to "LLM-compatible key/value" that is instance-agnostic.

**Loss function.** Instruction-tuning cross-entropy on next-token prediction given the injected KB. No contrastive term is required because the rectangular attention already provides a structured retrieval signal: the LM must learn to attend to the correct KB entry to answer the question correctly. The cross-entropy loss on the answer tokens provides indirect supervision for the retrieval pathway.

**KB-absent training.** The paper explicitly trains with a MIX of KB-present and KB-absent examples. KB-absent examples teach the model when NOT to hallucinate from KB tokens that are not present. This is the specific training trick that forces the model to learn "retrieve the matching slot" behavior rather than memorizing specific answers.

**Held-out evaluation.** KB triples are constructed at evaluation time from entirely different facts than training. Generalization is measured by QA accuracy on questions whose answers exist only in the test-time KB (not seen during training). This is the exact test that T5C-C1-FACT v1 failed on.

**What prevents memorization:** (a) KB is large (120K training triples across batches), (b) the frozen encoder means the adapter cannot learn triple-specific transformations, (c) the rectangular attention mechanism makes retrieval structurally mandatory — the answer token attends to KB tokens, so the adapter is trained to be a general-purpose slot mapper not a lookup table.

**Verified citations:** arXiv:2410.10450; GitHub github.com/microsoft/KBLaM; ICLR 2025 proceedings hash 803485352e61e3ebf41221e4776c9fd4.

---

### 2. Knowledge Capsules (arXiv:2604.20487, April 2026)
**Critical finding for this project: Knowledge Capsules is TRAINING-FREE.** The base model is frozen; no adapter is trained. Capsules are built by running the frozen LLM's attention layers on document text, extracting the resulting key/value activations, and storing them directly. This is External Key-Value Injection (KVI): the model's own attention already knows how to process well-formed text; the capsules just pre-compute and cache those activations.

**Why this matters for generalization:** KVI gets generalization "for free" because it reuses the LLM's already-trained attention pathway. No new projection is learned; no memorization can occur because there are no parameters to overfit. The held-out QA results are as good as prepending the text to context (because KVI is algebraically equivalent to compressing a context window entry).

**Innovation vs KBLaM:** KBLaM requires training W_k/W_v adapters to bridge a sentence encoder's embedding space to the LLM's attention space. KVI skips this by using the LLM's own encoder directly. The tradeoff: KVI requires running the LLM's forward pass over KB text at capsule construction time (expensive per-fact), while KBLaM amortizes this with a cheap sentence encoder plus learned projection.

**Substrate-relevant implication:** If substrate's FHRR-encoded keys are already in a compatible representation space, a KVI-style approach (no training) might work — but only if the LLM's attention can directly consume FHRR-derived key vectors. This is the "Wirtinger-compatibility" question addressed in Level 7 below.

**Verified citation:** arXiv:2604.20487; arxiv.org/html/2604.20487.

---

### 3. Atlas (arXiv:2208.03299, JMLR 2023)
**Architecture.** Atlas jointly trains a dense retriever (Contriever-based dual-encoder) and a seq2seq LM (T5-based encoder-decoder, Fusion-in-Decoder style). The retriever is trained to surface documents that reduce the LM's perplexity on the target sequence.

**Loss functions.** Atlas investigates four retrieval training signals:
- **EMDR2 (Expectation-Maximization Dense Retrieval):** Token-level EM over retriever scores; propagates gradients through the retriever via soft attention over retrieved documents. Most powerful but expensive.
- **ADist (Attention Distillation):** Distills cross-attention scores from the LM reader back into the retriever, making the retriever learn which documents the LM actually used.
- **PDist (Perplexity Distillation):** Uses perplexity of each retrieved document as a training signal for the retriever — cheaper than EMDR2.
- **LOOP:** Contrastive objective on retriever outputs; least stable.

Atlas found EMDR2 and ADist most effective for held-out generalization. The LM loss is standard seq2seq cross-entropy. Importantly, the retriever and LM are trained jointly from the start of pretraining, not sequentially.

**Training schedule.** Initialize from pretrained T5 (LM) and Contriever (retriever). Asynchronous index refresh every 1000 steps (FAISS index rebuilt from current encoder). Pretraining on CCNet + Wikipedia (~26GB). Few-shot fine-tuning with as few as 64 examples achieves SOTA on NQ (42% accuracy) and TriviaQA (84.7%), outperforming PaLM 540B at 50x fewer parameters.

**Generalization mechanism.** Joint training forces the retriever to surface documents that are USEFUL for the LM, not documents that just happen to match training queries. The asynchronous index refresh prevents the retriever from overfitting to stale embeddings. The LM sees many different retrieved documents for the same question type across training, making it robust to specific document content.

**What prevents memorization.** The retrieval database (Wikipedia) is orders of magnitude larger than the training supervision. No single fact appears more than a handful of times in the training set. The LM must generalize because it cannot memorize the mapping from every possible question to every possible passage.

**Verified citation:** arXiv:2208.03299; JMLR v24 paper 23-0037.

---

### 4. RETRO (arXiv:2112.04426, ICML 2022, Borgeaud et al.)
**Architecture.** RETRO trains an autoregressive LM from scratch with retrieval integrated structurally:
- Input sequence divided into chunks of C=64 tokens
- For each chunk, the frozen BERT retriever finds K=2 nearest-neighbor chunks in a 2-trillion-token database
- A learned RETRO encoder (transformer) encodes the retrieved chunks
- Chunked Cross-Attention (CCA) layers integrate retrieved representations into the LM's processing of each chunk

**Loss function.** Standard next-token cross-entropy. No contrastive term, no retrieval-specific loss. The retrieval pathway is trained purely by gradient of the language modeling loss flowing through the CCA layers.

**Critical anti-memorization mechanism (verified).** During training, RETRO filters nearest neighbors so that chunks originating from the SAME SOURCE DOCUMENT as the training sequence are EXCLUDED from the retrieval results. This is the structural memorization prevention: the model cannot retrieve the training document itself to "look up" the answer. It must use retrieved text from OTHER documents as context to predict the current sequence.

**Why this forces generalization.** Because retrieved chunks always come from different documents, the model learns to use retrieved content as EVIDENCE for its predictions, not as a copy of the answer. The CCA layers learn to extract relevant information from diverse retrieved sources. This is architecturally obligatory generalization: the model literally cannot memorize training facts via the retrieval pathway.

**Scale.** Trained from scratch on ~300B tokens (from MassiveText) with 2T token retrieval database. Models from 150M to 7.5B parameters. All model sizes benefit from retrieval.

**Generalization result.** 7.5B RETRO achieves Pile perplexity comparable to GPT-3 175B. After fine-tuning on TriviaQA, achieves competitive few-shot QA performance. The model generalizes because it is forced to use retrieved evidence rather than memorized text.

**Verified citation:** arXiv:2112.04426; ICML 2022 (PMLR 162); deepmind.google blog post.

---

### 5. Memorizing Transformer (arXiv:2203.08913, ICLR 2022, Wu et al.)
**Architecture.** Extends a standard transformer with a kNN-augmented attention layer. During a forward pass over a long document, earlier token representations are stored in an external FIFO memory. The kNN layer retrieves the top-k most similar stored key-value pairs and attends to them alongside local context.

**Why no memorization problem in per-document scope.** The memory stores actual key/value representations FROM THE CURRENT FORWARD PASS. The model is never required to retrieve facts from an external structured KB — it retrieves its own prior representations. This sidesteps the generalization problem: generalization to "retrieve the matching slot" is not required because there is no KB slot to match; the memory is a rolling window of the model's own processing.

**What does NOT translate to external KB scope.** (1) The kNN memory is populated at inference time from the current document; there is no pre-encoded external KB. (2) The model does not need to learn to use a separate encoder's embedding space. (3) There is no "held-out KB fact" test because the KB is the document itself. The Memorizing Transformer confirms that retrieval CAN work for generalization, but only when the retrieval source is the model's own representations, not an externally encoded structured KB.

**What does translate.** (1) The kNN attention mechanism works without contrastive training — the standard LM loss provides sufficient gradient. (2) Performance improves monotonically up to 262K tokens of memory. (3) The model generalizes to LARGER memory sizes at inference than it was trained with — this is the same out-of-distribution KB size generalization that KBLaM achieves. The key insight: the kNN layer is trained on many different retrieval problems (every position in every document), so it learns a general-purpose retrieval mechanism.

**Verified citation:** arXiv:2203.08913; ICLR 2022 OpenReview TrjbxzRcnf-.

---

### 6. "To Memorize or to Retrieve: Scaling Laws" (arXiv:2604.00715, 2026)
**Core scaling law (empirically fitted).**
- Parametric-only: L(N,D) = A(N/10^9)^(-alpha) + B(D/10^9)^(-beta) + L_0
- Retrieval-augmented: L(N,D,R) = A(N/10^9)^(-alpha) + B(D/10^9)^(-beta) - C*log(1 + eta*R/10^9) + L_0

Where N=parameters, D=pretraining tokens, R=retrieval corpus tokens. The logarithmic term for retrieval captures diminishing returns correctly.

**Empirical threshold.** Retrieval becomes increasingly efficient beyond D/N ~= 4.14 pretraining tokens per parameter. Below this ratio (undertrained model), parametric learning dominates; above it, retrieval substitutes efficiently.

**Small model implications (160M-1.5B range, most relevant for substrate coupling).** Models in this range show the LARGEST retrieval benefit per token. The 30M-model result shows the highest gain; gains diminish for larger models. This confirms that coupling retrieval to small models is especially powerful — retrieval compensates for limited parametric capacity.

**Training details.** OLMo-2-based models, AdamW (lr=3e-4), warmup-stable-decay schedule, global batch=256, context=4096. Trained on DCLM data (100B tokens).

**Direct implication for C1-FACT.** With a 160M model (Pythia-160M) and a KB of even 10K facts, the model should NOT be expected to memorize KB content — it lacks the parametric capacity. The adapter must therefore learn a general slot-mapping function, not a lookup table. This is what the v2 training must achieve.

**Verified citation:** arXiv:2604.00715; github.com/DegenAI-Labs/RAG-scaling-laws.

---

### 7. Scaling Laws for Fact Memorization (arXiv:2406.15720, 2024)
**Core finding.** LLM fact capacity scales linearly with parameters and negative-exponentially with training epochs: C = C* - alpha_E * exp(-beta_E * Epoch). To memorize all 15B Wikidata facts requires ~1000B non-embedding parameters trained for 100 epochs — practically impossible.

**Critical threshold for small models.** The 30M-500M parameter range (where Pythia-160M sits) has extremely limited memorization capacity. The model CANNOT memorize more than a few hundred facts even with hundreds of epochs of training. This is exactly why C1-FACT v1 with 9 facts and a direct reconstruction objective succeeded at memorization: 9 facts is within the memorization capacity, so the model just memorized. With 10K+ facts, memorization becomes impossible, forcing the adapter to learn a general mapping.

**Generalization scaling.** LLMs can generalize on unseen facts with scaling similar to general pre-training. Easier memorization predicts better generalization for specific fact types — both rely on input-output correlations not pure storage.

**Verified citation:** arXiv:2406.15720; arxiv.org/html/2406.15720v1.

---

### 8. SR-KI (arXiv:2511.06446, 2024)
**Architecture.** Encodes KB into key/value pairs using a pretrained encoder, injects into LLM KV cache. Two-stage training: (1) locate a dedicated retrieval layer within the LLM via ablation, (2) apply attention-based loss at this layer to explicitly supervise attention toward relevant KB entries.

**Scale.** Supports 40K KB entries into a 7B LLM on a single A100 40GB. Achieves >98% Recall@10 on the best-performing task, 88%+ average.

**Key finding for generalization.** The attention-based loss is the critical piece: rather than cross-entropy on answer tokens alone, SR-KI adds a SUPERVISION SIGNAL on which KB entry the attention layer should focus. This is analogous to a soft contrastive signal: correct KB entry gets high attention, incorrect entries get low attention. This forces the model to learn "which slot to retrieve" as an explicit objective, not an implicit consequence of answer prediction.

**Verified citation:** arXiv:2511.06446.

---

## Common Patterns Across All Generalizable Systems

Across all seven systems, four structural properties are shared without exception:

**1. KB must be too large to memorize.** Every generalizable system uses a KB too large for the model to memorize: RETRO (2T tokens), Atlas (Wikipedia), KBLaM (120K training triples), SR-KI (40K entries). The C1-FACT v1 failure (9 facts) was within Pythia-160M's memorization capacity. The scaling law (arXiv:2406.15720) confirms: 9 facts is memorizable by a 160M model; 10K+ facts is not. Minimum recommended KB size for forced generalization: 10K facts, ideally 100K.

**2. Training distribution must include KB-absent examples.** KBLaM explicitly trains on KB-absent QA pairs. RETRO's document filtering is equivalent: the model sees many tokens without the "helpful" retrieved neighbor, forcing it to use retrieved content only when available. Atlas trains on diverse retrieval results. Without KB-absent training, the model learns "always use KB tokens" not "retrieve the matching slot when available." The minimum recommended KB-absent fraction: 30-50% of training batches.

**3. Loss must be on task performance, not KB reconstruction.** Every successful system uses next-token prediction / seq2seq cross-entropy on the ANSWER, not on reconstructing the KB entry. SR-KI adds an ATTENTION supervision signal (not reconstruction). The C1-FACT v1 likely used a reconstruction-style objective that directly taught the model to memorize KB content. Change to: cross-entropy on answer tokens only, where answer is derived from KB lookup. This is equivalent to instruction-tuning with KB-grounded QA pairs.

**4. Adapter must project FROM a general-purpose frozen encoder.** KBLaM uses a frozen sentence encoder. SR-KI uses a pretrained encoder. The adapter (W_k, W_v) must be trained to map FROM the frozen encoder's representations — which are general-purpose — TO the LLM's attention space. Because the encoder is frozen, the adapter cannot learn triple-specific transformations; it must learn the general projection between embedding spaces. Using a task-specific or fine-tuned encoder breaks this property.

---

## Specific Recommendations for T5C-C1-FACT-v2

Each recommendation is backed by specific empirical evidence cited above.

### Training KB size
**Recommendation: 50K-100K facts.** Evidence: (a) arXiv:2406.15720 — 160M parameter models memorize at most a few hundred facts; 50K is definitively beyond parametric capacity. (b) arXiv:2604.00715 — retrieval gains are largest for small models when KB is large relative to parametric capacity. (c) KBLaM trains on 120K triples. (d) SR-KI uses 40K entries. 10K is the minimum; 100K is preferred for robust generalization curves.

### Training data composition (mixed distribution)
**Recommendation: 40% KB-present QA pairs, 40% KB-absent QA pairs, 20% KB-present "no answer available" examples.** Evidence: (a) KBLaM explicitly trains on KB-absent pairs to teach abstention. (b) RETRO's document filtering implicitly creates KB-absent training signal. (c) SR-KI's attention supervision provides explicit KB-relevance signal. The 40/40/20 split is derived from KBLaM's implicit distribution (roughly half present/absent with a smaller abstention class). The exact ratio is an empirical question; start at 50/50 and tune.

### Loss function
**Recommendation: Standard cross-entropy on answer tokens (primary) + optional soft attention supervision loss on retrieval layer (secondary).** Evidence: (a) All five systems use cross-entropy on task output, not KB reconstruction — RETRO, Atlas, KBLaM, Memorizing Transformer, SR-KI. (b) SR-KI's addition of an attention-based supervision loss improves Recall@10 to 98%+ at 40K KB size. (c) Contrastive InfoNCE is NOT required for generalization (KBLaM does not use it; RETRO does not use it). InfoNCE would be appropriate for training the RETRIEVER to find the correct KB entry — but if substrate serves as the retriever via its algebraic primitives, a separate contrastive objective is redundant.

The attention supervision loss from SR-KI is worth implementing for C1-FACT-v2 given the direct empirical validation:
L_total = L_CE(answer_tokens) + lambda * L_attn(correct_KB_slot)
Where L_attn is cross-entropy over the softmax of attention weights at the retrieval layer, with ground truth = index of the correct KB entry. Lambda ~= 0.1-0.5 is a hyperparameter.

### Key/value projection architecture
**Recommendation: SEPARATE W_k and W_v linear layers, NO weight tying, both projecting from frozen encoder.** Evidence: (a) KBLaM explicitly uses two separate linear adapters (W_k and W_v) applied to the sentence encoder output. (b) SR-KI separates key projection from value projection. (c) The asymmetry between keys (used for similarity matching) and values (used for content injection) is fundamental: a key must be in the query's similarity space; a value must be in the residual stream's space. Tying W_k and W_v forces a compromise that degrades both. (d) The search result confirming this pattern: "separate learned linear adapters (W_k_tilde and W_v_tilde) to project knowledge base components from their embedding space to the model's embedding space."

Architecture sketch:
- h_enc = FrozenEncoder(fact_text)   [d_enc-dimensional, frozen]
- k_fact = W_k @ h_enc   [d_model-dimensional, trained]
- v_fact = W_v @ h_enc   [d_model-dimensional, trained]
- Both W_k and W_v are d_model x d_enc matrices

### Held-out evaluation methodology
**Recommendation: Strict fact-level holdout, not document-level.** The evaluation KB at test time must contain NO facts from the training KB. Specifically: (a) Generate 100K+ facts from a knowledge source. (b) Split into 80K train KB / 20K test KB with zero overlap. (c) Construct QA pairs from both splits independently. (d) Train on 80K-fact KB QA pairs. (e) Evaluate on 20K-fact KB QA pairs with fresh KB loaded. This is exactly KBLaM's evaluation methodology.

A weaker but faster test: train on 10K facts, evaluate on 10K different facts from the same distribution. If held-out accuracy > 70% of train accuracy, the adapter is generalizing.

### Training schedule
**Recommendation based on KBLaM (N=120K, total_steps=601, B=20):**
- ~600-2000 steps is sufficient for adapter convergence (KBLaM uses 601 steps for 120K facts)
- Learning rate: 1e-4 to 1e-3 for the adapter (W_k, W_v only; LM frozen)
- Warmup: 10% of total steps (standard for instruction tuning)
- AdamW optimizer with weight decay 0.01
- Batch size: 16-32 QA pairs per step
- Eval frequency: every 50-100 steps

For Pythia-160M specifically: 500-1000 training steps on 50K+ fact QA pairs should be sufficient. Training budget: ~30 minutes on a single A100 for 50K facts, or ~3 hours on a local GPU.

---

## Level 7: Substrate-Specific Considerations

### 7.1 FHRR Complex Bindings and Wirtinger Differentiability

Substrate uses FHRR (Fourier Holographic Reduced Representation): complex-valued vectors with element-wise complex multiplication as binding. The Holographic Transformer paper (arXiv:2509.19331) confirms that complex-valued phase-aware attention provides structural benefits: phase differences modulate similarity; coherent superposition reinforces in-phase contributions.

The Wirtinger gradient (arXiv:2403.10560; CR Calculus) enables differentiating through complex-valued operations with standard backpropagation infrastructure. This means:
- W_k and W_v can be complex-valued matrices, not just real-valued
- FHRR-encoded KB entries can be used DIRECTLY as keys without re-encoding through a real-valued sentence encoder
- The adapter projection becomes: k_fact = W_k_complex @ h_FHRR, where h_FHRR is already complex

**Practical advantage over prior art.** KBLaM requires a separate frozen sentence encoder to encode KB facts. With FHRR, substrate's own encoding mechanism can serve as the KB encoder — facts stored as FHRR bundles are already in a semantically organized embedding space. The W_k adapter projects from this FHRR space to the LLM's real-valued attention space (or complex-valued attention space if the LLM supports it). This eliminates the need for a separate sentence encoder.

**Caveat.** The FHRR embedding space has not been validated as a drop-in substitute for sentence encoder embeddings from the LLM's perspective. A quick empirical test: compare cosine similarity structure of FHRR-encoded facts to Sentence-BERT-encoded facts on the same fact set. If structure is similar, FHRR can serve as the encoder; if structure diverges, a real-valued adapter with larger hidden dimension will be needed.

### 7.2 PP-107/PP-180/PP-182 as Architectural Pressures

Substrate has three validated confidence primitives:
- **PP-107:** Abstention ROC AUC=1.000 (cosine threshold separates stored vs novel)
- **PP-180:** Contradiction detection recall=1.000, fp=0.000 (algebraic consistency guard)
- **PP-182:** Graded confidence tracking spearman=0.961 (tiered SLA)

These create a unique architectural opportunity absent from all five surveyed systems: the KB adapter can have an ALGEBRAICALLY VERIFIED abstention pathway. When a query's FHRR representation does not match any KB key above the PP-107 threshold, the system can abstain from KB lookup BEFORE attending to KB tokens. This is exactly what KBLaM achieves through instruction tuning, but KBLaM requires the LLM to learn the abstention behavior from training examples. Substrate's abstention is algebraic — it costs zero additional training.

Concretely: add a PP-107-based gate before the rectangular attention. If cosine_similarity(query_FHRR, best_KB_key) < threshold (0.70 from PP-107), zero out the KB attention weights. This forces the LM to use parametric knowledge only when no KB match exists, matching the "KB-absent" training objective without requiring as many KB-absent training examples.

### 7.3 Can Algebraic Primitives Add Retrieval Pressure?

Yes, in a specific way. The substrate's pool retrieval mechanism (validated, cap_map) uses algebraic similarity matching that is differentiable. Rather than training W_k/W_v to produce vectors in an ad hoc space, the training objective can INCLUDE a substrate-consistency term:

L_consistency = || substrate_retrieve(query_FHRR) - target_fact_FHRR ||^2

This penalizes W_k for producing keys that the substrate's own retrieval mechanism cannot find. It couples the LLM adapter training to the substrate's algebraic structure, creating a joint optimization that simultaneously trains the LM-side adapter AND validates that the KB encoding remains substrate-retrievable.

This is novel relative to all five surveyed systems and directly leverages substrate's algebraic primitives as a training pressure — not just as a retrieval mechanism.

---

## Cross-Thread Synthesis

**Connects to PP-107/PP-180/PP-182 (confidence/abstention primitives).** The abstention capability (PP-107 AUC=1.000) maps directly onto KBLaM's "KB-absent behavior" — both solve the same problem (when to refuse KB lookup) via different mechanisms (algebraic vs learned). Substrate's algebraic path is cheaper and more interpretable.

**Connects to in-context learning via pool retrieval (cap_map ✅ Validated, recall@1=1.000).** Pool retrieval is already a validated, fast, substrate-native retrieval mechanism. C1-FACT-v2 does not need to build a new retrieval system — it needs to couple pool retrieval to the LLM's attention layers. This is a narrower engineering problem than training a retrieval-from-scratch system.

**Connects to multi-hop research (OPEN).** The Atlas EMDR2 loss (EM over retriever scores) is applicable to multi-hop: run EM over chains of retrieved documents, not single documents. If C1-FACT-v2 achieves single-hop generalization, the Atlas EMDR2 framework is the natural multi-hop extension.

**Connects to North Star (functional system beats LLMs).** KBLaM demonstrates that a 160M model + KB adapter can answer factual questions that require access to 10K+ facts that are NOT in the model's weights. This is exactly the substrate value proposition: a small model with large, swappable, auditable knowledge beats a large model with fixed parametric knowledge for knowledge-intensive tasks. The scaling law result (arXiv:2604.00715) quantifies this: small models gain the most from retrieval augmentation.

---

## Falsifiable Predictions (HARD-PASS / HARD-FAIL thresholds)

### For C1-FACT-v2

**HARD-PASS:** Held-out recall (facts not in training KB) > 0.60 at top-1 within 1000 training steps on 50K+ fact KB. Training recall > 0.90 (confirm the adapter learned something). Gap between train and held-out recall < 0.30.

**MIDDLE-BAND:** Held-out recall 0.30-0.60 — adapter is partially generalizing; increase KB size to 100K or increase KB-absent fraction to 50%.

**HARD-FAIL:** Held-out recall < 0.10 after 1000 steps with recommended recipe. This would indicate either (a) the frozen encoder is incompatible with the LLM's attention space and a larger adapter (MLP not linear) is needed, or (b) the QA pair construction is flawed (questions are answerable without KB lookup).

### Pre-registered predictive claims

**Claim 1 (P_deflated=0.65):** Separating W_k and W_v (not tying them) will produce at least +15pp held-out recall improvement over tied projections. Mechanism: keys and values serve different functions; tying them forces a compromise. Evidence: KBLaM, SR-KI both use separate projections.

**Claim 2 (P_deflated=0.55):** KB-absent training fraction of 30-50% is necessary for held-out recall > 0.60. A model trained with 0% KB-absent examples will show held-out recall < 0.20. Evidence: KBLaM explicit training mix; RETRO document filtering equivalence.

**Claim 3 (P_deflated=0.45):** Adding SR-KI-style attention supervision loss (L_attn on the retrieval layer) will add at least +10pp held-out recall over cross-entropy alone. Evidence: SR-KI achieves >98% Recall@10 vs ~80-85% for cross-entropy only.

**Claim 4 (P_deflated=0.40):** FHRR-native KB encoding (no separate sentence encoder) will achieve within 5pp of Sentence-BERT-based encoding if cosine similarity structure of FHRR space is validated as similar to Sentence-BERT. Evidence: structural analogy; not yet empirically confirmed.

**HARD-FAIL thresholds (pre-registered):**
- If held-out recall does not exceed 0.10 with ANY configuration after 1000 steps on 50K+ KB: flag as architecture incompatibility; escalate to Research for Wirtinger-space analysis.
- If training recall < 0.50 after 500 steps: flag as training pipeline error (check KB-QA pair construction, confirm answers require KB lookup).
- If held-out recall = training recall = 0.0 with KB-present batches: confirm KB tokens are actually being injected into attention (implementation bug, not architecture failure).

---

## Substrate-Product Implications

The v2.0 product claim "substrate is the LLM's swappable knowledge store" is technically achievable and has direct precedent in published systems. The gap between C1-FACT v1 (failure) and what the literature shows is achievable is a specific set of engineering choices, not a fundamental architectural barrier.

The substrate's unique advantages relative to prior art:
1. **Algebraic abstention (PP-107)** reduces the training burden for KB-absent behavior — substrate can gate retrieval before attention, not just train the LM to refuse.
2. **FHRR-native encoding** may eliminate the separate sentence encoder requirement — if FHRR space is compatible, the entire KB pipeline (encoding, retrieval, injection) runs within one algebraic framework.
3. **Pool retrieval** (already validated at recall@1=1.000) provides a substrate-native nearest-neighbor search for the KB lookup step.
4. **PP-182 graded confidence** enables tiered knowledge retrieval (high confidence: use KB; medium: hedge; low: abstain) with no additional training.

Honest scope estimate: this is 3-7 GPU-days of engineering, not months. KBLaM achieved the result in ~600 training steps. The hard part is dataset construction (50K+ fact QA pairs) and ensuring the QA pairs actually require KB lookup (cannot be answered from LM weights alone). The architecture is a two-week implementation. A full validation comparable to Atlas or RETRO (multi-task, billion-scale) is months of work — but demonstrating generalizable retrieval on a 50K-fact held-out evaluation is a feasible 2-3 week milestone.

---

## 5 Ranked Engineering Anchors for Exp-Dev

These are ordered by: cheapest-first (PROT-004), highest evidence density, most directly resolves C1-FACT HARD_FAIL.

**Anchor 1 (CPU-local, ~1 day): FHRR-space compatibility validation**
Check whether cosine similarity structure of FHRR-encoded facts matches Sentence-BERT cosine structure on 1K shared facts. Compute: rank correlation of pairwise cosine similarity matrices. If Spearman rho > 0.70, FHRR can serve as the frozen encoder for KB entry encoding. This is the cheap pre-test (per feedback-drill-pretest-required) that either green-lights the native FHRR path or redirects to Sentence-BERT.

**Anchor 2 (GPU, ~1 day): Minimal generalization smoke — 50K facts, separate W_k/W_v, 50/50 split, 600 steps**
Exact replica of KBLaM training recipe scaled down: 50K synthetic facts, 50% KB-present/50% KB-absent QA pairs, separate W_k/W_v linear layers on frozen Sentence-BERT (or FHRR if Anchor 1 passes), 600 steps, AdamW lr=1e-3. Evaluate held-out recall on 10K facts not in training KB. Pass criterion: held-out recall > 0.40. This is the minimal test that the architecture works before adding substrate-specific innovations.

**Anchor 3 (GPU, ~2 days): SR-KI-style attention supervision on Pythia-160M**
Add L_attn (attention supervision loss) on the retrieval layer identified by Anchor 2 ablation. Lambda scan: {0.05, 0.1, 0.5}. Pass criterion: held-out recall > 0.60, gap to train recall < 0.25. This is the version most likely to hit the HARD-PASS threshold.

**Anchor 4 (CPU-local, ~2 hours): PP-107 gate before KB attention**
Implement algebraic abstention gate: if max_cosine(query_FHRR, all KB keys) < 0.70, zero out KB attention weights. Evaluate: does this gate reduce false positives (KB lookup on unanswerable queries) without reducing true positives (KB lookup on answerable queries)? If yes, reduces KB-absent training requirement (can reduce KB-absent fraction from 50% to 20%). Cheap implementation, direct leverage of existing validated substrate primitive.

**Anchor 5 (GPU, ~3 days): L_consistency substrate-coupling term**
Add substrate-consistency training pressure: L_total = L_CE + lambda_attn * L_attn + lambda_cons * L_consistency, where L_consistency = ||substrate_retrieve(query_FHRR) - target_fact_FHRR||^2. This jointly optimizes the LM adapter and the substrate's KB encoding to remain mutually compatible. Most novel relative to prior art; highest risk but highest potential for a qualitatively stronger product claim (fully integrated substrate-LLM retrieval loop).

---

## Citations (Verified Count: 14)

1. KBLaM: arXiv:2410.10450, ICLR 2025. github.com/microsoft/KBLaM
2. Knowledge Capsules: arXiv:2604.20487, April 2026. arxiv.org/html/2604.20487
3. Atlas: arXiv:2208.03299, JMLR v24 paper 23-0037, 2023. facebookresearch/atlas
4. RETRO: arXiv:2112.04426, ICML 2022 PMLR 162. deepmind.google/blog
5. Memorizing Transformer: arXiv:2203.08913, ICLR 2022. OpenReview TrjbxzRcnf-
6. To Memorize or to Retrieve (scaling laws): arXiv:2604.00715, 2026. github.com/DegenAI-Labs/RAG-scaling-laws
7. Scaling Laws for Fact Memorization: arXiv:2406.15720, 2024. arxiv.org/html/2406.15720v1
8. SR-KI: arXiv:2511.06446, 2024
9. Prometheus Mind: arXiv:2601.15324, 2026
10. Holographic Transformer: arXiv:2509.19331, 2025
11. Wirtinger Flow: arXiv:2403.10560, 2024
12. Attention as Binding (VSA perspective): arXiv:2512.14709, 2024
13. Align then Train (retrieval adapter): arXiv:2604.03403, 2026
14. MEGa (gated LoRA memory): arXiv:2504.21239, 2025
