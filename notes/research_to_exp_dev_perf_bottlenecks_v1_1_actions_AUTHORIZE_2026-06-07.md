# Research -> Exp-Dev: v1.1 perf bottleneck actions AUTHORIZED

**From:** Research session
**To:** Exp-Dev + Testbed
**Date:** 2026-06-07
**Re:** Final-implementation perf bottlenecks 2x drill output. Per user blanket
authorization.

## TOP-PRIORITY v1.1 ACTION: Speculative decoding with Llama-1B draft model

Highest-ROI v1.1 engineering investment. Llama-1B already loaded in stack (KEY encoding);
reuse it as speculative decoding draft model. Zero additional VRAM. 1-2 engineer-weeks.
Expected 2-3x LLM latency reduction.

After integration: encoder forward passes become the new primary bottleneck (which leads
to the second action below).

Pre-test before full integration: benchmark current LLM generation latency at 100-token
output; compare to speculative-decoding-prototyped latency. HARD-PASS: >= 2x speedup
with quality degradation <= 1% on a held-out task.

Wall for pre-test: ~1 day. Wall for integration: 1-2 weeks if pre-test HP.

## SECOND-PRIORITY v1.1 ACTION: Distilled 50M encoder (replaces Llama-1B L15 for KEY job)

Required to make edge deployment claim true on RTX4060. Current stack ~8.3 GB total
exceeds 8 GB VRAM by ~0.3 GB. Distilled 50M encoder cuts the Llama-1B L15 1.2 GB to
~50 MB and brings the stack under 8 GB.

Already recommended in Phase 4a per prior encoder drill (CELL-3 alternative). Now URGENT
for edge claim. Will likely overlap with the CELL-3 bge-small@d=30 pre-test that's queued
(if that passes, distillation thread may obsolete entirely; cheaper outcome).

Pre-test: distill Llama-1B L15 onto 50M parameter encoder using cosine loss on substrate
KEY job. HARD-PASS: KEY job F1 >= 0.95 at 50M parameters.

Wall: ~2-3 days CPU/GPU.

## THIRD-PRIORITY v1.1 ACTION: Top-3 customer pitch update

Per drill recommendation:
- LEAD pitch with ENERGY/COST (100-1000x cheaper) — most robust claim regardless of
  bottlenecks
- SPEED claim recalibrated: "~5x faster than frontier p50 (3-5 sec)" pre-speculative;
  "~10x faster than frontier p50" post-speculative-decoding
- NOT defensible at frontier p25 (~2 sec) — honest reframing
- Multi-tenant cold-cache previously cited as risk is actually a STRENGTH (16 MB per
  customer; 1.6 GB for 100 customers; basically free)

Update customer-facing materials accordingly.

## What we DON'T need to do (per drill's brutal honesty)

- Further substrate micro-optimization (saves <1% wall-clock; wrong investment)
- More substrate pinv timing iterations (already at 1.77 ms; not the bottleneck)
- Worrying about multi-tenant cold-cache (basically free at substrate's storage density)

## Engineering sequence proposal

Week 1: Speculative decoding pre-test + distilled encoder pre-test (parallel)
Week 2: If both HP, integrate speculative decoding (1-2 weeks)
Week 3-4: Distilled encoder integration if needed
Week 5: End-to-end benchmark with new stack; customer pitch numbers revalidated

After Week 5: LLM generation reduced 2-3x; encoder reduced 5-10x; edge deployment
verified on RTX4060.

## Cross-references

- Final-impl perf bottlenecks 2x drill: notes/research_drill_final_implementation_perf_bottlenecks_2x_2026-06-07.md
- Drill Exp-Dev handoff: notes/exp_dev_handoff_research_final_impl_perf_bottlenecks_2026-06-07.md
- Prior encoder drill (CELL-3 distillation): notes/research_drill_cell3_distillation_alternatives_2x_2026-06-07.md
- Tier 4 consolidated routing: notes/research_to_exp_dev_tier4_consolidated_routing_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize speculative decoding pre-test (1 day) + distilled encoder pre-test
(2-3 days) in parallel. If both HP, file engineering sequence for integration. Update
customer pitch numbers per drill recommendations (lead with energy/cost; recalibrate
speed claim).

**Testbed:** consider if speculative decoding fits your lane (GPU + LLM training).
Coordinate with Exp-Dev.

Critical methodology lesson today: 3 catches in a row (cycle 159 T5, cycle 160 MarianMT,
cycle 164 entropy-max FALSE PASS) all caught by sanity-gate enforcement. The no-overclaim
rule + verdict() sanity enforcement are critical for honest product positioning.
