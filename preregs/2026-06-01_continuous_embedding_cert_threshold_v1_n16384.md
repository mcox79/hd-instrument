# Prereg: continuous_embedding_cert_threshold_v1_n16384

**Date:** 2026-06-01
**Anchor:** continuous_embedding_cert_threshold_v1_n16384
**Queue:** remote_cpu_queue
**Cap_map trigger:** v305 audit-grade-vector-store MIDDLE_BAND rescue R2 (Arm4 threshold sweep)

## Scientific question

Does there exist a threshold multiplier in [0.1, 0.9] where fp_rate=0 AND cert_rate >= 0.95 simultaneously in all 3 seeds? If yes: Arm 4 of the continuous-embedding-storage test closes to HARD_PASS at a calibrated operating point.

## Design

Same corpus as v2: N=16384, corpus=10000, seeds=[7,17,23].
Threshold multipliers: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9].
For each multiplier: threshold = mean(non_deleted_scores) * multiplier.
Report cert_rate and fp_rate at each multiplier per seed.
Score separation from v2: mean_nd~1.0, mean_del~0.007. Smoke confirms distribution separation is massive.

## Pre-registered bands

**PRIMARY: exists_clean_threshold**
- HARD-PASS: at least one multiplier achieves fp_rate=0 AND cert_rate >= 0.95 in ALL 3 seeds.
- HARD-FAIL: no multiplier achieves condition in any seed.
- MIDDLE: condition met in 1-2 of 3 seeds.

**SECONDARY: best_cert_rate at fp_rate=0**
- HARD-PASS: mean best_cert_rate at fp_rate=0 >= 0.95
- MIDDLE: 0.80-0.95
- HARD-FAIL: < 0.80

**Joint OVERALL**
- HARD-PASS: both arms HARD-PASS
- HARD-FAIL: either arm HARD-FAIL
- MIDDLE: otherwise

## Smoke result

Smoke (N=512, corpus=128, seed=17): HARD_PASS. Mean_nd=0.998, mean_del=0.007. Score separation=0.990. At mult=0.2 already cert_rate=1.0 fp_rate=0.0. Multiplier 0.8 is the highest clean threshold in smoke. Effect size is large: deleted scores are ~135x smaller than non-deleted scores. Strong prior that FULL will also HARD_PASS.

Smoke wall_s=0.05s (tiny at N=512). FULL scale: W build dominates at N=16384 (same as v2, ~10-15s/seed CPU). 3 seeds x 15s = 45s. Safety: ceil(1.5 * 45) = 68s -> 300s (round up generously). PROT-019 floor: 14400s.

## Timeout estimate

```
smoke_wall_s = 0.05 (N=512 smoke; dominated by W build at FULL scale)
Estimate from v2 wall_s=41s on GPU. CPU ~10-15x slower: 410-615s for 3 seeds.
ceil(1.5 * 615) = 923s -> 1200s.
PROT-019 floor: 14400s. timeout_s = 14400.
```

## PROT-018 N-suffix

`_n16384`: N_FULL = 16384. Confirmed via grep.

## Dependencies

None. Script is self-contained; same corpus generator as v2 (deterministic seed).
