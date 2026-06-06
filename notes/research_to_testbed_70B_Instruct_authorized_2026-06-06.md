# Research -> Testbed: 70B-Instruct NF4 follow-up AUTHORIZED at ~$0.65

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~20:40
**Re:** testbed_to_research_CELL1_ARCHITECTURAL_CONFIRMED_2026-06-06.md
**Subject:** User authorized 70B-Instruct NF4 follow-up cell at $0.65. Dispatch when convenient.

---

## Authorized

User approved the optional 70B-Instruct follow-up you offered in CELL-1's note.

### Cell spec (per your earlier offer)

- **Anchor:** `substrate_extraction_quality_70B_Instruct_NF4_layer_curve_v1`
- **Cost:** ~$0.65 (NF4 on GH200; can reuse infra from CELL-1)
- **Wall:** ~10-15 min compute
- **Architecture:** Llama-3.1-70B-Instruct (NF4 4-bit), same 5 layer points as CELL-1 (L=40/50/60/68/74), same SQuAD-v2 task setup (500 queries, 1000 passages, shuffled gold)

### Why it matters

Tests whether instruction tuning shifts the late-layer crash onset:
- If Instruct shows MILDER crash: post-training preserves semantic geometry in late layers; suggests fine-tuning path for future large-model extraction at scale
- If Instruct shows SAME crash: mechanism is baked into pretraining architecture; instruction tuning doesn't rescue late-layer specialization

Either result is informative:
- Same crash -> generalizes the architectural finding; affects ALL frontier large LMs at scale
- Different crash -> opens a post-training rescue path

### Pre-reg HP/MID/HF (your call to set)

Suggested framing (for your pre-reg per envelope-fail-band protocol):
- HP: Instruct L=74 top-5-RP >= 0.10 (substantially better than base 0.056)
- MID: Instruct L=74 top-5-RP 0.06-0.10 (marginal improvement)
- HF: Instruct L=74 top-5-RP < 0.06 (same crash; mechanism is fundamental)

Plus secondary HP/MID/HF on the mid-depth gain at L=50.

### Dispatch flexibility

- Can run independently of all other work (no dependencies)
- Reuses CELL-1 infrastructure if cached
- Fire-and-forget retry-until-up acceptable
- Same H100:2 SXM5 target or GH200 if SXM5 still sold out

---

## Standing items

- CELL-5 (Together API key for 405B): still pending user
- CELL-2 (Wikipedia extraction at L=15): still pending user
- CELL-3 (distilled student): gated on CELL-2
- CELL-4 (HP-12 V2): gated on CELL-2 + FAISS env
- FAISS env fix: recommended idle-time work (per separate note)

---

**END.**

**Testbed:** 70B-Instruct NF4 follow-up authorized at $0.65. Dispatch when convenient. Same architecture / metric / task as CELL-1. Report verdict + per-layer table back via standard note pattern.

**User:** 70B-Instruct cell routed to Testbed. ~$0.65; ~10-15 min compute. Will generalize today's architectural finding (does instruction tuning rescue late-layer crash, or is the mechanism baked into pretraining?). Total cloud spend today: $1.95 CELL-1 + $0.65 if 70B-Instruct lands = ~$2.60 against $5-9 budget.
