# Pre-registration: lock_in_amplifier_hd_frequency_smoke_v1

**Date:** 2026-06-23
**Anchor:** lock_in_amplifier_hd_frequency_smoke_v1
**Queue:** local_cpu_queue (smoke-only; CPU)
**N:** N_DIM=1024 (smoke) / 4096 (full); **Seeds:** [7, 17] (smoke) / [7, 17, 23] (full); **P_phases:** [1, 8, 32]; **k_signal:** 31

## Scientific question

Can a substrate-native "lock-in amplifier" mechanism lift recall above the noise-limited
floor by modulating the cue at a distinct HD-frequency (cyclic rotation by k positions)
and demodulating coherently at that frequency? USER intuition 2026-06-23: "pulse a weak
light at a frequency that not much stuff works at; filter only that frequency really far
away — you can almost always still pick up the signal." Novel mechanism for substrate;
no published precedent in HD-computing literature.

## Mechanism (substrate-native lock-in amplifier)

- "Frequency" via permutation operator: pi_k(v) = np.roll(v, k) -- cyclic rotation.
- TRANSMIT P phase-shifted copies; channel adds independent noise per phase:
    received_p = roll(cue, p*k_signal) * cos(2*pi*p/P) + noise_p   (independent noise_p per p)
- DEMODULATE: undo rotation + apply same cos carrier:
    decoded = (2/P) * sum_p roll(received_p, -p*k_signal) * cos(2*pi*p/P)
- Signal coheres via sum_p cos^2(2*pi*p/P) = P/2; SNR improvement = sqrt(P/2).
- ARM_BASELINE_SINGLE_SHOT: P=1, no modulation; reproduces single-shot noise floor.
- ARM_LOCK_IN_P{N}: P=N coherent phase copies; demod; match against codebook.

## Pre-registered bands

**HARD-PASS:** at the DISCRIMINATING SIGMA (where baseline recall is in [0.05, 0.30]),
P=32 lifts recall by >= 4x vs baseline AND P=8 lifts by >= 2x vs baseline. These factors
match the textbook lock-in amplifier SNR improvement sqrt(P/2): sqrt(16) = 4x for P=32;
sqrt(4) = 2x for P=8. If both hit, the mechanism is real and chain-grade-candidate.

**HARD-FAIL:** ARM_LOCK_IN_P32 absolute lift <= 0.01 at the discriminating sigma.
Permutation-as-frequency does not exploit the structure of random noise.

**MIDDLE:** Partial lift (between HARD-FAIL and HARD-PASS factors), OR baseline
out-of-discriminating-band (sigma sweep too narrow; re-tune).

## Calibration rationale

USER's original pre-reg targeted sigma=1.5 with baseline ~0.023, but empirical probe
showed that at the substrate's standard bipolar-codebook convention (codebook in
{-1, +1}^N), the noise-limited regime lives at sigma ~ 8-64 (N=1024) or sigma ~ 16-128
(N=4096), not 0.5-2.0. We therefore sweep sigma in [4, 64] (smoke) or [8, 128] (full)
and pick the discriminating sigma automatically per the verdict logic. The HARD-PASS
factor (>=4x for P=32) is the SNR-prediction from lock-in theory, not an arbitrary
threshold -- this makes the test a direct quantitative check of the mechanism's
substrate-native prediction.

SMOKE OBSERVED 2026-06-23 (local CPU, N=1024 M=50 sigmas=[4..64]):
- discrim_sigma=32 (baseline=0.115 in-band): P32=0.940 (x8.17); P8=0.405 (x3.52)
- HARD-PASS clearly tripped in smoke; mechanism appears real at substrate.

## N-suffix section

No _n suffix in anchor name (PROT-018 N/A). Smoke production N=1024; full production
N=4096. The cell is designed for SMOKE dispatch only (~10min CPU per USER spec); no
full-config queue entry planned in this cycle.

## Timeout estimate

Smoke wall ~ 25.6s at N=1024 (measured local); full would be ~25 * (4096/1024)^1.5 *
(3/2) = ~25 * 8 * 1.5 = ~300s = 5 min. The dispatch is local_cpu_queue smoke-only;
timeout 600s safety. Smoke gate via queue_add already passed during local validation.

timeout_s = 600

## Sanity self-tests (run at module import)

1. P=1 endpoint: lock_in_transmit(P=1) reduces to baseline_transmit byte-for-byte
   (same noise realization). PASSED.
2. v2 clean endpoint at sigma=0: signal recovers exactly via cos^2 sum = P/2.
   PASSED.
3. Permutation orthogonality at N=1024: roll(v, 31) . v / N -> O(1/sqrt(N)) for
   random gaussian v. PASSED.

## Implementation note

ASCII-only. numpy-only. PROT-018 N/A (no _n suffix). Local CPU queue; smoke is
the production for this cell (smoke-only ship per USER spec).
