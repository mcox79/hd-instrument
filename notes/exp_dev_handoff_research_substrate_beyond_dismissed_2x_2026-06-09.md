# exp_dev hand-off -- research: substrate beyond previously-dismissed capabilities (2x drill)

Filed-by: research sub-agent
Trigger: notes/research_drill_substrate_beyond_dismissed_2x_2026-06-09.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and WHY, not sweep grids, threshold formulas, or queue choices.

---

## Anchor Candidates (rank-ordered, cheapest decisive first)

### 1. analogy_map_b_n16384_v1024 (TIER 1 -- cheapest, highest P, already designed)
- Anchor pointer: analogy_map_b_n16384_v1024
- Substrate-product reading: FHRR 3-operation analogy (A XOR B XOR C_hat -> nearest codebook atom) confirms analogical reasoning as a substrate-native capability class. A:B::C:? on 100 analogy pairs. If HARD-PASS, product narrative gains "structured analogical reasoning without any external model" -- differentiates from pure retrieval systems.
- Tier hint: CPU smoke, ~5 min wall; Tier-1 (capability class opener, confirmed algebraic path)
- Why now: K=1 hop + FHRR bind are both confirmed; analogy is mechanistically 3 ops on top of those; highest ROI per wall-second of any open capability question on this drill; anchor already designed per research_drill_substrate_native_reasoning_capability_expansion_2026-06-06.md
- HARD-PASS: accuracy >= 0.70 at N=16384 on 100 analogy pairs
- HARD-FAIL: accuracy < 0.50

### 2. vision_bind_clip_n4096_m100_v512 (TIER 1 -- cross-modal capability opener)
- Anchor pointer: vision_bind_clip_n4096_m100_v512
- Substrate-product reading: CLIP image embedding projected to FHRR space, bound with text label atoms, recovered at query time. If HARD-PASS, product gains "substrate stores any-modality facts with algebraic audit" -- not just text. Opens the cross-modal provenance product story. Gates the multimodal_multihop chain.
- Tier hint: CPU smoke with pre-computed CLIP vectors (~5 min); Tier-1 (capability class opener)
- Why now: text-KG binding is confirmed at 1.000 (v430); image extension is one linear projection away; ConceptNet + Wikipedia ingestion already in progress on testbed (same encoder infrastructure); cross-modal binding was listed as PARTIAL in cap_map v430 -- this closes it
- HARD-PASS: cosine_sim(recovered_image_atom, original) >= 0.80 at N=4096 on 100 image-label pairs
- HARD-FAIL: cosine_sim < 0.70

### 3. defeasible_revision_khop_n16384_k3_v1024 (TIER 1 -- integration of confirmed components)
- Anchor pointer: defeasible_revision_khop_n16384_k3_v1024
- Substrate-product reading: contradiction detected (PP-180 confirmed) -> automatic edit of conflicting binding -> K=3 hop query post-revision returns consistent result. Demonstrates non-monotonic belief revision as a product capability: "substrate automatically corrects itself when contradictions are found." No LLM required.
- Tier hint: CPU; ~10-20 min wall; Tier-1 (integration demonstrator, all components confirmed)
- Why now: PP-117 negation exact, PP-180 contradiction 1.0/0.0, memory_editing all confirmed independently; the INTEGRATION is the only untested piece; 1-2 day engineering task; high-leverage product narrative
- HARD-PASS: post-revision K-hop accuracy >= 0.85 on a 10-fact K=3 chain test set
- HARD-FAIL: accuracy < 0.70

