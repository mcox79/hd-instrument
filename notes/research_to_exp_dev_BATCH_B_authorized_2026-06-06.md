# Research -> Exp-Dev: Batch B AUTHORIZED (7 cells; ~3h CPU total; $0)

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User
**Date:** 2026-06-06 ~19:45
**Re:** exp_dev_to_research_BATCH_A_results_2026-06-06.md (all 4 Batch A HP smoke) + cycle 128 (d_eff=82 unifying insight)
**Subject:** User authorized Batch B (revised based on Batch A + cycle 128). 7 cells; $0; ~3h CPU sequential or ~1.5h parallel. Pipeline refill ready.

---

## User authorized Batch B

Revised priorities based on Batch A wins (HOC1 closed word-order gate; EFFECTIVE-RANK validated d_eff=82 framework) + cycle 128 insight (encoder d_eff is the primary production lever).

### Ship in parallel (queues empty; pipeline urgent)

### NEW HIGHEST PRIORITY: EFFECTIVE-RANK SVD on multiple encoders

Anchor pointer: `effective_rank_svd_multi_encoder_v1`
- Architecture: SVD effective_rank diagnostic (same metric as Batch A Rank 2; participation ratio + rank90 + rank99) on:
  - Pythia-160m (already have residual npz locally)
  - Llama-3.2-1B at L=15 (CLOUD-1b's optimal layer; samples could come from CLOUD-1b's cached activations if available, otherwise quick fresh extraction)
  - mpnet-768 (already in use; sentence-transformer family)
  - MiniLM-L6-v2 (Batch A confirmed d_eff=82; use as reference)
- Goal: rank-order encoders by d_eff
- Why TOP priority: cycle 128 reframes Phase-4 -- encoder d_eff is the PRIMARY production-capacity lever. Random projection can't exceed rank; whitening rank-bounded. Higher-d_eff encoder = higher production substrate capacity.
- Wall: <30 min CPU; $0
- HP threshold: any encoder shows d_eff >= 2x MiniLM (>=160 in 384-class; >=400+ in 768-class)
- Strategic value: could change Phase 4 production encoder choice; cross-references distillation context (Llama-1B distilled from 8B+70B logits)

### Original Batch B cells (4)

**1. DIMSPARSE3-alpha at M near M_c** (compound math definitive)
- Anchor pointer: `dimsparse3_alpha_at_mc_v1`
- Architecture: 4 arms (baseline + dim-expansion + sparse-KEY alpha + compound) on real Pythia keys at M near M_c (NOT M=50 per cycle 124-125 LVH lesson)
- Use auto-assoc Hopfield exact-recovery on sign-binarized real keys (NOT M_50 metric per metric save)
- Wall: ~30 min CPU
- Strategic value: definitively answers compound stacking question with proper metric + M-regime

**2. CS-1 Donoho-Tanner algebraic audit** (paradigm-shift framework)
- Anchor pointer: `cs1_dt_algebraic_audit_v1`
- Architecture: algebraic computation of (delta=M/N, rho=k/M) operating point at each rescue arm; map shifts toward success zone
- Wall: ~1h CPU (algebraic; no GPU)
- Strategic value: EVEN HIGHER now that d_eff=82 anchors the framework empirically. Unifies Hadamard / dim-expansion / sparse-KEY axes in single phase-boundary calculator.

**3. fact_checked_khop** (composition demo)
- Anchor pointer: `fact_checked_khop_v1`
- Architecture: K-hop reasoning (K=3-5 first; can extend) + per-hop KF-1 hallucination detection at each step
- Wall: 10-20 min CPU
- Strategic value: composition of validated capabilities; unique vs frontier LLM (per-hop localization)

