# Exp-Dev shipped report -- cycle 57

**From:** Exp-Dev  **To:** Orchestrator  **Date:** 2026-06-04

## Shipped (1 new explicit handoff this cycle)
- **substrate_trained_mini_lm_readout_fix_nsweep_v1** (remote_cpu_queue, 21600s, VERIFIED) --
  USER-AUTHORIZED routing_substrate_training_n_sweep_readout_fix. Sweeps N in
  {512,1024,2048,4096,8192,16384} x 3 seeds, calibrated readout; finds the N-threshold where
  substrate-trained-LM learning emerges (follow-up to the readout-artifact de-confound). Smoke clean
  (gaps~0 at N<=512 = known no-learning regime; full N up to 16384 is the test).

## Already shipped earlier this session (not re-shipped)
- NHSE Anchor 2 (nhse_annulus_tau_crit_boundary) -- the prompt's "ship if not done"; already done.
- Capacity-stress (GPU), Q-A3 L=10000 (GPU), kappa3 sigma_g_ext (GPU), Q-B1 loading-boundary (CPU),
  PP-49 depth-parity, Joint D+H, mini_lm readout-fix v2.

## Queue state
CPU pending=3 (NHSE Anchor 2, Q-B1 loading boundary, N-sweep) + 1 running. GPU running/completing the
3 from the prior turn. Queues healthy; no padding added.

## Deferred (honest)
- PP-50 transition-zone N-sweep (TW-vs-Hadamard): built but smoke showed 0 violations -- my guessed
  multiplicative-noise model does not reproduce the PP-50 transition zone. Needs a PP-50-mechanism-matched
  rebuild before shipping (a deeper read of a PP-50 reference script). Not shipped.

## Scope
Stayed in lane: read metrics only for completion status; shipped only explicitly-requested handoffs;
no verdict interpretation / strategy. Verdicts propagate to Orchestrator via the bridge/watchdog.

**END.**
