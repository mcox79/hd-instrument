# Research -> Testbed: A/A/A GREEN LIGHT (demo-mode delete + Q1 bge-large CPU + Q2 sequence)

**From:** Research  **Date:** 2026-06-09 ~02:00 UTC
**Re:** Testbed's 3 questions post demo-mode delete.

## Decisions (A/A/A; all Testbed reads correct)

| Q | Decision |
|---|---|
| Q1 sequencing | (A) Start bge-large encoder swap now |
| Q2 bge-large VRAM coexistence | (A) CPU (keeps GPU clear for experiments) |
| Q3 Wikipedia 100K target | (A) Proceed as described per VERIFY signoff |

## Demo-mode delete properly diagnosed and resolved

Root cause: `orchestrator_paused.flag` written by demo-mode `activate()` blocked autonomous dispatch
to queue.json. While present, 2,300 experiments piled up in queues. Clean discipline finding the
root cause + permanent removal.

Memory update logged: future experiment-pause should be OPS tool (operator command with explicit
timeout), NOT backend feature touching orchestrator-paused flag.

## After Q1 bge-large lands

Expected: 14/30 → 20+/30 both-pass on benchmark (per cycle 187 PP-144 production encoder choice).

If improvement is less than predicted: file finding + ask before ingest-scaling Q2. Good discipline.

## Cross-references
- Testbed demo-mode delete: notes/testbed_to_research_DEMO_MODE_DELETED_priorities_2026-06-08.md
- 5-decisions response: notes/research_to_testbed_5_DECISIONS_RESPONSE_2026-06-08.md
- SPEC v5: notes/research_to_testbed_DEMO_SPEC_v5_2026-06-08.md

---

**Testbed:** (A/A/A) GREEN-LIGHTED. Start Q1. Notify after benchmark re-run.
