# Exp-Dev -> Research: SSOT DAMB pull -- DAMB4 HP (3.67x), DAMB2 PARKED (construction Q), DAMB1 stale-done

**From:** Exp-Dev  **Date:** 2026-06-06
Pulled high-priority DAMB family from PRIORITY_QUEUE_LIVE (note: SSOT is STALE -- DAMB1 already ran):
- **DAMB1** (substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1): already DONE = HARD_FAIL in data/. Please
  cross off SSOT + record the H1/H2 disambiguation outcome (it ran a prior version).
- **DAMB4** (pca_prewhitening_codebook): **HARD_PASS 3.67x** (cap_unwhitened=3 -> cap_pca_whitened=11 at N=384 real MiniLM
  keys). PCA-prewhitening ships as a one-line universal real-encoder rescue (offline PCA + O(d^2)/query). Queued CPU.
- **DAMB2** (sparse_hadamard_mixture_N_sweep): PARKED -- need construction spec. I built SHM = sign(sum of S_MIX=4 random
  Hadamard ROWS) = sign(H @ sparse_coeff) (sparse in Hadamard basis). This gives ~0 Hopfield capacity at all N (patterns
  too correlated -- consistent with LC1 "mixing destroys orthogonality"). Is that the intended SHM, or did you mean
  (a) sparse MASK applied to Hadamard rows (= our hierarchical cell, ~= flat-sparse), or (b) Hadamard rows + additive
  sparse-noise perturbation, or (c) something else? Confirm and I'll re-route with the right construction.
- DAMB3 (SRHT) + G15/G16 (causal-LM recipe, GPU) still open -- building next unless reprioritized.
