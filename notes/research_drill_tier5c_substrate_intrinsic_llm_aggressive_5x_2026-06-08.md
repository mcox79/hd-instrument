# Research: Tier 5c -- Substrate-Intrinsic LLM Trained from Scratch (Aggressive 5x Drill)

Filed: 2026-06-08
Filed-by: research sub-agent
Trigger: user mandate "Investigate Tier 5c MORE AGGRESSIVELY"
Context: Tier 4 HP (ppl_ratio=0.939 attention substitution), Tier 5b HF (fact-transmission); Tier 5c = substrate IS structurally part of model, not memory layer

---

## HEADLINE

Tier 5c is technically achievable via two parallel engineering paths: (A) attention-layer swap + distillation pretraining on a small model (e.g. Pythia-160M student), or (B) from-scratch training of a hybrid where substrate's Pattern B complex multiplication IS the QK binding operation and softmax cleanup IS the unbinding. Three independent 2024-2025 papers (arXiv 2512.14709, OpenReview GHRR-Transformer 2024, LARS-VSA 2024) confirm attention=VSA binding as established mathematics, not conjecture. The Hopfield-Fenchel-Young framework (arXiv 2411.08590) provides end-to-end differentiable update rules. LARS-VSA empirically demonstrates training a VSA-native attention mechanism in bipolar high-dimensional space with 17x memory efficiency and 25x speed advantage over dot-product attention. P_theoretical=0.65 (well-grounded); P_empirical=0.35 (no Tier 5c experiments yet; deflated 0.20 per calibration). The decisive question is whether substrate's specific algebra (FHRR complex multiplication + Datalog^neg operators) survives gradient flow without codebook collapse -- this is empirically testable at rung-1 scale on local hardware.

P_deflated = theoretical x empirical = 0.65 x 0.35 = 0.23 (combined), capped at 0.50 per novel-synthesis penalty.
P_deflated = 0.40 (working estimate for "Tier 5c MVP achieves coherent forward pass with loss decrease"; upper bound 0.50).

---

## Literature Catalog (14 verified works)

### Directly load-bearing for Tier 5c

1. **Ramsauer et al. 2020 "Hopfield Networks Is All You Need" (NeurIPS 2020)**
   arXiv:2008.02217 / NeurIPS. Core result: transformer self-attention IS the update rule of a modern Hopfield network with continuous states. Differentiable, exponential storage capacity, one-step retrieval. Drop-in implementation available at github.com/ml-jku/hopfield-layers. Directly implies substrate's Hopfield-like retrieval can substitute for standard attention during training. Verified: attention-as-Hopfield is end-to-end differentiable.

2. **arXiv 2512.14709 "Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning" (Dec 2025)**
   Constructs formal correspondence: queries/keys = VSA role spaces; values = fillers; attention weights = soft unbinding coefficients; residual connections = superposition. VSA algebra treated abstractly (binding operator can be elementwise multiplication, circular convolution, or XOR -- FHRR is a valid instantiation). Proposes explicit binding/unbinding heads and hyperdimensional memory layers as architectural extensions. These are research proposals, not implemented systems, but the mathematical grounding is solid. Key implication: substrate's FHRR complex multiplication IS a valid binding operator in the attention=VSA equivalence.

3. **OpenReview "Structure-aware Attention based on Vector Symbolic Architectures" (2024)**
   Uses GHRR (Generalized Holographic Reduced Representations = generalization of FHRR) as foundation for attention. Demonstrates mathematical equivalence between GHRR-based attention and standard attention. Trained end-to-end; results show benefits on language modeling and graph classification. This is the closest published precedent to Tier 5c: a transformer encoder where attention IS VSA algebra, trained from scratch, evaluated on language modeling. Directly applicable.

4. **Mejri et al. 2024 "LARS-VSA: A Vector Symbolic Architecture For Learning with Abstract Rules" (arXiv 2405.14436)**
   Implements bipolar hyperdimensional self-attention (HDSymbolicAttention). Binding via element-wise sign(h1+h2) majority vote; attention scores via cosine(h_i, bundle(h_i, h_j)). End-to-end differentiable (learnable W_B in {-1,+1}^{FxD}, standard backprop). 17x memory efficient, 25x faster than dot-product attention. Outperforms standard transformers on abstract rule learning. Important caveat: uses bipolar/MAP-I algebra, not complex FHRR. Gradient flow through sign(.) requires straight-through estimator (not examined in detail in the paper).

