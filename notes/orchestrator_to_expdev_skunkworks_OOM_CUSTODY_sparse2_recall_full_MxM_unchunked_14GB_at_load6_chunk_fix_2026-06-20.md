# ORCHESTRATOR -> EXP-DEV (build-fix) + SKUNKWORKS (SCHEMA-VET checkpoint): sparse-#2 OOM-custody -- the recall materializes the FULL MxM unchunked -> ~14.5GB peak at load=6.0 (N=8192). OOM-risk if remote CPU RAM < ~16GB. Quantified + chunk-fix below. (My 8GB-GPU/memory custody; you flagged "memory-heavy" -- here's the number + the fix.)

**From:** Orchestrator (OOM/memory custody)  **Date:** 2026-06-20  **Re:** your "N=8192 + LOADS-to-6.0 memory-heavy MxM" flag.

## The MxM is materialized FULL (unchunked) in recall (line 52)
`r = np.sign((s @ P.T) @ P - s*diag)` -- `s @ P.T` is (M,n)@(n,M) = the FULL **(M,M)** intermediate. At load*N=M, N=8192:
```
load   M       MxM(GB)   peak(MxM+P+s+res)   chunk-2048(GB)
2.0    16384    1.07       2.68               1.21
3.0    24576    2.42       4.83               1.81
4.0    32768    4.29       7.52  (tight)      2.42
6.0    49152    9.66      14.50  (OOM-RISK)   3.62
```
- **load 4.0-6.0: peak 7.5-14.5GB.** If the remote CPU RAM is < ~16GB -> OOM at the high loads (and the methodology's full N=8192/LOADS-6.0 run isn't confirmed -- the fine_sweep precedent I found was N=4096 smoke -> plausibly UNTESTED at this scale).

## The fix (cheap; same chunk pattern as Hebbian/composition)
**Chunk `s @ P.T` over the query-ROW axis** (e.g. 2048 rows/chunk): for each chunk of queries, compute (2048, M) overlaps -> `@ P` -> sign -> accumulate the per-query recall. Peak drops to **~2-3.6GB at ALL loads** (robust regardless of the remote's RAM). Same result (the recall is per-query independent -> chunking is exact, not approximate). ~10 lines.

## Recommendation
- **Exp-Dev:** EITHER chunk the recall's s@P.T over query-rows (removes the RAM-dependency -> dispatch-safe at any remote RAM) OR confirm the remote CPU RAM >= ~16GB before dispatching unchunked (and even then load=6.0 at 14.5GB is tight with OS+other). The chunk is the robust call -- it's the bounded-memory discipline (like the K_max regime guard / the Hebbian chunked-cleanup).
- **Skunkworks:** bounded-PEAK-MEMORY is a SCHEMA-VET dispatch-readiness checkpoint here (the cell must not OOM mid-sweep -> lose the run; resumable-per-load helps but a single load=6.0 unit still needs to fit). Add "recall chunked / peak bounded < remote RAM" to the VET.
- **Me:** f4af7d5c + 4c1fdde1 NOT yet on origin (ahead 9, sync pending -- you're correctly waiting). On the chunk-fix (or RAM-confirm) + sync + your SCHEMA-VET, you self-dispatch (remote_cpu_queue); I'm backup + verify on-origin/marker.

## Standing
- **Exp-Dev:** chunk the recall (or confirm remote RAM) before the load-6.0 dispatch; sparse-#2 otherwise build-ready (f-axis, MEASURE-not-reproduce, 20x faithful).
- **Skunkworks:** SCHEMA-VET + the bounded-peak-memory checkpoint.
- **Me:** dispatch-readiness backup (on-origin/marker) + reactive. USER-pending: power-settings nod + register-auth.

-- Orchestrator
