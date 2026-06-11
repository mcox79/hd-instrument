# Pre-registration: kb_determinism_scales_gpu_v1
**Date:** 2026-06-11  **Anchor:** kb_determinism_scales_gpu_v1  **Queue:** overnight_queue (GPU)  **Scales:** kb25k,kb50k  **Seeds:** 3
## Scientific question
Is PP-225 fact-recall seed-deterministic across kb25k and kb50k (extends the kb10k determinism check)? Runs each scale at 3 seeds.
## Pre-registered bands
HARD-PASS BOTH scales mean held-out >= 0.90 AND std <= 0.03. MIDDLE one scale. HARD-FAIL neither.
## Calibration rationale
kb25k/kb50k landed 0.996/0.994 at n=1 in the asymptote; deterministic head training -> std near zero expected. Confirms Tier-A across range.
## N-suffix section
Subprocesses validated kb25k/kb50k cells (frozen Pythia-1.4b + bge-large). ~10-15 min/run on CUDA. Per (scale,seed) checkpoint. Fits 8GB.
