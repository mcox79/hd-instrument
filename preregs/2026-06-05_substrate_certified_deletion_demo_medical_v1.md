# Prereg: substrate_certified_deletion_demo_medical_v1
## Anchor
substrate_certified_deletion_demo_medical_v1
## Routing
HP-12 core (THE killer demo): certified per-fact deletion -- substrate KB + RSA crypto accumulator + third-party verifier + 0 phantom. CPU $0.
## Bands
HARD-PASS cert<1ms AND 0 phantom AND verifier>=0.999 AND retention high. MIDDLE latency 1-10ms OR <1% phantom. HARD-FAIL phantom OR verifier fail.
Smoke: cert 0.512ms, phantom 0.0, verifier 1.0, retention 1.0 -> HARD_PASS. (1M-fact full demo needs sparse FAISS storage; core mechanism validated.)
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
