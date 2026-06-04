# Prereg: substrate_arch_ablation_matrix_bigram_v1_n512_gpu

## Anchor
substrate_arch_ablation_matrix_bigram_v1_n512_gpu

## Routing
notes/routing_bundled_substrate_explorations_for_gpu_occupancy_2026-06-04.md, Bundle A -- the IMMEDIATE
highest-value dispatch; REPLACES the 7-individual-test convergent batch (same coverage, one dispatch).

## Scientific question
Of the 7 brain-drill architectural variants, which beat the K=1 Hebbian baseline at a synthetic V=512 Zipf
bigram task (deliberately harder than wikitext char-bigram, which saturated all architectures)? 7 variants x
5 seeds = 35 cells, N=512, 1000 steps. Variants: hebbian_k1, cfrpe, drosophila_sparse (f=0.05),
stdp_asym (W_Heb + 0.5 W_STDP antisymmetric), friston_fep (precision-weighted cf-RPE), two_region
(N/2 bipolar + N/2 sparse), bottleneck_adaptor (K=8 experts + bottleneck router). Calibrated-temp readout (nats).

## Pre-registered bands (per-variant; gap = baseline_nats - variant_nats)
HP: variant beats K=1 by >0.30 nats AND 4/5 seeds. MIDDLE: 0.10-0.30 nats. HARD-FAIL: variant>=baseline.
AGGREGATE: HARD-PASS if ANY non-baseline variant HP; HARD-FAIL if ALL 6 HF; MIDDLE otherwise.

## Formula self-tests (PROT-022)
1. Zipf bigram cond-entropy < log(V). 2. cf-RPE shrinks error. 3. STDP antisym part W+W^T=0.
4. sparse support=f*N. 5. uniform nats=ln(V). [ALL PASS]

## Smoke gate
Smoke PASSED on remote GPU (N=256, V=128, 2 seeds): self-test green; task DISCRIMINATES -- cfrpe(+0.39 HP),
bottleneck_adaptor(+0.38 HP), drosophila_sparse(+0.28 MID), two_region(+0.30 MID), stdp_asym(~0 HF),
friston_fep(-0.68 HF). Full N=512/V=512/5-seed is the registered test.

## PROT-018 / 019 / 021
_n512 -> N=512. timeout 14400s. 5 seeds; partials keyed seed+run_mode.

## Queue
overnight_queue (GPU).
