# Prereg: svamp_learned_selector_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** direction A follow-up -- Research bipartite role-assigner (learned discriminative operand-pair selector).

## Motivation
v1 heuristic role-asymmetry: SVAMP first-2 0.287 -> heuristic-role 0.363. Operand selection is the bottleneck (crude heuristics
plateau; answer often pairs a NON-target number with a target number). Build a LEARNED pair-selector (perceptron scoring each
candidate pair so the gold pair outscores others), then op-direction classifier on the selected pair. Two-stage substrate-discriminative.

## Method
Selector: averaged perceptron over pair features (target-stem-match, in-question, same-noun, adjacency, magnitude, cross-target).
Op-classifier: averaged perceptron over op features on gold pairs (teacher forcing). Pipeline at test: select pair -> classify op.
Report pipeline acc + selector-pair acc (decomposition). Bundled SVAMP.

## Pre-registered verdict (NO defeat)
- HARD_PASS: pipeline >= 0.42 (drill-13 target).
- MIDDLE_BAND: >= 0.36 OR >= heuristic(0.363)+0.02.
- HARD_FAIL: < 0.36 and no better than heuristic.

Smoke (200 train, 80 test): pipeline 0.35, selector-pair acc 0.707 (selection works; op + world-knowledge cap pipeline). Full decisive.
