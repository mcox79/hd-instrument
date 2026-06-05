# Prereg: ex_concept_1_real_llama1b_concept_lm_v1
## Anchor
ex_concept_1_real_llama1b_concept_lm_v1
## Routing
Phase 2: EX-CONCEPT-1 REAL at Llama-3.2-1B (VQ real 1B per-token residuals -> concept-LM). CPU $0.
## Bands
HARD-PASS substrate top1 >=1.5x unigram AND >= bigram. MIDDLE >=1.2x. HARD-FAIL <1.2x.
Smoke: substrate 0.727 vs unigram 0.091 (8x), >= bigram 0.716 -> HARD_PASS on real Llama-1B concepts.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
