# exp_dev hand-off -- research: substrate-only language model 5x

**Filed:** 2026-06-08 by research sub-agent.

**Trigger:** User mandate: "Can substrate really not understand language? It couldn't be trained to understand it?" Research note: d:/AI/hd-instrument/notes/research_drill_substrate_only_language_model_5x_2026-06-08.md

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching queue-modifying actions.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Research finding summary (for context; exp_dev reads research note for detail)

Substrate CAN be trained as a language model. Three levels of evidence:
(1) Transformers already implement approximate VSA (arXiv 2512.14709; GPT-2 VSA paper arXiv 2412.07947).
(2) GHRR-Transformer (OpenReview zET0Zg71WT, Oct 2024) demonstrates end-to-end language modeling with VSA-based attention, claims language modeling benefits over standard transformer.
(3) LARS-VSA (arXiv 2405.14436, May 2024) demonstrates 25x speedup for VSA attention on relational tasks; authors explicitly propose a "VSA-only decoder" as future work.
Substrate's FHRR is Wirtinger-differentiable (no STE needed), giving it cleaner training gradients than bipolar VSA.
The categorical claim "substrate IS a complete cognitive architecture" is achievable via rung-1 experiments.

Six engineering paths identified (ranked by P_deflated x cost):
1. Substrate codebook trained on BERT via VQ-VAE -- CPU, 2 hours (Path 1)
2. Substrate-only TinyStories LM from scratch (GHRR recipe) -- GPU, 2-4 days (Path 3)
3. Substrate-distilled from Qwen-1.5B -- GPU, 2-5 days (Path 2)
4. Hybrid: substrate replaces mid-layers of Pythia-1.4B -- GPU, 2-4 weeks (Path 6)
5. Substrate-attention from scratch at 160M scale -- GPU, 4-8 weeks (Path 4)
6. Joint pretraining with differentiable retrieval (D-RAG style) -- GPU, 8-16 weeks (Path 5)

The research note pre-registers HARD-PASS / HARD-FAIL bands for paths 1, 2, 3, and 6.

The cheap decisive test is: substrate-10M trained on TinyStories corpus, compared to transformer-10M baseline. 4 GPU-days. HARD-PASS = perplexity within 15% of transformer-10M. HARD-FAIL = perplexity > 2x transformer-10M or training diverges.

---

## Anchor candidates (rank-ordered by P_deflated x cost)

### 1. Substrate codebook from BERT/word2vec via VQ-VAE (HIGHEST PRIORITY -- cheapest)
- Anchor pointer: Path 1 in research note Level 3. Train VQ-VAE where encoder = pretrained BERT embeddings, codebook = FHRR atoms. Measure codebook utilization, top-1 cosine similarity BERT->atom, and analogy test (king - man + woman = queen).
- Substrate-product reading: establishes whether substrate atoms can serve as semantic primitives for language. If HARD-PASS, the atom vocabulary is semantically coherent -- all downstream LM paths are viable. If HARD-FAIL (codebook collapse), VQ-VAE approach needs rotation trick or Dirichlet encoder fix (literature solutions available, 2024).
- Tier hint: CPU. This is a 2-hour run. No GPU needed.
- Why now: HIGHEST PRIORITY because it gates all other LM paths. A codebook that collapses means Path 3 needs a different vocabulary construction strategy. Costs almost nothing. P_deflated = 0.50 theoretical; P_empirical requires this pretest.

### 2. Substrate-only TinyStories 10M LM (decisive categorical test)
- Anchor pointer: Path 3 in research note Level 3. Implement GHRR-Transformer-style architecture using FHRR binding operations for attention. Train on TinyStories corpus (2B tokens, ~1500-word vocabulary). Compare perplexity and GPT-4-graded story quality vs same-size standard transformer baseline.
- Substrate-product reading: the single most important categorical test. A HARD-PASS on this anchor means "substrate IS a language model" as a factual product claim. A HARD-FAIL means substrate-only LM is not viable at this scale and architecture -- should investigate GHRR-Transformer's specific design choices before scaling.
- Tier hint: remote GPU preferred (training loop over 2B tokens). Estimate 2-4 GPU-days on A100.
- Why now: HIGH PRIORITY. Establishes the categorical claim. Gates v3.0 product roadmap. P_deflated for beating transformer-10M on TinyStories: 0.28. P_deflated for training converging: 0.55.
- Prerequisite: Anchor 1 (codebook quality) should complete first; if Anchor 1 HARD-FAILS, revisit codebook construction before Anchor 2.

