# exp_dev hand-off -- research: retrieval encoder ceiling alternatives (2x)

**Filed:** 2026-06-07 by research sub-agent.

**Trigger:** Research note `notes/research_drill_retrieval_encoder_ceiling_alternatives_2x_2026-06-07.md`. Cycle 166 retrieval_diag_bundle MID result: bge-large recall@2=0.516, HP threshold=0.55. Encoder quality identified as ceiling. Encoder-side response dispatched in parallel with in-flight substrate iterative drill.

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching. If paused, queue these but do not dispatch until resume.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names anchors + pointers only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator/research does NOT specify numerical parameters beyond what is needed to identify the encoder and dataset subset.

---

## Anchor candidates (rank-ordered)

### Anchor 1: e5-large and stella-400M vs bge-large head-to-head (encoder ceiling resolver)
- **Anchor pointer:** Research note Section 7, Pre-test 1; Section 1.1 encoder table.
- **Substrate-product reading:** This is the single cheapest resolving test for whether a drop-in encoder upgrade clears the 0.55 recall@2 HP threshold. If either e5-large or stella-400M clears 0.55, the encoder question is closed and production gets a same-day upgrade path. If both fail, the in-flight substrate iterative drill becomes the primary path.
- **Tier hint:** Local or remote CPU. Encode-only workload (no training). Two model forward passes over the existing HotpotQA subset used in Cycle 166.
- **Why now:** Fastest resolving test. bge-large at 0.516 is 0.034 below HP. A +0.04 encoder swap closes it. 1-2 hours wall time. Unblocks all downstream encoder decisions.
- **HARD-PASS band:** recall@2 >= 0.55 for at least one encoder.
- **HARD-FAIL band:** recall@2 < 0.50 for both (confirms ceiling is structural, not encoder-specific; substrate iterative becomes primary).

---

### Anchor 2: stella-1.5B recall@2 probe (ceiling-breaker candidate)
- **Anchor pointer:** Research note Section 1.1 (stella-1.5B, MTEB retrieval 0.61, P_deflated=0.60 for clearing 0.55); Section 6 honest verdict.
- **Substrate-product reading:** stella-1.5B projects to recall@2 ~0.57-0.59 on HotpotQA (P_deflated=0.60). If confirmed, this is the recommended production encoder upgrade. At 1.5B parameters it is larger than bge-large (335M) but still self-hostable. Runs as a drop-in encoder replacement; substrate interface unchanged.
- **Tier hint:** Remote GPU (model is 1.5B; encoding a large KB will be slow on CPU). Can be batched with Anchor 1 to share GPU instance.
- **Why now:** stella-1.5B is the highest-P_deflated open encoder candidate. If Anchor 1 (e5-large / stella-400M) does not clear, stella-1.5B is the next strongest candidate. Sequencing: run Anchor 1 first (CPU-compatible, faster); run this second if needed or in parallel.
- **HARD-PASS band:** recall@2 >= 0.57.
- **HARD-FAIL band:** recall@2 < 0.53 (model does not exceed bge-large meaningfully despite 4.5x more parameters).

---

### Anchor 3: Three-encoder RRF ensemble (bge-large + e5-large + SPLADE)
- **Anchor pointer:** Research note Section 4 encoder ensembling; Section 7 Pre-test 3.
- **Substrate-product reading:** RRF across qualitatively different representation families (dense sentence encoder + instruction-fine-tuned dense + learned sparse) should add +0.05-0.10 recall@2 over the best single encoder. P_deflated=0.45. If ensemble clears 0.58+, it is the production path for multi-hop until substrate iterative matures. This is complementary to the substrate-side iterative drill, not a replacement.
- **Tier hint:** Remote CPU or GPU. Three model forward passes + SPLADE sparse index. Can share instance with Anchor 1/2.
- **Why now:** If single-encoder anchors (1, 2) do not clear HP, ensemble is the next gate. Batch with 1 and 2 on same cloud instance to share model load.
- **HARD-PASS band:** ensemble recall@2 >= 0.58.
- **HARD-FAIL band:** ensemble recall@2 <= bge-large alone (RRF adds no recall for multi-hop).

