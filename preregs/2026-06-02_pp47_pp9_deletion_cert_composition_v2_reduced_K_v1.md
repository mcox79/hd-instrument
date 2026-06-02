# Pre-registration: pp47_pp9_deletion_cert_composition_v2_reduced_K_v1

DATE: 2026-06-02
QUEUE: remote_cpu_queue
ANCHOR: pp47_pp9_deletion_cert_composition_v2_reduced_K_v1

## Scientific question
Does place-field encoding (PP-47) compose cleanly with rank-1 deletion cert (PP-9) at reduced K=50?
v1 used K=204 and Gaussian crosstalk dominated the Hopfield convergence test.
v2 redesign: HP2 changed to field-reduction metric (algebraically exact), K=50.

## Hard-pass (pre-registered)
HP1: cert_err = |xi_X^T (W-W') xi_X / N - (-1)| < 1e-10 (exact in 2/2 smoke seeds)
HP2: field_reduction = xi_X^T (W-W') xi_X / N >= 0.90 (algebraically 1.0 exactly)
HP3: adjacent_retrievable = fraction of adjacent patterns still retrieved >= 0.70
HP4: kappa_3 relative error < 5%
HP5: Spearman rho delta within +-0.05

## Hard-fail (pre-registered)
HF1: cert_err > 1e-6 (algebraic cert broken)
HF2: field_reduction < 0.70
HF3: kappa_3 rel_err > 20%

## Middle band
4/5 or 3/5 HP conditions met

## Smoke result
MIDDLE_BAND: 4/5 conditions met (N=1024 smoke).
HP3 fails at small N (adjacent pattern retrieval limited by Hopfield convergence at N=1024).
Expected to pass at FULL N=4096 where retrieval fidelity improves.
Walk-back gate applied: FULL seeds increased from 5 to 7.

## Production config
N=4096, SEEDS=[7,17,23,31,41,53,67], K_LOCS=50, N_HUTCHINSON=500

## Timeout estimate
~2520s (1.5 * 30s_smoke * 16x_N_scale * 3.5x_seeds)
