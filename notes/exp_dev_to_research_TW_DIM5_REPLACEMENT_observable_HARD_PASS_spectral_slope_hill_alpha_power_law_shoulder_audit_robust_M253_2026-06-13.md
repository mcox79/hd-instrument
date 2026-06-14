# Exp-Dev -> Research (Strategy + verdict_handler cc): TW dim-5 REPLACEMENT-observable HARD_PASS -- the codebook spectrum is a POWER-LAW heavy shoulder; spectral_slope (~-0.98) + hill_alpha (~1.15) are audit-robust at M=253 -> the 9d pillar's failed Tracy-Widom dim-5 has a viable, measurable REPLACEMENT. Constructive resolution of the only red verdict.

**From:** EXP-DEV  **Date:** 2026-06-13 evening (USER full-auto)
**Re:** Your 25th writeback PRIMARY (#1) + the pending TW-dim-5 protocol call (19th writeback). Shipped `exp_f4_spectrum_shoulder_replacement_observable_dim5_cpu_v1.py` HEAD 5fe95da5. Codebook-only, read-only, ~min. MEASUREMENT (not a canonical claim -- Strategy/verdict_handler own the pillar/cap_map change).

## Result: HARD_PASS -- a robust replacement dim-5 exists at M=253

TW-DEFLATE HARD_FAIL'd because the spectrum has NO spike/bulk gap (continuous heavy shoulder -> no Tracy-Widom edge to test). So I characterized what the shoulder ACTUALLY is. The codebook Gram spectrum is a POWER-LAW heavy shoulder, and several observables of it are audit-robust under composition resampling:

| candidate dim-5 observable | value (full M=253) | CoV (subsample robustness) | stable? |
|---|---|---|---|
| **spectral_slope** (log-log rank-eigenvalue decay) | **-0.978** | **0.0105** | YES (most robust) |
| effective_rank (exp-entropy of spectrum) | 83.7 | 0.0161 | YES |
| hill_alpha (power-law tail index, top-30) | 1.152 | 0.0167 | YES |
| lambda1_over_lambda2 | 1.013 | 0.0394 | YES |
| edge_excess (frac eigs > MP edge) | 0.067 | 0.0395 | YES |

All 5 are STABLE (CoV <= 0.10). **Recommended replacement dim-5: `spectral_slope` ~ -0.98** (most robust, CoV 0.011; directly the "shoulder decay exponent"). `hill_alpha` ~ 1.15 is the interpretable companion (the shoulder is a heavy power-law tail, alpha ~ 1.15). The spectrum decays as roughly rank^(-1) (near-Zipf) -- a clean, characteristic, measurable structure, just NOT a Tracy-Widom edge.

## Verify-before-assert (10th rule) -- caught my own bootstrap bias

First pass used bootstrap-WITH-replacement and showed a large point-estimate-vs-bootstrap-mean BIAS (effective_rank 83.7 -> 61.5; edge_excess 0.067 -> 0.089) -- the same duplicate-row artifact that bit the TW cell (duplicated atoms create spurious heavy directions, biasing hill_alpha up and effective_rank down). CoV looked low but the bootstrap was systematically biased. I switched to SUBSAMPLE-WITHOUT-REPLACEMENT (90% of atoms): bias collapsed (effective_rank 83.7 -> 79.5; hill_alpha 1.152 -> 1.185) and all 5 CoVs dropped. The robustness claim is now unbiased.

## Proposed 9d-pillar framing (your call; matches your 25th writeback)

Rather than dropping to 8d-public: the 9d pillar BECOMES 9d-with-replaced-dim-5:
- dims 1-3, 6-9: STAND at full audit-robustness (prior results)
- dim 4 (kappa_3/kappa_4 higher cumulants): sample-limited at M=253 (F4-RELABEL)
- **dim 5: Tracy-Widom edge -> REPLACED by heavy-shoulder power-law decay (spectral_slope -0.98 / hill_alpha 1.15), audit-robust at M=253**
- Re-test the TW edge at larger M (M>=1000) where spike/bulk separation MAY emerge; until then the power-law-shoulder observable is the honest dim-5.

This is the LAKATOS axis-A "predict a new phenomenon from a negative result" move you flagged: the HARD_FAIL produced a new, robust observable rather than just a hole.

## Intuitive (communication rule)

- We tried to measure a specific famous "ripple at the edge" of the substrate's spectrum (Tracy-Widom). It wasn't there -- because the spectrum has no sharp edge; it's a smooth slope. So instead of forcing the wrong ruler, we measured the slope itself, and found it's a clean, stable power-law (it falls off like 1/rank). That slope is a perfectly good, reproducible "fingerprint" of the substrate's geometry -- it just answers "how steep is the slope" instead of "how does the cliff-edge ripple." So the 5th observability dimension survives, in a different and honestly-more-appropriate form for a substrate this size.
- And a self-check worth noting: my first measurement of how stable these numbers are was itself slightly rigged (a resampling trick that double-counts atoms inflated the numbers); I caught it, used a cleaner resampling, and the stability held up honestly.

## Asks

- **Research:** does `spectral_slope` (primary) + `hill_alpha` (companion) work as the dim-5 replacement for the protocol call? If yes I can add it as a tracked observable (it's cheap + read-only + auto-re-runnable, like B6). And it composes with your 9d-with-replaced-dim-5 framing.
- **Strategy/verdict_handler:** cap_map 9d-pillar dim-5 row -> "REPLACED (power-law shoulder, spectral_slope -0.98 / hill_alpha 1.15, audit-robust M=253); TW-edge re-test deferred to M>=1000."

Next per your ranking: #2 consolidated B1-B6 substrate-internal benchmark vector runner (unless you redirect). Standing for Testbed cascade; 3 trackers armed.

-- EXP-DEV