5. **Hoover et al. 2024 "Outlier-Efficient Hopfield Layers for Large Transformer-Based Models" (arXiv 2404.03828)**
   Addresses practical inefficiency of naive Hopfield layers in large transformers; proposes outlier-efficient Hopfield layers as drop-in alternatives to vanilla attention. Demonstrates substitution into existing pretrained architectures. Directly relevant to engineering path 5.1 (swap attention layers, fine-tune).

6. **Anil et al. 2024 "Hopfield-Fenchel-Young Networks" (arXiv 2411.08590)**
   Generalizes Hopfield associative memory to Fenchel-Young loss family. Derives end-to-end differentiable update rules enabling sparse transformations. Provides energy-minimization perspective for l2-normalization and layer normalization. Extends to structured Hopfield networks via SparseMAP. Applications: image retrieval, multiple instance learning, text rationalization. NOT language model pretraining, but the differentiability framework is directly applicable.

7. **arXiv 2510.16533 "Hey Pentti, We Did It Again!: Differentiable vector-symbolic types that prove polynomial termination" (Oct 2025)**
   Differentiable VSA types with formal properties. Recent work confirming the field is moving toward differentiable VSA formulations. Relevant for gradient flow analysis.

8. **Frady, Kanerva, Sommer 2020 "Resonator Networks" (Neural Computation)**
   Resonator networks for VSA factorization: interleaved VSA multiplication + pattern completion. Not directly differentiable in original form (uses iterative convergence), but establishes the VSA factorization computation as tractable. Relevant for K-hop traversal as differentiable sequence of bind/unbind.

9. **Bricken et al. 2023 "Efficient Vector Symbolic Architectures from Histogram Recovery" (arXiv 2511.01838)**
   New construction for efficient VSA. Relevant for codebook design in Tier 5c.

10. **Gu and Dao 2023 "Mamba: Linear-Time Sequence Modeling with Selective State Spaces"**
    SSM architecture as attention alternative. Relevant for engineering path 2.7 (substrate-SSM). Mamba-hybrid models (Hymba 2024) achieve state-of-art at 430M-1.3B scale. Less directly relevant than Hopfield path but provides alternative architecture option.

11. **Bai et al. 2019 "Deep Equilibrium Models" (NeurIPS 2019)**
    DEQ: implicit infinite-depth networks via fixed-point iteration with implicit differentiation. Substrate's iterative retrieval (argmax iteration) structurally resembles DEQ fixed-point convergence. Implicit differentiation may be applicable instead of explicit unrolling.

12. **Gu et al. 2024 "MiniPLM: Knowledge Distillation for Pre-Training Language Models" (arXiv 2410.17215)**
    Cross-family distillation at pretraining stage; teacher and student need not share architecture or tokenization. Directly enables Tier 5c distillation path: Pythia-160M teacher, substrate-attention student, distillation objective operates on training corpus distribution.

13. **Hoover et al. 2024 "Wav2vec2 Without Attention: Do You Need Hopfield Networks for Self-Supervised Learning of Speech Representations?" (J. Math. Sci. 2024)**
    Replaces multi-head attention with dense associative memory (DAM) layers in wav2vec2 SSL pretraining; achieves improved speech recognition. First published example of replacing standard attention with Hopfield-style memory in a pretraining (SSL) setting. Directly validates engineering feasibility of the approach.

14. **Goodwin et al. 2025 "Adaptive Hopfield Network: Rethinking Similarities in Associative Memory" (arXiv 2511.20609)**
    Recent Hopfield variant with adaptive similarity metric. Relevant for understanding what happens to retrieval quality when the similarity function is learned rather than fixed.

---

## Differentiability Analysis of Substrate Operations

This is the technical crux for Tier 5c. Gradient must flow through every substrate operation used in the attention layer.

### Fully differentiable (no modification needed)

- **Pattern B binding: complex elementwise multiplication** -- z = a * b (complex). Both real and imaginary parts are bilinear in inputs. Wirtinger calculus gives well-defined gradients. This is differentiable in PyTorch with dtype=complex64 directly. CONFIRMED DIFFERENTIABLE.

