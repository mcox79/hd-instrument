# Research: PP-8 Phase 2.5 Path 1a — Phi-3-hidden-state-derived codeword design review v1

Date: 2026-06-01
Origin: `notes/strategy_request_to_research_pp8_phi3_hidden_codeword_design_2026-06-01.md` (orchestrator/strategy; HIGH severity; gates Path 1a v1 implementation)
Method: 1 Sonnet drill (~4.5 min, generic VSA/ML terms only, design-pattern + lit-scan); main-thread synthesis

## HEADLINE

**Fixed Gaussian random projection + sign (`k_i = sign(R · h_i)`) is the recommended Path 1a v1 primary method.** Theoretical basis is solid (SimHash / JL lemma; collision probability monotone in cosine similarity); gradient pathway is clean (R fixed → no STE at key-generation); ~25MB R matrix; no new trainable parameters. NVSA (Hersche et al. 2023 Nature MI) is the closest published precedent — neural-to-bipolar direction is demonstrated as enabling end-to-end training. Calibrated P=0.50-0.60 after lit-scan deflation (above pure novel-synthesis due to NVSA precedent).

**Critical pre-flight diagnostic**: compute empirical Gram matrix `K_{ij} = (1/N) k_i · k_j` on projected hidden states BEFORE gradient training. If mean off-diagonal |K_{ij}| > 0.10, apply median-threshold centering. This catches LLM anisotropy / quantization collapse before they corrupt training.

## RECOMMENDED PRIMARY METHOD

**Option A: Fixed Random Projection + Sign**

- `k_i = sign(R · h_i)` where `R ∈ R^{4096 × 3072}` is fixed Gaussian, drawn once at init
- `h_i ∈ R^{3072}` is Phi-3 hidden state at the key-prompt last-token position
- R stored as float16 (~25MB); no new trainable parameters

**Why this resolves Phase 2.5's diagnosed failure mode**: random codewords had no learnable signal connecting "Key N" text to bipolar vector. Derived codewords ARE a deterministic function of `h_i`, so the LLM doesn't need to learn the mapping — only to produce hidden states whose projection retrieves correctly. Much weaker requirement; gradient-tractable.

**Why fixed R is preferred over trainable**: gradient flows through `h_i` (continuous LLM update direction); no second STE through key-generation. Trainable R would add dual STE gradient bias, compounding the issue that caused Phase 2.5 failures.

## ALGEBRAIC STRUCTURE PRESERVATION (Q2 answer)

Under fixed Gaussian R:
- `E[(1/N) k_i · k_j] = 1 - (2/π) arccos(cos θ_{ij})`
- For orthogonal `h_i ⊥ h_j`: expected normalized dot product = 0
- Standard deviation ≈ 1/√N = 0.016 at N=4096 (very tight concentration)

**Caveat (transformer anisotropy)**: Phi-3 hidden states are NOT uniformly distributed on hypersphere (post-LayerNorm anisotropy, Ethayarajh 2019). Derived codewords inherit this anisotropy → systematic positive bias in cross-correlations possible. **Pre-flight Gram-matrix diagnostic catches this.**

**XOR binding compatibility**: substrate's component-wise product binding requires near-orthogonal codewords. Threshold of concern: `|correlation| > 0.05` for memory loads >20% of capacity. Median-threshold centering (subtract empirical median from `R · h_i` before sign) restores balance if anisotropy detected.

## GENERALIZATION THEORY (Q3 answer)

Two mechanisms operate simultaneously:

**Mechanism 1 — Projection smoothness**: `E[d_H(k_i, k_j) / N] = (1/π) arccos(ρ_{ij})`. If LLM generalizes in continuous embedding space (similar prompts → similar hidden states), derived codewords are similar in Hamming sense, and substrate retrieval generalizes.

**Mechanism 2 — LLM embedding geometry inheritance**: LLM already learned that "Key 17" and "Key 18" cluster together (integer sequence structure). Derived codebook inherits this relational structure. Held-out integer keys produce hidden states in same cluster → codewords similar in appropriate ways.

**Calibrated P(generalization works for held-out keys given training pass) ≈ 0.55-0.65** for current toy-task structure (integer sequence with adjacent values). Deflated ~0.10 from base estimate of 0.65-0.75.

**Where generalization fails**: held-out keys outside training distribution in LLM embedding space → derived codewords effectively random relative to training set. Pre-reg requires held-out keys to be semantically DISTINCT from training (not interpolating within sequence).

## PRE-REGISTRATION (Path 1a v1)

**HARD-PASS** (any one sufficient):
- Validation top-1 ≥ 25% (vs ~1% random for 100-key task; 25× lift)
- Validation top-1 ≥ 5× random baseline + maintained across 2 distinct held-out key sets
- Cross-correlation diagnostic: median off-diagonal |K_{ij}| < 0.05 AND ≥90% of pairs < 0.10

**MIDDLE-BAND** (continue with modified design):
- Val top-1 in [5%, 25%) → continue to Full with median-threshold centering (Option D variant)
- Cross-correlations in [0.05, 0.15] → apply threshold-adjustment patch and rerun
- Train ≥ 25% AND val < 5% → generalization gap; prescribes trainable projection (Alternative B)

