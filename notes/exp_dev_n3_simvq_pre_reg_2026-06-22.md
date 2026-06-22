# PRE-REG: n3_vq_alignment_simvq_v1 (SimVQ-MVP-vs-baseline at V_C=1024, N_DIM=16384)

**From:** Exp-Dev (cell-author spawn, USER-authorized n3 design)
**Date:** 2026-06-22
**Cell source:** `experiments/exp_n3_vq_alignment_simvq_v1.py`
**Routing context:** `notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md` (Research drill, decode-side levers)
**Skunkworks structural-blocker compliance:** Skunkworks's N2 chain-grade structural blockers all 4 baked (see Instrumentation section).
**Composes with:** N2 `n2_capacity_scaling_v1` MIDDLE_BAND (LANDED_VET 2026-06-22) -- inherits residual data + best config + anchor-reproduction discipline.

## Independent variable
`PROJ_DIM` (linear-projection dimensionality for SimVQ-MVP arm). Three values swept per seed:
- **PROJ_DIM=768** = identity projection (matches N2 baseline; the ANCHOR-OK arm)
- **PROJ_DIM=64** = SimVQ-MVP, PCA-fit projection to 64 dims, then VQ in projected space
- **PROJ_DIM=32** = SimVQ-MVP, PCA-fit projection to 32 dims, more aggressive

## Fixed config (matches N2 best, reduces confounding)
- V_C = 1024
- N_DIM = 16384
- K = 1 (skip K=2 sweep; n2 shows K=2 floor-masked at every N; SimVQ-K2 deferred to follow-on)
- f_sparse = 0.006 (Willshaw sweet-spot)
- 3 seeds: 7, 17, 23 (matches N2)
- Corpus: pythia-160m residuals (matches N2 exactly; direct comparability via anchor arm)
- TRAIN_FRAC = 0.8, LAM_BACKOFF = 0.1, INTERP_B = 0.3 (Jelinek-Mercer baselines)

## SimVQ-MVP mechanism (substrate-only-gate compatible)
At INGEST (no LLM calls): fit a linear projection W (residual_dim, proj_dim) via PCA on L2-normalized
train residuals. Project all residuals through W, L2-renormalize in projected space, then fit
MiniBatchKMeans on the projected representations. The PCA-derived projection concentrates the
residual variance into proj_dim directions; the hypothesis (per Research drill) is that semantically
distinct residuals that MiniBatchKMeans conflates in 768-d Voronoi space get separated in
lower-d PCA-aligned space, reducing within-concept token entropy.

This is the **MVP form** of SimVQ. Full SimVQ (learnable W trained jointly with VQ) is a follow-on
cell if MVP HARD-FAILs. The MVP captures the "linear-projection-before-VQ" core mechanism.

## Pre-registered bands (decode-side ceiling_bpc primary; research note 2026-06-22)

### HARD_PASS (chain-grade; ALL of):
- some PROJ_DIM has `ceiling_bpc <= 1.75` (>= 0.30 bits drop from N2 anchor 2.049)
- same PROJ_DIM has `substrate_bpc <= 4.75` (>= 0.21 bits drop from N2 anchor 4.959)
- cv across seeds <= 0.05 for the passing config
- NOT saturated (alpha < 1.0; at N=16384 expected alpha~0.5 per N2)
- substrate-only-decode (zero LLM calls at inference -- enforced by code-trace + asserted in metrics)
- identity-arm anchor reproduces N2 ceiling_bpc=2.049 within 0.05 bits

### MIDDLE_BAND (mechanism partial; EITHER of):
- ceiling_bpc drops 0.10-0.30 bits vs identity arm
- substrate_bpc improves but doesn't beat bigram_bpc=3.844

