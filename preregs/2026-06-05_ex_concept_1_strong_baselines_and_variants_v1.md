# Prereg: ex_concept_1_strong_baselines_and_variants_v1
## Anchor
ex_concept_1_strong_baselines_and_variants_v1
## Routing
EX-CONCEPT-1 HONEST strong baselines (trigram + 1-layer transformer) + substrate improvement variants (extended-context K, single-pass). Per research stronger_baselines + improvement_variants. GPU $0.
## Bands
HARD-PASS best-substrate >= small-neural. MIDDLE best-substrate >= trigram. HARD-FAIL best-substrate < trigram.
Smoke (undertrained neural): substrate extctx_K2=0.656, trigram=0.710, neural=0.489 (undertrained). Full -> fair neural comparison.
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
