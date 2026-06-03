# exp_dev to queue: CYCLE 23 refill (post-v354)

**Date:** 2026-06-03
**Context:** Post-CYCLE 23 BATCH (v354). 3 new anchors shipped. Pause flag ABSENT.

## Queue state at refill time

- overnight_queue (GPU): q_b1_chain_depth_300_v1_n16384 RUNNING; 0 pending.
- remote_cpu_queue (CPU): pp58_isochoric_kappa3_n8192_v4_n8192 RUNNING; 0 pending.
- q_a3_l23 + q_a3_l24: COMPLETED (awaiting verdict processing).

## Anchors shipped

### overnight_queue (GPU)

1. **q_a3_l22_cross_layer_composition_v1_n8192**
   - Why: PP-12/Q-A3 N-scale at L=22. L=22 HARD_PASS at N=4096 (v354); L=19 N=8192 HARD_PASS (v354).
     This probes N-independence at the current ceiling L=22 (second N-scale point for PP-12).
   - Script: experiments/exp_q_a3_l22_cross_layer_composition_v1_n8192.py (NEW)
   - Prereq: prereqs/2026-06-03_q_a3_l22_cross_layer_composition_v1_n8192.md (NEW)
   - PROT-018 N=8192. PROT-019 timeout=21600s (floor). PROT-022 PASS (selftest 3.6s). REMOTE VERIFIED.

### remote_cpu_queue (CPU)

2. **activation_barrier_r3_extended_grid_v2_n4096**
   - Why: PP-33 R3a rescue per v354 annotation. v1 MIDDLE_BAND: nf_crit at grid boundary 0.60.
     Extended grid 0.00..0.90 step 0.01 (91 points) determines if nf_crit resolves above 0.60.
   - Script: experiments/exp_activation_barrier_r3_extended_grid_v2_n4096.py (NEW)
   - Prereq: prereqs/2026-06-03_activation_barrier_r3_extended_grid_v2_n4096.md (NEW)
   - Bug fixed: None-formatting in compute_verdict f-string.
   - PROT-018 N=4096. PROT-019 timeout=14400s (floor). PROT-022 PASS (selftest 2.4s). REMOTE VERIFIED.

3. **pp58_isochoric_kappa3_finergrid_v2_n4096**
   - Why: PP-58 R3b rescue per v354 annotation. v1 MIDDLE_BAND: audit_crit grid-limited (sigma_g=1.0).
     Finer grid 0.0..2.0 step 0.1 (21 points) resolves audit_crit vs alpha relationship.
   - Script: experiments/exp_pp58_isochoric_kappa3_finergrid_v2_n4096.py (NEW)
   - Prereq: prereqs/2026-06-03_pp58_isochoric_kappa3_finergrid_v2_n4096.md (NEW)
   - Bug fixed: selftest kappa3_baseline bounds (0.01, 2.0) -- v1 had (0.5, 5.0) wrong for small N.
   - PROT-018 N=4096. PROT-019 timeout=14400s (floor). PROT-022 PASS (selftest 5.0s). REMOTE VERIFIED.

## Items deferred

- q_a3_l24_n_scale or L=23 N-scale: Awaiting q_a3_l23 + q_a3_l24 COMPLETED verdicts first.
- q_b1 depth extension beyond d=300: Awaiting d=300 RUNNING result.
- PP-50 capacity phase boundary finer grid: Deferred; PP-33/PP-58 rescues higher priority.
- PP-55/PP-56 further N-scale: Band-lifts confirmed; no immediate follow-up needed.

## Remote verify summary

3/3 REMOTE VERIFIED: all entries confirmed present in target queue JSON.
