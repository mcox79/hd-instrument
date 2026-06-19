# Research -> Testbed: cloud experiments list for when user authorizes (priority-ordered)

**From:** Research session
**To:** Testbed (cloud-dispatch primary)
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~08:20
**Subject:** Comprehensive cloud-experiments queue. All gated on user authorization per cell/batch. Listed in priority order. Source of truth is `PRIORITY_QUEUE_LIVE.md` (TIER-CLOUD section).

---

## Direct note per process change (2026-06-06 08:05)

Research now owns `notes/PRIORITY_QUEUE_LIVE.md` as single source of truth for queue priority. Testbed should monitor the TIER-CLOUD section there for cloud-dispatch authorization signals.

This note duplicates the cloud-experiments list for your direct reference + adds Testbed-specific context.

---

## 10 cloud experiments rank-ordered

### CLOUD-1: 7B vs 70B extraction quality binding test (TOP PRIORITY when authorized)

- **Anchor:** `substrate_extraction_quality_7B_vs_70B_v1`
- **Cost:** ~$0.50-1.00 cloud H100 (prefill-only mode)
- **Wall:** ~15-20 min
- **Why first:** Gates ALL extraction infrastructure decisions ($31 CPU fleet vs $1 Mac fleet vs continued cloud-H100 baseline). Cheapest decisive test.
- **Setup:** Extract 1K Wikipedia abstracts via 7B (Llama-3-7B or similar) + 70B (Llama-3-70B); build substrate-VQ on each; benchmark retrieval accuracy on standard QA subset
- **HARD-PASS:** 7B substrate retrieval >= 80% of 70B baseline (substrate-purpose adequacy)
- **HARD-FAIL:** 7B < 60% of 70B (need larger models for substrate)
- **Strategic value:** if HP, $31 CPU fleet path dominates for Wikipedia-scale; if HF, M4 Max fleet at $1 electricity is the recommended path

### CLOUD-2: PHASE4A-2 distilled 22-26M student training

- **Anchor:** `substrate_distilled_22m_student_training_v1`
- **Cost:** ~$15 cloud H100
- **Wall:** ~2-4 hours
- **Why:** V_c=1M production scale + 20-40x extraction speedup forever after
- **Setup:** Train 6-layer 768-dim student distilled from Llama-1B layer 10; L2 activation match + InfoNCE contrastive; Wikipedia 100k articles training data
- **Gating:** Exp-Dev handoff training script
- **Status:** Phase 4a infrastructure cell (PHASE4A-2)

### CLOUD-3: SPARSE-CASCADE-SMOKE FD ratio test

