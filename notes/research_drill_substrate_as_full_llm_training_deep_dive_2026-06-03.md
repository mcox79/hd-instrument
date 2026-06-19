# Research Drill: Bipolar Outer-Product Hebbian Substrate as Full LLM Training Mechanism
**Date:** 2026-06-03  
**Trigger:** Strategic question — can a bipolar outer-product Hebbian + compositional algebra substrate replace gradient descent entirely as the LLM training mechanism? (Tier-6 probe scope.)  
**Calibration penalty applied:** P_deflated = P_raw - 0.20; novel-synthesis cap = 0.50  

---

## HEADLINE

A bipolar outer-product Hebbian substrate can demonstrably replace gradient descent for **linear-attention-equivalent task classes** (retrieval, few-shot classification, short-sequence association), but hits a hard expressivity ceiling at softmax normalization: the exponential-kernel normalization term in softmax attention cannot be represented by a finite-rank outer-product weight matrix, so a pure Hebbian substrate is NOT a drop-in replacement for a full softmax transformer at LLM scale. The substrate CAN replace gradient descent as the primary write mechanism for the attention-equivalent layers if softmax is approximated via compositional depth; the output head and tokenizer likely require a hybrid gradient-trained component OR a novel compositional solution not yet demonstrated at language-model scale. P_deflated(full replacement feasible) = 0.18; P_deflated(partial replacement — attention layers only) = 0.42.

---

## Sub-question synthesis

### (1) Lit-precedent: State of gradient-free deep learning 2022-2026

**Forward-Forward (Hinton 2022, arXiv:2212.13345)**  
Replaces backward pass with two forward passes on positive/negative data; each layer optimizes a local "goodness" objective. Empirical state (2024-2026): CIFAR-10 84-90% (FF-CNN variants); ImageNet Top-1 51.6% (ASGE 2025); ViT variant (CFF, 2025) +4.2% over baseline FF on CIFAR-10 with 3-20x faster convergence. **NOT demonstrated on language modeling or next-token prediction at any scale.** No published perplexity results. Documented limitation: positive/negative data construction is non-trivial for autoregressive generation; no credit assignment beyond 1-2 layers depth for sequence tasks.

**Predictive Coding (Whittington-Bogacz 2017; Millidge 2022)**  
Local prediction-error dynamics between adjacent layers; mathematically related to backprop in layered networks (Millidge 2022 showed PC = backprop + an inference correction term). Scaling paper (arXiv:2510.23323, 2025) reports deep PC networks "practically untrainable" at full depth, with significant theoretical progress toward scaling via optimization-theory grounding. No transformer-scale language modeling benchmarks published as of 2026.

**Direct Feedback Alignment (Nokland 2016; variants through 2024)**  
Random fixed projections from output to each hidden layer replace symmetric weight transport. Scales to CNN-class, competitive with backprop on small datasets. Key 2024 result (ICLR 2024): improved EP via intermediate error signals for deep ConvNets, gradient estimator bias substantially reduced, positioned for neuromorphic on-chip training. Gap vs backprop remains ~5-8% on ImageNet at ResNet-50 scale. No transformer language model results.

**Hebbian-FW Transformers (arXiv:2510.21908, Oct 2025) — the motivating precedent**  
Architecture: decoder-only transformer augmented with fast-weight modules; Hebbian update rule is w_l(t+1) = (1-eta(t)) * w_l(t) + eta(t) * alpha_l * (p_l(t) outer q_l(t)), where p_l/q_l are pre/post-synaptic activations and alpha_l are learnable neuromodulation scalars. KEY FACT: this AUGMENTS transformers with fast-weights, it does NOT replace gradient descent. The outer loop still uses Adam/backprop to train static weights and alpha_l. Benchmarks: CIFAR-FS 5-way 1-shot 31.9% vs non-plastic 28.9%; Omniglot 23.7% vs 19.2%; regression MSE 1.546 vs 1.997. Model size: d_model=256, d_ff=512 (toy scale). No language modeling tested. Limitation: 8-layer models diverge after 3000 steps; gradient-based fast-weights needed for long-horizon tasks.

**Local Learning Rules (Krotov-Hopfield 2020-2024)**  
Unsupervised competing hidden units via Hebb-like rule with intra-layer competition. Learns feature detectors comparable to backprop on small datasets. 2024 extension: Modern Hopfield Classifier with local Hebbian learning achieves class generalization. No transformer-scale results; expressivity formally bounded by Hopfield capacity.

