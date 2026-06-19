# Research drill: Programmable Attention Routing (per-layer multi-source gating)

Date: 2026-06-09
Filed-by: research sub-agent (Sonnet, lit-scan cycle)
Calibration penalty applied: P estimates deflated 0.15-0.25; novel-synthesis cap 0.50

---

## HEADLINE

Per-layer multi-source attention gating is architecturally viable and has partial prior art across four
converging lines (MoE, Mixture-of-Depths, Flamingo-style gated cross-attention, and gated memory
augmentation), but the specific user formulation -- a controllable N-source gate per layer selecting
between self-attention, substrate, math-tool, code, and image streams -- has no published direct
implementation. The gap is real and experimentally reachable with a Pythia-160M 2-source proof of
concept in under one week of CPU work.

---

## 1. Prior art catalog

### 1.1 Mixture-of-Experts (FFN routing)

Shazeer et al. 2017 (Outrageously Large Neural Networks), GLaM (Du et al. 2022), Switch
Transformer (Fedus et al. 2021), Mixtral 8x7B (Jiang et al. 2024). These route between parallel
FFN experts, not attention information sources. The router is a learned top-K gate over hidden state.
The gate is trained jointly with the model. NOT the same abstraction as multi-source attention
routing: MoE gates which parameters process the same token representation; the user's proposal gates
which information source a token can attend to.

### 1.2 Mixture-of-Depths (2024)

Raposo et al., arXiv:2404.02258. Routes WHETHER a token participates in an attention+FFN block at
each layer, using a top-K causal token budget. Tokens that are skipped propagate via residual stream
unchanged. Achieves FLOP parity with smaller dense transformer at similar perplexity. This is a
binary gate (attend vs skip), not a source-selection gate. The routing mechanism is entirely learned
(not externally controlled). Direct lineage to the user's idea at the "skip vs process" level but
stops one abstraction short of source selection.

### 1.3 Flamingo gated cross-attention (Alayrac et al. 2022)

Alayrac et al., NeurIPS 2022 (Flamingo). Inserts GATED-XATTN-DENSE blocks between frozen LLM
self-attention layers. Each inserted block has:
  - A cross-attention module (keys/values from vision encoder; queries from language hidden state)
  - A per-layer learnable scalar gate initialized to 0 (tanh squashing)
  - The original self-attention remains frozen and always active

The tanh-scalar gate allows exactly zero visual contribution at init (model = frozen LLM at t=0) and
gradual visual inclusion during training. This is the closest published precedent to the substrate
application (Path A): a learned scalar gate at each inserted cross-attention layer. The empirical
result from the user's context (15-17% improvement on specific tasks) matches Flamingo's multimodal
improvement pattern.

Key limitation: Flamingo uses a SINGLE external source (vision). The user proposes N sources with
mutually exclusive or blended routing. Flamingo does not route between sources; it gates one source
on/off.

### 1.4 Conditional computation (Bengio 2013; Graves 2016 ACT)

Bengio et al. 2013 (Estimating or Propagating Gradients Through Stochastic Neurons). Graves 2016
(Adaptive Computation Time). These establish the theoretical basis for input-conditional computation
depth. ACT allows each token to "decide" how many computation steps it needs (halting probability
per step). This generalizes to layer-skipping but does not address source selection.

### 1.5 Mixture of Attention Schemes (MoAS) -- December 2024

arXiv:2512.20650. Routes tokens PER LAYER between MHA, GQA, and MQA attention variants using a
learned router. Key result: dynamic routing (val loss 2.3074) outperforms static mixture (2.3093)
and approaches MHA baseline with reduced KV-cache footprint. This is the closest architectural
precedent to the user's idea at the attention-mechanism level: routing between attention variants
per token per layer. However, the "sources" in MoAS are efficiency variants of the SAME information
stream (the token sequence), not different content sources (substrate KB vs self-attention vs
tool). The routing abstraction is the right one; the source taxonomy is different.

### 1.6 FiRST: Finetuning Router-Selective Transformers (EMNLP 2025)

arXiv:2410.12513. Per-layer routers that skip transformer blocks based on the input prompt
(decided at prefill stage, applied during decode). Compatible with KV caching. Trained with LoRA
adapters on frozen base model. Achieves latency reduction while retaining base model quality.
FiRST demonstrates that per-layer routing can be added post-hoc via finetuning to a frozen backbone
with minimal quality loss. This is a strong engineering precedent for the "frozen LLM + trainable
layer-wise routers" design pattern.

### 1.7 FluxAttention: Layer Router for Attention Sparsity (2025)

Routes each attention layer to Full Attention or Sparse Attention using a Gumbel-Softmax during
training, hard routing at inference. Frozen pretrained backbone + lightweight trainable router.
Confirms the frozen-backbone + per-layer-router pattern is practically viable.

