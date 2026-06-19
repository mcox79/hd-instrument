# Pre-registration: adversarial_aqsim_path_d_compose_v3_n8192

Date: 2026-06-01
Anchor: adversarial_aqsim_path_d_compose_v3_n8192
Queue: overnight_queue (GPU)

## Hypothesis

3-way SCORE-level production stack (compression x Path D x a_query_sim defense) replicates
at N=8192, closing the single-N caveat from v2 N=4096 HARD_PASS (cap_map v307).
Cross-N strengthening: if unanimous at N=8192, compositional sub-row LIFTs further toward
0.80-0.95.

## Configuration

- N = 8192 (PROT-018 binding)
- M = 4096 (N/2 ratio matched to v2)
- depth = 5, K_paths = 100
- 90/10 adversarial/legitimate ratio
- COLLISION_ALPHA = 0.45 (subthreshold probes, < defense threshold 0.50)
- 5 seeds: [7, 17, 23, 31, 41]
- Device: cuda (GPU)

## Pre-registered bands

HARD-PASS: defense_activation_rate >= 0.90
           AND path_d_acc_gated_compressed >= 0.95
           AND |acc_gated_comp - acc_gated_uncomp| <= 0.05
           in 4/5+ seeds.

HARD-FAIL: defense_activation_rate < 0.50 in majority (defense not firing)
           OR path_d_acc_gated_compressed < 0.50 in majority (compression breaks Path D).
           OR special DEFENSE_STILL_UNNECESSARY if all def_act < 0.10.

MIDDLE-BAND: otherwise.

## PROT-022 BSC guard

N=8192: log2=13 (ODD). build_shared is verified to return non-degenerate codebook
at N=8192 in the instrumentation self-test.

## OOM check

N=8192 W = 256 MiB. Codebook M=4096 x 8192 = 128 MiB. Total peak ~500 MiB. Under 6 GB.

## Timeout estimate

v2 (N=4096) 5 seeds: estimated ~100s GPU. N=8192 is 2x N (linear scale for this workload).
smoke_wall_s = measured from smoke run. PROT-019 floor: 14400s.
timeout_s = 14400 (PROT-019 floor; actual estimated ~200-400s).

## N-suffix binding

_n8192: production N = 8192. Script assert N_FULL == 8192.

## Differential

Single N change vs v2: N=4096 -> N=8192. All other parameters identical.
Cross-N corroboration of v2 HARD_PASS.
