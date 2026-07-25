# Pre-reg: arc_aggregation_sparse_code_regime_v1

Cell: `experiments/exp_arc_aggregation_sparse_code_regime_v1.py`
Metrics: `data/exp_arc_aggregation_sparse_code_regime_v1/metrics.json`
Contract: INLINE-LOCAL foreground-to-completion; no push/remote-persist; ASCII-only; deterministic. VET-PENDING (skunkworks owns landed-VET).

## Question (LIVE, UNPROVEN, can-fail)
Does moving the fact-BUNDLE to a SPARSE code regime fix the dense-superposition-dilution seen on REAL
(noisy) retrieval in aggregation? Reference cell (`exp_arc_aggregation_retriever_bindsettle_v1`) found the
textbook signature: ORACLE bundle 0.766 > single 0.706 (helps clean); REAL bundle 0.298 < single 0.342
(hurts noisy). Hypothesis: DENSE-code crosstalk; sparse distributed codes (near-disjoint supports) compose
many items with low interference -> sparse bundle should beat single on REAL too.

## ONE variable
Code regime of the fact bundle: dense float vs SPARSE top-k bipolar (same operator as
`ppmi_sparse_encoder.encode_sparse`, applied to the SHARED SemanticHDEncoder so semantics are held fixed).
Retrieval (which facts), relevance weights, encoder, choices-space all identical between arms.

## Arms
Per pool {ORACLE gold-central, REAL held-out top-K}: {dense,sparse} x {single,bundle}. Plus
sparse_bundle_shuffle (must-fail). k* chosen by base-signal preservation on SPARSE_SINGLE (independent of
the bundle discriminator; calibration_check = adaptive_with_discriminator_gate).

## Bands (PRIMARY = REAL pool, Easy split; pre-registered BEFORE run)
- SPARSE_FIXES_CROSSTALK: sparse_bundle_real > sparse_single_real AND sparse_bundle_real >=
  dense_bundle_real + 0.03 AND base signal preserved (sparse_single_real >= dense_single_real - 0.05) AND
  shuffle collapses.
- SPARSITY_NEUTRAL (NULL, pre-registered honest): |sparse_bundle_real - dense_bundle_real| < 0.03 and still
  < single -> crosstalk NOT the limiter; loss is retrieval-noise/content, not superposition.
- INCONCLUSIVE_SPARSIFICATION_DAMAGED_CODE: sparse_single_real < dense_single_real - 0.05.
- Guards: POS_CONTROL_REPRO_FAIL (dense arms must reproduce prior 0.342/0.298 within 0.05, Gate D);
  MUSTFAIL_BREACH (shuffle); AGG_DISCRIMINATOR_SATURATED (dense_single_real >= 0.90).

## Mechanism instrumentation (direct crosstalk read)
bundle answer-margin = cos(B,correct) - max_wrong cos(B,wrong); pairwise mean |cos| among fact codes.
Dense vs sparse. Sparse fixing crosstalk => higher margin AND lower interference.

## Compute
sequential-CPU numpy (light closed-form scoring, no training fit); wall < 10min. storage = sharded.

## RESULT (MEASURED@ metrics.json, full: 1177 Easy / 487 Challenge)
Verdict = SPARSITY_NEUTRAL (the pre-registered NULL).
- real: dense_single 0.3475, dense_bundle 0.3008, sparse_single 0.3356, sparse_bundle 0.3084
  (delta_sparse_rescue +0.0076 < 0.03; sparse_bundle - sparse_single -0.0272). k*=0.5.
- oracle: dense_bundle 0.7681 > single 0.7001 (clean advantage reproduced); sparse_bundle 0.763 >
  sparse_single 0.6797 (clean advantage PRESERVED under sparse).
- crosstalk mechanism: fact-interference dense 0.7928 -> sparse 0.6639 (sparse DID reduce interference
  ~16%), but bundle answer-margin unchanged (dense -0.0149 -> sparse -0.0152) and accuracy neutral.
- gates: repro_ok True (0.3475 vs 0.342; 0.3008 vs 0.298), base_signal_preserved True, shuffle 0.2082
  collapsed True, arms_differ True.
INTERPRETATION (no spin): sparse coding engages the mechanism (measurably lower interference) but that does
NOT rescue real-retrieval aggregation -> superposition-crosstalk is NOT the limiter of the 0.298<0.342 loss;
the wall is retrieval noise/content (matches the reference cell's miss_diagnosis: retrieval_bottleneck
dominates). Consistent with prior GSBC/ARCH-B SPARSITY-NEUTRAL. Sparse is not the lever here.
