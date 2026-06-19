# Pre-registration: path_d_adversarial_composition_v1_n4096

**Date:** 2026-05-31
**Anchor:** path_d_adversarial_composition_v1_n4096
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_path_d_adversarial_composition_v1_n4096.py
**Cap-map rows:** R-PATH-D-NO-CEILING x adversarial-sub-row (composition)

## Hypothesis

Under 50/50 legitimate/adversarial interleaved workload at depth=5:
(1) a_query_sim defense gate rejects adversarial queries (defense_rate >= 0.85).
(2) Path D maintains acc >= 0.95 on legitimate queries that PASS the gate.

Defense and mechanism co-exist without mutual interference.

## Pre-registered Bands

**HARD-PASS:** defense_rate >= 0.85 on adversarial AND path_d_acc on gated_legit >= 0.95
in 4/5+ seeds. Composition coherent -- production deployment story complete.

**HARD-FAIL:** path_d_acc on gated legitimate < 0.70 in majority of cells (gate
interferes with Path D); OR defense_rate < 0.50 in majority (defense degrades
under Path D load). Production deployment has a compositional gap.

**MIDDLE-BAND:** partial composition -- some seeds pass both conditions, others
show marginal defense or marginal Path D accuracy under gate. Characterize
which condition is marginal.

## Middle-band outcome plan

If MIDDLE_BAND with Path D acc marginally below (0.70-0.95): check whether gate
false-positives are rejecting legitimate starts that Path D needs. Gate threshold
may need loosening. File strategy note: tune DEFENSE_A_SIM_THRESH.
If defense_rate marginal (0.50-0.85): the 50/50 interleaving may not produce
enough collision queries at this M value. Test with higher adversarial fraction.

## Config

- N = 4096 (PROT-018 binding)
- M = 2048 (nominal, M/N = 0.5)
- depth = 5, K_paths = 100
- N_LEG = 50 (legitimate starts), N_ADV = 50 (adversarial queries)
- Seeds: [7, 17, 23, 31, 41] (5 seeds)
- DEFENSE_A_SIM_THRESH = 0.5 (identical to G8)
- device: CUDA (overnight_queue, GPU)
- Total cells: 5 seeds x 1 M value

## Timeout estimate

- smoke_wall_s = 0.19s (N=1024, 1 seed, M=256, n_leg=12, n_adv=12)
- FULL: N=4096 (4x), 5 seeds (5x), larger M and queries
- formula: ceil(1.5 * 0.19 * (4096/1024)^1.5 * (5/1)) = ceil(1.5 * 0.19 * 8 * 5) = ceil(11.4) = 12s
- GPU speedup conservatively 5-10x; adding margin for CPU self-test overhead
- Rounded to 300s floor. Long-run flag: NO (well under 7200s).
- **timeout_s = 300**

## Smoke result

N=1024, 1 seed, M=256: PDAC_HARD_FAIL at smoke -- expected. Explanation:
At N=1024, max cosine similarity between stored keys = 0.031 (far below 0.5 threshold).
Adversarial collision queries cannot be constructed at N=1024; def_rate=0.000 is
a geometric artifact of small N, NOT an instrumentation bug.
acc_path_d_gated=1.000, acc_path_d_baseline=1.000 -- Path D metrics valid.
At N=4096 (FULL), G8 confirmed def=1.000 -- collision queries ARE formed.
Smoke-N calibration artifact; NOT suspicious-result territory; metrics non-null.
Proceeding to FULL at N=4096.

## N-suffix binding (PROT-018)

Anchor name _n4096 binds N_FULL = 4096. Verified: `N = 4096` in script.

## Strategic context

Closes the final production-deployment question after today's dual HARD_PASS cascade
(G7EXT + G8). If Path D + adversarial defense compose cleanly, the substrate can
handle interleaved adversarial/legitimate workloads in production without
architecture-level separation.
