# Prereg: asdiv_math_wk_oracle_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** Research BOUNDARIES-REJECTED, ASDiv Path 1 (math-WK LEX constants) + Path 2 (tighter oracle).

## Motivation
Base ASDiv 3-op reachability ceiling 0.68 was world-knowledge-bound. Does substrate-self-referential world-knowledge (Research's
LEX_constant atoms, rule 8) close it? Tighter oracle: WK constants fire only adjacent to a number (unit/multiplier), magnitude
bound on intermediates, exact match, +1 op budget for the unit-multiply.

## Method
Per op-count: base reachability (text numbers) vs +WK reachability (text + adjacency-triggered LEX constants). Report lift.

## Pre-registered verdict (Research gate, on 3-op ceiling)
- HARD_PASS: +WK 3-op ceiling >= 0.85 (world-knowledge closes the gap; NOT outside-substrate).
- MIDDLE_BAND: >= 0.75 OR lift >= 0.05.
- HARD_FAIL: lift < 0.03.

Smoke (30/op): 3-op base 0.828 -> +WK 0.931 (+0.103); 2-op +0.034. Full run (80 3-op items) decisive.
