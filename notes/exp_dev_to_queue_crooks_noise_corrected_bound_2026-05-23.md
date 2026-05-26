# Exp Dev -> Queue: wave14_crooks_noise_corrected_bound_v1

**Filed**: 2026-05-23
**Routing trigger**: research_crooks_noise_robust_2026-05-23.md (2x drill, cycle 177 CROOKS_NOISE_ENVELOPE_KILL rehab)

name=wave14_crooks_noise_corrected_bound_v1 script=experiments/exp_wave14_crooks_noise_corrected_bound_v1.py prereg=preregs/2026-05-23_wave14_crooks_noise_corrected_bound_v1.md timeout=600

## Smoke gate

PASSED (local, using smoke source data as fallback -- FULL data lives on remote runner).
- Source: data/exp_wave14_crooks_noise_envelope_v1_smoke/metrics.json (N=4096, 1 seed, 10 trials)
- p=0.10: delta_S_emp=0.2325 vs theta(0.10)+0.02=0.3881 -> CROOKS_NOISE_CORRECTED_PASS (margin=0.156)
- Self-test: 9/9 cases PASS (4 theta unit tests + 5 verdict cases)
- ASCII-only: PASS
- metrics.json produced: data/exp_wave14_crooks_noise_corrected_bound_v1_smoke/metrics.json

NOTE: Smoke used fallback (smoke source data). On the remote runner, the FULL
source data will be loaded: data/exp_wave14_crooks_noise_envelope_v1/metrics.json.
The script checks data availability and reports warnings if FULL is missing.

## FULL run config

This is a post-hoc re-analysis. No new substrate run; pure Python arithmetic.
- Source: data/exp_wave14_crooks_noise_envelope_v1/metrics.json (v157 FULL; N=16384)
- Re-analysis: apply theta(p) = ln(2)+p*ln(p)+(1-p)*ln(1-p) to each noisy cell
- Wall time: <10 seconds CPU
- No GPU needed; no torch import

## Queue routing decision

Routed to overnight_queue (remote runner) because the v157 FULL source data lives
on the remote machine (C:/dev/hd-instrument/data/exp_wave14_crooks_noise_envelope_v1/).
CPU-local option: local cpu_runner_0 is dead since 2026-05-21 (per MEMORY.md). If
revived, this would be a better fit (CPU-only, <10s). For now: remote queue is the
safe path; the re-analysis will find the FULL data there.

Dependency: wave14_crooks_noise_envelope_v1 FULL run must have completed before
this entry is dispatched. If the FULL run is still pending, hold this entry until
the FULL verdict lands (FileNotFoundError on dispatch is the signal to retry).

## Substrate-product axis

Cap 1 verifiable forensic erase -- Mechanism #1 rehabilitation.
If PASS: v157 KILL verdict reclassified as metric-definition artifact;
Cap 1 commercial SLA widens to tiered noise-tolerance certificate
(delta_S_emp <= theta(p) + 0.02 at declared noise rate p).
If FAIL: proceed to Mechanism #2 (wave14_crooks_redundant_r3_v1).
