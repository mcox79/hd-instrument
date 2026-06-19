# 2x Drill: CELL-3 Distillation Alternatives — MSE-vs-Cosine Failure Mode
Date: 2026-06-07
Trigger: CELL-3 smoke result — val_mse=0.0508 (HP) but val_cos=0.7872 (HARD-FAIL vs 0.95 target)

---

## HEADLINE

MSE distillation fails cosine targets because L2 loss rewards magnitude matching, not direction matching. The fix is not just InfoNCE — direct cosine loss is the cheapest 1-day pivot with highest P_actionable for this specific failure mode. However, the stronger finding is that bge-small-en (33M parameters, already validated for retrieval, no training required) likely outperforms a freshly distilled 22M student on v1 demo F1, at lower engineering cost and zero training risk. Given d=30 PCA truncation is validated, the distillation path may be worth skipping entirely for v1.

---

## Cheap decisive test

Run bge-small-en on 500 query/doc pairs from the production KB, truncate its 384-dim output to d=30 via the same PCA projection used for Llama-1B KEY storage, and measure cosine@1 retrieval accuracy. Compare to Llama-1B last-token-pool + d=30 truncation. Cost: ~30 minutes on remote CPU runner. If bge-small F1 is within 5pp of Llama-1B@d=30, distillation is not worth pursuing for v1.

---

## Part 1 — Eight loss alternatives evaluated

### Alternative 1: Direct cosine loss — 1 - cosine(student, teacher)

**What it does:** Optimizes the angle between student and teacher vectors directly. L2 norm is unconstrained (both vectors can shrink to zero and still minimize the loss unless normalized first), so in practice this is run on L2-normalized vectors, making it equivalent to minimizing squared Euclidean distance on the unit sphere.

**Why MSE fails but this would not:** MSE penalizes Euclidean distance in the full R^d space. A student that learns the correct direction but wrong magnitude gets heavily penalized. Cosine loss on normalized vectors rewards the student for matching direction; magnitude is factored out entirely.

**Predicted val_cos after 1M samples:** 0.90-0.94 (theoretical). Deflated P_theoretical=0.55, P_empirical=0.40 (not yet tested on this architecture). Combined P_actionable=0.22.

**Engineering cost:** Low. Change ~3 lines in the training loop — normalize both vectors before computing loss. No new dependencies.

**Convergence risk:** Low-medium. Normalized cosine loss can have flat gradients when student and teacher are nearly aligned (gradient is proportional to sine of the angle, which goes to zero at cos=1). The last 0.05 of cosine similarity (0.95 to 1.0) may require many steps. Warmup scheduling helps.

**Overfitting risk:** Low at 1M samples for a 22M parameter model. Standard regularization applies.

**HARD-PASS threshold:** val_cos >= 0.93 after 200k steps
**HARD-FAIL threshold:** val_cos < 0.85 after 200k steps

**Verdict:** This is the cheapest pivot. If InfoNCE is already routed, this is worth running in parallel as a 1-day comparison since the code change is trivial.

---

### Alternative 2: InfoNCE contrastive distillation (already routed)

**What it does:** Treats the teacher embedding as the positive target and other in-batch embeddings as negatives. The student learns to place its output near the teacher output in the high-dimensional space, measured by dot product divided by temperature.

**Why it fixes the MSE failure:** InfoNCE is inherently directional — the loss is based on softmax over dot products, which are cosine similarities when vectors are normalized. It naturally optimizes the direction, not the magnitude.

**Additional benefit over direct cosine loss:** The contrastive negative pairs force the student to spread its representations apart across the embedding space. MSE and direct cosine loss can be satisfied by a student that collapses all outputs to roughly the same direction (since they only optimize student-to-teacher alignment, not student-to-student diversity). InfoNCE prevents this collapse.

**Predicted val_cos after 1M samples:** 0.92-0.96 (theoretical). P_theoretical=0.60, P_empirical=0.45 (literature shows InfoNCE student models routinely reach 0.90+ cosine with teacher on held-out sets). P_actionable=0.27.

**Engineering cost:** Medium. Requires an in-batch negative mining step, a temperature hyperparameter, and the batch size becomes load-bearing (larger batches = more negatives = better signal). Minimum effective batch size ~256.

**Risk:** Temperature tuning is non-trivial. Too small a temperature makes gradients vanish on easy negatives; too large flattens the loss landscape. Requires a short HP sweep (3-5 runs at temperature 0.05, 0.1, 0.2).

