# Prereg: wave14_rprime3_R1_alt_geometry_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: R-PRIME-3 R1 rescue (alt-geometry metric post-HARD-FAIL v193)
**Source**: cap_map v193 R-PRIME-3 R1 rescue (5 rescues filed inline)

## Per [[feedback-rehabilitation-after-rejection]] / [[feedback-dont-overextend-theorems]]

R-PRIME-3 inner-product HARD-FAIL kills SPECIFIC metric, NOT all geometry framings. R1 preserves idea space via alt-metric (Wasserstein-1 between coordinate-marginal distributions ≈ cluster-structured distance).

## Hypothesis

Substrate task-pair retention correlates with Wasserstein-1 distance between substrate marginal distributions (cluster-structured) better than with bare inner-product overlap.

## Design

- N=1024 substrate width
- M_stored=100 items per task
- 10 task pairs per seed (>=6 required per R-PRIME-3 falsifier spec)
- 5 seeds: [7, 17, 23, 31, 41]
- Metric A: inner-product (control, the REJECTED metric)
- Metric B: Wasserstein-1 between sorted row-sums (alt-metric, cluster-structured)
- Pearson correlation retention vs each metric

## Falsifier bands (pre-registered)

- **HARD-PASS — R1 rescue SUCCEEDS; task-geometry 🔬 -> 🟡 under alt-metric**: |corr(retention, alt_metric)| >= 0.60 AND |corr(retention, inner_prod)| <= 0.35.
- **HARD-FAIL — R1 rescue FAILS; move to R2 sub-corpus geometry**: |corr(retention, alt_metric)| < 0.30 AND |corr(retention, inner_prod)| < 0.30 (both flat).
- **MIDDLE**: any intermediate; report bands.

## Smoke result (N=128, M=20, 3 pairs, 1 seed)

`RPRIME3_R1_HARD_PASS_ALT_GEOMETRY_RESCUE` at smoke (|corr_alt|=0.947, |corr_inner|=0.221). Promising but smoke-only with 3 pairs is underpowered; FULL at 10 pairs × 5 seeds.

## Self-test

`verdict self-test passed (4/4 cases)`.

## Queue

`queue=remote_cpu_queue name=wave14_rprime3_R1_alt_geometry_v1 script=experiments/exp_wave14_rprime3_R1_alt_geometry_v1.py prereg=preregs/2026-05-24_wave14_rprime3_R1_alt_geometry_v1.md timeout=2400`
