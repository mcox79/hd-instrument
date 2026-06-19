# Prereg: svamp_math_wk_lex_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** Research BOUNDARIES-REJECTED, SVAMP Path 1 (math-world-knowledge LEX constants; brain-can-do-it; rule 8).

## Motivation
v2 learned-selector plateaued 0.367 with ~26% items not text-solvable. Add Research's hand-authored math-WK LEX constants (dozen=12,
legs_per_dog=4, days_per_week=7, ...): when a constant trigger word is ADJACENT to a number ("3 dozen", "2 dogs"), add its value to
the number pool so the selector+op-classifier can compose. Substrate-self-referential (concept partition), no external knowledge.

## Method
A/B: base number pool vs WK-augmented pool, through the learned-selector + op-classifier pipeline. Bundled SVAMP.

## Pre-registered verdict (Research gate)
- HARD_PASS: +WK >= 0.42.
- MIDDLE_BAND: 0.39-0.42.
- HARD_FAIL: < 0.39.

NOTE: smoke (80) shows ~0 lift -- SVAMP gap is mostly SELECTION (multi-number), not WK constants (rarer in SVAMP than ASDiv).
Full run is the honest Path-1-on-SVAMP answer; the WK lever is expected to help ASDiv more (separate cell).
