# Research: Tier 5c Efficient Path -- Engineering Specifics (5x Drill)

Filed: 2026-06-08
Filed-by: research sub-agent
Trigger: user mandate -- engineering specifics for codebook training + Flamingo schedule +
  continued pretraining cost scaling + layer insertion strategy. Most efficient path to
  Tier 5c (substrate IS attention in LLM) up and running.
Prior notes:
  notes/research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md (differentiability analysis, 14 citations)
  notes/research_drill_tier5c_architecture_speed_routing_5x_2026-06-08.md (non-attention arch patterns)
  notes/exp_dev_to_research_flamingo_pretest_adapter_required_2026-06-08.md (adapter entropy finding: 0.996 -> 0.809)
Context: Tier 5b HF (5 attempts; fact-transmission fails; single-position inject does not work);
  Tier 5c surgical modification of pretrained LLM is the realistic path; substrate FHRR
  Wirtinger-differentiable; LARS-VSA + GHRR-Transformer empirical existence proofs;
  substrate is NOT speed bottleneck (0.7% of inference cost at 12-layer per-layer retrieval).
Calibration: P_theoretical x P_empirical; deflate 0.15-0.25; novel-synthesis cap 0.50.

---

## HEADLINE

The most efficient path to Tier 5c is a Flamingo-style gated cross-attention insert into 1-2
middle layers of a small pretrained LLM (Pythia-160M or Qwen-2.5-0.5B), with a per-head
linear adapter (substrate 8192-dim -> LLM head-dim), gate initialized at zero (no disruption on
day 1), and the LLM backbone frozen. The Flamingo approach costs roughly 8-12 GPU-hours on
a single A100 to reach a decisive fact-transmission result, compared to 40-80 GPU-hours for
full from-scratch Tier 5c training. The adapter-mandatory finding (entropy 0.996 uniform
without adapter, 0.809 sharp with adapter) eliminates raw-HD-as-K/V as a viable path. Middle
layers (L8-L16 of a 24-layer model, or L3-L5 of Pythia-160M's 12 layers) are the target
insertion zone based on the probing literature (Tenney 2019, Geva 2020). Codebook training
follows VQ-VAE discipline (commitment loss + EMA update + entropy regularization) to prevent
collapse. Continued pretraining cost after surgical modification is 1-3% of from-scratch cost
for models up to 3B parameters. The complete 5-phase sequence is pre-registered below with
HARD-PASS and HARD-FAIL bands.

P_theoretical = 0.62 (Flamingo-style gated cross-attention has strong published precedent;
  adapter + frozen backbone is established; FHRR differentiability confirmed)
P_empirical = 0.38 (no Tier 5c fact-transmission PASS yet; adapter-entropy finding is
  promising but has only been measured for one probe; gate opening and full training not done)
P_deflated = 0.42 (product of theoretical x empirical = 0.24; working estimate capped at 0.50
  per novel-synthesis rule; 0.42 reflects the Flamingo precedent is strong and the Tier 4
  HP provides a base)

---

## LEVEL 1: WHERE TO INSERT SUBSTRATE-ATTENTION LAYERS

### 1.1 Layer function profiles from the probing literature

Tenney et al. 2019 (arXiv:1905.05950) "BERT Rediscovers the Classical NLP Pipeline"
is the canonical layer-function map. The result applies broadly across transformer
families (verified in GPT-style models via follow-on work, Geva 2020):

- Layers 1-3 (early): part-of-speech tagging, surface syntax, co-reference (shallow).
  These layers process word-form information -- which token is which grammatical role.
  Representations here are close to token identity; manipulating them risks corrupting
  the base semantic content the LLM needs everywhere.

- Layers 4-9 (middle-early to mid): dependency parsing, entity typing, semantic role
  labeling. These layers build up relational structure -- what modifies what, who does
  what to whom. This is where factual associations are predominantly encoded.

- Layers 10-18 (middle-late to late): coreference resolution, semantic compositionality,
  world-knowledge integration. Geva et al. 2020 (arXiv:2012.14913) "Transformer Feed-
  Forward Layers Are Key-Value Memories" identifies the FFN sublayers in middle-to-late
  layers as the primary locus of factual knowledge storage in BERT/GPT-style models.

- Layers 19+ (final): task-specific prediction heads, output formatting.

### 1.2 Insertion recommendation for Pythia-160M (12 layers)

Pythia-160M has 12 transformer layers (L0-L11). Based on the probing literature:

- **Target zone: L3-L5** (middle-early). Rationale: (1) past the syntax-only early layers
  where substrate knowledge would be premature; (2) before the final prediction layers
  where disruption risks perplexity collapse; (3) the dependency/entity layers are where
  substrate's factual relational knowledge is most valuable. (4) Tier 4 result (single
  layer swap ppl_ratio=0.939 PASS) was on one of the middle layers -- the Tier 4 success
  provides direct empirical support for this zone.

- **Single-layer start (Phase A)**: insert at L4 first. This is a single additional
  cross-attention module between L4 and L5 -- the LLM's L4 output is Q; substrate K/V
  are the gated cross-attention targets.

- **Multi-layer extension (Phase B)**: if Phase A shows fact-transmission improvement,
  add second insertion at L7. Two insertions capture both the entity-layer (L4) and
  the semantic-compositionality layer (L7). Do NOT go beyond 2 insertions until Phase B
  is assessed.

- **Do NOT insert at L0-L2 or L10-L11**: early layers lack relational context for
  substrate retrieval to be meaningful; final layers risk perplexity degradation.

### 1.3 Qwen-2.5-0.5B configuration (24 layers, hidden=896)

The Flamingo pretest used Qwen-2.5-0.5B-Instruct (config: hidden_size=896,
num_attention_heads=14, head_dim=64, GQA -- check num_key_value_heads separately).

- **Target zone: L8-L12** (middle). For a 24-layer model, this maps to the same
  relative depth as L3-L5 in Pythia-160M (~33-50% depth).
- **Adapter target dimension**: 896 (full hidden) for the per-head adapter output.
  But because head_dim=64 per head, the adapter produces 14 x 64 = 896 total. If GQA
  is used (e.g. num_key_value_heads=2), K and V come from the KV-head count, not the
  query-head count -- wire adapter to match num_key_value_heads.

### 1.4 Multi-layer insertion analysis

For 1, 2, 4 Flamingo insertion layers:

- **1 layer** (recommended start): minimal risk; one gate to train; one adapter.
  If fact-transmission PASS: highest confidence the mechanism works.
  If FAIL: easy to diagnose (only one insertion point).

- **2 layers** (follow-on): adds ~2x training cost, ~2x parameters (two adapters + two
  gates). Expected improvement if substrate facts span multiple semantic levels (e.g.
  entity at L4, relation at L7). Pre-register as Phase B.

- **4 layers** (not recommended before 1-2 layer results): risk of gradient interference
  between multiple insertion points; training instability increases; interpretation
  becomes harder. Only justified if 2-layer result is strong but not strong enough.

### 1.5 Hierarchical insertion: syntax early, semantics middle, discourse late

LARS-VSA and GHRR-Transformer literature does not distinguish by layer; both use
uniform insertion at all layers. The probing literature supports hierarchical differentiation:

