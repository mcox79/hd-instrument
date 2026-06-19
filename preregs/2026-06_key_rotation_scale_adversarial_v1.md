# Pre-registration: key_rotation_scale_adversarial_cpu_v1
**Date:** 2026-06-11  **Anchor:** key_rotation_scale_adversarial_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does substrate key-rotation/revocation scale to 10K keys (sharded) and hold under adversarial old-key + random-key probing?
## Pre-registered bands
HARD-PASS new-key recall >= 0.90 AND adversarial old-key <= 0.10 AND random-key <= 0.05. MIDDLE new-key >= 0.85. HARD-FAIL else.
## Calibration rationale
Rotation R rebinds all keys; legit rotated keys recall, old/random keys recover nothing (revocation). Scales the K=120 cert to 10K sharded.
## N-suffix section
N=8192; 10000 facts / ~84 shards; sampled probing. Fast.
