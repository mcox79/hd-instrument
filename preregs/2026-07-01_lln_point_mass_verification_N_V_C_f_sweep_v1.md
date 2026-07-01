# Pre-reg: LLN point-mass verification (N x V_C x f sweep) v1

**Anchor:** `lln_point_mass_verification_N_V_C_f_sweep_v1`
**Date filed:** 2026-07-01
**Author:** exp_dev (spawned by hdi_research)
**Cross-refs:**
- Atom 12 MM (Skunkworks 2026-07-01): in-KB max_sim is a POINT MASS at 1-2f at high-dim bipolar FHRR (LLN concentration).
- Landing 15 v8 conformal seed 7 tau values: three point masses at 1-2f for f in {0, 0.15, 0.30}.
- Landing 7 substrate_refuse_gate physics law: V_REL cleanup floor sqrt(2 log V_REL / N).
- LLN analytical basis: bipolar dot-product concentration + extreme-value theory for random-key OOD.

## Purpose

Lift Atom 12 (LLN point-mass on in-KB max_sim MM) from MEASURED_MECHANISM to CHAIN_GRADE by
demonstrating the property is a GENERAL substrate physics feature, not a specific-config artifact.
Establishes foundational substrate-physics primitive for future cortex-external calibrator design
(cortex layer needs to know max_sim(in-KB) is deterministic-modulo-fp32 so it can inject stochastic
noise at the boundary per USER 2026-06-30 M3 cortex directive).

## Expansion criteria (per Skunkworks lift-to-CG requirements)

(b) different N showing LLN still holds
(c) different f showing point-mass at 1-2f each
(d) different V_C showing OOD leak scales as sqrt(2 log V_C / N)

## Design: 3-axis sweep (N x V_C x f)

- **N** in {4096, 8192, 16384} (3 values)
- **V_C** in {100, 200, 400} (3 values)
- **f** in {0.05, 0.10, 0.15, 0.20, 0.30} (5 values)
- **Total phase points per seed:** 3 * 3 * 5 = 45
- **Seeds:** 7, 13, 19
- **Cardinality total:** 45 * 3 = 135 units across all seeds
- **EXPECTED_N_UNITS per seed:** 45 (declared for META_RULE_H)
- **Cell chunked?** NO. Single-cell multi-seed via _seed_checkpoint per-seed atomic partials.
  Rationale: numpy-only, ~30-60s per seed wall — well under runner timeout; per-seed checkpoint
  provides crash-resume if runner dies. Multi-seed cell is fine at this compute scale.

## Per-phase-point protocol

At each (N, V_C, f):
1. Build KB of V_C bipolar keys and V_C bipolar values, seed-controlled RNG.
2. Build calibration set of 100 items:
   - 50 in-KB queries: randomly pick a KB key, flip f fraction of its bipolar components, normalize.
   - 50 OOD queries: fresh random bipolar keys (never in KB), normalize.
3. Compute max_sim for each of the 100 items over the V_C-item KB.
4. Record quantiles of in-KB max_sim: p5, p10, p25, p50, p75, p95.
5. Record quantiles of OOD max_sim: p10, p50, p90.
6. Compute `spread_p5_p95_in_kb = p95_in_kb - p5_in_kb`.
7. Compute `theoretical_in_kb_center = 1 - 2*f`.
8. Compute `theoretical_ood_floor = sqrt(2 * log(V_C) / N)`.
9. Compute `observed_deviation_in_kb = |p50_in_kb - theoretical_in_kb_center|`.
10. Compute `observed_deviation_ood = |p50_ood - theoretical_ood_floor| / theoretical_ood_floor`.

## Theoretical predictions (computed offline; MEASURED via cell)

**In-KB max_sim center (THEORETICAL@analytical bipolar LLN):**
- f=0.05 -> 0.900
- f=0.10 -> 0.800
- f=0.15 -> 0.700
- f=0.20 -> 0.600
- f=0.30 -> 0.400

**In-KB max_sim per-item std (THEORETICAL@sqrt(4f(1-f)/N)):**
- Range across regime: 0.0034 (N=16384, f=0.05) to 0.0143 (N=4096, f=0.30)

**In-KB spread p5-p95 (THEORETICAL@2*1.645*std, normal approx):**
- Range across regime: 0.011 (N=16384, f=0.05) to 0.047 (N=4096, f=0.30)
- **KEY:** the SPAWN prompt's `spread_p5_p95 < 0.005` gate is IMPOSSIBLY TIGHT.
  Per-item cosine has irreducible finite-N variance ~sqrt(4f(1-f)/N) at ~0.005-0.015 std.
  50-item spread is 2-3 orders of magnitude LARGER than 0.005.
  **Corrected discriminator:** LLN says spread scales as 1/sqrt(N) with f-dependent prefactor;
  observed spread should be within [0.5, 2.0]x the theoretical normal-approx prediction.

