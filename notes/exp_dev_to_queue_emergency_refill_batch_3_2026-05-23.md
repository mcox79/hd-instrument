# exp_dev -> queue: emergency refill batch #3 (2026-05-23 silent-idle event)

SILENT_IDLE event triggered. Earlier batch #2 (19:55) shipped 4 experiments but
some completed faster than expected (kappa_n_profile_v1=96s ran in <2 min; user
flagged "queues empty" twice). User requested 4-6 experiments with MUCH LONGER
runtimes (15 min minimum, 30-60 min target). Refill batch #3 designed for
multi-N scale-stress + multi-axis sweeps + longer MCMC chains.

Pre-batch state: overnight_queue=0, remote_cpu_queue=1 (amp_se_kerdock_longiter_v1
still pending from batch #2).

## Shipment table

| queue            | name                                       | script                                                          | prereg                                                              | timeout(s) | est ETA   |
|------------------|--------------------------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------|------------|-----------|
| overnight_queue  | wave14_kappa_n_profile_multi_N_v1          | experiments/exp_wave14_kappa_n_profile_multi_N_v1.py            | preregs/2026-05-23_wave14_kappa_n_profile_multi_N_v1.md             | 7200       | 45-60 min |
| overnight_queue  | wave14_vamp_amp_universality_multi_N_v1    | experiments/exp_wave14_vamp_amp_universality_multi_N_v1.py      | preregs/2026-05-23_wave14_vamp_amp_universality_multi_N_v1.md       | 7200       | 45-60 min |
| overnight_queue  | wave14_streaming_NESS_eta_sweep_v1         | experiments/exp_wave14_streaming_NESS_eta_sweep_v1.py           | preregs/2026-05-23_wave14_streaming_NESS_eta_sweep_v1.md            | 5400       | 30-45 min |
| overnight_queue  | wave14_sagawa_ueda_pareto_multiprotocol_v1 | experiments/exp_wave14_sagawa_ueda_pareto_multiprotocol_v1.py   | preregs/2026-05-23_wave14_sagawa_ueda_pareto_multiprotocol_v1.md    | 5400       | 30-45 min |
| remote_cpu_queue | wave14_rsb_exchange_mcmc_v1                | experiments/exp_wave14_rsb_exchange_mcmc_v1.py                  | preregs/2026-05-23_wave14_rsb_exchange_mcmc_v1.md                   | 5400       | 45-60 min |

## Hypotheses (1 line each)

1. **kappa_n_profile_multi_N_v1** (GPU): does the kappa_n GROWS pattern from v164a persist across N? Tests N in {1024, 4096, 16384} with 10 seeds, alpha in {0.5,1,2,4}, n_max=8. Requires t=7 primitive polynomial (newly added).
2. **vamp_amp_universality_multi_N_v1** (GPU): does VAMP-on-Kerdock-works / AMP-fails contrast survive at N=16384? 10 seeds across 3 N x 4 alpha cells.
3. **streaming_NESS_eta_sweep_v1** (GPU): does Cap 3 bimodal P(q) survive streaming bit-flip noise at rates eta in {0.001, 0.01, 0.1, 1.0}? 10 seeds x 4 beta cells at N=4096.
4. **sagawa_ueda_pareto_multiprotocol_v1** (GPU): Cap 1 Pareto-front across (M_base, p, protocol) at N=4096; 10 seeds x 30 trials per cell x 4x4x3 = 48 cells.
5. **rsb_exchange_mcmc_v1** (CPU): independent glass-transition probe via parallel-tempering swap acceptance; N=1024, 12 betas, 10,000 sweeps per chain, 3 alpha, 5 seeds.

## Mechanism-design notes

- kerdock builder PATCHED with t=7 primitive polynomial 0b10000011 (x^7+x+1); verified period 127 multiplicative cycle, full codebook construction at N=16384 produces (65536, 16384) matrix; SCP'd to remote BEFORE first ship.
- Reuse pattern: every v1 script is loaded as a module; v3 file structures pull from v1's verdict logic + helpers + self-tests. Inherited mature smoke gates.
- Smoke uses N=1024 (kerdock MM constraint: even log2). N=512 fails -- the rsb_exchange script smoke initially failed for this reason, patched.
- All 5 scripts have stdout/stderr reconfigure block, get_output_dir/write_metrics block with HDLAB_EXP_NAME, atomic write to metrics.json, validate_metrics required keys.
- All 5 self-tests + smokes PASSED locally; queue-side --self-test gate also passed for all.
- Importance: 4x HIGH (multi-N scale-stress on substrate fingerprint + Cap 1/3 envelope expansion are first-class capability work) + 1x MEDIUM (RSB cross-validation).

## Queue routing rationale

- 4 of 5 -> overnight_queue (GPU): all four are >5 min compute-heavy with multi-seed sweeps; per [[exp_dev]] Rule 0 (GPU-first when queue idle), routed to GPU even when not strictly cuda-required. The Pareto + streaming experiments are GPU-cheap-but-frequent matmuls.
- 1 of 5 -> remote_cpu_queue (CPU): rsb_exchange_mcmc is sequential PT chain MCMC; doesn't parallelize within chain; remote CPU runner is well-suited and the GPU queue already has 4 items.

## Pipeline pacing

After ship:
- overnight_queue: 4 pending
- remote_cpu_queue: 2 pending (incl. batch #2's amp_se_kerdock_longiter_v1 still queued)

Total ETA if runners serialize: GPU 4 * ~40 min = 160 min span (~2.5h); CPU 2 * ~45 min = 90 min span. Pipeline-busy window: at least 90 min, likely 150+ min. This addresses the user's complaint about "ship 4, all finish in <2 min" -- batch #3 has 5 multi-cell sweeps at 10 seeds each, plus the t=7 patch unlocking N=16384, which is genuinely 3-4 min per (N=16384, alpha=4) seed.

## Blockers

- Kerdock t=7 PATCH: applied locally to exp_wave14y_erase_kerdock_v3.py (PRIMITIVE_POLY entry for t=7 = 0b10000011), and SCP'd to remote BEFORE ship. Verified period-127 cycle and codebook construction at N=16384.
- amp_se_kerdock_longiter_v1 from batch #2 is STILL pending on remote_cpu_queue at ship time -- suggests batch #2 CPU did NOT fully drain (orchestrator brief said "may still be running OR may have completed faster than expected"; the queue shows it pending which means it has NOT YET run). RSB exchange will queue behind it. No action needed; runner will pick it up.
- All 5 scripts produce valid metrics.json structure; no metrics_invalid risk.