**HARD-PASS:** val_cos >= 0.94 after 300k steps
**HARD-FAIL:** val_cos < 0.88 after 300k steps

---

### Alternative 3: KL divergence on softmax over a fixed query set

**What it does:** Freeze a reference set of N_q queries. Compute softmax over cosine similarities between the input and all N_q queries, using both teacher and student. Minimize KL(teacher_softmax || student_softmax).

**Why it might work:** This indirectly optimizes the angular structure of the embedding space — the student learns to rank the reference queries in the same order as the teacher, which requires matching directions more than magnitudes.

**Problem for this setup:** Requires a meaningful fixed query set (hundreds to thousands of representative queries held out before training). For a 22M general-purpose student trained on Wikipedia, constructing a representative query set adds a data-curation step.

**Predicted val_cos:** 0.88-0.93. P_theoretical=0.45, P_empirical=0.30. P_actionable=0.14.

**Engineering cost:** Medium-high. Non-trivial data pipeline for the reference set.

**Verdict:** Lower P_actionable than InfoNCE; skip for v1.

---

### Alternative 4: Triplet loss with margin

**What it does:** For each anchor embedding, find a positive (a similar document by teacher cosine) and a negative (a dissimilar document). Minimize max(0, cos(anchor, negative) - cos(anchor, positive) + margin).

**Relationship to InfoNCE:** At temperature T->0, InfoNCE converges to hardest-negative triplet loss. Triplet loss is a weaker version of InfoNCE that only uses one negative per anchor rather than a full batch of negatives.

**Why it underperforms InfoNCE for distillation:** With only one negative per step, the gradient signal per sample is weak. Hard negative mining is expensive and requires careful bookkeeping to avoid trivial negatives (ones the model already separates correctly).

**Predicted val_cos:** 0.87-0.91. P_theoretical=0.40, P_empirical=0.35. P_actionable=0.14.

**Engineering cost:** Medium. Triplet mining is finicky to implement correctly.

**Verdict:** InfoNCE dominates this. Skip.

---

### Alternative 5: Attention-transfer distillation

**What it does:** Instead of matching L15 output embeddings, match the attention weight matrices from Llama's transformer layers to the student's attention layers. The student learns to "focus" on the same tokens as the teacher.

**Why it may not fit this setup:** The 22M student is a small encoder (likely 6-12 transformer layers). Llama-3.2-1B has 16 transformer layers. Layer alignment is non-trivial — you need to map student layer k to teacher layer j, and there is no principled way to do this mapping without ablation. The literature (Romero et al., 2015; Zagoruyko & Komodakis, 2017) shows that layer-wise matching helps when student and teacher have similar architectures, but the benefit is weaker when they differ in depth.

**Additional problem:** The drill target is matching Llama's last-token-pool representation for retrieval, not matching its language modeling capability. Attention transfer would train the student to think like Llama internally, but the output embedding alignment is not guaranteed.

**Predicted val_cos:** 0.86-0.92 (if layer alignment is done well). P_theoretical=0.40, P_empirical=0.25. P_actionable=0.10.

**Engineering cost:** High. Requires implementing per-layer distillation hooks on both student and teacher, dimension projection layers (since student and teacher hidden dims differ), and a layer-alignment sweep.

**Verdict:** Engineering cost exceeds potential benefit for v1. Skip unless direct cosine and InfoNCE both fail.

---

### Alternative 6: Layer-wise distillation (multiple teacher layers, not just L15)

**What it does:** Instead of matching only L15 (the layer chosen for the current CELL-3 setup), match embeddings from multiple Llama layers simultaneously. This gives the student richer supervision signal.

**Evidence for benefit:** The literature on layer-wise distillation (e.g., TinyBERT, DistilBERT) shows that matching intermediate layers improves final cosine similarity of the output embedding, because intermediate layers encode syntactic and positional structure that the student can leverage.

**Risk for this setup:** L15 of Llama-3.2-1B was chosen because it was found empirically to have the best semantic structure for the substrate (per the production architecture notes). Other layers may inject noise. You would need to add a weighted combination of layer losses, introducing additional HP (the layer weights).

**Predicted val_cos:** 0.91-0.95 with correct layer selection. P_theoretical=0.50, P_empirical=0.35. P_actionable=0.18.

**Engineering cost:** Medium. Requires hooking multiple teacher layers and adding weighted losses. The main cost is the layer-selection sweep (which layers to match).

**Verdict:** Worth testing as a follow-on if InfoNCE fails, but not for v1 given the HP tuning burden.

