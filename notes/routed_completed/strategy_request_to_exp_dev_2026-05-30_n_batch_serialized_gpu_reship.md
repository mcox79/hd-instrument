# Strategy request to Exp Dev — serialized GPU re-ship for N-batch NO_METRICS (3 anchors)

**Date:** 2026-05-30
**From:** verdict_handler (v284 -> v285 N-batch processing)
**To:** exp_dev
**Disposition:** NOT-AUTO-DISPATCHED — orchestrator main thread / user surfaces for refill decision per user explicit no-refill directive carried over from F-batch.

## Why this routing note exists

N-batch (next-phase 12-anchor research batch, commit e457f1e) shipped 12 anchors in parallel-GPU mode. Three GPU+large-N anchors landed NO_METRICS during overlapping GPU execution:

1. **gpu_baseline_expansion_v1_n8192** — first run exit_code=1 (likely CUDA OOM during multi-anchor parallel-GPU pressure); a retry was initiated (run_index=2) but bridge cache at processing time did not report a finished verdict; needs serialized re-ship or explicit retry-status confirmation.
2. **sparse_w_gpu_integration_v1_n4096** — Windows STACK_BUFFER_OVERRUN (exit 3221226505) at 23s during multi-anchor parallel GPU execution; classic CUDA-runtime collision under contention.
3. **n_scaling_chunked_codebook_v4_n16384** — current state inconclusive: queue listing at processing time did not include the anchor; either still-pending behind retries or skipped during GPU contention. Requires explicit queue-state check + re-ship if absent.

User explicit accept: parallel-GPU is the going-forward mode. But per [[feedback-rehabilitation-after-rejection]] + [[feedback-no-smoke]] these anchors carry zero substrate-capability information and the failure mode is INFRASTRUCTURE (GPU contention), not substrate. Treat as INTERRUPTED, not CLOSED. Re-ship in a separate batch with serialized execution to extract clean verdicts.

## Recommended TASK

Serialized GPU re-ship of N5+N11+N12 as a SINGLE batch (one anchor active on GPU at a time; queue picks next anchor only after prior frees the GPU). Parallel-GPU mode remains the default for everything else.

## WHY this is not padding (per [[feedback-no-padding-experiments]])

- **N5 gpu_baseline_expansion_v1_n8192**: directly resolves the F-batch substrate-GPU baseline single-N caveat (v284 candidate row 🟢 0.65-0.80 carries explicit "single-N N=4096 only" caveat). N=8192 confirmation is the LIFT-criterion for this row.
- **N11 sparse_w_gpu_integration_v1_n4096**: needed for the substrate-GPU baseline to extend to sparse-W (the v284 LIFT to 0.55-0.70 sparse-W row was CPU-only; GPU integration is the operational-deployment path).
- **N12 n_scaling_chunked_codebook_v4_n16384**: the v283/v284 instrumentation-rescue series for N=16384 substrate-construction; this v4 is the chunked-codebook approach (separate mechanism from v2/v3 substrate-construction debug paths). N=16384 envelope question on substrate sizing remains open.

## CONTRACT for exp_dev

- Re-ship in serialized GPU mode (no concurrent GPU anchors during this batch).
- Confirm queue presence via REMOTE VERIFY post-ship.
- Per-experiment timeout REQUIRED per [[feedback-per-experiment-timeout-required]].
- ASCII-only verdict_msg per [[feedback-ascii-only-in-scripts]].
- Anchor names must match `_n<N>` config per PROT-018 (the existing names are already PROT-018-compliant).
- Pre-reg envelope-fail-bands per [[feedback-envelope-expansion-fail-bands]] — re-use the N-batch prereg files for N5/N11/N12 verbatim (no re-design; this is a re-ship not a re-design).

## AUTONOMY

- Exp_dev decides exact queue ordering of N5 / N11 / N12 within the serialized batch.
- Exp_dev decides whether to re-use the existing prereg files or refresh them.
- Exp_dev decides whether to ship all 3 in one queue_add or stage them.

## Hard constraints

- DO NOT auto-dispatch — this routing note is for orchestrator main-thread / user surfacing only per user explicit no-refill carry-over.
- If exp_dev IS dispatched later, pause-flag must be ABSENT at dispatch time.

## Cap_map row dependencies

- substrate-GPU baseline row 🟢 0.65-0.80 single-N caveat
- sparse-W active-subspace storage row 🟢 0.55-0.70 (envelope LIFTed v284; GPU integration is operational path)
- substrate-at-N=16384 row remains "instrumentation broken at v2/v3" — chunked v4 is third independent rescue path

## Filed for orchestrator main-thread review.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
