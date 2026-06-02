# Pre-registration: eviction_id_external_codebook_v1

**Date:** 2026-06-02
**Anchor:** eviction_id_external_codebook_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_eviction_id_external_codebook_v1.py

## Scientific question (Caching-Policy Expressibility, Tier 2 NEGATIVE)
The substrate cannot natively distinguish "which pattern was written most recently"
from "which pattern was written least recently." Eviction candidate ID requires an
external codebook (write-count or timestamp register). Test: known patterns can be
probed via cosine (AUROC >= 0.70 distinguishing high vs low importance); but random
probes yield AUROC ~ 0.50 (cannot determine importance without the codebook).

## Pre-registered thresholds (Tier 2 NEGATIVE -- constraint confirmation)
- HARD-PASS (constraint confirmed): known_auroc >= 0.70 AND |random_auroc - 0.50| <= 0.15
  (known xi can be recovered; random probes cannot determine importance)
- MIDDLE: known_auroc in [0.60, 0.70) AND random near-0.5
- HARD-FAIL: random_auroc >= 0.70 (random probes can determine importance = constraint violated)

## Calibration note
Two groups: M_HIGH=25 patterns written N_A=4 times (high importance), M_LOW=25 written N_B=1 time.
Expected: W encodes importance implicitly in pattern magnitude, but random cosine probes cannot
extract this without knowing the stored vectors.

## Smoke result
HARD_PASS (constraint confirmed): known_auroc=0.733, random_auroc=0.510 (smoke N=1024, 2 seeds)
