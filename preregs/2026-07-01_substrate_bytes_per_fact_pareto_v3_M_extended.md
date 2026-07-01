# Pre-reg: substrate_bytes_per_fact_pareto_v3 (M-extended + FP16 range-fix)

**Date:** 2026-07-01
**Author:** hdi_exp_dev (spawned by research)
**Base cell:** commit `f9dd8c15` bytes_per_fact_pareto v2 (7 arms x 4 M-values)
**Skunkworks v2 audit:** commit `c7feb0c4` tiered v2 MIDDLE_BAND (override from HP);
21/28 cells at recall=1.000 (META_RULE_Q trip); FP16_DENSE arm=0.0 all M/all seeds.
**Anchor:** `substrate_bytes_per_fact_pareto_v3_seed_{7,13,19}`

## Why v3

Two v2 failure modes the auditor caught:
1. **META_RULE_Q ceiling saturation.** 21/28 (75%) of (arm, M) cells landed at
   recall=1.000. Discrimination is lost to the substrate ceiling. Auditor
   correctly demoted to MIDDLE_BAND. MM->CG lift requires extending M to
   force at least a subset of arms below the ceiling.
2. **FP16_DENSE all-zero collapse.** v2 confirmed the collapse hypothesis:
   BFLOAT16 stayed at 1.000 at all M while FP16 collapsed to 0.0 at all M.
   Since BFLOAT16 and FP16 have identical storage cost (2 bytes/elem) but
   different exponent widths (bf16=8 like fp32; fp16=5), the FP16 collapse
   is a RANGE issue in the Hebbian accumulator, not a precision issue.

## v3 changes

### Change 1: FP16 range-fix (structural)

Replace `FP16_DENSE` arm with `FP16_DENSE_RANGE_SAFE`:
- Accumulate Hebbian W in FP32 (transient build-time cost, not counted in
  bytes-per-fact denominator).
- Downcast W to FP16 for STORAGE (2 bytes/elem: same as v2 FP16 accounting).
- Rematerialize FP32 for readout (models real inference: dequant on load).

**Prediction:** FP16_range_safe recall should track BFLOAT16 within noise
(both are 2-byte/elem representations; only the accumulator is fixed).

**Bytes-per-fact accounting:** unchanged from v2 FP16 (2 bytes/elem for W, E, R).
The FP32 accumulator is transient; it is a build-time compute artifact, not a
storage cost that would ship in a deployed KG substrate.

### Change 2: M sweep extended (discrimination)

`FULL_M_SWEEP = [1000, 4000, 10000, 20000, 40000]` (v2 was 4-item; v3 adds
M=40000). At N=4096, Hopfield capacity ~= 0.14*N = 573 items; M=40k is 70x
overload. Expect ordering (crack-M) to be:
- BINARY_DENSE holds longest (v2 showed 0.9995 at M=20000)
- INT8, INT4 hold near BINARY (per-row scaling preserves sign structure)
- BFLOAT16, FP16_range_safe crack somewhere between M=20k and M=40k
- SPARSE_BIPOLAR_0p05 collapses first (v2 showed 0.83 at M=4000, 0.07 at M=20k)

Cardinality: 7 arms x 5 M-values = **35 units per seed** (v2 was 28).

### Change 3: META_RULE_Q strict gate in verdict logic

`ceiling_saturation_ratio = (# cells with recall >= 0.995) / total_cells`.
Auto-demote HP -> MIDDLE_BAND if ratio >= 0.70. Payload includes
`per_arm_top_M_recall` (visible crack pattern for auditor).

## Discriminator (HARD_PASS gates)

1. Positive control: FP32 recall @ M=4000 >= 0.85 (META_RULE_BC).
2. Pareto separation within each M (>=1 arm-pair differs by 2x bytes or 0.05 recall).
3. Monotonic recall decay per precision as M grows.
4. **FP16_range_safe recall >= 0.5 @ M=4000** (v3-specific: RANGE-fix rescues FP16).
5. INT4 recall >= 0.85 @ M=4000 (positive tier finding preserved).
6. Cross-seed cv <= 0.15.
7. All 7 mechanism_hash distinct.
8. Cardinality: 7 * 5 = 35 units per seed.
9. **META_RULE_Q strict: ceiling_saturation_ratio < 0.70.**

## Envelope

- **HARD_PASS:** all 9 gates. Requires discrimination through saturation.
  Emit `per_arm_top_M_recall` in payload so auditor sees the crack ordering.
- **MIDDLE_BAND:** ceiling_saturation_ratio >= 0.70 (still no discrimination),
  OR FP16_range_safe still collapses (range fix insufficient), OR INT4
  below 0.85 tier, OR pareto separation lost. Explicit META_RULE_Q message
  when saturation is the trip.
- **HARD_FAIL:** positive control breaks OR cardinality breach.

## Smoke gate (before full dispatch)

Smoke M sweep: `[500, 2000, 8000]` (n_ent=800, n_rel=50; max feasible M=40k
under unique-(s,p)). Smoke N_DIM_DENSE=2048, N_DIM_SPARSE=8192.

**Smoke ship criterion (v3-specific):** at smoke's top M (M=8000, N_DIM=2048),
at least 3/7 arms must land below recall=0.85. If smoke shows all-arms at
1.000 across all M, ABORT — the ceiling extended with N=2048 too, and full
dispatch will just repeat v2's ceiling-saturation MIDDLE_BAND. Consider
scaling n_ent further or dropping N_DIM.

Additionally FP16_range_safe smoke recall @ M=2000 >= 0.5 (verifies the range
fix works before spending full-run compute).

## Ship

- CPU-eligible (numpy + torch cpu OK).
- Dispatch to `remote_cpu_queue` via `hdi_orchestrator` (harness push-DENY).
- 3 seeds (7, 13, 19) chunked per file (independent per-seed cardinality).
- Timeout per formula: v2 seed_13 took ~O(minutes) at 28 units; v3 adds one
  M-tier (+25% units) plus M=40k is 2x the top-M work of M=20k. Estimate
  per-seed wall <= 40 min at N=4096; use `--timeout 3600s` per seed as slack.

## ASCII-only

No emoji, no em-dashes, no unicode. Author asserts.
