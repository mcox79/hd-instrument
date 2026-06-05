# Prereg: substrate_audit_core_C2_C3_pythia160m_residuals_v1_n4096
## Anchor
substrate_audit_core_C2_C3_pythia160m_residuals_v1_n4096
## Routing
Pythia extraction HARD_PASS -> audit-core on REAL residuals. C2 deletion-cert (HIPAA/GDPR wedge; unavailable in
fine-tuned LLMs) + C3 drift detection. Tier-1 product anchor. CPU numpy $0. Loads residuals.npz on runner.
## Bands
HARD-PASS C2>=0.95 AND C3-separation>=3x. MIDDLE one. HARD-FAIL neither. Smoke (synthetic): C2=1.00 C3=7.4x HARD_PASS.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
