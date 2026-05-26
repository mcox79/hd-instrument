# Prereg: wave14_fieldA_lyapunov_spectrum_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Field-A reservoir-computing Lyapunov spectrum (cross-framework cadence)
**Source**: `notes/exp_dev_handoff_fieldA_reservoir_lyapunov_2026-05-24.md`

## Hypothesis

Substrate dynamics may match reservoir-computing edge-of-chaos signatures (λ_1 ≈ 0 at edge). If so, opens echo-state mapping with closed-form memory-capacity from reservoir literature.

## Design

- N=1024 substrate width
- top-5 Lyapunov exponents via Benettin/Shimada-Nagashima QR method
- T_iter=1500 iterations, T_warmup=200 transient, QR re-orthonormalize every 5 steps
- 3 operating-density points: M_density in {0.05, 0.20, 0.50}
- 5 seeds: [7, 17, 23, 31, 41]
- Substrate dynamic: linear map x_{t+1} = W x_t with W = Hebbian outer-product over BSC code pairs

## Per [[feedback-lit-scan-calibration-penalty]]

Substrate is in uncharted regime for reservoir-computing literature; P deflated 0.15-0.25; HARD-FAIL thresholds explicit.

## Falsifier bands (pre-registered)

- **HARD-PASS — Field-A 🔬 -> 🟡 echo-state mapping opens**: |λ_1| <= 0.05 at >=1 operating point AND log-linear decay r² >= 0.85 across top-5.
- **HARD-FAIL — Field-A REJECTED**: max |λ_1| > 0.20 across all probed densities (firmly chaotic or contractive).
- **MIDDLE**: any intermediate; report bands.

## Smoke result (N=128, density=0.20, 1 seed, T=100)

`LYAP_HARD_FAIL_FAR_FROM_EDGE` at smoke (λ_1 = 0.81 deep in chaotic). Expected at smoke: N=128 with M=26 has high spectral radius. FULL at N=1024 probes density grid {0.05, 0.20, 0.50}; one or more should be near edge if hypothesis holds.

## Self-test

`verdict self-test passed (4/4 cases)`.

## Queue

`queue=remote_cpu_queue name=wave14_fieldA_lyapunov_spectrum_v1 script=experiments/exp_wave14_fieldA_lyapunov_spectrum_v1.py prereg=preregs/2026-05-24_wave14_fieldA_lyapunov_spectrum_v1.md timeout=3600`
