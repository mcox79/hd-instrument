# Pre-registration: refuse_gate_V_REL_sweep_v1

**Date:** 2026-07-01
**Anchor:** refuse_gate_V_REL_sweep_v1
**Script:** experiments/exp_refuse_gate_V_REL_sweep_v1.py
**Queue:** overnight_queue (numpy; laptop is USER's; per SMOKE-ONLY-local rule 2026-07-01)
**Seeds:** [11, 13, 19] (cross-cell consistent with v_rel_extension_v1)
**V_REL_SWEEP (full):** [64, 128, 256, 512, 1024]
**REGIMES:** [clean, moderate, heavy] (M1.3 REGIME_TABLE p_flip=0.00/0.08/0.20)
**EXPECTED_N_UNITS:** 45 (3 seeds x 5 V_REL x 3 regimes)

## Substrate-KB prior-work check (USER-locked 2026-07-01)

`bash tools/substrate_query.sh "refuse gate V_REL sweep calibration threshold sensitivity"`
returns rank-5 hit at cosine=0.30: `preregs/2026-06-25_substrate_refuse_gate_v_rel_extension_v1.md`
(chunk_prereg). On-disk verify: `exp_substrate_refuse_gate_v_rel_extension_v1` HARD_PASS 2026-06-26.

**Novelty vs prior:** prior cell had 1-axis (V_REL only) at fixed flip_frac=0.10.
Reported `RELATION_CHECK saturated at 1.000 refuse rate across ALL V_REL=[8..512]`
with Q-DISCIPLINE flag. This cell adds the noise-regime axis to break saturation
and characterize the (V_REL x regime) calibration surface. Also extends V_REL frontier
to 1024 (prior stopped at 512). This is a NEW discriminator, not a rediscovery.

## Promotion context (USER 2026-07-01)

Fixed V_REL=256 refuse-gate is CG. USER directive: sweep V_REL to characterize
the calibration surface. V_REL choice may or may not matter across regimes.
Monotonic sensitivity vs regime is the discriminator.

## Design (cell-author owns)

- Reuse audit primitives from v_rel_extension_v1 (identical subject/relation THRs)
- Add regime axis via numpy-native `apply_stochastic_flip` (mirrors M1.3
  NoiseChannel.bernoulli_flip_stochastic; cortex-boundary noise; stochastic
  count statistic, NOT v1's deterministic count)
- V_REL sweep = [64, 128, 256, 512, 1024]; regimes = [clean, moderate, heavy]
- Same NEAR-DOMAIN-MIXED 3-category discriminator (PURE_IN / PURE_OUT / NEAR)
- Two arms: ARM_AUDIT_RELATION_CHECK (CG mechanism), ARM_AUDIT_NAIVE_ALONE (baseline)
  (dropped v_rel_extension_v1's third arm INTENT_PLUS for surface cleanliness;
  RELATION_CHECK is the reported CG arm)

## Pre-registered bands (LOCKED at module init via assert)

**Signal: NEAR rel_sim_mean (continuous audit similarity), NOT refuse_rate.**
Refuse rates saturate at THR=0.40 given V_REL ranges + N=8192 (leak floor
stays below 0.10 << THR); continuous rel_sim IS the calibration surface.

**Physics calibration:** leak floor scales as `sqrt(2*log(V_REL)/N)`.
- V_REL=64,  N=8192: leak = 0.032
- V_REL=1024,N=8192: leak = 0.041
- Theoretical delta = 0.009 (regime-independent for random out-atom distractors)
- Empirical delta ~1.5-2.5x theoretical due to distractor noise mixing

### HARD_PASS_CALIBRATION_UNIFORM
- rel_sim monotonic under ALL 3 regimes (clean/moderate/heavy)
- AND per-regime spread >= **0.008** at each regime
- AND max_spread - min_spread <= **0.02** (regime-invariant)
- AND cv_relsim <= **0.05** at each cell
- AND sanity rails hold
- Meaning: V_REL is a calibration knob; magnitude regime-independent

### HARD_PASS_CALIBRATION_MONOTONIC
- rel_sim monotonic under ALL 3 regimes
- AND per-regime spread >= **0.008** at each regime
- BUT spread differs by > 0.02 across regimes (regime-dependent magnitude)
- Meaning: V_REL matters + regime interacts with magnitude

### MIDDLE_BAND_PARTIAL_SENSITIVITY
- rel_sim monotonic under all regimes
- AND max spread in [**0.004**, **0.008**)
- Weak calibration; V_REL delta below HP floor but above noise

### MIDDLE_BAND_NO_V_REL_SENSITIVITY
- Any regime max_spread < **0.004**
- Honest answer: V_REL doesn't calibrate at these ranges

### HARD_FAIL_NON_MONOTONIC
- rel_sim NOT monotonic under some regime (physics violation)

### HARD_FAIL_SANITY_RAIL
- PURE_IN answer < 0.85 at clean OR moderate (substrate broken)
- OR PURE_OUT refuse < 0.85 at ANY regime
- OR HP_CV_MAX breach on rel_sim across seeds

### HARD_FAIL_CARDINALITY_BREACH
- observed n_units < 45 (some unit failed silently)

## Q-DISCIPLINE guard (BIAS-Q)

If ARM_AUDIT_RELATION_CHECK NEAR near_refuse == 1.000 at ALL (V_REL, regime) cells:
- Verdict carries [Q-DISCIPLINE: saturation at all cells]
- Recommend regime shift (add catastrophic p=0.40) OR THR adjustment

## Discriminator-must-survive-scale (USER 2026-06-26)

**Analytical scale justification (option B):**
- Leak floor for V_REL random cos-hits: `sqrt(2*log(V_REL)/N)`
  - At V_REL=1024, N=2048 (smoke): 0.082
  - At V_REL=1024, N=8192 (full):  0.041
- Signal cos_match under heavy regime (p_flip=0.20): `1 - 2p = 0.60`
- Signal-to-leak gap: 0.60 - 0.082 (smoke) = 0.52; 0.60 - 0.041 (full) = 0.56
- Gap widens 8% at full-N vs smoke-N; discriminator is CONSERVATIVE at smoke
  (smoke is HARDER to separate than full). Full-N will show clearer surface.
- Under clean regime (p_flip=0.00): signal cos_match = 1.0 -> RELATION_CHECK
  never refuses PURE_IN; near_refuse depends purely on leak floor. V_REL scan
  at clean should stay flat near 0 (leak <= 0.082 << thr=0.40).
- Under heavy regime: as V_REL grows, log(V_REL)/sqrt(N) leak grows;
  monotonic near_refuse rise expected.
- **Smoke uses V_REL_SWEEP=[64,256,1024]** (spans full range) so smoke can
  discriminate monotonicity at 3 points AT the full-N discriminator scale.

**T11 selftest** additionally verifies that at smoke N=2048, V_REL=1024, heavy
regime, NEAR near_refuse is bounded strictly in (0.05, 1.00) -- the
discriminator has room to fire.

## Cross-cell discipline

- ASCII only
- Substrate-only at inference (numpy primitives; zero LLM forward calls; assert = 0)
- Per-arm per-cell metrics in per_unit (Fix #28)
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] cross-cell consistent
- META_M6: NAIVE_ALONE baseline derived in-cell at each (V_REL, regime)
- META_M7: smoke matches full on N + V_C_IN + N_QUERIES_PER_CATEGORY; only
  SEEDS + V_REL_SWEEP reduce (full [64,128,256,512,1024] vs smoke [64,256,1024])
- META_RULE_H CARDINALITY_OK: EXPECTED_N_UNITS=45 asserted in verdict; if
  observed < expected, HARD_FAIL_CARDINALITY_BREACH fires

## Capacity-feasibility (production-scale check per BIAS-M)

Per-unit wall dominated by V_REL=1024 matmul: 100 queries x N=8192 x 1024 =
~0.8 GFLOPS per category per arm; 3 cat x 2 arm = 4.8 GFLOPS per unit.
- V_REL=64:  ~1s per unit
- V_REL=256: ~4s per unit
- V_REL=512: ~8s per unit
- V_REL=1024: ~16s per unit
Sum for 3 seeds x 5 V_REL x 3 regimes = 45 units:
  ~3 seeds x 3 regimes x (1 + 2 + 4 + 8 + 16) = 9 x 31 = 279s = ~5min wall total.

## Timeout estimate

Formula (per SMOKE_ONLY_LOCAL 2026-07-01 -- full to remote):
`timeout_s = ceil(3.0 * expected_wall_s + 300s safety)`
Expected wall = 300s (measured above). Safety = 300s for cleanup at V_REL=1024 +
per-unit checkpoint I/O + numpy warmup. `timeout_s = 900 + 300 = 1800s (30min)`

## PROT compliance

- PROT-018 (`_n<N>` suffix): no `_n<N>` in anchor name; rule N/A
- PROT-019 (large-N timeout floor): no `_n<N>`; rule N/A
- PROT-020 (GPU queue requires torch): overnight_queue but numpy-only cell;
  runs on GPU machine CPU. Not GPU-utilized (low FLOP density; V_REL=1024 x
  N=8192 = 8M floats per matmul; GPU launch overhead > compute). Acceptable
  for this cell size (~5min total wall). No CUDA import; no torch.
- PROT-021 (long-timeout needs checkpoint): 1800s < 14400s floor; but
  per-(seed, V_REL, regime) checkpoint wired anyway.

## Pre-flight smoke + self-test gate

- Smoke: N=2048, V_C_IN=150, N_QUERIES=20, seeds=[11], V_REL_SWEEP=[64,256,1024]
  x REGIMES=[clean, moderate, heavy] = 9 units. Smoke wall = **1.5s** (measured 2026-07-01).
- Smoke verdict at author time: **HARD_PASS_CALIBRATION_UNIFORM**
  (spreads {0.019, 0.024, 0.020}; monotonic; regime-invariant magnitude).
  Confirms discriminator fires at smoke; full-N=8192 expected to show tighter
  spread (~0.009 theoretical) but still monotonic + uniform.
- Self-test T1-T11:
  - T1: bipolar unit-norm
  - T2: stochastic flip preserves L2 at p in {0, 0.08, 0.20, 0.40}
  - T3: stochastic flip has trial variance (cos_std in [0.005, 0.05])
        (NOT deterministic count; verifies M1.3 stochastic mode)
  - T4: build_substrate scales to V_REL=1024
  - T5: clean regime (p=0) yields self-id sim > 0.99
  - T6: heavy regime (p=0.20) drops audit sim to ~0.60 (in [0.50, 0.75])
  - T7: all 2 arms return refused booleans
  - T8: per-category eval has correct query counts
  - T9: bands locked
  - T10: LLM counter = 0
  - T11: discriminator survives scale (heavy V_REL=1024 smoke: NEAR refuse in
         (0.05, 1.00), not saturated at smoke)

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports BOTH directions:
- HARD_PASS conditions (monotonic + spread; UNIFORM as special case)
- MIDDLE_BAND (partial)
- HARD_FAIL (non-monotonic / no-sensitivity / sanity-rail / high-cv / cardinality)
- Per (seed, V_REL, regime, arm, category) breakdown in per_unit
- Per-regime `spread` + `monotonic` bool for Skunkworks step-0 re-read

## Strategic significance

If HARD_PASS_CALIBRATION_MONOTONIC:
- Refuse-gate calibration surface is characterized: V_REL is a knob under
  noise; ineffective in clean regime
- Enables cortex-level V_REL selection based on inferred noise regime
- Composes with adaptive-tau (in-flight cell) for regime-adaptive refuse-gate

If HARD_FAIL_NO_V_REL_SENSITIVITY:
- V_REL is not a useful calibration knob at all; refuse-gate is
  regime-invariant to relation library size in tested range
- Simplifies refuse-gate: fix V_REL at any capacity-feasible value

If HARD_FAIL_NON_MONOTONIC:
- Calibration surface is non-trivial (interference or resonance effects);
  triggers research drill into cross-term dynamics between subject and
  relation cleanup at scale

## Honest negatives possible

- Sanity PURE_IN might collapse at moderate + V_REL=1024 (moderate is too
  aggressive AT V_REL=1024 given N=8192); this triggers HARD_FAIL_SANITY_RAIL
  which is INFORMATIVE (calibration surface has a cliff below what cell tested)
- RELATION_CHECK might not saturate at clean (unlike v1 result at flip_frac=0.10)
  because at p=0.00, subject audit sim = 1.0 EXACTLY; the difference between
  clean and v_rel_extension_v1 flip=0.10 might reveal near_refuse != 0 at clean
  due to distractor accumulation (log(V_REL) leak crossing thr at V_REL=1024)
- Q-DISCIPLINE might fire under heavy at all cells if audit_thr=0.40 is too loose

## Dispatch plan

1. Author cell + prereg (this file) -- DONE
2. Self-test PASSED locally (T1-T11)
3. SMOKE run locally (SMOKE-ONLY-local rule; 9 units, ~30s expected)
4. Path-scoped commit (cell + prereg only; NEVER git add -A / .)
5. FULL dispatch via hdi_orchestrator to overnight_queue (numpy-only, CPU-runs-on-GPU-machine
   OK for 5min wall; not routed to remote_cpu_queue because overnight_queue has more
   headroom right now and no torch/CUDA present)
6. REMOTE VERIFY post-ship: cell-spec on remote matches local; metrics.json
   honors REQUIRED_FIELDS at landing

## Test plan post-landing

- Skunkworks step-0 honest re-read of per_unit per-(V_REL, regime) near_refuse
  (NOT verdict_msg framing)
- Verify cv <= 0.05 at each of 15 (V_REL x regime) cells
- Verify PURE_IN answer rail at clean + moderate (heavy allowed to break)
- Verify PURE_OUT refuse rail at all regimes
- Cross-cell: at (V_REL=256, regime=~flip_frac=0.10 equivalent) does near_refuse
  match v_rel_extension_v1 landed result? Sanity parity across cell versions.
- If HARD_PASS: file atom + hdlab primitive update; queue composition with
  adaptive-tau cell for regime-adaptive refuse-gate
- If HARD_FAIL: research drill into surface structure

## Routing rationale

- overnight_queue: 45 units at ~5min total wall; numpy-only; CPU-feasible.
  local_cpu_queue explicitly RULED OUT per SMOKE-ONLY-local rule (2026-07-01)
- remote_cpu_queue also acceptable; overnight_queue chosen for smaller wall +
  GPU-idle-anyway condition; hdi_orchestrator will pick queue at dispatch
- Pause flag verified NOT set at authorship time
- Push required (harness-DENIED to exp_dev); MUST route via hdi_orchestrator
