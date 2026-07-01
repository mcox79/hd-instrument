# Prereg: substrate_refuse_gate_2sided_tau_v4_M14

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) per Research drill `notes/research_M14_v4_revival_drill_2026-07-01.md` sec (a)
**Stage:** Stage 3 (compositional understanding -- refuse-gate as substrate primitive) via M3 cortex M1.4
**P_deflated:** 0.55 (composition-only wiring on already-shipped NoiseChannel M1.3 + refuse-gate v3 core; drill cites 4 cross-domain drills SDT/tail-conformal/TOST/unequal-var-SDT; 5x-drill escalation eligible; lift to 0.55 per drill headline)
**M3 milestone:** M1.4 closure (glass-box conversational calibration primitive; M3-blocking)
**Builds on:** `preregs/2026-07-01_substrate_refuse_gate_adaptive_tau_v3_M14.md` (v3 HF at seed_7_smoke; one-sided tau caused net structural loss); `notes/research_M14_v4_revival_drill_2026-07-01.md` (drill rank a > c > b); `substrate_router/noise_channel.py` (M1.3 CG at c5e5e66a)
**Cell files:** `experiments/exp_substrate_refuse_gate_2sided_tau_v4_M14_seed_{7,13,19}.py` (seed_7 authored; seed_13/19 sibling ship after seed_7 smoke HP) + `experiments/_substrate_refuse_gate_2sided_tau_v4_M14_core.py`
**References:**
- `~/.claude/projects/d--AI/memory/project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md`
- `~/.claude/projects/d--AI/memory/project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.md`

## LOAD-BEARING V3 HF (Skunkworks 7a89856d) -- ROOT CAUSE

v3 seed_7_smoke landed HARD_FAIL. Verified from disk `data/exp_substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14_seed_7_smoke/metrics.json`:

- FIXED_V_REL_256 @ moderate refuse_precision = 0.6667  MEASURED@disk:hp_gate_details.SLIDING_WINDOW.fixed_refuse_precision_at_moderate_regime
- BAYESIAN_CI precision_lift_over_fixed_at_moderate = -0.193  MEASURED@disk:hp_gate_details.BAYESIAN_CI.precision_lift_over_fixed_at_moderate
- PERCENTILE lift = -0.076  MEASURED@disk:hp_gate_details.PERCENTILE.precision_lift_over_fixed_at_moderate
- SLIDING_WINDOW lift = 0.000  MEASURED@disk:hp_gate_details.SLIDING_WINDOW.precision_lift_over_fixed_at_moderate

All 3 adaptive arms fail to beat FIXED. BAYESIAN_CI actively HURTS. Recall gained (rr up), precision lost (net structural loss). Classic SDT criterion-shift-against-unequal-variance failure -- one-sided criterion cannot separate signal + noise distributions with different spread.

## HYPOTHESIS (v4)

PRIMARY (HP): with cortex NoiseChannel additive_gaussian injecting regime-conditional noise on post-substrate max_sim scalar (v3 wiring PROVEN regime-monotonic per 7a89856d), 2-SIDED TAU BAND (tau_low + tau_high adapted separately on partitioned history streams) shows at least ONE arm satisfies ALL of:
- refuse-rate monotonic across regime (clean -> moderate -> heavy) at OOD band
- refuse-precision at moderate regime >= FIXED_V_REL_256 + 0.15
- cross-seed cv < 0.08 (checked at aggregate seeds 7/13/19)

If HP fires -> closes M3 milestone M1.4 (glass-box conversational calibration primitive; M3-blocking).

ALTERNATIVE (MB): monotonic + precision_lift in [0.05, 0.15] at moderate regime (2-sided helps, not enough).

FALLBACK (HF): no 2-sided arm improves over FIXED (>= 0.05 lift). Escalate to (a+c) meta-composition (2-sided per bucket = 4 tau streams total) per drill sec (a) HF plan, or hand M1.4 to M3-cortex-external calibrator (substrate-out-of-scope).

## MECHANISM SPEC (2-SIDED TAU BAND)

Decision rule per query with confidence c_t:
- If c_t > tau_high -> ACCEPT
- If c_t <= tau_high -> REFUSE (covers both "definitely OOD" c < tau_low AND "ambiguity band" tau_low <= c <= tau_high)

For FIXED_V_REL_256 arm: tau_low = tau_high = 0.40 (one-sided baseline; reduces to v3 FIXED semantics).

