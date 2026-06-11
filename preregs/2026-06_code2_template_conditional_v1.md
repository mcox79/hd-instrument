# Pre-registration: code2_template_conditional_cpu_v1

**Date:** 2026-06-11
**Anchor:** code2_template_conditional_cpu_v1
**Queue:** local_cpu_queue
**N:** 8192, **Ops:** 10, **Slots:** 5, **Templates:** 12, **Seeds:** 1

## Scientific question
The base code2 (global margin to nearest library program) and the literal per-op self-decode both HF, because the bug is a
CLEAN out-of-grammar op swap (a valid op phasor, wrong slot) that decodes as itself. Does a TEMPLATE-CONDITIONAL grammar
check -- identify the test program's nearest template, then flag the slot with the lowest match to that template's valid-op
set -- detect the bug? Per the code2 2x DEEP drill, reframed via my design-gap catch (Research-confirmed).

## Pre-registered bands

**HARD-PASS:** bug-detection F1 >= 0.78 (AUC reported).

**MIDDLE:** F1 >= 0.65.

**HARD-FAIL:** F1 < 0.65.

## Calibration rationale
0.78 is the drill's R-SOFT-DECODE target (lift from base ~0.5). The mechanism: store per-template per-slot valid-op bundles;
the ~4 correct slots robustly identify the true template; the out-of-grammar slot then shows a low grammar match to that
template's valid set (the bundle does not contain the bug op). tau swept in {0.05,0.10,0.15,0.20} by F1. This uses the
substrate's existing template structure (TSE-for-code), not a generic confidence margin.

## N-suffix section
N=8192 complex64; numpy CPU, seconds. n=1 exploratory; multi-seed n=5 follow-up if HARD_PASS (closes Wave-1 Tier-0 code2 gap).
