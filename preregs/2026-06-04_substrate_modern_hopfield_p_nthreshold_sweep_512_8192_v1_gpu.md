# Prereg: substrate_modern_hopfield_p_nthreshold_sweep_512_8192_v1_gpu

## Anchor
substrate_modern_hopfield_p_nthreshold_sweep_512_8192_v1_gpu

## Routing
notes/research_drill_substrate_training_n_threshold_3x_2026-06-04.md (sub-q4 + cross-thread: modern Hopfield
would lower N_threshold from ~3500 to ~500-1000) + research_drill_modern_hopfield_upgrade_path_3x. GPU.

## Scientific question
Does modern-Hopfield polynomial-p=4 retrieval (weight=sign(sim)|sim|^(p-1)) reach char-LM bigram learning at
a SMALLER code dim N than classical p=2 (lower the N_threshold)? Bank of M=3000 sampled bigram pairs (fixed
across cells); p in {2,4} x N in {512,1024,2048,3072,4096,8192}; 3 seeds; calibrated-temp readout; BPC gap
in nats. Unit-norm codes -> sim is cosine.

## Pre-registered bands (threshold = smallest N with gap>=0.5 nat)
HARD-PASS: N_thresh(p4) < N_thresh(p2) AND p4 gap@8192 >= 1.0 -> modern Hopfield lowers N_threshold.
MIDDLE: p4 >= p2 at matched N but N_thresh not strictly lower.
HARD-FAIL: p4 <= p2 across N (no benefit) OR neither reaches gap>=0.5 at any N.

## Formula self-tests (PROT-022)
1. poly sharpening (1/0.5)^3=8 vs ^1=2. 2. single-pair p4 recall cos>0.9 (=1.000). 3. uniform nats=ln(V). [PASS]

## Smoke gate
Smoke PASSED on remote GPU (N={256,512}, 2 seeds, p={2,4}): self-test green; both p learn (gap~1.0); no
threshold difference at tiny N (-> MIDDLE). Full {512..8192} x M_bank=3000 reveals threshold-lowering.

## PROT-018 / 021
NO _nN suffix (N swept). timeout 21600s. 3 seeds.

## Queue
overnight_queue (GPU).