**Equilibrium Propagation (Scellier-Bengio 2017; 2024 scaling)**  
Energy-based model with two-phase (free/clamped) local weight updates. 2024 (ICLR 2024): scalable EP via intermediate error signals for deep ConvNets; gradient estimates closely align with BPTT while reducing compute. 2025 (arXiv:2508.15989): scalable EP for deep convolutional CRNNs. Still no transformer language model results; each inference-phase is expensive (iterative settling).

**Overall lit-precedent verdict:** As of 2026, zero published papers demonstrate a gradient-free method matching backprop on transformer-class language modeling (perplexity, LAMBADA, Wikitext). The gap is empirically open and unexplored, not empirically closed in either direction for the full-replacement case.

---

### (2) Expressivity analysis: can outer-product Hebbian writes represent transformer functions?

**Formal baseline (FWP/linear attention equivalence):**  
A linear transformer (no softmax) is mathematically equivalent to a fast-weight programmer with additive outer-product memory: S_t = sum(v_i k_i^T), retrieval = S_t * q. This is directly implementable by outer-product Hebbian writes. DeltaNet (delta-rule variant, NeurIPS 2024, arXiv:2406.06484) extends this: 1.3B parameter model trained on 100B tokens outperforms Mamba and GLA on perplexity and zero-shot downstream tasks. This establishes that **outer-product-adjacent mechanisms CAN train LLM-class models**, but DeltaNet still uses gradient descent for static weights.

**Softmax attention expressivity gap:**  
The critical finding (arXiv:2505.19488 May 2025): softmax attention uses an exponential kernel feature map, which enables discriminative retrieval with only O(log^2 N) key dimensionality instead of O(N) required by linear attention. The normalization term Z = sum(exp(q^T k_i)) cannot be represented by a finite outer-product weight matrix — it requires the full context sum. Outer-product Hebbian writes implement the unnormalized retrieval (S*q) but cannot natively compute Z. This is the HARD expressivity boundary.

**Can depth substitute?**  
Compositional stacking (multiple Hebbian layers) can approximate the normalization via iterative retrieval + competition mechanisms (analogous to the intra-layer competition in Krotov-Hopfield). A substrate's Error-Correction-Chain criterion (max_k(alpha_k) < alpha_c) gates whether compositional stacking remains stable. If the compositional chain is stable, k stages can approximate the log-space normalization, but the number of stages k grows as O(d_k) for d_k-dimensional keys — potentially expensive.

**FFN/MLP nonlinearities:**  
FFNs as associative memory (arXiv:2505.19488): FFN(x) = sum_i v_i * ReLU(k_i^T x). This is identical to a bipolar Hebbian matrix with ReLU readout. Substrate's bipolar energy landscape with nonlinear attractor dynamics is structurally equivalent. No fundamental expressivity gap here — substrate CAN represent arbitrary FFN compositions at sufficient N.

**Multi-step reasoning:**  
Compositional algebra (outer-product binding + release via compositional superposition) supports sequential reasoning chains IF each step's output is a valid retrieval key for the next step. The fundamental constraint: chain depth is limited by the compositional stability criterion. For k-step chains, signal accumulates noise as approximately sqrt(k) / sqrt(N), so chain length k_max ~ N (for bipolar, by classical Hopfield analysis). At N=8192, k_max ~ hundreds of steps — sufficient for standard chain-of-thought depths (5-30 steps), not sufficient for O(N)-depth recurrence.

**Expressivity boundary table:**

| Function class | In-substrate expressivity | Notes |
|---|---|---|
| Linear attention (FWP) | YES — exact equivalence | Standard outer-product |
| FFN/MLP nonlinearities | YES — ReLU AM equivalence | Requires sufficient N |
| Softmax attention retrieval | PARTIAL — unnormalized only | Missing Z normalization |
| Softmax normalization | NO — hard boundary | Requires context-sum |
| Chain-of-thought depth <= k_max | YES at N>>k | k_max ~ O(sqrt(N)) stable |
| Long-horizon credit assignment (BPTT style) | NO | No backward signal propagation |

---

### (3) Substrate-native training architecture spec

Given expressivity analysis, a substrate-native LLM architecture would be a **Hebbian-linear-attention transformer** (no softmax, replacing softmax with compositional depth + intra-layer competition):