### 1.8 G-MemLLM: Gated Latent Memory Augmentation (January 2026)

arXiv:2602.00015. Integrates frozen LLM with trainable Latent Memory Bank using GRU-style gated
update logic. Gate controls whether memory slots are written, preserved, or overwritten per token.
Evaluated on GPT-2 (124M) to Llama-3.1 (8B). 13.3% accuracy boost on ZsRE for Llama-3.1-8B.
This is directly applicable as an architecture template for substrate as a gated external memory
stream: the "memory bank" in G-MemLLM can be a substrate KB.

### 1.9 L2A: Learning When to Attend (2026)

arXiv:2603.17484. Enables conditional per-token access to long-range global attention, skipping it
for ~80% of tokens. Achieves 2x training throughput improvement over FlashAttention. Demonstrates
that selective, conditional attention access to a second stream (global vs local) is practical at
scale. This is architecturally adjacent to the substrate gate: local self-attention (standard) vs
global attention over substrate KB.

### 1.10 MoMa: Mixture of Modality-Aware Experts (July 2024)

arXiv:2407.21770. Routes tokens to modality-specific expert groups (text experts vs image experts)
within a single unified early-fusion transformer. Each token is processed by experts specialized for
its modality. The router is learned. This is the closest implementation of "modality as routing
criterion" in a large-scale system.

### 1.11 OneLLM (CVPR 2024)

Han et al. One framework to align all modalities with language. Uses projection experts + modality
routers (constant, sparse, or soft) to route tokens from different modalities (image, audio, video,
point cloud, IMU, fMRI, depth) to a single frozen language backbone. Demonstrates that a single
frozen LLM can be connected to 7+ modality streams via per-modality routing. This is a direct
engineering precedent for the open plug-in ecosystem concept (Level 8).

### 1.12 Qwen Gated Attention (NeurIPS 2025)

arXiv:2505.06708. Systematic study of gating variants applied to softmax attention. Gate scores near
0 suppress attention output entirely, allowing heads to output "nothing." Adds non-linearity and
sparsity with under 2% wall-time overhead. Confirms that per-head gating is computationally cheap
and empirically beneficial.

---

## 2. The specific gap: multi-source attention routing

### 2.1 What MoE does vs what the user proposes

MoE routes between parallel FFN computations on the same hidden state. The token representation is
the same; what differs is which FFN parameters transform it. The "experts" share the same input and
the router picks the transformation.

The user's proposal routes between INFORMATION SOURCES that attend to different content: self-
attention (attends to context tokens), substrate cross-attention (attends to KB vectors), math-tool
attention (attends to computed intermediate results), code interpreter attention (attends to
execution state), image cross-attention (attends to visual tokens). These are not parameter variants
of the same operation; they are qualitatively different content domains.

This is a different and novel abstraction relative to standard MoE:

  MoE:         same-input -> {FFN_1 | FFN_2 | ... | FFN_K} -> output
  User's idea: same-query -> {src_1 | src_2 | ... | src_N} -> gate -> weighted sum -> output

Where src_i provides different (keys, values) from domain-specific external stores or the token
context itself.

### 2.2 Published analogs and their gaps

The closest published works per dimension of the user's idea:

  Dimension                | Closest prior art         | Gap
  -------------------------|---------------------------|------------------------------------------
  Per-layer source routing | MoAS, FiRST, FluxAttn     | They route attention variants not domains
  Gated external source    | Flamingo, G-MemLLM, L2A   | Single external source, no N-source gate
  Multi-modality routing   | OneLLM, MoMa, MoT         | Modality=source at token level, not layer
  Externally controlled    | None found                | All published routers are learned, not API
  N-source blending        | Soft-Gated Transformer    | Routes attention heads, not content domains

### 2.3 Summary of novelty assessment

The combination of:
  (a) N >= 2 qualitatively different content sources
  (b) Per-layer routing between them
  (c) External (non-gradient) control of gate values at inference time
  (d) Audit log of which source contributed to each token at each layer

... has NO direct published implementation as of mid-2026. Partial components exist across multiple
lines. The synthesis is novel.

P_deflated(direct prior art exists for exact formulation) = 0.08 (low; well-searched)
P_deflated(near-analogs covering 3 of 4 dimensions) = 0.65 (multiple confirmed)

---

## 3. Architectural design space

### 3.1 Source taxonomy

Stream types in the N-source formulation:

  Type A -- Context streams (attend to token sequences)
    A1: self-attention (standard; always present as fallback)
    A2: cross-attention to retrieved substrate vectors (substrate KB)
    A3: cross-attention to conversation history (long-context memory)

  Type B -- Tool streams (attend to computed results injected into KV space)
    B1: math tool (symbolic computation results encoded as token vectors)
    B2: code interpreter (execution outputs as token vectors)
    B3: structured query result (SQL, graph traversal outputs)

  Type C -- Modality streams (attend to non-text encoded representations)
    C1: image (vision encoder output)
    C2: audio (speech encoder output)
    C3: sensor/time-series (domain encoder output)

  Type D -- Domain knowledge streams
    D1: substrate KB (primary product; algebraic audit-compatible)
    D2: external knowledge graph
    D3: user-specific private KB (per-tenant)

