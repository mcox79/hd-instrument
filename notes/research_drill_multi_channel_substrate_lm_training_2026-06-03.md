# Research Drill: Multi-Channel Parallel Training Signals — Substrate Primitive-to-Channel Mapping
**Filed:** 2026-06-03
**Topic:** Can a bipolar associative-memory substrate with 12 operational primitives provide multi-channel parallel training signals analogous to biological neuromodulators + multi-modal sensory integration for transformer LLM training?
**2x discipline:** This is a paradigm-angle drill distinct from prior full-replacement / integration-depth notes filed today.
**Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]:** P_deflated = P_raw - 0.20; novel-synthesis cap = 0.50.

---

## HEADLINE

Current frontier LLM training is structurally single-channel: one scalar cross-entropy loss, one gradient, one optimizer state per parameter. Biological neural networks train via at least 7 chemically-distinct neuromodulator channels (dopamine RPE, acetylcholine salience, serotonin uncertainty, norepinephrine arousal, oxytocin social valence, histamine wakefulness, GABA inhibitory gating) PLUS parallel multi-modal sensory channels and multi-axis valence dimensions. A bipolar outer-product associative-memory substrate's 12 operational primitives map onto 8 independent training-signal channels spanning write / erase / repulse / monitor / contextualise / interpolate / diversify / certify — a richer signal space than any published multi-task or multi-modal ML system. P_deflated(joint 4+ primitive multi-channel training outperforms single-loss on a small transformer) = 0.38 after calibration penalty.

---

## Sub-Question 1: Mechanical Current-LLM Training

### (a) Forward pass mechanics
Tokenizer (BPE, ~50k vocab) maps input string to integer token sequence t_1...t_L. Embedding lookup E: {0..V-1} -> R^d_model maps each token to a d_model-dimensional vector. Each transformer layer applies:
- Multi-head attention: Q=XW_Q, K=XW_K, V=XW_V; Attn(Q,K,V) = softmax(QK^T / sqrt(d_k))V
- Feed-forward: FFN(x) = W_2 * ReLU(W_1 * x + b_1) + b_2
- LayerNorm + residual at each sub-layer
Total depth: 32 layers (Llama-3.1-8B); ~96 layers (GPT-4 class).

### (b) Loss function and the single gradient signal
Cross-entropy loss: L = -(1/L) * sum_t log P(t_{i+1} | t_1...t_i). This produces ONE scalar L per batch. Backpropagation computes dL/dw for every parameter w by reverse-mode automatic differentiation. The ENTIRE information content of the training signal for one batch is this one number. Per token, log P lies on (-inf, 0]; the gradient magnitude at position i depends on how wrong the prediction was, but all positions compete for the same scalar loss before aggregation. This is a single loss channel.

### (c) Optimizer state
AdamW maintains two per-parameter momentum accumulators:
- m_t = beta_1 * m_{t-1} + (1-beta_1) * g_t   [first moment, direction]
- v_t = beta_2 * v_{t-1} + (1-beta_2) * g_t^2  [second moment, scale]
- w_{t+1} = w_t - lr * m_t_hat / (sqrt(v_t_hat) + eps) - wd * w_t

At Llama-3.1-8B scale (~8B parameters), this requires storing 3x8B = 24B floats in optimizer state alone (~96 GB in float32). The optimizer signal is still derived from the SAME single cross-entropy gradient — it tracks moving averages of it.

### (d) Sample efficiency and Chinchilla
Kaplan et al. (2020, arXiv:2001.08361): L ~ N^(-0.076) * D^(-0.095) + irreducible. Hoffmann et al. (2022, Chinchilla, arXiv:2203.15556): compute-optimal training requires D_opt ~ 20 * N_params training tokens. For Llama-3.1-8B: ~8B params -> ~160B tokens minimum. Effective FLOPs per token: ~6N per forward+backward = ~48B FLOPs per token for 8B model. Sardana and Frankle (2023, arXiv:2401.00448) show inference-adjusted scaling prefers even more data-rich training. Practical sample efficiency is poor: each token contributes one scalar loss increment before being discarded.

### (e) Gradient signal richness across layers
Layer-wise gradient spectral analysis (Li et al. 2025, arXiv:2504.10766): high-quality reasoning data produces SMALLER, MORE STABLE gradient updates; gradient singular values cluster tightly. Lower layers receive highly attenuated gradients due to vanishing (residual connections mitigate but do not eliminate). Upper layers receive strong gradients from the cross-entropy head. The key finding: gradient signal at layer k carries information about the PREDICTION ERROR AT THE OUTPUT ONLY. It carries no information about intermediate layer quality, geometric structure of representations, or novelty/familiarity signals.