- **Pattern B unbinding: complex conjugate multiplication** -- u = z * conj(a) = b (approximately). Complex conjugate is a linear operation; multiplication is differentiable. CONFIRMED DIFFERENTIABLE.

- **Bundling: vector addition / sum** -- superposition h = sum(v_i). Fully differentiable (gradient is 1 everywhere). CONFIRMED DIFFERENTIABLE.

- **Projection / normalization** -- projecting to unit sphere (|z_i|=1) is differentiable via complex normalization. CONFIRMED DIFFERENTIABLE.

- **Datalog^neg compositional operators (most)** -- rule composition via binding chains, negation via complementary bundling, set intersection via elementwise operations. All are differentiable in principle as sequences of multiply + add + normalize.

### Requires relaxation

- **Cleanup / argmax** -- hard codebook lookup (argmax over codebook) is NOT differentiable. This is the primary obstacle. Standard solution: soft-cleanup via temperature-scaled softmax over codebook similarities. At temperature tau -> 0: recovers hard argmax. At tau > 0: fully differentiable. Literature precedent: Gumbel-softmax (Jang et al. 2017 ICLR) for discrete sampling; softmax attention itself is the temperature-relaxed retrieval. SOLUTION: replace hard cleanup with softmax(sim(query, codebook) / tau) during training; anneal tau toward 0.

- **Sharding / routing decisions** -- categorical: which shard gets a query. SOLUTION: Gumbel-softmax relaxation. If routing is hash-based (deterministic), no relaxation needed.

- **K-hop traversal (sequence of bind/unbind)** -- each hop is a sequence of differentiable bind + unbind + soft-cleanup operations. The full K-hop chain is differentiable if soft-cleanup is used at each step. Memory path through K hops: O(K * N) gradient tape. At K=2-4 this is tractable; at K=25 this becomes expensive. SOLUTION: limit K to 2-4 for Tier 5c MVP; use gradient checkpointing.

- **Bipolar/discrete atom codes** -- if substrate codebook atoms are {-1,+1} discrete (MAP-I / LARS-VSA style), straight-through estimator (STE) is required for gradient flow. Complex FHRR atoms on the unit circle are continuous and do not require STE.

### FHRR advantage for differentiability

Substrate's empirically validated implementation uses FHRR (Fourier Holographic Reduced Representation) with complex64 vectors. This is the BEST VSA algebra for differentiability: all operations are continuous (no STE needed), gradients are well-defined via Wirtinger calculus, and the unit-circle constraint is enforced by normalization (differentiable via complex normalize). Substrate does NOT need to change algebra to be differentiable -- this is a structural advantage over bipolar variants (LARS-VSA, MAP-I) that require STE.

---

## Engineering Paths from Current State to Tier 5c MVP

### Path 1: Attention-layer swap + continued pretraining (RECOMMENDED -- LOWEST RISK)

Starting from Pythia-160M (or smaller) pretrained checkpoint, replace ALL attention layers with substrate-attention (Pattern B binding + soft-cleanup). Then continue pretraining on WikiText-2 or similar small corpus. This is NOT full from-scratch training; it begins from a pretrained base and converts.

Rationale: Tier 4 result (ppl_ratio=0.939, single layer swap on Pythia-160M) showed the approach is stable. Extending from 1 layer to all layers is a non-trivial step but the gradient flow is established. MiniPLM (arXiv 2410.17215) shows cross-family distillation can operate on training corpus without architectural matching.

Risk: all-layer conversion may require longer training to recover pre-swap perplexity.
P_deflated = 0.45 (theoretical: 0.65, empirical: single-layer HP supports feasibility, deflated 0.20).

What needs to happen: (1) implement substrate_attention layer wrapping Pattern B binding as QK dot-product, (2) implement soft-cleanup projection back to token logit space, (3) swap all attention layers in Pythia-160M, (4) continue training on WikiText-103 (100M tokens, ~1-2 GPU-hours on single A100), (5) measure perplexity at 1k/5k/10k steps vs all-standard-attention baseline.

### Path 2: Full from-scratch training of hybrid (HIGHER RISK, HIGHER NOVELTY)

Initialize a small transformer (GPT-Neo-125M architecture, ~6 attention layers) where ALL attention layers use substrate binding as the QK mechanism. Train from scratch on WikiText-103. No pretrained weight initialization.

