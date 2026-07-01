# Pre-reg: multihop_reasoning_scale_invariance_N_axis_gpu_v1

**Date:** 2026-07-01
**Cell:** experiments/exp_multihop_reasoning_scale_invariance_N_axis_gpu_v1.py
**Anchor:** multihop_reasoning_scale_invariance_N_axis_gpu_v1
**Parents:**
- Cell: exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1 (Landing 6 family)
- Cell: exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1 (Landing 10 family)
- Prereg: preregs/2026-06-26_phase_diagram_multihop_depth_extension_via_partition_oracle_v1.md
**Author role:** hdi_exp_dev (via Director spawn 2026-07-01)
**Prior-work check:** substrate-KB query returned rank-1 hit (cosine 0.292) on parent prereg
`phase_diagram_multihop_depth_extension_via_partition_oracle_v1` — same anchor family. This
cell is a **direct N-axis extension**, not novel; the load-bearing primitive (partition-oracle
per-hop cleanup) is the same. Novelty = varying substrate N dimensionality while holding all
other regime parameters fixed to test scale-invariance of the per-step accuracy.

---

## Purpose / hypothesis

Atom 11 (Skunkworks 2026-07-01, MM_STANDARD) claims per-step accuracy of partition-oracle
multihop is invariant across depths d=15-60 at fixed N=8192, PART_SIZE=10. To LIFT this to
CHAIN_GRADE, Skunkworks requires expansion via ONE of:

- (a) different **N** at same PART_SIZE
- (b) different PART_SIZE
- (c) extended depth

This cell chose (a): sweep N ∈ {4096, 8192-implicit-via-parent, 16384} at fixed PART_SIZE=10.

**Hypothesis (LOAD-BEARING):** partition-oracle per-hop cleanup accuracy is invariant to
substrate N in the regime N ∈ [4096, 16384] at fixed (V_C=200, PART_SIZE=10, K_set=20,
n_partitions=20, n_chains=200). If per-step accuracy at (N=4096, d=15) and (N=16384, d=15)
matches (N=8192, d=15) within ± 0.05, and same at d=30, this is substrate-physics-strength
scale-invariance evidence for the CG lift.

## HYPOTHESIZED vs MEASURED discipline (META_RULE_AC)

The spawn prompt cited "Atom 11 MM_STANDARD: per-step accuracy 0.9853 ± 0.0016 across d=15-60
at fixed N=8192, PART_SIZE=10". Off-disk audit (2026-07-01 by cell-author) found:

- MEASURED@data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json
  per-seed arm_part_oracle_15hop.per_step_acc mean = **0.858 ± 0.05** (not 0.9853); top1 mean = 0.808
- MEASURED@data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json
  d=30 per-step mean = **0.682 ± 0.09**; d=15 per-step mean = 0.858 (matches extension cell)
- MEASURED@data/exp_phase_diagram_multihop_depth_at_production_V_C_2000_v1/metrics.json
  per-step mean = **0.976 ± 0.014** at V_C=2000, **PART_SIZE=100** (different regime)

The 0.9853 figure most closely matches the PART_SIZE=100 regime, NOT PART_SIZE=10 (the
regime the spawn prompt says was tested and the regime this cell inherits). Prereg bands
below use the **measured** PART_SIZE=10 references (0.858 at d=15; 0.682 at d=30), tagged
MEASURED@ per META_RULE_AC. Discrepancy flagged in completion report for Director/Skunkworks
resolution.

## Cell design

### Substrate config (holds fixed across arms)
- V_C = 200 (concepts)
- V_P = 10 (predicates)
- K_set = 20 (bindings per cue)
- N_PARTITIONS = 20 -> PART_SIZE = 10 (V_C / N_PARTITIONS; per Atom 11 fixed regime)
- n_chains = 200
- Encoder = bipolar substrate-native (E, R on cuda; row-normalized)
- Binding = elementwise product; scale sqrt(N); Hebbian outer-product ingest

### N axis (the sweep)
- N ∈ {4096, 16384}  (N=8192 is the parent reference, NOT re-run in this cell)

