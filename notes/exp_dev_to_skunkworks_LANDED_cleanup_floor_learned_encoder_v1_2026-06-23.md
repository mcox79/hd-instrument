# LANDED -- cleanup_floor_learned_encoder_v1 (META BRANCH #3 OF 3 CLOSED)

**From:** exp_dev (spawn-and-die author)
**To:** skunkworks (cert-owner; tier-up consideration)
**Anchor:** `cleanup_floor_learned_encoder_v1`
**Landed:** 2026-06-23 09:07 (full run; 3 seeds; elapsed ~0.6s)
**Metrics:** `data/exp_cleanup_floor_learned_encoder_v1/metrics.json`
**Commit:** bfd234b8

## Verdict (per-arm verified via peek_arm_metrics.py + direct JSON read)

**META_BRANCH3_CHAIN_GRADE_ELIGIBLE** -- Shannon-floor applies across RANDOM + LEARNED +
STRUCTURED codebook types at sigma=1.5.

Per-arm at discriminator sigma=1.5 (mean across 3 seeds, N_EVAL=200, N=2048, M=200):

| Arm | mean | std | cv | per-seed |
|---|---|---|---|---|
| ARM_RANDOM_BIPOLAR | 0.0217 | 0.0125 | 0.576 | [0.005, 0.025, 0.035] |
| ARM_CHAR_TRIGRAM_LEARNED | 0.0267 | 0.0094 | 0.354 | [0.040, 0.020, 0.020] |
| ARM_HUB_SPOKE_STRUCTURED | 0.0150 | 0.0082 | 0.544 | [0.005, 0.025, 0.015] |

All 3 arms recall(sigma=1.5) < 0.10 -> CHAIN_GRADE_ELIGIBLE rule fires.

## Sanity checks (PASS)

- sigma=0.0 sanity: all (seed, arm) cells recall >= 0.99 (sanity_violations=[])
- ARM_RANDOM_BIPOLAR at sigma=1.5 N=2048 = 0.0217 -> reproduces prior parent data point
  (0.027 from cleanup_floor_N_DIM_scan_v1) within tolerance +/- 0.01 (delta = 0.006)
- _LLM_CALL_COUNTER == 0 (substrate-only-decode gate intact)

## Cross-sigma map (per-arm)

| Arm | sigma=1.0 | sigma=1.5 | sigma=2.0 |
|---|---|---|---|
| ARM_RANDOM_BIPOLAR | 0.0550 | 0.0217 | 0.0250 |
| ARM_CHAR_TRIGRAM_LEARNED | 0.0350 | 0.0267 | 0.0167 |
| ARM_HUB_SPOKE_STRUCTURED | 0.0483 | 0.0150 | 0.0183 |

Floor is flat-low across all 3 arms in [1.0, 2.0]; no arm escapes 0.10 at any sigma in the
discriminating band. Even sigma=1.0 stays in the floor regime across all 3 codebook types.

## Cert-owner recommendation (NOT cert-owner's call -- this is exp_dev surfacing)

With branches #1 (N-DIM-INDEPENDENT 512-16384), #2 (M-INDEPENDENT 25-400), and #3
(codebook-type-INDEPENDENT across RANDOM + LEARNED + STRUCTURED) all closed, the META
`T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0`
(cert ledger row 675) has all 3 branches characterized.

Recommend Skunkworks deliberate tier-up of parent META to chain-grade. Cert-owner's call
under role-separation discipline.

## Honest framing notes (Fix #28 compliance)

- Verdict_msg was derived FROM per-arm metrics, not the other way around.
- I cross-checked verdict_msg framing against per-arm numbers directly (script above)
  before propagating this LANDED summary.
- 3-seed CV at sigma=1.5 is high for ARM_RANDOM_BIPOLAR (0.576) and ARM_HUB_SPOKE_STRUCTURED
  (0.544) because mean is near floor; absolute std is small (~0.008-0.013) and well within
  noise-floor regime. ARM_CHAR_TRIGRAM_LEARNED has the lowest CV (0.354) and the highest
  mean (0.0267), but still well below 0.10 threshold.
- N_DIM=2048 only; structured-arm scaling at other N_DIM untested. Cited honestly in scope.
- Conceptnet5_en_100k subject/object tokens = 200 English-word codebook seed; not all
  possible "learned" encoders tested -- substrate-native trigram bag is one family.
- HUB_SPOKE composition is 20x10 specific; tree/manifold/gradient-trained structured codebooks
  not in scope.

## Cites

- cert_ledger row 675 (parent META)
- Skunkworks tiering 2026-06-23 (MEASURED_MECHANISM until 3 branches close)
- cleanup_floor_N_DIM_scan_v1, cleanup_floor_M_scan_v1 (branches #1, #2)
- USER 2026-06-22 directive: empowered-to-experiment-where-lit-says-dismissed
- Fix #28 (verify per-arm metrics before cross-cell convergence claims)
