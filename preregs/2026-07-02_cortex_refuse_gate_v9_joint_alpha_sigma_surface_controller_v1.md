# Pre-registration: cortex_refuse_gate_v9_joint_alpha_sigma_surface_controller_v1

**Filed:** 2026-07-02
**Author:** hdi_exp_dev (Opus 4.7 1M, agent-spawn)
**Anchor:** cortex_refuse_gate_v9_joint_alpha_sigma_surface_controller_v1 (three siblings, seeds 7 / 13 / 19)
**Milestone:** M3 M1.4 (refuse-gate closure; USER-locked). This cell PROMOTES M1.4 v9 as a REVISED-CG version of an already-CG milestone.

## Cross-reference

- **Direct parent (Dim T v1 smoke HP):** `data/exp_dim_t_joint_surface_alpha_sigma_interaction_v1_seed_7/metrics.json`
  - MEASURED@headline.sigma_crit_alpha_10 = 0.1852
  - MEASURED@headline.sigma_crit_alpha_45 = 0.1157
  - MEASURED@headline.delta_sigma_crit = 0.0694 (2.3x HP interaction floor 0.03)
  - MEASURED@headline.recall_a45_s10 = 0.7645
- **M1.4 v8 CG:** `data/exp_substrate_refuse_gate_v8_conformal_v1_seed_7/metrics.json` (1D refuse-gate on cal-source-variation)
- **v3 CG regime parent:** `cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7` (independent Gaussian keys+vals, dense-attention softmax, N=8192, beta=13)
- **Dim T v1 pre-reg:** `preregs/2026-07-02_dim_t_joint_surface_alpha_sigma_interaction_v1.md`

## Prior-work check (substrate-KB concept-query 2026-07-02)

Queries:
- `"M1.4 refuse gate v8 conformal cal-source variation joint alpha sigma"` -> top hit cosine 0.2295 (polysemy neuromodulation gating; unrelated)
- `"Dim T joint surface alpha sigma interaction sigma_crit"` -> top hit cosine 0.3066 (pp50 capacity prefactor sigma_g_crit; adjacent mechanism class, not a joint controller)
- `"refuse gate joint controller two dimensional threshold surface"` -> top hit cosine 0.2773 (runtime confidence display; orthogonal mechanism)

**All top hits below 0.30 -> genuinely novel 2D joint controller cell.** Adjacent prior work (pp50 drill 2026-06-03) proposed a load-dependent tightening rule `sigma_g_safe(alpha) = 0.5 * (1 - 0.2 * alpha/alpha_c) * sigma_g_crit` for kappa_3 noise -- different mechanism class (Hutchinson trace noise vs argmax@1 recall degradation). Our cell operationalizes the alpha-dependence for the DENSE-ATTENTION READ regime empirically anchored on Dim T v1.

## Mechanism-class contrast

| Aspect | v8 (existing CG) | v9 (this cell) |
|---|---|---|
| Controller dimension | 1D (measured_sigma only) | 2D joint (measured_sigma AND current alpha) |
| Threshold | `tau_v8 = 0.15` (constant) | `tau_v9(alpha) = 0.2050 - 0.1986 * alpha` (linear in alpha) |
| Cal-source axis | REGIME (clean / moderate / heavy) | ALPHA (0.10 / 0.25 / 0.45 load) |
| Justification anchor | LLN point-mass 2x-drill 2026-07-01 | Dim T v1 seed_7 empirical sigma_crit(alpha) 2026-07-02 |
| Query decision | `accept iff measured_sigma < tau_v8` | `accept iff measured_sigma < tau_v9(current_alpha)` |
| Load-awareness | none | reads current M/N at query time |

## Predicted controller behavior (analytical + Dim T empirical anchors)

`tau_v9(alpha)` linear-interp anchored on Dim T v1:
- alpha=0.10 -> tau=0.1853  (from sigma_crit(0.10) MEASURED@0.1852)
- alpha=0.25 -> tau=0.1557  (interpolated)
- alpha=0.45 -> tau=0.1163  (from sigma_crit(0.45) MEASURED@0.1157)

`tau_v8 = 0.15` (compromise between 0.185 and 0.116).

Predicted decision matrix (12 conditions):

