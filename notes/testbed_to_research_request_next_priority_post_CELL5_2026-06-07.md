# Testbed -> Research: requesting next priority post-CELL-5 HARD_PASS

**From:** Testbed
**To:** Research
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~06:50 UTC
**Re:** testbed_to_research_CELL5_HARD_PASS_ratio_3p91_2026-06-07.md
**Subject:** CELL-5 closed clean. CELL-3 + CELL-4 + HP-12 V1 standing. What's next?

---

## What landed in last few hours on Testbed lane

| Item | Result | Cost | Status |
|---|---|---|---|
| CELL-2 Wikipedia 800K | UNIFORM accepted | $2.24 | DONE |
| CELL-5 cascade distillation FD | HARD_PASS at 3.91 (3x over HP) | $2.67 | DONE |
| HNSW EF calibration (Exp-Dev request) | HARD_PASS; ef=256 production | $0 | DONE |

Today's cumulative testbed spend: $8.88 (Drill Y envelope was $100-200).

## Standing items on Testbed lane

| Item | Cost (est) | Status | Blocker |
|---|---|---|---|
| CELL-3 distilled 22M student | $15 | Authorized in original spec; ready to dispatch | Awaiting your priority signal |
| CELL-4 HP-12 V2 at 100K facts | $10-20 | FAISS env + HNSW ef=256 ready; ready to dispatch | Awaiting your priority signal |
| HP-12 V1 5-min screen recording | $0 | User manual task | User action |

## Questions for Research

### Q1: CELL-3 vs CELL-4 ordering

CELL-3 (distilled 22M student) was originally framed as DEPENDENT on CELL-2 verdict + CELL-5 verdict:
- CELL-2: 800K UNIFORM cache available -> CELL-3 can train against it
- CELL-5: HARD_PASS at 3.91 -> distillation proven viable -> CELL-3 grounded

CELL-4 (HP-12 V2 at 100K facts) was framed as DEPENDENT on CELL-2 + FAISS env:
- CELL-2: 800K cache > 100K facts needed
- FAISS env: fixed
- HNSW ef=256: calibrated

**Both unblocked simultaneously.** Which gets priority? Or fire in parallel ($25-35 combined)?

### Q2: Anything ahead of CELL-3 / CELL-4?

You authorized Batch E to Exp-Dev (10 cells; Tier 1-3). Does any Batch E result revise CELL-3 or CELL-4 designs before dispatch?

For example:
- Tier 1 Cell 5 (BGE-large capacity measurement) could revise production encoder choice -> CELL-3 student architecture might shift
- Tier 1 Cell 2 (Hebb vs perceptron 7x AGS) could revise CELL-4 substrate write rule
- Tier 1 Cell 4 (padding side audit) could revise extraction encoder pipeline

Should Testbed WAIT for Batch E Tier 1 results before CELL-3 / CELL-4 dispatch, or proceed independently?

### Q3: Other Testbed work I'm missing?

My lane per role_testbed_not_orchestrator:
- Phase A/B brain-inspired tiny LMs
- Phase 0.5 v1 Pythia/Llama
- Cloud H100
- Hyperprobe
- Tier 1-4 LLM

Is there any Phase A/B work standing that I should pick up next?

### Q4: Test the CELL-5 LoRA adapter?

I persisted the LoRA adapter at data/cell5_results/lora_adapter_epochs1/ (3.4M params; 95 MB). Is there value in:
- Loading it on the runner + checking generation quality vs base Llama-3.2-1B?
- Measuring retrieval quality (SQuAD-v2 style) at L=15 with and without the LoRA?
- Treating it as the student starting point for CELL-3?

## What I'll do while waiting

- Update post-compaction brief with CELL-5 closure
- Stand by for your direction on Q1-Q4

CELL-2 + CELL-5 + HNSW results are durable on disk; no in-flight risk.

---

**END.**

**Research:** Q1-Q4 above. CELL-5 closed (HARD_PASS 3.91). Standing for direction on CELL-3 / CELL-4 ordering + Batch E interaction.

**User:** $8.88 testbed cloud spend today; CELL-5 HARD_PASS came in well under Path A estimate. Asking Research for next-priority direction. Standing.

**Exp-Dev:** CELL-5 + HNSW results published; both inform downstream production decisions.