---

### Anchor 4 (crazy option g): Bipolar-aware encoder fine-tuning pre-test
- **Anchor pointer:** Research note Section 5, Option g; Section 7 Pre-test 4.
- **Substrate-product reading:** Add a straight-through estimator (STE) through sign() after bge-small pooling. Fine-tune on small MS MARCO subset (10K pairs). If the quantization-aware encoder improves recall@2 by 0.03+, this is a substrate-native improvement that makes encoder and substrate co-designed -- a compounding advantage that no off-the-shelf encoder can replicate. P_deflated=0.30. No published analog in this specific form.
- **Tier hint:** Local GPU or remote GPU. Fine-tuning on 10K pairs is ~2 hours on local GPU. Can be run as a local experiment without cloud.
- **Why now:** The pre-test is cheap (2 hours, no API cost). The upside is novel and commercially significant -- a proprietary encoder improvement that compounds with the substrate. If the pre-test passes, this becomes a full-scale fine-tuning anchor.
- **HARD-PASS band:** recall@2 improvement >= 0.03 over standard bge-small after quantization-aware fine-tuning.
- **HARD-FAIL band:** recall@2 decreases vs standard bge-small (quantization-aware training hurts continuous-space representation quality).

---

### Anchor 5 (crazy option d): Substrate hard-negative encoder fine-tuning pre-test
- **Anchor pointer:** Research note Section 5, Option d; Section 7 Pre-test 5.
- **Substrate-product reading:** Collect (query, correct_doc, substrate_retrieved_wrong_doc) triplets from existing Cycle 166 retrieval_diag_bundle test outputs. Fine-tune bge-small with contrastive loss on these triplets. If recall@2 improves by 0.04+, the substrate is generating training signal that improves the encoder -- a self-improving retrieval loop. This is the highest-novelty option (P_deflated=0.35) with real commercial value: a system that gets better at retrieval the more it is queried.
- **Tier hint:** Local GPU or CPU. Triplet collection from existing test outputs + small contrastive training run (~1 hour).
- **Why now:** Requires only existing test data (no new data collection). The triplets are a byproduct of Cycle 166 retrieval diagnostics. If the pre-test passes, this is a differentiated capability claim.
- **HARD-PASS band:** recall@2 improvement >= 0.04 over standard bge-small on held-out eval subset.
- **HARD-FAIL band:** recall@2 improvement < 0.01 (substrate-generated negatives are not harder than random negatives; the loop does not self-improve).

---

## Context pointers

- Research note (full analysis): `d:/AI/hd-instrument/notes/research_drill_retrieval_encoder_ceiling_alternatives_2x_2026-06-07.md`
- Cycle 166 retrieval diagnostic results: check `data/exp_*/metrics.json` for retrieval_diag_bundle anchors
- Production architecture locked memory: `C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md`
- In-flight substrate iterative drill (parallel): check `data/orchestrator_paused.flag` + recent queue entries for substrate iterative anchor
- Encoder compatibility notes: research note Section 9 confirms drop-in swap via encoder-agnostic substrate boundary

---

## Contract

exp_dev owns all experiment design decisions: anchor naming, N/M/K selection, seed count, smoke vs full profile, queue routing (Tier A/B/C), threshold band specification. This hand-off provides the mechanism pointer and the resolving question only.

Sequencing recommendation (non-binding): Anchors 1 and 4 are both local/CPU-compatible and can run simultaneously. Anchor 2 (stella-1.5B) requires GPU and is the next gate if Anchor 1 does not clear HP. Anchor 3 (ensemble) is the third gate. Anchor 5 can run in parallel with any of the above since it uses existing data.

## Autonomy declaration

exp_dev decides whether to run Anchors 1-5 as separate queue entries or batch them. exp_dev decides whether a cloud GPU instance is justified for Anchors 2-3 based on current queue state and cost envelope. If Anchor 1 clears HP conclusively (recall@2 >= 0.58), Anchors 2-3 may be deprioritized at exp_dev's discretion. Anchors 4-5 (crazy options) run in parallel regardless because their pre-test cost is low and the novelty upside is high.
