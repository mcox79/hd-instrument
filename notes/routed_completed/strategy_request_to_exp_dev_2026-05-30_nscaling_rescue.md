# Routing note: n_scaling_modern_hopfield_v1_n16384 INCONCLUSIVE rescue

**From:** verdict_handler v283 batch processing (2026-05-30)
**To:** exp_dev (NOT auto-dispatched; orchestrator main-thread review)
**Anchor:** `n_scaling_modern_hopfield_v1_n16384`

## Verdict context

- Verdict: NSCALE_INCONCLUSIVE
- Elapsed: 115.91s
- Per-seed: per_M empty in all 3 seeds (seeds=[7,17,23]); max_M_at_95_recall=0 in all 3
- Configured M sweep: [2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144] at N=16384

## Failure mode

Script started, ran 116s, but the per_M list is empty for every seed. Either (a) the seed loop crashed before any M iteration completed metrics-write, (b) OOM at the first M attempt, or (c) instrumentation bug where the per_M append never fires.

## Rescue sequence (cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

1. **CHEAPEST (~5min):** Inspect the script's stderr (was it captured?) and the partial JSON write timestamps. If stderr shows OOM at M=2048, the issue is N=16384 GPU memory; if no stderr, instrumentation bug.

2. **CHEAP (~15min CPU debug):** Re-run with `--smoke` mode at small M to isolate whether the crash is in seed-setup or per-M loop. If smoke passes, FULL re-run with extra logging at each per_M iteration.

3. **CHEAP (~30min):** Incremental scaling - first verify at N=8192 that the same script produces non-empty per_M; then N=16384 to isolate N-specific bug.

## Suggested exp_dev contract

- Reproduce locally at smoke mode N=4096 M=[2048,4096] to verify instrumentation works at all
- Then attempt N=16384 with extra checkpoint writes between M values
- Document failure mode for orchestrator review BEFORE re-shipping FULL

## DO NOT auto-dispatch

User flagged "gpu and cpu are idle" with pending refill decision. Hold this routing note for orchestrator main-thread review.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
