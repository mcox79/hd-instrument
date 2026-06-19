# Prereg: ex_concept_strong_baselines_llama1b_v1
## Anchor
ex_concept_strong_baselines_llama1b_v1
## Routing
Phase 2: EX-CONCEPT honest strong baselines (trigram + trained neural) + substrate at REAL Llama-1B concepts. GPU $0.
## Bands
HARD-PASS best-substrate>=neural. MIDDLE >=trigram. HARD-FAIL <trigram.
Smoke: substrate extctx 0.683 ~ trigram 0.685 < neural 0.782 (honest: position-binding extctx; XOR k-gram [K2-XOR cell] reaches 0.783~neural).
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