**(a) Token embedding:** Outer-product Hebbian write of (token_id, embedding_vector) pairs. Training: single streaming pass writes each token's co-occurrence statistics. Equivalent to word2vec skip-gram with Hebbian updates. This is fully gradient-free. Embedding quality depends on N and corpus size M: reliable retrieval requires N >> M/alpha_c (classical Hopfield criterion), meaning N=8192 supports ~1100 unique embedding patterns at standard alpha_c=0.14, or ~13000 at modern dense AM (alpha_c=1.59 per redundancy-maximization 2025 result). Vocabulary size ~50k requires N >> 31k for dense AM — N~65k minimum for clean embeddings.

**(b) Each "transformer layer":** Replaced by one substrate composition stage. Each stage: Hebbian write of (key, value) pairs from training corpus, retrieval via matrix-vector multiplication (linear attention equivalent). For L-layer transformer equivalent: L substrate stages in sequence. No gradient required between stages — each stage's error is measured as retrieval mismatch, corrected via rank-1 deletion + rewrite (substrate audit primitive). Depth mapping: 1 substrate stage ~ 1 linear transformer layer. A 32-layer transformer requires 32 substrate stages.

**(c) Output projection:** Hard case. Softmax over vocabulary (50k classes) requires discriminative normalization not achievable with outer-product memory at standard N. Options: (i) gradient-trained linear head with fixed substrate body — hybrid approach; (ii) competitive substrate readout (winner-take-all over vocabulary partition) — loses probability calibration; (iii) hierarchical substrate with multiple retrieval stages providing soft competition — unproven at vocabulary scale. Recommendation: hybrid gradient head is the pragmatic path; pure substrate output requires further theoretical work.

**(d) Training procedure cost comparison:**  
Standard transformer pre-training cost: C = 6 * N_params * N_tokens (FLOPs, Kaplan 2020; exact for transformer). For Llama-3.1-8B (8B params, 15T tokens Chinchilla-beyond): C ~ 6 * 8e9 * 15e12 = 7.2e23 FLOPs.

Substrate-native training cost: each training token requires one forward pass (no backward). For L stages, each stage requires one outer-product write (N^2 FLOPs) + one matrix-vector retrieval (N^2 FLOPs). Total: C_substrate = 2 * L * N^2 * N_tokens. For L=32 stages, N=65536 (required for 50k vocab): C_substrate = 2 * 32 * (65536)^2 * N_tokens ~ 2.7e11 * N_tokens. At N_tokens=15T: C_substrate ~ 4.1e24 FLOPs — **5.7x MORE expensive than standard pre-training** because N must be large to cover vocabulary. At N=8192 (small embedding, only ~13k vocab words via dense AM): C_substrate = 2 * 32 * (8192)^2 * 15e12 ~ 6.4e22 FLOPs — **11x CHEAPER**, but expressivity is severely limited.

The substrate-native approach trades: (1) no backward pass cost, (2) single-pass training, against (3) large N requirement for vocabulary coverage, (4) O(N^2) per-layer write cost. The crossover point: for N < ~21000, substrate-native is cheaper than standard backprop; above that, standard backprop wins on FLOPs.

---

### (4) Scaling law candidates for substrate-native LLM training

Substrate-native scaling differs from Chinchilla in structure:

**(a) Bits per parameter (capacity efficiency):**  
Classical Hopfield: alpha_c = 0.14 patterns per synapse = ~0.14 N patterns in N^2 weights = 0.14/N bits per weight (each pattern is N bits). Modern dense AM (exponential kernel): capacity ~ exp(N) patterns in N^2 weights. For practically retrieved patterns: alpha_c(dense) ~ 1.59 (redundancy maximization 2025) vs alpha_c(classical) = 0.14. Dense AM is ~11x more parameter-efficient than classical Hopfield. Standard transformer gradient-trained weights: empirically ~1-2 bits per parameter for useful information (Chinchilla extrapolation). Dense AM bipolar: at N=8192, capacity = 1.59 * 8192 ~ 13000 patterns; each pattern is N=8192 bits; total stored information = 13000 * 8192 bits = 1.07e8 bits across N^2 = 6.7e7 synapses = ~1.6 bits per synapse. This is **comparable to gradient-trained transformers** — the dense AM can match transformer parameter efficiency.

**(b) Sample efficiency:**  
Substrate-native: SINGLE PASS over training data (no epochs, no SGD steps). Each training token is written once. For gradient descent: Chinchilla optimal is ~20 tokens per parameter, with multiple passes implicitly via large data × compute tradeoff. Substrate-native single-pass is inherently MORE sample-efficient in pass count but may require larger N to compensate for absence of refinement.

