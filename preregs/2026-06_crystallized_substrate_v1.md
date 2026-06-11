# Pre-registration: crystallized_substrate_cpu_v1
**Date:** 2026-06-11  **Anchor:** crystallized_substrate_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does a separate CRYSTALLIZED (frozen) substrate for foundational Tier-1 atoms protect them from heavy mutable-store churn,
vs a shared store? Sprint-4 engineered-wrapper architecture.
## Pre-registered bands
HARD-PASS crystallized Tier-1 recall >= 0.95 AND > shared by >= 0.20. MIDDLE crystallized >= 0.85. HARD-FAIL else.
## Calibration rationale
A frozen separate store has no interference; a shared store mixing 2000 mutable writes degrades Tier-1 recall. Mirrors write-lock/per-role wins.
## N-suffix section
N=8192 numpy; fast. n=1 exploratory; multi-seed if HARD_PASS.