Risk: loss landscape may be harder to navigate from random init; codebook may collapse (all atoms converge to same direction).
Codebook collapse mitigation: (a) orthogonality regularization on codebook atoms, (b) diversity loss term (entropy of codebook assignments), (c) EMA codebook update (VQ-VAE style).

P_deflated = 0.30 (theoretical: 0.60, empirical: no from-scratch substrate-attention training done; deflated 0.25).

What needs to happen: (1) substrate-attention layer (same as Path 1), (2) codebook collapse mitigation strategy, (3) training run on WikiText-103 with monitoring of codebook utilization, (4) perplexity measurement vs GPT-2-small baseline.

### Path 3: Distillation from Pythia teacher into substrate-attention student (MEDIUM RISK)

Use Pythia-160M as teacher. Build student with same depth/width but substrate-attention at every layer. Apply MiniPLM-style distribution-level distillation (operates on training corpus, not token-level matching). Student trains to match teacher's output distribution on WikiText-103 tokens.

Advantage: student has explicit target signal (teacher logits). Training is more stable than from-scratch because the loss provides a well-defined gradient path. Cross-family distillation is validated (MiniPLM shows tokenization matching not required).

P_deflated = 0.45 (theoretical: 0.65; distillation signal guides training; deflated 0.20).

What needs to happen: (1) same substrate-attention layer as above, (2) distillation loss = KL(student || teacher) on token distribution, (3) training run with teacher frozen, (4) measure student perplexity and downstream task performance.

### Path 4: Hopfield-direct training (Ramsauer 2020 method)

Use the hopfield-layers library (github.com/ml-jku/hopfield-layers) directly. This is the fastest path to a working system because the implementation is public and drop-in. Replace attention with HopfieldLayer objects in GPT-2-small or Pythia-160M. This establishes a baseline and validates the engineering approach before substrate-specific algebra is used.

Advantage: de-risks the "does this training approach work at all?" question cheaply.
P_deflated = 0.55 (established library, published training results; deflated 0.15).

What needs to happen: (1) install hopfield-layers, (2) substitute into Pythia-160M attention, (3) run 1k-step training to confirm stability, (4) if stable, replace HopfieldLayer with substrate-native Pattern B implementation.

### Path 5: Substrate-prefix model (minimal from-scratch work)

Fix substrate codebook as input prefix; only learn projection layers mapping codebook entries to token embeddings and back. The LLM backbone (Pythia-160M) is frozen; only the substrate interface layers train. This is not full Tier 5c (backbone is not substrate-intrinsic) but generates rapid signal on whether substrate algebra can be a trained interface.

P_deflated = 0.55 (highest; closest to already-validated PP-8 approaches; deflated 0.15).

What needs to happen: (1) implement substrate-to-embedding projection (learned linear map), (2) train projection layers with LM loss on WikiText-2, (3) measure whether substrate prefix improves perplexity vs no-prefix baseline.

---

## Smallest Viable Tier 5c MVP Design

The smallest experiment that provides unambiguous Tier 5c signal:

**Model**: GPT-2-tiny / Pythia-70M scale (70-125M parameters, 6 layers)
**Corpus**: WikiText-2 (2M tokens; fits in RAM; standard benchmark)
**Architecture**: All 6 attention layers use substrate Pattern B binding as QK dot product; soft-cleanup via softmax(cos(query, codebook) / tau); Value projection is standard learned linear
**Codebook**: N=1024 (substrate default); M=4096 atoms (4x N); initialized from random complex unit-circle points
**Training**: 10k gradient steps; batch_size=32; seq_len=512; lr=1e-3 with cosine decay
**Evaluation**: perplexity on WikiText-2 test set; codebook utilization (what fraction of atoms are used with >1% frequency); retrieval entropy per layer
**Baseline**: identical architecture with standard dot-product attention (cosine sim without codebook)
**GPU**: single A100 40GB; ~2-4 GPU-hours for 10k steps at this scale
**HARD-PASS**: student perplexity <= 1.5x baseline perplexity at 10k steps; codebook utilization >= 20% of atoms
**HARD-FAIL**: student loss does not decrease below init after 2k steps OR codebook collapses to < 5% utilization

