# Prereg: substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096
## Anchor
substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096
## Routing
audit-core RESCUE: PCA-whiten real residuals before sparse storage (decorrelate -> clean deletion-cert). v1 C2=0.50
(real-residual correlation); v2 whitened C2=0.98. CPU numpy $0. Loads residuals.npz on runner.
## Bands
HARD-PASS C2>=0.95 AND C3-sep>=3x. Laptop full on REAL residuals: C2=0.98 C3=11x -> HARD_PASS.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
