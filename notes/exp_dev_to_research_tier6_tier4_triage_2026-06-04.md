# Exp-Dev -> Research: Tier-6 Phase D + Tier-4 attention-substitution -- triage + build plan

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-04 ~21:10
**Re:** research_to_exp_dev_tier6_phase_D_and_tier4_attention_substitution (the substrate-intrinsic-LLM-training gap).

## Agreed: this is the right strategic gap (user: "vastly increase LLM training speed + substrate intrinsic")
Both tests use validated bio-primitives + are independent of the Llama hang. Triage:

### Tier-6 Phase D (substrate-hybrid 4-layer char-LM) -- BUILDING as next FOCUSED step (GPU)
This is a substantial build: a real gradient-backprop 4-layer transformer baseline + a substrate-hybrid variant
(substrate-Hebbian-attention layers W+=K@V^T / retrieve W@Q, DG-sparse + posbind + STDP + D-ECR, gradient output
head only) + matched-BPC + wall-time + audit-during-training. Per [[feedback-no-experiment-design-in-prompts]] +
not-firehosing-complex-builds: I will build it as a DEDICATED careful build (multi-iteration, ~1-2h), NOT squeeze
it into a 20-min cadence with 4 other obligations (a buggy gradient transformer would mislead).
- Loader: wikitext HfUriError persists -> will use SHAKESPEARE char-LM (your stated fallback) or synthetic 2nd-order.
- NOTE the SPEED kernel is already evidenced: training-speed Stage A + crossover-N sweep showed substrate
  one-shot Hebbian vs Adam (substrate's no-backprop advantage is task/scale dependent). Tier-6 adds the
  MULTI-LAYER + attention-as-sequence-mixing novelty + audit-during-training (the substrate-novel claim).

### Tier-4 Hopfield-attention substitution (1 attention layer swap in Pythia-160M) -- needs Pythia scaffold
Depends on the Pythia-160M model scaffold (load + single-layer swap). Same dependency as EX-CONCEPT-1's Pythia
extraction. Pythia LOADS on the runner (algorithm1-debug ran) so it's FEASIBLE + independent of the hung Llama,
but it's model-in-the-loop (Testbed-adjacent). Pairs with the Pythia-extraction request already filed.

## This cadence
GPU: Llama v7 RUNNING (50k-cap extraction, model loaded, ~2h to npz). CPU: B36-ratio + SQ2-load + SQ5-matrixfree
(N=100k, long-running) cycling -- 3 in flight. Verdicts batch-reported next cadence when they land. EX-CONCEPT-1
real + audit-on-real-residuals unblock when Pythia npz / v7 npz land.

## Commitment: Tier-6 Phase D is my next dedicated build (Shakespeare corpus; substrate-hybrid vs gradient baseline).
**END.**
