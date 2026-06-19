# Prereg: substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu

## Anchor
substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu

## Routing
notes/routing_bundled_substrate_explorations_for_gpu_occupancy_2026-06-04.md, Bundle D. TRIGGERED by
Bundle A drosophila_sparse=HP (the routing's pre-registered dispatch condition for Bundle D).

## Scientific question
At what sparse-coding density f does the Drosophila-MB substrate (sparse codes + single cf-RPE modulator)
maximize BPC gain over dense bipolar? f in {dense, 0.50, 0.25, 0.10, 0.05, 0.02, 0.01, single} x N in
{512, 2048}, 3 seeds, synthetic V=512 Zipf bigram, cf-RPE delta rule. Maps optimal density f*.

## Pre-registered bands (gap = dense_nats - sparse_nats at matched N)
HARD-PASS: ANY f<=0.10 beats dense by >0.30 nats AND 3/3 seeds. MIDDLE: best in [0.10,0.30]. HARD-FAIL:
dense >= all sparse. Reports f* = argmax gap.

## Formula self-tests (PROT-022)
1. sparse support=round(f*N), unit-norm. 2. single=1 active. 3. cf-RPE shrinks error. 4. uniform=ln(V). [PASS]

## Smoke gate
Smoke PASSED (N=256, V=128, 2 seeds): self-test green; all f values run; sparse~dense at tiny scale (HARD_FAIL
preview -- f* advantage needs full N=512/2048, V=512). Full run is the registered test.

## PROT-018 / 021
NO _nN suffix; N swept {512,2048} (declared as _512_2048). timeout 14400s. 3 seeds.

## Queue
overnight_queue (GPU).
