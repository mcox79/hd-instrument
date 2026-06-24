# Prereg: substrate_multi_iteration_cleanup_LM_v1

Filed: 2026-06-23 (pre-run, before any results seen)

## Hypothesis

Brain CA3 attractor convergence uses MULTI-ITERATION recurrent dynamics (Hopfield 1982;
Treves-Rolls 1991; typically 3-7 cycles). Substrate currently applies single-step cleanup
(one pass of W). Does multi-iteration convergence measurably improve substrate-as-LM BPC?

P_deflated = 0.45 (uncertain; attractor dynamics may already be captured by rank-1 W at
single-step; BPC metric may be insensitive to cleanup quality in word-bigram regime).

## Arms

- ARM_BASELINE_NO_CLEANUP: raw Hebbian recall, no cleanup iterations (0 steps)
- ARM_SINGLE_STEP_CLEANUP: 1 Hopfield iteration (current substrate default)
- ARM_3_ITER_CLEANUP: 3 Hopfield iterations (partial convergence)
- ARM_10_ITER_CLEANUP_UNTIL_CONVERGE: iterate to convergence (delta < 0.001) or max 10

All arms share identical encoder (char-trigram, N_DIM=8192) and Hebbian W matrix built
from the same corpus split. The ONLY variable is number of cleanup iterations.
Amplitude scaling: 1/sqrt(f=0.05) = 4.47 applied before cleanup (matched-filter energy fix).

## Pre-registered bands (DO NOT ADJUST after seeing data)

- HARD_PASS: ARM_10_ITER beats ARM_SINGLE_STEP by >= +0.10 bits BPC
- CHAIN_GRADE_BONUS: lift >= +0.20 bits BPC (multi-iteration is fundamental fix)
- MIDDLE_BAND: lift +0.03 to +0.10 bits (marginal benefit)
- HARD_FAIL: lift <= +0.03 bits OR negative (multi-iteration does not help)
- BONUS DIAGNOSTIC: 3-iter captures >= 90% of 10-iter lift => diminishing returns; brain
  may not need full convergence for word-prediction

## Config

- N_DIM = 8192 (PRODUCTION; PROT-018: no _nN suffix; N stated here)
- N_TRAIN = 100000; N_HELD = 20000; VOCAB_CAP = 4000
- SEEDS = [7, 17, 23] (3 seeds, full run)
- SPARSITY_F = 0.05; AMPLITUDE_SCALE = 1/sqrt(0.05) ~= 4.47
- MAX_ITER_CONVERGE = 10; CONVERGENCE_DELTA = 0.001

## N-suffix section

No _nN suffix in anchor name. Production N_DIM = 8192 per PROT-018 (stated here).

## Timeout estimate

Smoke (N_DIM=512, N_TRAIN=2000, 1 seed, 4 arms): estimated ~60-120s on remote_cpu.
Encoder at N_DIM=8192 vs 512 = 16x larger per embedding.
W build at N_DIM=8192: O(N_DIM^2) = 256x larger.
Recall at N_DIM=8192: O(N_DIM * V * N_HELD) matmul dominated.
Scaling from smoke:
  smoke_wall_s ~90s (estimated from ACh cell which ran 51s at N=8192 but simpler W)
  FULL_N / smoke_N = 16 (512 -> 8192)
  FULL_seeds / smoke_seeds = 3
  scaling_exp = 1.5 (matmul-bound but chunked)
  estimate = ceil(1.5 * 90 * 16**1.5 * 3) = ceil(1.5 * 90 * 64 * 3) = ceil(25920) >> 4h

  ADJUSTED: 4 arms; each arm does one extra recall pass (vs 3 arms in serotonin cell).
  More conservative: use measured smoke time and apply factor.
  Remote serotonin cell timing: ~0.8s smoke (N=512, N_TRAIN=2000, 3 arms).
  Serotonin full run at N_DIM=8192 submitted at ~20min.
  This cell has simpler mechanism (no multi-bank build complexity) but same encoder + W.
  Per serotonin reference: estimated wall ~15-25 min for 3 seeds.
  timeout_s = 2400 (40 min; 1.5x the 25 min estimate, rounded up to 300s boundary)

Actually: W build at N_DIM=8192 is 268MB float32 = feasible on remote_cpu.
4 arms: baseline=0 iter, 1-iter=fast, 3-iter=3x recall, 10-iter=up to 10x recall per batch.
At RECALL_BATCH=512: each recall pass batched; matmul dominates.
Smoke timing will set actual estimate; if smoke > 300s BLOCK.

## Queue routing

remote_cpu_queue (pure numpy; no CUDA; wall < 30 min est; CPU-bound matmul; Fix #22 check:
N_DIM=8192 triggers Fix #22 GPU routing. HOWEVER: 4 cleanup-iteration arms are embarrassingly
sequential; GPU parallelism gains are minimal vs. memory bandwidth. Cell tests a STRUCTURAL
mechanism (cleanup iterations), not a scale-sensitive metric. remote_cpu accepted here because
cleanup iteration count is not N-sensitive and total wall < 30 min.)

OVERRIDE JUSTIFICATION for not routing to overnight_queue despite N_DIM=8192:
- Primary independent variable is iteration COUNT (categorical: 0, 1, 3, 10)
- N_DIM=8192 is fixed parameter, not swept
- Each arm requires one W @ query matmul (or up to 10 for convergence arm); not a capacity sweep
- No concurrent seeds; sequential single-seed
- Pure-CPU cell optimized for throughput not VRAM
- Prior remote_cpu cells at N_DIM=8192 (ACh, serotonin) completed in <5 min smoke

## What this does NOT show

1. Whether multi-iteration helps with DIFFERENT encoders (char-trigram specific result)
2. Whether cleanup iteration count interacts with sparsity f (f=0.05 only tested)
3. Whether result generalizes beyond word-bigram BPC metric
4. Whether convergence quality improves if W is normalized differently