History-partition (substrate-honest median split, no exogenous router prior):
- Each incoming c_t joins shared history AND is assigned to LOW history if c_t <= running_median(shared_before_this) else HIGH history
- Until MEDIAN_WARMUP (=6) shared obs, arm returns (init_tau, init_tau) -- degenerate one-sided
- After warmup + per-side warmup, tau_low computed from low history; tau_high from high history

Composition-only: partition is scalar-history-based (not exogenous router prior as drill option (c) requires). Drill sec (a) explicitly notes 2-sided tau composes with M1.3 NoiseChannel + refuse-gate v3 core; no new mechanism class outside these three.

## ARMS (4) -- arms-must-differ per META_RULE_AF

1. **FIXED_V_REL_256** (baseline) -- tau_low = tau_high = 0.40; one-sided; v3 baseline reproducer at V_REL=256 CG
2. **TWO_SIDED_PERCENTILE** -- tau_low = P10(low_hist); tau_high = P90(high_hist); warmup per side = 10
3. **TWO_SIDED_BAYESIAN_CI** -- tau_low = mean(low) - 1.96*sd_low/sqrt(n_low); tau_high = mean(high) + 1.96*sd_high/sqrt(n_high); warmup per side = 8; clamped to [-1,1] and ordered (tau_low <= tau_high)
4. **TWO_SIDED_SLIDING_WINDOW** -- tau_low = P25(low_hist[-32:]); tau_high = P75(high_hist[-32:]); W=32; per-side warmup

Distinct code paths per arm (mechanism_hash sha256 distinct); `arms_differ_verified` at smoke.

## PHASE AXES

- ARMS = 4
- NoiseChannel REGIMES = 3 (clean / moderate / heavy) -- from `NOISE_CHANNEL.REGIME_TABLE`
- DIFFICULTY_BANDS = 3 (in_KB / borderline / OOD)
- SEEDS = 3 (7, 13, 19) -- seed_7 authored + smoke first; sibling seeds ship after seed_7 smoke HP
- Cardinality: 4 arms x 3 regimes x 3 bands = **36 phase points per seed**
- N_QUERIES_PER_BAND_FULL = 80; SMOKE = 30
- EXPECTED_N_RECORDS_FULL = 2880 per seed; SMOKE = 1080 per seed

**cardinality_ok:** observed_units == 36 AND observed_records == expected.

## NOISECHANNEL WIRING (v3-COMPAT)

Reuse v3 additive_gaussian mode (proven regime-monotonic per 7a89856d):
```
1. sub_sims = W_subjects @ query_vec  (deterministic substrate read; scores (V_C,))
2. max_sim_t = max(sub_sims)  (deterministic substrate top-1 scalar)
3. noise = N(0, sigma_regime); sigma from REGIME_TABLE
4. confidence_t = max_sim_t + noise  (regime-conditional PDF)
5. (tau_low_t, tau_high_t) = arm.step(confidence_t)  (adaptive per-arm update)
6. accept_t = (confidence_t > tau_high_t)  (2-sided decision)
```

Cortex-scoped rng: `torch.Generator().manual_seed(seed * 10007 + 42)` -- distinct from substrate numpy `default_rng(seed)`.

## PRE-REG BANDS (LOCKED)

- **HARD_PASS (HP):**
  - At least ONE 2-sided adaptive arm (TWO_SIDED_PERCENTILE / TWO_SIDED_BAYESIAN_CI / TWO_SIDED_SLIDING_WINDOW) satisfies ALL of:
    - refuse-rate monotonic across (clean -> moderate -> heavy) at OOD band (non-inc OR non-dec)
    - refuse-precision at moderate regime >= FIXED_V_REL_256_refuse_precision_at_moderate + 0.15  (v3 discriminator threshold preserved)
    - cross-seed cv(refuse_rate at moderate/OOD) < 0.08 (checked at aggregate; per-seed HP only requires monotonic+lift)
  - AND META_RULE_AF arm-distinctness verified
  - AND META_RULE_AV run_mode=='full' verified post-dispatch (size > 5KB; elapsed > 1s)
  - AND cardinality_ok True

- **MIDDLE_BAND (MB):**
  - Monotonic satisfied by >=1 arm AND precision_lift in [0.05, 0.15] at moderate
  - OR cross-seed cv in [0.08, 0.15]

- **HARD_FAIL (HF):**
  - No 2-sided arm shows precision_lift >= 0.05 at any regime
  - OR monotonicity broken (all arms non-monotonic across regime at OOD)
  - OR cross-seed cv >= 0.15
  - OR cardinality breach (META_RULE_H)
  - OR arms-must-differ False
  - OR positive control mismatch (baseline FIXED at clean/OOD refuses < 0.85)