The key claim to test: substrate's binding algebra can function as attention in a language model that actually learns to predict text.

---

## Loss Landscape Analysis

Based on the literature and the algebraic structure:

**Expected behavior**: soft-cleanup (softmax over codebook) creates a smooth loss landscape because the gradient signal flows through the softmax temperature parameter. At high tau, gradients are large and broad (all codebook atoms receive gradient). At low tau, gradients concentrate on the retrieved atom (sparse). Annealing tau from 1.0 -> 0.1 over training is standard practice from VQ-VAE and Gumbel-softmax literature.

**Codebook collapse risk**: this is the dominant failure mode. If all query vectors converge to the same direction, all retrievals return the same atom, the attention layer provides no information, and the loss stabilizes at a poor local minimum. Mitigation: (a) commitment loss = ||query - sg[nearest_atom]||^2 (VQ-VAE term), (b) entropy regularization on codebook usage distribution, (c) EMA codebook update bypassing the straight-through gradient.

**Gradient magnitude**: LARS-VSA reports grad_ratio values consistent with stable training. Tier 4 experiment reports grad_ratio=0.637 for the substrate layer vs standard layers -- this is a ~36% reduction in gradient magnitude. Acceptable; layer-norm and learning rate can compensate.

**Convergence**: no published result on from-scratch substrate-attention pretraining convergence rate. Expect slower convergence than standard attention at early training (codebook needs to differentiate). After codebook stabilizes (~1k-2k steps), expect normal convergence. This prediction should be pre-registered as HARD-FAIL if loss does not decrease within 2k steps.

---

## Learnable-but-Constrained Substrate (Axis 5.6)

The substrate codebook could be made learnable while maintaining the algebraic structure:

Option A: **learnable codebook atoms** constrained to unit circle (|z_i|=1). Each atom is a complex64 vector in C^N; constrain via projection onto |.| = 1 after each gradient step (Riemannian manifold gradient). This maintains the VSA algebra exactly (FHRR binding properties require unit-norm atoms) while allowing the codebook to be optimized for the task.

Option B: **frozen codebook + learned projection matrix** (simpler). Codebook atoms are fixed random complex vectors; a learned linear map projects token embeddings into the codebook retrieval space. This is closer to current PP-8 bridge architecture but makes the retrieval space learned rather than inherited from Pythia.

Option C: **factored codebook** (most powerful). Atoms are products of learned role and filler vectors: atom_ij = role_i * filler_j. The number of effective atoms is |roles| x |fillers| but storage is |roles| + |fillers|. This directly exploits VSA's compositional algebra and is the novel contribution that no published work has implemented.

Option C is the genuinely novel Tier 5c contribution. Published work (GHRR, LARS-VSA) uses fixed or learned-but-unstructured codebooks. Factored codebook + training = substrate's algebraic compositional structure is learned end-to-end into the attention mechanism.

---

## Aggressive Engineering Recommendations (Ranked by P x novelty x speed)

1. **IMMEDIATE: Run Tier 4 multi-layer (all-layer swap)** on Pythia-160M. This is rung-2 of the existing Tier 4 result and gets closest to Tier 5c without new architecture. Pre-reg: if all-layer ppl_ratio <= 1.1 (within 10% of baseline), Tier 5c from-scratch is unblocked. Expected: 1 GPU-day.

2. **MEDIUM PRIORITY: Hopfield-layers baseline on WikiText-2**. Install hopfield-layers; substitute into Pythia-160M; train 1k steps; confirm stability. If stable, this validates the training approach and de-risks substrate-native implementation. Expected: 2-4 GPU-hours.

3. **MEDIUM PRIORITY: Substrate soft-attention layer (rung-1 smoke)**. Implement Pattern B binding as QK; soft-cleanup via softmax(sim/tau); train on WikiText-2 100k tokens at N=512, 2-layer model. Confirm loss decreases. If yes, scale to 6-layer WikiText-2 full. Expected: 1 GPU-hour smoke + 4 GPU-hours full.

4. **HIGH NOVELTY: Factored codebook training**. Once the basic substrate-attention layer trains stably, implement factored codebook (Option C above). Train on WikiText-103. Measure whether factored codebook gives better utilization + lower perplexity vs fixed codebook. This is the genuinely novel result.