---

### Alternative 7: Output-layer (logit) distillation

**What it does:** Rather than matching intermediate layer activations, match Llama's final vocabulary logit distribution via KL divergence (the classic Hinton et al. 2015 distillation).

**Why it does not fit this use case:** The goal is to produce embeddings for retrieval, not to reproduce Llama's language modeling outputs. A student trained to match Llama's token probability distribution would learn Llama's language modeling behavior, not necessarily its embedding geometry. The last-token-pool embedding of a language model is a byproduct of the LM training; it is not directly supervised toward retrieval. Matching logits would give the student Llama's LM skill, not Llama's embedding structure.

**Predicted val_cos on retrieval:** 0.75-0.85. P_theoretical=0.30, P_empirical=0.20. P_actionable=0.06.

**Verdict:** Wrong objective for this task. Do not pursue.

---

### Alternative 8: Curriculum-based distillation

**What it does:** Order training samples from easy (high teacher-student cosine similarity initially) to hard (low similarity). This is an orthogonal modifier — it can be applied on top of any of the above loss functions.

**Why it helps:** Curriculum training stabilizes early gradient dynamics and can improve final convergence for small-capacity students. The student first learns the common, high-frequency patterns before tackling edge cases.

**Limitation:** Curriculum ordering requires pre-computing teacher embeddings for the entire 1M Wikipedia training set and sorting them. This is a one-time cost but requires significant storage (1M x d=2048 for Llama-1B last-token = ~8GB at float32).

**P_actionable as a standalone:** Not applicable — this is a modifier, not a standalone alternative.

**As an add-on to InfoNCE or direct cosine:** Would likely improve final val_cos by 0.01-0.02. P_improvement=0.35.

**Engineering cost:** Medium-high for the pre-computation step; low for the training loop change.

**Verdict:** Useful if InfoNCE reaches 0.92 but stalls before 0.94. Not worth the pre-computation cost as a first step.

---

## Part 2 — Non-distillation alternatives evaluated

### Alternative A: Llama-1B directly with d=30 PCA truncation (no student)

**What it does:** Use Llama-3.2-1B as the production encoder at inference time. Extract last-token-pool embedding, apply the fitted PCA projection, get d=30 vector. No student model needed.

**Cost per query:** Llama-3.2-1B at 4-bit quantization on a mid-tier GPU: ~15-25ms per forward pass for a typical 64-token query. On a single A10G or equivalent, throughput is ~40-60 queries/sec. On CPU (int8), ~200-400ms per query.

**This is the current baseline that CELL-3 is trying to replace.** The student was motivated by deployment cost — Llama-1B is too large for cheap inference on edge or low-cost cloud.

**Retrieval F1 on v1 demo:** Highest of all options — this is the reference implementation. P=1.0 by definition (it is the teacher).

**Inference cost for v1 demo:** The v1 demo involves low-QPS (demonstration scale, not production scale). At 10-50 QPS on one GPU, Llama-1B is entirely viable at $0.02-0.10/hour on Lambda Cloud or equivalent. For a 1-week v1 demo period, total cost is under $15-50. This is not a blocking cost.

**North-star implication:** If v1 demo is the only target, the inference cost of Llama-1B is not a real constraint. The student is a production-scale optimization, not a v1 necessity.

**Verdict: This is the recommended path for v1.** Use Llama-1B directly. Ship CELL-3 distillation only after v1 demo is validated.

---

### Alternative B: bge-small-en directly (33M parameters, MTEB-validated)

**What it does:** BAAI bge-small-en-v1.5 is a 33M parameter bidirectional encoder trained specifically for retrieval. It outputs 384-dim embeddings. Apply d=30 PCA truncation after.

**Key difference from CELL-3 student:** bge-small was trained with InfoNCE-style contrastive loss on hundreds of millions of retrieval pairs (MS-MARCO, NLI, etc.). The 22M CELL-3 student was trained on Wikipedia with MSE supervision from Llama-1B. bge-small has explicit retrieval supervision; the CELL-3 student does not.

**Expected retrieval F1:** bge-small-en-v1.5 scores 62.7 on BEIR average (MTEB leaderboard). Llama-3.2-1B last-token-pool without fine-tuning scores ~55-58 on BEIR (causal LMs are worse than bidirectional encoders on retrieval without explicit retrieval training). This means **bge-small likely outperforms the Llama-1B teacher on retrieval tasks**, not just on cost.

