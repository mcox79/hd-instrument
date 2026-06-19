# Prereg: substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu
## Anchor
substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu
## Routing
EX1 fair-value fix (my caveat: bigram beats substrate on 1st-order). 2nd-order Markov + trigram posbind context
-> substrate sees structure bigram-count cannot. J=10 ensemble, NO cf-RPE. GPU torch, $0. overnight_queue.
## Pre-registered bands (value test)
HARD-PASS ensemble_ppl < bigram_count_ppl AND ppl<20. MIDDLE: beats bigram but ppl>=20. HARD-FAIL: doesn't beat bigram.
## Formula self-tests (PROT-022)
roll-bind order-sensitive / K3 recall / ppl=exp(bpc) / N=8192. [PASS]
## Smoke gate
Smoke (N=512): ensemble=57.0 BEATS bigram_count=60.4 (substrate adds value); ppl>20 (small N). Full N=8192 -> lower ppl.
## PROT-018/019
_n8192 -> N=8192. timeout floor 21600s.
## Queue
overnight_queue (GPU torch).
