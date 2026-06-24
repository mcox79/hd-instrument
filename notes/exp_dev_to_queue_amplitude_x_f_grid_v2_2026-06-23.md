# exp_dev queue routing note: substrate_amplitude_x_f_grid_v2

**Filed:** 2026-06-23
**From:** exp_dev (Sonnet 4.6)
**Status:** SMOKE_PASS + REMOTE_VERIFIED

## Queue entry (Schema A)

```
queue=remote_cpu_queue name=substrate_amplitude_x_f_grid_v2 script=experiments/exp_substrate_amplitude_x_f_grid_v2.py prereg=prereqs/2026-06-23_substrate_amplitude_x_f_grid_v2.md timeout=300
```

## Crash diagnosis (v1 -> v2)

v1 crashed at 83s wall on FULL run (N=4096). Root cause:
- `_build_W(X, N)` computed (4096, 4096) float64 = 128MB per cell
- W was never used in `_measure_recall` (direct cosine readout; no Hopfield dynamics)
- 162 cells * 128MB = ~20GB accumulated; MemoryError before GC freed memory

v2 fix:
1. Removed `_build_W` entirely from `run_cell` (W is not needed)
2. Vectorized `_measure_recall` -- batch all probes at once, no Python trial loop
3. float32 throughout (half memory vs float64)
4. randint sign generation (avoids large int temp from rng.choice)
5. OOM guard: pre-check per-cell budget < 500MB before sweep

Per-cell peak: 11.3MB (was ~144MB). Full run ~20-25s on remote_cpu.

## Smoke results

- Smoke (N=512, M=40): PASS in 0.1s; arms discriminate cleanly
- Multi-scale (N=2048): PASS in 0.27s; no crash
- Full N=4096 single-cell timing: PASS ~0.08s/cell; no crash

Raw_pm1 vs inv_sqrt_f at (f=0.02, sigma=16, N=4096): 0.005 vs 0.800; lift=0.795 >> HARD_PASS 0.30.
Suspicious-result gate: PASS. Walk-back gate: not needed (effect size >> 1.0).

## Remote verify

queue_add.sh exit 0 + built-in SSH verify: substrate_amplitude_x_f_grid_v2 confirmed in
remote_cpu_queue/queue.json at marsh@home. Queue now has 4 pending.
