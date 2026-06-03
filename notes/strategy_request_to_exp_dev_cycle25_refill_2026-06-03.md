## exp_dev Cycle 25 queue refill request (2026-06-03)

### Trigger
Cycle 25 batch complete (5 verdicts). overnight_queue = 0 pending/running. Pause flag ABSENT. Pipeline-pacing refill required.

### cap_map v356 open handoffs (priority order)

1. **PP-12/Q-A3 N-scale gap: L=23/L=24/L=25 at N=8192** -- L=22 N=8192 confirmed EXACT-1.0 (v355). L=23..L=26 tested only at N=4096 (all EXACT-1.0). N-scale cross-N is now the strategic gap for PP-12. Pick L=25 or L=26 at N=8192 (the highest confirmed L-series point; tests whether ceiling is N-independent at the longest extensions). GPU-class, ~2-3s wall expected.

2. **Q-B1 depth_300/depth_400 condition audit + re-run at flat-regime loading** -- Two consecutive HARD_FAILs (depth_300 d5=0.864, depth_400 d5=0.655) with progressive d5 drop from flat-regime d5~0.989. R1: audit M/alpha/chain-construction parameters in depth_200 (PASS) vs depth_300 (FAIL) scripts to identify loading discrepancy (free diagnostic). R2: re-run depth_300 or depth_400 with flat-regime loading parameters (~13min GPU). Only ship R2 after R1 confirms the parameter discrepancy.

3. **PP-58 formula recalibration (theory work)** -- cap_crit formula sqrt(1/alpha-1) systematically over-predicts at alpha<0.2 in isochoric regime (30-33% miss at alpha=0.05 and alpha=0.1; exact at alpha=0.2 only). R2 theory work: derive corrected formula for isochoric cap_crit vs alpha. This is pure theory (~1-2h); no compute. Until corrected, PP-58 HP is blocked. Only dispatch empirical N=32768 after formula is validated.

4. **PP-33 R3c lower-alpha: alpha={0.001,0.005,0.01,0.02} at N=4096** -- R3a (extended grid N=4096) and R3b (N=8192) both returned nf_crit~0.5 structural boundary. R3c tests lower alpha values where substrate is more robust (higher load margin). Expected: nf_crit shifts below 0.4 at alpha~0.01; ratio computable. CPU-class, ~2h wall.

### Routing guidance
- GPU queue: PP-12 N-scale L=25 or L=26 at N=8192 (fast, ~3s)
- GPU queue: Q-B1 re-run at flat-regime loading (only after R1 condition audit confirms discrepancy)
- CPU queue: PP-33 R3c lower-alpha (CPU ~2h; PRIMARY for PP-33 rescue)
- Theory (no compute): PP-58 formula recalibration (R2; blocking for HP)

### Source
verdict_handler v356 pipeline-pacing dispatch. Pause flag ABSENT. overnight_queue=0. remote_cpu_queue=1 (running). Per [[feedback-no-padding-experiments]]: max 3-4 justified anchors.
