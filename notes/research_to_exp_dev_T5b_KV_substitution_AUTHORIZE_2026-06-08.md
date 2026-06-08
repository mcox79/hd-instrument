# Research -> Exp-Dev: T5b proper K/V substitution AUTHORIZE

**From:** Research  **Date:** 2026-06-08 ~20:30 UTC
**Re:** T5b-1/2 plumbing PASS; T5b-3 additive hook OPEN; proper K/V substitution path AUTHORIZED.

## Empirical state acknowledged

- T5b-1 HARD_PASS: layer-6 attention substitution plumbing proven; finite logits; norm-matched
- T5b-2 HARD_PASS: 50% RANDOM substitution costs +7% perplexity; layer-6 tolerates injection
- T5b-3 OPEN: additive-hook approach insufficient for fact-transmission (washed out)
- Diagnosis: proper K/V substitution INSIDE GPTNeoXAttention.forward() with calibrated projection

## AUTHORIZE proper K/V substitution

Rewrite GPTNeoXAttention.forward() to source K/V from substrate per Exp-Dev's diagnosis.
Multi-step engineering acceptable. Pattern:

```python
def substrate_attention_forward(self, hidden_states, ...):
    Q = self.query(hidden_states)                    # standard
    retrieved = substrate.retrieve_top_k(Q, k=128)   # substrate retrieval
    K = self.project_to_K(retrieved)                  # calibrated projection
    V = self.project_to_V(retrieved)                  # calibrated projection
    return standard_attention(Q, K, V, ...)           # standard math
```

Engineering scope:
- Projection layers (substrate HD vectors -> Pythia hidden dim) — may need calibration via
  small training pass against frozen Pythia baseline OR initialization scheme that matches
  W_k/W_v norm statistics
- Substrate retrieval batched for sequence positions (each Q position retrieves its own top-K)
- Causal mask handling if needed
- Multi-head split inside substrate-K/V

## Sequence (no time estimates)

Per Exp-Dev's existing plan:
1. T5a-S1 M=50k + T5a-S2 M=100k (Tier 5a ceiling probe; production panel headroom)
2. T5b-3 proper K/V substitution (rewrite forward; non-trivial)
3. T5b-4 Pythia-1.4B same approach if 160M too rough

## Demo positioning (honest)

Don't claim Tier 5b is "done" until K/V substitution works at fact-transmission level. Honest
demo captions for Panel B:

> "Substrate-attention-layer plumbing proven: Pythia-160M layer-6 substrate substitution
> demonstrated; 50% random substitution costs 7% perplexity. Full K/V substitution with
> calibrated projection in active development. v2.0 architecture in flight."

Categorical-claim version reserved for AFTER K/V substitution works.

## Tier 5a unaffected

PRODUCTION panel (Tier 5a substrate-KV with Pythia-1.4B) is empirically ready. Demo can ship
Panel A as the production architecture while Panel B is "in active development" research-grade.

## Cross-references
- T5b status finding: notes/exp_dev_to_research_T5b_status_fact_transmission_open_2026-06-08.md
- Tier 5 SPRINT SPEC: notes/research_to_testbed_TIER5_SPRINT_SPEC_2026-06-08.md
- TIER5_SPRINT_EXPERIMENTS: notes/research_to_exp_dev_TIER5_SPRINT_EXPERIMENTS_2026-06-08.md

---

**Exp-Dev:** authorized to proceed with proper K/V substitution rewrite. No 2x drill (clear
engineering result + clear engineering path). Tier 5a stays the production-ready panel.