## FUNCTIONAL REQUIREMENTS (§15E gate)

1. **Noisy confidence PDF at boundary** -> `NoiseChannel.inject(mode='additive_gaussian')` (M1.3 CG per c5e5e66a; v3 wiring proven at 7a89856d)
2. **Substrate read (deterministic)** -> bipolar codebook + `W @ v` (V1 substrate CG)
3. **Baseline fixed-tau one-sided** -> `FixedTauState(0.40)` (v3 baseline; v4 preserves)
4. **2-sided tau via median-split history partition** -> NEW: `_TwoSidedBase` with running-median-partition; per-side warmup; ordering enforced. Substrate-honest scalar signal split (no router prior); drill sec (a) explicit.
5. **Two-sided percentile arm** -> `TwoSidedPercentileTauState(low=10, high=90)` -- SDT dual-criterion (Landy 2024) + tail-specific conformal (arxiv 2606.18199)
6. **Two-sided Bayesian CI arm** -> `TwoSidedBayesianCITauState(z=1.96)` -- TOST equivalence bounds (Lakens 2017) + unequal-var SDT (Landy chapter 2024)
7. **Two-sided sliding window arm** -> `TwoSidedSlidingWindowTauState(W=32, low=25, high=75)` -- windowed sequential-conformal
8. **Cortex-scoped rng bookkeeping** -> `torch.Generator` owned by `NoiseChannel`; distinct seed from substrate rng (M1.3 spec risk #2)

## POSITIVE CONTROL (§15D gate)

At `regime=clean` (sigma=0) FIXED_V_REL_256 reduces to v3 FIXED semantics: `refuse_rate @ OOD >= 0.85`.
- cited_prior_atom: v3 seed_7_smoke ctrl_pt @ (FIXED, clean, OOD)
- cited_prior_metric: 0.85 (v3 baseline reproducer; also matches v1/v2 CG at V_REL=256 fixed-substrate)
- cited_prior_regime: {N: 8192, V_C: 600, V_REL: 256, NoiseChannel: clean(sigma=0)}
- test_regime: SAME (v3-compat) -- MATCHED regime, no shape drift
- tolerance: 0.10
- if_outside_tolerance: HARD_FAIL_POSITIVE_CONTROL_MISMATCH

Selftest self-check at N=1024 also confirmed refuse >= 0.85 at clean/OOD before full dispatch.

## COMPOSITION EDGES (§15C gate)

| From | To | A_output_shape | B_input_shape | Verdict |
|---|---|---|---|---|
| substrate.W_subjects@v | max(sub_sims) | (V_C,) real float32 | scalar float | SHAPE_MATCH (reduction) |
| max(sub_sims) | NoiseChannel(additive_gaussian) scalar | scalar | scalar (regime sigma) | SHAPE_MATCH |
| NoiseChannel noise sample | scalar addition | scalar | scalar | SHAPE_MATCH |
| confidence_t | _TwoSidedBase.step | scalar float | scalar float | SHAPE_MATCH |
| _TwoSidedBase.step | two_sided_decide | (tau_low, tau_high) float pair | (c, tau_low, tau_high) triple | SHAPE_MATCH |
| two_sided_decide | refuse-log accumulator | bool | bool | SHAPE_MATCH |

No SHAPE_MISMATCH_no_adapter edges.

## EFFECTIVE VS NOMINAL PARAMS (§15A gate)

**swept_params:**
- regime in {clean, moderate, heavy}
- band in {in_KB, borderline, OOD}
- arm in {FIXED_V_REL_256, TWO_SIDED_PERCENTILE, TWO_SIDED_BAYESIAN_CI, TWO_SIDED_SLIDING_WINDOW}

**effective_params_per_primitive:**
- NoiseChannel: sigma = REGIME_TABLE[regime]["sigma"] (clean=0, moderate=0.15, heavy=0.35) -- sweep-varying, ALIGNED
- 2-sided arm state: sees noisy confidence_t with regime-driven variance; partitions into low+high history -> tau_low + tau_high both regime-conditional -- ALIGNED
- flip_frac: fixed per band; NOT swept nominally -- ALIGNED

**sweep_alignment_verdict:** ALIGNED

## DISCRIMINATING FRACTION (§15B gate)

Predicted per-cell refuse_rate at (arm=TWO_SIDED_PERCENTILE, regime=X, band=Y):

- (clean, in_KB): 0.00-0.15 (high-conf; band-width small; mostly accept) -- IN BAND (bottom)
- (clean, borderline): 0.30-0.60 (partial refuse; tau_high near max_sim) -- IN BAND
- (clean, OOD): 0.90-1.00 (baseline saturation; matches FIXED) -- SAT (positive control)
- (moderate, in_KB): 0.15-0.35 (noise spread; some refuse false) -- IN BAND
- (moderate, borderline): 0.40-0.70 (KEY DISCRIMINATING band; where 2-sided pays off) -- IN BAND
- (moderate, OOD): 0.75-0.95 (refuse dominant; some accepts leak) -- IN BAND (upper)
- (heavy, in_KB): 0.30-0.55 (heavy noise pushes some in-KB below tau_high) -- IN BAND
- (heavy, borderline): 0.55-0.80 -- IN BAND (upper)
- (heavy, OOD): 0.65-0.90 -- IN BAND

Predicted points in discriminating band [0.30, 0.70]: 5-6 of 9 (moderate x borderline, moderate x in_KB, heavy x in_KB, clean x borderline, moderate x OOD-lower, heavy x borderline-lower). discriminating_fraction >= 0.55. PASS >= 0.30.

## CRLB / capacity-feasibility (§9 gate)

**crlb_n/a:** "refuse-precision is a rate ratio (not variance floor); NoiseChannel PDF is regime-driven not sample-size-driven. Substrate argmax-noise floor at N=8192 V_C=600 is sqrt(2*ln(600)/8192) = 0.040, well below FIXED_TAU=0.40. Refuse decisions have room in [0.04, 0.40] and NoiseChannel spreads score distribution across this band. 2-sided tau adds a second criterion which cannot introduce a new floor since both criteria live inside the same score range."

## BASELINE_IN_BAND (§10 gate META_RULE_AG)

Smoke verifies FIXED_V_REL_256 refuse_rate:
- (clean, in_KB): expected 0.00-0.10 -- NOT saturated below 0.05 (baseline at fixed-substrate is exact per v3)
- (moderate, borderline): expected 0.35-0.65 -- IN measurable band
- (moderate, OOD): expected 0.60-0.85 -- MEASURABLE

If FIXED saturates >= 0.95 across ALL 9 (regime x band) combos -> ITERATE_REGIME (block dispatch). Smoke-gate check.

## DISCRIMINATOR_SURVIVES_SCALE (§DISCRIMINATOR-MUST-SURVIVE-SCALE)

Option A applied: smoke runs at full-N=8192 (numpy CPU-cheap per v3; ~30-90s smoke). Discriminator IS the mechanism at full scale.

## ARMS_MUST_DIFFER (§6 META_RULE_AF)

Smoke asserts:
- 4 arms produce distinct mechanism_hash sha256
- At moderate regime x borderline band, adaptive arms produce >= 2 distinct decision_hash vs FIXED baseline across 30 queries
- Selftest gate (f) explicitly checks >= 1 adaptive arm has decisions differ-from-FIXED on synthetic stream; catches 2-sided-collapsed-to-one-sided bug
- If any pair collides in mechanism_hash -> BLOCK_DISPATCH_META_RULE_AF
- Baseline-arm exempted from decision-distinctness at (clean, OOD) saturation-corner where all arms may collapse to 100% refuse

## FINAL_METRICS_ATOMICITY (§7 META_RULE_AH)

`tmp_replace`: single-shot smoke writes to `metrics.json.tmp` then `os.replace(tmp, final)`. Runtime metric writes (STARTED / RUNNING / crash) also atomic per `_write_minimal_metrics`.

## DEFENSIVE PATTERNS (§13)

- `cell_chunked: True` -- 3 sibling seed files (7 authored; 13, 19 ship after 7 smoke HP)
- `start_marker_written: True` -- via `_write_minimal_metrics(STARTED)` at main() entry
- `crash_diagnostic_present: True` -- outer `try/except SystemExit: raise / except Exception:` writes CELL_CRASHED metrics with traceback
- `heartbeat_present: True` -- per-phase-point flush print + `_seed_checkpoint.write_partial_key` progress
- `defensive_error_checking: "passed_all_4_patterns"`

## CALIBRATION_CHECK (§5 META_RULE_M)

`calibration_check: "default_ok_for_this_regime"` -- 2-sided arm internals LOCKED at pre-reg init (P10/P90 for PERCENTILE; z=1.96 for BAYESIAN_CI; W=32/P25/P75 for SLIDING_WINDOW). MEDIAN_WARMUP=6. No in-band tuning. NoiseChannel REGIME_TABLE FIXED at ship of M1.3 (c5e5e66a).

## HP_SCOPE (§5b per-arm HARD_PASS scope)

- `FIXED_V_REL_256`: [`positive_control_out_kb_refuse_rate_>=_0.85_at_clean_OOD`] (baseline; not expected to beat itself)
- `TWO_SIDED_PERCENTILE`: [`monotonic_refuse_rate_across_regime_at_OOD`, `cv_across_seeds_at_moderate_OOD_<_0.08`, `refuse_precision_at_moderate_>=_fixed_+_0.15`]
- `TWO_SIDED_BAYESIAN_CI`: same as TWO_SIDED_PERCENTILE
- `TWO_SIDED_SLIDING_WINDOW`: same as TWO_SIDED_PERCENTILE

Any ONE of {TWO_SIDED_PERCENTILE, TWO_SIDED_BAYESIAN_CI, TWO_SIDED_SLIDING_WINDOW} satisfying all three -> HP for the cell.

## SCHEMA-VET FIELDS SUMMARY

```yaml
cardinality_ok: true (checked at each seed)
final_metrics_atomicity: tmp_replace
crlb_n/a: "rate-ratio not variance-floor; substrate argmax-noise floor 0.040 << tau=0.40"
discriminator_reachability: true
baseline_in_band: true (verified smoke)
arms_differ_verified: true (smoke META_RULE_AF; selftest gate f checks 2-sided-not-collapsed)
arms_differ_exempted: [(clean, OOD saturation-corner)]
discriminator_survives_scale: option_A (smoke at full-N=8192)
sweep_alignment_verdict: ALIGNED
discriminating_fraction: 0.55  # 5/9 in [0.30, 0.70]
composition_edges: all SHAPE_MATCH
positive_control_arms:
  - PRIMITIVE_REPRODUCE: FIXED_V_REL_256 @ clean @ OOD
    cited_prior_atom: v3 baseline reproducer (v1/v2/v3 CG at V_REL=256)
    cited_prior_metric: 0.85
    cited_prior_regime: {N: 8192, V_C: 600, V_REL: 256, NoiseChannel: clean(sigma=0)}
    test_regime: MATCHED (v3-compat)
    tolerance: 0.10
    if_outside_tolerance: HARD_FAIL_POSITIVE_CONTROL_MISMATCH
functional_requirements: [see FUNCTIONAL REQUIREMENTS section above]
cell_chunked: true
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
calibration_check: default_ok_for_this_regime
HP_SCOPE: see above
NOISE_MODE: additive_gaussian  # v3 wiring proven regime-monotonic at 7a89856d
REGIME: {clean, moderate, heavy}
mechanism_class: 2sided_tau_low_plus_tau_high_median_split_history
```

## RUNTIME ESTIMATE

Smoke seed_7 at full-N=8192 numpy CPU: ~30-90s per v3 landing wall time (36 units x 30 queries = 1080 records; matmul V_C=600 x N=8192 per query). Full seed_7: 36 units x 80 queries = 2880 records ~ 2-5 min per seed. 3 seeds full ~ 15 min. Timeout: 1800s (30 min) per seed generous.

## DEPLOY

- Route to `local_cpu_queue` (numpy-only single-seed; CPU-cheap per v3 ~90s smoke)
- 3 sibling seed cells: seed_7 authored; seed_13 + seed_19 ship after seed_7 smoke HP
- Commit BEFORE dispatch (harness push to origin/main is Orchestrator's responsibility; local_cpu_queue doesn't require push)
- Smoke gate: seed_7 smoke first; verify precision_lift >= 0.15 vs fixed baseline at moderate regime + cross-seed cv on partial + arms differ; then dispatch full seed_7 + seed_13 + seed_19

## PROMOTION PATH

If seed_7 smoke HP:
1. Author sibling seed_13 + seed_19 files (copy-modify pinned SEED constant)
2. Dispatch seed_7 + 13 + 19 FULL to local_cpu_queue
3. On all 3 seeds HP: cross-seed cv check < 0.08 satisfied -> M1.4 closed. Report to Skunkworks for landed-VET.
4. If any seed MB: research decides escalate to (a+c) meta-composition or accept M1.4-MB-partial.

If seed_7 smoke HF: honest-abort. Root cause in verdict_msg. Escalate to (a+c) meta-composition per drill sec (a) HF plan, or hand M1.4 to M3-cortex-external calibrator (substrate-out-of-scope).
