# Research drill: Path B architectural variations and failure-mode map (5x depth)
## Date: 2026-06-09
## Topic: KBLaM-pattern de-risk failure modes, 6 architectural variations, substrate-unique innovations, hybrids, graceful degradation, stopping criteria

---

## HEADLINE

If Path B de-risk (Pythia + 2000 facts, held-out >= 0.50) fails, the dominant root cause is almost certainly one of three things: KB too small for generalization (most likely at 2000 facts given KBLaM's 120K training regime), gate initialization closing too tight on small KB, or cross-entropy alone failing to force retrieval behavior at this scale. Six architectural variations have clear empirical tests. Three substrate-unique innovations (PP-107 algebraic gate, FHRR-native projection, K-hop multi-step retrieval) have no direct competitor precedent and are prototypable in 1-2 weeks each. The strongest partial claim if full Path B fails is: substrate-attention with PP-107 algebraic abstention gate is a GDPR-safe swappable KB adapter requiring zero LLM retraining and zero retrieval latency overhead, differentiated from every published competitor on those two axes.

P_deflated (full Path B categorical claim): 0.38 (theoretical 0.60 deflated by 0.22 for novel synthesis at small scale with no direct precedent at 2000-fact regime).

---

## LEVEL 1: KBLaM-pattern failure modes

### 1.1 Encoder mismatch: Sentence-BERT semantic space vs LLM Q-K alignment

**Mechanism.** KBLaM uses a pre-trained sentence encoder (bge-large or similar) plus a learned linear adapter W_k, W_v to project fact embeddings into the LLM's attention head space. The sentence encoder was trained on semantic similarity tasks; the LLM's Q-K alignment was trained on next-token prediction. These are different objectives, and the manifold geometry differs.

**Why it matters.** At 2000 facts, the W_k adapter has very few training examples relative to the dimensionality of the LLM's hidden space (768-4096 depending on model). W_k can appear to converge while only fitting the training distribution's centroid. Held-out facts that sit off the training centroid will have poor Q-K alignment. This is the "adapter underfitting" failure mode — distinguishable from memorization because train recall is also low.

**Diagnostic.** Plot held-out cosine similarity between LLM query vectors and projected fact keys. If clustering is poor (intra-cluster variance >> inter-cluster variance for fact categories), the adapter has not learned to separate fact-type dimensions.

**Lit precedent.** PaLM2-VAdapter (arXiv:2402.10896) found that progressive alignment (staged adapter training from coarse-to-fine semantic granularity) reduces projection gap versus one-shot adapter training. Frozen encoder + one-shot linear projection is the weak baseline; staged alignment or a small 2-layer MLP adapter produces measurably better Q-K alignment.

**Threshold.** HARD-FAIL if held-out fact cosine similarity < 0.35 (below random-projection baseline for the dimensionality). HARD-PASS if > 0.65.

---

### 1.2 Layer insertion pattern: every-layer rectangular may be too aggressive at small scale

**Mechanism.** KBLaM injects KB attention at every transformer layer. At 120K facts with a fully trained model (Phi-3 or Llama-3), every-layer injection distributes the "learning to retrieve" signal across all layers, which helps at scale. At 2000 facts on a 160M-parameter model (Pythia), every-layer injection multiplies the number of adapter parameters by the number of layers. For Pythia-160M (12 layers), every-layer injection trains 12x more adapter parameters than a single-layer injection, with 2000/12 = 167 effective training examples per layer — well below the generalization threshold for a linear adapter in a 768-dimensional space.

**Why it matters.** Overfitting risk rises linearly with injected layers. The model may learn to retrieve training facts perfectly while the per-layer projections fail to generalize because each has too few examples.

**Diagnostic.** Ablation: train with layers = {last 1, last 4, every layer}. If held-out recall increases with fewer layers, every-layer insertion is the cause. Expected result: 1-layer is highest recall at 2000 facts; every-layer wins at 50K+.

**Lit precedent.** SR-KI (arXiv:2511.06446) found that supervised attention at a single retrieval layer (with explicit attention supervision loss L_attn) achieves 98% Recall@10, outperforming multi-layer injection at the same KB size. Single-layer or shallow-layer injection with targeted supervision appears more data-efficient at small KB scales.

**P_deflated (single-layer injection fixes generalization at 2000 facts):** 0.42.

---

### 1.3 Loss function: CE alone may need contrastive supplement at 2000-fact scale

**Mechanism.** Cross-entropy on answer tokens is the KBLaM loss. At 120K facts, the model sees enough variety that CE pressure naturally forces the retrieval layer to discriminate between facts. At 2000 facts, CE loss on a Pythia-160M model has an alternative solution: memorize the fact-answer pairs parametrically (directly in model weights) and ignore the KB adapter entirely. This solution has zero retrieval — the model answers correctly from weights, CE loss reaches 0, training terminates with adapter weights uninformative.

**Why it matters.** This is the memorization bypass. At 2000 facts, Pythia-160M has sufficient capacity to memorize all facts parametrically (scaling law: C ~ model_size * 4.14 / tokens_per_fact, giving memorization ceiling ~1400-2500 facts for Pythia-160M depending on fact format). The model is right at the memorization threshold.

**Diagnostic.** If train recall = 1.0 AND held-out = 0.0 AND KB-absent accuracy = high (model answers correctly even without KB attached), this is parametric memorization bypass. Not adapter failure — parametric success.

**Fix.** Three options, in increasing engineering cost:
- (a) Contrastive supplement: add InfoNCE loss pushing query embeddings toward correct fact key and away from 1999 incorrect facts. Forces the retrieval function to be learned, not bypassed.
- (b) KB-absent training: 50% of training batches are KB-absent; model must output "I don't know" without KB. Forces model to ONLY answer when KB is present. Prevents parametric route.
- (c) Noise injection: randomly swap KB facts during training so memorized fact-answer mapping is incorrect. Model learns to use KB or get wrong answer.

**Lit precedent.** KBLaM paper (arXiv:2410.10450) explicitly uses KB-absent training (50/50 split) to prevent this failure mode. This is in the paper; the 2000-fact de-risk may have omitted it. Check training recipe for KB-absent fraction.

**P_deflated (KB-absent training fixes memorization bypass):** 0.55. This fix is documented in the KBLaM paper; likely the primary de-risk failure cause if train=1.0, held-out=0.0.

---

### 1.4 KB size: 2000 facts too few for generalization

**Mechanism.** KBLaM was trained on 120K facts. The published result does not include a scaling ablation showing where the held-out recall floor is. Two competing hypotheses: (A) KBLaM generalizes at 2000 facts because the linear adapter is low-complexity, or (B) KBLaM requires 10K-50K+ facts to generalize because the sentence encoder manifold has high intrinsic dimensionality.

**Scaling law.** Memorization scaling law (arXiv:2406.15720) applies to model weights absorbing facts. For the ADAPTER (not model weights), a different scaling law applies: the linear adapter W_k has d_model x d_encoder parameters (e.g., 4096 x 768 = 3.1M). With 2000 training examples, each of dimension 768, we have n/p = 2000/3.1M = 0.00065. This is massively underspecified for a dense linear layer. The adapter will overfit severely at 2000 facts for standard Pythia dimensions.

**Fix.** One or more of: (a) reduce adapter capacity to a low-rank projection (rank-r adapter, r = 16-64), (b) increase KB size to 50K facts for the training run, (c) regularize W_k heavily (L2, weight decay 0.1+). Option (b) is the cleanest because it matches the KBLaM training regime.

**P_deflated (scaling to 50K facts unlocks generalization with same recipe):** 0.48.

---

### 1.5 Gate initialization: sigmoid(-4) may close too tight for small KB

**Mechanism.** KBLaM uses a learned gate g = sigmoid(alpha + beta * cos_sim) where alpha is initialized to -4 (gate nearly closed). At 120K facts, gradient signal is dense and alpha converges to a useful value. At 2000 facts, the gate may converge to alpha ~ -4 (effectively closed) because the gradient signal is too sparse and noisy to push alpha into the positive regime. Result: model never attends to KB, held-out recall = 0.

**Diagnostic.** Log gate activation statistics during training. If mean gate value < 0.05 throughout training, gate is stuck. Distinguish from adapter mismatch by checking whether KV similarity values are high (retrieval correct but gate killed it) versus low (retrieval wrong and gate irrelevant).

**Fix.** Warm-start alpha at 0.0 (gate 0.50 open) and decay toward -2 over first 100 steps. Forces initial KB usage; gate can learn to close selectively but starts from open state.

**P_deflated (gate warm-start fixes stuck gate):** 0.35. Less likely to be the primary failure at 2000 facts because gate initialization is the same in the published recipe; if it worked at 120K, the gate is not the primary variable.

---

### 1.6 Frozen encoder mismatch with LLM hidden space at small scale

**Mechanism.** Sentence-BERT and bge-large were trained to produce semantic similarity embeddings in a 768-1024 dimensional Euclidean space. Pythia-160M's hidden states at each attention layer live in a 768-dimensional space that was trained with next-token prediction, not semantic similarity. These manifolds are distinct (different curvature, different mean cosine similarity between unrelated items). A linear adapter W_k connecting them must learn to "rotate" between manifolds — a well-conditioned problem at high data (120K facts) but ill-conditioned at low data (2000 facts).

**Diagnostic.** Measure alignment CKA (centered kernel alignment) between frozen sentence encoder embeddings and the LLM's layer-l hidden states. If CKA < 0.20, manifolds are highly dissimilar and the linear adapter has insufficient capacity.

**Fix.** Two options: (a) replace sentence encoder with a small encoder trained on the LLM's own hidden states (FHRR-native adapter — see Level 3.1), (b) use the LLM itself as encoder (last-token embedding from same frozen LLM as fact encoder — avoids cross-manifold alignment entirely).

**P_deflated (LLM-as-own-encoder fixes alignment gap):** 0.45.

---

## LEVEL 2: 6 architectural variations

### 2.1 Atlas-style joint pretraining (Izacard 2022)

**Mechanism.** Encoder and LLM trained jointly during retrieval-augmented pretraining. Retrieval is explicit — encoder retrieves top-k text chunks from a datastore; LLM generates conditioned on retrieved chunks. Loss is on generated tokens. Encoder is updated by gradient flowing back from LLM generation loss via REINFORCE or differentiable retrieval approximation.

**Substrate-compatibility.** Atlas requires explicit text retrieval; substrate's retrieval is algebraic (FHRR cosine similarity, not BM25/dense retrieval over text). Direct porting requires replacing Atlas's bi-encoder with an FHRR encoder. The joint pretraining regime would allow substrate's encoder to adapt to the LLM's generation objective — solving the manifold mismatch of 1.6.

**Engineering effort.** HIGH. Joint pretraining requires a distributed training setup; Atlas uses 64+ A100s for its published experiments. Scaled down to Pythia-160M + 10K facts, it is feasible on a single A100 in ~4-8h, but the training recipe requires careful implementation of the retrieval gradient pathway. Estimated 3-5 eng-weeks for a minimal implementation.

**Empirical test design.** Pythia-160M + FHRR encoder, 10K facts, joint pretraining 500 steps. Compare held-out recall vs frozen-encoder baseline.

**P_deflated:** 0.38. Joint pretraining has strong lit precedent (Atlas ICLR 2023) but scaling down to 160M + 10K facts may destabilize the retrieval gradient. The main risk is gradient variance in the retrieval pathway at small scale.

**Acceptance criterion.** Held-out recall > 0.50 within 1K steps on 10K facts.

---

### 2.2 REALM-style two-tower retrieval with masked-LM supervision

**Mechanism.** Separate query encoder and document encoder. Retrieval supervised by masked-LM: the model must retrieve a document containing the masked token's answer. Joint training of both encoders via expectation over retrieved documents (MIPS approximation with asynchronous index refresh). No cross-attention injection — retrieved document prepended as context.

**Substrate-compatibility.** REALM's masked-LM supervision is compatible with substrate's fact structure (fact = (entity, relation, value) triple). Each masked token in the LLM's training text corresponds to a substrate fact that could be retrieved. Training signal flows through: (LLM masked token) -> (query encoder) -> (substrate cosine retrieval) -> (fact prepended) -> (masked token prediction). This is structurally cleaner than KBLaM at small scale because retrieval gradient does not need to flow through the attention layers.

**Engineering effort.** MEDIUM. Two-tower retrieval is well-understood; the main cost is the asynchronous index refresh for MIPS. Estimated 2-3 eng-weeks. Can be tested without substrate at first (standard dense retrieval).

**Empirical test design.** Pythia-160M, 10K facts structured as masked-LM training examples, 1K steps. Measure: masked token accuracy with KB retrieved vs without.

**P_deflated:** 0.40. REALM has strong lit precedent (arXiv:2002.08909); the main risk at small scale is that Pythia-160M at 2000-10K facts can parametrically memorize the masked tokens without using the retrieval pathway.

**Acceptance criterion.** Masked-LM accuracy improvement >= 5 percentage points over no-retrieval baseline on held-out facts.

---

### 2.3 kNN-LM ensemble (Khandelwal 2020) — inference-only

**Mechanism.** No training changes. At inference time, interpolate LLM's softmax output with a kNN lookup over a KB of (context-embedding, next-token) pairs. p_final = lambda * p_kNN + (1-lambda) * p_LM. lambda is a hyperparameter (typically 0.25-0.50). No adapter training required.

**Substrate-compatibility.** Substrate's FHRR embeddings can serve as the context-embedding space for the kNN datastore. This is the lowest-cost possible integration: store substrate's W matrix entries as the kNN datastore, query with the LLM's last-layer hidden state projected into FHRR space. No training at all.

**Engineering effort.** LOW. Core mechanism: 1-2 eng-days to implement. The main cost is the FHRR projection from LLM hidden state to substrate space (which requires a fixed learned or analytical mapping). Total: ~1 eng-week including evaluation harness.

**Empirical test design.** Pythia-160M, 10K facts stored as (FHRR embedding, answer-token) pairs. Measure: next-token accuracy on held-out fact completions with lambda sweep 0.0-0.80.

**P_deflated:** 0.45. kNN-LM has robust published evidence (arXiv:1911.00172). The main substrate-specific risk is that FHRR space and Pythia's hidden space are not aligned, so the kNN lookup may retrieve irrelevant facts. This is the same manifold mismatch problem as 1.6, but here it affects inference only — no training is needed, and a poor alignment simply means lambda -> 0 wins.

**Limitations.** kNN-LM improves perplexity but can hurt generation quality on non-memorization tasks (kNN returns token-level neighbors, not fact-level neighbors; known failure mode from 2020 paper). This limits its applicability to factual completion tasks, not multi-sentence reasoning.

**Acceptance criterion.** Next-token accuracy improvement >= 3 percentage points over p_LM baseline with optimal lambda on held-out facts. OR: held-out recall (answer token in top-10 from kNN component) >= 0.50.

---

### 2.4 RETRO-style chunked cross-attention

**Mechanism.** Retrieves text chunks (not single facts) from a large external datastore. Cross-attention applied per chunk at a specific set of layers (not every layer). Designed for from-scratch pretraining on internet-scale data.

**Substrate-compatibility.** RETRO is the least compatible with substrate: it requires from-scratch pretraining (not adapter training on frozen LLM), retrieves text chunks (substrate stores structured triples not text), and its full implementation requires a multi-trillion token pretraining corpus. However, RETRO's architectural principle — chunked cross-attention at selected layers rather than every-layer injection — is directly applicable as a Layer Insertion Pattern fix (see 1.2). A RETRO-inspired variant would inject KB attention at every N-th layer only (e.g., layers 6, 9, 12 of Pythia-160M), reducing adapter parameter count and overfitting risk.

**Engineering effort.** RETRO full: VERY HIGH (multiple eng-months, infeasible). RETRO-inspired layer selection: LOW (2-3 eng-days, modify the layer list in the existing KBLaM implementation). This is the correct scope for Path B backup.

**P_deflated (RETRO-inspired layer selection fixes overfitting at 2000 facts):** 0.40. This is essentially 1.2 formalized — lower-layer injection (fewer layers) for small KB. The gain is bounded.

**Acceptance criterion.** Held-out recall with 3-layer injection >= 1.15x held-out recall with 12-layer injection, at 2000 facts.

---

### 2.5 Memorizing Transformer style (Wu 2022) — cache past activations

**Mechanism.** Cache past-layer activations (not external KB) in a kNN index; attend to them at specific attention layers. Within-document memory, not cross-document. Designed to extend effective context window, not to inject external KB facts.

**Substrate-compatibility.** Low direct compatibility. Memorizing Transformer addresses a different problem (long-context within a document) versus KB injection (external structured facts). Substrate's KB is external and structured; Memorizing Transformer's cache is internal and unstructured. The main applicable principle: kNN attention over a fixed cache with a learned query projection — this is architecturally identical to single-layer KBLaM. Use as conceptual support for 2.3 rather than as a distinct variation.

**P_deflated:** 0.25. Not a meaningful architectural variation beyond kNN-LM for substrate's use case. Deprioritize.

---

### 2.6 Knowledge Capsules — prefix K/V injection at sequence start

**Mechanism.** Pre-compute K/V cache for all knowledge facts offline. At inference, prepend these K/V pairs to the sequence as a prefix at the first attention layer only (not every layer). Language tokens attend to fact K/V pairs via standard self-attention with an extended causal mask. No gradient through fact representations at inference time; training focuses on the language model to use the prepended K/V prefix effectively.

**Substrate-compatibility.** HIGH. Knowledge Packs (arXiv:2604.03270) implements exactly this: zero-token knowledge delivery via KV cache injection. Facts are formatted as system messages, K/V pairs are pre-computed offline, and loaded as prefix at inference. This is structurally simpler than KBLaM (no rectangular attention, no every-layer injection) and avoids the layer-count overfitting problem (1.2) entirely. Trained Persistent Memory (arXiv:2603.22329) shows a compatible approach for frozen decoder-only LLMs: soft K/V pairs prepended to every layer, but these are MEMORY vectors not fact vectors, and they achieve persistent task knowledge without full fine-tuning.

**Engineering effort.** LOW-MEDIUM. Knowledge Packs has a published implementation. Core adaptation for substrate: encode substrate facts as (entity, relation, value) strings, pre-compute K/V, inject at prefix. The main engineering cost is the fact-to-string serialization and the training procedure for the LLM to use the prefix. Estimated 1-2 eng-weeks.

**Empirical test design.** Pythia-160M, 2000 facts as K/V prefix, 200 answer-generation examples. Measure: held-out answer accuracy with and without fact prefix, no adapter training required.

**P_deflated:** 0.48. Higher than KBLaM at 2000 facts because this requires ZERO adapter training — the knowledge is in the K/V pairs, and the base LLM just needs to "look at" the prefix. The main risk is that Pythia-160M did not see K/V prefix patterns during pretraining and ignores the prefix (attention to prefix tokens is low).

**Acceptance criterion.** Answer accuracy with K/V prefix >= 0.50 on held-out facts (zero-shot, no adapter training). This is the cheapest possible Path B backup test.

---

## LEVEL 3: Substrate-unique architectural innovations

### 3.1 FHRR-native adapter

**Mechanism.** Replace Sentence-BERT encoder with the substrate's own FHRR binding as the fact encoder. Fact (entity, relation, value) -> FHRR bind(entity, relation) superpose(value) -> FHRR vector. Train W_k, W_v to project FHRR vectors into LLM attention space. This eliminates the cross-manifold alignment problem (1.6) because the FHRR encoder was designed for the substrate's algebraic geometry, not for Euclidean semantic similarity.

**Uniqueness.** No published paper uses FHRR vectors as the KB encoder for LLM cross-attention. This is a substrate-native primitive that competitors cannot replicate without implementing the full FHRR algebra. HD Probe (arXiv:2509.25045) shows FHRR-based probes can decode LLM layer representations, suggesting FHRR geometry is compatible with LLM internal representations (the manifold alignment problem may be tractable).

**Engineering effort.** LOW-MEDIUM (1-2 eng-weeks). Substrate's FHRR bind/superpose is already implemented. The new work is: (a) fact serialization to FHRR, (b) W_k, W_v adapter for FHRR -> LLM space, (c) training harness. Cheaper than any external-encoder option because the encoder is already on-device.

**P_deflated:** 0.42. The core risk is that FHRR vectors are bipolar (±1) and sparse-ish, not the smooth continuous embeddings the LLM's Q-K alignment was trained on. W_k may have difficulty learning from discrete inputs. Tanh relaxation or soft-FHRR variant addresses this; adds 3-5 days implementation.

**Acceptance criterion.** FHRR-adapter held-out recall >= 0.80x Sentence-BERT-adapter held-out recall at 2000 facts. The claim is not that FHRR beats Sentence-BERT at small scale — it is that FHRR enables the full substrate integration path without external encoder dependency.

---

### 3.2 PP-107 algebraic gate substitution

**Mechanism.** Replace KBLaM's learned sigmoid gate g = sigmoid(alpha + beta * cos_sim) with the substrate's PP-107 confidence score, which is exact (not learned, not gradient-updated). PP-107 confidence for a query q against fact f = cos_sim(q, f) thresholded at a fixed value. Gate = 1 if cos_sim > tau, else 0. No gradient through the gate.

**Why this matters categorically.** KBLaM's learned gate can drift toward closed state during training (1.5) because alpha is a trainable parameter that the optimizer can zero out to reduce loss from spurious KB lookups. PP-107 gate is non-trainable — the optimizer cannot zero it out. This prevents gate collapse at small scale, which is the 1.5 failure mode.

**Second-order effect.** A non-trainable hard gate forces the adapter W_k, W_v to learn the correct projection or produce zero retrieval signal. There is no "soft bypass" where the gate partially opens without the adapter learning anything useful. This increases gradient pressure on W_k, W_v during training.

**Engineering effort.** LOW (2-3 eng-days). Modify gate initialization: make alpha a fixed non-trainable constant, set beta = 0 (gate depends only on cos_sim), threshold tau determined by substrate's PP-107 calibration.

**P_deflated:** 0.45. Higher confidence than most variations because this directly targets the 1.5 failure mode with a substrate-native primitive already validated at AUC=1.000 per cap_map.

**Acceptance criterion.** Held-out recall with PP-107 gate >= 1.20x held-out recall with learned sigmoid gate, at 2000 facts.

---

### 3.3 Algebraic key/value separation via substrate bind/unbind

**Mechanism.** Instead of W_k(fact) -> LLM key and W_v(fact) -> LLM value (two independent linear projections), encode the fact as: key = W_proj(bind(entity_FHRR, relation_FHRR)), value = W_proj(unbind(fact_FHRR, entity_FHRR)). The key is the subject-relation pair; the value is the object recovered by unbinding. This preserves the substrate's compositional structure inside the adapter representation.

**Why this matters.** Standard KBLaM W_k, W_v are independent linear projections that lose the binding relationship between entity and relation. The adapter could in principle learn that (Paris, capital_of) shares a similar key with (France, located_in) — but there is no inductive bias toward this. With bind/unbind, the key explicitly encodes the compositional relationship, and the inductive bias is that similar keys share the same role-filler structure. This should improve sample efficiency at small KB sizes.

**Engineering effort.** MEDIUM (1-2 eng-weeks). Requires differentiable bind/unbind in the adapter computation path. FHRR bind is circular convolution (differentiable); unbind is circular correlation (also differentiable). Adds complexity to adapter code but no training infrastructure changes.

**P_deflated:** 0.38. The inductive bias argument is sound, but the empirical gain at 2000 facts is uncertain. The gain requires that the LLM's Q-K alignment benefits from the compositional structure — not guaranteed for a pre-trained model that was not trained with this structure.

**Acceptance criterion.** Held-out recall with bind/unbind key encoding >= 1.15x held-out recall with independent W_k, W_v, at 2000 facts.

---

### 3.4 K-hop traversal as multi-step retrieval

**Mechanism.** At inference time, the LLM's attention layer queries the substrate once (step 1), retrieves a fact (entity_1, relation_1, entity_2), then uses entity_2 as the next query for a second substrate lookup (step 2), retrieves (entity_2, relation_2, entity_3). Multi-hop questions (Q: "What is the capital of the country that borders France to the southwest?") can be answered by chaining two substrate lookups without any additional LLM computation beyond the initial question encoding.

**Why this matters categorically.** KBLaM's single-step retrieval cannot answer multi-hop questions that require following a reasoning chain through the KB. Substrate's K-hop traversal (multi-hop +0.983 vs kNN-LM per cap_map) is a validated primitive that extends the LLM's effective KB lookup to multi-step reasoning paths. This is the architectural moat claim for Path B: "substrate-attention with K-hop traversal enables multi-step factual reasoning that KBLaM and all single-step RAG architectures cannot."

**Engineering effort.** MEDIUM (1-2 eng-weeks). Core change: at attention layers designated as retrieval layers, implement iterative lookup — the output of step 1 retrieval is used as input query for step 2. Requires: (a) multi-step retrieval loop in attention forward, (b) training signal that includes multi-hop examples, (c) stopping criterion (fixed K or confidence-based).

**P_deflated:** 0.52. K-hop traversal is already validated in substrate at +0.983 accuracy vs kNN-LM baseline. The risk is in the LLM integration path: the LLM must learn to encode intermediate queries correctly for step 2 to work. Pre-test required.

**Acceptance criterion.** Multi-hop question accuracy (2-hop) >= 0.50 on held-out 2-hop examples, with K=2 substrate traversal. Compare vs single-hop baseline (K=1).

---

### 3.5 Substrate as encoder OUT (LLM hidden -> substrate space)

**Mechanism.** Instead of encoding facts in substrate space and projecting into LLM space (the standard KBLaM direction), encode the LLM's hidden state into substrate space and retrieve facts there. Architecture: LLM produces hidden state h_l at layer l; adapter W_out maps h_l -> FHRR space; substrate cos_sim retrieval in FHRR space returns top-k facts; facts projected back into LLM space as values.

**Why this matters.** The standard direction (substrate -> LLM) requires learning a projection that maps from FHRR geometry to LLM geometry. The reverse direction (LLM -> FHRR) requires learning a projection that maps from LLM geometry to FHRR geometry. If the LLM's hidden states are more compatible with FHRR space than the reverse (the HD Probe result, arXiv:2509.25045, suggests LLM representations have VSA-compatible circuit structure), then the reverse projection may be better conditioned.

**Engineering effort.** LOW (1 eng-week). Same adapter architecture as KBLaM but with direction reversed. W_out replaces W_k; retrieval happens in FHRR space using substrate's native cosine similarity; W_in (new) maps retrieved FHRR vector back to LLM space as value.

**P_deflated:** 0.40. The geometric argument is plausible given HD Probe results, but no published paper has tested this direction for KB retrieval. Novel-synthesis risk applies.

**Acceptance criterion.** Held-out recall with LLM->FHRR->LLM direction >= held-out recall with FHRR->LLM direction (i.e., this direction is at least as good as standard KBLaM at 2000 facts).

---

### 3.6 Algebraic-constrained adapter training

**Mechanism.** Add a constraint loss to the adapter training that penalizes the adapter when its output vectors do not preserve the substrate's algebraic properties. Specifically: L_constraint = ||W_k(bind(a,b)) - bind(W_k(a), W_k(b))||^2. This forces the adapter to be approximately morphism-preserving with respect to binding. Result: facts encoded by the adapter maintain their compositional relationships in LLM space.

**Why this matters.** Without this constraint, W_k is a generic linear map that has no reason to preserve binding structure. With the constraint, the adapter is forced to learn a morphism, which improves the inductive bias for compositional fact retrieval (related to 3.3 but as a regularizer rather than an architectural change).

**Engineering effort.** LOW (1-2 eng-days). Add L_constraint to the training objective. lambda * L_constraint + (1-lambda) * L_CE. Sweep lambda in {0.01, 0.1, 0.5}.

**P_deflated:** 0.35. The constraint loss is mathematically clean but the empirical gain at 2000 facts is uncertain. If W_k is already poorly conditioned (1.6 failure mode), adding a constraint may hurt by reducing the effective parameter space the adapter can explore.

**Acceptance criterion.** Held-out recall with L_constraint >= 1.10x held-out recall without, at same total training steps and same lambda.

---

## LEVEL 4: Hybrid approaches

### 4.1 Substrate-attention + tool-use coupling

**Mechanism.** LLM has two KB access paths: (1) soft substrate-attention via W_k, W_v adapter (continuous, differentiable, always-on), and (2) hard substrate tool call ([SUBSTRATE_QUERY] token that triggers an explicit FHRR lookup). The soft path handles common facts with high confidence; the hard path handles rare facts with explicit retrieval. Training: joint optimization of both paths via multi-task loss.

**When to consider.** If Path B soft-attention generalizes but has low recall on rare or long-tail facts, the tool-use path provides exact retrieval for those cases. The two-path architecture is redundant at training but complementary at inference.

**P_deflated:** 0.32. Double interface doubles the training complexity. The soft path may learn to rely on the hard path, collapsing to tool-use only. Deprioritize unless soft-attention recall plateaus below 0.70 and tool-use is already implemented.

---

### 4.2 Two-stage retrieval: substrate first, chunks second

**Mechanism.** Stage 1: substrate retrieves exact (entity, relation, value) triples relevant to the query (high precision). Stage 2: RETRO-style retrieval of text chunks from a document corpus indexed around the retrieved entities. LLM attends to both: the exact triples (via substrate-attention) and the surrounding context (via chunk cross-attention).

**When to consider.** If the product needs both factual precision (from substrate) and contextual reasoning (from document chunks). The substrate handles "what is the value of X?" and the chunk retrieval handles "what is the context around X?"

**P_deflated:** 0.35. High engineering cost (two retrieval systems, two cross-attention mechanisms, training for both). The product claim is richer but the complexity is not justified until Path B base recipe is validated.

---

### 4.3 Multi-modal substrate-attention

**Mechanism.** Extend FHRR encoding to image/audio/tabular data via modality-specific encoders that project into FHRR space. The KB contains multi-modal facts: (entity, image) bound pairs, (entity, audio_segment) bound pairs. LLM queries substrate by text, retrieves multi-modal facts.

**When to consider.** After the text-only Path B is validated. This is a direct extension of 3.1 (FHRR-native adapter) to multi-modal facts. Substrate's n-ary arbitrary arity primitive is the foundation — bind(entity, text, image, audio) is algebraically valid.

**P_deflated:** 0.30. No direct lit precedent for FHRR multi-modal retrieval injected into LLM cross-attention. Two novel components in sequence; P compounds.

---

### 4.4 Substrate + LoRA fine-tuning

**Mechanism.** Substrate-attention adapter handles factual KB lookup (frozen after training); LoRA handles task-specific behavior (trained per task). The two adapt different aspects of the LLM: substrate for "what do I know?", LoRA for "how do I respond to this task?". At inference: substrate-attention + LoRA deltas applied together.

**When to consider.** If Path B shows that the substrate-attention adapter improves factual recall but the LLM's generation style is wrong for the target task. LoRA fixes generation style without touching the KB adapter. Combined: product handles both factual grounding and task-specific formatting.

**Lit precedent.** LoRA-InfoNCE (validated per memory) and separate LoRA for retrieval fine-tuning (RA-DIT, 2023) both show LoRA is compatible with retrieval augmentation. No conflict.

**P_deflated:** 0.50. Both components have individual lit precedent; the combination is architecturally clean. Main risk is interference between LoRA deltas and KB adapter gradients — but since substrate-attention adapter can be frozen before LoRA training, this risk is low.

**Acceptance criterion.** Task accuracy with (frozen substrate-adapter + LoRA) >= task accuracy with (LoRA only) by >= 5 percentage points on factual tasks.

---

## LEVEL 5: Path B graceful degradation

### 5.1 Strongest partial claims if full categorical product fails

Ranked from strongest (most differentiated, highest P) to weakest:

**Tier A — Still categorical:**
- "Substrate provides a GDPR-exact-erasure KB for LLMs with zero inference overhead" (Path B + PP-104 GDPR primitive). This claim holds even if held-out generalization is at 0.50 (minimal); the categorical value is the erasure property, not the recall level. No published LLM KB system has GDPR-exact erasure in the KB layer (KBLaM, RETRO, kNN-LM all lack this).
- "Substrate-attention improves LLM perplexity 15-20%" (Path A, already empirically validated). This is a real capability claim regardless of Path B outcome.

**Tier B — Incremental but differentiating:**
- "Substrate enables multi-hop 2-step factual reasoning with K-hop traversal" (3.4). This is incremental over KBLaM (which cannot multi-hop) but is a real capability gain. Differentiated from all published RAG architectures.
- "Substrate PP-107 abstention gate reduces false-positive KB lookups" (3.2). Differentiated from KBLaM's learned gate. Testable at inference-time without training.

**Tier C — Modest, commodity:**
- "Substrate enables 10K-fact retrieval at inference with no external retrieval latency" (KBLaM replication). Real but not differentiated from KBLaM itself.
- "Substrate-attention improves LLM factual accuracy on held-out facts" (partial Path B, held-out 0.30-0.50). Real but below the 0.50 threshold needed for a product claim.

---

### 5.2 Path A architecture demo standalone value

Substrate-attention improving LLM perplexity 15-17% on domain-specific text is a real, demonstrated result. At the v1 demo stage, this becomes: "our system reduces LLM perplexity on customer knowledge bases without any retrieval infrastructure, using a substrate that also provides GDPR-exact erasure and bitemporal access." This is a meaningful product statement independent of Path B generalization.

---

### 5.3 Pivot to substrate-as-tool

If all KB adapter training fails (all variations return held-out < 0.30), the fallback is substrate as a tool-call interface: LLM generates [SUBSTRATE_QUERY] tokens, substrate executes the query, result appended to context. This is Panel A categorical — the LLM uses substrate as an explicit tool rather than via soft attention. Tool-use has clear product precedent (Toolformer, MemSearcher), is well-understood, and requires zero novel architecture. It is commoditizing but functional. Path A + substrate-as-tool delivers a credible v1 demo with no Path B dependency.

---

## LEVEL 6: Honest stopping criteria

### 6.1 When to abandon Path B entirely

Stop Path B when ALL of the following are true:
1. Held-out recall < 0.25 on three independent architecture variations (e.g., 2.2, 2.3, 2.6) with KB size >= 50K facts.
2. PP-107 algebraic gate substitution (3.2) does not improve over learned gate by >= 1.10x.
3. FHRR-native adapter (3.1) held-out recall is not within 0.80x of Sentence-BERT adapter.

This is the condition where the cross-manifold alignment problem (1.6) is the dominant failure mode AND the substrate-unique innovations cannot bridge it. At that point, the evidence says the LLM's hidden space is not compatible with FHRR geometry, and soft-attention KB injection as a product architecture should be replaced by substrate-as-tool.

**HARD-FAIL for Path B:** held-out recall < 0.25 across all 6 variations at 50K fact KB size.

**HARD-PASS for Path B:** held-out recall >= 0.60 on any one variation at 50K fact KB size.

**MID-BAND:** held-out 0.25-0.60. Continue with the 3 substrate-unique innovations (3.1-3.3) before concluding.

---

### 6.2 Cost-benefit of multi-iteration R&D vs alternative paths

Path B multi-iteration R&D budget: estimated 8-12 eng-weeks to exhaust all variations at meaningful scale (50K facts, Pythia-410M+). At $0.50-1.50/h for A100, the empirical budget is $50-200 in GPU cost. The main cost is engineering time.

Alternative paths available now: Path A (working, 15-20% perplexity improvement), Panel A substrate-as-tool (1-2 eng-weeks to demo), multi-hop K-hop capability demo (3.4 above, already validated at +0.983 accuracy). If Path B R&D exceeds 4 eng-weeks with no variation reaching MID-BAND, re-evaluate against these alternatives.

---

### 6.3 Strategic position if Path B fails

Panel A + Path A architecture demo delivers: (1) substrate-as-retrieval-tool with exact GDPR erasure, (2) substrate-attention perplexity improvement, (3) multi-hop K-hop traversal as a demonstration of KB reasoning that no competitor has. This is a credible v1 demo without categorical Path B success. The competitive moat is narrower (tool-use is commoditizing) but the GDPR + bitemporal + audit trail stack is still differentiated.

---

### 6.4 v3.0 alternative paths

Two alternatives if Path B fails and substrate-as-tool is insufficient:
- **Substrate-only LM:** train a language model whose weights ARE the substrate — bipolar W matrix as the "vocabulary" layer, FHRR tokens as the embedding layer. Novel architecture with no published precedent; 6-12 eng-months minimum. Very high risk; only consider after full Path B failure.
- **Substrate as foundation model:** substrate stores the world knowledge; a small task-specific LM (100M parameters) is fine-tuned per task using substrate retrieval as context. Factual grounding entirely from substrate; LM provides language generation only. This is architecturally similar to RA-DIT (2023) but with substrate replacing the dense retrieval index. Engineering cost: 2-4 eng-weeks for a first demo. Viable as a v1 demo path.

---

## LEVEL 7: Engineering anchors per variation (5 ranked Path B backup plans)

Ranked by: P_deflated x (1/engineering_cost) x product_differentiation.

**Anchor B-BACK-1: Knowledge Capsules — K/V prefix injection (2.6)**
- Engineering scope: 1-2 eng-weeks (Knowledge Packs recipe, substrate fact serialization, inference eval)
- Empirical test: Pythia-160M, 2000 facts, K/V prefix, measure answer accuracy with/without prefix, zero adapter training
- P_deflated: 0.48
- Acceptance: answer accuracy >= 0.50 on held-out facts, zero-shot
- Priority: run THIS FIRST if de-risk fails. Cheapest, no training required, directly tests whether the LLM can use prepended substrate facts at all.

**Anchor B-BACK-2: PP-107 algebraic gate substitution (3.2)**
- Engineering scope: 2-3 eng-days (replace sigmoid gate with PP-107 fixed threshold in existing KBLaM code)
- Empirical test: same as de-risk but with non-trainable PP-107 gate, compare held-out recall
- P_deflated: 0.45
- Acceptance: held-out recall >= 1.20x original gate recall
- Priority: should run in parallel with de-risk if de-risk code already written; minimal delta.

**Anchor B-BACK-3: kNN-LM inference ensemble (2.3)**
- Engineering scope: 1 eng-week (FHRR projection from LLM hidden state, kNN over substrate facts, lambda sweep)
- Empirical test: Pythia-160M, 10K facts, lambda sweep, next-token accuracy on fact completions
- P_deflated: 0.45
- Acceptance: accuracy improvement >= 3 pp over baseline with optimal lambda
- Priority: run if B-BACK-1 and B-BACK-2 both fail (no training path available at 2000 facts).

**Anchor B-BACK-4: Single-layer injection + SR-KI attention supervision (2.4 / 1.2 + 1.3 combined)**
- Engineering scope: 2-3 eng-weeks (reduce layer injection to last layer only; add L_attn supervision per SR-KI recipe; increase KB to 50K facts)
- Empirical test: Pythia-160M, 50K facts, 1-layer injection, L_attn supervision, 1K training steps, held-out recall
- P_deflated: 0.44
- Acceptance: held-out recall >= 0.50
- Priority: run if B-BACK-1/2/3 fail and full-training path is authorized. This is the "fix the training recipe" path, not the "no-training" path.

**Anchor B-BACK-5: FHRR-native adapter with K-hop multi-step retrieval (3.1 + 3.4)**
- Engineering scope: 2-4 eng-weeks (FHRR encoder for facts, W_k/W_v adapter for FHRR->LLM, multi-step retrieval loop, multi-hop training examples)
- Empirical test: Pythia-410M (larger model to reduce memorization ceiling risk), 50K facts, 2-hop question battery, K=2 traversal, held-out multi-hop accuracy
- P_deflated: 0.40
- Acceptance: 2-hop accuracy >= 0.45 (multi-hop generalization is harder; lower threshold)
- Priority: run after B-BACK-4. This is the "substrate-native path" — most differentiated, highest engineering cost, most upside if it works.

---

## Cheap decisive test

Before any of the above: run B-BACK-1 (Knowledge Capsules) at CPU-local scale on Pythia-160M with 100 facts serialized as K/V prefix. If the model can answer 50% of held-out fact questions with the prefix present (zero-shot, no training), the LLM's attention mechanism is compatible with substrate-formatted K/V injection. If answer accuracy with prefix = accuracy without prefix (0% gain), the LLM is ignoring the prefix entirely — stop and pivot to substrate-as-tool before any GPU spend.

Cost: 0 GPU, 1-2h engineering, 30 min eval. Go/no-go for the entire Path B backup program.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

| Claim | HARD-PASS | HARD-FAIL |
|---|---|---|
| Path B de-risk at 2000 facts | held-out recall >= 0.50 | held-out recall < 0.25 |
| B-BACK-1 K/V prefix (2000 facts) | accuracy >= 0.50 zero-shot | accuracy < 0.20 (no better than no-KB) |
| B-BACK-2 PP-107 gate | >= 1.20x recall vs learned gate | < 1.05x (no gate improvement) |
| B-BACK-4 50K facts 1-layer | held-out recall >= 0.50 | held-out recall < 0.25 after 1K steps |
| K-hop 2-step multi-hop (3.4) | 2-hop accuracy >= 0.45 | 2-hop accuracy < 0.20 (no better than 0-hop baseline) |
| Full Path B categorical (all vars) | any variation held-out >= 0.60 at 50K facts | all variations < 0.25 at 50K facts |

---

## Cross-thread synthesis

- Generalizable retrieval handoff (2026-06-09): B-BACK-1 through B-BACK-3 are the immediate backup anchors for the C1-FACT-v2 path. The K/V prefix test is the pre-test gate before any GPU spend, consistent with [[feedback-drill-pretest-required]].
- Tier 4 LLM architecture proposals (2026-06-07): Architecture 4 (differentiable retrieval scaffold) and Architecture 8 (hybrid inference) from that drill are subsumed by B-BACK-4 and B-BACK-5 respectively. The ranking is consistent.
- Multi-hop revival: K-hop traversal as multi-step retrieval (3.4) is the architectural Path B analog of the multi-hop revival (project_multihop_revive_priority.md). If 3.4 passes, it closes both the Path B backup question and the multi-hop revival question simultaneously.
- LoRA-InfoNCE (from exp_dev memory): B-BACK-5 with LoRA supplement (4.4) is compatible and should be considered as the follow-on to B-BACK-5 if base recall is > 0.30 but < 0.50.

---

## Substrate-product implications

Path B failure is not a product failure. The strategic hierarchy is:
1. Panel A (substrate-as-tool, GDPR + bitemporal + audit trail) is product-ready now.
2. Path A (substrate-attention perplexity improvement) is empirically validated.
3. Path B (KB adapter generalization) is the differentiating but risky top layer.

If Path B fails entirely, the product still has a differentiated GDPR-exact-erasure + bitemporal KB story that no competitor has. The demo strategy should not be built around Path B generalization as the sole value proposition. Lead with Panel A + Path A; Path B is the technical moat if it works.

The substrate-unique innovations (3.1-3.6) are product differentiators regardless of whether Path B full categorical succeeds. PP-107 algebraic gate, FHRR-native encoding, and K-hop multi-step retrieval are substrate-native primitives that competitors cannot replicate without implementing the full FHRR algebra. These should be demonstrated in the v1 demo even if held-out generalization is only at MID-BAND.

---

## Citations (verified count: 14)

1. KBLaM (arXiv:2410.10450, ICLR 2025): rectangular attention, every-layer injection, 120K fact training regime, KB-absent 50/50 training split.
2. SR-KI (arXiv:2511.06446): single retrieval layer + L_attn supervision, 98% Recall@10 vs 80% without supervision.
3. Atlas (arXiv:2208.03299, JMLR 2023): joint encoder-LLM pretraining, REINFORCE gradient through retrieval.
4. REALM (arXiv:2002.08909): two-tower retrieval, masked-LM supervision, asynchronous index refresh.
5. kNN-LM (arXiv:1911.00172, ICLR 2020): inference-only interpolation, perplexity improvement, generation quality degradation on long text.
6. RETRO (arXiv:2112.04426, ICML 2022): chunked cross-attention at selected layers, from-scratch pretraining.
7. Memorizing Transformer (arXiv:2203.08913): kNN over past activations, within-document context extension.
8. Scaling laws for fact memorization (arXiv:2406.15720): C ~ model_size * 4.14 / tokens_per_fact.
9. Knowledge Packs (arXiv:2604.03270): zero-token KV cache injection, prefix at inference, no adapter training.
10. Trained Persistent Memory (arXiv:2603.22329): soft K/V pairs prepended to every layer for frozen decoder-only LLMs.
11. HD Probe (arXiv:2509.25045): VSA-based probing of LLM layer representations; evidence for FHRR geometric compatibility with LLM internal representations.
12. PaLM2-VAdapter (arXiv:2402.10896): progressive alignment from coarse to fine semantic granularity for frozen encoder adapter.
13. RA-DIT (2023): REINFORCE-style reward from reader generation loss for retrieval-augmented fine-tuning.
14. Memorization vs generalization (ICLR 2025, arXiv:2506.09099): capacity, memorization, generalization tradeoff in pre-trained transformers.