### Arms (4)
- `ARM_PART_ORACLE_15HOP_N4096`: partition-oracle per-hop at d=15, N=4096
- `ARM_PART_ORACLE_30HOP_N4096`: partition-oracle per-hop at d=30, N=4096
- `ARM_PART_ORACLE_15HOP_N16384`: partition-oracle per-hop at d=15, N=16384
- `ARM_PART_ORACLE_30HOP_N16384`: partition-oracle per-hop at d=30, N=16384

Chains built once per (seed, N) using make_deep_chains at max_depth=30; both d=15 and d=30
arms reuse the same chain set (d=15 = chains[:15] slice of d=30 chains). This mirrors parent's
W_pointer_v2 shared-W convention.

### Seeds
[7, 13, 19] — 3 seeds per arm.

### Verdict gates (LOCKED at module init; META_RULE_L strictly-above-floor applied)

**Reference values (all MEASURED @ N=8192, PART_SIZE=10):**
- d=15 per-step mean: 0.858 (cv 0.058)  -> reference from parent extension cell + ceiling cell (agree)
- d=30 per-step mean: 0.682 (cv 0.131)  -> reference from ceiling cell

**HP_SCALE_INVARIANCE_N_AXIS_15HOP** (per-N; each of 4096/16384 evaluated separately):
- HARD_PASS iff |per_step_mean(N, d=15) - 0.858| <= 0.05  AND  cv_across_seeds <= 0.10

**HP_SCALE_INVARIANCE_N_AXIS_30HOP** (per-N; each of 4096/16384):
- HARD_PASS iff |per_step_mean(N, d=30) - 0.682| <= 0.05  AND  cv_across_seeds <= 0.10

**HF_SCALE_VARIANCE_15HOP** (either N):
- HARD_FAIL iff |per_step_mean(N, d=15) - 0.858| > 0.10 (violates scale-invariance claim)

**HF_SCALE_VARIANCE_30HOP** (either N):
- HARD_FAIL iff |per_step_mean(N, d=30) - 0.682| > 0.10

**HF_MECHANISM_DEATH** (any arm):
- HARD_FAIL iff top1 < 0.10 at any (N, d) arm  (primitive broken)

### Verdicts
- `CHAIN_GRADE_SCALE_INVARIANT_N_AXIS`: all 4 arms HP (both Ns × both depths within 0.05)
- `PARTIAL_SCALE_INVARIANT_D15_ONLY`: N-invariance holds at d=15 but breaks at d=30
- `PARTIAL_SCALE_INVARIANT_D30_ONLY`: N-invariance holds at d=30 but breaks at d=15 (unlikely)
- `SCALE_VARIANT_N_AXIS`: any HF_SCALE_VARIANCE_* fires
- `MECHANISM_DEATH`: any HF_MECHANISM_DEATH
- `MIDDLE_BAND`: mixed HP + non-HF (middle band; inconclusive)

### HP_SCOPE (per-arm scope declaration, META_RULE_L addendum)
```
HP_SCALE_INVARIANCE_N_AXIS_15HOP: [ARM_PART_ORACLE_15HOP_N4096, ARM_PART_ORACLE_15HOP_N16384]
HP_SCALE_INVARIANCE_N_AXIS_30HOP: [ARM_PART_ORACLE_30HOP_N4096, ARM_PART_ORACLE_30HOP_N16384]
HF_MECHANISM_DEATH: [ALL]
```

### CARDINALITY_OK (META_RULE_H)
- EXPECTED_N_UNITS = 4 arms x 3 seeds = 12 units (full)
- Smoke EXPECTED_N_UNITS = 4 arms x 1 seed = 4 units
- Verdict logic counts observed unit records; emit `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`
  if observed < expected.

### DISCRIMINATOR_SURVIVES_SCALE
- Smoke design (option A + preview): smoke runs 1 seed at N=4096 d=15/30 AND N=16384 d=15/30.
  Discriminator = |per_step - reference| stability. If smoke at full-N shows deviation > 0.15
  from reference, ABORT full dispatch.
- Baseline reference (N=8192) is not re-run in this cell; parent metrics are the reference.