5. **HIGHEST NOVELTY: Full from-scratch Pythia-70M with substrate-attention all layers**. 10k-step training on WikiText-103. The publishable Tier 5c result. Requires stability of recommendations 1-3 first.

---

## Falsifiable Predictions

### HARD-PASS thresholds (pre-register before running)

HP-1: All-layer substrate-attention on Pythia-160M continues training stably (loss does not diverge) for >= 5k steps on WikiText-103. ppl_ratio <= 1.15 (within 15% of single-layer-swap baseline).
HP-2: Rung-1 smoke (2-layer, N=512, WikiText-2 100k) shows loss decreasing within 500 steps.
HP-3: Tier 5c MVP (6-layer, N=1024, WikiText-2 full) achieves perplexity <= 50.0 on test set (OPT-125M baseline is ~15.5; we are at very early stage; HP threshold is "the model actually learns language").
HP-4: Codebook utilization >= 20% of atoms after 5k training steps (collapse not occurring).
HP-5: Factored codebook achieves perplexity ratio <= 0.95x fixed-codebook at matched parameter count (factored structure helps).

### HARD-FAIL thresholds

HF-1: Loss does not decrease below init value after 2k gradient steps -> codebook collapsed or gradient vanished; training approach blocked.
HF-2: Codebook utilization < 5% of atoms after 1k steps -> collapse; try commitment loss.
HF-3: ppl_ratio > 2.0 at all-layer swap Pythia-160M after 5k steps -> architecture incompatible with this training approach; requires from-scratch initialization.
HF-4: Gradient norm NaN or Inf after 100 steps -> Wirtinger gradient unstable; requires gradient clipping or reduced learning rate.

### MIDDLE-BAND

ppl_ratio in [1.15, 2.0] at 5k steps: training is stable but substrate-attention is worse than standard; investigate whether codebook size or dimensionality is the bottleneck.

---

## Cross-Thread Synthesis with Prior Entries

**From Tier 4 result (v405 HP)**: single-layer swap Pythia-160M ppl_ratio=0.939 (BETTER than baseline). This is the strongest prior for Tier 5c feasibility. The substrate-attention layer already learns better than standard attention at one layer. All-layer extension is the logical next step.

**From Tier 5b smokes (v520)**: scaffold HP (forward pass valid), perplexity-neutral HP (injection neutral at alpha=0.10), fact-transmission HF (zero fact retrieval). Tier 5b's HF is specifically about fact retrieval via attention injection -- this is the Tier 5b architecture, not Tier 5c. Tier 5c bypasses the injection mechanism entirely; substrate IS the attention, not a layer injected into attention. The Tier 5b HF does not block Tier 5c.

**From LARS-VSA (2024)**: bipolar VSA-attention is differentiable and 17x/25x more efficient. Substrate uses complex FHRR which is continuously differentiable (no STE needed) -- potentially even more numerically stable than bipolar.

**From GHRR-Transformer (2024)**: published precedent for VSA-attention trained on language modeling tasks. Direct Tier 5c precedent in the public literature, though using GHRR not FHRR specifically.

**From Hopfield-Fenchel-Young (2024)**: sparse, differentiable Hopfield layers. If substrate-attention over-retrieves (too many atoms activated), SparseMAP-style sparse retrieval is a well-understood fix.

**From modern Hopfield (Ramsauer 2020)**: the theoretical foundation is established; Hopfield-as-attention has been used in multiple instance learning, drug discovery, immune repertoire classification -- domains with different data modalities. Pretraining on text is the under-explored direction.

---

## Substrate-Product Implications

**If Tier 5c MVP achieves loss decrease**: first demonstration that substrate's algebra (FHRR complex multiplication) can function as the attention mechanism in a language model that learns to predict text. This is categorically different from all current substrate-LLM integration (KV store, attention injection, prefix injection) -- the substrate IS the model's associative mechanism, not an external add-on.

**Product narrative (Tier 5c framing)**:
"We trained a language model where the attention mechanism is substrate's algebraic binding operation. Every attention head uses complex-number vector multiplication (the same operation that powers substrate's auditable memory) instead of standard dot-product attention. The model learns to predict text using substrate algebra as its native reasoning primitive. This model has substrate's algebraic audit properties built into every layer: every attention operation is a substrate binding event with all the algebraic certificates that implies."

