# Pre-reg: multi_hop_gpu_baseline_v1_n4096

**Date:** 2026-05-30
**Anchor:** multi_hop_gpu_baseline_v1_n4096 (S11, E6.4 baseline)
**Script:** experiments/exp_multi_hop_gpu_baseline_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** GPU vs CPU multi-hop baseline; engineering input.

## Hypothesis

At least one of B/D/E shows >=5x GPU speedup vs CPU AND killer features
(accuracy parity within 5%) pass on GPU.

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | >=1 path: >=5x GPU speedup AND |cpu_acc - gpu_acc| <= 0.05               |
| HARD_FAIL    | Any path crashes on GPU OR all 3 paths have accuracy parity broken (>0.05) |
| MIDDLE_BAND  | otherwise                                                                |

## Self-test

- N == 4096 (PROT-018).
- Smoke at N=1024 M=256 runs CPU-only branch (no GPU on local dev box).
- GPU branch runs on the overnight_queue GPU machine.

## Memory measurement

GPU peak per path via torch.cuda.max_memory_allocated.

## Timeout estimate

5 seeds x 2 devices = 10 device-runs. Per device-run ~10s for 3 paths.
~100s baseline + GPU compile + CPU slow path. **timeout_s = 14400** per
user spec.

## Production config

N=4096, M=2048, depth=5, K_paths=500, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
