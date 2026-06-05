# Prereg: substrate_concept_level_lm_proxy_v1_n2048_gpu
## Anchor
substrate_concept_level_lm_proxy_v1_n2048_gpu
## Routing
EX-CONCEPT-1 substrate-side (P_drill=0.35). PROXY (synthetic V=5000 concept Zipf) -- real Pythia-160M-VQ awaits
extraction pipeline (hung on Llama v6). J-ensemble trigram posbind + symmetric Hebbian, NO cf-RPE. GPU torch, $0.
## Pre-registered bands
HARD-PASS ensemble_ppl < 1.5*sqrt(V)~106 AND <<uniform. MIDDLE [106,212]. HARD-FAIL >3sqrtV.
## Formula self-tests (PROT-022)
roll-bind order / K3 recall / ppl=exp(bpc) / N=2048. [PASS]
## Smoke gate
Smoke (V=500): ensemble_ppl=37.7 (bar 34, uniform 500) -> MIDDLE, captures concept structure (<<uniform). Full V=5000.
## PROT-018/019
_n2048 -> N=2048. timeout 14400s.
## Queue
overnight_queue (GPU torch). NOTE: proxy data; real-Pythia-VQ version pending extraction.
