# Pre-registration: substrate_partition_routing_hierarchical_2level_v1

**Date:** 2026-06-25
**Anchor:** substrate_partition_routing_hierarchical_2level_v1
**Queue:** overnight_queue (GPU)
**Seeds:** [11, 13, 19], **DI:** 1024, **DC:** 256

## Why this cell exists

Research drill 2026-06-25 EXT-2 (refined): KG partition routing at M=10M+.

Cell 1 (`substrate_partition_routing_10M_full_v2`) is chain-grade @ M=100k +
bound @ M=1M today (Skunkworks tier-ruling). Routing accuracy is saturated at
1.0 at M=1M but suspect-by-construction: routing VSA is `subject_atom *
partition_label_atom` which is an FHRR pair-space capped at ~540 distinct
partitions for N=8192 (per Frady-Sommer). M=10M would need 5000 partitions
which is predicted to cliff.

Brain analog: hippocampal indexing into cortical regions (Goyal/Buzsaki 2021);
brain DOES NOT do single-level routing at 10M scale — uses HIERARCHICAL
indexing. Substrate analog = partition-of-partition (level-2 routing).

P(solve) = 0.55 per Research drill.

## Mechanism

Compare 3 ARMs at M ∈ {1M (rail), 10M}:

- **ARM_SINGLE_LEVEL** — Cell 1's flat 5000-partition routing at M=10M
  (predicted to cliff via FHRR pair-space cap)
- **ARM_2LEVEL_HIERARCHICAL** — 10 coarse × 1000 fine = 10000 fine
  partitions of 1000 each. Total routable = 10M. Stage 1 routes to coarse via
  CC_COARSE codebook (10 partitions, clean separation); Stage 2 routes within
  coarse partition via per-coarse CC_FINE codebook (1000 partitions; FHRR
  pair-space safe).
- **ARM_FLAT_KV_REFERENCE** — flat KV scan all N atoms (predicted to collapse;
  reference rail)

For each query at M=10M:
1. Generate target atom + retrieval cue (identity at TARGET_COS=0.133)
2. Generate clean coarse cue (CAT_COS_COARSE=0.80) + clean fine cue (CAT_COS=0.70)
3. Stage 1 (SINGLE_LEVEL only): route via CC_SINGLE @ part_size=2000
4. Stage 1+2 (2LEVEL only): coarse route -> fine route
5. Recall identity within routed partition

## Scientific question

