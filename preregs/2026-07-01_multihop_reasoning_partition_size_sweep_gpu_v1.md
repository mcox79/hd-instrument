# Pre-reg: multihop_reasoning_partition_size_sweep_gpu_v1

**Date:** 2026-07-01
**Cell:** experiments/exp_multihop_reasoning_partition_size_sweep_gpu_v1.py
**Anchor:** multihop_reasoning_partition_size_sweep_gpu_v1
**Parents:**
- Cell: exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1 (Landing 6 family)
- Cell: exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1 (Landing 10 family)
- Sibling: exp_multihop_reasoning_scale_invariance_N_axis_gpu_v1 (CG-expansion axis (a); N-axis)
- Prereg: preregs/2026-07-01_multihop_reasoning_scale_invariance_N_axis_gpu_v1.md
**Author role:** hdi_exp_dev (via Director spawn 2026-07-01)

**Prior-work check (substrate-KB concept-query 2026-07-01, exp_dev on spawn, BOTH queries):**
- Q1 "multihop reasoning PART_SIZE 5 20 partition oracle per step accuracy": rank-1 cosine 0.30
  on parent prereg `phase_diagram_multihop_depth_extension_via_partition_oracle_v1` (same anchor
  family; PART_SIZE=10 lineage). No prior cell varies PART_SIZE at fixed N=8192.
- Q2 "multihop different partition size N=8192 scale invariance": rank-1 cosine 0.30 on
  scale-invariant-differentiators note; no matching operational cell.
- Rediscovery-vs-novel: this cell is GENUINELY NEW along the PART_SIZE axis. Reproducer arm
  at PART_SIZE=10 must reproduce parent REFs (0.858 at d=15, 0.682 at d=30) as internal
  consistency check.

---

## Purpose / hypothesis

Atom 11 (Skunkworks 2026-07-01, MM_STANDARD) claims per-step accuracy of partition-oracle
multihop is invariant across depths d=15-60 at fixed N=8192, PART_SIZE=10. Skunkworks named
three CG-expansion axes:
- (a) different N at same PART_SIZE — covered by sibling N_axis cell
- (b) different PART_SIZE at same N — **this cell**
- (c) extended depth — deferred

**Hypothesis (LOAD-BEARING):** partition-oracle per-hop cleanup accuracy at fixed depth is
invariant to PART_SIZE in the regime PART_SIZE ∈ {5, 10, 20} at N=8192, V_C=200. If
per_step_mean(d=15, PART_SIZE) within ± 0.05 of REF_15HOP=0.858 for all three PART_SIZEs, and
per_step_mean(d=30, PART_SIZE) within ± 0.05 of REF_30HOP=0.682, this satisfies CG-expansion
axis (b) and lifts Atom 11 to CG on PS-axis.

**Alternative outcomes (informational):**
- Per_step degrades monotonically with PART_SIZE (larger local cleanup pool → more noise wins):
  MEASURED direction, informs future modeling
- Per_step improves monotonically with PART_SIZE (fewer partitions to route through):
  MEASURED direction, informs future modeling
- Non-monotonic: anomaly, requires investigation

## HYPOTHESIZED vs MEASURED discipline (META_RULE_AC)

The spawn prompt cited "Atom 11 MM_STANDARD: per-step accuracy 0.9853 ± 0.0016 across d=15-60
at fixed N=8192, PART_SIZE=10". Off-disk audit (2026-07-01 by cell-author) found:

- MEASURED@data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json:
  d=15 per_step_acc mean across seeds {11,13,19} = **0.8517, 0.8570, 0.8427; pooled mean 0.850**
- MEASURED@data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json:
  d=15 per_step_acc mean = **0.853, 0.8697, 0.851; pooled mean 0.858**
  d=30 per_step_acc mean = **0.6797, 0.6975, 0.6702; pooled mean 0.682**
- MEASURED@data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json:
  d=15 top1 mean 0.798; derived per-hop geometric = 0.798^(1/15) ≈ 0.985
  d=30 top1 mean 0.633; derived per-hop geometric = 0.633^(1/30) ≈ 0.985

The 0.9853 figure appears to reference **derived per-hop conditional** = `top1^(1/depth)`
(geometric per-hop), a DIFFERENT metric from `per_step_mean = np.mean(per_step_acc)` used by
the sibling N-axis cell (0.858/0.682). The parent per_step_acc array is a CUMULATIVE
top1-at-step-i curve; its mean and the geometric-per-hop derivation of final top1 differ.

**Convention chosen (matches sibling N-axis cell):** `per_step_mean` is the primary metric
with REFs 0.858 (d=15) and 0.682 (d=30). `per_step_geometric = top1^(1/depth)` is reported
per-arm as an informational field so downstream code can verify both interpretations. This
resolves the OLD-vs-NEW multihop family discrepancy called out in the spawn prompt: the OLD
cells' cumulative-curve mean is 0.858, the derived-per-hop is 0.985; they're not conflicting,
they're different quantities.

## Cell design

### Substrate config (holds fixed across arms)
- N = 8192 (dimensionality)
- V_C = 200 (concepts)
- V_P = 10 (predicates)
- K_set = 20 (bindings per cue)
- n_chains = 200
- max_depth = 30 (built once; d=15 slice reuses same chains)
- Encoder = bipolar substrate-native (E, R on cuda; row-normalized)
- Binding = elementwise product; scale sqrt(N); Hebbian outer-product ingest

### PART_SIZE axis (the sweep)
- PART_SIZE ∈ {5, 10, 20}  → n_partitions = V_C/PART_SIZE ∈ {40, 20, 10}

