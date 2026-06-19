# Pre-registration: kf5_steerable_beta_v3_n8192

**Filed:** 2026-05-27
**Script:** experiments/exp_kf5_steerable_beta_v3_n8192.py
**Queue:** overnight_queue
**N:** 8192 (BSC atoms; Kerdock not valid at N=8192)
**Seeds:** [7, 17, 23, 31, 41] (5-seed)
**Beta sweep (inference):** [2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0]
**Parent:** kf5_steerable_beta_v2 (N=4096 HARD_PASS; entropy collapse 7.59 bits)
**Cap_map row:** KF-5 steerable substrate (currently 60-72%)

## Hypothesis

KF-5 beta-steering generalizes to 2x larger substrate N=8192. If entropy collapse depth grows
or holds stable with N: substrate-intrinsic. If shrinks: finite-N artifact and the KF-5
claim does not extend to production scale.

## Pre-registered thresholds

**HARD_PASS:** (1) entropy monotone decreasing in >= 4/5 seeds AND (2) mean_entropy_range > 1.0 bit AND (3) bpc has interior minimum at some beta in {4, 8, 16, 32}.
  - If HARD_PASS AND mean_entropy_range >= 7.59 bits (v2 baseline): SCALE_CONFIRMED.

**HARD_FAIL:** entropy_range < 0.5 bits AND bpc monotonic in >= 4/5 seeds. No steering at N=8192.

**MIDDLE_BAND:** entropy monotone in < 4/5 seeds OR range in [0.5, 1.0] bits.
  - Middle-band plan: Check whether 1 specific seed fails or a systematic N-dependent degradation.
  - If systematic: formulate N-scaling hypothesis for next run at N=16384.
  - If isolated seed failure: re-run with 3 additional seeds.

## Formula self-tests (all verified in _instrumentation_selftest)

1. H(uniform over 256) = 8.0 bits. Verified: |H_computed - 8.0| < 0.01.
2. H(one-hot) = 0 bits. Verified.
3. HARD_PASS verdict logic: mk_seed_pass() -> KF5_HARD_PASS. Verified.
4. HARD_FAIL verdict logic: mk_seed_fail() -> KF5_HARD_FAIL. Verified.
5. OOM check: W at N=8192 float32 = 268MB < 6GB. Verified.

## Smoke gate

Smoke at N=1024, 1 seed, 3 betas ([2.0, 8.0, 64.0]):
- Result: MIDDLE_BAND (expected at 1-seed smoke; entropy range = 7.58 bits = strong signal)
- Smoke time: 0.3s
- No suspicious results (entropy collapsing from 7.887 to 0.306 across beta)
- Self-test: PASS

## Timeout estimate

- smoke_wall_s = 0.3 (at N=1024, 1 seed, 3 betas, CPU)
- FULL_N/smoke_N = 8192/1024 = 8; scaling_exp = 2.0 (W matrix ops dominate)
- FULL_seeds/smoke_seeds = 5; FULL_betas/smoke_betas = 7/3 = 2.33
- Raw scale: 8^2 * 5 * 2.33 = 746
- GPU speedup factor: ~10x (GPU vs laptop CPU)
- Effective: 0.3 * 746 / 10 = 22.4s; safety 3x: 67s
- Formula: ceil(1.5 * 22.4 * 3) = 101s -> **timeout_s = 900** (conservative; GPU cold start + codebook)

## N-suffix

anchor name `kf5_steerable_beta_v3_n8192` has suffix `_n8192`; production N_FULL = 8192 (PROT-018 binding verified in _instrumentation_selftest: `assert N_FULL == 8192`).