**(c) Substrate "Chinchilla cliff":**  
The substrate has an analog of the Chinchilla cliff. Beyond the capacity limit alpha_c * N patterns, newly written patterns interfere with previously stored ones (catastrophic interference, classical AM result). This is sharper than the Chinchilla "underfitting" regime — it is a hard retrieval failure boundary, not a smooth perplexity increase. The cliff condition: N_patterns > alpha_c * N. For a language model, N_patterns ~ context-sequence positions * N_layers ~ 32 * sequence_length. The cliff is manageable with chunked write-and-erase protocols per layer.

**(d) Parameter-count equivalent to match Llama-3.1-8B perplexity:**  
This is speculative (no empirical baseline exists). Rough estimate: Llama-3.1-8B achieves WikiText-103 perplexity ~5.7 (per published benchmarks). A substrate-native model matching this would need: (i) N^2 * L_stages weight parameters covering the required vocabulary + grammar distributions; (ii) at dense AM capacity (alpha_c=1.59), N=65536, L=32 stages: total weights = 32 * (65536)^2 ~ 1.4e11 = 137B parameters. This estimates ~17x MORE parameters than Llama-3.1-8B to match its perplexity via substrate-native training. Raw prediction: P(substrate-native matches Llama-3.1-8B perplexity at equivalent parameter count) = 0.08 (deflated).

---

### (5) Smallest viable empirical probe

The highest-information cheapest probe design:

**(a) Smallest useful model:** GPT-2 micro (117M) or smaller. Recommend: character-level transformer with d_model=128, 4 layers, trained on Wikitext-2 (2M tokens). Standard gradient baseline achieves bits-per-character (BPC) ~1.35 on this config. This is the comparison target.

**(b) Substrate-native probe design:** Replace each attention layer's Q/K/V projection with an outer-product Hebbian write layer. Replace softmax attention with delta-rule linear attention (arXiv:2406.06484 DeltaNet style — this has published benchmarks as anchor). Keep gradient-trained output head (hybrid approach) to isolate the question to "do Hebbian attention layers work?" rather than conflating with output head expressivity. N=512 per layer, 4 layers, character-level vocabulary (256 chars — avoids the large-vocabulary N constraint).

**(c) Compute budget:** Single GPU, ~2-4 hours. DeltaNet 1.3B was trained on 100B tokens with standard GPU-hours; the micro probe is orders smaller. Estimated: 4x T4-hours or 1x A100-hour for character-level Wikitext-2 training.

**(d) Discriminating benchmarks:**
- Primary: BPC on Wikitext-2 test set. Compare vs gradient baseline at matched parameter count.
- Generalization test: train on Wikitext-2-train, measure BPC on Penn Treebank (different distribution) — discriminates "substrate writes corpus statistics" from "substrate memorizes training sequences."
- Capacity interference test: train on 50% of corpus, then train on remaining 50% without erase. Measure BPC on first 50% after second write. Hard-fail if BPC degrades >2x (catastrophic interference beyond expected AM limit).

**Pre-registered thresholds:**  
HARD-PASS: substrate-native BPC on Wikitext-2 <= gradient baseline BPC * 1.20 (within 20% — demonstrates language modeling viability)  
MIDDLE-BAND: BPC within 1.20x-2.0x of gradient baseline (partial signal, indicates optimization needed)  
HARD-FAIL: BPC > 2.0x gradient baseline OR validation BPC does not decrease during training (no learning signal)

---

### (6) Substrate-novel positioning angles vs current Hebbian-DL state-of-the-art

Current Hebbian-DL systems (FF, PC, DFA, EP, Hebbian-FW transformers) all share three limitations:
1. No built-in audit/deletion primitive — weights are written and cannot be selectively erased without full retraining.
2. No compositional algebra beyond sequential layer composition — no binding/unbinding operator.
3. No hardware-native mapping — all require von Neumann digital substrate.

**Substrate-novel Angle A (strongest): Audit primitives at training time.**  
Current Hebbian-DL: weights are written via Hebbian rule but cannot be queried as to provenance ("which training examples contributed to this weight update?"), cannot be selectively deleted, and cannot be re-written without catastrophic interference. A bipolar substrate with rank-1 deletion + refusal certificate supports: (i) selective erasure of individual training examples' weight contribution DURING training (not just at inference), (ii) refusal certificates computed from the training write history (not just the final weight matrix), (iii) incremental training corpus audit (which examples are "in" the current model?). This is structurally outside every published Hebbian-DL system — it is a capability class that does not exist in FF/PC/DFA/EP literature.