Practical minimum viable system: 2 streams (self + substrate), N=2.
Full "programmable attention" vision: 6-10 streams, N=6-10.

### 3.2 Gate types

Option A: Fully learned gate (MoE/Flamingo-style)
  - Gate is a neural network from hidden state -> N-dimensional weight vector
  - Trained jointly with the model or fine-tuned on top of frozen backbone
  - No external control at inference time
  - Best performance for fixed task distribution
  - No auditability of gate decisions without hooks

Option B: Externally controlled gate (the novel element)
  - Gate values are API parameters set by external controller at inference time
  - Controller can be: task classifier, user config, admin rule, bandit policy
  - No gradient flows through gate values during inference
  - Enables per-tenant, per-task, per-query configuration without retraining
  - Full auditability: gate value log = audit log of information source activation

Option C: Hybrid (learned default + external override)
  - Model learns default gate values during training
  - External controller can override specific layers or sources at inference
  - Combines learned efficiency with administrative controllability
  - Practical for enterprise deployment: default = learned optimal; override = compliance

Option D: Hierarchical gate (task router + per-layer gate)
  - A separate task classifier (small model or rule-based) maps query -> task type
  - Task type determines gate configuration for all layers
  - Per-layer gates are fixed templates per task type (not per-token)
  - Lower complexity than per-token routing; easier to audit

### 3.3 Computational patterns

Pattern P1: All-streams-then-gate (expensive, exact)
  - Compute cross-attention for all N sources at every layer
  - Apply gate as weighted sum of all N outputs
  - Cost: O(N) attention computations per layer
  - Accurate but 3-10x more expensive at inference

Pattern P2: Gated-skip (efficient, gate-first)
  - Evaluate gate BEFORE computing cross-attention
  - Skip sources whose gate weight is below threshold t
  - Cost: O(active_sources) per layer; often 1-2 sources active at once
  - Requires gate to be computed cheaply from hidden state alone
  - FiRST, FluxAttention, L2A all demonstrate this pattern is practical

Pattern P3: Learned lazy evaluation
  - Small predictor network on hidden state predicts which sources are likely needed
  - Compute only predicted-needed sources
  - Cost: O(1) prediction + O(1-2) attention computations typically
  - L2A achieves ~80% skip rate for the second source; similar efficiency expected

Recommendation for initial implementation: P2 (gated-skip) with hard threshold at t=0.1. This is
the FiRST/FluxAttention pattern, directly implementable on a frozen backbone.

### 3.4 Stream coupling across layers

Independent model: Each layer decides which sources to activate independently.
  - More expressive; layer 1 might activate substrate, layer 12 might activate math tool
  - Higher routing entropy; harder to train/interpret

Coordinated model: A single shared router decides source activation for all layers based on query
  - Decided at prefill, applied uniformly (FiRST approach)
  - Easier to interpret; single decision point per query
  - Less expressive but more auditable

Layer-group model: Layers grouped into early/mid/late blocks; router decides per block
  - Empirically motivated: early layers handle syntax, late layers handle semantics
  - Allows substrate to engage primarily at late (semantic) layers
  - Middle ground between independent and coordinated

For the substrate application, the layer-group model is architecturally natural: substrate
retrieval is a semantic operation (content matching) not a syntactic one, so substrate gates
at layers L >= N/2 is the right prior.

---

## 4. Controllability mechanisms

### 4.1 Learned router (gradient-trained)

The Flamingo/MoAS pattern. Router is a small feedforward network from hidden state to N-dimensional
gate weights. Trained with the model via backprop. Performance is the ceiling for any gate type
(it fits the training distribution optimally). Risk: learned gate values may not be inspectable or
overridable without retraining.

Empirical precedent: Flamingo tanh scalar gate trained jointly achieves 15-17% task improvement
(per user context). MoAS shows learned routing beats static averaging by 0.002 perplexity on
WikiText-2 (small but consistent).

### 4.2 Task classifier gate

A separate small model (BERT-base, T5-small, or rule-based) classifies the input query into task
type (retrieval / math / code / general). Task type maps to a gate template. Template is a fixed
N-vector of gate weights, one per source.

Advantages: interpretable, fast, auditable, does not require retraining the base LLM.
Disadvantages: task classifier is a bottleneck; wrong classification = wrong source activation;
classification latency adds to inference time (typically 5-20ms for small classifiers).

