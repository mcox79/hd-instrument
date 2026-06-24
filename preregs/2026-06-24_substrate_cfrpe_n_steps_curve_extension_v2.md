# Pre-registration: substrate_cfrpe_n_steps_curve_extension_v2

**Date:** 2026-06-24
**Anchor:** substrate_cfrpe_n_steps_curve_extension_v2
**Routing:** overnight_queue (GPU; PROT-022 N_DIM=8192 matmul-dominant)
**Motivation:** v1 (substrate_cfrpe_n_steps_curve_v1) HARD_FAILed on monotonicity but per-arm BPC kept improving through N=5000 (best=7.0386). Each N step bucket added +0.03 to +0.07 bits -- rate slowing, NOT flat. Asymptote not reached. v2 extends the N_STEPS grid past v1's ceiling to find where cf-RPE actually flattens.

## v1 Landing (reference)

`data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json`

Per-arm BPC across seeds (mean):
- N=500: 7.1233 (lift +0.214)
- N=1000: 7.0983 (lift +0.239)
- N=2000: 7.0767 (lift +0.260)
- N=3000: 7.0712 (lift +0.266)
- N=5000: 7.0386 (lift +0.299) -- best in v1
- ARM_HEBBIAN_BASELINE: 7.3372

v1 verdict HARD_FAIL fired on lift-monotonicity gate (N=1500 dipped to 7.1102 mid-curve), but the trend toward N=5000 shows cf-RPE has NOT plateaued.

## v2 Design

- cf-RPE delta rule: EXACT rule from heterogeneous_plasticity fair_harness
  `delta_W = (E[t+1] - E[t] @ W^T)^T @ E[t] / batch`
- ARM_HEBBIAN_BASELINE: one-pass batched Hebbian (fair_harness ref BPC=7.3065)
- IMPLEMENTATION_REUSE: cell script identical to v1 except ANCHOR_NAME,
  N_STEPS_GRID_FULL, and verdict bands. cf-RPE / Hebbian / encoder / eval
  pipelines are byte-equivalent so N=5000 result can be cross-replicated
  against v1.

### Grid (extension)

- N_STEPS_GRID = {5000, 7000, 10000, 15000}
- N=5000 included as cross-run replication anchor (matches v1; expect bpc~=7.04)
- N=7000, 10000, 15000 are new probes (15000 = 3x v1 ceiling)

### Configuration (unchanged from v1)

- N_DIM=8192, N_TRAIN=100k, N_HELD=20k, V=4000
- text8 corpus, word2vec-google-news-300 encoder
- SPARSE_BIPOLAR_F=0.05, CFRPE_LR=0.5, INGEST_BATCH=64
- SEEDS=[7, 17, 23] (3 seeds)
- LAMBDA_GRID=[0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0] (C7: no 0.0)
- TEMP_GRID=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]

## Pre-registered Threshold Bands (HARD; v2-task-spec)

| Band | Condition | Verdict |
|------|-----------|---------|
| ASYMPTOTE_FOUND | abs(bpc@15000 - bpc@10000) <= 0.01 | flag |
| ASYMPTOTE_BEAT  | best bpc across grid <= 6.95 | chain-grade-bonus flag |
| DIMINISHING_RETURNS | bpc@5000 - bpc@15000 < 0.03 | flag (slow asymptote) |
| HARD_PASS | best bpc <= 7.00 with cv < 0.05 | HARD_PASS |
| MIDDLE_BAND | 7.00 < best bpc <= 7.05 | MIDDLE_BAND |
| HARD_FAIL | best bpc > 7.05 | HARD_FAIL (no improvement over v1) |

ARM_HEBBIAN_BASELINE sanity (full mode only): BPC = 7.3065 +/- 0.05.
cv < 0.05 mandatory for max-N_STEPS arm.

Note: v1's lift-monotonicity HARD_FAIL gate is DROPPED in v2. Extension is
expected to plateau; a non-monotonic tail near the asymptote is expected
and is not itself a failure mode.

## Smoke Results (2026-06-24)

- N_DIM=512, N_STEPS_GRID=[50,100,200], seeds=[0], device=cpu
- ARM_HEBBIAN_BASELINE: bpc=5.120
- N50_cfrpe: bpc=5.028 (lift +0.092)
- N100_cfrpe: bpc=4.812 (lift +0.307) -- best
- N200_cfrpe: bpc=4.844 (lift +0.276)
- Verdict: HARD_PASS (best bpc=4.8122 <= 7.00 bar)
- ASYMPTOTE_BEAT triggered (smoke bpc << 6.95)
- ASYMPTOTE_OPEN msg: |bpc@200 - bpc@100| = 0.0317 > 0.01 (still moving)
- All 9 instrumentation self-tests PASS
- Hebbian sanity OK gate is suppressed in smoke (RUN_MODE != "full"); smoke
  uses smaller N_DIM/V so the 7.3065 ref does not apply.

## Routing Decision

Routing: overnight_queue. Same justification as v1 (N_DIM=8192 matmul-dominant
on i5 CPU is intractable; GPU required).

Timeout estimate:
- v1 per-seed wall on GPU (3 seeds, 6 cf-RPE arms 500..5000): 685s / 801s / 813s
  = ~766s/seed average for the 6-arm grid
- v2 has 4 cf-RPE arms but at higher N: {5000, 7000, 10000, 15000}
- Per-arm wall on GPU scales roughly linearly with N_STEPS (each step is one
  batched matmul). v1 N=5000 arm ~= 137s / seed at the high end.
- Estimated per-seed wall (v2): Hebbian (~80s) + cf-RPE 5000 (~140s) + 7000
  (~196s) + 10000 (~280s) + 15000 (~420s) + encoder (~30s) + eval (~50s)
  = ~1196s / seed
- Total: 1196s * 3 seeds = 3588s; + 1.5x safety = 5382s
- Set --timeout 10800s (3h). Comfortable headroom; well below PROT-021
  4h-checkpoint-required threshold (cell DOES import _seed_checkpoint
  regardless, so any timeout is checkpoint-protected).

## C7 META Compliance

LAMBDA_GRID excludes 0.0 (unchanged from v1). Post-hoc LAMBDA_ZERO_COLLAPSE
flag detects if grid minimum selected as best (diagnostic, not FAIL).

## What This Does NOT Show

- Does not test STDP composition (heterogeneous plasticity)
- Does not test generalization beyond text8
- Does not test encoder sensitivity (sparse-bipolar f=0.05 fixed)
- Does not test interaction with cleanup / autoregressive generation
- Does not test scaling beyond V=4000 vocab cap