### 4. tom_firstorder_tenant_n16384_nagents4_v256 (TIER 1 -- first-order ToM via multi-tenant)
- Anchor pointer: tom_firstorder_tenant_n16384_nagents4_v256
- Substrate-product reading: 4 agents, each with tenant-partitioned W, each storing different beliefs about the same world. Querying "what does agent A believe about fact X?" returns agent A's stored belief, not the ground-truth world state. Demonstrates first-order theory of mind as a substrate-native capability.
- Tier hint: CPU; ~15-30 min wall; Tier-1 (capability class demonstration)
- Why now: multi-tenant isolation is confirmed at production scale (zero cross-leak); ToM framing is a 1-sentence restatement of confirmed capability; high product narrative value for multi-agent, negotiation, and social simulation applications
- HARD-PASS: tenant-query accuracy >= 0.80 on a 4-agent, 100-fact-per-agent test
- HARD-FAIL: accuracy < 0.60 (cross-tenant leak) or <0.70 (wrong-agent belief returned)

### 5. counterfactual_self_model_n16384_k3_v512 (TIER 2 -- meta-cognitive demo)
- Anchor pointer: counterfactual_self_model_n16384_k3_v512
- Substrate-product reading: delete a fact from substrate (GDPR erase, 0.0004ms), then query what K=3 hop chains are affected. "Substrate can audit what it would know if a fact were removed." No LLM can do this with algebraic guarantees.
- Tier hint: CPU; ~20-30 min wall; Tier-2 (meta-cognitive capability, integration of confirmed components)
- Why now: GDPR deletion + K-hop + Merkle audit all confirmed; integration gap only; high product narrative value for compliance/regulated use cases
- HARD-PASS: post-deletion K-hop accuracy (non-affected chains) >= 0.90; affected chains correctly return no result or alternative path
- HARD-FAIL: accuracy < 0.65 on affected-chain detection

### 6. spatial_relation_hop_n16384_k3_v256 (TIER 2 -- capability framing extension)
- Anchor pointer: spatial_relation_hop_n16384_k3_v256
- Substrate-product reading: (OBJECT_A, ABOVE, OBJECT_B) + (OBJECT_B, LEFT_OF, OBJECT_C) -> K=2 hop -> (OBJECT_A, ABOVE_LEFT_OF, OBJECT_C). Validates discrete 3D spatial relation reasoning as substrate-native. Extends K-hop from abstract facts to spatial domain.
- Tier hint: CPU; ~10-15 min wall; Tier-2 (domain extension of confirmed K-hop)
- Why now: K=3 multi-hop is confirmed at high accuracy; spatial relation triples are structurally identical to fact triples; 1-2 day engineering task
- HARD-PASS: spatial relation chain accuracy >= 0.75 on a 50-chain test set
- HARD-FAIL: accuracy < 0.60

### 7. affect_tagged_retrieval_n4096_v512_nrc (TIER 2 -- product differentiation for emotional applications)
- Anchor pointer: affect_tagged_retrieval_n4096_v512_nrc
- Substrate-product reading: bind text atoms with NRC valence atoms (positive/negative/arousal), then query with emotional context vector to retrieve emotionally-matched content. Demonstrates substrate as an emotionally-aware retrieval engine for counseling, therapy, and user-support products.
- Tier hint: CPU; ~10 min wall; Tier-2 (product differentiation)
- Why now: per-strength sharding (PP-107 AUC=0.96) is the mechanism; NRC lexicon is public domain; 2-3 day engineering task with clear HF boundary
- HARD-PASS: Pearson r >= 0.60 between substrate affect retrieval rankings and human affect ratings on NRC test set
- HARD-FAIL: r < 0.45

### 8. style_conditioned_bias_n4096_nauthor4_v512 (TIER 2 -- LLM augmentation story)
- Anchor pointer: style_conditioned_bias_n4096_nauthor4_v512
- Substrate-product reading: PPMI atoms extracted from 4 author corpora; author identity bound as style atoms; at generation time, style-conditioned retrieval bias shifts LLM output toward author-typical completions. Demonstrates substrate as a style controller for LLM generation.
- Tier hint: CPU; ~15-20 min wall; Tier-2 (LLM coupling extension)
- Why now: R3 concept-conditioned readout confirmed (+0.032 bpc); style conditioning is the same mechanism with author-specific atoms; 2-3 day engineering
- HARD-PASS: bpc delta (style-conditioned vs unconditioned) >= 0.010 on author-corpus held-out test
- HARD-FAIL: delta < 0.003 (noise)

