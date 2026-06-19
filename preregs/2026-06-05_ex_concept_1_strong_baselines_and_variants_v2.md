# Prereg: ex_concept_1_strong_baselines_and_variants_v2
## Anchor
ex_concept_1_strong_baselines_and_variants_v2
## Routing
EX-CONCEPT-1 honest baselines (FIXED neural: left-pad + 25 epochs) + substrate variants. Replaces v1 (broken neural). GPU $0.
## Bands
HARD-PASS best-substrate>=neural. MIDDLE >=trigram. HARD-FAIL <trigram.
Smoke: substrate extctx_K2=0.692 BEATS trigram 0.677 but LOSES to neural 0.747 -> MIDDLE (honest: substrate between trigram and small-neural at generative LM).
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
