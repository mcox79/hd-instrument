# Research -> Exp-Dev: three-paths v1 benchmark resolution (parallel cheap tests)

**From:** Research session
**To:** Exp-Dev
**Inform:** Testbed + Orchestrator
**Date:** 2026-06-07
**Re:** exp_dev_to_research_multihop_fairsize_ceiling_2026-06-07.md + Pattern B exploration + CELL-4 HP.

Run all three paths cheaply in parallel. User picks the v1 benchmark with full information
when all three resolve.

## Path A: Sequential agentic decomp ceiling test

The parallel LLM-decomp didn't work. The sequential agentic loop is the proper ceiling
measurement: retrieve hop-1, extract bridge answer from hop-1 passage, substitute into
hop-2 query, retrieve hop-2.

Method:
- Qwen2.5-1.5B-Instruct (same model you used; ungated, fair size)
- 50 HotpotQA bridge questions
- Sequential loop: Q -> bge-small retrieves top-3 -> Qwen extracts bridge entity from top-1
  passage -> Qwen reformulates Q2 with bridge -> bge-small retrieves top-2 for Q2 -> combine
- Measure recall@2hop on the combined top-2 result

HARD-PASS: recall@2hop >= 0.65 (proves agentic decomp can close at fair size)
BORDER: 0.50-0.65 (closer to closing; longer chain or better LLM might help)
HARD-FAIL: < 0.50 (HotpotQA 2-hop is genuinely fair-size-unwinnable)

Wall: 4-6 hours CPU (Qwen inference plus retrieval). Cost $0.

This is the definitive ceiling measurement. Either we have a path to the 70% target at
fair size, or we don't.

## Path B: Pattern B substrate-native decomposition

Already routed: Pattern B Phase 0 SRL pre-test (3 hours CPU, $0) and Phase 1 algebra
battery (5 cells, 1-2 days CPU, $0). If Phase 0 passes, the algebra cells test whether
substrate can do compositional decomposition via VSA unbinding (Pattern B 1B, 1C, 1E
specifically tests the K-hop unbinding mechanism).

If Path B works: substrate-native decomposition replaces the LLM decomp entirely. LLM
only generates final answer.

This is the high-leverage path; depends on SRL quality on customer-like text.

## Path C: Pivot to single-hop benchmark (FActScore, LongMemEval)

Single-hop benchmarks where substrate's strengths (audit, persistence, attribution)
matter more than multi-hop reasoning ability:

**FActScore pre-test:**
- 20 Wikipedia biographical entities
- Substrate stores ~50 facts per entity
- Generate Llama-1B answer to a question about the entity
- Substrate provides attribution via Merkle proof per supporting fact
- Measure FActScore (attribution-weighted accuracy) vs bare Llama-1B baseline

HARD-PASS: substrate FActScore >= 65% AND attribution coverage >= 90% AND bare Llama-1B
baseline measurable. Wall: 4-6 hours CPU. $0.

**LongMemEval pre-test:**
- 50 questions from the temporal subcategory
- Substrate ingests session history with timestamps
- Bitemporal as-of queries
- Measure temporal accuracy and "what did the system know at time T" support
- This was the highest-empirical-risk pre-test from the benchmark suite drill (does Llama-1B
  follow retrieved context?)

HARD-PASS: temporal accuracy >= 60% AND Llama-1B demonstrably follows context.
Wall: 4-6 hours CPU. $0.

If FActScore + LongMemEval both pass: pivot v1 demo headline to these benchmarks; multi-hop
HotpotQA becomes supporting evidence at most.

## Path coverage matrix

After all three paths complete:

| Path A | Path B | Path C | v1 demo recipe |
|---|---|---|---|
| HARD-PASS | * | * | Sequential agentic + bge-small for HotpotQA |
| HARD-FAIL | HARD-PASS | * | Pattern B substrate-native for HotpotQA |
| HARD-FAIL | HARD-FAIL | HARD-PASS | Pivot to FActScore + LongMemEval |
| HARD-FAIL | HARD-FAIL | HARD-FAIL | v1 demo needs scope re-evaluation |

The first matching row determines the v1 demo recipe. User reviews when all results in.

## CELL-4 result interpretation

Separately, the CELL-4 HARD_PASS (100K facts, perfect recall across noise sweep) confirms
the production substrate retrieval recipe works at v1 deployment scale. That's an
unambiguous positive even amid the multi-hop ceiling concern. The substrate retrieval
foundation is solid; the question is what TASK to run on top of it.

For storage / capacity: the cap_map row for "production retrieval at 100K" moves to ✅.
Independent of the v1 benchmark choice.

## Strategic note on the pitch

If Path A passes: substrate competes on "fair-size LLM head-to-head" pitch.

If Path B passes: substrate's compositional reasoning is the demo (north-star Pattern B
story).

If only Path C passes: pitch shifts to "structured/audited/persistent memory that no LLM
can match at any size." Stronger for regulated markets, weaker for technical demos. We
should be honest about which pitch we're optimizing for.

The multi-hop ceiling finding (if confirmed by Path A HARD-FAIL) is actually USEFUL
information: it tells us where the substrate-LLM-comparison story holds and where it
shifts to "substrate is incomparable to LLM at any scale."

## Cross-references

- Multi-hop ceiling result: notes/exp_dev_to_research_multihop_fairsize_ceiling_2026-06-07.md
- CELL-4 HP result: notes/testbed_note_substrate_hp12_v2_100k_pseudoinverse_v1_2026-06-07.md
- Pattern B exploration program: notes/research_to_exp_dev_pattern_b_full_exploration_program_2026-06-07.md
- Benchmark suite 3x drill: notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md
- Substrate-native decomp unification: notes/research_to_exp_dev_substrate_native_decomposition_connection_2026-06-07.md

---

**END.**

**Exp-Dev:** dispatch all three paths in parallel where CPU available. Sequential agentic
decomp is the most engineering-heavy (4-6 hours); Pattern B Phase 0 is the cheapest gate
(3 hours); FActScore + LongMemEval pre-tests are CPU-cheap. Apply decision rules
autonomously; file synthesis for user review when all three resolve.

**Testbed:** CELL-4 HARD_PASS noted. Substrate retrieval recipe at 100K is locked.
CELL-5 (cascade distillation) can dispatch when authorized; not gated on this routing.
