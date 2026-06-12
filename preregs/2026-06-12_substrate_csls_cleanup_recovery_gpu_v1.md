# Pre-registration: CSLS cleanup recovery (does hubness-correction recover the clustered-codebook decode deficit?)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_substrate_csls_cleanup_recovery_gpu_v1.py
**Routing:** indicated mitigation from Cell A+B verdict (Research revised-lock note named CSLS/MMR re-rank). Substrate-quality-first; NO LLM frame.
**Lane:** overnight_queue (GPU).

## Hypothesis
Cell A found the substrate decode ceiling is capped at ~0.89 (F=3) vs uniform-codebook 1.0 (-0.11 deficit) by the clustered
codebook (tw_edge_z=-2.26). If that deficit is HUBNESS (dense-region atoms winning the argmax), CSLS (Lample 2018) cleanup
re-rank -- score(est,c) = 2*cos(est,c) - r_k(c), r_k = mean cos to k nearest codebook neighbors -- recovers it. If it is
genuine semantic near-duplicates, CSLS cannot.

## Design
Same composition setup as Cell A (bundle(bind(R_i,B_i)) over 280-atom algebra_hrr corpus, unitary roles). Compare STANDARD
cleanup (argmax cosine) vs CSLS cleanup, cleanup@1 across F in {1,2,3,5,10,20}, 3 seeds x 20 trials, CSLS k=10.

## Pre-registered verdict bands
- **HARD-PASS:** CSLS cleanup@1 >= 0.95 at F=3 OR CSLS lift >= +0.05 over standard at F=3 (substantial hubness recovery).
- **MIDDLE:** CSLS lift +0.01-0.05 at F=3 (partial recovery).
- **HARD-FAIL:** CSLS lift < +0.01 (deficit is genuine near-duplicates, not hubness; cleanup re-rank cannot fix it -- mitigation would need atom de-duplication / finer encoding).
- **UNKNOWN:** corpus load fails.

## Substrate-product artifact (stands alone, no LLM frame)
Diagnoses WHY the substrate's clustered codebook caps decode (hubness vs genuine near-duplicates) and whether the standard
hubness mitigation recovers it -- directly informs the Stratified-Hybrid cleanup layer design.
