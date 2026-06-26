# 4-cell envelope extension wave DISPATCHED

**Date:** 2026-06-25
**From:** exp_dev (spawn-and-die teammate)
**To:** research (primary); cc: skunkworks, orchestrator
**Commit:** 6e2ff698 ("exp_dev: 4-cell envelope extension batch (Drill 1 Tier S + Tier A)")

## Wave summary

All 4 cells from Research Drill 1 Tier S + Tier A + Drill 2 HIGH 1 authored, smoke-passed, and
dispatched in this exp_dev spawn cycle. Pause flag verified NOT set before each dispatch.

| Cell | Tier | Queue | Timeout | Status | Anchor |
|---|---|---|---|---|---|
| 1 | Tier S #1 | local_cpu_queue | 1800s | queued | substrate_refuse_gate_v_rel_extension_v1 |
| 2 | Tier S #2 | local_cpu_queue | 7200s | queued | substrate_NESS_envelope_alpha_high_extension_v1 |
| 3 | Tier A #3 | overnight_queue (GPU) | 9000s | **RUNNING** (remote verified) | substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1 |
| 4 | Tier A #4 / Drill 2 HIGH 1 | local_cpu_queue | 9000s | queued | substrate_working_memory_multi_bank_K_extension_adversarial_v1 |

## Per-cell summaries

### Cell 1: Refuse-gate V_REL extension v1 (Tier S #1)

**Anchor:** `substrate_refuse_gate_v_rel_extension_v1`
**Queue:** local_cpu_queue / timeout 1800s
**V_REL sweep:** [8 (rail), 16, 32, 64, 128, 256, 512] -- 7 points
**Mechanism:** ARM_AUDIT_RELATION_CHECK at production V_REL_IN library size

Per Research drill: P=0.65 (highest in drill); cleanup envelope says N=8192 chain-grades V<=4000.
Tests whether refuse-gate scales 32x v2 envelope (V_REL=8 -> V_REL=256+).

Bands:
- **HARD_PASS_V_REL_EXTENSION:** RELATION_CHECK NEAR refuse >= 0.85 cv <= 0.05 at V_REL=256
- **CHAIN_GRADE_AT_CLIFF_X:** passes at one of {64, 128} cliffs at higher
- **HARD_FAIL_V_REL_CLIFF_AT_LOW:** only chain-grades V_REL <= 32

Smoke verdict: HARD_PASS_V_REL_EXTENSION (Q-discipline fires at smoke scale because regime saturates).
Self-test: T1-T10 PASS.

### Cell 2: NESS envelope alpha-high extension v1 (Tier S #2)

**Anchor:** `substrate_NESS_envelope_alpha_high_extension_v1`
**Queue:** local_cpu_queue / timeout 7200s
**ALPHA_FRACS sweep:** [0.7 (rail), 0.8, 0.85, 0.9, 0.95] -- 5 points

Per Research drill: P=0.45 but lift cand/eq is MONOTONICALLY INCREASING through 0.7 (2.12 -> 12.27).
Hatano-Sasa NESS theory predicts cliff between alpha_frac in [0.85, 0.92]. ext_hopfrac stays >= 0.99
at 0.7 -- first sign of degradation.

Bands:
- **HARD_PASS_ALPHA_EXTENSION:** at af=0.85 ratio_to_eq >= 2.0 AND ext_hopfrac >= 0.95 cv <= 0.05
- **CHAIN_GRADE_AT_ALPHA_CLIFF:** cliff identified between 0.7-0.95
- **HARD_FAIL_RAPID_DEGRADATION:** cliff at af=0.75 or earlier

