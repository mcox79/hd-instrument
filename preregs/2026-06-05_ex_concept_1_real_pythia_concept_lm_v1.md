# Prereg: ex_concept_1_real_pythia_concept_lm_v1
## Anchor
ex_concept_1_real_pythia_concept_lm_v1
## Routing
EX-CONCEPT-1 REAL: substrate next-concept-LM on REAL Pythia per-token residuals (VQ V_c=256 -> concept seqs -> Hebbian transition + cleanup). CPU numpy+sklearn $0.
## Bands
HARD-PASS substrate top1 >=1.5x unigram AND >= bigram-Markov. MIDDLE >=1.2x unigram. HARD-FAIL <1.2x.
Smoke (200 docs, V_c=64): substrate=0.613 vs unigram=0.037 (16.3x), >= bigram 0.596 -> HARD_PASS.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
