# exp_dev -> queue: emergency refill batch (2026-05-23 evening)

User flagged both queues empty at 19:50. Pause flag clear. Full automation. Four
non-trivial experiments shipped to keep pipeline busy across the next ~1.5h window.

Stagger and load profile:

| queue            | name                                  | script                                                            | prereg                                                           | timeout(s) | est ETA  |
|------------------|---------------------------------------|-------------------------------------------------------------------|------------------------------------------------------------------|------------|----------|
| overnight_queue  | kappa_n_profile_v1                    | experiments/exp_wave14_kappa_n_profile_v1.py                      | preregs/2026-05-23_wave14_kappa_n_profile_v1.md                  | 5400       | 30-45 min |
| overnight_queue  | vamp_amp_universality_contrast_v1     | experiments/exp_wave14_vamp_amp_universality_contrast_v1.py       | preregs/2026-05-23_wave14_vamp_amp_universality_contrast_v1.md   | 5400       | 30-45 min |
| remote_cpu_queue | parisi_pq_kerdock_v2                  | experiments/exp_wave14_parisi_pq_kerdock_v2.py                    | preregs/2026-05-23_wave14_parisi_pq_kerdock_v2.md                | 5400       | 45-60 min |
| remote_cpu_queue | amp_se_kerdock_longiter_v1            | experiments/exp_wave14_amp_se_kerdock_longiter_v1.py              | preregs/2026-05-23_wave14_amp_se_kerdock_longiter_v1.md          | 3600       | 20-30 min |

## Hypotheses (one line each)

1. **kappa_n_profile_v1** (GPU): higher free cumulants kappa_n for n=2..8 -- does substrate-MP deviation GROW / DECAY / SATURATE with n.
2. **vamp_amp_universality_contrast_v1** (GPU): VAMP-SE tracks empirical VAMP on Kerdock while AMP-SE diverges from empirical AMP -- clean substrate-product split.
3. **parisi_pq_kerdock_v2** (CPU): Parisi P(q12) on Kerdock-Hebbian W with 1e6 sweeps to resolve glass phase (v1 was under-resolved).
4. **amp_se_kerdock_longiter_v1** (CPU): AMP-on-Kerdock at 5x iter count -- discriminates explode / oscillate / non-SE-fixed-point trajectory shape from v163 AMP_SE_DIVERGES.

## Mechanism-design notes

- All 4 scripts use the stdout/stderr reconfigure top block and write metrics.json via
  the standard `validate_metrics + atomic .tmp+rename` pattern, fixing the v1 batch's
  `metrics_invalid: missing` failure.
- All four ran self-test + smoke locally before queueing; queue-side `--self-test` gate
  also passed.
- VAMP-SE for matched Gauss-Gauss is computed in closed form against the empirical
  singular spectrum (LMMSE posterior), not via a degenerate fixed-point iteration.
- Higher kappa_n inversion uses an exact Mobius recursion on the non-crossing partition
  lattice (Catalan(n) partitions enumerated; verified against closed forms for n<=4 and
  exactly equal to c for MP through n=8).
- Parisi v2 is a thin wrapper around v1; only the chain-length config differs.
- AMP-longiter trajectory metrics: oscillation_relative + log-slope_last500 + plateau
  ratio vs scalar SE give a clean per-cell trajectory class.

## Queue routing rationale

- GPU (overnight_queue): kappa_n_profile + VAMP/AMP contrast both do N=4096 SVD across
  multiple alpha and 5 seeds. Genuinely benefit from GPU.
- Remote CPU (remote_cpu_queue): parisi MCMC is sequential chain work that doesn't
  parallelize within a chain; AMP-longiter is numpy mat-vec dominated and CPU is fine.
  Both >5min wallclock, so per [[feedback-pipeline-pacing]] they go to remote (not local).

## Pipeline pacing

After ship, both queues have depth >= 1. Worst-case if both GPU ships finish before
either CPU ship: orchestrator should be notified by event log and queue-refilled before
GPU sits idle. Total pipeline-busy window est. 60-90 min.

## Blockers

None known. All scripts import existing kerdock builder + glauber routine; no framework
patches needed. If the remote CPU runner (cpu_runner_0 etc.) is dead, the remote_cpu_queue
entries will sit pending until the runner is revived. The two GPU jobs are immune.