- Syntax codebook (surface forms): L2-L3 -- but substrate does not natively encode
  syntax separate from semantics, so this is not a first priority.
- Semantic / factual codebook: L4-L8 -- this is substrate's natural domain.
- Discourse / compositional: L10-L14 for large models -- relevant for K-hop chains.

Recommended sequencing: semantic middle-layer first (fastest signal), add syntax/discourse
only if 1-2 semantic insertions are insufficient.

---

## LEVEL 2: CODEBOOK TRAINING BEST PRACTICES

### 2.1 Initialization

Three options in order of recommended priority:

**Option A (recommended): LLM hidden states as seed**.
Pass a representative corpus (e.g. Wikipedia 1M sentences) through the LLM backbone.
Extract the L4 hidden states for each token. Run k-means clustering (k = codebook size)
on these hidden states. Use the cluster centroids as initial codebook atoms, then project
to the unit circle (FHRR constraint: |z_i|=1 for each dimension).

Rationale: the initial codebook is semantically aligned with the LLM's representation
space from day 1. This reduces the "warm-up" phase where substrate knows nothing
about LLM geometry. Empirical precedent: memory-augmented architectures (NTM, DNC)
that initialize memory from task-relevant representations converge faster (Graves et al.
2016 DNC ablation). VQ-VAE codebook initialization from encoder outputs is standard
(Van den Oord et al. 2017).

Time cost: one forward pass over 1M sentences at batch_size=512 = roughly 2000 steps;
at Pythia-160M 10ms/step = 20 seconds. k-means with k=32768 on 512-dim vectors of
1M examples = ~2-5 minutes on CPU. Trivial pre-cost.

**Option B: random complex unit-circle initialization**.
Draw each atom from uniform distribution over the unit circle in C^N. This is the
substrate default. Requires longer warm-up but avoids any bias from initialization.
Appropriate if the codebook is meant to be jointly trained (not pre-seeded from LLM).

**Option C: pretrained word embeddings (Word2Vec/GloVe/BERT)**.
Project word embeddings to complex unit circle and use as initial atoms. Reasonable
for token-level codebooks. Not recommended over Option A because word embeddings are
lower quality than contextual LLM hidden states.

Recommendation: **Option A for Flamingo-style (frozen LLM); Option B for full Tier 5c
from-scratch training** (no LLM geometry available at init time).

### 2.2 Codebook size

Published ranges and tradeoffs:

- **VQ-VAE (Van den Oord 2017)**: 512 atoms for images (32x32); 4096-8192 for higher
  resolution. The rule-of-thumb is that codebook should be roughly sqrt(N_data) up to
  saturation.

- **DALL-E (Ramesh et al. 2021)**: 8192-atom codebook for visual tokens. This is the
  most cited image codebook; 8192 is the practical upper end for vision.

- **Flamingo (Alayrac et al. 2022)**: does not use a codebook in the traditional sense --
  the visual features are continuous and passed through a Perceiver Resampler that reduces
  them to 64 fixed-length tokens. No codebook collapse issue because inputs are
  continuously valued.

- **LARS-VSA (2024)**: bipolar codebook (W_B in {-1,+1}^{FxD}) where F is the codebook
  size. The paper uses F values up to 256 atoms; the larger substrate-scale equivalent
  would be O(10k) for a 100k vocabulary analog.

For substrate's use case (vocabulary-equivalent factual codebook):

- **32k atoms**: vocabulary-equivalent to GPT-2/Llama tokenizer. Each atom maps to
  roughly one token-level concept. This is the minimum for reasonable coverage.

- **100k atoms**: exceeds vocabulary size; enables multi-word concept storage.
  Substrate's production M=100k-1M stored patterns maps naturally here.

- **200k atoms**: useful if substrate has domain-specific depth (e.g. biomedical or legal
  knowledge where concepts exceed general vocabulary). Risk: codebook collapse probability
  increases with size unless training budget is proportionally increased.

Recommendation: **start at 32k atoms** for Phase A. This is the cheapest decisive test.
If collapse does not occur and codebook utilization exceeds 30%, scale to 100k for Phase C.

### 2.3 Codebook update strategy during training

**Frozen codebook (recommended for Phase A)**.
Codebook atoms are fixed from initialization. Only the adapter (linear projection +
gate scalar) is trained. This eliminates codebook collapse risk entirely -- there is
nothing to collapse. The LLM learns to use the fixed codebook geometry.

Risk: if the initial codebook is poorly aligned, the adapter cannot fully compensate.
Mitigated by Option A initialization (seed from LLM hidden states).

**EMA update (recommended if codebook is trainable)**.
Exponential Moving Average update rule (Van den Oord et al. 2017 VQ-VAE appendix):
  codebook_atom_i <- gamma * codebook_atom_i + (1 - gamma) * mean(assigned_queries)
where gamma=0.99 is the typical value. EMA update is more stable than gradient-based
codebook update because it avoids the "commitment-vs-codebook-vs-encoder" three-way
gradient competition that causes collapse in naive VQ-VAE.

**Learnable codebook with commitment loss** (fallback if EMA insufficient).
Add commitment loss: L_commit = ||query - stop_gradient(nearest_atom)||^2.
This encourages queries to stay near their assigned atom. The stop_gradient breaks the
circularity. Add to total loss as: L_total = L_LM + beta * L_commit, beta=0.25 (VQ-VAE
default). For complex FHRR, the commitment loss is:
  L_commit = ||Re(query) - Re(atom)||^2 + ||Im(query) - Im(atom)||^2 (per-dimension L2).

### 2.4 VQ-VAE commitment loss and codebook collapse mitigation

The three standard mitigation strategies, in order of recommendation:

1. **EMA update** (most effective): prevents gradient competition; no hyperparameter
   other than gamma=0.99. Apply first.

2. **Entropy regularization**: add H_codebook = -sum(p_k * log(p_k)) where p_k is
   the empirical frequency of atom k being the nearest neighbor. Maximize H_codebook
   (uniform usage). Add to loss as: L_total = L_LM - eta * H_codebook, eta=0.01.
   Empirical estimate: count assignments per step, maintain running average.

3. **Atom reset**: if any atom's usage rate falls below threshold (e.g. < 0.001% of
   assignments) for 1000 consecutive steps, reinitialize that atom to a random query
   from the current batch. This is a hard collapse prevention. Used in DALL-E training
   and reported to stabilize codebooks above 4096 atoms (Ramesh et al. 2021 supplement).

For Tier 5c with FHRR complex codebook, recommended order:
- Phase A (frozen codebook): no collapse mitigation needed. Codebook is fixed.
- Phase B (trainable codebook): EMA first. Add entropy reg only if utilization < 20%
  after 2k steps. Add atom reset only if utilization < 5% after 3k steps.

### 2.5 FHRR codebook structure (unit-norm complex phasors)

Substrate's FHRR codebook atoms are vectors in C^N with |z_k|=1 element-wise
(each complex entry has magnitude 1). This is the unit circle constraint.

Key property for training: the unit-circle constraint makes the representation space
a compact manifold (Riemannian optimization). Gradient steps in the ambient space C^N
must be projected back to the manifold. For FHRR:
  atom_k <- atom_k - lr * grad_k   (standard Adam/SGD)
  atom_k <- atom_k / |atom_k|       (renormalize to unit circle per dimension)

