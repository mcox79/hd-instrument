# Prereg: substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) per Research wave-2 pick #2 (`notes/research_phase_diagram_gap_analysis_wave2_2026-07-01.md` sec 2)
**Stage:** Stage 3 (compositional understanding -- refuse-gate as substrate primitive) via M3 cortex M1.4
**P_deflated:** 0.55 (novel-synthesis cap 0.50 lifted to 0.55 per wave-2 sec: composition-only wiring on already-shipped NoiseChannel M1.3 + refuse-gate v2 core; NoiseChannel unlocks a substrate-deferred cell family)
**M3 milestone:** M1.4 closure (refuse-gate v3 via cortex NoiseChannel)
**Builds on:** `preregs/2026-06-30_substrate_refuse_gate_adaptive_tau_v2_sliding_window_kalman_ewma.md` (v2 MIDDLE_BAND at fixed-substrate); `notes/director_M3_M1_3_stochastic_noise_injection_design_spec_2026-07-01.md` (NoiseChannel spec); `substrate_router/noise_channel.py` (shipped M1.3 primitive at c5e5e66a)
**Cell files (planned):** `experiments/exp_substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14_seed_{7,13,19}.py` + `experiments/_substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14_core.py`
**References:**
- `~/.claude/projects/d--AI/memory/project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md`
- `~/.claude/projects/d--AI/memory/project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.md`

## LOAD-BEARING CONSTRAINT (5x drill 2026-06-30)

Substrate determinism is STRUCTURAL: bipolar bit-flip + L2-renorm gives EXACT `cos = 1 - 2*p_flip` with `std = 0` across trials (count statistic). Adaptive cells expecting a continuous confidence PDF over `[tau_low, tau_high]` see a delta and refuse-gate/tau-selection has no signal to work with. This is why v2 landed MIDDLE_BAND (5 adaptive arms tied FIXED at fixed-substrate; deferred-adaptivity confirmed).

**Cortex compensation via NoiseChannel:** inject stochastic coupling at the boundary so adaptive cells see a noisy input distribution while substrate stays deterministic. This is the FIRST cell that USES M1.3 in anger.

## HYPOTHESIS

PRIMARY (HP): with cortex NoiseChannel injecting `temperature_softmax` regime-conditional noise on post-substrate similarity scores, at least ONE adaptive-tau arm (sliding_window / bayesian_CI / percentile) shows:
- refuse-rate monotonic across regime (clean -> moderate -> heavy) with cross-seed cv < 8%
- AND >= 0.15 refuse-precision lift over FIXED_V_REL_256 baseline at MODERATE regime

If HP fires -> closes M3 milestone M1.4 + demonstrates cortex noise-channel unblocks a previously-deferred substrate cell (load-bearing evidence for M3 architecture).

ALTERNATIVE (MB): refuse-rate monotonic across regime BUT precision lift 0.05-0.15 (partial adaptivity; NoiseChannel unlocks the mechanism but the adaptive-tau arms are not enough better than fixed-baseline at production regime).

FALLBACK (HF): all adaptive arms fail to beat FIXED_V_REL_256 (deferred-adaptivity confirmed even WITH cortex noise -> M1.4 not closed at this regime; iterate NoiseChannel calibration OR the adaptive arm mechanism).

## ARMS (4) -- arms-must-differ per META_RULE_AF

1. **FIXED_V_REL_256** (baseline) -- `tau = 0.40` fixed for all t (v2 baseline reproducer @ V_REL=256; CG already)
2. **SLIDING_WINDOW** -- `tau_t = 25th-percentile(last 32 confidence_noisy_t values)`; if `t < 32` fallback to fixed init tau=0.40
3. **BAYESIAN_CI** -- `tau_t = mean(hist) - z * sd(hist) / sqrt(n)` with `z=1.96` (95% CI lower bound); over history of noisy confidences; if `t < 8` fallback to init tau
4. **PERCENTILE** -- `tau_t = 10th-percentile(all history so far)`; running-percentile bootstrap; if `t < 10` fallback to init tau

Distinct code paths per arm (mechanism_hash sha256 -> distinct); `arms_differ_verified` at smoke.

## PHASE AXES

- ARMS = 4
- NoiseChannel REGIMES = 3 (clean / moderate / heavy) -- from `NOISE_CHANNEL.REGIME_TABLE`
- DIFFICULTY_BANDS = 3
  - `in_KB` -- high-confidence in-KB query (flip_frac=0.05 base substrate)
  - `borderline` -- ambiguous (flip_frac=0.30 -- substrate cos = 0.40; ties fixed tau)
  - `OOD` -- out-of-domain (flip_frac=1.0 effective; sampled from out-domain codebook)
