# Pre-reg: dim_t_joint_surface_alpha_sigma_interaction_v1

**Filed:** 2026-07-02
**Author:** hdi_exp_dev (spawned by hdi_research)
**Origin drill:** `notes/research_dim_t_regime_transitions_composition_2026-07-02.md` Section 7 Option B (cheapest decisive)
**Parent primitive:** `cortex_hippo_dense_beta_sweep_v3_query_noise` (CG 2026-07-01; measured sigma cliff at N=8192, alpha~0.49, beta=13, in sigma ∈ (0.1, 0.3])
**Cell slug:** `dim_t_joint_surface_alpha_sigma_interaction_v1`

## 1. HYPOTHESIS

The substrate's noise-tolerance sigma_crit is NOT independent of load alpha. Specifically:

- **HP_INTERACTION_CONFIRMED:** sigma at which recall crosses 0.50 at alpha=0.45 is SMALLER by >= 0.03 than at alpha=0.10 (joint surface confirmed; M3 refuse-gate must upgrade to joint (alpha, sigma) controller)
- **HF_INTERACTION_ABSENT:** sigma_crit at alpha=0.45 is within 0.02 of sigma_crit at alpha=0.10 (independent transitions; 1D refuse-gate sufficient)

## 2. DESIGN

- **Fixed:** N=8192, beta=13 (from v3 CG regime), numpy CPU
- **Sweep axis 1 (alpha):** M in {819, 3686} corresponding to alpha ∈ {0.10, 0.45} exactly (M = round(alpha * N))
- **Sweep axis 2 (sigma):** 8 sigma values {0.02, 0.05, 0.08, 0.10, 0.13, 0.15, 0.20, 0.30}
- **Seeds:** 3 (7, 13, 19) — chunked one-seed-per-cell per META_RULE §13
- **Encoding:** independent Gaussian keys+vals (v3 regime); queries = keys + N(0, sigma) then l2-normed
- **Readout:** dense-attention softmax(beta * cos(q, K)) @ V; argmax@1 recall (v3-identical mechanism)

**Cardinality per seed:** 2 alpha × 8 sigma = 16 arms
**EXPECTED_N_UNITS (per seed cell):** 16
**Cardinality per full run (3 seeds):** 48 arm outcomes

## 3. PROVENANCE-CONTROL CHECK

**Positive control arm (META_RULE §15 gate D):** at (alpha=0.10, sigma=0.0) and (alpha=0.45, sigma=0.0), recall must be 1.000 within 1e-3. Reproduces v3 NOISE_0P0 saturation exactly. If not, encoder is broken and downstream sigma-sweep is invalid. HF_BROKEN_PC fires.

**Positive control at alpha=0.45:** ARM (alpha=0.45, sigma=0.10) predicted MEASURED@`data/exp_cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7/metrics.json:headline.recall_r13_noise_0p1` = 0.78475. Cell must reproduce within +/- 0.10 (regime alignment gate). If deviation > 0.10 => HF_REGIME_MISMATCH.

## 4. HP / HF / MB conditions

Compute `sigma_crit_alpha_10` = smallest sigma such that mean recall (over 3 seeds; use aggregate metric writer) drops below 0.50; likewise `sigma_crit_alpha_45`. Define via linear interpolation between adjacent sigma sweep points.

- **HP_INTERACTION_CONFIRMED (main HP):** `sigma_crit_alpha_10 - sigma_crit_alpha_45 >= 0.03`
- **HP_MONOTONIC_ALPHA (secondary):** at sigma=0.10, `recall_mean(alpha=0.10) > recall_mean(alpha=0.45)` (higher load => less tolerance at fixed sigma)
- **HP_CROSS_SEED_TIGHT (calibration):** for every (alpha, sigma) point, cv = std/mean < 0.15 (or std < 0.02 when mean < 0.10)

