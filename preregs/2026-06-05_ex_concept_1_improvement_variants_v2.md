# Prereg: ex_concept_1_improvement_variants_v2
## Anchor
ex_concept_1_improvement_variants_v2
## Routing
EX-CONCEPT-1 Variant 3 (granularity V_c=1024) honest test vs trigram + trained 1-layer neural. Per research improvement_variants. GPU $0.
## Bands
HARD-PASS best-substrate >= neural. MIDDLE >= trigram. HARD-FAIL < trigram.
Smoke (V_c=128): substrate single_pass=0.667 ~ bigram 0.683; extctx HURTS (0.606). Full V_c=1024 + trained neural = fair test.
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