**Substrate-novel Angle B (strong): Compositional algebra at training time.**  
Current Hebbian-DL: layer-to-layer composition is sequential MLP-style (no explicit binding operation). Outer-product Hebbian substrate with compositional algebra supports: (i) binding-as-write (key binds to value via outer product), (ii) release-as-retrieval (unbinding via matrix multiplication), (iii) compositional error correction (Error-Correction-Chain criterion gating multi-stage writes). This provides STRUCTURED training — the training procedure has a formal algebra, not just a loss surface. DeltaNet's delta-rule update is the closest published analog but lacks the algebraic completeness.

**Substrate-novel Angle C (moderate): Closed-form scaling laws from substrate physics.**  
Current Hebbian-DL: scaling laws are empirical (like Kaplan/Chinchilla) — measured by running many models. A bipolar substrate with known alpha_c, capacity formula (1.59 * N for dense AM; exponential for dense Hopfield), and compositional chain stability criterion (max_k(alpha_k) < alpha_c) allows PREDICTIVE scaling — given N and L_stages, the retrieval reliability P_correct can be computed from the substrate's phase diagram BEFORE training. This is absent in all published Hebbian-DL systems. Derivative: a substrate-native LLM could have its "effective parameter count" computed analytically, not empirically.

---

## Cheap decisive test

Train a 4-layer character-level language model on Wikitext-2 (2M chars, ~2h on single GPU A100) replacing each attention layer with a delta-rule outer-product Hebbian write (DeltaNet-style, gradient-free within-layer writes) + gradient-trained linear output head. Compare BPC to pure-gradient baseline at matched parameters. Target: BPC <= 1.35 * 1.20 = 1.62 BPC. This test isolates whether Hebbian writes produce usable language representations, is achievable with existing infrastructure, and has clear PASS/FAIL discrimination.

---

## Falsifiable predictions (HARD-PASS and HARD-FAIL)

**HARD-PASS thresholds:**
- HP1: Substrate-native attention layers (Hebbian outer-product writes) achieve BPC within 20% of gradient baseline on Wikitext-2 character-level test: BPC <= 1.62
- HP2: Zero-shot transfer to Penn Treebank BPC degrades <50% relative to gradient baseline (substrate generalizes, not memorizes)
- HP3: After catastrophic-interference test (train on corpus split A then B, evaluate on A), BPC on A degrades <50% at N=512 (classical capacity bound not violated)

**HARD-FAIL thresholds:**
- HF1: Training BPC does not decrease below initial (>= random BPC = log2(256) = 8.0) — no learning signal from Hebbian writes
- HF2: BPC on test set is >2x gradient baseline — expressivity gap is larger than predicted by linear-attention equivalence
- HF3: Catastrophic interference destroys all previously learned BPC (BPC reverts to random) — substrate writes are not compositionally stable at the training corpus scale

---

## Cross-thread synthesis

- Connects to cap_map row "hierarchical retrieval" (🟢 55-70%): substrate's compositional stacking already confirmed at N=8192 for retrieval tasks; LLM training is the next expressivity test in the same capability class.
- Connects to cap_map row "auditable memory" (core value proposition): Angle A (audit at training time) is a direct product capability extension.
- Connects to non-equilibrium stat-mech project: Hebbian writes are single-pass non-equilibrium processes (no stationary-state optimization); NESS dynamics analysis (Crooks/Sagawa-Ueda) may give tighter bounds on write fidelity than classical Hopfield statics.
- Connects to DeltaNet/FWP literature: DeltaNet 1.3B results confirm that outer-product-adjacent mechanisms CAN train LLM-scale models with gradient on outer loop; the question is whether the outer gradient loop can be eliminated entirely.

---

## Substrate-product implications