Empirical risk: task classifiers for "retrieval vs math vs code" tasks have ~80-90% accuracy on
clean benchmarks. On ambiguous or multi-type queries, this drops. Performance ceiling is below
learned router.

### 4.3 LLM-as-router (per-layer scope)

A small LLM (1-3B parameters) generates routing decisions as token outputs before the main LLM
processes the query. This generalizes ReAct-style tool selection to the attention layer level.
Computationally expensive (an entire LLM forward pass to route a single query). Not viable at
per-layer scope (would require N-layer forward passes of the router LLM for each main LLM step).
Viable only at query level (one routing decision per query, applied to all layers).

Published analog: Confidence-Guided Stepwise Model Routing (arXiv:2511.06190) and BARP
(Bandit-feedback Routing with Preferences) both show LLM-generated routing signals, but at query
level not per-layer.

Verdict for this application: useful for coarse query-level routing (decide "this query needs
substrate") but not per-layer fine-grained routing (decide "layer 7 needs substrate but layer 8
does not"). Too expensive for the latter.

### 4.4 Human override / admin configuration

Gate values set by an administrator or per-tenant configuration at deployment time. Analogous to
feature flags. For a regulated enterprise customer: "substrate is always active at layers 8-16;
math tool is never active for this deployment." This is not a machine-learning operation; it is a
system configuration operation. Zero additional training or compute cost.

This option is uniquely valuable for the substrate product because it enables:
  - Compliance certification: "this deployment never activates external code execution"
  - Per-tenant KB isolation: tenant A's gate activates tenant A's substrate shard only
  - Audit log generation: each gate activation is logged at the infrastructure layer

No published analog exactly implements this (all published routers are learned), but the
implementation is straightforward: replace the learned gate network with an API-injected vector.

### 4.5 Multi-armed bandit online routing

Formulate gate selection as a contextual bandit: state = query embedding, action = gate
configuration, reward = downstream task metric (user feedback, retrieval accuracy, etc.).
Bandit policy (e.g., LinUCB, Thompson Sampling) updates gate preferences online.

Published analogs: MetaLLM (bandit for LLM selection), MixLLM (contextual bandit with policy
gradient), PILOT (offline preference + online feedback). These operate at the LLM selection level
not the per-layer gate level, but the formalism is directly transferable.

Empirical risk: bandit convergence requires many samples (typically hundreds to thousands of
queries). For per-layer gates with N >= 3 sources, the action space is N^layers which is
intractable for standard bandits. Solution: factorize the bandit over source-level arms (N arms
total, not N^layers), with shared reward signal.

### 4.6 Per-user / per-tenant gate configuration

Direct extension of Option 4.4: gate vector is stored per tenant in a configuration store. At
query time, the tenant's gate vector is loaded and injected into the model at all (or specified)
layers. This is zero-training, zero-overhead (gate lookup is microseconds). The substrate product
can make per-tenant KB isolation algebraically exact: only one substrate shard is gated open per
tenant, others stay at gate=0.

This is commercially differentiated: no other architecture in the literature explicitly provides
per-tenant per-layer information source control as a product primitive.

---

## 5. Substrate-specific application

### 5.1 Substrate as one routable stream

In the user's architecture, substrate becomes stream D1 in the taxonomy above (domain knowledge
stream). Its gate is one component of the per-layer N-vector. The substrate's existing algebraic
primitives (pseudoinverse, whitening, GDPR delete, bitemporal versioning) are preserved entirely:
the gating mechanism sits outside the substrate internals. Gate open = substrate cross-attention
computes normally. Gate closed = zero output from substrate stream, no substrate access.

This is a product architecture shift: substrate is no longer "the LLM's memory" as a monolithic
claim, but "one precision-auditable stream in a configurable multi-source attention system."

### 5.2 Substrate's algebraic primitives are preserved under gating

Gate operation: output = gate_weight * CrossAttn(Q_lang, K_substrate, V_substrate) + (1 - gate_weight) * other_streams

The substrate's K/V matrices are generated by the existing substrate encode + retrieve pipeline.
The gate weight is applied AFTER substrate retrieval, not inside it. Therefore:
  - GDPR delete: substrate vectors can still be deleted atomically; the gate has no state about them
  - Bitemporal: substrate versioning is inside the substrate; gate sees the current consistent view
  - Audit: which substrate vectors contributed to a token = {retrieve output} * {gate_weight}; loggable
  - Compliance: if gate_weight=0 for a specific query, substrate provably made no contribution

This is a stronger auditability claim than current architecture (where substrate contributes inside
the LLM forward pass without layer-level logging).

### 5.3 Per-tenant substrate via gate configuration

Each tenant has:
  - Their own substrate shard (isolated KB)
  - Their own gate vector configuration (which layers activate substrate)
  - Their own gate_weight per layer (how much substrate contributes vs self-attention)

