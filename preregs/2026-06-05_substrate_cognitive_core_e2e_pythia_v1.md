# Prereg: substrate_cognitive_core_e2e_pythia_v1
## Anchor
substrate_cognitive_core_e2e_pythia_v1
## Routing
HP-7: integrated cognitive-core e2e (retrieval->filter->Rule8 beta*->Bridge-A->Pythia + audit cert chain) vs Pythia-raw on multi-evidence QA. GPU $0.
## Bands
HARD-PASS substrate>=1.5x Pythia-raw AND cert reconstructible>=0.99. MIDDLE >=1.2x OR cert-only. HARD-FAIL <1.2x.
Smoke: substrate 1.0 / Pythia-raw 0.675 (1.48x) + cert 1.0 -> MIDDLE/borderline-HP. Note: single-evid=1.0 (retrieval easy; combination not isolated). Cert-chain auditability demonstrated.
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
