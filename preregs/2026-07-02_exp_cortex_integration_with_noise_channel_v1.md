# Pre-registration: exp_cortex_integration_with_noise_channel_v1

**Date:** 2026-07-02
**Anchor:** exp_cortex_integration_with_noise_channel_v1
**Queue:** remote_cpu_queue (FULL); local_cpu_queue (smoke only per USER 2026-07-01)
**N:** 8192, **Seeds:** [7, 13, 19] (3 seeds), **Primitives:** {M1.4, M1.5, M1.7, M1.8}
**Phase:** 3b (noise-enabled variant of Phase 3 cortex integration test)

## Scientific question

Does the Phase 2b NoiseChannel wiring (extracted 2026-07-02 commit 50f44b7cf;
CortexConfig fields `noise_channel_enabled` + `noise_channel_sigma_boundary`)
preserve composed-pipeline behavior when disabled (backwards-compat to Phase 3
CG) AND keep composition metrics bounded when enabled (no cross-primitive
corruption via side channel)?

Phase 3 (noise-DISABLED path) landed HARD_PASS 3-seed at
`data/exp_cortex_integration_end_to_end_v1/metrics.json` with delta=0.0000
across all 4 primitives (bit-identical composed vs individual). Phase 3b tests
that (a) enabling the noise channel does NOT break the Phase 3 baseline when
disabled (defensive backwards-compat) and (b) enabling the noise channel with
sigma in {0.05, 0.15} produces bounded composition-metric drift.

## Substrate physics documentation (framing warning; per §7 NO_HALLUCINATED_NUMBERS)

For 8192-D bipolar vectors + `NoiseChannel.inject` L2-preserving Gaussian noise:

- `cos(v_bipolar, inject(v_bipolar)) = 1/sqrt(1 + sigma^2)` THEORETICAL@
  hdlab/noise_channel.py:145-156 renorm math applied to bipolar-scaled vec
- MEASURED@ selftest computed: sigma=0.05 -> 0.9988; sigma=0.15 -> 0.9889
- **Substrate is highly noise-tolerant on bipolar vectors at these sigmas.**
- Contrast with UNIT-NORM Gaussian: cos ~ 1/sqrt(1 + n_dim*sigma^2); at n=8192
  sigma=0.15 -> 0.0736 THEORETICAL@ hdlab/noise_channel.py:243-266.

Additionally, per Phase 3 arm implementations (inherited unchanged for
backwards-compat reproduction test):
- M1.5 arm reads via `cx._context.read()` DIRECTLY; write path uses caller's
  clean role_key. No path from noise-perturbed q_2d to M1.5 metric.
- M1.7 arm invokes summarize_role via role_slot_context kwarg which routes
  item_keys/role_assign/val_indices direct to summarizer per
  cortex.py:369; no q_2d involvement.
- M1.8 arm invokes `_clarify_gate.evaluate_batch` on synthetic scores DIRECTLY;
  no q_2d involvement.
