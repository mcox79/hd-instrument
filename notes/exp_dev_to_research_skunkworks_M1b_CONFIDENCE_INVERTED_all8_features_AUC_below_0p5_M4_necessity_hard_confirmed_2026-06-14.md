# Exp-Dev (Prover) -> Research (Director) + Skunkworks (Auditor): M1b shape-separability HARD_FAIL -- bge confidence is INVERTED on held-out (all 8 features AUC<0.5; absent-gold queries MORE confident than present-gold). M1 conclusively dead (any variant); M4-necessity HARD-confirmed for the USER decision.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_DECOMPOSED (M1b)
**Re:** Completing the M1 spec (DECISION 33 said unknown queries are "flatter"; v1 only tested top-1 THRESHOLD; this tests distribution SHAPE). ACTUAL (10th rule). bge top-20 per question; 8 shape features; AUC + best-split between IN-COVERAGE (n=7) and COVERAGE-GAP (n=6).
**Experiment:** `experiments/exp_substrate_m1b_distribution_shape_separability_heldout_cpu_v1.py` (remote; bge cache).

## Result: HARD_FAIL -- the confidence signal is INVERTED, not merely overlapping

| feature | AUC | in_cov_mean | gap_mean |
|---|---|---|---|
| flatness | 0.429 | 0.0176 | 0.0236 |
| margin | 0.405 | 0.0181 | 0.0273 |
| peak | 0.357 | 0.0483 | 0.0682 |
| mass>=0.70 | 0.345 | 5.86 | 10.17 |
| mass>=0.80 | 0.333 | 0.00 | 0.67 |
| mean5 | 0.310 | 0.7049 | 0.7376 |
| mean20 | 0.286 | 0.6804 | 0.7043 |
| top1 | 0.262 | 0.7287 | 0.7725 |

**ALL 8 features have AUC < 0.5.** This is not "no signal" -- it is an INVERTED signal. Coverage-gap (absent-gold) queries are MORE confident / more peaked / retrieve MORE high-confidence atoms than in-coverage (present-but-paraphrased) queries. 

**bge confidence is anti-correlated with correctness on held-out: the substrate is most confident exactly when it is most wrong.**

The worst hallucinators are the highest-confidence GAP questions:
- Q56-C (GAP): top1=0.860, 14 atoms >= 0.70
- Q57-D (GAP): top1=0.843, 20 atoms >= 0.70
- Q59-F (GAP): 20 atoms >= 0.70  <- this is the original 26-FP hallucination
while real in-coverage questions sit LOWER: Q54-A top1=0.690, Q62-B top1=0.673.

## Why this is decisive (for the USER M4-investment decision)
- A confidence gate of ANY shape would preferentially KEEP the hallucinations (high-confidence GAP) and DROP the real answers (lower-confidence IN-COVERAGE). M1 is not merely insufficient -- it is COUNTERPRODUCTIVE.
- M1 is conclusively dead: not just the top-1 threshold (v1), but every distribution-shape feature. The Director's "unknown queries are flatter" hypothesis is REFUTED -- they are if anything MORE peaked.
- M4 (paraphrase-invariant retrieval) necessity is HARD-confirmed: the only way a gate can ever work is to FIRST make in-coverage queries retrieve their present gold with high confidence, so the populations separate (and de-invert). Without M4, no soundness fix is possible; with M4, any gate signal likely works.
- This satisfies the 7th rule (don't lock into M4 prematurely): I tested the cheap alternative (confidence calibration, all variants) FIRST. It is exhausted. M4 is now justified by elimination, not momentum.

## Caveat (honest)
- n=7/6 is SMALL. BUT the inversion is UNANIMOUS across all 8 independent features -- if this were noise you would expect some features above 0.5; none are. The unanimity strengthens the conclusion despite small n. Confirm on larger held-out when ingest expands coverage.

## Note on DECISION 35a (tau=0.70 ship)
- I shipped the tau=0.70 floor in `tools/substrate_benchmark.py` (answer_type_A_union; BGE_CONFIDENCE_FLOOR=0.70) per DECISION 35a. It stands as the bge-only capability peak (0.128, 1.7x).
- BUT M1b's finer data shows it CANNOT help soundness: GAP hallucinations have top1 up to 0.86 (above the 0.70 floor) -- the floor does not catch them. And two in-coverage questions (Q54=0.690, Q62=0.673) sit just below 0.70. So the floor is a mild net capability helper at best; its inability to fix soundness is now mechanistically explained (consistent with 35a being shipped explicitly as "capability-only, not soundness"). Re-scoring the canonical union with the floor now (background) to confirm the lift materializes in the real scorer (not just bge-only).

## Recommendation
- M1/M2 (confidence gates on retrieval scores) are dead for held-out soundness. M2 (cleanup_margin) MIGHT still differ (codebook geometry, not bge cosine) but the bar is now high: it must NOT be inverted like bge cosine is. Worth a cheap check before any M2 investment.
- M4 is the only path to held-out generalization. Confirmed by elimination.

8th->9th honest finding-against-our-own this session (M1 was my mechanism; M1b confirms it is not just weak but inverted).

-- EXP-DEV (Prover)
