# Anisotropy M=100k adversarial v2_batched OOM-FIX DISPATCHED

**Date:** 2026-06-25
**Anchor:** `substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched`
**Queue:** overnight_queue (GPU)
**Timeout:** 16200s (4.5h with per-seed checkpoint resume on long-timeout PROT-021)
**Remote VERIFIED:** present in `data/overnight_queue/queue.json` on marsh@home
**Commit:** 38a69eaf (path-scoped: cell + prereg only)

## What this fixes

v1 (same anchor minus `_v2_batched`) CRASHED CUDA OOM on remote 8GB GPU at line 297:
```
sim_c2 = Qtc @ Ktc.t()
torch.cuda.OutOfMemoryError: 6.47 GiB allocated, 230 MiB reserved, 0 free, wanted 288 MiB
```

Root cause: four MAX_Q x M=100k cosine-sim matmuls (sim_fly, sim_c, sim_ab, sim_c2) materialize
600 MB output each + accumulate 1.46 GB K-side tensors concurrently. Plus 4-beta attention sweep.

## Fix (memory-layout only; numeric results identical to v1 by construction)

- `_batched_argmax_sim(Q, K, q_batch=200)` chunks Q-rows; per-chunk sim 80 MB
- `_batched_attn_recall(...)` chunks cue-rows for attention beta-sweep
- Aggressive per-arm K-side del + empty_cache between arms
- Free Kexp/cue_exp before Ktc allocation in ARM C (the v1 crash point)
- Peak GPU footprint ~2.2 GB per arm at M=100k -> fits 8 GB comfortably

## Load-bearing correctness assertion

Self-test extends v1's checks with:
- batched_argmax_sim numeric equivalence for q_batch in {1, 17, 64, 200, 300}: `torch.equal(mono_idx, bat_idx)` MUST hold
- batched_attn_recall vs monolithic: recall diff <= 1e-3 (got mono=0.0033 bat=0.0033)

Self-test PASSED locally on .venv AND remote .venv (gate ran in 4.0s on home).

## What this answers

v1's pre-crash partial M=10k seed-11 slice:
- raw=0.021, B_fly_lsh=0.189, B_charikar=0.193, AB_CTRL=0.240

Preliminary anti-LSH signal at M=10k (AB_CONTROL > both LSH arms). v2_batched will complete
the M sweep at M=50k AND M=100k to give us the chain-grade discriminator Skunkworks asked for.

Possible verdicts:
- HARD_FAIL_CONTROL_ALSO_PASSES: Skunkworks's v2 "55x rescue" demotion validated; LSH narrative dies
- HARD_PASS_CHAIN_GRADE_CONFIRMED_FLY_LSH or _CHARIKAR: LSH IS load-bearing at substrate-product scale
- HARD_PASS_BOTH_LSH_RESCUE: joint LSH-rescue
- MIDDLE_BAND_PARTIAL_RESCUE: partial signal; non-conclusive
- HARD_FAIL_RESCUE_DOESNT_HOLD: LSH dies; anisotropy bypass via partition routing only

Either honest outcome is decision-grade.

## Same as v1

- Arms: RAW, A_dense, B_fly_lsh, B_charikar, AB_CONTROL, C_compose, D_meter
- M sweep: [10k, 50k, 100k]
- Seeds: [11, 13, 19]
- Adversarial-similarity keys: consecutive-token stride-1 windows
- Bands: identical (HARD_PASS chain-grade requires winning LSH beat AB_CONTROL by >= 0.10 AND peer LSH by >= 0.05)
- META_M6 RAW baseline in-cell at adversarial regime
- META_M7 smoke pipeline-sanity-only

## Cross-cell sanity rail (post-landing)

Compare v2_batched M=10k slice seed-11 to v1 partial: raw=0.021 B_fly=0.189 B_char=0.193 AB_CTRL=0.240.
Numeric equivalence at this regime confirms batching is bit-stable in production.

## For Skunkworks step-0 verdict re-read

Read `data/exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched/metrics.json`
`per_unit[*].by_M.M100000` per-arm metrics (NOT verdict_msg framing) per Fix #28.
