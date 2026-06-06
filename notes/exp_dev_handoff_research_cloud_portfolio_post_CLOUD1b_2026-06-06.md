# exp_dev hand-off -- research: cloud-experiment portfolio post-CLOUD-1b

**Filed:** 2026-06-06 by research sub-agent.

**Trigger:** CLOUD-1b HARD_PASS (8B/70B=1.43; 1B/8B=1.14) + Phase 4a layer-10 convention found wrong (correct layer = 92% depth, not 50%). Research note at: `notes/research_drill_cloud_portfolio_post_CLOUD1b_2026-06-06.md`

**Pause state:** Check `data/orchestrator_paused.flag`. If PAUSED, do not ship cloud cells; these are TIER-CLOUD cells routed to Testbed, not local exp_dev queue.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. Testbed / Exp-Dev design ALL of: exact batch size, sweep grids, threshold bands, anchor name suffix, queue choice, ETA. Research does NOT specify numerical parameters beyond what's already in the research note.

---

## What just landed (binding context)

CLOUD-1b returned HARD_PASS at $1.33 total:
- 1B top-5-RP = 0.282 (layer 15, 92% depth)
- 8B top-5-RP = 0.248 (layer 29, 92% depth)
- 70B (NF4) top-5-RP = 0.174 (layer 50, 62.5% depth; crashes at late layers)
- MiniLM-L6-v2 top-5-RP = 0.890 (upper bound)

**CRITICAL:** PHASE4A-6 Wikipedia extraction was spec'd at layer-10 (50% depth for 1B = 8/16 layers). Optimal is layer 15 (92% depth for 1B). ALL Phase 4a extraction specs must use L=15 for 1B or L=29 for 8B. Do not execute any extraction cell at layer-10.

---

## Anchor candidates (rank-ordered; Testbed primary for cloud cells)

### 1. `cloud_2a_fp16_70b_layer_curve_v1` [TIER-CLOUD; AUTHORIZED; Testbed]

- **Anchor pointer:** Research note Section "CELL-1" + `research_to_testbed_CLOUD1b_HP_ack_fp16_70B_followup_authorized_2026-06-06.md`
- **Substrate-product reading:** Disambiguates whether 70B late-layer retrieval crash is NF4 quant artifact or architectural. If quant artifact, cheap-fleet thesis extends to any model size including 70B fp16. If architectural, 1B/8B locked as production extraction models permanently.
- **Tier:** CLOUD (H100:2 required for 70B fp16; ~140 GB VRAM)
- **Why now:** ALREADY AUTHORIZED; ~$3-5; 30-45 min wall; binary binding answer. Optional add-on: 70B-Instruct NF4 at ~$0.65 if combined < $5.

### 2. `cloud_phase4a_6_wikipedia_1b_l15_extraction_v2` [TIER-CLOUD; per-cell auth needed; Testbed]

- **Anchor pointer:** Research note Section "CELL-2" + PRIORITY_QUEUE_LIVE.md TIER-CLOUD section
- **Substrate-product reading:** Full Wikipedia extraction at correct layer (1B L=15 vs prior L=10). $31-50 vs original $200-400 estimate. This extraction is the substrate foundation for HP-12 V2/V3 + all production demos. CRITICAL: Do NOT execute at L=10.
- **Tier:** CLOUD (Lambda CPU workers; 100-worker chunked approach)
- **Why now:** Gated only on CELL-1 result (~30 min wall); can authorize in parallel. Saves $150-370 vs original plan.

### 3. `cloud_phase4a_2_distilled_student_22m_v1` [TIER-CLOUD; per-cell auth needed; Testbed]

- **Anchor pointer:** Research note Section "CELL-3" + `research_drill_encoder_bottleneck_phase4a_infrastructure_2x_2026-06-05.md`
- **Substrate-product reading:** Trains 22-26M student distilled from Llama-3.2-1B AT LAYER 15 (revised from prior L=10 spec). 20-40x extraction speedup for V_c=1M production. PHASE4A-2 layer-match target must be updated from L=10 to L=15.
- **Tier:** CLOUD H100 (~$15; 2-4 hr)
- **Why now:** Gated on CELL-2 extraction completing (provides training data); unlocks all production-scale demos.

### 4. `cloud_cascade_distillation_fd_ratio_smoke_v1` [TIER-CLOUD; per-cell auth needed; Testbed]

- **Anchor pointer:** Research note Section "CELL-5" + prior CLOUD-3 spec in `research_to_testbed_cloud_experiments_list_when_authorized_2026-06-06.md`
- **Substrate-product reading:** Binds whether cascade distillation (405B -> 1B) closes the FD gap. Independent of 1B/8B retrieval question. Relevant for reasoning-quality extraction beyond retrieval.
- **Tier:** CLOUD (~$2-5 API + H100)
- **Why now:** Independent; can dispatch in parallel with CELL-1. Low cost; high-optionality answer.

---

## Context pointers (file paths, not summaries)

- Research note (full portfolio): `d:/AI/hd-instrument/notes/research_drill_cloud_portfolio_post_CLOUD1b_2026-06-06.md`
- CLOUD-1b results: `d:/AI/hd-instrument/notes/testbed_to_research_CLOUD1b_HARD_PASS_2026-06-06.md`
- fp16 70B authorization: `d:/AI/hd-instrument/notes/research_to_testbed_CLOUD1b_HP_ack_fp16_70B_followup_authorized_2026-06-06.md`
- Prior cloud experiments list: `d:/AI/hd-instrument/notes/research_to_testbed_cloud_experiments_list_when_authorized_2026-06-06.md`
- PRIORITY_QUEUE_LIVE.md: `d:/AI/hd-instrument/notes/PRIORITY_QUEUE_LIVE.md`
- Encoder bottleneck drill: `d:/AI/hd-instrument/notes/research_drill_encoder_bottleneck_phase4a_infrastructure_2x_2026-06-05.md`

---

## Contract section

This hand-off is actionable for Testbed (cloud cells) and for Exp-Dev (if any TIER-CLOUD-adjacent local cells surface). Deliverables expected:

- Testbed: execute CELL-1 (fp16 70B, already authorized) first; report per-layer curve; report back to Research + Exp-Dev + Orchestrator via standard note pattern
- After CELL-1: user auth signal for CELL-2 (Wikipedia extraction); then CELL-3 (distilled student); CELL-4 (HP-12 V2) in sequence
- CELL-5 (cascade distillation) can run in parallel anytime; independent

---

## Autonomy declaration

Testbed decides: exact Lambda instance type, batch size, seed count, intermediate checkpoint strategy, timeout, anchor name suffix, final cost vs estimate delta. Research has pre-reg'd the HP/MID/HF threshold bands in the research note; Testbed verifies pre-reg before dispatch and reports honestly.

---

**END.**
