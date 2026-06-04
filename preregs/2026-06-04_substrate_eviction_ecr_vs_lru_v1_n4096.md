# Prereg: substrate_eviction_ecr_vs_lru_v1_n4096
## Anchor
substrate_eviction_ecr_vs_lru_v1_n4096
## Routing
cross_domain_interference handoff anchor 2 (ECR-vs-LRU eviction). CPU numpy, $0.
## Scientific question
At 90% of alpha_c capacity, does Energy-Contribution-Ranked eviction (keep best-stored) maintain >95%
retrieval where LRU (evict oldest) degrades <90%? Audit-preserving eviction primitive. Stream 3*M_cap bipolar
patterns through an M_cap=0.90*0.138*N bank, N=4096, 3 seeds, policy in {LRU,ECR}.
## Pre-registered bands (retrieval = frac banked with self-overlap>0.95)
HARD-PASS: ECR>0.95 AND LRU<0.90. MIDDLE: ECR-LRU>0.03. HARD-FAIL: ECR<=LRU.
## Formula self-tests (PROT-022)
low-load recall / eviction changes ||W|| / alpha_c=0.138. [PASS]
## Smoke gate
Smoke (N=512): both 1.0 (finite-size; M_cap=63 at alpha=0.124 recalls perfectly at tiny N). Full N=4096 enters
the degradation zone where policy can diverge. Non-difference would itself be informative (policy moot in graceful zone).
## PROT-018/019/021
_n4096 -> N=4096. timeout floor 14400s. 3 seeds.
## Queue
remote_cpu_queue (numpy; GPU not needed).
