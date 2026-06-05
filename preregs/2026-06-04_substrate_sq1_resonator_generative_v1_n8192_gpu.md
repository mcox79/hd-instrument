# Prereg: substrate_sq1_resonator_generative_v1_n8192_gpu
## Anchor
substrate_sq1_resonator_generative_v1_n8192_gpu
## Routing
SQ1 (P_drill=0.68). Resonator-generative: resolve novel V^K factor-products (compositional creativity, the
drill's substrate-direct language path). GPU torch, $0. overnight_queue.
## Pre-registered bands (Kmax = max K with recovery>=0.95; generative space V^Kmax)
HARD-PASS V^Kmax>=1e12 (Kmax>=6 @ V=100). MIDDLE V^Kmax in [1e8,1e12). HARD-FAIL Kmax<4.
## Formula self-tests (PROT-022)
bind self-inverse / K=2 resolves / codebook bipolar / N=8192. [PASS]
## Smoke gate
Smoke (N=512,V=50): K=2 perfect, K=4 capacity-limited (small N). Full N=8192 + noise-injection resolves higher K.
## PROT-018/019
_n8192 -> N=8192. timeout floor 21600s.
## Queue
overnight_queue (GPU torch).
