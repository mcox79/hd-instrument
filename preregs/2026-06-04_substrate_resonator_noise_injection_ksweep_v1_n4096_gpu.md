# Prereg: substrate_resonator_noise_injection_ksweep_v1_n4096_gpu
## Anchor
substrate_resonator_noise_injection_ksweep_v1_n4096_gpu
## Routing
change_request_mode4_resonator_add_sparse_noise_injection_cells (Cell R5 noise-injection, arXiv:2412.00354)
+ routing_mode4_resonator_falsifier (K=5 baseline). GPU, $0. The change-request's R4 sparse-block-code cell
is DEFERRED (distinct architecture; needs literature-verified block-code binding before implementation).
## Scientific question
Does per-iteration annealed data-adaptive noise-injection (stochastic resonance) let a dense resonator escape
limit cycles and recover MORE factors than the deterministic baseline at N=4096? Arms {baseline,noise} x
K{5,10,20,30,50}, V=512, B=128, T=100, 5 seeds. recovery = frac trials with ALL K factors recovered.
## Pre-registered bands
per-K thr: 5->0.85, 10/20/30->0.70, 50->0.60; K_max = largest K passing thr in >=4/5 seeds.
HARD-PASS: noise K_max>=20 AND noise K_max>baseline. MIDDLE: noise K_max>baseline but <20. HARD-FAIL: noise<=baseline.
P deflated (lit-scan calibration): novel-synthesis cap ~0.30 for the 50x claim.
## Formula self-tests (PROT-022)
bind self-inverse / K=2 baseline recovers (mechanism, chance~1/V^2) / argmax cleanup / sigma anneals to 0. [PASS]
## Smoke gate
Smoke (N=512): mechanics PASS; K=5+ saturates at 0 for both arms (N=512 too small) -- N=4096 is the test.
## PROT-018/019/021
_n4096 -> N=4096. timeout floor 14400s. 5 seeds, per-seed partials.
## Queue
overnight_queue (GPU; queues behind Llama v6).