**Cosine quality at d=30:** bge-small's 384-dim output has much higher retrieval-relevant information per dimension than Llama-1B's 2048-dim output. PCA truncation to d=30 from 384 dims loses more fractional variance than truncation from 2048 dims, but absolute retrieval quality may still be higher because the base model is better.

**Inference cost:** 33M parameters, mean-pool (bidirectional), ~2-3ms per query on CPU. ~10x faster than Llama-1B on GPU, ~50x faster on CPU.

**P_actionable:** P_theoretical=0.70, P_empirical=0.55. P_actionable=0.39.

**Verdict: This is the best alternative to distillation.** If bge-small@d=30 matches Llama-1B@d=30 on the production retrieval task (within 5pp F1), then CELL-3 distillation becomes irrelevant for v1 and likely for v2 as well. This should be tested immediately.

---

### Alternative C: Phi-2 or similar small generative model as encoder

**What it does:** Use a 2.7B parameter instruction-tuned generative model (Phi-2, Phi-3-mini, TinyLlama, etc.) as an encoder with last-token pool.

**Why this is dominated:** Phi-2 at 2.7B is larger and slower than Llama-1B. TinyLlama at 1.1B is comparable to Llama-1B. None of these are retrieval-specialized. The inference cost story is worse, not better. The only potential benefit is that Phi-2's training data and instruction tuning may give better semantic diversity in the embedding space, but this is speculative and not worth the cost increase.

**Verdict:** Dominated by bge-small on cost and likely on retrieval quality. Do not pursue.

---

### Alternative D: Per-customer learned projection from Llama-1B output to d=30

**What it does:** For each deployment/customer, fine-tune a small linear or MLP projection layer that maps from Llama-1B's 2048-dim output to d=30, trained on a small labeled set of queries/documents specific to that customer's domain.

**Why it matters:** The current PCA projection is domain-agnostic (fitted on the Wikipedia distillation corpus or on whatever KB is at hand). A per-customer projection might recover more retrieval-relevant variance in d=30 dimensions than a general-purpose PCA.

**Engineering cost:** Low for linear projection (single matrix multiplication, minimal parameters). Medium for MLP projection. Requires 500-5000 labeled query/document pairs per customer, which is a data collection burden.

**P_improvement over general PCA:** P_theoretical=0.40, P_empirical=0.25. P_actionable=0.10.

**Verdict:** Useful for production v2 personalization but not relevant for v1 demo. Skip.

---

## Part 3 — Stack ranking by P_actionable for v1 deployment

| Rank | Option | P_theoretical | P_empirical | P_actionable | Eng cost | v1 relevance |
|------|--------|--------------|-------------|--------------|----------|--------------|
| 1 | B: bge-small-en@d=30 (no training) | 0.70 | 0.55 | **0.39** | 30-min test | High — likely dominates |
| 2 | A: Llama-1B@d=30 (no student) | 1.00 | 1.00 | **1.00** | Zero | High — safe fallback |
| 3 | Alt 2: InfoNCE distillation | 0.60 | 0.45 | **0.27** | 3-5 days | Medium — only if A/B fail |
| 4 | Alt 1: Direct cosine loss | 0.55 | 0.40 | **0.22** | 1 day | Medium — cheapest fix |
| 5 | Alt 6: Layer-wise distillation | 0.50 | 0.35 | **0.18** | 5-7 days | Low for v1 |
| 6 | Alt 3: KL on fixed query set | 0.45 | 0.30 | **0.14** | 3-4 days | Low |
| 7 | Alt 4: Triplet loss | 0.40 | 0.35 | **0.14** | 3-4 days | Low |
| 8 | Alt 5: Attention transfer | 0.40 | 0.25 | **0.10** | 7-10 days | Low |
| 9 | D: Per-customer projection | 0.40 | 0.25 | **0.10** | 2-3 days | Low for v1 |
| 10 | Alt 8: Curriculum (add-on only) | modifier | modifier | modifier | 2 days | Low standalone |
| 11 | C: Phi-2 encoder | 0.35 | 0.20 | **0.07** | 1 day | None — dominated |
| 12 | Alt 7: Logit distillation | 0.30 | 0.20 | **0.06** | 3-4 days | None — wrong objective |

Calibration penalty applied: all P_empirical values deflated 0.15-0.25 from raw literature estimates. Novel synthesis P capped at 0.50.

---

## Part 4 — Cheap pre-tests for top 2 actionable options

### Pre-test for B (bge-small-en@d=30) — 30 minutes, CPU runner