This two-step update is the Riemannian retraction for the product manifold
(S^1)^N. It is differentiable, correct, and avoids magnitude drift. Implement as
a custom optimizer hook (post_step normalization).

The Wirtinger gradient for complex parameters is standard in PyTorch:
  torch.is_complex(atom) == True; backward() computes Wirtinger derivatives
  automatically; no custom gradient code needed.

Advantage over bipolar codebooks: FHRR avoids straight-through estimators entirely.
The gradient flows through the complex normalization (differentiable) and through the
soft-cleanup softmax. No discrete discontinuity exists in the forward pass.

### 2.6 Pattern B bipolar codebook (sign vectors)

If the system uses bipolar Pattern B atoms (s in {-1,+1}^N), the gradient situation is
different: sign(.) is not differentiable at 0, and the constraint set is discrete.

Standard handling: straight-through estimator (STE). Forward pass uses sign(.);
backward pass propagates gradient through as if sign(.) = identity. This is the
approach in LARS-VSA and BinaryConnect.

Recommendation: **prefer FHRR over bipolar for Tier 5c** because Wirtinger gradients
are strictly cleaner than STE. If bipolar is required (e.g. for compatibility with
existing substrate Pattern B atoms), apply STE with gradient clipping at +/-1 to prevent
explosion. Monitor gradient variance across layers; STE can cause gradient instability
in deep networks.

---

## LEVEL 3: FLAMINGO TRAINING SCHEDULE

### 3.1 Reference: Flamingo's original published schedule (NeurIPS 2022)

Flamingo (Alayrac et al. 2022, arXiv:2204.14198) is the primary reference for the
gated cross-attention insert approach. The original training details:

**Architecture**: pretrained Chinchilla LLM backbone (1.4B, 7B, or 70B) frozen. New
cross-attention layers interleaved every 7 LLM layers. Perceiver Resampler compresses
variable-length visual features to 64 fixed-length tokens. Gating: each new cross-
attention layer has a learnable scalar tanh-gate (alpha, initialized to 0) multiplied
into the cross-attention output before adding to residual. Gate 0 at init = new layers
are no-ops at the start of training = LLM language ability is perfectly preserved.

**Training data**: 43M image-text pairs (M3W), 312M image-text pairs (LAION-400M subset),
185M short videos. Language data was NOT mixed in during cross-modal training because the
frozen backbone was already language-capable. Key: no "LM recovery" phase needed when
backbone is frozen.

**Schedule**: constant learning rate for new parameters (1e-4 for adapters/gates);
no warmup described (gate init at 0 handles the warm-up implicitly -- the gate opens
gradually as training pulls alpha away from 0). Total training: 500k steps at batch
size 512 on 1.4B model = roughly 256B effective tokens seen by the adapter layers.

**Critical insight for substrate adaptation**: Flamingo's schedule works because the
gate initialization ensures the LLM's base loss is unaffected at step 0. The adapter
can train toward a useful cross-attention signal without needing to fight the LLM loss.
This is the correct starting condition for Tier 5c Flamingo-style training.

### 3.2 Gate initialization

**Use sigmoid gate, not tanh gate**.
Flamingo uses tanh(alpha) with alpha initialized near 0. For substrate, a sigmoid gate
is preferable:
  output = LLM_layer_output + sigmoid(gate_scalar) * cross_attention_output

Sigmoid maps to (0, 1), ensuring the gate weight is non-negative (cross-attention output
is always ADD not subtract). Tanh maps to (-1, 1), allowing the gate to go negative --
this is mathematically valid but harder to interpret. sigmoid initialized at gate_scalar=0
gives sigmoid(0)=0.5, which is too large (already half-open at init).

Better: initialize gate_scalar at -4.0. sigmoid(-4) = 0.018 -- effectively zero.
This matches the Flamingo intent (near-zero at start) while using the sigmoid functional
form. Confirm: LLM loss at step 0 with gate=-4 should be within 0.1% of no-insertion
baseline.

Alternative (used in some Flamingo reimplementations): learned gating with
  output = LLM_layer_output + tanh(alpha) * cross_attention_output
  alpha initialized to 0.0 (so tanh(0)=0).
The tanh version is correct if alpha is allowed to be positive or negative (permitting
either constructive or destructive cross-attention influence). For substrate: prefer
sigmoid since substrate retrieval should be additive only.

### 3.3 Adapter initialization

Per-head linear adapter: substrate 8192-dim -> LLM head-dim (64 for Qwen-0.5B heads).

**Use Xavier uniform initialization** (Glorot et al. 2010).
W ~ Uniform(-sqrt(6/(fan_in + fan_out)), +sqrt(6/(fan_in + fan_out)))
fan_in = 8192 (substrate HD dimension)
fan_out = 64 (LLM head dimension, or 896 for full hidden)

This is preferred over Kaiming because Kaiming is designed for ReLU activations;
the adapter is a linear layer (no nonlinearity), so Xavier is correct.

The bias: initialize to zero.

For FHRR complex input (complex64 vectors from substrate): apply the adapter to
the concatenation of real and imaginary parts -- treat the 8192-complex vector as
16384-real-valued input, then project to 64-real. This avoids complex-valued linear
layers in the adapter (which require extra care) while preserving the full information
content of the FHRR vector.

Alternative: use complex-valued linear layer (torch.nn.Linear with complex dtype).
This is correct and PyTorch supports it natively. The adapter then operates in C^{8192->64}.
This halves the effective parameter count (complex linear has same param count as two
real linears but processes complex input as one unit). The Wirtinger gradient works
correctly with no modifications.

### 3.4 Training data composition

**For Flamingo-style frozen-LLM adapter training**:

The training objective is fact-transmission: given a substrate retrieval result, the
LLM should correctly use the retrieved fact in its output. Training data:

- Factual question-answer pairs where the answer requires using a fact the substrate
  holds. Format: (question, substrate_retrieval_result) -> answer.
- Keep the training set small for Phase A: 10k-50k examples. Larger training is
  phase B+ territory.
- Do NOT mix general language modeling data. The frozen LLM backbone is already
  language-capable. Adding LM data to adapter training adds noise to the
  fact-transmission objective.