### (f) Why current training is fundamentally single-channel
The single-channel structure follows from three architectural choices:
(i) One loss: L_CE is the only training objective in pre-training.
(ii) One backpropagation graph: dL/dw_k computed by a single chain rule.
(iii) One optimizer: all parameters share a single update rule.
Multi-task / multi-modal variants ADD auxiliary losses but still SUM or WEIGHT them into a single scalar before backprop: L_total = L_CE + lambda_1 * L_contrastive + ... This is still one gradient computation. The network cannot distinguish "this parameter learned quickly" from "this parameter is novel vs familiar" — all distinctions collapse into a single real number per step.

---

## Sub-Question 2: Biological Multi-Channel Training

### (a) Seven neuromodulator channels as independent training signals
Biological neural network training is fundamentally multi-channel because neuromodulators are DIFFERENT MOLECULES with different receptors, different projection patterns, different timescales, and different gating targets.

**Dopamine (DA):** Reward prediction error (RPE) = actual_reward - predicted_reward. Phasic DA signals (VTA, substantia nigra) gate long-term potentiation (LTP) at striatal synapses. Schultz et al. (1997, Science): DA neurons fire to unexpected rewards, are suppressed by omission. Nair et al. (2024, Cell Reports, PMC11571066): DA transients encode RPE INDEPENDENT of learning rate — they are a pure error signal. Channel semantics: "update weights toward outcomes that exceeded expectation; suppress pathways that led to worse-than-expected outcomes."

**Acetylcholine (ACh):** Associative salience and cholinergic gating. Namboodiri et al. (2025, biorxiv, PMC11741319): accumbal ACh signals associative salience during learning — ACh marks stimuli WORTH associating with outcomes, regardless of valence. Yu and Dayan (2005, Neuron): ACh signals expected uncertainty (known unknowns), NE signals unexpected uncertainty (unknown unknowns). Channel semantics: "boost plasticity when stimulus-outcome association is salient; suppress when routine."

**Serotonin (5-HT):** Risk/satiation/long-term discount. Cools et al. (2008): 5-HT encodes expected aversive uncertainty; 5-HT depletion increases risk-seeking. High 5-HT = conservative updating. Channel semantics: "constrain rapid weight changes; weight distal outcomes over proximate ones."

**Norepinephrine (NE):** Arousal and unexpected uncertainty gating. Cohen and Aston-Jones (2005): NE via locus coeruleus gates global cortical gain — high NE = explore (exploit-explore tradeoff). Yu and Dayan (2005): NE signals unexpected uncertainty = "model is wrong, consider exploration." Channel semantics: "when NE high, increase effective learning rate globally; use as a network-wide gain multiplier."

**Oxytocin:** Social bonding and trust modulation. Preferentially strengthens social/cooperative associations.

**Histamine:** Wakefulness and arousal modulation. Gates whether any learning happens at all (awake vs asleep).

**GABA (inhibitory gating):** Controls which circuits are plastic. GABA-B receptor activation suppresses dendritic LTP. Channel semantics: "veto plasticity in specific circuits while permitting it in others."

The key structural fact: these are not just "different learning rate scalars." Each modulator acts on DIFFERENT receptor subtypes in different cell compartments with different timescales (DA: 0.1-1s phasic; 5-HT: seconds to minutes tonic; histamine: circadian). They constitute PARALLEL, ASYNCHRONOUS, INDEPENDENT training signal channels.

### (b) Multi-modal sensory as parallel input feature channels
Visual, auditory, tactile, proprioceptive, interoceptive, nociceptive, and olfactory inputs project to different primary cortices and are processed IN PARALLEL. Cross-modal integration happens in superior colliculus and association cortex. Each sensory modality is an independent source of prediction error: I can predict incorrectly about auditory events without any error about visual events. This gives the brain N_modalities independent error sources per experience. Multi-modal learning research (PMC11655826, 2024 brain-inspired MSINN): multisensory integration neural networks integrating visual and audio senses confirms cross-modal representations form via coincident activation.

### (c) Valence dimension multiplicity
Formal structure of valence channels:
- Sign: positive / negative / neutral (3 values)
- Temporal: proximate (now) / distal (future) / retrospective (past) (3 values)
- Certainty: certain / uncertain / ambiguous (3 values)
- Familiarity: novel / familiar / habituated (3 values)

Full valence space: 3^4 = 81 distinguishable states, each potentially activating a different combination of neuromodulators. Real brains likely use a lower-dimensional subspace (~7-12 effective dimensions), consistent with the 7 named neuromodulators.

---

## Sub-Question 3: Multi-Channel ML Training Literature

