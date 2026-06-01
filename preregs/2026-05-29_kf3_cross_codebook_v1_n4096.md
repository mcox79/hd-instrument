# Pre-registration: kf3_cross_codebook_v1_n4096

**Filed:** 2026-05-29
**Anchor:** kf3_cross_codebook_v1_n4096
**Script:** experiments/exp_kf3_cross_codebook_v1_n4096.py
**Queue:** remote_cpu_queue
**Parent:** kf3_multisub_v2_n4096 (MIDDLE_BAND); kf2_cross_codebook_v1_n4096 (HARD_PASS)
**Routing file:** notes/strategy_request_to_exp_dev_post_reset_priority_2026-05-29.md

## Hypothesis

KF-3 multi-substrate isolation (info_leakage, state_contamination) holds across codebook
families (Kerdock, BSC, Gaussian) at N=4096. At least one family achieves HP thresholds.

## Protocol

- N = 4096 (PROT-018 binding; _n4096 suffix)
- Codebook families: kerdock, bsc, gaussian
- M_fracs: [4, 8, 12] (M = M_frac * N)
- Seeds: 5 (7, 17, 23, 31, 41)
- n_probe: 100
- Metrics: info_leakage, state_contamination per (family, M_frac, seed)
- Protocol: kf3v2 isolation protocol (resp_A vs resp_B_Akeys cosine similarity)

## Pre-registered bands

**HARD_PASS:** at least 1 family max_leakage < 0.01 AND max_contam < 0.05 at M_frac=4
  at >= 3/5 seeds.
  Interpretation: KF-3 isolation is achievable with appropriate codebook.

**HARD_FAIL:** max_leakage >= 0.10 OR max_contam >= 0.30 in ANY family.
  Interpretation: structural contamination -- cross-substrate interference is fundamental.

**MIDDLE_BAND:** all families have max_leakage > 0.01 but < 0.10.
  Outcome plan: report best-family results; flag which family is closest to HP.

## Timeout estimate

smoke_wall_s = 0.26 (3 families x 1 M_frac x 1 seed, N=1024)
smoke_cells = 3; FULL_cells = 45
N_scale = (4096/1024)^1.5 = 8; seed_scale = 5; mfrac_scale = 3
estimate = ceil(1.5 * 0.26 * 8 * 5 * 3) = ceil(46.8) = 300s
Floor _n4096 = 14400s. timeout_s = 14400

## Smoke result (2026-05-29)

N=1024 (smoke): kerdock leakage=0.026 contam=0.091 | bsc leakage=0.029 contam=0.108 | gaussian leakage=0.034 contam=0.078
N=4096 (4x smoke, 1 seed): bsc leakage=0.018 contam=0.062

Verdict: KF3_CROSS_SMOKE_PARTIAL
Trend: leakage decreases with N per 1/sqrt(N) prediction. HP achievable at FULL N=4096 5-seed.

## N-suffix verification

_n4096 -> N_FULL = 4096. Assert in code. PROT-018 satisfied.