**HARD-FAIL** (abandon primary; escalate):
- Val top-1 ≤ 2% (below 2× random for 100-key task)
- Cross-correlations >0.30 for >10% of pairs (codebook collapse)
- Train-val gap >40pp (memorization without generalization → structural failure)

**Generalization-to-held-out threshold**:
- Held-out key accuracy ≥ 50% of training-key accuracy; if <50%, Lipschitz argument failing → rescue path = Alternative C (contextual probe)

## ALTERNATIVES (ranked; for orchestrator/strategy/exp_dev sequence decision)

| # | Method | P (deflated) | Eng days | When to use |
|---|---|---|---|---|
| **Primary** | **Fixed random projection + sign** | **0.50-0.60** | **1-2** | **Path 1a v1** |
| Alt A | Fixed R + soft-retrieval proxy with annealing (tanh(β·W·k), β: 2→∞) | 0.45-0.55 | 1-2 | v2 if FM-3 (STE saturation) fires |
| Alt B | Trainable projection + orthogonality regularization | 0.35-0.45 | 3-5 | v3 if v1 MIDDLE-BAND on generalization gap |
| Alt C | Cross-attention probe + projection | 0.30-0.40 | 5-8 | v4 if generalization structure fundamentally wrong |
| (Skip) | VQ-VAE-style learned bipolar quantization | 0.20-0.30 | 5-7 | NOT recommended — three gradient discontinuities compound STE bias |

## SIX DOCUMENTED FAILURE MODES

| FM | Symptom | Diagnostic | Rescue |
|---|---|---|---|
| FM-1 Hidden-state collapse | Empirical Gram >50% of pairs with |K_{ij}|>0.10 | Pre-flight Gram matrix | Probe at different Phi-3 layer (mid-layer higher rank) |
| FM-2 Anisotropy-induced bias | All off-diagonals positive with mean ~0.1-0.2 | Pre-flight Gram matrix | Median-threshold (Option D) or codebook centering |
| FM-3 STE gradient saturation at retrieval | Training loss decreases <0.01/epoch after warmup | Loss curve | Alternative A (soft retrieval proxy with annealing) |
| FM-4 Dimension mismatch / effective rank | Top-1 plateaus at level consistent with ~300-500 effective dims | PCA spectrum of R·h_i | ZCA whitening before sign, OR reduce N |
| FM-5 Train/val task-design leak | Val accuracy matches train (artifactual generalization) | Explicit held-out semantically distinct | Re-design held-out set; pre-reg now requires distinctness |
| FM-6 Quantization × gradient incompatibility | 4-bit Phi-3 substantially worse than full-precision | Full-precision ablation | Full-precision probe layer on top of 4-bit backbone (LoRA-style) |

## NVSA PRECEDENT (load-bearing for P estimate)

Hersche et al. 2023 Nature Machine Intelligence: "Neuro-Vector-Symbolic Architecture for Solving Raven's Progressive Matrices" — neural perception frontend produces structured high-dim vectors compatible with VSA operators. Key claim: neural encoder and VSA reasoner share common representational language. **This is precisely Path 1a's claim**. NVSA uses neural→bipolar direction and demonstrates end-to-end gradient training.

NVSA precedent raises P above pure novel-synthesis territory. Mechanism is demonstrated in adjacent architecture; uncertainty narrows to Phi-3-specific empirical questions (anisotropy, 4-bit quantization, embedding-space structure for integer keys).

## RECOMMENDED SEQUENCE FOR PATH 1A FOLLOW-ON

1. **v1 Fixed projection** (this deliverable) → pre-flight Gram diagnostic → gradient training → pre-reg evaluation
2. **v2 (if FM-3 STE saturation)**: add soft-retrieval annealing (Alt A) — 1-2 eng-days incremental
3. **v3 (if v1 MIDDLE-BAND on generalization)**: trainable projection + orthogonality reg (Alt B) — 3-5 eng-days
4. **v4 (if generalization structure fundamentally wrong)**: cross-attention probe (Alt C) — 5-8 eng-days

If all four fail, Path 1a is structurally infeasible and orchestrator/strategy should evaluate whether to pivot back to Pattern B Anthropic API (PP-9 amortization) as primary substrate-LLM integration story.

## METHOD NOTES

- 1 Sonnet drill (~4.5 min wall, ~33K tokens); generic VSA/ML/SimHash/JL/NVSA terms only — no project-identifying fingerprints
- Per [[feedback-no-experiment-design-in-prompts]]: deliverable is design recommendation + pre-reg bands; specific sweep grids, batch sizes, exact N values for sub-experiments are exp_dev's call
- Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated 0.10-0.20; NVSA precedent narrows uncertainty band but does not eliminate it
- Per [[feedback-strategy-spec-formula-selftests]]: pre-reg bands include concrete numerical thresholds at multiple levels (Gram-matrix, val top-1, generalization gap) — testbed verifies these BEFORE training, not after

## CLOSURE

This research note closes `notes/strategy_request_to_research_pp8_phi3_hidden_codeword_design_2026-06-01.md`. The routing moves to `routed_completed/` with close-note. Testbed / exp_dev picks up the design + pre-reg for Path 1a v1 implementation.

Acted-on 2026-06-01: SimHash + semantic val recommendation adopted; v1+v1' bundle authorized for testbed via strategy_response_to_testbed_pp8_v1_v1prime_authorized
