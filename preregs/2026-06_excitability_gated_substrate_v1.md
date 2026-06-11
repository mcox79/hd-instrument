# Pre-registration: excitability_gated_substrate_cpu_v1
**Date:** 2026-06-11  **Anchor:** excitability_gated_substrate_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Above the capacity cliff (K>>capacity), does a priority-proportional excitability write-gain protect a high-priority subset
while ungated equal-gain collapses? Sprint-4 architecture.
## Pre-registered bands
HARD-PASS gated high-priority recall >= 0.90 AND > ungated by >= 0.25. MIDDLE gated >= 0.80. HARD-FAIL else.
## Calibration rationale
High excitability gain makes priority items dominate the additive bundle, surviving overload; ungated splits capacity across all K.
## N-suffix section
N=8192 numpy; K=1200 >> capacity. Fast. n=1; multi-seed if HARD_PASS.
