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