### GPU memory budget check (MEASURED@ formula THEORETICAL)
- W (fp32) at N=4096: 4096^2 * 4 = 67 MB per W  -> 1 W for d=30 chains = 67 MB
- W (fp32) at N=16384: 16384^2 * 4 = 1073 MB per W  -> 1 W for d=30 chains = 1.07 GB
- E (V_C=200, N): 200*N*4 = 3.3MB (N=4096) / 13MB (N=16384)
- R (V_P=10, N): 0.16MB (N=4096) / 0.65MB (N=16384)
- Attention W @ key: batched to bounded; ~200 * N * 4 bytes = trivial
- Peak per seed at N=16384: ~1.1 GB (single W + E + R + workspace) -> **fits 8GB VRAM comfortably**
- Only one W built per (seed, N) — depth=30 W covers both d=15 and d=30 arms.

### CELL-TEMPLATE MANDATES compliance (META_RULE_AC/AF/AG/AH + scope/scale/floor)
- arms_differ_verified: **True** (each arm's per-step tensor hashed at smoke gate; per-N and
  per-depth arms are structurally different due to different W dimensionality N; d=15 vs d=30
  differ in per_step_acc list length so bit-identity impossible)
- final_metrics_atomicity: **tmp_replace** (write_metrics uses tmp+os.replace via _seed_checkpoint)
- except SystemExit: raise BEFORE except Exception (in main outer-try): **True**
- crlb_floor_computed: **n/a** (no quantitative CRLB applies; per-step accuracy is empirical
  measurement of partition-oracle primitive; no Gaussian noise floor)
- crlb_n/a: "partition-oracle uses argmax over partition-restricted slice (200/20=10 candidates);
  argmax-noise floor is ~1/10=0.10 which is far below the ~0.86 measured; no CRLB constraint"
- baseline_in_band: **True** (partition-oracle per-step ~0.86 at d=15 IS the mechanism arm; no
  separate baseline; reference is prior CG data at N=8192, and the reference values are IN band
  0.05 < ref < 0.95 for both d=15 (0.858) and d=30 (0.682))
- discriminator survives scale: smoke at full-N (4096 + 16384) preview arm confirms
- HARD_PASS strictly above floor + 5% band-width: HP band is ± 0.05 window around measured
  reference; HF band is ± 0.10 window; 5% margin implicit in the strict-tolerance design
- HP_SCOPE declared per-arm above
- cardinality_ok: EXPECTED_N_UNITS declared; verdict emits BREACH sentinel
- per-unit failure-class instrumentation: try/except Exception (no bare/BaseException);
  crash writes CELL_CRASHED metrics + traceback via inline _write_crash_metrics helper
- calibration_check: **default_ok_for_this_regime** (V_C=200, K=20, n_chains=200, N_PART=20
  IS the load-bearing regime tested by parent cells; no adaptation needed)
- All numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

### Defensive error-checking (META_RULE #13)
- cell_chunked: **False** (single script; 3 seeds sequential; total wall ~3-15 min; runner-zombie
  risk low)
- start_marker_written: **True** (writes `_start_marker.json` at main() entry)
- crash_diagnostic_present: **True** (Exception → CELL_CRASHED metrics.json + traceback)
- heartbeat_present: **True** (uses experiments._cell_heartbeat.CellHeartbeat)
- defensive_error_checking: **passed_all_4_patterns**

### TEST-DESIGN gates (META_RULE §15)
- sweep_alignment_verdict: **ALIGNED** — sweep axis = substrate N_DIM; primitives experiencing
  effective N: all primitives use W at exactly the swept N (no intermediate downscaling); the
  per-step accuracy measurement directly depends on N via Hebbian binding fidelity ∝ 1/sqrt(N)
  after normalization
- discriminating_fraction: **1.00** (2/2 sweep points N ∈ {4096, 16384}; substrate physics
  predicts N-dependence in binding fidelity; smaller N = more crosstalk; larger N = less;
  either both points land in same band (invariance CG) or divergent (scale-variant tiering))
- composition_edges: [E->R->W (Hebbian bind); W@key->argmax (retrieval); argmax->target_part
  slice (oracle route)] all SHAPE_MATCH (all operate on N-dimensional tensors; no adapter needed)
- positive_control_arms: N/A because there IS no matched-regime prior CG data for N ∈
  {4096, 16384} at PART_SIZE=10; this cell IS the positive-control-generation step. Reference =
  N=8192 parent metrics used only as the invariance TARGET, not as reproducibility rail
  (would be circular since N is the swept axis).