### 3. Substrate mid-layer hybrid on Pythia-1.4B (parallel path to v2.0)
- Anchor pointer: Path 6 in research note Level 3 (also Level 4.2 in prior intrinsic-language note). Replace mid-to-late attention layers (not all layers) with substrate retrieval. Load substrate with same-corpus knowledge. Measure next-token accuracy delta vs unmodified Pythia-1.4B.
- Substrate-product reading: HARD-PASS means the hybrid architecture is the fastest path to v2.0 (no from-scratch training needed). HARD-FAIL (>15% accuracy drop) means key-space alignment needs a learned projection layer first. MID-BAND result (5-15% drop) means projection layer is the fix.
- Tier hint: remote GPU. Requires HuggingFace attention hook and substrate query integration.
- Why now: MEDIUM PRIORITY. Can run in parallel with Anchor 2. P_deflated = 0.38. This is the v2.0 critical path enabler.
- Note: PP-142 in prior handoff covers this anchor; if PP-142 is already queued, sequence after that result.

### 4. Substrate-distilled from Qwen-1.5B (narrow-domain factual QA)
- Anchor pointer: Path 2 in research note Level 3. Use Qwen-1.5B to generate question-answer pairs from a structured domain corpus. Train substrate bindings to reproduce teacher answers. Measure held-out QA accuracy vs teacher.
- Substrate-product reading: demonstrates the commercial path for "substrate as narrow-domain AI without LLM dependency." HARD-PASS means a substrate model can be deployed for a specific domain (enterprise wiki, medical formulary) without a hosted LLM. HARD-FAIL means substrate student cannot generalize beyond memorized pairs.
- Tier hint: remote GPU for teacher inference; substrate training is CPU.
- Why now: LOWER PRIORITY than Anchors 1-3. Gates commercial deployment narrative. P_deflated = 0.30.

### 5. Substrate-attention at 160M from scratch (GHRR replica)
- Anchor pointer: Path 4 in research note Level 3. Replace all attention in a Pythia-160M-sized architecture with FHRR-based substrate attention. Train from random initialization on same corpus as Pythia-160M.
- Substrate-product reading: full categorical proof at production scale. If perplexity is within 20% of Pythia-160M, this anchors the "substrate is a complete language model" claim at non-trivial scale.
- Tier hint: remote GPU. 4-8 GPU-weeks. Do NOT dispatch until Anchors 2 and 3 complete.
- Why now: NOT NOW. Gate on Anchors 2+3 results. P_deflated = 0.28.

---

## Sequencing recommendation

Dispatch order:
1. Anchor 1 (CPU, 2 hours) -- no GPU needed, zero queue cost.
2. Anchor 2 + Anchor 3 (parallel GPU dispatch, once Anchor 1 completes or Anchor 1 results in hand).
3. Anchor 4 (after Anchor 2 result in hand).
4. Anchor 5 (gate on Anchors 2+3 passing).

---

## Context pointers

- Research note (full): d:/AI/hd-instrument/notes/research_drill_substrate_only_language_model_5x_2026-06-08.md
- Prior intrinsic-language note: d:/AI/hd-instrument/notes/research_drill_substrate_llm_intrinsic_language_5x_2026-06-08.md
- Prior intrinsic-language handoff (PP-139 through PP-143): d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_intrinsic_language_5x_2026-06-08.md
- LARS-VSA paper: arXiv 2405.14436
- GHRR-Transformer: OpenReview zET0Zg71WT
- Attention-as-binding: arXiv 2512.14709
- Linearithmic cleanup: arXiv 2506.15793
- TinyStories: arXiv 2305.07759
- kNN-LM: arXiv 1911.00172
- D-RAG: EMNLP 2025 / OpenReview D0vilzHmI3
- Production architecture lock: d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md

---

## Contract section

This hand-off is triggered by research findings that are exp_dev-actionable. Anchor 1 (codebook VQ-VAE) and Anchor 2 (TinyStories from scratch) are new anchors not previously in the queue. Anchor 3 overlaps with PP-142 from the prior handoff -- exp_dev should check whether PP-142 is already queued before adding Anchor 3.

exp_dev has full authority to:
- Choose anchor names, parameter values, threshold bands, queue assignment
- Reorder anchors if queue state or runner availability dictates
- Add smoke-test versions of Anchors 2 and 5 before full dispatch
- Decide whether Path 1 runs as a standalone anchor or as a pre-flight check for Path 3

exp_dev does NOT need to follow this sequencing recommendation exactly. The recommendation is a prior; the queue state and pause flag are the constraints.

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: this file provides context, motivation, and anchor candidates. exp_dev designs all experimental details autonomously. Research sub-agent has no authority over queue order, parameter choices, or go/no-go decisions after this hand-off.
