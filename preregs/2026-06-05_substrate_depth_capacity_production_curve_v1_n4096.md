# Prereg: substrate_depth_capacity_production_curve_v1_n4096
## Anchor
substrate_depth_capacity_production_curve_v1_n4096
## Routing
Consolidation: depth-vs-load curve for plain vs cleanup-augmented retrieval (production knob). Combines K_max
load-sweep + NEW EXP 3 cleanup. CPU numpy $0.
## Bands
HARD-PASS high-load cleanup/plain>=1.5x. Smoke: lf1=24/24 lf2=4/24 lf3=0/24 -> 15x at high load HARD_PASS.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
