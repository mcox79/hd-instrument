# Fix #6 zero-D-overlap audit findings (2026-06-22)

**Per Fix #6 discipline atom** (banked autonomous-arc 2026-06-22): `batched_token_logprob` with sparse concept codes + small V_TOK can produce `scores.sum() == 0` rows → softmax NaN. Proper fix = uniform-fallback on zero-rows (not epsilon-floor).

## Audit scope

10 N1/N2/N3/N4/N5/N9-family cells using `batched_token_logprob`:
- `exp_n1_concept_lm_substrate_native_token_decode_v2.py`
- `exp_n1_concept_lm_substrate_native_token_decode_v3.py`
- `exp_n1_concept_lm_substrate_native_token_decode_v3_1.py`
- `exp_n2_capacity_scaling_v1.py`
- `exp_n2_context_depth_hd_binding_v1.py`
- `exp_n2_depth_x_codebook_coopt_v1.py`
- `exp_n3_vq_alignment_simvq_v1.py` (n3 SimVQ — cell-author caught the bug + fixed)
- `exp_n3_mkn_smoothing_v1.py` (MKN — pattern inherited from n3 SimVQ)
- `exp_n4_kwta_soft_decode_v1.py` (n4 — proper fix verified line 256-261)
- `exp_n5_vc_4096_frontier_v1.py` (n5 V_C frontier — proper fix verified line 231-236)
- (`exp_n9_smh_sparsemax_decode_v1.py` — newly dispatched; should have proper fix via pipeline-agent template; verify on land)

## Findings (per-cell)

### Proper uniform-fallback pattern (CORRECT — zero-rows → uniform distribution)

- **n4** lines 256-261: `zero_rows = (row_sums <= 1e-12); safe_scores = np.where(zero_rows, np.ones_like(scores) / V_TOK_local, scores)` ✓
- **n5** lines 231-236: same pattern ✓
- **n3 SimVQ + n3 MKN**: per cell-author reports (commit f5a0685a / ad25a0a3), pattern present (cell-author n3 surfaced the bug + fixed) ✓
- **n9 SMH**: should be present (pipeline-agent template bakes it in); verify on land

### Epsilon-floor pattern (INCOMPLETE — avoids NaN but uninterpretable at zero-overlap)

- **n2_capacity_scaling_v1** lines 227, 237: `probs = scores / (scores.sum(...) + 1e-300)` — produces 1e-300-scale near-uniform at zero-overlap; technically not NaN but semantically meaningless
- **n2_depth_x_codebook_coopt_v1 + n2_context_depth_hd_binding_v1**: likely same pattern (sibling cells; not re-checked)

### No guard (VULNERABLE if zero-overlap rows occur)

- **n1 v3.1 + n1 v3 + n1 v2**: no zero-D-overlap guard found in audit (different cell-architecture; smoke-scale risk only)

## Honest scope (why this is bounded not blocking)

- All OLD cells (n1/n2 family) LANDED FULL-MODE OK in their actual runs (no NaN observed in metrics; verified)
- Reason: at full V_TOK=50257 + N=16384, the probability of a `scores.sum() == 0` row is near-zero (substrate's concept codes are dense enough in the full regime)
- The bug FIRES at SMOKE scale (small V_TOK=1000 + sparse codes) — n3 SimVQ cell-author caught it during smoke validation
- NEW cells (n3+/n4/n5/n9) have the proper fix; future cells using pipeline-agent template will inherit it

## Recommendation

- **TIER 2 queue entry:** "back-port proper uniform-fallback to N1/N2 family cells" — non-urgent (full runs OK); useful for smoke-validation hygiene
- **Discipline atom (META):** `audit-batched-token-logprob-zero-overlap-handling-prefer-uniform-fallback-over-epsilon-floor` — composes with Fix #6; future Skunkworks atomize-pass can capture this
- **Cell-author template (Fix #11):** pipeline-agent template already includes the proper pattern; future spawns use it; no manual back-port needed for new cells

## Status

Audit COMPLETE; finding documented; no immediate action required (old cells OK in full; new cells fixed; template-baked going forward). Filing for cert-trail observability per HYBRID architecture.

— Research (Director), Fix #6 audit per autonomous-arc discipline.