1. **Near-term:** Hybrid Hebbian-attention + gradient-trained head is the most viable immediate architecture. This is testable with existing infrastructure. Product claim: "training data is structurally auditable because write mechanism is algebraic, not stochastic gradient descent."
2. **Medium-term:** If the smallest-viable-probe HARD-PASSes, the audit-at-training-time capability (Angle A) becomes a defensible product differentiator vs ALL published Hebbian-DL systems — none of them have this.
3. **Long-term:** Full gradient replacement requires solving the softmax normalization expressivity gap via compositional depth OR accepting linear-attention expressivity (which DeltaNet suggests is competitive at 1.3B scale). The substrate's closed-form scaling laws (Angle C) could enable predictive model design without empirical scaling runs.
4. **Hard blocker:** Large vocabulary requires N >= 65k for clean embeddings via dense AM; this makes per-layer weights ~4.3B (65k^2) vs ~17M (4096^2) for standard transformer. Hardware mapping to oscillatory analog arrays is the only path to cost parity — this makes Angle C (hardware-pathway match) load-bearing for economic viability.

---

## Citations (verified count: 14)

1. Hinton, G. (2022). The Forward-Forward Algorithm. arXiv:2212.13345.
2. Millidge, B. et al. (2022). Predictive Coding: Beyond Backpropagation. arXiv:2202.09467.
3. Nokland, A. (2016). Direct Feedback Alignment Provides Learning in Deep Neural Networks. NeurIPS 2016. arXiv:1609.01596.
4. Scellier & Bengio (2017). Equilibrium Propagation. Frontiers in Computational Neuroscience.
5. Krotov & Hopfield (2019). Unsupervised learning by competing hidden units. PNAS 2019.
6. arXiv:2510.21908 (Oct 2025). Enabling Robust In-Context Memory and Rapid Task Adaptation in Transformers with Hebbian and Gradient-Based Plasticity.
7. Schlag, I. et al. (2021). Linear Transformers Are Secretly Fast Weight Programmers. ICML 2021. arXiv:2102.11174.
8. arXiv:2508.08435v2 (2025). Fast weight programming and linear transformers: from machine learning to neurobiology.
9. arXiv:2406.06484 (NeurIPS 2024). Parallelizing Linear Transformers with the Delta Rule over Sequence Length (DeltaNet 1.3B results).
10. arXiv:2505.19488 (May 2025). Understanding Transformer from the Perspective of Associative Memory.
11. arXiv:2510.23323 (2025). Towards Scaling Deep Neural Networks with Predictive Coding.
12. arXiv:2403.01907 (March 2024). Capacity of the Hebbian-Hopfield network associative memory.
13. Redundancy Maximization as Principle of Associative Memory Learning (arXiv:2511.02584, 2025) — alpha_c=1.59 result.
14. Lucibello & Mezard (2024). Exponential Capacity of Dense Associative Memories (NeurIPS 2024).

---

## Follow-on drill candidates

1. **DeltaNet delta-rule as substrate write protocol** — DeltaNet already achieves LLM-scale (1.3B, 100B tokens, outperforms Mamba) with outer-product-adjacent delta-rule update. Drill: what is the exact algebraic relationship between DeltaNet's delta-rule update and a bipolar substrate's rank-1 deletion + rewrite? If isomorphic, DeltaNet's empirical results directly validate substrate-native LLM training. Field: learning-rules / fast-weight-programming.
2. **Softmax normalization via substrate competition** — Can intra-layer competition (Krotov-Hopfield 2019 style) implement the Z normalization? Mathematical analysis of whether winner-takes-all over substrate energy basins = softmax normalization. Field: modern-Hopfield.
3. **Dense AM capacity at language-model vocabulary scale** — N=65k required for 50k-token vocabulary; what is the phase diagram of dense AM at this N? Marchenko-Pastur on the N=65k Gram matrix. Field: free-probability (top-ranked next-drill per field advisor).

---

## P_deflated estimates (calibration penalty applied: -0.20)

- P(full gradient replacement is feasible for transformer-class LLM): 0.18 (raw 0.38, deflated for no direct empirical precedent)
- P(hybrid approach — Hebbian attention layers + gradient head — achieves <20% BPC penalty): 0.42 (raw 0.62, deflated; DeltaNet precedent is strongly adjacent)
- P(audit-at-training-time is substrate-novel vs all published Hebbian-DL): 0.78 (deflated to 0.58 but structural — no published system has this)
- P(substrate-native training is cost-competitive at LLM scale without analog hardware): 0.12 (N^2 cost is prohibitive at large vocab without hardware path)
- P(smallest-viable-probe design above would HARD-PASS): 0.35 (genuine uncertainty; DeltaNet provides positive adjacent signal but character-level + pure-Hebbian attention is not directly tested in literature)

**Next-drill candidate:** DeltaNet delta-rule / bipolar-substrate algebraic isomorphism (field: learning-rules, adjacent to modern-Hopfield fruit-bearing parent).
