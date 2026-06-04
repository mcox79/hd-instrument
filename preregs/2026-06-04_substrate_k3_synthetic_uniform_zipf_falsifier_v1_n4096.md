# Prereg: substrate_k3_synthetic_uniform_zipf_falsifier_v1_n4096
## Anchor
substrate_k3_synthetic_uniform_zipf_falsifier_v1_n4096
## Routing
routing_k3_synthetic_uniform_zipf_falsifier_test_2026-06-04. Isolates whether the Zipf marginal is load-bearing
for Bundle E's K=3 trigram HP. CPU numpy. Self-contained 2-arm design (2nd-order Markov; zipf vs uniform target
selection = skewed vs flat marginal; posbind K=3 + symmetric Hebbian both arms). 5 seeds. V=70, N=4096.
## Pre-registered bands (verdict on the UNIFORM arm; gap nats)
HARD-FAIL (Zipf load-bearing): uniform gap<0.5 AND <=1/5 seeds>0.5. MIDDLE: uniform gap in [0.5,0.8].
HARD-PASS (Zipf NOT load-bearing): uniform gap>0.8 AND 4/5 seeds. zipf arm reported as in-harness reference.
## Formula self-tests (PROT-022)
roll-bind order-sensitive / K=3 recall>0.5 / zipf marginal entropy<uniform (manipulation works) / uniform=ln(V). [PASS]
## Smoke gate
Smoke (N=256,V=40): mechanics+manipulation PASS (zipf_ent 3.17<unif 3.38; uniform gap 0.13<<zipf 0.45). Full N=4096 decides.
## PROT-018/019/021
_n4096 -> N=4096. timeout floor 14400s. 5 seeds, per-seed partials.
## Queue
remote_cpu_queue (numpy; GPU not needed).
