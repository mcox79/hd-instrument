# exp_dev hand-off -- research: Tier 5c substrate-intrinsic LLM aggressive 5x drill

Filed-by: research sub-agent (2026-06-08)
Trigger: notes/research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Tier 5c = substrate IS structurally part of the LLM's attention mechanism; not a memory
layer or injected prefix. The current empirical frontier is Tier 4 (single-layer attention
substitution on Pythia-160M, ppl_ratio=0.939 HARD_PASS v405) and Tier 5b (scaffold + 
perplexity-neutral smokes PASS; fact-transmission HF v520).

Three independent 2024-2025 papers confirm attention=VSA binding as established
mathematics: GHRR-Transformer (2024) trains VSA-attention on language modeling;
LARS-VSA (2024) achieves 17x/25x efficiency with bipolar VSA-attention;
Hopfield-Fenchel-Young (2024) provides end-to-end differentiable Hopfield update rules.

Substrate's FHRR complex multiplication is the BEST algebra for differentiability
(continuously differentiable via Wirtinger calculus; no straight-through estimator
needed; unit-circle constraint enforced by normalization). This is a structural
advantage over bipolar VSA variants in the published literature.

Critical blockers to test first:
- Gradient flow through complex FHRR binding in training context (probe anchor)
- Codebook collapse (all atoms converge to same direction) -- dominant failure mode
- Training stability under all-layer swap (Tier 4 was single-layer only)

Sequence: diagnostic probe -> all-layer swap on pretrained -> from-scratch smoke -> 
novelty tier (factored codebook).

---

## Anchor Candidates (rank-ordered by P_actionable x prerequisite order)

### 1. t5c_differentiability_probe_v1 (MUST RUN FIRST; CPU; 20-30 min)

Anchor pointer: t5c_differentiability_probe_v1 (new; not yet queued)
Substrate-product reading: Verifies gradient flow through complex FHRR binding in a
  2-layer substrate-attention LM. If gradients reach the codebook atoms, Tier 5c
  training is unblocked. If zero/NaN gradients: diagnose before any GPU spend.
Tier hint: CPU laptop; ~20-30 min wall; no GPU needed
Why-now: eliminates implementation bugs before any GPU dispatch; cheapest gate.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: loss decreases step 1->100; all gradients non-zero; no NaN/Inf; codebook
    utilization > 0 (at least some atoms retrieved)
  HARD-FAIL: zero gradient at codebook OR NaN/Inf in forward/backward pass
  MID-BAND: gradients non-zero but codebook gradient < 0.001x output projection gradient
    (signal reaching codebook but very weak; increase tau or learning rate)

Architecture spec (research recommendation):
  2 layers, N=256, codebook M=1024, soft-cleanup via softmax(cos(q, atoms)/tau) tau=1.0,
  batch_size=4, seq_len=64, 100 gradient steps, WikiText-2 tokenized data

### 2. t5c_allayer_swap_pythia160m_v1 (HIGHEST PRIORITY GPU; runs after Anchor 1 PASS)

Anchor pointer: t5c_allayer_swap_pythia160m_v1 (new; not yet queued)
Substrate-product reading: All 12 attention layers in Pythia-160M swapped to substrate
  Pattern B binding. Continued fine-tuning on WikiText-103 5k steps. This is the
  direct rung-2 follow-on to v405 single-layer HP. If stable: Tier 5c pathway confirmed
  open from pretrained baseline. If diverges: all-layer swap requires from-scratch init.
Tier hint: GPU (A100 40GB; ~4-8 GPU-hours; Lambda Cloud or local if VRAM)
Why-now: highest-information GPU anchor; builds directly on v405 evidence; 2 seeds.

Pre-reg bands:
  HARD-PASS: ppl_ratio <= 1.15 at 5k steps; loss decreases after first 500 steps;
    codebook utilization >= 20% of atoms; no training divergence
  HARD-FAIL: loss NaN within 100 steps; ppl_ratio > 2.0 at 5k steps; codebook
    utilization < 5% at 2k steps
  MID-BAND: ppl_ratio in [1.15, 2.0] at 5k steps; training stable but substrate-
    attention underperforms standard attention at all-layer scale

### 3. t5c_hopfield_baseline_pythia160m_v1 (DERISKING BASELINE; parallel to Anchor 2)

Anchor pointer: t5c_hopfield_baseline_pythia160m_v1 (new; not yet queued)
Substrate-product reading: Uses hopfield-layers library (github.com/ml-jku/hopfield-layers)
  to swap Pythia-160M attention layers. Runs 2k steps on WikiText-2. This derisks the
  training approach using a well-tested public implementation before substrate-native
  code. If HopfieldLayer training is unstable at this scale: the Hopfield-as-attention
  training approach itself is the blocker, not substrate-specific code.