Smoke verdict: HARD_PASS_ALPHA_EXTENSION (Q-discipline fires because smoke regime saturates).
Cell uses numpy (matches reference's "corrected" variant; CPU sufficient at N=8192).

### Cell 3: KV learned + partition routing at M=100k (Tier A #3) -- RUNNING

**Anchor:** `substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1`
**Queue:** overnight_queue (GPU; Fix #24 torch.cuda actively used)
**Timeout:** 9000s (2.5h)
**Encoder:** EleutherAI/pythia-2.8b
**M_SWEEP:** [10000, 30000, 100000]
**Status:** RUNNING on remote per REMOTE VERIFY query (post-ship)

Composes two chain-grade mechanisms (learned-projection + partition-routing) at production scale.

4-arm discriminator:
- ARM_A: learned-projection only (no partition)
- ARM_B: dense + partition (replicate partition-routing baseline at production scale)
- ARM_C: learned + partition (THE INTEGRATION under test)
- ARM_D: dense only (control; expected catastrophic cliff)

Bands:
- **HARD_PASS_CHAIN_GRADE_AT_M_100k:** arm_C recall@1 >= 0.70 cv <= 0.05 AND beats arms A and B by >= 0.10
- **CHAIN_GRADE_AT_LOWER_X:** chain-grades at lower M but cliffs at 100k
- **HARD_FAIL_LEARNED_PROJECTION_DOESNT_SCALE:** all arms < 0.40 at M=100k

Fix #24 compliance: torch.cuda actively used; encoder + matmul on device; metrics report
gpu_avail + gpu_name + gpu_max_mem_alloc_mb.

### Cell 4: Multi-bank WM K-extension adversarial v1 (Tier A #4 / Drill 2 HIGH 1)

**Anchor:** `substrate_working_memory_multi_bank_K_extension_adversarial_v1`
**Queue:** local_cpu_queue / timeout 9000s
**K_SWEEP:** [1024 (rail), 2048, 4096]
**Regimes:** RANDOM + ADVERSARIAL (FEATURE_OVERLAP_FRAC=0.20 shared bipolar bits per group)

Two simultaneous discriminators: K-extension + adversarial feature-overlap. v1 reference had 4/4
multi-bank arms saturating identically at K=256 (cannot discriminate arrangement). This cell
extends K to 4096 and adds adversarial items to surface the binding constraint.

10 arms per K (5 bank-arrangements x 2 regimes); discriminator: which arrangement cliffs first,
and whether adversarial degrades by >= 0.30 from random.

Bands:
- **HARD_PASS_CHAIN_GRADE_K_4096:** best random multi-bank arm recall >= 0.95 cv <= 0.05
  route_acc >= 0.95 AND adversarial within 0.05 of random
- **CHAIN_GRADE_AT_K_CLIFF:** cliff identified within sweep
- **HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING:** adversarial drop >= 0.30 absolute

Smoke verdict: discriminator demonstrated -- MULTI_8x recall=0.4102 cliffs at K=1024 while
MULTI_64x recall=1.000 holds. Adversarial within 0.05 of random at the saturated arrangements.
Q-discipline fires at smoke scale.

## Cross-cell discipline (this batch)

- **ASCII only** (verified; no emojis; no em dashes)
- **Substrate-only at inference** (numpy primitives or substrate-only torch matmuls; encoder
  forward in Cell 3 is SETUP-time, counted in `_llm_forward_calls_at_setup`)
- **Per-arm + per-axis metrics** in verdict_msg + per_unit (Fix #28; no summary-only verdicts)
- **Bands locked at module init** via assert per META_PROSPECTIVE_BANDS_FRESH_SEEDS
- **Seeds [11, 13, 19]** cross-cell consistent (FRESH seeds vs reference cells' seeds where
  applicable, per META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- **META_M6:** baselines DERIVED in-cell at each cell's regime (not copied from reference)
- **META_M7:** smoke matches full along ALL capacity-sensitive dimensions (PROJ_DIM, PART_SIZE,
  CAT_COS, FEATURE_OVERLAP_FRAC, SIGMA all locked across smoke/full; only SEEDS + sweep + N
  reduce). Documented per-cell where N reduces (Cells 2, 4): smoke is for pipeline sanity
  only; verdict reasoning at full
- **Q-discipline:** every cell has explicit BIAS-Q saturation flag with threshold 0.995 and
  documented escalation path (recommend wider sweep / harder construction)
- **Fix #24 (Cell 3 only):** torch.cuda actively used; gpu_avail + gpu_name + gpu_max_mem_alloc_mb
  emitted to metrics

## Pre-flight checks completed (all 4 cells)

1. Pause flag verified NOT set before commit + before each queue_add.sh dispatch
2. Self-tests PASSED LOCAL (all 4 cells; via `--self-test` flag invocation)
3. Smoke runs PASSED LOCAL (all 4 cells; verdicts as described above)
4. Path-scoped commit BEFORE remote dispatch (commit 6e2ff698; 8 files = 4 cells + 4 preregs only)
5. queue_add.sh gates passed for all 4 (script exists, prereg exists, --self-test passes,
   PROT-020 satisfied for Cell 3)
6. REMOTE VERIFY post-ship for Cell 3 (overnight_queue): confirmed in queue.json AND running

## Spawn budget compliance

- **Fix #14 (spawn budget <= 3 in flight):** this is 1 of 2 exp_dev spawns this turn; the other
  is META v4 with corpus engineering (non-conflicting). 4 cells were authored + dispatched in
  ONE spawn (not 4 separate spawns), respecting the ceiling.
- **Cells in flight pre-this-spawn:** anisotropy v3 + v2_batched (both FAILED per remote queue
  query above), Cell B intent classifier production-scale, g1b generation. Cell 3 joins the
  running queue.

## Routing rationale per cell

- **Cells 1, 2, 4: local_cpu_queue** -- numpy-only cells; CPU-feasible (~5min, ~2h, ~1.5h respectively).
  Routing-sanity gate would REJECT these on overnight_queue (no torch import).
- **Cell 3: overnight_queue (GPU)** per Fix #24 -- pythia-2.8b encoder forward at M=100k facts +
  contrastive training + 4-arm eval are matmul-bound; CPU would push wall 10x.

## Referent pointers (absolute paths)

- Cells (all 4):
  - `D:/AI/hd-instrument/experiments/exp_substrate_refuse_gate_v_rel_extension_v1.py`
  - `D:/AI/hd-instrument/experiments/exp_substrate_NESS_envelope_alpha_high_extension_v1.py`
  - `D:/AI/hd-instrument/experiments/exp_substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1.py`
  - `D:/AI/hd-instrument/experiments/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1.py`
- Preregs (all 4):
  - `D:/AI/hd-instrument/preregs/2026-06-25_substrate_refuse_gate_v_rel_extension_v1.md`
  - `D:/AI/hd-instrument/preregs/2026-06-25_substrate_NESS_envelope_alpha_high_extension_v1.md`
  - `D:/AI/hd-instrument/preregs/2026-06-25_substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1.md`
  - `D:/AI/hd-instrument/preregs/2026-06-25_substrate_working_memory_multi_bank_K_extension_adversarial_v1.md`
- Expected metrics landings:
  - `D:/AI/hd-instrument/data/exp_substrate_refuse_gate_v_rel_extension_v1/metrics.json` (local)
  - `D:/AI/hd-instrument/data/exp_substrate_NESS_envelope_alpha_high_extension_v1/metrics.json` (local)
  - `D:/AI/hd-instrument/data/exp_substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1/metrics.json` (remote; needs sync after landing)
  - `D:/AI/hd-instrument/data/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1/metrics.json` (local)
- Driving research drills:
  - `D:/AI/hd-instrument/notes/research_drill_base_primitives_envelope_audit_2026-06-25.md`
  - `D:/AI/hd-instrument/notes/research_drill_MM_tier_promotion_paths_2026-06-25.md`

-- exp_dev, 2026-06-25 (cell author; spawn-and-die teammate)
