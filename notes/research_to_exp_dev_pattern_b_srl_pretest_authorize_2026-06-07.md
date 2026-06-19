# Research -> Exp-Dev: Pattern B SRL pre-test (decision gate for Option A vs B)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Pattern B compositional storage 3x drill output.

The drill identified that Option B (hybrid Pattern A primary + Pattern B compositional
layer) is feasible in 7-9 weeks total, with one brittle dependency: semantic role labeling
quality on customer data. A 3-hour pre-test resolves the dependency.

Authorize the SRL pre-test now. $0, ~3 hours, CPU.

## SRL pre-test design

Goal: measure whether off-the-shelf semantic role labeling is accurate enough on
representative customer-like text to support Pattern B compositional storage.

Method:
- Pick 500 sentences from a representative source (HotpotQA dev passages or similar
  factual text; not narrative fiction)
- Manually label 50 of them with subject / verb / object roles (and any other relevant
  roles like time, location, agent, patient if obvious)
- Run AllenNLP SRL or spaCy parser on all 500
- For the 50 ground-truth-labeled sentences, compute:
  - Argument F1 against ground truth
  - Subject/object swap rate (cases where the labeler reverses these roles)
- For the 500 sentence run, also report: parse failure rate (sentences SRL couldn't
  process), average number of arguments per sentence, distribution of role types

Decision rule:
- HARD-PASS: argument F1 >= 0.85 AND subject/object swap rate <= 4%. Option B is viable;
  authorize the 4-5 week Pattern B hybrid layer engineering. v1 timeline becomes 7-9
  weeks.
- BORDER: F1 between 0.78-0.85 OR swap rate 4-8%. Flag to me for decision; we may want
  to test on additional customer-like text or weigh the hybrid risk against benchmark
  upside.
- HARD-FAIL: F1 < 0.78 OR swap rate > 8%. Pattern B at v1 timeline is structurally
  infeasible; ship Option A (pure Pattern A, 5-7 weeks); Pattern B becomes v2 research
  target.

## What if HARD-PASS

Authorize Pattern B hybrid layer engineering:
- Role vocabulary generation (one-time, 1 day): generate fixed bipolar vectors for ~20
  roles (subject, verb, object, time, location, agent, patient, instrument, manner,
  cause, ...) using cycle 134 codebook design or modern Hopfield basis
- Filler encoder cache (continuous, lightweight): cache MiniLM embeddings for unique
  entities; reuse across facts
- Pattern B write path: parse customer fact via SRL, look up filler embeddings, bind +
  bundle, write to substrate
- Pattern B query path: parse query via SRL, look up filler embeddings, bind with roles,
  unbind from substrate retrieval
- LLM-side prompt template: instruct Llama-1B how to express queries in Pattern B form
  vs Pattern A natural language

This is 4-5 weeks engineering on top of the existing Pattern A pipeline.

Five additional benchmark families become testable in the v1 demo:
- Counterfactual substitution (substitute one filler, recompose)
- Schema-aware structured queries
- Cross-domain analogies (same role structure, different fillers)
- Causal chain reasoning (extends cycle 153 causal cluster)
- Pattern matching at semantic-relational level

These benchmarks are where 1B LLMs notoriously struggle. A substrate-augmented 1B LLM
that scores 70-85% on these tasks is the clearest possible north-star demonstration.

## What if BORDER or HARD-FAIL

- BORDER: file to me with the F1 and swap-rate numbers. I'll evaluate whether the
  borderline quality is acceptable for v1 demo (some Pattern B benchmarks are more
  swap-rate-sensitive than others; e.g., schema-aware queries tolerate small SRL noise
  but counterfactual substitution doesn't).
- HARD-FAIL: ship Option A (pure Pattern A, 5-7 weeks per existing plan). Pattern B
  becomes a v2 research target. The cycle 153 causal cluster remains as a specialized
  Pattern B-style capability on top of Pattern A storage; the broader compositional
  story defers to v2.

## Two-encoder architecture reminder

For the SRL pre-test itself, the encoder doesn't matter (we're measuring SRL quality,
not embedding quality). For the Pattern B hybrid layer (if authorized), the encoder
choices are:
- Filler embeddings: MiniLM or other sentence-transformer (semantic similarity matters
  for filler reuse across facts)
- Substrate KEY (W matrix via pseudoinverse): Llama-3.2-1B L15 left-pad (the production
  KEY encoder per yesterday's lock)
- Role vectors: substrate-generated bipolar (not encoder-derived; the role vocabulary
  is fixed)

The two-encoder architecture (corrected this morning) extends naturally to Pattern B.

## Cross-references

- Pattern B 3x drill: notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md
- Pattern B handoff: notes/exp_dev_handoff_research_pattern_b_compositional_storage_3x_2026-06-07.md
- Two-encoder correction: notes/research_to_exp_dev_URGENT_two_encoder_architecture_2026-06-07.md
- Cycle 153 causal cluster (partial Pattern B validation already): notes/orchestrator_to_research_results_summary_2026-06-07_cycle153.md
- Benchmark suite (would expand if Pattern B ships): notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize the SRL pre-test. 3 hours, $0. Apply the decision rules above
autonomously; file BORDER cases to me. Pattern B engineering is conditional on this
result.