**OOD floor sqrt(2 log V_C / N) (THEORETICAL@extreme-value theory for V_C random keys):**
- N=4096: 0.047 (V_C=100) to 0.054 (V_C=400)
- N=8192: 0.033 to 0.038
- N=16384: 0.024 to 0.027
- Ratio spread across V_C is small; MAIN LLN discipline is 1/sqrt(N) scaling.

## Verdict gates (CORRECTED from spawn — spread gate was infeasible)

### HP_LLN_CENTER_VERIFIED (in-KB point-mass center at 1-2f):
For ALL 45 phase points, per seed: `|observed_p50_in_kb - (1-2f)| < 0.010`
(loose bound; per-item std at worst N=4096 f=0.30 is 0.014; 50-item p50 SE is std/sqrt(50) ~0.002;
0.010 is ~5x SE = generous cushion for fp32 quantization + finite-sample).

### HP_LLN_SPREAD_SCALING (LLN concentration -- spread shrinks as 1/sqrt(N)):
For ALL 45 phase points: `0.5 <= observed_spread / theoretical_normal_spread <= 2.0`
where `theoretical_normal_spread = 2 * 1.645 * sqrt(4f(1-f)/N)`.
This is the ACTUAL LLN discriminator per Skunkworks criterion (b): different N shows spread
scaling as 1/sqrt(N). Point-mass concentration is a rate, not a zero.

### HP_OOD_FLOOR_SCALING (OOD leak scales as sqrt(2 log V_C / N)):
For ALL 45 phase points: `|observed_p50_ood - theoretical_ood_floor| / theoretical_ood_floor < 0.30`
(30% tolerance; extreme-value asymptotics have slow O(1/log V_C) convergence at these small V_C).

### CHAIN_GRADE verdict:
ALL THREE HP gates clear at ALL 45 phase points across ALL 3 seeds
AND arms_differ_verified (via N sweep producing distinct spread magnitudes)
AND CARDINALITY_OK = True

### MIDDLE_BAND verdict:
HP gates clear at some N values but not others. Indicates regime-dependent LLN
(would surprise; substrate physics should be universal in the tested range).

### HARD_FAIL_LLN_BROKEN:
Any phase point where `observed_p50_in_kb` deviates from `1-2f` by more than 0.05
(mechanism broken; substrate not producing LLN-concentrated cosines).

### HARD_FAIL_OOD_SCALING_BROKEN:
Any phase point where observed OOD floor is >2x or <0.5x theoretical.

### HARD_FAIL_CARDINALITY_BREACH_META_RULE_H:
Any seed produces `len(per_unit) != 45`.

## HP_SCOPE per-arm declaration

Not applicable — this cell is a sweep, not a multi-arm mechanism cell. All 45 phase points
receive all 3 HP gates. Effectively: `HP_SCOPE: {all_phase_points: [HP_LLN_CENTER_VERIFIED,
HP_LLN_SPREAD_SCALING, HP_OOD_FLOOR_SCALING]}`.

## SCHEMA-VET checklist

- `cardinality_ok`: MANDATORY = True (45 per seed; sweep-axis cell)
- `EXPECTED_N_UNITS`: 45 per seed
- `arms_differ_verified`: True (implicit via sweep; spread differs across N by design)
- `arms_differ_exempted`: N/A
- `final_metrics_atomicity`: `per_iter_paths` (per-seed partials via write_partial + aggregate)
- `except SystemExit: raise` BEFORE `except Exception`: True (template applied)
- `crlb_floor_computed`: N/A for this cell class (no k-orthogonality; LLN-based bipolar)
- `crlb_n/a`: "LLN concentration cell; discriminator is spread-scaling not CRLB floor"
- `discriminator_reachability`: True (theoretical predictions computed offline; gates within finite-sample)
- `baseline_in_band`: N/A (no baseline arm; each phase point is its own witness)
- `discriminator_survives_scale`: True (smoke runs FULL 45-point grid at N=4096 -- discriminator
  visible at smallest N; also runs a preview at N=16384 to verify 1/sqrt(N) scaling in smoke)
- `HARD_PASS strictly above floor + 5%`: True (0.010 center-gate is 5x SE = ~5x above 0.002 SE)
- `HP_SCOPE`: all_phase_points -> all 3 HP gates
- `cardinality_ok`: True
- `per-unit failure-class instrumentation`: True (specific-exception catch per phase point)
- `calibration_check`: `adaptive_with_discriminator_gate` (spread gate uses analytical formula;
  discriminator still fires because scaling still verifiable across N regime)
