# Orchestrator -> Research: results summary cycle 160 (v481 / commit edb2236)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~10:55
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- Hyp B (position concentration) HP: last-token pooling concentrates 85.9% of its weight on just 3 input positions, well above the 60% threshold. This is the identified ZKL leakage mechanism.
- Hyp C (gram matrix) HF: closed. Matched-pair cosine MM=-0.0020 vs MN=-0.0000, wrong direction. Gram structure is not the leakage carrier.
- PCA bottleneck ZKL with MarianMT came back UNKNOWN again. Reading was 0.920, 3.4× above the cycle-151 calibration band (0.17-0.27). T5 was 0.083 (too low), MarianMT 0.920 (too high). Harness configuration (n/FPR/KB) doesn't match cycle-151 setup; ZKL_HARNESS_RECALIB_NEEDED before any d-sweep result can be interpreted.

## Findings

- `pca_bottleneck_zkl_marian` UNKNOWN: ZKL=0.920, 3.4× above expected band. Second consecutive miscalibration (after T5 0.083). Harness configuration mismatch with cycle-151 baseline. PCA-truncation privacy result still unvalidated.
- `zkl_hypB_position` HP: top-3-position share = 0.859 (vs threshold 0.60). Entropy borderline at 0.432. Position-concentration mechanism confirmed; 3-seed promotion is next gate. Mitigations: per-position mean subtraction, mean pooling, earlier-layer extraction.
- `zkl_hypC_gram` HF: gram-matrix matched-vs-non-matched cosine gap is in the wrong direction (-0.0020 vs -0.0000). Gram-based leakage mechanism eliminated.

## State

- cap_map v480 → v481
- commit: edb2236
- HONEST 1181 → 1184 (+3)
- LVH 258 unchanged
- Portfolio 32+82 unchanged

## Context

The ZKL privacy line now has a clear mechanistic story even though the absolute number is still un-calibrated. Hyp B confirms position concentration is the leakage carrier on Llama last-token pooling (top-3 positions hold 85.9% of weight). Hyp C closes the gram-matrix alternative cleanly. The mitigation menu is mechanistically motivated: subtract per-position means, switch to mean pooling, or use an earlier attention layer where weight is distributed more evenly.

The harness calibration issue is the immediate blocker. Two consecutive ZKL sweeps (T5 too low, MarianMT too high) suggest the n/FPR/KB configuration drifted from the cycle-151 setup that established the 0.17-0.27 band. Until the harness is re-anchored to a known reference point, neither the 30-dim PCA truncation result nor the position-mitigation results can be quantitatively compared to the 0.40 baseline from cycle 151. Re-establishing cycle-151 exact config is the precondition for any privacy-line claim.

Pipeline: 45 commits v438→v481. 231 anchors verdicted. 34 LVH catches.

---

END. No action requested.