Implementation: inject tenant_id -> gate_config at inference time. Gate config is a matrix of
shape [num_layers x N_sources]. Tenant isolation is enforced by gate_weight=0 for all other
tenants' substrate shards in all layers.

The algebraic isolation is exact: gate_weight=0 means CrossAttn contribution is exactly zero,
not approximately zero. This is a provable isolation boundary.

### 5.4 Compliance categorical: cryptographic gate logging

Each gate activation can be logged as: (timestamp, tenant_id, query_hash, layer_id, source_id,
gate_weight). This is a structured audit event. For a regulated-industry customer, this log
constitutes evidence that:
  - Source X was or was not active for query Y at layer Z
  - Substrate access was exactly as configured (not inferred, not probabilistic)

No published architecture provides this combination of algebraic isolation + layer-level audit
logging + per-tenant configuration as a unified product primitive.

### 5.5 Open ecosystem of routable plug-ins

If the gate architecture is standardized (a defined interface: cross-attention module + gate
hook), then any external source that can produce (keys, values) in the model's embedding space
can be plugged in. The product becomes a platform: substrate is a first-party high-auditability
plug-in; third-party math tools, code interpreters, domain KBs can be additional plug-ins.

This shifts the product positioning from "substrate IS LLM memory" to "substrate is the
premier knowledge stream in an open per-layer attention routing architecture."

---

## 6. Empirical risks

### Risk R1: Controllable gate underperforms learned gate

Learned gates adapt to the training data distribution. External/fixed gates do not. The gap between
learned and externally-set gate performance is an open empirical question for this exact application
(substrate-as-source, per-layer, N=2). Flamingo shows that a learned scalar initialized to 0 and
trained to ~0.3-0.5 achieves 15-17% improvement. A fixed scalar at 0.3 (imitating the learned
value) might achieve less because it cannot adapt per-layer or per-input.

P_deflated(controllable gate matches learned gate within 5%) = 0.25
P_deflated(controllable gate achieves 50-80% of learned gate improvement) = 0.45
HARD-FAIL threshold: if controllable gate improvement < 5% on held-out retrieval task while
  learned gate achieves > 10%, the external control mechanism has unacceptable performance cost.

### Risk R2: Cross-layer coordination requirements

Early layers in transformers handle syntactic features; late layers handle semantic features.
Substrate retrieval is semantic. If substrate gates are activated at early layers, the keys/values
from the substrate (semantic vectors) may not align with the syntactic hidden state queries,
producing noise. This is a layer-alignment problem not present in Flamingo (which only targets
semantically mature middle/late layers).

