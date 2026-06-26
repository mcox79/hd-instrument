# Pre-registration: substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1

**Date:** 2026-06-25
**Anchor:** substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1
**Script:** experiments/exp_substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1.py
**Queue:** overnight_queue (GPU; Fix #24 torch.cuda actively used on encoder + contrastive training)
**Seeds:** [11, 13, 19] (cross-cell consistent; FRESH seeds vs KV reference's [0..4])
**M_SWEEP (full):** [10000, 30000, 100000]
**Encoder (full):** EleutherAI/pythia-2.8b (matches reference cell)
**PROJ_DIM:** 256 (matches reference)
**HELDOUT_FRAC:** 0.25 (matches reference)
**PART_SIZE:** 2000 (matches partition routing reference; locked across smoke/full)
**CAT_COS:** 0.70 (matches partition routing reference)

## Promotion context (Tier A #3 / Research DRILL 1 ITEM 5)

KV learned projection (`exp_kv_learned_projection_v1`) chain-grade HARD_PASS at M up to 10k. Verbatim:
```
HARD_PASS: LEARNED contrastive projection GENERALIZES the value-cue->key alignment to HELD-OUT
facts (recall>=0.70, beats analytic ceiling by >0.30, seed-robust). keysep REPORTED (=0.878).
HELD-OUT learned-recall worst=0.827 | keysep=0.878 | std=0.019 | analytic-ceiling=0.080
(margin=0.747) | shuffled-ctrl=0.015 | n_enc=2
```

Dense KV cliffs sharply M=10k -> M=50k: `M=10000[r@1=0.827] | M=50000[r@1=0.149]`
(verbatim from related capacity sweep). Partition routing (`exp_substrate_partition_routing_10M_full_v2`)
chain-grade @ M=100k routed recall@10=0.97 part_size=2000; partial HARD_PASS @ M=1M.

Research drill: P=0.55; compute ~3-6h GPU (heavy; route via Orchestrator). Composes two chain-grade
mechanisms; failure mode is informative either way.

## v1 design (composition cell)

Compose learned-projection + partition-routing at production scale. Tests held-out generalization
where neither dense KV nor unrouted learned projection survives:

- **Arm A** (`ARM_A_LEARNED_NO_PARTITION`): learned-projection only (no partition). Baseline
  scaling -- expected to cliff sharply past M=10k per related capacity-sweep evidence.
- **Arm B** (`ARM_B_DENSE_PARTITION`): dense (no learned projection) + partition routing.
  Replicate partition-routing baseline at production scale; tests partition routing alone.
- **Arm C** (`ARM_C_LEARNED_PARTITION`): learned-projection + partition routing. THE INTEGRATION
  under test -- compounds contrastive de-crowding within routed partition.
- **Arm D** (`ARM_D_DENSE_NO_PARTITION`): dense-only control. Expected catastrophic cliff at M=100k.

Routing cues built around CAT_COS=0.70 + per-key partition-index assignment (deterministic
`index // PART_SIZE`).

## Pre-registered bands (LOCKED at module init via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS)

### HARD_PASS_CHAIN_GRADE_AT_M_100k
- ARM_C held-out recall@1 >= **0.70** at M=100k across seeds
- AND cv across seeds <= **0.05**
- AND keysep <= **0.95** (table-stakes de-crowding)
- AND (ARM_C - ARM_A) >= **0.10** absolute (composition lift vs learned-only)
- AND (ARM_C - ARM_B) >= **0.10** absolute (composition lift vs partition-only)

### CHAIN_GRADE_AT_LOWER_X
- ARM_C chain-grades at M=10k or M=30k but cliffs at M=100k
- Composition extends part of envelope; production-scale chain-grade not reached

### MIDDLE_BAND_NO_CHAIN_GRADE
- ARM_C reaches recall >= 0.40 at some M but not 0.70 with cv <= 0.05
- Partial composition; below chain-grade gate

### HARD_FAIL_LEARNED_PROJECTION_DOESNT_SCALE
- ALL arms (A, B, C) below recall=0.40 at M=100k
- Composition does NOT close at production scale

## Q-discipline guard (BIAS-Q)

If ALL arms (A, B, C, D) saturate >= **0.995** at M=100k:
- Verdict carries `[Q-DISCIPLINE: saturated arms at M=...; corpus too easy at scale]`
- Recommend M=500k+ extension OR contrastive-hard-negative injection
- Flag is documentation, not auto-demotion

## Fix #24 GPU dispatch must actually use GPU

Script:
- imports torch + transformers (PROT-020 satisfied)
- asserts cuda available at full or smoke fallback to CPU (smoke only)
- Encoder forward (pythia-2.8b) ALWAYS on GPU at full (torch.float16 on cuda)
- Contrastive training (`train_contrastive`) ALL ON GPU (`torch.optim.Adam` on cuda tensors)
- Per-unit matmul (M-row keys @ M-row queries) on GPU during InfoNCE training
- emits `gpu_avail`, `gpu_name`, `gpu_max_mem_alloc_mb` to metrics

## Cross-cell discipline

- ASCII only (verified)
- Substrate-only at inference (encoder forward is SETUP-time; counter `_llm_forward_calls_at_inference`
  asserted to 0 at FULL evaluation; `_llm_forward_calls_at_setup` reports encoder forward count)
- Per-arm + per-M metrics in verdict_msg + per_unit (Fix #28)
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] (cross-cell consistent; FRESH vs reference's [0..4])
- META_M6: analytic ceiling (svd-whiten on held-out) computed in-cell PER M, NOT copied
- META_M7: smoke matches full on PROJ_DIM (128 vs 256 reduced for smoke speed), HELDOUT_FRAC,
  PART_SIZE, CAT_COS (capacity-sensitive). Only ENCODER, M_SWEEP, SEEDS, TRAIN_STEPS reduce

NOTE on PROJ_DIM: smoke uses 128 vs full 256 -- this IS a capacity-sensitive dim change. The
mitigation: smoke is for PIPELINE SANITY (does it run, does it converge); the verdict regime
is full M=100k. Smoke PROJ_DIM=128 was inherited from reference cell's smoke pattern; reference
chain-grade holds at PROJ_DIM=256 production scale. META_M7 risk noted; acceptable for smoke.

## Capacity-feasibility analysis

Per (M, seed) wall on RTX 4060 Ti:
- Encoder forward at M=100k facts at pythia-2.8b ~5-10min
- Contrastive training 600 steps @ batch=256 dim=2560->256 on M=100k: ~3-5min
- 4-arm evaluation (recall@1 + keysep): ~1-2min
- Per (M, seed) wall: ~10-15min

3 M-values x 3 seeds = 9 units; ENCODER FORWARD is per (M, seed) since make_facts is determined
by M (different M = different fact corpus). So 9 encoder forwards x ~7min + 9 train x 5min +
9 eval x 2min = ~125min (~2h).

If pre-encode optimization is added (encode max-M once, slice for smaller M), can drop to ~90min.

Memory: M=100k keys+queries at hidden_size=2560 (pythia-2.8b) = ~2GB float16. PROJ_DIM=256
W matrix = 2560 x 256 = 0.6MB. Total ~3GB activations + ~6GB encoder weights = 9GB. Fits 16GB
RTX 4060 Ti with comfortable headroom.

## Timeout estimate

Formula: timeout_s = ceil(1.5 * smoke_wall_s * (FULL_M/smoke_M)^1.0 * (FULL_seeds/smoke_seeds) *
                          (FULL_encoder_size_ratio))

Smoke wall NOT measured (smoke needs GPU + pythia-160m + small M; not run locally on laptop).
Estimate from reference cell: `kv_learned_projection_v1` ran at 382s for M_SWEEP=[2000,10000] +
5 seeds = ~7.6s per (M, seed). Scaling: M factor 100k/10k = 10x; encoder factor pythia-2.8b vs
pythia-2.8b = 1x; seeds 5 -> 3 = 0.6x.

Reference per-unit: 7.6s. Full per-unit estimate: 7.6 * 10 * 1 = 76s on KV-only. Composition cell
adds partition-routing eval (~2x compute). Per-unit: ~150s. 9 units = 1350s = 22.5min.

But that doesn't include the per-seed encoder forward at M=100k facts (not in reference cell's
inner loop). Add ~5min/seed encoder = ~45min total + 22min eval = ~70min.

Conservative budget: **timeout_s = 9000 (2.5h)** -- matches anisotropy v3 budget; provides 2x
headroom for encoder forward at production scale. Below 14400s PROT-021 threshold;
per-(M, seed) checkpoint wired.

## PROT compliance

- PROT-018 (`_n<N>` suffix): anchor has no `_n<N>` suffix.
- PROT-019 (large-N timeout floor): no `_n<N>` suffix.
- PROT-020 (GPU queue requires torch): script `import torch` at module top; OK.
- PROT-021 (long-timeout needs checkpoint): timeout 9000s < 14400s; per-(M, seed) checkpoint wired.

## Pre-flight smoke + self-test gate

- Smoke: pythia-160m, M_SWEEP=[400, 1000], seeds=[11], PROJ_DIM=128, TRAIN_STEPS=200
- Smoke wall NOT measured locally (no GPU on laptop); will measure on remote during gate
- Self-test (numpy + torch, no GPU forward) asserts T1-T7:
  T1 make_facts count; T2 recall@1 self-id; T3 svd-whiten topk dim;
  T4 keysep in [-1, 1]; T5 cat-cue routing at CAT_COS=0.70;
  T6 bands locked; T7 LLM counter = 0
- Self-test PASSED LOCAL (verified before commit)
- Remote smoke gate during queue_add.sh dispatch

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports BOTH directions:
- HARD_PASS_CHAIN_GRADE_AT_M_100k (composition delivers chain-grade at production scale)
- CHAIN_GRADE_AT_LOWER_X (envelope extends partially; cliff identified)
- MIDDLE_BAND (partial; below gate)
- HARD_FAIL_LEARNED_PROJECTION_DOESNT_SCALE (composition fails completely)
- Per-arm per-M per-seed breakdown in per_unit for Skunkworks step-0 honest re-read

## Strategic significance (decision-grade)

If HARD_PASS_CHAIN_GRADE_AT_M_100k:
- Substrate KV scales to 100k FACTS at chain-grade with held-out generalization
- Production-scale knowledge-graph retrieval becomes substrate-feasible
- Composes BOTH chain-grade mechanisms (learned projection + partition routing) at the integration

If CHAIN_GRADE_AT_LOWER_X:
- Envelope partially extends; honest cliff identifies the binding constraint at production scale

If HARD_FAIL_LEARNED_PROJECTION_DOESNT_SCALE:
- Neither learned nor partition nor composition closes at M=100k
- Refute composition hypothesis; substrate KG retrieval bounded at lower scale

## Honest negatives possible

- Arm C may saturate at 1.000 across all M (Q-discipline; corpus too easy)
- Encoder forward on 100k facts may push memory limits (cell may need to chunk encoder forward)
- Contrastive training at M=100k InfoNCE temperature may need re-tuning (loss may plateau)
- Per-seed variance at M=100k may push cv above 0.05 (held-out shuffle sensitivity)
- Partition routing accuracy at large n_partitions (50 partitions for M=100k) may degrade vs reference's
  high-partition success

## Dispatch plan

1. Author cell + prereg (this file) -- DONE
2. Self-test PASSED locally -- DONE (T1-T7 PASS)
3. Path-scoped commit BEFORE remote dispatch (cell + prereg only)
4. Dispatch via `bash tools/orchestrator/queue_add.sh overnight_queue substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1 experiments/exp_substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1.py preregs/2026-06-25_substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1.md 9000`
5. queue_add.sh SCPs script + prereg to marsh@home; SSH triggers remote queue_add.py
6. Post-ship verification: queue_add.sh confirms entry present in remote `data/overnight_queue/queue.json`
7. File dispatch notification in batch note

## Routing rationale

- **overnight_queue (GPU) per Fix #24:** pythia-2.8b encoder forward at M=100k, contrastive training
  on dim=2560 -> 256, 4-arm eval -- all matmul-bound + GPU-resident encoder. CPU would be 10x+ wall.
- **Spawn budget:** this is part of a 4-cell wave authored in a single exp_dev spawn (within
  Fix #14 ceiling; 3 of 4 routes local_cpu_queue; only this 1 routes overnight_queue).
- **Pause flag verified NOT set** at dispatch authorship time. Re-checked before queue_add.sh.

## Test plan post-landing

- Skunkworks step-0 honest re-read of per_arm per_M recall@1 + keysep + route_acc
  (NOT verdict_msg framing per Fix #28)
- Verify cv across 3 seeds at M=100k for arm_C is <= 0.05 for chain-grade claim
- Verify arm_D (dense control) DID collapse as expected (cliff confirmation)
- Verify arm_C does NOT trivially saturate without lift over arms A and B
  (compositional lift >= 0.10 is the discriminator)
- If HARD_PASS_CHAIN_GRADE_AT_M_100k: queue composition extension at M=1M (hierarchical routing)
- If HARD_FAIL_LEARNED_PROJECTION_DOESNT_SCALE: queue research drill into capacity bound mechanism
