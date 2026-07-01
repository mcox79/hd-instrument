# Pre-reg: sparsity_free_axis_v1

**Filed:** 2026-07-01 (UTC)
**Author:** hdi_exp_dev (Opus 4.7 1M)
**Research pointer:** `notes/research_phase_diagram_gap_analysis_wave2_2026-07-01.md` (§3)
**Composes:** A x C batch v2 CG (calibration) per META_RULE_AT
**Design classifier:** Axis C (sparsity) SWEPT as FREE axis; encoder FIXED at HRR-real (chain-grade default); regime SWEPT (PC vs WM); regime-conditional annotation per META_RULE_AO.

---

## Motivation (verified from wave-2 §3)

Axis C sparsity has <5% inner coverage per TRUE_PHASE_DIAGRAM (2026-06-30). Wave-1 batch A v2 tested sparsity x encoder cross-product at fixed PC regime. UNDRILLED: sparsity swept as FREE axis with encoder FIXED at chain-grade default (HRR-real) across PC + WM regimes.

**Substrate-product framing:** if sparsity alpha in {0.005, 0.01, 0.025, 0.05, 0.10, 0.20} shifts K_cliff / bank-recall monotonically at HRR-real, we get a substrate-only capacity lever DECOUPLED from encoder choice. If FLAT, confirms sparsity is not a load-bearing substrate axis (closure valuable as negative).

**Cross-domain grounding (Tier-1b scope-expansion, drill_count=1):**
- Sparse-coding / compressed-sensing: L1-LASSO phase transitions predict capacity-cliff shift with sparsity.
- Bio: DG mossy-cell sparse coding (Kesner-Rolls); optimal sparsity ~1-5% for pattern separation.
- Matsci: sparse crossbar arrays (Sebastian 2020) show sparsity-dependent read-noise floor.

---

## Design (LOCKED)

### Grid

- **Axis C (SWEPT):** sparsity alpha in {0.005, 0.010, 0.025, 0.050, 0.100, 0.200} = 6 levels
- **Axis regime (SWEPT):** {PC, WM} = 2 regimes
- **Encoder (FIXED):** hrr_real (chain-grade default; Gaussian codebook L2-normalized; renormalize after mask)
- **Binding (FIXED):** Hadamard (dense element-wise for hrr_real)
- **Seeds:** {7, 13, 19} (3-seed chunked per USER 2026-06-28)

**Cardinality per seed:** 6 alpha x 2 regime = 12 phase points.
- FULL: `EXPECTED_N_UNITS_FULL = 12`
- SMOKE: 6 alpha x 1 regime (PC only) = 6 -> `EXPECTED_N_UNITS_SMOKE = 6`
- SMOKE uses full-N + half-M per DISCRIMINATOR-SURVIVES-SCALE.

### Regime parameters

**PC regime (single-bank pattern completion):**
- N = 8192 (cliff-observable per PC v2.2 CG)
- M_items = 100 (FULL) / 50 (SMOKE)
- Corruption c = 0.485 (cliff-K per PC v2.2 CG, MEASURED@2daf9b55)
- T_cleanup = 5 iters, beta = 8.0
- Query = corrupt(X) -> T-step modern-Hopfield cleanup -> top1 recall

**WM regime (multi-bank working memory):**
- N = 8192
- K = 500 keys per bank (FULL); K = 250 (SMOKE)
- B = 16 banks
- Corruption c = 0.30 (WM regime standard)
- T_cleanup = 3, beta = 8.0
- Query = bind(key_b, corrupt(value_b_i)) at random bank b, index i; unbind; top1 over K
- Aggregate bank-averaged top1

### Fixed regime knobs (BOTH regimes)

- Encoder = hrr_real, sign_op = L2-normalize, score = dot product
- Sparsity mask applied per row after codebook build; renormalize AFTER mask.

---

## Discriminator (HP band; META_RULE_L band-floor MB)

**HARD_PASS (CG-eligible):**
- HP_A: `per_regime_sparsity_range >= 0.10` for AT LEAST ONE regime, where range = max(recall) - min(recall) across 2 NON-ADJACENT sparsity levels (e.g., alpha=0.005 vs alpha=0.10)
- HP_B: monotonicity check: recall(alpha) monotonic in alpha across 6 sparsity levels for AT LEAST ONE regime (Spearman |rho| >= 0.80 with fixed direction)
- HP_C: 3-seed cv <= 0.10 per (regime, alpha) point
- HP_D: cardinality_ok = True (observed_n_units == expected)
- HP_E: baseline_in_band (RANDOM_FLOOR arm at chance 1/M for PC, 1/K for WM; per-point discriminator = mechanism - floor)

HP_B is **HP-critical** (monotonicity is the load-bearing "sparsity as free lever" claim).

**MIDDLE_BAND:**
- Sparsity range >= 0.10 in one regime BUT monotonicity fails, OR
- Monotonicity passes BUT range < 0.10 (weak lever), OR
- 3-seed cv > 0.10 but < 0.15 (borderline consistency)

