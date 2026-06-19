# Testbed -> Research: CELL-A2 killed pre-verdict (flash-attn compile hang); A2 no longer load-bearing

**From:** Testbed
**To:** Research (primary) + Exp-Dev (inform)
**Date:** 2026-06-08 ~15:38 UTC
**Re:** A2 Llama-8B Path B test was dispatched (cluster cella2-100520, GH200 us-east-3) but
killed at 87 min sunk, $3.30 cost, without ever running the actual experiment.

## What happened

Cluster acquired cleanly + setup phase 1-3 (HF token, GPU detect, torch install) succeeded.
Setup hung in `pip install flash-attn>=2.5,<3 --no-build-isolation` (added as speed
optimization). On aarch64 + cu128 + torch 2.11.0, no precompiled wheel exists; pip
compiled from source. Compile observed running for 60+ min with no completion.

GPU 0% utilization throughout (3 MiB used / 96 GB free); Llama-3.1-8B download
never started (HF cache empty); the actual A2 experiment never ran.

## Why I killed it (vs waiting)

User decision: A2 is no longer load-bearing for v1 demo because cycle 187 PUBLIC
BENCHMARK WIN already proves substrate multi-hop categorically (WebQSP 98.2% +
CWQ 94.7% + FB15K-237 sharded 1.0/0.85 vs monolithic 0.05 = 140x gap).

Specifically:
- A2 was testing whether Llama-8B can produce traversable Wikipedia triples
- The DEMO's multi-hop story now anchors on real-KG benchmarks (WebQSP / CWQ / FB15K)
- A2's verdict would only affect the Wikipedia-NER quality in the demo (Llama-8B vs spaCy)
- Either NER path ships the demo; A2 is "nice to have", not "must have"

So waiting 30-60 more min and burning $2-3 more was not justified.

## Cost ledger

| Item | Cost |
|---|---|
| CELL-A2 (killed pre-verdict) | $3.30 |
| Today's Testbed total | ~$5 ($3.30 A2 + $1.50 v1 demo plan filing iterations) |

## Lessons saved to memory

1. **[[feedback-pip-install-timeout-on-aarch64-compiled-packages]]** — wrap source-compile pip installs in `timeout 600` OR drop entirely if graceful runtime fallback exists; CELL-A2's flash-attn fix was the wrong direction (graceful `||` fallback only fires on failure not while running)

2. **[[feedback-pre-dispatch-speed-harden-progress-discipline]]** — updated to include "if optimization requires source compile, drop it OR timeout"

## Going forward for A2 / Wikipedia NER

If we DECIDE we need the A2 verdict (e.g., Week 2 of v1 demo build wants empirical
evidence for the Llama-8B-vs-spaCy NER choice), I can redispatch with:
- flash-attn DROPPED entirely (script's SDPA fallback handles it; ~10% slower but no
  compile risk)
- ~30 min total wall expected; ~$1.20 cost

But that's a Week-2 decision, not a today decision. For now: spaCy is the Wikipedia
NER default per the build plan; A2 stays on the parking lot.

## What's next for Testbed

Kicking off AUDIT WEEK Day 1 immediately: substrate primitive portability audit on
laptop (no GPU dependency). Per build plan REV1.

## Cross-references

- A2 verification request: notes/testbed_to_research_a2_llama8b_priority_verify_2026-06-08.md
- Research A2 CONFIRM: notes/research_to_testbed_A2_CONFIRM_proceed_with_n100_2026-06-08.md
- v1 demo BUILD PLAN: notes/testbed_v1_demo_BUILD_PLAN_2026-06-08.md
- Cycle 187 public benchmark win: research/orchestrator commit de62f1dc
- Benchmark suite results for demo: notes/exp_dev_to_testbed_benchmark_suite_results_2026-06-08.md
