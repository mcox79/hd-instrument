# G12 Memory Pattern Characterization v1 at N=4096

## Anchor
memory_pattern_characterization_v1_n4096

## Queue
overnight_queue (GPU)

## Script
experiments/exp_memory_pattern_characterization_v1_n4096.py

## Scientific question
Production engineering foundation. Profile memory access patterns for
substrate operations (store, retrieve, edit, multi_hop). Identify dominant
allocation per operation.

## Pre-registered bands
- HARD_PASS: clean profile emitted for all 4 operations AND identifies
  dominant allocation per operation.
- HARD_FAIL: instrumentation crashes OR profile incoherent.
- MIDDLE_BAND: partial.

## Note
This is a CHARACTERIZATION test. The result IS the profile, not a HP/HF call
on substrate behavior. We pass when profiling cleanly runs.

## Config
- N = 4096 (PROT-018 _n4096)
- M = 2048
- N_OPS_PER_TYPE = 100
- depth = 5, K_paths = 100, N_STARTS = 16
- Seeds: [7, 17, 23, 31, 41]
- Operations: [store, retrieve, edit, multi_hop]
- Instrumentation: torch.cuda.memory_allocated, max_memory_allocated,
  memory_reserved per op

## Self-test
- 4 operations profiled at smoke; verdict gates HP/HF exercised
- Live CPU smoke at N=1024 M=128 with reduced n_ops

## Timeout estimate
- smoke wall ~3s
- 5 seeds * 4 op types; multi_hop is the heavy op (~50s)
- scaling_exp = 1.5; estimate = ceil(1.5 * 3 * 4 * 5 * 4) = 360s, with
  multi_hop margin
- timeout_s = 14400 (user spec).

## Importance
HIGH - production engineering foundation; memory profile is rate-limiter
for compaction/streaming design.