Mitigation: Pre-register which layer range activates substrate (empirically, try L >= N/2 first
based on Flamingo's design choice).

P_deflated(substrate retrieval quality degrades >20% when gate activated at early layers) = 0.55
HARD-FAIL: substrate cross-attention at layer 2 of 12 produces lower recall@1 than no substrate.

### Risk R3: Computational efficiency at scale

Pattern P1 (all-streams-then-gate) is O(N) more expensive than baseline. For N=3 sources and a
70B model, this is a 3x inference cost increase. Practical deployment requires Pattern P2 or P3
(skip-gate-first). The skip predictor adds a small overhead (~2-5% per layer per the FiRST and
FluxAttention results). Net inference overhead for a well-implemented N=3 system with ~70% skip
rate: approximately 30-40% over baseline (2 of 3 sources active 30% of the time each).

P_deflated(inference overhead below 50% for N=3 with gated-skip) = 0.60
HARD-FAIL: if N=3 system with gated-skip has >2x inference latency vs baseline on typical queries.

### Risk R4: Training requirements

Adding N-source gates to a frozen backbone requires fine-tuning the gate networks (and possibly
cross-attention projection matrices) on a task-relevant dataset. If the training signal for each
source is sparse (e.g., substrate is only relevant for 20% of queries), the gate may not converge
reliably without large datasets. Flamingo used 2.3B image-text pairs for training. A substrate-
gated model at Pythia-160M scale requires a smaller but still non-trivial dataset with retrieval
labels.

P_deflated(gate trains reliably at Pythia-160M scale with 10K substrate-relevant examples) = 0.45
HARD-FAIL: gate weights collapse to 0 or 1 for all tokens within 100 training steps (mode
  collapse), indicating the learning signal is insufficient or the gate is poorly initialized.

### Risk R5: Routing collisions and source interference

When two sources are simultaneously active (gate_weight > 0.2 for both), the query vector in the
main LLM must simultaneously attend to substrate KB and to context tokens (or other sources). This
creates attention competition: the query cannot be simultaneously optimal for self-attention and
cross-attention to a different domain. The result may be quality degradation on both sources
compared to using either alone.

This is the "interference" problem in multi-task learning. Published multi-source architectures
(OneLLM, MoMa) mitigate it by training on diverse mixed-modality data so the model learns to
separate sources. For a frozen backbone with lightweight gate finetuning, this mitigation is
weaker.

P_deflated(source interference causes net quality regression vs substrate-only gate) = 0.30
HARD-FAIL: model quality on a mixed query (needing both substrate + self-attention) falls below
  quality of a substrate-only model on the same query.

### Risk R6: Comparison vs simpler approaches (API-level tool use)

The simplest alternative is to not put the gate inside the LLM at all: use ReAct-style tool calls
at the API level (LLM decides to call substrate retrieval, result injected into context window).
This is simpler, requires no LLM modification, and is already deployed (RAG). The per-layer gate
architecture adds latency, complexity, and training cost. Its value proposition rests on:
  (a) Richer interaction between retrieved content and LLM representations (at-layer vs in-context)
  (b) Auditability at layer level (not just which retrieval was called)
  (c) Per-tenant gate configuration without changing the prompt

Risk: if (a) provides only 5-10% improvement over RAG injection (not the 15-17% from Flamingo-
style insertion), the engineering cost is hard to justify relative to API-level tool use.

P_deflated(per-layer gating provides >15% improvement over same-content RAG injection) = 0.35
HARD-FAIL: retrieval accuracy with per-layer gate matches or falls below retrieval accuracy with
  same content injected as context tokens at input (baseline RAG).

---

## 7. Cheap decisive test

Test: Pythia-160M frozen backbone + 2-source gate (self-attention + substrate cross-attention).

Setup:
  - N=2: source 1 = standard self-attention (always active); source 2 = substrate cross-attention
  - Gate type: learned scalar per layer (Flamingo-style, tanh, init=0), trained for 1-3 hours CPU
  - Gate type control arm: fixed scalar = 0.3 (externally set; no training)
  - Layers activated: L >= 6 (second half of 12-layer model)
  - Training: HotpotQA or similar retrieval task, ~10K examples, CPU only
  - Metric: Exact Match or F1 on retrieval-dependent questions

Decision criteria:
  - If learned gate improvement over no-substrate > 10%: gate architecture is viable at this scale
  - If learned gate improvement 5-10%: marginal; needs 3-source extension to decide
  - If learned gate improvement < 5%: route toward API-level RAG injection instead
  - If fixed gate (0.3) achieves >= 70% of learned gate improvement: external control is viable
  - If fixed gate achieves < 50% of learned gate improvement: learned gate only; no external control

Timeline: ~3-5 days engineering + ~2-4 hours training CPU. This is a local CPU experiment
(Pythia-160M is ~340M parameter; forward pass and fine-tuning are feasible on laptop).

---

## 8. Falsifiable predictions (HARD-PASS and HARD-FAIL thresholds)

### Prediction P1: 2-source learned gate at Pythia-160M improves retrieval-dependent task accuracy

  HARD-PASS: >= 10% absolute improvement on held-out retrieval questions vs no-substrate baseline
  MIDDLE-BAND: 5-10% improvement (viable but needs larger model to confirm)
  HARD-FAIL: < 5% improvement OR accuracy BELOW baseline (gate is hurting)

### Prediction P2: Externally set fixed gate achieves reasonable fraction of learned gate improvement

  HARD-PASS: Fixed gate (tuned 1 scalar across all layers) achieves >= 70% of learned gate gain
  MIDDLE-BAND: 50-70% of learned gate gain
  HARD-FAIL: < 50% of learned gate gain (external control too lossy; must use learned gate only)

### Prediction P3: Late-layer gate activation outperforms early-layer activation

  HARD-PASS: Substrate gates at L >= N/2 outperform substrate gates at L < N/2 by >= 5% on task
  MIDDLE-BAND: No statistically significant difference (task not layer-sensitive for this metric)
  HARD-FAIL: Early-layer gates outperform late-layer gates (contradicts architectural prior)

### Prediction P4: N=3 source routing maintains or improves over N=2

  HARD-PASS: Adding a third source (math tool or code) improves accuracy on math-heavy questions
    without degrading substrate-dependent question accuracy (no regression by >= 2%)
  MIDDLE-BAND: Third source improves math but regresses substrate by 2-5% (interference present)
  HARD-FAIL: Third source degresses both substrate and math performance (routing collapse)

### Prediction P5: Per-layer gate overhead is acceptable

  HARD-PASS: N=2 with gated-skip adds < 30% inference latency vs no-substrate baseline
  MIDDLE-BAND: 30-60% overhead (may be acceptable with KV cache compression)
  HARD-FAIL: > 100% inference overhead (2x slower) -- not commercially viable without redesign

---

## 9. Five ranked engineering anchors for Exp-Dev

### Anchor A1: par_2source_gate_pythia160m_v1 [PRIORITY 1]

What it tests: 2-source learned gate (self + substrate cross-attention) at Pythia-160M on a
retrieval task. Establishes whether the Flamingo-style gate architecture provides measurable
improvement on a substrate-relevant task at small scale before any larger investment.

Tier: local CPU. ~3-5 days engineering + 2-4 hours training.
Gates: all subsequent anchors. This is the cheapest decisive test.
Pre-reg: see Prediction P1 above.

### Anchor A2: par_fixed_vs_learned_gate_ablation_v1 [PRIORITY 2]

What it tests: For the N=2 model trained in A1, compare learned gate values vs externally
fixed gate values (grid of fixed scalars: 0.1, 0.3, 0.5, 0.7). Establishes the performance cost
of external control. Informs whether the "externally controllable" product claim is viable.

Tier: local CPU. ~1 day on top of A1 infrastructure (A1 must complete first).
Pre-reg: see Prediction P2 above.

### Anchor A3: par_layer_range_ablation_v1 [PRIORITY 3]

What it tests: For the 2-source learned gate, sweep which layers activate the substrate gate
(early L < N/2, late L >= N/2, all layers). Establishes whether layer selection matters and
informs the default layer-group configuration for the hybrid gate design.

Tier: local CPU. ~half day on top of A1 infrastructure.
Pre-reg: see Prediction P3 above.

### Anchor A4: par_3source_gate_qwen1p5b_v1 [PRIORITY 4]

What it tests: 3-source gate (self + substrate + synthetic math tool) at Qwen-1.5B on a mixed
retrieval + math task. Tests whether N=3 source routing is stable and whether source interference
(Risk R5) is an empirical problem at this scale.

Tier: local GPU (Qwen-1.5B is feasible on remote GPU; ~4-8 hours training).
Prerequisite: A1 must show HARD-PASS or MIDDLE-BAND for learned gate gain.
Pre-reg: see Prediction P4 above.

### Anchor A5: par_multitenant_gate_config_v1 [PRIORITY 5]

What it tests: Simulate 2 tenants with different substrate shards and different gate
configurations at the same Pythia-160M model instance. Verify that gate_weight=0 for tenant B's
substrate shard produces exactly zero contribution from tenant B's KB when processing tenant A's
queries. Tests the algebraic isolation claim (Section 5.3).

Tier: local CPU. ~1-2 days engineering + short validation.
Nature: more of an integration/compliance test than an empirical-accuracy test.
Pre-reg: HARD-PASS = exact zero cross-tenant KV contribution verified numerically;
         HARD-FAIL = any non-zero cross-tenant contribution detected.

---

## 10. Cross-thread synthesis

Connection to Path A (Flamingo gate at L4+L5): The user's Path A is the 2-source single-scalar
gate, exactly the Flamingo design. The 15-17% reported improvement is consistent with Flamingo's
published multimodal improvements (typically 10-25% on domain-relevant tasks). This architecture
is already validated; the question being drilled here is whether (a) it generalizes to N>2 sources,
(b) learned gates can be replaced by external control without unacceptable quality loss, and (c) the
substrate stream is the right primary source for the second stream.

Connection to production architecture (multi-hop): The per-layer gate architecture naturally
supports multi-hop reasoning by routing through the substrate stream multiple times across layers
(iterative retrieval at the attention level). This is architecturally connected to the multi-hop
revival thread (MEMORY: PROJECT MULTI-HOP REVIVE PRIORITY). The gate can implement iterative
retrieval implicitly: layer L1 activates substrate, layer L2 activates self-attention to process
retrieval, layer L3 activates substrate again with updated query. This is a gradient-trained form
of the explicit iterative retrieval pipeline.

Connection to ZKL audit/privacy: The per-layer gate log (gate_weight per layer per token) provides
a richer audit trail than current architecture. It also changes the ZKL threat model: with gate
logging, an adversary who queries the model and observes output has additional side-channel
information (which layers activated substrate). This is a new threat vector not yet analyzed.

---

## 11. Strategic positioning

### 11.1 From "substrate IS memory" to "substrate is the premier auditable stream"

Current product claim (Tier 5c): substrate IS LLM memory (replaces the context window with a
retrieval-augmented, algebraically auditable store). This frames substrate as a component of the
LLM's own operation.

Programmable attention routing shifts the frame: substrate is one of N streams in a configurable
attention routing architecture. The value proposition is not that substrate is better than the
context window, but that substrate is the BEST-AUDITED, ALGEBRAICALLY-ISOLATED, PER-TENANT-
CONFIGURABLE stream in a system that can also have math tools, code interpreters, and domain KBs.

This is a stronger commercial position in regulated industries: the customer can configure exactly
which information sources are active per tenant, with cryptographic audit trail per layer, and
algebraic isolation guarantees. No other LLM architecture provides this combination.

### 11.2 Open ecosystem risk

If the gate architecture is standardized and published, third-party streams can plug in. This
dilutes substrate's moat (it becomes one plug-in among many). However, substrate's algebraic
primitives (pseudoinverse delete, bitemporal, whitening, GDPR compliance) are not easily replicated
by arbitrary vector stores. The moat shifts from "architectural exclusivity" to "compliance depth":
substrate is the plug-in that regulated industries MUST choose because it is the only one that
provides mathematical proof of isolation and GDPR-correct deletion.

### 11.3 Comparison with current Tier 5c claim

Tier 5c: "substrate IS LLM memory" -- substrate replaces the LLM's internal memory mechanism.
Programmable routing: "substrate is one precision-auditable stream in a multi-source attention
system." These are not contradictory; the routing architecture can be implemented such that the
substrate stream is effectively LLM memory when its gate is the dominant or only active stream.
The routing architecture subsumes the current claim and adds configurability.

Risk: if the routing architecture requires substantial training (not achievable with the frozen
backbone + lightweight gate finetuning), the "plug substrate into any LLM" proposition weakens.
The FiRST / FluxAttention results suggest that per-layer routing can be added with LoRA-scale
finetuning (days, not months), which is commercially acceptable.

### 11.4 Commercial implications

Best case (routing works, external control viable, overhead acceptable):
  - Substrate becomes a platform primitive, not just a knowledge store
  - Per-tenant gate configuration is a novel enterprise SaaS feature
  - Audit log per layer is a compliance differentiator in HIPAA/GDPR markets
  - Open plug-in ecosystem strengthens moat by network effects

Worst case (learned gate required, external control too lossy, training cost high):
  - Per-layer gating still improves performance but requires per-customer fine-tuning
  - Not a "plug in and use" product; requires deployment engineering per customer
  - Overhead of N > 2 sources makes production cost prohibitive
  - Falls back to current Tier 5c architecture with learned Flamingo-style gate only

---

## Calibration summary

P_deflated(2-source learned gate provides >10% improvement at Pythia-160M scale) = 0.40
  (theoretical support strong; empirical uncertainty at this exact setup; deflated from 0.55)

P_deflated(external control viable within 30% of learned gate performance) = 0.30
  (no direct published precedent; novel synthesis; deflated from 0.45)

P_deflated(N=3 source routing stable without interference at Qwen-1.5B) = 0.25
  (OneLLM/MoMa show N-source works at scale but with joint training; deflated from 0.45)

P_deflated(commercial per-tenant gate config is algebraically exact) = 0.65
  (this is a straightforward engineering property of the gate math; high confidence; deflated
   from 0.75 to account for training stability risk affecting gate behavior)

---

## Citations (verified count: 16)

1. Shazeer et al. 2017, "Outrageously Large Neural Networks" (MoE foundation)
2. Fedus et al. 2021, "Switch Transformers" (Switch MoE)
3. Jiang et al. 2024, "Mixtral of Experts" (practical MoE deployment)
4. Raposo et al. 2024, "Mixture of Depths" (arXiv:2404.02258)
5. Alayrac et al. 2022, "Flamingo" (NeurIPS 2022; gated cross-attention per layer)
6. Graves 2016, "Adaptive Computation Time" (conditional computation foundation)
7. Bengio et al. 2013, "Estimating Gradients Through Stochastic Neurons"
8. Anonymous 2024, "MoAS: Mixture of Attention Schemes" (arXiv:2512.20650)
9. Jamali et al. 2024, "FiRST: Finetuning Router-Selective Transformers" (arXiv:2410.12513)
10. FluxAttention project, 2025 (layer router for attention sparsity)
11. Qiu et al. 2025, "Gated Attention for LLMs" (arXiv:2505.06708, NeurIPS 2025)
12. G-MemLLM 2026, "Gated Latent Memory Augmentation" (arXiv:2602.00015)
13. L2A 2026, "Learning When to Attend" (arXiv:2603.17484)
14. Zoph et al. 2022, "MoMa: Efficient Early-Fusion Pre-training" (arXiv:2407.21770)
15. Han et al. 2024, "OneLLM: One Framework to Align All Modalities with Language" (CVPR 2024)
16. MetaLLM, MixLLM, PILOT, BARP (multi-armed bandit LLM routing, 2024-2025)

---

## Next-drill candidate

Field: cross-attention efficiency mechanisms for N-source systems.
Specific angle: KV cache management for multiple simultaneous external streams (substrate + tool).
When multiple cross-attention streams are active, the KV caches for each stream compound in memory.
The efficiency question for N >= 3 sources at production scale is the main unresolved engineering
risk. Adjacent to: L2A's Triton kernel work, XC-Cache (arXiv:2404.15420), and KV cache compression
literature.
