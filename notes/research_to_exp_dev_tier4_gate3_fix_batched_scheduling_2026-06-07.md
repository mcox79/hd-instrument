# Research -> Exp-Dev: Tier 4 Gate 3 (defrag consistency) fix — batched/priority-queue scheduling

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Cycle 165 tier4_defrag_consistency MID (delta=0 lossless; lat_cv=0.359 blocks HP).

## Authorize Gate 3 fix

Per cycle 165 result: defrag is LOSSLESS (delta=0; LoRA stability + substrate state preserved
across defrag pass). The blocker is latency variance (lat_cv=0.359; HP needs lower).

Fix per cycle 165 orchestrator recommendation: batched or priority-queue scheduling for
defrag pass so it doesn't contend with query traffic.

## Method

- Implement priority queue for substrate ops: queries get higher priority than defrag pass
- Defrag yields to incoming queries; resumes when idle
- Measure: lat_cv on queries during defrag; lat_cv on defrag throughput

HARD-PASS: lat_cv < 0.10 on queries during defrag; defrag completes in reasonable time
(e.g., < 2x non-contended).

BORDER: lat_cv 0.10-0.20.

HARD-FAIL: lat_cv > 0.20 (priority queue doesn't sufficiently isolate; need stronger
isolation like separate process / shard).

Wall: ~1-2 days engineering.

## Why this matters

Tier 4 program needs all 3 gates to PASS before authorizing the 5-8 engineer-week build.
Gates 1 (vocab injection) and 2 (orthogonal stability) are HP with strong margins. Gate
3 fix is the last gate. After it clears, Tier 4 build is empirically justified.

## Cross-references

- Cycle 165: notes/orchestrator_to_research_results_summary_2026-06-07_cycle165.md
- Tier 4 consolidated routing: notes/research_to_exp_dev_tier4_consolidated_routing_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize Gate 3 fix. ~1-2 day engineering. File verdict on completion. If
HP, Tier 4 build is empirically justified (5-8 engineer-week program).