- M1.4 arm uses uncorrelated bipolar queries; even with noise perturbation,
  max_sim vs random keys stays ~0.03 (noise doesn't create correlation);
  refuse_rate stays ~1.0.

**EMPIRICAL PREDICTION:** delta_noise_on_vs_off ~ 0.00 across all primitives
at both sigmas. This is CORRECT wiring behavior (Phase 3 arms bypass the noise
pathway by design) AND correct substrate physics (bipolar noise tolerance).
The DISCRIMINATOR-FIRES gate is the noise-effect probe (unit-norm query
router-path max_sim shift), which per THEORETICAL prediction should show
substantial cos-shift at sigma=0.15.

## Pre-registered bands

**HARD-PASS (all 4 conditions):**
1. **Backwards-compat gate:** all 4 primitives satisfy
   `|noise_off_metric - individual_metric| <= 0.05` per seed. Reproduces Phase
   3 CG under disabled noise (defensive; catches wiring regression that would
   change the Phase 3 baseline).
2. **Noise-light stability gate:** all 4 primitives satisfy
   `|noise_light_metric - noise_off_metric| <= 0.05` per seed (sigma=0.05 does
   NOT corrupt sub-primitive state via side channel).
3. **Noise-moderate bounded gate:** all 4 primitives satisfy
   `|noise_moderate_metric - noise_off_metric| <= 0.20` per seed (sigma=0.15
   drift stays bounded).
4. **Noise-effect probe wiring-live gate:** `max_seed(probe_moderate_cos_shift)
   >= 0.001` on unit-norm queries at sigma=0.15. Confirms NoiseChannel is
   actually perturbing q_2d in forward() (not silently ignored).

**MIDDLE:** conditions 1-2 pass and probe fires (live wiring, no corruption);
3 of 4 primitives bounded under sigma=0.15 but one drifts in (0.20, 0.30].
NOISE_MODERATE_DRIFT_FLAG.

**HARD-FAIL:** any of:
- Condition 1 fails (WIRING_HAZARD_BACKWARDS_COMPAT: Phase 2b broke Phase 3
  baseline).
- >=2 primitives fail condition 2 (WIRING_HAZARD_LIGHT_NOISE: noise corrupts
  sub-primitive state).
- Probe wiring liveness fails (NOISE_NOT_APPLIED: NoiseChannel appears silently
  bypassed).
- Any primitive drift > 0.30 under sigma=0.15 (upper HF bound).
- Cardinality breach (n_units != 48).

## Calibration rationale

Per-primitive metric definitions unchanged from Phase 3 (see
`preregs/2026-07-02_exp_cortex_integration_end_to_end_v1.md` L40-109 for full
detail). Phase 3b adds noise variants of the COMPOSED arm:

- `NOISE_OFF`: `CortexConfig(noise_channel_enabled=False)` — matches Phase 3.
- `NOISE_LIGHT`: `CortexConfig(noise_channel_enabled=True,
  noise_channel_sigma_boundary=0.05)` — 'light' regime per
  `hdlab.noise_channel.REGIME_SIGMA` THEORETICAL@ noise_channel.py:65.
- `NOISE_MODERATE`: `CortexConfig(noise_channel_enabled=True,
  noise_channel_sigma_boundary=0.15)` — 'moderate' regime; USER 2026-06-30 5x
  drill anchor point CITED@ hdlab/noise_channel.py:11 M1.4 CG-anchor.
- `INDIVIDUAL`: primitives called directly with matched config; no noise
  (reference).

**Reference metrics (Phase 3 CG):**
- M1.4 refuse_rate = 1.0000 MEASURED@`data/exp_cortex_integration_end_to_end_v1/metrics.json:delta_summary.m14.composed_mean`
- M1.5 recall = 1.0000 MEASURED@ same file `.m15.composed_mean`
- M1.7 role_top1 = 1.0000 MEASURED@ same file `.m17.composed_mean`
- M1.8 clarify_recall = 0.6600 MEASURED@ same file `.m18.composed_mean`

**Predicted metrics under noise (empirical prediction):**
- All 4 primitives, all 3 seeds, both sigmas: metric == NOISE_OFF metric within
  numerical precision (~1e-6). Reasoning: arm implementations bypass q_2d
  pathway (M1.5/M1.7/M1.8) or use uncorrelated queries (M1.4) where bipolar
  noise math preserves cos ~0.99. HYPOTHESIZED@ this pre-reg.

## Noise-effect probe (discriminator-fires gate)

Independent of arm metrics: verifies NoiseChannel is actually being applied to
q_2d in `forward()`. Method: use 20 unit-norm Gaussian queries per seed,
compute max_sim via `cortex.forward(q, context_keys, context_vals)` twice —
once with noise=False, once with noise=True at target sigma; report mean
|max_sim_off - max_sim_on| across queries.

THEORETICAL@ hdlab/noise_channel.py:245-266 (test_5 regime monotonicity):
unit-norm query at n_dim=8192 sigma=0.15 has expected cos(clean, injected)
~ 0.074; the max_sim shift on a random tape is proportional. Probe passes if
mean shift >= 0.001 (extremely permissive floor; any live wiring should
substantially exceed).

## Compute architecture (mandatory per USER-locked 2026-07-02)

Class: **(c) mixed** — inherits `hdlab.cortex.Cortex` MIXED storage strategy
plus NoiseChannel NO_STORAGE per hdlab/noise_channel.py:31.

Justification:
- Sub-primitive storage strategies preserved unchanged from Phase 2b landed
  cortex.py:24-35 (M1.3 NO_STORAGE / M1.5 MIXED / M1.7 SHARDED / M1.4 + M1.6
  + M1.8 NO_STORAGE).
- Compute mode: numpy/torch CPU; no torch.cuda. Per-primitive walls unchanged
  from Phase 3 (~30s per seed FULL); noise arms add ~2x overhead for the
  extra forward calls -> ~15s per seed FULL. 3 seeds -> ~45s + 20-query
  probe x 3 seeds x 2 sigmas ~15s -> ~60s FULL total.
- Not a GPU-batching candidate (per-arm walls << 10s; sequential pipeline
  composition per §GPU-BATCHING-MANDATORY discipline exemption for cell wall
  < 10s per phase-point).
- Sequential-CPU appropriate: primitives compose a natural pipeline with
  sequential dependencies (write -> read -> summarize -> classify).

## Storage strategy declaration

`storage_strategy: "MIXED_inherited_per_primitive_no_facade_storage_plus_NO_STORAGE_noise_channel"`
matches Cortex facade + NoiseChannel line-referenced sources.

## SCHEMA-VET pre-reg fields (mandatory per hdi_exp_dev CHECKLIST)

- `cardinality_ok: True`. `EXPECTED_N_UNITS = 4 primitives x 4 arms x 3 seeds
  = 48`. Verdict logic counts `len(per_unit)`; if `!= 48`, emit
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `arms_differ_verified: True`. 4 arms per primitive have distinct source-hash
  code paths (noise_off vs noise_light vs noise_moderate use different
  sigma constants + noise_enabled flag; individual is a separate function).
  META_RULE_AF asserted at cell-run entry.
- `final_metrics_atomicity: "tmp_replace"`. Single-shot cell; writes
  metrics.json.tmp then os.replace atomically.
- `crlb_n/a: "integration-fidelity test + noise-wiring liveness check; no
  capacity-noise floor; metric is |delta| tolerance not signal-detection"`.
- `baseline_in_band: True` (exempt via bit-identity design). COMPOSED baseline
  for M1.5/M1.7 = 1.0 at pre-registered discriminator regime (STM within
  capacity; role-slot fully-populated) is CORRECT-BY-DESIGN. Discriminator-
  fires gate is the noise-probe cos-shift (unit-norm queries; expected shift
  substantial per THEORETICAL prediction).
- `calibration_check: "default_ok_for_this_regime"`. Sub-primitive defaults
  inherited from Phase 1 CG selftests + Phase 3 CG.
- `discriminator_reachability: True`. HP thresholds achievable per THEORETICAL
  prediction (arms bypass noise pathway -> delta ~0 by design + wiring); probe
  cos-shift floor 0.001 is extremely permissive per unit-norm noise math.
- `discriminator_fires: True`. Noise-effect probe (unit-norm queries; expected
  cos-shift >> 0.001 at sigma=0.15) IS the discriminator-fires gate. It's
  independent of arm metrics because arm implementations bypass q_2d by
  design (Phase 3 inheritance for backwards-compat reproduction).
- `cell_chunked: False`. Single-seed-per-run via for-loop over [7,13,19];
  wall per seed < 60s; runner-death risk negligible on remote_cpu_queue.
- `start_marker_written: True`. `_write_start_marker` at main() entry.
- `crash_diagnostic_present: True`. `except Exception -> _write_crash_metrics`
  with SystemExit/KeyboardInterrupt ordering per META_RULE.
- `heartbeat_present: True`. `emit_heartbeat` per seed via
  `experiments._cell_heartbeat` helper.
- `defensive_error_checking: "passed_all_4_patterns"`.
- `progress_logging: "print_flush_true"`. All progress lines use flush=True.

## §15 test-design gates

- Gate A `effective_vs_nominal_parameter_audit`: N/A — no swept axis.
- Gate B `bracket_includes_discriminating_band`: N/A — integration-fidelity
  test. Discriminator is delta from reference + noise-effect probe cos-shift.
- Gate C `signal_shape_compatibility_audit`: SHAPE_MATCH for all edges (Phase
  2b landed selftests verified 9 selftests passing including 3 noise-specific
  ones per hdlab/cortex.py:538-611).
- Gate D `reproduce_prior_chain_grade_result_as_positive_control`: THIS CELL
  reproduces Phase 3 CG via NOISE_OFF arm. Each primitive's NOISE_OFF arm at
  matched (seed, N, K) MUST reproduce Phase 3 metric within 0.05
  (backwards-compat gate = Gate D writ large).
- Gate E `functional_requirement_decomposition_present`:
  - FR1: Cortex noise wiring must be backwards-compat when disabled (Phase 3
    reproduction) — GATE 1.
  - FR2: Cortex noise wiring must not corrupt sub-primitive state when
    enabled at light regime — GATE 2.
  - FR3: Cortex noise wiring must bound composition metrics under moderate
    regime — GATE 3.
  - FR4: Cortex noise wiring must actually be perturbing q_2d (not silently
    bypassed) — GATE 4 (noise-effect probe).

## Ablation-fires equivalent

Phase 3 used explicit ABLATED arms (refuse_tau=-1, empty context, etc.) as
discriminator-fires. Phase 3b uses the NOISE_EFFECT PROBE arm — an
architecturally-distinct discriminator-fires gate: unit-norm queries route
through the noise-affected pipeline; max_sim shift verifies wiring is live
regardless of the arm-metric flatness prediction.

## N-suffix section

Not sweep-axis dependent. N_DIM = 8192 (Cortex default); anchor is
`exp_cortex_integration_with_noise_channel_v1` (no _n<N> suffix; single N
regime matches Phase 2b CG envelope).

## Timeout estimate

Per-seed wall (Phase 3 elapsed 9.7s at 3 arms x 4 primitives x 3 seeds = 36
units -> ~0.27s per unit):
- 4 arms x 4 primitives x 3 seeds = 48 units -> ~13s
- Plus 3 seeds x 2 sigmas x 20 unit-norm queries (probe): ~10s
- Overhead: ~5s
- Total FULL wall: ~30-45s

Timeout: `full_timeout_s = 600s` (10 min floor per PROT-019). Smoke seeds=[7]
+ reduced grid + 1-sigma probe: ~10s wall; `smoke_timeout_s = 300s`.

## Framing warning (repeat for framing safety)

- Empirical result of delta=0.0000 across NOISE_OFF/LIGHT/MODERATE on all
  primitives is EXPECTED and CORRECT (arms bypass q_2d by design). Do NOT
  frame as "noise wiring is broken" — the probe (independent gate) verifies
  liveness.
- WIRING_HAZARD interpretation is reserved for: (a) NOISE_OFF != INDIVIDUAL
  (backwards-compat broken by Phase 2b landing), (b) any arm drifting >0.20
  under noise (side-channel corruption), or (c) probe cos-shift ~0
  (NoiseChannel silently no-op'd).
- Do NOT modify Phase 3 cell (this is a NEW cell). Phase 3 stays as noise-off
  baseline CG reference.

## Prognosis (from spawn prompt + this pre-reg analysis)

P_CG = 0.60 (Phase 2b wired cleanly + selftests pass + arm bypass predicts
delta=0 automatically + noise-probe should fire per THEORETICAL noise math);
P_MB = 0.30 (unexpected sub-primitive state corruption at moderate sigma is
possible if noise gets into caches or provenance state); P_HF = 0.10
(Phase 2b integration introduced a wiring regression that changes Phase 3
baseline OR probe cos-shift comes back ~0 signaling silent no-op).
