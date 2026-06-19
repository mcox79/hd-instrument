# exp_dev hand-off -- research: substrate cross-modal extension

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: research note d:/AI/hd-instrument/notes/research_drill_substrate_cross_modal_2x_2026-06-09.md

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and context pointers only. exp_dev designs the experiments.

---

## Pause state block

This hand-off is valid regardless of current pause state. Anchors 1-3 are CPU-local and do not require cloud authorization. Anchors 4-5 are CPU-local. Anchors 6-10 require standard queue routing.

---

## Anchor candidates (rank-ordered)

### 1. VISION-CLIP-SUBSTRATE [Priority: SHIP FIRST]
Anchor pointer: embed 1000 CLIP ViT-B/32 image embeddings (512-d float32) into existing FHRR substrate codebook via random complex projection to N=1024. Measure recall@1 and recall@10 for image query and cross-modal text query.
Substrate-product reading: validates whether the text-substrate plumbing extends to vision with zero architectural change. If it works, all other cross-modal anchors are unblocked.
Tier hint: CPU-local smoke, < 2hr wall, $0. Tier-1 by cost.
Why now: cheapest decisive test for entire cross-modal direction. HARD-PASS recall@1 >= 0.80; HARD-FAIL < 0.50.

### 2. AUDIO-WHISPER-SUBSTRATE [Priority: parallel with anchor 1]
Anchor pointer: Whisper base model encoder hidden states (512-d) projected to N=1024 FHRR. Insert 500 audio clips from a public speech dataset (Librispeech). Measure recall@1 for audio query.
Substrate-product reading: validates audio modality path. VoiceHD precedent (88.4% on Isolet) gives positive prior.
Tier hint: CPU-local, ~2hr, $0. HARD-PASS recall@1 >= 0.75; HARD-FAIL < 0.40.
Why now: second cheapest test; independent of anchor 1.

### 3. MULTIMODAL-COMPOSE [Priority: after anchor 1 passes]
Anchor pointer: mixed 500-image + 500-text FHRR corpus. Issue compositional queries using BIND(image_FHRR, attribute_text_FHRR). Measure precision@10.
Substrate-product reading: validates the core cross-modal product differentiator (single algebraic query across modalities). No other system does this at sub-ms latency.
Tier hint: CPU-local, ~4hr, $0. HARD-PASS precision >= 0.70; HARD-FAIL < 0.40.
Why now: this is the product demo claim. Needs to be validated before any customer-facing demo.

### 4. VISUAL-MULTIHOP [Priority: after anchors 1+3 pass]
Anchor pointer: image FHRR -> entity binding lookup -> Wikipedia fact FHRR -> answer retrieval. Test on 100 image-question pairs using existing Wikipedia substrate KB. Measure fact recall.
Substrate-product reading: cross-modal multi-hop is the most differentiated product claim relative to standard multimodal RAG. If this works it justifies the "substrate collapses the fusion layer" positioning.
Tier hint: CPU-local using existing KB, ~1 day. HARD-PASS fact recall >= 0.60; HARD-FAIL < 0.30.
Why now: existing Wikipedia substrate (184K facts) is already deployed. This anchor reuses it.

### 5. SCENE-GRAPH-SUBSTRATE [Priority: independent of anchors 1-4]
Anchor pointer: synthetic 2- and 3-object scenes encoded as SUM(pos_i * obj_i) in FHRR. Resonator network factorization. Test recovery accuracy at k=2,3,4.
Substrate-product reading: compositional visual understanding. Validates that substrate can represent structured visual scenes, not just flat embeddings.
Tier hint: CPU-local, ~1 day, $0. HARD-PASS >= 80% at k=2; HARD-FAIL < 50%.
Why now: resonator is a known technique (Frady 2020) with existing open-source code. Adaptation to FHRR substrate is straightforward.

### 6. CROSS-MODAL-ERASURE [Priority: after anchor 1 passes]
Anchor pointer: insert cross-modal vectors (image + text). Erase one image record. Verify Merkle root update. Confirm erased item not retrievable. Measure erase latency.
Substrate-product reading: GDPR Article 17 erasure works cross-modality. EU AI Act Article 12 compliance argument. Direct product differentiator.
Tier hint: CPU-local, ~1hr, $0. HARD-PASS: erase < 1ms AND no retrieval of erased item. HARD-FAIL: other items affected by erase.
Why now: low cost, high regulatory relevance. EU AI Act Article 12 enforcement August 2026.

### 7. CROSS-MODAL-SCALE [Priority: after anchors 1-3 pass, may need remote CPU]
Anchor pointer: scale mixed image+text codebook to 100K entries. Measure recall degradation vs text-only baseline. Check quasi-orthogonality (via cosine distribution of cross-modal pairs).
Substrate-product reading: production viability at scale. Ensures modality mixing does not degrade retrieval.
Tier hint: remote CPU queue. HARD-PASS: recall degradation < 5%. HARD-FAIL: > 20% degradation.
Why now: scaling behavior is unknown for mixed-modality codebooks. Should be validated before committing to cross-modal production deployment.

### 8. VIDEO-MOMENT [Priority: de-prioritized, GPU required for encoding]
Anchor pointer: temporal binding via permutation (PERMUTE^t applied to frame_FHRR). Bundle clip. Query by timestep. Measure frame retrieval accuracy.
Substrate-product reading: video temporal indexing. Compliance, surveillance, training data provenance use cases.
Tier hint: needs GPU for CLIP/DINO encoding of frames. Remote GPU queue. HARD-PASS: >= 0.70 frame recall; HARD-FAIL: < 0.40.
Why now: lower priority than anchors 1-6. De-prioritize until CPU anchors are validated.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_cross_modal_2x_2026-06-09.md
- Existing substrate KB: Wikipedia 184K facts, ConceptNet 458K facts (see TESTBED OVERNIGHT CHAIN brief in MEMORY.md)
- v195 handoff template: d:/AI/hd-instrument/notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md
- NVSA open-source code: https://github.com/IBM/neuro-vector-symbolic-architectures
- Resonator networks code: rctn.org/bruno/papers/resonator1.pdf (Frady et al.)
- Prior exp_dev brief: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md

---

## Contract

exp_dev owns all experiment design decisions (HP selection, dataset choice, batch size, encoder variant). Research provides literature context and P estimates only. Research does NOT prescribe implementation.

## Autonomy declaration

exp_dev may reorder, split, or combine the above anchors based on queue state and runner availability. Anchors 1-3 are recommended for immediate CPU dispatch. Anchors 7-8 require queue routing decision per cloud-vs-CPU discipline (feedback_route_gpu_vs_cpu_by_torch_not_N.md).
