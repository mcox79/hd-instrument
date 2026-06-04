# Prereg: substrate_spectral_edge_n_extension_finer_v2_4096_65536_gpu
## Anchor
substrate_spectral_edge_n_extension_finer_v2_4096_65536_gpu
## Routing
Finer follow-up to substrate_spectral_edge_n_extension_decisive_v1 (HARD_PASS beta=0.331 BBP-critical but
wide CI [-0.09,0.71]) per product_critical_deletion_cert_sigma_recalibration. 5 N points + 50 seeds tightens
the N-point-limited slope CI -> sharpens the deletion-cert sigma recalibration constant. Owned GPU, $0.
## Scientific question
beta_local of std(lambda_1) across seeds (5 N {4096,8192,16384,32768,65536} x 50 seeds, additive-on-patterns
noise, sigma_g=0.8). Resolve BBP-critical(1/3) vs Gaussian(1/2) vs TW(2/3) with a tight bootstrap 95% CI.
## Pre-registered bands (beta_local)
HARD-PASS BBP-critical: beta in [0.28,0.40]. MIDDLE [0.40,0.55]. HARD-FAIL beta>0.55 (TW) or <0.20 (noise).
## Formula self-tests (PROT-022)
power_iteration(diag)=5 / N^-1/3 scaling / bootstrap CI no-crash. [PASS]
## Smoke gate
Smoke PASSED on remote GPU (reduced grid/seeds, verdict noisy as expected). Full 5-N/50-seed gives tight CI.
## PROT-018 / 021
No _nN suffix (N swept 4096..65536). 50 seeds. timeout 14400s.
## Queue
overnight_queue (GPU; lambda_1 power iteration on M x M Gram, M=0.05N; matrix-free, fits 8GB).
