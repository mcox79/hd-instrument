# Failure Diagnosis: combo1_p3_dam_implicit_gram_v3_n8192_production_envelope_v1
**Date:** 2026-06-02  
**Exit code:** 1 at 9.8s  
**Queue:** overnight_queue (GPU)  

## Root cause
Brand-refresh slope computation at M=N*4 materializes `_G = Xi_sub @ Xi_sub.T` where Xi_sub is (M, N) = (32768, 8192). G = 32768 x 32768 float32 = 4.29 GB. On 8 GB GPU with W matrix (268 MB) + intermediate Krylov buffers = OOM crash at ~9.8s.

## Evidence
- exit_code=1 at 9.8s = early crash (no result written).
- In FULL mode: M_LIST = [N*2=16384, N*4=32768]; Brand refresh at M=32768 creates G = 32768^2 x 4 = 4.29 GB.
- VRAM budget: 8 GB total; W=268MB + G=4.29GB + Krylov buffers easily exceeds 8GB.

## Fix implemented
wave5_cell5_combo1_n65536_LOCAL_stretch_v1 uses alpha=0.05 -> M=3277; M x M Gram = 43MB. The fix is to always bound M by alpha*N, not by N*4. The production_envelope script used M_LIST=[N*2, N*4] which breaks the matrix-free invariant.

## Routing
Strategy: combo1_p3_dam_implicit_gram_v3_n8192 needs a v4 rewrite bounding M by alpha*N (not N*4 multipliers). The stretch test at N=65536 uses this correctly. If n8192 production envelope is needed, use alpha=0.05 -> M=409; G = 409^2 x 4 = 0.67 MB. Not re-shipped in Cycle 11 (superseded by n65536 stretch).
