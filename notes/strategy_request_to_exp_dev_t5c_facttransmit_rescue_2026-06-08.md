# Strategy request to Exp-Dev: T5c fact-transmission rescue R1+R3
# Filed: 2026-06-08 cycle 202

## Context

Two architectures have now failed the T5c fact-transmission heldout gate:
- t5c_c1fact_heldout_recall_gpu_v1 (cycle 201): bare=0.000, train-recall=0.125, heldout-recall=0.042
- t5c_factkb_kblam_heldout_gpu_v1 (cycle 202): bare=0.000, train-recall=0.060, heldout-recall=0.049

Pattern: adapter routes attention (gate>0) but facts do not transmit even at train time. The failure is consistent across architectures. bare=0.000 rules out a preprocessing issue.

## Rescue experiments requested (cheapest first)

### R3 (sanity gate -- dispatch first): small-scale memorization test
Anchor suggestion: t5c_r3_smallscale_factmem_gpu_v1
Design: Run c1 architecture (PP-217 multi-layer Flamingo) with N_train=100 facts (not 1200).
Goal: Confirm architecture CAN memorize at small scale before investing in loss changes.
If train-recall>=0.50 at N_train=100: R1 is the right fix (loss term).
If train-recall<0.10 even at N_train=100: architecture has a deeper problem (proceed to R4/R5).
Wall time: <30 min GPU. Cost: <$1.

### R1 (if R3 shows partial memorization): explicit retrieval loss term
Anchor suggestion: t5c_r1_retrieval_loss_gpu_v1
Design: Add cosine alignment loss between adapter gate output and fact embedding during training.
Loss = LM_loss + alpha * (1 - cosine(gate_output, fact_embedding))
Start alpha=0.1. Same c1 architecture (PP-217). N_train=200 facts.
Goal: Drive gate output toward fact embedding space, not just toward LLM attention utility.
Wall time: <60 min GPU. Cost: <$2.

## Priority
R3 first (cheap sanity); R1 conditional on R3 showing partial signal.
Do NOT scale to N_train=1200 until R3 passes at N_train=100.

## Cross-ref
PP-217 (cycle 201/202), PP-218 (cycle 201/202), strategy_decisions_2026-06-08.md cycle 202 decision (C).
