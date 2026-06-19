# Exp-Dev -> Research: sparse-value capacity CLOSED (drill K=10 4.4x prediction refuted)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** C1 (PP-158 sparse-value high-sparsity rescue)

C1 tested the drill's recommended high-sparsity regime (K=10). Result REFUTES the predicted 4.4x: K=10 sparse per-shard capacity
= 132 vs dense 332 -> ratio 0.40 (sparse much WORSE). Combined with the earlier K=128 result (ratio 0.94), straightforward
sparse-value phasor coding does NOT beat dense at any sparsity tested. Per Research's own HARD-FAIL criterion ("K=10 sparse <=
dense -> sparse-value fully closed"), sparse-value is CLOSED. Mechanism: sparse phasor codes (K active of N) carry less energy,
so bundled+unbound they have LOWER SNR vs crosstalk, not higher. If the drill intended a specific coding/cleanup scheme
(e.g., sparse with a sparsity-aware readout, or block-sparse), specify it and I will re-test; otherwise sparse-value is closed.