### (a) Multi-task learning (MTL)
Caruana (1997); Ruder (2017 survey). Auxiliary losses from related tasks improve feature representations via gradient sharing. Typical channel count: 2-5 tasks. CLIP (Radford et al. 2021): image-text contrastive gives 2 modality channels + InfoNCE loss direction. KEY LIMITATION: all auxiliary losses are summed into ONE gradient before optimizer update. True parallelism is absent.

### (b) Multi-modal foundation models
CLIP (Radford 2021): InfoNCE contrastive between image encoder and text encoder. Flamingo (Alayrac et al. 2022): visual + language with cross-attention. Gemini (Google 2024): image, audio, video, text. Channel count by modality: 2-4 inputs. BUT: gradient still flows from a single joint loss. Multi-modal training is multi-CHANNEL INPUT, not multi-channel gradient signal. The loss aggregation collapses signal diversity before weight update.

### (c) Multi-objective RL and constitutional AI
MORLAIF (Guo et al. 2024, arXiv:2406.07295): decomposes RLHF into separate preference models for toxicity, factuality, sycophancy. Multiple reward scalars combined via scalarization before PPO update. Safe RLHF (ICLR 2024): safety + helpfulness as separate reward models, constrained PPO. Constitutional AI (Bai et al. 2022): multi-principle AI feedback. Channel count: 3-8 reward dimensions. STILL single gradient after scalarization. Genuine multi-channel would require separate PPO update trajectories per reward dimension with conflict-resolution before parameter write.

### (d) Self-supervised auxiliary objectives
MAE (He et al. 2022): reconstruction + representation. SimCLR/MoCo: contrastive. JEPA (LeCun 2022): joint-embedding prediction. Multi-objective SSL (SLIP, SILC, etc.): 2-4 objectives combined with weights. Same aggregation problem applies.

### (e) Curriculum and active learning
Bengio et al. (2009) curriculum: training order modulation is a 1-dimensional channel (difficulty). Active learning: informative sample selection is another 1-dimensional channel. Neither provides true parallel gradient channels.

### (f) Neuro-inspired ML training rules
Dopaminergic RL (Sutton-Barto Temporal Difference): one channel (TD error = biologically-grounded RPE). Three-factor Hebbian rules (Gerstner et al. 1996; Fremaux-Gerstner 2016 review): pre*post*modulator, where modulator is a scalar global neuromodulator signal. Published three-factor implementations: one neuromodulator per training loop (e.g., dopamine). Multi-neuromodulator three-factor rules (combining DA + ACh + NE simultaneously) are theoretically described in computational neuroscience but NOT implemented in any published LLM training loop.

KEY FINDING: The ML field has proposed neuromodulator-inspired training rules but has never implemented more than 1-2 simultaneously, and never at LLM scale.

**Summary table — training channel count by method:**

| Method | Input channels | Gradient channels | True parallelism |
|---|---|---|---|
| Standard LLM pre-training | 1 | 1 | No |
| Multi-task learning | 1 | 1 (summed) | No |
| CLIP | 2 (image+text) | 1 (InfoNCE) | No |
| Multi-modal (Gemini) | 4 | 1 (joint) | No |
| MORLAIF | 1 | 1 (scalarized) | No |
| Constitutional AI | 1 | 1 (multi-principle summed) | No |
| Three-factor Hebbian | 1 | 2 (pre*post + modulator) | Partial |
| Proposed substrate | 1 | up to 8 | YES (parallel write ops) |

---

## Sub-Question 4: Substrate Primitive-to-Channel Mapping (Load-Bearing Table)

Each of the 12 primitives provides a DISTINCT training signal channel when applied in parallel. The channels are orthogonal in function: they answer DIFFERENT questions about the same training sample, producing DIFFERENT weight-update signals.

### Primitive 1: Outer-product Hopfield write (Hebbian)
- **Training signal:** Constructive — strengthen connection between co-active patterns.
- **Plain language:** "Remember this pattern."
- **Biological analog:** DA-gated LTP. When a rewarding outcome co-occurs with a stimulus, dopamine gates LTP at the synapse encoding that stimulus-response association.
- **ML analog:** Standard cross-entropy gradient descent.
- **Unique contribution:** This IS the single-loss channel. Channel 1 of 8; the baseline.

### Primitive 2: Certified rank-1 deletion (Fisher-class removal)
- **Training signal:** Destructive, targeted — erase a specific pattern from weight space with mathematical certificate. Weight update is OPPOSITE in direction to the write, targeting a specific stored pattern.
- **Plain language:** "Forget this pattern specifically, with proof of removal."
- **Biological analog:** LTD + synaptic depotentiation. Low-frequency stimulation or mismatch signals (5-HT-mediated) drive LTD at specific synapses. The serotonin channel encodes "this association was aversive/costly, weaken it."
- **ML analog:** Machine unlearning (Golatkar 2020, Chien 2024 class). Certified removal via influence function rank-1 Newton step. Currently post-hoc only; in multi-channel training this would be an ONLINE parallel signal.
- **Unique contribution:** Standard gradient descent has no explicit forget signal. Cross-entropy can de-weight patterns only indirectly by strengthening competing patterns. Explicit deletion certificate is a NOVEL channel that single-loss training cannot provide.

