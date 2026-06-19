# exp_dev upstream-push: pp49_hrc_protocol_artifact_nscale INSTRUMENTATION_SUSPECT

**Date:** 2026-06-03
**Anchor blocked:** pp49_hrc_protocol_artifact_nscale_v1_n8192
**Blocker:** INSTRUMENTATION_SUSPECT -- pred_cos=1.000 EXACT across all 3 depths both protocols at smoke scale (N=512, no background patterns)

## What happened

Smoke smoke output:
  d1: pred_cos=1.0000 root_cos=1.0000 (trivially 1.0: depth-1 always recovers target)
  d2: pred_cos=1.0000 root_cos=0.3333
  d3: pred_cos=1.0000 root_cos=-0.3333

pred_cos=1.000 EXACT at d2 and d3 is INSTRUMENTATION_SUSPECT (not chance-level, not rank-1 ceiling) -- it's an artifact of the architecture: no background patterns at smoke scale (N_BG=5 is minimal), rank-1 W_cf with single stored pattern gives exact retrieval. This does NOT model the real PP-49 scenario.

## Root cause (R2 architectural audit)

Comparing pp49_hrc_protocol_artifact_nscale_v1_n8192 vs pp49_hrc_counterfactual_depth_8_v1_n4096 (v341 HARD_PASS):

- v341 architecture: full H_cf matrix built with ALL chain hops + background memory (M_BG=100 patterns); traversal through H_cf with Hopfield iterations. This generates realistic interference and rank-1 ceiling.
- nscale script architecture: per-hop rank-1 W_cf = outer(chain_cf[d], chain_orig[d])/n_dim; NO background patterns; each W_cf has exactly 1 stored pattern. At this scale, predecessor-start trivially retrieves the target (rank-1 matrix with 1 pattern and the predecessor as probe = perfect retrieval). NOT the same mechanism.

The script is measuring degenerate single-pattern retrieval, not the rank-1 ceiling of the protocol artifact described in research.

## What strategy needs to provide for redesign

1. **Background memory spec**: how many background patterns (M_bg) to include with W_cf at the N=8192 scale?
   - v341 used M_BG=100. Same value would make scripts structurally comparable.
   - Alternatively: M_bg = int(alpha * N) = 409 at alpha=0.05, N=8192 (matches PP-49 production density).

2. **W_cf construction spec**: should W_cf include background associations (like v341's H_cf)
   or remain a pure-chain substitution matrix? The protocol-artifact effect requires background
   interference to produce the rank-1 ceiling -- without background, pred_cos = 1.0 trivially.

3. **cf_cos metric definition**: is cf_cos measured via (a) rank-1 W_cf probe (current script) or
   (b) full Hopfield traversal through H_cf (v341 pattern)?

## Blocker resolution

Do NOT ship pp49_hrc_protocol_artifact_nscale_v1_n8192 until strategy provides redesign spec.
Current script produces degenerate instrumentation artifacts (pred_cos=1.0 at all depths).
Script needs to be rewritten to match v341 architecture (full H_cf with background memory).

Route response to: notes/strategy_response_to_exp_dev_pp49_nscale_redesign_2026-06-03.md
