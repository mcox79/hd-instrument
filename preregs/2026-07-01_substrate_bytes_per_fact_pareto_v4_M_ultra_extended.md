# Pre-reg: substrate_bytes_per_fact_pareto_v4 (M-ultra-extended, N=2048)

**Date:** 2026-07-01
**Author:** hdi_exp_dev (spawned by research)
**Base cell:** commit `225cfd78` bytes_per_fact_pareto v3 (7 arms x 5 M-values,
N_DIM_DENSE=4096; FP16_range_safe validated at 0.98 recall at M=40k).
**Skunkworks v3 audit:** commit `3197b903` tiered v3 MIDDLE_BAND (META_RULE_Q
trip); ceiling_saturation_ratio=0.7143 all three seeds; recommendation:
extend M further so more arms escape the 0.98 ceiling.
**Anchor:** `substrate_bytes_per_fact_pareto_v4_seed_{7,13,19}`

## Why v4

v3 discharged the FP16 range hypothesis (FP16_range_safe = 0.98 at M=40k
matching BFLOAT16 within noise) but the discriminator itself remained
saturated: 25/35 (71.4%) cells at recall >= 0.995, tripping META_RULE_Q
strict and locking the cell at MIDDLE_BAND. For MM -> CG lift, we must push
the top-M until a substantial subset of arms (>=3/7 target) fall below
the 0.85 recall band at top-M so per-arm crack-point ordering becomes the
Pareto-informative signal.

## v4 changes

### Change 1: M sweep further extended

v3: `[1000, 4000, 10000, 20000, 40000]` (5 M-values).
v4: `[1000, 4000, 10000, 40000, 80000, 160000]` (6 M-values).

Drop interior M=20000 (redundant with 10k and 40k for crack-detection) and
add M=80000 + M=160000 as ceiling-escape points. Cardinality: 7 arms x 6 M
= **42 units per seed** (v3 was 35).

At N=2048, Hopfield capacity ~= 0.14 * N = 287 items:
- M=80k  is 279x overload (BINARY typically holds through here)
- M=160k is 558x overload (even BINARY should crack)

Expected crack-point ordering (informational; not a gate):
- SPARSE_BIPOLAR_0p05 cracks first (M<=10k; v3 showed 0.07 at M=40k)
- FP32, BFLOAT16, FP16_range_safe crack around M=40k-80k
- INT8, INT4 crack around M=80k
- BINARY_DENSE holds longest, cracks at M=160k

### Change 2: N_DIM_DENSE 4096 -> 2048; N_DIM_SPARSE 16384 -> 8192

Compute + memory rationale:
- FP32 dense W at N=4096 M=160k queries: batched keys become expensive on
  laptop-scale CPU (~4x per M-step).
- N=2048 W matrix = 16.8 MB FP32 (vs 67.1 MB at N=4096). Comfortable margin.
- N=2048 keeps Hopfield capacity substantive (287 items) while making the
  M=558x overload discriminator tractable.
- SPARSE arm N=8192 preserves 4x dense/sparse ratio (v3 disciplinar).

### Change 3: META_RULE_Q strict gate retained

`ceiling_saturation_ratio = (# cells with recall >= 0.995) / total_cells`.
Auto-demote HP -> MIDDLE_BAND if ratio >= 0.70. Emit `per_arm_top_M_recall`
so auditor sees which arms cracked and where.

**v4 target:** with M=160k = 558x overload at N=2048, expect ceiling ratio
to fall to ~0.30-0.50 (roughly BFLOAT16 + FP16_rs + INT8 + INT4 hold at
low-M; BINARY may hold across all M; SPARSE + high-M cells crack).

## Discriminator (HARD_PASS gates; unchanged from v3)

1. Positive control: FP32 recall @ M=4000 >= 0.85 (META_RULE_BC).
2. Pareto separation within each M (>=1 arm-pair differs by 2x bytes or 0.05 recall).
3. Monotonic recall decay per precision as M grows.
4. FP16_range_safe recall >= 0.5 @ M=4000 (v3-carry).
5. INT4 recall >= 0.85 @ M=4000 (positive tier).
6. Cross-seed cv <= 0.15.
7. All 7 mechanism_hash distinct.
8. Cardinality: 7 * 6 = 42 units per seed.
9. **META_RULE_Q strict: ceiling_saturation_ratio < 0.70** (v4 escape target).

## Envelope

- **HARD_PASS:** all 9 gates. MM -> CG lift achieved via per-arm crack-point
  discrimination through M=160k. Emit `per_arm_top_M_recall` for auditor.
- **MIDDLE_BAND:** ceiling_saturation_ratio still >= 0.70 (M=160k insufficient
  at N=2048; needs even more M or smaller N). Also MB on any of: FP16_rs
  regression, INT4 tier collapse, cv breach, hash collision, pareto lost.
- **HARD_FAIL:** positive control breaks OR cardinality breach.
- **ESCALATION:** if smoke at M=20k with N=1024 still shows all arms at
  recall=1.000, escalate FULL M to M=320000 (require pre-reg amendment).

## Smoke gate (before full dispatch)

Smoke M sweep: `[500, 2000, 8000, 20000]` (n_ent=800, n_rel=50; max feasible
unique-(s,p) = 40000). Smoke N_DIM_DENSE=1024, N_DIM_SPARSE=4096.
Smoke Hopfield capacity ~= 0.14 * 1024 = 143 items; M=20k is 139x overload
(analogous to full M=160k at N=2048 in overload-multiple terms).

**Smoke ship criteria (v4-specific):**
- At smoke's top M (M=20k, N_DIM=1024), at least **3/7 arms below recall=0.85**.
  If smoke shows all-arms >=0.85 at M=20k, ABORT and escalate to M=320k FULL
  or drop N=1024 further at smoke.
- FP16_range_safe smoke recall @ M=2000 >= 0.5 (verify range-fix carries).
- Positive control: FP32 recall @ M=2000 (smoke's ~M=4000 nominal) >= 0.85.

## Ship

- CPU-eligible (numpy + torch cpu OK). Memory: N=2048 FP32 W = 16.8 MB;
  M=160k triples = 3.8 MB; batch keys = 16.4 MB. Well within laptop RAM.
- Dispatch to `remote_cpu_queue` via `hdi_orchestrator` (harness push-DENY).
- 3 seeds (7, 13, 19) chunked per file (independent per-seed cardinality).
- Timeout per formula: v3 seed_13 took ~30 min at N=4096 with 35 units;
  v4 has 42 units at N=2048 (0.25x per-unit compute) so per-seed wall ~10-15
  min. Use `--timeout 3600s` per seed as slack (matches v3 pre-reg).

## Cross-seed cv check

Post-full: `tools/peek_arm_metrics.py exp_substrate_bytes_per_fact_pareto_v4_seed_*`
should show:
- Recall CV <= 0.15 at each (arm, M) cell
- Bytes-per-fact CV <= 0.15 (deterministic per config; expect ~0)

## ASCII-only

No emoji, no em-dashes, no unicode. Author asserts.
