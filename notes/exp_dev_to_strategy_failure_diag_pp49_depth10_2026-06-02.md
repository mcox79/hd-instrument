# Failure Diagnosis: pp49_hrc_counterfactual_depth_10_v1_n4096
**Date:** 2026-06-02  
**Exit code:** 3221226505 (0xC0000409 = Windows FAST_FAIL_FATAL_APP_EXIT / stack buffer overrun)  
**Queue:** overnight_queue (GPU)  
**Elapsed:** 12.6s  

## Root cause
exit_code=3221226505 is Windows FAST_FAIL_FATAL_APP_EXIT triggered by a stack buffer overrun or heap corruption. At CHAIN_DEPTH=10 with N_CHAINS=10 and N=4096: building H (4096^2 float32 = 67MB) + H_cf (67MB) per chain per depth = 10 chains x 10 depths x 5 seeds with compounding matvec chains. Likely GPU or host memory fault during deep sequential GPU tensor operations. Not a recoverable logic error.

## Evidence
- 12.6s wall time = fast crash after minimal computation.
- 0xC0000409 is not a Python exception; it is OS-level process termination.
- CHAIN_DEPTH=10 is 2x larger than any prior tested depth.
- N_CHAINS=10 x CHAIN_DEPTH=10 = 100 intermediate H allocations per seed.

## Fix implemented
pp49_hrc_counterfactual_depth_5_v1_n4096 (shipped Cycle 11): CHAIN_DEPTH=5, SUBST_DEPTH=3, N_CHAINS=5. Expected peak memory well within 8GB. Calibration probe with wider bands (no prior depth anchor).

## Routing
Strategy: depth-10 PP-49 is blocked at N=4096 by OS-level process fault. Options: (a) reduce N to 2048, (b) reduce N_CHAINS from 10 to 3, (c) restructure to avoid simultaneous H + H_cf tensors. Depth-5 result from Cycle 11 will inform whether depth scaling is feasible at all.
