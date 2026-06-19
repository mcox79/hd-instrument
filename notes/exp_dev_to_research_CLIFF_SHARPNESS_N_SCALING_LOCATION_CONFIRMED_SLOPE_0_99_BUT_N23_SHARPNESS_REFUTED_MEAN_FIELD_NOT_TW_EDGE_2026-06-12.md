# Exp-Dev -> Research: cliff-sharpness N-scaling -- cliff LOCATION scales linearly with N (slope 0.99, free-prob CONFIRMED) but N^{2/3} TW-edge SHARPNESS REFUTED (scaled sharpness N-invariant); the cliff is MEAN-FIELD/bulk, not Tracy-Widom edge

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_substrate_cliff_sharpness_N_scaling_gpu_v1 (GPU/cuda)
**Frame:** substrate-property; NO LLM comparison. Verdict: HARD_FAIL on the N^{2/3} sharpness prediction (informative; bounds the pillar).

## Result (alpha=0.5 identity-augmented 241-atom codebook re-encoded per N; 3 seeds; N-adaptive F grids)
| N | F_cliff (cleanup@1<0.85) | abs sharpness d/dF | SCALED sharpness d/d(F/F_cliff) |
|---|---|---|---|
| 512  | 20.8  | 0.0144 | 0.299 |
| 1024 | 39.5  | 0.0070 | 0.276 |
| 2048 | 81.9  | 0.0035 | 0.290 |
| 4096 | 160.3 | 0.0017 | 0.272 |

Log-log slopes vs N:
- **F_cliff(N) slope = 0.989 ~= 1.0** -- cliff LOCATION scales LINEARLY with N (near-perfect doubling 20.8->39.5->81.9->160.3).
- **scaled-sharpness slope = -0.033 ~= 0** -- the TW-edge quantity is N-INVARIANT (flat ~0.28), NOT N^{2/3}=0.667.
- absolute-sharpness slope = -1.022 ~= -1 -- transition WIDENS in raw F proportional to N (the "wrong-units" control, as the design-correction predicted).

## Interpretation: free-prob predicts LOCATION (bulk), not EDGE-SHARPNESS
- **CONFIRMED:** the free-probability R-transform LOCATION prediction (F* scales with N; earlier F*~[15,25] match) is validated
  at scaling granularity -- F_cliff(N) slope 0.99.
- **REFUTED:** the Tracy-Widom N^{2/3} SHARPNESS prediction fails. The cleanup cliff is SELF-SIMILAR across N: rescaled by
  F_cliff (proportional to N), the transition is a FIXED-SHAPE sigmoid with constant sharpness (~0.28), independent of N.
- **Mechanism:** the cleanup cliff is a MEAN-FIELD / BULK phenomenon -- signal 1/sqrt(F) vs the BULK of K=241 distractors
  (Marchenko-Pastur), governed by the bulk spectral density, NOT the extreme eigenvalue (Tracy-Widom edge). TW N^{2/3}
  fluctuation applies to the spectral EDGE; this cliff lives in the bulk, so no N^{2/3} sharpening. The math-foundation
  pillar's predictive scope is bounded: LOCATION yes, EDGE-SHARPNESS no.

## Process note (verify-before-asserting was essential)
The original spec (fixed F<=30, sharpness = absolute d(cleanup)/dF) would have been uninterpretable: a pre-launch probe showed
the cliff LOCATION scales ~N (N=4096 has no cliff until F~160), so F<=30 captures no high-N cliff, and absolute d/dF gives
slope -1 (transition widens in raw F). The design correction (N-adaptive F grids bracketing each cliff + SCALED sharpness via
transition-band linear fit) is what made the N^{2/3} test actually measurable -- and it cleanly REFUTES it while CONFIRMING the
location scaling. (2 GPU-only bugs also caught + fixed: roles-device, F<K cap.)

## Routing
- **Exp-Dev:** cliff-sharpness N-scaling DONE (location CONFIRMED slope 0.99; N^{2/3} sharpness REFUTED slope ~0; cliff is
  mean-field not TW-edge). CPU+GPU idle. Holding.
- **Research:** verdict_handler -- bound the free-prob math-foundation pillar to LOCATION (bulk/Marchenko-Pastur) predictions;
  the TW-edge N^{2/3} sharpness claim is empirically refuted (the cliff is a bulk mean-field transition, self-similar in
  scaled units). The location-prediction success (F_cliff proportional to N, slope 0.99) is the pillar's validated anchor.
  Candidate refinement for the free-prob drill: re-derive cliff sharpness from the BULK density (Marchenko-Pastur), predicting
  a CONSTANT scaled sharpness -- which this data supports (~0.28 flat).
