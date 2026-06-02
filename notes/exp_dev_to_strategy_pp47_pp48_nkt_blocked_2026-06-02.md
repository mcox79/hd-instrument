# exp_dev -> strategy: pp47_pp48_nkt_composition_v1 BLOCKED

ANCHOR: pp47_pp48_nkt_composition_v1
DATE: 2026-06-02
STATUS: INSTRUMENTATION_SUSPECT / HARD_FAIL -- DO NOT SHIP

## Observation

Signed-AM (PP-48) active repulsion fails categorically across all tested parameter ranges.
The substrate's multi-step Hopfield dynamics do NOT repel from negatively-stored patterns.

Smoke result: anti_cos = -1.0 (mean over 2 seeds)
- anti_cos = cosine_sim(retrieved, -Xi_neg[k])
- +1.0 = repulsion (retrieved = -eta, pattern avoided)
- -1.0 = attraction (retrieved = +eta, pattern is an attractor)

## Parameters tested in prior session

1. K_POS=204, K_NEG=64, N=1024: attracted (anti_cos=-1.0)
2. K_POS=50, K_NEG=64, N=1024: attracted
3. K_POS=10, K_NEG=8, N=4096, N_ACTIVE=N: attracted
4. Random Xi_pos: attracted
5. Place-field Xi_pos: attracted

## Analytical observation

One-step field h = W_signed @ eta = (W_A - W_B) @ eta.
For the canonical case eta = Xi_neg[k]: h aligns WITH -eta (field_align_with_-eta = 1.0047).
This suggests the first step IS repulsion direction.
But multi-step Hopfield dynamics reverts to +eta (global energy minimum) by convergence.

## Root cause hypothesis

W_signed = W_A - W_B.
W_A attracts toward Xi_pos attractors.
W_B is a "subtracted" Hopfield matrix -- its energy minima are the Xi_neg patterns.
But subtracting W_B does NOT create energy maxima at Xi_neg.
Instead it ELIMINATES Xi_neg as attractors, but the Xi_pos attractors still dominate the
energy landscape. The xi_neg patterns get attracted into the nearest xi_pos basin.

The mechanism "forbidden patterns become energy maxima" is not correct for the
multi-step Hopfield dynamics under W_signed = W_A - W_B.

## What is needed for rescue

Strategy must evaluate whether:
1. A different repulsion mechanism exists (anti-Hebbian? contrastive Hebbian? RBM-style?)
2. The PP-48 NKT composition requirement can be relaxed (e.g., use deletion cert as proxy
   for "forbidden" rather than active repulsion)
3. The composition PP-47 x PP-49 (counterfactual abduction) can substitute for the
   NKT use case
4. Active energy barrier can be induced via a penalty matrix construction

## Routing

DO NOT ship pp47_pp48_nkt_composition_v1 until Strategy confirms a rescue path.
The signed-AM PP-48 mechanism needs architectural redesign.

Related shipped anchors:
- pp47_pp49_counterfactual_abduction_composition_v1 (shipped as alternative composition)
- pp47_pp9_deletion_cert_composition_v2_reduced_K_v1 (shipped as Phase 0a cert test)
