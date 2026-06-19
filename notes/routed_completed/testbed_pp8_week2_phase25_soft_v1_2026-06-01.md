# Testbed deliverable: PP-8 Phase 2.5 iteration 2 (soft-substrate) — escalation, not iteration

**Date**: 2026-06-01
**Anchor**: pp8_w2_p25_soft_substrate_h100_v1_n4096
**Verdict**: **MIDDLE** — loss decrease 42.7% (PASS the >=30% criterion); val top-1 0.0000% (FAIL the >random criterion); **identical 0% val to both prior runs**
**Cost**: $0.85 actual (76% under predicted $3.58)
**Wall**: 11.9 min
**Cumulative session Lambda**: $6.53
**Status**: ESCALATE TO USER — the 3-point convergence indicates task design, not gradient pathology

## TL;DR

Three different training pipelines (substrate-bypass / STE / soft-attention) produced IDENTICAL 0/1000 val accuracy despite very different gradient flow and different loss-decrease percentages. The pattern is too clean to be a gradient pathology. The bottleneck is the toy task design itself: my dataset generates a randomized key_text -> target_token mapping with NO learnable signal connecting "Key {idx}: " text to the substrate's bipolar codebook representation of that key. Held-out val keys are fundamentally unlearnable.

This exceeds the gradient-pathology scope of the orchestrator's STE/Gumbel pre-approval contingency. Surfacing for user/strategy decision before consuming iteration 3.

## The 3-point pattern

| Variant | Loss decrease | Val top-1 | Notes |
|---|---|---|---|
| Phase 2 baseline | 44.5% | 0.000% | soft_tanh -> bridge (substrate bypassed) |
| Phase 2.5 STE | 37.8% | 0.000% | discrete cleanup + STE backward |
| Phase 2.5 soft | **42.7%** | **0.000%** | softmax-attention, fully differentiable |

All three trained to similar loss decreases (37-44%) with NO val improvement above random's 0.0977% baseline. Held-out val keys produce 0/1000 correct predictions every time.

## Why this is task-design, not gradient-flow

The toy dataset construction:
- 4096 (key_idx, val_idx) pairs from the substrate's relation graph
- `val_to_token[val_idx] = random token from 1024-token pool` (deterministic but RANDOM mapping)
- 1000 val keys held out (never seen in training)
- Training example: text "Key {key_idx:04d}: " -> target_token = val_to_token[relation[key_idx]]

The model has THREE possible signals connecting key text to target token:
1. **Substrate's relation graph** (key_codebook -> val_codebook): the only signal that could carry held-out information, IF the model can map text -> key_codebook (it cannot, see below)
2. **Direct memorization** (text -> target_token via Phi-3 + LoRA + bridge weights): works for training keys; provides ZERO signal for held-out val keys (the mapping is random by construction)
3. **Bridge prior** (some constant prefix shifts Phi-3 output distribution): also useless for held-out val keys (per-key correctness needs per-key prefix differentiation)

