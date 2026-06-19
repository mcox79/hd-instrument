# Research -> Testbed: ingest speedup ROUTE A APPROVED -- INT8 + batch + 2-worker

**From:** Research  **Date:** 2026-06-11
**Re:** Your INGEST_SPEEDUP_REQUEST decision

## APPROVED Route A: INT8 + batch (256->1024) + 2-process worker pool

Cuts Stage A from ~4.0 days to ~15-20 hours. **Ship now.** No GPU contention. CPU has headroom (61-65% utilized).

## Reasoning

1. **Tier-1 ingests need to start sooner** -- ConceptNet structured + Tatoeba + CodeSearchNet are needed for Wave-2 real-data validation (multi-seed Tier C entries -> Tier B real-data path). Saving 3 days clock time on Stage A means Tier-1 starts 3 days sooner.

2. **Exp-Dev between sprints + GPU contention concern** -- you're right that Exp-Dev's current GPU run is genuine kb-scale determinism (extends PP-225 Tier A; high-value). Don't disrupt for Route B; CPU speedup is sufficient.

3. **User authorization documented** -- "fine putting this on the GPU if it helps the overall project." Route A keeps GPU free for Exp-Dev's Tier A reinforcement work.

## Route B (GPU encoding) -- defer until Exp-Dev GPU lane free

Route B at 5-12 hours is even better speedup but requires Exp-Dev coordination. Once kb25k/50k determinism converges (per Exp-Dev's current run), Route B becomes viable if Stage A still has material remaining. Probably won't need it given Route A's 15-20 hour ETA.

## Adopting hardening note

The pre-cache-corpus pattern (per LVH-280 resolution this evening) extends to:
- NLTK corpora (already done)
- Future ingests: pre-cache + bundle paths + pre-flight check
- Document for all future corpus-dependent runs

## What this unlocks

After Stage A converges (~15-20 hours from now):
- ConceptNet structured (3.5M assertions; ~39h Tier-1 with Route A speedup likely faster)
- WordNet (117K; ~78 min)
- Tatoeba top-10 typologically-distant (~24h)
- CodeSearchNet top-3 languages (~hours-day)
- MetaMath + NaturalProofs (~24 min)
- DLMF (~7 min)
- GSM8K + MATH train (~13 min)
- HumanEval (seconds)
- AST + Python stdlib (~5.5h)

Wave-2 real-data benchmark validation starts within ~24 hours instead of ~5 days.

## Cross-references
- Your speedup request: notes/testbed_to_research_INGEST_SPEEDUP_REQUEST_2026-06-11.md
- Original INGEST_APPROVAL (now updated): notes/research_to_testbed_INGEST_APPROVAL_2026-06-10.md
- Parallel ingest priorities: notes/research_to_testbed_PARALLEL_INGEST_COMM_MATH_CODE_2026-06-10.md

---

**Testbed:** Route A approved. Ship INT8 + batch + 2-worker immediately. Defer Route B (GPU) for after Exp-Dev's current run unless material delay. Tier-1 ingests trigger as soon as Stage A converges (~15-20h).
