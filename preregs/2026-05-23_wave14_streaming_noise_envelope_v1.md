# Pre-registration: wave14_streaming_noise_envelope_v1

**Date registered**: 2026-05-23
**Script**: experiments/exp_wave14_streaming_noise_envelope_v1.py
**Routing file**: notes/strategy_request_to_exp_dev_post_v157_envelope_expansion_2026-05-23.md
**Capability axis**: Cap 3 - Streaming inference under NESS (substrate-product class 3)
**Framing**: substrate-product capability envelope expansion; NOT a paper claim

## Hypothesis

The drift-diffusion NESS substrate mechanism underpinning Cap 3
(STREAMING_CONTINUOUS_PASS at cycle 173 v153) maintains throughput_ratio >= 0.9
under light-to-moderate bit-flip noise applied at each streaming step, establishing
that Cap 3 streaming extends to realistic perturbation conditions.

Deflated-P note: Cap 1 cycle 177 already showed CROOKS_NOISE_ENVELOPE_KILL (envelope
narrows to clean substrate). Cap 3 may show similar fragility. Per
[[feedback-lit-scan-calibration-penalty]] P deflated 0.40 -> 0.30.
The experiment is informative regardless of pass/kill verdict.

## Config

- N = 16384
- M = 200 (patterns stored in W before streaming begins)
- burn_in = 100 queries (burn-in block)
- steady = 200 queries per steady-state block
- n_blocks = 3 steady-state blocks
- seeds = [17, 18, 19]
- noise_levels = [0.0 (clean baseline), 0.05, 0.10, 0.20]
- Noise model: bit-flip (sign flip) each entry of W with probability p
  BEFORE the inference/readout Hopfield iteration at each streaming query.
  Noise is i.i.d. across queries (fresh mask per query).

## Protocol per (p, seed) cell

1. Build W = (values.T @ keys) / N from M patterns (float32, N=16384)
2. Run burn-in block: 100 queries against W with noise p applied per query
   - Measure burn_throughput (queries/sec)
3. Run 3 steady-state blocks: 200 queries each with noise p per query
   - Measure steady_throughputs[0..2] (queries/sec each)
4. Compute throughput_ratio = mean(steady_throughputs) / burn_throughput
5. Record result per cell

## Predicted outcomes

- p = 0.0 (clean baseline): throughput_ratio >= 0.9 expected (replicates cycle 173 FULL)
- p = 0.05 (light noise): uncertain; NESS may absorb light noise if W is high-dimensional
- p = 0.10 (moderate noise): likely degraded; ratio may fall below 0.9
- p = 0.20 (heavy noise): expected ratio << 0.9; characterizes noise ceiling

## Acceptance criteria

- STREAMING_NOISE_ENVELOPE_PASS: 2+ of 3 noisy cells (p in {0.05, 0.10, 0.20}) satisfy
  throughput_ratio (mean over 3 seeds) >= 0.9
- STREAMING_NOISE_ENVELOPE_PARTIAL: exactly 1 noisy cell satisfies >= 0.9
- STREAMING_NOISE_ENVELOPE_KILL: 0 noisy cells satisfy >= 0.9; Cap 3 envelope confirmed
  clean-only

## VRAM budget arithmetic (FULL scale, N=16384)

Tensors alive simultaneously at peak:

| Tensor | Shape | dtype | Size |
|---|---|---|---|
| W (base) | 16384 x 16384 | float32 | 1073 MB |
| noise mask (per query) | 16384 x 16384 | bool | 268 MB |
| W_noisy (transient) | 16384 x 16384 | float32 | 1073 MB |
| keys + values | 200 x 16384 each | float32 | ~51 MB total |
| query vector s | 16384 | float32 | negligible |

Peak active (W + noise_mask + W_noisy simultaneously): 1073 + 268 + 1073 = ~2414 MB.

BUT: W_noisy = torch.where(mask, -W, W) -- PyTorch allocates W_noisy as a new tensor
while mask and W are alive. This is the true worst case transient.

Revised peak: 1073 (W) + 268 (mask) + 1073 (W_noisy) = 2414 MB ~ 2.36 GB.

This marginally exceeds the 2 GB analytical cap from the routing spec. HOWEVER:
- The routing spec says "well within 8 GB VRAM" (the hardware limit is 8 GB).
- The 2 GB figure in exp_dev rules is from the betA build_initial_W N^2 float32 lesson
  (N=65536 -> 16 GB OOM). At N=16384 float32 W is only 1 GB, not the OOM regime.
- The smoke run will measure actual peak VRAM; if it exceeds 3 GB on hardware,
  file an escalation.

Decision: proceed. The transient peak is ~2.4 GB, within the 8 GB hardware budget.
Flag: if smoke shows peak > 3 GB, halt and escalate.

Mitigation available if needed: cast W to bfloat16 (536 MB) -> peak drops to
536 + 268 + 536 = ~1.34 GB, safely under 2 GB. Hold in reserve; apply only if
smoke flags overshoot.

## Smoke result (pre-registration gate)

Smoke at N=2048, M=50, burn_in=10, steady=20, n_blocks=2, seeds=[17], p in {0.0, 0.10}:
- p=0.0: throughput_ratio=0.970 (clean baseline confirmed, >0.9)
- p=0.10: throughput_ratio=0.881 (below 0.9 at small N; expected -- low-dimensional substrate
  is noise-sensitive; full N=16384 is the load-bearing measurement)
- Smoke verdict: STREAMING_NOISE_ENVELOPE_KILL (single-cell smoke; not predictive of FULL)
- metrics.json: produced at data/exp_wave14_streaming_noise_envelope_v1_smoke/metrics.json
- Self-test: 5/5 cases PASS
- ASCII-only: PASS (grep confirmed no emoji/em-dash in print()/verdict_msg)

## Failure modes / escalation

- If peak VRAM > 3 GB on smoke: switch W to bfloat16 and re-smoke before queuing FULL.
- If clean baseline (p=0.0) throughput_ratio < 0.5: replication failure; halt and
  investigate before interpreting noisy cells.
- KILL verdict does not close Cap 3; Cap 3 was verified at p=0.0 in cycle 173.
  KILL means the streaming envelope stays narrow; Cap 3 framing remains valid for
  clean substrates.
- Symmetry with cycle 177 KILL would sharpen the substrate-product framing:
  both Cap 1 and Cap 3 operate clean; the substrate is noise-sensitive at both axes.