For the substrate signal (#1) to carry over to val, the readout would need to learn:
- `text("Key {K_val}: ")` -> `soft_query` such that `nearest_key_in_codebook(soft_query) == K_val`

But the connection between the text "Key 12345" and the substrate's bipolar codeword codebook[12345] is RANDOM — there's no semantic alignment in the dataset construction. The substrate's codewords are random bipolar at build time; nothing in the LLM's input pipeline pre-aligns them.

For training keys, the readout can MEMORIZE the (key_text, key_codeword) mapping via gradient descent. But each key is seen ~1.29 times in training; even perfect memorization wouldn't extend to held-out keys.

In short: my dataset's task is *not designed* to require substrate generalization. It's a random associative-recall task where the substrate is incidental.

## What this means for the strategic question

The original question was "does the substrate make the bridge useful in extending Phi-3?" My empirical findings can answer two things:

1. **Bridge IS trainable** ✓ (44.5% / 37.8% / 42.7% loss decreases across 3 variants; no NaN/Inf; all gradients flow)
2. **Substrate's contribution to LLM output cannot be demonstrated by this task design** — the task isn't constructed to require generalization-via-substrate

The orchestrator's pre-approval was anticipating gradient-pathology issues, with the architectural-pivot trigger being "3 iterations of STE/Gumbel attempts all fail." But what we have isn't gradient pathology — soft-substrate's fully-differentiable attention gradients are clean, and loss decreases are healthy. The issue is upstream of the gradient design.

## Three paths forward

### Path 1: Redesign the toy task to be substrate-substantive

Construct a task where the val accuracy ABSOLUTELY requires substrate-mediated lookup. Options:
- (1a) Encode key text via Phi-3 hidden state at train time; treat key codeword as a LEARNED projection of the hidden state. Then the substrate's relation graph carries generalization because the key codeword IS the hidden state derivative.
- (1b) Build the substrate from training data: each substrate (key, val) pair = (key_text_tokens, val_text_tokens) so the codewords are aligned with token embeddings. The substrate stores a learned dictionary; the val task tests "can the LLM use the dictionary."
- (1c) Verify-by-control: train on overlapping keys (no held-out); confirm val accuracy can be >0 in principle. Establish baseline before redesigning.

Engineering scope: 2-6 hours depending on which option. Cost: ~$1-3 per H100 dispatch. Strategic value: HIGH — the result becomes informative either way.

### Path 2: Concede the toy task design and move to Phase 3 (Rescue C)

Per parent handoff Phase 3 = multi-hop autonomous retrieval ("substrate retrieves chains via its own autonomous Path D, LLM consumes the results"). This is an independent measurement: does the substrate's MULTI-HOP retrieval produce useful output when chained through the bridge? It doesn't require the same kind of held-out generalization the Phase 2 toy task was attempting.

Cost: $10-30 per parent handoff. Cap_map PP-8 stays at 0.55-0.65 with caveat "Phase 2/2.5 toy task design empirically inadequate to demonstrate substrate utility; Phase 3 multi-hop test may provide alternative signal."

### Path 3: Accept Phase 2.5 result as the empirical finding; document; defer

Cap_map caveat addition: "Phase 2 + Phase 2.5 (3 iterations: bypass / STE / soft-attention) all produced identical val=0% on the toy associative-recall task. The bottleneck is empirically demonstrated to be the toy task design (random key_text-to-token mapping has no signal for held-out keys, regardless of training pipeline). Bridge trainability validated (loss decreases 37-44% all three runs)."

PP-8 P-band stays where it is. Continue Week 3+ build with a properly-substrate-substantive task.

## My recommendation

**Path 1c (verify-by-control) FIRST**: cheap ($1-2 H100 + 30 min eng) sanity check that the architecture CAN learn ANY val signal when keys aren't held out. If THAT passes, the architecture is sound and we just need a better task. If THAT fails, there's a deeper bug in the pipeline I haven't identified.

Then **Path 1a** (key codewords derived from Phi-3 hidden state) as the principled redesign — this is the natural architecture where substrate stores hidden-state-keyed facts and the LLM can in-principle learn to retrieve them. Cost: ~3-4 hours engineering + $2-5 H100. This is the version that ACTUALLY tests the strategic claim.

Path 3 (defer) is cleanest if user wants to move forward on Week 3+ build right now without spending more on Phase 2 task-redesign.

## Cost discipline

- Cumulative today: $6.53 (under $50-150 PP-8 envelope by wide margin)
- 1 iteration remaining in STE/Gumbel contingency budget ($22 remaining)
- Path 1c is ~$1-2 within contingency
- Path 1a is ~$2-5 within contingency

## SCP-back hardening continues to work

6/6 files preserved for this run. Path: `data/lambda_batch_results/pp8_w2_p25_soft_substrate_h100_v1_n4096_8b8d49a3/`.

## Files referenced

- This deliverable
- `notes/testbed_pp8_week2_phase2_qlora_v1_2026-06-01.md` (Phase 2 baseline; commit c54948b)
- `notes/testbed_pp8_week2_phase25_ste_v1_2026-06-01.md` (Phase 2.5 STE; commit 8d1e44a)
- `data/lambda_batch_results/pp8_w2_p25_soft_substrate_h100_v1_n4096_8b8d49a3/` (full results)
- `testbed/llm_integration/phase2_qlora_train.py` (commits 2b03fc3 + b76fc9b + c1726e5 + d82c5d9 + 94be23c)
- `testbed/llm_integration/phase2_toy_dataset_gen.py` (dataset construction; v1 was per-handoff but architecturally incomplete)


---
**ROUTED-COMPLETED**: Acted-on 2026-06-01: Path 1c authorized response filed (strategy_response_to_testbed_pp8_phase25_path_1c_authorized_2026-06-01.md)
