# Prereg: substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu

## Anchor
substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu

## Routing
notes/routing_bundle_a_combined_superadditive_test_2026-06-04.md. Owned GPU, $0.

## Scientific question
Is cf-RPE + Drosophila-sparse SUPERADDITIVE (beyond either alone) at bigram V=512, N=512? 4 arms x 5 seeds:
A1 hebbian (baseline), A2 cfrpe (bipolar+cf-RPE), A3 sparse_hebbian (sparse+symmetric), C_AB (sparse+cf-RPE).
NOTE: corrects Bundle A's conflation -- its "drosophila_sparse" was actually sparse+cf-RPE (=C_AB); A3 here is
the missing pure sparse+symmetric-Hebbian arm.

## Pre-registered bands (BPC nats)
HARD-PASS (superadditive): combined < min(cfrpe, sparse_hebbian) - 0.20 nats AND 4/5 seeds.
MIDDLE (additive): combined in [min-0.20, min+0.05]. HARD-FAIL (substitutive): combined >= min single.

## Formula self-tests (PROT-022)
1. sparse support=f*N unit-norm. 2. cf-RPE shrinks error. 3. zipf cond-ent<log(V). 4. uniform=ln(V). [PASS]

## Smoke gate
Smoke PASSED on remote GPU (N=256, V=128, 2 seeds): all 4 arms run; combined~cfrpe (substitutive preview --
cf-RPE is the main driver, sparse adds little on top). Full N=512/V=512/5-seed is the registered test.

## PROT-018 / 021
_n512 -> N=512. timeout 14400s. 5 seeds.

## Queue
overnight_queue (GPU).
