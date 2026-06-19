# Prereg: exp_hp12_v1_api_surface_test_v1
## Anchor
exp_hp12_v1_api_surface_test_v1
## Routing
HP-12 V1 HIPAA API surface (4 endpoints: post_fact/query/delete_fact/get_audit) e2e test. CPU $0.
## Bands
HARD-PASS all 4 endpoints + recall>0.95 + audit-verified + 0-phantom + retention>0.95. MIDDLE phantom<1%. HARD-FAIL endpoint/cert/phantom fail.
Smoke: endpoints_ok, recall 1.0, audit 1.0, phantom 0.0, retention 1.0 -> HARD_PASS.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
