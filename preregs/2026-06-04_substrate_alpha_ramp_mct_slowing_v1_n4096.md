# Prereg: substrate_alpha_ramp_mct_slowing_v1_n4096
## Anchor
substrate_alpha_ramp_mct_slowing_v1_n4096
## Routing
exp_dev_handoff_research_cross_domain_interference_capacity_degradation (anchor 1). CPU numpy, $0.
## Scientific question
(a) graceful (acc>95% below 0.85*alpha_c) -> catastrophic (drop at alpha_c=0.138) capacity curve, establishing
M<0.85*alpha_c*N operational safety constant; (b) MCT: does sign-convergence step-count diverge near alpha_c
(free capacity early-warning)? Auto-assoc Hopfield, N=4096, alpha grid {0.02..0.20}, 3 seeds.
## Pre-registered bands
HARD-PASS: graceful (frac>0.95 at alpha<=0.117) AND catastrophic drop>0.30 (0.117->0.16) AND MCT steps ratio
(alpha>=0.138 vs <=0.08) > 1.5x. MIDDLE: drop 0.15-0.30 or mct 1.2-1.5x. HARD-FAIL: no graceful zone or no transition.
## Formula self-tests (PROT-022)
low-load frac~1 / alpha_c=0.138 / steps>=1 / overlap in [-1,1]. [PASS]
## Smoke gate
Smoke PASSED (N=512): HARD_PASS -- graceful->catastrophic (1.0->0.97->0.85->0.64->0.14), MCT ratio 10.3x.
## PROT-018/019/021
_n4096 -> N=4096. timeout floor 14400s. 3 seeds.
## Queue
remote_cpu_queue (numpy; GPU not needed).