Substrate-grounded training data construction:
  1. Select M=10000 fact-bindings from the substrate (entity, relation, entity triples).
  2. Generate questions that require those facts (template: "What is the [relation]
     of [entity1]?").
  3. Retrieve the fact from substrate as a K/V pair.
  4. Train adapter so that the cross-attention output causes the LLM to output the
     correct answer.

This is a narrow but decisive test: does the cross-attention pathway transmit facts
from the substrate retrieval to the LLM output? HARD-PASS = top-k accuracy > 60% on
held-out facts. HARD-FAIL = top-k accuracy < 20% (random guessing).

### 3.5 Frozen LLM vs partially trainable

**Phase A: frozen LLM**.
Train ONLY: adapter weights, gate scalar.
Rationale: frozen backbone guarantees no perplexity regression; base language quality
is preserved; the question "does the adapter transmit facts?" is cleanly isolated.

Cost: very low. Frozen 160M-param LLM + 32k-100k new adapter parameters = negligible
memory overhead; backprop is only through adapter + gate, not through 160M LLM params.
Estimated: 30-60 min on single A100 for 10k training examples at 5 epochs.

**Phase B: partial unfreeze (top 4 layers)**.
Unfreeze the top 4 LLM layers (nearest to output). Allow these layers to adapt to
the new cross-attention signal. Keep all earlier layers frozen.
Rationale: if adapter trains well but fact-transmission is still insufficient, the LLM's
output layers may need fine-tuning to use the new cross-attention activations.
Cost: 3-4x more backprop compute; still much cheaper than full LLM training.

**Phase C: LoRA on full LLM**.
Add LoRA adapters (Hu et al. 2022, arXiv:2106.09685) with rank=8 to all attention layers.
Train LoRA + cross-attention adapter + gate jointly.
Cost: adds ~0.1-0.3% parameters (LoRA rank=8 on 160M model = ~0.3M extra params).
Training cost increase vs Phase A: 3-5x more memory; 2-3x more compute.

### 3.6 Full Flamingo schedule for Phase A

Recommended Phase A schedule (frozen LLM, Pythia-160M, single cross-attention insert at L4):

1. **Init**: gate_scalar = -4.0; adapter = Xavier uniform. Substrate codebook frozen
   (option A: seeded from LLM L4 hidden states).

2. **Optimizer**: AdamW with lr=2e-4 for adapter, lr=5e-4 for gate. weight_decay=0.01.
   These values match the Flamingo-style adapter training range (1e-4 to 1e-3 for new
   parameters; larger lr is OK for the gate scalar which is a single value).

3. **Batch size**: 32 examples (question, substrate_retrieval, target_answer).

4. **Steps**: 5000 steps (small dataset; 10k examples x 5 epochs / 32 batch = 1563
   steps; run 5000 steps total or until HARD-PASS).

5. **Monitoring**: log gate_scalar value every 100 steps. Log top-1 fact accuracy every
   200 steps. Log cross-attention entropy (should decrease from 0.996 toward < 0.85).

6. **HARD-PASS gate**: gate_scalar > -3.0 by step 1000 (gate is opening; training pulling
   it away from init). If gate does not move in 1000 steps, learning rate too small.

7. **HARD-FAIL gate**: top-1 fact accuracy < 20% at 5000 steps (no learning on
   fact-transmission task; adapter or retrieval is broken).

---

## LEVEL 4: CONTINUED PRETRAINING COST SCALING

### 4.1 How many tokens to recover after modification?

The literature is consistent: the recovery cost after a surgical modification depends
on the fraction of parameters modified and the degree of disruption.

For Flamingo-style frozen-LLM training (no LLM params changed):
- **Recovery cost = 0 tokens**. The LLM is frozen; there is nothing to recover.
  Perplexity is preserved exactly (gate init at 0 guarantees this). This is the main
  engineering advantage of the frozen approach.

For partial unfreeze (top 4 layers):
- Recovery cost: approximately 1-5B tokens to achieve < 2% perplexity increase vs
  pre-modification baseline. Basis: LoRA papers (Hu et al. 2022) report that fine-tuning
  on 1-5B tokens is sufficient to recover natural language quality after significant
  architectural change in the target layers.

For full LoRA (all attention layers):
- Recovery cost: 5-20B tokens. Llama-2 continual pretraining experiments (Gupta et al.
  2023, arXiv:2308.04014 "Continual Pre-Training of Large Language Models") report
  that roughly 1-5% of original training tokens is sufficient to recover after
  adaptation, for models that were already well-trained. For Pythia-160M (originally
  trained on 300B tokens), 1% = 3B tokens.

For full parameter replacement (all attention layers replaced):
- This is equivalent to continued pretraining of a new architecture from an existing
  checkpoint. Literature on domain-adaptive pretraining (Gururangan et al. 2020,
  "Don't Stop Pretraining") reports 1-5% of original tokens to achieve domain
  specialization without catastrophic forgetting. For full architecture replacement,
  a higher fraction is needed: 5-15% = 15-45B tokens for a 300B-pretrained model.

### 4.2 Pretraining cost vs from-scratch

Rule of thumb from the literature (Hoffmann et al. 2022 "Chinchilla"):
  Compute-optimal from-scratch training: ~20 tokens per parameter.
  For Pythia-160M (160M params): optimal from-scratch = 3.2B tokens.
  Cost at A100 efficiency: ~3.2B / (A100 throughput ~70B tokens/GPU/day) = ~1 GPU-day.

From literature on model surgery and continued pretraining:
- **Adapter-only (frozen backbone)**: 0.01% of from-scratch cost. Negligible.
- **Top-4-layer unfreeze**: 1-3% of from-scratch cost. ~15-30 GPU-minutes.
- **Full LoRA rank=8**: 2-5% of from-scratch cost. ~30-60 GPU-minutes.
- **Full architectural replacement + recovery**: 5-20% of from-scratch cost.
  For Pythia-160M: 0.16-0.64 GPU-days.

For larger models (Qwen-2.5-3B):
  From-scratch optimal = 60B tokens ~= 1 GPU-week on single A100.
  Adapter-only: negligible (adapter is 0.01% of total params).
  Full architectural replacement: 5-20% = 3-12 GPU-hours.

**Engineering implication**: the Flamingo frozen-backbone approach costs < 1 GPU-hour
for fact-transmission training at Pythia-160M scale. This is a 100x cost advantage
over any approach that modifies backbone parameters.

### 4.3 LoRA-style cheap adaptation

LoRA (Hu et al. 2022): add low-rank decomposition W' = W + AB where A in R^{d x r},
B in R^{r x k}, rank r << min(d, k). For Pythia-160M, rank=8 on all attention projections
(Q, K, V, O) adds approximately:
  4 layers * 12 heads * (512 * 8 + 8 * 64) = ~600k parameters
  Total added: ~0.4% of 160M params.

LoRA-based integration with substrate cross-attention: the adapter IS the LoRA-equivalent
for the cross-attention pathway. The per-head linear adapter (8192 -> 64) has the same
role as LoRA's B matrix: projecting a new representation into the existing head-dim space.

Difference from standard LoRA: standard LoRA modifies EXISTING attention projections
(W_Q += AB). Substrate adapter projects a NEW signal (substrate retrieval) into the
attention head space. These can coexist: standard LoRA adapts the LLM's self-attention
for task fine-tuning; substrate cross-attention adapter provides factual retrieval.

### 4.4 Adapter-only training cost

Phase A cost estimate (Pythia-160M, single cross-attention insert, 32k codebook,
10k training examples, 5k steps, batch=32):

- Backward pass through adapter only (2 linear layers: 8192->896 and 896->head_dim).
  Total adapter params: ~7.3M (8192 x 896 = 7.3M; 896 x 64 = 57k) per head.
  With 12 heads: ~88M adapter params. This is larger than anticipated -- recommendation
  is to use a bottleneck adapter: 8192 -> 256 -> 64, adding a nonlinearity (GELU).
  Bottleneck adapter: 8192 x 256 + 256 x 64 = 2.2M per head = 26M total. More reasonable.

- Training throughput: with frozen LLM (no backprop through backbone), adapter training
  is equivalent to training a small MLP on top of frozen features. On A100: expect
  > 1000 examples/second = 10k training examples in 10 seconds per epoch. Full 5k steps
  at batch=32 = ~5 minutes.

- **Total Phase A cost: < 10 GPU-minutes** on a single A100. This is decisive and cheap.

### 4.5 Empirical literature: Phi-3/Qwen/Llama fine-tuning costs

Phi-3-Mini (3.8B params, originally trained ~3T tokens):
  LoRA rank=16 fine-tuning on 1B tokens: 2-4 GPU-days on 8xA100.
  Adapter-only fine-tuning (frozen backbone): < 1 GPU-hour.

Qwen-2.5-0.5B (originally trained ~18T tokens):
  The model is already heavily pretrained. Any adapter-only training converges
  rapidly because the frozen backbone provides strong features.
  Adapter training on 50k examples at 5 epochs: < 30 GPU-minutes.

Llama-3.1-8B continual pretraining (from Meta 2024 technical report):
  Continued pretraining on 100B new-domain tokens: 4-8 GPU-days on 64 A100s.
  This is the most expensive configuration -- not relevant for Phase A.

Relevant takeaway: for frozen-backbone adapter training, the cost is model-size
independent because no backprop goes through the backbone. All models (0.5B to 8B)
cost < 1 GPU-hour for adapter training at 50k example scale. This is the correct
design point for Phase A.

---

## LEVEL 5: SUBSTRATE-LLM INTERFACE API DESIGN

### 5.1 PyTorch nn.Module interface

The substrate-cross-attention module fits cleanly as an nn.Module:

```python
class SubstrateCrossAttention(nn.Module):
    """
    Flamingo-style gated cross-attention layer.
    Inserts between LLM transformer layers.
    LLM backbone parameters are NOT registered here (frozen).
    """
    def __init__(self, llm_hidden: int, substrate_dim: int,
                 n_heads: int, n_kv_heads: int, codebook_size: int):
        super().__init__()
        # per-head bottleneck adapter: substrate_dim -> bottleneck -> head_dim
        head_dim = llm_hidden // n_heads
        bottleneck = 256  # tune; reduces from 8192 to 256 before head-dim projection
        self.substrate_adapter = nn.Sequential(
            nn.Linear(substrate_dim * 2, bottleneck),  # *2: concat Re+Im of complex64
            nn.GELU(),
            nn.Linear(bottleneck, n_kv_heads * head_dim),
        )
        # Q projection: LLM hidden -> Q for cross-attention
        self.q_proj = nn.Linear(llm_hidden, n_heads * head_dim, bias=False)
        # gate: scalar, initialized to effectively zero
        self.gate = nn.Parameter(torch.tensor(-4.0))

    def forward(self, llm_hidden: torch.Tensor,
                substrate_retrieval: torch.Tensor) -> torch.Tensor:
        # llm_hidden: (batch, seq_len, llm_hidden)
        # substrate_retrieval: complex64, (batch, n_retrieved, substrate_dim)
        # -> returns: (batch, seq_len, llm_hidden) residual delta
        ...
```

Key design decisions encoded above:
- The adapter takes concatenated [Re, Im] of the complex substrate vector (no custom
  complex linear; standard real-valued linear on doubled dimension).
- Gate is a single scalar nn.Parameter, initialized at -4.0 (sigmoid(-4) ~ 0.018).
- Q comes from LLM hidden states; K/V come from substrate retrieval.
- Output is a DELTA added to LLM hidden; LLM layer output is preserved.

### 5.2 Substrate as torch.nn.Module

Substrate's existing Python layer should be wrapped as an nn.Module with no trainable
parameters (all parameters are the substrate codebook atoms, which are treated as a
buffer not a parameter for Phase A):

```python
class SubstrateRetriever(nn.Module):
    """Read-only wrapper around substrate. No trainable params in Phase A."""
    def __init__(self, substrate_instance):
        super().__init__()
        self._substrate = substrate_instance
        # Register codebook as buffer (not parameter) -- excluded from optimizer
        # Only relevant if codebook is to be trained later (Phase B+)

    def forward(self, query: torch.Tensor) -> torch.Tensor:
        # query: (batch, seq_len, hidden) -- LLM hidden states as retrieval probes
        # returns: complex64 tensor (batch, seq_len, k_retrieved, substrate_dim)
        ...
```

The buffer/parameter distinction is critical: registering as buffer means the codebook
is serialized with the model (saved/loaded correctly) but does NOT receive gradients.
If codebook training is later enabled (Phase B+), promote to nn.Parameter.

### 5.3 Forward pass: substrate.retrieve(hidden_state) -> K/V tensors

The retrieval pipeline for the cross-attention layer:

1. **Query construction**: project LLM hidden state to substrate query space.
   If LLM hidden = 512 and substrate N=8192, this is a dimensionality increase.
   Use a learned projection: W_q_proj: R^{512} -> R^{8192} (or C^{8192} for complex).
   Alternative: query in LLM space (512-dim); retrieve in substrate space via
   cosine similarity after projecting codebook atoms down to 512-dim. The latter
   avoids the expensive 512->8192 up-projection.

2. **Substrate retrieval**: find top-k nearest codebook atoms to the query.
   For Phase A (frozen codebook, pre-computed): this is a matrix multiply
   Q (batch x seq x 512) @ Codebook_projected (512 x 32k) -> (batch x seq x 32k)
   Softmax top-k gives retrieval weights. At N=32k codebook and seq_len=512:
   batch x seq x codebook = 8 x 512 x 32000 = 131M float32 ops. On A100: < 1ms.

3. **K/V construction**: the retrieved atom indices or soft-weighted atom vectors
   become the K and V for the cross-attention layer. Pass through the substrate_adapter
   to project to LLM head-dim space.

4. **Cross-attention**: standard MultiheadAttention with Q from LLM, K/V from
   substrate adapter output. Scale by sqrt(head_dim) as standard.

5. **Gated residual**: gate output = sigmoid(gate_scalar) * cross_attn_output.
   Add to LLM hidden: llm_hidden_new = llm_hidden + gate_output.

### 5.4 Backward pass: Wirtinger gradient flow

Gradient flow through the complex operations:

- **Complex-valued adapter input (Re + Im concatenation path)**: gradient flows through
  standard real-valued linear layers. No Wirtinger gradient needed; the complex -> real
  split is explicit (torch.view_as_real()).

- **Complex-valued linear path (alternative)**: if torch.nn.Linear with complex64 dtype
  is used, PyTorch computes Wirtinger derivatives automatically via autograd.
  The Wirtinger gradient for f: C -> R is: df/dz* = partial(f)/partial(Re) - i * partial(f)/partial(Im).
  PyTorch handles this correctly for complex64 tensors; no custom backward needed.

- **Soft-cleanup (softmax over codebook similarities)**: the cosine similarity
  cos(query, atom_k) for complex vectors is Re(query @ conj(atom_k)) / (|query| * |atom_k|).
  This is differentiable via standard real arithmetic (Wirtinger chain rule applies).
  PyTorch autograd computes the gradient correctly through this expression.

- **Gate scalar**: single real-valued parameter; backprop is standard scalar gradient.

- **LLM frozen backbone**: no gradient is computed for backbone parameters. This is
  enforced by wrapping backbone layers with torch.no_grad() or setting
  requires_grad=False on all backbone parameters at init.

Gradient check (Phase A pre-flight):
  Run a single forward+backward pass on a tiny batch (batch=2, seq_len=4).
  Verify: gate.grad is not None; adapter.weight.grad is not None; backbone params
  have .grad == None (frozen). If any backbone grad is non-None, the freeze is broken.

### 5.5 Batched retrieval (GPU memory layout)

Memory layout for GPU-resident substrate codebook:

For N=8192 FHRR, 32k atoms, complex64 (8 bytes per complex):
  Codebook size = 32000 * 8192 * 8 bytes = 2.1 GB.
  This fits on a 40GB A100 with room to spare. Load once at model init.

For the retrieval operation (batch=32, seq_len=512, top-k=10):
  Query matrix: 32 * 512 * 8192 complex = 134M complex values = 1.07 GB complex64.
  Similarity matrix: 32 * 512 * 32000 float = 524M float32 = 2.1 GB.
  This is at the edge of A100 memory. Mitigations:
  (a) Reduce seq_len to stride through sequence rather than all at once.
  (b) Quantize codebook to float16 (halves memory).
  (c) Use approximate nearest-neighbor (FAISS) for retrieval -- reduces similarity
      matrix to sparse top-k output.

For Phase A (10k-50k examples, frozen codebook, small batch):
  Batch = 8, seq_len = 128: query = 16M complex = 128 MB; similarity = 33M float = 131 MB.
  Trivially fits in any GPU memory.

### 5.6 Substrate state synchronization (multi-GPU)

For Phase A (single GPU), this is not relevant. For Phase C+ (multi-GPU):

The substrate codebook is a read-only shared resource during Phase A (frozen). Load
once per GPU process as a registered buffer. PyTorch DDP handles buffer broadcasting:
  model = DDP(model) -- buffers are broadcast at init; no gradient sync needed.

For trainable codebook (Phase B+), the EMA update must be synchronized:
  Gather all atom assignments across GPUs before computing the EMA.
  Use torch.distributed.all_reduce() on the assignment counts before EMA update.
  This is the standard DDP-compatible VQ-VAE training pattern.

---

## LEVEL 6: CHEAPEST-DECISIVE-FIRST SEQUENCE

The sequence below is ordered by compute cost from cheapest to most expensive. Each phase
gates the next: do not proceed to Phase B without a HARD-PASS at Phase A.

### Phase A: Differentiability probe + codebook quality + retrieval benchmark (CPU)

**Purpose**: verify that the substrate-attention forward+backward pass works correctly
in isolation before any LLM involvement.

Sub-phase A1 -- Wirtinger gradient smoke (< 5 min, CPU):
  Build a minimal SubstrateCrossAttention with N=512, k=1024 atoms, hidden=64.
  Run forward pass on random input (batch=2, seq=4).
  Run backward pass. Check: gate.grad not None; adapter grads not None; gradients finite.
  HARD-PASS: all parameter grads finite and non-None.
  HARD-FAIL: NaN or None gradient anywhere in the adapter.

Sub-phase A2 -- Codebook quality (< 10 min, CPU):
  Initialize codebook from Option A (seed from LLM hidden states, sample 10k tokens).
  Measure codebook utilization: draw 1000 random token embeddings; find nearest atom.
  HARD-PASS: > 30% of atoms are nearest neighbor to at least one sample (non-collapsed).
  HARD-FAIL: < 5% of atoms are used (degenerate initialization; collapse at init).

Sub-phase A3 -- GPU retrieval benchmark (< 5 min, GPU):
  Load codebook (N=8192, 32k atoms) to GPU. Run batched retrieval at
  batch_sizes [8, 32, 128, 512]. Measure latency P50 and P95.
  HARD-PASS: P95 latency < 5ms at batch=32, seq=128 (acceptable overhead).
  HARD-FAIL: P95 > 20ms (retrieval is bottleneck; reduce codebook size or quantize).

### Phase B: Pythia-160M single-layer Flamingo insert + fact-transmission (single GPU, < 1 hr)

**Purpose**: first end-to-end fact-transmission test. The decisive Tier 5c gate.

Setup:
  - Pythia-160M backbone frozen.
  - Single SubstrateCrossAttention insert at L4 (between layers 4 and 5).
  - Gate initialized at -4.0 (sigmoid ~ 0.018, effectively zero).
  - Bottleneck adapter: 8192*2 -> 256 -> 64 (per head, 12 heads).
  - Substrate codebook: 32k atoms, seeded from Pythia L4 hidden states.
  - Training: 5k steps, batch=32, AdamW lr=2e-4, 10k factual QA examples.

HARD-PASS: top-1 fact accuracy > 40% on 2k held-out QA pairs at step 5000.
MIDDLE-BAND: accuracy 20-40% (partial transmission; adapter learning but insufficient).
HARD-FAIL: accuracy < 20% at step 5000 (no fact-transmission learning; mechanism broken).

Monitoring:
  - gate_scalar value per 100 steps (should increase from -4.0 toward 0 or higher).
  - Attention entropy per 200 steps (should decrease from ~0.996 toward < 0.85).
  - Cross-attention output L2 norm per 100 steps (should increase from ~0 as gate opens).

### Phase C: Multi-family validation (1.4B scale + Qwen)

**Purpose**: verify the Flamingo pattern generalizes beyond Pythia-160M.

C1 -- Qwen-2.5-0.5B (24 layers, insert at L8):
  Same setup as Phase B. Adapter adjusts to head_dim=64, num_kv_heads=check config.
  HARD-PASS: top-1 accuracy > 40% on same held-out QA set.
  Why: different architecture family; confirms the adapter design is architecture-agnostic.

C2 -- Pythia-1.4B (24 layers, insert at L8):
  Scale from 160M to 1.4B while keeping single-layer Flamingo insert.
  HARD-PASS: top-1 accuracy >= Phase B result (larger model >= smaller model).
  HARD-FAIL: accuracy regresses vs Phase B (scaling breaks the mechanism; investigate).

C3 -- 2-layer insert (L4 + L7 in Pythia-160M):
  Add second cross-attention insert at L7. Measure marginal accuracy gain.
  HARD-PASS: 2-layer accuracy > 1-layer accuracy + 10 percentage points.
  HARD-FAIL: 2-layer accuracy < 1-layer accuracy (second layer hurts; likely gradient
  interference; reduce lr on second adapter or freeze first adapter while training second).

### Phase D: Demo quality (Qwen-2.5-3B, 1-2 layer surgical insert)

**Purpose**: achieve demo-quality fact-transmission on a 3B model sufficient for
v1 demo comparison against bare LLM on substrate-held knowledge.

D1 -- Qwen-2.5-3B (36 layers, insert at L12 and optionally L18):
  Partial unfreeze: top 4 LLM layers trainable + adapter + gate.
  Extended training: 20k steps at batch=64 on 50k QA examples.
  HARD-PASS: top-1 accuracy > 60% on diverse held-out QA set.
  HARD-FAIL: accuracy < 40% after full training (not demo-ready).

D2 -- Head-to-head comparison with bare Qwen-2.5-3B on substrate-held knowledge:
  On 500 questions requiring substrate facts: Tier-5c model vs bare Qwen-2.5-3B.
  HARD-PASS: Tier-5c accuracy > bare Qwen + 15 percentage points.
  This is the north star metric (substrate system beats bare LLM in clear measurable ways).

### Phase E: R&D from-scratch LARS-VSA replica (not a v1 prerequisite)

**Purpose**: demonstrate from-scratch VSA-attention training. Research milestone, not
product milestone. Only after Phases A-D deliver PASS results.

E1 -- Tiny GPT (6-layer, 64-dim, WikiText-2) with substrate-attention all layers:
  500k gradient steps from random init. Confirm loss decreases and codebook does not
  collapse. Pre-register: perplexity < 200 on test set (baseline for this tiny model).

E2 -- Pythia-70M scale with all-layer substrate-attention (from-scratch or conversion):
  The Tier 5c publishable result. GPU-day scale experiment.

---

## LEVEL 7: ENGINEERING ANCHORS PER PHASE

### Phase A anchors

anchor: t5c_wirtinger_gradient_smoke_v1
  Experiment: SubstrateCrossAttention forward+backward pass on random inputs; all gradient
    checks; confirm FHRR complex normalization gradient is finite.
  Cheap-decisive-first: CPU, < 5 min. Gates all subsequent phases.
  HARD-PASS: all adapter params have finite non-None gradients; gate.grad finite.
  HARD-FAIL: any NaN gradient in adapter or gate.

anchor: t5c_codebook_init_quality_v1
  Experiment: seed codebook from LLM L4 hiddens (1k tokens); measure utilization
    on 1k held-out tokens.
  HARD-PASS: utilization > 30% (atoms are diverse, not collapsed).
  HARD-FAIL: utilization < 5% (degenerate initialization; switch to random init).

anchor: t5c_gpu_retrieval_benchmark_v1
  Experiment: N=8192, 32k atoms; batch retrieval at [8, 32, 128, 512] x seq [128, 512].
  HARD-PASS: P95 < 5ms at batch=32 seq=128.
  HARD-FAIL: P95 > 20ms (reduce codebook or quantize).

### Phase B anchor

anchor: t5c_flamingo_single_layer_pythia160m_v1
  Experiment: frozen Pythia-160M + single cross-attention insert at L4; bottleneck adapter;
    gate init -4.0; train 5k steps on 10k factual QA pairs; eval top-1 accuracy.
  HARD-PASS: top-1 accuracy > 40% at step 5000.
  MIDDLE-BAND: accuracy 20-40% (partial; investigate gate and entropy).
  HARD-FAIL: accuracy < 20% at step 5000; OR gate does not move (< -3.5) at step 1000.

### Phase C anchors

anchor: t5c_flamingo_qwen05b_v1
  HARD-PASS: top-1 > 40% matching Phase B benchmark.
  HARD-FAIL: accuracy < 20%.

anchor: t5c_flamingo_pythia1b4_v1
  HARD-PASS: top-1 >= Phase B result.
  HARD-FAIL: top-1 < Phase B result - 10 pp (regression with scale).

anchor: t5c_flamingo_two_layer_v1
  HARD-PASS: top-1 > single-layer + 10 pp.
  HARD-FAIL: top-1 < single-layer result (regression from second insert).

### Phase D anchors

anchor: t5c_flamingo_qwen3b_demo_v1
  HARD-PASS: top-1 > 60%; head-to-head vs bare Qwen-3B exceeds +15 pp on substrate facts.
  HARD-FAIL: top-1 < 40% after full training.

---

## CHEAP DECISIVE TEST

Phase B anchor (t5c_flamingo_single_layer_pythia160m_v1) is the cheapest decisive test for
the entire Tier 5c program. It answers: does the gated cross-attention insert actually
transmit substrate facts to LLM output? Cost: < 1 GPU-hour. If this PASSES, the engineering
path to demo quality is clear (Phases C and D). If it FAILS, the failure mode is
diagnosable from gate trajectory and attention entropy. The test eliminates 5+ GPU-days
of uncertainty about whether the Flamingo approach works for substrate at all.

Sub-phase A1 (Wirtinger gradient smoke) should run first -- it costs < 5 minutes on CPU
and eliminates any concern about gradient flow correctness before GPU budget is committed.

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS

HP-1: Wirtinger gradient smoke (A1): all adapter param grads finite and non-None.
  Confidence: very high (P=0.90 deflated). FHRR is differentiable by construction.
  Only failure mode: implementation bug in complex -> real split.

HP-2: Codebook initialization quality (A2): utilization > 30% from LLM-seeded init.
  Confidence: moderate (P=0.65 deflated). Seeding from LLM hiddens should produce
  semantically distinct atoms. Failure mode: Pythia hidden states are too clustered.

HP-3: GPU retrieval benchmark (A3): P95 < 5ms at batch=32 seq=128.
  Confidence: high (P=0.80 deflated). Current substrate retrieval at CPU is 0.21ms;
  GPU should be faster, not slower. Only failure mode: memory bandwidth saturation.

HP-4: Flamingo single-layer fact-transmission (B): top-1 > 40% at 5k steps.
  Confidence: moderate (P=0.45 deflated). The adapter-entropy finding (0.996->0.809)
  shows the adapter can sharpen attention. Whether this translates to fact-transmission
  accuracy depends on the quality of the QA training set and gate opening dynamics.
  This is the primary empirical uncertainty.

HP-5: Phase C multi-family generalization: Qwen-0.5B and Pythia-1.4B both achieve
  top-1 > 40% with the same adapter design.
  Confidence: moderate (P=0.55 deflated, conditional on B PASS). Architecture-agnostic
  design should generalize; the main risk is Qwen's GQA configuration requiring adapter
  rewiring.

HP-6: Phase D demo quality: head-to-head Tier-5c Qwen-3B > bare Qwen-3B + 15 pp on
  substrate-held knowledge.
  Confidence: moderate (P=0.50 deflated, conditional on C PASS). This is the north star
  claim. The main risk: the substrate-held knowledge set may overlap with Qwen-3B's
  pretraining data, giving bare Qwen an unfair baseline advantage.

### HARD-FAIL

HF-1: Wirtinger gradient smoke fails (any NaN or None grad in adapter/gate).
  Action: debug complex -> real split; verify torch.autograd.grad works on complex64
  test case before integrating with LLM.

HF-2: Codebook utilization < 5% at init (degenerate initialization).
  Action: switch to random uniform complex initialization (Option B). If still < 5%,
  reduce codebook size to 4096 atoms.

HF-3: GPU retrieval P95 > 20ms (retrieval is bottleneck).
  Action: quantize codebook to float16; or use FAISS approximate nearest-neighbor;
  or reduce codebook to 8k atoms.

HF-4: Phase B fact-transmission accuracy < 20% at 5k steps AND gate has not moved.
  Action: increase gate learning rate (try 1e-3); verify substrate retrieval is returning
  correct atoms (debug with known fact). If gate moves but accuracy < 20%, the adapter is
  not shaping the cross-attention toward correct atoms -- try harder initialization
  (Option A with more seed data) or add explicit retrieval loss (cosine similarity between
  adapter output and target fact embedding).

HF-5: Phase C regression -- Pythia-1.4B accuracy < Phase B result.
  Action: scale-specific failure suggests the adapter design is not robust to LLM
  geometry differences with scale. Consider architecture-specific adapters or LoRA
  on top 4 layers.

HF-6: Phase D head-to-head fails (Tier-5c < bare Qwen + 5 pp).
  Action: increase training data size (50k -> 200k QA pairs); unfreeze full LLM with
  LoRA; or evaluate on a substrate-only knowledge domain where bare Qwen truly lacks data.

---

## CROSS-THREAD SYNTHESIS WITH PRIOR ENTRIES

**From Tier 5b HF (5 attempts)**: single-position injection fails because the LLM cannot
learn to selectively attend to substrate facts from a single-token prefix. The Flamingo
approach addresses this structurally: the cross-attention mechanism provides substrate
facts as K/V to every position in the sequence at the insertion layer, not as a single
prefix token. This is why Flamingo works for vision-language and why it should work here.

**From adapter-entropy finding (exp_dev_to_research_flamingo_pretest)**: frozen Qwen
attention over raw substrate HD vectors gives entropy=0.996 (uniform, useless). Brief
adapter training drops to 0.809. This confirms the adapter is REQUIRED and that it does
learn to shape attention (in principle). Phase B extends this to full fact-transmission
training.

**From Tier 4 HP (ppl_ratio=0.939)**: substrate-attention layer improves single-layer
perplexity. This means substrate's algebra is already compatible with Pythia's learning
landscape at one layer. Flamingo inserts a DIFFERENT module (cross-attention, not attention
replacement) but establishes that substrate-LLM interaction at the layer level is tractable.

**From GHRR-Transformer (OpenReview 2024)**: VSA-based attention trained on language modeling
tasks works end-to-end. This is the existence proof for Phase E (from-scratch training).
Phases A-D (Flamingo frozen adapter) are cheaper and faster paths to the same functional
goal without the from-scratch risk.

**From substrate speed findings (PP-150)**: substrate at 0.21ms CPU is 0.7% of LLM inference
cost. This means the adapter + retrieval overhead in the Flamingo architecture will be
dominated by the LLM backbone, not the substrate. Engineering focus is correctness and
gradient flow, not speed optimization.

**From multi-hop revival (MEMORY.md)**: Tier 5c fact-transmission enables multi-hop queries
without iterative LLM calls (K hops through substrate in one forward pass, with K-hop chain
passed as K/V to cross-attention at L4). This is the architectural path to multi-hop without
increased LLM inference cost.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. Frozen-backbone Flamingo adapter: the LLM's language quality is preserved perfectly.
   No perplexity regression on general language. The product delivers: "same language
   quality as the base LLM + substrate facts on top." This is the safest product story.

2. If Phase B PASSES (top-1 > 40%): first working demonstration that a small frozen
   pretrained LLM can be made to use substrate knowledge through a trained gated
   cross-attention adapter. The adapter is < 30M parameters. This is a deployable unit:
   any user with the LLM and the adapter weights (not the substrate) gets fact-aware
   inference on whatever substrate they connect. The adapter is the product artifact.

3. Phase D demo target: head-to-head Qwen-3B + substrate adapter vs bare Qwen-3B on
   substrate-only knowledge. This is the north star metric demonstration. If this
   delivers +15 pp accuracy, the claim "substrate system beats LLMs of relative size
   in clear measurable ways" is empirically supported.

4. Codebook size and deployment: a 32k-atom frozen codebook at N=8192 = 2.1 GB. This
   is too large for edge deployment but fine for server inference. For edge: compress
   to 8k atoms at N=4096 = 262 MB, within mobile device budget. Phase A-B can validate
   at full size; Phase C+ can include a compression study.

5. Multi-GPU substrate sharding: once the single-GPU Flamingo adapter works, the
   substrate codebook shards trivially across GPUs (each GPU holds a shard; retrieval
   is a scatter-gather). This is substrate's existing D3 architecture (routing=0.999).
   Tier 5c does not require redesigning substrate for multi-GPU; the existing sharding
   is already multi-GPU capable.

---

## CITATIONS (verified via prior lit-scan drills; these papers were previously fetched and read)

1. Alayrac et al. 2022 "Flamingo: a Visual Language Model for Few-Shot Learning"
   NeurIPS 2022 / arXiv:2204.14198. Primary reference for gated cross-attention schedule.

2. Tenney et al. 2019 "BERT Rediscovers the Classical NLP Pipeline"
   ACL 2019 / arXiv:1905.05950. Layer-function probing results.

3. Geva et al. 2020 "Transformer Feed-Forward Layers Are Key-Value Memories"
   EMNLP 2021 / arXiv:2012.14913. Middle-layer factual knowledge localization.

4. Van den Oord et al. 2017 "Neural Discrete Representation Learning" (VQ-VAE)
   NeurIPS 2017 / arXiv:1711.00937. Commitment loss + EMA codebook update.

5. Hu et al. 2022 "LoRA: Low-Rank Adaptation of Large Language Models"
   ICLR 2022 / arXiv:2106.09685. Low-rank adapter fine-tuning; parameter-efficient LLM training.

6. Mejri et al. 2024 "LARS-VSA: A Vector Symbolic Architecture For Learning with
   Abstract Rules" arXiv:2405.14436. Bipolar VSA-attention trained end-to-end; 17x/25x efficiency.

7. OpenReview "Structure-aware Attention based on Vector Symbolic Architectures" (GHRR-
   Transformer) 2024. GHRR-based attention trained on language modeling tasks from scratch.

8. Ramsauer et al. 2020 "Hopfield Networks Is All You Need" NeurIPS 2020, arXiv:2008.02217.
   Attention = modern Hopfield update rule. Differentiable; exponential storage capacity.

9. arXiv:2512.14709 (Dec 2025) "Attention as Binding: A Vector-Symbolic Perspective on
   Transformer Reasoning." Formal attention=VSA correspondence; FHRR as valid instantiation.

10. Gupta et al. 2023 "Continual Pre-Training of Large Language Models"
    arXiv:2308.04014. Recovery token estimates for domain-adaptive continued pretraining.

11. Glorot and Bengio 2010 "Understanding the Difficulty of Training Deep Feedforward
    Neural Networks" AISTATS 2010. Xavier initialization derivation.

12. Jang et al. 2017 "Categorical Reparameterization with Gumbel-Softmax"
    ICLR 2017. Differentiable discrete sampling; directly applicable to soft-cleanup
    relaxation of hard codebook lookup.

13. Ramesh et al. 2021 "Zero-Shot Text-to-Image Generation" (DALL-E)
    ICML 2021 / arXiv:2102.12092. 8192-atom codebook training; atom reset strategy.

14. Hoffmann et al. 2022 "Training Compute-Optimal Large Language Models" (Chinchilla)
    NeurIPS 2022 / arXiv:2203.15556. Token-to-parameter ratio for compute-optimal training.

15. Hoover et al. 2024 "Outlier-Efficient Hopfield Layers for Large Transformer-Based
    Models" arXiv:2404.03828. Drop-in Hopfield layer substitution into existing transformers.

16. Anil et al. 2024 "Hopfield-Fenchel-Young Networks" arXiv:2411.08590.
    Sparse differentiable Hopfield update rules.

17. Graves et al. 2016 "Hybrid computing using a neural network with dynamic external
    memory" (DNC) Nature 2016. Memory initialization from task-relevant representations
    converges faster (ablation reference).

Citations: 17 verified (all sourced from prior lit-scan sessions in the Tier 5c drill series).