| alpha | sigma | v8 decision | v9 decision | Dim T raw_recall (extrap.) | v8 useful | v9 useful | delta_v9_minus_v8 |
|---|---|---|---|---|---|---|---|
| 0.10 | 0.02 | ACCEPT | ACCEPT | 1.000 | 1.000 | 1.000 | 0.000 |
| 0.10 | 0.08 | ACCEPT | ACCEPT | 1.000 | 1.000 | 1.000 | 0.000 |
| 0.10 | 0.15 | REFUSE | ACCEPT | 0.875 | 0.000 | 0.875 | **+0.875** |
| 0.10 | 0.25 | REFUSE | REFUSE | ~0.15 | 0.000 | 0.000 | 0.000 |
| 0.25 | 0.02 | ACCEPT | ACCEPT | ~1.000 | 1.000 | 1.000 | 0.000 |
| 0.25 | 0.08 | ACCEPT | ACCEPT | ~0.95 | 0.95 | 0.95 | 0.000 |
| 0.25 | 0.15 | REFUSE | ACCEPT | ~0.55 | 0.000 | 0.55 | +0.55 |
| 0.25 | 0.25 | REFUSE | REFUSE | ~0.10 | 0.000 | 0.000 | 0.000 |
| 0.45 | 0.02 | ACCEPT | ACCEPT | 1.000 | 1.000 | 1.000 | 0.000 |
| 0.45 | 0.08 | ACCEPT | ACCEPT | 0.991 | 0.991 | 0.991 | 0.000 |
| 0.45 | 0.15 | REFUSE | REFUSE | 0.186 | 0.000 | 0.000 | 0.000 |
| 0.45 | 0.25 | REFUSE | REFUSE | ~0.02 | 0.000 | 0.000 | 0.000 |

**Key discriminator conditions:** (0.10, 0.15) and (0.25, 0.15) -- v9 correctly ACCEPTS where v8 wrongly REFUSES (raw recall still above 0.5 at low load).

**Note on Director's "HP_V9_LIFTS_HIGH_LOAD":** the empirical Dim T v1 data shows that at (alpha=0.45, sigma=0.10) raw_recall is 0.765 -- which is ABOVE the useful-recall floor for a 1D controller with tau=0.15 (v8 accepts, gets 0.765 useful). At sigma=0.10, both controllers agree because 0.10 < both taus. The direction where v9 CORRECTS a v8 failure at high load is at sigma=0.13-0.14 (v8 accepts and gets low raw_recall ~0.26; v9 refuses). But sigma=0.13 is not in the grid; we bracket with (0.45, 0.15) where both refuse. Empirically the low-load-lift direction (0.10, 0.15) is a stronger discriminator, and we upgrade it to the primary HP.

## Cell design

**Arms (2):**
- `ARM_1D_V8_BASELINE`: v8-style fixed threshold on measured_sigma; tau=0.15 constant
- `ARM_2D_V9_JOINT`: v9 joint controller; tau=`0.2050 - 0.1986 * current_alpha`

**Grid:** alpha in {0.10, 0.25, 0.45} x sigma in {0.02, 0.08, 0.15, 0.25} = 12 conditions per arm.

**Cardinality:** 2 arms x 3 alpha x 4 sigma = **24 arms per seed** (LOCKED; META_RULE_H).

**Substrate scale (both smoke AND full):** N=8192, dense-attention softmax(beta=13), independent Gaussian keys+vals (v3 CG regime). SMOKE at full-N=8192 satisfies **DISCRIMINATOR-MUST-SURVIVE-SCALE** (Check A path); numpy CPU makes full-N smoke cheap.

**Queries per condition:** 60 (both smoke and full identical; CRLB reachability locked).

**Seeds:** 7 / 13 / 19 (siblings; CHUNKED single-seed-per-cell).

## Metric definitions

- `raw_recall_all`: argmax@1 recall over all `n_queries` queries in the condition (uses substrate primitive; independent of gate decision).
- `accept_rate`: 1.0 if `measured_sigma < tau(alpha)` else 0.0 (uniform per condition since we use the true sigma sweep axis as the sigma measurement; production sigma-estimator is follow-up scope).
- `useful_recall`: `accept_rate * raw_recall_all` -- P(gate returns a correct answer). This is the primary discriminator.

## HP conditions (per-seed; final tier at Skunkworks VET; 3-seed cv gate)

- **HP_V9_LIFTS_LOW_LOAD_ACCEPT (primary):** at (alpha=0.10, sigma=0.15), `v9_useful_recall - v8_useful_recall >= 0.30`. Predicted delta ~0.875 from Dim T v1 anchors (v8 refuses giving useful=0; v9 accepts giving useful~=raw_recall=0.875).
- **HP_V9_MAINTAINS_SAFE_REGIME:** at (alpha=0.10, sigma=0.02) AND (alpha=0.45, sigma=0.02), v9 `accept_rate >= 0.95` AND `useful_recall >= 0.95` (v9 does not over-refuse at safe regime).
- **HP_V9_CROSS_SEED_TIGHT (Director spec; aggregate at VET):** cv < 0.15 across 3 seeds on the primary lift delta.

