# Prereg: substrate_capacity_sweep_n32768_asymptotic_alpha_v1
## Anchor
substrate_capacity_sweep_n32768_asymptotic_alpha_v1
## Routing
Research two_regime_alpha Cell-2 (Tier-1 gate): confirm alpha=0.040 asymptote at N=32768 before Phase-3 N=65536 commit. W-free Hopfield. CPU $0.
## Bands
HARD-PASS alpha@N32768 in [0.038,0.045]. MIDDLE [0.030,0.038). HARD-FAIL <0.030 or >0.050.
Smoke reproduces two-regime trend (0.0596@N2048 -> 0.0498@N4096); full reaches N=32768.
## Queue
remote_cpu_queue 14400s. PROT-022 PASS (W-free==explicit-W self-test).
