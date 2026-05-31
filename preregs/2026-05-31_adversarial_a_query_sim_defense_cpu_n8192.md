# Pre-registration: adversarial_a_query_sim_defense_cpu_n8192

**Date:** 2026-05-31
**Anchor:** adversarial_a_query_sim_defense_cpu_n8192
**Queue:** remote_cpu_queue
**Script:** experiments/exp_adversarial_a_query_sim_defense_cpu_n8192.py
**Cap-map row:** adversarial-sub-row (LIFT at v299)

## Hypothesis

a_query_sim defense that HARD_PASSed at N=4096 GPU (G8, today) and at N=16384
cloud A10 GPU (cross-N, today) also holds at N=8192 on CPU codepath.
Defense is hardware-agnostic and N-8192-valid.

## Pre-registered Bands

**HARD-PASS:** a_query_sim defense achieves defense_rate >= 0.95 AND fp_rate <= 0.05
across all 15 cells (3 M-values x 5 seeds) at N=8192 on CPU.

**HARD-FAIL:** defense degrades sharply: def_rate < 0.50 OR fp_rate > 0.20 at ANY cell.
Indicates codepath or N-sensitivity in the defense mechanism.

**MIDDLE-BAND:** partial defense -- some M-values or seeds pass HP threshold,
others do not. May indicate M-dependent or seed-dependent geometry.

## Middle-band outcome plan

If MIDDLE_BAND: check which M-value(s) fail. If only M=6144 (highest load), report
defense has a load ceiling. Strategy decides whether to restrict to M <= 4096 for
adversarial deployment or commission a threshold-tuning follow-up.

## Config

- N = 8192 (PROT-018 binding)
- M_grid = [2048, 4096, 6144] (M/N = {0.25, 0.5, 0.75} -- matches cloud cross-N structure)
- N_ADV = 32, N_LEG = 64
- Seeds: [7, 17, 23, 31, 41] (5 seeds)
- DEFENSE_A_SIM_THRESH = 0.5 (identical to G8 and cross-N cloud)
- device: CPU (remote_cpu_queue)
- Total cells: 15 (3 M x 5 seeds)

## Timeout estimate

- smoke_wall_s = 0.08s (N=1024, 1 seed, 2 M-values = 2 cells)
- FULL cells: 15; smoke cells: 2
- N scale: 8192/1024 = 8
- formula: ceil(1.5 * 0.08 * 8^1.5 * (15/2)) = ceil(1.5 * 0.08 * 22.6 * 7.5) = ceil(20.4) = 21s
- rounded to 300s floor
- **timeout_s = 300**

## Smoke result

N=1024, 1 seed, M=[256,512]: AQS_CPU_HARD_PASS
def=1.000 fp=0.000 on both M values. 0.08s elapsed.
No suspicious results. Proceeding to FULL.

## N-suffix binding (PROT-018)

Anchor name _n8192 binds N_FULL = 8192. Verified: `N = 8192` in script.

## Strategic context

Closes both the N=8192 gap and the CPU-codepath caveat on the adversarial-sub-row LIFT
at v299. If PASS + Anchor A PASS + v3 in-flight PASS: three independent corroborations
of today's HARD_PASS cascade from different N values and hardware paths.