- **Anchor:** `substrate_cascade_distillation_fd_ratio_smoke_v1`
- **Cost:** ~$2 cloud API + 4h GPU
- **Wall:** ~4 hours
- **Why:** Validates cascade distillation viability for 405B -> 70B -> 8B -> 1B -> 50M
- **Setup:** FD(fine-tuned-1B, 405B) / FD(off-shelf-1B, 405B) on 5K sentences
- **HARD-PASS:** FD ratio < 0.40 (>60% gap closed)
- **HARD-FAIL:** > 0.70 (cascade doesn't work)
- **Strategic value:** validates 405B Wikipedia digestion at $65 one-time vs $14k/run

### CLOUD-4: Llama-3.1-8B Tier-4 (optional; user previously deprioritized)

- **Anchor:** `substrate_tier4_hopfield_attention_substitution_llama_3_1_8b_v1`
- **Cost:** ~$2-4 cloud H100
- **Wall:** ~30-45 min
- **Why:** Cross-scale (50x param jump from 1B to 8B); strengthens architectural-primitive claim
- **Status:** USER PREVIOUSLY DEPRIORITIZED at 2026-06-05 -- only run if user re-authorizes
- **Setup:** Replicate Tier-4-Llama at 8B with same GQA + RoPE adaptation; SWAP_LAYER=mid

### CLOUD-5: PHASE4A-6 Wikipedia layer-10 cache extraction

- **Anchor:** `substrate_wikipedia_layer10_cache_extraction_v1`
- **Cost:** ~$200-400 cloud H100 (BUT per chunked-extraction drill, could drop to ~$30 with prefill + sparse)
- **Wall:** ~8-10 hours (overnight)
- **Why:** One-time investment; eliminates extraction step for ALL future Wikipedia experiments
- **Setup:** Pre-extract Llama-1B (or distilled-student) layer-10 activations for full English Wikipedia (~6.7M articles); store as compressed npz
- **Status:** Day 6-7 of Phase 4a infrastructure plan; not urgent

### CLOUD-6: HP-12 V2 build at 100K facts

- **Anchor:** `substrate_certified_deletion_demo_medical_100k_facts_v2`
- **Cost:** ~$10-30 cloud (depends on extraction strategy)
- **Wall:** ~2-3 days
- **Why:** HP-12 V1 SHIPPED at 10K + 50 facts; V2 scales to 100K for production credibility
- **Gating:** FAISS env fix + Tier-1 cubic-tensor cell (Slot 2 in PRIORITY_QUEUE_LIVE.md)
- **Setup:** PubMed 100K abstracts + substrate W matrix; cert latency + retention + frontier contrast at scale

### CLOUD-7: Gemma-2-2B per-token extraction (Phase 3 production prep)

- **Anchor:** `substrate_gemma_2b_per_token_extraction_v1`
- **Cost:** ~$5-8 cloud H100 for 10K abstracts; ~$30-50 for 1M
- **Wall:** ~1-2 hours for 10K; ~10-15 hours for 1M
- **Why:** Phase 3 production LLM partner is Gemma-2-2B (per blueprint); distillation-trained from 27B teacher; superior intermediate-layer geometry
- **Setup:** Adapt Llama-1B extraction script for Gemma-2-2B (model_id swap; bf16 native; 26 layers interleaved attention; SentencePiece tokenizer)
- **Gating:** Phase 3 production launch timing

### CLOUD-8: HP-12 V3 build at 1M facts with Gemma-2-2B

- **Anchor:** `substrate_certified_deletion_demo_medical_1m_v3_gemma`
- **Cost:** ~$50-100 cloud
- **Wall:** ~5-10 days
- **Why:** Phase 3 production launch demo (1M-fact medical KB with certified deletion via Gemma-2-2B partner)
- **Gating:** CLOUD-7 (Gemma extraction done) + cubic-tensor empirical (Slot 2)

### CLOUD-9 (BIG): 100 idle M4 Max volunteer fleet POC

- **Anchor:** `substrate_m4_max_fleet_chunked_extraction_poc_v1`
- **Cost:** ~$1 electricity ($0 hardware if volunteer)
- **Wall:** depends on fleet coordination
- **Why:** Validates 333,000x cost reduction claim for 405B Wikipedia
- **Gating:** CLOUD-1 (if 7B quality adequate) + fleet coordination infrastructure first
- **Strategic value:** if HP, the audacious vision unlocks at literally hobbyist budget

### CLOUD-10 (BIG): Full Wikipedia 7B extraction via 100 CPU cloud workers

- **Anchor:** `substrate_wikipedia_7b_full_extraction_chunked_v1`
- **Cost:** ~$31 cloud (per chunked-extraction drill)
- **Wall:** ~7.7 hours
- **Why:** Delivers full Wikipedia substrate at $31; unlocks audacious vision empirically
- **Gating:** CLOUD-1 confirms 7B quality + chunking infrastructure built

---

## How Testbed should consume this

1. Monitor `PRIORITY_QUEUE_LIVE.md` TIER-CLOUD section + this note for changes
2. When user authorizes a cloud dispatch (via direct message or this note's CHANGELOG), execute per spec
3. Report verdict back to Research + Exp-Dev via standard note pattern
4. Research updates PRIORITY_QUEUE_LIVE.md (crosses off + adds follow-ons)

---

## Open Testbed asks (standing; non-cloud)

These are runner-env asks that have been outstanding:
- FAISS HNSW environment fix (Windows OpenMP conflict; blocks HP-12 V2 build)
- Optional Llama-1B weights local download (~30 min + HF token; gates HotpotQA-1B in Tier-3)
- Watchdog fix permanent commit (mentioned in earlier note as committed; please confirm)

---

## Standing items unrelated to cloud

- Orchestrator action on PID zombie kills (separate note: `research_to_orchestrator_INVESTIGATE_AND_KILL_zombie_runners_2026-06-06.md`)
- User HP-12 V1 screen recording (manual task)

---

## Discipline declarations

- Per [[feedback-cloud-only-when-absolutely-necessary]]: cloud cells justified per-cell with cost + strategic value
- Per [[feedback-batch-cloud-experiments]]: where multiple cloud cells share bootstrap (e.g., model load), batch in one cluster
- Per user 2026-06-06 ~08:15: cloud experiments included in live queue + notified to Testbed directly
- ASCII-only

---

**END.**

**Testbed:** 10 cloud experiments rank-ordered. CLOUD-1 (7B vs 70B; ~$0.50-1.00) is highest-priority binding test when user authorizes; gates extraction-infrastructure decisions. CLOUD-2 + CLOUD-3 are Phase 4a infrastructure (~$15-17 total). CLOUD-5/7/8 are larger Phase 3 production prep. CLOUD-9/10 are the audacious-vision cells.

**Exp-Dev:** No change to your lane. PRIORITY_QUEUE_LIVE.md TIER-CLOUD section is informational for you; Testbed primary on cloud.

**Orchestrator:** No change to your lane. Standing for PID kill action per separate note.

**User:** Cloud queue ranked + Testbed notified directly. CLOUD-1 (~$0.50-1.00 binding test) is the highest-value cheap cloud cell whenever you authorize.
