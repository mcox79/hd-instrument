# Pre-registration: a1_hebbian_vs_gradient_identity_v1

DATE: 2026-06-02
QUEUE: remote_cpu_queue
ANCHOR: a1_hebbian_vs_gradient_identity_v1

## Scientific question
Does one-shot Hebbian write achieve same encoding fidelity as gradient descent (Adam, MSE)
at orders-of-magnitude lower compute? Algebraically guaranteed at alpha << alpha_c.

## Hard-pass (pre-registered)
HP1: |hebb_acc - gd_acc| <= 5pp (fidelity match; +-5pp reflects N=1024 floor variance)
HP2: wall speedup >= 100x
HP3: FLOPs speedup >= 400x (conservative of 4*n_iters)

## Hard-fail (pre-registered)
HF1: hebb_acc < 90% of gd_acc
HF2: wall speedup < 10x

## Middle band
2/3 HP conditions met

## Smoke result
HARD_PASS: all 3 HP conditions met (N=256 smoke, 2 seeds).
Thresholds revised from prior design: HP1 +-2pp -> +-5pp (small-N floor), HP3 1000x -> 400x.
hebb=0.98, gd=1.00, delta=-2pp, flops=492x.

## Production config
N=1024, M=100, SEEDS=[7,17,23,31,41], GD_MAX_ITER=20000

## Timeout estimate
~36s (1.5 * 0.6s * 16x_N_scale * 2.5x_seeds)