**HF conditions:**
- **HF_INTERACTION_ABSENT:** `|sigma_crit_alpha_10 - sigma_crit_alpha_45| < 0.02` AND HP_MONOTONIC_ALPHA fails (Sonnet drill Type-3 interaction claim refuted; refuse-gate stays 1D)
- **HF_TOTAL_SATURATION:** all 16 points at recall >= 0.98 (both alpha below cliff at all tested sigma; sigma range insufficient)
- **HF_TOTAL_COLLAPSE:** all 16 points at recall <= 0.02 (both alpha above cliff at all tested sigma; sigma range insufficient)
- **HF_BROKEN_PC:** recall(alpha, sigma=0.02) < 0.95 for either alpha (positive control broken)
- **HF_REGIME_MISMATCH:** recall(alpha=0.45, sigma=0.10) deviates from v3 CG value 0.785 by > 0.10 (regime doesn't reproduce)
- **HF_CARDINALITY_BREACH_META_RULE_H:** n_arms != 16 per seed

**MB conditions:**
- 0.01 <= `sigma_crit_alpha_10 - sigma_crit_alpha_45` < 0.03: small interaction, inconclusive
- Cross-seed cv >= 0.15 at any point

## 5. META_RULE COMPLIANCE (SCHEMA-VET checklist)

- `cardinality_ok`: TRUE (`EXPECTED_N_UNITS = 16` per seed)
- `arms_differ_verified`: TRUE at smoke gate (hash-check across 16 arms; ceiling ties at sigma=0.0 exempt)
- `final_metrics_atomicity`: `tmp_replace`
- `except SystemExit: raise` before `except Exception` (no BaseException)
- `crlb_floor_computed_M`: sigma_min = sqrt(0.25/M); for M=819 => 0.0175, for M=3686 => 0.0082. HP delta 0.03 >> CRLB gap at both M values. `discriminator_reachability`: TRUE
- `baseline_in_band`: gate not applicable in classic sense (no baseline-vs-mechanism; both arms measured). Per-alpha sigma=0.02 point serves as PC (must saturate) and sigma=0.30 as ceiling break (must be < 0.50).
- `discriminator_survives_scale`: TRUE — smoke runs AT full N=8192 (numpy fast at these M values; ~1 min per seed) so scale-saturation cannot mask
- `calibration_check`: `default_ok_for_this_regime` (v3 CG confirms v3 regime; this cell extends the alpha axis while holding beta/N/encoding fixed)
- `HP_SCOPE`: applies to all 16 arms uniformly (no exemption)
- `cell_chunked`: TRUE (one seed per cell file: seed_7, seed_13, seed_19)
- `start_marker_written`: TRUE
- `crash_diagnostic_present`: TRUE
- `heartbeat_present`: TRUE (uses experiments._cell_heartbeat)
- `defensive_error_checking`: `passed_all_4_patterns`

### META_RULE §15 gates (composition/sweep cell):

- **A) effective_vs_nominal_parameter_audit:** swept params are `alpha` and `sigma`. `effective_alpha = M/N = M/8192`. Since M is set from alpha (not partition-routed), `effective_alpha == nominal_alpha`. sweep_alignment_verdict: ALIGNED
- **B) bracket_includes_discriminating_band:** predicted recall per (alpha, sigma) from v3 CG extrapolation:
  - alpha=0.10 predicted (sat at low sigma; cliff moves to higher sigma per O(1/sqrt(alpha)) scaling per Dim T drill Section 4)
  - alpha=0.45 predicted (matches v3: 1.0 / 0.785 / 0.003 at sigma 0.0/0.1/0.3)
  - Discriminating-band [0.30, 0.70] predicted to include at least (alpha=0.45, sigma=0.13) and (alpha=0.10, sigma=0.20) and (alpha=0.10, sigma=0.30). Predicted discriminating_fraction >= 3/16 = 0.19; if smoke shows < 0.19 in band, regime nudge needed.
  - HYPOTHESIZED@this-prereg: `points_in_discriminating_band` >= 3
- **C) signal_shape_compatibility_audit:** single dense-attention primitive; no composition edges. SHAPE_MATCH trivial.
- **D) reproduce_prior_chain_grade_result_as_positive_control:** ARM (alpha=0.45, sigma=0.10) reproduces v3 CG at 0.785 +/- 0.10 tolerance. See Section 3 above. `positive_control_arms` declared. `regime_extension_audit`: SHAPE_MATCH (v3 uses M=4000 alpha=0.488 beta=13 N=8192; this cell uses M=3686 alpha=0.45 beta=13 N=8192 — near-identical regime; alpha=0.10 M=819 is the new extension, SHAPE_MATCH by construction since it's a pure alpha reduction within same primitive)
- **E) functional_requirement_decomposition_present:**
  - FR1: measure recall@1 at fixed (alpha, sigma) — chain-grade primitive: dense-attention Hopfield READ (v3 CG)
  - FR2: interpolate sigma_crit at recall=0.50 crossing — analytic; no substrate primitive

## 6. Runtime + timeout

Estimated runtime per seed (16 arms, N=8192):
- alpha=0.10, M=819: per-arm wall ~ 0.5s (small M dominant scaling)
- alpha=0.45, M=3686: per-arm wall ~ 10s (v3 measured ~10.8s at M=4000 identical regime)
- Total per seed: ~ 8 * 0.5 + 8 * 10 = 84s ~ 90s

**per_seed timeout:** 3600s (huge margin per spawn spec).

## 7. Discipline: HYPOTHESIZED vs MEASURED tags in this pre-reg

- alpha=0.45/sigma=0.10 predicted 0.785: MEASURED@`data/exp_cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7/metrics.json:headline.recall_r13_noise_0p1`
- alpha=0.10/sigma-cliff prediction: HYPOTHESIZED@this-prereg (based on Dim T drill Section 4 O(1/sqrt(N)) shift + qualitative alpha-dependence; NOT measured yet)
- sigma_crit interaction >= 0.03: HYPOTHESIZED@this-prereg (Sonnet drill Section 3 joint-surface claim; this cell IS the test)
- CRLB floor sigma_min = sqrt(0.25/M): THEORETICAL@binomial-CLT

## 8. Ship plan

1. Smoke (local_cpu_queue): seed_7 only, verify cell runs at N=8192 full config, verify PC at (0.45, 0.10) reproduces v3 0.785 +/- 0.10
2. If smoke HARD_PASS or MB: hand off seed_7 + seed_13 + seed_19 FULL to hdi_orchestrator for remote_cpu_queue dispatch
3. Landed-VET: hdi_skunkworks reads 3-seed aggregate + tiers HP/HF/MB per this pre-reg