**HARD_FAIL:**
- All points SATURATED at ceiling (>= 0.95) or FLOOR (<= 0.05) with no discrimination
- Cardinality breach (observed != expected)
- Arms identical (mechanism == random per point)
- Positive control fail
- cv > 0.15

## META rules composed

- **META_RULE_AC:** arms_differ_verified at smoke gate (MECHANISM vs RANDOM_FLOOR at each point)
- **META_RULE_AE:** discriminator bands LOCKED at module init (constants)
- **META_RULE_AF:** final_metrics_atomicity via tmp_replace
- **META_RULE_AG:** CRLB floor computed + reachable (per-point `crlb_1step_cliff_prediction`)
- **META_RULE_AH:** except SystemExit: raise BEFORE except Exception in main()
- **META_RULE_AO:** regime-conditional annotation (per-point verdict tier + regime tag)
- **META_RULE_AT:** compose with A x C v2 CG (batch A) as calibration point; positive control = hrr_real @ alpha=0.10 in PC regime top1 in [0.30, 0.90]
- **META_RULE_AX:** per-arm mechanism_hash distinct per (regime, alpha)
- **META_RULE_AY:** HARD_FAIL on self-reported distinctness False
- **META_RULE_H (CARDINALITY_OK):** `EXPECTED_N_UNITS_FULL=12`, `EXPECTED_N_UNITS_SMOKE=6`; halt on breach
- **META_RULE_J:** no silent except -- per-point exceptions HALT (no bare except)
- **META_RULE_L:** band-floor result = MIDDLE_BAND not HARD_PASS
- **META_RULE_Q:** SATURATION check -- at alpha=0.005 (very sparse) recall may saturate to FLOOR; mitigation = 6-level design forces at least 4 non-trivial points
- **META_RULE_AV:** verify FULL run mode not selftest

## Positive control (META_RULE_BC)

- **PC regime, hrr_real @ alpha=0.10, M=100, c=0.485:** top1 in [0.30, 0.90] band
  - THEORETICAL@Hopfield capacity 2M log(M)/N_eff: cap_ratio = 2*100*log(100)/(0.10*8192) = 1.12; sits just below break edge; expect solid recall.
- **WM regime, hrr_real @ alpha=0.10, K=500, B=16, c=0.30:** bank-avg top1 in [0.20, 0.80] band

## CRLB / capacity-feasibility (META_RULE_AG)

Per-point `crlb_1step_cliff_prediction(N, M_or_K, alpha)`:
- PC alpha=0.005: N_eff=41, sqrt(2 log 100 / 41)=0.474, cliff=0.263 (BELOW 0.485; predicted FLOOR)
- PC alpha=0.050: N_eff=410, sqrt(2 log 100 / 410)=0.150, cliff=0.425 (BELOW 0.485; predicted breaking)
- PC alpha=0.100: N_eff=819, cliff=0.462 (near 0.485; predicted MB)
- PC alpha=0.200: N_eff=1638, cliff=0.481 (near 0.485; predicted HP band)
- WM alpha=0.005: N_eff=41, sqrt(2 log 500 / 41)=0.549 -> cliff negative; predicted FLOOR
- WM alpha=0.200: N_eff=1638, cliff=0.469 (above 0.30; predicted HP)

Prediction: PC regime shows cliff between alpha=0.05 and alpha=0.20; WM regime shows cliff between alpha=0.025 and alpha=0.10.

## HYPOTHESIZED landing

**Most likely outcome:** monotonicity CG in >=1 regime with sparsity_range in [0.15, 0.40]; cv < 0.10.

**If flat both regimes:** confirms encoder-invariant sparsity does NOT drive capacity in HRR-real; META_RULE_AO extension of batch A v2 finding (sparsity effect encoder-conditional to fhrr).

## Chunked architecture

- Sibling files: `exp_sparsity_free_axis_v1_seed_{7,13,19}.py`
- Shared core: `experiments/_sparsity_free_axis_v1_core.py`

## PROT / dispatch

- PROT-018: anchor has `_n8192` suffix (single-N)
- PROT-019: `_n8192` requires `--timeout >= 3600s` per FULL seed
- Queue routing: CPU-eligible (numpy + small torch); anchor: `remote_cpu_queue` per seed
- Formula self-test timeout: 120s (`--self-test`)
- Smoke timeout: 300s (SMOKE half-M)
- FULL timeout per seed: 3600s

## Discriminator survives scale (USER 2026-06-26)

- SMOKE at N=8192 (full N)
- SMOKE half-M (PC: 50; WM: K=250)
- SMOKE PC-only regime (6 points) -- verifies PC discriminator visible before dispatching WM
- Preview arm: alpha=0.005 (predicted FLOOR) + alpha=0.20 (predicted HP band); if SMOKE shows range < 0.05 at full N in PC, FULL WILL NOT DISCRIMINATE -> ABORT full dispatch.

## Author

hdi_exp_dev 2026-07-01 (Opus 4.7 1M; agent-spawn; wave-2 §3)