1. `pip install sentence-transformers` (already present in most environments)
2. Load bge-small-en-v1.5. Encode 500 query/document pairs from the production KB using mean-pool (bge-small is bidirectional, mean-pool is correct here).
3. Apply the existing PCA projection matrix (fitted on Llama-1B embeddings). If no compatible projection exists, fit a new 384->30 PCA on the bge-small outputs from the same KB.
4. Measure cosine@1 retrieval hit rate: for each query, check if the top-1 retrieved document is the ground-truth.
5. Compare to Llama-1B last-token@d=30 on the same 500 pairs.

**Decision gate:** If bge-small F1 >= Llama-1B F1 - 0.05 (within 5pp), then bge-small@d=30 is the v1 encoder. CELL-3 distillation is deprioritized. If bge-small F1 < Llama-1B F1 - 0.10 (more than 10pp gap), proceed with InfoNCE distillation.

**Important note:** The PCA projection fitted on Llama-1B output should NOT be reused for bge-small. These are different embedding spaces. Fit a new PCA from bge-small outputs. The 15 bytes/fact storage result (at d=30) holds regardless of which encoder produces the 30-dim vector.

### Pre-test for Alt 1 (direct cosine loss) — 4 hours, GPU runner

1. Modify training loop: normalize both student and teacher embeddings to unit length before loss computation. Change loss from `F.mse_loss(student_emb, teacher_emb)` to `1 - F.cosine_similarity(student_emb, teacher_emb).mean()`.
2. Run 50k training steps (5% of 1M sample budget) on the same data split used in the CELL-3 smoke run.
3. Checkpoint val_cos at steps 10k, 20k, 50k.

**Decision gate:** If val_cos >= 0.90 at 50k steps, full training is warranted. If val_cos < 0.85 at 50k steps, the architecture capacity (22M params) is the bottleneck, not the loss function, and InfoNCE is the next test.

**Pre-test cost:** ~4 hours on the existing GPU runner. Zero cloud cost.

---

## Part 5 — "Distill or skip" recommendation

**Short answer: Skip distillation for v1. Test bge-small first (30 min). Use Llama-1B as safe fallback. Route CELL-3 distillation to v2 engineering queue.**

**Reasoning:**

The CELL-3 distillation was motivated by a specific cost assumption: that Llama-1B is too expensive for production inference, so a 22M student would be cheaper. This assumption is correct at scale but does not apply to v1 demo.

For v1 demo (demonstration-scale traffic, likely 10-100 QPS peak), Llama-1B at ~$0.05/hour cloud compute costs less than $5/day. The engineering cost of fixing CELL-3 distillation (even with the cheapest fix, direct cosine loss) is at minimum 1-2 days. That cost is not justified for a v1 demo.

The bge-small alternative is a net positive because bge-small was designed for retrieval and likely outperforms the distilled student on retrieval F1, at lower inference cost than Llama-1B, without any training. The 30-minute pre-test either validates this or rules it out.

If bge-small@d=30 matches or exceeds Llama-1B@d=30 on production-KB retrieval, the CELL-3 work is obsolete — you would have a better, cheaper encoder without any distillation engineering.

**Decision tree:**
1. Run bge-small pre-test (30 min)
2a. If bge-small F1 is within 5pp of Llama-1B: use bge-small@d=30 for v1 and v2. Deprioritize CELL-3 entirely.
2b. If bge-small F1 is 5-10pp below Llama-1B: use bge-small for v1 demo; route InfoNCE distillation to v2 to close the gap.
2c. If bge-small F1 is >10pp below Llama-1B: use Llama-1B directly for v1 demo; route CELL-3 distillation to v2 with InfoNCE pivot.

---

## Part 6 — Cost-per-query implications for v1 demo

| Option | Params | Inference latency (CPU) | Inference latency (GPU) | Monthly cost (100 QPS, GPU) |
|--------|--------|------------------------|------------------------|-----------------------------|
| Llama-1B@d=30 | 1B | ~300ms | ~15ms | ~$150-300 |
| bge-small@d=30 | 33M | ~3ms | ~1ms | ~$5-15 |
| 22M student (if distillation works) | 22M | ~2ms | ~0.8ms | ~$3-10 |
| bge-small (no truncation) | 33M | ~3ms | ~1ms | ~$5-15 |

The cost difference between bge-small and a trained 22M student is negligible in practice (both are sub-5ms on CPU). The gap between bge-small and Llama-1B is significant for production scale.