### Primitive 3: Sherman-Morrison rank-1 update (curvature-adjusted write)
- **Training signal:** Second-order constructive — write this pattern with curvature adjustment, weighting the update by inverse Hessian geometry.
- **Plain language:** "Remember this pattern, but scale the update by how hard this association was to learn."
- **Biological analog:** Acetylcholine-gated plasticity. ACh signals associative SALIENCE (Namboodiri 2025) — how surprising and worth-associating a stimulus-outcome pair is. High ACh boosts the learning rate for this specific association based on its unexpectedness. The SM update scales by local curvature, which correlates with novelty (novel patterns = high curvature = large update).
- **ML analog:** L-BFGS / quasi-Newton rank-1 Hessian approximation. GaLore memory-efficient training (Zhao et al. 2024, arXiv:2402.05961).
- **Unique contribution:** Provides a curvature-weighted signal SEPARATE from the plain gradient magnitude. AdamW approximates this via second-moment estimate, but that estimate cannot distinguish "high curvature because novel" from "high curvature because conflicting."

### Primitive 4: Free-cumulant spectral fingerprint (Voiculescu kappa_n)
- **Training signal:** Self-diagnostic monitor — measure whether the weight matrix is storing patterns in a degenerate subspace. Hutchinson trace estimation gives a scalar measure of W's spectral coverage. High trace = W is full-rank, diverse. Low trace = W is collapsed (representation collapse).
- **Plain language:** "Monitor whether the network is learning diverse representations or collapsing."
- **Biological analog:** Norepinephrine arousal signal. NE via locus coeruleus gates cortical GAIN broadly — when NE is high (unexpected uncertainty, surprise), the network is pushed to use more of its representational capacity. Cohen-Aston-Jones (2005): NE as gain modulator.
- **ML analog:** Hutchinson trace estimation for Hessian monitoring. Spectral norm regularization. Representation collapse detection in contrastive learning (Jing et al. 2022 dead neurons / collapse).
- **Unique contribution:** A SELF-MONITORING channel that feeds back into the training loop. Standard single-loss training has no representation-collapse detector as an online training signal.