- functional_requirements:
  1. Encode entities into HD bipolar codes (met by bipolar_gpu primitive; CG per numerous atoms)
  2. Bind (entity, relation, next-entity) triples into a Hebbian W (met by ingest_hebbian_gpu;
     CG per Cell B v2 depth=5 partition-oracle atom)
  3. Retrieve next-entity per-hop by cleanup argmax against W@(prev*rel*sq) (met by CG
     partition_oracle primitive)
  4. Route argmax to target partition slice (oracle; CG via parent partition_oracle_v5 hardened)
  5. Iterate d times; compute per-step and top1 accuracy (met by arm_part_oracle_at_depth)
  All 5 functional requirements map to existing chain-grade primitives; no novel mechanism.

### Cross-references
- Atom 11 MM_STANDARD (Skunkworks 2026-07-01) — the atom this cell aims to lift to CG
- Landing 6 = ceiling sweep 20-25-30 v1 (CHAIN_GRADE_DEPTH_CEILING_30) at N=8192, PART_SIZE=10
- Landing 10 = phase diagram partition-oracle extension v1 (CHAIN_GRADE_DEPTH_EXTENDS) at
  N=8192, PART_SIZE=10 (Note: naming per spawn prompt; actual landing labels TBD by Director)

## Dispatch plan
- Smoke: local_cpu_queue (SMOKE ONLY per USER-locked 2026-07-01), 1 seed, N=4096 + N=16384
  both, d=15 + d=30 both, chains n=30, timeout=1800s
- Full: overnight_queue via Orchestrator handoff (Director dispatches; harness-DENIED to me),
  3 seeds × 4 arms = 12 units, timeout=3600s

## Timeout formulas
- Smoke wall ~ N=4096: ~5s (67 MB W); N=16384: ~30s (1 GB W); serialized 2 Ns * 2 depths * 1 seed ~ 60s + overhead
- Smoke timeout: 1800s (30 min; generous)
- Full wall: 3 seeds * (4096-wall + 16384-wall) ~ 3 * (30 + 90) ~ 6 min per GPU
- Full timeout: 3600s (1 hr; 6x margin)

## References for HP band derivation

- MEASURED@d:/AI/hd-instrument/data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json:per_seed.arm_part_oracle_15hop.per_step_acc: 3 seeds × 15 steps = 45 values, mean 0.850, stdev 0.054
- MEASURED@d:/AI/hd-instrument/data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json:per_seed.arm_part_oracle_15hop.per_step_acc: 3 seeds × 15 steps = 45 values, mean 0.858, stdev 0.050 (pooled with above: 0.854)
- MEASURED@d:/AI/hd-instrument/data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json:per_seed.arm_part_oracle_30hop.per_step_acc: 3 seeds × 30 steps = 90 values, mean 0.682, stdev 0.090

Reference bands used:
- d=15 reference: 0.858 (rounded 0.86) — the CENTER of HP band
- d=30 reference: 0.682 (rounded 0.68) — the CENTER of HP band
- HP tolerance: ± 0.05 (roughly 1x reference stdev)
- HF threshold: ± 0.10 (roughly 2x reference stdev; catches non-invariance)

## Success criteria for CG lift on Atom 11
- If ALL 4 arms HARD_PASS AND cv_across_seeds ≤ 0.10 for each -> CHAIN_GRADE_SCALE_INVARIANT_N_AXIS
- Combined with parent's Landing 6+10 data, this gives 3 N values × 2 depths = 6 independent
  data points supporting the "per-step accuracy is invariant to substrate physics parameters
  in this regime" claim → Atom 11 lifts from MM_STANDARD to CHAIN_GRADE

## Failure modes and interpretation
- CHAIN_GRADE_SCALE_INVARIANT_N_AXIS: substrate physics genuinely N-invariant here; CG lift on Atom 11
- SCALE_VARIANT_N_AXIS: substrate physics N-dependent; Atom 11 stays MM_STANDARD; need to
  narrow the regime to specific N range
- MECHANISM_DEATH at N=4096: capacity-pressure crossed; partition-oracle fails when W is too small
- MIDDLE_BAND: inconclusive; may need cv-tightening or more seeds

## LLM-forward-call assertion
- _LLM_CALL_COUNTER[0] == 0 at cell exit (substrate-only; zero LLM inference)

---
**Author:** hdi_exp_dev sub-agent, 2026-07-01
**Dispatch route:** local_cpu_queue smoke → overnight_queue full (Director dispatches full)
