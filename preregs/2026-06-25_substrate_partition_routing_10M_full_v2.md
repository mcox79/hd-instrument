# Pre-registration: substrate_partition_routing_10M_full_v2

**Date:** 2026-06-25
**Anchor:** substrate_partition_routing_10M_full_v2
**Queue:** overnight_queue (GPU; per Fix #24 torch.cuda actively used)
**Seeds:** [11, 13, 19] (cross-cell consistent with today's batch)
**N_SWEEP:** [10000, 100000, 1000000]
**PART_SIZE:** 2000 (LOCKED across smoke/full — USER directive)
**DI:** 1024, **DC:** 256, **TARGET_COS:** 0.133, **CAT_COS:** 0.70

## Promotion context

USER 2026-06-25 directive: 5 chain-grade-eligible cells stuck in smoke (n_seeds=1; cannot tier-rule chain-grade per BIAS-14).
Re-dispatch each in FULL mode with n_seeds>=3 so Skunkworks can tier-rule. Most important = partition-routing 10M cell:
potentially closes substrate-product KG envelope question that today's Cell B (dense KV cliff at M=50k) left partially open.

The v1 smoke result: routed recall@10 = 0.9333 N-INVARIANT across N=[10k, 100k] with partition_size=2000; flat recall cliffs
0.825 -> 0.675; routing accuracy 1.000. HARD_PASS but n_seeds=1 -> not cert-eligible.

## Strategic significance

If this holds at full mode (3 seeds + N=1M added):
- Substrate has chain-grade KG scaling to 100k via partition routing (vs Cell B's 50k cliff with dense single KV).
- If 1M holds too -> the substrate-product KG envelope question Cell B left open is closed at 1M scale.
- If cliff between 100k and 1M -> envelope known precisely.
- If 100k fails -> v1 smoke result was an artifact; partition-routing rescue doesn't survive at scale.

## Mechanism (DECOUPLED-CUE; unchanged from v1)

Per atom: TWO independent cues:
- **CATEGORY cue c_p** (dim Dc=256, shared within partition p): drives ROUTING (clean, CAT_COS=0.70).
- **IDENTITY cue id_g** (dim Di=1024, unique per atom near-orthogonal): drives CLEANUP within routed partition.

Query: cat-cue + identity-cue; routing accuracy governed by cat_noise (clean), INDEPENDENT of identity TARGET_COS — so flat
goes into the interference-collapse regime WITHOUT breaking routing (the artifact that killed the naive single-noise model).

Per (N, seed):
- Build P = N / 2000 category-vector centroids.
- Sample N_QUERIES=200 atom indices uniformly in [0, N).
- Build noisy identity queries + clean category queries.
- ROUTED recall@10 = recover identity within routed partition.
- FLAT recall@10 (rail) = recover identity over ALL N (streamed chunks).
- Routing accuracy = fraction of queries routed to true partition.

## Pre-registered bands (LOCKED at module init via assert)

### HARD_PASS_CHAIN_GRADE_PARTITION_ROUTING_AT_M_100k
- routed recall@10 mean >= 0.85 at N=100k
- cv <= 0.05 across 3 seeds at N=100k
- routing accuracy mean >= 0.95 at N=100k

### HARD_PASS_PARTIAL_AT_M_1M (stretch)
- routed recall@10 mean >= 0.50 at N=1M (only valid if HARD_PASS_AT_M_100k also holds)

### CHAIN_GRADE_AT_LOWER_M_CLIFF
- cliff = routed recall@10 drops from >=0.85 to <0.50 between consecutive N. Cert as MEASURED_MECHANISM (envelope identified).

### HARD_FAIL_PARTITION_DEGRADES
- routed recall@10 < 0.50 at N=100k (would invalidate v1 smoke result)

## Q-discipline (BIAS-Q: suspect 1.000 results) — USER explicit

The smoke result was 0.9333 routed recall@10. If full gives:
- **>= 0.995** at any N: suspect saturation; honest UNDER-claim; tier as MEASURED_MECHANISM unless mechanism story explains.
- **>= 0.95 and < 0.995**: OK chain-grade if cv tight and mechanism story (e.g. clean cat-cue + small part_size routinely
  hit by 200 N_QUERIES = signal-rich regime).

The verdict carries a `[Q-DISCIPLINE: suspect saturation]` note if triggered.

## Cross-cell discipline (this batch)

- ASCII only (verified in script)
- Substrate-only (zero LLM forward calls; no transformer import; numpy + torch only)
- Per-arm metrics in verdict_msg (Fix #28): routed/flat/route-acc PER N PER seed reported
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] (consistent with cross-cell composition this arc)
- Smoke-vs-full discipline: smoke matches full on PART_SIZE=2000 + DI + DC + TARGET_COS + CAT_COS (every capacity-sensitive
  dimension). Only N_SWEEP and N_QUERIES differ between smoke (N=[10k,100k], 1 seed) and full (N=[10k,100k,1M], 3 seeds).
- META_M6: NAIVE baseline is FLAT recall@10 streamed over ALL N (computed in-cell, not copied from another cell's regime).

## Capacity-feasibility analysis

Per (N, seed) GPU wall:
- N=10k: ~3s (chunked flat over 10k; routed over 2000)
- N=100k: ~10s (chunked flat over 100k)
- N=1M: ~60s (chunked flat over 1M = 4 chunks of 250k)

Per seed: ~75s + setup; 3 seeds: ~4-5min total + per-seed checkpoint overhead.

Memory: identity chunks of 250k x 1024 float32 = 1GB per chunk; W never materialized (recomputed from (seed, g0) per chunk).
Category matrix: P_max=500 x 256 = 0.5MB. Query buffers: 200 x 1024 + 200 x 256 ~ 1MB.

## Timeout estimate

Smoke wall (laptop CPU fallback if no GPU): ~10s for 2 N + 1 seed
formula: timeout_s = ceil(1.5 * smoke_wall * (FULL_N_max / smoke_N_max)^1.5 * (FULL_seeds / smoke_seeds))
                  = ceil(1.5 * 10 * (1e6 / 1e5)^1.5 * (3 / 1))
                  = ceil(1.5 * 10 * 31.6 * 3) = 1422s

Conservative budget: **timeout_s = 3600** (1 hour) — accounts for GPU memory mgmt overhead + seed checkpoint resume.

## PROT compliance

- PROT-018 (`_n<N>` suffix): anchor name does NOT contain `_n<N>` suffix; PROT-018 does not apply.
- PROT-019 (large-N timeout floor): same, no `_n<N>`; rule does not apply.
- PROT-020 (GPU queue requires torch): script `import torch` verified; OK.
- PROT-021 (long-timeout needs checkpoint): script imports `_seed_checkpoint`; OK. Timeout 3600s < 14400s threshold anyway.

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports both directions per N AND per seed:
- routed recall@10 per N per seed (the headline)
- flat recall@10 per N per seed (the cliff rail)
- routing accuracy per N per seed (the routing rail)
- cv across seeds per N (the stability rail)
- partition <= cap (the structural rail)

## Fix #24 GPU dispatch must actually use GPU

Script asserts `torch.cuda.is_available()` AT START + emits `gpu_avail / gpu_name` to metrics. Compute is matmul-dominated
(chunked Q x A.T for flat; partition-local A @ q for routed). All tensors on DEV (cuda or cpu). Smoke runs on local CPU
fallback (acceptable for smoke-gate); full runs on GPU runner.

## Honest negatives possible

- routed recall MAY degrade at 1M if cat_cue interference grows (P=500 partitions; some collisions).
- routing accuracy at P=500 may dip from 1.000 (smoke had only P=50 at N=100k).
- cv may be > 0.05 if seeds catch different cat-noise realizations near the routing decision boundary.

Any of these tier the result honestly per the prereg bands. No padding.
