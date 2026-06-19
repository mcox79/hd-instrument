# Research -> Exp-Dev: sleep defrag pre-test (cheap aggregator on fever-class KB, ~1-2 hr CPU)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Sleep defrag 3x drill output. Tests whether substrate aggregator matches LLM
closed-book on a specific aggregated regularity, validating the 50-60% domain-specific
closure claim.

## Pre-test design

Method:
- Generate or curate 100 medical case facts about fevers (synthetic OK for v0 pre-test;
  e.g., "Patient A presented with fever and was diagnosed with infection"; "Patient B
  fever caused by dehydration"; etc.)
- Store in substrate
- Run minimal co-occurrence aggregator: scan stored facts; identify frequent "fever ->
  cause" patterns; produce derived regularity ("of 100 fever cases, 70 had infection
  cause; 15 dehydration; 10 inflammation; 5 other")
- Query the derived regularity in two ways:
  - From substrate: retrieve the aggregated regularity directly
  - From bare LLM (Qwen-1.5B or similar, closed-book): "What are common causes of fever?"
- Compare accuracy: substrate aggregator vs LLM parametric on the SAME aggregated
  regularity

HARD-PASS: substrate aggregator's output matches LLM closed-book on the aggregated
regularity within accuracy difference <= 0.05.
BORDER: 0.05-0.15 difference.
HARD-FAIL: substrate aggregator < LLM accuracy - 0.15.

Wall: 1-2 hours CPU.

## What this validates

If HARD-PASS: confirms the drill's 50-60% domain-specific closure claim. Customer pitch
can include "substrate continual learning + sleep defrag closes the implicit generalization
gap on your domain."

If HARD-FAIL: aggregator approach is bounded; need richer mechanism (LLM-supervised
aggregation, learned regularity encoder, etc.).

## Implementation note

v0 pre-test can use a STRING-KEYED dictionary aggregator (no VSA algebra needed). The
goal is to test whether the AGGREGATED REGULARITY (the output of sleep defrag) matches
LLM closed-book on the same regularity question — not whether substrate's algebra does
the aggregation efficiently. Algebraic efficiency is a v1.1 engineering concern after
the conceptual validation.

## Follow-on engineering if pre-test passes

- Build proper substrate-algebra aggregator (sleep defrag pass via VSA operations)
- Integrate as background process running during low-query periods
- Add audit chain for derived regularities (provenance back to source facts)
- GDPR cascade: if source fact erased, recompute or remove derived regularity
- Estimated 2-4 weeks engineering for v1.1 / v2

## Cross-references

- Sleep defrag 3x drill: notes/research_drill_sleep_defrag_implicit_generalization_3x_2026-06-07.md
- Parametric knowledge + synthesis 2x: notes/research_drill_parametric_knowledge_synthesis_2x_2026-06-07.md
- Continual learning history (cycle 154 online concept extension HP; cycle 162 production
  scale validation): scorecard entries

---

**END.**

**Exp-Dev:** authorize 1-2 hr CPU pre-test. v0 string-keyed dict for aggregator (no VSA
needed for conceptual validation). Decision rules autonomous per case. File synthesis on
completion.
