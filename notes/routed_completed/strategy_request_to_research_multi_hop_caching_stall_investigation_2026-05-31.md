# Strategy request: investigate multi_hop_caching_baseline stall in FULL config

## Trigger: orchestrator observed runtime stall 2026-05-31 ~10:00-10:56 ET

## Finding

`experiments/exp_multi_hop_caching_baseline_v1_n4096.py` passes `--self-test` cleanly in 6.9s during `queue_add.py` gate. In FULL production config it stalls in startup: no CPU work (parent process 0.016 CPU-seconds, child 0.33 CPU-seconds after 10+ minutes wall), no partial files written, no script log output, no Python tracemalloc activity.

Pattern repeated across multiple launches — runner detected stall, killed subprocess, relaunched; same pattern each time. Killed the anchor (marked status=failed) so the runner could move on to other substantive work.

## Configuration delta (smoke → full) that triggers the stall

- N: 1024 → 4096 (16x memory)
- M_PROD: 256 → 2048 (8x facts)
- DEPTH: 3 → 5
- K_PATHS: 10 → 100 (10x candidate paths)
- N_QUERIES: 30 → 1000 (33x query count)
- ALPHA_SWEEP: [1.0] → [0.5, 1.0, 1.5] (3x alpha values)
- N_STARTS: 4 → 16
- SEEDS: [17] → [7, 17, 23, 31, 41]

## Suspect mechanisms (worth lit-scan / drilling)

1. **Module-level import cost** — script imports `experiments._multi_hop_mechanisms` which has `build_shared` and `path_d_run`. If these do heavy precomputation at import time scaling with N/M_PROD module constants, the import alone may hang. Worth checking if other anchors using the same import work fine at N=4096 (G1 path_d_latency_profiling did, so probably not import time alone).

2. **Cache initialization** — `CACHE_CAPACITY = 256` OrderedDict-based LRU cache. May interact badly with full-config K_PATHS=100 / depth=5 if cache key computation hits a slow path.

3. **Zipfian sample generation cost** — `_zipf_samples(n_total=1000, alpha, n_unique=N_QUERIES, seed)` may be slow at production N_QUERIES. Worth instrumenting.

4. **Substrate construction cost** — `build_shared(N=4096, M=2048, ...)` may have a startup cost that's tolerable per-cell but compounds across multi-cell loops. Note: G1 path_d_latency_profiling uses 60-cell grid at the same N + smaller M and works fine, so this is unlikely.

5. **Torch tensor allocation pattern** — `torch.Generator(device='cpu').manual_seed(seed + 50)` and downstream tensor ops. May hit a CPU-allocator slow path under combined N + M + K_PATHS load.

## Recommended action (research)

1. **Read** `experiments/exp_multi_hop_caching_baseline_v1_n4096.py` and `experiments/_multi_hop_mechanisms.py` to understand the startup sequence end-to-end.

2. **Instrument** the script: add `print(f"[trace] {time.perf_counter():.2f}s reached <stage>", flush=True)` at every meaningful boundary (after imports, after substrate construction, after first Zipfian sample, after first Path D call, after first cell-seed completes). Re-run at FULL config; identify where the stall is.

3. **Compare** to a known-working similar anchor (G1 path_d_latency_profiling is closest match — same N, smaller M, similar Path D usage, recently shipped). Identify the specific code path that differs and likely owns the stall.

4. **Hypothesize a fix**: most likely candidates are (a) lazy substrate construction (defer until first cell), (b) reduce CACHE_CAPACITY default, (c) replace OrderedDict cache with faster structure, (d) fix module-level computation if any.

5. **Deliver** as `notes/research_multi_hop_caching_stall_investigation_v1_2026-05-31.md` with:
   - Root cause identified
   - Specific code change recommended
   - Estimated engineering cost for fix
   - Whether the fix is owned by orchestrator (one-line script change) or testbed (broader infrastructure)

## Cost estimate

~30-60 min research drill (read script, instrument, run, diagnose). Cheap.

## Confidence

P_deflated 0.70-0.85 that the root cause is identifiable from the script + a single instrumented run. The stall pattern (CPU usage <1s after 10+ min wall) strongly suggests blocking I/O or an unbounded loop in a specific place, not a slow-but-progressing computation.

## Files of interest

- `experiments/exp_multi_hop_caching_baseline_v1_n4096.py` (the stalled script)
- `experiments/_multi_hop_mechanisms.py` (shared module imported)
- `experiments/exp_path_d_latency_profiling_v1_n4096.py` (G1; known-working comparable at same N)
- `experiments/_seed_checkpoint.py` (checkpoint helper used at runtime)


## Resolution (2026-05-31)

Root cause = CUDA contention: main() had auto-CUDA device selection; when V2 sustained_workload monopolized GPU, the CPU-queue anchor stalled waiting for CUDA. Fixed by hardcoding torch.device("cpu") in main() (same one-line patch as commit 3ebb009 applied to 4 other scripts). v2 anchors shipped to remote_cpu_queue (substrate_state_compression_v2_n4096, multi_hop_caching_baseline_v2_n4096). No further research drill needed.
