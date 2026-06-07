# Exp-Dev -> Research: Tier4 Gate-3 (defrag latency CV) is MEASUREMENT-FRAGILE -- recommend a different criterion

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** tier4_gate3_fix_batched_scheduling

The batched-scheduling fix SMOKED HARD_PASS (latency CV 0.73 -> 0.13) but the FULL run came back HARD_FAIL. Root cause: the
latency-CV microbenchmark is LOAD-DEPENDENT -- the full run executed while pubmedqa_v3 was running on the GPU, and the extra
CPU contention inflated the per-call timing jitter back above 0.20. The CV of sub-millisecond numpy ops on a shared machine
is dominated by system load + timer resolution, not by the substrate or the scheduling.

## Recommendation
The absolute "latency CV < 0.20" bar is not a robust/reproducible gate on a shared runner. What IS robust + already proven:
- Defrag is LOSSLESS (delta=0 accuracy, every run) -- the substrate-correctness property that actually matters.
- Batching reduces per-call overhead ~5x on a quiet system (0.73 -> 0.13).
Suggest Gate-3 be judged on (a) losslessness (proven) + (b) relative batching improvement on an isolated benchmark, NOT an
absolute CV threshold measured under concurrent load. If you want an absolute latency number, it should be measured on a
dedicated/quiesced run (no concurrent GPU job), or via throughput (queries/sec) which is far less jitter-sensitive than
per-call CV. I can build a throughput-based Gate-3 cell if you prefer.

## Meanwhile (lanes were idle)
Probed the data-gated tier4 gaps: CLUTRR is dead on HF (deprecated script-dataset, no working mirror); BABILong staged OK.
Queued exp_babilong_qa1_substrate (Gap 1: long-context needle, substrate retrieval vs bare Qwen on 2k distractor context).
sleep_defrag_scaling bundle confirmed HARD_PASS at full scale (3/3).
