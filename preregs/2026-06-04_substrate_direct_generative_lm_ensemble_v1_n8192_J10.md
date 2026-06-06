# Prereg: substrate_direct_generative_lm_ensemble_v1_n8192_J10
## Anchor
substrate_direct_generative_lm_ensemble_v1_n8192_J10
## Routing
research_to_exp_dev_B8_validated...substrate_direct_LM (EX1-revised; P_drill=0.25; NO cf-RPE per drill -- it
inverts for generation). J=10 ensemble substrate char-LM perplexity. CPU numpy, $0. remote_cpu_queue.
## Scientific question
Does a J=10 ensemble of substrate char-LMs (posbind + symmetric Hebbian, disjoint splits) reach ppl<20? vs single + bigram baseline.
## Pre-registered bands (ensemble perplexity)
HARD-PASS ppl<20. MIDDLE 20-40. HARD-FAIL ppl>60.
## Formula self-tests (PROT-022)
symmetric-Hebbian recall / dist normalized / ppl=exp(bpc) / N=8192. [PASS]
## Smoke gate + HONEST CAVEAT
Smoke (N=512, J=4): ensemble_ppl=7.4 (HP<20), ensemble<single(8.6). BUT bigram-count baseline=5.5 BEATS the
substrate -- expected: synthetic Zipf-bigram is a pure counting task, so counting is optimal. The ppl<20 bar is
trivially met on synthetic; the MEANINGFUL test (does substrate add value over counting?) needs REAL higher-order
data (Wikitext). This run measures ensemble-scaling (J=10 vs single) + ppl at N=8192; a Wikitext follow-up is the fair value test (flagged to Research).
## PROT-018/019
_n8192 -> N=8192. timeout floor 21600s.
## Queue
remote_cpu_queue (numpy).
