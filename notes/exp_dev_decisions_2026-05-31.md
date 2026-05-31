# exp_dev decisions 2026-05-31

- Shipped modern_hopfield_cpu_extended_v9_n16384 to remote_cpu_queue: M sweep {4N,8N,16N} at N=16384 (86400s timeout). Smoke PASS (max_M=4096 at N=1024). REMOTE VERIFY PASS. Extends C1 ceiling test past 4N.
- Shipped query_margin_gate_smoke_v1_n4096 to remote_cpu_queue: Pareto defense smoke (p2_defense_rate vs legit_fpr) at N=4096 M=2048 depth=5 (14400s; PROT-019 floor). Smoke PASS (pre-registered HARD_FAIL pattern at smoke scale). REMOTE VERIFY PASS. PROT-019 required bump from 7200 to 14400s.
