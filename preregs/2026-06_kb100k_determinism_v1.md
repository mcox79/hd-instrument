# Pre-registration: kb100k_determinism_gpu_v1
**Date:** 2026-06-11  **Anchor:** kb100k_determinism_gpu_v1  **Queue:** overnight_queue (GPU)  **Seeds:** 3  **Device:** CUDA
## Scientific question
Is PP-225 production-scale (kb100k) fact-recall seed-deterministic at n=3? Bulletproofs the Tier-A claim at the largest validated scale.
## Pre-registered bands
HARD-PASS mean held-out >= 0.90 AND std <= 0.03. MIDDLE mean>=0.90 std>0.03. HARD-FAIL mean<0.90.
## Calibration rationale
kb100k landed 0.997 at n=1 in the asymptote; deterministic head training -> std near zero expected. Confirms production-scale Tier-A is seed-stable.
## N-suffix section
Subprocesses validated kb100k cell (frozen Pythia-1.4b + bge-large, N_FACTS=100000). ~15-30 min/seed on CUDA. Per-seed checkpoint. Fits 8GB.
