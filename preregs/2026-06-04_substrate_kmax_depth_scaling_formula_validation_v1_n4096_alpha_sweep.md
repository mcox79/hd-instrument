# Prereg: substrate_kmax_depth_scaling_formula_validation_v1_n4096_alpha_sweep
## Anchor
substrate_kmax_depth_scaling_formula_validation_v1_n4096_alpha_sweep
## Routing
overnight NEW EXP 1. Validate K_max=3.3(1-a/ac)^2/a depth formula. Background-LOAD (M random transitions) separated
from probe-chain DEPTH (redesigned). CPU numpy $0.
## Bands
HARD-PASS median rel-err<=25%. MIDDLE <=50%. HARD-FAIL >50% (formula needs revision). NOTE: smoke shows formula
appears PESSIMISTIC (substrate reasons to K_CAP regardless of load); full N=4096 K_CAP=50 gives the real curve, high-load points test shallow predictions.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
