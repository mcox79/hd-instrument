# Prereg: exp_hp12_v1_end_to_end_demo_backend_v1
## Anchor
exp_hp12_v1_end_to_end_demo_backend_v1
## Routing
HP-12 V1 demo BACKEND e2e: pre-seed + live-ingest + query + delete+RSA-cert + third-party-verify + 0-phantom re-query. CPU $0.
## Bands
HARD-PASS write<1ms AND live-recall>0.95 AND certs-verified AND 0-phantom AND retention>0.95. MIDDLE recall>0.90+0-phantom, write ms-scale. HARD-FAIL phantom OR cert-fail.
Smoke: live-recall 1.0, certs 1.0, phantom 0.0, retention 1.0; write 7.4ms@N2048 (ms-scale real-time, <1ms needs bf16/BLAS) -> MIDDLE.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
