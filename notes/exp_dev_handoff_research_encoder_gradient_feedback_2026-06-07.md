# exp_dev hand-off -- research: encoder gradient feedback from retrieval failures

**Filed:** 2026-06-07 by research sub-agent.

**Trigger:** Research drill notes/research_drill_encoder_gradient_feedback_2x_2026-06-07.md completed. Finding is exp_dev-actionable: three cheap pre-tests identified, concrete LoRA adapter mechanism specified, HARD-PASS / HARD-FAIL thresholds pre-registered. Closes encoder ceiling (recall@2=0.516 vs HP=0.55) and bridge-ID accuracy (~65%) simultaneously.

**Pause state:** Check data/orchestrator_paused.flag before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, batch size, tau, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator and research do NOT specify numerical parameters beyond what is in the research note.

---

## Anchor candidates (rank-ordered)

### Anchor 1: LoRA contrastive pre-test on retrieval failure triplets
- **Anchor pointer:** Research note Section 4, Pre-test 1. Batch contrastive LoRA rank-4 adapter on HotpotQA retrieval-failure triplets.
- **Substrate-product reading:** Closes encoder ceiling. If HARD-PASS (recall@2 >= 0.55), this is the v1.5 production path. P_deflated=0.45. The adapter is 0.77M parameters and negligible inference overhead. Per-customer adapter capability is a product feature.
- **Tier hint:** Local GPU or remote_cpu. Memory: bge-large (1.3 GB) + adapter. No cloud needed for this pre-test.
- **Why now:** This is the minimum-cost resolving test. 2 hours local GPU. All components available (bge-large already in use; PEFT/LoRA available via HuggingFace). Failure mining from HotpotQA dev set is a 1-day implementation.

### Anchor 2: Hard-negative source comparison (substrate-derived vs failure-mined vs random)
- **Anchor pointer:** Research note Section 4, Pre-test 2. Three conditions: (a) failure-mined negatives, (b) random negatives, (c) substrate-derived confusable negatives (binding neighbor search).
- **Substrate-product reading:** If substrate-derived negatives match or beat failure-mined negatives (HARD-PASS), this validates crazy option (a) substrate-supervised contrastive learning -- a substrate-native training signal that requires no external annotation. P_deflated=0.35.
- **Tier hint:** Local GPU. 3 training runs.
- **Why now:** Sequentially after Anchor 1 (requires LoRA training infrastructure from Anchor 1 to be built). Can be run in the same session.

### Anchor 3: LoRA rank ablation (rank 2 vs 4 vs 8)
- **Anchor pointer:** Research note Section 4, Pre-test 3.
- **Substrate-product reading:** Confirms that rank-4 is the correct operating point. If rank-8 wins by >= 0.02, promotes to rank-16 and changes the adapter parameter estimate for per-customer storage planning.
- **Tier hint:** Local GPU. 3 training runs.
- **Why now:** Parallelizable with Anchor 2 once Anchor 1 infrastructure is built. Required for adapter architecture decision before v1.5 engineering.

### Anchor 4: Encoder distillation probe (substrate success prediction)
- **Anchor pointer:** Research note Section 3, crazy option (d). For 200 (query, fact) pairs in HotpotQA, run substrate binding check; label success/failure; fine-tune a logistic head on frozen encoder embeddings; measure AUC.
- **Substrate-product reading:** AUC > 0.75 would confirm that substrate binding success is predictable from encoder embeddings. This validates the encoder-distillation-from-substrate path (P_deflated=0.35) as a v2 mechanism.
- **Tier hint:** Local CPU (logistic head on frozen embeddings; no GPU needed). Very cheap (~30 minutes).
- **Why now:** Cheapest test. Can be run immediately with existing substrate infrastructure. No LoRA dependency.

---

## Context pointers

- Research note (full mechanism, math, risk analysis): d:/AI/hd-instrument/notes/research_drill_encoder_gradient_feedback_2x_2026-06-07.md
- Prior encoder ceiling drill (baseline recall@2 numbers): d:/AI/hd-instrument/notes/research_drill_retrieval_encoder_ceiling_alternatives_2x_2026-06-07.md
- Post-compaction brief (afternoon): d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md
- Production architecture: notes/production_architecture_locked_2026-06-07.md (in MEMORY.md)
- RL-for-dense-retriever precedent paper: arxiv 2602.03645
- Teleportation negatives paper: arxiv 2210.17167

---

## Contract

exp_dev owns ALL experimental design decisions (batch size, tau, learning rate, epoch count, seed, queue routing). This hand-off provides the mechanism description and pre-registered thresholds only. Research does NOT specify run parameters.

**Autonomy declaration:** exp_dev may reorder anchors, combine anchors into a single run, or substitute equivalent anchors per the standard Tier A/B/C routing policy. If the encoder infrastructure for LoRA (PEFT) is not yet available in the runner environment, Anchor 4 (logistic head probe, no LoRA dependency) should be dispatched first.
