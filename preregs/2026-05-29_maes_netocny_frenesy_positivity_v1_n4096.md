# Pre-Registration: maes_netocny_frenesy_positivity_v1_n4096

Date: 2026-05-29
Anchor: maes_netocny_frenesy_positivity_v1_n4096
Queue: remote_cpu_queue
Script: experiments/exp_maes_netocny_frenesy_positivity_v1_n4096.py
Timeout: 14400s
Justification: BAND-LIFTING for non-eq classification 67-77% lower bound per
notes/research_noneq_framework_consolidation_v276_2026-05-29.md Anchor candidate A.

## Question
Does substrate satisfy Maes-Netocny frenesy positivity?
For an ensemble of probe patterns subject to forward (Hebbian write) and reverse
(anti-Hebbian erase) substrate trajectories, is the time-symmetric reactivity
(frenesy = total forward + reverse coarse-grained transitions per probe) strictly
positive with sigma_margin >= 2.0 across seeds?

## Config
N=4096 (PROT-018 binds), m_frac=0.125 (M_init=512), BSC codebook, SEEDS=[7,17,23,31,41].
M_delta_frac=1/64, M_probe_frac=0.05 (~205 probes), alpha_hebbian=0.1. Single-batch CPU smoke.

## Pre-Registered Thresholds
HARD_PASS:
  - frenesy_per_probe_mean > 0 in all 5/5 seeds
  - frenesy_sigma_margin (K_mean / SE(K)) >= 2.0 in >= 4/5 seeds
  - forward_transitions_total > 0 AND reverse_transitions_total > 0 across all seeds
  Substrate satisfies Maes-Netocny frenesy positivity; non-eq class narrowed to
  Maes-Netocny + Sagawa-Ueda lineage; 4th independent non-eq stream secured.

HARD_FAIL:
  - >= 3/5 seeds in near-zero frenesy band (K_mean < 0.05 * M_probe) OR
  - >= 3/5 seeds with forward_transitions == 0 OR reverse_transitions == 0
  Substrate has trivial time-symmetric dynamical activity; fast-layer non-eq claim
  weakened.

MIDDLE_BAND:
  - frenesy positive but sigma_margin < 2.0 in >= 3/5 seeds.

## Calibration Note
First direct frenesy measurement on substrate. Calibration penalty applied per
[[feedback-lit-scan-calibration-penalty]]: Maes-Netocny frenesy is a published
observable with operational definition; bands chosen via standard non-eq dynamical
activity practice (positivity + sigma >= 2.0 lower bound). M_probe sized so that
expected K_mean under any non-trivial transition rate is well above the HF
near-zero floor.

## Justification (BAND-LIFTING)
Per notes/research_noneq_framework_consolidation_v276_2026-05-29.md Anchor A and
Paper outline G3: HP here lifts Maes-Netocny three-part class P_deflated from
~0.55-0.65 toward >= 0.70 (publication-grade). Cheapest decisive probe to add a
4th non-eq evidence stream (TCFT + SKAH-M + BID outside-Hopfield + frenesy).

## Parent
exp_ortho_noneq_corroborator_v1.py (Hatano-Sasa NESS trajectory infrastructure).
Reuses incremental-Hebbian write/erase protocol; adds:
(a) forward+reverse trajectory recording with coarse-grained sign-state observable
(b) per-probe transition counts -> frenesy K_j
(c) sigma_EP proxy from forward/reverse imbalance.
