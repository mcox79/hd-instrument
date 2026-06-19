# Prereg: svamp_role_asymmetry_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** Research direction A (pivot from ASDiv 3-op; SVAMP asymmetric-op-order where discriminative weighting lifts 2.4x).

## Motivation
SVAMP failure = operand SELECTION (which 2 of N numbers; e.g. "290 bananas/2 groups->145" needs target-aligned selection not
first-2) + op DIRECTION (X-Y vs Y-X). Role-asymmetry = bind each number to its entity-noun + role (subject/object) + question-target
alignment + transfer-verb direction. Substrate-discriminative, no LLM.

## Method
A/B, averaged perceptron over directional op-class (ADD/SUB_ab/SUB_ba/MUL/DIV_ab/DIV_ba):
- BASELINE: first-2-number operand + non-role features.
- +ROLE: target-aligned operand selection + role-asymmetry directional features.
Bundled SVAMP (svamp.json, 700 train / 300 test).

## Pre-registered verdict (NO defeat)
- HARD_PASS: +role >= 0.42 (drill-13 target).
- MIDDLE_BAND: +role 0.33-0.42 OR lift >= 0.05.
- HARD_FAIL: +role < 0.30 AND lift < 0.03.

Smoke (200 train): baseline 0.175 -> +role 0.300 (lift +0.125); full run (700 train) decisive.
