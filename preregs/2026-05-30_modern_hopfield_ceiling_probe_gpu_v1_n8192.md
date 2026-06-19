# G5 Modern Hopfield Ceiling Probe GPU v1 at N=8192

## Anchor
modern_hopfield_ceiling_probe_gpu_v1_n8192

## Queue
overnight_queue (GPU)

## Script
experiments/exp_modern_hopfield_ceiling_probe_gpu_v1_n8192.py

## Scientific question
T3 confirmed max_M >= N at N=16384 CPU but the sweep stopped at M=N.
G5 extends the M-sweep at N=8192 (GPU-feasible per P2 sub1) past M=N to
identify the actual ceiling.

## Pre-registered bands
- HARD_PASS: max_M_at_95_recall >= 2N (= 16384) on >= 2/3 seeds.
- HARD_FAIL: max_M_at_95_recall = N (= 8192) on >= 2/3 seeds.
- MIDDLE_BAND: otherwise.

## Config
- N = 8192 (PROT-018 _n8192)
- M sweep [N, 2N, 4N, 8N] = [8192, 16384, 32768, 65536]
- Codebook: BSC, C = max(M_sweep) = 65536
- Seeds: [7, 17, 23]
- N_PROBE = 200 per M-cell
- RECALL_THRESHOLD = 0.95

## OOM check
- W = 8192*8192 float32 = 256 MiB
- Codebook 65536 x 8192 float32 = 2 GiB
- Sim (65536 x 200) float32 = 50 MiB
- Peak ~2.5 GiB, under 6 GiB headroom on 8 GiB runner GPU.

## Self-test
- N_FULL == 8192
- M_SWEEP_FULL == [8192, 16384, 32768, 65536]
- Verdict gates HP/HF/MB exercised with fake cells
- Live CPU smoke at N=1024 with M_SWEEP_SMOKE = [512, 1024]

## Timeout estimate
- smoke wall ~2s on CPU
- FULL N/N_smoke = 8, FULL_seeds/smoke_seeds = 3, scaling_exp = 2.0 (matrix-heavy)
- estimate = ceil(1.5 * 2 * 8^2 * 3) = 576s. Add margin for FULL M=8N codebook
  construction (3 GiB-class write).
- timeout_s = 21600 (6h budget per user spec; allows 3 seeds at 65536 codewords
  at N=8192).

## Importance
HIGH - first ceiling-finding probe at N=8192 GPU for Modern Hopfield activation.
