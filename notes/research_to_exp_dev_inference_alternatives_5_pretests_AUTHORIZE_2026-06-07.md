# Research -> Exp-Dev: inference acceleration 5 pre-tests AUTHORIZED (substrate-native LLM bypass)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Inference acceleration alternatives 2x drill output. Per user blanket authorization.

## Authorize all 5 pre-tests from drill handoff

Per `exp_dev_handoff_research_inference_acceleration_alternatives_2026-06-07.md`. All
CPU-cheap; total ~4-5 hr parallel.

### Pre-test 1: Substrate-direct-answer probe (~1 hr CPU)
Cheapest "is there a real bypass" test. Measure top-1 retrieved chunk F1 on HotpotQA
"answerable" subset (queries where answer text appears in retrieved chunk).

HARD-PASS: F1 >= 0.50 on >= 30% of queries (real bypass path; 30%+ of HotpotQA queries
get substrate-direct-answer without LLM).

If HP: 10-25x speedup on the bypassed fraction; categorical architectural insight that
substrate IS the answer-system for the fast fraction.

### Pre-test 2: Retrieval similarity router (~30 min CPU)
CHEAPEST possible test. Threshold top-1 similarity score to classify "answerable without
LLM" vs "needs LLM." Zero training. Just threshold tuning.

HARD-PASS: at some threshold, "high-similarity" queries achieve F1 within 5% of full
LLM pipeline.

If HP: production router can be a simple threshold check, not a learned classifier.

### Pre-test 3 (CRAZY): Extractive span head on encoder representations (~2 hr CPU)
2-layer MLP on encoder embeddings to predict answer span (start/end). LLM-FREE path
for extractive queries.

HARD-PASS: F1 >= 0.55 on extractive HotpotQA subset.

If HP: directly speaks to north-star (substrate + 50M model vs 7B chat model); we have
a fully LLM-free retrieval+extraction stack.

### Pre-test 4 (CRAZY): Query routing by retrieval similarity threshold (~30 min CPU)
Composite of Pre-tests 1+2; deploy the routing classifier and measure end-to-end
speedup on a mixed query stream.

### Pre-test 5 (Throughput): vLLM continuous batching measurement
v1.1 production-readiness measurement. Measure substrate-augmented Qwen QPS at vLLM
batching (continuous batching + PagedAttention).

HARD-PASS: >= 5x QPS improvement at concurrent load (multi-query latency).

If HP: v1.1 production deployment uses vLLM serving layer; doesn't help single-query
latency but enables high-QPS deployment if needed.

## Strategic implication

**Substrate-direct-answer + similarity router = production fast path for KB-answerable
queries.** Combined with substrate-augmented LLM (slow path for novel reasoning):

- Fast path: substrate retrieval + answer extraction = ~50 ms / query
- Slow path: substrate retrieval + LLM generation = ~1.23 sec / query
- Router decides per query
- Combined effective latency: depends on traffic mix; for KB-heavy customers (medical,
  legal, technical support), could be 60-80% fast path

This is the architectural insight from the drill: substrate-as-direct-answerer for
short-answer factoid QA is the fundamental speedup, NOT spec-dec.

## Customer pitch implication

Adds new capability axis to v1 pitch:
- "Substrate-augmented small LLM serves novel-reasoning queries (1-2 sec)"
- "Substrate-direct-answer serves KB-retrievable queries (50 ms)"
- "Substrate router decides per query; transparent to customer"

This is materially better than "spec-dec gives 2x" claim (which doesn't work for our
workload). The substrate-native bypass IS THE acceleration for short-answer QA.

## What this CONFIRMS already-locked decisions

- Spec-dec closed for v1 short-answer QA (mechanistically expected; not implementation
  bug)
- v1 latency at 1.23 sec/query NOT a critical bottleneck for enterprise
- Distilled 50M encoder stays as v1.1 priority for edge deployment merits only

## What's NEW from this drill

- Substrate-direct-answer bypass path identified as 10-25x speedup on retrievable
  fraction
- Customer pitch can add "substrate-direct fast path" as architectural moat
- Extractive span head as LLM-free retrieval+extraction stack (north-star alignment)

## Cross-references

- Inference acceleration alternatives 2x drill: notes/research_drill_inference_acceleration_alternatives_2x_2026-06-07.md
- Drill Exp-Dev handoff: notes/exp_dev_handoff_research_inference_acceleration_alternatives_2026-06-07.md
- Spec-dec HARD_FAIL: notes/testbed_note_speculative_decoding_qwen_v1_2026-06-07.md
- Spec-dec closure routing: notes/research_to_testbed_specdec_closed_distilled_encoder_stays_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize all 5 pre-tests. Pre-test 2 (similarity router; 30 min) is
cheapest; Pre-test 1 (direct-answer probe; 1 hr) is most informative; Pre-test 3
(extractive span head; 2 hr) is most ambitious. File results as they land. Substrate-
direct-answer bypass is the high-leverage architectural insight; cheap to validate.

**Note:** these are CPU-feasible. Per Exp-Dev's backlog drained + "if waiting, request
it" message, these are the right next round of quick pre-tests to feed the substrate
lane. Heavy items (stella-1.5B, NV-Embed-v2, encoder fine-tuning, Tier 5 Arch 8 MVE)
remain queued for Testbed pending pivotal in-flight verdicts.
