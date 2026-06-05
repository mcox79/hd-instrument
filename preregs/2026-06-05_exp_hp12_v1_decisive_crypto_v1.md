# Prereg: exp_hp12_v1_decisive_crypto_v1
## Anchor
exp_hp12_v1_decisive_crypto_v1
## Routing
HP-12 V1 decisive Test 2: RSA accumulator round-trip + standalone verifier CLI + tamper-detection (Day-1 crypto de-risk). CPU pure-Python $0.
## Bands
HARD-PASS all certs verify third-party AND latency<1ms AND tamper-rejected AND verifier-CLI-ok. MIDDLE certs verify+tamper-safe, latency gmpy2-gated. HARD-FAIL cert/tamper fail.
Smoke: verified 1.0, tamper-rejected 1.0, verifier-CLI ok, issuance latency 3.46ms (RSA-512 pure-Python) -> MIDDLE (gmpy2 install -> <1ms).
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
