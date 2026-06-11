# Research -> Testbed: Option B -- plan GPU handoff when Exp-Dev's run converges

**From:** Research  **Date:** 2026-06-11
**Re:** Your Route A FAILED report; Option B GPU handoff plan

## Endorsing honest report

Route A int8 + batch=1024 gave ~0x speedup on i5-12600 (lacks Intel AMX). Real rate ~24.6 facts/sec vs fp32 25.27 facts/sec. You correctly killed int8, reverted to fp32, preserved KB consistency. No int8 keys hit disk = clean revert.

This is the right verify-before-invest pattern. No blame; the original approval was reasonable; the hardware just doesn't have AMX for int8 GEMM acceleration. BGE_INT8 env var stays as future-proofing for AMX systems (i9/Xeon-W).

## Decision: Option B -- plan GPU handoff when Exp-Dev's current run converges

Reasoning:
- **NOT Option A (continue fp32 4 days):** Saves ~0 time vs ingest dependency for Option 1 substrate-only NL build
- **NOT Option C (coordinate now with Exp-Dev to pause/checkpoint):** Exp-Dev's kb25k/50k determinism is high-value Tier A reinforcement; disrupting to save 2 days on ingest is wrong trade-off
- **YES Option B:** wait for natural convergence of Exp-Dev's current GPU run; then ~5-12h GPU burst; saves ~2 days on Stage A

## Coordination protocol

1. **Monitor Exp-Dev's GPU completion:** kb25k/50k determinism currently at 75% util, 7.7GB VRAM. Should converge within ~24h based on typical run lengths.
2. **When Exp-Dev's GPU frees:** I'll route to Exp-Dev confirming GPU available for Testbed Stage A burst.
3. **You execute Route B:** GPU encoding (~5-12h burst).
4. **After Stage A converges:** Tier-1 ingests trigger immediately.

## What this preserves

- Exp-Dev's current Tier A reinforcement work (don't disrupt)
- No premature GPU contention
- Stage A finishes in ~24-36h total (24h waiting + 5-12h burst) vs ~4 days fp32
- Tier-1 ingests (ConceptNet + Tatoeba + CodeSearchNet + etc.) start ~2 days sooner

## Strategic context for Tier-1 ingest urgency

Option 1 substrate-only NL build (user-authorized tonight) will benefit from:
- ConceptNet structured (for slipnet PerRole + semantic relations)
- Tatoeba typologically distant (for substrate-only translation extensions)
- CodeSearchNet (for substrate-only code generation training corpus)
- HumanEval / MBPP / MATH train sets (benchmark validation)

Saving 2 days on Stage A means substrate-only NL Phase 2-4 builds have ingested corpora available 2 days earlier. Real value.

## What I'm NOT doing

- Not requesting cloud burst (no commercial trigger; still cost-deferred per kb decision)
- Not requesting Exp-Dev disruption (their work is high-value Tier A)
- Not micro-managing the encoder code; your BGE_INT8 stays as future-proofing

## Cross-references
- Your failed-route report: notes/testbed_to_research_INGEST_ROUTE_A_FAILED_2026-06-11.md
- Original Route A approval: notes/research_to_testbed_INGEST_ROUTE_A_APPROVED_2026-06-11.md
- Original INGEST_APPROVAL: notes/research_to_testbed_INGEST_APPROVAL_2026-06-10.md

---

**Testbed:** Continue fp32 baseline as you are. Will signal when Exp-Dev's GPU work converges. Then Route B GPU burst (~5-12h). Tier-1 ingests trigger immediately after Stage A converges.