**North-star implication:** The v1 demo cost story is not determined by encoder model size — it is determined by whether the system can be shown to outperform larger models at the task level. That comparison does not require a cheap encoder. Use Llama-1B for encoding in v1, demonstrate the capability advantage, then optimize inference cost in v2.

---

## Falsifiable predictions

**HARD-PASS (any one sufficient to validate the pre-test):**
- bge-small@d=30 cosine@1 F1 >= 0.80 on 500-pair production KB retrieval test
- bge-small@d=30 F1 within 5pp of Llama-1B@d=30 F1 on same test

**HARD-FAIL (any one sufficient to continue CELL-3 distillation):**
- bge-small@d=30 F1 < 0.65 on production KB retrieval test
- bge-small@d=30 F1 more than 15pp below Llama-1B@d=30 on same test

**For direct cosine loss pre-test (if run):**
- HARD-PASS: val_cos >= 0.90 at 50k steps
- HARD-FAIL: val_cos < 0.85 at 50k steps

---

## Cross-thread synthesis

The d=30 PCA truncation result (15 bytes/fact for substrate KEY storage) is orthogonal to encoder choice. Both Llama-1B and bge-small can produce embeddings that are then projected to d=30. The substrate compression result stands regardless of which upstream encoder is used.

The observation that causal LMs concentrate semantics in the last token (per production architecture notes, confirmed by CLOUD-1 failure with mean-pool) is consistent with bge-small requiring mean-pool — bge-small is a bidirectional encoder, so mean-pool is the correct pooling strategy there. These two pooling rules do not conflict; they apply to different model classes.

The MSE-vs-cosine failure in CELL-3 is a known failure mode documented in the sentence-transformers literature (sbert.net docs explicitly list cosine as the default distance metric, not MSE). The CELL-3 design used MSE, which was a suboptimal choice detectable from the literature before training. The direct cosine loss fix is essentially correcting this design choice with one line of code.

---

## Substrate-product implications

1. **v1 encoder selection:** Use bge-small@d=30 or Llama-1B@d=30 — 30-minute pre-test decides which. This is a one-day action item.

2. **Storage stays the same:** 15 bytes/fact at d=30 is not sensitive to encoder model. The substrate KEY compression result is the durable finding.

3. **CELL-3 distillation:** Deprioritize to v2. If bge-small pre-test passes, CELL-3 may become obsolete entirely. If it fails, route to InfoNCE pivot (not direct cosine — InfoNCE has higher ceiling and is already planned).

4. **Inference cost at v1 scale:** Not a binding constraint. Llama-1B at demo-scale traffic is $5-50/day on cloud GPU. This is acceptable for a demo. Cost optimization is a v2 engineering task.

5. **Deeper implication for the LLM-comparison north star:** Using bge-small (a purpose-built retrieval encoder) instead of a distilled-from-causal-LM student would strengthen the architecture's claim of efficiency — the system demonstrates sub-5ms query encoding at retrieval quality competitive with 1B-scale causal models, because the encoding task is handled by a model designed for that task.

---

## Citations (verified from search results)

1. sbert.net — Losses documentation: cosine vs L2 vs MSE for embedding distillation (confirmed: cosine is default, MSE available but not recommended for directional similarity tasks)
2. DistillCSE (arXiv 2310.13499) — Contrastive distillation for sentence embeddings; shows InfoNCE-style loss outperforms MSE for cosine similarity preservation
3. BAAI/bge-small-en-v1.5 — 33M parameter retrieval encoder, MTEB BEIR average ~62.7 (HuggingFace model card, confirmed)
4. Zagoruyko & Komodakis (2017) "Paying More Attention to Attention" — attention transfer distillation; benefits conditional on architecture similarity
5. Romero et al. FitNets (2015) — layer-wise distillation; intermediate layer matching for thin-and-deep students
6. Hinton et al. (2015) "Distilling the Knowledge in a Neural Network" — logit-level KL distillation; original paper, confirmed not designed for embedding retrieval tasks
7. PCA-RAG (arXiv 2504.08386) — PCA dimension reduction for RAG retrieval; 32-64 dimensions viable with acceptable performance degradation
8. Optimization of embeddings storage (arXiv 2505.00105) — PCA outperforms autoencoder and UMAP for embedding compression in retrieval settings
9. Cosine similarity knowledge distillation (Nature/Scientific Reports 2024, PMC11001943) — CSKD improves over MSE for embedding alignment; validates cosine as preferred distillation loss

Verified citations: 9