Declared confound: n_partitions varies with PART_SIZE (since V_C fixed at 200). This is the
INHERENT structure of "vary PART_SIZE at same N" — the argmax-cleanup arity varies from 5 to
20 candidates per hop.

### Arms (6)
- `ARM_PART_ORACLE_15HOP_PS5`:   d=15  PART_SIZE=5   n_partitions=40  (rail)
- `ARM_PART_ORACLE_30HOP_PS5`:   d=30  PART_SIZE=5   n_partitions=40  (rail)
- `ARM_PART_ORACLE_15HOP_PS10`:  d=15  PART_SIZE=10  n_partitions=20  (reproducer / parent regime)
- `ARM_PART_ORACLE_30HOP_PS10`:  d=30  PART_SIZE=10  n_partitions=20  (reproducer / parent regime)
- `ARM_PART_ORACLE_15HOP_PS20`:  d=15  PART_SIZE=20  n_partitions=10  (rail)
- `ARM_PART_ORACLE_30HOP_PS20`:  d=30  PART_SIZE=20  n_partitions=10  (rail)

Chains built once per seed at max_depth=30 across V_C=200; W ingested once per seed. All 6
arms share the same chains + W; only the partition boundary + argmax arity differ per arm.
This isolates PART_SIZE as the sole differentiator.

### Seeds
[7, 13, 19] — 3 seeds per arm. EXPECTED_N_UNITS = 3.

CARDINALITY_OK = True; verdict emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if
observed_n_units < 3.

### Verdict gates (LOCKED at module init; META_RULE_L strictly-above-floor applied)

**Reference values (all MEASURED @ N=8192, PART_SIZE=10):**
- REF_15HOP = 0.858 (pooled 6 values from parent extension + ceiling cells)
- REF_30HOP = 0.682 (pooled 3 values from ceiling cell)

**HP_15HOP_PS<k>** (per PART_SIZE k in {5, 10, 20}):
- HARD_PASS iff |per_step_mean(d=15, k) - 0.858| <= 0.05 AND cv_across_seeds <= 0.10

**HP_30HOP_PS<k>** (per PART_SIZE k):
- HARD_PASS iff |per_step_mean(d=30, k) - 0.682| <= 0.05 AND cv_across_seeds <= 0.10

**HF_SCALE_VARIANCE** (any arm):
- HARD_FAIL iff |per_step_mean - REF| > 0.10 at any of the 6 arms

**HF_MECHANISM_DEATH** (any arm):
- HARD_FAIL iff top1 < 0.10 at any arm (mechanism cliff)

**Verdict tiers:**
- `CHAIN_GRADE_SCALE_INVARIANT_PS_AXIS`  — all 6 arms HP; Atom 11 CG-lift on PS-axis
- `PARTIAL_SCALE_INVARIANT_D15_ONLY`     — all d=15 arms HP; d=30 mixed
- `PARTIAL_SCALE_INVARIANT_D30_ONLY`     — all d=30 arms HP; d=15 mixed (unlikely)
- `PARTIAL_SCALE_INVARIANT_MIDDLE_PS_ONLY` — only PS=10 reproducer HP (rail failure)
- `SCALE_VARIANT_PS_AXIS`                — HF_SCALE_VARIANCE fires
- `MECHANISM_DEATH`                      — HF_MECHANISM_DEATH fires
- `MIDDLE_BAND`                          — inconclusive
- `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` — insufficient seeds

### CRLB floor (META_RULE_9)

Per-arm floor = 1/PART_SIZE (argmax over PART_SIZE candidates):
- PART_SIZE=5:  CRLB floor = 0.200
- PART_SIZE=10: CRLB floor = 0.100
- PART_SIZE=20: CRLB floor = 0.050

All parent REFs (per_step_mean 0.68-0.86) sit well above all three floors; discriminator
window HP band (REF ± 0.05) reachable by construction at parent regime; HF_MECHANISM_DEATH
(top1 < 0.10) reachable at all PART_SIZEs (floor 0.05 < DEATH_FLOOR 0.10 for PS=20).

### Discriminator reachability

Both HP + HF sides reachable per PART_SIZE:
- HP: reached at parent PS=10 regime by construction (parent CG demonstrates it)
- HF_SCALE_VARIANCE: reached if PART_SIZE genuinely shifts per_step by > 0.10
- HF_MECHANISM_DEATH: reached at all PART_SIZE (floor 1/PS <= 0.20 < 0.10 for PS=20 case)

### Discriminator-survives-scale (USER 2026-06-26 rule)

Smoke uses full-N=8192 with n_chains=30 (reduced) but same PART_SIZE grid. Reproducer arm
(PS=10) at full-N smoke must show top1 within loose window of parent regime. This satisfies
Check A (smoke at full-N) per rule.

## Wall estimate
Sibling N-axis cell (~1.34 GB W at N=16384) landed in ~150s per seed on GPU. This cell uses
N=8192 (single W per seed = 268 MB) with 6 arm evaluations per seed (vs 4 in sibling). Expected
seed wall ~50-80s on GPU; total ~200s for 3 seeds. Local CPU smoke ~30-60s.

## Timeout
--timeout 3600 (60min hard cap; ample margin)

## Backend
torch.cuda (GPU) mandatory for full run; smoke OK on CPU.

## Queue
overnight_queue (GPU dispatch via hdi_orchestrator; harness-DENIED direct push)

## Dispatch pointer
Post-smoke handoff via SendMessage to hdi_orchestrator with commit hash + spec.