### Primitive 5: Counterfactual associative memory via rank-1 substitution
- **Training signal:** Model-based evaluation — predict what WOULD HAVE been stored if this input were different. Counterfactual weight state W' = W - (u v^T) + (u' v^T); counterfactual loss delta_L = L(W') - L(W).
- **Plain language:** "Evaluate alternative outcomes that were not taken."
- **Biological analog:** Orbitofrontal cortex (OFC) counterfactual valuation. OFC encodes "what would have happened if I had chosen otherwise" — critical for model-based RL and credit assignment. Distinct circuit from striatal DA RPE.
- **ML analog:** Causal abstraction / interchange interventions (Geiger 2023, JMLR). Optimal ablation / activation patching (Li NeurIPS 2024).
- **Unique contribution:** A MODEL-BASED signal (what should I have stored?) as opposed to the model-free gradient. No published LLM uses counterfactual weight perturbation as an online training signal.

### Primitive 6: Hierarchical negative-pattern memory tree (refusal/anti-cert)
- **Training signal:** Certificate repulsion — mark an input class as REPULSED, building a certificate tree of negative examples. Weight updates driven by negative examples as explicit repulsion vectors.
- **Plain language:** "Actively avoid this pattern class — build a hierarchy of what not to know."
- **Biological analog:** Basolateral amygdala (BLA) fear memory. BLA encodes fear/aversion associations via a circuit DISTINCT from nucleus accumbens reward (DA channel). This is an "anti-reward" channel — negative valence associations stored in a separate memory system from positive ones.
- **ML analog:** RLHF/DPO refusal fine-tuning. Contrastive representation: push negative examples away in embedding space.
- **Unique contribution:** Explicit hierarchical REPULSION. Standard cross-entropy reduces probability of wrong tokens but does not explicitly repel in weight space. Explicit anti-Hebbian certificate is structurally distinct from lowering a probability.

### Primitive 7: Bipartite anti-Hebbian active repulsion (contrastive CHL)
- **Training signal:** Discriminative — reduce co-activation between patterns that should NOT be associated. Anti-Hebbian update: delta_W = -alpha * pre * post^T for co-activating pairs that should be separated. Contrastive Hebbian Learning (CHL) is the symmetric complement to Hebbian LTP.
- **Plain language:** "Separate these patterns — make them distinguishable from each other."
- **Biological analog:** GABAergic interneurons gate which neurons participate in a given representation; active inhibition at specific synapses prevents spurious co-activation. GABA-B mediated LTD is the molecular implementation.
- **ML analog:** Contrastive Self-Supervised Learning (SimCLR negative pairs). Equilibrium Propagation negative-phase update (Scellier-Bengio 2017). DPO's negative-example penalty term.
- **Unique contribution:** Explicit pairwise repulsion, complementary to P6 (certificate-tree) and P2 (single-pattern deletion). The trio P2/P6/P7 gives three distinguishable "forget" channels: forget one pattern (P2), avoid a class (P6), distinguish two patterns (P7).

### Primitive 8: Hippocampal spatial place-field encoding (sparse Hopfield)
- **Training signal:** Sparsity / episode uniqueness — encode this input in a sparse, unique representation to reduce pattern interference.
- **Plain language:** "Memorize this specific instance uniquely — reduce interference with nearby memories."
- **Biological analog:** Hippocampal CA3 pattern completion + DG pattern separation. Dentate gyrus performs sparse encoding (5% active neurons), CA3 stores sparse representations. High ACh during exploration shifts toward pattern separation; low ACh shifts toward pattern completion.
- **ML analog:** Sparse autoencoders for interpretability. Mixture-of-experts routing (sparse activation). Sparse dictionary learning (LASSO, ICA).
- **Unique contribution:** A SPARSITY REGULARIZATION signal as an independent training channel with explicit episodic-vs-semantic distinction. Standard training has L2/weight decay but no structural sparsity that preserves individual memory instances.

### Primitive 9: Hierarchical recurrent associative-network retrieval
- **Training signal:** Chain consistency — ensure that multi-step reasoning chains can complete retrieval. Recurrent retrieval: W^k * x converges to a clean attractor at each hop k. Signal: if retrieval diverges at hop k, penalize the weight configuration.
- **Plain language:** "Check that multi-step reasoning chains converge stably."
- **Biological analog:** Prefrontal cortex (PFC) working memory maintenance + goal-directed retrieval. PFC maintains a chain of sub-goals and tests whether each intermediate retrieval step is recoverable. PFC is modulated by DA (D1 receptors stabilize working memory representations).
- **ML analog:** ARMT (Associative Recurrent Memory Transformer, ICML 2024, arXiv:2407.04841). Hierarchical Memory Transformer (HMT, arXiv:2405.06067, 2024). Recurrent state supervision in RNNs.
- **Unique contribution:** A CHAIN CONSISTENCY signal — multi-hop retrieval quality as an independent training objective. Standard transformers are not trained with explicit recurrent-retrieval consistency objectives.

### Primitive 10: Bilinear matrix-trace estimator Tr(W A W' B)
- **Training signal:** Cross-layer coherence — measure the cross-correlation between two weight matrices across different layers. Tr(W_l * A * W_{l'} * B) measures how much layer l's weight geometry aligns with layer l'. Signal: inter-layer coherence as a training objective.
- **Plain language:** "Ensure different layers are learning consistently with each other."
- **Biological analog:** Corticothalamic coherence — thalamus provides a global clock signal synchronizing cortical oscillations across areas. The thalamic signal is "are you aligned with the global representation?"
- **ML analog:** CKA (Centered Kernel Alignment) for layer representational similarity. Bilinear MLP mechanistic interpretability (arXiv:2410.08417, 2024). Knowledge distillation / Fitnets consistency regularization across layers.
- **Unique contribution:** A CROSS-LAYER COHERENCE signal. Standard single-loss training has no mechanism for a layer to "know" whether it is consistent with other layers beyond the gradient signal passed through.

### Primitive 11: Multi-modular parallel associative memory banks
- **Training signal:** Diversity / disagreement — operate multiple independent memory modules in parallel; use ensemble disagreement as an uncertainty signal.
- **Plain language:** "Consult multiple experts in parallel and note where they disagree."
- **Biological analog:** Cerebellar parallel fibers + Purkinje cell integration. ~160,000 parallel fiber inputs per Purkinje cell compute a parallel ensemble prediction. Discordance among Purkinje cells generates an error signal (climbing fibers = the prediction-error teacher signal).
- **ML analog:** Multi-head attention (parallel retrieval modules). Mixture-of-Experts routing. Deep Ensemble uncertainty estimation (Lakshminarayanan 2017).
- **Unique contribution:** Explicit DISAGREEMENT signal across parallel modules. Standard multi-head attention exists but does not use inter-head disagreement as an explicit training objective. Inter-module disagreement as a training signal is unused in published LLM training.

### Primitive 12: Stacked independent-W composition (multi-stage read-write)
- **Training signal:** Compositional stability — verify that multiple write-read cycles chained with independent weight matrices remain stable. End-to-end composition consistency: W_{k+1}(W_k(x)) -> stable attractor.
- **Plain language:** "Ensure that multiple memory operations chained together produce a coherent result."
- **Biological analog:** Prefrontal-hippocampal-striatal circuit composition. A complete goal-directed action requires coordinated write/read across PFC (goal), hippocampus (sequence), striatum (action selection). Each stage has independent plasticity rules.
- **ML analog:** Multi-hop reasoning (ARMT), chain-of-thought training, compositional generalization benchmarks (SCAN, COGS).
- **Unique contribution:** A COMPOSITIONAL CONSISTENCY signal. Standard training optimizes each layer's gradient independently; no explicit cross-layer compositional consistency objective exists.

### Maximally diverse 4-primitive channel set
For a minimum-viable multi-channel system, these 4 primitives span the most orthogonal signal space:
- P1 (write / constructive) — baseline positive channel
- P2 (erase / destructive) — anti-P1, serotonin analog
- P4 (spectral monitor / self-diagnostic) — orthogonal to P1/P2, NE analog
- P7 (contrastive repulsion / discriminative) — orthogonal to P4, GABA analog

Together: write + erase + monitor + repulse = constructive + destructive + diagnostic + discriminative = 4 truly independent signal channels. Adding P5 (counterfactual, OFC analog) and P9 (chain consistency, PFC-DA analog) gives a 6-channel system covering the core biological learning circuit.

---

## Sub-Question 5: Minimum-Viable Multi-Channel Training Experiment

### Design principle
Smallest experiment exercising P1 + P2 + P7 as INDEPENDENT, PARALLEL training signal channels for a small autoregressive transformer LM. "Parallel" means: each channel computes its own weight-update direction, and the three updates are COMPOSED (not summed into a single scalar) before the parameter step.

### Architecture
- Model: GPT-2 Small equivalent — 12 layers, 12 heads, d_model=768, ~117M parameters.
- Tokenizer: GPT-2 BPE, vocab=50257.
- Baseline: standard Adam + cross-entropy pre-training on same corpus with same compute.

### Training channels (explicit)
**Channel 1 (P1, Hebbian write):** Standard cross-entropy loss on next-token prediction. Gradient g_1 = dL_CE/dw via backprop.

**Channel 2 (P7, anti-Hebbian contrastive):** For each batch of positive examples (real next tokens), generate negative examples via random token replacement at 20% of positions. Anti-Hebbian loss: L_anti = -log(1 - P(negative_token | context)) summed over replaced positions. Gradient g_2 = dL_anti/dw via backprop. Direction: OPPOSITE to what would be learned from the negative tokens.

**Channel 3 (P4, spectral monitor signal):** Every K=100 steps, compute Hutchinson trace estimate of W_V projection matrices: Tr(W_V) = E[z^T W_V z] for z ~ N(0,I). If Tr(W_V) < threshold_low (representation collapse), add trace-maximization penalty L_trace = -lambda * Tr(W_V). Gradient g_3 = dL_trace/dw when active.

**Channel composition (NOT simple summation):**
- Compute g_1, g_2, g_3 independently.
- Conflict-resolve: for each parameter w, if sign(g_1) == sign(g_2), combine additively. If signs conflict, project g_2 onto the orthogonal complement of g_1 (Gram-Schmidt). This preserves the biological analogy: the dopamine channel (P1) and GABA inhibitory channel (P7) should not cancel but should address different dimensions.
- Update: w <- w - lr * (g_1 + alpha_2 * g_2_projected + alpha_3 * g_3_active)

### Corpus
OpenWebText (~8GB subset, ~6.7B tokens). Use 500M tokens for training. This is ~3x Chinchilla-optimal for a 117M model, ensuring the data-rich regime where training dynamics dominate.

### Compute
- Single A100-80GB: 117M model with 3 concurrent channel computations. Estimated: ~4-6 hours for 500M tokens (standard GPT-2 training baseline is ~5h on 1xA100 for similar corpus size). Channel overhead: +30-60% for the anti-Hebbian and trace computations. Total: ~8-10h on 1xA100. Cost: ~$12-18 on Lambda Cloud at $2/h for A100.
- Local GPU option (RTX 3090 / 4090): ~24h equivalent. Feasible as a local run.

### Pre-registered bands

**HARD-PASS (strong multi-channel benefit):**
- Multi-channel model final val perplexity <= 0.92 * single-channel baseline (at least 8% improvement)
- AND: multi-channel model representation diversity Tr(W_V) mean across layers >= 1.3 * baseline
- AND: multi-channel model negative-token rejection rate <= 0.8 * baseline at equivalent perplexity

**MIDDLE-BAND (partial benefit, warrants follow-up):**
- Multi-channel val perplexity in range (0.92, 1.02) * baseline
- Representation diversity improvement in range (1.0, 1.3) * baseline
- Negative rejection improvement > 0
- Overall: channels doing different things even if net perplexity gain is small

**HARD-FAIL (multi-channel adds nothing or hurts):**
- Multi-channel val perplexity >= 1.05 * single-channel baseline (5% worse)
- OR: Tr(W_V) diversity NOT improved over baseline despite trace monitoring channel
- OR: training instability (gradient explosion / NaN) in >20% of random seeds

**Highest-information cheapest probe (before full run):**
A 5M-token smoke test (15m on GPU) with batch_size=32, checking:
1. Do the three gradient channels have cosine similarity < 0.3 (orthogonal)? If cos_sim(g_1, g_2) > 0.7, channels are redundant and the multi-channel hypothesis is defeated before full training.
2. Does the trace channel fire at all (Tr(W_V) drop below threshold)? If never fires, the spectral monitoring channel is inert.
3. Is training stable (no NaN in 5k steps)?

This smoke takes ~20 minutes on a single A100 and costs < $1. It is the cheapest decisive test.

---

## Cross-Thread Synthesis

Today's prior drills (substrate as full training replacement, anti-Hebbian at LM scale, tier 1-to-5 integration) establish:
- Outer-product Hebbian CAN replace attention function at linear-attention expressivity level (P1 is viable)
- Anti-Hebbian at LM scale has ZERO published precedent (P7 is greenfield)
- Certified removal is well-developed in unlearning literature but never used online (P2 is ready for adaptation)
- ARMT / HMT show hierarchical recurrent retrieval is deployed at LLM scale (P9 has precedent)

The multi-channel angle is DISTINCT from the full-replacement angle: it does NOT require any primitive to replace gradient descent entirely. Instead, it AUGMENTS standard gradient descent with parallel signals from the primitive set. This is a lower-bar, higher-viability contribution path. P_deflated is higher (0.38) than full-replacement P_deflated (0.18).

Prior biological framing note (feedback_brain_inspired.md): neuromodulator analogs are durable. The DA/ACh/NE/5-HT/GABA mapping in Sub-Q 4 is grounded in peer-reviewed computational neuroscience (Schultz 1997; Yu-Dayan 2005; Cohen-Aston-Jones 2005; Namboodiri 2025) and provides a stable framing for external discussion and product communication.

---

## Falsifiable Predictions (HARD-PASS / HARD-FAIL)

**FP1 — Channel orthogonality:**
HARD-PASS: cos_sim(g_1=CE gradient, g_7=anti-Hebbian gradient) < 0.2 averaged across 100 training steps on GPT-2-small.
HARD-FAIL: cos_sim > 0.6 (channels are largely redundant).
P_deflated(HARD-PASS FP1) = 0.45. Rationale: CE and anti-Hebbian gradients act on different token positions — negatives are uniformly placed, not at error-prone positions — so natural orthogonality is expected. Deflated from P_raw=0.65.

**FP2 — Perplexity improvement:**
HARD-PASS: multi-channel val perplexity <= 0.92 * baseline at matched compute.
HARD-FAIL: val perplexity >= 1.05 * baseline.
P_deflated(perplexity HARD-PASS) = 0.30. Deflated from P_raw=0.50. MTL literature shows +2-8% on related tasks; degradation on unrelated tasks is also common. Middle-band is the most likely outcome.

**FP3 — Representation diversity:**
HARD-PASS: Tr(W_V) mean across all attention layers in multi-channel model >= 1.3 * baseline Tr(W_V).
HARD-FAIL: Tr(W_V) <= 1.05 * baseline.
P_deflated(diversity HARD-PASS) = 0.35. Deflated from P_raw=0.55.

**Joint probability (all three HARD-PASS):** 0.30 * 0.45 * 0.35 = 0.047. This is a paradigm-opening experiment, not a near-certain win. Most likely outcome: middle-band with at least one HARD-PASS condition met.

**P(at least middle-band outcome with useful empirical signal) = 0.68** (deflated from P_raw=0.85). The middle-band outcome is still scientifically load-bearing: demonstrating that channels are orthogonal and the trace monitor fires is sufficient to establish multi-channel framework as worth further investment.

---

## Substrate-Product Implications

Per [[feedback-no-papers-product-only]]:

**1. Multi-channel training as a product differentiator.** If a substrate-augmented LLM trained with P1+P2+P7+P4 shows verifiable representation diversity gains, this is directly product-marketable as "auditable training with erase, repulse, and coherence-monitor certificates." Maps directly to the Audit+Compliance killer feature (deletion certificate, compositionality audit API).

**2. Contrastive anti-Hebbian as "negative knowledge" feature.** A model trained with explicit P7 anti-Hebbian signals can provide a structural guarantee: "these N patterns were actively repulsed during training, not merely under-weighted." This is distinct from RLHF refusal fine-tuning (post-hoc) and provides a mechanistic certificate.

**3. Spectral monitoring as live drift detection.** P4 (trace estimator) run as an online training signal is exactly the "live drift detection" killer feature — if trace drops, the model is drifting toward collapse, and the trace channel auto-corrects. Direct product value for long-context continual learning.

**4. Biological framing as a durable product frame.** Having neuromodulator analogs for each primitive (DA -> P1, 5-HT -> P2, ACh -> P3, NE -> P4, BLA -> P6, GABA -> P7) allows the product to be framed accessibly to computational neuroscience and cognitive science audiences beyond standard ML engineers. Expands addressable audience.

---

## Citations (Verified Count: 14)

1. Schultz, W. et al. (1997). "A Neural Substrate of Prediction and Reward." Science 275:1593-1599.
2. Yu, A.J. & Dayan, P. (2005). "Uncertainty, Neuromodulation and Attention." Neuron 46:681-692.
3. Cohen, J.D. & Aston-Jones, G. (2005). Locus coeruleus-NE modulation of cortical gain.
4. Namboodiri, V.M.K. et al. (2025). "Accumbal acetylcholine signals associative salience during learning." PMC11741319.
5. Nair, A. et al. (2024). "Dopamine transients encode reward prediction errors independent of learning rates." Cell Reports. PMC11571066.
6. Hoffmann, J. et al. (2022). "Training Compute-Optimal Large Language Models." arXiv:2203.15556.
7. Kaplan, J. et al. (2020). "Scaling Laws for Neural Language Models." arXiv:2001.08361.
8. Li, M. et al. (2025). "How Instruction and Reasoning Data shape Post-Training." arXiv:2504.10766.
9. Radford, A. et al. (2021). "Learning Transferable Visual Models From Natural Language Supervision" (CLIP). OpenAI.
10. Guo, J. et al. (2024). "Multi-objective Reinforcement Learning from AI Feedback." arXiv:2406.07295.
11. Ramsauer, H. et al. (2021). "Hopfield Networks is All You Need." ICLR 2021.
12. Scellier, B. & Bengio, Y. (2017). "Equilibrium Propagation." Front. Comput. Neurosci.
13. Sardana, N. & Frankle, J. (2023). "Beyond Chinchilla-Optimal." arXiv:2401.00448.
14. Zhao, J. et al. (2024). "GaLore: Memory-Efficient LLM Training by Gradient Low-Rank Projection." arXiv:2402.05961.

---

## Next-Drill Candidates

1. **Three-factor Hebbian rules at transformer scale** — computational neuroscience literature (Gerstner et al.; Fremaux-Gerstner 2016) has fully specified multi-neuromodulator three-factor rules. Drill: can these be applied to transformer attention weights directly? What is the training stability analysis? Field=learning-rules, adjacent to modern-hopfield. Cost: 1 day theory.

2. **Free-probability spectral fingerprint as a live training monitor** — Voiculescu free-cumulants (kappa_n) for W_V matrices during training. Does the kappa_2 / kappa_3 trajectory differentiate high-quality from low-quality training data? Drill into arXiv:2502.18808 (optimal trace estimation) + Hutchinson variants. Advisor score: 5.5 (top ranked). Cost: 1 day theory + 30 min CPU.

3. **CHL / Equilibrium Propagation at GPT-2-small scale** — Scellier-Bengio 2017 provides the theoretical foundation for bipartite anti-Hebbian as a backprop complement. 2024 ICLR: scalable EP for deep ConvNets. Gap: no transformer language model results. Drill: theoretical barriers to EP-class training of decoder-only transformers? Field: adjacent to modern-hopfield + learning-rules. Cost: 2 days theory.

---

## P_deflated Summary

- P(multi-channel training outperforms single-loss on small transformer, any metric): 0.50 (novel-synthesis cap applied)
- P(channel orthogonality — P1 and P7 gradients cos_sim < 0.2): 0.45
- P(perplexity HARD-PASS at 8% improvement): 0.30
- P(representation diversity HARD-PASS): 0.35
- P(joint all-three HARD-PASS): 0.047
- P(at least middle-band outcome with useful empirical signal): 0.68

The middle-band outcome is the expected result and is still scientifically load-bearing.