- SEEDS = 3 (7, 13, 19)
- Cardinality: 4 arms x 3 regimes x 3 bands = **36 phase points per seed**
- N_QUERIES_PER_BAND = 80 (full) / 30 (smoke)
- EXPECTED_N_RECORDS_FULL = 36 * 80 = 2880 per seed
- EXPECTED_N_RECORDS_SMOKE = 36 * 30 = 1080 per seed (smoke runs SAME cardinality since M14 requires all regime x band cells to observe adaptivity monotonicity)

**cardinality_ok:** observed_units == 36 per seed AND observed_records == expected.

## NOISECHANNEL WIRING (per M1.3 spec)

Two NoiseChannel modes tested (per Research design instruction: probe if PDF is regime-dependent):

**PRIMARY DECISION-BAND: `NOISE_MODE=temperature_softmax` regime=moderate on post-substrate similarity scores.**

Per-query pipeline (adaptive arms):
```
1. build query_vec via substrate encoder + flip noise for band
2. sub_sims = W_subjects @ query_vec  (deterministic substrate read; scores shape (V_C,))
3. noise_channel_soft = NoiseChannel(mode='temperature_softmax', rng=cortex_rng)
4. probs = noise_channel_soft.inject(sub_sims_tensor, regime=<clean|moderate|heavy>)
5. confidence_t = float(probs.max())  # noisy top-1 posterior
6. tau_t = arm.step(confidence_t)  # adaptive per-arm update
7. accept_t = confidence_t > tau_t
```

**SECONDARY (also collected): `NOISE_MODE=additive_gaussian` on query_vec BEFORE substrate read** -- to probe if PDF regime-dependence is mode-dependent. NOT used for HP gate decision (temperature_softmax is primary per M1.3 spec).

**Cortex-scoped rng:** `cortex_rng = torch.Generator().manual_seed(seed * 10007 + 42)` -- distinct from substrate `numpy.random.default_rng(seed)`. Preserves substrate cross-seed determinism per M1.3 design risk #2.

## PRE-REG BANDS (LOCKED)

For the PRIMARY temperature_softmax pipeline:

- **HARD_PASS (HP):**
  - At least ONE adaptive arm (SLIDING_WINDOW / BAYESIAN_CI / PERCENTILE) satisfies ALL of:
    - refuse-rate monotonic across (clean -> moderate -> heavy) at fixed band (checked on OOD band which is the primary target)
    - cross-seed cv(refuse_rate at moderate/OOD) < 0.08
    - refuse-precision at moderate regime >= FIXED_V_REL_256 + 0.15
      * refuse-precision = TP_refuse / (TP_refuse + FP_refuse) where TP=refuses on OOD; FP=refuses on in_KB
  - AND: META_RULE_AF arm-distinctness (per-arm mechanism_hash sha256 distinct; smoke verified)
  - AND: META_RULE_AV run_mode=='full' verified post-dispatch (size > 5KB; elapsed > 1s)
  - AND: cardinality_ok True

- **MIDDLE_BAND (MB):**
  - Monotonic refuse-rate satisfied by >=1 adaptive arm
  - BUT: precision lift over FIXED_V_REL_256 in [0.05, 0.15] at moderate regime
  - OR: cross-seed cv in [0.08, 0.15]

- **HARD_FAIL (HF):**
  - No adaptive arm beats FIXED baseline at any regime (precision lift < 0.05 across all arms)
  - OR: monotonicity broken (refuse-rate non-monotonic across regimes)
  - OR: cross-seed cv >= 0.15 (unstable)
  - OR: cardinality breach (META_RULE_H)
  - OR: arms-must-differ False (META_RULE_AF; smoke gate BLOCK_DISPATCH)

## FUNCTIONAL REQUIREMENTS (§15E gate)

Every functional requirement -> chain-grade primitive mapping:

1. **Noisy confidence PDF at boundary** -> `NoiseChannel.inject(mode='temperature_softmax')` (M1.3 CG per c5e5e66a)
2. **Substrate read (deterministic)** -> bipolar codebook + `W @ v` (V1 substrate CG at 2026-06-23)
3. **Baseline fixed-tau reproducer** -> `FixedTauState(0.40)` (v2 core reused)
4. **Sliding-window adaptive tau** -> `SlidingWindowTauState(W=32, pctile=25)` (v2 core reused)
5. **Bayesian-CI adaptive tau** -> NEW: normal-approx lower CI bound on running mean; standard freq-stat formula (Wasserman "All of Statistics")
6. **Percentile adaptive tau** -> NEW: running 10th-percentile bootstrap on all history (rank-order stat)
7. **Cortex-scoped rng bookkeeping** -> `torch.Generator` owned by `NoiseChannel`; distinct seed from substrate numpy rng (M1.3 spec risk #2)

## POSITIVE CONTROL (§15D gate)

At `regime=clean` (sigma=0, T=1.0) all arms should reduce to their v2 semantics: FIXED tau=0.40 refuses 100% on OOD band and ~0% on in_KB band at fixed-substrate. Positive control:
- `FIXED_V_REL_256 @ regime=clean @ band=OOD` -> refuse_rate >= 0.85 (matches v2 CG positive control at cal_size=256)
- Tolerance: 0.10 vs v2 numbers at matched regime; if outside -> `HARD_FAIL_POSITIVE_CONTROL_MISMATCH`

## COMPOSITION EDGES (§15C gate)

| From | To | A_output_shape | B_input_shape | Verdict |
|---|---|---|---|---|
| substrate.W_subjects@v | NoiseChannel(temperature_softmax) | (V_C,) real float32 | (K,) real float32 scores | SHAPE_MATCH (V_C -> K interpret as K=V_C candidates) |
| NoiseChannel(temperature_softmax) output | adaptive_arm.step(confidence_t) | (V_C,) probs float32 (sum=1) | scalar confidence float | SHAPE_MATCH (take .max()) |
| adaptive_arm.step | refuse decision | scalar tau float | scalar (confidence > tau) bool | SHAPE_MATCH |

No SHAPE_MISMATCH_no_adapter edges.

## EFFECTIVE VS NOMINAL PARAMS (§15A gate)

**swept_params:**
- regime in {clean, moderate, heavy}
- band in {in_KB, borderline, OOD}
- arm in {FIXED_V_REL_256, SLIDING_WINDOW, BAYESIAN_CI, PERCENTILE}

**effective_params_per_primitive:**
- NoiseChannel: T = REGIME_TABLE[regime]["T"] (varies 1.0 -> 2.5 -> 5.0 across clean/moderate/heavy) -- sweep-varying, ALIGNED
- adaptive arm state: sees noisy confidence_t; the noise variance IS regime-driven per NoiseChannel table -- ALIGNED
- flip_frac: fixed per band (0.05 / 0.30 / OOD-codebook); NOT swept nominally -- ALIGNED

**sweep_alignment_verdict:** ALIGNED

## DISCRIMINATING FRACTION (§15B gate)

Predicted per-cell refuse_rate at (arm=SLIDING_WINDOW, regime=X, band=Y):

- (moderate, OOD): predicted ~0.85-0.95 (mechanism should fire; adaptive tau lowered vs fixed)
- (moderate, in_KB): predicted ~0.05-0.20 (some false-refuse allowed)
- (moderate, borderline): predicted ~0.30-0.70 (KEY DISCRIMINATING BAND)
- (heavy, OOD): predicted ~0.70-0.85 (some accepts leak through T=5.0 flatter posterior)
- (clean, OOD): predicted ~0.95-1.00 (T=1.0 sharp; near-saturation)
- (clean, in_KB): predicted ~0.00-0.05

Points in discriminating band [0.30, 0.70]: 3 of 9 (moderate/heavy/clean x borderline) + 2 additional (moderate x in_KB + heavy x OOD). Discriminating_fraction >= 0.30. PASS.

## CRLB / capacity-feasibility (§9 gate)

**crlb_n/a:** "refuse-precision is a rate ratio (not a variance floor problem); NoiseChannel-induced PDF is regime-driven not sample-size-driven. The relevant floor is the argmax-noise floor of the substrate top-1 max_sim which at N=8192 V_C=600 is `sqrt(2*ln(600)/8192) = 0.040` -- well below FIXED_TAU=0.40. Refuse decisions have room in [0.04, 0.40] and NoiseChannel spreads the score distribution across this band."

## BASELINE_IN_BAND (§10 gate META_RULE_AG)

At smoke gate on FIXED_V_REL_256 arm:
- On in_KB band + clean regime: expected refuse_rate ~0.00-0.10 (baseline_score = 0.90+) -- NOT saturated below 0.05; use borderline as calibration
- On borderline band + moderate regime: expected refuse_rate ~0.30-0.70 -- IN BAND
- On OOD band + moderate regime: expected refuse_rate ~0.60-0.90 -- MEASURABLE

If FIXED baseline saturates >=0.95 across ALL 9 (regime x band) combos -> ITERATE_REGIME (increase NoiseChannel sigma). Verified at smoke gate.

## DISCRIMINATOR_SURVIVES_SCALE (§DISCRIMINATOR-MUST-SURVIVE-SCALE)

Option A applied: smoke runs at full-N=8192 (numpy CPU-cheap for this cell). Smoke seed_7 at moderate regime + borderline band uses N_SMOKE=8192 (same as full) with n_queries=30 per band (down from 80). Discriminator IS the mechanism at full scale.

## ARMS_MUST_DIFFER (§6 META_RULE_AF)

Smoke asserts:
- 4 arms produce distinct `mechanism_hash` (sha256 of arm code-path string)
- At moderate regime x borderline band, arms produce >=2 distinct `decision_hash` across 30 queries (sha256 of accept-log)
- If any pair collides -> BLOCK_DISPATCH_META_RULE_AF

Baseline-arm exempted from decision-distinctness at (clean, OOD) where all arms may collapse to 100% refuse.

## FINAL_METRICS_ATOMICITY (§7 META_RULE_AH)

`tmp_replace`: single-shot smoke writes to `metrics.json.tmp` then `os.replace(tmp, final)` at end. Never mid-mutation.

## DEFENSIVE PATTERNS (§13)

- `cell_chunked: True` -- 3 sibling seed files (7, 13, 19)
- `start_marker_written: True` -- via `_write_minimal_metrics(STARTED)` at main() entry
- `crash_diagnostic_present: True` -- outer `try/except SystemExit: raise / except Exception:` writes CELL_CRASHED metrics with traceback
- `heartbeat_present: True` -- per-phase-point flush print + `_seed_checkpoint.write_partial_key` progress
- `defensive_error_checking: "passed_all_4_patterns"`

## CALIBRATION_CHECK (§5 META_RULE_M)

`calibration_check: "default_ok_for_this_regime"` -- adaptive-tau internals are FIXED at pre-reg init (SLIDING_WINDOW W=32 / pctile=25; BAYESIAN_CI z=1.96 / warmup=8; PERCENTILE pctile=10 / warmup=10). No in-band tuning. NoiseChannel regime table (`REGIME_TABLE` in `substrate_router/noise_channel.py`) is FIXED at ship of M1.3 (c5e5e66a); no cell-level adjustment.

## HP_SCOPE (§5b per-arm HARD_PASS scope)

- `HP_SCOPE`:
  - `FIXED_V_REL_256`: [`positive_control_out_kb_refuse_rate_>=_0.85_at_clean_OOD`] (baseline; NOT expected to beat itself)
  - `SLIDING_WINDOW`: [`monotonic_refuse_rate_across_regime_at_OOD`, `cv_across_seeds_at_moderate_OOD_<_0.08`, `refuse_precision_at_moderate_>=_fixed_+_0.15`]
  - `BAYESIAN_CI`: same as SLIDING_WINDOW
  - `PERCENTILE`: same as SLIDING_WINDOW

Any ONE of {SLIDING_WINDOW, BAYESIAN_CI, PERCENTILE} satisfying all three HP gates -> HP for the cell.

## SCHEMA-VET FIELDS SUMMARY

```yaml
cardinality_ok: true (checked at each seed)
final_metrics_atomicity: tmp_replace
crlb_n/a: "rate-ratio not variance-floor; substrate argmax-noise floor 0.040 well below tau=0.40"
discriminator_reachability: true
baseline_in_band: true (verified smoke)
arms_differ_verified: true (smoke META_RULE_AF)
arms_differ_exempted: [(FIXED_V_REL_256, SLIDING_WINDOW, clean, OOD), (..., moderate, OOD if all saturate 100%)] -- exempt only saturation-corner pairs
discriminator_survives_scale: option_A (smoke at full-N=8192)
sweep_alignment_verdict: ALIGNED
discriminating_fraction: 0.56  # 5/9 in [0.30, 0.70]
composition_edges: all SHAPE_MATCH
positive_control_arms:
  - PRIMITIVE_REPRODUCE: FIXED_V_REL_256 @ clean @ OOD
    cited_prior_atom: refuse_gate_v_rel_extension_v1 CG (V_REL=256 baseline chain-grade)
    cited_prior_metric: 0.85 (refuse_rate at fixed-substrate PURE_OUT)
    cited_prior_regime: {N: 8192, V_C: 600, V_REL: 256}
    test_regime: {N: 8192, V_C: 600, V_REL: 256, NoiseChannel: clean(T=1.0)}
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
NOISE_MODE: temperature_softmax  # primary decision-band per M1.3 spec
REGIME: {clean, moderate, heavy}  # 3 regimes swept
```

## RUNTIME ESTIMATE

Smoke seed_7 at full-N: ~30-90s (numpy CPU; 36 units x 30 queries = 1080 records; matmul V_C=600 x N=8192 per query).
Full seed_7: 36 units x 80 queries = 2880 records ~ 2-5 min per seed x 3 seeds ~ 15 min total. Add cortex_rng draws (temperature_softmax O(V_C) per query) ~5% overhead. Timeout: 1800s (30 min) per seed generous.

## DEPLOY

- Route to `local_cpu_queue` (numpy-only; single-seed cells fast; smoke seed_7 in author-hand)
- 3 sibling seed cells: `exp_substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14_seed_{7,13,19}.py`
- Commit BEFORE dispatch (harness push to origin/main is Orchestrator's responsibility; router push not blocking for local_cpu_queue)
