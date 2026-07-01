# Pre-registration: multihop_reasoning_vc_axis_sweep_gpu_v2

**Anchor:** `multihop_reasoning_vc_axis_sweep_gpu_v2`
**Cell:** `experiments/exp_multihop_reasoning_vc_axis_sweep_gpu_v2.py`
**Author:** exp_dev
**Date:** 2026-07-01
**Supersedes:** `experiments/exp_multihop_reasoning_vc_axis_sweep_gpu_v1.py` (Wave 18 dispatch crash 2026-07-01)

## V1 crash context (MEASURED, disk-cited)

- v1 dispatched Wave 18 FULL to overnight_queue at N_DIM=8192, N_CHAINS=200, MAX_DEPTH=30,
  V_C_VALUES=[100, 200, 400].
- v1 crashed at V_C=100 arm with:
  `RuntimeError: make_deep_chains: only 100/200 at max_depth=30`
- Root cause (THEORETICAL@ analysis of `make_deep_chains` loop,
  `experiments/exp_multihop_reasoning_vc_axis_sweep_gpu_v2.py:304-333`):
  `make_deep_chains` accumulates unique START-concepts in a `used_s` set across
  N_CHAINS iterations. Successors sampled uniquely within each chain (needs
  V_C > max_depth) but starts must ALSO be unique across chains, giving
  N_CHAINS <= V_C as the binding constraint. V_C=100 x N_CHAINS=200 is
  impossible by construction.
- v1 smoke used N_CHAINS_LOCAL=30, so smoke satisfied 30 <= V_C=100 and passed.
  This is a DISCRIMINATOR-MUST-SURVIVE-SCALE gap: smoke feasibility did not
  imply full feasibility. v2 fixes at design level.

## V2 fix (simple: drop V_C=100 arm)

- V_C_VALUES: `[100, 200, 400]` -> `[200, 400]` (2 arms x 2 depths = 4 arms per seed)
- All other parameters unchanged: N=8192, PART_SIZE=10, MAX_DEPTH=30, N_CHAINS=200
- Sibling cell `_partition_size_sweep` (Wave 14) already covers V_C=200 x
  PART_SIZE-sweep, so V_C<200 substrate probing has partial existing coverage
  through the PART_SIZE-axis.
- 2x V_C range (200 -> 400) still tests PART_SIZE-limited-cleanup hypothesis
  (per_step invariant under fixed PART_SIZE, varying V_C).
- Feasibility asserts added at module init:
  - `N_CHAINS <= vc` for every vc in V_C_VALUES (start-set constraint)
  - `vc > MAX_DEPTH` for every vc (per-chain successor uniqueness)
  - `vc % PART_SIZE == 0` (partition arity)

## Config (MEASURED@ cell module init, LOCKED at import)

| Field | Value |
|-------|-------|
| N_DIM_FIXED | 8192 |
| V_C_VALUES | [200, 400] |
| PART_SIZE_FIXED | 10 |
| MAX_DEPTH | 30 |
| DEPTHS | [15, 30] |
| N_CHAINS (FULL) | 200 |
| N_CHAINS_LOCAL (smoke) | 30 |
| SEEDS (FULL) | [7, 13, 19] |
| SEEDS (smoke) | [7] |
| EXPECTED_N_UNITS | 3 (FULL) / 1 (smoke) |
| ARMS_PER_SEED | 4 |
| CRLB_FLOOR (constant per PART_SIZE=10) | 0.10 |
| REF_15HOP (parent atom REF at V_C=200) | 0.858 |
| REF_30HOP (parent atom REF at V_C=200) | 0.682 |
| HP_TOL | 0.05 |
| HF_TOL | 0.10 |
| DEATH_FLOOR | 0.10 |
| CV_CAP | 0.10 |

REF values MEASURED@ parent + ceiling cells 2026-06-27 (see cell docstring
lines 23-30 for exact source metrics.json paths and per-seed values).

## Envelope-fail bands (per-arm)

- **HP** (per arm): `|per_step_mean - REF| <= 0.05` AND `cv_across_seeds <= 0.10`
- **HF_SCALE_VARIANCE** (per arm; full only): `|per_step_mean - REF| > 0.10`
- **HF_MECHANISM_DEATH** (per arm, any mode): `top1_min < 0.10`
- **HARD_FAIL_CARDINALITY_BREACH_META_RULE_H**: `observed_n_units < EXPECTED_N_UNITS`

## Verdict tiers

- **CHAIN_GRADE_SCALE_INVARIANT_VC_AXIS**: all 4 arms HP
- **PARTIAL_SCALE_INVARIANT_D15_ONLY**: both d=15 HP; d=30 mixed
- **PARTIAL_SCALE_INVARIANT_D30_ONLY**: both d=30 HP; d=15 mixed
- **PARTIAL_SCALE_INVARIANT_MIDDLE_VC_ONLY**: V_C=200 arms HP; V_C=400 not (rail failure)
- **SCALE_VARIANT_VC_AXIS**: HF_SCALE_VARIANCE fires anywhere
- **MECHANISM_DEATH**: HF_MECHANISM_DEATH fires anywhere
- **MIDDLE_BAND**: partial HP without clean sub-pattern

## HP_SCOPE per-arm

All 4 arms (arm_d15_vc200, arm_d30_vc200, arm_d15_vc400, arm_d30_vc400) share
the same HP gates (`|per_step - ref_depth| <= 0.05`, `cv <= 0.10`). ref_depth
is REF_15HOP for d=15 arms, REF_30HOP for d=30 arms.

## META_RULE compliance

