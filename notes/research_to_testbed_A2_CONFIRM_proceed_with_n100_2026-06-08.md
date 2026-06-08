# Research -> Testbed: A2 Llama-8B Path B CONFIRM proceed; recommend n=100 not n=60

**From:** Research  **Date:** 2026-06-08 ~09:55  **Re:** Testbed verification request on
A2 priority before cloud dispatch.

## Three confirmations

### 1. HP gate still recall@2 >= 0.55? CONFIRMED
Same threshold as:
- notes/research_to_exp_dev_path_B_GPU_dispatch_clarification_2026-06-08.md
- notes/research_to_exp_dev_extractor_escalation_AUTHORIZE_2026-06-08.md
- notes/research_to_exp_dev_iterative_drill_5_anchors_AUTHORIZE_2026-06-08.md (I2 anchor)

No newer Research note has changed the gate. 0.55 maps directly to HippoRAG / BridgeRAG
class performance.

### 2. Sample size — RECOMMEND BUMP TO n=100
You're correct that 95% CI on 0.55 with n=60 is ~±0.13 (wider than load-bearing
threshold). For a v1.5 customer-pitch claim, that's not tight enough.

**Recommendation: bump to n=100.** 95% CI tightens to ~±0.10. Incremental cost is
minor (n=100 is ~1.67x n=60 = same compute lane on GH200; ~$8-10 total vs $5-7).

If even tighter CI desired, could do n=150 (CI ~±0.08), but n=100 is the sweet spot
for first-pass HP/HF determination. If A2 BORDER at n=100, escalate to n=150 + Llama-70B.

### 3. Multi-hop revival mandate STANDING — and contingencies are clear
Per yesterday's user mandate + today's cycle 181 convergence:

**State after cycle 178+181:**
- PP-99 single-shot + LLM attention on fuzzy bge: -0.023 of RAG (matches transformers) — VALIDATED
- Substrate K-hop on clean bindings: K=12 recovery=0.987; oracle HotpotQA = 1.0 — VALIDATED
- The OPEN question is: does Llama-8B extractor produce traversable KGs from HotpotQA passages?

**A2 contingencies:**
- HP (recall@2 >= 0.55): substrate ships KG-QA at HippoRAG/BridgeRAG class; v1.5
  free-text multi-hop revival path validated; pitch upgrade adds "categorical
  substrate-K-hop multi-hop on free-text via 8B extractor at 10-30x downstream cost"
- HF (recall@2 < 0.55): substrate's free-text multi-hop is fundamentally extractor-
  bound at 8B class; PP-99 path still ships at RAG parity; structured-KB v1.5 still
  wins categorically; pitch becomes "substrate is multi-hop ready; free-text path
  requires 70B+ extractor or structured-input domain"
- BORDER (0.45-0.55): escalate to Llama-3.1-70B as quality calibration

Either outcome leaves substrate's multi-hop story defensible. HP is the bigger pitch
win; HF still ships v1 + v1.5 cleanly.

## Plan

PROCEED with A2 cloud dispatch at n=100. Cost envelope ~$8-10 (well within $20-50
authorized).

D1 (T5-1) + E2 (Wish 2 multimodal) hold for after A2 verdict per user "do a2 alone
first" directive.

## Cross-references
- Testbed verification request: notes/testbed_to_research_a2_llama8b_priority_verify_2026-06-08.md
- Path B clarification: notes/research_to_exp_dev_path_B_GPU_dispatch_clarification_2026-06-08.md
- Extractor escalation: notes/research_to_exp_dev_extractor_escalation_AUTHORIZE_2026-06-08.md
- v1.5 LOCK-IN batch: notes/exp_dev_handoff_research_v1.5_LOCK_batch_2026-06-08.md
- Cycle 181 multi-hop convergence: notes/orchestrator_to_research_results_summary_2026-06-08_cycle181.md

---

**Testbed:** PROCEED A2 at n=100, single dispatch (no D1/E2 batching per user "a2 alone
first"). Sample-size bump approved by Research; cost-control flag acknowledged.
