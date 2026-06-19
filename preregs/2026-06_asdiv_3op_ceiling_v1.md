# Prereg: asdiv_3op_ceiling_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** Research direction B (T-3OP-CEILING) + direction C (ASDiv simple/complex diagnostic).

## Motivation
Instrument-only oracle (no LLM, no trained solver): max accuracy the substrate compositional engine could reach with a perfect
operator/operand selector. For each ASDiv item, extract numbers from problem text (digits + written-out words) and test whether a
depth-<=k binary-op tree (+,-,*,/) over them reaches the gold answer. Report ceiling split by formula op-count (1/2/3 = simple->complex).

## Pre-registered verdict (NO defeat)
- 3-op ceiling >= 0.85 -> HARD_PASS (architecture reach fine; bottleneck is selector; build T-3OP-RECURSE).
- 0.65-0.85 -> MIDDLE_BAND.
- < 0.65 -> HARD_FAIL (most 3-op items need implicit world-knowledge constants; comprehension boundary not composition gap).

NOTE: oracle is a LOWER bound (number extraction may miss some constants). Smoke (30/op): 1-op 0.967, 2-op 0.862, 3-op 0.828 --
honest gradient (reach strong even at 3-op; modest decline = world-knowledge constants). Full run (80 3-op items) decisive.
