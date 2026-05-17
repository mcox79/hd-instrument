# Experiment M6: FHRR vs BSC bundle capacity (hardware-substrate comparison)

**Date:** 2026-05-17
**Phase:** Week 7 molecule experiments

## Hypothesis

Both FHRR and BSC implement the bundle/bind/unbind algebra, but with very different per-component cost:

- FHRR: complex64, 8 bytes per component, multiply-add per bind, FFT-free binding.
- BSC: int8 +/-1, 1 byte per component, integer multiply per bind, integer sum + sign per bundle.

The BSC capacity at matched N should be lower because the binary representation discards continuous-valued interference detail — but only by a constant factor, not orders of magnitude.

## Predicted

- FHRR recovery curve as in M2: ~100% through k=50, falls below 90% near k=100.
- BSC recovery curve roughly tracks FHRR but with a 1.5-2x lower effective capacity.
- BSC stores 8x less per atom (1 byte vs 8).
- Bind operations: FHRR is 6N FLOPs; BSC is N XOR/mul + sign equivalent, ~5x cheaper.

## Falsification

- BSC recovery >= FHRR recovery: binary is doing as well as complex, surprising and a strong hardware-substrate win.
- BSC complete failure (~0%) at all k: BSC implementation is broken.

## Result (2026-05-17)

| k | FHRR recovery | BSC recovery |
|---|---|---|
| 2 | 100% | 100% |
| 5 | 100% | 100% |
| 10 | 100% | 100% |
| 20 | 100% | 99.7% |
| 30 | 100% | 94.9% |
| 50 | 99.1% | 78.7% |
| 75 | 96.1% | 57.2% |
| 100 | 87.7% | 43.4% |
| 150 | 69.1% | 27.2% |

Storage: FHRR uses 8 bytes/component (complex64); BSC uses 1 byte/component (int8). **FHRR is 8x larger per atom.**

## Takeaway: the substrate-tradeoff curve, empirically

BSC keeps pace with FHRR through k=10 but degrades earlier — its 50% recovery boundary is around k~85, while FHRR's is around k~190 (extrapolating). **BSC's effective capacity at N=1024 is ~2.5x lower than FHRR's.**

Cost-per-capacity:
- FHRR: 8 bytes/component, capacity ~190 -> 8192/190 = 43 bytes per "stored item" capacity.
- BSC: 1 byte/component, capacity ~85 -> 1024/85 = 12 bytes per "stored item" capacity.

**BSC wins the storage-efficiency-per-capacity comparison by ~3.5x** despite holding fewer items per substrate. This is the canonical hardware-substrate insight: dense binary representations are net-efficient when memory dominates the cost ledger.

Compute:
- FHRR bind: 6N complex-mul FLOPs (~12 KFLOPs at N=1024).
- BSC bind: N integer mul + sign (~1 KOP).
- BSC is ~12x cheaper per bind in raw op count, and the ops are simpler (no float multipliers needed).

## Pre-registration check

Predicted "BSC capacity 1.5-2x lower." Empirical: ~2.5x lower. Within the ballpark but slightly worse than predicted. The storage 8x prediction is exact.

## Implications for hardware-substrate goal

This is the first concrete data point for the "what substrate is best for what workload" question (project goal #2). For workloads where memory is cheap and compute is expensive (e.g., GPU-bound transformer-style), FHRR's higher capacity may justify the cost. For edge / neuromorphic / in-memory-compute, BSC's binary representation maps directly to existing hardware (Loihi-class chips, RRAM, content-addressable memory) and the 8x storage advantage compounds at scale.

For Week 8 scaling-law experiment: run capacity sweeps for FHRR and BSC at N in {1k, 4k, 16k, 64k, 256k} and fit exponents separately. Hypothesis: BSC's slope of capacity-vs-N matches FHRR's slope (both linear in N) but with a constant offset.
