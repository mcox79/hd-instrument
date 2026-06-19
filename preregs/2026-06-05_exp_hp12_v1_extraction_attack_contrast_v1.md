# Prereg: exp_hp12_v1_extraction_attack_contrast_v1
## Anchor
exp_hp12_v1_extraction_attack_contrast_v1
## Routing
HP-12 V1 deletion moat: extraction-attack (blackbox direct+perturbed, whitebox weight-probe) post-deletion vs ROME 38%/MEMIT 29%. CPU $0.
## Bands
HARD-PASS residual<=1% AND retention>0.95. MIDDLE <=5%. HARD-FAIL >10%.
Smoke: pre-extractable 1.0 -> post-residual 0.0, retention 1.0 -> HARD_PASS (categorical deletion).
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