### 9. timeseries_ngramsubstrate_n4096_window30_v64 (TIER 3 -- cross-modal expansion)
- Anchor pointer: timeseries_ngramsubstrate_n4096_window30_v64
- Substrate-product reading: 30-day financial time-series window binned into 64 value atoms + position atoms; pattern stored in substrate; query retrieves most-similar historical patterns. Demonstrates substrate as a time-series pattern memory with algebraic provenance.
- Tier hint: CPU; ~10-15 min wall; Tier-3 (cross-modal extension)
- Why now: n-gram language modeling mechanism confirmed; time-series n-grams are the same mechanism on a different vocabulary; ConceptNet + Wikipedia ingest shows substrate handling large diverse corpora
- HARD-PASS: pattern retrieval precision >= 0.65 on held-out financial time-series test
- HARD-FAIL: precision < 0.50

### 10. multimodal_multihop_n4096_k3_v512 (TIER 3 -- gated on vision_bind_clip passing)
- Anchor pointer: multimodal_multihop_n4096_k3_v512
- Substrate-product reading: image -> FHRR image_entity_atom -> K=3 hop over KG -> answer atom. "Substrate answers questions about images by multi-hop reasoning over stored knowledge, with cryptographic audit trail." Differentiates from vision-language models (no audit, no algebraic certificates).
- Tier hint: GPU preferred (CLIP inference); ~30-60 min wall; Tier-3 (frontier capability, gated)
- Why now: CONDITIONAL on vision_bind_clip PASSING; K=3 multi-hop confirmed; cross-modal first step is the extension
- HARD-PASS: image->answer accuracy >= 0.65 on a 50-question visual QA test set (where answer is in KG)
- HARD-FAIL: accuracy < 0.45 OR vision_bind_clip fails (auto-block)

---

## Context Pointers

- Research note: notes/research_drill_substrate_beyond_dismissed_2x_2026-06-09.md
- Prior reasoning handoff (inspiration): notes/exp_dev_handoff_research_substrate_native_reasoning_2026-06-06.md
- Analogy anchor already designed: see notes/exp_dev_handoff_research_substrate_native_reasoning_2026-06-06.md anchor 1
- T5C PATH B KBLaM: notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md section "PATH B CORRECTED"
- Cross-modal binding v430: data/exp_substrate_multimodal_binding_text_kg_v1/metrics.json
- Multi-tenant isolation: data/exp_pp13_*/metrics.json or equivalent
- K-hop K=10 confirmed: data/exp_khop_*/metrics.json
- STRIPS D=10: data/exp_strips_*/metrics.json
- ConceptNet 8M loading: see testbed overnight chain MEMORY.md entry 2026-06-09
- PP-107 graded confidence: data/exp_pp107_*/metrics.json
- PP-117 negation: data/exp_pp117_*/metrics.json
- PP-180 contradiction: data/exp_pp180_*/metrics.json
- GDPR erasure: data/exp_pp9_*/metrics.json or similar
- Merkle audit: data/exp_pp184_*/metrics.json or similar

---

## Contract

exp_dev's job: design anchors, set pre-reg thresholds (already pre-registered above), ship to queue, verify post-ship.
Orchestrator's job: decide which anchors to activate and when.
This file is a ranked option list -- not a dispatch order.

## Autonomy declaration

Research has pre-registered all HARD-PASS and HARD-FAIL thresholds above. Exp-dev has full autonomy to dispatch any anchor in TIER 1 without further approval. TIER 2 and TIER 3 anchors require orchestrator confirmation or the standard queue-refill cadence decision. The multimodal_multihop anchor (rank 10) is explicitly GATED on vision_bind_clip passing -- do not dispatch multimodal_multihop unless vision_bind_clip returns cosine_sim >= 0.80.
