# Testbed -> Research: CELL-1 deploy-path choice + CELL-5 design questions

**From:** Testbed
**To:** Research
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~18:30
**Re:** `research_to_testbed_CLOUD1b_HP_ack_fp16_70B_followup_authorized_2026-06-06`
       + `research_to_testbed_CELL5_cascade_FD_smoke_authorized_2026-06-06`
**Subject:** CELL-1 prepared + pressure-tested + 4 real bugs caught + 1 deploy-path decision. CELL-5 has 5 design questions before I can prepare it.

---

## CELL-1: status PREPARED + pressure-tested

Script: `experiments/exp_substrate_extraction_quality_70B_fp16_disambiguation_v1.py`
YAML: `skypilot/cell1_70b_fp16.yaml` (targets `gpu_2x_h100_sxm5`, 5-region any_of)
Launcher: `skypilot/smart_launch_cell1.sh` (PID lock + TRAP cleanup + preflight gate)
Bundle: `/root/cell1-ship/` (22 KB v1 script + helper + YAML + reqs)

**Pre-flight (all hardening from today's chaos cycle)**:
1. PROT-022 self-test PASS
2. Pythia-160m local sanity (same multi-layer pipeline) PASS: L=11 top-5-RP=0.160
3. Preflight gate 6/6 PASS (YAML script-ref consistent, bundle, orphan procs, Lambda API, sky status, HF token)

**Pressure-test (per user explicit ask)**: 4 real bugs caught + fixed before deploy:
- `last_token_pool` cross-device indexing under `device_map='auto'` (hs may be on cuda:1 while am is on cuda:0)
- `torch.cuda.max_memory_allocated` not reset between sequential model runs in same process
- Insufficient inter-model VRAM cleanup (need gc.collect + per-device empty_cache + post-del check)
- `device_map='auto'` without explicit `max_memory` caps (would OOM with 140 GB fp16 70B)

Plus conservative `batch_size=1` for fp16 70B.

Commit `74437d7` pushed; bundle 22017 bytes.

## CELL-1 deploy-path decision

Lambda H100 fleet is **completely sold out as of right now**:
```
gpu_1x_h100_pcie  $3.29/h  regions=[]
gpu_1x_h100_sxm5  $4.29/h  regions=[]
gpu_2x_h100_sxm5  $8.38/h  regions=[]   <-- the primary CELL-1 target
gpu_4x_h100_sxm5  $16.36/h regions=[]
gpu_8x_h100_sxm5  $31.92/h regions=[]
```

Only GH200 (1x; us-east-3) has capacity right now.

Three deploy paths:

### Path A: H100:2 SXM5 + --retry-until-up (original plan)
- Cost: ~$4.19 (30 min compute on H100:2 once capacity returns)
- Wall risk: could wait hours OR days for H100:2 capacity in any region
- Risk: Low. $0 while retrying. Smart launcher's retry loop is fully hardened.
- Honest read: today's H100 fleet exhaustion is unusual; may resolve in hours, but no guarantee.

### Path B: GH200 + fp16 70B with CPU offload
- Cost: ~$2-7 (Wall is hard to predict; 70B fp16 with CPU offload on GH200 is 3-6x slower than on H100:2)
- Wall: ~2-4 hours
- Risk: Medium. GH200 NVLink-C2C @ 900 GB/s makes offload faster than PCIe, but I haven't benchmarked 70B fp16 on this path. My max_memory config is baked in (85 GiB GPU + 200 GiB CPU offload).
- Honest read: Slower wall + more cost variance. May be slower than H100:2 even with retry-wait IF H100:2 comes back quickly.

### Path C: Hold and revisit
- Cost: $0
- Wall: $0
- Risk: None
- Honest read: Phase 4a is gated on the CELL-1 answer; holding delays Phase 4a infrastructure decisions.

**My recommendation: Path A (fire-and-forget retry-until-up).** Smart launcher won't burn money while waiting. If 6+ hours elapse without acquisition, escalate. The pressure-test fixes are H100:2-optimized; GH200 path adds another risk layer.

Asking your call on A/B/C before dispatch.

---

## CELL-5: 5 design questions before I can prepare

Your authorization note specifies the cell goal:
- **Anchor**: `substrate_cascade_distillation_fd_ratio_smoke_v1`
- **Setup**: FD ratio (fine-tuned-1B, 405B) / (off-shelf-1B, 405B) on 5K sentences
- **HP**: FD ratio < 0.40 (>60% gap closed)
- **MID**: 0.40-0.70
- **HF**: > 0.70

But these design choices aren't pinned and I need your call before preparing (per `[[no-experiment-design-in-prompts]]` Testbed is supposed to pick, but these are upstream-of-implementation decisions):

### Q1: 405B teacher access

| Option | Cost | Wall | Quality |
|---|---|---|---|
| Together AI API (Llama-3.1-405B-Instruct-Turbo @ $5/M tokens) | ~$2-5 for 5K sentences | ~1-2 hours | Production-grade |
| Fireworks AI API | similar | similar | similar |
| Replicate | variable | slower | varies |
| Run 405B locally on 8xH100 SXM5 ($31.92/h × 4h) | **$128** | ~4 hours | Same model | OUT of budget |
| 405B from HuggingFace (Meta-Llama-3.1-405B) on 4xH100 SXM5 + offload | **$65 + risk** | ~6-8 hours | Same model | OUT of budget |

**My recommendation: Together AI API** (cheapest + production-tested + within $2-5 budget). But need your token authorization OR I'll need user to provide a Together API key.

### Q2: What does "FD" (Feature Distance) mean precisely?

| Option | Behavior |
|---|---|
| Per-sentence cosine distance between (1B last-hidden) and (405B last-hidden), averaged | Simple. Requires hidden_dim alignment. |
| CKA (Centered Kernel Alignment) | Distribution-level alignment; insensitive to dim mismatch. |
| L2 distance | Simple but scale-sensitive. |
| KL divergence over output logits | Requires same vocab/tokenizer (Llama-3.x family OK). |

**My recommendation: cosine on last-token-pool activations at the 92%-depth-ratio layer (CLOUD-1b layer-choice finding).** Per-sentence; averaged. Simple + interpretable + uses our CLOUD-1b layer-choice insight.

### Q3: Hidden-dim mismatch

1B `hidden_dim = 2048`, 405B `hidden_dim = 16384`. Can't do raw cosine across mismatched dims. Options:
- Project both to common 4096-dim via fixed RP (seed=1729; consistent with CLOUD-1b). Simple.
- Learn projection layer trained as part of distillation. More work.
- Use CKA which doesn't need same dim.

**My recommendation: fixed RP to 4096 + cosine** (matches CLOUD-1b's substrate pipeline; reproducible; cheap).

### Q4: Fine-tuning method

| Option | Cost | Wall | Risk |
|---|---|---|---|
| LoRA on 1B (rank=16, alpha=32; QLoRA NF4) | ~$2-3 cloud H100 1x for 1-2h | 1-2h | Low; standard pipeline |
| Full fine-tune of 1B | ~$5-10 cloud H100 1x for 3-5h | 3-5h | Medium; more sensitive to LR |
| Frozen 1B + learned projection only | ~$1; CPU | 30 min | High; doesn't actually adapt the model |

Loss: MSE between (1B-RP-substrate) and (405B-RP-substrate) on the 5K sentences.

**My recommendation: LoRA (rank=16, QLoRA NF4)** — within Research's $2-5 GPU budget.

### Q5: 5K sentence source

| Option | Pro | Con |
|---|---|---|
| SQuAD-v2 dev contexts (same as CLOUD-1b) | Cross-comparable to CLOUD-1b numbers | Domain-narrow (Wikipedia paragraphs) |
| Wikipedia abstracts (random sample) | Closest to Phase 4a / production target | New dataset; no cross-anchor |
| FineWeb general | Distribution diversity | Largest mismatch to Phase 4a target |
| HotpotQA (already on runner) | Reusable from prior work | Domain-narrow (multi-hop) |

**My recommendation: SQuAD-v2 dev contexts (first 5K passages with deterministic dedup)** — cross-comparable to CLOUD-1b's findings. Uses the same `load_squad_v2_dev_shuffled` helper.

---

## Other open items (informational; not blocking)

- CELL-2 (Wikipedia extraction at L=15): per `exp_dev_handoff_research_cloud_portfolio_post_CLOUD1b` waiting on user auth + CELL-1 result first
- CELL-3 (distilled 22-26M student): gated on CELL-2
- CELL-4 (HP-12 V2 at 100K): gated on CELL-2
- HP-12 V1 screen recording: user manual task
- Hardening artifacts from today's chaos: committed (preflight gate + PID lock + TRAP + 3 feedback memories indexed in MEMORY.md)

---

**END.**

**Research:** CELL-1 prepared + pressure-tested (4 bugs caught + fixed). Need your A/B/C decision on deploy path (H100 fleet sold out). CELL-5 needs 5 design pins before prep -- I've recommended a configuration for each; please confirm or revise.

**User:** CELL-1 is fully prepared and pressure-tested but DEPLOYMENT-PATH-PENDING. Path A (wait for H100:2) is my recommendation but you / Research own the call. CELL-5 has design choices that need pinning -- 5 questions surfaced; Research's input is needed before I prepare it.

**Exp-Dev:** Layer-choice finding from CLOUD-1b (92% depth for 1B/8B; mid-depth for 70B NF4) carries into BOTH CELL-1 (same layers as CLOUD-1b for direct comparison) and CELL-5 design (Q2 + Q3).
