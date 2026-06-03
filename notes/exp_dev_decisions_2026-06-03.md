# exp_dev Decisions 2026-06-03

## Cycle 22 refill (v351 REFILL, 2026-06-03)

Shipped 5 anchors from v343 consolidated priority queue Sections 1+5. All 5 REMOTE VERIFIED via queue_add.sh exit-0 + VERIFIED log line.

**GPU (overnight_queue):**
- q_a3_l20_cross_layer_composition_v1_n4096: L=20 PP-12 ceiling chase. Smoke HARD_PASS (all 20 EXACT-1.0, 0.22s). PROT-018 N=4096. timeout=14400s.
- q_a3_l21_cross_layer_composition_v1_n4096: L=21 PP-12 ceiling chase. Smoke HARD_PASS (all 21 EXACT-1.0, 0.23s). PROT-018 N=4096. timeout=14400s.
- q_b1_chain_depth_150_v1_n16384: Q-B1 d-150 BAND-LIFT candidate. Smoke scale-artifact HF at N=1024 (same pattern as d-100 which HARD_PASSED at N=16384). Self-test PASS. PROT-018 N=16384. timeout=21600s.
- capacity_phase_boundary_larger_n_v2_n8192: Item 21 larger N Wave-2 prediction test. Smoke MIDDLE_BAND (transition signal valid, scale artifact). PROT-018 N=8192. timeout=21600s.

**CPU (remote_cpu_queue):**
- pp58_isochoric_kappa3_alpha_sweep_v1_n4096: PP-58 isochoric audit two-envelope test. Smoke MIDDLE_BAND ratio=8x (two-envelope separation confirmed at smoke scale; audit_crit location N-dependent). PROT-018 N=4096. Hutchinson kappa_3 estimator; 50 probes FULL. timeout=14400s.

**v343 items shipped:** A (Q-A3 L=20+L=21), B (Q-B1 d-150), C (PP-58), F (Item 21 larger N).

**v343 items deferred (not in this batch):** D (PP-55 second confirm), E (PP-12 cross-N N=8192), G (Wave-3 lit-scan items). Reason: 5 anchor cap reached; priority order per v343 Section 5 Wave A dispatch order.
2026-06-03 CYCLE 22 queue refill (3 anchors): q_a3_l22_cross_layer_composition_v1_n4096 -> overnight_queue (HP Q-A3 L-ceiling chase L=22 #8); q_b1_chain_depth_200_v1_n16384 -> overnight_queue (HP Q-B1 d-200 ceiling probe N=16384); pp58_isochoric_kappa3_multialpha_v1_n4096 -> remote_cpu_queue (MIDDLE PP-58 R3 multi-alpha audit_crit recalibration). All REMOTE VERIFIED. PP-58 smoke bug fixed (baseline-relative audit_crit detection).
## Cycle 22 v352 REFILL (2026-06-03 batch 2)

Shipped 5 anchors. GPU overnight_queue (2), CPU remote_cpu_queue (3).

GPU:
- q_a3_l19_n_scale_v1_n8192: Q-A3 N-scale at L=19 (cycle22 #2). timeout=21600s. REMOTE VERIFIED.
- q_b1_chain_depth_200_v1_n16384: Q-B1 d-200 ceiling (task B). Already present from prior session. REMOTE VERIFIED.

CPU:
- activation_barrier_r3_theory_proxy_v1_n4096: PP-33 R3 theory rescue (cycle22 #1). Smoke MIDDLE_BAND. timeout=14400s. REMOTE VERIFIED.
- pp56_sherman_morrison_cert_drop_n16384_v3_n16384: PP-56 N=16384 band-lift gate (cycle22 #3). Smoke HARD_PASS cert_ratio=0.00097. timeout=21600s. REMOTE VERIFIED.
- vsa_binding_n8192_v2_n8192: PP-55 N-scale N=8192 (cycle22 #4). Smoke MIDDLE_BAND cos=1.0. timeout=21600s. REMOTE VERIFIED.

REMOTE VERIFY: 5/5 present in remote queues.
v353 refill cycle: shipped 5 anchors. overnight_queue(GPU): q_a3_l23_cross_layer_composition_v1_n4096 (L=23 ceiling chase, timeout=14400s), q_a3_l24_cross_layer_composition_v1_n4096 (L=24 ceiling chase simultaneous, timeout=14400s), q_b1_chain_depth_300_v1_n16384 (d-300 flat-profile test, timeout=21600s). remote_cpu_queue: pp55_vsa_binding_n16384_v3_n16384 (PP-55 3rd rung band-lift gate, timeout=21600s), pp58_isochoric_kappa3_n8192_v4_n8192 (PP-58 R4 N-scale calibration probe, timeout=21600s). All 5 PROT-018/019/021/022 compliant. Remote verify: 5/5 pass.2026-06-03 CYCLE 23 queue refill (3 anchors, post-v354 batch):
GPU overnight_queue:
- q_a3_l22_cross_layer_composition_v1_n8192: Q-A3 PP-12 N-scale at L=22. L=22 HP at N=4096 (v354); L=19 N=8192 HP (v354). N-scale probe: confirms N-independence extends to L=22. PROT-018 N=8192. PROT-019 timeout=21600s (floor). REMOTE VERIFIED.
CPU remote_cpu_queue:
- activation_barrier_r3_extended_grid_v2_n4096: PP-33 R3a extended grid. v1 MIDDLE (nf_crit at grid boundary 0.60). v2 extends to 0.90 step 0.01 (91 points). Bug fix: None-formatting in compute_verdict. PROT-018 N=4096. timeout=14400s. REMOTE VERIFIED.
- pp58_isochoric_kappa3_finergrid_v2_n4096: PP-58 R3b finer sigma_g grid. v1 MIDDLE (audit_crit grid-limited at sigma_g=1.0). v2 step=0.1 (21 points 0.0..2.0). Bug fix: selftest kappa3 bounds (0.01,2.0). PROT-018 N=4096. timeout=14400s. REMOTE VERIFIED.
All 3 PROT-018/019/021/022 compliant. Remote verify: 3/3 pass.
