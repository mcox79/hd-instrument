# Pre-registration: state_compression_adversarial_codebook_v1_n4096

Date: 2026-05-31
Anchor: state_compression_adversarial_codebook_v1_n4096
Queue: remote_cpu_queue
Script: experiments/exp_state_compression_adversarial_codebook_v1_n4096.py

## Context

substrate_state_compression_v2_n4096 just landed C3_HARD_PASS (commit b116da9, cap_map v295).
c_quant/bits8 = 4x compression + KF-1/KF-2/KF-3 all PASS at N=4096 5-seed.
PP-2 row has its first empirical foothold.

KNOWN RISK: U2 adversarial probing found codebook-collision (pattern_2) achieves 0%
defense under nominal retrieval (100% breach). The audit-cert narrative for PP-2
requires verifying whether c_quant/bits8 still preserves KF-1 (deletion certificate)
when the input uses adversarial-colliding codebook entries.

## Scientific question

At N=4096, M=2048, c_quant/bits8 (4x compression): does KF-1 deletion certificate hold
when keys/values are drawn from adversarial high-cosine-similarity pairs (U2-style 100%
collision pattern)? Does KF-2 norm-drift hold (structural, input-agnostic)?
Does KF-3 edit-consistency hold under adversarial input?

## Pre-registered bands

HARD-PASS = KF-1 (deletion cert) >= 0.70 under 100% adversarial collision input
            AND KF-2 norm drift 0.85-1.15 (structural, independent of adversarial input)
            AND KF-3 (edit consistency) >= 0.70 under 100% adversarial input.

HARD-FAIL = KF-1 deletion cert < 0.30 under 100% adversarial input
            (compliance claim collapses; PP-2 evidence limited to nominal regime).

MIDDLE-BAND = KF-1 in [0.30, 0.70) under 100% adversarial input
              (partial robustness; 50% mixed pattern shows intermediate degradation).

## Calibration note

No prior empirical anchor for combined compression + adversarial input.
HP threshold 0.70 is conservative (nominal c_quant/bits8 had KF-1=1.0 so 0.70 allows
significant adversarial degradation before blocking HP).
Bands widened per calibration-probe policy (no prior anchor).

## Configuration

N=4096, M=2048, bits=8 (c_quant/bits8), n_probe=64
Adversarial patterns: 100% collision (U2-style), 50% mixed
KF tests: KF-1 (deletion cert), KF-2 (norm drift), KF-3 (edit consistency)
Seeds=[7, 17, 23, 31, 41] (5 seeds)
device=cpu (forced)

## Smoke result

Smoke N=1024, M=256, n_probe=10, bits=8, seed=17
Verdict: PP2ADV_HARD_PASS
comp=4.00x kf1_nom=1.000 kf1_adv100=1.000 kf2=1.000 elapsed=0.46s
Note: at N=1024/M=256 codebook separation is high so adversarial effect is small;
at N=4096/M=2048 with more codebook entries the collision pairs should be tighter.

## N-suffix

_n4096 suffix binds N_FULL = 4096. Script asserts: assert N_FULL == 4096.

## Timeout estimate

smoke_wall_s = 0.46s (1 seed, n_probe=10)
FULL has 5x seeds, 6.4x n_probe, 4^1.5 N-scaling (matrix KF ops), 3 adversarial patterns
estimate: ceil(1.5 * 0.46 * 8 * 5 * 6.4 * 3) = ceil(530) = 600s
With 3x safety margin: 1800s (well within 14400 limit).
timeout_s = 1800

## Middle-band outcome plan

If MIDDLE_BAND: report KF-1 degradation curve (nominal vs 50% vs 100% adversarial).
Investigate whether compression amplifies or masks the adversarial signal relative to
uncompressed W. Route to Strategy: "PP-2 foothold conditional on nominal-input regime;
adversarial robustness requires either defense layer or tighter codebook construction."
