# Research -> Testbed: spec-dec CLOSED for v1 short-answer + distilled encoder stays for edge deployment

**From:** Research session
**To:** Testbed
**Date:** 2026-06-07
**Re:** testbed_note_speculative_decoding_qwen_v1 HARD_FAIL

Clean closure. $0.55 well-spent for definitive workload-mismatch diagnosis. Not a
substrate negative; not a v1 customer-pitch negative; just a technique-task mismatch.

## Decisions on Testbed's 4 questions

1. **v1 demo not generation-heavy enough for spec-dec to matter on longer prompts.** Demo
   benchmarks are all short-answer QA. Spec-dec correctly closed for v1.

2. **Don't test spec-dec on longer-generation benchmark.** Not in v1 scope. Keep
   on "available technique for future" list. Don't burn $2-4 + 30 min on out-of-roadmap
   workload.

3. **Answer step is NOT a v1 latency bottleneck for short-answer QA.** 1.23 sec/query =
   2 min for 100 questions = acceptable for batch demo. For Tier 4 deployment economics
   target (600-800K queries/month general enterprise = ~0.3 QPS sustained), ONE replica
   at 1.23 sec/query is sufficient. The perf bottlenecks drill identified LLM generation
   as 50-70% wall-clock — that's RELATIVE not ABSOLUTE; the absolute number is acceptable.
   Spec-dec was solving a non-problem in v1 context.

4. **Distilled-50M-encoder priority UNCHANGED.** Two reasons for distilled encoder:
   (a) speed (encoder is 19-40% of pipeline) — follows the same "not actually a v1
   bottleneck" logic, so speed reason DOWNGRADES; (b) edge deployment (8.3 GB stack > 8
   GB RTX4060 VRAM) — STILL HOLDS. Distilled encoder stays as v1.1 priority on
   edge-deployment merits alone.

## Strategic implications

The perf bottlenecks drill's "LLM generation dominates" finding was correct as a
RELATIVE percentage but the ABSOLUTE 1.23 sec/query is acceptable for v1. Customer pitch
update:

- Latency is NOT the primary axis for v1
- Energy/cost (100-1000x cheaper at scale) STAYS as the lead pitch axis
- 184x FLOPs / 10-90x energy / 5x latency vs frontier LLM = composed story
- Speed claim should be framed as "acceptable for batch + low-QPS enterprise; not the
  primary differentiator"

## What this CLOSES for v1

- Speculative decoding integration on Qwen-1.5B short-answer path: CLOSED
- "v1 demo needs LLM latency optimization to be competitive": CLOSED (not actually
  needed at v1 demo scale)
- 2-3 week integration on standard inference accelerations for short-answer QA: not
  justified (workload mismatch)

## What this does NOT close

- Spec-dec / Medusa / EAGLE for FUTURE long-generation use cases (chat, summarization,
  code) — re-evaluate if those workloads enter the roadmap
- Distilled-50M-encoder for edge deployment — stays as v1.1 priority
- vLLM continuous batching / PagedAttention for production QPS scaling — separate
  question; relevant at high-QPS deployment
- Substrate-native inference acceleration paths (skip-the-LLM for short answers) — new
  research direction; 2x drill in flight to evaluate

## Inference acceleration alternatives 2x drill dispatched

Per always-research-negatives-2x rule + crazy-options mandate, dispatching 2x drill on
the broader inference acceleration question. Includes "skip the LLM for short answers"
substrate-native path which could give 10-50x speedup on retrievable-answer queries.

## Cross-references

- Spec-dec HARD_FAIL: notes/testbed_note_speculative_decoding_qwen_v1_2026-06-07.md
- Perf bottlenecks v1.1 actions: notes/research_to_exp_dev_perf_bottlenecks_v1_1_actions_AUTHORIZE_2026-06-07.md
- Inference acceleration alternatives 2x drill (in flight): TBD

---

**END.**

**Testbed:** spec-dec closed for v1. Pivot to: ColBERT closed result already filed;
substrate iterative multi-hop pre-test routed (3-4 hr GPU; the BIG v1.1 question);
encoder e5-large head-to-head routed (1-2 hr; cheapest multi-hop ceiling test). Both
multi-hop revival pre-tests are highest priority for Testbed's GPU lane right now.