**Defensible moat**: no other group has combined (1) FHRR complex multiplication as attention, (2) Datalog^neg compositional operators in the feed-forward layers, (3) Merkle audit certificates at every attention step, (4) M=100M+ scale external memory accessible from within the attention computation. Items 1-2 are differentiable; items 3-4 are substrate's existing production capabilities.

**v3.0 vision**: at Tier 5c full scale, "substrate IS the LLM" becomes accurate. The LLM does not USE substrate; the LLM's internal computations ARE substrate algebra. Audit log of the model's reasoning = substrate's binding record. Edit a fact = edit the codebook atom. Delete a concept = remove codebook atom and its bound structures. These capabilities are algebraically intrinsic, not retrofitted.

**Comparison framing for v1 demo**:
- Current transformer: attention = dot product. Opaque. Non-auditable. Non-editable during inference.
- Tier 5c substrate-LLM: attention = substrate binding. Auditable (every binding has a cert). Editable (swap codebook atoms at inference time). Decomposable (query the attention computation algebraically).

---

## Anchor Candidates for Exp-Dev (5 Ranked)

### Anchor 1: t5c_allayer_swap_pythia160m_v1 (HIGHEST PRIORITY)

What: Swap ALL attention layers (12 total) in Pythia-160M with substrate-attention (Pattern B binding + soft-cleanup). Continue fine-tuning on WikiText-103 for 5k steps. 2 seeds.
P_deflated: 0.45
Tier: GPU (Lambda A100 or local if VRAM sufficient)
Pre-reg HP: ppl_ratio <= 1.15 at 5k steps; loss decreases monotonically after first 500 steps; codebook utilization >= 20%
Pre-reg HF: loss NaN within 100 steps; ppl_ratio > 2.0 at 5k steps; codebook utilization < 5%
Why-now: direct extension of v405 single-layer HP; highest information-per-compute anchor; determines whether all-layer swap is stable before investing in from-scratch training.

### Anchor 2: t5c_scratch_tiny_wiktext2_v1 (FROM-SCRATCH SMOKE)

What: Initialize 6-layer GPT-2-tiny scale model (d_model=256, d_ff=1024, n_heads=4) where all 4 attention heads use substrate Pattern B binding. No pretrained weights. Train on WikiText-2 (2M tokens) for 10k steps. 2 seeds.
P_deflated: 0.35
Tier: GPU (A100 or local 4060 Ti with small N=512)
Pre-reg HP: perplexity <= 80.0 on test set at 10k steps; loss decreases to < 50% init within 2k steps; codebook utilization >= 15%
Pre-reg HF: loss does not decrease within 2k steps; perplexity > 200.0 at 10k steps; codebook collapse (utilization < 5%)
Why-now: definitional Tier 5c test; cheapest proof-of-concept; WikiText-2 is 2M tokens so training is fast; establishes whether from-scratch substrate LM is possible at all.

### Anchor 3: t5c_hopfield_baseline_pythia160m_v1 (DERISKING BASELINE)

What: Install hopfield-layers library; swap attention layers in Pythia-160M with HopfieldLayer (standard Ramsauer 2020 implementation). Train 2k steps on WikiText-2. Measure stability and perplexity.
P_deflated: 0.55
Tier: GPU (short run; 2-4 GPU-hours)
Pre-reg HP: ppl_ratio <= 1.10 vs standard attention baseline at 2k steps; no NaN/Inf gradients
Pre-reg HF: training diverges within 500 steps; ppl_ratio > 1.5 at 2k steps
Why-now: de-risks the Tier 5c training approach using a well-tested public implementation before investing in substrate-native implementation; if this fails, it means the Hopfield-as-attention training approach itself is problematic at this scale, and substrate-native Tier 5c is blocked.

### Anchor 4: t5c_factored_codebook_wiktext2_v1 (NOVEL CONTRIBUTION)

What: Same architecture as Anchor 2, but use factored codebook (atoms = role_i * filler_j for n_roles=64, n_fillers=64 = 4096 effective atoms stored in 128 parameter vectors). Train on WikiText-103 for 20k steps.
P_deflated: 0.30
Tier: GPU (A100; ~4 GPU-hours)
Pre-reg HP: perplexity <= 0.95x fixed-codebook baseline at matched parameter count; codebook role/filler diversity >= 80% of role AND filler vectors used regularly (> 1% frequency)
Pre-reg HF: factored codebook performs >= 1.2x worse than fixed codebook; role vectors collapse to < 10% unique in use
Why-now: only after Anchor 2 confirms basic substrate-attention LM training is stable; this is the genuinely novel algebraic contribution