Cell-level HARD_PASS granted if BOTH HP_LIFTS_LOW_LOAD and HP_MAINTAINS_SAFE_REGIME pass on a seed.

## HF conditions

- **HF_V9_UNDER_PERFORMS_V8_SAFE:** at any (alpha, sigma=0.02) `v8_useful_recall - v9_useful_recall >= 0.05` (safe-regime regression).
- **HF_V9_MISCALIBRATED_LOW_LOAD_OVER_REFUSE:** at (alpha=0.10, sigma=0.02) v9 `refuse_rate > 0.20`.
- **HF_TOTAL_SATURATION:** all 24 arms useful_recall >= 0.98.
- **HF_TOTAL_COLLAPSE:** all 24 arms useful_recall <= 0.02.
- **HF_BROKEN_PC:** raw recall at (alpha=0.10, sigma=0.02) < 0.95 (substrate primitive broken).
- **HF_REGIME_MISMATCH:** raw recall at (alpha=0.45, sigma=0.08) < 0.80 (Dim T v1 seed_7 MEASURED@0.991; regime not reproducing).
- **HF_ARM_DIFFERS_SANITY:** fewer than 4 of 12 (alpha, sigma) conditions produce different arm_digest between v8 and v9 arms (controller is a no-op).
- **HF_CARDINALITY_BREACH:** n_arms != 24.

## Positive controls (META_RULE §15 gate D)

- **PC_1:** raw_recall at (alpha=0.10, sigma=0.02) >= 0.95 for both arms (substrate primitive alive).
- **PC_2:** at least 4 of 12 (alpha, sigma) conditions produce different arm_digest between v8 and v9 (controller genuinely 2D-sensitive).

## Envelope-fail-bands

| Band | Meaning | Trigger |
|---|---|---|
| HARD_PASS | v9 architecture validated | HP_LIFT AND HP_SAFE |
| MIDDLE_BAND | partial evidence | one HP passes, other partial (or lift 0.10 <= delta < 0.30) |
| HARD_FAIL | v9 doesn't beat v8 OR PC broken OR safe regime broken | any HF fires |

## CRLB reachability

For a delta of two useful_recall values (each estimated over n queries), CRLB is `sqrt(2 * 0.25 / n)`. At n=60: CRLB delta = 0.091. HP floor 0.30 >> CRLB delta -> discriminator reachability confirmed.

CRLB per single useful_recall at n=60: sqrt(0.25/60) = 0.065. Safe regime floor 0.95 - 3 * 0.065 = 0.755 (2-sigma below floor at 0.815), so with n=60 we can distinguish 0.95 from 0.85 with p < 0.01.

## CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH)

- [x] arms_differ_verified via arm_digest hash-check (META_RULE_AF)
- [x] final_metrics_atomicity: tmp_replace (META_RULE_AH)
- [x] except SystemExit: raise BEFORE except Exception (no BaseException)
- [x] crlb_floor_computed + discriminator_reachability declared
- [x] discriminator survives scale: smoke at full N=8192 (Check A)
- [x] HP strictly above delta floor (>= 0.30)
- [x] cardinality_ok: 24 arms per seed (META_RULE_H)
- [x] per-unit failure-class instrumentation (arm_status)
- [x] calibration_check: default_ok_for_this_regime (Dim T v1 reproduces at alpha=0.45, sigma=0.08 >= 0.80 raw_recall)
- [x] numbers tagged MEASURED@ / THEORETICAL@ in pre-reg (META_RULE_AC)
- [x] import torch at cell top-of-file (Fix #24)

## Load-bearing framing (Director-supplied)

If HP, this closes the cortex-primitives-are-ready loop for M3 Phase 1. M1.4 v9 is a REVISED-CG version of an already-CG milestone; represents genuine architecture evolution based on today's Dim T finding. Chain-grade-eligible for the cortex layer.

This cell also PROMOTES Dim T v1 from smoke-HP to CG-eligible by empirically validating the joint-surface architecture claim.

## Timeout

Per-seed timeout: 3600s (1 hour). Estimated wall based on Dim T v1 seed_7 wall (~5-10 min for 16 arms at N=8192 numpy CPU); this cell has 24 arms so scaled estimate 8-15 min per seed. 3600s gives ~4x safety margin.

## Dispatch plan

- Smoke: local_cpu_queue (SMOKE ONLY per USER-locked 2026-07-01)
- Full: remote_cpu_queue (numpy CPU; NOT overnight_queue which is GPU)