| Rule | Status | Field / Evidence |
|------|--------|------------------|
| H (cardinality_ok) | PASS | `EXPECTED_N_UNITS = len(SEEDS) = 3`; verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if `len(per_seed) < EXPECTED_N_UNITS` |
| J (failure-class instrumentation) | PASS | `_write_crash_metrics` writes `CELL_CRASHED` + type + traceback on outer Exception; `except SystemExit: raise` FIRST |
| K (discriminator-fires) | PASS | Reproducer arm at V_C=200 tracks parent REF; ARMS-MUST-DIFFER hash asserts arms produce distinct per_step vectors |
| L (strict-above-floor) | PASS | HP band `|diff| <= 0.05` is centered on REF (both sides bounded); not at-floor |
| M (calibration-check) | `default_ok_for_this_regime` | Parent CG data at V_C=200 PS=10 is exact regime of reproducer arm |
| AC (MEASURED/HYPOTHESIZED tagging) | PASS | REFs tagged MEASURED@ parent atoms; crash tagged MEASURED@ Wave 18 dispatch; feasibility analysis tagged THEORETICAL@ code |
| AF (arms-must-differ) | PASS | `_arms_must_differ` hash-test at each seed; `arms_differ_verified: True` in metrics |
| AG (baseline-in-band) | PASS | REF 0.68-0.86 sits inside (0.05, 0.95); mechanism arm at REF is in-band by design |
| AH (atomic metrics write) | `tmp_replace` | `write_metrics` uses tmp+os.replace; `_write_crash_metrics` uses tmp+os.replace |
| §8 (SystemExit ordering) | PASS | Outer try/except in `__main__` orders `SystemExit -> KeyboardInterrupt -> Exception` |
| §9 (CRLB) | PASS | `crlb_floor_per_vc: 0.10` for all V_C; HP band `REF+/-0.05` far above floor; `discriminator_reachability: True` |
| §13 (chunked + start-marker + crash-diag + heartbeat) | PARTIAL | multi-seed but not chunked (3 seeds in single cell); start_marker + crash_diagnostic present; no explicit heartbeat (elapsed_s printed per arm as progress) |
| §15A (effective params) | ALIGNED | swept param V_C = effective V_C in `arm_part_oracle_at_depth` (E_effective.shape[0] == V_C for that arm); no partition-oracle drift |
| §15B (discriminating band) | PASS | Both REFs (0.858, 0.682) fall in discriminating band (0.30, 0.90); 4/4 arms in band by design |
| §15C (composition edges) | N/A | single primitive (partition-oracle cleanup); no cross-primitive composition |
| §15D (positive control) | PASS | ARM_D15_VC200 and ARM_D30_VC200 ARE the positive-control reproducer arms (parent regime) |
| §15E (functional requirements) | PASS | one functional requirement: per-hop cleanup accuracy invariant under vocabulary size at fixed local-arity; mapped to partition-oracle primitive (chain-grade) |
| §16 (run_mode verification) | PASS | RUN_MODE derived from `--smoke` / `--self-test` / env `HDLAB_RUN_MODE` / anchor name; smoke = SEEDS=[7], N_CHAINS_LOCAL=30 -> distinct from full |
| §17 (print-progress flushing) | PASS | all `print(..., flush=True)`; per-arm and per-V_C progress lines; `sys.stdout.reconfigure` at file top |

## Discriminator-must-survive-scale

- **Choice (C):** discriminator-preview arm at full-N=8192 in smoke.
- Smoke runs SEEDS=[7], N_CHAINS_LOCAL=30 at N=8192 full-dim. This DOES exercise
  the substrate at production N and V_C values; only N_CHAINS is reduced (30 vs
  200) because full-N chain construction is time-dominated by per-seed cost.
- v2 smoke should demonstrate that the mechanism operates end-to-end at V_C=200
  and V_C=400 at full N=8192; the per-step accuracy will be NOISIER at N_CHAINS=30
  but non-zero at all 4 arms if the mechanism is alive.
- HF_SCALE_VARIANCE gate is DISABLED in smoke mode (per code, lines 730-746): the
  noise ceiling from N_CHAINS=30 vs N_CHAINS=200 could inflate |diff| above HF_TOL
  as a smoke-artifact; full mode gates the scientific claim.

## Runtime budget

- FULL (per seed): ~2 min per (V_C, depth) arm at N=8192 on GPU; 4 arms per seed;
  building W once per V_C; ~10 min per seed; 3 seeds serial = ~30 min end-to-end.
  Timeout: 3600s (1h; 2x safety margin).
- SMOKE (1 seed x N_CHAINS=30): ~1-3 min end-to-end. Timeout: 900s.

## Route

- SMOKE: local_cpu_queue (USER-locked 2026-07-01: smoke only on local; USER laptop
  stays available). Verify SMOKE_PASS at all 4 arms + arms-differ verified.
- FULL: overnight_queue via Orchestrator (GPU idle NOW; USER-flagged). Push +
  queue_add authored by Orchestrator (exp_dev harness-DENIED push).

## Failure-mode audit (v1 crash + regression checks)

- Chain-construction feasibility asserted at module init (`N_CHAINS <= vc` per V_C).
- If any future author bumps N_CHAINS above 200, they'll hit the assert BEFORE
  build if V_C is unchanged. Regression-safe against v1-class start-set exhaustion.
- If future author adds V_C < N_CHAINS, module import fails deterministically.

## Novelty

Substrate-KB concept-check 2026-07-01 for "multihop V_C vocabulary scale invariance
chain cleanup drop arm" returned top hits at cosine=0.264 (below 0.30 novelty
threshold), same as v1's original prior-work check. This is a bug-fix iteration
of already-novel v1 design; novelty verdict stands.