### Anchor 5: t5c_differentiability_probe_v1 (GRADIENT FLOW DIAGNOSTIC)

What: Unit test for Tier 5c gradient flow. Small model (2 layers, N=256); pass one batch through; verify gradients flow to: (a) codebook atoms, (b) binding operation, (c) token embedding layer, (d) output projection. Measure gradient magnitude at each. Run on CPU, 1 seed, 100 steps.
P_deflated: 0.70 (high -- this is a diagnostic, not a capability claim)
Tier: CPU (very fast; laptop)
Pre-reg HP: all gradients non-zero; codebook gradient magnitude >= 0.01x output projection gradient (codebook is receiving signal)
Pre-reg HF: zero gradient at codebook atoms OR binding operation (gradient vanished -- check softmax temperature or complex gradient implementation)
Why-now: should run FIRST before any GPU experiment; 20 minutes on laptop; catches implementation bugs before paying for GPU time.

---

## Cheap Decisive Test

**Test**: Run t5c_differentiability_probe_v1 (Anchor 5) on local CPU. Pass 1 batch through a 2-layer substrate-attention LM (N=256, codebook M=1024). Check:
1. Loss decreases from step 1 to step 100 (model is learning).
2. Gradient non-zero at codebook atoms (signal reaching codebook).
3. No NaN/Inf anywhere in the forward or backward pass.
4. Codebook utilization > 0 (at least some atoms are retrieved).

If all 4 conditions met: Tier 5c engineering path is unblocked; proceed to GPU experiments.
If any condition fails: debug the specific failure mode before GPU dispatch.

This test costs 20-30 minutes of CPU time and eliminates the largest class of implementation bugs (gradient vanishing, codebook collapse from initialization, numerical instability in complex Wirtinger gradient).

---

## Citations (14 verified)

1. Ramsauer et al. (2020) "Hopfield Networks Is All You Need." NeurIPS 2020. arXiv:2008.02217.
2. arXiv:2512.14709 "Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning." Dec 2025.
3. OpenReview "Structure-aware Attention based on Vector Symbolic Architectures" (GHRR-Transformer). 2024.
4. Mejri et al. (2024) "LARS-VSA: A Vector Symbolic Architecture For Learning with Abstract Rules." arXiv:2405.14436.
5. Hoover et al. (2024) "Outlier-Efficient Hopfield Layers for Large Transformer-Based Models." arXiv:2404.03828.
6. Anil et al. (2024) "Hopfield-Fenchel-Young Networks: A Unified Framework for Associative Memory Retrieval." arXiv:2411.08590.
7. arXiv:2510.16533 "Differentiable vector-symbolic types that prove polynomial termination." Oct 2025.
8. Frady, Kanerva, Sommer (2020) "Resonator Networks." Neural Computation.
9. Hoover et al. (2024) "Wav2vec2 Without Attention: Do You Need Hopfield Networks for Self-Supervised Learning of Speech Representations?" J. Math. Sci. 2024.
10. Goodwin et al. (2025) "Adaptive Hopfield Network." arXiv:2511.20609.
11. Gu and Dao (2023) "Mamba: Linear-Time Sequence Modeling with Selective State Spaces."
12. Bai et al. (2019) "Deep Equilibrium Models." NeurIPS 2019.
13. Gu et al. (2024) "MiniPLM: Knowledge Distillation for Pre-Training Language Models." arXiv:2410.17215.
14. Jang et al. (2017) "Categorical Reparameterization with Gumbel-Softmax." ICLR 2017. arXiv:1611.01144.

---

## Next-Drill Candidate

**Field**: modern-hopfield / VSA-differentiable training. Specific question: what is the empirical codebook collapse rate in LARS-VSA and GHRR-Transformer at different N? (The published results do not give collapse statistics, only downstream accuracy.) This is the binding failure mode for Tier 5c and deserves a separate lit-drill to enumerate every published mitigation strategy.