Tier hint: GPU (A100; ~2-4 GPU-hours); requires hopfield-layers pip install
Why-now: cheap insurance; runs in parallel with Anchor 2 if GPU available.

Pre-reg bands:
  HARD-PASS: ppl_ratio <= 1.10 at 2k steps; no NaN/Inf gradients
  HARD-FAIL: training diverges within 500 steps; ppl_ratio > 1.5 at 2k steps
  MID-BAND: ppl_ratio in [1.10, 1.50] at 2k steps; stable but underperforms

### 4. t5c_scratch_tiny_wikitext2_v1 (FROM-SCRATCH SMOKE; after Anchors 1+2)

Anchor pointer: t5c_scratch_tiny_wikitext2_v1 (new; not yet queued)
Substrate-product reading: 6-layer GPT-2-tiny scale model (d_model=256, d_ff=1024,
  n_heads=4) where ALL attention heads use substrate Pattern B binding. No pretrained
  weights. Train on WikiText-2 (2M tokens) for 10k steps. Definitional Tier 5c test:
  LLM trained from scratch with substrate attention. 2 seeds.
Tier hint: GPU (A100; ~2-4 GPU-hours at small scale)
Why-now: only after Anchors 1 and 2 confirm gradient flow and training stability;
  from-scratch requires more steps to converge than fine-tuning.

Pre-reg bands:
  HARD-PASS: perplexity <= 80.0 on test set at 10k steps; loss decreases to < 50%
    of init within 2k steps; codebook utilization >= 15%
  HARD-FAIL: loss does not decrease within 2k steps; perplexity > 200.0 at 10k steps;
    codebook collapse (utilization < 5%)
  MID-BAND: perplexity in [80.0, 200.0] at 10k steps; model learns but underperforms
    standard-attention baseline at same scale

### 5. t5c_factored_codebook_wikitext103_v1 (NOVEL CONTRIBUTION; after Anchor 4 PASS)

Anchor pointer: t5c_factored_codebook_wikitext103_v1 (new; not yet queued)
Substrate-product reading: Same as Anchor 4 architecture but with factored codebook:
  atoms = role_i * filler_j (complex FHRR multiplication) for n_roles=64, n_fillers=64.
  4096 effective atoms stored in 128 parameter vectors (n_roles + n_fillers).
  Train on WikiText-103 for 20k steps. Measures whether substrate's compositional
  algebra (learned factored codebook) improves over fixed or unstructured codebook.
  This is the genuinely novel Tier 5c contribution not in any published work.
Tier hint: GPU (A100; ~4-8 GPU-hours)
Why-now: only after Anchor 4 confirms basic substrate-attention LM training is stable;
  factored codebook is the structural novelty of this architecture.

Pre-reg bands:
  HARD-PASS: perplexity <= 0.95x fixed-codebook baseline at matched parameter count;
    codebook role AND filler diversity >= 80% of vectors used regularly (>1% frequency)
  HARD-FAIL: factored codebook performs >= 1.2x worse than fixed codebook; role vectors
    collapse to < 10% unique in use
  MID-BAND: perplexity within [0.95x, 1.20x] of fixed-codebook; factored structure
    neither clearly helps nor hurts

---

## Context pointers

- Research note (full analysis): notes/research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md
- Tier 4 HP precedent (single-layer swap): cap_map v405 annotation, cycle 75
- Tier 5b smokes (scaffold + ppl-neutral HP; fact-transmission HF): cap_map v520 annotation, cycle 194
- hopfield-layers library: https://github.com/ml-jku/hopfield-layers
- GHRR-Transformer (VSA-attention language modeling): OpenReview zET0Zg71WT
- LARS-VSA (bipolar VSA-attention, end-to-end differentiable): arXiv:2405.14436
- Hopfield-Fenchel-Young (differentiable sparse Hopfield): arXiv:2411.08590

---

## Contract section

Research finding: attention=VSA binding is established mathematics (3 independent 2024-
2025 papers). Substrate's FHRR is the best algebra for differentiability. Tier 4 HP
provides empirical foothold (single-layer substitution stable + improved). Tier 5c MVP
is achievable via the 5-anchor sequence above. P_deflated=0.40 (combined theoretical x
empirical; capped at 0.50).

Dominant failure mode: codebook collapse. Mitigation: commitment loss (VQ-VAE style),
entropy regularization on codebook usage, EMA codebook update.

Gate sequence: probe (CPU) -> all-layer pretrained (GPU) -> from-scratch (GPU) ->
factored codebook (GPU). Each gate conditions the next.

## Autonomy declaration

exp_dev designs anchor implementations, sweep grids, hardware routing, and pre-reg
validation autonomously. This file provides strategic context and recommended thresholds.
exp_dev may modify thresholds, sequence, or architecture details based on what it finds
during implementation. The mandatory gate is the CPU differentiability probe before any
GPU dispatch for Tier 5c experiments.
