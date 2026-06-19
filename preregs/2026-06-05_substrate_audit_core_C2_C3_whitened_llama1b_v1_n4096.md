# Prereg: substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096
## Anchor
substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096
## Routing
Phase 2: audit-core C2 deletion-cert + C3 drift on REAL Llama-1B residuals (last-token slice 10000x2048). HIPAA/GDPR wedge at 1B. CPU $0.
## Bands
HARD-PASS C2>=0.9 AND C3 drift-sep>=3x. MIDDLE one. HARD-FAIL neither.
Full(real): C2=1.00 C3=15.5x -> HARD_PASS. Fix: whiten newb into store-space (orig dim 2048>M).
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
