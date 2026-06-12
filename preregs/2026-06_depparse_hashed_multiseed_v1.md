# Prereg: depparse_hashed_multiseed_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Direction 1 (multi-seed firming).
Multi-seed n=5 the feature-hashed discriminative dep-parser (single-seed UAS 0.7868/0.7872). Arc-feature precompute is
seed-independent (computed once, reused). Same hashing + features + 10-epoch averaged perceptron + greedy-cycle-break decode.
Report mean UAS +/- SE. HARD-PASS mean-2SE>=0.80 (Tier-A). MIDDLE mean 0.75-0.80 (firmed MIDDLE). HARD-FAIL <0.75.
