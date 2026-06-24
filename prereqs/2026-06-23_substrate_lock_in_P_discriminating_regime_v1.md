# Prereg: substrate_lock_in_P_discriminating_regime_v1

**Filed by:** exp_dev (Sonnet 4.6) 2026-06-23
**Anchor name:** substrate_lock_in_P_discriminating_regime_v1
**Script:** experiments/exp_substrate_lock_in_P_discriminating_regime_v1.py
**Queue:** remote_cpu_queue

## Scientific question

Does lock-in P=64 create by-construction-saturation (all recall=1.000) that precludes
discriminating-regime experiments? If P=16 shows a discriminating region [0.4, 0.95] at
sigma=64, then P=16 is the chain-grade discriminator default and P=64 over-spec.

Hypothesis (from Research handoff 2026-06-23): Skunkworks repeatedly flags by-construction
saturation because P=64 is too easy at N=8192 M=500. The Lisman-canonical P=7 may be more
discriminating. This cell characterizes the full P curve.

## Configuration

- N: 8192 (full); 512 (smoke)
- M: 500 (full); 100 (smoke)
- P_sweep: {4, 7, 16, 32, 64}
- K_SIGNAL: 31 (fixed -- single k; does not sweep k)
- SIGMAS: [16, 32, 64, 128]
- seeds: [7, 17, 23] (full); [7, 17] (smoke)
- N_EVAL: 200 (full); 100 (smoke)
- Mechanism: pure numpy lock-in amplifier (cyclic roll carrier)
- Baseline arm: P=1 (single-shot, no lock-in)

## Pre-registered HARD bands

**HARD_PASS** (both conditions required):
1. P=64 recall@sigma=64 >= 0.995 (P=64 saturates as expected)
2. P=16 recall@sigma=64 in [0.40, 0.95] (discriminating regime exists at P=16)

Interpretation: P=64 is over-spec; P=16 is the chain-grade discriminator default.
Future cells should run at P=16 to stay in the discriminating regime and avoid by-construction
saturation from Skunkworks.

**MIDDLE_BAND** (either sub-condition):
- P=16 recall@sigma=64 in (0.95, 1.0): P=16 also saturates -- need lower P or higher sigma
- P=16 recall@sigma=64 < 0.40: P=16 too noisy at sigma=64 -- need lower sigma

**HARD_FAIL**:
- All P in {7, 16, 32, 64} recall@sigma=64 >= 0.99
- Interpretation: by-construction saturation is structural at N=8192 M=500 sigma=64;
  no discriminating regime exists across the full P sweep for this N/M/sigma regime.
  Lock-in P is not a viable discriminating axis here.

## No prior empirical anchor

This is a calibration probe for P-axis discrimination. No prior substrate measurement of
P-vs-recall at N=8192 M=500. Bands are set from theory (lock-in SNR lift = sqrt(P/2));
at P=16: SNR lift = 2.83x over single-shot. At sigma=64, single-shot baseline recall is
near zero for M=500 N=8192 (SNR ~= sqrt(8192*1^2)/64 ~ 1.4 for dense bipolar; P=16 lifts
to ~4.0 which should give good recall). P=64 lifts to ~5.65x, expected to saturate.

Per calibration-probe policy: bands are set at +/-50% of theoretical prediction. Bands
above (0.40 to 0.95 for P=16) span the expected discriminating regime.

## Timeout estimate

smoke_wall_s: measured empirically below after smoke run.
Scaling: pure numpy matmul at N=8192, each seed runs P_sweep x sigma_sweep inner loop.
Per-seed cost: ~5 seeds x 4 sigmas x loop cost = linear in seeds.
- Full N/smoke N ratio: 8192/512 = 16 (but numpy vectorized matmul: scaling_exp ~ 1.5 for vector ops)
- Full seeds / smoke seeds: 3/2 = 1.5
- Estimate from smoke: ceil(1.5 * smoke_wall_s * 16^1.5 * 1.5)
  At smoke_wall_s ~ 10s (estimated -- N=512 M=100 is trivial): ceil(1.5 * 10 * 64 * 1.5) = 1440s
- Using scaling_exp=1.0 (pure numpy matmul at fixed N is linear in N*M): ceil(1.5 * 10 * 16 * 1.5) = 360s
- Conservatively: 900s (15 min)

Filed timeout: 1800s (30 min) -- 2x conservative buffer.

## N-suffix note

No _nN suffix in anchor name. Production N = 8192. Rationale: this is a parameter-sweep
cell not a capacity benchmark; the N=8192 value follows from the existing lock-in amplifier
primitive at chain-grade scale.

## WHAT_THIS_DOES_NOT_SHOW

- Does not establish chain-grade cert for lock-in mechanism (that is v1_FULL)
- Does not test k_signal sweep (fixed k=31)
- Does not test sigma < 16 regime
- Does not show LM performance impact
- Establishes discriminating-regime operating point for discriminator design only
