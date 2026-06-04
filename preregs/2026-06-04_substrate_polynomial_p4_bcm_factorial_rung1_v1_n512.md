# Prereg: substrate_polynomial_p4_bcm_factorial_rung1_v1_n512

## Anchor
substrate_polynomial_p4_bcm_factorial_rung1_v1_n512

## Priority
A (Q3 GREEN; polynomial-p modern-Hopfield upgrade + bcm_snr_poly_p factorial). Tests whether
polynomial-p=4 retrieval lowers the substrate-as-training capacity floor at small N.

## Scientific question
2x2 factorial (p=2 vs p=4) x (cumulative vs episodic E=200) at N=512. Modern-Hopfield polynomial-p
retrieval (bipolar, Demircigil 2017): weight_k = sign(sim)*|sim|^(p-1), sim=ctx.key/N. Calibrated-temp
BPC readout. Does p=4 learn (BPC < uniform-1.0) where classical p=2 fails, and beat p=2 at matched mode?

## Pre-registered bands (BITS)
HARD-PASS: best p4 arm BPC < uniform-1.0 on >=2/3 seeds AND p4 beats p2 at matched mode by >0.3 bit.
MIDDLE: p4 partial (BPC<uniform-0.5) OR p4>p2 but <0.3 bit OR 1/3 seeds.
HARD-FAIL: p4 no better than p2 (upgrade does not help) OR no arm learns (all within 0.3 bit of uniform).

## Formula self-tests (PROT-022)
1. p4 single-pair recall cosine>0.9. 2. poly sharpening (1/0.5)^3=8 at p4. 3. uniform_bpc=log2(vocab)>0. [PASS]

## N-suffix binding (PROT-018)
anchor _n512; production N=512. 3 seeds (PROT-021).

## Timeout
4 arms x 3 seeds, bank retrieval at N=512; timeout_s=7200.

## Smoke gate
Smoke PASSED (N=128, 2 seeds): all arms run; p4_cumulative > p2_cumulative contrast emerging (+0.14/+0.26
vs ~0); episodic arms negative at tiny N (limited bigram coverage) -- full N=512 is the real test.

## Queue
remote_cpu_queue (CPU; pure numpy).