Does hierarchical 2-level partition routing extend the substrate KG chain-grade
envelope from M=1M (Cell 1's verified bound) to M=10M?

## Pre-registered bands

**HARD_PASS_M_10M_VIA_HIERARCHICAL:**
- ARM_2LEVEL routed recall@10 >= 0.80 at M=10M
- AND ARM_SINGLE recall <= 0.50 at M=10M (cliffs as predicted by FHRR cap)
- AND ARM_FLAT_KV recall <= 0.10 at M=10M (collapses by design at flat-KV)
- AND cv <= 0.05 across seeds for ARM_2LEVEL
  (substrate KG extends to M=10M chain-grade via 2-level routing; single-level
   + flat both fail confirming the hierarchical mechanism story)

**CHAIN_GRADE_AT_M_10M:**
- ARM_2LEVEL recall@10 >= 0.70 at M=10M
- (lift over ARM_SINGLE; chain-grade but not full HP)

**HARD_FAIL_HIERARCHICAL_DOESNT_HELP:**
- ARM_2LEVEL recall@10 < 0.50 at M=10M
- OR ARM_2LEVEL <= ARM_SINGLE at M=10M
  (hierarchical doesn't avoid the FHRR cap)

**MIDDLE_BAND:**
- ARM_2LEVEL recall@10 in [0.50, 0.70] at M=10M
  (partial lift but not chain-grade)

## Calibration rationale

- 0.80 floor for ARM_2LEVEL chosen because brain literature (HNSW, ScaNN)
  shows hierarchical small-world indices achieve >= 0.85 at billion-scale.
  Substrate at 10M with proper 2-level routing should be in this regime.
- Single-level cliff at 0.50: predicted by FHRR pair-space cap (~540
  partitions for N=8192) being violated by 10x (5000 partitions for M=10M);
  cliff is the FHRR cleanup failing.
- Flat collapse at 0.10: by-construction collapse of dense KV at M=10M;
  recall@10 falls to ~10/10M = 1e-6 floor but cluttered noise lifts to ~0.05-0.10.
- cv <= 0.05 cross-seed because routing geometry is deterministic at each
  seed; cross-seed variation reflects partition-assignment lottery.

## Q-discipline (BIAS-Q: suspect 1.000 results)

If ARM_2LEVEL recall >= 0.995 at M=10M, raise as suspect-saturation: route_acc
or recall integrity should not saturate to 1.000 at this M without mechanism
story. Honest expectation: 0.80-0.95 range.

## Capacity-feasibility analysis (Frady-Sommer + Cell 1 data)

- FHRR pair-space cap at N=8192: ~N / (k * log V) ~ 8192 / (2 * log 5000) =
  ~540 distinct partition labels distinguishable.
- ARM_SINGLE at M=10M needs 5000 partition labels -> 9x over cap -> CLIFF.
- ARM_2LEVEL at M=10M:
  - Level 1: 10 coarse partitions (well under cap)
  - Level 2: 1000 fine partitions per coarse (right at cap; should still be
    cleanly resolvable)
  - Total: 10000 fine partitions of 1000 atoms each = 10M
- Per-partition cleanup: ~1000 atoms vs DI=1024 -> SNR ~1.0 (right at
  threshold; recall@10 should be in the 0.50-0.90 range)

Capacity feasible for 2-level; predicted cliff for single-level.

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix; this cell tests routing
hierarchy at fixed DI=1024 and varying M. PROT-018 does not apply. Per
PROT-019: timeout >= 3600s required because M=10M flat scan is heavy.

## Timeout estimate

Smoke ~ 5min at M=[100k, 1M], 1 seed (smaller M).
FULL: M ∈ {1M, 10M}, 3 seeds, 3 arms. Flat scan at M=10M is dominant cost.
- Flat scan @ M=10M = 10M * 200 queries * DI=1024 = 2e12 ops per seed.
  ~30-60s per seed on a modern GPU (CHUNK=250000 per pass = 40 passes).
- 2-level routing: 10 + 1000 partitions per fine matmul = small.
- Total per seed for M=10M: ~120s (flat dominant) + 30s for routing + 60s
  for M=1M ~ 200s per seed.
- 3 seeds * 200s = 600s.
formula: ceil(1.5 * 600 * (10M/1M)^1.0)
       = 9000s. Adding overhead for partition codebook setup at 10M scale =
       12000s. budget timeout_s = 12000 (3.3h).
timeout_s = 12000

## Provenance rail

ARM_SINGLE_LEVEL at M=1M must reproduce Cell 1's routed_recall ~ 0.95 + route_acc
~ 1.0 within +/- 0.10. If breaches, raise method-skew flag.

## Fix #24 GPU-actually-used verification

This cell IS torch-ported (identity_chunk_t + routing matmuls + flat scan are
all on DEV=cuda). Per Fix #24, GPU utilization is the right routing decision.
GPU memory for M=10M chunk processing at CHUNK=250000 * DI=1024 * 4 bytes =
1GB per chunk; sequential chunk processing keeps peak memory bounded.

## Cross-cell apples-to-apples

Seeds [11, 13, 19] cross-cell consistent with Cell 1 (substrate_partition_
routing_10M_full_v2). Cell 1's M=1M result is the rail for this cell's
hierarchical ARM_2LEVEL at M=1M (both should land at chain-grade routed_recall
>= 0.85).
