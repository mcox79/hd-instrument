# Pre-registration: wave14_crooks_noise_envelope_v1

**Date registered**: 2026-05-23
**Script**: experiments/exp_wave14_crooks_noise_envelope_v1.py
**Routing file**: notes/strategy_request_to_exp_dev_crooks_noise_envelope_v1_2026-05-23.md
**Capability axis**: Cap 1 - verifiable forensic erase (substrate-product class 1)
**Framing**: substrate-product capability envelope expansion; NOT a paper claim

## Hypothesis

The Crooks-FT-anchored erase protocol (anti-Hebbian outer-product subtraction) maintains
delta_S_emp < 0.05 under light-to-moderate bit-flip noise on the substrate, establishing
that Cap 1 (verifiable forensic erase) extends to realistic perturbation conditions.

## Config

- N = 16384
- M_base = 200 (patterns in substrate before erase trial)
- n_trials = 50 per (p, seed) cell
- seeds = [17, 18, 19]
- noise_levels = [0.0 (clean baseline), 0.05, 0.10, 0.20]
- Noise model: bit-flip (sign flip) each entry of W with probability p AFTER insertion,
  BEFORE the anti-Hebbian erase step

## Protocol per trial

1. Build W_base with M_base patterns via Hebbian outer-product (bf16; no float32 upcast)
2. Generate (k_test, v_test) test pattern pair
3. Measure H_baseline = retrieval_entropy(W_base, k_test, candidates)
4. Forward: W_inserted = W_base + outer(v_test, k_test) / N
5. Noise: W_noisy = apply_bit_flip_noise(W_inserted, p)
6. Reverse: W_erased = W_noisy - outer(v_test, k_test) / N
7. Measure H_erased = retrieval_entropy(W_erased, k_test, candidates)
8. Record delta_S = abs(H_erased - H_baseline)

## Predicted outcomes

- p = 0.0 (clean baseline): delta_S_emp ~ 0.0 (replicates v1 Crooks PASS)
- p = 0.05 (light noise): delta_S_emp < 0.05 expected (noise level low relative to N=16384)
- p = 0.10 (moderate noise): uncertain; may drift above 0.05
- p = 0.20 (heavy noise): expected delta_S_emp > 0.05; characterizes noise ceiling

## Acceptance criteria

- CROOKS_NOISE_ENVELOPE_PASS: 2+ of 3 noisy cells (p in {0.05, 0.10, 0.20}) satisfy
  delta_S_emp (mean over 3 seeds x 50 trials) < 0.05
- CROOKS_NOISE_ENVELOPE_PARTIAL: exactly 1 noisy cell satisfies < 0.05
- CROOKS_NOISE_ENVELOPE_KILL: 0 noisy cells satisfy < 0.05; Cap 1 envelope confirmed
  clean-only

## VRAM budget

- W (16384 x 16384) bf16 = 536 MB
- build_initial_W intermediate: (N x M_base) float32 = 16384 x 200 x 4 = ~13 MB (safe;
  NOT the N x N float32 OOM pattern from Bet A; M_base axis is 200 not N)
- torch.outer(v, k) intermediate per trial = (16384 x 16384) bf16 = 536 MB (transient)
- Peak active estimate: W_base (536 MB) + outer product (536 MB) + W_inserted (536 MB)
  = ~1.6 GB peak (conservative); in practice PyTorch reuses memory across steps.
  Strategy predicted ~1 GB. Both are well under the 2 GB cap.

## Smoke result (pre-registration gate)

Smoke at N=4096, M_base=50, n_trials=10, seeds=[17], p in {0.0, 0.10}:
- p=0.0: delta_S_emp=0.0000 (clean erase confirmed)
- p=0.10: delta_S_emp=0.2325 (noise disrupts erase at small N)
- Smoke verdict: CROOKS_NOISE_ENVELOPE_KILL (expected at smoke scale; sanity band [0.0, 0.5] satisfied)
- metrics.json: produced at data/exp_wave14_crooks_noise_envelope_v1_smoke/metrics.json

Smoke note: KILL at N=4096 does not pre-determine the FULL verdict; at N=16384 the substrate
has 16x more dimensions so noise at p=0.05 affects a smaller fractional volume. The FULL
run across 3 seeds x 50 trials is the load-bearing measurement.

## Failure modes / escalation

- If peak VRAM exceeds 2 GB: halt and file exp_dev_to_strategy escalation (unexpected
  allocation path; N x N float32 intermediate somewhere)
- If clean baseline (p=0.0) delta_S_emp > 0.01: halt and file escalation (v1 Crooks
  replication failure; investigate before interpreting noisy cells)
- KILL verdict does not close Cap 1; Cap 1 was verified at p=0.0 in cycle 173. KILL means
  the noise envelope stays narrow; Cap 1 commercial framing remains valid for clean substrates.