### HARD_FAIL:
- ceiling_bpc change < 0.05 bits across all PROJ_DIM (SimVQ-MVP does NOT help -- route to Path A V_C=4096)
- OR identity-arm anchor mismatch (PROJ_DIM=768 ceiling_bpc differs from N2's 2.049 by > 0.05) -- baseline broken, cell INCONCLUSIVE
- OR LLM-call counter > 0 at any inference path -- substrate-only-gate violated

## Discriminating-regime requirement (C5 per cert-architecture)
The CAN-fail regime is V_C=1024, N_DIM=16384. The cell MUST report per-seed ceiling_bpc for the
identity arm. If identity-arm ceiling_bpc doesn't replicate N2's 2.049 within 0.05 bits, the
baseline is corrupt and the cell is INCONCLUSIVE (anchor mismatch path -> HARD_FAIL).

## Instrumentation (all 4 Skunkworks chain-grade structural blockers baked)

1. **per_unit**: `metrics["per_seed"][i]["per_unit"]` is a list of dicts, one per (seed, PROJ_DIM).
   Each entry contains: `seed, proj_dim, substrate_bpc, ceiling_bpc, bigram_bpc, unigram_bpc,
   substrate_top1, ceiling_top1, substrate_concept_top1, codebook_utilization, alpha, saturated,
   is_identity_arm, effective_proj_dim, k_active, n_trans, n_token_test_pairs,
   llm_forward_calls_at_inference, wall_s`. Recompute-off-per_unit ready (Skunkworks audit
   discipline `cited-number-must-reproduce-from-cell`).

2. **cv <= 0.05**: computed across seeds for each PROJ_DIM in the `verdict()` function. The HARD_PASS
   band requires the passing PROJ_DIM's substrate_bpc cv <= 0.05.

3. **zero_llm_calls_at_inference LOGGED**: module-level `_LLM_CALL_COUNTER = [0]` counter.
   `metrics["zero_llm_calls_at_inference"] = True` and `metrics["total_llm_forward_calls_observed"]`
   are baked. Code-trace audit: zero `model(`, `forward(`, `.generate(`, `transformers.`, `torch.`
   imports or calls in the cell (re-verified). Pythia residuals are PRE-COMPUTED at ingest;
   inference path is pure numpy.

4. **VQ-floor decomposition**: ceiling_bpc reported PER-PROJ_DIM (the irreducible within-concept-
   token entropy at oracle concept prediction). substrate_bpc - ceiling_bpc = distillation gap.
   gain_above_vq_floor = identity_ceiling - simvq_ceiling = the load-bearing mechanism claim.

## Smoke verdict (pre-flight gate; PASSED)
**Smoke config:** V_C=1024, N_DIM=512, V_TOK=1000, 1 seed (seed=1), MAX_DOCS=200, PROJ_DIM_GRID=[768,16,8].
**Smoke run on remote (marsh@home, the production runner):**
- selftest 10/10 PASS
- All 3 PROJ_DIM arms produced finite BPC metrics (zero NaNs after divide-by-zero fallback fix)
- zero_llm_calls_at_inference: True (asserted at metrics write)
- Identity arm produced sub_bpc=2.831, ceiling_bpc=1.030 (at smoke scale; absolute values do
  NOT match N2 full-scale 5.288/2.049 -- expected divergence at smoke scale; the anchor-mismatch
  HARD_FAIL is the smoke verdict's INTENDED behavior since smoke != full)
- Wall time 13.6s for 3 PROJ_DIM x 1 seed at smoke scale

**Smoke gate green:** mechanism end-to-end works; per_unit shape correct; cv computation reaches
finite numbers; LLM-call counter audits to 0; anchor-check infrastructure fires correctly (it
catches the smoke-vs-full configuration mismatch, validating the gate's discrimination).

## Measured runtime estimate (from smoke + N2 lineage)

**Smoke MEASURED:** 13.6s for 3 PROJ_DIM x 1 seed at N=512/V_TOK=1000/MAX_DOCS=200 on remote.

**Full-scale extrapolation (per the discipline "MEASURE, don't quote"):**
- N2 N=16384/K=1 wall ~30 min/seed for 2 K configs (per n2 production metrics)
- One K-config-arm ~ 15 min wall at N=16384 full scale
- One PROJ_DIM arm has SAME compute as one K=1 config (sparse codebook + transition store +
  W = N^2 matmul + recall + decode are the dominant costs; PCA adds <0.1% overhead at 768x768
  covariance fit)
- 3 PROJ_DIM x 3 seeds = 9 cells x ~15 min = ~135 min wall budget total (assuming serial)

**Dispatch timeout = 18000s (5 hours)**: 2x the measured-extrapolation, generous margin for VQ
re-fitting per arm + checkpoint resume overhead.

## Falsifiable predictions (research note 2026-06-22, deflated)

### Prediction 1 (PRIMARY, calibrated P=0.40-0.45)
SimVQ MVP at PROJ_DIM=64 OR 32 lowers ceiling_bpc by >= 0.30 bits at V_C=1024, N_DIM=16384.
Mechanism: PCA projection separates residuals with heterogeneous token distributions into
different Voronoi cells; lower within-concept token entropy -> lower ceiling.

### Prediction 2 (nullability)
If SimVQ HARD_FAILs (ceiling_bpc change < 0.05 across all PROJ_DIM), the bottleneck is NOT
VQ-alignment at V_C=1024; the substrate's decode floor is codebook-granularity-limited, and
Path A (V_C=4096 x N=32768+) becomes the only evidence-based next step.

### Prediction 3 (anchor sanity)
Identity arm (PROJ_DIM=768) should reproduce N2's ceiling_bpc=2.049 within 0.05 bits at full
scale. If not, the cell's harness deviates from N2 in some way (anchor-mismatch HARD_FAIL).

## Dispatch plan
- Queue: `remote_cpu_queue` (residuals_per_token.npz lives on marsh@home; ~34.5MB; verified
  present on remote)
- Timeout: 18000s (5h, 2x measured-extrapolation margin)
- Self-test: PASSED on local (.venv Python 3.11) + on remote (marsh@home .venv)
- Smoke: PASSED on remote with real residuals (zero NaN, zero LLM calls, mechanism end-to-end)
- Substrate-only-gate: PASSED by code-trace (zero LLM-related imports / calls; verified in commit)

## Cell author notes
- This is the FIRST Path B (decode-side improvement) cell, following Research drill priority #1.
- SimVQ MVP form (PCA-init projection) chosen per Research note for low-engineering-cost first probe.
- If MVP MIDDLE_BANDs, full-learned SimVQ (joint VQ + W training) is the natural follow-on.
- If MVP HARD_PASSes, the composition cell (SimVQ + MKN smoothing) is the next ship.
- If MVP HARD_FAILs (ceiling unchanged), Path A (V_C=4096 x N=32768+) becomes the evidence-based path.

-- Exp-Dev (cell-author spawn, context dies on reply)