**4. NEG1 DeBERTa NLI drop-in** (LOWER priority now)
- Anchor pointer: `neg1_deberta_nli_v1`
- Architecture: drop-in MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli; replace MiniLM cosine scorer with contradiction probability
- Re-priced: HOC1 closes word-order gate (AUC 0.970) cheaply; NEG1 only needed for NEGATION/CONTRADICTION (G5/G13 unanimous 3-seed HF)
- Wall: ~30-60 min CPU (model load + inference)
- Strategic value: completes Phase 4 hallucination 3-signal stack: substrate grounding + HOC1 bigrams + NEG1 NLI

### 2 FREE cells from 70B late-layer drill

**5. ANISOTROPY diagnostic L=50 vs L=74** (directly tests primary H2 mechanism)
- Anchor pointer: `anisotropy_diagnostic_70b_l50_l74_v1`
- Architecture: layer-wise average cosine similarity between 500 query embeddings at L=50 vs L=74 on Llama-3.1-70B NF4
- Wall: <5 min local CPU (uses cached CLOUD-1b activations if available; otherwise quick extraction)
- HP: avg cosine at L=74 >> L=50 (e.g., >=0.92 vs <=0.65) -- anisotropy collapse confirmed
- Strategic value: $0 confirmation of late-layer prediction-geometry specialization mechanism

**6. ENCODER vs DECODER at 130M matched scale** (resolves MiniLM 5.11x puzzle)
- Anchor pointer: `encoder_vs_decoder_130m_matched_scale_v1`
- Architecture: MiniLM-L6-v2 (22M) vs ~130M causal LM (Pythia-130m or similar) vs ~130M encoder-only model on same SQuAD-v2 task
- Wall: <60s laptop CPU
- HP: encoder-only models >> causal-LM at matched param count
- Strategic value: tests whether MiniLM's advantage is bidirectionality (architecture) or scale-objective. Long-term substrate extractor architecture decision.

---

## Dispatch sequence recommendation

Batch B1 (immediate parallel; mostly free):
- EFFECTIVE-RANK multi-encoder (top priority; <30 min)
- ANISOTROPY diagnostic (<5 min; uses cached if avail)
- ENCODER vs DECODER (<60s)
- fact_checked_khop (10-20 min)

Batch B2 (parallel with B1 or after):
- DIMSPARSE3-alpha (~30 min)
- CS-1 algebraic audit (~1h; runs while B1 completes)
- NEG1 DeBERTa NLI (~30-60 min; lower priority but still in batch)

Total wall: ~3h sequential or ~1.5h with parallelism. $0.

---

## Cross-references

- Batch A results: `notes/exp_dev_to_research_BATCH_A_results_2026-06-06.md`
- Cycle 128 insight: `notes/orchestrator_to_research_results_summary_2026-06-06_cycle128.md`
- 70B late-layer drill: `notes/research_drill_large_lm_late_layer_retrieval_crash_2026-06-06.md`
- Cloud cells: handled directly by user with Testbed (CELL-1 hardware + Together API key)
- Re-pointed family: continue with separate flow (Slot 9/14/G8 with auto-assoc Hopfield)

---

## Contract

You design anchor specifics, sweep grids, HP/MID/HF thresholds, queue assignments, timeout formulas. Pre-reg per envelope-fail-band protocol. write_metrics() required fields. ASCII-only.

Re-pointed real-encoder capacity family (Slot 9/14/G8/etc.) continues in parallel with this batch -- not part of Batch B but a separate ongoing track.

---

**END.**

**Exp-Dev:** Batch B authorized (7 cells; ~3h CPU sequential / ~1.5h parallel; $0). Ship batch B1 immediately in parallel (4 cells; mostly free); B2 after or in parallel (3 cells). EFFECTIVE-RANK multi-encoder is the NEW HIGHEST PRIORITY per cycle 128 -- could change Phase 4 production encoder choice.

**User:** Batch B (7 cells) routed to Exp-Dev. $0 + ~3h CPU. Re-pointed real-encoder family continues separately. Cloud cells (CELL-1 + CELL-5) being handled directly by you with Testbed.
