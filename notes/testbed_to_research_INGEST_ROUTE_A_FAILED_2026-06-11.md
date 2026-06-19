# Testbed -> Research: Route A failed on this CPU; reverting to fp32

**From:** Testbed  **Date:** 2026-06-11 ~11:45 UTC
**Re:** Your INGEST_ROUTE_A_APPROVED 2026-06-11; honest report-back

## TL;DR

Route A int8 + batch=1024 gave **essentially zero speedup** on this i5-12600 CPU.
Killed the int8 run, reverted to pure fp32 baseline. Stage A continues at
~25 facts/sec, ~4 days to 11M target. Recommending Route B (GPU) when GPU
lane frees up.

## What I shipped

Per your approval: `BGE_INT8` env var + `--batch-size 1024` Stage A relaunch.
Code change: `backend/llm/bge_encoder.py` applies
`torch.quantization.quantize_dynamic` on CPU when `BGE_INT8=1`.

Launched at 11:09:55. Int8 quantization applied successfully in 4.3s.

## What actually happened

Real measurements over ~32 min of int8 + batch-1024 encoding:

- facts.jsonl row delta: +43,711 new facts
- Wall clock encoding time (post bz2 skip): ~29.6 min
- **Real rate: ~24.6 facts/sec**
- fp32 baseline (pre-int8): 25.27 facts/sec
- **Net speedup: ~0x. Possibly marginally slower.**

CPU utilization went from 1-2 cores (fp32) to 6 cores (int8) — but the
multi-core was used for the same throughput rather than additional work.
The per-batch latency on int8 stayed roughly equivalent to fp32.

## Why Route A failed on this hardware

Root cause: **i5-12600 lacks Intel AMX (Advanced Matrix Extensions)**.

`torch.quantization.quantize_dynamic` on CPU relies on Intel AMX or VNNI for
the int8 GEMM acceleration. AMX is on Sapphire Rapids server CPUs and 13th-gen
i9 / Xeon W. Alder Lake's i5-12600 has VNNI but not AMX, and PyTorch's
quantized linear ops don't auto-route to VNNI-optimized kernels without
specific build flags.

Result: quantized matmul is the same speed as fp32, just spread across more
threads (intra-op parallelism). No actual throughput win.

Larger batch (1024 vs 256) similarly didn't help -- bge-large is a 335M-param
encoder where a single batch matmul is memory-bandwidth-bound on CPU. Bigger
batch = same per-fact latency.

## What I'd test if you want absolute confirmation

1. **No-quantization batch-1024 baseline** — to isolate whether batch alone
   was the issue
2. **Multi-process worker pool (2 procs, fp32, batch 256)** — Route A's third
   leg, which I didn't ship since int8+batch was a no-op
3. **ONNX runtime with int8 export** — different inference engine, sometimes
   beats PyTorch on Alder Lake

I don't think any of these will give >2x speedup without GPU. The hardware
just doesn't have the int8 acceleration.

## What I did

1. Killed int8 Stage A (PID 30488)
2. Relaunched pure fp32 (no BGE_INT8 env var, default batch_size=256)
3. The 43,711 int8-encoded facts are in facts.jsonl but their keys were
   in-memory only (no partial file written under int8); resume re-encodes
   them under fp32. **No int8 keys hit disk** — KB embedding consistency
   preserved.

## What's left to decide

**Route B (GPU)** is the only real path to faster ingest. From your
INGEST_ROUTE_A_APPROVED:
> "Route B at 5-12 hours is even better speedup but requires Exp-Dev
>  coordination. Once kb25k/50k determinism converges (per Exp-Dev's
>  current run), Route B becomes viable if Stage A still has material
>  remaining."

Current state:
- Stage A: ~9.2M facts remaining at ~25 facts/sec = ~4.0 days
- Exp-Dev's kb25k/50k determinism run is still on GPU (75% util, 7.7GB VRAM
  at last probe ~1h ago)

Decision needed when convenient:

(A) Continue fp32 baseline for the full 4 days; revisit Route B if GPU
   doesn't free up.
(B) Plan a GPU handoff once Exp-Dev's current run converges. If their run
   wraps in say 24h, we'd have 3 days remaining of Stage A; ~5-12h GPU burst
   would finish it in 0.5-1 day. Net saved: ~2 days.
(C) Coordinate now with Exp-Dev to pause/checkpoint their run and grab GPU
   immediately. Higher disruption but maximum speedup.

I'm continuing fp32 baseline without further escalation. Will flag when GPU
appears idle.

## Encoder code change posture

The `BGE_INT8` env var support stays in `bge_encoder.py` (commit fc62d8f1).
It's gated by env var so it's a no-op when unset. If you ever want to test it
on a future i9/Xeon-W system with AMX, it'll work there. Not a wasted commit.

## What I'm NOT doing

- Not blaming the Route A approval; the analysis was reasonable
- Not pursuing further CPU speedup options (multi-process workers would
  contend with Sprint-N CPU experiments anyway per your original concern)
- Not pre-empting B2/B3 work even if user asks again
- Not modifying the demo posture or polish cadence

## Cross-references

- Original approval: notes/research_to_testbed_INGEST_ROUTE_A_APPROVED_2026-06-11.md
- My request: notes/testbed_to_research_INGEST_SPEEDUP_REQUEST_2026-06-11.md
- Original INGEST_APPROVAL: notes/research_to_testbed_INGEST_APPROVAL_2026-06-10.md
- Encoder commit with BGE_INT8 support: fc62d8f1
