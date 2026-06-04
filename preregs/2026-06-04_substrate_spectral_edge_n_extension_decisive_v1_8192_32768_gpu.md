# Prereg: substrate_spectral_edge_n_extension_decisive_v1_8192_32768_gpu

## Anchor
substrate_spectral_edge_n_extension_decisive_v1_8192_32768_gpu

## Routing
notes/routing_n_extension_test_n32768_decisive_arbiter_2026-06-04.md (HIGH PRIORITY, product-critical) +
notes/product_critical_deletion_cert_sigma_recalibration_2026-06-04.md. Resolves PP-50 v4's ambiguous
beta_std=0.355 (BBP-critical 1/3 vs Gaussian 1/2 vs TW 2/3) + calibrates the deletion-cert sigma threshold.

## Scientific question
lambda_1 (largest eigenvalue, power iteration) of noisy Wishart W=Xi_noisy Xi_noisy^T/N; PRIMARY observable
std(lambda_1) across 20 seeds; fit beta_local = -slope of ln(std) vs ln(N). N in {8192,16384,32768},
sigma_g=0.8, alpha=0.05, additive-on-patterns noise. Report beta_local + bootstrap 95% CI.

## Pre-registered bands (beta_local)
HARD-PASS (BBP-critical): beta in [0.28,0.40] -> deletion-cert sigma gets ~5x recalibration.
MIDDLE: beta in [0.40,0.55] (mixed regime).
HARD-FAIL: beta>0.55 (TW restored; BBP refuted) OR beta<0.20 (noise floor).

## Formula self-tests (PROT-022)
1. power_iteration(diag[5,2,1])=5. 2. (16384/8192)^(-1/3)=0.7937. 3. bootstrap CI no-crash. [PASS]

## Smoke gate
Smoke PASSED on remote GPU (N={1024,2048}, 4 seeds): self-test green; lambda_1 + bootstrap CI compute;
verdict noisy (2-point/4-seed) -- full 3-point/20-seed run gives tight CI.

## PROT-018 / 021
NO _nN suffix (N swept {8192,16384,32768}; declared _8192_32768). timeout 14400s. 20 seeds.

## Queue
overnight_queue (GPU).
