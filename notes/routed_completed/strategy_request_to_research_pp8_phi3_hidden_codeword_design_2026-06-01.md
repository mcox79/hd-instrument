# Strategy request to research: PP-8 Path 1a -- Phi-3-hidden-state-derived key codeword design review

**From**: strategy (orchestrator)
**To**: research
**Date**: 2026-06-01
**Trigger**: PP-8 Phase 2.5 escalation; Path 1c (sanity check) authorized in parallel; Path 1a design review needed before implementation commitment
**Related**: `notes/strategy_request_to_strategy_pp8_phase25_task_design_escalation_2026-06-01.md`, `notes/strategy_response_to_testbed_pp8_phase25_path_1c_authorized_2026-06-01.md`

## Task

Design review of Phi-3-hidden-state-derived key codeword construction for substrate-LLM coupling (Path 1a of PP-8 Phase 2.5).

## Context

PP-8 Phase 2.5 encountered 3 iterations of val=0% across gradient strategies (bypass / STE / soft-attention). Testbed diagnosis: bottleneck is task design -- "Key {idx}: " text has no learnable signal connecting to substrate's randomly-built bipolar codeword for that key index. Path 1a proposes to fix this by deriving key codewords from Phi-3 hidden states instead of building them randomly.

The strategic claim: if key codewords are derived from the LLM's own representation space (hidden states), the LLM should be able to learn to retrieve via alignment because the codewords are "near" the LLM's natural geometry.

## Key design questions

1. **Projection method**: Phi-3 hidden dimension is 3072-dim continuous-valued. Substrate codeword is bipolar N=4096. What is the best projection: random projection + sign? Trainable linear projection + sign? Learned bipolar quantization? What does the literature say about continuous-to-bipolar projections that preserve retrieval geometry?

2. **Algebraic structure preservation**: substrate binding uses XOR (for BSC bipolar) or CCB (circular convolution). When key codewords are derived from continuous LLM embeddings, how do we ensure the derived codewords preserve the substrate's algebraic structure? Does random projection + sign preserve approximate XOR-independence properties?

3. **Generalization theory**: what makes the derived codewords carry over to held-out keys? The toy task's failure was that random codewords have no signal LLM can learn from. With Phi-3-hidden-derived codewords, what is the theoretical basis for train/val generalization? Is it smoothness of the projection, or something about the LLM's embedding geometry?

4. **Alternatives**: what are 2-3 concrete alternatives to random-projection + sign, with calibrated P estimates for each? NVSA (Hersche 2023, Nature MI) is the closest precedent (neural -> bipolar direction); what does that architecture suggest?

## Deliverable

1. Design recommendation for the projection method with rationale.
2. 2-3 concrete alternatives, each with: projection method description + theoretical justification + estimated P(val > random baseline) + estimated engineering complexity.
3. Pre-reg for the recommended Path 1a v1: what result would confirm the design is working vs failing?
4. Any known failure modes or gotchas (e.g., codebook correlation artifacts, quantization collapse, hidden-state dimension mismatch).

Per [[feedback-no-experiment-design-in-prompts]]: deliverable names ANCHORS + POINTERS only; experiment parameter specifics (sweep grids, exact N, exact batch sizes) belong to exp_dev. Research deliverable is a design recommendation, not a full experiment script.

## Deadline

~2-3h research wall. Testbed runs Path 1c in parallel. Strategy will authorize Path 1a v1 implementation from this deliverable + Path 1c result.

## Reference files

- `notes/testbed_pp8_week2_phase25_soft_v1_2026-06-01.md` (Phase 2.5 soft substrate deliverable with diagnosis)
- `notes/substrate_capability_map.md` PP-8 row (current substrate-LLM integration state)
- NVSA (Hersche 2023, Nature MI) -- neural-to-bipolar precedent


---
**Closed 2026-06-01:** Research delivered as `notes/research_pp8_phi3_hidden_codeword_design_v1_2026-06-01.md`. Primary recommendation: fixed Gaussian random projection + sign (Option A) with median-threshold pre-flight diagnostic. P=0.50-0.60 (NVSA precedent raises above pure novel-synthesis). Pre-reg HARD-PASS: val top-1 ≥25% OR ≥5× random + held-out maintained; cross-correlation median <0.05. 3 alternatives ranked (Alt A soft-retrieval annealing for FM-3 rescue; Alt B trainable+ortho-reg for v3; Alt C cross-attention probe for v4). 6 failure modes documented with diagnostics + rescues. Testbed/exp_dev picks up for Path 1a v1 implementation.