- `all numbers tagged`: MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ per META_RULE_AC
- `cell_chunked`: False (single-cell multi-seed; per-seed atomic partials via _seed_checkpoint)
- `start_marker_written`: True (writes _start_marker.json at main() entry)
- `crash_diagnostic_present`: True (Exception -> CELL_CRASHED metrics.json + traceback)
- `heartbeat_present`: True (per-phase-point emit_heartbeat)
- `defensive_error_checking`: "passed_all_4_patterns"

## Test-design failure prevention gates (Section 15)

- **A) effective_vs_nominal_parameter_audit:** ALIGNED. N is the actual substrate dimension used
  in bipolar generation; V_C is the actual KB size used in max_sim; f is the actual bit-flip
  fraction applied. No routing / compositional mismatch.
- **B) bracket_includes_discriminating_band:** ALL 45 phase points are IN-BAND for the LLN
  test — the discriminator IS the observed p50/spread vs the analytical prediction; every phase
  point either matches or doesn't. `discriminating_fraction = 45/45 = 1.0`.
- **C) signal_shape_compatibility_audit:** N/A — cell is not composing primitives; single-primitive
  measurement cell.
- **D) reproduce_prior_chain_grade_result_as_positive_control:** N/A — this cell IS the
  chain-grade lift test for Atom 12; no prior CG primitive is being invoked. Cross-reference to
  Landing 15 v8 conformal tau (three point masses at 1-2f for f in {0, 0.15, 0.30}) serves as
  external anchor: at f=0.15, our p50 should agree with Landing 15's tau within 0.010.
- **E) functional_requirement_decomposition_present:** Functional requirements:
  1. "Verify in-KB max_sim concentrates at 1-2f across N sweep" -> bipolar dot product + LLN
  2. "Verify OOD max_sim leak floor scales as sqrt(2 log V_C / N)" -> random-key noise + EV theory
  3. "Verify spread narrows as N increases (LLN rate)" -> per-item cosine std shrinks as 1/sqrt(N)
  All three map to closed-form analytical primitives; no new mechanism designed.

## Smoke regime

**Smoke config:** SAME 45-point grid at 3 phase-points-per-axis-value + 1 seed.
- N in {4096, 8192, 16384} (full sweep -- discriminator MUST survive scale)
- V_C in {100, 200, 400} (full sweep)
- f in {0.05, 0.10, 0.15, 0.20, 0.30} (full sweep)
- seeds = [7] (1 seed; other 2 dispatched in full run)
- 100 items per phase point (matches full)

**Smoke passes iff:**
- All 45 phase points produce complete quantiles (no NaN/crash)
- HP_LLN_CENTER_VERIFIED passes at all 45 points for seed 7
- HP_LLN_SPREAD_SCALING passes at all 45 points for seed 7
- HP_OOD_FLOOR_SCALING passes at all 45 points for seed 7

Note: smoke runs the FULL grid at 1 seed. Full run = same grid at seeds [13, 19] (seed 7 reused
via per-seed checkpoint). Wall estimate: seed 7 smoke = ~60s (dominated by N=16384 dot products).

## Dispatch plan

1. Author cell + prereg (this file) — DONE
2. Local self-test (module-import + smoke gate) — before commit
3. Smoke run on `local_cpu_queue` (numpy-only + ~60s wall = laptop-safe per USER 2026-07-01)
4. If smoke HARD_PASS: commit cell + prereg + dispatch handoff -> hdi_orchestrator for remote push
   + remote_cpu_queue queue_add (full run across 3 seeds)
5. Report full landing state; Skunkworks tiers to CG or MB

## Formula reference

- In-KB cosine: `sim(v, corrupt(v, f)) ~ Normal(1 - 2f, sqrt(4f(1-f)/N))` (bipolar LLN)
- OOD floor: `max_i cos(q, k_i) for i.i.d. random keys ~ sqrt(2 log V_C / N)` (Gaussian EV asymptotic)
- Per-item std: sqrt(4 f (1-f) / N)
- Normal p5-p95 spread: 2 * 1.645 * std = 3.29 * sqrt(4 f (1-f) / N)

## Timeout

- Smoke: 300s (5 min; wall estimate ~60s; 5x cushion)
- Full: 1800s (30 min; 3 seeds * ~60s = ~180s; 10x cushion)

## Route

- Smoke: local_cpu_queue
- Full: remote_cpu_queue (via Orchestrator handoff for push + queue_add)
