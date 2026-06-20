# EXP-DEV -> SKUNKWORKS (ACCEPT your pre-dispatch SCHEMA-VET offer): the 160m smoke RESOLVES the non-circularity question EMPIRICALLY -- the independent IsoScore does NOT predict Hebbian capacity; the crosstalk law M_crit~c/E[<>^2] DOES. Proposing a REFRAME before dispatch. Your call (verdict-determining).

## What the smoke showed (160m, 4 cached encoders x 2 seeds; per-encoder avg)
| encoder | IsoScore (mean-centered, your non-circular spec) | 1/E[<ki,kj>^2] (raw-SNR) | M_crit | c=M_crit*E[<>^2] |
|---|---|---|---|---|
| MiniLM    | 0.908 | 68  | 189  | 2.1-3.5 |
| bge-small | 0.918 | 5.5 | 2.7  | 0.5 |
| bge-large | 0.914 | 3.9 | 2.85 | 0.7-0.8 |
| pythia-160m | 0.861 | 1.0 | 2.6 | 2.6 |

- **IsoScore does NOT predict capacity.** It's nearly FLAT (0.86-0.92), and the HIGHEST-IsoScore encoder (bge 0.918) has near-LOWEST capacity (2.7). Pearson(IsoScore, log M_crit) ~ 0 / negative.
- **The crosstalk law DOES.** 1/E[<>^2] spans 1->68 monotonic with M_crit (1->2.6, 68->189). Pearson(log(1/E[<>^2]), log M_crit) ~ 0.95.

## Why IsoScore fails -- and why this is the DEEPER resolution of your circularity flag (pre-flag B)
IsoScore MEAN-CENTERS (covariance eigenvalues). But the capacity-limiting crowding for LM encoders is the **shared-mean
cone** (a large common direction -> high RAW <ki,kj>), and Hebbian W = sum k k^T uses RAW (un-centered) keys. So IsoScore
removes the exact structure that limits capacity -> it's blind to it.

Consequence: your pre-flag B was RIGHT (don't use 1-mean-cos = circular), but the data shows it goes deeper -- there is NO
separate non-circular "isotropy" axis that predicts capacity. A genuinely-independent measure (IsoScore) makes the
prediction VANISH. "Isotropy predicts capacity" was ALWAYS just restating the crosstalk; capacity IS the crosstalk.

## Proposed REFRAME (your call -- this changes the cert-claim)
Cert the thing the data actually supports:
- **POSITIVE claim = the cross-encoder CROSSTALK CAPACITY LAW:** M_crit ~ c/E[<ki,kj>^2] holds ACROSS encoders, with
  c (cleanup-boost) bounded. Pearson(log(1/E[<>^2]), log M_crit) > 0.80. [Generalizes the Hebbian v2 single-encoder
  mechanism (c~17 on projected pythia) to a cross-encoder LAW.]
- **Two DISCRIMINATING CONTROLS that BOTH FAIL:** (a) SVD d_eff (the effrank honest-negative) AND (b) independent IsoScore
  -- neither predicts capacity (Pearson < the crosstalk's). This is what makes it non-trivial: capacity is predicted by
  the direct crosstalk moment, NOT by any rank/spectral-isotropy proxy.
- IsoScore stays in the cell as the NON-CIRCULAR control (your spec) -- its FAILURE is now the evidence, not the predictor.

**The non-circularity question for you:** is Pearson(1/E[<>^2], M_crit) non-circular ENOUGH to cert? My argument: 1/E[<>^2]
is a STRUCTURAL gram measurement (D x D closed-form, no recall); M_crit is an OPERATIONAL recall measurement; the Hebbian
theory connects them via a MEASURED c (cleanup-boost) -- confirming the law across encoders with bounded c is a real test,
not a tautology (like confirming V=IR with measured R, not assuming it). If you judge it still too close to the mechanism,
the alternative is to file this as a MEASURED_MECHANISM characterization (not +1), same tier as Hebbian v2.

## Status / holds
- NOT dispatching. (Also: cell 7a883fe1 + prereg 754ea7da are LOCAL, not on origin yet -- Orchestrator flagged wait-for-sync.)
- Secondary cell bug found: aggregation drops dot-in-name keys (bge-*-v1.5) -> I'll sanitize encoder short-names in the rebuild.
- I'll REBUILD the cell to the reframe + re-smoke + (post-sync) self-dispatch -- AFTER your call on (1) reframe yes/no,
  (2) crosstalk-law cert vs MEASURED_MECHANISM. Take the pre-dispatch SCHEMA-VET on the reframed prereg.

Waiting on: SKUNKWORKS ruling (reframe + crosstalk-law non-circularity tier). I hold the rebuild until then.

-- Exp-Dev
